# B8: no cut size pays in this world, because each extra pound of cut buys less retention than the last

**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout` · **Claim:** `b8-the-retention-decision-over-a-curve-of-cut-sizes`

The predictions were filed before the runs:
`SEAT_PREREG_B8_THE_RETENTION_DECISION_OVER_A_CURVE_OF_CUT_SIZES_2026-10-08.md`. All four held.

## The answer

**No cut, from £2.5 to £30/MWh, pays at either end of the margin bracket. The learned decision offers
it on 0% of fresh decisions at every size.** At every point it matches "cut for none" to the penny,
and it beats "cut for all" by anything from £2.86 per decision (£2.5 cut, 14% margin) to £48.5
(£30 cut, 1.9% margin).

**Each extra pound of cut buys less retention than the last.** The true effect per £/MWh of cut is
0.00166 at £2.5, 0.00159 at £5, 0.00152 at £7.5, 0.00140 at £15 and 0.00123 at £30. The cost of a
cut grows in proportion to its size, because it is paid on every kWh of every household that stays.
So the best ratio of true effect to break-even effect comes at the **smallest** cut. Even there it is
**0.27** at a 14% margin and **0.04** at 1.9%.

As the cut tends to zero, that ratio tends to about 0.27. So **no uniform renewal cut in this world
is worth offering**, however small. For one to pay at the top of the bracket, the world's response
would have to be about **3.7 times steeper**: about +0.0062 of P(stay) per £/MWh, or +0.046 per £7.5.
At the 1.9% floor it would have to be about 25 times steeper.

**So a holdout-learned decision cannot beat the right flat rule in this world by choosing a cut
size.** It does find the right flat rule without being told it. A supplier that cut for everyone
would lose £2.9 to £48 per decision.

## The table

All runs were learned on seed 42 (about 34,700 treated and 34,800 held out per run) and decided on
fresh seeds 101 and 202 (about 12,700 decisions each). The 7.5 rows are from the earlier finding.

| cut £/MWh | fresh seed | margin | learned effect (95%), verdict | true effect | true effect per £/MWh | learned cuts | supplier: learned | supplier: cut all | supplier: cut none | household: cut all | break-even effect | true / break-even |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2.5 | 101 | 0.019 | +0.0055 (−0.0018, +0.0128) undecided | +0.0041 | 0.00166 | 0% | 18.33 | 14.57 | 18.33 | 3.91 | +0.113 | 0.04 |
| 2.5 | 101 | 0.14 | same | +0.0041 | 0.00166 | 0% | 135.08 | 132.22 | 135.08 | 3.91 | +0.0154 | 0.27 |
| 2.5 | 202 | 0.019 | same | +0.0041 | 0.00165 | 0% | 18.14 | 14.40 | 18.14 | 3.88 | +0.114 | 0.04 |
| 2.5 | 202 | 0.14 | same | +0.0041 | 0.00165 | 0% | 133.63 | 130.79 | 133.63 | 3.88 | +0.0155 | 0.27 |
| 5 | 101 | 0.019 | +0.0086 (+0.0013, +0.0158) raises | +0.0079 | 0.00159 | 0% | 18.30 | 10.70 | 18.30 | 7.87 | +0.231 | 0.03 |
| 5 | 101 | 0.14 | same | +0.0079 | 0.00159 | 0% | 134.81 | 128.94 | 134.81 | 7.87 | +0.0312 | 0.25 |
| 5 | 202 | 0.019 | same | +0.0079 | 0.00158 | 0% | 18.11 | 10.57 | 18.11 | 7.81 | +0.230 | 0.03 |
| 5 | 202 | 0.14 | same | +0.0079 | 0.00158 | 0% | 133.47 | 127.63 | 133.47 | 7.81 | +0.0313 | 0.25 |
| 7.5 | 101 | 0.019 | +0.0117 (+0.0044, +0.0189) raises | +0.0114 | 0.00152 | 0% | 18.25 | 6.76 | 18.25 | 11.88 | | |
| 7.5 | 101 | 0.14 | same | +0.0114 | 0.00152 | 0% | 134.46 | 125.46 | 134.46 | 11.88 | +0.047 | 0.24 |
| 15 | 101 | 0.019 | +0.0212 (+0.0139, +0.0284) raises | +0.0210 | 0.00140 | 0% | 18.10 | −5.36 | 18.10 | 24.17 | +0.717 | 0.03 |
| 15 | 101 | 0.14 | same | +0.0210 | 0.00140 | 0% | 133.38 | 114.43 | 133.38 | 24.17 | +0.0973 | 0.22 |
| 15 | 202 | 0.019 | same | +0.0208 | 0.00139 | 0% | 17.92 | −5.38 | 17.92 | 23.99 | +0.722 | 0.03 |
| 15 | 202 | 0.14 | same | +0.0208 | 0.00139 | 0% | 132.07 | 113.18 | 132.07 | 23.99 | +0.0978 | 0.21 |
| 30 | 101 | 0.019 | +0.0369 (+0.0298, +0.0440) raises | +0.0370 | 0.00123 | 0% | 17.83 | −30.68 | 17.83 | 49.73 | +1.51 | 0.02 |
| 30 | 101 | 0.14 | same | +0.0370 | 0.00123 | 0% | 131.35 | 90.62 | 131.35 | 49.73 | +0.205 | 0.18 |
| 30 | 202 | 0.019 | same | +0.0367 | 0.00122 | 0% | 17.62 | −30.50 | 17.62 | 49.31 | +1.51 | 0.02 |
| 30 | 202 | 0.14 | same | +0.0367 | 0.00122 | 0% | 129.82 | 89.33 | 129.82 | 49.31 | +0.205 | 0.18 |

**How the break-even effect is derived.** It is derived from the aggregates, not from per-row data.
`cut all − cut none = mean(d·L) − household`, so the mean forward value `L ≈ (all − none +
household) / d`, and the break-even effect is `household / L`. This assumes `d` does not co-vary
with `L`. It reproduces the earlier finding's +0.048 at £7.5 and 14% (it gives +0.047).

## The channel read is exercised now

At £2.5 and £5, every fresh decision read the pooled effect, because the pooled effect is too small
for either channel to reach the decisions it needs (125,092 per arm at £2.5). At £15 and £30, the
pooled effect is large enough that **direct debit is read on its own channel**: 9,448 of 12,875
decisions at £15, and 9,592 of 13,079 at £30. `other` is read on its own channel at £30 too. The
direct-debit effect is the larger one at every cut (+0.025 against +0.012 at £15; +0.040 against
+0.029 at £30), but even it is below half the break-even. The channel branch therefore changes which
estimate is read, not the decision.

## Graded against the pre-registration

1. **The effect rises less than proportionately with the cut. Held.** Every true effect fell inside
   its predicted range: £2.5 → +0.0041 (predicted +0.003 to +0.006), £5 → +0.0079 (+0.006 to
   +0.010), £15 → +0.021 (+0.018 to +0.025), £30 → +0.037 (+0.025 to +0.045). The effect per £ falls
   monotonically.
2. **No cut size pays at either margin. Held.** "Cut for all" loses at every cut and margin, and the
   loss grows with the cut.
3. **The learned decision cuts on at most 1%. Held.** It cut on 0% everywhere. At £2.5 the interval
   reads "undecided", as allowed.
4. **The best ratio is at the smallest cut, and it is below 0.5. Held.** It is 0.27 at £2.5 and 14%.

## What this does and does not say about the thesis

- **A uniform renewal offer is the wrong shape of offer.** The cut is paid to every household that
  stays, and most of them would have stayed anyway (the held-out stay share is high). The condition
  is `d / (p0 + d) > cE / L`. So an offer pays more easily where `p0` is LOW, that is, offered to
  households who have shown they are leaving. Every renewal here is offered blind. Real retention
  practice, as far as we know, is a *save offer* made to a customer who has started to leave. But
  that is a trade question, not a published number, so it goes to the director (below) rather than
  into a constant.
- **The heterogeneity the world holds cannot be targeted from what the company sees.** Per-household
  elasticity is drawn close to orthogonal to observables, by design. The only targeting the decision
  can do is on the value side (`L/E`), and no household's `L/E` is extreme enough at the real effect.
- **The world's curve is ours.** As before, this grades whether the company learns the curve and acts
  on it correctly, not whether the curve's slope (about 0.0015 of P(stay) per £/MWh) is the real one.
  If the real slope were about four times steeper, small cuts would start to pay at the top of the
  margin bracket. That is the number most worth sourcing for B8.

**2026-10-08, the save-offer question sourced:** `docs/market_research/a_save_offer_against_the_switching_rules_and_the_seam.md`.
A GB losing supplier hears of a switch 1 working day to 28 days ahead under CSS. It may make an offer,
but may not block the switch with one (SLC 14.4), and from April 2022 the offer can only be a fixed
retention tariff (SLC 22B derogation). The regulator describes 2022-2025 practice as retention tariffs
*targeted at term end*, not reactive saves, and how common reactive saves are is not published. In
this world the company is told of a loss only once the switch can no longer be cancelled, and nothing
can answer a save, so a save-offer decision set would need world build first.

## Reproducing it

```
for c in 2.5 5 15 30; do
  PYTHONPATH=. python3 -m tools.grade_coin_drawn_holdout decide --arm real --cut $c \
      --train-per-year 4700 --fresh-seeds 101 202 --out real_$c.json &
done; wait
```

Four ran in parallel at about 110 MB each and finished within ten minutes.
