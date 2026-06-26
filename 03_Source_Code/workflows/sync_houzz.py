"""
sync_houzz.py
Daily read sync — logs into Houzz Pro and reads project data, daily logs,
and schedule info into Postgres + Qdrant. Read-only. No writes to Houzz.
Scheduled: 6:45 AM daily (before HubSpot sync and morning brief).

Requires: HOUZZ_EMAIL and HOUZZ_PASSWORD in .env
"""
import sys, os, json, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "integrations"))

import psycopg2, psycopg2.extras
from datetime import date, datetime
from memory_utils import upsert_one
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

HOUZZ_EMAIL    = os.environ.get("HOUZZ_EMAIL", "")
HOUZZ_PASSWORD = os.environ.get("HOUZZ_PASSWORD", "")

DB = dict(
    host=os.environ.get("POSTGRES_HOST", "localhost"),
    port=int(os.environ.get("POSTGRES_PORT", 5432)),
    dbname=os.environ.get("POSTGRES_DB", "hci_os"),
    user=os.environ.get("POSTGRES_USER", "hci_admin"),
    password=os.environ.get("POSTGRES_PASSWORD", ""),
)


def pg():
    return psycopg2.connect(**DB, cursor_factory=psycopg2.extras.RealDictCursor)


def ensure_houzz_tables(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS houzz_projects (
            id               SERIAL PRIMARY KEY,
            houzz_project_id TEXT UNIQUE NOT NULL,
            project_name     TEXT,
            client_name      TEXT,
            status           TEXT,
            raw_data         JSONB,
            synced_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS houzz_daily_logs (
            id               SERIAL PRIMARY KEY,
            houzz_project_id TEXT NOT NULL,
            log_date         DATE,
            content          TEXT,
            weather          TEXT,
            crew             TEXT,
            raw_data         JSONB,
            synced_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE (houzz_project_id, log_date)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS houzz_schedule_items (
            id               SERIAL PRIMARY KEY,
            houzz_project_id TEXT NOT NULL,
            task_name        TEXT,
            start_date       DATE,
            end_date         DATE,
            status           TEXT,
            raw_data         JSONB,
            synced_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)


def run(headless: bool = True) -> dict:
    """
    Log into Houzz Pro and read project data.
    Returns summary of what was synced.

    headless=False opens a visible browser (useful for first-time setup / debugging).
    """
    if not HOUZZ_EMAIL or not HOUZZ_PASSWORD:
        return {
            "status": "skipped",
            "reason": "HOUZZ_EMAIL and HOUZZ_PASSWORD not set in .env — add them to enable Houzz sync"
        }

    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

    result = {"projects": 0, "daily_logs": 0, "schedule_items": 0, "vectors": 0, "errors": []}

    conn = pg()
    cur  = conn.cursor()
    ensure_houzz_tables(cur)
    conn.commit()

    print("\n=== Houzz Daily Sync ===")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=headless,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--disable-dev-shm-usage",
            ]
        )
        ctx = browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="America/Denver",
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"macOS"',
            }
        )
        page = ctx.new_page()
        # Remove webdriver property
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        try:
            # ── Login ──────────────────────────────────────────────────────────
            print("  Logging into Houzz Pro...")
            page.goto("https://pro.houzz.com/login", wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(4000)

            # Check for rate-limit page
            if "429" in page.title() or "Too Many" in page.content()[:500]:
                result["errors"].append("Houzz rate-limited (429). Wait a few minutes and retry.")
                return result

            # Try multiple selector strategies for email input
            email_sel = None
            for sel in ['input[type="email"]', 'input[name="email"]', '#email',
                        'input[autocomplete="email"]', 'input[autocomplete="username"]',
                        'input[placeholder*="email" i]', 'input[placeholder*="Email" i]']:
                try:
                    page.wait_for_selector(sel, timeout=3000)
                    email_sel = sel
                    break
                except Exception:
                    continue

            if not email_sel:
                # Dump page for debugging
                title = page.title()
                url   = page.url
                result["errors"].append(f"Could not find email input. Page: '{title}' at {url}")
                return result

            page.fill(email_sel, HOUZZ_EMAIL)
            for sel in ['input[type="password"]', 'input[name="password"]', '#password',
                        'input[autocomplete="current-password"]']:
                try:
                    page.wait_for_selector(sel, timeout=2000)
                    page.fill(sel, HOUZZ_PASSWORD)
                    break
                except Exception:
                    continue

            page.keyboard.press("Enter")
            page.wait_for_load_state("networkidle", timeout=25000)
            page.wait_for_timeout(3000)

            if "login" in page.url.lower() or "signin" in page.url.lower():
                result["errors"].append("Login failed — check HOUZZ_EMAIL and HOUZZ_PASSWORD in .env")
                return result
            print("  ✓ Logged in")

            # ── Project list ───────────────────────────────────────────────────
            page.goto("https://pro.houzz.com/projects", wait_until="networkidle", timeout=20000)
            page.wait_for_timeout(2000)

            # Collect project links
            project_links = page.eval_on_selector_all(
                'a[href*="/projects/"]',
                'els => els.map(e => ({href: e.href, text: e.innerText.trim()}))'
            )
            # Deduplicate and filter to actual project pages
            seen = set()
            projects = []
            for l in project_links:
                href = l["href"]
                if "/projects/" in href and href not in seen and l["text"]:
                    seen.add(href)
                    projects.append(l)

            print(f"  Found {len(projects)} project links")

            for proj in projects[:20]:  # cap at 20 projects
                try:
                    proj_url  = proj["href"]
                    proj_name = proj["text"]
                    proj_id   = proj_url.rstrip("/").split("/")[-1]

                    # Upsert project
                    cur.execute("""
                        INSERT INTO houzz_projects (houzz_project_id, project_name, status, raw_data)
                        VALUES (%s, %s, 'active', %s)
                        ON CONFLICT (houzz_project_id) DO UPDATE SET
                            project_name = EXCLUDED.project_name, synced_at = NOW()
                        RETURNING id
                    """, (proj_id, proj_name, json.dumps({"url": proj_url})))
                    conn.commit()
                    result["projects"] += 1

                    # ── Daily logs ─────────────────────────────────────────────
                    log_url = f"{proj_url.rstrip('/')}/daily-reports"
                    page.goto(log_url, wait_until="networkidle", timeout=15000)
                    page.wait_for_timeout(1500)

                    log_entries = page.eval_on_selector_all(
                        '[class*="daily-report"], [class*="dailyReport"], [data-testid*="report"]',
                        '''els => els.map(el => ({
                            date:    el.querySelector('[class*="date"]')?.innerText?.trim() || "",
                            content: el.innerText?.trim()?.slice(0, 1500) || ""
                        }))'''
                    )

                    for entry in log_entries[:30]:
                        if not entry.get("content"):
                            continue
                        try:
                            log_date = _parse_date(entry.get("date", ""))
                            cur.execute("""
                                INSERT INTO houzz_daily_logs
                                    (houzz_project_id, log_date, content, raw_data)
                                VALUES (%s, %s, %s, %s)
                                ON CONFLICT (houzz_project_id, log_date) DO UPDATE SET
                                    content = EXCLUDED.content, synced_at = NOW()
                            """, (proj_id, log_date, entry["content"],
                                  json.dumps(entry)))

                            # Ingest into Qdrant project_memory
                            vec_id = abs(hash(f"houzz_{proj_id}_{log_date}")) % 1_000_000 + 30000
                            upsert_one("project_memory", vec_id, entry["content"], {
                                "type":       "houzz_daily_log",
                                "project":    proj_name,
                                "log_date":   str(log_date) if log_date else "",
                                "source":     "houzz",
                            })
                            result["daily_logs"] += 1
                            result["vectors"]    += 1
                        except Exception as e:
                            result["errors"].append(f"log entry: {e}")

                    conn.commit()

                    # ── Schedule ───────────────────────────────────────────────
                    sched_url = f"{proj_url.rstrip('/')}/schedule"
                    page.goto(sched_url, wait_until="networkidle", timeout=15000)
                    page.wait_for_timeout(1500)

                    sched_items = page.eval_on_selector_all(
                        '[class*="task"], [class*="schedule-item"], [class*="gantt"]',
                        '''els => els.map(el => ({
                            name:   el.querySelector('[class*="name"], [class*="title"]')?.innerText?.trim() || el.innerText?.trim()?.slice(0, 100),
                            status: el.querySelector('[class*="status"]')?.innerText?.trim() || "",
                            dates:  el.querySelector('[class*="date"]')?.innerText?.trim() || ""
                        }))'''
                    )

                    for item in sched_items[:50]:
                        if not item.get("name"):
                            continue
                        try:
                            cur.execute("""
                                INSERT INTO houzz_schedule_items
                                    (houzz_project_id, task_name, status, raw_data)
                                VALUES (%s, %s, %s, %s)
                            """, (proj_id, item["name"], item.get("status"), json.dumps(item)))
                            result["schedule_items"] += 1
                        except Exception as e:
                            result["errors"].append(f"schedule item: {e}")

                    conn.commit()

                except PWTimeout:
                    result["errors"].append(f"Timeout on project {proj_name}")
                except Exception as e:
                    result["errors"].append(f"Project {proj_name}: {e}")

        except Exception as e:
            result["errors"].append(f"Fatal: {e}")
            import traceback; traceback.print_exc()
        finally:
            browser.close()
            cur.close()
            conn.close()

    result["status"] = "success" if not result["errors"] else "partial"
    print(f"  ✓ Houzz sync — {result['projects']} projects, {result['daily_logs']} logs, "
          f"{result['schedule_items']} schedule items, {len(result['errors'])} errors")
    return result


def _parse_date(text: str):
    """Best-effort date parse from Houzz UI strings."""
    if not text:
        return None
    for fmt in ("%B %d, %Y", "%b %d, %Y", "%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text.strip(), fmt).date()
        except ValueError:
            continue
    return None


if __name__ == "__main__":
    import sys
    headless = "--visible" not in sys.argv
    r = run(headless=headless)
    print(json.dumps(r, indent=2, default=str))
