**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a-commons-artefact-cannot-tell-when-its-source-was-revised

# Pre-registration: what divisor does each cap period in v1.31 carry, and can it be corroborated from inside the workbook?

**Written:** 2026-09-07, delivery seat, BEFORE running the comparison in P1 below.
**Subject:** `tools/ofgem_cap_unit_rate_composition.py`, extending to the twelve cap periods
`Default-tariff-cap-level-v1.31.xlsx` carries beyond October–December 2023.

## Why this exists rather than just doing the work

The finding that opened this lane
(`SEAT_FINDING_THE_CAP_COMPOSITION_CITES_A_MODEL_TWELVE_EDITIONS_STALE_...`) states the divisor rule
as **two** bases: 3,100 kWh up to P15a, 2,500 kWh from P15b (January 2026) onwards, sourced from the
note in row 7 of `ElecSingle_Other_Benchmark`. It also states that the four 2026 periods "rest on the
publisher's note alone" because `ofgem_default_tariff_cap_windows.json` stops at 2025-12-31.

Opening the workbook to do the work, two things are visible that the finding did not have:

- **Row 8 of the same sheet** carries a SECOND note, from a decision published 27 May 2026, saying
  the benchmark was revised AGAIN from July 2026 (cap P16b). Row 7's note is therefore itself
  superseded as a complete statement of the rule.
- **`1c Consumption adjusted levels`, rows 6–7**, publishes the mapping as a table:
  `Consumption (MWh) (Defaulted to show latest TDCV)` = 2.5 · `Revised benchmark consumption (MWh)
  Jan 2026 - Jun 2026` = **2.7** · `Revised benchmark consumption (MWh) July 2026 onwards` = 2.5.

So the header cell's 2,500 kWh is the LATEST basis, not the basis from P15b — and a reader who
followed the finding's two-base rule would divide January–June 2026 by 2,500 when the model divides
by 2,700, running 8% high on those two periods. That is a smaller error than the 24% the finding
caught, in the same direction, and it would have been invisible for exactly the same reason: every
share stays right.

## Predictions, fixed before measurement

| # | prediction | confidence |
|---|---|---|
| **P1** | `1c Consumption adjusted levels` restates every period at ONE consumption (its own header says 2.5 MWh, "defaulted to show latest TDCV"). So at GB average, `(1c typical − 1c nil) / (main benchmark − main nil)` should equal `2500 / divisor(period)`: **0.8065** for periods to December 2025, **0.9259** for January–June 2026, **1.0000** for July 2026 onwards. | moderate |
| **P2** | Electricity VAT is **0%**, not 5%, for October 2026 – March 2027 (1a's note, and its `GB average, inc VAT` electricity row is identical to its ex-VAT row while gas carries 5%). A downstream reader converting the published ex-VAT unit rate at a flat 1.05 is wrong for those periods. | high — sighted, not yet checked across the sheet |
| **P3** | The eight periods January 2024 – October 2025 reproduce the published including-VAT cap level to within 0.5% at 3,100 kWh, as the opening finding measured. Re-derived here as a control on my own reader, not as new evidence. | high |
| **P4** | No period the artefact ALREADY publishes moves, at any decimal place the artefact carries, once the per-period divisor is in. All 21 are pre-2026 and all are 3,100. | high |

**P1 is the one that matters.** If it holds, the 2026 divisors are corroborated from a second,
independent place in the publisher's own workbook rather than resting on a prose note — which is what
the opening finding said could not be done. **Named failure mode:** `1c` may instead be a historical
restatement at each period's THEN-CURRENT typical consumption, in which case the ratio is ~1.0
everywhere and the test says nothing. That outcome is not a refutation of the divisor rule; it is the
test being uninformative, and it will be reported as that and not as support.

**If P1 comes back uninformative**, the 2026 periods are published with their divisor's provenance
stamped as the publisher's own consumption table (still a table, not prose) and the artefact says
plainly that no independent corroboration exists for them yet.

## What this does not test

Whether 2,700 and 2,500 are the RIGHT typical consumption values as a matter of policy. That is
Ofgem's decision to make and the model is the primary record of it; the only question here is which
number the model divides each column by.
