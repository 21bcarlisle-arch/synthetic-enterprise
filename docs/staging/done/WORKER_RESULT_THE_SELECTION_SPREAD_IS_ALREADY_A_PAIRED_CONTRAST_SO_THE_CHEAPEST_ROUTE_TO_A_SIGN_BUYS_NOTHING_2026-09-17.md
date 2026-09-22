# The selection spread is ALREADY a paired contrast, so the cheapest route to a sign buys nothing

**Date:** 2026-09-17
**Lane:** A_strategy_governance (drawn as a Lane 0 delivery-seat direction — part THREE of
"make the selection leg's published arithmetic honest about one objective, then establish whether
a sign is reachable at all")
**Subject:** `tools/selection_variance_decomposition.py` (new);
`tests/tools/test_selection_variance_decomposition.py` (new);
`docs/observability/selection_variance_decomposition_20260917.json` (new)
**Severity:** BLOCKING — `site/data/value_arms.json` publishes
`seeds_needed_to_state_a_sign: 24`. On the objective the company actually prices under, computed
by the artefact's own `distance_to_a_sign`, the number is **121**. The page understates the
distance to the thesis question by a factor of five.
**Item** `the-page-prices-a-sign-off-a-spliced-family-and-nobody-has-asked-where-the-variance-comes-from`
**Answers** `WORKER_RESULT_THE_EIGHTEEN_SEED_FAMILY_IS_SPLICED_ACROSS_AN_OBJECTIVE_CHANGE_AND_THE_TWENTY_FOUR_SEED_PRICE_CAME_OFF_THE_SPLICE_2026-09-17.md`

---

## What was asked, and what part of it this is

The item had three parts. **Part ONE is not doable this turn and part of it is refuted.** The
twelve seeds it names (`3100001`–`3100012`, PID 3819244) had not settled — at 23:00 the job was
3.8 hours in with no `/var/tmp/value_cycle_ab_s1_noise_floor_next12_20260917.json` on disk. And the
fold it asks for is the thing a concurrent seat holds a live claim against
(`read-next12-alone-it-cannot-be-folded-into-the-eighteen`): those seeds are pinned at `7da627b90`,
which differs from the published family's tree in 18 simulation files. **A refold on "the 24" is
not available and would not be one family if it were.**

So this turn did part THREE, which the item itself says is the part that decides what comes after,
and which needs no draw at all because the per-seed arm values are already on disk.

## The decomposition

`selection_gbp = value_advantage − level_advantage`, both measured on the **same seed**.

| component | share of the spread | how it was established |
|---|---|---|
| common to both arms | **82.3%, and ALREADY REMOVED** | across-arm covariance on the one-objective family |
| per-household elasticity draw | **100% of what remains** | by construction — the family re-draws only elasticity |
| book composition | **not estimable here** | the book is held FIXED across seeds; this is a fact about the experiment, not the book |

On the current-objective family (`...20260910b.json`, `9f0ab066f`, n = 9): had the two arms been
drawn on independent seeds the variance would be £4,905,110; realised it is £868,221. The
correlation between the arms is **0.829**.

**The subtraction that produces the published figure IS a paired estimator, and it is already in
force.** There is no unpaired version of `selection_gbp` awaiting improvement.

### The exactness, printed

Two dated `all`/`only` pairs show *why* the cancellation is exact. Households outside the priced
roster shift **both** arms by the same number to ten decimal places, so the differencing removes
them entirely — `selection_gbp` is bit-identical between the two runs on every seed of both dates:

| date | seed | shift in value arm | shift in level arm | `selection_gbp` identical |
|---|---|---|---|---|
| 2026-09-03 | 11111 | £420.5413190000 | £420.5413190000 | yes |
| 2026-09-03 | 22222 | £420.5413330000 | £420.5413330000 | yes |
| 2026-09-03 | 33333 | £420.5413190000 | £420.5413190000 | yes |
| 2026-08-31 | 22222 | £524.2017420000 | £524.2017420000 | yes |

**And the limit of that evidence is published beside it.** The `only`/`except` legs cut the book by
whether a household's account is on the priced roster, and that roster covers **95.8%** of it — on
2026-09-03, `only` re-drew 341 of 356 households and `except` re-drew 15. `except`'s `selection_gbp`
is the *same number on all three seeds* because the 15 households it varies cancel. **The existing
decomposition machinery is a 96/4 cut, not a decomposition**, and it cannot be read as evidence
that a large non-priced remainder would cancel — no such remainder has ever been measured. That is
why this finding does not claim one.

## Which route, with the arithmetic that chose

| route | what it costs | what it buys |
|---|---|---|
| **more seeds** | 112 more seeds ≈ **142 hours** of guest time | the sign, *if* mean and sd stay put |
| **paired estimator** | nothing | **nothing — the route is SPENT, not cheap** |
| **larger priced book** | pricing **13.4×** the households — 295 → ~3,960 | the sign at the 9 seeds already in hand |

Seeds needed scale as `1/n` in the priced count (mean `n·mu`, sd `sigma·sqrt(n)`, so sems from zero
go as `sqrt(n)`) while seeds cost linearly in what they buy. **A larger priced book is the only
route whose cost does not scale linearly with what it buys** — and that scaling rests on
independence across households, which is an *assumption*: the two priced-book sizes on disk differ
by two accounts, far too little leverage to test it.

**The recommendation is that nobody queues another seed.** Not because 142 hours is unaffordable,
but because the one cheap experiment that would tell us whether the book route works has not been
run: **a three-seed `only` leg at a deliberately halved roster measures the scaling for about a
fortieth of what buying the seeds costs.** Prescribing "draw more seeds" from here is the same
error the item was filed to stop, in its most expensive form.

## Against the prediction filed before the measurement

The item predicted the current-objective price at "about 118". Computed by
`distance_to_a_sign` — the artefact's own function, imported rather than re-spelled — it is
**121** (the prediction used Student's t, the artefact uses a flat 2.0-sem bar). The prediction
stands. The published **24** is an artefact of pooling nine seeds priced under an objective that
charged nothing for a departure with nine priced under one that charges £27.50.

## What I got wrong on the way, and it matters

The first mutation run reported **all six mutations green** — six controls that could not fail. The
flattering reading was "six equivalences". It was a **broken simulation**: the extract I built by
copying `tools/` and symlinking the sibling packages left `/home/rich/synthetic-enterprise` at
`sys.path[0]`, so pytest imported the *real tree's* module and graded an unmutated file. The file
on disk said `"buys": 1.0` while the runtime returned `0.0`.

Re-run in a `git archive` extract, which has no path back, **six of seven mutations fired**. The
seventh — `1.0 - paired/unpaired` → `abs(...)` — was a **missing test**, not an equivalence:
anti-correlated arms make the subtraction *amplify* the spread, and the absolute value would report
that harm as an equal-sized benefit, recommending pairing exactly where it is worst. That control
now exists and fires.

**An extract that shares a path with the tree it is grading is not an extract.** Every mutation
result measured in one is worthless, and it reads exactly like a clean pass.

## Still owed

1. **The published 24.** `site/data/value_arms.json` still carries it. Replacing it is entangled
   with which family the page publishes, and a concurrent seat holds the live claim on that
   decision — so this finding states the honest number and the evidence, and does not race it.
2. **The halved-roster scaling probe** — three seeds, and it decides the only affordable route.
3. Part ONE when `3100001`–`3100012` settle, read as its own twelve-seed family and **not** folded.
