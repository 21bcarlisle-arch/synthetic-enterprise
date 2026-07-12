# Settlement Timetable, Rebilling Cascade & DD Payment Allocation — Real UK Market Practice

Research date: 2026-07-12
Scope: feeds M2 (settlement timetable / DD cash-engine) build work, per SUNDAY_WIDE discovery-flood.

## Access note (read this before trusting confidence tags below)

Live fetch attempts this session: `www.elexon.co.uk` returned HTTP 403 with a Cloudflare
"challenge" mitigation header (`cf-mitigated: challenge`) on every path tried, including
`/knowledgebase/reconciliation/` and `/bsc-and-codes/rules-guidance/settlement-timetable/` — the
site is bot-walled and could not be read this session. `www.ofgem.gov.uk` is reachable (HTTP 200
on the root and on `/search`), but the specific back-billing guidance URL I tried
(`/information-consumers/energy-advice-households/back-billing`) returned a genuine
"Sorry, we can't seem to find that content for you" 404 — Ofgem appears to have moved or renamed
that page since it was last indexed, and the site's own search results still point at the same
dead URL. Per R9, every finding below is tagged for how it was obtained: **[M]** = recalled from
well-established training-era domain knowledge, cross-referenced against internally-consistent
detail (BSC structure, Bacs scheme mechanics) I have moderate-to-high confidence in but could NOT
freshly verify against a live document this session; **[L]** = specific numeric/code-level detail
I recall with lower confidence and flag explicitly as needing direct verification before being
treated as authoritative (e.g. wired into a compliance-critical invariant). Nothing below should
be read as freshly fetched evidence — treat it as a structured recall pass to be verified against
Elexon's actual BSC Section T / Settlement Calendar (once reachable) and Ofgem's actual SLC text
before M2 encodes exact day-offsets or licence-condition numbers.

---

## (a) Elexon BSC settlement run timetable

**domain**: other (industry_systems / settlement)
**assumption_tested**: whether the simulation's planned "real settlement timetable (D+1/D+... true-up)" (W3_2_settlement_timetable) reflects the real BSC settlement-run cascade shape.
**benchmark_value**: [M] The BSC (Balancing and Settlement Code) does not settle a trading day once — it runs the SAME Supplier Volume Allocation / imbalance calculation for each Settlement Date MULTIPLE times over an extended window, each run using progressively better data (estimated/default profile data → actual metering data → agreed dispute resolutions). The historical (pre-reform) run sequence, commonly cited as **II → SF → R1 → R2 → R3 → (DF) → RF**, spans from a few working days after the trading day (Initial Settlement) out to roughly **12–14 months** later for Final Reconciliation (RF) under the old Standard Settlement Timetable. [L] I do not have high confidence in the exact day-offsets for each individual run code (II/SF/R1/R2/R3) this session — these should be verified directly against Elexon's BSC Section T / published Settlement Calendar once the site is reachable, rather than hard-coded from this recall.
**confidence**: M (structure/shape), L (exact day-offsets per run)
**source**: Elexon BSC Section T ("Trading Charges / Settlement"), Elexon's published Settlement Calendar / Guidance on Standard Settlement Timetable — cited from training-era knowledge, NOT fetched live this session (site Cloudflare-walled).
**date**: 2026-07-12
**finding**: The important structural fact for M2 is the CASCADE itself — a single settlement date is revisited by multiple runs over a long tail (weeks to over a year), each capable of revising the volume/imbalance-cost allocation for that historical period. I also recall the November 2022 "Reconciliation Reform" (BSC Modification, part of the run-up to Market-wide Half-Hourly Settlement) shortened this tail and reduced the NUMBER of runs for most supplier meter types — this is directly relevant to M2 because a 2026-scoped build should target the REFORMED (shorter) timetable, not the pre-2022 one, but I could not verify the reformed timetable's exact run count/offsets this session. **Action**: before W3_2_settlement_timetable is built, get a live fetch of Elexon's current Settlement Calendar (once the Cloudflare block clears, or via an alternate authorised channel) rather than relying on this recall for exact numbers — the STRUCTURE (multi-run cascade, long tail, later runs override earlier ones) is solid enough to design against now; the exact offsets are not.

**domain**: other (industry_systems / settlement)
**assumption_tested**: whether "settlement run" and "customer catch-up rebilling" (the already-built D3 atom) are the same mechanism.
**benchmark_value**: [M] They are NOT the same mechanism in the real market, and conflating them would be a fidelity error. The BSC settlement-run cascade operates at WHOLESALE/PORTFOLIO level — it revises how much a SUPPLIER (as a BSC Party) owes/is owed for its aggregate metered volume vs. its contracted position, settled via the imbalance/cash-out mechanism between the supplier and BSCCo/Elexon. Customer-level catch-up rebilling (estimated meter read corrected against an actual read) is a RETAIL billing mechanism governed by Ofgem Standard Licence Conditions (back-billing cap), entirely separate from — though ultimately funded by — the wholesale settlement process.
**confidence**: M
**source**: General BSC/SVA (Supplier Volume Allocation) structure knowledge — training-era, not fetched live this session.
**date**: 2026-07-12
**finding**: A real supplier does NOT re-issue individual customer bills every time an Elexon reconciliation run (R1/R2/R3/RF) revises the wholesale numbers — that would require re-billing millions of customers repeatedly for over a year after every trading day, which is not how UK retail billing works in practice. Instead, wholesale settlement revisions flow into the supplier's own P&L/treasury as a cost/revenue TRUE-UP in the period the revision lands, and only reach customers indirectly via future tariff-setting (SVT cap movements, fixed-tariff renewal pricing) — not via retroactive individual rebills. **This directly matters for M2**: the settlement-timetable atom (W3_2) should model the wholesale-side true-up hitting the company's own books/cash position (consistent with D2_three_clocks' "three clocks" framing — physical/financial/regulatory), NOT wire itself into the customer-facing catch-up rebilling mechanism the D3 atom already owns. Building W3_2 as "another instance of D3's per-customer catch-up" would double up two genuinely different real-world mechanisms under one name.

---

## (b) Rebilling / adjustment cascade pattern when a settlement run revises a prior estimate

**domain**: other (billing_metering / policy_costs)
**assumption_tested**: how real suppliers absorb a wholesale settlement revision without disrupting customer billing.
**benchmark_value**: [M] Standard industry pattern: (1) supplier accrues wholesale costs against ESTIMATED/interim settlement data as trading happens; (2) as later runs (R1/R2/R3/RF) revise the true metered volume and imbalance price, the supplier's own management accounts absorb the delta as a true-up adjustment (a cost/revenue swing recognised in the period the run lands, i.e. non-monotonic and can be a credit or a further charge); (3) large systemic revisions (e.g. a whole GSP-group calculation correction) are managed as portfolio-level treasury/hedging events, feeding FORWARD into tariff and risk decisions, not backward into individual customer accounts.
**confidence**: M
**source**: General SVA/BSC settlement + supplier treasury practice knowledge — training-era, not fetched live.
**date**: 2026-07-12
**finding**: The project's own D2_three_clocks atom (`docs/design/maturity_map.yaml`, level_current=0, depends_on W1_reveal_over_time) already frames this correctly as reconciling "physical/financial/regulatory" clocks per bill, and its own evidence trail already found a real, quantified instance of the underlying gap (saas/bill_generator.py's blended-rate non-commodity billing vs simulation/hedged_settlement.py's per-levy real-world cost, a ±27.7%/-25.3% non-monotonic gap across years) — this is the SAME class of finding as the real-world pattern above (billed ≠ settled, reconciled later, not customer-facing). This validates the direction D2/W3_2 are already pointed in; no correction needed to the existing framing, but it confirms the sequencing dependency (W3_2 depends_on D2_three_clocks, D2 depends_on W1_reveal_over_time) is the right shape — settlement-run cascade modelling should sit on TOP of the reveal-over-time spine, not be built as a customer-facing rebilling clone of D3.

---

## (c) Direct-debit payment-allocation practice when a rebill changes the amount owed mid-cycle

**domain**: other (banking_payment_rails)
**assumption_tested**: how real suppliers reconcile a mid-cycle billing correction against an already-scheduled or already-processed Direct Debit collection.
**benchmark_value**: [M] Two dominant DD product shapes in UK energy retail: (i) **fixed/"budget" DD** — a smoothed monthly instalment set from an annual estimate, reviewed periodically (commonly at least annually, or triggered by an abnormal usage/rebilling event); a mid-cycle correction adjusts the account's running balance and is absorbed into the NEXT instalment review, not an immediate extra collection. (ii) **variable/"accurate" DD** — collects the exact billed amount each cycle; a rebill simply changes the amount of the NEXT scheduled collection to match the corrected bill.
**confidence**: M
**source**: General UK energy-supplier billing/DD product knowledge — training-era, not fetched live.
**date**: 2026-07-12
**finding**: In neither shape does a real supplier silently alter a DD collection that has ALREADY been submitted into the Bacs processing pipeline — this is a hard rails constraint (see below), not a policy choice. A correction becomes a NAMED, visible adjustment line on the next bill/collection (consistent with Ofgem's clear-billing expectations), and a large correction is commonly offered to the customer as a spread-over-several-instalments payment plan rather than a lump-sum debit, especially for a debt (undercharge) correction.

**domain**: other (banking_payment_rails)
**assumption_tested**: whether a supplier can change a Direct Debit amount inside an already-in-flight collection cycle.
**benchmark_value**: [M] No — under the Bacs Direct Debit Guarantee scheme rules, any change to the AMOUNT, DATE, or FREQUENCY of a Direct Debit must be notified to the payer IN ADVANCE of the collection being debited. [L] The commonly-cited default advance-notice period is **10 working days "or as otherwise agreed"** — many billers (including energy suppliers) negotiate a shorter agreed notice period with their bank/Bacs sponsor for routine variable-amount collections, sometimes cited around 3 working days, but I do not have high confidence in the exact negotiated figure for UK energy suppliers specifically and flag it [L].
**confidence**: M (the advance-notice principle itself), L (the exact day-count figure)
**source**: Bacs/Pay.UK Direct Debit Guarantee terms — training-era knowledge, not fetched live this session.
**date**: 2026-07-12
**finding**: This is DIRECTLY consistent with what the project's own W5_1_banking_payment_rails atom already found and built (`docs/design/maturity_map.yaml`): its 2026-07-11 entry cites a real, WebSearch-verified 3-working-day Bacs processing cycle (submission → AUDDIS mandate confirm/reject on day 2 → collection), and ARUDD failure reports arriving up to 2 working days AFTER the collection day, "never instantly." **Action for M2**: a rebill/catch-up correction discovered WHILE a DD collection is already in the 3-day Bacs pipeline cannot retroactively change that collection's amount — it must land on the NEXT collection cycle, with its own advance-notice lead time if the amount changes materially. If M2's DD cash-engine design lets a same-cycle correction silently alter an in-flight collection amount, that would be a rails-physics violation of the same class W5_1 was built specifically to prevent (its own stated purpose: "cash lands when the rails say," not when the company recalculates).

---

## Cross-reference: what's already registered in `docs/design/maturity_map.yaml` (read-only, not edited)

Grepped for `settlement`, `DD`/`direct debit`, `R1`/`R2`/`R3`/`RF`, `Section T`, `BSCP`, `banked clock`, `three_clocks` across the file. Relevant atoms found:

- **W3_2_settlement_timetable** (`lane: W3_industry_systems`, `real_world_twin: "Elexon's SBP/SSP settlement run timetable"`) — `level_current: 0`, `level_target: 2`, `evidence: []`, `simplifications: []`, `expert_hour: not_attempted`, `depends_on: [D2_three_clocks]`. **NOT YET BUILT AT ALL** — this is the direct target atom for the settlement-run-cascade research above; it currently has zero evidence and zero framing text, so this document is genuinely new input for it, not confirmation of existing work.
- **D2_three_clocks** (`lane: D_billing_metering`, `real_world_twin: "settlement timetable D+1/D+... true-up cycle"`) — `level_current: 0`, `level_target: 2`, `depends_on: [W1_reveal_over_time]`. Already has one real, quantified finding in its evidence trail (the blended-rate vs per-levy non-commodity billing gap, ±27.7%/-25.3% non-monotonic across years) that is the SAME CLASS of billed-vs-settled divergence the real-world settlement cascade produces — good sign the framing is already pointed correctly; loop_stage is `idle` pending the advisor's epoch framing, not yet a live build.
- **W5_1_banking_payment_rails** (`real_world_twin: "Bacs Direct Debit cycle (AUDDIS/ARUDD/ADDACS), card acquirer settlement"`) — `level_current: 2`, `level_target` not confirmed in this read but clearly built substantially: `simulation/bacs_rails.py` (rails timing sim, 3-day cycle, real AUDDIS/ARUDD reason codes, WebSearch-verified) and `simulation/dd_collection_book.py` (wired into the live DD flow, reusing `arrears_engine.py::payment_outcome()`'s unchanged decision with an independently-seeded RNG for timing) are both built and tested. This is the RAILS-TIMING side of (c) above — already well-covered; the remaining gap per (c)'s finding is specifically the MID-CYCLE REBILL INTERACTION (does a same-cycle correction respect the 3-day pipeline / advance-notice rule), which doesn't yet appear as an explicit scenario in what I could see of this atom's evidence.
- **D3 (estimated-billing/catch-up rebilling atom, name not captured in this grep pass but clearly identifiable from its evidence text)** — already built to level 3 (real_world_twin met, Expert-Hour passed twice). **Internal inconsistency worth flagging**: one 2026-07-11 evidence entry cites the back-billing 12-month cap as **"Ofgem SLC 31A"**, while a later 2026-07-12 entry (`ADVISOR_STEER_BACKBILLING_GATE.md`) cites the SAME cap as **"SLC 21BA."** [L] My own best recollection is that the substantive domestic back-billing licence condition is generally referred to as SLC 21B/21BA ("Back-Billing"), not 31A — but I could not confirm this independently this session (Ofgem's own back-billing guidance URL 404'd, and I did not locate Ofgem's current consolidated Standard Licence Conditions document to check the number directly). **Recommend**: verify the correct SLC number directly against Ofgem's consolidated domestic supply licence conditions document before the next time this mechanism is touched — a compliance-critical invariant (`company/compliance/domain_invariants.py::BACK_BILLING_CAP_RESPECTED`, per the D3 atom's own evidence) citing the wrong licence condition number is a real (if likely cosmetic) documentation defect, not a functional one, since the actual 12-month cap VALUE appears correctly encoded regardless of which SLC label is attached to it.

---

## Summary for the M2 build

The most actionable finding: **the wholesale settlement-run cascade (Elexon's II/SF/R1/R2/R3/RF-style multi-run re-settlement of each trading day over an extended tail) and the customer-facing catch-up-rebilling mechanism the D3 atom already built are two genuinely different real-world mechanisms that must NOT be collapsed into one** — the former is a portfolio-level wholesale cost/revenue true-up flowing into the company's own books and future tariff-setting (which is exactly what the still-unbuilt W3_2_settlement_timetable / D2_three_clocks pair is already correctly scoped toward), while the latter is an individual-customer retail billing correction bounded by the Ofgem back-billing cap (which D3 already handles). When M2 gets to the DD cash-engine step, the concrete rails constraint to design against is that a same-cycle billing correction cannot retroactively alter a Direct Debit collection already inside Bacs's ~3-working-day submission/processing pipeline (which W5_1_banking_payment_rails has already modelled accurately) — a correction must land on the NEXT collection cycle, with its own advance-notice lead time if the amount changes materially, and a large correction should be exposed to the customer as a visible adjustment line or a spread payment plan rather than a silent same-cycle amount change. Live verification of Elexon's exact settlement-run day-offsets was blocked this session (Cloudflare 403 on elexon.co.uk) and should be re-attempted via an alternate channel before W3_2 encodes specific numeric offsets; similarly, the SLC 31A vs 21BA naming inconsistency already sitting in the project's own D3 evidence trail is a small, cheap, worth-fixing loose end for whoever next touches that atom.
