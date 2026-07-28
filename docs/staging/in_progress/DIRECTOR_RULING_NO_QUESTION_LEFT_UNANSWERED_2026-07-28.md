<!-- MINT COVERAGE MAP (updated worker tick 2026-07-28, commit d05dd80af) — deliverables 1-3 BUILT,
deliverable 4 in flight. NOT archived to done/: this ruling still carries UNANSWERED questions (§3),
and by its own §1 it is NOT fully consumed while any is unanswered — now ENFORCED MECHANICALLY, not
by this banner (tools/ruling_archive_question_gate.py refuses the archival commit; R15-proven both
ways at the git boundary). Parked in in_progress/. REMAINING BLOCKING SUB-ITEM: (4) five of the six
§3 questions are only CARRIED (non-silent, with a reason), not yet ANSWERED — the archive gate blocks
until they close (answered / I-don't-know / not-measurable / wrong).
  [1] LANDED — question-register mechanism + archive-block gate LIVE (background/open_question_register.py, tools/ruling_archive_question_gate.py, wired into pre-commit). Mint archived to done/. Level blocked_on director_level_up (R16).
  [2] LANDED — register SEEDED + published, 0 silent (docs/observability/open_question_register.json: Q3 answered, five carried-with-reason). Mint archived to done/.
  [3] LANDED — daily-note open-question line LIVE (background/daily_self_note.open_question_line; live render: 5 unanswered, 0 silent). Mint archived to done/.
  [4] IN FLIGHT — PLANNER_MINTED_answer_six_outstanding_questions (in_progress/, L3 DISCOVER, self-drawable). Q3 (cohort) answered; Q1/Q2/Q4/Q5/Q6 carried pending the batched investigation.
This ruling's OWN archive gate now governs its archival: it will permit done/ only once every §3
question carries a CLOSING disposition (not merely 'carried'). The mechanism enforces the rule on
itself — the acceptance test made real. -->
<!--
ORIGINAL BANNER (superseded 2026-07-28 by the above; retained for provenance):
all 4 WORK-THIS-CREATES deliverables MINTED as self-drawable atoms; deliverable 1's archive-block
was not yet built; BLOCKING SUB-ITEMS were (1) mechanism not built; (4) the six not yet answered.
-->

# [DIRECTOR-RULING] — No question left unanswered. A question is a first-class open item. (2026-07-28)

**Type:** [DIRECTOR-RULING] via advisor bridge. Director's instruction, verbatim: *"Let's never leave questions unanswered please."*

## 0. The bug, named

When a ruling is consumed, its **work items** are minted and tracked. Its **questions evaporate** — nothing treats a question as an item that must be closed. Consequence: at least six questions posed in director rulings over the last two days appear to be outstanding, each absorbed without an answer ever returning.

This is the same class as the backlog finding — named-and-not-done that nothing enumerates — applied to questions instead of work.

## 1. DECISION

**A question posed in a director ruling or steer is a first-class open item.** It must be enumerable, tracked, and answered. Consequences:

- **A ruling is not fully consumed while any of its questions is unanswered.** Consumption today means "work items minted, doc archived"; that is now insufficient. Archiving a ruling with open questions is a claim-status defect.
- **Unanswered questions are named-and-not-done** and therefore belong in the backlog surface established by the coherence ruling §5, subject to the same requirement: enumerable and checkable from primary state, never asserted.
- **An answer may be "I don't know", "not yet measurable", or "the question is wrong, because…"** — all three close a question. What may not happen is silence.
- **This binds the advisor equally.** Before staging any ruling, the advisor checks the open-question register — to avoid re-asking what has been answered, and to chase what has not been. An advisor who forgets his own questions has no standing to demand answers.

## 2. PROBLEM — the mechanism is yours

How questions are extracted from rulings (an explicit block? a parser? a convention?), where they are tracked, how they are aged and escalated, and how they surface in the daily note — **your design.** You know the consumption path and the observability surfaces.

One non-negotiable: it must be **impossible to archive a ruling as consumed while it carries an unanswered question**, and that must be enforced mechanically rather than by discipline — the lesson of every rule this project has: exhortations decay, mechanisms hold.

If you judge some questions genuinely rhetorical or answered-in-passing, propose how the mechanism distinguishes those rather than treating every sentence with a question mark as an obligation.

## 3. Seed the register with these — outstanding as far as the advisor can see

If any of these was in fact answered, **say where** and close it; the advisor may have missed it in the mirror.

1. **Why was `merit_order` drawable only from 2026-07-28?** (from `d81197736` §5.) Epoch gate, dependency, or scheduling artifact — and *is it drawing now*, since that date is today?
2. **What does the harness exit-criterion counter currently read, and what caused the last reset?** (from `d81197736`, repeated in `1494d6160` §4b.) A night of HARDEN-while-content-unminted should have been resetting it; if it is not yet wired to primary state, say so — a criterion that cannot observe last night is not yet a control.
3. **Cohort assignment status** (from `e685eb76d`, repeated in `1494d6160` §4a): done, in flight, blocked, or counter-proposed? No cohort or coverage-report work has appeared since the ruling.
4. **Stall-set coverage verdict** on the four named events — console rescue, publish-gate wedge over an hour, origin freeze over thirty minutes, advisor restart-ruling (from `d81197736` §3). Detected, detector added, or argued out?
5. **Staleness disposition** in the gap taxonomy (from `27271871e` §3a).
6. **Blast radius as positive value versus risk** (from `27271871e` §3b).

## WORK THIS CREATES

1. A question-tracking mechanism of your design, with the archive-block enforced mechanically.
2. The register seeded and published, with the six above either answered or carried with a reason.
3. Questions surfaced in the daily note alongside the other open items.
4. Answers to the six — batched, not one at a time.

Acceptance: no ruling can be archived carrying an unanswered question, and the current open-question set is inspectable from published artifacts without asking the machine.

**Risk & proportionality:** adds a tracked item class and one archive-gate condition; mechanism is the machine's. Tag: **proceed.**

— Advisor bridge, carrying the director's instruction — and recording that the six outstanding questions are the advisor's to have chased. 2026-07-28.
