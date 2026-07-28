<!-- SUPERVISOR_DRAW: self-drawable -->
# [PLANNER-MINTED] — Surface open questions in the daily self-note (deliverable 3) (2026-07-28)

**Source:** `DIRECTOR_RULING_NO_QUESTION_LEFT_UNANSWERED_2026-07-28.md`, deliverable **3** ("Questions
surfaced in the daily note alongside the other open items.").

**Provenance:** RUNG-7 planner mint from the ruling's WORK THIS CREATES block. grep-confirmed net-new
— `background/daily_self_note.py` carries the `named_and_not_done_line` (open WORK) but has no
open-QUESTION line. This adds the sibling line for the question register.

**Serves:** the ruling §1 — unanswered questions "belong in the backlog surface established by the
coherence ruling §5, subject to the same requirement: enumerable and checkable from primary state."
The daily note is where named-and-not-done work already surfaces; questions surface there too,
"alongside the other open items."

**Fidelity/robustness gained (one sentence):** every morning the self-note reports the open-question
count and the oldest open question, exactly as it already reports named-but-unminted work — so an
outstanding director question is visible daily, not only on demand.

---
## Lane / level / deps
- **Lane:** `H_harness` (one derived line in `daily_self_note.render_note`, mirroring
  `named_and_not_done_line`).
- **Target level:** `blocked_on: director_level_up` for any level claim (R16).
- **Deps:** the register from **deliverable 1** (this line reads it). Can land in the same increment as
  deliverable 1; kept as a distinct atom because the ruling names it distinctly.

## Exit criteria
- `daily_self_note.render_note` carries an open-question line: 🔴 with count + oldest when any question
  is open, ✅ CHECKED when the open set is empty — derived from PRIMARY state (the register / rulings),
  never from the tick's own belief (LAW C).
- A live rendered note quoted showing the line populated by the seeded six (deliverable 2).
- **R15 / consumer test:** a test in `test_daily_self_note.py` asserts the line renders 🔴 when an open
  question exists and ✅ when none — the fail-open direction (a missing register silently dropping the
  line) is covered.

## Walls untouched
- **R11/R17:** the note is an honesty surface; the line is enumerable + checkable, not asserted.
- **No level self-bump (R16):** `blocked_on: director_level_up`.
- **No safety/auth/curriculum move.**
