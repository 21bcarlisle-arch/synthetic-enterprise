# The capability index — AO1, the reuse surface

**Atom:** `AO1_capability_index` (lane H_harness, L0→L2, 2026-08-08).
**Serves:** `DIRECTOR_PROGRAMME_ARCHITECTED_OUT_2026-08-05.md` step **MAP**, specified by
`ADVISOR_PROPOSAL_CAPABILITY_INDEX_AND_DEMO_2026-08-04.md` §1, amended by
`ADVISOR_ADDENDUM_ARCHITECTED_OUT_EDGE_INTEGRITY_2026-08-06.md`.
**Mechanism:** `tools/capability_index.py`. **Proof:** `tests/tools/test_capability_index.py`.

---

## Purpose, guarantees, why — before the mechanism

*(Stated first per the OPS1 don't-accrete rule: a mechanism added without a designed reason
tracing to the goal is forbidden.)*

**Purpose.** Answer *"do we already have this?"* in seconds, so that writing fresh stops being
the cheapest move available to a turn.

**Why it is needed, in evidence rather than principle.** The programme names the cause —
**write-time blindness** — and the director lists the damage: two DD mandate registers (one with
zero callers), a back-billing module found by collision, a `comfort_constraint_for` parameter no
caller ever supplied, four orphan-transition instances, a from-scratch working-day calculator
written on 2026-08-03 while `company/compliance/working_days.py` already existed and `holidays`
sits in the ecosystem. None of that was carelessness. Across ~840 production modules, discovering
what exists genuinely cost more than creating it again. This changes that price and nothing else.

**Guarantees.**

1. **Every row is derived from source at query time.** No committed index artefact, no register,
   nothing a turn can forget to update. The index cannot be stale because it does not persist.
2. **Coverage is proven against an independent oracle, not assumed.** Every tracked non-test `.py`
   under a declared root has a row, checked against `git ls-files` — a different source from the
   filesystem walk the rows come from.
3. **No silent exclusion.** A top-level directory holding tracked Python is a declared root or
   carries a written reason; a new package cannot land invisible.
4. **Absence is visible.** Missing description, missing test evidence and missing callers are
   *rows*, not gaps you would have to already suspect in order to look for.

**What it does not do.** It does not decide anything. It does not force reuse — the director's
wall stands: *forced reuse that couples two purposes is the mirror error of duplication and is
equally a defect.* The index makes the look cheap; the choice stays the builder's, and recording
that choice is AO2's job, not this one's.

---

## What a row is, and why the module

One row = one production Python module. Rejected alternatives, and the reason:

| Unit | Why not |
|---|---|
| Maturity-map atom | The map's `file_scope` is reported unarbitrable (below). An index built on it inherits that. |
| Package / subsystem | Too coarse to answer a reuse question — "billing exists" does not tell you `add_working_days` does. |
| Function | ~40k rows nobody reads, and the import a builder writes is module-shaped anyway. |

The module is the unit a builder actually reuses (`from company.billing.working_days import …`),
the only unit that exists on disk without ambiguity, and the one that already carries an authored
description — its docstring, written once, beside the code, by whoever knew what it was for.

Per row, the proposal's four questions:

- **plain words** — the docstring's first sentence. `null` means *unnamed capability*: a real row,
  never a skip, and never a filename dressed up as a description.
- **status** — `wired` (something imports it or runs it by path), `entrypoint` (a command),
  `orphan` (neither), `package` (namespace-only `__init__.py`), `unparsed` (could not be read).
- **evidence** — the test files that import or drive it. Nothing can be *claimed* here, because
  the list **is** the grep.
- **demo** — how you would see it: a site surface it writes, a test run, a command.

## The addendum, answered

**A1 — degraded edges are MAP's precondition.** Satisfied by construction, not by a field sweep:
**the index never reads `maturity_map.yaml`.** Every field comes from source. The 48 multiply-claimed
files, the directory-level scope claims and the four prose `depends_on` values cannot degrade an
index that does not consult them. The addendum's own risk section names the alternative — "A1 read as
licence for a large field-normalisation sweep across 185 atoms, consuming a lane and destabilising
the draw" — and this delivery touches nothing the draw reads.

**A3 — the gate cannot ask "is this still wired?"** `--orphans` is the standing read-time answer, and
it is mutation-proven: remove the only caller of a real module and it appears. It counts **references
by path** as callers, not only imports — `background_worker.py` runs `run_queued_tasks.py` via
`exec(open(...))`, and the first run of this tool called that live dispatcher an orphan. Reporting a
working mechanism as dead is how a retirement pass deletes something load-bearing, so the false-orphan
reading is a defect of the same weight as the miss.

**A2 — temporal provenance** is not addressed here. It is a property of *map assertions*, and this
index makes none: it re-derives on every query, so "when was this last verified against reality" is
answered by *now*. A2 belongs to whatever continues to assert levels, not to this atom.

## R15 — an index is a textbook fail-open control

An index that under-reports does not look broken. It looks like a small codebase. The builder reads
"nothing to reuse" and writes the duplicate — so a wrong index is **worse than no index**, because
the answer now carries authority. The integrity checks are therefore the substance of the tool:

| Guard | Fires when | Mutation that proved it |
|---|---|---|
| Vacuity floor | Fewer than `ROW_FLOOR` rows | `if len(rows) < ROW_FLOOR` → `if False` |
| Per-root vacuity | A declared root exists but yields no rows | (as above, separately witnessed) |
| Coverage hole | A tracked non-test file has no row | drop a known module from the rows |
| Unclassified root | A top-level package is neither declared nor excused | add `trading/` and `git add` it |
| Unparsed | A file cannot be read | suppress the finding |
| Oracle unavailable | git cannot answer | `raise` → `return []` |

**Tautology, killed explicitly.** Coverage compares the row walk against `git ls-files`, not against
itself; `test_coverage_oracle_is_independent_of_the_row_walk` breaks the walk while leaving git's
view intact and requires the finding to appear. A walk checked against itself would pass by
construction and prove nothing.

**Fail-silent, killed explicitly.** rc 2 ("could not run") is distinct from rc 0 ("clean"), and an
unavailable oracle raises rather than returning an empty list that would agree with an empty index.

**The R15 test that was itself blind.** The first version of the floor test asserted only that some
finding began with `VACUITY` — a tag the per-root guard also emits. Deleting the floor outright left
all 23 tests green. That is the union-metric blindness reappearing *inside* an R15 test, and it was
only found by mutating the source. The floor now has a test that witnesses it alone, on a tree where
every root has rows and coverage is whole.

## Write-time gate, applied to this atom's own build

The programme's rule, applied to the tool that implements the programme: `tools/generate_capabilities_json.py`
already exists and produces `site/data/capabilities.json`. **Not extended, for cause** — it is a
hand-authored register of ~12 marketing cards for the company page, whose prose is deliberately
static and whose only derived field is a headline number from the latest run. AO1 needs the
opposite properties (every field derived, all ~840 modules, absence made visible). Extending it
would have coupled a public brand surface to a build-time developer query, which is the coupling
error the director names as equal in weight to duplication. The two share no code and answer
different questions.

**Ecosystem question, part class CUSTOM.** The derivation is repo-specific — the wall, the lanes,
the harness conventions. Standard library `ast` and `git` do the general work; nothing was
hand-rolled that a library provides. No new dependency was added, so no pin or determinism
statement is owed.

## Using it

```
python3 tools/capability_index.py --find "working day"   # before you write anything
python3 tools/capability_index.py --orphans              # what is asserted but no longer wired
python3 tools/capability_index.py --unnamed              # capability nobody described
python3 tools/capability_index.py --json --out /tmp/i.json
```

Runs in ~3s over the whole repo. rc 0 = trustworthy, 1 = integrity findings (do not stand behind
it), 2 = could not run.

## First run — a dated observation, not a maintained figure

2026-08-08, commit at the time of writing. **Reproduce rather than cite: these numbers are derived
and will move.**

- **837 rows** — 490 wired, 57 entrypoint, 268 orphan, 97 unnamed, 67 with no test evidence.
- **Orphans concentrate almost entirely in `company/`: 260 of 268** (background 5, simulation 3).
  That corroborates the July dependency analysis KNIFE target ("~320 zero-import company modules")
  from an independent derivation, and puts the number at 260 once path-invoked callers are counted.
- **97 unnamed rows** — code with no docstring — is AO1's own first finding: those are the modules
  most likely to be built twice, because nothing describes them to the next reader.

## What this atom does not deliver

The gate (AO2), the join tests (AO3), the hotspot passes (AO5). This is MAP: the lowest-risk step
and the safety condition for the rest. The index without the gate is a demo — that is the
director's own framing, and it is the reason AO2 is drawable the moment this lands.
