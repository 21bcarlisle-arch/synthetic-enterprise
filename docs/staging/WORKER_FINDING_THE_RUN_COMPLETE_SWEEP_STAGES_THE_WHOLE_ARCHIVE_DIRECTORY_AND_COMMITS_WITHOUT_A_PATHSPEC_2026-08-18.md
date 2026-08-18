# WORKER FINDING — the publish sweep stages the WHOLE archive directory and commits with no pathspec, so it lands other lanes' findings and none of their repairs

**Severity:** BLOCKING · **Lane:** H_harness

**Found:** 2026-08-18, worker tick, while building the class fix owed by
`WORKER_FINDING_THE_DISCHARGE_RELEASE_READS_THE_NODE_FROM_THE_WORKING_TREE_AND_ITS_CONTROL_READS_ONLY_THE_FILE_2026-08-18.md`
§6(C). That finding put this as a QUESTION ("should `process_run_complete.py` commit
`docs/staging/**` at all?"). This document answers it with the mechanism, which is sharper than the
question assumed: the sweep does not merely happen to carry staging paths, it stages the archive
directory by name and then commits the entire index.
**Measured at:** HEAD `96c665098`, working tree of 2026-08-18. §1 is `observed-with-evidence` (R9);
§3 is labelled where inferred.
**Class:** `archiving is done by a process that cannot know whether the work landed`.

## 1. The two lines, and what they do together

`background/process_run_complete.py`, in the publish path:

```
3312    if DONE_DIR.exists():
3313        files.append(str(DONE_DIR))          # `git add docs/staging/done` — the WHOLE directory
...
3352        subprocess.run(["git", "add"] + files, ...)
3378        result = subprocess.run(["git", "commit", "-m", msg], ...)   # NO pathspec
```

Two independent reasons the same commit takes work it knows nothing about:

* **the add is a DIRECTORY.** It exists so the run's own `run_complete_*.md` markers land, but
  `git add` on a directory stages every file under it — including a finding document a worker moved
  into `done/` moments earlier and has not committed.
* **the commit has NO pathspec.** `git commit -m msg` commits the INDEX. Anything any other writer
  had already staged goes with it. The same module knows the correct shape and uses it elsewhere
  (line 3816: `["git", "commit", "-m", msg, "--"] + list(paths)`), and this project's standing rule
  is "commit specific paths, not a broad add".

The `tree_lock()` around the add/commit pair carries a comment saying it prevents exactly this
sweep. It does not, and the gap is structural rather than a bug in the lock: the lock closes the
window between THIS writer's add and commit, while the paths at risk were staged BEFORE the lock was
ever acquired. A comment that names a protection the code does not provide is why nobody looked
again for three weeks.

## 2. What it did, measured

`git show --stat 96c665098` — *"Auto-process run complete: report + LATEST.md + site/"* — carries:

```
docs/staging/done/WORKER_FINDING_..._FLOOR_SITS_ABOVE_WHERE_IT_BREAKS_2026-08-18.md      43 ++
docs/staging/done/WORKER_FINDING_..._TEN_OF_NINETEEN_SHARED_FIELDS_2026-08-18.md         84 ++
docs/staging/done/run_complete_2026081*.md                                             4 files
```

and **no** `tools/couple_w2_11_d5.py` — the module both of the first two documents certify. Two
findings, two lanes, one publish commit, neither repair in it. Both were BLOCKING; both are now in
`done/`, where no scanner re-surfaces them. The repairs are still uncommitted in this working tree
(`git status` shows `tools/couple_w2_11_d5.py`, `tests/tools/test_couple_w2_11_d5.py` modified), and
the only reason they are known at all is that another tick happened to be reading the same files.

**Why this is worse than an untidy commit.** Archiving to `done/` is not a filing act, it is the step
that ENDS a record's drawability — the staging scanners read the root, not `done/`. So the sweep
performs the one irreversible bookkeeping move in this system, on documents it did not author, with
no ability to check the thing that move asserts.

## 3. Disposition and what is owed

* **Not repaired in this tick, deliberately.** The tick that found it was drawn on a different
  BLOCKING finding in the same lane and landed that one; fixing this on sight is the treadmill
  SELF_INTERRUPT_DISCIPLINE names. It is registered here so it is drawable, which is precisely what
  the defect denies its own victims.
* **(A) The pathspec.** `git commit -m msg -- <files>` on the publish path, using the list the
  function already built. Reversible, mechanical, and the same module already does it 400 lines
  later. *Inferred:* this alone removes the swept-index half.
* **(B) The directory add.** Stage the run's OWN markers by name rather than `DONE_DIR` wholesale.
  The marker paths are known to the caller; the directory is a convenience that costs correctness.
* **(C) The cheap variant the parent finding proposed, worth having as well as (A)/(B) because it
  closes the class rather than this caller:** refuse to move a document INTO `done/` when the
  document's own `**Discharged:**` nodes are absent from the tree being committed. As of this tick
  that check exists and is one call —
  `background.finding_severity.parse_discharge(text).released` now reads the INDEX, so "is the work
  this document claims actually in the commit" is answerable by the archiver.
* **(D) The orphans.** `done/WORKER_FINDING_THE_BELIEF_AXIS_NULL_CONTROL_CANNOT_FAIL...` and
  `done/WORKER_FINDING_THE_DOOR_LEDGER_TRIPWIRE_COMPARED_TEN_OF_NINETEEN_SHARED_FIELDS...` are
  archived with their repairs unlanded. Their 15 dangling citations are declared in
  `tests/architecture/test_no_committed_discharge_cites_an_unlanded_falsifier.py::_KNOWN_UNLANDED`
  as of this tick, so the debt is at least visible and the ratchet refuses to let it rot. Whoever
  lands `tools/couple_w2_11_d5.py` must delete those entries — the stale-entry test makes that
  compulsory, not optional.
* **(E) A record gap inherited from the same orphan, carried forward so it is not lost with the
  archived page.** The uncommitted D30 repair in the working tree moves that atom's declared band
  (`above_edge_range` `(-328, -308)` → `(-333, -308)`) and its axis floor (`n_customers` 24 → 17)
  without writing D30's store record. *Inferred:* that belongs on D30's next draw.
