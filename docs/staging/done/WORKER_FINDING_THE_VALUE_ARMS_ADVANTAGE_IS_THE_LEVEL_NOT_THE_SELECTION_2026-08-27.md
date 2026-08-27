# The value arm's advantage is the LEVEL, not the SELECTION — and the enterprise-value reading that says otherwise is circular

**Date:** 2026-08-27. **Author:** the delivery seat.
**Instrument:** `flat_at_level`, the third arm, built at the director's instruction —
*"build the third arm properly in renewal_margin_uplift"*. Landed with this finding.
**Supersedes the withdrawn attempt:** `WORKER_FINDING_THE_LEVEL_VS_SELECTION_TEST_CANNOT_BE_BUILT_FROM_THE_FLAT_CONSTANT_2026-08-27.md`,
whose closing line — *"a genuine third arm inside `renewal_margin_uplift`"* — is what this built.

## The question

With the renewal schedule repaired, the value arm beats flat rules by **£7,065.86** over the decade
while `belief_vs_outcome.discrimination_auc` is **0.4653** — below a coin flip. An advantage that
cannot be attributed to inference has to be attributed to something. The arm's median margin was
**£44.50/MWh** against the flat rule's **£2.00**. So: the LEVEL it priced at, or the SELECTION it made?

## The instrument, and the three properties that make it a control

`flat_at_level` applies **one** uplift to every renewal it prices — the same renewals `value_based`
prices, through the same guards, under the same lawful ceiling. The arms differ by the CHOOSING and
by nothing else.

1. **Same population** — it does not early-return, so it reaches the same term-index, commodity,
   tariff-type and observed-state guards.
2. **Same ceiling** — clamped, unlike `flat_rules`. This is the confound that made the withdrawn
   attempt return 9.4×: comparing an *unbounded* level against a *bounded* selection measures the bound.
3. **One level** — no customer attribute reaches the price.

**A defect only a third arm could expose:** `renewal_margin_uplift` called `decide_margin(arm=VALUE_BASED)`
as a hardcoded literal. Invisible while the only other arm returned early; live the moment a third
exists, because `flat_at_level` renewals would have been priced by the value arm and **the comparison
would have compared the arm with itself**. Now passes the arm it was given, pinned by an AST test.

## The result — both windows agree

| window | control (flat @£2) | value_based | flat_at_level @£44.50 | level share of the advantage |
|---|---|---|---|---|
| **full decade** | £111,269.70 | £118,335.56 (+£7,065.86) | **£119,724.66 (+£8,454.96)** | **119.7%** |
| 2019 | £14,031.86 | £17,099.66 (+£3,067.81) | £18,091.04 (+£4,059.19) | 132.3% |

> **The level explains all of the advantage. The selection is worth −£1,388.80 over the decade**
> (−£991.38 on 2019). Not merely uninformative — mildly value-destructive, in the same direction on
> both windows.

This is what an AUC of 0.4653 predicts. An estimator that ranks *worse* than chance cannot select
profitably, and the two measurements corroborate rather than merely coexist.

## The enterprise-value reading disagrees, and must be DISCARDED rather than reported

EV tells the opposite story — level +£5,145.68 against the arm's +£7,149.28, i.e. the level gets only
**72%** and selection looks worth **+£2,004**. It is tempting to report this as "the two clocks
disagree" (R14). That would be wrong, and it is the more dangerous of the two errors available here.

`build_enterprise_value` (`saas/enterprise_value.py:147`) projects CLV **from `churn_risk` — the
company's own belief**. The arm chooses its margin by maximising expected value under
`enriched_churn_estimate` (`value_based_renewal.py:681`). **The arm optimises under a model, and EV
then re-scores the resulting book under the same model.** That is R15's TAUTOLOGY pattern exactly:
the checked value derived from the same source it checks. The value arm is guaranteed to look better
on EV whether or not its choices were good, and with AUC at 0.4653 the belief doing the scoring is
anti-informative.

**Realised net is the only measure here not derived from the company's own beliefs.** It is the verdict.

## Caveats, stated because they are real and not removable

- **The populations diverge** — 31 renewals priced against the value arm's 25. Different prices cause
  different churn, so the surviving book differs. This is inherent to *any* arm comparison in a world
  where price affects retention; it is not a confound that a better instrument would remove.
- **The arm is flat except where the cap binds.** `distinct_margins: 4` on the decade. Clamping is the
  only mechanism that can vary a single constant, so those four values are the cap binding — correct
  behaviour, and the clamp is required for property 2 above.

## The instrument reported its own clamp as never happening — found in this arm's first decade run

That run returned `distinct_margins: 4` **and** `endpoint_at_ceiling: 0`, both describing the same
book. `arm_decision_shape` reads `endpoint_side`, which the value arm's *search* sets and this branch
did not — so the clamp fired silently and the shape described a purely flat, unclamped arm. **A zero
meaning "nobody wrote this field", presented as "this did not happen"**: R15's FAIL-SILENT pattern, in
code written the same day, by the seat that spent the day hunting exactly this.

Fixed and R15-proven both directions (fires when the cap bites; stays silent when a ceiling is present
but above the level, which is the case an `is not None` test gets wrong). The net figures are unchanged
— `min(level, headroom)` and the guarded assignment are behaviourally identical; only the reporting was
blind.

## What it means, and where it goes

**This is a property of the WORLD, not a defect in the company** — see
`docs/design/WHAT_A_HOUSEHOLD_DECIDES_ON.md`, filed the same day. Every axis in the world is a
universal response function, and the three drawn per-household attitude weights
(`price_sensitivity`, `green_stance`, `channel_pref`) are consumed by nothing. Two households in
identical circumstances behave identically, so there is almost nothing for per-customer selection to
select *on*, and the level should carry the advantage. It does.

R12: this is a diagnostic, not a target. The correct response is **not** to tune the company's
selection until it beats the level — it is to widen the world, per that roadmap, and re-run this exact
comparison afterwards. **The level-vs-selection gap is the natural measure of whether widening the
world worked**, and it now exists as a standing instrument rather than a one-off.

---

*Evidence: `run_value_cycle_ab.py` realised metrics, full-decade and 2019 windows, schedule-fixed.
Arm + 17 R15 tests land with this doc.*
