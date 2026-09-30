**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted` (lane-0 `re-establish-boot-sha-drift-against-origin`)

# Boot-sha drift grades each daemon against the DISK, so a checkout behind origin read as a current fleet

**2026-10-01.** The carried row asked: does `evaluate_boot_sha_drift()` grade a daemon's boot sha
against local HEAD or against origin? Settled by running it, with a divergence live (shared tree
HEAD `ebc9af681`, 1 ahead / 13 behind `origin/main`).

## What it grades against

**Neither.** `boot_sha.changed_paths_since(sha, boot_blobs)` runs `git diff --name-only <boot sha> --`,
which compares against the **working tree**, filtered by the content the daemon loaded at boot.
That is right for its question (would a restart load different code?), and it is why it is not
"stale vs HEAD". It cannot see origin at all: a commit on the trunk that is not checked out is on
no disk.

## Live output, before the change (origin/main code, run in the shared tree)

```
head: ebc9af681   population 10, graded 10, stale [], unresolved {}, vacuous False
stamper: works (12 units declare it)
```

## Live output, with the trunk leg added

```
head:  ebc9af681   trunk: ecb326104   graded 10/10   stale []
behind_trunk:
  background-worker  background/process_run_complete.py, background/resource_headroom.py
  deadmans-switch    background/process_run_complete.py, background/resource_headroom.py
  naive-organ        background/process_run_complete.py, background/resource_headroom.py
  sim-runner         background/process_run_complete.py, background/resource_headroom.py
```

So the report said 0 stale while 4 of 10 daemons were running code the trunk had already replaced.
Restarting them would change nothing; advancing the checkout would.

**A correction, recorded here.** My first hand count, `git diff HEAD origin/main` (two dots), said
five daemons and also named `delivery_lane.py` and `direction_path_check.py`. Those differences
come from the checkout's own ahead commit (`ebc9af681`). They are the ahead leg, not code anyone is
missing. The mechanism uses `HEAD...origin/main` (three dots), which gives four daemons.

## What changed

- `boot_sha.paths_behind_trunk()` and `boot_sha.trunk_sha()` return None when the ref is missing
  (the gate extract has no origin/main). None means unresolved; it never means an empty set.
- `process_reconciler.loaded_code_behind_trunk()`: for each daemon, the trunk's changed paths that
  fall inside its code closure.
- `evaluate_boot_sha_drift()` now reports **two legs**: `stale` (vs disk, unchanged) and
  `behind_trunk` (disk vs origin), plus `trunk`. Existing consumers of `stale` are unaffected.
- Controls in `tests/background/test_boot_sha_deployment.py` run over a real diverged clone (one
  ahead, one behind). Four mutations were each caught: two dots instead of three, `set()` on a
  failed diff, dropping the closure intersection, and `{}` for an unresolved leg.

## Disposition

The carried row is **corrected, not withdrawn**: the premise ("it grades against HEAD") was wrong,
but the blindness it suspected was real. Not yet done: nothing renders `behind_trunk`.
`deploy_restart --report` and `health_check` still print only the disk leg. That rendering is the
next increment, and it should go through the reconciler's advance path, not a restart.
