# [WORKER-FINDING] The static-quality ratchet is red on committed main, not on working-tree dirt

**Found:** 2026-08-09, during the AO5 KNIFE draw (incidental — not this atom's scope).
**Disposition:** QUEUED per SELF_INTERRUPT_DISCIPLINE. Not fixed on sight; the machine is not blocked.
**Rank:** backlog unless someone is wedged by it.

## Observed, with evidence

`tests/architecture/test_static_quality_ratchet.py` fails two tests:

```
F401: baseline 279, now 280
F811: baseline  95, now  96
I001: baseline 1388, now 1389
```

**The drift is entirely in committed code.** Verified against a clean export rather than inferred:

```
$ git archive HEAD | tar -x -C /tmp/headtree && cd /tmp/headtree
$ ruff check --select F401,F811,I001 .
HEAD census: {'F401': 280, 'I001': 1389, 'F811': 96}
```

Ruled out, each by direct check rather than by assumption:

- **Not this tick's files.** `tools/knife_hotspot_measure.py` and
  `tests/tools/test_knife_hotspot_measure.py` are clean on all three rules; removing them and
  re-running left the suite red.
- **Not the other uncommitted work in the shared tree.** Every untracked `.py`
  (`tests/system/scale_constraints.py`, `test_scale_constraints.py`,
  `test_scale_constraint_mutation.py` — the AO4 build, still untracked) scores zero on all three
  rules, and no tracked-modified file's count differs from its HEAD version.

This matters because the known wedge class here is the opposite one — *"the gate lints the WORKING
TREE, so one uncommitted lint error wedges publishing for everyone"*. This is not that. Reaching
for the usual remedy (find whose dirt it is) would have found nothing, which is why the
attribution is written down.

## Not currently blocking

The pre-commit test-gate selects an impacted subset (14 test files for this commit) and did not
include the architecture tier, so commits are landing. The failure surfaces to anyone running
`pytest tests/architecture/` or a full suite.

## What closing it needs

The baseline was frozen 2026-08-06 and the drift arrived in the bulk `.py` commits since. Three
violations, one per rule. **Fix the three, do not raise the baseline** — the test says so itself,
and a raised baseline is the ratchet optimising itself.

One attribution caveat, so the next reader does not chase it: the same census reports
`invalid-syntax` for `company/trading/emir_reporting_register.py`. That is a **ruff-version
artefact, not a defect** — `ast.parse` accepts the file. Checked, so nobody re-checks it.

## Also observed, separately worth a look

`tests/system/scale_constraints.py` and its two test files are **untracked** while
`AO4_scale_constraints_executable` sits at L2 in the map. That is the orphaned-green-work-in-tree
class (`WORKER_FINDING_ORPHANED_GREEN_WORK_IN_TREE_2026-08-08.md`), recurring. Not verified beyond
the `git status` line above — stated as `observed`, with no claim about how it got there.
