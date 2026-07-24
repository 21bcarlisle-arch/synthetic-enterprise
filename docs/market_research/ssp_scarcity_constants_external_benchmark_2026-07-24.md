# SSP Residual-Demand Scarcity Constants (A0/A1/A2) — External Benchmark Search

**Task:** ground the price engine's fitted scarcity-multiplier constants (`sim/price_engine.py`
`A0=0.326998, A1=1.334629, A2=3.828327, X_TIGHT=0.70, SCARCITY_EXPONENT=2.0`) against a
published UK marginal-cost / scarcity-pricing benchmark. This is the named S3 gap in
`docs/fidelity/EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md` §3 item 4, and the `independent_anchor`
field of ledger row `W1_6_physics_price_signal::ssp_residual_demand_scarcity_calibration_2026_07_19`.

**Epistemic scope:** discovery-only (docs/market_research/ + external published sources).
No simulation code read or touched. No recalibration recommended (R12 — this is gather-only;
any acting on this finding is a separate mint). R13 — decided blind to company P&L; nothing
here was chosen or filtered based on how it would make the model look.

**Network status:** available this tick (`ofgem.gov.uk`, `neso.energy`, `gov.uk` all returned
HTTP 200 on probe). **However, general web search was NOT usable** — Google/Bing returned
either bot-block pages or, more subtly, results for a mangled/ignored query (a Bing query for
`GB "value of lost load" capacity market reliability standard` returned only generic hits for
the substring "GB" = gigabyte, and a second attempt returned only generic dictionary-definition
hits for "value" — i.e. multi-term/quoted queries were not honoured by the reachable route).
DuckDuckGo and Mojeek returned explicit bot-challenge pages (CAPTCHA / 403). This is recorded
per R9 as `observed-with-evidence`, not assumed. What DID work reliably: **direct gov.uk URLs**,
**gov.uk's own `/api/search.json` full-text endpoint** (exact-phrase queries return genuine,
precise hits; multi-term unquoted queries are fuzzy-ranked across gov.uk's full corpus and are
not useful for narrow technical searches), and **Wikipedia's `list=search` API**. Elexon's own
site (`elexon.co.uk`) blocks direct `curl` with a 403 at the edge/WAF layer regardless of path —
not reached this session; a future pass should try Elexon's Insights API (already whitelisted
elsewhere in this project) rather than the marketing/knowledgebase site.

---

## Finding 1 — GB cash-out/scarcity price ceiling: £6,000/MWh (H confidence)

**domain**: electricity_pricing
**assumption_tested**: whether the price engine's fitted convex tight-margin term (`A2=3.828`,
kicking in above `X_TIGHT=0.70`) produces price *magnitudes* of a scale consistent with the
real UK regulatory ceiling on scarcity-driven Balancing Mechanism/cash-out prices.
**benchmark_value**: **£6,000/MWh** — the explicit cap DECC's Dynamic Dispatch Model (DDM) used
for modelled scarcity price spikes under Electricity Balancing Significant Code Review (cash-out)
reform, cited in the government's own Capacity Market parameter-setting note: *"The DDM takes
into account the impact of Cash-out reform and allows market prices to spike up to £6,000/MWh."*
**confidence**: H — primary UK government source, directly fetched and quoted verbatim.
**source**: DECC, *"Background on setting Capacity Market parameters"* (2015-10-15), PDF fetched
from `https://assets.publishing.service.gov.uk/media/5a74aec6ed915d0e8e39a2dc/Capacity_Market_-_parameters_0810.pdf`
(via `https://www.gov.uk/government/publications/setting-capacity-market-parameters`), retrieved
2026-07-24.
**date**: 2026-07-24 (source dated 2015-10-15; the £6,000/MWh cash-out ceiling design has not
been reversed by any later document found this session — not independently re-confirmed against
a post-2018 Reserve Scarcity Pricing methodology statement, see Gap note below).
**finding**: The recalibrated engine's own reported max output is **£574.22/MWh** (full window,
`docs/fidelity/EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md` §2.3), against a real observed SSP max
of **£4,037.80/MWh** in the same window, and now against a real *regulatory design ceiling* of
£6,000/MWh. All three numbers sit on the same axis: the model's tail is roughly an order of
magnitude below both the empirical extreme and the regulatory scarcity-price ceiling. This is a
genuine external anchor for the already-honest tail-underproduction gap named in §2.3 (0.013%
of periods negative vs 2.241% real; max £574 vs real £4,038) — it does not newly discover the
gap, it grounds it with a real published number. **No action recommended** (R12) — this
confirms the gap is real and of plausible real-world scale, it does not tell us how to fix A2.

---

## Finding 2 — GB Reliability Standard: LOLE ≤ 3 hours/year (H confidence)

**domain**: electricity_pricing
**assumption_tested**: whether treating `X_TIGHT=0.70` (engaging the convex kicker on roughly
the tightest 30–40% of settlement periods, per the fidelity doc's own grid-search note) as a
"scarcity" term is consistent with how rare genuine supply scarcity is under the real GB
reliability framework.
**benchmark_value**: the statutory GB Reliability Standard is a **Loss of Load Expectation (LOLE)
of 3 hours per year**; the actual assessed LOLE for winter 2025/26 is **<0.1 hours/year**, with
a de-rated capacity margin of **6.1GW (10.0% of ACS peak demand)**.
**confidence**: H — primary joint DESNZ/Ofgem statutory report, directly fetched and quoted.
**source**: DESNZ & Ofgem, *"Statutory security of supply report: 2025"* (ISBN 978-1-5286-6122-5,
HC 1464), PDF fetched from
`https://assets.publishing.service.gov.uk/media/693bddf4c72b0f8ccf33d68d/statutory-security-of-supply-report-2025.pdf`,
retrieved 2026-07-24.
**date**: 2026-07-24 (report covers winter 2025/26 assessment, viewed by DESNZ 2025-10-09 per
its own footnote).
**finding**: 3 hours/year out of 8,760 is ≈0.034% of periods — genuine loss-of-load risk is
designed to be a rare-event tail, not a routine 30–40%-of-periods occurrence. This is a
**naming/interpretation flag, not a numerical defect**: the code's convex kicker (labelled
"scarcity" in `sim/price_engine.py`'s comments) is, on its own documented behaviour, better
understood as a *general tight-margin/merit-order markup* term (real SSP genuinely does rise
when residual demand is high relative to dispatchable capacity, well short of actual loss-of-load)
rather than a literal LOLE-scarcity-event mechanism — the fidelity doc itself is honest about this
distinction (§2.2, "matching the physical intent... blows up convexly only when RD is unusually
tight" — not "only during loss-of-load events"). No change recommended; flagged for future
documentation clarity only.

---

## Finding 3 — CM demand-curve reference-technology figures (context only, NOT a direct A0/A1/A2 anchor) (H confidence, low relevance)

**domain**: electricity_pricing
**assumption_tested**: whether CCGT is the right reference marginal technology for the price
engine's gas-floor SRMC term (context for interpreting the multiplier's baseline, not the
multiplier constants themselves).
**benchmark_value**: 2015 Capacity Market demand-curve parameters — Net-CONE (Cost of New
Entry) = **£49/kW/year**, based on the lowest CM bid of a new **Combined Cycle Gas Turbine
(CCGT)** in DECC's Dynamic Dispatch Model; auction price cap = 1.5× Net-CONE = **£75/kW**;
price-taker threshold = 50% of Net-CONE = **£25/kW**.
**confidence**: H (same primary source as Finding 1), but flagged **low relevance** — these are
£/kW/year *capacity* payments (a different market, a different unit, a different mechanism)
and are NOT directly comparable to A0/A1/A2 (dimensionless multipliers on a £/MWh energy floor
price). Included only because it independently corroborates CCGT as the real-world reference
marginal plant for GB electricity price-setting, which supports (does not test) the price
engine's structural choice of a gas-fired SRMC floor as `P_gas_floor`.
**source**: same DECC 2015 document as Finding 1.
**date**: 2026-07-24.
**finding**: no action — background corroboration only, explicitly not offered as a numeric
benchmark for A0/A1/A2.

---

## Finding 4 — No published source found using the SAME functional form (honest gap record)

**domain**: electricity_pricing
**assumption_tested**: does any published UK source fit or report the specific dimensionless
multiplier form `A0 + A1·x + A2·max(0, x−X_TIGHT)^p` (x = residual demand / 35,000MW asserted
dispatchable capacity) against real SSP, such that A0/A1/A2 as literal numbers could be checked
against a third party's own fitted coefficients?
**benchmark_value**: none found.
**confidence**: L (absence-of-evidence, not evidence-of-absence — bounded by the search
degradation described above; a properly working search tool could plausibly surface an Ofgem/
NESO Reserve Scarcity Pricing (RSP) methodology statement, an academic GB merit-order paper
(e.g. Newbery-style missing-money analyses), or an Elexon BSC Loss Adjustment/Imbalance Pricing
guidance note with a comparable functional form — none of these were reached this session).
**source**: n/a (negative finding).
**date**: 2026-07-24.
**finding**: **this named gap (S3) is NOT closed by this pass.** What this pass adds is two real,
directly relevant *bounding* anchors (Findings 1 and 2 above) that the fitted constants' *output
magnitudes and engagement frequency* can be sanity-checked against, even though the constants
themselves (A0/A1/A2 as bare numbers) remain unbenchmarked against any third-party fit. Recorded
honestly as a partial anchor, not a false "gap closed."

---

## Search-tooling note for future DISCOVER passes (procedural, not a finding)

This session's search-engine access was materially degraded in a way worth recording so the next
attempt doesn't re-spend the same budget: Google (via `r.jina.ai` proxy) is temporarily
abuse-alleviation-blocked for anonymous access; Bing (via the same proxy) returns syntactically
valid pages but the query terms appear not to reach Bing's ranking (results matched only a
single incidental word from the query, both times tried); DuckDuckGo (`html.duckduckgo.com`) and
Mojeek both return explicit bot-challenge/403 pages. **What worked:** `gov.uk`'s own
`/api/search.json?q=...` (best with an exact quoted phrase — an unquoted multi-term query
fuzzy-matches across gov.uk's entire corpus and returns noise), direct `gov.uk` collection pages
(walking `/government/collections/<slug>` → publication pages → attached PDFs was the single most
productive path this session), and Wikipedia's `list=search` API. Elexon's own site 403s direct
`curl` regardless of path attempted (both bare and via the jina reader proxy) — worth trying
Elexon's Insights/data API endpoints (already used elsewhere in this project, e.g.
`sim/cache/elexon_ssp_full.json`'s provenance) rather than the marketing site for any future
Elexon-sourced methodology document.
