# The world's dwelling for a drawn home is the company's own estimate

**Severity:** BLOCKING · **Lane:** W4_the_wall

**Found:** 2026-08-17, during KNIFE pass 3 step 30 (`KNIFE3_wall_crossing_paydown`, register §3y)
**Class:** B2/B3 inversion — a company BELIEF constituting a world FACT
**Disposition:** QUEUED, not fixed on sight (`SELF_INTERRUPT_DISCIPLINE`)

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
