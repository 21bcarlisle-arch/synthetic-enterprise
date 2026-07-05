[SUPPLIER] CUSTOMER 360 REDESIGN -- director critique of the live C1 page. Current state: a dark-themed data dump. Target: a professional SaaS CRM account view. This elaborates WEBSITE_AS_SHOWCASE tab 4 and takes priority within it.

DIRECTOR CRITIQUE OF CURRENT PAGE (C1, live):
- Elec account page with a gas widget, not a dual-fuel customer: Account Details says "commodity: electricity" under a Dual Fuel header; gas has NO tariff/meter/contract/bills shown.
- ZERO consumption anywhere -- an energy CRM without kWh. Meter says Smart; show the data.
- NO timeline: none of the event ledger, life events, offers, payments, complaints on the record.
- NO actions: no renewal countdown, no next-best-action, nothing to DO.
- Numbers do not reconcile on-page (GBP339 margin vs GBP1,949 net-after-CTS unexplained; 120 bills GBP4,520 vs GBP3,498 revenue; P&L table stops at 2020).
- No IA: one scroll, uniform card weight, no charts, metric soup without definitions.

THE REDESIGN -- Customer 360, structured as a household with accounts:

1. HEADER IDENTITY STRIP: customer/household identity (synthetic persona name + property archetype from the human sim), segment + vulnerability/PSR flags, tenure, satisfaction indicator (company-observed), live balance, contract status PER FUEL with renewal countdown chips. This is the who/where/state in 3 seconds.

2. TABBED IA (not one scroll): Overview | Accounts | Consumption | Billing & Payments | Timeline | Risk & Actions.

3. ACCOUNTS TAB: two first-class account panels -- Electricity (MPAN) and Gas (MPRN): tariff name + unit rate + standing charge, contract start/end + renewal window state, meter type/serial, EAC. Combined roll-up on Overview only.

4. CONSUMPTION TAB: monthly usage chart per fuel across the full history, weather overlay (the physics visible), smart-meter granularity where held. This is the product's core noun -- it must be a chart, not absent.

5. BILLING & PAYMENTS: statement view (bill -> payment -> balance running ledger), bill DRILL-DOWN with the full itemisation the sim already computes (commodity/network/levies/standing/VAT per fuel), payment method + DD status, arrears aging + payment-plan state where applicable.

6. TIMELINE TAB: the QP decision event ledger rendered for this customer -- company-observed events (contacts, complaints, bills, payments, offers WITH their H1 EV, tariff changes, dunning steps) in sequence. This is where the week's architecture becomes visible per-customer.

7. RISK & ACTIONS: churn journey stage AS THE COMPANY INFERS IT (not sim truth -- portal is the company view), trend not just a number; three-horizon value (H1 committed / H2 realized / H3 forecast) replacing the current metric soup, each with a one-line definition; NEXT BEST ACTION from the decision loop with its EV ("Renewal in 43 days -- recommended: fixed-offer X, EV +GBPz").

8. RECONCILIATION RULE (consistency gate extended to page level): every roll-up on the page must visibly reconcile -- combined = elec + gas on the same screen; bills total ties to revenue with the difference labeled (VAT/standing); P&L covers ALL years. A page that cannot explain its own numbers fails the gate.

9. DESIGN SYSTEM: this page is the reference implementation for the site/ design system (grid, type scale, chart components, card hierarchy with sparklines on KPIs). Professional, restrained, data-dense. Charts are mandatory: usage, margin by year, value trend.

ACCEPTANCE: Rich's eyes on the live C1 page. Report "awaiting Rich's visual review" -- the case-study recommender should then link into these views.
