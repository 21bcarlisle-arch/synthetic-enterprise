**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# Pre-registration: what observing only the electricity leg in the rival's ledger moves

Claim `observe-only-the-electricity-leg-in-the-rival-ledger`. Written 2026-10-01 BEFORE either arm ran.
Parent: `SEAT_FINDING_A_GAS_RENEWAL_IS_NOW_PRICED_AGAINST_THE_GAS_SVT_AND_THE_RIVAL_LEDGER_MIXES_BOTH_FUELS_2026-10-01.md`.

## The change (one variable)

`run_phase2b` feeds `_competitor_position_ledger.observe(term_start, unit_rate)` only when the
decision leg is electricity. A gas-only household's gas strike (~£30–40/MWh ex-VAT against
~£150 for electricity) no longer enters the quarter mean the rival chases.

## Correction to the item's own direction, made before the run

The item said "reference up, differential vs market UP, churn p UP". That is not consistent with
itself. The rival reference is `svt + k·min(0, position − svt)`, floored at cost, and the
differential is `(offer − reference)/reference`. Removing rates that sit below every electricity
rate RAISES the quarter mean, which raises the reference or leaves it unchanged. So the same
offer reads relatively CHEAPER. The differential falls and churn p falls. That is also what the
parent finding argues ("electricity churn is overstated"). These are the predictions I register:

- **R1** On matched electricity renewal events, `market_reference_gbp_per_mwh` rises or stays the
  same. It never falls, except on events downstream of a path divergence (a flipped departure
  changes later ledger contents). The number that rise is between 1 and all of them. I cannot
  bound it from below with confidence, because the cost floor and a `None` position both mask
  the chase.
- **R2** `price_differential_vs_market_reference` falls or stays the same on every matched
  electricity event where R1 rose, with the same divergence exception.
- **R3** Electricity `realized_churn_probability` falls on at least as many events as it rises.
  The mean falls by 0–10% relative. I expect small, because the parent measured the
  competing-risk pass-through as diluted.
- **R4** Electricity churned count moves by −3..0 and never rises by more than 1. A handful of
  rolls is evidence of little.
- **R5** Gas renewal events do not read the rival after `price-the-gas-renewal-against-the-gas-svt`.
  So they are identical except where the account's path diverged.
- **R6** `price_differential_vs_svt` is identical on every matched event, because it does not read
  the ledger.
