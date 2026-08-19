#!/usr/bin/env python3
"""R15 proof for the generated-path file_scope gate (class fix for the G13 starvation).

The control's job is to make one declaration impossible: an atom claiming ground a generator
rewrites, which makes it permanently invisible to its own build lane. So the mutations drive
that boundary from both sides -- generated ground offends, authored source does not -- and the
ratchet is driven in both directions, because a freeze that can only grow is a place debt goes
to be forgotten.

The fail-closed direction is toward RAISING. The tempting failure here is very quiet: if the
oracle finds nothing, no scope entry matches anything, `violations()` returns `[]`, and the gate
prints a clean tree. That is the FAIL-OPEN killer pattern exactly -- a passing result computed
from evidence nobody could read -- so both empty-oracle paths are tested to raise.
"""
from __future__ import annotations

import pytest

from tools import file_scope_generated_paths as fs

GENERATED = {"site/data/dashboard.json", "site/data/glossary.json"}


# ---------------------------------------------------------------------------
# The predicate: what counts as generated ground
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("entry", [
    "site/data/dashboard.json",   # the artefact itself
    "site/data/",                 # the directory, with a slash   (G13's actual declaration)
    "site/data",                  # the directory, without one    (H14's actual declaration)
    "docs/observability/",
    "docs/observability/scale_probe_10k/report.json",   # nested below the tree
])
def test_MUTATION_every_shape_of_generated_ground_offends(entry):
    """All three shapes are LIVE in the map today; a gate catching only the tidy one would have
    missed G13, which is the case it exists for."""
    assert fs.offends(entry, GENERATED)


@pytest.mark.parametrize("entry", [
    "tools/lab_query.py",
    "tests/tools/test_lab_query.py",
    "company/analytics/clv_three_horizon.py",
    "site/index.html",              # site/, but not site/data/
    "docs/design/maturity_map.yaml",  # docs/, but not a generated tree
])
def test_authored_source_does_NOT_offend(entry):
    """The other side of the boundary. A gate that flags ordinary source gets disabled, and a
    disabled gate is how the eight-day starvation happens again."""
    assert not fs.offends(entry, GENERATED)


# ---------------------------------------------------------------------------
# The ratchet: both directions
# ---------------------------------------------------------------------------
def test_MUTATION_a_new_declaration_fails_the_commit(monkeypatch):
    monkeypatch.setattr(fs, "violations",
                        lambda root=None: sorted(fs.FROZEN | {("NEW_atom", "site/data/x.json")}))
    problems = fs.gate_violations()
    assert len(problems) == 1
    assert problems[0].startswith("NEW: NEW_atom")
    assert "never be drawn" in problems[0]


def test_MUTATION_a_repaired_declaration_ALSO_fails_so_the_freeze_can_only_shrink(monkeypatch):
    """The direction people forget. If a repair does not force the freeze to shrink, the list
    silently becomes a permanent amnesty and the gate stops meaning anything."""
    frozen = sorted(fs.FROZEN)
    monkeypatch.setattr(fs, "violations", lambda root=None: frozen[1:])
    problems = fs.gate_violations()
    assert len(problems) == 1 and problems[0].startswith("STALE FREEZE:")


def test_the_frozen_set_exactly_matches_the_live_map(monkeypatch):
    """The ratchet's resting state. Green today; goes red the moment either side moves, which
    is the whole point of freezing rather than ignoring."""
    assert fs.gate_violations() == []


# ---------------------------------------------------------------------------
# FAIL-CLOSED -- the quiet one
# ---------------------------------------------------------------------------
def test_MUTATION_FAIL_CLOSED_an_oracle_that_scans_nothing_raises(monkeypatch, tmp_path):
    """Nothing scanned -> nothing generated -> no scope matches -> a serene clean tree. That is
    the exact fail-open shape R15 names, and it must raise instead."""
    with pytest.raises(fs.OracleUnavailable):
        fs.generated_artefacts(root=tmp_path)


def test_MUTATION_FAIL_CLOSED_an_oracle_that_finds_zero_artefacts_raises(monkeypatch, tmp_path):
    """Modules present, no artefacts found -- a plausible outcome of a refactor that changes how
    output paths are built. This project publishes a site from generated JSON, so zero is a
    broken oracle rather than good news, and the message says which."""
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "x.py").write_text("A = 1\n")
    with pytest.raises(fs.OracleUnavailable) as exc:
        fs.generated_artefacts(root=tmp_path)
    assert "broken oracle" in str(exc.value)


def test_MUTATION_FAIL_CLOSED_an_unreadable_map_raises(monkeypatch, tmp_path):
    monkeypatch.setattr(fs, "generated_artefacts", lambda root=None: GENERATED)
    with pytest.raises(fs.OracleUnavailable):
        fs.violations(root=tmp_path)


# ---------------------------------------------------------------------------
# The live tree
# ---------------------------------------------------------------------------
def test_the_oracle_finds_the_real_generated_artefacts():
    """Asserts the oracle's REACH, not a count. Pinning 116 would go red on the next generator
    added -- the pinned-literal defect this project found four times this week."""
    found = fs.generated_artefacts()
    assert len(found) > 50, "the segment-join oracle has lost its reach"
    assert any(p.startswith("site/data/") for p in found)
    assert any(p.startswith("docs/observability/") for p in found)


def test_the_repaired_instance_stays_repaired():
    """G13 is the atom this class fix was extracted from. Asserts the PROPERTY (no generated
    ground in its scope) rather than the exact path list, so a legitimate scope edit does not
    fail here while a regression to `site/data/` does."""
    import yaml
    loaded = yaml.safe_load(fs.MAP_PATH.read_text(encoding="utf-8"))
    atoms = loaded if isinstance(loaded, list) else (loaded or {}).get("atoms", [])
    g13 = next(a for a in atoms
               if isinstance(a, dict) and a.get("id") == "G13_projection_consumers")
    generated = fs.generated_artefacts()
    offending = [s for s in (g13.get("file_scope") or []) if fs.offends(s, generated)]
    assert offending == [], (
        f"G13 has regressed onto generated ground ({offending}) -- it will stop being drawn "
        "again, silently, exactly as it did for the eight days before 2026-08-19"
    )
    assert g13.get("file_scope"), "G13 now has an EMPTY file_scope, which starves it differently"
