"""
mine_hubspot.py
One-time deep data mining of ALL HubSpot data.
Pulls: all deals (all properties), all notes for every deal, all contacts,
       all companies, engagement history (calls, emails, meetings).
Writes to Postgres + embeds into Qdrant project_memory.
"""
import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "integrations"))

import psycopg2, psycopg2.extras
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

from hubspot import _request
from memory_utils import upsert_one

DB = dict(
    host=os.environ.get("POSTGRES_HOST", "localhost"),
    port=int(os.environ.get("POSTGRES_PORT", 5432)),
    dbname=os.environ.get("POSTGRES_DB", "hci_os"),
    user=os.environ.get("POSTGRES_USER", "hci_admin"),
    password=os.environ.get("POSTGRES_PASSWORD", ""),
)

# All useful deal properties to pull
DEAL_PROPS = ",".join([
    "dealname", "dealstage", "amount", "closedate", "createdate",
    "description", "dealtype", "pipeline",
    "project_name", "architecht", "building_plan_links",
    "conditional_waiver_status", "unconditional_waiver_status",
    "subcontract_status", "tradescope", "division",
    "estimator", "package_name", "package_number",
    "hs_lastmodifieddate", "notes_last_updated",
    "num_notes", "num_associated_contacts",
    "hubspot_owner_id", "closed_won_reason", "closed_lost_reason",
])

STAGE_NAMES = {
    "3524209344": "Not Started",
    "3524209345": "Scope Ready",
    "3524209346": "Sent Out",
    "3524209347": "Bids Receiving",
    "3524209348": "Leveling",
    "3524209349": "Awarded",
    "3524209350": "Not Awarded",
}


def pg():
    return psycopg2.connect(**DB, cursor_factory=psycopg2.extras.RealDictCursor)


def ensure_tables(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS hubspot_contacts (
            id                  SERIAL PRIMARY KEY,
            hubspot_contact_id  TEXT UNIQUE NOT NULL,
            first_name          TEXT,
            last_name           TEXT,
            email               TEXT,
            phone               TEXT,
            company             TEXT,
            job_title           TEXT,
            city                TEXT,
            state               TEXT,
            raw_properties      JSONB,
            synced_at           TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS hubspot_companies (
            id                  SERIAL PRIMARY KEY,
            hubspot_company_id  TEXT UNIQUE NOT NULL,
            name                TEXT,
            domain              TEXT,
            city                TEXT,
            state               TEXT,
            phone               TEXT,
            industry            TEXT,
            raw_properties      JSONB,
            synced_at           TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS hubspot_engagements (
            id                  SERIAL PRIMARY KEY,
            hubspot_engagement_id TEXT UNIQUE NOT NULL,
            deal_id             TEXT,
            engagement_type     TEXT,
            subject             TEXT,
            body                TEXT,
            created_at          TIMESTAMPTZ,
            synced_at           TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    # Add pipeline column to deals if missing
    cur.execute("""
        ALTER TABLE hubspot_deals ADD COLUMN IF NOT EXISTS pipeline TEXT;
        ALTER TABLE hubspot_deals ADD COLUMN IF NOT EXISTS raw_properties JSONB;
        ALTER TABLE hubspot_deals ADD COLUMN IF NOT EXISTS owner TEXT;
    """)


# ── Deals ──────────────────────────────────────────────────────────────────────

def get_all_deals():
    results, after = [], None
    while True:
        url = f"/crm/v3/objects/deals?limit=100&properties={DEAL_PROPS}"
        if after:
            url += f"&after={after}"
        data, err = _request("GET", url)
        if err or not data:
            print(f"  Deal fetch error: {err}")
            break
        results.extend(data.get("results", []))
        after = (data.get("paging") or {}).get("next", {}).get("after")
        if not after:
            break
        time.sleep(0.1)
    return results


def upsert_deal(cur, deal):
    p = deal.get("properties", {})
    deal_id = deal["id"]
    stage_key = p.get("dealstage", "")
    stage_name = STAGE_NAMES.get(stage_key, stage_key)
    amount = p.get("amount")
    try:
        amount = float(amount) if amount else None
    except (ValueError, TypeError):
        amount = None

    cur.execute("""
        INSERT INTO hubspot_deals (
            hubspot_deal_id, deal_name, stage, amount, close_date,
            last_modified, pipeline, raw_properties, synced_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        ON CONFLICT (hubspot_deal_id) DO UPDATE SET
            deal_name      = EXCLUDED.deal_name,
            stage          = EXCLUDED.stage,
            amount         = EXCLUDED.amount,
            close_date     = EXCLUDED.close_date,
            last_modified  = EXCLUDED.last_modified,
            pipeline       = EXCLUDED.pipeline,
            raw_properties = EXCLUDED.raw_properties,
            synced_at      = NOW()
        RETURNING id
    """, (
        deal_id,
        p.get("dealname", ""),
        stage_name,
        amount,
        p.get("closedate"),
        p.get("hs_lastmodifieddate"),
        p.get("pipeline"),
        json.dumps(p),
    ))
    return cur.fetchone()["id"]


def embed_deal(deal):
    p = deal.get("properties", {})
    deal_name  = p.get("dealname", "")
    stage      = STAGE_NAMES.get(p.get("dealstage", ""), p.get("dealstage", "unknown"))
    amount     = p.get("amount", "")
    desc       = p.get("description", "")
    proj_name  = p.get("project_name", "")
    arch       = p.get("architecht", "")
    trade      = p.get("tradescope", "")
    pkg        = p.get("package_name", "")
    pkg_num    = p.get("package_number", "")
    div        = p.get("division", "")
    sub_status = p.get("subcontract_status", "")
    cw_status  = p.get("conditional_waiver_status", "")
    won_reason = p.get("closed_won_reason", "")
    lost_reason= p.get("closed_lost_reason", "")
    estimator  = p.get("estimator", "")
    plans      = p.get("building_plan_links", "")

    parts = [f"HubSpot deal: {deal_name}."]
    if proj_name:    parts.append(f"Project: {proj_name}.")
    if stage:        parts.append(f"Stage: {stage}.")
    if amount:       parts.append(f"Amount: ${amount}.")
    if desc:         parts.append(f"Description: {desc}.")
    if arch:         parts.append(f"Architect: {arch}.")
    if trade:        parts.append(f"Trade scope: {trade}.")
    if pkg:          parts.append(f"Package: {pkg} #{pkg_num}.")
    if div:          parts.append(f"Division: {div}.")
    if estimator:    parts.append(f"Estimator: {estimator}.")
    if sub_status:   parts.append(f"Subcontract status: {sub_status}.")
    if cw_status:    parts.append(f"Conditional waiver: {cw_status}.")
    if won_reason:   parts.append(f"Won reason: {won_reason}.")
    if lost_reason:  parts.append(f"Lost reason: {lost_reason}.")
    if plans:        parts.append(f"Plan links: {plans}.")

    text = " ".join(parts)
    vec_id = 20000 + int(deal["id"])
    upsert_one("project_memory", vec_id, text, {
        "type":       "hubspot_deal",
        "deal_id":    deal["id"],
        "deal_name":  deal_name,
        "stage":      stage,
        "amount":     float(amount) if amount else 0,
        "project":    proj_name or deal_name,
        "tradescope": trade,
    })


# ── Notes (all deals, paginated) ───────────────────────────────────────────────

def get_all_note_ids_for_deal(deal_id):
    note_ids, after = [], None
    while True:
        url = f"/crm/v3/objects/deals/{deal_id}/associations/notes?limit=100"
        if after:
            url += f"&after={after}"
        data, _ = _request("GET", url)
        if not data:
            break
        note_ids.extend([r["id"] for r in data.get("results", [])])
        after = (data.get("paging") or {}).get("next", {}).get("after")
        if not after:
            break
        time.sleep(0.05)
    return note_ids


def get_note_detail(note_id):
    data, _ = _request("GET",
        f"/crm/v3/objects/notes/{note_id}?properties=hs_note_body,hs_timestamp,hs_lastmodifieddate")
    return data


def mine_notes(cur, deals, result):
    print(f"\n  Mining notes for {len(deals)} deals...")
    vectors_added = 0
    for i, deal in enumerate(deals):
        deal_id   = deal["id"]
        deal_name = deal.get("properties", {}).get("dealname", "")
        note_ids  = get_all_note_ids_for_deal(deal_id)
        if not note_ids:
            continue

        for nid in note_ids:
            n = get_note_detail(nid)
            if not n:
                continue
            p    = n.get("properties", {})
            body = (p.get("hs_note_body") or "").strip()
            ts   = p.get("hs_timestamp", "")
            if not body:
                continue
            try:
                cur.execute("""
                    INSERT INTO hubspot_notes (hubspot_note_id, deal_id, body, note_timestamp)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (hubspot_note_id) DO UPDATE SET
                        body = EXCLUDED.body, synced_at = NOW()
                """, (nid, deal_id, body, ts or None))
                result["notes"] += 1

                # Embed into project_memory
                text = f"HubSpot note on deal '{deal_name}': {body}"
                vid  = abs(hash(f"note_{nid}")) % 900_000 + 100_000
                upsert_one("project_memory", vid, text, {
                    "type":      "hubspot_note",
                    "deal_id":   deal_id,
                    "deal_name": deal_name,
                    "timestamp": ts or "",
                })
                vectors_added += 1
            except Exception as e:
                result["errors"].append(f"note {nid}: {e}")
            time.sleep(0.05)

        if (i + 1) % 50 == 0:
            cur.connection.commit()
            print(f"    {i+1}/{len(deals)} deals processed — {result['notes']} notes so far")

    cur.connection.commit()
    result["vectors"] += vectors_added
    print(f"  ✓ {result['notes']} notes, {vectors_added} note vectors")


# ── Contacts ───────────────────────────────────────────────────────────────────

CONTACT_PROPS = "firstname,lastname,email,phone,company,jobtitle,city,state"

def get_all_contacts():
    results, after = [], None
    while True:
        url = f"/crm/v3/objects/contacts?limit=100&properties={CONTACT_PROPS}"
        if after:
            url += f"&after={after}"
        data, err = _request("GET", url)
        if err or not data:
            break
        results.extend(data.get("results", []))
        after = (data.get("paging") or {}).get("next", {}).get("after")
        if not after:
            break
        time.sleep(0.1)
    return results


def mine_contacts(cur, result):
    print("\n  Mining contacts...")
    contacts = get_all_contacts()
    print(f"  Fetched {len(contacts)} contacts")
    vectors_added = 0
    for c in contacts:
        p = c.get("properties", {})
        cid = c["id"]
        fname = p.get("firstname", "")
        lname = p.get("lastname", "")
        full  = f"{fname} {lname}".strip()
        email = p.get("email", "")
        phone = p.get("phone", "")
        co    = p.get("company", "")
        title = p.get("jobtitle", "")
        city  = p.get("city", "")
        state = p.get("state", "")

        try:
            cur.execute("""
                INSERT INTO hubspot_contacts (
                    hubspot_contact_id, first_name, last_name, email, phone,
                    company, job_title, city, state, raw_properties
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (hubspot_contact_id) DO UPDATE SET
                    first_name = EXCLUDED.first_name,
                    last_name  = EXCLUDED.last_name,
                    email      = EXCLUDED.email,
                    company    = EXCLUDED.company,
                    job_title  = EXCLUDED.job_title,
                    raw_properties = EXCLUDED.raw_properties,
                    synced_at  = NOW()
            """, (cid, fname, lname, email, phone, co, title, city, state, json.dumps(p)))
            result["contacts"] += 1

            # Embed into vendor_memory (contacts are often vendors/clients/architects)
            if full or co:
                text_parts = [f"HubSpot contact: {full}."]
                if co:    text_parts.append(f"Company: {co}.")
                if title: text_parts.append(f"Title: {title}.")
                if email: text_parts.append(f"Email: {email}.")
                if phone: text_parts.append(f"Phone: {phone}.")
                if city:  text_parts.append(f"Location: {city}, {state}.")
                text = " ".join(text_parts)
                vid  = abs(hash(f"contact_{cid}")) % 900_000 + 2_000_000
                upsert_one("vendor_memory", vid, text, {
                    "type":    "hubspot_contact",
                    "name":    full,
                    "company": co,
                    "email":   email,
                })
                vectors_added += 1
        except Exception as e:
            result["errors"].append(f"contact {cid}: {e}")

    cur.connection.commit()
    result["vectors"] += vectors_added
    print(f"  ✓ {result['contacts']} contacts, {vectors_added} contact vectors")


# ── Companies ──────────────────────────────────────────────────────────────────

COMPANY_PROPS = "name,domain,phone,city,state,industry,description,numberofemployees,annualrevenue"

def get_all_companies():
    results, after = [], None
    while True:
        url = f"/crm/v3/objects/companies?limit=100&properties={COMPANY_PROPS}"
        if after:
            url += f"&after={after}"
        data, err = _request("GET", url)
        if err or not data:
            break
        results.extend(data.get("results", []))
        after = (data.get("paging") or {}).get("next", {}).get("after")
        if not after:
            break
        time.sleep(0.1)
    return results


def mine_companies(cur, result):
    print("\n  Mining companies...")
    companies = get_all_companies()
    print(f"  Fetched {len(companies)} companies")
    vectors_added = 0
    for co in companies:
        p    = co.get("properties", {})
        coid = co["id"]
        name = p.get("name", "")
        domain   = p.get("domain", "")
        phone    = p.get("phone", "")
        city     = p.get("city", "")
        state    = p.get("state", "")
        industry = p.get("industry", "")
        desc     = p.get("description", "")
        employees= p.get("numberofemployees", "")

        try:
            cur.execute("""
                INSERT INTO hubspot_companies (
                    hubspot_company_id, name, domain, city, state, phone, industry, raw_properties
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (hubspot_company_id) DO UPDATE SET
                    name  = EXCLUDED.name,
                    phone = EXCLUDED.phone,
                    city  = EXCLUDED.city,
                    industry = EXCLUDED.industry,
                    raw_properties = EXCLUDED.raw_properties,
                    synced_at = NOW()
            """, (coid, name, domain, city, state, phone, industry, json.dumps(p)))
            result["companies"] += 1

            if name:
                parts = [f"HubSpot company: {name}."]
                if industry:  parts.append(f"Industry: {industry}.")
                if city:      parts.append(f"Location: {city}, {state}.")
                if phone:     parts.append(f"Phone: {phone}.")
                if domain:    parts.append(f"Website: {domain}.")
                if desc:      parts.append(f"Description: {desc}.")
                if employees: parts.append(f"Employees: {employees}.")
                text = " ".join(parts)
                vid  = abs(hash(f"company_{coid}")) % 900_000 + 3_000_000
                upsert_one("vendor_memory", vid, text, {
                    "type":     "hubspot_company",
                    "name":     name,
                    "industry": industry,
                    "city":     city,
                })
                vectors_added += 1
        except Exception as e:
            result["errors"].append(f"company {coid}: {e}")

    cur.connection.commit()
    result["vectors"] += vectors_added
    print(f"  ✓ {result['companies']} companies, {vectors_added} company vectors")


# ── Engagements (calls, emails, meetings) ──────────────────────────────────────

def get_engagements_for_deal(deal_id):
    """Pull all engagement activity logged against a deal."""
    data, err = _request("GET",
        f"/engagements/v1/engagements/associated/deal/{deal_id}/paged?limit=50")
    if err or not data:
        return []
    return data.get("results", [])


def mine_engagements(cur, deals, result):
    print(f"\n  Mining engagement history for {len(deals)} deals...")
    vectors_added = 0
    # Only mine deals that are likely to have activity (have notes count > 0)
    active_deals = [d for d in deals
                    if int(d.get("properties", {}).get("num_notes", "0") or "0") > 0]
    print(f"  {len(active_deals)} deals with activity")

    for deal in active_deals:
        deal_id   = deal["id"]
        deal_name = deal.get("properties", {}).get("dealname", "")
        engagements = get_engagements_for_deal(deal_id)
        for eng in engagements:
            e    = eng.get("engagement", {})
            eid  = str(e.get("id", ""))
            etype = e.get("type", "")
            ts    = e.get("createdAt", "")
            meta  = eng.get("metadata", {})
            subject = meta.get("subject", "") or meta.get("title", "")
            body    = (meta.get("body", "") or meta.get("text", "") or
                      meta.get("html", "") or "")[:2000]

            if not body and not subject:
                continue
            try:
                cur.execute("""
                    INSERT INTO hubspot_engagements
                        (hubspot_engagement_id, deal_id, engagement_type, subject, body, created_at)
                    VALUES (%s, %s, %s, %s, %s, to_timestamp(%s / 1000.0))
                    ON CONFLICT (hubspot_engagement_id) DO UPDATE SET
                        body = EXCLUDED.body, synced_at = NOW()
                """, (eid, deal_id, etype, subject, body, ts if ts else None))
                result["engagements"] += 1

                text_parts = [f"HubSpot {etype.lower()} on deal '{deal_name}'."]
                if subject: text_parts.append(f"Subject: {subject}.")
                if body:    text_parts.append(body[:500])
                text = " ".join(text_parts)
                vid  = abs(hash(f"eng_{eid}")) % 900_000 + 4_000_000
                upsert_one("project_memory", vid, text, {
                    "type":      f"hubspot_{etype.lower()}",
                    "deal_id":   deal_id,
                    "deal_name": deal_name,
                })
                vectors_added += 1
            except Exception as ex:
                result["errors"].append(f"engagement {eid}: {ex}")
            time.sleep(0.05)

    cur.connection.commit()
    result["vectors"] += vectors_added
    print(f"  ✓ {result['engagements']} engagements, {vectors_added} engagement vectors")


# ── Deal-to-contact associations ───────────────────────────────────────────────

def embed_deal_contacts(deals, result):
    """For each deal, pull associated contacts and embed the relationship."""
    print(f"\n  Mining deal-contact associations...")
    vectors_added = 0
    for deal in deals[:100]:  # cap to avoid rate limits
        deal_id   = deal["id"]
        deal_name = deal.get("properties", {}).get("dealname", "")
        data, _   = _request("GET",
            f"/crm/v3/objects/deals/{deal_id}/associations/contacts?limit=20")
        if not data:
            continue
        contact_ids = [r["id"] for r in data.get("results", [])]
        for cid in contact_ids:
            c, _ = _request("GET",
                f"/crm/v3/objects/contacts/{cid}?properties=firstname,lastname,email,jobtitle,company")
            if not c:
                continue
            p = c.get("properties", {})
            name  = f"{p.get('firstname','')} {p.get('lastname','')}".strip()
            title = p.get("jobtitle", "")
            email = p.get("email", "")
            co    = p.get("company", "")
            if not name:
                continue
            text = (f"Contact on deal '{deal_name}': {name}."
                    + (f" Role: {title}." if title else "")
                    + (f" Company: {co}." if co else "")
                    + (f" Email: {email}." if email else ""))
            vid = abs(hash(f"deal_contact_{deal_id}_{cid}")) % 900_000 + 5_000_000
            upsert_one("project_memory", vid, text, {
                "type":      "deal_contact",
                "deal_id":   deal_id,
                "deal_name": deal_name,
                "contact":   name,
            })
            vectors_added += 1
            result["vectors"] += 1
            time.sleep(0.05)
    print(f"  ✓ {vectors_added} deal-contact association vectors")


# ── Main ───────────────────────────────────────────────────────────────────────

def run():
    print("\n" + "="*60)
    print("  HCI HubSpot Deep Mining")
    print("="*60)

    result = {
        "deals": 0, "notes": 0, "contacts": 0, "companies": 0,
        "engagements": 0, "vectors": 0, "errors": [],
    }

    conn = pg()
    cur  = conn.cursor()

    try:
        ensure_tables(cur)
        conn.commit()

        # 1 — All deals with all properties
        print("\n  Pulling all deals...")
        deals = get_all_deals()
        print(f"  Fetched {len(deals)} deals")
        for deal in deals:
            try:
                upsert_deal(cur, deal)
                embed_deal(deal)
                result["deals"] += 1
                result["vectors"] += 1
            except Exception as e:
                result["errors"].append(f"deal {deal.get('id')}: {e}")
        conn.commit()
        print(f"  ✓ {result['deals']} deals upserted and embedded")

        # 2 — All notes for all deals
        mine_notes(cur, deals, result)

        # 3 — Contacts
        mine_contacts(cur, result)

        # 4 — Companies
        mine_companies(cur, result)

        # 5 — Engagement history
        mine_engagements(cur, deals, result)

        # 6 — Deal-contact associations (top 100 deals)
        embed_deal_contacts(deals, result)

    except Exception as e:
        conn.rollback()
        result["errors"].append(f"Fatal: {e}")
        import traceback; traceback.print_exc()
    finally:
        cur.close()
        conn.close()

    print("\n" + "="*60)
    print(f"  DONE — {result['deals']} deals, {result['notes']} notes, "
          f"{result['contacts']} contacts, {result['companies']} companies, "
          f"{result['engagements']} engagements")
    print(f"  Total vectors: {result['vectors']}")
    if result["errors"]:
        print(f"  Errors ({len(result['errors'])}): {result['errors'][:5]}")
    print("="*60)
    return result


if __name__ == "__main__":
    run()
