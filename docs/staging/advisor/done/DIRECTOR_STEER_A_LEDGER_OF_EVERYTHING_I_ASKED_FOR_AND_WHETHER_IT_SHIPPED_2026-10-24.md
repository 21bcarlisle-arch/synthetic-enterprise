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

## Done

*24 Oct 2026, the delivery seat. First cut `b8b14269e`; the remainder in `6473a1b4e`, `904a091f7`
and the commit that carries this file to done/. The ledger is `tools/director_asks_ledger.py` over
the rulings in `docs/direction/director_asks.yaml`, built at every publish into How it's built and
`site/data/director_asks.json`.*

**1. The ledger, from the record.** 368 rows: every `DIRECTOR_*` asking document in every staging
folder, the canon §15 owed list, the October rulings with no document, and 174 asks itemised from
the 37 console transcripts (his turns only; machine text, answered questions, repeats and asks that
became their own document get no row). By status: **255 shipped, 47 partly, 6 not started,
28 superseded, 2 declined, 24 closed with a Done section naming evidence, 6 open** (the advisor
files still in the queue). **Closed with no evidence: 0**, down from 134; every one of those
documents is now ruled with a commit or a path, each re-verified against git before it was merged.
A 13 Oct "Fate" line on a document was not taken as evidence: several overstate what shipped.

**2. The fifteen in-progress documents.** Ruled in the first cut (`b8b14269e`) and moved to done/:
3 superseded, 2 shipped, 10 partly, each with what is missing and its next step.

**3. The twelve owed items.** Rows `canon_s15_owed_1` to `_12`: 10 shipped with evidence, 2 partly
(the loyalty-finding knowledge page and a named headline-title guard; float against Decimal has
evidence and has never been put to him).

**4. The class.** A director document reaching done/ after 25 Oct without a Done section naming a
commit or a path reds `--check`; an open, partly or not-started ask with no movement for 21 days and
no `held` reason reds it too. Both legs are mutation-proven in
`tests/design/test_a_director_ask_cannot_stand_still_or_close_without_evidence.py`. The control
fired once during this work on its own: six rows merged with `moved` set to the day of the ask went
STALE, and were corrected to the ruling's day.

**5. Published.** How it's built, under "What a human actually decided", shows the counts and every
open row with its next step, and the whole ledger one tap down (`tools/harness_page_figures.py`).

**What the audit found that matters most** (each a `partly` row with its next step):
- he ruled W1_8 zonal pricing out on 21 Jul ("REMA is a waste of time"), yet it is still an open
  map atom at target 3 and B5_regional_basis_risk depends on it (handed on);
- the run manifest and stratified rotation (25 Jul) have no production caller, so the per-run
  ledger and the three separate scores never run;
- the owned-quantity registry gate (28 Jul) was pruned unbuilt on 24 Aug, while the divergences it
  found (net margin, five emission-factor tables) are the class CLAUDE.md names;
- console 8 Sep: a leaky home is heated like a new build ("overstates the saving in exactly the
  homes we'd target"); the setpoint landed (`0388be7c1`) but the inside temperature does not yet
  depend on the fabric;
- console 21 Aug: the write-time gate still fires only on new modules, not on edits to a file that
  holds a control;
- the book of a few thousand (7 Oct) is runnable but not what the live book does.

**Recommended to close** (his call; each is a row): console 31 Aug "fix your task list" (session
hygiene); console 9 Sep weather error at the extremes (the store went per-cell, so the question it
gated is gone); console 10 Sep the two orphaned sessions (swept by later drains); and the
director-record page (18 Aug), which this ledger on How it's built now does the job of.
