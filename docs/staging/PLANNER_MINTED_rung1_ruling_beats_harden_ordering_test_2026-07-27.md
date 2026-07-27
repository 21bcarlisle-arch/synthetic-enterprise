<!-- SUPERVISOR_DRAW: self-drawable -->
# [PLANNER-MINTED] — Rung-1 ordering test: a staged ruling draws BEFORE any HARDEN, asserted at find_work level (§3) (2026-07-27)

**Provenance:** RUNG-7 mint from a ratified ruling's WORK THIS CREATES block (§2+§4, landed 6f2be1d41).
Source: `DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27.md`, deliverable **3** ("Rung-1
ordering test per §3").

**Why a distinct mint (not covered by item 1):** item 1's landed R15 proves the *draw helper*
(`_unconsumed_director_ruling_or_steer` suppresses the HARDEN tier). §3's requirement is stated one
level up — at `find_work()` itself: *"with a HARDEN candidate and an unconsumed staged ruling both
available, the ruling must draw first"* and no HARDEN is appended as an `ALSO`. The banner records item
3 as OPEN precisely because item 1 only *partially* covers it (helper-level, not find_work-level). This
mint closes the gap with the explicit end-to-end assertion.

**Serves:**
- **§3 verbatim** — "Rung 1 means rung 1. A staged `[DIRECTOR-RULING]` or `[STEER]` waiting behind
  HARDEN passes is a rung-order violation."
- The 2026-07-27 08:23–10:25 incident (§0) — the acceptance clause requires today's exact state
  reproduced as a failing test at the level the user experiences it (the `find_work()` primary the
  drawn turn actually receives), not only the internal helper.

**Robustness gained (one sentence):** `find_work()`, given a live HARDEN candidate AND an unconsumed
staged director ruling, returns the ruling as the SOLE `primary` — never the ruling with a
`"ALSO — RULE 0 self-refill … HARDEN"` tail — proven to go RED if the rung order is inverted.

---

## Scope — BUILD (harness lane)
- **Lane:** harness. **Target level:** L2 (test-only hardening of a landed mechanism).
- **Exit criteria:**
  1. A test in `tests/background/test_supervisor.py` that drives the REAL `find_work()` (not just the
     helper) with a fixture where both a HARDEN re-verify candidate and an unconsumed staged ruling are
     present, and asserts: (a) the returned primary is the ruling's mint instruction; (b) the returned
     text contains NO HARDEN `ALSO` clause.
  2. **R15 both ways (binding):** mutate the ordering (let the HARDEN `ALSO` append despite the
     unconsumed ruling, or invert the rung priority) → the test goes RED; restore → green. The mutation
     must target the ORDERING, not the helper already covered by item 1's tests.
  3. Fixture isolation per [[feedback_new_draw_rung_needs_fixture_isolation]] — pin any register/flag
     paths the new test touches so it does not red the existing "map empty → rest" find_work tests.
- **Deps:** item 1 (landed) — this asserts item 1's mechanism at the find_work boundary; no new
  production code expected (test-only) unless the assertion surfaces a real ordering gap, in which case
  fix it in `supervisor.py` under this atom. Disjoint file_scope from #1 (deadman/daily-note) → concurrent.

## Walls untouched
- One-way doors: none — test-only git-reversible change.

## Window
Director-ruled; drawable now. Failing test FIRST is the deliverable itself.

— Planner mint, RUNG-7 refill from ruling WORK THIS CREATES §4, 2026-07-27.
