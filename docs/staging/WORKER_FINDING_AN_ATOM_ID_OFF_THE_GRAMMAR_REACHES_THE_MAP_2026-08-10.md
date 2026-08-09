# WORKER FINDING — the atom-id grammar is checked only where the commit gate cannot see it

**Found:** 2026-08-10, during the H34 build (incidental — not that atom's scope).
**Disposition:** fixed the INSTANCE in passing because it was about to be committed red;
QUEUED the CLASS as an atom. Not blocking.
**Rank:** backlog unless someone is wedged by it.

## Observed, with evidence

An atom `OPS_surgical_landing_tool` sat in the working tree's
`docs/design/maturity_map.yaml` (uncommitted, minted this cycle from
`DIRECTOR_RULING_HOOK_BYPASS_IS_A_WALL_2026-08-09`) and in the derived
`site/data/maturity_map.json`. Its id does not match the map contract's grammar:

```
$ python3 -m pytest tests/design/test_maturity_map_contract.py::test_a_every_id_matches_grammar_or_is_allowlisted -q
E   AssertionError: id(s) off the ^[A-Z]+[0-9]+_[a-z0-9_]+$ grammar and not on LEGACY_IDS
E   (rename onto the grammar, do NOT extend the allowlist): ['OPS_surgical_landing_tool']
```

`observed-with-evidence`. The same mint DID register the id on
`tests/design/test_maturity_map_facets.py::REVIEWED_CLOSE_TO_LEARN`, so the author
was following the registration checklist — the grammar is simply not part of any
check that runs when an atom is written.

`inferred`: the id is a lane prefix with no ordinal (`OPS` where `OPS1`, `OPS2` and
`OPS3` already exist), which reads like a hand-written id rather than one derived
from the lane's next free ordinal.

## Why the check did not fire before the map was written

Two gaps, and the second is the one that makes this a class:

1. **Nothing validates an id at MINT time.** `ID_GRAMMAR` appears in exactly one
   place in the tree — `tests/design/test_maturity_map_contract.py`. Grep over
   `tools/`, `background/` and the rest of `tests/` returns nothing. Every writer
   of the map (planner mints, self-refill, a hand edit) can emit any id it likes.

2. **The pre-commit gate does not run that test on a map change.**
   `tools/pre_commit_test_gate.py::LEVEL_SENSITIVE_TESTS` runs the level/ledger
   tests plus `tests/design/test_maturity_map_facets.py` on a
   `docs/design/maturity_map.yaml` edit — deliberately, per its own comment about
   the F1c registration incident — but NOT `test_maturity_map_contract.py`. So an
   off-grammar id is committable, and only the full publish suite says so. That is
   the same shape as the incident that put the facets test in that list.

## What was done here, and what was not

**Instance, fixed:** renamed to `OPS4_surgical_landing_tool` (the next free ordinal
on that prefix) in the map and in the `REVIEWED_CLOSE_TO_LEARN` allowlist. The atom
is unbuilt (`level_current: 0`, `loop_stage: build`, no artefacts), so the rename
costs nothing and is reversible. Renamed rather than allowlisted because the
contract test says in as many words: *rename onto the grammar, do NOT extend the
allowlist*.

**Class, NOT fixed (this is the atom):** the grammar belongs where ids are made, and
`test_maturity_map_contract.py` belongs in `LEVEL_SENSITIVE_TESTS`. R10 — an
absurdity-class defect may not be closed with an instance fix.

## The exit criteria a fix would have to meet

1. Every map writer validates the id against the LIVE `ID_GRAMMAR` before writing,
   with the grammar declared in ONE place both the writer and the test read (a
   second copy is the two-sources-of-truth defect the notes-store contract already
   names).
2. The next free ordinal for a lane prefix is DERIVED from the map, so a writer
   cannot pick `OPS` when `OPS1..OPS3` exist.
3. `tests/design/test_maturity_map_contract.py` joins `LEVEL_SENSITIVE_TESTS`, so
   an off-grammar id is uncommittable rather than merely reported by the publish
   suite. Check first whether the whole `tests/design/` directory should be the
   unit there — three separate design tests have now each been added after their
   own incident, which is the accretion pattern OPS1 forbids.
4. R15 both ways: a synthetic off-grammar id FAILS the writer, and a legitimate new
   id PASSES — with the failure proven at the write, not only at the test.
