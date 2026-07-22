# F4 — International Expansion Probe (DISCOVER)

**Track:** F4, Forward-Discovery Register (aspirational × medium — tests the "global by design" claim).
**Status:** DISCOVER-only. No build, no new map atoms. Names candidate atoms as *proposals* only.
**Date:** 2026-07-22. **Author:** autonomous worker (forward-discovery tick).

**Provenance & honesty (R9).** Written without live network access (autonomous run). The **absorb/break
verdicts in §4 are anchored to the actual repository code** (file:line evidence) — an independent source
in the strict sense that the code is what it is regardless of what the pitch claims or what the SIM
"wants", and it is NOT SIM ground truth. The **candidate-market facts** (Ireland's market structure,
tax rates, settlement admin) are **author domain knowledge, recalled — labelled `[recall, validate]`**
and must be validated against the named independent sources (SEMO, CRU, Revenue.ie, EirGrid) before any
figure is used in a build. Structural claims (SEM is a gross pool, CRU not Ofgem, € not £) are
well-established and low-risk; the *magnitudes* (VAT %, PSO levy, ISP length) are the part that needs a
fetch.

---

## 1. The claim under test

This probe produces **evidence for or against the transferability claim — not a market-entry plan**
(the register's own framing). The claim lives in `PURPOSE_PITCH_V4.md`:

- **§11 "Global by design":** *"Market structure, regulator, climate, tariff regime, building stock and
  payment culture are variables the simulator samples, not architecture it must rebuild. What stays
  constant is the core: supply and demand mechanics, hedging and risk, the customer lifecycle, the
  billing and payment waterfall, the decision architecture, the observability layer."*
- **§13 "What is not proven":** *"That the blueprint **transfers** to another market without more work
  than the argument implies."*

So the pitch already concedes the conclusion is unproven. F4's contribution is to **test §11's specific
partition** — the list of what "stays constant" — against the code, and say **which items actually hold
constant and which are GB structure masquerading as a constant.** That converts a one-line hedge (§13)
into a ranked, evidenced verdict.

## 2. The candidate market — Republic of Ireland (I-SEM)

The register asks for **ONE** candidate. I pick the **Republic of Ireland** under the **Single
Electricity Market (SEM / I-SEM)**, for three reasons:

1. **It is the most plausible *real* second market for a GB supplier** — geographic and linguistic
   adjacency, and several GB-heritage retail brands already operate on the island. If "global by design"
   means anything operationally, Ireland is where it gets exercised first.
2. **It is deliberately the *gentlest* realistic pick.** It shares a half-hourly settlement heritage, a
   liberalised retail market, and a similar building/climate profile. The rhetorical value is asymmetric:
   *if even the closest neighbour breaks core assumptions, the "just a variable" reading of §11 is
   optimistic.* A harder market only breaks more.
3. **A sharper-granularity counterfactual is noted, not chosen:** **ERCOT (Texas)** settles on 15-minute
   intervals with nodal pricing and no retail price cap; **AEMO NEM (Australia)** moved to **5-minute**
   settlement in 2021. Either would break the hardcoded `48`-period assumption (§4.5) far harder than
   Ireland does. Ireland's mildness on *that* axis is exactly why it **hides** the settlement-granularity
   break — see §4.5.

## 3. What varies — concrete enumeration

`[recall, validate]` on all right-hand values. Change-class in the final column: **DATA** (a value the
architecture should absorb), **STRUCTURE** (a shape the code hardcodes), **BRAIN** (changes what a core
algorithm *means*).

| Dimension | GB (built) | Republic of Ireland | Change class |
|---|---|---|---|
| Wholesale market structure | Decentralised bilateral trading + Elexon imbalance settlement | **SEM/I-SEM gross mandatory pool** (ex-ante DAM/IDM + single imbalance price; EU Target Model) | **BRAIN** — changes what "buy forward + hedge" resolves to |
| Settlement granularity | 48 half-hourly periods | HH heritage; EU Imbalance Settlement Period moving toward **15-min** | STRUCTURE (mild for IE, hard for ERCOT/NEM) |
| Settlement reconciliation cadence | Elexon BSC R1/R2/R3/RF (to ~28 months) | SEMO reconciliation timetable (different runs/lags) | STRUCTURE |
| Regulator | Ofgem | **CRU** (Commission for Regulation of Utilities) | DATA (regime key) |
| Retail price regulation | Ofgem default-tariff **price cap** | **No domestic price cap** | STRUCTURE — the *class* of invariant has no analogue |
| Currency | £ / GBP | **€ / EUR** | STRUCTURE (deepest) |
| Consumption tax | 5% VAT (domestic) / 20% (I&C); GB policy costs | **VAT ~13.5% (temp 9%)** + **PSO levy** + carbon tax on gas | STRUCTURE + DATA |
| Metering identifier | MPAN / MPRN(gas); DCC; Elexon | **MPRN** (elec) via **ESB Networks**; **SEMO** market ops | STRUCTURE (seam vocabulary) |
| Smart-meter maturity | DCC rollout advanced | ESB Networks **NSMP** — different penetration/timeline | DATA (anchor value) |
| Consumer protection | Ofgem SLCs (SLC14 etc.) | **EU + CRU** supplier obligations | DATA (regime key) |
| Building stock / EPC | EPC; gas-dominant heating | **BER** (Building Energy Rating); more oil / solid-fuel heat | DATA (anchor provenance) |
| Payment culture | High DD penetration | Different DD / bill-pay mix | DATA (anchor value) |

## 4. Absorb vs break — mapped to the code

For each of §11's "what stays constant" items, does the code **actually** hold it constant when the
jurisdiction changes? Verdicts anchored to the repo.

**4.1 Regulatory obligations — ABSORBS.** `company/compliance/obligations_register.py` is keyed by
`regime` (required field, `:241`), with an extensible `KNOWN_REGIMES` frozenset (`:153-161`: Ofgem,
HMRC, HSE, ICO, BSC/MRA, DESNZ, Energy Ombudsman) and `effective_from`/`effective_to` (`:248-249`).
Harm-tiering is universal (`derive_risk_tier`). **CRU and Irish/EU consumer-protection obligations fit
behind this seam as new rows — no schema change.** This is the design working as PORTABILITY constraint
7 intended.

**4.2 Invariant class/anchor separation — PARTIAL.** `company/compliance/domain_invariants.py`
structurally separates invariant **classes** (`RateInvariant`, `RangeInvariant`, `YearlyRangeInvariant`,
`StructuralInvariant`) from values, and every class carries `jurisdiction: str = _UK` +
effective-dates (`:85-134`), with an explicit note (`:51-62`) that a non-UK addition "must set this
explicitly." **But** every concrete value defaults to `_UK` and lives in one flat `ALL_INVARIANTS` list
in the same module — there is **no data-loader seam**, so a second market's values are added as more
GB-defaulted globals, not dropped in as a separate file. Constraint 2's test ("loading a second market's
values must require no schema or code change") is *schema-satisfiable but not realised*. **Sharper: one
invariant *class* structurally assumes a GB institution** — the price-cap-derived `_ELEC_CAP_BY_YEAR`
anchor (`:42-48`) and the cap invariant itself. Ireland has **no domestic price cap**, so this is not a
"different value" — the invariant has **no analogue** and must be made regime-optional, not
re-anchored. That is the difference between DATA and STRUCTURE.

**4.3 Decision architecture / internal seams — ABSORBS.** `company/interfaces/internal_seams.py` types
crossings by **function** (`Domain` enum PRICING/BILLING/SETTLEMENT/COLLECTIONS; messages
`PriceCardIssued`, `SettlementPosition`, `OverdueInvoiceReferred`) with an explicit "no counterparty
hardcoded" note. The **decision architecture and observability layer** — §11's strongest constant — are
genuinely market-agnostic.

**4.4 SIM/company seam vocabulary — PARTIAL/BREAK.** `company/interfaces/sim_interface.py` is typed by
function at the *method* level (`get_settlement_data`, `get_forward_price`, `notify_churn`) — good — but
its **payload vocabulary is GB-baked**: `get_settlement_data(mpan, period)` hardcodes the GB meter id
`mpan` and a `'YYYY-MM-DD:SP'` settlement-period format (`:36-37`); `LiveSimInterface` wires **Elexon /
NBP TTF** as *the* price source (`:255-291`) and branches on `fuel ∈ {electricity, gas}` only. The
`tools/market_adapters/` port (`MARKET_ADAPTER_SOURCE` env-swappable behind `MarketDataPort`) is the
**target pattern** — the SIM seam has not yet been refactored to it.

**4.5 Settlement granularity (`48`) — BREAK.** `PERIODS_PER_DAY = 48` is a **hardcoded constant
duplicated independently** across `simulation/hh_consumption.py:14`, `simulation/demand_model.py:38`,
`sim/weather_engine.py:36`, plus `SETTLEMENT_PERIODS_PER_YEAR = 17_520` (`saas/cost_to_serve.py:37`),
literal `range(1, 49)` in run scripts, and `_EXPECTED_PERIODS_PER_DAY = 48`
(`company/market/hh_data_quality.py:20`) — ~10 modules, no single `market.settlement_granularity`.
Ireland's HH heritage makes this **mild** — which is precisely the trap: the gentlest pick lets the break
hide. ERCOT (15-min) or NEM (5-min) would force the rework §11 says isn't there. Directly violates
PORTABILITY constraint 3.

**4.6 Reconciliation window — BREAK (contained).** Elexon `_R1/_R2/_R3/_RF_MONTHS` + shares + variance
bands are hardcoded and **duplicated verbatim** in `company/regulatory/settlement_reconciliation.py:28-38`
and `simulation/settlement_timetable.py:65-79`. Cleanly isolated (good) but not resolved from a regime
config; SEMO's cadence would mean editing both copies.

**4.7 Tax / VAT — BREAK.** VAT is **hardcoded numeric literals keyed by customer segment, never by
jurisdiction**: `VAT_RATE = 0.05` (`company/billing/invoice.py:19`), `VAT_RATE_BY_MARKET =
{"resi":0.05,"SME":0.05,"I&C":0.20}` (`dual_fuel_bill.py:25`), `VAT_RESIDENTIAL=0.05` /`VAT_SME=0.20`
(`domain_invariants.py:151-158`). Irish VAT (~13.5%, temp 9%) + PSO levy + carbon tax have **no
representation path** — and PORTABILITY constraint 4's own concrete case (energy VAT vs insurance IPT on
one bill) is already unrepresentable. Violates constraint 4.

**4.8 Currency — BREAK (deepest).** **No `Money`/`Currency` type exists anywhere** (grep: zero hits).
GBP is baked into **field naming** — ~6,100 `_gbp`/`gbp_per` field names across `company/`, `saas/`,
`simulation/` (`vat_gbp`, `total_amount_gbp`, `unit_rate_gbp_per_mwh`), plus `£` in report rendering and
`pence` assumptions. A euro-denominated market touches thousands of field names and every serialised
schema. **This is the deepest structural blocker — deeper than settlement granularity** — and it maps
onto §11's "billing and payment waterfall" constant, which therefore does **not** hold.

## 5. Verdict on the transferability claim

§11's "what stays constant" list **splits cleanly in two**, and the code says which half is real:

- **Genuinely constant (portable — the design working):** *decision architecture*, *observability
  layer*, *customer lifecycle* logic, and the *regulatory-obligations governance layer* (§4.1, §4.3).
  For a market like Ireland these are a **data-and-adapter exercise**, exactly as §11 claims — new
  `regime` rows, new anchor values, a CRU obligation set.
- **Not constant (GB structure mislabelled as a constant):** the **"billing and payment waterfall"**
  fails on all three of currency (§4.8), tax (§4.7) and settlement granularity (§4.5); **"supply and
  demand mechanics / hedging and risk"** is partly BRAIN-level (SEM's gross pool changes what "buy
  forward + hedge" resolves to, §3) and rides on the GB-baked SIM-seam vocabulary (§4.4).

**So §13's admission is correct, and now quantified:** transfer is cheap for the *brain and governance*
layers (as designed) and a **real rework for the transactional core**, with **currency the deepest single
blocker**. This is **evidence *against* the strong reading of §11** ("geography is just a variable we
sample") and **evidence *for* the weak reading** (the *core reasoning* is market-agnostic; the *plumbing*
is GB-shaped). Note the pitch's own hedge — "Britain first because it is one of the hardest markets" — is
about market *difficulty*, not about whether the *code* generalises; the transactional-core breaks are
about **structure, not difficulty**, so a gentler market does not rescue them. The honest headline: **the
architecture is portable where it reasons and GB-bound where it transacts.**

## 6. A meta-finding: the portability debt is logged diffusely

The doctrine (`PORTABILITY_DESIGN_CONSTRAINTS.md`) says to *"log it as a portability debt item"* — but the
debt is scattered as inline notes across design frames (`SYNTHETIC_FUTURES_GENERATION_FRAME.md`,
`adoption_geography.py`, several `frame/*` docs) with **no single rankable register**. The items this
pass surfaces (currency deepest, then settlement granularity, tax, SIM-seam vocabulary, invariant-value
loader, cap-invariant-as-regime-optional) exist as diffuse TODOs. **That diffusion is itself a finding:**
"logged" currently means "mentioned somewhere," which reads as covered when it isn't.

## 7. Epistemic wall

This pass read **only**: the pitch, the code seam, already-fetched repo domain artefacts, and recalled
public facts about Ireland's market. It read **no SIM ground truth** — the absorb/break verdicts are
statements about the *company/interface/plumbing* code, which is the legitimate object of a portability
review. No customer, no market, no household data touched. Ireland-specific market **magnitudes** remain
`[recall, validate]`.

## 8. Candidate graduation — no atom opened

DISCOVER-only; **no atom opened** (BUILD-open is a director/twin call). Candidate proposals, ranked by the
depth of the break they close:

1. **A consolidated `PORTABILITY_DEBT.md` register** (§6) — cheap, aggregates the diffuse notes into one
   rankable list; the natural *first* graduation because it is doc-only and makes the rest decidable.
2. **A `Money`/currency abstraction** (remediation-on-touch per the standing constraint, never a
   speculative sweep) — the deepest blocker (§4.8).
3. **A `market.settlement_granularity` config object** replacing the duplicated `48` constants (§4.5).
4. **Making the price-cap invariant regime-optional** so a no-cap market has no phantom anchor (§4.2).

**Open items — network-gated `[recall, validate]`** (recorded so they are not re-searched fruitlessly):
Irish domestic VAT-rate history + PSO levy + carbon-tax magnitudes (Revenue.ie / CRU); the current
I-SEM/EU Imbalance Settlement Period length and SEMO reconciliation timetable (SEMO/EirGrid); MPRN /
ESB Networks smart-meter penetration; CRU consumer-protection obligations vs Ofgem SLC mapping.

**No further autonomous DISCOVER increment on F4 without network** — the remaining work is either a
doc-only graduation (proposal 1, a director/twin call) or requires a live SEMO/CRU/Revenue fetch. Next
tick should draw a still-open track or await director graduation.

---

## 9. Increment (2026-07-22, network-restored tick) — the three magnitudes CLOSED

Network was probed live this tick (CRU HTTP 200, Revenue 302) — the `no-network-in-autonomous-runs`
assumption did not hold, so §8's network-gated `[recall, validate]` magnitudes were worked against
primary/regulator sources. Single-track discipline held (F4 only). None is SIM ground truth. **Each
result confirms — and in two cases *sharpens* — the §4 absorb/break verdicts; none overturns one.**

**(1) Settlement granularity / ISP length — CONFIRMS §4.5's "mild for IE" *and* sharpens the trap.**
The I-SEM Balancing Market trading day is divided into **48 × 30-minute imbalance settlement periods**,
each containing **six 5-minute imbalance *pricing* periods** (SEMO *Industry Guide to the I-SEM —
Trading*, Ch. 5; SEMO *Balancing Market* overview). So the settlement *period* is 30 min — **identical to
GB's 48 half-hours** — which is exactly why the `48` constant (§4.5) does not break for Ireland. But the
**5-minute imbalance-pricing sub-layer is a genuine structural addition GB has no analogue for**: a build
that took Ireland's *pricing* seriously would need a granularity the hardcoded `48` cannot express even
in the gentle pick. Net: the "gentlest pick hides the settlement break" finding is now **doubly
confirmed** — settlement granularity absorbs (48==48), and the one place Ireland *does* differ (5-min
pricing) is precisely the sub-period the GB `48` constant flattens away. The harder counterfactuals
(ERCOT 15-min, NEM 5-min settlement) remain the real break.

**(2) VAT — CONFIRMS §4.7's BREAK and makes the magnitude precise (and *larger* than GB).** Irish
domestic electricity VAT is **9%** — a temporary reduction from the **13.5%** reduced rate, first cut in
May 2022 and, per the **7 Oct 2025 Budget, now extended to 31 December 2030** (gov.ie Dept. of Finance;
Irish Times 2025-04-01). So the operative rate is **9% today, reverting to a 13.5% baseline**. Either way
it is **~2× GB's 5% domestic rate** — the hardcoded `VAT_RATE = 0.05` (§4.7) is not merely
jurisdiction-blind, it is off by a factor of ~2 for the *nearest* market. The recall (`~13.5%, temp 9%`)
was correct; the material refinement is that the "temporary" 9% is now a five-year fixture, so a build
would key on 9%, not 13.5%.

**(3) PSO levy — CONFIRMS §4.7's "no representation path" and identifies a whole missing *line item*.**
Ireland's **Public Service Obligation levy** (funds renewable/security-of-supply schemes) is a
**mandatory per-customer charge with no GB bill-line analogue**. CRU's 2025/26 final decision (CRU/2025)
sets the domestic charge at **€1.46/month ex-VAT (€17.52/yr; ~€19.10 incl. 9% VAT)** from 1 Dec 2025,
down from €3.23/month; the total levy is **€125.38m** (revised 20 Oct 2025 down from €162.37m, itself a
55% cut on 2024/25's €251.79m). Crucially it has been **zero or *negative* (a rebate to customers)** in
recent years. Two design consequences: **(a)** the levy's *existence* is **STRUCTURE** — GB's bill model
has no fixed regulatory standing-charge line of this kind keyed to the *regime*; **(b)** its *value* is a
**DATA anchor that flips sign** (rebate ↔ charge) by annual CRU decision, so any representation must allow
a **negative** per-customer regulatory charge, not just a positive one. This is a second concrete case
(alongside VAT-vs-IPT in §4.7) that PORTABILITY constraint 4's "monetary treatment" seam cannot currently
carry.

**Still `[recall, validate]` (lower-priority refinements, not blocking the verdict):** Irish **carbon
tax** on gas magnitude; **SEMO settlement reconciliation timetable** run/lag structure (the analogue to
Elexon R1/R2/R3/RF in §4.6); **ESB Networks MPRN smart-meter penetration**; and the **CRU
consumer-protection obligation ↔ Ofgem SLC** mapping (§4.1). These refine anchor values inside verdicts
that are already settled; none changes an absorb/break call.

**Verdict unchanged, now magnitude-anchored.** All three closed magnitudes *strengthen* §5's headline —
**portable where it reasons, GB-bound where it transacts** — by pricing the transactional-core breaks:
VAT is ~2× off, the PSO levy is a missing sign-flipping line item, and even the "mild" settlement axis
hides a 5-min pricing granularity. **F4 is now DISCOVER-complete to the depth this lane warrants** — the
only remaining moves are the doc-only `PORTABILITY_DEBT.md` graduation (§8 proposal 1, a director/twin
call) or the lower-priority recall refinements above. **No atom opened, no map level change** (BUILD-open
is director-reserved). Next tick should draw a still-open track (F5 per-supplier % shares) or await
director graduation.
