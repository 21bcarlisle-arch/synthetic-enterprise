**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# FINDING: the battery's fingerprint closes the two-spec collision and leaves the two-tree, one-spec collision wide open

**Found 2026-09-06 03:20 BST, delivery seat, worktree `/var/tmp/se-seat-executor` at `e20d5a2dc`,
claim id `fuel-mix-return-annotation-and-battery-anchor`. Subject:
`tools/contract_battery.py`. Not measured by running it — established by reading the engine, and
by the near-miss described at the end, which is what put me on it.**

---

## The near-miss, first, because it is the reason this is filed

I was drawn on an item whose third deliverable was "re-run the battery so the results file matches
the new spec fingerprint". A re-run was **already in flight** — PID 1448564, launched 03:06:22 from
the shared tree. I was one command away from starting a second run of the **same spec** to complete
the tenth column. Had I done so, the two runs would have shared one results file, silently, with no
refusal from anything.

I found this only because I checked `ps` before acting. **Nothing in the instrument would have told
me**, and the resulting file would have carried rows from two trees under one fingerprint.

## The defect

`fingerprint()` exists because two *different* specs for one subject once collided on a
name-derived path and published `SURVIVED ALL 3 CALLER SUITES: M1..M8` for mutations that were
never applied. Its own docstring says the fix means "two specs for one subject cannot collide by
default at all". That is true, and it is not the whole space.

**Two runs of the SAME spec produce the SAME fingerprint and therefore the SAME default path** —
`/var/tmp/{spec.name}_battery_{fp}.json`, a global path with nothing tree-scoped in it. The
fingerprint check at `contract_battery.py:447` refuses a *different* stored fingerprint; two
identical ones sail through, because matching is exactly what it is looking for.

Four verified properties combine:

1. **The results path is global, not per-tree.** `--out` defaults to `/var/tmp/...`. Several
   worktrees (`/home/rich/synthetic-enterprise`, `/var/tmp/se-seat-executor`,
   `/var/tmp/se-direction-battery`, …) share one `/var/tmp`.
2. **Read once, write whole.** `results` is loaded a single time at line 446, then written back
   entire from the in-memory dict at **thirteen** sites. Whichever run writes last wins; every row
   the other wrote after that read is gone.
3. **No lock of any kind.** No `flock`, no `fcntl`, no `O_EXCL`, no pid file — verified by grep
   over the whole module.
4. **Resume adopts rows across trees.** `todo = [s for s in suites if s not in row["per_suite"]]`
   means a run that finds a suite already recorded **skips it and keeps the other run's cell**.

## Why the fingerprint cannot close this, and it is not a bug in the fingerprint

`fingerprint()` hashes the subject's **path**, the suite **paths**, the mutation text, the poison
and the null strings. It does **not** hash the subject's bytes, the suites' bytes, or the commit.

**So fingerprint identity is not tree identity.** Two lanes at different commits — or the same
commit with different uncommitted work, which is the normal state of the shared tree — produce the
same fingerprint and merge their cells into one file under it. The instrument's whole purpose is to
stop a result being read as evidence of running code that no single run produced, and this is that
shape, entered through the one door the existing refusal does not watch.

That the two runs agree on the *spec* is exactly what makes it invisible: there is no disagreement
for anything to detect.

Secondary and cosmetic, recorded so it is not mistaken for the same severity: `--pristine` defaults
to a global path too, so concurrent runs clobber each other's copy. It is only ever written, never
read back — `restore()` uses the in-memory `original` — so it is a debugging artefact, not a
correctness risk.

## What would refute this

A lock, a tree-scoped path component, or a refusal on a live concurrent holder existing anywhere in
`contract_battery.py`. None does. Alternatively: evidence that the runner guarantees one battery
per subject at a time across all worktrees — the dispatcher launching two seats three seconds apart
on one claim id is already on the record as evidence it does not.

## The repair, and why it is NOT in the commit that files this

The smallest mechanism that can fail: a sidecar `<out>.lock` created `O_EXCL` holding pid, worktree
path and start time. If it exists and the pid is **live**, refuse and name the holder. If it exists
and the pid is **dead**, say plainly that a previous run was killed, and proceed. Remove on exit
beside the existing `atexit` restore.

Deliberately not landed here, for a stated reason rather than a shrug: this is a **new control on
the instrument every other lane's battery runs through**, and a control added in haste to an
instrument is the exact defect class this file is filed under. It needs its own mutation-proven
test — one that shows the refusal *can* fire, not merely that a clean run still passes, since a
lock that never engages passes every test a careless author would write. It also should not land in
the same commit as a result I want reproducible against an unmoved fingerprint.

**Hand-off:** build the lock and its test as one atom. Done means the refusal fires against a live
holder, names it, and a poisoned round proves the test would go red if the refusal were removed.
