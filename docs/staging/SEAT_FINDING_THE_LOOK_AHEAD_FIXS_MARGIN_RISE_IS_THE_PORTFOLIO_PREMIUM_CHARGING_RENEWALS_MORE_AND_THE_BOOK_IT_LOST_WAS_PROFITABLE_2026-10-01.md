**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing` — Lane 0 delivery

# The look-ahead fix's margin rise is the portfolio premium charging renewals more, and the book it lost was profitable

Claim `attribute-the-look-ahead-fixs-margin-rise-by-writer-and-book`. Graded against
`docs/staging/records/SEAT_PREREGISTRATION_THE_LOOK_AHEAD_FIXS_MARGIN_RISE_SPLIT_BY_WRITER_AND_BOOK_2026-10-01.md`
(landed `06fa922b7`, before either arm returned).

**Disposition of the draw's duplicate-work note.** "Already held under this very id" was this
draw's own write. No rival seat or `surgical_land` was working this id.

**Answer.** The +£7,331 is not value created. It is £9,154 more revenue taken from renewing
customers on exactly the same kWh. Almost all of it comes from the portfolio premium, now reading the
crisis losses it had been looking past. The world pushed back: three customers left on churn rolls
identical in both arms, and the 16 terms they took were profitable (−£1,235).

## Set-up

Arms: `old` = `65401d319` (parent of `cd0c7c39c`), `new` = `cd0c7c39c`. One default world each.
Script and data are in `/var/tmp/se-attr/` (`measure.py`, `compare.py`, `followup.py`). The partition
is by term key `customer|fuel|term_start`. It sums to ΔM exactly by construction, and it did.

## Pre-registered against what came back

| | prediction | result | |
|---|---|---|---|
| P0 | reproduce 319,176 / 316,175 records, 3,250 / 3,236 renewals, £122,754 / £130,085 | exact: £122,753.75 / £130,084.50, Δ +£7,330.75 | holds |
| P1 | matched first terms Δ = £0 | £0.00 on 244 terms | holds |
| P2 | (a) same-extent renewals ≥ +£4,000 and below the total | **+£8,565.44** on 2,953 renewals, which is more than the whole rise | **MISSED** |
| P3 | composition positive, +£1,000 to +£4,000 (the lost book was loss-making) | **−£1,234.69**: the lost book was profitable | **MISSED, sign** |
| P4 | `portfolio_premium` ≥ 70% of writer £ | £9,291 of £9,177 (101%) | holds |
| P5 | ≥ 60% of (a) on renewals starting 2021-07-01 to 2022-12-31 | £5,631 of £8,565 (66%) | holds |
| P6 | writer £ reconciles to Δnet on (a) within 10% | £9,177 against £8,565, residual −£611 (6.7%) | holds |

## The split

| channel | Δ net | Δ revenue | terms |
|---|---|---|---|
| (a) matched renewals, same extent | **+£8,565.44** | +£9,154.11 | 2,953 |
| (f) matched first terms | £0.00 | £0.00 | 244 |
| (b1) terms in the old arm only | **−£1,234.69** | −£5,006.24 | 16 |
| (b1) terms in the new arm only | £0.00 | | 0 |
| (b2) matched terms whose extent moved | £0.00 | | 0 |
| **total** | **+£7,330.75** | +£4,147.86 | |

Within (a), each writer's £ is the change in that writer's rate move × the term's kWh:

| writer | £ | renewals moved |
|---|---|---|
| `portfolio_premium` | +£9,291.26 | 1,367 |
| `profitability_uplift` | −£97.26 | 2 |
| `margin_surcharge` | −£71.16 | 238 |
| `price_cap` clamp | +£53.86 | 10 |
| struck rate | £0.00 | 0 |

kWh and standing charge are identical on every (a) term.

**The residual on (a)** is −£611: Δnet is £589 below Δrevenue, and wholesale cost fell £97.
`run_phase2b` charges bad debt as a fraction of revenue (`_bad_debt = revenue × world incidence`),
which fits the sign and size: about 7.5% of the extra revenue, which was weighted towards the crisis.
I did not log `bad_debt_gbp`, so this is the probable cause, not a measured one.

## Why the premium charged more

The earlier finding's untested story is now measured, using the per-call last-4 lookback the
original arms logged (`/var/tmp/se-pp/`). In 2021H2–2022 (550 renewals), the mean portfolio margin
rate the premium read went from **−0.091 with foresight to −0.235 without it**. The mean chain uplift
rose by 3.4 points. With foresight, the lookback was mostly terms that had just started; they would
run into the 2023 price fall, so they looked less bad than the crisis terms that had actually ended.
Read honestly, the margins were worse, so the premium charged more. 2024 goes the same way at a
smaller size (reading 0.291 → 0.230, uplift +1.8 points), and so does 2025 (0.214 → 0.179, +1.5).

## The book that left

There were 16 terms from three customers. The `roll` value is the same in both arms for each of them,
so common random numbers held; what moved was the probability.
- `SYN-2016-001`, 2019-01-01. The offer was £146.66 against £139.24/MWh, and p_retain went
  0.7309 → 0.7302 against a roll of 0.7306. That is a knife-edge, decided by the higher offer. The
  customer's six 2019–2020 terms went with it (−£215).
- `PROS-2022-0010` and `PROS-2022-0097`, both dual fuel, at their 2024 renewals. **The offer was
  identical in both arms.** p_churn rose 0.29 → 0.32 and 0.17 → 0.20. Their 2022 Q2/Q4 and 2023 Q1
  rates were higher under `new` (e.g. £568 against £469/MWh in 2022 Q4), so the churn hazard is
  carrying price history. Which term in `build_churn_risk` does this is not traced. Eight terms in
  2024–2025 (−£1,020).

## What this changes

- **Do not read the +6% as value created.** By the mission's two-sided test it is a transfer: the
  same energy at a higher price. It is also the correct consequence of removing foresight, because
  the company now prices off losses it has actually seen. The fix stands; the figure is not a gain.
- **The world can defeat this.** At a 3-point churn sensitivity it cost three customers and £1,235.
  That is a 13% give-back on £9,154 of extra revenue. The coupled-triad question is whether that
  price-to-churn response is the right size. The answer belongs to the churn model's evidence, not
  to this pair.
- **The 14% standing-charge feedback grew for the same reason.** The premium reads lower, honest
  margins, so it amplifies any margin loss more. That explains the direction of both misses in
  `SEAT_FINDING_WITHOUT_THE_LOOK_AHEAD_..._14_PERCENT_...`. Their sizes are not attributed here.
