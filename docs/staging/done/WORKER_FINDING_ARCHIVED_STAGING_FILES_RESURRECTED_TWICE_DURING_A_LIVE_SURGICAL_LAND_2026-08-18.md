# WORKER FINDING — 22 just-archived staging docs came back to the root, twice, byte-identical, while an unrelated publish pipeline was mid-run

**Severity:** LATENT · **Lane:** H_harness

## What happened, observed-with-evidence

This tick archived 23 discharged (`RECORDED`) `WORKER_FINDING_*` docs from `docs/staging/` to
`docs/staging/done/` via `git mv` under `tree_lock`, landed with `tools/surgical_land.py`
(commit `3e7565971`, pushed, `--verify` receipt-consistent). Immediately after landing, 22 of
the 23 root copies (all but one that had been untracked) reappeared in `docs/staging/` as
**untracked, byte-identical** copies of the files just archived. Removed again under
`tree_lock`; `python3 -m background.finding_classes --check` went from PASS -> 22 "TWO ROOMS"
failures -> PASS again once removed a second time. The resurrection recurred exactly once
after the fix, not a steady drip — consistent with one concurrent process doing it once, not
an ongoing loop.

Timing: the reappeared files' mtimes clustered at 18:27:53, within the same minute
`tools/surgical_land.py` ran. Throughout this whole window (17:49 onward) one heavy git-using
process was live: `background/process_run_complete.py`, running a publish gate for
`run_complete_20260818T164457Z.md` (a `pytest` subprocess, ~4 CPU-minutes, still running at
observation time).

## What was ruled out, not assumed

- **`tools/surgical_land.py`'s own "refresh real index" step** (`_refresh_index_for`) only
  runs `git update-index --index-info` — it touches the INDEX, never the working tree, and
  the resurrected files were untracked (`??`), i.e. present on disk but absent from the
  index. This step cannot be the mechanism.
- **`background/staging_watcher.py`'s remote-staging bridge** (`_extract_advisor_staging_files`)
  explicitly skips any name already present in `done/` or `in_progress/` before writing it —
  read directly, this guard is real and would refuse exactly this resurrection. Also this
  bridge only fires for `[ADVISOR-STAGED]` commits, and these 23 files were never advisor-staged.

## What was not established (R9 — not claimed)

The actual writer was not identified. `process_run_complete.py` is the strongest correlated
candidate (only heavy git-touching process alive for the whole window) but this is
**inferred from timing correlation, not observed at the write** — its source was not read for
a checkout/reset step that would explain writing pre-archival file content back to disk.
Whether this is a one-off artefact of a long-running publish holding an old working-tree
snapshot, or a reproducible class, is unknown; it fired once and did not recur on a second
check.

## Why this is LATENT not BLOCKING

No damage: the resurrected copies were content-identical to the archived versions (verified
byte-for-byte before both removals), never diverged, and the actual commit/push is correct
and verified. `finding_classes --check`'s "TWO ROOMS" rule caught the inconsistency
immediately and by mechanism, not by luck — the control worked as designed. Nothing published
was wrong at any point.

## What would close it (none built; QUEUED, not fixed on sight — SELF_INTERRUPT_DISCIPLINE)

Identify the actual writer (read `process_run_complete.py`'s git-touching code paths for
anything that checks out or resets `docs/staging/` from an old ref while it holds the tree
lock for its own gate run) and either (a) scope it away from `docs/staging/`, or (b) if it is
an inherent property of a long-held checkout racing an archive, make `finding_classes --check`
part of the routine post-archive step rather than something a worker tick has to think to
re-run.

## Not claimed (R9)

- No claim this is the same mechanism as
  `WORKER_FINDING_A_PATHSPEC_PROTECTS_OTHER_LANES_FROM_MY_INDEX_BUT_NOT_FROM_MY_STALE_COPY_2026-08-18`
  (that finding is about a stale WORKING COPY silently reverting a committed line via a
  pathspec commit; this is about deleted, untracked files reappearing on disk with no commit
  involved). Related family (`uncommitted_and_orphaned_work` / shared-tree timing), distinct
  shape.
- No claim about whether this has happened before and gone unnoticed — not audited.
