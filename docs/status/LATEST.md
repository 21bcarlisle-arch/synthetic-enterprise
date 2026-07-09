## THE SUPERVISOR — architecture rebuild (doorbell failure #4, R3)
Last updated: 2026-07-09T05:38:27Z

**Status:** COMPLETE. 16,026 tests pass (full suite minus known-slow simulation integration suites).
Epistemic: PASS.

**Doorbell failure #4 + architecture rebuild:** the relay_lock fix (strike 3, same day) closed
the multi-daemon race, but a fourth failure the same night proved individual-call-site fixes
insufficient. Evidence (docs/retrospectives/2026-07-09-doorbell-failure-4-supervisor.md,
R9-labelled): `agenda.should_nudge()` nudged the open-agenda snapshot exactly once (R5's "never
repeat" misapplied to turn-granting) and never again by design -- work sat undone 5+ hours.
Independently, session_watchdog's autoloop fired "delivered (confirmed)" 34 times over that same
window with zero resulting work. Independently again, staging_watcher.py went silently inert for
5+ hours while still alive, taking every one of its bundled responsibilities down with it.

**Fix: `background/supervisor.py`** -- a single dumb loop, sole turn-granting authority. Every 2
minutes: if idle AND real work exists on disk (open agenda / unprocessed staging / urgent
from_rich / usage-pause just ended), grants one turn via the locked relay, logs the decision every
cycle, no "already done" memory. Beyond the literal spec: tracks a work-state fingerprint across
cycles and escalates via one deduped NTFY if grants keep succeeding with zero progress for ~16
minutes -- the piece that would have caught tonight specifically. Demoted to non-authoritative
fast-path hints: staging_watcher's new-file wake, dispatcher's URGENT relay. Removed outright:
session_watchdog's autoloop send + dead cap machinery, agenda.py's whole nudge-once mechanism
(retirement-guarded by an explicit test). Usage-limit pause/resume now each fire one NTFY
transition. `health_check.py`/`start_worker.sh` updated. 27 new tests including explicit
simulations of all 4 historical failure modes by name. All three affected daemons restarted live,
verified.

**Prior:** Wake-doorbell strike 3 fix + BILL_CORRECTNESS_ADDENDUM Defect 1 CLOSED (2026-07-08/09,
see docs/retrospectives/2026-07-08-wake-doorbell-third-strike.md). Defects 2-4 (bill period/reads/
MPAN, ToU-ready line structure, portal-vs-ledger-vs-sample reconciliation) next; Defect 5 (I&C
billing model) registered to backlog. DOMAIN_SENSE_AND_COMPLIANCE.md queued behind Phase 4.

**Latest simulation results (2016–2025)** — auto-processed (468s / 8 min):
- Net margin: £1,526,516.74 | Gross: £6,447,283.33 | Capital: £51,210
- Treasury: £2,466,636 → £3,903,143 | 38 committee interventions | 1550 bills issued
- Enterprise value: £8,220,970.68 | Net after CTS: £6,414,742
- Retention: 12 offers, 12/12 retained | 6 no-offer churns | 6 total churned accounts
