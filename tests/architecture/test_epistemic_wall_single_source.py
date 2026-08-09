"""R15 control for the KNIFE-pass-3 extraction: ONE definition of "a crossing".

WHAT THIS GUARDS, AND WHY IT IS NOT THE RATCHET
-----------------------------------------------
`test_epistemic_wall_ratchet.py` guards the WALL: no new crossing, allowlist only shrinks.
This module guards the DEFINITION of a crossing — that the three instruments which answer
"is this import a wall crossing?" answer it from `tools/epistemic_wall.py` and not
from private copies:

  * the ratchet (`tests/architecture/test_epistemic_wall_ratchet.py`) — the gate,
  * the KNIFE ledger (`tools/knife_hotspot_measure.py`) — the report,
  * the phase-close scanner (`tools/epistemic_verifier.py`) — the wider, dynamic-import reach.

The defect class is real and this repo has paid for it twice, both found by KNIFE passes and
both recorded in `docs/design/KNIFE_HOTSPOT_PASSES.md`: the scanner's `APPROVED_ORCHESTRATION`
outlived the two crossings it exempted (a dead exemption is a pre-authorised re-entry), and its
seam was a FILE while the ratchet's seam was the PACKAGE — so it passed the seam module pass 2
built for a reason other than the one it stated. Three registers of one concept drift silently;
the drift, not either register, was the defect.

R15 — THE THREE KILLER PATTERNS, ANSWERED
------------------------------------------
TAUTOLOGY   — the single-source tests assert OBJECT IDENTITY (`is`) between each consumer's names
              and the shared module's, not equality of two independently-computed values. Two
              copies of the same walker would compare EQUAL on today's tree and are exactly what
              must fail; only identity distinguishes them.
FAIL-OPEN   — the perimeter mutations move the shared definition and assert every consumer MOVES
              WITH IT. A consumer holding a private copy would keep its old answer and red.
              Each mutation carries a vacuity assertion on the un-mutated tree first, so a test
              that passed because it measured nothing would be caught.
FAIL-SILENT — a consumer that cannot be imported is a FAILED test here, never a skip.
"""

from __future__ import annotations

import ast
import os
import sys

import pytest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import tests.architecture.test_epistemic_wall_ratchet as ratchet  # noqa: E402
import tools.epistemic_verifier as verifier  # noqa: E402
import tools.epistemic_wall as shared  # noqa: E402
import tools.knife_hotspot_measure as ledger  # noqa: E402

# The names the atom named: the walk, and the two classifiers.
EXTRACTED = ("build_edges", "company_reads_sim", "sim_reads_company")


# --------------------------------------------------------------------------
# Single source — by identity, not by equality.
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", EXTRACTED)
def test_the_ratchet_uses_the_shared_definition_object_itself(name):
    """Not "computes the same answer" — IS the same function. Two identical copies of
    the walker would satisfy an equality check and are precisely the defect."""
    assert getattr(ratchet, name) is getattr(shared, name), (
        f"{name} in the ratchet is not the shared object — a private copy has reappeared"
    )


def test_the_ratchet_uses_the_shared_perimeter():
    for const in ("REPO_ROOT", "WALL_DIRS", "SEAM_PACKAGE", "SIM_PACKAGES", "COMPANY_PACKAGES"):
        assert getattr(ratchet, const) == getattr(shared, const), f"perimeter drift on {const}"
    assert ratchet.RawEdge is shared.RawEdge


def test_the_ledger_reads_the_shared_definition_not_the_test_module():
    """The ledger used to import the walker OUT of the ratchet test module. It now imports
    the shared one; naming the test module here would resurrect the coupling the extraction
    removed."""
    src = open(os.path.join(REPO, "tools", "knife_hotspot_measure.py"), encoding="utf-8").read()
    fn = src[src.index("def _wall_edges"):src.index("def _py_files")]
    assert "from tools.epistemic_wall import" in fn
    assert "test_epistemic_wall_ratchet" not in fn


def test_the_verifier_reads_the_shared_perimeter():
    assert verifier.SIM_PACKAGES is shared.SIM_PACKAGES
    assert verifier.COMPANY_PACKAGES is shared.COMPANY_PACKAGES
    assert verifier.is_sim_module is shared.is_sim_module
    # Its regex list and exemption set are DERIVED, so they cannot drift silently.
    for pkg in shared.SIM_PACKAGES:
        assert any(pkg in p for p in verifier.FORBIDDEN_SOURCES), f"{pkg} unguarded by the regexes"
        assert f"{pkg}/" in verifier.EXEMPT_PATHS
    assert shared.SEAM_PATH_PREFIX in verifier.EXEMPT_PATHS


def test_no_second_walker_is_defined_anywhere():
    """The extraction is worthless if a fourth reader writes its own AST census. Any module
    under tools/ or tests/architecture/ DEFINING one of the extracted names — other than the
    shared module — is a second definition, whatever it is called."""
    offenders = []
    for base in ("tools", os.path.join("tests", "architecture")):
        for dirpath, _dn, fns in os.walk(os.path.join(REPO, base)):
            for fn in fns:
                if not fn.endswith(".py"):
                    continue
                path = os.path.join(dirpath, fn)
                if os.path.samefile(path, shared.__file__):
                    continue
                try:
                    tree = ast.parse(open(path, encoding="utf-8").read(), filename=path)
                except (SyntaxError, UnicodeDecodeError):
                    continue
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name in EXTRACTED:
                        offenders.append(f"{os.path.relpath(path, REPO)}:{node.lineno} {node.name}")
    assert not offenders, (
        "a SECOND definition of the crossing walker/classifiers exists:\n  "
        + "\n  ".join(offenders)
        + "\nImport tools/epistemic_wall.py instead."
    )


# --------------------------------------------------------------------------
# R15 mutation — move the definition, and every consumer must move with it.
# --------------------------------------------------------------------------

def test_mutation_widening_the_sim_perimeter_moves_every_consumer(monkeypatch):
    """Add a package to the SIM side of the wall and assert the ratchet's classifier AND the
    verifier's forbidden test both start seeing it. A consumer with a private copy would not."""
    probe = shared.RawEdge(src="saas.rogue", dst="fictional_sim_pkg.engine", path="x.py", lineno=1)

    # VACUITY GUARD: on the real perimeter this is not a crossing and not forbidden.
    assert ("saas.rogue", "fictional_sim_pkg.engine") not in ratchet.company_reads_sim([probe])
    assert not verifier._module_is_forbidden("fictional_sim_pkg.engine")

    monkeypatch.setattr(shared, "SIM_PACKAGES", shared.SIM_PACKAGES | {"fictional_sim_pkg"})

    assert ("saas.rogue", "fictional_sim_pkg.engine") in ratchet.company_reads_sim([probe]), (
        "the ratchet's classifier did not follow the shared perimeter"
    )
    assert verifier._module_is_forbidden("fictional_sim_pkg.engine"), (
        "the verifier did not follow the shared perimeter"
    )


def test_mutation_moving_the_seam_moves_the_classification(monkeypatch):
    """Repoint the seam and assert exemption follows it in BOTH directions. The seam is the
    single most load-bearing constant here: a stale copy would exempt the wrong package."""
    a = shared.RawEdge(src="company.interfaces.supply_book", dst="sim.forward_curve", path="x", lineno=1)
    b = shared.RawEdge(src="simulation.run_phase2b", dst="company.interfaces.supply_book", path="y", lineno=1)

    # VACUITY GUARD: with the real seam, both are exempt (they ARE the seam).
    assert not ratchet.company_reads_sim([a])
    assert not ratchet.sim_reads_company([b])

    monkeypatch.setattr(shared, "SEAM_PACKAGE", "company.elsewhere")

    assert ("company.interfaces.supply_book", "sim.forward_curve") in ratchet.company_reads_sim([a]), (
        "class (a) exemption did not follow the shared seam"
    )
    assert ("simulation.run_phase2b", "company.interfaces.supply_book") in ratchet.sim_reads_company([b]), (
        "class (b) exemption did not follow the shared seam"
    )


def test_mutation_ledger_probe_follows_the_shared_walker(monkeypatch):
    """The ledger's crossing population is the shared classifiers' output, not a re-walk."""
    real = ledger.probe_wall_crossings()
    assert real.edges, "vacuity: the ledger measured no crossings at all"

    monkeypatch.setattr(shared, "sim_reads_company", lambda edges: {})
    monkeypatch.setattr(shared, "company_reads_sim", lambda edges: {})
    assert ledger.probe_wall_crossings().edges == frozenset(), (
        "the ledger's population survived neutering the shared classifiers — it walks its own"
    )


# --------------------------------------------------------------------------
# The deleted exemptions must stay deleted, and must now FIRE.
# --------------------------------------------------------------------------

def test_the_stale_orchestration_carve_out_is_gone():
    """`WORKER_FINDING_STALE_ORCHESTRATION_CARVE_OUT_2026-08-09.md`. Absence of the name is the
    weak half; the strong half is the next test, which proves the import is now caught."""
    assert not hasattr(verifier, "APPROVED_ORCHESTRATION")
    assert not hasattr(verifier, "APPROVED_SEAM")
    src = open(verifier.__file__, encoding="utf-8").read()
    # The two formerly-exempt names may appear only inside the comment that records the deletion.
    for name in ("simulation.run_phase4c_on_phase2b", "simulation.run_segments"):
        for line in src.splitlines():
            if name in line:
                assert line.lstrip().startswith("#"), f"{name} is live again at: {line.strip()}"


@pytest.mark.parametrize("module", ["simulation.run_phase4c_on_phase2b", "simulation.run_segments"])
def test_the_formerly_exempt_orchestration_imports_now_fire(tmp_path, module):
    """The finding's own scenario: if either import came back in company-side code, the scanner
    used to wave it through. It must now be a violation."""
    f = tmp_path / "reporting.py"
    f.write_text(f"from {module} import main\n")
    assert len(verifier._scan_file(str(f))) == 1, f"{module} is still exempt"
    assert verifier._module_is_forbidden(module)


def test_a_comment_cannot_launder_a_crossing_in_the_regex_fallback(tmp_path):
    """The deleted `APPROVED_SEAM` branch matched a SUBSTRING of the offending LINE, so a
    trailing comment naming the seam cleared a real crossing. The fallback runs on files the
    AST cannot parse, so this was reachable."""
    laundered = "from simulation.household import Household  # company/interfaces/sim_interface\n"
    assert len(verifier._scan_lines(laundered, "saas/rogue.py")) == 1, (
        "a comment still launders a wall crossing in the regex fallback"
    )
    # VACUITY GUARD: the fallback is not simply flagging every line.
    assert verifier._scan_lines("from company.interfaces.sim_interface import x\n", "saas/ok.py") == []


def test_the_seam_exemption_is_a_property_of_the_importing_file():
    """Where the exemption legitimately lives — the same place the ratchet puts it (the
    company-side endpoint), not the text of a line."""
    assert verifier._is_exempt(shared.SEAM_PATH_PREFIX + "supply_book.py")
    assert not verifier._is_exempt("saas/reporting/annual_report.py")
