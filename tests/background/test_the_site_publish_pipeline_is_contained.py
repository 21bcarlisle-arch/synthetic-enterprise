"""A test process may not run the live site publish pipeline.

The control under test is `background/live_ledger_guard.py::guard_site_publish_pipeline`,
built for the 2026-09-09 LATENT finding `SEAT_FINDING_A_TEST_REWROTE_TWENTY_SIX_LIVE_
FEEDS_INTO_A_DEGRADED_PUBLISH_STATE_AND_THE_ONLY_THING_THAT_NOTICED_BLAMED_THE_WRITER`.

IT IS BACK BESIDE ITS TWIN, AND THE ROUND TRIP IS THE POINT. For one commit this guard
lived in `process_run_complete.py` instead, because `test_live_ledger_guard.py::test_the_
narrowing_to_measurement_ledgers_is_measured_not_assumed` was **RED AT HEAD** (86
unguarded observability writers against a bound of 74) for reasons that had nothing to do
with it, and the commit gate selects any test that NAMES a staged path -- so touching
`live_ledger_guard.py` would have refused that landing on two-week-old drift belonging to
nobody. **The bound was not raised to 86.** The writers were guarded instead: 30 of them
across 17 modules, taking the census 86 -> 56, below the 74 it was frozen at on
2026-08-26 -- both figures measured in a clean HEAD extract at 8c53c35e5 carrying this
lane's hunks and nothing else, NOT in the shared working tree, which reads 87 -> 57
because it holds four other lanes' uncommitted modules. Then the guard came home. A
ratchet that has silently stopped ratcheting does
not merely fail to catch things -- it pushes unrelated code out of its proper module, and
that is the cost this note exists to record.

THE POISON ROUND RAN FIRST, AND IT IS WHY THESE TESTS MEAN ANYTHING (R15 -- "survived"
means two opposite things, so reachability is proved before any mutation is scored). On
2026-09-09, at commit `b9ff0425b` with the guard ABSENT, `tests/tools/
test_website_integrity_fix.py::test_generate_dashboard_json_returns_gate_status` was run
alone against a tree measured clean of these paths (`git status --porcelain -- site/
docs/state/` -> 0 lines). It PASSED, in 143.62s, and left 27 paths dirty: 26 tracked
feeds plus one NEW untracked feed, with `site/data/publish_steps.json` flipped to
degraded / run_stamp "unknown" / 6 failing steps. The unguarded path is therefore
reachable and was being taken. These tests are not born green.

R15: every test below is paired with the source mutation it fires on, named in its own
docstring. A control that cannot fail is worse than none.
"""

from __future__ import annotations

import ast
import inspect
import textwrap
from pathlib import Path

import pytest

from background import live_ledger_guard as guard
from background import process_run_complete as prc
from background.live_ledger_guard import (
    PUBLISHED_FEED_DIRS,
    SitePublishUnderTest,
    guard_site_publish_pipeline,
)

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
BACKGROUND_DIR = PROJECT_DIR / "background"


def test_the_site_publish_pipeline_is_refused_under_a_test_process():
    """The refusal fires, and this test process IS the subject -- no fixture, no
    monkeypatch, no simulated condition. If it does not raise here it will not raise
    for the test that was actually publishing.

    MUTATION: drop the `raise` -- this reds."""
    with pytest.raises(SitePublishUnderTest):
        guard_site_publish_pipeline(entry_point="probe")


def test_outside_a_test_process_the_site_publish_is_permitted(monkeypatch):
    """THE CONTROL MUST BE ABLE TO SAY YES. A guard that refuses everything passes
    every refusal test AND silently stops the real publish daemon -- the site would
    freeze and the suite would stay green.

    PATCHED ON `live_ledger_guard`, NOT ON `process_run_complete`, and that is not
    cosmetic: the guard resolves `in_test_process` from the module it is DEFINED in.
    While it was exiled this line read `prc` and worked; after the move the same line
    patches a name nothing reads, the refusal fires anyway and the test goes RED -- loudly
    wrong rather than vacuously green, which is the only reason the move was safe to make.

    MUTATION: drop the `if not in_test_process(): return` early exit -- this reds, and
    so does every real publish cycle."""
    monkeypatch.setattr(guard, "in_test_process", lambda: False)
    assert guard.guard_site_publish_pipeline(entry_point="probe") is None


def test_the_site_publish_refusal_names_what_to_do_instead():
    """A refusal that names its reason is how you find out the refusal was wrong.
    Whoever hits this is reading a traceback from a test they did not write, so it must
    say what to change and where the bytes would have gone.

    MUTATION: replace the message with a bare class name -- this reds."""
    with pytest.raises(SitePublishUnderTest) as exc:
        guard_site_publish_pipeline(entry_point="generate_dashboard_json")
    msg = str(exc.value)
    assert "generate_dashboard_json" in msg, "does not name the entry point refused"
    assert "Mock this entry point" in msg, "does not name the remedy"
    assert "site/data" in msg, "does not name where the bytes would have gone"


def test_there_is_no_env_var_override_on_the_site_publish_guard():
    """An escape hatch is a FAIL-OPEN door that the offending process is exactly the
    one able to set -- the same argument as for the ledger guard.

    MUTATION: add `if os.environ.get("ALLOW_SITE_PUBLISH"): return` -- this reds by
    reading the guard's own source for an environment read."""
    src = (BACKGROUND_DIR / "live_ledger_guard.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "guard_site_publish_pipeline")
    reads_env = [n for n in ast.walk(fn)
                 if isinstance(n, ast.Attribute) and n.attr in {"environ", "getenv"}]
    assert reads_env == [], "guard_site_publish_pipeline reads the environment"


def test_the_published_feed_dirs_are_the_ones_that_were_actually_polluted():
    """The subject is DERIVED containment, not a hand-list of feeds -- a feed added
    tomorrow is covered on the day it is created. But the three directories themselves
    are the definition, so they must be right: the paths the poison round dirtied have
    to fall inside them.

    MUTATION: drop `docs/state` from PUBLISHED_FEED_DIRS -- this reds on
    `docs/state/sim_data.json`, which the poison round did dirty."""
    observed = [
        "site/data/publish_steps.json",     # the publish-state ledger itself
        "site/state/PROJECT_STATE.txt",     # not JSON, and still a published feed
        "docs/state/sim_data.json",         # the one outside site/
    ]
    for rel in observed:
        p = (PROJECT_DIR / rel).resolve()
        assert any(
            p.is_relative_to(d.resolve()) for d in PUBLISHED_FEED_DIRS
        ), f"{rel} was polluted by the poison round but is outside PUBLISHED_FEED_DIRS"


# ===========================================================================
# WIRED INTO PRODUCTION. Calling the guard directly says nothing about whether
# the pipeline calls it (R15: a control that calls the estimator directly is
# blind to whether production wires it).
# ===========================================================================

def test_the_publish_pipeline_actually_calls_the_guard_first():
    """POSITION IS THE PROPERTY, not merely presence. The coverage gate on the next
    line writes too, so a guard placed after it still leaks. This asserts the call is
    the FIRST statement of the function body after its docstring.

    MUTATION: move the call below `_cohort_coverage_gate_permits_publish()`, or delete
    it -- both red."""
    fn = ast.parse(textwrap.dedent(inspect.getsource(prc.generate_dashboard_json))).body[0]
    body = [n for n in fn.body if not (isinstance(n, ast.Expr)
                                       and isinstance(n.value, ast.Constant)
                                       and isinstance(n.value.value, str))]
    first = body[0]
    assert isinstance(first, ast.Expr) and isinstance(first.value, ast.Call), (
        f"the first statement of generate_dashboard_json is not a call: {ast.dump(first)}")
    assert getattr(first.value.func, "id", None) == "guard_site_publish_pipeline", (
        "generate_dashboard_json does not call guard_site_publish_pipeline first; "
        f"it starts with {ast.dump(first.value.func)}")


def test_the_site_publish_guard_is_imported_at_top_level_with_no_try():
    """FAIL-SILENT. MUTATION: wrap the import in `try: ... except ImportError:
    guard_site_publish_pipeline = lambda **k: None`. That is an unavailable check
    reading as a passed one; this reds."""
    tree = ast.parse((BACKGROUND_DIR / "process_run_complete.py").read_text(encoding="utf-8"))
    top_level = {n.module for n in tree.body if isinstance(n, ast.ImportFrom)}
    assert "background.live_ledger_guard" in top_level, (
        "process_run_complete does not import the guard at module top level")
