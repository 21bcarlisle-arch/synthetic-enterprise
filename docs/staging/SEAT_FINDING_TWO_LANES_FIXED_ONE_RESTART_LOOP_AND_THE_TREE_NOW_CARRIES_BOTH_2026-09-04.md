**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# Two lanes fixed the same restart loop within two minutes of each other, and the merged tree now carries both mechanisms

**Found:** 2026-09-04, delivery seat, immediately after landing one of the two. Recorded because I
cannot attribute the outcome, and saying so is the point.

---

## What happened

Two lanes independently found the same defect — daemons restarted every ten minutes to clear a
staleness condition a restart cannot clear — and fixed it by different routes, two minutes apart:

| | commit | where | how |
|---|---|---|---|
| theirs | `3ecf355d8` (10:47:31) | `background/boot_sha.py` | the boot stamp records HEAD **plus the content hash of every file that differed from HEAD at that instant**, so the comparison is exact |
| mine | `d7d658284` (10:46-ish) | `background/deploy_restart.py` | the changed set is dated from the **process**: keep only paths whose mtime is newer than `now - running_age_s` |

`711730228` merged them. The merge is clean and gated (`gate-rc: 0`, 398 passed), and both live in
the running tree: `changed_paths_since` now returns a content-correct set, and
`unincorporated_since_start` then dates that set a second time.

## Why this is a finding and not a happy ending

**Theirs is strictly better than mine.** It compares content, which is the actual question. Mine
compares mtime, which is a proxy I named as a proxy in its own docstring. On the cases that matter
the two agree — a file whose mtime predates the process start is a file the process loaded, and it
compares equal under theirs too — so mine is now, on the restart path, a **second implementation of
a rule that already has one**.

That is this project's most expensive recurring shape and it is named in CLAUDE.md: one legal
requirement, five implementations, a defect fixed in one of them in July and still live in another
in August. Two mechanisms for one rule is how that starts. It is invisible to every lane except this
seat, because each lane's own commit is correct and green.

**And I cannot attribute the outcome.** Both changes reached the running tree in the same merge, so
whatever the restart log does next, I cannot say which fix did it. The honest statement is *"I cannot
yet say"*, and the one-variable version has not been run.

## What I am NOT doing, and why

I am not deleting my filter in this turn. It is fail-closed, it is not wrong, and removing a guard on
a live loop that has been running for eight hours — on the strength of an argument rather than a
measurement — is the wrong order. Their own commit already shows why: their first draft let a deleted
path collapse the whole content map to `None`, silently restoring the over-report, and was caught
only because the fix "appeared to change no daemon's count at all". A second draft written in a hurry
against a live incident is exactly the thing not to trust yet.

## The disposition I recommend, for whoever takes this

1. Confirm the loop has stopped with both in place (the acceptance test, not an argument).
2. Then run the **one-variable** version: disable `unincorporated_since_start`'s filter alone and
   check the staleness sets are unchanged. If they are — which is what I expect, since theirs
   subsumes mine — **delete mine** and keep theirs.
3. Keep two things from mine regardless of that outcome, because they are keyed to properties rather
   than to today's answer and survive either implementation:
   - `test_no_published_time_behind_can_exceed_the_rows_own_running_age` — the bound that six of
     eleven published rows were breaking by up to 27 hours.
   - the `predates_start` field, which publishes what the dating removed, so a staleness set can
     never shrink silently again.

## Still open, unchanged by the merge

`unincorporated_for_s` can still return a **negative** age: `daemon_deployment_report` samples
`now = time.time()` once and stats the files afterwards. Filed in
`SEAT_FINDING_THE_STALENESS_SIGNAL_COULD_NOT_BE_CLEARED_BY_THE_RESTART_IT_TRIGGERED_2026-09-04.md`
and not fixed there either, for the reason given: the obvious clamp to `0.0` breaks the
`bool(time) == bool(verdict)` invariant.
