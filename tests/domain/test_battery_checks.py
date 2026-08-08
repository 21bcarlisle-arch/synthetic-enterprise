"""AO8 -- the battery lines that ARE mechanised, as standing checks.

Each test here is named by exactly one register entry with
`disposition: mechanised`, and integrity fails if that pairing breaks in either
direction. Do not add a test here without registering it, and do not register a
line as mechanised without a test that can actually fail.

Two of the three are CLASS guards in this repo's established source-scan idiom
(tools/segment_case_guard.py, tools/child_stderr_guard.py): they scan the whole
tree rather than one call site, because R10 forbids closing an absurdity class
with an instance fix. A guard that only checked the modules that exist today
would stay silent on the module added tomorrow, which is the only case it is
for.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent

# 1 therm = 29.3071 kWh. Published conversion; the value the tree must agree on.
PUBLISHED_KWH_PER_THERM = 29.3071
#: Relative tolerance for a therm constant. 0.1% admits the rounded forms the
#: tree legitimately uses (29.31, 29.307) and rejects a genuine confusion --
#: 29.0, 31.0, or a 100-kBTU mix-up -- which is the defect the battery names.
THERM_TOLERANCE = 0.001

_SCANNED_ROOTS = ("sim", "company", "saas", "simulation", "interface", "tools")

#: Numbers that are a therm conversion wherever they appear. Matched on the
#: literal so a NEW module introducing its own constant is caught, not just the
#: ones known at authoring time.
_THERM_LITERAL = re.compile(r"\b(2[0-9]\.\d+|3[0-9]\.\d+|0\.0\d{3,})\b")
#: `therm`/`therms` only where the word ENDS -- a bare `therm` substring also
#: occurs inside `thermal`, `thermostat`, `thermal_lag_hours`, and matching
#: those made the first version of this guard fire on a daylight calculation.
#: A guard that cries wolf gets deleted, so the boundary is load-bearing.
_THERM_CONTEXT = re.compile(r"therms?(?![a-zA-Z])", re.IGNORECASE)
#: A conversion line names BOTH units. Without this, any numeric threshold that
#: happens to sit on a therm-bearing line (`price_pence_per_therm < 30.0`) reads
#: as a mis-stated conversion. Requiring the pair keeps the guard on conversions.
_ENERGY_UNIT = re.compile(r"[kmg]wh", re.IGNORECASE)


def _python_files() -> list[Path]:
    out: list[Path] = []
    for root in _SCANNED_ROOTS:
        base = ROOT / root
        if not base.is_dir():
            continue
        out.extend(p for p in base.rglob("*.py") if "__pycache__" not in p.parts)
    return out


def test_the_therm_scan_reaches_a_known_site() -> None:
    """Vacuity guard for the GAS-8 scan.

    Without this, a scan that silently matched nothing would report "all therm
    constants agree" over an empty set -- the population-control fail-open
    (1557/1557 passed while the field was absent). Asserting the scan finds a
    site we know exists makes the coverage claim falsifiable.
    """
    files = _python_files()
    assert len(files) > 100, f"source scan collapsed to {len(files)} files"
    hits = [p for p in files if _THERM_CONTEXT.search(p.read_text(encoding="utf-8", errors="ignore"))]
    assert hits, "therm scan found no therm-bearing module at all -- scan is broken"
    names = {p.name for p in hits}
    assert "gas_nominations.py" in names, (
        "the scan no longer reaches company/market/gas_nominations.py, a module "
        f"known to define a therm constant; reached: {sorted(names)}"
    )


def _therm_constants() -> list[tuple[Path, int, float]]:
    """Every numeric literal on a therm-mentioning line, with its location."""
    found: list[tuple[Path, int, float]] = []
    for path in _python_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if not _THERM_CONTEXT.search(text):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if not (_THERM_CONTEXT.search(line) and _ENERGY_UNIT.search(line)):
                continue
            for raw in _THERM_LITERAL.findall(line):
                value = float(raw)
                # Constants appear either as kWh-per-therm (~29.3) or as its
                # reciprocal scaled to MWh (~0.02931). Normalise both to
                # kWh-per-therm so one comparison covers both spellings.
                if 0.02 < value < 0.05:
                    value = value * 1000.0
                elif not (20.0 < value < 40.0):
                    continue
                found.append((path, lineno, value))
    return found


def test_gas_8_therm_conversion_is_single_and_published() -> None:
    """GAS-8: "Therms and kilowatt-hours confused, or the conversion assumed."

    The battery's objection is to an ASSUMED conversion. The tree currently
    spells the constant five ways across five modules (29.3071, 29.307, 29.31,
    29.3, 0.02931). All five agree to within 0.03%, so nothing is materially
    wrong today -- but nothing stops the sixth from being wrong, and that is
    precisely the confusion the advisor is warning about. This pins every
    spelling to the published value.
    """
    constants = _therm_constants()
    assert constants, "no therm constants found -- the scan cannot be vacuous"
    wrong = [
        (str(p.relative_to(ROOT)), lineno, value)
        for p, lineno, value in constants
        if abs(value - PUBLISHED_KWH_PER_THERM) / PUBLISHED_KWH_PER_THERM > THERM_TOLERANCE
    ]
    assert not wrong, (
        "therm conversion disagrees with the published 29.3071 kWh/therm at "
        f"{wrong}. A therm constant is a shared primitive: fix the site, or if "
        "the literal is not a conversion, move it off the therm-bearing line."
    )


# --------------------------------------------------------------------------
# NCS-B3 -- fuel purity of the levy stack
# --------------------------------------------------------------------------

#: Levies that may only ever reach an ELECTRICITY bill.
ELECTRICITY_ONLY_LEVIES = frozenset({
    "get_ro_cost_per_mwh",
    "get_cfd_levy_per_mwh",
    "get_cm_levy_per_mwh",
    "get_fit_levy_per_mwh",
    "get_electricity_policy_cost_per_mwh",
    "get_electricity_network_cost_per_mwh",
})
#: Levies that may only ever reach a GAS bill.
GAS_ONLY_LEVIES = frozenset({
    "get_ggl_per_mwh",
    "get_gas_ccl_per_mwh",
    "get_gas_network_cost_per_mwh",
})

#: Modules that assemble a single-fuel cost stack. A dual-fuel assembler
#: legitimately touches both sets and is not listed.
_GAS_STACK_MODULES = ("simulation/gas_settlement.py",)
_ELEC_STACK_MODULES = ("simulation/hedged_settlement.py",)


def _called_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                names.add(func.id)
            elif isinstance(func, ast.Attribute):
                names.add(func.attr)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                names.add(alias.name)
    return names


@pytest.mark.parametrize("relpath", _GAS_STACK_MODULES + _ELEC_STACK_MODULES)
def test_ncs_b3_the_fuel_purity_scan_reaches_its_targets(relpath: str) -> None:
    """Fail-closed coverage guard: a renamed/moved stack module must FAIL.

    If the assembler moves and this file keeps pointing at the old path, the
    purity test below would pass over a file that no longer exists -- covered
    on paper, checking nothing.
    """
    path = ROOT / relpath
    assert path.is_file(), (
        f"declared cost-stack module {relpath} is gone. Fuel purity is now "
        "unchecked for that fuel: repoint this list, do not delete the entry."
    )
    assert _called_names(path), f"{relpath} parsed to zero calls -- scan is broken"


def test_ncs_b3_fuel_purity_of_the_levy_stack() -> None:
    """NCS-B3: "a gas bill carrying RO, CfD, CM, or AAHEDC is disqualified; an
    electricity bill carrying GGL likewise."

    Checked structurally at the assembler rather than on a sampled bill,
    because a sampled bill only proves the sample. If a gas cost stack cannot
    even reference an electricity-only levy, no gas bill can carry one.
    """
    violations: list[str] = []
    for relpath in _GAS_STACK_MODULES:
        used = _called_names(ROOT / relpath) & ELECTRICITY_ONLY_LEVIES
        if used:
            violations.append(f"{relpath} (gas stack) reaches electricity levies {sorted(used)}")
    for relpath in _ELEC_STACK_MODULES:
        used = _called_names(ROOT / relpath) & GAS_ONLY_LEVIES
        if used:
            violations.append(f"{relpath} (electricity stack) reaches gas levies {sorted(used)}")
    assert not violations, "fuel purity breached: " + "; ".join(violations)


# --------------------------------------------------------------------------
# ELEC-4 -- negative prices
# --------------------------------------------------------------------------


#: A price this far below zero cannot plausibly be an ordinary lower-mode draw
#: (it is ~4 sigma below `lower_mode_mean`), so a price beyond it is evidence of
#: the negative-price REGIME rather than of a gaussian tail. The control arm
#: below asserts that premise instead of assuming it.
NEGATIVE_REGIME_DEPTH_GBP_PER_MWH = -20.0


def _prices(records) -> list[float]:
    out = [_price_of(r) for r in records]
    return [p for p in out if p is not None]


def test_elec_4_negative_prices_are_reachable() -> None:
    """ELEC-4: "No negative prices."

    DIFFERENTIAL, not merely behavioural. The first version of this test just
    asserted "some price is below zero" -- and it PASSED with the generator's
    negative-price overlay disabled, because `lower_mode_mean=50, std=18`
    throws the occasional sub-zero draw on its own. A control that stays green
    when the mechanism it names is removed is exactly the R15 "cannot fail"
    shape, so it is written as a comparison instead:

      control arm   negative_days_per_year=0  -> the regime is off
      treatment arm negative_days_per_year=30 -> the regime is on

    Same seed, same everything else. The claim is that the MECHANISM produces
    the negatives, which is what the battery line is actually about.
    """
    from sim.scenario.bimodal_generator import ScenarioParams, generate_scenario_prices

    seed = "battery-elec-4"
    control = ScenarioParams(negative_days_per_year=0.0)
    treatment = ScenarioParams(
        negative_days_per_year=30.0, negative_price_mean=-30.0, negative_price_std=15.0
    )

    control_prices = _prices(generate_scenario_prices(2026, 2028, scenario=control, seed=seed))
    treatment_prices = _prices(generate_scenario_prices(2026, 2028, scenario=treatment, seed=seed))
    assert control_prices and treatment_prices, "scenario generator produced no prices"

    deep = NEGATIVE_REGIME_DEPTH_GBP_PER_MWH
    control_deep = [p for p in control_prices if p < deep]
    treatment_deep = [p for p in treatment_prices if p < deep]

    # The fixture asserts its own premise: if the ordinary distribution widened
    # far enough to reach the depth threshold by chance, this test would be
    # measuring noise, and it says so rather than quietly passing.
    assert not control_deep, (
        f"premise broken: with the negative-price regime OFF, {len(control_deep)} prices "
        f"still fall below {deep} GBP/MWh. The depth threshold no longer separates the "
        "regime from the ordinary lower mode, so this test would be measuring noise."
    )
    assert treatment_deep, (
        "the price generator cannot produce a negative price from its negative-price "
        "regime. GB power prices go negative regularly and increasingly; a model that "
        "cannot reach that state is missing a real regime (ELEC-4)."
    )


def _price_of(record) -> float | None:
    if isinstance(record, dict):
        for key in ("systemSellPrice", "price", "price_gbp_per_mwh", "value"):
            if key in record:
                return float(record[key])
        return None
    for key in ("price", "price_gbp_per_mwh", "value"):
        if hasattr(record, key):
            return float(getattr(record, key))
    return None
