"""Per-household seasonal gas shape — the gas half of W2_30, published as MODELLED
and explicitly NOT VALIDATED.

WHAT WAS ALREADY BUILT, AND WHY THIS IS NOT A SECOND COPY OF IT
---------------------------------------------------------------
W2_30 names two deliverables. The ELECTRICITY one is already shipped and wired:
`simulation.fabric_demand_path.fabric_providers_for_book` drives every eligible
premise's half-hourly electricity from W1_11 fabric physics and W1_12 behaviour,
`run_phase2b` settles real money off it, and `tools/book_shape_spread.py` measures
that the result is a genuine spread rather than rescaled copies of one profile
(2022-01, 5,778 pairs: mean absolute half-hourly share difference 0.006463 on the
fabric path against 0.003446 on the legacy one, and the legacy path's closest pair
— family1 vs single1 — sits at 1.6e-4, which is the collapse the switch exists to
remove). Nothing here re-implements any of that; this module never generates a
shape.

The GAS one is not wired, and `run_phase2b` says why in its own words: "GAS IS
DELIBERATELY NOT SWITCHED. `run_gas_term` takes an AQ, not a shape_fn ... Driving
gas demand from fabric while the AQ belief stays frozen at its declared value would
lock in a permanent 4x hedge mismatch no real supplier could carry."

THAT OBJECTION IS CORRECT AND IT DOES NOT APPLY TO WHAT THE CANON ASKED FOR.
DIRECTOR_CANON_THE_DEMAND_VECTOR_2026-09-07 sets the two resolutions from the
PRICE, not the physics: electricity needs half-hourly because that is where the
price and the settlement live; gas needs only a SEASONAL shape, because the price
does not move within a month. A seasonal shape is a statement about WHEN the year's
volume is consumed, not about how much of it there is. So this module changes the
shape and never the level — the AQ belief is untouched, and the 4x mismatch that
stopped the switch cannot arise from a term that conserves the annual total by
construction (`level_is_preserved` is the failable control for exactly that).

WHAT IS ACTUALLY WRONG TODAY
----------------------------
`gas_settlement.resi_daily_gas_kwh` splits every domestic customer's gas 70/30 —
70% space heating scaling with the day's HDD, 30% DHW and cooking flat year-round.
`_GAS_BOILER_HEATING_FRACTION = 0.70` is sourced (DUKES Table 4.3, calibrated to a
Jan:Jul ratio of ~5.3x) and it is a POPULATION AVERAGE being used as a PER-HOUSEHOLD
parameter. Two homes at the same AQ — a pre-1919 detached with poor insulation and
a post-2000 flat with full insulation and four occupants — do not have the same
split, and under the shipped code they have exactly the same one, to every decimal
place. That is the gas twin of the electricity defect: identical shape wearing
different levels.

WHAT THIS MODULE DOES
---------------------
It PROJECTS a household's own fabric-physics daily gas series onto the two-term form
settlement already consumes, and reports the fraction that projection implies. It
fits, it does not generate: the physics is W1_11/W1_12's, the parameterisation is
`gas_settlement`'s, and this is the seam between them. One implementation of the
daily formula exists and it lives in `gas_settlement`; the control here calls THAT
function rather than restating it, so a change to settlement's arithmetic cannot
leave this module quietly agreeing with a formula nobody uses any more.

NOT VALIDATED, AND THAT IS A DIRECTOR DECISION, NOT A GAP TO CLOSE
------------------------------------------------------------------
Canon section 6: the only household shape artefact available is Elexon Profile Class
1 — one population-average curve on a 1997 reference year — and NEED is annual. SERL
has half-hourly with EPC linkage but is accredited-access and is NOT pursued. So
every split this module returns carries `validated=False`, permanently, and
`NOT_VALIDATED_STATEMENT` is the sentence that must appear on the reader-facing
surface rather than in a footnote. A row that closes claiming validated shape has
crossed a director decision, not raised a level. `validated` is not a field a caller
may set: there is no argument for it and no code path that produces True.

AN HONEST NONE, NEVER A PLAUSIBLE NUMBER
-----------------------------------------
A window that cannot separate the two terms — no cold days, no warm days, or a
series that does not respond to cold at all — returns a `SeasonalGasRefusal` naming
its reason, and the caller keeps the population constant and says so. That is the
same shape `fabric_demand_path` uses for coverage: the refusal is decided before any
settlement happens and the reason is carried into the run's own record.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

from simulation.gas_settlement import (
    GAS_HDD_REFERENCE_ANNUAL,
    resi_daily_gas_kwh,
)

#: The sentence the reader-facing surface must carry, verbatim, beside any per-household
#: seasonal gas shape. Canon section 6: PC1 is a population average on a 1997 reference
#: year and SERL is accredited-access and not pursued, so nothing here has been checked
#: against a measured household. It is a statement, not a hedge: the shape is modelled,
#: the model is stated, and no observation supports it.
NOT_VALIDATED_STATEMENT = (
    "This household's seasonal gas shape is MODELLED and has NOT been validated against "
    "any measured household. No per-household gas shape observation is available to us: "
    "Elexon Profile Class 1 is one population-average curve on a 1997 reference year, and "
    "SERL's half-hourly panel is accredited-access and is not pursued. The shape follows "
    "from this home's fabric, its occupancy and its weather; the annual volume it is "
    "applied to is the company's own declared AQ and is unchanged by it."
)

#: The minimum spread of daily HDD a window must show before the two terms can be told
#: apart. NOT a domain quantity and not sourced as one: it is the identifiability
#: condition of a two-parameter fit. Below it the heating term and the flat term are
#: collinear, and any fraction between 0 and 1 explains the data equally well -- so the
#: fit would return a number set by rounding noise. 5.0 HDD is a little over a third of
#: the gap between the reference January (350/31 = 11.3 HDD/day) and the reference July
#: (5/31 = 0.16), i.e. a window has to span a real part of the heating season to qualify.
MIN_HDD_SPREAD_FOR_IDENTIFIABILITY = 5.0

#: The minimum number of days a fit is allowed to rest on. A two-parameter fit on a
#: handful of days is arithmetic, not evidence. 60 days is the same floor
#: `premise_trace.daily_variability_is_non_degenerate` already requires of a daily gas
#: series before it will judge one, and it is reused rather than re-chosen.
MIN_DAYS_FOR_FIT = 60


@dataclass(frozen=True)
class SeasonalGasSplit:
    """One household's own seasonal gas split, in the parameterisation
    `gas_settlement.resi_daily_gas_kwh` already consumes.

    `heating_fraction` replaces the population constant for THIS household and nothing
    else: the annual volume stays the company's declared AQ.
    """

    customer_id: str
    heating_fraction: float
    hdd_reference_annual: float
    n_days: int
    hdd_spread: float
    #: Share of the daily series' variance the two-term form accounts for. Reported so a
    #: reader can see how well settlement's shape actually describes this home's physics,
    #: never used as a filter -- a poor fit is a finding about the two-term form, not a
    #: reason to hide the household (R12: a diagnostic, never a target).
    fit_r_squared: float

    @property
    def validated(self) -> bool:
        """Always False, by director decision (canon section 6). There is no argument
        that sets this and no code path that returns True."""
        return False

    def not_validated_statement(self) -> str:
        return NOT_VALIDATED_STATEMENT


@dataclass(frozen=True)
class SeasonalGasRefusal:
    """Why this household has NO per-household seasonal shape, carried rather than
    discarded so a customer silently keeping the population constant is visible in the
    run instead of inferred from its numbers."""

    customer_id: str
    reason: str


def _fit_two_term(
    daily_kwh: Sequence[float], daily_hdd: Sequence[float]
) -> tuple[float, float, float]:
    """Least squares of ``kwh = slope * hdd + intercept``, both terms held non-negative.

    Returns ``(slope, intercept, r_squared)``. A negative fitted intercept means the
    home's summer base is indistinguishable from zero, so the fit is re-run with the
    base pinned at zero rather than a negative base being carried into a fraction --
    the same for a negative slope. Pinning is stated here because it is the only place
    the two-term form is allowed to disagree with the arithmetic.
    """
    n = len(daily_kwh)
    mean_h = sum(daily_hdd) / n
    mean_k = sum(daily_kwh) / n
    s_hh = sum((h - mean_h) ** 2 for h in daily_hdd)
    s_hk = sum((h - mean_h) * (k - mean_k) for h, k in zip(daily_hdd, daily_kwh))
    slope = s_hk / s_hh if s_hh > 0 else 0.0
    intercept = mean_k - slope * mean_h
    if intercept < 0.0:
        # Pin the base at zero and re-fit the slope through the origin.
        slope = (
            sum(h * k for h, k in zip(daily_hdd, daily_kwh)) / sum(h * h for h in daily_hdd)
            if any(h > 0 for h in daily_hdd)
            else 0.0
        )
        intercept = 0.0
    if slope < 0.0:
        slope = 0.0
        intercept = mean_k
    ss_tot = sum((k - mean_k) ** 2 for k in daily_kwh)
    ss_res = sum(
        (k - (slope * h + intercept)) ** 2 for h, k in zip(daily_hdd, daily_kwh)
    )
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return slope, intercept, r_squared


def seasonal_gas_split(
    customer_id: str,
    daily_kwh: Sequence[float],
    daily_hdd: Sequence[float],
    *,
    hdd_reference_annual: float = GAS_HDD_REFERENCE_ANNUAL,
) -> SeasonalGasSplit | SeasonalGasRefusal:
    """This household's own heating fraction, fitted from its own daily gas series.

    `daily_kwh` is the household's fabric-physics gas trace (W1_12), `daily_hdd` the
    HDD it saw on those same days at its own location. Both are the WORLD's, not the
    company's belief: the company's AQ is applied to the resulting shape by
    `gas_settlement` and is not read here.

    Returns a `SeasonalGasRefusal` -- never a fabricated fraction -- when the window
    cannot identify the two terms.
    """
    if len(daily_kwh) != len(daily_hdd):
        raise ValueError("daily_kwh and daily_hdd must describe the same days")
    if len(daily_kwh) < MIN_DAYS_FOR_FIT:
        return SeasonalGasRefusal(
            customer_id,
            f"a {len(daily_kwh)}-day window cannot identify a two-term seasonal split "
            f"(at least {MIN_DAYS_FOR_FIT} days required)",
        )
    if hdd_reference_annual <= 0.0:
        raise ValueError("the annual HDD reference must be positive")
    spread = max(daily_hdd) - min(daily_hdd)
    if spread < MIN_HDD_SPREAD_FOR_IDENTIFIABILITY:
        return SeasonalGasRefusal(
            customer_id,
            f"the window spans only {spread:.2f} HDD/day, below the "
            f"{MIN_HDD_SPREAD_FOR_IDENTIFIABILITY} needed to tell the heating term from "
            "the flat one -- any fraction would fit equally well",
        )
    total = sum(daily_kwh)
    if total <= 0.0:
        return SeasonalGasRefusal(
            customer_id, "the household consumed no gas over the window"
        )

    slope, intercept, r_squared = _fit_two_term(daily_kwh, daily_hdd)
    if slope <= 0.0:
        return SeasonalGasRefusal(
            customer_id,
            "gas consumption does not rise with cold over this window, so no part of it "
            "can be attributed to space heating",
        )

    annual_heating = slope * hdd_reference_annual
    annual_flat = intercept * 365.0
    annual_total = annual_heating + annual_flat
    if annual_total <= 0.0:
        return SeasonalGasRefusal(
            customer_id, "the fitted annual total is not positive"
        )
    return SeasonalGasSplit(
        customer_id=customer_id,
        heating_fraction=annual_heating / annual_total,
        hdd_reference_annual=hdd_reference_annual,
        n_days=len(daily_kwh),
        hdd_spread=spread,
        fit_r_squared=r_squared,
    )


def seasonal_gas_splits_for_book(
    *,
    customers: Sequence[Mapping],
    daily_gas_series_for: Callable[[Mapping], tuple[Sequence[float], Sequence[float]] | None],
    hdd_reference_annual: float = GAS_HDD_REFERENCE_ANNUAL,
) -> tuple[dict[str, SeasonalGasSplit], list[SeasonalGasRefusal]]:
    """Decide, ONCE for the whole book, which gas customers settle on their own seasonal
    shape — the same shape `fabric_demand_path.fabric_providers_for_book` uses on the
    electricity side, and for the same reason: a measurement of a different population
    from the one that settles is not a measurement of the switch.

    `daily_gas_series_for(customer)` returns `(daily_kwh, daily_hdd)` for that household's
    own fabric trace, or None if no trace can be built for it. It takes the CUSTOMER RECORD
    and not the id, because resolving a premise to a weather site reads its `location` --
    the same signature `fabric_providers_for_book`'s accessors take, and for the same
    reason. The accessor is injected so this function is testable without the
    fabric/weather stack, and so the caller decides how expensive a window to generate.

    Returns `(splits_by_customer_id, refusals)`. Every customer appears in exactly one of
    them, so a household keeping the population constant is visible in the run's own
    record rather than inferred from an absence.
    """
    splits: dict[str, SeasonalGasSplit] = {}
    refusals: list[SeasonalGasRefusal] = []
    for customer in customers:
        cid = str(customer.get("customer_id", ""))
        if not cid:
            raise ValueError("a customer record without a customer_id cannot be classified")
        series = daily_gas_series_for(customer)
        if series is None:
            refusals.append(
                SeasonalGasRefusal(cid, "no fabric trace: keeping the population constant")
            )
            continue
        daily_kwh, daily_hdd = series
        outcome = seasonal_gas_split(
            cid, daily_kwh, daily_hdd, hdd_reference_annual=hdd_reference_annual
        )
        if isinstance(outcome, SeasonalGasRefusal):
            refusals.append(outcome)
        else:
            splits[cid] = outcome
    return splits, refusals


# ---------------------------------------------------------------------------
# The controls. Each names the defect it fires on.
# ---------------------------------------------------------------------------


def level_is_preserved(
    split: SeasonalGasSplit, aq_kwh: float, daily_hdd: Sequence[float], *, tol: float = 1e-6
) -> bool:
    """The claim that makes this switch safe: applying a per-household heating fraction
    moves WHEN the year's gas is consumed and never HOW MUCH of it there is.

    Settles a reference year through `gas_settlement.resi_daily_gas_kwh` -- the SAME
    function settlement calls, never a restatement of it -- at this household's fraction
    and at the population constant, and requires the two annual totals to agree. Fires if
    the per-household fraction changes the annual volume, which is the AQ mismatch
    `run_phase2b` refused the switch to avoid.

    `daily_hdd` must be a year whose HDD sums to the reference; otherwise both totals move
    together and the control cannot see a level change (that is the point of the check
    below, not an inconvenience).
    """
    if abs(sum(daily_hdd) - split.hdd_reference_annual) > 1.0:
        raise ValueError(
            "level preservation is only defined against a reference-HDD year; this window "
            f"sums to {sum(daily_hdd):.1f} against a reference of "
            f"{split.hdd_reference_annual:.1f}"
        )
    at_household = sum(
        resi_daily_gas_kwh(aq_kwh, hdd, heating_fraction=split.heating_fraction)
        for hdd in daily_hdd
    )
    at_population = sum(resi_daily_gas_kwh(aq_kwh, hdd) for hdd in daily_hdd)
    return abs(at_household - at_population) <= tol * max(1.0, abs(at_population))


def population_spread_is_material(
    splits: Sequence[SeasonalGasSplit], *, min_p90_p10_gap: float = 0.05
) -> bool:
    """R15-failable: True iff the book's fitted heating fractions actually differ.

    FIRES on the shipped defect this atom exists to remove -- every household handed the
    same 0.70 -- and on the mutation that hands every household the population mean under
    a new name. A p90-p10 gap of 0.05 is five percentage points of a household's annual
    gas moving between the seasonal term and the flat one; below that the "per-household"
    shape is a relabelling of one profile.

    Raises on fewer than five households: a spread claim over four homes is arithmetic,
    not a measurement (FAIL-OPEN guard).
    """
    if len(splits) < 5:
        raise ValueError("a spread claim needs at least five households")
    fractions = sorted(s.heating_fraction for s in splits)
    p10 = fractions[int(0.10 * len(fractions))]
    p90 = fractions[min(len(fractions) - 1, int(0.90 * len(fractions)))]
    return (p90 - p10) >= min_p90_p10_gap


def every_split_declares_it_is_not_validated(splits: Sequence[SeasonalGasSplit]) -> bool:
    """R15-failable: True iff no split anywhere claims validation. Fires the moment a
    code path invents a validated shape -- which would cross a director decision rather
    than raise a level. Raises on an empty set: a vacuous pass over nothing is exactly the
    reading this control must not be able to give."""
    if not splits:
        raise ValueError("cannot judge the validation claim of an empty set of splits")
    return all(
        (not s.validated) and s.not_validated_statement() == NOT_VALIDATED_STATEMENT
        for s in splits
    )
