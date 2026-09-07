"""The commodity share of the domestic electricity UNIT RATE, read off Ofgem's own cap model.

WHY THIS EXISTS
---------------
`docs/market_research/domestic_shift_response_as_a_function_of_pass_through.md` needs `s`, the
commodity share of the domestic electricity unit rate, to convert a tariff pass-through into the
peak-to-off-peak price ratio a household actually faces. It could only anchor `s` partially: the
knowledge map carries "wholesale (~40%)" of the **cap**, and recorded — correctly — that the
unit-rate share must be HIGHER, because the standing charge carries network residual and other
fixed costs the unit rate then does not. It named reading the cap's unit-rate composition as the
cheapest open job it had.

THIS IS A READING OF PUBLISHED LAW, NOT AN ESTIMATE. Ofgem's supplementary "default tariff cap
level" model publishes, per charge restriction period and per distribution region, the £/year cap
allowance for each cost component at the benchmark consumption AND at nil consumption. The nil
column IS the standing charge. So

    unit rate component (p/kWh) = (benchmark £/yr - nil £/yr) / benchmark kWh x 100

is Ofgem's own construction, not an apportionment invented here, and

    s = (DF + CM unit-rate components) / (total unit rate)

is the commodity share of the unit rate exactly as the bridge needs it.

WHAT `s` TURNS OUT TO BE, AND WHY A SCALAR WOULD HAVE BEEN WRONG
----------------------------------------------------------------
It is not a constant. It runs from ~0.42 in the calm period before the gas crisis to ~0.81 at the
January 2023 peak. The landed bridge printed a grid whose best-supported row was 0.40 — BELOW every
value the law actually carries, in every period, which is the direction that finding predicted from
the denominators alone. A caller wanting one number must say which cap period it is for.

TWO THINGS THAT WOULD HAVE MADE THIS READ WRONG, GUARDED HERE
--------------------------------------------------------------
1. **The two sheets do not have the same column count.** `ElecSingle_Other_3100kWh` ends at column
   57 and `ElecSingle_Other_Nil` at 58 in v1.19. Indexing the nil sheet with the benchmark sheet's
   column number happens to work for these two but is one Ofgem revision away from silently
   subtracting the wrong period. Columns are resolved by their PERIOD LABEL in each sheet
   independently, and a period present in one sheet and not the other is skipped by name.
2. **The components are ex-VAT and the published headline cap is not.** A share is unaffected by a
   uniform VAT rate, so `s` is safe either way — but the derived unit rate is not, and it is
   published here. It is cross-checked against
   `docs/domain_artefact_library/regulatory/ofgem_default_tariff_cap_windows.json`, which carries
   the published INCLUDING-VAT levels: the check is that derived x VAT reproduces them. That check
   is the reason to believe the decomposition at all, so it FAILS CLOSED rather than warning. VAT is
   itself per-period — electricity is zero-rated from October 2026 to March 2027 — so it is a
   schedule here and not the 1.05 that a "uniform rate" reading would have applied.
3. **THE BENCHMARK CONSUMPTION IS NOT A CONSTANT AND THE SHEET HEADER IS NOT THE ANSWER.** The
   denominator changed twice in 2026 and the sheet carries all three bases under one header cell
   reading the LATEST of them. Reading that cell divides 29 of 33 periods by 2,500 instead of 3,100
   and inflates every historical unit rate by 24% — while every share stays right, because the
   divisor cancels, so the headline this module exists to publish would look untouched.
   `BENCHMARK_KWH_SCHEDULE` carries the dated bases and `_verify_benchmark_schedule` refuses if the
   workbook stops agreeing with them.

ALL THREE PAYMENT METHODS ARE MEASURED, not just direct debit. Publishing one share over a
population that is really three is this project's most expensive recurring shape; the three differ
and the artefact carries all of them.
"""

from __future__ import annotations

import json
import re
import statistics
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

MODEL_DIR = PROJECT / "sim" / "cache" / "ofgem_cap_level_models"
OUT_PATH = (PROJECT / "docs" / "domain_artefact_library" / "regulatory"
            / "ofgem_cap_unit_rate_composition.json")
CAP_WINDOWS = (PROJECT / "docs" / "domain_artefact_library" / "regulatory"
               / "ofgem_default_tariff_cap_windows.json")

#: WHERE THE MODEL ACTUALLY LIVES, and it is not where this artefact looked until 2026-09-07. The
#: old URL (/energy-policy-and-regulation/policy-and-regulatory-programmes/default-tariff-cap) is a
#: policy page: it returns 200 and carries exactly one workbook link, the Annex 9 levelisation
#: model, which is a different publication. So the recorded recipe "go there and read the cap level
#: model's version" could never terminate in anything but `cannot_tell`, and the artefact sat behind
#: v1.19 for twelve cap periods while its supersession check ran and reported nothing. THIS page
#: carries the full versioned history, v1.2 (2019-02) to v1.31 (2026-08).
MODEL_INDEX_URL = (
    "https://www.ofgem.gov.uk/energy-regulation/domestic-and-non-domestic/energy-pricing-rules"
    "/energy-price-cap/energy-price-cap-default-tariff-levels"
)

#: Ofgem's benchmark annual consumption for the single-rate electricity meter, in kWh, PER CAP
#: PERIOD — and it is not one number, which is the whole reason this is a schedule and not a
#: constant. Each entry is (first cap period start it applies to, kWh); the first entry has no start
#: because it is the basis every period ran on until the first revision.
#:
#: THE SHEET'S OWN HEADER CELL IS NOT THE ANSWER AND TAKING IT IS WRONG BY 24%. In v1.31 the header
#: of `ElecSingle_Other_Benchmark` reads "2,500 kWh" while its own note says every cap period up to
#: P15b is still on 3,100 — one header, three bases, in one column block. A reader that trusts the
#: header divides 29 of 33 periods by 2,500, runs 24% high on every historical unit rate, and every
#: SHARE stays right because the divisor cancels, so nothing in the headline would look wrong.
#:
#: WHERE EACH ROW COMES FROM, and the three do not have the same standing:
#:   3100 — the basis of the whole pre-2026 series. Corroborated against published including-VAT cap
#:          levels: the eight periods January 2024 – October 2025 that can be checked land within
#:          0.5%, and at 2,500 the same eight land 24% high. This one is measured, not asserted.
#:   2700 — Ofgem's 21 November 2025 benchmark-consumption decision, in force from cap P15b.
#:   2500 — the 27 May 2026 "review of typical domestic consumption values" decision, from cap P16b.
#: The two 2026 rows are the publisher's own figures, read from the `1c` consumption table (NOT from
#: prose), and `_verify_benchmark_schedule` refuses if the workbook stops agreeing with them. They
#: are NOT independently corroborated: `ofgem_default_tariff_cap_windows.json` stops at 2025-12-31,
#: so there is no published level to check the four 2026 periods against. That is stated in the
#: artefact's basis rather than left for the reader to discover.
BENCHMARK_KWH_SCHEDULE: tuple[tuple[str | None, int], ...] = (
    (None, 3100),
    ("2026-01-01", 2700),
    ("2026-07-01", 2500),
)

#: The `1c` cells the schedule's two revised rows are checked against, as
#: (column header must contain, expected MWh). The header carries the date range in words, so this
#: is checking BOTH the value and the period it is claimed for.
BENCHMARK_SCHEDULE_WITNESS = (
    ("Jan 2026 - Jun 2026", 2.7),
    ("July 2026 onwards", 2.5),
)
BENCHMARK_WITNESS_SHEET = "1c Consumption adjusted levels"
BENCHMARK_WITNESS_ROW_LABEL = "Electricity: Single-rate"

#: VAT on domestic ELECTRICITY, as a multiplier, per cap period — also not one number. The cap
#: model's component build-up is ex-VAT and the published cap levels are inclusive, so this is the
#: conversion between two published quantities and it is what the cross-check applies. The zero-rated
#: window is the Government's announcement, named in the v1.31 model's own `1a` note
#: (https://www.gov.uk/government/news/new-pm-cuts-tax-on-household-electricity-bills-to-give-breathing-space-on-cost-of-living)
#: and visible in the workbook: for October–December 2026 the model's "GB average, inc VAT"
#: electricity row is IDENTICAL to its ex-VAT row, while gas on the same row still carries 5%.
#: Each entry is (from, to-exclusive, multiplier); anything outside them is `VAT_MULTIPLIER_DEFAULT`.
VAT_MULTIPLIER_DEFAULT = 1.05
VAT_MULTIPLIER_WINDOWS: tuple[tuple[str, str, float], ...] = (
    ("2026-10-01", "2027-04-01", 1.00),
)

#: How closely derived-x-VAT must reproduce the published cap level before the decomposition is
#: believed, as a proportion. Set from what a correct read actually achieves (better than 0.5%
#: across every period checked) with room for Ofgem's own rounding of the published p/kWh headline.
CROSS_CHECK_TOLERANCE = 0.02

#: The date the default tariff cap came into force. Columns before it are Ofgem's OWN back-cast,
#: labelled "Historical examples ... for illustration only" in the model itself -- a cap level for a
#: period in which no cap existed. They are read and published here, but they are NOT the law and
#: the headline share is taken over the in-force periods only. Some of them fall below 0.40, so
#: mixing the two would have made the headline claim false in the flattering direction.
CAP_IN_FORCE_FROM = "2019-01-01"

#: The components that are the COMMODITY. DF is the wholesale direct fuel allowance; CM is the
#: capacity market cost, which is a wholesale-category component in Ofgem's own row labelling.
#: Everything else -- policy, network, operating, EBIT, headroom, adjustment allowance -- is not.
COMMODITY_COMPONENTS = ("DF", "CM")

PAYMENT_METHODS = {
    "direct_debit": "Other",
    "standard_credit": "SC",
    "prepayment": "PPM",
}


def _named(path: Path) -> str:
    """A path for a REFUSAL MESSAGE, project-relative when it can be and whole when it cannot.

    `Path.relative_to` RAISES on a path outside the project, so building a refusal message with it
    turns a clean refusal into a ValueError from inside the error path -- the fail-open that is
    hardest to see, because the caller gets a crash where the code was carefully written to explain
    itself. Found by the control that pointed this module at a temporary directory.
    """
    try:
        return str(path.relative_to(PROJECT))
    except ValueError:
        return str(path)


class CapModelUnavailable(RuntimeError):
    """Raised when the cap composition cannot be read.

    Deliberately an exception. The model workbooks are gitignored source data, so a linked worktree
    extract has none of them, and an instrument that returned "commodity share 0.0" there would read
    exactly like "measured the law, found no wholesale in it".
    """


def _sheet_rows(worksheet) -> tuple[dict[str, int], dict[tuple[str, str], tuple]]:
    """(period label -> column index, (region, component) -> its row).

    Both keyed by NAME, never by position, for the reason the module docstring gives: the two
    sheets this is joined across do not agree on column count.
    """
    rows = list(worksheet.iter_rows(min_row=12, max_row=worksheet.max_row,
                                    max_col=worksheet.max_column, values_only=True))
    if not rows:
        raise CapModelUnavailable(f"sheet {worksheet.title!r} carries no rows from row 12")
    header = {str(cell).strip(): index
              for index, cell in enumerate(rows[0]) if cell and "20" in str(cell)}
    body: dict[tuple[str, str], tuple] = {}
    for row in rows[3:]:
        component, region = row[2], row[3]
        if component and region:
            body[(str(region), str(component))] = row
    if not header or not body:
        raise CapModelUnavailable(
            f"sheet {worksheet.title!r} yielded {len(header)} periods and {len(body)} component "
            "rows; the model's layout is not what this reader was written against"
        )
    return header, body


def _number(row: tuple, index: int) -> float | None:
    value = row[index] if index < len(row) else None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def benchmark_kwh(period_start: str | None) -> int:
    """The divisor Ofgem's model applies to a cap period starting `period_start`.

    A period whose start cannot be parsed gets the earliest basis, because every unlabelled column
    in this model is one of Ofgem's pre-2019 illustrative back-casts and those are all pre-2026.
    """
    divisor = BENCHMARK_KWH_SCHEDULE[0][1]
    for starts_from, kwh in BENCHMARK_KWH_SCHEDULE[1:]:
        if period_start and starts_from and period_start >= starts_from:
            divisor = kwh
    return divisor


def _benchmark_sheet_name(workbook, suffix: str) -> str:
    """The benchmark sheet, resolved by PATTERN rather than by a name built from the divisor.

    v1.19 calls it `ElecSingle_Other_3100kWh` and v1.31 calls it `ElecSingle_Other_Benchmark`. The
    old f-string could only name one of those, so it failed closed on v1.31 — which is the right
    failure, and it is also why this artefact sat twelve cap periods behind. Both spellings are
    accepted; a sheet named for a consumption is NOT read as evidence of the divisor, because in
    v1.31 the two disagree for four periods.
    """
    pattern = re.compile(rf"^ElecSingle_{re.escape(suffix)}_(Benchmark|\d+kWh)$")
    matches = [name for name in workbook.sheetnames if pattern.match(name)]
    if len(matches) != 1:
        raise CapModelUnavailable(
            f"expected exactly one sheet matching {pattern.pattern!r}, found {matches}; the model's "
            "sheet naming is not what this reader was written against"
        )
    return matches[0]


def _verify_benchmark_schedule(workbook, periods_present: list[str | None]) -> list[dict]:
    """Refuse unless the workbook's own consumption table still says what the schedule says.

    THIS IS THE CONTROL THAT MAKES THE SCHEDULE SAFE TO HARDCODE. A dated divisor written into this
    module is a claim about the publisher, and a claim about the publisher that nothing re-asks is
    exactly the shape that put this artefact twelve editions behind. So the two 2026 rows are
    checked against `1c`'s consumption table, which states them as figures against named date ranges
    rather than in prose, and a disagreement REFUSES rather than warns: a fourth basis arriving
    unnoticed would inflate a published unit-rate series while leaving every share correct.

    It fails closed the other way too. If the model carries a cap period on or after the first
    revision and the witness table cannot be read at all, the divisor for those periods is
    unverifiable and nothing is published — rather than falling back on the pre-2026 basis, which
    would be wrong by 24% and silent.
    """
    first_revision = BENCHMARK_KWH_SCHEDULE[1][0]
    revised_periods = [start for start in periods_present
                       if start and first_revision and start >= first_revision]
    if BENCHMARK_WITNESS_SHEET not in workbook.sheetnames:
        if revised_periods:
            raise CapModelUnavailable(
                f"the model carries {len(revised_periods)} cap period(s) from {first_revision} but "
                f"has no {BENCHMARK_WITNESS_SHEET!r} sheet to confirm which benchmark consumption "
                "they are divided by. The schedule is not applied on trust."
            )
        return []
    sheet = workbook[BENCHMARK_WITNESS_SHEET]
    rows = list(sheet.iter_rows(min_row=1, max_row=12, max_col=8, values_only=True))
    header = next((row for row in rows if any(
        isinstance(cell, str) and "benchmark consumption" in cell.lower() for cell in row)), None)
    body = next((row for row in rows if any(
        isinstance(cell, str) and cell.strip().startswith(BENCHMARK_WITNESS_ROW_LABEL)
        for cell in row)), None)
    if header is None or body is None:
        if revised_periods:
            raise CapModelUnavailable(
                f"{BENCHMARK_WITNESS_SHEET!r} carries no benchmark-consumption table for "
                f"{BENCHMARK_WITNESS_ROW_LABEL!r}, so the {len(revised_periods)} cap period(s) from "
                f"{first_revision} cannot have their divisor confirmed"
            )
        return []
    witnessed = []
    for phrase, expected_mwh in BENCHMARK_SCHEDULE_WITNESS:
        column = next((index for index, cell in enumerate(header)
                       if isinstance(cell, str) and phrase.lower() in cell.lower()), None)
        found = body[column] if column is not None and column < len(body) else None
        if not isinstance(found, (int, float)) or isinstance(found, bool):
            raise CapModelUnavailable(
                f"{BENCHMARK_WITNESS_SHEET!r} does not state a benchmark consumption for "
                f"{phrase!r}; the schedule in this module claims one and the model no longer "
                "confirms it, so the divisor for the 2026 periods is not established"
            )
        if round(float(found) * 1000) != round(expected_mwh * 1000):
            raise CapModelUnavailable(
                f"{BENCHMARK_WITNESS_SHEET!r} says {float(found)} MWh for {phrase!r} and "
                f"BENCHMARK_KWH_SCHEDULE assumes {expected_mwh} MWh. The benchmark consumption has "
                "been revised again. Every unit rate on the new basis would be published wrong "
                "while every share stayed right, so nothing is published until the schedule is "
                "brought up to the model."
            )
        witnessed.append({"applies_from": phrase, "kwh": int(round(float(found) * 1000))})
    return witnessed


def vat_multiplier(period_start: str | None) -> float:
    """The VAT multiplier on domestic ELECTRICITY for a cap period, which is not always 1.05."""
    for begins, ends, multiplier in VAT_MULTIPLIER_WINDOWS:
        if period_start and begins <= period_start < ends:
            return multiplier
    return VAT_MULTIPLIER_DEFAULT


def composition(model_path: Path, payment_method: str) -> dict:
    """Per cap period, the unit-rate composition for one payment method.

    Regions are reported as a median with the full min..max spread beside it, never as a bare
    average: the regional spread is real (it is network cost) and a reader who is told only the
    middle cannot see how wide it is.
    """
    try:
        import openpyxl
    except ImportError as exc:  # pragma: no cover - environment, not logic
        raise CapModelUnavailable(f"openpyxl is needed to read the cap model: {exc}") from exc

    suffix = PAYMENT_METHODS[payment_method]
    workbook = openpyxl.load_workbook(model_path, read_only=True, data_only=True)
    try:
        benchmark_sheet = _benchmark_sheet_name(workbook, suffix)
        nil_sheet = f"ElecSingle_{suffix}_Nil"
        if nil_sheet not in workbook.sheetnames:
            raise CapModelUnavailable(
                f"{model_path.name} has no sheet {nil_sheet!r}; it is not a cap level model of the "
                "shape this reader was written against"
            )
        head_full, body_full = _sheet_rows(workbook[benchmark_sheet])
        head_nil, body_nil = _sheet_rows(workbook[nil_sheet])
        witnessed = _verify_benchmark_schedule(
            workbook, [_period_start(label) for label in set(head_full) & set(head_nil)])
    finally:
        workbook.close()

    regions = sorted({region for region, _ in body_full if region})
    periods = []
    for label in sorted(set(head_full) & set(head_nil), key=lambda k: head_full[k]):
        column_full, column_nil = head_full[label], head_nil[label]
        starts = _period_start(label)
        divisor = benchmark_kwh(starts)
        shares: list[float] = []
        unit_rates: list[float] = []
        standing: list[float] = []
        for region in regions:
            total_full = body_full.get((region, f"Total_{region}"))
            total_nil = body_nil.get((region, f"Total_{region}"))
            if total_full is None or total_nil is None:
                continue
            full_year, nil_year = _number(total_full, column_full), _number(total_nil, column_nil)
            if full_year is None or nil_year is None:
                continue
            unit_rate = (full_year - nil_year) / divisor * 100.0
            if unit_rate <= 0:
                continue
            commodity = 0.0
            for component in COMMODITY_COMPONENTS:
                at_full = body_full.get((region, component))
                at_nil = body_nil.get((region, component))
                if at_full is None or at_nil is None:
                    continue
                commodity += ((_number(at_full, column_full) or 0.0)
                              - (_number(at_nil, column_nil) or 0.0))
            shares.append(commodity / divisor * 100.0 / unit_rate)
            unit_rates.append(unit_rate)
            standing.append(nil_year / 365.0 * 100.0)
        if not shares:
            continue
        periods.append({
            "cap_period": label,
            "starts": starts,
            "cap_in_force": bool(starts and starts >= CAP_IN_FORCE_FROM),
            "benchmark_kwh": divisor,
            "commodity_share_of_unit_rate": round(statistics.median(shares), 4),
            "commodity_share_min": round(min(shares), 4),
            "commodity_share_max": round(max(shares), 4),
            "unit_rate_p_per_kwh_ex_vat": round(statistics.median(unit_rates), 3),
            "standing_charge_p_per_day_ex_vat": round(statistics.median(standing), 3),
            "regions": len(shares),
        })
    if not periods:
        raise CapModelUnavailable(
            f"{model_path.name} yielded no period with a positive unit rate in any region"
        )
    return {"payment_method": payment_method, "periods": periods,
            "benchmark_consumption_witnessed_in_model": witnessed}


#: A window whose `source` starts with this was itself derived from the cap level model, so checking
#: this module's derivation against it compares the workbook with itself. THAT IS NOT CORROBORATION
#: AND IT WOULD NOT LOOK LIKE A DEFECT: the excluded rows agree almost exactly, so admitting them
#: would IMPROVE the reported worst error while destroying what the number means. The cross-check is
#: the only evidence the benchmark-minus-nil decomposition is right; it has to stand on a series
#: published by a route that does not pass through this workbook.
SELF_DERIVED_WINDOW_SOURCE = "ofgem_default_tariff_cap_level_model"


def _published_levels() -> list[dict]:
    """Published cap levels that can honestly corroborate this module — self-derived rows removed."""
    if not CAP_WINDOWS.exists():
        raise CapModelUnavailable(
            f"{_named(CAP_WINDOWS)} is absent, so the derived unit rate cannot be "
            "checked against the published one. The decomposition is not published unchecked."
        )
    windows = json.loads(CAP_WINDOWS.read_text()).get("windows", [])
    return [window for window in windows
            if not str(window.get("source", "")).startswith(SELF_DERIVED_WINDOW_SOURCE)]


_MONTHS = {name: index for index, name in enumerate(
    ["January", "February", "March", "April", "May", "June",
     "July", "August", "September", "October", "November", "December"], start=1)}


def _period_start(label: str) -> str | None:
    """'April 2022 - September 2022' -> '2022-04-01'. None when the label is not a period."""
    head = label.split("-")[0].split("–")[0].strip().split()
    if len(head) != 2 or head[0] not in _MONTHS or not head[1].isdigit():
        return None
    return f"{head[1]}-{_MONTHS[head[0]]:02d}-01"


def cross_check(periods: list[dict]) -> dict:
    """Derived unit rate x VAT against Ofgem's published including-VAT cap level.

    THIS IS THE EVIDENCE THE DECOMPOSITION IS RIGHT, not a formality. The subtraction
    (benchmark - nil) is the whole method; if it reproduces the published headline across the cap
    periods it can be checked on, the components underneath it are being read correctly too.
    """
    published = {window["from"]: window for window in _published_levels()}
    checked, worst, rows = 0, 0.0, []
    for period in periods:
        start = _period_start(period["cap_period"])
        window = published.get(start) if start else None
        if window is None or not isinstance(window.get("elec"), (int, float)):
            continue
        # The artefact carries GBP/MWh including VAT; p/kWh x 10 = GBP/MWh is its own conversion.
        derived = period["unit_rate_p_per_kwh_ex_vat"] * vat_multiplier(start) * 10.0
        error = abs(derived - window["elec"]) / window["elec"]
        checked += 1
        worst = max(worst, error)
        rows.append({"cap_period": period["cap_period"], "derived_gbp_per_mwh": round(derived, 2),
                     # `.get`, not `[...]`: cross_check's contract is a period's DERIVED unit rate
                     # against a published level, and callers that hand it only that much -- the
                     # controls in tests/tools/test_tou_price_shape_episode.py do -- must keep
                     # working. The basis is reported when it is known, not demanded.
                     "benchmark_kwh": period.get("benchmark_kwh"),
                     "vat_multiplier": vat_multiplier(start),
                     "published_gbp_per_mwh": window["elec"], "relative_error": round(error, 5)})
    if not checked:
        raise CapModelUnavailable(
            "no cap period in the model could be matched to a published level, so the "
            "decomposition has no corroboration and is not published"
        )
    if worst > CROSS_CHECK_TOLERANCE:
        raise CapModelUnavailable(
            f"the derived unit rate misses the published cap level by {worst:.1%} at worst, over "
            f"{CROSS_CHECK_TOLERANCE:.0%} tolerance. The benchmark-minus-nil decomposition is not "
            "reproducing Ofgem's own published headline, so nothing under it should be believed."
        )
    return {"periods_checked": checked, "worst_relative_error": round(worst, 5), "rows": rows}


def _corroboration_by_basis(periods: list[dict]) -> dict:
    """Per benchmark basis, how many published periods the cross-check actually reaches.

    THE CROSS-CHECK COVERS LESS OF THE SERIES EVERY QUARTER AND NOTHING SAID SO. It can only reach a
    period for which `ofgem_default_tariff_cap_windows.json` carries a published level, and that
    artefact stops before the 2026 periods -- which are precisely the ones on the two NEW divisors.
    So the basis that most needs corroborating is the one with none, and a reader seeing "worst
    error 0.5%" beside a 33-period table would reasonably assume otherwise. This counts it instead
    of leaving it to be noticed.
    """
    published = {window["from"] for window in _published_levels()}
    by_basis: dict[int, dict] = {}
    for period in periods:
        entry = by_basis.setdefault(period["benchmark_kwh"],
                                    {"benchmark_kwh": period["benchmark_kwh"],
                                     "periods_published": 0, "periods_cross_checked": 0})
        entry["periods_published"] += 1
        if period["starts"] in published:
            entry["periods_cross_checked"] += 1
    rows = [by_basis[key] for key in sorted(by_basis)]
    uncorroborated = [row["benchmark_kwh"] for row in rows if not row["periods_cross_checked"]]
    return {
        "by_benchmark_kwh": rows,
        "bases_with_no_cross_checked_period": uncorroborated,
        "what_that_means": (
            "A basis listed in `bases_with_no_cross_checked_period` has NO period whose derived "
            "unit rate could be compared with a published cap level, because "
            "ofgem_default_tariff_cap_windows.json does not reach it. Those periods' unit rates "
            "rest on the model's own consumption table alone. Their SHARES are unaffected: a share "
            "is a ratio and the divisor cancels, so it is right whatever the benchmark is."
            if uncorroborated else
            "Every benchmark basis published here has at least one period checked against a "
            "published cap level."
        ),
    }


def latest_model() -> Path:
    """The model workbook covering the most cap periods.

    Ofgem republishes the whole history in every revision, so the highest version covers every
    earlier one. Chosen by version number parsed from the filename, not by mtime: a cache refetched
    in a different order would otherwise silently change which law was read.
    """
    if not MODEL_DIR.exists():
        raise CapModelUnavailable(
            f"{_named(MODEL_DIR)} is absent. The cap level models are gitignored "
            "source data, which is what a linked worktree extract looks like, and it is NOT a "
            "finding that the cap carries no commodity cost."
        )
    candidates = []
    for path in MODEL_DIR.glob("*.xlsx"):
        digits = path.stem.replace("_", ".").split("v")[-1].split(".")
        version = tuple(int(part) for part in digits[:2] if part.isdigit())
        if len(version) == 2:
            candidates.append((version, path))
    if not candidates:
        raise CapModelUnavailable(f"no versioned cap level model in {_named(MODEL_DIR)}")
    return max(candidates)[1]


def measure() -> dict:
    model = latest_model()
    by_method = {name: composition(model, name) for name in PAYMENT_METHODS}
    direct_debit = by_method["direct_debit"]["periods"]
    in_force = [p["commodity_share_of_unit_rate"] for p in direct_debit if p["cap_in_force"]]
    if not in_force:
        raise CapModelUnavailable(
            "no period in the model falls on or after the date the cap came into force, so every "
            "share available is Ofgem's own illustrative back-cast and none of it is the law"
        )
    return {
        "artefact": "ofgem_cap_unit_rate_composition",
        "what_this_is": (
            "The COMMODITY SHARE OF THE DOMESTIC ELECTRICITY UNIT RATE, derived from Ofgem's own "
            "published cap level model as (benchmark-consumption allowance minus nil-consumption "
            "allowance) / benchmark kWh, per component. The nil column IS the standing charge, so "
            "this is Ofgem's construction and not an apportionment invented here."
        ),
        "why_it_was_needed": (
            "The shift-response bridge converts a tariff pass-through into the price ratio a "
            "household faces, and needs the commodity share of the UNIT RATE. The knowledge map "
            "carried wholesale ~40% of the BILL -- a different denominator. This closes that gap."
        ),
        "source_model": model.name,
        "source_url": MODEL_INDEX_URL,
        "basis": {
            "vat": (
                "Components are EX-VAT, and VAT ON ELECTRICITY IS NOT A CONSTANT: it is 5% except "
                "from 2026-10-01 to 2027-03-31, where it is ZERO under the Government's "
                "announcement, as stated in the v1.31 model's own `1a` note and visible in the "
                "workbook (for October-December 2026 the model's GB-average INCLUDING-VAT "
                "electricity row equals its ex-VAT row, while gas on the same row still carries "
                "5%). A caller converting the ex-VAT unit rates published here to an "
                "including-VAT figure at a flat 1.05 is wrong for those two periods. Shares are "
                "unaffected by VAT at any rate; unit rates are not."
            ),
            "meter": "single-rate electricity",
            "benchmark_consumption": {
                "it_is_not_a_constant": (
                    "THE DENOMINATOR CHANGED TWICE IN 2026 AND THE SHEET HEADER STATES ONLY THE "
                    "LATEST OF THE THREE BASES. Every period here is divided by the benchmark "
                    "consumption that applied to it, carried in `benchmark_kwh` on each period row "
                    "so no reader has to infer it. Reading the header cell instead would divide 29 "
                    "of the 33 periods by 2,500 rather than 3,100 and publish every historical unit "
                    "rate 24% high -- while every SHARE stayed exactly right, because the divisor "
                    "cancels out of a ratio. That is why this is stated beside the figures."
                ),
                "schedule_kwh_per_year": [
                    {"applies_from": starts_from or "the start of the series", "kwh": kwh}
                    for starts_from, kwh in BENCHMARK_KWH_SCHEDULE
                ],
                "provenance": {
                    "3100": (
                        "The basis of the whole pre-2026 series, and CORROBORATED rather than "
                        "asserted: the eight periods January 2024 - October 2025 that a published "
                        "cap level exists for land within 0.5% at 3,100 kWh and 24% high at 2,500."
                    ),
                    "2700": "Ofgem's benchmark-consumption decision of 21 November 2025, from P15b.",
                    "2500": (
                        "Ofgem's 'review of typical domestic consumption values' decision of "
                        "27 May 2026, from P16b."
                    ),
                    "how_the_two_2026_values_are_held": (
                        "Read from the model's own `1c Consumption adjusted levels` table, which "
                        "states them as figures against named date ranges rather than in prose, and "
                        "re-checked against that table on every run: a disagreement REFUSES to "
                        "publish rather than warning, because a fourth basis arriving unnoticed "
                        "would inflate a whole unit-rate series while every share stayed right."
                    ),
                },
            },
            "commodity_components": list(COMMODITY_COMPONENTS),
            "regional_treatment": "median across distribution regions, with the full spread beside it",
        },
        "headline": {
            "s_is_not_a_constant": True,
            "scope": f"periods with the cap actually in force, i.e. from {CAP_IN_FORCE_FROM}",
            "min_share": min(in_force),
            "max_share": max(in_force),
            "min_share_including_ofgems_illustrative_backcast": min(
                p["commodity_share_of_unit_rate"] for p in direct_debit),
            "covers": (f"{min(p['starts'] for p in direct_debit if p['cap_in_force'])} to "
                       f"{max(p['starts'] for p in direct_debit if p['cap_in_force'])}"),
            "reading": (
                "The commodity share of the electricity unit rate is ABOVE 0.40 in every period the "
                "cap has actually been in force, which is the direction the shift-response finding "
                "predicted from the denominators. It is not a scalar: it runs from roughly 0.41 in "
                "the calm periods before the gas crisis to roughly 0.81 at the January 2023 peak, "
                "so a caller citing one value must name the cap period it belongs to. THIS CLAIM IS "
                "KEYED TO A WINDOW -- see `covers` -- and the window grows with every Ofgem "
                "edition. It is re-derived from the periods actually read on every run, so a future "
                "period below 0.40 moves `min_share` here rather than leaving this sentence "
                "standing over evidence that no longer supports it."
            ),
            "the_backcast_is_not_the_law": (
                "Ofgem's model also carries pre-2019 columns it labels 'for illustration only' -- a "
                "cap level for periods in which no cap existed. Several fall BELOW 0.40. They are "
                "published here for completeness and excluded from this headline, because reading "
                "them as cap periods would make the claim above false in the flattering direction."
            ),
        },
        "cross_check_against_published_cap_levels": cross_check(direct_debit),
        "which_periods_the_cross_check_reaches": _corroboration_by_basis(direct_debit),
        "by_payment_method": by_method,
    }


def _with_carried_source_check(result: dict) -> dict:
    """The rebuilt artefact, keeping the `source_check` block the rebuild does not produce.

    WITHOUT THIS, RE-RUNNING THE DERIVATION DELETES THE SUPERSESSION BLOCK. `measure()` reads a
    workbook; it does not fetch a publisher, so it cannot honestly author a `fetched` date, a
    version token or a verdict -- and it therefore emits none. Writing its output straight over the
    artefact took the file from `superseded` to un-askable and wedged every lane on the ASKABLE leg
    of `tools/commons_source_supersession.py`. The failure arrived through the one action a diligent
    session would take, which is the worst shape a control can have.

    The block is carried VERBATIM and never edited here, because everything in it is a claim about a
    publisher that this module did not visit. The one thing a re-run does know is which workbook it
    read, so a model name that no longer matches the recorded `version_token` is stated as an
    inconsistency for the next reader rather than quietly reconciled.
    """
    if not OUT_PATH.exists():
        return result
    try:
        previous = json.loads(OUT_PATH.read_text())
    except json.JSONDecodeError:
        return result
    block = previous.get("source_check")
    if not isinstance(block, dict):
        return result
    carried = dict(result)
    carried["source_check"] = block
    token = block.get("version_token")
    if isinstance(token, str) and token and token not in result["source_model"]:
        print(
            f"NOTE: rebuilt from {result['source_model']}, while `source_check.version_token` still "
            f"records {token}. The block is carried unedited -- only a pass that actually visited "
            "the publisher may move it.",
            file=sys.stderr,
        )
    return carried


def main(argv=None) -> int:
    del argv
    try:
        result = measure()
    except CapModelUnavailable as exc:
        print(f"REFUSED: {exc}")
        return 2
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(_with_carried_source_check(result), indent=1) + "\n")
    check = result["cross_check_against_published_cap_levels"]
    print(f"model: {result['source_model']}")
    print(f"cross-check: {check['periods_checked']} periods, worst error "
          f"{check['worst_relative_error']:.3%}")
    print(f"{'cap period':32s} {'s':>7s} {'min':>7s} {'max':>7s} {'unit p/kWh':>11s} {'kWh':>6s}")
    for period in result["by_payment_method"]["direct_debit"]["periods"]:
        print(f"{period['cap_period'][:32]:32s} {period['commodity_share_of_unit_rate']:7.4f} "
              f"{period['commodity_share_min']:7.4f} {period['commodity_share_max']:7.4f} "
              f"{period['unit_rate_p_per_kwh_ex_vat']:11.2f} {period['benchmark_kwh']:6d}")
    print(f"written to {_named(OUT_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
