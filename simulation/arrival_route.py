"""How a domestic account OPENS, and therefore which product it opens ON.

Roadmap item C6 (`docs/design/CHOICE_AND_CHANNEL_ROADMAP.md`) — *"Home moves. The third route onto
a variable tariff, and absent entirely. A move onto a deemed contract is a departure for the losing
supplier with a cause, an arrival for the gaining one that was never won, and the origin of a large
share of the SVT stock."* C6's own simplification is the one built here: **move rates conditioned on
tenure only.**

WHAT THIS QUANTITY IS, SAID BEFORE IT IS MEASURED
-------------------------------------------------
Not the share of the BOOK on a default tariff. That is a STOCK, it is published, it lives in
`tools/published_tariff_mix.py`, and `simulation/svt_product.py` forbids in terms reading it as an
input: *"the published year-by-year fixed/SVT split printed beside the result as a CHECK. Never an
input: if the split has to be set to land in range, the behaviour is wrong and setting it hides
that."* Nothing here imports it and `tests/architecture/test_switching_rate_commons.py` holds that.

The quantity here is a FLOW: **of the domestic accounts a supplier opens in year y, what share open
on the incumbent's default tariff rather than on a deal the household chose?** An account opens by
exactly one of two routes in this world's scope:

  - **a switch** — the household chose this supplier, which means it chose a PRODUCT, and a
    switcher switches to a deal. It arrives on a fixed term.
  - **a move-in** — the household took supply at a premises without agreeing terms, so a deemed
    contract arises automatically with the incumbent at default-tariff rates, cap-protected from
    January 2019. It arrives on the default tariff, and it was never won.
    (`docs/domain_artefact_library/scope_briefs/ADVISOR_SCOPE_BRIEF_CHANGE_OF_TENANCY_2026-08-07.md`:
    *"the moment a new occupier takes supply without agreeing terms, a deemed contract arises with
    the incumbent under the ~licence deemed-contract scheme, at deemed/SVT rates, cap-protected.
    There is no lawful gap"*.)

So the share is `m / (m + s)`, where `m` is move-ins per household-year and `s` is external changes
of supplier per account-year. Both are published; neither is chosen here.

WHY THE LABEL IS `svt` AND NOT `deemed`, WHICH LOOKS LIKE THE OBVIOUS ONE
-------------------------------------------------------------------------
This world's `deemed` product is out-of-contract spot + 20% — a GAP between contracts, which is what
`DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md` calls it and what the settlement path implements.
A real deemed contract is not priced that way: it is charged at the supplier's default-tariff rate
and has sat under the default tariff cap since January 2019. The product the record describes is the
one `simulation/svt_product.py` builds, so that is the one minted. Writing `deemed` here would put a
move-in on spot+20% for a decade, which the published cap forbids outright post-2019.

WHAT EACH PUBLISHED NUMBER COUNTS, BECAUSE THE RATIO IS ONLY A QUANTITY IF THEY AGREE
-------------------------------------------------------------------------------------
`m`  English Housing Survey 2024-25, Annex Tables 1.1 and 3.7. Households that moved INTO a tenure
     in the previous 12 months, over households in that tenure. One move = one account opened at the
     new premises with the incumbent supplier.
`s`  `docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json`, via
     `simulation.market_switching_propensity.published_departure_band`. External changes of supplier
     on a GB domestic electricity MPAN, over all GB domestic electricity accounts. One switch = one
     account opened with the gaining supplier.

Both are **account openings per account-year**, which is what makes the ratio a share. Two
mismatches are real and are declared rather than smoothed:

  1. `m` is ENGLAND and households (25.0m); `s` is GB and domestic electricity meter points (28.0m).
     England is ~84% of GB households and a household is ~one MPAN, so the two denominators differ
     by about 11% in coverage, not in kind. No correction is applied — inventing one would be a
     third number nobody published.
  2. `m` is a LOWER bound. Annex Table 3.7's per-tenure flows sum to 1.62m of the 1.8m households
     the same report says moved, because inter-tenure flows other than private-rent→owner-occupy are
     not broken out. The 0.18m shortfall is carried as a declared gap by
     `move_rate_reconciliation()` rather than distributed. A lower `m` gives a lower default-tariff
     arrival share, which UNDERSTATES this repair — the conservative direction.

AND IT IS A LOWER BOUND FOR A SECOND, LARGER REASON
----------------------------------------------------
There are three routes onto a default tariff and this module is one of them. Never-engaged and
rolled-off-a-fixed already exist in this world (`simulation/renewals.py`'s passive roll, C1b). C6 is
the missing third. So the share below is the share of arrivals on the default tariff **at the moment
of arrival**, and it is not, and must not be read as, the share of the book that ends up there.

R13. This is a BASELINE-world fidelity change. Its warrant is that the world's generated SVT share
is BELOW the published one in every comparable year and worst at 2016, where it is 0.0% against a
published 66–74% — and `docs/market_research/gb_domestic_default_tariff_share_2016_2025.md` §4 names
this exact absence as the cause: *"home-move-onto-incumbent does not exist in this world"*. The
direction of the repair was therefore known before it was built and is not claimed as a blind
prediction. What was NOT chosen to land anywhere is the MAGNITUDE: it falls out of two published
rates and a ratio, and no endpoint of it was compared against the SVT check before it was written.
Where the switching band gives a range, the HIGH end is taken, which gives the SMALLEST default
arrival share — the same anti-flattering tie-break `published_departure_band`'s own docstring
records.

REUSE
-----
REUSE: simulation/arrival_route.py
CLASS: CUSTOM
INDEX: searched "arrival route", "home move", "deemed", "tariff type", "default tariff", "tenure",
       "acquisition", "switching rate", "published share".
       `simulation/market_switching_propensity.py` holds `s` and is IMPORTED rather than extended:
       its subject is DEPARTURE (a supplier losing an account) and this module's is ARRIVAL. Folding
       an opening rate into a module whose every other reading is a loss would give it two subjects.
       `simulation/household_segments.py` holds `TENURE_POPULATION_SHARE` and `tenure_for_customer`
       and is IMPORTED for the tenure spine rather than extended: it is the household's persistent
       traits, and a move RATE is a property of the housing market, not of the household.
       `tools/published_tariff_mix.py` is the nearest published row and is deliberately NOT imported
       — it is the CHECK on this module's output, and importing it would put the judge inside the
       thing judged. See the second paragraph.
       `simulation/svt_product.py` holds the PRODUCT this module routes an arrival onto, and is
       imported for its label constant only.
"""
from __future__ import annotations

from typing import Optional

from simulation.household_segments import TenureType
from simulation.svt_product import SVT_TARIFF_TYPE

#: English Housing Survey 2024-25, Chapter 1 / Annex Table 1.1 (MHCLG, fetched 2026-09-19):
#: 25.0m households in England — owner occupied 16.2m (65%), private rented 4.7m (19%), social
#: rented 4.1m (16%). Same edition as the move flows below, deliberately: a rate whose numerator
#: and denominator come from different survey years is two publications differenced.
EHS_HOUSEHOLDS_BY_TENURE_MILLIONS: dict[TenureType, float] = {
    TenureType.OWNER_OCCUPIER: 16.2,
    TenureType.PRIVATE_RENTER: 4.7,
    TenureType.SOCIAL_RENTER: 4.1,
}

#: English Housing Survey 2024-25, Chapter 3 "Housing history and future housing" / Annex Table 3.7
#: (MHCLG, fetched 2026-09-19). Households that moved INTO each tenure in the previous 12 months:
#:   owner occupied  354k within tenure + 66k new households + 191k in from private rent  = 611k
#:   private rented  640k within tenure + 182k new households                             = 822k
#:   social rented   149k within tenure +  40k new households                              = 189k
#: These are the flows the report breaks out. They sum to 1.622m against the same report's headline
#: 1.8m movers; `move_rate_reconciliation()` carries the difference as a declared gap.
EHS_MOVES_INTO_TENURE_MILLIONS: dict[TenureType, float] = {
    TenureType.OWNER_OCCUPIER: 0.611,
    TenureType.PRIVATE_RENTER: 0.822,
    TenureType.SOCIAL_RENTER: 0.189,
}

#: English Housing Survey 2024-25, Chapter 3: *"approximately 1.8 million households moved home in
#: the previous 12 months"*. Held only so the per-tenure flows can be reconciled against the
#: publisher's own headline rather than summed and trusted.
EHS_TOTAL_MOVERS_MILLIONS = 1.8

#: The product a move-in opens on. Not a choice made here — see the module docstring's second
#: section. `simulation/svt_product.py` owns the product itself.
ARRIVAL_DEFAULT_TARIFF_TYPE = SVT_TARIFF_TYPE


def home_move_rate_per_household_year(tenure: TenureType) -> float:
    """Move-ins into `tenure` per household-year in `tenure`, EHS 2024-25.

    ~3.8% owner-occupier, ~17.5% private renter, ~4.6% social renter. The spread is the whole point
    of conditioning on tenure and it is the direction C6 predicted in prose before this was
    computed: *"renters move several times more often than owners."*
    """
    return (
        EHS_MOVES_INTO_TENURE_MILLIONS[tenure] / EHS_HOUSEHOLDS_BY_TENURE_MILLIONS[tenure]
    )


def move_rate_reconciliation() -> dict:
    """The per-tenure flows against the publisher's own headline, as a number rather than a claim.

    Exists because the shortfall is the honest weakness of this anchor and a docstring saying so
    rots. A reader — or a control — can see how much of the published move volume this module
    actually carries.
    """
    carried = sum(EHS_MOVES_INTO_TENURE_MILLIONS.values())
    return {
        "carried_millions": round(carried, 4),
        "published_headline_millions": EHS_TOTAL_MOVERS_MILLIONS,
        "uncarried_millions": round(EHS_TOTAL_MOVERS_MILLIONS - carried, 4),
        "share_of_published_carried": round(carried / EHS_TOTAL_MOVERS_MILLIONS, 4),
        "why_uncarried": (
            "Annex Table 3.7 breaks out within-tenure moves, newly formed households and the "
            "private-rent -> owner-occupy flow. The remaining inter-tenure flows are not published "
            "separately. They are NOT distributed across the three tenures: doing so would invent a "
            "split the survey does not report, and leaving them out biases the arrival share DOWN, "
            "which understates this repair rather than flattering it."
        ),
    }


def default_tariff_arrival_share(year: int, tenure: TenureType) -> Optional[float]:
    """Share of accounts opened in `year` by a household of `tenure` that open on the default
    tariff, `m / (m + s)`. `None` when the published switching record has no band for `year`.

    `None` is a result and consumers must fail closed on it — an arrival in a year the record cannot
    speak for gets no product, the same honest silence the drawn book carried before C6.
    """
    from simulation.market_switching_propensity import published_departure_band

    band = published_departure_band().get(int(year))
    if band is None:
        return None
    # The HIGH end of the switching band, which is the LOW end of this share. Same anti-flattering
    # tie-break `published_departure_band`'s docstring records for the world's own level.
    switch_rate = float(band[1]) / 100.0
    move_rate = home_move_rate_per_household_year(tenure)
    denominator = move_rate + switch_rate
    if denominator <= 0.0:
        return None
    return move_rate / denominator


def arrival_tariff_type(roll: float, year: int, tenure: TenureType) -> Optional[str]:
    """`"svt"` if this arrival opened on a deemed contract, else `None`.

    `None` is NOT "fixed". `DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md` refused labelling the
    unlabelled remainder, and nothing here changes that: the published record establishes what a
    MOVE-IN opens on (a deemed contract, by operation of the licence) and establishes nothing about
    what the rest of a drawn book opens on. Only the arrivals whose product is settled by law get
    one. The remainder keeps its honest silence, and that silence is still the thing the company's
    `UPLIFTABLE_TARIFF_TYPES` guard refuses.

    `roll` is supplied by the caller from its own named RNG substream so this module holds no
    generator and cannot perturb any draw sequence.
    """
    share = default_tariff_arrival_share(year, tenure)
    if share is None:
        return None
    return ARRIVAL_DEFAULT_TARIFF_TYPE if roll < share else None
