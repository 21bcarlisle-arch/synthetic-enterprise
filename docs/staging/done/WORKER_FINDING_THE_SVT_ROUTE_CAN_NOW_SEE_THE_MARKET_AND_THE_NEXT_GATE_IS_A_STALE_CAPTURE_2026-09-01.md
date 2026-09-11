# FINDING — the SVT route can now see the market, and the next gate is a stale capture

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`
**Filed:** 2026-09-01.
**Pre-registration:** `WORKER_PREREGISTRATION_WHAT_GIVING_THE_SVT_HAZARD_A_MARKET_TERM_MUST_MOVE_2026-09-01.md`,
filed before the term was written and before any measurement below was run.
**Discharges:** `WORKER_FINDING_THE_ROUTE_CARRYING_MOST_DEPARTURES_IS_INVARIANT_TO_THE_RECORD_IT_IS_FITTED_AGAINST_2026-08-31.md`
(`18a09617d`), and item 2 of the owed list at
`WORKER_FINDING_THE_SVT_FLOORS_FILED_REPAIR_APPLIES_A_2024_REFERENCED_RATIO_TO_A_2019_20_RATE_2026-08-31.md`.

---

## What landed

`simulation.departure_risks.svt_inertia_hazard` now takes a **required, keyword-only**
`market_switching_multiplier`, wired through `simulation/svt_product.inertia_hazard_for_term` from
each cap segment's own **start** year. Inside the hazard the multiplier is **re-referenced from
2024 to the 2019–20 window** §4 inferred `0.20` / `0.10` against, then applied to the **annual**
rate before the constant-hazard conversion.

Three design points, each of which was a way to get this wrong:

1. **Required, not defaulted at 1.0.** The refusal that demanded this term inspects the
   *signature*. A defaulted parameter would have lifted the refusal while every caller kept running
   market-blind — the term would have reached nothing and the control that named the defect would
   have reported green. `test_the_market_term_reaches_the_hazard_and_is_not_merely_in_the_signature`
   drives 2020 against 2022 and reads the answer, precisely because signature-keyed controls cannot.
2. **Re-referenced, not multiplied.** The form filed at `18a09617d` was
   `floor × market_switching_multiplier(year)`, which levels a 2019–20 rate up into the market it
   was already measured in by a constant **1.375776** in every year. The year cancels, so no
   year-shaped check can see it, and it is exactly invisible at 2024 where `multiplier(2024) = 1.0`.
3. **Applied to the annual rate, not the converted hazard.** Scaling after the segment conversion
   would re-level an already-converted quantity and break the recomposition property.

**Nothing is fitted.** The factor is the record's own ratio divided by the record's own value in the
window the constants state they were inferred in. `factor(2019–20 mean) = 1.0` by construction, so
inside the inference window the world still runs the published 0.20 / 0.10 — which is what keeps the
level checkable.

## Knowledge first — the record's own account of 2022, established before any term was written

`docs/market_research/svt_rates_active_passive_2016_2025.md` §3: *"Active renewal **effectively
collapsed**. Suppliers withdrew fixed tariffs — wholesale costs exceeded the Ofgem price cap ceiling
so no viable fixed product could be offered. […] **Customers did not voluntarily churn: no
competitive fixed alternatives existed.**"*

The direction asked specifically whether there were acquisition tariffs to switch **to**. The source
answers it directly and negatively: there were not. The suppression is a **supply-side** fact, not a
household-preference one — the destination product did not exist — which is exactly what a hazard
keyed only to `years_on_svt` and `segment_days` cannot represent. Magnitude from the commons:
**4.30%** in 2022 against **23.00%** in 2020.

---

## Measured, at real inputs, all ten years

Predictions were filed per year before the run. Old floors reproduced live on 2026-09-01 rather than
inherited from 08-31.

| year | accts | target % | old floor % | factor | **predicted %** | **measured %** | reachable |
|---|---|---|---|---|---|---|---|
| 2016 | 3 | 17.60 | 0.04 | 0.7946 | 0.04 | **0.03** | (partial year) |
| 2017 | 57 | 14.00 | 9.27 | 0.6321 | 5.86 | **5.67** | yes |
| 2018 | 53 | 20.00 | 11.36 | 0.9029 | 10.26 | **10.17** | yes |
| 2019 | 39 | 21.30 | 11.60 | 0.9616 | 11.16 | **11.12** | yes |
| 2020 | 48 | 23.00 | 9.85 | 1.0384 | 10.23 | **10.27** | yes |
| 2021 | 54 | 18.40 | 9.62 | 0.8307 | 7.99 | **7.88** | yes |
| 2022 | 55 | **4.30** | **12.80** | 0.1941 | 2.49 | **2.33** | **yes** |
| 2023 | 54 | 12.50 | 12.43 | 0.5643 | 7.01 | **6.77** | yes |
| 2024 | 54 | 16.10 | 9.12 | 0.7269 | 6.63 | **6.49** | yes |
| 2025 | 48 | 17.90 | 4.90 | 0.8081 | 3.96 | **3.90** | (partial year) |

**P1 CONFIRMED**, every year inside ±0.4pp — **with one wrong detail I am keeping rather than
revising.** I predicted the measured floor would land *"slightly BELOW"* `old × factor` universally,
and gave the second-order argument for it. The argument is right and my sentence was not: it only
implies "below" for `factor < 1`. **2020 is the single year with `factor > 1` (1.0384) and it came
in slightly ABOVE** — 10.27 against 10.23 — which the same `h ≈ ta + t(1−t)a²/2` term predicts. The
prediction's stated *mechanism* covered the case; its stated *direction* did not.

**P2 CONFIRMED — this is the claim.** 2022's floor **12.80% → 2.33%** against a 4.30% target.
Previously unreachable at *every* point in the published band, including its bottom (8.99%). It is
now reachable with headroom, and by a mechanism rather than a constant: nothing about §4's bands
moved.

**P3 CONFIRMED in direction, and my magnitude band was WRONG.** 2023's renewal anchor
**0.0300 → 2.4417**. I predicted "above 1.0, predicted 1.3–2.0". It is above 1.0 as claimed but
outside the band I named. The route the company can actually price against stopped being extinct,
which is the leg that mattered; my sizing of it was too narrow.

**P4 CONFIRMED.** Spearman against the published midpoint 2017–2024: **−0.26 → +0.9048** (predicted
> 0.7).

**P5 CONFIRMED.** CV ratio against the record: **0.368 → 1.0387** (predicted > 0.7). *Recomputed the
old figure as 0.368 where `18a09617d` recorded 0.336; the difference is population, not arithmetic,
and I did not chase it because both are far below the 0.7 the prediction turned on.*

**P6 CONFIRMED — the wedge MOVED rather than cleared, as pre-registered.**

## Re-verified 2026-09-01 by a second worker, at a denominator that had moved

A later tick was drawn on this same item, found it already landed at `c628cb37d` and on origin, and
**re-ran the table rather than inheriting it** — the direction that drew it said so explicitly, and
this repo has paid before for a cited baseline that came from a different run than the comparison.

`svt_market_invariance_refusal()` returns `None` live. The staleness leg fires live, in its own
words: *"1221 of 1221 SVT rows reproduce under a MARKET-BLIND hazard"*. Floors recomputed from each
row's own `sim_years_on_svt` / `sim_segment_days` / `market_year` under the current hazard:

| year | accts | target % | old floor % | **new floor %** | reachable |
|---|---|---|---|---|---|
| 2016 | 3 | 17.60 | 0.04 | 0.03 | yes |
| 2017 | 57 | 14.00 | 9.27 | 5.67 | yes |
| 2018 | 53 | 20.00 | 11.36 | 10.17 | yes |
| 2019 | **41** | 21.30 | **11.04** | **10.58** | yes |
| 2020 | **49** | 23.00 | **9.65** | **10.06** | yes |
| 2021 | **53** | 18.40 | **9.30** | **7.62** | yes |
| 2022 | **52** | **4.30** | **12.83** | **2.34** | **yes** |
| 2023 | **51** | 12.50 | **11.94** | **6.51** | yes |
| 2024 | **52** | 16.10 | **9.06** | **6.45** | yes |
| 2025 | 48 | 17.90 | 4.79 | 3.81 | yes |

**The claim holds and the denominator is NOT the same one.** Bolded cells are the years whose
account count moved between the two runs (2022: 55 → 52). The capture is unchanged — the union
denominator is not, because it is computed over both routes from a tree other lanes keep landing
into. So this is the stronger reading rather than a repeat: the conclusion survived a population
change nobody arranged for it. 2022 lands at **2.34%** here against **2.33%** filed, and every year
is reachable in both.

**Do not read the two tables as one series.** Same mechanism, two populations — differencing a cell
across them measures the denominator, not the hazard.

---

## The next gate, and it is honest

`svt_market_invariance_refusal()` now returns `None` — it is keyed to the live signature, so it
lifted by construction and will come back up by itself if the term is ever removed.

But **all 1,266 rows of every committed capture reproduce only under a market-BLIND hazard**, so
`svt_composition_refusal` now refuses them as **stale**, in those words, and the whole-book fit
still emits no `YEAR_LEVEL_ANCHOR` block. That is the correct answer: the recorded floors are the
flat 0.20/0.10 the record contradicts, and fitting against them would solve the renewal anchor
around a world that no longer exists.

I added that staleness leg deliberately. Without it a pre-market-term capture lands in the existing
`neither` branch and reads as *"the world runs a hazard this fit does not model"* — sending the next
reader to hunt a mechanism disagreement that is really an artefact older than the code.

**The ordinary repair is blocked, and not by this lane.** At this HEAD `run_phase2b` emits no
`svt_decisions` key, so `tools/capture_departure_factors.py` writes no SVT sibling at all — the
1,266-row siblings came from a working tree carrying another lane's uncommitted roll and recorder
(`WORKER_FINDING_A_PUBLISHED_CAPTURE_WAS_PRODUCED_BY_CODE_THAT_WAS_NEVER_COMMITTED_2026-08-31.md`).
**So the fit table above is a diagnostic computed at the capture's real per-household inputs under
the current hazard, and is explicitly not a constant.** Nothing was pasted into
`simulation/departure_level_anchor.py`.

## What is owed

1. **Land the SVT departure route's recorder in `run_phase2b`** so a capture can be regenerated. Until
   then no whole-book anchor can be emitted by the ordinary route. This is the binding item and it
   is in another lane.
2. **Re-run the capture, then the whole-book fit**, and only then consider a constant.
3. **`population_anchor._churn_by_year` is still blind to 2022** and is untouched here. It must not
   be repaired by inserting a `sim_churn_rate` of 0.0 — that publishes a measured zero-churn crisis
   year. Its five arithmetic consumers fail closed instead.
4. **The base window's evidence is documentary** — §4's basis column — and no arithmetic in this
   repo can test it. Recorded on the constant itself. Robustness holds: every other plausible window
   moves the re-levelled rate by a few per cent against the 37.6% mismatch being corrected.

## Controls, and the one mutation that did not fire

Three mutations, each firing on the leg it targets:

| mutation | fires |
|---|---|
| drop the factor (term accepted, ignored) | `test_the_market_term_reaches_the_hazard_and_is_not_merely_in_the_signature` |
| the naive 2024-referenced `rate × multiplier(year)` | `test_the_published_rate_is_unchanged_inside_its_own_inference_window` |
| default the term to 1.0 | `test_the_market_term_is_required_so_a_caller_cannot_quietly_run_market_blind` |

**Mutation 1 did NOT fire the base-year control, and that is an EQUIVALENCE, not a missing test.**
Deleting the factor entirely leaves the rate at exactly 0.20 inside the inference window — which is
precisely what that control asserts. Its subject is the re-referencing, not the presence of the
term, and the two legs are meant to be independent. Establishing which of the two it was is the rule;
recording that it is the unflattering-to-check one rather than assuming the flattering answer is the
point.

**A control was INVERTED, and it deserves naming.**
`test_the_fit_refuses_while_the_svt_route_cannot_see_the_market` asserted
`svt_market_invariance_refusal() is not None` — it required the refusal to be **up**. That is a
control asserting the model stays bad: keyed that way it goes red on the repair and green on the
defect. It is now
`test_the_svt_route_can_see_the_market_so_the_fit_no_longer_refuses`, with the can-fire leg preserved
by injecting the market-blind hazard the world ran until today.

## Two pre-existing reds, neither mine

Verified against a clean `git archive HEAD` checkout with the artefacts symlinked in, not assumed:
`test_a_cause_the_mix_cannot_observe_is_absent_rather_than_zero` and
`test_the_declaration_can_tell_a_one_route_capture_from_a_two_route_one` fail at HEAD, before this
change. Which of the two fires depends on which report artefacts are present in the tree.
