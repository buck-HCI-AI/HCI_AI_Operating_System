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
    def _structured_context(question: str) -> list:
        """Opportunistically pull real structured DB context when the question
        looks like a cost or vendor-reliability question — cheaper and more exact
        than relying on vector search alone for numeric answers."""
        import re
        lines = []
        q = question.lower()

        csi_match = re.search(r'\bdivision\s*0?(\d{1,2})\b|\bcsi\s*0?(\d{1,2})\b', q)
        csi = None
        if csi_match:
            csi = (csi_match.group(1) or csi_match.group(2)).zfill(2)

        cost_words = ("cost", "price", "budget", "expensive", "$", "sqft", "square foot", "per foot")
        sub_words = ("reliable", "sub", "subcontractor", "vendor", "contractor", "trade", "who should")

        if any(w in q for w in cost_words):
            from historical_cost_svc import HistoricalCostService
            summary = HistoricalCostService.cost_benchmark_summary(csi_division=csi)
            if summary["by_division"]:
                lines.append("HISTORICAL COST BENCHMARKS (real, from historical_cost_records):")
                for g in summary["by_division"][:6]:
                    lines.append(
                        f"  Division {g['csi_division']}: n={g['sample_size']}, "
                        f"avg=${g['avg_awarded']:,.0f}, median=${g['median_awarded']:,.0f}, "
                        f"range=${g['min_awarded']:,.0f}-${g['max_awarded']:,.0f}"
                    )
                lines.append(f"  (limitation: {summary['known_limitation']})")

        if any(w in q for w in sub_words):
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

        return lines

    @classmethod
    def query(cls, question: str, max_sources: int = 8) -> dict:
        cache_key = f"field_brain:query:{hash(question)}"
        cached = cls.cache_get(cache_key)
        if cached:
            cached["cached"] = True
            return cached

        all_results = []
        seen = set()
        for collection in FIELD_COLLECTIONS:
            results = cls.search(question, collection=collection, limit=3)
            for r in results:
                key = r.get("text", "")[:100] or r.get("payload", {}).get("text", "")[:100]
                if key and key not in seen:
                    all_results.append(r)
                    seen.add(key)
            if len(all_results) >= max_sources:
                break
        all_results = all_results[:max_sources]

        structured_lines = cls._structured_context(question)
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
            "model_used": "claude-haiku-4-5-20251001",
            "cached": False,
        }
        cls.cache_set(cache_key, result, ttl=QUERY_TTL)
        return result
