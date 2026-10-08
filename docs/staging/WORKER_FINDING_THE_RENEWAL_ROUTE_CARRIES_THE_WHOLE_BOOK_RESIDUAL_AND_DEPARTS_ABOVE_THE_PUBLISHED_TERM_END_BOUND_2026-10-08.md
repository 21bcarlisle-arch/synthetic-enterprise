**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

> **Reconciled 2026-10-08 (seat), one definition for both findings: per fixed-term ENDER, left the
> supplier within 42 days / 12 months of the term end.** Settled run to 2025-06-07 at `8c1e077c3`,
> resi electricity. **2017-2021: 14.2% within 42 days (29/204, CI 10-20%), 21.6% within 12 months
> (44/204, CI 17-28%). WITHDRAWN for 2017-2021:** bound 1 and bound 2 below multiplied or compared a
> per-ACTIVE-decision rate (41.9%) with per-ender and per-account figures; on the per-ender rate the
> world sits inside both. **REOPENED for 2024-2025 only:** 30.4% within 42 days (14/46, CI 19-45%);
> at 2025 that alone takes term-enders to ~9.5% of accounts against a published 10.4% total, and the
> 12-month rate is unobservable before the window ends. **Four draws (worker, 2026-10-08): 2024
> 20.0% (27/135) WITHDRAWN; 2025 29.3% (17/58, CI 19-42%) not shown to exceed, not settleable
> before the window ends -- result at the foot.** Verdict and corrected bound: the last
> section. The seat finding carries the same definition and verdict.

# The renewal route carries the whole book's residual, and departs above what the published record allows at a term end

*Filed 2026-10-08 as the fidelity defect named by
`SEAT_FINDING_THE_WORLD_LOSES_FORTY_PERCENT_AT_EACH_ANNIVERSARY_AGAINST_A_PUBLISHED_SIX_2026-10-08.md`
(tests 1 and 2 graded there). Fix it blind to company results. This finding does not touch the churn
draw.*

## The defect

The settled world's renewal route departs at **E[depart] 41.9% per renewal decision, 2017-2024**
(`python3 -m tools.measure_departure_level`, capture
`qep_g_second_qep_pass_anchor_departure_factors.json`): 35.0 / 28.6 / 43.3 / 42.7 / 44.7 at
2017-2021, **56.9 at 2024 and 67.8 at 2025**. The coin-drawn decision set reproduces it
independently (0.40 pooled), so it is the world and not the set.

The whole book is in band (17-21% at 2017-2020), so the LEVEL is right and the SPLIT between routes
is not. The mechanism is named in `tools/fit_year_level_anchor.py::svt_composition_refusal`: *"the
whole-book fit holds the SVT contribution fixed and solves the renewal anchor around it."* The
renewal anchor (`departure_level_anchor.YEAR_LEVEL_ANCHOR`, 2.0x to 20.8x) is therefore the residual
between the published total and whatever the SVT route and the world's fixed-term share leave. No
published term-end figure constrains it.

## Why it is outside the record, on published figures only

Two bounds, neither an invented number:

1. **Arithmetic against the total (2024-2025).** Departures at a term end, over all accounts, cannot
   exceed all switching. Ofgem State of the Market (January 2026) puts the GB fixed-term share at
   about one third by July 2025 and half that a year earlier. At 2025, 1/3 x 0.678 = 22.6% of accounts
   against a published total of 10.4%. At 2024, 1/6 x 0.569 = 9.5% against 9.0%. Both exceed the
   total before a single SVT household has switched. The ceiling the record allows on P(leave | term
   end) is 0.104 / 0.333 = **0.31 at 2025** and 0.09 / 0.167 = **0.54 at 2024**, even if every
   switch came from a term-ender.

   *[Seat, 2026-10-08: the arithmetic multiplies P(leave | ACTIVE decision) by the share of ALL
   accounts on a fix. About 63% of term-enders roll passively and are in the share but not the rate.
   Recomputed on the per-ender rate below: inside at 2017-2021 and 2024, near-binding at 2025.]*
2. **Composition from the trials (2017-2021).** EFTC (Ofgem 2019, n = 19,553): 6% external
   switching in the **six weeks** around term end, in both arms. A household that does not leave then
   rolls to the default, and default-tariff households leave at about 1% a month (CMOL control, 1.0%
   over 30 days; CMOC control 2.9%). That composes to roughly 6% + 11 x 1-3% = **17-39% in the year**.
   The world's 43-45% at 2019-2021 is above the top of that. This is a rough composition of two
   published figures with different populations, NOT an established term-end rate: the record
   publishes no annual departure share for a term-ender, and that gap is the knowledge item.

   *[Seat, 2026-10-08: the 43-45% compared here is per active decision; the composed range is per
   term-ender. The world's per-ender 12-month rate at 2017-2021 is 21.6%, inside 17-39%. The EFTC 6%
   is not the 42-day comparator either: it is the control arm after a letter sent a few days before
   term end, so it excludes households that had already acted on the statutory notice. It is a
   floor, as this bound says.]*

2017-2018 (35.0, 28.6) sit inside the composed range and are not shown wrong.

## What this is not

- **Not the price response.** On the decision set, offering 5-40% below the default moves pooled
  P(leave) only from 0.40 to 0.33 (0.399 / 0.403 / 0.400 to 0.328 / 0.331 / 0.329 on seeds 42 / 101 /
  202). At 2025 a 40% cut still leaves 0.54 against the 0.31 ceiling in bound 1. No market fix
  closes the gap, so the level is not a default-vs-fix artefact.
- **Not the whole-book level.** That is fitted to the published record and is in band. Re-fitting
  the whole-book anchor does not fix this; it is the constraint the fit lacks.

## What would fix it (for the W2 lane, blind to company results)

Give the fit a second constraint: a term-end departure share bounded by the published record (the
ceiling in bound 1 per year, the EFTC six-week external share as a floor) so the residual can no
longer land wholly on the renewal route. Where it then cannot meet both the whole-book band and the
term-end bound, the remainder belongs to the SVT route or the world's fixed-term share, and that is
the next measurement, not a number to pick. Knowledge first: a published annual departure share for
GB term-enders (Ofgem RMI or the EFTC follow-up) would replace the composed range.

## Who reads the wrong number today

Every retention figure divides by the share leaving: the save-offer decision set
(`tools/grade_save_offer_shapes.py`), the B8 holdout grade, and any retention arm on a settled run.
The shape RANKING there is likely to survive (reactive save first); the LEVELS are not.

NEXT for W2: add the term-end bound to `tools/fit_year_level_anchor.py` as a refusal before any
re-fit, then re-capture and re-fit; this finding's bound 1 is the control.
*[Superseded 2026-10-08 by the NEXT at the end: bound 1 as written is withdrawn, so it cannot be
the control. "Who reads the wrong number" above also narrows: the save-offer set's levels are
per active decision, which is that set's own population, not a world defect.]*

## Reconciliation with the seat finding: what each figure counts (seat, 2026-10-08, written before measuring)

This finding and the corrected head of
`SEAT_FINDING_THE_WORLD_LOSES_FORTY_PERCENT_AT_EACH_ANNIVERSARY_AGAINST_A_PUBLISHED_SIX_2026-10-08.md`
give opposite verdicts on the same base. They count different things:

| figure | numerator | denominator | where |
|---|---|---|---|
| 41.9% (this finding) | expected departures on the renewal route | **active renewal decisions**: the ~35% of fixed-term enders whose anniversary draws `rolls_active_renewal` true | `tools.measure_departure_level` |
| 0.40 (decision set) | departures at the default | the same active decisions, asked of every household | `coin_drawn_decision_set` |
| 7.8% (seat head) | left the supplier within 42 days of term end | **all fixed-term enders**, 80 founders to 2019 (9/116) | scratch probe, not landed |
| 6% (EFTC control) | external switches within 6 weeks | all customers ending a 1-year fix at one supplier | Ofgem 2019, §4.1 |
| 10.4% / 9.0% (bound 1) | all domestic changes of supplier in the year | **all accounts** | Ofgem / DESNZ |

The world splits a fixed-term end in two (`simulation/run_phase2b.py`, `renewals.build_renewal_schedule`):
an active decision, which leaves at the boundary with the renewal route's hazard; or a passive roll
onto the default for a year, which leaves on the SVT route's segment hazard. So **41.9% is
P(leave | active)**, not P(leave | term end). Bound 1 as written multiplies a per-active-decision
rate by a per-account fixed-term share, which is not a quantity: the ~65% passive rollers are in
the fixed-term share's population but not in the rate's. That is the error to test.

The comparable quantity is the share of **all** fixed-term enders who leave the supplier within 42
days (EFTC's window) and within 12 months (bound 1's window: with one-year fixes, every fixed
account ends one term a year, so fixed share x P(leave within 12 months | term end) is the share of
all accounts leaving from a term end in that year).

### Predictions (seat, 2026-10-08, before the run)

From one settled run to the window end at origin `8c1e077c3`, resi electricity, fixed-term ends:

- **Q1, 42 days, 2017-2021:** roughly 0.35 active x 0.39 renewal-route hazard + a small passive
  SVT share = **10-16%** (central 13%). Above EFTC's 6% by about 2x, so a gap survives at the
  boundary; the seat head's 7.8% sat at the low end on a 116-ender sample.
- **Q2, 12 months, 2017-2021:** Q1 plus the passive rollers' year on the default = **18-28%**.
- **Q3, 42 days, 2024-2025:** 0.35 x 0.57-0.68 = **20-26%**. 12 months (2024 only; the window
  ends 2025-06-07): **28-38%**.
- **Q4, bound 1 recomputed:** fixed share x the 12-month per-ender rate stays UNDER the published
  total at both 2024 (1/6 x ~0.33 = 5.5% < 9.0%) and 2025 (1/3 x ~0.25 at 42 days = 8% < 10.4%).
  So bound 1, on the right denominator, is predicted NOT to show a defect.
- **Q5, verdict:** neither finding is right as written. Bound 1 is withdrawn; a smaller gap
  survives against EFTC at the boundary (world ~2x the published 6% within six weeks), filed on W2
  with the per-ender rate as its control.

### Result (seat, 2026-10-08, after the run): Q1 Q2 Q4 held, Q3 refuted high, Q5 half right

Run: `simulation.run_phase2b.main()` to 2025-06-07 at `8c1e077c3` (31 min, 458 customers), resi
electricity, fixed-term ends inside the window, home moves counted separately and NOT as departures.
Probe: `/var/tmp/se-dep-recon/an.py` (not landed). The same probe on the seat head's own 2019 run
(`fid.pkl`, `fae73df3a`) gives 14/119 = **11.8%** at 42 days, not 7.8%: the head's figure prorated
an expected value and excluded ends after 2019-11-19; this is the realised count.

| term ends | n | left within 42 days | left within 12 months | route at the end (left at boundary / re-fixed / rolled passive) |
|---|---|---|---|---|
| 2017-2021 | 204 | **14.2%** (CI 10.1-19.7) | **21.6%** (CI 16.5-27.7) | 27 / 48 / 119 (+10 none after) |
| 2024 | 32 | 31.2% (CI 18-49) | 2/7 observable | 10 / 3 / 16 |
| 2025 | 14 observable | 28.6% (CI 12-55) | unobservable | 4 / 2 / 12 |
| 2024-2025 | 46 | **30.4%** (CI 19-45) | unobservable | 14 / 5 / 28 |

- **Q1 held** (14.2% in 10-16%). **Q2 held** (21.6% in 18-28%). **Q3 refuted high:** 30.4% against
  20-26%, because the active leavers' share at 2024 is 10 of 13 (77%), above the 57% the capture
  gave. On 46 ends this cannot be separated from noise.
- **Q4, bound 1 recomputed on the per-ender rate** (fixed share x per-ender rate against the published
  total; 2017-2021 fixed share ~0.35-0.45, the inverse of Ofgem RMI's 55-65% default share):

  | year | fixed share | per-ender rate | share of accounts leaving at a term end | published total | verdict |
  |---|---|---|---|---|---|
  | 2017-2021 | 0.35-0.45 | 0.216 (12 months) | 7.6-9.7% | 15.6-20.8% | inside |
  | 2024 | 1/6 | 0.312 (42 days, a floor on 12 months) | >= 5.2% | 9.0% | inside unless the 12-month rate exceeds 0.54 |
  | 2025 | 1/3 | 0.286 (42 days) | >= 9.5% | 10.4% | near-binding: leaves <= 0.9 pp for every default-tariff account |

  The 2025 row is upper-biased: accounts ending a fix in 2025 are those who fixed in 2024, when the
  share was rising from 1/6. At 1/4 it reads 7.2%. Q4 held for 2017-2021 and 2024; 2025 cannot be
  told on 14 observable ends.
- **Q5, half right.** Bound 1 is withdrawn as written. The predicted surviving gap "~2x EFTC's 6% at
  the boundary" is **not** a defect: EFTC's 6% excludes households who acted before the trial letter,
  so it is a floor, and 14.2% sits above it. What survives is 2024-2025 only.

### Verdict (seat, 2026-10-08)

**2017-2021: withdrawn.** On the per-ender definition the world is inside every published bound:
above the EFTC floor at 42 days, inside the composed 17-39% at 12 months, and term-end departures are
under half the published total. The 41.9% is a correct P(leave | active decision); it was never a
per-ender rate. It still bears on the save-offer decision set, whose leaving base is the active
population (the seat finding's head already says so).

**2024-2025: reopened, not shown.** The per-ender 42-day rate (30.4%) at a 1/3 fixed share uses
almost all of 2025's published switching before any default-tariff household moves. That is a
candidate W2 defect, held open on 46 ends with a CI of 19-45%.

**The corrected control for W2, replacing bound 1:** for each year, fixed-term share x P(leave within
12 months | fixed-term END, all enders) <= the published total, with the 42-day per-ender rate >=
EFTC's 6% as the floor. Never the renewal route's per-decision E[depart]. Settle 2025 on more than one
seed before any re-fit; the 12-month rate at 2024-2025 is not observable inside a window ending
2025-06-07, so the 42-day rate is the only measurable leg there and is a lower bound.

NEXT for W2 (supersedes the line above): a multi-seed per-ender count at 2024-2025 against the
corrected control, before any change to the level anchor or the churn draw. If 2025 then exceeds it,
add the corrected control to `tools/fit_year_level_anchor.py` as a refusal and re-fit blind to company
results.

## Multi-seed per-ender count, 2024 and 2025 (worker, 2026-10-08)

### Design and predictions (written before the runs)

**What varies.** Four settled runs to 2025-06-07 at origin `3ff16bada`: the base run and the renewal
dice re-rolled at floor seeds 11111, 22222, 33333 through `run_value_cycle_ab._churn_roll_redraw_patch`
(the existing floor leg, no code change, every account re-rolled, the patch asserted to fire). The
BOOK is held: a different book seed is `EP17_varied_population_draw`, the director's, and no record
authorises one. So the four runs are four draws of the same 458 households' term-end dice, not four
populations. The interval below is the pooled Wilson interval over enders; it understates the
book-to-book spread, and says so.

**What is counted.** Per resi electricity fixed-term ENDER (the reconciled definition above): left the
supplier within 42 days, and within 12 months, of the term end. Home moves are not departures. Inside
a window ending 2025-06-07 the 12-month leg is observable only for 2024 ends up to 2024-06-07, and
not at all for 2025; the 42-day leg for 2025 ends up to 2025-04-26.

**The bound, per year.** Fixed-term share x per-ender rate <= published switching total. The
per-ender ceiling is total / share: **2024: 0.090 / (1/6) = 0.54. 2025: 0.104 / (1/3) = 0.31**, or
0.42 at a 1/4 share (2025's enders fixed during 2024, when the share was rising from 1/6).

**Predictions:**

- **P1, 2024, 42 days:** pooled 22-34% (base seed alone was 10/32). Inside 0.54.
- **P2, 2024, 12 months, ends to 2024-06-07:** 30-42%. Inside 0.54 at the top of its interval.
- **P3, 2025, 42 days:** 20-34%, point under 0.31, interval upper end above it. Not distinguishable
  from the 1/3-share ceiling; inside the 1/4-share ceiling.
- **P4, verdict:** no year shown to exceed the bound. The 2024-2025 gap is withdrawn beside its claim;
  the corrected bound stays the W2 control. If P3's point estimate lands above 0.31, the 2025 gap
  survives and stays filed on W2.

### Result (worker, 2026-10-08, after the four runs): P3 and P4 held, P1 and P2 refuted low

Four runs at `1925b7365` (= `3ff16bada` + this doc), resi electricity, window end 2025-06-07. The
floor patch fired on every seeded run (119, 112, 117 renewal rolls redrawn; base untouched).
Probe: `/var/tmp/se-w2te/pool.py` over `/var/tmp/se-w2te/s*.pkl`.

| Term ends | Leg | base | 11111 | 22222 | 33333 | Pooled | CI95 | Per-ender ceiling |
|---|---|---|---|---|---|---|---|---|
| 2017-2021 | 42 d | 29/204 | 28/210 | 32/202 | 35/200 | **15.2%** | 13-18 | — (EFTC floor 6%) |
| 2017-2021 | 12 m | 44/204 | 43/210 | 45/202 | 47/200 | **21.9%** | 19-25 | composed 17-39% |
| 2024 | 42 d | 10/32 | 6/33 | 7/34 | 4/36 | **20.0%** | 14-28 | 0.54 (share 1/6) |
| 2024, ends to 06-07 | 12 m | 2/7 | 1/7 | 2/7 | 0/7 | **17.9%** | 8-36 | 0.54 |
| 2025, ends to 04-26 | 42 d | 4/14 | 4/16 | 6/13 | 3/15 | **29.3%** | 19-42 | 0.31 (1/3) · 0.42 (1/4) |
| 2024-2025 | 42 d | 14/46 | 10/49 | 13/47 | 7/51 | **22.8%** | 17-29 | — |

- **P1 refuted low:** 20.0% against a predicted 22-34%. The base seed's 10/32 was the high draw of
  four; the 30.4% that reopened 2024-2025 was one draw's luck, not the world's rate.
- **P2 refuted low:** 17.9% against 30-42%. It is BELOW the 2024 42-day rate only because the two legs
  count different enders (the 12-month leg sees only the 28 ends before 2024-06-07); it is not a
  12-month rate below a 42-day one.
- **P3 held:** 29.3%, point under 0.31, interval 19-42% straddling it. Inside the 1/4-share ceiling.
- **P4 held:** no year is shown to exceed the bound. The 2017-2021 withdrawal also survives four
  draws (15.2% / 21.9%).

### Verdict (worker, 2026-10-08)

**2024: withdrawn.** 20% per ender at a 1/6 share is 3.3% of accounts against a 9.0% total; the
interval sits wholly inside the ceiling.

**2025: not shown, and not settleable inside this window.** Which share applies: a 2025 term end is
the end of a fix taken in 2024 (most are 12-month), so the share is 2024's rising one, between 1/6
and 1/3, not 2025's 1/3. At 1/4 the 42-day point puts term-enders at 7.3% of accounts against 10.4%;
at 1/3 it is 9.8%, 94% of the total before any default-tariff switch or any departure later than 42
days. The control's leg is the 12-month rate, which the window cannot observe for a single 2025 end,
and the 42-day rate is only its floor. So the gap is withdrawn as a DEFECT CLAIM (nothing measured
exceeds the bound) and is NOT cleared. No refusal goes into `tools/fit_year_level_anchor.py` and
there is no re-fit: the NEXT above made both conditional on 2025 exceeding, and it does not.
The churn draw and the level anchor are untouched.

**What this cannot say.** The book is held, so the four runs are four rolls of the same households'
dice; the interval understates book-to-book spread. A varied book is `EP17_varied_population_draw`
and is the director's.

**NEXT for W2:** none on this count. A 12-month leg for any 2025 end needs settled data into 2026,
past the 2016-2025 record, so it cannot be measured here at all. The corrected control stays as
written and 2025 is held at "inside on the point, open on the interval".
