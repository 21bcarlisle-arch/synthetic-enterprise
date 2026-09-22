**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — wire the live-record readers through the shared-tree resolver)

# The stale live-record room is 53, not 23 — and staleness alone does not decide who gets wired

**2026-09-16, scheduled tick, worker seat.** The survey half of the Lane 0 item, recorded so the
next invocation does not re-derive it. The wiring half landed in the same turn for four readers.

## The premise held

`d895d845e` is an ancestor of `origin/main` and the resolver is there, but it had only **two**
callers (`process_run_complete._read_publish_gate_state`, `seat_executor._shared_tree_log`). The
per-reader wiring was explicitly not claimed by that commit. Not spent; the work was real.

## The room, re-measured on the real tree

The item cited *75 live-state paths, 30 tracked, 23 stale*. Measured today over
`git ls-files docs/observability` with a byte comparison of `HEAD:<path>` against the working copy:

    271 tracked paths under docs/observability/
     53 with HEAD content differing from live

Wider than 23 because the tree moved, and because the item's census counted only the paths the
daemons write, while the room `is_live_record_path` actually derives is every path under the
directory. **Use the derived room, not the daemon list** — that is the whole point of the resolver.

## The finding that mattered: staleness is not the defect

Wiring all 53 would be the instance fix wearing a class fix's clothes. What decides harm is the
DIRECTION of the error, and it is not always the flattering one. Three measured counterexamples,
deliberately NOT wired:

| record | HEAD vs live | direction |
|---|---|---|
| `.last_tested_hash` | 9B vs 9B, differing | a stale hash never equals HEAD → reads as NOT TESTED → alarms MORE |
| `.seat_heartbeat.json` | 939B vs 938B | a stale beat reads as OLDER → the seat looks DEADER |
| `action_needed_register.json` | 19474B vs 19332B | HEAD is LARGER → staleness OVER-reports work owed |

Each of those already fails closed. Redirecting them buys nothing and costs a git subprocess per
read.

## The four wired, each measured

| record | HEAD | live | why the stale read flatters |
|---|---|---|---|
| `.launch_records.json` | 4 records | 12 | `check` exists to CONTRADICT a settled `live` claim; 8 did not exist to be contradicted, and `load`'s bare `except: return []` makes a wrong-tree read look like a clean board |
| `trust_ledger.json` | 2 verdicts | 3 | can only UNDER-count `defects_found_post_close`, and drops the NEWEST verdicts — the evidence a recent close went badly |
| `.supervisor_stuck_state.json` | key 33 days old, no `episode_key`/`prior_unreadable` | current | a prior keyed to the wrong episode reads as "not stuck before" → escalation clock restarts every cycle |
| `.operational_layer_signal.json` | no `timed_out_at`/`blocked_by` | both present | the draw still FIRES (`last_result`/`consecutive_red` agree), so nothing looks wrong — it just hands over no evidence and blames "it predates the payload" |

Reads only. The `save`/`_save_ledger` side is deliberately untouched: a worktree's write was
already stranded and still is, and redirecting it would give a disposable tree a route to write
the shared record.

## What is left, and what is NOT yet established about it

Ranked by byte delta. **The direction of the error has NOT been established for any row below** —
only the delta has. Each still needs the per-reader read that the four above got, and the
counterexample table is the reason that cannot be skipped.

    size_ratchet_warnings.jsonl      71,513 -> 13,009,496   tools/size_ratchet{,_gate}.py
    retired_paths_served.json         5,748 ->    139,223   tools/retired_paths_still_served.py + 2
    model_tier_log.jsonl                797 ->  1,511,050   background/model_tier.py + 2
    test_execution_log.jsonl         18,286 ->    447,040   background/suite_duration_watch.py + 4
    edge_traffic.jsonl              130,580 ->  3,610,162   tools/edge_traffic_capture.py + 2
    lane_hook_denials.jsonl             317 ->      4,424   background/decision_log.py
    coupled_gap_ledger.json         168,967 ->    169,896   31 modules; the PUBLIC Proof door's ledger
    sanity_adjudication_ledger.json 207,874 ->    276,543   background/sanity_daemon.py + 1
    canon_drift.json                  4,554 ->      5,332   tools/canon_drift_check.py + 1

`coupled_gap_ledger.json` is the one to do next despite its small delta: 31 modules read it and it
feeds a public door. A small byte delta is not a small consequence.

Several rows (`run_history.json`, `run_insights.json`, `self_clearing_alarm_census.json`,
`value_based_pricing_arms.json`, `daemon_deployment.json`, `publish_gate_red_census.json`) are
SMALLER live than at HEAD, which is the `action_needed_register.json` shape — check before wiring.

## Method note worth keeping

The trust-ledger control did not fire on its first draft. It asserted the real missing verdict's
name (`H27_payment_belief_gap`), and that subject is ALREADY the last entry of the live ledger — so
a reader ignoring the resolver read the real file and passed. A fixture fitted to today's answer.
It now asserts a sentinel no real ledger can contain. **When a control's fixture uses a real value
from the live record it is testing, the mutant reads the live record and agrees.**
