# poesys.net — Four-Section Vision and Restructure

## The Architecture

poesys.net is restructured into four top-level sections with a
persistent navigation bar. Each section is a distinct view of the
same underlying system, from a different perspective and for a
different audience.

The four sections map directly onto the project's long-term vision:
- SIM is the world
- Supplier is the company operating in that world
- Customers is what the company's decisions feel like to a person
- Project is the evidence that the methodology works

---

## Section 1 — SIM (The Market Environment)

**What it is:** Ground truth. The complete UK energy market
environment as the simulation models it. This is what actually
exists — not what the company thinks exists.

**Why it matters for the project:** The SIM is the forcing function.
Every time it models something the company can't yet handle — a new
customer life event, a regulatory change, a market structure shift —
it creates pressure to build real company software to respond. A
customer moves house in the SIM; the company has to build a home
move process. A price cap changes; the company has to build
cap-compliant tariff logic. The SIM drives feature build.

**What it shows:**

*Wholesale Market*
- Spot prices (SSP) 2016-2025 — the real Elexon data
- Forward curve by tenor: day-ahead, season-ahead, year-ahead
- Bid-ask spread and liquidity conditions
- Market regime indicator: CALM / VOLATILE / CRISIS
- 2021-2022 crisis timeline: when prices spiked, how high, how long

*Physical Market*
- Demand by region and settlement period
- Generation mix: gas, wind, solar, nuclear, interconnectors
- Balancing mechanism: system long/short, BM prices
- Interconnector flows: IFA, BritNed, VikingLink

*Weather*
- Temperature by location (London, Manchester, Glasgow, Cotswolds)
- HDD/CDD — the demand drivers
- Wind and solar irradiance
- Correlation with demand and price spikes

*Regulatory Environment*
- Ofgem price cap by quarter 2019-2025
- Policy cost stack by year: RO, FiT, CfD, CM, CCL rates
- Regulatory calendar: upcoming obligations, consultations
- Key events: SoLR appointments, supplier failures 2021-2022

*The Customer World (human simulation layer — build toward this)*
- Simulated population: household types, property characteristics
- Life events distribution: births, moves, job changes, retirements
- Fuel poverty geography: LIHC bands by region
- EV adoption curve, heat pump penetration, solar rollout
- Behaviour segments: price-sensitive, loyal, vulnerable, engaged
- This is the hyper-personalised human simulation — the most
  distinctive part of the project. The SIM knows what a real
  supplier cannot: the true state of each customer's life.

**Transition to real:** SIM interfaces swap to real feeds —
N2EX/ICE for wholesale, Elexon API for settlement, Met Office
for weather, Ofgem publications for regulatory. The section
structure doesn't change. Only the data source changes.

---

## Section 2 — Supplier (The Company MI)

**What it is:** The company's view of itself — but only what it's
allowed to see. This is the epistemic layer made visible. The
company does not see SIM ground truth; it sees what it can observe
through its own records, market data feeds, and customer interactions.

**Why it matters for the project:** This section proves the company
can operate autonomously. It shows the decisions the company makes,
the outcomes those decisions produce, and whether they're working.
The gap between SIM ground truth (Section 1) and what the Supplier
can see (Section 2) is the epistemic cost — the price of imperfect
information — made visible.

**What it shows:**

*Trading Desk*
- Open forward positions by customer and tenor
- Portfolio P&L: actual vs naked counterfactual
- VaR: current vs stressed floor, mandate compliance
- Hedge effectiveness: did the hedging strategy add or cost value?
- Forward curve: company's estimate vs SIM ground truth (the gap)
- Risk committee: interventions, decisions, outcomes

*Financial*
- P&L waterfall: revenue → wholesale → gross → capital → net
- Balance sheet: cash, receivables, forward book MTM, VAT liability
- Cash flow: operating, investing, financing
- Management accounts: monthly close, variance vs benchmark
- Treasury: position, headroom, working capital

*Customer Book*
- Book composition by segment
- Churn risk by customer (company estimate vs SIM truth)
- CLV by customer — who creates and destroys value
- Retention offers: made, outcomes, ROI
- Bill shock events: count, severity, customer impact
- Vulnerability register: flags, severity, actions taken

*Operations*
- Billing: invoices issued, paid, overdue, bad debt
- Collections: arrears by age, escalation pipeline
- Complaints: open, resolved, ombudsman referrals
- Regulatory filings: submitted, due, overdue

*Insights (the "so what" layer)*
- Executive coherence narrative: one paragraph, what the business
  is doing and whether it's working
- Per-area "so what": trading, customers, risk, financial, operations
- Recommended actions: what the company should do differently
- Trend: is performance improving or deteriorating run-on-run?
- Anomaly flags: anything outside expected range, highlighted

*Talk to the Supplier Data*
- Natural language query: "which customers were unprofitable in 2022?"
- Claude API with run data as context
- Answers questions about the company's own records

---

## Section 3 — Customers (The Customer Portal)

**What it is:** The company's decisions as experienced by a person.
Log in as any simulated customer and see exactly what that customer
sees — their bills, their consumption, their account, their options.

**Why it matters for the project:** This section makes the simulation
real. When you log in as C7 (HH smart meter on ToU tariff) and see
a half-hourly consumption chart with peak/off-peak pricing overlaid
and a real invoice you can download — the company stops being
abstract. This is the test: does it feel like a real energy supplier?

It also proves the transition is possible. The portal is built the
same way whether the customer is simulated or real. When real
customers arrive, only the authentication layer changes.

**What it shows:**

*Home screen (after login)*
- Current tariff name and unit rates
- Last bill: amount, due date, payment status
- Next renewal date and current contract term
- Account balance

*Bills*
- List of all invoices: date, amount, status (PAID/UNPAID/OVERDUE)
- Click any invoice: full line-item breakdown
  - Consumption (kWh)
  - Unit rate(s) — peak/off-peak for ToU customers
  - Standing charge
  - Non-commodity costs (itemised by levy: RO, FiT, CfD, CM, CCL)
  - Subtotal ex-VAT
  - VAT
  - Total due
- Download invoice as PDF

*Consumption*
- Monthly bar chart (all customers)
- Half-hourly chart last 30 days (HH/smart meter customers)
- Peak vs off-peak split (ToU customers)
- Year-on-year comparison

*Account*
- Tariff details and contract dates
- Payment method and direct debit status
- Contact preferences
- Vulnerability flags (if any — shown sensitively)
- Renewal options: what tariffs are available

*For I&C customers*
- Settlement statement by period
- Volume tolerance position: contracted vs actual
- Half-hourly demand profile
- CCL and climate change agreement position
- Capacity market obligations

*Talk to your account*
- Customer can ask questions: "why is my bill higher this month?"
- Claude API with that customer's data as context
- The company's service layer responds
- This is where the autonomous customer service capability lives

**Login:** account number only (C1, C7, C_IC1 etc.) for simulation.
No password needed until real customers arrive.

**URL:** poesys.net/customers/ — part of the main Cloudflare Pages
site, not a separate service. No port numbers, no Tailscale required.

---

## Section 4 — Project (The Evidence Layer)

**What it is:** The meta view. What this project is, what it's
discovered, what it's built, and where it's going. The investor
deck in live dashboard form, updating automatically as the project
progresses.

**Why it matters for the project:** The simulation-first methodology
is the thesis. This section proves it works. Every major discovery
is documented. The velocity charts show autonomous progress in real
time. The key findings — regime-change blindness, activity-based
pricing gap, forward curve overpricing, 2021 crisis survival —
are presented as evidence, not claims.

**What it shows:**

*About*
The project description (updated framing):
"Poesys is a high-fidelity autonomous simulation of a UK electricity
and gas supply business, running continuously against real
Elexon/NESO half-hourly settlement data (2016-2025). The goal is a
simulation detailed enough to say: 'that is how a real UK energy
supplier works' — and use it to build and prove the software that
would run one autonomously. When the software is proven, the market
interfaces swap from simulated to real — and the company transacts."

*Key Discoveries*
The things the simulation found that no specification would have:
- Regime-change blindness: how 28 real suppliers failed in 2021,
  replicated in simulation before the fix
- Activity-based pricing gap: large SME customers net-negative
  under flat margin pricing
- Forward curve overpricing: half-hourly sigma 4.3x too high,
  causing systematic margin inflation
- 2021 crisis survival: treasury drawdown, churn spike, recovery

*Build Evidence*
- Cumulative phases over time (chart)
- Test count growth over time (chart)
- Codebase size over time (chart)
- Simulated data generated (not downloaded) over time (chart)
- Current state: phases, tests, modules, run time

*Investor Summary Card*
Started: June 2026
Phase: [current] | Tests: [current] | Modules: [current]
Net margin (latest): £[X] | Treasury: £[X]
Survived: 2021-2022 crisis (30+ real suppliers failed)
Built by: 1 human (strategy) + Claude Code + Qwen (execution)
Time to transact: [what remains]

*Roadmap*
The remaining path to a transacting company:
- SIM interfaces → real market feeds
- Customer portal → real authentication, real customers
- Capital → when the blueprint is proven
The five transition tests from DESTINATION_VISION.md

---

## Implementation

### Navigation bar
Persistent across all pages. Four tabs: SIM | Supplier | Customers | Project
Current section highlighted. Mobile-first — collapses to hamburger on small screens.

### URL structure
- poesys.net/ → redirects to poesys.net/supplier/ (default view)
- poesys.net/sim/ → SIM section
- poesys.net/supplier/ → Supplier MI (current dashboard content)
- poesys.net/customers/ → Customer portal (replaces port 8000)
- poesys.net/project/ → Project evidence

### Migration
- Current dashboard content → moves to /supplier/
- Port 8000 uvicorn portal → moves to /customers/ as static+API
- Timeline/velocity → /project/
- PRIORITIES.md → /project/priorities/

### Phase order
1. Navigation bar and URL restructure (move existing content)
2. /customers/ portal live (replace port 8000)
3. /project/ section with about, discoveries, build evidence
4. /sim/ section starting with wholesale prices and weather
5. Insight layer and "talk to data" in /supplier/
6. Human simulation layer in /sim/ (long horizon)

## Gate

Phase is not complete until:
- Navigation bar visible on all pages on mobile
- poesys.net/customers/ loads and Rich can log in as C1
- poesys.net/project/ shows the investor summary and at least
  one velocity chart
- No port numbers or Tailscale IPs needed for any section

## NTFY on completion
1. "poesys.net restructured — 4 sections live"
2. "customers.poesys.net or poesys.net/customers/ — log in as C1 now"
3. "Project section: [URL] — velocity charts and build evidence live"
