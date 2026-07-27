<!-- SUPERVISOR_DRAW: self-drawable -->
# [PLANNER-MINTED / PROPOSE-THEN-PROCEED] — LAW C: watchdog + daily note verify from PRIMARY state, not the tick's enumeration (2026-07-27)

**Provenance:** RUNG-7 planner refill (director ruling `WORK_IS_THE_DEFAULT_2026-07-23`). Minted from `docs/staging/in_progress/DIRECTOR_RULING_FAILURE_BIAS_LAWS_2026-07-27.md`, which names LAW C but leaves it un-drawn.

**Serves:**
- **DIRECTOR_RULING_FAILURE_BIAS_LAWS LAW C** — "The watchdog and the daily note derive their verdict from primary state — the actual contents of `in_progress/`, the campaign registers, the defect ledger, the maturity map — never from the tick's published enumeration. Two sources that can disagree, so a false claim in one is visible from the other."
- **R15 (controls must be able to FAIL) — FAIL-SILENT / TAUTOLOGY killers** — the ruling's failures #3 (enumeration published "whole authorized set empty" while open mints existed in `in_progress/`), #4 (STALL page suppressed by the watched component's own rest declaration), #5 (daily note reported the law's *status* not its *effect*). All three are a checker reading the same source it checks. This law severs that independence coupling ([[feedback_fail_silent_control_patterns]]: a watchdog's liveness signal must be one it cannot itself refresh).

**Robustness gained (one sentence):** the STALL watchdog and the morning self-note compute their verdict directly from primary state (`in_progress/` contents, `CAMPAIGN_REGISTER.yaml`, the defect ledger, `maturity_map.yaml`) rather than trusting the tick's own published enumeration, so a false "empty / at rest" claim in the enumeration is contradicted — and paged — by the independent read.

---

## Scope — BUILD (harness lane; director-ruled, drawable now)

1. **Independent watchdog verdict.** The deadman/STALL check must NOT accept the tick's self-declared rest as sufficient. It independently scans primary state for drawable-but-undrawn work (open `in_progress/` mints with `SUPERVISOR_DRAW: self-drawable`, OPEN campaign items, unresolved defect-ledger rows, drawable maturity atoms). If primary state shows drawable work while the tick declares rest → PAGE (un-suppressible, per LAW A's re-arm).
2. **Daily note reports EFFECT not status.** The self-note computes, over its window, the *effect* metric the ruling demands: e.g. "always-drawable lane drew N atoms in the last 24h" / "M dead hours with drawable work present" — never merely "lane WIRED". Derive from run history + primary state, not from the enumeration.
3. **R15 (binding, both ways):** falsify the enumeration in a test — inject a tick that publishes "authorized set empty" while `in_progress/` holds a self-drawable mint — and prove the watchdog STILL pages (independence). Mutation: point the watchdog back at the enumeration and prove the test REDS (false-empty passes silently). Outcome-test the daily note: a note that reports "WIRED" over a window with dead hours is a FAIL.

## Walls untouched (director-reserved)
- One-way doors: none — git-reversible harness change; paging uses `notify()` not `send_ntfy` in new modules ([[project_r17_tick_never_rests]]).
- L3 level moves stay `blocked_on: director_level_up`.

## Window
Director-ruled mechanism; no propose window. Drawable now. This is the independent-counterpart half of the sweep's remediation (LAW C is what the sweep assigns to any suppression that fails toward quiet).

— Planner mint, RUNG-7 refill, 2026-07-27.

---
## DISPOSITION — LANDED (core), 2026-07-27 worker tick
**Item 1 (independent watchdog verdict) + item 2 (daily-note EFFECT cross-check): LANDED and R15-proven both ways.**
- New independent primitive `background/primary_state_scan.py::drawable_undrawn_mints` — reads `in_progress/` directly, imports NOTHING from `supervisor.py` (the LAW-C second source).
- Deadman (`deadmans_switch.py`): `_check_drawable_undrawn_escalation` pages `[ACT]` on a self-drawable mint undrawn >2h **regardless of the tick's enumeration**, and a self-drawable mint now **vetoes** the proven-rest `[STALL]` fold — severing the deadman's trust in `_is_drained_and_gated()`.
- Daily note (`daily_self_note.py::r17_effect_crosscheck`): cross-checks the enumeration STATUS against the independent read; renders 🔴 CONTRADICTION on a false REST-LEGITIMATE.
- Tests: `test_deadmans_switch.py` LAW-C block + `test_daily_self_note.py` LAW-C block (R15 both ways, independence-import asserted).
- Register `authorized_set_enumeration` + `daily_note_r17_status` → `landed_partial`.

**Named LAW-C follow-on (recorded in `suppression_register.json`, NOT re-mint on sight):** independence over the OTHER primary sources (open campaign items, defect-ledger rows, drawable maturity atoms — still read only through the supervisor's drained check) and the full dead-hours-with-work-present time-series metric. Lower value now that the concrete self-drawable-mint blind spot is closed.
