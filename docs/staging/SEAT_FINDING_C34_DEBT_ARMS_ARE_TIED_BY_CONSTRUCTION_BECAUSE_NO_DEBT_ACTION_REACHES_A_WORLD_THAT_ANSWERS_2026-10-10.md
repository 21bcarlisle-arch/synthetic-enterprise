**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 4 · **Atom:** `C34_next_best_action_is_one_decision_across_debt_retention_upsell_and_carbon_judged_by_clv` · **Claim:** `c34-debt-branch-is-the-runs-collections-decision`

# C34's debt branch: the two arms tie by construction, because no debt action reaches a world that answers

## Disposition of the duplicate-work note

The draw said the claim was already held under this id. The holder was this draw itself: its own
write at 10:56:57, made by the executor that spawned this invocation. No rival seat or
`surgical_land` was on the subject. So I did not release it as a duplicate.

## The premise, re-measured

The premise still holds. `company/crm/next_best_action.py` has no production caller; `orphan_baseline.json:136`
still lists it. The cited commits c0c5fa955 and 1aa97f1a4 are on origin. They built the plan offer
through the seam and the world's memory of an agreed plan, not this decision.

## Why I did not wire it or run the arms

The focus row asks for a choice at the SLC 27.5B trigger among three debt actions: a plan through
the seam, a payment-method change, or nothing. The choice would be made on forward value net of the
company's own bad-debt belief, and graded against a flat "same plan for everyone" rule on the
400-founder book. Read at HEAD, every route by which that choice could change an outcome is closed:

1. **The world answers every plan offer None.** `simulation.plan_offer_response.PUBLISHED_BASIS`
   is None in all three slots: take-up, instalment keep rate and instalment size. Each carries the
   reason that no published source gives it (`docs/market_research/domestic_repayment_plan_take_up_and_keep_rates.md`).
   I printed it at HEAD this turn. An offer changes no ledger, no settlement and no departure.
2. **No payment-method change crosses the seam.** `SimInterface` exposes `get_payment_method`, which
   is read-only, plus the plan pair and `send_contact`. `send_contact` accepts only the SVT-switching
   instruments sourced in `simulation/contact_response.py`. There is no company-to-world write of a
   payment method, so a move to direct debit or to prepayment has no world counterpart.
3. **"Nothing" is not a lawful alternative at the trigger.** The ladder's `repayment_plan_offer`
   step is the company's SLC 27.8 obligation. A per-customer rule that withholds it from some
   triggered accounts is a licence breach, not a decision. So the only lawful menu at the trigger is
   {plan}. That is the flat rule.
4. **The row says the branch "needs no uplift estimate".** That is true only of the module as built,
   where the debt branch is a forced constraint (`_debt_constraint`). Choosing *among* debt actions
   on forward value net of bad debt needs each action's effect on default. That is exactly the
   uplift that nothing establishes: no published rate, and no holdout (B8 L3 shows a 400-household
   holdout never decides).

**Pre-registered prediction, written before any run and not run:** if the debt decision were wired
and both arms run on the 400-founder book at the default seeds, every household's net value would be
bit-identical across arms. The paired difference would be exactly 0 with a zero-width interval, and
the verdict would be "cannot tell". The prediction is refutable by the run. I did not spend about 8
hours of box time on it, because the four points above make it hold by construction. Under the
CLAUDE.md rule, a decision that cannot be wrong is not graded.

## The arrears grade the row asked me to read first

`403b46746` reads the arrears re-take NOT MET, HIGH: 6.1% pooled over dice seeds 0–2, which is
1.19× Ofgem. Resampled by account, though, the pooled interval is 4.7–7.5%, so over-holding is "not
established either way". Any C34 debt result would rest on a world whose debt level is graded high
on its point estimate. Its interval does not establish that, so a result would need both caveats,
not only the first.

## What would unblock it (raised in `for_the_director`)

A debt decision can be graded only when the world can answer at least one debt action. There are two
routes:

- **(a) a sourced plan take-up and keep rate.** The research doc records that the published Ofgem
  stocks do not bound them. This is a knowledge gap, and it stays open.
- **(b) the director names a curriculum world with a stated take-up and keep rate.** These are
  curriculum values, marked as such and decided blind to company results. The decision could then be
  graded inside that named world.

My recommendation is (b), as a named curriculum world. It is his call because it is curriculum.
Until then, the C34 level move is refused, and the refusal is named in
`docs/design/simplifications/C34_next_best_action_is_one_decision_across_debt_retention_upsell_and_carbon_judged_by_clv.yaml`.
The module stays in the orphan baseline: removing it with a caller that cannot change anything would
read as a wired decision.

## A practitioner question in the same raise

Is a company-initiated payment-method change a *debt action* a GB supplier takes at the 27.5B
trigger? Moving a household to prepayment for debt is the regulated involuntary-PPM route (Ofgem's
2023 code). Moving it to direct debit needs the household's mandate. I read neither as a lever the
company can pull alone. If that frame is wrong, the menu changes.
