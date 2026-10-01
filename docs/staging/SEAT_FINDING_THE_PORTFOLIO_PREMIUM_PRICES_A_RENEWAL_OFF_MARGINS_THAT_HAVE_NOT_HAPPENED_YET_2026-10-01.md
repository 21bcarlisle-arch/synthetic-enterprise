**Severity:** BLOCKING · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing` — Lane 0 delivery

# The portfolio premium prices a renewal off margins that have not happened yet

Found 2026-10-01 by a missed pre-registered prediction (P1 in
`done/SEAT_FINDING_THE_2025_STANDING_CHARGE_IS_TABLED_FROM_THE_CAP_MODEL_2026-10-01.md`). This is an
**epistemic-wall** defect: the company reads something no real supplier could know at the moment
it prices.

## The evidence

The only change was the world's **2025** standing-charge rows. These are read only by
`hedged_settlement` and `gas_settlement`, and only for 2025 dates. Every standing charge before 2025
was identical between the two arms. Yet 12 account-term-years in **2024** moved unit revenue. All of
them were renewals that started 2024-07-01 or 2024-10-01 (net +£0.53). A renewal priced in mid-2024
reacted to settlement that happened in 2025.

## The mechanism (read from the code; not separately measured)

- `simulation/run_phase2b.py` walks `all_terms` in term-START order.
- Each term is settled **to its end** inside its own iteration.
- At about line 3377, the term's realised margin rate is appended to `portfolio_elec_margin_rates`
  or `portfolio_gas_margin_rates` straight away.
- A later iteration (a renewal starting later) passes that list to `decide_renewal_rate`, and
  `portfolio_position` takes the last `PORTFOLIO_PREMIUM_LOOKBACK` entries. That constant (4, in
  `company/pricing/tariff_engine.py`) is commented "last N **completed** electricity terms", so the
  intended reading was always as-of.

So a term that started in February 2024 and settles to February 2025 contributes its whole-term
margin to a renewal priced in July 2024. The list carries no dates, so nothing downstream can
bound it as-of. The other learned writers are bounded:
- `renewal_unit_rate_uplift` filters `settled_records` as-of `term_start`.
- `margin_surcharge` reads the same account's previous term, which ended before this one began.

The 12% attribution (`SEAT_FINDING_THE_12_PERCENT_IS_...`) puts £1,040 of £1,356 through this
writer. **That figure measured a real channel, but part of what it carries is foresight.**

## What it is not yet

**The magnitude is unmeasured.** It is the share of lookback entries, at each renewal, that come
from terms which had not ended by that renewal's start. It is also the premium difference against an
as-of-bounded list. Until that is measured, every published renewal rate, margin and value-arm
figure downstream of the portfolio premium carries an unbounded look-ahead. That is why this is
BLOCKING and not LATENT.

## The remedy, proposed and not done here

Append a term's margin rate when the term ENDS, not when it is settled. Keep a pending queue keyed
by term end date, and drain it into the list for every term that ended on or before the reading
renewal's `term_start`. The append site and the read site both stay in the world. The company side
(`portfolio_position`) is unchanged, so the seam is untouched.

The fix needs its own pre-registered pair of runs, because it moves every renewal's premium. It is
handed on as the next item.
