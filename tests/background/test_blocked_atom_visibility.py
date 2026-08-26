"""FUT3 -- tests for `background/blocked_atom_visibility.py`.

R15 governs the shape of this file. The module is a CONTROL asserting a three-way visibility
property, so most of what follows is proof that it can FAIL: each of its findings is driven red by
a mutation, and each refusal test is preceded by an assertion that the honest path is green
(otherwise a permanently-red control would look like a working one).

The tautology killer is `test_the_draw_verdict_follows_the_draw`: the draw itself is mutated and
the module's verdict must move with it. A module that re-read `loop_stage` for itself would keep
reporting EXCLUDED while the draw handed the atom out.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from background import blocked_atom_visibility as bav
from background import supervisor

REPO = Path(__file__).resolve().parents[2]


def _atom(atom_id: str, **over) -> dict:
    """A minimal drawable atom. H_harness / target 2 on purpose: the coupled-triad gate only bites
    world atoms stepping to L3, and this fixture is about the park, not that gate."""
    base = {
        "id": atom_id,
        "title": atom_id,
        "lane": "H_harness",
        "level_current": 0,
        "level_target": 2,
        "loop_stage": "build",
        "dial_inherited": 3,
        "depends_on": [],
        "file_scope": [],
    }
    base.update(over)
    return base


def _map(*atoms: dict) -> list[dict]:
    """Pad to the vacuity floor with atoms that are already at target, so they are never drawn and
    never parked -- the padding must not be able to change any verdict."""
    filler = [
        _atom("FILLER_%03d" % i, level_current=2, level_target=2, lane="D_billing_metering")
        for i in range(bav.ATOM_FLOOR + 5 - len(atoms))
    ]
    return list(atoms) + filler


# ---------------------------------------------------------------------------
# Vacuity -- an empty population is a failed measurement, never a clean one
# ---------------------------------------------------------------------------

def test_a_short_map_raises_rather_than_reading_as_clean(tmp_path):
    short = tmp_path / "m.yaml"
    short.write_text(yaml.safe_dump([_atom("ONLY")]), encoding="utf-8")
    with pytest.raises(bav.ProbeUnavailable, match="floor"):
        bav.load_atoms(short)


def test_an_unreadable_map_raises(tmp_path):
    with pytest.raises(bav.ProbeUnavailable, match="unreadable"):
        bav.load_atoms(tmp_path / "does_not_exist.yaml")


def test_zero_parked_atoms_raises_because_it_is_indistinguishable_from_a_broken_filter():
    atoms = _map(_atom("A"), _atom("B"))
    assert not any(bav.is_parked(a) for a in atoms)
    with pytest.raises(bav.ProbeUnavailable, match="zero parked atoms"):
        bav.parked_atoms(atoms)


def test_the_park_is_loop_stage_not_block_reason():
    """Ten atoms on the live map carry a `block_reason` while being actively built. Keying the
    parked set on that field would misreport every one of them as blocked."""
    built_but_annotated = _atom("BUILT", loop_stage="build", block_reason="a note about a gate")
    parked = _atom("PARKED", loop_stage="idle")
    assert bav.is_parked(built_but_annotated) is False
    assert bav.is_parked(parked) is True


# ---------------------------------------------------------------------------
# Property 1 -- the draw, proven BOTH ways
# ---------------------------------------------------------------------------

def test_the_park_is_what_excludes_the_atom_from_the_draw():
    atoms = _map(_atom("PARKED", loop_stage="idle"))
    assert bav.park_exclusion_status(atoms) == {"PARKED": bav.EXCLUDED_BY_PARK}


def test_the_vacuity_control_lifting_the_park_makes_the_same_atom_drawable():
    """The other half of the same claim: without this, "not drawn" could mean the fixture was
    never drawable in the first place."""
    atoms = _map(_atom("PARKED", loop_stage="idle"))
    control = [bav._unparked(atoms[0])] + atoms[1:]
    assert "PARKED" in bav.draw_offers(control)


def test_an_atom_excluded_for_another_reason_is_not_counted_as_proof_the_park_works():
    """An atom at its own target is undrawable regardless of the park. Reporting it as
    EXCLUDED_BY_PARK would inflate the proof count with atoms that prove nothing."""
    atoms = _map(_atom("AT_TARGET", loop_stage="idle", level_current=2, level_target=2))
    assert bav.park_exclusion_status(atoms) == {"AT_TARGET": bav.EXCLUDED_OTHERWISE}


def test_a_probe_where_nothing_is_attributable_to_the_park_reports_itself_vacuous():
    atoms = _map(_atom("AT_TARGET", loop_stage="idle", level_current=2, level_target=2))
    report = bav.build_report(atoms, probe_clocks=False)
    assert any("VACUOUS DRAW PROBE" in f for f in report.integrity_findings)


def test_the_dependencies_travel_with_the_probed_atom():
    """The draw's dependency gate returns False for a dependency it cannot find, so a lone atom
    with `depends_on` would be excluded by the FIXTURE rather than by the park -- and would then be
    silently misfiled as EXCLUDED_OTHERWISE."""
    dep = _atom("DEP", level_current=2, level_target=2)
    child = _atom("CHILD", loop_stage="idle", depends_on=["DEP"])
    atoms = _map(child, dep)
    assert bav.park_exclusion_status(atoms)["CHILD"] == bav.EXCLUDED_BY_PARK


def test_the_draw_verdict_follows_the_draw(monkeypatch):
    """TAUTOLOGY KILLER. Mutate the draw so it hands back everything it is given; the module's
    verdict must flip to DRAWN. A module that decided drawability from `loop_stage` itself would
    still report the atom excluded while the real draw was offering it."""
    atoms = _map(_atom("PARKED", loop_stage="idle"))
    assert bav.park_exclusion_status(atoms) == {"PARKED": bav.EXCLUDED_BY_PARK}

    def _draw_everything(rng=None, exclude_stalled=False):
        return yaml.safe_load(supervisor.MATURITY_MAP_PATH.read_text(encoding="utf-8"))

    monkeypatch.setattr(supervisor, "_maturity_map_draw_concurrent", _draw_everything)
    assert bav.park_exclusion_status(atoms) == {"PARKED": bav.DRAWN}


def test_a_parked_but_drawable_atom_is_a_finding(monkeypatch):
    atoms = _map(_atom("PARKED", loop_stage="idle"))
    monkeypatch.setattr(
        supervisor, "_maturity_map_draw_concurrent",
        lambda rng=None, exclude_stalled=False: yaml.safe_load(
            supervisor.MATURITY_MAP_PATH.read_text(encoding="utf-8")),
    )
    report = bav.build_report(atoms, probe_clocks=False)
    assert any("PARKED-BUT-DRAWABLE" in f for f in report.integrity_findings)


def test_the_probe_restores_the_supervisor_it_borrowed():
    """The probe repoints a production module's map path and stubs two of its live-state readers.
    Leaving any of that in place would corrupt the real draw for the rest of the process."""
    before = (supervisor.MATURITY_MAP_PATH,
              supervisor._build_in_progress_ids,
              supervisor._prefer_unmerged_free)
    bav.draw_offers(_map(_atom("PARKED", loop_stage="idle")))
    assert (supervisor.MATURITY_MAP_PATH,
            supervisor._build_in_progress_ids,
            supervisor._prefer_unmerged_free) == before


def test_the_probe_restores_the_supervisor_even_when_the_draw_raises(monkeypatch):
    before = supervisor.MATURITY_MAP_PATH

    def _boom(rng=None, exclude_stalled=False):
        raise RuntimeError("draw exploded")

    monkeypatch.setattr(supervisor, "_maturity_map_draw_concurrent", _boom)
    with pytest.raises(RuntimeError):
        bav.draw_offers(_map(_atom("PARKED", loop_stage="idle")))
    assert supervisor.MATURITY_MAP_PATH == before


# ---------------------------------------------------------------------------
# Property 2 -- the staleness clocks
# ---------------------------------------------------------------------------

def test_the_real_staleness_clocks_carry_a_row_for_every_parked_atom_on_the_live_map():
    """The ruling's actual claim, against the real map and AO11's own reader -- confirmed, not
    assumed. This is the assertion the atom's `origin_note` demanded: read the reader, not the draw."""
    atoms = bav.load_atoms()
    parked = {a["id"] for a in bav.parked_atoms(atoms)}
    assert parked, "vacuity: the live map has no parked atoms"
    visible = bav.clock_visible_ids(atoms)
    assert not (parked - visible)


def test_a_clock_reader_that_filtered_parked_atoms_would_be_caught(monkeypatch):
    """R15: the finding must be reachable. Give AO11 the drawability filter the origin_note feared
    it might share with the supervisor, and the check goes red."""
    atoms = _map(_atom("PARKED", loop_stage="idle"), _atom("BUILDING"))
    monkeypatch.setattr(
        bav, "clock_visible_ids",
        lambda atoms=None: {a["id"] for a in atoms if not bav.is_parked(a)},
    )
    report = bav.build_report(atoms, probe_draw=False)
    assert any("PARKED-AND-UNCLOCKED" in f for f in report.integrity_findings)


def test_an_empty_clock_report_raises_rather_than_reading_as_all_invisible(monkeypatch):
    sys.path.insert(0, str(REPO))
    from tools import map_assertion_provenance

    monkeypatch.setattr(map_assertion_provenance, "build_rows", lambda **kw: [])
    with pytest.raises(bav.ProbeUnavailable, match="no rows"):
        bav.clock_visible_ids(_map(_atom("PARKED", loop_stage="idle")))


def test_an_unavailable_clock_reader_is_a_failed_check_not_a_pass(monkeypatch):
    sys.path.insert(0, str(REPO))
    from tools import map_assertion_provenance

    def _boom(**kw):
        raise RuntimeError("git unavailable")

    monkeypatch.setattr(map_assertion_provenance, "build_rows", _boom)
    with pytest.raises(bav.ProbeUnavailable, match="build_rows failed"):
        bav.clock_visible_ids(_map(_atom("PARKED", loop_stage="idle")))


def test_a_skipped_probe_is_a_finding_not_a_silent_pass():
    atoms = _map(_atom("PARKED", loop_stage="idle"))
    report = bav.build_report(atoms, probe_draw=False, probe_clocks=False)
    assert any("DRAW PROBE NOT RUN" in f for f in report.integrity_findings)
    assert any("CLOCK PROBE NOT RUN" in f for f in report.integrity_findings)


# ---------------------------------------------------------------------------
# Property 3 -- the dial counts the parked atoms
# ---------------------------------------------------------------------------

def test_the_dial_counts_parked_atoms_and_a_park_filtering_reader_would_not():
    atoms = _map(_atom("PARKED", loop_stage="idle"), _atom("BUILDING"))
    report = bav.build_report(atoms, probe_draw=False, probe_clocks=False)
    assert report.lane_weights_all["H_harness"] == 2
    assert report.lane_weights_excluding_parked["H_harness"] == 1


# The live map's UNPARKED coverage of the ruling's three named subjects, frozen and dated.
#
# WHY THIS IS A CENSUS AND NOT A BARE `== []` (2026-08-17). It was `== []` for all three, and
# that is the one thing this measurement can never assert for long: `[]` encodes the DEFECT the
# ruling was written about (every atom on these subjects parked, so a park-filtering reader sees
# the zero the mint was made to fix), so the assertion turns RED the first time the map improves.
# It did, on 2026-08-15, when the SITE2 draw minted `W2_17_dual_fuel_leg_clv_attribution` --
# loop_stage `build`, `blocked_on: null`, a LIVE atom on `clv`. Good news, read as a failure, and
# it sat in the working tree as one of the reds holding the content publish frozen from
# 2026-08-14T07:04Z.
#
# Frozen rather than deleted, because the property is still load-bearing in BOTH directions: a
# NEW unparked atom on any of the three subjects reds this, and so does W2_17 going back to
# parked. Move an entry here only with the atom id that earned it and the date -- an empty list
# shrinking to a name is progress and must be recorded; a name growing back to `[]` is the
# regression this control exists to catch.
UNPARKED_SUBJECT_COVERAGE: dict[str, list[str]] = {
    "clv": [
        "W2_17_dual_fuel_leg_clv_attribution",  # 2026-08-15, SITE2 draw
        # 2026-08-19. Unparked by the map hunk swept into 02ada0701 (an H27 landing whose
        # pathspec carried three atom edits; see WORKER_FINDING_AN_EPOCH_3_CURRICULUM_BLOCK_
        # WAS_DISCHARGED_CITING_A_DIRECTOR_INSTRUCTION_WITH_NO_ARTEFACT_2026-08-19.md §1).
        # RECORDED, not reverted, and the distinction from EP6 is the whole point: EP1 is
        # EPOCH 2, whose gate is the RULED EPOCH2_EVIDENCE_PASS (docs/staging/done/), not a
        # director unblock -- 92 of 133 epoch-2 atoms are already unparked, and EP1's own
        # `block_reason` was empty, so nothing was crossed. EP6 was epoch 3 behind R13 and
        # WAS reverted. This entry is the ledger line this constant's docstring asks for.
        "EP1_clv_three_horizon",
    ],
    "counterparty_adapter": [
        # 2026-08-25. Unparked by the door, not around it, and the distinction from EP6 is again
        # the whole point: EP6 was an epoch-3 curriculum park discharged by a `block_reason_
        # discharged:` field citing an artefact that exists on no channel, and it WAS reverted.
        # This one names a real one and the artefact NAMES THE ATOM'S SUBJECT --
        # `docs/staging/DIRECTOR_CONSOLE_2026-08-25.md:264`, quoted in the map beside the cell:
        # "Wire the carbon ledger to live meter reads and grid intensity, publish it with its
        # provenance, and say plainly what it does and does not yet include." The park was
        # curriculum SEQUENCING (epoch-3 commitment set did not include it, pull-forward was
        # proposal-only), and being asked for the thing directly is exactly what a pull-forward
        # proposal exists to obtain -- so `block_reason` is null, `loop_stage` is `build`, and
        # the field is DELETED-to-null the way `apply_release` does it rather than renamed.
        "EP13_adapter_carbon_intensity",
    ],
    "forecast_feed": [],
}


def test_on_the_live_map_the_rulings_named_subjects_are_covered_and_their_unparked_set_is_frozen():
    """The load-bearing measurement, and the reason the visibility property is not decorative: the
    ruling's evidenced problem was ZERO atoms touching CLV, a counterparty adapter or a forecast
    feed. Every such subject must still be COVERED, and the subset a park-filtering reader can
    actually see must match `UNPARKED_SUBJECT_COVERAGE` exactly -- see that constant for why the
    parked-only half is a dated census rather than a bare zero."""
    report = bav.build_report(bav.load_atoms(), probe_draw=False, probe_clocks=False)
    for subject, expected in UNPARKED_SUBJECT_COVERAGE.items():
        assert report.subject_coverage_all[subject], subject
        assert sorted(report.subject_coverage_excluding_parked[subject]) == sorted(expected), (
            f"{subject}: a park-filtering reader now sees "
            f"{sorted(report.subject_coverage_excluding_parked[subject])}, frozen as "
            f"{sorted(expected)}. If an atom was unparked, record it in "
            "UNPARKED_SUBJECT_COVERAGE with its id and date; if one went back to parked, that is "
            "the regression this control exists to catch."
        )


def test_subject_coverage_is_matched_on_the_id_as_the_ruling_measured_it():
    atoms = _map(_atom("EPX_adapter_something", loop_stage="idle"),
                 _atom("SOMETHING_ELSE", title="this is all about clv really"))
    coverage = bav.subject_coverage(atoms)
    assert coverage["counterparty_adapter"] == ["EPX_adapter_something"]
    assert coverage["clv"] == []


# ---------------------------------------------------------------------------
# R12 -- measurability gates, the number never does
# ---------------------------------------------------------------------------

def test_a_lopsided_dial_is_reported_and_passes():
    """An all-harness map is the worst possible imbalance and still returns no finding. If the
    number could fail the check, the cheapest fix would be minting empty commercial atoms."""
    atoms = [_atom("PARKED", loop_stage="idle")] + [
        _atom("H_%03d" % i, level_current=2, level_target=2) for i in range(bav.ATOM_FLOOR + 4)
    ]
    report = bav.build_report(atoms, probe_clocks=False)
    assert report.harness_share == 100.0
    assert [f for f in report.integrity_findings if "harness" in f.lower()] == []


# ---------------------------------------------------------------------------
# The generated document
# ---------------------------------------------------------------------------

def test_check_fails_when_the_document_disagrees_with_the_derivation(tmp_path, monkeypatch):
    doc = tmp_path / "BLOCKED_ATOM_VISIBILITY.md"
    monkeypatch.setattr(bav, "DOC_PATH", doc)
    assert bav.main(["--write", "--no-clock-probe"]) == 0
    assert bav.main(["--check", "--no-clock-probe"]) == 2  # the skipped probe is itself a finding
    doc.write_text(doc.read_text(encoding="utf-8").replace("232", "1"), encoding="utf-8")
    rc_out = bav.main(["--check", "--no-clock-probe"])
    assert rc_out == 2


def test_check_fails_when_the_document_has_never_been_generated(tmp_path, monkeypatch):
    monkeypatch.setattr(bav, "DOC_PATH", tmp_path / "absent.md")
    assert bav.main(["--check"]) == 2


def test_the_committed_document_agrees_with_the_live_derivation():
    """R11-shaped: the artefact a reader actually opens must carry today's numbers."""
    rc = subprocess.run(
        [sys.executable, "-m", "background.blocked_atom_visibility", "--check"],
        cwd=REPO, capture_output=True, text=True,
    )
    assert rc.returncode == 0, rc.stderr[-3000:]


def test_json_payload_carries_the_findings_and_the_baseline(capsys, monkeypatch):
    monkeypatch.setattr(bav, "MAP_PATH", REPO / "docs" / "design" / "maturity_map.yaml")
    assert bav.main(["--json", "--no-clock-probe"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["mint_baseline"]["harness"] == 82
    assert payload["total_atoms"] >= bav.ATOM_FLOOR
    assert any("CLOCK PROBE NOT RUN" in f for f in payload["integrity_findings"])
