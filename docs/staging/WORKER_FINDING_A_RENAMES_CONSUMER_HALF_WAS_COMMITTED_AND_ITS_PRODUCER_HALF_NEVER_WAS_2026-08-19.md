**Severity:** BLOCKING · **Lane:** H_harness
**Discharged:** `tests/saas/test_net_after_cts_and_blindfold_arithmetic.py::TestNoModuleReadsTheDeletedCostToServeMarginLine`,
`tests/saas/test_clv_margin_basis.py`, `tests/tools/test_derived_basis_parentage_gate.py`,
`tests/saas/test_cost_to_serve.py`, `tests/saas/test_clv_model.py`, `tests/saas/test_enterprise_value.py`,
`saas/cost_to_serve.py`, `saas/clv_model.py`, `saas/enterprise_value.py`,
`simulation/run_phase4c_on_phase2b.py`, `tools/run_phase4b_on_phase2b.py` — the producer half is
committed by the commit carrying this line, which is the whole repair: the work was never
re-derived, only landed, and the repo-wide AST census closes the reader class.

# FINDING — a rename's consumer half was committed and its producer half never was, so 22 runs died on a defect that is in no commit

**Found by:** the RUNG 1d producer-starvation draw, 2026-08-19 21:00Z, sent to diagnose
`KeyError: 'net_margin_gbp'`.
**Class:** a contract change that lands in halves. Every control this repo owns reads a COMMIT;
the scheduled producer executes the WORKING TREE. A defect that lives only in the difference
between them is invisible to all of them, by construction.

## The one-line defect

`saas/cost_to_serve.py` deleted `net_margin_gbp` and split it into `contribution_margin_gbp` /
`net_of_all_costs_margin_gbp`; the consumer half of that repair was committed, the producer half
never was, and the live producer has been running the half-applied rename ever since.

## Observed, with evidence

Every claim below is `observed-with-evidence` (R9).

**22 scheduled runs died on this one KeyError, over three days** —
`grep -c "KeyError: 'net_margin_gbp'" docs/observability/sim-runner-log.md` = 22, first at
`2026-08-17 15:31 UTC`, last at `2026-08-19 20:56 UTC`, distributed:

| date (UTC) | dead runs |
|---|---|
| 2026-08-17 | 10 |
| 2026-08-18 | 10 |
| 2026-08-19 | 2 |

The current streak, from `docs/observability/.sim_producer_state.json`: `consecutive_failures: 9`,
`first_failure_ts` = 2026-08-19 20:05:05Z, `last_failure_ts` = 2026-08-19 20:56:05Z — a 51-minute
outage on top of two earlier ones of the same shape.

**The whole repair was uncommitted.** At HEAD (`2227083c8`) the old key is still everywhere:

| file | HEAD | working tree |
|---|---|---|
| `saas/cost_to_serve.py` | emits `net_margin_gbp` | emits `contribution_margin_gbp` + `net_of_all_costs_margin_gbp` |
| `saas/clv_model.py` | no `CLV_MARGIN_BASIS` at all | `CLV_MARGIN_BASIS = "net_of_all_costs_margin_gbp"` |
| `simulation/run_phase4c_on_phase2b.py:403` | reads `net_margin_gbp` | reads both new lines |
| `tools/run_phase4b_on_phase2b.py` | reads `net_margin_gbp` | reads both new lines |

**But three CONSUMERS of that repair were already committed** — this is what makes it a
half-landing rather than simply unlanded work:

* `saas/reporting/annual_report.py:858` publishes
  `enterprise_value["portfolio"]["margin_basis"]` as `enterprise_value_margin_basis`. At HEAD
  `build_enterprise_value` does not emit `margin_basis`, so the `.get()` returns `None`.
* `tools/generate_dashboard_data.py:259-264` maps that field through
  `_MARGIN_FIELD_TO_COST_BASIS`, whose only two keys are the NEW names, and falls to
  `UNKNOWN_COST_BASIS` otherwise — which `_check_derived_basis_parentage` then rejects.
* `tests/tools/test_derived_basis_parentage_gate.py` pins that behaviour. **Correction,
  2026-08-19, on re-verification:** this third bullet was wrong when written — that file was
  UNTRACKED, not committed (`git cat-file -e HEAD:...` = "exists on disk, but not in HEAD"). The
  two bullets above it are correct and are what make this a half-landing; this one was a fourth
  uncommitted file, so it joins the landable set rather than the evidence. The finding's own
  class — a claim about what is committed, made without asking a commit — reached its own text.

So HEAD is not a working fallback. **At HEAD the producer runs and the publisher's parentage gate
fails; in the tree the publisher passes and the producer crashed.** There was no tree, at any
point in those three days, in which the pipeline was whole — and the halves were split across the
commit boundary, which is exactly the line every control reads.

## Why nothing caught it

The producer is invoked as `python3 -m tools.run_annual_report` with `cwd=PROJECT_DIR`
(`background/sim_runner.py:234-238`). It therefore executes the **working tree**, while stamping
**HEAD** into its own log line and its output filename — every one of the 22 failures is recorded
against `git=<a commit that would not have failed>`. `run_output_2227083c8_*.json` names a tree
that was never run.

That is the structural blindness, and it is upstream of the three watchers the RUNG 1d docstring
already enumerates (publish-gate wedge detector, operational-layer signal, freshness clocks). Those
three miss the outage; this one misses the CAUSE. A commit-reading control cannot be made to see
it — not by widening it, because its subject is the wrong tree.

## What was done

**Second attempt, 2026-08-19 — the first one wrote this section and did not commit it.** The
paragraph below was already here, in the past tense, when the next tick drew this finding as still
BLOCKING: at that point HEAD still emitted `net_margin_gbp` from `saas/cost_to_serve.py`, still had
no margin-basis constant in `saas/clv_model.py`, and `simulation/run_phase4c_on_phase2b.py:403`
still read the deleted key. A finding whose subject is "the repair was written and never
committed" had its own repair written and never committed, and said so in the past tense — the
discharge additionally did not parse (its test node sat past a line that did not end in a comma,
so the release read no falsifier and correctly refused). Both halves are fixed by the commit that
carries this edit; the tense below is now true of that commit and of no earlier one.

The producer half is landed, with its class control. The repair was not re-derived: it was written
on 2026-08-17 and 2026-08-18, is complete, and its tests pass. The defect was that it had never
been committed. Landing it is the fix.

The class control is the one the repair's own author wrote and left uncommitted —
`test_no_module_reads_net_margin_gbp_off_a_cost_to_serve_view`, a repo-wide AST census that
resolves bindings rather than matching names, with R15 mutation tests both ways: it catches the
exact line that killed the 22 runs, catches the `.get()` and renamed-local spellings a grep would
miss, and does NOT fire on the ledger headline or on settlement records, which legitimately still
carry `net_margin_gbp`. That census is what closes the reader class (R10) — landing it is the point
of this pass as much as landing the fix.

`simulation/run_phase4c_on_phase2b.py` carried a second lane (EP6 pass 12,
`include_schema_version=True` on two seam calls). It was landed by worktree swap with only the
margin hunk, per the standing two-lane rule; the EP6 hunks were restored to the tree untouched and
remain that lane's to land.

## What remains — successor finding, NOT closed here

**The producer stamps a commit whose tree it did not execute.** The fix is one line in
`background/sim_runner.py::_git_head` — mark the stamp dirty when the executed tree differs from
HEAD, so the log and the output filename stop making a provenance claim that is false whenever a
lane is mid-flight. It is deliberately not taken in this pass: `sim_runner.py` currently carries
another lane's uncommitted RUNG 1d work (the very mechanism that drew this finding), and adding a
hunk to it would repeat, in the file that mechanises producer health, the exact defect this finding
is about. Filed rather than fixed, and named here so the omission is not silent.

Note this defect is a REPEAT: the `sim_runner.py` RUNG 1d docstring records nine consecutive
failures on 2026-08-17 "on one KeyError", which is this same KeyError. The mechanism built in
response measured the outage correctly and drew the work correctly — and the outage recurred twice
more anyway, because what was missing was never a detector. It was a commit.
