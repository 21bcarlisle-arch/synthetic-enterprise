**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 4 · **Atom:** `C29_decisions_stop_being_lookup_tables` · **Claim:** released on landing

# The value-arm renewal price still reads no payment-behaviour score

The rest of `SEAT_FINDING_THE_PAYMENT_SCORE_REACHES_THE_CHURN_BELIEF_AND_THE_RETENTION_GUARD_PRICES_IT_AS_IF_THE_DEBTOR_PAYS_2026-10-07.md`
(in `done/`). Its guard defect is fixed on origin in `6870d3c8b`. That finding also named this
residue and did not fix it. It is filed here so that closing the parent does not drop it from the queue.

Read at HEAD `73577018f`, 2026-11-25:

- `decide_margin` (`company/pricing/value_based_renewal.py:837`) accepts `behaviour_score` and
  forwards it to `enriched_churn_estimate` (line 986).
- Its one adapter call (line 1575) has forwarded `arrears_state`, `credit_risk`,
  `unpaid_bills_by_age` and `payment_method` since 2026-10-03. It still does not forward
  `behaviour_score`. So the arm's churn term reads every account as having no payment history,
  while the renewal churn belief in `run_phase2b` (line 4520) does read it.
- `DISTRESS_SCORES` (line 286) is defined and read by nothing in the repository (grepped all `*.py`).

**Why it was not wired in this turn:** wiring it moves the value-arm controls' outputs. Raising a
debtor's believed leave probability inside a price is a judgement C29 owns. The state already moves
the hazard (Ofgem CIM w6 Table 56), so there is a double-counting question to settle first: does the
score add information beyond `arrears_state` for the same account, or does it re-count it?

**Next:** knowledge first. Say what each of the two signals counts. Then either forward the score
behind a `DecisionPolicy` flag whose off-arm is bit-identical, or delete `DISTRESS_SCORES` with a
named reason.
