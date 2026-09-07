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
   the published INCLUDING-VAT levels: the check is that derived x 1.05 reproduces them. That check
   is the reason to believe the decomposition at all, so it FAILS CLOSED rather than warning.

ALL THREE PAYMENT METHODS ARE MEASURED, not just direct debit. Publishing one share over a
population that is really three is this project's most expensive recurring shape; the three differ
and the artefact carries all of them.
"""

from __future__ import annotations

import json
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

#: Ofgem's benchmark annual consumption for the single-rate electricity meter, in kWh. It is the
#: denominator of the model's own per-kWh conversion and is named in the sheet title, so it is read
#: back from the sheet rather than trusted from here — this is the expected value, not the source.
BENCHMARK_KWH = 3100

#: VAT on domestic energy, as a multiplier. NOT a choice: the cap model's component build-up is
#: ex-VAT and the published cap levels are inclusive, so this is the conversion between two
#: published quantities and it is what the cross-check applies.
VAT_MULTIPLIER = 1.05

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
        benchmark_sheet = f"ElecSingle_{suffix}_{BENCHMARK_KWH}kWh"
        nil_sheet = f"ElecSingle_{suffix}_Nil"
        missing = [name for name in (benchmark_sheet, nil_sheet) if name not in workbook.sheetnames]
        if missing:
            raise CapModelUnavailable(
                f"{model_path.name} has no sheet(s) {missing}; it is not a cap level model of the "
                "shape this reader was written against"
            )
        head_full, body_full = _sheet_rows(workbook[benchmark_sheet])
        head_nil, body_nil = _sheet_rows(workbook[nil_sheet])
    finally:
        workbook.close()

    regions = sorted({region for region, _ in body_full if region})
    periods = []
    for label in sorted(set(head_full) & set(head_nil), key=lambda k: head_full[k]):
        column_full, column_nil = head_full[label], head_nil[label]
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
            unit_rate = (full_year - nil_year) / BENCHMARK_KWH * 100.0
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
            shares.append(commodity / BENCHMARK_KWH * 100.0 / unit_rate)
            unit_rates.append(unit_rate)
            standing.append(nil_year / 365.0 * 100.0)
        if not shares:
            continue
        starts = _period_start(label)
        periods.append({
            "cap_period": label,
            "starts": starts,
            "cap_in_force": bool(starts and starts >= CAP_IN_FORCE_FROM),
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
    return {"payment_method": payment_method, "periods": periods}


def _published_levels() -> list[dict]:
    if not CAP_WINDOWS.exists():
        raise CapModelUnavailable(
            f"{_named(CAP_WINDOWS)} is absent, so the derived unit rate cannot be "
            "checked against the published one. The decomposition is not published unchecked."
        )
    return json.loads(CAP_WINDOWS.read_text()).get("windows", [])


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
        derived = period["unit_rate_p_per_kwh_ex_vat"] * VAT_MULTIPLIER * 10.0
        error = abs(derived - window["elec"]) / window["elec"]
        checked += 1
        worst = max(worst, error)
        rows.append({"cap_period": period["cap_period"], "derived_gbp_per_mwh": round(derived, 2),
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
            "vat": "components are EX-VAT; shares are unaffected by a uniform rate, unit rates are",
            "meter": f"single-rate electricity, benchmark {BENCHMARK_KWH} kWh/year",
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
            "reading": (
                "The commodity share of the electricity unit rate is ABOVE 0.40 in every period the "
                "cap has actually been in force, which is the direction the shift-response finding "
                "predicted from the denominators. It is not a scalar: it runs from roughly 0.41 in "
                "the calm periods before the gas crisis to roughly 0.81 at the January 2023 peak, "
                "so a caller citing one value must name the cap period it belongs to."
            ),
            "the_backcast_is_not_the_law": (
                "Ofgem's model also carries pre-2019 columns it labels 'for illustration only' -- a "
                "cap level for periods in which no cap existed. Several fall BELOW 0.40. They are "
                "published here for completeness and excluded from this headline, because reading "
                "them as cap periods would make the claim above false in the flattering direction."
            ),
        },
        "cross_check_against_published_cap_levels": cross_check(direct_debit),
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
    print(f"{'cap period':32s} {'s':>7s} {'min':>7s} {'max':>7s} {'unit p/kWh':>11s}")
    for period in result["by_payment_method"]["direct_debit"]["periods"]:
        print(f"{period['cap_period'][:32]:32s} {period['commodity_share_of_unit_rate']:7.4f} "
              f"{period['commodity_share_min']:7.4f} {period['commodity_share_max']:7.4f} "
              f"{period['unit_rate_p_per_kwh_ex_vat']:11.2f}")
    print(f"written to {_named(OUT_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
