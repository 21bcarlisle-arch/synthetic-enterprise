# SEAT FINDING — /tmp reached 100% mid-turn, and the failure surfaced as every command losing its output rather than as a disk error

**Severity:** LATENT · **Lane:** H_harness

**Date:** 2026-09-10 (delivery seat, found while working the lane-0 door-test item)

---

## What happened

Mid-turn, every `Bash` call began returning:

> `Command output was lost: the temp filesystem at /tmp/claude-1000/... is full (0MB free). The
> child process's stdout/stderr writes failed with ENOSPC.`

The commands still **ran**. Only their output was lost. That is the dangerous shape: a `git`, a
`pytest` or a `surgical_land` invocation completes and the session cannot see what it said, so a
refusal reads identically to a success and to a crash. `df` itself could not report, because `df`
also writes to stdout.

Measured by redirecting to a file on `/var/tmp` and reading it back:

```
tmpfs   12G  12G  0  100%  /tmp
7.6G  /tmp/pytest-of-rich      <- 509 basetemp directories
1.3G  /tmp/claude-1000
~1.9G /tmp/{headfull,headnow,headx,mycommit,headtree,llg_base_*,llg_head_*}
```

## The cause, and the part of it I did not fix

**`/tmp` is a 12G tmpfs — it is RAM.** Two producers fill it:

1. **509 pytest basetemps** under `/tmp/pytest-of-rich`, 7.6G. pytest garbage-collects its own
   basetemps only within one root and only a few deep; at this rate of concurrent runs it cannot
   keep up. The lowest-numbered dirs (`pytest-1774`, `pytest-1776`, ~5,200 entries each) were being
   **written to at the moment of measurement**, so they are live sessions and were left alone.
2. **Hand-made HEAD extracts left behind by earlier turns** — `/tmp/headfull`, `/tmp/headnow`,
   `/tmp/headx`, `/tmp/mycommit`, `/tmp/headtree` — ~316M each. `tools/surgical_land.py`'s
   `sweep_stale_extracts()` returned `(0, 0)`: it sweeps only extracts it made and marked with a
   PID. **Nothing sweeps a hand-made one**, and every "extract HEAD, apply hunks, land `--content`"
   procedure in the memory index makes one.

I removed only the group in (2) plus `/tmp/cim` and `/tmp/iso_dr`, all idle 3+ hours, freeing 1.4G.
**The 7.6G in (1) is untouched and will refill.** This will recur, probably within the day.

## Why it is worth a finding rather than a cleanup

* The symptom does not name the cause. Nothing said "disk"; every tool simply went quiet. A tick
  that cannot read its own output is a tick that can report anything.
* `surgical_land` **does** refuse honestly on this — `MIN_FREE_MB`, "REFUSED on DISK, not on code"
  — and that refusal is the good case. The bad case is the ~1.9G of extracts *made by procedures
  this project's own memory recommends*, which nothing reclaims.
* It is a shared-machine failure: it wedges every concurrent lane at once, not the lane that filled
  it.

## What would fix it, in order of size

1. **A sweeper for hand-made extracts.** `sweep_stale_extracts` already has the shape; what it
   lacks is a claim on anything it did not create. Cheapest honest version: sweep any directory
   directly under `/tmp` that is a git checkout of this project and has been idle > 90 minutes —
   the same 90 minutes the run reaper already uses.
2. **A basetemp cap for the pytest lanes** (`--basetemp` under `/var/tmp`, or a numbered-dir retention
   the concurrent rate can actually keep up with). `/tmp` being RAM is the reason this is urgent
   rather than merely untidy.
3. **A headroom check that reads disk, not only memory.** `background.resource_headroom.sample()`
   is the figure this project quotes for memory; a lane about to run a full gate has no equivalent
   question to ask about the filesystem it will run in.

Not done here, and deliberately: this was found while working an unrelated lane-0 item, and the
1.4G freed is enough to finish it. Filing beats routing around it.
