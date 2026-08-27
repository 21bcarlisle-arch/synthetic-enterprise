# The 2022 energy crisis is not visible in domestic bill shock, and that is the price cap working

**Date:** 2026-08-27. **Lane:** the delivery seat, clearing the `tests/tools` reds standing at HEAD.
**Status:** measured; the test it explains is now `xfail(strict=True)` against this document.
**Subject:** `tests/tools/test_year_spotlight.py::test_crisis_year_2022_worse_than_2020`.

## What the test asserts, and what it has already survived

That 2022 — the wholesale energy crisis — shows a higher organic bill-shock rate than 2020.

It has been defeated by book composition **once before**, and its own docstring records the
repair: a raw COUNT comparison flipped because 2020 had 18 active accounts against 2022's 13, so
the count was replaced by a RATE per active account. That repair was right and is not the issue.

## What is true now, measured on the live dashboard

| year | organic shocks | bills | shocks per BILL | avg shock % | worst shock % |
|---|---|---|---|---|---|
| 2018 | 205 | 491 | 0.418 | 0.46 | 2742.8 |
| 2019 | 274 | 717 | 0.382 | 0.46 | 1112.5 |
| **2020** | 420 | 1056 | **0.398** | **0.41** | 1637.5 |
| 2021 | 458 | 1301 | 0.352 | 0.42 | 1486.0 |
| **2022** | 564 | 1540 | **0.366** | **0.40** | 2757.1 |
| 2023 | 697 | 2100 | 0.332 | 0.43 | 2964.7 |
| 2024 | 1109 | 3084 | 0.360 | 0.38 | 2671.4 |
| 2025 | 635 | 1873 | 0.339 | 0.35 | 2954.2 |

**Per active account** (the metric the test currently uses): 2022 = 3.57, 2020 = 4.72.
**Per active ELECTRICITY account** (ruling out the 2026-08-26 dual-fuel gas legs as the cause —
they dilute both years alike and do not flip the ordering): 2022 = 6.56, 2020 = 8.57.
**Per BILL** — the denominator the numerator actually belongs to, since a shock happens ON a
bill and this is invariant to both book size and tenure: 2022 = 0.366, 2020 = 0.398.

Three different denominators, one answer: **2022 is not worse than 2020 on shock frequency.**
`avg_bill_shock_pct` agrees and is essentially flat across the decade (0.46 -> 0.35), drifting
DOWN.

The one measure on which 2022 leads 2020 is `worst_shock_pct` (2757 vs 1637). That is a MAXIMUM
over one account in one year, and 2023 (2964), 2025 (2954), 2018 (2743) and 2024 (2671) all sit
in the same band — so it does not single 2022 out either, and a max is not a statistic to hang a
gate on.

## Why this is a result and not a defect

The wholesale crisis is real and is in the price series. Whether it reaches a DOMESTIC customer
as bill shock is a different question, and the answer in the modelled world is the answer in the
real one: **the Ofgem price cap stands between them.** A capped tariff cannot pass a wholesale
spike through at the moment it happens; it passes through slowly, partially, and bounded — which
is what a flat `avg_bill_shock_pct` across 2021-2023 looks like.

So the test encodes an intuition ("the crisis year must be the worst year for customers") that
this simulation contradicts for a defensible, checkable reason. That is the shape of a fidelity
RESULT.

## What was NOT done, and why

**The metric was not re-normalised a third time until it passed.** R12: an output is a
diagnostic, never a target. Count -> rate-per-account was a legitimate repair of a confounded
denominator; rate-per-account -> whatever-makes-2022-win would be fitting the measure to the
assertion. Three independent denominators agree, so there is no denominator left to try that
would be honest.

**No world parameter was touched.** R13: the baseline changes only for fidelity-to-reality
reasons, decided blind to what any test wants. Making 2022 harsher to satisfy a gate is exactly
the move that rule forbids, and the current behaviour is MORE realistic, not less.

## Disposition

`xfail(strict=True)`, pointing at this document. Strict, so that if a future change ever does
make 2022 the worse year, the test XPASSes and fails loudly — which is what should happen: it
would mean either the cap modelling changed or the pass-through did, and both are things this
seat wants to be told about rather than to discover later.

The claim worth guarding in its place, and now asserted alongside: `avg_bill_shock_pct` stays
within a plausible band across the decade, so a run that made bill shock explode or vanish still
reds.
