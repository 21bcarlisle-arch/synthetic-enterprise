**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Judge the forecast benchmark by hedge cost, not error alone (2026-11-16)

**Type:** STEER, through the advisor channel. It amends `DIRECTOR_STEER_BENCHMARK_ONE_COMPANY_FORECAST_AGAINST_A_FREE_TIME_SERIES_FOUNDATION_MODEL_2026-11-13.md` before it runs. The director's words, from chat on Mon 16 Nov:

- 09:27 GMT, sharing https://arxiv.org/html/2511.13616v2 with no comment; 10:04 GMT, again: "Probably no use but interesting"
- 10:04 GMT, sharing https://github.com/jingyaogong/minimind; 10:05 GMT: "Same here ? https://github.com/karpathy/nanoGPT"
- 10:06 GMT: "There's no value in a energy gpt? Or energy JEV?"
- 10:07 GMT, on the advisor's recommendation below: "Yes"

## What the advisor found (check it)

- **The paper:** Maciejowska, Lipiecki and Uniejewski, "Statistical and economic evaluation of forecasts in electricity markets: beyond RMSE and MAE", arXiv 2511.13616v2 (revised 31 Mar 2026), *Energy Conversion and Management*.
  - **Data:** 192 day-ahead price forecasts for Germany–Luxembourg, 2016–2024, scored by the arbitrage profit of two stylised batteries.
  - **Finding:** RMSE and MAE are only weakly related to profit. Error dispersion and association measures (correlation with realised prices, timing of daily peaks and troughs) relate strongly. Two forecasts with identical RMSE (10) and MAE (9) earned €24.68 and €0.16.
  - **Limits:** one market, one simple battery, point forecasts only.
- **The 13 Nov benchmark, as staged,** scores its three arms (company estimate, Timestral, seasonal-naive) by MASE and quantile loss only. By this paper, that can choose the less valuable forecast. It has not yet run.

## The amendment

1. **Keep MASE and quantile loss, but make the deciding score economic.** For each arm, compute the hedge cost and the imbalance cost the company would have incurred had that forecast sized the hedge, through the same hedge path (`company/trading/hedge_desk.py` and what feeds it), in forward years. Keep the arms' inputs identical, as before.
2. **Add the paper's shape scores:** dispersion of errors, correlation of forecast with outturn, and timing of daily peak and trough.
3. **Report disagreement as a finding.** If error and money rank the arms differently, say so, and say which one the company should trust and why.
4. **The leakage rule is unchanged:** forward years primary, with the history-versus-forward gap reported.

## What waits on the result

**A household-representation trial (the "energy JEPA").** The idea: learn a compact description of each home from what a real supplier observes (half-hourly reads, payments, responses to price), and use it to predict who gains from a tariff, whose DD will fail, and who under-uses an EV or battery. It is a candidate for the M3/M4 method of discovering hidden household weights. It does **not** start now. If the benchmark shows a generic forecasting model beats the company's own, propose a knowledge page and a scoped trial. If not, file it as considered and parked, with the reason.

Named risks for that later trial:
- circularity when training on our own simulated households;
- real-data limits under W11. Low Carbon London is public; SERL is licensed and local only, with aggregates out;
- it must beat the existing hand-built segments on decisions and money.

## Reading-log entries to append

| Date | Source | Shared by | What we took | Verdict |
|---|---|---|---|---|
| 2026-11-16 | Maciejowska, Lipiecki & Uniejewski, arXiv 2511.13616v2 (*Energy Conversion and Management*) | Director | Error scores can pick the economically worse forecast; judge by the decision's cost and by shape. | ADOPT (amends the 13 Nov benchmark) |
| 2026-11-16 | Pavlyshyn, "Your agent doesn't need an ontology. It needs a conceptual model" (Substack, 15 Nov) | Director | Facts, processes and rules; ontology only at organisational boundaries. Our plain-language concept register already follows it. Gap: no declared supplier-side payment lifecycle. | NOTED; lifecycle test offered, not staged |
| 2026-11-16 | jingyaogong/minimind (Apache-2.0; 64M model, full training pipeline on one consumer GPU) and karpathy/nanoGPT (superseded by nanochat) | Director | Good resources for understanding how models are made; too small for any machine work. | LEARNING ONLY |

## Risk

Touches: the queued benchmark's scoring only.
Blast radius: none. It is a measurement.
Probable failure mode: **an economic score that rewards luck in a short window.** Use the full forward sample and report the bound it earns.

Proportionality: doc-and-measurement only. Implement directly.

— Director steer, 16 Nov 2026, his words above; the reading and drafting are the advisor's.
