"""The join tier's REPORT-ONLY landing, and the two rules that keep it honest.

Design: `docs/design/JOIN_TEST_TIER.md` §3 and §2.

This module is the tier's own control surface, and it deliberately does NOT carry
`join_report_only`: it must stay blocking. If the containment guard below were
itself report-only, the fail-open channel it exists to close would be open and
nothing would notice.

Two properties:

1. **Report-only is MECHANISED, not promised.** The publish gate's real marker
   expression deselects `join_report_only`, so a red join test alarms but cannot
   wedge the live site. Asserted against the LIVE argv the gate runs, not against
   a restatement of it.

2. **The channel it opens is CONTAINED.** Adding a deselected marker class means
   any content test could be silenced by taking the marker. So: no module outside
   `tests/system/` may carry it. And the advisor's "one real rule" for this tier —
   test helpers that reach across the wall must live where production code cannot
   import them — is enforced rather than assumed, or the test scaffolding becomes
   the back door.
"""

import ast
import subprocess
import sys
from pathlib import Path

import pytest

from background import process_run_complete as prc

ROOT = Path(__file__).resolve().parents[2]
SYSTEM_TIER = ROOT / "tests" / "system"

#: Every report-only marker this tier carries. `scale_report_only` joined on
#: 2026-08-09 (AO4_scale_constraints_executable) on identical terms. They are
#: SEPARATE markers on purpose — one marker would mean promoting either tier out
#: of report-only promotes both, and the two earn their stable weeks
#: independently. Containment and coverage below are asserted over the whole set,
#: so a third marker added without extending this tuple fails the coverage half.
REPORT_ONLY_MARKERS = ("join_report_only", "scale_report_only")

#: The exact expression the publish gate runs. Pinned as a literal (not rebuilt
#: from REPORT_ONLY_MARKERS) — a check that derives the expected value from the
#: same source it checks is a tautology and would agree with any drift (R15).
EXPECTED_GATE_EXPR = (
    "not operational and not join_report_only and not scale_report_only"
)
#: Where a test-tree import would be a genuine WALL breach: the layers the
#: epistemic wall actually separates. Zero tolerance -- the cross-wall helpers in
#: chains.py must be unreachable from anything shippable.
WALL_ROOTS = ("company", "saas", "sim", "simulation", "interface")

#: The wider surface. Same SHAPE of defect (test scaffolding reachable from
#: non-test code) but not a wall breach, so it is pinned rather than fixed on
#: sight (SELF_INTERRUPT_DISCIPLINE: queue by default, the supply is infinite).
WIDER_ROOTS = ("background", "tools")

#: Known, pre-existing instances in WIDER_ROOTS. An amnesty with no "exactly
#: these" bound measures nothing -- the test below asserts the offender set is
#: EXACTLY this, so a new one fails and a fixed one fails too (forcing the stale
#: pin to be removed rather than quietly protecting nothing).
KNOWN_WIDER_TEST_IMPORTS = {
    "tools/build_battery_register.py -> tests.domain.battery_register",
    # KNIFE pass 1's pin (`knife_hotspot_measure` -> the ratchet test module) was REMOVED
    # here on 2026-08-09, because the thing it was pinned against actually happened: pass 3's
    # declared first step rehomed the walker (`build_edges`/`company_reads_sim`/
    # `sim_reads_company`) into `tools/epistemic_wall.py`, and the ratchet, the hotspot
    # ledger and `tools/epistemic_verifier.py` now all import it from there. The pin said the
    # honest fix was exactly that rehome; the rehome landed, so the pin goes with it.
    #
    # This deletion is the amnesty working as designed rather than an edit to accommodate one:
    # the set is asserted EXACTLY, so a FIXED offender reds just as loudly as a new one and
    # the stale pin cannot outlive the crossing it was protecting.
}


# ── property 1 — report-only is wired into the gate that actually runs ───────

def test_the_publish_gate_deselects_the_join_tier():
    argv = prc.publish_gate_pytest_argv("tests/")
    assert prc.PUBLISH_GATE_MARKER_EXPR == EXPECTED_GATE_EXPR
    assert "-m" in argv
    assert argv[argv.index(prc.PUBLISH_GATE_MARKER_EXPR) - 1] == "-m", (
        "the marker expression is present in argv but not as the value of `-m` — it is "
        "not actually deselecting anything"
    )


@pytest.mark.parametrize("module", [
    "tests/system/test_join_work_loop.py",
    "tests/system/test_scale_constraints.py",
])
def test_pytest_really_deselects_the_marked_tier_not_just_the_config(module):
    """Resolve the marker the way pytest resolves it, on the REAL tier.

    The config constant agreeing with itself is a tautology; what matters is
    whether collection under the gate's own expression actually drops these
    modules. Collect `tests/system/` under the live marker expression and assert
    nothing survives. One representative module per report-only marker — a second
    marker that was registered but never added to the gate expression would pass
    every string check above and fail here.
    """
    r = subprocess.run(
        [sys.executable, "-m", "pytest", module,
         "--collect-only", "-q", "-p", "no:cacheprovider",
         "-m", prc.PUBLISH_GATE_MARKER_EXPR],
        cwd=str(ROOT), capture_output=True, text=True,
    )
    assert "no tests ran" in r.stdout or "0 tests collected" in r.stdout or \
           "deselected" in r.stdout, (
        f"{module} was NOT deselected by the publish gate's own marker expression "
        f"— report-only is not in force.\nstdout:\n{r.stdout[-2000:]}"
    )


@pytest.mark.parametrize("marker", REPORT_ONLY_MARKERS)
def test_a_red_join_test_cannot_wedge_the_publish_gate(tmp_path, marker):
    """The end-to-end claim, on a throwaway tree: a RED marked test passes the
    gate's selector, and a RED unmarked one still fails it.

    Both directions. Without the second, 'report-only works' would also be
    satisfied by a selector that deselects everything. Run per marker: each one
    opens its own fail-open channel and each has to be shown to be contained.
    """
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "conftest.py").write_text(
        "def pytest_configure(config):\n"
        + "".join(
            f"    config.addinivalue_line('markers', '{m}: x')\n"
            for m in (*REPORT_ONLY_MARKERS, "operational")
        )
    )
    # A green UNMARKED test, so the synthetic tree mirrors the real gate: with
    # only a deselected test present pytest exits 5 ("no tests collected"), which
    # would read as a wedge for a reason that can never occur against the real
    # suite.
    (tmp_path / "tests" / "test_surface_ok.py").write_text(
        "def test_a_healthy_surface():\n    assert True\n"
    )
    (tmp_path / "tests" / "test_join_red.py").write_text(
        "import pytest\n"
        f"pytestmark = pytest.mark.{marker}\n"
        "def test_brittle_join():\n    assert False, 'a brittle join test'\n"
    )

    def _run():
        return subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-q", "-p", "no:cacheprovider",
             "-m", prc.PUBLISH_GATE_MARKER_EXPR],
            cwd=str(tmp_path), capture_output=True, text=True,
        ).returncode

    assert _run() == 0, "a red REPORT-ONLY join test wedged the gate — the whole point"

    (tmp_path / "tests" / "test_content_red.py").write_text(
        "def test_a_real_broken_surface():\n    assert False, 'a real content break'\n"
    )
    assert _run() != 0, (
        "a red UNMARKED content test passed the gate — the deselection is too wide and "
        "real breaks would now publish"
    )


# ── property 2 — the channel the marker opens stays contained ────────────────

def _module_level_marks(path: Path) -> set[str]:
    """Marker names a module applies at module level, resolved the way pytest
    resolves them (a `pytestmark` assignment), NOT by substring.

    A substring detector diverges from the mechanism it audits in both
    directions — a docstring mentioning the marker reads as marked, and an
    aliased marker reads as unmarked. That is the exact control-fidelity defect
    already found and fixed in `test_publish_gate_scope.py`; do not reintroduce it.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return set()
    marks: set[str] = set()
    for node in tree.body:
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        if not any(isinstance(t, ast.Name) and t.id == "pytestmark" for t in targets):
            continue
        marks |= {n.attr for n in ast.walk(node) if isinstance(n, ast.Attribute)}
    return marks


@pytest.mark.parametrize("marker", REPORT_ONLY_MARKERS)
def test_join_report_only_marker_is_confined_to_the_system_tier(marker):
    """CONTAINMENT. The gate now ignores anything carrying these markers, so a
    content or safety-wall test that took one would silently stop blocking."""
    strays = [
        str(p.relative_to(ROOT))
        for p in (ROOT / "tests").rglob("test_*.py")
        if marker in _module_level_marks(p)
        and SYSTEM_TIER not in p.parents
    ]
    assert strays == [], (
        f"{marker} escaped tests/system/ — these modules are now deselected from "
        f"the publish gate and can no longer block a bad publish: {strays}"
    )


def test_every_join_module_actually_carries_the_marker():
    """The other direction: an UNMARKED module in this tier is blocking, which
    contradicts the report-only landing the director ruled. This module is the
    single deliberate exception — it is the control surface and must stay
    blocking.

    Each module must carry EXACTLY ONE of the report-only markers. Zero would
    block publish; two would mean promoting one tier out of report-only silently
    leaves the module deselected under the other, which is how a tier gets
    promoted on paper and stays report-only in fact.
    """
    wrong = {
        p.name: sorted(_module_level_marks(p) & set(REPORT_ONLY_MARKERS))
        for p in sorted(SYSTEM_TIER.glob("test_*.py"))
        if p.name != Path(__file__).name
        and len(_module_level_marks(p) & set(REPORT_ONLY_MARKERS)) != 1
    }
    assert wrong == {}, (
        "every module in this tier must carry exactly one report-only marker; these do "
        f"not: {wrong}"
    )


def test_this_control_module_is_itself_blocking():
    """A containment guard that is itself deselected guards nothing."""
    assert not (_module_level_marks(Path(__file__)) & set(REPORT_ONLY_MARKERS))


# ── the advisor's "one real rule" for this tier ──────────────────────────────

def test_no_production_module_imports_the_test_tree():
    """Test helpers that reach across the wall must live where production code
    cannot import them — otherwise the test scaffolding becomes the back door.

    `tests/system/chains.py` deliberately sees BOTH sides of the wall (it must, to
    verify the wall holds at all). That is safe only while nothing shippable can
    import it.
    """
    offenders = _test_tree_importers(WALL_ROOTS)
    assert offenders == set(), (
        "a layer BEHIND THE EPISTEMIC WALL imports the test tree — the cross-wall "
        f"helpers in chains.py are now reachable from shippable code: {sorted(offenders)}"
    )


def test_the_wider_test_tree_import_surface_does_not_grow():
    """Same defect shape outside the wall roots, pinned rather than fixed on sight.

    Bounded EXACTLY, not as a floor: a new offender fails, and so does a fixed
    one. An amnesty that only checks "no more than before" lets the pin outlive
    the thing it pins and silently protect nothing
    (`feedback_forgiveness_baseline_needs_a_once_only_guard`).
    """
    offenders = _test_tree_importers(WIDER_ROOTS)
    assert offenders == KNOWN_WIDER_TEST_IMPORTS, (
        "the non-test code that imports the test tree has changed.\n"
        f"  new:   {sorted(offenders - KNOWN_WIDER_TEST_IMPORTS)}\n"
        f"  fixed: {sorted(KNOWN_WIDER_TEST_IMPORTS - offenders)} "
        "(remove it from KNOWN_WIDER_TEST_IMPORTS)"
    )


def _test_tree_importers(roots: tuple[str, ...]) -> set[str]:
    """`<relpath> -> <imported test module>` for every non-test module under
    `roots` that imports from the test tree.

    Line numbers are deliberately excluded from the key: pinning them would make
    the set churn on any unrelated edit above the import, and a pin that fails
    for cosmetic reasons gets suppressed rather than read.
    """
    found: set[str] = set()
    for root in roots:
        for path in (ROOT / root).rglob("*.py"):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except (OSError, SyntaxError):
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                else:
                    continue
                for name in names:
                    if name == "tests" or name.startswith("tests."):
                        found.add(f"{path.relative_to(ROOT)} -> {name}")
    return found


@pytest.mark.parametrize("chain_helper", ["run_physical_chain", "assert_money_join"])
def test_the_cross_wall_helpers_live_only_in_the_test_tree(chain_helper):
    """NON-VACUITY for the guard above: the helpers it protects genuinely exist in
    the test tree. A containment guard over an empty set passes forever."""
    from tests.system import chains

    assert hasattr(chains, chain_helper)
    assert Path(chains.__file__).is_relative_to(ROOT / "tests")
