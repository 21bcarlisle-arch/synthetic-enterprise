**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The fix-0 capture's twice-counted departures are the world re-asked at an offer, not a home's two fuels

*Lane 0 item `one-home-one-departure-decision-across-two-fuels`. Inputs: `/var/tmp/se-fix0-capture/departure_factors_fix0.json`
(282 rows, capture r2 at `f0012484a2`), its `capture.log` roster, `tools/capture_departure_factors.py`,
`simulation/run_phase2b.py` and `simulation/retention_offer.py` at `1c14ccff96`.*

## For the director, in plain English

The refit was blocked because 22 accounts appeared to leave twice. The item said these were dual-fuel homes
deciding once per fuel. **They are not.** The world already makes one leave-or-stay decision per home: the
electricity leg rolls, and the gas leg follows it (`departure_decision_leg`, in place since 16 Sep). What
doubled the count is the measuring tool. When the company makes a retention offer or a save offer, the world is
asked again, on the same dice, what the household would do at the lower price. The capture tool recorded each
of those "what if" answers as a separate decision. The world was right. The tool's count was wrong.

## The evidence (read from the capture, before any change)

- In **19 of the 35** duplicate (account, date) pairs, the account has **no gas leg** in the run's roster
  (`SYN-2016-045`, `SYN-2016-163`, …; no `…g` in `Gas customers:`). A home that buys one fuel cannot make two
  fuel decisions.
- In **35 of 35** pairs, the second row has a lower `new_rate_gbp_per_mwh` than the first, by about 3–5%. Two fuels
  would carry two unrelated rates. A discount produces exactly this pattern.
- `retention_modifier` is `None` on every row, because `ask_world_at_offer` passes a discounted **rate**, not a
  modifier. The capture's wrapper sits on `run_phase2b.roll_lifecycle_event`, and both re-asks
  (`ask_world_at_offer` at `run_phase2b.py:5070`, the save re-ask at `:5177`) resolve that name at call time. So
  the wrapper records every call.
- The "1 split" pair (churned, then renewed) is **an offer that worked**: the household leaves at the full rate and
  stays at the offer. The 1 triple is an offer followed by a save.

So the 1 split is not world behaviour, and the world needs no repair. The repair belongs in the capture.

## The repair

`tools/capture_departure_factors.py` writes **one row per decision**. The first call for a (supply point, term start)
is the decision at the price the household was quoted. Its factors and its `realized_churn_probability` are the
pre-offer ground truth, the same pre-offer quantity `answer_retention_offer` already keeps. Later calls on the same
key are nested under that row as `reasked_at` (kind `retention_offer` or `save_on_loss_notice`, the rate, the
world's P(stay) and its answer). No information is dropped, and no reader counts a hypothetical answer as a decision.

## Pre-registration (written BEFORE the probe and the re-capture)

- **P1.** A re-capture at the repair has **0** duplicate (customer_id, event_date) pairs in the renewal table.
- **P2.** The number of rows carrying a non-empty `reasked_at` is 25–45 (r2 had 35 pairs). Fewer than 15 would mean
  offers stopped being made, and the world has moved under the capture.
- **P3.** `account_denominator_refusal` stops refusing on "depart more than once", or names **≤ 2** accounts
  (re-acquisitions). If it still names more than 2, this diagnosis is wrong, and the dual-fuel hypothesis returns.
- **P4.** No prediction on the value of the 2021 anchor. The fitter may refuse on a different, named ground. That
  refusal gets recorded. It is not worked around.
- **Probe before the re-capture.** Removing every row after the first per (account, date) from r2 gives 246 rows.
  The probe tests P3 on the existing capture. It is not the re-capture, and its anchor is not landed.

## The probe on r2, graded (2026-11-27, after the pre-registration)

I kept the first row per (account, date) and ran `python3 -m tools.fit_year_level_anchor /tmp/seat-dedup-probe.json`
with r2's SVT sibling. Renewal rows went from 282 to 246, departures to 112 + 251.
- **P3 on the probe: HELD.** "Depart more than once" fell from **22** accounts to **1**, `SYN-2016-582`.
- **That 1 is the same class, one step further.** On 2017-12-10 it left at the quoted rate (P(stay) 0.17, roll
  0.3841) and was kept by the offer at £128.96 (P(stay) 0.668). The run's own log prints `p_retain=0.6681` and
  keeps it on supply until it really leaves on 2024-12-08. Keeping the first call is not enough: the quoted-rate
  answer is not what happened. So **the decision row now carries the outcome the run KEPT** (`event_type`,
  joined from `result["customer_events"]` after the run, with the offer, save and debt objection applied). The
  quoted-rate answer stays beside it as `event_type_at_quoted_rate`. Factors and `realized_churn_probability`
  stay the quoted-rate (pre-offer) ones.
- **The probe still emits no anchor, on a different named ground.** `emission_refusal`: the renewal route carries
  only 31% of departures, so the renewal-only table cannot be the world's level. That refusal belongs to the
  renewal-only fallback. The whole-book fit runs only once the account refusal clears, and only the re-capture
  can show that. The probe's per-year diagnostic for 2021 (18 rows, anchor 2.6764) is not the world's level and
  is not landed.
- **A second probe that approximates the kept outcome** (a decision counts as stayed if any re-ask renewed) clears
  `SYN-2016-582`. It is then refused on `SYN-2016-206`, which decides after it departed: it rolled `churned` on
  2018-04-27 (P(stay) 0.341, roll 0.973), but the log has no `[CHURN]` line, both legs `[DECLINED-FIX]` onto the
  default tariff, and it stays on the SVT route. A re-ask cannot produce that. A debt objection can:
  `simulation/debt_objection.apply_objection` turns `churned` into `renewed`, and the kept event lands in
  `customer_events`. So the real join is needed, and the approximation is not enough. This is a third route of
  the same class: the world's answer at the quoted rate is not what the run kept.

## Correction to the 26 Nov page

`SEAT_FINDING_THE_WORLDS_2021_END_OF_FIX_RISE_…_2026-11-26.md` says the 35 pairs are "one dual-fuel home's two
supply legs". **That is wrong**, for the reasons above. The world rolls once per home (`departure_decision_leg`).
No world change is made, and the baseline does not move.

## What is next

The re-capture at the repair, held on its artefact. Then `tools/fit_year_level_anchor` on it, and the 2021 refit
lands with `SE_LANDED_SIGNAL=/var/tmp/se-fix0-anchor-refit-landed.sha`. The rankq re-grade stays held on that file.

## Disposition of the item (re-drawn 2026-11-27, after aa620cb77)

The item `one-home-one-departure-decision-across-two-fuels` was re-drawn asking for a world change keying one
renewal decision per home. **That part is spent:** the world already does it (`departure_decision_leg`,
`simulation/customer_events.py:458`, called at `simulation/run_phase2b.py:3672`), so no world change is made and
the K8 dual-fuel-switching section the draw asked for is not needed to justify a build that will not happen.
The remainder (re-capture, P1-P3 grade, 2021 refit with the signal file) is carried by the successor
`fix0-2021-anchor-refit-on-the-one-decision-capture`. The re-capture `longjob-one-decision-recapture` was
already in flight at re-draw (launched 03:57Z, artefact
`/var/tmp/se-reask-capture/departure_factors_one_decision.json`); it was not launched a second time. The claim is
released.

## The re-capture at aa620cb77, graded (2026-11-27, `departure_factors_one_decision.json`)

- **P1: HELD.** 0 duplicate (customer_id, event_date) pairs in 246 renewal rows.
- **P2: HELD.** 35 rows carry a non-empty `reasked_at`.
- **P3: HELD.** `account_denominator_refusal` returns `None`: no account departs more than once. The
  re-ask diagnosis stands, and the dual-fuel hypothesis stays dead.
- **P4: the fitter refuses, on a new named ground, and no anchor is landed.**
  `YEAR_LEVEL_ANCHOR[2021]` is unchanged, and `/var/tmp/se-fix0-anchor-refit-landed.sha` is not written.
  Clearing the account refusal let the whole-book fit reach `svt_composition_refusal` for the first time
  on this book. It refused: *"112 of 9131 SVT rows are reproduced by NEITHER composition (e.g.
  SYN-2016-266 on 2016-06-08: recorded 0.010783)"*. The renewal-only fallback then refused on its own
  ground, as the probe had: the renewal route carries 30% of departures.

**What the 112 are.** The world is self-consistent. On every row, `realized_churn_probability` equals
`sim_svt_inertia × sim_action_propensity`. It is the fitter's recomputed hazard that differs. All 112 are an
account's **last** SVT segment (112 accounts, 109 stayed and 3 churned). In each, the recorded
`sim_svt_inertia` inverts to the full cap period (92 days in most cases), while `sim_segment_days` records
fewer days. Example: `SYN-2016-422` is billed 2016-10-01→2016-12-11 (71 days, the log's term 1), but its
hazard was rolled over the period to 2017-01-01.

**The cause is a world defect, not a fitter defect.** `run_phase2b` clips `term_end_str` for a move-out, a
riding leg's departure or an erroneous gain returned. It then called `inertia_hazard_for_term(term, …)`,
which read the unclipped `term["term_end"]`. So the world rolled SVT drift over days it no longer supplied
the account. That overstates SVT departures. The overstatement is small, but it falls on exactly the accounts
that were leaving anyway. The fix is decided on fidelity grounds, blind to company results: exposure is days
supplied. `inertia_hazard_for_term` takes `supplied_until`, and the run loop passes `term_end_str`. Test:
`test_a_segment_cut_short_carries_the_hazard_of_the_days_supplied_not_the_cap_period`. I mutated it by
ignoring `supplied_until`, and it fired.

## Pre-registration for the re-capture at the supplied-days fix (written BEFORE it runs)

- **P5.** `svt_composition_refusal` returns `None`: 0 rows are reproduced by neither composition.
- **P6.** SVT-segment departures fall by 0–3 from 251. Only the 3 churned last segments can move, and only
  when their roll exceeds the shorter hazard. A rise would mean the fix touched something other than
  clipped segments.
- **P7.** P1–P3 still hold: 0 duplicates, 25–45 rows re-asked, and no account departing twice.
- **P8.** No prediction on the anchor's value, and no prediction on whether the whole-book fit then emits.
  If it refuses again, that refusal gets recorded. It is not worked around.

The capture worktree `/var/tmp/se-reask-capture-wt` had already been removed when this grade ran: not a worktree and not on disk.

**Disposition, 2026-11-27 08:16 GMT (draw of `fix0-2021-anchor-refit-on-the-one-decision-capture`).** The
supplied-days re-capture is still running and has not written
`/var/tmp/se-supplied-capture/departure_factors_supplied_days.json`. Its log is mid-2019 at about 15.9M
settlement periods. The live process is pid 3329877 under `run.sh` pid 3329847. The pid 2534655 that the
item names is gone, so read pids from `pgrep -af supplied`, not from the item. No grade or refit was run, and
no second capture was started. The successor `fix0-2021-anchor-refit-on-the-supplied-days-capture` is
gated on that artefact and now carries P5–P8, the fitter run and the 2021 refit landing. This item was
released in its favour.

## The re-capture at the supplied-days fix, graded (2026-11-27, `departure_factors_supplied_days.json`)

The capture ran at `a64e05ed3c`, which contains the supplied-days fix, with `YEAR_LEVEL_ANCHOR[2021]` at 7.73378.

- **P5: HELD.** `svt_composition_refusal` returns `None`.
- **P6: HELD.** SVT-segment departures went from 251 to 250. The (customer_id, event_date) keys are identical
  across 9,131 rows. Exactly 112 rows changed their recorded probability, the 112 clipped last segments.
  One changed its fate: `SYN-2016-161` on 2023-04-01, whose probability went from 0.006114 to 0.001820
  against a roll of 0.004114. Nothing outside the clipped segments moved.
- **P7: HELD.** 0 duplicate pairs in 246 renewal rows. 35 rows are re-asked.
  `account_denominator_refusal` returns `None`.
- **P8: the whole-book fit EMITS.** It returns 2017 7.584393, 2018 8.764136, 2019 17.199964,
  2020 18.195573, 2021 **22.102960** and 2024 52.100342. 2016, 2022, 2023 and 2025 are not fitted
  (edge years and years with no renewals). On this capture 2021's SVT floor is 10.02% against a record of
  15.57%, carried by 18 renewal decisions.

**The anchor is NOT landed this turn, and a control is the reason.** With 2021 set to 22.102960,
`test_switching_rate_commons::test_the_capture_the_band_verdict_is_read_from_was_produced_by_the_live_anchor`
reds. The committed capture (`docs/reports/qep_g_second_qep_pass_anchor_departure_factors.json`) ran 2021 at
7.73378. The control's own instruction is to re-capture rather than edit the expectation, so the anchor
lands together with a capture taken under it. That capture is launched as unit `longjob-anchor7-capture`.
It runs in worktree `/var/tmp/se-anchor7-capture-wt`, which is origin/main plus this one-line anchor change,
and writes `/var/tmp/se-anchor7-capture/departure_factors_anchor7.json`.
`/var/tmp/se-fix0-anchor-refit-landed.sha` is still unwritten. `/var/tmp/se-supplied-capture-wt` was
already gone when this grade ran.

**One pass, not a fixed point.** The same fit disagrees with the committed 2017-2020 and 2024 values by up to
2.5x. This pass moves 2021 only, as the item directed. The other years are a separate decision.

## Pre-registration for the capture under 2021 = 22.102960 (written BEFORE it runs)

- **P9.** On the new capture, `fit_whole_book`'s 2021 achieved level at 22.102960 is within **0.3pp** of
  15.57%, the acceptance used by the QEP passes. If it is outside, the anchor does not land on this capture.
  2021 is re-fitted on it and captured once more.
- **P10.** The 2017-2020 whole-book levels move by less than 0.3pp from this capture's. The 2021 anchor acts
  only on 2021 decisions. Book composition changes only from 2022 onward.
- **P11.** P1, P3 and P5 still hold: 0 duplicates, no account departing twice, and no composition refusal.
- **P12.** No prediction on 2022-2025 levels, and no prediction on whether
  `test_the_committed_rung_1_verdict_still_reproduces_and_names_every_year_it_fails` still holds when this
  capture replaces the committed one. If it reds, the record it holds has changed. That gets recorded,
  not edited to fit.
