# PRE-REGISTRATION — what the draw regrade does to the only family that recorded its rosters

**Severity:** INFORMATIONAL (a prediction, filed before the measurement it predicts)
**Filed:** 2026-09-24, delivery seat, claim `entitled-draw-count-needs-a-family-that-records-its-rosters`
**Written BEFORE running the regrade. Whatever the numbers say, this file stays beside them.**

---

## Why this is being measured at all

The drawn direction asks for two things:

1. *"Re-fold or re-run the served noise-floor family (`NOISE_FLOOR_PATH`) so its seed rows carry
   `scored_decisions`"*
2. *"then let `sems_to_state_a_sign` take `priced_decision_draws.draws_the_spread_is_entitled_to`
   instead of `selection['n']` once that count is EXACT rather than a bound."*

**Leg 1 is impossible by re-folding and I am not going to pretend otherwise.** A fold reads the
seed rows that exist; `scored_decisions` was added to the seed-row writer on 2026-09-24 and the
served family was drawn 2026-09-17. The rosters were never written, so there is nothing on disk to
fold them out of. Recovering them means re-running eighteen seeds, which the producer's own comment
prices at days of the only box. That is a real cost decision and it is recorded here rather than
silently skipped.

**Leg 2 has a live input today, which is the thing the direction did not know.** The direction says
*"No published floor records its rosters"*. That is false as stated. A census of all 28 floor
artefacts in `docs/observability/` finds exactly one that does:
`value_cycle_ab_s1_noise_floor_five_seed_head_20260924.json` — 5 of 5 seed rows carry
`scored_decisions`. It is not the SERVED family, which is why the headline figure cannot move; but
it means the exact branch can be exercised on recorded data rather than on a fixture.

## The arithmetic objection this measurement exists to settle

The verdict is `|mean| > bar * sem`, where `sem = stdev / sqrt(n)` and `bar = t(n - 1)`.

Substituting the draw count into `sems_to_state_a_sign` alone — exactly what leg 2 prescribes —
moves `bar` and leaves `sem` computed over the seed count. But if two seeds met the same
priced-decision set, their residuals are identical, and that duplication touches **three** terms,
not one:

* `bar = t(n-1)` is taken at too many degrees of freedom — the half the direction names;
* `stdev` is **deflated**, because an exact duplicate sits at no distance from its twin;
* `sqrt(n)` in the denominator of the sem is **inflated**.

So the prescribed substitution is a third of the correction, in the conservative direction. It is
not wrong so much as incomplete, and publishing it as *the* regrade would state a confidence over a
quantity nobody had defined — which is this project's named recurring failure. The honest move is
to collapse the family to its distinct draws and recompute the whole leg over them.

## The predictions

Recorded before running anything. The five-seed head holds 5 seeds over 3 distinct decision sets.

1. **The collapsed stdev will be LARGER than the 5-row stdev.** Duplicates sit at zero distance
   from each other and pull the dispersion down; removing them should let it back up.
2. **The required margin `bar * sem` will be at least 2x the 5-seed one.** The bar rises
   2.7764 -> 4.3027 (x1.55) and `sqrt(5)/sqrt(3)` contributes x1.29 before any stdev move.
3. **The sign verdict will flip from stateable to not-stateable**, if it is stateable at 5 seeds.
4. **`the_floor_regrade_agrees` will be True on this family** — `at_least` is 3 and the distinct
   residual count is 3, so the existing `width_if_each_value_counted_once` re-grade and the roster
   count should land on the same number. If they disagree, the measured coextension between an
   unchanged decision set and a pinned residual is refuted on the one family that can test it, and
   that refutation is the finding rather than this regrade.

Prediction 4 is the one worth being wrong about: it is the only check here that can falsify the
floor the served family's published bound rests on.

## What would make me withdraw the whole approach

If the collapsed mean is not well defined — if the duplicate residuals turn out to differ in the
rest of the row in a way that makes "one draw" the wrong unit — then the collapse is unsound and
the bound stands as the honest publication. That is a real outcome and not a failure.
