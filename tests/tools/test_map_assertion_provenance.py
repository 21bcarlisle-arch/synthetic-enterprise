"""AO11 — tests for the map-assertion provenance clocks.

Every fixture here is a REAL git repository with REAL commits made at
controlled times. Nothing about `git blame` or `git log` is mocked, because
the whole tool is an assertion about what git history says: a mocked git would
prove only that the mock returns what the test told it to — the tautology
pattern, dressed as coverage.

R15 is the organising principle. A staleness report that silently finds
nothing looks exactly like a healthy map, so the tests that matter are the
ones that MUTATE the source and prove each guard goes red on its own named
defect, then green again on restore.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools import map_assertion_provenance as mp  # noqa: E402

# ---------------------------------------------------------------------------
# Fixture: a real repo whose history we control to the second
# ---------------------------------------------------------------------------

def _git(repo: Path, *args: str, when: str | None = None) -> str:
    env = None
    if when:
        import os
        env = dict(os.environ, GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
    proc = subprocess.run(["git", "-C", str(repo)] + list(args),
                          capture_output=True, text=True, env=env, check=True)
    return proc.stdout


def _write_map(repo: Path, atoms: list[dict]) -> None:
    p = repo / mp.MAP_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(yaml.safe_dump(atoms, sort_keys=False, default_flow_style=False),
                 encoding="utf-8")


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    r = tmp_path / "repo"
    r.mkdir()
    _git(r, "init", "-q")
    _git(r, "config", "user.email", "t@example.com")
    _git(r, "config", "user.name", "T")
    return r


def _commit(repo: Path, when: str, message: str = "c") -> None:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", message, when=when)


def _atom(atom_id: str, level: int, scope: list[str], name: str = "n",
          note: str = "z", **extra) -> dict:
    # Prose sits on BOTH sides of `level_current`, as it does in the real map
    # (`name`/`title` above, `origin_note` below). That layout is load-bearing for
    # the prose test: a block-granular blame could date the claim by the first line
    # of the block, the last, or the newest of them, and a fixture whose prose sits
    # on only one side lets two of those three strategies pass unnoticed. It did —
    # this test SURVIVED its own mutation twice before the fixture was fixed.
    return {"id": atom_id, "name": name, "lane": "H_harness", "level_current": level,
            "file_scope": scope, **extra, "note": note}


EARLY = "2026-01-01T00:00:00+0000"
MIDDLE = "2026-02-01T00:00:00+0000"
LATE = "2026-03-01T00:00:00+0000"


def _rows(repo: Path) -> dict[str, dict]:
    return {r["atom"]: r for r in mp.build_rows(repo)}


# ---------------------------------------------------------------------------
# The three clocks
# ---------------------------------------------------------------------------

def test_the_three_clocks_are_derived_from_real_history(repo: Path):
    """asserted_at from the map's own line, artefacts_moved_at from the code."""
    (repo / "tools").mkdir()
    (repo / "tools" / "thing.py").write_text("x = 1\n", encoding="utf-8")
    _write_map(repo, [_atom("A", 2, ["tools/thing.py"])])
    _commit(repo, EARLY)

    (repo / "tools" / "thing.py").write_text("x = 2\n", encoding="utf-8")
    _commit(repo, LATE, "artefact moves")

    row = _rows(repo)["A"]
    assert row["asserted_at"] < row["artefacts_moved_at"], row
    # The two clocks came from different files, which is the whole point.
    assert row["status"] == mp.STALE
    assert row["stale_days"] == pytest.approx(59.0, abs=1.0)


def test_prose_edits_do_not_reset_the_assertion_clock(repo: Path):
    """The clock is on the `level_current` line, not the atom block.

    If touching any field in the block re-dated the claim, then adding an
    evidence string would silently mark a years-old level as freshly asserted —
    the assertion would launder itself clean every time somebody wrote a note.
    """
    (repo / "tools").mkdir()
    (repo / "tools" / "thing.py").write_text("x = 1\n", encoding="utf-8")
    _write_map(repo, [_atom("A", 2, ["tools/thing.py"], name="first wording",
                            note="first note")])
    _commit(repo, EARLY)

    (repo / "tools" / "thing.py").write_text("x = 2\n", encoding="utf-8")
    _commit(repo, MIDDLE, "artefact moves")

    asserted_before = _rows(repo)["A"]["asserted_at"]
    # Rewrite every prose line in the block, above and below the level line, leaving
    # the level itself untouched. Any block-granular blame re-dates the claim here.
    _write_map(repo, [_atom("A", 2, ["tools/thing.py"],
                            name="a much longer and quite different wording",
                            note="a much longer and quite different note")])
    _commit(repo, LATE, "prose only")

    row = _rows(repo)["A"]
    assert row["asserted_at"] == asserted_before, "prose edit re-dated the level claim"
    assert row["status"] == mp.STALE, "a prose edit laundered a stale cell clean"


def test_a_level_change_does_reset_the_assertion_clock(repo: Path):
    """The mirror of the above: changing the claim IS a new assertion."""
    (repo / "tools").mkdir()
    (repo / "tools" / "thing.py").write_text("x = 1\n", encoding="utf-8")
    _write_map(repo, [_atom("A", 1, ["tools/thing.py"])])
    _commit(repo, EARLY)
    (repo / "tools" / "thing.py").write_text("x = 2\n", encoding="utf-8")
    _commit(repo, MIDDLE, "artefact moves")

    assert _rows(repo)["A"]["status"] == mp.STALE
    _write_map(repo, [_atom("A", 2, ["tools/thing.py"])])
    _commit(repo, LATE, "level moves")
    assert _rows(repo)["A"]["status"] == mp.CURRENT


# ---------------------------------------------------------------------------
# The contradiction class -- and its mirror error
# ---------------------------------------------------------------------------

def test_contradicted_fires_on_the_dd_shape(repo: Path):
    """L0 cell, every artefact it names committed AFTER the claim.

    This is the instance the atom exists for: the DD cell read level 0 with no
    ledger entry while all six sub-parts were built, committed and live.
    """
    _write_map(repo, [_atom("DD", 0, ["company/dd.py"])])
    _commit(repo, EARLY)

    (repo / "company").mkdir()
    (repo / "company" / "dd.py").write_text("built = True\n", encoding="utf-8")
    _commit(repo, LATE, "the work lands, the cell still reads 0")

    row = _rows(repo)["DD"]
    assert row["status"] == mp.CONTRADICTED
    assert row["scope_exclusive"] is True


def test_contradicted_does_not_fire_when_artefacts_predate_the_claim(repo: Path):
    """The mirror error, and it is the same weight as missing a real one.

    Most L0 cells name files that ALREADY EXIST, because the work is to change
    them. Reading those as "already built" reported four live, unstarted atoms
    as contradictions on the first real run.
    """
    (repo / "tools").mkdir()
    (repo / "tools" / "existing.py").write_text("x = 1\n", encoding="utf-8")
    _commit(repo, EARLY, "the file this atom intends to CHANGE already exists")

    _write_map(repo, [_atom("NEW", 0, ["tools/existing.py"])])
    _commit(repo, LATE, "atom minted against it")

    assert _rows(repo)["NEW"]["status"] == mp.CURRENT


def test_shared_scope_is_marked_so_a_confound_cannot_pass_as_evidence(repo: Path):
    """Two atoms claiming one file: neither can be dated by it alone."""
    _write_map(repo, [_atom("A", 0, ["tools/shared.py"]),
                      _atom("B", 0, ["tools/shared.py"])])
    _commit(repo, EARLY)
    (repo / "tools").mkdir()
    (repo / "tools" / "shared.py").write_text("x = 1\n", encoding="utf-8")
    _commit(repo, LATE, "moved -- but for which atom?")

    rows = _rows(repo)
    assert rows["A"]["status"] == mp.CONTRADICTED
    assert rows["A"]["scope_exclusive"] is False
    assert rows["B"]["scope_exclusive"] is False


# ---------------------------------------------------------------------------
# The recorded clock, and what its release actually does (R11: no orphan transitions)
# ---------------------------------------------------------------------------

def test_recording_a_verification_clears_stale(repo: Path):
    """The release has a tested effect: verifying a cell makes it CURRENT."""
    (repo / "tools").mkdir()
    (repo / "tools" / "thing.py").write_text("x = 1\n", encoding="utf-8")
    _write_map(repo, [_atom("A", 2, ["tools/thing.py"])])
    _commit(repo, EARLY)
    (repo / "tools" / "thing.py").write_text("x = 2\n", encoding="utf-8")
    _commit(repo, LATE, "artefact moves")

    assert _rows(repo)["A"]["status"] == mp.STALE
    mp.record_verification("A", "checked by hand", repo=repo, now=4.2e9)
    row = _rows(repo)["A"]
    assert row["status"] == mp.CURRENT
    assert row["verified_at"] == 4.2e9


def test_the_existing_self_certification_ledger_counts_as_a_verification(repo: Path):
    """A level self-certified with evidence IS a check, and is already on disk.

    Ignoring it would report every just-certified atom as never-verified and
    bury the real stale cells under noise.
    """
    (repo / "tools").mkdir()
    (repo / "tools" / "thing.py").write_text("x = 1\n", encoding="utf-8")
    _write_map(repo, [_atom("A", 2, ["tools/thing.py"])])
    _commit(repo, EARLY)
    (repo / "tools" / "thing.py").write_text("x = 2\n", encoding="utf-8")
    _commit(repo, LATE)

    gate = repo / mp.GATE_LEDGER_PATH
    gate.parent.mkdir(parents=True, exist_ok=True)
    gate.write_text(json.dumps({"atom": "A", "action": "LEVEL_UP_SELF_CERTIFIED",
                                "level": 2, "ts": 4.2e9}) + "\n", encoding="utf-8")
    assert _rows(repo)["A"]["status"] == mp.CURRENT


def test_a_malformed_ledger_line_loses_its_own_evidence_not_the_ledger(repo: Path):
    led = repo / mp.LEDGER_PATH
    led.parent.mkdir(parents=True, exist_ok=True)
    led.write_text("{not json\n" + json.dumps({"atom": "A", "ts": 99.0}) + "\n",
                   encoding="utf-8")
    assert mp.verification_times(repo) == {"A": 99.0}


def test_record_refuses_a_timestamp_with_no_statement_of_what_was_checked(repo: Path,
                                                                         monkeypatch):
    monkeypatch.setattr(mp, "REPO", repo)
    assert mp.main(["--record", "A"]) == 2
    assert not (repo / mp.LEDGER_PATH).exists()


# ---------------------------------------------------------------------------
# R15 -- NOT-FRESH-BY-DEFAULT: a cell nobody can check must never read as checked
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("scope,expected", [
    ([], mp.NO_ARTEFACTS),
    (["docs/design"], mp.DIRECTORY_SCOPE),
    ([mp.MAP_PATH], mp.TAUTOLOGICAL),
])
def test_unverifiable_scopes_are_never_current(repo: Path, scope, expected):
    (repo / "docs" / "design").mkdir(parents=True)
    (repo / "docs" / "design" / "d.md").write_text("x\n", encoding="utf-8")
    _write_map(repo, [_atom("A", 2, scope)])
    _commit(repo, EARLY)

    row = _rows(repo)["A"]
    assert row["status"] == expected
    assert row["status"] in mp.UNVERIFIABLE
    assert row["status"] != mp.CURRENT


def test_untracked_artefacts_are_unverifiable_not_current(repo: Path):
    """On disk but never committed: no clock exists, so nothing can be claimed.

    An untracked build passing as verified is a real class in this repo's
    history — twice.
    """
    _write_map(repo, [_atom("A", 2, ["tools/thing.py"])])
    _commit(repo, EARLY)
    (repo / "tools").mkdir()
    (repo / "tools" / "thing.py").write_text("x = 1\n", encoding="utf-8")  # never committed

    row = _rows(repo)["A"]
    assert row["status"] == mp.UNTRACKED_ARTEFACTS
    assert row["status"] in mp.UNVERIFIABLE


def test_a_level_2_claim_whose_artefacts_do_not_exist_is_reported(repo: Path):
    _write_map(repo, [_atom("A", 2, ["tools/never_written.py"])])
    _commit(repo, EARLY)
    assert _rows(repo)["A"]["status"] == mp.MISSING_ARTEFACTS


# ---------------------------------------------------------------------------
# R15 -- MUTATION PROOFS: each guard must go red on its own named defect
# ---------------------------------------------------------------------------

def test_vacuity_guard_fires_when_the_map_parse_collapses():
    """Mutation: a parse yielding near-zero cells must FAIL, not read clean."""
    few = [{"atom": "A", "level_current": 2, "status": mp.CURRENT, "asserted_at": 1.0,
            "verified_at": None, "artefacts_moved_at": 2.0, "scope_claims_map": False,
            "scope_exclusive": True}]
    findings = mp.integrity_findings(few)
    assert any("VACUITY" in f and "floor" in f for f in findings), findings

    healthy = [dict(few[0], atom="A%d" % i) for i in range(mp.ATOM_FLOOR + 1)]
    assert mp.integrity_findings(healthy) == []


def test_vacuity_guard_fires_when_the_blame_join_breaks(repo: Path, monkeypatch):
    """Mutation: break the line->atom join. Zero stale cells must not read clean.

    This is the 1557/1557-passed-while-the-field-was-absent shape: with no
    asserted_at anywhere, every cell would fall back to a 0.0 clock and the
    report would look healthy.
    """
    (repo / "tools").mkdir()
    (repo / "tools" / "thing.py").write_text("x = 1\n", encoding="utf-8")
    _write_map(repo, [_atom("A%d" % i, 2, ["tools/thing.py"])
                      for i in range(mp.ATOM_FLOOR + 1)])
    _commit(repo, EARLY)

    assert not any("blame join" in f for f in mp.integrity_findings(mp.build_rows(repo)))

    monkeypatch.setattr(mp, "assertion_lines", lambda text: {})
    findings = mp.integrity_findings(mp.build_rows(repo))
    assert any("blame join is" in f for f in findings), findings


def test_vacuity_guard_fires_when_the_commit_time_pass_breaks(repo: Path, monkeypatch):
    """Mutation: an empty path->date map means nothing can EVER be found stale."""
    (repo / "tools").mkdir()
    (repo / "tools" / "thing.py").write_text("x = 1\n", encoding="utf-8")
    _write_map(repo, [_atom("A%d" % i, 2, ["tools/thing.py"])
                      for i in range(mp.ATOM_FLOOR + 1)])
    _commit(repo, EARLY)

    monkeypatch.setattr(mp, "path_commit_times", lambda r: {})
    findings = mp.integrity_findings(mp.build_rows(repo))
    assert any("commit-time" in f for f in findings), findings


def test_independence_guard_fires_when_a_cell_is_dated_against_the_map(repo: Path):
    """Mutation: classify a map-claiming cell as ordinary. The tautology must be caught.

    Its two clocks would then share one source, so the answer would be
    guaranteed by construction rather than measured.
    """
    rows = [{"atom": "A%d" % i, "level_current": 2, "status": mp.CURRENT,
             "asserted_at": 1.0, "verified_at": None, "artefacts_moved_at": 2.0,
             "scope_claims_map": False, "scope_exclusive": True}
            for i in range(mp.ATOM_FLOOR + 1)]
    assert mp.integrity_findings(rows) == []

    rows[0]["scope_claims_map"] = True  # dated against the file it asserts
    findings = mp.integrity_findings(rows)
    assert any("INDEPENDENCE" in f for f in findings), findings

    rows[0]["status"] = mp.TAUTOLOGICAL  # correctly quarantined -> silent again
    assert mp.integrity_findings(rows) == []


def test_every_cell_unverifiable_is_itself_a_finding():
    """No comparison actually made is not a clean report."""
    rows = [{"atom": "A%d" % i, "level_current": 2, "status": mp.NO_ARTEFACTS,
             "asserted_at": 1.0, "verified_at": None, "artefacts_moved_at": None,
             "scope_claims_map": False, "scope_exclusive": False}
            for i in range(mp.ATOM_FLOOR + 1)]
    assert any("every cell is unverifiable" in f for f in mp.integrity_findings(rows))


def test_git_unavailable_raises_rather_than_reporting_nothing_stale(tmp_path: Path):
    """FAIL-SILENT: an unavailable check is a FAILED check.

    A non-repo must not yield an empty, therefore clean-looking, report.
    """
    not_a_repo = tmp_path / "bare"
    (not_a_repo / "docs" / "design").mkdir(parents=True)
    (not_a_repo / mp.MAP_PATH).write_text(yaml.safe_dump([_atom("A", 2, [])]),
                                          encoding="utf-8")
    with pytest.raises(RuntimeError):
        mp.build_rows(not_a_repo)


def test_cli_reports_could_not_run_instead_of_a_clean_exit(tmp_path: Path,
                                                           monkeypatch, capsys):
    monkeypatch.setattr(mp, "REPO", tmp_path)
    assert mp.main([]) == 2
    assert "COULD NOT RUN" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# The live map -- the tool must actually run against the real repo
# ---------------------------------------------------------------------------

def test_the_live_map_parses_and_carries_no_integrity_findings():
    rows = mp.build_rows()
    assert len(rows) >= mp.ATOM_FLOOR
    assert mp.integrity_findings(rows) == []
    assert {r["status"] for r in rows} <= set(mp.STATUS_ORDER)


def test_the_live_map_has_cells_on_both_sides_of_every_clock():
    """A report where nothing is current, or nothing is stale, is not measuring."""
    rows = mp.build_rows()
    assert mp.by_status(rows, mp.CURRENT), "no cell is current -- the clock is stuck"
    assert mp.by_status(rows, mp.STALE), "no cell is stale -- the comparison is inert"


# ---------------------------------------------------------------------------
# THE HOLD RECORD'S OWN VALIDITY WINDOW (H27 Expert Hour #22, atom D41)
#
# Every fixture below is written in the two conventions the two real registers
# actually use, because the defect being guarded is a PROSE record falling
# behind a DATA one, and a fixture in a convention nobody writes would prove
# only that the regex matches itself.
# ---------------------------------------------------------------------------

_H27_SHAPE = [
    "NINETEENTH HOUR (2026-08-11), on Hour #18's leads 1 AND 2. Level stays 2.",
    "TWENTIETH HOUR (2026-08-12), on the instrument Hour #19 built. Level stays 2.",
    "TWENTY-FIRST HOUR (2026-08-12), on Hour #20's leads. Level stays 2.",
]
_HGAP_SHAPE = [
    "2026-08-12 THE FOURTEENTH EXPERT HOUR RAN ON THE QUESTION THE THIRTEENTH LEFT, "
    "AND IT FOUND SOMETHING, SO THE LEVEL STAYS 2. OPENER FOR THE FIFTEENTH HOUR: more.",
    "2026-08-12 THE FIFTEENTH EXPERT HOUR RAN ON THE QUESTION THE FOURTEENTH LEFT, "
    "AND IT FOUND SOMETHING, SO THE LEVEL STAYS 2. OPENER FOR THE SIXTEENTH HOUR: more.",
]


def _held_atom(register, hold_surfaces=(), current=2, target=3, atom="A1"):
    return {"atom": atom, "level_current": current, "level_target": target,
            "register": list(register), "hold_surfaces": list(hold_surfaces)}


def test_the_verdict_carried_in_the_register_entry_is_current_by_construction():
    """The working analogue (R4): H_GAP keeps no hold note and needs none, because
    the one act an Hour cannot skip -- recording itself -- carries the verdict."""
    assert mp.hold_record_findings([_held_atom(_HGAP_SHAPE)]) == []


def test_a_hold_note_behind_its_register_FIRES():
    findings = mp.hold_record_findings(
        [_held_atom(_H27_SHAPE, ["HELD AT L2 AFTER EXPERT HOUR #18 (2026-08-11)."])])
    assert len(findings) == 1
    assert mp.HOLD_STALE in findings[0]
    assert "Hour #21" in findings[0] and "#18" in findings[0] and "3 Hour(s) behind" in findings[0]


def test_MUTATION_a_forward_pointer_does_not_count_as_an_answer():
    """THE NAMED FAIL-OPEN. Every hold record ends by naming the NEXT Hour, so the
    highest number mentioned is current by construction, one ahead of the truth.
    At the first real instance -- one Hour behind -- a mention check reads green on
    the defect it was built for."""
    one_behind = _H27_SHAPE[:2]
    stale_note = ("HELD AT L2 AFTER EXPERT HOUR #19 (2026-08-11). "
                  "The next promoter runs Hour #20 on the corrected instrument.")
    # A mention check would see #20 in the note, equal to the register, and pass.
    assert 20 in mp.hour_ordinals(stale_note)
    findings = mp.hold_record_findings([_held_atom(one_behind, [stale_note])])
    assert len(findings) == 1 and mp.HOLD_STALE in findings[0]
    assert "1 Hour(s) behind" in findings[0]


def test_MUTATION_a_register_forward_pointer_does_not_invent_an_hour():
    """The same defect on the other side, and it is not hypothetical: H_GAP's
    fifteenth entry ends 'OPENER FOR THE SIXTEENTH HOUR'. Counting mentions
    reports a perfectly current atom as one Hour behind -- it did, on the first
    real run of this check."""
    assert 16 in mp.hour_ordinals(_HGAP_SHAPE[-1])
    assert mp.entry_hour(_HGAP_SHAPE[-1]) == 15
    assert mp.hold_record_findings([_held_atom(_HGAP_SHAPE)]) == []


def test_MUTATION_hours_recorded_with_no_verdict_anywhere_FIRES():
    silent = [e.replace("Level stays 2.", "Nothing said about the level.")
              for e in _H27_SHAPE]
    findings = mp.hold_record_findings([_held_atom(silent, ["A note that answers nothing."])])
    assert len(findings) == 1 and mp.HOLD_UNANSWERED in findings[0]


_DRIFTED = ["This entry buries its ordinal a very long way in, well past any "
            "reasonable prefix, so that nothing at the front says which one it is, "
            "and only here does it admit to being the TWENTY-SECOND HOUR."]


def test_MUTATION_an_entry_that_stops_self_identifying_RAISES():
    """A convention change must refuse, not guess. An unavailable check is a
    failed check (R15).

    The refusal now comes from the POPULATION floor rather than from the entry
    parse, and the distinction is the point: nothing in the store parses, so the
    check is unavailable. What changed is only which guard says so.
    """
    with pytest.raises(ValueError, match="VACUITY"):
        mp.hold_record_findings([_held_atom(_DRIFTED)])


def test_a_non_hour_entry_beside_a_real_one_contributes_nothing_and_does_NOT_raise():
    """The other half of that discrimination, and the defect it was born from.

    `simplifications_store.for_atom` returns EVERY entry an atom has, not only
    Hour entries -- a DISCOVER/FRAME note mentioning an Hour in its body is
    ordinary and must not be read as an Hour entry. Treating "does not
    self-identify" as "the convention has moved" red-wedged HEAD and blocked
    every commit in the repo until this was split.

    Both directions are driven from ONE call so they cannot be separately
    arranged: the note contributes no ordinal, AND the real Hour beside it is
    still parsed, so the check stays live rather than being switched off.
    """
    note = ("2026-08-12 DISCOVER/FRAME ONLY, level stays 0 (worker tick, LANE 3 "
            "idle draw). No BUILD code written and nothing in file_scope touched. "
            "The lead it takes forward was opened by the TWENTY-SECOND HOUR.")
    assert mp.entry_hour(note) is None, "a DISCOVER/FRAME note is not an Hour entry"
    assert 22 in mp.hour_ordinals(note), "the ordinal IS present -- position is the whole test"

    findings = mp.hold_record_findings([_held_atom(list(_HGAP_SHAPE) + [note])])
    assert findings == [], (
        "the real Hour entries beside the note still answer the draw -- if this "
        "fires, the note was counted as a later unanswered Hour"
    )


def test_MUTATION_a_register_that_parses_to_nothing_RAISES_rather_than_passing():
    with pytest.raises(ValueError, match="VACUITY"):
        mp.hold_record_findings([_held_atom(["a register entry naming no session at all"])])


def test_an_atom_at_its_target_is_not_asked_why_it_is_held():
    """No draw asks the question, so a stale answer misleads no one -- and a
    finding here would be noise that trains the reader to ignore the check."""
    assert mp.hold_record_findings(
        [_held_atom(_H27_SHAPE, ["HELD AT L2 AFTER EXPERT HOUR #18."], current=3, target=3)]) == []


def test_the_population_is_derived_from_the_store_not_hand_typed():
    """The construct this repo records having been escaped by nine times."""
    atoms = mp._map_atoms()
    rows = mp.hold_record_atoms(atoms)
    assert len(rows) == len(atoms), "every map cell is offered to the check"
    with_hours = [r for r in rows
                  if any(mp.entry_hour(e) for e in r["register"])]
    assert with_hours, "no atom in the live store parses an Expert Hour -- check is inert"


def test_the_live_store_carries_no_stale_hold_record():
    """R11 for a governance record: the real answer to the real draw, not a fixture."""
    atoms = mp._map_atoms()
    assert mp.hold_record_findings(mp.hold_record_atoms(atoms)) == []


def test_a_stale_hold_record_reaches_the_CLI_and_not_only_the_suite(monkeypatch, capsys):
    """D34's control was never wired into its own CLI and nobody noticed for two
    Hours. This proves the finding reaches the caller's refusal, not just pytest."""
    monkeypatch.setattr(mp, "hold_record_atoms", lambda atoms, store=None: [
        _held_atom(_H27_SHAPE, ["HELD AT L2 AFTER EXPERT HOUR #18."])])
    rc = mp.main(["--check"])
    err = capsys.readouterr().err
    assert rc != 0
    assert mp.HOLD_STALE in err


def test_the_CLI_refuses_rather_than_passing_when_the_hold_check_is_unavailable(
        monkeypatch, capsys):
    def _boom(atoms, store=None):
        raise ValueError("VACUITY: the register's convention has moved")

    monkeypatch.setattr(mp, "hold_record_atoms", _boom)
    assert mp.main(["--check"]) == 2
    assert "COULD NOT RUN" in capsys.readouterr().err
