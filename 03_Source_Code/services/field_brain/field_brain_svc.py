"""
Field Brain Service — cross-project historical intelligence, general-purpose.

Buck's framing (2026-07-08): "what does a similar build cost per sqft, who is the
most reliable sub for this type of job" were examples, not the whole spec — this
needs to answer hundreds of question shapes the field or GBT might ask, not just
those two. Same pattern as project_brain (retrieval + Claude synthesis), but
deliberately not scoped to one project: pulls from historical_cost_records,
vendors/bid_packages, lessons_learned, and every cross-project Qdrant collection.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from base import BaseIntelligenceService

QUERY_TTL = 300

# Cross-project collections — deliberately no project_number filter
FIELD_COLLECTIONS = [
    "hci_historical_costs",
    "vendor_memory",
    "hci_vendor_intelligence",
    "lessons_learned",
    "project_memory",
    "hci_project_documents",
    "drive_memory",
]

SYSTEM_PROMPT = """You are the Field Brain for Hendrickson Construction — a high-end
residential remodeler and builder in Aspen, Colorado. You answer cross-project
questions a PM or superintendent would ask in the field: what similar work has cost
historically, which subs perform reliably on which trades, what issues have come up
before on similar scopes, and what lessons apply to a new decision.

You draw on real historical cost records, vendor bid/award history, and lessons
learned across every past and current HCI project — not just one job.

Answer specifically and cite numbers with their source when you have them. If the
data doesn't cover what's being asked, say so plainly rather than guessing — a wrong
number is worse than an honest 'not enough historical data yet.' Be concise."""


class FieldBrainService(BaseIntelligenceService):
    SERVICE_NAME = "field_brain"
    STATUS = "active"

    @staticmethod
    def _detect_named_project(question: str) -> dict | None:
        """If the question names one specific job ('kitchen cabinet details on
        101F', 'what's in the plans for 606 Starwood'), resolve it so search can
        be scoped to just that job's own documents. Found live 2026-07-08 (Buck):
        asking about 101F's cabinets returned Sunnyside's and Starwood's cabinet
        docs mixed in - FIELD_COLLECTIONS is cross-project by design for
        comparison questions ('average cost per sqft across jobs'), but a
        single-job question has no business seeing other jobs' plans. Only scope
        when a job is actually named, so the comparison use case stays intact."""
        import re
        rows = FieldBrainService.pg_query("SELECT project_code, name FROM projects WHERE status != 'sandbox'")
        q_upper = question.upper()
        for r in rows:
            if r["project_code"] and re.search(rf'\b{re.escape(r["project_code"])}\b', q_upper):
                return r
        q_lower = question.lower()
        for r in rows:
            parts = (r["name"] or "").lower().split()
            num = next((p for p in parts if p.isdigit()), None)
            word = next((p for p in parts if p.isalpha() and len(p) > 2), None)
            if num and word and num in q_lower and word in q_lower:
                return r
        return None

    @staticmethod
    def _matches_project(result: dict, project: dict) -> bool:
        """Post-filter: Qdrant's project_number payload field is unpopulated on
        existing hci_project_documents rows and doesn't exist at all on
        drive_memory - the only reliable signal today is the source/filename
        path, which real Drive-synced chunks carry as '{Project Folder}/{file}'.
        Matches on address-key (house number + first street word) the same way
        _addr_key() does elsewhere in this codebase, so 'Ln.' vs 'Lane' style
        abbreviation differences don't cause false negatives."""
        payload = result.get("payload", {})
        source = (payload.get("source") or payload.get("original_filename") or "").lower()
        if not source:
            return False
        code = (project.get("project_code") or "").lower()
        if code and code in source:
            return True
        parts = (project.get("name") or "").lower().split()
        num = next((p for p in parts if p.isdigit()), None)
        word = next((p for p in parts if p.isalpha() and len(p) > 2), None)
        return bool(num and word and num in source and word in source)

    @staticmethod
    def _structured_context(question: str, named_project: dict | None = None) -> list:
        """Opportunistically pull real structured DB context when the question
        looks like a cost or vendor-reliability question — cheaper and more exact
        than relying on vector search alone for numeric answers.

        named_project (2026-07-08): when the question names one specific job,
        the cross-project cost-benchmark and vendor-reliability sections below
        are "other jobs' data" by definition (comps FROM other jobs to estimate
        THIS one) and get skipped entirely - Buck was explicit that a single-job
        question shouldn't reference other jobs at all. Risk patterns get scoped
        to just that project instead of skipped, since "risks on this job" is
        still a legitimate single-job question."""
        import re
        lines = []
        q = question.lower()

        csi_match = re.search(r'\bdivision\s*0?(\d{1,2})\b|\bcsi\s*0?(\d{1,2})\b', q)
        csi = None
        if csi_match:
            csi = (csi_match.group(1) or csi_match.group(2)).zfill(2)

        cost_words = ("cost", "price", "budget", "expensive", "$", "sqft", "square foot", "per foot")
        sqft_words = ("sqft", "square foot", "square feet", "per sf", "per foot", "/sf")
        sub_words = ("reliable", "sub", "subcontractor", "vendor", "contractor", "trade", "who should")

        if not named_project and any(w in q for w in sqft_words):
            from historical_cost_svc import HistoricalCostService
            bench = HistoricalCostService.sqft_benchmarks()
            if bench["comps"]:
                lines.append(
                    "REAL $/SF COMPS (2026-07-08 — learned from monitored/reference jobs with real "
                    "construction cost history, to inform estimates on the live pilot jobs, which are "
                    "still in permitting and have no cost history of their own yet):"
                )
                for c in bench["comps"]:
                    lines.append(
                        f"  {c['project_code']} ({c['project_type']}): ${c['cost_per_sf']:,.2f}/SF "
                        f"@ {c['gsf']:,.0f} SF, total ${c['total_cost']:,.0f} — {c['cost_basis']}"
                    )
                lines.append(f"  GSF-weighted average new-build $/SF: ${bench['weighted_avg_cost_per_sf']:,.2f}")
                lines.append(f"  {bench['note']}")
                sqft_num = re.search(r'(\d[\d,]{2,6})\s*(?:sq\.?\s*ft|sf\b|square)', q)
                if sqft_num:
                    target = float(sqft_num.group(1).replace(",", ""))
                    is_remodel = "remodel" in q or "renovation" in q or "existing" in q or not ("new build" in q or "new construction" in q)
                    est = HistoricalCostService.estimate_by_sqft(target, is_remodel)
                    if "error" not in est:
                        lines.append(
                            f"  Applied to {target:,.0f} SF ({'remodel' if is_remodel else 'new build'}): "
                            f"${est['estimate_low']:,.0f} - ${est['estimate_high']:,.0f} "
                            f"(expected ${est['estimate_expected']:,.0f})"
                        )

        if not named_project and any(w in q for w in cost_words):
            from historical_cost_svc import HistoricalCostService
            summary = HistoricalCostService.cost_benchmark_summary(csi_division=csi)
            if summary["by_division"]:
                lines.append("HISTORICAL COST BENCHMARKS BY CSI DIVISION (real, from historical_cost_records):")
                for g in summary["by_division"][:6]:
                    lines.append(
                        f"  Division {g['csi_division']}: n={g['sample_size']}, "
                        f"avg=${g['avg_awarded']:,.0f}, median=${g['median_awarded']:,.0f}, "
                        f"range=${g['min_awarded']:,.0f}-${g['max_awarded']:,.0f}"
                    )
                lines.append(f"  (limitation: {summary['known_limitation']})")

        if not named_project and any(w in q for w in sub_words):
            from vendor_intelligence_svc import VendorIntelligenceService
            ranked = VendorIntelligenceService.most_reliable(csi_division=csi, limit=8)
            if ranked["ranked_vendors"]:
                lines.append("\nRANKED VENDORS BY RELIABILITY (real, from vendors + award history):")
                for v in ranked["ranked_vendors"][:8]:
                    wr = f"{v['win_rate_pct']}%" if v.get("win_rate_pct") is not None else "n/a"
                    var = f"{v['avg_cost_variance_pct']}%" if v.get("avg_cost_variance_pct") is not None else "n/a"
                    lines.append(
                        f"  {v['company_name']} ({v.get('trade') or '—'}): "
                        f"win_rate={wr}, awarded_jobs={v.get('awarded_count') or 0}, "
                        f"avg_cost_variance={var}, bid_count={v['bid_count']}"
                    )

        # Buck, 2026-07-08: "we need more than just sqft details - we need full
        # picture of build questions that will be asked on site." Lessons learned
        # and risk patterns cover sequencing, lead times, code compliance, safety,
        # schedule drivers - the actual shape of on-site questions, not just cost/sub.
        # Pulled unconditionally (not gated behind a keyword list) because these
        # real 45 rows span too many real topics to enumerate trigger words for.
        try:
            from lessons_learned_svc import LessonsLearnedService
            ll = LessonsLearnedService.search_lessons(question)
            text_matches = ll.get("text_matches") or []
            if text_matches:
                lines.append("\nRELEVANT LESSONS LEARNED (real, from past HCI projects):")
                for l in text_matches[:5]:
                    lines.append(
                        f"  [{l.get('category', 'other')}"
                        f"{', Div ' + l['csi_division'] if l.get('csi_division') else ''}] "
                        f"{l.get('title', '')}: {(l.get('description') or '')[:200]}"
                        + (f" Recommendation: {l['future_recommendation'][:150]}" if l.get('future_recommendation') else "")
                    )
        except Exception:
            pass

        risk_words = ("risk", "issue", "problem", "delay", "watch out", "careful", "gotcha", "gone wrong")
        if any(w in q for w in risk_words):
            try:
                if named_project:
                    rows = FieldBrainService.pg_query("""
                        SELECT r.risk_type, r.severity, r.description, p.project_code
                        FROM risks r JOIN projects p ON p.id = r.project_id
                        WHERE r.status = 'open' AND p.project_code = %s
                        ORDER BY CASE r.severity WHEN 'critical' THEN 0 WHEN 'high' THEN 1
                                  WHEN 'medium' THEN 2 ELSE 3 END
                        LIMIT 8
                    """, (named_project["project_code"],))
                    header = f"\nOPEN RISKS ON {named_project['project_code']} (real, from risks table):"
                else:
                    rows = FieldBrainService.pg_query("""
                        SELECT r.risk_type, r.severity, r.description, p.project_code
                        FROM risks r JOIN projects p ON p.id = r.project_id
                        WHERE r.status = 'open'
                        ORDER BY CASE r.severity WHEN 'critical' THEN 0 WHEN 'high' THEN 1
                                  WHEN 'medium' THEN 2 ELSE 3 END
                        LIMIT 8
                    """)
                    header = "\nOPEN RISK PATTERNS ACROSS LIVE PROJECTS (real, from risks table):"
                if rows:
                    lines.append(header)
                    for r in rows:
                        lines.append(f"  [{r['severity']}] {r['project_code']} ({r['risk_type']}): {r['description'][:180]}")
            except Exception:
                pass

        return lines

    @classmethod
    def query(cls, question: str, max_sources: int = 8) -> dict:
        cache_key = f"field_brain:query:{hash(question)}"
        cached = cls.cache_get(cache_key)
        if cached:
            cached["cached"] = True
            return cached

        named_project = cls._detect_named_project(question)
        # Scoped to just that job's own plans/documents when one is named (Buck,
        # 2026-07-08) - skip the cross-project vendor/cost/lessons collections
        # entirely rather than searching them and filtering after, since a
        # single-job question has no business matching against other jobs' data
        # at all. Search wider (limit) since post-filtering by source path drops
        # most hits from other jobs' documents in the same collection.
        collections = ["drive_memory", "hci_project_documents"] if named_project else FIELD_COLLECTIONS
        per_collection_limit = max_sources * 4 if named_project else 3

        all_results = []
        seen = set()
        for collection in collections:
            results = cls.search(question, collection=collection, limit=per_collection_limit)
            for r in results:
                if named_project and not cls._matches_project(r, named_project):
                    continue
                key = r.get("text", "")[:100] or r.get("payload", {}).get("text", "")[:100]
                if key and key not in seen:
                    all_results.append(r)
                    seen.add(key)
            if len(all_results) >= max_sources:
                break
        all_results = all_results[:max_sources]

        structured_lines = cls._structured_context(question, named_project)
        context_lines = list(structured_lines)
        for r in all_results:
            text = r.get("payload", {}).get("text") or r.get("text", "")
            src = r.get("payload", {}).get("source") or r.get("payload", {}).get("original_filename", "")
            collection = r.get("collection", "")
            if text:
                context_lines.append(f"\n[Source: {src} ({collection})]\n{text[:500]}")

        context = "\n".join(context_lines) if context_lines else "No matching historical data found."
        prompt = f"FIELD CONTEXT:\n{context}\n\nQUESTION: {question}"
        answer = cls.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1024)

        sources = [
            {
                "text": (r.get("payload", {}).get("text", "") or r.get("text", ""))[:200],
                "source": r.get("payload", {}).get("source") or r.get("payload", {}).get("original_filename", ""),
                "score": round(r.get("score", 0), 3),
                "collection": r.get("collection", ""),
            }
            for r in all_results
        ]

        result = {
            "question": question,
            "answer": answer,
            "sources": sources,
            "structured_context_used": bool(structured_lines),
            "scoped_to_project": named_project["project_code"] if named_project else None,
            "model_used": "claude-haiku-4-5-20251001",
            "cached": False,
        }
        cls.cache_set(cache_key, result, ttl=QUERY_TTL)
        return result
