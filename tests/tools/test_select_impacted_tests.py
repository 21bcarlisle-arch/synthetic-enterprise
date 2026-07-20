"""R15 proof for tools/select_impacted_tests.py (director test-throughput steer, 2026-07-20).

The selector's ONLY risk is under-selection: dropping a test that would have caught a real
regression. R15 requires proving, by MUTATION, that this does not happen. These tests build a small
SYNTHETIC repo tree, inject a real regression into a production module, ask the selector for the
impacted set, and prove (a) the guarding test is IN the set, (b) running only that selected set goes
RED on the mutation, and (c) a non-mappable change fails SAFE to the full suite. Because the mutation
proof runs on a synthetic tree it is hermetic and fast -- it is a genuine "the guard still fires"
demonstration, not a claim about the real 19k-test suite.
"""
from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

import tools.select_impacted_tests as sel


def _write(root: Path, rel: str, body: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(body), encoding="utf-8")


@pytest.fixture
def synth_repo(tmp_path: Path) -> Path:
    """A minimal repo tree exercising the exact 'shallow map misses transitive coupling' case:
      company/core.py            -- the production module under change
      company/billing/bill.py    -- imports core (transitive user)
      tests/company/test_bill.py -- imports bill, asserts on core's behaviour THROUGH bill
      tests/company/test_unrelated.py -- imports neither; must NOT be selected
    The convention map (test_<stem>.py) would select only test_core.py (absent here) for a core.py
    change -- test_bill.py is exactly what a filename map misses and the import graph must catch.
    """
    _write(tmp_path, "company/__init__.py", "")
    _write(tmp_path, "company/billing/__init__.py", "")
    _write(tmp_path, "company/core.py", """
        def unit_rate_pence():
            return 25  # the value a regression will corrupt
    """)
    _write(tmp_path, "company/billing/bill.py", """
        from company.core import unit_rate_pence
        def bill_total(kwh):
            return kwh * unit_rate_pence()
    """)
    _write(tmp_path, "tests/__init__.py", "")
    _write(tmp_path, "tests/company/__init__.py", "")
    _write(tmp_path, "tests/company/test_bill.py", """
        from company.billing.bill import bill_total
        def test_bill_total_uses_correct_rate():
            assert bill_total(100) == 2500  # 100 kwh * 25p -- guards company/core.py's value
    """)
    _write(tmp_path, "tests/company/test_unrelated.py", """
        def test_addition():
            assert 1 + 1 == 2
    """)
    return tmp_path


def test_transitive_guard_is_selected(synth_repo: Path):
    """A change to core.py selects test_bill.py (transitive user) -- the case a filename map misses."""
    result = sel.select(["company/core.py"], root=synth_repo)
    assert result["full_suite"] is False
    assert "tests/company/test_bill.py" in result["tests"]
    # And it does NOT over-select the genuinely unrelated test.
    assert "tests/company/test_unrelated.py" not in result["tests"]


def test_mutation_selected_subset_goes_red(synth_repo: Path):
    """R15 CORE: inject the real regression, run ONLY the impact-selected subset, prove it fails.
    This is the proof that selection did not drop the guard -- the mutation is caught by exactly the
    set the selector returns, with nothing else run."""
    subset = sel.select(["company/core.py"], root=synth_repo)["tests"]
    assert subset, "selector must return at least the guarding test"

    def run_subset() -> subprocess.CompletedProcess:
        # PYTHONDONTWRITEBYTECODE: never cache a .pyc, so the mutated source is always re-read
        # (a same-second-mtime stale .pyc would otherwise mask the mutation -- a harness artifact,
        # not a selector property).
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        return subprocess.run(
            [sys.executable, "-m", "pytest", *subset, "-q", "-p", "no:cacheprovider"],
            cwd=str(synth_repo), capture_output=True, text=True, env=env,
        )

    # Baseline: the selected subset is GREEN before the mutation.
    assert run_subset().returncode == 0, "selected subset should pass before the mutation"

    # MUTATE the production module (a real regression: wrong unit rate).
    core = synth_repo / "company/core.py"
    core.write_text(core.read_text().replace("return 25", "return 99"), encoding="utf-8")

    # The SAME selected subset must now go RED -- the guard still fires under the new regime.
    red = run_subset()
    assert red.returncode != 0, (
        "MUTATION ESCAPED: the impact-selected subset stayed green after a real regression.\n"
        + red.stdout[-2000:]
    )


def test_non_mappable_change_fails_safe_to_full_suite():
    """A non-.py change (a data ledger, config, site file) cannot be graph-analysed -> the selector
    must fall back to the FULL suite, never a narrowed set. Fail-safe direction: run too much."""
    result = sel.select(["docs/observability/coupled_gap_ledger.json"])
    assert result["full_suite"] is True
    assert result["tests"] == []
    assert result["unmappable"] == ["docs/observability/coupled_gap_ledger.json"]


def test_mixed_change_with_one_unmappable_still_full_suite():
    """If ANY changed path is unmappable, the whole selection is unsafe -> full suite (a mappable
    change alongside an opaque one must not lull the selector into narrowing)."""
    result = sel.select(["company/core.py", "some/config.yaml"])
    assert result["full_suite"] is True


def test_changed_test_file_is_its_own_guard(synth_repo: Path):
    """A changed test file selects itself even if nothing imports it."""
    result = sel.select(["tests/company/test_unrelated.py"], root=synth_repo)
    assert "tests/company/test_unrelated.py" in result["tests"]


def test_empty_change_selects_nothing():
    result = sel.select([])
    assert result["full_suite"] is False
    assert result["tests"] == []


def test_real_repo_graph_catches_billing_coupling():
    """Non-hermetic sanity check against the REAL repo: a change to the bitemporal event log selects
    the billing account-ledger test that transitively uses it -- the concrete coupling the shallow
    convention map (only test_bitemporal_event_log.py) misses. Guards against a future refactor
    silently breaking the analyser on the real tree."""
    result = sel.select(["company/interfaces/bitemporal_event_log.py"])
    assert result["full_suite"] is False
    assert "tests/company/billing/test_account_ledger.py" in result["tests"]
