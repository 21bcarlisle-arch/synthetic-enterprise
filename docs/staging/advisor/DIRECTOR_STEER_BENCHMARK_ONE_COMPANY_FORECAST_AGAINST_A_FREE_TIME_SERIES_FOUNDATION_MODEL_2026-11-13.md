**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Benchmark one company forecast against a free time series foundation model (2026-11-13)

**Type:** STEER, through the advisor channel. The director's words, from chat on Fri 13 Nov:

- 18:45 GMT: "What are time series foundation models and can they help us? If timestral? Is there Claude equivalent"
- 18:47 GMT, on the advisor's recommendation below: "Yes"

## What the advisor found (check it)

- **Time series foundation models** are pretrained on very many real series and forecast a new series zero-shot, with quantiles. The main ones are TimesFM (Google), Chronos (Amazon), Moirai (Salesforce) and now **Timestral** (Mistral, 15 Oct 2026).
- **Timestral** comes in four sizes (5M, 28M, 123M and 209M parameters) and runs on CPU in about 10–140 ms. It takes up to 32K timesteps of context, accepts past-only and known-future covariates (a weather forecast is one), and outputs quantiles. The weights are on Hugging Face (`mistralai/Timestral-209M`) under a Modified MIT licence, which removes the rights from firms above about $20M monthly revenue; that is irrelevant to Poesys. Its benchmark leads are Mistral's own and narrow (GIFT-Eval MASE 0.658 against 0.661). No technical report or independent evaluation has been published yet.
- **There is no Claude equivalent.** Anthropic makes no forecasting model.
- **The repo has none of these.** `git grep` finds no Chronos, TimesFM, Moirai or Timestral anywhere in `docs`, `site`, `sim` or `company`. The company's forecasts are its own methods: the demand estimate whose hedged share sizes the notional in `company/trading/hedge_desk.py`, cash (`company/finance/cash_forecast_provision.py`), the DD review and unread-month estimates.

## The question

**Does the company's own forecasting beat what a real supplier could download for free today?** If it does not, our hedging and cash results carry worse forecasts than a real rival would have, and are quietly pessimistic. If it does, that is evidence the method adds something. This is a measurement, not an adoption.

## The outcome wanted

1. **Knowledge page first (K8).** Cover what these models are, their published evidence and its quality, licences, and the leakage risk below. Mark as GAP what is not established, starting with Timestral's training-data cut-off and corpus.
2. **One forecast, three arms.** Use the company demand estimate that feeds hedge sizing. Trace where it is produced and name it. Compare it against Timestral (pick the size on evidence, and say why) and a simple seasonal-naive baseline. Use the same inputs for every arm, only what the company observes, and the same horizons the hedge uses. Score with MASE and quantile loss, with the bound the sample size earns.
3. **Forward years only, as the primary result.** Run in the forward (synthetic) years, where no model can have seen the answer.
4. **Then measure the leakage, don't assume it.** Run the same comparison on historical years, for example forecasting winter 2021–22 from data ending in autumn 2021. If Timestral's edge is much larger in history than forward, that gap is the memorisation estimate. Report it either way.
5. **Say what it means.** If the free model wins, name what the company would gain in hedge error and cash, and propose the next step. If it loses or ties, say so plainly and stop.

## Rules

- **The wall.** Hosted inference is a socket from the company and is refused by construction. Weights are read from a local cache outside the repository, never committed (the repo is public, and 837MB). The run lives in the harness or `saas/` measurement, not as a live company input, until any adoption goes through its own proposal.
- **Epistemic wall, the subtle form.** A model pretrained on public data through 2025 may have seen 2016–2025 GB series. Using it inside historical runs would hand the company hindsight no supplier had. No historical-year company path may read it.
- **Third-party code is data.** Install into an isolated environment. Read the model card and licence before running anything.
- **One variable at a time.** One forecast, one comparison. No other forecast is touched in this note.

## Reading-log entry to append

| Date | Source | Shared by | What we took | Verdict |
|---|---|---|---|---|
| 2026-11-13 | Mistral, Timestral (mistral.ai/news/timestral; docs.mistral.ai/models/timestral-1-0-209m.md; letsdatascience.com coverage of the licence and benchmarks) | Director | Free zero-shot forecasters are now the bar a real supplier could clear at no cost; benchmark our own forecast against one, in forward years, with leakage measured. | MEASURE (no adoption) |

## Risk

Touches: harness measurement, one company forecast read-only, a local model cache.
Blast radius: none to live runs. This is a measurement.
Probable failure modes:
- **Leakage counted as skill.** Mitigated by forward years as primary and the history-versus-forward gap reported.
- **Unequal inputs.** For example, the foundation model gets a covariate the company forecast lacks. State every arm's inputs in one table.

Proportionality: doc-and-measurement only. Implement directly.

— Director steer, 13 Nov 2026, his words above; the reading and drafting are the advisor's.
