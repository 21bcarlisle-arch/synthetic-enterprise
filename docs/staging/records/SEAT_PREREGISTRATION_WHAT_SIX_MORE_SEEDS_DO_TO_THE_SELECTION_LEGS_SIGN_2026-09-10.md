# PRE-REGISTRATION — what six more seeds do to the selection leg's sign

**Severity:** RECORDED
**Lane:** G_data_learning
**Filed:** 2026-09-10, BEFORE the run was launched
**Claim:** `the-selection-leg-has-a-mean-and-not-enough-draws-to-state-its-sign`

---

## The state this bets against

`docs/observability/value_cycle_ab_s1_noise_floor.json` — mode `all`, world `39a192ce04c1eda8`,
producing commit `c066c114b`, generated 2026-09-09T15:17:31Z — holds nine seeds
(`11111,22222,…,99999`). Every figure in `site/data/value_arms.json → error_bar` is computed off it:

| quantity | n = 9 |
|---|---|
| `selection_gbp` mean | **−1,078.17** |
| `selection_gbp` stdev | 1,810.50 |
| sem | 603.50 |
| \|mean\| / sem | **1.787** |
| `distinguishable_from_zero` | **false** |

More draws do not shrink the stdev — that is the world's own dispersion. They shrink the **sem**,
which is the only quantity a sign is stated from. At this mean and this stdev the two-sided 95%
threshold `|mean| ≥ 1.96·sd/√n` is crossed at **n = 11** — but n = 11 is a knife-edge that is met
only if the mean does not move at all, and the mean is exactly the thing new draws move.

## The seed set — REVISED 18:41Z, before either run had written a byte

**What I was going to do.** Six new seeds on the family's own visual scheme — `10101, 20202, 30303,
40404, 50505, 60606` → a family of 15 — launched as two sequential legs, plus `11111` re-run at
today's HEAD as the reproduction control.

**Why that is not what is happening.** `floor_run_headroom_refusal()` refused the launch, correctly,
and naming its reason: **two floor legs are already running on this guest**, holding 12.5 GB and
still growing. Reading their cmdlines rather than assuming:

| pid | started (UTC) | seeds | mode | writes to |
|---|---|---|---|---|
| 1072649 | 14:50:22 | `11111 … 99999` — **the existing nine** | `all` | `/var/tmp/se-floorrun-20260910` (own worktree) |
| 1146711 | 15:06:44 | `111111 … 999999` — **nine new** | `all` | `/home/rich/synthetic-enterprise` (shared tree) |

(`--level-arm` differs between them and is **inert here**: `main()` never reads `args.level_arm` on
the `--noise-floor-seeds` branch. The two runs are comparable.)

So the draws this bet needs are already being drawn, by two other lanes, and a third leg would be
both refused and actively harmful — it would starve two runs that are four hours in. **The seed set
is therefore theirs, not mine, and it is better than mine on both counts:** nine new members instead
of six (**n = 18**), and a nine-seed reproduction block instead of a one-seed one.

**R12 pre-commitment, unchanged in force.** The seed lists above are the whole list; they were fixed
by another lane before I saw them and I cannot revise them. I will not commission a further seed
after seeing the answer. Whatever these two runs return is the result — including "still cannot
state a sign" and including a sign that flips positive.

**This revision is legitimate and here is the evidence:** at 18:41:29Z, verified by `ls`, neither
`value_cycle_ab_s1_noise_floor_20260910.json` nor `..._20260910b.json` existed at any of the three
candidate paths. No number from either run was in front of me when the predictions below were
written. The original six-seed predictions are preserved verbatim in the sections that follow and
are graded too, as the model they came from is the same one.

At the measured ~41 min/seed the legs land ~21:00Z and ~21:15Z, later under mutual contention.

## Prediction 1 — the reproduction block, and it is the load-bearing one

Seed `11111` has returned `selection_gbp = +1,260.9262` **to the penny** at three consecutive
producing commits (`ac6433b8`, `4e853a83`, `c066c114`). Before that it did not: at `04361d6c` it was
+1,199.55 and at `1d821e12` +2,349.68. So the leg is reproducible under code motion *sometimes*, and
pid 1072649 is re-drawing all nine at a fourth tree.

> **I predict all nine reproduce to the penny** — mean −1,078.1657, stdev 1,810.5008, identical
> member for member.

This is the fold's precondition and I am stating the consequence in advance: **if they do not match,
I do not fold.** A family whose members were drawn by different code is not a family. The page
already carries exactly this caveat about the floor-vs-figure pair — `floor_tree_pairing.caveat`:
*"sizing it needs the same seed drawn under both trees"* — and says the page cannot measure it.
Pid 1072649 **is** that measurement, at nine seeds rather than one, so this settles a question the
page currently declares unanswerable, whichever way it goes. A partial match (some seeds move, some
do not) is the most informative outcome of all and I predict it will not happen.

## Prediction 2b — the mean, the sem and the sign at n = 18

The operative predictions, on the seed sets actually running. Same model as 2–4 below, with a
nine-member new block instead of a six-member one: `mean₁₈ = 0.5·(−1078.17) + 0.5·X̄₉ⁿᵉʷ`, and
`X̄₉ⁿᵉʷ` has predictive sd `√(σ²/9 + sem²) = 853.5`, so `mean₁₈` has conditional sd **427**.

> * **mean₁₈** — point **−1,078**; 80% band **[−1,625, −531]**; 95% band **[−1,915, −242]**.
>   Stays negative with ~99% probability.
> * **sem₁₈** — point **427** (band [340, 520]); stdev unchanged at ~1,810 (band [1,450, 2,200]).
> * **threshold the mean must beat** — `1.96 × 427 ≈ **836**`.
> * **does the sign become stateable?** `Φ((1078 − 836)/427) = Φ(0.57) =` **~71%**, and pulling that
>   down for the sem's own uncertainty: **I predict ~65% yes, a stateable negative sign.**

Note the direction of the change and that it is not a mistake: nine new draws make the *outcome*
less predictable than six would have (427 > 382) because the new block carries more weight, while
simultaneously making a sign *more likely to be stateable* (threshold 836 < 916) because the sem
falls. More draws pin the mean; they do not make the next result easier to guess.

**If only pid 1072649 lands** (nine reproductions, no new members): the family stays at nine, no
sign is stateable — that is arithmetic, not a prediction — and the deliverable is the code-motion
measurement plus the distance-to-a-sign arithmetic below.
**If only pid 1146711 lands** (nine new members, no reproduction block): I fold only if its
`world_identity.digest` is `39a192ce04c1eda8`, and the page carries an unmeasured-code-motion
caveat naming the two producing commits.

## Prediction 2 — the mean at n = 15

The six new draws are exchangeable with the nine. Conditioning on the nine already in hand,
`mean₁₅ = 0.6·(−1078.17) + 0.4·X̄₆`, and `X̄₆`'s predictive sd is `√(σ²/6 + sem²) ≈ 954`, so the
conditional sd of `mean₁₅` is `0.4 × 954 ≈ 382`.

> **Point: −1,078. 80% band: [−1,570, −590]. 95% band: [−1,830, −330].**
> **I predict the mean stays negative — ~99.7% under this model — and I predict it does NOT
> leave the 95% band.** A mean outside [−1,830, −330] refutes the exchangeability assumption
> itself, not just the point estimate, and I will say so if it happens.

## Prediction 3 — the standard error at n = 15

The stdev is a property of the world and should not move much; the sem falls as `1/√n`.

> **sem: point 467, band [370, 570]. stdev: point 1,810, band [1,450, 2,200].**
> The 95% threshold the mean must beat is `1.96 × sem ≈ 916` (band [725, 1,117]).

## Prediction 4 — does the sign become stateable?

Combining 2 and 3: `P(mean₁₅ ≤ −916)` with `mean₁₅ ~ N(−1078, 382)` is `Φ(0.42) ≈ 0.66`; widening
for the sem's own uncertainty pulls that down.

> **I predict ~60% — more likely than not, and a long way from certain.**
> Concretely: **yes, a stateable negative sign** is my single most likely outcome, and I am
> recording in advance that a 40% "still cannot" is not a failed run and is not a cue to add seeds.

If leg B dies and the family is 12: threshold 1,024, conditional sd of `mean₁₂` ≈ 302, so
`P(state a sign) ≈ Φ(0.18) ≈ 0.43` — **at n = 12 I predict the sign is more likely than not still
unstateable**, and the page will say so with 12 in front of the reader.

## Prediction 5 — the level share

> `level_share_of_advantage` mean at n = 15: point 1.069, band [1.02, 1.12]. Stays above 1.0,
> i.e. the level arm keeps accounting for more than all of the advantage.

## What I do with each outcome, decided now

| outcome | what the page says |
|---|---|
| reproduction block mismatches | **no fold.** Page keeps n = 9; the finding is that the family cannot be extended across this code motion, and the size of that code difference is now *measured* where the page currently says it can only be caveated. |
| n = 18, \|mean\|/sem ≥ 1.96, mean negative | The page **states the negative sign**: the per-customer selection arm is worse than its own flat-at-level baseline. |
| n = 18, \|mean\|/sem ≥ 1.96, mean positive | The page states the positive sign. Same machinery, and this pre-registration is refuted. |
| n = 18, \|mean\|/sem < 1.96 | The page says plainly that it **still cannot state a sign at 18 seeds**, prints `sems_from_zero` against 1.96 and the `seeds_needed_to_state_a_sign` the new family implies, and the reader sees the distance rather than a bare "no". |

**The arm is not tuned in any branch.** A selection leg worth nothing is a complete answer, and a
stated negative is the most valuable result available here: it converts a suspicion into a finding.

## A defect found while writing this, filed here because it is this bet's subject

The direction that drew this work states that the artefact's own arithmetic says
`sems_from_zero: 1.79` against `sems_needed_to_state_a_sign: 1.96` with
`seeds_needed_to_state_a_sign: 11`, "and the page says so".

**The page does not say so, and neither does the artefact.** `grep -rn sems_from_zero` over the
whole tree returns nothing. The three numbers are arithmetically right — 1078.17/603.50 = 1.787,
and `(1.96 × 1810.50 / 1078.17)² = 10.83 → 11` — but they exist only in the sentence that drew the
work. A reader of `site/data/value_arms.json` gets `distinguishable_from_zero: false` and no measure
of **how far** from stateable the leg is, or what it would take.

That gap is landed separately from this run, because it is true at n = 9 and stays true at n = 15,
and because it is what makes the fourth row of the table above sayable at all.

---

*Filed before the run. The result is graded beside this file whichever way it goes.*
