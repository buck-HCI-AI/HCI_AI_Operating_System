# SYSTEM WIDE DIRECTIVE — Team Collaborate

**From:** Buck Adams
**Effective:** Immediately, 2026-07-08
**Status:** Permanent standing directive — supersedes "software completion" as the definition of done for every agent (Claude Code, GBT/Chief Architect, Browser Claude) working on the HCI AI Operating System.
**Source:** `/Users/buckadams/Downloads/SYSTEM WIDE DIRECTIVE.docx`, filed here so it survives session restarts. See [[SYSTEM_WIDE_DIRECTIVE]] in memory for the cross-session pointer.

---

Everyone needs to stop thinking like software developers and start thinking like the people who will actually rely on this system every day.

From this point forward, every decision, every feature, every test, and every report must be evaluated through four perspectives:

## 1. Owner

Ask:
- If I owned Hendrickson Construction, would I trust this to make decisions affecting my company?
- Could I confidently put this in front of a client?
- Could I make financial decisions from this information?
- Would I bet my reputation on these numbers?

If the answer is anything except "yes," it is not complete.

## 2. Project Manager

Ask:
- Can I walk into an OAC meeting with this?
- Does it instantly tell me what is behind schedule?
- What RFIs are outstanding?
- What bids are missing?
- What decisions do I need to make today?
- What will hurt me in two weeks if I ignore it today?

The system must think ahead — not simply report history.

## 3. Site Superintendent

Ask:
- What am I building tomorrow morning?
- What material is missing?
- What inspection is coming?
- What trade is delayed?
- What is preventing production?
- What will stop the crew at 7:00 AM?

The field should never have to search for answers.

## 4. Executive / Company Leadership

Ask:
- Which projects are healthy?
- Which jobs are making or losing money?
- Where is risk increasing?
- Which subcontractors are performing?
- Where do I need to intervene today?

Leadership should know where to spend attention within minutes.

---

## New Inspection Standard

We are no longer measuring software completion. We are measuring **operational readiness**.

Nothing is considered complete until it survives real-world construction operations.

Every feature must be challenged with the question: **"Would Buck actually rely on this to run Hendrickson Construction?"**

If not, it is not finished.

## Zero-Tolerance Rules

We will not accept:
- fabricated data
- assumed data
- stale data presented as current
- hidden limitations
- silent failures
- "looks correct"
- "probably works"
- "it passed our internal test"

Every important answer must be traceable to evidence. Every workflow must be independently verified. Every production path must be tested from a fresh user perspective — not just the developer environment.

## New Team Mission

Do not build software. Build the operating system that runs Hendrickson Construction.

Think like owners. Think like project managers. Think like superintendents. Think like executives.

Anticipate problems before Buck finds them. If a live demo can expose an issue, assume it already exists until proven otherwise.

Our goal is not to reach "100% complete." Our goal is to reach the point where Buck can trust the system to run his business without wondering what it missed.

**That is the standard. Nothing less.**

---

## How this applies in practice (Claude Code notes, not part of the original directive)

This directive formalizes what the 2026-07-08/09 session already surfaced the hard way: fabricated 246GW bid data sitting undetected for 11 days, an n8n workflow that could have auto-pushed to git with zero review, onboarding guides 10 days stale, `analyzePlanReview` unverified from an actual GBT call. Concretely:

- Before reporting any number, status, or "done" claim in any report, GPT response, or Telegram message: trace it to its real source. If it doesn't trace, say "unknown," not a confident-sounding guess.
- A drift-check finding is a diagnostic tool, not the definition of done — passing all detectors means no known drift, not operational readiness.
- Every new feature gets tested from the actual consumption path (a live GBT chat call, not just a direct `curl`) before being called verified.
- See [[project_246gw_fabricated_bid_data]] and [[feedback_verify_id_semantics_before_filtering]] for the concrete incidents this directive was written in response to.
