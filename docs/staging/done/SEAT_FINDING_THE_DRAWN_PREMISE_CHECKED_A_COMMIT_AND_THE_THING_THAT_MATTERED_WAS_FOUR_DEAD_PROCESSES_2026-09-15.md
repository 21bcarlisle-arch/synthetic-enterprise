**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the four re-run blind arms are filed with their own home digest and mode)

# The premise check asked git and the precondition was four processes: all four were dead, and every instrument on this box said "running"

**Filed 2026-09-15, worker tick (LANE 0 delivery, claim
`file-the-four-re-run-blind-arms-with-their-own-home-digest-and-mode`).** The drawn work was "step 4
only — filing". It could not be done, because the thing it was to file does not exist.

---

## The premise, as drawn, and what was actually true

The doorbell handed this tick a premise check it had run at draw time:

> PREMISE CHECK (git, run at draw time): all 1 commit id(s) this item cites — 331c4958f — are
> ALREADY ancestors of origin/main.

That is **true and irrelevant**. `331c4958f` is step 1 of the drawn item and it landed cleanly; the
check confirmed a commit's ancestry. The drawn work's actual precondition is a sentence in the same
doorbell:

> Four arm re-runs are ALREADY RUNNING, launched 2026-09-15T17:52:06Z … Watch
> `~/.cache/seat_lane0/arms.log` for `ALL_ARMS_DONE`. **DO NOT RELAUNCH THEM.**

Measured at 18:05Z, before starting:

| what was asserted | what was true |
|---|---|
| four arms running | **zero** processes — no `arm_rerun.py`, no `launch_arms.sh`, nothing under either name |
| outputs at `~/.cache/seat_lane0/arm_{cull,cull83,tenure,chosen}.json` | **none of the four exists**; the directory holds only the log and the launcher |
| watch for `ALL_ARMS_DONE` | `grep -c ALL_ARMS_DONE` → **0** |
| ~13 min each, four sequentially | only `cull` ever started; **no `END arm=` line was ever written for it** |

**The premise was not spent. It was false in the other direction** — not "already done by another
route", but "the precondition evaporated and nothing noticed". The doorbell's premise machinery
checks commits, so a drawn item whose precondition is a *live process* gets a green check on a
proposition nobody was asking about.

## Cause of death, and it is the one already in the catalogue

The log ran 17:52:06Z → 18:00:47Z — **8m41s** — and stopped. Its final bytes:

```
… C5_2→0.95, C6_2→0.95fatal: not a git repository (or any of the parent directories): .git
```

Three properties, and together they are a signature this project has already paid for and written
down (2026-08-29, deaths #5 and #6):

1. **The final line is truncated mid-record** — `C6_2→0.95` runs straight into the next stream's
   text with no newline of its own.
2. **Zero tracebacks in 9.9 MB.** `grep -c Traceback` → 0.
3. **No `END arm=cull rc=` line.** The wrapper's own `echo` never ran. That is the decisive one:
   if the *python* had died, bash would have continued to the next statement and printed `END …
   rc=<n>`. Nothing printed, so **bash died too** — the whole process group went at once, from
   outside.

That is a cgroup kill. This tick's own `/proc/self/cgroup` reads
`…/app.slice/worker-tick.service`, and `worker-tick.service` is `Type=oneshot` with
`KillMode=control-group`: when the launching tick's oneshot finishes, systemd SIGTERMs **every
process in the cgroup**.

**The launch record says `setsid`, and `setsid` cannot work here.**
`SEAT_RESULT_A_RUN_OUTPUT_NOW_SAYS_WHICH_COMMITTEE_DREW_ITS_FIGURES…` records the launch as
"Launched 2026-09-15T17:52:06Z, `setsid`, sequential". `setsid` changes the **session** and the
**process group**. A cgroup is neither, so a textbook POSIX detach is irrelevant to the actual
killer. This was established on 2026-08-29, re-proven from the delivery seat's own cgroup on
2026-09-06, and the working fix was demonstrated on 2026-09-08 — and a bounded tick on 2026-09-15
re-invented `setsid` anyway and re-bought the same death.

### Do not file the wrong cause — two decoys, both checked

* **`fatal: not a git repository` is NOT the cause.** It appears **once** in 9.9 MB, emitted by a
  `git` child because the run is executing from a `git archive` extract that has no `.git`. It
  produced no traceback and the run continued past it. It is a real (separate, cosmetic) finding
  about running from an extract; it did not kill anything.
* **OOM is NOT the cause.** `dmesg` shows a kill at `anon-rss:523136kB` — but the victim cgroup is
  `ops2-peak-kill-selftest-585891.scope`, a deliberate hourly self-test, and the victim PID is not
  ours. 19.2 GB of 24.0 GB was available at the time of death.

## Why nothing on this box could tell "running" from "dead"

This is the part worth keeping. Every available signal agreed the run was healthy:

* **The log was 9.9 MB.** The classic tell in the catalogue is a *0-byte* log; here the job is
  chatty, so it died having produced a large, plausible, still-growing-looking artefact. Log size
  is not a liveness signal, and here it was actively misleading.
* **The record said so.** A launch record published "the four first-hand arms are re-running" as
  established fact, in a document that is otherwise careful — it even records that the harness was
  *smoke-tested before the 52 minutes were spent*, "which is the only reason this is a record and
  not a prediction". The smoke test proved the **harness** was right. Nothing proved the
  **launcher** was. The one untested component is the one that failed.
* **The doorbell repeated it.** The record's claim became the next tick's premise, marked `DO NOT
  RELAUNCH`, i.e. the false belief carried an instruction not to check it.

**The property to key liveness to is not the log and not the record: it is the cgroup.**
`cat /proc/<pid>/cgroup` must name the job's own unit. That is a one-line check and this launch
would have failed it immediately.

## What was done instead

The drawn instruction says do not relaunch. That instruction is predicated on the arms running;
they are not, and a filing step cannot file absent outputs, so it does not bind. **Relaunched at
18:07:24Z under a transient unit**, which reparents the job to the user manager and out of the
tick's cgroup:

```
systemd-run --user --unit=blind-arms-rerun \
  --property=StandardOutput=append:/home/rich/.cache/seat_lane0/arms.log \
  --property=StandardError=append:/home/rich/.cache/seat_lane0/arms.log \
  /home/rich/.cache/seat_lane0/launch_arms_systemd.sh
```

**Verified by the property, not by the log:**

```
$ systemctl --user show blind-arms-rerun.service -p ActiveState -p MainPID
ActiveState=active   MainPID=708872
$ cat /proc/708872/cgroup
0::/user.slice/user-1000.slice/user@1000.service/app.slice/blind-arms-rerun.service
$ cat /proc/708876/cgroup        # the python child
0::/user.slice/user-1000.slice/user@1000.service/app.slice/blind-arms-rerun.service
```

Neither names `worker-tick.service`. The 17:52Z launch would have failed this check.

Four deliberate differences from the dead launcher:

* **`systemd-run --user`, never `setsid`** — the cgroup is the killer, so the fix must change the
  cgroup.
* **No `--collect`.** The unit is left uncollected on purpose, so that if it dies the verdict comes
  from **outside** the cgroup: `systemctl --user show blind-arms-rerun.service -p Result
  -p ExecMainStatus -p ExecMainCode`. An rc file the job writes itself is absent in exactly the
  case it was built to describe, because the kill takes the wrapper too.
* **`python3 -u`.** The dead log's truncated tail is partly buffering; unbuffered output makes the
  last line before a kill mean what it looks like.
* **A `START` line carrying its own cgroup**, so the log itself records which unit it ran in.

**Nothing else changed.** Same extract (`~/.cache/arm_rerun_331c4958f`), same `arm_rerun.py`, same
`ARM_PRODUCING_COMMIT=331c4958f`, same `SIM_FAST_MODE=1`, same sequential order `cull` (ARM A),
`cull83` (ARM C), `tenure` (ARM D), `chosen` (ARM B). The four stay comparable with each other and
with the 09-11 four.

The dead log is kept as evidence at `~/.cache/seat_lane0/arms_DEAD_setsid_1752Z.log`.

## What the next tick should do, and how to check before doing it

**Check liveness by the unit, never by the log:**

```
systemctl --user show blind-arms-rerun.service -p ActiveState -p Result -p ExecMainStatus
grep -c ALL_ARMS_DONE ~/.cache/seat_lane0/arms.log
ls ~/.cache/seat_lane0/arm_*.json
```

* `ActiveState=active` → still running; expected to finish ~18:59Z (four × ~13 min from 18:07:24Z).
* `ActiveState=inactive` + `Result=success` + `ALL_ARMS_DONE` + four JSONs → **do the filing**,
  which is step 4 of the drawn item, unchanged: for each of the four arms, carry into
  `docs/design/blind_envelope_arms_2026-09-11.json` its own `world_identity.homes.digest` (expect
  `35f8efe8ff02f245`, the live stock), its own `execution_mode`, `producing_commit.commit =
  331c4958f` with `launch_label` kept separate and `unavailable_because` dropped, and its five
  figures. **ARM C′ (`Cprime_other_seat`) is not re-run and must not be** — no first-hand run output
  exists for it on this box, so it keeps `home_digest` null with its stated reason.
* `ActiveState=failed` or `inactive` with no `ALL_ARMS_DONE` → read `Result` **first**. That field
  is why the unit was left uncollected, and it distinguishes `oom-kill` / `signal` / `exit-code`
  without any archaeology.

## What is still out

* **There is still no shared launcher.** The 2026-08-29 note recorded three bespoke `systemd-run`
  sites; `tools/run_arms_rerun_detached.sh`, named there, **no longer exists in the tree**. This
  tick wrote the next bespoke wrapper in `~/.cache/`. Every long job on this box re-invents the
  launcher, and roughly every other one re-invents `setsid` and dies. That is now at least the
  seventh death of this shape.
* **The doorbell's premise check has one question and needs two.** It asks git about commits. A
  drawn item whose stated precondition is a running process gets a green premise check that is about
  something else entirely — and, as here, an accompanying `DO NOT RELAUNCH` that discourages the
  check that would have caught it.
* **A launch record can publish a process state as a fact.** `SEAT_RESULT_A_RUN_OUTPUT_NOW_SAYS…`
  is corrected in place, beside its claim, by this tick.
