**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `OPS_stale_copy_and_landing_doors`

# Three of the five live reverts are cleared from the shared tree, and the two left are a REPLACEMENT the seat can decide but no door can enact

The Lane 0 item `land-the-weather-hdd-pile-written-twice-and-committed-never` was **already spent
at origin** before this turn began. `a2145439a`, `9ca0d887d` and `ce4a60430` are all ancestors of
`origin/main`, `HEAD == origin/main`, and the content is there and not just the SHAs: `git show
origin/main:sim/weather_hdd.py` carries `_premise_sky()` reading
`simulation.weather_inputs.cell_weather_for_customer_id`, and
`tests/sim/test_the_hdd_leg_reads_the_premises_own_cell.py` is at origin in full. The blocking
finding is in `docs/staging/done/`, both result notes are committed, and the claim
`ten-of-eighteen-premises-get-a-climate-normal-instead-of-the-worlds-weather` was bound to
`a2145439a` by the previous invocation.

What was NOT done, and what this turn did: the five revert copies the previous invocation
correctly *identified* were left sitting in the working tree. They were still there.

## What cleared

`python3 -m tools.refresh_to_head --write --slug hdd-pile-stale-reverts-20260922` over three
paths. All three are now clean against HEAD; the discarded bytes are recoverable from
`refs/preserved/refresh-to-head/hdd-pile-stale-reverts-20260922`.

| path | verdict | what its diff would have reverted |
|---|---|---|
| `sim/weather_ingestor.py` | `refreshable` | `LIMIT_RESET_SECONDS`, `CLEARABLE_BY_BACKOFF_SECONDS`, `reset_seconds` — the hourly-limit fix of 09-17 |
| `tools/build_weather_world.py` | `refreshable` | `_horizon_words` and the quota-stop path |
| `tests/sim/test_weather_ingestor.py` | `refreshable` | `test_the_hourly_limit_is_a_stop_and_not_a_retry_like_the_minutely_one` — the three-leg partition control |

Note the third row. The copy deleted **the control over the whole partition** while leaving the
two-limit copy of the code it grades. Landing that pile by pathspec would have reverted the fix
and the test that proves it in one commit, and the remaining tests would have stayed green,
because they were written against the two-limit classifier the copy restores.

## What did not clear, and why it is the finding

`simulation/premise_population.py` and `tests/simulation/test_premise_population.py` are the
memory-ceiling lane's subject, not the HDD lane's, and both are refused:

```
simulation/premise_population.py        [refused_supplies_names_head_lacks]
tests/simulation/test_premise_population.py  [refused_replacement_no_landable_hunk]
```

**The decision itself is not hard, and I have made it: HEAD wins, on both files.** The evidence is
three-sided and none of it is a preference.

1. **HEAD is the post-correction copy.** HEAD binds `PRODUCTION_PARENT_RSS_MB = 227.0` and
   `load_whole_run_rss_curve`. The working copy binds neither: it prices the probe's **child**
   only, which is precisely the defect
   `SEAT_RESULT_THE_CEILING_WAS_PRICING_ONE_CHILD_NOT_THE_CGROUP_..._2026-09-22.md` was written to
   close. The working copy is the draft that correction superseded.
2. **The working copy's tests cannot run against HEAD.** They reach for
   `load_settlement_ceiling_slope` and `measured_whole_run_rss_curve`; HEAD binds neither name.
   Landing any hunk of that file lands a red.
3. **Its "new" names are superseded renames, not additions.** The copy supplies
   `WHOLE_RUN_FOOTPRINT`; HEAD carries `WHOLE_RUN_FOOTPRINT_POPULATION`. The rename is this
   repo's own recurring lesson applied — say what the number *counts* — and landing the copy's
   hunks 0 and 1 "because they add without deleting" would reintroduce a constant whose name
   omits the thing that makes it readable, alongside the one that does not.

**And there is no door that enacts it.** `refresh_to_head` refuses REPLACEMENT by design and says
*"Decide it, then land the winner deliberately."* That sentence assumes the winner is the working
copy. When the winner is **the base**, there is nothing to land — the enactment required is
discarding the working copy, and the only tool for that is `git checkout <path>`, which is
forbidden here, and `refresh_to_head` declines to be it:

> Refreshing it would discard an ordinary edit, which is `git checkout <path>` with a nicer name
> — and that is forbidden here for this exact reason.

That refusal is right for an *ordinary edit*. It is wrong for a copy the stale-copy control has
already judged `predates_landing`, where the clock has established the copy cannot be carrying
work built on the landing. `--superseded` does not reach either file: it relaxes exactly one class
(`SUPERSEDED_DEAD`) and both of these land in different branches.

So a REPLACEMENT resolved in the base's favour has **no legal exit**. It sits in the tree
permanently, wedging every lane that touches the file, and the stale-copy door refuses every
landing over it — which is the door working correctly and the tree staying stuck anyway.

## What this predicts, and it is falsifiable

The 22-path census is not draining. Three left it today by `refresh_to_head`; the ones that remain
will be disproportionately REPLACEMENT and SUPPLIES_NEW, because those are the two classes with no
exit. **Prediction, filed before the next census: re-run `tools.stale_copy_refusal --census` after
the next three landing attempts and the count will not fall below ~19 by refreshing alone.** If it
does, this diagnosis is wrong and the exit exists somewhere I did not look.

## The smallest mechanism that would close it

A `--base-wins` flag on `refresh_to_head`, admitting REPLACEMENT and SUPPLIES_NEW **only when the
stale-copy control has already returned `predates_landing` or `predates_landing_by_clock`** for
that path — i.e. only where the clock, not the operator, has established the copy is older than
the landing. Preservation already exists and is unchanged. The control that must be able to fail:
a copy that does NOT predate its landing must still be refused under `--base-wins`, or the flag is
`git checkout <path>` with a nicer name after all — which is the exact thing the docstring above
refuses to become, and the reason the flag needs that precondition rather than an operator's word.

Not built this turn: it is another lane's tool, it needs its own mutation-proven controls, and a
half-built door over a forbidden operation is worse than the wedge it removes.
