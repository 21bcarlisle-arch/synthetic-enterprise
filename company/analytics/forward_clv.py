"""B11 — forward customer value, fitted on the book's early years and graded on the later ones.

WHAT IS FORECAST, SAID BEFORE IT IS MEASURED. For every billing account on supply at the
end of the cut year, two things over the held-back months that follow:

  * MARGIN — the settlement-record net margin the account earns (`net_gbp` in the run's
    `per_customer_monthly`, summed across the account's fuels by
    `saas.customer_reaction._billing_account_id`). It is the company's own ledger figure
    BEFORE cost-to-serve and bad debt; neither is in the monthly record, so neither is in
    the forecast or in what it is graded against.
  * DEPARTURE — the account's last supplied month falls before the book's last month. A
    departure is any end of supply, and the forecast's survival stays all-cause: margin
    stops however the account leaves. A lever that acts on one cause (a retention offer acts
    on switches, not on moves) needs the split, so where the book carries a move-out
    register the result also counts departures by cause and fits a SWITCH hazard with each
    move censored at its date (slice 4). Where it carries none, ``LIMITATION_DEPARTURE_CAUSE``
    is on the result and the split is None, never a zero. With a register, both rules are also
    graded on each held-back outcome alone: stayers, switchers and movers (slice 5).

GRADING A DEPARTURE p (slice 6). Two questions, kept apart because one score answers both
badly: is the rule's LEVEL right (calibration-in-the-large, mean p minus the realised rate, with
its interval), and does it RANK departers above stayers (an AUC with a DeLong interval, and the
paired per-customer minus flat difference). Within one held-back outcome the realised value is a
constant, so a Brier score there grades only the level -- slice 5 read the level difference as a
win three times. Each outcome is therefore ranked against the held-back stayers instead.

THE FORECAST is ``sum over held-back months of P(still supplied) x monthly margin``.
Realised is the margin the account actually earned in those months (zero after it left).

TWO RULES, ON THE SAME ACCOUNTS AND THE SAME HELD-BACK MONTHS.

  * PER-CUSTOMER — margin is the account's own fitted monthly margin shrunk toward its
    segment's by an empirical-Bayes credibility weight ``n / (n + k)``. ``k`` is NOT
    chosen: it is the ratio of within-account to between-account variance in the fit
    years, so the book itself says how far one account's history can be trusted. When the
    between-account variance is not positive the book says "not at all" and the account
    gets its segment's value — reported, not hidden. Departure hazard is a life table by
    CONTRACT YEAR of tenure (twelve-month buckets because fixed terms are annual), fitted
    on the fit years' months at risk, so two accounts in one segment get different
    survival according to where each is in its tenure.
  * FLAT — one monthly margin and one monthly departure hazard per segment.

A segment is the account's ``segment`` (resi/SME) and the fuels it holds (electricity,
gas, or dual). Nothing else about an account is used.

THE CUT YEAR. ``DEFAULT_CUT_YEAR`` is 2020: the last full year a supplier could have
fitted on before the 2021–22 wholesale crisis. Fitting through 2020 and forecasting
2021 onward is the hardest honest test this book allows — a model of customer value that
cannot be graded across a regime change has not been tested — and it leaves five fit
years and every held-back month through the book's end. The level of both forecasts is
expected to miss through the crisis; what the comparison grades is whether the
per-customer rule places value between accounts better than the flat rule does.

THE DEVIATION WINDOW (B11 slices 2-3). At a cut inside or just after a regime change, an
account's place relative to its segment is taken from the months before the regime moved, and
the level is still fitted through the cut. Where the regime moved is READ, not picked:
``regime_boundary_month`` finds the first month, on or after the cap began, in which wholesale
gas set an all-time high over the whole published record. The window ends the month before.
2021-05 on the record we hold. Slice 2's hand-picked 2020-12 was chosen after its answer was seen.
With no such month by the cut, the window is the fit window, i.e. the rule as first shipped.

THE HAZARD WINDOW (slice 6). ``hazard_fit_from_year`` fits both hazards on the months from that
January to the cut only, left-truncated: an account is at risk from the later of its first month
and the window's start, and its contract year is still counted from its first month. It exists to
test whether the fit window's early years set the level; the default is the whole fit window.

THE LEVEL BY CAUSE (slice 7). With a register, the flat rule's segment hazard is split into a
switch hazard and a move hazard and run as competing risks, so the all-cause level miss is divided
between the causes rather than re-fitted. A retention lever acts on one term only, and slice 6
found the regime moved one term (switching) far more than the other.

TENURE GIVEN CALENDAR TIME (slice 8). On one cohort a contract year IS a calendar year, so the
tenure table can be a recency estimator in disguise (slice 7 found the founders' oldest year fitted
on the cut year alone). Every run so far opens in 2016, but later cohorts open each year after, and
``exit_cells`` with ``standardised_ratios`` ask whether a contract year carries anything once its
calendar year is held. It assumes no cohort effect, which no single book can test.

THE BOUND. Every comparison is paired over the same accounts: the mean of
(per-customer absolute error − flat absolute error) with a normal-approximation 95%
interval on that mean. An interval that straddles zero is reported as "cannot tell",
not as a win for whichever side the point estimate favours.

EPISTEMIC WALL. Reads only the supplier's own per-account ledger and roster from a run's
report JSON. No world state, no socket.
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from statistics import NormalDist
from typing import Mapping, Sequence

from saas.customer_reaction import _billing_account_id

__all__ = [
    "CAP_ERA_START",
    "DEFAULT_CUT_YEAR",
    "HELD_BACK_OUTCOMES",
    "LIMITATION_DEPARTURE_CAUSE",
    "LIMITATION_NO_MOVE_REGISTER",
    "LIMITATION_SWITCH_LEVEL_IS_THE_REGIME",
    "AccountHistory",
    "Backtest",
    "OutcomeGrade",
    "PairedComparison",
    "Ranking",
    "book_from_run_output",
    "load_book",
    "move_outs_from_run_output",
    "regime_boundary_month",
    "run_backtest",
    "backtest_run_output",
    "StandardisedRatio",
    "exit_cells",
    "pooled_ratio",
    "standardised_ratios",
]

DEFAULT_CUT_YEAR = 2020

# The default tariff cap's first window (docs/domain_artefact_library/regulatory/
# ofgem_default_tariff_cap_windows.json). It only skips the all-time highs a young series sets
# in its first years: every month from 2018-10 to 2021-05 reads the same boundary.
CAP_ERA_START = "2019-01"

LIMITATION_DEPARTURE_CAUSE = (
    "departures cannot yet be split into switches and moves: the book records only that "
    "supply ended, so the hazard is all-cause"
)
# Why the book has no register, so the reader does not go looking for a company-side gap: the
# world generates home moves only behind docs/design/curriculum/home_moves_activation.json
# (B7), off until the incoming deemed occupant is supplied.
LIMITATION_NO_MOVE_REGISTER = (
    "the run carries no move-out register (home_move_outs): the world's home moves are off, "
    "so no departure in this book can be told to be a move"
)
# Slice 7 (docs/staging/SEAT_FINDING_B11_THE_MOVE_TERM_TRANSFERS_AND_THE_SWITCH_TERM_IS_THE_REGIME_2026-10-11.md):
# on the slice-5 book the move term's level held at cuts 2020, 2022 and 2023 (every interval holds
# zero) while the switch term over-predicted at all three (+0.24, +0.14, +0.05), shrinking only as
# the collapse entered the fit window. Fitting the switch level to a held-back rate is fitting to
# the answer, so it is published with this instead of a calibrated constant.
LIMITATION_SWITCH_LEVEL_IS_THE_REGIME = (
    "the switch term's level is the fit window's switching regime, not a property of the "
    "customer: it cannot see a regime change after the cut (switching collapsed in the 2021-23 "
    "crisis); the move term is the part of the departure level that held across it"
)

_TWO_SIDED_95 = NormalDist().inv_cdf(0.975)
_MONTHS_PER_CONTRACT_YEAR = 12


def _month_index(ym: str) -> int:
    y, m = ym.split("-")
    return int(y) * 12 + int(m) - 1


def _month_label(idx: int) -> str:
    return f"{idx // 12:04d}-{idx % 12 + 1:02d}"


@dataclass(frozen=True)
class AccountHistory:
    """One billing account's supplied months and the margin each earned."""

    account_id: str
    segment: str
    monthly_net_gbp: Mapping[int, float]  # month index -> net margin that month

    @property
    def first_month(self) -> int:
        return min(self.monthly_net_gbp)

    @property
    def last_month(self) -> int:
        return max(self.monthly_net_gbp)


def book_from_run_output(run_output: Mapping) -> tuple[list[AccountHistory], int]:
    """`(accounts, last month of the book)` from a run's report JSON.

    Fuels of one household are merged into its billing account; a fuel's segment label
    comes from `per_customer_lifetime`. The book's last month is the latest month any
    account was supplied — the edge of what can be observed, so a last month equal to it
    is "still supplied", never "departed".
    """
    lifetime = run_output.get("per_customer_lifetime", {})
    monthly: dict[str, dict[int, float]] = defaultdict(lambda: defaultdict(float))
    fuels: dict[str, set[str]] = defaultdict(set)
    segment_of: dict[str, str] = {}
    for year in run_output["years"].values():
        for cid, months in year.get("per_customer_monthly", {}).items():
            acct = _billing_account_id(cid)
            info = lifetime.get(cid, {})
            fuels[acct].add(info.get("commodity") or "unknown")
            segment_of.setdefault(acct, info.get("segment") or "unknown")
            for ym, rec in months.items():
                monthly[acct][_month_index(ym)] += float(rec["net_gbp"])
    accounts = []
    for acct, months in monthly.items():
        held = fuels[acct]
        fuel = "dual" if {"electricity", "gas"} <= held else "+".join(sorted(held))
        accounts.append(
            AccountHistory(acct, f"{segment_of[acct]} {fuel}", dict(months))
        )
    book_end = max(a.last_month for a in accounts)
    return sorted(accounts, key=lambda a: a.account_id), book_end


def move_outs_from_run_output(run_output: Mapping) -> dict[str, int] | None:
    """Billing account -> the last month it was supplied before moving out, or None when the
    run has no move-out register at all (moves not in this world -- not "nobody moved").

    Reads `household` and `move_date` only: what a supplier learns from a move-out notice
    and its final read. The record's journey state and catchability are the world's and are
    not read. Supply ends at `move_date` exclusive, so a move on the 1st leaves the month
    before as the last one supplied.
    """
    register = run_output.get("home_move_outs")
    if register is None:
        return None
    out: dict[str, int] = {}
    for rec in register:
        last_day = date.fromisoformat(rec["move_date"]) - timedelta(days=1)
        month = last_day.year * 12 + last_day.month - 1
        # Fuels of one household carry one move date; keep the earliest if they ever differ.
        acct = rec["household"]
        out[acct] = min(month, out.get(acct, month))
    return out


@dataclass(frozen=True)
class PairedComparison:
    """Per-customer minus flat, paired over the same accounts. Negative favours per-customer."""

    metric: str
    n: int
    per_customer: float
    flat: float
    mean_difference: float
    interval_95: tuple[float, float] | None
    verdict: str


def _mean_with_interval(xs: Sequence[float]) -> tuple[float, tuple[float, float] | None]:
    """Mean signed error per account with its 95% interval: the aggregate miss, per head."""
    n = len(xs)
    if n < 2:
        return (sum(xs) / n if n else float("nan"), None)
    mean = sum(xs) / n
    half = _TWO_SIDED_95 * math.sqrt(sum((x - mean) ** 2 for x in xs) / (n - 1) / n)
    return mean, (mean - half, mean + half)


@dataclass(frozen=True)
class Ranking:
    """Each rule's AUC, departers against stayers: the chance a departer was given the higher p.

    0.5 is a rule that knows nothing about who leaves; the level of p does not enter. Each AUC
    carries its DeLong 95% interval, and the paired difference (per-customer minus flat, on the
    same accounts, so the covariance counts) carries one too. Positive favours per-customer.
    """

    departers: int
    stayers: int
    per_customer: tuple[float, tuple[float, float] | None]
    flat: tuple[float, tuple[float, float] | None]
    difference: tuple[float, tuple[float, float] | None]
    verdict: str


def _placements(pos: Sequence[float], neg: Sequence[float]) -> tuple[list[float], list[float]]:
    """DeLong's structural components: each departer's share of stayers it outranks, and each
    stayer's share of departers that outrank it. A tie counts a half."""
    def psi(x: float, y: float) -> float:
        return 1.0 if x > y else 0.5 if x == y else 0.0

    v10 = [sum(psi(x, y) for y in neg) / len(neg) for x in pos]
    v01 = [sum(psi(x, y) for x in pos) / len(pos) for y in neg]
    return v10, v01


def _cov(a: Sequence[float], b: Sequence[float]) -> float:
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (len(a) - 1)


def _ranking(departers: Sequence["AccountForecast"],
             stayers: Sequence["AccountForecast"]) -> Ranking:
    m, n = len(departers), len(stayers)
    if m < 2 or n < 2:
        nan = (float("nan"), None)
        return Ranking(m, n, nan, nan, nan,
                       f"cannot tell: {m} departer(s) and {n} stayer(s), an interval needs two of each")
    pc10, pc01 = _placements([f.per_customer_departure_p for f in departers],
                             [f.per_customer_departure_p for f in stayers])
    fl10, fl01 = _placements([f.flat_departure_p for f in departers],
                             [f.flat_departure_p for f in stayers])

    def bound(mean: float, var: float) -> tuple[float, tuple[float, float]]:
        half = _TWO_SIDED_95 * math.sqrt(max(var, 0.0))
        return mean, (mean - half, mean + half)

    auc_pc, auc_fl = sum(pc10) / m, sum(fl10) / m
    var_pc = _cov(pc10, pc10) / m + _cov(pc01, pc01) / n
    var_fl = _cov(fl10, fl10) / m + _cov(fl01, fl01) / n
    cov = _cov(pc10, fl10) / m + _cov(pc01, fl01) / n
    diff = bound(auc_pc - auc_fl, var_pc + var_fl - 2 * cov)
    lo, hi = diff[1]
    verdict = ("per-customer ranks better" if lo > 0 else "flat ranks better" if hi < 0
               else "cannot tell: the 95% interval straddles zero")
    return Ranking(m, n, bound(auc_pc, var_pc), bound(auc_fl, var_fl), diff, verdict)


def _paired(metric: str, pc: Sequence[float], fl: Sequence[float]) -> PairedComparison:
    n = len(pc)
    diffs = [a - b for a, b in zip(pc, fl)]
    mean_pc = sum(pc) / n if n else float("nan")
    mean_fl = sum(fl) / n if n else float("nan")
    mean_d = sum(diffs) / n if n else float("nan")
    if n < 2:
        return PairedComparison(
            metric, n, mean_pc, mean_fl, mean_d, None,
            f"cannot tell: {n} account(s) graded, an interval needs two",
        )
    sd = math.sqrt(sum((d - mean_d) ** 2 for d in diffs) / (n - 1))
    half = _TWO_SIDED_95 * sd / math.sqrt(n)
    lo, hi = mean_d - half, mean_d + half
    if hi < 0:
        verdict = "per-customer better"
    elif lo > 0:
        verdict = "flat better"
    else:
        verdict = "cannot tell: the 95% interval straddles zero"
    return PairedComparison(metric, n, mean_pc, mean_fl, mean_d, (lo, hi), verdict)


@dataclass(frozen=True)
class AccountForecast:
    account_id: str
    segment: str
    tenure_months_at_cut: int
    credibility_weight: float
    per_customer_margin_gbp: float
    flat_margin_gbp: float
    realised_margin_gbp: float
    per_customer_departure_p: float
    flat_departure_p: float
    departed: bool


@dataclass(frozen=True)
class OutcomeGrade:
    accounts: int
    margin_error: PairedComparison
    # This outcome's departers ranked against the held-back stayers; None for the stayers.
    ranking_against_stayers: Ranking | None
    # Forecast minus realised, per account, for each rule: which way the miss runs in this outcome.
    margin_bias: Mapping[str, tuple[float, tuple[float, float] | None]]


HELD_BACK_OUTCOMES = ("stayer", "switcher", "mover")


def _grade_outcome(forecasts: Sequence[AccountForecast],
                   stayers: Sequence[AccountForecast] | None) -> OutcomeGrade:
    return OutcomeGrade(
        len(forecasts),
        _paired("absolute margin error, GBP per account",
                [abs(f.per_customer_margin_gbp - f.realised_margin_gbp) for f in forecasts],
                [abs(f.flat_margin_gbp - f.realised_margin_gbp) for f in forecasts]),
        None if stayers is None else _ranking(forecasts, stayers),
        {"per_customer": _mean_with_interval(
            [f.per_customer_margin_gbp - f.realised_margin_gbp for f in forecasts]),
         "flat": _mean_with_interval(
            [f.flat_margin_gbp - f.realised_margin_gbp for f in forecasts])},
    )


@dataclass(frozen=True)
class Backtest:
    cut_year: int
    margin_deviation_fit_months: tuple[str, str]
    fit_months: tuple[str, str]
    held_back_months: tuple[str, str]
    accounts_graded: int
    accounts_excluded: Mapping[str, int]
    shrinkage_k_by_segment: Mapping[str, float | None]
    hazard_by_contract_year: Mapping[int, float]
    hazard_by_segment: Mapping[str, float]
    segment_hazard_ratio: Mapping[str, float]
    forecasts: tuple[AccountForecast, ...]
    margin_error: PairedComparison
    departure_brier: PairedComparison
    margin_bias: Mapping[str, tuple[float, tuple[float, float] | None]]
    aggregate: Mapping[str, float]
    limitations: tuple[str, ...]
    margin_deviation_window_reason: str = ""
    # Slice 4. None when the book has no move-out register; otherwise the fit and held-back
    # windows' departures as {"switch": n, "move": n}, and the switch hazard by contract year
    # with each move censored at its date.
    departures_by_cause: Mapping[str, Mapping[str, int]] | None = None
    switch_hazard_by_contract_year: Mapping[int, float] | None = None
    # Slice 5. None without a register; otherwise each held-back outcome ("stayer", "switcher",
    # "mover") with both rules graded on its own accounts. A rule can win on the book and lose on
    # the movers, and a retention lever only ever acts on the switchers.
    error_by_outcome: Mapping[str, OutcomeGrade] | None = None
    # Slice 6. Mean departure p minus the realised rate, per rule, with its interval: the level.
    departure_calibration: Mapping[str, tuple[float, tuple[float, float] | None]] | None = None
    # Departed against stayed over the whole graded book: the ranking, which the level cannot buy.
    departure_ranking: Ranking | None = None
    # The book's own departure record by calendar year, every account on supply: months at risk,
    # departures, and (with a register) switches and moves. A reading of the ledger, not a forecast.
    departures_by_calendar_year: Mapping[int, Mapping[str, int]] | None = None
    hazard_fit_months: tuple[str, str] | None = None
    # Slice 7. None without a register. The flat rule's segment hazard split into a switch hazard
    # (moves censored) and a move hazard (switches censored), run as competing risks: each cause's
    # mean predicted incidence and the realised share of graded accounts that left by it, and the
    # calibration (incidence minus left-by-this-cause) with its interval. The two incidences sum
    # to the flat departure p, so the all-cause level miss is split between the causes, not re-fit.
    departure_incidence_by_cause: Mapping[str, tuple[float, float]] | None = None
    departure_calibration_by_cause: Mapping[str, tuple[float, tuple[float, float] | None]] | None = None


def regime_boundary_month(
    wholesale_by_month: Mapping[str, float], through: int, anchor: str = CAP_ERA_START
) -> int | None:
    """First month in [`anchor`, `through`] whose wholesale price is above every earlier month of
    the record, or None. Reads nothing after `through`, so a cut never sees its own future."""
    months = sorted((_month_index(ym), p) for ym, p in wholesale_by_month.items())
    start = _month_index(anchor)
    before = [p for m, p in months if m < start]
    if not before:
        raise ValueError(
            f"the wholesale record starts {_month_label(months[0][0]) if months else 'nowhere'}, "
            f"not before {anchor}: an all-time high needs a record before the anchor"
        )
    high = max(before)
    for m, p in months:
        if m < start:
            continue
        if m > through:
            return None
        if p > high:
            return m
    return None


def _fit_margins(
    accounts: Sequence[AccountHistory], fit_end: int
) -> tuple[dict[str, float], dict[str, float | None], dict[str, tuple[float, int]]]:
    """Segment mean monthly margin, EB shrinkage `k` per segment, each account's own (mean, n)."""
    own: dict[str, tuple[float, int]] = {}
    by_seg: dict[str, list[str]] = defaultdict(list)
    within_ss: dict[str, float] = defaultdict(float)
    within_df: dict[str, int] = defaultdict(int)
    seg_total: dict[str, float] = defaultdict(float)
    seg_months: dict[str, int] = defaultdict(int)
    for a in accounts:
        vals = [v for m, v in a.monthly_net_gbp.items() if m <= fit_end]
        if not vals:
            continue
        mean = sum(vals) / len(vals)
        own[a.account_id] = (mean, len(vals))
        by_seg[a.segment].append(a.account_id)
        within_ss[a.segment] += sum((v - mean) ** 2 for v in vals)
        within_df[a.segment] += len(vals) - 1
        seg_total[a.segment] += sum(vals)
        seg_months[a.segment] += len(vals)
    seg_mean = {s: seg_total[s] / seg_months[s] for s in seg_months}
    k_by_seg: dict[str, float | None] = {}
    for s, ids in by_seg.items():
        if len(ids) < 2 or within_df[s] == 0:
            k_by_seg[s] = None  # no between-account spread is estimable: full pooling
            continue
        sigma2 = within_ss[s] / within_df[s]
        means = [own[i][0] for i in ids]
        grand = sum(means) / len(means)
        var_means = sum((m - grand) ** 2 for m in means) / (len(means) - 1)
        tau2 = var_means - sum(sigma2 / own[i][1] for i in ids) / len(ids)
        k_by_seg[s] = sigma2 / tau2 if tau2 > 0 else None
    return seg_mean, k_by_seg, own


def _fit_hazards(
    accounts: Sequence[AccountHistory], fit_end: int, censored: frozenset[str] = frozenset(),
    fit_start: int | None = None,
) -> tuple[dict[int, float], dict[str, float], dict[str, float]]:
    """Monthly departure hazard by contract year, by segment, and each segment's ratio to the
    contract-year table — all on fit months only.

    An account is at risk in each supplied month up to the cut; it departs in its last
    month when that month is before the cut's last month (at the cut a supplier knows it
    has gone). A last month AT the cut is censored, not a departure.

    Trailing contract years with no exit are folded into the year before: a zero drawn
    from a handful of long-tenure accounts is an absence of evidence, not a hazard of nil.
    The segment ratio is observed over expected exits under the contract-year table
    (indirect standardisation), so the per-customer hazard carries the segment's level AND
    the account's tenure, and holds strictly more than the flat rule does.

    An account in `censored` is at risk to its last month but its end is not an exit: that
    is how the switch hazard treats a move.

    `fit_start` left-truncates: months before it are not at risk and an exit before it is not
    counted, while the contract year is still counted from the account's first month.
    """
    at_risk_cy: dict[int, int] = defaultdict(int)
    exits_cy: dict[int, int] = defaultdict(int)
    at_risk_seg: dict[str, int] = defaultdict(int)
    exits_seg: dict[str, int] = defaultdict(int)
    start = fit_start if fit_start is not None else min(a.first_month for a in accounts)
    for a in accounts:
        if a.first_month > fit_end or a.last_month < start:
            continue
        end = min(a.last_month, fit_end)
        for m in range(max(a.first_month, start), end + 1):
            cy = (m - a.first_month) // _MONTHS_PER_CONTRACT_YEAR
            at_risk_cy[cy] += 1
            at_risk_seg[a.segment] += 1
        if a.last_month < fit_end and a.account_id not in censored:
            cy = (a.last_month - a.first_month) // _MONTHS_PER_CONTRACT_YEAR
            exits_cy[cy] += 1
            exits_seg[a.segment] += 1
    if not at_risk_cy:
        raise ValueError(
            f"no account is on supply from {_month_label(start)} to {_month_label(fit_end)}: "
            "a hazard needs months at risk"
        )
    years = sorted(at_risk_cy)
    while len(years) > 1 and exits_cy[years[-1]] == 0:
        last = years.pop()
        at_risk_cy[years[-1]] += at_risk_cy.pop(last)
    by_cy = {cy: exits_cy[cy] / at_risk_cy[cy] for cy in years}
    by_seg = {s: exits_seg[s] / n for s, n in at_risk_seg.items()}
    expected: dict[str, float] = defaultdict(float)
    for a in accounts:
        if a.first_month > fit_end or a.last_month < start:
            continue
        for m in range(max(a.first_month, start), min(a.last_month, fit_end) + 1):
            expected[a.segment] += _hazard_at(by_cy, m - a.first_month)
    ratio = {
        s: (exits_seg[s] / expected[s]) if expected[s] > 0 else 1.0 for s in at_risk_seg
    }
    return by_cy, by_seg, ratio


def _hazard_at(by_cy: Mapping[int, float], tenure_months: int) -> float:
    # Beyond the longest tenure the fit years saw, the oldest contract year's rate holds. A
    # left-truncated window can lack the first years; below its youngest, the youngest holds.
    cy = tenure_months // _MONTHS_PER_CONTRACT_YEAR
    seen = [c for c in by_cy if c <= cy]
    return by_cy[max(seen) if seen else min(by_cy)]


@dataclass(frozen=True)
class StandardisedRatio:
    """Observed exits over the exits expected if only the OTHER axis mattered, for one key."""

    key: int  # a contract year, or a calendar year
    months_at_risk: int
    observed: int
    expected: float
    ratio: float | None
    interval_95: tuple[float, float] | None  # Byar's approximation to the exact Poisson bound


def exit_cells(
    accounts: Sequence[AccountHistory], book_end: int, censored: frozenset[str] = frozenset(),
) -> dict[tuple[int, int], tuple[int, int]]:
    """(calendar year, contract year) -> (months at risk, exits), over every observed month.

    The exit rule is ``_fit_hazards``' with the book's last month as the cut. On one cohort the
    two keys move together, so a contract-year table cannot tell tenure from calendar time;
    where cohorts open in different years the same contract year is seen in several calendar
    years, and ``standardised_ratios`` asks whether it carries anything once the year is held.
    """
    cells: dict[tuple[int, int], list[int]] = defaultdict(lambda: [0, 0])
    for a in accounts:
        for m in range(a.first_month, min(a.last_month, book_end) + 1):
            cells[(m // 12, (m - a.first_month) // _MONTHS_PER_CONTRACT_YEAR)][0] += 1
        if a.last_month < book_end and a.account_id not in censored:
            m = a.last_month
            cells[(m // 12, (m - a.first_month) // _MONTHS_PER_CONTRACT_YEAR)][1] += 1
    return {k: (v[0], v[1]) for k, v in cells.items()}


def _poisson_ratio_interval(observed: int, expected: float) -> tuple[float, float] | None:
    if expected <= 0:
        return None
    z = _TWO_SIDED_95
    lower = 0.0 if observed == 0 else observed * (
        1 - 1 / (9 * observed) - z / (3 * math.sqrt(observed))) ** 3
    o1 = observed + 1
    upper = o1 * (1 - 1 / (9 * o1) + z / (3 * math.sqrt(o1))) ** 3
    return lower / expected, upper / expected


_AXES = {"calendar_year": 0, "contract_year": 1}


def standardised_ratios(
    subject: Mapping[tuple[int, int], tuple[int, int]],
    reference: Mapping[tuple[int, int], tuple[int, int]],
    rate_by: str,
    report_by: str,
) -> list[StandardisedRatio]:
    """Indirect standardisation: ``subject``'s exits over those ``reference``'s exit rate by
    ``rate_by`` (pooled over the other axis) would give, one ratio per key of ``report_by``.

    Tenure given calendar time is ``rate_by="calendar_year", report_by="contract_year"`` with
    one population as both: a contract year away from 1 carries something its calendar years
    do not. Another population as reference with ``report_by="calendar_year"`` asks whether the
    subject leaves as the reference did in the same years.
    """
    for axis in (rate_by, report_by):
        if axis not in _AXES:
            raise ValueError(f"an axis must be one of {sorted(_AXES)}, not {axis!r}")
    by, keep = _AXES[rate_by], _AXES[report_by]
    risk: dict[int, int] = defaultdict(int)
    exits: dict[int, int] = defaultdict(int)
    for k, (n, e) in reference.items():
        risk[k[by]] += n
        exits[k[by]] += e
    rate = {k: exits[k] / n for k, n in risk.items() if n}
    obs: dict[int, int] = defaultdict(int)
    exp: dict[int, float] = defaultdict(float)
    months: dict[int, int] = defaultdict(int)
    for k, (n, e) in subject.items():
        if k[by] not in rate:
            continue  # the reference never saw this key: nothing to expect from, so not graded
        obs[k[keep]] += e
        exp[k[keep]] += n * rate[k[by]]
        months[k[keep]] += n
    out = []
    for key in sorted(months):
        o, x = obs[key], exp[key]
        out.append(StandardisedRatio(key, months[key], o, x, o / x if x > 0 else None,
                                     _poisson_ratio_interval(o, x)))
    return out


def pooled_ratio(ratios: Sequence[StandardisedRatio]) -> StandardisedRatio:
    """All keys together, keyed -1: the subject's one overall ratio to the reference."""
    o = sum(r.observed for r in ratios)
    x = sum(r.expected for r in ratios)
    return StandardisedRatio(-1, sum(r.months_at_risk for r in ratios), o, x,
                             o / x if x > 0 else None, _poisson_ratio_interval(o, x))


def run_backtest(
    accounts: Sequence[AccountHistory],
    book_end: int,
    cut_year: int = DEFAULT_CUT_YEAR,
    margin_fit_end_year: int | None = None,
    wholesale_gas_by_month: Mapping[str, float] | None = None,
    move_out_month_by_account: Mapping[str, int] | None = None,
    hazard_fit_from_year: int | None = None,
) -> Backtest:
    """Fit on months up to December of `cut_year`; forecast and grade every later month.

    `margin_fit_end_year` (B11 slice 2) takes the per-customer DEVIATION -- own mean minus
    segment mean, and the shrinkage `k` -- from the months up to that year only, and adds it
    to the segment level fitted through the cut. The level stays the flat rule's; only which
    accounts sit above or below their segment comes from the earlier window. At the default
    (the cut year) it is `w*own + (1-w)*segment`, the rule as first shipped. An account with
    no month in the earlier window gets its segment's value.

    `wholesale_gas_by_month` (slice 3) READS that window's end instead: the month before
    `regime_boundary_month`. Giving both is refused -- one window, one source.

    `move_out_month_by_account` (slice 4, `move_outs_from_run_output`) splits departures. A
    departure is a move when its last supplied month IS the account's move-out month; an
    account that switched away before a later move date left by switching. The forecast is
    unchanged by it.

    `hazard_fit_from_year` (slice 6) fits both departure hazards on that January to the cut only.
    """
    fit_end = _month_index(f"{cut_year}-12")
    if hazard_fit_from_year is not None and hazard_fit_from_year > cut_year:
        raise ValueError(
            f"hazard window from {hazard_fit_from_year} starts after the cut {cut_year}: it would "
            "fit on held-back months"
        )
    hazard_start = (None if hazard_fit_from_year is None
                    else _month_index(f"{hazard_fit_from_year}-01"))
    if margin_fit_end_year is not None and wholesale_gas_by_month is not None:
        raise ValueError(
            "a deviation window from a chosen year AND from the wholesale record: give one"
        )
    if margin_fit_end_year is not None:
        dev_end = _month_index(f"{margin_fit_end_year}-12")
        dev_reason = f"chosen: deviation through {margin_fit_end_year}-12"
    elif wholesale_gas_by_month is not None:
        boundary = regime_boundary_month(wholesale_gas_by_month, fit_end)
        dev_end = fit_end if boundary is None else boundary - 1
        dev_reason = (
            f"read: no wholesale all-time high from {CAP_ERA_START} to the cut"
            if boundary is None else
            f"read: wholesale gas set an all-time high in {_month_label(boundary)}"
        )
    else:
        dev_end = fit_end
        dev_reason = "the fit window (no deviation window asked for)"
    if dev_end > fit_end:
        raise ValueError(
            f"margin fit year {margin_fit_end_year} is after the cut {cut_year}: the "
            "deviation would read held-back months"
        )
    first = min(a.first_month for a in accounts)
    if fit_end >= book_end:
        raise ValueError(
            f"cut year {cut_year} leaves no held-back months: the book ends "
            f"{_month_label(book_end)}"
        )
    seg_mean, k_by_seg, own = _fit_margins(accounts, fit_end)
    dev_seg_mean, k_by_seg, dev_own = (
        (seg_mean, k_by_seg, own) if dev_end == fit_end else _fit_margins(accounts, dev_end))
    by_cy, by_seg_h, seg_ratio = _fit_hazards(accounts, fit_end, fit_start=hazard_start)
    horizon = book_end - fit_end
    excluded = {"joined after the cut (no fit history)": 0, "left before the cut": 0}
    forecasts: list[AccountForecast] = []
    for a in accounts:
        if a.first_month > fit_end:
            excluded["joined after the cut (no fit history)"] += 1
            continue
        if a.last_month < fit_end:
            excluded["left before the cut"] += 1
            continue
        k = k_by_seg.get(a.segment)
        if a.account_id in dev_own and k is not None:
            own_mean, n = dev_own[a.account_id]
            w = n / (n + k)
            deviation = own_mean - dev_seg_mean[a.segment]
        else:
            w, deviation = 0.0, 0.0
        pc_margin_rate = seg_mean[a.segment] + w * deviation
        fl_margin_rate = seg_mean[a.segment]
        tenure = fit_end - a.first_month + 1
        s_pc = s_fl = 1.0
        pc_total = fl_total = 0.0
        h_fl = by_seg_h.get(a.segment, 0.0)
        for step in range(horizon):
            # Margin is earned in a month the account starts supplied; departure takes
            # effect at the month's end, as the fit counted it.
            pc_total += s_pc * pc_margin_rate
            fl_total += s_fl * fl_margin_rate
            s_pc *= 1 - min(1.0, seg_ratio[a.segment] * _hazard_at(by_cy, tenure + step))
            s_fl *= 1 - h_fl
        realised = sum(v for m, v in a.monthly_net_gbp.items() if m > fit_end)
        forecasts.append(
            AccountForecast(
                a.account_id, a.segment, tenure, w, pc_total, fl_total, realised,
                1 - s_pc, 1 - s_fl, a.last_month < book_end,
            )
        )
    pc_err = [abs(f.per_customer_margin_gbp - f.realised_margin_gbp) for f in forecasts]
    fl_err = [abs(f.flat_margin_gbp - f.realised_margin_gbp) for f in forecasts]
    pc_brier = [(f.per_customer_departure_p - f.departed) ** 2 for f in forecasts]
    fl_brier = [(f.flat_departure_p - f.departed) ** 2 for f in forecasts]
    margin_bias = {
        "per_customer": _mean_with_interval(
            [f.per_customer_margin_gbp - f.realised_margin_gbp for f in forecasts]
        ),
        "flat": _mean_with_interval(
            [f.flat_margin_gbp - f.realised_margin_gbp for f in forecasts]
        ),
    }
    realised_total = sum(f.realised_margin_gbp for f in forecasts)
    aggregate = {
        "realised_margin_gbp": realised_total,
        "per_customer_margin_gbp": sum(f.per_customer_margin_gbp for f in forecasts),
        "flat_margin_gbp": sum(f.flat_margin_gbp for f in forecasts),
        "realised_departures": float(sum(f.departed for f in forecasts)),
        "per_customer_expected_departures": sum(f.per_customer_departure_p for f in forecasts),
        "flat_expected_departures": sum(f.flat_departure_p for f in forecasts),
        # The spread a count of independent departures earns, so a miss can be read
        # against the noise the sample size alone would produce.
        "per_customer_departures_sd": math.sqrt(
            sum(f.per_customer_departure_p * (1 - f.per_customer_departure_p) for f in forecasts)
        ),
        "flat_departures_sd": math.sqrt(
            sum(f.flat_departure_p * (1 - f.flat_departure_p) for f in forecasts)
        ),
    }
    by_cause: dict[str, dict[str, int]] | None = None
    switch_by_cy: dict[int, float] | None = None
    by_outcome: dict[str, OutcomeGrade] | None = None
    moved: frozenset[str] | None = None
    incidence_by_cause: dict[str, tuple[float, float]] | None = None
    calibration_by_cause: dict[str, tuple[float, tuple[float, float] | None]] | None = None
    if move_out_month_by_account is None:
        limitations = [LIMITATION_DEPARTURE_CAUSE, LIMITATION_NO_MOVE_REGISTER]
    else:
        limitations = [LIMITATION_SWITCH_LEVEL_IS_THE_REGIME]
        moved = frozenset(
            a.account_id for a in accounts
            if move_out_month_by_account.get(a.account_id) == a.last_month
        )
        by_cause = {w: {"switch": 0, "move": 0} for w in ("fit", "held_back")}
        for a in accounts:
            if a.last_month >= book_end:
                continue
            window = "fit" if a.last_month < fit_end else "held_back"
            by_cause[window]["move" if a.account_id in moved else "switch"] += 1
        switch_by_cy = _fit_hazards(accounts, fit_end, moved, hazard_start)[0]
        partition: dict[str, list[AccountForecast]] = {o: [] for o in HELD_BACK_OUTCOMES}
        for f in forecasts:
            outcome = ("stayer" if not f.departed
                       else "mover" if f.account_id in moved else "switcher")
            partition[outcome].append(f)
        by_outcome = {o: _grade_outcome(fs, None if o == "stayer" else partition["stayer"])
                      for o, fs in partition.items()}
        left_by = {f.account_id: o for o, fs in partition.items() for f in fs}
        switched = frozenset(a.account_id for a in accounts if a.account_id not in moved)
        h_cause = {"switch": _fit_hazards(accounts, fit_end, moved, hazard_start)[1],
                   "move": _fit_hazards(accounts, fit_end, switched, hazard_start)[1]}
        causes = (("switch", "switcher"), ("move", "mover"))
        predicted: dict[str, list[float]] = {"switch": [], "move": []}
        errors: dict[str, list[float]] = {"switch": [], "move": []}
        for f in forecasts:
            hs = h_cause["switch"].get(f.segment, 0.0)
            hm = h_cause["move"].get(f.segment, 0.0)
            alive, inc = 1.0, {"switch": 0.0, "move": 0.0}
            for _ in range(horizon):
                inc["switch"] += alive * hs
                inc["move"] += alive * hm
                alive *= 1 - hs - hm
            for cause, outcome in causes:
                predicted[cause].append(inc[cause])
                errors[cause].append(inc[cause] - (left_by[f.account_id] == outcome))
        if forecasts:
            incidence_by_cause = {
                c: (sum(predicted[c]) / len(forecasts), len(partition[o]) / len(forecasts))
                for c, o in causes}
        calibration_by_cause = {c: _mean_with_interval(e) for c, e in errors.items()}
    by_year: dict[int, dict[str, int]] = defaultdict(
        lambda: {"months_at_risk": 0, "departures": 0}
        | ({} if moved is None else {"switch": 0, "move": 0}))
    for a in accounts:
        for m in a.monthly_net_gbp:
            by_year[m // 12]["months_at_risk"] += 1
        if a.last_month < book_end:
            row = by_year[a.last_month // 12]
            row["departures"] += 1
            if moved is not None:
                row["move" if a.account_id in moved else "switch"] += 1
    # The oldest contract year holds for every month beyond it. When one calendar year is all that
    # fitted it, the per-customer level for the book's longest-tenured accounts is that year's rate
    # (slice 7: the cut year alone, at every cut), so a good level there is recency, not tenure.
    oldest = max(by_cy)
    oldest_years = {m // 12 for a in accounts if a.first_month <= fit_end
                    for m in range(max(a.first_month + oldest * _MONTHS_PER_CONTRACT_YEAR,
                                       hazard_start if hazard_start is not None else first),
                                   min(a.last_month, fit_end) + 1)}
    if len(oldest_years) == 1:
        limitations.append(
            f"the per-customer hazard's oldest contract year ({oldest}) is fitted on "
            f"{oldest_years.pop()} alone, and holds for every later month of tenure: for the "
            "accounts there its level is one calendar year's rate, not a tenure effect"
        )
    pooled = sorted(s for s, k in k_by_seg.items() if k is None)
    if pooled:
        limitations.append(
            "no between-account margin spread is estimable in segment(s) "
            f"{', '.join(pooled)}: the per-customer margin there IS the flat one"
        )
    limitations.append(
        "margin is settlement-record net before cost-to-serve and bad debt, which the "
        "monthly ledger does not carry"
    )
    return Backtest(
        cut_year=cut_year,
        margin_deviation_fit_months=(_month_label(first), _month_label(dev_end)),
        fit_months=(_month_label(first), _month_label(fit_end)),
        held_back_months=(_month_label(fit_end + 1), _month_label(book_end)),
        accounts_graded=len(forecasts),
        accounts_excluded=excluded,
        shrinkage_k_by_segment=k_by_seg,
        hazard_by_contract_year=by_cy,
        hazard_by_segment=by_seg_h,
        segment_hazard_ratio=seg_ratio,
        forecasts=tuple(forecasts),
        margin_error=_paired("absolute margin error, GBP per account", pc_err, fl_err),
        departure_brier=_paired("departure Brier score per account", pc_brier, fl_brier),
        margin_bias=margin_bias,
        aggregate=aggregate,
        limitations=tuple(limitations),
        margin_deviation_window_reason=dev_reason,
        departures_by_cause=by_cause,
        switch_hazard_by_contract_year=switch_by_cy,
        error_by_outcome=by_outcome,
        departure_calibration={
            "per_customer": _mean_with_interval(
                [f.per_customer_departure_p - f.departed for f in forecasts]),
            "flat": _mean_with_interval([f.flat_departure_p - f.departed for f in forecasts]),
        },
        departure_ranking=_ranking([f for f in forecasts if f.departed],
                                   [f for f in forecasts if not f.departed]),
        departures_by_calendar_year={y: dict(r) for y, r in sorted(by_year.items())},
        hazard_fit_months=(_month_label(first if hazard_start is None else hazard_start),
                           _month_label(fit_end)),
        departure_incidence_by_cause=incidence_by_cause,
        departure_calibration_by_cause=calibration_by_cause,
    )


def load_book(path: Path | str) -> tuple[list[AccountHistory], int]:
    return book_from_run_output(json.loads(Path(path).read_text()))


def backtest_run_output(
    path: Path | str,
    cut_year: int = DEFAULT_CUT_YEAR,
    margin_fit_end_year: int | None = None,
    wholesale_gas_by_month: Mapping[str, float] | None = None,
    hazard_fit_from_year: int | None = None,
) -> Backtest:
    """A run's book, split by departure cause where it carries a move-out register. The caller hands in the wholesale series
    (`SimInterface.monthly_wholesale_prices("gas")`); importing the live interface here would
    give the company layer a route to a real endpoint, which `tools/company_network_isolation`
    refuses."""
    run_output = json.loads(Path(path).read_text())
    return run_backtest(
        *book_from_run_output(run_output), cut_year, margin_fit_end_year,
        wholesale_gas_by_month, move_outs_from_run_output(run_output), hazard_fit_from_year,
    )


if __name__ == "__main__":  # pragma: no cover - a reading aid, not a door
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "docs/reports/run_output_latest.json"
    cut = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_CUT_YEAR
    dev = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] != "-" else None
    hazard_from = int(sys.argv[4]) if len(sys.argv) > 4 else None
    bt = backtest_run_output(target, cut, dev, hazard_fit_from_year=hazard_from)
    print(f"cut {bt.cut_year}: fit {bt.fit_months}, held back {bt.held_back_months}")
    print(f"deviation window {bt.margin_deviation_fit_months}: "
          f"{bt.margin_deviation_window_reason}")
    print(f"graded {bt.accounts_graded}, excluded {dict(bt.accounts_excluded)}")
    print(f"k by segment {bt.shrinkage_k_by_segment}")
    print(f"hazard by contract year {bt.hazard_by_contract_year}")
    print(f"hazard by segment {bt.hazard_by_segment}")
    print(f"segment hazard ratio {bt.segment_hazard_ratio}")
    print(f"margin bias (forecast - realised, per account) {bt.margin_bias}")
    for c in (bt.margin_error, bt.departure_brier):
        print(c)
    print({k: round(v, 1) for k, v in bt.aggregate.items()})
    print(f"departures by cause {bt.departures_by_cause}")
    print(f"hazard window {bt.hazard_fit_months}")
    print(f"departure calibration (mean p - realised) {bt.departure_calibration}")
    print(f"departure ranking {bt.departure_ranking}")
    print(f"flat incidence by cause (predicted, realised) {bt.departure_incidence_by_cause}")
    print(f"flat calibration by cause {bt.departure_calibration_by_cause}")
    for year, row in (bt.departures_by_calendar_year or {}).items():
        print(f"  {year}: {row}")
    for outcome, g in (bt.error_by_outcome or {}).items():
        print(f"{outcome}: {g.accounts} account(s), bias {g.margin_bias}")
        print(f"  {g.margin_error}")
        print(f"  {g.ranking_against_stayers}")
