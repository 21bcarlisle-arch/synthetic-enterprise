# The GB wholesale-energy domain — topic map (nodes, typed edges, per-node scope)

**Deliverable #1** of `DIRECTOR_RULING_KPILOT_DECOMPOSITION_2026-07-28.md` (§3, §4, §5.1).
**Serves:** DIRECTOR_AXES Axis 1 (Website) + Axis 3 (Believability). Campaign: SITE_MODEL_SPINE knowledge lane.
**Lane:** FRAME / DISCOVER — doc-only. This artefact DECIDES the graph; it does not rewrite pages. The
page-level re-home and stub creation are deliverables #4 (`stubs_and_content_rehome`) and the one deep
node is #3 (`one_node_to_depth_with_charts`), which consume this map.
**Status:** proposal (proceed-by-default per ruling tag). The live graph in `site/data/knowledge_wholesale.json`
is UNCHANGED by this artefact — the machine-readable block in §5 is the target #4 reconciles the live graph to.
**Wall:** public-reality commons only; no simulation-internal value appears here. Reversible via git.

---

## 0. The class rule this map obeys (ruling §1)

A node's **scope paragraph** below states *what a complete treatment of that node contains* — it is not a
list of what we have not yet written. Named gaps for any node live in that node's residuals rung when the
node is built, never in its body. Where a node is not yet understood well enough to explain, it ships as an
honest **stub** (identity + place in the graph + "not yet written"), never as a gap list in costume.

---

## 1. The joint test (ruling §3) — the sole rule that decides nodes

> **Do these things share products, mechanisms AND drivers?** Shared → one topic. Different → separate
> topics joined by a typed edge.

Every node and every merge below is argued against this test. The test is applied *across the whole domain*,
not only to the gas/electricity pair the director named — because the director's ruling explicitly invites
it: *"Apply it across the domain; if you judge the joint sits elsewhere for some pair, argue it with the test."*

---

## 2. The domain's real joints — the split the ruling requires

The pilot topic was a single page, **"wholesale price formation,"** that carried gas as a mere `drives`
stub of the electricity price. That is the merger §3 forbids. Applying the joint test to the gas/electricity
pair:

| | **Gas wholesale** | **Electricity wholesale** |
|---|---|---|
| **Products** | NBP spot, TTF, within-day → month → season → annual contracts, storage capacity products, LNG cargoes | Baseload & peak blocks, day-ahead auction (N2EX / EPEX), EFA-period blocks, within-day, seasons |
| **Mechanisms** | Storage injection/withdrawal cycles, LNG cargo arbitrage, pipeline & terminal (Norwegian, IUK/BBL) flows, supply–demand balancing at NBP | Merit-order stacking — the *marginal plant* sets the price; residual demand after wind/solar picks the marginal unit |
| **Drivers** | Global LNG competition (Asia vs Europe), European storage fill levels, weather-driven heat demand, Norwegian supply availability | Gas price (the coupling edge below), carbon price, wind & solar output, demand, interconnector flows |

**All three of products, mechanisms and drivers differ.** By the test they are **two topics**, not one.
They are **coupled, not merged**: for most GB hours a gas plant is marginal, so the gas price drives the
electricity price. That coupling is exactly one typed edge — `gas-wholesale --drives--> electricity-wholesale`
— never a shared body.

This single split is the reason the data structure matters (ruling §4): once gas and electricity are
separate objects with separate scopes, a conflated page becomes structurally impossible to write.

---

## 3. The nodes (with per-node scope paragraph + joint-test argument + re-home)

### 3.1 `gas-wholesale` — **GB gas wholesale** *(top-level topic; NEW — promoted from the `gas-price` stub)*
**Scope (what a complete treatment contains):** the GB gas market as a market in its own right — how the
National Balancing Point price is set by the balance of supply (Norwegian pipeline imports, LNG send-out,
UKCS production, storage withdrawal, interconnector flows) against demand (heat, power-station burn,
industry); the contract curve from within-day to annual; the role of seasonal storage arbitrage and LNG
cargo optionality; and why GB, as a price-taker on a globally-traded fuel, tracks TTF and Asian LNG rather
than any domestic cost stack.
**Joint-test argument:** distinct from electricity on all three axes (table §2) → its own topic.
**Re-home:** the existing `gas-price` stub (blurb *"the fuel cost that sets the marginal plant's bid"*)
collapses INTO this node — "the gas price" is one *output* of gas wholesale, not a driver-stub hanging off
electricity. The `gas-price --drives--> wholesale-price-formation` edge is replaced by
`gas-wholesale --drives--> electricity-wholesale`.

### 3.2 `electricity-wholesale` — **GB electricity wholesale** *(top-level topic; the RE-HOME of the current page)*
**Scope:** how the half-hourly GB wholesale electricity price is set at the margin — residual demand after
renewables selects the marginal plant on the merit-order stack, and that plant's short-run marginal cost
(fuel + carbon + variable O&M) sets the price for the whole market; the traded products (baseload/peak
blocks, day-ahead auction, EFA periods) through which that price is discovered ahead of delivery; and the
characteristic behaviour of the price (gas-led level, diurnal and seasonal shape, negative-price frequency
as renewables grow).
**Joint-test argument:** distinct from gas wholesale (table §2); the current `wholesale-price-formation`
page IS this topic's core explanation. **This is the recommended candidate for the one deep node (#3)** —
the price-formation charts and SRMC reconstruction (W1_6, DONE) already sit on this node, and the director's
steer that "product structure and shape is possibly the most important thing" lands squarely here.
**Re-home:** the current `wholesale-price-formation` page body moves here; the URL becomes this node (or
redirects). Its merit-order / EFA / negative-price content stays; its gas content moves to §3.1.

### 3.3 `carbon-price` — **The UK carbon price (UK ETS + CPS)** *(top-level topic; kept separate)*
**Scope:** the price of emitting a tonne of CO₂ in GB power — the traded UK ETS allowance (UKA) price set by
a capped auction market, plus the fixed Carbon Price Support top-up; how the cap trajectory, industrial
demand and policy set the allowance price; and how that per-tonne cost enters every fossil plant's marginal
bid and therefore the electricity price.
**Joint-test argument:** vs electricity — different product (UKA allowances), different mechanism
(cap-and-trade auction, not merit order), different drivers (cap policy, industrial demand) → **separate
topic**, coupled by `carbon-price --drives--> electricity-wholesale`. (This is a second, independent worked
example of the §3 test, exactly as the ruling invites.)
**Re-home:** existing `carbon-price` stub stays as this node; edge unchanged.

### 3.4 `gb-electricity-market` — **The GB electricity market (structure & settlement)** *(context / parent)*
**Scope:** the market these prices live in — half-hourly settlement periods, the roles (generators,
suppliers, the ESO, Elexon), the trading timeline from forward to gate-closure to imbalance, and how BSC
settlement reconciles metered volumes against contracted positions.
**Joint-test argument:** shares the settlement *mechanism* with electricity-wholesale but is a distinct
topic (market *structure & rules* vs *price at the margin*) → kept as a parent context node,
`electricity-wholesale --part-of--> gb-electricity-market`.
**Re-home:** existing `gb-electricity-market` stub stays.

### 3.5 `merit-order-residual-demand` — **Merit order & residual demand** *(mechanism of electricity-wholesale)*
**Scope:** the cheapest-first dispatch queue; residual demand = demand − (wind + solar + must-run); how the
intersection of residual demand with the stack picks the marginal unit whose SRMC becomes the price; and how
a growing renewable fleet shifts the stack (more hours on cheap/zero-marginal-cost plant, more negative-price
hours, sharper peaks when the wind drops).
**Joint-test argument:** shares products, drivers and the price-setting mechanism with electricity-wholesale
— it IS electricity-wholesale's central mechanism → a `mechanism-of` sub-node, not a separate topic.
**Re-home:** existing stub stays; edge `mechanism-of --> electricity-wholesale`.

### 3.6 `imbalance-cashout-settlement` — **Imbalance & cash-out** *(mechanism of electricity-wholesale)*
**Scope:** how being short or long against your contracted position is priced — the single imbalance price,
the balancing actions that set it, and the cash-out ceiling (£6,000/MWh) that caps a shortfall; why this is
the price that ultimately disciplines a supplier's hedging.
**Joint-test argument:** an electricity settlement mechanism → `mechanism-of --> electricity-wholesale`
(also `part-of` the market node); not a separate topic.
**Re-home:** existing stub stays.

### 3.7 `hedging-forward-market` — **Hedging & the forward market** *(cross-cutting; downstream of both fuels)*
**Scope:** how a supplier buys ahead — the forward curve, the blocks and shapes it trades, and how a hedge
programme blunts the delivered price a supplier would otherwise face at spot; applies to BOTH electricity
and gas procurement.
**Joint-test argument:** the forward market is a *product layer over both* gas and electricity, so it is
not merged into either — it is a downstream cross-cutting node with a `prerequisite-for` edge from each
fuel's spot topic (`electricity-wholesale --prerequisite-for--> hedging-forward-market`, and the same from
`gas-wholesale`). Kept as its own node precisely so the "supplier procurement" story does not get buried in
either spot topic.
**Re-home:** existing stub stays; a second inbound edge from `gas-wholesale` is added.

### 3.8 `price-cap` — **The retail price cap** *(retail boundary; downstream of the domain)*
**Scope:** how the wholesale price reaches a household — Ofgem's cap methodology, its wholesale-cost
allowance and the lag with which wholesale moves pass through to the capped tariff.
**Joint-test argument / placement note:** this node is **retail, not wholesale** — it sits at the domain
boundary. It is kept in the map as an explicit *downstream boundary* node (`electricity-wholesale
--feeds/bounded-by--> price-cap`) so the wholesale→retail seam is visible and honest, but it is flagged as
outside the wholesale domain proper and should NOT be treated as a peer wholesale topic.
**Re-home:** existing stub stays, re-typed as a boundary node.

---

## 4. Reconciliation against the LIVE graph — nothing orphaned

Every one of the 8 current entries in `site/data/knowledge_wholesale.json` has a stated destination
(exhaustive — no orphan, no dead backlink):

| Current entry | Kind now | Becomes |
|---|---|---|
| `wholesale-price-formation` | page | `electricity-wholesale` (re-home; candidate deep node #3) |
| `gas-price` | stub | **collapses into new `gas-wholesale` top-level node** |
| `carbon-price` | stub | `carbon-price` (kept, separate top-level) |
| `gb-electricity-market` | stub | `gb-electricity-market` (kept, parent context) |
| `merit-order-residual-demand` | stub | kept, `mechanism-of electricity-wholesale` |
| `imbalance-cashout-settlement` | stub | kept, `mechanism-of electricity-wholesale` |
| `hedging-forward-market` | stub | kept, + new inbound edge from `gas-wholesale` |
| `price-cap` | stub | kept, re-typed as retail **boundary** node |

The single structural change is the **promotion of `gas-price` → `gas-wholesale` as a top-level topic** and
the retyping of its edge to `gas-wholesale --drives--> electricity-wholesale`. Everything else is a
kind/edge clarification, not a new page.

---

## 5. Machine-readable target graph (for deliverable #4 to reconcile the live JSON to)

> This block is the DECIDED graph. #4 reconciles `site/data/knowledge_wholesale.json` to it and creates the
> stub pages; #3 fills `electricity-wholesale` to depth. This artefact does not itself edit the live file.

```json
{
  "domain": "gb-wholesale-energy",
  "topics": [
    {"id": "electricity-wholesale", "title": "GB electricity wholesale", "kind": "page", "level": "top", "note": "re-home of wholesale-price-formation; candidate deep node (#3)"},
    {"id": "gas-wholesale", "title": "GB gas wholesale", "kind": "stub", "level": "top", "note": "promoted from gas-price stub"},
    {"id": "carbon-price", "title": "The UK carbon price (UK ETS + CPS)", "kind": "stub", "level": "top"},
    {"id": "gb-electricity-market", "title": "The GB electricity market (structure & settlement)", "kind": "stub", "level": "context"},
    {"id": "merit-order-residual-demand", "title": "Merit order & residual demand", "kind": "stub", "level": "mechanism"},
    {"id": "imbalance-cashout-settlement", "title": "Imbalance & cash-out", "kind": "stub", "level": "mechanism"},
    {"id": "hedging-forward-market", "title": "Hedging & the forward market", "kind": "stub", "level": "cross-cutting"},
    {"id": "price-cap", "title": "The retail price cap", "kind": "stub", "level": "boundary", "note": "retail, not wholesale — boundary node"}
  ],
  "edges": [
    {"from": "gas-wholesale", "type": "drives", "to": "electricity-wholesale"},
    {"from": "carbon-price", "type": "drives", "to": "electricity-wholesale"},
    {"from": "merit-order-residual-demand", "type": "mechanism-of", "to": "electricity-wholesale"},
    {"from": "imbalance-cashout-settlement", "type": "mechanism-of", "to": "electricity-wholesale"},
    {"from": "electricity-wholesale", "type": "part-of", "to": "gb-electricity-market"},
    {"from": "electricity-wholesale", "type": "prerequisite-for", "to": "hedging-forward-market"},
    {"from": "gas-wholesale", "type": "prerequisite-for", "to": "hedging-forward-market"},
    {"from": "electricity-wholesale", "type": "bounded-by", "to": "price-cap"}
  ]
}
```

---

## 6. What this map does NOT do (handoff to the other deliverables)

- **Independent-domain evidence (#2, `scope_independence_evidence`):** the scope paragraphs above are
  derived from market structure, but the ruling §2 bar — *material neither the director nor the repo
  supplied*, with a per-item provenance ledger — is #2's job. #2 sharpens each scope paragraph here with
  cited practitioner/market-structure material (e.g. LNG cargo arbitrage mechanics, EFA-period
  microstructure) and tags provenance. This map is the frame it fills.
- **The one deep node (#3):** recommended = `electricity-wholesale` (argued in §3.2). #3 owns that node's
  body + charts.
- **Stubs + re-home (#4):** creates the stub pages for every node that is not the deep node and re-homes the
  current page content per the §4 table; reconciles the live JSON to §5.

**Acceptance check (ruling):** no node's scope paragraph above is a gap list — each states what the node
*covers*. Gas and electricity are separate top-level topics joined by one `drives` edge. The joint test is
stated and applied to the gas/electricity pair AND independently to carbon-price. ✔
