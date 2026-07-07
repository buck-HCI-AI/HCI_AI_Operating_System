"""
Minimal single-user OAuth 2.0 Authorization Server Provider for the HCI MCP server.

Buck is the only real user of this system. There is no multi-tenant login screen -
"authorize" auto-approves immediately once a client is dynamically registered,
issuing a code tied to Buck. This satisfies remote MCP clients (Claude, ChatGPT)
that require a full OAuth flow (dynamic client registration + auth code + token
exchange) rather than a static API key, without needing Buck to manually create
or paste a Client ID anywhere - the client registers itself against /register.

Storage: Postgres (mcp_oauth_clients / mcp_oauth_codes / mcp_oauth_tokens), so
tokens survive a server restart.
"""
import os, sys, secrets, time
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
from db import pg

from mcp.server.auth.provider import (
    OAuthAuthorizationServerProvider, AuthorizationParams, AuthorizationCode,
    RefreshToken, AccessToken, RegistrationError, AuthorizeError, TokenError,
)
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken

CODE_TTL_SECONDS = 300
ACCESS_TOKEN_TTL_SECONDS = 60 * 60 * 24 * 30  # 30 days - single-user private system
BUCK_SUBJECT = "buck@hendricksoninc.com"


def _q_one(sql, params=()):
    conn = pg()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def _exec(sql, params=()):
    conn = pg()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
        conn.commit()
    finally:
        conn.close()


class HCIOAuthProvider(OAuthAuthorizationServerProvider):

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        row = _q_one("SELECT client_info FROM mcp_oauth_clients WHERE client_id = %s", (client_id,))
        if not row:
            return None
        return OAuthClientInformationFull.model_validate(row["client_info"])

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        _exec(
            "INSERT INTO mcp_oauth_clients (client_id, client_info) VALUES (%s, %s) "
            "ON CONFLICT (client_id) DO UPDATE SET client_info = EXCLUDED.client_info",
            (client_info.client_id, client_info.model_dump_json()),
        )

    async def authorize(self, client: OAuthClientInformationFull, params: AuthorizationParams) -> str:
        # Single-user system - Buck is the only resource owner, auto-approve.
        code = secrets.token_urlsafe(32)
        code_obj = AuthorizationCode(
            code=code,
            scopes=params.scopes or [],
            expires_at=time.time() + CODE_TTL_SECONDS,
            client_id=client.client_id,
            code_challenge=params.code_challenge,
            redirect_uri=params.redirect_uri,
            redirect_uri_provided_explicitly=params.redirect_uri_provided_explicitly,
            resource=params.resource,
            subject=BUCK_SUBJECT,
        )
        expires_dt = datetime.now(timezone.utc) + timedelta(seconds=CODE_TTL_SECONDS)
        _exec(
            "INSERT INTO mcp_oauth_codes (code, client_id, code_data, expires_at) VALUES (%s, %s, %s, %s)",
            (code, client.client_id, code_obj.model_dump_json(), expires_dt),
        )
        from urllib.parse import urlencode, urlparse, parse_qs
        parts = urlparse(str(params.redirect_uri))
        query = parse_qs(parts.query)
        query["code"] = [code]
        if params.state is not None:
            query["state"] = [params.state]
        new_query = urlencode({k: v[0] for k, v in query.items()})
        return parts._replace(query=new_query).geturl()

    async def load_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: str
    ) -> AuthorizationCode | None:
        row = _q_one(
            "SELECT code_data, expires_at FROM mcp_oauth_codes WHERE code = %s AND client_id = %s",
            (authorization_code, client.client_id),
        )
        if not row:
            return None
        if row["expires_at"] < datetime.now(timezone.utc):
            return None
        return AuthorizationCode.model_validate(row["code_data"])

    async def exchange_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: AuthorizationCode
    ) -> OAuthToken:
        _exec("DELETE FROM mcp_oauth_codes WHERE code = %s", (authorization_code.code,))

        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)
        expires_dt = datetime.now(timezone.utc) + timedelta(seconds=ACCESS_TOKEN_TTL_SECONDS)

        access_obj = AccessToken(
            token=access_token, client_id=client.client_id, scopes=authorization_code.scopes,
            expires_at=int(expires_dt.timestamp()), resource=authorization_code.resource,
            subject=authorization_code.subject,
        )
        refresh_obj = RefreshToken(
            token=refresh_token, client_id=client.client_id, scopes=authorization_code.scopes,
            subject=authorization_code.subject,
        )
        _exec(
            "INSERT INTO mcp_oauth_tokens (token, token_type, client_id, token_data, expires_at) VALUES (%s,'access',%s,%s,%s)",
            (access_token, client.client_id, access_obj.model_dump_json(), expires_dt),
        )
        _exec(
            "INSERT INTO mcp_oauth_tokens (token, token_type, client_id, token_data, expires_at) VALUES (%s,'refresh',%s,%s,NULL)",
            (refresh_token, client.client_id, refresh_obj.model_dump_json()),
        )
        return OAuthToken(
            access_token=access_token, token_type="Bearer",
            expires_in=ACCESS_TOKEN_TTL_SECONDS, refresh_token=refresh_token,
            scope=" ".join(authorization_code.scopes) if authorization_code.scopes else None,
        )

    async def load_refresh_token(self, client: OAuthClientInformationFull, refresh_token: str) -> RefreshToken | None:
        row = _q_one(
            "SELECT token_data FROM mcp_oauth_tokens WHERE token = %s AND client_id = %s AND token_type='refresh' AND revoked=FALSE",
            (refresh_token, client.client_id),
        )
        if not row:
            return None
        return RefreshToken.model_validate(row["token_data"])

    async def exchange_refresh_token(
        self, client: OAuthClientInformationFull, refresh_token: RefreshToken, scopes: list[str]
    ) -> OAuthToken:
        access_token = secrets.token_urlsafe(32)
        expires_dt = datetime.now(timezone.utc) + timedelta(seconds=ACCESS_TOKEN_TTL_SECONDS)
        access_obj = AccessToken(
            token=access_token, client_id=client.client_id, scopes=scopes or refresh_token.scopes,
            expires_at=int(expires_dt.timestamp()), subject=refresh_token.subject,
        )
        _exec(
            "INSERT INTO mcp_oauth_tokens (token, token_type, client_id, token_data, expires_at) VALUES (%s,'access',%s,%s,%s)",
            (access_token, client.client_id, access_obj.model_dump_json(), expires_dt),
        )
        return OAuthToken(
            access_token=access_token, token_type="Bearer",
            expires_in=ACCESS_TOKEN_TTL_SECONDS, refresh_token=refresh_token.token,
            scope=" ".join(scopes) if scopes else None,
        )

    async def load_access_token(self, token: str) -> AccessToken | None:
        row = _q_one(
            "SELECT token_data, expires_at FROM mcp_oauth_tokens WHERE token = %s AND token_type='access' AND revoked=FALSE",
            (token,),
        )
        if not row:
            return None
        if row["expires_at"] and row["expires_at"] < datetime.now(timezone.utc):
            return None
        return AccessToken.model_validate(row["token_data"])

    async def revoke_token(self, token: AccessToken | RefreshToken) -> None:
        _exec("UPDATE mcp_oauth_tokens SET revoked = TRUE WHERE token = %s", (token.token,))
