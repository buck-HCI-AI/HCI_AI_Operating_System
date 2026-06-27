"""
Historical Cost Miner — enriches historical cost records from awarded bids.
Computes variance between bid amount and final cost.
Writes directly to historical_cost_records (safe enrichment of existing records).
"""
from .base_miner import BaseMiner, MiningResult


class HistoricalCostMiner(BaseMiner):
    MINER_NAME = "historical_cost_miner"
    SOURCE_SYSTEMS = ["postgres:bid_entries", "postgres:historical_cost_records"]
    TARGET_STORES = ["historical_cost_records"]

    def mine(self) -> MiningResult:
        run_id = self.start_run()
        result = MiningResult(self.MINER_NAME, run_id)
        try:
            self._sync_awarded_bids(result)
            self._compute_variances(result)
            self._generate_benchmarks(result)
            return self.complete_run(run_id, result)
        except Exception as e:
            return self.fail_run(run_id, str(e))

    def _sync_awarded_bids(self, result: MiningResult):
        """Create historical_cost_records for awarded bids that don't have one yet."""
        awarded = self._query("""
            SELECT be.id as bid_entry_id, be.bid_amount, be.date_received,
                   be.project_id, be.vendor_id,
                   bp.package_name, bp.csi_division,
                   v.company_name as vendor_name
            FROM bid_entries be
            JOIN bid_packages bp ON bp.id = be.bid_package_id
            LEFT JOIN vendors v ON v.id = be.vendor_id
            WHERE be.status = 'awarded'
              AND NOT EXISTS (
                  SELECT 1 FROM historical_cost_records hcr
                  WHERE hcr.bid_package_id = be.bid_package_id
                    AND hcr.project_id = be.project_id
              )
            LIMIT 100
        """)
        result.records_scanned += len(awarded)

        for bid in awarded:
            if not bid["bid_amount"] or not bid["project_id"]:
                continue
            self._execute("""
                INSERT INTO historical_cost_records
                    (project_id, bid_package_id, csi_division, scope_description,
                     awarded_amount, completed_date, notes, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'mining_auto')
                ON CONFLICT DO NOTHING
            """, (
                bid["project_id"],
                bid.get("bid_entry_id"),
                bid.get("csi_division"),
                bid.get("package_name"),
                bid["bid_amount"],
                bid.get("date_received"),
                f"Auto-synced from awarded bid entry {bid['bid_entry_id']}",
            ))
            result.items_auto_written += 1
            result.intelligence_extracted += 1

    def _compute_variances(self, result: MiningResult):
        """Compute variance_pct where final_cost and awarded_amount both exist."""
        records = self._query("""
            SELECT id, awarded_amount, final_cost
            FROM historical_cost_records
            WHERE awarded_amount IS NOT NULL
              AND final_cost IS NOT NULL
              AND (variance_pct IS NULL OR variance_pct = 0)
            LIMIT 50
        """)
        result.records_scanned += len(records)

        for rec in records:
            try:
                awarded = float(rec["awarded_amount"])
                final = float(rec["final_cost"])
                if awarded > 0:
                    variance = round(((final - awarded) / awarded) * 100, 2)
                    self._execute(
                        "UPDATE historical_cost_records SET variance_pct = %s WHERE id = %s",
                        (variance, rec["id"])
                    )
                    result.items_auto_written += 1
            except (TypeError, ZeroDivisionError):
                pass

    def _generate_benchmarks(self, result: MiningResult):
        """Compute per-CSI average costs and surface any outliers as intelligence."""
        benchmarks = self._query("""
            SELECT csi_division,
                   COUNT(*) as record_count,
                   AVG(awarded_amount) as avg_awarded,
                   AVG(final_cost) as avg_final,
                   AVG(variance_pct) as avg_variance_pct
            FROM historical_cost_records
            WHERE awarded_amount IS NOT NULL
            GROUP BY csi_division
            HAVING COUNT(*) >= 2
            ORDER BY csi_division
        """)
        result.summary["csi_benchmarks"] = len(benchmarks)
        result.summary["divisions_with_data"] = [b["csi_division"] for b in benchmarks if b["csi_division"]]

        for b in benchmarks:
            if b.get("avg_variance_pct") and abs(float(b["avg_variance_pct"])) > 15:
                self.queue_for_approval(
                    action_type="cost_variance_alert",
                    title=f"Cost variance alert: CSI {b['csi_division']}",
                    description=(
                        f"Division {b['csi_division']} shows avg variance of "
                        f"{b['avg_variance_pct']:.1f}% across {b['record_count']} records. "
                        "Review for estimating calibration."
                    ),
                    payload=dict(b),
                    priority="medium"
                )
                result.items_queued_for_review += 1
