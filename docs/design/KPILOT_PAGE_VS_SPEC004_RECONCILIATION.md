# Reconciliation — the PAGE vs Board Spec 004, gaps named

**Deliverable #2** of `DIRECTOR_RULING_KPILOT_SCOPE_FIRST_2026-07-28.md` (ruling §2). Every expectation
in the blind Spec 004 either **appears on the page** (or a child), or is recorded here as a **named
gap**. The ruling's complaint is precise: *"the page appears not to have been reconciled against it."*
This is that reconciliation.

**Distinct from `docs/design/BOARD_SPEC_004_RECONCILIATION.md`**, which scores Spec 004 against the
built **machinery** (what the sim knows). This scores Spec 004 against the **PAGE** (what a reader
sees). The machinery doc is the "what we actually know" input; the gap between the two — things the
machinery knows but the page never surfaces — is itself part of the punch-list.

## Evidence basis (R9 / R11)

- **Scored against:** `site/data/knowledge_wholesale.json` (as_of 2026-07, claims last_verified
  2026-07-25), which `site/knowledge/wholesale-price-formation/index.html` fetches at runtime
  (`fetch("../../data/knowledge_wholesale.json")`) and renders 1:1 into the rung blocks via its
  `set(...)` calls. This IS the rendered content source. — *observed.*
- **Not yet done here:** a Playwright live-fetch asserting each rendered pixel value. That belongs to
  the delta's publish step (#5, R11 verify-to-pixel) — flagged, not claimed. Rows below cite the data
  field that renders; a value marked PRESENT is present *in the rendered source*, pending the #5 pixel
  check. — *labelled honestly per R9.*

## Scoring key

- **PRESENT-ON-PAGE** — the expectation is treated on the page itself.
- **PRESENT-WEAK** — mentioned but incomplete (e.g. qualitative where a number is required).
- **PRESENT-ON-CHILD / STUB-ONLY** — a topic-graph child exists; STUB-ONLY means it is a stub, not yet
  a treatment.
- **NAMED-GAP** — the page explicitly names this as a gap in the "Where our picture is still weak"
  block (the honest column — these are *good*: named, not hidden).
- **ABSENT-UNNAMED** — neither present nor named as a gap. **These are the defect** — they feed the
  #4/#5 punch-list.

---

## A. Spec 004 disqualification battery (§5), row by row

| # | Spec 004 battery item | Score | Evidence / where on page |
|---|---|---|---|
| 1 | Power anchored to gas + carbon (marginal-unit arithmetic) | **PRESENT-ON-PAGE** | `headline`, `plain`, `theory` SRMC + `worked` example; figures ccgt_eff 49%, gas_ef 0.183, carbon_support ~£18. Strongest part of the page. |
| 2 | Hockey stick / scarcity convexity | **PRESENT-WEAK** | Magnitudes present (`expected_shape.crisis_tail` several hundred £/MWh; `cashout_ceiling` £6,000). But the *mechanism* (climbing the stack through peakers/imports/DR; the convex price–residual-demand surface) is **ABSENT-UNNAMED**. |
| 3 | Negative prices at real frequency | **PRESENT-WEAK** | `expected_shape.negative` = "occur in a small share of periods in high-renewables years." Qualitative only — **no numeric low-single-digit % frequency** and no trend. Spec 004 requires the frequency. |
| 4 | Wind correlated with price (displacement) | **PRESENT-WEAK** | `plain`/`theory` imply residual demand and "windy day" but never state the wind→price displacement at delivery explicitly. |
| 5 | Reversion to a fixed mean / regime layer / 2021–22 containability | **ABSENT-UNNAMED** | Page cites "2021-2022" spike magnitudes only. **Nothing** on mean reversion, regime shifts, level-that-jumps, or the 2021–22 containability lesson. Major gap. |
| 6 | Storage in gas formation / winter–summer spread | **ABSENT-UNNAMED** | No storage, no seasonality, no winter–summer spread anywhere. |
| 7 | Jumps / fat tails / vol clustering (non-Gaussian) | **ABSENT-UNNAMED** | Not addressed. |
| 8 | The severed joint driver (weather moves demand AND price together) | **ABSENT-UNNAMED** | Gas-sets-price and renewables are present, but the *joint* driver (one weather draw moves demand↑, wind↓, gas-burn↑, prices↑ together) — the shared disqualifier of Specs 001/002/004 — is not stated. |
| 9 | Forwards that forecast / risk premium / term structure | **STUB-ONLY** | Topic graph has a `hedging-forward-market` stub (class settled/slow); the price page says nothing on forward-≠-forecast or risk premia. |
| 10 | Flat volatility (seasonal vol, vol→delivery) | **ABSENT-UNNAMED** | Not addressed. |
| 11 | No outage process / interconnector + foreign-fleet shocks (French channel) | **ABSENT-UNNAMED** | No interconnectors, no outages, no 2022 French-nuclear channel. |
| 12 | Static regime / structural transition (growing zeros + spikes, shrinking middle) | **ABSENT-UNNAMED** | `residuals.marginal_hours_gap` notes gas load factors falling ~50%→28% (a hint), but the bimodal transition is not explained. |

**Battery tally:** PRESENT-ON-PAGE 1 · PRESENT-WEAK 3 · STUB-ONLY 1 · ABSENT-UNNAMED 7.

## B. Director §3 named-gap list, row by row (the reader-facing scope)

| Director §3 item | Score | Evidence / where on page |
|---|---|---|
| **Structure of wholesale prices** (baseload/peak, seasons, quarters, months, day-ahead, within-day; shape) — *director's #1, "possibly the most important thing we use"* | **ABSENT-UNNAMED** | The traded-product structure appears **nowhere** on the page. The single largest scope hole. |
| Gas as the global anchor (NBP/TTF, LNG, gas sets power for most hours) | **PRESENT-WEAK** | "Price follows gas" is the page's core claim (`one_line`, `plain`); but **NBP/TTF, LNG as marginal cargo, the global channel** are absent. Gas-*sets*-power present; gas-*price-formation* absent. |
| Weather → demand AND generation | **PRESENT-WEAK** | Weather implicit via "windy day"; the demand-and-generation joint route is not drawn out (see battery #8). |
| Interconnectors and imports | **ABSENT-UNNAMED** | Absent. |
| CfDs and renewable support (merit order AND consumer cost) | **ABSENT-UNNAMED** | `gas_exposure ~30%` figure is present but the CfD mechanism and the dispatch-cost-vs-consumer-cost split are absent. |
| Negative prices (when, why, how often) | **PRESENT-WEAK** | When/why partly implied; **how often not quantified** (battery #3). |
| Seasonality across the year | **ABSENT-UNNAMED** | Absent (battery #6). |

## C. What the page HAS that Spec 004 credits (keep — ruling §6)

- **Marginal-price principle + SRMC arithmetic** with real cited figures (DUKES, DESNZ, HMRC) —
  PRESENT-ON-PAGE, strong.
- **Carbon**: CPS ~£18 present *and* the traded-ETS-series absence honestly named (`ets_gap`).
- **Falsifiable expected-shape bands** (baseload £40–90, crisis tails, £6,000 cash-out ceiling,
  negative prices) — the "what the data should look like" discipline is good.
- **Four honestly named gaps** already on the page (`reduced_form`, `ets_gap`, `marginal_hours_gap`,
  `coal_om_gap`) — the machinery good the ruling says to keep and refill.
- **The belief-revision block** (hedging near-naked → 0.80–0.90) with both clocks — the two-clock
  mechanic the ruling explicitly preserves.

## D. Punch-list — ABSENT-UNNAMED rows feeding deliverables #4/#5

These are the rows that are **neither present nor named** — the delta the director is buying. Each
becomes a named gap on the page (#5) and a backlog mint-source
(`DIRECTOR_RULING_PUBLISHED_GAPS_ARE_THE_BACKLOG`):

1. **Traded-product structure** (baseload/peak, seasons/quarters/months, day-ahead/within-day, shape) — *highest priority; director's #1.* → scope-brief **S2**.
2. **Gas price formation** — NBP/TTF, LNG marginal cargo, storage, the global channel (not just "gas sets power"). → **S4**.
3. **Interconnectors / imports** and the French-nuclear channel. → **S7**.
4. **CfDs & renewable support** — merit-order effect *and* consumer-cost effect. → **S8**.
5. **Seasonality & storage** — winter–summer spread, injection/withdrawal logic. → **S11**.
6. **Regimes & 2021–22** — reversion to a level that jumps; containability-after-onset. → **S12**.
7. **Forwards & risk premia** — forward-≠-forecast; promote the stub. → **S13**.
8. **The joint driver** stated explicitly. → **S6**.
9. **Non-Gaussian dynamics** — jumps, fat tails, vol clustering, outage process. → **S7/S10**.
10. **The structural transition** — bimodal distribution, growing zeros + spikes. → **S14**.
11. **Negative-price frequency**, quantified (upgrade PRESENT-WEAK → complete). → **S9**.
12. **Scarcity mechanism** behind the magnitude bands (upgrade PRESENT-WEAK). → **S10**.
13. **Rung-5 charts** — price series, merit-order stack, seasonal shape, negative-price frequency. → **S15** (deliverable #4).

**Headline finding:** the page is strong and honest on *how the marginal plant sets the price* (S1/S3/
S5) and correctly names four machinery gaps — but is **ABSENT-UNNAMED on the majority of the topic**,
including the single item the director ranked first (the traded-product structure). It is, exactly as
the director said, "too big and too small at once": a hub-shaped skeleton on the marginal principle
with the price-formation *body* missing and, critically, **not named as missing**. The fix is not
more prose in the existing blocks — it is the decomposition (#3) plus filling/naming these 13 rows.

---

*Provenance: deliverable #2, doc-only reconciliation, no maturity-map level claimed. Reads Spec 004
(exists) + the machinery reconciliation (exists) + the page's live data source. Feeds #3
(decomposition) and #5 (delta). 2026-07-28.*
