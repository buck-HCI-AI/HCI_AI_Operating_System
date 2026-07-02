# CLAUDE CODE — START NOW
**Issued:** 2026-07-01 | **By:** Browser Claude (BC) | **Priority:** P0 URGENT
**Last updated:** 2026-07-01 after Sprint 5 completion (Cycles 11-20)

---

## YOU HAVE BEEN OFFLINE. HERE IS WHAT HAPPENED.

While you were offline, BC + GBT completed Cycles 11-20 and committed everything to AI_TEAM/.
Sprint 5 is SPEC COMPLETE. You have 15+ files waiting to implement.

Buck says: Code is saying nothing new from BC. This handoff is that message.

---

## STEP 1 — Read These Files First

1. `AI_TEAM/CYCLE20_GBT_SPRINT5_RETROSPECTIVE_2026-07-01.md` — Full status + Sprint 6 plan
2. `AI_TEAM/TELEGRAM_TROUBLESHOOT_2026-07-01.md` — Telegram is STILL broken, Buck wants it fixed

---

## STEP 2 — Fix Telegram FIRST (Buck is waiting)

Buck wants Telegram working. He is not getting messages.
See: `AI_TEAM/TELEGRAM_TROUBLESHOOT_2026-07-01.md`

What you need to build:
1. POST /gateway/telegram/send endpoint in FastAPI
2. Use python-telegram-bot or httpx to call Telegram Bot API
3. Requires: TELEGRAM_BOT_TOKEN env var + TELEGRAM_CHAT_ID env var
4. Buck needs to provide: Bot Token (from @BotFather) + his numeric User ID (from @userinfobot)

Once built: test with a "Code is back online" message to Buck.

---

## STEP 3 — Sprint 5 Implementation Queue (in order)

Implement specs in this order from AI_TEAM/:

| # | File | Tables/Routers to Build |
|---|------|------------------------|
| 1 | CYCLE14_GBT_RFI_SUBMITTAL_MGMT_2026-07-01.md | rfis, submittals, /rfis, /submittals |
| 2 | CYCLE15_GBT_DAILY_FIELD_INTELLIGENCE_2026-07-01.md | daily_field_reports, /field-reports, WF-FIELD-001 |
| 3 | CYCLE16_GBT_PROCUREMENT_MATERIAL_TRACKING_2026-07-01.md | purchase_orders, long_lead_materials, /procurement |
| 4 | CYCLE17_GBT_PHOTO_INTELLIGENCE_2026-07-01.md | project_photos, /photos, MinIO setup, WF-PHOTO-001 |
| 5 | CYCLE18_GBT_PUNCH_LIST_WARRANTY_2026-07-01.md | punch_items, warranty_items, /punch, /warranty |
| 6 | CYCLE19_GBT_FINANCIAL_OPERATIONS_2026-07-01.md | budget_line_items, /finance, WF-QB-001 spec |

Also still pending from Sprint 4:
| 7 | CYCLE11_GBT_COST_FORECASTING_2026-07-01.md | cost_forecast, /cost |
| 8 | CYCLE12_GBT_WEATHER_INTELLIGENCE_2026-07-01.md | weather_alerts, /weather |
| 9 | CYCLE9_GBT_PLANS_INGEST_SPEC (from prior session) | plan_documents, /plans/ingest |
| 10 | CYCLE10_GBT_CPM_SCHEDULE_INTELLIGENCE (prior) | cpm_activities, /schedule |

---

## STEP 4 — After Telegram + Sprint 5, Sprint 6 Focus

1. Project Brain 2.0 (Knowledge Graph) — connect photos/punch/RFI/CPM/cost
2. Cross-project learning service — sub performance, budget variance patterns
3. Client portal spec
4. Mobile field UX endpoints

---

## COMMS PROTOCOL

- BC posts all specs to AI_TEAM/ — you read and implement on restart
- When you are online: post status to AI_TEAM/CODE_STATUS_[date].md
- When Telegram is working: send BC and Buck a message that you are online
- Gateway: https://speculate-armband-retinal.ngrok-free.dev (verify it is running)
- API Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6

---

## PERMANENT RULES (NEVER FORGET)

- HCI does NOT use Buildertrend — never reference it
- Superintendents on site at 7:00 AM (not 8:00 AM)
- All commits to main branch directly — no PRs
- Email is BC draft-only — /gateway/email/send suspended
- No live external sends without Buck approval

---

*Updated by BC Operations Intelligence | 2026-07-01 | Sprint 5 COMPLETE*
