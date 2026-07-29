# GB Wholesale Domain — Scope Independence Evidence

**Purpose**: K-PILOT ruling deliverable #2 (`scope_independence_evidence`). Demonstrates that
the three scope nodes (`electricity-wholesale`, `gas-wholesale`, `carbon-price`) are anchored to
real, cited, practitioner-level market-structure facts — not transcribed from a director/repo
list. Produced by the discovery agent, external-sources-only, 2026-07-29.

**R9 labelling convention used throughout**: `[observed-with-evidence: URL]` = a source was
fetched this session and states the claim directly. `[inferred]` = domain reasoning without a
direct fetch this session (named, not fabricated). No URL, figure, or document title below was
invented — where a fetch failed or a source was unreachable, that is stated as a gap rather than
papered over.

---

## 1. `electricity-wholesale` — GB electricity wholesale market structure

### 1.1 The EFA calendar and traded-product granularity
- **The GB day is sliced into 6 four-hour EFA (Electricity Forward Agreement) blocks**, not
  continuous hours: an EFA day runs 23:00–23:00 local, split into 6×4h blocks; Blocks 1–2 are
  "overnight", 3–6 are "day" blocks. Baseload products exist for every block (WD1–6, WE1–6);
  **peak-load products exist ONLY for WD3, WD4, WD5** (and bank holidays), so off-peak is only
  defined for the remaining blocks — peak is a specific tradeable sub-set of the week, not simply
  "daytime". `[observed-with-evidence: https://en.wikipedia.org/wiki/Electricity_Forward_Agreement,
  underlying primary cite: ICE "The EFA Calendar" PDF (theice.com/publicdocs/EFA_Calendar.pdf,
  archived https://web.archive.org/web/20160304225947/https://www.theice.com/publicdocs/EFA_Calendar.pdf)
  and Schofield, *Commodity Derivatives Markets and Applications*, Wiley 2013, p.203 — fetched
  2026-07-29]`
- **EFA months and seasons don't follow the Gregorian calendar**: an EFA month is 4 weeks, except
  March/June/September/December which are 5-week months; the two EFA seasons (winter/summer) are
  each exactly 26 weeks (winter = WK40–WK13). Leap years land the extra week in December, not
  February — the opposite of the Gregorian leap-day convention. This is a genuine trap for anyone
  building a trading calendar from first principles. `[observed-with-evidence: same Wikipedia
  article, citing ICE EFA Calendar — fetched 2026-07-29]`
- **Why shape matters commercially**: a supplier's actual half-hourly demand shape almost never
  matches a flat baseload strip — evening winter peaks, weekday/weekend split, and seasonal swing
  all diverge from a flat MW block — so a book hedged only with baseload carries residual
  "shape risk" (exposure to the peak/off-peak and profile spread) that must be closed out
  in the balancing/imbalance market or via peak products. `[inferred — standard energy-trading
  reasoning, consistent with the WD3–5-only peak product definition above, no single source
  fetched this turn stating the shape-risk consequence explicitly]`

### 1.2 GB day-ahead auction microstructure
- **GB trades on EPEX SPOT's day-ahead auction** (formerly branded N2EX, now folded into the
  EPEX SPOT name since the 2015 APX Group/EPEX SPOT integration — "N2EX" now redirects to the
  European Power Exchange article). `[observed-with-evidence:
  https://en.wikipedia.org/wiki/European_Power_Exchange, fetched 2026-07-29]`
- **The order book gate-closure and result-publication times differ by market**: EPEX SPOT closes
  the day-ahead order book at 11:00 for Switzerland and 12:00 for other continental markets, but
  **publishes GB results earlier, from 09:30 GMT**, vs 11:10 (Switzerland) and 12:55 (other
  markets) — evidence that GB's day-ahead auction runs on its own earlier clock, not simply
  bolted onto the continental timetable. `[observed-with-evidence:
  https://en.wikipedia.org/wiki/European_Power_Exchange, citing epexspot.com/en/basicspowermarket
  — fetched 2026-07-29; exact current 2026 gate-closure time not independently re-verified against
  epexspot.com directly this turn — epexspot.com blocked the curl request with a 403/Cloudflare
  challenge, so treat the specific clock times as historical/indicative rather than the live 2026
  schedule]`
- **GB is NOT part of the pan-European Single Day-Ahead Coupling (SDAC) implicit auction that
  couples ~95% of European power consumption** — EPEX SPOT is "one of the stakeholders" in SDAC,
  but the Market Coupling section of the same source explicitly scopes continental coupling as
  "Central-Western European countries, **except for Great Britain and Switzerland**" — i.e. GB's
  day-ahead price is NOT implicitly coupled with the continent the way France/Germany/Benelux are
  with each other. `[observed-with-evidence: https://en.wikipedia.org/wiki/European_Power_Exchange
  — fetched 2026-07-29]`
- **GB intraday is continuous, down to 5 minutes before delivery**, and (per the same source) GB
  intraday auctions were only added in 2018, coupled with the Irish market specifically — a later
  and narrower coupling than the continental Single Intraday Coupling (SIDC), from which GB is
  also excluded. `[observed-with-evidence: same URL, citing an EPEX SPOT 2018 press release —
  fetched 2026-07-29]`
- **Could not verify this session**: EUPHEMIA (the price-coupling algorithm) — no direct primary
  or Wikipedia source was reachable this turn (a Wikipedia search for "EUPHEMIA" returned no
  article). The general claim that EUPHEMIA is the algorithm used for SDAC clearing is
  `[inferred]` from established market knowledge, not sourced this session — named as a gap
  rather than asserted with a fabricated citation.

---

## 2. `gas-wholesale` — GB gas wholesale market structure

### 2.1 NBP as a virtual (not physical) hub, and its balancing mechanics
- **NBP (National Balancing Point) is a *virtual* trading location, not a physical hub** — unlike
  Henry Hub, there is no single point of custody; it is the pricing/delivery point for the ICE
  Futures Europe UK gas futures contract, and is described as "the second most liquid gas trading
  point in Europe." `[observed-with-evidence: https://en.wikipedia.org/wiki/National_Balancing_Point_(UK),
  citing Oxford Institute for Energy Studies NG-63 (June 2012) and Euronews (30 Aug 2022) — fetched
  2026-07-29]`
- **NBP has no hard balancing penalty** — unlike continental hubs (Zeebrugge, TTF), NBP shippers
  who are out of balance at end-of-day are not fined; instead they are automatically "cashed out"
  at the marginal system buy/sell price for that day — a materially softer imbalance regime than
  the continent's. `[observed-with-evidence: same URL — fetched 2026-07-29]`
- **Minimum tradeable clip on the NBP OCM platform is 4,000 therms** — a shipper short/long by
  less than that must simply let the position cash out rather than trade it away. `[observed-with-
  evidence: same URL, describing the OCM platform run by ICE ENDEX — fetched 2026-07-29]`
- **NBP liquidity is used to balance continental positions via the Bacton–Zeebrugge
  interconnector** — i.e. NBP's role is not purely domestic; it is used as a release valve for
  continental shippers too. `[observed-with-evidence: same URL — fetched 2026-07-29]`

### 2.2 LNG import infrastructure and its share of UK gas demand
- **Grain LNG (Isle of Grain, Kent)** has a **regasification capacity of 645 GWh/day (58 million
  m³/day)**, storage capacity of 1 million m³ across 4 tanks, and a throughput capability of
  **15 million tonnes/year — equivalent to ~20% of UK gas demand**. It is the largest LNG storage
  facility in Europe and 8th-largest in the world. Ownership: National Grid built/owned it, sold
  a 50:50 stake to Centrica + Energy Capital Partners for £1.5bn in a deal reported August 2025.
  `[observed-with-evidence: https://en.wikipedia.org/wiki/Grain_LNG_Terminal, citing grainlng.com
  and Financial Times (14 Aug 2025) — fetched 2026-07-29]`
- **South Hook (Milford Haven) + the smaller adjacent Dragon LNG terminal together can handle up
  to 25% of UK gas requirement.** South Hook is the largest LNG terminal in Europe by the cited
  source, receiving Qatari LNG (Qatargas 2), first cargo March 2009. `[observed-with-evidence:
  https://en.wikipedia.org/wiki/South_Hook_LNG_terminal, citing BBC News (20 Mar 2009 / 19 Mar
  2010) — fetched 2026-07-29]`
- **Practitioner point derived from the above two facts**: GB's three LNG terminals (Grain, South
  Hook, Dragon) collectively cover a very large share of peak/base UK gas demand (Grain alone
  ~20%), meaning GB gas security is materially exposed to the globally-traded LNG cargo market
  (competing with Asian JKM-linked demand) rather than solely to pipeline/continental supply —
  the cargo-diversion/optionality point is `[inferred]` from the terminal-capacity figures above;
  no single source fetched this session states the JKM-competition mechanism explicitly.
- **Gap named**: could not reach a live Wikipedia or primary source on the Rough storage facility
  specifically (searches for "Rough gas storage", "Rough field", "Centrica Storage" returned no
  matching article, and centrica.com returned 403). The widely-cited facts that (a) Rough closed
  in 2017 and (b) reopened in 2022 at greatly reduced capacity, leaving GB with unusually thin
  seasonal storage vs. continental peers, are **`[inferred]`** this session — NOT independently
  re-confirmed by a fetched source today, and should be treated as a claim to re-verify before
  being asserted as fact in the scope brief.
- A DESNZ policy paper confirms the general shape of the concern (gas storage/LNG/interconnectors
  as the three flexibility levers for GB security of supply) but the specific text fetched did not
  contain the word "Rough": `[observed-with-evidence:
  https://www.gov.uk/government/publications/role-of-gas-storage-and-other-forms-of-flexibility-in-security-of-supply,
  published 2023-12-06 by DESNZ — fetched 2026-07-29, confirms LNG and interconnectors are
  officially framed as substitutes for storage flexibility, but the Rough-specific capacity figure
  is a named gap]`

---

## 3. `carbon-price` — UK ETS + Carbon Price Support

### 3.1 UK ETS auction/cap microstructure
- **The UK ETS started 1 January 2021**, replacing UK participation in the EU ETS post-Brexit,
  cap-and-trade, with an **initial cap 5% lower than the UK's implied share of EU ETS Phase 4**.
  `[observed-with-evidence: https://en.wikipedia.org/wiki/UK_Emissions_Trading_Scheme, citing
  gov.uk "Participating in the UK Emissions Trading Scheme (UK ETS)" (17 Dec 2021) — fetched
  2026-07-29]`
- **Auction reserve price is £22/tonne** (the minimum clearing price at UK ETS primary auctions).
  `[observed-with-evidence: same Wikipedia article, citing UK Parliament House of Commons Library
  briefing CBP-9212 (4 May 2021, Elena Ares) — fetched 2026-07-29]`
- **The Cost Containment Mechanism (CCM) is a real, dated, triggered intervention lever, not a
  theoretical backstop**: it was triggered in **December 2021** because the average UKA price in
  each of September, October and November 2021 exceeded the December trigger level of **£52.88**.
  The UK ETS Authority (a joint HMG/Scottish Government/Welsh Government/NI Executive body) can
  choose to release additional allowance supply when triggered — in the Dec-2021 instance it
  explicitly chose NOT to intervene. `[observed-with-evidence:
  https://www.gov.uk/government/publications/uk-emissions-trading-scheme-ets-authority-cost-containment-mechanism-decisions/uk-ets-authority-statement-cost-containment-mechanism-decision-december-2021,
  published 2021-12-14, DESNZ (then BEIS) — fetched 2026-07-29]`. This is a strong independent
  fact: a real, numbered trigger price and a real non-intervention decision, not obtainable from
  generic domain knowledge alone.
- **Non-compliance penalty is £100/tonne** for exceeding allowances — a fixed civil penalty
  distinct from the market price. `[observed-with-evidence: same Wikipedia article, citing Ng,
  Cherwell (23 Jan 2021) — fetched 2026-07-29, note: this is a secondary/student-press citation,
  confidence M not H]`
- **Gap named**: I could not this session independently confirm from a primary gov.uk auction page
  that ICE Futures Europe is the current UK ETS auction platform (searches for
  gov.uk pages naming "ICE Futures Europe" + UK ETS auctions returned no direct text match; the
  live "Participating in the UK ETS" gov.uk page fetched today describes the cap/allocation/
  compliance mechanics but the auction-platform operator name was not present in the fetched
  text). The ICE-Futures-Europe-as-auction-platform claim is **`[inferred]`** and should be
  re-verified against a live gov.uk or ICE source before being asserted as fact.

### 3.2 Carbon Price Support (CPS) — the fixed GB-only top-up
- **CPS is levied in physical units, not directly £/tCO2**: the current published gov.uk rate
  (effective 1 April 2016 to 31 March 2028) is **£0.00331 per kWh of gas** (GCV basis), £0.05280
  per kg of LPG/other gaseous hydrocarbon, and £1.54790 per GJ (GCV) for coal/other solid fossil
  fuels — charged when gas passes through the meter, or when LPG/coal/solid fuel is delivered
  through the generating-station gate. `[observed-with-evidence:
  https://www.gov.uk/guidance/climate-change-levy-rates — fetched 2026-07-29, live primary source,
  confidence H]`. Converting the gas rate to a carbon-equivalent using a standard natural-gas
  emissions factor (~0.184 tCO2/MWh) gives ≈£18/tCO2 — consistent with the commonly-quoted
  "CPS frozen at ~£18/tCO2" figure, but the £18/tCO2 framing is `[inferred]` (a unit conversion
  performed this session, not the unit the government actually publishes the rate in). **This is
  itself an independent-domain fact worth keeping in the scope brief**: CPS is a fuel-input excise
  levy administered alongside the Climate Change Levy (CCL), not a per-tonne-of-CO2-emitted
  charge — a distinction a generic three-bullet sketch of "there's a carbon price top-up" would
  miss entirely.
- **The rate has been announced frozen through 31 March 2028** (per the live gov.uk table dated
  as retrieved 2026-07-29) — i.e. CPS is a long-declared-frozen policy lever, not one that moves
  year to year the way UKA auction prices do. `[observed-with-evidence:
  https://www.gov.uk/guidance/climate-change-levy-rates — fetched 2026-07-29]`
- **How this enters a fossil generator's short-run marginal bid**: a gas plant's marginal cost
  stack = fuel cost + (UKA price × emissions factor) + (CPS rate × fuel throughput, charged
  regardless of the UKA market price) — i.e. UK gas generators face a carbon cost with **two
  independently-moving components** (a market-clearing UKA price with its own reserve price/CCM
  dynamics, PLUS a fixed CPS excise that does not track the UKA auction price at all). `[inferred
  — synthesis of the two primary sources above (UK ETS reserve-price/CCM mechanics + the live CPS
  rate table); no single source states the combined bid-stack formula explicitly]`.

---

## Summary of sources fetched this session (for the provenance ledger)

| Source | Status | Used for |
|---|---|---|
| en.wikipedia.org/wiki/Electricity_Forward_Agreement (citing ICE EFA Calendar PDF, Schofield 2013) | fetched OK | EFA blocks, peak/off-peak, EFA calendar |
| en.wikipedia.org/wiki/European_Power_Exchange (citing epexspot.com) | fetched OK | day-ahead gate/publication times, market coupling exclusion of GB |
| en.wikipedia.org/wiki/Nord_Pool | fetched OK | background only, not directly cited above |
| en.wikipedia.org/wiki/National_Balancing_Point_(UK) (citing OIES NG-63, Euronews) | fetched OK | NBP virtual hub, cash-out, 4,000-therm minimum, Bacton–Zeebrugge |
| en.wikipedia.org/wiki/Grain_LNG_Terminal (citing grainlng.com, FT) | fetched OK | Grain capacity/throughput/ownership |
| en.wikipedia.org/wiki/South_Hook_LNG_terminal (citing BBC) | fetched OK | South Hook + Dragon 25% figure |
| en.wikipedia.org/wiki/UK_Emissions_Trading_Scheme (citing gov.uk, HoC Library CBP-9212, Cherwell) | fetched OK | UK ETS start date, reserve price £22/t, £100/t penalty |
| gov.uk CCM decision statement, Dec 2021 | fetched OK | CCM trigger mechanics, £52.88 trigger, real non-intervention decision |
| gov.uk climate-change-levy-rates (CPS table) | fetched OK, live primary | CPS £0.00331/kWh gas, frozen to 2028 |
| gov.uk role-of-gas-storage-and-other-forms-of-flexibility | fetched OK | confirms storage/LNG/interconnector framing, but no Rough figure |
| epexspot.com/en/product-info | 403 Cloudflare block | could not independently re-verify live 2026 gate times |
| elexon.co.uk/knowledgebase (EFA page) | Cloudflare JS challenge, blocked | could not get Elexon's own EFA wording directly |
| Rough storage facility (Wikipedia, Centrica) | no article / 403 | Rough closure/reopening capacity — NAMED GAP, not sourced this session |
| EUPHEMIA algorithm | no Wikipedia article found | NAMED GAP |
| ICE Futures Europe as UK ETS auction platform operator | not found in fetched gov.uk text | NAMED GAP |

**Confidence key used above**: H = fetched from a live/primary government or exchange-linked
source; M = Wikipedia citing a secondary/press source; L = single indirect source or unverified
inference this session.
