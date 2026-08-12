# WORKER FINDING — the wedge record cited a test that no longer exists, and the draw kept serving it

**Severity:** LATENT · **Lane:** H_harness

**Found:** 2026-08-12, worker tick drawn on the RUNG-1 publish-gate wedge doorbell.
**Class:** a hand-kept second copy of an answer the register already carries — the SAME class as
`WORKER_FINDING_THE_RECORD_THAT_ANSWERS_THE_DRAW_IS_NOT_REQUIRED_TO_BE_CURRENT_2026-08-12.md`,
in a different register. That one is `level_hold_note`; this one is `.publish_gate_state.json`.
**Disposition:** QUEUED (SELF_INTERRUPT_DISCIPLINE). Not blocking — it cost one round trip, not
the tick. **Rank requested:** backlog.

## What the draw handed me (observed-with-evidence)

The RUNG-1 doorbell fired priority-zero on a ~4496-min publish wedge. The one fact it offers a
diagnosing tick — `blocking_tests` in `docs/observability/.publish_gate_state.json` — read:

```
"blocking_tests": ["FAILED tests/company/test_phase_ob_settlement_reconciliation.py::TestRAGThresholds::test_zero_monthly_revenue_is_green"]
```

The first thing any tick does with that is run it. At HEAD (`5d1187fcf`):

```
$ python3 -m pytest "tests/company/test_phase_ob_settlement_reconciliation.py::TestRAGThresholds::test_zero_monthly_revenue_is_green"
ERROR: not found: .../test_zero_monthly_revenue_is_green
(no match in any of [<Class TestRAGThresholds>])
no tests ran in 0.03s
```

**The cited test does not exist.** It was renamed to
`test_zero_monthly_revenue_with_open_exposure_is_red` at `33592d8d1` (2026-08-12 18:10), an
ancestor of HEAD, as part of the repair for this very wedge.

## Why the record was stale, exactly

Every recorded failure predates the repair — verified with `git merge-base --is-ancestor`:

| recorded failure | commit | time | vs repair `33592d8d1` (18:10) |
|---|---|---|---|
| #1 | `4a26daece` | 17:00 | before |
| #2 | `cc4315beb` | 17:19 | before |
| #3 | `3abd6e1df` | 17:35 | before |
| #4 | `3e80712ef` | 17:49 | before |

The true cause was `2abb973c2` (16:49), which correctly changed `_rag` to return RED for open
exposure at zero revenue but left the sibling test asserting GREEN — source and test landing in
one commit, disagreeing.

## The asymmetry that makes this a defect rather than a stale field

`.last_gate_blocking_tests.json` — the *upstream* record — **is** guarded. `last_blocking_tests()`
returns `([], None)` for absent, unreadable, malformed **and stale**, and its docstring is explicit
that all four mean "this alarm does not know". That is the right shape.

`.publish_gate_state.json` then persists a **snapshot copy** of that value
(`_write_publish_gate_state(... "blocking_tests": blocking ...)`), and the copy inherits **none of
the guard**. It is written fresh at failure time and then simply sits there — through a repair,
through a rename, indefinitely — with no relation to HEAD asserted at read time.

So the guarded record correctly forgets, and the unguarded copy of it keeps answering.

## Why nothing caught it

The freshness guard is **time-based** (`2 * GATE_SUITE_TIMEOUT_SECONDS`), which answers "was this
recorded recently?" — a good proxy for the case it was built for. It cannot answer the case here:
the record *was* recent when written, and what changed underneath it was **the tree, not the
clock**. A node id is a claim about the current tree; nothing resolves it against one.

This is the FAIL-SILENT pattern in R15's own terms. "Not found" from pytest is ambiguous between
*the record is stale because the cause was repaired* (true here, benign) and *collection is
broken* (alarming). The reader cannot tell which without doing the git archaeology above.

## Recommended fix (not applied this tick)

Resolve, don't just store. Where the state is written or rendered for the draw, check each cited
node id against the current tree (`--collect-only -q` on the node id, or the already-materialised
HEAD checkout) and label it:

- resolves → cite it as now
- does not resolve → `RECORDED BLOCKER NO LONGER EXISTS AT HEAD (renamed or removed) — this
  record predates a repair; re-run the gate for a current blocker`

Never silently drop it: absent and repaired are different facts, and the distinction is the whole
point of the guard above.

**R15 both ways, mutation-tested:** (a) a live blocker still resolves and is still cited — mutate
by deleting the test, assert the label flips; (b) a repaired/renamed blocker is labelled and is
NOT presented as current work — mutate by restoring the old name, assert it is cited plainly.

## What this cost

One round trip on a priority-zero draw: run the named test, get "not found", then reconstruct the
repair from `git log` to learn the record was simply old. Small — but it lands on the single path
the project has designated priority zero, at the moment a tick is hunting for a cause, and
[[feedback_a_bare_head_extract_is_not_the_gates_subject]] is on record for how a reproduction
artefact becomes a filed false cause in exactly that window.
