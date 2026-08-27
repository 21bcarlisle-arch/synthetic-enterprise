**Severity:** LATENT · **Lane:** H_harness

# [SEAT] re-run-the-three-arm-ab-on-the-s1-world was claimed and has not moved for 2.0h

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **1 times without its state changing**, over **2.2h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 1th page does not.

## The alarm, verbatim

```
[SEAT] re-run-the-three-arm-ab-on-the-s1-world was claimed and has not moved for 2.0h
No commit has touched its 4 claimed path(s) (docs/design/THE_VALUE_CYCLE_REALISED_AB.md, docs/staging/in_progress/LANE0_THREE_ARM_AB_ON_THE_S1_WORLD_2026-08-27.md, tests/tools/test_the_level_arm_in_the_ab_runner.py, tools/run_value_cycle_ab.py) in that time. The claim is released and the work is drawable by any lane.
What the seat said it was doing: First act, and it costs minutes: `docs/design/THE_VALUE_CYCLE_REALISED_AB.md` still opens its 2019 ladder section with "THE HEADLINE ... the win is NOT price" and a 1.16x figure, and the later full-wi
```

## What is known without diagnosing anything

- Signature: `seat-claim:re-run-the-three-arm-ab-on-the-s1-world` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-27T15:01:40+00:00
- Repeats before escalation: 1 (threshold `ESCALATE_AFTER_REPEATS`)
- Paging for this signature is now SUPPRESSED. It resumes automatically the moment the
  underlying state changes — including when it clears.

## What this document is asking for

The repetition is the finding. Something is failing the same way on a loop and nothing is
converging on it, which is the shape the director named as "a symptom, not an event". Draw
this, diagnose the condition named above, and either fix it or record why the alarm is wrong.

Archive to `docs/staging/done/` when the condition is resolved. While this document is live
-- here or in `in_progress/` -- a continuing condition APPENDS a dated line below rather than
filing a second document (2026-08-24). A condition that returns AFTER this has been archived
files a fresh document, because that is a new episode and an R3 two-strike signal.

## RESOLVED 2026-08-27 — the alarm was RIGHT, and the disposition is the only thing that failed

**The alarm machinery is not at fault and needs no change.** It fired on the correct condition
(no commit touched the claimed paths in 2.2h), it escalated itself into the draw exactly as the
2026-08-20 instruction says, and it released the claim so another lane could take the work. Every
part of that worked. What failed is that the document then sat **untracked in the staging root**
and nobody dispositioned it — so the diagnosis below was available two hours before it was read.

**Why the claim stopped moving: the run it was waiting on had been dead since 15:12:53Z.**
Full R9-labelled evidence is in
`docs/staging/in_progress/LANE0_THREE_ARM_AB_ON_THE_S1_WORLD_2026-08-27.md`. In short:

- **OBSERVED** — launched 15:08:25Z with session detachment demonstrably held
  (`pid == pgid == sess == 1128717`); last wrote 4m28s later; 56,229 lines; no `END rc=` line, no
  traceback; artefact never created; PID gone.
- **OBSERVED** — **not** an OOM kill. `dmesg`'s buffer covers the window (back to Aug 26 00:38)
  and holds no `Killed process` record between 16:08 and 16:13 local; the nearest are *before*
  the launch and 15 minutes *after* the death.
- **OBSERVED** — the `oom_kills_total` counter that was going to be cited as the cause is
  contaminated: all 64 records in the buffer are this repo's own
  `ops2-peak-kill-selftest-<pid>.scope`, a control OOM-ing itself in a private cgroup
  (`tests/tools/test_measure_publish_gate_subject_cost.py:3148,3173`). Filed separately.
- **OBSERVED** — no `END` line at all means the wrapper *shell* died with the child, i.e. the
  whole group went, not just Python.
- **INFERRED** — this is the **fifth** death of a class already diagnosed in this repo at
  `tools/measure_publish_gate_subject_cost.py:207–229` ("THE FOURTH DEATH", 2026-08-10):
  `start_new_session` changes session and group but **not `ppid`**, so a killer walking a bounded
  tick's descendants still finds the job.

**R3 two-strike disposition — do not detach a sixth time.** The escalation was already built
(`systemd-run --user`, which re-parents out of the descendant tree). `tools/run_value_cycle_ab.py`
simply had no launch mode able to reach it. The re-run uses `systemd-run --user` and the Lane 0
file records the exact invocation.

This episode is closed. A recurrence files a fresh document.

