**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `A45_the_canon_is_a_standing_subject`

# The standing charge is four declarations, and the one carrying a citation names a quantity the source does not publish

**Found:** 2026-08-31, continuing the domain-constant origin debt after the VAT de minimis
(`WORKER_FINDING_THE_VAT_DE_MINIMIS_WAS_ONE_FUELS_LIMIT_APPLIED_TO_BOTH_2026-08-31.md`). This is the
director's third named example — *"a standing charge that matches neither fuel"* — researched
before anything was changed, and the research says **do not change it yet**.

## What is established, from the published record

**Ofgem, energy price cap unit rates and standing charges, fetched 2026-08-31.** Cap period
**1 October – 31 December 2026**, Direct Debit, GB national average:

| fuel | standing charge |
|---|---|
| electricity | **54.83 p/day** |
| gas | **29.68 p/day** |

Ofgem states the standing charge **varies by region, payment method, fuel and meter type**, and it
is published **per cap period** — it is a four-dimensional quantity, not a number.

## The four declarations in this repository

| where | value | origin |
|---|---|---|
| `company/pricing/tariff_comparison.py` | `STANDING_CHARGE_RESI_P_PER_DAY = 53.0` | comment: *"Ofgem average 2024 (published)"* |
| " | `STANDING_CHARGE_SME_P_PER_DAY = 60.0` | none |
| `company/billing/renewal_engine.py` | `_STANDING_CHARGE_P_DAY` by segment, fallback **61.0** | none |
| `saas/non_commodity.py` | `STANDING_CHARGE_GBP_PER_DAY` — per fuel **and** per segment | none |

Only the last has the right **shape**. None of them has a source.

## The citation is the finding, and it is not what I expected

The earlier note on this (2026-08-30) said 53.0 "is very nearly the dual-fuel sum" of the repo's own
27.0 + 25.0 = 52.0. **Having now read the published record, that reading is one of two available and
neither is established:**

* 53.0 is within 2 p/day of **today's published ELECTRICITY standing charge** (54.83), and
* 53.0 is within 1 p/day of the **sum of this repo's own two per-fuel figures** (52.0).

Both are coincidences until someone shows which quantity the number was taken from, and **that is
the point**: a constant that plausibly matches two different quantities is a constant whose meaning
nobody can recover. Recorded this way rather than repeating the earlier claim, which asserted the
sum reading as if it were established.

**And the comment cites a quantity Ofgem does not appear to publish.** *"Ofgem average 2024"* — the
source publishes standing charges **per fuel**, per region, per payment method, per cap period. A
single cross-fuel "average" is not among them. So this is the class the origin gate explicitly says
it cannot catch, stated in its own docstring: *"a comment naming Ofgem beside a number Ofgem never
published passes here, and no scan can catch that — only reading the source can."* **This is the
first instance found by reading.**

## The deeper problem: no single number can be right, whatever its value

The standing charge **moved by more than a factor of two inside the modelled window** —
`docs/market_research/ofgem_cap_windows.md` records the electricity leg going *"~25 ppd in 2021 to
~45 ppd in 2022"*, and it is 54.83 today. A scalar applied across 2016–2025 is wrong in every year
but at most one, **regardless of which fuel or which year it was taken from.**

`compare_tariffs` is single-fuel by construction — it calls
`sim_interface.get_forward_price("electricity", ...)` and nothing else — so whichever reading is
right, every annual cost it returns carries a fixed error of tens of pounds a year, identically
across all three options it compares. **The ranking is unaffected and every absolute figure is
wrong**, which is the version that survives casual checking longest.

## Severity, measured

**LATENT.** No `site/` feed reads `compare_tariffs`; `company/portal/app.py` is the only non-test
consumer of that neighbourhood and the portal is not served — the sole uvicorn unit is
`background.file_api`. Measured before filing, per the standing correction to the 2026-08-30 VAT
finding.

## What I did NOT do, and why that is the finding rather than a shortfall

**I did not file a commons artefact, and I did not change the constant.**

One cap period is not a series. An artefact holding 2026-Q4 alone would be *read* as the authority
for 2016–2025 the first time someone needed a number — which is precisely how
`STANDING_CHARGE_RESI_P_PER_DAY = 53.0` came to carry the comment it carries. **A one-row authority
is more dangerous than no authority**, because it converts "nobody knows" into "someone checked".

Per the standing rule — *a number you need is a question to research, never a value to pick; if
nothing establishes it, that is a finding to file and the code carries the gap explicitly* — the
gap is filed here and the code is left carrying it visibly rather than being given a fresher
placeholder.

## What is owed, in order

1. **The published standing-charge series, per fuel, per cap period, 2019 onwards** (the cap begins
   1 Jan 2019; before that there is no cap and the question is a different one). Ofgem publishes it
   alongside the unit-rate table this repository already holds as
   `ofgem_default_tariff_cap_windows.json`, whose own `basis` says
   *"standing_charge: EXCLUDED — this is a unit-rate ceiling only"*. **That artefact is the natural
   home and it says so itself.**
2. **Then one authority, fuel-keyed and period-keyed**, that the other three call — and
   `standing_charge_rate()` **refuses an unknown fuel**, the same shape the VAT de minimis repair
   just took.
3. **Then decide whether `company/pricing/tariff_comparison.py` should exist.** It is unreached, it
   is single-fuel while presenting a household bill, and a wrong module nobody calls is cheaper to
   delete than to correct.
