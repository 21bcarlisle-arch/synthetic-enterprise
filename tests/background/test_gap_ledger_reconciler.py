"""R15 for the gap-ledger family reconcile: it must be able to FAIL, able to PASS, and it must
fail CLOSED on every way of not knowing.

The named defect this control exists to catch: a gap ledger row is rendered on a public door
while the code that produced it has changed underneath, so a reader is shown a measurement taken
by a program nobody runs any more. The three fail-open shapes a freshness check is exposed to are
each pinned below: FAIL-OPEN on missing fields, FAIL-SILENT when git cannot grade the commit, and
TAUTOLOGY (attributing a row to a module that merely READS it, which would make "the producer has
not changed" true by construction for readers that never change).

Every unit test injects its own world -- ledger, writers, declared set, family, and the git
answer -- so none of them reads live disk (feedback_new_draw_rung_needs_fixture_isolation). The
two tests that DO read live state say so in their names and assert only structural properties.
"""
import subprocess

from background import gap_ledger_reconciler as glr

_WRITER = "tools/couple_x_c1.py"
_ATOM = "W9_1_example_world"


# A writer fixture is now a module with a real WRITE SITE, not one that merely spells the atom id.
# Before 2026-08-19 `producers_for` attributed by substring, so `WORLD_ATOM_ID = '...'` alone was
# enough and this fixture could not tell a producer from a file that mentions one. Attribution is
# an AST resolution from a `write_gap_entry(...)` argument, so the fixture states the write.
def _writer_source(atom=_ATOM, twin="C1_example"):
    return (f"--write-ledger\nWORLD_ATOM_ID = '{atom}'\nTWIN_ATOM_ID = '{twin}'\n"
            "def run():\n    write_gap_entry(WORLD_ATOM_ID, TWIN_ATOM_ID, result)\n")


def _writers(text=None):
    return {_WRITER: text or _writer_source()}


def _row(**over):
    # `metric` and a support key are part of the DEFAULT because every live ledger row carries
    # both, and because the support pass added 2026-08-12 refuses a second measurement it cannot
    # grade. Without them here that refusal would sit in front of the freshness tests below and
    # quietly re-point them at itself -- the relocation shape this project has already been bitten
    # by (feedback_a_new_refusal_relocates_a_sibling_assertion_behind_it). The descriptor-less and
    # undeclared-family shapes are exercised on purpose, by the tests that name them.
    row = {"twin_atom_id": "C1_example", "gap": 0.4, "metric": "detection",
           "components": {"universe_size": 1557, "truth_size": 31},
           "run_git_commit": "a" * 40, "measured_at": "2026-08-09T00:00:00+00:00"}
    row.update(over)
    return row


def _reconcile(ledger, since=0, **kw):
    kw.setdefault("writers", _writers())
    kw.setdefault("declared", set())
    kw.setdefault("family", [])
    return glr.reconcile(ledger=ledger, since_fn=lambda sha, paths: since, **kw)


def _status(results, item):
    return next(r["status"] for r in results if r["item"] == item)


# --- the control CAN pass -------------------------------------------------------------------
# A band nobody has ever seen pass is indistinguishable from one that cannot, and a control that
# can only fail wedges whatever it gates (feedback_control_that_can_only_fail_wedges).

def test_a_row_whose_producers_have_not_moved_is_CURRENT_and_the_reconcile_reads_clean():
    results = _reconcile({_ATOM: _row()}, since=0)
    assert _status(results, _ATOM) == glr.CURRENT
    assert glr.drift(results) == []
    assert "clean" in glr.summary_lines(results)[0]


# --- the control CAN fail, on its own named defect -------------------------------------------

def test_a_row_whose_producer_changed_since_its_own_commit_is_STALE():
    results = _reconcile({_ATOM: _row()}, since=3)
    assert _status(results, _ATOM) == "stale"
    detail = next(r["detail"] for r in results if r["item"] == _ATOM)
    assert "3 commit(s)" in detail and _WRITER in detail
    assert [r["item"] for r in glr.drift(results)] == [_ATOM]


# --- fail CLOSED on every way of not knowing --------------------------------------------------

def test_a_row_with_no_run_git_commit_is_DRIFT_not_silently_current():
    results = _reconcile({_ATOM: _row(run_git_commit=None)}, since=0)
    assert _status(results, _ATOM) == "unattributable"


def test_a_row_with_no_measured_at_is_DRIFT_not_silently_current():
    results = _reconcile({_ATOM: _row(measured_at="")}, since=0)
    assert _status(results, _ATOM) == "unattributable"


def test_a_sha_GIT_CANNOT_GRADE_is_DRIFT_an_unavailable_check_is_a_failed_check():
    """The FAIL-SILENT shape: `git log <sha>..HEAD` returns non-zero for a commit that is not in
    this repo, and a checker that read that as "no commits since" would pass every row measured
    on a branch that never landed."""
    results = _reconcile({_ATOM: _row()}, since=None)
    assert _status(results, _ATOM) == "unattributable"


def test_a_row_shaped_wrong_is_DRIFT_not_a_crash():
    results = _reconcile({_ATOM: "not-an-object"}, since=0)
    assert _status(results, _ATOM) == "unattributable"


def test_a_row_no_writer_names_has_NO_PRODUCER_and_that_is_drift():
    results = _reconcile({"W9_9_unwritten": _row()}, since=0)
    assert _status(results, "W9_9_unwritten") == "no_producer"


# --- the TAUTOLOGY shape ----------------------------------------------------------------------

def test_a_module_that_only_READS_the_ledger_is_not_discovered_as_a_producer(tmp_path):
    """`background/coupled_triad.py` names half these atoms in its coupling table and
    `tools/generate_premise_demand_data.py` reads the ledger for the site. Attributing a row to
    its reader would make freshness true by construction: readers change on a different clock
    from the code that took the measurement. Exercised through the real discovery seam on a tmp
    tree -- injecting the writer map would bypass the very filter under test."""
    (tmp_path / "tools").mkdir()
    (tmp_path / "background").mkdir()
    (tmp_path / "background" / "reader.py").write_text(
        f"GAP_LEDGER_PATH = 'coupled_gap_ledger.json'\nCOUPLING = {{'{_ATOM}': 'C1'}}\n")
    (tmp_path / "tools" / "couple_x_c1.py").write_text(
        f"ap.add_argument('--write-ledger')\n{_writer_source()}")
    writers = glr.discover_writers(tmp_path)
    assert set(writers) == {"tools/couple_x_c1.py"}
    assert glr.producers_for(_ATOM, writers, project_dir=tmp_path) == ["tools/couple_x_c1.py"]


# --- the family-level halves ------------------------------------------------------------------

def test_a_declared_coupled_pair_with_no_ledger_row_is_NEVER_MEASURED():
    results = glr.reconcile(ledger={}, writers=_writers(), declared={"W9_2_uncoupled"},
                            family=[], since_fn=lambda sha, paths: 0)
    assert _status(results, "W9_2_uncoupled") == "never_measured"


def test_a_family_tool_whose_output_appears_in_no_row_is_NEVER_LANDED():
    """The orphan-transition class in its family form: a couple_* tool with a green test, a
    --write-ledger flag, and no number anywhere. Found live on tools/couple_cohort.py."""
    results = glr.reconcile(ledger={}, writers=_writers(), declared=set(),
                            family=["tools/couple_orphan.py"], since_fn=lambda sha, paths: 0)
    assert _status(results, "tools/couple_orphan.py") == "never_landed"


def test_a_family_tool_that_DID_land_a_row_is_not_reported_as_never_landed():
    results = glr.reconcile(ledger={_ATOM: _row()}, writers=_writers(), declared=set(),
                            family=[_WRITER], since_fn=lambda sha, paths: 0)
    assert [r["item"] for r in glr.drift(results)] == []


# --- live structural checks (read real disk; assert shape, never a pinned number) --------------

def test_discovery_reads_SOURCE_so_the_family_cannot_be_escaped_by_not_editing_a_list():
    """An index that must be hand-edited is fail-open by construction. The expectation here is
    derived from the glob, not from any list inside the module under test."""
    writers = glr.discover_writers()
    family = glr.family_members()
    assert "tools/couple_fabric.py" in family
    assert set(family) - set(writers) == set(), "every couple_* tool must be a discovered writer"
    assert "background/coupled_triad.py" not in writers, "the L3 gate reads the ledger, not writes"


def test_commits_since_returns_None_for_a_sha_this_repo_has_never_seen():
    """Independence: this exercises real git rather than the module's own notion of failure."""
    assert glr.commits_since("f" * 40, ["background/gap_ledger_reconciler.py"]) is None
    assert glr.commits_since("", ["background/gap_ledger_reconciler.py"]) is None
    assert glr.commits_since("HEAD", []) is None


def test_commits_since_counts_real_commits_on_a_real_path():
    head = subprocess.run(["git", "-C", str(glr.PROJECT_DIR), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    assert glr.commits_since(head, ["docs/design/maturity_map.yaml"]) == 0


def test_every_live_ledger_row_gets_a_verdict_from_the_known_set():
    """The reconcile must be total over the ledger it actually has: a row it cannot classify is a
    row it would silently drop."""
    known = {glr.CURRENT, "stale", "unattributable", "no_producer", "never_measured",
             "never_landed", glr.SUPPORT_CHANGED, glr.SUPPORT_UNGRADEABLE}
    # The REAL ledger, explicitly. This directory's conftest pins `glr.LEDGER_PATH` at an absent
    # file to keep the rest-ladder tests off live disk, so a bare `reconcile()` here graded an
    # empty dict and this test asserted nothing about any real row (it read as green throughout).
    real = glr.PROJECT_DIR / "docs" / "observability" / "coupled_gap_ledger.json"
    ledger = glr.load_ledger(real)
    assert ledger, f"no live gap rows at {real} -- this test is vacuous, not passing"
    results = glr.reconcile(ledger=ledger)
    live_rows = {r["item"] for r in results if r["kind"] == "row"}
    assert live_rows == set(ledger)
    assert {r["status"] for r in results} <= known


# --- THE WORK LIST: which stale rows a re-run could actually clear ---------------------------
# The drift set above is only half a control until something can act on it. `refresh_work` is the
# DRAIN: it names the rows a re-measurement would clear and the command that takes it. These pin
# the three ways that list could lie -- offering a command that cannot re-take the row, hiding a
# row that has no runner, and including an item no re-run could ever clear (which would wedge the
# draw rung that consumes it: background/supervisor.py::_stale_gap_row_draw).

def _runner_writers():
    # Valid Python, deliberately: attribution parses the source now, so a fixture that is not a
    # module was never a stand-in for a writer. The dangling `if` this used to carry raised
    # SyntaxError and reported `attribution_unresolved` -- the fail-closed branch working.
    return {_WRITER: _writer_source() + "if __name__ == '__main__':\n    main()\n"}


def test_a_stale_row_yields_the_command_that_would_re_take_it():
    results = _reconcile({_ATOM: _row()}, since=3, writers=_runner_writers())
    work = glr.refresh_work(results, writers=_runner_writers())
    assert [w["item"] for w in work] == [_ATOM]
    assert work[0]["command"] == "python3 -m tools.couple_x_c1 --write-ledger"
    assert work[0]["no_runner"] is False


def test_the_command_is_the_MODULE_form_because_the_path_form_dies_on_import():
    """Found by RUNNING one, not reading it: `python3 tools/couple_w2_4_c6.py --write-ledger`
    fails with ModuleNotFoundError: simulation, `python3 -m tools.couple_w2_4_c6` writes the row.
    A work list whose command cannot execute is a work list nobody can act on."""
    assert glr.refresh_command(["tools/couple_w2_4_c6.py"]).startswith(
        "python3 -m tools.couple_w2_4_c6")
    assert ".py" not in glr.refresh_command(["tools/couple_w2_4_c6.py"])


def test_a_CURRENT_row_yields_no_work_so_the_drain_can_reach_empty():
    """Measured live on 2026-08-10: re-running one tool moved the drift set 11 -> 10 and its row
    read CURRENT. A work list that never empties is a treadmill, not a control."""
    results = _reconcile({_ATOM: _row()}, since=0, writers=_runner_writers())
    assert glr.refresh_work(results, writers=_runner_writers()) == []


def test_a_row_whose_only_producer_cannot_be_RUN_stays_listed_as_no_runner():
    """FAIL-CLOSED. `background/fabric_gap_ledger.py` writes rows through a function and has no
    `__main__` -- it is a producer, not a runner. A refreshable row with no runner is a WORSE
    defect (a published number nobody can re-take), so it must stay in the list rather than be the
    one entry that silently disappears (feedback_coverage_derived_from_exclusion_source_is_failopen)."""
    lib = {"background/fabric_gap_ledger.py":
           f"WORLD = '{_ATOM}'\ndef write():\n    write_gap_entry(WORLD, twin, result)\n"}
    results = _reconcile({_ATOM: _row()}, since=3, writers=lib)
    work = glr.refresh_work(results, writers=lib)
    assert [w["item"] for w in work] == [_ATOM]
    assert work[0]["command"] is None and work[0]["no_runner"] is True


def test_a_row_with_no_run_git_commit_is_refreshable_because_re_measuring_clears_it():
    results = _reconcile({_ATOM: _row(run_git_commit=None)}, since=0, writers=_runner_writers())
    assert _status(results, _ATOM) == "unattributable"
    assert [w["item"] for w in glr.refresh_work(results, writers=_runner_writers())] == [_ATOM]


def test_an_UNREADABLE_ledger_is_ONE_defect_not_one_per_pair_and_tool(monkeypatch, tmp_path):
    """FAIL-OPEN, found by the never_landed repair above breaking a rest-ladder fixture.

    `load_ledger` returns `{}` for a file that is absent or malformed, and the reconcile then
    graded that empty dict as though the ledger legitimately held no rows: every declared pair
    came back `never_measured` and every couple_* tool came back `never_landed`. Eleven work items
    were manufactured out of ONE unread file, and the only thing that had been hiding it was the
    blanket never_landed exclusion. The verdicts were artefacts of the read failing, not facts
    about any tool (feedback_population_defined_at_as_of_is_an_artefact)."""
    monkeypatch.setattr(glr, "LEDGER_PATH", tmp_path / "not_here.json")
    results = glr.reconcile()
    assert [r["status"] for r in results] == ["ledger_unreadable"]
    assert glr.refresh_work(results, writers=_runner_writers()) == []

    (tmp_path / "not_here.json").write_text("{ this is not json")
    assert [r["status"] for r in glr.reconcile()] == ["ledger_unreadable"]


def test_a_READABLE_ledger_never_reports_unreadable_so_the_branch_can_pass(monkeypatch, tmp_path):
    """The other direction: a control nobody has seen read clean is indistinguishable from one
    that cannot. An EMPTY-but-present ledger is a real state and is NOT the unreadable defect --
    the distinction is file existence, never row count."""
    path = tmp_path / "ledger.json"
    path.write_text("{}")
    monkeypatch.setattr(glr, "LEDGER_PATH", path)
    assert glr.ledger_is_readable() is True
    assert "ledger_unreadable" not in {r["status"] for r in glr.reconcile()}


def test_a_NEVER_MEASURED_pair_is_excluded_because_there_is_nothing_to_run():
    """A pair the MAP declares with no ledger row and no producer to point at. No command exists,
    so including it would make the rung permanently non-empty and therefore ignored
    (feedback_control_that_can_only_fail_wedges)."""
    results = glr.reconcile(ledger={}, writers=_runner_writers(), declared={"WORLD_x"},
                            family=[], since_fn=lambda s, p: 0)
    assert {r["status"] for r in results} == {"never_measured"}
    assert glr.refresh_work(results, writers=_runner_writers()) == []


def test_a_NEVER_LANDED_tool_that_CAN_BE_RUN_is_drawn_because_the_run_lands_the_row():
    """THE 2026-08-10 REPAIR. The first cut swept never_landed in with never_measured under one
    sentence -- "no re-run clears a row that does not exist" -- and that is false for a tool that
    exists on disk and is invocable: running it is precisely what lands the row.
    `tools/couple_cohort.py` sat in the live drift set for two days as a permanent member no rung
    could act on, and `python3 -m tools.couple_cohort` runs clean in seconds. An exclusion that
    hides the one item a single command would close is a cleanup, not a control
    (feedback_a_ratchet_with_no_drain_is_a_cleanup_not_a_control)."""
    orphan = "tools/couple_cohort.py"
    writers = {orphan: "--write-ledger\nWORLD_ATOM_ID = 'W2_2'\nif __name__ == '__main__':\n"}
    results = glr.reconcile(ledger={}, writers=writers, declared=set(),
                            family=[orphan], since_fn=lambda s, p: 0)
    assert _status(results, orphan) == "never_landed"
    work = glr.refresh_work(results, writers=writers)
    assert [w["item"] for w in work] == [orphan]
    assert work[0]["command"] == "python3 -m tools.couple_cohort --write-ledger"
    assert work[0]["no_runner"] is False


def test_a_NEVER_LANDED_tool_that_CANNOT_BE_RUN_stays_off_the_work_list():
    """The wedge guard, kept as the NARROW rule rather than as a ban on the status. Here the item
    IS the tool: no invocable runner means no command could ever land its row, so listing it would
    make the rung permanently non-empty. This is the one place the fail-closed listing used for
    ROWS is deliberately reversed -- a stale ROW hides a live public figure behind its absence, a
    dead TOOL hides nothing. It stays reported in the DRIFT set either way."""
    orphan = "tools/couple_dead.py"
    lib = {orphan: "write_gap_entry(\n"}          # writes, but no __main__ and no flag
    results = glr.reconcile(ledger={}, writers=lib, declared=set(),
                            family=[orphan], since_fn=lambda s, p: 0)
    assert _status(results, orphan) == "never_landed"           # still visible as drift
    assert glr.refresh_work(results, writers=lib) == []         # but never offered as work


def test_a_READER_is_never_offered_as_the_command_that_refreshes_a_row():
    """The tautology guard, at the work-list layer: attributing the refresh of a row to a module
    that only reads the ledger would print a command that cannot re-take the measurement."""
    reader = {"tools/generate_premise_demand_data.py":
              f"coupled_gap_ledger.json\nif __name__ == '__main__':\n{_ATOM}\n"}
    assert glr.runners_for(list(reader), reader) == []


def test_every_live_refreshable_row_carries_a_status_the_reconcile_can_clear():
    """Independence: read against live disk, asserting only that the work list is a SUBSET of the
    drift set and never invents an item the reconcile did not report."""
    results = glr.reconcile()
    drifting = {r["item"] for r in glr.drift(results)}
    work = glr.refresh_work(results)
    assert {w["item"] for w in work} <= drifting
    assert all(w["status"] in glr.REFRESHABLE_STATUSES for w in work)


def test_a_producer_that_only_MENTIONS_the_flag_is_not_invocable():
    """The runner test has two halves and both have to bite: writes the ledger AND can be run.
    A library whose docstring mentions `--write-ledger` (this reconciler's own source does, in the
    marker regex) is not a command anyone can type at it."""
    prose = {"background/fabric_gap_ledger.py":
             f"'''rows land when a tool passes --write-ledger.'''\nwrite_gap_entry(\n{_ATOM}\n"}
    assert glr.runners_for(list(prose), prose) == []


# --- THE GRADED SUBJECT IS THE COMMITTED LEDGER (2026-08-11) ---------------------------------
# Named defect: this module graded the WORKING TREE file while the public door renders the
# COMMITTED one, so a re-run that was never committed moved the checked value and left the
# published value stale -- and the control reported `clean` over it. Live evidence at the time:
# working tree read "clean -- all 14 rows", HEAD read DRIFT on W2_11_payment_behaviour_source.

def test_a_row_stale_at_HEAD_but_re_measured_on_disk_is_MEASURED_NOT_LANDED_not_current():
    """THE FAIL-OPEN ITSELF. The disk row is current; the committed row is not. Reporting this
    as `current` (grading disk) is the defect -- the door still shows the old number."""
    results = _reconcile({_ATOM: _row()}, since=3, unlanded={_ATOM: _row()})
    # since_fn is injected as a constant, so the disk row would grade stale too -- pin the
    # asymmetry explicitly instead, with a since_fn that answers per-sha.
    results = glr.reconcile(
        ledger={_ATOM: _row(run_git_commit="a" * 40)},
        unlanded={_ATOM: _row(run_git_commit="b" * 40)},
        writers=_writers(), declared=set(), family=[],
        since_fn=lambda sha, paths: 0 if sha == "b" * 40 else 3)
    assert _status(results, _ATOM) == glr.MEASURED_NOT_LANDED
    assert _status(results, _ATOM) != glr.CURRENT, "grading the working tree is the fail-open"
    assert glr.drift(results), "a measured-but-unlanded row must not read clean"


def test_MEASURED_NOT_LANDED_is_drawn_as_a_LAND_not_a_RE_RUN():
    """The repair is to commit the measurement. Re-running republishes a figure that can move,
    to fix a problem that was only ever that the existing figure was never committed."""
    results = glr.reconcile(
        ledger={_ATOM: _row(run_git_commit="a" * 40)},
        unlanded={_ATOM: _row(run_git_commit="b" * 40)},
        writers=_writers(), declared=set(), family=[],
        since_fn=lambda sha, paths: 0 if sha == "b" * 40 else 3)
    work = glr.refresh_work(results, writers=_writers())
    entry = next(w for w in work if w["item"] == _ATOM)
    assert "surgical_land" in entry["command"]
    assert "--write-ledger" not in entry["command"], "must not re-take an existing measurement"


def test_a_row_stale_at_HEAD_with_NO_disk_measurement_stays_STALE():
    """The overlay must not swallow the ordinary case: no disk row means nothing was re-taken,
    so the work really is a re-run. Without this the new status could mask every stale row."""
    results = glr.reconcile(
        ledger={_ATOM: _row()}, unlanded={}, writers=_writers(), declared=set(), family=[],
        since_fn=lambda sha, paths: 3)
    assert _status(results, _ATOM) == "stale"


def test_a_ledger_that_reads_on_disk_but_NOT_at_HEAD_is_drift_not_clean(monkeypatch, tmp_path):
    """FAIL-CLOSED. An uncommitted ledger cannot describe the door. It must not fall back to
    the working tree and report row verdicts as though they were published."""
    path = tmp_path / "coupled_gap_ledger.json"
    path.write_text('{"%s": {"gap": 0.4}}' % _ATOM)
    monkeypatch.setattr(glr, "LEDGER_PATH", path)
    assert glr.ledger_is_readable() is True
    assert glr.landed_ledger() is None, "a path outside the repo is not readable at HEAD"
    assert [r["status"] for r in glr.reconcile()] == ["ledger_not_committed"]


# The REAL ledger, explicitly: this directory's conftest pins `glr.LEDGER_PATH` at an absent file
# to keep the rest-ladder tests off live disk, so a bare `landed_ledger()` here reads None and
# every assertion below it would be vacuous rather than true.
_REAL_LEDGER = glr.PROJECT_DIR / "docs" / "observability" / "coupled_gap_ledger.json"


def test_landed_ledger_CAN_read_so_the_HEAD_branch_can_pass():
    """The HEAD read must be able to succeed on the real tracked ledger -- a branch that can
    only fail would wedge every live reconcile at `ledger_not_committed`."""
    landed = glr.landed_ledger(_REAL_LEDGER)
    assert isinstance(landed, dict) and landed, "the real ledger must read at HEAD"


# --- THE GRADER IS NOT ITS OWN PRODUCER (2026-08-11) -----------------------------------------

def test_the_reconciler_is_never_discovered_as_a_writer_of_the_ledger_it_grades():
    """TAUTOLOGY, pointing at itself. This module quotes `--write-ledger`, so it matches the
    write marker; `producers_for` attributes a row to any writer whose source contains the atom
    id. The first comment here that names an atom would make every commit to the GRADER mark
    that row stale. Latent at HEAD only because the text named no atom -- armed by one comment.
    """
    writers = glr.discover_writers()
    assert glr._SELF not in writers
    # and the marker really does match it, i.e. the exclusion is load-bearing, not decorative
    from pathlib import Path
    assert glr._WRITE_MARKER.search((glr.PROJECT_DIR / glr._SELF).read_text())


def test_a_real_ledger_row_never_attributes_itself_to_the_grader():
    """Population form of the above, over the live ledger: no row may name this module as a
    producer, on any atom id, however the module's prose changes."""
    writers = glr.discover_writers()
    landed = glr.landed_ledger(_REAL_LEDGER)
    assert landed, "vacuity guard -- an unread ledger would pass this loop trivially"
    for atom_id in landed:
        assert glr._SELF not in glr.producers_for(atom_id, writers), atom_id


# FAIL-SILENT, the third killer pattern: the checker itself unavailable. Added 2026-08-11 because
# a mutation survived -- `landed_ledger` falling back to `load_ledger(path)` on a git failure was
# caught by NO test. The outside-the-repo test above returns before git is ever called, so it
# proved nothing about what happens when git answers badly. An unavailable check is a FAILED
# check, and here the fail-open is silent: it would resume grading the working tree, which is the
# precise defect this whole section exists to remove.

def _failing_run(*a, **k):
    class _P:
        returncode = 1
        stdout = ""
        stderr = "fatal: path does not exist in HEAD"
    return _P()


def test_landed_ledger_returns_None_when_git_CANNOT_answer_and_never_falls_back_to_disk(
        monkeypatch):
    monkeypatch.setattr(glr.subprocess, "run", _failing_run)
    assert glr.landed_ledger(_REAL_LEDGER) is None, (
        "a git failure must not fall back to the working-tree ledger -- that silently restores "
        "the working-tree-subject fail-open")


def test_landed_ledger_returns_None_when_git_is_UNAVAILABLE(monkeypatch):
    def _boom(*a, **k):
        raise OSError("git not found")
    monkeypatch.setattr(glr.subprocess, "run", _boom)
    assert glr.landed_ledger(_REAL_LEDGER) is None


def test_a_git_failure_makes_the_whole_reconcile_report_drift_not_row_verdicts(monkeypatch):
    """Population form: the reconcile must not emit per-row verdicts it cannot ground."""
    monkeypatch.setattr(glr, "LEDGER_PATH", _REAL_LEDGER)
    monkeypatch.setattr(glr.subprocess, "run", _failing_run)
    results = glr.reconcile()
    assert [r["status"] for r in results] == ["ledger_not_committed"]
    assert glr.drift(results)


# --- THE REFRESH COMMAND MUST REPRODUCE THE ROW -----------------------------------------------
# 2026-08-11, H_GAP_fabric_belief_truth_gap Expert Hour. The named defect: `refresh_command`
# emitted the BASE invocation, so for a tool whose default population differs from the one the
# row was measured on, the drain's own acceptance test ("the row reads CURRENT afterwards") is
# satisfied by a re-run that REPLACES the quantity instead of re-taking it. Observed on the real
# ledger: `W1_11_fabric_physics_core` carries 200 DRAWN premises, `python3 -m tools.couple_fabric
# --write-ledger` measures 15 AUTHORED ones, and `inference_improvement` moves +0.0227 -> -0.0440
# -- a SIGN flip on a published claim. The row now declares the args that reproduce it.

_INVOCABLE = (_writer_source() + "if __name__ == '__main__':\n    main()\n")

def test_a_row_that_declares_its_arguments_is_refreshed_WITH_them():
    """The defect, directly: a declared population must survive into the command."""
    results = glr.reconcile(
        ledger={_ATOM: _row(components={"refresh_args": ["--population", "200",
                                                         "--population-seed", "17"]})},
        writers=_writers(_INVOCABLE), declared={_ATOM: "C1_example"}, family=[_WRITER],
        since_fn=lambda *_a, **_k: 3,
    )
    work = glr.refresh_work(results, writers=_writers(_INVOCABLE), ledger={
        _ATOM: {"components": {"refresh_args": ["--population", "200",
                                                "--population-seed", "17"]}}})
    assert [w["command"] for w in work] == [
        "python3 -m tools.couple_x_c1 --write-ledger --population 200 --population-seed 17"]


def test_a_row_declaring_NOTHING_still_gets_the_base_invocation():
    """Able to PASS, and no regression for the rows that predate the declaration: absence of
    `refresh_args` must behave exactly as this function did before it existed."""
    results = glr.reconcile(
        ledger={_ATOM: _row()}, writers=_writers(_INVOCABLE), declared={_ATOM: "C1_example"},
        family=[_WRITER], since_fn=lambda *_a, **_k: 3,
    )
    work = glr.refresh_work(results, writers=_writers(_INVOCABLE), ledger={_ATOM: {"components": {}}})
    assert [w["command"] for w in work] == ["python3 -m tools.couple_x_c1 --write-ledger"]


def test_the_ledger_may_not_inject_anything_but_a_flag_or_a_number():
    """The ledger is DATA and this output is RUN by a tick. A row that declares a path, a shell
    metacharacter, a `--flag=value` pair or an env assignment is refused WHOLE -- falling back to
    the base invocation, which is the pre-existing behaviour, never a partially-trusted line."""
    for hostile in (["; rm -rf /"], ["--population", "200; curl evil"], ["$(id)"],
                    ["--out=/etc/passwd"], ["--population", "&& echo"], ["PATH=/tmp"],
                    ["../../etc/passwd"], ["--population", "200", "|tee"]):
        assert glr.safe_refresh_args(hostile) == [], hostile
        assert glr.refresh_command([_WRITER], hostile) == (
            "python3 -m tools.couple_x_c1 --write-ledger")
    # ... and the benign shapes the tools actually emit are kept.
    assert glr.safe_refresh_args(["--seed", "17", "--unit-rate", "7.4", "--premises", "-1"]) == [
        "--seed", "17", "--unit-rate", "7.4", "--premises", "-1"]


def test_a_non_list_declaration_is_ignored_rather_than_crashing_the_drain():
    """FAIL-SAFE on a malformed field: the work list is how a stuck tick finds its work, so a
    junk `refresh_args` must cost the arguments, never the list."""
    for junk in (None, "population 200", 200, {"population": 200}):
        assert glr.safe_refresh_args(junk) == []
        assert glr.refresh_command([_WRITER], junk) == "python3 -m tools.couple_x_c1 --write-ledger"


# --- SUPPORT: the row's population, not just the commit that measured it ----------------------
# WORKER_FINDING_THE_REFRESH_COMMAND_CAN_CHANGE_THE_POPULATION_2026-08-10 (BLOCKING, H_harness).
# The named defect: RUNG 4b's refresh command re-took `W2_11_payment_behaviour_source` against
# the TOOL's CLI defaults rather than the row's own population -- gap 0.0859 -> 0.0131 with
# `universe_size` 1557 -> 12000 -- and every status here called the replacement a refresh.
# These pin the fix in both directions and, per R15, the ways it could fail to be a control:
# always-red on rows with no descriptor, silent on the `current` branch, and a naming rule that
# cannot tell a POPULATION from an OUTCOME.

def _sized(universe, truth, **over):
    """A detection-family row, the family the finding was found on."""
    comps = {"universe_size": universe, "truth_size": truth, "caught": 3, "n_false_flags": 1}
    comps.update(over.pop("components", {}))
    return _row(metric="detection", components=comps, **over)


def _both(head, disk, since=None):
    return glr.reconcile(ledger={_ATOM: head}, unlanded={_ATOM: disk},
                         writers=_writers(), declared=set(), family=[],
                         since_fn=since or (lambda sha, paths: 0))


def test_a_re_measurement_on_a_DIFFERENT_POPULATION_is_SUPPORT_CHANGED_not_a_refresh():
    """THE FINDING, reproduced at the shape it was found in: same row name, same metric, a
    population 7.7x larger. Provenance is perfect -- and the quantity has been replaced."""
    results = _both(_sized(1557, 31), _sized(12000, 1215, run_git_commit="b" * 40))
    assert _status(results, _ATOM) == glr.SUPPORT_CHANGED
    detail = next(r["detail"] for r in results if r["item"] == _ATOM)
    assert "universe_size 1557 -> 12000" in detail
    assert "truth_size 31 -> 1215" in detail
    assert glr.drift(results), "a replaced quantity must not read clean"


def test_the_population_swap_is_caught_on_a_row_that_grades_CURRENT():
    """THE FAIL-OPEN THIS PASS EXISTS FOR. The `measured_not_landed` overlay skips `current`
    rows, and a re-run on unchanged code lands exactly there: both measurements are attributable
    to code that has not moved, so freshness is satisfied and the population still swapped.
    Grading this `current` is the silence the finding names."""
    results = _both(_sized(1557, 31), _sized(12000, 1215))
    assert _status(results, _ATOM) != glr.CURRENT
    assert _status(results, _ATOM) == glr.SUPPORT_CHANGED


def test_SUPPORT_CHANGED_IS_NOT_OFFERED_A_COMMAND_so_the_drain_cannot_publish_it():
    """R11, THE RELEASE: the status has to DO something or it is a label. Same two rows, same
    staleness -- the only difference is whether the population moved. With it unchanged the
    drain hands over the `surgical_land` command; with it moved the drain offers nothing at all,
    which is the automatic republish of a replaced figure not happening."""
    def stale_at_head(sha, paths):
        return 0 if sha == "b" * 40 else 3

    same_pop = _both(_sized(1557, 31), _sized(1557, 31, run_git_commit="b" * 40),
                     since=stale_at_head)
    assert _status(same_pop, _ATOM) == glr.MEASURED_NOT_LANDED
    landed = glr.refresh_work(same_pop, writers=_writers())
    assert "surgical_land" in next(w for w in landed if w["item"] == _ATOM)["command"]

    moved_pop = _both(_sized(1557, 31), _sized(12000, 1215, run_git_commit="b" * 40),
                      since=stale_at_head)
    assert _status(moved_pop, _ATOM) == glr.SUPPORT_CHANGED
    work = glr.refresh_work(moved_pop, writers=_writers())
    assert not [w for w in work if w["item"] == _ATOM], (
        "a row whose population moved must not be handed a command -- re-running reproduces "
        "the replacement and landing it is the act that needs deciding")


def test_a_re_measurement_on_the_SAME_population_is_NOT_support_changed():
    """NOT ALWAYS RED. The ordinary honest re-measurement -- new numbers, same population --
    must keep reading `measured_not_landed` and stay drainable."""
    results = _both(_sized(1557, 31, gap=0.4),
                    _sized(1557, 31, gap=0.31, run_git_commit="b" * 40),
                    since=lambda sha, paths: 0 if sha == "b" * 40 else 3)
    assert _status(results, _ATOM) == glr.MEASURED_NOT_LANDED


def test_a_moved_OUTCOME_is_not_a_moved_POPULATION():
    """The register discriminates support from outcome, which a name-shaped rule cannot:
    `caught` and `n_false_flags` are `n_*`/count-shaped and are results OF the measurement.
    Reading them as support would cry population-moved on every real re-measurement."""
    results = _both(_sized(1557, 31, components={"caught": 3, "n_false_flags": 1}),
                    _sized(1557, 31, components={"caught": 99, "n_false_flags": 40},
                           run_git_commit="b" * 40),
                    since=lambda sha, paths: 0 if sha == "b" * 40 else 3)
    assert _status(results, _ATOM) == glr.MEASURED_NOT_LANDED


def test_a_SECOND_measurement_of_a_row_with_no_support_descriptor_is_UNGRADEABLE():
    """FAIL-SILENT, refused. `W1_5`, `W1_6`, `W2_4` and `W2_6` record no population size at all.
    Their re-measurements must not be landed on the strength of a check that could not run."""
    bare = _row(metric="prediction", components={"mae_model": 0.1})
    results = _both(bare, _row(metric="prediction", components={"mae_model": 0.2},
                               run_git_commit="b" * 40),
                    since=lambda sha, paths: 0 if sha == "b" * 40 else 3)
    assert _status(results, _ATOM) == glr.SUPPORT_UNGRADEABLE
    assert not [w for w in glr.refresh_work(results, writers=_writers()) if w["item"] == _ATOM]


def test_an_UNDECLARED_metric_family_fails_CLOSED_rather_than_comparing_nothing():
    """Two rows with no declared support keys compare EQUAL as empty dicts if the descriptor is
    allowed to be empty -- the fail-open that would pass every unknown family silently."""
    novel = _row(metric="a_metric_family_invented_after_this_register", components={"x": 1})
    results = _both(novel, _row(metric="a_metric_family_invented_after_this_register",
                                components={"x": 2}, run_git_commit="b" * 40),
                    since=lambda sha, paths: 0 if sha == "b" * 40 else 3)
    assert _status(results, _ATOM) == glr.SUPPORT_UNGRADEABLE


def test_a_support_key_that_VANISHES_between_measurements_is_a_change():
    """Dropping the descriptor is not agreeing with it. Without this a writer could clear every
    support verdict by recording less."""
    results = _both(_sized(1557, 31),
                    _row(metric="detection", components={"truth_size": 31},
                         run_git_commit="b" * 40),
                    since=lambda sha, paths: 0 if sha == "b" * 40 else 3)
    assert _status(results, _ATOM) == glr.SUPPORT_CHANGED
    assert "universe_size 1557 -> absent" in next(
        r["detail"] for r in results if r["item"] == _ATOM)


def test_a_non_integer_size_is_not_read_as_support():
    """A population size that arrived as a float or a flag is a descriptor this cannot compare;
    reading it anyway would be the fail-open. Bools are ints in Python and are excluded by name."""
    assert glr.row_support(_row(metric="detection",
                                components={"universe_size": 1557.0}))[0] is None
    assert glr.row_support(_row(metric="detection",
                                components={"universe_size": True}))[0] is None
    assert glr.row_support(_row(metric="detection",
                                components={"universe_size": 1557}))[0] == {"universe_size": 1557}


def test_a_row_with_ONE_measurement_gets_NO_support_verdict_even_with_no_descriptor():
    """THE UNCLEARABLE-ALARM GUARD. Identical committed and disk rows are ONE measurement, so
    there is no comparison to make. Without this condition the four descriptor-less rows would
    report UNGRADEABLE on every clean reconcile forever -- an alarm no act can clear."""
    bare = _row(metric="prediction", components={"mae_model": 0.1})
    results = _both(bare, dict(bare))
    assert _status(results, _ATOM) == glr.CURRENT
    assert glr.drift(results) == []


def test_the_live_ledger_says_which_rows_can_answer_the_support_question():
    """Reads the REAL ledger. Not a pin on the four names -- a pin that the register still
    resolves the live rows it claims to, so a writer that stops recording its population, or a
    metric family added without a declaration, shows up here instead of going quiet."""
    real = glr.PROJECT_DIR / "docs" / "observability" / "coupled_gap_ledger.json"
    ledger = glr.load_ledger(real)
    assert ledger, f"no live gap rows at {real} -- this test is vacuous, not passing"
    graded = {k: glr.row_support(v)[0] for k, v in ledger.items()}
    answerable = {k for k, v in graded.items() if v}
    assert answerable, "no live row can answer the support question -- the register resolves none"
    assert len(answerable) >= 10, (
        "the live ledger's support coverage went backwards: only "
        f"{sorted(set(ledger) - answerable)} cannot answer, expected the four known rows "
        "(W1_5, W1_6, W2_4, W2_6) at most")


# --- ATTRIBUTION IS A WRITE SITE, NOT A MENTION (2026-08-19) -----------------------------------
# WORKER_FINDING_A_GAP_ROW_IS_ATTRIBUTED_TO_ANY_WRITER_THAT_MERELY_NAMES_IT (BLOCKING, H_harness).
# The mutation and its null control, in the finding's own words: "a writer that MENTIONS a key in
# a comment only must NOT appear in that key's producer set (the mutation, which the old code
# fails); a writer that WRITES a key it does not spell in prose must still appear (the null
# control: move the sample, not the law -- otherwise 'match nothing' passes the first test)."

_OTHER = "W9_2_other_world"


def test_a_writer_that_only_MENTIONS_another_row_in_a_comment_is_not_its_producer():
    """THE MUTATION. One comment in `tools/couple_clv.py` citing a naming precedent put it in
    `WORLD_recontracting_relationship_start`'s producer set -- a row it has never computed -- and
    that suppressed `never_landed` on the file itself. The mention is the ONLY thing that moves
    here: the write site is untouched, so a rule that read text would attribute both."""
    mentioning = _writer_source() + f"# see the `{_OTHER}` precedent for the naming\n"
    writers = {_WRITER: mentioning}
    assert glr.producers_for(_ATOM, writers) == [_WRITER], "its own row must survive"
    assert glr.producers_for(_OTHER, writers) == [], "a comment is evidence of nothing"
    # and the substring rule -- what shipped until this repair -- really does fail it, so the
    # assertion above has a subject and is not true of every possible implementation
    assert _OTHER in mentioning


def test_a_writer_that_WRITES_a_key_it_never_SPELLS_is_still_its_producer():
    """THE NULL CONTROL: move the sample, not the law. `match nothing` would pass the mutation
    above. `background/live_payment_triad.py` is the live case -- it imports WORLD_ATOM_ID from
    `tools.couple_w2_11_d5` and its own text never contains `W2_11_payment_behaviour_source`, so
    the substring rule was blind to a REAL producer while attributing the row to a reader."""
    writers = glr.discover_writers()
    triad = "background/live_payment_triad.py"
    assert _ATOM not in writers[triad] and "W2_11_payment_behaviour_source" not in writers[triad], \
        "vacuity guard -- this test means nothing unless the id is genuinely absent from the text"
    assert triad in glr.producers_for("W2_11_payment_behaviour_source", writers)


def test_a_row_is_never_attributed_to_a_module_that_merely_READS_or_DOCUMENTS_it():
    """The population form, over the live ledger. Three modules were attributed by prose alone
    at HEAD c728642c3: `background/gap_metric.py` -> W2_9 (a worked example in a docstring),
    `background/fabric_gap_ledger.py` -> W1_5 (a sentence about L3), `background/
    live_ledger_guard.py` -> W2_11. None of them writes those rows."""
    writers = glr.discover_writers()
    landed = glr.landed_ledger(_REAL_LEDGER)
    assert landed, "vacuity guard -- an unread ledger would pass this loop trivially"
    index = glr.write_site_attribution(writers)
    for atom_id, producers in ((a, glr.producers_for(a, writers, index)) for a in landed):
        assert producers, f"{atom_id} lost every producer -- a row with none reads fresh forever"
        for path in producers:
            assert atom_id in index[path], f"{path} attributed to {atom_id} without a write site"
    assert "background/gap_metric.py" not in glr.producers_for("W2_9_segment_debt_tnc", writers)
    assert "background/fabric_gap_ledger.py" not in glr.producers_for(
        "W1_5_premise_demand_shape", writers)


def test_a_DELEGATED_write_attributes_the_caller_that_never_names_the_ids():
    """`tools/couple_fabric.py` calls `fgl.write_fabric_gap_entries(observations, ...)`: the ids
    are fixed inside the callee and the caller's write site names none of them. Dropping it would
    be the fail-OPEN direction -- the tool that computes W1_11/W1_12 would stop marking them
    stale. One level of delegation is resolved on purpose; a second surfaces as unresolved."""
    writers = glr.discover_writers()
    for atom_id in ("W1_11_fabric_physics_core", "W1_12_premise_trace_generator"):
        assert "tools/couple_fabric.py" in glr.producers_for(atom_id, writers), atom_id


def test_an_UNRESOLVABLE_write_site_is_reported_and_never_silently_empty():
    """FAIL-CLOSED, and the direction reversed with this repair: a missed producer no longer
    manufactures work, it makes a published row read FRESH forever. So a write site whose id this
    resolver cannot read must be drift, not an empty set. Mutation: the same module with the id
    computed at runtime instead of bound."""
    dynamic = {_WRITER: "def run(kind):\n    write_gap_entry('W9_' + kind, twin, result)\n"}
    assert glr.unresolved_write_sites(dynamic) == {_WRITER: [2]}
    results = glr.reconcile(ledger={}, writers=dynamic, declared=set(), family=[],
                            since_fn=lambda s, p: 0)
    assert _status(results, _WRITER) == glr.ATTRIBUTION_UNRESOLVED
    # NULL CONTROL: the same shape with the id bound reports nothing, so the alarm is about
    # resolvability and not about the presence of a write call
    assert glr.unresolved_write_sites(_writers()) == {}


def test_the_live_writer_family_has_no_unresolvable_write_site():
    """The live reading behind the branch above: empty today, and this is where a writer that
    starts computing its key at runtime lands instead of quietly losing its staleness signal."""
    assert glr.unresolved_write_sites(glr.discover_writers()) == {}


def test_a_marker_matched_on_PROSE_ALONE_produces_nothing():
    """`background/gap_metric.py` and `background/live_ledger_guard.py` quote `--write-ledger` in
    help text and have no write call, so `_WRITE_MARKER` discovers them. Producing nothing is the
    correct answer for them, not a miss -- and it must not be reported as unresolved either."""
    writers = glr.discover_writers()
    index = glr.write_site_attribution(writers)
    for path in ("background/gap_metric.py", "background/live_ledger_guard.py"):
        assert path in writers, f"{path} must still be discovered -- else this asserts nothing"
        assert index[path] == set()
        assert path not in glr.unresolved_write_sites(writers)
