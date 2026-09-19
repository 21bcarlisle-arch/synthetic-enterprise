"""The publish commit must carry the ledger its published series was built from.

THE DEFECT THESE CONTROL, measured 2026-09-19. `docs/observability/run_history.json` is tracked,
is read by `tools.generate_dashboard_data.extract_run_history` / `count_run_history_total` and is
named by `background.naive_organ.detect_t6` as its own raw data -- and it was in no commit's
pathspec. So `site/data/dashboard.json` was committed fresh on every publish cycle while the
ledger it was built from stayed at its 2026-07-17 bytes for 64 days. Every fresh checkout, which
is every isolated worktree and every fork, held a published artefact none of its own inputs could
reproduce; T6's verdict on the status page inverted depending on which copy the reader had.

WHY NOTHING RED ON IT AND NOTHING COULD: the file was present, it parsed, and it returned a
number. There is no natural edge in a read-modify-write that never commits. The edge has to be
built, and it has to be built on the TREE THE COMMIT CREATES rather than on the working copy,
because the working copy was always right -- that is precisely why it went unnoticed.

KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. Not "the ledger has 100 entries" (goes green the
day the file is deleted) and not "the last entry is 52f572916" (goes red the day a run succeeds).
The property is: *a run the committed dashboard publishes can be found in the committed ledger*.
It tolerates the ledger being AHEAD of the dashboard -- the benign direction, one cycle's skew --
and fails when the ledger is BEHIND, which is the whole of the defect.
"""

import inspect
import json
from pathlib import Path

import pytest

import background.process_run_complete as prc

PROJECT = Path(__file__).resolve().parents[2]
DASHBOARD = PROJECT / "site" / "data" / "dashboard.json"
LEDGER = PROJECT / "docs" / "observability" / "run_history.json"


def _load(path):
    """Read a published artefact, or FAIL -- absent and unreadable are not passes here.

    A `return None` on a missing file would make every leg below vacuous in exactly the tree
    where the question matters most: the extract `surgical_land` gates, where a path left out of
    the pathspec is simply not there."""
    if not path.exists():
        pytest.fail("{} is absent from this tree, so the question cannot be asked -- which is "
                    "the failing answer, not a reason to skip".format(path.relative_to(PROJECT)))
    try:
        return json.loads(path.read_text())
    except (ValueError, OSError) as exc:
        pytest.fail("{} did not parse: {}".format(path.relative_to(PROJECT), exc))


def test_every_run_the_committed_dashboard_publishes_is_in_the_committed_ledger():
    """THE DEFECT: the site publishes a run-history series its own committed source lacks.

    Read off disk rather than through `git show`, on purpose: `surgical_land` gates an extract
    that has no `.git`, and the tree the commit would create is exactly the subject. On the
    shared working tree this asks a weaker question (both copies are live there) and still
    answers it truthfully."""
    dashboard = _load(DASHBOARD)
    series = dashboard.get("run_history") or []

    # NON-VACUITY FIRST. An empty series would satisfy "every entry is in the ledger" trivially,
    # and an empty published series is itself the failure -- the control's own filters must not
    # be allowed to empty the evidence set.
    assert series, (
        "site/data/dashboard.json publishes an EMPTY run_history. Either the ledger it is built "
        "from has gone missing from the build's tree, or `extract_run_history` is failing "
        "closed -- both are the defect this control exists for, not a pass.")

    ledger = _load(LEDGER)
    assert isinstance(ledger, list) and ledger, (
        "docs/observability/run_history.json is not a non-empty list, so the published series "
        "above stands on nothing this tree contains.")

    committed_runs = {entry.get("git_hash") for entry in ledger if isinstance(entry, dict)}
    missing = [e.get("git_hash") for e in series if e.get("git_hash") not in committed_runs]
    assert not missing, (
        "The committed dashboard publishes {} run(s) that the committed ledger cannot account "
        "for: {}. The published series and the source it was built from are different vintages "
        "-- the 64-day divergence of 2026-09-19. Whatever wrote dashboard.json must commit "
        "docs/observability/run_history.json in the SAME commit.".format(len(missing), missing))


def test_the_publisher_names_every_insights_artefact_a_published_figure_is_built_from():
    """THE DEFECT: an insights output is written every cycle and left out of the commit list.

    The lower bound is derived from two OTHER modules, never from the helper under test: a path
    is in scope when `tools.generate_insights` declares it as an output AND
    `tools.generate_dashboard_data` declares it as an input. That intersection is the membership
    test in one sentence -- *this cycle rewrites it and a published figure reads it* -- and it
    moves on its own when either module gains or renames a path."""
    import tools.generate_dashboard_data as reader
    import tools.generate_insights as writer

    observability = (PROJECT / "docs" / "observability").resolve()

    def _declared(module):
        return {
            value.resolve()
            for name, value in vars(module).items()
            if not name.startswith("_")
            and isinstance(value, Path)
            and observability in value.resolve().parents
        }

    must_be_committed = _declared(writer) & _declared(reader)
    assert must_be_committed, (
        "Neither module declares a shared docs/observability path any more. The control has lost "
        "its subject rather than passed -- find where the insights artefacts moved to.")

    named_by_publisher = {p.resolve() for p in prc.insights_artefact_paths()}
    orphaned = must_be_committed - named_by_publisher
    assert not orphaned, (
        "{} is rewritten by tools/generate_insights.py on every publish cycle and read by "
        "tools/generate_dashboard_data.py to build a published figure, and "
        "process_run_complete.insights_artefact_paths() does not name it. Its committed copy "
        "will freeze while the artefact built from it is committed fresh.".format(
            sorted(str(p.relative_to(PROJECT)) for p in orphaned)))


def test_the_publish_commit_actually_reaches_that_list():
    """THE DEFECT: the helper is correct, complete, and called by nobody.

    The two legs above both pass on a publisher that never appends the paths to its pathspec --
    the 'a cited constant has a caller' shape, here on the one function whose path list IS the
    commit."""
    source = inspect.getsource(prc.git_commit_push)
    assert "_publish_insights_artefacts(files)" in source, (
        "git_commit_push no longer appends the insights artefacts to its path list, so "
        "run_history.json and run_insights.json are back to being regenerated every cycle and "
        "committed by none. If the call moved, move this assertion to where it went -- do not "
        "delete it.")
