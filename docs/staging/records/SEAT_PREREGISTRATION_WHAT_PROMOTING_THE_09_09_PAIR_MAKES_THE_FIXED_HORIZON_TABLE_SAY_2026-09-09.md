**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — promote-the-09-08b-pair-and-give-the-fixed-horizon-cut-its-own-interval) · **Class:** measurements_that_mirror

# Pre-registration: what promoting the 09-09 pair makes the fixed-horizon table say

**Written BEFORE the floor run finished**, so the predictions below are about a file that does not
exist yet. At the time of writing `value_cycle_ab_s1_noise_floor_20260909.json` is absent, unit
`longjob-noise-floor-20260909` is `active`, PID 4064918, **56 minutes elapsed** against the 09-08b
floor's 1h58m. This exists so the promotion is graded rather than described after its answer is
known.

**Do not relaunch anything.** Check the artefact and the unit first:
`python3 -m background.launch_liveness --check`.

## The move being pre-registered

Copy `value_cycle_ab_s1_three_arm_20260909.json` → `value_cycle_ab_s1_three_arm.json` and
`..._noise_floor_20260909.json` → `..._noise_floor.json` (a file copy; `THREE_ARM_PATH` and
`NOISE_FLOOR_PATH` do not move), then `python3 -m tools.generate_value_arms_data`.

The three-arm side is already on disk and readable, so the four legs below are **facts, not
predictions** — `generated_at` 2026-09-09T01:24:34Z, world digest `39a192ce04c1eda8`, the same
world as the promoted 09-08b run:

| leg | n | concordance | own 95% null | p |
|---|---:|---:|---|---:|
| `the_published_population_ratio_outcome` | 168 | 0.5337857 | [0.4493929, 0.5503571] | 0.1907 |
| `settled_only_ratio_outcome` | 124 | 0.4992769 | [0.4410334, 0.5581778] | 0.9891 |
| `settled_only_pounds_outcome` | 124 | 0.5129503 | [0.4403103, 0.5587694] | 0.66645 |
| **`every_priced_decision_pounds_outcome`** — the estimand | **161** | **0.4210267** | **[0.4458340, 0.5540430]** | **0.0045** |

What is NOT known is the floor, and what the generator does when both sides move at once.

## Predictions

**P1.** `method_skill.fixed_horizon.available` becomes `true` and the block stops rendering its
withheld sentence. All four rows render a number **and** an interval; none renders "no interval on
this cut's own n". *Refuted if any row renders bare, or if the block stays withheld.*

**P2.** The estimand renders **0.4210** against **0.4458–0.5540**, and the page's composed verdict
for that row is the **worse-than-chance** reading rather than "we cannot tell" — it is the only one
of the four whose observed value falls outside its own interval. *Refuted if the page reads
`cannot_tell` on that row, or if the reading is composed from `inside_the_null` rather than from
the three numbers.*

**P3.** The survivor headline and the bridge's leg 0 continue to agree **to the last bit** on both
ends of the interval ([0.4493929, 0.5503571]), for the reason established on 2026-09-09: identical
seed, draw count and initial ordering make them one computation performed twice, not two samples
that agree. *Refuted if they differ at any decimal — which would mean the populations diverged.*

**P4 — the one I am least sure of.** The floor is the input I cannot see. I predict the
**promotion succeeds without any block losing a bound** — `error_bar` stays available, and no
contrast that is bounded today becomes unbounded. *Refuted if any currently-bounded figure goes
bare, which is the failure mode this family of moves keeps producing and the reason the floor is a
precondition rather than a nicety.*

**P5 — the will-not-move claim.** `world_provenance.one_world_across_every_figure` stays `true`.
This is independent rather than merely conceptually separate: both promoted artefacts carry world
digest `39a192ce04c1eda8`, the same digest the 09-08b pair carries, and `_world_provenance` reads
the artefacts' own `world_identity` before any contrast is composed. *Refuted if it moves at all.*

**P6.** The render repair landed at `9bcea85c4` changes rendered bytes for the **first time** on
this promotion. Today it is a no-op (live render sha `bcfbdc058e1ee7e3` identical with and without
it) because the promoted 09-08b artefact predates the per-leg spread and the block returns before
reaching `row()`. *Refuted if the live rendered bytes change before the 09-09 pair is promoted.*

## What would make this move wrong

If the floor run's own arms disagree with the three-arm run's world digest, the pair is not a pair
and promoting it would put two worlds on one page. **Check both digests before copying either
file.** That check is cheap and the failure it prevents is the one this page exists to refuse.
