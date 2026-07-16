#!/bin/bash
# Runs the CA (Chief Architect) Assistants API orchestrator one cycle at a time.
# Invoked periodically by launchd (com.hci.gbt-orchestrator, every 10 min).
cd "$(dirname "$0")" || exit 1
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 orchestrator.py
