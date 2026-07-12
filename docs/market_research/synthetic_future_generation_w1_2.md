# W1_2_generate_futures — DISCOVER findings: mechanism vs. content boundary

**Atom:** `W1_2_generate_futures` (epoch 3, `docs/design/maturity_map.yaml`). **Status:** DISCOVER
only, per EPOCH_GATING_AND_ATOM_AUTHORSHIP.md Rule 1 — BUILD stays gated pending epoch sequencing
and `depends_on: [W1_reveal_over_time]` (W1 itself currently L2/3, loop_stage idle, blocked on the
M4 rederivation per its own registration). This atom's own prior note additionally requires that,
even once unblocked, generated scenario CONTENT is director-authored curriculum (CLAUDE.md R13),
never agent-invented.

## Internal check first: zero prior art, confirmed

Grepped the codebase for any existing synthetic-future-price generation mechanism before assuming
none exists. `sim/forward_curve.py::generate_forward_price()` exists but is a DIFFERENT thing: a
backward-looking decision-time PRICING MODEL (EWMA of real historical spot + seasonal shape + term
premium) used to price a fixed-rate tariff *during* the real 2016-2025 replay — it consumes real
history, it does not generate new ground-truth history beyond it. `evidence: []`/`file_scope: []`
on this atom's own registration is accurate — genuinely greenfield.

## Two distinct real-world traditions found, external research

1. **NESO Future Energy Scenarios (FES) — narrative/curated scenario framework.** FES presents a
   small number of NAMED, qualitatively-distinct future pathways (e.g. differing net-zero routes),
   each an independent-analyst-curated story with quantified consequences, not a stochastically
   sampled distribution of paths. **[L] NESO has moved FES off its former annual cycle — the next
   full FES publication is not due until 2028**, with interim system planning driven by separate
   strategic processes — confirms this is a deliberately-paced, human-curated artefact in the real
   world, not a cheap/automatable one.
2. **Quantitative energy-trading practice — stochastic path-generation mechanisms.** Real trading
   risk desks (per vendor/methodology sources: KYOS, Montel, QuantRisk, and the academic 3-factor
   commodity forward-curve literature) generate MANY synthetic price paths from a single CALIBRATED
   model, typically combining: mean-reversion, seasonality, jump-diffusion (captures real
   discontinuous spikes, not just smooth diffusion), regime-switching volatility (a hidden Markov
   chain toggling between calm/stressed volatility regimes, estimated via MCMC), and
   cross-commodity correlation/cointegration (electricity and gas do not move independently). This
   is a MECHANISM, agnostic to any specific narrative — the same calibrated engine can be pointed at
   different stress targets.

## Implication for this atom's own mechanism/content boundary (the actual open question)

The atom's existing registration draws the line at "the underlying mechanism/engine" (buildable,
not director-gated content) vs. "any scenario beyond that" (director's own instrument, R13). This
DISCOVER pass grounds that line in real practice rather than leaving it abstract:

- **The MECHANISM layer**, informed by the quant tradition above, is a calibratable stochastic
  generator: fit mean-reversion/seasonality/volatility-regime/jump parameters against the SIM's own
  real 2016-2025 history (the same data `sim/forward_curve.py`'s seasonal calibration and
  `calculate_sigma_recent()` already use), then sample new paths from it. This is a real, scoped,
  buildable capability — NOT itself a scenario, in the same sense a random-number generator is not
  itself a specific dice roll.
- **The CONTENT layer**, informed by the NESO tradition above, is which specific stress/target the
  mechanism is pointed at and named as ("Scenario: repeat of 2021-22 but starting from a weaker
  treasury position", "Scenario: sustained high-volatility regime, no crisis resolution") — this
  is squarely the director's call per R13, matching FES's own real-world practice of a small number
  of deliberately-authored, independently-curated named pathways rather than an arbitrary sampled
  distribution.

## Named next step (not built — mechanism sizing is a FRAME task, not decided here)

If/when `depends_on` (W1_reveal_over_time reaching its own M4-gated target) clears and the director
opens this atom's sequencing, the concrete FRAME question is: does the mechanism reuse
`sim/forward_curve.py`'s existing calibration data (`sim/data/seasonal_calibration.json`) as its
starting parameters (fastest, reuses already-validated real-world anchoring), or does it need its
own independent volatility-regime calibration (the forward-curve model has no jump-diffusion or
regime-switching term today — `calculate_sigma_recent()` is a plain recent-window stdev, not a
Markov-regime model)? Not resolved here — a genuine sizing question for the next real FRAME pass,
not decided unilaterally in this DISCOVER pass.

## Honest open items (R10)

- No specific stress scenario is proposed or implied by this document — that would be a content
  decision, explicitly out of scope for DISCOVER and reserved to the director (R13).
- NESO's own detailed price-stress-testing methodology (as opposed to FES's narrative-scenario
  framework) was not found in this pass at a level of technical detail beyond what's summarised
  above — a deeper read of NESO's own published Energy Forecasting Strategy documents would be the
  next external-research step if the director wants closer regulatory-practice anchoring before the
  mechanism is sized.
