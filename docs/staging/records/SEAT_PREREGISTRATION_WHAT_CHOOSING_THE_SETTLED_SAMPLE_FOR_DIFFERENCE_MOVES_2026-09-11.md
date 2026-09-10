**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
`W2_29_the_coverage_is_re_measured_against_the_demand_vector`

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
