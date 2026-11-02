**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** none — Lane 0 `the-gas-cv-is-the-period-average-of-the-daily-series`

# Pre-registration: how far the fixed 39.5 gas CV sits from the published period average (2026-11-02)

Written before the National Gas series was summarised; only five rows of LDZ(EA) had been seen
(Jan 2022 and Jan 2024, 38.0 to 39.3). For G1 of
`docs/market_research/a_gas_read_is_a_volume_and_the_bill_converts_it.md`.

## What is measured

The published daily CV per charging area (National Gas data portal, PUBOB4507-PUBOB4519, the
13 LDZs), every gas day it serves. For each LDZ and calendar month: the R5 CV (mean of the month's
daily values, truncated to 0.1 MJ/m3) against (a) the untruncated mean and (b) the 39.5 stand-in the
book bills at today. A calendar month stands in for a billing period, since the book bills monthly.

## Predictions

1. **Coverage.** The portal serves the LDZ series from about Nov 2021 only, so 2016 to Oct 2021 is
   not transcribable from it. (Seen while probing: PUBOB4507's first row is 1 Nov 2021.)
2. **Range.** Every daily value lies in 38 to 41 MJ/m3 (R8), except possibly a handful of days.
3. **Truncation.** R5 truncation lowers the month's CV by 0 to 0.1, mean about 0.05, so about 0.13%
   mean and under 0.26% max. This is near-certain by arithmetic and is the page's filed prediction.
4. **The stand-in's error.** 39.5 sits ABOVE most LDZ-months: the mean R5 CV across LDZ-months is
   between 39.0 and 39.5. The mean absolute gap between 39.5 and the R5 month CV is 0.2 to 0.6
   MJ/m3 (0.5% to 1.5% of billed gas energy), and the largest single LDZ-month gap is under 1.5
   MJ/m3 (under 4%). So the stand-in over-bills gas energy on average, by under 1.5%.
5. **Spread across LDZs.** In a given month, LDZ CVs differ by under 1.0 MJ/m3 top to bottom
   (the reg 4A cap ties an area's CV to the lowest input plus 1).

A result outside 4 or 5 refutes the stated belief and is written beside it, not over it.

## Result (2 Nov 2026, same session, after the predictions above)

Over the final versions: 13 LDZs x 1,522 gas days, 650 LDZ-months.

1. **Coverage: held.** First gas day 1 Nov 2021 for every area, none missing to 31 Dec 2025.
2. **Range: held, narrowly.** 24 of 19,786 final daily values lie outside 38-41 (lowest 36.0, LDZ(NO)
   and LDZ(NW), Aug 2022, from a republication eight months later; highest 41.3).
3. **Truncation: held.** Mean 0.118%, max 0.249%.
4. **Partly refuted.** The mean R5 month CV is 39.477, inside 39.0-39.5. The mean absolute gap is 0.42
   MJ/m3, inside 0.2-0.6. The largest gap is 1.50 MJ/m3, which is NOT under 1.5 (it is 3.95% of the
   bill's gas energy, under 4%). The claim that the stand-in over-bills on average is right in sign
   and empty in size: +0.07%, with 53% of LDZ-months below 39.5. The error is regional: NO averages
   40.30 and WS 38.93.
5. **Refuted.** Cross-LDZ spread in a month: mean 1.56, max 2.70 MJ/m3, not under 1.0. The belief
   misread reg 4A: the cap ties an area to its own lowest input plus one, not to the other areas.

**Not predicted, found:** the portal keeps every version. Read 5 days after month end, 89 of 650
LDZ-months give a different R5 from the final record (up to 2.2 MJ/m3, SC Nov-Dec 2023), and SC and
WS carry runs of exactly 38.0 that behave like a default. Filed as G7 on the page.
