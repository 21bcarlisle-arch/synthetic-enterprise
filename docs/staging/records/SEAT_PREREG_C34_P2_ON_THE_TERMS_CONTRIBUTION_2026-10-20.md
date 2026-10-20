# Pre-registration: C34's P2 band once its margin is the term's contribution

**Written 2026-10-20, after the build and before any on-arm re-run.** Claim
`c34-renewal-margin-net-of-pass-through` (Lane 0, seat direction). No run carrying the change has been
launched or read to write this. The finding is
`SEAT_FINDING_C34S_RENEWAL_MARGIN_IS_THE_ALL_IN_RATE_LESS_THE_WHOLESALE_FORWARD_SO_IT_IS_NOT_A_MARGIN_2026-10-20.md`.

## What changed, said first

C34 used to be handed `(unit rate − company forward) × company EAC / 12`. It is now handed
`term_contribution_per_month`, which is
`[(unit rate − pre_margin_unit_rate) × company EAC − FIXED_OVERHEAD_GBP_PER_YEAR["resi"]] / 12`
per leg (`next_best_action_and_cross_sell.md` §6.1, amended 2026-10-20).
- The pre-margin rate is the company's forward, plus capital, plus the term's locked policy and
  network costs.
- The standing charge is left out as a stated GAP.
- A leg whose term records no locked costs is counted in
  `next_best_action_legs_without_contribution` and is not decided.

Nothing else changed. The switch stays off on every standing policy.

## What the inputs say before the run (printed with the company's own functions)

At an unmoved strike (pre-margin + GBP 2/MWh) on 3.1 MWh, the unit leg keeps GBP 0.52/month in every
year. Cost to serve is GBP 4.58/month per leg, so the contribution is about −GBP 4.1 per leg and
−GBP 8.1 for a dual household. Over the same leg the old spread read GBP 15.8 (2016) to GBP 30.2
(2024). The contribution goes positive only where an upstream writer raised the strike above its
cost. One example: a strike GBP 29/MWh over cost on 2.7 MWh reads +GBP 2/month. Another is a large
account. On r4, no household at GBP 30/month or less was advised.

## Predictions, on the same book and command as r4 with only this commit added

- **P2′a. Advised rows are 0 to 10 of about 978 (≤ 1%).** The band for "the floor binds on the
  company's belief" is 0–2%.
- **P2′b. The median household contribution is between −GBP 10 and −GBP 2 a month.**
- **P2′c. At least 60% of households have a negative contribution.**
- **P2′d. Legs without a contribution are at most 5% of rolls.** Both fuels' renewal routes write
  the locked costs onto the term dict.

## What each refutation would mean

- **P2′a above 2%.** Either the writers move the strike far more often than the flat-margin reading
  says, or the floor admits advice on a negative contribution. Read `value_change_gbp` and the
  margin on the advised rows before anything else.
- **P2′b above −GBP 2.** The upstream writers (portfolio premium, profitability uplift, margin
  feedback) carry most of the book's strike above cost. That would be a finding about the strike,
  not about C34.
- **P2′d above 5%.** Some route builds a renewal term without its locked costs. Name it. Do not
  fall back to the spread.

## What a confirmation would and would not show

A confirmation shows that C34's floor binds once it reads what the supplier keeps. It does **not**
show that advice is worthless. With the standing charge out, the contribution is a lower bound
(F11). Whether a positive-sum action should be paired with a price that shares its value remains
the director's question (M2).
