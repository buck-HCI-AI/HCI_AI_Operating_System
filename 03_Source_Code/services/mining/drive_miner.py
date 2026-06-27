"""
Google Drive Miner — scans drive_sync_log for new/modified documents.
Classifies documents, infers project, extracts intelligence candidates.
Writes to: background_learning_records, approval_queue.
"""
from .base_miner import BaseMiner, MiningResult

_DOC_KEYWORDS = {
    "meeting": ["meeting", "minutes", "agenda", "oac", "preconstruction"],
    "bid": ["bid", "quote", "proposal", "pricing", "estimate"],
    "daily_log": ["daily log", "field report", "superintendent", "super daily"],
    "rfi": ["rfi", "request for information"],
    "submittal": ["submittal", "shop drawing", "product data"],
    "budget": ["budget", "gcmax", "cost", "allowance"],
    "schedule": ["schedule", "gantt", "lookahead", "milestone"],
    "drawing": ["drawing", "plan", "elevation", "section", "dwg"],
    "spec": ["spec", "specification", "division"],
    "contract": ["contract", "agreement", "subcontract"],
    "photo": ["photo", "image", "jpg", "jpeg", "png"],
}

_HIGH_VALUE = {"meeting", "daily_log", "rfi", "bid", "submittal"}


def _classify(name: str) -> str:
    name_lower = name.lower()
    for doc_type, keywords in _DOC_KEYWORDS.items():
        if any(kw in name_lower for kw in keywords):
            return doc_type
    return "other"


def _infer_project(name: str, path: str) -> tuple:
    text = (name + " " + path).lower()
    if "eastwood" in text or "64ew" in text:
        return 1, "64 Eastwood"
    if "francis" in text or "101f" in text:
        return 2, "101 Francis"
    if "riverside" in text or "1355" in text:
        return 3, "1355 Riverside"
    if "sagebrusch" in text or "83sb" in text:
        return 4, "83 Sagebrusch"
    return None, None


class DriveMiner(BaseMiner):
    MINER_NAME = "drive_miner"
    SOURCE_SYSTEMS = ["google_drive"]
    TARGET_STORES = ["background_learning_records", "approval_queue"]

    def mine(self) -> MiningResult:
        run_id = self.start_run()
        result = MiningResult(self.MINER_NAME, run_id)
        try:
            files = self._query("""
                SELECT file_path, file_name, file_type, synced_at
                FROM drive_sync_log
                ORDER BY synced_at DESC
                LIMIT 300
            """)
            result.records_scanned = len(files)

            for f in files:
                name = f.get("file_name") or ""
                path = f.get("file_path") or ""
                doc_type = _classify(name)
                project_id, project_name = _infer_project(name, path)

                rec_id = self.register_discovery(
                    source_system="google_drive",
                    source_id=path or name,
                    source_name=name,
                    project_id=project_id,
                    metadata={"doc_type": doc_type, "file_type": f.get("file_type"),
                               "project": project_name, "synced_at": str(f.get("synced_at"))}
                )
                if rec_id:
                    result.records_discovered += 1

                if doc_type in _HIGH_VALUE and project_id:
                    self.queue_for_approval(
                        action_type="document_intelligence",
                        title=f"New {doc_type.replace('_',' ')}: {name}",
                        description=(
                            f"High-value document detected in Google Drive for "
                            f"{project_name}. Approve to ingest into Project Brain."
                        ),
                        payload={"file_name": name, "file_path": path,
                                 "doc_type": doc_type, "project_id": project_id},
                        project_id=project_id,
                        priority="medium" if doc_type in ("bid", "rfi") else "low"
                    )
                    result.items_queued_for_review += 1
                    result.intelligence_extracted += 1

            result.summary = {
                "files_scanned": len(files),
                "high_value_queued": result.items_queued_for_review,
                "doc_types": {}
            }
            return self.complete_run(run_id, result)
        except Exception as e:
            return self.fail_run(run_id, str(e))
