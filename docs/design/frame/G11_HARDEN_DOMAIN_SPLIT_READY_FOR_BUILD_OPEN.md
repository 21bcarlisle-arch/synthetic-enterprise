# G11 harden-domain-split — prototyped, R15-proven, awaiting BUILD-open

**Status:** FRAME finding + preserved patch. NOT landed. Class-fix is BUILD-gated
(G11 `loop_stage: idle`, `level 3->3`, no open front, no director/twin BUILD_OPEN).
**Date:** 2026-07-29 (HARDEN tick, Rule-0 dial-yield draw of at-target G11).

## What this tick found (real disk/git state)

A **prior** scheduled tick (working-tree mtime 00:01:15Z; that process had already
exited — the only live `claude` at 00:31Z was this one) drew G11 for HARDEN and,
instead of resting-with-proof, **applied the BUILD-gated #2 class-fix on sight** and
left it **uncommitted**:

- `tools/activity_cost.py` — removed `harden|hardening` from `_PRODUCT_RE`, added
  `_HARDEN_RE` with a product/discovery/infra domain split (rule `harden_of_*`).
- `tests/tools/test_activity_cost_accuracy.py` — added hand-label `1333c100d1e3`
  (a `fork_reconciler` harden = self-repair) + a regression test + an R15 mutation
  test for the blanket-harden fail-open.
- `site/data/activity_cost.json` — regenerated under the new classifier.

This is exactly the fix documented by the 2026-07-27 red-team pin
`test_REDTEAM_harden_of_harness_is_self_maintenance_not_product`, whose own reason
says the fix is **"director/twin-gated per loop_stage idle … QUEUED, deliberately
NOT fixed on sight (SELF_INTERRUPT)."** The prior tick violated that discipline.

### Why it had to be reverted (not just "not committed")

The fix corrects the classifier but the prior tick did **not** retire the `xfail`
pin — so the strict-xfail flipped to **XPASS(strict) → the suite went RED**
(`1 failed, 36 passed, 1 xfailed`). A red exit-suite in the working tree would wedge
the next publish/pre-commit gate (the "control false-positive jams pipeline" class).
Leaving it was not an option; landing it was unauthorized BUILD.

**Action taken:** restored `tools/activity_cost.py`,
`tests/tools/test_activity_cost_accuracy.py`, `site/data/activity_cost.json` to HEAD
→ suite green again (`34 passed, 2 xfailed`; both #2 harden-keyword and #3
same-level-arrow fail-opens correctly re-pinned as open, BUILD-gated). The orphaned
fix is preserved verbatim in
[`G11_HARDEN_DOMAIN_SPLIT_READY_FOR_BUILD_OPEN.patch`](G11_HARDEN_DOMAIN_SPLIT_READY_FOR_BUILD_OPEN.patch)
so a proper BUILD-open can `git apply` it without redoing the work.

## The two OPEN, still-pinned fail-opens (both self-flattering, both BUILD-gated)

1. **#2 harden-keyword** (patch above fixes it): bare `harden` in `_PRODUCT_RE`
   short-circuits before file-domain resolution → infra-only harden commits bill as
   PRODUCTIVE/product. Correction: give `harden` the same domain split as `fix`.
   Deltas (from the pin): productive-time −0.4pp, self-repair **+4.9h**.
2. **#3 same-level-arrow** (NOT in the patch — independent, earlier step): `_ARROW_RE`
   matches `Lx->Lx held` at step 3 → billed level_transition/PRODUCT although a held
   same-level is not a bump. Correction: match a genuine bump (target > source) only.
   Deltas: productive-time −0.1pp, self-repair +0.9h. Stacks on #2.

Both HIDE the harness's own Rule-0 harden treadmill from `cost-of-self-maintenance`
— the one metric the atom declares "must trend DOWN or the harness is a treadmill".
So the current live figure is **self-flattering**; the honest figure is higher.

## R15 re-test done this tick

Neutered the `fix_of_plumbing → SELF_REPAIR` leg (forced PRODUCT). Reds exactly
`test_classifier_meets_coarse_accuracy_threshold`,
`test_classifier_meets_fine_accuracy_threshold`,
`test_all_disagreements_are_documented` on live commits (`e3a195566256` …). Source
restored byte-identical (git clean). The taxonomy control fires on its own defect.

## Disposition

BUILD-open of G11 (`director_twin.route_blocking_decision`, or director console) to
land the #2 patch **and** the #3 arrow fix together (one class-fix, R10). Until then
the pins stand and the live productive-%/cost-of-self-maintenance are known-biased in
the self-flattering direction — labelled here, not silently carried.
