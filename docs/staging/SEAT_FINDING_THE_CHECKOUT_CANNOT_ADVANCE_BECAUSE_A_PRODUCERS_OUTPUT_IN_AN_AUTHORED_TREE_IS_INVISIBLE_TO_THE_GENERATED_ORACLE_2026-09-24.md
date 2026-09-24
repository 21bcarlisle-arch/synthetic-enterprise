**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The shared checkout cannot advance because a producer's output living in an authored tree is invisible to the generated-path oracle — and the producer's own repair is stuck behind that same gap

Claim id: `the-shared-checkout-is-the-second-gap-between-a-landed-commit-and-a-running-daemon`.
Measured 2026-09-24, after landing `5eba17198` (which made the gap measurable —
`records/SEAT_RESULT_THE_CHECKOUT_GAP_IS_MEASURED_AND_A_RESTART_WOULD_HAVE_HIDDEN_IT_2026-09-24.md`).

## The state

`deploy_restart.checkout_drift()` on the shared tree, after the landing above:

```
{'behind': 12, 'ahead': 3, 'contains_origin': False, 'gap_paths': 32}
MISSING 12 commit(s) from origin/main (32 path(s) the daemons cannot load whatever their stamp says)
```

It is DIVERGED, so no fast-forward is possible until the tree's own 3 commits reach origin.

## Why the reconciler never closes it — two causes, both measured

**Cause 1: the refusal names producer output that nothing recognises as producer output.**

`origin_reconcile`'s `NOT_ADVANCED` refusals name 11 paths, and 9 of them are the
`docs/staging/WORKER_FINDING_REPEATING_ALARM_*.md` family — *"modified here, and origin changes it
too"*. These are rewritten every tick by `background/alarm_repetition.py`. `advance_shared_tree`
grew a fifth blocker class on 2026-09-18 for exactly this shape (`generated_output_verdicts` — *"a
PRODUCER'S OWN OUTPUT: never hash-equal because its producer rewrites it every tick"*).

**It does not reach them.** One-variable control, run against the shared tree's own copy:

```
origin_reconcile._split_generated(['docs/staging/WORKER_FINDING_REPEATING_ALARM_SEAT_CLAIM_2026-09-15.md'])
  -> ([], ['docs/staging/WORKER_FINDING_REPEATING_ALARM_SEAT_CLAIM_2026-09-15.md'], '')
```

Generated list **empty**; the path is classified **authored**. `docs/staging/` is an authored tree,
so a regenerated document living inside it is invisible to the oracle — and under the module's own
all-or-nothing rule one permanently unresolvable path is fatal to every other class beside it.

This repo already names the shape in the opposite direction:
`tests/tools/test_a_generated_path_in_an_authored_tree_is_still_generated.py` exists, and
`file_scope_generated_paths` carries `AUTHORED_UNDER_A_GENERATED_TREE`. The mirror case — a
GENERATED path under an AUTHORED tree — is the one live here, and it is the blocker.

**Cause 2: the gate's run lock starves the reconciler.** Over the last 40 logged cadences:

| outcome | count |
|---|---|
| `GATE_RUNNING` | **19** |
| `REFUSED_CONFLICT` | 10 |
| `NOT_ADVANCED` | 7 |
| `LEVEL` | 4 |

The reconciler stands down for the publish gate on roughly half of all cadences and never reaches
a decision window at all. The two most recent entries (04:55Z, 05:00Z) are both `GATE_RUNNING`.
This is the deadlock already in this seat's memory — the gate is slow/red partly *for being
behind*, and the thing that would fix behind stands down for the gate.

## The recursion, which is this item's whole thesis one turn deeper

`background/alarm_repetition.py` differs between the checkout and origin by **130 insertions and
375 deletions** — a substantial rework (`9640ca528`, `6ccae119e`, `22ec75803`, `465a0dfca`) sitting
on origin and absent from the box. The daemon rewriting the blocking documents is running the OLD
code, and the new code cannot reach it because those rewrites are what blocks the advance.

**A producer's output blocks the checkout that carries the producer's repair.**

## NOT established, and recorded rather than guessed

Whether the reworked `alarm_repetition.py` would actually stop rewriting those 9 documents. One of
the landed notes is titled *"the alarm document is no longer its own store **and the collision is
still there by design**"*, which reads as saying it would NOT. If so, Cause 1 is the whole remedy
and the recursion is a compounding factor rather than the mechanism. **Do not assume the restart
fixes it** — that assumption is the same shape this claim exists to refuse.

## The remedy, in the order the evidence supports

1. **Teach the generated-path oracle that `docs/staging/WORKER_FINDING_REPEATING_ALARM_*.md` is
   producer output**, so class five can clear it. This is the load-bearing step and it is the only
   one that makes the tree advanceable without a person. Note `file_scope_generated_paths` is a
   frozen-count census with membership pinned by tests — this is its own careful piece of work, not
   a one-line addition, which is why it is handed on rather than half-built here.
2. Re-measure with `deploy_restart.checkout_drift()`. It is now the honest oracle:
   `merge-base --is-ancestor`, never `reconcile-watch`'s exit code.
3. **Only then** restart the daemons. Doing it before the checkout advances clears all eleven
   `stamp-predates-process` verdicts and delivers none of the repair — see the result note.
4. Separately: `GATE_RUNNING` starving the reconciler on half of all cadences is a second,
   independent defect and wants its own measurement.

## What this turn did NOT do, deliberately

Advance the shared tree. It is diverged and its 9 blocking paths are another lane's uncommitted
producer output; clearing them by hand is the judgement `origin_reconcile` refuses to make
unattended, and this turn's isolation from the shared index is the reason it was allowed to run.
The refusal's own words: *"THE STEP IS TO LAND OR REVERT THOSE PATHS, NOT TO RE-RUN THIS MODULE."*
