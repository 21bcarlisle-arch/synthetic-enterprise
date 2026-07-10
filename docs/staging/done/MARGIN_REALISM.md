# MARGIN_REALISM — levels, volatility, pressure, and who holds the difficulty dials (P1)

**Staged:** 2026-07-10 by advisor; director-decided after reviewing the new
percentage-margin surfaces. **Map cells:** E (opex), B (pricing/margin bridge),
W3 (cap as binding publication), REPORTING (revenue reconciliation), plus two
permanent method laws. **Sequencing:** gauge fix and diagnosis are immediate
(background-eligible); mechanism builds enter their lanes' loops in the order
below. Does not pre-empt in-flight map/pixel work.

## The observation (director, verified by advisor from site data)
Net margin % by year: 10.2 / 13.6 / 23.3 / 19.5 / 10.5 / 4.4 / 9.8 / 5.6 /
15.9 / 12.5. Real UK domestic retail: ~1-3% net in normal years, with negative
years (2018 killed real suppliers; we booked our best year). Gross swings
30-65% vs a fairly stable real ~35-45%. Levels ~5x too high; volatility far
too high. One good bone: 2021-22 crisis compression is directionally right.

## Two permanent method laws (CLAUDE.md)
**LAW A — anti-goal-seek:** margin (and any output metric) is a DIAGNOSTIC,
never a target. Plausibility bands, anchored to INDEPENDENT external sources
(Ofgem supplier-margin data), are sanity-daemon flags that trigger R4 on the
MECHANISM. No fudge factors, no calibrating outputs toward benchmarks, ever.
**LAW B — the baseline/curriculum split:** the BASELINE world (real 2016-25
history + externally-calibrated generators) may only change for
fidelity-to-reality reasons, decided blind to company P&L — never tuned
because company results look wrong. The CURRICULUM (which worlds the company
must live through: scenario batteries, population draws, stress regimes,
generated futures) is the DIRECTOR'S instrument: difficulty changes are named,
versioned, director-authored artefacts ("Scenario: 2018 price war"), never
silent parameter drift, and NEVER adjusted by the agent in response to company
outcomes. Rationale on record: the agent controls both sides of the wall; the
curriculum must face the director, not the builder. If the game is too easy the
director hardens it — and right now, toughening and fidelity are the SAME
backlog, because the world is easy chiefly because it is incomplete.

## Work, in strict order (attribution between every step via the margin bridge)

### 1. Fix the gauge first (REPORTING — immediate)
Two revenue series disagree by ~40% (supplier.json years[].revenue_gbp vs
fra_ratio_series annual_revenue_gbp, e.g. 2016: 10,417 vs 15,362). Root-cause,
define THE revenue (and the margin denominator) once, reconcile every surface,
add to the consistency gate. No mechanism work lands until percentages are
computed on a trustworthy base. Also state clearly what "gross" and "net"
currently include/exclude, per year, on the surface itself.

### 2. Diagnosis: the per-year margin decomposition (background, R9)
For each year: decompose margin into its drivers (commodity cost vs revenue,
hedge P&L contribution, policy/network shares, bad debt) and produce the
missing-cost-lines list vs a real domestic bill stack. Output: one document,
evidence-cited; it becomes the margin bridge's seed (Lane B).

### 3. First mechanism — the cost of being a company (Lane E)
Build the opex/cost-to-serve line: anchored £/customer/yr (external sources:
published supplier accounts, Ofgem cost stacks; register anchors), covering
service, billing/systems, acquisition amortisation, overhead. SUPPLIER-side
only; no world parameter touched. Re-run; bridge attributes the level shift.
Expected direction: net toward low single digits. If it lands wildly off, LAW A:
investigate mechanisms, do not tune.

### 4. Second mechanism — hedge-tariff alignment (Lane B)
Volatility fix: cost is locked when price is locked — hedging aligns to priced
tariff commitments (fixed books hedged at signing horizon; SVT hedged to the
cap-observation logic). Residual margin variance = shape/volume/churn only.
Bridge attributes the volatility change.

### 5. Third mechanism — the cap binds (W3, world-side, one change alone)
The existing price-cap module becomes a BINDING constraint on SVT pricing,
arriving as a regulatory publication event (fidelity: it is one). This is a
baseline-fidelity change (the cap really existed from 2019), not curriculum.
Bridge attributes the compression.

### 6. Register, do not build: the pressure roadmap (director's difficulty rack)
Register in the map as named capabilities with the CURRICULUM tag where
applicable: competitor field (W2 — the price ceiling), working-capital/cash
seasonality squeeze (E — the liquidity trade-off), settlement true-up risk
(W3/D — rides the epoch-2 spine), hostile population draws + adverse generated
futures (epoch 4 — invented difficulty, arriving where invention is the point).
These are the "more structural and strategic trade-offs" — sequenced, named,
director-ranked.

## Side-tagging rule
Every commit under this programme carries a tag: SIM-BASELINE / CURRICULUM /
SUPPLIER / WALL / REPORTING. Nobody should ever have to wonder which side of
the wall a change lived on.

## DoD
Gauge reconciled + gated; diagnosis doc filed; opex live with bridge
attribution and pixel-verified surfaces; alignment live with volatility
attribution; cap binding with compression attribution; pressure roadmap
registered with curriculum tags; both laws in CLAUDE.md. Margin surfaces then
re-read by the director — HIS Expert Hour is the close, not a green suite. One
NTFY per completed step (pixel rule applies).