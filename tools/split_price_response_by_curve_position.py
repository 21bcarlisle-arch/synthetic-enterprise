"""Split a one-variable arm's per-decision `sim_price_response` change by CURVE POSITION and ARM.

Subject: two captured factor tables from `tools/capture_departure_factors.py`, differing by one
variable. Default pair is C3 (the price the household is SHOWN) against `main`:

    baseline  docs/reports/c2_departure_factors.json
    arm       docs/reports/c3_shown_price_departure_factors.json

Opened by: `docs/staging/WORKER_PREREGISTRATION_WHAT_THE_SHOWN_PRICE_MUST_SHOW_2026-08-30.md`,
whose result section names this split as the owed next step:

    "The candidate mechanism for the sign: `_savings_to_rate` is piecewise and flattens toward its
    calibrated ceiling, so a household already deep in the saturated region loses little propensity
    when its perceived saving is cut, while a low-consumption household gains a lot when lifted
    from the steep part of the curve. The gains at the bottom would then outweigh the losses at
    the top. THIS IS NOT ESTABLISHED."

WHY A TOOL AND NOT A ONE-OFF SCRIPT. The hypothesis it tests is about WHERE ON A CURVE a population
sat, and the answer it returns refutes the hypothesis -- so the next person to disbelieve the
refutation needs to re-run it, not re-derive it. It is also the shape any future one-variable arm
wants: `churn_position_multiplier` is the single seam every price-position change passes through,
so "which households did this move, and were they on the steep part or the flat part" is a question
that will be asked again.

Usage:  python3 -m tools.split_price_response_by_curve_position [baseline.json] [arm.json]
"""
from __future__ import annotations

import collections
import json
import statistics
import sys
from pathlib import Path

from simulation.market_switching_propensity import (
    _CALIBRATED_SAVINGS_CEILING_GBP,
    _LAST_INFORMED_SLOPE_PER_GBP,
    _MAX_RATE,
    _PARITY_RATE,
)

PROJECT = Path(__file__).resolve().parent.parent
DEFAULT_BASELINE = PROJECT / "docs" / "reports" / "c2_departure_factors.json"
DEFAULT_ARM = PROJECT / "docs" / "reports" / "c3_shown_price_departure_factors.json"

#: The segment boundaries of `_savings_to_rate`, in GBP of annual pounds-on-the-table. Written as
#: the boundaries rather than re-deriving them from the function, because the function is PIECEWISE
#: WITH A JUMP and its segment edges are the subject here, not an implementation detail.
_SEGMENTS: list[tuple[float, float, str]] = [
    (0.0, 100.0, "0-100    steep bottom"),
    (100.0, 250.0, "100-250  steepest"),
    (250.0, 400.0, "250-400  flattening"),
    (400.0, float("inf"), ">=400    SATURATED"),
]

#: The rate `_savings_to_rate` reaches at the top of its last GRADUATED segment (400 GBP minus an
#: epsilon). NOT `_MAX_RATE`: the curve JUMPS from 0.18 to 0.22 at exactly 400 GBP, so rates in
#: [0.18, 0.22) are unreachable and inverting the graduated formula across that gap fabricates a
#: number. The first draft of this tool did exactly that and reported a mean of 520 GBP for a
#: bucket whose members are all censored at 400 -- caught by printing the curve at real inputs
#: before trusting the table, which is the only reason it is not in the write-up.
_LAST_GRADUATED_RATE = 0.13 + 0.05 * ((400.0 - 1e-9 - 250.0) / 150.0)


def pounds_on_the_table(price_response: float, differential: float) -> tuple[float, bool]:
    """Invert `churn_position_multiplier` to `(|differential| x bill, censored)` in GBP.

    THE BILL IS NOT IN THE CAPTURED TABLE, which is why this inverts rather than reads. That is
    exact rather than approximate: within an arm `churn_position_multiplier` is a strictly monotone
    function of the pounds, so the response determines them -- EXCEPT on the saturated shelf.

    `censored` is True where the answer is a FLOOR and not a value. On the cheaper arm
    `_savings_to_rate` is flat at `_MAX_RATE` above 400 GBP, so every household with a perceived
    saving of 400 GBP or more produces the identical response of 0.227273 and the pounds cannot be
    recovered. Returning 400.0 with the flag set says "at least this", and every caller below
    reports that bucket's pounds as a floor rather than a mean. A tool that silently returned 400.0
    unflagged would be publishing a censored quantity as a measured one.

    The dearer arm has no such shelf: `churn_position_multiplier` continues above the ceiling at
    `_LAST_INFORMED_SLOPE_PER_GBP`, which is invertible, so those recover exactly.
    """
    if differential > 0.0:
        rate = price_response * _PARITY_RATE
        if rate > _MAX_RATE:
            beyond = (rate - _MAX_RATE) / _LAST_INFORMED_SLOPE_PER_GBP
            return _CALIBRATED_SAVINGS_CEILING_GBP + beyond, False
    else:
        rate = _PARITY_RATE / price_response

    if rate >= _LAST_GRADUATED_RATE:
        # On or past the jump. Everything here is the saturated shelf: a floor, not a value.
        return _CALIBRATED_SAVINGS_CEILING_GBP, True
    if rate < 0.07:
        return 100.0 * (rate - 0.05) / 0.02, False
    if rate < 0.13:
        return 100.0 + 150.0 * (rate - 0.07) / 0.06, False
    return 250.0 + 150.0 * (rate - 0.13) / 0.05, False


def segment_of(pounds: float) -> str:
    for lo, hi, name in _SEGMENTS:
        if lo <= pounds < hi:
            return name
    return _SEGMENTS[-1][2]


def load_pairs(baseline_path: Path, arm_path: Path) -> list[dict]:
    """Decisions present in BOTH arms, keyed on (customer, event date).

    THE INTERSECTION IS THE POPULATION AND THE DROPPED ROWS ARE REPORTED. A price change re-times
    some renewals, so the two tables do not hold the same decisions; differencing a decision
    against nothing is how a re-timing gets published as an attrition effect.
    """
    base = {(r["customer_id"], r["event_date"]): r for r in json.loads(baseline_path.read_text())}
    arm = {(r["customer_id"], r["event_date"]): r for r in json.loads(arm_path.read_text())}
    pairs = []
    for key, b in base.items():
        a = arm.get(key)
        if a is None:
            continue
        pounds_b, censored_b = pounds_on_the_table(
            b["sim_price_response"], b["price_differential_vs_market_reference"]
        )
        pounds_a, censored_a = pounds_on_the_table(
            a["sim_price_response"], a["price_differential_vs_market_reference"]
        )
        pairs.append({
            "base": b, "arm": a,
            "pounds_base": pounds_b, "pounds_arm": pounds_a,
            "censored": censored_b or censored_a,
            "segment": segment_of(pounds_b),
            "arm_side": (
                "CHEAPER (we undercut the market)"
                if b["price_differential_vs_market_reference"] <= 0.0
                else "DEARER (we price above it)"
            ),
        })
    return pairs


def _report_side(pairs: list[dict], side: str) -> float:
    sub = [p for p in pairs if p["arm_side"] == side]
    print(f"\n  === {side} — {len(sub)} decisions ===")
    print("  baseline curve position     n  cens   mean pounds  ->  arm     mean price_response      "
          "sum d(p_churn) pp   departures")
    print("  " + "-" * 124)
    for _lo, _hi, name in _SEGMENTS:
        v = [p for p in sub if p["segment"] == name]
        if not v:
            continue
        n_censored = sum(1 for p in v if p["censored"])
        mark = ">=" if n_censored else "  "
        pb = statistics.fmean(p["pounds_base"] for p in v)
        pa = statistics.fmean(p["pounds_arm"] for p in v)
        rb = statistics.fmean(p["base"]["sim_price_response"] for p in v)
        ra = statistics.fmean(p["arm"]["sim_price_response"] for p in v)
        dp = sum(
            100.0 * (p["arm"]["realized_churn_probability"] - p["base"]["realized_churn_probability"])
            for p in v
        )
        db = sum(1 for p in v if p["base"]["event_type"] == "churned")
        da = sum(1 for p in v if p["arm"]["event_type"] == "churned")
        print(f"  {name:26} {len(v):4}  {n_censored:4}  {mark}{pb:6.0f}  -> {mark}{pa:6.0f}     "
              f"{rb:7.3f} -> {ra:7.3f}     {dp:+9.2f}          {db} -> {da}")
    total = sum(
        100.0 * (p["arm"]["realized_churn_probability"] - p["base"]["realized_churn_probability"])
        for p in sub
    )
    print(f"  {'SIDE TOTAL':26} {len(sub):4}{' ' * 62}{total:+9.2f}")
    return total


def main(argv: list[str]) -> int:
    baseline_path = Path(argv[1]) if len(argv) > 1 else DEFAULT_BASELINE
    arm_path = Path(argv[2]) if len(argv) > 2 else DEFAULT_ARM
    n_base = len(json.loads(baseline_path.read_text()))
    n_arm = len(json.loads(arm_path.read_text()))
    pairs = load_pairs(baseline_path, arm_path)

    print(f"baseline: {baseline_path.name}  ({n_base} renewal decisions)")
    print(f"arm     : {arm_path.name}  ({n_arm})")
    print(f"paired  : {len(pairs)}   dropped as unmatched (re-timed by the change): "
          f"{n_base - len(pairs)}")
    print()
    print("  `>=` marks a CENSORED bucket: the curve is flat above 400 GBP on the cheaper side, so")
    print("  those pounds are a floor and not a mean. See `pounds_on_the_table`.")

    cheaper = _report_side(pairs, "CHEAPER (we undercut the market)")
    dearer = _report_side(pairs, "DEARER (we price above it)")

    print()
    print(f"  NET over {len(pairs)} paired decisions: {cheaper + dearer:+.2f}pp summed, "
          f"mean {(cheaper + dearer) / len(pairs):+.4f}pp per decision.")

    # The monotone check: within a side, does a fall in perceived pounds always move the response
    # the same way? If it does, curve POSITION cannot be what decides the sign -- SIDE is.
    violations = 0
    moved = 0
    for p in pairs:
        d_pounds = p["pounds_arm"] - p["pounds_base"]
        d_resp = p["arm"]["sim_price_response"] - p["base"]["sim_price_response"]
        if abs(d_pounds) < 1e-9 or abs(d_resp) < 1e-9:
            continue
        moved += 1
        expected_up = (d_pounds < 0) if p["arm_side"].startswith("CHEAPER") else (d_pounds > 0)
        if (d_resp > 0) != expected_up:
            violations += 1
    print(f"  Decisions whose response moved: {moved}. Violations of "
          f"'fewer perceived pounds -> more switchy when cheaper, less switchy when dearer': "
          f"{violations}.")
    print()
    print("  READ THE SIDES, NOT THE SEGMENTS. If every segment within a side carries the same")
    print("  sign, then where a household sat on the curve sets the SIZE of its move and not the")
    print("  direction; what sets the direction is which side of the market the company priced on.")

    year_mix: dict[int, list[int]] = collections.defaultdict(lambda: [0, 0])
    for p in pairs:
        year_mix[int(p["base"]["event_date"][:4])][0 if p["arm_side"].startswith("CHEAPER") else 1] += 1
    print()
    print("  year   cheaper  dearer   share cheaper")
    for year in sorted(year_mix):
        c, d = year_mix[year]
        print(f"  {year}    {c:5}   {d:5}     {c / (c + d):.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
