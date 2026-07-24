# UK Supplier Forward-Hedge Counterparty Landscape — Market Research

**Purpose:** grounds a new counterparty dimension on `ForwardContract`
(`company/trading/forward_book.py`) so a per-counterparty credit-exposure
register and margin-call/collateral mechanic are built on real market
structure, not invented plausibility. Read-only research; no simulation
code read or changed by this agent.

**Date:** 2026-07-24
**Method:** live fetch of primary/authoritative sources (Ofgem, ICE, ECC/EEX,
LCH, Wikipedia-mirrored primary reporting of Reuters/Bloomberg/BBC) via
`curl`, this session, 2026-07-24. URLs and exact extracted text quoted
below. Where no public figure exists, the gap is flagged explicitly per R9
(evidence before narrative) — no fabricated numbers.

---

## RQ1 — Who does a UK supplier actually trade forward hedges WITH?

**domain**: forward_curve / credit_risk
**assumption_tested**: A UK supplier's forward hedge book has counterparties that fall into distinct types: cleared-exchange, bilateral OTC, and broker-intermediated OTC — and clearing venue is distinct from executing counterparty.
**benchmark_value**: Confirmed three real channel types:
1. **Exchange-cleared, CCP-guaranteed** — trades executed on ICE Futures Europe (UK NBP gas, UK power) or EEX/Nasdaq/N2EX-adjacent venues, novated to a central counterparty (CCP) at execution. Fetched ICE product page for "UK NBP Natural Gas Futures" (`https://www.ice.com/products/910/UK-NBP-Natural-Gas-Futures`, retrieved 2026-07-24) lists `Exchange: ICE Futures Europe`, `Clearing Venues: ICEU` — i.e. **ICE Clear Europe** is the CCP; the exchange (IFEU) and the CCP (ICEU) are explicitly separate fields on the contract spec, confirming the venue/CCP distinction. For EU-domiciled power/gas futures the equivalent CCP is **European Commodity Clearing AG (ECC)**, part of EEX Group (Wikipedia, `https://en.wikipedia.org/wiki/European_Commodity_Clearing`, retrieved 2026-07-24: "ECC assumes the counterparty risk and guarantees the physical and financial settlement of transactions... provides clearing services for EEX, EEX Asia and EPEX SPOT").
2. **Bilateral OTC (ISDA/EFET-governed)** — direct trades with banks, energy trading houses/majors (Shell, BP, Vitol, Trafigura, Uniper-type), generators, and other suppliers, settled under a master agreement (ISDA or EFET) with a bilateral Credit Support Annex (CSA).
3. **Broker-intermediated OTC** — voice/screen brokers (e.g. ICAP/Tullett Prebon-type energy desks) arrange bilateral trades without taking principal risk; the broker is an intermediary, not a counterparty to the trade.
4. **LCH** (`https://en.wikipedia.org/wiki/LCH_(clearing_house)`, retrieved 2026-07-24) is confirmed as "a British clearing house group" offering multi-asset clearing (SwapClear for OTC derivatives) — relevant if any OTC-but-cleared swaps are modelled, distinct from the fully-bilateral-uncleared case.
**confidence**: H — primary product-spec and clearing-house pages, fetched directly this session.
**source**: ICE product page (ice.com/products/910), ECC Wikipedia (mirrors ECC's own "About" description), LCH Wikipedia. All retrieved 2026-07-24.
**date**: 2026-07-24
**finding**: The clearing-venue/executing-counterparty distinction is real and load-bearing — a cleared trade's *credit* counterparty (for margining purposes) is the CCP (ICE Clear Europe / ECC), not the original trade counterparty, because of novation. A bilateral OTC trade has no such substitution — the named counterparty carries full credit risk for the life of the trade. This directly supports giving `ForwardContract` a `counterparty_type` (CCP-cleared vs bilateral-OTC vs broker-intermediated) rather than only a `counterparty_name`, because the credit-exposure mechanics differ structurally by type, not just by identity.

---

## RQ2 — Volume distribution across channels

**domain**: forward_curve / credit_risk
**assumption_tested**: A mid-size UK supplier's forward book splits roughly X% cleared-exchange vs Y% bilateral-OTC, with a small number of concentrated active counterparties.
**benchmark_value**: **No public, supplier-level breakdown was found.** Suppliers do not publish "% of hedge book cleared vs bilateral" in RNS filings, CSS PDFs, or Ofgem disclosures — this is treated as commercially sensitive trading-desk information, not a regulatory disclosure requirement.
**confidence**: ungrounded-gap for the precise split; L (indirect/structural reasoning) for a defensible range.
**source**: Searched Ofgem Financial Resilience Transparency Report 2025 (`https://www.ofgem.gov.uk/sites/default/files/2025-04/FRC_transparency_report.pdf`, retrieved and full-text-extracted 2026-07-24) — this 20-page report covers capital/liquidity resilience requirements in detail but contains **no counterparty-mix or cleared/bilateral split disclosure**. General search of Ofgem, NAO and CMA publications (DuckDuckGo/Bing queries this session) surfaced no such figure.
**date**: 2026-07-24
**finding**: This is an explicit **R9 ungrounded-gap** — do not fabricate a supplier-reported split. The most defensible *inferred* structure, reasoned from market mechanics rather than a cited figure: standardised, liquid, near-dated products (prompt month/quarter/season baseload power and NBP gas, out to ~2-3 years) are the products actually listed on ICE/EEX and are where exchange liquidity concentrates: it is standard market practice (well-documented convention, not a specific % source) for suppliers to execute the *liquid, standard-tenor* portion of their hedge programme on-exchange (cleared) and use bilateral OTC for bespoke shapes (e.g. long-dated PPAs, shaped/profiled power, non-standard tenors, and CfD-adjacent structures) that don't have a listed contract. A plausible planning range — **labelled inferred-best-estimate, not sourced** — is 40–70% cleared-exchange / 30–60% bilateral-OTC for a mid-size supplier's flat/standard hedge volume, with bespoke/shaped/PPA volume close to 100% bilateral by construction. Active bilateral counterparty COUNT for a mid-size supplier is plausibly small (order of magnitude: single-digit to low-teens active ISDA counterparties — banks + 2-4 trading houses + a couple of generator PPA counterparties), reasoned from the fact that ISDA/CSA onboarding has real legal/credit setup cost per counterparty, so suppliers concentrate rather than spread thin — again **not a cited figure**.

---

## RQ3 — Credit/collateral mechanics per channel

**domain**: credit_risk
**assumption_tested**: Cleared trades require initial + variation margin to a CCP (daily/intraday); bilateral OTC uses CSA-governed collateral with credit limits anchored to counterparty rating.
**benchmark_value**: Confirmed structurally — this is standard, well-documented CCP/ISDA market architecture, not UK-energy-specific:
- **Cleared**: a CCP (ICE Clear Europe / ECC / LCH) requires **Initial Margin** (IM) at trade inception sized to potential future exposure, plus **Variation Margin** (VM) marked and called at least daily (often intraday in volatile markets) as the position's MtM moves. ECC's own description (fetched above) states it "guarantees the physical and financial settlement of transactions" — the guarantee mechanism *is* the margin system; this is standard CCP risk-management architecture common to ICE Clear Europe, ECC and LCH alike.
- **Bilateral OTC (ISDA + CSA)**: collateral terms are negotiated per counterparty pair in a Credit Support Annex — typically an unsecured **Threshold** (an amount of MtM exposure the counterparty may run before collateral is called) sized to the counterparty's credit rating (higher-rated counterparties get a higher/uncapped threshold — e.g. AA-rated banks historically often had large or zero-threshold CSAs pre-2008; post-crisis thresholds have compressed toward zero for most trading pairs), a **Minimum Transfer Amount**, and a **credit limit** that a supplier's own credit/risk function sets per counterparty, itself a function of (a) published agency rating, (b) internal assessment of the counterparty's exposure/name, and (c) the size of any CSA threshold already negotiated.
**confidence**: M — this is standard, widely-documented ISDA/CCP market architecture (not UK-energy-specific primary-sourced this session beyond the CCP-guarantee language above), well-established and low-risk to assert as market convention.
**source**: ECC/ICE fetched pages (as above) for the CCP-guarantee mechanism; ISDA/CSA structure is standard derivatives-market convention (ISDA Master Agreement + CSA is the industry-standard bilateral OTC documentation framework worldwide).
**date**: 2026-07-24
**finding**: Supports the target design directly: a **cleared** `ForwardContract` should MtM against a CCP with margin called ~daily and no meaningful "credit limit" concept (CCP absorbs member default risk via its default waterfall) — the credit-exposure register's per-counterparty logic is really only load-bearing for the **bilateral-OTC** subset. A "rating-anchored prior modulated by observed settle/dispute history" cap design (as posed in the task) is a reasonable model of how a real credit-risk desk sets bilateral limits: agency rating sets the starting ceiling, and a track record of clean settlement (or disputes/late payment) adjusts it up or down over time — this matches real practice even though no single public source states the exact formula (credit-limit-setting methodology is internal/proprietary at every real supplier).

---

## RQ4 — Are counterparty credit ratings publicly observable?

**domain**: credit_risk
**assumption_tested**: A supplier can legitimately observe published agency ratings (S&P/Moody's/Fitch) of its trading counterparties without violating the epistemic wall; it cannot observe a counterparty's true, unpublished default probability.
**benchmark_value**: **Yes, grounded.** Long-term issuer credit ratings from S&P Global Ratings, Moody's and Fitch are published and are explicitly designed as a public signal for exactly this purpose — market counterparties (including energy trading desks) routinely reference published headline ratings (e.g. "A-", "Baa2", "BBB+") in credit policy documents and press releases without needing subscriber access to the underlying rating rationale/reports (which ARE paywalled — the headline letter-grade rating itself is public; the detailed analytical report is not). Example already surfaced in this research: Uniper's near-collapse and nationalisation was reported with explicit reference to rating-agency and market credit actions around it (Reuters/Bloomberg coverage retrieved via Wikipedia mirror, `https://en.wikipedia.org/wiki/Uniper`, retrieved 2026-07-24).
**confidence**: H — this is a well-established, easily-verified fact about how credit ratings function as a market institution (the entire point of a published issuer rating is public observability); not dependent on a single fetched page.
**source**: General market-structure fact (S&P/Moody's/Fitch business model is public-rating-as-product); Uniper case as illustrative example of ratings/credit actions being publicly reported in real time.
**date**: 2026-07-24
**finding**: This cleanly supports the epistemic wall: `ForwardContract`'s counterparty dimension may carry an observable **published rating band** (e.g. "A", "BBB", "BB or below / unrated") as a legitimate input a real supplier could read — this is NOT a simulation-internal read. What must stay wall-side is any *true* underlying default probability, internal risk model, or non-public rating-agency analytical detail — those are simulation-internal ground truth the company must infer from observed behaviour (settlement history, late payment, disputes), not read directly.

---

## RQ5 — Collateral/margin-call death-loop: is this a real failure mode?

**domain**: credit_risk
**assumption_tested**: A wholesale price spike can trigger margin/collateral calls that drain a supplier's liquidity faster than its hedges protect the book — a real, evidenced failure mode, not an invented one.
**benchmark_value**: **Grounded, but with an important nuance the research surfaced — worth stating precisely rather than overclaiming:**
- **UK domestic supplier failures, autumn 2021–2022 (30 suppliers, incl. Bulb):** the Ofgem-commissioned Oxera review (referenced directly in Ofgem's own Financial Resilience Transparency Report, `FRC_transparency_report.pdf`, fetched and full-text-extracted 2026-07-24) states the dominant root cause was the **opposite** of a margin-call death-loop on a hedged book: "Having agreed fixed low-cost deals to attract more customers, some suppliers had not purchased energy in advance to 'hedge' their risk and could not afford to buy energy at elevated prices" — i.e. UK domestic-market failures were overwhelmingly **naked/under-hedged exposure**, not collateral calls killing well-hedged books. BBC's contemporaneous report on the same Oxera review used the phrase suppliers treated market entry as a "free bet" (`https://www.bbc.com/news/business-61353794`, retrieved 2026-07-24, full text extracted). Bulb's collapse (Nov 2021, £1.7bn government support, confirmed via `https://en.wikipedia.org/wiki/Bulb_Energy`, retrieved 2026-07-24) sits in this same under-hedged-exposure category, not a documented margin-call-liquidity case.
- **The margin-call liquidity-drain mechanism IS real, but the clearest evidenced cases sit one level up the value chain — at generators/large integrated energy traders, mostly continental European, in 2022:** Uniper (Germany, Fortum-majority-owned) required a €15bn German-government rescue (July 2022) and full nationalisation (Sept–Dec 2022, ~$29bn total cost per Reuters) after running out of cash buying replacement gas at spot prices when Russian pipeline supply was cut, with liquidity support explicitly structured around a "€4 billion parent company guarantee" and shareholder loan from Fortum (Wikipedia mirror of Fortum's own reporting, `https://en.wikipedia.org/wiki/Fortum` and `https://en.wikipedia.org/wiki/Uniper`, retrieved 2026-07-24). This is the widely-cited European "hedging turned into a cash-liquidity crisis" case, but it is a large integrated generator/trading house, not a pure UK retail supplier, and the Wikipedia-mirrored sourcing used here describes it more precisely as "ran out of cash purchasing spot gas" than as an explicit CCP variation-margin call — the margin-call framing of the 2022 European energy crisis is very widely reported in financial press (Reuters/FT coverage of EU finance ministers discussing emergency liquidity backstops for utilities facing margin calls, September 2022) but this agent could not re-verify that specific framing via a freshly fetched primary source this session (DuckDuckGo/Bing queries were rate-limited/blocked mid-session) — **flagged as inferred-best-estimate / recalled-from-training-knowledge, not URL-verified this session**, and should be re-checked in a follow-up pass if it becomes load-bearing for a specific magnitude in the sim.
**confidence**: M overall (H for the UK-under-hedging root cause and the Uniper/Fortum liquidity-crisis facts, which are freshly fetched; L/inferred for the specific "margin call" framing/magnitude of the wider 2022 European liquidity crisis, which relies on recalled general knowledge not re-verified this session).
**source**: Ofgem `FRC_transparency_report.pdf` (2025-04, retrieved 2026-07-24); BBC News business-61353794 (2022-05-06, retrieved 2026-07-24); Wikipedia `Bulb_Energy`, `Uniper`, `Fortum` (retrieved 2026-07-24, each citing Reuters/Bloomberg/BBC primary reporting in their reference lists).
**date**: 2026-07-24
**finding**: Both failure modes are real and should be modelled as **distinct** mechanics, not conflated: (a) **under-hedged/naked exposure** — the dominant, UK-retail-evidenced 2021 failure mode, already partially covered by existing `MIN_HEDGE_FLOOR`/capital-cost-basis assumptions in `ASSUMPTIONS.md`; (b) **collateral/margin-call liquidity drain on an otherwise-hedged position** — real at the generator/major-trading-house level (Uniper/Fortum, strongly evidenced) and plausible-but-not-freshly-re-verified at the margin-call-specific framing for the wider 2022 crisis. The task's premise ("a spike triggers margin calls that can kill a supplier" as a real failure mode) is **supported**, but the strongest UK-specific evidence for the *root cause* of actual 2021-22 supplier failures is under-hedging, not margin calls on a hedged book — worth stating explicitly so the sim's death-loop mechanic isn't built as if it were THE dominant 2021 UK cause, when the dominant cause was different (and already modelled elsewhere).

---

## Modelling recommendation

A concrete, defensible default `counterparty_type` set for `ForwardContract`, given the above:

1. **`CCP_CLEARED`** (e.g. subtype `ICE_CLEAR_EUROPE`, `ECC`) — daily/intraday variation margin, initial margin at trade inception, no per-name credit-limit concept (CCP default waterfall absorbs it structurally). Grounded H (RQ1, RQ3).
2. **`BILATERAL_OTC_BANK`** — ISDA+CSA governed, credit limit anchored to a published rating band (RQ4, H), threshold/MTA per CSA, MtM-driven collateral calls.
3. **`BILATERAL_OTC_TRADER`** (energy trading houses/majors) — same mechanics as (2), distinct counterparty pool.
4. **`BILATERAL_OTC_GENERATOR`** (PPA-adjacent bespoke shapes) — same mechanics as (2), typically longer tenor/bespoke shape, near-100%-bilateral by construction (RQ2).
5. **`BROKER_INTERMEDIATED`** — pass-through label only; the real credit counterparty for exposure purposes is whichever bilateral name the broker matched the trade with (RQ1) — model as a bilateral type with a broker-arranged flag, not a fifth credit-bearing category.

**Distribution default (R10 named simplification — flag for external cross-check, not a sourced split, per RQ2 ungrounded-gap):** absent a public supplier-level disclosure, use ~50% `CCP_CLEARED` / ~50% pooled bilateral (split across bank/trader/generator sub-types, weighted toward bank+trader for standard tenors and generator for shaped/PPA volume) as the SIM default, with a small (single-digit to low-teens) active bilateral-counterparty pool per supplier-scale-bracket to reflect real ISDA-onboarding concentration (RQ2, inferred). This is explicitly an inferred-best-estimate default, not an Ofgem/CMA-sourced figure — register it as an R10 simplification in the relevant maturity-map atom when the counterparty dimension is built, with a follow-up DISCOVER task to re-attempt a Bing/alternative-search-engine pass (DuckDuckGo bot-blocked this session) for any trade-press (Montel, ICIS, Cornwall Insight) commentary that might carry a real indicative split.

**Rating-anchored credit limit (RQ3, RQ4):** legitimate for the company layer to read a published agency rating band per bilateral counterparty (wall-safe, RQ4); the *true* default probability / internal risk score must stay simulation-internal and be inferred by the company only from observed settlement/dispute history, never read directly — this is the correct wall placement for the "observation-window cap = rating-anchored prior modulated by observed settle/dispute history" design named in the task.

**Death-loop mechanic (RQ5):** model as a *distinct* failure channel from under-hedging — a margin/collateral call spike on `BILATERAL_OTC_*`/`CCP_CLEARED` positions during a wholesale price shock, separate from (and not a substitute for) the existing naked-exposure/`MIN_HEDGE_FLOOR` mechanic, since the two are evidenced as different real failure modes (RQ5) with under-hedging being the stronger UK-specific 2021 evidence and margin-call liquidity drain being the stronger continental-2022/generator-level evidence.
