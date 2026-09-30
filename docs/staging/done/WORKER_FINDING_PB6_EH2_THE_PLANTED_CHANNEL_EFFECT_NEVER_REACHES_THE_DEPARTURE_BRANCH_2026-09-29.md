**Severity:** LATENT · **Lane:** W4_the_wall · **Epoch:** 3 · **Atom:** `PB6_the_engagement_observable_crosses_the_seam`

# PB6 EH-2: plant 0.5x and plant nothing, through the real loop

**2026-09-29.** Drawn as Lane 0 `pb6-eh2-planted-and-null-engagement-recovery`, after `bc16b269b`
(EH-1 remedy). Harness: `tools/_pb6_engagement_recovery_arm.py`.

## The arms

- **planted**: `simulation.household_segments.CIM_SWITCH_RATE_BY_CHANNEL[PREPAYMENT]` halved
  (0.031 -> 0.0155) before the run. The mean-preserving normaliser recomputes, so the world's
  prepayment multiplier becomes 0.307 against HEAD's 0.589.
- **null**: all three channels set equal (0.056), every world multiplier exactly 1.0.
- **head**: the world as it stands (prepayment multiplier 0.589), for prediction 3.

Each is one `simulation.run_phase2b.main()` over the full window, graded on the company's
`payment_method_engagement_reading(<method>, 2026)` read off the run's own ledger at scope exit.

## Read BEFORE running: where the world's channel effect acts

Tracing the call sites before writing predictions changed what I expect.
`engagement_multiplier_for_channel` reaches the run loop only through
`active_renewal_probability_for_customer`, which has two callers: `renewals.build_renewal_schedule`
(electricity) and the gas-leg roll in `run_phase2b` (line ~780). Both decide whether a fixed term
becomes an **SVT stint**. An SVT term is `_indexed_tariff`, so no renewal decision is booked on it.

The departure branch, where `observe_competitive_loss` is booked, rolls
`rolls_active_renewal(..., active_renewal_probability(_engagement_level))` at line ~2361. That is
the archetype alone, **without the channel multiplier**. So the plant changes how many decisions a
prepayment household reaches, and not the departure rate per decision.

## Pre-registration (filed before either arm ran)

1. **The company does not recover the plant.** Planted and null end-of-run prepayment factors
   differ by less than 0.10, and the planted arm does NOT read within 0.10 of 0.307.
2. **Both arms move up from the prior toward 1.0**, reading roughly 0.65-0.85. The per-decision
   channel O/E is approximately book O/E, so the likelihood ratio is about 1. The weight is about
   0.3-0.5 on a book this size. Sampling noise is large (log sd ~0.3), so this is a range and not
   a point.
3. **Prepayment decision COUNT falls in the planted arm** compared with null, because more
   prepayment terms go to SVT stints. That is the only place the plant shows.
4. (Finding prediction 3) The head-world factor is above 0.585 and above what the pre-EH-1 raw
   rule gives on the same counts.

If 1 fails, meaning the company does recover something, then my reading of the call sites is
wrong and that is the more important result.

## Result (worktree at `ad3e03018`, one full-window `run_phase2b.main()` per arm, graded at 2026)

| arm | world PPM multiplier | PPM decisions | PPM lost / predicted pre-factor | ratio | w | **factor** | pre-EH-1 raw rule, same counts |
|---|---:|---:|---:|---:|---:|---:|---:|
| null | 1.000 | 20 | 4 / 6.91 | 0.474 | 0.411 | **0.537** | 0.427 |
| planted | 0.307 | **2** (all in 2017) | 0 / 0.38 | 0.549 | 0.036 | **0.584** | 0.562 |

Book: 91 (null) and 84 (planted) closed renewal decisions over the whole window, with 42 losses in
each. Standard credit reached only 5 and 4 decisions. Direct debit read 1.005 (null) and 0.925
(planted) against a prior of 1.057.

1. **HELD.** Planted minus null is 0.047. The planted arm reads 0.584, which is the prior, and is
   nowhere near 0.307. **The company does not recover a planted channel effect. EH-2 answers FAIL.**
2. **REFUTED, and kept beside the claim.** The null arm moved DOWN from the prior (0.537), not up
   toward 1.0. The world's truth in that arm is 1.0. The cause is 4 prepayment losses against 6.91
   predicted. That is about 1.5 sd of log noise at n=20. It could also be something in the world
   correlated with prepayment that the company's pre-factor belief does not carry (for example the
   world's debt objection holding indebted prepayment households in place). **I cannot yet say
   which.** It is one run on a deterministic book, so no second seed exists to separate them.
3. **HELD, and much stronger than predicted.** The plant took prepayment decisions from 20 to 2.
   After 2017, not one prepayment household in the planted arm reached a fixed renewal: every one
   of them sat on SVT stints, where no decision is booked and no renewal departure is rolled.
4. See the head-arm row below.

## What this means: two structural reasons, and neither of them is the EH-1 rule

**(a) The world expresses "shops less" as exposure, and the ledger counts only decisions.** A
low-engagement household in this world rolls to SVT and faces no renewal departure roll until it rolls
back. The departure branch's own active roll omits the channel. So per decision, the plant carries
almost no signal, and the ledger's denominator (fixed renewal decisions) excludes exactly the SVT
time where the effect lives. CIM's 3.1% is a rate per household over six months, meaning per unit
of EXPOSURE. The ledger measures per DECISION. **Before any remedy, say which is meant.** Either
the company's exposure should be customer-time, SVT stints included (company side), or the world
should put the channel on the per-decision roll too (sim side, and it would double-count the SVT
route unless the two are reconciled). This is a definition question, not a constant. I have not
picked a side.

**(b) The book is far too small to learn a channel factor from.** It has at most 20 prepayment
decisions in nine years. Even a perfectly expressed plant would get about w = 0.4. The rule can
only be graded on a book at PB1's population scale.

## Head arm (finding prediction 3)

| arm | world PPM multiplier | PPM decisions | PPM lost / predicted pre-factor | ratio | w | **factor** | pre-EH-1 raw rule, same counts |
|---|---:|---:|---:|---:|---:|---:|---:|
| head | 0.589 | 10 | 1 / 2.56 | 0.358 | 0.202 | **0.530** | 0.457 |

4. **HALF HELD.** The remedied rule reads above the raw rule on the same counts (0.457 to 0.530,
   and 0.427 to 0.537 in the null arm), so EH-1 does move the real-run factor up. It does NOT read
   above the prior of 0.585, because 1 loss against 2.56 predicted on 10 decisions pulls it down.
   The raw-rule column reuses the remedied weight, so it compares likelihoods and blends and is
   not a byte-exact replay of `bc16b269b~1`.

The three arms also order prepayment decision counts exactly as the plant does: 20 (multiplier
1.0), 10 (0.589), 2 (0.307). That is prediction 3's mechanism seen at three points: the world's
channel effect lands on how many renewals a household REACHES.

## Next

The per-decision vs per-exposure definition in (a) comes first, because any remedy on either side
of the wall is a different model depending on the answer. That is PB6's next step. The artefacts
are in `/var/tmp/pb6_eh2/` (`<arm>.json` holds the full counts per method and year). They are not
committed, so re-running the harness is the reproduction.
