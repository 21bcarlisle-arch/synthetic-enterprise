**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The publisher knows its citation is dead and cannot say so, because the recorder is a module snapshot two hours older than its own repair — and the fleet detector built to catch that reads `stale 0`

Class: `publish_gate_and_wedge`. Measured 2026-09-25 06:18–07:05Z in the SHARED tree
`/home/rich/synthetic-enterprise` at HEAD `9d9008c85`, against a live gate cycle
(`process_run_complete` PID 2045699) that ran to completion during the measurement.

## What the RUNG-1 draw was sent at, and why it was never findable

The priority-zero draw names
`tests/background/test_stall_class_register.py::test_wedge_adapter_fires_past_the_directors_one_hour_bar`.
That test is **green**: 28/28 in the shared working tree (three runs), and 28/28 in a clean
`git archive HEAD` extract. Its subject module and its own file are byte-identical to HEAD —
neither `background/stall_class_register.py` nor the test has changed since `5987001f5`
(2026-08-03).

The publisher had already established this itself, four minutes before the draw's own last
recorded failure (`sim-runner-log.md`, 2026-09-25 06:33 UTC):

> Publish gate: the citation is `dead` — re-run at HEAD, all 1 cited red(s) PASS — … so this
> citation is DEAD. **It is recorded here rather than in `blocking_tests`, where it would send
> the next reader at green tests.**

The red is real but **order-dependent**: the gate's own run at 06:29 UTC reported
`1 failed, 1674 passed, 8 skipped` with `assert (None is not None)` at
`test_stall_class_register.py:290` — i.e. `detect_publish_gate_wedge` returned `None` as test
#1675 of the scoped suite, in a process where 1674 tests had already run. It does not return
`None` standalone. **A red that exists only in suite order, cleared by a citation re-check that
runs standalone, is a red no reader can be sent at.**

## The recorder cannot name the cause, and the reason is not in the code

`background/process_run_complete.py` at HEAD has the sixth-cause branch
(`rc == EXIT_SCOPED_GATE_REFUSED`, landed `4a030f9f5`, **2026-09-24 08:22Z**). It exists to stop
exactly this: its own comment says the generic fallback records `"cause": "unattributed" …` on a
cycle "whose own blocking record, written four minutes earlier by the same process, named one red
test". The disk copy carries it — 10 occurrences of `EXIT_SCOPED_GATE_REFUSED`,
`git status --porcelain` clean against HEAD.

The record written by the live cycle at **06:33:19Z on 2026-09-25**, twenty-two hours after that
repair landed:

```
ts      2026-09-25T06:33:19Z    rc 81    kind test_regression
cause             unattributed
cause_evidence    "recorded with no observation attached (rc=81, kind=test_regression) --
                   this exit path names no cause, so which one it was is NOT established here"
blocking_tests    []            total_red 0
```

That is the **generic** branch's wording, verbatim, for an rc the sixth-cause branch handles
above it. The child process runs the disk file; the **parent** — `background_worker.py`, which
reads the child's rc and calls `record_publish_gate_outcome` — does not. It booted at
**2026-09-24 06:10:33Z** and holds the module snapshot Python cached then: **2 hours 12 minutes
before the repair landed**.

`record_publish_gate_outcome` has exactly two production callers — `background_worker.py:561` and
`sim_runner.py:548` — and both reach it through `background/publish_outcome_route.py:71`, whose
import is lazy but whose result `sys.modules` caches for the life of the process. **Both processes
booted within one second of each other at 2026-09-24 06:10:33-34Z**, so whichever of the two wrote
the 06:33:19Z record held the pre-repair snapshot. There is no third caller outside `tests/`.

So the loop closes on itself: the gate refuses → the recorder cannot name which refusal →
`blocking_tests` is emptied → RUNG 1 re-fires on the stalest surviving citation, which the
publisher has already proved green. Fifty-nine consecutive failures, `wedge_since` 2026-09-21.

## The instrument built for this reads `stale 0`

`background/deploy_restart.py --report` exists to answer "which daemon is running code older than
a repair". Run at 06:45Z:

```
head 9d9008c85  observed 11  stale 0  unresolved 11  session-hosting 0
  background-worker  running 1.0d  code 7.2d  modules 0  MID-WORK  UNRESOLVED:stamp-predates-process
  … all 11 rows identical in the last field …
plan: restart 0 | defer 0 | hold 11
```

`stale` is `bool(changed)`, and `changed` comes from the boot-stamp comparison. When the stamp is
unusable the comparison yields nothing, so `stale` is `False` — and `restart_plan` holds on
`unresolved` with "unknown is not stale". Both halves are individually correct and fail-closed in
direction. **Composed, the summary line a reader sees is `stale 0` over a fleet where all 11 are
running snapshots a day old.** The `restart` limb has been unreachable for 21 days; `deploy_restart.py`
already says so in prose at its own line 754, and nothing keys a control to it.

The stamps on disk are dated 2026-09-17/18; the daemons booted 2026-09-24. The stamper itself is
**not** broken — `python3 -m background.boot_sha <session>`, the exact string the generated units
declare as `ExecStartPre`, was probed here at 07:31 local and wrote a correct record (removed
after). It was repaired at `ec1012c01`. The daemons simply booted from a checkout that did not yet
carry it, and `ExecStartPre` cannot run again without a restart — which `restart_plan` will not
order, because the missing stamp is the thing that makes it hold. **The condition is self-sealing:
the only act that repairs the stamp is the act the unusable stamp forbids.**

## Falsifiers — each one would refute a named claim above

1. A caller of `record_publish_gate_outcome` exists that booted AFTER 2026-09-24 08:22Z and could
   have written the 06:33:19Z record from an up-to-date module. *(Checked: the only two production
   callers are `background_worker.py` and `sim_runner.py`, both via `publish_outcome_route.py`, and
   both booted 06:10:33-34Z. Every other match in the tree is under `tests/`.)*
2. The generic wording is reachable for rc=81 in the HEAD copy. *(It is not: the rc==81 branch
   returns before the fallback.)*
3. `stale` counts an unresolved row. *(It does not: `"stale": bool(changed)`.)*
4. The blocking test is red at HEAD standalone. *(It is not: 28/28, twice, two trees.)*

## The remedy, in order — and why the order is the finding

1. **Restart `background-worker.service`** (not mid-cycle). This alone converts every subsequent
   rc=81 from `unattributed` into a named cause, because the repair is already on disk. It is the
   cheapest act here and it is what makes the wedge diagnosable at all.
2. Key a control to the **property** `deploy_restart` claims: a fleet in which no row can reach
   `restart` is not a green fleet, and the summary must publish `unresolved` where a reader looks
   for `stale`. A count that reads 0 because the question could not be asked is the fail-open case
   this file's own `read_boot_ts` docstring was written against.
3. ~~The order-dependent red itself is a separate subject and is NOT diagnosed here.~~
   **CORRECTED BESIDE THE CLAIM, 07:22Z — the census answered it and I was wrong about what it
   would find.** `tools/enumerate_publish_gate_reds` ran the gate's argv without `-x` at
   `7ef75772d` (1345s, `outcome: complete`, so this is an enumeration and not a fail-fast guess).
   It found **2 reds in 1 file**, and neither is the test the draw named:

   ```
   FAILED tests/background/test_the_publisher_classifies_the_tools_real_refusals.py
            ::test_a_red_gate_is_a_refusal_and_names_the_gate_that_refused
   FAILED tests/background/test_the_publisher_classifies_the_tools_real_refusals.py
            ::test_a_green_gate_over_a_changed_surface_actually_lands
   ```

   `test_wedge_adapter_fires_past_the_directors_one_hour_bar` is GREEN in that enumeration. It
   was the fail-fast gate's first red at 06:29Z and is not a red at `7ef75772d` at all — so the
   citation the draw carried was not merely dead, it was never the depth of the problem either.
   **DEPTH IS NOW ESTABLISHED at 2, which the draw's own "DEPTH UNKNOWN" clause asked for.**

   These two REPRODUCE STANDALONE, unlike the one the draw named, and their cause is in their own
   refusal text: `68717e7e1` (2026-09-25, "the landing door runs the message chain too") made
   `tools/git-hooks/commit-msg` a SECOND required chain in `surgical_land`, fail-closed —
   *"the MESSAGE gate is UNAVAILABLE: … An unavailable check is a FAILED check (R15)"*. The
   `repo` fixture in that test file builds only `pre-commit`, so both tests that drive a real
   landing refused before reaching their own subject. **The tool was right and the fixture had
   stopped describing a real repo.** Repaired in the same commit as this finding, by building the
   fixture from `surgical_land.HOOK_REL`/`MSG_HOOK_REL` rather than a retyped name, so a third
   chain wired later cannot red these two for a reason that is not their subject.

   Mutation-proven both ways: dropping `MSG_HOOK_REL` back out of the fixture's set reproduces
   exactly those 2 reds and no others (so the repair is load-bearing, not cosmetic), and making
   `surgical_land.land` refuse unconditionally reds all three tests in the file including the null
   control (so they can still see a total publishing outage).

Related, same mechanism, already filed:
`SEAT_FINDING_THE_DECLARED_BOOT_STAMPER_HAS_STAMPED_NOTHING_SINCE_2026_09_04_SO_NO_DAEMONS_CODE_VERSION_IS_KNOWN_2026-09-24.md`
(the stamper; now repaired in code and undelivered to any running process) and
`SEAT_FINDING_THE_SIXTH_CAUSES_INSTRUMENT_IS_ABSENT_FROM_THE_ONLY_TREE_THAT_WOULD_RUN_IT_2026-09-24.md`
(whose measurement — "0 occurrences in the shared working copy" — is now **refuted**: the symbols
are present on disk. The instrument is no longer absent from the tree. It is absent from the
process, which is a different fact with a different remedy, and that is this document's subject).
