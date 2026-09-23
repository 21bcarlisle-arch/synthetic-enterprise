**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — both legs cleared: the larger floor was already on disk, and our own cap cost the funnel a third of its supply

**Filed:** 2026-09-22. Drawn as Lane 0 delivery,
`the-two-legs-that-bind-the-arm-are-nine-seeds-and-one-censored-funnel`. This works the prediction
filed in §8 of `SEAT_RESULT_THE_TWENTY_EIGHT_CUSTOMER_YEAR_SHORTFALL_IS_A_COIN_FLIP_AND_FOUR_OF_TEN_YEARS_WERE_BOUND_BY_OUR_OWN_PROSPECT_CAP_2026-09-22.md`.
**Both clauses are CONFIRMED**, and the marking is recorded beside the prediction in §10 of that
file, not over it.

## 0. Neither run needed to be run the way the item said

The item asked for two runs and told me to launch them detached because a job started from a
bounded tick dies with it. Both turned out to be cheap, for different reasons, and the reasons are
the finding:

* **The larger floor already exists on disk.** It has for five days. Nothing had re-priced the
  requirement on it.
* **The funnel does not need settling to be measured.** The 88-minute, 13.9 GB run everyone reaches
  for measures what this machine could SETTLE. The supply question is answered by
  `plan_growth_campaign`, which is a pure resolver and takes **1.7 seconds**.

Measured headroom before starting, as instructed: 18,006 MB available of 24,032 MB total, with
`process_run_complete` at 983 MB and a gate pytest at 765 MB. Neither leg needed any of it.

## 1. LEG ONE — the floor at more than nine seeds. Clause one CONFIRMED.

`CURRENT_WORLD_NOISE_FLOOR_PATH` — the family the requirement is computed from — is still the
**nine**-seed artefact of 2026-09-09. But `NOISE_FLOOR_PATH`, the constant the page's own error bar
uses, has pointed at an **eighteen**-seed family since 2026-09-17. Same world `39a192ce04c1eda8`,
same clock, same redraw mode, folded by the sanctioned `tools/fold_noise_floor_family.py`.

**One page, one question, two sample sizes, with the smaller one under the figure that gets
differenced.** That is the same defect `CURRENT_WORLD_NOISE_FLOOR_PATH`'s own comment block records
having fixed once already, when it moved 3 → 9 in September: *"Two blocks on one page answering one
question at two sample sizes, with the wider-sampled one in the flattering position."* It happened
again, in the same direction, and the block that records the lesson is the block it happened to.

The requirement is the squared coefficient of variation of the floor family, `V/c²`, times the
book's 1,122 customer-years — algebraically `n/t²`. Priced on each family on disk:

| family | n | mean | sd | t | p | point | 95% interval |
|---|---|---|---|---|---|---|---|
| `..._20260909b` — **what the requirement publishes** | 9 | −1,078.17 | 1,810.50 | 1.7865 | 0.112 | 3,163.9 | [670, **∞**] |
| `..._folded18_20260917` — pooled two arms | 18 | −624.13 | 1,472.89 | 1.7978 | 0.090 | 6,248.6 | [1,382, **∞**] |
| `..._folded18_single_arm_20260917` — **`NOISE_FLOOR_PATH`** | 18 | −959.78 | 1,631.80 | **2.4954** | **0.023** | 3,243.3 | [957, **179,880**] |

Row one reproduces the published 3,163.87 exactly, which is what establishes that this is the right
instrument and not a second implementation of it.

**Clause one said the point estimate would move by less than 2× and the 97.5% end would come back
finite for the first time. Both hold on the single-arm family:** the point moves 3,163.9 → 3,243.3,
a factor of **1.025**, and the upper end is finite at 179,880 customer-years (a 200,000-draw
parametric bootstrap on the producer's own iid-normal model puts it at 66,368). The centre's sign is
determined at 18 draws — p = 0.023 against 0.112 — and that is the whole mechanism: a requirement
divided by a centre whose interval straddles zero has no upper end, and this centre's no longer
does.

**The unflattering half, recorded because it is the half that would not survive a re-run.** On the
POOLED eighteen the upper end stays infinite and the point moves to 6,248.6 — a factor of 1.98,
still under 2× but only just, and in the opposite direction. So "finite" is a property of the
single-arm family and not of eighteen seeds. The single-arm family is the sanctioned one — it is
what `NOISE_FLOOR_PATH` names, and the pooled one is refused elsewhere on the page for pooling two
value arms — so the answer stands, but it stands on which family, not on how many draws.

**And finite is not useful.** 179,880 customer-years against a capacity of 1,200 is an upper end
that excludes nothing. The reason the comparison was a coin flip has not gone away: under the
producer's own model, at 18 single-arm seeds, the requirement still exceeds the control funnel's
supply in **50.1%** of draws. Clause one is confirmed and it does not rescue the claim it was
filed under.

**A 36-seed run was not launched, and that is a judgement, not an omission.** The 12-seed `next12`
family — same world, same mode — replicates this family's LEVEL and refutes its WIDTH: sd 5,398 vs
1,631, F = 10.94 on df (11,17), p = 2.3e-05. The sign here rests entirely on the width. More seeds
**on this instrument** cannot settle a disagreement **between two instruments**; the owed run is the
one-variable one this repo already names (the twelve at `4e7938f673`), and 26 hours of the same
instrument would buy a tighter interval around a width that is itself contested.

## 2. LEG TWO — the funnel with our cap lifted. Clause two CONFIRMED.

`tools/prospect_cap_probe.py`, landed with this. It passes `prospects_per_year` as an argument and
never writes the constant, because which world the company lives through is the director's. It
calls `plan_growth_campaign` and not `live_population._resolve_campaign`, because the latter writes
`docs/observability/book_growth_campaign.json` — the shared tree, while other lanes read it.

**The control arm reproduces the campaign record on disk exactly** — 500 funnel wins, 2,368.0
customer-years, the same four prospect-bound years — and the artefact carries that comparison as
`control_reproduces_the_campaign_record: true`. Without it no difference below is attributable to
the cap rather than to the harness.

| cap | funnel wins | supply (cy) | years bound by OUR cap | what binds instead |
|---|---|---|---|---|
| **400 (shipped)** | 500 | 2,368.0 | **4** | 4 mandate, 2 market |
| 500 | 597 | 2,665.9 | 3 | |
| 600 | 656 | 2,829.7 | 2 | |
| **800** | 731 | 3,019.1 | **0** | 6 mandate, 2 market, 2 capital |
| 1,200 | 790 | 3,258.7 | 0 | |
| 4,000 | 816 | 3,592.8 | 0 | 7 mandate, 3 capital |

**The single cleanest sentence in this document: at a cap of 800 our own instrument binds ZERO
years.** Every remaining constraint is a commercial result — the supplier's own growth mandate, the
real GB switching rate in 2022 and 2023, and capital. The cap did not merely understate four years;
it was the binding constraint on 40% of the record, and removing it hands all four back to the
world.

Supply saturates: beyond ~800 the funnel is reaching into affordable quotes it was never short of,
and 10× the cap buys 51.7% more supply, not 10×.

**Did it clear the top of its own current interval?** The prediction named 3,423 customer-years.
That number is the top of the control's exact-Poisson count interval ([457.1, 545.8] wins) carried
at **6.271 cy/win**, and here the item's own arithmetic has to be restated before it can be used —

> **Two estimators of one quantity, on one tree, 24.5% apart.** "The funnel's whole demand" has two
> figures. `customer_years_all_wins_would_cost` is a **projection** off a run that settled 81 of
> 500 wins: **2,368.0** (4.736 cy/win). `customer_years_committed` from the one run that actually
> settled the whole funnel, at budget 3,400, is a **measurement**: **3,135.5** (6.271 cy/win). Both
> live in `docs/observability/settlement_ceiling_slope_20260921.json`, 767 customer-years apart, one
> called `campaign_demand_customer_years` and the other `funnel_supply_customer_years`. The
> published comparison used the measurement; the record on disk carries the projection.

So the clause is answered on **both** rulers, like for like, and clears on both:

| ruler | control supply | top of its Poisson interval | first cap that clears | supply at 800 |
|---|---|---|---|---|
| projection (4.736 cy/win) | 2,368.0 | **2,585** | **500** (2,665.9) | 3,019.1 |
| measurement (6.271 cy/win) | 3,135.5 | **3,423** | **500** (3,743.8) | 4,584.1 |

A 25% lift clears it on either ruler. **Clause two is confirmed, and `prospect_ceiling_statement` —
which said those years "understate what this supplier would have done" — is vindicated rather than
re-opened.** The direction of the projection's error makes the finding conservative: the projection
reads 24.5% LOW against the only measurement, so the lifted supply is if anything understated.

## 3. What this does to the thesis's acceptance test

The published claim is that the book needed to sign the per-customer selection arm cannot be built.
On the numbers now on the record, with our own cap gone and the floor at the sample size the page's
own error bar already uses:

| | customer-years |
|---|---|
| requirement, point (18 single-arm seeds) | 3,243.3 |
| supply, cap lifted to 800, measurement ruler | 4,584.1 |
| supply, cap lifted to 4,000 | 5,117.1 |

P(requirement > supply) falls from **0.501** at the shipped cap to **0.345** at 800 and 0.306 at
4,000. **That is no longer a coin flip, and it has moved to the side the published sentence denies.**

It is still not a demonstration that the book can be built, and this document does not claim one.
It establishes something narrower and sufficient for the next item: the comparison that produced
"the answer is NO" was made between a requirement priced on the smaller of two floors and a supply
figure censored by our own instrument in four of ten years, and when both are repaired the
inequality points the other way most of the time. **The public surface still states it as settled.**

## 4. What was deliberately not changed

* **`PROSPECTS_PER_YEAR` is untouched at 400.** The probe reports what a lift would buy; it is not
  this item's to change the world, and a diagnostic that edits the baseline is the wall.
* **`CURRENT_WORLD_NOISE_FLOOR_PATH` is untouched at nine seeds.** Moving it to eighteen would
  re-price a published figure inside a turn whose subject was measuring it, and the same comment
  block that records the 3 → 9 move records that moving a floor constant alone is a defect in one
  of its two directions. It is the next item and it is named as one below.
* **`tools/generate_value_arms_data.py` is untouched.** Its working copy in this tree is dirty with
  another lane's hunks (86+/127−, over the RSS-ceiling docstring). Committing it inside this
  pathspec would carry their work inside mine.

## 5. What is owed next, ranked

1. **Move `CURRENT_WORLD_NOISE_FLOOR_PATH` to the eighteen-seed single-arm family, or state in the
   artefact why the requirement is priced on nine while the error bar beside it uses eighteen.**
   One of those two is owed; silence is not.
2. **`site/data/value_arms.json` still publishes `what_is_not_established` saying the answer "is NO:
   2.82x this book is 3,164 customer-years against a capacity of 1,200".** That is an unqualified
   claim on a public surface, resting on a point estimate whose interval is [957, 179,880] and on a
   supply figure this document shows was censored. It was already named as "the next item and the
   one that matters" before this run; it is more wrong now, not less.
3. **Give the funnel's demand ONE home.** 2,368.0 and 3,135.5 are the same quantity under two
   names in one artefact. A reader has no way to know which one a downstream sentence used.

## 6. Reproduction

```bash
python3 -m tools.prospect_cap_probe          # -> docs/observability/prospect_cap_probe.json
```

```python
import json, math
from scipy import stats, optimize
BOOK = 1122.0
for p in ("value_cycle_ab_s1_noise_floor_20260909b",
          "value_cycle_ab_s1_noise_floor_folded18_single_arm_20260917"):
    s = json.load(open(f"docs/observability/{p}.json"))["selection_gbp_spread"]
    n, mean, sd = s["n"], s["mean"], s["stdev"]
    t = abs(mean) * math.sqrt(n) / sd
    solve = lambda q: optimize.brentq(
        lambda d: stats.nct.cdf(t, n - 1, d) - q, -12, 12)
    lo, hi = sorted([solve(0.975), solve(0.025)])
    print(n, round(t, 4), round(2 * stats.t.sf(t, n - 1), 4),
          round(sd * sd / (mean * mean) * BOOK, 1),
          "upper=inf" if lo < 0 < hi else round(n / min(abs(lo), abs(hi)) ** 2 * BOOK, 1))
# 9  1.7865 0.1118 3163.9 upper=inf
# 18 2.4954 0.0232 3243.3 179880.3
```

Sources read: `docs/observability/value_cycle_ab_s1_noise_floor_20260909b.json`,
`..._folded18_20260917.json`, `..._folded18_single_arm_20260917.json`, `..._next12_20260917.json`,
`docs/observability/book_growth_campaign.json`,
`docs/observability/settlement_ceiling_slope_20260921.json`, `site/data/book_growth.json`,
`site/data/value_arms.json`, `tools/generate_value_arms_data.py` (constants block,
`_can_this_book_be_built`), `simulation/live_population.py` (`_resolve_campaign`),
`simulation/net_new_acquisition.py` (`quote_capacity`, `homes_in_market`,
`plan_growth_campaign`).
