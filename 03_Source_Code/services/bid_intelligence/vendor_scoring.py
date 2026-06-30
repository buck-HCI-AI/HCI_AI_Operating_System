"""
BTW-8 — Vendor Performance Scoring.

Scoring formula (100 pts total):
  Response score   (0-40): responded to sent bids? how fast?
  Coverage score   (0-30): engaged across multiple live projects?
  History score    (0-30): bid_count, win_rate_pct from vendor record

Grade:
  A  80-100  Preferred — reliable, responsive, proven
  B  60-79   Active    — solid, minor gaps
  C  40-59   Watch     — slow or thin history
  D  0-39    Risk      — non-responsive or no track record
"""
from datetime import date


LIVE_PROJECT_IDS = [1, 2, 3, 8]


def score_vendor(vendor_id: int, conn) -> dict:
    today = date.today()
    with conn.cursor() as cur:
        # Base vendor info
        cur.execute("""
            SELECT id, company_name, trade, tier, bid_count, win_rate_pct,
                   avg_bid_amount, last_bid_date
            FROM vendors WHERE id = %s
        """, (vendor_id,))
        row = cur.fetchone()
        if not row:
            return {}
        vid, name, trade, tier, bid_count, win_rate, avg_amt, last_bid = row

        # Bid entries for this vendor across live projects
        cur.execute("""
            SELECT project_id, date_sent, date_received, status,
                   CASE WHEN date_received IS NOT NULL AND date_sent IS NOT NULL
                        THEN date_received - date_sent END AS response_days
            FROM bid_entries
            WHERE vendor_id = %s AND project_id = ANY(%s)
        """, (vendor_id, LIVE_PROJECT_IDS))
        entries = cur.fetchall()

    sent  = [e for e in entries if e[1] is not None]
    rcvd  = [e for e in entries if e[2] is not None or e[3] in ('received','bid_received','awarded')]
    resp_times = [e[4] for e in entries if e[4] is not None]

    # ── Response score (0-40) ──────────────────────────────────────────────
    if not sent:
        response_score = 20  # neutral — never contacted
        response_note  = "not yet contacted"
    elif not rcvd:
        days_waiting = (today - sent[0][1]).days if sent else 0
        if days_waiting <= 7:
            response_score = 25
            response_note  = f"sent {days_waiting}d ago, awaiting"
        elif days_waiting <= 14:
            response_score = 15
            response_note  = f"sent {days_waiting}d ago, no response"
        else:
            response_score = 0
            response_note  = f"sent {days_waiting}d ago, non-responsive"
    else:
        if resp_times:
            avg_resp = sum(resp_times, 0) / len(resp_times)
            if avg_resp <= 5:
                response_score = 40
            elif avg_resp <= 10:
                response_score = 35
            elif avg_resp <= 14:
                response_score = 28
            else:
                response_score = 20
            response_note = f"avg response {avg_resp:.0f}d"
        else:
            response_score = 30
            response_note  = "responded (no date recorded)"

    # ── Coverage score (0-30) ──────────────────────────────────────────────
    unique_projects = len(set(e[0] for e in entries))
    if unique_projects >= 3:
        coverage_score = 30
    elif unique_projects == 2:
        coverage_score = 20
    elif unique_projects == 1:
        coverage_score = 10
    else:
        coverage_score = 0

    # ── History score (0-30) ───────────────────────────────────────────────
    bc = bid_count or 0
    wr = float(win_rate or 0)
    if wr >= 30:
        history_score = 30
    elif wr >= 15:
        history_score = 25
    elif wr >= 5:
        history_score = 18
    elif bc >= 5:
        history_score = 12
    elif bc >= 1:
        history_score = 8
    else:
        history_score = 5  # brand new — neutral not penalized

    total = response_score + coverage_score + history_score
    grade = "A" if total >= 80 else "B" if total >= 60 else "C" if total >= 40 else "D"
    label = {"A": "Preferred", "B": "Active", "C": "Watch", "D": "Risk"}[grade]

    return {
        "vendor_id": vid,
        "company_name": name,
        "trade": trade or "—",
        "current_tier": tier,
        "score": total,
        "grade": grade,
        "label": label,
        "breakdown": {
            "response": response_score,
            "coverage": coverage_score,
            "history": history_score,
        },
        "response_note": response_note,
        "unique_projects": unique_projects,
        "bids_sent": len(sent),
        "bids_received": len(rcvd),
        "avg_response_days": round(sum(resp_times, 0) / len(resp_times), 1) if resp_times else None,
        "historical_win_rate": float(win_rate or 0),
        "avg_bid_amount": float(avg_amt or 0),
        "as_of": date.today().isoformat(),
    }


def score_all_vendors(conn, min_score: int = 0) -> list[dict]:
    """Score every vendor that has any engagement with live projects."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT DISTINCT vendor_id FROM bid_entries
            WHERE project_id = ANY(%s) AND vendor_id IS NOT NULL
        """, (LIVE_PROJECT_IDS,))
        vendor_ids = [row[0] for row in cur.fetchall()]

    results = []
    for vid in vendor_ids:
        s = score_vendor(vid, conn)
        if s and s.get("score", 0) >= min_score:
            results.append(s)
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def write_scores_to_db(scores: list[dict], conn) -> int:
    """Persist scores back to vendor_performance_scores table (upsert)."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vendor_performance_scores (
                id              SERIAL PRIMARY KEY,
                vendor_id       INTEGER NOT NULL REFERENCES vendors(id),
                score           INTEGER NOT NULL,
                grade           TEXT NOT NULL,
                label           TEXT NOT NULL,
                response_score  INTEGER,
                coverage_score  INTEGER,
                history_score   INTEGER,
                response_note   TEXT,
                unique_projects INTEGER,
                bids_sent       INTEGER,
                bids_received   INTEGER,
                scored_at       TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE (vendor_id)
            )
        """)
        count = 0
        for s in scores:
            cur.execute("""
                INSERT INTO vendor_performance_scores
                  (vendor_id, score, grade, label, response_score, coverage_score,
                   history_score, response_note, unique_projects, bids_sent, bids_received)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (vendor_id) DO UPDATE SET
                  score=EXCLUDED.score, grade=EXCLUDED.grade, label=EXCLUDED.label,
                  response_score=EXCLUDED.response_score, coverage_score=EXCLUDED.coverage_score,
                  history_score=EXCLUDED.history_score, response_note=EXCLUDED.response_note,
                  unique_projects=EXCLUDED.unique_projects, bids_sent=EXCLUDED.bids_sent,
                  bids_received=EXCLUDED.bids_received, scored_at=NOW()
            """, (s["vendor_id"], s["score"], s["grade"], s["label"],
                  s["breakdown"]["response"], s["breakdown"]["coverage"],
                  s["breakdown"]["history"], s["response_note"],
                  s["unique_projects"], s["bids_sent"], s["bids_received"]))
            count += 1
        conn.commit()
    return count
