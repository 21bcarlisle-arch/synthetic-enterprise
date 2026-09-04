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
from pathlib import Path

from simulation.market_switching_propensity import published_departure_band
from tools.published_tariff_mix import default_tariff_share, years_with_an_established_figure

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

#: Ofgem Consumer Engagement Survey 2018, via the same §2: 29% of customers on SVT 3+ years, 23% on
#: SVT under 3 years. Within the SVT segment that is 29/(29+23) long-stayer.
#:
#: IT IS ONE YEAR'S READING AND IT IS CARRIED ACROSS ALL OF THEM, which is a real weakness and the
#: reason `svt_segment_churn_band` also returns `mix_free_envelope`. The envelope is the two rows'
#: outer hull -- every tenure mix that could exist -- and every verdict below is checked to be the
#: same on both. A conclusion that held only at the 2018 mix would be a conclusion about 2018.
SVT_TENURE_SURVEY_LONG_STAYER_PCT = 29.0
SVT_TENURE_SURVEY_RECENT_PCT = 23.0

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

BASES = ("as_published", "all_domestic")


def svt_segment_churn_band() -> dict[str, tuple[float, float]]:
    """The published SVT segment's external churn band, composed and mix-free.

    `tenure_composed` weights the two published rows by the one published tenure split. It is the
    best available reading and it rests on a single survey year.

    `mix_free_envelope` is `(min of the low ends, max of the high ends)` -- the value the segment
    could take under ANY tenure mix, including mixes nobody has measured. It is strictly wider and
    it is what a verdict has to survive to be a verdict about the record rather than about 2018.
    """
    long_share = SVT_TENURE_SURVEY_LONG_STAYER_PCT / (
        SVT_TENURE_SURVEY_LONG_STAYER_PCT + SVT_TENURE_SURVEY_RECENT_PCT
    )
    composed = tuple(
        round(long_share * long_end + (1.0 - long_share) * recent_end, 6)
        for long_end, recent_end in (
            (SVT_CHURN_LONG_STAYER[0], SVT_CHURN_RECENT[0]),
            (SVT_CHURN_LONG_STAYER[1], SVT_CHURN_RECENT[1]),
        )
    )
    return {
        "tenure_composed": composed,  # type: ignore[dict-item]
        "mix_free_envelope": (
            min(SVT_CHURN_LONG_STAYER[0], SVT_CHURN_RECENT[0]),
            max(SVT_CHURN_LONG_STAYER[1], SVT_CHURN_RECENT[1]),
        ),
        "long_stayer_share_of_svt": (round(long_share, 6), round(long_share, 6)),
    }


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
    if "--write" in argv:
        ARTEFACT.write_text(json.dumps(reading, indent=1) + "\n")
        print(f"  wrote {ARTEFACT.relative_to(PROJECT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
