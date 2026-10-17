**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 4 · **Subjects:** `PB4_engagement_separated_from_elasticity`, `EP17_varied_population_draw` · **Claim:** `the-worlds-switching-gradient-by-payment-and-tariff` (Lane 0 delivery)

# Pre-registration: where the world loses the published switching gradient by payment method and tariff

Written 2026-10-17 at origin `1e89cde3a`, before any outcome in the run has been read against world
truth. What has been read: the run file's schema (field names only) and the world's code. Slice 10's
addendum ratios (switch-only, company-observed payment and tariff: prepayment vs DD 0.98 / 1.16,
fixed vs default 0.77 / 0.82, at cuts 2020 / 2023) are KNOWN and are not predicted here. The finding
goes in a separate file, graded beside each line below. This file is not edited after the run.

**Measurement only. No world value changes before the 19 Oct publish.**

## The book

`docs/reports/run_output_latest.json` in the shared tree, producing commit `78f77c34e`, the same book
slice 10 graded. Harness-side, truth used as an instrument: world payment channel and engagement
archetype are read through `simulation.household_segments` (deterministic per customer id), never
fed back to the company.

## What the code says the world does (read before the data)

1. **The payment channel enters ONE place in switching:** the active-renewal gate,
   `p = archetype_p × engagement_multiplier_for_channel(channel)`, archetype_p 0.50 / 0.24 / 0.20.
   The multiplier is the CIM w6 rate over its population mean: DD 0.056, SC 0.057, PPM 0.031,
   normalised, so roughly DD 1.06, SC 1.08, PPM 0.59.
2. **A fixed term can only end in a switch at its end**, and only if that renewal is active. A passive
   renewal rolls to SVT and cannot depart at that occasion.
3. **On SVT, the only departure route is the inertia hazard**, which reads the archetype and years on
   SVT (20%/yr recent, 10%/yr long-standing), times action propensity (income stress × housing
   tenure). **It does not read the payment channel.**
4. **Every customer starts on a fixed term.** So "on a fixed tariff" in this world is, for most
   account-months, a customer's FIRST term, which nobody chose against us.

So the channel's gradient is assigned on E (the gate), but a PPM household that the gate sends to
SVT meets an SVT hazard with no channel term in it. Whether the gradient survives depends on whether
P(switch | active renewal) differs from what the same household then leaves at on SVT.

## The quantities, defined before measured

- **Switch:** a departure whose cause is not a home move (`svt_inertia`, `bill_shock`,
  `price_position`, `dissatisfaction`, or any other non-move cause), one per account.
- **Exposure:** supplied account-years from the company's own term record (`account_state_log`),
  each term row classed as:
  - **first-term fixed:** a fixed row with no earlier fixed row on the account;
  - **renewal-chosen fixed:** a fixed row after an earlier one (reached only by an active renewal);
  - **default:** an SVT row.
- **Switch rate:** switches per account-year, a switch credited to the tariff cell of the term it
  ended. Payment group = the world's own channel (electricity draw for the household).
- **Bounds:** 95% Poisson interval on each rate; the ratio's interval from the log-ratio standard
  error sqrt(1/a + 1/b). Cells with fewer than 5 switches are reported and not graded.
- **Active-renewal probability each group carries:** the mean of
  `active_renewal_probability_for_customer` over the group's accounts, and separately the REALISED
  active share at fixed term ends where the run records it.

## Predictions

- **P1 (the draw assigns the channel gradient).** Mean drawn active-renewal probability, PPM over DD:
  between 0.45 and 0.75. SC over DD: between 0.85 and 1.20. Reading (a) is refuted for payment if P1
  holds.
- **P2 (the gate fires at the realised end).** Realised active share at fixed term ends, PPM over DD:
  below 0.85, if at least 5 PPM term ends exist.
- **P3 (the SVT hazard carries no channel).** SVT switch rate per account-year, PPM over DD: between
  0.70 and 1.40 (interval covers 1). If P3 holds and the whole-book ratio sits near 1, the loss is
  (b): the gradient is assigned on the gate and washed out because the gate only routes a household
  between two exits of similar size.
- **P4 (the published 0.55 is not reached).** Whole-book switch rate per account-year, PPM over DD,
  world channel: above 0.75. (Slice 10 read 0.98 / 1.16 on the company's channel; predicted to agree
  in direction on world truth.)
- **P5 (renewal-chosen fixed is a selected population).** Mean drawn active-renewal probability on
  renewal-chosen fixed accounts exceeds that on first-term fixed accounts, by at least 0.03.
- **P6 (tariff cells).** Switch rate per account-year:
  - first-term fixed below default (ratio below 1);
  - renewal-chosen fixed over first-term fixed above 1;
  - renewal-chosen fixed over default: between 0.6 and 1.8, so short of the published 2.8.
- **P7 (where the tariff gradient goes).** The published 2.8 is lost mainly to (c): this world's
  "fixed" is dominated by first terms (predicted over 60% of fixed account-years), and its switching
  happens only at term ends. Stated beside it, a fourth reading the direction did not list: CIM w6
  asks tariff type at the time of the survey, after any switch, and a household that just switched is
  likely to be on a new fix. Part of the 2.8 may be switchers landing on fixes, which no losing
  supplier could observe beforehand. This is checked against the source text, not assumed.

## Grading rule for (a), (b), (c)

For each gradient (prepayment vs DD, standard credit vs DD, fixed vs default):

- **(a)** if the drawn active-renewal probability does not carry the published direction;
- **(b)** if it does, but the realised switch rate does not (interval covers 1, or the wrong side of
  it);
- **(c)** if the switch rate on the population the published survey describes (renewal-chosen fixed,
  or channel within one tariff cell) carries it and the observable's whole population does not.

More than one may hold. F11: when the evidence is ambiguous, read it against the thesis (that the
world can carry the gradient).

## What follows, filed now

Any world change this implies is pre-registered in the finding for after the publish, and not built.
