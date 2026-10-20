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

## Grade, 2026-10-20 14:40 BST — on arm at `c61d8b608`, full window, default seed

Run: second leg of unit `longjob-retention-guard-contribution-grade-c61d8b608`, the same worktree
and command as the graded off book with `next_best_action_decides_at_renewal` and
`next_best_action_decides_per_household` on. Output `/var/tmp/se-ret-margin/on_arm.json`, log
`/var/tmp/se-ret-margin/run.log` (second half).

| | Predicted | `c61d8b608` on arm | Verdict |
|---|---|---|---|
| P2′a advised rows | 0–10 of ~978, ≤ 1% | **4 of 972 (0.41%)** | confirmed |
| P2′b median household contribution | −GBP 10 to −GBP 2 /month | **−GBP 3.91** | confirmed |
| P2′c households with a negative contribution | ≥ 60% | **85.8%** of 324 | confirmed |
| P2′d legs without a contribution | ≤ 5% of rolls | **2 of 1,467 legs** (0 rolls, 2 riding legs) | confirmed |

The four advised rows are two renewals, both 2023:
- PROS-2022-0248, dual fuel, 2023-08-10: contribution GBP 34.5/month, the GBP 2/month give-up, value
  change GBP 7.6.
- PROS-2022-0400, electricity, 2023-12-21: the very large account the retention grade also named
  (GBP 189.9/month). Three action rows were advised, value changes GBP 1.8 to GBP 55.0.

Both are what the inputs section said would be the only ones: a large account, or a strike well
above its cost.

**The book is unmoved, to the penny.** Net margin is GBP 446,883.96 on both arms, and so are
offers (9), retention spend and no-offer churns (66). That is the design: the switch records and
sends nothing. It is also a placebo control on the off book's figure. The −GBP 100,746 move against
the published book is not run noise, and attributing it is still owed to C1/C2 beside the retention
grade. That control (`longjob-retention-guard-parent-control-6fe4282c0`, at `6fe4282c0`,
`/var/tmp/se-ret-margin/parent_off.json`) launched 14:35 BST. *Corrected 2026-10-20 18:30 BST: the −GBP 100,746
was two clocks differenced, the published settled-realised net against the provisioned printed line.
Like for like, the move is −GBP 657, of which the guard is −GBP 805
(`SEAT_PREREG_THE_RETENTION_GUARD_ON_THE_TERMS_CONTRIBUTION_2026-10-20.md`, Correction).*

**What this does and does not settle.** C34's floor binds once it reads what the supplier keeps
(it advises 0.4% of rolls). With the standing charge left out, the contribution is a lower bound
(F11), so "0.4%" is a floor on how often advice clears it, not an estimate. Switching it on would
move no money, because it records only. That makes the switch a question of whether the log is
worth its run time, not of value. The question that would move money stays the director's (M2):
should a positive-sum action be paired with a price that shares its value?
