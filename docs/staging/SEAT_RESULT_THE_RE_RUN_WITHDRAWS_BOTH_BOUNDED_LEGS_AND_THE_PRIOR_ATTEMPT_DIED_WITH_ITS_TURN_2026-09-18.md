**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# Re-running the arms withdraws both bounded legs, and the first attempt died with the turn that launched it

**Filed:** 2026-09-18 · **Claim id:**
`the-two-arms-have-never-priced-the-same-population-and-the-page-says-they-have`
**Pre-registration:** `docs/staging/records/PREREG_GIVING_THE_LEVEL_ARM_THE_SUPPORT_BOUND_AND_WHAT_IT_MOVES_2026-09-18.md`
**The code and controls this grades:** `b329e702b`

---

## What was already landed, and what I re-verified rather than took on trust

`b329e702b` (04:55) landed the whole of the drawn item except the run: the shared support frontier
in `decide_margin`, five controls, and the three false sentences corrected in place. It asserts its
three unit controls were mutation-proven. **I re-verified that independently** rather than reading
the claim, in a clean `git archive` extract of HEAD with the support clamp deleted — the pre-fix
behaviour exactly:

```
3 failed, 17 passed
  test_the_two_arms_price_and_refuse_TOGETHER_across_the_whole_frontier
  test_the_level_arms_refusal_is_the_VALUE_ARMS_OWN_REASON
  test_the_support_clamp_is_NOT_reported_as_the_lawful_CEILING
```

Exactly the three named legs red and the other seventeen stay green, so this is not the
broken-simulation shape where a mutation moves both sides and proves nothing. The claim holds.

## Why nothing had been published: the first re-run died with the turn that launched it

`b329e702b`'s message and its finding's *"What is not yet done"* both say the re-run **is in
flight**. It was, when they were written. It was not by the time anyone could read them, and
nothing in the tree can notice the difference.

| evidence | reading |
|---|---|
| `/var/tmp/longjob-value-cycle-ab-20260918.log`, 9,067,981 bytes, last write **05:21:12** | stopped mid-leg |
| no process on this machine holds a descriptor to it (swept every `/proc/*/fd`) | the writer is gone |
| a completed three-arm log from the same runner (`..._20260910.log`) is 28,063,326 bytes | ~32% of a run's output |
| its last progress line is a term ending 2025-01-01, with **one** setup banner | it had finished ~one leg of three |
| no artefact at `docs/observability/value_cycle_ab_s1_three_arm_20260918.json`, nor in `/var/tmp` | the run produced nothing |
| `/var/tmp/three_arm_20260918.log`, 4,380 bytes, last write 04:13 | a second attempt that died inside setup |

The last write is **05:21:12**; this turn's seat process started at **05:21**. The run stopped
within seconds of the previous turn ending. I did not observe the launch, so I cannot distinguish a
shared process group from an explicit kill, and I am not going to claim which — the remedy is the
same either way and it is in the next section.

**4,380 bytes is not "barely started", it is *nothing measurable done*.** My own relaunch sat at
exactly that byte count for fourteen minutes at the same point, so that is the setup phase before
the first settlement period. The 04:13 attempt got that far and no further.

## What the run actually costs, measured, and why a bounded invocation cannot hold it

Priced against a completed sibling run rather than estimated:

* **setup runs once per leg, not once per run** — `grep -c "=== Processing terms chronologically ==="`
  on the completed 09-10 log returns **3**, and `"NBP daily records"` also returns **3**;
* setup in this worktree costs **~14 min** per leg (measured: the log held at 4,380 bytes from
  05:24 to 05:38);
* the settlement loop runs at **22,786 periods/s** (measured over 90s: 2,686,000 → 4,736,800),
  and a leg is ~8,060,000 periods from the sibling leg — **~6 min** of loop;
* so **~20 min per leg, ~60 min for three.**

That is longer than the window of the invocation that launched it, which is the whole defect. This
turn's run is `setsid`-detached with **SID == PID == 1414666**, so it outlives this turn by
construction:

```
python3 -u -m tools.run_value_cycle_ab --level-arm \
  --out /var/tmp/value_cycle_ab_s1_three_arm_support_20260918.json
  launched 05:24:01 · log /var/tmp/longjob-three-arm-support-20260918.log
```

## THE RESULT: the re-run does not move the bounded legs, it WITHDRAWS them

This is measured, and it is measured on a question that is not the run's numbers — the publisher's
structural response to a point estimate *newer than its floor*. I took the published artefact,
bumped only `generated_at`, and asked the publisher's own functions:

| | as published (point 09-10) | after the re-run (point 09-18) |
|---|---|---|
| `_seed_spreads(...).available` | `True` | **`False`** |
| `_floor_admission(...).rule` | `stamp_proxy` | `stamp_proxy` |
| `_floor_admission(...).admitted` | `True` | **`False`** |
| `_staleness_caveat(...)` fires | no | **yes** |

`_legs_on_one_bar` republishes `_seed_spreads`' refusal verbatim when it is unavailable, so **all
three bounded legs go unavailable together** — by that function's own design, because every leg is
graded off the same seed rows.

**So the drawn item's expectation needs correcting, and the correction is not a disappointment.**
The item says *"Expect the LEVEL leg to move — it is the one published figure currently stating a
confident sign, and moving it is the point."* The level leg's sign (`positive`, 63.0 standard
errors from zero) is **not** a reading of the three-arm run at all: it is the mean of the folded
**18-seed floor family**, and `single_run.gbp` is the only part of that block the three-arm run
supplies. A re-run cannot move that sign. What it does is make the floor older than the figure it
bounds, and the guard then refuses the pairing. The level leg stops stating a sign — it does not
state a different one.

That is the fail-closed answer and it is the right one. A post-fix point estimate inside a pre-fix
seed family is the pooling defect this project has shipped before: the 18 seeds were drawn where the
level arm priced 65 renewals the value arm refused, and the new figure is drawn where it cannot.
`what_each_number_is_over` says *"`single_run.gbp` is one member of the 18"*, which would have gone
false the moment the new run landed. The guard refuses before that sentence can be published.

> **CORRECTION, filed beside the claim (2026-09-18, same day).** Two numbers above name the wrong
> floor artefact. The live `NOISE_FLOOR_PATH` is
> `value_cycle_ab_s1_noise_floor_folded18_single_arm_20260917.json`, stamped **2026-09-17T21:39:28Z**
> — not `..._folded18_20260917.json` at 15:14:19Z, which is a *different* folded-18 family (the
> pooled-arm one) and is not what the page reads. The refusal fires identically either way, because
> both predate the re-run, so **the result is unaffected**; the citation was wrong and is corrected
> here rather than silently edited above. Found by reading `NOISE_FLOOR_PATH` at line 316 while
> repairing the doors, not by anything going red — nothing checks a finding's citations.

**The floor's own admission was never strong enough to see this.** `_floor_admission` pairs on the
floor's *declared* book identity — and the folded-18 floor's `book_identity.declared` is **`null`**,
so it was only ever admitted on the stamp proxy. A declared book would not have caught this either:
the declared book is the book the run was *given*, which the arm fix does not change. The thing that
moved is the **priced** population, and no pairing rule on this page can see it. The stamp ordering
catches it here by luck of direction, not by construction.

## What this means for "republish both legs"

Both legs are republished **as point estimates from the new run**, and their bounded signs are
**withdrawn with a named reason** until the floor is re-run on the post-fix tree. That is the
honest reading of the item's "done means", and it is a narrower claim on the page than what is
there today, not a wider one.

Two published figures the item cites are **not** touched by this run, and a reader should not expect
them to move:

* `current_world.selection_gbp = £270.21` — the £270 residual the item names — is read from
  `CURRENT_WORLD_THREE_ARM_PATH`, pinned to `value_cycle_ab_s1_three_arm_20260908.json`. Repointing
  that constant is a separate decision with its own history in the source (it was tried and
  reverted once already), and it is **not** done here.
* `error_bar.contrast_bounds.*` are the floor family's own figures and move only with the floor.

## Owed, and deliberately not done here

**Re-running the folded-eighteen floor on the post-fix tree is 54 full passes** (~18 hours at the
rate measured above) and it is what restores a sign to either leg. It was already named as separate
work in `b329e702b`'s finding; this result adds the measurement that makes it *blocking for the
signs* rather than merely owed — until it runs, the page states no direction for the level leg or
the selection leg.

## What would refute this result

If the completed run's artefact carries a `generated_at` **earlier** than 2026-09-17T15:14:19Z, the
staleness branch does not fire and the legs survive — the probe above would then be measuring a
case that cannot arise. The run started 05:24 on 2026-09-18, so this is a formality, and it is
written down because a prediction that cannot be wrong is not one.
