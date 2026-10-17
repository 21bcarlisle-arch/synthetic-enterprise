**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality`

# W2_36: theft now arises at a premise, and at the IA's own volume it looks exactly like a void

**Fate (2026-10-16):** ATOM -- the next W2_36 slice grades the company's screen
(`company/billing/theft_indicator.py`) against the world's thefts and voids together.

## What was built

This is the third item in the order for the director's ruling 4 of 2026-10-08
(`SEAT_PROPOSAL_THE_ORDER_FOR_VOIDS_VULNERABILITY_AND_THEFT_2026-10-08.md`): theft as a
premise-level study in the minutes tier. The new code is in `simulation/meter_reads.py`:

- `premise_theft_months` gives a premise a theft state as a two-state chain held stationary at
  `q6_theft_prevalence_domestic_electricity`, with turnover set by `q6_theft_months_before_detection`.
- `premise_theft_study` returns true use, what the meter registers, and the stolen kWh.

No run reads either function, by design: 52,000 customer-years buy about 30 detections.
Knowledge: `unbilled_energy_and_revenue_assurance.md` K4 and §5, plus a new register row,
`q6_theft_share_of_premise_use_unregistered`.

## Printed at real inputs (20,000 premises, 120 months, 333 kWh a month)

| Quantity | Value | Against |
|---|---|---|
| Theft stock, months 0 / 60 / 119 | 0.84% / 1.01% / 1.22%; mean 0.99% | register 1% |
| Stolen share of throughput | 0.99% | TEM 0.5–0.9%, AUG studies 1–2.5% (all sectors) |
| Premises that steal at some point in ten years | 5.8% | not published |

## The finding

**At the volume the IA implies, a domestic theft registers nothing.** The 2014 IA's case counts
are "consistent with" £250m only if each domestic case takes all of an average home's use. At its
own Table 4 inputs that gives £248m; at half the use it gives £166m. So the register's default is
1.0, and its partial-tamper end is a GAP.

At 1.0 a theft premise shows the company the same actual/EAC ratio of 0 as a B7 void, which the
world now also draws. A ratio screen alone cannot tell the two apart, whatever threshold is
chosen. What separates them in reality is outside the ratio:
- a void has no occupier, so letters go unanswered and a change of tenancy follows;
- a theft has someone living there, often paying.

Grading that is the next slice. **I cannot yet say** how many voids a ratio screen would send to
investigation for each theft it finds. That needs the world's void rate and theft rate on one
population. Prediction, written before it is run: at the defaults, voids outnumber thefts among
the screen's zero-ratio premises, because 1% of premises are stealing at any time while every
move-out opens a void.

## Mutation record

Each of these was run on a copy loaded into `sys.modules`, so the shared tree's file was never
mutated. Every one turned the theft tests red:
- theft never starts;
- theft never ends;
- the meter ignores the hidden share;
- the refusal of a zero share is removed.

A placebo run with the source unchanged stayed green.

## Graded: thefts outnumber voids in an empty month, and the window does the separating (worker, 2026-10-16)

**Correction beside the prediction above.** I predicted "voids outnumber thefts among the screen's
zero-ratio premises". **That is refuted.** Probe: `tools/theft_void_screen_probe.py`, using the
world's own moves, voids and thefts on one population. Control:
`tests/tools/test_theft_void_screen_probe.py`, mutation-proven over four arms plus a placebo.
Grades: `records/WORKER_PREREG_W2_36_WHAT_A_RATIO_SCREEN_FINDS_AMONG_VOIDS_AND_THEFTS_2026-10-16.md`.

The ratio cannot tell a void from a theft. **Length can.** A void runs 0.7 to 1.15 months and a
theft about 24. So what a screen flags depends on its window and its cut. The ratio itself decides
nothing.

| Flags per 10,000 premise-years | thefts | private voids | social voids |
|---|---|---|---|
| Month empty (ratio under 0.05) | about 1,100 | 0.2 | 112 |
| Month under 0.4 | about 1,100 | 848 | 430 |
| Month under 0.65 | about 1,100 | **1,740** | 669 |
| Year under 0.65 | 84–107 | 0 | 0 |

- An empty month is a theft about nine times in ten in a social let (1,166 of 1,278), and almost always in a private
  let. A private void (about 21 days) cannot empty a calendar month.
- Voids outnumber thefts only at a loose monthly cut, and only in private lets. That is where a
  ratio screen would send investigators to empty homes.
- An annual screen flags almost only thefts, but it sees about a tenth as many. It needs a theft to
  cover most of a calendar year, so it detects late.

**What this cannot say, carried as GAPs:**
1. **The void tail.** The world's void is one fixed length per tenure (the register gives a
   centre and a range, not a distribution). Empty-month voids come entirely from long voids. At
   the social high end (2.0 months) they rise from 112 to 502. A real tail of months-long voids
   (probate, empty-at-sale) is unpublished, so 112 is a floor.
2. **Owner voids** are a GAP (`q1_void_months_owner`). Owner rows show thefts only.
3. **Low-use occupied homes.** Use here is flat at the EAC, so the third source of flags is not
   priced. That is the next slice: run the same probe over the world's own household demand, so
   the screen's false positives include homes that simply use little.

**Fate (2026-10-16, after grading):** ATOM -- W2_36's next slice prices the third source (low-use
occupied homes, from the world's household demand) in the same probe.

## The third source priced: occupied homes flag by the shape of the company's expectation, not by low use (worker, 2026-10-16, late)

Pre-registration and grades:
`records/WORKER_PREREG_W2_36_WHAT_THE_SCREEN_FLAGS_AMONG_OCCUPIED_HOMES_2026-10-16.md`. The probe is
`tools/theft_void_screen_probe.occupied_screen_table`. It reads the published run's own book and
asks the company's own expectation for every month: `estimate_unread_kwh` over its last three
actual reads, or `opening_estimate_kwh` before its first read. The control is in
`tests/tools/test_theft_void_screen_probe.py`. It is mutation-proven: if the void is never
attributed, if the void never ends, if the company never learns from its reads, or if the
expectation ignores the profile, the control goes red. A placebo run stays green.

Beside the earlier table, per 10,000 premise-years:

| Cut | thefts | private voids | social voids | occupied homes (run book) |
|---|---|---|---|---|
| Month empty (under 0.05) | about 1,100 | 0.2 | 112 | **0** |
| Month under 0.4 | about 1,100 | 848 | 430 | 576 |
| Month under 0.65 | about 1,100 | 1,740 | 669 | **1,939** |
| Year under 0.65 | 84–107 | 0 | 0 | **0** |

- **The empty-month screen is still a theft screen.** No occupied home empties a period.
- **At a loose monthly cut, occupied homes are the largest source of flags.** They flag more than
  private voids and more than thefts. The flags are the expectation's shape error: weather-driven
  homes in summer, after a winter-heavy read window. They are not low use. A real screen keyed to a
  profile-shaped estimate would see the same thing in a storage-heated home on a domestic profile.
- **An annual window flags nothing occupied.** So the annual screen's flags stay almost all thefts.
- **Corrected beside my own premise:** in the run, a void is on the account. It is the incoming
  occupier's opening stub at 0 kWh. On a billing-period window it reads as an empty period
  (276 per 10,000 premise-years on the run's mixed-tenure book).

**GAPs carried.**
1. Whether the world's summer-to-winter swing in fabric homes matches published heating-season
   shapes. If it is too steep, the 1,939 is inflated. The flags concentrate in ten accounts, so
   this is the first thing to check.
2. The run book is one seed and mixed tenure, so it is not split by tenure the way the void table is.
3. The two populations differ: thefts and voids come from 20,000 synthetic premises per tenure,
   and occupied homes from the run's 633 accounts. The rates are per premise-year on each, so they
   sit side by side but are not one draw.

**Fate (2026-10-16, after this slice):** ATOM -- W2_36's remaining kinds (K5 meter faults, K6
settlement against billing) stand. GAP 1 is the next fidelity question for this screen.
**K5 knowledge first (worker, 2026-10-17).** `unbilled_energy_and_revenue_assurance.md` §K5 now
carries the legal in-service limits and the only published counts, which cover disputed meters
(2003–2014 electricity, 2011 gas). No population fault rate or fast/slow split is published, so a
world K5 build, after the 2026-10-19 publish, carries its prevalence as a named `None`.

## The company's screen now has two structural flags, and neither needed a ratio cut (seat, 2026-10-17)

Knowledge first: `unbilled_energy_and_revenue_assurance.md` §4a. No licence condition or code
prescribes a screening window or cut. The BSC's Long Term Vacant rule defines a void by its
*absence* of an occupier: two "Site Not Occupied" visits 75–215 days apart (P245). Up to 2% of
occupied homes use no gas (Ofgem, 20 June 2014). The flags are in `company/billing/theft_indicator.py`:
- `empty_period_flags`: zero advance between two actual reads on an **electricity** account while a
  named occupier was liable. A gas empty period is `not_screened`, and a period wholly the owner's
  void or "the occupier"'s is filed `void`.
- `annual_window`: at least 360 days of registered use over the company's own expectation. Its cut
  is `None`, so at default it reports `unscreened`.

Graded with this probe (`--structural`), beside the ratio screen's table above. Pre-registration
and grades: `records/WORKER_PREREG_W2_36_WHAT_THE_STRUCTURAL_FLAGS_FIND_2026-10-17.md`.

| Per 10,000 premise-years | theft | theft and void in one month | void alone | occupied (run book) |
|---|---|---|---|---|
| Ratio screen, month under 0.05 (earlier) | about 1,100 | n/a | 0.2–112 | 0 |
| **Empty period, named occupier** | 1,074–1,156 | 0–26 | **0** | **0** |
| Annual window, default | unscreened | unscreened | unscreened | unscreened |
| Annual window at 0.65 (instrument only) | 84–107 | 6–19 | 0 | 0 |

- The empty-period flag keeps the empty-month screen's theft count and drops its voids, with no
  threshold. It uses the occupier, as published vacancy practice does, instead of a ratio.
- **Not yet shown on a run:** the run book's void stubs are never judged, because the company has
  no opening read before an incoming account's first period. A real change of tenancy has one (an
  occupier's opening read). Whether the company should hold it is the next question here. The
  named-occupier leg is proven by the unit control and the synthetic table.
- Mutation record: the flag that always reads a named occupier, judging a span with no opening read,
  screening gas, and reading a short window as annual each red the control. Dropping the probe's
  void share reds the probe control. A placebo and one equivalence (resetting a span only at an
  actual read, which the loop already does) stay green.

## GAP 1 read: the ten flaggers are electric-heated, and their swing is outside the published range because their level is (worker, 2026-10-17)

Draw `the-fabric-homes-summer-swing-against-published-heating-shapes`. Measurement only; no world
code was touched. This was not pre-registered: the reading came first. The build it leads to is
pre-registered in `WORKER_FINDING_AN_ELECTRIC_HEATED_FABRIC_HOME_PRICES_ITS_PRIOR_BILL_AT_THE_GAS_RATE_AND_RUNS_TWO_TO_FOUR_TIMES_SERL_2026-10-17.md`.

**Population.** Same published run (`78f77c34e`). The ten accounts with the most own-reads flags
under 0.65 hold 239 of the 377. Heating and tenure come from the world's household register
(`HouseholdDemandRegister`). An `OCC-` account is matched to its premise's outgoing account by move
date. Each month's figure is true kWh per day over whole calendar-month billed periods.

**The comparator.** The gas finding's SERL series is for gas-heated homes. **Nine of the ten are
not gas-heated**: five storage, two direct electric, one air-source heat pump, one unresolved. SERL's
aggregated tables (figshare 25472560, v2) give electric-heated homes only as an annual level
(Figure_46 for 2022, Figure_13 for 2023), not by month. So the published range for their swing is
built from SERL alone:
- the base is the gas-heated homes' electricity median by month (Figure_4);
- heating and hot water take the shape of the same homes' gas median by month (Figure_4: DJ/JJA
  9.4 in 2021, 10.8 in 2022, 9.5 in 2023);
- they are sized to the electric-heated quartiles.

DJ/JJA is the mean of December and January over the mean of June to August.

| SERL-anchored DJ/JJA | p25 | median | p75 |
|---|---|---|---|
| Storage radiators, 2022 (6.9 / 12.5 / 17.5 kWh/day) | 1.35 | 2.83 | **3.83** |
| Storage radiators, 2023 (8.0 / 11.9 / 16.7) | 1.69 | 2.61 | 3.47 |
| Electric radiators, 2022 (6.7 / 10.6 / 15.6) | 1.35 | 2.40 | 3.48 |
| "Other electric", 2022 (9.9 / 15.4 / 21.3) | 2.20 | 3.45 | 4.42 |

**The ten, by month** (kWh/day, pooled 2016–2025):

| Account | Heating, tenure | Jan | Apr | Jul | Oct | Dec | DJ/JJA | kWh/yr |
|---|---|---|---|---|---|---|---|---|
| SYN-2016-127 | direct, owner | 64.7 | 32.3 | 12.6 | 33.1 | 61.8 | 4.90 | 12,849 |
| PROS-2017-0336 | storage, owner | 154.9 | 62.1 | 9.6 | 50.6 | 138.6 | **15.01** | 24,733 |
| SYN-2016-064 | storage, owner | 68.1 | 40.2 | 12.3 | 43.7 | 66.3 | 4.51 | 14,967 |
| SYN-2016-435 | storage, private | 57.4 | 22.1 | 8.2 | 23.8 | 52.1 | 6.77 | 10,243 |
| OCC-d8e674fa38de | gas (premise C8), owner; `hh_metered_reads` | 54.5 | 34.5 | 11.1 | 27.8 | 49.7 | 4.28 | 11,594 |
| PROS-2020-0189 | storage, private | 41.1 | 19.1 | 8.1 | 18.4 | 40.2 | 4.95 | 8,025 |
| OCC-6414723cb77a | unresolved, private | 56.2 | 20.1 | 7.9 | 18.8 | 50.0 | 6.73 | 9,493 |
| SYN-2016-012 | storage, private | 29.6 | 10.9 | 7.1 | 14.3 | 28.0 | 4.06 | 5,650 |
| SYN-2016-269 | heat pump, owner; legacy profile | 39.0 | 27.1 | 14.0 | 23.8 | 38.5 | 2.66 | 9,560 |
| PROS-2019-0246 | direct, owner | 53.1 | 20.1 | 12.2 | 20.0 | 48.4 | 4.28 | 9,627 |

**Their classes** (median per account, pooled; full table in `/var/tmp/fabswing/measure.out`):

| Class | n | DJ/JJA median [p25–p75] | JJA ÷ annual mean |
|---|---|---|---|
| Storage, fabric, all tenures | 15 | 2.55 [2.09–4.95] | 0.62 |
| Storage, fabric, owner | 9 | 2.11 [2.08–4.51] | 0.71 |
| Storage, fabric, private renter | 5 | 4.06 [2.10–4.95] | 0.46 |
| Direct electric, fabric (all owner) | 5 | 4.28 [2.83–4.90] | 0.45 |
| Storage or direct, legacy profile | 19 | 1.39 | 0.84 |
| Gas-heated, fabric | 204 | 1.16 [1.09–1.25] | 0.94 |
| Gas-heated, legacy profile | 187 | 1.39 | 0.84 |

**Verdict: outside the published range.** Nine of the ten (median 4.9) are above SERL's storage
p75 of 3.83. Only the heat pump (2.66) is inside. **The level is the main cause, not the shape.**
- Within one year, each home's DJ/JJA can be set beside the SERL envelope **at its own level**.
  For four of the ten (SYN-2016-127, SYN-2016-064, PROS-2019-0246, OCC-d8e674fa38de) it sits at or below
  that envelope in every year but one. Their swing is what published heating seasons give a home that uses that much.
- **What no published figure supports is how much they use.** They use 15–75 kWh/day, against
  SERL's storage p75 of 17.5 (2022) and electric-radiator p75 of 15.6. Nine of the ten are above
  those p75s every year; SYN-2016-012 (14.8–16.2) is the exception. Of the fabric storage homes with a whole year, the median uses 19.6 kWh/day
  in 2022 and 42.3 in 2023. SERL's medians are 12.5 and 11.9. The fabric direct-electric homes use
  29 against 10.6.
- **A shape excess remains in five.** At their own level, SYN-2016-435, PROS-2020-0189,
  OCC-6414723cb77a and SYN-2016-012 are 1.2–1.6 times steeper than the envelope.
  PROS-2017-0336 is about 2.2 times steeper. Its 15.0 is above the gas heating-and-hot-water
  shape's own DJ/JJA of 9.5–10.8, so even a home that was all heating could not reach it on that
  shape. Its summer is 9 kWh/day under a 24.7 MWh year.
- **Tenure** splits the storage class: private renters are at 4.06, owners at 2.11. The five
  storage homes rented privately carry four of the ten.

**What this says about the 1,939.** It is inflated, and by a world defect, not by the screen. The
flags concentrate where the world's electric-heated homes use two to four times what SERL measures.
A home at SERL's storage p75 would still swing 3.5–3.8 against the company's legacy-profile
expectation of 1.39, so electric-heated homes would still flag in summer. **I cannot yet say** how
far 1,939 falls. The build finding carries the prediction.

**The same reading on the gas question.** Fabric gas-heated homes read DJ/JJA 1.16 against SERL's
1.33–1.35 for gas-heated homes' electricity: **too flat**, which is the carried row
`a-gas-heated-homes-electricity-has-no-season`, measured again on the run book. The two misses run
in **opposite directions**, so no single cause explains both. The gas-heated miss does not inflate
the screen, because a flatter summer is flagged less.

**GAPs.**
1. No published monthly series for electric-heated homes was read. The envelope assumes their
   heating takes the season of gas-heated homes' gas. Possible sources are HES R66141 §15.3
   (Fig. 544–545, all electric heating) and Elexon PC2 coefficients (not in the repo).
2. OCC-d8e674fa38de's premise was matched by move date. The register gives that premise gas heating,
   but its trace is `hh_metered_reads`, not the fabric path. Its 11.6 MWh with a steep winter is
   not explained here.
3. Fabric electric-heated homes with a whole calendar year are few: 4 storage and 2 direct in 2022.

## The screen reaches the billing run, behind a switch that is off (worker, 2026-10-17)

**What was built.** Knowledge first: `unbilled_energy_and_revenue_assurance.md` §4b, what a
supplier must do with a flagged account. It is read from DCUSA Schedule 23 (the Revenue Protection
Code of Practice, v5.11) and the duties page. A lead engages an SLC 12A.6 investigation alongside
the TRAS score. The visit is unannounced, with a warrant only after access fails. The unrecorded
units are assessed by RPCoP Appendix 7. Nothing is charged before 12A.11(g)'s evidence of intent
or culpable negligence, and 21BA's 12-month limit does not apply (21BA.2(c)).
`company/billing/monthly_bill_assembly.build_monthly_bills` now calls
`theft_indicator.screen_billing_run` on every account it bills. That calls `boundary_read_status`
for an incoming account and `empty_period_flags` for every account, and records each flag with its
act. It runs only when the caller hands it a list, and `simulation/run_phase4c_on_phase2b`
hands one only under `DecisionPolicy.theft_screen_in_billing_run`, which is False everywhere. So
the 19 Oct publish computes nothing new and not one bill moves (the control asserts the bills are
equal either way). Control: `tests/company/billing/test_the_theft_screen_reaches_the_billing_run.py`.
It goes red when the run stops calling the screen, when the boundary read is not consulted, and
when a void is filed as a lead (three in-process mutants, all red).

**What the switch-on arm would flag and act on, on the published run book** (`run_output_latest.json`,
78f77c34e; `python3 -m tools.theft_void_screen_probe --occupied-run docs/reports/run_output_latest.json --billing-screen`).
The probe feeds the same `screen_billing_run` the book's own bills and reads, in the billing run's
shape. 987 accounts and 38,854 bills; 4 incoming electricity accounts could not be linked.

| Fuel / status / act | Flags | Accounts | Assessed unrecorded kWh | Assessed charge (£) | Unrecorded kWh, world's truth |
|---|---|---|---|---|---|
| electricity / void / `bill_the_void` | 16 | 16 | 0 | 0.00 | 0 |
| electricity / investigate / `refer_for_investigation` | 0 | 0 | 0 | 0.00 | 0 |
| gas / not_screened / `none` | 0 | 0 | 0 | 0.00 | 0 |

**Reading.** Switched on, the screen would refer no account and recover nothing. That is the right
answer for this book, not a dead screen. The run draws no theft (the world's theft is a study,
`premise_theft_study`), so there is nothing unrecorded to find, and the 16 voids are correctly kept
off the lead list. This was not pre-registered. It repeats the seat's structural grade of the same
day on the same book (16 spans, all `void`, 0 `investigate`), now reached through the billing
run's own function. Two instruments agree. The other three zeros are not evidence of anything:
no gas account has an empty span between two actual reads, and no named electricity account does.

**What it cannot yet say.** What the screen would recover on a book with theft in it. That needs the
world's theft in the settled run, not only in the study. Until then the assessed-charge column can
only be exercised by the control's synthetic lead (Appendix 7 method 1, priced at the account's own
billed commodity rate). Turning the switch on is a separate commit, after the 19 Oct publish is read.
