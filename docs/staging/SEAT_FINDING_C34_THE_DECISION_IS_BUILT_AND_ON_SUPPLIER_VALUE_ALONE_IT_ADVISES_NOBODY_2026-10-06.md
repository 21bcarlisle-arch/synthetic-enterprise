**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 4 · **Atom:** `C34_next_best_action_is_one_decision_across_debt_retention_upsell_and_carbon_judged_by_clv` · **Claim:** `c34-first-slice-one-decision-over-the-built-measures-judged-by-forward-clv`

# C34 slice 1: the decision is built, and on supplier value alone it advises nobody

## Disposition of the duplicate-work note

The draw said the claim was already held under this id. The holder was this invocation (the draw's
own write, nine seconds old; no rival seat or `surgical_land` was running). The module did not
exist on origin. Work done, not released as a duplicate.

## What landed

`company/crm/next_best_action.py` and `tests/company/crm/test_next_best_action.py`.

- **The decision.** For one account: debt support when SLC 27.5B's trigger fires (two consecutive
  missed monthly payments), whatever else scores. Otherwise, among the actions the company estimates
  leave the customer no worse off, the one that raises forward value most, and only if it raises it
  at all. Forward value is B11's shape (sum of P(supplied) × monthly margin; first month earned in
  full, as `forward_clv.run_backtest` counts it). What is ranked is the uplift against doing nothing,
  not a propensity.
- **The flat baseline** is B11's flat rule carried over: one action for every account, picked on the
  book's mean estimated effect.
- **The grade** scores each rule's choices on the TRUE effect (a harness argument, as
  `tools/decision_probe.py` holds truth), paired over the same accounts with B11's `_paired`
  interval.
- **Controls.** Planted arm: the right action differs between accounts, so per-customer beats flat
  (interval below zero). Null arm: one action is right for every varied account, so the difference is
  exactly zero and the verdict is "cannot tell". Misled arm: the estimates point the wrong way, so
  the grade returns "flat better". This is the leg that proves the grade can rule against the rule it
  grades. Partition control: all four branches (debt, tariff, carbon, nothing) can be taken. Four
  mutations bite: customer gate removed, trigger off by one, `max` replaced by first-listed, and the
  positive-value floor removed.
- **Left out.** The retention discount at an SVT-to-fix conversion (the director's open row), and
  non-energy cross-sell (no world counterpart; research §3.3).
- **Dormant on purpose.** Recorded in `docs/design/orphan_baseline.json` in the same commit. No uplift
  estimate exists: no published supplier-own uplift (research §7 gap 1) and no holdout (B8 idle). With
  today's inputs, every estimate carries a named `None`, so every non-debt decision would be
  "nothing", with that stated as the reason. Wiring it before W2_39 (households respond to contact)
  and B8 exist would publish a decision that cannot be wrong.

## What the numbers at real inputs said (printed before the tests were written)

On B11-scale inputs (margin £5–30/month, hazard 0.5–3%/month, 48 months), take an advice action that
gives up £2–3 of margin a month and cuts the hazard by 0.1–0.3 points. It **loses** £34–121 of
supplier forward value in every cell. And the ranking between two such actions **flips** between a
£15 and a £30 account under identical effect estimates. So the account's own B11 numbers make the
choice per customer even before any heterogeneous uplift exists.

## The question for the director: what "the customer's benefit first, then ours" means in the rule

Slice 1 reads the ruling as: **customer benefit is a gate, then supplier forward value is the
objective.** The printed table shows the consequence. Advice that saves the customer money is
chosen only when its retention effect pays for the margin it gives up. On plausible numbers, that
means almost never. The rule is then "do no harm, take what pays us", which is a transfer-safe
rule, not a value-creating one.

The alternative the mission points at: **rank on value created (customer benefit + supplier
change), subject to neither side being worse off.** That is still not a transfer, but it gives away
margin the customer gains more from. It would also need a horizon for the customer's benefit, and
nothing establishes one.

**Recommendation:** keep the gate-then-CLV reading for slice 1, because the atom title says "chosen
by its effect on CLV". Ask the director whether C34's objective should become joint value with a
no-loss floor on both sides. It is a one-line change to `decide`'s `max` key, and the planted, null
and misled arms carry over unchanged. Raised in `for_the_director`.

## Next slice

A production caller only after an uplift estimate exists: the first wire is B8's holdout
(`whether` to act, logged), graded against `tools/decision_probe.py`'s true counterfactual on the
W2_39 world.
