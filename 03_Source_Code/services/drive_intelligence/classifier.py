"""
Document classifier for Drive Intelligence Service.
Maps file names and MIME types to HCI document categories and routing destinations.
"""
import re

# Classification categories (ordered — first match wins)
CLASSIFICATION_RULES = [
    # Drawing / Plan
    (r"floor.?plan|drawing|blueprint|plan.?set|permit.?set|architectural|elevat|section|detail|cad|dwg|revit",
     "Drawing / Plan"),
    # Schedule
    (r"schedule|gantt|milestone|timeline|baseline|master.?sched",
     "Schedule"),
    # Bid / Estimate
    (r"bid|estimate|takeoff|proposal|rfp|rfq|rom|level.?5|budget",
     "Bid / Estimate"),
    # Contract
    (r"contract|subcontract|agreement|aia|exhibit|scope.?of.?work|sow",
     "Contract"),
    # Change Order
    (r"change.?order|c\.o\.|pco|potential.?change",
     "Change Order"),
    # Invoice / Payment
    (r"invoice|payment|pay.?app|lien.?waiver|retainage|billing",
     "Invoice / Payment"),
    # SOP
    (r"\bsop\b|standard.?operating|procedure",
     "SOP"),
    # Company Policy
    (r"policy|handbook|safety.?plan|quality.?control|qc.?plan",
     "Company Policy"),
    # Architecture Handbook
    (r"architecture|handbook|adr|volume.?\d|chapter",
     "Architecture Handbook"),
    # Business Process
    (r"business.?process|workflow|process.?map|btw|backlog",
     "Business Process"),
    # Historical Cost
    (r"historical.?cost|cost.?data|unit.?cost|benchmark",
     "Historical Cost"),
    # Lesson Learned
    (r"lesson.?learned|post.?mortem|retrospective",
     "Lesson Learned"),
    # Vendor / Subcontractor
    (r"vendor|subcontractor|sub.?list|coi|insurance|w-?9|prequalif",
     "Vendor / Subcontractor"),
    # Client Communication
    (r"client|owner|letter|email|meeting.?minute|rfi|submittal",
     "Client Communication"),
    # Meeting Notes
    (r"meeting|minutes|agenda|notes|call.?notes",
     "Meeting Notes"),
    # Field Report / Daily Log
    (r"daily.?log|field.?report|site.?report|inspection|punch.?list|punchlist",
     "Field Report / Daily Log"),
    # Platform Intelligence
    (r"platform.?intel|browser.?handoff|handoff|discovery",
     "Platform Intelligence"),
    # Agent Handoff
    (r"agent.?handoff|handoff.?bus",
     "Agent Handoff"),
    # Project Document (catch-all project-related)
    (r"project|job|site|\d{3,4}.+(?:st|ave|rd|blvd|ln|dr|way|ct|pl)|eastwood|riverside|francis|garmish|cemetery|mcskim",
     "Project Document"),
]

# Routing destinations keyed by classification
ROUTING_MAP = {
    "Drawing / Plan":           "Project Brain",
    "Schedule":                 "Project Brain",
    "Bid / Estimate":           "Historical Cost Library",
    "Contract":                 "Project Brain",
    "Change Order":             "Project Brain",
    "Invoice / Payment":        "Project Brain",
    "SOP":                      "SOP Library",
    "Company Policy":           "SOP Library",
    "Architecture Handbook":    "Architecture Handbook",
    "Business Process":         "Business Process Library",
    "Historical Cost":          "Historical Cost Library",
    "Lesson Learned":           "Lessons Learned",
    "Vendor / Subcontractor":   "Project Brain",
    "Client Communication":     "Project Brain",
    "Meeting Notes":            "Project Brain",
    "Field Report / Daily Log": "Project Brain",
    "Platform Intelligence":    "Platform Intelligence",
    "Agent Handoff":            "Agent_Handoff/Inbox",
    "Project Document":         "Project Brain",
    "Unknown / Needs Review":   "Needs Human Review",
}

# Project name detection patterns
PROJECT_PATTERNS = {
    "101 Francis":    r"101.?francis|101.?w.?francis",
    "1355 Riverside": r"1355.?riverside",
    "64 Eastwood":    r"64.?eastwood|eastwood",
    "655 Garmisch":   r"655.?(south.?)?garmis|garmisch",
    "813 McSkimming": r"813.?mcskim",
    "825 Cemetery":   r"825.?cemetery|cemetery.?lane",
    "1762 Red Mountain": r"1762.?red.?mountain|red.?mountain",
    "606 Starwood":   r"606.?starwood|starwood",
    "370 Gerbaz":     r"370.?gerbaz|gerbaz",
    "246 Gallo":      r"246.?gallo",
    "349 Draw":       r"349.?draw",
    "574 Johnson":    r"574.?johnson",
}


def classify(name: str, mime_type: str = "") -> str:
    name_lower = (name or "").lower()
    for pattern, category in CLASSIFICATION_RULES:
        if re.search(pattern, name_lower, re.IGNORECASE):
            return category
    return "Unknown / Needs Review"


def detect_project(name: str) -> str | None:
    name_lower = (name or "").lower()
    for project, pattern in PROJECT_PATTERNS.items():
        if re.search(pattern, name_lower, re.IGNORECASE):
            return project
    return None


def get_routing(category: str) -> str:
    return ROUTING_MAP.get(category, "Needs Human Review")


def confidence_score(name: str, category: str) -> float:
    """Rough confidence 0.0-1.0. Higher when name clearly matches category."""
    if category == "Unknown / Needs Review":
        return 0.2
    name_lower = name.lower()
    for pattern, cat in CLASSIFICATION_RULES:
        if cat == category and re.search(pattern, name_lower, re.IGNORECASE):
            # More matches = higher confidence
            matches = len(re.findall(pattern, name_lower, re.IGNORECASE))
            return min(0.95, 0.65 + (matches * 0.1))
    return 0.5


def classify_file(file: dict) -> dict:
    name      = file.get("name", "")
    mime      = file.get("mimeType", "")
    category  = classify(name, mime)
    routing   = get_routing(category)
    project   = detect_project(name)
    confidence = confidence_score(name, category)
    auto_ingest = confidence >= 0.75 and routing != "Needs Human Review"

    return {
        "category":    category,
        "routing":     routing,
        "project":     project,
        "confidence":  round(confidence, 2),
        "auto_ingest": auto_ingest,
    }
