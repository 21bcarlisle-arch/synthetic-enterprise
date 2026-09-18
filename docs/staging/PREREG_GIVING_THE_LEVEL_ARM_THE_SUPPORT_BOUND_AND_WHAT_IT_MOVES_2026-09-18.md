**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# PRE-REGISTRATION — the level arm gets the churn-support bound, and what that is expected to move

**Filed:** 2026-09-18, before running anything and before writing the code.
**Claim id:** `the-two-arms-have-never-priced-the-same-population-and-the-page-says-they-have`

---

## What I checked before writing this, rather than taking the drawn item's word for it

| the item's claim about the tree | checked how | result |
|---|---|---|
| the gap is **67** renewals, **64** of them the value arm's refusals | `decision_population` in `docs/observability/value_cycle_ab_s1_three_arm.json` | **66** and **65** — value priced 215/declined 65, level priced 281/declined 0 |
| `decision_population.the_mechanism` still attributes the gap to roster divergence | read `tools/run_value_cycle_ab.py:3816` at HEAD `a08752789` | **refuted in the CODE** — the sentence is now derived from `_denominator_reconciliation` and says "THE SMALLER ARM'S OWN REFUSALS" when the declines own the gap. **True of the PUBLISHED artefact**, which is the 2026-09-10 run and carries the old string. The correction reaches a reader only on a re-run. |
| `why_this_is_not_a_defect` still licences comparing arm-level totals | same | same shape — the conditional branch already says "IT MAY WELL BE ONE". The *unconditional* docstrings above it (`decision_population`, `declined_renewals`, `level_vs_selection`) do still assert the refuted mechanism, and those are what this turn corrects. |
| the value arm's bound is at L874 | read | `support_pct = max_supported_rate_increase_pct()` → 83.098…%; `ceiling_from_support = current_rate × 1.831` |

## The design departure, declared before the measurement

The item prescribes: raise `MarginDecisionUnavailable` **when the clamped level does not survive
the support ceiling**. Taken literally that does *not* make the populations equal, and the
arithmetic says so before any run:

* the value arm refuses iff **no candidate** survives, i.e. `base + min(candidates)=0.50 > ceiling`;
* the literal level rule refuses iff `base + 20 > ceiling`.

`{base + 0.50 > c}` ⊂ `{base + 20 > c}`. So the literal rule makes the level arm's priced set a
strict **subset** of the value arm's, on every renewal whose support headroom falls in [0.50, 20).
That reproduces the published defect with the opposite sign — level-arm refusals of renewals the
value arm priced — and would make the tree's existing "prices EXACTLY the renewals the value arm
prices" claims false in the other direction.

**So I implement the same FRONTIER, not the same threshold**: the level is clamped by the support
ceiling exactly as it is already clamped by the lawful ceiling, and the arm refuses — with the value
arm's own named reason — when no margin at or above `min(candidates)` survives **both** bounds.
That is the value arm's refusal predicate verbatim, so the two arms price and refuse together by
construction, which is the property the item asks for.

## Predictions (recorded before the run)

1. `declined_renewals.level_arm_priced_the_same_renewal == 0` on the new run. This is the property
   the fix is for and the control is keyed to it.
2. The level arm's `declined` goes from **0** to of order **60–70**, and its `priced` falls from 281
   to within a few of the value arm's.
3. Priced counts will **not** be exactly equal, and expecting them to be would be wrong: the arms'
   rosters still diverge through churn (2037 vs 2050 renewals offered on the last run). I predict
   `decision_population.reconciliation.explained_by_declines` ≈ 0 (±2) and the residual gap to be
   roster only — that, not integer equality, is what "same population" can mean across a
   sequential A/B.
4. `level_vs_selection.level_advantage_gbp` **falls** (the level arm loses the margin it used to
   earn on ~65 renewals the value arm refused), so `selection_gbp = value_adv − level_adv`
   **rises** from `−332.64`. I predict the sign flips to positive; I do **not** predict a
   magnitude, and the noise floor already published for this contrast is wider than the move, so a
   sign flip is not by itself a claim that the choosing is worth something.
5. The level arm will also price LOWER where the support bound clamps it without refusing, so some
   of the move in 4 is a price change and not only a population change. These are not separable in
   one run and the artefact will not claim they are.

## What would refute the design

If the new run shows `level_arm_priced_the_same_renewal > 0`, the frontier is not shared and the
change failed. If the level arm's `declined` is 0, the bound never bit and the fix is inert.
