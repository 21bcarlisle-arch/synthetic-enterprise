# [WORKER-REPORT] KNIFE3 step 12 — the world's churn ceiling was the company's belief about it (2026-08-10)

**Severity:** RECORDED · **Lane:** W4_the_wall

Commit `d6ee063ea`, pushed to `origin/main`. Atom `KNIFE3_wall_crossing_paydown`, **level
deliberately still 0** — run_phase2b, run_phase4c_on_phase2b's remaining 10, B2's four
`customer_events` edges and B4's `dd_collection_book` residual all stand.

## The atom's FIRST STEP was already landed — verified, not assumed

The draw's own instruction is *"FIRST STEP, BEFORE ANY CUT: lift `build_edges` /
`company_reads_sim` / `sim_reads_company` out of the ratchet TEST module into a shared module."*
That landed 2026-08-09: `tools/epistemic_wall.py` holds the definition, the ratchet, the KNIFE
ledger and `tools/epistemic_verifier.py` all import it, and
`tests/architecture/test_epistemic_wall_single_source.py` guards against a second copy. Checked
before cutting, per the atom's own warning about moving the net while planning the cuts.

## THE EXIT CLAUSE, stated on the draw as the atom requires

Against the count that **survives passes 1 and 2**, not the stale 107:

> **50 live crossings survived into pass 3** (48 direct + 2 indirect via a bridge package), **0 of
> them in the strictly-forbidden company-reads-sim direction** — measured at HEAD and in the
> working tree and identical in both. **EXIT** = every one of the 50 carries a disposition of
> `cut`, or a design block naming why it stands, with the walker — never the claim — as arbiter,
> and `tools.wall_crossing_dispositions` reporting OK in BOTH modes.

The exit is **not a target count**. R12 governs: the crossing count is a diagnostic, and nothing
here may be promoted or shortened to move it.

## The cut: 50 → 49 live (48 → 47 direct)

`simulation.satisfaction_churn -> saas.churn_model`. The world clamped its own GROUND-TRUTH churn
probability at the company's `MAX_CHURN_PROBABILITY`, so the company's belief about the ceiling
**was** the ceiling. The world's ceiling now lives at `simulation/churn_ceiling.py`; the company
keeps its estimate. Both are 0.95, so every clamp returns the identical float and **no number
moves** — measured, not asserted.

**THE FINDING IS THE FILING, NOT THE FIX,** and it is the part worth reading. This edge sat under
`B2_company_brain_decides_the_world`, the design that says of itself *"this is a coupled-triad
build, not a mechanical move, and it must not be attempted as one."* It is not that design's
shape. B2's other four edges hand the company's **reasoning** the job of deciding who churns; this
one handed it a **number** — cuttable in an afternoon. B3's own executed block had already written
the sentence that describes it (*"a belief constituting the fact it is a belief about"*) about a
different edge, without anyone noticing it fitted a second live one. **A design block is a ruling
about a CLASS, so a misfiled member is a defect of the same kind as a miscounted edge — and
nothing in the tooling looks for one.** Recorded as register §3g. B2 is now 4 edges and no easier.

The world had **three** copies of this ceiling, one of them the company's: the borrowed constant, a
private `_MAX_CHURN_PROBABILITY` in `switching_propensity`, and a bare `0.95` literal in
`customer_events`. One home now; the other two are aliases. **Only the first is an edge** — the
other two are housekeeping counted as zero.

**R15, both mutations RUN on the real tree, not named.** (1) the deleted import re-injected as a
same-name alias reds the two named controls plus four independent reds in the wall ratchet
including the frozen census (6 failed / 12 passed, reverted); (2) **the vacuity guard, the one with
teeth** — (1) would pass identically against a company constant nothing reads — mutating
`MAX_CHURN_PROBABILITY` to a literal `1.0` inside `churn_probability` reds exactly
`test_the_same_mutation_does_move_the_companys_own_answer` and nothing else (1 failed / 5 passed,
reverted). No test pins the two constants equal: that would restore in the suite the coupling the
cut removes from the code (B3's and B7's recorded refusal, third application).

## TWO STANDING FINDINGS ARE CLOSED BY THIS COMMIT — archived with HEAD evidence

**`WORKER_FINDING_THE_EPISTEMIC_WALL_IS_BREACHED_AT_HEAD_2026-08-09` — CLOSED, and it was closed
before this tick started.** Re-measured on a clean `git archive HEAD` checkout at the top of this
tick: `company_reads_sim` = **0** at HEAD and in the working tree, identical. The
`saas.reporting.annual_report -> simulation.run_phase4c_on_phase2b` import the finding names is
gone from every commit. Filed here rather than silently, because the finding's own point was that
*nobody knew* — so its closure has to be measured on the shipping tree too, not inferred.

**What that finding asked for structurally is now built.** Its cause was that the wall was
enforced only AFTER the commit. `tests/architecture/test_epistemic_wall_ratchet.py` was not in
`tools/pre_commit_test_gate.py`'s always-run `CONTROL_TESTS`: per-file selection ran it when the
RATCHET was edited (the case needing it least) and stayed silent when a sim module landed a fresh
`saas.*` import (the only case it exists for). Added — same R10 class the three neighbouring
entries were each added for, applied to the one control CLAUDE.md classes as a **WALL** rather than
a dial. Cost stated rather than glossed: **~4.8s on every code commit**, by far the most expensive
entry in that list, because it is an AST walk of four packages.

**`WORKER_FINDING_THE_RUFF_RATCHET_IS_RED_AT_HEAD_2026-08-10` — CLOSED.** Fixed at source, never
by raising the baseline. The finding measured I001 at 1386 vs a baseline of 1384; by the time of
this tick HEAD carried 1385 (one having been repaired elsewhere). Sorting the import block this
cut already touched (`simulation/customer_events.py`) takes it to **1384 = baseline exactly**.
Verified on a clean HEAD checkout of `d6ee063ea`, not the working tree:

```
$ git archive HEAD | tar -x -C /tmp/knife3_head2 && cd /tmp/knife3_head2
$ ruff check --statistics | grep -E 'I001|F841'
1384    I001    unsorted-imports
 130    F841    unused-variable
$ python3 -m pytest tests/architecture/test_static_quality_ratchet.py -q
13 passed
```

## ONE THING LEFT DIRTY, and it is not mine

`F841` reads **131** in the WORKING TREE against a baseline of 130. Located rather than assumed —
a per-file diff of tree against HEAD names exactly one source: **`tools/scale_probe_10k.py`**,
another lane's uncommitted file (the AO12 10k probe). It is not in this commit, HEAD is clean at
130, and it will red the static-quality ratchet for whoever commits that file. Left for its owner
per SELF_INTERRUPT_DISCIPLINE; flagged here so it is not rediscovered as a mystery.

## Measured, both trees

```
tools.wall_crossing_dispositions: 49 live crossings (47 direct, 2 indirect); 91 ruled
                                  (cut 42, owed 49, grandfathered 0); 3 cut designs -- OK
tools/knife_hotspot_measure.py:   wall_crossings  4 files  49 edges -- KNIFE LEDGER OK
tools.epistemic_verifier:         PASS, 541 company/+saas/ files, no barrier violations
clean HEAD checkout of d6ee063ea: 47 direct crossings; the cut edge absent
suites:  tests/architecture/ + wall_crossing_dispositions + knife_hotspot_measure
         + the three churn suites + test_pre_commit_test_gate = 250 passed
         (the 2 static-quality reds in that run were the pre-existing HEAD I001,
          now fixed, and the foreign F841 above)
```
