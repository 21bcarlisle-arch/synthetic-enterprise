**Severity:** LATENT · **Lane:** A_strategy_governance · **Atom:** `value-arms-error-bar` · **Class:** `measurements_that_mirror`

# Pre-registration: the balance-at-close write-off rule, run alone

**2026-09-27, filed before the rule is built and before any run.** The design is
`docs/staging/SEAT_DESIGN_THE_WRITE_OFF_RULE_RE_KEYED_TO_THE_BALANCE_AT_CLOSE_2026-09-27.md`, and the
result it is graded beside is
`docs/staging/records/SEAT_RESULT_THE_SELECTION_SWITCH_IS_ONE_ACCOUNTS_CHURN_ROLL_AND_ITS_MONEY_IS_THE_WRITE_OFF_RULE_2026-09-27.md`.

## The one variable

`simulation.arrears_engine.compute_emergent_bad_debt` and `compute_debt_recovery` change from
"every failed or disputed bill of an eventual leaver is written off at due+90 (dispute: +60)" to
"failed and disputed bills add to a running balance, and at close the balance is written off, dated
at the final bill's due date (C4 convention). A live balance with no payment for six years is
statute-barred (leg 4a). A stayer's provision is None (leg 4b)." The bills, behaviour, churn set
and seed are held fixed. The measurement runs both rules in one process over the same inputs:
`docs/reports/run_output_latest.json` (10,681 bills, 90 churned accounts). The two-state rerun
(`longjob-two-state-diff-rerun-20260927`, pid 42827) is still resident at about 9 GB, so no second
multi-GB run is launched. The per-account swing on `PROS-2016-0098` is graded by construction from
the same function, not from a new world run.

## The design's prediction, as written

- **D1.** The leaver's write-off falls, because cured bills leave the total.
- **D2.** The stayer's cost is unchanged at zero, because leg 4b is a gap.
- **D3.** The selection sign therefore moves toward retention.

## The seat's own predictions, derived from the build's constants before running

The design keeps C1, C2b and C3b at None, so the build has **no cure path**. There is no
re-presentation (C2 is blocked on C1 and C2b), and no arrangement paydown (C3b has no household
probability). A later successful payment pays its own bill. On a running account, balance = bills −
payments, so a payment of one bill's amount leaves the arrears where they were. The balance at
close is therefore the sum of the failed and disputed amounts, which is the old rule's amount.

- **S1.** Leaver write-off before recovery: **identical to the old rule to the penny for all 90
  churned accounts**, summed over years. So **D1 is REFUTED**.
- **S2.** Dating: no leaver write-off £ moves to an EARLIER year. A positive share moves LATER.
- **S3.** Recovery (DCA / sale): the per-account total can differ, but only because the archetype
  is read at the write-off year and that year moves. Book total within 10% of the old rule.
- **S4.** Stayer cost: zero under both rules (**D2 holds**). Leg 4a fires **0 times** on the real
  book, since every stayer makes payments that restart the clock (s.29(5)).
- **S5.** The £6,766.59 write-off swing on `PROS-2016-0098` is **unchanged in amount**: the account
  churns in both fates and each fate writes off the sum of its failed bills under either rule. So
  **D3 is REFUTED**. The selection sign does not move. The lever that would move it is C2b or C3b,
  not the write-off's key.
- **S6.** A write-off dated in a year with no settlement record for that account is dropped by
  `apply_emergent_bad_debt` (it keys on the last record of the (customer, year)). The final due
  date is period_end + 14, so a December close lands in January. Under the new rule the dropped
  amount is non-zero on the real book. I cannot say whether it is larger or smaller than under the
  old rule, and I will report both.

If S1 fails, a cure path I did not see exists in the build, and that is the finding.
