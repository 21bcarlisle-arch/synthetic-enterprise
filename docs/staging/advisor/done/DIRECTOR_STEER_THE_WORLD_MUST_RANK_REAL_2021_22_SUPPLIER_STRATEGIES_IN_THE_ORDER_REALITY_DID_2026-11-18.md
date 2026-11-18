**Severity:** LATENT · **Lane:** W3_industry_systems · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] The world must rank real 2021–22 supplier strategies in the order reality did (2026-11-18)

**Type:** STEER, through the advisor channel. The director's words, from chat on Wed 18 Nov:

- 05:38 GMT, sharing https://linas.substack.com/p/nubank-ai-agents-simulated-customers with no comment.
- 05:41 GMT, sharing a transcript of the Nubank and Snowglobe conference talk, "simulation maxxing", with no comment.
- 05:57 GMT, on the advisor's recommendation below: "Yes"

## What the advisor found (check it)

- **The sources.**
  - Linas Beliūnas (17 Nov) on Nubank's paper "Screen Before You Serve": candidate support agents talk to thousands of simulated customers, and an LLM judge scores them. Only versions that beat the incumbent go to live A/B tests. Reported results: release cycle 21.2 → 4.4 days; self-service +4.9 points; tNPS +36.7.
  - The talk, by Snowglobe's CEO and a Nubank engineer, adds that sim and real eval scores correlated "pretty high" (no figure given) and that 80% of expert labels found simulated data usable. Their words: the gains count only once you "close out the sim-to-real gap".
  - Both are vendor-adjacent, and parts are paywalled.
- **The line that matters:** "A simulator earns its keep by ranking agent versions correctly, not by sounding like real customers." Their simpler frontier-model simulator "ranked the best version of the agent last."
- **Our world is checked mostly for sounding right.** `sim/scenario/fidelity_check.py` tests generated returns against a block bootstrap of the real 2016–2025 record on mean, volatility, lag-1 autocorrelation, tail heaviness, tail direction and volatility clustering. It has been hardened by red teams several times. `tests/test_coupled_triad_gate.py` checks that the world *can* defeat the company. **Nothing checks that the world ranks strategies in the order reality ranked them.** A world can match every moment and still reward the wrong strategy.
- **We have no live customers, but we have real outcomes.** In 2021–22 a large number of GB suppliers exited (about 30; establish the count) while others survived. The causes are documented in public reviews. Candidates to find and read:
  - Ofgem's own reviews of the supplier failures and its SoLR decisions;
  - Oxera's review for Ofgem of its supply market regulation;
  - the NAO report on the energy supplier market (2022);
  - the BEIS Select Committee report on energy pricing (2022).

  Commonly named causes: unhedged or short-hedged positions; fixed tariffs sold below forward cost; thin capital; customer credit balances used as working capital; the price cap's lag. That is our sim-to-real check.

## The question

**Run through our world's real 2021–22, do stylised versions of real supplier strategies fail and survive in the order they did in reality?**

## The outcome wanted

1. **Knowledge page first (K8).** From the published reviews, set out which kinds of strategy failed and which survived, and why, with figures where published: hedging cover, capital, tariff mix, credit-balance reliance. Write GAP where unpublished. Name no private individual. Firms are named only as the published reviews name them.
2. **Four to six stylised strategies,** each defined only from that page's evidence, for example:
   - unhedged with cheap fixes;
   - partly hedged on a thin capital base;
   - well hedged and capitalised;
   - credit balances used as working capital;
   - variable-only.

   Every parameter traces to the page or is marked GAP; none is picked.
3. **Pre-register the real ordering,** and the predicted world ordering, before any run.
4. **Run each strategy through 2021–22 in the world,** as a harness instrument, not as the company. Report:
   - survival or failure, and when;
   - the cash and liquidity path;
   - the binding cause of failure.

   Compare the world's ranking with reality's, and say what bound a handful of strategies earns.
5. **Treat a wrong ranking as the most important finding the world can produce.** If the world spares a strategy reality killed, or kills one reality spared, diagnose why: weather, prices, hedging mechanics, the cap, collections or credit balances. Fix it for fidelity reasons only, blind to company results (R13). Re-run.
6. **If it ranks correctly, keep it as a standing check.** Re-run it when the world changes materially, beside the moment checks, so a fidelity change that breaks the ranking is caught.

## Rules

- **The baseline/curriculum split and R13.** This is fidelity, decided blind to company results. The stylised strategies are instruments; the company never sees them or their results.
- **Truth stays an instrument (W7).** This measures the world; it does not train or tune the company.
- **No number picked.** A strategy parameter with no published source is GAP, and a strategy with too many GAPs is dropped, with the reason.
- **Erring against our own thesis is the safe direction (F11).** If the ranking is ambiguous, report it as not established.

## Reading-log entries to append

| Date | Source | Shared by | What we took | Verdict |
|---|---|---|---|---|
| 2026-11-18 | Linas Beliūnas, "Nubank AI agents and simulated customers" (17 Nov), on Nubank's "Screen Before You Serve" | Director | A simulator is judged by ranking candidates correctly, not by sounding real. Our fidelity checks are moment-matching; none checks ranking. | ADOPT: ranking-validity test |
| 2026-11-18 | Snowglobe and Nubank conference talk, "simulation maxxing" (transcript) | Director | Persona grounding stays consistent across tool calls (ours already does). Sim-to-real must be closed before sim results are trusted. Ours can be closed against 2021–22 outcomes. | SUPPORTS the above |

## Risk

Touches: one knowledge page, a harness instrument running stylised strategies through the world, and possibly world fidelity fixes.
Blast radius: none to the company. Fidelity fixes re-baseline every run and are stated.
Probable failure modes:
- **Strategies tuned until the ranking comes out right.** Mitigated by parameters from the page only, and the ordering pre-registered.
- **A correct ranking for the wrong reason.** Report the binding cause of each failure and compare it with the published cause.

Proportionality: fidelity instrument. Knowledge page first, then implement.

— Director steer, 18 Nov 2026, his words above; the reading and drafting are the advisor's.

## Done

*Delivery seat, 18 Nov 2026, the morning of his "Yes". Steps 1 and 2 are landed; steps 3–6 are handed on as
continuation `world-ranks-real-2021-22-supplier-strategies`, and this file moves to done so the rung-zero draw stops
re-offering a steer whose next piece is already in the queue.*

1. **Knowledge page (K8):** `docs/market_research/why_gb_suppliers_failed_or_survived_2021_22.md`, feeding
   `suppliers-accounts-and-capital`. Read in full text: Oxera's May 2022 review for Ofgem and the NAO's June 2022
   report. Not read, and marked GAP: the BEIS Committee report (parliament.uk refuses automated fetches), Ofgem's SoLR
   decision pages and its 2022 resilience consultations (404 at the addresses tried).
   - **What reality supports is a two-tier ranking, not a full order.** Oxera: "none of these individual factors alone
     predict failure"; all failed firms had negative equity; at least four failed suppliers were well hedged (over 50%
     at nine months or more: Together, PFP, Simplicity, Orbit). Failures bunch in Sep–Oct 2021 whatever the hedge, from
     0% to 91%. So a strict order of five strategies would test a precision reality does not have.
   - **Corrected beside the claim:** the "22 of 26" hedging figure in `company_treasury_risk.md` has no source here.
     The NAO's count is 17 of 24 administrators' reports (71%), and 18 of 24 (75%) cite the price cap.
2. **Strategies, defined from the page only:** four failure strategies (S1–S4) take their hedge and credit-balance
   parameters from Oxera's Tables 3.3 and A6.1. The equity level and fixed-tariff share are GAP for all four (only the
   sign is published). **S5, the only survivor strategy, is all GAP in the sources read and is not yet defined.**
   Variable-only is dropped, because no published firm ran it. Without S5 the test can only check that the world kills
   S1–S4, and a world that kills everyone would pass. That is the test's binding gap, named before any run.
3. **Reading log:** two rows appended under "Testing and controls"; `site/data/reading_log.json` regenerated.
4. **Not yet done (continuation):** source S5 from survivors' published FY2020 accounts and Ofgem's 2022 resilience
   material, or record it unsourceable; discover whether the world can run a stylised supplier's cash path outside the
   company; pre-register the real two-tier ordering and the predicted world ordering; then run.

Decision: fidelity yes
