**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [SEAT] the live-record resolver was not wired into the other two readers of the file it was named for

`background/live_ledger_guard.shared_tree_live_record` landed in `d895d845e` to stop a reader in
a linked worktree being handed git's stale checkout of a TRACKED live record. It was named for
`docs/observability/.publish_gate_state.json`. **That file has three readers and the commit wired
one.** The other two are `background/supervisor.py::_publish_gate_wedge_active` and
`tools/model_tier_report.py::_gate_failures`, and both are flattering on the stale copy.

This was drawn as "wire the remaining 22", which framed the work as the tail. The head was open.

## The census, measured 2026-09-16 in this worktree against the shared tree at `/home/rich/synthetic-enterprise`

`git ls-files docs/observability` gives 30 tracked paths that the drawn item counted; asking the
same question of the whole tracked set — *does the live byte content differ from `HEAD`'s?* —
gives **54**. The item's 23 was the subset it had enumerated, not the room. The room is
`is_live_record_path`'s room, and it is 54 wide today.

## The per-reader verdict, which is the work the resolver's commit explicitly did not claim

A reader is **FLATTERING** when the stale `HEAD` copy makes it UNDER-report a problem the live
copy would have reported. That is the only direction that matters: a stale copy that makes a
check fire twice costs a wasted tick; one that makes it not fire at all costs the finding.

| record | reader | `HEAD` says | live says | verdict |
|---|---|---|---|---|
| `.publish_gate_state.json` | `supervisor._publish_gate_wedge_active` | `failures: []` | `episode_failures: 37`, `alerted_at` set | **FLATTERING** — `len([]) < PUBLISH_GATE_WEDGE_MIN_FAILURES` returns `None`: *no wedge*, on a gate that has failed 37 times |
| `.publish_gate_state.json` | `model_tier_report._gate_failures` | `failures: []` | 37 failures | **FLATTERING** — reports a tier whose gate never failed |
| `.operational_layer_signal.json` | `supervisor._operational_layer_red_draw` | `last_result: "green"`, frozen at ts `1786721720` | `last_result: "green"`, ts `1789553731` | **FLATTERING BY CONSTRUCTION** — the only value that draws is `red`, and a frozen checkout can only ever hold what was committed. It agrees today by luck; it can never disagree. |
| `.supervisor_stuck_state.json` | `supervisor._load_stuck_state` | key field `"key"`, `first_seen_at` 2026-05 | key field `"episode_key"` — **a different schema** | **FLATTERING** — the current episode key can never match a record written before the rename, so `first_seen_at` resets every cycle and the stuck episode never escalates |
| `.human_last_input` | `console_instruction_record` capture-lapse check | `1788196377` | `1789557569` | **FLATTERING** — `lag_h = last_human - captured_end`; an OLDER `last_human` makes the lag SMALLER, so `lag_h > CAPTURE_LAG_FINDING_HOURS` goes false and the lapse this control exists to detect does not fire |
| `.product_interleave_state.json` | interleave owed-check | `owed: ["OPS13_..."]` | `owed: []` | **NOT flattering** — stale over-reports owed work. Fail-safe. Left alone deliberately. |
| `.last_tested_hash` | `process_run_complete` (2 sites) | a stale sha | HEAD's sha | **NOT flattering** — a stale sha never equals `git_hash`, so the gate re-runs. Costs a tick, hides nothing. Left alone. |
| `.daily_self_note_last_date`, `.sanity_daemon_last_digest_date` | once-per-day stamps | an old date | today | **NOT flattering** — stale republishes. Noisy, not flattering. Left alone. |
| `.seat_heartbeat.json` | `seat_continuity._read` | an old beat | a current beat | **NOT flattering**, and doubly so on inspection: stale reads as a DEAD seat and alarms, *and* `note_activity` is a read-modify-write over the same path (`prev = _read(p)` then replace), so it carries `.launch_records.json`'s hazard as well. It also runs on EVERY tool call, and the resolver spends a `git` subprocess per live-record read. Three independent reasons to leave it. |
| `.launch_records.json` | `launch_liveness.load` | — | — | **UNDECIDED, and deliberately not wired.** `record()` is a read-modify-write over this path. Resolving the READ without the WRITE makes a linked worktree read shared records and write them into its own copy, where the next read ignores them. Wiring this one needs the write side decided first, and the write side is governed by `guard_live_ledger_write`'s doctrine, not this resolver's. Filed as owed. |

**The distinction the drawn item asked for is real and it is roughly half.** Five of the eleven
readers surveyed are flattering; four are fail-safe and wiring them would be motion; one cannot be
decided from the read side alone.

## Pre-registration, written before the control was run

The wiring below is graded by a behavioural control, not by reading the call sites. **Prediction:
reverting any one of the five wired readers to its unresolved path makes exactly its own leg fail
and no other.** If a revert makes *no* leg fail, the control is a tautology and the wiring is
unproven. If it makes several fail, the legs are not independent and the control grades one thing
while claiming five.

The partition-reachability leg already in
`tests/background/test_a_live_record_read_from_a_linked_worktree_reads_the_shared_tree.py` is the
control over the whole room and is not duplicated per reader — that file's own docstring says why.

### The result, kept beside the prediction: REFUTED on first run, 2 of 6 mutations did not fire

Six reverts were run (five readers, and the wedge draw's paired `.last_tested_hash` half counted
separately). Four failed exactly their own leg as predicted. **Two failed nothing**, and under
the standing rule — *a mutation that does not fire is either a missing test or an equivalence,
establish which, and never assume it is the flattering one* — both were run down. Both were
**missing tests**, in the same shape: a fixture that agreed with the fixed and the broken code
alike.

- **`.last_tested_hash`** — the first draft gave the stale and live copies two arbitrary shas,
  neither equal to `head`. The "a pass at HEAD supersedes these failures" escape was therefore
  shut in *both* worlds and the two halves could not disagree. The reachable flattering state is
  the stale copy naming HEAD: a worktree detached at the very sha git's blob records reads *the
  gate passed at HEAD* and returns silence. Fixture corrected to that state.
- **`.human_last_input`** — the first draft put the stale stamp at "19 days ago" against a
  20-day-old capture, which is ~24h of lag, still over the 12h bar, so the reverted reader
  reported the lapse anyway. The stamp is now placed relative to the capture's own end instant
  the way the function measures it (+6h → no lapse). Fixture corrected.

After both corrections all six reverts fire, one leg each; the two `.publish_gate_state.json` /
`.last_tested_hash` reverts fire the same leg, which is correct — they are two halves of one
control and wiring one without the other is the defect that leg exists to refuse.

**What this cost and what it bought:** the prediction was worth writing precisely because it was
wrong. Two of the five wirings were, for twenty minutes, backed by legs that could not fail —
which is the condition `docs/design/CONTROLS_THAT_CANNOT_FAIL.md` is named for, reached by
writing the fixture before asking what would make it discriminate.

## What is owed after this

- `.launch_records.json`: decide the write side, then wire the read.
- The remaining tracked-and-stale records with no *decision-bearing* reader (the `.md` daemon
  logs, the `.jsonl` append-only series) were not surveyed per-reader. They are append-only or
  display-only and a stale read of them mis-renders a page rather than suppressing a check. That
  is a real but lesser class and it is NOT closed by this work.
