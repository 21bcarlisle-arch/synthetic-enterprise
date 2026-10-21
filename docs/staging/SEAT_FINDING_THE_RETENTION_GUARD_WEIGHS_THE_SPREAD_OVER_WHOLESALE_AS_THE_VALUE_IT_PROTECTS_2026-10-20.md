**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 4 · **Atom:** `C29_decisions_stop_being_lookup_tables`

# The retention guard weighs the spread over wholesale as the value it protects

**Found by** the delivery seat on 20 Oct 2026. It turned up while giving C34 a margin net of
pass-through costs (`next_best_action_and_cross_sell.md` §6.1, amended 2026-10-20).

## The defect

`simulation/run_phase2b.py` sets
`expected_margin = (unit_rate − company_fwd) × eac_for_ret / 1000` and hands it to
`retention_value_protected`. That value is weighed against the discount's cost, `ret_cost`, and is
also passed to the holdout as `term_margin_gbp`.
- `unit_rate` is the all-in strike, and `company_fwd` is the wholesale forward. The difference still
  carries capital and the term's locked policy and network costs.
- At real inputs the spread reads GBP 190–360 a year on a 3.1 MWh electricity leg, from 2016 to 2024.
  The term's own contribution is about −GBP 49 a year where nothing moved the strike: GBP 2/MWh on
  3.1 MWh, less GBP 55 cost to serve.
- So the guard overstates what retention protects by the pass-through costs. On the default policy
  it offers discounts the company's own cost stack would refuse.

This is the same defect C34's caller carried. Here it is live on every run.

## Why it is not repaired with C34's

It is the default policy. Repairing it moves every run's retention offers, the holdout's decided
cuts and every value-arm digest. It needs its own pre-registered run, not a rider on a switch that
defaults off.

## What would discharge it

The guard reads `term_contribution_per_month` (`company/interfaces/renewal_advice.py`) × 12,
or the same quantity through one shared function. The standing-charge GAP stated in §6.1 goes with
it. The count of retention offers and the retained-margin result are predicted before the run.

## Repaired, 2026-10-20; the run's grade is owed

- **The guard reads the contribution.** `expected_margin` is `term_contribution_per_year`, the one
  function C34 reads per month. The missed-retention log writes the same value.
  `counterfactual_retention` counts a `None` margin as unpriced and never sums it as zero, although
  no renewal route writes a fixed term without its locked costs today.
- **The off book will move.** Before any run, `/var/tmp/se-ret-margin/reconstruct.py` rebuilt the
  92 offers on the 19 Oct book. The median value goes from GBP 290 a year to −GBP 31, and about 11
  of the 92 would still be offered. The prediction is filed at
  `records/SEAT_PREREG_THE_RETENTION_GUARD_ON_THE_TERMS_CONTRIBUTION_2026-10-20.md`.
- **Still owed:** the full-window default-policy run graded against that file. It is handed on as
  `grade-the-contribution-margin-on-the-off-book-and-the-c34-arm`. It closes this finding.

## Crediting the standing charge's opex makes the guard refuse nothing it can size (20 Oct 2026)

The contribution now credits Ofgem's nil-consumption opex (§6.1, third landing;
`records/SEAT_PREREG_CREDITING_THE_STANDING_CHARGE_OPEX_IN_THE_TERM_CONTRIBUTION_2026-10-20.md`).
Printing the guard at real inputs, before any run:
- A risk-tier cut is capped at the term's floor, so it costs at most the margin over the floor.
- The value it protects is that margin + the credit (£41.57 on 2019 electricity) − £55 + the
  £27.50 replacement spend avoided, which is the margin + £14.07.
- On `CURRENT_POLICY` (no bad-debt netting, no engagement weight), value is therefore above cost
  on every resi renewal where a cut can be sized, on both fuels and in every period of the table.
- About 11 of the 92 offers would survive on the contribution alone. With the credit, every resi one
  of the 92 is predicted to survive again (P4b in the note above). *Measured 21 Oct on the full window
  at `ec7fd9942`: the guard sized 233 resi cuts and offered all 233, against 47 of 243 without the
  credit; offers 7 → 95, departures 236 → 235. Graded in
  `records/SEAT_RESULT_CREDITING_THE_STANDING_CHARGE_OPEX_IN_THE_TERM_CONTRIBUTION_2026-10-21.md`.*

**The credit is right, and it exposes what the guard has always lacked.** The guard weighs the
whole term as if the offer certainly keeps the household. It carries no weight for the chance that
the offer changes the outcome. With the value honest, only that missing weight decides, and it is
missing on the default policy. The weight exists, off by default: C29's engagement
(`retention_weighs_engagement`) and the holdout's measured uplift (B8). Turning one on is a policy
change for its own pre-registered run. It is not a rider on this landing, and this finding stays
open for it.
