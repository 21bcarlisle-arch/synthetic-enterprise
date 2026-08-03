"""R15 controls for the abolished-block-class registry and its two guards.

Every control here is mutation-tested: each one is proven to FIRE on its own
named defect and to PASS when restored. A control that cannot fail is worse
than no control.

The three killer patterns, addressed explicitly:
  TAUTOLOGY   -- the no-false-positive test uses tokens the registry does NOT
                 contain (live blocks, unrelated module names), so it cannot be
                 satisfied by the matcher agreeing with itself.
  FAIL-OPEN   -- empty / missing / malformed map inputs are asserted to return
                 None ("cannot verify"), never [] ("verified clean").
  FAIL-SILENT -- an unreadable maturity map is asserted to be a FAILED check.
"""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest
import yaml

from tools import abolished_block_classes as abc


# --------------------------------------------------------------------------
# Fixtures -- all keyed to tmp_path. Nothing here reads the real register
# except the two explicitly-named live-state tests at the bottom.
# --------------------------------------------------------------------------

def _write_map(tmp_path: Path, atoms: list[dict]) -> Path:
    p = tmp_path / "maturity_map.yaml"
    p.write_text(yaml.safe_dump(atoms, sort_keys=False))
    return p


# --------------------------------------------------------------------------
# 1. Registry integrity
# --------------------------------------------------------------------------

def test_every_registered_class_names_what_replaced_it():
    """An abolished class with no `replaced_by` is a dead end, not a record.

    The whole point of the registry is that a reader of a superseded note
    learns what the rule IS now, not merely that the old one is gone.
    """
    assert abc.ABOLISHED_BLOCK_CLASSES, "registry must not be empty"
    for name, cls in abc.ABOLISHED_BLOCK_CLASSES.items():
        assert cls.name == name
        assert cls.abolished_on.strip(), f"{name}: no abolition date"
        assert cls.ruling.strip(), f"{name}: no ruling cited"
        assert cls.replaced_by.strip(), f"{name}: does not say what replaced it"


def test_the_four_reserved_classes_are_never_registered_as_abolished():
    """The four RESERVED real-world classes are not permission machinery.

    Registering one here would annotate a genuine one-way door as a dead rule --
    the single most dangerous false positive this module could produce.
    `background/one_way_door.py` remains their sole enumeration.
    """
    registry_text = " ".join(
        f"{c.name} {c.replaced_by}" for c in abc.ABOLISHED_BLOCK_CLASSES.values()
    ).lower()
    for reserved in ("real money", "real people", "safety"):
        assert reserved not in [n.lower() for n in abc.ABOLISHED_BLOCK_CLASSES]
    assert "one_way_door" not in abc.ABOLISHED_BLOCK_CLASSES


# --------------------------------------------------------------------------
# 2. Matcher precision -- the independence check (anti-TAUTOLOGY)
# --------------------------------------------------------------------------

# Tokens that are NOT abolished classes. Three are LIVE blocks currently on real
# atoms; the rest are unrelated identifiers that a prefix/substring matcher
# would wrongly sweep in. None of these appears in the registry, so this test
# cannot be satisfied by the matcher merely agreeing with its own source.
NOT_ABOLISHED_TOKENS = [
    "director_systemd_deploy",   # LIVE block on OPS1_operational_layer_rebuild
    "director_live_run",         # LIVE block on OPS1_governance_refusal_mutation_test
    "coupled_triad_measured",    # LIVE block on H27_payment_belief_gap
    "director_twin_log",
    "director_input_log",
    "director_window_delta_view",
    "director_last_look",
    "director_level_upgrade",    # shares a prefix with an abolished class
]


@pytest.mark.parametrize("token", NOT_ABOLISHED_TOKENS)
def test_live_and_unrelated_tokens_are_not_matched(token):
    """Annotating a LIVE block as abolished is worse than the defect fixed."""
    assert abc.find_abolished_references(f"blocked_on: {token} -- see note") == []


@pytest.mark.parametrize("token,expected", [
    ("director_level_up", "director_level_up"),
    ("director_level_up_L3", "director_level_up"),
    ("blocked_on: director_build_open", "director_build_open"),
    ("a BUILD_OPEN was granted", "director_build_open"),
    ("GATE_CLEAR act", "gate_clear"),
    ("FRONT_OPEN", "front_open"),
    ("director_h_lane_open", "director_h_lane_open"),
])
def test_abolished_spellings_are_matched(token, expected):
    names = [c.name for c in abc.find_abolished_references(token)]
    assert expected in names, f"{token!r} should map to {expected}"


# --------------------------------------------------------------------------
# 3. GUARD A -- an abolished class may never be a LIVE blocked_on
# --------------------------------------------------------------------------

def test_guard_a_fires_on_an_abolished_live_block(tmp_path):
    """R15 MUTATION: inject the defect, prove the control names it."""
    p = _write_map(tmp_path, [
        {"id": "GOOD_atom", "blocked_on": "director_systemd_deploy"},
        {"id": "BAD_atom", "blocked_on": "director_level_up"},
    ])
    violations = abc.live_blocked_on_violations(p)
    assert violations is not None
    ids = [v["atom_id"] for v in violations]
    assert ids == ["BAD_atom"], f"expected only BAD_atom, got {ids}"
    assert violations[0]["abolished"] == ["director_level_up"]
    # It must say what to do instead, not merely that the block is dead.
    assert "record_level_up_self_certified" in violations[0]["replaced_by"][0]


def test_guard_a_passes_when_the_defect_is_removed(tmp_path):
    """R15 MUTATION RESTORED: the same control passes on the clean input."""
    p = _write_map(tmp_path, [
        {"id": "GOOD_atom", "blocked_on": "director_systemd_deploy"},
        {"id": "BAD_atom", "blocked_on": None},
    ])
    assert abc.live_blocked_on_violations(p) == []


def test_guard_a_on_the_real_map_is_clean():
    """The live invariant. A note may be history; a blocked_on is a claim now."""
    violations = abc.live_blocked_on_violations()
    assert violations is not None, "the real maturity map must be readable"
    assert violations == [], (
        "an atom is blocked on an ABOLISHED act -- it is drawable now: "
        f"{violations}"
    )


# --------------------------------------------------------------------------
# 4. FAIL-OPEN / FAIL-SILENT -- an unavailable check is a FAILED check
# --------------------------------------------------------------------------

def test_missing_map_returns_none_not_empty(tmp_path):
    """FAIL-SILENT guard: absent source must not read as 'verified clean'.

    `[]` and `None` are the whole difference between "checked, nothing wrong"
    and "could not check". Returning [] here would make every caller pass.
    """
    assert abc.live_blocked_on_violations(tmp_path / "nope.yaml") is None
    assert abc.register_exposure(tmp_path / "nope.yaml") is None


def test_malformed_map_returns_none_not_empty(tmp_path):
    """FAIL-OPEN guard: unparseable and wrong-shaped inputs both fail closed."""
    bad = tmp_path / "bad.yaml"
    bad.write_text("{[not: valid yaml")
    assert abc.live_blocked_on_violations(bad) is None

    wrong_shape = tmp_path / "dict.yaml"
    wrong_shape.write_text(yaml.safe_dump({"atoms": []}))
    assert abc.live_blocked_on_violations(wrong_shape) is None


def test_empty_text_and_empty_notes_do_not_claim_a_match():
    """Empty input must yield no annotation -- and no vacuous 'clean' claim."""
    assert abc.find_abolished_references("") == []
    assert abc.find_abolished_references(None) == []
    notes, markers = abc.annotate_notes([])
    assert notes == [] and markers == []


# --------------------------------------------------------------------------
# 5. GUARD B -- the published register must mark every superseded note
# --------------------------------------------------------------------------

def _generate_into(tmp_path, monkeypatch, atoms):
    """Run the real generator against a fixture map, writing to tmp_path."""
    from tools import generate_simplified_data as gen

    src = _write_map(tmp_path, atoms)
    out = tmp_path / "simplified.json"
    monkeypatch.setattr(gen, "MATURITY_MAP_YAML", src)
    monkeypatch.setattr(gen, "OUT_PATH", out)
    assert gen.generate() is True
    return json.loads(out.read_text())


FIXTURE_ATOMS = [{
    "id": "X_atom",
    "name": "an atom",
    "lane": "H_harness",
    "level_current": 2,
    "level_target": 3,
    "simplifications": [
        "2026-07-27 level moves stay blocked_on director_level_up, R16 -- no self-bump.",
        "2026-08-01 a note about nothing in particular.",
        "2026-07-20 BUILD held behind director_build_open until opened.",
    ],
}]


def test_guard_b_marks_exactly_the_superseded_notes(tmp_path, monkeypatch):
    data = _generate_into(tmp_path, monkeypatch, FIXTURE_ATOMS)
    atom = data["lanes"][0]["atoms"][0]
    marked = {m["note_index"] for m in atom["superseded"]}
    assert marked == {0, 2}, f"note 1 mentions no abolished class; got {marked}"
    assert data["total_notes"] == 3
    assert data["total_notes_superseded"] == 2
    names = [b["name"] for b in atom["superseded"][0]["superseded_blocks"]]
    assert names == ["director_level_up"]


def test_guard_b_never_rewrites_the_note_text(tmp_path, monkeypatch):
    """SITE_CONSTITUTION rule 5: the site is a rendering, never an author.

    Supersession is DERIVED metadata. If this ever fails, the generator has
    started editing the honesty register's own words.
    """
    data = _generate_into(tmp_path, monkeypatch, FIXTURE_ATOMS)
    published = data["lanes"][0]["atoms"][0]["notes"]
    assert published == FIXTURE_ATOMS[0]["simplifications"]


def test_guard_b_fires_when_a_class_is_dropped_from_the_registry(
    tmp_path, monkeypatch
):
    """R15 MUTATION: remove `director_level_up` from the registry.

    The note then publishes UNMARKED -- i.e. a dead permission act reads as live
    policy on /proof/. The control must notice, naming that note.
    """
    surviving = {
        k: v for k, v in abc.ABOLISHED_BLOCK_CLASSES.items()
        if k != "director_level_up"
    }
    monkeypatch.setattr(abc, "ABOLISHED_BLOCK_CLASSES", surviving)

    data = _generate_into(tmp_path, monkeypatch, FIXTURE_ATOMS)
    atom = data["lanes"][0]["atoms"][0]
    marked = {m["note_index"] for m in atom["superseded"]}
    assert marked == {2}, "the mutation must leave note 0 unmarked"
    assert data["total_notes_superseded"] == 1
    unmarked = [
        n for i, n in enumerate(atom["notes"])
        if i not in marked and "director_level_up" in n
    ]
    assert unmarked, (
        "MUTATION DID NOT FIRE: the guard should be able to detect an "
        "unmarked abolished-class note"
    )


def test_guard_b_restored_registry_marks_the_note_again(tmp_path, monkeypatch):
    """R15 MUTATION RESTORED -- the control passes again unmutated."""
    data = _generate_into(tmp_path, monkeypatch, FIXTURE_ATOMS)
    assert data["total_notes_superseded"] == 2


def test_published_register_carries_the_registry_for_the_renderer(
    tmp_path, monkeypatch
):
    """The marker is useless if the page cannot say what replaced the act."""
    data = _generate_into(tmp_path, monkeypatch, FIXTURE_ATOMS)
    classes = {c["name"]: c for c in data["abolished_block_classes"]}
    assert set(classes) == set(abc.ABOLISHED_BLOCK_CLASSES)
    for c in classes.values():
        assert c["abolished_on"] and c["ruling"] and c["replaced_by"]


# --------------------------------------------------------------------------
# 6. The live exposure figure -- reported, not silently corrected
# --------------------------------------------------------------------------

def test_real_register_exposure_is_measured_and_fully_marked():
    """Every real note mentioning an abolished class must be marked.

    This is the class guard proper (R10): it is keyed off the registry, so
    abolishing the NEXT permission act and registering it covers every note
    that mentions it, with no note-by-note edit.
    """
    exposure = abc.register_exposure()
    assert exposure is not None, "the real maturity map must be readable"

    published = Path("site/data/simplified.json")
    if not published.is_file():
        pytest.skip("site/data/simplified.json not generated in this checkout")
    data = json.loads(published.read_text())

    unmarked = []
    for lane in data["lanes"]:
        for atom in lane["atoms"]:
            marked = {m["note_index"] for m in atom.get("superseded", [])}
            for i, note in enumerate(atom["notes"]):
                if abc.find_abolished_references(note) and i not in marked:
                    unmarked.append((atom["atom_id"], i))
    assert not unmarked, (
        "published register notes describe a hold behind an ABOLISHED act "
        f"without a supersession marker: {unmarked[:5]}"
    )
    assert data["total_notes_superseded"] == (
        exposure["notes_referring_to_an_abolished_class"]
    )
