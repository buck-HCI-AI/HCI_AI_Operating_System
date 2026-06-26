"""SOP 22 — COI / W-9 / Lien Waiver: execution service (Layers 1+2)."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import services.db as db
from shared.base_sop import BaseSOP
from shared.sop_data_model import SOPStatus
from shared.stop_condition import StopConditionChecker
from .sop_22_templates import REQUIRED_INPUT_KEYS, INPUT_LABELS, ComplianceDoc
from .sop_22_agent import SOP22Agent


class SOP22COIService(BaseSOP):
    SOP_NUMBER = "22"

    @classmethod
    def start_doc_collection(cls, project_id: int, sop_21_instance_id: int, owner_name: str) -> dict:
        instance = cls.create_instance(project_id=project_id, owner_name=owner_name, owner_role="pm",
                                        parent_instance_id=sop_21_instance_id)
        iid = instance["id"]
        cls.confirm_input(iid, "sop_21_instance_id", str(sop_21_instance_id))
        cls.transition_status(iid, SOPStatus.IN_PROGRESS, owner_name, "COI/W-9/Lien doc collection started")
        return {"instance": instance, "status": SOPStatus.IN_PROGRESS.value,
                "next_step": "Generate checklist via generate_doc_checklist() or add documents individually."}

    @classmethod
    def generate_doc_checklist(cls, instance_id: int, subs: list[str]) -> dict:
        result = SOP22Agent.generate_doc_checklist(subs, "")
        for item in result.get("checklist", []):
            doc = ComplianceDoc(
                doc_code=item.get("doc_code", "DOC-000"),
                doc_type=item.get("doc_type", "COI"),
                party_name=item.get("party_name", ""),
                party_role=item.get("party_role", "subcontractor"),
            )
            cls.save_output(instance_id, "compliance_doc", f"Doc — {doc.doc_type} / {doc.party_name}", content=doc.to_dict())
        return result

    @classmethod
    def mark_received(cls, instance_id: int, doc_code: str, actor: str = "pm") -> dict:
        return cls._update_doc_status(instance_id, doc_code, "RECEIVED", actor)

    @classmethod
    def verify_coi(cls, instance_id: int, doc_code: str, provided_limits: dict, verifier: str) -> dict:
        rows = db.query("SELECT id, content FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'compliance_doc' AND content->>'doc_code' = %s LIMIT 1",
                        (instance_id, doc_code))
        if not rows:
            return {"error": f"Doc {doc_code} not found"}
        row = rows[0]
        content = json.loads(row["content"]) if isinstance(row["content"], str) else row["content"]
        result = SOP22Agent.verify_coi_coverage(content.get("party_name", ""), provided_limits)
        content["ai_verified"] = True
        content["verified_by"] = verifier
        content["deficiencies"] = [str(d) for d in result.get("deficiencies", [])]
        content["status"] = "VERIFIED" if result.get("meets_minimums") else "REJECTED"
        db.execute("UPDATE sop_outputs SET content = %s WHERE id = %s", (json.dumps(content), row["id"]))
        cls._log_event(instance_id, "coi_verified", f"{doc_code}→{'PASS' if result.get('meets_minimums') else 'FAIL'}", verifier)
        return result

    @classmethod
    def pm_approve(cls, instance_id: int, pm_name: str) -> dict:
        rows = db.query("SELECT content FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'compliance_doc' AND content->>'doc_type' = 'COI' AND content->>'status' != 'VERIFIED'", (instance_id,))
        unverified_cois = len(rows)
        if unverified_cois > 0:
            return {"status": "blocked", "message": f"{unverified_cois} COIs not yet verified"}
        cls.transition_status(instance_id, SOPStatus.APPROVED, pm_name, "All compliance docs verified")
        return {"status": SOPStatus.APPROVED.value}

    @classmethod
    def hand_off_to_sop23(cls, instance_id: int, actor: str, project_id: int, owner_name: str,
                           superintendent_name: str, project_name: str, project_type: str,
                           construction_start: str) -> dict:
        StopConditionChecker.check_sc07_handoff_destination(instance_id, owner_name)
        cls.transition_status(instance_id, SOPStatus.HANDED_OFF, actor, "Handed off to SOP 23")
        from sop_23_project_startup.sop_23_service import SOP23ProjectStartupService
        sop23 = SOP23ProjectStartupService.start_startup(
            project_id, instance_id, owner_name,
            superintendent_name, project_name, project_type, construction_start,
        )
        return {"sop_22_status": SOPStatus.HANDED_OFF.value, "sop_23_instance": sop23}

    @classmethod
    def _update_doc_status(cls, instance_id: int, doc_code: str, status: str, actor: str) -> dict:
        rows = db.query("SELECT id, content FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'compliance_doc' AND content->>'doc_code' = %s LIMIT 1",
                        (instance_id, doc_code))
        if not rows:
            return {"error": f"Doc {doc_code} not found"}
        row = rows[0]
        content = json.loads(row["content"]) if isinstance(row["content"], str) else row["content"]
        content["status"] = status
        db.execute("UPDATE sop_outputs SET content = %s WHERE id = %s", (json.dumps(content), row["id"]))
        cls._log_event(instance_id, "doc_status_updated", f"{doc_code}→{status}", actor)
        return {"doc_code": doc_code, "status": status}

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
        instance = cls.get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}
        rows = db.query("SELECT COUNT(*) AS cnt FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'compliance_doc'", (instance_id,))
        total = rows[0]["cnt"] if rows else 0
        rows2 = db.query("SELECT COUNT(*) AS cnt FROM sop_outputs WHERE sop_instance_id = %s AND output_type = 'compliance_doc' AND content->>'status' = 'VERIFIED'", (instance_id,))
        verified = rows2[0]["cnt"] if rows2 else 0
        return {"instance": instance, "total_docs": total, "verified_docs": verified, "audit_trail": cls.get_audit_trail(instance_id)}
