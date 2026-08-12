# WORKER REPORT — the gate's own control was untracked, so the gate kept falling back to the full suite

**Severity:** RECORDED · **Lane:** H_harness

**Date:** 2026-08-10 · **Lane:** RUNG 1 / PRIORITY ZERO (publish-gate wedge) · **Commit:** `ebfcc5eca`

## What was red (R9: observed-with-evidence)

The tick drew a wedge claiming "~1627 min failing, no pass at HEAD 00a042eec, 142 consecutive
failures." Two distinct causes, both **observed** in `docs/observability/sim-runner-log.md`:

1. **17:28 UTC** — `Publish gate RED -- blocking test(s): FAILED
   tests/background/test_self_clearing_alarm_census.py::test_every_live_hit_is_dispositioned`.
   Already fixed by `00a042eec`. Re-run in a clean `git archive HEAD` extract: **16 passed**.
   The named blocking test passes when you run it — the episode counter was carrying a
   corpse (`feedback_named_blocking_test_passes_when_you_run_it`).

2. **17:20 UTC** — `Publish gate scope: SUBJECT MISMATCH: 2 scoped test path(s) do not exist
   under the root this gate runs against (tests/background/test_publish_gate_blocking_payload.py,
   tests/background/test_wedge_suspects_from_the_red.py) ... Falling back to the full suite.`

Cause of (2), **observed**: both files were **untracked** (`git status --porcelain -uall`).

## Why that is the more durable defect

`publish_scope.resolve_scope()` reads the tree it is handed; the gate **runs** in a HEAD
checkout. An untracked test in the publish path therefore does two harms at once:

- **It is invisible to the gate it protects.** Both files import
  `background.process_run_complete` — a publish-path source — so they are *blocking* tests by
  the import graph. Untracked, they never ran in any gate. The H42 control was local-green only
  (`feedback_untracked_build_passes_local_green`). The mechanism had landed; only its control
  had not (`feedback_a_control_committed_without_its_mechanism_reds_head`, inverted).
- **It degrades the gate to the full suite.** The mismatch fallback is correct in direction — an
  uncomputable scope must never narrow — but the full suite is the slow path that has been
  producing the `rc=4` "no FAILED/ERROR summary line found" reds and the OOM kills
  (`feedback_truncated_pytest_is_an_oom_not_a_failure`). A missing path made a *narrow, green*
  gate present as a *wide, red* one.

## What was done

Landed exactly the two paths via `tools/surgical_land` (no bypass; the gate ran against the tree
the commit would create, **gate-rc 0**, receipt verified). Pushed: `00a042eec..ebfcc5eca`.

## Evidence at the new HEAD

Clean `git archive HEAD` extract:

- `resolve_scope` → `full_suite: False`, **131 blocking test files, ABSENT: []** — the mismatch
  fallback no longer fires.
- Both H42 tests are now *in* the gate's blocking scope.
- `test_self_clearing_alarm_census.py` + both H42 files: **47 passed**.

## Left undone, deliberately

- **The run_complete queue was not flushed by me.** A publisher (`pid 3037153`) was live on
  `run_complete_20260809T131422Z.md` with its gate mid-flight; a second publisher would contend
  the run lock, and a third concurrent suite on a 15G box is the known OOM shape
  (`reference_the_box_has_15g_ram_and_tmp_is_a_tmpfs`). The red is removed; the running
  publisher flushes the queue. **R11 on the folded live site is therefore NOT claimed here** —
  no live-surface assertion was made.
- **`tools/scale_probe_10k.py` + `tests/tools/test_scale_probe_10k.py` are still untracked**, and
  the test carries **no `scale_report_only` marker**, so landing it would put it straight into
  the blocking set. Same class as above, different risk profile — filed, not landed on a
  priority-zero tick.
- **Latent, unfixed:** `publish_scope.resolve_scope(root=...)` accepts `str` and dies with
  `TypeError: unsupported operand type(s) for /: 'str' and 'str'` at line 137. Every current
  caller passes a `Path`, so it is not live — but it is a fail-hard on a control's entry point.

## The class

An untracked file in the publish path is not merely unlanded work — it **changes the gate's
scope**, and the scope is derived from a different tree than the gate runs in. Any lane that
writes a test importing a publish-path source and does not commit it converts a narrow green
gate into a wide red one. The standing check is `git status --porcelain -uall tests/` before
declaring an unwedge diagnosis complete.
