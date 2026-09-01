# [WORKER FINDING] Bill shock is three causes and a sign collapsed into one `abs()`, and the world already labels two of them

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`
**Found:** 2026-09-01, by the delivery seat, on the director's instruction to establish what bill shock actually is before building satisfaction's rationale.
**Knowledge:** `docs/market_research/satisfaction_drivers_and_the_three_bill_shocks.md` (published sources, fetched live this pass).

## Class registration

Belongs to `measurements_that_mirror`. **Refused consolidation, correctly** — that register is
`H_harness` and this is `W2_customer_generator`; it will be listed under "Refused consolidation —
out of lane, still live" and stays in the queue.

## The measure

`saas/bill_generator.generate_bill`:

    bill_shock_pct = abs(total_amount_gbp - previous_bill_total_gbp) / previous_bill_total_gbp

and `company/billing/monthly_bill_assembly` **recomputes it in the same shape** after folding a
catch-up correction onto the bill.

## What the published record says it should be able to tell apart

Three causes that diverge on responsibility and remedy (full sourcing on the knowledge page):

| cause | responsibility | published magnitude | remedy |
|---|---|---|---|
| **(a)** catch-up after a run of estimates | supplier's **inference** failure | median domestic backbill **£1,160**; capped at 12 months by SLC 21BA | actual reads |
| **(b)** DD set too low → debit → reset | supplier's **operational** failure | **>7m** SVT customers, **avg +62%**, **8% >100%** (Ofgem DD review, 2022) | better DD setting |
| **(c)** genuine renewal price rise | supplier's **commercial choice** | the cap and the fixed-to-SVT spread | price differently |

## What our world does — measured, on `run_output_latest.json`, 10,906 bills

**All three, plus the sign, collapse into one scalar.**

| | |
|---|---|
| consecutive bill pairs carrying a shock figure | **10,655** |
| of those, shocks ≥30% | **3,249** |
| …that carry a catch-up (cause **a**) | **655 — 20.2%** |
| …that land on a bill whose own basis is **estimated** | **1,981 — 61.0%** |
| …**where the bill FELL** | **1,364 — 42.0%** |
| catch-up direction among the shocked | undercharge **340** / overcharge **315** |

**42% of large "bill shocks" are bills that went down**, including 315 catch-up *refunds*. The world
reads a supplier returning money as an event that reduces satisfaction and clarity, identically to
one that takes money.

**61% of shocks are measured against a bill that is itself an estimate** — a guess compared with a
guess, presented to the household as a fact about its own consumption.

---

## CORRECTION, made the same day, and it found a bigger defect than the one it corrects

**One row of the table above crossed two populations, which is the defect this document is about,
committed inside it.** The wrong version is kept above rather than edited away.

**What was wrong.** The row *"…where the bill FELL — 1,364 — 42.0%"* was presented as a property of
the 3,249 bills whose **stored** `bill_shock_pct` is ≥0.30. It is not. The direction came from a
*reconstructed* pairing (consecutive bills, same customer, same commodity) and was then quoted
against a count selected by the stored field. Two legs, two populations, one percentage. The other
rows — catch-up 20.2%, estimated basis 61.0%, undercharge 340 / overcharge 315 — are properties of
**the bill itself** and are unaffected.

**The corrected figures, with each population named.**

| | population A: stored `bill_shock_pct` ≥ 0.30 | population B: recomputed movement ≥ 30% |
|---|---:|---:|
| n | **3,249 bills** | **2,269 pairs** (of 10,654) |
| carry a catch-up | 20.2% | 33.3% |
| on an estimated bill | 61.0% | 35.7% |
| **the bill FELL** | *not recoverable — see below* | **40.9%** |

So the corrected headline is **40.9% of large bill MOVEMENTS are decreases**, on population B. The
direction of population A's members cannot be recovered from the artefact at all, which is the next
paragraph and is worse.

## The bigger defect: the stored shock cannot be reproduced from the published bill

Checking the stored field against a recomputation on the pair it should describe:

    stored bill_shock_pct == abs(this - previous)/previous   on   3,198 of 10,654 pairs  =  30.0%

**Seventy per cent of the published `bill_shock_pct` values cannot be reproduced from the published
bills.** Tested and excluded: it is not the grouping (same-customer-same-fuel, both-fuels
interleaved and customer-plus-segment all give the identical 30.0%, so the same pairs match under
every grouping), and it is not a component convention (ex-VAT, ex-catchup and ex-both all sit at
30.0–30.2%).

**What does discriminate is the PREVIOUS bill's basis:**

| | previous bill was `actual` | previous bill was `estimated` |
|---|---:|---:|
| reproducible | **3,075** | 123 |
| not reproducible | 841 | **6,615** |

96% of the reproducible pairs follow an actual bill; 89% of the irreproducible ones follow an
estimated bill. **`bill_shock_pct` is measured against the previous bill's total as the pipeline
held it at the time — and where that bill was an estimate, its total was subsequently revised by the
catch-up reconciliation, so the stored shock is a difference against a number that no longer exists
in the published artefact.**

That is `figures_on_a_superseded_clock` — a figure frozen before the rows it summarises were
mutated — sitting inside the field that drives satisfaction, clarity and contact propensity.

And it sharpens the finding rather than softening it. **The household's "shock" is measured against
an estimate the supplier itself later admitted was wrong.** That is not a fourth cause beside the
director's three; it is the measurement being taken from the wrong baseline for the majority of the
book, and it is the same root as cause (a): we estimated, we were wrong, and the instrument that is
supposed to record what the household experienced recorded our own revision instead.

## What this changes in the owed list

Item 1 (split by cause) and item 2 (drop the `abs()`) stand. **A new item goes ahead of both:
`bill_shock_pct` must be computed against a baseline that survives into the artefact**, or it cannot
be checked by anyone — including by the control that would police items 1 and 2. A measure that
cannot be reproduced from what is published is not a measurement of the world; it is a measurement
of an intermediate state nobody can see.

### Cause (c) is not separable at all

No bill field in the artefact names a renewal, tariff change, price change or contract event
(checked across every key present on any of the 10,906 bills). There is no way, from a bill, to tell
a commercial price rise from an operational catch-up.

### Cause (b) does not reach the household at all — and the world knows it

The DD machinery exists and is substantial. `annual_dd_review` over the record:

    total_reviews 806 · increase 522 · decrease 209 · maintain 75
    large_increase 431 · avg_variance_pct 106.2

`company/billing/dd_review_runner.py` says so itself, honestly and in its own docstring:

> *"DD4b — the CONSEQUENCE half — is the registered NEXT gated step, NOT built here: routing a
> `large_increase` review into the live churn/resentment engine… This module already emits the
> `large_increase` flag DD4b will route on, so the seam is ready."*

So the world computes **431 large DD increases, flags every one, and routes them nowhere.** And
`bill_shock_pct` cannot pick them up, because it is computed from **bill totals** — and **178 of the
book's 251 accounts (71%) are on a level direct debit**, paying a fixed £64.48/month regardless of
the bill. `dd_level_collection_book` reports `all_schedules_level_fixed: true`.

**For 71% of the book, the world's bill-shock signal is computed from a number the household does
not pay, while the number it does pay changes in a 431-event stream that feeds nothing.**

### And the DD level is outside the published band

Comparing our increases with Ofgem's published distribution for the worst quarter in the GB record:

| | Ofgem, Feb–Apr 2022 (crisis) | our world, whole record |
|---|---:|---:|
| increases above **100%** | **8%** of SVT customers | **31.0%** (162 of 522) |
| average / median increase | **+62%** average | **+52%** median, **+174%** mean |

Ofgem required every supplier that raised a DD by more than 100% to re-review it; **over 900,000**
direct debits fell into that exercise and it produced twelve compliance engagements and an
enforcement order. **Our world produces >100% increases at roughly four times the rate of the worst
published quarter on record, as its steady state, and nothing checks it.** That is a rung-1 level
failure on a variable that has never been checked against a band, and the band exists.

*(`LARGE_INCREASE_THRESHOLD_PCT = 15.0` is declared in its own comment as "deliberately conservative
and NOT sourced to a specific published figure". It can now be sourced, or at least bounded: Ofgem's
own operational cut for "this needs a second look" was 100%.)*

## Why this is `measurements_that_mirror`

The instrument reads its own subject back. `bill_shock_pct` is the *company's own bill total*
differenced against *the company's own previous bill total* — so what it measures is how much the
company's billing moved, not what happened to the household. When the company estimates badly for
six months and then corrects, the instrument records "the customer was shocked". When the company
refunds an overcharge, it records the same thing. The one input that would make it a fact about the
world rather than about our billing — **which of the three causes produced it** — is available on
the bill for (a), available in a register for (b), and discarded at the point the number is formed.

**The world already decides this and then throws the answer away** — the same shape as
`WORKER_FINDING_THE_WORLD_ALREADY_DECIDES_WHO_ROLLS_TO_SVT_AND_THEN_DISCARDS_THE_ANSWER_2026-08-30`,
at a second address, found the same way.

## What is owed

1. **Split the measure by cause, not by adding a term.** `bill_shock_pct` should become a small
   record — magnitude, **direction**, and cause in {`catchup`, `dd_reset`, `price_change`,
   `consumption`} — because the three have different responsibility and different remedies and a
   scalar cannot carry that. Causes (a) and (b) are already labelled upstream; only (c) needs a new
   marker, and renewals already know when they fire.
2. **Sign first, and separately.** Dropping the `abs()` is one line and changes 42% of large shocks
   from a penalty to a benefit. It moves published figures, so it is its own pre-registered,
   one-variable change — and it must not be bundled with (1) or neither can be attributed.
3. **Check the DD level against the published band** before routing DD4b. Routing a stream that
   produces >100% increases at four times the crisis rate into churn would make the world leak for a
   reason that is our own mis-calibration, not a household's response.
4. **NOT the satisfaction rebuild.** The director's instruction was knowledge first, and the
   knowledge says the dominant driver of GB domestic dissatisfaction is not the bill at all — it is
   **how long a problem takes to resolve, being kept updated, and being told how long it will take**
   (complaint-handling satisfaction 44% against 80–87% for everything routine). Satisfaction's
   missing rationale is a *resolution* term, not a better bill-shock term. That is now established
   and is the next build.

## What this finding does not claim

Not that any published figure is wrong today. Not that the DD machinery is wrong — it is careful,
cites SLC 27B, and is honest in its own docstring about what it has not wired. The claim is that
three causes with opposite remedies, and a sign, arrive at the household's satisfaction as one
absolute number, and that the information needed to separate them already exists on our side of the
wall.
