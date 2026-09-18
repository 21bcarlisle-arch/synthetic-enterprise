**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# PRE-REGISTRATION — can the selection-leg family be refolded larger than eighteen from artefacts already in the tree?

A pre-registration, not a defect. Filed before the measurements it describes.

**Filed:** 2026-09-17 ~22:25 BST, from the isolated worktree at `ea3780580`.
**Claim:** `the-selection-leg-is-six-seeds-short-of-a-sign-and-its-point-estimate-is-negative`
**Answered by:** `SEAT_RESULT_THE_PUBLISHED_EIGHTEEN_POOLS_TWO_VALUE_ARMS_AND_THE_SIGN_IT_CANNOT_STATE_IS_STATEABLE_ON_ONE_2026-09-17.md`

---

## Why this is being asked now

The drawn item is *"refold the selection-leg family and publish it"*, and it names two long jobs as
the source of the new seeds. Measured at draw time, both premises about those jobs have moved:

1. **The AUC leg is finished AND already landed.** `/var/tmp/value_cycle_ab_floor_with_auc_20260917.json`
   is byte-identical (`diff` over `json.tool`, rc=0) to
   `docs/observability/value_cycle_ab_s1_noise_floor_auc3_20260917.json`, committed in `ab71cf877`
   ("the AUC is measured for the first time and it does not clear its own null"), which is an
   ancestor of `origin/main`. The item's instruction to *"copy each artefact into
   docs/observability/ and commit it"* is therefore **spent for this artefact**, and its 3 seeds are
   *already* refused entry to this family by `c21d9209e` on disjoint-operating-point grounds
   (`level_gbp_per_mwh` 38.50/38.50/36.25 against 20.00 on all eighteen).

2. **The next12 leg cannot land this turn.** `longjob-floor-next12-20260917` is `ActiveState=active`
   with `CPUUsageNSec` = 7,783 s (~130 min CPU) against an ~11h estimate, started 19:11:33 BST.
   `/var/tmp/value_cycle_ab_s1_noise_floor_next12_20260917.json` does not exist. There is nothing to
   copy and no 30-seed fold to perform.

So the only refold available to this turn is from floor artefacts **already in the tree**. That is a
question nobody here has looked at, and it is worth asking before spending 11h of compute on twelve
more seeds: if the family can legitimately grow from evidence we already own, the sign question is
answered at zero marginal cost.

## The question

Of the floor artefacts in `docs/observability/`, how many are **legitimately foldable** into the
published eighteen — same world digest, same `redraw_scope.mode`, same `clock`, same level-arm
operating point, and no repeated seed?

## Prediction, before running the census

**The published eighteen is already the maximal legitimate fold, and the census will find no
additional foldable member.** I expect every other floor artefact in the tree to fail at least one
leg: a different `redraw_key`/`redraw_scope.mode` (the `only`/`except` partition probes), a
different world digest, a repeated seed, or a different level operating point. The reason is not
statistical — it is that a prior turn assembled `value_cycle_ab_s1_noise_floor_folded18_20260917.json`
from exactly two sources deliberately, and a third eligible source sitting unfolded beside it would
be an omission rather than a choice.

**If this prediction is wrong** — if a foldable member exists — then the eighteen understates the
evidence we hold, the published `seeds_needed_to_state_a_sign` of 24 is priced off too small a
family, and folding it is this turn's work.

**Stated so it can fail:** the census prints, per artefact, the five comparison legs and a
verdict. A single artefact passing all five refutes the prediction above.

## The item's own prediction, restated so it stays next to its answer

Filed by the drawn item before the twelve seeds land, and **not** discharged by this turn:

> the refolded family will NOT state a sign at 24 and the negative point estimate will hold.

That is a prediction about the 30-seed family (18 + 12), and it can only be graded when
`longjob-floor-next12-20260917` settles. It is recorded here so that it is read beside its result
rather than revised after it.

## Second question, pre-registered before looking — is the book seam a RUN seam?

The census (reported in the result document named above) refuted nothing but surfaced something I
did not expect and did not go looking for: **three** artefacts carry the seed set 11111–99999 at the same
world digest, the same `mode=all`, the same clock and the same £20.00 level arm —
`value_cycle_ab_s1_noise_floor.json`, `..._20260909b.json` (a fold source) and `..._20260910.json`
(not a fold source). Same seeds, same world, same operating point, drawn from different code trees.

That makes a replication test available for free, and it bears directly on the item's WHY. The seam
the item splits the eighteen at — "the half that names its book" versus "the half that does not" —
**is the run seam**: the book-less half is all of `20260909b` (n=9, mean -1078.17) and the
book-naming half is all of `20260910b` (n=9, mean -170.09). The two halves are two *runs*, not two
samples from one run. So the £908 between them is confounded: it could be redraw noise, or it could
be whatever changed in the tree between the two runs.

**Prediction, before I read the numbers:** the per-seed `selection_gbp` in `20260909b` and
`20260910` will **differ**, despite identical seeds, world, mode, clock and level arm — because the
two carry different producing commits, and one records a book while the other records none, which is
itself evidence the tree moved between them. I further predict the per-seed differences will be
**material against the family's own spread** (stdev £1,473), i.e. not rounding.

**What each outcome means.** If they are identical, the seed set alone determines the figure, the
book seam carries no tree effect, and pooling the eighteen is clean. If they differ materially, the
published eighteen pools two code trees, its spread is **not** the elasticity-redraw floor it is
labelled as, and the £908 between halves has a candidate cause that is not noise. The second is the
outcome that would make this a finding rather than a note.

**This cannot be graded by the twelve seeds in flight.** `next12` is one run on one pinned tree, so
it can widen the family but can never separate run effect from redraw effect. Only a same-seed
comparison can, and the tree already holds one.

## Why the 24-seed price is not robust

From the item's own WHY, and it is the reason the second question above matters:
Split the eighteen at the book seam and `seeds_needed` is 23 pooled, 121 on the half that names its
book (n=9, mean -170.09, sem 310.59) and 12 on the half that does not (n=9, mean -1078.17, sem
603.50). Both halves are negative, so the *sign* of the point estimate is not in question — only the
price of stating it. The halves' means differ by £908, 1.34 standard errors of their difference and
therefore itself unstateable, so pooling is not refuted and the family must not be cut on this
evidence.
