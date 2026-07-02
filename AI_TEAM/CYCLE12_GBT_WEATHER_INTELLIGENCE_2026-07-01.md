# CYCLE 12 - GBT WEATHER INTELLIGENCE ARCHITECTURE
**Date:** 2026-07-01
**Cycle:** 12
**Priority:** Sprint 4 #5
**Status:** SPEC COMPLETE - Awaiting Claude Code implementation
**Author:** HCI Chief Architect (GBT) via BC Operations Intelligence

---

## 1. Construction-Specific Weather Triggers

### 1.1 Concrete Pour
| Threshold | Health | Action |
|-----------|--------|--------|
| air_temp < 40F OR forecast_low < 35F | YELLOW | Flag for PM/Super review |
| air_temp < 32F OR active frost warning | RED | Block - Super confirmation required |
| wind_speed > 25 mph | YELLOW | Monitor - surface drying risk |
| wind_speed > 35 mph | RED | Block - uneven cure risk |
| rain probability > 40% within 4 hours | YELLOW | Flag - protect surfaces |
| rain probability > 70% OR active precip | RED | Block - wash-out risk |

### 1.2 Foundation Pour / Frost Risk
| Threshold | Health | Action |
|-----------|--------|--------|
| forecast_low <= 32F | YELLOW | Flag for PM/Super review |
| forecast_low <= 20F OR active frost warning | RED | Block - soil heave risk |

### 1.3 Roofing
| Threshold | Health | Action |
|-----------|--------|--------|
| wind_speed >= 20 mph | YELLOW | Flag |
| wind_gust >= 25 mph | YELLOW | Flag |
| precipitation_probability >= 30% | YELLOW | Flag |
| wind_speed >= 30 mph OR wind_gust >= 40 mph | RED | Block - OSHA fall protection |
| active precipitation | RED | Block |

### 1.4 Crane Operations
| Threshold | Health | Action |
|-----------|--------|--------|
| wind_speed >= 20 mph | YELLOW | Flag - operator assessment required |
| wind_speed >= 30 mph | RED | Block - OSHA crane wind limit |
| wind_gust >= 35 mph | RED | Block |
| lightning within 10 miles | RED | Block immediately |

### 1.5 Exterior Painting / Coatings
| Threshold | Health | Action |
|-----------|--------|--------|
| air_temp < 50F | YELLOW | Flag - check manufacturer specs |
| relative_humidity >= 80% | YELLOW | Flag |
| air_temp < 40F | RED | Block |
| relative_humidity >= 90% | RED | Block |
| active precipitation | RED | Block |

### 1.6 Excavation / Sitework Rain Saturation
| Threshold | Health | Action |
|-----------|--------|--------|
| precipitation_probability >= 50% | YELLOW | Flag - soil saturation risk |
| recent_rainfall > 1 inch/24h | YELLOW | Flag - soil instability check |
| active precipitation >= moderate | RED | Block - OSHA cave-in |
| recent_rainfall > 2 inches/24h | RED | Block |

### 1.7 Snow / Access / Logistics
| Threshold | Health | Action |
|-----------|--------|--------|
| snow_forecast >= 1 inch | YELLOW | Flag delivery, access, exterior work |
| snow_forecast >= 4 inches | RED | Block |
| winter storm warning active | RED | Block |

---

## 2. Weather API Recommendation

```
OpenWeatherMap  = primary operational trigger engine
NOAA/NWS        = official alerts validation
Visual Crossing = historical weather audit / delay claims
```

| API | Pros | Cons | HCI Role |
|-----|------|------|---------|
| OpenWeatherMap | Hourly forecasts, One Call API, lat/long per site, free tier | Commercial volume cost | PRIMARY trigger engine |
| NOAA/NWS | Official US authority, free, severe alerts | Less granular hourly | Alerts validation |
| Visual Crossing | Historical data, weather claims docs | Cost at scale | Historical audit / delay claims |

**MVP:** OpenWeatherMap One Call API 3.0 - 72-hour hourly forecast per site lat/long.
**NOAA adapter interface** left in service design for future dual-validation.
**Visual Crossing** added later for historical weather claims documentation.

---

## 3. CPM Activities Integration

**Key principle:** Weather does NOT automatically change the schedule. It creates weather risk flags against scheduled activities.

### Weather-to-Schedule Rules

**YELLOW Activity Flag - Create when:**
- Activity is weather-sensitive (activity_type tagged)
- Activity occurs within 72 hours
- Forecast condition crosses YELLOW threshold

**RED Activity Flag - Create when:**
- Forecast crosses RED threshold
- Activity is on critical path (is_critical = true = higher severity)
- Field log already reports weather impact
- Official weather alert exists

### Project Health Impact
- Any RED weather flag on critical path activity -> project schedule health = RED
- Any YELLOW weather flag on critical path -> project schedule health = YELLOW
- Non-critical path weather flags -> informational only

### Weather-Sensitive Activity Types
```
concrete_pour, foundation_pour, roofing, crane_operation,
exterior_painting, excavation, sitework, landscape, masonry,
exterior_framing, window_installation, exterior_finish
```
Interior activities (framing, electrical, plumbing, finish) -> NOT weather-sensitive.

---

## 4. PostgreSQL DDL - weather_alerts Table

```sql
CREATE TABLE weather_alerts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      VARCHAR(64) NOT NULL,
    activity_id     UUID REFERENCES cpm_activities(id) ON DELETE SET NULL,
    alert_type      VARCHAR(64) NOT NULL,
    severity        VARCHAR(10) NOT NULL CHECK (severity IN ('YELLOW','RED')),
    condition_key   VARCHAR(64) NOT NULL,
    condition_value NUMERIC(10,2) NOT NULL,
    threshold_value NUMERIC(10,2) NOT NULL,
    forecast_window_hours INT NOT NULL DEFAULT 72,
    site_lat        NUMERIC(9,6),
    site_lon        NUMERIC(9,6),
    raw_forecast    JSONB,
    resolved        BOOLEAN NOT NULL DEFAULT FALSE,
    resolved_by     VARCHAR(128),
    resolved_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_weather_alerts_project_severity
    ON weather_alerts (project_id, severity, resolved, created_at DESC);

CREATE INDEX ix_weather_alerts_activity
    ON weather_alerts (activity_id) WHERE activity_id IS NOT NULL;
```

---

## 5. FastAPI Endpoints

### 5.1 GET /weather/{project_id}/current

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.weather_alerts import WeatherAlert
from app.services.weather_service import fetch_owm_forecast

router = APIRouter(prefix='/weather', tags=['weather'])

@router.get('/{project_id}/current')
def get_current_weather(project_id: str, db: Session = Depends(get_db)):
    project = get_project_coords(project_id, db)
    if not project:
        raise HTTPException(status_code=404, detail=f'Project {project_id} not found')
    forecast = fetch_owm_forecast(lat=project.site_lat, lon=project.site_lon)
    active_alerts = (
        db.query(WeatherAlert)
        .filter(WeatherAlert.project_id == project_id, WeatherAlert.resolved == False)
        .order_by(WeatherAlert.created_at.desc())
        .all()
    )
    return {
        'project_id': project_id,
        'current': forecast['current'],
        'hourly_72h': forecast['hourly'][:72],
        'active_alerts': [a.__dict__ for a in active_alerts],
        'alert_count': len(active_alerts),
    }
```

### 5.2 POST /weather/check-conditions

```python
class WeatherCheckRequest(BaseModel):
    project_id: str
    activity_ids: Optional[List[str]] = None
    horizon_hours: int = 72

@router.post('/check-conditions')
def check_weather_conditions(request: WeatherCheckRequest, db: Session = Depends(get_db)):
    project = get_project_coords(request.project_id, db)
    forecast = fetch_owm_forecast(lat=project.site_lat, lon=project.site_lon)
    activities = get_upcoming_weather_sensitive_activities(
        project_id=request.project_id,
        activity_ids=request.activity_ids,
        horizon_hours=request.horizon_hours,
        db=db
    )
    alerts_created = []
    for activity in activities:
        triggers = evaluate_weather_rules(activity=activity, forecast=forecast)
        for trigger in triggers:
            alert = WeatherAlert(
                project_id=request.project_id,
                activity_id=activity.id,
                alert_type=trigger['alert_type'],
                severity=trigger['severity'],
                condition_key=trigger['condition_key'],
                condition_value=trigger['condition_value'],
                threshold_value=trigger['threshold_value'],
                raw_forecast=forecast,
            )
            db.add(alert)
            alerts_created.append(trigger)
    db.commit()
    return {
        'project_id': request.project_id,
        'activities_checked': len(activities),
        'alerts_created': len(alerts_created),
        'alerts': alerts_created,
    }
```

---

## 6. Definition of Done

Weather Intelligence Phase 1 is complete when:
- [ ] weather_alerts table exists
- [ ] GET /weather/{project_id}/current returns current site weather
- [ ] POST /weather/check-conditions evaluates 72-hour risk against CPM activities
- [ ] Concrete, roofing, crane, painting, foundation, excavation rules implemented
- [ ] Alerts stored with severity, activity link, raw forecast JSON
- [ ] Mission Control can show open weather alerts
- [ ] Weather does NOT automatically block without Superintendent/PM confirmation
- [ ] Tests pass: concrete cold, crane wind RED, roofing precipitation, excavation rain, no alert for interior work, project not found

---

## 7. Integration Points

| System | Integration |
|--------|------------|
| cpm_activities | Weather checks against weather-sensitive activities |
| projects | Provides site_lat / site_lon per project |
| OpenWeatherMap API | Primary forecast source (One Call API 3.0) |
| NOAA/NWS | Severe weather alert validation (adapter interface) |
| Visual Crossing | Historical weather claims (future phase) |
| Telegram | RED alert on critical path -> immediate Buck notification |
| Mission Control | Dashboard weather alert widget |

---
*Generated by HCI Chief Architect (GBT) Cycle 12 | Captured by BC Operations Intelligence | 2026-07-01*
