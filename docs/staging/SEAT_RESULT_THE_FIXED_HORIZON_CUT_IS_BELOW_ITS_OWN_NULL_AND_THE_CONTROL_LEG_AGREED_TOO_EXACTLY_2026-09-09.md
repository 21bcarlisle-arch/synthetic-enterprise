**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — promote-the-09-08b-pair-and-give-the-fixed-horizon-cut-its-own-interval) · **Class:** measurements_that_mirror

# RESULT — the fixed-horizon cut is below its own null, and the control leg agreed too exactly

Grading `docs/staging/records/SEAT_PREREGISTRATION_WHAT_THE_FIXED_HORIZON_CUTS_OWN_NULL_INTERVAL_WILL_SAY_2026-09-09.md`,
filed before `concordance_null_spread` had ever been run on any leg of the bridge.

**Graded against `docs/observability/value_cycle_ab_s1_three_arm_20260909.json`** — the run the
pre-registration commissioned and named its address for. `generated_at` 2026-09-09T01:24:34Z,
`producing_commit` `62334dc76`, world digest `39a192ce04c1eda8` — **the same world as the 09-08b
run**, checked, so the leg-by-leg comparison below is one variable and not two.

---

## The four legs as measured

| leg | n | concordance | own 95% null | half-width | p | reading |
|---|---:|---:|---|---:|---:|---|
| 0 `the_published_population_ratio_outcome` | 168 | 0.5337857 | [0.4493929, 0.5503571] | 0.050482 | 0.1907 | not distinguishable |
| 1 `settled_only_ratio_outcome` | 124 | 0.4992769 | [0.4410334, 0.5581778] | 0.058572 | 0.9891 | not distinguishable |
| 2 `settled_only_pounds_outcome` | 124 | 0.5129503 | [0.4403103, 0.5587694] | 0.059230 | 0.66645 | not distinguishable |
| 3 `every_priced_decision_pounds_outcome` — **the estimand** | **161** | **0.4210267** | **[0.4458340, 0.5540430]** | **0.054104** | **0.0045** | **worse_than_chance** |

`null_constant_signal_concordance` is exactly 0.5 on all four.

## The six predictions, graded

| | Predicted | Measured | |
|---|---|---|---|
| **P1** | estimand's half-width between 0.050 and 0.075 | **0.054104** | **CONFIRMED** |
| **P2** | estimand reads `worse_than_chance` (0.4209 below its own lower bound) | 0.4210267 < 0.4458340 | **CONFIRMED** |
| **P3** | `p_two_sided` between 0.005 and 0.05 | **0.0045** | **direction CONFIRMED, stated range MISSED at the low end** |
| **P4** | legs 1 and 2 both `not_distinguishable_from_no_information` | 0.4993 and 0.5130, both inside | **CONFIRMED** |
| **P5** | leg 0 reproduces the concordance's interval within 0.005 **but not exactly** | agrees to **0.0 on both ends** | **CONFIRMED on the bound, REFUTED on the "not exactly"** |
| **P6** | point null exactly 0.5 on every leg; intervals differ between legs | 0.5 on all four; four distinct intervals | **CONFIRMED** |

### P3 — the range was missed, and it is recorded rather than re-drawn

0.0045 is below the stated floor of 0.005 by 0.0005. The headline claim — *below 0.05* — holds and
carries P2 with it. The floor was written to stop the prediction being unfalsifiable in the
flattering direction, and it was set slightly too high. Recorded here rather than widened.

### P5 — the control agreed too exactly, and that makes it a weaker control than it was designed to be

The pre-registration predicted the two intervals would differ in the third or fourth decimal,
because `concordance_null_spread` shuffles a list whose initial order differs between the two call
sites, making them two independent 20,000-draw samples of one distribution. **They agree to the
last bit on both ends.**

That is not a defect in the book and it is not a defect in the bridge — leg 0's population *is* the
concordance's, which is what P5 was built to check, and it passed. But the mechanism by which it
passed is not the one claimed: identical seed, identical draw count and an identical initial
ordering of the same points produce the identical permutation sequence, so leg 0's null and
`method_skill.null_spread` are **one computation performed twice, not two samples that agree**.

**So P5 cannot detect a defect shared by both call sites.** It discriminates a population mismatch
(different points → different shuffles → different interval) and nothing else. That is still worth
having and it is less than the pre-registration claimed for it. Named here so the next reader does
not take agreement-to-the-last-bit as independent corroboration.

## The "will not move" claim — the point estimates DID move, and the design could not have settled it

The pre-registration reserved this as a separate claim: *"If any of 0.5338 / 0.4993 / 0.5130 /
0.4209 moves in the run carrying this work, the change was not additive and the attribution of
everything above is void."*

**All four moved.** And the stated inference does not follow, because the grading design changed
two things at once — it added the permutation *and* re-ran the whole three-arm simulation. That is
this project's own rule about attribution, applied to a pre-registration I wrote.

The move is one half-pair unit, exactly:

| leg | pairs (both runs) | Δ concordance | Δ ÷ (0.5 / pairs) |
|---|---:|---:|---:|
| 0 | 14,000 | −3.571e-05 | **−1.000** |
| 1 | 7,606 | −6.574e-05 | **−1.000** |
| 2 | 7,606 | −6.574e-05 | **−1.000** |
| 3 | 12,194 | +8.201e-05 | **+2.000** |

`comparable_pairs` is identical across the two runs on every leg, so the populations are the same
size; a handful of individual pairs changed side. That is a fresh simulation pass over the same
world, not a code path that mutates its input.

**Additivity is provable independently, and was proved rather than assumed.** `_horizon_leg`
computes `concordance` from `points` at `tools/run_value_cycle_ab.py:2028`, before
`concordance_null_spread` is called at `:2042`; the spread function builds its own `signals` and
`outcomes` lists and shuffles a copy (`shuffled = list(signals)`), never touching `points`. Driven
directly: the points list is unmutated across the call and `_concordance` returns the identical
value before and after it. So the additive claim holds **by construction and by driving it**, and
the run-to-run movement is attributable to the book, not the change.

## What this settles, and what it does not

**Settles:** the estimand has an interval computed on its own 161 decisions and its own tie
structure, and it is **below** that interval at p = 0.0045. The claim the survivor cut could not
support — that the arm's price ranks joint value *worse than a signal carrying nothing*, once the
departures are admitted — is available from this run, on this cut, with its own bound.

**Does not settle, and this is the honest limit:** the interval is a permutation over decisions
treated as exchangeable, and these 161 are clustered on a few dozen accounts. The true interval is
wider than [0.4458, 0.5540]. The artefact's own `bound` prose says so and it renders with the
figure.

## What is next

1. **The 09-09 run has no noise floor, so it cannot be promoted and this interval does not yet
   render.** `docs/observability/value_cycle_ab_s1_three_arm_20260909.json` is on disk **untracked**;
   there is no `value_cycle_ab_s1_noise_floor_20260909.json` and no floor job is live
   (`launch_liveness --check`: PASS, no stale claim; no `longjob-*` unit). Promoting it without one
   republishes the headline contrast with no error bar — the documented defect this page already
   refuses. **Its floor is a run, not an edit, and it is the single thing standing between this
   measurement and the reader.**
2. Until then the publisher's withholding of `method_skill.fixed_horizon` on the promoted 09-08b
   pair is **correct and should not be edited around**: that artefact predates `62334dc76` and
   genuinely carries no per-leg interval. The withholding names the absence and the reason.
3. `fixed_horizon.sample` publishes 10 display rows, not the scored 161, so no downstream consumer
   can recompute this interval from the artefact. That is the right call — a second source for one
   figure — but it means the interval must come from the run or not at all.
