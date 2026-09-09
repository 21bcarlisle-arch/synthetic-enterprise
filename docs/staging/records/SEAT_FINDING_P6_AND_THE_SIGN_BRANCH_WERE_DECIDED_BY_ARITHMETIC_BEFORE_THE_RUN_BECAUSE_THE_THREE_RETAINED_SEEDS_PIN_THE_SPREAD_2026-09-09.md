**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — land the nine-seed floor through the witness path and grade its pre-registration beside it) · **Class:** controls_that_cannot_fail

# Two of the nine-seed run's seven predictions were decided before it started, because the three retained seeds pin the spread from below

**Written 2026-09-09T12:20Z, while PID 704091 is still in flight.** 14 of its 27 passes have
started; `docs/observability/value_cycle_ab_s1_noise_floor_20260909b.json` does not exist.
**Nothing below is a reading of that run's output.** Every input is quoted from
`docs/observability/value_cycle_ab_s1_noise_floor.json` (generated 2026-09-09T06:57:00Z) and from
`site/data/value_arms.json`, both on disk before the run was launched.

This is filed *before* the answer for the same reason the correction it extends was: a statement
about what a prediction can do, made after the prediction's result is known, is worthless.

---

## The claim

**P6 cannot be refuted by this run, and `_sign_determined` cannot fire on this artefact.** Both
follow from one property of the run's own design — the three original seeds are re-run and
**retained** — and neither depends on anything the six new seeds return.

## The derivation

The run keeps seeds 11111 / 22222 / 33333 and adds six. P2 predicts the old three reproduce to the
penny: **+1,260.93 / −3,036.25 / +494.45**. Take P2 as given for a moment (it is graded separately
below).

For a nine-point sample containing three fixed values, the sample standard deviation is minimised
when the six free values all sit at the mean of the three fixed ones. Writing the three as `x_i`
with mean `m₃` and the six free values at `m`, and putting `u = m − m₃`:

    Σ(x − x̄)² = 2u² + Σ(x_i − m₃)²

which is minimised at `u = 0`, giving `Σ(x − x̄)² = Σ(x_i − m₃)²` — the three fixed rows' own sum of
squared deviations, **unchanged by adding rows**. So

    m₃ = −426.9579
    Σ(x_i − m₃)² = 10,506,350.52
    sd_min(n=9) = √(10,506,350.52 / 8) = **£1,145.99**

attained only if all six new seeds return exactly −426.96.

*Checked two ways, because an arithmetic refusal that rests on one derivation cannot be refuted.*
A 200,000-draw random search over the six free values on [−4000, +4000] bottomed out at £1,162.16,
and a scan holding all six equal reproduced **£1,145.99 at v = −427.0**, matching the analytic
result to the penny.

## What that decides

**P6 — "the page still refuses to state a direction".** The page's gate is
`_resolvable(point, spread)` = `|point| > stdev`, over `realised.split.selection_gbp` = **+£319.10**.
It needs `stdev < £319.10`. The arithmetic minimum is £1,145.99 — **3.591× the threshold**. There is
no assignment of the six new seeds that lets the page state a direction.

P6 must therefore be graded **"held, and held vacuously — decided before the run"**, not "held, as
predicted". Grading it as a prediction that survived a test would be this repository's own named
defect one document along: a control keyed to an answer it could not fail to give.

**This sharpens the 10:13Z correction rather than repeating it.**
`SEAT_FINDING_THE_ERROR_BAR_CONTROL_AND_ITS_OWN_PREREGISTRATION_WERE_BOTH_GRADED_ON_A_QUANTITY_THE_PAGE_DOES_NOT_GATE_ON_2026-09-09.md`
priced the chance of the gate opening at **1.4 × 10⁻⁶ at n = 9**, treating the sample sd as a draw
from σ = £2,291.98. That framing was right about the decision it drove (do not buy the 116-seed
run) and **understated its own case**: conditional on the three rows being *retained rather than
re-drawn*, the probability is not small, it is **exactly zero**. The earlier figure is not corrected
— it answers a different question, "what if all nine seeds were fresh" — but the run that was
actually launched is not that experiment.

**The sign branch.** The same correction flagged that `_sign_determined` becomes an independent
branch for the first time at n ≥ 5, and that a `no_sign` clause appearing after publish would be
"the branch working, not a regression". On *this* artefact it cannot appear: `_sign_determined`
returns True only when every row falls on one side of zero, and the retained three already straddle
it (−3,036.25 against +1,260.93). It is **False by construction**, whatever the six return. So the
absence of a `no_sign` clause after publish is likewise not evidence about the branch. The branch is
live in general and unreachable here, and those are different states.

## What is still genuinely open, with its falsification window stated

The run is still worth its hours — for reason (1) in that correction, σ at 8 degrees of freedom
instead of 2. And three predictions remain live:

| | condition on the six new seeds | open? |
|---|---|---|
| **P2** | the old three reproduce to the penny | **live, and it is the load-bearing one** |
| **P3** in [−900, +900] | six-seed mean in **[−1,136.52, +1,563.48]** | **live** |
| **P3** refuted downward (mean < −2,291.98) | six-seed mean **< −3,224.49** | live, but this requires the six new seeds to average **below the most negative seed ever observed** (−3,036.25) |
| **P4** sd ∈ [1,200, 2,400] | lower half nearly forced: the floor is £1,145.99, only **£54.01** below the predicted bound | **upper half live, lower half nearly vacuous** |
| **P5** ≥ 5 of 9 positive | **4 of the 6 new seeds positive** (two of the old three already are) | **live, and untouched by any of this** |
| **P7** level share ∈ [0.90, 1.20] | untouched | **live** |

**P3's "the two cuts agree" branch — the outcome the delivery item names as the one that would make
the negative selection sign a finding about the arm — requires the six new seeds to average worse
than the worst seed the instrument has ever produced.** That is not impossible, and it is worth
saying out loud before the answer that it is the far tail of the two branches, not an even bet.

**Everything above is conditional on P2, and that is what makes it falsifiable.** If the three old
seeds do not reproduce, the fixed rows are not fixed, the £1,145.99 floor does not exist, and every
row of this document is void — which is precisely what the pre-registration already says P2's
failure would mean, and it would then be the deliverable ahead of any sign.

## The wedge check, which is why this was measured now rather than after

The same correction records that a control keyed to `2 · SEM` **would have gone red on the very
result this item was drawn to produce**, and a site red wedges every lane. That is a class, so it
was worth asking whether any *other* control reds at n = 9 before three more hours of compute
landed on it.

Four nine-seed floors were built from the real artefact's own rows and aggregated through the
producer's own `_spread`/`sem`/`distinguishable` arithmetic, each driving a gate to a state the
three-seed floor cannot reach, and each run through
`tests/tools/test_generate_value_arms_data.py` and
`site/test_the_baseline_comparison_reaches_the_reader.py`:

| probe | n | mean | sd | floor key | page gate | all one side |
|---|---|---|---|---|---|---|
| A — sd intact (what P3/P4 expect) | 9 | −20.10 | 1,948.06 | False | False | no |
| B — floor key forced true | 9 | +2,524.35 | 2,492.55 | **True** | False | no |
| C — every row one side of zero | 9 | +989.49 | 332.64 | True | False | **True** |
| POISON — page forced to resolve | 9 | +319.00 | 2.74 | True | **True** | yes |

**264 passed, 1 skipped on every one of the four.** Nothing wedges.

**And the poison round is what makes that green mean anything.** "Everything passed" has two
opposite causes, and the second is that the probe never reached the code. It reached it: under
POISON the feed's `error_bar.spread_to_point_estimate_ratio` moves **7.183 → 0.009**,
`distinguishable_from_zero` flips False → True, and **`.headline` itself changes** — 25 feed keys
in all. The mechanism responds to the floor's contents; the suites simply do not constrain it in
this range. Module paths were confirmed to resolve to this worktree
(`/var/tmp/se-seat-executor/...`) and not to the shared tree before any of this was believed.

The canonical floor was restored by copy after every swap and its md5 re-checked
(`c79e03d72a1cc29c1e2574cfb4a74258`); no probe artefact is committed and no figure from one is
published anywhere.

## What is next

- **Grade P6 as vacuous, and say so in the result document**, quoting the £1,145.99 floor. The
  honest grade is not "held".
- **Do not read the absence of a `no_sign` clause as evidence** about `_sign_determined`.
- The general shape, which is not this turn's work: **a pre-registration over a run that RETAINS its
  earlier observations has predictions whose falsification windows are constrained before it
  starts, and nothing computes them.** The window is cheap arithmetic and it is exactly what tells
  a live bet from a decided one. Both the pre-registration and its own first correction missed it
  on the same document within six hours. Filed as a question for the seat's next orientation rather
  than minted, because the right scope may be one helper that prints the reachable range of every
  pre-registered quantity given the rows a re-run carries over.
