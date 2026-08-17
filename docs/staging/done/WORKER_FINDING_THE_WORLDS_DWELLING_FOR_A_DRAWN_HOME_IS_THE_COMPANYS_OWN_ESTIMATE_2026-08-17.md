# The world's dwelling for a drawn home is the company's own estimate

**Severity:** BLOCKING · **Lane:** W4_the_wall

**Found:** 2026-08-17, during KNIFE pass 3 step 30 (`KNIFE3_wall_crossing_paydown`, register §3y)
**Class:** B2/B3 inversion — a company BELIEF constituting a world FACT
**Disposition:** REPAIRED 2026-08-17 (KNIFE3 step 31, register §3z) — see the discharge section below
**Discharged:** `tests/simulation/test_the_worlds_dwelling_is_drawn_not_believed.py::test_mutating_the_suppliers_modal_band_does_not_move_the_worlds_dwelling`, `tests/simulation/test_the_worlds_dwelling_is_drawn_not_believed.py::test_the_companys_guess_about_a_drawn_home_is_wrong_at_the_published_rate`, `simulation/premise_population.py` — the world now DRAWS a drawn home's dwelling from the published EHS band marginal, so the company's modal-band guess is right at the published prevalence (0.426) instead of by construction (100%)

BLOCKING because a scored accuracy figure is right by construction, and the population it is right
about is the one that grows.

**On class consolidation:** by title this is `measurements_that_mirror`, whose lane is `H_harness`,
so `background/finding_classes.py` will refuse it out of lane and leave it uncounted in that class
document. That refusal is the mechanism working, not a defect to route around — the lane above is
where the defect lives, and the identical-shape precedent
(`WORKER_FINDING_THE_WORLDS_CONTACT_RATE_IS_THE_COMPANYS_ESTIMATE_2026-08-11`) is filed the same way.
The lane was not set to `H_harness` to make a counter tick.

Found by KNIFE3 step 30 while re-ruling the wall crossing
`simulation.run_phase2b -> saas.property_model` (`docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md`
§3y). Filed rather than fixed on sight, per SELF_INTERRUPT_DISCIPLINE: it outlives the wall row that
surfaced it, because it would still be true if the wall did not exist.

## The finding

`saas/property_model.py::build_properties()` builds the world's GROUND TRUTH dwelling record for each
resi electricity customer. For a customer the roster authored (C1–C9) it reads the authored
`home_type` / `epc_rating` / `bedrooms`. For a DRAWN customer (`SYN-*`) — one the live population
draw created — there is no authored dwelling, so it calls `_derive_syn_property_fields()`.

That function's own docstring says what it returns:

> Reads only the OBSERVABLE `consumption_band`; returns **saas-side approximations**

So the world's ground truth about a drawn household's home is the SUPPLIER'S APPROXIMATION of that
home. This is the belief-is-truth inversion `B2_company_brain_decides_the_world` names for churn,
applied to dwelling physics.

## The measurement

The company's zero-knowledge fallback lives in `company/crm/property_discovery.py`:

```
DEFAULT_EPC_RATING = EPCRating.D          # UK modal EPC band (Ofgem/EPC register distribution)
DEFAULT_ASSUMPTION_CONFIDENCE = 0.1
```

The world's constant lives in `saas/property_model.py`:

```
_SYN_MODAL_EPC_RATING = "D"               # UK domestic modal EPC band; honest population default
```

Two comments, each independently justifying "the UK modal band". One constant. Measured against the
live population on 2026-08-17:

| cohort | the company's confidence-0.10 default EPC is correct for |
|---|---|
| DRAWN (`SYN-*`) | **2/2 — 100%** |
| AUTHORED (C1–C9) | **3/7 — 43%** |

43% is what a population prior looks like when it is guessing. 100% is what it looks like when it is
reading its own answer back — and it cannot be anything else, because the same literal produced both
sides. `property_type` has the identical shape (`PropertyType.SEMI_DETACHED` against `"semi"`).

`property_discovery.py`'s module docstring states the intent this defeats:

> A belief built this way MAY diverge from the customer's actual home; **that imperfection is the
> point.**

For the drawn cohort there is no imperfection, and there cannot be one.

## Why it is BLOCKING rather than RECORDED

Two reasons, and the second is the one that matters.

1. The company's dwelling belief feeds EPC-band consumption multipliers, ASHP uplift and the
   demand-shape adjustment through `HouseholdDemandRegister` / `epc_multiplier` in
   `simulation/run_phase2b.py`. Any harness figure scoring the supplier's property belief against the
   world's is scoring a copy against its original.
2. **The drawn cohort is the half that GROWS.** The book scales by drawing, not by authoring — today
   it is 2 of 9 resi elec, and every future customer arrives that way. So the supplier's measured
   dwelling accuracy climbs toward 100% as the book grows, for no reason connected to the supplier
   getting better at anything. A metric that improves with book size and not with skill is the
   R12 anti-goal-seek shape arriving through the back door.

Zero callers today would set the FIGURE trigger, not the CONTROL trigger — but there is a live
consumer, so both fire.

## What the fix is NOT

Duplicating the constant so each side owns its own copy (B3's move) kills the wall crossing and
leaves this defect intact, now sourced from a literal on each side, reading as two independent
sources that agree. That is strictly worse than today, because today the shared lineage is visible in
a single call.

## What the fix is

The world needs its own dwelling draw from a real external distribution — an EPC-band and
dwelling-type distribution with a named published source, held as a literal in the style
`HOUSEHOLD_SIZE_SHARE_ONS_TS017` already sets in this same module. **That anchor is not in the tree
and must not be invented**: fabricating a band distribution to unblock the work is the R13 breach
(baseline changes for fidelity reasons, against a real source). So the first step is a DISCOVER pass
for the real distribution, not a build.

Tracked as the DISCOVER half of `B12_the_dwelling_is_the_worlds_and_the_company_only_discovers_it`
in the wall-crossing register; that block also holds the constraint that the BUILD half must not land
without it.

## Falsifier

A test that mutates `_SYN_MODAL_EPC_RATING` (or the company's `DEFAULT_EPC_RATING`) and asserts the
OTHER side does not move. It is red today for every drawn customer, in both directions. Note the
mutation must be run against the drawn cohort specifically — on the authored cohort it already
passes, which is exactly how this survived.

---

## DISCHARGED 2026-08-17 (KNIFE3 step 31, register §3z) — REPAIRED, and one premise of this
## finding was FALSE

**The world now draws the dwelling.** `simulation.population_draw.SyntheticCustomer` carries a
`premise` — the world's property type, build era, EPC band, bedrooms and heating for that drawn home,
drawn by `simulation.premise_population.draw_premise()` from the published England housing-stock
joint. It is HIDDEN SIM TRUTH on the same footing as `cohort`: `to_customer_dict()` does not emit it,
so the repair did not trade a mirror for a leak
(`test_the_drawn_customer_dict_still_carries_no_dwelling`).

**"That anchor is not in the tree and must not be invented" was WRONG, and that is the finding's own
error.** `simulation/premise_population.py:190` has held `PUBLISHED_EPC_BAND_SHARE` with
`EPC_BAND_SOURCE = "EHS 2022-23 Energy Chapter AT1_2 (MHCLG, July 2024)"` since C14's population
half — raked onto the published property-type and build-era marginals and checked against an ONS
conditional that was not a raking target. The DISCOVER pass this finding filed as its first step was
therefore not needed: the anchor was three files away, in the world layer, with a named publisher.
Its own module docstring even names this defect ("`SyntheticCustomer` carries no `home_type`,
`epc_rating` or `bedrooms`, so `simulation.household.make_household` defaults every draw to the same
`suburban_semi` — a population of clones"), so the two halves of the repair were sitting on either
side of an unwired seam. **Lesson, generalised beyond this instance: a finding that says an anchor
must be discovered has to name the search it did. This one did not, and the search was one grep.**

**The measured mirror is gone.** On the live activated book the two drawn homes are now a post-2000
terraced band C (4 bed) and a pre-1919 semi band F (2 bed), so the company's confidence-0.10 default
(`D`) is correct **0/2** on the drawn cohort where it was 2/2, against an unchanged 3/7 on the
authored one. On a cohort large enough to have a rate (λ=300/yr), the same guess is right at the
PUBLISHED prevalence of band D — 0.426 — and its `SEMI_DETACHED` property-type guess at the published
semi share, both judged to 3.5 binomial SD.

**Both live dwelling consumers were repaired, not just the one this finding named.** The record
(`saas.property_model.build_properties`, now taking `dwellings=`) AND the household register
(`HouseholdDemandRegister` → `build_household_register` → `make_household(customer, drawn=...)`,
which was independently defaulting every drawn home to `suburban_semi`/`"D"` — a THIRD copy of the
same literal). Fixing only the record would have left the world holding two different homes for one
customer.

**The fallback is labelled, not deleted.** Every property record now carries `dwelling_basis` —
`authored_roster` / `world_draw` / `saas_approximation`. The R10 drawn-shape class guard requires
`build_properties` to cope with a bare drawn record, so the supplier's approximation still answers
when no world dwelling is supplied; what it can no longer do is pass as ground truth silently.
`test_every_live_consumer_asks_the_world_for_the_dwelling` walks the AST of every non-test call site
and fails if a new consumer omits the world's dwelling.

**Controls:** `tests/simulation/test_the_worlds_dwelling_is_drawn_not_believed.py`, 11 tests, both
mutation directions plus the vacuity guard that proves the mutation is reachable
(`test_the_suppliers_modal_band_is_still_reachable_without_the_worlds_dwelling`).

**What this did NOT do:** the wall crossing `simulation.run_phase2b -> saas.property_model` is
STILL OWED and still uncut — 8 live crossings, unchanged, per
`python3 -m tools.wall_crossing_dispositions` on the working tree. The defect that made the crossing
matter is repaired; the module is still misfiled and still immovable (four company-side importers,
per §3y's re-measurement). Booking the edge on the strength of this repair is exactly the
false-completion class B12's block exists to prevent.

**Owed, named rather than dropped:** a drawn home's `build_era` and `heating_system` now reach the
household register from the world's draw, but `make_household`'s authored-roster path still derives
them from `home_type` archetypes for the C1-C9 cohort, and `_derive_syn_property_fields` remains the
company-side approximation for accessors like `_epc_rating_of`. That asymmetry is correct (the
company's estimate SHOULD be its own), but the authored cohort's dwelling is still an authored
fixture rather than a draw — the same "whoever wrote the fixture composed the population" objection
`premise_population` raises, now the only place it survives.

**The obvious sibling was checked and is NOT one.** `saas.customers.make_acquired_customer` clones a
drawn predecessor's dwelling through `_home_type_of` / `_derive_syn_property_fields`, so a home-move
successor carries the SUPPLIER's approximation as authored-looking `home_type`/`epc_rating` fields.
That is not a second instance of this defect: `run_phase2b` builds property records and the household
register from `CUSTOMERS` only, never from `SUCCESSOR_CUSTOMERS` (`grep` of both call sites), and the
successor's cloned fields are read by company-side consumers (`_epc_rating_of` in
`saas/home_move_win_rate.py`), which is where an approximation belongs. Recorded because "the same
shape must exist next door" is a guess until someone looks.
