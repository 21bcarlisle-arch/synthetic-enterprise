**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# RESULT: the tenth suite cannot see the subject, and the caller it tests has no test of the path that calls it

**Measured 2026-09-06 04:51–05:01 BST. Delivery seat, claim `fuel-mix-tenth-suite-reachability`.
Pre-registered at `docs/staging/SEAT_PREREG_WHAT_THE_TENTH_SUITES_POISON_ROUND_AT_THE_LIVE_FINGERPRINT_WILL_SHOW_2026-09-06.md`
(with its 04:45 mechanism addendum), landed BEFORE the poison pass wrote a cell.**

## The measurement

Spec fingerprint **`d7eb36a0b901`** — the live one, `tools/grid_intensity_feed_contract_battery`
at `1c9a08792`. Results file `/var/tmp/grid_intensity_fuel_mix_battery_d7eb36a0b901.json`.

| round | suite | result |
|---|---|---|
| baseline | `tests/tools/test_ep13_embedded_generation_bound.py` | `rc=0 failed=0`, **623.1s** |
| poison | `tests/tools/test_ep13_embedded_generation_bound.py` | **`reaches_subject: false`** — NEVER REACHES, `rc=0`, **609.3s** |
| poison | `tests/background/test_delivery_lane.py` (control) | stayed green, 2.0s |
| poison | `tests/design/test_atom_notes_store.py` (control) | stayed green, 1.8s |
| null | `tests/tools/test_ep13_embedded_generation_bound.py` | **`grades_text: false`** — `22 passed`, 609.5s |

The run ended cleanly: `END 2026-09-06 05:11:32 BST rc=0`.

**All four pre-registered predictions held.** 1 (`reaches_subject: false`) ✓. 2 (both controls
green, so the floor discriminates rather than reddening nothing) ✓. 3 (`grades_text: false`) ✓.
4 (baseline green at 623.1s; poison 609.3s and null 609.5s, both inside the 545–665s band) ✓.

This is the answer `/var/tmp/grid_intensity_fuel_mix_battery_95c9da4db380.json` already carried.
The point of re-buying it was **provenance**: `95c9da4db380` is the fingerprint of no committed
spec, and this one is reproducible from `1c9a08792`.

## THE DECISION: the ~2h grading run is NOT bought

Per the rule stated before the answer. Eleven mutation rounds at ~610s each is **~112 minutes** to
write eleven cells whose value the poison round already determines — each would arrive stamped
`survived_but_unreachable`, which is the engine's own words for *proves nothing*. Paying two hours
to record a value that is known in advance is the purest form of the thing this instrument exists
to find.

The claim is released on that basis. Nothing about `fuel_mix`'s ten contracts is left unmeasured
that this spend would have measured.

## What it cost to learn, and what that says about the instrument's own economics

Two runs died before one finished, and neither death was the battery's fault:

- **PID 1448564** (03:06) graded nine suites at an uncommitted spec that cannot be reconstructed —
  the reason this round existed at all.
- **PID 1675351** (04:31) banked the baseline and was **killed at ~18 minutes, mid-poison-pass,
  exit 130**. It was launched from the delivery seat's own bounded invocation, and
  `/proc/self/cgroup` for that seat is `…/app.slice/seat-executor.service`: a
  `KillMode=control-group` teardown SIGTERMs every process in the cgroup whatever its PGID.
  Relaunched at 04:51 under `systemd-run --user --unit=fuel-mix-poison-tenth-suite`, verified into
  its own cgroup, it completed the pass in 609.3s.
- **The subject was restored correctly through the kill** — `tools/generate_grid_intensity_feed.py`
  in the shared tree came back byte-identical to the pristine copy. The engine's `atexit`/signal
  restore did its job on a `SIGTERM` it did not choose, which is the case it was written for.

**The battery's per-suite checkpointing is what made the second death cheap.** `_baseline`,
`_poison` and `_null_round` each write the whole results file after every suite, so the 623s
baseline survived the kill and the relaunch resumed straight into the pass that mattered. That is
worth naming as a property, because the same design is what let the 04:31 run cost 18 minutes
instead of 30.

## The finding this actually produced

The reachability answer is bookkeeping. Underneath it is a defect in the tree:

> **`tools/ep13_embedded_generation_bound.measure()` is executed by nothing but `main()`, and no
> test runs `main()`.**

`measure()` (line 516) is the rung that loads the real caches, calls `fuel_mix()` at line 527, and
produces `docs/observability/ep13_embedded_generation_bound.json` — a published artefact. Its only
caller is `main()` at line 614. The suite's entry points are `measure_year`, `day_mean_series`,
`fit_surface_nd`, `apply_surface_nd`, `build_coordinates`, `verdicts`, `within_day_deviation`,
`oracle_is_unreachable_from` and the `held_out` fixture; **`measure` is in the transitive call
closure of none of them.**

**The name collision is how it hid.** The suite defines its own helper `_measure` at
`tests/tools/test_ep13_embedded_generation_bound.py:88` — six call sites, 623 seconds of runtime —
and it calls `measure_year` on synthetic worlds. A reader scanning for coverage of `measure` finds
`_measure` everywhere and stops. `grep` for the name is satisfied; the mechanism is untouched.
This is `no_caller_and_never_runs` wearing `controls_that_cannot_fail`'s clothes: 623 seconds of
green that never touch the function that writes the published file.

So the honest reading of the tenth column is not *"a suite that happens not to reach the subject"*.
It is *"the one path by which this caller calls `fuel_mix` has no test at all"* — and that is the
thing the two hours would have spent 112 minutes rediscovering one green cell at a time.

## What is NOT established

- **The null round's green is weak evidence and must not be read as a clean bill.** It returned
  `grades_text: false` — but a suite green in every round is green in the null round too, and this
  suite demonstrably reads the subject's bytes at test line 291. What it establishes is that the
  null marker is not an import of the oracle. It does not establish that the suite ignores the
  subject's text, and the source says it does not.
- **`survived_all` stays `None` for all eleven rows, permanently.** `353d0e910` made the verdict
  three-valued, so the JSON now says `null` with `ungraded_callers` naming this suite — honest,
  where `false` read as "proved". But a column nobody will ever buy means no row of this spec can
  ever carry a caller verdict. Whether the caller population should exclude a suite the poison
  round proved blind is a real question about the engine, and **it is deliberately not answered
  here**: dropping the column would delete the finding above, which is the most valuable thing
  this subject produced.
- **Whether that suite could catch `fuel_mix` failing is unknown, not ruled out.** The spec
  declares no `hard_poison`, so the second floor does not exist for this subject and the engine
  says so in its own summary. What is established is *"this suite runs no path that imports the
  subject"*.
- **Poison-green does not imply mutation-green in general.** For a suite that never imports the
  subject nothing done to it can redden the suite; but this suite reads the subject's TEXT, and a
  text-grader can redden for an edit the poison never made. What closes the gap here is
  per-mutation and not a theorem: the only text assertion is *"the feed does not import the
  oracle"*, and no mutation in `MUTATIONS` adds such an import. **A twelfth mutation would have to
  re-make that argument.**

## The other thing this cost

`grep -rln systemd-run tools/ background/` returns three bespoke sites and no shared launcher, a
week after that was written down as the reason long jobs keep dying here. This turn made a fourth,
in `/var/tmp`. Every long job on this box re-invents the transient-unit launch, and the ones that
re-invent `setsid` instead die — `setsid` changes the session and the process group, and the killer
is the cgroup. That is `tools/wait_for.py`'s missing other half: R18 made **waiters** name a subject
and carry a deadline, and nothing yet makes a **launcher** outlive its launcher. Handed on rather
than built here, because it is not what this claim was drawn for.
