**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used` · **Claim:** `d48-slice-4-retire-the-worlds-estimator-and-attribute-the-electricity-residual`

# D48 slice 4: the feed no longer estimates, and the electricity residual comes from the world's flat gas-heated homes

## Where the work came from

The duplicate-work note said this id was already held. The holder was this invocation's own
draw: the claim was 23 seconds old, and no other process named it. The premise was not spent.
`1cab58412` left both loose ends open and said so.

The predictions were filed before any measurement, in
`records/SEAT_PREREG_D48_SLICE_4_THE_ELECTRICITY_RESIDUAL_AND_THE_OPENING_ESTIMATE_2026-10-06.md`.
Every measurement below uses the slice 3 capture (`run_phase2b()`, 261,066 settled records, 87
leavers), with bills built on that one world.

## A. One estimator, and it is the company's

**What changed.** `simulation/meter_reads.simulate_read` now reports only whether a read
arrived. An estimated event carries no figure. `ReadArrivalFeed.read_for` no longer takes the
company's trailing reads or day counts. Those were company state sent across to the world only
so the world could do the company's arithmetic (EP8 pass 5,
`docs/design/EP8_ESTIMATION_CUT_DISCOVER_2026-09-07.md` §3, sized exactly this move).

Before an account's first actual read, the company now bills its registry EAC (electricity) or
AQ (gas), spread over the period by the published profile:
`company/billing/unread_month_estimate.opening_estimate_kwh`. Where registration carried no
figure (3 domestic electricity points in this book), Ofgem's TDCV MEDIUM band stands in. That is
the same fallback the opening direct debit already uses. After the first read, the slice 3
estimate from the company's own reads is unchanged.

**What it removed.** For the opening period the world used to send `true_consumption_kwh` as the
"estimate". On this world, 471 estimated bills (345 electricity, 126 gas) equalled the
household's real use to the penny. That was the defect filed on 2026-09-07
(`done/SEAT_FINDING_THE_WORLD_ESTIMATES_A_NEW_CUSTOMERS_CONSUMPTION_AT_EXACTLY_THE_TRUTH_…`).
With the estimate made company-side it can no longer be written at all: no true figure is in
scope there.

| Shaped estimator, same world | Before | **After** |
|---|---|---|
| Elec December net / gross | +3.2% / 17.3% | **+4.2% / 21.3%** |
| Elec June net / gross | +1.6% / 15.6% | **+3.7% / 19.9%** |
| Gas December net / gross | −6.5% / 16.3% | **−6.6% / 16.6%** |
| Gas June net / gross | −3.8% / 16.1% | **−2.5% / 18.0%** |
| Per-bill \|error\| / billed kWh, elec / gas | 26.2% / 18.6% | **29.9% / 20.5%** |
| Estimated bills exactly equal to use | 471 | **1** |
| Elec barred kWh (K3) | 2,078 | 2,180 |

**The D48 grades rise here because the earlier ones were flattered.** Every earlier slice's
gross figure counted the 471 perfect openings as a success of the estimator. The new figures
are the first that contain no estimate made from the truth.

**Predictions scored:**

| | Result |
|---|---|
| A1: only opening estimates and their run's catch-up move | **right**. 470 opening estimates and 70 first-actual catch-ups moved. No other bill moved |
| A2: elec per-bill error rises by more than 0.5 pp | **right** (+3.7 pp) |
| A3: December/June net moves by less than 2 pp for either fuel | **wrong for electricity June, by 0.1 pp** (+2.1 pp). Right for the other three |

**Controls and the mutations that red them** (each run against the edited tree, then reverted):

| Mutation | Red |
|---|---|
| Opening period uses the shaped-from-reads path (never reaches registry) | `test_the_billing_run_bills_only_its_own_estimate_…` |
| Opening estimate reads `eac_kwh` for gas | `test_the_opening_estimate_is_the_registry_figure_…` |
| No TDCV fallback (`band=None`) | `test_the_opening_estimate_is_the_registry_figure_…` |
| Feed sends a figure again | `test_the_feed_reports_status_and_never_a_figure_to_bill`, `test_the_estimate_is_a_belief_not_a_read_of_the_truth` |

## B. The electricity residual is the world's, not the estimator's

Slice 3 left two moves unexplained: electricity June gross rose (12.9% → 15.6%) and barred kWh
rose (1,230 → 2,078). The test was each household's own winter/summer ratio (Dec–Feb kWh/day
over Jun–Aug, from its **actual-read** bills of 28 days or more only).

**The world's electricity households are mostly flat.** Of the 85 households with both
seasons read, **57 have a ratio below 1.15**, and the tercile cuts fall at 1.00 and 1.09. The
published profile is 1.49. **56 of those 57 are gas-heated fabric premises.** The legacy PC1
path the other households settle on has a ratio of 1.39 by its own base shape (12.49 kWh/day in
winter, 8.99 in summer). So the flatness is the fabric demand path's. It is filed separately
(`SEAT_FINDING_THE_FABRIC_PATH_GIVES_A_GAS_HEATED_HOMES_ELECTRICITY_NO_SEASON_2026-10-06.md`).

**June electricity, by the household's own ratio (flat feed estimate → shaped):**

| Own ratio | Runs | Gross | Net |
|---|---|---|---|
| Flattest third (< 1.00) | 76 | 2.3% → **9.2%** | −0.6% → +4.2% |
| Middle third (1.00–1.09) | 119 | 3.4% → **13.3%** | 0.0% → +2.3% |
| Steepest third (≥ 1.09) | 56 | 32.9% → **25.9%** | +2.1% → +4.7% |
| Not established | 28 | 13.5% → 10.9% | −12.5% → −7.3% |

December shows the same pattern: steep 43.9% → 30.9%, flat and middle about 3% → 10–13%. The
seasonal shape is right for the households that have a season and wrong for the flat majority.
Net bias still improved because the steep households carry most of the kWh: 31% of billed
electricity sits in the 11 households above 1.6.

**The barred runs** (23 runs barred in either arm; full list in `/tmp/d48s4/an.out`, regenerable
with `/tmp/d48s4/b.py` and `an.py`). The three largest increases are +376, +250 and +185 kWh,
on households with ratios of 0.94, 1.08 and 1.04. Every run whose barred kWh rose belongs to a
household with a ratio below 1.1. The mechanism: with a winter or spring window, the shaped rate
divides by a high profile weight, the summer months are then under-billed, and the shortfall
runs past 12 months. The decreases are the mirror case: summer windows (ending June to August)
whose shaped estimate over-bills the winter.

| | Result |
|---|---|
| B1a: 5 or fewer runs differ; 70% or more of the increase in 3 or fewer | **wrong** on the first clause: about 20 runs differ, in both directions. The top three carry 810 of the +848 kWh net, but only because the offsetting runs cancel |
| B1b: increasing runs have ratio < 1.49 and windows ending October to March | **right on ratio** (all below 1.1). **Wrong on the window**: 7 of 11 end October to March, and 4 end April to June |
| B2a: flattest third, June gross higher shaped | **right** (2.3% → 9.2%) |
| B2b: steepest third, June gross lower shaped | **right** (32.9% → 25.9%) |
| B2c: flattest third carries most of the increase | **wrong**. The middle third carries more (+26,342 kWh against +7,904). Both are far below 1.49, so the cut that mattered was the published ratio, not the terciles |
| B2d: the refutation case (all terciles rise alike) | did not occur. The household-shape account stands |

## What this means

The estimator now does what a real supplier's does. What remains is whether the world's
households are right to be flat. If the fabric path is fixed to carry the seasonal swing that
PC1 households show, the flat majority shrinks, and the shaped estimate's gross error should
fall with it. That change belongs to the world lane, on published evidence, and it is decided
blind to this grade. This finding does not move it.

Not done here: `consecutive_estimated_count` still round-trips through the world as `+ 1` of a
counter the company holds (EP8 pass 5 §3). It is a pure increment and changes no number, so it
was left alone rather than widening the seam change.
