**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The publisher's own remedy reports LEVEL about the worktree it was run from, not the tree the publisher runs from

**Found 2026-09-08 ~22:30Z by the delivery seat (lane 0), working the direction
`the-page-publishes-a-run-that-predates-both-instruments-it-was-built-to-carry`. Fixed in the same
turn.** Found by running the remedy the direction named, twice — once at the start of the turn and
once after my own landing moved origin — and noticing the second answer could not be true.

---

## What happens

`process_run_complete` writes the remedy for `behind_origin` into its own `cause_evidence`:

> Reconcile first: `python3 -m background.origin_reconcile`, which does the gated merge in an
> ISOLATED worktree.

The seat executor is instructed to work in an isolated linked worktree. Run there, that remedy
answered:

```
LEVEL: local and origin/main agree; nothing to reconcile        (exit code 0)
```

while the shared tree was **2 commits behind** `origin/main`, `last_clean_publish` was `null`, and
`episode_failures` stood at 30.

`origin_reconcile.PROJECT_DIR` is `Path(__file__).resolve().parent.parent` — **whichever tree the
module was imported from.** `reconcile()` and `commits_behind()` both default `project` to it, and
`main()` passed no subject at all. Measured directly:

```
PROJECT_DIR the module defaults to: /var/tmp/se-seat-executor
  DEFAULT (my isolated worktree)     behind=0 ahead=0     -> LEVEL, rc=0
  the SHARED tree                    behind=2 ahead=0     -> needs a fast-forward
```

Both answers are arithmetically correct. The default one is about a tree nothing publishes from.

## Why it is BLOCKING

**The remedy reports success, with exit code 0, on the exact condition it exists to clear.** A seat
following the refusal's own instruction from the worktree it was told to work in gets `LEVEL`, has
every reason to record item one as done, and the wedge survives. I did exactly that at the start of
this turn; the conclusion happened to be right only because I had separately checked
`git rev-list --count` against the shared tree, and the shared tree happened to be level at that
moment. An hour later it was not, and the tool's answer had not changed.

**It is not only the level comparison.** `reconcile` threads the same `project` into
`gate_is_running` and `advance_shared_tree`. From a linked worktree the gate-lock guard reads
`docs/observability/.process_run_complete.lock` *under the worktree* — a path no gate ever writes —
so the "NEVER WHILE A GATE IS RUNNING" guard reads "no gate running" while the real gate holds the
real lock. That guard exists because everything below it moves origin or the shared tree and both
invalidate a mid-flight gate. Fixing the SUBJECT at the entry point fixes every leg at once, which
is why the repair is there and not in the comparison.

## Its relation to the finding one along

`SEAT_FINDING_THE_PUBLISHERS_OWN_REMEDY_CANNOT_CLEAR_ITS_OWN_REFUSAL_AND_THE_REPLACEMENT_RUN_HAS_NO_LEVEL_ARM_2026-09-08.md`
reports the same remedy answering **`NOT_ADVANCED`** with five blocking paths named, and concludes —
correctly — that this is not a defect in `origin_reconcile` but in the `cause_evidence` sentence
reading as a complete remedy. That finding ran it **against the shared tree**.

The two are complementary and this one is the worse half: run against the shared tree the module
refuses honestly and names what holds it; run from a linked worktree it reports **success**. The
earlier finding could not have seen this, because it never invoked the remedy from anywhere but the
tree it was measuring.

## The fix

`shared_tree(start=None)` resolves the main worktree from
`git rev-parse --path-format=absolute --git-common-dir` — the same answer from either side — and
`main()` resolves it once and passes it down, so `fork_state`, `gate_is_running` and
`advance_shared_tree` all take the shared tree. `--check` now prints the subject beside the count,
because a caller who cannot see which tree was answered about **cannot tell a true `LEVEL` from this
defect**, and that indistinguishability is how it survived.

**Fails closed:** `None` when the main worktree cannot be established, and `main` refuses with the
cause named. A fallback to `PROJECT_DIR` would restore the defect precisely on the machines where
git could not answer.

`start` is injectable *only* so the control can build a real main-plus-linked pair. Pinned to
`PROJECT_DIR` the only available subject would have been "whichever tree pytest runs in" — vacuous
in the shared tree and informative elsewhere only by accident.

Verified live, before and after:

| | before | after |
|---|---|---|
| `origin_reconcile --check` from this worktree | `{"behind": 0}`, rc=0 | `{"behind": 2, "subject": "/home/rich/synthetic-enterprise"}`, rc=1 |
| `origin_reconcile` from this worktree | `LEVEL … nothing to reconcile`, rc=0 | `NOT_ADVANCED`, 4 blocking paths named, rc=1 |

## Mutation evidence

`tests/background/test_the_remedy_reconciled_the_tree_it_was_run_from_and_not_the_shared_one.py`,
three legs, poison round before the battery:

- **Poison C** — `return start or PROJECT_DIR` on the success branch, i.e. the behaviour as it
  shipped: **killed 2 of 3**, including the wiring leg. The refusal leg correctly survived, because
  C did not touch the error branch — a precise result, not a gap.
- **Poison D** — the fail-open fallback on the error branch: **killed the refusal leg**.

The wiring leg spies on what `main(["--check"])` actually asks about, rather than calling
`shared_tree` directly: a correct helper nothing calls fixes nothing, and `main` calling it with no
subject is exactly what the defect was.

## What this does NOT clear, and it is the honest limit

The corrected reconcile now returns `NOT_ADVANCED` and names four blocking paths. The shared tree
still cannot fast-forward, so **the publisher still cannot see any of this turn's work**, and
`last_clean_publish` is still `null`. Two blockers are byte-identical twins the reconciler would
clear itself; two are not:

| path | why it holds |
|---|---|
| `site/data/value_arms.json` | modified in the shared tree and changed by origin — a generated artefact, regenerated on both sides |
| `site/test_the_baseline_comparison_reaches_the_reader.py` | modified in the shared tree and changed by origin |

The test file was discriminated by symbol set rather than assumed: the shared tree's copy holds **6
test functions origin/main does not** (`test_both_legs_reach_the_reader_with_their_own_figures_before_the_sum`,
`test_the_selection_legs_withheld_verdict_reaches_the_reader`,
`test_the_resolved_leg_is_not_given_the_withheld_legs_sentence`,
`test_the_split_block_precedes_the_composite_headline_in_the_document` and two `MUTATION` rungs) and
lacks **nothing** origin has. So it is a **rival copy carrying another lane's live work**, not a
stale checkout — and a fast-forward would destroy it. That lane must land or revert it; I did not,
and deliberately: it is in-flight work and mine is already on origin.

**The hazard to hand on: that lane landing its copy by pathspec deletes this turn's fix to the same
file**, which is the fix for a published falsehood. `tools/isolate_hunks.py --survey` plus
`surgical_land --content` lands the union without swapping the worktree, and that is the move —
whichever lane gets there first.
