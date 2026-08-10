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
    results = glr.reconcile()
    live_rows = {r["item"] for r in results if r["kind"] == "row"}
    assert live_rows == set(glr.load_ledger())
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


def test_NEVER_LANDED_and_NEVER_MEASURED_are_excluded_because_no_re_run_clears_them():
    """The rung that consumes this list must be able to DRAIN. `tools/couple_cohort.py` has landed
    no row at all and `WORLD_x` is a declared pair with no row -- re-running changes neither, so
    including them would make the rung permanently non-empty and therefore ignored
    (feedback_control_that_can_only_fail_wedges)."""
    results = glr.reconcile(ledger={}, writers=_runner_writers(), declared={"WORLD_x"},
                            family=["tools/couple_cohort.py"], since_fn=lambda s, p: 0)
    assert {r["status"] for r in results} == {"never_measured", "never_landed"}
    assert glr.refresh_work(results, writers=_runner_writers()) == []


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
