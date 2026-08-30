**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `A46_book_depth_is_a_curriculum_question`

# Pre-registration — what the clean ceiling slope must show, filed before it has one point

**Filed 2026-08-29, while `settlement-ceiling-slope.service` is still WAITING for the box.** No
point of it has been measured. Everything below is a prediction, and it is written down now so
that a result agreeing with it counts for something and a result refuting it cannot be quietly
re-read. The basis half of this item landed in `9dd0ab90e`; this is the number half.

## What is running, and how to find it

```
systemctl --user status settlement-ceiling-slope.service
docs/observability/settlement_ceiling_slope_20260829.log     # progress
docs/observability/settlement_ceiling_slope_20260829.json    # the artefact
```

Script: `/tmp/settlement_ceiling_slope.sh`. It waits for another lane's `run_value_cycle_ab`
legs (which the probe's own guard **cannot** see — `_LIVE_RUN_PATTERN` is
`"tools.run_annual_report"` and that job invokes the run as a library), then places the
`sim_runner` hold, drains the in-flight producer, measures **1,200 and 2,000** with
`--publish-interval 3600 --time-share 0.9`, and lifts the hold from an `EXIT` trap.

**Do not grade this off `settlement_ceiling_probe.json`.** That artefact's 2,000 row is the
contaminated one (`WORKER_FINDING_THE_CEILING_PROBE_READ_THE_PRODUCERS_BOOK_BACK_AS_ITS_OWN_
RESULT_2026-08-29`), which is why this run writes its own path.

**1,200 is re-measured rather than reused.** The existing clean 1,200 row was taken by the
pre-fix probe on a different afternoon; a slope stitched across two instrument versions measures
the difference between two afternoons, not the cost of a customer-year. **2,800 was dropped from
§6's three-point spec** and the reason is recorded rather than left as a gap: the top-of-range
question is answered by `recommend()`'s `funnel_supply_customer_years` without a run, and buying
it costs ~52 more minutes of stood-down publisher.

## The predictions, numbered so they can be marked

*Marked 2026-08-30 against `docs/observability/settlement_ceiling_slope_20260829.json`. **The run
returned one clean point (1,200) and one contaminated point (2,000)**, so every mark below that
leans on the 2,000 point leans on an observation the artefact itself bars from the slope
(`campaign_record_agrees: false`). That is stated in each mark rather than once at the top, because
a caveat at the top is a caveat nobody carries down the page.*

1. **The 2,000 point will be ceiling-bound, not funnel-bound.** It will commit ~2,000
   customer-years, not ~1,200. The contaminated row said 1,199.9 and concluded *"the funnel, not
   the ceiling, bounds this range"*; that was the mirror, and if the clean point reproduces
   1,199.9 then the mirror diagnosis was **wrong** and the funnel really does run out — which
   would be the more interesting result and would mean the ceiling is already above what the
   campaign can supply.

   > **RIGHT — on a point that is not clean.** The 2,000 run reported
   > `customer_years_committed: 1995.3`, `wins: 261`, `wins_refused_by_settlement_budget: 244`:
   > ceiling-bound, not funnel-bound, and the mirror diagnosis stands. **But this point carries
   > `campaign_record_agrees: false`**, so the prediction is confirmed by an observation of exactly
   > the kind it was written to replace. It is right, and it is not yet *established*.

2. **Clean cost at 2,000 will be MATERIALLY BELOW the contaminated 2,223.6s / 7,322.7 MB** —
   call it 1,500–1,800s and 6,000–6,800 MB. This is the falsifiable half of the contamination
   claim. If the clean point lands near 2,223s, the producer cost far less than was argued, and
   the write-up that leaned on "wall clock and RSS more than doubled" overstated it.

   > **WRONG on wall clock, right on memory — and it landed on the branch I wrote against myself.**
   > 2,097.6 s and 6,784.5 MB. The RSS is inside the predicted 6,000–6,800 MB band; **the wall clock
   > is not remotely inside 1,500–1,800 s — it is 5.7% below the contaminated figure, which is
   > "near 2,223s" by any reading.** By this file's own stated test, *"the producer cost far less
   > than was argued, and the write-up that leaned on 'wall clock and RSS more than doubled'
   > overstated it."* I am taking that verdict as written. The one hedge that is fair, and it cuts
   > both ways: this point was itself contaminated and another lane's suite ran throughout, so
   > neither figure is a clean cost — which is a reason the comparison is weak, not a reason the
   > prediction survives.

3. **Memory will NOT bind, at either point.** Marginal memory will come out near 2.3–3.3 MB per
   customer-year, so 2,000 peaks well under the guest's 24,032 MB. Read headroom live
   (`background.resource_headroom.sample()`), never from this file.

   > **RIGHT on the claim that binds, WRONG on the band.** Peaks were 3,952.4 MB at 1,200 and
   > 6,784.5 MB at 2,000 — both far under the guest and under even the 0.5 share allowed of it
   > (12,016 MB). Memory did not bind, and that is the load-bearing half. The band was optimistic:
   > the implied marginal is **3.54 MB/cy**, above the predicted 2.3–3.3. And that number cannot be
   > quoted as a measurement — `marginal` in the artefact is `[]`, because a marginal needs two
   > clean points and there is one.

4. **Therefore the recommendation will be that 1,200 is not an engineering limit at all.** The
   memory leg is slack, and after `9dd0ab90e` the time leg is a publish interval nobody has
   chosen. If 1–3 hold, the honest output is **not a new number** but a table mapping chosen
   interval → affordable ceiling, put in front of the director, because the interval is the
   decision and the ceiling is its consequence.

   > **RIGHT that 1,200 is not an engineering limit. WRONG about the deliverable, twice over.**
   > The first sentence held: the memory leg is slack (3) and the time leg is a chosen publish
   > interval, so 1,200 is not a limit this machine imposes. The predicted *artefact* failed in two
   > separate ways. **First, it could not be built:** the interval → ceiling table came back
   > `decidable: false` at all five intervals, because one clean point affords no cost per
   > customer-year. **Second, it should not have been built even if it could:** a table of intervals
   > and ceilings is precisely the artefact that would have let the director spend the cadence for
   > nothing. What made A46 a decision was a column this prediction did not contain — how many of
   > the accounts a ceiling buys the method could price, which is **zero at every row** and put
   > there by a different finding that landed the same night.

**Prediction 4 is the one I am least sure of and it is the one that matters**, because it says the
deliverable is a decision rather than a measurement. If the slope shows memory binding earlier
than expected, 4 is refuted and the ceiling is a real engineering limit after all — which is the
answer the direction explicitly named as complete and useful: *"the probe says 1,200 is right and
the ceiling is real."*

> **Marked: that is not how it failed.** Memory never came close to binding, so the "ceiling is
> real" branch was not taken. 4 was refuted from the other side — not by a bound that was tighter
> than expected, but by there being **no second clean point to compute any bound from**, and by the
> deliverable being wrong in kind rather than in value. I was least sure of 4 and I was wrong about
> 4, and I was wrong in a direction I had not enumerated. Neither branch I wrote down happened.

## What the run actually returned, so a later reader does not have to re-derive it

| | 1,200 | 2,000 |
|---|---|---|
| wall clock | 928.6 s | 2,097.6 s |
| peak RSS | 3,952.4 MB | 6,784.5 MB |
| customer-years committed | 1,195.4 | 1,995.3 |
| wins booked | 90 | 261 |
| wins refused by the budget | 415 | 244 |
| `clean` | **true** | **false** — `campaign_record_agrees: false` |

`marginal: []`, `recommendation.decidable: false`. Priced up into a menu in
`docs/design/A46_THE_PRICED_MENU_2026-08-30.md` §2, and the derived menu artefact is
`docs/observability/settlement_ceiling_menu_20260830.json`.

## What to do with the result, so this does not drift a fourth time

1. Mark each prediction above **beside** the result, right or wrong, in this file.
2. If 1–3 hold: build the interval→ceiling table into
   `SETTLEMENT_CUSTOMER_YEAR_BUDGET`'s note and send the director the interval question with a
   recommendation attached — never a bare ask.
3. Either way, replace `NOT YET KNOWN` in
   `tools/generate_book_growth_data.py::engine_bound_basis` with what the slope established.
   **That string is the reader's copy of this answer** and it is the thing that goes stale
   silently; the door control asserts the sentence reaches the page, not that it is current.
4. Confirm the hold is gone: `ls docs/review_gates/.sim_runner_hold`. If it exists and
   `pgrep -f settlement_ceiling_slope` finds nothing, it is stale and it is stalling publication
   — delete it.

## The thing most likely to go wrong, said in advance

**The box never goes quiet and the run gives up at its 6-hour deadline**, having placed no hold
and measured nothing. That is not a silent failure — the log says `GAVE UP` and the slope is
still owed — but it is the outcome that leaves this item exactly where it was. The last attempt
died of contention and I predicted three points would fit in a tick; the correction I wrote then
was that I had checked the box was idle once and treated it as a property of the next hour. This
run waits for the box instead of assuming it, which is the fix, but waiting is not the same as
succeeding.
