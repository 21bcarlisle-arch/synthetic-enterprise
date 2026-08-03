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
        # 5.3/5.4: a CLOSED register now also requires that the standing structural review has
        # actually HAPPENED recently -- an unrun ensuring activity is not evidence of no drift.
        c.REVIEW_STAMP_KEY: {
            "date": datetime.now(timezone.utc).date().isoformat(),
            "evaluator": "phase-close-evaluator",
            "verdict": "pass",
            "subject": "shared_primitive_census_fixture",
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


# --------------------------------------------------------------------------- THE WIRING (SP5's actual acceptance)
# The census was built standalone and nothing read it -- which is precisely the
# consumed-not-absorbed failure mode this atom exists to catch. These controls
# fail if register 9 is ever unwired from the gap-register reader, so the
# mechanism cannot silently revert to a module nobody calls.

def test_census_is_registered_as_gap_register_9():
    """Unwiring the census from _REGISTERS must FAIL here, not pass silently."""
    from background import gap_register_scan

    assert "shared_primitive_census" in gap_register_scan._REGISTERS, (
        "the shared-primitive census is not wired into the gap-register reader "
        "-- a census nothing reads cannot make a rest claim impossible"
    )
    assert gap_register_scan._REGISTERS["shared_primitive_census"] is (
        c.census_register_open
    )


def test_open_census_alone_makes_a_rest_claim_impossible(tmp_path, monkeypatch):
    """The atom's acceptance: an OPEN duplication blocks rest ON ITS OWN.

    Every other register is removed, so this cannot pass on some other
    register's residue -- it passes only if register 9 is genuinely wired and
    genuinely reaches `gap_register_open`.
    """
    from background import gap_register_scan

    dirty = _write(tmp_path / "census.json",
                   json.dumps(_clean_census(clone_count=999)))
    assert c.census_register_open(dirty), "fixture must actually be OPEN"

    monkeypatch.setattr(gap_register_scan, "_REGISTERS", {
        "shared_primitive_census": gap_register_scan._REGISTERS[
            "shared_primitive_census"],
    })
    assert gap_register_scan.gap_register_open(
        {"shared_primitive_census": dirty}) is True


def test_clean_census_alone_does_not_manufacture_work(tmp_path, monkeypatch):
    """The other half of R15: the control must also be able to read CLOSED.

    A register that is OPEN unconditionally is as useless as one that is never
    OPEN -- it would make `gap_register_open` a constant.
    """
    from background import gap_register_scan

    clean = _write(tmp_path / "census.json", json.dumps(_clean_census()))
    assert c.census_register_open(clean) == []

    monkeypatch.setattr(gap_register_scan, "_REGISTERS", {
        "shared_primitive_census": gap_register_scan._REGISTERS[
            "shared_primitive_census"],
    })
    assert gap_register_scan.gap_register_open(
        {"shared_primitive_census": clean}) is False


def test_missing_census_reaches_the_reader_as_open_not_absent(
    tmp_path, monkeypatch
):
    """FAIL-SILENT guard at the SEAM, not just inside the census module.

    An unavailable check is a FAILED check. If the census artefact is missing,
    the gap-register reader must see an OPEN `unreadable` row -- never an empty
    register that reads as "nothing to do".
    """
    from background import gap_register_scan

    monkeypatch.setattr(gap_register_scan, "_REGISTERS", {
        "shared_primitive_census": gap_register_scan._REGISTERS[
            "shared_primitive_census"],
    })
    residue = gap_register_scan.open_residue(
        {"shared_primitive_census": tmp_path / "does_not_exist.json"})
    rows = residue["shared_primitive_census"]
    assert rows and rows[0]["id"] == "unreadable"
    assert gap_register_scan.gap_register_open(
        {"shared_primitive_census": tmp_path / "does_not_exist.json"}) is True


# --------------------------------------------------------------------------- 5.3/5.4 the standing
# review itself, R15 both ways. Without these the review is an exhortation in a checklist: a session
# that never runs it leaves no trace and the register reads CLOSED anyway.
def test_never_recorded_standing_review_reads_open(tmp_path):
    """MUTATION: drop the review stamp from an otherwise-perfect census -> the register must OPEN.
    This is the control that makes 'nobody ever ran the standing review' visible as WORK rather
    than as silence."""
    data = _clean_census()
    del data[c.REVIEW_STAMP_KEY]
    p = _write(tmp_path / "census.json", json.dumps(data))
    rows = c.census_register_open(p)
    assert [r["id"] for r in rows] == ["standing_review_never_recorded"], rows
    # RESTORE: put the stamp back -> the row closes on its own merits, not by omission.
    assert c.census_register_open(_write(tmp_path / "b.json", json.dumps(_clean_census()))) == []


def test_null_review_stamp_is_not_a_valid_review(tmp_path):
    """`generate()` carries forward a null stamp when no review has ever run -- a null must read
    OPEN exactly like an absent key, never as 'present therefore fine'."""
    p = _write(tmp_path / "census.json", json.dumps(_clean_census(**{c.REVIEW_STAMP_KEY: None})))
    assert [r["id"] for r in c.census_register_open(p)] == ["standing_review_never_recorded"]


def test_stale_standing_review_reads_open(tmp_path):
    """A review that happened once, long ago, is not a STANDING activity. Past the retro cadence's
    own threshold it must re-open -- the same 'unmeasured is not evidence of no drift' rule the
    census staleness check already applies to itself."""
    threshold = c._stale_days_threshold()
    old = (datetime.now(timezone.utc) - timedelta(days=threshold + 3)).date().isoformat()
    stamp = {"date": old, "evaluator": "phase-close-evaluator", "verdict": "pass",
             "subject": "shared_primitive_census_old"}
    p = _write(tmp_path / "census.json", json.dumps(_clean_census(**{c.REVIEW_STAMP_KEY: stamp})))
    rows = c.census_register_open(p)
    assert [r["id"] for r in rows] == ["standing_review_overdue"], rows
    # RESTORE: a review inside the window closes it.
    fresh = dict(stamp, date=(datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat())
    assert c.census_register_open(
        _write(tmp_path / "b.json", json.dumps(_clean_census(**{c.REVIEW_STAMP_KEY: fresh})))) == []


def test_needs_work_verdict_keeps_the_register_open(tmp_path):
    """5.4 step (iii): a NEEDS_WORK verdict's named drifted items are OPEN work. A fresh review that
    FAILED must not close the register just because it is recent."""
    stamp = {"date": datetime.now(timezone.utc).date().isoformat(),
             "evaluator": "phase-close-evaluator", "verdict": "needs_work", "subject": "s"}
    p = _write(tmp_path / "census.json", json.dumps(_clean_census(**{c.REVIEW_STAMP_KEY: stamp})))
    assert [r["id"] for r in c.census_register_open(p)] == ["standing_review_needs_work"]


def test_malformed_review_stamp_fails_safe_open(tmp_path):
    for bad in ({"date": "2026-08-01"}, {"date": "not-a-date", "evaluator": "e", "verdict": "pass",
                                         "subject": "s"}):
        p = _write(tmp_path / f"c{abs(hash(str(bad)))}.json",
                   json.dumps(_clean_census(**{c.REVIEW_STAMP_KEY: bad})))
        rows = c.census_register_open(p)
        assert rows and rows[0]["id"] == "standing_review_malformed", (bad, rows)


def test_generate_carries_a_review_forward_but_never_fabricates_one(tmp_path):
    """TAUTOLOGY guard on the carry-forward: regenerating the census must preserve a review that
    really happened (with its OWN date, so freshness is still judged honestly) and must NOT invent
    one when the prior census has none -- otherwise the act of regenerating would silently close
    the row the review is supposed to hold open."""
    src = tmp_path / "proj"
    (src / "company").mkdir(parents=True)
    stamp = {"date": "2026-07-30", "evaluator": "phase-close-evaluator", "verdict": "pass",
             "subject": "shared_primitive_census_2026-07-30"}
    prev = _write(tmp_path / "prev.json", json.dumps(_clean_census(**{c.REVIEW_STAMP_KEY: stamp})))
    carried = c.generate(project_dir=src, previous_census_path=prev)
    assert carried[c.REVIEW_STAMP_KEY] == stamp, "a real review must survive regeneration"

    no_prev = c.generate(project_dir=src, previous_census_path=tmp_path / "absent.json")
    assert no_prev[c.REVIEW_STAMP_KEY] is None, "regeneration must never fabricate a review"


def test_record_standing_review_refuses_without_an_independent_verdict(tmp_path, monkeypatch):
    """The load-bearing 5.4 control: the census may NOT certify its own review. With an empty trust
    ledger (no fresh-context evaluator ever filed a verdict), the stamp is REFUSED."""
    from background import trust_ledger as tl

    monkeypatch.setattr(tl, "LEDGER_PATH", _write(tmp_path / "ledger.json", "[]"))
    p = _write(tmp_path / "census.json", json.dumps(_clean_census()))
    with pytest.raises(ValueError, match="no trust-ledger verdict"):
        c.record_standing_review("subj-1", "pass", "phase-close-evaluator", path=p)


def test_record_standing_review_accepts_a_real_recorded_verdict(tmp_path, monkeypatch):
    """RESTORE side: once the fresh-context evaluator's verdict IS in the ledger, the stamp lands
    and the register's review row closes. Both states are reachable -- the control is not
    unconditionally-refusing theatre."""
    from background import trust_ledger as tl

    monkeypatch.setattr(tl, "LEDGER_PATH", _write(tmp_path / "ledger.json", json.dumps([{
        "task_class": "harness_supervisor", "verdict": "pass",
        "evaluator_name": "phase-close-evaluator",
        "evaluated_at": datetime.now(timezone.utc).date().isoformat(),
        "subject": "subj-1", "defects_found_post_close": 0, "rework_required": False, "notes": "",
    }])))
    data = _clean_census()
    del data[c.REVIEW_STAMP_KEY]
    p = _write(tmp_path / "census.json", json.dumps(data))
    assert c.census_register_open(p), "precondition: the register is OPEN before the review"

    stamp = c.record_standing_review("subj-1", "pass", "phase-close-evaluator", path=p)
    assert stamp["evaluator"] == "phase-close-evaluator"
    assert c.census_register_open(p) == [], "a properly-recorded review closes the row"


def test_record_standing_review_refuses_a_non_whitelisted_evaluator(tmp_path, monkeypatch):
    """A self-reported grader name cannot appear in the ledger at all (trust_ledger's own
    INDEPENDENT_EVALUATORS whitelist), so no matching entry exists and the stamp is refused. The
    building session cannot route around 5.4 by naming itself the evaluator."""
    from background import trust_ledger as tl

    monkeypatch.setattr(tl, "LEDGER_PATH", _write(tmp_path / "ledger.json", "[]"))
    with pytest.raises(ValueError):
        tl.record_verdict(tl.TaskClass.HARNESS_SUPERVISOR, tl.Verdict.PASS,
                          "the-session-that-built-it", "subj-1")
    p = _write(tmp_path / "census.json", json.dumps(_clean_census()))
    with pytest.raises(ValueError, match="no trust-ledger verdict"):
        c.record_standing_review("subj-1", "pass", "the-session-that-built-it", path=p)


def test_record_standing_review_refuses_when_the_ledger_is_unavailable(tmp_path, monkeypatch):
    """FAIL-SILENT guard: an unavailable independence check is a FAILED independence check. The
    stamp must be REFUSED, never written optimistically."""
    from background import trust_ledger as tl

    def _boom():
        raise OSError("ledger unavailable")

    monkeypatch.setattr(tl, "_load_ledger", _boom)
    p = _write(tmp_path / "census.json", json.dumps(_clean_census()))
    with pytest.raises(RuntimeError, match="trust ledger unavailable"):
        c.record_standing_review("subj-1", "pass", "phase-close-evaluator", path=p)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
