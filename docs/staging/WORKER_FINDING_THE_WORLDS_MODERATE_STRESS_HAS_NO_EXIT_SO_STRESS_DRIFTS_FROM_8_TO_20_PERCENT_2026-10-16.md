**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_38_the_worlds_debt_is_graded_against_ofgems_quarterly_series` · **Claim:** `the-budget-decides-how-much-of-each-bill-is-paid`
**Knowledge:** debt-and-collections -- `docs/market_research/debt_and_collections.md` (FCA Financial Lives rows, negative life events), `docs/market_research/household_budget_w2_4.md` §2026-10-16 (why this stays separate from the budget build)

# The world's MODERATE income stress has no way back to LOW, so stress drifts from 8% to 20% over a decade

*A second world defect, kept apart from the payment-draw fix on purpose. It came out of the
by-year table in
`WORKER_FINDING_THE_WORLDS_PAYMENT_DRAW_HAS_NO_PRICE_INPUT_SO_2022_CANNOT_RAISE_NON_PAYMENT_AND_THE_BUDGET_BUILT_FOR_IT_IS_UNWIRED_2026-10-16.md`.
Diagnosis and prediction only. No world code changes before the 2026-10-19 publish, and this fix
does not ship in the same build as the budget fix, because two changes landing together cannot be
told apart.*

## What was measured

Among billed electricity accounts at Q4, the share in MODERATE or HIGH stress rises steadily:
**8% (2016), 10%, 12%, 13%, 14%, 15%, 16%, 18%, 20% (2024)**. It rises in calm years and crisis
years alike (one seed, about 250 to 420 accounts a year, from the table in the finding above).

## What the published comparator counts, before comparing

FCA Financial Lives: the share of adults who had **a negative life event in the last 12 months**
(job loss, an unwanted cut in hours, bankruptcy, separation, serious illness, bereavement,
becoming a main carer). It was **19% in 2017, 21% in 2020, 20% in 2022 and 18% in 2024** (original
algorithm; `debt_and_collections.md`, FLS 2024 vulnerability report p. 36). That counts **people**,
over a **12-month flow window**. The world's tier is a **household stock state** with no window.
So the two levels are not like for like, and **19-22% is not the target for 20%.** What does carry
over is the **trend**. The published share is flat for seven years, and the world's doubles and
more. A stock driven by a steady flow and a steady exit rate should also be flat. A stock that
climbs for ten years means the exit rate is too low.

## The mechanism (read from the code, not yet measured by tier)

In `simulation/life_events.py`:
- new_baby, retirement_starts and divorce move **LOW → MODERATE**;
- job_loss and illness move **LOW or MODERATE → HIGH**;
- income_recovery moves **HIGH → LOW** at `_INCOME_RECOVERY_ANNUAL_PROB = 0.50`;
- **no event moves MODERATE → LOW.** A MODERATE household leaves only by getting worse first.
  Retirement-driven MODERATE is permanent unless a job loss or illness follows.

A second, smaller point sits in the same block. The comment on `_INCOME_RECOVERY_ANNUAL_PROB` cites
"median UK unemployment spell ~6 months". Under a constant hazard, a 6-month median means
about **0.75** recover within a year, not 0.50 (1 − 0.5², derived). So HIGH also drains more
slowly than its own source says.

## Prediction (filed before any tier-by-year measurement)

- **S1.** Split by tier, the drift is in **MODERATE**: MODERATE's share of billed accounts rises
  monotonically, or nearly so, from 2016 to 2024, and at least 80% of the 12-point rise is
  MODERATE. HIGH stays within ±3 points of its 2017 share in every year.
- **S2.** Among accounts present in both Q4 2016 and Q4 2024, no account goes from MODERATE to LOW
  without passing through HIGH (it follows from the code; the check is that the instrument agrees).
- **S3, the fix's effect.** Adding a MODERATE → LOW exit holds the MODERATE + HIGH share within ±3
  points of its 2017 level over 2017-2024, provided the exit is at least as fast as HIGH's 0.50.

*Refutation:* if HIGH carries most of the rise, the defect is the slow HIGH exit (0.50 against its
source's 0.75), not the missing MODERATE exit. Say so beside S1.

## What the fix needs before it is built (K8)

- **A sourced exit rate from MODERATE.** **GAP.** No figure is on the knowledge layer for how long
  a household's finances stay strained after a birth, a separation or retirement. Candidates to
  research: ONS/Understanding Society persistence of financial difficulty, and FCA FLS movement
  between "financially resilient" states. Do not pick a number.
- **Whether retirement belongs in MODERATE at all.** Pensioner income is stable. The published
  driver is the drop in income at retirement, not ongoing strain. Research before keeping the
  transition.
- **HIGH's exit rate re-read against its own cited source** (the 0.50 against 0.75 above).

## How it interacts with the budget build

The budget build (`household_budget_w2_4.md` §2026-10-16) does not read the stress tier. It reads
the margin. The per-bill transient draw that stays in place does read the tier, so this drift
keeps nudging the world's heads upward whichever build lands first. **Order:** the budget build
lands first, as the first world change after the publish. This fix goes in a later build, so each
move in the yearly table can be attributed to one change.

**Fate:** open, for a build after the budget build. The page and the exit-rate research come first.
