**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `value-arms-error-bar` · **Claim:** `read-selection-with-and-without-arrears-write-offs` (Lane 0 delivery)
**Class:** `no_caller_and_never_runs`

# The value arm cannot see arrears, because the pricing adapter never forwards them

Evidence and numbers: `docs/staging/records/SEAT_RESULT_THE_SELECTION_LEG_IS_A_CHURN_PART_AND_A_CREDIT_PART_AND_THE_VALUE_ARM_NEVER_SEES_ARREARS_2026-10-02.md`.

**The gap.** `ae101f936` says the arrears state reaches "`decide_margin(arrears_state=)` → `_score` → the
offered margin". On the production path it does not. `renewal_rate_chain` (line 437 on origin) calls
`renewal_margin_uplift`, and that calls `decide_margin` without `arrears_state`, `credit_risk`,
`payment_delay_days`, `behaviour_score`, `bill_shock_count` or `satisfaction_score`. So every value-arm
renewal is priced at `unknown` arrears and `medium` credit risk. The controls call `decide_margin`
directly and cannot see this.

**The defect behind it.** Once forwarded, `arrears_state` still enters only the churn hazard. The bad-debt
term in `expected_annual_costs` reads `credit_risk` alone. So a worsening debtor is priced *down* to
retain it, and its expected default never reaches the cost.

**Remedy (not done in this item, which forbade pricing changes):**
1. Forward the company's ledger state through the chain, which has the account and the term start, to `renewal_margin_uplift` and on to `decide_margin`.
2. Add a control that goes through `renewal_margin_uplift` and fails when the forward is dropped.
3. Decide, from published evidence, how an observed arrears position moves the expected bad-debt cost.

Step 3 is a knowledge question. No figure for it is established in this tree, and none is to be invented.

**Why it matters now.** The 1002b and 1002c selection legs are positive without write-offs (+£7,736 and
+£5,475). The sign is set by one account's credit loss. Until the arm can see credit, the selection leg
measures churn pricing *plus* a credit lottery the arm cannot enter.
