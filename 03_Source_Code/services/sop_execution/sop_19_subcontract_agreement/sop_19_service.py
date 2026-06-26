"""SOP 19 — Subcontract Agreement: execution service (Layers 1+2)."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
from datetime import date
import services.db as db
from shared.base_sop import BaseSOP
from shared.sop_data_model import SOPStatus
from shared.stop_condition import StopConditionChecker
from shared.approval_engine import ApprovalEngine
from shared.sop_kpi import SOPKPITracker
from .sop_19_templates import (
    REQUIRED_INPUT_KEYS, INPUT_LABELS, CONTRACT_SECTIONS,
    SubcontractSection, EXECUTION_AUTHORITY,
)
from .sop_19_agent import SOP19Agent


class SOP19SubcontractAgreementService(BaseSOP):
    SOP_NUMBER = "19"

    @classmethod
    def start_agreement(cls, project_id: int, sop_16_instance_id: int,
                         awarded_sub: str, award_amount: float,
                         scope_basis: str, trade_name: str,
                         trade_code: str, owner_name: str) -> dict:
        """Create SOP 19 instance. Triggered from SOP 16 handoff."""
        instance = cls.create_instance(
            project_id=project_id,
            owner_name=owner_name,
            owner_role="pm",
            parent_instance_id=sop_16_instance_id,
        )
        iid = instance["id"]
        cls.confirm_input(iid, "sop_16_instance_id", str(sop_16_instance_id))
        cls.confirm_input(iid, "awarded_sub", awarded_sub)
        cls.confirm_input(iid, "award_amount", str(award_amount))
        cls.confirm_input(iid, "scope_basis", scope_basis)
        cls.confirm_input(iid, "trade_name", trade_name)
        cls.confirm_input(iid, "trade_code", trade_code)

        cls.transition_status(iid, SOPStatus.IN_PROGRESS, owner_name,
                              f"Subcontract agreement started — {awarded_sub}")
        return {"instance": instance, "status": SOPStatus.IN_PROGRESS.value,
                "awarded_sub": awarded_sub, "award_amount": award_amount,
                "next_step": "Draft all sections via run_ai_draft_all() or draft individual sections."}

    @classmethod
    def _load_inputs(cls, instance_id: int) -> dict:
        rows = db.query("""
            SELECT input_key, confirmed_by FROM sop_inputs WHERE sop_instance_id = %s
        """, (instance_id,))
        return {r["input_key"]: r["confirmed_by"] for r in rows}

    @classmethod
    def run_ai_draft_all(cls, instance_id: int) -> dict:
        """Layer 3: AI drafts all standard contract sections at once."""
        inputs = cls._load_inputs(instance_id)
        awarded_sub = inputs.get("awarded_sub", "")
        trade_name = inputs.get("trade_name", "")
        trade_code = inputs.get("trade_code", "")
        award_amount = float(inputs.get("award_amount", 0))
        scope_basis = inputs.get("scope_basis", "")

        results = {}

        # Draft scope section first
        scope_draft = SOP19Agent.draft_scope_section(
            awarded_sub, trade_name, trade_code, scope_basis, award_amount
        )
        cls._save_section(instance_id, scope_draft)
        results["scope_of_work"] = scope_draft

        # Draft remaining sections
        for section_type in CONTRACT_SECTIONS:
            if section_type == "scope_of_work":
                continue
            draft = SOP19Agent.draft_contract_section(
                section_type, awarded_sub, trade_name, award_amount
            )
            cls._save_section(instance_id, draft)
            results[section_type] = draft

        cur = cls.get_instance(instance_id)
        if cur and cur["status"] != SOPStatus.AI_DRAFTED.value:
            cls.transition_status(instance_id, SOPStatus.AI_DRAFTED, "AI",
                                  "All subcontract sections drafted by AI")

        return {"sections_drafted": len(results), "results": results,
                "next_step": "PM to review each section via confirm_section(), then call pm_approve()."}

    @classmethod
    def draft_section(cls, instance_id: int, section_type: str,
                      content: str = "", actor: str = "pm") -> dict:
        """PM manually drafts or overrides a contract section."""
        if section_type not in CONTRACT_SECTIONS:
            return {"status": "validation_error",
                    "errors": [f"section_type must be one of {CONTRACT_SECTIONS}"]}
        section = SubcontractSection(
            section_type=section_type, content=content, ai_drafted=False
        )
        output_id = cls._save_section(instance_id, section.to_dict())
        cls._log_event(instance_id, "section_drafted", section_type, actor)
        return {"output_id": output_id, "section_type": section_type}

    @classmethod
    def confirm_section(cls, instance_id: int, section_type: str,
                        pm_name: str) -> dict:
        """PM confirms a drafted section is acceptable."""
        rows = db.query("""
            SELECT id, content FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'subcontract_section'
            AND content->>'section_type' = %s ORDER BY id DESC LIMIT 1
        """, (instance_id, section_type))
        if not rows:
            return {"error": f"No section found for type '{section_type}'"}

        row = rows[0]
        content = json.loads(row["content"]) if isinstance(row["content"], str) else row["content"]
        content["pm_confirmed"] = True
        db.execute("UPDATE sop_outputs SET content = %s WHERE id = %s",
                   (json.dumps(content), row["id"]))
        cls._log_event(instance_id, "section_confirmed", section_type, pm_name)
        confirmed_count = cls._count_confirmed_sections(instance_id)
        return {"section_type": section_type, "confirmed": True,
                "confirmed_sections": confirmed_count,
                "total_sections": len(CONTRACT_SECTIONS)}

    @classmethod
    def verify_insurance(cls, instance_id: int,
                          provided_limits: dict) -> dict:
        """Check sub's insurance against HCI minimums."""
        inputs = cls._load_inputs(instance_id)
        result = SOP19Agent.verify_insurance_requirements(
            inputs.get("awarded_sub", ""), provided_limits
        )
        cls.save_output(instance_id, "insurance_verification",
                        "Insurance Verification", content=result)
        cls._log_event(instance_id, "insurance_verified",
                       "meets_minimums=" + str(result.get("meets_minimums")), "system")
        return result

    @classmethod
    def run_final_review(cls, instance_id: int) -> dict:
        """AI reviews all sections together before PM approval."""
        rows = db.query("""
            SELECT content FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'subcontract_section'
        """, (instance_id,))
        sections = [
            json.loads(r["content"]) if isinstance(r["content"], str) else r["content"]
            for r in rows
        ]
        inputs = cls._load_inputs(instance_id)
        result = SOP19Agent.review_full_draft(
            sections,
            inputs.get("awarded_sub", ""),
            inputs.get("trade_name", ""),
            float(inputs.get("award_amount", 0)),
        )
        cls.save_output(instance_id, "final_review", "AI Final Review", content=result)
        return result

    @classmethod
    def pm_approve(cls, instance_id: int, pm_name: str) -> dict:
        """PM routes subcontract draft to execution authority."""
        confirmed = cls._count_confirmed_sections(instance_id)
        if confirmed < len(CONTRACT_SECTIONS):
            return {
                "status": "blocked",
                "message": (
                    f"Only {confirmed}/{len(CONTRACT_SECTIONS)} sections confirmed. "
                    "All sections must be PM-confirmed before routing to execution."
                ),
            }
        cls.transition_status(instance_id, SOPStatus.INTERNAL_REVIEW, pm_name,
                              "PM reviewing complete draft")
        cls.transition_status(instance_id, SOPStatus.APPROVAL_REQUIRED, pm_name,
                              "Subcontract ready for execution — routed to signing authority")
        return {"status": SOPStatus.APPROVAL_REQUIRED.value,
                "confirmed_sections": confirmed,
                "next_step": f"Execute subcontract via record_execution(). {EXECUTION_AUTHORITY} required."}

    @classmethod
    def record_execution(cls, instance_id: int, executed_by: str,
                          subcontract_number: str,
                          execution_date: str | None = None) -> dict:
        """Gate 19-C: record subcontract execution. Requires principal/PM signature."""
        exec_date = execution_date or date.today().isoformat()

        ApprovalEngine.create_gate_record(
            sop_instance_id=instance_id,
            gate_id="AG-19-C",
            gate_name="Subcontract Execution Authority",
            required_before_status=SOPStatus.ISSUED.value,
            approver_name=executed_by,
            approver_role="Principal/PM",
        )

        cls.save_output(instance_id, "execution_record", "Subcontract Execution Record",
                        content={
                            "executed_by": executed_by,
                            "execution_date": exec_date,
                            "subcontract_number": subcontract_number,
                        })

        inputs = cls._load_inputs(instance_id)
        award_amount = float(inputs.get("award_amount", 0))

        cls.transition_status(instance_id, SOPStatus.APPROVED, executed_by,
                              f"Gate 19-C: Executed by {executed_by}")
        cls.transition_status(instance_id, SOPStatus.ISSUED, executed_by,
                              f"Subcontract #{subcontract_number} executed and issued")

        row = db.query_one("SELECT project_id FROM sop_instances WHERE id = %s",
                           (instance_id,))
        pid = row["project_id"] if row else None
        SOPKPITracker.record_kpi(instance_id, "SOP19_SUBCONTRACT_VALUE",
                                  award_amount, "$", pid)

        return {"status": SOPStatus.ISSUED.value, "gate": "AG-19-C",
                "executed_by": executed_by, "subcontract_number": subcontract_number,
                "execution_date": exec_date,
                "next_step": "Archive via archive() when all parties have signed copies."}

    @classmethod
    def archive(cls, instance_id: int, actor: str = "pm") -> dict:
        """Archive the completed subcontract. Final status: Archived."""
        StopConditionChecker.check_sc04_approval_gate(
            instance_id, "AG-19-C", "Subcontract Execution Authority"
        )
        cls.transition_status(instance_id, SOPStatus.HANDED_OFF, actor,
                              "Subcontract archived — project execution phase")
        cls.transition_status(instance_id, SOPStatus.ARCHIVED, actor,
                              "Subcontract agreement complete and archived")
        return {"status": SOPStatus.ARCHIVED.value}

    @classmethod
    def _save_section(cls, instance_id: int, section_dict: dict) -> int:
        section_type = section_dict.get("section_type", "unknown")
        output_id = cls.save_output(
            instance_id, "subcontract_section",
            f"Section — {section_type}", content=section_dict
        )
        return output_id

    @classmethod
    def _count_confirmed_sections(cls, instance_id: int) -> int:
        rows = db.query("""
            SELECT COUNT(DISTINCT content->>'section_type') AS cnt
            FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'subcontract_section'
            AND (content->>'pm_confirmed')::boolean = TRUE
        """, (instance_id,))
        return rows[0]["cnt"] if rows else 0

    @classmethod
    def get_full_status(cls, instance_id: int) -> dict:
        instance = cls.get_instance(instance_id)
        if not instance:
            return {"error": "Instance not found"}
        missing = cls.get_missing_inputs(instance_id, REQUIRED_INPUT_KEYS)
        confirmed = cls._count_confirmed_sections(instance_id)
        rows = db.query("""
            SELECT content->>'section_type' AS sec_type,
                   (content->>'pm_confirmed')::boolean AS confirmed
            FROM sop_outputs
            WHERE sop_instance_id = %s AND output_type = 'subcontract_section'
        """, (instance_id,))
        sections = [dict(r) for r in rows]
        gates = ApprovalEngine.get_gates(instance_id)
        return {
            "instance": instance,
            "missing_inputs": [INPUT_LABELS.get(k, k) for k in missing],
            "sections": sections,
            "confirmed_sections": confirmed,
            "total_required_sections": len(CONTRACT_SECTIONS),
            "approval_gates": gates,
            "audit_trail": cls.get_audit_trail(instance_id),
        }
