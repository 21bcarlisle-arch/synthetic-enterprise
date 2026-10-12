**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# The DD shock, the save and the mover: the world's range ends, filed before any supplier arm (2026-10-12)

**Fate (2026-10-12, clear-the-decks):** ATOM -- re-site DD4b's trigger onto the loop's own DD review (not the renewal review) so it sees the 2022-23 crisis, then freeze its range ends; also run the handed-off save and mover supplier arms (P1)

The four-principles audit (`SEAT_FINDING_THE_SAVE_THE_MOVER_OFFER_AND_THE_PAYMENT_WORK_AGAINST_THE_FOUR_PRINCIPLES_2026-10-11.md`
§3 DD-shock row, §1 P2, §2 P1/P2) asked for three things. For each world response the supplier is
graded against, file the world's own predictions at the low and high end before a supplier arm runs.
Set the frozen world inside each range, or name 0 as a sensitivity end. For the mover, research
movers' supplier choice and keep k as a labelled range or replace it.

The plan half of the item's title is already done: `f49c13405` froze the payment world (plans,
early contact, own-reasons cancellation, DD amount and date), with predictions filed first.

Read at origin `c38e4db39`. Book for the runs: 40 and 200 founders, settlement budget 0, through
`/var/tmp/m_scale.py`, with `/var/tmp/dd4b_runs/dd4b_run.py` setting only DD4b's strengths.

## The answer in one paragraph

**DD4b cannot be frozen yet, because its trigger misses the crisis.** It answers a material DD rise
only at a *renewal* review. In this world the DD review that a household actually meets runs after
the loop (`run_phase4c_on_phase2b`), where no payment is drawn. On 200 founders the world's own annual
review makes **299 rises above 15%, 122 of them in 2022–23**. DD4b sees **10, all from 2017–19**.
Freezing it at its range ends now would file predictions about a trigger that answers 3% of its own
exposure. It is handed on (below), sequenced after the DD review moves into the loop. **The save**
has its two ends already: k = 0 is the published low end (0 saves), and k = 0.92 is the published
high end (0.041 per switch). The shipped 1.0 sits at that high end, as far as 12 switches can tell.
Its predictions are filed below for the supplier's fresh-seed grade. **The mover's k stays a
labelled range [0, 1].** Nothing published narrows it. The only supplier claim (about 30%) is half
of what k = 1 gives, so k = 1 is the generous end.

## 1. DD4b: why it is not frozen

**Exposure, measured with a probe that changes nothing.** The probe sets the complaint share to
1e-12 and the other two strengths to 0. So every shocked review is recorded, and no response can
fire. At 40 founders its total net (31,124.47) and bad debt (440.85) equal the freeze's default
run (`/var/tmp/wp_runs/frz-default`).

| Year | Renewal events, stayed or left (200 founders) | ...that DD4b answers (population A, shocked; 3 of the 10 left at that renewal) | The world's annual DD reviews | ...rising more than 15% |
|---|---|---|---|---|
| 2017 | 57 | 7 | 177 | 30 |
| 2018 | 49 | 2 | 138 | 78 |
| 2019 | 37 | 1 | 114 | 33 |
| 2020 | 24 | 0 | 93 | 20 |
| 2021 | 20 | 0 | 78 | 14 |
| **2022** | **0** | **0** | 70 | **54** |
| **2023** | 6 (no shock reading) | 0 | 71 | **68** |
| 2024–25 | 16 | 0 | 106 | 2 |
| **Total** | 211 (2 in 2016) | **10 (all LOW stress)** | 847 | **299** |

*Sources: `/var/tmp/dd4b_runs/f200-probe/report.json`: `customer_events[].sim_experienced_bill_shock`;
`annual_dd_review.events`, rise = (recommended − current) / current. At 40 founders the probe found 2
shocks (2017-07 and 2018-04), the same 2 the DD4b commit `d2dddf804` reported.*

**Why.** `experienced_bill_shock_at_renewal` is computed only on a renewal event. In this book no
renewal falls in 2022, and the six in 2023 carry no shock reading. Over 7m real SVT direct debits
rose by 62% in 2022 (Ofgem, July 2022; `what_bill_shock_is.md`). Those rises were reviews of a
default-tariff household's DD, not renewals. The world does run that review, but as post-processing:
`company/interfaces/dd_review.annual_dd_review_view`, called from `run_phase4c_on_phase2b.py:387`,
after the loop has drawn every payment. The route that would answer it already exists:
`dd_shock_response.respond_to_told_amount` (DD4c, `3a35fbc8f`) answers any told amount by PB4's
one definition. But nothing in the loop calls it, because no reviewed amount exists there.

**So the fix is a re-site, not a new response.** First, the DD review becomes the supplier's decision,
taken in the loop month by month, with the amount told to the household through the seam. That is
queued as `four-principles-the-dd-review-and-dunning-move-to-the-supplier` (audit §4 row 1); it was
drawn and nothing has landed. Then DD4b answers that told amount through `respond_to_told_amount`,
and the renewal-site call in `run_phase2b.py` (around line 3753) retires, or one rise is answered twice.
Only then are the predictions at the range ends worth filing. **Low and high were not run on the
current trigger.** With 10 LOW-stress shocks on 200 founders, the result is arithmetic. At high:
expect about 1 cancellation (0.10 × 10), about 2 complaints (0.24 × 10), and a 4× failure rate for a
year on about 10 households. That says nothing about 2022. Handed on as
`dd4b-answers-the-told-amount-at-the-in-loop-review-then-freeze-at-the-range-ends` (W2).

**The default, decided: 0 is named as the sensitivity end where the evidence allows it.** All three
toggles ship at 0, below each range's low end (`assumption_toggles.yaml`, `dd4b_*`). Setting a value
inside the range would change the shipped book, and the curriculum belongs to the director. So:

- For **cancel** (low 0.01) and **failure uplift** (low 0.25), each low end is "a floor, not a
  measurement". So 0, meaning no response, is a legitimate sensitivity end. A supplier grade must
  report low and high, and a result at 0 alone is not a grade.
- For **complaint**, the low end (0.02) is argued from evidence: a shock adds at least one more
  background year of complaining. 0 is below what the evidence supports. **Recommendation:** when
  DD4b is re-sited, the frozen world takes the complaint share at its low end, 0.02. That is the
  director's call to switch, and it is reversible.

## 2. The save: its ends, and predictions for the supplier's grade

**The ends exist and are not new numbers.** `world_save_response_scale` k multiplies the effect of
the save price on the world's own renewal roll. The published save rate is
`q4_save_rate_on_loss_notice`, from 0 to 0.041 per switch (ESTIMATE). k = 0 gives the 0 end. The
0.041 end is k = 0.041 / 0.0444 = **0.9234**, from the settled run of 2026-10-08. In that run, at a
flat 4% cut, k = 1 gave 0.5328 expected saves over 12 switches
(`SEAT_FINDING_THE_REACTIVE_SAVE_IN_THE_SETTLED_RUN_2026-10-08.md`). **So the shipped 1.0 sits at
the high end.** 0.0444 against 0.041 is within what 12 switches can resolve. It is left at 1.0, and
graded at 0, 0.92 and 1.

**Predictions for the grade.** That grade is `four-principles-the-save-mover-and-renewal-cut-graded-on-fresh-seeds-across-world-ranges`
(C), on the production book to 2025-06-07, under the standing price match, on each authorised fresh
seed. These predictions are filed before any arm runs:

| # | Quantity | Prediction | Why |
|---|---|---|---|
| S1 | k = 0 against `off` | account-state lists and total net identical to the penny on every seed; 0 saved | structural: at k = 0 the save price leaves P(stay) at the offer's, so a leaver stays a leaver (held at a flat cut on 2026-10-08) |
| S2 | saves at k = 0.92 against k = 1 | never more, up to the first account whose path diverges | same roll, smaller P(stay) |
| S3 | offers per seed | 0 to 5 | 2 of 23 CSS-held notices at the base seed; the price match is inert when the company's renewal is already at or below the market's best deal or below its cost floor (21 of 23 at base) |
| S4 | saves per seed at k = 1 | 0 to 3; pooled across seeds, saves per CSS-held loss notice at most 0.08 | base 1 / 23 = 0.043 |
| S5 | on − off total net, every seed, every k | under 0.5% of that seed's total net | base +£1,582 |
| S6 | stayer price moves; vulnerable twin shortfalls | 0 and 0 on every seed and k | the guards in `afd818b22` |

**What would refute the world rather than these numbers:** a save at k = 0 (S1), or more saves at
0.92 than at 1 before any divergence (S2).

## 3. The mover: k from research

**Researched 2026-10-12. Nothing narrows k** (recorded in `docs/market_research/home_moves.md` §8.5
G8.4). No source splits movers three ways (took us with them / stayed on the destination's deemed
contract / switched again). The Ofgem/Ipsos *Consumer Engagement Survey 2019* gives "I moved home" as
the prompt for 7–8% of engagers. That is engagers who moved, not movers who engaged, and no mover
denominator is published to invert it. The one take-up-shaped figure is BFY Group's unnamed supplier,
whose mover retention rose from about 5% to about 30%. It is a consultancy case study, with no base
and no price. Nothing compares a mover's stay with a renewer's at the same price. **So k stays the
whole answer, as a labelled range [0, 1].** A mover-specific response is suggested in direction
only: movers answer the move, not the price. There is no number to build it from.

**A reality check, not an input (canon W8).** At k = 1, 9 of 15 offered movers followed (60%,
`68793db33`, 40 founders, base seed), about twice the best figure any supplier has claimed. k = 1 is
the generous end, and the published figure points towards the lower half. The offer is off
(`move_with_us_activation.json`), so no default is moved. **The grade runs at k ∈ {0, 0.5, 1}.**

**Predictions for that grade.** Same continuation; 40 founders, budget 0, each fresh seed. Filed
before any arm runs:

| # | Quantity | Prediction | Why |
|---|---|---|---|
| M1 | k = 0 against `off` | identical account terms and total net on every seed; 0 followers | structural, and held at base in `68793db33` |
| M2 | followers at 0.5 against 1 | never more, up to the first divergence; pooled, 0.3 to 0.7 of k = 1's | same roll against half the P(stay) |
| M3 | followers / answerable offers at k = 1, pooled | 0.4 to 0.8 | a renewing household's P(stay) in this world; base 9 / 15 |
| M4 | followers supplied at the new home | at most half of followers | base 2 of 9: gas-only legs, destination cells outside the weather store, and half-hourly files are not carried |
| M5 | stayer price moves; vulnerable twin shortfalls | 0 and 0 | the premium hold in `68793db33` |
| M6 | sign of on − off at k = 1 | turns on the supplied count; 0.00 on a seed with none supplied | base +£1,579.90 from 2 supplied |

## Limits

The DD4b census comes from one seed, at 200 founders. Why no renewal event falls in 2022 on this
book was not traced. The re-site makes it moot, because the review, not the renewal, carries the
shock. I did not run
the save or the mover arms; those are the supplier lane's, and they come after these predictions.
The save's 0.92 rests on 12 switches. The mover research could not reach uSwitch, MoneySuperMarket
or supplier investor material (search was blocked), so those are unsearched, not confirmed empty.
