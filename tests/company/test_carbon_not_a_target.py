"""CARBON_NOT_A_TARGET grep-guard (CARBON_NOT_A_TARGET_CONSTRAINT.md, MAKE_IT_STICK).

£/tCO2e and every carbon metric is a DIAGNOSTIC — it may NOT feed any decision
surface (the atom draw, the risk committee, a pricing/personalisation reward
path, or a selection/fitness function). This test mechanises that: NO decision
surface may import `company.carbon`. It is the load-bearing control the
constraint exists to provide.

R15 (control must be able to FAIL): the detector is self-tested BOTH directions —
it FIRES on a synthetic carbon import and is QUIET on clean code — so a
fail-silent detector (that never fires) cannot pass this suite while the real
surfaces drift. The mutation that proves it: add `from company.carbon.
carbon_ledger import CarbonLedger` to any listed surface and this test goes red.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent.parent


def _imports_company_carbon(source: str) -> bool:
    """True iff `source` imports anything from the `company.carbon` package
    (or the bare `carbon_ledger` module). AST-based, so a comment or a string
    mentioning carbon never false-positives."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            root = node.module.split(".")
            if root[:2] == ["company", "carbon"] or root[-1] == "carbon_ledger":
                return True
        elif isinstance(node, ast.Import):
            for n in node.names:
                parts = n.name.split(".")
                if parts[:2] == ["company", "carbon"] or parts[-1] == "carbon_ledger":
                    return True
    return False


# -- R15 self-test of the detector (both directions) ------------------------

def test_detector_fires_on_a_carbon_import():
    assert _imports_company_carbon(
        "from company.carbon.carbon_ledger import CarbonLedger\nx = CarbonLedger()"
    )
    assert _imports_company_carbon("import company.carbon.carbon_ledger")


def test_detector_quiet_on_clean_code():
    assert not _imports_company_carbon(
        "# carbon is the mission but this module must not read it\n"
        "from company.pricing.cost_to_serve import cost\nx = cost()"
    )


# -- the actual guard: decision surfaces must not import carbon --------------

# The decision surfaces the constraint names (atom draw, risk committee,
# pricing/personalisation reward, selection/fitness). Globs; only existing
# files are scanned.
_SURFACE_GLOBS = (
    "background/supervisor.py",
    "sim/risk_committee.py",
    "sim/risk_committee_agent.py",
    "sim/risk_committee_rules.py",
    "company/risk/*.py",
    "company/pricing/*.py",
    "company/crm/portfolio_repricing.py",
    "company/crm/renewal_pricing_engine.py",
    "company/regulatory/supplier_fitness_register.py",
)


def _surface_files():
    files = []
    for g in _SURFACE_GLOBS:
        if "*" in g:
            files.extend(sorted(_ROOT.glob(g)))
        else:
            p = _ROOT / g
            if p.is_file():
                files.append(p)
    return files


def test_decision_surfaces_exist():
    # Guard against a silently-empty scan (fail-silent): the core surfaces must
    # resolve to real files, else the guard would vacuously "pass".
    files = _surface_files()
    assert len(files) >= 5, f"decision-surface scan resolved too few files: {files}"


@pytest.mark.parametrize("path", _surface_files(), ids=lambda p: str(p.relative_to(_ROOT)))
def test_decision_surface_does_not_import_carbon(path):
    src = path.read_text(encoding="utf-8")
    assert not _imports_company_carbon(src), (
        f"{path.relative_to(_ROOT)} imports a carbon metric -- CARBON_NOT_A_TARGET: a carbon "
        "figure may never feed a decision surface (draw / risk committee / pricing / fitness)"
    )
