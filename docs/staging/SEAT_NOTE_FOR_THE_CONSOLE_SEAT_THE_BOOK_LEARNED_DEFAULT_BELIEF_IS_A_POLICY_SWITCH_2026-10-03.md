# For the console seat: the book-learned default belief is a policy switch your probe can flip

**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `unminted` · **Claim:** `the-company-default-belief-is-measured-against-its-own-ledger` (Lane 0 delivery)

**2026-10-03.** This is the hand-off the delivery item asked for. Nothing here touched
`tools/decision_probe.py` or `/var/tmp/se-probe*`.

## The switch

```python
dataclasses.replace(policy, renewal_default_belief="own_book")   # default: "segment_table"
```

`company/policy/decision_policy.py`; the names are `DEFAULT_BELIEF_SEGMENT_TABLE` and
`DEFAULT_BELIEF_OWN_BOOK`. On the default every run is byte-identical to before, and
`LivePaymentTriad.default_belief_rate` is never called. On `own_book` the run asks the triad's door at
each priced resi renewal. The rate chain resolves the switch from `active_policy()` beside the arm, so
re-ask the value rule inside `policy_scope`, the same way the flat-level arm is swapped.

**What it changes.** In `decide_margin`, the bad-debt cost on next year's bill becomes the book's
learned rate times the candidate's revenue. It replaces BOTH the segment table and the account's own
persistence term (`observed_non_payment_provision_rate`). The stock term on money already owed is
unchanged. The rate comes from `company/pricing/default_belief.py`: the company's own bad-debt charge
per GBP billed, by arrears state at the renewal, from outcomes resolved before that date, shrunk
towards 2.0% by one account-year. It is not keyed on payment method (see the prepayment finding
below).

## What the ledger says, decided blind to the probe

Full-decade run at `e69dbbfe5`, default policy, 175 resi accounts. The full row is in
`docs/institutional/knowledge_map.md`, *The company's own default belief, measured against its own
ledger*. Each belief at the start of an account-year, set against what that year was then charged
(n = 471):

| arrears state | table | persistence term (live since `e0370bf94`) | book-learned | charged |
|---|---|---|---|---|
| all | 2.00% | 6.48% | 2.84% | 2.17% |
| no_debt | 2.00% | 2.50% | 0.73% | 0.42% |
| in_arrears_steady | 2.00% | 7.41% | 3.30% | 2.53% |
| worsening | 2.00% | 13.82% | 6.81% | 5.55% |

The table is right on level and wrong on shape. The persistence term your fix put live is about 3x
high in every state. The book-learned rate is closest in every state and still reads high.

**My prediction for your probe, written before it runs.** The bad-debt part of the value rule's
selection shrinks on `own_book`. On today's code the arm charges a debtor about 3x its realised loss
and charges a clean payer more than its realised loss too, so its view of who is costly is inflated
across the board. I am NOT predicting the sign of the selection leg as a whole. Two seeds of a
residual whose per-seed sd is about GBP 4,700 cannot carry it.

## Read these beside the probe

- `SEAT_FINDING_THE_RENEWAL_PRICE_NOW_CHARGES_A_CLEAN_PREPAYMENT_HOUSEHOLD_MORE_THAN_A_CLEAN_DIRECT_DEBIT_ONE_2026-10-03.md`.
  `e0370bf94` crossed the director's 2026-09-23 prepayment line, by GBP 2.00-2.75/MWh, and
  `test_the_price_rests_only_on_observables_a_supplier_may_use` is red at HEAD. `own_book` closes the
  gap for clean accounts. The director has it on NTFY with a recommendation.
- `SEAT_FINDING_THE_COMPANY_LEDGER_BILLS_ONE_SETTLEMENT_RECORD_A_MONTH_NOT_THE_MONTHS_BILL_2026-10-03.md`.
  Your stock term reads absolute GBP from a ledger whose monthly bill is one settlement record (median
  GBP 0.023), so in a run it is close to zero.
- `SEAT_FINDING_THE_LEDGER_PAYS_BY_ONE_METHOD_DRAW_AND_THE_SEAM_REPORTS_ANOTHER_2026-10-03.md`. Your
  provision row is chosen by the seam's method, and the debt was produced under the other draw. They
  agree on 104 of 175 accounts.
