**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# R4 splits three CEILINGS to three FLOORS, and the half we can bound is the half that cannot abate

**Measured:** 2026-09-07, delivery seat, claim `a49-builds-the-r3-and-r4-ceiling-instruments`.
**Instrument:** `tools/r4_product_ceiling.py`. **Artefact:** `docs/observability/r4_product_ceiling.json`.
**Held by** 16 controls in `tests/tools/test_r4_product_ceiling.py`, six of them mutation-proven in
a battery run before this was written.
**Predicted in** `SEAT_PREREG_WHAT_THE_R3_AND_R4_CEILINGS_WILL_RETURN_2026-09-07.md` (P4, P5),
filed before either instrument existed.

This closes A49's second and larger deliverable. R3's is
`SEAT_RESULT_R3S_TIMING_CEILING_CLEARS_ITS_NULL_AND_IS_WORTH_PENCE_2026-09-07.md`.

---

## The verdict per product, which is the actual deliverable

A49's requirement is that each instrument state whether it is a true **CEILING** (a negative
retires the candidate outright) or a handicapped **FLOOR** (a negative retires nothing). R4 is not
one programme, so it does not get one answer — and the split is decided by what the book holds, not
by how promising the product sounds.

| product | bound | £/household-yr | kgCO2e/household-yr | why |
|---|---|---:|---:|---|
| **tariff fit** | CEILING | 2.19 | **0.00, by rule** | the company holds both sides of the subtraction |
| **time-shifting** | CEILING | — (see below) | 91.7 | R3's own figure, read not recomputed |
| **advice** | CEILING | not additive | not additive | a CHANNEL for the two above, not a pot beside them |
| **efficiency (fabric)** | FLOOR | `None` | `None` | no fabric parameter reaches the book |
| **solar** | FLOOR | `None` | `None` | no roof area, pitch or orientation |
| **heat pump** | FLOOR | `None` | `None` | no incumbent heating system to difference against |

The three floors return **`None`, never 0.0**. A zero would be read as "solar is worth nothing";
a `None` with its missing datum named cannot be.

## The census, run rather than assumed

The FLOOR verdicts rest entirely on the company holding no property attribute, so that is
**computed from the run output each time** rather than stated in prose: `property_attribute_census`
walks every log for any fabric, EPC, floor-area, roof, insulation, glazing, tenure or occupancy
field. **Across 29 logs it found zero.** If the world ever starts writing one, the verdict moves on
its own — the control is keyed to the property, not pinned to today's answer.

The world *does* hold a `fabric_eligibility` register, and it is the sharper version of the same
point: **4 of 152 rows are eligible** ("domestic premise with fabric parameters and local weather"),
2.6%. The book can be eligible and blind at the same time, and here it is.

## The predictions

- **P4 — R4 splits, and the split is the finding.** *Confirmed in every part.* Tariff fit a true
  ceiling with carbon exactly zero by rule; time-shifting a ceiling and it is R3's rung, cited not
  recomputed; efficiency, solar and heat pumps all floors. On **advice** the prereg said "I do not
  yet know, and I am recording that rather than guessing" — the answer is that advice is a
  **channel**, not a seventh pot. Its ceiling *is* the ceiling of the arms it delivers, and adding
  it to them would count the same value twice.
- **P5 — the bounded part cannot abate, the abating part cannot be bounded.** *Confirmed.*

## What it means

**The canon's charge is now arithmetic rather than assertion.** *"Today the company can make a
household cheaper and never greener"* — tariff fit is the one money lever this book can bound, and
its abatement is **exactly zero by the director's own standing rule**: savings count only from
reduced or time-shifted usage, never from discounting. A cheaper tariff changes no kWh and no hour.

**And both bounded arms are small.** £2.19 of bill saving and £4.03 of carbon value per
household-year — and only **7 of 68 households are priced above the market reference at all**. So
the entire part of R4 this book can bound is worth a few pounds a household-year. **Any real value
in R4 lives in the three arms that are FLOORS.**

**R4 is NOT retired**, and that follows from the floor verdict rather than from optimism: nothing
here bounds the measures *from above*, so a small reading on the bounded arms retires nothing about
the unbounded ones. **What stands between R4 and a real bound is a DATA ACQUISITION, not a model** —
and that is a materially different programme from the one R4 describes.

## Two things the instrument refuses to do

1. **It refuses to total.** The products are not disjoint (advice is the channel for the others;
   solar and a heat pump both change grid import) and the columns are not one currency. A total is
   the number a reader would quote.
2. **It refuses to add the currencies.** Tariff fit's pounds are a **bill saving**. Time-shifting's
   pounds are **carbon valued at the traded price** — not a bill saving at all, because this book
   holds **no time-of-use tariff** for a shifted kWh to be cheaper on. That absence is itself a
   named gap and it is the product decision that would let the household *share* in the value R3
   measures. Value created and then shared: R3 measures the creation, and there is currently no
   instrument of sharing.

## The defect this instrument was caught by, kept beside the number it produced

The first draft of `rate_against_reference` collected rates from every log and market references
from the one log that carries them, then differenced the per-household **means**. It returned
**£88.21** per household-year for tariff fit. The true figure is **£2.19** — a **40x artefact**.

The rate was averaged over every priced term a household ever had; the reference only over its
renewal occasions; and GB electricity prices move by a factor of three across 2016–2025.
**Differencing two averages taken over different windows is not a price gap, it is a price trend.**
This is the "before dividing two numbers, say out loud what each one counts" rule, and printing the
numbers at real inputs is what caught it — not more thinking, and not a test, which would have been
written against the wrong quantity. `test_a_rate_and_a_reference_on_DIFFERENT_rows_are_not_compared`
now holds it, and restoring the cross-log pairing turns it red.

## The controls

Six mutations applied in place and reverted, each killing at least one control; baseline green
before and after:

| mutation | red |
|---|---|
| cross-log pairing restored (the £88.21 artefact) | 1 |
| signed gaps instead of positive-side-only | 1 |
| the measure arms become CEILINGs reporting 0.0 | 2 |
| the census marker list emptied | 1 |
| time-shifting's carbon value moved into the bill-saving column | 1 |
| the thin-book refusal replaced by a number | 1 |

## Named gaps

1. **Property attributes.** The single acquisition that would turn three FLOORS into CEILINGS. A
   data question, not a modelling one.
2. **A time-of-use tariff.** Without one, time-shifting has a carbon ceiling and no bill-saving
   ceiling at all.
3. **Book depth (A46)** bounds how much any of this can be *demonstrated* over.

## What A49 now has, and what it still does not

Both instruments exist, each declares its own bound kind on its own surface, and each answers "what
is the most this could be worth if it worked perfectly" against a stated null. **Neither is wired
to a published surface** — both are run on demand and frozen in the orphan baseline as deliberately
dormant, like the six ceiling instruments before them. Putting R3's and R4's readings on `/harness/`
beside R1's gate is the obvious next increment and is not in this one.

— Delivery seat, 2026-09-07.
