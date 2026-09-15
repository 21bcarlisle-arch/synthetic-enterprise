**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

**Knowledge:** none — this is a provenance/harness state, not domain understanding.

# The floor's pin named the commit that LANDED the run, not the one that PRODUCED it

**Found 2026-09-10T14:5xZ** while holding the Lane 0 item *"pair-move the 20260910 run and its floor
so the independent grading reaches the page"*, ~5h before the floor it concerns finishes. Nothing is
broken by it and nothing was re-run because of it; it is written down so the **next** floor is
pinned correctly, and so the next seat does not repeat a justification that is not true.

Pre-registration and measurements:
`docs/staging/records/SEAT_PREREG_WHAT_THE_20260910_PAIR_MOVE_CHANGES_AND_WHICH_PAIR_THE_BOUNDS_COME_FROM_2026-09-10.md`.

## The premise is NOT spent

Both commits the item cites are ancestors of `origin/main`, but the move itself has not happened:
`docs/observability/value_cycle_ab_s1_three_arm.json` is still the 09-09T13:58:12Z run and
`..._noise_floor.json` still the 09-09T15:17:31Z floor. `longjob-noise-floor-20260910` (PID 1072649)
was **~3 minutes old**, not nearly done, when this turn opened — it started 2026-09-10T14:50Z and
runs ~5h. `launch_liveness --check` PASS, headroom 17.6 GB of 24 GB, no headroom refusal.

**The pair move is still owed and still correct to do.** It is simply not doable inside this turn.

## The finding

The item justifies the pairing this way:

> *"The floor was launched in a worktree pinned to the run's OWN commit 4e7938f67, so the two share a
> book by construction rather than by a git-diff argument."*

**`4e7938f67` is not the run's own commit.** The 20260910 run records:

```
producing_commit.commit       = 9cf9d16edfe3362751dc115edb0c038bc31bfe9e
producing_commit.resolved_at  = 2026-09-10T13:28:13Z
```

`4e7938f67` is the commit that **landed the artefact**. The two are different by construction and
the field's own docstring says so: *"resolved at process start, when Python bound the modules this
run executed — **NOT at artefact assembly, which is a later tree**"*. A run that takes hours is
always committed by a later commit than the one that ran it, so the landing commit is the one a seat
naturally reaches for and it is always the wrong one.

`/var/tmp/se-floorrun-20260910` is pinned to `4e7938f67`, and `run_value_cycle_ab.producing_commit()`
resolves by `git rev-parse HEAD` at process start. So **the floor will stamp `4e7938f67` and the run
it bounds carries `9cf9d16ed`**, and `_floor_tree_pairing` will take its `same=False` branch.

### The conclusion survives — but on the argument the item said it was avoiding

The pairing is sound. It is sound because of a git-diff argument, which I ran:

```
git diff --name-only 9cf9d16ed 4e7938f67 -- simulation/ company/ saas/ tools/ interface/ background/
  → empty
```

The whole diff touches `docs/`, `site/` and `tests/` only. **Not one byte of executed producer code
differs between the two candidate pins.** So the floor and the run were drawn by identical code; the
artefact simply cannot say so.

## Why the run was NOT killed and re-pinned

Re-pinning was live for about ten minutes and I decided against it. The reasons, in order:

1. **`same_tree=False` is already what the live page publishes.** Today's pair renders
   `same_tree=False` (floor `c066c114b`, figure `8b846013e`). The move does not introduce the amber;
   it carries an existing one forward with different hashes. There is no regression to avoid.
2. **`_floor_tree_pairing` renders, it does not gate.** Its two call sites (lines 1317, 7662) feed
   display dicts. `contrast_bounds` is admitted by `_staleness_caveat`, which the move *clears*.
   Measured: the pair move restores `contrast_bounds` to 7 keys / 3 contrasts and flips
   `is_it_available_today` to `true` — AUC 0.6236502960640892 on 120 scored decisions.
3. **The asymmetry.** Killing a healthy 5-hour job to change a 40-character provenance string risks
   the item's whole deliverable for a presentational gain on a caveat that is honest either way.

That is a judgement, not a rule, and it is reversible: the floor can be re-run pinned to
`9cf9d16ed` at any time for one more ~5h pass.

## What the amber will say, and the one sentence in it that is too narrow

The `same=False` branch will publish, correctly, that the two were *"drawn by DIFFERENT code"* and
that *"neither is thereby wrong and both name the same world"*. Its caveat then says the difference
is removed by **"only re-running the arms under the floor's tree"**.

That names one of two remedies and it is the expensive one. Re-running the **floor** under the arms'
tree is the same fix from the other end and is far cheaper — the floor is one job, the arms are
three. Not repaired here: it is the control's general prose, the control is otherwise keyed to the
property rather than to today's pair, and changing it is a code change on a page whose next landing
is meant to be a pure data move.

## The rule this generalises to

> **Pin a noise floor to the run's `producing_commit`, not to the commit that landed the run's
> artefact.** They are never the same commit for a job that takes hours, and only the first one
> makes `_floor_tree_pairing` able to say `same_tree: true`.

This is the cheap half of the owed work already filed as
`SEAT_FINDING_THE_NOISE_FLOOR_CARRIES_NO_BOOK_IDENTITY_SO_THE_PAIRING_RULE_IS_A_STAMP_PROXY_WRONG_IN_BOTH_DIRECTIONS_2026-09-09.md`.
That finding wants the floor to carry a book identity; this one observes that the floor already
carries a `producing_commit`, that the consumer already reads it, and that the only thing standing
between the page and a clean `same_tree: true` is **which commit the launching seat pins to**.

## What is next

The pair move itself, unchanged and still correct, once the floor lands ~2026-09-10T19:5xZ:
copy `value_cycle_ab_s1_three_arm_20260910.json` → `value_cycle_ab_s1_three_arm.json` **and** the new
floor → `value_cycle_ab_s1_noise_floor.json` **together**, re-run `tools.generate_value_arms_data`,
land the three paths in one commit. Expect `staleness_caveat: None`, `contrast_bounds` restored to 3
contrasts, `is_it_available_today: true`, and `same_tree: false` with the amber above.
