**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Class:** controls_that_cannot_fail · **Atom:** (Lane 0 delivery — confirm the first clean publish after the split pair landed)

# A live record is TRACKED, so every worktree reads a two-month-old placeholder as live state

**Found:** 2026-09-16, Lane 0 delivery, claim
`publish-wedge-confirm-the-first-clean-publish-after-the-split-pair-landed`
**Pre-registration:** `PREREG_IS_THE_COPY_TEST_STILL_RED_AT_HEAD_AFTER_THE_SPLIT_PAIR_LANDED_2026-09-16.md`

## The finding

`docs/observability/.publish_gate_state.json` is **tracked in git**. Its only commit is
`f534b9f3d`, 2026-07-17, content in full:

```json
{"alerted_at": null, "failures": []}
```

Every linked worktree checks that out — and the seat executor *mandates* that delivery turns run
in a linked worktree. Fed to `process_run_complete._read_publish_gate_state`, every `setdefault`
in that function lands on the flattering value: `episode_failures` 0 (`len([])`), `total_red` 0,
`wedge_since` None, `blocking_tests` empty, `state_unavailable` **False**. It reads as a publisher
that has never failed.

The live file on the shared tree, read at 05:48:24Z the same morning, read
`episode_failures: 34`, `last_clean_publish: null`, `wedge_since` 2026-09-15.

Each of those `setdefault` lines carries a careful comment reasoning about a state file "written
before this field existed", and several explicitly choose the fail-CLOSED direction for that case
— `episode_failures` defaults to the in-window count and the comment says "never to 0, which would
UNDER-report a live episode". That reasoning is correct and it is blind to this case: the file is
not old, it belongs to **a different tree**.

## How it was reached, which is the part that matters

This finding is not incidental. The drawn item's own done-condition was:

> read `docs/observability/.publish_gate_state.json` for `last_clean_publish != null` and
> `episode_failures == 0`

Followed literally from the worktree it was issued in, the placeholder answers **yes** to the
second clause and omits the first entirely. A seat that read its own tree — the obedient reading —
would have recorded a 146-hour publish wedge as cleared on the strength of a two-month-old empty
file. The instruction and the defect point the same way.

## It is a class, and one member of it was already closed

`background/live_ledger_guard.py` fixed the **write** side at the choke point and derives its
room rather than listing it: *a live ledger == any path under `docs/observability/`*. The **read**
side had been fixed once, privately, for one file — `seat_executor._shared_tree_log`, written
after the same rebinding made `ids_run_since` answer `[]` and an orientation report
`drawn: [], steered: false`. Its docstring names the cause exactly: `PROJECT_DIR` is derived from
`__file__`, so a module imported out of a linked worktree silently rebinds the whole published
record to that worktree.

Measured statically over the daemons, 2026-09-16:

| | count |
|---|---|
| live-state paths written under `docs/observability/` | 75 |
| of those, **tracked in git** | 30 |
| of those, HEAD content **differing from live** | 23 |
| of those, already closed (`_shared_tree_log`) | 1 |

Twenty-three files whose checked-out copy is a stale answer to a live question. One had been
fixed. `.publish_gate_state.json` was the next one to bite, and it bit the delivery lane's own
done-condition.

## What landed

`live_ledger_guard.shared_tree_live_record(path)` — the read-side resolver, beside
`is_live_record_path` and deriving the same room. In a linked worktree it resolves a live record
to the shared tree's copy via `git rev-parse --git-common-dir`; in the main tree, for a non-live
path, when git will not answer, or when the shared copy is absent, it returns the path unchanged.
It is a resolver and not a guard on purpose: every caller already handles a missing file, and
turning a working read into a raise would break orientation paths that must survive it.

Wired into two consumers: `process_run_complete._read_publish_gate_state` (the instance above) and
`seat_executor._shared_tree_log`, whose private body it replaces.

Graded by `tests/background/test_a_live_record_read_from_a_linked_worktree_reads_the_shared_tree.py`
against a real git worktree, not a mock of one. Mutation-proven:

- resolver body → `return path` (the pre-fix behaviour): **2 legs fail**, including the partition control.
- publish-gate reader reverted to read the tracked file directly: **the wiring leg fails**.
- room guard deleted: **nothing fails — established as an EQUIVALENCE, not a missing test.**
  `relative_to(LIVE_RECORD_DIR)` below it refuses every path the guard would have. The line is
  kept only because it skips a `git` subprocess per non-live read, and now says so in place so the
  next reader does not take it as graded.

## What is NOT claimed

The remaining 22 tracked-and-stale live records are **not** fixed. The mechanism now exists and
derives the whole room, but only two callers resolve through it. Each remaining reader is its own
wiring, and whether a stale read is harmful depends on whether that reader's defaults are
flattering — `.publish_gate_state.json`'s are, which is what made it reachable and severe. That
survey is the next piece of work and is handed on rather than claimed here.

## Why a BLOCKING finding is filed in `done/` on the day it was written

Not because it is finished — it is not; 22 readers are still unwired. `finding_classes --render`
consolidated it into `CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md` on sight, and `--check` then
refuses any document that is named by a class register and still sitting in the staging root. The
consolidated design is that the **class** is the drawable unit and `class_debt.py` ranks it by what
it has cost; that class's own disposition records `OPEN` as its drawable state. So the remaining
work is carried there and in this turn's hand-off, not by leaving this file in the queue. Read the
"What is NOT claimed" section above as the live part.

## The prior of this shape

`site/data/delivery.json` already records, on 2026-09-03: *"`.publish_gate_state.json` now reports
`total_red` 0 and `blocking_tests` empty while carrying `last_clean_publish` null and a live
`gate_refusal` — the exact shape that reads as green and is not"*, and notes the failure mode is
"structural and unfixed", with *"saying so on the surface is an exhortation, not a mechanism"*.
That entry was right about the shape and did not have the cause. The cause is that the file is
tracked.
