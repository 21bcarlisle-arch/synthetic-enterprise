# WORKER FINDING — the wedge detector fed itself: publishing a green moves HEAD past the green

**Date:** 2026-08-12
**Severity:** BLOCKING · **Lane:** H_harness
**Status:** FIXED + mutation-proven. Second, genuine red found and fixed in the same pass.
**Class:** R15 — a control whose independence check is unsatisfiable in the state it exists to judge.

## What the doorbell said

> the publish gate has been FAILING for ~4528 min (4 failures in-window, **no pass at HEAD
> bfd97592c**) and is BLOCKING ALL publishing … EPISODE: 201 consecutive failures.

## What was actually true (observed-with-evidence, R9)

| Claim | Evidence | Verdict |
|---|---|---|
| The named blocking test is red | `pytest …::TestRAGThresholds::test_zero_monthly_revenue_is_green` → **"not found"** | **inferred, false** — split into two tests at `0bfb796d2` |
| The gate has not passed | `.last_tested_hash` = `62818325d`, mtime 18:34:52 — sole writer is the gate's own rc=0 | **observed** — it passed |
| Publishing is blocked | commit `999517203` "Auto-process run complete … net=£1,526,252" at 18:34:53 | **observed** — it published |
| The queue is backed up | `ls docs/staging/run_complete_*.md` → **0** | **observed** — drained |

Every recorded failure **predates** the green. Newest failure was at `3e80712ef` (17:49 BST); the
repair `0bfb796d2` landed 17:54; the gate went green at `62818325d`.
`git merge-base --is-ancestor 3e80712ef 62818325d` → **the pass is a descendant of the last
failure.** There was no wedge. There had been no wedge for hours.

## Root cause — the check could not be satisfied by a healthy pipeline

`supervisor.py::_publish_gate_wedge_active` cross-checked independence with **exact equality**:

```python
if head and last_tested and head == last_tested:   # a pass at HEAD => stale failures
    return None
```

The gate's subject is a **commit**, so a green is stamped at the SHA the suite ran against. But
**publishing that green result is itself a commit** — and every other lane keeps landing too. Eight
commits sat between the pass and HEAD. Equality can therefore never hold *precisely when the gate is
healthy and busy*, which is the one case the check exists to detect.

The failure mode was not merely stale, it was **self-perpetuating**: the phantom draw fires
priority-zero → the tick it wakes does real work and commits it → HEAD moves one further from the
recorded pass → the next tick's draw is armed harder. 201 consecutive "failures" over ~75h, each
tick making the next worse.

This is the **same rule the sibling consumer had already fixed on its own side of the contract**.
`record_publish_gate_outcome` keys on the **marker's** hash, and its docstring names this exact
hazard — "HEAD moves under a long publish cycle as other lanes land, so a HEAD-keyed check would
refuse to clear after a genuinely green gate". `LAST_TESTED_HASH_CONTRACT` names two consumers; the
fix reached one of them. (Memory class: *the shared rule reached two of three sweeps*.)

## The fix

`_gate_pass_supersedes_failures()`: the failures are stale when `.last_tested_hash` names a commit
**on HEAD's history** that is **strictly newer than the newest recorded failure**, established by
git ancestry. Exact-equality fast path kept.

**Independence is preserved, not traded away.** Failure SHAs come from the publish-outcome state
file; `.last_tested_hash` is written by exactly one writer (the gate's rc=0); git ancestry supplies
the ordering neither carries. A publisher that publishes nothing still cannot manufacture a green.

**Fail-safe toward drawing** in every uncertain direction: no usable failure SHA, a pass off HEAD's
history, a pass at the same commit as the failure, or ancestry unknowable → still draws.

## R15 mutation proof

Tests use a **real git repository**, not a stubbed ancestry oracle — the defect is a claim about
ancestry, so a mocked oracle would pass just as happily against the broken check (TAUTOLOGY).

| Direction | Result |
|---|---|
| Guard live, live-defect scenario | **PASS** |
| Guard disabled at runtime | **FAIL** ← load-bearing |
| Must-still-draw set, guard disabled | **PASS** ← never depended on it |

Must-still-draw directions pinned: pass *predates* the failures; pass on a branch HEAD never took;
ancestry unknowable; pass at the same commit as the failure. **20 passed.**

Verified on real disk state: `_publish_gate_wedge_active()` → **None**.

## The second finding — a genuine red hiding behind the phantom

`tests/background/test_self_clearing_alarm_census.py::test_every_live_hit_is_dispositioned` was
**red at HEAD**, unmarked and therefore inside the publish gate's scope. Two state paths from the
ntfy-digest lane (`dea39a3bf`) were undispositioned. Both dispositioned `benign` after reading the
code, not by rubber-stamp:

- `ntfy_digest_queue.jsonl` — opened `"a"`, never rewritten/truncated anywhere in the module.
- `.ntfy_digest_state.json` — the **inverse** of this class: the write happens only inside
  `if _was_delivered(result)`, so the failure path writes *nothing* and undelivered items ride the
  next digest. Neither key is an episode clock.

**The phantom was masking a real one.** A detector that cries wolf every tick is not merely noisy —
it buries the genuine red in its own noise.

## Disposition of the two cited findings

The alarm cited two findings as "already holding the suspects". Neither was a cause: the wedge was
phantom, so no suspect could be. `…ARCHIVED_FINDING_LEFT_A_COPY…` is already in `done/`;
`…PUBLIC_PANEL_SERVED_LOADING…` remains open as a product finding, unrelated to the gate.

## Residue (QUEUED, not fixed here — SELF_INTERRUPT_DISCIPLINE)

The wedge **record** still reads RED in the working tree (`episode_failures: 201`, frozen 18:05)
because `record_publish_gate_success` is only routed from *outside* the publisher, after the
subprocess exits — filed by the previous tick as
`WORKER_FINDING_THE_WEDGE_CLEARS_ON_PROCESS_EXIT_NOT_ON_THE_RECORDED_PASS_2026-08-12.md`. The draw
is now correct regardless of that field, so this costs accuracy in a future episode's *age*, not
publishing. HEAD's committed copy is already clean (`{"alerted_at": null, "failures": []}`); the
live file is daemon-owned and deliberately left to its owner rather than hand-edited under a
concurrent writer.
