**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The leg that produces the published bound was OOM-killed after 1h 09m and wrote nothing, and an absent artefact reads exactly like a run still in progress

**Class:** `controls_that_cannot_fail` (primary), `uncommitted_and_orphaned_work` (secondary)
**Filed:** 2026-09-03, delivery seat, Lane 0, claim
`the-baseline-was-beaten-in-a-world-that-no-longer-exists`
**Subject:** `tools/run_value_cycle_ab.py` noise-floor mode; transient units
`se-noise-floor-20260903`, `se-floor-only-20260903`, `se-floor-except-20260903`.

## What happened

Act (b) of the Lane 0 draw needs four legs measured in one world: the three-arm run and three floor
legs (`all`, `only`, `except`). At 10:17/10:23Z on 2026-09-03 all three floor legs were launched
**concurrently** as transient units. At 11:27:32Z systemd reported:

```
se-noise-floor-20260903.service: The kernel OOM killer killed some processes in this unit.
se-noise-floor-20260903.service: Failed with result 'oom-kill'.
Consumed 1h 9min 7.465s CPU time over 1h 9min 35.554s wall clock time,
  6.4G memory peak, 895.8M memory swap peak.
```

The leg that died is `--redraw-mode all` — **the undecomposed floor, which is the ± figure the page
publishes**. It wrote no artefact. `docs/observability/value_cycle_ab_s1_noise_floor_20260903.json`
does not exist and never did.

The guest is ~24 GB (`background.resource_headroom.sample()["total_mb"]` — read, never quoted). Three
legs at a 6.4 GB peak is 19.2 GB before anything else on the machine, and two other seats were
running. At the kill, swap was down to 149 MB of 8 GB. `oom_kills_total` on this guest stands at 357,
so this is a standing condition and not an unlucky day.

## Why it is worse than a lost hour

**The failure is silent in the only place anyone looks.** `--out` names the artefact at launch; a run
that dies at 90 minutes leaves that path absent, and an absent path is exactly what a run still in
progress looks like. There is no exit code to read — the launcher returned long ago — and nothing
polls the unit's `Result`. The next session sees "no artefact yet", concludes the legs are still
going, and waits, or relaunches the same three-up configuration and loses another 1h 09m.

That is how this cost was paid twice already: the pre-registration filed earlier today estimated
"~2h24 each" from the 2026-08-29 log and budgeted ~8 hours for the four legs, on the assumption that
launching them in parallel buys wall-clock. On this guest it does the opposite — it converts three
finishing runs into two finishing runs and one that burns an hour and produces nothing.

## Why a check on free memory at launch would not have caught it

This is the part worth keeping. A floor leg **starts small and grows** across its hour. When the
third leg launched, the first two held about a gigabyte each and `MemAvailable` looked ample. Any
guard keyed to free memory *now* waves all three through and changes nothing.

The quantity that has to be compared is the **peak the running legs are collectively heading for**
against what the guest can ever offer them. On the numbers that actually occurred: three legs at
6.4 GB need 19.2 GB; the guest could offer 15 GB available + 2 GB already held = 17 GB. Refused,
correctly, at the moment of the third launch.

## The fix

Landed with this finding. `tools/run_value_cycle_ab.py` gains `floor_run_headroom_refusal()`, called
before a noise-floor run starts:

- every floor leg already running is counted at the **measured** 6.4 GB peak (`FLOOR_RUN_PEAK_MB`,
  sourced to the systemd accounting quoted above, rounded DOWN — this number exists to refuse, and a
  requirement set above the true one refuses runs that would have finished);
- their current RSS is added back, because the sample already counts it as used;
- the caller's own peak is added on top;
- fails closed when `/proc/meminfo` cannot be read, and names its reason on stdout;
- `--ignore-headroom` overrides, for a guest that actually grew.

`running_floor_legs()` reads `/proc` directly and excludes this process **and its ancestors**. Not
`pgrep -f`: the string that identifies a floor leg is the string a session writes when it talks about
one, so a cmdline grep matches the process asking the question and reports a leg that does not exist
— which would make the refusal fire forever on an idle guest, i.e. make the bound unmeasurable. That
is the same failure class as the thing being prevented.

Mutation-proved, five legs, each with a sole-witness subject: dropping the running-leg term from the
requirement; refusing unconditionally (the PASS branch must stay reachable or no floor can ever run
again); failing open on an unreadable `/proc/meminfo`; failing open on an absent `MemAvailable`;
dropping the self/ancestor exclusion from the census.

**One of those mutations survived on the first attempt and the test was wrong, not the code.** The
census test asserted `os.getpid()` was absent from the census on the live `/proc` and its docstring
claimed this process's command line contains the pattern. It does not — pytest's cmdline carries
neither `run_value_cycle_ab` nor `--noise-floor-seeds` — so the assertion was vacuous. Rewritten to
drive a fake `/proc` in which this process's own entry **does** match, which is the only arrangement
where the exclusion is the thing being measured. Recorded because "the mutation survived, so I fixed
the test" is also what it would look like if the code had been right and I had weakened the control.

## What is still owed

The `all` leg must be re-run **alone**, after the two survivors finish, and the four legs promoted
together. Until then the page's contrast and its bound come from two worlds. `se-floor-only-20260903`
and `se-floor-except-20260903` were still running when this was filed, at ~5 GB each with 4.4 GB
available — they may yet meet the same end, and if they do the same refusal is what stops the next
session from repeating the configuration.
