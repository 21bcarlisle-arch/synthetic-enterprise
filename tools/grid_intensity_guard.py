"""R10 class closure: exactly ONE annual UK grid-intensity series may exist under company/ + saas/.

WHY THIS EXISTS (2026-08-14, discharging
`docs/staging/WORKER_FINDING_THREE_LIVE_GRID_INTENSITY_SERIES_DISAGREE_BY_HALF_2026-08-14.md`,
BLOCKING, lane `F_risk_compliance`).

Three series in this tree claimed to measure the same quantity from the same cited source and
disagreed by up to 55.6%:

    year   published (annual report)   carbon_footprint   carbon_intensity_register
    2024   196.1                       126                181.0

At most one could be right, the published one was not obviously it, and the spread WIDENED over
time (19.6% in 2019 -> 55.6% in 2024), so it was not a transcription slip. Two of the three had no
renderer at all; nothing in the tree could observe that they disagreed.

R10 forbids closing an absurdity-class defect with an instance fix. Deleting two tables closes the
instance. THIS closes the class: a second annual grid-intensity or fuel-mix series appearing
anywhere under `company/` or `saas/` is a hard failure, wherever it is declared and whatever it is
called.

THREE ARMS, because each historical instance would have escaped the other two:

* ARM 1 -- NAME-KEYED. A year-keyed dict of numbers bound to a carbon-ish name. Catches
  `_ELECTRICITY_INTENSITY_G_CO2E_PER_KWH` and `_GRID_AVERAGE_INTENSITY`, the two deleted literals.
* ARM 2 -- SHAPE-KEYED, name-independent. A year-keyed dict whose values CONSTRUCT fuel-mix
  records. Catches the third one, `_UK_FUEL_MIX`, which arm 1 misses twice over: it was declared
  as a LOCAL INSIDE A FUNCTION BODY (`_section_carbon_emissions`), and its values are calls rather
  than numbers.
* ARM 3 -- NESTED-DICT. A year-keyed dict whose values are dicts of numbers. Added in the same
  pass that wrote arms 1 and 2, because measuring the residue immediately found a FOURTH published
  table the first two both missed: `company/billing/fuel_mix.py::_FUEL_MIX_BY_YEAR`, whose values
  are `{"renewable": ..., "gas": ...}` literals. It renders the annual report's OTHER fuel-mix
  section, and the two published sections disagree — see the ratchet below.

All three walk the whole AST, not module scope: a function body is where the published copy hid.

FAIL-CLOSED ON ITS OWN SUBJECT (R15 killer patterns 2 and 3, FAIL-OPEN and FAIL-SILENT). The guard
exits rc=2, not rc=0, when it cannot see the thing it is guarding: if the owner module is missing
from the declared path, or no longer declares the canonical series, or the scanned packages are
absent. A guard that reports "no second series" because the FIRST one vanished has not passed --
it has lost its subject, which is the wrong-subject failure this project has filed repeatedly.

WHY `sim/` AND `simulation/` ARE NOT SCANNED, and it is not convenience. Those carry generation
emission factors as WORLD PHYSICS (`sim/merit_order_reconstruction.py::EF_GAS_TCO2_PER_MWH_E_BY_YEAR`,
tCO2 per MWh thermal). They are a different quantity on the far side of the epistemic wall, and the
company may not read them. Folding them into a company-side owner would be a wall breach, not a
reconciliation.

WHAT THIS GUARD DOES NOT CLOSE, stated so its silence is not read as coverage. The PER-FUEL factor
tables are a separate and larger class -- three of them survive
(`carbon_emissions._EMISSION_FACTORS_G_CO2_PER_KWH`,
`carbon_intensity_register._CARBON_INTENSITY_G_CO2_PER_KWH`,
`fuel_mix_disclosure._CARBON_INTENSITY`), disagreeing on gas by 394.0 vs 490.0, and so are the
single-scalar gas and flat-grid factors (0.18316 / 0.18253 / 0.183, and 0.2104 / 0.207). Those are
filed as their own finding; this guard's subject is the ANNUAL SERIES only.

CLI: `python3 -m tools.grid_intensity_guard` -- rc 0 clean, rc 1 violations, rc 2 coverage hole.
"""

from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

ROOT = Path(__file__).resolve().parent.parent

#: The one module allowed to declare the series. Relative to the repo root.
OWNER_REL_PATH = "company/regulatory/carbon_emissions.py"

#: The names the owner must still declare. If either goes missing the guard has lost its subject.
OWNER_REQUIRED_NAMES = ("UK_GRID_FUEL_MIX", "grid_intensity_g_co2e_per_kwh")

#: Packages searched for a second copy. See the docstring for why sim/ and simulation/ are out.
SCANNED_PACKAGES = ("company", "saas")

#: A key is a "year" if it is a bare int in this window. Wide on purpose: a table starting at 1990
#: or running to 2050 is the same defect as one covering 2016-2025.
YEAR_MIN = 1990
YEAR_MAX = 2100

#: Three years is the smallest thing that is recognisably a SERIES rather than a pair of constants.
MIN_YEARS = 3

#: Arm 1's name filter. A grid-intensity table has to be called something for a reader to find it.
CARBONISH_NAME = re.compile(r"CARBON|CO2|CO₂|EMISSION|INTENSITY|FUEL_?MIX|GRID", re.IGNORECASE)

#: Arm 2's shape filter: a call to anything whose name ends in these constructs a mix record.
MIX_RECORD_CALLS = ("FuelMixRecord", "FuelMixSnapshot")

#: THE RATCHET. One instance survives this pass, and it is named rather than excluded by a
#: convenient predicate. It may only SHRINK: `scan_tree` reports a ratcheted violation as
#: `known=True` instead of failing, and `test_the_ratchet_has_no_stale_entries` fails if an entry
#: stops violating — so removing the instance FORCES removing the entry, and nothing can be added
#: here without editing this file in a reviewed commit. A guard whose exemption list can grow
#: silently is the R15 fail-open shape; this one cannot.
#:
#: WHY THIS ONE IS NOT FIXED IN THE SAME PASS. Reconciling it means choosing which of two
#: PUBLISHED tables is the source, and they disagree: the annual report's two sections each
#: publish a `Low Carbon %` column for the same years, differing by up to 3.4pp (2023: 59% in the
#: Carbon Emissions Reporting Observatory, 62.4% in the UK Grid Fuel Mix Disclosure), with the
#: sign of the difference flipping across the decade. Picking a winner without a fetched source
#: would revalue a published table on the guesser's authority — the exact move the finding that
#: created this guard refused to make. It is filed as its own finding and is EP13's to source.
KNOWN_SECOND_SERIES = {
    "company/billing/fuel_mix.py::_FUEL_MIX_BY_YEAR":
        "the annual report's OTHER published fuel-mix table (UK Grid Fuel Mix Disclosure "
        "section, 5 buckets). Reconciling it against UK_GRID_FUEL_MIX (8 buckets) revalues one "
        "of two published sections and needs a sourced answer -- WORKER_FINDING_TWO_PUBLISHED_"
        "FUEL_MIX_TABLES_DISAGREE_ON_LOW_CARBON_2026-08-14.md",
}


class CoverageError(RuntimeError):
    """The guard cannot see its own subject -- an rc=2 condition, never a pass."""


@dataclass(frozen=True)
class Violation:
    path: str
    line: int
    name: str
    arm: str
    detail: str

    @property
    def key(self) -> str:
        """The ratchet key. Path + name, never the LINE — a ratchet keyed on a line number
        expires the first time anything above it is edited, and expiring silently is the point
        of failure this project has filed against pinned controls repeatedly."""
        return f"{self.path}::{self.name}"

    @property
    def known(self) -> bool:
        return self.key in KNOWN_SECOND_SERIES

    def render(self) -> str:
        return (
            f"{self.path}:{self.line}: {self.arm} -- `{self.name}` {self.detail}. "
            f"The single owner is {OWNER_REL_PATH}; call "
            f"`grid_intensity_g_co2e_per_kwh(year)` instead of declaring a second series."
        )


def _numeric_constant(node: ast.AST) -> bool:
    """True for `196.0`, `196` and `-196.0`; False for strings, names and expressions."""
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        node = node.operand
    return isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool)


def _year_keys(node: ast.Dict) -> int:
    """Count keys that are bare int years. `None` keys (a `**spread`) are not years."""
    count = 0
    for key in node.keys:
        if isinstance(key, ast.Constant) and isinstance(key.value, int) and not isinstance(key.value, bool):
            if YEAR_MIN <= key.value <= YEAR_MAX:
                count += 1
    return count


def _is_numeric_dict(node: ast.AST) -> bool:
    """True for `{"renewable": 24.6, "gas": 42.6}` — arm 3's per-bucket inner table."""
    return (
        isinstance(node, ast.Dict)
        and bool(node.values)
        and all(_numeric_constant(v) for v in node.values)
    )


def _is_mix_record_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
    return name in MIX_RECORD_CALLS


def _assigned_names(node: ast.AST) -> List[str]:
    """The names an Assign/AnnAssign binds. Tuple targets are unpacked, not skipped."""
    names: List[str] = []
    targets: Sequence[ast.AST]
    if isinstance(node, ast.Assign):
        targets = node.targets
    elif isinstance(node, ast.AnnAssign):
        targets = [node.target]
    else:
        return names
    for target in targets:
        for sub in ast.walk(target):
            if isinstance(sub, ast.Name):
                names.append(sub.id)
            elif isinstance(sub, ast.Attribute):
                names.append(sub.attr)
    return names


def scan_source(source: str, rel_path: str) -> List[Violation]:
    """Both arms over one module's AST. Walks function bodies too -- that is where one hid."""
    violations: List[Violation] = []
    tree = ast.parse(source, filename=rel_path)
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        value = node.value
        if not isinstance(value, ast.Dict):
            continue
        years = _year_keys(value)
        if years < MIN_YEARS:
            continue
        names = _assigned_names(node)
        label = names[0] if names else "<unnamed>"

        if value.values and all(_numeric_constant(v) for v in value.values):
            if any(CARBONISH_NAME.search(n) for n in names):
                violations.append(Violation(
                    path=rel_path, line=node.lineno, name=label, arm="ARM 1 (name-keyed)",
                    detail=f"binds a {years}-year table of numbers under a carbon/intensity name",
                ))
                continue

        if value.values and all(_is_mix_record_call(v) for v in value.values):
            violations.append(Violation(
                path=rel_path, line=node.lineno, name=label, arm="ARM 2 (shape-keyed)",
                detail=f"binds a {years}-year table of fuel-mix records",
            ))
            continue

        if value.values and all(_is_numeric_dict(v) for v in value.values):
            if any(CARBONISH_NAME.search(n) for n in names):
                violations.append(Violation(
                    path=rel_path, line=node.lineno, name=label, arm="ARM 3 (nested-dict)",
                    detail=f"binds a {years}-year table of per-bucket numbers under a "
                           f"carbon/fuel-mix name",
                ))
    return violations


def _python_files(root: Path, packages: Iterable[str]) -> List[Path]:
    files: List[Path] = []
    for package in packages:
        base = root / package
        if not base.is_dir():
            raise CoverageError(
                f"scanned package `{package}/` does not exist under {root} -- the guard would "
                f"pass by scanning nothing"
            )
        files.extend(
            p for p in sorted(base.rglob("*.py"))
            if "__pycache__" not in p.parts
        )
    if not files:
        raise CoverageError(f"no python files found under {list(packages)} in {root}")
    return files


def _check_owner(root: Path, owner_rel: str) -> None:
    owner = root / owner_rel
    if not owner.is_file():
        raise CoverageError(
            f"owner module {owner_rel} is missing -- the series has no declared home, so "
            f"'no second series' means nothing"
        )
    source = owner.read_text(encoding="utf-8")
    missing = [n for n in OWNER_REQUIRED_NAMES if not re.search(rf"\b{re.escape(n)}\b", source)]
    if missing:
        raise CoverageError(
            f"owner module {owner_rel} no longer declares {missing} -- the canonical series moved "
            f"or was deleted without moving this guard's OWNER_REL_PATH with it"
        )


def scan_tree(
    root: Path = ROOT,
    packages: Iterable[str] = SCANNED_PACKAGES,
    owner_rel: str = OWNER_REL_PATH,
    include_known: bool = False,
) -> List[Violation]:
    """Second annual grid-intensity series under `packages`. Raises CoverageError on rc=2.

    `include_known=False` (the default, and what the gate runs) drops the ratcheted instances in
    `KNOWN_SECOND_SERIES`. `include_known=True` returns everything, which is how the ratchet's own
    staleness test can tell that an entry has stopped violating and must be deleted.
    """
    packages = tuple(packages)
    _check_owner(root, owner_rel)
    owner_abs = (root / owner_rel).resolve()
    violations: List[Violation] = []
    for path in _python_files(root, packages):
        if path.resolve() == owner_abs:
            continue
        rel = path.relative_to(root).as_posix()
        try:
            violations.extend(scan_source(path.read_text(encoding="utf-8"), rel))
        except SyntaxError as exc:
            raise CoverageError(f"{rel} does not parse ({exc}) -- the guard cannot read it") from exc
    if include_known:
        return violations
    return [v for v in violations if not v.known]


def main(argv: Sequence[str] | None = None) -> int:
    try:
        # ROOT explicitly, not the default argument: a default is bound at def time, so a test
        # that repoints ROOT would silently keep scanning the real tree and pass for free.
        violations = scan_tree(root=ROOT)
    except CoverageError as exc:
        print(f"GRID-INTENSITY GUARD COVERAGE HOLE: {exc}", file=sys.stderr)
        return 2
    if violations:
        print(
            f"GRID-INTENSITY GUARD: {len(violations)} second series under "
            f"{'/, '.join(SCANNED_PACKAGES)}/ (R10 class closure)",
            file=sys.stderr,
        )
        for violation in violations:
            print("  " + violation.render(), file=sys.stderr)
        return 1
    print(
        f"GRID-INTENSITY GUARD: clean -- one series, owned by {OWNER_REL_PATH}"
        + (f" (+{len(KNOWN_SECOND_SERIES)} ratcheted, see KNOWN_SECOND_SERIES)"
           if KNOWN_SECOND_SERIES else "")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
