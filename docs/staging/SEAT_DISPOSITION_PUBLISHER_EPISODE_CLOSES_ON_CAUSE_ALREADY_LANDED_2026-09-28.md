# Disposition: `the-fork-closed-and-the-publisher-episode-closes-when-its-cause-does` — premise spent

**Severity:** RECORDED · **Lane:** H_harness

No defect: a re-drawn item whose work had already landed.

Redrawn 2026-09-28. Part two had already landed as `c0f71f95b` (on origin/main) and `84944706c` (banner renders `held`):

- The episode closes on the first routed cycle where its cause is re-asked of origin/main and no longer holds (`episode_closed_by.rule = cause_cleared`).
- A weekly-window hold reads as held, with its next window.
- `tests/background/test_a_publish_episode_reads_held_refused_or_recovered.py` drives held / refused / recovered and asserts each is reachable. Two mutations were shown red in `c0f71f95b`. Re-run at draw time: 2 passed.

Live DONE check on the shared tree, `docs/observability/.publish_gate_state.json`:
- `episode_closed_by = {rule: cause_cleared, reason: "`behind_origin` no longer holds: re-asked of origin/main, HEAD is 0 behind and 0 ahead", wedge_since: 1790517440}` — the 2026-09-27 ~14:00Z episode, closed by the new rule and not by an ordinary publish.
- `episode_failures = 0`, `wedge_since = null`; shared HEAD is level with origin/main.

The duplicate "live claim" was this same id. The item is released and credited to `c0f71f95b`; nothing was rebuilt.

**Second redraw, same day.** The live state was unchanged: `episode_closed_by.rule = cause_cleared`, `episode_failures = 0`, `wedge_since = null`, and the control still passes (2 passed). The first disposition only ran `--release`, and the continuation stayed offerable. `--premise-spent` refused: the ledger already credits a landing, and a delivered item outranks premise-spent. This time `--release` retired the continuation ("will not be offered again"), and `seat_work_in_hand.release` cleared the second store. Nothing was rebuilt.
