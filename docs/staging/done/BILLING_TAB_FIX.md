[SUPPLIER] Customer 360 BILLING TAB broken per Rich (live report, portal otherwise "much better"). Advisor pre-diagnosis attached -- fix with a real executed-JS reproduction, not a code read.

ADVISOR VERIFIED (via API, cannot execute the SPA):
- site/data/customers/*.json exist, invoices carry full itemisation, field contract (date/amount_gbp/status) MATCHES renderBills() exactly. Data layer sound.
- doLogin() correctly fetches both fuel legs (base + dual_fuel_combined.gas_account_id).
- C1 elec invoices correctly END 2020-12-29 (60 invoices) -- C1 churned Dec 2020 in SIM truth; RK replaced the old fabricated 120-bills-to-2025 with real ledger data.

DO, in order:
1. REPRODUCE with the established Node/vm DOM-harness pattern (QY/QZ style): drive the REAL page JS through login(C1) -> click Billing tab -> renderBillingTab()+renderBills() against the live C1.json/C1g.json. Capture the actual failure (exception? empty render? race where ACTIVE_TAB renders before the gas fetch resolves? BILL_FUEL toggle referencing a null leg?). Fix the real fault at root. Test with a churned customer (C1), an active-through-2025 customer (C4), a gas-only login (C1g), and a single-fuel customer.
2. CLOSED-ACCOUNT UX (likely part of what Rich perceives as broken): when an account's invoices end because the customer churned, the Billing tab must SAY so -- a status line like "Account closed Dec 2020 -- final bill C1-INV60" from the timeline/churn data -- never just silently show fewer years than the old page did. Honest data needs honest labelling.
3. REGRESSION: permanent harness test executing renderBills against the live C1.json artifact (not a mock), asserting non-empty render + year buttons + closed-account notice. The billing tab must never ship unexecuted again.
Report with the captured harness output per R1; visual acceptance stays with Rich.
