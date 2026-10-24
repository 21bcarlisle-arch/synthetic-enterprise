**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] A ledger of everything the director asked for, and whether it shipped (2026-10-24)

**Type:** STEER, through the advisor channel. The director's words, from chat on Sat 24 Oct. This follows today's finding that the front-door diagram's L2 layer (ruled 9 Oct) and its live picture (ruled 27 Jul) only half shipped:

- 09:45 BST: "Ok. Are there other things I've asked for this never finished shipping?? (Maybe for good reason, maybe not?)"

**When:** start now; first cut by the Monday 26 Oct publish. The machine holds the record, so the audit is yours. What follows is the advisor's quick look, a starting point.

---

## What the advisor found in a quick look (origin, 24 Oct)

1. **Fifteen director documents are still in `docs/staging/in_progress/`, most from July:**
   - `DIRECTOR_STEER_LEGIBILITY_AND_SEGMENTATION_2026-07-20`
   - `DIRECTOR_STEER_COVERAGE_STAGE4_VALUE_FRONTIER_2026-07-20`
   - `DIRECTOR_STEER_SITE_REORIENT_TO_PURPOSE_2026-07-19`
   - `DIRECTOR_STEER_WHOLESALE_VALUE_CHAIN_2026-07-22`
   - `DIRECTOR_STEER_SCENARIO_SPINE_AND_TRADING_FRICTION_2026-07-23`
   - `DIRECTOR_RULING_SITE_MODEL_SPINE_2026-07-23`
   - `DIRECTOR_CAMPAIGN_SITE_MODEL_SPINE_2026-07-23`
   - `DIRECTOR_RULING_SITE_REBUILD_V5_STRUCTURE_2026-07-23`
   - `DIRECTOR_AXIS1_SITE_VERDICT_ROWSCORED_2026-07-23`
   - `DIRECTOR_STEER_DUNNING_DEBT_PROVISIONING_2026-07-25`
   - `DIRECTOR_RULING_MOTHBALL_THE_APPARATUS_2026-07-29`
   - `DIRECTOR_INSTRUCTION_QUERYABLE_PROJECTIONS_2026-08-10`
   - `DIRECTOR_DECISION_PENDING_RATE_REBASELINE_AND_SPLIT_APPROVAL_2026-08-14`
   - `DIRECTOR_BRIEF_WEBSITE_STRUCTURE_2026-08-17`
   - `DIRECTOR_RULING_FRONT_DOOR_STAYS_SIMPLE_AND_EXPLORATION_GOES_DEEPER_2026-10-09`
2. **Canon §15 "Owed to the director", 12 items.** The canon-alignment steer of 12 Oct, step 7, required "for each … either show the evidence that it is done or do it … Report each in the stretch log". The advisor can find no such report, and that steer sits in `done/` without a Done section. The items are:
   - the merge-cost measurement;
   - the triage of carried items;
   - the responsiveness-correlation proposal;
   - SLC 22B;
   - the "price keyed to the meter" paraphrase;
   - the owed knowledge pages and the headline–title guard;
   - float against Decimal;
   - the CLV discount rate;
   - the text of R16 and R17;
   - the parked-documents audit (123 documents);
   - why every stretch-log fix goes quiet within a week;
   - the one-word mode control and the route measurement, which may be partly answered by `tick_mode` and `--routes`.
3. **Rulings this month with no build yet, from today's page reviews:**
   - gas follows a moving household (ruled 17 Oct, knowledge page landed 22 Oct);
   - the cap's published levels ingested as a binding series;
   - the pricing engine still "Planned" against C13;
   - settlement true-ups "Planned" while the world says Live;
   - the L2 diagram sheets (9 Oct).

## WORK THIS CREATES

1. **Build the ledger from the record, not from memory.** Cover every director ask since June: each `DIRECTOR_*` document in every staging folder, every advisor-channel file, console words in the director input log, canon rulings, and the §15 owed list. One row per distinct ask, with these columns:
   - the ask, in his words, with the date;
   - the status: **shipped** (link the evidence: commit, page or control), **partly shipped** (what is missing), **not started**, **superseded** (by what, with the ruling), or **declined** (with the reason he accepted);
   - for anything not shipped: why, and whether the reason still holds;
   - the next step, or a recommendation to close it (G9).
2. **Rule on the fifteen in-progress documents.** Close each as shipped or superseded, with evidence. Otherwise put it into the priority order with a next step. Nothing stays "in progress" by default.
3. **Report the twelve owed items.** Give evidence of delivery, or deliver in priority order. That is what step 7 of the 12 Oct steer required.
4. **Fix the class (P13).** A director document reaches `done/` only with a Done section that links its evidence. A partly shipped ask stays visible as a row until it ships or he releases it. Make the ledger a generated, standing view, refreshed at each publish. Add a control that reds when an ask has had no movement for 21 days without a recorded reason. Prove it able to fail (R15).
5. **Publish it.** Put a summary on How it's built under "What a human actually decided": counts by status, and the open rows with their next step, so the director can see it without asking. Keep the full ledger one tap down.

## Report

One stretch-log entry with:
- the ledger's counts by status;
- the fifteen in-progress rulings;
- the twelve owed items;
- the mechanism;
- the open asks you recommend he close or drop, each with a recommendation.

— Director steer, 24 Oct 2026, his words above; the quick look and drafting are the advisor's.
