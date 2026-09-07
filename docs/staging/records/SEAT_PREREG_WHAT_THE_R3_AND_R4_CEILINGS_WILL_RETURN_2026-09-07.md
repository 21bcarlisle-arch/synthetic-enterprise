**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# [SEAT PREREG] — What the R3 and R4 ceiling instruments will return, written before either is run (2026-09-07)

A pre-registration, not a defect. It is filed because A49's two deliverables are measurements whose
answers I do not know, and a prediction written after the answer is not a prediction.

**Atom:** `A49_the_ceiling_comes_before_the_programme_on_r3_and_r4`.
**Claim id:** `a49-builds-the-r3-and-r4-ceiling-instruments`.

---

## Why this is being written now

A49's gating decision landed 2026-09-07 in `d7b2a35d4`: the gate is OPEN — R1 does not retire R3 or
R4 — and it does **not** license building them, because R1 bounds INFERENCE and says nothing about
what a carbon score or an advice product is worth. So what stands between A49 and its target level
is exactly what it was minted for: **a ceiling instrument per side.**

I have read the substrate and designed the instruments. I have **not run either**. Everything below
is a prediction against a design that is fixed before the first number.

---

## The designs, stated so the predictions are falsifiable

### R3 — the score (£/tCO2e), against E5's half-hourly footprint and the intensity feed

R3 is *"£ per tonne of CO₂e abated ... the only measure that would let the company optimise for
something other than margin"*. A score is worth nothing unless there is abatement to score, so the
ceiling question is **how much carbon the book could abate at all**, and the score's own unit needs
a comparator.

The only lever the electricity carbon *shape* offers is **timing**. The advisor scope brief
(`ADVISOR_SCOPE_BRIEF_CARBON_2026-08-04`, §B) is explicit: gas emits when burned, so no
time-shifting benefit exists in gas, and *"time-shifting only pays in electricity"*. So the R3
instrument bounds the timing lever and states plainly that reduction and measures are **not** in its
scope — they are R4's.

Rungs, one book, one method:

| rung | what it is |
|---|---|
| `baseline` | no score at all. The book's emissions on its own timing. Zero abatement by construction. |
| `hindsight_ceiling` | every shiftable kWh placed in the cleanest half hours of its own day, with **perfect foreknowledge** of the intensity shape. |
| `forecast_ceiling` | the same, acting on the **published forecast** rather than hindsight, handicapped by the feed's own measured `capture_mean`. |
| `null_ceiling` | the same optimiser against a **shuffled** within-day shape. Destroys the signal, keeps the optimiser's freedom. |

**The headline assumes 100% of load is shiftable — deliberately, and it is physically absurd.**
No published source I could find establishes a domestic shiftable-load share; grep over
`docs/market_research/`, `docs/domain_artefact_library/` and `docs/institutional/` returns nothing.
Rather than invent one, the ceiling is reported at the parameter-free bound (every kWh moves), which
is what a ceiling is for, with the linear curve across shiftable shares beside it and the missing
parameter named as a gap. A number invented for that slot would be load-bearing within a week.

**CEILING or FLOOR:** a true **CEILING** for the timing lever, and the instrument must say so on its
own surface. Perfect foreknowledge of the half-hourly shape is exactly the quantity a real forecast
approximates, so nothing buildable beats `hindsight_ceiling`. A negative there retires time-shifting
outright. It is a ceiling *of the timing lever only* and retires nothing else.

### R4 — products beyond price, against the book and the consumption feed

R4 is *"advice, tariff fit, efficiency measures, solar, heat pumps, time-shifting"*, and the canon's
charge is that *"the company can make a household cheaper and never greener"*. The ceiling question
per product: the most it could be worth per household-year, in £ and tCO2e, under **perfect
targeting and perfect adoption**, against the null of **price alone** — the money-only lever the
company already has.

The instrument's real deliverable is the **CEILING/FLOOR verdict per product**, because that is what
decides whether a negative retires anything. It is decided by what the book holds, and the book's
observable set is `OBSERVABLE_FIELD_SCOPE` in `tools/r1_inference_ceiling.py`: rates, the SVT
spread, `company_eac_kwh`, margin and portfolio position. **No property attribute appears anywhere
in it** — no EPC, no floor area, no heating system, no roof, no occupancy.

## The predictions

Written now, and each is refutable by the instrument I am about to build.

**P1 — R3's timing ceiling clears its shuffled null.** The feed's own `by_year` puts the demand-
weighted within-day p95/p5 spread at 2.8–3.1x, which is a real signal an optimiser can exploit and a
shuffle destroys. I expect `hindsight_ceiling` well clear of `null_ceiling`. *Confidence: high — this
is close to arithmetic.*

**P2 — and it is small in money once it is a score.** This is the prediction I actually hold least
firmly and the one worth having. At the sourced DESNZ traded carbon value (£44/tCO2e, 2025 real,
`ssp_multiplant_srmc_stack_heat_rates_2026-07-25.md`), I predict the **whole-book** hindsight timing
ceiling monetises to **under £10 per household-year even at 100% shiftable load**, and therefore to
a fraction of that at any believable share. If that holds, R3-as-a-score is not retired but it is
**bounded far below the money levers**, and the honest headline is that the score's value is as an
*optimisation target the company does not have*, not as an abatement pot. *Confidence: low-to-medium.
This is the number I most expect to be wrong about, and it decides how R3 gets built.*

**P3 — the forecast handicap costs about a seventh.** The feed's measured `capture_mean` runs ~0.87,
so `forecast_ceiling` should land near 87% of `hindsight_ceiling`, not near zero and not near one.

**P4 — R4 splits, and the split is the finding.** I predict:
- **tariff fit** — a true CEILING, and its **carbon ceiling is exactly zero by rule, not by
  measurement**: the director's standing rule is that savings count only from reduced or
  time-shifted usage, never from discounting. This is the canon's charge made arithmetic — the
  company's one working lever is the one that cannot abate.
- **time-shifting** — a true CEILING, and it is R3's rung. R4 cites it rather than recomputing it.
- **efficiency, solar, heat pumps** — handicapped **FLOORS**, every one, because the book holds no
  property attribute to target on. A negative retires nothing.
- **advice** — I do not yet know, and I am recording that rather than guessing.

**P5 — R4's money ceiling is dominated by tariff fit, and its carbon ceiling is dominated by
everything that is a floor.** If true, that is A49's answer in one sentence: the part of R4 we can
bound is the part that cannot abate, and the part that abates is the part we cannot bound without
data the company does not hold. **The named gap would then be a data-acquisition question, not a
modelling one** — and that is a materially different programme from the one R4 describes.

## What would make me wrong in a way that matters

If P2 fails high — the timing ceiling monetises to tens of pounds per household-year — then R3 is a
real pot and should be built ahead of R4. If P4's floor verdict is wrong because some property
attribute *is* observable that I did not find, R4's efficiency arm becomes gateable and the
data-acquisition finding evaporates. Both are checked by the instruments, not by argument.

## What this does not claim

Neither instrument measures whether the company *can* deliver either programme, and neither is a
ranking system. They bound what the programmes could be worth if they worked perfectly, which is the
only question A49 asks. R5's book depth (`A46`) bounds how much any ceiling can be *demonstrated*
over; that is a caveat both instruments must carry, not a reason to park them.

— Delivery seat, 2026-09-07, before the first run.
