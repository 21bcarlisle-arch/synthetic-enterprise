**Severity:** LATENT · **Lane:** H_harness

# The OOM victim counter is the harness reading its own self-test back

`background/resource_headroom.py` publishes `oom_kills_total` from `/proc/vmstat oom_kill`, and
uses its **delta** to count the "VICTIMS taken during" a headroom episode (lines 38, 436–480,
527). Every one of those victims, right now, is a control deliberately OOM-ing **itself**.

## Class registration

Belongs to `measurements_that_mirror`. The instrument reads the harness's own activity back and
reports it as a property of the machine.

## Observed

| check | result |
|---|---|
| `Killed process` records in the `dmesg` ring buffer (back to Wed Aug 26 00:38) | **64** |
| of those, in an `ops2-peak-kill-selftest-<pid>.scope` cgroup | **64** |
| of those, in any other cgroup | **0** |
| distinct non-self-test `oom_memcg=` values in the whole buffer | **none** |

Every record is the same balloon — `total-vm:540388kB, anon-rss:523136kB, oom_score_adj:200` —
because it is the same fixture each time. The cgroup is created by this repository's own test:

```
tests/tools/test_measure_publish_gate_subject_cost.py:3148,3173
    unit = "ops2-peak-kill-selftest-{}".format(os.getpid())
```

The counter moved **105 → 107 between 17:21Z and 19:12Z today** while
`MemAvailable` sat at 18,625 MB of 24,032 MB — i.e. it rose by two during a window with no memory
pressure whatsoever. It rises when the publish-gate cost test runs, not when the machine is
short of memory.

## Why it matters, concretely

This is not cosmetic, and it is not the arithmetic that is wrong — the counter faithfully reports
what `/proc/vmstat` says. The defect is the **subject**: the number is presented as evidence about
the machine's memory pressure, and its actual subject is the test suite's own scheduling.

1. **It fabricates victims inside a real episode.** `resource_headroom` opens an episode, records
   `oom_kills_at_open`, and attributes the later delta to that episode. A publish-gate cost test
   running during any episode injects phantom victims into it. The episode is then more severe
   than the machine was.
2. **It was about to be cited as a root cause today.** The Lane 0 direction for the dead three-arm
   A/B run said to "check the OOM counter (`oom_kills_total: 105`)" and named memory pressure as
   the leading candidate. Had that been taken at face value, the run's death would have been
   closed as an OOM kill. It was not one — `dmesg` holds no kill in the window at all, and the
   real cause is a descendant-reaping killer already diagnosed in this repo at
   `tools/measure_publish_gate_subject_cost.py:207–229`. A contaminated instrument nearly bought a
   wrong diagnosis for a recurring failure that has now killed five runs.
3. **It is FAIL-OPEN in the direction that hurts.** A counter that only ever goes up, fed by a
   test, cannot distinguish "no real kills" from "no kills observed". A genuine OOM kill would be
   the 65th record among 64 decoys.

## The R4 nearest working analogue

`background/oom_watch.py` already draws the distinction this counter misses. Its line 93 says
`read_oom_kills` answers a **"DIFFERENT QUESTION"** to
`measure_publish_gate_subject_cost._scope_oom_killed`, "and deliberately not folded into it" —
i.e. somebody already saw that a scoped self-inflicted kill is a different thing from a machine
running out of memory. That separation was made in `oom_watch` and never propagated to
`resource_headroom`, which still counts both as one.

## What a fix has to do (not done here — this is the finding, filed per SELF-INTERRUPT DISCIPLINE)

Count victims from a source that can name the cgroup, and **exclude scopes the harness created
itself**, rather than from the undifferentiated `/proc/vmstat` total. The exclusion must be by
*writer*, not by prefix convenience — the memory note on directory-scoped exclusions applies:
ask who creates each excluded scope, and make the count going **down** to zero the passing case.

**R15 note for whoever builds it:** the control must be mutation-tested against a *real* kill in a
non-self-test cgroup, not only against the self-test one. A filter that excludes everything passes
this trivially, which is the failure mode to test for. And `/proc/vmstat` resets at boot, so
"lifetime" in the module docstring (line 13, "stands at 64 lifetime kills") is per-boot — a second,
smaller inaccuracy in the same sentence.
