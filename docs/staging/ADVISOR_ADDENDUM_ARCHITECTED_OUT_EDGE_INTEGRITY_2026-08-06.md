# [ADVISOR-ADDENDUM] — Edge integrity as MAP's precondition (2026-08-06)

**Amends:** `DIRECTOR_PROGRAMME_ARCHITECTED_OUT_2026-08-05.md`. Does not supersede it: the goal, the
MAP → NET → KNIFE → RHYTHM sequence, the write-time gate, the target-design document and the board
shape all stand unchanged. Three amendments only, all to weighting and coverage.

**Status:** director-prompted, advisor-staged. Mechanisms are the worker's, as in the parent programme.

**Context for zero-context readers:** the parent programme names *write-time blindness* as the cause of
duplicate mechanisms, unwired modules and four orphan-transition instances, and answers it with MAP
(a derived capability index consulted before anything new is minted), NET (five system join tests),
KNIFE (hotspot consolidation) and RHYTHM (consolidation at every epoch close). This addendum reads
that programme against `ADVISOR_REVIEW_MATURITY_MAP_TAXONOMY_2026-08-05.md`, staged the day before,
and finds three joins between them that neither document makes.

---

## A1 — MAP inherits degraded edges; F2/F5(a) are its precondition, not its neighbours

MAP is first in sequence because it is lowest risk. But a derived index is worth exactly what the
fields it derives from are worth, and the taxonomy review reports those fields degraded:

- 48 files claimed by more than one atom, and whole directories claimed as scope (`docs/design` by 31
  atoms, `tools` by 16, `background` by 13) — a directory claim makes ownership unanswerable there.
- Four `blocked_on`/`depends_on` values hold prose rather than atom ids, so the dependency graph is
  uncomputable as it stands.
- The same fields are sometimes string, sometimes list.

**Required outcome:** before MAP's index is treated as an authority the builder must consult, its
input fields must be able to answer "who owns this file" and "what does this depend on" mechanically.
Whether that means fixing the fields, deriving from source rather than from the map, or narrowing
what the index claims to cover is the worker's call — but an index built on unarbitrable scope will
report reuse candidates it cannot stand behind, and a write-time gate is only as trustworthy as its
worst row.

## A2 — F5(c) temporal provenance is the stale-cell class, not a tidy-up

The taxonomy review files "provenance carries zero dates" under registry integrity details, beside
"one atom has `epoch: None`". That understates it.

A cell reading L0 while its artefacts on disk say L2 is a validity-window failure: an assertion that
was true when written and is silently false now, with nothing carrying when it was written or when it
was last checked against reality. This is a recurring class, not an instance — most recently the
DD cell reading level 0 with no ledger entry while all six sub-parts were built, committed and live.

The company layer is already built bitemporal (`bitemporal_event_log.py`, valid-time and
transaction-time). The governance layer that steers it is not. **Required outcome:** a map assertion
should carry when it was made and when it was last verified against the artefacts it claims, so
staleness is a query rather than a discovery. Re-use of the existing bitemporal primitive is the
obvious candidate; whether it fits is the worker's judgement, and per the parent programme's own
rule, forced reuse that couples two purposes is equally a defect.

## A3 — The gate cannot catch the orphan class; that needs a standing read-time query

The write-time gate asks *do we already have this?* It cannot ask *is this still wired?*

Every orphan instance to date passed write time cleanly and rotted afterwards: a mandate register
that lost its callers, a coupler with no production caller and an emitter that never emits, a
`comfort_constraint_for` parameter no caller ever supplied, a tool claimed as a production caller
that grep refutes on both halves. Each was a live mechanism with a dead input or a dead mechanism
with a live claim. No gate at mint time would have seen any of them.

**Required outcome:** the same derived surface that answers "do we already have this?" should also
answer, on a standing basis, "what is asserted here that the code no longer supports" — mechanisms
with no caller, claimed evidence paths that do not exist, cells whose level contradicts their
artefacts. Absence must be queryable, not discoverable. Per R15 the queries must be failable and
mutation-proven: remove a real caller and the orphan list must light up, or the query is decoration.

---

## Decided vs open

**Decided (director, 2026-08-06):** these three are amendments to the parent programme's weighting and
coverage; the programme itself is unchanged and remains ratified.
**Open to the worker:** every mechanism — how edge integrity is achieved, whether the bitemporal
primitive is reused or a lighter form suffices, how and when the standing queries run, and the
sequencing of A1 relative to MAP's first delivery.
**Reserved (unchanged):** epistemic-law enforcement, safety controls, REPO_PRIVATE, R13 dials.

## Risk

**What it touches:** the sequencing of an already-ratified programme, and — if A1 is taken literally —
`maturity_map.yaml`'s own fields, which are the draw's input.

**Blast radius:** editing scope or dependency fields changes which atoms are drawable. A careless pass
could block real work or fail open and grant colliding forks. This is the same surface that produced
the parked-dependency cascade and the target-matched draw bug.

**Probable failure:** A1 is read as licence for a large field-normalisation sweep across 185 atoms,
consuming a lane and destabilising the draw mid-flight.

**Mitigations, inline:** treat A1 as report-first — measure which fields are unarbitrable and publish
the list before changing any of them; change scope fields for one lane at a time, never map-wide;
prove the draw returns the same candidate set before and after each pass, and stop if it does not.
A2 and A3 are additive (new fields, new queries) and carry no draw risk if they assert nothing the
draw reads until proven.

**Proportionality:** A2 and A3 reversible and narrow — just do them. A1 touches the draw's input —
named mitigations above apply, report before edit.

---

*Advisor addendum, 2026-08-06. Sources read this session: the parent programme, the taxonomy review,
the structural audit, and status/LATEST.md.*
