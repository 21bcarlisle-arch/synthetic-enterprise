# Alarm → Response Runbook

TRUST_LEDGER_AND_BILLING_CHECK.md item 3 (P2, 2026-07-13): retrospectives are
backward-looking; this is the forward map from each alarm this project
actually raises to its exact response, owner, escalation path, and the test
that proves the alarm fires at all. One row per alarm — an alarm with no
defined response is decoration, not safety.

First four rows are the four historical doorbell failures this project's own
turn-granting rebuild (background/supervisor.py, 2026-07-09) was built to
never repeat — each already has a dedicated retrospective and a regression
test; this table is the missing forward link from "this fired" to "this is
what happens next."

| # | Alarm (trigger) | Detected by | Response | Owner | Escalation if unanswered | Proof it fires |
|---|---|---|---|---|---|---|
| 1 | Doorbell failure #1: raw send into a busy pane corrupts the turn | `send_keys_when_idle()`'s pre-send `is_session_idle()` check | Send refused; caller logs "not delivered", retries next cycle with a fresh draw | supervisor.py (automatic, no human step) | None needed — refusal IS the fix; if refusals persist >1h, folds into row 6 (STUCK escalation) | `tests/background/test_tmux_relay.py`'s busy-pane-refusal tests |
| 2 | Doorbell failure #2: urgent from_rich message queued but never woken | `background/agenda.py`'s urgent-item detection + staging-watcher's own from_rich scan | Immediate NTFY wake, gated by `_check_staging_age()` (>2h unactioned) | staging-watcher / session-watchdog | `_check_staging_age()` surfaces in the routine health_check.py report if still unactioned | `tests/background/test_health_check.py`'s staging-age tests |
| 3 | Doorbell failure #3 (strike 3): autoloop racing staging-watcher's own wake, double-delivery | `background/tmux_relay.py`'s `relay_lock()` — a single cross-daemon mutex every wake-sender acquires | Second sender blocks on the lock rather than interleaving a second send | tmux_relay.py (automatic) | None needed — mutual exclusion structurally prevents the race, not a retry | `tests/background/test_tmux_relay.py`'s concurrent-lock tests |
| 4 | Doorbell failure #4: 34 "delivered (confirmed)" turns over 5.5h, zero real work | `_check_stuck_escalation()` — wall-clock, disk-persisted (`STUCK_STATE_FILE`), keyed on a narrow work-state fingerprint | One NTFY after `STUCK_THRESHOLD_SECONDS` (1h) of the identical unchanged fingerprint, `escalated` flag prevents repeat spam | supervisor.py (automatic detection) + director (reads the NTFY, decides real-blocker vs needs-investigation) | If the director doesn't respond and the SAME fingerprint persists, no further alarm fires today (a real gap — see "Known gap" below) | `tests/background/test_supervisor.py`'s `TestFailureMode4DeliveredButNoProgress` |
| 5 | Doorbell failure #5: busy-regex false positive, session misread as busy indefinitely | `pane_in_copy_mode()` / `ensure_live_tail()` clearing frozen scrollback before the idle check | Pane cleared, idle check re-run same cycle | supervisor.py / session-watchdog (automatic) | None needed — self-correcting within one cycle | `docs/retrospectives/2026-07-09-doorbell-failure-5-busy-regex.md`'s own regression coverage |
| 6 | Anti-livelock: same atom re-drawn N=2+ times with zero state change (2026-07-13, ANTI_LIVELOCK_AND_WIDTH.md) | `_record_atom_draw_and_check_stall()` — per-atom fingerprint tracker (`ATOM_STALL_STATE_FILE`) | Atom soft-deprioritised (`stalled: true` surfaced on the generated site map); draw prefers a different candidate | supervisor.py (automatic) | If EVERY candidate is stalled (no real alternative), falls back silently to re-offering one — folds into row 4's own 1h STUCK alarm as the real backstop | `tests/background/test_supervisor.py::test_maturity_map_draw_concurrent_exclude_stalled_prefers_other_candidate` |
| 7 | Map genuinely exhausted: no BUILD candidate, no idle/DISCOVER-FRAME candidate, no PRIORITIES.md backlog item | `check_map_exhausted_escalation()` (`MAP_EXHAUSTED_STATE_FILE`) | NTFY on the transition into exhaustion (not every idle cycle — R5, never repeat an unchanged status) | supervisor.py (automatic) + director (author new atoms / re-rank) | Idle-turn counter (`_record_idle_turn()`) keeps a running all-time total, visible in the routine log even with no new NTFY | `tests/background/test_supervisor.py::TestMapExhaustedEscalation` |
| 8 | Daemon missing after a session/host restart (2026-07-13, director live in-console: "verify the full daemon set and alarm if any are missing") | `background/health_check.py::run_health_check()` against `EXPECTED_PANES`, now also called automatically by `session_watchdog.py::restart_claude()` immediately post-restart | NTFY naming exactly which daemon(s) are down, needs_input=True | session-watchdog (automatic trigger) + director (restart or investigate) | Routine `health_check.py --quiet` (already wired into `background/start_worker.sh`) re-flags on its own next run if unresolved | `tests/background/test_session_watchdog.py::test_verify_daemon_set_after_restart_ntfys_on_missing_daemon` |
| 9 | Usage-limit / rate-cap hit mid-autonomous-run | `usage_limit_detected()` (pane-text regex, best-effort) | Auto-wait + downtime-task queueing (`handle_usage_limit()`), no confirmation gate, falls back to the confirmation-gated restart path if the limit outlives `USAGE_LIMIT_MAX_WAIT_SECONDS` | session-watchdog (automatic) | Falls back to `handle_session_ended()`'s own NTFY-gated restart flow | `tests/background/test_session_watchdog.py`'s usage-limit tests |
| 10 | Sanity-daemon population/domain-sense implausibility (e.g. C6 SME-as-Household VAT class) | `background/sanity_daemon.py` + `company/compliance/population_sanity.py`/`domain_invariants.py` | Logged to `docs/observability/sanity_adjudication_ledger.json`, adjudicated real/false-positive on next review pass; real findings become R10 class-level fixes, never instance patches | sanity-daemon (automatic detection) + agent (adjudication + fix) | Unadjudicated findings accumulate visibly in the ledger — no silent drop | `tests/background/test_sanity_daemon.py` (existing) |

## Known gap (honest, not silently closed)

Row 4's escalation column is genuinely weak: a STUCK NTFY fires once per
distinct fingerprint, `escalated: true` is set, and if the SAME fingerprint
somehow persists for hours after that single alert (the director missed it,
or is asleep), no SECOND alarm fires today. This is a real, deliberate design
choice (R5: never repeat an unchanged status, avoid alert fatigue) but it
means a genuinely stuck, unanswered blocker can go quiet after one NTFY. Not
fixed here — flagged as a real trade-off for a future re-rank, not an
oversight papered over.

## Maintenance

This table is a snapshot, not a living index — the source of truth for what
NTFYs actually fire is each daemon's own code + its `docs/observability/
*-log.md`. Re-verify this table at the next harness-pruning ritual (phase-
close checklist item 6a) alongside the retro check, not on its own separate
cadence — a runbook nobody re-reads decays exactly the way MAKE_IT_STICK
warns against.
