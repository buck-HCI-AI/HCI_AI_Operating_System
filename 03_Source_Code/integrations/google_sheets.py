"""
HCI AI — Google Sheets API client.

Active trackers:
  64 Eastwood:    1yAmLo3IIp3Vqs3BQJ6QB2O4as0KqXMZxcVvjzGBZDcQ  tab: Bid Tracking
  101 Francis:    1JExX5CeVBedTEFitM8B6hveF4Prhk0Oy6BZSBu058LE  tab: Bid Tracking
  1355 Riverside: 1-64X4XGc4P_GmYl7DRt8nGsBNfaVdP_G3qwfBLJSsnA  tab: Sheet1
"""
import json, urllib.error, urllib.parse, urllib.request
from credentials import get_google_token


def _token() -> str:
    return get_google_token("sheets")


def read_range(sheet_id: str, range_: str) -> list[list]:
    token = _token()
    req = urllib.request.Request(
        f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/{urllib.parse.quote(range_)}")
    req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read()).get("values", [])


def batch_update(sheet_id: str, updates: list[tuple[str, list]]) -> dict:
    """updates: [(range_str, [[value, ...]]), ...]"""
    token = _token()
    body = json.dumps({
        "valueInputOption": "USER_ENTERED",
        "data": [{"range": r, "values": v} for r, v in updates],
    }).encode()
    req = urllib.request.Request(
        f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values:batchUpdate",
        data=body, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


# Sheet IDs
SHEETS = {
    "64_eastwood":    "1yAmLo3IIp3Vqs3BQJ6QB2O4as0KqXMZxcVvjzGBZDcQ",
    "101_francis":    "1JExX5CeVBedTEFitM8B6hveF4Prhk0Oy6BZSBu058LE",
    "1355_riverside": "1-64X4XGc4P_GmYl7DRt8nGsBNfaVdP_G3qwfBLJSsnA",
    "project_registry": "1hvOqih5b7ENsLxjU0NxP4JXg1vqGZGxO6mxRBg3nNrk",
}
