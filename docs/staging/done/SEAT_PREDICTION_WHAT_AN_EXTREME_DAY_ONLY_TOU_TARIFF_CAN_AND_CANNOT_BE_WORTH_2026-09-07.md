**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — A49, the skew not the spread)

# PREDICTION — what an extreme-day-only time-of-use tariff can and cannot be worth

**Written 2026-09-07, BEFORE the instrument that answers it exists.** No concentration figure has
been computed. `docs/observability/tou_extreme_day_concentration.json` does not exist and
`tools/tou_extreme_day_concentration.py` has not been written. Filed separately from the result so
the result cannot be read as a prediction made after its own answer.

## What is established before the run, and is not predicted

From `docs/observability/tou_price_shape_by_episode.json`, landed at c325d0c53:

| | 2016-2020 | 2021-2023 | 2024-2025 |
|---|---|---|---|
| median within-day wholesale ratio | 1.772 | 1.791 | **1.696** |
| p90 within-day wholesale ratio | 3.385 | 3.712 | **6.670** |
| days clearing 2:1 faced, at full pass-through | 2.8% | 7.9%¹ | **14.6%** |
| gross achievable value, £/household/year | 51.36 | 178.59 | 106.93 |
| everyday product, company £/household/year, opt-in | 0.608 | — | **1.391** |

¹ read from the α=1.00 row of the 2021-2023 episode.

The median has FALLEN to the flattest of the record while the p90 has nearly doubled. That is
skew, not spread, and it is the one thing in ten years that has actually moved.

Cost anchor, sourced and already in code: `saas.opex_ledger.CAC_ONE_OFF_GBP_PER_SINGLE_FUEL_CUSTOMER`
= **£27.50**, midpoint of the CMA-era £25–£30 single-fuel PCS commission
(`docs/market_research/B2_CATEGORY6_CAC_ANCHORS.md`). Per-notification and per-event compliance cost:
**nothing in the knowledge layer establishes one.** No figure will be invented for it; it is carried
as a break-even instead.

## The structural result I already hold, and am therefore NOT claiming as a discovery

Company value under either product is `Σ_days saving_d × kwh_d × response_d(α) × (1−α)` over the
days the tariff pays on. The extreme-day product sums a **subset** of the everyday product's days,
and every term is non-negative. So under one response model and one α:

> **extreme(q) ≤ everyday, always, for every q < 100%.**

This is arithmetic, not a finding. It means the whole commercial question is displaced: the
extreme-day product cannot be better on gross value, so it can only be better on **cost avoided on
the days it does not pay**, or on a **called-day attention premium** — a household responding harder
to "tonight matters" than to a standing tariff it has habituated to. Arcturus 2.0 models neither.

I am stating this in advance so that if the instrument reports extreme > everyday at a common α,
that is a **defect in my instrument** and not a result. It is a control on my own code.

## The predictions

**P1 — concentration is real and is a 2024-2025 phenomenon.** The top decile of days by achievable
saving carries **≥ 35%** of 2024-2025's total gross achievable value. Point estimate 40–55%. For
2016-2020 I predict materially less: 25–32%.

**P2 — most of the everyday product's published value is the regression intercept.** Arcturus's
primary constant is −0.011, so a household shown a flat price is credited with a 1.1% peak
reduction (already pinned as an artefact in `tests/tools/test_tou_price_shape_episode.py`). On the
~85% of 2024-2025 days whose faced ratio is near 1, that intercept is essentially the whole
response. I predict **≥ 50%** of the everyday product's £1.391 is intercept, not price response.
Point estimate 55–75%.

**P3 — with the intercept removed, the everyday product falls under £1.00/household/year**, and the
top-decile product then delivers between **40% and 70%** of it.

**P4 — the break-even running cost is under a penny a day.** Value forgone by not paying on the
bottom 90% of days, divided by the days avoided, is **under 1p per household per day**. Point
estimate 0.1–0.4p. Read the other way: the everyday tariff would have to cost more than that, per
household, per day, to run, before dropping to extreme days is worth doing.

**P5 — the attention premium needed is at least a doubling.** For extreme(10%) to match everyday,
called-day response must be multiplied by **≥ 2×**. Point estimate 1.8–3.0×.

**P6 — the extreme days cannot be called from yesterday.** A persistence caller (call tomorrow
extreme iff today was in the top decile) achieves **recall below 30%** on the top decile. Point
estimate 15–25%. We hold no day-ahead auction series, so perfect foresight is the ceiling and
persistence is the skill-free floor; the truth is between them and the instrument must say so
rather than publish the ceiling alone.

**P7 — the payout is not a proposition you can recruit against.** The single biggest calendar year
carries **≥ 25%** of the decade's extreme-day value, and in at least one of the ten years the
top-decile value per household is **less than half** the decade median.

**P8 — neither product clears recruitment.** Payback against the sourced £27.50 CAC exceeds **19
years** for the everyday product and is longer for the extreme one.

## The verdict rule, fixed in advance

- **BETTER** requires one of: (a) a *sourced* per-household-day running cost for the everyday tariff
  above P4's break-even, or (b) a *sourced* called-day attention premium above P5's break-even.
- **MERELY RARER** otherwise: the concentration is real, the product is a strict subset of the
  everyday one, and nothing established closes the gap.
- Neither verdict is allowed to rest on a number invented to fill the slot. If the break-evens land
  in territory nothing in the knowledge layer can speak to, that is a **named gap** and the answer
  is MERELY RARER **with the gap stated**, not a hedge.

**I predict MERELY RARER**, and I expect the interesting part of the answer to be the size of the
break-evens rather than the verdict — a premium of 2× is a research question somebody could go and
settle against NESO's Demand Flexibility Service, which is the real GB product that pays only on
called days. A premium of 40× is not.

## What would refute me

P1 low (concentration under 35%) refutes the premise that the skew is worth a product at all. P4
landing above 1p/household/day would mean the everyday tariff's running cost is plausibly the
binding constraint and the extreme product is a live commercial option. P6 recall above 50% would
mean the days are callable and the attention premium is reachable. Any of those flips the reading.
