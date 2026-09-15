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
from tools import maturity_map_store as map_store  # noqa: E402

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


# ---------------------------------------------------------------------------
# The OTHER spelling of the same tree (delivery seat, 2026-09-15)
# ---------------------------------------------------------------------------
def _module(tmp_path, name: str, body: str):
    d = tmp_path / "tools"
    d.mkdir(exist_ok=True)
    (d / name).write_text(body, encoding="utf-8")


def test_MUTATION_a_path_spelled_as_ONE_WHOLE_STRING_is_generated(tmp_path):
    """THE DEFECT: the matcher wanted `docs` and `observability` as SEPARATE constants in one
    assignment, so `tools/canon_drift_check.py`'s `DEFAULT_REPORT =
    "docs/observability/canon_drift.json"` was invisible while its artefact sat squarely inside a
    GENERATED_TREES member. Restoring the segment-pair-only matcher makes this RAISE
    (nothing found at all), which is how the mutation was proven rather than assumed."""
    _module(tmp_path, "drift.py",
            'from pathlib import Path\n'
            'ROOT = Path(__file__).resolve().parents[1]\n'
            'DEFAULT_REPORT = "docs/observability/canon_drift.json"\n')
    assert fs.generated_artefacts(root=tmp_path) == {"docs/observability/canon_drift.json"}


def test_a_loose_constant_naming_SOMEBODY_ELSES_artefact_is_not_swept(tmp_path):
    """THE SCOPE IS THE DISTINCTION, and it is measured rather than inherited. An ASSIGNMENT is
    where a module names its own destination; a constant in a `for rel in (...)` that the body
    then READS is where it names an artefact belonging to somebody else --
    `knowledge_layer_gate.orphan_research` is the live instance. Widening to every string constant
    also sweeps PROSE (`"site/data/customers.json + site/data/dashboard.json"` is a real constant
    in this tree), so this control holds the boundary in both directions at once."""
    _module(tmp_path, "gateish.py",
            'from pathlib import Path\n'
            'PROJECT = Path(__file__).resolve().parents[1]\n'
            'ARTEFACT = "docs/observability/mine.json"\n'
            'def read_them():\n'
            '    for rel in ("site/data/not_mine.json", "site/data/nor_this.json"):\n'
            '        (PROJECT / rel).read_text()\n')
    found = fs.generated_artefacts(root=tmp_path)
    assert found == {"docs/observability/mine.json"}


def test_MUTATION_the_gates_OWN_freeze_list_is_not_evidence_about_itself(monkeypatch, tmp_path):
    """CIRCULARITY, and it is the reason `_SELF` exists. `FROZEN` holds `(atom_id, file_scope)`
    pairs COPIED OUT OF THE MATURITY MAP -- the declarations this gate judges. Read back as
    constants they make four map declarations prove that the ground they name is generated, so
    `violations()` would agree with the map by construction and a frozen entry would keep itself
    alive. Both legs are driven: with `_SELF` pointed elsewhere the fixture's freeze path IS read
    (so the control cannot pass by the fixture simply missing the matcher), and with `_SELF`
    pointed at it, it is not."""
    _module(tmp_path, "gate_with_a_freeze.py",
            'FROZEN = frozenset({\n'
            '    ("SOME_atom", "docs/observability/frozen_debt.json"),\n'
            '})\n')
    _module(tmp_path, "a_real_producer.py",
            'from pathlib import Path\n'
            'OUT = Path(__file__).resolve().parents[1] / "site" / "data" / "real.json"\n')

    assert "docs/observability/frozen_debt.json" in fs.generated_artefacts(root=tmp_path)

    monkeypatch.setattr(fs, "_SELF", (tmp_path / "tools" / "gate_with_a_freeze.py").resolve())
    found = fs.generated_artefacts(root=tmp_path)
    assert found == {"site/data/real.json"}, (
        "the gate read its own freeze list as a producer's evidence -- an atom's declaration "
        "proving the ground it stands on is generated"
    )


def test_the_gate_half_is_SUBSUMED_by_the_prefix_test_and_the_docstring_says_so(monkeypatch):
    """A PROPERTY, NOT TODAY'S ANSWER, and the claim it guards is load-bearing prose. The drawn
    item said a path this oracle cannot see is a `file_scope` entry that silently starves its
    atom. It is not: `offends()` decides every entry under a generated-tree PREFIX without
    consulting the set at all, and every member this oracle can return is under one -- so
    `gate_violations()` cannot move however wide the oracle gets, and the consumer that DOES move
    is `origin_reconcile`'s exact-membership union. If a GENERATED_TREES entry or `offends` ever
    changes so that membership stops being subsumed, this goes red and the docstring above is
    stale -- which is the only way that sentence can be kept honest."""
    found = fs.generated_artefacts()
    escaping = sorted(p for p in found if not fs.offends(p, set()))
    assert escaping == [], (
        f"{len(escaping)} oracle members are no longer caught by the prefix test alone "
        f"({escaping[:3]}), so widening the oracle now CAN move the commit gate and the frozen "
        "debt list must be re-measured against the wider set"
    )


def test_the_repaired_instance_stays_repaired():
    """G13 is the atom this class fix was extracted from. Asserts the PROPERTY (no generated
    ground in its scope) rather than the exact path list, so a legitimate scope edit does not
    fail here while a regression to `site/data/` does."""
    import yaml
    loaded = map_store.load_atoms(fs.MAP_PATH)
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
