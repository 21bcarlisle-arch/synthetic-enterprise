**Severity:** BLOCKING · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `A48_enterprise_value_is_the_method_not_the_book`

# Discovery: the repository already contains the researched acquisition model, and the live path spends the invented one

Director, 2026-08-28: *"COST_PER_ACQUISITION £150 resi and £400 SME, RESI_OFFER_COST_GBP £50, and
the quote cost derived from the acquisition cost, are all invented numbers with no source behind
them. And the retention one is wrong in kind, not just value."*

All of that is confirmed. **The larger finding is that the correct answer was already written down,
with sources, and reaches no code.**

Knowledge page: `site/data/knowledge_topics.json` →
`acquisition-and-retention-economics`, rendered at `/knowledge/acquisition-and-retention-economics/`.

---

## 1. There are two acquisition-cost models in this repository

| | **The researched one** | **The invented one** |
|---|---|---|
| Lives in | `saas/opex_ledger.py` | `saas/growth_mandate.py` |
| Domestic | £55 dual-fuel, £27.50 single, PCS commission | £150 flat |
| Business | **per-kWh trail**, 0.5–2.0p/kWh, billed over the term | £400 one-off |
| Source | `docs/market_research/B2_CATEGORY6_CAC_ANCHORS.md`, cited to CMA App. 8.3 and broker rate cards | none |
| Called by | **its own tests, and nothing else** | `company/interfaces/growth_desk.py` → the live campaign |

The researched module's own comment states the structural point exactly: *"I&C acquisition via a
broker is a real, ONGOING per-kWh commission — a structurally DIFFERENT cost shape (a trail
commission embedded in the unit rate for the life of the contract, not a one-off spend at signup) —
applied at billing time via `broker_commission_gbp()`, not at acquisition time."*

The research file goes further and makes the recommendation in terms: *"recommend modelling as an
ongoing per-kWh cost line (not a one-off acquisition cost), applied at billing time, rather than
forcing it into the same 'one-off CAC per new customer' shape as the residential channels."*

**That recommendation was written on 2026-07-10, implemented in `opex_ledger`, and never wired.**
`COST_PER_ACQUISITION["SME"] = 400.0` is the shape the research explicitly says not to use, and it
is the one the campaign spends.

## 2. The knowledge map already contradicted the constant

`docs/institutional/knowledge_map.md` line 71, at confidence **H**: *"PCW acquisition channel …
Commission: **£30-60/dual-fuel customer**."* The same map lists "cost per acquisition by channel" as
one of its top three gaps.

So the map simultaneously records a figure that contradicts the live constant and flags the area as
a gap — and neither reached the code. **This is the chain the director's P8 names: knowledge exists,
discovery never runs against it, so a constant gets chosen because a number was needed.**

## 3. The retention model is wrong in kind, and the law says so

`company/analytics/counterfactual_retention.py` carries **both** shapes at once:

- `RESI_OFFER_COST_GBP = 50.0` — a cash cost per offer, and
- `_TIER_CLASS_BY_DISCOUNT` — 3%, 5% and 8% **discounts**.

A discount already reduces revenue. Charging £50 beside it books the same intervention twice, once
correctly as foregone margin and once as a cash line that no supplier ever pays.

**And there is a licence condition on exactly this.** Ofgem's SLC 22B, the Ban on Acquisition-only
Tariffs, has since April 2022 prohibited offering a fixed-term deal to new customers that is not
also available to existing ones. Retention is possible only through a specific carve-out — in
Ofgem's words, *"The BAT's Market-wide Derogation … enables suppliers to offer bespoke,
retention-only deals to their existing customers when they are coming to the end of a fixed-term
deal."*

A retention offer is therefore **a tariff, offered at a defined contractual moment, permitted by a
named derogation**. It is a price. `RESI_OFFER_COST_GBP` models it as a payment, which is not a
smaller version of the right thing — it is a different thing.

**The sim spans the discontinuity and does not model it.** Before April 2022, acquisition-only deals
were lawful and were the most attractive prices in the market; that asymmetry is what drove the
switching volumes the world is calibrated on. From April 2022 they are banned. Our world applies one
set of retention physics across 2016–2025.

## 4. What else is invented in the same neighbourhood

- `ACQUISITION_WIN_RATE = {"resi": 0.20, "SME": 0.12}` — comment reads *"Lower than home-move rates
  … because we're competing blind"*, which is a rationale, not a source.
- `FIXED_COST_MONTHLY = 50.0` with the comment *"calibrate to match overhead ratio"* — an admitted
  placeholder. Ofgem's 2017 efficient operating-cost benchmark was **£78/customer/year electricity
  and £89 gas**; £50/month across a 15-account book is about £40 per account per year.
- `IC_OFFER_COST_GBP = 200.0`, `_RETENTION_EFFECTIVENESS = 0.20`,
  `ASSUMED_EFFECTIVENESS_PER_DISCOUNT_POINT = 0.04` — no sources.

## 5. One near miss, recorded because it is the failure the page exists to prevent

A search summary offered "£90 per customer" as an Ofgem customer-acquisition benchmark. The source
(price cap EBIT consultation, May 2023) says at §4.24 that £90 is **depreciation and amortisation of
fixed assets**; §4.25 shares only the *six-year lifetime* with the CMA's acquisition-cost
amortisation. Publishing £90 as a CAC benchmark would have produced **an invented number with a real
citation attached** — worse than an invented number, because the citation stops anyone checking.

## 6. What the published record will not give us

The actual per-customer acquisition costs the six large suppliers reported to the CMA are **redacted**
in the published appendix — every figure that would settle it appears as an empty bracket. No
GB-energy-specific direct/brand-marketing CAC exists in any public source searched. So the honest
output is a **shape**, not a number, and the Knowledge page says so rather than picking a midpoint.

---

## The roadmap

**Ordered so that nothing is calibrated before it is understood. Not started — this document is the
discovery step, and the ordering is the deliverable.**

**R1 — Retire the invented table, wire the researched one.** Make `growth_desk` read
`opex_ledger.acquisition_cost_gbp()` and delete `COST_PER_ACQUISITION`. Domestic acquisition becomes
£55 dual-fuel. *Every published figure moves* — the campaign currently spends £112.50 a quote.
Cheapest step, largest effect, and it needs no new research.

**R2 — Give business acquisition its real shape.** Route SME/I&C through
`broker_commission_gbp()` at billing time. This deletes a cost the model currently charges at
signup and adds one that runs the length of the contract, so it changes the timing of the P&L and
not just its level.

**R3 — Make the retention offer a price.** Remove `RESI_OFFER_COST_GBP` and
`IC_OFFER_COST_GBP` as cash lines; let the discount tiers reduce revenue, which they already
compute. Assert the double-count is gone: a retained account should differ from a lost one in
revenue and not in operating costs.

**R4 — Model the BAT as a time-indexed licence condition.** From 2022-04-01, a fixed-term offer to a
new customer must be available to existing ones; retention-only deals are permitted by derogation at
end of fixed term. This belongs in `company/compliance/domain_invariants.py`, which already carries
`effective_from`/`effective_to`, alongside the regulation commons. It is the first thing on this list
that changes the *world* rather than the company, so it is R13 baseline work and must be argued on
fidelity.

**R5 — Amortise acquisition over a customer lifetime in the analytics, not the P&L.** The accounts
expense it as incurred (GAAP/IFRS, and our P&L is right to); the CMA's economic analysis amortises
over six years. Both are correct in their own frame and the model should be able to show both.

**R6 — Connect acquisition spend to collateral.** The CMA records the mechanism directly: growing
fast means acquisition costs up front, which *"weakened a firm's balance sheet … increasing the
perceived riskiness of the supplier and, therefore, the quantity of collateral that trading
counterparties required."* We have a growth campaign and we have `B6_collateral_cash_death_loop`, and
nothing joins them. This is the highest-value item and the one that needs the most other work first.

**Not on the roadmap, deliberately:** picking a direct/brand-marketing CAC. No published GB-energy
figure exists, and the honest response to that is to model the channels we can source and record
that we cannot source the third — not to average two guesses.

## Still live
