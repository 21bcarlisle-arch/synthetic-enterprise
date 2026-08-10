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


def _writers(text=None):
    return {_WRITER: text or f"--write-ledger\nWORLD_ATOM_ID = '{_ATOM}'\n"}


def _row(**over):
    row = {"twin_atom_id": "C1_example", "gap": 0.4,
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
        f"ap.add_argument('--write-ledger')\nWORLD_ATOM_ID = '{_ATOM}'\n")
    writers = glr.discover_writers(tmp_path)
    assert set(writers) == {"tools/couple_x_c1.py"}
    assert glr.producers_for(_ATOM, writers) == ["tools/couple_x_c1.py"]


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
             "never_landed"}
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
    return {_WRITER: f"--write-ledger\nWORLD_ATOM_ID = '{_ATOM}'\nif __name__ == '__main__':\n"}


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
    lib = {"background/fabric_gap_ledger.py": f"write_gap_entry(\nWORLD = '{_ATOM}'\n"}
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
