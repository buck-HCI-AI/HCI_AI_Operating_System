"""Operating Rules Engine — evaluate and manage configurable business rules."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))

import json
from dataclasses import dataclass
import services.db as db
from base import BaseIntelligenceService


@dataclass
class RuleEvalResult:
    matched: bool
    rule_code: str
    rule_name: str
    action: str       # block / alert / escalate / require_input / pass
    action_target: str
    authority: str
    message: str


class OperatingRulesService(BaseIntelligenceService):
    SERVICE_NAME = "operating_rules"
    STATUS = "active"

    @classmethod
    def evaluate_rule(cls, context: str, field: str, value) -> RuleEvalResult:
        """
        Evaluate all active rules that match the given context and field.
        Returns the most severe matching rule result, or a 'pass' result.
        """
        rows = cls.pg_query("""
            SELECT rule_code, rule_name, applies_to, condition_field,
                   condition_op, condition_value, action, action_target, authority
            FROM operating_rules
            WHERE active = TRUE
            AND (applies_to = %s OR applies_to = 'all' OR applies_to = 'all_projects')
            AND condition_field = %s
        """, (context, field))

        worst_result = None
        severity_rank = {"block": 3, "escalate": 2, "alert": 1, "require_input": 1}

        for row in rows:
            op = row["condition_op"]
            try:
                threshold = type(value)(row["condition_value"])
            except (ValueError, TypeError):
                threshold = row["condition_value"]

            matched = False
            if op == ">" and value > threshold:
                matched = True
            elif op == ">=" and value >= threshold:
                matched = True
            elif op == "<" and value < threshold:
                matched = True
            elif op == "<=" and value <= threshold:
                matched = True
            elif op == "==" and str(value) == str(threshold):
                matched = True
            elif op == "!=" and str(value) != str(threshold):
                matched = True

            if matched:
                result = RuleEvalResult(
                    matched=True,
                    rule_code=row["rule_code"],
                    rule_name=row["rule_name"],
                    action=row["action"],
                    action_target=row["action_target"] or "",
                    authority=row["authority"] or "",
                    message=f"Rule {row['rule_code']} triggered: {row['rule_name']}"
                )
                if worst_result is None or (
                    severity_rank.get(row["action"], 0) >
                    severity_rank.get(worst_result.action, 0)
                ):
                    worst_result = result

        return worst_result or RuleEvalResult(
            matched=False, rule_code="", rule_name="", action="pass",
            action_target="", authority="",
            message=f"No rule matched for {context}.{field} = {value}"
        )

    @classmethod
    def list_rules(cls, category: str | None = None,
                   active_only: bool = True) -> list[dict]:
        params: list = []
        conditions = []
        if active_only:
            conditions.append("active = TRUE")
        if category:
            conditions.append("rule_category = %s")
            params.append(category)
        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        rows = cls.pg_query(f"""
            SELECT rule_code, rule_name, rule_category, applies_to,
                   condition_field, condition_op, condition_value,
                   action, action_target, authority, active, effective_date
            FROM operating_rules {where}
            ORDER BY rule_category, rule_code
        """, params or None)
        return [dict(r) for r in rows]

    @classmethod
    def get_rule(cls, rule_code: str) -> dict | None:
        row = cls.pg_one(
            "SELECT * FROM operating_rules WHERE rule_code = %s", (rule_code,)
        )
        return dict(row) if row else None

    @classmethod
    def update_rule(cls, rule_code: str, condition_value: str | None = None,
                    action: str | None = None, active: bool | None = None,
                    change_reason: str = "", modified_by: str = "") -> dict:
        """Update a rule. Logs previous state for audit."""
        current = cls.pg_one(
            "SELECT * FROM operating_rules WHERE rule_code = %s", (rule_code,)
        )
        if not current:
            return {"error": f"Rule {rule_code} not found"}

        prev = dict(current)
        updates, params = [], []
        if condition_value is not None:
            updates.append("condition_value = %s")
            params.append(condition_value)
        if action is not None:
            updates.append("action = %s")
            params.append(action)
        if active is not None:
            updates.append("active = %s")
            params.append(active)

        updates += ["previous_value = %s", "change_reason = %s",
                    "modified_by = %s", "updated_at = NOW()"]
        params += [json.dumps(prev), change_reason, modified_by]
        params.append(rule_code)

        cls.pg_execute(
            f"UPDATE operating_rules SET {', '.join(updates)} WHERE rule_code = %s",
            params
        )
        return {"rule_code": rule_code, "updated": True}

    @classmethod
    def create_exception(cls, rule_code: str, exception_reason: str,
                         risk_accepted: str, mitigation: str, approver: str,
                         expires_at: str, created_by: str,
                         sop_instance_id: int | None = None,
                         project_id: int | None = None) -> dict:
        """Record a rule exception. All fields required — no silent bypasses."""
        row = cls.pg_execute_returning("""
            INSERT INTO operating_rule_exceptions
                (rule_code, sop_instance_id, project_id, exception_reason,
                 risk_accepted, mitigation, approver, expires_at, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s::TIMESTAMPTZ, %s)
            RETURNING id
        """, (rule_code, sop_instance_id, project_id, exception_reason,
              risk_accepted, mitigation, approver, expires_at, created_by))
        return {"exception_id": row["id"], "rule_code": rule_code}
