# WORKER FINDING — the class checker has no automated caller

**Severity:** LATENT · **Lane:** H_harness

**Discharged:** `tests/tools/test_pre_commit_gate_class_checker.py::test_staging_only_commit_still_runs_the_checker`, `tests/tools/test_pre_commit_gate_class_checker.py::test_broken_consolidation_refuses_the_commit`, `tests/tools/test_pre_commit_gate_class_checker.py::test_unimportable_checker_fails_closed`, `tests/tools/test_pre_commit_gate_class_checker.py::test_checker_imports_from_a_foreign_cwd`, `tools/pre_commit_test_gate.py` — the checker now has an automated caller in the pre-commit gate, scoped to commits touching the staging room and running BEFORE the pure-docs early return; moving it after that return (the obvious wiring, which would miss every staging-only commit) fires the first node by name. The three decisions this finding said a repair had to make are each proven: WHERE (node 1), WHAT A FAILURE DOES (node 2 — rc 1, reason on stderr), FAIL-CLOSED ON UNAVAILABILITY (node 3 — R15's third killer pattern, injected both ways). Node 4 is the regression the gate caught on itself: the first draft imported without putting the repo root on sys.path, so under the hook's own script invocation the fail-closed branch fired environmentally and refused every staging commit.

**Date:** 2026-08-12 · **Found by:** the rung-1c draw that added rule 6 to `check()`
(`WORKER_REPORT_A_CONSOLIDATIONS_SEVERITY_IS_WRITTEN_ONCE_AND_NEVER_RE_READ_2026-08-12.md`)

## Observed

`background/finding_classes.py::check` enforces six rules over the five class documents: at most one
class per finding, no unconsolidated instance, no resurrection, printed count equals list length, no
document in two rooms, and (new) the printed severity still equals the derived one.

**Nothing runs it.** Searched for callers:

- no Python consumer outside `tests/background/test_finding_classes.py`
- no reference in `tools/pre_commit_test_gate.py`
- no `.sh`, `.yaml`, `.yml`, `.toml`, `.cfg` reference outside `docs/`
- no scheduling entry

It runs when an agent types `python3 -m background.finding_classes --check`. Every class document tells
the reader to do so — "Membership is DERIVED, never hand-kept: `--check` re-derives it from the
filesystem and fails if…" — which reads like a standing guarantee and is in fact an invitation.

## Why it matters

The six rules guard the states that rot *between* draws: a sixteenth instance filed against a class
nobody re-rendered, an archived finding resurrected into the root by the shared tree, a class document
still printing `BLOCKING` after its last blocking member was discharged. Those are exactly the states no
agent is looking at when they occur — which is what a scheduled control is for.

Its own subject matter is a live one: `_blocking_lane_draw` freezes a lane off these documents' headers,
and `check()` is the only thing that can say a header has gone unbacked.

This is the shape `CLASS_NO_CALLER_AND_NEVER_RUNS_2026-08-12` catalogues, applied to the checker that
polices the class documents themselves.

## Severity: LATENT, not BLOCKING

The *release* path does not depend on it — a discharge propagates through `--render`; `check()` is the
net that catches a forgotten re-render. The live tree currently passes all six rules. So this is an
unrun safety net, not an active misreport.

## What a repair has to decide (not decided here)

1. **Where.** The pre-commit gate, scoped to commits touching `docs/staging/**` — cheap, and fires on
   the write that would cause the rot. Or `supervisor._blocking_lane_draw`, which is where the stale
   header is *consumed*; more correct, but it changes what can freeze a lane and costs a filesystem
   walk on every cycle.
2. **What a failure does.** Refusing a commit and freezing a lane are very different releases, and
   R11 requires the release to have a tested effect either way.
3. **Fail-closed on its own unavailability** (R15's third killer pattern) — a checker that is skipped
   because its module did not import is a checker that passed.

Needs its own design and its own mutation proof; not a line to append to the commit that found it.
