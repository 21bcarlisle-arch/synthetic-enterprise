**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `the-level-selection-retake-died-twice-and-its-own-correction-asserts-it-live`)

**Knowledge:** none new. This scores a pre-registered prediction and records a harness repair; no
domain constant moves.

# The re-take survived its fourth launch, and the split is a number that still cannot be read

Beside `SEAT_PREREGISTRATION_WHAT_THE_CURRENT_BOOK_RETAKE_OF_THE_LEVEL_SELECTION_SPLIT_CAN_AND_CANNOT_SETTLE_2026-09-07.md`,
`SEAT_CORRECTION_THE_FIRST_RETAKE_LEFT_NO_EVIDENCE_IT_SURVIVED_ITS_OWN_LAUNCH…_2026-09-07.md` and
`SEAT_FINDING_THE_RETAKE_DIED_A_THIRD_TIME_AND_THE_KILLER_WAS_NEVER_THE_SESSION…_2026-09-08.md`.
All three stand; none is edited.

---

## The premise the drawn item was written on is spent

The doorbell says *"two launches, two silent deaths, no artefact at any path"*. **There is an
artefact.** The transient-user-unit relaunch — launch #4, the one the third-death finding describes
as alive with a five-minute proof behind it — ran to completion.

| | |
|---|---|
| launched | 2026-09-08 00:32:23, `systemd-run --user --unit=value-cycle-ab-current-book` |
| finished | `END 2026-09-08T01:20:15+01:00 rc=0` — **48 minutes**, no kill |
| systemd's own verdict | `Result=success`, `ExecMainStatus=0` — held outside the job, uncollected on purpose |
| artefact | `/var/tmp/value_cycle_ab_current_book_2026-09-08.json`, 148,660 bytes |
| produced by | `04361d6c7`, resolved at process start |
| world | `39a192ce04c1eda8` — **the same digest the prereg names**, which is the branch it predicted |

**The cgroup diagnosis was right.** Three deaths under `setsid`, none under a transient user unit,
same job, same book, same machine. That is one clean observation and not a proof, but it is the
only launcher change between the fourth attempt and the three that died.

**And the waiter said DEADLINE, which is why nobody knew.** `tools/wait_for.py --deadline 300`
reported *"still waiting … 240s of 300s; pid 3661620"* and then deadlined — correct behaviour, and
for a 48-minute job it is an answer about the first five minutes and nothing else. The run then sat
finished, with its number in it, for an hour before anything asked again. That is the same defect
in its third costume, and the repair below is aimed at it.

## The four predictions, scored

The prereg was written before any run existed and is unedited. It went **4 for 4**.

| # | predicted | measured | |
|---|---|---|---|
| 1 | `value_advantage_gbp` lands **outside** the 09-03 run's £2,335.87; direction not signed | **£17,738.64** | ✅ |
| 2 | `level_gbp_per_mwh` will **not** return to 48.25 | **20.00** | ✅ |
| 3 | `level_share_of_advantage` will be **a number**, and it will **still not be readable** | **98.5%**, `readable: false` | ✅ |
| 4 | `no_observed_history` stays near its post-repair floor, does not return to 179 | **0** on all three arms | ✅ |

Prediction 3 was the load-bearing one and it was a prediction about the *page*, not the run. The
prereg named the branch precisely: *if this run's `world_identity` is still `39a192ce04c1eda8`, the
09-03 floor is admitted on its digest, its three sign-changing seeds are read, and `readable` comes
out `false`* — as against `null`, which is the weaker "not asked" state. The digest is unchanged and
the feed says:

> Across 3 re-draws of the same quantity in this same world — same book, same code, only the
> per-household price-sensitivity draw moved — **the level leg runs −£882 to £9,085 and CHANGES
> SIGN.** A leg that is not determined in direction cannot be expressed as a share of anything, so
> this world's single draw of that share — 98.5% — is one draw's arithmetic and not a composition.
> The share itself spans −60.1% to 2014.5% over those same draws.

## What this does NOT say, and the prereg saw this coming

**98.5% is not "the advantage is nearly all price level".** The prereg wrote, before the number
existed: *"Recorded here so that a later tick, holding a level-dominated result, cannot read this
lane's framing as licence to state it."* This is that tick. The share is unreadable for the reason
above, and it is one draw of a quantity whose own floor spans −60% to +2,014% in this same world.

**Nor may it be differenced against the 09-03 run's 6.8%.** More than one thing changed between
them — twenty-four files of book, the writer-3 gas repair, and `flat_at_level` takes its level from
**each run's own realised median margin** (48.25 then, 20.00 now), so the level arm is redefined by
its own result. Two figures whose difference is not attributable to anything. The page states this
in its own words rather than in a footnote.

**What did happen is that the book got much bigger to win or lose.** The advantage went from £2,336
to £17,739 on the same world digest, and the honest reading of a share moving in company with that
is how much book there is, not how much better the company chose.

## What landed

1. **The artefact is in the tree** at `docs/observability/value_cycle_ab_s1_three_arm_20260908.json`
   and `CURRENT_WORLD_THREE_ARM_PATH` points at it. It supersedes the 09-03 run *with provenance*,
   beside it and not instead of it.
2. **Two controls were keyed to today's answer and are re-keyed.** Both went red the moment the
   page became more honest, which is exactly backwards, and both are in `tests/tools/`:
   * `test_the_generator_reads_the_current_world_floor_from_its_own_constant` synthesises its floor
     and left it on the 09-03 clock. `_staleness_caveat` correctly withholds a bound whose error bar
     predates its point estimate, so the wiring assertion reddened for the calendar. The fixture now
     stamps the floor onto the point estimate's clock, exactly as it already stamps the world digest.
   * `test_the_creation_leg_carries_its_own_live_world_bound_and_not_the_advantages` asserted a live
     bound exists. It does not, and should not: **every floor on disk now predates the run this page
     publishes.** The control now asserts the age refusal on the real pairing *first*, by name, and
     puts the wiring on trial on a clock-stamped floor. It reds if the refusal's reason is anything
     other than age, and it goes quiet by itself when the floor leg is re-run.
3. **A launch record that can be re-asked** — `background/launch_liveness.py`, below.

## `background/launch_liveness.py` — the liveness half of the drawn item

The drawn item asks that *"a document reading 'in flight' is contradicted by something other than a
person checking a pid."* The subject is therefore the **claim**, not the job: `tools/wait_for.py`
already answers "is it alive right now" better than anything new could, and what it cannot do is be
asked again tomorrow by whoever reads the document.

A record names the job, its transient unit, the artefact it writes, and — the part that turns a
contradiction into an address — **the documents that assert it is live**. `--check` re-asks and
settles. Run against the real subject:

```
$ python3 -m background.launch_liveness --check
value-cycle-ab-current-book: FINISHED -- the artefact `/var/tmp/value_cycle_ab_current_book_2026-09-08.json`
  exists, the unit's Result=success and ExecMainStatus=0, and the job's own rc file says 0
  CONTRADICTS docs/staging/records/SEAT_CORRECTION_THE_FIRST_RETAKE_LEFT_NO_EVIDENCE… -- it says this run is in flight; it is not
  CONTRADICTS docs/staging/records/SEAT_FINDING_THE_RETAKE_DIED_A_THIRD_TIME… -- it says this run is in flight; it is not
check: FAIL (1 launch record(s) claimed live and are not)
```

**Systemd is asked first and the rc file only corroborates**, which is the whole design. The 09-07
relaunch wrote an rc file so "gone" could be told from "gone with rc=137"; it could not, because a
SIGKILL to the cgroup takes the wrapper that would have written it, so the file is absent in exactly
the case it was built to describe. *An exit-status file written by the process being killed cannot
report its own kill.* `test_a_group_kill_is_diagnosed_with_no_rc_file_and_no_artefact` is the
control for that: no rc file, no artefact, no exit code, `Result=oom-kill` — and the verdict must
still be DIED.

**It fails closed.** A probe that cannot be run returns UNREADABLE and settles nothing; so does
UNKNOWN. "We could not look" never renders as "it died" — that would be worse than the hand-check it
replaces, because it would settle a live claim on no evidence. Settling is one-way: a record never
returns to `live`. Nine controls, and the partition is asserted reachable before any leg's meaning
is (`test_every_verdict_is_reachable`), because a verdict function whose every branch refuses passes
every per-branch test written against it.

## What is still owed, in order

1. **The floor leg, and it is what the drawn item was really about.**
   `--noise-floor-seeds 11111,22222,33333 --redraw-mode all` on this same book. Until it runs, the
   page publishes a point estimate with the caveat *"the error bar is older than the figure it
   bounds"* — which is honest and is not an answer. **Launch it through a transient user unit and
   record it with `launch_liveness --record`**; that is now the route.
2. **A shared launcher.** Item 1 of the third-death finding's owed list is untouched: four bespoke
   shell scripts in `/var/tmp`, each re-discovering the cgroup by dying. `launch_liveness` records a
   launch; it does not perform one.
3. **Checkpointing.** Three deaths cost roughly five hours of wall-clock for zero figures because
   the tool writes its artefact once, at the end.

## Reversal

Every part is a file. Revert the commit; `CURRENT_WORLD_THREE_ARM_PATH` returns to the 09-03
artefact, which is still on disk and still honestly measured.
