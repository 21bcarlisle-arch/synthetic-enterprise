"""B11 — forward customer value, fitted on the book's early years and graded on the later ones.

WHAT IS FORECAST, SAID BEFORE IT IS MEASURED. For every billing account on supply at the
end of the cut year, two things over the held-back months that follow:

  * MARGIN — the settlement-record net margin the account earns (`net_gbp` in the run's
    `per_customer_monthly`, summed across the account's fuels by
    `saas.customer_reaction._billing_account_id`). It is the company's own ledger figure
    BEFORE cost-to-serve and bad debt; neither is in the monthly record, so neither is in
    the forecast or in what it is graded against.
  * DEPARTURE — the account's last supplied month falls before the book's last month. A
    departure is any end of supply. ``LIMITATION_DEPARTURE_CAUSE`` is carried on every
    result: the book cannot yet split departures into switches and home moves, so the
    hazard here is all-cause and no lever that acts on one cause can be graded against it.

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
from pathlib import Path
from statistics import NormalDist
from typing import Mapping, Sequence

from saas.customer_reaction import _billing_account_id

__all__ = [
    "DEFAULT_CUT_YEAR",
    "LIMITATION_DEPARTURE_CAUSE",
    "AccountHistory",
    "Backtest",
    "PairedComparison",
    "book_from_run_output",
    "load_book",
    "run_backtest",
    "backtest_run_output",
]

DEFAULT_CUT_YEAR = 2020

LIMITATION_DEPARTURE_CAUSE = (
    "departures cannot yet be split into switches and moves: the book records only that "
    "supply ended, so the hazard is all-cause"
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
    accounts: Sequence[AccountHistory], fit_end: int
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
    """
    at_risk_cy: dict[int, int] = defaultdict(int)
    exits_cy: dict[int, int] = defaultdict(int)
    at_risk_seg: dict[str, int] = defaultdict(int)
    exits_seg: dict[str, int] = defaultdict(int)
    for a in accounts:
        if a.first_month > fit_end:
            continue
        end = min(a.last_month, fit_end)
        for m in range(a.first_month, end + 1):
            cy = (m - a.first_month) // _MONTHS_PER_CONTRACT_YEAR
            at_risk_cy[cy] += 1
            at_risk_seg[a.segment] += 1
        if a.last_month < fit_end:
            cy = (a.last_month - a.first_month) // _MONTHS_PER_CONTRACT_YEAR
            exits_cy[cy] += 1
            exits_seg[a.segment] += 1
    years = sorted(at_risk_cy)
    while len(years) > 1 and exits_cy[years[-1]] == 0:
        last = years.pop()
        at_risk_cy[years[-1]] += at_risk_cy.pop(last)
    by_cy = {cy: exits_cy[cy] / at_risk_cy[cy] for cy in years}
    by_seg = {s: exits_seg[s] / n for s, n in at_risk_seg.items()}
    expected: dict[str, float] = defaultdict(float)
    for a in accounts:
        if a.first_month > fit_end:
            continue
        for m in range(a.first_month, min(a.last_month, fit_end) + 1):
            expected[a.segment] += _hazard_at(by_cy, m - a.first_month)
    ratio = {
        s: (exits_seg[s] / expected[s]) if expected[s] > 0 else 1.0 for s in at_risk_seg
    }
    return by_cy, by_seg, ratio


def _hazard_at(by_cy: Mapping[int, float], tenure_months: int) -> float:
    # Beyond the longest tenure the fit years saw, the oldest contract year's rate holds.
    cy = min(tenure_months // _MONTHS_PER_CONTRACT_YEAR, max(by_cy))
    return by_cy[cy]


def run_backtest(
    accounts: Sequence[AccountHistory],
    book_end: int,
    cut_year: int = DEFAULT_CUT_YEAR,
    margin_fit_end_year: int | None = None,
) -> Backtest:
    """Fit on months up to December of `cut_year`; forecast and grade every later month.

    `margin_fit_end_year` (B11 slice 2) takes the per-customer DEVIATION -- own mean minus
    segment mean, and the shrinkage `k` -- from the months up to that year only, and adds it
    to the segment level fitted through the cut. The level stays the flat rule's; only which
    accounts sit above or below their segment comes from the earlier window. At the default
    (the cut year) it is `w*own + (1-w)*segment`, the rule as first shipped. An account with
    no month in the earlier window gets its segment's value.
    """
    fit_end = _month_index(f"{cut_year}-12")
    dev_end = fit_end if margin_fit_end_year is None else _month_index(
        f"{margin_fit_end_year}-12")
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
    by_cy, by_seg_h, seg_ratio = _fit_hazards(accounts, fit_end)
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
    limitations = [LIMITATION_DEPARTURE_CAUSE]
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
    )


def load_book(path: Path | str) -> tuple[list[AccountHistory], int]:
    return book_from_run_output(json.loads(Path(path).read_text()))


def backtest_run_output(
    path: Path | str, cut_year: int = DEFAULT_CUT_YEAR, margin_fit_end_year: int | None = None
) -> Backtest:
    return run_backtest(*load_book(path), cut_year, margin_fit_end_year)


if __name__ == "__main__":  # pragma: no cover - a reading aid, not a door
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "docs/reports/run_output_latest.json"
    cut = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_CUT_YEAR
    dev = int(sys.argv[3]) if len(sys.argv) > 3 else None
    bt = backtest_run_output(target, cut, dev)
    print(f"cut {bt.cut_year}: fit {bt.fit_months}, held back {bt.held_back_months}")
    print(f"graded {bt.accounts_graded}, excluded {dict(bt.accounts_excluded)}")
    print(f"k by segment {bt.shrinkage_k_by_segment}")
    print(f"hazard by contract year {bt.hazard_by_contract_year}")
    print(f"hazard by segment {bt.hazard_by_segment}")
    print(f"segment hazard ratio {bt.segment_hazard_ratio}")
    print(f"margin bias (forecast - realised, per account) {bt.margin_bias}")
    for c in (bt.margin_error, bt.departure_brier):
        print(c)
    print({k: round(v, 1) for k, v in bt.aggregate.items()})
