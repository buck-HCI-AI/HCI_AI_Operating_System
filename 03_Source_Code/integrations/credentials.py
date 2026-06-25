"""
HCI AI — n8n credential decryption utility.
Decrypts OAuth tokens stored in n8n's SQLite database for direct API calls.
"""
import base64, hashlib, json, os, sqlite3, ssl, urllib.parse, urllib.request
import certifi

SSL_CTX = ssl.create_default_context(cafile=certifi.where())

N8N_DB = os.path.expanduser("~/.n8n/database.sqlite")
ENCRYPTION_KEY = os.environ.get("N8N_ENCRYPTION_KEY", "V2eUhJr67YMkYY1nFAFvnyOKMnGuhgSL")


def decrypt_credential(cred_id: str) -> dict:
    db = sqlite3.connect(N8N_DB)
    cur = db.cursor()
    cur.execute("SELECT data FROM credentials_entity WHERE id = ?", (cred_id,))
    row = cur.fetchone()
    db.close()
    if not row:
        raise ValueError(f"Credential {cred_id} not found")

    raw = base64.b64decode(row[0])
    salt, ct = raw[8:16], raw[16:]

    def evp_kdf(password: bytes, salt: bytes, key_size=32, iv_size=16) -> tuple:
        d, d_i = b"", b""
        while len(d) < key_size + iv_size:
            d_i = hashlib.md5(d_i + password + salt).digest()
            d += d_i
        return d[:key_size], d[key_size:key_size + iv_size]

    key, iv = evp_kdf(ENCRYPTION_KEY.encode(), salt)

    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
    return json.loads(unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(ct), 16))


# Credential IDs (from n8n)
CRED_IDS = {
    "outlook":       "I9EZEhr72Zo6vPWX",
    "hubspot":       "H44xFkyJ22zQfjOQ",
    "google_sheets": "Z9ViG2jWlb66ncRi",
    "google_drive":  "UDJZyRl4iZXIr4qI",
}


def get_hubspot_auth() -> str:
    """Returns the HubSpot Authorization header value (already includes 'Bearer ')."""
    cred = decrypt_credential(CRED_IDS["hubspot"])
    return cred["value"]


def get_google_token(service: str = "sheets") -> str:
    """Refreshes and returns a Google OAuth access token."""
    cred_id = CRED_IDS.get(f"google_{service}", CRED_IDS["google_sheets"])
    cred = decrypt_credential(cred_id)
    scope_map = {
        "sheets": "https://www.googleapis.com/auth/spreadsheets",
        "drive":  "https://www.googleapis.com/auth/drive",
    }
    params = {
        "grant_type":    "refresh_token",
        "refresh_token": cred["oauthTokenData"]["refresh_token"],
        "client_id":     cred["clientId"],
        "client_secret": cred["clientSecret"],
        "scope":         scope_map.get(service, scope_map["sheets"]),
    }
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        urllib.parse.urlencode(params).encode(), method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, context=SSL_CTX) as r:
        return json.loads(r.read())["access_token"]


def get_ms_token() -> str:
    """Refreshes and returns a Microsoft Graph OAuth access token."""
    cred = decrypt_credential(CRED_IDS["outlook"])
    params = {
        "grant_type":    "refresh_token",
        "refresh_token": cred["oauthTokenData"]["refresh_token"],
        "client_id":     cred["clientId"],
        "client_secret": cred["clientSecret"],
        "scope":         "https://graph.microsoft.com/.default offline_access",
    }
    token_url = cred.get("accessTokenUrl",
                         "https://login.microsoftonline.com/common/oauth2/v2.0/token")
    req = urllib.request.Request(
        token_url, urllib.parse.urlencode(params).encode(), method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, context=SSL_CTX) as r:
        return json.loads(r.read())["access_token"]
