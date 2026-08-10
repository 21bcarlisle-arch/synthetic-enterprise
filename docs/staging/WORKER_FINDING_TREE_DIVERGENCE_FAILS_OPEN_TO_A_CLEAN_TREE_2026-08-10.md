# [WORKER-FINDING] The tree-divergence measure fails OPEN to "clean", and the artefact at HEAD proves it fired that way (2026-08-10)

**Class:** R15 FAIL-OPEN. **Subject:** `background/tree_divergence.py::changed_paths`.
**Why it matters:** this module is the *entire* accountability half of
`DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09`. The ruling removed the punishment (the gate
stopped reading the working tree) on the express condition that *"squatting gets named daily"*.
If the naming half can silently report a clean tree, the ruling's cost side is inert and nothing
in the machine observes uncommitted work at all.

## The defect

```python
def changed_paths(project_dir: Path | None = None) -> list[str]:
    out = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], ...)
    if out.returncode != 0:
        return []          # <-- "git could not answer" is returned as "nothing diverges"
```

`measure()` then reports `total_files: 0`, `breaches()` returns `[]`, and
`process_run_complete.py::_publish_tree_divergence` notifies nothing. A git read that *failed* is
indistinguishable, at every downstream reader, from a genuinely clean tree — the textbook
fail-open shape (R15: *"passes on missing/zero/empty/malformed"*), and here the failure mode is
not hypothetical: `git status` on this repo contends with a shared index and a live tree lock
several times an hour (see `feedback_stale_index_lock_wedges_git`,
`feedback_shared_index_blocks_merge`).

## Evidence

**observed-with-evidence** — the persisted artefact written by the publish path,
`docs/observability/tree_divergence.json`, at `measured_at 1786333430` (2026-08-10 03:43:50 UTC):

```json
{"attributed_files": 0, "by_lane": {}, "oldest_age_hours": 0.0, "oldest_path": null,
 "total_files": 0, "unattributed_files": 0}
```

**observed-with-evidence** — the same `measure()` re-run by hand against the same tree six
minutes later (03:50:01 UTC), unchanged code, unchanged repo:

```
total_files: 346, attributed 17, unattributed 329, oldest 14.85h
by_lane: unattributed:docs=321, H_harness=17, unattributed:tests=5, unattributed:tools=3
breaches: ['346 source files diverge from HEAD (threshold 15)',
           'the oldest has sat 14.85h (threshold 4.0h): docs/staging/run_complete_20260809T125051Z.md']
```

**observed-with-evidence** — the fail-open reproduced directly, by giving `changed_paths` a
directory where `git status` returns non-zero:

```
changed_paths on git-error: []
total_files: 0 | breaches: []
```

**inferred (but it is the only route to the observed value)** — the 03:43:50 artefact cannot be a
correct measurement. Its `oldest_path` would have had to be one of the queued
`docs/staging/run_complete_*.md` markers, which have sat since 2026-08-09 12:58 local and are
neither generated-prefixed nor dot-prefixed, so a working `git status` was bound to return them.
`0` is reachable only through the `returncode != 0` branch (or through running the measure against
a tree with no `.git`, e.g. the gate's `git archive` checkout — which is the *same* branch).

## Why this one is worth its own finding rather than a note

It is the third distinct member of a class this machine has already paid for twice — a control
whose subject is the working tree, or whose unavailability reads as a pass
(`WORKER_FINDING_THE_INDEX_READS_THE_WORKING_TREE_2026-08-09`,
`WORKER_FINDING_THE_WEDGE_ALARM_IS_DISARMED_BY_RUNS_THAT_PUBLISH_NOTHING_2026-08-10`). And it is
*silently* the weakest of the three: the alarm at least prints something wrong, whereas this one
prints a clean bill of health for a tree carrying 346 divergent files, including 17 in `H_harness`
with a declared `file_scope`.

## Recommendation — proceeding on this unless redirected

Make it fail CLOSED, in the shape the rest of the module already argues for:

1. `changed_paths` returns `None` (not `[]`) when `git status` fails; `measure()` records
   `"unavailable": true` and omits the counts rather than reporting zeroes.
2. `breaches()` treats `unavailable` as its own named breach —
   *"tree divergence could not be measured (git status rc=N); this is a FAILED check, not a clean
   tree"* — so the daily naming still fires, saying the true thing.
3. R15 mutation test both ways: with the guard removed, a git-error tree reports clean and the
   guard test fires; restored, it names the unavailability. `breaches()` is already documented as
   PURE and mutation-testable, so the test has somewhere honest to live.

This never punishes and never blocks — `_publish_tree_divergence` still returns `None`, so the
publish path cannot branch on it, exactly as the ruling requires.

**Not fixed on sight** (SELF_INTERRUPT_DISCIPLINE): filed as an atom-shaped finding while the
rung-1 publish wedge holds priority zero.

— Worker tick, 2026-08-10.
