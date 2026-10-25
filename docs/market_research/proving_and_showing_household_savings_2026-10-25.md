# Proving household savings, and showing them so customers and a regulator believe them

**Knowledge:** proving-and-showing-household-savings

Written 2026-10-25 from the advisor's cited evidence pack
`docs/staging/advisor/done/DIRECTOR_EVIDENCE_PROVING_AND_SHOWING_HOUSEHOLD_SAVINGS_2026-10-25.md`,
with the CalTRACK and ECO in-use-factor sections of the gap-closure pack
(`DIRECTOR_EVIDENCE_GAP_CLOSURE_TDCV_VAT_RTS_CALTRACK_ECO_IUF_2026-10-25.md`), under the director's
steer that the advice roadmap needs its knowledge first (25 Oct, 05:37: "Then proving if it did or
didn't. Sharing the savings clearly for the customer to enjoy"). **[derived]** is the pack author's
arithmetic; **[unverified]** items are not claims until sourced, and section 8 records what was
checked against primary sources while drafting.

## 0. What this project does today (read from code, not run)

- **The household's side of the score is a price comparison, not a measured saving.**
  `company/analytics/household_value_share.py:49-54` computes what a household would have paid on the
  published default tariff at its own metered volumes, minus what it paid. That is the "you saved £X
  against the price cap" line real bills carry. It does not measure a change in consumption, and its
  docstring says it cannot measure value created (`:56-66`).
- **The world holds the true counterfactual, and nothing grades a supplier's savings estimate against
  it.** No module in `company/`, `simulation/` or `sim/` implements CalTRACK, IPMVP, a deemed-savings
  table, a minimum-detectable-saving calculation or a claim audit.
- **The world does model the prebound effect** (`simulation/household.py:231`;
  `simulation/fabric_demand_path.py:312`), which is the mechanism behind deemed savings over-predicting.
- **Flexibility events use a trivial baseline in the world** (`sim/flex_dispatch.py:9-13`), so no
  baseline-gaming or baseline-error test is possible yet.
- **Advice reaches no household** (`C30_advice_reaches_a_household`, level 0).

## 1. Deemed, modelled and metered savings

- **Deemed.** ECO4 and GBIS score measures from a partial-project scores matrix based on annual bill
  saving (https://www.ofgem.gov.uk/guidance/eco4-scores). ECO1 cut modelled savings by an in-use factor
  per measure; confirmed in Ofgem's ECO Measures Table v1.6 (2 Dec 2014,
  https://www.ofgem.gov.uk/ofgem-publications/83100/energycompaniesobligation-measures-pdf, fetched
  2026-10-25): cavity wall and loft 35%; solid brick wall built before 1967 (E&W) or 1965 (Scotland)
  33%; other solid walls and room-in-roof 25%; flat roof, underfloor, draught-proofing, glazing and
  similar 15%; district heating 10%; none given for boilers, storage heaters, controls, heat pumps or PV.
  ECO3 and ECO4 dropped the factor for a "percentage of property treated" adjustment.
- **Modelled.** SAP/RdSAP or an engineering model; the ECO4/GBIS mid-scheme assessment used "well-
  understood modelling techniques" with "no sensitivity analysis" (DESNZ, Nov 2024).
- **Metered.** From meter data. DESNZ proposed a voluntary pay-for-performance route rewarding
  measured gains with SMETERs. **SMETER accuracy:** in a blind 30-home trial against co-heating tests,
  bias (NMBE) ran −0.7% to −26.9% and scatter (CV(RMSE)) 13.4% to 38.9%; the best beat an expert RdSAP
  (https://assets.publishing.service.gov.uk/media/6a4790e28effd97622f53c04/smeter-case-studies-evidence-base-annex.pdf).
  In the MEASURED trial (56 homes), calculated heat loss matched measured in only 30% of homes and
  overestimated it in 59%.

## 2. M&V methods

**IPMVP options** (from a secondary summary citing EVO 10000-1:2022; EVO's own text not fetched): A,
retrofit isolation with key parameters measured; B, retrofit isolation with all parameters measured;
C, whole facility from utility meters; D, calibrated simulation. For a supplier with smart-meter data,
Option C is the natural default. A non-routine adjustment accounts for "an unexpected change that
causes energy use within the measurement boundary to change" (an extension, a new EV).

**CalTRACK** (https://caltrack-technical-documentation.readthedocs.io/en/latest/methods.html, fetched
2026-10-25):
- Daily and billing methods: a 365-day baseline ending at the intervention, with no more than 37
  missing days (10%). Hourly methods need **no minimum baseline length**, but over 90% of hours must be
  present in the same calendar month and the neighbouring months of the previous year.
- Model forms: intercept only, HDD only, CDD only and HDD+CDD (cooling not tried for gas); balance
  points searched 30–90°F in steps of at most 3°F; at least 20 degree days a year. Daily models by
  ordinary least squares, billing by weighted least squares.
- Hourly: a time-of-week-and-temperature model with 168 weekly slots; a slot is "occupied" if the
  fixed balance-point model under-predicts more than 65% of its points; neighbouring months weighted 0.5.
- Uncertainty: fractional savings uncertainty with a t-statistic "usually 90%" and Sun–Baltazar
  autocorrelation coefficients (billing a = −0.00022, b = 0.03306, d = 0.94054; daily a = −0.00024,
  b = 0.03535, d = 1.00286); a building CV(RMSE) of 100% recommended as a default, waivable; FSU
  thresholds set by the procurer (examples: under 15% for non-wires alternatives, 25% for
  pay-for-performance); site FSUs combined across a portfolio by root-sum-of-squares, which "does not
  eliminate inherent systemic biases".

**ASHRAE Guideline 14.** Model calibration: CV(RMSE) ≤ 20% monthly and ≤ 30% hourly, NMBE ≤ ±5% and
±10% (https://energy-data.io/standards/ashrae-guideline-14/). The 20% monthly figure is for regression
savings baselines; calibrated simulation is held to 15% monthly / NMBE ±5% and 30% / ±10% hourly
(corrected 25 Oct, second read; Burman et al. 2020 and NREL quoting G14, secondary). "ASHRAE Guideline 14 requires that the
savings uncertainty be less than 50% of the annual savings at 68% confidence" (EVO M&V Focus #5,
https://evo-world.org/en/news-media/m-v-focus/868-m-v-focus-issue-5/1164-why-r2-doesn-t-matter,
fetched 2026-10-25). G14 itself is a purchased document.

**Practice.** Monthly regression is generally usable only when savings are at least 10% of use;
fewer than 6 months of data give unacceptably high bias; 9-month models have median bias near zero
(Kemper, ACEEE 2015). Autocorrelated residuals understate uncertainty: Bayesian AR(1) and Newey–West
intervals achieved coverage close to 95% where the best method of Touzani et al. (2019) reached 71%
(arXiv 2607.25382). BIT's Nest evaluation used HDD normalisation with propensity matching and
fixed-effects difference-in-differences and measured 4.5–5% of household gas.

## 3. Comparison groups and the size of a detectable saving

- **RCTs** are the gold standard (Ofgem CMOL ~150,000 customers; BIT IHD-vs-app 7,903). The
  workhorse is matched difference-in-differences: all seven supplier smart-meter studies in BIT's 2023
  meta-analysis used it.
- **Controls matter:** across 156 trials the average saving was 7.4%; controlled studies found ~2%,
  uncontrolled ~9.6% (Delmas, Fischlein & Asensio 2013).
- **One home:** hourly models detect a median 3.6% at 90% confidence; daily 4.3% (Kemper, 96 US homes).
- **Portfolios (95% half-widths):** BIT IHD vs app ~±1.4pp electricity and ±1.8pp gas at ~2,760 per
  arm; SENS smart thermostat ±3.9% at ~395 per arm; SENS GenGame ±2.0%.
- **Rule of thumb [derived]:** half-width ≈ 1.5pp × √(2,760 / n per arm): ±4.5pp at 300, ±2.5pp at
  1,000, ±0.8pp at 10,000, ±0.25pp at 100,000. Weather and price shocks cancel between arms of an RCT;
  they do not cancel in a single home's before-and-after.
- **Baseline length:** at least 6 months, ideally 9–12; heating-led gas savings need a winter.

## 4. Flexibility-event baselines

- DFS 2022/23: average use over the previous 10 working days (or 4 weekend days), plus a domestic
  in-day adjustment from the window 4 to 1 hours before the event (NESO DFS deep-dive). NESO's own
  slides showed inflating the 3-hour window could net £1.98 per kWh at a £3/kWh reward; the
  adjustment was removed for 2023/24.
- ERM and CSE on ~139,000 domestic customers in 2022/23 (https://www.neso.energy/document/371411/download):
  the in-day adjustment applied to 77% of customer-events and "often obscured true response"; average
  delivery 0.39 kWh per participating consumer per event (Centre for Net Zero: 0.31); ~52% of
  opted-in consumers actually reduced; over the whole day 62% *increased*; post-event demand exceeded
  baseline in 14 of 18 events; no systematic gaming, but 60% of the top 1% of shifters moved load into
  the pre-event window; average reward £1.19 per consumer per event.
- The standardised baselines from 1 Apr 2026 include "Recent History"; nomination accuracy limits
  10% net and 20% absolute error; unrestricted resubmission "introduces a material risk of gaming".

## 5. What really saves (measured)

- **Smart meters and IHDs:** Early Learning Project 2.3% electricity, 1.5% gas; BIT 2023 meta-analysis
  pooled −3.43% electricity and −2.97% gas (robustness −2.61% and −2.43%); the cost-benefit analysis
  assumes 3.0% and 2.2% for credit, 0.5% gas for prepayment. Apps did not meet a 0.5% equivalence bar
  against IHDs. Advice changes the result: 10% for 200 low-income prepayment customers with in-home
  advice against 3% without.
- **Home energy reports:** Allcott (2011), ~600,000 households, 2.0% on average (6.3% top decile of
  prior use, 0.3% bottom). Allcott & Rogers (2014): 1–1.3% after the first report, ~3% in year 2; after
  reports stop, effects decay 10–20% a year; 58–60% of total savings arrive after the intervention ends.
  Cadmus plans on ~20% decay.
- **Fabric (NEED 2025):** first-year median gas savings 16% solid wall, 9% cavity plus loft; cavity
  wall alone 5.7–11.5% by cohort, falling for later cohorts. **Measured against modelled:** BRE's
  16-home solid-wall trial achieved ~73% of the predicted saving.
- **Biases:** prebound (actual ~30% below calculated across 3,400 German dwellings, ~40% for the least
  efficient); direct rebound for heating 10–30% best guess (UK estimate up to 70% direct); Hawthorne
  ~2.7% that vanished after the study; boomerang among low users under descriptive norms, removed by
  an injunctive cue.

## 6. Defensible claims

What confounds a measured saving: weather; price changes; life events (a non-routine adjustment);
load shifting around events; other programmes. Only a randomised or matched comparison separates the
supplier's effect from these.

- **Ofgem Standards of Conduct (SLC 0):** information "complete, accurate and not misleading", in
  "plain and intelligible language".
- **CMA Green Claims Code (2021):** truthful, clear, no material omissions, fair comparisons, full
  life cycle, substantiated.
- **ASA, British Gas, 4 Mar 2026** ("Save up to £546 with a heat pump"): upheld. An "up to" claim needs
  a significant proportion of customers to achieve it, and only 34% of 194 did; modelled status and
  assumptions must be in the ad itself; assumptions must represent actual customers
  (https://www.asa.org.uk/rulings/british-gas-services-ltd-a25-1295064-british-gas-services-ltd.html).
- **ASA, Octopus, 23 Apr 2025:** "most homes would save" was misleading without its basis; "learn
  more" is not adequate signposting
  (https://www.asa.org.uk/rulings/octopus-energy-ltd-a24-1265573-octopus-energy-ltd.html).

**Ten design rules for any saving shown to a customer** (from the pack): label the evidence class
(estimated / measured, your home / measured, homes like yours); show the baseline and its basis in the
message; give a range, or "too small to measure for one home", below ~4% (hourly) or ~10% (monthly);
normalise for weather and say so; "up to" only where a significant share achieve it; lead with
pounds and warm hours, carbon second; pair comparisons with an injunctive cue for low users; count
only net savings for flexibility events; decay cumulative savings; keep it auditable and check
vulnerable customers are not pushed into under-heating.

**Showing savings.** Personalised pounds drive switching (CMOL: 1% control, 2.9% across letter arms,
3.4% supplier-branded), but money framing can backfire for conservation; health and environment
messages saved 8% against control (Asensio & Delmas 2015). Customers found "warm hours" easier than kWh
(ESC). Event engagement is concentrated: ~1% of DFS consumers opted into every event; 61% earned £0–£1
per event.

## 7. What only a simulation can test (the savings grader)

Because the world holds each home's true counterfactual, it can grade the supplier's own estimator:
(1) estimator bias and interval coverage by method; (2) an empirical minimum-detectable-saving curve
from 1 to 100,000 homes; (3) deemed-to-true ratio by measure (expect ~0.7), split by prior use to test
the prebound mechanism; (4) confounder stress tests (cold winter, price shock, EV, baby, home working);
(5) rebound, Hawthorne and persistence ground truth; (6) flexibility baseline gaming; (7) an audit of
every "you saved £X" message against the ASA test; (8) value-share fairness by segment.

## 8. Verification of the pack's [unverified] items (2026-10-25)

| Item | Outcome | Source |
|---|---|---|
| ECO in-use factors ~35% cavity and loft, 33% solid wall | **confirmed**, with scope — 33% is pre-1967 solid brick only; other solid walls 25%; ECO1 measures only | Ofgem ECO Measures Table v1.6 |
| IPMVP options A–D definitions | still open — confirmed only at a secondary source citing EVO 10000-1:2022 | NSW M&V Guide Module 2 (via gap pack) |
| IPMVP routine / non-routine adjustments; life events as non-routine | still open — non-routine defined at the secondary source; routine not | as above |
| G14 ~15% monthly CV(RMSE) for calibrated simulation | still open — G14 is paywalled; the secondary summary gives ≤20% monthly / ≤30% hourly for savings models | energy-data.io |
| G14: savings uncertainty < 50% at 68% confidence | **confirmed** | EVO M&V Focus #5 |
| CalTRACK 365-day baseline (also "CalTRACK's 12 months") | **corrected** — 365 days for daily and billing methods; hourly methods need no minimum length | CalTRACK methods 2.2.1.1–2.2.1.2 |
| CalTRACK ~90% data coverage | **corrected** — ≤37 missing days (10%) for daily/billing; >90% of hours in matched months for hourly | CalTRACK 2.2.1.2 |
| CalTRACK HDD/CDD models with a balance-point search | **confirmed** | CalTRACK 3.2, 3.4 |
| CalTRACK hourly time-of-week-and-temperature model with occupancy | **confirmed** | CalTRACK 3.8 |
| CalTRACK built for portfolio aggregation | **confirmed** — portfolio FSU by root-sum-of-squares; primary use case energy-efficiency procurement | CalTRACK 4.3.2.5 |
| Opower 1.4–3.3% across programmes | still open (Cadmus gives 1.5–2.5% in years 1–2) | — |

Counts: confirmed 5, corrected 2, still open 4 (of 11 [unverified] items).

## 9. Headline bands (candidate population checks; calibration only, never per-home targets)

- Smart meter + IHD saving: electricity 2.3–3.4%, gas 1.5–3.0%; prepayment gas ~0.5%.
- Home energy reports: ~2.0% average; decay 10–20%/yr after stopping.
- Controlled vs uncontrolled information studies: ~2% vs ~9.6%.
- Measured/modelled, solid wall: ~0.73; prebound actual/calculated ~0.70 (~0.60 least efficient).
- NEED median gas saving: solid wall 16%; cavity 5.7–11.5%; cavity + loft 9%.
- Heating direct rebound: 10–30% best guess.
- Single-home minimum detectable saving: ~3.6% with hourly data; ≥10% needed with monthly.
- DFS delivery per participating household per event: 0.31–0.39 kWh.

## 10. Named gaps

EVO IPMVP text; the G14 calibration clause; LBNL M&V 2.0 acceptance criteria; ECO3/ECO4 in-use
factors; Allcott & Kessler; the Opower cross-programme range; Gillingham's rebound review; Ofgem rules
specific to estimated savings in sales; how OVO, British Gas, Ohme and Tesla apps present savings; any
trial on the believability of "you saved £X"; NEED's own modelled-vs-measured ratio; a GB DFS
baseline-accuracy figure against a true counterfactual; a GB heat-as-a-service or savings-share
result with measured savings; SMETER data-duration requirements.

## Second read: the advisor's verification pass, 25 Oct 2026 (gap-closure items only)

An independent read by the advisor (GB-packs verification file, 25 Oct, pass 2 §5). It covers the
gap-closure pack's tagged items. This page carries only that pack's CalTRACK and ECO sections, so
four of the five items were never on it; they are added here so the pack's tally is complete. The
proving-and-showing pack's own items are a separate read and are not reconciled here.

| Item | §8 outcome | Advisor | Reconciled | Source |
|---|---|---|---|---|
| G14 calibration limits (§8 row 4) | still open: secondary gives ≤20% monthly / ≤30% hourly | confirmed: hourly NMBE <10%, CV(RMSE) <30% (NREL); monthly ≤15% / ≤5% from a Q&A site | **still open**, DISAGREES. Hourly limits now rest on NREL | https://www.nrel.gov:443/docs/fy19osti/70865.pdf ; https://unmethours.com/question/15/when-calibrating-an-energy-model-what-are-the-typical-metrics-to-show-proper-calibration/ |
| PHE 2014 bands: <16°C respiratory, 9-12°C cardiovascular, <5°C hypothermia (new row) | not on this page | corrected: the review gives no such bands. ≥18°C "poses minimal risk"; blood-pressure risk rises below 18°C, more below 16°C; evidence weak | **corrected** (primary: the PHE review) | https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/468196/Min_temp_threshold_for_homes_in_winter.pdf |
| Condensing boilers effectively mandatory since 2005 (new row) | not on this page | confirmed: Approved Document L 2005 | **confirmed** (manufacturer page, secondary) | https://baxi.co.uk/trade/legislation/boiler-plus |
| EST in-situ condensing-boiler trial "around 2009" (new row) | not on this page | confirmed: DECC, 19 Jun 2009, sixty boilers | **confirmed**. Its summary says nothing on sludge or cleaning | https://www.gov.uk/government/publications/in-situ-monitoring-of-efficiencies-of-condensing-boilers-and-use-of-secondary-heating-trial-final-report-2009 |
| Boiler Plus (2018) requires a system clean and a filter (new row) | not on this page | corrected: filter plus clean-and-flush (BS 7593) came with the 2022 Part L uplift in England; Boiler Plus was ErP ≥92%, controls and combi measures | **corrected** (trade press, secondary) | https://baxi.co.uk/trade/legislation/boiler-plus ; https://phpionline.co.uk/feature-articles/part-l-and-water-treatment/ |

DISAGREES, G14 monthly: the advisor's 15% comes from a Q&A site, and §8's secondary gives 20%. The two
may be different clauses (calibrated simulation against a savings regression model). G14 is paywalled,
so neither is primary; the item stays open and the §2 body figure is left as it was.

The tally below is §8's plus the four new rows: two confirmed, two corrected.

**Counts: confirmed 7 · corrected 4 · still open 4.**

## Second read: the advisor's verification pass, 25 Oct 2026 (proving-and-showing items)

The advisor's read of the proving-and-showing pack (GB-packs verification file, pass 3 §3). Its 13
items map onto §8's rows (its #12 repeats #6; its #13 is the life-events half of the adjustments row).
This section reconciles §8 and the gap-closure section above; the tally below covers the whole page.

| Item (§8 row) | Prior outcome | Advisor | Reconciled | Source |
|---|---|---|---|---|
| ECO in-use factors | confirmed | confirmed (ECO2t table: CWI/loft 35%; SWI 33% pre-1967 solid brick, else 25%) | **confirmed** | https://www.ofgem.gov.uk/system/files/docs/2018/01/eco2t_measures_table_-_jan_2018_-_v1.2.pdf |
| IPMVP options A–D | still open (secondary only) | confirmed | **confirmed** (DOE FEMP M&V Guide 5.0) | https://www.energy.gov/sites/default/files/2024-10/mv_guide_5_0.pdf |
| IPMVP routine / non-routine adjustments; life events | still open | confirmed (eqs 2-1, 2-2; occupancy as non-routine) | **confirmed** | same |
| G14 ~15% monthly CV(RMSE), calibrated simulation | still open, DISAGREES in the gap-closure read | confirmed: 15% / ±5% monthly, 30% / ±10% hourly; 20% is the regression-baseline figure | **confirmed**, secondary. A second independent quote (Burman 2020) agrees with the first and explains the 20%: it is a different clause. §2 corrected | https://discovery-pp.ucl.ac.uk/10117731/3/Burman_2020_BPA_SimBuild_JainN.pdf (secondary) |
| G14 savings uncertainty <50% at 68% | confirmed | confirmed | **confirmed** | https://onebuilding.org/archive/equest-users-onebuilding.org/2009-March/001184.html (secondary) |
| CalTRACK 365-day baseline | corrected (hourly needs no minimum) | confirmed (max_days = 365) | **corrected**. **DISAGREES**: the advisor read eemeter's compliance page; §8 read the CalTRACK methods 2.2.1.1–2.2.1.2, which carry the hourly exception | https://eemeter.readthedocs.io/caltrack_compliance.html |
| CalTRACK ~90% coverage | corrected (≤37 missing days; >90% of hours) | confirmed (0.9) | **corrected**. **DISAGREES** on the label only: same 90%, but §8's primary read gives the per-method rule | same |
| CalTRACK HDD/CDD balance-point search | confirmed | confirmed (30–90°F, ≤3°F steps; ≥10 non-zero, ≥20 total degree-days) | **confirmed** | same |
| CalTRACK hourly TOWT with occupancy | confirmed (CalTRACK 3.8) | still open (docs.caltrack.org blocked) | **confirmed**. **DISAGREES**: §8 read the methods page the advisor could not reach | — |
| CalTRACK built for portfolio aggregation | confirmed (CalTRACK 4.3.2.5) | still open | **confirmed**. **DISAGREES**: as above | — |
| Opower 1.4–3.3% | still open | confirmed: 1.4–3.3% by utility, average 2.0% | **confirmed**, secondary (J-PAL summary of Allcott 2011). Cadmus's 1.5–2.5% in years 1–2 sits inside it | https://www.povertyactionlab.org/evaluation/opower-evaluating-impact-home-energy-reports-energy-conservation-united-states (secondary) |

The four gap-closure rows above (PHE bands, condensing 2005, EST trial, Boiler Plus) are unchanged.

**Counts: confirmed 11 · corrected 4 · still open 0.**
