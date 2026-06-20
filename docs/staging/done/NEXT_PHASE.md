# Proposed Next Phase: 6b — Event-Driven Customer Lifecycle (MVP)

## Context

Phase 6a (HH smart meter customers, C7-C9) is complete and committed
(`b6a6508`). Per CLAUDE.md's 14 June 2026 decisions: "I&C deferred until HH
and event-driven customer lifecycle are in place" — HH is now done. This
proposal targets gap #1 of the "five hollow gaps": *"No customer events
actually firing... The customer roster has been static since 2016."*

The full lifecycle (acquisition, renewal, home move, complaint, debt,
disconnection — all "as actual events with timestamps and consequences") is
too large for one phase. This proposal scopes an **MVP**: renewal-time churn
events that actually remove an account from the portfolio, using data/models
that already exist (`saas/churn_model.py`, `saas/home_move_win_rate.py`).
Complaint/debt/disconnection events and replacement-customer onboarding are
explicitly deferred (see "Out of scope").

## Proposed scope

1. **Event roll at each renewal point.** `simulation/run_phase2b.py` already
   computes renewal schedules per customer (`simulation/renewals.py`). At
   each renewal date, compute `effective_retention_probability` (via
   `build_churn_risk()` + `build_home_move_win_rate()`, fed the settlement
   records accumulated so far — Point-in-Time safe, since both only use
   history up to that date) and roll a seeded random draw against it.

2. **Deterministic seeding.** A single seed (e.g. derived from
   `customer_id` + renewal date string, via `random.Random(seed)`) so the
   same run produces the same event sequence — required for reproducible
   tests and reports.

3. **Two outcomes:**
   - **Retained** (probability = `effective_retention_probability`):
     contract continues exactly as today — no behaviour change.
   - **Lost**: the account stops generating settlement records from that
     date forward. The portfolio genuinely shrinks. No replacement customer
     is onboarded in this MVP (see "Out of scope" — this makes the MVP a
     *decommissioning* mechanic, the simplest real consequence to implement
     and verify).

4. **Event log.** New `simulation/customer_events.py` (or extend
   `run_phase2b`'s output dict) — a chronological list of
   `{customer_id, event_date, event_type: "renewed"|"churned", churn_probability,
   win_probability, effective_retention_probability}`. Exposed in
   `run_output_latest.json` for the annual report.

5. **Report section.** New "Customer Lifecycle Events" section in
   `ANNUAL_REPORT.md` — replaces the existing "Losses (churn / home move)
   during year: Not available" placeholder (REPORTING_BACKLOG item 7's
   churn-threshold question becomes partially moot — an account either
   churned or didn't, no threshold needed for *this* metric).

6. **Tests.** Determinism (same seed -> same events), a "lost" event
   actually stops settlement for that customer (portfolio totals reflect
   fewer periods), a "retained" outcome is byte-for-byte identical to current
   behaviour. Existing 283 tests must still pass — need to verify none of
   them assert exact whole-run figures that this would perturb (a quick
   `grep` of `tests/` for hardcoded net-margin/treasury figures from a full
   `run_phase2b` run suggests none do — fixtures are hand-built — but this
   needs confirming before merging).

## Out of scope (deferred to later phases)

- **Replacement-customer onboarding** when an account churns (a new occupant
  moving into the vacated property, possibly winning back the contract per
  `home_move_win_rate`'s "win" case). This MVP only implements the "loss"
  side — accounts can shrink but the portfolio doesn't grow new ones yet.
  Needed for a full lifecycle but adds substantial complexity (new
  `customer_id` allocation, property/asset record reuse, HH vs profile-class
  assignment for the new occupant).
- **Acquisition events** for genuinely new (not replacement) customers.
- **Complaint, debt, and disconnection** as roster-affecting events — these
  affect an account's *treatment* (credit risk, contact frequency) more than
  its existence, and `saas/payment_behaviour.py` / `saas/contact_model.py`
  already model the risk scores; turning them into discrete timestamped
  events with consequences is a separate design question.
- **ToU tariffs** (listed after event-driven lifecycle in CLAUDE.md's
  roadmap) — HH data from Phase 6a makes this buildable next, but per the 14
  June decisions it comes after this phase.

## Open questions for Rich

- Is a portfolio that can only *shrink* (no replacement onboarding) a
  meaningful enough step, or should 6b be rescoped to wait for replacement
  onboarding to land in the same phase (larger, but a more complete
  "lifecycle" story)?
- `effective_retention_probability` for the current portfolio's profile
  (mostly low bill-shock counts) likely keeps churn probability close to the
  5% baseline — over 2016-2025 with ~9-13 annual renewal points per account
  across ~10 years, expect roughly 0-2 churn events total across the whole
  run at that rate. Is that a strong enough "fidelity delta" for the token
  cost, or should the MVP also include a stress-test mode (e.g. force a
  churn in a crisis year) to prove the mechanic works end-to-end?

## Gate

Per CLAUDE.md's opt-out REVIEW_GATE pattern: proceeding with this scope in 4
hours unless Rich redirects via staging or NTFY.
