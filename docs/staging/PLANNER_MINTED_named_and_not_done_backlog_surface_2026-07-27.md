<!-- SUPERVISOR_DRAW: self-drawable -->
# [PLANNER-MINTED / PROPOSE-THEN-PROCEED] — "Named-and-not-done" must be enumerable and checkable from primary state (§5) (2026-07-27)

**Provenance:** RUNG-7 mint from a ratified ruling's WORK THIS CREATES block (§2+§4, landed 6f2be1d41).
Source: `DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27.md`, deliverable **5** ("Backlog
surface per §5, first output = the named-but-unminted enumeration"), **as restated by the amendment**.

**The RESTATED problem (amendment governs):** ignore the prescribed surface shape. The requirement is:
*"everything named-and-not-done must be enumerable and checkable, so that 'no below-target work
anywhere' can be verified against reality rather than asserted."* One wall (per LAW C): it must derive
from **primary state** (the map, the staging tree, the rulings/steers themselves), **never from the
tick's own enumeration**. Whether the answer is a published surface, a live query, a daily-note
assertion, or a gate check is the builder's to design — state the reasoning and evidence for the choice.

**Serves:**
- **§5 (restated)** — makes "no below-target work" a CHECKABLE claim, closing the §0 root cause (the
  tick asserted "no below-target work anywhere" while three named items sat unminted).
- **LAW C (independent verification)** — the checker must not read the tick's own belief; it re-derives
  from primary state, so a tick that is wrong about being idle is caught by an organ it cannot influence.
- The daily self-note honesty contract ([[project_overnight_liveness_freeze_and_operational_red_2026_07_25]],
  R17) — "no below-target work" in the morning note must be backed by this enumeration.

**Robustness gained (one sentence):** any claim that the authorized work set is empty is checkable
against an independently-derived enumeration of everything named-and-not-done (source → atom-or-
"unminted" → lane → status → age), computed from primary state rather than from the tick's own
say-so — so a false "idle" reading is caught, not published.

---

## Scope — PROPOSE-THEN-PROCEED (harness/observability lane)
- **Lane:** harness / observability. **Target level:** L2.
- **Design choice to make FIRST (the amendment gives this to the builder — decide + justify):** which
  form best satisfies "enumerable AND checkable from primary state" at least cost —
  (a) a gate/assertion the deadman or daily-note runs (cheapest, no new published surface), or
  (b) a derived observability artifact + site backlog panel (most visible, more surface to maintain).
  Recommendation to evaluate: START at (a) — a derivation function that scans primary state
  (maturity_map.yaml + staging tree incl. PLANNER_MINTED docs + the rulings' WORK THIS CREATES blocks
  via the landed §4 parser) and yields the named-and-not-done set; the daily note asserts against it and
  the deadman can consult it. Add a published surface only if the director wants the window. State the
  reasoning per LAW A ("the plan is a diagnostic").
- **Exit criteria:**
  1. A derivation (call it `named_and_not_done()` or similar) that reads ONLY primary state — NOT the
     tick's cached enumeration (LAW C wall; independence R15: mutate a primary source, e.g. add an
     unminted deliverable to a ruling's block, and the enumeration must change).
  2. **First output = the current named-but-unminted set** (§5's explicit first job) — reuse the §4
     parser (`work_this_creates_deliverables`) across staged/in_progress rulings & steers, diff against
     minted atoms (map + PLANNER_MINTED docs), emit the residue. Verify this mint tick's own output:
     after these mints land, items 3/4/5/6 show as MINTED (not unminted), item 1-gap as MINTED, item 2
     as covered.
  3. **R15 both ways (binding):** seed a known named-but-unminted item → it appears in the enumeration;
     mint it → it disappears. Mutate the derivation to read the tick's own "idle" belief instead of
     primary state → the LAW-C independence test goes RED.
  4. Wired to a real consumer (daily note assertion and/or a gate) so "no below-target work" is checked,
     not asserted.
- **Deps:** item 2 (landed — the §4 parser this reuses). Complements #1 (which excludes HARDEN from
  work accounting) and #4 (missing-block surface). Some file_scope overlap with #1 in `daily_self_note.py`
  — if built concurrently, coordinate the daily-note edits (serialize or disjoint functions).

## Walls untouched
- One-way doors: none — git-reversible harness/observability change.
- LAW C wall is binding: never derive the check from the tick's own enumeration.

## Window
Restated as a PROBLEM by the amendment → propose the form (a vs b) with reasoning before building the
larger option; the derivation + first-output enumeration (option a core) is drawable now.

— Planner mint, RUNG-7 refill from ruling WORK THIS CREATES §4, 2026-07-27.
