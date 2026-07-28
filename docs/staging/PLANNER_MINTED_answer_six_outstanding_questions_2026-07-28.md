<!-- SUPERVISOR_DRAW: self-drawable -->
# [PLANNER-MINTED] — Answer the six outstanding director questions, batched (deliverable 4) (2026-07-28)

**Source:** `DIRECTOR_RULING_NO_QUESTION_LEFT_UNANSWERED_2026-07-28.md`, deliverable **4** ("Answers to
the six — batched, not one at a time.").

**Provenance:** RUNG-7 planner mint from the ruling's WORK THIS CREATES block. grep-confirmed net-new.
This is the substantive INVESTIGATION half — reading primary state to answer each of the six §3
questions. Distinct from deliverable **2** (which seeds/publishes the register and may carry a row with
a reason); this atom produces the actual answers, batched, so the register rows flip `carried →
answered`. Drawable NOW, doc-only (DISCOVER / L3) — **no dependency on the mechanism** (deliverable 1):
the answers are found by reading git + disk, and can be recorded in the ruling's own answer block or a
staged findings doc pending the register.

**Serves:** the ruling's core decision — "an answer may be I-don't-know / not-yet-measurable /
the-question-is-wrong; what may not happen is silence." The advisor recorded these as *his* to have
chased; this atom chases them.

**Fidelity/robustness gained (one sentence):** six director questions that were absorbed without a
returning answer get batched, evidence-backed answers (or an explicit I-don't-know / not-measurable /
wrong-question disposition) — closing them per the ruling's own definition of closure.

---
## The six (with the primary state to read for each)
1. **`merit_order` drawable only from 2026-07-28 — why, and is it drawing now?** Read `d81197736` §5,
   the maturity map atom's `loop_stage`/gate/`drawable_from`, and TODAY's draw log
   (`docs/observability/run_history.json` / discovery-log). Answer: gate/dep/artifact + drawing-now Y/N
   with evidence.
2. **Harness exit-criterion counter reading + last-reset cause; wired to primary state?** Read the
   exit-criterion mechanism (`docs/design/HARNESS_EXIT_CRITERION_PROPOSAL_2026-07-27.md` /
   `DIRECTOR_RULING_HARNESS_EXIT_CRITERION_RATIFIED_2026-07-27`) + its counter state. If it cannot
   observe last night's HARDEN-while-unminted, say so plainly ("not yet a control").
3. **Cohort assignment status.** Read `e685eb76d`, `1494d6160` §4a, and the CA1–CA4 atoms
   ([[project_cohort_activation_ruling_minted]]: ALL 4 BUILT, `blocked_on level_up`). Answer: BUILT,
   blocked on director_level_up — cite the atoms.
4. **Stall-set coverage verdict on the four events.** For each of console rescue / publish-gate wedge
   >1h / origin freeze >30m / advisor restart-ruling: detected by a live detector, detector added, or
   argued out? Cross-check the deadman/liveness tiers + memories
   ([[project_overnight_liveness_freeze_and_operational_red_2026_07_25]],
   [[feedback_self_verifying_push]], [[project_eighth_class_pending_batch_deadlock_2026_07_27]]).
5. **Staleness disposition in the gap taxonomy.** Read `27271871e` §3a + the gap register / coupled-gap
   ledger. Answer the disposition (aged-out / carried / re-triaged).
6. **Blast radius as positive value vs risk.** Read `27271871e` §3b. Answer or mark
   the-question-is-wrong / not-yet-measurable with reasoning.

## Lane / level / deps
- **Lane:** `L3 DISCOVERY` (doc-only). Drawable NOW — no `director_build_open` / no code change.
- **Target level:** N/A (a findings/answers artefact, not a levelled atom); records answers for the
  register (deliverable 2) to consume.
- **Deps:** none to produce the answers; feeds deliverable 2.

## Exit criteria
- Each of the six has a batched, evidence-backed answer OR an explicit I-don't-know / not-yet-measurable
  / the-question-is-wrong-because disposition — **none silent** (ruling §1).
- Each answer cites the primary state read (git sha / file / atom), not assertion (R9: evidence before
  narrative).
- Recorded where the register (deliverable 2) can consume them (the ruling's answer block or a staged
  findings doc), so the six can be closed and the ruling eventually archived.

## Walls untouched
- **R9:** every answer labelled observed-with-evidence or inferred; evidence before narrative.
- **R12:** answers are diagnostics; nothing is tuned toward them.
- **No safety/auth/curriculum/level move** — a read-only investigation.
