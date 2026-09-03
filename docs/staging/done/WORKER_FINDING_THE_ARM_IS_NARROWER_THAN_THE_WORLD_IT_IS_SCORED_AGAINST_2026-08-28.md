**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `A48_enterprise_value_is_the_method_not_the_book`

# The pricing arm is electricity-only, the world's switching response is dual-fuel, and the guard's stated reason has drifted

Costing item 3 of
`WORKER_FINDING_THE_METHOD_REACHES_TWO_PERCENT_OF_RENEWALS_AND_THE_PAGE_DIVIDED_BY_THE_WRONG_THING_2026-08-28`:
gas is **357 renewals, 29.5%** of everything the world offers, and the arm cannot touch any of it.
Unlike the other two exclusions this one is a **company** limit, not a baseline-world one, so R13
does not reserve it.

## The guard, and what it says

`company/crm/customer_profitability.py`:

```
UPLIFTABLE_COMMODITY: str = "electricity"
```

with the reason, verbatim: *"gas is priced off a book this policy has never been calibrated
against."*

## What the code now supports, checked one input at a time

The reason names calibration. Every calibration input it could mean is **already commodity-aware**:

| input | state | evidence |
|---|---|---|
| cost-to-serve | takes `commodity`, and its docstring explicitly handles "a gas day" | `saas/cost_to_serve.py::cost_to_serve_for_period(segment, revenue_gbp, commodity, periods)` |
| standing charge | gas rates present for **every** segment (resi, SME, I&C) | `saas/non_commodity.py::STANDING_CHARGE_GBP_PER_DAY` |
| the world's switching response | **calibrated DUAL-FUEL** — `MARKET_SAVINGS_BY_YEAR` is annotated "GBP/yr, **dual-fuel**", DESNZ/Ofgem engagement series | `simulation/market_switching_propensity.py` |
| churn probability | takes no commodity at all | `saas/churn_model.py::churn_probability(bill_shock_count)` |

**The third row is the one that matters and it points the other way.** The world's churn response is
calibrated on the saving a household gets by switching its *dual-fuel* supply. The company's arm can
only re-price the electricity half. So the arm is not matched to a world it was fitted for — **it is
narrower than the world it is scored against**, and every published comparison is an
electricity-only policy being judged by a dual-fuel switching curve.

## Where the constant is actually used

Three sites, and all three take a commodity argument already:

1. `company/pricing/value_based_renewal.py:1251` — the settled-record filter.
2. `:1293` — `cost_to_serve_for_period(..., UPLIFTABLE_COMMODITY, ...)`.
3. `:1323` — `standing_charge_rate(UPLIFTABLE_COMMODITY, segment)`.

Plus the eligibility guard at `customer_profitability.py:247`.

**The mechanical widening is passing the renewal's own commodity through instead of a module
constant.** That is small. It is not the cost.

## What the cost actually is

**The open question is not plumbing, it is whether the uplift POLICY behaves on gas.** The arm
raises margin on accounts whose prior term was unprofitable. Gas margins have a different shape —
seasonal, weather-driven, and settled on a daily rather than half-hourly basis — and nothing has
measured whether "unprofitable prior term" means the same thing there. A policy widened without
that check would price 357 renewals on an inference nobody has tested, and the resulting
comparison would look six times bigger and be exactly as trustworthy as the untested half.

So the cost is **one measurement, not one edit**: run the arm's profitability uplift over the gas
book in DIAGNOSTIC mode — computing what it would have charged without charging it — and compare
the distribution of uplifts against the electricity one. If gas uplifts are the same shape, the
widening is evidenced. If they are wilder, the guard was right for a reason its own comment did not
give.

## Why this is filed rather than built

Widening the arm changes what the company does to 357 renewals and would move every published
figure again, on the same day two of them have already moved. The measurement above is the
precondition and it is cheap; the widening is not the kind of thing to do in the same breath as
discovering that it is possible.

**It also is not urgent in the way it looks.** The 2.07% coverage is a bound on what the A/B can
say, not a defect in what it says. Tripling the surface would improve the instrument's resolution —
which is the same wall `A46` (book depth) and the 17-decision ladder keep hitting — but on a
policy half of which is untested.

## What is NOT claimed

- Not that the guard is wrong. It may be exactly right; what is shown is that **its stated reason
  has drifted from what the code supports**, which is the same class the canon drift check exists
  for (`A45`) — a claim that was true when written and is no longer checked by anything.
- Not that gas uplifts are safe. Nothing here measured them; that is the work.
- Not that the world's dual-fuel calibration is a defect. It matches reality — households switch
  dual fuel. The mismatch is that the company answers with one fuel.

## WORK THIS CREATES

1. **Measure gas uplift in diagnostic mode** and compare the distribution to electricity. Cheap; no
   behaviour change; the precondition for everything below.
2. **If the shapes match**, thread the renewal's commodity through the four sites and re-run. The
   priced surface goes from 25 to roughly 25 + gas-eligible renewals, and every A/B figure is
   restated on the wider surface with its own bound.
3. **Register the guard's reason as a canon claim.** "Gas is priced off a book this policy has never
   been calibrated against" is exactly the shape `canon_claims.yaml` binds: a stated reason with a
   predicate over the code. It drifted silently for as long as it has been true that
   `cost_to_serve_for_period` takes a commodity.

## Still live
