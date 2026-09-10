**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

**Knowledge:** none — this is provenance and harness state, not domain understanding.

# The rival floor is a different SEED FAMILY, not just a different tree; and the floor in flight will land two commits ahead of the run it bounds

Filed against the Lane 0 item *"pair-move the 20260910 run and its floor"*
(claim `pair-move-20260910-after-the-floor-lands`), fourth successive draw. The premise is **still
unspent** and the pair move is **still blocked on the artefact** — that much repeats
`SEAT_FINDING_THE_PAIR_MOVES_FLOOR_IS_STILL_NOT_ON_DISK...` at `020b9e60d` and is not restated here.

What is new is four measurements, three of which correct a document or the drawn item itself.

---

## 1. The rival `_20260910b` floor uses a DIFFERENT SEED FAMILY — this is the real reason to refuse it

The drawn item says the rival run *"is NOT the pair-move source"* and gives the reason as the tree it
ran from (*"now 15 behind/9 ahead of origin/main"*). That reason is true but it is not the strongest
one, and a tree-distance argument invites a future seat to decide the distance is small enough.

The rival artefact **now exists** — the item was written while it was still running:

```
/home/rich/synthetic-enterprise/docs/observability/value_cycle_ab_s1_noise_floor_20260910b.json
  generated_at 2026-09-10T21:34:43Z   producing_commit 9f0ab066f
```

It is not in `/var/tmp`, which is why a `find /var/tmp` sweep (including the one in the previous
finding) reports it absent. `background.launch_liveness --check` names it correctly.

Its seeds are **six digits**. Every other floor's, and the run in flight's, are **five**:

| artefact | seeds |
|---|---|
| rival `_20260910b` | `111111 222222 333333 444444 555555 666666 777777 888888 999999` |
| canonical now (`_20260909b`) | `11111 22222 33333 44444 55555 66666 77777 88888 99999` |
| **run in flight** (`--noise-floor-seeds`, from its cmdline) | `11111 22222 33333 44444 55555 66666 77777 88888 99999` |

**So the two 2026-09-10 floor runs do not share a single seed.** The rival is not a slower or
faster copy of the same measurement that a seat could substitute in a hurry — it is a different
draw, and its spread is not comparable seed-for-seed with any floor this project has published.
`generate_value_arms_data`'s own note (the `NOISE_FLOOR_PATH` block, on the 09-08/09-09 pair) turns
on exactly that comparison: *the SAME seed in the SAME world returns a DIFFERENT `selection_gbp`
under two trees*. That diagnostic **cannot be run at all** between the rival and anything else,
because there is no shared seed to hold fixed.

**The refusal is therefore not a judgement about tree distance and should not be recorded as one.**

## 2. PRE-REGISTRATION, filed before the artefact exists: the floor will name `4e7938f67`, two commits ahead of the run it bounds

The floor run's cwd is `/var/tmp/se-floorrun-20260910`, whose `HEAD` is `4e7938f673…`. The producing
commit is resolved *at process start* (the artefact's own `resolved_when` says so), and that process
started 2026-09-10T14:50:22Z with that worktree already checked out. So:

> **Prediction:** the artefact will carry `producing_commit.commit = 4e7938f673be871dcd52faa413a9ba8b9167a8d4`.
> The run it will bound, `value_cycle_ab_s1_three_arm_20260910.json`, carries `9cf9d16edfe336…`.
> `git rev-list --count 9cf9d16ed..4e7938f67` = **2**, and `9cf9d16ed` is an ancestor.

**Recorded now so it cannot be fitted afterwards.** If the artefact names something else, this
paragraph is wrong and the reason is worth more than the pair move.

This is a two-commit floor/run code gap, not a zero one. **It is not a reason to withhold the pair
move** — the status quo pair is mismatched too (`c066c114b` floor against a different run) — but the
next seat should state the gap rather than let the page imply the floor was measured on the run's
own tree. This is the same class as
`SEAT_FINDING_THE_FLOORS_PIN_NAMED_THE_COMMIT_THAT_LANDED_THE_RUN_NOT_THE_ONE_THAT_PRODUCED_IT_2026-09-10.md`.

## 3. The regenerate leg is numerically EMPTY, so the pair move is a clean one-variable experiment

Measured, not assumed: `python3 -m tools.generate_value_arms_data` was run in this worktree against
the **committed** pair and the output diffed against the committed feed.

```
site/data/value_arms.json | 10 +++++-----   (5 insertions, 5 deletions)
```

All five are `generated_at` and `publishing_tree_commit` (twice each, plus the `reading` sentence
that interpolates the latter). **No figure moves.** The feed was then restored.

**Therefore every numeric change in the four-path commit is attributable to the new floor alone** —
the regenerate leg contributes none of it. That is worth having established in advance, because it
is what makes the pair move interpretable at all: without it, a seat landing the commit could not
say whether a moved contrast came from the floor or from the generator.

It also gives the move a falsifier: **if the pair move changes no figure, the mechanism is refuted,
not confirmed.**

## 4. Corrections

**(a) The previous finding's "decelerating" reading does not hold.** At `020b9e60d` I wrote that the
marginal rate was 19.1 min/sweep against a 17.5 average, and called the run *"decelerating
slightly"*. The next sweep refutes it:

| reading | sweeps | elapsed from 14:50Z | avg min/sweep |
|---|---|---|---|
| 21:32:25Z | 22 | 402 min | 18.3 |
| **21:49Z** | **23** | **419 min** | **18.2** |

Sweep 23 took **≤16.6 min**, below both the average and the 19.1 marginal that produced the
deceleration claim. **One sweep is a weak sample and this does not establish acceleration either** —
what it establishes is that the previous marginal was noise read as a trend. Four sweeps remain;
at the 18.2 min/sweep average that is **~23:02Z**.

**(b) The drawn item names the wrong module.** It says `launch_liveness --check` under `tools.`;
there is no `tools/launch_liveness.py`. It is `python3 -m background.launch_liveness --check`.

**(c) The item's "both running units" is now one.** `arms-rerun-20260910b` finished at 21:34:43Z
(`Result=success`, `ExecMainStatus=0`). Only `noise-floor-20260910` is still running.

**(d) A non-finding, recorded so it is not re-investigated.** `launch_liveness --check` printed
`check: FAIL (1 launch record(s) claimed live and are not)` and the next invocation printed `PASS`.
That is **not** a fail-open: the first call reconciled the just-finished rival's record, and the
exit code tracked the verdict each time (the FAIL path is `return 1` at
`background/launch_liveness.py:557`). It reads like a fail-open only if the two runs are compared
without noticing the state changed between them, and an exit code read through a pipe
(`… | tail; echo $?`) reports `tail`'s status, not the checker's — which is how it was nearly
mis-filed here.

## 5. What is left

Unchanged from `020b9e60d` §4 and needing no further judgement: on the artefact's arrival, copy it to
the dated and canonical floor paths, copy `_three_arm_20260910.json` to the canonical run path,
`python3 -m tools.generate_value_arms_data`, and land **all four paths in one commit** from a
worktree on `origin/main`. The run half must not land without the floor half — that half-move is
column B of the item's own pre-registration and is strictly worse than doing nothing.

**Two things to state on landing, from §2 and §3:** the floor/run code gap is two commits, and any
figure that moves is the floor's doing.
