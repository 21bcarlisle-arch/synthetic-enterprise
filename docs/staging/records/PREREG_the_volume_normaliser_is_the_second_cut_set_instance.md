**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_13`

# PRE-REGISTRATION — is `volume_factor_normaliser` the second instance of the cut-set class?

**This document is the RECORD: the predictions, and what happened to them. It owes nothing.**

**Written 2026-09-23, BEFORE any of the measurements below were run.**
Claim id: `the-daytime-cuts-joint-is-unpublished-and-two-more-response-scales-may-have-single-centres`

## The class, stated before looking

From the daytime repair (`PREREG_the_property_record_composition_fields.md`, same day):

> Any index whose NUMERATOR is assembled from a **variable** number of terms and whose
> DENOMINATOR is a **fixed** constant is aggregate-neutral only for the one cut-set the
> denominator was computed on. Nothing in the code says so, and it stays harmless for exactly as
> long as every caller supplies that cut-set.

`demand_model._reference_daytime_rate` was instance one: a single constant across cut-sets whose
population means are 0.470 and 0.443, measured at a 4.1% silent cut to the live book's daytime
demand the first time a caller supplied more than the size cut.

The candidate for instance two is `demand_model.volume_factor_normaliser(commodity)`:
`functools.lru_cache`d on **commodity alone**, computed as the share-weighted mean of
`need_volume_index(n, commodity)` over `HOUSEHOLD_SIZE_POPULATION_SHARE` — i.e. at
`children_count=0`, every person read as an adult. The factor it normalises,
`occupancy_volume_factor`, takes `children_count` and a per-household `child_weight` draw, so its
numerator is `adults + w·children` — **a variable number of terms against a fixed denominator.**

## Predictions, in order, each falsifiable

**P1 (tree).** On the live book (`simulation.live_population.live_population()`), the record
count is 144 and `children_count` is present-and-zero on all 144 — `dwelling_records`
sets `DEFAULT_CHILDREN_COUNT = 0` under a stated R10 gap. So no production caller supplies the
children cut today, and the defect is latent rather than live. *(This is the draw's own claim
about the tree, which is an un-re-asked prediction until I run it. I predict the daytime
defect's shape repeats: 0 of 144.)*

**P2 (the second path exists).** `premise_trace.behaviour_profile_for` DOES draw a
`children_count` for itself, uncited, `randint(0, people_count-1)` for households of 3+. So one
home has two answers for children exactly as it did for pensioner/employment — and that field is
the next one along the delegation `composition_cuts_for` just built. I predict wiring it is
already reachable: `build_demand_shape` reads `property["children_count"]` and passes it straight
into `occupancy_volume_factor`, so there is no further plumbing between that draw and the defect.

**P3 (the class — the strong prediction).** Feeding the live book's people counts with a
non-zero children composition, against today's single normaliser, puts the population mean volume
factor **below 1.0**, and I predict **below 0.98** — i.e. it breaks
`volume_factor_is_unbiased` at its own tol of 0.02. Direction is forced (`w < 1`, so children
lower adult-equivalents, and the NEED curve is increasing); the magnitude is not. If it lands
inside 0.98–1.0 the class is confirmed but the instance is below its own control's tolerance and
that is a different, weaker finding — which I would report as such.

**P4 (knowledge).** There is **no** published anchor in this repository for the distribution of
dependent children WITHIN a household size. R10 GAP (a) in `dwelling_records` names exactly this
absence ("no anchor for how many children a household of a given size contains") and the W2_13
market-research file flags it as `R10-DISTRIBUTION-CANDIDATE`. I predict I find no table that
closes it, and therefore that **the children-cut reference cannot be computed from published
evidence today**. If that holds, the honest repair is a normaliser keyed on its cut-set whose
children-cut branch **refuses with a named reason** rather than returning a plausible number —
an honest `None` beats an invented centre.

**P5 (the size-only answer does not move).** Whatever the repair, `volume_factor_normaliser`
for the size-only cut-set returns the same float it returns today, and every existing size-only
caller is byte-identical. This is what makes the repair safe to land under the legacy path, and
it is what made instance one safe.

**P6 (is there a third?).** The draw says "two more response scales may have single centres". I
predict at least one FURTHER fixed centre in the same family that is NOT an instance — a
denominator that is legitimately fixed because its numerator has a fixed term count — and I
predict `premise_trace`'s `appliance_intensity = (people_count / 2.4) ** 0.6` is that non-instance
(persons over mean persons: one term either side). Naming a non-instance is the point; a class
that matches everything catches nothing.

## What "done" means for this item

No exit test was written for it, so: **done is that `volume_factor_normaliser` can no longer be
read as mean-1 for a cut-set it was not computed on** — either it is centred per cut-set, or it
refuses that cut-set by name. Concretely:

1. The normaliser takes its cut-set, not just the commodity.
2. The children cut-set gets its own centre if one is anchorable, and a NAMED REFUSAL if not.
3. `occupancy_volume_factor` and `build_demand_shape` carry that refusal to their callers rather
   than silently under-levelling.
4. A control that can fail: the mutation that reverts the normaliser to a single constant turns
   the control red, and the control is keyed to the PROPERTY (mean-1 per cut-set), not to
   today's float.
5. The size-only path is unchanged to the float (P5), proven by a test that pins it.

## Results, against the predictions above

Run 2026-09-23, after the file above was written and before any code changed.

| | prediction | observed | verdict |
|---|---|---|---|
| **P1** | 144 records, `children_count` present-and-zero on all | **144**, `{0: 144}` | **HELD** |
| **P2** | `premise_trace` draws children itself; no plumbing in between | draws `randint(0, n−1)` for 3+; `build_demand_shape` reads the field straight into the factor | **HELD** |
| **P3** | children-wired book mean **below 0.98**, breaking the control | **0.98458** elec / **0.98678** gas — control **GREEN** | **REFUTED (magnitude)** |
| **P4** | no anchor for children-within-size; the centre is not computable | none found; R10 GAP (a) population half | **HELD** |
| **P5** | size-only float byte-identical | `1.4456452584044155` / `1.2512721741165458`, unchanged | **HELD** |
| **P6** | a fixed centre that is NOT an instance | `(people_count / 2.4) ** 0.6` — persons over mean persons | **HELD** (and a second found) |

**P3 is the prediction that mattered and I got it wrong in the direction that matters.** I
predicted the defect would break its own control. It does not: the measured cut is **1.54%**
(electricity) and **1.32%** (gas) against a `VOLUME_FACTOR_BIAS_TOL` of **2%**. So
`volume_factor_is_unbiased` returns True on a book that is being silently cut — the R15 control
written for exactly this class of defect cannot see this instance of it.

That refutation changed the repair. For instance one, recentring was enough because the control
caught the un-recentred state. Here a band cannot be the mechanism, and widening or narrowing the
band is not available either: **a tolerance chosen before a defect was measured is not evidence
about that defect**, and tuning it to 0.01 so this instance trips would be keying a control to
today's answer. The mechanism is therefore a NAMED REFUSAL at the one function that makes the
aggregate claim, plus an identity control at 1e-12 over the reference population — where
neutrality is an identity, not an estimate, and so has no business being asserted at a tolerance
wide enough to hide the defect.

**And the class is confirmed with a sharper statement than the draw gave it.** The draw said the
class is "variable numerator, fixed denominator". True, but incomplete: what made instance one
expensive was that its control caught it, and what makes instance two dangerous is that its
control does not. **The class is not "a fixed centre"; it is "a neutrality claim whose cut-set is
implicit", and the control over such a claim must be keyed to the reference population, not to a
book.** A book is a sample and its deviation has somewhere to hide.

**P6, the non-instances, and why naming them was worth the line.** `(people_count / 2.4) ** 0.6`
in `premise_trace.behaviour_profile_for` and `household_physical_layer._profile_from`, and
`_DHW_REFERENCE_OCCUPANCY = 2.4` in `cooking_daily_kwh`, are all fixed centres against a headcount
— and all three are fed **total persons** against a **mean-persons** centre. One term either
side, cut-set closed, not instances. They would become instances the moment a caller passed
`BehaviourProfile.adult_count` (which exists, one dataclass away) instead of `people_count`;
checked, and no caller does. A class that matches every ratio catches nothing, so the boundary is
part of the finding.

## What was delivered against "done"

1. ✅ `volume_factor_normaliser(commodity, children_reference=None)` takes its cut-set.
2. ✅ The children cut-set gets its own centre from a supplied reference, and
   `CHILDREN_WITHIN_SIZE_REFERENCE` is an explicit `None` with the R10 GAP (a) reason written at
   it — not a plausible default.
3. ✅ `population_mean_volume_factor` / `volume_factor_is_unbiased` RAISE
   `UnanchoredReferencePopulation` on a children book with no reference, naming the measured 1.5%
   and the fact that the band cannot see it. `occupancy_volume_factor` still answers for a single
   household, because its RELATIVE claim is sound and only its LEVEL claim was not — the two were
   conflated in one docstring sentence and are now separated.
4. ✅ Three mutations run and all three fire: children branch reverted to the all-adult centre (6
   reds); refusal deleted (1 red, the partition control); refusal made to fire on everything (8
   reds). The last is the one that matters — a guard that refuses everything passes every
   per-branch test, and one control over the whole partition is what catches it.
5. ✅ Size-only path pinned byte-identical.

## What is left, and it is a research task not a build task

**`CHILDREN_WITHIN_SIZE_REFERENCE` is owed a sourced distribution.** Until it has one, no lane can
honestly wire `dwelling_records.DEFAULT_CHILDREN_COUNT` to `premise_trace`'s own children draw —
the delegation that `composition_cuts_for` performed for pensioner/employment cannot be performed
for this field, because that draw (`randint(0, people_count − 1)`, uniform, uncited) is not a
reference population either, and centring on it would be normalising a gap against itself. The
named lead is the one the W2_13 research pass already filed as `R10-DISTRIBUTION-CANDIDATE`; ONS
Census 2021 household-composition tables are the obvious place and were not fetched here. The
refusal is what stops that wiring landing silently in the meantime, and a refusal that names its
reason is how it gets corrected.
