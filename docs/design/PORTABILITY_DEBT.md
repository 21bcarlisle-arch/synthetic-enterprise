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

## The design law at the seams — this register is now the ALLOWLIST (A9, 2026-08-10)

Atom `A9_market_at_the_seams_design_law`, from
`docs/design/refs/ADVISOR_ANALYSIS_MARKET_PORTABILITY_2026-08-07.md`. The analysis splits the machine
into INVARIANT / PARAMETERISE / ADAPTER-SWAP / REBUILD. The middle two imply a design law, and this
atom owns it:

> **RULE 1** — no counterparty identity is hardcoded across a seam.
> **RULE 2** — every market-varying quantity is reachable as a table, not a literal.

Everything above this section RECORDS breaches under remediation-on-touch. That is the right rule for
shipped code and it stays. But a register that only records is a **cleanup, not a control**: it grows
monotonically and nothing stops the next breach from being added to it. `tests/architecture/test_market_at_the_seams.py`
is the other half — it makes a **NEW** breach FAIL, so the maintenance rule this file has always
stated ("add a row here **in the same change**") is now enforced rather than hoped for.

**How it works.** The test derives the seam surface (the two boundary packages plus the `*seam*.py`
naming convention — derived, never hand-listed, because a hand-list is fail-open by omission), scans
it by AST, and compares against the baseline block below. Prose is exempt and contract is not:
"this seam carries what Elexon publishes" is documentation of provenance; `mpan` as an argument name
or a payload key is the GB market spelled into the contract. Rows here are exact in **both**
directions — a new breach fails, and so does a row whose code has been remediated (that is the drain;
without it the ratchet is a cleanup again). The truth side (an AST scan of real code) and the
allowlist side (this hand-maintained file) share no source, so a wrong register cannot make the scan
agree with it.

**What it is not.** It builds no second market and no second segment — GB SME/I&C is the analysis's
recommended first extension and is a separate future draw. It sweep-renames none of the 58 baseline
sites: remediation-on-touch stands. It adds no scale-debt axis (C-S1..C-S5 stay at their own touch
points, per the cross-reference below).

**The baseline is the live core of rows #1 and #5** — the currency-in-field-name break and the
GB-baked seam vocabulary — measured at the seam surface only, which is why the counts here are far
smaller than row #1's repo-wide 6,850. Remediating a seam means **shrinking a row here in the same
change** and marking the table row above CLOSED with the commit that did it. Never widen a row to
make the test green.

<!-- BEGIN market-at-the-seams baseline -->
```text
# kind            path                                                 token        sites
# Recorded debt at the seam surface, 2026-08-10; renewal rows amended
# 2026-08-13 by KNIFE step 24 (register §3s) and again by step 25 (§3t) under
# the same-change rule -- the gas strike and the ToU offer are two more doors
# whose fields name a currency. Recorded rather than renamed: sweeping currency
# out of field names is a Money type, not a wall pass (remediation-on-touch).
# renewal_offer 12 -> 9, REVERTED 2026-08-24 (same day). The 9 -> 12 amendment recorded
# B4_competitor_field's two new crossing fields (`published_svt_gbp_per_mwh`,
# `published_market_switching_multiplier`) PRE-EMPTIVELY, on the reasoning that B4 was being
# built by another worker tick in the shared tree and "whoever commits first pays". That
# reasoning only holds in one direction. B4's code was UNCOMMITTED, so the row shipped debt
# the committed tree does not contain -- and this register is exact in BOTH directions, so
# `test_the_baseline_does_not_overstate_the_debt_it_records` then refused EVERY lane's commit
# until B4 landed. Observed: the H44 landing (an unrelated harness atom, four unrelated paths)
# was refused by this row. The same-change rule cuts both ways: a row may not be written for
# code that is not in the same commit, any more than code may be written without its row. B4
# re-adds these two sites in the commit that lands the fields.
# renewal_offer 9 -> 12, RE-ADDED 2026-08-24 by the commit that lands B4_competitor_field
# (L0 -> L1) -- the same commit carries `published_svt_gbp_per_mwh` and
# `published_market_switching_multiplier` into company/interfaces/renewal_offer.py, so the row
# and the code now arrive together and the register is exact in both directions again. This is
# the block above's own instruction being carried out, not a second pre-emptive amendment.
# RECORDED RATHER THAN RENAMED for the reason row #1 gives: the currency belongs in a Money
# type the adapter supplies, and lifting it out is a cross-cutting change, not a wall pass.
# growth_desk 13 -> 22, amended 2026-08-24 under the same-change rule (atom PB3). The
# net-new acquisition campaign needed the supplier's own quote budget on the world side, and
# the epistemic-wall ratchet refused the direct `simulation -> saas.growth_mandate` import,
# so the decision was routed through this seam as `plan_growth_campaign_year()` +
# `quote_cost_gbp()`. Nine more sites, every one of them row #1's shape: `net_assets_gbp`,
# `budget_gbp`, `headroom_gbp`, `quote_cost_gbp` -- a currency spelled into a field name.
# RECORDED RATHER THAN RENAMED, for the reason the block above already gives: getting the
# currency out is a Money type carried by the adapter, not a rename, and doing it here would
# put a cross-cutting type change inside a wall pass. The debt is real: a second market
# reading this seam gets a budget denominated in a currency it does not use.
# growth_desk 22 -> 25, amended 2026-08-28 under the same-change rule (roadmap R2 of
# WORKER_FINDING_THE_SOURCED_ACQUISITION_MODEL_IS_UNWIRED_AND_THE_INVENTED_ONE_IS_LIVE). Business
# acquisition stopped being a one-off spend and became an ongoing broker trail charged per kWh at
# billing time, so the world needs a monthly accrual schedule back across this seam:
# `broker_commission_schedule()` returns `{month, amount_gbp}` rows. Three more sites, all row
# #1's shape -- a currency spelled into a field name -- and the same disposition applies. Note the
# SECOND market quantity hiding in that door and not counted by this register: the trail is a rate
# per kWh, and kWh is as market-varying as GBP. It stays inside `saas/opex_ledger.py` and does not
# cross, which is why the door hands over a settled amount rather than a rate.
# dd_review_outcome 2 -> 6, and dd_review 0 -> 3, amended 2026-09-02 under the same-change rule
# (atom `D_opening_dd_seasonal_sizing`). Until today the direct debit had no estimate behind it:
# both books opened every customer at their FIRST ISSUED BILL, so the monthly payment was an
# accident of which month the account started in. Giving it an annualised opening amount means
# the world must be able to ask what that amount WAS -- `opening_monthly_amount()` returns it,
# `annual_dd_review_view()` now takes an `opening_dd_gbp` mapping, and the refusal path names
# the same quantity. Every new site is row #1's shape and nothing else: a currency spelled into
# a field name.
# WHY THIS IS NOT THE WIDENING THIS FILE FORBIDS. The forbidden move is loosening a row so an
# UNCHANGED seam stops failing. Here the seam genuinely gained a money field it did not carry
# before, and the register is doing its job by making that visible in the same commit that adds
# it. The disposition is unchanged and on-touch: getting the currency out is a `Money{amount,
# ccy}` type the adapter carries, which is row #1's cross-cutting remediation, not a rename to
# be done inside a billing-arithmetic change.
# THE SECOND MARKET QUANTITY BEHIND THIS DOOR, and it deliberately does not cross: the door takes
# NO unit rate and NO standing charge. The first draft did, which made the world import
# `company.pricing.ofgem_price_cap` to work out the supplier's own tariff -- two live wall
# crossings, refused at the gate. A supplier's tariff is not something the world computes on its
# behalf; the world asks what the payment was set to and is told. So `gbp` is the only
# market-varying token here, and that is by construction rather than by luck.
# Machine-read by
# tests/architecture/test_market_at_the_seams.py. Exact in both directions.
counterparty      company/interfaces/recorded_sim_interface.py         mpan         2
counterparty      company/interfaces/sim_interface.py                  mpan         7
counterparty      company/interfaces/sim_interface.py                  nbp          1
market_quantity   company/interfaces/credit_refund_requests.py         gbp          5
market_quantity   company/interfaces/dd_review.py                      gbp          3
market_quantity   company/interfaces/dd_review_outcome.py              gbp          6
market_quantity   company/interfaces/growth_desk.py                    gbp         25
market_quantity   company/interfaces/internal_seams.py                 gbp          5
market_quantity   company/interfaces/point_in_time_view.py             gbp          4
market_quantity   company/interfaces/recorded_sim_interface.py         gbp          5
market_quantity   company/interfaces/renewal_offer.py                  gbp         12
market_quantity   company/interfaces/renewal_rate_chain.py             gbp          9
market_quantity   company/interfaces/sim_interface.py                  gbp          12
market_quantity   company/interfaces/tou_offer.py                       gbp          3
# EP6 WALL-PROTOCOL ROWS, recorded 2026-08-21 and recorded LATE -- read the note below the
# block before treating this as an ordinary amendment. Three passes of the typed payment/flex
# contracts (273312507, 21c286c15, fbf44bb94) added `amount_gbp`, `cleared_price_gbp_per_mwh`
# and `utilisation_payment_gbp` to seam payloads. Every one is row #1's shape: a currency
# spelled into a field name. Getting it out means a Money type carried by the adapter, which is
# EP6's own design work and not a thing to do while the publish queue is stopped.
market_quantity   company/interfaces/collection_submission.py          gbp          3
market_quantity   interface/contracts/flex_observable_seam.py          gbp          6
market_quantity   interface/contracts/payment_observable_seam.py       gbp         11
market_quantity   simulation/payment_seam_adapter.py                   gbp          9
```
<!-- END market-at-the-seams baseline -->

### Why four rows were amended 2026-08-21 without a remediation, and why that is not the widening this register forbids

This file says **"Never widen a row to make the test green."** Four rows were widened on
2026-08-21 and the test went green, so the exception has to be argued rather than assumed.

What that sentence protects against is a lane that is *touching a seam* choosing the register
over the work. That is not what happened. Three separate EP6 passes added currency-named fields
and **none of them could have been stopped at commit time**: `test_market_at_the_seams.py` was
not on the pre-commit gate's always-run list, and the gate otherwise selects tests by name stem,
which no seam module matches. So the maintenance rule this register states — *add the row in the
same change* — was **unenforceable by construction** for the whole life of this control. Every
one of those commits was green when it landed.

The breach surfaced instead in the publish gate, ~27 hours later, as
`publishing has been down` with 43 failed publish attempts and a state file still naming a
different, already-passing test.

So the amendment is a LATE RECORD of debt that the same-change rule would have collected at
landing time, not a softening. The remediation (a Money type supplied by the adapter) stays
owed and stays EP6's.

**The actual repair is in the same change as this note**: `test_market_at_the_seams.py` is now
on the pre-commit gate's always-run list, beside `test_epistemic_wall_ratchet.py`, which was
added 2026-08-10 after the identical failure — a repo-wide AST scan enforced only by the publish
gate, so a breach could land and be found hours later. That comment ends *"`WORKER_FINDING_THE_
EPISTEMIC_WALL_IS_BREACHED_AT_HEAD_2026-08-09` is what that costs."* This is the second time,
with the second control of the same shape, and it cost 27 hours of publishing.

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
