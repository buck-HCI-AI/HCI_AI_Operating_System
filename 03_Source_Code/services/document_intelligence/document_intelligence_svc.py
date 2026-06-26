"""Document Intelligence Service — smart document retrieval and classification."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from base import BaseIntelligenceService


class DocumentIntelligenceService(BaseIntelligenceService):
    SERVICE_NAME = "document_intelligence"
    STATUS = "active"

    @staticmethod
    def search_documents(query: str, project_number: str = None,
                         category: str = None) -> dict:
        filters = {}
        if project_number:
            filters["project_number"] = project_number
        if category:
            filters["document_category"] = category

        # Search both drive_memory and project documents
        drive_results = BaseIntelligenceService.search(
            query, collection="drive_memory", limit=6,
            project_filter=project_number)
        proj_results  = BaseIntelligenceService.search(
            query, collection="hci_project_documents", limit=6,
            project_filter=project_number)

        # Merge and deduplicate by text prefix
        all_results, seen = [], set()
        for r in drive_results + proj_results:
            key = r.get("text", "")[:80]
            if key not in seen:
                all_results.append(r)
                seen.add(key)
        all_results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return {"query": query, "results": all_results[:10], "total": len(all_results)}

    @staticmethod
    def classify_document(filename: str, content_preview: str = "") -> dict:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "ingestion"))
        from classifier import classify, load_project_aliases_from_db
        aliases = load_project_aliases_from_db()
        result = classify(filename, content_preview, aliases)
        return {"filename": filename, "classification": result}

    @staticmethod
    def ingest_document(file_path: str, source_system: str = "api",
                        project_hint: str = None) -> dict:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "ingestion"))
        from ingest import ingest_file
        return ingest_file(file_path, source_system=source_system, project_hint=project_hint)
