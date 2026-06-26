"""SOP 25 — Daily Log: Layer 4 data fields and validators."""
from __future__ import annotations
from dataclasses import dataclass, field

REQUIRED_INPUT_KEYS = [
    "project_id", "superintendent_name", "sop_23_instance_id",
]

INPUT_LABELS = {
    "project_id":           "Project ID",
    "superintendent_name":  "Superintendent name",
    "sop_23_instance_id":   "SOP 23 Project Startup — completed instance ID",
}

WEATHER_CONDITIONS = ["clear", "partly_cloudy", "overcast", "rain", "heavy_rain", "wind", "fog", "snow"]
LOG_STATUS = ["OPEN", "CLOSED", "LOCKED"]


@dataclass
class DailyLogEntry:
    log_date: str
    weather: str
    temperature_hi: int = 0
    temperature_lo: int = 0
    wind_mph: int = 0
    work_performed: list[str] = field(default_factory=list)
    crews_on_site: list[dict] = field(default_factory=list)
    total_workers: int = 0
    equipment_on_site: list[str] = field(default_factory=list)
    materials_received: list[str] = field(default_factory=list)
    visitors: list[str] = field(default_factory=list)
    delays: list[dict] = field(default_factory=list)
    safety_observations: list[str] = field(default_factory=list)
    incidents: list[dict] = field(default_factory=list)
    rfi_refs: list[str] = field(default_factory=list)
    inspector_visits: list[str] = field(default_factory=list)
    superintendent_notes: str = ""
    status: str = "OPEN"
    ai_risk_flags: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        errors = []
        if not self.log_date:
            errors.append("log_date required (YYYY-MM-DD)")
        if self.weather not in WEATHER_CONDITIONS:
            errors.append(f"weather must be one of {WEATHER_CONDITIONS}")
        if self.status not in LOG_STATUS:
            errors.append(f"status must be one of {LOG_STATUS}")
        return errors

    def to_dict(self) -> dict:
        return {
            "log_date": self.log_date,
            "weather": self.weather,
            "temperature_hi": self.temperature_hi,
            "temperature_lo": self.temperature_lo,
            "wind_mph": self.wind_mph,
            "work_performed": self.work_performed,
            "crews_on_site": self.crews_on_site,
            "total_workers": self.total_workers,
            "equipment_on_site": self.equipment_on_site,
            "materials_received": self.materials_received,
            "visitors": self.visitors,
            "delays": self.delays,
            "safety_observations": self.safety_observations,
            "incidents": self.incidents,
            "rfi_refs": self.rfi_refs,
            "inspector_visits": self.inspector_visits,
            "superintendent_notes": self.superintendent_notes,
            "status": self.status,
            "ai_risk_flags": self.ai_risk_flags,
        }


class SOP25Templates:
    REQUIRED_INPUT_KEYS = REQUIRED_INPUT_KEYS
    INPUT_LABELS = INPUT_LABELS
    WEATHER_CONDITIONS = WEATHER_CONDITIONS
    LOG_STATUS = LOG_STATUS
