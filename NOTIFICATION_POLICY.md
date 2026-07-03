# Notification Policy Registry
## HCI AI Operating System v2.2

**Authority:** 2nd BTW Directive — Notification Service  
**Owner:** Chris Hendrickson (Hendrickson Construction) | **HCI-AI Owner / PM & SS:** Buck Adams  
**Updated:** 2026-06-27

---

## Provider Stack

| Priority | Provider | Use Case | Status |
|---|---|---|---|
| 1 | ntfy.sh | Primary push (iOS/Android) | READY — configure NTFY_TOPIC |
| 2 | Pushover | Backup push | PENDING — add PUSHOVER_TOKEN |
| 3 | Email (n8n) | Standard delivery | READY — n8n SMTP built-in |
| 4 | SMS (Twilio) | Critical only | PENDING — add TWILIO creds |
| 5 | Slack | Team channel | Future — Sprint 6 |
| 6 | Teams | Enterprise | Future — Sprint 7 |
| 7 | APNs | Native iOS | Future — Sprint 7 |

---

## Policy Engine

```
Event → Severity Classification → Provider Selection → Dispatch
```

| Severity | Providers | Example Events |
|---|---|---|
| CRITICAL | ntfy + Pushover + SMS | Service down, data loss risk, contract deadline <24h |
| HIGH | ntfy + Email | Owner decision pending, mining finds risk, Houzz blocked |
| MEDIUM | Email | New inbox item, mission blocked, routine alert |
| LOW | Weekly digest only | Automation opportunity detected, non-urgent queues |

---

## Event Routing

### From Executive Inbox
| Event | Severity | Trigger |
|---|---|---|
| New OWNER-level item | HIGH | Immediately on creation |
| Item unresolved >24h | HIGH | n8n daily check |
| Item unresolved >72h | CRITICAL | n8n daily check |
| Item deadline <48h | CRITICAL | n8n daily check |

### From Mining Engine
| Event | Severity | Trigger |
|---|---|---|
| Schedule risk detected | HIGH | On mining completion |
| Bid deadline approaching | HIGH | On mining completion |
| New duplicate vendor group found | MEDIUM | Weekly digest |
| Mining run failed | HIGH | On failure |

### From System Health
| Event | Severity | Trigger |
|---|---|---|
| Service down | CRITICAL | Health check every 15min |
| Service degraded >30min | HIGH | Continuous monitor |
| API response time >5s | MEDIUM | Monitor |

### From AI Agents
| Event | Severity | Trigger |
|---|---|---|
| Mission blocked >4h | HIGH | AUTO-PM review |
| Agent idle >2h during hours | MEDIUM | AUTO-PM review |
| Mission completed | LOW | Digest |

---

## ntfy.sh Setup

**Topic:** `hci-executive` (default — set NTFY_TOPIC in .env to customize)

**Buck's phone setup:**
1. Install ntfy app (iOS App Store / Google Play)
2. Subscribe to topic: `hci-executive`
3. Enable notifications

**Self-hosted option:** Set NTFY_URL to internal ntfy server for privacy.

---

## API Endpoint

```
POST /api/v1/services/notifications/send
{
  "title": "string",
  "message": "string",
  "severity": "CRITICAL | HIGH | MEDIUM | LOW",
  "tags": ["string"],
  "action_url": "string (optional)",
  "topic": "string (optional, overrides default)"
}
```

**n8n usage:**
```json
{
  "url": "http://localhost:8000/api/v1/services/notifications/send",
  "method": "POST",
  "headers": {"X-API-Key": "{{ $env.HCI_API_KEY }}"},
  "body": {
    "title": "HCI AI Alert",
    "message": "{{ $node['Previous'].json.message }}",
    "severity": "HIGH"
  }
}
```

---

## .env Variables Required

```bash
# ntfy.sh (primary push)
NTFY_URL=https://ntfy.sh          # or self-hosted URL
NTFY_TOPIC=hci-executive          # subscribe to this on your phone
NTFY_TOKEN=                       # optional, for private topics

# Pushover (backup)
PUSHOVER_TOKEN=                   # app token from pushover.net
PUSHOVER_USER_KEY=                # your user key from pushover.net

# Email (routed via n8n)
N8N_EMAIL_WEBHOOK=                # n8n webhook URL for email dispatch
EXECUTIVE_EMAIL=buck@ahmaspen.com

# SMS / Twilio (critical only)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_FROM=                      # your Twilio number
EXECUTIVE_PHONE=                  # Buck's phone number
```

---

*Notification Policy Registry | HCI AI OS v2.2 | Hendrickson Construction, Inc. | 2026-06-27*
