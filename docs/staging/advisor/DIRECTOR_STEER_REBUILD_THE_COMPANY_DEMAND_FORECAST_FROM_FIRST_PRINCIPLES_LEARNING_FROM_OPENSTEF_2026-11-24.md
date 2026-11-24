**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Rebuild the company's demand forecast from first principles, learning from OpenSTEF (2026-11-24)

**Type:** STEER, through the advisor channel. It extends the queued forecast benchmark:
- `DIRECTOR_STEER_BENCHMARK_ONE_COMPANY_FORECAST_AGAINST_A_FREE_TIME_SERIES_FOUNDATION_MODEL_2026-11-13.md`;
- as amended by `DIRECTOR_STEER_JUDGE_THE_FORECAST_BENCHMARK_BY_HEDGE_COST_NOT_ERROR_ALONE_2026-11-16.md`.

The director's words, from chat on Tue 24 Nov:

- 05:11 GMT, sharing https://github.com/OpenSTEF/openstef with no comment.
- 05:23 GMT, on the advisor's suggestion to add OpenSTEF as a benchmark arm: "I'm more interested in replicating it's techniques from first principles than just using it"
- 05:24 GMT, on the advisor's recommendation below: "Yes"

His preference matches his Predbat ruling (10 Nov): learn and be inspired, build our own, don't copy. For M4, the forecasting method should be the company's own.

## What the advisor found (check it)

**The source.** OpenSTEF (LF Energy; MPL-2.0; 169 stars, about 3,100 commits). It is "a model-agnostic Python framework for creating short-term forecasts in the energy sector":
- gradient-boosted models (XGBoost, LightGBM);
- Chronos-2 support;
- probabilistic outputs;
- a backtesting and evaluation package (`openstef-beam`).

The advisor believes it originated at Alliander, the Dutch DSO; the page did not confirm this. The advisor read only the repository page, not the full README or code.

**Techniques the advisor understands OpenSTEF to use.** Verify each from its documentation and code; treat this list as a starting point, not a source.
1. **Lag features:** demand at the same half-hour 1 day and 7 days earlier, plus rolling means.
2. **Weather features done properly:** temperature for heating, solar radiation for PV, and wind converted through a power curve rather than raw speed.
3. **Calendar features:** weekday, bank holidays, clock changes, school holidays.
4. **Quantile (probabilistic) forecasts:** a band per half-hour. Hedge sizing needs the band, not only the centre.
5. **Splitting net demand into components:** base load, solar and wind separated from a measured total. For us this is households with PV, batteries and EVs (the 10 Nov range steer), whose net import is load minus generation.
6. **Input validation before training:** stuck ("flatliner") readings, outliers and gaps. For a supplier, a stuck meter is a real observable.

## The outcome wanted

1. **Knowledge page first (K8): short-term demand forecasting for a supplier, from first principles.** For each technique, cover:
   - what it does and why it works;
   - the published evidence (OpenSTEF's documentation and papers, plus the wider literature: GEFCom, the load-forecasting surveys);
   - **what our company can legitimately observe to feed it**: its own customers' metered or settled demand as a real supplier receives it, with its real lags; published weather *forecasts*; calendars; customer asset data it holds;
   - what is GAP.

   OpenSTEF's code is **reference reading only**. We write our own; nothing is copied into the repository (MPL-2.0 is file-level copyleft, and the repo is public).
2. **Rebuild the company's demand forecaster one technique at a time,** in this order unless the page argues otherwise:
   1. lags;
   2. calendar;
   3. weather;
   4. quantiles;
   5. the net-demand component split;
   6. input validation, alongside whichever step first needs it.

   **Each step is an arm in the queued benchmark** and earns its place only by lowering hedge and imbalance cost in forward years (16 Nov amendment). MASE, quantile loss and the shape scores are reported beside it. A step that does not lower cost is recorded and reverted, with the reason.
3. **The existing arms stay as outside yardsticks:** Timestral and the seasonal-naive baseline. Report the rebuilt forecaster against both at each step.

## Rules

- **The epistemic wall, and the backtest trap.** Weather inputs are the forecast as published at the time of the decision, never the outturn that followed. Using outturn weather is the commonest way forecasting backtests flatter themselves, and here it would breach the wall. Demand lags use only data a supplier would hold by then; settlement and meter-read delays are real. Prove both with a test that fails if outturn weather or not-yet-available demand reaches the forecaster.
- **Forward years primary;** historical years reported with the leakage caveat (13 Nov).
- **K8 and the REUSE rule.** Knowledge page before code; a REUSE block naming what the index returned.
- **Fidelity-neutral world.** This changes the company's method, never the world.

## Reading-log entries to append

| Date | Source | Shared by | What we took | Verdict |
|---|---|---|---|---|
| 2026-11-24 | OpenSTEF (LF Energy, MPL-2.0): open short-term energy forecasting framework | Director | Learn its techniques from first principles and build our own: lags, calendar, weather, quantiles, net-demand split, input validation. Each step earns its place by hedge cost. | ADAPT (rebuild, don't use) |
| 2026-11-24 | Anthropic, "Introducing Claude Ship" (23 Nov): Code Review, PR Steward, Claude Approvals; Team and Enterprise only | Director | Not available on Max, and PR-based. Confirms approval rules read from the base, observe-first gates, "how to reverse it" on every fix, and a fixer that never approves. | CONFIRMS DIRECTION |
| 2026-11-24 | Claude Code Code Mode docs (shared again; page not fetchable from the advisor's session) | Director | No evidence of headless (`-p`) support yet. Backlog item E-cm stands, re-checked each Friday. | NO CHANGE |
| 2026-11-22 | A friend's system-dynamics model, "UK electricity supplier – essence" (9 stocks; behaviour constants are assumptions on sliders) | Director | Reviewed and diagrammed for the director; not taken forward, by his decision. | NOT TAKEN FORWARD |

## Risk

Touches: one knowledge page; the company's demand forecaster, step by step; the queued benchmark's arms.
Blast radius: hedge sizing, once a step is adopted. Each step is measured by hedge cost and reversible.
Probable failure modes:
- **Weather or demand leakage** flattering the rebuilt forecaster. Mitigated by the published-forecast rule and a failing test.
- **Complexity that does not pay.** Each step must lower cost, or it is reverted.

Proportionality: company capability. Knowledge page first, then implement step by step.

— Director steer, 24 Nov 2026, his words above; the reading and drafting are the advisor's.
