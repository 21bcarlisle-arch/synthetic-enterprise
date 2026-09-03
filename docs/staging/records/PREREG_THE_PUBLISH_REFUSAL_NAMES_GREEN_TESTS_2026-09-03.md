**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: what the publish register names, and what actually refuses

Written **before** the measurements below were run, at HEAD `a082be80b`, 2026-09-03T01:07Z.
Filed by the delivery seat working the claim `the-publish-wedge-is-one-staged-unwired-file`.

## What is already known (measured, not predicted)

These were established before this file was written and are therefore **not** predictions:

- `docs/staging/run_complete_*.md` on the shared tree: **35**, spanning `20260902T160532Z` to
  `20260903T004653Z`. The drawn brief cited 29. The queue is **rising**, not falling.
- `docs/observability/.publish_gate_state.json` (shared tree) carries `episode_failures: 27`,
  `total_red: 5`, and four `failures[]` rows all of kind `test_regression` with reason
  `process_run_complete rc=1 on run_complete_*.md`.
- `background.publish_freshness.describe()` on the **shared** tree says
  `content publishing: live -- figures reached origin 0.7h ago`. It says
  `NO verified publish on record` in a linked worktree, because `STATE_FILE` is resolved from
  `__file__` and the state file is untracked — a per-tree reading, not a per-project one.
- `tools/orphan_ratchet.py` is **silent, rc=0, in both trees**, and for two different reasons:
  at HEAD neither `tools/artefact_rerun_diff.py` nor its baseline entry exists; in the shared
  tree **both** exist (`A  tools/artefact_rerun_diff.py`, `M  docs/design/orphan_baseline.json`
  carrying `tools.artefact_rerun_diff` at line 331). The freeze the brief asks for has already
  been written — and never committed.

## The predictions

**P1 — the register names tests that are green.** The five node ids in
`.publish_gate_state.json:blocking_tests`, all in
`tests/background/test_a_staged_document_no_longer_blocks_every_landing.py`, pass at HEAD
`a082be80b`. If they pass, the register has sent every reader to the wrong file since
2026-09-02T07:13Z (`wedge_since`).

**P2 — the live refusal is not a test.** The current `process_run_complete rc=1` on the oldest
queued `run_complete_*.md` is a **non-test** refusal: a named gate declining, not a pytest red.
The classifier files it `test_regression` because that is its default, not because it observed a
test fail.

**P3 — the orphan ratchet is not the cause.** Because the module and its baseline entry are
staged *together*, the ratchet cannot be what refuses the current publish. If the wedge were the
orphan ratchet, `tools/orphan_ratchet.py` would be non-zero in the shared tree, and it is not.

## What would refute each

- **P1 refuted** if any of the five node ids fails at HEAD in a clean run.
- **P2 refuted** if reproducing `process_run_complete` on a queued file yields a genuine pytest
  `FAILED`/`ERROR` summary line.
- **P3 refuted** if the reproduction's output carries the orphan-ratchet banner
  (`THIS COMMIT ADDS WORK THAT NOTHING RUNS`).

## Why this is registered rather than just measured

Three of the four `failures[]` rows above were filed `test_regression` by a classifier that,
by its own docstring at `background/process_run_complete.py:3269`, knows it cannot tell a
non-test gate from a test. If I measure first and write after, I cannot show that I expected the
default to be wrong rather than discovering it was.

**Graded:** see the finding filed beside this file.
