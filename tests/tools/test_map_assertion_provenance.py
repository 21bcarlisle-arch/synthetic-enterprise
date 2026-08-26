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


# ---------------------------------------------------------------------------
# THE LANDING ITSELF (H27 Expert Hour #25, atom D42)
#
# The defect these guard is a landing that exists ONLY in the working tree, so
# every fixture below is a real repo with a real HEAD and a real dirty tree.
# A mocked git would prove the mock returns what the test told it to, which is
# the same objection AO11's own first tests recorded.
#
# NOTE ON THIS FILE'S OWN LABELS: the label examples here are deliberately
# written with the ordinal split out of the string (`_label`), because a check
# keyed on a string in code cannot tell its own documentation from its subject.
# Spelling a live label in a comment made this check report a phantom landing on
# its first run.
# ---------------------------------------------------------------------------

def _label(qualifier: str, n: int) -> str:
    return "%s Expert %s #%d" % (qualifier, "Hour", n)


def _code_rows(*entries) -> dict:
    return {"code": [{"path": p, "head": h, "worktree": w} for p, h, w in entries],
            "records": []}


def _record_rows(*entries) -> dict:
    return {"code": [], "records": [{"atom": a, "path": p, "head_entries": h,
                                     "worktree_entries": w} for a, p, h, w in entries]}


def test_hour_work_written_and_not_committed_FIRES():
    """The witnessed shape: 162 lines self-labelled with an Hour, uncommitted."""
    findings = mp.unlanded_hour_findings(
        _code_rows(("tools/x.py", "def f(): pass  # %s" % _label("H27", 21),
                    "def f(): pass  # %s\ndef g(): pass  # %s"
                    % (_label("H27", 21), _label("H27", 22)))),
        ["H27_payment_belief_gap"])
    assert len(findings) == 1
    assert mp.UNLANDED_WORK in findings[0]
    assert "#22" in findings[0] and "#21" not in findings[0]
    assert "H27_payment_belief_gap" in findings[0]


def test_hour_work_that_is_committed_is_silent():
    """Not always-red: the same label on both sides is a landing, not a finding."""
    text = "def f(): pass  # %s" % _label("H27", 22)
    assert mp.unlanded_hour_findings(_code_rows(("tools/x.py", text, text)),
                                     ["H27_payment_belief_gap"]) == []


def test_MUTATION_reading_the_working_tree_on_BOTH_sides_goes_blind():
    """TAUTOLOGY (R15): the two sides must come from two trees. Hand the check the
    working-tree text as its own HEAD -- the state it exists to detect reads clean,
    every time, which is what an independence failure looks like from inside."""
    tree = "def f(): pass  # %s" % _label("H27", 22)
    assert mp.unlanded_hour_findings(_code_rows(("tools/x.py", None, tree)),
                                     ["H27_payment_belief_gap"]) != []
    assert mp.unlanded_hour_findings(_code_rows(("tools/x.py", tree, tree)),
                                     ["H27_payment_belief_gap"]) == []


def test_MUTATION_an_unqualified_label_is_not_attributed_to_anybody():
    """WRONG SUBJECT (R15): three atoms run Hours. A bare ordinal belongs to none
    of them, and counting it would hand one atom's work to another."""
    with pytest.raises(ValueError, match="VACUITY"):
        mp.unlanded_hour_findings(
            _code_rows(("tools/x.py", "", "# Expert Hour #22 landed here")),
            ["H27_payment_belief_gap"])


def test_an_ambiguous_qualifier_still_FIRES_and_names_every_cell_it_could_be():
    """This check's own first-run defect, pinned both ways. Two live cells begin
    `H27`, so resolving a qualifier to one atom invented work for a second -- and
    dropping the ambiguous label instead would have gone inert on the very atom
    the check was built for. It fires, and says which cells it could mean."""
    findings = mp.unlanded_hour_findings(
        _code_rows(("tools/x.py", "", "# %s" % _label("H27", 22))),
        ["H27_payment_belief_gap", "H27_phone_act_channel", "H_GAP_fabric"])
    assert len(findings) == 1
    assert "AMBIGUOUS" in findings[0]
    assert "H27_payment_belief_gap" in findings[0]
    assert "H27_phone_act_channel" in findings[0]
    assert "H_GAP_fabric" not in findings[0]


def test_a_label_naming_no_map_cell_is_reported_rather_than_dropped():
    findings = mp.unlanded_hour_findings(
        _code_rows(("tools/x.py", "", "# %s" % _label("ZZ9", 3))), ["H27_payment_belief_gap"])
    assert len(findings) == 1 and "no map cell" in findings[0]


def test_a_file_that_does_not_exist_at_HEAD_is_reported_not_skipped():
    """FAIL-OPEN ON MISSING (R15): a brand-new uncommitted file is the strongest
    form of unlanded, and an absent HEAD side must never read as agreement."""
    findings = mp.unlanded_hour_findings(
        _code_rows(("tools/new.py", None, "# %s" % _label("H27", 25))),
        ["H27_payment_belief_gap"])
    assert len(findings) == 1
    assert "does not exist at HEAD" in findings[0]


def test_an_hour_entry_written_but_not_committed_FIRES():
    """The second half of the witnessed near miss: the VERDICT itself unlanded."""
    head = ["TWENTY-SECOND HOUR (2026-08-12), on leads. Level stays 2."]
    tree = head + ["TWENTY-THIRD HOUR (2026-08-13), verified and landed. Level stays 2."]
    findings = mp.unlanded_hour_findings(
        _record_rows(("H27_payment_belief_gap", "docs/design/simplifications/H27.yaml",
                      head, tree)))
    assert len(findings) == 1
    assert mp.UNLANDED_RECORD in findings[0] and "#23" in findings[0]


def test_a_record_whose_entries_are_all_committed_is_silent():
    head = ["TWENTY-SECOND HOUR (2026-08-12), on leads. Level stays 2."]
    assert mp.unlanded_hour_findings(
        _record_rows(("A1", "docs/design/simplifications/A1.yaml", head, list(head)))) == []


def test_MUTATION_nothing_parsing_anywhere_RAISES_rather_than_passing():
    """FAIL-SILENT (R15): an unparseable convention is an unavailable check, and
    an unavailable check is a FAILED check -- never a clean repo."""
    with pytest.raises(ValueError, match="VACUITY"):
        mp.unlanded_hour_findings(_code_rows(("tools/x.py", "def f(): pass", "def f(): x")))


def test_the_record_store_and_its_renderings_are_never_a_landing(repo: Path):
    """A record repeating the claim is record-against-record one level down: at the
    real near miss the register named the Hour while the code did not exist."""
    for path in ("docs/design/simplifications/A1.yaml", "site/data/proof.json",
                 "tools/real.py"):
        p = repo / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x = 1  # %s\n" % _label("H27", 22), encoding="utf-8")
    _commit(repo, EARLY)
    paths = mp._labelled_code_paths(repo)
    assert paths == ["tools/real.py"]


def test_the_population_is_derived_from_both_trees_not_from_one(repo: Path):
    """A file only HEAD carries and a file only the tree carries are both asked
    about -- the tree-only direction is the whole point, and the HEAD-only one
    keeps a deletion from reading as a clean sweep."""
    (repo / "tools").mkdir()
    (repo / "tools" / "committed.py").write_text("# %s\n" % _label("H27", 21), encoding="utf-8")
    _commit(repo, EARLY)
    (repo / "tools" / "uncommitted.py").write_text("# %s\n" % _label("H27", 22), encoding="utf-8")
    _git(repo, "add", "-A")
    assert mp._labelled_code_paths(repo) == ["tools/committed.py", "tools/uncommitted.py"]


def test_the_end_to_end_check_fires_on_a_real_repo_with_real_uncommitted_work(repo: Path):
    """The whole path -- git show, disk read, label parse, finding -- on a repo
    whose HEAD and working tree really do differ."""
    (repo / "tools").mkdir()
    src = repo / "tools" / "couple.py"
    src.write_text("# %s\n" % _label("H27", 21), encoding="utf-8")
    _write_map(repo, [_atom("H27_payment_belief_gap", 2, ["tools/couple.py"])])
    _commit(repo, EARLY)
    src.write_text("# %s\n# %s\n" % (_label("H27", 21), _label("H27", 22)), encoding="utf-8")

    atoms = mp._map_atoms(repo)
    rows = mp.unlanded_hour_atoms(atoms, repo=repo)
    findings = mp.unlanded_hour_findings(rows, [a["id"] for a in atoms])
    assert len(findings) == 1
    assert "#22" in findings[0] and "tools/couple.py" in findings[0]

    src.write_text("# %s\n" % _label("H27", 21), encoding="utf-8")
    assert mp.unlanded_hour_findings(mp.unlanded_hour_atoms(atoms, repo=repo),
                                     [a["id"] for a in atoms]) == []


def test_git_that_cannot_answer_RAISES_rather_than_reporting_nothing_unlanded(tmp_path: Path):
    """FAIL-SILENT (R15): "the tree is clean" and "I could not look at the tree"
    are the same silence and opposite facts."""
    with pytest.raises(Exception):
        mp._labelled_code_paths(tmp_path)
    with pytest.raises(RuntimeError):
        mp._head_text("tools/x.py", tmp_path)


def test_a_malformed_record_loses_its_own_entries_not_the_whole_check():
    assert mp._register_entries("{{ not: yaml: [") == []
    assert mp._register_entries("- a plain list, not the store's shape") == []
    assert mp._register_entries(None) == []


def test_unlanded_work_reaches_the_CLI_under_its_OWN_exit_code(monkeypatch, capsys):
    """D34's lesson (wired into the CLI, not only the suite) and the reason it is
    NOT in the shared findings list: 2 stays COULD-NOT-RUN, 3 is the finding, so a
    caller can tell an unavailable check from an unlanded landing."""
    monkeypatch.setattr(mp, "unlanded_hour_atoms",
                        lambda atoms, repo=None, store_dir=None:
                        _code_rows(("tools/x.py", "", "# %s" % _label("H27", 22))))
    assert mp.main(["--unlanded"]) == 3
    assert mp.UNLANDED_WORK in capsys.readouterr().err

    monkeypatch.setattr(mp, "unlanded_hour_atoms",
                        lambda atoms, repo=None, store_dir=None: _code_rows(
                            ("tools/x.py", "# %s" % _label("H27", 22),
                             "# %s" % _label("H27", 22))))
    assert mp.main(["--unlanded"]) == 0


def test_the_CLI_refuses_rather_than_passing_when_the_landing_check_is_unavailable(
        monkeypatch, capsys):
    def _boom(atoms, repo=None, store_dir=None):
        raise RuntimeError("git show failed")

    monkeypatch.setattr(mp, "unlanded_hour_atoms", _boom)
    assert mp.main(["--unlanded"]) == 2
    assert "COULD NOT RUN" in capsys.readouterr().err


def test_the_live_repo_parses_above_the_label_floor():
    """Vacuity on the REAL trees: this check must be able to see the convention
    the repo is actually written in. It asserts the check RUNS and parses -- not
    that it is empty, because unlanded work is a legitimate live state (an Hour
    mid-flight is exactly that) and a test that demanded zero would make every
    Hour's own tick red."""
    atoms = mp._map_atoms()
    findings = mp.unlanded_hour_findings(mp.unlanded_hour_atoms(atoms),
                                         [a.get("id") for a in atoms if a.get("id")])
    assert all(f.startswith((mp.UNLANDED_WORK, mp.UNLANDED_RECORD)) for f in findings)


# --- D41's parser, repaired by Hour #25 -------------------------------------

def test_a_verdict_naming_its_own_hour_through_an_adjective_IS_READ():
    """The live register's only self-answering sentence, verbatim in shape. This
    was invisible and it reddened D41's own live test on a current register."""
    entry = ("TWENTY-FOURTH HOUR (2026-08-13), on Hour #23's finding. It found a red. "
             "THE LEVEL STAYS 2 FOR THE TWENTY-FOURTH CONSECUTIVE HOUR.")
    assert mp.entry_hour(entry) == 24
    assert 24 in mp.answered_hours(entry)
    assert mp.hold_record_findings([_held_atom([entry])]) == []


def test_MUTATION_a_wildcard_ordinal_would_swallow_the_real_one():
    """The alternation is load-bearing, not tidiness: with `[A-Z]+` as the first
    group, "AND THE TWENTIETH HOUR" matches on AND, the scan resumes past it, and
    the ordinal inside the match is LOST -- a parse that drops Hours silently."""
    import re as _re
    wildcard = _re.compile(r"\b([A-Z]+(?:-[A-Z]+)?)\b(?:\s+[A-Z]+){0,2}\s+HOUR\b")
    text = "AND THE TWENTIETH HOUR ran."
    assert [m.group(1) for m in wildcard.finditer(text)] == ["AND"]
    assert mp.hour_ordinals(text) == {20}


def test_the_intervening_run_is_bounded_so_a_far_off_ordinal_is_not_claimed():
    """Not always-green: an ordinal five words from HOUR is a different sentence,
    and reading it would let an unrelated mention answer the draw."""
    assert mp.hour_ordinals("THE TWENTIETH ATOM WAS DRAWN AND THEN SOMEBODY RAN AN HOUR") == set()


def test_a_brand_new_uncommitted_file_is_reported_as_absent_at_HEAD_end_to_end(repo: Path):
    """FAIL-OPEN ON MISSING through the BUILDER, not just the pure function. The
    fixture-level version of this survived its own mutation: `_head_text` handing
    back "" for an absent file left every assertion green, because only the
    end-to-end path can tell an empty file from a file that is not there."""
    (repo / "tools").mkdir()
    (repo / "tools" / "old.py").write_text("# nothing\n", encoding="utf-8")
    _write_map(repo, [_atom("H27_payment_belief_gap", 2, ["tools/old.py"])])
    _commit(repo, EARLY)
    (repo / "tools" / "brand_new.py").write_text("# %s\n" % _label("H27", 25), encoding="utf-8")
    _git(repo, "add", "-A")

    atoms = mp._map_atoms(repo)
    findings = mp.unlanded_hour_findings(mp.unlanded_hour_atoms(atoms, repo=repo),
                                         [a["id"] for a in atoms])
    assert len(findings) == 1
    assert "tools/brand_new.py" in findings[0]
    assert "does not exist at HEAD at all" in findings[0]
    assert mp._head_text("tools/brand_new.py", repo) is None


# --- D43: whose atom did that Hour build? (H27 Expert Hour #26) -------------
#
# D42 asks whether an Hour's work is COMMITTED. These ask one step earlier:
# whether what it committed is inside the subject the map says its atom is
# about. Both halves of the question have their own rule and the asymmetry is
# load-bearing -- coverage is prefix-aware (a directory scope really does put
# the file under that cell's clocks), attribution is not (a directory claim is
# DIRECTORY_SCOPE, "ownership unarbitrable", this module's own word for it).

def _subject_rows(labels: dict, scopes: dict) -> dict:
    """labels: {path: [(QUALIFIER, ordinal), ...]}; scopes: {atom_id: [paths]}."""
    return {"labels": [{"path": p, "labels": sorted(v)} for p, v in sorted(labels.items())],
            "scopes": scopes}


def test_an_hour_landing_outside_its_own_cells_scope_FIRES():
    """The witnessed shape: Hours #22 and #25 are recorded against H27 and built
    AO11's module, which H27 does not declare and AO11 was never told about."""
    findings = mp.hour_subject_findings(_subject_rows(
        {"tools/map_assertion_provenance.py": [("H27", 25)]},
        {"H27_payment_belief_gap": ["tools/couple_w2_11_d5.py"],
         "AO11_map_assertion_provenance": ["tools/map_assertion_provenance.py"]}))
    assert len(findings) == 1
    assert mp.OFF_SCOPE in findings[0] and mp.FOREIGN_SCOPE in findings[0]
    assert "AO11_map_assertion_provenance" in findings[0]
    assert "#25" in findings[0]


def test_an_hour_inside_its_own_cells_scope_is_silent():
    """NOT ALWAYS-RED: the ordinary case -- an Hour that built its own subject."""
    assert mp.hour_subject_findings(_subject_rows(
        {"tools/couple_w2_11_d5.py": [("H27", 24)]},
        {"H27_payment_belief_gap": ["tools/couple_w2_11_d5.py"]})) == []


def test_a_directory_scope_COVERS_its_own_files_for_the_on_subject_question():
    """`file_scope` mixes granularities: ~20 live cells scope bare `tools`. An
    Hour landing inside a directory its own cell declares IS on subject, and its
    assertion clock really does see the change."""
    assert mp.hour_subject_findings(_subject_rows(
        {"tools/anything.py": [("A8", 3)]},
        {"A8_experiment_loop_speed": ["tools", "background"]})) == []


def test_a_directory_claim_never_NAMES_the_wronged_owner():
    """WRONG POPULATION (R15): a finding with twenty owners has none. Only a cell
    naming the FILE is reported as the party that was not told."""
    findings = mp.hour_subject_findings(_subject_rows(
        {"tools/map_assertion_provenance.py": [("H27", 25)]},
        {"H27_payment_belief_gap": ["tools/couple_w2_11_d5.py"],
         "AO11_map_assertion_provenance": ["tools/map_assertion_provenance.py"],
         "A8_experiment_loop_speed": ["tools", "background", "tests"],
         "G11_activity_cost_utilisation": ["background", "tools", "site"]}))
    assert len(findings) == 1
    assert "AO11_map_assertion_provenance" in findings[0]
    assert "A8_experiment_loop_speed" not in findings[0]
    assert "G11_activity_cost_utilisation" not in findings[0]


def test_a_path_no_cell_names_says_so_rather_than_inventing_an_owner():
    findings = mp.hour_subject_findings(_subject_rows(
        {"tools/orphan.py": [("H27", 9)]},
        {"H27_payment_belief_gap": ["tools/couple_w2_11_d5.py"]}))
    assert len(findings) == 1
    assert mp.FOREIGN_SCOPE not in findings[0]
    assert "No map cell names that path as its own." in findings[0]


def test_an_ordinary_word_before_the_label_is_not_an_atom():
    """WRONG SUBJECT, and a defect in this check's own first live run: the
    convention's regex takes whatever word precedes "Expert Hour", so prose --
    "...landed AFTER Expert Hour #18", "the CELL Expert Hour #15 built" --
    parsed as a qualifier and invented seven findings against atoms that have
    never existed. A qualifier counts only if it names a map cell, and that
    filter is DERIVED FROM THE MAP rather than a stopword list."""
    scopes = {"H27_payment_belief_gap": ["tools/couple_w2_11_d5.py"]}
    for word in ("AFTER", "UNTIL", "CELL", "HOLE", "ASYMMETRY"):
        with pytest.raises(ValueError, match="VACUITY"):
            mp.hour_subject_findings(_subject_rows(
                {"tools/somewhere_else.py": [(word, 18)]}, scopes))


def test_a_real_label_beside_prose_is_still_read():
    """The filter must not go INERT: prose is dropped, the atom label survives."""
    findings = mp.hour_subject_findings(_subject_rows(
        {"tools/map_assertion_provenance.py": [("AFTER", 18), ("H27", 22)]},
        {"H27_payment_belief_gap": ["tools/couple_w2_11_d5.py"],
         "AO11_map_assertion_provenance": ["tools/map_assertion_provenance.py"]}))
    assert len(findings) == 1
    assert "H27" in findings[0] and "AFTER" not in findings[0]


def test_an_ambiguous_qualifier_is_on_subject_when_EITHER_cell_declares_it():
    """D42's first-run defect in the opposite direction. Two live cells begin
    `H27`; an ambiguous label must never MANUFACTURE a finding.

    BOTH ORDERS, and the second one survived a mutation before it existed:
    `_candidates` sorts, and the live pair happens to put the DECLARING cell
    first (`H27_payment_belief_gap` < `H27_phone_act_channel`), so resolving
    the ambiguity to `owners[0]` was indistinguishable from resolving it
    honestly. A control certified only on the alphabetical luck of today's map
    is testing the map, not the rule."""
    for declarer, other in (("H27_a_declaring_cell", "H27_zz_other_cell"),
                            ("H27_zz_declaring_cell", "H27_aa_other_cell")):
        assert mp.hour_subject_findings(_subject_rows(
            {"tools/couple_w2_11_d5.py": [("H27", 24)]},
            {declarer: ["tools/couple_w2_11_d5.py"], other: []})) == [], declarer


def test_an_ambiguous_qualifier_that_is_off_subject_for_BOTH_still_fires():
    findings = mp.hour_subject_findings(_subject_rows(
        {"tools/map_assertion_provenance.py": [("H27", 22)]},
        {"H27_payment_belief_gap": ["tools/couple_w2_11_d5.py"],
         "H27_phone_act_channel": [],
         "AO11_map_assertion_provenance": ["tools/map_assertion_provenance.py"]}))
    assert len(findings) == 1
    assert "AMBIGUOUS" in findings[0]
    assert "H27_payment_belief_gap" in findings[0] and "H27_phone_act_channel" in findings[0]


def test_MUTATION_no_label_parsing_RAISES_rather_than_reading_clean():
    """FAIL-SILENT (R15): a convention that drifted off atom ids is an
    unavailable check, and an unavailable check is a FAILED check."""
    with pytest.raises(ValueError, match="VACUITY"):
        mp.hour_subject_findings(_subject_rows(
            {}, {"H27_payment_belief_gap": ["tools/couple_w2_11_d5.py"]}))


def test_an_empty_map_side_RAISES_rather_than_reporting_everything_off_subject():
    """FAIL-OPEN ON MISSING, in the direction that COSTS: with no scopes at all
    every label reads off-subject, which is the loudest possible report handed
    out for free. "Nothing is off subject" and "I could not read the map" are
    the same silence and opposite facts.

    IT MATCHES THE MAP-SIDE MESSAGE, not the word VACUITY, and this survived a
    mutation before it did: with no scopes, no qualifier resolves to a cell, so
    every label is dropped and the LABEL floor raises anyway -- deleting the map
    guard outright left the suite green. A test that accepts either guard's
    refusal is testing that something refused, not that this one did."""
    with pytest.raises(ValueError, match="subject side of this check is empty"):
        mp.hour_subject_findings(_subject_rows(
            {"tools/couple_w2_11_d5.py": [("H27", 24)]}, {}))


def test_hours_on_subject_counts_only_hours_that_reached_a_declared_file():
    rows = _subject_rows(
        {"tools/couple_w2_11_d5.py": [("H27", 24)],
         "tools/map_assertion_provenance.py": [("H27", 25)]},
        {"H27_payment_belief_gap": ["tools/couple_w2_11_d5.py"],
         "AO11_map_assertion_provenance": ["tools/map_assertion_provenance.py"]})
    assert mp.hours_on_subject("H27_payment_belief_gap", rows) == {24}
    assert mp.hours_on_subject("AO11_map_assertion_provenance", rows) == set()


def test_hours_on_subject_REFUSES_a_cell_the_map_does_not_carry():
    """FAIL-OPEN (R15): a typo'd id must not report zero Hours on subject, which
    reads as the strongest possible finding about a real cell."""
    with pytest.raises(KeyError):
        mp.hours_on_subject("H27_typo", _subject_rows(
            {"tools/couple_w2_11_d5.py": [("H27", 24)]},
            {"H27_payment_belief_gap": ["tools/couple_w2_11_d5.py"]}))


def test_the_working_tree_side_is_not_this_checks_subject(repo: Path):
    """Two adjacent questions kept apart on purpose: an Hour mid-flight (D42's
    subject) must not read as an Hour that built the wrong thing."""
    (repo / "tools").mkdir()
    (repo / "tools" / "couple.py").write_text("# %s\n" % _label("H27", 24), encoding="utf-8")
    _write_map(repo, [_atom("H27_payment_belief_gap", 2, ["tools/couple.py"])])
    _commit(repo, EARLY)
    (repo / "tools" / "elsewhere.py").write_text("# %s\n" % _label("H27", 26), encoding="utf-8")
    _git(repo, "add", "-A")

    atoms = mp._map_atoms(repo)
    rows = mp.hour_subject_rows(atoms, repo=repo)
    assert [e["path"] for e in rows["labels"]] == ["tools/couple.py"]
    assert mp.hour_subject_findings(rows) == []


def test_the_end_to_end_check_fires_on_a_real_repo_with_real_committed_work(repo: Path):
    """The whole path -- git grep, git show, label parse, map read -- on a repo
    whose HEAD really does carry an Hour outside its own cell's scope."""
    (repo / "tools").mkdir()
    (repo / "tools" / "couple.py").write_text("# %s\n" % _label("H27", 24), encoding="utf-8")
    (repo / "tools" / "other.py").write_text("# %s\n" % _label("H27", 25), encoding="utf-8")
    _write_map(repo, [_atom("H27_payment_belief_gap", 2, ["tools/couple.py"]),
                      _atom("AO11_map_assertion_provenance", 2, ["tools/other.py"])])
    _commit(repo, EARLY)

    atoms = mp._map_atoms(repo)
    rows = mp.hour_subject_rows(atoms, repo=repo)
    findings = mp.hour_subject_findings(rows)
    assert len(findings) == 1
    assert "tools/other.py" in findings[0] and "#25" in findings[0]
    assert "AO11_map_assertion_provenance" in findings[0]
    assert mp.hours_on_subject("H27_payment_belief_gap", rows) == {24}


def test_off_subject_work_reaches_the_CLI_under_its_OWN_exit_code(monkeypatch, capsys):
    """Own exit code 4 -- D42's precedent. Off-subject work is a REPORT to the
    next draw and to the cell that owns the file, never a repo-wide refusal: the
    honest case (a defect found here really does live there) must not wedge
    every lane. 2 stays COULD-NOT-RUN."""
    monkeypatch.setattr(mp, "hour_subject_rows", lambda atoms, repo=None: _subject_rows(
        {"tools/map_assertion_provenance.py": [("H27", 25)]},
        {"H27_payment_belief_gap": ["tools/couple_w2_11_d5.py"],
         "AO11_map_assertion_provenance": ["tools/map_assertion_provenance.py"]}))
    assert mp.main(["--hour-subject"]) == 4
    assert mp.OFF_SCOPE in capsys.readouterr().err

    monkeypatch.setattr(mp, "hour_subject_rows", lambda atoms, repo=None: _subject_rows(
        {"tools/couple_w2_11_d5.py": [("H27", 24)]},
        {"H27_payment_belief_gap": ["tools/couple_w2_11_d5.py"]}))
    assert mp.main(["--hour-subject"]) == 0


def test_the_CLI_refuses_rather_than_passing_when_the_subject_check_is_unavailable(
        monkeypatch, capsys):
    def _boom(atoms, repo=None):
        raise RuntimeError("git grep failed")

    monkeypatch.setattr(mp, "hour_subject_rows", _boom)
    assert mp.main(["--hour-subject"]) == 2
    assert "COULD NOT RUN" in capsys.readouterr().err


def test_the_live_repo_names_the_off_subject_hours_this_atom_actually_ran():
    """Proven on the REAL bytes, not a fixture -- the measurement Hour #26 was
    drawn to make. Every H27 finding names a real cell that owns the file, and
    the on-subject count is strictly below the highest ordinal the register
    carries, which is the whole finding: the number answering the 2->3 draw is
    not a count of examinations of this atom."""
    atoms = mp._map_atoms()
    rows = mp.hour_subject_rows(atoms)
    findings = mp.hour_subject_findings(rows)
    assert all(f.startswith(mp.OFF_SCOPE) for f in findings)
    h27 = [f for f in findings if f.startswith("%s: H27 " % mp.OFF_SCOPE)]
    assert h27, "the atom whose Hours this check was built from must still be visible"
    assert any("AO11_map_assertion_provenance" in f for f in h27)
    on = mp.hours_on_subject("H27_payment_belief_gap", rows)
    assert on and max(on) >= 24
    assert len(on) < max(on) - 1, "some recorded Hour left no mark on this cell's own files"


# ---------------------------------------------------------------------------
# THE ID A CITATION POINTS AT  (D45, H27 Expert Hour #29)
#
# These are the tests the mechanism landed WITHOUT. It was found in the working
# tree carrying 218 lines, a CLI flag and a wire into the default refusal path,
# and not one line of test -- the shape of "a commit landed two controls it
# never ran", one step earlier. So the first thing measured here is the thing
# that check exists to measure: on the LIVE bytes, not a fixture.
# ---------------------------------------------------------------------------

#: EVERY FIXTURE ID BELOW USES THIS PREFIX, and that is a control rather than
#: a naming whim. This file carries Expert-Hour labels, so it is INSIDE the
#: population the check reads: a fixture writing `atom D44` is a citation of
#: the live map, and the first draft of these tests manufactured seven
#: findings against the repo out of its own test data. The prefix filter is
#: derived from the map, so a prefix no lane uses cannot be a citation --
#: pinned below, because the day a `ZQ` lane is minted this file starts lying.
FIXTURE_PREFIX = "ZQ"


def test_this_files_own_fixture_ids_use_a_prefix_the_map_DOES_NOT_carry():
    """Otherwise these fixtures become findings about the real map -- the
    wrong-population defect this very control was corrected for, committed by
    its own test file."""
    live = mp._lane_prefixes(a["id"] for a in mp._map_atoms() if a.get("id"))
    assert live, "the map supplied no lane prefixes -- this pin is unavailable"
    assert FIXTURE_PREFIX not in live


def _cite_rows(texts: dict, ids: list[str]) -> dict:
    """texts: {path: text}; ids: the map's own cells."""
    return {"texts": [{"path": p, "text": t} for p, t in sorted(texts.items())],
            "atom_ids": sorted(ids)}


def _bulk(n: int) -> str:
    """Citations that all resolve, to clear the vacuity floor without findings."""
    return " ".join("atom ZQ%d_ok" % i for i in range(1, n + 1))


def _bulk_ids(n: int) -> list[str]:
    return ["ZQ%d_ok" % i for i in range(1, n + 1)]


def test_a_citation_naming_no_cell_at_all_is_a_PHANTOM():
    """The witnessed shape: eight consecutive Hours wrote `atom D37` ... `atom
    D44` into shipped source while the map's D series stopped at D36."""
    findings = mp.cited_atom_findings(_cite_rows(
        {"tools/couple.py": "mechanised as atom ZQ44. " + _bulk(25)},
        _bulk_ids(25) + ["ZQ36_bill_render_footing"]))
    assert len(findings) == 1
    assert findings[0].startswith(mp.PHANTOM_ATOM)
    assert "`atom ZQ44`" in findings[0] and "tools/couple.py" in findings[0]
    assert "mint it, or stop citing it" in findings[0]


def test_the_two_findings_are_KEPT_APART_because_the_repairs_differ():
    """A slug that has drifted is CORRECTED; an id nothing carries is MINTED.
    One finding for both would send the reader to the wrong repair."""
    ids = _bulk_ids(25) + ["ZQ35_the_render_site_sweep_stops_at_this_processs_edge"]
    stale = mp.cited_atom_findings(_cite_rows(
        {"a.py": "atom ZQ35_the_reader_precision_was_read_at_one_of_two_sites " + _bulk(25)},
        ids))
    assert len(stale) == 1 and stale[0].startswith(mp.STALE_ATOM_SLUG)
    assert "ZQ35_the_render_site_sweep_stops_at_this_processs_edge" in stale[0]
    phantom = mp.cited_atom_findings(_cite_rows({"a.py": "atom ZQ99_nothing " + _bulk(25)}, ids))
    assert len(phantom) == 1 and phantom[0].startswith(mp.PHANTOM_ATOM)


def test_a_citation_that_resolves_is_SILENT_in_both_of_its_two_forms():
    """The full id, and the short code a single id extends -- `atom D44` must
    resolve once `D44_the_thing` exists, or every Hour's shorthand is a finding."""
    ids = _bulk_ids(25) + ["ZQ44_the_normalisation_kind_is_declared"]
    assert mp.cited_atom_findings(_cite_rows(
        {"a.py": "atom ZQ44 and atom ZQ44_the_normalisation_kind_is_declared " + _bulk(25)},
        ids)) == []


def test_the_prefix_filter_is_DERIVED_FROM_THE_MAP_not_a_stopword_list():
    """A token whose prefix no live cell uses is not an atom citation BY
    DEFINITION -- and the same token becomes one the day that lane exists. A
    hand-typed stopword list would go stale at the first lane added; this reads
    the map's own ids, so nothing here needs editing."""
    assert mp.atom_citations("see atom X9_thing for the rest", {"D", "W"}) == set()
    assert mp.atom_citations("see atom X9_thing for the rest", {"X", "D"}) == {"X9_thing"}


def test_a_LANE_GLOB_is_not_a_citation_and_the_MUTATION_proves_the_filter_is_load_bearing():
    """MEASURED on the live bytes before this was fixed: the prefix filter alone
    reported `PHANTOM_ATOM: atom W` out of `a product-lane atom (W*/D/B/E/...)`.
    A lane glob has no repair -- there is no atom W to mint and no citation to
    correct -- so the finding was manufactured, not found. Mutating the filter
    away brings it straight back."""
    prose = "a product-lane atom (W*/D/B/E/C/F/G-product/SITE, NOT H_harness)"
    assert mp.atom_citations(prose, {"W", "D", "H"}) == set()

    original = mp._is_id_shaped
    try:
        mp._is_id_shaped = lambda token: True          # the pre-fix behaviour
        assert mp.atom_citations(prose, {"W", "D", "H"}) == {"W"}
    finally:
        mp._is_id_shaped = original
    assert mp.atom_citations(prose, {"W", "D", "H"}) == set()


def test_the_id_shape_filter_ADMITS_every_id_the_map_carries():
    """The fail-open direction, and the one that would look like a clean map: a
    filter that dropped a real citation would silence the check on exactly the
    ids it exists to find. Proven against the LIVE map, so a future id shaped
    unlike today's (22 cells carry no number at all) fails here first."""
    ids = [a["id"] for a in mp._map_atoms() if a.get("id")]
    assert len(ids) > mp.ATOM_FLOOR
    unshaped = [i for i in ids if not mp._is_id_shaped(i)]
    assert unshaped == [], "the shape filter would drop citations of these live cells"


def test_the_lane_number_grammar_matches_the_map_contracts():
    """The pin the module's own comment PROMISES BY NAME -- and did not have.
    `_LANE_NUMBER` is mirrored from the map-contract test rather than imported;
    a mirror nothing compares is a second description that rots from the day it
    is written."""
    import re as _re
    src = (Path(__file__).resolve().parents[1] / "design"
           / "test_maturity_map_contract.py").read_text(encoding="utf-8")
    m = _re.search(r"^_LANE_NUMBER = re\.compile\((.+)\)$", src, _re.M)
    assert m, "the contract test no longer defines _LANE_NUMBER under that name"
    contract = _re.compile(eval(m.group(1)))  # noqa: S307 -- our own repo's literal
    assert contract.pattern == mp._LANE_NUMBER.pattern
    for atom_id in (a["id"] for a in mp._map_atoms() if a.get("id")):
        mine = mp._lane_number(atom_id)
        theirs = contract.match(atom_id)
        assert (mine is None) == (theirs is None)
        if mine is not None:
            assert mine == theirs.group(1) + theirs.group(2)


def test_an_empty_map_side_RAISES_rather_than_calling_every_citation_a_phantom():
    with pytest.raises(ValueError, match="VACUITY"):
        mp.cited_atom_findings(_cite_rows({"a.py": "atom D44"}, []))


def test_nothing_readable_RAISES_rather_than_reporting_clean_over_an_empty_population():
    with pytest.raises(ValueError, match="VACUITY"):
        mp.cited_atom_findings(_cite_rows({}, _bulk_ids(25)))


def test_MUTATION_a_citing_convention_that_moved_RAISES_rather_than_reading_clean():
    """Below the floor is INDISTINGUISHABLE from a repo with no phantoms, and
    the two are opposite facts. An unavailable check is a FAILED check."""
    with pytest.raises(ValueError, match="only 1 atom citation"):
        mp.cited_atom_findings(_cite_rows({"a.py": "atom ZQ1_ok"}, _bulk_ids(25)))
    # ... and the same population one citation above the floor does NOT raise.
    assert mp.cited_atom_findings(_cite_rows(
        {"a.py": _bulk(mp.CITATION_FLOOR)}, _bulk_ids(25))) == []


def test_the_store_records_are_IN_the_population_and_the_archive_is_NOT(repo: Path, tmp_path):
    """A citation in a per-atom store record is a CLAIM ABOUT THE MAP and is
    read; an archived snapshot is a frozen copy of a record since rewritten,
    and holding it to today's map would demand edits to history."""
    (repo / "tools").mkdir()
    (repo / "tools" / "c.py").write_text("# H27 Expert Hour #29\n", encoding="utf-8")
    store = repo / "docs" / "design" / "simplifications"
    (store / "archive").mkdir(parents=True)
    (store / "ZQ5_account_hierarchy_payments.yaml").write_text(
        "atom_id: ZQ5\nnote: mechanised as atom ZQ77_live\n", encoding="utf-8")
    (store / "archive" / "old.yaml").write_text(
        "note: mechanised as atom ZQ88_archived\n", encoding="utf-8")
    _write_map(repo, [_atom("ZQ5_account_hierarchy_payments", 2, ["tools/c.py"])])
    _commit(repo, EARLY)

    rows = mp.cited_atom_rows(mp._map_atoms(repo), repo=repo, store_dir=store)
    read = {e["path"] for e in rows["texts"]}
    assert any(p.endswith("ZQ5_account_hierarchy_payments.yaml") for p in read)
    assert not any("archive/" in p for p in read)
    tokens = set()
    for e in rows["texts"]:
        tokens |= mp.atom_citations(e["text"], {"ZQ"})
    assert "ZQ77_live" in tokens and "ZQ88_archived" not in tokens


def test_the_two_readers_are_independent_the_ids_never_come_from_the_citing_text(repo: Path):
    """The tautology R15 names: derive the ids from the text that cites them and
    every citation resolves by construction. The ids come off the map."""
    (repo / "tools").mkdir()
    (repo / "tools" / "c.py").write_text(
        "# H27 Expert Hour #29\n# mechanised as atom ZQ44_never_minted\n", encoding="utf-8")
    store = repo / "docs" / "design" / "simplifications"
    store.mkdir(parents=True)
    _write_map(repo, [_atom("ZQ5_account_hierarchy_payments", 2, ["tools/c.py"])])
    _commit(repo, EARLY)

    rows = mp.cited_atom_rows(mp._map_atoms(repo), repo=repo, store_dir=store)
    assert rows["atom_ids"] == ["ZQ5_account_hierarchy_payments"]
    assert "ZQ44_never_minted" not in " ".join(rows["atom_ids"])


def test_citations_reach_the_CLI_and_a_broken_read_is_never_a_PASS(monkeypatch, capsys):
    monkeypatch.setattr(mp, "cited_atom_rows",
                        lambda atoms, repo=None, store_dir=None: _cite_rows(
                            {"a.py": "atom ZQ44 " + _bulk(25)}, _bulk_ids(25)))
    assert mp.main(["--citations"]) == 1
    assert mp.PHANTOM_ATOM in capsys.readouterr().err

    monkeypatch.setattr(mp, "cited_atom_rows",
                        lambda atoms, repo=None, store_dir=None: _cite_rows(
                            {"a.py": _bulk(25)}, _bulk_ids(25)))
    assert mp.main(["--citations"]) == 0

    def _boom(atoms, repo=None, store_dir=None):
        raise RuntimeError("git grep failed")

    monkeypatch.setattr(mp, "cited_atom_rows", _boom)
    assert mp.main(["--citations"]) == 2
    assert "COULD NOT RUN" in capsys.readouterr().err


def test_a_phantom_joins_the_DEFAULT_integrity_findings_not_a_report_only_code(
        monkeypatch, capsys):
    """Deliberately UNLIKE D42 and D43. Those two are about the working tree and
    about attribution, where a repo-wide refusal would punish an honest lane
    mid-flight; a phantom id is neither, and any lane can discharge it by
    minting the cell or dropping the citation."""
    monkeypatch.setattr(mp, "cited_atom_rows",
                        lambda atoms, repo=None, store_dir=None: _cite_rows(
                            {"a.py": "atom ZQ44 " + _bulk(25)}, _bulk_ids(25)))
    assert mp.main([]) == 1
    assert mp.PHANTOM_ATOM in capsys.readouterr().err


def test_the_end_to_end_citation_check_fires_on_a_real_repo(repo: Path):
    """git grep, disk read, map read, prefix filter, resolver -- no mocks."""
    (repo / "tools").mkdir()
    (repo / "tools" / "c.py").write_text(
        "# H27 Expert Hour #29\n# mechanised as atom ZQ44, per atom ZQ5_x.\n" + _bulk(25),
        encoding="utf-8")
    store = repo / "docs" / "design" / "simplifications"
    store.mkdir(parents=True)
    _write_map(repo, [_atom(i, 2, ["tools/c.py"]) for i in _bulk_ids(25) + ["ZQ5_x"]])
    _commit(repo, EARLY)

    findings = mp.cited_atom_findings(
        mp.cited_atom_rows(mp._map_atoms(repo), repo=repo, store_dir=store))
    assert len(findings) == 1
    assert findings[0].startswith(mp.PHANTOM_ATOM) and "`atom ZQ44`" in findings[0]


def test_the_live_repo_carries_no_phantom_D_SERIES_the_mint_landed():
    """The tripwire fired and was discharged, 2026-08-14.

    It was written as `{D37..D45} <= phantoms` -- RED the day the mint landed,
    at which point the assertion was to be rewritten. The mint landed this
    tick: nine cells, D37..D45, in `docs/design/maturity_map.yaml`. So the
    assertion is now the direction that keeps meaning something -- NOT ONE of
    those nine ids may go back to being a phantom, which is what would happen
    if a cell were renamed or deleted while the nine Hours' source kept citing
    it. Still measured on the REAL bytes, never a fixture."""
    findings = mp.cited_atom_findings(mp.cited_atom_rows(mp._map_atoms()))
    phantoms = {f.split("`atom ")[1].split("`")[0]
                for f in findings if f.startswith(mp.PHANTOM_ATOM)}
    assert phantoms & {"D%d" % n for n in range(37, 46)} == set(), (
        "a minted D37..D45 cell has gone back to being a phantom -- the map "
        "was edited away from ids that nine Hours' committed source cites: "
        + ", ".join(sorted(phantoms))
    )
    assert not any("`atom W`" in f for f in findings), \
        "a lane glob is not a citation -- see the id-shape filter"
