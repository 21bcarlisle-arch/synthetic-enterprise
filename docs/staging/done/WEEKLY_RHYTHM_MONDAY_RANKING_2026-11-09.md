**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — weekly rhythm

# Monday: retrospective on the week gone, and the ranking for the week ahead

**Due:** 2026-11-09 (Europe/London). Armed by the step before it.

**Write the week's ranking into the section at the foot of THIS document.** It stays in the staging root until Friday closes it, so every orientation this week meets it. It does not go in `DIRECTION.yaml`: `direction.FOCUS_MAX_AGE_HOURS` is 12.0, so that record is a stretch record and a weekly ranking placed there expires by Monday evening. Each stretch's `focus` draws FROM the ranking below; a deliberate deferral goes in that stretch's `not_now`, which already refuses an entry with no `why`.

**Overdue outranks new feature work.** Anything below goes into `focus` unless it goes into `not_now` with a reason. It does not outrank a live defect — the priority-zero rungs still come first, which is the ordering the supervisor already applies to this queue.

## Overdue rituals, measured from their own artefacts

- **harness_pruning** (never run) — The harness pruning ritual (HARNESS_BEST_PRACTICE_ASSESSMENT.md §6): which controls have never fired, which duplicate another, which are keyed to today's answer. Verdicts belong in a new dated docs/design/HARNESS_PRUNE_<date>.md.
- **mothball_audit** (last run 2026-07-29, 13 day(s) past a 90-day cadence) — Re-run the mothball question over the apparatus: for every gate, queue, window and reporting ritual, what is this actually for under THE STANDARD? Mothball what cannot say. Verdicts belong in a new dated docs/design/MOTHBALL_<date>.md.
- **claude_md_decay_audit** (last run 2026-08-27, 29 day(s) past a 45-day cadence) — The CLAUDE.md decay audit: which rules in CLAUDE.md are now enforced elsewhere, which have no enforcement at all, and which describe a machine that no longer exists. Findings belong in a new dated *_DECAY_AUDIT_<date>.md.

## Parked work that stated what remained

- **ADVISOR_FINDINGS_REGISTER_ERROR_CHANNELS_ARE_INERT_2026-08-09.md** (92d) — OPEN: §2a (older certificate = more wrong, as a mean shift) and §2b (
- **WORKER_FINDING_THE_ONLY_DOOR_PAIR_A_TEST_RUN_CAN_REPUBLISH_IS_THE_ONE_NOTHING_COMPARED_TO_ITS_LEDGER_2026-08-17.md** (84d) — OPEN: §"What this tick did NOT build" **item 2** — the SITE-lane > live tripwire. It is unbuildable *as a gating control* until the finding-4 dive

The rest of the parked room is 21 document(s), oldest 108 day(s). That is a count, deliberately, not a list: the bulk drain is already declined in `DIRECTION.yaml`'s `not_now` with a reason that still stands, and re-listing it every week would make this rhythm the noise it exists to replace.

## End-to-end check

_Template -- replace this paragraph with the check itself._ Read the canon (`docs/design/DIRECTOR_CANON*.md`, `docs/staging/DIRECTOR_CANON_*`, `docs/design/THE_MODEL_ON_A_PAGE.md`, `CLAUDE.md`), the logic, and the work and findings in question TOGETHER, as hypotheses under test, stated and unstated. For each surprise, list every explanation the evidence allows -- the world wrong, the maths wrong, the director wrong, it not being that simple, something none of us has thought of -- ranked by evidence, not convenience. Raise each resulting concern with `python3 -m background.director_concerns --raise --kind ... --what ... --proposal ...` and carry on; it never blocks the work.

**Written late, on Saturday 14 Nov, from origin at 84a44b51c3.** This Monday was opened at 07:01 on 9 Nov and held the baton for five days. That is the rhythm's own finding, and it is bigger than this week: **no step has closed since the rhythm was built.** Every Monday from 7 Sep to 9 Nov is in `done/` with a DID_NOT_FIRE finding beside it. Each one lapsed and none was closed. The seat's focus carried this step for four orientations and the draw never took it. So the step's place in the focus list was the defect, not the step itself.

**Canon against the work.** M2/M4: the thesis is that per-customer inference creates value a flat baseline cannot. The 13 Nov 18:21 thesis_read says plainly that nothing moved against it. The belief reads AUC 0.52 (0.41 to 0.65), and the renewal churn belief ranks leavers backwards (AUC 0.333 on 268 desk states). The 12-draw family that settles the question was due to read after 08:00Z today, and its grade is not on origin as I write. **So there is still no evidence the method beats the baseline. I cannot yet say whether the family will show any.** F11 applies: the safe reading is "no skill" until the grade says otherwise. The week's real work went to the book's correctness, not the thesis. Examples: the refund clock's one home (ceeefa5960), S6b (69866925bd), the closing set-off on the statement walk (84a44b51c3), and the plan re-offer row (a481c9ab96). That matches the director's 11 Nov scope ("the fix and its book"). M3's floor is untouched this week. The staged proposal on a hidden per-household utility is the director's to rule.

**Logic: the learning loop as it reads on origin (7 days).** repayment-posting 30 of 49 (STOP, 15 code-or-reader misses), level-dd 41 of 57 (STOP), class-l 11 of 12, close-refund-book 15 of 15, eleventh-read-prereg 6 of 6. That is 0.143 regressions per fix over 21 graded fixes, and cold-read escapes are [2]. W1 worked as designed: both STOP areas now have their maps on origin (LEVEL_DD_AREA_MAP_2026-11-11, and REPAYMENT_POSTING_AREA_MAP_2026-11-14 in ad48737415). The stop condition is built into the draw (c29205f253). The repayment-posting count rose from the 25 of 41 the drawn item quoted to 30 of 49. The post-map S6b grade added 5 held and 3 missed, so the map did not yet lower the miss rate. One week is not evidence either way.

**Surprises, each with its explanations ranked by evidence.**

1. *The W2_21 insulation world change (e17ebc596a, 19:08 13 Nov) landed 47 minutes after the seat's direction (389f8f5f19, 18:50) held "the W2_21 insulation flag" to 16 Nov.* (a) Most likely: the claim opened at 18:22, before the direction landed. The worker had no not_now to read, and the draw does not re-read not_now against claims already in hand. This is the same class as the open `wrong` row: "the draw has no reading of a standing ruling's scope". (b) The change is a baseline fidelity correction made blind to company results, which the baseline/curriculum split permits at any time. The hold was about the 16 Nov book's attribution, not a wall. (c) The seat's hold was wrong to apply to a fidelity fix at all. (b) is true but beside the point. The cost of the landing was attribution, and 83991f5fef paid it by writing a one-variable record into the 16 Nov pre-registrations (166 of 358 campaign accounts replaced). Net: no harm to the book's readability. The class remains: a hold written after a claim opened does not reach that claim.
2. *Run cost per settled leg-year rose 43% week on week* (median 1.064 s, up from 0.746). (a) The book grew in content, not in accounts: leg-years are flat at about 4,390, so more work is done per leg-year (N29 replay, refund clock, statement walk). (b) Box contention from concurrent landings and value runs. (c) A real regression. **I cannot yet say.** The remedy this section names is to profile one small run before the next long one. It is not done, and it belongs to the 16 Nov reset.
3. *Two learning-loop trailers read unparsed* (a481c9ab96, ef64912eee). Both are prose lines that happen to begin a wrapped line with "Graded:". Neither is a malformed trailer. The Friday step below records what each one graded. The parser reads any line that starts with `Graded:`, so prose can trip it. That is a reader gap, but it is reported, never dropped, which is the safe direction. It is worth one guard (require `held=` before the line counts as a trailer, else ignore it rather than refuse it). That is not this tick's work.

**Concerns for the director.** None raised. Each surprise above is the machine's or the seat's to fix, and none touches strategy, vision or canon intent. The open M3 utility proposal is already in his queue.

## The knowledge pages' claims against the drawn world

All 6 claim(s) hold.

| claim | measured | band | verdict | page | source |
|---|---|---|---|---|---|
| `dual_share_of_homes` | 76.0% | 70.0%–85.0% | holds | `docs/market_research/how_a_gb_domestic_book_splits_by_fuel_and_how_a_two_fuel_home_switches.md` | Floor: the whole market, 72% of households (CMA/GfK 2014 ¶41). Ceiling: a challenger built by switching, 80% (UW) to 90%+ (First Utility) of customers dual (CMA EMI App. 2.2), at 84-86% gas homes. §2, §5. |
| `dual_share_of_gas_homes` | 89.6% | 81.0%–96.0% | holds | `docs/market_research/how_a_gb_domestic_book_splits_by_fuel_and_how_a_two_fuel_home_switches.md` | §5a: P(both fuels with us | home has gas) 0.83 (market stock, CMA PF ¶9) to 0.94 (Ofgem CES 2017 §3; UW, First Utility). |
| `gas_home_share` | 84.9% | 81.5%–88.5% | holds | `docs/market_research/how_a_gb_domestic_book_splits_by_fuel_and_how_a_two_fuel_home_switches.md` | §3: P(gas meter) 84% (DESNZ subnational 2024) to 86% (EHS 2017-18 AT3.5). The off-grid share is its complement, 14-16%. |
| `gas_only_share_of_homes` | 4.2% | 0.0%–15.0% | holds | `docs/market_research/how_a_gb_domestic_book_splits_by_fuel_and_how_a_two_fuel_home_switches.md` | §2: a gas-only account is a split home's gas leg, 4m of 31m supplier customers (13%, CMA PF ¶9). |
| `gas_only_homes_without_gas` | 0.0% | 0.0%–0.0% | holds | `docs/market_research/how_a_gb_domestic_book_splits_by_fuel_and_how_a_two_fuel_home_switches.md` | §2: Ofgem CES 2017 finds under 1% of households with gas and no electricity, so a gas-only account is a split home whose electricity is elsewhere. It sits on a home with a gas meter. |
| `direct_debit_share_of_accounts` | 73.8% | 66.5%–75.5% | holds | `docs/market_research/gb_payment_method_migration_rates.md` | DESNZ Quarterly Energy Prices, Dec 2025 commentary, p.9: standard electricity DD 69% (Sept 2020) to 72% (Sept 2025), gas to 73%. |

## The map: concepts, their layers, and what attaches to none

71 concepts registered; 17 also named, not declared, 4 home gone.
213 of 230 research notes attach to a published page; 17 attach to none.

Coverage (reporting only): 22 of 52 published pages sit on a concept; 62 of 230 notes attach to a page a concept uses; 17 notes sit on no page (5 ruled owed a page, 12 ruled dead, 0 unruled); 82 of 467 supplier and world modules attach to a concept (0 more declared machinery, 385 on none); 59 of 71 concepts miss a layer, 0 with no recorded reason.

- home gone: collect.payment_method -- supplier: company.billing.payment_method_register
- home gone: collect.consumption_forecast -- supplier: company.billing.consumption_forecast
- home gone: asset.pv_self_consumption -- supplier: company.regulatory.seg_export_estimator
- home gone: asset.pv_specific_yield -- supplier: company.regulatory.seg_export_estimator
- also named, not declared: collect.amount -- 2 modules
- also named, not declared: collect.collection -- 1 modules
- also named, not declared: collect.arrears -- 7 modules
- also named, not declared: collect.payment_method -- 4 modules
- also named, not declared: collect.consumption_forecast -- 1 modules
- also named, not declared: switch.loss_notice -- 1 modules
- also named, not declared: switch.debt_objection -- 2 modules
- also named, not declared: capital.mcr -- 1 modules
- also named, not declared: accounts.segmental_statement -- 1 modules
- also named, not declared: optimise.demand_flexibility_event -- 2 modules
- also named, not declared: tariff.default_tariff -- 3 modules
- also named, not declared: tariff.fixed_term_end -- 2 modules
- also named, not declared: tariff.time_of_use -- 3 modules
- also named, not declared: meter.smart_meter -- 2 modules
- also named, not declared: settle.mhhs -- 3 modules
- also named, not declared: vuln.self_disconnection -- 1 modules
- also named, not declared: vuln.fuel_poverty -- 1 modules

Forward knowledge plan: 130 rows {'priority': 11, 'owed': 3, 'constants': 95, 'waiting': 21}
cost per row 0.67 points (0.44-0.88), one landed knowledge_page session per row; all rows 87.1 (57.2-114.4)
builds drawn before their knowledge, last 30 days: 45 of 119 (a lower bound) {'C34_next_best_action_is_one_decision_across_debt_retention_upsell_and_carbon_judged_by_clv': 16, 'E6_a_forward_cash_forecast_per_customer_charges_expected_loss_as_arrears_build': 9, 'C35_the_supplier_finds_the_share_of_value_it_prices_by_optimising_joint_value_against_the_households_response': 8, 'C5_key_moment_conversion': 6, 'W2_37_complaints_arise_from_billing_failures_and_the_silent_unhappy_are_modelled': 5, 'W2_41_a_household_cancels_its_mandate_as_its_own_act': 5, 'W2_39_households_respond_to_contact_including_badly': 2, 'W2_42_debt_reaches_prepayment_only_by_the_legal_route': 2, 'B13_a_dual_fuel_household_is_one_account_across_both_fuels': 1}

**Reporting only.** A second home or an uncalled home is read in the end-to-end check; it becomes binding once the backlog it exposes is planned.

## Company-side orphans: does every one still carry its ruling

6 company-side orphan(s), each carrying a ruling whose referent holds.

## Explore's cast: does each feature still work

No unaccounted gap. 8 of 8 slots filled.

- spent: above_cap: its gap has closed; drop the entry
- spent: storage_heating: its gap has closed; drop the entry
- spent: ev: its gap has closed; drop the entry
- spent: debt: its gap has closed; drop the entry

## Canon against canon

0 problem(s); 9 attributed quote(s) compared on the standing pages (`tools/canon_against_canon.py`).

## How it's built: page aging

Clean: no dated section is over 30 days old and no superseded line is presented as current.

## Insight due for challenge

1 row(s) due within 30 days. Write the brief with `python3 -m tools.insight_challenge --brief <file>`, give it to a blind reader, and write each verdict back beside its row in `site/data/knowledge_facets.json`:

- 2026-12-05 · weather-cells: How finely Britain must be divided for pricing is a price list, not one number: 34, 89 or 987 weather cells depending on

## Merge pressure, this week

- **79 merges**, forced by: work 68, seat_record 5, mixed 3, empty 2, publish 1.
- **4 conflicted**, 3 resolved by someone; conflicted paths: `docs/staging/SEAT_FINDING_A_LEVEL_DIRECT_DEBIT_HOUSEHOLD_IS_DUNNED_PER_BILL_SO_ITS_PAGE_PRINTS_OVERDUE_WHILE_IN_CREDIT_2026-11-07.md` 2, `docs/staging/SEAT_FINDING_THE_B3CE2A4E73_BOOK_FAILS_THE_DOMAIN_INVARIANT_GATE_ON_SEVEN_ROWS_2026-11-04.md` 1, `tools/generate_billing_ledger.py` 1.
- **Landing wait added by merges: 7.3 h** (median per merge, by kind: work 122s, mixed 131s, seat_record 104s, empty 168s, publish 71s).
- Measured by `python3 -m tools.merge_pressure_census --since 7.days`.

**Ask why it recurs, not how to clear it.** If one kind or one path dominates, that is the next item; if the wait has not fallen since the last change aimed at it, say so.

## Run cost per settled leg-year, this week

| at | sha | accounts | leg-years | wall s | peak MB | s / leg-yr | MB / leg-yr |
|---|---|---|---|---|---|---|---|
| 2026-11-04T03:02:51+00:00 | b3ce2a4e73 | 1291 | 4295.7 | 4161.2 | 4491.8 | 0.969 | 1.046 |
| 2026-11-04T05:45:36+00:00 | b3ce2a4e73 | 1291 | 4295.7 | 4334.9 | 4477.4 | 1.009 | 1.042 |
| 2026-11-04T08:27:45+00:00 | b3ce2a4e73 | 1291 | 4295.7 | 4270.0 | 4462.7 | 0.994 | 1.039 |
| 2026-11-04T11:28:50+00:00 | ba868134c4 | 1291 | 4295.7 | 4496.1 | 4495.9 | 1.047 | 1.047 |
| 2026-11-04T14:35:25+00:00 | 667a12d10a | 1291 | 4295.7 | 4226.1 | 4510.0 | 0.984 | 1.05 |
| 2026-11-04T18:54:05+00:00 | 9b2f18a966 | 1301 | 4369.9 | 4663.9 | 4455.5 | 1.067 | 1.02 |
| 2026-11-04T18:54:51+00:00 | a6b7a0fd47 | 1301 | 4369.9 | 4653.2 | 4480.1 | 1.065 | 1.025 |
| 2026-11-04T20:19:59+00:00 | c07e8ccce9 | 801 | 713.7 | 2013.4 | 1599.5 | 2.821 | 2.241 |
| 2026-11-04T22:34:55+00:00 | 1388ca021e | 1302 | 4391.1 | 5040.1 | 4467.3 | 1.148 | 1.017 |
| 2026-11-05T02:14:00+00:00 | fd91027799 | 1302 | 4389.6 | 4671.5 | 4533.1 | 1.064 | 1.033 |
| 2026-11-07T17:08:22+00:00 | fa915ac0d7 | 1302 | 4389.6 | 4854.9 | 4584.3 | 1.106 | 1.044 |
| 2026-11-07T20:02:34+00:00 | fa915ac0d7 | 1302 | 4389.6 | 4935.4 | 4538.8 | 1.124 | 1.034 |
| 2026-11-08T00:26:13+00:00 | 5e7e3e2c83 | 1302 | 4389.6 | 5175.7 | 4506.1 | 1.179 | 1.027 |
| 2026-11-08T03:45:21+00:00 | 40842cdbe6 | 1302 | 4389.6 | 5182.9 | 4431.7 | 1.181 | 1.01 |
| 2026-11-08T16:03:48+00:00 | 9dfbf9f960 | 785 | 542.6 | 209.2 | 1514.9 | 0.386 | 2.792 |
| 2026-11-08T16:15:29+00:00 | 630952183d | 801 | 713.7 | 298.1 | 1627.9 | 0.418 | 2.281 |
| 2026-11-08T16:28:24+00:00 | 4a48d535fe | 801 | 713.7 | 294.2 | 1613.4 | 0.412 | 2.261 |
| 2026-11-08T23:27:41+00:00 | 342599376c | 1302 | 4393.4 | 4972.6 | 4596.0 | 1.132 | 1.046 |
| 2026-11-09T03:23:53+00:00 | 9e4f83d78e | 1302 | 4389.6 | 5258.5 | 4619.5 | 1.198 | 1.052 |
| 2026-11-09T06:43:04+00:00 | af065c6c49 | 1302 | 4393.4 | 5635.7 | 4463.9 | 1.283 | 1.016 |

s_per_leg_year: median 1.064 this week against 0.746 the week before (+43%) **MOVED -- explain it or fix it**

mb_per_leg_year: median 1.048 this week against 1.137 the week before (-8%)

**A move is a question, not a number.** If seconds or megabytes per leg-year moved, profile one small run (cProfile, not tracemalloc, on this box) and name the hotspot before the next long run starts.

## Does the work follow the priority order

- **Live BUILD draw:** step 2 100%.
- **Landed commits since 2026-10-05:** step 0: 1649, step 2: 87, step 3: 53, step 4: 226, step 5: 86 (step 0 is work in no step).
- **Measured by** `python3 -m tools.draw_follows_the_order`.
- **VIOLATION:** step 6 has no drawable atom: EP16_anchored_generators is idle (); SPINE_1_scenario_world_state is not on the map
- **VIOLATION:** step 7 has no drawable atom: C4_adoption_physics is idle (); W1_10_ev_heatpump_geography is not on the map

**A violation is the next item.** If the landed work sits in a later step than the draw says it should, the dials are not what is choosing; find what is.

## The basics: may forward years start

**Not yet: 2 of 8 gate atoms at target.** Forward runs wait.

| Gate atom | Now → target |
|---|---|
| `E6_a_forward_cash_forecast_per_customer_charges_expected_loss_as_arrears_build` | 1 → 2 |
| `W2_41_a_household_cancels_its_mandate_as_its_own_act` | 1 → 2 |
| ✓ `PB8_a_households_payment_channel_changes_over_its_tenure` | 2 → 2 |
| `EP4_collections_journey` | 2 → 3 |
| `B7_customer_state_layer_moves_and_shocks` | 1 → 3 |
| `W2_40_voids_tied_to_move_outs` | 1 → 3 |
| `EP12_adapter_css_rec_switching` | 2 → 3 |
| ✓ `B13_a_dual_fuel_household_is_one_account_across_both_fuels` | 2 → 2 |

Lines: 9 done, 6 partial, 0 absent, of 15.

- PARTIAL (payment and debt) the collections desk works arrears to its journey -- EP4_collections_journey at 2, target 3
- PARTIAL (payment and debt) a household cancels its own mandate -- W2_41_a_household_cancels_its_mandate_as_its_own_act at 1, target 2
- PARTIAL (payment and debt) the forward cash forecast charges expected loss as arrears build -- E6_a_forward_cash_forecast_per_customer_charges_expected_loss_as_arrears_build at 1, target 2
- PARTIAL (dual fuel) a mover's final bill and the end of supply -- B7_customer_state_layer_moves_and_shocks at 1, target 3
- PARTIAL (switching) the company decides an objection in the CSS window -- EP12_adapter_css_rec_switching at 2, target 3
- PARTIAL (switching) a save on the loss notice -- EP12_adapter_css_rec_switching at 2, target 3

## Cost of the work to come

Cost of work to come, fitted from 974 landed sessions over 30 days (one point = USD 7.6 weighted; the week holds 100). Each landed session carries its share of the spend that landed nothing: every session spent 695 points, 1.69x what the landed sessions alone spent.

| work class | landed sessions | median points | range | open level steps |
|---|---|---|---|---|
| world_build | 218 | 0.70 | 0.44-1.10 (quartiles) | 102 |
| supplier_build | 129 | 0.70 | 0.51-1.08 (quartiles) | 40 |
| grading_run | 226 | 0.48 | 0.32-0.77 (quartiles) | 1 |
| knowledge_page | 85 | 0.67 | 0.44-0.88 (quartiles) | 3 |
| site_page | 48 | 0.91 | 0.43-1.16 (quartiles) | 21 |
| harness | 131 | 0.48 | 0.35-0.86 (quartiles) | 33 |
| record | 137 | 0.35 | 0.24-0.53 (quartiles) | 6 |

**Landed sessions per level step:** median 2, range 1-9 (quartiles), measured over 11 level steps named by a landed commit; 5 step(s) no landed commit names are left out, not counted as zero. Biased LOW: work toward a step in a commit that does not name the atom is not counted.
**Atom backlog:** 206 open level steps, about 278 points (89-1937), **2.8 weeks (0.9-19.4)** at the full allowance.
**Advisor queue:** 1 director file(s).
**This week:** no reading since Monday's reset (last: 44% at 2026-10-25T06:35 UTC), so what remains is not known.

| step | atom | points | fits this week | split first |
|---|---|---|---|---|
| 2 | W2_36 | 1.4 (to 9.9) | no |  |
| 2 | D48 | 1.4 (to 9.7) | no |  |
| 2 | B7 | 2.8 (to 19.8) | no |  |
| 2 | W2_37 | 2.8 (to 19.8) | no |  |
| 3 | E6 | 1.4 (to 9.7) | no |  |
| 3 | W2_41 | 1.4 (to 9.9) | no |  |
| 3 | B11 | 1.4 (to 9.7) | no |  |
| 3 | EP1 | 1.4 (to 9.7) | no |  |
| 3 | W2_38 | 1.3 (to 8.0) | no |  |
| 4 | W2_39 | 1.4 (to 9.9) | no |  |
| 4 | C34 | 2.8 (to 19.5) | no |  |
| 4 | C35 | 1.4 (to 9.7) | no |  |
| 4 | C29 | 2.8 (to 19.5) | no |  |
| 4 | PB4 | 1.4 (to 9.9) | no |  |
| 4 | PB5 | 2.8 (to 19.8) | no |  |
| 4 | B12 | 1.4 (to 9.7) | no |  |
| 4 | W3_3 | 2.8 (to 19.8) | no |  |
| 5 | EP4 | 1.4 (to 9.7) | no |  |
| 5 | C30 | 4.2 (to 29.8) | no |  |
| 5 | G14 | 1.4 (to 9.9) | no |  |
| 5 | C5 | 2.8 (to 19.5) | no |  |
| 6 | EP16 | 4.2 (to 29.8) | no |  |
| 7 | C4 | 2.8 (to 19.5) | no |  |

**Estimate against actual:** no item drawn with an estimate has landed yet; the draw records one on every Lane 0 item from now on.
**Not yet estimated:** open findings (no classifier reads them yet).

**Within the priority order, never instead of it.** Of two items of equal value take the cheaper. The draw flags (`COST FLAG`) any item estimated above 10 points before it starts; split it, or say why not. A class whose items miss by more than 3x either way is a finding, and its fit is refitted from the landed sessions every time this runs.

## The ranking for this week

_Written by the Monday step. Ordered. Anything above the line outranks new feature work; nothing here outranks a live defect._

*Written after the week it ranks, so it records what the week was ranked by: the seat's stretch focus, under the director's 11 Nov scope.*

1. The fix and its book: the reg 6D refund clock (landed ceeefa5960), the repayment-posting map (landed ad48737415), and the statement walk's set-off (landed 84a44b51c3), all ahead of the 16 Nov book.
2. The value test's 12-draw family, read per household per year (driver 77bf74f880; it reads 14 Nov).
3. The rhythm itself: close this Monday and file Friday, so the 16 Nov balance review has a Friday to read (this commit).

### Deliberately not this week, and why

- Any new fix in level-dd or repayment-posting: both read STOP under W1 until their maps exist. Both now do.
- The eight DO NOT DRAW BEFORE 16 Nov items, plus W3_3, B12 and N17: each grades or changes a book that does not exist yet.
- The three overdue rituals (harness pruning, mothball, CLAUDE.md decay): they are outside "the fix and its book". They go to the first stretch after the 16 Nov reset.

---

Close it with `python3 -m background.weekly_rhythm --close`. That arms the next step — nothing else does — and archives this document to `done/` itself, so the rhythm disposes of everything it files.
