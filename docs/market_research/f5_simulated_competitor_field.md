# F5 — Simulated Competitor Field (DISCOVER)

**Track:** F5, Forward-Discovery Register (mission-required × high).
**Status:** DISCOVER-only. No build, no new map atoms. Names candidate atoms as *proposals* only.
**Date:** 2026-07-22. **Author:** autonomous worker (forward-discovery tick).

**Provenance & honesty (R9).** Written without live network access (autonomous run). Quantitative
market-structure figures below are **author domain knowledge, recalled — labelled `[recall, validate]`**
and must be validated against the named independent sources before any figure is used in a build or a
board figure. Structural claims (archetypes, behaviours, the regime shift) are well-established and
low-risk; the market-share *numbers* are the part that needs a fetch. Register unverified figures in
`ASSUMPTIONS.md` on graduation, exactly as `COMPETITOR_PLATFORMS_2026.md` did.

---

## 1. The gap, stated precisely

The register's framing — "pricing/retention decisions currently face **no opposition**" — is confirmed
by the code. The competitor field today is a **scalar, not a field**:

- SIM side: `simulation/market_switching_propensity.py` → `MARKET_SAVINGS_BY_YEAR` (an exogenous
  £/yr series 2016–2025) feeding a piecewise savings-elasticity curve.
- Company side: `company/crm/market_conditions.py` → `MARKET_SWITCHING_MULTIPLIER_BY_YEAR` (a
  year-indexed multiplier, independently reimplemented from the same public DESNZ/Ofgem series —
  correctly walled).
- Observable-tariff plumbing already exists and is **correctly walled**:
  `company/market/tariff_benchmarking.py` reads only public sources (Ofgem comparison tool, uSwitch,
  DUKES, press notices). Nothing to fix on the wall here.

**The defect is not a wall violation — it is a missing feedback edge.** The "savings available" a
customer compares against is a *fixed historical series*, not the output of competitors reacting to
our tariff. Consequences that make retention meaningless:

1. **No price response.** If the company cuts price, no competitor matches; if it raises price, the
   best-alternative rate the customer sees does not move — churn rises per a fixed elasticity but no
   *named opponent* harvests the churn or defends its own book.
2. **No strategic share war.** A challenger burning capital for acquisition share (2016–2020) and an
   incumbent defending a fat back-book (SVT-anchored) are indistinguishable — both collapse to the
   same scalar.
3. **No regime interaction.** The scalar *encodes* the 2022 "nowhere cheaper to go" regime as a
   number (0.44), but the company can't *discover* that regime by watching competitor tariffs move —
   it's handed the answer. The coupled-triad GAP (belief vs truth) is therefore untestable here.

This is the minimum a competitor model must add: **make the best-alternative rate endogenous to (a)
wholesale/cap physics and (b) at least one competitor archetype that responds to our pricing.**

---

## 2. The real UK household competitor field (anchor)

Two structurally distinct eras, both inside our 2016–2025 baseline window — the model must be
**regime-aware** or it will be wrong in one era:

**Era A — challenger boom (≈2016–2020).** 50–70+ active domestic suppliers `[recall, validate]`.
Price competition intense; "tease-and-squeeze" the dominant challenger tactic (cheap 12-month
acquisition fix → roll to expensive SVT). Savings available £150–£350/yr. This is the era the model
must let a *strategic entrant* exist in.

**Era B — post-crisis consolidation (≈2022–present).** **29 suppliers failed Jul 2021–May 2022**
`[VALIDATED 2026-07-22 against independent already-fetched repo sources — not SIM ground truth]`:
`company_commercial_strategy.md:103` (Ofgem SotM 2025 / NAO), `energy_market_complexity_june2026.md:99`,
and `svt_rates_active_passive_2016_2025.md:75` all independently record **29 failures / ~4M customers
into SoLR**; SoLR mutualisation **~£2.7bn / ~£94/household** (`company_commercial_strategy.md:103`,
`energy_market_complexity_june2026.md:16,98`); ~one-third of customers back on fixed deals by Jul 2025,
matching the pre-crisis ~35% engaged share (`svt_rates_active_passive_2016_2025.md:80`, Ofgem SotM
Jan 2026). (`ofgem_regulation.md:84` says "28 by December 2021" — a consistent by-that-date subset of
the full Jul-21→May-22 wave, not a conflict.) The field collapsed to a post-consolidation oligopoly.
Approximate per-supplier household-supply shares below were the *era-shape* recall; the precise Q2 2025
per-firm shares are now **CLOSED against Ofgem *State of the Market* (Jan 2026) — see §8** (Octopus 25 /
British Gas 21 / E.ON 16 / OVO 12 / EDF 10 / Scottish Power 8; six-largest 92%). The table below keeps the
*archetype* mapping; use §8 for the calibrated figures:

| Archetype | Real exemplar(s) | ~share | Pricing behaviour |
|---|---|---|---|
| SVT-anchored incumbent | British Gas (Centrica) | ~20–24% | Prices at/near cap; heavy back-book; low acquisition appetite; high base inertia |
| Efficient tech challenger | Octopus Energy (absorbed Bulb) | ~20%+ | Thin margin, high NPS/service, tracker/Agile products; retention via service not just price |
| Consolidated incumbent | E.ON Next (+npower book), EDF, OVO (+SSE retail), ScottishPower | ~8–18% each | Cap-following fixed deals; moderate acquisition |
| Prepayment / PAYG specialist | Utilita | ~3–4% | Distinct segment, distinct cost-to-serve; largely off the switching-savings axis |
| Green-premium (values-led) | Good Energy, Ecotricity | small | Prices *above* market; retention via values, low price-elasticity |

Regulatory events that reshape competitor *behaviour* (already in `churn_price_elasticity.md`, restated
as behaviour-drivers): **Default Tariff Cap** (Jan 2019, compresses the acquisition/back-book gap);
**Acquisition Tariff Ban** (Apr 2022); **"Fairer for existing customers"** rule (~2023, *permanently*
removes new-customer exclusives → kills tease-and-squeeze, shifts competition from price to service).

---

## 3. The two poles the register names — and the minimum between them

The register asks for "tariff-following vs strategic entrants." These are the two poles; the minimum
useful model is a **two-tier field**, not 60 named firms:

**Tier 1 — deterministic tariff-follower band (the majority).** Best-alternative rate =
`f(price_cap, wholesale_forward, fixed_spread, era_regime)`. Does *not* react to our moves. Cheap.
Its value over the current scalar: the best-alternative rate becomes **endogenous to wholesale/cap
physics** rather than a hardcoded series, so the 2022 "nowhere cheaper to go" regime *emerges* from
the cap sitting below the wholesale-driven fixed price, instead of being asserted as `0.44`.

**Tier 2 — 1–3 strategic archetypes that respond.** A small set of agents with:
- an **acquisition appetite** (capital-backed for the challenger; back-book-defending for the incumbent),
- a **response function** on the gap between our tariff and theirs (undercut, match, or harvest),
- a **regime gate** (a capital-burning challenger only exists in Era A; the ban/fairer-pricing rule
  switches its tactic off in Era B).

This is what makes retention *meaningful*: underprice → an entrant matches and the share war costs us
margin, not just customers; overprice → an entrant harvests our churn and we can *observe* the loss.

**Simplicity guard (C-S / SIMPLICITY GUARD).** The minimum is a response *function* plus a regime
gate — not a multi-agent auction, not per-firm cost stacks for all 60. Resist building the boom-era
firm-by-firm; model the *band* + a handful of *archetypes*.

---

## 4. The epistemic wall (binding)

The competitor field is **SIM-side ground truth.** The company observes it only through the same
interfaces a real supplier has:

| The company MAY observe (public / own data) | The company may NEVER read (SIM internal) |
|---|---|
| Competitor **published tariffs** (PCW/Ofgem tool/press) — already `tariff_benchmarking.py` | Competitor **cost stacks, hedge books, capital positions** |
| Its **own** customer gains/losses (win/loss flows) | Competitor **churn curves / acquisition strategy / response function** |
| Published market-share stats (Ofgem SotM, lagged) | Which competitor a leaving customer went to *and why* (only aggregate, lagged) |

So the company must **infer** competitor strategy from observed tariffs + its own flows — and is
**allowed to be wrong** (the coupled-triad GAP). `company/market/market_share_estimator.py` already
does this inference shape; the field would give it something real to be wrong about. A modelled
competitor "acquisition appetite" is SIM truth; the company's *estimate* of it is a separate, walled
belief.

**No new wall crossing needed:** the observable feed already exists and is walled. The field lives
entirely behind the existing `tariff_benchmarking` observable — the company sees prices move, not the
strategy that moved them.

---

## 5. Independence & validation

- **Validation status (2026-07-22 tick, no live network — cross-checked against already-fetched,
  independent, published-source repo docs; the SIM scalar was NOT used as a check):**
  - **CLOSED — market structure:** the SoLR-failure count (**29 / ~4M / ~£2.7bn / ~£94/hh**), the
    post-2023 re-fixing (~one-third), and the two-era shape are now corroborated by ≥3 independent
    Ofgem/NAO-anchored docs (cited inline in §2). These no longer need a fetch.
  - **CLOSED — per-supplier % shares:** the §2 table's per-firm percentages were `[recall, validate]`
    with no repo-corpus corroboration; they are now closed against a live fetch of Ofgem *State of the
    Market* (Jan 2026) — Q2 2025 domestic-electricity shares Octopus 25 / British Gas 21 / E.ON 16 /
    OVO 12 / EDF 10 / Scottish Power 8, six-largest 92% (**see §8**, with the domestic-vs-all-sectors
    denominator caveat). No fetch-gated item now remains open in F5.
- The market-share table (§2) must be validated against **Ofgem *State of the Market* / retail market
  share data** and the SoLR-failure count against **Ofgem's SoLR record** — never against SIM ground
  truth (the scalar series is *not* an independent check; it is the thing being replaced).
- The savings-elasticity anchoring (`churn_price_elasticity.md`, DESNZ/Ofgem) is the **demand-side**
  half and stays authoritative — F5 supplies the **supply-side** rate the elasticity acts on. The two
  must reconcile: the field's best-alternative rate, run through the existing elasticity curve, must
  reproduce the observed 2016–2025 switching series **for fidelity reasons only** (R13 baseline wall —
  calibrate the field to reality, never to company P&L).

---

## 6. Candidate graduation shape (PROPOSAL ONLY — not map-registered)

If the director graduates F5, the natural minimal build (one coupled triad, per COUPLED_TRIAD doctrine):

- **SIM:** a two-tier competitor field (deterministic tariff-follower band + 1–3 regime-gated
  strategic archetypes) emitting a per-year best-alternative tariff behind the existing observable.
- **COMPANY:** consumes the observable tariff feed (unchanged wall), estimates competitor appetite
  from own win/loss, prices/retains against it — allowed to misread.
- **HARNESS:** measures the belief-vs-truth GAP (company's estimated competitor response vs the SIM's
  true response function) and asserts the field, run through the existing elasticity, reproduces the
  real 2016–2025 switching series.

No atom is opened here. This is the DISCOVER artefact only; BUILD-open is a director/twin call.

**Graduation hazard found this tick (code-anchored, non-network) — two scalars, one regime, both must
retire together.** The 2022 "nowhere cheaper to go" regime is currently encoded *twice, independently*:
`simulation/market_switching_propensity.py::MARKET_SAVINGS_BY_YEAR[2022] = -200.0` (SIM-side: "no
competitive alternative below SVT; fixed deals 1,000+ GBP more expensive") **and**
`company/crm/market_conditions.py::MARKET_SWITCHING_MULTIPLIER_BY_YEAR[2022] = 0.44` (company-side, an
independent reimplementation of the same public DESNZ/Ofgem series — correctly walled). Both are
hand-calibrated constants for the *same real-world fact*. When F5 graduates and the best-alternative
rate becomes **endogenous** (Tier-1 follower band = `f(cap, wholesale, spread, regime)`), the SIM
`MARKET_SAVINGS_BY_YEAR` scalar it replaces must retire **in lockstep** — otherwise the field emits an
emergent rate while the old scalar still drives elasticity, and the two silently diverge (a classic
half-migrated-parameter defect). The company-side `0.44` multiplier is on the *other side of the wall*
and stays a legitimately-independent belief (the company may keep its own calibration and be wrong — the
coupled-triad GAP), but the graduation build must be explicit about which of the two scalars it retires
(the SIM one) and which it leaves as a walled company belief (the multiplier). This is a *build-sequencing*
finding, not a new wall crossing: verified by reading both files this tick, neither against SIM ground
truth. It sharpens §6's SIM bullet — "emitting a per-year best-alternative tariff" must **replace**
`MARKET_SAVINGS_BY_YEAR`, not sit beside it.

---

## 7. One-line finding

**The competitor field is a scalar, not a field:** best-alternative rate is a fixed historical series,
so pricing/retention face a non-reactive opponent. The observable-tariff wall is already correct; the
missing piece is a *response edge* — the minimum being a cap/wholesale-endogenous follower band plus
1–3 regime-gated strategic archetypes. Market *structure* figures (29 supplier failures / ~4M customers
/ ~£2.7bn SoLR mutualisation / post-2023 re-fixing) are now **validated** against independent
already-fetched repo sources (§5); the per-supplier **% shares** were the last `[recall, validate]`
item and are now **CLOSED** against a live Ofgem *State of the Market* (Jan 2026) fetch — **see §8**.

---

## 8. Increment (2026-07-22, network-restored tick) — per-supplier % shares CLOSED

Network was probed live this tick (Ofgem reachable, HTTP 301) so §7's one remaining `[recall, validate]`
item — the per-supplier % shares — was worked against primary/regulator sources. **The item is now
closed;** none of these figures is SIM ground truth (all are public regulator/DESNZ data, the correct
observable side of the wall).

**Per-supplier domestic-electricity market share, Q2 2025 (Ofgem *State of the Market*, Jan 2026):**

| supplier | domestic electricity share |
|---|---|
| Octopus | **25%** |
| British Gas | **21%** |
| E.ON | **16%** |
| OVO | **12%** |
| EDF | **10%** |
| Scottish Power | **8%** |
| — six largest combined | **92%** (domestic elec + gas, Q2 2025) |

The six sum to exactly 92%, matching the reported top-six concentration — an internal consistency check
on the figures. The **head is heavy and the ordering matters:** Octopus (25%) has overtaken British Gas
(21%) to become the largest electricity supplier (~12.9m household accounts at 31 Oct 2024; ~23.7% of the
available market then, still climbing) — **the first change at the top since 1990s liberalisation**, and
Octopus is the *only* big-six supplier gaining share in both fuels. A tariff-follower band that treats all
competitors as one homogeneous pool would miss this: the field has a **growing disruptor** (Octopus,
share-taking) against **share-ceding incumbents** (British Gas 20.3%→21% is roughly flat; the tail —
E.ON/OVO/EDF/Scottish Power — is where share is bleeding).

**Denominator caveat, recorded so it can't mislead a build:** two "concentration" numbers coexist and are
*not* interchangeable. Ofgem's **domestic-only** top-six = **91% (Q4 2024) → 92% (Q2 2025)**. DESNZ's
*Competition in UK Electricity Markets 2024* reports top-six = **65%** and top-three = **45%** — but that
is the **all-sectors traded-electricity** denominator (industrial + commercial + domestic combined, where
smaller suppliers outside the top nine hold 21.9%). DESNZ's *domestic-slice* top-three is **44%**, far
closer to Ofgem's domestic concentration. A graduation build calibrating the competitor field to the
**domestic** market must use the Ofgem domestic series (92% top-six), not the DESNZ all-sectors 65% — the
gentle-looking lower number is the wrong denominator.

**How this sharpens §3/§6 (does not overturn them).** The minimum-useful model in §6 — a follower band +
1–3 regime-gated archetypes — is *confirmed* as the right shape, but the shares tell the archetypes what
to be: at minimum **(a) a share-taking disruptor** (Octopus's trajectory), **(b) share-ceding incumbents**
(the ex-Big-Six majors), and **(c) a long competitive tail** (the ~8% outside the top six, the SoLR-churn
source from §5's 29 failures). A single homogeneous "market rate" scalar cannot represent a field where
the largest player is *actively taking* share while the rest cede it — which is exactly the reactivity F5
exists to add. **No atom opened, no map level change** (BUILD-open is a director/twin call). This closes
the last non-churn network-gated increment on F5 — and, per the register lane-state, the **last one across
the whole F1–F5 register**.

**Sources (this tick):** Ofgem *State of the Market — Energy Retail Highlights* (Jan 2026,
`ofgem.gov.uk/sites/default/files/2026-01/State-of-the-Market-Energy-Retail-Highlights-January-2026.pdf`);
DESNZ *Competition in UK Electricity Markets 2024* (Sep 2025,
`assets.publishing.service.gov.uk/media/68da73e049e17d00a56ffb60/`); Ofgem retail-market-indicators data
portal; corroborated by Cornwall Insight / Solar Power Portal reporting of the Ofgem-confirmed Octopus #1
position. All observable-side public sources; none is SIM ground truth.

---

## 9. Increment (2026-07-22, later tick) — the switching-series calibration target is DOUBLE-VALUED, and the callable one is live-DISCONFIRMED

**Code-anchored finding, validated against a live independent source (network probed live this tick:
ofgem.gov.uk / gov.uk HTTP 200).** §5 names the F5 graduation calibration target precisely: "the field's
best-alternative rate, run through the existing elasticity curve, must reproduce the observed 2016–2025
switching series (R13 baseline wall)." This tick found that the repo holds **two independent "observed
switching series" that materially disagree in exactly the crisis years F5 hinges on** — and that they
diverge on *which* is sourced and *which* is a clean callable:

| year | `docs/market_research/churn_price_elasticity.md` §1 (cites DESNZ QEP 2.1 / Energy UK / Ofgem SotM) | `company/market/market_report.py::_UK_SWITCHING_RATE_PCT` (per-line unsourced) |
|---|---|---|
| 2017 | 14% | 18.5% |
| 2019 | 21% | 18.9% |
| **2020** | **23%** (6.39m) | **14.2%** |
| **2021** | **18%** (5.06m) | **6.1%** |
| 2022 | 3–4% | 2.8% |
| 2025 | 15–18% | 13.0% |

**Live-source adjudication (independent, observable-side, NOT SIM ground truth):** Energy UK electricity
switching (via Energy UK press + GOV.UK *Quarterly Domestic Energy Switching Statistics*) reports **2020 ≈
5.9m switches** and **2021 ≈ 5.1m switches ("14% lower than 2020")**. On the ~28m domestic-account
denominator that is **~21% (2020) and ~18% (2021)** — which **corroborates the `churn_price_elasticity.md`
series closely (2020: 23%/6.39m; 2021: 18%/5.06m ≈ exact)** and **disconfirms the `market_report.py`
series by ~3× in 2021 (6.1% vs a live-validated ~18%)**. The two series roughly agree only at the 2022
trough (2.8% vs 3–4%); for 2020–2021 the `market_report.py` numbers are not any recognisable published
gross-switch figure and carry no per-line citation (the module docstring claims Ofgem/Energy Trends/Citizens
Advice provenance generically, but the crisis-year values match none of them).

**Why this is a graduation hazard, not a live defect (severity, honestly stated).** `get_switching_rate()`
/ `market_benchmark()` / `_UK_SWITCHING_RATE_PCT` currently have **zero consumers** across
`company/ saas/ simulation/ site/ background/` — the series drives no live output today, so nothing is
presently wrong on the surfaces. **But it is precisely the landmine an F5 build would step on:** it is the
one *clean, importable* `get_switching_rate(year: int) -> float` accessor, docstringed as authoritative
Ofgem market intelligence, sitting in the company market module — exactly what a graduation build would
reach for as §5's calibration target, in preference to a series buried in a markdown research doc. A build
that calibrated the emergent competitor field so its elasticity output reproduced `get_switching_rate()`
would be calibrating to figures live Energy UK data disconfirms ~3× in the two most important regime years
(the 2020 engagement peak and the 2021 pre-collapse), silently baking a wrong best-alternative reactivity
into the field for the era that most distinguishes Era A from the crisis.

**Disposition (build-sequencing, sharpens §5/§6 — no atom opened, no map level change, honours the wall).**
Switching rates are public observables (the company MAY read them — the wall is intact; validation was
against Energy UK / GOV.UK, never the SIM scalar). The graduation build must (a) treat
`churn_price_elasticity.md` §1 as the **authoritative** switching-series calibration target (it is sourced
*and* live-corroborated), (b) **reconcile or retire** `market_report.py::_UK_SWITCHING_RATE_PCT` in the
same change so a single "observed switching series" exists in code — mirroring §6's two-scalars-one-regime
hazard (`MARKET_SAVINGS_BY_YEAR` must retire in lockstep): here a **second** double-valued anchor for the
same real-world fact, on the *observable* side rather than the SIM side, both needing single-sourcing
before the field is calibrated. Verified by reading both repo files this tick and adjudicating against a
live independent Energy UK / GOV.UK source; the SIM scalar was not used as a check.

**Source (this tick):** Energy UK electricity switching reports (`energy-uk.org.uk/news/switching-remains-down-at-year-end/`
— 2021 total 5.1m, "14% lower than 2020" ⟹ 2020 ≈ 5.9m); GOV.UK *Quarterly Domestic Energy Switching
Statistics* (`gov.uk/government/statistical-data-sets/quarterly-domestic-energy-switching-statistics`).
Observable-side public data; none is SIM ground truth.
