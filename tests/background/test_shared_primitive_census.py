"""R15 both-ways for SP5 -- the shared-primitive census as a standing gap register
(background/shared_primitive_census.py).

Every test pins its own fixture paths/trees (feedback_new_draw_rung_needs_fixture_isolation: a
new register must never read live disk in a test). Covers the three named killer patterns:
  TAUTOLOGY   -- the generator recomputes from a fresh source tree every call, never re-reads its
                 own prior JSON for the live-computed fields (only `previous_register_count` is a
                 deliberate carry-forward, and even that is diffed against a FRESH register_count).
  FAIL-OPEN   -- an empty/malformed/missing census file must read OPEN, never vacuously CLOSED
                 (the exact class named in the build brief: verdict({}) must never read met/closed).
  FAIL-SILENT -- an unavailable staleness-threshold import (retro_cadence_check) must not silently
                 disable staleness detection.
Plus a REAL bug this build pass caught and fixed: a whole-docstring co-occurrence heuristic for
quantity ownership false-positived on `simulation/arrears_engine.py` (a docstring mentioning both
"single source of truth" and, ~300 chars later, "bad debt"/"cost_to_serve" incidentally) -- fixed
with a bounded-proximity regex; both-ways proven below.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from background import shared_primitive_census as c


# --------------------------------------------------------------------------- helpers
def _write(p: Path, text: str) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def _clean_census(**overrides) -> dict:
    """A hand-built census dict that should read CLOSED (empty residue) -- every check passes on
    its own merits, not by omission."""
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "clone_count": 100,
        "clone_ceiling": 223,
        "register_count": 91,
        "previous_register_count": 91,
        "migration_note": None,
        "shared_primitive_inventory": {
            "working_day_calculator": {"exists": True, "caller_count": 5, "migrated_count": 5},
            "vat_constant": {"exists": False, "caller_count": 0, "migrated_count": 0},
        },
        "quantity_registry_coverage": {
            "net_margin": {"has_owner": True, "owner_module": "x.py"},
            "carbon": {"has_owner": True, "owner_module": "y.py"},
        },
    }
    data.update(overrides)
    return data


# --------------------------------------------------------------------------- CLOSED baseline
def test_clean_census_reads_closed(tmp_path):
    p = _write(tmp_path / "census.json", json.dumps(_clean_census()))
    assert c.census_register_open(p) == []
    assert c.shared_primitive_census_open(p) is False


# --------------------------------------------------------------------------- (a) clone drift, both ways
def test_clone_drift_past_ceiling_opens_then_restore_closes(tmp_path):
    p = _write(tmp_path / "census.json", json.dumps(_clean_census(clone_count=224)))
    rows = c.census_register_open(p)
    assert any(r["id"] == "clone_drift" for r in rows)

    # RESTORE (never git-checkout a mutation -- edit the fixture back)
    _write(p, json.dumps(_clean_census(clone_count=223)))  # AT the ceiling, not over
    assert c.census_register_open(p) == []


# --------------------------------------------------------------------------- (b) unmigrated primitive
def test_unmigrated_primitive_opens(tmp_path):
    data = _clean_census()
    data["shared_primitive_inventory"]["working_day_calculator"] = {
        "exists": True, "caller_count": 24, "migrated_count": 0,
    }
    p = _write(tmp_path / "census.json", json.dumps(data))
    rows = c.census_register_open(p)
    assert any(r["id"] == "unmigrated:working_day_calculator" for r in rows)


def test_primitive_that_does_not_exist_yet_never_flags_unmigrated(tmp_path):
    # exists=False (not yet built, e.g. RNG substream) must NOT be treated as an unfinished
    # migration -- that is a DIFFERENT, already-tracked problem (its own map atom), not this row.
    data = _clean_census()
    data["shared_primitive_inventory"]["rng_substream_primitive"] = {
        "exists": False, "caller_count": 12, "migrated_count": 0,
    }
    p = _write(tmp_path / "census.json", json.dumps(data))
    rows = c.census_register_open(p)
    assert not any("rng_substream_primitive" in r["id"] for r in rows)


# --------------------------------------------------------------------------- (c) uncovered quantity
def test_uncovered_quantity_opens(tmp_path):
    data = _clean_census()
    data["quantity_registry_coverage"]["carbon"] = {"has_owner": False, "owner_module": None}
    p = _write(tmp_path / "census.json", json.dumps(data))
    rows = c.census_register_open(p)
    assert any(r["id"] == "no_owner:carbon" for r in rows)


# --------------------------------------------------------------------------- (d) register growth
def test_register_growth_without_migration_note_opens(tmp_path):
    data = _clean_census(register_count=95, previous_register_count=91, migration_note=None)
    p = _write(tmp_path / "census.json", json.dumps(data))
    rows = c.census_register_open(p)
    assert any(r["id"] == "register_growth" for r in rows)


def test_register_growth_with_migration_note_does_not_open(tmp_path):
    data = _clean_census(
        register_count=95, previous_register_count=91,
        migration_note="merged 4 registers into Register base class",
    )
    p = _write(tmp_path / "census.json", json.dumps(data))
    rows = c.census_register_open(p)
    assert not any(r["id"] == "register_growth" for r in rows)


def test_register_shrink_never_opens(tmp_path):
    data = _clean_census(register_count=85, previous_register_count=91)
    p = _write(tmp_path / "census.json", json.dumps(data))
    assert not any(r["id"] == "register_growth" for r in c.census_register_open(p))


# --------------------------------------------------------------------------- FAIL-OPEN: missing/malformed/empty
def test_missing_file_reads_open_unreadable():
    rows = c.census_register_open(Path("/nonexistent/shared_primitive_census.json"))
    assert rows and rows[0]["id"] == "unreadable"


def test_malformed_json_reads_open_unreadable(tmp_path):
    p = _write(tmp_path / "census.json", "{not valid json")
    rows = c.census_register_open(p)
    assert rows and rows[0]["id"] == "unreadable"


def test_empty_object_reads_open_not_vacuously_closed(tmp_path):
    """THE NAMED FAIL-OPEN CLASS (build brief, citing the sibling W1_6b fork's finding: 'verdict({})
    returning met=True vacuously'). An empty {} must NEVER read CLOSED -- it must read OPEN because
    the required fields are absent, not because any check happened to pass."""
    p = _write(tmp_path / "census.json", "{}")
    rows = c.census_register_open(p)
    assert rows != [], "an empty census object must not vacuously read CLOSED"
    assert rows[0]["id"] == "unreadable"


def test_non_dict_json_reads_open(tmp_path):
    p = _write(tmp_path / "census.json", "[1, 2, 3]")
    rows = c.census_register_open(p)
    assert rows and rows[0]["id"] == "unreadable"


def test_malformed_inventory_entry_fails_safe_open(tmp_path):
    data = _clean_census()
    data["shared_primitive_inventory"]["working_day_calculator"] = "not-a-dict"
    p = _write(tmp_path / "census.json", json.dumps(data))
    rows = c.census_register_open(p)
    assert any("inventory:working_day_calculator" in r["id"] for r in rows)


def test_non_numeric_counts_fail_safe_open(tmp_path):
    data = _clean_census()
    data["shared_primitive_inventory"]["working_day_calculator"] = {
        "exists": True, "caller_count": "many", "migrated_count": None,
    }
    p = _write(tmp_path / "census.json", json.dumps(data))
    rows = c.census_register_open(p)
    assert any("inventory:working_day_calculator" in r["id"] for r in rows)


# --------------------------------------------------------------------------- staleness (R15 fail-safe)
def test_stale_census_opens_even_when_everything_else_clean(tmp_path):
    old = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    p = _write(tmp_path / "census.json", json.dumps(_clean_census(generated_at=old)))
    rows = c.census_register_open(p)
    assert any(r["id"] == "stale" for r in rows)


def test_fresh_census_does_not_open_on_staleness(tmp_path):
    p = _write(tmp_path / "census.json", json.dumps(_clean_census()))
    rows = c.census_register_open(p)
    assert not any(r["id"] == "stale" for r in rows)


def test_unparseable_generated_at_fails_safe_open(tmp_path):
    p = _write(tmp_path / "census.json", json.dumps(_clean_census(generated_at="not-a-date")))
    rows = c.census_register_open(p)
    assert rows and rows[0]["id"] == "unreadable"


# --------------------------------------------------------------------------- FAIL-SILENT: staleness threshold
def test_staleness_threshold_falls_back_when_retro_module_unavailable(monkeypatch):
    """If retro_cadence_check (the retro cadence this rides, per 5.3) is unimportable, the
    staleness check must fall back to a conservative constant, NEVER silently disable staleness
    detection (an unavailable checker is a FAILED checker, not a passed one)."""
    import sys

    monkeypatch.setitem(sys.modules, "background.retro_cadence_check", None)
    threshold = c._stale_days_threshold()
    assert threshold == c._STALE_DAYS_FALLBACK


def test_standing_review_due_fails_safe_when_retro_module_unavailable(monkeypatch):
    import sys

    monkeypatch.setitem(sys.modules, "background.retro_cadence_check", None)
    msg = c.standing_review_due()
    assert msg is not None and "DUE" in msg


def test_standing_review_due_delegates_to_retro_cadence(monkeypatch, tmp_path):
    """5.1/5.3 must not invent a second scheduling mechanism -- verify the delegation is real by
    pointing the retro dir at an EMPTY directory (no retro doc ever recorded) and confirming the
    real retro_cadence_check module reports staleness through this wrapper."""
    msg = c.standing_review_due(retro_dir=tmp_path)
    assert msg is not None and "learn-loop cadence has never fired" in msg


# --------------------------------------------------------------------------- generator: real AST clone detection
def test_clone_census_finds_a_real_cross_file_structural_clone(tmp_path):
    body = "\n".join(f"    x{i} = {i} + {i}" for i in range(20))  # >=45 AST nodes once parsed
    src = f"def do_thing(a, b):\n{body}\n    return x0\n"
    f1 = _write(tmp_path / "mod_a.py", src)
    f2 = _write(tmp_path / "mod_b.py", src.replace("do_thing", "do_the_same_thing"))
    files = [f1, f2]
    result = c._clone_census(files, project_dir=tmp_path, node_threshold=10)
    assert result["clone_set_count"] == 1
    assert result["clone_count"] == 2


def test_clone_in_single_file_does_not_count_cross_file(tmp_path):
    body = "\n".join(f"    x{i} = {i} + {i}" for i in range(20))
    src = f"def a(n):\n{body}\n    return x0\n\ndef b(n):\n{body}\n    return x0\n"
    f1 = _write(tmp_path / "mod_a.py", src)
    result = c._clone_census([f1], project_dir=tmp_path, node_threshold=10)
    assert result["clone_set_count"] == 0, "a same-file duplicate is not a CROSS-FILE clone"


def test_differently_shaped_functions_do_not_clone(tmp_path):
    f1 = _write(tmp_path / "mod_a.py", "def f(x):\n    return x + 1\n")
    f2 = _write(tmp_path / "mod_b.py", "def g(y):\n    if y:\n        return y * 2\n    return 0\n")
    result = c._clone_census([f1, f2], project_dir=tmp_path, node_threshold=1)
    assert result["clone_set_count"] == 0


def test_unparseable_file_is_recorded_not_silently_dropped(tmp_path):
    bad = _write(tmp_path / "broken.py", "def f(:\n    pass\n")
    result = c._clone_census([bad], project_dir=tmp_path)
    assert result["unparseable"], "a syntax error must be surfaced, not silently skipped"


# --------------------------------------------------------------------------- generator: register count
def test_register_count_matches_filename_heuristic(tmp_path):
    company = tmp_path / "company"
    _write(company / "foo_register.py", "x = 1\n")
    _write(company / "bar.py", "x = 1\n")
    _write(company / "sub" / "baz_register.py", "x = 1\n")
    assert c._register_count(tmp_path) == 2


def test_register_count_zero_on_missing_company_dir(tmp_path):
    assert c._register_count(tmp_path) == 0


# --------------------------------------------------------------------------- generator: TAUTOLOGY guard
def test_generate_recomputes_from_source_never_from_its_own_prior_output(tmp_path):
    """The generator must derive clone_count/register_count/inventory freshly from the CURRENT
    tree every call -- proven by mutating the tree between two calls and observing the numbers
    move (a tautological generator that just echoed a cached value would not)."""
    project = tmp_path / "proj"
    company = project / "company"
    _write(company / "a_register.py", "x = 1\n")

    first = c.generate(project_dir=project, roots=("company",), previous_census_path=tmp_path / "none.json")
    assert first["register_count"] == 1

    _write(company / "b_register.py", "x = 1\n")
    second = c.generate(project_dir=project, roots=("company",), previous_census_path=tmp_path / "none.json")
    assert second["register_count"] == 2, "must reflect the FRESH tree, not the first call's cached value"


def test_write_census_records_previous_register_count_for_drift_detection(tmp_path):
    project = tmp_path / "proj"
    company = project / "company"
    _write(company / "a_register.py", "x = 1\n")
    out_path = tmp_path / "out.json"

    # previous_census_path pinned to a nonexistent fixture path -- must NEVER default to the real
    # live docs/observability/shared_primitive_census.json (test-isolation: a real disk artefact
    # must not leak into an unpinned test).
    no_prior = tmp_path / "no_prior.json"
    c.write_census(path=out_path, project_dir=project, roots=("company",), previous_census_path=no_prior)
    first = json.loads(out_path.read_text())
    assert first["register_count"] == 1
    assert first["previous_register_count"] is None  # nothing to compare on the first run

    _write(company / "b_register.py", "x = 1\n")
    c.write_census(path=out_path, project_dir=project, roots=("company",), previous_census_path=out_path)
    second = json.loads(out_path.read_text())
    assert second["register_count"] == 2
    assert second["previous_register_count"] == 1


# --------------------------------------------------------------------------- quantity-ownership proximity (the real bug found+fixed)
def test_incidental_cooccurrence_does_not_falsely_claim_ownership(tmp_path):
    """Reproduces the real false-positive this build pass found in
    simulation/arrears_engine.py: a docstring declares 'single source of truth' for something
    UNRELATED, and ~300 chars later happens to mention an unrelated quantity in passing. That must
    NOT read has_owner=True (the fail-open this proximity fix closes)."""
    filler = "x" * 300
    text = (
        f'"""Single source of truth for payment outcomes. {filler} '
        f'replacing the old cost_to_serve.get_bad_debt_rate() formula."""\n'
    )
    f = _write(tmp_path / "mod.py", text)
    coverage = c._quantity_coverage([f], project_dir=tmp_path)
    assert coverage["cost_to_serve"]["has_owner"] is False
    assert coverage["bad_debt"]["has_owner"] is False


def test_genuine_proximate_ownership_declaration_is_detected(tmp_path):
    text = '"""This module is the single owning module for net margin across the codebase."""\n'
    f = _write(tmp_path / "mod.py", text)
    coverage = c._quantity_coverage([f], project_dir=tmp_path)
    assert coverage["net_margin"]["has_owner"] is True
    assert coverage["net_margin"]["owner_module"] == "mod.py"


# --------------------------------------------------------------------------- diagnostic-only (R12)
def test_open_residue_counts_is_diagnostic_not_a_score(tmp_path):
    p = _write(tmp_path / "census.json", json.dumps(_clean_census(clone_count=999)))
    assert c.open_residue_counts(p) == len(c.census_register_open(p))


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
