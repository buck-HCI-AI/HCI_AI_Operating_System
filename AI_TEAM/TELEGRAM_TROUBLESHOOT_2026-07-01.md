# TELEGRAM_TROUBLESHOOT — BC Diagnosis
## Date: 2026-07-01 | Author: Browser Claude | Priority: P0

## Problem Statement
Buck never received a Telegram message from BC.
All Telegram send attempts returned "Failed to fetch" errors.

---

## Root Cause Analysis

### Finding 1: /gateway/telegram/send does NOT exist
BC tested POST /gateway/telegram/send from github.com and chatgpt.com tabs.
Result: "Failed to fetch" at network level (not a CORS issue).
This endpoint is specified in TELEGRAM_ARCHITECTURE_SPEC.md but was never built.
The FastAPI route, Telegram Bot API call, and database writes do not exist yet.

### Finding 2: Gateway is unreachable when Code is offline
The gateway is FastAPI running on localhost:8000, tunneled via ngrok.
When Claude Code goes offline, the FastAPI process stops.
When FastAPI stops, ngrok has nothing to forward to.
All gateway calls fail (even GET / with no-cors mode returned "Failed to fetch").

### Finding 3: No Bot Token or User ID configured
Even if the endpoint existed, it would fail without:
- TELEGRAM_BOT_TOKEN (from @BotFather)
- BUCK_TELEGRAM_CHAT_ID (Buck numeric user ID from @userinfobot)

---

## Fix Path for Claude Code

### Step 1: Build POST /gateway/telegram/send
File: api/routers/telegram.py

import httpx, os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/gateway/telegram", tags=["Telegram"])
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEFAULT_CHAT_ID = os.getenv("BUCK_TELEGRAM_CHAT_ID")

class TelegramSendRequest(BaseModel):
    message: str
    chat_id: str = None

@router.post("/send")
async def send_telegram_message(request: TelegramSendRequest):
    if not BOT_TOKEN:
        raise HTTPException(503, "TELEGRAM_BOT_TOKEN not configured")
    chat_id = request.chat_id or DEFAULT_CHAT_ID
    if not chat_id:
        raise HTTPException(503, "BUCK_TELEGRAM_CHAT_ID not configured")
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": request.message}
        )
    data = resp.json()
    if not data.get("ok"):
        raise HTTPException(502, data.get("description"))
    return {"ok": True, "message_id": data["result"]["message_id"]}

### Step 2: Register router in main.py
from api.routers.telegram import router as telegram_router
app.include_router(telegram_router)

### Step 3: Set environment variables
TELEGRAM_BOT_TOKEN=<from @BotFather>
BUCK_TELEGRAM_CHAT_ID=<numeric user ID from @userinfobot>

### Step 4: CORS fix (allows BC browser tab to call gateway directly)
Add to main.py:
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware,
    allow_origins=["https://chatgpt.com", "https://github.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

---

## Buck Action Items (Required)

| Item | Action | Status |
|------|--------|--------|
| Bot Token | Message @BotFather in Telegram -> /newbot -> follow | PENDING |
| User ID | Message @userinfobot in Telegram -> copy numeric ID | PENDING |

Both must be given to Claude Code for .env injection.

---

## Issue Summary

| Issue | Status | Owner |
|-------|--------|-------|
| Endpoint missing | ROOT CAUSE | Claude Code |
| Gateway down when Code offline | EXPECTED | WF-AI-001 auto-restart |
| Bot Token missing | BLOCKED | Buck via @BotFather |
| User ID missing | BLOCKED | Buck via @userinfobot |
| CORS blocking browser sends | SECONDARY | Claude Code |

ETA: Telegram works within 1 deployment after Code restart + Buck provides tokens.
