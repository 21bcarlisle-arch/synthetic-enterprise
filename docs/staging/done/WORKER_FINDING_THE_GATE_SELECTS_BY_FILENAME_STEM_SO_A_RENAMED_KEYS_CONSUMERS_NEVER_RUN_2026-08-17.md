# WORKER FINDING — the pre-commit gate selects tests by filename STEM, so the consumers of a renamed published key never run, and one of them was red at HEAD for a day before anyone looked

**Severity:** LATENT · **Lane:** H_harness

**Found:** 2026-08-17, worker tick, while measuring the blast radius of the D44/H27-Hour-#30
land (`1135a6316`) rather than asserting it.
**Not fixed on sight** (SELF-INTERRUPT DISCIPLINE): the two INSTANCES are repaired in the same
commit that found them, because one of them was a red I had just caused. The CLASS — the gate's
selection rule — is not, and that is what this document is for.
**Rank:** backlog.

---

## The finding

`tools/pre_commit_test_gate.py` chooses which tests to run from the changed paths by NAME STEM:
a change to `background/gap_metric.py` selects `tests/**/test_gap_metric*.py`. That rule is a
good proxy for "the tests OF this module". It is not a proxy at all for "the tests that CONSUME
this module", and those are different populations the moment a module renames something it
publishes.

Measured, not inferred. The D44 lane renamed two `components` keys at their source
(`components["normalisation"]` → `normaliser` in `misapplication_gap`, →
`normalisation_absent_reason` in `ageing_gap`) so they would stop shadowing the entry-level
declared field. Two test modules assert on those keys. Neither shares a stem with
`background/gap_metric.py`:

| module | selected by the gate on a `gap_metric.py` change? | state |
| --- | --- | --- |
| `tests/test_gap_metric_misapplication_class.py` | YES (stem matches) | updated in the lane |
| `tests/test_gap_normalisation_declaration.py` | no — but named in the lane | updated in the lane |
| `tests/tools/test_d7_ageing_measures.py` | **no** | **went red at `1135a6316`** |
| `tests/tools/test_couple_w2_5_c7.py` | **no** | **already red at `983403352`** |

The second red is the one that matters, because it is not about this land at all. It was red at
HEAD *before* this tick, on the OLDER half of the same atom — the D44 requirement that every
`GapResult` declare a normalisation kind — and it stayed red without wedging anything, because
nothing selects it. `tools/couple_w2_5_c7.py` has not changed since, so the gate has had no
occasion to run the test that would have reported it.

## Why this is a control-shaped defect and not a to-do

The gate is the project's answer to "a commit is green". Its selection rule makes that claim
scoped to *stems*, while the sentence a reader takes from a green gate is scoped to *the tree*.
Those agree exactly until a module changes something OTHER MODULES read by name — which is the
case the gate is most needed for, because a renamed key is precisely the change a type checker
would not catch and a caller would not import.

R15 reading: this is FAIL-OPEN. A consumer test that is never selected cannot be red, so its
absence from the run reads identically to its passing.

## What closing it would need (R10 — the class, not these two files)

- A selection rule that can reach a consumer: at minimum, when a changed file is a module that
  other test modules IMPORT, select those importers too (an AST/import census is already the
  technique used elsewhere in this repo — `test_gap_metric_misapplication_class.py` runs a
  call-site census, so the machinery exists).
- A standing census that answers a cheaper question directly: **is any test in the repo red at
  HEAD right now?** The two reds here were both invisible to every gate the project runs, and
  the only reason either was found is that a tick measured a blast radius by hand. A periodic
  full-suite run against HEAD, whose output is a NUMBER rather than a gate, would have caught
  the `couple_w2_5_c7` red a day earlier without blocking anybody.
- R15 both ways on whichever is built: it must go red on a renamed key whose consumer is not a
  stem match, and it must NOT go red on an ordinary same-stem change.

## Reachability — observed, not inferred

Both reds were reproduced by bisecting against real commits: `tests/tools/test_d7_ageing_measures.py`
passes at `983403352` and fails at `1135a6316`; `tests/tools/test_couple_w2_5_c7.py` fails at
both. Both are repaired in the commit that files this document, so the instances are closed and
the population this finding is about is the selection rule.

## Provenance

Found while discharging closure condition 3 of
`docs/staging/done/WORKER_FINDING_A_NAN_GAP_DEFEATS_THE_UNDEFINED_READING_GUARD_2026-08-17.md`
(BLOCKING, lane H_harness, rung 1c) — the blast-radius measurement that document's own class
demands, which is what turned up the reds that no gate had.
