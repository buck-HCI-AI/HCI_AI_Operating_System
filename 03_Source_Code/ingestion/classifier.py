#!/usr/bin/env python3
"""
Document classifier for the Knowledge Ingestion Engine.
Detects project, category, CSI division, version, date, and discipline
from filename patterns and content preview.
"""
import re, os
from typing import Optional, Dict, Any
from datetime import datetime

# Active project lookup — used for project detection from filename/content
# Loaded fresh from Postgres at runtime; this is the static fallback.
PROJECT_ALIASES: Dict[str, list] = {
    "64EW":  ["64 eastwood", "64eastwood", "eastwood"],
    "101F":  ["101 francis", "101francis", "francis"],
    "1355R": ["1355 riverside", "1355riverside", "riverside"],
    "83SB":  ["83 sagebrusch", "83sagebrusch", "sagebrusch"],
}

CATEGORY_PATTERNS: Dict[str, list] = {
    "drawings":              ["drawing", "plan", "blueprint", "floor plan", "elevation", "section", "dwg", "arch"],
    "specifications":        ["spec", "specification", "div ", "section 0", "csi"],
    "bids":                  ["bid", "quote", "proposal", "rfp", "rfb"],
    "contracts":             ["contract", "agreement", "subcontract", "aba", "prime contract"],
    "change_orders":         ["change order", "change_order", "_co_", "-co-", " co "],
    "rfis":                  ["rfi", "request for information", "rfi-"],
    "submittals":            ["submittal", "shop drawing", "product data", "material data"],
    "meeting_minutes":       ["meeting", "minutes", "agenda", "mtg"],
    "daily_reports":         ["daily log", "daily report", "site report", "field report"],
    "budgets":               ["budget", "cost summary", "estimate", "cost plan", "leveling"],
    "schedules":             ["schedule", "gantt", "timeline", "milestone", "lookahead"],
    "procurement":           ["procurement", "purchase order", " po ", "po-", "lead time", "long lead"],
    "photos":                [".jpg", ".jpeg", ".png", ".tiff", "photo", "image"],
    "client_correspondence": ["owner letter", "client", "homeowner"],
    "vendor_correspondence": ["vendor", "subcontractor", "sub-bid", "sub bid"],
    "sop":                   ["sop", "standard operating", "procedure", "policy", "process"],
    "template":              ["template", "_tmpl", "-tmpl"],
    "registry":              ["registry", "vendor list", "contact list", "subcontractor list"],
}

CSI_KEYWORDS: Dict[str, list] = {
    "01": ["general requirements", "general conditions", "progress payment", "allowance", "meeting minutes"],
    "02": ["existing conditions", "demolition", "demo", "hazmat", "abatement", "survey"],
    "03": ["concrete", "slab", "footing", "foundation", "reinforcing"],
    "04": ["masonry", "brick", "block", "stone", "mortar", "grout"],
    "05": ["metals", "structural steel", "steel", "iron", "rebar"],
    "06": ["wood", "plastic", "composite", "framing", "lumber", "millwork", "cabinet", "casework", "carpentry"],
    "07": ["thermal", "moisture", "roofing", "insulation", "waterproofing", "air barrier", "flashing", "sealant"],
    "08": ["openings", "doors", "windows", "hardware", "glazing", "storefront", "curtain wall"],
    "09": ["finishes", "drywall", "gypsum", "flooring", "tile", "paint", "ceiling", "plaster", "carpet", "hardwood"],
    "10": ["specialties", "toilet accessory", "lockers", "fire extinguisher", "signage"],
    "11": ["equipment", "appliance", "kitchen equipment", "laundry", "residential appliance"],
    "12": ["furnishings", "furniture", "blinds", "shades", "window treatment"],
    "13": ["special construction", "pool", "spa", "sauna", "home theater", "wine cellar"],
    "14": ["conveying", "elevator", "lift", "escalator"],
    "15": ["mechanical", "hvac", "plumbing", "piping", "duct", "radiant heat", "snowmelt"],
    "16": ["electrical", "lighting", "power", "conduit", "panel", "low voltage", "av", "solar"],
}

VERSION_PATTERN = re.compile(
    r'[_\-\s]v(\d{1,2})(?:\.\d+)?(?:[_\-\s]|$)|'
    r'[_\-\s]rev\.?(\d+)(?:[_\-\s]|$)|'
    r'[_\-\s](v\d{2})(?:[_\-\s]|$)',
    re.IGNORECASE
)

DATE_IN_FILENAME = re.compile(r'(?:^|[_\-\s])(\d{4})(\d{2})(\d{2})(?:[_\-\s]|$)')


def load_project_aliases_from_db() -> Dict[str, list]:
    """Pull project aliases from Postgres. Falls back to static dict on error."""
    try:
        import psycopg2, os
        conn = psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=int(os.environ.get("POSTGRES_PORT", 5432)),
            dbname=os.environ.get("POSTGRES_DB", "hci_os"),
            user=os.environ.get("POSTGRES_USER", "hci_admin"),
            password=os.environ.get("POSTGRES_PASSWORD", ""),
        )
        cur = conn.cursor()
        cur.execute("SELECT project_number, name, address FROM projects WHERE status = 'active'")
        rows = cur.fetchall()
        conn.close()
        if not rows:
            return PROJECT_ALIASES
        aliases = {}
        for number, name, address in rows:
            terms = [name.lower()]
            if address:
                terms.append(address.lower())
            # split address to get street name alone
            parts = address.lower().split() if address else []
            if len(parts) >= 2:
                terms.append(" ".join(parts[:2]))
            aliases[number] = terms
        return aliases
    except Exception:
        return PROJECT_ALIASES


def detect_project(filename: str, content_preview: str = "", aliases: Optional[Dict] = None) -> Optional[str]:
    """Return project_number (e.g. '64EW') or None."""
    if aliases is None:
        aliases = PROJECT_ALIASES
    haystack = (filename + " " + content_preview).lower()
    for project_number, terms in aliases.items():
        for term in terms:
            if term in haystack:
                return project_number
    return None


def detect_category(filename: str, content_preview: str = "") -> str:
    """Return document category string."""
    haystack = (filename + " " + content_preview).lower()
    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if pattern in haystack:
                return category
    return "unknown"


def detect_csi_division(content: str) -> Optional[str]:
    """Return 2-digit CSI division code or None."""
    content_lower = content.lower()
    scores: Dict[str, int] = {}
    for div, keywords in CSI_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in content_lower)
        if score > 0:
            scores[div] = score
    if not scores:
        return None
    return max(scores, key=lambda d: scores[d])


def detect_version(filename: str) -> str:
    """Return version label like 'v1', 'v02', or 'v1' as default."""
    base = os.path.splitext(os.path.basename(filename))[0]
    m = VERSION_PATTERN.search(base)
    if m:
        for g in m.groups():
            if g:
                return g.lstrip("v").lstrip("0") or "1"
    return "1"


def detect_date(filename: str) -> Optional[str]:
    """Return ISO date string from YYYYMMDD in filename, or None."""
    base = os.path.basename(filename)
    m = DATE_IN_FILENAME.search(base)
    if m:
        y, mo, d = m.group(1), m.group(2), m.group(3)
        try:
            dt = datetime(int(y), int(mo), int(d))
            return dt.date().isoformat()
        except ValueError:
            pass
    return None


def classify(filepath: str, content: str = "", aliases: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Full classification pass. Returns dict with all detected metadata fields.

    Args:
        filepath:  full or relative file path
        content:   extracted text (first 2000 chars is enough for classification)
        aliases:   optional project alias dict (defaults to DB-loaded or static)
    """
    filename = os.path.basename(filepath)
    preview = content[:2000] if content else ""

    return {
        "project_number":  detect_project(filename, preview, aliases),
        "document_category": detect_category(filename, preview),
        "csi_division":    detect_csi_division(preview) if preview else None,
        "version_label":   f"v{detect_version(filename)}",
        "document_date":   detect_date(filename),
        "original_filename": filename,
    }
