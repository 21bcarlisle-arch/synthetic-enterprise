**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Landings are not reaching origin: where the commit gate's hour goes (2026-11-22)

*Delivery seat, 2026-11-22, claim `the-commit-gate-finishes-inside-its-hour`.*

## Pre-registration (written 21:55Z, before attempt 3 of reg 6C was timed)

Three candidate causes, and what each predicts for the reg 6C landing (pid 134360, attempt 3,
hook started 21:34:11Z) and for the 18:40Z bounded landing refused at 19:40Z:

1. **Test-selection growth.** The pytest leg alone runs near the hour, CPU-bound, with no stall.
2. **Contention with s.12g** (admitted 19:32:32Z). Wall time far above CPU time for the gate's
   cgroup; memory/io pressure stall totals large; the same selection ran faster before 19:32Z.
3. **Full re-gating after disjoint origin moves.** Each attempt fits its hour, but the trunk moves
   inside every attempt, the compare-and-swap refuses, and each re-gate pays the whole cost again.

What I expect, stated now: (3) for reg 6C and something other than contention for the 19:40Z
refusal, because receipts after 19:32Z show the same pytest speeds as receipts before it. If the
attempt-3 pytest leg alone exceeds 40 minutes, (1) is a contributor and I will say so.

## What was measured

The gate keeps no record of how long each leg takes; there is no per-leg timing in the hook,
`pre_commit_test_gate` or the landing logs. The legs below are put together from process start
times (`ps -o lstart`), a 15 s process-tree sampler on pid 134360 (`/tmp/gate_probe/reg6c.log`),
the shared tree's reflog, systemd's per-unit accounting and the cgroup's pressure files.

### reg 6C, `land-reg-6c-erroneous-gains` (pid 134360, 6 paths, 173 test files selected)

| attempt | base | started | ended | wall | trunk moves inside it |
|---|---|---|---|---|---|
| 1 | d48ffb389 | 19:40:55 | lost, seeing 80d11db93 (20:24:43 - 20:47:17) | 44-66 min | 3 (19:53, 20:10, 20:24) |
| 2 | 80d11db93 | ~20:25-20:47 | lost, seeing ee82f4c3a (21:18:14 - 21:34:11) | 31-69 min | 5 (20:47, 21:09, 21:10, 21:17, 21:18) |
| 3 | ee82f4c3a | hook 21:34:11 | still running at 22:03 | see below | -- |

Legs of attempt 3, from process starts:

| leg | from | to | wall |
|---|---|---|---|
| extract, message chain, hook chain up to the test gate | (attempt start) | 21:34:24 | 13 s from hook start |
| test gate's structural checks + selection | 21:34:24 | 21:35:19 | 55 s |
| main pytest, 173 files | 21:35:19 | still running at 22:03:00 | >27 min 40 s, **24 min 11 s of it on CPU (87%)** |

Count of re-gates after origin moved: **2** so far (attempt 1 -> 2 and attempt 2 -> 3), each of
them a full re-run. The 9 paths the trunk moved between d48ffb389 and ee82f4c3a are **all
disjoint** from reg 6C's 6 paths: eight are docs and work items, one is
`tests/simulation/test_net_new_acquisition.py`.

Contention, measured on the unit's own cgroup: 11,167 s of CPU over ~126 min of wall time (more
than one core at times), memory-pressure stall total 7.4 s, io 12.4 s, MemoryHigh/Max unset. The
gate's pytest runs at 84-87% of a core on a 16-core box with load average ~6.

### the 19:40Z refusal, `land-se-seat-executor-1795372804` (the bounded-landing change)

| leg | wall |
|---|---|
| whole unit (extract + chains + pytest to 63%, killed at 3600 s) | 18:40:04 - 19:40:31, 3,627 s |
| CPU over the same window (systemd accounting) | **569 s (16% of wall)** |

52 of its 60 minutes ran **before** s.12g was admitted (19:32:32Z), so contention with s.12g
cannot explain it. It was not computing: with 16% CPU it was blocked for most of the hour, and the
log ends mid-run with no output for the last stretch. Its selection for these paths is 51-52 files
(re-derived with `select_targets`), smaller than reg 6C's. **What it blocked on is NOT
established.** I checked one hypothesis and ruled it out: that the gate's tests inherited the
turn's marker and handed off to a nested unit. The unit sets `SE_DETACHED_LANDING`, so
`in_bounded_turn` is false there, and the journal shows no nested unit started in that window. That
landing is owned by `re-land-the-bounded-landing-hand-off-if-it-did-not-reach-origin`, and a re-run
of it is the next reading.

### before s.12g against after it, same pytest leg (the receipts' own `tests:` line)

| landing | tests | pytest wall |
|---|---|---|
| 21 Nov 11:37Z (before) | 594 | 566 s |
| 22 Nov 18:50Z (before) | 1,912 | 718 s |
| 22 Nov 19:50Z (after) | 608 | 484 s |
| 22 Nov 20:24Z (after) | 594 | 431 s |
| 22 Nov 21:09Z (after) | 973 | 531 s |

The same-sized selection ran no slower after s.12g was admitted.

## The named cause

**Full re-gating after trunk commits that touch disjoint paths.** One reg 6C attempt (~45-60 min,
mostly a CPU-bound 173-file pytest) fits inside the 3600 s timeout. But the trunk moved every 15-30
minutes, so every attempt lost the compare-and-swap. Every retry then paid the whole selection
again, on a tree that differed from the one already gated green only in paths the movers brought.
No number of attempts could win that race.

Test-selection size is a contributor, not the cause: 173 files is what this change touches (the
billing suite is selected as a whole by design), and it fits in an hour. Contention is not the
cause: there were no stalls, and the pytest legs ran no slower after s.12g. **The 3600 s timeout is
not raised.**

## The fix (tools/surgical_land.py)

A lost race now writes the commit of the tree it gated GREEN (unreferenced, like the one git's own
CAS strands). The next attempt hands that commit to the gate through `PRE_COMMIT_GATE_MERGE_PARENT`.
The new tree is the merge of that green tree with the new base, so it is gated the way the hook
already gates a merge (`selection_paths`, since 2026-10-03): every structural check reads the whole
change, and pytest selects only the paths that differ from both sides. A disjoint move selects
nothing. A path the lane rewrote between attempts is selected again. A red verdict is never
carried. The receipt names the tree with `prior-green:`. What this gives up is the merge rule's own
stated cost, that a union of two green sides can be red, and nothing more. Mutation-proven in
`tests/tools/test_a_lost_race_regates_only_what_the_move_brought.py`.

Applied to reg 6C, attempt 2 would have selected no tests and taken minutes.

## Not closed here

- The gate records no per-leg timing, which is why this table had to be rebuilt by hand.
- The 19:40Z hour at 16% CPU has no cause yet (see above).
- reg 6C's own pid 134360 is still running the OLD code (it imported it at 19:40) and keeps
  re-gating in full. It was not touched.
