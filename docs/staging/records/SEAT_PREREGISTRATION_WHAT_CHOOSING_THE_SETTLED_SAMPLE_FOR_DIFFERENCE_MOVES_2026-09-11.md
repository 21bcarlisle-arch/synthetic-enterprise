**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
`W2_29_the_coverage_is_re_measured_against_the_demand_vector`

# PRE-REGISTRATION — what choosing the settled sample for difference moves

## THIS FILE HOLDS TWO PRE-REGISTRATIONS OF ONE EXPERIMENT, AND NEITHER IS REVISED

Two lanes pre-registered the same experiment on 2026-09-11, on the two sides of the origin fork,
at the same path. The merge commit carrying this file is the one that closed that fork. Both are
reproduced below **verbatim**, because a pre-registration that is edited after the fork it was
written on is not a pre-registration — and choosing one of the two would have destroyed a filed
prediction while leaving the record looking complete.

They are NOT duplicates. They predict against **different bases**, which is the whole reason both
are worth keeping:

| | §A — the shared tree's side | §B — `origin/main`'s side |
|---|---|---|
| Base | fitted-joint homes (`0d86d6dfe`) | coarse homes; those four fields absent |
| Baseline read | 500 wins / 91 settled / 18.3% / 409 refused | 502 / 90 / 17.96% / 412 |
| P1 band | worst-axis KS ratio **[1.2x, 2.0x]** | **>= 1.25x**, kill below **1.10x** |
| Per-year proportionality | replace with weights that reconstruct it | same, and `customer_years` enters as an axis |

**§B's §0 is answered by the commit that carries this file, and it was answered in §B's own
favour.** §B measured that `0d86d6dfe` was not an ancestor of `origin/main`, filed that as
`SEAT_FINDING_TWENTY_ONE_GATED_COMMITS_NEVER_REACHED_ORIGIN_AND_THE_TREES_HAVE_DIVERGED_2026-09-11.md`,
and wrote: *"If P1 fails on this base and the same measurement passes on the shared tree's `main`,
the honest reading is that the chooser needs the richer home — which would make promoting those 21
commits the higher-value work, and I will say so rather than fit the design to the base I happen to
be on."* This merge **is** that promotion. The fitted-joint fields and the chooser are now on one
base for the first time, so the two-bases caveat that both documents carry has expired, and P1 is
answerable on the richer home exactly as §B asked — without either arm being re-banded after the
fact.

**What is NOT settled by the merge:** neither document's predictions have been graded here. The
merge closed the fork; it did not run the counterfactual arm.

**WHERE THE GRADING IS, added 2026-09-15 because the sentence above was the only thing a reader
met and it points nowhere.** "Not graded *here*" was true of the merge commit and false as the
last word on the subject — the grading was already filed two files away, in this directory, with
no pointer in either direction:

* `SEAT_RESULT_THE_SETTLED_BOOK_IS_CHOSEN_AND_WEIGHTED_2026-09-11.md` — ten predictions, **6 hold
  and 4 fail**. Worst-axis KS 0.12798 culled against 0.08241 chosen (1.553×), 84 settled against
  the cull's 90, per-account inflation 0.057–14.774 against a flat 5.57.
* `SEAT_RESULT_P6_THE_CHOSEN_BOOK_IS_2_45_PERCENT_WORSE_ON_GROSS_MARGIN_2026-09-11.md` — takes the
  one withheld prediction. |Δ| = 2.45%, **sign against the change**.

**IT IS §B THAT WAS GRADED, BY NAME AND BY BAND.** The result's table grades "≥1.25×, kill below
1.10×" and "distinct fabric vectors ≥70", which are §B's bands; §A's P1 band is [1.2×, 2.0×] and
its P2 is about per-year shares. **§A is graded only in substance** — the measured 1.553× falls
inside §A's P1 band, §A's P4 is §B's P7, §A's P5 is §B's P4 — and by coincidence of content rather
than by anything a reader could follow. Recorded rather than repaired: re-grading §A against its
own numbering is real work and is named in
`SEAT_RESULT_THE_SETTLEMENT_SELECTORS_LOSING_MODE_IS_LIVE_AND_ONE_OF_ITS_TWO_ROUTES_HAD_NO_CONTROL_2026-09-15.md`
as what is next.

---

## §A — pre-registration filed on the shared tree's side (fitted-joint homes)

# PRE-REGISTRATION — what choosing the settled sample for difference moves

**Written 2026-09-11, before any arm was run.** Lane 0 delivery, claim
`the-settlement-sample-is-a-count-based-cull-and-the-chooser-earns-1.64x-at-its-size`.

---

## The question

`simulation/net_new_acquisition.plan_growth_campaign` wins ~500 accounts and can settle ~91 of
them. Which 91 is decided today by a **systematic count cull**:

```python
wanted = int((i + 1) * sample_rate) > int(i * sample_rate)
```

Every settled account then stands for the same `1 / sample_rate` (~5.46) accounts, published as one
number (`settlement_sample_rate`, 18.3%) on every row.

**Does choosing those 91 for DIFFERENCE over the demand axes, and carrying a per-account weight,
make the settled book a better stand-in for the campaign's wins than the count cull does?**

## Why it is being asked here and not on the world's stock

Measured 2026-09-10 (`simulation/premise_population.py`, the fitted-stock-joint block): chosen+
weighted beats a random draw on worst KS by **1.68x at N=40, 1.31x at N=400, 1.04x at N=4,400**.
The world's stock is 4,400 — nothing to compress, so the chooser is deliberately NOT wired there.
The settlement sample is 91 of 500. That is the size at which the design earns something.

## What is NOT being changed, stated so a later reader cannot infer otherwise

This is an **engineering artefact**, not a baseline change and not a curriculum act. The campaign
above the sampling pass is untouched: the quotes, the spend, the funnel's verdict on each prospect,
the company's own plan. `SETTLEMENT_CUSTOMER_YEAR_BUDGET` does not move. Nothing the company
decided can see this pass — the two-pass shape is what guarantees it, and it stays.

## Predictions, in order, before the first arm runs

**P1 — the count cull is NOT a random draw, so the 1.64x will not be reproduced.** The cull is
systematic on a year-ordered list, which is implicit stratification by year. It is therefore
already better than random on every axis correlated with acquisition year, and no better than
random on the within-year axes. I predict the chosen+weighted arm improves worst-axis KS against
all campaign wins by a factor in **[1.2x, 2.0x]**, and I predict the *gain is concentrated on the
fabric axes* (floor area, heat-loss coefficient, remaining insulation ceiling) rather than on cost.

**P2 — a pure difference-chooser will DEGRADE the per-year proportionality, and this is the thing
most likely to make the change not worth having.** The cull's one real virtue is that each year's
booked wins are proportional to that year's funnel wins, so `booked / rate` estimates any year
without bias. Cluster medoids over a fabric space have no reason to respect year at all. I predict
unweighted per-year shares move by more than 5 percentage points on at least one year. **The
per-account weights must reconstruct the per-year proportionality; if they cannot, the change is
refused.** That is the acceptance test, and it is written here before the number is known.

**P3 — the settled account count changes, so every published financial figure moves.** Today: 582
commercial, 173 settled, 91 of 500 wins settled, 409 refused. The chooser returns medoids plus axis
extremes plus per-fuel extremes, so its k is not exactly the cull's count and the customer-year
guard binds on a different set. **I do not predict the sign of the company's P&L move**, and
nothing in the implementation may be adjusted in response to it.

**P4 — the null case stays byte-identical.** When `campaign_cy <= headroom_cy` the whole pass is a
no-op today: nothing refused, no sample, no note. The chooser must not run at all in that case. A
run at 13 founders must be byte-identical to HEAD. This is the leg that shows the change is aimed
at the artefact and not at the answer.

**P5 — the hard budget guard still binds and is still the invariant.** Selection is by design;
the budget is in customer-years. The settled set may never exceed `customer_year_budget`, however
the members were chosen. If the chooser's set is dearer than the cull's, fewer accounts settle, and
that is the correct outcome rather than a bug.

## What would refute the change

- P2 fails and the weights cannot reconstruct per-year proportionality → **refused**, and the
  finding is that the count cull's stratification was the load-bearing property all along.
- The chosen+weighted arm's worst-axis KS is **not better** than the cull's → refused; the cull
  was already doing the job and the 1.64x did not transfer to this population.
- The demand vector computable for a *candidate* turns out to carry no more information than
  property type already carries → the premise of the whole item is wrong and that is the finding.

## How it is measured — one variable, one HEAD

The campaign is run **once**. Its candidate list `(year, prospect, in_market, customer_years)` is
captured and both selection rules are applied to that same fixed list. The campaign above the pass
is deterministic and identical in both arms by construction, so the only variable is the selection
rule. Running the campaign twice would put the seed stream in the comparison.

## Stated in advance: which of the two the change keeps

The instruction allows either "keep the per-year proportionality or replace it with per-account
weights that reconstruct it, and say which". **The intent is to replace it with per-account
weights that reconstruct it**, because a single global inflation factor is exactly the defect —
18.3% inflates the settled book to the commercial one with one number for every account. With
per-account weights the inflation is per account and arguable. If P2 refutes that, the fallback is
to keep the year stratification and choose for difference WITHIN each year, and that fallback is
named here so choosing it later is not a result fitted to the answer.

---

## §B — pre-registration filed on `origin/main`'s side (coarse homes)

# PRE-REGISTRATION — what choosing the settled sample for difference moves, and the one number that could kill it

**Filed 2026-09-11, delivery seat, BEFORE the chooser is wired into `net_new_acquisition` and
BEFORE any counterfactual arm is run.** The baseline arm in §2 was run first and is a READING of
what is already on disk, not a test of the change; every number in §4 is a prediction whose answer
I do not have.

Drawn item: *"the settlement sample is a count-based cull and the chooser earns 1.64x at its size"*.

---

## 0. THE PREMISE OF THE DRAWN ITEM IS NOT ON THE BASE I CAN LAND ON, and this is the first finding

The item says the chooser "has something real to choose over ... it did not before `0d86d6dfe`".
`0d86d6dfe` **is not an ancestor of `origin/main`**. Measured in this worktree, 2026-09-11:

```
git rev-parse HEAD origin/main main
  cf16f724e…  (HEAD == origin/main)
  6f5f1d3f4…  (the shared tree's `main`)
git rev-list --count main..HEAD   →  25
git rev-list --count HEAD..main   →  21
```

The shared tree's `main` and `origin/main` have **diverged**: the shared tree holds 21 gated
commits that were never promoted (`0d86d6dfe` among them, and with it `Household.floor_area_band`,
`has_loft_insulation`, `has_cavity_wall_insulation`, `has_mains_gas_supply` and the NEED-fitted
draw), while `origin` moved 25 commits past their common base. `simulation/household.py` at
`origin/main` carries **none** of those four fields. This is not the "tree is behind origin" shape —
it is both at once, and no worktree cut from `origin/main` (which is every worktree the promotion
route can serve) can see that lane's landed work.

**This is filed as its own finding** — `SEAT_FINDING_TWENTY_ONE_GATED_COMMITS_NEVER_REACHED_ORIGIN_
AND_THE_TREES_HAVE_DIVERGED_2026-09-11.md`. It is recorded here because it changes what this
pre-registration can honestly claim.

**AND THE ITEM'S "it did not before `0d86d6dfe`" IS TOO STRONG, by that commit's own correction.**
`0d86d6dfe`'s message corrects the claim it inherited: *"the first version of this comment said the
demand vector was UNMEASURABLE… Wrong: `fabric_physics.floor_area_m2` derives one from property
type and bedroom count and the axes always evaluated."* So on `origin/main` the fabric vector
**does** evaluate for every drawn home; it is *coarser*, not absent. The drawn item's WHY inherited
the uncorrected sentence.

**So this build is keyed to what a household actually carries, not to whether one commit landed.**
The feature matrix is read off `fabric_physics.fabric_parameters(household)`, which is defined on
both bases. On `origin/main` it resolves the coarse home; when the 21 commits reach `origin` the
same code resolves the fitted-joint home with no edit. That is the only design that is correct on
both, and it is why no `floor_area_band` is named anywhere in the change.

**Consequently the 1.64× in the item's WHY is NOT this build's expected number and is not used as
one.** It was measured on a 20,000-point *generated* population with the fitted-joint attributes.
This build is measured on `origin/main`'s own candidates, and §4 predicts against that.

## 1. What is being built

Replace the systematic 1-in-*N* count cull in `net_new_acquisition`'s sampling pass with a sample
**chosen for difference over the demand axes and carrying a per-account weight**.

* **The candidates** are unchanged: every funnel win, `(year, prospect, in_market, customer_years)`.
* **The feature matrix** is `fabric_physics.fabric_parameters(prospect.premise.household)` —
  fabric W/K, raw infiltration ACH, volume m³, solar aperture m², internal gain kW — **plus
  `customer_years`**, which is the campaign's own time axis (see §3).
* **The choosing** is `tools.demand_vector_coverage.choose_for_difference`: cluster medoids, one
  per distinct region of behaviour, plus every axis extreme, plus the extremes **within each fuel**,
  with fuel taken from `DrawnPremise.commodity`.
* **The weighting** is `fit_weights`: non-negative least squares against the candidate population's
  own CDF, so each settled account carries the mass of commercial wins it stands for.
* **The budget stays the invariant.** `SETTLEMENT_CUSTOMER_YEAR_BUDGET` is in customer-years and the
  chooser selects by count, so `k` is found by bisection: the largest `k` whose chosen set costs
  ≤ the headroom. The hard per-account guard is kept unchanged underneath it.
* **Fail closed:** if any candidate has no household to place in the vector, the whole campaign
  falls back to the systematic cull and **says so in `notes`**. A partly-chosen, partly-culled
  sample would be a third population nobody named.

## 2. The baseline arm, read before the change (seed 42, `origin/main` @ `cf16f724e`)

```
opening book 83 · funnel wins 502 · settled 90 · refused 412
settlement_sample_rate 0.1796 · customer-years 1195.4 of 1200.0 (all wins would cost 2386.4)
distinct fabric vectors among the 90 settled winners: 47
```

Per year the cull is exactly proportional by construction (4/24, 6/35, 8/45, 13/70, 13/72, 10/59,
4/20, 10/56, 15/83, 7/38).

**Note the numbers are not the item's.** The item quotes 500 wins / 91 settled / 18.3% / 409
refused; those are the *shared tree's* figures, taken with the fitted-joint homes. On the base this
turn can promote to, the same run gives 502 / 90 / 17.96% / 412. Quoting the item's figures as this
build's baseline would have been the two-bases-differenced error.

**47 distinct vectors among 90 settled accounts is the number that makes this design's value an
open question here.** Half the settled book is already a duplicate of another row of it — which is
what the chooser exists to fix — but a coarse population also caps how much difference there is to
find, and `choose_for_difference` explicitly refuses to draw two near-identical households.

## 3. Per-year proportionality: REPLACED, not kept, and the replacement is measurable

The instruction allows either. **I am replacing it.** A sample chosen for difference cannot also be
proportional by count — the two criteria are opposed in exactly the way the demand-vector canon
says span and reproduce are opposed — so keeping the per-year count proportional would mean culling
inside each year, which reintroduces the count rule this change exists to remove.

Instead **`customer_years` enters the fit as an axis**, so the *weighted* sample reconstructs the
year composition: each year's summed weight estimates that year's funnel wins. `customer_years` is
a strictly decreasing function of the in-market date within the campaign, so matching its CDF is
matching the campaign's time marginal. This makes proportionality a **fitted property that can be
measured and can fail** (P3), where today it is a property of the arithmetic that cannot.

**And it is what makes the inflation arguable.** Today one number, `1/0.1796`, multiplies every
settled account by 5.57 to read the commercial book. After this change each account carries its own
mass, so the inflation is per account — and a reader can disagree with one account's weight, which
they cannot do with a scalar.

## 4. The predictions, in bands, decided before the counterfactual is run

Both arms at **one HEAD, one variable**, seed 42, driven from outside the tree.

**P1 — THE ONE THAT CAN KILL THE BUILD.** Worst-axis weighted KS of the chosen+weighted settled
book against the full 502-candidate population, versus the systematic cull's KS against the same
population: **ratio ≥ 1.25×**. If it comes in **below 1.10×** the design does not earn its keep on
this base's homes and I will *not* wire it — I will land the measurement and the refusal, the same
shape as `0d86d6dfe`'s own refusal at 1.04×. I am deliberately banding this well below the item's
1.64×, because that figure was taken on a population with four attributes this base does not have.

**P2 — the settled book stops repeating itself.** Distinct fabric vectors among the settled
accounts rises from **47** to **≥ 70** (of ~90). Medoids are one per region by construction, so a
large residue of duplicates would mean the clustering is not separating this population.

**P3 — the weights reconstruct the year composition.** For every one of the ten years, the summed
weight of that year's settled accounts lands within **±25%** of that year's funnel wins, and the
campaign total lands within **±2%** of 502. If any single year misses by more than 25% the fit is
not carrying the time axis and §3's claim is false as written.

**P4 — the budget stays the invariant and the count barely moves.** Settled accounts land in
**80–100** (baseline 90) and committed customer-years **never exceed 1200.0**. The chooser is free
to pick dearer or cheaper cohorts, so the count may move; the ceiling may not.

**P5 — the inflation stops being one number.** The ratio of the largest per-account weight to the
smallest **non-zero** per-account weight is **≥ 3.0**. Below that, per-account weighting is a scalar
wearing a vector's clothes and §3's argument for it is weak.

**P6 — the P&L moves, and I cannot predict the sign.** The settled book's total gross margin moves
by **more than 1.0%** in absolute terms against the baseline. Direction not predicted: the chooser
deliberately pulls in tails, and whether this world's tails are dearer or cheaper to serve than its
bulk is the thing being measured. *Recording that `0d86d6dfe` predicted the same band and got
−0.37% — I am predicting a larger move here because that change moved which homes exist, and this
one moves which homes are on the BOOK, which is the composition every financial figure sums over.*

**P7 — the null case stays byte-identical.** With a budget the campaign fits inside
(`sample_rate == 1.0` today), the chosen path must not run at all: same winners, same order, no
weights note, no refusals. A change aimed at the artefact must be invisible when the artefact is
absent.

## 5. What this pre-registration does NOT claim

* It does not claim the 1.64× reproduces here. §0.
* It does not claim the fitted-joint homes are unnecessary. If P1 fails on this base and the same
  measurement passes on the shared tree's `main`, the honest reading is that the chooser needs the
  richer home — which would make promoting those 21 commits the higher-value work, and I will say
  so rather than fit the design to the base I happen to be on.
* It does not touch `simulation/premise_population.py` or the world's stock. `0d86d6dfe` refused
  the chooser *there* at 1.04× and that refusal stands; this is the settled book, at N≈90, which is
  the size the item correctly identifies as where compression can earn something.
