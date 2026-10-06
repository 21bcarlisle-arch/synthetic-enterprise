**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used` · **Claim:** `d48-slice-3-a-seasonal-estimate-for-the-unread-month`

# D48 slice 3: the unread month is now estimated with the season, and the gas bias is gone

## Where the work came from

At draw time the duplicate-work note said this same id was already held. The holder was this
invocation's own draw. The only live seat on the item was this one, and no rival `surgical_land`
was running. The premise was not spent: `06cda5325` graded the bias and left the estimator
unchanged.

The predictions were filed first, in
`records/SEAT_PREREG_D48_SLICE_3_A_PROFILE_SHAPED_ESTIMATE_2026-10-06.md`. That was before the
world was captured and before the profile numbers were in hand.

## What changed

**Who makes the estimate.** It used to be computed on the world side, in
`simulation/meter_reads.simulate_read`, and handed to the company as part of the read event. A
bill estimate is the supplier's own work. The company now makes it in
`company/billing/unread_month_estimate.py`, from two things it holds:

- its own last three actual-read periods;
- a published monthly shape.

The feed's figure is used only in the opening period, where the company has no read to derive an
estimate from. The read event is replaced as well, so the published read log carries the estimate
the bill was priced on.

**The method** is how settlement turns a meter advance into an annual rate (an Elexon EAC; a
Xoserve AQ against the end-user category's load profile):

- divide the window's kWh by the profile weight of the days it covers;
- multiply by the profile weight of the period being billed.

With every day weighted equally this reduces to the old pro-rata-by-day estimate. A test asserts
exactly that.

**The shape.** DESNZ Energy Trends 5.5 and 4.2 (domestic, 2023-2025 average) stand in for
Elexon's PC1 profile and Xoserve's EUC01B profile. Both of those are gated to settlement parties.
The research is in `docs/market_research/how_a_supplier_shapes_an_estimate_for_an_unread_month.md`.
It names two gaps:

- the stand-in is actual weather, not seasonal normal;
- it is dated later than most of the run.

## Before and after: same captured world, one variable

The decade world was run once (`run_phase2b()`, 261,066 settled records, 87 leavers). Bills were
then built under three estimators. Grades are pooled over every December, then every June, from
2016 to 2024. "Gross" is the summed absolute true-up as a share of the run's billed kWh.

| | Baseline (feed's flat estimate) | Flat weights, company-side | **Shaped** |
|---|---|---|---|
| Elec December net / gross | +10.30% / 17.3% | +10.35% / 17.3% | **+3.2% / 17.3%** |
| Elec June net / gross | −1.74% / 12.9% | −1.72% / 12.9% | **+1.6% / 15.6%** |
| Gas December net / gross | +23.85% / 53.3% | +23.85% / 53.3% | **−6.5% / 16.3%** |
| Gas June net / gross | −26.25% / 43.7% | −26.33% / 43.7% | **−3.8% / 16.1%** |
| Per-bill \|error\| / billed kWh, elec | 25.9% | 25.9% | 26.2% |
| Per-bill \|error\| / billed kWh, gas | 59.0% | 59.1% | **18.6%** |

- The baseline column reproduces slice 2 to the decimal.
- The flat-weights column moves the estimate to the company side and changes nothing else. It
  matches the baseline within 0.1 pp. The remainder is the 29 February weight. So the shape is the
  only thing that moved the third column.

**Predictions, scored against the measurements:**

| Prediction | Result |
|---|---|
| P1 Elec December \|net\| < 5% | right (+3.2%) |
| P2 Gas December \|net\| < 10% | right (−6.5%) |
| P3 Elec June \|net\| < 5% | right (+1.6%) |
| P4 Gas June \|net\| < 10% | right (−3.8%) |
| P5 Gross falls everywhere; gas December below 35% | **wrong for electricity**: December unchanged, June rose 12.9 → 15.6%. Right for gas (16.3%) |
| P6 No opposite-signed residuals over 5% | right. Both fuels keep one sign: electricity slightly under-bills, gas slightly over-bills |
| P7 K2 unchanged within 0.5 pp | right (+0.3 and +0.4 pp) |

## Is the world's season the published one?

The book's own shape was measured from actual-read full-month bills (kWh per day, by calendar
month). Only the company's reads were used.

| | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Elec, book % | 11.6 | 9.9 | 10.1 | 8.0 | 7.2 | 6.2 | 6.5 | 6.5 | 6.5 | 8.1 | 9.9 | 9.7 |
| Elec, published % | 10.8 | 8.9 | 9.1 | 8.1 | 7.3 | 6.7 | 6.8 | 7.0 | 7.3 | 8.2 | 9.7 | 10.2 |
| Gas, book % | 15.8 | 12.5 | 12.7 | 9.1 | 5.7 | 2.9 | 2.2 | 2.3 | 3.5 | 7.2 | 12.0 | 14.0 |
| Gas, published % | 17.1 | 13.4 | 12.3 | 7.9 | 4.1 | 2.6 | 2.3 | 2.3 | 3.4 | 7.1 | 12.2 | 15.2 |

The two shapes agree closely. Gas is published slightly steeper in December and January than the
world is, which fits gas over-billing slightly at December (−6.5%). That fit is consistent with
the data but has not been tested one variable at a time.

## What I did not predict

**K3, the barred share of under-billed kWh, rose:**

- **Gas: 1.25% → 3.11%.** The share rose because its denominator collapsed. Under-billed kWh fell
  from 303,044 to 82,468 (−73%). Barred kWh fell too, from 3,800 to 2,566 (−32%). Less energy is
  barred, out of a much smaller pool of under-billing.
- **Electricity: 1.05% → 1.80%.** Barred kWh **rose**, from 1,230 to 2,078, over 16-17 barred
  true-ups. I cannot yet say why. The count is small enough that one or two long runs could carry
  the whole difference. The test is to list the barred runs under both estimators and diff them.

**Electricity gross did not fall, and June got worse.** The likely reason is that household-level
electricity shapes vary more than one profile class allows: electric heating and Economy 7
households look different from PC1 averages. The published table blends PC1 and PC2. This is not
established. The test is to split the June gross by the household's own winter/summer ratio from
its actual reads.

## Left in place, and why

- `simulation/meter_reads.simulate_read` still computes the flat estimate. The company now
  overrides it wherever it has a read. The world-side estimator survives for the opening period
  and for `generate_meter_read_log` (tests and standalone analysis only). That makes two
  estimators, one of them now nearly dead. The next step is for the feed to stop estimating, and
  for the company to make the opening estimate too, from the registry EAC/AQ that
  `annual_consumption_estimate` already holds. That change is on the sim side of the seam.
- `tests/saas/test_a_published_bill_shock_can_be_recomputed.py::test_the_baseline_is_present_exactly_when_the_shock_is`
  is red in this worktree against the committed `docs/reports/run_output_latest.json` (from the
  `a88fb2436` publish): 4,015 bills publish a baseline with no ratio. It reads the artefact, not
  this code, so this change did not cause it. Recorded so the next reader does not attribute it here.

## Controls and the mutations that red them

`tests/company/billing/test_unread_month_estimate.py`:

- with flat weights, the estimate equals the old one;
- the season works both ways, for both fuels, in one statement;
- each shape sums to one and peaks in winter;
- with no read or no shape there is no estimate;
- the billing run bills its own shaped estimate, and uses the feed's only without a read, both in
  one statement.

`tests/company/billing/test_billing_accuracy.py` now withdraws the shape with an autouse fixture.
Those tests grade the measure, and the scripted flat estimate is their instrument.

| Mutation | Tests failing |
|---|---|
| Read event not replaced | 1 |
| Shaped estimate not used for pricing | 1 |
| Window of one read | 1 |
| No season | 2 |
| Month length ignored | 1 |
| Empty-window guard dropped | 0. It was an equivalence: an empty window has zero weight, and the `weight <= 0` guard already returns None. The redundant clause was removed |

## What this changes for the customer

A household whose meter goes unread in winter is now billed close to what it is using, instead of
its autumn rate. For gas, December under-billing was +24% of billed kWh, which was paid later as a
catch-up. That catch-up mostly disappears. In summer the household is no longer over-billed by a
quarter. In the D48 grade both moves show up as gas gross error dropping from about half to about
a sixth.
