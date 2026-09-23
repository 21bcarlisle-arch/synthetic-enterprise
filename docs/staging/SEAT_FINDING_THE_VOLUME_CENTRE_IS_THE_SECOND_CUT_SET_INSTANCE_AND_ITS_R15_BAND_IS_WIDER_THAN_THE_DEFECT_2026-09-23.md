**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_13`

# The volume centre is the second cut-set instance — and its R15 band is wider than the defect

Claim id: `the-daytime-cuts-joint-is-unpublished-and-two-more-response-scales-may-have-single-centres`
Pre-registration (predictions written before the measurements):
`docs/staging/records/PREREG_the_volume_normaliser_is_the_second_cut_set_instance.md`

## The finding, in one paragraph

`simulation.demand_model.volume_factor_normaliser` was the second instance of the class the
daytime reference repair uncovered the same day: an index whose numerator is assembled from a
**variable** number of terms (`adults + w·children`) against a denominator computed on **one**
cut-set (households read as all adults, `lru_cache`d on commodity alone). Confirmed by
measurement: on the live 144-home book with the children `premise_trace` already draws for
itself, the population mean volume factor is **0.98458** (electricity) and **0.98678** (gas) —
a silent **1.5% / 1.3% cut to the whole book's volume**, latent today because
`dwelling_records.DEFAULT_CHILDREN_COUNT` is 0 on all 144 records, and live the moment anyone
wires that field. It is repaired and landed: the centre is now per cut-set, the size-only float is
byte-identical, and the children cut-set without a reference population is **refused by name**.

## The part that is not a repeat, and is why this is filed BLOCKING

**The R15 control written for exactly this class could not see this instance.**
`volume_factor_is_unbiased` compares the book's mean factor against 1.0 with
`VOLUME_FACTOR_BIAS_TOL = 0.02`. The defect is 0.0154. **The control returns True on a book that
is being cut.** I pre-registered "below 0.98, the control fires" and that prediction is REFUTED —
the measurement said the control stays green, and the refutation is worth more than the
confirmation would have been.

For the daytime instance a band was sufficient because the defect (4.1%) happened to exceed it.
That was luck, not design: nothing chose 0.02 with any defect in view. So the general lesson is
not "recentre per cut-set" — it is:

> **A neutrality claim must be controlled against its REFERENCE POPULATION, where neutrality is
> an identity and can be asserted to 1e-12, not against a BOOK, where it is an estimate and any
> tolerance wide enough to accommodate sampling is also wide enough to hide a re-levelling.**

The repair carries both: the identity control at 1e-12 over the reference, and the band retained
for books — with a control asserting *the relation* that the defect fits inside the band, so
tightening the band below the defect is what turns it red rather than a pinned 0.9846 that would
rot the day the book changes.

## What landed

- `volume_factor_normaliser(commodity, children_reference=None)` — cut-set keyed. `None` returns
  the exact float it always returned (`1.4456452584044155` / `1.2512721741165458`).
- `CHILDREN_WITHIN_SIZE_REFERENCE = None` — R10 GAP (a)'s **population half**, declared absent
  with its reason at the constant rather than filled with a plausible number. Assign a sourced
  distribution there and every children-cut centre becomes computable with no other edit.
- `UnanchoredReferencePopulation`, raised by `population_mean_volume_factor` and
  `volume_factor_is_unbiased` when a book declares children and no reference exists. Refusing —
  not returning False: False reads as "the response is biased", and the true statement is "you
  asked a question whose centre does not exist".
- `occupancy_volume_factor` still answers for one household. Its RELATIVE claim was always sound;
  only its LEVEL claim was not, and the two sat in one docstring sentence. They are separated.
- Six controls, three mutations run: children branch reverted to the all-adult centre (6 reds),
  refusal deleted (1 red), refusal made to fire on everything (8 reds). The last is the one that
  matters — a guard that refuses everything passes every per-branch test.
- A pointer at `dwelling_records.DEFAULT_CHILDREN_COUNT`: wiring that field owes a reference
  population, which is not discoverable from the field itself.

## What this BLOCKS, and on what

**No lane may wire `DEFAULT_CHILDREN_COUNT` to `premise_trace`'s children draw until
`CHILDREN_WITHIN_SIZE_REFERENCE` has a source.** That delegation is the obvious next step — it is
literally the next field along from the pensioner/employment one that landed hours earlier — and
it is the wrong move today for a reason the field does not advertise: `premise_trace`'s draw is
`randint(0, people_count − 1)`, uniform and uncited, so centring the response on it would be
normalising a gap against itself. The refusal is what stops that landing silently. The research
lead is already filed as `R10-DISTRIBUTION-CANDIDATE` in
`docs/market_research/occupancy_consumption_volume_shape_w2_13.md`; ONS Census 2021
household-composition tables are the obvious source and were not fetched here.

## Where the class stops

Three further fixed centres were checked and are NOT instances: `(people_count / 2.4) ** 0.6` in
`premise_trace.behaviour_profile_for` and `household_physical_layer._profile_from`, and
`_DHW_REFERENCE_OCCUPANCY = 2.4` in `premise_trace.cooking_daily_kwh`. All three take **total
persons** against a **mean-persons** centre — one term either side, cut-set closed. They become
instances the moment a caller passes `BehaviourProfile.adult_count`, which exists one dataclass
away; no caller does today. Naming the boundary is part of the finding: a class that matches
every ratio catches nothing.
