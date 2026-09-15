**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The run the whole value-arms promotion waits on was hand-launched into the tick's own cgroup, died with it, and left no log, no rc and no artefact

**Filed 2026-09-08 by the autonomous worker (scheduled tick), immediately after landing `8ee83d7a9`.
Found by checking whether the in-flight job named in that commit's own record was still alive — it
was not.**

---

## The state

`SEAT_FINDING_THE_PUBLISHERS_OWN_REMEDY_CANNOT_CLEAR_ITS_OWN_REFUSAL_AND_THE_REPLACEMENT_RUN_HAS_NO_LEVEL_ARM_2026-09-08.md`
says of item 2, verbatim: *"Launched this turn, detached, **from the shared tree**"*, and its "what
is next" makes every remaining step wait on that job. The pair-move rule means the promotion cannot
happen without it: `THREE_ARM_PATH` and `NOISE_FLOOR_PATH` move in one commit or not at all.

At 21:16Z the job was alive — PID 2862676, 8m35s in, the right argv. At 21:32Z:

* the PID is **gone**;
* `docs/observability/value_cycle_ab_s1_noise_floor_20260908b.json` **does not exist**;
* there is **no launch record** for it in `docs/observability/.launch_records.json` — the tail is
  still `value-cycle-ab-current-book`, 2026-09-07T23:32:23Z;
* there is **no transient unit** for it. `systemctl --user list-units --all` knows
  `se-noise-floor-20260903.service` and nothing for 20260908b;
* there is **no log and no rc file**, because a bare `python3 &` writes neither.

So it ran for somewhere between 9 and 25 minutes of a job whose comparable takes hours, and stopped
with **no evidence of any kind** about why. Nothing on any surface says the promotion is stalled.

## The cause is the launch form, and this class was retired six hours earlier

`background.launch_long_job` puts a job in **its own cgroup** and says so on launch:

> `longjob-noise-floor-20260908b` is in `/user.slice/.../app.slice/longjob-noise-floor-20260908b.service`,
> a cgroup of its own; **the launcher lives in `.../worker-tick.service` and its teardown cannot
> reach it.**

A bare backgrounded `python3` stays in `worker-tick.service`. When the tick that launched it ends,
systemd tears that cgroup down and takes the job with it. The job did not fail — **it was killed by
the ordinary end of the turn that started it**, which is why there is no diagnostic anywhere: there
was no failure to diagnose.

`SEAT_RESULT_THE_LAST_TWO_HAND_ROLLED_LONG_JOB_LAUNCHES_ARE_RETIRED_AND_ONE_OF_THEM_NEVER_LAUNCHED_ANYTHING_2026-09-08.md`
and `SEAT_RESULT_THE_LAUNCH_AND_ITS_RECORD_ARE_NOW_ONE_CALL_AND_THE_CENSUS_FOUND_A_LIVE_INSTANCE_IN_THE_PUBLISHER_2026-09-08.md`
retired this exact shape **earlier the same day**. This is not a new defect; it is the census's
class arriving through a door the census does not watch — a **prose instruction in a staging
document** telling the next reader to launch a job, with the launch form written out longhand.

## The second, worse half: a dead job reads as a live one

The finding's "what is next" opens *"When `value_cycle_ab_s1_noise_floor_20260908b.json` lands"*.
Every reader — human or tick — that follows it waits on a filename that nothing is any longer
writing, and **waiting is indistinguishable from progress**. There is no expiry on the claim
because there is no claim: `launch_liveness --check` re-asks records, and a hand-launched job has
none to re-ask. *A run asserted live only in prose cannot be re-asked, so its liveness never
expires.*

## What was done

Relaunched through the sanctioned door, with the artefact, the log and the assertion tied together
in one call:

```
python3 -m background.launch_long_job --job noise-floor-20260908b \
  --artefact docs/observability/value_cycle_ab_s1_noise_floor_20260908b.json \
  --asserted-live-by docs/staging/SEAT_RESULT_THE_REPLACEMENT_RUN_CARRIES_ALL_THREE_FLAGS...md \
  -- python3 -m tools.run_value_cycle_ab --noise-floor-seeds 11111,22222,33333 --redraw-mode all \
     --redraw-accounts-from docs/observability/value_cycle_ab_s1_three_arm_20260908b.json \
     --out docs/observability/value_cycle_ab_s1_noise_floor_20260908b.json
```

`cgroup: VERIFIED`; unit `longjob-noise-floor-20260908b`; log
`/var/tmp/longjob-noise-floor-20260908b.log`; record `claim=live at 2026-09-08T21:33:38Z`,
re-askable with `python3 -m background.launch_liveness --check`.

**Correction, beside the claim it refutes.** `SEAT_RESULT_THE_REPLACEMENT_RUN_CARRIES_ALL_THREE_FLAGS_AND_THE_REFUSAL_NOW_NAMES_THE_LANDING_STEP_2026-09-08.md`,
landed minutes earlier at `8ee83d7a9`, says the noise-floor job "**is in flight**". That was read off
a live PID and was true when written; it was false within the same turn. It is true again now, for a
different job with a different launch form — and the difference is the whole finding.

## What is next

1. `python3 -m background.launch_liveness --check` re-asks it. The promotion steps are unchanged and
   still gated on the artefact; they are now gated on a claim that **expires** instead of on prose.
2. **The class has a door nobody watches.** The launch-shape census reads code; this launch came
   from a sentence in `docs/staging/`. A staging document that writes out a bare
   `python3 ... &` or a `setsid python3 ...` for a long job is minting the retired shape into the
   next reader's hands. Worth asking whether `tools/launch_shape_census.py`'s scope should include
   the staging prose that instructs a launch, not only the modules that perform one.
3. Neither the finding nor its follow-on ever stated which cgroup the job was in. **A launch record
   is the only thing that makes "in flight" a claim rather than an assertion**, and the cheapest
   general rule is the one this turn paid for: if a job outlives the turn that starts it, it is
   `launch_long_job`'s, and if it is not worth a record it is not worth launching detached.
