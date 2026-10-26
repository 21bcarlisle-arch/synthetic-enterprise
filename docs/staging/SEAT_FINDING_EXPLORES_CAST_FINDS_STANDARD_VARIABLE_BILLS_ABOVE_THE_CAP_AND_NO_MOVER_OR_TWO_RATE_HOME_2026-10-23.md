**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`

# Explore's cast finds standard-variable bills above the cap, and no mover or two-rate home to show

Raised by the cast rules in `tools/generate_explore_cast.py`, built for the director's 23 Oct
steer (`docs/staging/advisor/done/DIRECTOR_STEER_EXPLORE_IS_A_LIVE_FEATURE_DEMO_THAT_PROVES_THE_FEATURES_WORK_2026-10-23.md`).
His 09:30 point was that each cast rule is also a check that its feature works. On the published
run of 19 Oct (`8b6fea024`, 550 households), three of those checks say a feature does not work.

## 1. Bills on the standard variable tariff above the binding ceiling

**What was measured.** The population is every resi invoice dated before the household's first
renewal on that fuel. Before that renewal, the tariff can only have been standard variable. The
run does not record term length, so this is the one population that is certainly capped. It
undercounts, which is the safe direction. Each invoice's all-in unit rate is (commodity + non-
commodity) × (1 + its own VAT rate) ÷ kWh. Standing charge is excluded and catch-up bills are
skipped. That rate is compared with the household-facing ceiling for the period: min(Ofgem cap,
EPG), from `docs/domain_artefact_library/regulatory/ofgem_default_tariff_cap_windows.json`.

**Result.** 4,764 of 14,012 graded invoices are more than 0.5% above the ceiling, covering 199 of
550 households. 1,791 are above it **on the commodity line alone**. Every capped year is affected:
2019 448, 2020 306, 2021 497, 2022 1,075, 2023 1,557, 2024 685, 2025 196 (invoices). The worst is
January 2023 electricity at 77.6p/kWh against an EPG of 34.0p and an Ofgem level of 67.5p.

**This is not the 1 Oct finding re-found.** `SEAT_FINDING_AN_SVT_SEGMENT_WAS_BILLED_ABOVE_THE_CAP_BY_THE_RENEWAL_CHAIN`
was closed by `592596b44`, and that commit IS an ancestor of the run's `8b6fea024`.

**The mock-up's case, answered.** SYN-2016-306's November 2022 bills come to 51.89p/kWh
electricity and 14.76p/kWh gas, all-in including VAT. Those are **exactly the Ofgem cap levels for
Oct–Dec 2022** (518.9 and 147.6 £/MWh), not the EPG rates the household should have paid (34.0p
and 10.32p). The bill charges the household the cap, and the Treasury's half of the EPG never
reaches it. (That bill falls after the household's 2019 renewal, so it is outside the population
counted above. It shows the EPG leg on its own.)

**I cannot yet say which cause it is.** The explanations the evidence allows, ranked:
(a) non-commodity cost is billed on top of a unit rate that is itself capped, which can only be true
of the 2,973 invoices whose commodity line is under the ceiling; (b) the EPG is not applied to the
household's bill, which fits the 306 case exactly; (c) "before the first renewal" is not the same
as "on standard variable", for example if acquisition was itself onto a fix. That would make the
check wrong, not the bill, and it is the first thing to rule out. (d) A regional cap above the GB
average explains a few percent at most and cannot explain 2×. The one-variable test is to re-grade
the same invoices against the tariff type the run records on the segment, not the timeline.

**Re-graded 23 Oct (correction beside the claim):** (c) is refuted. On the run's recorded
`tariff_type`, 4,579 of the 4,764 are `svt` invoices. The causes are A, an incoming occupant priced
as non-domestic (3,600 invoices, fixed), and B, the EPG not passed to the household (1,817, next):
`SEAT_FINDING_SVT_BILLS_ABOVE_THE_CAP_ARE_TWO_DEFECTS_NOT_A_GRADING_ARTEFACT_2026-10-23.md`.

## 2. The insulation that never reached the bills (mock-up check 2)

SYN-2016-306's timeline says gas use moved −24% from February 2022. On billed gas, which actual
reads correct through catch-ups (Dec 2022, Apr 2023, Aug 2023, Mar 2024 are all `A` with
`catchup_applied`), the household used 24,506 kWh in 2021 and 22,542 kWh in 2023: **−8%**.
Electricity fell about 18% on the same basis. So the estimate does not ignore actual reads; the
catch-ups land. What did not reach the meter is most of the stated −24%. One untested explanation:
the effect line averages the months before the event against the months after it, and for an event
dated in February that is winter against spring. I have not checked that; it is the next thing to test.

## 3. A debt that was never chased (mock-up check 3)

The £93.68 bill of 30 Apr 2019 drew a first notice (22 May 2019) and a second notice offering a
payment plan (5 Jun 2019). After that there was nothing for five years. £68.50 of it was written
off on 19 Jul 2024, 13 days after the household left on 6 Jul 2024, and placed with an agency on
18 Aug 2024. The gas leg is the same shape: notices in June–July 2018, then write-off of £16.85 on
the same day. The collections ladder has no step after the second notice, and the write-off fires
only on leaving. That is the shape `done/SEAT_FINDING_A_FAILED_BILL_IS_WRITTEN_OFF_IN_FULL_IFF_THE_CUSTOMER_EVER_LEAVES_2026-09-27.md`
recorded, and it still holds on the 19 Oct run. The gas timeline's `"commodity": "electricity"`
on its renewals (at an electricity £/MWh rate) is confirmed on `SYN-2016-306g`.

**Built 24 Oct (beside the claim).** "The ladder has no step after the second notice" was true of
the PUBLISHED record and not of the company. There are two ladders:
- The published per-bill stage list is `arrears_engine.LEDGER_NOTICES`, two notices, read by the
  world's `arrears_stages`.
- The company's live desk (`collections_journey`, run by the triad) has five rungs, up to a Consent
  prepayment offer at day 90. After that rung it went silent until the household left.

The desk now acts past its top rung. Each further missed bill re-offers the SLC 27.6 menu through
the plan door. A live debt is written off by one named rule: the statute bar, six years past due
and six years since any payment.
- K8 page: `docs/market_research/company_debt_management.md`, "After the last rung".
- Partition control: `tests/company/billing/test_the_collections_ladder_has_a_step_after_the_last_rung.py`.

**Still open (handed on):**
- The explore page and the per-bill record show `LEDGER_NOTICES`, not the desk's journey. A reader
  still sees two notices and silence until the per-household record carries the desk's stages.
- The two ladders still disagree on the plan-offer day (21 against 28).

## 4. Slots no household can fill

- **The mover.** The published per-household record has no move-out event and no final-bill
  marker. The 181 `OCC-` accounts are not linked to the household they replaced. Until the 22 Oct
  mover fix emits those links, the slot says so on the page.

  **Re-graded 2026-10-24** (rules: `docs/market_research/home_moves.md` §8.8; measure:
  `billing_accuracy.move_out_final_bills`, over the published run of 2026-10-22, producing commit
  `1044c8fe0d`, no new arm):
  - The household record now carries a `moved_out` event and a `final_bill` event, with the
    closing read's basis and the amount (`tools/generate_customer_reaction_chain.py`). An `OCC-`
    page names its predecessor account from `occupier_successions`. The current run predates that
    field, so all 181 pages say "the run predates occupier_successions" until the next run.
  - **256 move-outs.** 249 closed an account with a final bill. 7 name an account whose final bill
    ended 28 days to 9 months *before* the move. The account had already left us, so the move
    closed nothing of ours, and those 7 are graded against nothing. The world puts a move in the
    supplier's register for a household it no longer supplies. Filed here, not yet chased.
  - **Final bill within 6 weeks (SLC 27.17): 249 of 249 on time, and that proves nothing.** Every
    bill's issue date is its period end (`invoice.py`), so every final bill is dated the day
    before the move (−1 day). The late branch cannot fire in this run. It is proven able to fire
    on a fixture (`test_every_final_bill_branch_can_be_taken`).
  - **Closing read: 164 of 249 estimated (66%)**, 85 actual (electricity 87/136 estimated, gas
    78/113). No rule requires an actual closing read, and the published share is a GAP (G8.9). A
    mover is told to read the meters on the day, so two in three closing on an estimate is a
    fidelity question for the read lane. Not graded as a breach.
  - **Credit refunded within 10 working days of the final bill (GSoP reg 6D): 19 of 21 on time,
    2 late (14 and 20 working days).** Only direct-debit accounts that closed in credit are in
    the refund log. For the other 228 the run records no closing balance. The late tail is the
    world's `credit_refund_events.ON_TIME_PROBABILITY` draw. The log labels this rule "SLC 14",
    which is the wrong locus (corrected in §8.8).
  - **Debt carried: unmeasured, `None` with its reason.** The run publishes no closed account's
    balance at its final bill. Next: publish that balance per closed account, then this branch
    reads it.
- **Storage heating.** Every one of the run's 38,554 invoices carries one `Anytime` register. There
  is no profile-class-2 home to show. The rule is proven able to fire on a two-register bill
  (`test_the_storage_rule_fires_on_a_two_register_bill`), so the slot is empty because of the run,
  not because the rule is blind.

## Also seen, not yet graded

The EV slot's best household is PROS-2021-0219, and its electric car moved its use by **+8%** (99 →
108 kWh/month). A real EV adds far more than 9 kWh a month. This is filed for the EV lane as a
fidelity question, not a breach: no published rule says how much an EV must add.

## Handed on

- Wire the cast's coverage checks into Monday's end-to-end step (`background/weekly_rhythm.py`), so
  a feature that stops working reds the build before a reader sees it (steer item 4, third bullet).
- Render the customer view from `company/portal/templates/` (steer, view 1). Today the page draws
  it from the same invoices and ledger, and says "simulated household". It does not claim to be
  the supplier's own portal.
- The cold-reader pass the steer asks for (one energy reader, one tech reader).

## Why this stays BLOCKING, 24 Oct 07:25: the fixes are on origin, and the published run is not

The defects in sections 1, 3 and 4 have been built or graded on origin. Section 1 fell from 5,488 to 104
of 24,597 on the fresh run (`d909b69338`). This file still holds lane D, and correctly. The site publishes
run `8b6fea024` of 19 Oct (`site/data/explore_cast.json` `meta.run_git_commit`; `company.json`,
`billing_accuracy.json` and `case_studies.json` are the same). None of the fixes reaches it:
`4bc21e9209` (an incoming occupant is domestic), `4ef70aba92` (the EPG reaches the bill) and
`ce35a25e21` (the void stub's estimate). Its households' bills, and the ledger, debt and revenue figures
drawn from them, still charge 199 of 550 households above the ceiling.
That is `background/finding_severity.py`'s BLOCKING: "a published figure may be wrong".

**What clears it is a published run whose commit carries all three fixes, not more code.** The fresh
run that carries them (`/var/tmp/se-overcap-out/run_output_88cdf35e48.json`) was a grading run. It is
not in `docs/reports/`, so no publish can pick it. Two things stand in the way, measured at 07:23 UTC:

- The shared checkout, which the simulation runner executes, is **106 commits behind origin and
  0 ahead**. Not one of the three fixes is an ancestor of its HEAD. A run it produced now would
  publish the over-cap bills again. Bringing it level is claimed (`the-shared-checkout-reaches-origin`,
  07:20 UTC) and is in the orienting seat's focus, so this file does not do it.
- The publish hold opens Mon 26 Oct 04:00 GMT (`.publish_gate_state.json`).

**To close:** once a run at a commit that has `ce35a25e21` as an ancestor is published, re-grade it with
`tools.grade_svt_invoices_over_ceiling`. The cast's `book_breaches.above_cap` should then fall from 199
households to near the 16 the fresh run showed. Lower this file to LATENT on that reading, not before.

**Amended 24 Oct, beside the condition above.** A run carrying `ce35a25e21` is not yet safe to publish.
On the fresh run at `c5a8090187`, that fix gives 5 electricity void stubs receipts of about 47.7× the
Treasury's share. Their bills go to as low as −£2,950, and £5,898 is never booked:
`done/SEAT_FINDING_THE_VOID_STUB_EPG_FIX_CREDITS_HOUSEHOLDS_48_TIMES_THE_TREASURY_SHARE_AND_THE_LEDGER_BOOKS_NONE_OF_IT_2026-10-24.md` (closed 25 Oct: the fold fix graded clean at `1c30d6c728`).
The publish that clears this file must carry that file's fix too.

## The path from run to page, 24 Oct 15:30Z (`the-monday-publish-carries-a-run-with-the-billing-fixes`)

**(a) The run the publisher picks.** Whichever `docs/staging/run_complete_*.md` marker
`background/process_run_complete.py::_process` handles first once `publish_freshness.content_publish_window`
opens at Mon 26 Oct 04:00Z. Every marker handled before then is archived on HOLD and is gone. Nothing
re-publishes a held run when the window opens. The marker is written only by `background/sim_runner.py::run_simulation`,
and it names that run's `run_output_<HEAD>_<stamp>.json`. So Monday publishes the first sim-runner run
that finishes after 04:00Z. A run made by hand with `tools.run_annual_report --save-json` writes no marker,
so the publisher never sees it, whatever directory it lands in.

**(b) The shared checkout.** Yes: sim-runner runs `tools.run_annual_report` with `cwd` set to the
shared checkout, at its HEAD, and `code_admission` defers it unless that HEAD is on origin. The HEAD
is `95e78ec777`, 15 behind origin. It carries `ce35a25e21`, `4ef70aba92` and `4bc21e9209`. It does
not carry `3a31999db`, so a run there now would bill the void stubs 48× (c5a8090187's shape). The
reconciler's fast-forward was held by 27 paths. 22 of them are byte-identical to origin, which the
reconciler clears by itself. Four were older copies of the asks-ledger landing (b8b14269e), which
origin supersedes: `tools/harness_page_figures.py`, `tests/tools/test_harness_page_figures.py` and
`site/harness/index.html` were refreshed with `refresh_to_head --base origin/main`, and the bytes
are preserved on `refs/preserved/refresh-to-head/monday-publish-shared-ff-2026-10-24`. The fourth,
the generated `site/data/director_asks.json`, was set to origin's bytes; its old copy is at
`/var/tmp/director_asks.json.shared-copy-2026-10-24`. **One path still holds it:
`docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md`.** It carries a live edit written at 14:02Z by
the lane correcting "SLC 27B" to the SLC 27.15 duty, which is also editing `M2_PAYMENTS_AUDIT_DD_RAILS.md`
and `phase-history.md`. Its hunks do not overlap origin's (owner/due fields from 4e3a978bf). It
clears when that lane lands. It is not this item's to land.

**Two things a reader of the runner should know.** The runner has been due since 22 Oct 20:59Z and
defers every five minutes to the s14clean long jobs. Its between-run pause, in the running daemon,
is 4,685 s, not the declared week. `_declared_cadence_seconds` runs at import, before `sys.path` holds
the project, so under `python3 background/sim_runner.py` it falls back to the consumer floor. That
fallback is why a run will finish after 04:00Z at all: at a weekly pause, the run that finishes
first would be held, and the next would come a week later. **Fixing the import without moving the
window would leave Monday with no run.**

**(c) Reachable by the ordinary route.** The graded run that publishes is sim-runner's first run
after 04:00Z, so nothing has to be carried into `docs/reports/` by hand. What was missing was the
grade. `process_run_complete.billing_grade_refusal` now runs `tools.grade_svt_invoices_over_ceiling`
on every run before regeneration, and refuses one it names a defect on. The grader now names
over-cap as a defect too: share above `OVER_CEILING_SHARE_BOUND` (2%). Until now it counted over-cap
and never named it, so `defects: []` passed every pre-fix run. At real inputs:

| run | refusal |
|---|---|
| `1044c8fe0d` (22 Oct, pre-fix) | 6,719 of 24,417 default-tariff bills (27.5%) over, 307 households |
| `8b6fea024` (19 Oct, published) | 5,488 of 18,398 (29.8%), 244 households |
| `88cdf35e48` (three fixes) | none: 104 of 24,597 (0.42%), 16 households |
| `c5a8090187` (void-stub defect) | carved GBP 205,866.61 != booked GBP 199,968.51; 5 negative estimates |

**(d) Not silent.** The banner on every live-data page now says it:
`site/data/publish_provenance.json` `figures_caveat`, rendered by `site/assets/freshness-banner.js`
and `publish_provenance.banner_line`. It reads: "The billing, customer and debt figures on this
site come from run 8b6fea024 of 19 Oct 2026, which predates the price-cap fixes: 5,488 of its 18,398
standard-variable bills (29.8%) are above the household's cap ceiling." It is pinned to that run.
Only `record_verified` clears it, which means a publish that passed the grade. If Monday's run is
refused, the publisher keeps the 19 Oct figures, pauses the banner, and keeps this sentence.

**Prediction, filed before Monday.** If the register lands and the shared tree fast-forwards before
about 02:50Z, the first run after 04:00Z is at a commit carrying all four fixes. The grade passes at
about 0.4% over, and `explore_cast.json` `book_breaches.above_cap` falls from 199 to about 16. If the
tree is still at `95e78ec777`, the run is refused on carved != booked, and the 19 Oct figures stay up
under the caveat. Lower this file to LATENT on the first reading, not the second.

## The reading on the closing run, 25 Oct (`1c30d6c728`, not a published run)

The fold fix's closing run graded clean. `tools.grade_svt_invoices_over_ceiling` gives `defects: []`
on it, so the publisher's grade would pass it:

- 6 of 24,597 default-tariff invoices are above min(cap, EPG) (0.02%, against the 2% bound). They sit
  on 2 households, all outside the EPG windows (2019: 2, 2024: 4).
- Carved equals booked at GBP 200,091.73, and there are no negative estimates.

**The six have a cause, and it is a new one.** All six are gas SVT, on `SYN-2016-428g` (Jan and Feb
2019) and `PROS-2017-0393g` (Apr, May, Jun and Aug 2024). Each is billed at the mean of the rates its
term has carried since a mid-quarter start, not at the cap quarter's rate. The table, and the class
(5 legs, 22 bills, mispriced in both directions), are in
`SEAT_FINDING_A_GAS_SVT_TERM_STARTED_OFF_A_CAP_QUARTER_IS_BILLED_AT_THE_MEAN_OF_EVERY_RATE_IT_HAS_CARRIED_2026-10-25.md`.
That file is LATENT and does not gate Monday.

**This file stays BLOCKING.** Its condition is a *published* run, and this run is not one. It clears on
the first run after 2026-10-26T04:00Z that passes the publisher's grade and publishes, and it is
lowered to LATENT on that reading.

**Prediction, filed before Monday's run.** Suppose the run is at a commit carrying `3a31999db`, and
nothing else on the billing path has moved. Then the grade passes at about 6 over (0.02%), and
`book_breaches.above_cap` falls from 199 to about 2 households, not the 16 predicted above. The
cast's 16 was `88cdf35e48`'s. If the runner's commit predates `3a31999db`, the grade refuses on
carved != booked, and the 19 Oct figures stay up under the caveat.

## Monday's run: launched at `b2bc3d8da5`, 25 Oct 12:27Z (pre-registered before it finished)

The sim runner had deferred every cycle, and the newest run on `run_output_latest`
(`904a091f7b`, 03:16Z) carries none of `063dc4bbd`, `33dd50527`, `9bb30c4de` and `a0ed2aa7b`. So a full
run was launched by hand. It uses `background.launch_long_job`, unit `longjob-mondays-run-b2bc3d8da5`,
and runs from a clean worktree at origin/main `b2bc3d8da5`, which carries all four and `3a31999db`.
Its imports are off-commit by nothing. The artefact is
`docs/reports/run_output_b2bc3d8da5_20261025T1230Z.json`. A rival landing, "a credit in the middle of
an account's life comes off the next paid bill", was still in its gate at launch, so this run does
not carry it.

**Predictions, written while the run was in flight:**
1. `tools.grade_svt_invoices_over_ceiling` gives `defects: []`, with **0** default-tariff invoices
   over min(cap, EPG) out of about 24,660. This follows `e526b740f`'s side run at `7559a676f7`: 0 of
   24,663. The "about 6" predicted above was `1c30d6c728`'s, before `063dc4bbd` ended the
   overlapping terms. If any are over, I expect the mid-quarter-start gas SVT class (the six of
   `SEAT_FINDING_A_GAS_SVT_TERM_STARTED_OFF_A_CAP_QUARTER...`) and nothing else.
2. Carved equals booked, and no estimate is negative.
3. `move_out_final_bills.credit`: every move-out the ledger closes in credit has a refund recorded,
   none is owed and unrefunded, and none of the closure refunds goes to an account the ledger holds
   in debt or settled. I cannot predict the count. `a0ed2aa7b`'s 7 was a 60-founder run, and this
   book has 263 move-out rows.

## Monday's run graded, 25 Oct 14:50Z: all three predictions held, and it is on `run_output_latest`

The unit `longjob-mondays-run-b2bc3d8da5` finished at 13:32Z (1h05m wall, 5.4 GB peak). Its
artefact, `docs/reports/run_output_b2bc3d8da5_20261025T1230Z.json`, is stamped `b2bc3d8da5` and
carries `063dc4bbd`, `33dd50527`, `9bb30c4de` and `a0ed2aa7b`. Nothing graded or promoted it
afterwards: a hand launch writes no run-complete marker.

**The grade** (`python3 -m tools.grade_svt_invoices_over_ceiling <run>`, `defects: []`):

| Prediction | Result |
|---|---|
| 1. 0 default-tariff invoices over min(cap, EPG), about 24,660 graded | **0 of 24,663** (0 households). 12,607 more are ungradeable, meaning the grader's excess function returns `None` for them. |
| 2. Carved equals booked, no negative estimate | **£200,459.54 carved = £200,459.54 booked** on 3,553 bills. None of it is outside the EPG windows. 0 negative estimates. 0 overlapping term legs. |
| 3. Every in-credit move-out is refunded, none is unrefunded, none goes to the wrong account | **100 of 848** closing balances are in credit. All 100 have an `account_closure` refund (£7,093.49), 0 are owed and unrefunded, and 0 refunds go to an account not in credit. |

**Not predicted, and still open:** 10 of the 100 closure refunds were paid in 13 to 24 working
days, against the code's own deadline of `_REFUND_DEADLINE_WORKING_DAYS = 10`
(`company/billing/credit_refund.py:27`). They are flagged `breached_slc14_deadline`. This grade does
not say whether 10 working days is the licence's figure, or whether the lag is a billing-cycle
artefact. That is the next read.

**This run does not carry `dac6b90d7`** ("a credit in the middle of an account's life comes off the
next paid bill"). That fix landed after `b2bc3d8da5`. The 100 closure credits above are therefore
before it. `dac6b90d7`'s own 60-founder reading cut them from 7 to 2.

**Promoted.** `docs/reports/run_output_latest.json` on the shared tree is now a byte copy of this
run (`cmp` clean). The bytes it replaced are still on disk as
`run_output_904a091f7b_20261025T031613Z.json`. To reverse, copy that file back.

**Why the site would still not move on Monday without one more step.** The publisher HOLDs any run
that completes mid-week, archives its marker, and nothing offers that run again when the window
opens. `refused_marker_to_rearm` re-arms refusals only, not holds. All four `904a091f7b` runs of 24
and 25 Oct were held this way. So Monday's publish happens only if a run happens to finish after
Mon 04:00. The runner has deferred every cycle since 04:20Z, waiting on landings first. As a
one-off, the transient user timer `mondays-window-marker-20261026` fires at **2026-10-26 04:05Z**.
It runs `/var/tmp/mondays-window-marker/drop_marker.py`, which writes a run-complete marker for
whatever run is on `run_output_latest` at that moment, and only if no marker is already pending.
The publisher's own refusals all still apply. The log is `/var/tmp/mondays-window-marker/out.log`.
To reverse, `systemctl --user stop mondays-window-marker-20261026.timer`. It does not survive a
restart of the user manager. The structural fix, a held run re-offered at window open, is handed on
as `a-held-run-is-offered-again-when-the-weekly-window-opens`.

**Prediction for Monday, filed before it happens.** The marker is written at 04:05Z and the
billing grade passes. The publish lands `b2bc3d8da5`'s figures, and `figures_caveat` clears. A later
run at a newer HEAD may finish first. If so, that run publishes instead and the marker step reports
a pending marker.

## The renewal slot's "100% churn risk" is a saturated belief of 0.999, not a clip (25 Oct, copy pack B3)
### What the record says (read, not inferred)

- SYN-2016-441's `retention_decision` of 5 Oct 2018 stores `company_belief: 0.999` against
  `sim_truth: 0.0`. The "100%" is the ledger's `{:.0%}` format
  (`company/analytics/decision_event_ledger.py:77`), not the stored value.
- The belief **saturates**; nothing clips it. `MAX_CHURN_PROBABILITY = 1.0`
  (`company/crm/churn_model.py:388`) and above `CHURN_SATURATION_ELBOW = 0.90` the score runs
  through an asymptotic curve toward 1.0. A 0.999 is the curve far up its tail, i.e. a raw score
  well past the elbow. `churn_desk` rounds to four places (`_ESTIMATE_DP`).
- The published run holds only two retention-decision shapes besides this one (beliefs 0.448 and
  0.385), so this household is the outlier the cast rule exists to find: the rule picks the
  largest belief-truth gap.

### Does it change the decision

- **The tier: no.** `retention_discount_for_risk` (`company/policy/decision_policy.py:365`) takes
  the first threshold the belief clears, so every belief above the top tier gets the same 5%.
- **The value of offering: yes, in proportion.** The £1,313 "expected term margin at risk" scales
  with the belief, so a saturated belief roughly doubles the case for a retention spend against a
  ~50% one. It cannot flip the offer here (offer cost £118 against £1,313), but it does inflate the
  published expected value (£1,195).

### Not established (the next measurement)

- Which input drove the raw score past the elbow in Oct 2018 for this household: a rate rise at
  renewal, a bill-shock count, or the market-pressure multiplier. Read the renewal log row for
  SYN-2016-441 on 2018-10-05 before calling the saturation wrong; a very large rate rise makes a
  near-certain belief defensible, and the truth of 0.0 would then be the world's question.
- Stale comment, same subject: `company/pricing/value_based_renewal.py:215` still says the cap is
  0.95 and "five percent of the book is modelled as staying whatever they are charged". The
  constant is 1.0 since the elbow change; the docstring's argument may no longer hold.

### What landed with this finding

The Explore renewal vignette now renders from a sentence template with the stored belief to one
decimal (`tools/generate_explore_cast.py::_renewal_words`), so the page reads 99.9%, which is the
supplier's belief, not a rounded certainty it never held.

**Reading, 26 Oct 01:21Z (before the window).** The shared checkout's HEAD has `3a31999db`, `ce35a25e21`,
`4ef70aba92` and `4bc21e9209` as ancestors. It is 0 ahead of origin and 89 behind. sim-runner is up
(pid 1470317). The site still shows `8b6fea024`. So the prediction's first branch applies: grade passes
at about 6 over, and above_cap falls to about 2. Still BLOCKING until that publish is read.
