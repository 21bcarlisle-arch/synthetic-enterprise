# FINDING — a finished cut sat uncommitted on the shared tree, and every control was green

**Severity:** LATENT · **Lane:** H_harness

**Date:** 2026-08-12 · **Atom:** `KNIFE3_wall_crossing_paydown` · **Class:** record/code divergence
**Status:** instance repaired and landed (`f3de95f94`, `55a841d12`); the CLASS is filed here, not fixed on sight.

## Observed, with evidence

This tick drew `KNIFE3_wall_crossing_paydown` and found step 19 — the counterparty
collateral desk cut — **already built and not committed**:

```
?? company/interfaces/counterparty_collateral.py
?? company/risk/counterparty_collateral_desk.py
?? tests/company/interfaces/test_counterparty_collateral_seam.py
 M simulation/run_phase2b.py
 M tests/architecture/test_epistemic_wall_ratchet.py
 M docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md
```

All six mtimes 2026-08-12 00:25–00:30. The work was complete: 14 seam tests, 5 of them
mutations; the ratchet allowlist already had its three `LEGACY_SIM_READS_COMPANY` tuples
deleted; register §3n already written. Run on the working tree it was green —
92 passed across the four wall/architecture suites, `wall_crossing_dispositions` rc 0.

## Why nothing caught it

**The three artefacts agreed with each other.** The register said `cut`, the ratchet
allowlist no longer named the edges, and the code no longer made the imports — so every
control that compares one of these to another was satisfied. `wall_crossing_dispositions.py`
measures **the working tree** and printed `OK`. There was no red anywhere, on any machine,
for anyone to see.

That is the distinguishing feature: this is not a control that failed open, it is a
**complete and internally consistent change set that simply never became a commit**. The
controls were doing exactly their job on exactly the tree in front of them.

## Why it matters more than a lost afternoon

On this tree there are concurrent writers (`process_run_complete.py`, the interactive
session, `autonomous_runner.py` turns). An orphaned change set of this size is one broad
`git add` away from landing under another lane's commit message — a five-file cut, its
ratchet allowlist and its register section attributed to a publish commit. It is also one
worktree prune away from being gone. Related, already recorded:
`feedback_forks_die_dirty_audit_before_prune`,
`feedback_a_concurrent_sweeper_can_commit_one_half_of_a_two_file_atomic_write`,
`feedback_untracked_build_passes_local_green`.

## The second half of the same finding

The atom's own record (`docs/design/simplifications/KNIFE3_wall_crossing_paydown.yaml`)
still read **STEP 17 / "36 of 91 live"**. Step 18 (`9ef7d5d6e`, flexibility revenue,
register §3m, 36 → 34) had landed its code and its register section and **not** updated the
record either. So the record was two steps behind the tree, in the direction that
*understates* progress.

This is the mirror of `feedback_the_record_can_outrun_the_code`: here the **code outran the
record**. Both break the same property — a reader re-deriving the atom's progress from its
own store gets the wrong number — and the previous step already filed a version of this
(`WORKER_FINDING_AN_ATOMS_OWN_RECORD_STATES_TWO_COUNTS_FOR_ONE_TREE_2026-08-11`). That is
now **three consecutive steps** in which this atom's record was wrong about the tree, which
under R3 (two-strike redesign) means the mechanism, not the instance, is the thing to change.

## I then committed the same defect myself, which found the real mechanism

Landing the six paths above, I left behind **two more files belonging to the same step** —
`tests/company/risk/test_collateral_death_test_wiring.py` and
`test_mtm_sample_reveal_wiring.py`, mtimes 00:35/00:36, the two guards that follow the moved
code. `f3de95f94` was therefore **half a change set, and HEAD was RED**, observed:

- HEAD's `test_collateral_death_test_wiring.py` line 17 reads
  `from simulation.run_phase2b import _mc2_collateral_death_test`; HEAD's `run_phase2b.py`
  contains **zero** occurrences of that name — a collection error.
- HEAD's `test_mtm_sample_reveal_wiring.py` parses `run_phase2b.py` for the
  `for <var> in _sample_dates:` MtM loop, which moved to the desk. (The four surviving
  `_sample_dates` hits in `run_phase2b.py` are an unrelated fabric-series local, not a loop
  iterator, so `loop_found` is False and the guard's own vacuity assertion fires — it fails
  loud rather than passing on an empty set, which is the property its header claims.)

Fixed in `59fc53903`; `tests/company/risk` + the seam + the ratchet now 395 passed.

**`python3 -m tools.surgical_land` ran the pre-commit gate and returned rc 0 on that red
tree.** That is the finding, and it is measured, not inferred — `tools.pre_commit_test_gate.tests_for`:

```
company/risk/counterparty_collateral_desk.py -> []
company/interfaces/counterparty_collateral.py -> ['tests/company/interfaces/test_counterparty_collateral_seam.py']
simulation/run_phase2b.py -> ['tests/simulation/test_run_phase2b.py',
                              'tests/simulation/test_run_phase2b_event_log.py',
                              'tests/simulation/test_run_phase2b_reveal_source_wiring.py']
```

The map is by **name stem**. A test is reachable only if it is *named after* its subject. Both
missing guards reach `run_phase2b.py` the other two ways a test can — one **imports a symbol
from it**, the other **AST-parses its source text** — and neither is named after it, so neither
is selectable. A brand-new 19k module maps to **no tests at all**, since nothing is named after
a file that did not exist a moment ago.

This is the same class as
`WORKER_FINDING_A_POPULATION_TEST_IS_UNREACHABLE_BY_ANY_STEM_SELECTOR_2026-08-10`, now shown to
have let a red HEAD through a gate that is the last thing standing between a working tree and
`origin/main`. A stem map cannot see the two strongest kinds of guard this project writes —
source-wiring guards and seam guards — precisely because they are deliberately filed next to
the *behaviour* they protect rather than next to the file they read.

## Recommendation — and what I did

The prose remedy ("a KNIFE step is not done at green, it is done at LANDED-AND-RECORDED")
is an exhortation, and MAKE_IT_STICK says exhortations evaporate. Two mechanisms, ranked —
the second is the one that matters, and I only found it by repeating the defect:

**1 (RECOMMENDED, and the one I will take). Close the gate's blind spot: reach tests by
REFERENCE, not by name stem.** For each changed source path, also select tests that
*mention* it — its module dotted-path in an import, or its filesystem path in a string
literal. A grep-grade reverse index over `tests/` is enough; it needs no test-name
convention and it is exactly what finds a guard that AST-parses its subject. Both missing
guards name `run_phase2b` in their source and would have been selected. This turns a gate
that returned rc 0 on a red tree into one that fails — which is the R15 property the gate
is supposed to have and, as of today, demonstrably does not.

The honest caveat: this widens the gate's subject and therefore its runtime, and a
reverse-index that is itself derived is a staleness surface. That is a smaller cost than a
gate whose rc 0 means nothing, and it is measurable — the size of the widening should be
reported when it is built, not assumed.

**2 (weaker, keep as a backstop). A tick-boundary orphan check.** At the end of a bounded
invocation, `git status --porcelain` restricted to the drawn atom's `file_scope` must be
empty or the tick names what it left behind. Cheap, reads real git state. But note it would
NOT have caught my own half-landing: the two stranded guards live under
`tests/company/risk/`, which is not in this atom's declared `file_scope` — a scope declared
in advance cannot enumerate the files a cut turns out to touch. It catches the overnight
orphan; it does not catch the partial landing. Recording that limit rather than selling the
check as a fix for both.

**Both are harness atoms** (`H_harness`, small), not work for a KNIFE step: a wall pass must
not land gate machinery in the same commit as an import move, which is B7's rule and the
reason step 17's naming residual was also left alone. Minting is itself a code change to the
map and this tick's `file_scope` is the wall pass, so I have not minted them here.
**Unless objected to, the next harness draw takes mechanism 1.**

I did the reversible parts: landed step 19 (`f3de95f94`), found and fixed my own half-landing
(`59fc53903`), and brought the atom's record up to step 19 with the divergence stated in the
record rather than quietly corrected.

## Not claimed

Nothing here identifies *why* the previous tick exited without committing — no evidence was
found either way, and per R9 that stays `inferred`-at-best and therefore unstated. The
finding is about what the controls could and could not see, which is observable.

Nor is it claimed that the gate has *never* worked: it has caught real reds, and the stem map
selects correctly whenever a test is named after its subject, which is the common case. The
claim is narrower and is the one demonstrated above — a test that reaches its subject by
import or by parsing its source is unreachable, and a newly created module is unreachable
outright.
