"""People phase 1, re-cut: the physical layer, standing alone.

The director's canon of 2026-09-07 (`DIRECTOR_CANON_THE_DEMAND_VECTOR`, §4) splits
people phase 1 in two:

    THE PHYSICAL LAYER drives kWh and shape: occupancy count, presence pattern,
    heating schedule and setpoint, appliance and asset ownership.

    THE COMMERCIAL LAYER drives payment, arrears, churn and elasticity: income,
    fuel poverty, payment method, credit risk, attitude.

    "Merged, we cannot tell a household that used less because nobody was home
    from one that could not afford it -- and those demand the opposite response
    from a supplier."

That sentence is not a hypothetical here. Both causes are live and both land on
the same number: `away_day_calendar` empties the house (physical) and
`comfort_constraint_for(income_stress=...)` turns the stat down (commercial), and
`fabric_demand_path` folds both into one kWh series with nothing on the record
saying which did it. This module is the seam that keeps them apart.

WHAT IT DOES, AND WHAT IT DELIBERATELY DOES NOT
-----------------------------------------------
It does NOT fork a parallel premise generator. `housing_joint_phase1_what_the_draw
_already_carries.md` is explicit that "anything here that forks a parallel premise
generator is the defect, not the deliverable", and four live modules already hold
the pieces. This assembles them:

  * occupancy      -- `household_segments.OCCUPANCY_POPULATION_SHARE` (ONS Census
                      2021 TS017), which is a PHYSICAL quantity that happens to be
                      housed in the commercial module. See LAYER_OF below.
  * presence       -- `premise_trace.behaviour_profile_for` / `away_day_calendar`
  * schedule       -- `fabric_physics.heating_schedule_for`
  * assets         -- the `Household` record's own ownership fields

ONE THING IT FIXES ON THE WAY. Occupancy had two sources that disagree.
`occupancy_for_customer` draws it from the Census marginal; `behaviour_profile_for`
draws `people_count` from BEDROOMS, on its own substream, because no caller ever
supplied the segmentation field its docstring says attaches "UNCHANGED where a
caller has them". So the population's headcount distribution was a function of the
bedroom draw and not of TS017. This module is that caller: it supplies the
census-anchored count, so the physical layer has one occupancy source instead of
two. Nothing in `premise_trace` changes -- the parameter was always there.

THE CORRELATION IS DECLARED, NOT MERGED
----------------------------------------
The canon asks for the correlations between the layers to be modelled "as
correlations, not as one layer". `LAYER_CORRELATIONS` is where they are declared.
Income-to-occupancy is the one the canon names by example, and it is NOT
established: `segmentation_joint_structure.md` records occupancy as "its own
Census-anchored marginal (TS017), not cross-tabbed to tenure/EPC in any doc
found". So it carries `established=False` and a named reason rather than a
coefficient picked to fill the slot -- an honest gap the reader can see, which a
plausible number would have hidden.
"""

from __future__ import annotations

import dataclasses
import datetime as dt
import random
from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from simulation.fabric_physics import HeatingSchedule, heating_schedule_for
from simulation.household import Household
from simulation.household_segments import OCCUPANCY_POPULATION_SHARE, OccupancyBand
from simulation.premise_trace import (
    BehaviourProfile,
    ComfortConstraint,
    away_day_calendar,
    behaviour_profile_for,
)


class Layer(str, Enum):
    """Which of the canon's two layers an attribute belongs to."""

    PHYSICAL = "physical"
    COMMERCIAL = "commercial"


# Every field of the drawn `Household` record, classified. TOTAL and DISJOINT --
# `test_every_drawn_household_attribute_is_assigned_to_exactly_one_layer` fails
# when a new attribute lands unclassified, which is how the layers would silently
# re-merge. `customer_id` is the join key and belongs to neither, so it is named
# here rather than left to be inferred.
_IDENTITY_FIELDS = frozenset({"customer_id"})

LAYER_OF: dict[str, Layer] = {
    # Fabric and geometry -- what the building is.
    "property_type": Layer.PHYSICAL,
    "build_era": Layer.PHYSICAL,
    "epc_rating": Layer.PHYSICAL,
    "bedrooms": Layer.PHYSICAL,
    "insulation": Layer.PHYSICAL,
    # Heating plant.
    "heating_system": Layer.PHYSICAL,
    "boiler_age": Layer.PHYSICAL,
    # Appliance and asset ownership -- the canon's fourth physical item.
    "has_solar": Layer.PHYSICAL,
    "solar_kwp": Layer.PHYSICAL,
    "solar_install_year": Layer.PHYSICAL,
    "has_battery": Layer.PHYSICAL,
    "battery_kwh": Layer.PHYSICAL,
    "has_ev": Layer.PHYSICAL,
    "ev_charger_kw": Layer.PHYSICAL,
    "has_smart_meter": Layer.PHYSICAL,
    "smart_meter_install_year": Layer.PHYSICAL,
    # Physical suitability for the assets above.
    "has_driveway": Layer.PHYSICAL,
    "roof_aspect": Layer.PHYSICAL,
    # MEASURED FABRIC (2026-09-10), from the NEED-fitted joint the world's stock is now drawn
    # from. Floor area was previously INFERRED inside `fabric_physics.floor_area_m2` from the
    # property type and a bedroom count; it is a drawn fact now, and the insulation measures are
    # what an installer actually fitted rather than what the EPC letter implies.
    "floor_area_band": Layer.PHYSICAL,
    "has_loft_insulation": Layer.PHYSICAL,
    "has_cavity_wall_insulation": Layer.PHYSICAL,
    # PHYSICAL, and the call is worth stating because the obvious reading is the other one.
    # NEED derives this from whether a gas METER could be matched to the dwelling, which sounds
    # like a billing relationship -- and a billing relationship would be commercial. The fact it
    # stands for is not: it is whether the building has a gas connection, which is infrastructure
    # and is true of the dwelling whoever supplies it and however they are billed. The commercial
    # facts about gas -- the tariff, the payment method, the supplier -- are elsewhere and stay
    # there. The derivation caveat is real and is recorded on the field itself: 50.3% of flats
    # read "not gas" when they are communal or unmetered, so this measures a MATCHED METER and is
    # a lower bound on connection.
    "has_mains_gas_supply": Layer.PHYSICAL,
    # WHERE THE HOME IS (W2_19). Physical because what it conditions is the headcount, the
    # ruling's layer one: "the household you would EXPECT given the postcode". An area also
    # correlates with income, but that correlation is to be DECLARED between the layers (see
    # `LayerCorrelation`). It is not a reason to put the address in the commercial layer.
    "output_area": Layer.PHYSICAL,
    # The one commercial attribute on the physical record. This IS the merge the
    # canon names: it sits on `Household` beside the fabric, and
    # `fabric_demand_path` reads it straight off there into the demand path.
    "income_stress": Layer.COMMERCIAL,
}


@dataclass(frozen=True)
class LayerCorrelation:
    """A correlation BETWEEN the layers, declared rather than merged.

    `established` is the load-bearing field. False means we have looked and found
    nothing that fixes the strength -- not that nobody asked. A True row without a
    `source` is refused by
    `test_a_declared_correlation_is_either_sourced_or_openly_unestablished`,
    because an unsourced coefficient is exactly the placeholder that reads as an
    answer.

    `in_the_world` is a different question from `established`, and the difference is the point:
    `established` asks whether the REAL strength is known; `in_the_world` asks whether OUR draw
    carries any association at all. The first is answered from the published record, the second
    only by measuring the draw -- `measure_layer_associations` below, over the attributes named in
    `measured_as`. A row declared absent that the draw carries, or a carried association with no
    row, is the canon's "correlation assumed rather than measured", and
    `test_every_association_the_world_draws_between_the_layers_is_declared` goes red on either.
    """

    physical: str
    commercial: str
    established: bool
    source: str | None
    reason: str
    in_the_world: bool
    measured_as: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.established and not self.source:
            raise ValueError(
                f"the {self.physical} <-> {self.commercial} correlation claims to be "
                "established and names no source"
            )


LAYER_CORRELATIONS: tuple[LayerCorrelation, ...] = (
    LayerCorrelation(
        physical="occupancy",
        commercial="income_stress",
        established=False,
        source=None,
        reason=(
            "the canon names income -> house size -> occupancy as real, and nothing "
            "read establishes its strength. Occupancy is anchored on ONS Census 2021 "
            "TS017 as a MARGINAL; segmentation_joint_structure.md records it as 'not "
            "cross-tabbed to tenure/EPC in any doc found'. Closing this needs a "
            "published cross-tabulation of household size against income, which no "
            "source in the commons carries. The FRS/HBAI low-income rates by family type "
            "(POPULATION_COVERAGE_SOURCE_LANDSCAPE.md, 'apply') are the nearest candidate and "
            "are keyed on composition, not headcount. Until then the two are drawn "
            "independently and the sample is NOT claimed to span the joint. MEASURED "
            "2026-09-30 at 2025-12-31: chi2 5.6/6 dof (seed 11, n 1954) and 6.9/6 (seed 23, "
            "n 2040) -- independent, as declared."
        ),
        in_the_world=False,
        measured_as=("occupancy",),
    ),
    LayerCorrelation(
        physical="asset_ownership",
        commercial="income_stress",
        established=False,
        source=None,
        reason=(
            "solar/EV/battery co-ownership against tenure and income is carried in "
            "the population-coverage register as 'assumed', not fused. W1_10 models "
            "adoption as spatially correlated by region, which is a different joint: "
            "it says WHERE adopters are, not WHO they are. Nothing in the draw conditions "
            "adoption on income stress; measured 2026-09-30, every asset field is independent "
            "of it at the control's threshold."
        ),
        in_the_world=False,
        measured_as=("has_solar", "has_battery", "has_ev", "has_smart_meter", "has_driveway"),
    ),
    # FOUND BY MEASURING, 2026-09-30, not declared by anyone before. The draw CARRIES this one,
    # at Cramer's V 0.14 (p < 1e-11 on two seeds), and it is the only cross-layer association it
    # carries. The path is `life_events._RETIREMENT_PROB_BY_ERA`: retirement, a commercial
    # transition (LOW -> MODERATE), fires on the DWELLING's build era, on the premise that a
    # 1945-64 house holds people born 1945-64. `boiler_age` is drawn from the era and rides the
    # same path. Declared here because it is real in the world; whether it should BE real is
    # the life-events lane's question, filed rather than fixed from this seam.
    LayerCorrelation(
        physical="build_era",
        commercial="income_stress",
        established=False,
        source=None,
        reason=(
            "carried by the draw through life_events._RETIREMENT_PROB_BY_ERA, which keys "
            "retirement on the dwelling's build era as a proxy for its occupants' birth "
            "cohort. Nothing read establishes that a house's age predicts its occupants' "
            "age, and composition_cuts_for draws pensioner_present on the physical layer "
            "independently of that retirement, so the world holds two answers to 'is "
            "someone here retired'. Closing it needs the EHS age-of-HRP by dwelling-age "
            "cross-tab, or the retirement keyed on the drawn pensioner instead."
        ),
        in_the_world=True,
        measured_as=("build_era", "boiler_age"),
    ),
)


# Within-band headcount, from the same ONS Census 2021 TS017 note that anchors
# OCCUPANCY_POPULATION_SHARE in `household_segments`: 3-person 16.0% / 4-person
# 12.9% inside the 3-4 band, and 5/6/7/8+ at 4.5/1.5/0.5/0.4% inside the 5+ band.
# The shares are the published ones; only the renormalisation within band is done
# here, so no headcount number is invented.
_WITHIN_BAND_SHARES: dict[OccupancyBand, tuple[tuple[int, float], ...]] = {
    OccupancyBand.ONE_PERSON: ((1, 1.0),),
    OccupancyBand.TWO_PERSON: ((2, 1.0),),
    OccupancyBand.THREE_TO_FOUR_PERSON: ((3, 0.160), (4, 0.129)),
    OccupancyBand.FIVE_PLUS_PERSON: ((5, 0.045), (6, 0.015), (7, 0.005), (8, 0.004)),
}


def people_count_for(customer_id: str, output_area: str | None = None) -> int:
    """The household's headcount. ONE draw for this home, wherever in the world it is asked.

    THE DEFECT THIS CLOSES (measured 2026-09-17). This function drew its own headcount from the
    TS017 marginal, and `dwelling_records.people_count_for_area` drew ANOTHER one for the same
    home to build its property record. Both are correct draws from the same published
    distribution, on different named substreams -- so the book's two paths disagreed about how
    many people live in a house for **102 of 134 homes**, by up to five people. Neither
    distribution was wrong: property mean 2.388, this one 2.485, ONS 2.37. The per-home
    ASSIGNMENT was two different answers to one question.

    That is the same shape `occupancy_band_for` below names in its own docstring -- *"two draws of
    one quantity is the defect this module just fixed"* -- committed again one module over, which
    is why the fix is delegation rather than a second copy of the right formula.

    AND THE DELEGATE IS THE RICHER ONE, deliberately. `people_count_for_area` conditions on the
    premise's output area where one exists and falls back to the national draw visibly through
    `people_count_source`.

    `output_area` is threaded rather than looked up here: this module has no address book, and a
    lookup invented here would be a third answer to the same question. Every caller in this module
    passes `household.output_area`. The day homes gained areas (W2_19, 2026-09-27), the one caller
    here that passed only the id would have been national while the property record was local.
    `test_one_home_has_one_headcount` checks that exact disagreement over the live book.
    """
    from simulation.dwelling_records import people_count_for_area

    return people_count_for_area(customer_id, output_area)


def _national_headcount_draw(customer_id: str) -> int:
    """The band-then-within-band draw this module used before it delegated.

    KEPT AND STILL EXERCISED because `_WITHIN_BAND_SHARES` above is the only place the published
    within-band split (3-person 16.0% / 4-person 12.9%, and 5/6/7/8+ at 4.5/1.5/0.5/0.4%) is
    written down, and deleting the only caller would leave that table unreachable and unverified.
    It is NOT the world's headcount any more -- `people_count_for` is -- and nothing outside this
    module's own tests may call it, or the defect above comes straight back.
    """
    rng = random.Random(f"physical_layer_people_count_{customer_id}")
    roll = rng.random()
    cumulative = 0.0
    for band, share in OCCUPANCY_POPULATION_SHARE.items():
        cumulative += share
        if roll < cumulative:
            return _headcount_within(band, customer_id)
    return _headcount_within(OccupancyBand.FIVE_PLUS_PERSON, customer_id)


def occupancy_band_for(customer_id: str, output_area: str | None = None) -> OccupancyBand:
    """The band the headcount above falls in. Derived from the count, never drawn
    beside it -- two draws of one quantity is the defect this module just fixed."""
    count = people_count_for(customer_id, output_area)
    if count == 1:
        return OccupancyBand.ONE_PERSON
    if count == 2:
        return OccupancyBand.TWO_PERSON
    if count <= 4:
        return OccupancyBand.THREE_TO_FOUR_PERSON
    return OccupancyBand.FIVE_PLUS_PERSON


def _headcount_within(band: OccupancyBand, customer_id: str) -> int:
    options = _WITHIN_BAND_SHARES[band]
    if len(options) == 1:
        return options[0][0]
    rng = random.Random(f"physical_layer_within_band_{band.value}_{customer_id}")
    total = sum(share for _, share in options)
    roll = rng.random() * total
    cumulative = 0.0
    for count, share in options:
        cumulative += share
        if roll < cumulative:
            return count
    return options[-1][0]


@dataclass(frozen=True)
class PhysicalLayer:
    """One household's physical layer, assembled and standing alone.

    Nothing on this record is read from the commercial layer. That is asserted by
    `test_the_physical_layer_does_not_move_when_only_the_commercial_layer_moves`,
    which is the control that would go red if a later change wired income back in.
    """

    customer_id: str
    occupancy_band: OccupancyBand
    people_count: int
    children_count: int
    pensioner_present: bool
    someone_employed: bool
    daytime_occupancy: float
    away_days_per_year: int
    schedule: HeatingSchedule
    assets: dict[str, object]

    @property
    def comfort_setpoint_c(self) -> float:
        return self.schedule.comfort_setpoint_c

    def presence_profile(self) -> BehaviourProfile:
        """The presence half of this layer, in the shape `away_day_calendar`
        reads. Built from the record's OWN fields rather than re-drawn, so the
        away calendar cannot disagree with the record it is attributed against."""
        return _profile_from(self)


def physical_layer_for(
    customer_id: str,
    household: Household,
    *,
    seed: int | None = None,
) -> PhysicalLayer:
    """Assemble the physical layer for one household.

    Reads only physical attributes of `household`. The commercial ones are on the
    same record -- `income_stress` is right there -- and are deliberately not
    touched: that restraint is the deliverable, and the control names it.
    """
    profile = _profile_for(customer_id, household, seed=seed)
    schedule = heating_schedule_for(customer_id, household, seed=seed)
    assets = {
        name: getattr(household, name)
        for name, layer in LAYER_OF.items()
        if layer is Layer.PHYSICAL and name in _ASSET_FIELDS
    }
    return PhysicalLayer(
        customer_id=customer_id,
        occupancy_band=occupancy_band_for(customer_id, household.output_area),
        people_count=profile.people_count,
        children_count=profile.children_count,
        pensioner_present=profile.pensioner_present,
        someone_employed=profile.someone_employed,
        daytime_occupancy=profile.daytime_occupancy,
        away_days_per_year=profile.away_days_per_year,
        schedule=schedule,
        assets=assets,
    )


_ASSET_FIELDS = frozenset(
    {
        "has_solar",
        "solar_kwp",
        "has_battery",
        "battery_kwh",
        "has_ev",
        "ev_charger_kw",
        "has_smart_meter",
        "has_driveway",
    }
)


def _profile_for(
    customer_id: str, household: Household, *, seed: int | None
) -> BehaviourProfile:
    """`behaviour_profile_for`, given the census-anchored headcount it always
    accepted and never received."""
    return behaviour_profile_for(
        customer_id,
        household,
        seed=seed,
        people_count=people_count_for(customer_id, household.output_area),
    )


# ---------------------------------------------------------------------------
# The discriminator -- nobody home, or could not afford it
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ComfortAttribution:
    """Why a household's comfort is below its own schedule, by layer.

    The two causes are reported SEPARATELY and are never summed. They are not in
    the same units -- days absent is a count of days, setpoint reduction is
    degrees applied to every heated day -- and dividing or adding them would
    manufacture a quantity that counts nothing. Where both are present the
    attribution refuses to rank them and says so; `counterfactual_recipe` names
    the run that would settle it.
    """

    customer_id: str
    days_absent: int
    days_observed: int
    absent_share: float
    setpoint_reduction_c: float
    comfort_hours_lost: float
    rationing_intensity: float
    dominant_layer: Layer | None
    why_not_ranked: str | None

    @property
    def presence_is_a_cause(self) -> bool:
        return self.days_absent > 0

    @property
    def affordability_is_a_cause(self) -> bool:
        return self.rationing_intensity > 0.0

    @property
    def counterfactual_recipe(self) -> str | None:
        """What to run to split the kWh, when the attribution cannot rank.

        Only where BOTH causes are live. `dominant_layer is None` is also how the
        nothing-to-attribute case reads, and offering a split recipe there would
        send a reader to run two counterfactuals over a household whose comfort
        nothing reduced.
        """
        if not (self.presence_is_a_cause and self.affordability_is_a_cause):
            return None
        return (
            "run build_fabric_demand_series twice over the same weather and "
            "household: once with away_days forced empty, once with "
            "ComfortConstraint.unconstrained(). The difference of each against "
            "the base run is that layer's kWh, and only then is one bigger than "
            "the other."
        )


def attribute_lost_comfort(
    layer: PhysicalLayer,
    constraint: ComfortConstraint,
    dates: Sequence[dt.date],
    *,
    seed: int | None = None,
) -> ComfortAttribution:
    """Separate the presence cause from the affordability cause.

    This is the director's sentence made readable: a supplier holding this record
    can tell the household that was away from the household that turned the stat
    down, and those two want opposite things done to their direct debit.

    It refuses to rank the two when both are live. That refusal is the honest
    answer and it is reachable -- a household can perfectly well be both away in
    August and rationing in January.
    """
    if not dates:
        raise ValueError("attribute_lost_comfort needs at least one date")
    observed = set(dates)
    # `away_day_calendar` distributes the household's whole YEAR of away days
    # across the dates it is handed -- hand it a month and the household takes all
    # its holidays that month. So the calendar is always drawn over the full
    # calendar years the window touches, and the window is intersected afterwards.
    # Attribution over a supplier's real observation period (a billing month) is
    # the whole point of this function, and getting that wrong made every
    # household absent in every window.
    away = away_day_calendar(
        layer.customer_id, layer.presence_profile(), _full_years_spanning(observed), seed=seed
    )
    days_absent = len(away & observed)
    days_observed = len(observed)

    dominant, why = _rank(
        presence=days_absent > 0,
        affordability=constraint.rationing_intensity > 0.0,
    )
    return ComfortAttribution(
        customer_id=layer.customer_id,
        days_absent=days_absent,
        days_observed=days_observed,
        absent_share=days_absent / days_observed,
        setpoint_reduction_c=constraint.setpoint_reduction_c,
        comfort_hours_lost=1.0 - constraint.comfort_hours_retained,
        rationing_intensity=constraint.rationing_intensity,
        dominant_layer=dominant,
        why_not_ranked=why,
    )


def _rank(*, presence: bool, affordability: bool) -> tuple[Layer | None, str | None]:
    """Which layer dominates, or the refusal and its reason.

    Two of the four outcomes are refusals and they are DIFFERENT refusals: one
    says we cannot yet tell, the other says there is nothing to tell. Collapsing
    them would send a reader to run a counterfactual over a household whose
    comfort nothing reduced.
    """
    if presence and affordability:
        return None, (
            "both layers are reducing this household's comfort and they are not "
            "commensurable: days absent is a count of days, setpoint reduction is "
            "degrees on every heated day. We cannot yet tell which is the larger "
            "share of the kWh without running the counterfactual."
        )
    if presence:
        return Layer.PHYSICAL, None
    if affordability:
        return Layer.COMMERCIAL, None
    return None, "neither layer is reducing comfort: there is nothing to attribute."


def _full_years_spanning(observed: set[dt.date]) -> list[dt.date]:
    """Every day of every calendar year the observation window touches."""
    days: list[dt.date] = []
    for year in sorted({d.year for d in observed}):
        day = dt.date(year, 1, 1)
        while day.year == year:
            days.append(day)
            day += dt.timedelta(days=1)
    return days


def _profile_from(layer: PhysicalLayer) -> BehaviourProfile:
    return BehaviourProfile(
        people_count=layer.people_count,
        children_count=layer.children_count,
        pensioner_present=layer.pensioner_present,
        someone_employed=layer.someone_employed,
        wake_period=13,
        sleep_period=45,
        weekend_shift_periods=2,
        daytime_occupancy=layer.daytime_occupancy,
        away_days_per_year=layer.away_days_per_year,
        appliance_intensity=(layer.people_count / 2.4) ** 0.6,
    )


def unclassified_household_fields() -> tuple[str, ...]:
    """Fields of the drawn `Household` that `LAYER_OF` does not place.

    The census the control runs. Returned rather than asserted so a caller can
    report WHICH attribute went unplaced, not merely that one did.
    """
    known = set(LAYER_OF) | _IDENTITY_FIELDS
    return tuple(
        f.name for f in dataclasses.fields(Household) if f.name not in known
    )


#: Above this many distinct values a chi-square over a book of a few thousand homes has cells too
#: thin to read (an output area has thousands), so the pair is returned UNMEASURED with that
#: reason rather than given a statistic that means nothing.
_MAX_LEVELS_FOR_A_CONTINGENCY = 12


@dataclass(frozen=True)
class LayerAssociation:
    """One physical attribute against one commercial one, as the draw actually has them.

    `chi2` is None when the pair could not be measured, and `unmeasured_because` says why.
    Cramer's V is reported beside the statistic because chi-square alone grows with the book: V
    is the strength, chi2 with its dof is whether it is there at all.
    """

    physical: str
    commercial: str
    n: int
    chi2: float | None
    dof: int
    cramers_v: float | None
    unmeasured_because: str | None = None


def measure_layer_associations(
    homes: Sequence[tuple[str, Household, Household]],
) -> list[LayerAssociation]:
    """Measure every physical attribute against every commercial one over a drawn book.

    `homes` is `(customer_id, household as drawn, household at the date measured)`. The commercial
    layer MOVES -- income stress changes through life events and starts LOW for every home -- so a
    reading at the draw would find nothing and prove nothing; the caller picks the date. Physical
    fields are read at the same date, because assets are adopted over the run. `occupancy` is read
    off the assembled physical layer, which is the headcount the demand path sees.

    Continuous fields (kWp, kWh, kW) are not measured: a contingency over a float is a table of
    ones. They are not silently dropped either -- their integer siblings (`has_solar`, ...) carry
    the ownership question.
    """
    physical_values: dict[str, list[str]] = {"occupancy": []}
    commercial_values: dict[str, list[str]] = {}
    for customer_id, drawn, at_date in homes:
        physical_values["occupancy"].append(
            occupancy_band_for(customer_id, drawn.output_area).value
        )
        for name, layer in LAYER_OF.items():
            value = getattr(at_date, name)
            if isinstance(value, float):
                continue
            target = physical_values if layer is Layer.PHYSICAL else commercial_values
            target.setdefault(name, []).append(str(getattr(value, "value", value)))

    out: list[LayerAssociation] = []
    for commercial, cvals in commercial_values.items():
        for physical, pvals in physical_values.items():
            out.append(_association(physical, commercial, pvals, cvals))
    return out


def _association(
    physical: str, commercial: str, pvals: list[str], cvals: list[str]
) -> LayerAssociation:
    n = len(pvals)
    rows, cols = sorted(set(pvals)), sorted(set(cvals))
    if len(rows) < 2 or len(cols) < 2:
        return LayerAssociation(physical, commercial, n, None, 0, None,
                                f"{physical if len(rows) < 2 else commercial} takes one value "
                                "over the whole book, so there is nothing to associate")
    if len(rows) > _MAX_LEVELS_FOR_A_CONTINGENCY:
        return LayerAssociation(physical, commercial, n, None, 0, None,
                                f"{physical} takes {len(rows)} values, too many for a "
                                f"contingency over {n} homes")
    counts: dict[tuple[str, str], int] = {}
    for p, c in zip(pvals, cvals):
        counts[(p, c)] = counts.get((p, c), 0) + 1
    row_total = {r: sum(counts.get((r, c), 0) for c in cols) for r in rows}
    col_total = {c: sum(counts.get((r, c), 0) for r in rows) for c in cols}
    chi2 = 0.0
    for r in rows:
        for c in cols:
            expected = row_total[r] * col_total[c] / n
            chi2 += (counts.get((r, c), 0) - expected) ** 2 / expected
    k = min(len(rows), len(cols)) - 1
    return LayerAssociation(physical, commercial, n, chi2,
                            (len(rows) - 1) * (len(cols) - 1), (chi2 / (n * k)) ** 0.5)
