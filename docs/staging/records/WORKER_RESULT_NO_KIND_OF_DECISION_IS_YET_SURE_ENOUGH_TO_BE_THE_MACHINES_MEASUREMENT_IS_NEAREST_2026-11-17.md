**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# No kind of decision is yet sure enough to be the machine's; measurement is nearest at 15 of 16 (2026-11-17)

*Answers part 1 of `docs/staging/advisor/done/DIRECTOR_STEER_MEASURE_HOW_OFTEN_THE_DIRECTOR_ACCEPTS_THE_RECOMMENDATION_AND_LET_THE_SURE_KINDS_BE_DECIDED_2026-11-17.md`.
The kinds, the answer codes, the qualifying rule and the predictions below were written before any
answer was counted. Per the steer, this goes in the stretch log and the Friday review, not to the
director: no kind qualifies, so there is nothing for him to rule.*

## Answer

**No kind qualifies.** Measurement is nearest: he accepted 15 of 16 measurement recommendations as
they were made, and the 90% lower bound is 0.76 against the 0.80 the rule needs. At the next
answer it qualifies if no more than one of its first 20 is changed. With two changed it needs 28.
Strategy is lowest: 12 of 19 explicit answers (0.63), and every one of the other seven is a
change, not a refusal. Across 77 decisions he refused one recommendation outright: the off-box
routine of 13 Nov ("We already have a check").

| kind | decisions | yes | changed | no | silence | other | yes share of explicit | 90% bound | qualifies |
|---|---|---|---|---|---|---|---|---|---|
| fidelity | 11 | 8 | 2 | 0 | 0 | 1 | 0.80 | 0.54-0.93 | no |
| measurement | 16 | 15 | 1 | 0 | 0 | 0 | 0.94 | 0.76-0.99 | no |
| outside_source | 6 | 6 | 0 | 0 | 0 | 0 | 1.00 | 0.69-1.00 | no |
| harness | 13 | 11 | 2 | 0 | 0 | 0 | 0.85 | 0.63-0.95 | no |
| curriculum | 7 | 6 | 1 | 0 | 0 | 0 | 0.86 | 0.55-0.97 | no |
| strategy | 20 | 12 | 7 | 0 | 0 | 1 | 0.63 | 0.44-0.79 | no |
| g5 | 4 | 3 | 0 | 1 | 0 | 0 | 0.75 | 0.36-0.94 | no |

Bounds are Wilson at 90%. Strategy, curriculum and g5 stay with him whatever their rate, so their
rows are shown for completeness, not as candidates.

## The sources, and what each misses

| Source | Holds | Misses |
|---|---|---|
| `for_the_director` closes (`director_concerns.closes_on_record`: decisions.jsonl, DIRECTION.yaml history, the live copies) | 45 rows, 5 Oct to 16 Nov, each with the proposal and his answer in `resolution` | Rows raised before 5 Oct carry no `resolution`. Its own kinds (strategy, canon_intent, vision, reserved) are where a row was sent, not what it decided. |
| `docs/staging/advisor/done/` headers quoting his reply "on the advisor's recommendation" | 32 replies, 24 Oct to 17 Nov (two of them today's steers, still in `advisor/`; two already counted as `for_the_director` rows are dropped) | **Survivorship.** The advisor stages what he said yes to, so a refusal in chat leaves no file. Prediction 3 held: there is no "no" in it. Its rates are upper bounds. |
| `docs/direction/director_asks.yaml` | Whether each of his own asks shipped | His asks, not his answers to ours. Not used. |
| Any source | | **Silence.** Silence closes nothing: a row stays open until answered, and a balance proposal that "stands" at the reset leaves no answer record. Zero silence in the table means "not recorded", not "did not happen". |

Fidelity, harness and curriculum come mostly from the unbiased source; measurement and
outside_source come mostly from the biased one (13 of 16, 6 of 6). So the kind nearest the line
is also the one whose rate is most likely to be high because of how it was recorded.

## Prediction against result

| | Predicted | Result |
|---|---|---|
| 1. harness and measurement highest, point >= 0.9 | both >= 0.9 | measurement 0.94; **harness 0.85, refuted**; outside_source 1.00 is the highest |
| 2. strategy lowest, <= 0.6, rest mostly changed | <= 0.60 | **0.63, refuted narrowly**; lowest, and all seven others are changes, none a refusal |
| 3. no "no" in advisor/done | none | none, held |
| 4. at least one kind qualifies (harness), on advisor data | qualifies | **refuted: none qualifies** |

## Pre-registration (written 2026-11-17 ~08:10Z, before any answer was counted)

Seen before writing this: 3 for_the_director resolutions (two "APPROVED ... amended", one truncated)
and the 27 advisor/done header lines quoting his reply to an advisor recommendation (all yes-shaped:
"Yes", "Do it", "Stage it", "Measure it", "Add it", one "Go, but also ..."). That is a look at
roughly a third of one source, so the predictions below on advisor files are not blind.

**A decision** is one recommendation put to him (a for_the_director row, or an advisor
recommendation his quoted reply answers), counted once, under the kind of what was recommended.

**Kinds** (one per decision, by what the recommendation would change):
- `fidelity` -- how the world models reality (physics, data, behaviour).
- `measurement` -- run a measurement, trial, probe, benchmark or experiment before changing anything.
- `outside_source` -- adopt or reject an outside source, tool, plugin, model or framework.
- `harness` -- the machine's own process: gates, queues, seats, efficiency, publishing, the site's upkeep.
- `curriculum` -- which world the company lives through (forward years, book depth, switches of world).
- `strategy` -- strategy, vision, canon intent, mission wording, supplier product direction.
- `g5` -- a G5 wall (reserved action).

**Answers**: `yes` (explicit, recommendation unchanged; an unrelated extra ask beside it still counts
yes and is flagged); `changed` (explicitly accepted with an amendment or condition to the
recommendation itself, or a different option chosen); `no`; `silence` (closed as yes because he did
not answer); `other` (withdrawn by the machine, or returned without a ruling).

**Near-certain**: the kind's `yes` share of EXPLICIT answers (yes+changed+no) has a Wilson 90% lower
bound >= 0.80, on >= 10 explicit answers. Silence never counts toward it.

**Predictions.**
1. `harness` and `measurement` have the highest yes shares (point >= 0.9).
2. `strategy` has the lowest explicit-yes share (point <= 0.6), most of the rest `changed`, few `no`.
3. Source bias: the advisor channel stages what he said yes to; a "no" in chat leaves no file. So
   advisor-sourced rates are upper bounds. Prediction: no `no` appears in advisor/done at all.
4. At least one kind qualifies (predicted: `harness`), but only on advisor-sourced decisions, so the
   proposal has to carry the source bias.

## A second pre-registration, graded on this count

A seat lane pre-registered the same steer on its own at 08:32Z
(`docs/staging/done/SEAT_FINDING_HOW_OFTEN_THE_DIRECTOR_ACCEPTS_THE_RECOMMENDATION_BY_KIND_2026-11-17.md`,
3d9dbe930). Its timestamp is in git; the one above was written at about 08:10Z and is on disk only, so
the seat's is the better-dated of the two. Its bar is stricter: a Wilson **95%** lower bound, kinds
in a priority order, and REDIRECT kept apart from NO. Here it is graded on this count, where "changed"
holds both AMENDED and REDIRECT. Under its bar no kind qualifies either; measurement's 95% lower bound
is 0.72.

| Seat prediction | Result on this count |
|---|---|
| P1 harness plain YES >= 85%, short on count | 11 of 13 (0.85), n under 20: **held** at the line |
| P2 measurement plain YES >= 85% | 15 of 16 (0.94): **held** |
| P3 outside source YES + AMENDED >= 90% | 6 of 6: **held** |
| P4 fidelity YES about 70%, AMENDED about 20% | 8 and 2 of 10 (80%, 20%): **held**, roughly |
| P5 strategy YES <= 60%, AMENDED >= 30% | 12 and 7 of 19 (63%, 37%): YES **refuted narrowly**, AMENDED held |
| P6 curriculum and G5 under 5 each | curriculum 7: **refuted**; G5 4: held |
| P7 NO under 10% overall | 1 of 76 explicit answers: **held** |
| P8 sources B and C over-represent YES | no NO in the advisor source: **held** |
| P9 SILENCE not measurable | not recorded anywhere: **held** |

**The second coding (0fadd2b9b).** The seat then coded 85 decisions itself and reconciled them
against this record. On the 76 decisions both of us coded, answers agree 66 of 76 (69 of 76 on yes
against not-yes), but kinds agree only 57 of 76. The measurement/harness boundary is the most
contested. Under its own coding, measurement is 19 of 19 (95% lower bound 0.83), which would qualify.
The whole difference is one call, the third-arm trial ("Add it, but start by checking..."): coded as
changed, as here, it is 18 of 19 (bound 0.75). Where both coders call a decision measurement, it is
14 of 15. **So the verdict holds: no kind qualifies yet.** It also shows that a kind's verdict can
turn on one coding call. Before any proposal, the kind boundary needs a fixed rule (or the answer
needs coding at answer time, the seat's continuation `director-answer-code-at-answer-time`), not a
reader's judgement after the fact. Nine of its decisions are not in this count; six are plain yes.

## The coding, one row per decision

`ftd` is a `for_the_director` close, `adv` an advisor-channel reply. A "yes" with an unrelated
ask beside it stays yes and is noted.

| decision | source | kind | answer | note |
|---|---|---|---|---|
| `step-1-s-knowledge-says-the-priority` | ftd | strategy | changed |  |
| `household-carbon-is-mostly-heating-gas-is` | ftd | strategy | changed |  |
| `home-moves-can-now-be-switched-on` | ftd | curriculum | yes |  |
| `b8-no-uniform-renewal-cut-from-2` | ftd | strategy | changed | timing condition and home-mover retention added |
| `the-founder-ceiling-and-prospect-cap-sized-by-rare-events` | ftd | curriculum | yes | budget raised beside it |
| `the-save-offer-needs-two-practitioner-figures` | ftd | strategy | changed | refused the figures, sent to published switching data |
| `acquisition-selects-on-each-prospects-own-responsiveness` | ftd | fidelity | changed | option 1 plus option 2 run both ways |
| `the-world-s-arrears-read-1-67x` | ftd | fidelity | changed | a range from Ofgem data, not the Centrica bound |
| `does-a-retention-discount-offered-to-a` | ftd | strategy | other | withdrawn by the seat |
| `whether-per-customer-pricing-beats-a-flat` | ftd | curriculum | yes | authorised under the seed-family runner |
| `the-scale-lane-s-seed-families-need` | ftd | curriculum | yes |  |
| `c34-s-debt-decision-cannot-be-graded` | ftd | strategy | changed | merged into a personal payment plan |
| `practitioner-question-at-an-annual-direct-debit` | ftd | fidelity | yes | he said it was answerable from Ofgem |
| `the-advisor-trial-steer-sonnet-5-5` | ftd | harness | changed | capped at seven days; seat stays on Opus |
| `the-end-to-end-review-of-claude` | ftd | harness | yes | 'Agree all' |
| `time-is-scored-in-minutes-not-converted-to-money` | ftd | strategy | yes | 'Agree all' |
| `no-atom-can-reach-l3-while-an` | ftd | harness | yes | 'Agree all' |
| `a-household-s-electricity-carbon-is-shown` | ftd | fidelity | yes | 'Agree all' |
| `c34-next-best-action-the-customer-s` | ftd | strategy | yes | 'Agree all' |
| `the-run-s-company-cannot-learn-whether` | ftd | strategy | yes | 'Agree all' |
| `a-held-lane-crash-can-now-wake` | ftd | g5 | yes | 'Agree all' |
| `the-capital-target-binds-from-2025-but` | ftd | fidelity | yes | 'Agree all' |
| `the-founder-number-has-two-readings-now` | ftd | curriculum | changed | households, not supply points |
| `your-400-household-founder-ruling-fits-in` | ftd | curriculum | yes | memory watched on three runs |
| `your-22-oct-front-door-steer-lists` | ftd | strategy | changed | build scale goes on the front door |
| `the-estimated-bill-can-read-the-customer` | ftd | strategy | yes | became the 23 Oct switch-on delegation |
| `canon-h1-owes-r16-and-r17-section` | ftd | strategy | yes |  |
| `forward-years-ruling-of-24-oct-17` | ftd | curriculum | yes | checkpoint-and-resume added |
| `the-26-oct-advisor-steer-asks-that` | ftd | strategy | yes |  |
| `a-practitioner-question-k4-published-sources-exhausted` | ftd | fidelity | other | returned: a supplier choice, not his |
| `the-improvement-loop-world-then-supplier-then` | ftd | strategy | yes |  |
| `the-time-steer-s-hidden-value-of` | ftd | strategy | yes |  |
| `m3-names-three-currencies-money-time-carbon` | ftd | strategy | yes |  |
| `licensed-microdata-for-the-customer-needs-corpus` | ftd | g5 | yes | 'non commercial'; he registers |
| `the-value-test-redesign-two-choices-in` | ftd | measurement | yes |  |
| `your-2-nov-ruling-to-register-with` | ftd | strategy | yes |  |
| `the-next-world-additions-ranked-30-oct` | ftd | fidelity | yes |  |
| `the-design-read-of-the-value-test` | ftd | measurement | yes |  |
| `the-publish-window-is-anchored-to-monday` | ftd | harness | yes |  |
| `off-box-liveness` | ftd | harness | yes |  |
| `the-customer-carbon-figure-co1-inherits-neso` | ftd | fidelity | yes |  |
| `value-test-baseline-and-axis-weighting` | ftd | strategy | changed | 'Yes. No.' -- a hidden weighted utility |
| `the-off-box-dead-man-misses-stops` | ftd | g5 | no | 'We already have a check' |
| `the-value-test-s-sized-book-candidate` | ftd | measurement | yes |  |
| `ep11-is-titled-direct-debit-against-a` | ftd | g5 | yes |  |
| `A_THIRD_ARM_OPUS_WITH_A_FABLE_ADVISOR` | adv | measurement | changed | check the Max plan first |
| `MEASURE_WHERE_READING_TOKENS_GO` | adv | measurement | yes |  |
| `GO_ON_THE_TWO_READER_REVIEW` | adv | harness | yes | extra question beside it |
| `THE_VALUE_TEST_MUST_BE_ABLE_TO_ANSWER` | adv | measurement | yes | extra ask beside it |
| `JUDGE_THE_FORECAST_BENCHMARK_BY_HEDGE_COST` | adv | measurement | yes |  |
| `BENCHMARK_ONE_COMPANY_FORECAST_AGAINST_A_FREE_TS_MODEL` | adv | outside_source | yes |  |
| `RELEASE_THE_READING_TOKEN_MEASUREMENT` | adv | measurement | yes |  |
| `END_THE_FEATURE_FREEZE_A_THIRD_TO_FEATURES` | adv | harness | changed | a weekly balance review added as a condition |
| `PROVE_FABLE_SERVED_EVERY_FABLE_READING` | adv | measurement | yes |  |
| `NOTHING_LOGGED_IS_LEFT_TO_MALINGER` | adv | harness | yes | extra ask beside it |
| `HOW_EACH_ASSET_IS_RUN_IS_A_SOURCED_MIX` | adv | fidelity | yes |  |
| `CALIBRATE_THE_READERS_ON_OUR_HISTORY` | adv | harness | yes |  |
| `FORWARD_WEATHER_AND_PRICES_MUST_MOVE_TOGETHER` | adv | fidelity | yes |  |
| `THE_WEEKLY_SWEEP_GAINS_A_FILTERED_GITHUB_SCAN` | adv | outside_source | yes |  |
| `ABSTRACTION_IS_ONE_RESEARCH_FAMILY` | adv | measurement | yes |  |
| `ESTIMATE_THE_COST_OF_WORK_TO_COME` | adv | harness | yes |  |
| `OFFICIAL_PLUGINS_EARN_THEIR_PLACE` | adv | outside_source | yes |  |
| `FRAME_THE_CUSTOMER_NEEDS` | adv | strategy | yes |  |
| `MEASURE_WHAT_COMMITTED_GENERATED_DATA_COSTS_US` | adv | measurement | yes |  |
| `TEST_CLAUDE_MD_BY_DELETING_AND_ADDING_BACK` | adv | measurement | yes |  |
| `ONE_WRITER_PER_SHARED_FILE_MEASURE_FIRST` | adv | measurement | yes |  |
| `THE_NAIVE_ORGAN_HAS_REFUSED_EVERYTHING` | adv | harness | yes |  |
| `STATE_OUR_CARBON_DEFINITIONS_SECOND_CHECK` | adv | fidelity | yes |  |
| `ONE_LIGHT_TAXONOMY_FIVE_FACETS` | adv | harness | yes |  |
| `THE_MAP_REGISTER_BORROWS_SKOS_FIELDS` | adv | outside_source | yes |  |
| `WOULD_LINKING_FINDINGS_TO_CONCEPTS_HAVE_CAUGHT` | adv | measurement | yes |  |
| `A_STANDING_EXTERNAL_READING_HABIT` | adv | outside_source | yes |  |
| `OCF_UK_PV_TERMS_ACCEPTED` | adv | outside_source | yes |  |
| `A_STEER_WITH_MORE_THAN_TWO_OUTCOMES_GETS_A_DECISION_MAP` | adv | harness | yes |  |
| `TIME_IS_VALUE_A_SUPPLIER_CAN_CREATE` | adv | strategy | yes |  |
| `COST_PER_RESULT_AND_REWORK_RATE (17 Nov)` | adv | measurement | yes | extra ask beside it |
| `MEASURE_HOW_OFTEN_THE_DIRECTOR_ACCEPTS (17 Nov)` | adv | measurement | yes |  |

## From now on: the snapshot

Each new `for_the_director` row now carries `based_on`, the commit its recommendation was written
against (`director_concerns.based_on_snapshot`; Claes's `BasedOnSnapshotId`). A later reader can
then check his answer against what was known when he was asked. Rows raised before today have none.

## The company side (a note, not a build)

The company partly does this. `company/governance/decision_rights.py` keeps a bitemporal decision
log: each event has request, context, decision, rationale, valid time and transaction time. But
only two call sites write to it: the renewal desk and the ledger's write-offs. Two of the six
registered classes are wired. And `context` is a free dict per call site, not a reference to a
reproducible view of what the supplier could see. M4's method would need each customer decision
(price, DD amount, collections step, advice) to log the view it read, keyed to a point-in-time
snapshot (`company/interfaces/point_in_time_view.py` is the natural key). Not built here.

## When to read it again

When measurement reaches 20 explicit answers. If at most one is changed, it qualifies, and the
proposal goes to `for_the_director` as one line, carrying the source-bias caveat above. The
`based_on` field makes the next count checkable against what he knew.

**Reverse:** delete this record. Nothing reads it.
