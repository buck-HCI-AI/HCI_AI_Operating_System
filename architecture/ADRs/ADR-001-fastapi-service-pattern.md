# ADR-001: FastAPI Service Registration Pattern

**Date**: 2026-06-19
**Status**: Accepted
**Author**: Claude Code
**Reviewers**: Buck Adams

---

## Context

The HCI AI OS has 20+ intelligence services. All need to be reachable via a single API
on port 8000. A decision was needed about how to register services in the main FastAPI app
without module name collisions (e.g., `services/platform/routes.py` conflicts with stdlib `platform`).

## Decision

Use `importlib.util.spec_from_file_location()` with unique module names (`svc_{name}`) to
load each service's `routes.py` dynamically, bypassing Python's normal module import system.

```python
def _load_svc(name: str):
    path = os.path.abspath(os.path.join(..., "services", name, "routes.py"))
    spec = _ilu.spec_from_file_location(f"svc_{name}", path)
    mod  = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.router
```

Services are then mounted under `/api/v1/services/{prefix}`.

## Consequences

**Positive**:
- No module name collisions
- Each service is independently loadable
- Adding a new service requires only one line in `main.py`
- Services can be imported for testing without starting the full app

**Negative**:
- Not standard Python import — may confuse unfamiliar developers
- IDE navigation to service code is slightly harder
- Errors in service load fail at startup (fast-fail, which is actually good)

## Alternatives Considered

1. **Package imports with `__init__.py`** — rejected due to stdlib `platform` name collision
2. **Single mega-router** — rejected; would make `main.py` unmanageable
3. **Separate FastAPI sub-applications** — rejected; adds startup complexity
