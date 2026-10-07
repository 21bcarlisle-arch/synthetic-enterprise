**Severity:** MATERIAL · **Lane:** C_customer_ops · **Atom:** `C29_decisions_stop_being_lookup_tables` · **Direction item:** `retention-guard-nets-the-companys-own-bad-debt-belief` · **Claim:** released on landing

# The retention guard nets the company's own bad debt, and on the chosen book it withdraws nothing

Pre-registration: `SEAT_PREREGISTRATION_THE_RETENTION_GUARD_NETS_THE_COMPANYS_OWN_BAD_DEBT_BELIEF_2026-10-07.md`
(beside this file, written 06:55Z, before either arm ran). Opened by
`docs/staging/SEAT_FINDING_THE_PAYMENT_SCORE_REACHES_THE_CHURN_BELIEF_AND_THE_RETENTION_GUARD_PRICES_IT_AS_IF_THE_DEBTOR_PAYS_2026-10-07.md`.

## What was built

`DecisionPolicy.retention_nets_bad_debt`, off on every standing policy. When it is on, the guard
subtracts the company's own learned bad-debt rate by arrears state (`company.pricing.default_belief`,
the rate the renewal chain already reads) times the term's energy billing. The netting is in
`growth_desk.retention_value_protected`. The run hands it the belief only under the flag. With the
flag off, the guard's value is bit-identical. Controls:
`tests/company/test_the_retention_guard_nets_the_companys_own_bad_debt_belief.py`. A planted debtor
learned through `default_belief` loses its offer and a payer keeps theirs, and the partition is
asserted first. A chain control checks the run's AST.

## The measurement

`tools/_c29_retention_engagement_arm.py {off|net}`, full 2016–2025 window, shipped sampler, at
`a5bef9df1` plus this change. Raw output: `/tmp/retnet/{off,net}.json` (not kept). That world predates
`4088674a4` (W2_20 step d, heat follows the gas meter). The guard's headroom (a median of 15.7×) is
wide enough that I do not expect that world to make it bind, but that is a prediction, not a reading.

| | offers | to POOR/CRITICAL | retention spend | renewal departures | total net |
|---|---|---|---|---|---|
| off | 73 | 11 (3 CRITICAL, 8 POOR; 7 accounts; £399.97) | £3,830.00 | 31 | £200,083.70 |
| net | 73 | 11 | £3,830.00 | 31 | £200,083.70 |

**The two arms are identical in every guard row, every renewal roll and every total.** Netting the
charge moved no decision.

**Why.** The guard refused **nothing in either arm**: all 73 guard calls offered. The value it
protects is 4.9× to 15.7× (median) the offer's cost. To withdraw an offer, the charge would have to
take at least 79.5% of the value. The largest charge the company's own belief produced was 7.9% of
it: £76.76 on PROS-2016-0098, against £2,303 protected and a £195 offer. The company's learned
bad-debt rates are a few percent of billing. Margin plus the £55 acquisition cost is many times a 3–8%
discount, so no bad-debt rate the book has learned can bind.

## Predictions, graded

- **P1 held.** 11 offers to POOR/CRITICAL accounts, inside 3–20. They are 15.1% of offers against
  11.6% of renewals read (388 of 3,335), so the score's uplift does carry debtors over the threshold
  more often.
- **P2 failed.** I predicted 1–10 withdrawals; there were 0. I had priced the guard as binding near
  the margin. It does not bind anywhere on this book.
- **P3 held vacuously.** No GOOD/EXCELLENT offer was withdrawn, but none of any score was. It is not
  evidence of anything.
- **P4 half held.** Departures differ by 0 (≤ 2). Spend did not fall; it is identical.

## What this means

1. **The transfer the finding named is real, and it is decided at the threshold, not at the guard.**
   £400 of £3,830 went to accounts the company scores POOR/CRITICAL. The guard is an always-yes on
   this book, so no term inside it, bad debt or engagement, can redirect much. Engagement saved 10
   offers on 2026-10-05 only because it *multiplies* the value.
2. **The guard compares the account's whole value with the discount**, as if the offer certainly
   saves the account. The economic test is the offer's *incremental* effect on staying, times the
   value, against a cost paid to every account offered. The company has no learned belief about
   that effect. `company/analytics/counterfactual_retention.py` carries `_RETENTION_EFFECTIVENESS =
   0.20`, which its own docstring says has no source. Building the incremental guard on it would
   put an invented number into a decision, so it is **not done here**. Learning the effect from the
   company's own offered and not-offered renewals is the next item:
   `retention-guard-weighs-the-offers-learned-incremental-effect`.
3. **The netting stays, off by default.** It is the right valuation and costs nothing. It starts to
   matter once the guard can bind.

## Found on the way: a red already on HEAD

`tests/company/test_the_per_account_engagement_estimate_ranks_better_than_the_channel_alone.py::test_the_estimate_ranks_the_worlds_trait_better_than_the_channel_when_the_trait_is_there`
is red at `a5bef9df1` with HEAD's own `engagement_estimate.py`: planted lift 0.2725 against the
pre-registered 0.30 floor. That fits the refit's halved lift (C29 finding of 2026-10-05). Any commit
touching `company/crm/engagement_estimate.py` selects it and is refused, so this change put its
netting in the growth desk instead. That placement is equivalent: the charge comes off the margin
before the same function runs. The floor is a pre-registered threshold, so lowering it is a
judgement for C29's owner, not a fix. Recorded here, not changed.
