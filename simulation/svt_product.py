"""The world's standard variable product: a price that changes on a calendar, not at a renewal.

WHY THIS EXISTS
---------------
`docs/design/DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md` (2026-08-28) ruled that the
drawn book's silent `tariff_type` is a fidelity defect, that setting it to `fixed` is refused,
and that *"what is owed is a standard-variable product the world does not have."* This is that
product. The brief of 2026-08-30 restates it as WORK item 4, with the added requirement that it
be **generated from behaviour** and that the published split be a check on the output rather
than an input.

The world could settle exactly four products before this — `fixed`, `flex`, `deemed`,
`pass_through` — and none of them is a standard variable tariff. `deemed` comes closest and is
not it: it is out-of-contract spot + 20%, a gap BETWEEN contracts, priced as a penalty and
lasting days. An SVT is where two thirds of a real domestic book LIVES, for years, at a
published price.

WHAT MAKES IT A DIFFERENT PRODUCT AND NOT A DIFFERENT LABEL
-----------------------------------------------------------
Three properties, and each one is a thing a fixed term has that this does not:

  1. **No locked unit rate.** The rate is the published Ofgem default-tariff cap for the period,
     read from `simulation.svt_rates`. It changes when the cap changes and the household is not
     consulted. `build_renewal_schedule` locks `prev_fixed_unit_rate` for everything that is not
     `flex`; an SVT account never reaches that line because it never goes through that builder's
     loop at all.
  2. **No term boundary.** The segments below are CAP PERIODS, not contracts. A segment ending
     is a price change, not an expiry: nothing is renewed, nothing is offered, and the household
     makes no decision. That is why `run_phase2b` treats `svt` as an indexed tariff alongside
     `deemed` and `flex` — the renewal decision is gated out at exactly the same seam.
  3. **No renewal notice.** `notice_date` equals the segment start because there is nothing to
     give notice of. The 42-day notice a fixed term carries (`NOTICE_DAYS`) is a contractual
     artefact of a term ending.

WHY THE SEGMENTS ARE QUARTERS
-----------------------------
Not a modelling choice — it is the shape of the published series. `simulation/svt_rates.py` is
keyed on `(year, quarter_start_month)` with quarter starts at January, April, July and October,
and each period's rate holds until the next begins. Segmenting on anything else would either
average across a cap change or invent detail the anchor does not carry.

Before 2019 there was no cap and the series holds a supplier-set midpoint with a stated ±15%
band. The segmentation is the same; only the confidence in the number differs, and that is the
anchor's own caveat, not this module's.

WHAT THIS DELIBERATELY DOES NOT DO YET, AND WHY NO ACCOUNT IS ASSIGNED TO IT
---------------------------------------------------------------------------
**An account on this product cannot currently leave.** The renewal decision is the only place
`run_phase2b` rolls for a departure, and this product correctly has no renewal decision. So a
household moved onto SVT today would become immortal, and a book of immortal households earns
more than a real one.

That is a change in the company's favour, made blind to nothing, and R13 forbids it. **So the
product exists and settles, and nothing is assigned to it.** `build_renewal_schedule` routes
here only for a customer record that says `tariff_type: "svt"`, and no roster writes that
value — which `test_svt_product.py::test_no_account_is_on_the_svt_product_yet` asserts, so the
day someone assigns one, the control that says the inertia hazard is missing fires first.

What is owed before assignment, in order:
  * an **inertia hazard** — the published SVT churn rate is roughly 10–15%/yr and the world
    already holds the anchored figure as `renewal_engagement.PASSIVE_CHURN_CAP = 0.10`, the
    ceiling on a passive roller's realised churn. Converted to a per-segment hazard it is
    `1 - (1 - 0.10) ** 0.25 = 0.0260` a quarter, which recomposes to 0.100 over four. A
    departure from SVT has no term structure and must be able to land in any quarter.
  * **assignment generated from behaviour**: never engaged; a fixed term ended and the household
    did not act; or a home move onto the incumbent. The third does not exist in the world at all
    (`docs/design/CHOICE_AND_CHANNEL_ROADMAP.md`, C6), so the generated SVT share will come out
    LOW against the published one — the direction that leaves more of the book priceable than
    reality would, and therefore an upper bound on the company's honest in-scope surface.
  * the **published year-by-year fixed/SVT split** printed beside the result as a CHECK. Never
    an input: if the split has to be set to land in range, the behaviour is wrong and setting it
    hides that.

REUSE
-----
REUSE: simulation/svt_product.py
CLASS: CUSTOM
INDEX: searched "svt", "standard variable", "variable tariff", "default tariff", "cap",
       "indexed", "deemed", "schedule".
       `simulation/svt_rates.py` owns the published rate series and is IMPORTED, never
       re-anchored — it is the anchor and the ceiling, and a second series for "what the cap
       is" would be one name and two numbers. It is a calendar table and cannot be a product by
       itself, which is the whole reason this module exists.
       `simulation/renewals.build_renewal_schedule` builds CONTRACT terms — it prices each term
       through `request_renewal_offer`, gives every term a 42-day notice date and locks
       `prev_fixed_unit_rate`. All three are properties of a contract ending, and all three are
       wrong for a product that never ends. Extending it with a fourth `tariff_type` branch
       would have put a no-renewal product inside a loop whose every line assumes a renewal;
       instead it DELEGATES here on one condition, which is the smaller change to that file.
       `simulation/renewals.py`'s own `deemed` branch is the nearest working analogue and was
       read closely: same "no offer, no notice, calendar-priced" shape, different economics
       (spot + premium, days long, a penalty) and it is emitted INSIDE the term loop as a gap
       between contracts, so it cannot carry a product that replaces the contract.
       `simulation/renewal_engagement.PASSIVE_CHURN_CAP` is the anchored inertia figure and is
       cited above rather than copied, because the hazard that consumes it is not built here.
"""

from __future__ import annotations

from datetime import date, timedelta

from sim.forward_curve import generate_forward_price
from simulation.svt_rates import get_svt_elec_rate_gbp_per_mwh

#: Cap-period starts, straight off `simulation/svt_rates.py`'s own key structure. Named here
#: rather than imported because that module keeps it private; the duplication is one tuple and
#: `test_the_segment_starts_match_the_published_series` fails if the two ever disagree.
CAP_PERIOD_START_MONTHS: tuple[int, ...] = (1, 4, 7, 10)

#: What the world calls this product wherever a `tariff_type` is read.
SVT_TARIFF_TYPE = "svt"


def _next_cap_period_start(day: date) -> date:
    """The first cap-period start strictly after `day`."""
    for month in CAP_PERIOD_START_MONTHS:
        if month > day.month:
            return date(day.year, month, 1)
    return date(day.year + 1, CAP_PERIOD_START_MONTHS[0], 1)


def build_svt_schedule(
    customer_id: str,
    original_acquisition_date: str,
    report_end_date: str,
    price_records: list[dict],
    lookback_temps_fn=None,
) -> list[dict]:
    """One segment per cap period from acquisition to report end, priced at the published rate.

    Shaped exactly like the term dicts `simulation.settlement.run_settlement` expects, so a
    schedule from here is interchangeable with one from `build_renewal_schedule` at every
    downstream reader. The differences a reader can see are all in the VALUES:

      * `tariff_type` is `"svt"`, which `run_phase2b` treats as indexed — no renewal decision.
      * `notice_date` equals the segment start; there is nothing to give notice of.
      * `unit_rate_gbp_per_mwh` is the published cap rate for the period, not a struck price.
        No company module is asked to price it, because no supplier prices a capped default
        tariff — it is handed the number.

    The first segment starts on the acquisition date rather than on a cap boundary, so a
    household that arrives mid-quarter is billed from the day it arrived at the rate then in
    force. Every subsequent segment starts on a boundary.

    `price_records` and `lookback_temps_fn` are used only for the SIM's own forward-price
    estimate, which settlement needs for margin and hedging and which is not a price offered to
    anybody. The signature deliberately does NOT take `eac_kwh` or `segment`: neither can change
    a capped rate, and taking them would invite a future edit that lets them.
    """
    segment_start = date.fromisoformat(original_acquisition_date)
    report_end = date.fromisoformat(report_end_date)
    segments: list[dict] = []

    while segment_start <= report_end:
        segment_start_str = segment_start.isoformat()
        next_start = _next_cap_period_start(segment_start)
        segment_end = min(next_start, report_end + timedelta(days=1))

        rate = get_svt_elec_rate_gbp_per_mwh(segment_start_str)
        lookback_temps = (
            lookback_temps_fn(segment_start_str) if lookback_temps_fn else None
        )
        sim_fwd = generate_forward_price(
            segment_start_str, price_records, lookback_daily_mean_temps_c=lookback_temps
        )
        segments.append({
            "customer_id": customer_id,
            "acquisition_date": segment_start_str,
            # NO NOTICE. A fixed term carries `term_start - NOTICE_DAYS` because a contract is
            # ending and the supplier must say so. Nothing is ending here.
            "notice_date": segment_start_str,
            "unit_rate_gbp_per_mwh": rate,
            "forward_price_gbp_per_mwh": sim_fwd,
            # The company did not price this and is not asked to. Handing it the SIM's own
            # forward keeps the settlement arithmetic whole without inventing a company belief
            # about a number the company never formed one about.
            "company_forward_price_gbp_per_mwh": sim_fwd,
            "tariff_type": SVT_TARIFF_TYPE,
            "term_end": segment_end.isoformat(),
        })
        segment_start = next_start

    return segments
