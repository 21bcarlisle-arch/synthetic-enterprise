"""C14 — company-side thermal parameter inference.

**Purpose.** Give the supplier a per-premise belief about the physical fabric it
is selling energy into — a heat loss coefficient (HLC, kW/K) and a thermal
response time — built ONLY from what a real UK supplier can actually obtain:
its own meter reads, published weather, and the EPC register.

**Guarantee.** Every belief this module returns carries its evidence basis and
an uncertainty band, and no belief is ever derived from simulation internals.
A premise whose evidence cannot support an estimate raises rather than returning
a confident-looking number (R15 fail-open: an unusable fit is a FAILED fit, not
a quiet default).

**Why it exists.** This is the COMPANY leg of the coupled triad with
`W1_12_premise_trace_generator`. The SIM knows each premise's actual
`(R_ia, R_im, C_i, C_m)`. The company knows none of it. What it has instead is
an *estimate of an estimate*: an EPC is itself a modelled assessment (usually a
reduced-data assessment with assumed values for anything not visible on a
walk-round), and the supplier then reads that model. Three distinct error
sources, each faced by a real supplier:

1. **EPC modelling error** — the certificate's fabric is modelled, not measured.
2. **EPC staleness** — a certificate lodged before a retrofit describes a house
   that no longer exists. The company sees only the lodgement date.
3. **EPC absence** — roughly 40% of the stock has no certificate at all, and the
   covered 60% is transaction-biased (recently sold or let).

The module copes with all three by WIDENING UNCERTAINTY, never by correcting
toward the truth: a bias correction would require knowing the answer, which is
precisely what the wall withholds. Being wrong in a measurable direction is the
point — `H_GAP_fabric_belief_truth_gap` prices the consequence.

**Wall discipline (a gate on this atom, not a nicety).** This module imports
nothing from `simulation.*` or `sim.*`, and does not read SIM state through any
other path. `sim_imports_in()` below is a standing, failable control on that,
exercised both ways in the test suite.

**Estimator choice (SIMPLICITY GUARD).** The FRAME left the estimator open and
said: if regularised least squares on the heating-response gradient will do,
do that first and escalate to a UKF only if the measured gap demands it. It
does do, so this is weighted OLS with a searched balance-point temperature,
shrunk toward the EPC prior by inverse-variance weighting in log space. No
filter, no state-space machinery, no learning problem.
"""

from __future__ import annotations

import datetime as dt
import math
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Sequence

import numpy as np

# ---------------------------------------------------------------------------
# Company-side assumptions. Every constant here is `domain-knowledge` and a
# CANDIDATE TO VERIFY, not a settled value — and, more importantly, every one of
# them is a company BELIEF. The SIM's corresponding constants are different by
# construction; that divergence is a modelled error source, not a bug to align.
# ---------------------------------------------------------------------------

BALANCE_POINT_GRID_C: tuple[float, ...] = tuple(
    round(10.0 + 0.5 * i, 1) for i in range(17)
)
"""Candidate balance-point temperatures (10.0–18.0 C). The company cannot see a
setpoint, so it searches for the temperature at which demand starts responding.
The UK gas convention (15.5 C) sits inside the grid but is not assumed."""

MIN_READ_INTERVALS = 6
"""Fewer than six usable intervals cannot support a two-parameter fit with any
honesty. Raises rather than fitting."""

MIN_HDD_SPAN_K = 3.0
"""The heating-degree-day range across intervals must actually span something;
a read history at one temperature cannot see a gradient at all."""

MIN_PEAK_HDD_K = 5.0
"""The history must also CONTAIN genuinely cold weather, not merely vary.

MEASURED (2026-08-03): a summer-only read history passed the span test on its
own, because the searched balance point drifts up to 18 C and a UK July still
produces a few degree days of spread. The fit then extrapolates winter fabric
loss from July hot water and holidays. A supplier that has never observed the
premise in the cold does not know its heat loss — the span alone was a
fail-open."""

MIN_FIT_R2 = 0.50
"""Below this the demand simply is not degree-day-responsive (electric-heated
premise dominated by baseload, unoccupied property, faulty meter). The fit is
then declared unusable — the company falls back to the EPC prior and SAYS SO."""

ASSUMED_BOILER_EFFICIENCY = 0.85
"""The supplier does not know the boiler's age or condition. A single
mid-estate seasonal efficiency is what it can actually assume."""

ASSUMED_HEAT_PUMP_SCOP = 2.8
"""A flat seasonal COP. The real machine's COP falls with ambient temperature,
so this assumption biases the inferred HLC in cold weather — deliberately
retained, because a real supplier working from an annual SCOP has exactly this
error."""

ASSUMED_DISTRICT_HEAT_EFFICIENCY = 1.0
ASSUMED_RESISTIVE_EFFICIENCY = 1.0

EPC_MODELLING_RELATIVE_SD = 0.30
"""Spread of EPC-modelled fabric performance against measured (coheating-class)
performance. `domain-knowledge` — the "performance gap" literature puts it in
the tens of percent; a candidate to verify against a published study."""

EPC_STALENESS_SD_PER_YEAR = 0.02
"""Extra relative uncertainty per year since lodgement — the chance that the
fabric has been changed since the certificate was written."""

EPC_MAX_RELATIVE_SD = 0.55
"""Cap: past a certain age the certificate is not evidence at all, and pretending
its uncertainty keeps growing linearly would be false precision."""

STOCK_PRIOR_RELATIVE_SD = 0.60
"""A premise with no certificate at all: the company knows only its property
type, so its prior is the stock-class mean with very wide uncertainty."""

METHOD_RELATIVE_SD_FLOOR = 0.15
"""Structural (not statistical) error in the gradient method itself: setback
periods, internal and solar gains, away days and deadband cycling all mean the
observed gradient is not exactly the HLC even with perfect meter data. An OLS
standard error alone would understate the company's real uncertainty."""

CADENCE_SD_PER_INTERVAL_DOUBLING = 0.05
"""Extra structural uncertainty for every DOUBLING of the mean read interval.

MEASURED, not assumed (2026-08-03, against `W1_12` traces): the same premise
inferred from daily / weekly / monthly reads came out 0.2% / 8% / 18% from the
truth, while the OLS standard error barely moved (0.136 -> 0.148). The
regression through interval means is not the regression through daily values
when the underlying daily response is kinked at the balance point, and the
kink is smeared further the longer the interval. Without this term the company
reports the same confidence for a quarterly-read premise as for a smart-metered
one — a fail-open in the uncertainty model, and the reason a coarse-read premise
must fall out of `is_actionable`."""

MAX_ACTIONABLE_RELATIVE_SD = 0.35
"""The widest belief the company will spend money on (`is_actionable_belief`).

Named rather than inlined (2026-08-09) because it is a DIAL a downstream decision
depends on, and an unnamed threshold is one nobody can find, compare or mutate —
this project's own orphan-constant class. It sits below `STOCK_PRIOR_RELATIVE_SD`
(0.60) by construction: a stock prior must fail this test on its width alone even
if the basis check were removed, so the two halves of the refusal are independent
rather than one masking the other."""

FLAT_SCOP_EXTRA_RELATIVE_SD = 0.40
"""Extra uncertainty on any heat-pump premise, because `ASSUMED_HEAT_PUMP_SCOP`
is a FLAT seasonal figure applied to a machine whose COP falls with ambient
temperature. Cold-day electricity therefore rises faster than linearly in
degree days, and a linear gradient reads that as fabric loss.

MEASURED: an ASHP premise came out 55% above its true HLC on daily reads, ten
times the error of the equivalent gas premise. The company does not know the
machine's COP curve, so it cannot correct the bias — but it does know that it is
assuming one away, and saying so is what the widened band is for."""

# --- The company's own coarse fabric model -------------------------------
# DELIBERATELY COARSER than the SIM's: one whole-envelope U-value per age band
# rather than separate wall/roof/window/ground paths. This is what a supplier
# can build from register fields, and the divergence from the SIM's finer model
# is one of the three error sources this atom exists to represent.

_ENVELOPE_U_BY_ERA: dict[str, float] = {
    "pre-1919": 1.55,
    "1919-1944": 1.45,
    "1945-1964": 1.30,
    "1965-1980": 1.05,
    "1981-2000": 0.70,
    "post-2000": 0.40,
}

_INSULATION_FACTOR: dict[str, float] = {
    "full": 0.62,
    "partial": 0.83,
    "poor": 1.00,
    "unknown": 0.90,
}

_ENVELOPE_AREA_RATIO: dict[str, float] = {
    # External envelope area per m^2 of floor area, including the exposure
    # penalty of a detached form and the shelter of a flat.
    "detached": 2.30,
    "semi-detached": 1.75,
    "terraced": 1.35,
    "flat": 0.80,
}

_STOCK_HLC_KW_PER_K: dict[str, float] = {
    # No-certificate fallback: the class mean the company would use.
    "detached": 0.32,
    "semi-detached": 0.24,
    "terraced": 0.20,
    "flat": 0.14,
}

_STOCK_FLOOR_AREA_M2: dict[str, float] = {
    "detached": 130.0,
    "semi-detached": 92.0,
    "terraced": 79.0,
    "flat": 61.0,
}

_STOREY_HEIGHT_M = 2.4
_VENTILATION_ACH_BY_ERA: dict[str, float] = {
    "pre-1919": 0.95,
    "1919-1944": 0.85,
    "1945-1964": 0.75,
    "1965-1980": 0.65,
    "1981-2000": 0.55,
    "post-2000": 0.50,
}

_SIM_IMPORT_RE = re.compile(
    r"^\s*(?:from\s+(simulation|sim)(?:\.[A-Za-z0-9_.]+)?\s+import\b"
    r"|import\s+(simulation|sim)(?:\.[A-Za-z0-9_.]+)?\b)",
    re.MULTILINE,
)


class WallViolationError(RuntimeError):
    """Raised when company-layer code is found reaching into SIM internals."""


class InsufficientObservationError(ValueError):
    """Not enough observable evidence to support any belief at all."""


class UnusableMeterHistoryError(ValueError):
    """The meter history itself is malformed — non-monotonic register, duplicate
    or non-finite reads. Distinct from 'not enough of it'."""


class EvidenceBasis(str, Enum):
    """What a belief actually rests on. Carried on every belief so a downstream
    decision can refuse to act on a stock prior."""

    METER_AND_EPC = "meter_and_epc"
    METER_ONLY = "meter_only"
    EPC_ONLY = "epc_only"
    STOCK_PRIOR = "stock_prior"


# ---------------------------------------------------------------------------
# Observables — the ONLY inputs. Every field here is something a real UK
# supplier can obtain: its own billing register, a published weather series, and
# the open EPC register.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MeterRead:
    """One register read. Cumulative, because that is what a meter reports —
    the company derives consumption by differencing, exactly as it must."""

    read_date: dt.date
    cumulative_kwh: float


@dataclass(frozen=True)
class PublishedWeatherDay:
    """A day of the PUBLISHED weather series — a regional station or gridded
    product, not the premise's true local field. The company never sees the
    latter, and the difference is a genuine error source."""

    date: dt.date
    mean_temp_c: float


@dataclass(frozen=True)
class EpcCertificate:
    """The EPC register record as the company reads it — the certificate's own
    vocabulary (plain strings), never the SIM's enums.

    `modelled_space_heat_kwh_yr` is the certificate's own modelled figure where
    the register carries one; it is used only as a cross-check, never as the
    primary estimate, because it embeds the assessor's standard occupancy
    assumptions rather than this household's behaviour.
    """

    lodged_date: dt.date
    total_floor_area_m2: float
    property_type: str
    build_era_band: str
    insulation: str = "unknown"
    main_heating_fuel: str = "mains gas"
    modelled_space_heat_kwh_yr: float | None = None


@dataclass(frozen=True)
class HeatingResponseFit:
    """The weighted OLS fit of consumption against heating degree days."""

    balance_point_c: float
    gradient_kwh_per_day_k: float
    baseload_kwh_per_day: float
    gradient_relative_se: float
    r2: float
    n_intervals: int
    days_covered: int
    hdd_span_k: float

    @property
    def mean_interval_days(self) -> float:
        return self.days_covered / self.n_intervals

    @property
    def is_usable(self) -> bool:
        return (
            self.r2 >= MIN_FIT_R2
            and self.gradient_kwh_per_day_k > 0.0
            and self.n_intervals >= MIN_READ_INTERVALS
        )


@dataclass(frozen=True)
class HlcPrior:
    """The company's fabric prior before any meter evidence is applied."""

    hlc_kw_per_k: float
    relative_sd: float
    basis: EvidenceBasis
    floor_area_m2: float
    certificate_age_years: float | None


def log_normal_interval_95(value: float, relative_sd: float) -> tuple[float, float]:
    """The 95% interval of a strictly-positive quantity with multiplicative error.

    EXTRACTED FROM `ThermalBelief.interval_95` (2026-08-09) so that a consumer which
    holds a fabric number WITHOUT a full belief object — the harness's counterfactual
    truth arm, the EPC prior taken on its own — computes the same interval from the
    same code. A second implementation of this three-line formula elsewhere would be
    a drift surface that no test could see.
    """
    _require_finite("relative_sd", relative_sd)
    if value <= 0.0 or not math.isfinite(value):
        raise InsufficientObservationError(
            f"a log-normal interval needs a positive finite value, got {value!r}"
        )
    if relative_sd < 0.0:
        raise InsufficientObservationError(
            f"a relative sd cannot be negative, got {relative_sd!r}"
        )
    sigma = math.sqrt(math.log1p(relative_sd**2))
    mu = math.log(value) - 0.5 * sigma**2
    return (math.exp(mu - 1.96 * sigma), math.exp(mu + 1.96 * sigma))


def is_actionable_belief(basis: EvidenceBasis, relative_sd: float) -> bool:
    """Whether a fabric belief is tight enough to spend money on.

    EXTRACTED FROM `ThermalBelief.is_actionable` (2026-08-09) for the same reason as
    `log_normal_interval_95`: the harness must judge actionability by the COMPANY's
    rule, not by a copy of it. `relative_sd` is checked for finiteness FIRST because
    every comparison below is NaN-blind — `nan <= 0.35` is False, so a NaN sd would
    read as "not actionable" for the right answer by accident here and could read the
    other way in any future variant of this predicate.
    """
    _require_finite("relative_sd", relative_sd)
    return basis != EvidenceBasis.STOCK_PRIOR and relative_sd <= MAX_ACTIONABLE_RELATIVE_SD


@dataclass(frozen=True)
class ThermalBelief:
    """What the company believes about one premise's fabric, and how sure it is.

    `hlc_kw_per_k` is the posterior. `relative_sd` is its one-sigma relative
    uncertainty. `basis` says what it rests on — a caller that would spend money
    on this belief should check `is_actionable` rather than the point estimate.
    """

    premise_id: str
    hlc_kw_per_k: float
    relative_sd: float
    basis: EvidenceBasis
    prior: HlcPrior
    meter_hlc_kw_per_k: float | None
    meter_relative_sd: float | None
    fit: HeatingResponseFit | None
    response_time_constant_hours: float | None
    notes: tuple[str, ...] = field(default_factory=tuple)

    @property
    def hlc_per_m2_w_per_k(self) -> float:
        """Fabric performance normalised for size — the form in which premises
        are actually compared for a retrofit decision."""
        return 1000.0 * self.hlc_kw_per_k / self.prior.floor_area_m2

    @property
    def interval_95(self) -> tuple[float, float]:
        """Log-normal 95% interval: HLC is strictly positive and its errors are
        multiplicative, so a symmetric band would put mass below zero."""
        return log_normal_interval_95(self.hlc_kw_per_k, self.relative_sd)

    @property
    def is_actionable(self) -> bool:
        """Whether this belief is tight enough to base a fabric intervention on.
        A stock prior never is: it contains no information about THIS premise."""
        return is_actionable_belief(self.basis, self.relative_sd)


# ---------------------------------------------------------------------------
# The wall control — a pure function over source text, so the test can mutate
# the text rather than the repo (R15 both ways, no disk mutation needed).
# ---------------------------------------------------------------------------


def sim_imports_in(source: str) -> list[str]:
    """Return every `simulation`/`sim` import found in `source`.

    THE standing control on this atom's wall condition. Independent of the thing
    it checks in the sense that matters: it reads the source text, not the
    module's own beliefs about itself, so it still fires if someone adds an
    import and forgets to update anything else.
    """
    return [m.group(0).strip() for m in _SIM_IMPORT_RE.finditer(source)]


def assert_wall_intact(module_path: str | Path | None = None) -> None:
    """Raise if this module (or `module_path`) reaches into the SIM."""
    path = Path(module_path) if module_path is not None else Path(__file__)
    found = sim_imports_in(path.read_text())
    if found:
        raise WallViolationError(
            f"{path} imports SIM internals — the company may not see inside the "
            f"simulation: {found}"
        )


# ---------------------------------------------------------------------------
# Meter reads -> consumption intervals
# ---------------------------------------------------------------------------


def _require_finite(name: str, value: float) -> float:
    """Reject non-finite values FIRST. Every comparison below is NaN-blind:
    `nan > x` is False, so a NaN sliding into a threshold test passes it."""
    v = float(value)
    if not math.isfinite(v):
        raise UnusableMeterHistoryError(f"{name} is not finite: {value!r}")
    return v


@dataclass(frozen=True)
class ConsumptionInterval:
    start: dt.date
    end: dt.date
    kwh: float

    @property
    def days(self) -> int:
        return (self.end - self.start).days

    @property
    def kwh_per_day(self) -> float:
        return self.kwh / self.days


def consumption_intervals(reads: Sequence[MeterRead]) -> list[ConsumptionInterval]:
    """Difference cumulative reads into per-interval consumption.

    Rejects — rather than silently repairing — the register faults a real
    supplier meets: a read that goes backwards (meter exchange or misread), two
    reads on the same day, a non-finite value. Silently clamping these to zero
    is the fail-open that would let a broken history produce a confident belief.
    """
    if len(reads) < 2:
        raise InsufficientObservationError(
            f"need at least 2 reads to derive consumption, got {len(reads)}"
        )
    ordered = sorted(reads, key=lambda r: r.read_date)
    out: list[ConsumptionInterval] = []
    for previous, current in zip(ordered, ordered[1:]):
        _require_finite("cumulative_kwh", previous.cumulative_kwh)
        _require_finite("cumulative_kwh", current.cumulative_kwh)
        if current.read_date == previous.read_date:
            raise UnusableMeterHistoryError(
                f"two reads on {current.read_date} — cannot form an interval"
            )
        if current.cumulative_kwh < previous.cumulative_kwh:
            raise UnusableMeterHistoryError(
                f"register goes backwards between {previous.read_date} and "
                f"{current.read_date}: {previous.cumulative_kwh} -> "
                f"{current.cumulative_kwh} (meter exchange or misread)"
            )
        out.append(
            ConsumptionInterval(
                start=previous.read_date,
                end=current.read_date,
                kwh=current.cumulative_kwh - previous.cumulative_kwh,
            )
        )
    return out


def heating_degree_days(
    weather: Sequence[PublishedWeatherDay], balance_point_c: float
) -> dict[dt.date, float]:
    """Degrees below the balance point, floored at zero, per published day."""
    if not weather:
        raise InsufficientObservationError("no published weather supplied")
    out: dict[dt.date, float] = {}
    for day in weather:
        temp = _require_finite("mean_temp_c", day.mean_temp_c)
        out[day.date] = max(0.0, balance_point_c - temp)
    return out


def _interval_mean_hdd(
    interval: ConsumptionInterval, hdd_by_day: dict[dt.date, float]
) -> float | None:
    """Mean HDD over the days a read interval covers, `(start, end]`.

    Returns None if ANY day is missing from the published series — a partially
    covered interval would understate degree days and drag the gradient down,
    so it is dropped rather than approximated.
    """
    total = 0.0
    day = interval.start + dt.timedelta(days=1)
    while day <= interval.end:
        value = hdd_by_day.get(day)
        if value is None:
            return None
        total += value
        day += dt.timedelta(days=1)
    return total / interval.days


# ---------------------------------------------------------------------------
# The estimator
# ---------------------------------------------------------------------------


def _weighted_ols(
    x: np.ndarray, y: np.ndarray, w: np.ndarray
) -> tuple[float, float, float, float]:
    """Weighted OLS of y on x. Returns (intercept, slope, slope_se, r2)."""
    sw = w.sum()
    mx = float((w * x).sum() / sw)
    my = float((w * y).sum() / sw)
    sxx = float((w * (x - mx) ** 2).sum())
    if sxx <= 0.0:
        raise InsufficientObservationError(
            "the degree-day regressor has no variance — cannot fit a gradient"
        )
    sxy = float((w * (x - mx) * (y - my)).sum())
    slope = sxy / sxx
    intercept = my - slope * mx
    residual = y - (intercept + slope * x)
    dof = len(x) - 2
    if dof <= 0:
        raise InsufficientObservationError("not enough intervals to estimate error")
    sigma2 = float((w * residual**2).sum() / (sw * dof / len(x)))
    slope_se = math.sqrt(max(sigma2, 0.0) / sxx * (sw / len(x)))
    syy = float((w * (y - my) ** 2).sum())
    r2 = 0.0 if syy <= 0.0 else max(0.0, 1.0 - float((w * residual**2).sum()) / syy)
    return intercept, slope, slope_se, r2


def fit_heating_response(
    reads: Sequence[MeterRead],
    weather: Sequence[PublishedWeatherDay],
    *,
    balance_point_grid: Sequence[float] = BALANCE_POINT_GRID_C,
) -> HeatingResponseFit:
    """Fit mean daily consumption against mean heating degree days.

    The balance point is SEARCHED, not assumed: the company cannot see the
    thermostat setpoint, and the temperature at which a house starts drawing
    heat is a function of its gains and its fabric as well as its setpoint.
    Intervals are weighted by their length, so a quarterly read does not carry
    the same weight as a daily one.
    """
    intervals = consumption_intervals(reads)
    if len(intervals) < MIN_READ_INTERVALS:
        raise InsufficientObservationError(
            f"need at least {MIN_READ_INTERVALS} read intervals, got {len(intervals)}"
        )

    best: HeatingResponseFit | None = None
    for balance_point in balance_point_grid:
        hdd_by_day = heating_degree_days(weather, balance_point)
        xs: list[float] = []
        ys: list[float] = []
        ws: list[float] = []
        for interval in intervals:
            mean_hdd = _interval_mean_hdd(interval, hdd_by_day)
            if mean_hdd is None:
                continue
            xs.append(mean_hdd)
            ys.append(interval.kwh_per_day)
            ws.append(float(interval.days))
        if len(xs) < MIN_READ_INTERVALS:
            continue
        span = max(xs) - min(xs)
        if span < MIN_HDD_SPAN_K or max(xs) < MIN_PEAK_HDD_K:
            continue
        try:
            intercept, slope, slope_se, r2 = _weighted_ols(
                np.array(xs), np.array(ys), np.array(ws)
            )
        except InsufficientObservationError:
            continue
        candidate = HeatingResponseFit(
            balance_point_c=balance_point,
            gradient_kwh_per_day_k=slope,
            baseload_kwh_per_day=intercept,
            gradient_relative_se=(
                abs(slope_se / slope) if slope > 0 else float("inf")
            ),
            r2=r2,
            n_intervals=len(xs),
            days_covered=int(sum(ws)),
            hdd_span_k=span,
        )
        if best is None or candidate.r2 > best.r2:
            best = candidate

    if best is None:
        raise InsufficientObservationError(
            "no balance point produced a fittable series — the read history is "
            "too short, too sparse against the weather series, or spans too "
            "little of the heating season"
        )
    return best


def assumed_conversion_efficiency(main_heating_fuel: str) -> float:
    """The company's assumed fuel-to-heat conversion factor.

    It does NOT know the boiler's age or the heat pump's real COP curve, so a
    single seasonal figure is what it can assume — and that assumption is a
    modelled error source, not an approximation to be tightened by peeking.
    """
    fuel = main_heating_fuel.strip().lower()
    if "heat pump" in fuel or "ashp" in fuel or "gshp" in fuel:
        return ASSUMED_HEAT_PUMP_SCOP
    if "gas" in fuel or "oil" in fuel or "lpg" in fuel:
        return ASSUMED_BOILER_EFFICIENCY
    if "district" in fuel or "community" in fuel:
        return ASSUMED_DISTRICT_HEAT_EFFICIENCY
    return ASSUMED_RESISTIVE_EFFICIENCY


def hlc_from_gradient(gradient_kwh_per_day_k: float, efficiency: float) -> float:
    """Convert a fuel-side degree-day gradient into a heat-side HLC in kW/K.

    gradient [fuel kWh/day/K] x efficiency [heat kWh per fuel kWh] / 24 h.
    """
    if gradient_kwh_per_day_k <= 0.0:
        raise ValueError("a non-positive heating gradient cannot yield an HLC")
    return gradient_kwh_per_day_k * efficiency / 24.0


def _rejection_reason(fit: HeatingResponseFit) -> str:
    """Name the condition that ACTUALLY failed.

    A diagnostic that always blames the same condition is a lie the next
    debugger has to unpick: a flat consumption history was being reported as
    "r2 below floor" when what really rejected it was a non-positive gradient.
    """
    if fit.gradient_kwh_per_day_k <= 0.0:
        return (
            f"gradient {fit.gradient_kwh_per_day_k:.3f} kWh/day/K is not "
            f"positive — demand is not degree-day responsive"
        )
    if fit.r2 < MIN_FIT_R2:
        return (
            f"r2={fit.r2:.2f} below {MIN_FIT_R2:.2f} — demand is not "
            f"degree-day responsive"
        )
    return f"only {fit.n_intervals} usable intervals, need {MIN_READ_INTERVALS}"


def method_structural_sd(
    fit: HeatingResponseFit, *, main_heating_fuel: str
) -> float:
    """Structural (non-statistical) uncertainty on a gradient-derived HLC.

    Grows with the read interval and with the weakness of the conversion
    assumption. This is the company reasoning about its OWN method — every term
    is derivable from what it can see (how often it reads the meter, what fuel
    the premise burns), never from the answer.
    """
    doublings = math.log2(max(fit.mean_interval_days, 1.0))
    sd = METHOD_RELATIVE_SD_FLOOR + CADENCE_SD_PER_INTERVAL_DOUBLING * doublings
    fuel = main_heating_fuel.strip().lower()
    if "heat pump" in fuel or "ashp" in fuel or "gshp" in fuel:
        sd = math.sqrt(sd**2 + FLAT_SCOP_EXTRA_RELATIVE_SD**2)
    return sd


def epc_prior(
    certificate: EpcCertificate | None,
    *,
    as_of: dt.date,
    property_type_hint: str | None = None,
) -> HlcPrior:
    """The company's fabric prior from the EPC register.

    Handles all three register error sources explicitly:
    absence -> stock-class prior with `STOCK_PRIOR_RELATIVE_SD`;
    staleness -> prior sd inflated by age since lodgement;
    modelling error -> the `EPC_MODELLING_RELATIVE_SD` floor, which is never
    removed no matter how new the certificate is.
    """
    if certificate is None:
        kind = _normalise_property_type(property_type_hint)
        if kind is None:
            raise InsufficientObservationError(
                "no certificate and no property type — the company has no fabric "
                "prior for this premise at all"
            )
        return HlcPrior(
            hlc_kw_per_k=_STOCK_HLC_KW_PER_K[kind],
            relative_sd=STOCK_PRIOR_RELATIVE_SD,
            basis=EvidenceBasis.STOCK_PRIOR,
            floor_area_m2=_STOCK_FLOOR_AREA_M2[kind],
            certificate_age_years=None,
        )

    kind = _normalise_property_type(certificate.property_type)
    if kind is None:
        raise InsufficientObservationError(
            f"unrecognised EPC property type {certificate.property_type!r}"
        )
    era = certificate.build_era_band.strip().lower()
    if era not in _ENVELOPE_U_BY_ERA:
        raise InsufficientObservationError(
            f"unrecognised EPC age band {certificate.build_era_band!r}"
        )
    area = _require_finite("total_floor_area_m2", certificate.total_floor_area_m2)
    if area <= 0.0:
        raise InsufficientObservationError("EPC floor area must be positive")

    insulation = certificate.insulation.strip().lower()
    u_value = _ENVELOPE_U_BY_ERA[era] * _INSULATION_FACTOR.get(
        insulation, _INSULATION_FACTOR["unknown"]
    )
    envelope_area = _ENVELOPE_AREA_RATIO[kind] * area
    fabric_w_per_k = u_value * envelope_area
    ventilation_w_per_k = (
        0.33 * _VENTILATION_ACH_BY_ERA[era] * area * _STOREY_HEIGHT_M
    )
    hlc = (fabric_w_per_k + ventilation_w_per_k) / 1000.0

    age_years = max(0.0, (as_of - certificate.lodged_date).days / 365.25)
    relative_sd = min(
        EPC_MAX_RELATIVE_SD,
        math.sqrt(
            EPC_MODELLING_RELATIVE_SD**2 + (EPC_STALENESS_SD_PER_YEAR * age_years) ** 2
        ),
    )
    return HlcPrior(
        hlc_kw_per_k=hlc,
        relative_sd=relative_sd,
        basis=EvidenceBasis.EPC_ONLY,
        floor_area_m2=area,
        certificate_age_years=age_years,
    )


def _normalise_property_type(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip().lower().replace("_", "-")
    if text in _STOCK_HLC_KW_PER_K:
        return text
    if "maisonette" in text or "apartment" in text or "flat" in text:
        return "flat"
    if "end-terrace" in text or "mid-terrace" in text or "terrac" in text:
        return "terraced"
    if "semi" in text:
        return "semi-detached"
    if "detach" in text:
        return "detached"
    if "bungalow" in text:
        return "detached"
    return None


def estimate_response_time_constant(
    reads: Sequence[MeterRead],
    weather: Sequence[PublishedWeatherDay],
    *,
    balance_point_c: float,
) -> float | None:
    """Estimate how long the premise's demand REMEMBERS yesterday's weather.

    Honest naming matters here: this is a DEMAND-response time constant, not the
    building's thermal time constant. The company cannot see indoor temperature,
    so it cannot observe a free-running decay; what it can see is that a cold day
    still costs money the following day. Regressing daily consumption on today's
    and yesterday's degree days gives a memory fraction, and a first-order read
    of that fraction gives a time constant in hours.

    Returns None — never a fabricated number — when the read history is not
    daily (the dominant real case: quarterly or monthly billing reads simply
    cannot see this) or the lag term comes out non-positive.
    """
    intervals = [i for i in consumption_intervals(reads) if i.days == 1]
    if len(intervals) < 2 * MIN_READ_INTERVALS:
        return None
    hdd_by_day = heating_degree_days(weather, balance_point_c)

    rows: list[tuple[float, float, float]] = []
    for interval in intervals:
        today = hdd_by_day.get(interval.end)
        yesterday = hdd_by_day.get(interval.end - dt.timedelta(days=1))
        if today is None or yesterday is None:
            continue
        rows.append((today, yesterday, interval.kwh_per_day))
    if len(rows) < 2 * MIN_READ_INTERVALS:
        return None

    design = np.array([[1.0, today, yesterday] for today, yesterday, _ in rows])
    target = np.array([kwh for _, _, kwh in rows])
    try:
        coeffs, *_ = np.linalg.lstsq(design, target, rcond=None)
    except np.linalg.LinAlgError:
        return None
    b_today, b_lag = float(coeffs[1]), float(coeffs[2])
    if b_today <= 0.0 or b_lag <= 0.0:
        return None
    memory = b_lag / (b_today + b_lag)
    if not 0.0 < memory < 1.0:
        return None
    return -24.0 / math.log(memory)


def infer_thermal_parameters(
    *,
    premise_id: str,
    reads: Sequence[MeterRead],
    weather: Sequence[PublishedWeatherDay],
    certificate: EpcCertificate | None,
    as_of: dt.date,
    property_type_hint: str | None = None,
    main_heating_fuel: str | None = None,
) -> ThermalBelief:
    """Infer one premise's fabric belief from observables ONLY.

    The shrinkage is inverse-variance in LOG space: HLC is strictly positive and
    both error sources are multiplicative, so combining them arithmetically
    would bias the posterior upward and could produce a negative lower bound.
    """
    notes: list[str] = []
    prior = epc_prior(
        certificate, as_of=as_of, property_type_hint=property_type_hint
    )
    fuel = main_heating_fuel or (
        certificate.main_heating_fuel if certificate else "mains gas"
    )
    efficiency = assumed_conversion_efficiency(fuel)

    fit: HeatingResponseFit | None = None
    meter_hlc: float | None = None
    meter_sd: float | None = None
    try:
        fit = fit_heating_response(reads, weather)
    except (InsufficientObservationError, UnusableMeterHistoryError) as exc:
        notes.append(f"no usable meter evidence: {exc}")

    if fit is not None and fit.is_usable:
        meter_hlc = hlc_from_gradient(fit.gradient_kwh_per_day_k, efficiency)
        meter_sd = math.sqrt(
            fit.gradient_relative_se**2
            + method_structural_sd(fit, main_heating_fuel=fuel) ** 2
        )
    elif fit is not None:
        notes.append(f"meter fit rejected: {_rejection_reason(fit)}")

    if meter_hlc is None:
        basis = prior.basis
        posterior = prior.hlc_kw_per_k
        posterior_sd = prior.relative_sd
        response = None
    else:
        basis = (
            EvidenceBasis.METER_AND_EPC
            if prior.basis == EvidenceBasis.EPC_ONLY
            else EvidenceBasis.METER_ONLY
        )
        if prior.basis == EvidenceBasis.STOCK_PRIOR:
            notes.append(
                "no certificate — the estimate rests on meter evidence alone, "
                "regularised only by the stock-class prior"
            )
        posterior, posterior_sd = _log_space_blend(
            (prior.hlc_kw_per_k, prior.relative_sd), (meter_hlc, meter_sd)
        )
        assert fit is not None
        response = estimate_response_time_constant(
            reads, weather, balance_point_c=fit.balance_point_c
        )
        if response is None:
            notes.append(
                "read cadence too coarse to see thermal memory — no response "
                "time constant inferred"
            )

    return ThermalBelief(
        premise_id=premise_id,
        hlc_kw_per_k=posterior,
        relative_sd=posterior_sd,
        basis=basis,
        prior=prior,
        meter_hlc_kw_per_k=meter_hlc,
        meter_relative_sd=meter_sd,
        fit=fit,
        response_time_constant_hours=response,
        notes=tuple(notes),
    )


def _log_space_blend(
    a: tuple[float, float], b: tuple[float, float]
) -> tuple[float, float]:
    """Inverse-variance combination of two (value, relative_sd) estimates."""
    values = []
    precisions = []
    for value, relative_sd in (a, b):
        if value <= 0.0:
            raise ValueError("a non-positive HLC estimate cannot be blended")
        sigma2 = math.log1p(max(relative_sd, 1e-9) ** 2)
        values.append(math.log(value))
        precisions.append(1.0 / sigma2)
    total = precisions[0] + precisions[1]
    mu = (values[0] * precisions[0] + values[1] * precisions[1]) / total
    sigma2 = 1.0 / total
    return math.exp(mu), math.sqrt(math.expm1(sigma2))


# ---------------------------------------------------------------------------
# Standing controls — failable relationships, not pinned values.
# ---------------------------------------------------------------------------


def evidence_narrows_uncertainty(belief: ThermalBelief) -> bool:
    """A belief that used meter evidence must be TIGHTER than the prior it
    started from. If shrinkage ever widened uncertainty, the blend is wrong."""
    if belief.meter_hlc_kw_per_k is None:
        return belief.relative_sd == belief.prior.relative_sd
    return belief.relative_sd < belief.prior.relative_sd


def belief_is_bracketed_by_its_sources(belief: ThermalBelief) -> bool:
    """The posterior must lie between the prior and the meter estimate — a
    shrinkage estimator that lands outside both has a sign or weighting error.
    Deliberately a RELATIONSHIP, not a pinned value: it holds whatever the
    generator produces."""
    if belief.meter_hlc_kw_per_k is None:
        return belief.hlc_kw_per_k == belief.prior.hlc_kw_per_k
    low = min(belief.prior.hlc_kw_per_k, belief.meter_hlc_kw_per_k)
    high = max(belief.prior.hlc_kw_per_k, belief.meter_hlc_kw_per_k)
    return low - 1e-12 <= belief.hlc_kw_per_k <= high + 1e-12


def relative_gap(inferred_hlc_kw_per_k: float, actual_hlc_kw_per_k: float) -> float:
    """|inferred - actual| / actual — the gap metric `H_GAP` will aggregate.

    Defined HERE so the company and the harness cannot drift apart on what the
    number means, but never CALLED here: the company has no access to the actual
    value, and this function exists for the harness to apply from outside.
    """
    if not math.isfinite(actual_hlc_kw_per_k) or actual_hlc_kw_per_k <= 0.0:
        raise ValueError("the actual HLC must be positive and finite")
    if not math.isfinite(inferred_hlc_kw_per_k):
        raise ValueError("a non-finite inferred HLC has no gap")
    return abs(inferred_hlc_kw_per_k - actual_hlc_kw_per_k) / actual_hlc_kw_per_k
