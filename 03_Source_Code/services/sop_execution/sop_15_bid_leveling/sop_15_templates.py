"""SOP 15 — Layer 4: Data field definitions for bid leveling."""
from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import date


MIN_RESPONSIVE_BIDS = 3  # configurable via Operating Rules Engine


@dataclass
class BidAdjustment:
    description: str
    amount: float  # positive = add to base, negative = deduct
    reason: str
    is_estimate: bool = False  # True if amount is estimated, not quoted


@dataclass
class BidRecord:
    bidder_name: str
    bid_amount_base: float
    bid_received_date: str
    bid_responsive: bool = True
    bidder_id: int | None = None
    qualifications_raw: str = ""
    qualifications_parsed: dict = field(default_factory=dict)
    alternates_included: list[dict] = field(default_factory=list)
    alternates_excluded: list[dict] = field(default_factory=list)
    exclusions_list: list[str] = field(default_factory=list)
    scope_inclusions: list[str] = field(default_factory=list)
    adjustment_items: list[BidAdjustment] = field(default_factory=list)
    risk_flags: list[dict] = field(default_factory=list)
    contract_qualifications: list[str] = field(default_factory=list)
    schedule_exceptions: list[str] = field(default_factory=list)
    prior_performance_score: float | None = None
    recommendation_flag: str = "pending"  # recommended / caution / reject / pending
    recommendation_reason: str = ""

    @property
    def bid_amount_adjusted(self) -> float:
        total_adjustments = sum(a.amount for a in self.adjustment_items)
        return round(self.bid_amount_base + total_adjustments, 2)

    def to_dict(self) -> dict:
        return {
            "bidder_name": self.bidder_name,
            "bid_amount_base": self.bid_amount_base,
            "bid_amount_adjusted": self.bid_amount_adjusted,
            "adjustments": [
                {"description": a.description, "amount": a.amount,
                 "reason": a.reason, "is_estimate": a.is_estimate}
                for a in self.adjustment_items
            ],
            "bid_received_date": self.bid_received_date,
            "bid_responsive": self.bid_responsive,
            "exclusions_list": self.exclusions_list,
            "contract_qualifications": self.contract_qualifications,
            "schedule_exceptions": self.schedule_exceptions,
            "risk_flags": self.risk_flags,
            "prior_performance_score": self.prior_performance_score,
            "recommendation_flag": self.recommendation_flag,
            "recommendation_reason": self.recommendation_reason,
        }


@dataclass
class LevelingOutput:
    instance_id: int
    project_id: int
    trade_name: str
    bids: list[BidRecord]
    ai_recommendation: dict = field(default_factory=dict)
    buck_award: dict | None = None

    @property
    def responsive_bids(self) -> list[BidRecord]:
        return [b for b in self.bids if b.bid_responsive]

    @property
    def low_adjusted_bid(self) -> float | None:
        amounts = [b.bid_amount_adjusted for b in self.responsive_bids]
        return min(amounts) if amounts else None

    def to_comparison_table(self) -> list[dict]:
        low = self.low_adjusted_bid or 1
        return sorted([
            {
                "bidder": b.bidder_name,
                "base_bid": b.bid_amount_base,
                "adjustments": b.bid_amount_adjusted - b.bid_amount_base,
                "adjusted_total": b.bid_amount_adjusted,
                "vs_low": round(b.bid_amount_adjusted - low, 2),
                "pct_over_low": round((b.bid_amount_adjusted - low) / low * 100, 1),
                "risk_level": "HIGH" if any(f.get("severity") == "HIGH"
                                            for f in b.risk_flags) else "LOW",
                "perf_score": b.prior_performance_score,
                "rec_flag": b.recommendation_flag,
            }
            for b in self.responsive_bids
        ], key=lambda x: x["adjusted_total"])


class SOP15Templates:
    MIN_RESPONSIVE_BIDS = MIN_RESPONSIVE_BIDS
