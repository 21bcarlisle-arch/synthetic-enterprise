**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# How often the director accepts the recommendation, by kind of decision (2026-11-17)

*From the director's steer of 17 Nov 07:35 ("Do it"):
`docs/staging/advisor/done/DIRECTOR_STEER_MEASURE_HOW_OFTEN_THE_DIRECTOR_ACCEPTS_THE_RECOMMENDATION_AND_LET_THE_SURE_KINDS_BE_DECIDED_2026-11-17.md`.
Claes's stage 2 to stage 3: compare what was suggested with what was picked, then let the machine decide
where the picks almost always match.*

## Pre-registration (written before any count; the results section is below it and was written after)

**What was seen before writing this.** The resolutions of 3 of the 45 closed `for_the_director` rows,
which were printed while I checked the store's format: all three approved, two of them with amendments. Also
one fact about silence, found while looking for sources: one resolution among the 45 mentions it, and no
structured field records silence anywhere. Nothing else had been read.

**The unit.** One recommendation put to the director and one answer from him.

**Sources.**
- (A) Every closed `for_the_director` row: `background.director_concerns.closes_on_record()`, which merges
  `decisions.jsonl`, the committed revisions of `DIRECTION.yaml` and both live copies. Each row holds the
  machine's `proposal` and his `resolution`.
- (B) `docs/staging/advisor/done/DIRECTOR_RULING_*`: his answer to a recommendation, quoted.
- (C) `docs/staging/advisor/done/DIRECTOR_STEER_*`, only where the quoted words answer a recommendation the
  advisor put to him ("Do it" or "yes" on "the advisor's recommendation"). A steer that is only his own
  initiative is not a decision on a recommendation, and is excluded.
- Excluded: `DIRECTOR_READING_*` (usage readings), `DIRECTOR_EVIDENCE_*` (data he supplied), notices and
  questions. They answer no recommendation.

**Answer codes.** YES: as recommended. AMENDED: approved with a change of substance. NO: rejected, or he
chose otherwise. REDIRECT: he answered a different question or asked for more. SILENCE: taken as yes because
he did not answer. WITHDRAWN: the machine withdrew it, which is excluded from every rate.

**Kinds.** One per decision, assigned by the subject of the recommendation. Where two apply, the first in
this order wins:
1. a G5 wall;
2. strategy, vision or canon intent;
3. a curriculum or world choice (which world the company lives through);
4. a fidelity change (making the world or the supplier more like the real thing);
5. adopting or rejecting an outside source;
6. a measurement or trial;
7. a harness or efficiency change.

**Near-certain.** The Wilson 95% lower bound on explicit plain YES must be at least 0.80. AMENDED counts
against it: an amendment is a case where deciding for him would have been wrong. SILENCE never counts toward
it.

**Predictions.**
- P1. Harness/efficiency: plain YES at least 85%. It is the only kind I expect could reach near-certain, and
  I expect even it to fall short on count (n under 20).
- P2. Measurement or trial: plain YES at least 85%.
- P3. Outside source: YES plus AMENDED at least 90%, because he shares the sources he wants adopted.
- P4. Fidelity: plain YES about 70%, AMENDED about 20%.
- P5. Strategy, vision or canon: plain YES at most 60%, AMENDED at least 30%.
- P6. Curriculum and G5: fewer than 5 each, too few to rate.
- P7. NO is under 10% overall.
- P8. Sources (B) and (C) over-represent YES. A file is written once he engages, and a recommendation he
  turned down in chat may never be filed.
- P9. SILENCE cannot be measured from the record (observed, not predicted; see above).

*The pre-registration above was landed and promoted (3d9dbe930) before any decision was coded.*

## Results (coded after the predictions; one coder, not blind)

**85 decisions**: 44 seat rows from (A); 6 rulings from (B) that no (A) row already counts; 35 advisor
recommendations from (C). One (A) row was withdrawn and is excluded. Four files were excluded because
the recommendation they answered is not written beside his answer (the four reserved questions of 26 Oct,
the NTFY channel of 4 Nov, forward years of 24 Oct, which was his own initiative, and the flex pack of 25
Oct, which has no recorded answer). Every coded decision, with its kind and answer, is listed at the end.

All sources
| Kind | n | YES (of which with additions) | AMENDED | NO | REDIRECT | plain-YES rate, 95% Wilson | near-certain? |
|---|---|---|---|---|---|---|---|
| G5 wall | 4 | 2 (0) | 0 | 1 | 1 | 50% [0.15, 0.85] | no |
| strategy/vision/canon | 23 | 17 (2) | 5 | 1 | 0 | 74% [0.54, 0.87] | no |
| curriculum/world | 7 | 4 (2) | 1 | 1 | 1 | 57% [0.25, 0.84] | no |
| fidelity | 17 | 12 (0) | 2 | 1 | 2 | 71% [0.47, 0.87] | no |
| outside source | 7 | 7 (0) | 0 | 0 | 0 | 100% [0.65, 1.00] | no |
| measurement/trial | 19 | 19 (2) | 0 | 0 | 0 | 100% [0.83, 1.00] | yes |
| harness/efficiency | 8 | 7 (1) | 1 | 0 | 0 | 88% [0.53, 0.98] | no |
| **all** | 85 | 68 (7) | 9 | 4 | 4 | 80% [0.70, 0.87] | |

(A) the seat's for_the_director rows only
| Kind | n | YES (of which with additions) | AMENDED | NO | REDIRECT | plain-YES rate, 95% Wilson | near-certain? |
|---|---|---|---|---|---|---|---|
| G5 wall | 2 | 1 (0) | 0 | 1 | 0 | 50% [0.09, 0.91] | no |
| strategy/vision/canon | 17 | 12 (1) | 4 | 1 | 0 | 71% [0.47, 0.87] | no |
| curriculum/world | 7 | 4 (2) | 1 | 1 | 1 | 57% [0.25, 0.84] | no |
| fidelity | 12 | 7 (0) | 2 | 1 | 2 | 58% [0.32, 0.81] | no |
| outside source | 0 | 0 (0) | 0 | 0 | 0 | - | no |
| measurement/trial | 3 | 3 (0) | 0 | 0 | 0 | 100% [0.44, 1.00] | no |
| harness/efficiency | 3 | 3 (0) | 0 | 0 | 0 | 100% [0.44, 1.00] | no |
| **all** | 44 | 30 (3) | 7 | 4 | 3 | 68% [0.53, 0.80] | |

(B)+(C) the advisor's recommendations only
| Kind | n | YES (of which with additions) | AMENDED | NO | REDIRECT | plain-YES rate, 95% Wilson | near-certain? |
|---|---|---|---|---|---|---|---|
| G5 wall | 2 | 1 (0) | 0 | 0 | 1 | 50% [0.09, 0.91] | no |
| strategy/vision/canon | 6 | 5 (1) | 1 | 0 | 0 | 83% [0.44, 0.97] | no |
| curriculum/world | 0 | 0 (0) | 0 | 0 | 0 | - | no |
| fidelity | 5 | 5 (0) | 0 | 0 | 0 | 100% [0.57, 1.00] | no |
| outside source | 7 | 7 (0) | 0 | 0 | 0 | 100% [0.65, 1.00] | no |
| measurement/trial | 16 | 16 (2) | 0 | 0 | 0 | 100% [0.81, 1.00] | yes |
| harness/efficiency | 5 | 4 (1) | 1 | 0 | 0 | 80% [0.38, 0.96] | no |
| **all** | 41 | 38 (4) | 2 | 0 | 1 | 93% [0.81, 0.97] | |

**Against the predictions.**
- P1 holds: harness 7 of 8 (88%), n under 20, not near-certain.
- **P2 holds, and my expectation beside P1 was wrong.** Measurement or trial is 19 of 19 plain YES, with a
  Wilson lower bound of 0.83. It is the only kind that reaches near-certain. I expected harness to be the
  only candidate and expected it to fall short.
- P3 holds: outside sources 7 of 7. That earns a lower bound of 0.65, and about 16 straight yeses are needed
  to reach 0.80.
- P4 roughly holds: fidelity is 71% plain YES. But the disagreements went to NO and REDIRECT (3), not
  AMENDED (2). All four of the seat's fidelity NO and REDIRECT answers say the same thing: research it, the
  answer is published or is the supplier's own choice (A05, A07, A12, A29). That is K4 being taught one row
  at a time.
- **P5 is refuted.** Strategy, vision and canon is 74% plain YES, not 60% or less, and AMENDED is 22%, not
  30% or more. Part of the cause is one "Agree all" on 12 Oct that closed four of these rows at once.
  Without them it is 13 of 19 (68%, lower bound 0.46): still above my bar, but less so.
- **P6 is half refuted.** Curriculum came to 7 decisions, not under 5: founder counts and seed families went
  to him repeatedly. G5 had 4, as predicted.
- P7 holds: NO is 4 of 85 (5%).
- P8 is consistent with the data, but the data cannot separate its causes. The advisor's recommendations get
  plain YES 93% of the time and the seat's 68%. Within one kind, fidelity is 100% for the advisor and 58%
  for the seat. Two explanations fit: files are written only once he engages (selection), or the advisor
  shapes its recommendation in the chat with him before he answers. Nothing in the record tells these apart.
- P9 holds: SILENCE is 0 coded, because the record never says so. Every rate above is explicit answers only.

**What the count cannot carry.**
- One coder, coding after the predictions were written. The kind boundaries are mine. The contestable
  calls: founder count as curriculum; the losses line (A17) and the carbon definitions as fidelity; the
  early publish (A38) as harness.
- Answers are not independent. One message answered 8 rows on 12 Oct, one answered 3 on 31 Oct, and one
  answered 2 on 10 Oct.
- (A) is what `closes_on_record` finds, and it does not reach before the 5 Oct list began. At least one row
  closed outside it: the reader trial, which was withdrawn on 26 Oct and then ruled on 28 Oct.

## A second coder, and the verdict it changes

This steer was drawn twice. While this count was landing, the interactive seat on the shared tree coded
the same question independently. Its record is
`docs/staging/records/WORKER_RESULT_NO_KIND_OF_DECISION_IS_YET_SURE_ENOUGH_TO_BE_THE_MACHINES_MEASUREMENT_IS_NEAREST_2026-11-17.md`.
It counts 77 decisions on Wilson 90% bounds and concludes that no kind qualifies, with measurement
nearest at 15 of 16. It carries the `based_on` snapshot, the company note, the reading-log row and the
move of the steer to done. So this commit lands none of those, and **this count's proposal to the
director is withdrawn before it reached him**. The two codings are the only inter-coder check this
question has had, so the comparison is recorded here.

**Agreement on the 76 decisions both coded.** (Answers map as YES and YES+ to yes, AMENDED to changed,
and REDIRECT to changed or other.) Answer agreement is 66 of 76 (87%). On the split that decides the bar,
yes against not-yes, it is 69 of 76 (91%). **Kind agreement is 57 of 76 (75%).**
- The measurement/harness boundary takes 5 of the 19 kind disagreements: two-reader review, calibrate the
  readers, estimate the cost of work, the decision map, and abstraction.
- The rest sit on strategy against fidelity or curriculum, and on G5 against harness, outside source or
  fidelity.
- The seven yes against not-yes splits are A06, A09, A12, A13, A19, the third-arm trial and ending the
  feature freeze.

**The verdict turns on one call.** Measurement is 19 of 19 here and 15 of 16 there.
- The difference is the third-arm trial ("Add it, but start by checking it's available on my max plan?").
  This count coded it as yes with an addition; the other coded it as changed.
- Coded as changed, this count gives 18 of 19, with a 95% lower bound of 0.75: not near-certain.
- On the 15 decisions both coders call measurement, it is 14 of 15 yes.
- So the result does not survive a second reader, and F11 sends it the conservative way: **no kind
  qualifies yet.** This corrects the P2 line above, which said measurement is near-certain on this
  count's own coding. That stands as a description of this coding only.

**What this adds to the other record.**
1. Answer codes drawn by a reader weeks later disagree about one time in ten on exactly the line the bar
   tests. The fix is to record the answer code when the answer is recorded (`--answer`), beside `based_on`,
   so the next count does not depend on a coder. That is handed on.
2. The kinds need their boundary written down before a kind can move to the machine. The two coders split
   a quarter of the time, and measurement against harness is the most-used boundary.
3. The 9 advisor and ruling decisions only this count found are all coded and listed below. Six of them
   are plain yes. With them, the other record's "measurement reaches 20 explicit answers" is nearer than it
   looks, depending on the boundary.

## The coded decisions

Kinds: 1 G5 · 2 strategy/vision/canon · 3 curriculum/world · 4 fidelity · 5 outside source ·
6 measurement/trial · 7 harness/efficiency. `YES+` means yes with an addition that changed nothing
recommended. A-ids are the `closes_on_record` rows sorted by close date (A08 withdrawn).

- (A) A00 2 AMENDED · A01 2 AMENDED · A02 4 YES · A03 4 AMENDED · A04 3 YES+ · A05 4 REDIRECT · A06 4 YES · A07 4 NO · A09 3 AMENDED · A10 3 YES · A11 3 REDIRECT · A12 4 AMENDED · A13 2 YES+ · A14 2 YES · A15 2 YES · A16 2 YES · A17 4 YES · A18 2 YES · A19 2 AMENDED · A20 7 YES · A21 4 YES · A22 3 NO · A23 3 YES · A24 2 NO · A25 4 YES · A26 2 YES · A27 3 YES+ · A28 2 YES · A29 4 REDIRECT · A30 2 YES · A31 2 YES · A32 2 YES · A33 1 YES · A34 6 YES · A35 2 YES · A36 2 YES · A37 6 YES · A38 7 YES · A39 7 YES · A40 4 YES · A41 2 AMENDED · A42 1 NO · A43 6 YES · A44 4 YES
- (B) R_correctness_first 2 YES · R_end_freeze 2 YES+ · R_lifecycle_test 6 YES · R_two_reader 6 YES · R_ocf_terms 1 YES · R_release_reading 6 YES
- (C) S_abstraction 5 YES · S_close_checked 7 YES · S_reading_habit 5 YES · S_decision_map 5 YES · S_third_arm 6 YES+ · S_benchmark_tsfm 5 YES · S_calibrate_readers 6 YES · S_cost_per_result 6 YES · S_estimate_cost 6 YES · S_fwd_weather 4 YES · S_frame_needs 2 YES · S_asset_mix 4 YES · S_judge_by_hedge 6 YES · S_measure_data 6 YES · S_measure_tokens 6 YES · S_nothing_logged 7 YES+ · S_plugins 5 YES · S_taxonomy 7 YES · S_one_writer 6 YES · S_prove_fable 6 YES · S_review_own_code 7 AMENDED · S_carbon_defs 4 YES · S_test_claude_md 6 YES · S_skos 5 YES · S_naive_organ 7 YES · S_value_test_answer 6 YES+ · S_weekly_sweep 5 YES · S_time_hassle 4 YES · S_linking_findings 6 YES · S_knowledge_checks 4 YES · S_own_loop 2 AMENDED · S_front_door 2 YES · S_copy_pack 2 YES · S_externals 1 REDIRECT · S_this_steer 6 YES

## Answered

*Worker, 17 Nov.* Closed together with the worker's count
(`docs/staging/records/WORKER_RESULT_NO_KIND_OF_DECISION_IS_YET_SURE_ENOUGH_TO_BE_THE_MACHINES_MEASUREMENT_IS_NEAREST_2026-11-17.md`).
It grades P1-P9 against that count: seven held, P5's YES share refuted narrowly (0.63), and P6 refuted
(7 curriculum decisions). Both codings agree that no kind qualifies. The steer moves to advisor/done
in the same commit, with `based_on` on new rows. The `based_on` change touches only `raise_concern`,
not `--answer`, so it does not collide with `director-answer-code-at-answer-time`.
