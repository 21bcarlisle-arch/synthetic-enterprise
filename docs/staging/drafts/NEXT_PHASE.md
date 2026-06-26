# Phase 79 Proposal: Portal consumption history page

**The gap:** The Destinationvision Portal MVP spec requires "Consumption: half-hourly chart for
HH customers, monthly for others." The portal currently has login, dashboard, bills, tariff
comparison, and trading views — but no consumption data view. This is the last mandatory
element of the Portal MVP.

The Destinationvision's key test: "When Rich logs in as C7 (HH smart meter customer) and sees
their half-hourly consumption chart with peak/off-peak pricing overlaid, the simulation stops
being abstract. The customer experience is real."

**What to build:**

1. company/billing/consumption.py (new):
   - read_consumption_history(account_id, db_path) → list of {period, kwh, month, year}
   - Reads from the invoice DB (total_consumption_kwh per billing period already stored in bills)
   - group_by_month(records) → monthly totals with year/month labels
   - For HH customers (C7–C9, metering=="HH"): flag is_hh=True

2. company/portal/app.py:
   - GET /account/{id}/consumption route
   - Loads consumption history via read_consumption_history()
   - Passes is_hh flag (from saas.customers)
   - Renders templates/consumption.html

3. company/portal/templates/consumption.html (new):
   - Table of monthly consumption (year, month, kWh, running total)
   - HH customers: banner "Smart meter data — half-hourly resolution available"
   - Dashboard: add consumption link alongside bills and tariff-compare

4. Dashboard template update: link to /account/{id}/consumption

5. Tests (~10 new in tests/company/portal/test_consumption.py):
   - test_consumption_route_returns_200
   - test_consumption_shows_monthly_totals
   - test_hh_customer_shows_smart_meter_banner
   - test_consumption_unknown_customer_returns_404
   - test_consumption_history_groups_correctly
   - (etc.)

**Why this phase, not something else:**
- The Destinationvision explicitly calls the consumption view out as a Portal MVP requirement
- Invoice DB already has total_consumption_kwh — no new SIM interface needed
- Completes the customer journey: login → dashboard → bills → consumption → tariff compare
- Makes the "customer is real" test passable without any architecture changes

**Files changed:** company/billing/consumption.py (new), company/portal/app.py (extended),
company/portal/templates/consumption.html (new), company/portal/templates/dashboard.html
(minor: add link), tests/company/portal/test_consumption.py (new). ~10 new tests.
