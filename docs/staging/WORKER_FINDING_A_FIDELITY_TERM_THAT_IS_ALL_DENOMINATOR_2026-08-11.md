# WORKER FINDING — a control's fidelity term was 100% its own normaliser, so it refused a perfect instrument and passed a broken one

Filed 2026-08-11 by the worker tick that drew `H_GAP_fabric_belief_truth_gap` (L2->L3).
This is the **second** Expert Hour on this atom's caveat machinery, run under the
termination condition the previous Hour wrote for itself: *an Hour that finds nothing NEW
moves the level; one that finds something lands the finding and the level stays.*
It found something. **The level stays at 2.**
Rank: backlog. Nothing here blocks.

## The shape, in one line

A fidelity term expressed as a RATIO measures both of its parts. If the perturbation
preserves the numerator by construction and moves the denominator by design, then the
"artefact" is entirely the intended move — and because the two can also cancel, the same
term will pass a genuinely broken instrument.

## What was actually wrong (observed with evidence — run, not read)

The previous Hour (`696dcf06e`) correctly found that `panel_mirror_accuracy_drift` was a
compound and split the artefact out as `panel_mirror_epc_gap_drift` — the movement of the
REGISTER arm's normalised gap, the arm the reflection is built around. That became
`panel_mirror_relative_infidelity`, and that became the gate `panel_mirror_is_attributable`,
and that became the published `MIRROR INCONCLUSIVE` sentence.

The gap is a ratio: `mean|register − truth|` over the no-skill baseline. The reflection is
`2*prior − value`, so every premise's `|register − truth|` is algebraically identical
before and after.

**Measured on all four populations this atom runs on:**

| population | register-arm MAE drift | no-skill baseline drift | published "infidelity" |
|---|---|---|---|
| authored 15 | **0.000e+00** | 12.37% | 14.11% -> INCONCLUSIVE |
| drawn 200 (published row) | **0.000e+00** | 1.87% | 1.91% |
| suite "blunt" fixture | **0.000e+00** | 40.00% | 66.67% -> INCONCLUSIVE |
| suite "faithful" fixture | **0.000e+00** | 0.00% | 0.00% |

1. **FALSE POSITIVE, published.** On the authored panel the row printed *"the instrument
   disturbed the arm it was built around by 14.1% of its gap"*. The disturbance was
   `0.000e+00`. What moved 12.4% was the no-skill baseline — a property of the truth
   population, and **reflecting the truth population is what the mirror IS**. The exact
   class the previous Hour named ("split intended from artefact") reappeared one level
   down, in its own replacement term.

2. **FAIL-OPEN, latent and worse.** Numerator and denominator can move together and
   cancel. Over 400 subpanels drawn from this atom's own published 200-premise population,
   under the log reflection (the fallback that really does not preserve the register's
   error), **13 subpanels moved the register arm's own error by 20%–125% while the ratio
   read UNDER the 5% band** and `is_attributable` returned True. Worst case: n=30, error
   moved 125.15%, control read 4.21%.

3. **The R15 tests confirmed it rather than catching it.** The 2x2's "faithful" cell used
   `_fixed_offset_population` — an ADDITIVE register error, whose reflection is a pure
   translation, so the baseline cannot move. The "blunt" cell used a PROPORTIONAL error, so
   it can. The suite was therefore discriminating *additive vs proportional register error*,
   never *preserved vs disturbed*, which is zero in every cell. The fixture's own docstring
   said so out loud — *"the whole of it is the denominator moving"* — and the gate was
   pointed at it anyway.

## The generalisation (R10 — apply at next touch, do not retrofit speculatively)

**A fidelity term must be measured on an un-normalised quantity.** Where a control reports
"how much did the instrument disturb what it promised to preserve", that number must be the
raw preserved quantity, not a ratio containing it:

* **A ratio measures its denominator too.** If the perturbation moves the normaliser by
  design, the ratio is a compound in exactly the sense the split was meant to end.
* **A control whose subject is zero by construction cannot fail** — so measure it off the
  artefact actually built, never assert it from the algebra, and prove it fires through a
  real code path that breaks the promise (here: the log-preserving fallback).
* **Check the fixtures discriminate on the named quantity.** Two cells that differ in
  verdict prove nothing if the named quantity is identical in both.
* **A ratio can cancel.** Test the fail-open direction explicitly, on real subpopulations,
  not only the false-positive one.

## Mechanised here (not exhortation)

`epc_register_mae` / `panel_mirror_register_mae` ride in the ledger row (the raw pair, so
the share is recomputable by the reader); `panel_mirror_register_infidelity` is the artefact
and is now the gate; `panel_mirror_normaliser_drift` is the intended move and gets its own
`MIRROR YARDSTICK MOVED` sentence stating that the two gap figures are on different scales
and that the money verdict never divides by the baseline;
`panel_mirror_relative_infidelity` is retained, reported, and documented as a compound that
is NOT the gate. `_register_mae` deliberately does not read the rounded
`components["mae_model"]`, which would quantise the subject at 1e-6.

**R15, five source mutations, each firing its own named test, md5 byte-clean restore
(`4bc8898b21e5090315ad1bb2c75178af`), 15 green on the same selection unmutated:** gate reads
the ratio again / artefact measured off the original rows / normaliser folded into the gate /
intended-move disclosure dropped from the silent branch / artefact fail-opens on a moved zero.

**No published figure moved.** Re-taken on the row's own declared population
(`--seed 17 --unit-rate 7.4 --population 200 --population-seed 17`): gap 0.4269 / 0.4042,
two-level still RED on `L2.4_scale_spread_p90_p10` (the birth condition holding, not a
regression). The whole ledger diff is `measured_at`, `run_git_commit` and the four new
fields. Suites: 265 passed 2 xfailed across `test_premise_two_level` +
`test_couple_fabric` + `test_gap_ledger_reconciler`; epistemic verifier PASS on 543 files.

## Termination condition for the NEXT Hour, restated

Unchanged in form and still falsifiable: **an Hour on this caveat machinery that finds
nothing NEW moves the level; one that finds something lands the finding and the level
stays.** Two consecutive Hours have now found a defect in the previous Hour's own fidelity
term, both of the same family (a disclosed number that is not the quantity it is named
after). The next Hour should start by asking what `panel_mirror_register_infidelity` is a
ratio OF, and whether that denominator can move.
