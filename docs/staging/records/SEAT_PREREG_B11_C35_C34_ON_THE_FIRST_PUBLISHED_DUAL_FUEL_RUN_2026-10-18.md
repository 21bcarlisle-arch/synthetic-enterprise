# Pre-registration: B11, C35 and C34 on the first published run of the dual-fuel book

**Written 2026-10-18 ~12:00Z. No dual-fuel run output has been read for this prereg, and no run has been made.**
Claim `predict-the-supplier-figures-on-the-first-dual-fuel-run` (Lane 0, seat). DEVELOPMENT.
Starting points: `docs/staging/WORKER_FINDING_THE_COMPANY_DECIDES_A_DUAL_HOUSEHOLD_PER_LEG_AND_C35_CHARGED_IT_TWO_RISES_FOR_ONE_BENEFIT_2026-10-18.md`
§§2–3; `docs/staging/SEAT_FINDING_B11_RESCALING_THE_KEY_OVER_THE_CUT_CLOSES_THE_LEVEL_TO_FLAT_AND_MOVES_IT_AWAY_FROM_THE_REALISED_RATE_2026-10-17.md`;
`docs/staging/records/SEAT_PREREG_C35_THE_RETENTION_RISE_THROUGH_THE_COMPANYS_OWN_CODE_AT_BOTH_HAZARD_ENDS_2026-10-17.md`.

## 0. Which run this is about: two corrections to the item that asked for it

- **316fbe5cd is not the first dual-fuel run.** `c136809f5` (the fuel is drawn from the home)
  was committed at 01:14Z on 18 Oct. The sim-runner then started runs at **02:03Z
  (`c136809f5`), 04:52Z (`0697a37a8`) and 07:42Z (`17a866aa9`)**. All three are on disk on the
  shared tree, at 92,743,401 bytes each, with three different sha256s. `316fbe5cd` started at
  10:30Z. I have read none of them. A grep of `docs/`, `tools/` and `background/` for their file
  names finds only runner markers, logs and claim stores. No finding reads their B11 or C35
  figures. `DIRECTION.yaml`'s "the first on the dual book" for 316fbe5cd is wrong on the same
  evidence.
- **The 19 Oct publish will almost certainly not carry 316fbe5cd.** The publisher holds every
  completion until the weekly window opens (`publish_freshness.content_publish_window`, Monday
  04:00 London = **2026-10-19T03:00Z**). Each completion before then logs `HOLD (weekly publish
  window)`, as the three above did. The publish carries the first run whose completion marker
  arrives after 03:00Z. Today's cadence is about 90 min of run and 78 min of pause, 2h49m start
  to start. Projected from 10:30Z, a run completes near 02:05Z (held) and the next starts near
  03:24Z and completes near **04:54Z Monday**. That run is at whatever HEAD the shared tree has
  near 03:24Z. Its sha cannot be named today. **This prereg is about that run:** the first
  `run_output_<sha>_20261019T*.json` whose marker is processed after 03:00Z. Equivalently, it is
  the run that `ed3dadd9d`'s successor publish commits as `run_output_latest.json.gz`.
- **What voids it.** These predictions are about the change of BOOK, holding the supplier fixed.
  If, between `d21526456` and the publish run's sha, a commit changes
  `company/analytics/forward_clv.py`, `company/crm/next_best_action.py`,
  `tools/retention_rise_count.py`, the population draw, or a `DecisionPolicy` default these
  readings pass through, then the grade has two variables. The grade must then say "I cannot
  attribute" and re-take the reading on the `17a866aa9` run as the one-variable control. (It is on
  the dual book, and its sha predates every such change.) If no such commit lands, any of the four
  dual-book runs should give the same figures to the digit at a fixed seed. **P0: the publish
  run's B11 and C35 readings equal those on the `17a866aa9` run**, unless a commit of that kind
  lands before it.

## 1. What changes between the books, said before anything is differenced

The old readings were taken on the 772-account book at `78f77c34e`, which was about 1% dual. The new
book is the origin `live_population()` measured in the C35 finding: **788 supply points in 447
households, 341 (76%) dual, both legs of each dual home acquired on the same date.**

- **A B11 "account" is a household.** `book_from_run_output` merges fuels under
  `_billing_account_id`. One hazard and one departure cover both legs, and a household departs
  only when its last leg's last month is behind it. On the old book, accounts ≈ supply points. On
  the new one, accounts ≈ 0.57 × supply points. **So "graded" falls by about 40% while supply
  points do not move.**
- **B11's segment label carries the fuel** (`f"{segment} {fuel}"`, with `dual` its own value).
  The flat hazard is fitted per segment. So most of the book moves into new `… dual` segments,
  each with its own flat hazard.
- **Departure is a household event in the world.** The move is drawn once per household, and the
  loss notice goes to every point of the household (C35 finding §2). The flat rule's miss is the
  regime (pre-crisis switching at 2020; the 2021–22 crisis exits in the fit window at 2022/23).
  That is world history, and the fuel mix does not change it.
- **A C35 "case" is a decision × one of three advice effects.** Off, a decision is a renewal row,
  which is one leg. With `--per-household`, it is one `(billing_account, term_start)` group. C35
  needs a `tools/decision_probe.py` output drawn on the dual book. **The publish run does not
  produce one.** A probe is its own engine run on the control path. Grading (2) and (3) therefore
  needs one probe run at the publish run's sha (or `17a866aa9` under the voiding rule), with
  `retention_rise_count` given that probe and the publish run's output. The old probe
  (`/var/tmp/retention_rise/probe_default.json`) is a 1%-dual book and must not be used. It would
  be a placebo (C35 finding §3).

## 2. B11: `backtest_run_output` at cuts 2020, 2022 and 2023 (switch key with `switch_on_default=True`, `rescale_over="fit_window"`)

Old (772 accounts): graded 253 / 256 / 266. Flat calibration (mean p − realised) +0.241 / +0.181 /
+0.072. Switch key vs flat, AUC difference: switchers 2023 **+0.103 (+0.002, +0.205)**, whole book
2023 **+0.133 (+0.056, +0.209)**. No clearance at 2020 or 2022.

- **B1. Graded** 125–175 at each cut (point 146 / 148 / 154 = old × 447/772). Why: households,
  not legs (§1). The old 0.33 graded share of accounts is held, because which homes are on supply
  at a cut is acquisition and departure history, and fuel does not change it.
- **B2. Flat calibration stays positive at all three cuts, and its order is kept (2020 > 2022 >
  2023).** Each value is within ±0.06 of the old one: 2020 in +0.18…+0.30, 2022 in +0.12…+0.24,
  2023 in +0.01…+0.13. Why: the miss is the regime, and a household's departure is one event, so
  merging legs neither doubles departures nor exposure. What could move it: dual homes are gas
  homes with larger bills, and if the world's switching responds to the size of the saving,
  dual segments switch more in both fit and hold-back. The sign of that on the *miss* is unknown
  to me, so I give it the width and no direction.
- **B3. The switch key's 2023 whole-book clearance survives; the switchers' 2023 clearance does
  not.** On ~58% of the graded accounts, intervals widen by about √(772/447) ≈ 1.31. Whole book:
  half-width ~0.10 against a point near +0.13, so it still clears (I put this at ~70%).
  Switchers: about 17 graded at 2023 instead of 30, half-width ~0.13 against +0.10, so **"cannot
  tell" (~65%)**. At 2020 and 2022, nothing clears flat for either outcome. EP17's rule still
  reads **not yet** in every case. If the switchers do still clear at 2023, B3 is wrong in the
  flattering direction, and it gets recorded as wrong.
- **B4. Dual segments appear in `hazard_by_segment`** as their own rows, holding about 3/4 of
  the graded households.

## 3. C35: `tools/retention_rise_count.py` on a dual-book probe, without and with `--per-household`

Old (260 renewal rows, 780 cases): **211/780 rescued at both hazard ends** (71 / 71 / 69 by
effect). Refusals: 408 with no published default (136 pre-2019 rows × 3), 158 where the rise is
above the headroom under the default, 3 where the advice needs no rise, 0 on the household floor.
Household keeps a median of 0.40 of its gross benefit (full window).

**The finding's §3 prediction, which is my starting point, corrected on one half.** It said
rescued decisions fall by about the dual share, and that the household's median kept share rises
from 0.40 "because one rise replaces two". The first half I keep. The second is keyed to the
wrong quantity. The tool's `kept` is per *decision*. A per-leg decision already records one
benefit minus one rise. Its error is that the household holds two such decisions against one
benefit, and per-decision `kept` cannot see that. The finding's own table at real inputs gives a
*lower* per-decision share per household (17.6 of 96, against 20.6 and 19.6 per leg), because the
household rise (2.15) is slightly above each leg's (2.06, 2.09). So:

- **C1. Per leg (switch off).** Renewal rows 220–320, because rows scale with supply points,
  which barely moved. The pre-2019 share of rows is 40–60% (old 52%), all refused "no published
  default". Rescued is 22–35% of cases. Of the cases from 2019, more are rescued than the old 57%
  (211 of 372). Why: a gas leg's headroom under the gas default is (default − offer) × ~11.5 MWh,
  against ~3 MWh for electricity, so "above the headroom" refusals fall.
- **C2. Per household.** Decisions = 0.55–0.60 × renewal rows (447/788 = 0.567, plus single
  legs renewing apart). **Rescued cases fall by less than decisions do: rescued(on) /
  rescued(off) is 0.60–0.80, not 0.57.** Why: summing both legs' headroom removes most of the
  dual homes' above-headroom refusals, while the advice's cost is charged once. So the rescue
  *rate* per case is higher on than off.
- **C3. Kept share.** The median per decision on is within −0.05…+0.02 of the median off, and
  off is within ±0.08 of 0.40. It does not rise. The real change is in the household, which pays
  one rise instead of two. Nothing the tool prints shows that, so it must not be read off `kept`.
- **C4. Hazard ends.** Total rescued differs by ≤10 cases between full window and cut-year
  window, both on and off (old: 0).
- **C5. Merge refusals on.** "Two hazards" and "two sets of estimates" are 0, since the hazard is
  keyed on the billing account and the estimates are the household's. "One leg renewing alone"
  is ≤10% of dual households' groups, because both legs open on one date with one fix length.

## 4. C34's joint-value floor across the same renewals

**What is counted, first.** In this instrument a case enters C35 only because C34's floor refused
it. At a share of zero (no rise), our forward-value change is negative (`value_change < 0`), so the
joint-value rule takes nothing. The cases C34 does *not* refuse are exactly `refused["needs no
rise"]`. **C34's refusals = cases − no-forecast − needs-no-rise.** The household's floor at share
zero never binds (advice benefits the household), so every C34 refusal is on our side.

- **J1.** C34's floor refuses ≥97% of cases, off and on (old: 777 of 780). On the dual book it
  is still positive-sum and negative on our side in every cell.
- **J2.** "Needs no rise" is ≤3% off. On, it is the same or higher, but ≤5%. Why: a summed
  household margin makes the hazard cut worth more against one £2–3/month given up.
- **J3.** Refusals on the household floor (the rise taking more than the advice gives) are 0,
  off and on, as on the old book.

## 5. How it will be graded (not this item)

After the publish lands, the first item is to name the run's sha and check the voiding rule (§0).
It then runs `backtest_run_output` at the three cuts with the switch key and `ranking_between`
against flat; runs one `decision_probe` on that sha; and runs `retention_rise_count` without and
with `--per-household`. Every prediction above is graded beside its result, and the wrong ones
are kept. The C34, C35 and B11 rows that the seat carries as wrong are re-taken from that grade,
not from this file.

**Book note, 2026-10-19 (seat).** The 19 Oct publish run (`8b6fea024`) predates `30246d6f0`, so its campaign wins are dual on **every** gas home: 172 of 172, 0 gas-only, against about 0.906 at the published rate. The readings here are taken on that always-dual campaign book. It holds about 413 dual households where the split rate gives about 397, roughly 4% fewer. Do not difference a later run's dual counts against these readings as if only the company changed. Reading and prediction: `docs/staging/records/SEAT_PREREG_THE_FIRST_RUN_WITH_SPLIT_CAMPAIGN_HOMES_AGAINST_THE_ALWAYS_DUAL_CAMPAIGN_BOOK_THE_19_OCT_RUN_CARRIES_2026-10-19.md`.

## 6. Grade, 2026-10-19 (seat): P0 and B11. C35 and C34 wait on the probe

**The run.** The publish is `2a195224b` (merged as `f8f3d0fd5`). Its `run_output_latest.json.gz` is
`run_output_8b6fea024_20261019T033010Z.json`, so the run sha is **`8b6fea024`**.

**Void rule (§0).** Between `d21526456` and `8b6fea024`, no commit touches `forward_clv.py`,
`next_best_action.py`, `retention_rise_count.py` or the population draw. Two commits touch the
supplier. `c002699e7` adds `save_offer.household_save_rates` behind a new
`DecisionPolicy.save_offer_decides_per_household`, default False. `c8e55febc` factors
`closed_ids_from_bills` out of `dd_balance_book` without changing what it returns. Neither changes
a default these readings pass through, so the grade is not voided. P0 was measured anyway rather
than argued.

Instrument: `backtest_run_output(path, cut, switch_on_default=True, rescale_over="fit_window")`.
Calibration is read from `departure_calibration`. Ranking is per-customer against flat: whole book
from `departure_ranking`, and by outcome from `error_by_outcome[o].ranking_against_stayers`.

| cut | graded (dual / elec / gas) | flat cal. | key cal. | whole book key − flat | switchers | movers |
|---|---|---|---|---|---|---|
| 2020 | 184 (132 / 46 / 6) | +0.242 | +0.219 | +0.046 (−0.011, +0.102) | 48: +0.052 (−0.010, +0.113) | 27: +0.035 (−0.050, +0.119) |
| 2022 | 192 (134 / 53 / 5) | +0.177 | +0.156 | +0.032 (−0.036, +0.100) | 26: +0.037 (−0.043, +0.117) | 16: +0.024 (−0.084, +0.133) |
| 2023 | 201 (146 / 50 / 5) | +0.088 | +0.066 | +0.075 (−0.013, +0.162) | 20: +0.040 (−0.069, +0.149) | 12: **+0.133 (+0.008, +0.258)** |

- **P0 (publish run equals the `17a866aa9` run): HELD.** The same script on
  `run_output_17a866aa9_20261018T074212Z.json` prints every figure above identically, to the digit.
- **B1 (graded 125–175 at each cut): WRONG, too low at every cut.** The graded counts are
  184 / 192 / 201. The share I held fixed did hold: graded plus excluded is **550** accounts at
  every cut, and 184/550 = 0.33. What was wrong is the household count. I scaled from 447, but
  this run's campaign is dual on every gas home (book note above), and its book merges to 550
  billing accounts.
- **B2 (flat calibration positive at every cut, order 2020 > 2022 > 2023, each within ±0.06 of the
  old value): HELD.** The readings are +0.242 / +0.177 / +0.088, against old values of
  +0.241 / +0.181 / +0.072.
- **B3 (the whole-book 2023 clearance survives; switchers at 2023 cannot tell; nothing clears at
  2020 or 2022): WRONG on its main claim.** The whole book at 2023 is +0.075 (−0.013, +0.162), which
  cannot tell. The point fell from +0.133, and the interval widened as predicted. Switchers at 2023
  cannot tell: HELD. Nothing clears at 2020 or 2022: HELD. **The one clearance left is movers at
  2023** (12 departers), and that is not a retention lever. EP17's rule reads **not yet**, and the
  switch key now clears flat on no outcome a retention action acts on, at any cut.
- **B4 (dual segments appear and hold about 3/4 of graded households): HELD.** The shares are
  0.72 / 0.70 / 0.73. The dual segment's flat hazard sits above the electricity segment's at every
  cut: 0.0204 against 0.0172 at 2020, and 0.0168 against 0.0129 at 2023.

**Seat rows that took B11 from the old book** must now be re-taken from this table. That applies
especially to anything citing the whole-book 2023 clearance (+0.133).

## 7. Why the whole-book 2023 clearance went (worker, 2026-10-19)

It was neither the sample nor the dual leg. **About 65% of the old +0.133 came from
cross-segment pairs where flat ranked worse than chance (0.409).** The old book's `resi gas`
segment carried the highest flat p and 2 departures in 37, and the key's 36+ band reordered
those homes. On the dual book those homes are dual, flat's cross-segment AUC is 0.545, and that
credit is gone. Of the fall of 0.058, 0.044 is that term and 0.014 is the within-segment term
(+0.108 → +0.075, inside noise). **The key's own AUC rose, 0.580 → 0.592.** Subsampling the old
run to 201 accounts leaves the point at +0.1325 (SD 0.022, 0.45% of draws ≤ +0.075). Dual and
single cannot be told apart (+0.068 against +0.117). Also, the old graded book was 33% dual at 2023. The 1% was its opening founders, and campaign
wins added the rest. Grade and figures:
`SEAT_PREREG_WHY_THE_SWITCH_KEY_LOST_ITS_2023_WHOLE_BOOK_CLEARANCE_ON_THE_DUAL_BOOK_2026-10-19.md`.
No supplier build is filed. The instrument change (grade the key within segment) is
`docs/staging/WORKER_FINDING_THE_SWITCH_KEYS_WHOLE_BOOK_GAIN_OVER_FLAT_WAS_TWO_THIRDS_FLATS_OWN_INVERTED_GAS_SEGMENT_2026-10-19.md`.

## 8. Grade, 2026-10-19 (seat): C35 and C34

**Instrument.** `tools.decision_probe` at `8b6fea024` (worktree `/var/tmp/probe-8b6fea024`, whose
later commits are salvage commits of `docs/context-handshake-latest.md` only, so no code is touched),
written to `/var/tmp/dualgrade/probe_8b6fea024.json`. Then `tools.retention_rise_count` on that probe
and `run_output_8b6fea024_20261019T033010Z.json`, without and with `--per-household`.

| | renewal rows | decisions | rescued / cases | by effect | no default | rise our side needs | needs no rise | kept (median) |
|---|---|---|---|---|---|---|---|---|
| off, full window | 182 | 182 | 144 / 546 | 49 / 49 / 46 | 294 | 105 | 3 | 0.345 |
| off, cut year | 182 | 182 | 144 / 546 | 49 / 49 / 46 | 294 | 106 | 2 | 0.310 |
| on, full window | 182 | **182** | 144 / 546 | 49 / 49 / 46 | 294 | 105 | 3 | 0.345 |
| on, cut year | 182 | **182** | 144 / 546 | 49 / 49 / 46 | 294 | 106 | 2 | 0.310 |

**Off and on are identical, and the reason was not foreseen.** Of the 182 rows, 178 are electricity
and 4 are gas. All 4 gas rows belong to opening founders (`SYN-2016-009`, `-163`, `-332`), and none
belongs to a dual household's gas leg. 129 of the 178 electricity rows are dual households whose gas
leg is absent. No `(billing_account, term_start)` group holds two rows. The probe writes a row only
when the world calls `roll_lifecycle_event`, and **the world draws a dual household's renewal once,
on electricity** (the 18 Oct worker finding §5). The run's whole lifecycle stream agrees: 370
electricity events against 13 gas, and no `…g` id among them. So on this book the C35 instrument
sees each dual household once, through its electricity leg's margin and headroom only. The gas leg's
margin and its headroom under the gas default are missing. **This is not a per-household count. It
is a per-household decision costed on one leg.** Filed as
`docs/staging/SEAT_FINDING_THE_DECISION_PROBE_SEES_A_DUAL_HOUSEHOLD_ONLY_THROUGH_ITS_ELECTRICITY_LEG_SO_C35_PER_HOUSEHOLD_MERGES_NOTHING_2026-10-19.md`.

- **C1 (per leg: rows 220–320; pre-2019 share 40–60%; rescued 22–35% of cases; from 2019, more
  rescued than the old 57%): rows WRONG, the rest HELD in number.** There are 182 rows, below the
  range. I scaled rows with supply points, and a dual household's gas leg is not a row (above). The
  pre-2019 share is 98/182 = 54%. Rescued is 144/546 = 26%. From 2019 the rate is 144/252 = 57.1%,
  against the old 56.7%. That is "more" by 0.4 pt, which is noise, and **the reason I gave is
  refuted**: gas headroom cannot lower refusals when no dual gas leg is in the instrument.
- **C2 (decisions 0.55–0.60 × rows; rescued on/off 0.60–0.80): WRONG.** Both are 1.00. The
  instrument has no pair to merge.
- **C3 (kept on within −0.05…+0.02 of off; off within ±0.08 of 0.40): HELD on full window, WRONG
  on cut year.** On equals off exactly, but vacuously. Off is 0.345 on the full window (−0.055) and
  0.310 on the cut year (−0.090, outside).
- **C4 (rescued differs by ≤10 between hazard ends): HELD.** The difference is 0, as on the old book.
- **C5 (no "two hazards" or "two estimates" refusals; one leg renewing alone in ≤10% of dual
  groups): HELD, but vacuous.** No group was merged.
- **J1 (C34's floor refuses ≥97% of cases, off and on): HELD.** 546 − 0 − 3 = 543, which is 99.5%.
- **J2 (needs no rise ≤3% off, ≤5% on): HELD.** 3/546 = 0.5% on both.
- **J3 (no refusals on the household floor): HELD.** None appear.

**What the 1%-dual wrong row is re-taken to.** C35 on the dual book reads **144/546 rescued at both
hazard ends** (old 211/780). C34's floor refuses 543/546 (old 777/780). Both are now **costed on the
electricity leg of each dual household**, so they are not yet a household reading. The per-household
switch cannot be graded on this instrument until the probe writes the gas leg beside its electricity
roll. Honest counts from `/var/tmp/retention_rise/per_renewal.py`: rescued with the rise actually
billed 91/182 (g=2, c=0.1 pt, module), all electricity.
