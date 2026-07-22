> **FOLDED — in_progress (2026-07-22, autonomous worker).** These sourced anchors are folded into
> `docs/design/WHOLESALE_VALUE_CHAIN_FRAME.md` §3.1/§3.2/§3.4/§8.5, tagged `[advisor-sourced — verify vs
> primary at BUILD]` per R9 (candidates, not inherited facts). Honest gaps in §D remain BUILD
> discovery-agent work; the incoming board blind-spec is the third leg to reconcile. Parked alongside the
> steer it companions.

# ADVISOR DISCOVERY — Wholesale product & shaped-cost anchors (companion to WHOLESALE_VALUE_CHAIN steer, 2026-07-22)

**Type:** [EVIDENCE] — advisor web research, sourced. **Candidates to verify against primary documents, not facts to inherit** (R9). Fold into the WHOLESALE_VALUE_CHAIN DISCOVER; where your reading of the primary sources differs, yours wins with citation.

## A. Product conventions (documented)

- **Seasons:** Winter = Oct–Mar, Summer = Apr–Sep (Platts European Electricity methodology; legacy EFA seasons WK40–13 / WK14–39).
- **Baseload** = continuous 23:00–23:00 delivery, equal each hour (ICE UK Base Future spec: 23:00–22:59 LLT Mon–Sun). **Peak** = 07:00–19:00 London time, weekdays (EFA blocks 3–5). Off-peak = blocks 1,2,6 WD + all weekend. EFA day = six 4-hour blocks from 23:00; Gregorian calendar for new contracts since Oct-2014, EFA legacy still used.
- **The ladder that actually trades:** ICE lists consecutive months (up to 156), quarters, seasons, calendars — strips registrable across any consecutive run. So the SIM's product set should be: seasonal base + peak, quarters, months, day-ahead — with months/quarters/seasons rollable into strips.
- **Venues by horizon:** forwards/futures years out (ICE + bilateral OTC) → **day-ahead single-price auctions (N2EX/EPEX; the most-quoted GB price signal)** → continuous intraday to gate closure T-1h → balancing at the **single imbalance price** (SSP=SBP — which our settlement record already shows correctly).

## B. The shaped-cost benchmark — the cap's own construction (the public anchor)

- Ofgem's cap wholesale allowance currently uses a **3-month observation window, 1.5-month notice lag, 12-month forward view** (quarterly cap periods; pre-2022 it was 6-2-12 with semi-annual periods). This IS a published "annualised shaped cost" construction to anchor against — and its historical methodology changes are themselves fidelity events.
- Ofgem's own MHHS technical paper shows **demand shaped from peak and baseload contracts to a half-hourly profile** — literally the director's construct, diagrammed by the regulator. Note their stated simplification: the cap index assumes suppliers buy only **quarterly** products, while real suppliers trade seasonal + quarterly — the SIM should model the *real* behaviour and can score the cap-index as a benchmark belief.
- **Additional allowances that must exist in the cost stack** (set as fixed % uplifts in 2019, under review since): shaping, imbalance, transaction costs; +1% additional risk allowance; and an **ex-ante backwardation allowance** — constructed by comparing the index-approach cost vs a nominal supplier buying only in-season. That is a real, *dynamic* contango/backwardation mechanism with a published construction — the answer to "largely static view of contango vs backwardation."
- Precedent for regime stress: the £61/customer volatility adjustment (2022). And supplier evidence on record (Octopus response): **bid-ask spreads for base and peak are non-linear in volatility** — an anchor for spread/transaction-cost modelling.

## C. Hedging behaviour (documented direction, verify depth)

Suppliers hedge anticipated load **long, in layered strips across horizons**, replicating the desired supply profile; generators short their output. Fixed tariffs lock the shaped forward cost at acquisition; default/SVT reprices cap-index-like. The cover-fan-by-horizon is therefore the natural instrument of the hedge program, and the value-add ledger = achieved shaped cost vs the benchmark.

## D. What the advisor could NOT establish openly (honest gaps for your DISCOVER)

Actual supplier hedge ladders (proprietary — infer bounds from cap methodology + published strategy statements); historical seasonal/quarter forward *marks* (commercial: ICIS/Argus/Platts — check what Ofgem publishes in cap annexes as free proxies); day-ahead N2EX history access terms.

**A parallel blind anchor is being commissioned:** the board (uncontaminated by build state) will specify what a competent GB supplier's trading function comprises. Reconcile all three — board expectation, this documentary evidence, your primary-source DISCOVER — and treat disagreements as findings.

— Advisor, sourced research, 2026-07-22. Sources: Platts European Electricity methodology; ICE UK Base Future spec; Ofgem cap wholesale-methodology decisions (2022) and MHHS technical paper (2026); Ofgem additional-wholesale-allowances CfI; Octopus consultation response; EFA calendar references.
