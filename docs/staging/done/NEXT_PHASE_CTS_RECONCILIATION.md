[DESIGN NOTE] Cost-to-Serve Ledger Reconciliation -- Tier 3, proceeding in 4h unless redirected

## The bug (SUPPLIER_TAB_OVERHAUL.md FIX list: "Accounts waterfall shows CTS GBP0 every year vs
Insights cost-to-serve GBP91,780 -- reconcile (gate covers it)")

Confirmed against live data (docs/reports/run_output_latest.json, site/data/dashboard.json):
- management_accounts.annual[year].cost_to_serve_gbp is 0.0 for every year 2016-2025.
- cost_to_serve_portfolio_gbp (used in CLV/enterprise-value/customer-profitability elsewhere) is
  GBP91,780.10 for the same run.

## Root cause

company/finance/double_entry.py defines chart-of-accounts code 6100 ("Cost to Serve") and
income_statement() already derives cost_to_serve_gbp from that account's ledger balance -- but
to_journal_entry()'s event-type dispatch (lines 66-103) has no case for a cost-to-serve event.
No such event type is ever emitted by simulation/run_phase2b.py or saas/ledger.py, so account
6100 never receives a posting and always nets to zero. The 6100 account code appears to have
been set up in anticipation of this wiring, but the wiring itself was never done.

Meanwhile saas/cost_to_serve.py -- the module that DOES compute the real GBP91,780 figure, used
by enterprise_value.py, customer_profitability_scorecard.py, renewal_pricing_engine.py, and
fair_value_assessment_register.py for real per-customer profitability/pricing decisions -- has
two components per its own docstring: (1) fixed overhead (billing/IT/smart-meter, GBP55/120/500
per account per year by segment) and (2) a flat BAD_DEBT_RATE * revenue provision.

## The complication (why this is not a trivial wiring fix)

Phase QD (2026-07-04) replaced the flat-rate bad-debt formula used elsewhere in the P&L with
real, emergent bad debt from the payment/arrears model (simulation/arrears_engine.py) --
finding the flat formula overstated bad debt roughly 30x (GBP92,551 flat-rate vs GBP3,051 real).
That fix was never applied to saas/cost_to_serve.py's own BAD_DEBT_RATE component, which still
uses the old flat-rate assumption for the customer-value/pricing figures.

If cost_to_serve_gbp is wired into the ledger as-is (its current formula, including the flat
bad-debt component), the annual accounts' new CTS line would carry the same discredited bad-debt
assumption Phase QD superseded elsewhere on the SAME P&L -- alongside, not instead of, the real
emergent bad_debt_gbp line (account 6001) that already reflects the true arrears outcome. Two
different bad-debt figures for the same underlying economic event, on the same year's accounts.
This would also move the reported net margin/treasury for every one of the 10 historical years
by the introduced amount (currently GBP91,780.10 net, or less if the bad-debt component is
excluded per option B) -- a real change to the headline "net" figure quoted in every commit
message, LATEST.md, and ANNUAL_REPORT.md, not a cosmetic dashboard fix.

## Options

A. Wire cost_to_serve_gbp into the ledger unchanged (simplest, fastest, but re-introduces the
   discredited flat bad-debt assumption as a second bad-debt line alongside the real one).
B. Fix saas/cost_to_serve.py first -- drop its own BAD_DEBT_RATE component (bad debt is already
   owned by the emergent arrears engine), leaving cost-to-serve as pure fixed-overhead allocation,
   THEN wire that corrected (smaller) figure into the ledger. Changes the GBP91,780 headline figure
   itself and ripples into every downstream consumer (CLV, enterprise value, customer
   profitability scorecard, renewal pricing, fair value assessment) -- more correct, larger
   surface area, needs a full test-suite pass to catch any hardcoded expectations.
C. Leave the ledger's CTS line at GBP0 (i.e. treat cost-to-serve as a customer-value/pricing
   concept only, never a cash P&L line) and instead fix the SUPPLIER_TAB_OVERHAUL.md complaint by
   relabelling/footnoting the waterfall so it does not imply reconciliation with a figure it was
   never meant to include.

Recommendation: B is the architecturally correct fix (removes a real double-bad-debt-modelling
bug, not just a display inconsistency) but is the largest and most consequential of the three --
it changes reported net margin across the whole run history. Proposing to proceed with B unless
redirected, specifically because leaving a customer-value module quietly using bad-debt
assumptions Phase QD already disproved is a live pricing-decision-quality issue in the company
layer, not just a spreadsheet-reconciliation nicety.

## Tier classification

Tier 3 (novel finding, not literally what SUPPLIER_TAB_OVERHAUL.md's "reconcile (gate covers it)"
bullet anticipated -- that phrasing reads as a superficial wiring/display fix; the actual fix
changes a real financial calculation feeding company pricing decisions and the board's reported
net margin). Classifying up per CLAUDE.md's "if in doubt, classify UP." 4h opt-out window applies;
proceeding with option B if not redirected.
