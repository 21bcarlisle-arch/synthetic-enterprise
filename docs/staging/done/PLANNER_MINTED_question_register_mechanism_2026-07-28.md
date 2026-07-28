<!-- SUPERVISOR_DRAW: self-drawable -->
# [PLANNER-MINTED] — Open-question register + mechanical archive-block (deliverable 1) (2026-07-28)

**Source:** `DIRECTOR_RULING_NO_QUESTION_LEFT_UNANSWERED_2026-07-28.md`, deliverable **1** ("A
question-tracking mechanism of your design, with the archive-block enforced mechanically.").

**Provenance:** RUNG-7 planner mint from a ratified ruling's WORK THIS CREATES block (§2+§4,
`DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27` — rulings/steers ARE a mint source).
grep-confirmed NO existing `PLANNER_MINTED_*`/map atom builds a question register or an
archive-block on unanswered questions — net-new. The mechanism design is explicitly the machine's
(§2); this atom carries that design brief.

**Serves:** the ruling's non-negotiable — *"it must be impossible to archive a ruling as consumed
while it carries an unanswered question, enforced mechanically rather than by discipline."* This is
the exact structural sibling of the already-landed `named_but_unminted()` backlog surface
(`background/primary_state_scan.py`): that mechanism made *work* named-and-not-done enumerable from
primary state; this makes *questions* named-and-not-answered enumerable and blocks archival on them.

**Fidelity/robustness gained (one sentence):** a director-ruling question can no longer evaporate on
consumption — it becomes a first-class, enumerable, checkable open item whose non-closure
mechanically prevents the ruling being archived to `done/`.

---
## Design brief (the mechanism is ours — §2)
- **Extraction (how a question becomes an item, and rhetorical-vs-obligation split):** a ruling
  carries questions in ONE of two authoritative forms — (a) an explicit `## QUESTIONS` / "Seed the
  register with these" enumerated block (as THIS ruling's §3 already provides, 6 numbered items), or
  (b) `?`-terminated sentences inside the **DECISION** section only. Prose questions elsewhere
  (rhetorical framing, "why am I the bottleneck?") are NOT obligations. When ambiguous, the
  mechanism defaults to TRACKED (fail-closed toward the ruling's intent) and lets a close-with-reason
  ("the question is wrong, because…") discharge a false positive cheaply — the asymmetry the ruling
  itself names. This split is the design proposal §2 requests; state it in the built artefact.
- **Tracking:** an append-only register (`docs/observability/open_question_register.json` or a
  derivation over the rulings themselves — builder's call, mirror the LAW-C "derive from primary
  state, import nothing from the tick" discipline of `named_but_unminted`). Each row: source ruling +
  git sha, question text, status ∈ {open, answered, carried, wrong}, disposition/answer, first-seen,
  age.
- **Ageing/escalation:** age from first-seen; an open question past a threshold escalates the same
  way named-but-unminted residue does (🔴 in the note, feeds the backlog surface §5 as
  named-and-not-done per the ruling §1).
- **Archive-block (the non-negotiable):** the ruling-consumption/archival path (whatever moves a
  ruling to `done/`) gains ONE gate condition: refuse while the source ruling carries any `open`
  question. Enforced in code, R15-mutation-proven both ways.

## Lane / level / deps
- **Lane:** `H_harness`. BUILD authorized by THIS ratified ruling (tag: **proceed**; gate-after —
  a ratified ruling is standing BUILD auth for its own named scope; NOT an off-front H atom needing
  `director_build_open`).
- **Target level:** `level_current 0 → 3`, **`blocked_on: director_level_up`** (levels are proposals;
  the commit-time gate reverts a self-bump — R16).
- **Deps:** none to start (DISCOVER/design + register build drawable now). Deliverables **2** (seed +
  publish), **3** (daily-note surfacing) and **4** (answers) consume this register's shape.

## Exit criteria
- (a) A question register that enumerates open questions from PRIMARY state (the rulings + git),
  importing nothing from the tick's own enumeration (LAW C independence — mirror `primary_state_scan`).
- (b) The rhetorical-vs-obligation split implemented and documented (the §2 proposal).
- (c) **Archive-block LIVE:** the consumption path cannot move a ruling to `done/` while it carries an
  open question.
- (d) **R15 both ways (mandatory):** MUTATION — a ruling with a demonstrably-open question is offered
  to the archive path ⇒ the gate FIRES (refuses); once all its questions are answered/carried/wrong ⇒
  the gate passes. FAIL-SAFE — an unreadable register/ruling reads **has-open-questions** (block), never
  fail-open to "no questions → archive freely".

## Walls untouched
- **No safety-control / auth / R13 / curriculum move:** an observability + archival-gate mechanism over
  published state only.
- **No level self-bump (R16):** lands `blocked_on: director_level_up`.
- **R15:** the archive-block is a control that can FAIL its own named defect (unanswered-question archival).
