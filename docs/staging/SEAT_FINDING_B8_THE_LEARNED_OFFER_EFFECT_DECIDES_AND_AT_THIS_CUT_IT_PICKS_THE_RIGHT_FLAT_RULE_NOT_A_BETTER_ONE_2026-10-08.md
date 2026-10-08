# B8: the company decides on its learned offer effect. At a £7.5/MWh cut it picks the right flat rule, not a better one

**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout` · **Claim:** `b8-the-learned-offer-effect-drives-a-decision-and-meets-the-flat-baseline`

The predictions were filed before the runs:
`SEAT_PREREG_B8_THE_LEARNED_OFFER_EFFECT_DECIDES_AGAINST_THE_FLAT_RULES_2026-10-08.md`. All four held.

## The answer

**The learned decision never offers the £7.5/MWh cut, on any fresh decision, at either end of the
published margin bracket.** So it matches the flat rule "cut for none" to the penny, and it beats
"cut for all" by about £9.00 per decision at a 14% margin and £11.49 at 1.9%. That is not learning
beating the right flat rule. It is learning *choosing* the right flat rule, which a supplier could
not know in advance without a holdout. The household's side shows what was declined: "cut for all"
would have saved households about £11.80 per decision.

**The arithmetic says why, and it is not close.** The cut buys +0.0114 of P(stay). At a 14% margin, a
retained household is worth about £250 over its expected tenure, so the retention is worth about
£2.80. The cut costs about £11.80 in revenue given to the households that stay, most of whom would
have stayed anyway. **The cut would need about +0.048 of P(stay), four times what the world gives, to
pay at the top of the bracket.**

**The cut branch is reachable.** On the planted arm (+0.10 planted, about +0.087 after the cap at 1),
the same decision offers the cut on 93% of decisions at 14% and on 0% at 1.9%. At 14% it beats
"cut for none" by about £6.90 per decision, and it beats "cut for all" by £0.09. The 7% it declines
are households whose bill is small next to their kWh. The null arm offers the cut nowhere: its
interval never says "raises staying".

## What was built

- **`company/pricing/discovered_price_sensitivity.retention_cut_decision`.** It reads
  `estimate_offer_effect` and offers the cut only where two things hold. The holdout's interval must
  say the offer raises staying. And `(p0 + d)(L - cE)` must be more than `p0 L`. Here `L` is the
  household's margin share of its last twelve bills, valued over `1 + s/(1-s)` years at the observed
  held-out stay share `s`. `cE` is the cut on its billed kWh. The margin share has no default, and
  the caller names which end of the bracket it means.
- **`estimate_offer_effect_by_channel` and `effect_for_channel`.** A channel is read on its own
  estimate only when its smaller arm holds the decisions per arm the pooled effect needs for 80%
  power. Otherwise the pooled estimate is used, and the read says which one and why.
- **`billed_kwh` crosses the seam.** It is the kWh the company billed over the trailing year. A
  supplier meters and bills this, and a cut per MWh is charged on it. It sits on the allow-list next
  to the bills.
- **`tools/grade_coin_drawn_holdout.py decide`.** It learns on seed 42, decides on fresh seeds 101
  and 202, and grades every rule against the world's own P(stay) at each offer.
- **Two controls, five mutations, all red.** The tests are
  `test_the_decision_takes_every_branch_and_the_margin_is_what_flips_it` (one partition over
  cut / no cut on value / no cut on an undecided interval) and
  `test_a_channel_is_read_on_its_own_only_when_it_holds_the_decisions_the_effect_needs`. The five
  mutations: the verdict check dropped, the channel read always taken, the channel read never taken,
  the margin share ignored, and the comparison inverted.

## The margin is a bracket, not a number

Nothing establishes what share of a retained household's bill a supplier keeps. Two published ends
bound it:

- **1.9%**, the cap's EBIT allowance (`ASSUMPTIONS.md` rows 49 and 300). This end assumes every opex
  pound leaves with the customer.
- **14%**, the top of the sector's gross margin before opex (`supplier_financial_reporting.md`).
  This end assumes no opex pound does.

The real figure depends on how much opex one customer carries away, which is **a practitioner
question for the director**. At this cut it makes no difference, because the decision is the same at
both ends. It would make a difference for an offer with an effect between roughly +0.01 and +0.05.

## The graded table

The decisions were learned on seed 42 and graded on fresh seeds. The real arm was trained on 34,674
treated and 34,792 held-out decisions; the null and planted arms on about 6,300 per arm. Each fresh
seed holds about 12,600 decisions. Value is the supplier's forward value per decision, in £; the
household saving is the cut paid to households who stay, per decision.

| arm | fresh seed | margin | learned effect (95%) and verdict | true effect on fresh | learned cuts | supplier: learned | supplier: cut all | supplier: cut none | household: learned | household: cut all |
|---|---|---|---|---|---|---|---|---|---|---|
| real | 101 | 0.019 | +0.0117 (+0.0044, +0.0189) raises | +0.0114 | 0% | 18.25 | 6.76 | 18.25 | 0.00 | 11.88 |
| real | 101 | 0.14 | same | +0.0114 | 0% | 134.46 | 125.46 | 134.46 | 0.00 | 11.88 |
| real | 202 | 0.019 | same | +0.0114 | 0% | 18.07 | 6.66 | 18.07 | 0.00 | 11.79 |
| real | 202 | 0.14 | same | +0.0114 | 0% | 133.13 | 124.17 | 133.13 | 0.00 | 11.79 |
| null | 101 | 0.019 | +0.0005 (−0.0167, +0.0178) undecided | 0 | 0% | 18.35 | 6.72 | 18.35 | 0.00 | 11.63 |
| null | 101 | 0.14 | same | 0 | 0% | 135.21 | 123.58 | 135.21 | 0.00 | 11.63 |
| null | 202 | 0.019 | same | 0 | 0% | 18.15 | 6.61 | 18.15 | 0.00 | 11.54 |
| null | 202 | 0.14 | same | 0 | 0% | 133.76 | 122.22 | 133.76 | 0.00 | 11.54 |
| planted | 101 | 0.019 | +0.0946 (+0.0786, +0.1106) raises | +0.0866 | 0% | 18.34 | 7.81 | 18.34 | 0.00 | 13.26 |
| planted | 101 | 0.14 | same | +0.0866 | 93% | 142.11 | 142.02 | 135.13 | 12.03 | 13.26 |
| planted | 202 | 0.019 | same | +0.0865 | 0% | 18.14 | 7.70 | 18.14 | 0.00 | 13.15 |
| planted | 202 | 0.14 | same | +0.0865 | 93% | 140.53 | 140.43 | 133.69 | 11.96 | 13.15 |

## Per channel: neither channel is large enough, so the decision reads the pooled effect

The drawn population carries two payment channels, `direct_debit` and `other`, not the three the
2026-10-03 slopes were split by. On the 69,000-decision training set:

| channel | per arm (T / H) | effect (95%) | verdict |
|---|---|---|---|
| direct_debit | 24,776 / 25,132 | +0.0159 (+0.0073, +0.0245) | raises staying |
| other | 9,898 / 9,660 | +0.0006 (−0.0130, +0.0143) | undecided |

The pooled effect needs **27,701 decisions per arm**. Direct debit is short of that by about 2,900,
and `other` by about 18,000. So every fresh decision read the pooled estimate, and the read says so.
On these intervals direct debit looks more responsive than `other`, but they overlap, and I cannot
yet say the channels differ. The direct-debit point (+0.016) would not pay the cut either way.

## Graded against the pre-registration

1. **Real arm. Held.** It cut on 0% of decisions on every channel. Learned equals none. "Cut for all"
   lost £9.00 and £8.96 at 14% (predicted £8–13) and £11.49 and £11.41 at 1.9%. The household saving
   under "cut for all" was £11.79–11.88 (predicted £10–14).
2. **Null arm. Held.** It cut on 0%.
3. **Planted arm. Held.** At 14% it cut on 93% (predicted more than half) and beat "cut for none".
   At 1.9% it cut on 0%.
4. **Per channel. Held.** Neither channel reaches the per-arm count. Direct debit comes closest.

## What this does not establish

- **The world's curve is ours.** As at L1, this shows the company can learn the effect and act on it
  correctly. It does not show the real effect of a £7.5 cut is +0.011.
- **The tenure valuation is a simplification.** It is a constant held-out stay share with no
  discount rate. Re-acquisition cost is not counted on the retention side. Adding the sourced £55
  acquisition cost to the value of a stay adds about £0.63 per decision at the real effect, which
  changes no decision.
- **No production retention path reads the decision yet.** `run_phase2b`'s retention tiers still
  price offers on the unsourced `RETENTION_EFFECTIVENESS`. Wiring this decision into the run loop is
  the L3 step.
- **One cut size.** The break-even effect (+0.048 at 14%) says a smaller cut with a proportionately
  smaller effect would fail the same way. A curve over cut sizes is the obvious next measurement, and
  it costs minutes.

## Reproducing it

```
PYTHONPATH=. python3 -m tools.grade_coin_drawn_holdout decide --arm real --train-per-year 4700 --fresh-seeds 101 202 --out real.json
PYTHONPATH=. python3 -m tools.grade_coin_drawn_holdout decide --arm null --train-per-year 850 --fresh-seeds 101 202 --out null.json
PYTHONPATH=. python3 -m tools.grade_coin_drawn_holdout decide --arm planted --train-per-year 850 --fresh-seeds 101 202 --out planted.json
```

The three ran in parallel and all finished within about ten minutes, the real arm last.
