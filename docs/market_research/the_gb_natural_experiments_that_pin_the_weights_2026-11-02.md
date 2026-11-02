**Knowledge:** the-customer-needs-framework

# The GB natural experiments that pin the weights: collective switches, the fix share's collapse and rebound, opt-out enrolment and the 2023 prepayment pause (2026-11-02)

This is page 2 of the customer-needs domain as `docs/design/THE_KNOWLEDGE_BASE_STRUCTURE.md` §4 ranks it. It answers
the 30 Oct corpus steer (`docs/staging/advisor/DIRECTOR_STEER_BUILD_THE_CUSTOMER_KNOWLEDGE_CORPUS_AND_PROPOSE_THE_NEXT_SIM_ADDITIONS_2026-10-30.md`),
Ask 1 and both addenda (verify, challenge, expand; back every parameter with data).

The other pages in this domain rest on what households *said*. This page collects the places where the GB record
shows what households *did* when something outside them changed. Those are the only numbers that can bound the
size of a response. Every figure is graded: **D** derived by us from primary data, **P** reported in a primary
publication by the body holding the data, **S** a secondary summary, **A** an assumption with a range.

## 0. What each experiment measures, stated before any number

Four events. They measure different things and must not be read as one "engagement" number.

| # | Event | What changed | What it measures | Who it measures |
|---|---|---|---|---|
| 1 | Ofgem's Collective Switch trials, 2018-19 | A randomised offer, by letter, of a cheaper tariff and an easy route to it | **Shopping propensity when hassle and search cost are removed**, and how much the messenger and the brand matter | Households on a default tariff with one supplier for **3+ years**, non-prepayment |
| 2 | The fix share's collapse and rebound, 2021-26 | Fixed deals withdrawn market-wide in the crisis, then re-offered from H2 2023 | **How fast households who had been fixed re-fix** once fixes return | The whole non-prepayment book |
| 3 | Opt-in against opt-out enrolment on time-of-use tariffs | The default, not the offer | **The size of the default effect** | ToU trials and offers, six countries, UK included |
| 4 | The 2023 involuntary-prepayment pause | Debt-route prepayment installs stopped (Feb 2023), then restarted under licence rules | **How large the imposed route into prepayment is** | Households in debt to their supplier |

"Switching" in the trials is Ofgem's own definition (report para 3.15): a loss notification or an internal tariff
request, for one or both fuels, inside the trial window, whether or not it completed. It includes **internal**
tariff changes. It is not "moving supplier".

## 1. The Collective Switch trials (P, derived rates are D)

Source: Ofgem, *Ofgem's Collective Switch Trials* (2019), raw in `data/lake/ofgem_collective_switch_trials_2019/`
with the arm-by-arm rates in `trial_results.csv`.

| Trial | Fieldwork | n | Treated | Control | Ratio (D) |
|---|---|---|---|---|---|
| 1, supplier A, letters from the supplier | Mar-Apr 2018 | 55,000 | 26.9% | 2.6% | 10.3× |
| 1, same letters from Ofgem | | | 15.0% | 2.6% | 5.8× |
| 2, supplier B, exclusive tariff | Oct-Dec 2018 | 105,000 | 24.0% | 3.5% | 6.9× |
| 2, open market (no exclusive tariff) | | | 17.5% | 3.5% | 5.0× |
| 3, supplier C, exclusive tariff | Jan-Mar 2019 | 105,000 | 29.5% | 4.5% | 6.6× |
| 3, open market | | | 24.5% | 4.5% | 5.4× |
| Re-engagement (trial 1 non-switchers, six months on) | Oct-Dec 2018 | 5,140 | 14% | 2% | 7× |
| Small or medium supplier's exclusive tariff | Sep-Nov 2018 | 2,750 | 19% | 4% | 4.75× |

What the trials establish:
- **The untreated rate.** A household 3+ years on a default tariff changed tariff at **2.6% to 4.5% over a trial
  window of roughly two to three months** (P). This is the only randomised GB measure of the baseline. It is a
  window rate. It is not annualised here, because the windows differ by trial and seasonality is not controlled.
- **Hassle is most of the barrier.** Taking the search and the paperwork away moved 12 to 25 points of the book (the Ofgem-branded and re-contact arms at the low end).
  The open-market arm, with no exclusive price, still moved 14 to 20 points. Most of the effect is the easy route,
  not the price (P).
- **The messenger is worth 12 points.** The same letter from the supplier got 26.9%; from Ofgem, 15.0% (P). The
  report reads this as trust in, or familiarity with, the incumbent.
- **Brand matters at the point of choice.** When the exclusive tariff came from a small or medium supplier, 26% of
  switchers took it, against 70% and 68% when it came from a better-known supplier (P, report para 4.12).
- **Non-response is not a fixed trait.** Half a year after ignoring the first offer, 14% of non-switchers moved when
  asked again (P).

Grading the advisor's pack against the report:
- "Switching was 27% vs 3%, 24% vs 4% and 29.5% vs 4.5%": **confirmed** (the report rounds 26.9 and 2.6 in its text;
  its figure prints trial 2's control as 3.5%).
- "Raised switching about eightfold": **corrected** to 5× to 10× by trial and arm. Eight is inside the range but
  hides that trial 1's supplier-branded arm is the outlier.
- Sample sizes "n = 55k, 105k, 105k, 5k and about 2.5k": **corrected** for the last: Table 2 gives 2,750 (the power
  calculation in para 3.47 gives 2,502).
- The messenger effect, 27% against 15%: **confirmed**.

## 2. The fix share's collapse and rebound (D and P)

The steer cites "the fix share's 44% → 13% → 38%". **No source for those three numbers was found** in either
advisor pack, in the tree, or in Ofgem's current indicators. They are graded A until one is found. The primary
record, on stated bases:

| Reading | Fixed (or not default) | Default | Basis | Grade, source |
|---|---|---|---|---|
| April 2019 | about 47% not default | 53% (elec), 51% (gas) | non-prepayment, ~25 suppliers | P, Ofgem State of the Market 2019 §3.24 (`tools/published_tariff_mix.py`) |
| April 2023 | about 10% | about 90% on SVT | all domestic | P, Ofgem State of the Market April 2025 (same module) |
| July 2024 | about 16-17% on fixed | | all domestic electricity | D from Ofgem's "twice the proportion" statement (same module) |
| July 2025 | about one-third on fixed | | all domestic | P, Ofgem State of the Market January 2026 |
| **April 2026** | **43.5% active-choice fixed (elec), 45.1% (gas)** | **53.1% (elec), 53.3% (gas)** | non-prepayment, large and medium suppliers | **D**, from Ofgem's retail-market-indicator chart data, `data/lake/ofgem_retail_market_indicators_2026_04/` |
| April 2026 | | 58.5% (elec), 58.3% (gas) | all payment methods | P, Ofgem page text |

The 2020 and 2021 readings remain the declared gap `tools/published_tariff_mix.py` already carries.

What this establishes:
- **The shape holds; the steer's numbers do not.** The trough was nearer 10% than 13%. On the non-prepayment basis
  the rebound reached about 44%, not 38%. On the all-payment basis it reached at most 41.5%, since 58.5% were on
  default. The steer's 38% may be a third basis; it is not one we found.
- **The default share returned to its pre-crisis level.** Non-prepayment default was 53% in April 2019 and 53.1%
  in April 2026 (D against P). Under three years after fixes came back, the book had re-sorted itself to where it
  was. That is evidence that the fixed/default split is a stable property of the households, not of the offers in a
  given year.
- **The sticky core is about a third of the book.** In April 2026, 31.7% of non-prepayment electricity accounts
  (32.6% gas) were on a default tariff held for **3+ years** (D, reconciled to Ofgem's text). That is the
  population trial 1-3 sampled, and the population whose window rate was 2.6-4.5%.
- **What it does not show.** It cannot separate the households who re-fixed from those who were never fixed: the
  indicators are counts, not panels.

## 3. Opt-in against opt-out, and stated against revealed (P)

Source: Nicolson, Fell and Huebner (2018), a review of 66 uptake measures from 27 studies in six countries. The
rows used are in `data/lake/nicolson_tou_uptake_review_2018/table3_uptake_by_factor_extract.csv`.

| Factor | Mean | Median | 95% interval | Measures |
|---|---|---|---|---|
| Opt-out enrolment | 83% | 87% | 57-108% | **3** |
| Opt-in enrolment | 26% | 25% | 21-32% | 62 |
| Survey (stated willingness) | 37% | 36% | 31-43% | 34 |
| Trial recruitment | 23% | 12% | 10-36% | 20 |
| Commercial sign-up | 17% | 7% | 1-33% | 12 |
| UK measures | 30% | 30% | 22-37% | 15 |

- **This is not a GB natural experiment.** The steer lists it with the GB events; it is an international review.
  The opt-out figure rests on **three measures**, and its interval runs past 100%. It is confirmed as the paper's
  finding and graded P, but it is **too thin to be a world parameter alone**. GB has no published opt-out
  enrolment on a domestic tariff.
- **The "3-5×" stated-revealed gap is corrected to "about 2× to 5×, depending on the statistic".** The paper's
  "five times" is median survey willingness (36%) over median commercial sign-up (7%): 5.1× (D). On means it is
  37% over 17%: 2.2× (D). The gap is to commercial sign-up; against trial recruitment it is 1.6× (means) or 3× (medians).

## 4. The 2023 involuntary-prepayment pause (P, with one S)

- **How many.** Ofgem's market compliance review covered **more than 150,000 involuntary installations** across
  eight suppliers, from **1 January 2022 to 31 January 2023**, warrant installs and smart meters switched remotely
  together. It found fewer than 1% were fitted where it was not safe or reasonably practicable. Suppliers paid
  £5.6m compensation to about 40,000 customers and wrote off £13m of debt (P, Ofgem press release, 28 May 2025).
- **The pause and the restarts.** Suppliers paused involuntary installs in February 2023. A Code of Practice
  followed in April 2023 and became a supply licence condition on 8 November 2023. Restarts, per Ofgem's checker
  page: EDF, Octopus and Scottish Power 8 January 2024; E.ON 21 February 2024; OVO 18 September 2024; Good Energy
  6 January 2025 (P).
- **A count that disagrees by four times.** Citizens Advice estimated that **600,000 people were moved onto
  prepayment for debt in 2022** (S: an advocacy estimate, January 2023). Ofgem's reviewed cases are 150,000+ over
  thirteen months. **They do not count the same thing.** Ofgem counts involuntary installs (no consent). Citizens
  Advice counts people moved for debt, which includes moves the household agreed to under pressure, and it counts
  people, not meters. Neither is the flow of imposed prepayment by itself. The gap between them is the size of the
  "chosen under debt" route, which is the chosen-against-imposed split the steer asks about. It is not established.
- **Rate against the stock (D, wide).** Against about 4.3m prepayment customers (Ofgem State of the Market 2019
  §3.56; a 2019 stock against a 2022 flow), 150,000 in thirteen months is about 3% of the stock a year by Ofgem's
  count, and about 14% by Citizens Advice's. Read it as a range, not a point.

**GAP-NE-1.** Suppliers report involuntary-install monitoring data to Ofgem after restarting. Ofgem's page does not
publish it. A post-restart flow is therefore not established.

## 5. What this pins on the other pages

| Page | Bound this page sets |
|---|---|
| 1, price sensitivity is two traits | The shopping trait's floor among sticky defaults: 2.6-4.5% per two-to-three-month window (randomised control). Its ceiling when hassle is removed: 14-30%. The ceiling-to-floor ratio is the part of shopping that is hassle and trust, not price. |
| 3, the needs framework | Trust is a measured weight, not only a survey attitude: the same offer from the incumbent got 12 points more than from the regulator. |
| 5, stated against revealed | The gap is 2× to 5× by statistic, not 3-5×. A stated willingness used as a parameter must say which. |
| Chosen against imposed prepayment (Ask 2 candidate) | The imposed flow is 3% to 14% of the stock a year, by count. The world cannot draw the split from published data. |

**What to check next against our own world (not run on this page):** the world's tariff-change rate for a household
3+ years on a default tariff, over a ten-week window, against the trials' control arms of 2.6-4.5%. That is the one
randomised GB number the world's departure model can be graded against directly. It is a check, not an input: the
trial rates are public-reality knowledge and never cross the seam.

## 6. Confirmed, corrected, extended

- **Confirmed:** the trial rates and the messenger effect; the opt-out/opt-in rates as the paper states them; the
  restart dates.
- **Corrected:** "eightfold" to 5×-10×; the small-supplier trial n to 2,750; the fix share's trough and rebound
  numbers (the steer's 44/13/38 is unsourced: about 47, about 10 and about 44 on the bases above); the stated-revealed
  gap to 2×-5× by statistic; opt-out enrolment from "a GB natural experiment" to an international review on three
  measures.
- **Extended:** the April 2026 tariff-type shares, derived from Ofgem's chart data; the sticky core of about a
  third of the non-prepayment book; the open-market arm showing most of the effect is the route, not the price; the
  four-fold gap between Ofgem's and Citizens Advice's prepayment counts, and what each one counts.

No world or company value changes on this page. World additions follow the correctness exit test (ruling of
26 Oct).
