# Retro — tmux-injection THIRD strike + the fail-silent dead-man's switch (6h blackout)

**Date:** 2026-07-14 · **Class:** director-flagged P0 (blackout 22:12–04:00, found at 05:00 by a
corrupted input box) · **Prior strikes:** `2026-07-08-test-suite-tmux-leak.md`,
`2026-07-13-tmux-injection-two-strikes.md` (closed 23:05, commit `e7969cd29`) → **reopened <6h later**.

## What happened (observed-with-evidence, R9)
- `supervisor-log`: "Turn grant not delivered (busy/unconfirmed) -- retrying next cycle" repeated for
  hours. `injection-log.jsonl`: last real entry 22:13; nothing after. `deadmans-switch-log`: "activity
  recent (0min ago) -- not blocked" every 15-min cycle while staged files climbed **31 → 59**.
  Director saw the `claude` input box holding a doorbell + "/usage" repeated dozens of times.
- **Root cause A (the jam):** `session_watchdog.check_session_usage()` fired `/usage` + Enter via a
  RAW `subprocess.run(["tmux","send-keys",...])` — never routed through the gated relay, invisible to
  the injection-log. On a busy pane a slash command isn't recognised (only recognised as the *entire*
  input on an idle prompt), so the keystrokes accumulated UNSUBMITTED. The gate's own accumulation
  guard (`_pane_has_pending_input`) then *correctly* refused every legitimate turn grant while junk
  sat in the box → deadlock: raw `/usage` keeps the box dirty → every gated grant refuses → no turn
  clears the box → repeat. ~6h, zero commits.
- **Root cause B (the silence):** `deadmans_switch` used `max(last_commit, max mtime over
  docs/observability/)` as its "alive" signal. Every daemon — **including the switch's own 15-min log
  write** — refreshes that directory, so the staleness clock never advanced past ~0. A watchdog that
  refreshes its own liveness signal is structurally incapable of firing. Fail-silent (R15).

## Why the two-strike fix didn't hold (the real lesson)
The 23:05 fix hardened `_safe_to_inject` (byte-stability, accumulation guard) — i.e. it fixed the
**gated path**. It never asked *"is every pane writer actually on this path?"* One wasn't:
`check_session_usage` had been a raw writer since long before, on the false comfort that a `/usage`
read is harmless. Fixing a shared primitive proves nothing about callers that bypass it. **R3's
"redesign, don't patch" means making the bypass structurally impossible, not hardening the gate a
third time.**

## The mechanisms shipped (MAKE_IT_STICK — code, not prose)
1. **`test_no_raw_tmux_send_keys_outside_relay_module`** greps the whole `background/` tree and FAILS
   on any raw `tmux send-keys` outside `tmux_relay.py`. Was RED on 3 sites before the fix. This is the
   permanent audit the two-strike retro should have produced — no new bypass can be added silently.
2. **`read_slash_dialog_when_idle`** — the gated `/usage` path (idle+empty+byte-stable, read-back
   verify the dialog rendered = "submit landed", Ctrl-U rollback if not), under the shared relay lock.
3. **Deadman keys on the git COMMIT clock ALONE** — the observability-mtime term is deleted, not
   narrowed. `test_daemon_log_writes_do_not_mask_a_stale_commit` replays the exact outage (stale
   commit + fresh daemon logs) and asserts the alarm fires. Two tiers: [BLOCKED] (queued + no commit
   ≥45m), [STALL] (no commit ≥90m, backstop), both suppressed only in a declared usage pause.

## Rule candidates
- **R-candidate (bypass audit):** when closing any defect on a shared safety primitive, the closure is
  incomplete until a mechanism proves *every* caller is on the primitive. Hardening the primitive
  while a bypass exists is a two-strike-in-waiting. (Generalises R3.)
- **R-candidate (self-referential liveness):** a watchdog's liveness signal must be something the
  watchdog and its sibling daemons CANNOT themselves move. If the monitor's own activity can reset the
  staleness clock, the control is fail-silent by construction (R15). Prefer an external, work-only
  signal (git commits) over "is any process breathing."

## Loose ends
- Chronic (pre-blackout) residual: ~61 `run_complete_*.md` queued (oldest 07:28 the prior day); the
  auto-processor is draining newest-first but is chronically behind — registered as an atom, not
  conflated with this acute incident.
