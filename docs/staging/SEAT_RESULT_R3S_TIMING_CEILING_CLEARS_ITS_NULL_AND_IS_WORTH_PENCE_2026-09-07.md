**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# R3's timing ceiling clears its null by 4.82x and is worth £4 a household-year at a shiftable share no household has

**Measured:** 2026-09-07, delivery seat, claim `a49-builds-the-r3-and-r4-ceiling-instruments`.
**Instrument:** `tools/r3_carbon_score_ceiling.py`. **Artefact:** `docs/observability/r3_carbon_score_ceiling.json`.
**Held by** 19 controls in `tests/tools/test_r3_carbon_score_ceiling.py`, five of them
mutation-proven in a battery run before this was written (below).
**Predicted in** `SEAT_PREREG_WHAT_THE_R3_AND_R4_CEILINGS_WILL_RETURN_2026-09-07.md`, filed before
the first run. The predictions are reproduced beside the answers so the order is checkable.

---

## What it is

A49's first deliverable: *"what is the most this programme could be worth if it worked perfectly"*,
for R3 — the £/tCO2e score. A score is worth nothing unless there is abatement to score, so the
question is how much carbon this book could abate at all.

**It declares itself a true CEILING and says why**, which is A49's own requirement. Perfect
foreknowledge of the half-hourly intensity shape is exactly the quantity a real forecast
approximates, and perfect compliance is exactly what advice approximates, so nothing buildable
beats the top rung. **A negative would retire time-shifting outright.** `bound_kind`,
`bound_kind_reason` and `bound_scope` are values in the module, not prose in a docstring, and a
control asserts they reach the payload.

**It is a ceiling of the TIMING lever on ELECTRICITY, and of nothing else.** Reduction, gas,
physical measures, tariff switching, embodied carbon and rebound are each named in
`not_bounded_by_this` — because a timing ceiling read as a bound on the whole carbon programme
would retire the mission on the strength of a lever that was never the whole of it. Gas has no
timing lever at all (it emits when burned), which is the scope brief's §B and this instrument's
reason for excluding gas legs from the book.

## The numbers, at real inputs

Over 20 whole days in 2016, 2021, 2022 and 2025, against a book of 68 households carrying an
electricity EAC (median 2,674 kWh/yr):

| rung | gCO2e per shifted kWh | book tCO2e/yr | £/household-yr |
|---|---:|---:|---:|
| `baseline` — no score | 0 | 0 | 0 |
| `hindsight_ceiling` — perfect foreknowledge | 40.75 | 10.68 | 6.91 |
| `forecast_ceiling` — acting on the published forecast | 34.98 | 9.17 | 5.93 |
| `forecast_ceiling_corrected` — and the shape's own exaggeration removed | 23.79 | 6.23 | **4.03** |
| `null_ceiling` — max over 200 skill-free draws | 8.45 | — | — |

**Every one of those is at a shiftable share of 1.0 — every kWh in the day moved into the six
cleanest half hours.** No household does that, and the figure is reported there deliberately: no
published source in this repository establishes a domestic shiftable share, so the alternative was
to invent one. The curve is published instead. At 10% of load moved the corrected figure is **£0.40
per household-year**.

## The predictions, and how they came out

- **P1 — clears its null.** *Confirmed.* 4.82x, against a noise floor built by picking the shift
  window from a shuffled day and scoring it on the real one.
- **P2 — under £10 per household-year even at 100% shiftable.** *Confirmed*, and this was the one
  I held least firmly. £6.91 at perfect foreknowledge, £4.03 corrected. It is the number that
  decides how R3 gets built.
- **P3 — the forecast handicap costs about a seventh.** *Confirmed.* The feed's measured
  `capture_mean` is 0.8585, so the forecast rung is 86% of hindsight.

## What it means, and it is two-sided

**As money, R3's timing lever is negligible** — pence per household-year at any believable
shiftable share, against a book whose money levers move tens of pounds. A carbon score justified as
a revenue or saving mechanism is refuted by its own ceiling.

**As carbon, it is not.** 91.7 kgCO2e per household-year at the corrected ceiling is roughly a
sixth of a 2,674 kWh household's electricity footprint. The gap between those two readings is
entirely the price of carbon: at the DESNZ traded value of £44/tCO2e a sixth of a household's
electricity carbon is worth four pounds. **That is the mission's central difficulty stated as
arithmetic, not as a worry** — the thing the company exists to abate is, at market prices, nearly
worthless to abate. R3's real argument was always that the score is *"the only measure that would
let the company optimise for something other than margin"*, and this ceiling supports exactly that
reading and refutes the revenue one.

**And it is shrinking.** On the typical-day series across the full 2016–2025 record the headroom
fell **42.1%** as the grid decarbonised — 51.9 gCO2e/kWh in 2016 to 30.0 in 2025. The timing
programme is worth less every year it is not built, and that trend is the finding a single
figure would have hidden.

## What is NOT retired by this

Time-shifting is not retired: it clears. But the ceiling bounds only timing, so **R3 as a whole is
not bounded by this document** — reduction and measures are R4's subject and are bounded there.
Anyone quoting £4.03 as "what R3 is worth" would be widening a scope the payload explicitly closes.

## The controls, and the poison round that came before them

Five mutations applied in place and reverted, each killing at least one control; baseline green
before and after:

| mutation | red |
|---|---|
| the null becomes shuffle-then-optimise (the natural way to write it, and it returns the ceiling exactly) | 2 |
| the gas-leg filter removed | 1 |
| a missing overstatement correction defaults to 1.0 | 1 |
| `BOUND_KIND` flipped to `FLOOR` | 1 |
| the empty-book refusal replaced by a zero | 1 |

The first is the load-bearing one and it is asserted directly: `TestTheNullIsARealNull::
test_the_OBVIOUS_null_is_the_ceiling_wearing_a_nulls_name` proves the trap is real, so nobody
"simplifies" the null into it. A shuffle is a permutation; the cleanest window of a shuffled day IS
the cleanest window of the day, so shuffle-then-optimise reports the ceiling as its own noise floor
and reads as a spectacular confirmation.

## Named gaps this leaves open

1. **The shiftable share of domestic load.** Nothing in the knowledge layer, the commons or the
   market research establishes one. This is a question to research, and it is the single number
   that would turn this ceiling into an estimate.
2. **The non-traded (appraisal) carbon value** is held here only as an *asserted* anchor
   (~£80–90/tCO2e, `docs/market_research/population_coverage/value_outcome_model.json`, whose own
   note calls it asserted). Sourcing it would roughly double every money figure above and would not
   change the reading. The traded value is used because GB grid generation sits inside the UK ETS.
3. **20 days across 4 years** is a small panel, and the figure carries its sample size for that
   reason. The typical-day cross-check covers all ten years and understates the level.
4. **Book depth (A46)** bounds how much any ceiling can be *demonstrated* over. Carried as a
   caveat, not as a reason to park.

— Delivery seat, 2026-09-07.
