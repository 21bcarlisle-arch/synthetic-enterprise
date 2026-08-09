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
