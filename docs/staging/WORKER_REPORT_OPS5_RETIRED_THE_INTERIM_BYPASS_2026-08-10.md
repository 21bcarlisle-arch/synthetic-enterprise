# WORKER REPORT — OPS5: the interim bypass shape is retired, and held by a guard (2026-08-10)

**Atom:** `OPS5_retire_the_interim_bypass_shape` (L0→L2, self-certified into
`gate_authorizations.jsonl`) · deliverable 2 of the WORK THIS CREATES block in
`DIRECTOR_RULING_HOOK_BYPASS_AND_SURGICAL_LANDING_2026-08-09`.

## What was done

The 2026-08-09 ruling sanctioned exactly one interim hook-bypass shape (four conditions
together) **with an expiry attached to one event: the arrival of the tool**. `OPS4` landed
(`a86dc9f3f`), so the expiry fell due. It is now executed rather than announced:

1. **`docs/design/SURGICAL_LANDING.md`** — the retirement section is rewritten from
   forward-tense ("expires with this tool… is OPS5") to a past-tense record carrying a
   machine-readable marker:
   `<!-- INTERIM_BYPASS_SHAPE: RETIRED 2026-08-10 -- replaced by tools/surgical_land.py (OPS5) -->`
2. **`CLAUDE.md`** — now states **HOOK-BYPASS IS A WALL** *and*, in the same bullet as the
   shared-tree commit discipline it serves, the legal move
   (`python3 -m tools.surgical_land -m "<msg>" -- <paths>`). Both halves deliberately together:
   a wall stated without its legal move is what produced the 2026-08-09 bypass.
3. **`tests/tools/test_interim_bypass_retirement.py`** — the mechanism (MAKE_IT_STICK). Four
   guards; **7 named mutations run and each observed red on its own defect**, file green on
   restore. The forward-tense guard needed no mutation: it was **red on HEAD** on the doc's own
   live sentence until this atom rewrote it.
4. **`tools/pre_commit_test_gate.py`** — new `CANON_SURFACE_FILES` (third sibling of
   `LEVEL_SURFACE` / `MINT_MARKER`): editing CLAUDE.md or the design doc re-runs the guard at
   commit time instead of leaving it to the publish suite.

**R11, the release triggers something:** the retirement is bound to a **subprocess** check that
`python3 -m tools.surgical_land --help` runs green — withdrawing the exception while the
replacement is dead would leave *no* legal move on a dirty shared tree, which is the failure
SURGICAL_LANDING.md's own argument predicts. A subprocess, not an import, because this repo has
already paid for a CLI entry point that in-process tests were blind to.

**Vacuity:** the class guard scans `CLAUDE.md` + `docs/design/**.md` (not `docs/staging/**` —
the rulings there are the historical *record* and must keep saying the exception was granted)
and requires the design doc to keep describing what was retired, so deleting the section cannot
make the control pass by having nothing to check.

**CLAUDE.md size:** was 34,979 / 35,000 chars — no room for the wall. Trimmed three bullets that
are provably restated elsewhere in the same file, then added the wall: **34,974 chars, 128
lines**. Removed: *"Observability artifacts verified by fetch"* (→ R11 + R1 + R2, verbatim),
*"The simulation is not the company"* (→ the whole Architectural Laws section), *"Non-blocking
concurrency"* (→ RULE 0 + R17 + the stronger no-polling-wait rule). Also compressed the
tree-lock bullet's tail, keeping every fact.

## One thing deliberately NOT landed — needs disposition

`docs/design/maturity_map.yaml` carries my OPS5 hunk (level 0→2, `loop_stage: harden`,
`file_scope` extended) **and, underneath it, ~545 lines of an uncommitted `records_rehomed:
[evidence]` refactor** left by a tick that stopped ~02:58–03:27 without committing — together
with modified `tools/simplifications_store.py` and untracked
`tests/design/test_atom_records_store.py`. This looks like the in-flight repair behind
`WORKER_FINDING_THE_MAP_RATCHET_REPAIR_DID_NOT_HOLD_2026-08-10` / `..._MAP_SIZE_RATCHET_RED_ON_HEAD_...`.

Landing the map would have swept that whole refactor — **and only half of it**: the map side
would go in without the store code and untracked test that make it coherent, which is the exact
"a landed pass had half its code uncommitted" class already filed on 2026-08-09. Under
SELF_INTERRUPT_DISCIPLINE that is queued, not fixed on sight.

**So:** the OPS5 map hunk sits in the working tree with that residue. The ledger holds the L2
record and the guard is live at HEAD, so nothing is lost — but **whoever draws the rehoming
residue must land the map with the OPS5 hunk in it** (or the atom reads L0/`build` at HEAD and
can be re-drawn). Recommendation: disposition the rehoming residue as its own draw — adopt it,
do not rebuild it — and carry the OPS5 hunk through with it.

## Evidence

* `tests/tools/test_interim_bypass_retirement.py` — 7 passed; 7/7 mutations killed.
* Level-sensitive + affected suites together: **123 passed**
  (`test_gate_authorization`, `test_level_promotion_gate`, `test_generate_proof_coupled_gaps`,
  `test_coupled_triad_gate`, `test_maturity_map_facets`, `test_pre_commit_test_gate` (26),
  `test_surgical_land`, and the new guard).
* `python3 -m tools.surgical_land --help` → rc 0, live.
