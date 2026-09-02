# [WORKER FINDING] The deadman has run nine-day-old code since 24 August, so a landed fix is not a running one

**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted
**Found:** 2026-09-02, while answering the director's question about whether the worktree reaper
caused the 830-test red.

## Class registration

Belongs to `no_caller_and_never_runs`. One layer further out than every previous instance: here the
caller **exists, is committed, and is mutation-proven** — and the process that would run it has not
loaded it.

## The measurement

```
$ ps -eo pid,lstart,args | grep deadmans_switch
484  Mon Aug 24 15:16:33 2026  /usr/bin/python3 background/deadmans_switch.py

$ grep -c "WORKTREE REAP" docs/observability/deadmans-switch-log.md
0
```

The deadman's process started **2026-08-24** and has been running continuously for nine days. It is
a long-lived `while True` daemon, not a timer-fired oneshot, so it holds the module it imported at
start. `_check_worktree_reap` — landed last night in `580c47101`, wired into `run_cycle`, and pinned
by a test that reds if the call is removed — **has never executed**. Its log line does not appear
once.

## What that means for last night's work, said plainly

I reported the worktree lifetime as fixed and wired to the cycle. **The wiring is real in git and
absent in the running machine.** The reaper has run exactly three times in its life, all three by my
hand at ~22:20 yesterday. That is also the answer to the director's adjacency question — see the
companion finding — but it is a much bigger fact than that one answer.

## The class, and why it is worse than the ones before it

Every previous instance was a mechanism nobody had connected. This one is connected. The test proves
the connection. `grep` proves the connection. And the connection is not running, because the
DEPLOYMENT step — restarting the daemon that holds the code — is not part of landing, is not checked
by anything, and leaves no red.

So `background/` currently has two populations that look identical from the repository:

1. code the daemons are running, and
2. code that is committed, tested, green, and will not run until something restarts a process.

**Nothing tells them apart**, and nothing anywhere reports the age of a running daemon against the
age of the code it loaded. That is the same shape as the empty acceptance list and the unwired
reaper: a fact nobody can observe, so nobody acts on it.

## What is owed, and it is not "restart the daemon"

Restarting is the instance fix and it is worth doing. The class fix is a control that can FAIL:

1. **A daemon's loaded code has an age, and something must report it.** Every long-lived daemon in
   `process_manifest.yaml` can be asked when its process started; every module it imports has a
   committed mtime. A daemon older than the newest commit to a module it holds is running stale code
   and should say so — loudly, with the module named, on the same cadence as every other check.
2. **Landing a change to a daemon module should name the daemons that hold it.** The information is
   already in `process_manifest.yaml`; nothing joins it to a pathspec.
3. **It must fail closed.** A daemon whose start time cannot be read is UNPROVEN, not fresh.

Not built here. It wants its own pre-registration because it will page on a real, standing condition
the moment it is armed — the honest expectation is that several daemons are stale right now, and the
first run will say so about more than one.

## What this finding does not claim

Not that the daemon is broken — it has been doing its job for nine days. Not that long-lived daemons
are wrong; the deadman must outlive what it watches, which is exactly why it does not restart. The
claim is narrower and it is about EVIDENCE: **a green test proves the code is right, and proves
nothing whatever about the code being loaded.** I asserted otherwise last night, in a commit message
and to the director, and that assertion was not checked because nothing on this box can check it.
