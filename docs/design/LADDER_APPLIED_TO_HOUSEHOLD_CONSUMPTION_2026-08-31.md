# The ladder applied to household consumption — the world draws an EAC and then bills something uncorrelated with it

**Canon:** `docs/staging/DIRECTOR_CANON_WORLD_VALIDATION_LADDER_2026-08-31.md`, WORK item 2 —
*"each existing world variable assessed against the four rungs, with the result stated on its
Knowledge page."*

**Variable:** residential electricity consumption — how much energy a household actually uses.
**Why this one first:** it is the largest per-customer number in the world. Every bill, every
revenue figure, every margin, every CLV and the company's own EAC belief are computed over it. It
is also the variable with **no Knowledge page at all**, which under the canon's own rule
(*"a page that cannot say is a page whose variable has not been validated"*) means it has never
been validated.

---

## The finding, in one line

**The world assigns each household a consumption level from the published band, and then bills it a
volume that is uncorrelated with that level.**

Paired over the 125 residential electricity accounts with at least a year on supply:

| | median | IQR | p90/p10 spread |
|---|---|---|---|
| **drawn** `eac_kwh` | 2,489 | 1,744 – 3,614 | **2.43×** |
| **billed**, annualised | 4,545 | 3,895 – 4,932 | **1.49×** |
| billed / drawn, per household | **1.81×** | 1.29 – 2.55 | range 0.45 – 4.59 |

**Spearman rank correlation between drawn and billed: ρ = −0.058.**

The household the world decided was a heavy user is not the household that gets billed as one. The
drawn heterogeneity is not attenuated on the way to the meter — it is absent from it.

## Where it goes

`simulation/hedged_settlement.run_hedged_term` (and `run_flex_term`, `run_deemed_term`) build every
settlement record as `shape[period - 1]`, where `shape` comes from the caller. `run_phase2b` binds
that per customer — `_weather_adjusted_shape_fn(SHAPE_LOADERS[profile_class], weather_by_customer,
property_record, …, household_register, customer_id)` — so consumption **does** vary by household,
through EPC, property, weather and assets.

**What it never passes is `eac_kwh`.** The level comes from `sim/profile_class_1.load_pc1_shape`,
whose own docstring says it returns *"48 half-hourly consumption values (kWh) for an average PC1
customer"* — Elexon Group Average Demand, an **absolute** series, not a normalised shape. It
annualises to **3,928 kWh**, and every household starts there before its EPC multiplier (median
1.25) and weather move it.

So the household's own EAC is used for hedging-volume and treasury sizing and is decorative at the
meter. **Two descriptions of one household's consumption, never reconciled** — the ontology canon's
"a concept has one home" failure, on the most fundamental variable in the world.

## Against the four rungs

**Rung 0 — red lines: PASSES.** No household consumes negative or absurd energy; the drawn bands
are enforced against `domain_invariants.TDCV_*` and a drift-guard test holds
`population_draw.TDCV_BANDS_KWH` to them.

**Rung 1 — level: CANNOT YET SAY, and the honest answer is not the obvious one.** The billed median
of 4,545 is 1.82× Ofgem's TDCV medium of 2,500. It is tempting to call that a level failure and it
may be one — but **GAD and TDCV are different published quantities**. Elexon's Group Average Demand
is the mean over all PC1 *meters*, which include electrically-heated and larger properties; Ofgem's
TDCV is a *typical* value for a medium-consumption household, set for bill comparison. Declaring a
1.82× error by dividing one by the other is two true numbers whose legs are different populations,
which is this project's most repeated way of publishing something misleading. **What the right
published counterpart is, is a knowledge question and is stated as open below.**

**Rung 2 — mechanism: PASSES in part.** Consumption responds to weather (HDD/CDD through
`build_demand_shape`), to season and day type through the profile class, to EPC fabric, and to
assets — EV, ASHP and solar all move it in the right direction with the right sign. It has not been
checked that the *magnitude* of the weather response matches the published elasticity, so this is a
qualified pass.

**Rung 3 — heterogeneity: PASSES BY THE WRONG ROUTE, which is worth stating precisely.** Households
do differ, and they differ for reasons a supplier could in principle infer — EPC rating and property
type are public data. So there is something to infer. **But the variation the world intended is not
the variation it produces**: the drawn EAC, which is the world's own statement of how much this
household uses, reaches nothing. A rung 3 that passes through a side door while the front door is
disconnected is exactly the kind of pass the canon warns about, because it looks like validation and
is not.

## The repair, and it goes downward as the canon requires

**Scale each household's profile to its own EAC.** That is what a profile class is for: the industry
convention is a *normalised* shape multiplied by the customer's annual quantity. Doing it here would
close both open rungs in one move and without touching any aggregate:

* the level stops being GAD's magnitude and becomes the drawn EACs' magnitude, which already sits on
  the published band — so rung 1 is answered by the individuals, not by scaling anything;
* the drawn heterogeneity reaches the meter, so ρ stops being zero and the world's own statement
  about a household becomes something a supplier could be right or wrong about.

**This is a correction, not a curriculum choice**, and the direction is against our own thesis: it
reduces every household's billed volume by roughly a factor of 1.8, which reduces revenue, margin
and CLV across the whole book. The director's standing rule is that where the evidence is ambiguous
we choose the option that makes the company's advantage harder to demonstrate; here the correction
does that on its own.

**It is not made in this document.** It changes every financial figure the project publishes, so it
wants its own pre-registration — what the level, the spread and the company's EAC error must show
after the change — and a one-variable run, which is the canon's own discipline and this project's
rule about attributing a move when more than one thing changed.

## What is open, stated rather than assumed

1. **Which published quantity is the right counterpart for a household's annual consumption** — TDCV
   (a typical value, for bill comparison) or NEED/GAD (a measured mean, over all meters). The
   knowledge map already holds both: NEED 2026 median 2,500 with IQR 1,600–4,100, and TDCV
   Low/Med/High 1,600/2,500/3,800. The two are close, which is itself evidence that the world's 4,545
   is high against both — but "close" is not "the same question", and the page should say which it
   is being checked against.
2. **Whether the weather response has the published magnitude**, not merely the right sign.
3. **Household consumption has no Knowledge page.** Under the canon this variable's rung positions
   have nowhere to be stated. That is the first thing owed, and this document is its draft.
