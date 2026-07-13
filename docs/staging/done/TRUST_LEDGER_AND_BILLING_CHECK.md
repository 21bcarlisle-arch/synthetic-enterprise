# TRUST LEDGER (+ two elevations) and a BILLING/MODEL SAFETY CHECK (P1 / P0-tiny)

**Staged:** 2026-07-13 by advisor; director-raised from a published nine-layer
harness article. Advisor assessment: most layers Poesys already has in stronger
form (constitution -> CLAUDE.md R-rules; separation of powers -> fresh-context
evaluators + lane-wall hooks + epistemic verifier; frontier-decides/cheap-
executes -> the model routing already in CLAUDE.md line 14; injection defence ->
HMAC relay + a staging watcher that never executes content). Three genuine gaps
follow. Fold the recurring re-check into HARNESS_BEST_PRACTICE_ADOPTION rather
than opening a new stream.

## 1. TRUST LEDGER — earned autonomy per task-class (the real gap, P1)
Today autonomy is BINARY and STATIC: proceed unless a one-way door
(PROCEED_BY_DEFAULT). The maturity map grades the PRODUCT (atoms); nothing
grades the PROCESS (which classes of work the builder has statistically earned
the right to do unattended). Expert-Hour and evaluator pass/fail data already
exists and currently has NO autonomy consequence.

**Requirement:** a trust ledger keyed by TASK CLASS (e.g. billing changes,
pricing logic, harness/supervisor edits, site/presentation, docs/discovery).
Per class: N completed, evaluator pass rate, defects found post-close, rework
rate. Autonomy level per class derives from that record — earned upward after N
verified runs above threshold, and **automatically REVOKED when quality slips**
(a class that starts failing goes back under review without anyone deciding).

**Coherence:** this is the SAME mechanism as (a) the company's scrutiny dial
(rises on incidents, falls on calm) and (b) the DIRECTOR_TWIN's fidelity metric
(overturn rate). Build ONE ledger with three subjects, not three ledgers.

**GOODHART SAFEGUARDS — non-negotiable, the article omits these:**
- The grader must be fresh-context and independent. **The builder may NEVER
  modify, tune, or select its own evaluator** — that path is closed at the tool/
  hook level, not by policy.
- Pass rates are measured by the grader, never self-reported.
- The trust score is a DIAGNOSTIC. The director may override any level at any
  time. It is never a target (Law A) — if it becomes something to optimise, it
  is worthless.
- Watch for the tell: rising pass rates with falling defect-discovery is
  evidence of grader capture, not quality. Alarm on it.

## 2. DONE-IS-MONITORED — elevate the daily walk (P2, registered-not-built)
Every CLOSED atom re-verified on a cadence, not trusted forever. The daily
Expert-Hour walk is already registered and unbuilt; it is now CHEAP — cold-eyes
personas exist and the multi-atom draw can run them wide, in parallel, at
zero collision risk. Build it: a closed atom that silently regresses is the most
expensive defect class we have (four stale-surface incidents prove it).

## 3. ALARM -> RESPONSE RUNBOOK (P2)
We have retrospectives (backward-looking) but no FORWARD map from each alarm to
its exact response and owner. The [ACTION NEEDED] rule failing four times is
precisely the symptom this layer prevents: an alarm with no defined response is
decoration. One row per alarm: trigger, who/what responds, the response, the
escalation if unanswered, and the test that proves it fires.

## 4. BILLING / MODEL SAFETY CHECK (P0 but tiny — do today)
Reported: included Fable-5 access on paid plans runs to ~2026-07-19, after which
Fable-class usage moves to prepaid credits, with **access stopping with no grace
period** if credits are not enabled.
**Advisor's read: probably not our exposure** — the main session reported
Sonnet 5 last night, and CLAUDE.md's model policy pins judgment agents to Opus.
But the downside (a hard stop mid-autonomous-run, which the watchdog cannot
recover from) is severe and the check is minutes. Therefore:
- Confirm and REPORT the exact model each lane actually runs (main session,
  subagents, supervisor micro-turns, twin) — the director cannot see this.
- Confirm whether ANY lane is on a Fable/Mythos-class model. If so, flag
  immediately as a director decision (billing = director-reserved).
- Establish whether a hard spend/credit stop can occur mid-session, and if so
  ensure the watchdog treats it as a distinct failure mode with a director NTFY
  — not a silent death.
- Note for the fan-out work: with N concurrent forks re-reading shared context,
  PROMPT CACHING becomes a real cost lever. Confirm caching is actually being
  exercised across the fan-out; if not, that is free money on the table.

## DoD
Trust ledger designed and thin-started (one task class, real data, safeguards
enforced at tool level); daily-walk elevated in PRIORITIES; alarm->response
runbook drafted with the four historical alarm failures as its first rows;
billing/model check answered in the next digest with the exact model per lane.
Recurring harness re-check absorbs this at future boundaries.
