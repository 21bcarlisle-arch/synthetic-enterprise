**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a51-derating-callers-and-the-dsr-cmu-shape

# PRE-REGISTRATION: what a real aggregated DSR CMU is made of, written before I read the register

**Written:** 2026-09-07, delivery seat, claim `a51-derating-callers-and-the-dsr-cmu-shape`.
Written **after** the two CSVs were downloaded and **before** either was opened — no column of
either file has been read at the time of writing, only the CKAN resource listing that names them.

## Why this measurement exists

`capacity_market_published_record.DOMESTIC_PARTICIPATION_REFUSAL` refuses the domestic Capacity
Market leg, and the whole weight of the refusal currently rests on **one division**: a 1,000 kW
minimum CMU against a 3.0–15.4 kW whole flexible house, therefore ~80 households to reach the
smallest unit that can prequalify. That is arithmetic over two published constants. It is not an
observation, and **it cannot be wrong in an interesting way** — no matter what the world does, 1000
divided by 12.4 is 80.6.

The same NESO dataset that gave up the de-rating factors publishes the **Capacity Market Register**
itself: every CMU and every Component inside it, with capacities. That register can say what an
aggregated DSR CMU is *actually built from*. It is the one piece of evidence in reach that could
**refute** the refusal rather than restate it, which is the only reason to spend a turn on it.

## What would refute the refusal, stated before I look

The refusal says a household reaches the CM only inside an aggregator's DSR CMU, and that what the
aggregator passes through is bilateral and unpublished. Two distinct claims sit under that, and the
register can only speak to the first:

* **The participation claim** — domestic-scale load does not hold agreements in its own right, and
  reaching the CM means being a Component in someone else's CMU. **REFUTED IF** the register
  contains CMUs whose components are predominantly single-digit-kW, i.e. domestic aggregation is a
  thing that visibly happens at scale in the published record. That would not make a household a
  CMU; it would move the refusal's grounds from "the arithmetic forbids it" to "it happens, and we
  still cannot price it", which is a materially weaker and more honest refusal.
* **The pass-through claim** — no publication states what an aggregator pays a member. The register
  **cannot** refute this and I am not going to claim it did. Component capacity is not a payment.

## Predictions (I do not know the answers)

Against DSR CMUs only — the class an aggregated demand-response unit falls in, and the class whose
de-rating factor `DSR_TECHNOLOGY_CLASS` names.

1. **Component count.** Median DSR CMU has **≤ 5** components; the 90th percentile is **< 50**. A
   real DSR CMU is a handful of large industrial sites, not a crowd.
2. **Component size.** Median DSR component connection capacity **≥ 200 kW**. Fewer than **1%** of
   DSR components are below **15.4 kW** — the largest whole-house flex figure in
   `flexibility_potential.py`, i.e. the most generous domestic scale this book carries.
3. **No domestic-shaped CMU.** **Zero** DSR CMUs have a majority of their components below 15.4 kW.
4. **The ~80 is a floor, and a misleading one.** The median DSR CMU is materially larger than the
   1 MW minimum — I predict a median **de-rated** capacity of **2–10 MW**, so a *typical* DSR CMU
   built from domestic flex would need **several hundred** households, not 80. If so, the refusal's
   published number is right about the threshold and understates the practical requirement by
   roughly an order of magnitude, and the finding is that ~80 is the answer to a question nobody
   is actually asking.
5. **The floor itself.** I predict the smallest awarded DSR CMU in the register sits at or just
   above 1 MW of de-rated capacity, confirming the threshold binds in practice rather than being
   a formality that awarded units clear by miles.

If 1–3 come out as predicted, the refusal is **corroborated by observation** and I will say so in
exactly those terms — corroborated, not proved, because absence of domestic components in the
register is consistent with domestic aggregation being small, new, or filed under a component name
that does not say "household".

## What I will not claim either way

* That a component **is** a household. The register publishes a capacity, not an occupancy. A 4 kW
  component could be a household, a lift motor, or a rounding of something bigger.
* That the DSR class is the only route. It is the route this book's I&C leg models and the one
  `DSR_TECHNOLOGY_CLASS` names; if the register shows domestic-scale aggregation arriving under
  some other class, that is a finding and not a refutation of anything written here.
* Anything about pass-through. See above.

## The other half of the same claim, pre-registered separately from the numbers

The de-rating callers. I have **already read** all three modules as I write this, so what follows
is a reading and not a prediction, and it is fixed here so the finding cannot be tuned to it:

* `company/market/flexibility_potential.py` — the domestic leg returns `None` unconditionally. My
  reading is that **no factor belongs here and none ever will**: a multiplier below 1 makes a
  refused number smaller, never legal, and the missing thing is an agreement, not a factor.
* `company/market/capacity_market.py` — `CMUnit.derated_capacity_kw` already **names its input as
  de-rated**. My reading is that applying `derating_factor()` inside `annual_revenue_gbp` would
  **double-count**, and the live hazard is the opposite one: nothing stops a caller passing a
  rated figure into a field whose name says de-rated.
* `company/regulatory/capacity_market.py` — carries `_DERATING_FACTOR = 0.92` with the comment
  "Assumed average de-rated supply margin %". My reading is that this is an **invented constant
  doing the wrong job**: the supplier's Capacity Market charge is levied on *demand*, and demand
  is not de-rated. I predict, before running it, that removing the 0.92 is not the fix — the
  whole quantity is already established elsewhere in this repo and this module reinvents it.

**Prediction on that last one, and it is a real one:** the £/MWh this module produces for a real
input is **more than 2×** the sourced Ofgem Annex 9 figure in `docs/market_research/
capacity_market_levy_2016_2024.md` for the same year, and the direction is **over**, not under.
