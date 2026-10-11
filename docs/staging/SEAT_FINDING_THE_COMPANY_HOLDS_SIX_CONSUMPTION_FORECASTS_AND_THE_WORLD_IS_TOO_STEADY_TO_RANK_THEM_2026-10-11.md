**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`

# The company holds six consumption forecasts per property, not one, and the world is too steady to say which is best

Claim `one-consumption-forecast-per-property-or-several`. This answers **question 2** of the
director's console message of 2026-10-11T04:20Z
(`docs/staging/console/DIRECTOR_CONSOLE_2026-10-11.md`). The predictions were written before any
error was computed and are graded below as written:
`docs/staging/records/SEAT_PREREG_ONE_CONSUMPTION_FORECAST_PER_PROPERTY_OR_SEVERAL_2026-10-11.md`.
No code that sets a DD was changed.

## The answer in four lines

1. **Several.** There are five production forecasts and a sixth behind the customer portal. No
   two consumers share one, except the opening DD and the first estimated bills. Forward CLV
   uses none.
2. **Best against held-back actuals, in this world:** the trailing twelve months of **settled**
   kWh, which is the electricity hedge's figure. Its median error over the next year is 0.5%
   for electricity and 2.9% for gas on the premises where the world varies at all. **But that
   ranking is mostly the world's**, not the forecasts'. The world's households use almost
   exactly the same amount every year. The median change from one year to the next is 0.08%
   for electricity and 0.43% for gas, against **14.7%** in the published NEED 2026 record
   (`docs/market_research/how_far_a_settled_eac_sits_from_next_years_use.md`). In a world that
   repeats itself, "last year" wins by construction. **I cannot yet say which level forecast is
   best for a real household.**
3. **What the world CAN grade is the seasonal shape and the cost of estimated bills, and both
   matter.** Unshaped twelfths under-forecast gas winter use by 30% and over-forecast summer
   use by 76–79%. The published profile cuts the winter error to 2–8% but still misses summer
   by 12–21%. Every forecast built on billed kWh carries the estimated months: on fabric
   electricity, billed kWh has a median 4.2% annual error against 0.5% for settled kWh.
4. **They should be one.** The recommendation is below. In short: one per-property forecast
   with an annual level taken from **actual reads** (the industry's annualised advance) and the
   published seasonal shape at normal weather, read by DD opening, DD review, estimated bills,
   hedge volume and CLV alike.

## 1. The consumers and the forecast each one actually calls

Traced by reading the call chains, 2026-10-11, at `5b9c698a7`.

| # | consumer | forecast it calls | annual level from | seasonal shape |
|---|---|---|---|---|
| F1 | **Opening DD** (`company/interfaces/dd_review_outcome.opening_monthly_amount` → `company/billing/annual_consumption_estimate.estimate_annual_consumption` / `opening_monthly_dd_gbp`), and **estimated bills before the first read** (`unread_month_estimate.opening_estimate_kwh`) | registry EAC/AQ, else Ofgem TDCV band | registration, never updated | none in the DD (÷12); published profile on the estimated bill |
| F2 | **Estimated bills** after the first read (`company/billing/monthly_bill_assembly` → `unread_month_estimate.estimate_unread_kwh`), so also the period-end **estimated billing outstanding** (`saas/ledger.estimated_billing_outstanding`) | last 3 actual reads ÷ published profile weight | 3 months of reads | DESNZ monthly profile |
| F3 | **Annual DD review** (`company/billing/dd_review_runner.run_annual_reviews` → `dd_review._recommended_monthly`; `simulation/dd_balance_book.reviewed_standing`, default rule `last_year_spend`) | last 12 months' **billed** spend (£), or billed kWh at new rates | last 12 billed months, estimates included | none (÷12) |
| F4 | **Electricity hedge volume** (`simulation/run_phase2b._company_eac_estimate` → `company/trading/hedge_decision`) | last 12 months' **settled** kWh; first term: declared EAC × household multiplier | last 12 settled months | none (annual × term fraction) |
| F5 | **Gas hedge volume** (`simulation/run_phase2b`, gas leg) | registry AQ × `household_demand_register.gas_eac_multiplier_for_date` | registration, never updated from gas reads | none |
| F7 | **Customer portal** (`company/portal/app.py` → `consumption_forecast.forecast_annual_cost` → `eac_calibration.calibrate_eac`) | 2 years' billed kWh, annualised | 24 billed months | fixed 30/22/18/30 by quarter |
| — | **Forward CLV** (`company/analytics/forward_clv.py`) | **no consumption forecast**: it projects each account's shrunk mean monthly margin × survival | — | — |
| — | **Unbilled revenue** | **not computed**: `saas/ledger` returns `unbilled_revenue_gbp: None` with a named reason. `company/finance/revenue_accruals.RevenueAccrualsLedger` has no caller. | — | — |

Also found and not used by any run consumer: `company/market/seasonal_demand.py` (a portfolio
demand forecast with no caller).

**So one property has up to five answers about the same twelve months:**
- the DD is opened on the registry figure and reviewed on last year's bills;
- the bills are estimated from three reads;
- the hedge buys on last year's settled volume (electricity) or the registry AQ (gas);
- the portal shows a two-year average.

## 2. Graded against held-back actuals

**Run:** `docs/reports/run_output_latest.json` (producing commit `7379375f6`), 980 billed
customers, residential only.

**Truth:** each month's `true_consumption_kwh`. It is used only to grade.

**Anchor:** every 1 January from 2017 to 2024 with 12 full months either side. Each forecast
predicts the next 12 months.

**Intervals:** 95% bootstrap, resampling properties. Pinned premises are counted separately,
because the world pins their annual figure to the declaration (§3).

**The premises where the world varies** (electricity `fabric_physics`, gas `fabric_seasonal_split`):

| forecast | fuel | n (props) | median \|annual error\| | median bias | winter bias / \|err\| | summer bias / \|err\| | within ±10% |
|---|---|---|---|---|---|---|---|
| F1 opening | elec | 282 (282) | 4.8% [4.3, 5.3] | +4.8% | +11.5 / 12.4 | −5.8 / 9.1 | 89% |
| F1 opening | gas | 121 (121) | 12.1% [9.3, 14.9] | −0.9% | +1.5 / 12.6 | −13.4 / 21.2 | 46% |
| F1 registry, held | elec | 586 (172) | 0.7% [0.6, 0.9] | +0.3% | +10.0 / 10.5 | −9.7 / 10.5 | 98% |
| F1/F5 registry, held | gas | 202 (68) | **9.8%** [7.7, 12.9] | +0.3% | +1.8 / 11.0 | −13.6 / 19.0 | 51% |
| F2 3 reads, profiled | elec | 577 (169) | **6.3%** [5.7, 6.9] | −0.6% | +7.0 / 10.0 | −8.7 / 10.9 | 75% |
| F2 3 reads, profiled | gas | 200 (67) | 7.5% [6.7, 9.3] | −1.5% | +1.8 / 8.3 | −13.5 / 17.2 | 61% |
| F3 billed 12m | elec | 586 (172) | 4.2% [3.5, 4.7] | 0.0% | flat −9.9 / profiled +8.4 | flat +12.3 / profiled −9.0 | 83% |
| F3 billed 12m | gas | 202 (68) | 7.6% [6.0, 8.9] | −0.2% | flat −30.2 / profiled +4.2 | flat +79.3 / profiled −11.9 | 65% |
| F4 settled 12m | elec | 586 (172) | **0.5%** [0.4, 0.6] | 0.0% | flat −10.8 / profiled +9.3 | flat +13.8 / profiled −10.2 | 99% |
| F4 settled 12m | gas | 202 (68) | **2.9%** [2.5, 3.4] | −0.1% | flat −30.2 / profiled +4.0 | flat +76.0 / profiled −11.8 | 87% |
| F7 portal | elec | 414 (130) | 3.7% [2.8, 4.3] | +0.4% | +14.9 / 16.2 | −15.7 / 16.5 | 91% |
| F7 portal | gas | 134 (53) | 6.8% [6.1, 8.5] | +2.5% | −16.5 / 17.2 | +55.4 / 55.4 | 64% |

Winter is October to March and summer is April to September. "Flat" is the annual figure ÷ 12,
which is how F3 and F4 are actually consumed. "Profiled" is the same level spread by the
published DESNZ monthly profile, shown to separate the level error from the shape error.

**The pinned premises** (electricity `legacy_pc1_rescaled`, gas `population_70_30_split`):
- F4 is **0.0%** for both fuels and F3 is 1.4% (electricity) and 5.2% (gas).
- F1 held at the registry figure is bimodal: exact for most premises, about 20% off for some.
  Its median 7.4% has the interval [0.0, 20.0] for electricity. I have not traced why.
- The full table is reproduced by the script in the appendix with `pinned`.

### Prediction against result

| # | predicted | result |
|---|---|---|
| 1 | more than one forecast | **Held.** Five in production plus the portal. Known from the trace, so not a test. |
| 2 | F4 ≈ F3 < F7 < F2 < F1 ≈ F5, F4 at 5–10% | **Order partly held, magnitudes refuted.** On fabric electricity: F4 0.5 < F1-held 0.7 < F7 3.7 < F3 4.2 < F2 6.3. F7 beat F3, and **F1 held at the registry is second best, not worst**, because the world draws a fabric premise's volume from the declared EAC (`_base_profile_eac`'s own docstring calls this self-referential and says the repair is owed). On gas, F1/F5 is worst (9.8%), as predicted. F4 at 0.5% and 2.9% is far below the predicted 5–10%. The cause is §3, not forecasting skill. |
| 3 | F1 over-forecasts on the median, F2 unbiased | **Mixed.** F1 at opening over-forecasts electricity by +4.8% [4.3, 5.3] and is unbiased on gas. F2 is unbiased on electricity and −1.5% on gas. |
| 4 | flat twelfths under-forecast gas winter by >30% and over-forecast summer by >50%; profile cuts winter to <15% | **Held.** Flat: −30.2% winter, +76% to +79% summer. Profiled winter error is 2–8%. Summer stays −12% to −21% under the profile, so the world's gas summer is heavier than DESNZ's profile. That is the same shape as the open season finding `SEAT_FINDING_A_GAS_HOMES_SEASON_MISS_IS_THE_WINTER_AND_LIGHTING_IS_THE_ONE_TERM_OFF_ITS_SOURCE_2026-10-09.md`. |
| 5 | gas worse than electricity for every forecast | **Held** on the fabric subset for every forecast. |
| 6 | best = trailing actual year at normal weather with the published shape; they should be one | **Level: cannot yet tell** (§3). **Shape and unification: held**, see the recommendation. |

## 3. Why the ranking is mostly the world's: year-on-year change is about 30–180× too small

The median absolute change in a property's true calendar-year consumption between consecutive
years in the same run:

| demand provider | fuel | year pairs | median \|change\| | p90 |
|---|---|---|---|---|
| `legacy_pc1_rescaled` | elec | 548 | **0.01%** | 0.03% |
| `fabric_physics` | elec | 586 | 0.51% | 2.88% |
| `population_70_30_split` (and unlabelled) | gas | 332 | **0.00%** | 0.43% |
| `fabric_seasonal_split` | gas | 202 | 2.86% | 10.85% |
| **published: NEED 2026, all dwellings, 2016→2024** | elec | 330,884 | **14.7%** | 58% |
| published: NEED, 2021→2022 | elec | 41,989 | 16.7% (median ratio 0.923) | 59% |

Two cautions on that comparison:
- **The NEED spread bundles more than household change.** It also includes change of occupier,
  EAC↔AA transitions and rounding (see the knowledge page). So 14.7% is an upper reference for
  household change, not a target.
- **The gap is still at least an order of magnitude.** The world shows no 2022 demand response
  at all (median change in 2022 is 0.00% for both fuels), against a published median ratio of
  0.923. About half the book is pinned to its declaration every year.

**What follows for this question:**
- Any trailing-year forecast scores near zero here. A real one would carry an irreducible error
  of the order of the published spread.
- The F3/F4/F7 differences (≤4 points) would be swamped in reality.
- This is a **fidelity finding about the world**, filed here and handed on as a world item. It
  is decided blind to company results under the baseline/curriculum split. It is not a reason
  to change any forecast.

## 4. Two things found on the way

**(a) The electricity hedge reads volume the company never read.** This is a wall question and
needs the interface steward's judgement before anyone acts on it.
- `_company_eac_estimate` sums the **settled** kWh for the 12 months before the term. On a
  sample of 2016–17 renewals it equalled the true total exactly (C5: company 17,436, true
  17,436, billed 17,333).
- That held even where 6–11 of the 12 months were billed as **estimates**. In this run 79% of
  traditional-meter months are estimated (24,495 of 31,120).
- A real supplier's NHH settlement for unread days is EAC-profiled, not the household's actual
  use. Over a read-bounded year the meter advance does reveal the total, so the leak is the gap
  between the calendar window and the read window. Its size is the F3-against-F4 gap above:
  about 4 points on fabric electricity.
- The first-term fallback multiplies the declared EAC by
  `household_demand_register.eac_multiplier_for_date`, which follows the household's own EV,
  solar and heat-pump assets.
- The gas leg's AQ multiplier is EPC-banded.
- Neither multiplier obviously crosses `company/interfaces/sim_interface.py`.

**(b) The published demand-estimation error grades the past against itself.**
- `demand_estimation_log.error_pct` (median −0.07% in this run) compares `company_eac`, the
  trailing settled year, with `true_eac`, the mean annual settled consumption to date
  (`_derive_eac_from_settlement`). Both are backward-looking reads of the same fold.
- `tools/generate_dashboard_data.py` publishes it as `demand_estimation_annual`. It measures
  how far last year's settled figure sits from the run-average settled figure, which is not
  forecast accuracy.
- The held-back version is §2's F4 row.

## Recommendation: one forecast

**One per-property forecast object, owned by billing and read by all five consumers:**
- **Level:** the industry's own method. Annualise the consumption between two actual reads at
  least six months apart (an annualised advance, against the published profile weight, as
  `estimate_unread_kwh` already does for three months). Where no such pair exists, fall back to
  the registry EAC/AQ (F1's ladder, SLC 27.15's ordering).
  - This is F4's level made observable. It replaces F2's three-read window, which is the worst
    learned forecast here (6.3% and 7.5%).
- **Shape:** the published monthly profile at seasonal normal. It is already in
  `unread_month_estimate.MONTHLY_SHARE_OF_ANNUAL_USE`. The world's gas summer is heavier than
  that profile, and which of the two is right is the open season finding's question.
- **Consumers:**
  - the DD (opening and review) prices the next 12 months of that forecast, as the director
    specified in question 2, instead of last year's spend;
  - estimated bills use the same level and shape;
  - the hedge buys the same volume through a seam call, instead of reading the settled fold in
    `simulation/`;
  - forward CLV can value volume against it, instead of extrapolating margin alone.

**What would change the recommendation:** a world with published-scale year-on-year variation
in which the registry or a longer window beats the trailing actual year. That is the world item
below, and the grading script reruns unchanged on its output.

## What is handed on

- **World item (W2, fidelity):** give the pinned providers (`legacy_pc1_rescaled`,
  `population_70_30_split`) year-on-year variation, and check the fabric premises' 2022
  response, against NEED's published year-on-year distribution. Then re-run the appendix
  script. This is decided blind to company results.
- **Interface-steward question:** finding 4(a).
- **Design:** the payment-plan design (question 3) should take its consumption from the single
  forecast above. Building it is the design's first slice, after the knowledge page the
  director's addendum requires.

## Appendix: the grading script

Run from a worktree at `5b9c698a7`:
`python3 grade.py <run_output.json> {all|fabric|pinned}`.

It reads the run output only. The company functions it calls are
`unread_month_estimate.estimate_unread_kwh` and `MONTHLY_SHARE_OF_ANNUAL_USE`.

```python
"""Grade each consumption forecast the company holds against held-back actual 12-month consumption."""
import json, random, statistics as st, sys, collections
from datetime import date
sys.path.insert(0, ".")
from company.billing.unread_month_estimate import estimate_unread_kwh, MONTHLY_SHARE_OF_ANNUAL_USE

d = json.load(open(sys.argv[1]))
SUBSET = sys.argv[2] if len(sys.argv) > 2 else "all"
reg = d.get("opening_registry_kwh_by_customer") or {}
prov = d.get("demand_provider_by_customer") or {}
gprov = d.get("gas_shape_provider_by_customer") or {}
def keep(cid, f):
    p = prov.get(cid) if f == "electricity" else gprov.get(cid, gprov.get(cid[:-1]))
    return SUBSET == "all" or (SUBSET == "fabric") == (p in ("fabric_physics", "fabric_seasonal_split"))
series, fuel = collections.defaultdict(dict), {}
for b in d["bills"]:
    if b.get("segment") != "resi":
        continue
    ps = date.fromisoformat(b["period_start"][:10])
    series[b["customer_id"]][(ps.year, ps.month)] = b
    fuel[b["customer_id"]] = b["commodity"]
def true_kwh(b):
    return b["true_consumption_kwh"] if b.get("true_consumption_kwh") is not None else b["total_consumption_kwh"]
def months(y, m, n):
    out = []
    for _ in range(n):
        out.append((y, m)); m += 1
        if m == 13: y, m = y + 1, 1
    return out
def back(y, m, n):
    out = []
    for _ in range(n):
        m -= 1
        if m == 0: y, m = y - 1, 12
        out.append((y, m))
    return list(reversed(out))
WINTER = {10, 11, 12, 1, 2, 3}
Q7 = {1: .30, 2: .30, 3: .30, 4: .22, 5: .22, 6: .22, 7: .18, 8: .18, 9: .18, 10: .30, 11: .30, 12: .30}
def prof(f, ym):
    return [MONTHLY_SHARE_OF_ANNUAL_USE[f][m - 1] for _, m in ym]
rows = []
def add(name, f, cid, annual, share, nt, ym):
    if annual is None or annual <= 0:
        return
    w = lambda xs, win: sum(x for x, (_, m) in zip(xs, ym) if (m in WINTER) == win)
    rows.append((name, f, cid, annual, sum(nt), w([annual * s for s in share], True), w(nt, True),
                 w([annual * s for s in share], False), w(nt, False)))
for cid, s in series.items():
    f = fuel[cid]
    if not keep(cid, f):
        continue
    first = sorted(s)[0]; ym = months(*first, 12)
    if all(k in s for k in ym) and reg.get(cid):
        add("F1_opening", f, cid, float(reg[cid]), prof(f, ym), [true_kwh(s[k]) for k in ym], ym)
    for y in range(2017, 2025):
        prev, nxt, prev24 = back(y, 1, 12), months(y, 1, 12), back(y, 1, 24)
        if not all(k in s for k in prev + nxt):
            continue
        nt, p, flat = [true_kwh(s[k]) for k in nxt], prof(f, nxt), [1 / 12] * 12
        if reg.get(cid):
            add("F1_registry_static", f, cid, float(reg[cid]), p, nt, nxt)
        act = [k for k in sorted(s) if k < (y, 1) and s[k]["billing_basis"] == "actual"][-3:]
        win = [(date.fromisoformat(s[k]["period_start"][:10]), date.fromisoformat(s[k]["period_end"][:10]),
                s[k]["total_consumption_kwh"]) for k in act]
        if win:
            add("F2_three_reads_profiled", f, cid, estimate_unread_kwh(f, win, date(y, 1, 1), date(y, 12, 31)), p, nt, nxt)
        f3 = sum(s[k]["total_consumption_kwh"] for k in prev); f4 = sum(true_kwh(s[k]) for k in prev)
        for nm, v in (("F3_billed_12m", f3), ("F4_settled_12m", f4)):
            add(nm + "_flat", f, cid, v, flat, nt, nxt); add(nm + "_profiled", f, cid, v, p, nt, nxt)
        if all(k in s for k in prev24):
            add("F7_portal_2y_quarters", f, cid, sum(s[k]["total_consumption_kwh"] for k in prev24) / 2,
                [Q7[m] / 3 for _, m in nxt], nt, nxt)
pct = lambda p, a: 100 * (p - a) / a if a > 0 else None
def boot(per, stat, n=1000, seed=7):
    rnd, cids = random.Random(seed), list(per)
    v = sorted(stat([x for c in (rnd.choice(cids) for _ in cids) for x in per[c]]) for _ in range(n))
    return round(v[int(.025 * n)], 1), round(v[int(.975 * n)], 1)
for name in sorted({r[0] for r in rows}):
    for f in ("electricity", "gas"):
        per = collections.defaultdict(list)
        for r in rows:
            if r[0] == name and r[1] == f and r[4] > 0 and r[6] > 0 and r[8] > 0:
                per[r[2]].append((pct(r[3], r[4]), pct(r[5], r[6]), pct(r[7], r[8])))
        xs = [x for v in per.values() for x in v]
        if not xs:
            continue
        mae = lambda z: st.median(abs(x[0]) for x in z)
        print(name, f, len(xs), len(per), "|ann|", round(mae(xs), 1), boot(per, mae),
              "bias", round(st.median(x[0] for x in xs), 1),
              "win", round(st.median(x[1] for x in xs), 1), round(st.median(abs(x[1]) for x in xs), 1),
              "sum", round(st.median(x[2] for x in xs), 1), round(st.median(abs(x[2]) for x in xs), 1),
              "<=10%", round(sum(abs(x[0]) <= 10 for x in xs) / len(xs), 3))
```
