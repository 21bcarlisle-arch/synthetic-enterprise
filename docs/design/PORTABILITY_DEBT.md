# PORTABILITY_DEBT.md — the consolidated, rankable portability-debt register

**Status:** DISCOVER artifact (doc-only). Created 2026-07-22 by the always-drawable forward-discovery
lane (`H_forward_discovery_draw`, F4 graduation, network-free) under **RULE 0 / R17** — the tick never
rests while authorized DISCOVER/FRAME work exists at any priority. This file **opens no build atom and
moves no map level**: consolidating already-surfaced debt is DISCOVER output, not a graduation. The
*code-remediation* items below (a `Money` type, a settlement-granularity config, a regime-optional cap
invariant) remain **director/twin BUILD calls** and are named here as candidates only, not opened.

> **Director ruling — 2026-07-22 (console; F4 graduation):** *"GRADUATE item (1) only: the doc-only
> `PORTABILITY_DEBT.md` register. Items (2)-(4) become remediation-on-touch notes in it, not builds."*
> This ratifies exactly the state below: **item (1) — this consolidated register — is the graduation**
> (doc-only, done), and every code-remediation row (the `Money` type #1, VAT-by-jurisdiction #2,
> settlement-granularity config #3, and the rest) is a **remediation-on-touch note, NOT a build**. No
> atom is opened by this ruling; a row becomes a build only if the director later opens one explicitly.
> The register's own **append-and-rerank maintenance rule** (below) is the standing home for future debt.

## Why this file exists

The **portability doctrine** (`docs/staging/done/PORTABILITY_DESIGN_CONSTRAINTS.md`, 2026-07-10,
director-approved standing constraint) says: honouring a portability constraint in already-built code
that would need rework is **logged as portability debt, not fixed opportunistically**. The
**scale-readiness addendum** (`PRODUCTION_READINESS_SCALE_ADDENDUM.md`, 2026-07-13) adds the same
remediation-on-touch rule for its five constraints.

The F4 international-expansion probe (`docs/market_research/f4_international_expansion_probe.md`,
2026-07-22) surfaced the **meta-finding** this file closes: *the portability debt the doctrine says to
"log" was logged **diffusely** — inline notes scattered across modules, with no rankable register.
"Mentioned somewhere" reads as covered when it isn't.* This is that register: one place, ranked by
break depth, evidence-anchored to actual repo code (independent of SIM ground truth), so a future
second-market/second-product build can size the rework instead of rediscovering it.

**Long-range destination** (the doctrine's frame): one multi-segment / multi-geography / multi-product
supplier. The two review lenses are *would a second market fit behind this seam* and *would a second
product fit inside this brain*. F4's verdict, now the organising principle of this register:
**the architecture is portable where it reasons and GB-bound where it transacts** — the brain/governance
layer ABSORBS a second market; the transactional core BREAKS.

## The register

Break depth: **1 (deepest)** = structural, pervasive, blocks any non-GB market · **2** = structural but
localised · **3** = value/config only. Remediation: **on-touch** = fix at next real touch of that code
(never speculatively) · **config** = extract a named parameter · **class** = a type/class change, not a
value. All items are **remediation-on-touch** debt unless a director opens an atom.

| # | debt item | layer | break depth | evidence (repo code, verified 2026-07-22) | remediation | status |
|---|-----------|-------|:-----------:|-------------------------------------------|-------------|--------|
| 1 | **No `Money`/currency abstraction** — monetary amounts are raw floats named `*_gbp`; currency is baked into the field name, so a second currency cannot be represented without touching every arithmetic site | transactional core | **1** | **6,850** `*_gbp` field-name occurrences across **330** `.py` files (`grep -rhoE '[a-z_]+_gbp\b'` over company/saas/sim/simulation/interface) | on-touch (introduce a `Money{amount, ccy}` type at next billing-arithmetic touch; do **not** sweep-rename) | OPEN — deepest blocker |
| 2 | **VAT hardcoded, keyed by segment not jurisdiction** — `0.05`/`0.20` literals per customer segment, no jurisdiction axis; IE domestic electricity is **9%** (temp to 2030-12-31; 13.5% baseline) — a quantified **~2× factor error**, not just jurisdiction-blindness | transactional core | **2** | `company/billing/invoice.py:19` `VAT_RATE = 0.05`; segment dicts in `saas/non_commodity.py` (`vat_rate()`), `company/billing/dual_fuel_bill.py` (`resi`/`SME` → `0.05`) | class (add a jurisdiction axis to `vat_rate()`; keep segment axis) | OPEN |
| 3 | **Settlement granularity `48` duplicated** — the half-hour count is a literal spread across the code, not one config; mild for IE (also 48 × 30-min) but a **hard break** for ERCOT-15min / NEM-5min. The gentle pick (IE) *hides* it. IE also adds a 5-min imbalance-*pricing* sub-layer the `48` constant flattens away | transactional core | **1** (for non-HH markets) | literal `48` referenced in **41** `.py` files across company/sim/simulation | config (`market.settlement_granularity`) | OPEN |
| 4 | **Reconciliation window Elexon-hardwired** — the settlement/reconciliation timetable is GB-specific and **duplicated** across the sim and company sides | transactional core | 2 | duplicated sim + company reconciliation-window logic (F4 §4) | config + de-dup at next touch | OPEN |
| 5 | **SIM-seam payload vocabulary GB-baked** — the sim/company boundary payloads carry GB-specific tokens (`mpan`, `:SP` settlement-period suffixes, Elexon/NBP references) rather than regime-neutral field names | seam | 2 | `mpan`, `:SP`, Elexon/NBP tokens in the sim-interface payloads (F4 §4) | on-touch (regime-neutral field naming at next seam change) | OPEN |
| 6 | **Price-cap invariant structurally assumes a GB institution** — the domestic price-cap check presumes a cap *exists*; Ireland has **no** domestic cap, so the invariant must become **regime-optional, not re-anchored** (a class change, not a value change) | brain (invariant class) | 2 | `company/compliance/domain_invariants.py` cap invariant; contrast the already-present `jurisdiction` field (lines 85, 104) which the brain layer *does* honour | class (make cap invariant regime-optional) | OPEN |
| 7 | **No PSO-levy-class bill-line abstraction** — IE has a mandatory **per-customer PSO levy** with **no GB bill-line analogue** (€1.46/mo ex-VAT 2025/26; total €125.38m; historically zero or a negative rebate — its value can **flip sign**). It is STRUCTURE, a missing regime-keyed line item, not a value tweak | transactional core | 2 | no regime-keyed extensible non-commodity line-item slot for a market-mandated levy (F4 §9) | class (regime-keyed bill-line registry) | OPEN |

## What ABSORBS (the portable-where-it-reasons half — recorded so the register is honest both ways)

Not debt — carried here so the split is legible and a future build doesn't "remediate" what already works:

- **Obligations register is `regime`-keyed + extensible** (`company/compliance/obligations_register.py`) — a
  CRU obligation fits as new rows; law is keyed by regime, not implicitly Ofgem.
- **Invariant *classes* carry `jurisdiction` + effective-dates** (`domain_invariants.py`) — a non-UK
  invariant can't silently fire against UK output.
- **Decision architecture + observability are counterparty-free** (`internal_seams.py`) — no counterparty
  hardcoding in the reasoning layer.

F4's verdict stands and is now consolidated: **transfer is a data-and-adapter exercise for the brain, a
real rework for the plumbing.**

## Doctrine cross-reference (the seven standing portability constraints + five scale constraints)

The debt items above are the *concrete instances* of the abstract constraints already in `CLAUDE.md`:
no hardcoded clock speed / settlement granularity (→ #3) / monetary treatment (→ #1), product as
first-class wherever fuel is one, obligations register keyed by regime not Ofgem (ABSORBS — see above).
Scale constraints C-S1..C-S5 (event-arrival tolerance, idempotency/replay, async wall contracts,
persistence-behind-interface, time-scale-invariance) are a **separate** debt axis (scale, not geography)
and are tracked at their own remediation-on-touch points — not duplicated here to avoid a second diffuse
log. If a scale-debt instance ever needs a rankable home, it belongs in a sibling `SCALE_DEBT.md`, not
smuggled into this geography register.

## Maintenance rule

This register is **append-and-rerank**, not authoritative-until-stale: when a real touch remediates an
item, mark it CLOSED with the commit that did it (never delete the row — the history is the point). When
a new portability break is discovered (a third market, a new bill line), add a row here **in the same
change** rather than an inline note — that is the whole reason this file exists. A portability break
"mentioned somewhere" but not in this table is, by this file's own doctrine, **not logged**.
