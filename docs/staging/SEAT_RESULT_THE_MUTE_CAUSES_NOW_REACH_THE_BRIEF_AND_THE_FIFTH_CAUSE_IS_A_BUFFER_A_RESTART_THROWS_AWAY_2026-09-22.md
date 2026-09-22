# The mute causes now reach the brief, and the fifth cause is a buffer a restart throws away

**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

**Lane 0 item:** `the-mute-daemon-causes-are-filed-in-a-key-nothing-reads-and-are-not-committed`
**Date:** 2026-09-22

---

## What was outstanding, and what it actually was

The measurement half was done and is not redone here: four `log_silence` blocks sat in
`background/process_manifest.yaml`, uncommitted, and `grep -rn log_silence` returned the manifest
and nothing else. The load-bearing defect was that **no reader read the key** — a finding filed
where nothing looks is not filed.

Both halves are now closed. `declared_daemon_health` reads `log_silence` onto every declared row as
`declared_cause`, and `_mute_sentence` splits the mute daemons into **NO CAUSE ON FILE** (the
actionable list, the only part that asks anything of the reader) and **CAUSE ESTABLISHED AND ON
FILE** (shown, but asking nothing).

**The two keys are deliberately not merged.** `why_no_log` is a *measured* absence — this reading
could not get a number. `declared_cause` is a *declared* one — a human established why and wrote it
down. Collapsing a declared cause into a measured absence is the same defect the reader was built
to fix, one level up.

## A fifth cause: block-buffered stdout that SIGTERM discards

The item expected the five newly-mute daemons to be fresh starts and asked whether a fresh start is
evidence of anything. **It is not a fresh start — it is a permanent state**, and the mechanism is
new:

1. Under systemd a daemon's stdout is a socket, not a tty, so Python **block-buffers it at 8 KiB**.
   None of `supervisor`, `deadmans-switch`, `staging-watcher`, `naive-organ` passes `flush=True`.
2. `background/deploy_restart.py` restarts these units on every landing that touches their module —
   measured at a **~10-minute cycle** (`Consumed 1min 23s CPU over 10min 25s wall clock`,
   `NRestarts=0`, so this is a deploy, not a crash loop).
3. **The SIGTERM that ends a run does not flush the buffer.**

A few lines per 10-minute run can never reach 8 KiB, so every line is discarded at every restart,
forever. The age never grows because the restart clock resets it — *a fresh start is what this looks
like permanently*.

**Controlled directly, not inferred.** An unflushed `print()` in a `systemd-run` unit produced no
journal line while alive **and none after `systemctl stop`**; the identical file with
`sys.stdout.reconfigure(line_buffering=True)` reached the journal in under a second. All four
daemons are emphatically alive — their own log files were written 2–8 minutes before the reading
(`supervisor-log.md` at 380,766 lines).

This also **answers the open question left on the `ntfy-responder` row**, which said block-buffering
was "the obvious candidate and the volume argues against it". The volume does not argue against it:
what matters is volume *per run between restarts*, and ~1,300 lines over 106 h is roughly two lines
per 10-minute run — nowhere near 8 KiB.

## Which definition of mute — 4 and 5 came from two of them

This is now stated on the page rather than inferred from the count:

- **A** — "the daemon's *own stdout* has written no journal line since it started." The manifest's
  first four rows were established under this.
- **B** — "*nothing inside the unit* has written in this run — not the daemon, not any child it
  spawned — so the only entry is systemd's own." **This is the one the reader applies.**

B is the honest one for a *liveness* question: under A, `ntfy-responder` and `dispatcher` graded
mute while demonstrably working, because their newest lines came from a `git push` **child** —
output that is proof the daemon is alive and doing its job. A remains right for a *diagnosability*
question. **So a count moving 4 → 5 is not decay**, which is why the sentence names the sessions and
tells the reader the count is not the reading.

*A correction to my own working note, kept beside the claim:* I first read those child lines as
coming from a **dead** run, because pid 321004 is far below the current MainPID 2358733. That was
wrong — `_SYSTEMD_INVOCATION_ID` matches the unit's current `InvocationID`, so the lines are from
this run and the reader is right. Pid ordering is not a run boundary on this box; the invocation id
is.

## The wiring is proven by a daemon changing behaviour, not by an assertion

`background/staging_watcher.py`'s `log()` now passes `flush=True`. **Pre-registered before the
change:** `staging-watcher` reads `mute: true`; with the flush it should read `mute: false` and
leave the mute list.

`deploy_restart` restarted the unit at 17:46:19 and its own MainPID wrote a line at **+58 ms**. The
reading flipped as predicted. Same daemon, same startup path, same unit — **only `flush=True`
changed**. The file remains the system of record; this makes the daemon audible on the channel the
brief's liveness reading actually watches, so a staging doorbell going quiet is distinguishable from
one going away.

`naive-organ` was deliberately **not** given the same repair: its output is judgement, not trace,
and a second copy of its verdicts in a store with no retention policy is not an improvement. Its row
says so.

## A sixth shape, observed in both states

`background-worker` is **intermittently audible** — the same mechanism, but sometimes verbose enough
to push past 8 KiB before the SIGTERM. Observed seven minutes apart with one restart between: at
17:40 not mute (MainPID 1767967 had written two `[process_run]` lines), at 17:47 mute. Its `mute`
reading is true but **not stable**, so its appearance in the actionable list is evidence about that
run's verbosity, never about the daemon's health.

## Control

`test_A_MUTE_DAEMONS_ESTABLISHED_CAUSE_REACHES_THE_BRIEF_AND_AN_UNESTABLISHED_ONE_IS_ASKED_FOR`
asserts both sides of the partition against two daemons mute for the *same* number of seconds, so
the cause is the only discriminator. Mutation-proven at two distinct legs: dropping `declared_cause`
from the row kills the "cause reaches the brief" assert; merging the two populations kills the
`ACTIONABLE_ONLY` assert. The fixture is built by *stripping* the live manifest, so it cannot drift
into asserting a cause the manifest no longer carries.

## What is left

`worker-seat-manager` remains mute by construction with no write-out path at all. Its row already
records that a heartbeat line is a real behaviour change to the daemon that seeds the worker seat
and deserves its own evidence. That is still the right call and it is still open.
