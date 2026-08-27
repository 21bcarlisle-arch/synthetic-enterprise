**Severity:** LATENT · **Lane:** H_harness

# WORKER FINDING — the evidence page's fixture copies one of the map's two halves, so its fail-open floor is red and the two raise-tests above it rest on nothing

**Staged:** 2026-08-27, worker tick (EP13 map-cap rehome draw). **Class:** `F_harness` · R15 FAIL-OPEN.
**Rank:** after the current top item — a red control that is NOT in any commit gate's target set, so it
blocks nothing today and is queued per SELF_INTERRUPT rather than fixed on sight.
**Not caused by this tick's change.** Attributed below against `HEAD`, both sources restored.

## The observation

`tests/tools/test_evidence_pages.py::test_the_record_store_actually_supplies_the_citations` is RED:

```
assert cited > 50, f"only {cited} citations built -- the store is not feeding this page"
E   AssertionError: only 15 citations built -- the store is not feeding this page
```

The live page is fine. `tools.generate_evidence_data.build_payload()` against the real tree builds
**214 citations over 46 atoms, 209 resolved / 1 relocated / 4 missing**. The same call through the
test's `sources` fixture builds **15 citations over 4 atoms**. The page is not the subject that is
broken; the fixture is.

**Attribution — `observed-with-evidence`, not inferred.** Rebuilt with all four fixture sources AND
every store file restored from `HEAD` via `git show`: still 15. The count is identical before and
after this tick's `maturity_map.yaml` / `EP13_adapter_carbon_intensity.yaml` edit, so the red
pre-dates it.

## The cause

The map has been **split into two halves** (`tools/maturity_map_store.py::map_text` — *"the live half
then the closed half, concatenated"*). Every reader gets the whole map through `map_text`, which
reads `docs/design/maturity_map.yaml` and appends `_closed_text(...)`.

The fixture (`tests/tools/test_evidence_pages.py:387`) copies four source files by
`shutil.copy2(src, tmp_path / src.name)` and copies the record store with `copytree`. It copies the
**live half only**. Measured:

| | `map_text` bytes | atoms |
|---|---|---|
| live tree | 311,909 | **298** |
| fixture copy | 101,033 | **74** |

So 224 of 298 atoms do not exist in the fixture's map at all. The 46 atoms the node→atom mapping puts
on the page mostly resolve `in_map: False`, carry no record, and therefore no citation — 42 of 46.

The fixture's docstring says *"Real copies of all four sources under tmp_path"*. It is a **five**-source
build (H41 made the record store the fifth, and the fixture was extended for exactly that reason — see
its own comment at line 401). The split made it six. The comment that was added when the store became a
source is the shape of the fix that was missed when the map became two files.

## Why this matters beyond one red

This test is a **declared fail-open floor**, in its own words:

> *"FAIL-OPEN FLOOR for the two tests above: prove the store is what the citations come from, not
> merely that removing it raises. Without this, a build that got its evidence from somewhere else
> entirely would still satisfy both raise-tests."*

The two tests it floors (`test_the_record_store_is_load_bearing`, `test_an_empty_store_raises`) delete
or empty the store and require `EvidenceSourceUnavailable`. On a fixture where 42 of 46 atoms are
already unresolvable, those raises are cheap — and the floor that was built to say so is the thing
that is red. **The floor is doing its job; nobody is reading it.**

Second, `_attach_rehomed_names` has a two-tier fail rule — raise if *not one* declared name resolves,
render blank for a single absence. Under the fixture exactly **4** resolve out of ~296 declared. That
is one atom away from the raise and reads as a pass. A ratio, not a `not resolved`, is what that rule
was trying to express.

## Repair, recommended (not taken this tick)

1. Fixture: copy **both** map halves. Derive the closed-half path from
   `maturity_map_store` rather than naming it, so a third half cannot reintroduce this.
2. Assert the fixture's own subject: `atom_records(fixture_map)` must yield the same atom COUNT as the
   live map. A fixture that silently loses 75% of its population is the defect, and no downstream
   assertion can see it.
3. `_attach_rehomed_names` / `_attach_rehomed_evidence`: make the unavailable-source tier a
   **proportion** (e.g. `resolved < 0.5 * declared` raises), so "the store is mostly not being read"
   fails as loudly as "the store is not being read at all".

R15 note for whoever takes it: the repair is only proven when the fixture-count assertion in (2) is
mutation-tested by reverting (1) — the citation bar alone is a number that can be met by a fixture
that is wrong in a different way.

## Evidence

* `python3 -m pytest tests/tools/test_evidence_pages.py -q` → 1 failed, 59 passed.
* `tools/maturity_map_store.py::map_text` — the two-half concatenation.
* `tests/tools/test_evidence_pages.py:387-406` — the fixture, and its own H41 comment.
* Not in any commit gate target set: `pre_commit_test_gate.select_targets` for the map and store paths
  returns 8 tests, none of them this file.
