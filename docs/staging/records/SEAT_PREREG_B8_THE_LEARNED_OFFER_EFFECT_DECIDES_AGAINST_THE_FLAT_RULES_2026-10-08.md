# Pre-registration: the learned offer effect drives a retention decision, graded against both flat rules

**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout` · **Claim:** `b8-the-learned-offer-effect-drives-a-decision-and-meets-the-flat-baseline`

Filed 2026-10-08 before any run below. Result goes in a separate finding; this file is not edited after the runs.

## What the decision is

At a renewal the company offers the cut `c` (£/MWh off the published default) or not. With `p0` the
held-out stay share it observes on the household's channel, `d` the learned effect, `M` the
household's annual margin (margin share `g` x its last twelve bills) and `E` its billed kWh, the
forward value of each option is

- no cut: `p0 * M * (1 + f)`
- cut:    `(p0 + d) * (M * (1 + f) - c * E)`

where `f = s / (1 - s)` is the expected further years of supply after this one, from the company's
own observed held-out stay share `s`. It offers the cut where the second is larger AND the holdout's
interval says the offer raises staying; otherwise it does not, with the reason named.

`g` is NOT picked. The knowledge layer carries two published brackets and the right value lies
between them: the cap's EBIT allowance, 1.9-2.6% of the bill (`ASSUMPTIONS.md` rows 49 and 300,
treating all opex as leaving with the customer) and the sector's gross margin, 8-14% of revenue
before opex (`supplier_financial_reporting.md`, treating all opex as fixed). The decision is graded
at both ends, 0.019 and 0.14. How much opex leaves with one customer is a practitioner question.

## Predictions (arithmetic from the 2026-10-07 L run: d ~ +0.0115 at c = 7.5, s ~ 0.60)

At g = 0.14 a typical household has M ~ £130/yr, so retention is worth d * M * 2.5 ~ £3.7, against a
cut cost of p1 * c * E ~ £14. The cut would need d ~ 0.045 to pay at g = 0.14.

1. **Real arm (cut 7.5), both ends of g:** the learned decision offers the cut on 0% of fresh
   decisions, on every channel. Its supplier value equals "cut for none" to the penny. "Cut for
   all" loses supplier value at both ends, by about £8-13 per decision at g = 0.14 and more at 0.019.
   The household saving is ~£10-14 per decision under "cut for all" and 0 under learned and none.
2. **Null arm:** offers the cut on 0% of decisions (the interval never says "raises staying").
3. **Planted arm (+0.10, priced as costing the same cut):** at g = 0.14 the decision offers the cut
   on more than half of decisions and beats "cut for none" on supplier value; at g = 0.019 it
   offers it on 0%. This is the control that the CUT branch can be taken at all.
4. **Per channel:** no channel reaches the ~28,500 decisions per arm the pooled effect needs for
   80% power at size L (about 35,000 per arm in total). Direct debit comes closest. Where a channel
   is short, the decision reads the pooled estimate and says so.

If 1 holds, learning does NOT beat the right flat rule at this offer: it matches "cut for none" and
beats "cut for all". That is a result, not a failure: the method's value at this offer is knowing
which flat rule is right, and the household's side of it is the saving the company declines to give.
