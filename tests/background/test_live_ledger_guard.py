"""A test process may not write a live observability ledger.

The control under test is `background/live_ledger_guard.py`, built for the
2026-08-17 BLOCKING finding (H27 Expert Hour #33): `simulation/run_phase2b.py`
writes the coupled gap ledger with `ledger_path` defaulted, 67 test modules
import it, and one of them replaced the 1600-invoice population with a
276-invoice fixture book -- republishing the public Proof door's payment
belief-vs-truth gap 0.0834 -> 0.0311.

R15: every test below is paired with the source mutation it fires on, named in
its own docstring. A control that cannot fail is worse than none.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from background import live_ledger_guard as guard
from background.live_ledger_guard import (
    LIVE_RECORD_DIR,
    LiveLedgerWriteUnderTest,
    guard_live_ledger_write,
    in_test_process,
    is_live_record_path,
)

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
BACKGROUND_DIR = PROJECT_DIR / "background"


# ===========================================================================
# The guard says YES when it should -- without this it is a control that
# refuses everything, which is indistinguishable from a broken import.
# ===========================================================================

def test_a_scratch_path_is_permitted(tmp_path):
    """MUTATION: make `guard_live_ledger_write` raise unconditionally. Every
    existing ledger test (all of which use tmp_path) goes red, and so does
    this."""
    p = tmp_path / "ledger.json"
    assert guard_live_ledger_write(p, writer="t") is p


def test_a_path_outside_the_record_dir_is_not_a_live_record(tmp_path):
    assert is_live_record_path(tmp_path / "coupled_gap_ledger.json") is False


# ===========================================================================
# The guard says NO when it should.
# ===========================================================================

def test_the_live_coupled_gap_ledger_is_refused_from_a_test_process():
    """The incident itself. MUTATION: delete the
    `guard_live_ledger_write(...)` line from `write_gap_entry` -- this reds."""
    live = LIVE_RECORD_DIR / "coupled_gap_ledger.json"
    with pytest.raises(LiveLedgerWriteUnderTest) as exc:
        guard_live_ledger_write(live, writer="probe")
    assert "probe" in str(exc.value)


def test_a_relative_and_dot_dot_spelling_of_the_same_file_is_the_same_subject():
    """FAIL-OPEN. MUTATION: replace the `Path(path).resolve()` +
    `relative_to` test in `is_live_record_path` with a string
    `str(path).startswith(str(LIVE_RECORD_DIR))`. This reds -- a traversal
    spelling names the identical inode and would sail through."""
    traversal = LIVE_RECORD_DIR / ".." / "observability" / "coupled_gap_ledger.json"
    assert is_live_record_path(traversal) is True
    with pytest.raises(LiveLedgerWriteUnderTest):
        guard_live_ledger_write(traversal, writer="probe")


def test_an_unresolvable_path_fails_closed(monkeypatch):
    """FAIL-OPEN. MUTATION: change `is_live_record_path`'s except branch to
    `return False`. An unresolvable path is not evidence of innocence."""
    class _Exploding:
        def __fspath__(self):
            raise OSError("cannot resolve")
    assert is_live_record_path(_Exploding()) is True


def test_a_new_ledger_nobody_enumerated_is_covered_on_the_day_it_is_created():
    """The subject is DERIVED (containment in the record dir), never a
    hand-listed set of filenames. MUTATION: replace `is_live_record_path` with
    a membership test against a literal tuple of today's three ledger names --
    this reds, because a ledger invented in this test is not in it."""
    invented = LIVE_RECORD_DIR / "a_ledger_that_does_not_exist_yet.json"
    assert is_live_record_path(invented) is True
    with pytest.raises(LiveLedgerWriteUnderTest):
        guard_live_ledger_write(invented, writer="probe")


# ===========================================================================
# Test-process detection -- the OTHER half of the predicate.
# ===========================================================================

def test_detection_survives_the_env_var_being_absent(monkeypatch):
    """FAIL-OPEN. MUTATION: reduce `in_test_process` to the
    `PYTEST_CURRENT_TEST` check alone. `PYTEST_CURRENT_TEST` is unset during
    collection and at module import, so a write in either window -- which is
    exactly where an import-time daemon write lands -- would be permitted.
    `pytest in sys.modules` is the signal that still holds."""
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    assert in_test_process() is True


def test_outside_a_test_process_the_live_write_is_permitted(monkeypatch):
    """The control must be able to say yes to the REAL writer, or it has
    silently disabled the measurement of record instead of protecting it.
    MUTATION: drop the `if not in_test_process(): return path` early exit --
    this reds, and so does every real `--write-ledger` invocation."""
    monkeypatch.setattr(guard, "in_test_process", lambda: False)
    live = LIVE_RECORD_DIR / "coupled_gap_ledger.json"
    assert guard.guard_live_ledger_write(live, writer="probe") is live


def test_there_is_no_env_var_override():
    """An escape hatch is a FAIL-OPEN door that the offending process is
    exactly the one able to set. MUTATION: add
    `if os.environ.get("ALLOW_..."): return path` -- this reds by reading the
    guard's own source for an environment read inside the refusal path."""
    src = (BACKGROUND_DIR / "live_ledger_guard.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "guard_live_ledger_write")
    reads_env = [n for n in ast.walk(fn)
                 if isinstance(n, ast.Attribute) and n.attr in {"environ", "getenv"}]
    assert reads_env == [], "guard_live_ledger_write reads the environment"


# ===========================================================================
# THE CLASS CONTROL (R10) -- every live-ledger writer is guarded, and the
# population is DERIVED from the tree, not transcribed here.
# ===========================================================================

GAP_LEDGER_CONVENTION = "GAP_LEDGER_PATH"


def _gap_ledger_modules() -> dict:
    """Every `background/*.py` that speaks the `GAP_LEDGER_PATH` convention --
    binding it OR importing it -- mapped to its parsed tree.

    THE SUBJECT IS THE CONVENTION, NOT A FILENAME LIST. Every measurement
    ledger a published surface derives from names its destination with this one
    constant, so a fourth one joins the population by following the same house
    convention, with nobody editing this test. The `import` half is not
    cosmetic: `gap_metric.py` -- the module the 2026-08-17 incident actually ran
    through -- IMPORTS the constant from `coupled_triad.py` rather than binding
    it, and an assignment-only predicate silently excluded exactly the writer
    this control exists for (caught building this test, not after)."""
    found = {}
    for py in sorted(BACKGROUND_DIR.glob("*.py")):
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                names.add(node.id)
            elif isinstance(node, ast.alias):
                names.add(node.asname or node.name)
        if GAP_LEDGER_CONVENTION in names:
            found[py.name] = tree
    return found


def _functions_that_write(tree) -> list:
    """Functions whose body calls `.write_text(` -- i.e. actually persist."""
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for call in ast.walk(node):
            if (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                    and call.func.attr == "write_text"):
                out.append(node)
                break
    return out


def test_the_writer_population_is_not_empty():
    """A census that finds nothing reads as a clean sweep. MUTATION: break the
    AST predicate so it matches no module -- the class test below would then
    pass vacuously; this one reds first."""
    mods = _gap_ledger_modules()
    assert {"gap_metric.py", "dd_h_solvency_gap.py",
            "conversation_gap_ledger.py"} <= set(mods), sorted(mods)
    writers = {n for n, t in mods.items() if _functions_that_write(t)}
    assert len(writers) >= 3, f"expected three persisting modules, got {sorted(writers)}"


def test_every_live_ledger_writer_calls_the_guard():
    """R10: the class fails automatically, not the instance. MUTATION: delete
    the guard call from ANY ONE of the three writers -- this names that
    function and reds. A fourth ledger module following the house convention
    reds on the day it lands, unguarded."""
    unguarded = []
    for name, tree in _gap_ledger_modules().items():
        for fn in _functions_that_write(tree):
            calls = {c.func.id for c in ast.walk(fn)
                     if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)}
            if "guard_live_ledger_write" not in calls:
                unguarded.append(f"{name}::{fn.name}")
    assert unguarded == [], (
        "these persist a live measurement ledger with no test-process "
        f"refusal: {unguarded}")


def test_the_narrowing_to_measurement_ledgers_is_measured_not_assumed():
    """This control's subject is the MEASUREMENT-ledger family, not every file
    under `docs/observability/`. That narrowing has to be counted rather than
    assumed away, because the excluded set is not empty: daemon STATE writers
    (`supervisor.py`'s stuck/interleave/stall savers, `trust_ledger.py`,
    `fidelity_evidence_ledger.py`) persist under the same directory from the
    same test processes and are the SAME SHAPE of defect -- a test's state
    becoming the record. They are OWED, not covered: filed on the finding, not
    silently dropped.

    MEASURED 2026-08-17, not estimated: **75** persisting functions across 40
    `background/` modules touch that directory outside the guarded family. That
    is far too large to guard in this tick without reding the many existing
    tests that deliberately write live state paths, and pretending otherwise
    would be the same defect one level up. So the number is pinned HERE, where
    a reader of this control sees the boundary of what it actually covers.

    This test pins the excluded count so it cannot grow unnoticed. If it moves,
    the honest response is to widen the guard, not to bump the number."""
    covered = set(_gap_ledger_modules())
    excluded = []
    for py in sorted(BACKGROUND_DIR.glob("*.py")):
        if py.name in covered:
            continue
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        src = py.read_text(encoding="utf-8")
        if "observability" not in src:
            continue
        for fn in _functions_that_write(tree):
            excluded.append(f"{py.name}::{fn.name}")
    assert len(excluded) <= 75, (
        f"the un-guarded observability-writer population GREW to {len(excluded)} "
        "-- widen `live_ledger_guard` rather than this bound: "
        f"{sorted(excluded)}")


def test_the_guard_is_imported_at_top_level_with_no_try():
    """FAIL-SILENT. MUTATION: wrap any writer's
    `from background.live_ledger_guard import ...` in `try: ... except
    ImportError: guard_live_ledger_write = lambda p, **k: p`. That is an
    unavailable check reading as a passed one; this reds."""
    for name in ("gap_metric.py", "dd_h_solvency_gap.py", "conversation_gap_ledger.py"):
        tree = ast.parse((BACKGROUND_DIR / name).read_text(encoding="utf-8"))
        top_level = {n.module for n in tree.body if isinstance(n, ast.ImportFrom)}
        assert "background.live_ledger_guard" in top_level, (
            f"{name} does not import the guard at module top level")


# ===========================================================================
# End to end, on the real writer -- the finding's own reproduction.
# ===========================================================================

def test_write_gap_entry_refuses_the_default_path_and_leaves_the_record_untouched():
    """The incident, closed at the choke point. Before this control,
    `write_gap_entry` with `ledger_path` defaulted persisted from inside
    pytest; that is how a fixture book became the door's supplier."""
    from background import gap_metric as gm

    live = gm.GAP_LEDGER_PATH
    before = live.read_bytes() if live.is_file() else None

    result = gm.GapResult(
        metric="belief", gap=0.5, raw_gap=0.5, g0=1.0,
        baseline="probe baseline", components={}, normalisation="divisor",
    )
    with pytest.raises(LiveLedgerWriteUnderTest):
        gm.write_gap_entry("W2_TEST_probe", "D_TEST_probe", result)

    after = live.read_bytes() if live.is_file() else None
    assert after == before, "the live coupled gap ledger was modified by a test"
    if after is not None:
        assert "W2_TEST_probe" not in json.loads(after)


def test_write_gap_entry_still_writes_when_given_a_scratch_path(tmp_path):
    """The guard must not have broken the legitimate path -- every existing
    ledger test uses this shape."""
    from background import gap_metric as gm

    p = tmp_path / "ledger.json"
    result = gm.GapResult(
        metric="belief", gap=0.5, raw_gap=0.5, g0=1.0,
        baseline="probe baseline", components={}, normalisation="divisor",
    )
    ledger = gm.write_gap_entry("W2_TEST_probe", "D_TEST_probe", result, ledger_path=p)
    assert "W2_TEST_probe" in ledger
    assert "W2_TEST_probe" in json.loads(p.read_text(encoding="utf-8"))
