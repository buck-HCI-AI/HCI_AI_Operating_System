"""SINGLE SOURCE OF TRUTH for HCI's canonical project/bid folder structure.

Authoritative source: "Project Folder Organization" master doc
(Google Doc 1dUrrHXLCaLG9eOjZ1CK3a1gC6GqTJ3c4iTjx18vJLE4 / .docx
1jkhKqeKyxTIaQYzoEqa8vz1J7UkrBw-T), read verbatim 2026-07-21. Buck's ruling that
day made this the final standard and overruled the old "Letter scheme"
(01_General Conditions / 02_Demo / 06_Carpentry / 08_Openings / 22_Plumbing /
32_Site / 33_Utilities), which was WRONG and must never be generated again.

Rules from the doc + Buck:
- Sub-package numbers are INDEPENDENT of the division number (e.g. 06 contains
  "11_Cabinets" while there is also a top-level "11_Equipment & Appliances" - the
  two 11s are unrelated). Only 06/07/08/09/15/16 have sub-packages.
- 10/11/12/13/14 are their OWN top-level divisions, NOT sub-packages under 10.
- Cost codes are tracker DATA fields, never folder names.
- The master doc has a typo "28_Landscadping"; the correct spelling is
  "28_Landscaping" (the live 101F folder is already correct).
"""

# 00_Bids -> ordered top-level division folders, each with its ordered sub-packages.
CANONICAL_BID_STRUCTURE = {
    "01_General Requirement": [],
    "02_Site Work": [],
    "03_Concrete": [],
    "04_Masonry": [],
    "05_Metals": [],
    "06_Wood & Plastic": ["9_Carpentry", "11_Cabinets", "12_T&G Ceiling"],
    "07_Thermal & Moisture": ["5_Waterproofing", "13_Insulation", "14_Roofing"],
    "08_Door & Windows": ["15_Doors/Windows Exterior", "16_Interior Doors"],
    "09_Finishes": ["17_Glazing", "18_Drywall & Plaster", "19_Tile & Stone", "20_Flooring", "22_Paint"],
    "10_Specialties": [],
    "11_Equipment & Appliances": [],
    "12_Furnishings": [],
    "13_Special Construction": [],
    "14_Conveying Systems": [],
    "15_Mechanical": ["21_HVAC", "24_Plumbing"],
    "16_Electrical": ["25_Electric", "26_Low Voltage", "34_Solar"],
    "28_Landscaping": [],
    "33_Radon": [],
}

# The 16 root project folders (siblings of 00_Bids).
CANONICAL_ROOT_FOLDERS = [
    "00_Bids", "01_Budget", "02_Pay Applications", "03_Permit Information",
    "04_Drawings", "05_Specifications", "06_RFI & Submittals", "07_Change Orders",
    "08_General Photos", "09_Contracts", "10_Project Notes", "11_Schedule",
    "12_Client", "13_Internal", "14_Survey Information", "15_Weekly Meetings",
]

# 09_Contracts/Subcontracts uses division-numbered subfolders (no sub-packages).
CANONICAL_SUBCONTRACT_DIVISIONS = [d for d in CANONICAL_BID_STRUCTURE if not d.startswith("01_")]

# division_num ("06") -> canonical division folder name.
DIVISION_NUM_TO_FOLDER = {name.split("_", 1)[0].zfill(2): name for name in CANONICAL_BID_STRUCTURE}

# Map a real bid sub-scope (from drive_bids.division_name suffix / extraction) to
# the canonical sub-package folder it belongs in. Keyed by lowercase keyword found
# in the scope text. Note: Tile AND Stone both map to "19_Tile & Stone" (one folder).
SUBPACKAGE_KEYWORD_MAP = {
    # 06 Wood & Plastic
    "carpentry": "9_Carpentry", "framing": "9_Carpentry", "rough carpentry": "9_Carpentry",
    "millwork": "9_Carpentry", "trim": "9_Carpentry",
    "cabinet": "11_Cabinets", "casework": "11_Cabinets",
    "t&g": "12_T&G Ceiling", "tongue": "12_T&G Ceiling", "ceiling": "12_T&G Ceiling",
    # 07 Thermal & Moisture
    "waterproof": "5_Waterproofing", "damproof": "5_Waterproofing",
    "insulation": "13_Insulation",
    "roof": "14_Roofing",
    # 08 Door & Windows
    "window": "15_Doors/Windows Exterior", "exterior door": "15_Doors/Windows Exterior",
    "garage door": "15_Doors/Windows Exterior", "storefront": "15_Doors/Windows Exterior",
    "interior door": "16_Interior Doors", "door hardware": "16_Interior Doors",
    # 09 Finishes
    "glazing": "17_Glazing", "glass": "17_Glazing", "mirror": "17_Glazing",
    "drywall": "18_Drywall & Plaster", "plaster": "18_Drywall & Plaster", "stucco": "18_Drywall & Plaster",
    "tile": "19_Tile & Stone", "stone": "19_Tile & Stone",
    "floor": "20_Flooring", "carpet": "20_Flooring", "hardwood": "20_Flooring",
    "paint": "22_Paint",
    # 15 Mechanical
    "hvac": "21_HVAC", "mechanical": "21_HVAC", "heating": "21_HVAC",
    "plumb": "24_Plumbing",
    # 16 Electrical
    "electric": "25_Electric", "power": "25_Electric",
    "low voltage": "26_Low Voltage", "av": "26_Low Voltage", "data": "26_Low Voltage", "security": "26_Low Voltage",
    "solar": "34_Solar", "pv": "34_Solar",
}


def canonical_subpackage_for(division_num: str, scope_text: str) -> str | None:
    """Return the canonical sub-package folder name for a bid's scope within a
    division, or None if the division has no sub-packages / no keyword matches.
    scope_text is the sub-scope description (e.g. the division_name em-dash suffix)."""
    subs = CANONICAL_BID_STRUCTURE.get(DIVISION_NUM_TO_FOLDER.get(str(division_num).zfill(2), ""), [])
    if not subs or not scope_text:
        return None
    t = scope_text.lower()
    # longest keyword first so "interior door"/"door hardware"/"low voltage" beat "door"/"av"
    for kw in sorted(SUBPACKAGE_KEYWORD_MAP, key=len, reverse=True):
        if kw in t and SUBPACKAGE_KEYWORD_MAP[kw] in subs:
            return SUBPACKAGE_KEYWORD_MAP[kw]
    return None
