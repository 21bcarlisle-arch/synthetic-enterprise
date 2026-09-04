"""What the published record can and cannot bear about the SVT and fixed routes, with no world in it.

Opened by `docs/staging/SEAT_FINDING_THE_LEVEL_IS_CLAMPED_AND_THE_MECHANISM_UNDER_IT_IS_
COMPRESSED_NOT_MISDIRECTED_2026-09-03.md` §11.
Pre-registration: `docs/staging/SEAT_PREREGISTRATION_WHETHER_THE_PUBLISHED_SEGMENT_RATES_COMPOSE_
TO_THE_PUBLISHED_BAND_2026-09-04.md`.

THE QUESTION THIS ANSWERS, AND THE ONE IT REFUSES TO
-----------------------------------------------------
§9 of the finding put the world's departure shortfall onto a single quantity -- the hazard per
SVT-account-year -- and measured the gap at 1.67x and 1.71x against the world's own published source
in the two years the world runs that source to within 4%. It closed by asking whether
`SVT_INERTIA_ANNUAL_RECENT = 0.20` is the right published quantity at all, *"because the hazard is
drift off the SVT product and the band it is being asked to reproduce is external change of
supplier"*.

That question has a form settleable from published evidence alone. The record publishes three things
that must be mutually consistent, and this module composes them:

    R(y)  =  s(y) * H_svt(y)  +  (1 - s(y)) * H_fixed(y)

  R      GB domestic ELECTRICITY changes of supplier over ALL GB domestic electricity accounts.
         `simulation.market_switching_propensity.published_departure_band`, off the regulation
         commons, whose own numerator field says in terms: *"NOT tariff switches within the same
         supplier, which Ofgem's survey instruments do count and which are a different quantity."*
  s      share of GB domestic accounts on a default/SVT tariff. `tools.published_tariff_mix`, two
         declared bases, an explicit `None` at 2020 and 2021.
  H_svt  external changes of supplier per SVT-account-year.
  H_fix  external changes of supplier per fixed-tariff-account-year.

ONE EQUATION, TWO UNKNOWNS, SO THE RECORD ADMITS A LINE AND NOT A POINT. That is the whole result
and it is why this module publishes an interval everywhere a lesser reading would publish a number.
`admissible_svt_churn` is that line's projection onto `H_svt`, and it is wide.

THE ASYMMETRY THAT MAKES THE LINE WIDE, AND IT IS A DEFINITION PROBLEM AND NOT A DATA ONE
-------------------------------------------------------------------------------------------
`H_fixed` IS NOT 0.35. `svt_rates_active_passive_2016_2025.md` §4 publishes ~35% for *"fixed at
expiry -> active switch"*, and that row counts households who **actively renew onto a new fixed
deal**. A household that picks a new fixed deal *with its existing supplier* has made an internal
tariff move, which the published numerator above explicitly does not count. So

    H_fixed  =  FIXED_ACTIVE_RENEWAL_SHARE * phi

where **phi is the external share of active fixed-term renewals**, and `EXTERNAL_SHARE_OF_ACTIVE_
RENEWALS` below is `None` because nothing published establishes it. That `None` is the deliverable.
`gb_switching_rate_denominators.md` §7 already records the same instrument failing on the adjacent
question -- Ofgem's CIM wave 6 has the larger base and is *further* from what is needed, *"because
its population includes internal tariff switches"*. The quantity is one survey cross-tabulation away
and it is not published.

WHY THIS IS A SEPARATE MODULE FROM THE READINGS IT SITS BESIDE
---------------------------------------------------------------
§8, §9 and §10's readings live in `tools/fit_year_level_anchor.py` and every one of them takes a
captured run as its subject. This one has no subject in the world at all: it is three published
series composed against each other, and its verdict must stay true whatever the world does. Putting
it in a module whose every other function opens a capture would make that property a convention
instead of a fact. The single place it does look at the world is
`where_the_worlds_point_falls`, which reads the COMMITTED artefact `svt_route_shortfall_
decomposition.json` rather than the capture, is labelled, and returns a declared `None` if that file
is absent rather than crashing the published reading that does not need it.

REUSE
-----
REUSE: tools/published_route_split.py
CLASS: CUSTOM
INDEX: searched "route split", "published band", "segment churn", "svt churn", "composition",
       "admissible", "feasible", "tariff mix", "switching rate", "commons".
       `tools/published_tariff_mix.py` is the nearest row and is IMPORTED rather than extended: it
       is the one home for the tariff MIX and the segment churn rates are not the mix -- folding
       them in would give that module two subjects and the next session no way to tell which of them
       a caller wanted.
       `tools/fit_year_level_anchor.py` holds the three readings this one follows and is deliberately
       not extended, for the reason in the paragraph above.
       `simulation/departure_risks.py` holds `SVT_INERTIA_ANNUAL_RECENT`/`_LONG_STAYER`, which are
       the TOP of each published band clipped to a point and wired as world INPUTS. A check that
       imported them would be measuring the world against the world's own choice of where to sit
       inside the evidence. The bands are re-declared here from the same source section, and
       `test_the_published_route_split_does_not_read_the_worlds_clipped_constants` holds that.
"""
from __future__ import annotations

import itertools
import json
import sys
from dataclasses import dataclass
from pathlib import Path

from simulation.market_switching_propensity import published_departure_band
from tools.published_tariff_mix import (
    default_tariff_share,
    fixed_share,
    years_with_an_established_figure,
)

PROJECT = Path(__file__).resolve().parent.parent
ARTEFACT = PROJECT / "docs" / "reports" / "published_route_split.json"
#: The world reading this is compared against. Read as a committed artefact, never re-derived.
SHORTFALL_ARTEFACT = PROJECT / "docs" / "reports" / "svt_route_shortfall_decomposition.json"

#: `svt_rates_active_passive_2016_2025.md` §4, both rows, AS BANDS. The source labels every row a
#: STRUCTURAL INFERENCE at confidence M and says in terms that *"direct published SVT vs fixed churn
#: rates by tariff type are not available"*. The bands are carried whole here because the world's
#: `SVT_INERTIA_ANNUAL_RECENT = 0.20` is the TOP of the first one, chosen under the director's
#: anti-flattering tie-break -- a defensible world choice and an inadmissible one for a check.
SVT_CHURN_RECENT = (0.15, 0.20)
SVT_CHURN_LONG_STAYER = (0.05, 0.10)

@dataclass(frozen=True)
class TenureObservation:
    """One published observation of the SVT segment's tenure split, with its instrument named.

    THE FIELD THAT EARNS THIS A DATACLASS IS `population`. The two observations in the register are
    NOT the same measurement taken twice: one is a consumer survey over all domestic customers and
    one is supplier-returned stock over non-prepayment accounts. A bare pair of percentages would
    let the next reader difference them as a trend, and they are not a trend.
    """

    year: int
    long_stayer_pct: float
    recent_pct: float
    instrument: str
    population: str
    source: str
    #: Which way restoring the population's exclusions would move `long_stayer_share`, or "" when
    #: nothing is excluded. NEVER a correction factor: the correction is not established and a
    #: number here would be read as one. The DIRECTION is established and it is what bounds.
    restoring_the_excluded_moves_the_long_stayer_share: str

    @property
    def long_stayer_share(self) -> float:
        """The long-stayer share WITHIN the SVT segment, which is what composes the segment band.

        Both observations publish their two rows over the whole account base, so the segment share
        is the ratio and not the first figure -- reading 0.203 off the 2025 row would be composing
        the segment band with the share of ALL accounts that are long-stayer defaulters.
        """
        return self.long_stayer_pct / (self.long_stayer_pct + self.recent_pct)


#: EVERY published observation of this quantity that the tree holds, and the register exists because
#: §13 of the finding asked for a second one and it was already here -- in `ASSUMPTIONS.md` L176 and
#: in `continuous_behavioural_engagement_w2_14.md` §1a, cited and dated, load-bearing for the R13
#: ruling since 2026-07-22. That is this repository's VAT shape a fourth time in one chain, so the
#: fix is the same structural one `published_tariff_mix` applied to the share series: ONE home.
#:
#: The two disagree by 19 points of within-segment share, which is the finding. The 2018 row is
#: retained as the historical one and is NOT replaced: a register that overwrote it would lose the
#: disagreement, and the disagreement is the whole result.
SVT_TENURE_OBSERVATIONS: tuple[TenureObservation, ...] = (
    TenureObservation(
        year=2018,
        long_stayer_pct=29.0,
        recent_pct=23.0,
        instrument="consumer survey, self-reported tariff type and tenure",
        population="GB domestic customers, prepayment included",
        source="Ofgem Consumer Engagement Survey 2018, via "
               "docs/market_research/svt_rates_active_passive_2016_2025.md §2",
        restoring_the_excluded_moves_the_long_stayer_share="",
    ),
    TenureObservation(
        year=2025,
        long_stayer_pct=20.3,
        recent_pct=34.6,
        instrument="supplier-returned administrative stock",
        population="GB domestic ELECTRICITY accounts, NON-PREPAYMENT",
        source="Ofgem Retail Market Indicators data portal, default-tariff panel, October 2025 "
               "stock, fetched 2026-07-08; carried in docs/market_research/ASSUMPTIONS.md L176 "
               "and cross-validated in continuous_behavioural_engagement_w2_14.md §1a",
        # `published_tariff_mix` establishes both halves: prepayment is ~15% of domestic accounts
        # and >90% of it is on a default tariff, and it is the segment least likely to have moved
        # tariff recently. So the excluded population is disproportionately long-stayer DEFAULT and
        # restoring it can only raise this share -- toward 2018's, never away from it. 0.3698 is
        # therefore a LOWER BOUND, and every verdict below is also taken at `observed_mix_hull`,
        # which contains every mix between the two observations whatever the true correction is.
        restoring_the_excluded_moves_the_long_stayer_share="up, toward the 2018 observation",
    ),
)

#: The observation the ORIGINAL reading composed with, kept named so the sections §13 published at
#: it stay identifiable. `tenure_composed` is still this one and still means 2018.
_HISTORICAL_OBSERVATION = SVT_TENURE_OBSERVATIONS[0]

#: `svt_rates_active_passive_2016_2025.md` §4: *"Fixed at expiry -> active switch ~35%"*.
#: THIS IS NOT A CHANGE-OF-SUPPLIER RATE. It counts households who actively renew onto a new fixed
#: deal, of whom an unestablished share stay with the same supplier. See the module docstring.
FIXED_ACTIVE_RENEWAL_SHARE = 0.35

#: The external share of active fixed-term renewals. **UNESTABLISHED, AND THAT IS THE FINDING.**
#: A `None` with a named reason cannot be read as evidence and a 0.5 written here could be. Every
#: function below that would need it takes it as an argument and sweeps it instead.
#:
#: WHAT WOULD CLOSE IT: a domestic instrument that separates "switched supplier" from "switched
#: tariff with the same supplier" on the same base. Ofgem's Consumer Impacts of Market Conditions
#: survey fields both events and publishes them combined; the cross-tabulation exists in the
#: underlying data tables and was not reachable this pass.
EXTERNAL_SHARE_OF_ACTIVE_RENEWALS: float | None = None


@dataclass(frozen=True)
class SwitcherSplitObservation:
    """One CIM wave's split of reported switching into external and internal, on ONE base.

    THE FIELD THAT EARNS THIS A DATACLASS IS `recall_window_years`. Every other register in this
    module is keyed by the year it describes; this one is not, because a six-month recall window
    asked in January straddles two calendar years and the published default-tariff share moves
    between them. A bare `year` would have forced a choice nothing establishes, so the window is
    carried whole and every verdict below is taken at the MOST GENEROUS year the window touches.

    Counts are the published WEIGHTED counts, rounded to 4dp from the data-table cells. Shares are
    derived and never stored: `net` is the survey's own union of the two actions and is NOT their
    sum in W1, so a stored share would silently pick one denominator and lose that.
    """

    wave: int
    fieldwork: str
    recall_window_years: tuple[int, ...]
    base_unweighted: int
    base_weighted: float
    #: "I/we have switched to a new supplier"
    external_weighted: float
    #: "I/we have switched tariff with the same supplier"
    internal_weighted: float
    #: The table's own "Net: Have switched". The UNION, so it is <= the sum when a respondent
    #: reported both. Held rather than derived because the overlap is the thing worth seeing.
    net_switched_weighted: float

    @property
    def external_share_of_switching(self) -> float:
        """`phi_survey` -- external over ALL reported switching. NOT `phi`; see the reading."""
        return self.external_weighted / self.net_switched_weighted

    @property
    def internal_rate_of_all_households(self) -> float:
        """Internal switches per household over the RECALL WINDOW. Deliberately not annualised.

        Annualising would only raise it, and every verdict this feeds is of the form "internal
        switching already EXCEEDS a ceiling". Taking the un-annualised six-month rate is therefore
        the conservative direction, and it means no annualisation convention is load-bearing.
        """
        return self.internal_weighted / self.base_weighted

    @property
    def both_actions_overlap(self) -> float:
        """Weighted respondents reporting BOTH actions: the sum less the published union."""
        return self.external_weighted + self.internal_weighted - self.net_switched_weighted


#: Ofgem's Consumer Impacts of Market Conditions survey, question C4 -- *"Which, if any, of these
#: have you or your household done IN THE PAST 6 MONTHS?"*, base all respondents, with **"switched
#: to a new supplier" and "switched tariff with the same supplier" as separate response options on
#: the same base**. This is the instrument §11 of the finding asked for and §14 restated as the only
#: thing the chain still owed, and it is REPORTED BEHAVIOUR rather than intention.
#:
#: Source: wave 6 data tables, Table 108 (`W2W Tables`), which carries all six waves in one banner.
#: `docs/market_research/gb_domestic_switcher_split_cim_2022_2025.md` holds the provenance.
#:
#: WHY THIS DOES NOT CLOSE `EXTERNAL_SHARE_OF_ACTIVE_RENEWALS`, stated at the register rather than
#: only in the reading, because the register is what a future session will reach for first: the base
#: is ALL HOUSEHOLDS, so both response options mix the SVT route and the fixed-renewal route. The
#: survey adds one equation and one unknown (the rate at which SVT households move internally) and
#: an equation that arrives with its own unknown identifies nothing.
SWITCHER_SPLIT_OBSERVATIONS: tuple[SwitcherSplitObservation, ...] = (
    SwitcherSplitObservation(
        wave=1, fieldwork="March 2022", recall_window_years=(2021, 2022),
        base_unweighted=2944, base_weighted=2873.6930,
        external_weighted=267.9529, internal_weighted=378.7993,
        net_switched_weighted=632.3701,
    ),
    SwitcherSplitObservation(
        wave=2, fieldwork="July 2022", recall_window_years=(2022,),
        base_unweighted=2984, base_weighted=2954.5042,
        external_weighted=245.1449, internal_weighted=368.6360,
        net_switched_weighted=613.7809,
    ),
    SwitcherSplitObservation(
        wave=3, fieldwork="November/December 2022", recall_window_years=(2022,),
        base_unweighted=3457, base_weighted=3456.9999,
        external_weighted=252.4255, internal_weighted=500.8593,
        net_switched_weighted=753.2848,
    ),
    SwitcherSplitObservation(
        wave=4, fieldwork="July 2023", recall_window_years=(2023,),
        base_unweighted=3434, base_weighted=3434.0000,
        external_weighted=157.8359, internal_weighted=379.2057,
        net_switched_weighted=537.0416,
    ),
    SwitcherSplitObservation(
        wave=5, fieldwork="January 2024", recall_window_years=(2023, 2024),
        base_unweighted=3439, base_weighted=3439.0000,
        external_weighted=191.9714, internal_weighted=398.4467,
        net_switched_weighted=590.4181,
    ),
    SwitcherSplitObservation(
        wave=6, fieldwork="January/February 2025", recall_window_years=(2024, 2025),
        base_unweighted=3458, base_weighted=3458.0000,
        external_weighted=182.8863, internal_weighted=588.5251,
        net_switched_weighted=771.4115,
    ),
)

BASES = ("as_published", "all_domestic")


def compose_at_mix(long_share: float) -> tuple[float, float]:
    """The SVT segment's external churn band at a named within-segment long-stayer share.

    A FREE FUNCTION AND NOT A CLOSURE OVER THE REGISTER, so a control can hand it a mix nobody
    observed and check the composition is monotone -- the property that makes `observed_mix_hull`
    a hull rather than a pair of unrelated bands.
    """
    return tuple(  # type: ignore[return-value]
        round(long_share * long_end + (1.0 - long_share) * recent_end, 6)
        for long_end, recent_end in (
            (SVT_CHURN_LONG_STAYER[0], SVT_CHURN_RECENT[0]),
            (SVT_CHURN_LONG_STAYER[1], SVT_CHURN_RECENT[1]),
        )
    )


def svt_segment_churn_band() -> dict[str, tuple[float, float]]:
    """The published SVT segment's external churn band, at each observed mix and mix-free.

    `tenure_composed` weights the two published rows by the 2018 survey's tenure split. It is what
    §11-§13 read, it is retained under its original name and value, and it rests on one survey year.

    `mix_free_envelope` is `(min of the low ends, max of the high ends)` -- the value the segment
    could take under ANY tenure mix, including mixes nobody has measured. It is strictly wider and
    it is what a verdict has to survive to be a verdict about the record rather than about 2018.

    `tenure_composed_2025` is the same composition at the SECOND observation, and
    `observed_mix_hull` is the hull of every mix BETWEEN the two -- which is the band a verdict has
    to survive to be a verdict about mixes anything has actually seen. It sits strictly inside
    `mix_free_envelope`, and the gap between those two is the space in which the mix-free
    envelope's admission lives. See §14 of the finding: the admission lives entirely in that gap.

    ORDER IS LOAD-BEARING IN THE RETURNED DICT. The two new keys are appended AFTER the three §13
    published, so every value §13's artefact carries keeps its place and its bytes, and a reader
    diffing the two artefacts sees additions rather than a rewrite.
    """
    return {
        "tenure_composed": compose_at_mix(_HISTORICAL_OBSERVATION.long_stayer_share),
        "mix_free_envelope": (
            min(SVT_CHURN_LONG_STAYER[0], SVT_CHURN_RECENT[0]),
            max(SVT_CHURN_LONG_STAYER[1], SVT_CHURN_RECENT[1]),
        ),
        "long_stayer_share_of_svt": (
            round(_HISTORICAL_OBSERVATION.long_stayer_share, 6),
            round(_HISTORICAL_OBSERVATION.long_stayer_share, 6),
        ),
        # ONE BAND PER OBSERVATION, NAMED BY ITS YEAR AND NOT BY ITS POSITION. The first draft read
        # `SVT_TENURE_OBSERVATIONS[1]`, which is a register that cannot lose a row and cannot gain
        # one in the middle -- `test_a_second_tenure_observation_cannot_move_the_mix_free_envelope_
        # or_the_constant_pair` caught it by handing the module a one-row register. The historical
        # observation is already published as `tenure_composed` and is not repeated here.
        **{
            f"tenure_composed_{o.year}": compose_at_mix(o.long_stayer_share)
            for o in SVT_TENURE_OBSERVATIONS
            if o.year != _HISTORICAL_OBSERVATION.year
        },
        "observed_mix_hull": _observed_mix_hull(),
    }


def _observed_mix_hull() -> tuple[float, float]:
    """Every mix BETWEEN the observations, as one band. Falls back to the historical one alone.

    A hull over an EMPTY register would be `min()` of nothing, which raises -- and a reading that
    crashes when its register is emptied cannot report that its register was emptied. The
    historical observation is always in the hull for that reason, and the control that empties the
    register is what found it.
    """
    composed = [compose_at_mix(o.long_stayer_share) for o in SVT_TENURE_OBSERVATIONS]
    composed.append(compose_at_mix(_HISTORICAL_OBSERVATION.long_stayer_share))
    return (min(c[0] for c in composed), max(c[1] for c in composed))


#: The bands every phi verdict below is taken at, in one place because it was written out twice and
#: a third caller was about to write it a third time. The two §13 published come FIRST so their
#: entries keep their position in the committed artefact.
def phi_verdict_bands() -> dict[str, tuple[float, float]]:
    """The four segment bands the constant-phi question is asked at, named and ordered."""
    svt = svt_segment_churn_band()
    ordered = ["tenure_composed", "mix_free_envelope"]
    ordered += [k for k in svt if k.startswith("tenure_composed_")]
    ordered.append("observed_mix_hull")
    return {k: svt[k] for k in ordered}


def observed_mix_bands() -> tuple[str, ...]:
    """The bands built from a tenure mix something has OBSERVED, as against one nobody has measured.

    THE DISTINCTION IS THE WHOLE OF §14 and it is derived here rather than inferred at each caller,
    because the one band that must NOT be in it -- `mix_free_envelope` -- is the one whose
    inclusion would make every §14 flag read the way §13 expected.
    """
    return tuple(b for b in phi_verdict_bands() if b != "mix_free_envelope")


def _corners(
    year: int, basis: str, *, at_share: float | None = None
) -> list[tuple[float, float]] | None:
    """`[(R_fraction, s_fraction), ...]` over both published bands' endpoints, or None on a gap.

    The identity is BILINEAR in `(s, H_svt)`, so over a box its extrema are attained at corners and
    enumerating them is exact. Doing it by hand -- "s is increasing so take the high end" -- gets
    the sign wrong whenever `H_svt` and `H_fixed` swap order, which they do between 2019 and 2022.

    `at_share` PINS `s` TO ONE VALUE instead of sweeping the published pair, and it exists for one
    caller: the joint reading, which derives a hazard AT a named share endpoint and must then judge
    it at THAT endpoint. Sweeping both would compare a hazard solved at one share against an
    interval taken over two, which is the mixed-pair defect the joint reading exists to correct.
    The year's gap check still runs: an `at_share` for a year with no published figure is still a
    refusal, because the band `R` is what makes the corner and the year's absence is not about `s`.
    """
    share = default_tariff_share(year, basis)
    band = published_departure_band().get(year)
    if share is None or band is None:
        return None
    if at_share is not None:
        share = (at_share,)  # type: ignore[assignment]
    return list(itertools.product((band[0] / 100.0, band[1] / 100.0), share))


def forward_composition(
    year: int, basis: str, phi: float, *, svt_band: tuple[float, float]
) -> dict | None:
    """Compose the published segment rates at `phi` and say where the result sits on the band.

    Returns percentages, to match `published_departure_band`'s units, and a `verdict` of
    `above` / `below` / `overlaps`. **`overlaps`, not `inside`**: both sides are bands, and a
    composed band that straddles the published one is not a world sitting inside the record -- it is
    two intervals with a non-empty intersection, which is the most this evidence can say.
    """
    corners = _corners(year, basis)
    if corners is None:
        return None
    h_fixed = FIXED_ACTIVE_RENEWAL_SHARE * phi
    composed = [
        100.0 * (s * h + (1.0 - s) * h_fixed)
        for (_r, s), h in itertools.product(corners, svt_band)
    ]
    lo_c, hi_c = min(composed), max(composed)
    lo_r, hi_r = published_departure_band()[year]
    return {
        "composed_pct": [round(lo_c, 4), round(hi_c, 4)],
        "band_pct": [lo_r, hi_r],
        "verdict": "above" if lo_c > hi_r else ("below" if hi_c < lo_r else "overlaps"),
    }


def admissible_svt_churn(
    year: int, basis: str, *, at_share: float | None = None
) -> dict | None:
    """The interval of `H_svt` the published record admits, as `phi` ranges over [0, 1].

    `H_svt = (R - (1 - s) * FIXED_ACTIVE_RENEWAL_SHARE * phi) / s`, which is DECREASING in `phi`:
    every departure the fixed route is credited with is one the SVT route no longer has to supply.
    So the low end is at `phi = 1` and the high end at `phi = 0`, and
    `test_the_admissible_svt_churn_falls_as_the_external_share_rises` holds that direction -- it is
    the one that separates a reading recomputed from the record from a cached column.

    `at_phi_1` CAN COME OUT NEGATIVE, and it is reported rather than clipped to zero. A negative
    value is not an arithmetic slip: it says the fixed route at `phi = 1` alone already exceeds the
    whole published band, so the record REFUSES `phi = 1` in that year. Clipping it to 0.0 would
    turn a refusal into a boundary and hide the only place this identity constrains `phi` from
    above.

    `at_share` pins `s`; see `_corners`. Passing it NARROWS the interval, because part of the width
    here is the published share's own band and not `phi`.
    """
    corners = _corners(year, basis, at_share=at_share)
    if corners is None:
        return None
    at_1 = [(r - (1.0 - s) * FIXED_ACTIVE_RENEWAL_SHARE) / s for r, s in corners]
    at_0 = [r / s for r, s in corners]
    return {
        "at_phi_1": [round(min(at_1), 6), round(max(at_1), 6)],
        "at_phi_0": [round(min(at_0), 6), round(max(at_0), 6)],
        "admissible": [round(min(at_1), 6), round(max(at_0), 6)],
        "record_refuses_phi_1": max(at_1) < 0.0,
    }


def phi_admitting(
    year: int, basis: str, h_svt: float, *, at_share: float | None = None
) -> list[float] | None:
    """The `phi` interval the record needs if the SVT segment ran at `h_svt`, or None on a gap.

    `phi = (R - s * h_svt) / ((1 - s) * FIXED_ACTIVE_RENEWAL_SHARE)`. Values outside [0, 1] are
    returned as they fall: **a negative interval is the record refusing `h_svt` outright**, because
    it would need the fixed route to contribute negative departures, and above 1 means the record
    would need more external switching from fixed households than the published active-renewal
    share can supply. Both are results and neither is clipped.

    `at_share` pins `s`; see `_corners`. The joint reading MUST pass it: a `phi` taken over both
    published share endpoints, for a hazard solved at one of them, is not the same question.
    """
    corners = _corners(year, basis, at_share=at_share)
    if corners is None:
        return None
    phis = [
        (r - s * h_svt) / ((1.0 - s) * FIXED_ACTIVE_RENEWAL_SHARE) for r, s in corners
    ]
    return [round(min(phis), 6), round(max(phis), 6)]


def _refused_years() -> dict[str, str]:
    """Years the band covers that this reading will not score, each with its named reason."""
    established = set(years_with_an_established_figure())
    return {
        str(year): (
            "no established default-tariff share; "
            f"{tuple(str(y) for y in sorted(set(published_departure_band()) - established))} are "
            "declared gaps in tools.published_tariff_mix and are NOT interpolated -- the interval "
            "spans the crisis"
        )
        for year in sorted(set(published_departure_band()) - established)
    }


def where_the_worlds_point_falls() -> dict | None:
    """Where the world's operating and required hazards sit inside the record's admissible interval.

    THE ONE PLACE THIS MODULE LOOKS AT THE WORLD, and it looks at the committed artefact rather than
    a capture. Returns `None`, not an exception, when that artefact is absent: a published reading
    that cannot be computed without a world file would not be a published reading.

    THE JOINT RESULT THIS EXISTS TO SURFACE. §9's `required_hazard` is conditional on the world's
    OWN SVT share, which §10 then measured as BELOW the published one. Applying that required hazard
    at the PUBLISHED share is therefore not the same counterfactual, and it is the one a reader will
    assume: it asks what happens if both repairs land. `phi_admitting_required` is that question's
    answer, and where it is negative the record refuses the pair -- raising the hazard to what the
    world needs AND correcting the share to published overshoots the record. The two repairs are not
    additive and this is the only place that is said.
    """
    if not SHORTFALL_ARTEFACT.exists():
        return None
    shortfall = json.loads(SHORTFALL_ARTEFACT.read_text())
    rows: dict[str, dict] = {}
    for year_s, row in sorted(shortfall["per_year"].items()):
        year = int(year_s)
        entry: dict = {
            "world_hazard": row["factors"]["hazard"],
            "required_hazard_at_band_low": row["required_hazard"]["at_band_low"],
        }
        for basis in BASES:
            admissible = admissible_svt_churn(year, basis)
            entry[basis] = {
                "admissible_svt_churn": None if admissible is None else admissible["admissible"],
                "phi_admitting_world": phi_admitting(year, basis, row["factors"]["hazard"]),
                "phi_admitting_required": phi_admitting(
                    year, basis, row["required_hazard"]["at_band_low"]
                ),
            }
        rows[year_s] = entry
    return {
        "source": str(SHORTFALL_ARTEFACT.relative_to(PROJECT)),
        "measured_at_anchor": shortfall["measured_at_anchor"],
        "world_level_digest": shortfall["world_level_digest"],
        "per_year": rows,
    }


#: The composition counterfactual this joins §9's reading to. Committed artefact, never re-derived.
COMPOSITION_ARTEFACT = PROJECT / "docs" / "reports" / "svt_composition_vs_published.json"

#: The accountings §10 publishes, headline first. Both are carried here for the reason §10 carries
#: them: a verdict that depends on which one you pick is a verdict about the pick.
ACCOUNTINGS = ("renewal_rescaled", "renewal_held")

#: The published share endpoints §10 evaluates at. The joint reading is computed at each SEPARATELY
#: and judged at the SAME one, which is the whole point of it.
SHARE_ENDPOINTS = ("at_published_low", "at_published_high")


def intersect_spans(spans: list[list[float]]) -> dict:
    """`[lo, hi]` common to every span, and whether that is a real interval or an empty one.

    A MODULE-LEVEL PURE FUNCTION AND NOT A CLOSURE, on purpose. Both intersections this reading
    publishes are currently EMPTY, so a verdict frozen to `False` reproduces the artefact exactly
    and a control over the artefact alone cannot tell a derivation from a constant -- which is what
    happened: the first draft of `test_the_one_phi_question_is_asked_of_the_unrepaired_world_too`
    stayed green when `is_non_empty` was replaced by `False`. Lifting the rule out here makes the
    non-empty branch reachable from a control with spans it constructs itself, so both branches are
    exercised whatever the world happens to say this week.

    An empty intersection is returned with its endpoints CROSSED (`lo > hi`) rather than as `None`:
    the amount by which they cross is how far apart the years are, and that is the reading.
    """
    lo, hi = max(s[0] for s in spans), min(s[1] for s in spans)
    return {"intersection": [round(lo, 6), round(hi, 6)], "is_non_empty": lo <= hi}


#: The years the rung-1 verdict fits. The constant-phi question is asked over these FIRST, because
#: they are the set the repair is judged on, and then over every scored year so that a verdict which
#: turns on the fitted subset cannot be mistaken for one about the whole record.
FITTED_YEARS = (2017, 2018, 2019, 2023, 2024)

#: A year excluded from the constant-phi intersection with its reason, NOT dropped. 2022 is the one
#: stretch of this record where the market itself stopped offering the product the identity's fixed
#: route is made of: there were no fixed deals to renew onto for most of it. Asking a constant phi
#: to span that is asking one behavioural parameter to describe two markets, and the arithmetic
#: agrees loudly -- at the tenure-composed band 2022's whole phi interval is NEGATIVE. It is
#: reported in its own field, at both bands, rather than filtered out of the headline in silence.
STRUCTURAL_BREAK_YEARS: dict[int, str] = {
    2022: "the crisis year. Fixed-term offers were withdrawn across the market for most of it, so "
          "the identity's fixed route -- households actively renewing onto a NEW fixed deal -- is "
          "describing a product that was largely not for sale. A phi held constant across it is "
          "one parameter over two markets. EXCLUDED FROM THE HEADLINE INTERSECTION AND REPORTED "
          "SEPARATELY, with its own phi interval at both bands, so the exclusion is checkable "
          "rather than assumed.",
}


def phi_span_at_a_segment_band(
    year: int, basis: str, svt_band: tuple[float, float]
) -> list[float] | None:
    """The phi interval the record admits when `H_svt` may be ANYWHERE in `svt_band`, or None.

    THE NO-WORLD COMPANION TO `one_phi_for_every_year`. §12 took its phi intervals at the world's
    per-year hazard -- a POINT -- and read the empty intersection as *"a statement about the
    world"*. That inference needs a non-empty result to have been attainable, and nothing had
    checked whether it was. This is the same intersection with the world's hazard replaced by a
    PUBLISHED band, so the question can be asked of the record on its own.

    `phi = (R - s·H) / ((1 - s)·0.35)` is strictly DECREASING in `H` for any `s` in (0, 1), so over
    the box its extremes sit at the band's endpoints: the low end of phi at `H = band_hi` and the
    high end at `H = band_lo`. Enumerating the two endpoints is therefore exact and not a sample.
    Getting that direction backwards inverts the interval into a silent always-empty, which is a
    fail-closed that reads exactly like a finding --
    `test_the_phi_span_widens_with_the_segment_band` holds it.

    Values outside [0, 1] are returned as they fall, for the reason `phi_admitting` gives: a span
    entirely below zero is the record REFUSING that segment band in that year, and clipping turns a
    refusal into a boundary the reader cannot distinguish from one.
    """
    at_hi = phi_admitting(year, basis, svt_band[1])
    at_lo = phi_admitting(year, basis, svt_band[0])
    if at_hi is None or at_lo is None:
        return None
    return [at_hi[0], at_lo[1]]


def whether_a_constant_phi_survives_the_record_alone() -> dict:
    """Does the PUBLISHED record admit one constant phi? Asked with no world in it at all.

    §12 handed on one question -- *"a mismatch here can live in the share series as easily as in
    the hazard ... which of the two moves is the next question"* -- and left one premise unchecked:
    that an empty phi intersection is *"a statement about the world"*. Both are answered here from
    three published series and nothing else.

    THREE NESTED QUESTIONS, EACH LOOSER THAN THE LAST, because the answer changes between them and
    which one you asked is the whole verdict:

    1. **A constant PAIR** -- one `H_svt` and one phi, both fixed across years. `constant_pair`
       sweeps `H` and reports whether any value admits a common phi.
    2. **`H_svt` free per year inside `tenure_composed`, phi constant.** The best available reading
       of the segment, and it rests on one survey year.
    3. **`H_svt` free per year inside `mix_free_envelope`, phi constant.** The value the segment
       could take under ANY tenure mix. A verdict has to survive this to be about the record rather
       than about 2018 -- which is the distinction §11 built `verdict_is_mix_dependent` for and
       which §12's one-phi reading never applied to itself.

    WHAT A NON-EMPTY INTERSECTION IS AND IS NOT. It is an interval phi COULD take if phi were
    constant over the years intersected. The record does not supply that constancy and neither does
    this module: `EXTERNAL_SHARE_OF_ACTIVE_RENEWALS` stays `None` and
    `test_the_external_share_of_active_renewals_stays_a_declared_gap` keeps it there. The interval
    is published as `conditional_interval` under an `assumption` field for exactly that reason -- an
    interval written into a slot reads as an established figure inside a week.
    """
    scored = sorted(set(published_departure_band()) & set(years_with_an_established_figure()))
    bands = phi_verdict_bands()

    per_year: dict[str, dict] = {}
    for year in scored:
        per_year[str(year)] = {
            "band_pct": list(published_departure_band()[year]),
            "is_a_structural_break": year in STRUCTURAL_BREAK_YEARS,
            **{
                basis: {
                    band_name: phi_span_at_a_segment_band(year, basis, band)
                    for band_name, band in bands.items()
                }
                for basis in BASES
            },
        }

    headline_years = [y for y in scored if y not in STRUCTURAL_BREAK_YEARS]
    year_sets = {
        "fitted_years": [y for y in FITTED_YEARS if y in scored],
        "every_scored_year": scored,
        "every_scored_year_less_structural_breaks": headline_years,
    }

    verdicts: dict[str, dict] = {}
    for basis in BASES:
        by_band: dict[str, dict] = {}
        for band_name in bands:
            by_set: dict[str, dict] = {}
            for set_name, years in year_sets.items():
                spans = [per_year[str(y)][basis][band_name] for y in years]
                result = intersect_spans(spans)
                # The pairs that would refuse on their own. A refusal carried by ONE pair is a
                # different fact from one that needs all seven years, and a reader given only the
                # crossed endpoints cannot tell which they have.
                refusing = [
                    [a, b]
                    for i, a in enumerate(years)
                    for b in years[i + 1:]
                    if not intersect_spans(
                        [per_year[str(a)][basis][band_name], per_year[str(b)][basis][band_name]]
                    )["is_non_empty"]
                ]
                by_set[set_name] = {
                    "n_years": len(years),
                    "years": [str(y) for y in years],
                    **result,
                    "minimal_refusing_pairs": refusing,
                }
            by_band[band_name] = by_set
        # THE FLAG §11 BUILT AND §12 DID NOT USE. Computed per year-set, never asserted: the leg
        # that froze it was written expecting the answer it did not get in §11 either.
        by_band["verdict_is_mix_dependent"] = {
            set_name: (
                by_band["tenure_composed"][set_name]["is_non_empty"]
                != by_band["mix_free_envelope"][set_name]["is_non_empty"]
            )
            for set_name in year_sets
        }
        # §14. THE DISTINCTION `verdict_is_mix_dependent` CANNOT MAKE, and it is not a second
        # version of it. That flag compares ONE observed mix against a mix nobody has measured, so
        # a True there means "the verdict depends on the tenure mix" and cannot say whether it
        # depends on the 2018 SURVEY specifically. With two observations it can: this asks whether
        # the verdict is the same at every mix anything has actually observed.
        by_band["the_verdict_is_the_same_at_every_observed_mix"] = {
            set_name: len({
                by_band[b][set_name]["is_non_empty"] for b in observed_mix_bands()
            }) == 1
            for set_name in year_sets
        }
        verdicts[basis] = by_band

    return {
        "what_this_is":
            "whether ONE constant phi reconciles the published departure band with the published "
            "default-tariff share, at a published SVT segment band. THREE PUBLISHED SERIES AND NO "
            "WORLD. The no-world companion to §12's `one_phi_for_every_year`, which took the same "
            "intersection at the world's per-year hazard and read its emptiness as a statement "
            "about the world.",
        "identity": "R(y) = s(y)·H_svt(y) + (1 - s(y))·0.35·phi, with phi constant across the "
                    "years intersected and H_svt free per year inside the named segment band.",
        "the_assumption_that_is_not_the_records":
            "phi CONSTANT across years. The record does not supply that and this module does not "
            "adopt it: an intersection is what phi could be IF it were constant, and its emptiness "
            "is equally a statement that phi moved. Which is why `EXTERNAL_SHARE_OF_ACTIVE_"
            "RENEWALS` stays None whatever this returns.",
        "published_segment_bands": {k: list(v) for k, v in bands.items()},
        "year_sets": {k: [str(y) for y in v] for k, v in year_sets.items()},
        "structural_breaks": {str(y): r for y, r in STRUCTURAL_BREAK_YEARS.items()},
        "years_refused": _refused_years(),
        "per_year": per_year,
        "verdicts": verdicts,
        "constant_pair": _whether_any_constant_pair_admits_a_common_phi(),
    }


def _long_stayer_share_implying(h_lo: float, h_hi: float) -> dict[str, float]:
    """What within-segment long-stayer share each end of a segment band implies, inverting the mix.

    `compose_at_mix` is affine and strictly decreasing in the long-stayer share at BOTH ends -- a
    long-stayer churns less -- so each endpoint inverts to exactly one mix. This is what turns "the
    mix-free envelope admits a constant phi" into a sentence about a segment nobody has observed:
    the envelope's low end is a segment that is ENTIRELY long-stayer and its high end is one with
    NO long-stayers, and the two observations sit at 0.37 and 0.56.
    """
    lo_span = SVT_CHURN_RECENT[0] - SVT_CHURN_LONG_STAYER[0]
    hi_span = SVT_CHURN_RECENT[1] - SVT_CHURN_LONG_STAYER[1]
    return {
        "implied_by_the_bands_low_end": round((SVT_CHURN_RECENT[0] - h_lo) / lo_span, 6),
        "implied_by_the_bands_high_end": round((SVT_CHURN_RECENT[1] - h_hi) / hi_span, 6),
    }


def whether_the_constant_phi_verdict_turns_on_one_survey_year() -> dict:
    """§13 asked for a second tenure observation. Here is what the record says with it. NO WORLD.

    §13 closed by naming its own binding weak input -- *"the single Ofgem CES 2018 tenure split,
    which is carried across nine years and is what separates a record that refuses constancy from
    one that admits it"* -- and asked for **one more observation of that one quantity**, saying it
    *"decides whether the record refuses a constant phi or admits 0.62-0.85 of one"*.

    THE SECOND OBSERVATION WAS ALREADY IN THE TREE, and the sentence it was asked to settle turns
    out to be the wrong dichotomy. This function is the reading that shows which, and it is built so
    that the answer §13 expected is fully reportable: `the_verdict_is_the_same_at_every_observed_mix`
    is derived from the verdicts and never written down, so a run where the two observations
    disagreed would say so here in the same field.

    WHAT IT ADDS THAT `whether_a_constant_phi_survives_the_record_alone` DOES NOT. That function now
    reports four bands, which is the mechanism. This one reports the QUESTION: whether the refusal
    is a property of the record or of one survey, and -- when the two observed mixes agree and the
    mix-free envelope does not -- what tenure mix the envelope's admission actually requires. A
    reader given four bands and no such field would have to do that inversion themselves, and the
    inversion is the finding.
    """
    verdicts = whether_a_constant_phi_survives_the_record_alone()
    bands = phi_verdict_bands()
    observed = [b for b in observed_mix_bands() if b in bands]

    per_basis: dict[str, dict] = {}
    for basis in BASES:
        by_set: dict[str, dict] = {}
        for set_name in verdicts["year_sets"]:
            at_band = {
                band: verdicts["verdicts"][basis][band][set_name] for band in bands
            }
            same_at_every_observed = len({at_band[b]["is_non_empty"] for b in observed}) == 1
            refuses_everywhere_observed = all(
                not at_band[b]["is_non_empty"] for b in observed
            )
            by_set[set_name] = {
                "is_non_empty_by_band": {b: at_band[b]["is_non_empty"] for b in bands},
                "intersection_by_band": {b: at_band[b]["intersection"] for b in bands},
                "the_verdict_is_the_same_at_every_observed_mix": same_at_every_observed,
                "refuses_at_every_observed_mix": refuses_everywhere_observed,
                # The result §13's dichotomy has no slot for: the record can refuse at every mix
                # anything has SEEN and still admit somewhere in the mix-free envelope. That is
                # neither "refuses" nor "admits 0.62-0.85" -- it is the admission being relocated
                # to a segment composition no instrument supports.
                "admits_only_outside_every_observed_mix": (
                    refuses_everywhere_observed
                    and at_band["mix_free_envelope"]["is_non_empty"]
                ),
                "minimal_refusing_pairs_by_band": {
                    b: at_band[b]["minimal_refusing_pairs"] for b in bands
                },
            }
        per_basis[basis] = by_set

    return {
        "what_this_is":
            "whether the constant-phi refusal is a property of the published record or of the one "
            "2018 survey year the segment band was composed with. §13 asked for a second "
            "observation of the SVT tenure split; this is the record read with it. Three published "
            "series and no world.",
        "what_section_13_asked_for": (
            "a second tenure split for the SVT segment in any year other than 2018. §13 called it "
            "'the highest-leverage sourcing question this chain has produced' and said one more "
            "observation would decide 'whether the record refuses a constant phi or admits "
            "0.62-0.85 of one'."
        ),
        "where_it_was_found": (
            "IN THIS TREE, cited and dated, and load-bearing since 2026-07-22. "
            "docs/market_research/ASSUMPTIONS.md L176 carries Ofgem's Retail Market Indicators "
            "October-2025 default-tariff stock split and the R13 ruling turns on it; "
            "continuous_behavioural_engagement_w2_14.md §1a cross-validates the same figure "
            "against CMA Appendix 9.1. Nothing pointed either of them at the segment band. That is "
            "the shape §10 recorded -- 'it was already in the tree, three times' -- for the fourth "
            "time in this one chain, and the structural fix is the register above: one home."
        ),
        "observations": [
            {
                "year": o.year,
                "long_stayer_pct": o.long_stayer_pct,
                "recent_pct": o.recent_pct,
                "long_stayer_share_of_svt": round(o.long_stayer_share, 6),
                "composed_band": list(compose_at_mix(o.long_stayer_share)),
                "instrument": o.instrument,
                "population": o.population,
                "source": o.source,
                "restoring_the_excluded_moves_the_long_stayer_share":
                    o.restoring_the_excluded_moves_the_long_stayer_share,
            }
            for o in SVT_TENURE_OBSERVATIONS
        ],
        "the_two_observations_disagree_by": round(
            max(o.long_stayer_share for o in SVT_TENURE_OBSERVATIONS)
            - min(o.long_stayer_share for o in SVT_TENURE_OBSERVATIONS),
            6,
        ),
        "they_are_not_a_trend": (
            "one is a consumer survey over all domestic customers and one is supplier-returned "
            "stock over non-prepayment electricity accounts. Two points on two instruments over "
            "two populations are not a series, and this reading does not interpolate between them "
            "or extrapolate beyond them -- it takes the HULL, which is every mix between the two "
            "and needs neither assumption."
        ),
        "bands": {k: list(v) for k, v in bands.items()},
        "observed_mix_bands": list(observed),
        # The inversion that makes the mix-free envelope's admission a sentence about a segment
        # rather than a number. Published for BOTH bands so the observed hull's own implied mixes
        # sit beside it and the reader can see the envelope is asking for something else entirely.
        "what_each_bands_endpoints_imply_about_the_segment": {
            band: _long_stayer_share_implying(*bands[band]) for band in bands
        },
        "the_observed_range_of_the_long_stayer_share": [
            round(min(o.long_stayer_share for o in SVT_TENURE_OBSERVATIONS), 6),
            round(max(o.long_stayer_share for o in SVT_TENURE_OBSERVATIONS), 6),
        ],
        "by_basis": per_basis,
        "what_stays_none_whatever_this_says": (
            "EXTERNAL_SHARE_OF_ACTIVE_RENEWALS. A second tenure observation constrains the SVT "
            "side of the identity and says nothing about the external share of active fixed-term "
            "renewals. The owed sourcing question is unchanged: one cross-tabulation of Ofgem's "
            "Consumer Impacts of Market Conditions survey, separating 'switched supplier' from "
            "'switched tariff with the same supplier' on one base."
        ),
    }


#: The `H_svt` grid the constant-pair sweep runs over, and its step. 0 to 0.40 covers every value
#: the published rows, the world's constants and the world's own required hazards can take
#: (§9's largest is 0.334); the step is fine enough that a slack of -0.31 cannot be a grid artefact.
_CONSTANT_PAIR_H_MAX = 0.40
_CONSTANT_PAIR_H_STEP = 0.0001


def _whether_any_constant_pair_admits_a_common_phi() -> dict:
    """Is there ONE `H_svt` and ONE phi, both constant, that the record admits in every year?

    The tightest of the three questions and the one that needs no segment band at all -- `H` sweeps
    freely, so the published rows are not an input and the reading cannot inherit their weakness.

    THE SLACK IS PUBLISHED, NOT JUST THE VERDICT. `widest_slack` is the largest `hi - lo` over the
    grid, negative when every `H` refuses. A bare `False` cannot be told apart from a sweep that
    never ran, and the MARGIN is what says whether the refusal is a rounding away from admitting.
    """
    out: dict[str, dict] = {}
    for basis in BASES:
        years = [y for y in FITTED_YEARS if default_tariff_share(y, basis) is not None]
        admitting: list[float] = []
        widest: tuple[float, float, float, float] | None = None
        steps = int(round(_CONSTANT_PAIR_H_MAX / _CONSTANT_PAIR_H_STEP)) + 1
        for i in range(steps):
            h = round(i * _CONSTANT_PAIR_H_STEP, 6)
            spans = [phi_admitting(y, basis, h) for y in years]
            lo, hi = max(s[0] for s in spans), min(s[1] for s in spans)  # type: ignore[index]
            if widest is None or (hi - lo) > widest[1]:
                widest = (h, hi - lo, lo, hi)
            # phi is a SHARE, so admitting also means the common interval reaches [0, 1] at all.
            if lo <= hi and lo <= 1.0 and hi >= 0.0:
                admitting.append(h)
        assert widest is not None  # the grid is never empty
        out[basis] = {
            "years": [str(y) for y in years],
            "h_svt_grid": [0.0, _CONSTANT_PAIR_H_MAX, _CONSTANT_PAIR_H_STEP],
            "n_h_values_admitting_a_common_phi": len(admitting),
            "any_constant_pair_admitted": bool(admitting),
            "widest_slack": {
                "at_h_svt": round(widest[0], 6),
                "slack": round(widest[1], 6),
                "crossed_phi_interval": [round(widest[2], 6), round(widest[3], 6)],
            },
        }
    return out


def how_much_of_the_records_move_the_share_series_can_carry() -> dict:
    """WHICH OF THE TWO MOVES — the published share series, or behaviour. A bound, not a trend.

    §12's handover. Hold `H_svt` and phi at ANY constants across a pair of years and the composed
    departure rate moves by exactly

        dV = (s2 - s1)·(H_svt - 0.35·phi)

    so the share series' movement, on its own, can supply an interval of moves and no more. Put
    that interval beside the move the record actually made. Where they do not intersect, **the
    share series cannot have carried that step whatever the two behavioural parameters are**, and
    the movement is behavioural. Bilinear over a box, so the corners are exact.

    THE TRAP THIS READING WALKED INTO ON ITS FIRST RUN, and the reason `record_requires_a_move`
    exists. Two of the seven pairs come out `share_can_carry = True`, and in both the record's own
    move interval CONTAINS ZERO -- its bands are wide enough that no move is required at all, so
    anything carries it, including nothing. Counting those as evidence that composition works would
    be a pass branch that cannot fail. They are flagged and excluded from the denominator, and the
    denominator is reported as what it is.

    `spans_a_gap` marks 2019->2022, which is three years and not a step: 2020 and 2021 have no
    published share and are still not interpolated.
    """
    bands = phi_verdict_bands()
    band_r = published_departure_band()
    scored = sorted(set(band_r) & set(years_with_an_established_figure()))

    out: dict[str, dict] = {}
    for band_name, h_band in bands.items():
        by_basis: dict[str, dict] = {}
        for basis in BASES:
            pairs: dict[str, dict] = {}
            for y1, y2 in zip(scored, scored[1:]):
                s1 = default_tariff_share(y1, basis)
                s2 = default_tariff_share(y2, basis)
                if s1 is None or s2 is None:  # pragma: no cover - scored years all have a share
                    continue
                r1, r2 = band_r[y1], band_r[y2]
                record_move = [round(r2[0] - r1[1], 6), round(r2[1] - r1[0], 6)]
                # (H_svt - 0.35·phi) over H in the segment band and phi in [0, 1].
                k = (h_band[0] - FIXED_ACTIVE_RENEWAL_SHARE, h_band[1])
                d_s = (s2[0] - s1[1], s2[1] - s1[0])
                products = [100.0 * a * b for a, b in itertools.product(d_s, k)]
                reachable = [round(min(products), 6), round(max(products), 6)]
                requires = not (record_move[0] <= 0.0 <= record_move[1])
                pairs[f"{y1}->{y2}"] = {
                    "record_move_pp": record_move,
                    "share_reachable_move_pp": reachable,
                    "record_requires_a_move": requires,
                    "spans_a_gap": (y2 - y1) != 1,
                    "share_can_carry": not (
                        reachable[1] < record_move[0] or record_move[1] < reachable[0]
                    ),
                }
            judged = {
                k: v for k, v in pairs.items()
                if v["record_requires_a_move"] and not v["spans_a_gap"]
            }
            by_basis[basis] = {
                "pairs": pairs,
                "n_pairs_judged": len(judged),
                "n_pairs_the_share_series_can_carry": sum(
                    1 for v in judged.values() if v["share_can_carry"]
                ),
                "pairs_excluded_because_the_record_requires_no_move": [
                    k for k, v in pairs.items() if not v["record_requires_a_move"]
                ],
                "pairs_excluded_because_they_span_a_gap": [
                    k for k, v in pairs.items() if v["spans_a_gap"]
                ],
            }
        out[band_name] = by_basis
    return {
        "what_this_is":
            "the largest step the PUBLISHED SHARE SERIES can produce on its own, with both "
            "behavioural parameters held at any constants, against the step the record made. "
            "§12's handover question, answered as a bound.",
        "identity": "dV = (s2 - s1)·(H_svt - 0.35·phi), bilinear over the box, corners exact.",
        "why_a_denominator_is_reported":
            "a pair whose record move interval contains zero requires no move, so `share_can_carry` "
            "is True there for a reason that is not evidence. Those pairs are named and excluded, "
            "and so is the one that spans the 2020-2021 gap.",
        "by_band": out,
    }


def _provenance(path: Path) -> str:
    """The path a reading names as its source: repo-relative inside the tree, absolute outside it.

    An artefact read from outside the repo -- which is what a control does when it perturbs one --
    must still be NAMED. Raising instead would make the source field the reason the reading cannot
    be tested, and silently printing a bare filename would let an out-of-tree input read as the
    committed one.
    """
    try:
        return str(path.relative_to(PROJECT))
    except ValueError:
        return str(path)


def where_the_worlds_joint_point_falls() -> dict | None:
    """§9's hazard and §10's share moved TOGETHER, judged against the record at that same share.

    THE SECOND THING §11 LEFT OWED, and the one that is not a sourcing job. §11 said the two
    readings must be re-run jointly; the step it took was a MIXED pair and this is the correction.

    `where_the_worlds_point_falls` computes `phi_admitting_required` by feeding §9's
    `required_hazard` -- solved holding the world's OWN, lower, SVT share fixed, and therefore sized
    to close the entire gap on the SVT route alone -- into a composition evaluated at the PUBLISHED
    share. That is not "both repairs land". It is one repair sized to do all the work, applied on
    top of another repair that has already done part of it, and it DOUBLE-COUNTS by construction.
    §11's result 2 -- *"the record refuses the pair"* -- is that double-count.

    The self-consistent quantity is already published by §10 and nobody had multiplied it out:

        H_joint  =  world_hazard  x  hazard_multiple_still_required_at_band_low

    where the multiple is taken at a named published share endpoint on a named basis under a named
    accounting, with the renewal route already moved to its complement. `H_joint` is then judged
    against `admissible_svt_churn` and `phi_admitting` **pinned to that same share** -- not swept
    over the published pair, which is the mixed comparison one level down and would re-introduce the
    defect while claiming to have fixed it.

    NO WORLD IS OPENED HERE EITHER. Both inputs are committed artefacts and a missing one returns a
    declared `None` rather than crashing the published reading that does not need them.

    THE DIRECTION IS FORCED AND THE VERDICT IS NOT. `H_joint < required_hazard` always, by roughly
    the composition multiple, because composition supplies departures the hazard then does not have
    to. Whether the smaller number is ADMISSIBLE is a question about the record, and it is the one
    that flips 2017.
    """
    if not (SHORTFALL_ARTEFACT.exists() and COMPOSITION_ARTEFACT.exists()):
        return None
    shortfall = json.loads(SHORTFALL_ARTEFACT.read_text())
    composition = json.loads(COMPOSITION_ARTEFACT.read_text())

    rows: dict[str, dict] = {}
    for year_s in sorted(composition["years_measurable"]):
        comp = composition["per_year"][year_s]
        short = shortfall["per_year"].get(year_s)
        if short is None:  # pragma: no cover - the two readings share their fitted-year set
            continue
        year = int(year_s)
        world_hazard = short["factors"]["hazard"]
        entry: dict = {
            "world_hazard": world_hazard,
            # §9's number, carried so the two can be read side by side and the gap between them
            # is visible rather than asserted. It is NOT the joint requirement.
            "required_hazard_holding_the_worlds_share_fixed": short["required_hazard"]["at_band_low"],
            "world_svt_account_day_share": comp["world_svt_account_day_share"],
            "band_pct": comp["band_pct"],
        }
        for basis in BASES:
            if basis not in comp["bases"]:  # pragma: no cover - both bases are always present
                continue
            per_endpoint: dict = {}
            for endpoint in SHARE_ENDPOINTS:
                cell = comp["bases"][basis][endpoint]
                share = cell["published_svt_account_day_share"]
                admissible = admissible_svt_churn(year, basis, at_share=share)
                if admissible is None:  # pragma: no cover - measurable years have a share
                    continue
                lo, hi = admissible["admissible"]
                accountings: dict = {}
                for accounting in ACCOUNTINGS:
                    multiple = cell[accounting]["hazard_multiple_still_required_at_band_low"]
                    if multiple is None:  # pragma: no cover - svt_pp is positive in every year
                        continue
                    # ROUNDED BEFORE phi IS TAKEN FROM IT, not after. A reader who recomputes phi
                    # from the hazard this artefact publishes must get the number this artefact
                    # publishes; taking phi off the unrounded value leaves the two differing in the
                    # last place and the reading not reproducible from its own printed inputs.
                    joint = round(world_hazard * multiple, 6)
                    phi = phi_admitting(year, basis, joint, at_share=share)
                    accountings[accounting] = {
                        "hazard_multiple_still_required": multiple,
                        "joint_required_hazard": joint,
                        "joint_hazard_is_admissible": lo <= joint <= hi,
                        "phi_admitting_joint": phi,
                        # A phi interval entirely below zero is the record REFUSING the pair: it
                        # would need the fixed route to contribute negative departures. Above 1 is
                        # the other refusal and it is a different sentence, so both are named.
                        "record_refuses_the_joint_pair": phi is not None and phi[1] < 0.0,
                        "record_needs_more_than_the_fixed_route_can_supply": (
                            phi is not None and phi[0] > 1.0
                        ),
                    }
                per_endpoint[endpoint] = {
                    "published_svt_account_day_share": share,
                    "composition_multiple": cell["composition_multiple"],
                    "admissible_svt_churn_at_this_share": [lo, hi],
                    # THE UNREPAIRED WORLD AT THE SAME SHARE, so that anything the joint point is
                    # blamed for can be checked against what was already true before the repair.
                    # Without it, a property of this world's shape reads as a property of the
                    # repair, which is the attribution error this whole finding keeps paying for.
                    "phi_admitting_the_worlds_current_hazard": phi_admitting(
                        year, basis, world_hazard, at_share=share
                    ),
                    "accountings": accountings,
                }
            entry[basis] = per_endpoint
        rows[year_s] = entry

    def _refused(basis: str) -> list[str]:
        """Years the record refuses on EVERY endpoint and accounting -- a robust refusal."""
        return [
            y for y, row in rows.items()
            if row.get(basis)
            and all(
                acc["record_refuses_the_joint_pair"]
                for ep in row[basis].values()
                for acc in ep["accountings"].values()
            )
        ]

    def _flipped(basis: str) -> list[str]:
        """Years the MIXED pair was refused in and the JOINT pair is admitted in everywhere.

        This is the set §11's result 2 named and this reading corrects. It is derived from the two
        verdicts rather than written down, so it cannot say "flipped" about a year that was never
        refused in the first place.
        """
        mixed = where_the_worlds_point_falls() or {"per_year": {}}
        out = []
        for y, row in rows.items():
            was = mixed["per_year"].get(y, {}).get(basis, {}).get("phi_admitting_required")
            if not (was and was[1] < 0.0):
                continue
            if row.get(basis) and all(
                not acc["record_refuses_the_joint_pair"]
                for ep in row[basis].values()
                for acc in ep["accountings"].values()
            ):
                out.append(y)
        return out

    def _phi_intersection(basis: str, accounting: str, key: str) -> dict:
        """Is there ONE phi the record admits in every comparable year at once?

        phi is a single behavioural quantity -- the external share of active fixed-term renewals --
        and it may move year to year, but it is one quantity per year and the years are supposed to
        be describing one market. So the per-year intervals having an EMPTY intersection is a
        statement about the world, and it is derived here rather than read off by eye.

        Taken as a UNION over the two share endpoints per year, which is the most generous reading:
        an empty intersection under the generous union is empty under any of them. Computed for the
        world's current hazard as well as the joint one, because an emptiness that was already there
        before the repair is not evidence about the repair.
        """
        los, his, per_year_phi = [], [], {}
        for year_s, row in rows.items():
            if basis not in row or not row[basis]:
                continue
            spans = [
                ep[key] if key in ep else ep["accountings"][accounting]["phi_admitting_joint"]
                for ep in row[basis].values()
            ]
            spans = [s for s in spans if s is not None]
            if not spans:
                continue
            lo_y, hi_y = min(s[0] for s in spans), max(s[1] for s in spans)
            los.append(lo_y)
            his.append(hi_y)
            per_year_phi[year_s] = [round(lo_y, 6), round(hi_y, 6)]
        if not los:  # pragma: no cover - every measurable year yields a span
            return {"years": {}, "intersection": None, "is_non_empty": None}
        return {"years": per_year_phi, **intersect_spans(list(per_year_phi.values()))}

    return {
        "what_this_is": (
            "§9's required hazard and §10's published share applied TOGETHER and judged against "
            "the record at that same share. The correction to `where_the_worlds_point_falls`, "
            "which pairs a hazard solved at the world's share with a composition at the published "
            "one and so double-counts the repair."
        ),
        "identity": (
            "H_joint = world_hazard x hazard_multiple_still_required_at_band_low, where the "
            "multiple already has the renewal route moved to the complement of the published "
            "share. H_joint is then judged at THAT share and no other."
        ),
        "sources": {
            "hazard_and_required": _provenance(SHORTFALL_ARTEFACT),
            "share_and_still_required_multiple": _provenance(COMPOSITION_ARTEFACT),
        },
        "measured_at_anchor": shortfall["measured_at_anchor"],
        "world_level_digest": shortfall["world_level_digest"],
        "headline_accounting": composition["headline_accounting"],
        "years_measurable": sorted(rows),
        "years_refused": composition["years_refused"],
        "years_the_record_refuses_the_joint_pair": {b: _refused(b) for b in BASES},
        # NOT PRE-REGISTERED. Derived after the per-year numbers were seen, and labelled so rather
        # than presented as though it had been predicted. `at_the_worlds_current_hazard` is the
        # control on it: if that is empty too, the emptiness is a property of this world's shape and
        # not of the repair, and nothing here may be said about the repair on the strength of it.
        "one_phi_for_every_year": {
            "status": "derived after the fact; not a graded prediction",
            "at_the_joint_hazard": {
                b: {a: _phi_intersection(b, a, "_joint") for a in ACCOUNTINGS} for b in BASES
            },
            "at_the_worlds_current_hazard": {
                b: _phi_intersection(b, ACCOUNTINGS[0], "phi_admitting_the_worlds_current_hazard")
                for b in BASES
            },
        },
        "years_the_mixed_pair_refused_and_the_joint_pair_admits": {
            b: _flipped(b) for b in BASES
        },
        "per_year": rows,
    }


def _renewal_route_internal_ceiling(years: tuple[int, ...]) -> dict:
    """The MOST internal switching the fixed-renewal route can produce, over `years`.

    A fixed-term household can only make an internal move by actively renewing onto a new deal with
    its existing supplier, so the route's internal output is `(1 - s) * 0.35 * (1 - phi)` and its
    ceiling is at `phi = 0`: `(1 - s) * 0.35`. Nothing about phi is assumed to state the ceiling --
    that is the point of taking it at the endpoint.

    Evaluated at the LARGEST published fixed share across every year the recall window touches, so
    the ceiling is the most generous one the record allows and a reading that still exceeds it
    cannot be argued down by the choice of year. Years with no established share contribute nothing
    and are named rather than dropped.
    """
    considered, missing, best = [], [], None
    for year in years:
        band = fixed_share(year, "all_domestic")
        if band is None:
            missing.append(year)
            continue
        considered.append(year)
        best = band[1] if best is None else max(best, band[1])
    return {
        "years_considered": considered,
        "years_with_no_established_fixed_share": missing,
        "most_generous_fixed_share": best,
        "ceiling": None if best is None else round(best * FIXED_ACTIVE_RENEWAL_SHARE, 6),
    }


def whether_the_survey_split_identifies_phi() -> dict:
    """What Ofgem's CIM external/internal split does and does not settle about `phi`.

    THE SOURCING §11 ASKED FOR AND §14 CALLED THE ONLY THING STILL OWED HAS ARRIVED, AND IT DOES
    NOT CLOSE THE CONSTANT. Stating why in one place, because "we found the survey" and "we know
    phi" are one sentence apart and the gap between them is this repository's recurring shape.

    Over all households, the two published rates decompose by route:

        E  =  s * H_svt        +  (1 - s) * 0.35 * phi          <- external; this IS the record's R
        I  =  s * J_svt        +  (1 - s) * 0.35 * (1 - phi)    <- internal; the survey's new row

    `J_svt`, the rate at which SVT households move onto a fix WITH THEIR EXISTING SUPPLIER, is not
    published anywhere. So the survey's second row arrives carrying its own unknown, and two
    equations in three unknowns identify no more than one equation in two did. `phi_survey`, the
    external share of ALL reported switching, is a MIXTURE of the two routes' external shares
    weighted by how much switching each route produces -- it is not `phi` and is not a bound on it
    in either direction without an assumption about `J_svt` that nothing supplies.

    WHAT THE SURVEY DOES SETTLE, AND IT NEEDS NO ASSUMPTION AT ALL: `J_svt >= 0` is enough to make
    the second equation a testable ceiling. Internal switching that exceeds `(1 - s) * 0.35` cannot
    have come from the fixed-renewal route at any `phi`, so the excess is the SVT route -- a route
    the world has no mechanism for. That is `internal_exceeds_the_renewal_routes_ceiling`.
    """
    waves = []
    for obs in SWITCHER_SPLIT_OBSERVATIONS:
        ceiling = _renewal_route_internal_ceiling(obs.recall_window_years)
        rate = obs.internal_rate_of_all_households
        exceeds = None if ceiling["ceiling"] is None else rate > ceiling["ceiling"]
        waves.append({
            "wave": obs.wave,
            "fieldwork": obs.fieldwork,
            "recall_window_years": list(obs.recall_window_years),
            "base_unweighted": obs.base_unweighted,
            "external_rate_of_all_households": round(
                obs.external_weighted / obs.base_weighted, 6
            ),
            "internal_rate_of_all_households": round(rate, 6),
            "phi_survey": round(obs.external_share_of_switching, 6),
            "both_actions_overlap_weighted": round(obs.both_actions_overlap, 4),
            "renewal_route_internal_ceiling": ceiling,
            "internal_exceeds_the_renewal_routes_ceiling": exceeds,
            "multiple_of_the_ceiling": (
                None if ceiling["ceiling"] is None else round(rate / ceiling["ceiling"], 4)
            ),
        })
    phis = [w["phi_survey"] for w in waves]
    judged = [w for w in waves if w["internal_exceeds_the_renewal_routes_ceiling"] is not None]
    return {
        "what_this_is": (
            "Ofgem Consumer Impacts of Market Conditions, question C4, six waves on one base, "
            "reported behaviour over the past six months. The instrument the finding has asked for "
            "since §11. It separates external from internal switching and it does NOT identify phi."
        ),
        "source": "docs/market_research/gb_domestic_switcher_split_cim_2022_2025.md",
        "per_wave": waves,
        "phi_survey_span": [min(phis), max(phis)],
        "phi_survey_is_not_phi": (
            "phi_survey is external over ALL reported switching, on a base of all households. phi "
            "is external over ACTIVE RENEWALS AT A FIXED-TERM END. The survey's base contains the "
            "SVT route, which contributes to both of its rows, so phi_survey is a route mixture. "
            "Two different populations; the ratio of the survey's two rows is not phi."
        ),
        "why_the_survey_cannot_close_it": (
            "I = s*J_svt + (1-s)*0.35*(1-phi) introduces J_svt, the SVT segment's INTERNAL move "
            "rate, which nothing published establishes. One new equation, one new unknown."
        ),
        # The result that survives all of that, because it needs only J_svt >= 0.
        "internal_exceeds_the_renewal_routes_ceiling_in_every_judged_wave": bool(judged) and all(
            w["internal_exceeds_the_renewal_routes_ceiling"] for w in judged
        ),
        "judged_waves": len(judged),
        "what_that_means": (
            "internal switching is already larger than the ENTIRE fixed-term active-renewal "
            "population, at the most generous published fixed share and with no annualisation. So "
            "most internal switching originates from default/SVT households moving onto a fix with "
            "their existing supplier -- and `simulation/renewals.py` has no such move at all. This "
            "is the published half of the question §9 raised and could not settle: the world's "
            "SVT hazard is calibrated as drift off the SVT PRODUCT and graded against a band of "
            "EXTERNAL changes of supplier, and those differ by exactly this route."
        ),
        "the_constant_is_still": EXTERNAL_SHARE_OF_ACTIVE_RENEWALS,
    }


def published_route_split() -> dict:
    """The whole reading, as the committed artefact carries it."""
    svt = svt_segment_churn_band()
    scored = sorted(set(published_departure_band()) & set(years_with_an_established_figure()))
    per_year: dict[str, dict] = {}
    for year in scored:
        row: dict = {"band_pct": list(published_departure_band()[year])}
        for basis in BASES:
            share = default_tariff_share(year, basis)
            row[basis] = {
                "default_tariff_share": None if share is None else list(share),
                "admissible_svt_churn": admissible_svt_churn(year, basis),
                "forward_at_phi_1": forward_composition(
                    year, basis, 1.0, svt_band=svt["tenure_composed"]
                ),
                "forward_at_phi_1_mix_free": forward_composition(
                    year, basis, 1.0, svt_band=svt["mix_free_envelope"]
                ),
                "phi_admitting_published_svt_band": [
                    phi_admitting(year, basis, svt["tenure_composed"][0]),
                    phi_admitting(year, basis, svt["tenure_composed"][1]),
                ],
            }
            # DERIVED FROM THE TWO VERDICTS, NEVER WRITTEN DOWN. The tenure split is one survey
            # year carried across nine, so a verdict that holds only at that mix is a verdict about
            # 2018. This says, per year, which ones those are -- and 2018's own overshoot is one of
            # them, which is not the answer the leg was written expecting.
            row[basis]["verdict_is_mix_dependent"] = (
                row[basis]["forward_at_phi_1"]["verdict"]
                != row[basis]["forward_at_phi_1_mix_free"]["verdict"]
            )
        per_year[str(year)] = row
    return {
        "what_this_is": (
            "what the PUBLISHED record can and cannot bear about the split of GB domestic "
            "departures between the SVT route and the fixed-term route. Three published series "
            "composed against each other, with no world in the reading except the clearly labelled "
            "`where_the_worlds_point_falls`. Nothing here is fitted and nothing here picks a value."
        ),
        "identity": (
            "R = s * H_svt + (1 - s) * H_fixed, where R is GB domestic ELECTRICITY changes of "
            "supplier over all GB domestic electricity accounts, s is the published default-tariff "
            "account share, and H_svt / H_fixed are external changes of supplier per account-year "
            "WITHIN each segment. One equation, two unknowns: the record admits a line."
        ),
        "the_unestablished_quantity": {
            "name": "phi -- the external share of active fixed-term renewals",
            "value": EXTERNAL_SHARE_OF_ACTIVE_RENEWALS,
            "why_it_is_none": (
                "`svt_rates_active_passive_2016_2025.md` §4's ~35% counts households actively "
                "renewing onto a NEW FIXED DEAL, which includes staying with the same supplier. "
                "The published numerator counts external changes of supplier only. Nothing "
                "published establishes the split."
            ),
            "what_would_close_it": (
                "a domestic instrument separating 'switched supplier' from 'switched tariff with "
                "the same supplier' on one base. Ofgem's Consumer Impacts of Market Conditions "
                "survey fields both and publishes them combined -- "
                "`gb_switching_rate_denominators.md` §7 already records wave 6 being FURTHER from "
                "an adjacent question for exactly this reason."
            ),
        },
        "published_svt_segment_churn": {
            k: list(v) for k, v in svt_segment_churn_band().items()
        },
        "published_fixed_active_renewal_share": FIXED_ACTIVE_RENEWAL_SHARE,
        "bases": list(BASES),
        "years_scored": [str(y) for y in scored],
        "n_years_scored": len(scored),
        "years_refused": _refused_years(),
        # The overshoot that does NOT depend on the single published tenure survey. Any year outside
        # this set overshoots only at the 2018 mix, and saying so is the difference between a
        # statement about the record and a statement about one survey.
        "years_above_the_band_on_every_tenure_mix": {
            basis: [
                y for y, row in per_year.items()
                if row[basis]["forward_at_phi_1"]["verdict"] == "above"
                and row[basis]["forward_at_phi_1_mix_free"]["verdict"] == "above"
            ]
            for basis in BASES
        },
        "per_year": per_year,
        "where_the_worlds_point_falls": where_the_worlds_point_falls(),
        # The correction to the section above it, and it is published BESIDE it rather than
        # replacing it: a reader who sees only the joint reading cannot tell that the mixed one was
        # ever taken, and §11's result 2 was drawn from the mixed one.
        "where_the_worlds_joint_point_falls": where_the_worlds_joint_point_falls(),
        # §13. The two readings that need NO world, published beside the ones that do, because
        # §12's premise -- that an empty phi intersection is a statement about the world -- can only
        # be checked by asking the record the same question on its own.
        "whether_a_constant_phi_survives_the_record_alone":
            whether_a_constant_phi_survives_the_record_alone(),
        "how_much_of_the_records_move_the_share_series_can_carry":
            how_much_of_the_records_move_the_share_series_can_carry(),
        # §14. The question §13 handed on, answered with the second observation it asked for.
        # Published as its own section rather than folded into the one above it, because the
        # sections above answer "what does the record admit" and this one answers "and does that
        # answer belong to the record or to one survey year" -- which is a different question and
        # has a different failure mode.
        "whether_the_constant_phi_verdict_turns_on_one_survey_year":
            whether_the_constant_phi_verdict_turns_on_one_survey_year(),
        "whether_the_survey_split_identifies_phi": whether_the_survey_split_identifies_phi(),
        "how_to_regenerate": "python3 -m tools.published_route_split --write",
    }


def main(argv: list[str]) -> int:
    reading = published_route_split()
    svt = reading["published_svt_segment_churn"]
    print()
    print("  THE PUBLISHED ROUTE SPLIT — three published series, no world in them")
    print()
    print(f"  published SVT segment churn, tenure-composed: "
          f"{svt['tenure_composed'][0]:.4f}–{svt['tenure_composed'][1]:.4f} per account-year")
    print(f"  mix-free envelope:                            "
          f"{svt['mix_free_envelope'][0]:.4f}–{svt['mix_free_envelope'][1]:.4f}")
    print(f"  published fixed active-renewal share:         "
          f"{FIXED_ACTIVE_RENEWAL_SHARE}  × phi, and phi is {EXTERNAL_SHARE_OF_ACTIVE_RENEWALS}")
    print()
    for basis in BASES:
        print(f"  basis = {basis}")
        print(f"  {'year':>6} {'band %':>13} {'share':>13} {'composed % @phi=1':>19} "
              f"{'verdict':>9} {'admissible H_svt':>20}")
        for year_s, row in reading["per_year"].items():
            cell = row[basis]
            fwd, adm = cell["forward_at_phi_1"], cell["admissible_svt_churn"]
            share = cell["default_tariff_share"]
            print(
                f"  {year_s:>6} {row['band_pct'][0]:>6.1f}–{row['band_pct'][1]:<6.1f} "
                f"{share[0]:>6.3f}–{share[1]:<6.3f} "
                f"{fwd['composed_pct'][0]:>8.1f}–{fwd['composed_pct'][1]:<9.1f} "
                f"{fwd['verdict']:>9} "
                f"{adm['admissible'][0]:>9.3f}–{adm['admissible'][1]:<9.3f}"
            )
        print()
    for year_s, reason in reading["years_refused"].items():
        print(f"  REFUSED {year_s}: {reason}")
    print()
    print(f"  scored {reading['n_years_scored']} years; "
          f"refused {len(reading['years_refused'])}.")
    print("  The admissible interval is WIDE because phi is unestablished, not because the")
    print("  arithmetic is loose. The record cannot settle SVT_INERTIA_ANNUAL_RECENT until it is.")
    print()
    joint = reading["where_the_worlds_joint_point_falls"]
    if joint is None:
        print("  JOINT READING UNAVAILABLE: a committed world artefact is absent. Regenerate with")
        print("  `python3 -m tools.fit_year_level_anchor --svt-shortfall --composition`.")
        print()
    else:
        mixed = reading["where_the_worlds_point_falls"] or {"per_year": {}}
        acc = joint["headline_accounting"]
        print(f"  THE JOINT PAIR — §9's hazard and §10's share moved together, accounting = {acc}")
        print("  (`required` is §9's, solved at the WORLD's share and so sized to do all the work;")
        print("   `H_joint` is what is left after composition has done its part. Both are the same")
        print("   world; only the mixed one is compared against a share it was not solved at.)")
        print()
        for basis in BASES:
            print(f"  basis = {basis}   (published share at its HIGH endpoint)")
            print(f"  {'year':>6} {'required':>9} {'H_joint':>9} {'admissible H_svt':>21} "
                  f"{'in?':>4} {'phi (joint)':>19} {'phi (mixed, §11)':>19}")
            for year_s, row in joint["per_year"].items():
                ep = row.get(basis, {}).get("at_published_high")
                if ep is None or acc not in ep["accountings"]:
                    continue
                cell = ep["accountings"][acc]
                lo, hi = ep["admissible_svt_churn_at_this_share"]
                was = mixed["per_year"].get(year_s, {}).get(basis, {}).get("phi_admitting_required")
                phi = cell["phi_admitting_joint"]
                print(
                    f"  {year_s:>6} "
                    f"{row['required_hazard_holding_the_worlds_share_fixed']:>9.4f} "
                    f"{cell['joint_required_hazard']:>9.4f} "
                    f"{lo:>9.4f}–{hi:<10.4f} "
                    f"{('YES' if cell['joint_hazard_is_admissible'] else 'no'):>4} "
                    f"{phi[0]:>8.3f}–{phi[1]:<9.3f} "
                    f"{(f'{was[0]:>8.3f}–{was[1]:<9.3f}' if was else ' ' * 18)}"
                )
            refused = joint["years_the_record_refuses_the_joint_pair"][basis]
            flipped = joint["years_the_mixed_pair_refused_and_the_joint_pair_admits"][basis]
            print(f"    record refuses the joint pair in: {refused or 'no year'}")
            print(f"    mixed pair refused, joint pair admitted: {flipped or 'no year'}")
            print()
        for year_s, reason in joint["years_refused"].items():
            print(f"  JOINT REFUSED {year_s}: {reason}")
        print()
    const = reading["whether_a_constant_phi_survives_the_record_alone"]
    print("  DOES THE RECORD ADMIT ONE CONSTANT phi? — no world in this section at all")
    print("  (H_svt free per year inside the named segment band; phi held constant across years.)")
    print()
    for basis in BASES:
        pair = const["constant_pair"][basis]
        print(f"  basis = {basis}")
        for band_name in const["published_segment_bands"]:
            band = const["published_segment_bands"][band_name]
            print(f"    H_svt in {band[0]:.4f}–{band[1]:.4f}  ({band_name})")
            for set_name in const["year_sets"]:
                cell = const["verdicts"][basis][band_name][set_name]
                lo, hi = cell["intersection"]
                refusing = ", ".join(f"{a}/{b}" for a, b in cell["minimal_refusing_pairs"])
                print(
                    f"      {set_name:>42}  n={cell['n_years']}  "
                    f"phi = [{lo:>7.4f}, {hi:>7.4f}]  "
                    f"{'ADMITS' if cell['is_non_empty'] else 'REFUSES'}"
                    + (f"   refused by: {refusing}" if refusing else "")
                )
        print(f"    a constant PAIR (one H_svt AND one phi, H swept freely): "
              f"{'ADMITTED' if pair['any_constant_pair_admitted'] else 'REFUSED'} — "
              f"widest slack {pair['widest_slack']['slack']:+.4f} at H_svt="
              f"{pair['widest_slack']['at_h_svt']:.4f}")
        mix_dep = const["verdicts"][basis]["verdict_is_mix_dependent"]
        print(f"    verdict_is_mix_dependent: "
              f"{ {k: v for k, v in mix_dep.items()} }")
        print()
    for year_s, reason in const["structural_breaks"].items():
        row = const["per_year"][year_s]
        print(f"  STRUCTURAL BREAK {year_s} — excluded from the headline, phi span "
              f"{row['all_domestic']['tenure_composed']} (tenure-composed, all_domestic)")
        print(f"    {reason.split('.')[0]}.")
    print()
    carry = reading["how_much_of_the_records_move_the_share_series_can_carry"]
    print("  WHICH OF THE TWO MOVES — the published share series, or behaviour")
    print("  (largest step the share series can supply with BOTH behavioural parameters constant.)")
    print()
    for band_name, by_basis in carry["by_band"].items():
        for basis, cell in by_basis.items():
            print(f"  {band_name} | {basis}: the share series can carry "
                  f"{cell['n_pairs_the_share_series_can_carry']} of {cell['n_pairs_judged']} "
                  f"pairs where the record requires a move")
            for name, pair in cell["pairs"].items():
                flags = " ".join(
                    f for f, on in (
                        ("NO-MOVE-REQUIRED", not pair["record_requires_a_move"]),
                        ("SPANS-GAP", pair["spans_a_gap"]),
                    ) if on
                )
                print(
                    f"    {name:>12}  record [{pair['record_move_pp'][0]:>7.3f},"
                    f"{pair['record_move_pp'][1]:>7.3f}]pp   share can reach "
                    f"[{pair['share_reachable_move_pp'][0]:>7.3f},"
                    f"{pair['share_reachable_move_pp'][1]:>7.3f}]pp   "
                    f"{'carries' if pair['share_can_carry'] else 'CANNOT':>7}  {flags}"
                )
            print()
    turns = reading["whether_the_constant_phi_verdict_turns_on_one_survey_year"]
    print("  DOES THAT VERDICT BELONG TO THE RECORD, OR TO ONE SURVEY YEAR? — §13's question")
    print()
    for obs in turns["observations"]:
        band = obs["composed_band"]
        print(f"    {obs['year']}  long-stayer {obs['long_stayer_pct']:>4.1f}% / recent "
              f"{obs['recent_pct']:>4.1f}%  ->  within-segment "
              f"{obs['long_stayer_share_of_svt']:.4f}  ->  band "
              f"{band[0]:.4f}–{band[1]:.4f}")
        print(f"          {obs['instrument']}; {obs['population']}")
        if obs["restoring_the_excluded_moves_the_long_stayer_share"]:
            print("          restoring the excluded population moves this share "
                  f"{obs['restoring_the_excluded_moves_the_long_stayer_share']}")
    print(f"    the two observations disagree by {turns['the_two_observations_disagree_by']:.4f} "
          "of within-segment share")
    print()
    for band_name, implied in turns["what_each_bands_endpoints_imply_about_the_segment"].items():
        band = turns["bands"][band_name]
        seen = "OBSERVED" if band_name in turns["observed_mix_bands"] else "not observed"
        print(f"    {band_name:>22} {band[0]:.4f}–{band[1]:.4f}  implies a segment "
              f"{implied['implied_by_the_bands_low_end']:.3f}–"
              f"{implied['implied_by_the_bands_high_end']:.3f} long-stayer   [{seen}]")
    lo, hi = turns["the_observed_range_of_the_long_stayer_share"]
    print(f"    anything observed sits between {lo:.4f} and {hi:.4f}")
    print()
    for basis, by_set in turns["by_basis"].items():
        for set_name, cell in by_set.items():
            same = cell["the_verdict_is_the_same_at_every_observed_mix"]
            print(f"    {basis:>13} | {set_name:>42}  "
                  f"same at every observed mix: {'YES' if same else 'NO'}   "
                  f"refuses at every observed mix: "
                  f"{'YES' if cell['refuses_at_every_observed_mix'] else 'no'}   "
                  f"admits ONLY outside them: "
                  f"{'YES' if cell['admits_only_outside_every_observed_mix'] else 'no'}")
    print()
    print(f"  phi is still {EXTERNAL_SHARE_OF_ACTIVE_RENEWALS}. An interval an intersection admits")
    print("  is what phi COULD be if phi were constant; the record does not say that it is.")
    print()
    if "--write" in argv:
        ARTEFACT.write_text(json.dumps(reading, indent=1) + "\n")
        print(f"  wrote {ARTEFACT.relative_to(PROJECT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
