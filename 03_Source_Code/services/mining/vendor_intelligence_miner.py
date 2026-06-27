"""
Vendor Intelligence Miner — computes win rates, bid frequency, CSI coverage from bid data.
Enriches existing vendor records with performance intelligence.
Auto-writes to vendors table (enrichment only — no new vendors created without approval).
"""
from .base_miner import BaseMiner, MiningResult


class VendorIntelligenceMiner(BaseMiner):
    MINER_NAME = "vendor_intelligence_miner"
    SOURCE_SYSTEMS = ["postgres:bid_entries", "postgres:vendors"]
    TARGET_STORES = ["vendors"]

    def mine(self) -> MiningResult:
        run_id = self.start_run()
        result = MiningResult(self.MINER_NAME, run_id)
        try:
            self._compute_vendor_stats(result)
            self._flag_coverage_gaps(result)
            self._surface_top_performers(result)
            return self.complete_run(run_id, result)
        except Exception as e:
            return self.fail_run(run_id, str(e))

    def _compute_vendor_stats(self, result: MiningResult):
        stats = self._query("""
            SELECT
                be.vendor_id,
                COUNT(*) as total_bids,
                COUNT(*) FILTER (WHERE be.status = 'awarded') as awards,
                AVG(be.bid_amount) as avg_bid,
                MIN(be.date_received) as first_bid_date,
                MAX(be.date_received) as last_bid_date,
                array_agg(DISTINCT bp.csi_division) FILTER (WHERE bp.csi_division IS NOT NULL) as divisions
            FROM bid_entries be
            JOIN bid_packages bp ON bp.id = be.bid_package_id
            WHERE be.vendor_id IS NOT NULL
            GROUP BY be.vendor_id
        """)
        result.records_scanned = len(stats)

        for s in stats:
            total = s["total_bids"] or 0
            awards = s["awards"] or 0
            win_rate = round((awards / total) * 100, 1) if total > 0 else 0.0

            # Update vendor performance fields
            self._execute("""
                UPDATE vendors SET
                    bid_count = %s,
                    win_rate_pct = %s,
                    last_bid_date = %s,
                    avg_bid_amount = %s
                WHERE id = %s
            """, (total, win_rate, s.get("last_bid_date"), s.get("avg_bid"), s["vendor_id"]))
            result.items_auto_written += 1
            result.intelligence_extracted += 1

        result.summary["vendors_updated"] = result.items_auto_written

    def _flag_coverage_gaps(self, result: MiningResult):
        """Flag CSI divisions where we have fewer than 3 vendors."""
        coverage = self._query("""
            SELECT bp.csi_division, COUNT(DISTINCT be.vendor_id) as vendor_count
            FROM bid_packages bp
            LEFT JOIN bid_entries be ON be.bid_package_id = bp.id
            WHERE bp.csi_division IS NOT NULL
            GROUP BY bp.csi_division
            HAVING COUNT(DISTINCT be.vendor_id) < 3
            ORDER BY vendor_count ASC
            LIMIT 20
        """)

        gaps = [{"division": g["csi_division"], "vendors": g["vendor_count"]} for g in coverage]
        if gaps:
            result.summary["coverage_gaps"] = gaps
            self.queue_for_approval(
                action_type="vendor_coverage_gap",
                title=f"Vendor coverage gaps: {len(gaps)} CSI divisions need more vendors",
                description=(
                    f"{len(gaps)} CSI divisions have fewer than 3 vendors. "
                    f"Top gaps: {', '.join(g['division'] for g in gaps[:5] if g['division'])}. "
                    "Review to expand vendor registry."
                ),
                payload={"gaps": gaps},
                priority="low"
            )
            result.items_queued_for_review += 1

    def _surface_top_performers(self, result: MiningResult):
        top = self._query("""
            SELECT v.company_name, v.win_rate_pct, v.bid_count, v.csi_divisions
            FROM vendors v
            WHERE v.win_rate_pct IS NOT NULL AND v.bid_count >= 3
            ORDER BY v.win_rate_pct DESC
            LIMIT 10
        """)
        result.summary["top_performers"] = [
            {"vendor": r["company_name"], "win_rate": r["win_rate_pct"], "bids": r["bid_count"]}
            for r in top
        ]
