"""Tests for background/process_run_complete.py."""

import contextlib
import functools
import importlib
import inspect
import json
import os
import re
import subprocess
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import background.process_run_complete as prc
from tests.background.publish_gate_root_shape import materialise_repo_shaped_root

# Files the publish pipeline writes through modules OTHER than prc, each resolving its own
# output path from its own __file__ or cwd -- so re-rooting prc.PROJECT_DIR does not reach
# them. (module, attribute, repo-relative path it must currently point at.)
_PIPELINE_OUTPUT_PATHS = (
    ("background.agent_status", "STATUS_FILE", "docs/observability/agent_status.json"),
    ("background.agent_status", "SITE_STATUS_FILE", "site/data/agent_status.json"),
)

# The two market-feed publishers take their destination as a DEFAULT ARGUMENT, which Python
# bound to the real path at def-time -- so redirecting the module constant they were defaulted
# from changes nothing, and both feeds kept being rewritten for real. Rebind the argument
# itself. (module, function, output keyword, repo-relative path it must currently default to.)
_PIPELINE_OUTPUT_WRITERS = (
    ("simulation.publish_market_feed", "publish", "output_path",
     "docs/market_data/price_feed.json"),
    ("simulation.publish_consumption_data", "publish_consumption", "output_path",
     "docs/market_data/consumption_feed.json"),
)

# THE SAME LEAK ONE PUBLISH STAGE FURTHER OUT (2026-09-04). Four more collaborators take their
# destination as an OPTIONAL keyword that DEFAULTS TO None and fall back to a module constant
# (`dest = OUT_PATH if out_path is None else out_path`). Neither registry above reaches that
# shape: there is no attribute prc owns to re-root, and the def-time default is `None`, not a
# path -- so the assertion in _PIPELINE_OUTPUT_WRITERS would not even have fired. The five tests
# here that drive main()/_process() end to end were therefore rewriting four TRACKED files in the
# real tree on every run, and `grid_intensity_feed.json` LOST 2027 of its 2314 lines each time,
# because the regeneration runs against whatever the test environment can reach rather than the
# record the committed file holds. A shorter feed is not an obviously-broken feed; it is a
# plausible one, and the publish daemon commits generated site output it finds in the tree.
# (module, function, output keyword, module constant holding the real destination, repo-relative)
_PIPELINE_OUTPUT_FALLBACK_WRITERS = (
    ("tools.generate_grid_intensity_feed", "generate", "out_path", "OUT_PATH",
     "docs/market_data/grid_intensity_feed.json"),
    ("tools.couple_value_based_pricing", "generate", "out_path", "OUT_PATH",
     "docs/observability/value_based_pricing_arms.json"),
    ("tools.generate_explore_carbon", "generate", "out_path", "OUT_PATH",
     "site/data/explore_carbon.json"),
    ("tools.fetch_weather_data", "generate_weather_data", "output_path", "WEATHER_JSON",
     "site/data/weather.json"),
)

# Every module the publish block imports, and what makes it safe to run here. This set is
# compared against the LIVE source of _process()/_run_weather_data() by the control below, so
# wiring a new collaborator into the publish block reds this file until someone says which of
# the two it is -- which is the only moment isolating it is cheap. It is a signature of the
# publish block, not a rulebook: the reasons are read by the next person, the equality is what
# has teeth.
_PUBLISH_BLOCK_COLLABORATORS = {
    "background": "staging_archive_policy -- read-only classification",
    "background.agent_status": "isolated by _PIPELINE_OUTPUT_PATHS",
    "background.notify": "writes only its own transitions file, under a re-rooted PROJECT_DIR",
    "background.tree_lock": "neutralised directory-wide by _isolate_project_dir",
    "simulation.publish_consumption_data": "isolated by _PIPELINE_OUTPUT_WRITERS",
    "simulation.publish_market_feed": "isolated by _PIPELINE_OUTPUT_WRITERS",
    "tools": "merge_atom_status -- folds an inbox that does not exist in the sandbox",
    "tools.couple_value_based_pricing": "isolated by _PIPELINE_OUTPUT_FALLBACK_WRITERS",
    "tools.fetch_weather_data": "isolated by _PIPELINE_OUTPUT_FALLBACK_WRITERS",
    "tools.generate_explore_carbon": "isolated by _PIPELINE_OUTPUT_FALLBACK_WRITERS",
    "tools.generate_grid_intensity_feed": "isolated by _PIPELINE_OUTPUT_FALLBACK_WRITERS",
    "tools.generate_insights": "written through RUN_INSIGHTS_PATH/RUN_HISTORY_PATH, which prc "
                               "owns and _isolate_project_dir re-roots",
    "tools.revenue_sanity_check": "reads the run payload; writes nothing",
}


def _imported_modules(source):
    """The module names a block of source imports. Kept a plain function so the control over it
    can be handed a source string it built itself -- see the reachability leg below."""
    return set(re.findall(r"^\s*from ([\w.]+) import", source, re.M))


# A STUB THAT MODELS ONLY THE RETURN CODE IS LYING ABOUT THE REST (2026-08-09, R10 class
# closure; the ~4.5h publish wedge, 41 consecutive gate failures).
#
# Every `subprocess.run` stub in this file was a bare `MagicMock()` with `returncode` set and
# nothing else, so `.stdout` came back a MagicMock. That is not what `subprocess.run(...,
# text=True)` returns. It cost nothing for as long as no production line READ a stdout these
# stubs had not already special-cased -- and then `_head_checkout` started writing the output
# of `git rev-parse HEAD` into the checkout's `.git/HEAD`, and three tests died with
#
#     TypeError: data must be str, not MagicMock
#
# which says nothing whatsoever about the code under test. The gate is `-x`, so that wedged
# publishing for every caller.
#
# R10 forbids closing that at the instance. The population is open-ended: ANY future line that
# reads a stdout no stub anticipated is the next instance, and the failure will again look like
# a product bug rather than a fixture lying about a type. So the SUBJECT is fixed -- one shared
# factory that honours the contract (`str` under text mode, `bytes` otherwise), with
# `git rev-parse` answering in the shape of a real SHA. Per-command outputs a test actually
# cares about are still set by that test, on top of this.
#
# Guarded by test_every_subprocess_stub_here_models_the_return_contract below, so a bare
# `MagicMock()` stub reintroduced here fails immediately instead of years later, in the gate.
_FAKE_HEAD_SHA = "0123456789abcdef0123456789abcdef01234567"


def fake_completed(cmd, returncode=0, **kwargs):
    """A type-correct stand-in for a `subprocess.run` result. See the note above.

    `git ls-remote` ANSWERS WITH THE SAME SHA (2026-08-19). It used to answer with the empty
    string, which `_push_reached_origin` reads -- correctly, fail-closed -- as "origin did not
    advance". So the default fixture in this file modelled a publish whose push never landed,
    and `test_main_success_flow` was asserting the happy-path return code of a cycle that had
    NOT published. That was invisible while every failing publish outcome still exited 0
    (EXIT_PUBLISH_DID_NOT_LAND names the incident); the moment the exit code started carrying
    the outcome, the fixture's own claim became visible and false. The two tests that are about
    a push NOT reaching origin set `ls-remote` explicitly on top of this, as they always did.

    `git merge-base --is-ancestor` ANSWERS ONLY WHAT A STUB HONESTLY CAN (2026-09-16). The push
    verdict now asks REACHABILITY rather than equality (`_push_reached_origin`), so this fixture
    acquired a new subject -- and the blanket rc=0 fall-through answered "yes, reachable" to every
    question, which turned the phantom-push control green with the phantom still in it. That is
    the fake-more-permissive-than-its-subject shape, one paragraph below the fixture defect this
    docstring already records. There is no commit graph here, so the only ancestry a stub can
    honestly claim is identity: same sha -> reachable, anything else -> not. A test that needs a
    real ancestry answer builds a real repository -- see
    test_the_publish_verdict_asks_reachability_and_not_equality.py.
    """
    text = bool(kwargs.get("text") or kwargs.get("universal_newlines") or kwargs.get("encoding"))
    head = list(cmd[:2])
    out = _FAKE_HEAD_SHA + "\n" if head == ["git", "rev-parse"] else ""
    if head == ["git", "ls-remote"]:
        out = "{}\trefs/heads/main\n".format(_FAKE_HEAD_SHA)
    if list(cmd[:3]) == ["git", "merge-base", "--is-ancestor"]:
        returncode = 0 if len(cmd) > 4 and cmd[3] == cmd[4] else 1
    m = MagicMock()
    m.returncode = returncode
    m.stdout = out if text else out.encode()
    m.stderr = "" if text else b""
    return m


@pytest.fixture(autouse=True)
def _origin_is_level(monkeypatch):
    """Hold the divergence read at "level with origin" for this file.

    `git_commit_push` reads origin BEFORE it stages anything (2026-09-01: the publish loop's own
    retry was widening the fork it was blocked by — see `_divergence_refusal`), and the sandbox
    `PROJECT_DIR` these tests run in is not a git repository at all, so the read would answer
    UNREADABLE and every test below would measure the refusal instead of its own subject.

    STATED, NOT NEUTERED. This is the assumption these tests already made silently when the
    question did not exist, and it is now written down. The guard itself is proven against real
    git in `test_a_behind_origin_publish_refuses_instead_of_deepening_the_fork.py`, which does
    NOT use this fixture — so setting it here cannot make that control green.
    """
    monkeypatch.setattr(prc, "_commits_origin_is_ahead_by", lambda: 0)


@pytest.fixture(autouse=True)
def _the_landing_lands(monkeypatch):
    """Hold the publish COMMIT at "landed" for this file, for the same reason as the fixture above.

    The publish commit became a `surgical_land` landing on 2026-09-08 -- it builds
    HEAD-plus-its-pathspec and gates that tree in a clean extract, precisely so that another
    lane's uncommitted work can no longer refuse it. The sandbox `PROJECT_DIR` these tests run in
    is not a git repository, so the real tool would refuse every one of them and each test below
    would measure that refusal instead of its own subject -- exactly what `_origin_is_level`
    exists to prevent one step earlier.

    STATED, NOT NEUTERED. The tests in this file that are ABOUT the landing's outcomes override
    this in their own body (which runs after the fixture and therefore wins), and the classifier
    is driven against the real tool, in a real repository, by
    `test_the_publisher_classifies_the_tools_real_refusals.py` -- which does NOT use this
    fixture, so pinning it here cannot make that control green.
    """
    monkeypatch.setattr(
        prc, "_land_publish_commit",
        lambda pathspec, msg, git_hash: {"sha": "0" * 40, "refusal": "", "lost": []})


@pytest.fixture(autouse=True)
def _isolate_project_dir(tmp_path_factory, monkeypatch):
    """Point PROJECT_DIR -- and EVERY module path derived from it -- at a throwaway tree,
    for every test in this file. Zero real-tree WRITES (real-tree reads of static input
    data are left alone: see the collaborator note at the bottom of this fixture).

    THE INCIDENT (issue #11, "the ghost pusher"). Six tests below ran against the REAL
    PROJECT_DIR with the REAL `subprocess.run`: the four change-detection gate tests, which
    call `prc._process()` directly, and the two frozen-baseline trigger tests. Two of the
    four -- the pair whose marker fingerprint MATCHES, so the gate takes its SKIP branch --
    reach `_refresh_published_liveness_on_skip`, which is `git add` + `git commit` + `git
    push origin HEAD:main`. Running THIS FILE therefore manufactured a real
    `chore(liveness): ... (git=abc)` commit on whatever branch was checked out and pushed
    it; it failed to land only where credentials were absent. The sibling tests were fine
    -- `_full_isolation_setup` and `TestRefreshPublishedLivenessOnSkip._wire` both wire
    PROJECT_DIR correctly -- which is precisely why the leak survived: the file LOOKED
    isolated.

    WHY A DIRECTORY-WIDE RE-ROOT AND NOT FOUR MONKEYPATCHES. Per-test wiring is what
    failed. It is opt-in, it is invisible when omitted, and prc has FIFTEEN module-level
    paths under the repo root -- a test that remembers PROJECT_DIR and forgets LAST_PUSH_FILE
    is still touching the real tree. This walks prc's namespace and re-roots every Path
    living under the real repo into a per-test sandbox, mirroring the real layout. A path
    constant added to prc tomorrow is isolated the day it lands, with nothing to remember
    (R10: close the class, not the instance).

    Tests needing specific contents still monkeypatch their own paths in the test BODY,
    which runs after this fixture and therefore wins.
    """
    real_root = Path(prc.__file__).resolve().parent.parent
    sandbox = tmp_path_factory.mktemp("prc_tree")
    for name, value in list(vars(prc).items()):
        if not isinstance(value, Path):
            continue
        try:
            relative = value.resolve().relative_to(real_root)
        except ValueError:
            continue  # already outside the repo -- not ours to re-root
        target = sandbox / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(prc, name, target)
    assert prc.PROJECT_DIR == sandbox, "PROJECT_DIR itself must be re-rooted, not just its children"
    # tree_lock resolves its own LOCK_FILE from ITS OWN __file__, so re-rooting prc's paths
    # does not move it -- an unwired test would still flock the real docs/observability/.tree.lock
    # and serialise itself against the live publisher. No test in this file asserts locking
    # behaviour (two already stub it in their own body), so neutralise it directory-wide.
    monkeypatch.setattr(prc, "tree_lock", lambda *a, **k: contextlib.nullcontext())
    # The pipeline also writes through COLLABORATORS that resolve their own output paths from
    # their own __file__/cwd, so prc.PROJECT_DIR does not reach them: driving main() end-to-end
    # (test_main_success_flow and the force-republish trio) rewrote four real files on every
    # run -- the live agent-status door and the two published market feeds. Redirect the
    # OUTPUTS only; their inputs (the SSP cache, the NBP CSV, the HH data dir) stay real,
    # because reads are harmless and stubbing them would quietly turn the publish steps into
    # no-ops rather than isolating them.
    for module_name, attribute, relative in _PIPELINE_OUTPUT_PATHS:
        module = importlib.import_module(module_name)
        current = getattr(module, attribute)  # AttributeError here = renamed away, isolation lost
        assert str(current).endswith(relative), (
            "{}.{} now points at {!r}, not {!r} -- this fixture is no longer isolating it".format(
                module_name, attribute, str(current), relative)
        )
        target = sandbox / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(module, attribute, target)
    for module_name, function_name, keyword, relative in _PIPELINE_OUTPUT_WRITERS:
        module = importlib.import_module(module_name)
        original = getattr(module, function_name)
        default = inspect.signature(original).parameters[keyword].default
        assert str(default).endswith(relative), (
            "{}.{}({}=) now defaults to {!r}, not {!r} -- this fixture is no longer "
            "isolating it".format(module_name, function_name, keyword, str(default), relative)
        )
        target = sandbox / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(module, function_name,
                            functools.partial(original, **{keyword: target}))
    for module_name, function_name, keyword, constant, relative in _PIPELINE_OUTPUT_FALLBACK_WRITERS:
        module = importlib.import_module(module_name)
        original = getattr(module, function_name)
        default = inspect.signature(original).parameters[keyword].default
        assert default is None, (
            "{}.{}({}=) now defaults to {!r}, not None -- it no longer falls back to {}, so this "
            "fixture is redirecting the wrong thing".format(
                module_name, function_name, keyword, default, constant)
        )
        current = getattr(module, constant)  # AttributeError here = renamed away, isolation lost
        assert str(current).endswith(relative), (
            "{}.{} now points at {!r}, not {!r} -- this fixture is no longer isolating it".format(
                module_name, constant, str(current), relative)
        )
        target = sandbox / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(module, function_name,
                            functools.partial(original, **{keyword: target}))


@pytest.fixture(autouse=True)
def _isolate_fingerprint_file(tmp_path_factory, monkeypatch):
    """Redirect the change-detection fingerprint file to a per-test temp path so
    no test reads or pollutes the real docs/observability/ file (same isolation
    discipline as .last_tested_hash). Tests that want the gate to fire write to
    prc.LAST_FINGERPRINT_FILE explicitly."""
    fp = tmp_path_factory.mktemp("fp") / ".last_processed_fingerprint.json"
    monkeypatch.setattr(prc, "LAST_FINGERPRINT_FILE", fp)


@pytest.fixture(autouse=True)
def _isolate_log_file(tmp_path_factory, monkeypatch):
    """Redirect prc.LOG_FILE to a per-test temp path for every test in this
    file -- made autouse (2026-07-11) after two tests (test_gate_skips_
    identical_run, test_gate_never_skips_admin_event) were found live to have
    called prc._process() without their own explicit monkeypatch, each
    writing real 'Processing run_complete_X.md'/'run_complete_Y.md' log lines
    straight into the production docs/observability/sim-runner-log.md during
    a real fast-test-suite gate run -- confirmed via direct grep, the exact
    literal marker names only exist in this test file. Same test-isolation-
    leak class as the tmux-scrollback retro. A per-test explicit
    monkeypatch.setattr(prc, "LOG_FILE", ...) elsewhere in this file is now
    redundant but harmless."""
    log_path = tmp_path_factory.mktemp("log") / "log.md"
    monkeypatch.setattr(prc, "LOG_FILE", log_path)


def make_marker(tmp_path, git_hash="abc1234", elapsed_s=1870.0, json_data=None):
    """Write a realistic run_complete marker and its JSON to tmp_path."""
    if json_data is None:
        json_data = {
            "total_net_gbp": -8317.21,
            "total_gross_gbp": -7089.58,
            "total_capital_gbp": 1228.0,
            "starting_treasury_gbp": 29846.0,
            "final_treasury_gbp": 11131.0,
            "committee_wake_ups_total": 323,
            "bills_total": 1117,
            "enterprise_value_gbp": -20661.90,
            "net_margin_after_cost_to_serve_gbp": -23569.0,
            "retention_log": [
                {"outcome": "retained"},
                {"outcome": "retained"},
            ],
            "no_offer_churn_log": [{"reason": "below_threshold"}] * 3,
            "churned_billing_accounts": ["C1", "C2", "C3"],
            "administration_event": None,
        }

    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    ts = "20260621T104002Z"
    json_path = reports_dir / f"run_output_{git_hash}_{ts}.json"
    json_path.write_text(json.dumps(json_data))

    marker_text = (
        f"Simulation Run Complete\n\n"
        f"Git: {git_hash}\n"
        f"JSON: {json_path}\n"
        f"Duration: {elapsed_s:.0f}s | Size: 263 KB\n"
    )
    marker = tmp_path / "staging" / f"run_complete_{ts}.md"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(marker_text)
    return marker, json_data


def test_parse_marker_extracts_git_hash_elapsed_json_path(tmp_path):
    marker, _ = make_marker(tmp_path, git_hash="def5678", elapsed_s=2100.0)
    fields = prc.parse_marker(marker)
    assert fields["git_hash"] == "def5678"
    assert fields["elapsed_s"] == 2100.0
    assert "run_output_def5678" in str(fields["json_path"])


def test_update_latest_md_replaces_block(tmp_path, monkeypatch):
    latest = tmp_path / "LATEST.md"
    latest.write_text(
        "Last updated: 2026-01-01T00:00:00Z\n\n"
        "**Latest simulation results (2016-2025)** - auto-processed (0s / 0 min):\n"
        "- Net margin: old data\n"
        "\n"
        "**Some other section** here\n"
    )
    monkeypatch.setattr(prc, "LATEST_MD", latest)

    json_data = {
        "total_net_gbp": -8317.21,
        "total_gross_gbp": -7089.58,
        "total_capital_gbp": 1228.0,
        "starting_treasury_gbp": 29846.0,
        "final_treasury_gbp": 11131.0,
        "committee_wake_ups_total": 323,
        "bills_total": 1117,
        "enterprise_value_gbp": -20661.90,
        "net_margin_after_cost_to_serve_gbp": -23569.0,
        "retention_log": [{"outcome": "retained"}, {"outcome": "retained"}],
        "no_offer_churn_log": [{}] * 3,
        "churned_billing_accounts": ["C1", "C2"],
    }
    prc.update_latest_md(json_data, elapsed_s=1870.0)

    text = latest.read_text()
    assert "£-8,317.21" in text
    assert "323 committee interventions" in text
    assert "**Some other section**" in text


def test_main_success_flow(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(prc, "DONE_DIR", tmp_path / "staging" / "done")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(prc, "RUN_LOCK_FILE", tmp_path / ".process_run_complete.lock")
    # generate_dashboard_json writes to the REAL site/data/dashboard.json (hardcoded path
    # inside generate_dashboard_data.py) — mock it to avoid corrupting the live dashboard
    # Returns True (gate passed) -- generate_dashboard_json's return value now
    # drives an immediate NTFY on consistency-gate failure (Phase QF); this
    # mock represents the happy path, not a gate failure.
    monkeypatch.setattr(prc, "generate_dashboard_json", lambda p, git_hash="unknown": True)
    # run_fast_tests writes to the REAL docs/observability/.last_tested_hash on a
    # returncode==0 fake pytest run — mock it to avoid corrupting the live cache file
    monkeypatch.setattr(prc, "LAST_TESTED_HASH_FILE", tmp_path / ".last_tested_hash")
    # generate_insights writes to the REAL docs/observability/run_insights.json and
    # run_history.json (hardcoded defaults) -- redirect to avoid corrupting the live
    # exec-summary data with this test's fake abc1234/-8317.21 fixture.
    monkeypatch.setattr(prc, "RUN_INSIGHTS_PATH", tmp_path / "run_insights.json")
    monkeypatch.setattr(prc, "RUN_HISTORY_PATH", tmp_path / "run_history.json")

    latest_md = tmp_path / "LATEST.md"
    latest_md.write_text(
        "Last updated: 2026-01-01T00:00:00Z\n\n"
        "**Latest simulation results (2016-2025)** - auto-processed (0s / 0 min):\n"
        "- Net margin: old\n"
        "\n"
        "**Next section**\n"
    )
    monkeypatch.setattr(prc, "LATEST_MD", latest_md)

    marker, json_data = make_marker(tmp_path)

    def fake_run(cmd, **kwargs):
        return fake_completed(cmd, **kwargs)

    monkeypatch.setattr(prc.subprocess, "run", fake_run)
    _stub_head_checkout(monkeypatch, tmp_path)

    rc = prc.main(str(marker))
    assert rc == 0
    assert not marker.exists()
    assert (tmp_path / "staging" / "done" / marker.name).exists()


def _stub_head_checkout(monkeypatch, tmp_path, name="head-stub"):
    """Yield a MATERIALISED stand-in for `prc._head_checkout()`.

    These tests stub `prc.subprocess.run` wholesale, so the real `_head_checkout` mkdir's a
    directory and then `git archive`/`tar` never populate it -- which is precisely the broken
    state the 2026-08-12 wedge produced for real (`git init` -> `fatal: cannot mkdir`, empty
    directory, gate runs the full suite against a tree holding none of the repo, 28 cycles).
    `_run_gate_in` now refuses that root, so these tests must supply a checkout that looks
    EXTRACTED or they test the refusal instead of their own subject.

    The SHAPE it must have is not restated here (2026-08-12, R10 class closure after the same
    hand-typed shape wedged publishing twice): `publish_gate_root_shape` owns it, so a change
    to `PUBLISH_PATH_SOURCES` or `ROOT_REPO_MARKER` reaches this stub too."""
    checkout = materialise_repo_shaped_root(tmp_path / name)

    @contextlib.contextmanager
    def _fake_checkout():
        yield checkout

    monkeypatch.setattr(prc, "_head_checkout", _fake_checkout)
    return checkout


def _full_isolation_setup(tmp_path, monkeypatch):
    """Same isolation as test_main_success_flow, factored out for the
    force-republish tests below."""
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(prc, "DONE_DIR", tmp_path / "staging" / "done")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(prc, "RUN_LOCK_FILE", tmp_path / ".process_run_complete.lock")
    monkeypatch.setattr(prc, "generate_dashboard_json", lambda p, git_hash="unknown": True)
    monkeypatch.setattr(prc, "LAST_TESTED_HASH_FILE", tmp_path / ".last_tested_hash")
    monkeypatch.setattr(prc, "RUN_INSIGHTS_PATH", tmp_path / "run_insights.json")
    monkeypatch.setattr(prc, "RUN_HISTORY_PATH", tmp_path / "run_history.json")
    monkeypatch.setattr(prc, "FORCE_REPUBLISH_FLAG", tmp_path / ".force_republish_once")
    latest_md = tmp_path / "LATEST.md"
    latest_md.write_text(
        "Last updated: 2026-01-01T00:00:00Z\n\n"
        "**Latest simulation results (2016-2025)** - auto-processed (0s / 0 min):\n"
        "- Net margin: old\n"
        "\n"
        "**Next section**\n"
    )
    monkeypatch.setattr(prc, "LATEST_MD", latest_md)

    def fake_run(cmd, **kwargs):
        return fake_completed(cmd, **kwargs)
    monkeypatch.setattr(prc.subprocess, "run", fake_run)
    _stub_head_checkout(monkeypatch, tmp_path)


# --- FORCE_REPUBLISH_FLAG -- no-orphan-transitions fix (2026-07-10,
# CLAIM_EQUALS_PIXEL.md/END_TO_END_VERIFICATION.md): a hold release must
# force a real republish, even when the fixed code's headline figures
# happen to fingerprint-match the last processed run ---

def test_change_detection_gate_skips_identical_run_when_not_forced(tmp_path, monkeypatch):
    _full_isolation_setup(tmp_path, monkeypatch)
    marker, json_data = make_marker(tmp_path)
    prc.LAST_FINGERPRINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    fp = prc._run_fingerprint(json_data)
    fp["source_git_hash"] = "abc1234"  # matches make_marker()'s default git_hash -- genuinely nothing changed
    prc.LAST_FINGERPRINT_FILE.write_text(json.dumps(fp, sort_keys=True))

    rc = prc.main(str(marker))

    assert rc == 0
    assert (tmp_path / "staging" / "done" / marker.name).exists()
    assert not prc.LATEST_MD.read_text().count("Net margin: \xa3")  # LATEST.md never touched


def test_force_republish_flag_bypasses_identical_fingerprint(tmp_path, monkeypatch):
    """The exact regression: an identical-looking fingerprint must not skip
    processing when a hold was just released."""
    _full_isolation_setup(tmp_path, monkeypatch)
    marker, json_data = make_marker(tmp_path)
    prc.LAST_FINGERPRINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    prc.LAST_FINGERPRINT_FILE.write_text(json.dumps(prc._run_fingerprint(json_data), sort_keys=True))
    prc.FORCE_REPUBLISH_FLAG.parent.mkdir(parents=True, exist_ok=True)
    prc.FORCE_REPUBLISH_FLAG.touch()

    rc = prc.main(str(marker))

    assert rc == 0
    assert "Net margin: \xa3" in prc.LATEST_MD.read_text()  # LATEST.md WAS regenerated


def test_force_republish_flag_consumed_exactly_once(tmp_path, monkeypatch):
    _full_isolation_setup(tmp_path, monkeypatch)
    marker, json_data = make_marker(tmp_path)
    prc.FORCE_REPUBLISH_FLAG.parent.mkdir(parents=True, exist_ok=True)
    prc.FORCE_REPUBLISH_FLAG.touch()

    prc.main(str(marker))

    assert not prc.FORCE_REPUBLISH_FLAG.exists()


def test_main_returns_1_for_missing_marker(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(prc, "RUN_LOCK_FILE", tmp_path / ".process_run_complete.lock")
    rc = prc.main(str(tmp_path / "nonexistent.md"))
    assert rc == 1


def test_main_returns_1_when_tests_fail(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(prc, "DONE_DIR", tmp_path / "staging" / "done")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(prc, "RUN_LOCK_FILE", tmp_path / ".process_run_complete.lock")
    # Returns True (gate passed) -- generate_dashboard_json's return value now
    # drives an immediate NTFY on consistency-gate failure (Phase QF); this
    # mock represents the happy path, not a gate failure.
    monkeypatch.setattr(prc, "generate_dashboard_json", lambda p, git_hash="unknown": True)
    monkeypatch.setattr(prc, "RUN_INSIGHTS_PATH", tmp_path / "run_insights.json")
    monkeypatch.setattr(prc, "RUN_HISTORY_PATH", tmp_path / "run_history.json")

    latest_md = tmp_path / "LATEST.md"
    latest_md.write_text(
        "Last updated: 2026-01-01T00:00:00Z\n\n"
        "**Latest simulation results (2016-2025)** - auto-processed (0s / 0 min):\n"
        "- Net margin: old\n"
        "\n"
    )
    monkeypatch.setattr(prc, "LATEST_MD", latest_md)

    marker, _ = make_marker(tmp_path)

    call_count = [0]

    def fake_run(cmd, **kwargs):
        call_count[0] += 1
        failed = "pytest" in " ".join(str(a) for a in cmd)
        return fake_completed(cmd, returncode=1 if failed else 0, **kwargs)

    monkeypatch.setattr(prc.subprocess, "run", fake_run)

    rc = prc.main(str(marker))
    assert rc == 1
    assert marker.exists()


from background.process_run_complete import _fmt_gbp


def test_fmt_gbp_positive():
    assert _fmt_gbp(1000) == "£+1,000"


def test_fmt_gbp_negative():
    assert _fmt_gbp(-500) == "£-500"


def test_fmt_gbp_zero():
    assert _fmt_gbp(0) == "£+0"


def test_fmt_gbp_large():
    assert _fmt_gbp(1_234_567) == "£+1,234,567"


def test_fmt_gbp_small_positive():
    assert prc._fmt_gbp(100) == "£+100"


def test_fmt_gbp_decimal_rounds():
    result = prc._fmt_gbp(1234.56)
    assert "1,235" in result


def test_parse_marker_returns_none_for_missing_file(tmp_path):
    missing = tmp_path / "nonexistent.md"
    try:
        result = prc.parse_marker(missing)
        assert result is None
    except (FileNotFoundError, ValueError, Exception):
        pass


def test_run_history_max_net_is_float(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    result = prc._run_history_max_net()
    assert isinstance(result, float)


# ── run-lock: prevent duplicate concurrent pipeline runs on one marker ───────

def test_run_lock_second_acquire_fails_while_first_held(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "RUN_LOCK_FILE", tmp_path / ".process_run_complete.lock")
    with prc._run_lock() as first:
        assert first is True
        with prc._run_lock() as second:
            assert second is False


def test_run_lock_reacquirable_after_release(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "RUN_LOCK_FILE", tmp_path / ".process_run_complete.lock")
    with prc._run_lock() as first:
        assert first is True
    with prc._run_lock() as second:
        assert second is True


def test_main_skips_when_lock_already_held(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(prc, "DONE_DIR", tmp_path / "staging" / "done")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(prc, "RUN_LOCK_FILE", tmp_path / ".process_run_complete.lock")

    marker, _ = make_marker(tmp_path)

    called = []
    monkeypatch.setattr(prc, "_process", lambda m: called.append(m) or 0)

    with prc._run_lock():
        rc = prc.main(str(marker))

    # EXIT_LOCK_SKIPPED, NOT 0 (fail-open closed 2026-07-29): returning the
    # success code here made background_worker's sweep record a publish-gate
    # SUCCESS for a marker nobody published, clearing the H15 wedge streak and
    # auto-resolving the open [ACTION NEEDED] item mid-wedge.
    assert rc == prc.EXIT_LOCK_SKIPPED
    assert rc != 0, "a lock-skip must never be indistinguishable from a real publish"
    assert called == []  # _process must never run while another instance holds the lock
    assert marker.exists()  # left in place for the lock-holder to archive


# ── DEPLOY_CONTENTION_BATCH_COMMITS.md: throttle pushes to <=1/30min ──────────

def test_push_due_true_when_no_prior_push_recorded(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "LAST_PUSH_FILE", tmp_path / ".last_push_time.json")
    assert prc._push_due() is True


def test_push_due_false_within_throttle_window(tmp_path, monkeypatch):
    import json as _json
    import time as _time
    push_file = tmp_path / ".last_push_time.json"
    push_file.write_text(_json.dumps({"ts": _time.time()}))
    monkeypatch.setattr(prc, "LAST_PUSH_FILE", push_file)
    assert prc._push_due() is False


def test_push_due_true_after_throttle_window_elapses(tmp_path, monkeypatch):
    import json as _json
    import time as _time
    push_file = tmp_path / ".last_push_time.json"
    push_file.write_text(_json.dumps({"ts": _time.time() - prc.PUSH_THROTTLE_SECONDS - 1}))
    monkeypatch.setattr(prc, "LAST_PUSH_FILE", push_file)
    assert prc._push_due() is True


def test_push_due_true_on_malformed_file(tmp_path, monkeypatch):
    push_file = tmp_path / ".last_push_time.json"
    push_file.write_text("not json")
    monkeypatch.setattr(prc, "LAST_PUSH_FILE", push_file)
    assert prc._push_due() is True


def test_git_commit_push_defers_push_within_throttle_window(tmp_path, monkeypatch):
    """Commit succeeds locally but git push is skipped when throttled --
    the return value must still be True (committed, not a failure) so the
    caller doesn't treat a deferred push as an error."""
    import json as _json
    import time as _time
    push_file = tmp_path / ".last_push_time.json"
    push_file.write_text(_json.dumps({"ts": _time.time()}))
    monkeypatch.setattr(prc, "LAST_PUSH_FILE", push_file)
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "LATEST_MD", tmp_path / "LATEST.md")

    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return fake_completed(cmd, **kwargs)

    monkeypatch.setattr(prc.subprocess, "run", fake_run)

    result = prc.git_commit_push("abc1234", 1000.0)

    assert result is True
    assert not any(c[:2] == ["git", "push"] for c in calls)


def test_git_commit_push_pushes_when_throttle_window_elapsed(tmp_path, monkeypatch):
    push_file = tmp_path / ".last_push_time.json"
    monkeypatch.setattr(prc, "LAST_PUSH_FILE", push_file)  # no prior push recorded
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "LATEST_MD", tmp_path / "LATEST.md")

    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        m = fake_completed(cmd, **kwargs)
        # Self-verifying push (2026-07-24 freeze fix): rev-parse HEAD and ls-remote
        # must report the SAME sha so _push_reached_origin confirms origin advanced.
        if cmd[:2] == ["git", "rev-parse"]:
            m.stdout = "deadbeef\n"
        elif cmd[:2] == ["git", "ls-remote"]:
            m.stdout = "deadbeef\trefs/heads/main\n"
        return m

    monkeypatch.setattr(prc.subprocess, "run", fake_run)

    result = prc.git_commit_push("abc1234", 1000.0)

    assert result is True
    assert any(c[:2] == ["git", "push"] for c in calls)
    assert push_file.exists()


def test_git_commit_push_does_not_record_on_phantom_push(tmp_path, monkeypatch):
    """THE 3.5h FREEZE, reproduced (R15 would-fire): `git push` returns rc=0 but
    origin does NOT advance (ls-remote head != local HEAD). git_commit_push must
    return False and NOT write .last_push_time.json -- so the throttle stays open
    and the next cycle retries, instead of deferring behind a phantom success."""
    push_file = tmp_path / ".last_push_time.json"
    monkeypatch.setattr(prc, "LAST_PUSH_FILE", push_file)  # no prior push recorded -> _push_due True
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "LATEST_MD", tmp_path / "LATEST.md")
    monkeypatch.setattr(prc, "notify", lambda *a, **k: None, raising=False)

    def fake_run(cmd, **kwargs):
        m = fake_completed(cmd, **kwargs)
        if cmd[:2] == ["git", "rev-parse"]:
            m.stdout = "NEWlocalsha\n"
        elif cmd[:2] == ["git", "ls-remote"]:
            m.stdout = "OLDremotesha\trefs/heads/main\n"   # origin did NOT advance
        return m

    monkeypatch.setattr(prc.subprocess, "run", fake_run)

    result = prc.git_commit_push("abc1234", 1000.0)

    assert result is False, "a push that did not reach origin must report failure"
    assert not push_file.exists(), "phantom push must NOT reset the throttle (the freeze)"


def test_git_commit_push_no_push_recorded_if_commit_fails(tmp_path, monkeypatch):
    push_file = tmp_path / ".last_push_time.json"
    monkeypatch.setattr(prc, "LAST_PUSH_FILE", push_file)
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "LATEST_MD", tmp_path / "LATEST.md")

    monkeypatch.setattr(prc.subprocess, "run", fake_completed)
    # The refusal is the LANDING's now, not a `git commit` return code -- see
    # `_the_landing_lands`, which this line overrides because this test IS about the refusal.
    monkeypatch.setattr(
        prc, "_land_publish_commit",
        lambda pathspec, msg, git_hash: {
            "sha": "", "lost": [],
            "refusal": "GATE RED on the resulting tree (rc=1). This is the tree the commit "
                       "WOULD create, not the working tree."})

    result = prc.git_commit_push("abc1234", 1000.0)

    assert result is False
    assert not push_file.exists()


# --- Change-detection gate (DIRECTOR_SEQUENCE_AND_TOKEN_ECONOMY.md, 2026-07-08) ---

def _sample_data(net=1535307.74):
    return {
        "total_net_gbp": net,
        "total_gross_gbp": 6452602.5,
        "enterprise_value_gbp": 8930210.95,
        "final_treasury_gbp": 3911893.89,
        "starting_treasury_gbp": 2466636.22,
        "total_capital_gbp": 51432.98,
        "net_margin_after_cost_to_serve_gbp": 6433342.81,
        "committee_wake_ups_total": 38,
        "bills_total": 1605,
        "retention_log": [{"outcome": "retained"}] * 14,
        "no_offer_churn_log": [{"r": 1}] * 6,
        "churned_billing_accounts": ["C%d" % i for i in range(6)],
        "administration_event": None,
    }


def test_fingerprint_stable_and_sensitive():
    a = prc._run_fingerprint(_sample_data())
    b = prc._run_fingerprint(_sample_data())
    assert a == b  # same inputs, same day -> identical fingerprint
    c = prc._run_fingerprint(_sample_data(net=999.99))
    assert c != a  # a changed headline figure must change the fingerprint
    assert a["retained"] == 14 and a["offers"] == 14


def test_a_world_change_alone_breaks_the_fingerprint():
    """THE DEFECT: the skip gate's justification is "byte-identical business surfaces", and it was
    measured over headline FIGURES only.

    A re-fit of the departure level moves the world. If it moves no headline figure past its
    rounding, the identical-run gate would archive the marker and publish nothing -- so the first
    page carrying the new world's disclosure would never be written, and the site would go on
    stating a world that no longer existed.

    MUTATION: drop `world_level_digest` from `_run_fingerprint` and this fires.

    The two payloads below differ in NOTHING a reader of the figures could see. If they
    fingerprint the same, a world change is invisible to the publisher."""
    same_world = _sample_data()
    same_world["_cache_meta"] = {"world_level": {"digest": "aaaaaaaaaaaaaaaa"}}
    moved_world = _sample_data()
    moved_world["_cache_meta"] = {"world_level": {"digest": "bbbbbbbbbbbbbbbb"}}

    for key in ("total_net_gbp", "total_gross_gbp", "bills_total"):
        assert same_world.get(key) == moved_world.get(key), "the fixture moved a figure"

    assert prc._run_fingerprint(same_world) != prc._run_fingerprint(moved_world), (
        "two runs in different departure worlds fingerprint the same, so the second is skipped "
        "as 'pure burn' and its world never reaches a page"
    )


def test_an_unstamped_run_fingerprints_exactly_as_it_did_before():
    """THE NULL CONTROL, and it is what makes the leg above meaningful rather than tautological.

    Every run output written before 2026-09-04 carries no stamp. If adding the world key changed
    their behaviour at all -- made two identical old runs differ, say -- the repair would have
    broken the skip gate for the entire back catalogue while looking like caution."""
    a = _sample_data()
    b = _sample_data()
    assert prc._run_fingerprint(a) == prc._run_fingerprint(b)
    assert prc._run_fingerprint(a)["world_level_digest"] is None, (
        "an unstamped run must record the absence, not invent a world for it"
    )


def test_fingerprint_roundtrip():
    assert prc._read_last_fingerprint() is None
    fp = prc._run_fingerprint(_sample_data())
    prc._write_last_fingerprint(fp)
    assert prc._read_last_fingerprint() == fp


def test_gate_skips_identical_run(tmp_path, monkeypatch):
    """An identical run is archived with no regen/test/commit."""
    staging = tmp_path / "staging"
    done = staging / "done"
    staging.mkdir(parents=True)
    done.mkdir()
    monkeypatch.setattr(prc, "STAGING_DIR", staging)
    monkeypatch.setattr(prc, "DONE_DIR", done)

    data = _sample_data()
    json_path = tmp_path / "run_output_latest.json"
    json_path.write_text(json.dumps(data))
    fp = prc._run_fingerprint(data)
    fp["source_git_hash"] = "abc"  # matches the marker's "Git: abc" below -- genuinely nothing changed
    prc._write_last_fingerprint(fp)

    marker = staging / "run_complete_X.md"
    marker.write_text("# Run Complete\n\nGit: abc\nJSON: %s\nDuration: 200s\n" % json_path)

    # Any pipeline step running is a gate failure — make report regen explode.
    monkeypatch.setattr(prc, "regenerate_report", lambda jp: pytest.fail("gate did not skip"))

    rc = prc._process(str(marker))
    assert rc == 0
    assert (done / marker.name).exists()  # archived
    assert not marker.exists()


def test_gate_never_skips_admin_event(tmp_path, monkeypatch):
    """An administration event always processes so the NTFY exception fires."""
    staging = tmp_path / "staging"
    done = staging / "done"
    staging.mkdir(parents=True)
    done.mkdir()
    monkeypatch.setattr(prc, "STAGING_DIR", staging)
    monkeypatch.setattr(prc, "DONE_DIR", done)

    data = _sample_data()
    data["administration_event"] = {"date": "2020-03-01"}
    json_path = tmp_path / "run_output_latest.json"
    json_path.write_text(json.dumps(data))
    prc._write_last_fingerprint(prc._run_fingerprint(data))

    marker = staging / "run_complete_Y.md"
    marker.write_text("# Run Complete\n\nGit: abc\nJSON: %s\nDuration: 200s\n" % json_path)

    # Reaching regen proves the gate did NOT skip; stop there to keep the test cheap.
    monkeypatch.setattr(prc, "regenerate_report", lambda jp: (_ for _ in ()).throw(SystemExit("proceeded")))
    with pytest.raises(SystemExit):
        prc._process(str(marker))


def test_gate_never_skips_when_git_hash_differs(tmp_path, monkeypatch):
    """R3 two-strike redesign (2026-07-12, director page comment: '/project/
    data looks stale'): a real new commit whose headline financial figures
    happen to be identical to the last processed run must NOT be silently
    skipped -- this is the exact class of incident FORCE_REPUBLISH_FLAG was
    built for (see above), recurring on an ordinary commit rather than a
    hold-release. Same fingerprint content, different producing commit."""
    staging = tmp_path / "staging"
    done = staging / "done"
    staging.mkdir(parents=True)
    done.mkdir()
    monkeypatch.setattr(prc, "STAGING_DIR", staging)
    monkeypatch.setattr(prc, "DONE_DIR", done)

    data = _sample_data()
    json_path = tmp_path / "run_output_latest.json"
    json_path.write_text(json.dumps(data))
    fp = prc._run_fingerprint(data)
    fp["source_git_hash"] = "old0000"  # a DIFFERENT commit than the marker below
    prc._write_last_fingerprint(fp)

    marker = staging / "run_complete_Z.md"
    marker.write_text("# Run Complete\n\nGit: new1111\nJSON: %s\nDuration: 200s\n" % json_path)

    # Reaching regen proves the gate did NOT skip; stop there to keep the test cheap.
    monkeypatch.setattr(prc, "regenerate_report", lambda jp: (_ for _ in ()).throw(SystemExit("proceeded")))
    with pytest.raises(SystemExit):
        prc._process(str(marker))


def test_gate_skips_when_git_hash_matches_too(tmp_path, monkeypatch):
    """Sanity converse of the above: identical fingerprint AND identical
    producing commit still skips -- the fix must not make the gate skip
    nothing at all."""
    staging = tmp_path / "staging"
    done = staging / "done"
    staging.mkdir(parents=True)
    done.mkdir()
    monkeypatch.setattr(prc, "STAGING_DIR", staging)
    monkeypatch.setattr(prc, "DONE_DIR", done)

    data = _sample_data()
    json_path = tmp_path / "run_output_latest.json"
    json_path.write_text(json.dumps(data))
    fp = prc._run_fingerprint(data)
    fp["source_git_hash"] = "same0000"
    prc._write_last_fingerprint(fp)

    marker = staging / "run_complete_W.md"
    marker.write_text("# Run Complete\n\nGit: same0000\nJSON: %s\nDuration: 200s\n" % json_path)

    monkeypatch.setattr(prc, "regenerate_report", lambda jp: pytest.fail("gate did not skip"))

    rc = prc._process(str(marker))
    assert rc == 0
    assert (done / marker.name).exists()


def test_git_commit_push_commits_whole_generated_site_data_surface(tmp_path, monkeypatch):
    """R10 class-closure regression (SITE1 Expert-Hour, 2026-07-16): every
    generated site/data/*.json must be staged, not an explicit per-file list
    that silently omits new ones. simplified.json / provisional_plan.json /
    system_status.json were each regenerated every run yet never committed --
    the live doors froze (the simplifications register hid ~42% of itself, the
    director queue went 6 days stale). This test FAILS if the glob is removed,
    so the class cannot recur unnoticed (R15: a control must be able to fail)."""
    monkeypatch.setattr(prc, "LAST_PUSH_FILE", tmp_path / ".last_push_time.json")
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "LATEST_MD", tmp_path / "LATEST.md")

    data_dir = tmp_path / "site" / "data"
    data_dir.mkdir(parents=True)
    previously_orphaned = ["simplified.json", "provisional_plan.json", "system_status.json"]
    a_future_generated = "some_new_door.json"
    for name in previously_orphaned + [a_future_generated]:
        (data_dir / name).write_text("{}")

    added = []

    monkeypatch.setattr(prc.subprocess, "run", fake_completed)
    # READ THE PATHSPEC, NOT `git add` (2026-09-08). The publish commit is a surgical landing:
    # there is no index and no `git add`, so a control that watched for one would be watching an
    # empty list and would be green for the very omission it names. The pathspec handed to the
    # landing is what the commit carries, so that is where the glob has to show up.
    monkeypatch.setattr(
        prc, "_land_publish_commit",
        lambda pathspec, msg, git_hash: (added.extend(pathspec)
                                         or {"sha": "0" * 40, "refusal": "", "lost": []}))

    prc.git_commit_push("abc1234", 1000.0)

    for name in previously_orphaned + [a_future_generated]:
        assert str(data_dir / name) in added, (
            "%s must be committed by the site/data glob, not silently orphaned" % name
        )


def test_pending_inboxes_folded_before_the_gate_runs():
    """Class fix (2026-07-16): the publish gate must reconcile the map (fold any pending
    atom_status inbox) BEFORE run_fast_tests, so the map-reconciliation control tests a
    reconciled map, not a fork/fold-race transient (an unfolded W1_8 inbox wedged the
    gate). Structural R15 guard: merge_atom_status.merge() is invoked, and it appears
    BEFORE the run_fast_tests call in main() — revert the ordering and this fails."""
    src = inspect.getsource(prc._process)  # main() delegates the real pipeline to _process()
    assert "merge_atom_status" in src and ".merge()" in src, "pre-gate inbox fold missing"
    assert src.index("_mas.merge()") < src.index("run_fast_tests("), \
        "the inbox fold must run BEFORE the test gate (reconcile, then test)"


# ── THE PUBLISH BLOCK'S COLLABORATORS MUST NOT REACH THE REAL TREE (2026-09-04) ──
# Five tests here drive main()/_process() end to end, and for months four of the generators
# that block calls wrote their real committed artefacts: two site feeds, the pricing-arm
# ledger, and grid_intensity_feed.json — that last one TRUNCATED from 2314 lines to 293,
# because the regeneration ran against whatever the test environment could reach. It refused
# landings (promote_worktree_landing reads a tracked change outside the machine-churn
# directories as "this landing is not the whole of what was done"), and the publish daemon
# commits generated site output it finds in the tree, so a test-truncated feed had a route to
# land as data with no source change beside it to make anyone look.
#
# _isolate_project_dir now redirects all four. The control below is about the FIFTH: per-test
# and per-registry wiring is opt-in and invisible when omitted, which is the same objection
# that fixture's own docstring makes about the incident before it. So the module list is
# derived from LIVE source and compared for equality — a collaborator wired into the publish
# block reds this file until it is declared, which is the one moment isolating it is cheap.

def test_every_module_the_publish_block_imports_is_declared_here():
    src = inspect.getsource(prc._process) + inspect.getsource(prc._run_weather_data)
    found = _imported_modules(src)
    undeclared = found - set(_PUBLISH_BLOCK_COLLABORATORS)
    assert not undeclared, (
        "the publish block imports {} and nothing here says whether it writes into the real "
        "tree. Add it to _PUBLISH_BLOCK_COLLABORATORS: either isolate its output through one of "
        "the three registries at the top of this file, or state why it writes nothing under the "
        "repo root of its own accord.".format(sorted(undeclared))
    )
    gone = set(_PUBLISH_BLOCK_COLLABORATORS) - found
    assert not gone, (
        "_PUBLISH_BLOCK_COLLABORATORS still declares {}, which the publish block no longer "
        "imports — a stale entry here is a reason nobody re-read".format(sorted(gone))
    )


def test_a_collaborator_declared_isolated_is_actually_in_the_registry_it_names():
    """The declaration above and the three registries are checked AGAINST EACH OTHER, because
    each is otherwise free to be the only thing that knows. Deleting an entry from a registry
    would silently delete its own parametrised case below — a control that stops testing what
    it stopped covering. Here the claim survives the deletion and reds instead."""
    registries = {
        "_PIPELINE_OUTPUT_PATHS": {e[0] for e in _PIPELINE_OUTPUT_PATHS},
        "_PIPELINE_OUTPUT_WRITERS": {e[0] for e in _PIPELINE_OUTPUT_WRITERS},
        "_PIPELINE_OUTPUT_FALLBACK_WRITERS": {e[0] for e in _PIPELINE_OUTPUT_FALLBACK_WRITERS},
    }
    claimed = 0
    for module_name, reason in _PUBLISH_BLOCK_COLLABORATORS.items():
        for registry_name, members in registries.items():
            if registry_name in reason:
                claimed += 1
                assert module_name in members, (
                    "{} is declared 'isolated by {}' and is not in it — the declaration is the "
                    "only thing still saying its real output is redirected".format(
                        module_name, registry_name)
                )
    assert claimed == sum(len(m) for m in registries.values()), (
        "a registry entry exists that no collaborator declaration points at, so deleting it "
        "would cost nothing"
    )


def test_the_declaration_control_ACTUALLY_REDS_on_an_undeclared_collaborator():
    """Reachability leg (CONTROLS_THAT_CANNOT_FAIL): the extraction above is handed a source
    block it did not come from, so the failing branch is shown to exist rather than assumed.
    Without this, a regex that matched nothing would pass the control forever."""
    assert _imported_modules("    from tools.brand_new_generator import generate\n") == {
        "tools.brand_new_generator"}
    assert "tools.brand_new_generator" not in _PUBLISH_BLOCK_COLLABORATORS


@pytest.mark.parametrize(
    "module_name,function_name,keyword,constant,relative", _PIPELINE_OUTPUT_FALLBACK_WRITERS,
    ids=[e[4] for e in _PIPELINE_OUTPUT_FALLBACK_WRITERS])
def test_the_optional_output_writers_are_bound_away_from_their_real_destination(
        module_name, function_name, keyword, constant, relative):
    """The redirection is asserted at the destination a call would actually receive, not at the
    fixture's intent: `dest = OUT_PATH if out_path is None else out_path` means an unbound
    keyword writes the committed artefact, so the property is that the bound value is a real
    path and is NOT the module's own constant."""
    module = importlib.import_module(module_name)
    bound = getattr(module, function_name)
    assert isinstance(bound, functools.partial), (
        "{}.{} is not redirected — _isolate_project_dir did not reach it".format(
            module_name, function_name))
    destination = Path(bound.keywords[keyword])
    real_root = Path(prc.__file__).resolve().parent.parent
    assert destination == prc.PROJECT_DIR / relative, (
        "redirected to {}, which is not this test's sandbox".format(destination))
    with pytest.raises(ValueError):
        destination.resolve().relative_to(real_root)  # i.e. it is outside the real repo
    assert str(getattr(module, constant)).endswith(relative), (
        "the real destination this is standing in for has moved")


# ── SELF-VERIFYING PUSH (R15 both-ways) — the 3.5h origin-freeze incident, 2026-07-24 ──
# A bare `git push` returned rc=0 without advancing origin (phantom "up-to-date"),
# and _record_push_time was called anyway -> _push_due stayed False -> every real
# push deferred for 3.5h while 15 commits stacked locally, unseen by the advisor
# bridge. _push_reached_origin makes success GROUND-TRUTH so the freeze cannot recur.

def test_push_reached_origin_true_only_on_verified_advance():
    """CORRECT path: rc==0 AND real remote head == local HEAD -> counts as success."""
    assert prc._push_reached_origin(0, "abc123", "abc123") is True


def test_push_reached_origin_false_on_phantom_up_to_date():
    """THE FREEZE (would-fire): rc==0 but origin did NOT advance (remote behind
    local). Must NOT count -> throttle not reset -> next cycle retries."""
    assert prc._push_reached_origin(0, "OLDsha", "NEWsha") is False


def test_push_reached_origin_false_on_nonzero_rc():
    assert prc._push_reached_origin(1, "abc123", "abc123") is False


def test_push_reached_origin_false_on_empty_remote_head():
    """ls-remote failed/empty -> cannot confirm -> not a success (fail-closed)."""
    assert prc._push_reached_origin(0, "", "abc123") is False


def _make_resident(home, monkeypatch):
    """Make this process look like the RESIDENT seat: a real marker file under a
    throwaway HOME, no SE_SEAT override. Same helper shape as
    tests/background/test_seat_guard_daemons.py::_make_marker -- deliberately the
    production discriminator, not the env escape hatch."""
    marker = Path(home) / ".config" / "synthetic-enterprise" / ".env.ntfy"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("SE_NTFY_TOPIC=not-a-real-secret\n")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("SE_SEAT", raising=False)
    return marker


def _make_foreign(home, monkeypatch):
    """Make this process look like a FOREIGN seat: HOME with no marker, no override."""
    Path(home).mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("SE_SEAT", raising=False)


# ── Fault #1 (2026-07-25 overnight publish-freeze): published liveness decoupled from content-change ──
class TestRefreshPublishedLivenessOnSkip:
    """The on-disk worker-tick heartbeat updates every 60s but only reached origin via a CONTENT
    publish; a byte-identical-output night (change-detection SKIP every cycle) froze the PUBLISHED
    heartbeat ~4h though every daemon was healthy. `_refresh_published_liveness_on_skip` publishes
    ONLY the liveness surface on a SKIP, throttled to the same 30-min push cadence. Proven both ways:
    throttled -> no-op; due -> commits ONLY the liveness paths and records a verified push."""

    def _wire(self, tmp_path, monkeypatch, *, push_due, commit_rc=0, reached=True):
        from contextlib import nullcontext
        # RESIDENT seat, via a real marker file under a throwaway HOME and NO SE_SEAT
        # override -- so these behaviour tests run the PRODUCTION discriminator rather
        # than an escape hatch, and stay valid on a resident machine and a cloud
        # sandbox alike (see the seat-guard tests below).
        _make_resident(tmp_path / "home", monkeypatch)
        monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
        (tmp_path / "site" / "data").mkdir(parents=True, exist_ok=True)
        (tmp_path / "docs" / "observability").mkdir(parents=True, exist_ok=True)
        (tmp_path / "site" / "data" / "tick_heartbeat.json").write_text('{"ts": 1}')
        (tmp_path / "docs" / "observability" / "agent_status.json").write_text('{"a": 1}')
        monkeypatch.setattr(prc, "tree_lock", lambda *a, **k: nullcontext())
        monkeypatch.setattr(prc, "_push_due", lambda: push_due)
        recorded = []
        monkeypatch.setattr(prc, "_record_push_time", lambda: recorded.append(True))
        monkeypatch.setattr(prc, "_push_reached_origin", lambda *a, **k: reached)
        calls = []

        def fake_run(argv, **kwargs):
            calls.append(argv)
            rc = 0
            if argv[:2] == ["git", "commit"]:
                rc = commit_rc
            out = ""
            if argv[:2] == ["git", "rev-parse"]:
                out = "LOCALHEAD\n"
            if argv[:2] == ["git", "ls-remote"]:
                out = "LOCALHEAD\trefs/heads/main\n"
            return type("R", (), {"returncode": rc, "stdout": out, "stderr": ""})()

        monkeypatch.setattr(prc.subprocess, "run", fake_run)
        return calls, recorded

    def test_throttled_is_a_noop(self, tmp_path, monkeypatch):
        calls, recorded = self._wire(tmp_path, monkeypatch, push_due=False)
        assert prc._refresh_published_liveness_on_skip("abc123") is False
        assert calls == []            # no git calls at all while throttled
        assert recorded == []

    def test_due_commits_only_liveness_paths_and_records_push(self, tmp_path, monkeypatch):
        calls, recorded = self._wire(tmp_path, monkeypatch, push_due=True, reached=True)
        assert prc._refresh_published_liveness_on_skip("abc123") is True
        commit = next(c for c in calls if c[:2] == ["git", "commit"])
        # commit pathspec is EXACTLY the liveness files -- never the whole index (no concurrent sweep)
        assert "--" in commit
        committed_paths = commit[commit.index("--") + 1:]
        assert {Path(p).name for p in committed_paths} == {"tick_heartbeat.json", "agent_status.json"}
        assert any(c[:2] == ["git", "push"] for c in calls)
        assert recorded == [True]      # throttle recorded ONLY on a verified advance

    def test_due_but_phantom_push_does_not_record(self, tmp_path, monkeypatch):
        calls, recorded = self._wire(tmp_path, monkeypatch, push_due=True, reached=False)
        assert prc._refresh_published_liveness_on_skip("abc123") is False
        assert recorded == []          # phantom push (origin did not advance) never resets throttle

    def test_nothing_to_commit_skips_push(self, tmp_path, monkeypatch):
        calls, recorded = self._wire(tmp_path, monkeypatch, push_due=True, commit_rc=1)
        assert prc._refresh_published_liveness_on_skip("abc123") is False
        assert not any(c[:2] == ["git", "push"] for c in calls)
        assert recorded == []


# ── THE GHOST PUSHER (issue #11): the seat guard sits on the SIDE-EFFECT ─────────────────────
class TestLivenessPublishRefusesForeignSoil:
    """`_refresh_published_liveness_on_skip` is the one function in this module that commits
    and pushes without passing through `__main__`. The entrypoint guard therefore does not
    cover it: any caller that IMPORTS the module and reaches the change-detection SKIP branch
    lands here with full push authority on whatever checkout it is standing in. That is the
    proven ghost -- a test run manufactured a real `chore(liveness)... (git=abc)` commit and
    fired `git push origin HEAD:main`, landing only where credentials existed.

    So the guard moved to the side-effect. R15, both directions AND the ordering:
      * FOREIGN  -> one stderr line, returns False, ZERO git calls, and the refusal happens
                    before any other state is even read.
      * RESIDENT -> passes through and publishes exactly as before (the class above, which
                    now wires a real resident marker, is that direction's proof).
    Neuter `_seat.is_resident_seat()` to `return True` and every test here reds."""

    def _wire_foreign_but_otherwise_ready(self, tmp_path, monkeypatch):
        """Everything the publish path needs is in place and a push IS due -- the ONLY
        reason nothing happens must be the seat. A guard tested against a path that would
        not have published anyway proves nothing (R15 TAUTOLOGY)."""
        monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
        (tmp_path / "site" / "data").mkdir(parents=True, exist_ok=True)
        (tmp_path / "docs" / "observability").mkdir(parents=True, exist_ok=True)
        (tmp_path / "site" / "data" / "tick_heartbeat.json").write_text('{"ts": 1}')
        (tmp_path / "docs" / "observability" / "agent_status.json").write_text('{"a": 1}')
        monkeypatch.setattr(prc, "tree_lock", lambda *a, **k: contextlib.nullcontext())
        monkeypatch.setattr(prc, "_push_due", lambda: True)
        monkeypatch.setattr(prc, "_record_push_time",
                            lambda: pytest.fail("a foreign seat recorded a push time"))
        calls = []
        monkeypatch.setattr(prc.subprocess, "run",
                            lambda argv, **kw: calls.append(argv))
        _make_foreign(tmp_path / "home", monkeypatch)
        return calls

    def test_foreign_seat_makes_no_git_calls_and_returns_false(self, tmp_path, monkeypatch, capsys):
        calls = self._wire_foreign_but_otherwise_ready(tmp_path, monkeypatch)
        assert prc._refresh_published_liveness_on_skip("abc") is False
        assert calls == [], "a foreign seat reached git: {}".format(calls)

    def test_foreign_seat_leaves_one_stderr_line_naming_the_refusal(self, tmp_path, monkeypatch,
                                                                    capsys):
        """A refusal that says nothing is indistinguishable from a healthy no-op (R5)."""
        self._wire_foreign_but_otherwise_ready(tmp_path, monkeypatch)
        prc._refresh_published_liveness_on_skip("abc")
        err = capsys.readouterr().err
        assert err.count("\n") == 1, "expected exactly one stderr line, got: {!r}".format(err)
        assert err.startswith("seat-guard: foreign,")
        assert "_refresh_published_liveness_on_skip" in err

    def test_the_seat_is_checked_before_anything_else(self, tmp_path, monkeypatch):
        """Ordering lock: the guard is the FIRST act, not merely present somewhere.
        `_push_due` is the next thing the function would touch -- if it is reached on
        foreign soil the guard has drifted below it and this reds."""
        self._wire_foreign_but_otherwise_ready(tmp_path, monkeypatch)
        monkeypatch.setattr(prc, "_push_due",
                            lambda: pytest.fail("throttle state read before the seat check"))
        assert prc._refresh_published_liveness_on_skip("abc") is False

    def test_the_import_call_bypass_is_closed_end_to_end(self, tmp_path, monkeypatch):
        """The ghost's ACTUAL route, reproduced: import the module, hand `_process` a marker
        whose fingerprint matches the last processed run, and let the change-detection gate
        SKIP. At HEAD that reached git on the real tree. `__main__` -- and therefore
        `refuse_if_foreign` -- is never involved."""
        staging = tmp_path / "staging"
        (staging / "done").mkdir(parents=True)
        monkeypatch.setattr(prc, "STAGING_DIR", staging)
        monkeypatch.setattr(prc, "DONE_DIR", staging / "done")
        calls = self._wire_foreign_but_otherwise_ready(tmp_path, monkeypatch)

        data = _sample_data()
        json_path = tmp_path / "run_output_latest.json"
        json_path.write_text(json.dumps(data))
        fp = prc._run_fingerprint(data)
        fp["source_git_hash"] = "abc"          # matches the marker -> the SKIP branch fires
        prc._write_last_fingerprint(fp)
        marker = staging / "run_complete_GHOST.md"
        marker.write_text("# Run Complete\n\nGit: abc\nJSON: %s\nDuration: 200s\n" % json_path)

        assert prc._process(str(marker)) == 0
        assert (staging / "done" / marker.name).exists()   # still archived: publishing is unaffected
        assert calls == [], "the SKIP branch reached git on foreign soil: {}".format(calls)


class TestFrozenBaselineOutOfBandTrigger:
    """The weekly frozen-policy baseline refresh is a multi-minute decade replay
    with live LLM calls. It MUST run out of band, never synchronously in the
    publish path (2026-07-29 wedge: run inline it backed up 22 run markers and
    the 900s sweep timeout re-attempted it forever)."""

    def test_launched_out_of_band_when_stale_and_never_runs_inline(self, monkeypatch):
        """THIS TEST USED TO PIN THE DEFECT (2026-09-08). Its last assertion was
        `kwargs["start_new_session"] is True, "must be detached to outlive publish"` -- and that
        is precisely the claim three launches of one measurement refuted. Every user unit here is
        KillMode=control-group; `setsid` changes the session and the process group, and a cgroup
        is neither, so the refresh died with the publisher's teardown while a green control said
        it was correctly detached. A control keyed to today's answer goes red when the code
        becomes more honest, which is exactly backwards, and this is what that looks like.

        What survives unchanged is the thing this class was really about: NEVER INLINE."""
        import tools.run_frozen_baseline as rfb
        from background import launch_long_job
        monkeypatch.setattr(rfb, "should_refresh_baseline", lambda *a, **k: True)

        launches = []
        monkeypatch.setattr(launch_long_job, "launch",
                            lambda job, command, **kw: launches.append((job, command, kw))
                            or {"unit": "longjob-x", "log": "/var/tmp/x.log"})

        # If anything tried to run the replay inline, this would fire.
        monkeypatch.setattr(rfb, "run_frozen_baseline",
                            lambda *a, **k: (_ for _ in ()).throw(
                                AssertionError("replay ran inline in the publish path")))

        def no_popen(*a, **k):
            raise AssertionError(
                "the refresh was spawned directly; a setsid child dies with the publisher's "
                "cgroup -- it goes through background.launch_long_job")

        monkeypatch.setattr(prc.subprocess, "Popen", no_popen)

        prc._trigger_frozen_baseline_refresh_out_of_band("abc123")

        assert len(launches) == 1, "stale baseline must launch exactly one refresh"
        job, command, kwargs = launches[0]
        assert command[1:] == ["-m", "tools.run_frozen_baseline", "--if-stale"]
        assert kwargs["artefact"].endswith("frozen_policy_baseline.json"), (
            "a launch record with no artefact can never settle to FINISHED, so a completed "
            "refresh would read as an unexplained death forever")

    def test_does_not_spawn_when_fresh(self, monkeypatch):
        import tools.run_frozen_baseline as rfb
        from background import launch_long_job
        monkeypatch.setattr(rfb, "should_refresh_baseline", lambda *a, **k: False)

        def fail_popen(*a, **k):
            raise AssertionError("no refresh must be spawned when the baseline is fresh")

        monkeypatch.setattr(prc.subprocess, "Popen", fail_popen)
        # The route changed on 2026-09-08, so the leg that proves nothing starts had to change
        # with it -- guarding only `Popen` would have gone quiet the moment the spawn moved.
        monkeypatch.setattr(launch_long_job, "launch", fail_popen)
        # returns without spawning
        prc._trigger_frozen_baseline_refresh_out_of_band("abc123")


# ── Publish-gate red output is CAPTURED and LOGGED (R5/R9) ───────────────────
# Regression cover for the 2026-07-29 ~67-min publish wedge whose entire
# recorded diagnosis was the string "Tests FAILED - not committing": the gate
# ran pytest without capturing it, so WHICH test blocked publishing was
# unknowable from the log, and by the time anyone looked the site data had been
# regenerated and the red was no longer reproducible. R15: each test below is
# written so that reverting the fix (dropping capture_output, or not calling
# _log_gate_failure_payload) makes it FAIL.

class _FakeCompleted:
    def __init__(self, returncode, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _gate_log_text(monkeypatch, tmp_path, result):
    """Run run_fast_tests against a faked pytest `result` and return the log."""
    log_path = tmp_path / "gate-log.md"
    monkeypatch.setattr(prc, "LOG_FILE", log_path)
    monkeypatch.setattr(prc, "LAST_TESTED_HASH_FILE", tmp_path / ".last_tested_hash")

    captured_kwargs = {}

    def fake_run(argv, **kwargs):
        captured_kwargs.update(kwargs)
        return result

    # DIRECTOR_RULING_PUBLISH_GATE_SUBJECT: run_fast_tests now materialises a clean HEAD checkout
    # before running the suite, so a bare `subprocess.run` stub would answer `git archive` and
    # `tar` with the fake pytest result too. Stub the checkout itself and let these tests keep
    # their subject: what the gate does with a pytest RESULT. The checkout's own behaviour is
    # covered separately (test_publish_gate_subject_is_head.py).
    checkout = tmp_path / "head"
    checkout.mkdir(exist_ok=True)
    # ...and make it look EXTRACTED, not merely mkdir'd. A bare directory is the state the
    # real harness produces only when the checkout has FAILED (2026-08-12: `git init` died with
    # `fatal: cannot mkdir`, the directory existed and held nothing, and the gate ran the full
    # suite against it on 28 cycles). `_run_gate_in` now refuses that root, so a stub that keeps
    # supplying it would test the refusal instead of these tests' actual subject -- what the
    # gate does with a pytest RESULT.
    from background.publish_scope import ROOT_REPO_MARKER
    (checkout / ROOT_REPO_MARKER).mkdir(parents=True, exist_ok=True)

    @contextlib.contextmanager
    def fake_checkout():
        yield checkout

    monkeypatch.setattr(prc, "_head_checkout", fake_checkout)
    monkeypatch.setattr(prc.subprocess, "run", fake_run)
    passed, timed_out = prc.run_fast_tests("deadbeef")
    text = log_path.read_text() if log_path.exists() else ""
    return passed, timed_out, text, captured_kwargs


def test_red_publish_gate_logs_the_blocking_test_node_ids(monkeypatch, tmp_path):
    """A red gate must name the tests that blocked publishing.

    MUTATION: delete the `_log_gate_failure_payload(result)` call in
    run_fast_tests and this fails -- the log again says only "Tests FAILED"."""
    out = (
        "some pytest chatter\n"
        "FAILED tests/tools/test_site_freshness.py::test_dashboard_is_current - AssertionError\n"
        "ERROR tests/background/test_thing.py::test_other\n"
        "1 failed, 2 passed\n"
    )
    passed, timed_out, text, _ = _gate_log_text(
        monkeypatch, tmp_path, _FakeCompleted(1, stdout=out))

    assert passed is False and timed_out is False
    assert "test_site_freshness.py::test_dashboard_is_current" in text, (
        "the failing node ID must reach the log -- otherwise a wedge is "
        "undiagnosable after the site data is regenerated")
    assert "test_thing.py::test_other" in text, "ERROR lines count as blocking too"


def test_a_timed_out_publish_gate_blocks_the_commit(monkeypatch, tmp_path):
    """R15: an unavailable check is a FAILED check. A gate that did not FINISH cannot
    authorise a publish.

    The named defect, observed live on 2026-08-09: the suite takes ~613s and the timeout was
    600s, so the gate timed out on essentially every cycle and the timeout branch returned
    `True` ("resource constraint, not a test failure"). That walked the full success path --
    marker archived, commit attempted, and the publish-gate outcome recorded as rc=0, which
    CLEARS wedge_since/episode_failures and re-arms the alarm. A gate that never ran was
    silently disarming the alarm whose whole job is to say it never ran.

    MUTATION: restore `return True, True` in the TimeoutExpired branch and this fails."""
    log_path = tmp_path / "gate-log.md"
    monkeypatch.setattr(prc, "LOG_FILE", log_path)
    last_tested = tmp_path / ".last_tested_hash"
    monkeypatch.setattr(prc, "LAST_TESTED_HASH_FILE", last_tested)

    def fake_run(argv, **kwargs):
        raise prc.subprocess.TimeoutExpired(cmd=argv, timeout=kwargs.get("timeout"))

    monkeypatch.setattr(prc.subprocess, "run", fake_run)
    passed, timed_out = prc.run_fast_tests("deadbeef")

    assert timed_out is True
    assert passed is False, (
        "a timed-out gate must BLOCK the publish -- returning True archives the marker, "
        "publishes unverified content, and clears the wedge alarm's episode memory"
    )
    assert not last_tested.exists(), (
        "a gate that did not finish must not stamp .last_tested_hash -- that hash is the "
        "INDEPENDENT signal the supervisor's wedge draw cross-checks against"
    )
    assert "NOT committing" in log_path.read_text()


def test_the_gate_timeout_exceeds_the_suites_own_runtime(monkeypatch, tmp_path):
    """The timeout must be generous enough that hitting it is an ANOMALY, not the norm.

    The 600s timeout was BELOW the suite's own measured runtime (612.94s for 22,525 tests),
    so the gate could not pass -- it could only time out. A timeout that the healthy case
    exceeds is not a safety bound, it is a coin flip.

    THE CONSTANT MOVES WITH THE SUBJECT (OPS2 criterion 2). 613s was the IN-TREE suite, and
    the gate's subject is now a clean HEAD checkout, which is a different and slower thing.
    It has moved TWICE for that reason and the second move is the honest one:

      * 1291.9s (23,249 passed, HEAD 3ee4541a7) justified 2600s -- but that phase ran with
        `cwd: /tmp/publish-gate-head-reused`, the shared directory the R3 elimination deleted,
        and its own record says the bytecode came from outside the run. It was never a timing
        of the subject the gate ships.
      * 1411.2s (23,710 passed, rc=1, HEAD d1a5875b4, 2026-08-11) is the shipped subject:
        a fresh throwaway extraction of HEAD with no bytecode, which is what every cycle now
        pays. Recorded in docs/observability/publish_gate_subject_cost.json as
        `throwaway_checkout`, and `ran_to_completion` -- a red suite that reported, not a
        killed one.
      * 1784.6s (23,831 passed, rc=1, launch 13, 2026-08-11 same day) is the SAME phase
        re-timed after a HEAD change dropped it for comparability. 121 more tests, and the box
        was shared with the in-tree baseline phase; both push the same way and neither is
        separable from this record. It ran to completion, so it is a real timing, and it
        justified 3600.
      * **1867.6s** (`in_tree_baseline`, launch 13, rc=-15) is the worst phase the record now
        carries, and it is a LOWER BOUND -- SIGTERM mid-suite, twenty-one progress dots, no
        summary line. That is why it may appear here at all: the asymmetry this atom's harness
        enforces (`_ran_to_completion_from`) lets a truncated duration RAISE a floor, because
        the suite provably ran at least that long and up is the safe direction, while refusing
        it as a ratio DENOMINATOR, where it would only overstate. This assertion is a floor.

    THE PAIRING IS THE POINT AND IT HAD TO BE REPAIRED HERE. This constant tracked the worst
    COMPLETED phase while test_the_timeout_clears_the_floor_the_measurement_implies reads the
    worst of ALL phases from the record; once the truncated baseline became the worst, the two
    diverged and a revert to 3600 would have reddened only the record-reading one. Transcribing
    the same phase the floor is taken over restores them as each other's witness.

    MUTATION: set GATE_SUITE_TIMEOUT_SECONDS back to 3600 (the bound derived against the 1784.6s
    phase) and this fails, because 3600 < 2 * 1867.6. It fails TOGETHER WITH
    test_the_timeout_clears_the_floor_the_measurement_implies, which reads the record itself --
    that pairing is what makes this transcription a second witness rather than a copy of the
    claim, and it is why the constant here must be moved by hand every time the bound moves."""
    # Measured on the subject the gate ACTUALLY runs -- a cold throwaway checkout. Cold is the
    # only side left to bound on since reuse was eliminated: every cycle extracts HEAD fresh, and
    # the timeout now BLOCKS publishing rather than degrading the gate. The worst measured phase
    # is a LOWER bound on its own runtime (rc=-15), which is admissible for a floor and for
    # nothing else -- see the docstring.
    # RE-MEASURED TWICE ON 2026-08-21, 1867.6 -> 38.6 -> 1674.0, and the middle value was wrong
    # in the way this whole file is about. 38.6s was a true timing of `publish_gate_pytest_argv()`
    # -- a function the gate does not run. The real path is `_scoped_gate_argv()`. 1674.0 is the
    # MAX of 310 completed real gate runs in publish_gate_duration.jsonl (median 1199, p90 1384).
    #
    # 1867.6s was a true measurement of a subject the gate NO LONGER RUNS: the whole tree. The
    # gate now runs `PUBLISH_GATE_SCOPE` -- 1,183 tests verifying the published output, timed on
    # the real argv the same day at 38.6s.
    #
    # Leaving the old figure here would have been worse than stale. This assertion demands
    # `bound > 2 x MEASURED`, so against 1867.6 it FORCES the bound to at least 3735s -- a test
    # whose stated purpose is protecting the bound was the thing ratcheting it upward, and it
    # would have reverted the cap on the next run. That is how a ceiling becomes monotonic: not
    # by anyone deciding to raise it, but by a control measuring a subject that has moved.
    #
    # The 2x factor is unchanged and still right for its stated reason -- a routine timeout is a
    # publish BLOCK, so the bound must clear the healthy case comfortably. Against the real
    # subject, 300s clears 38.6s by 7.7x.
    MEASURED_SUITE_SECONDS = 1674.0
    assert prc.GATE_SUITE_TIMEOUT_SECONDS > MEASURED_SUITE_SECONDS * 2, (
        f"gate timeout {prc.GATE_SUITE_TIMEOUT_SECONDS}s leaves too little headroom over the "
        f"~{MEASURED_SUITE_SECONDS}s the SCOPED gate actually takes; a routine timeout is a "
        "publish BLOCK, so the bound must clear the healthy case comfortably"
    )
    # And the other direction, which never existed before and is the whole point of the cap: the
    # bound may not be raised past what a publish gate can afford. Without this, the assertion
    # above is satisfiable by any large number.
    assert prc.GATE_SUITE_TIMEOUT_SECONDS <= prc.PUBLISH_GATE_CEILING_RATCHET_SECONDS


def test_red_publish_gate_captures_output_rather_than_discarding_it(monkeypatch, tmp_path):
    """The gate must actually CAPTURE pytest's output.

    MUTATION: drop `capture_output=True` from the subprocess.run call and this
    fails -- stdout/stderr go to the daemon's console and are lost."""
    _, _, _, kwargs = _gate_log_text(
        monkeypatch, tmp_path, _FakeCompleted(1, stdout="FAILED tests/a.py::t\n"))
    assert kwargs.get("capture_output") is True, \
        "publish-gate pytest output must be captured, not discarded"
    assert kwargs.get("text") is True, "captured output must be decoded to str"


def test_red_publish_gate_logs_a_tail_even_with_no_summary_line(monkeypatch, tmp_path):
    """Fail-open guard: a red with no FAILED/ERROR summary (collection error,
    internal pytest crash) must STILL log evidence, never a silent red.

    MUTATION: make _log_gate_failure_payload return early when node_ids is
    empty and this fails."""
    _, _, text, _ = _gate_log_text(
        monkeypatch, tmp_path,
        _FakeCompleted(2, stderr="INTERNALERROR> Traceback: conftest import blew up"))
    assert "no FAILED/ERROR summary line found" in text
    assert "conftest import blew up" in text, \
        "a red with no summary line must still carry its output tail"


def test_green_publish_gate_logs_no_failure_payload(monkeypatch, tmp_path):
    """Independence: the payload logger fires ONLY on red (R15 -- a control
    that fires on every run carries no signal).

    MUTATION: call _log_gate_failure_payload unconditionally and this fails."""
    passed, _, text, _ = _gate_log_text(
        monkeypatch, tmp_path, _FakeCompleted(0, stdout="100 passed\n"))
    assert passed is True
    assert "Publish gate RED" not in text
    assert (tmp_path / ".last_tested_hash").read_text().strip() == "deadbeef"


def test_gate_failure_log_tail_is_bounded(monkeypatch, tmp_path):
    """A pathological suite must not balloon the shared log file.

    MUTATION: remove the [-GATE_FAILURE_TAIL_CHARS:] slice and this fails."""
    huge = "x" * 200_000 + "\nFAILED tests/a.py::t\n"
    _, _, text, _ = _gate_log_text(monkeypatch, tmp_path, _FakeCompleted(1, stdout=huge))
    assert len(text) < prc.GATE_FAILURE_TAIL_CHARS * 3, \
        "the red-gate tail must be bounded, not the whole suite output"
    assert "FAILED tests/a.py::t" in text, "the summary line must survive the bound"


# --- The commit-timeout crash that wedged publishing (2026-08-03) -------------
# git_commit_push runs the FULL pre-commit hook chain, whose site_lane_gate branch
# alone measured 27.3s against a 30s subprocess cap. The TimeoutExpired was UNCAUGHT:
# it propagated out of _process(), so process_run_complete exited rc=1 having logged
# NEITHER "Nothing to commit or commit failed" NOR "Done", and the wedge detector
# recorded a "test_regression" that was nothing of the sort. R15 -- these prove the
# catch is real, not asserted.

#: What `surgical_land.run_gate` raises when the pre-commit hook chain outruns its own deadline
#: and is KILLED. Copied from `run_gate`'s fail-closed branch: an unavailable gate is a failed
#: gate, so the tool converts the kill into a refusal -- and the publisher has to read the kill
#: back out of the text, because a killed child has no verdict and the reader must not be sent to
#: the tests. `test_the_publisher_classifies_the_tools_real_refusals.py` drives the real tool and
#: is what keeps this string honest.
GATE_KILLED_REFUSAL = (
    "the gate could not be EXECUTED (Command '['sh', 'tools/git-hooks/pre-commit']' timed out "
    "after 3600 seconds) -- refusing rather than landing ungated.")


def _commit_push_with(monkeypatch, run_side_effect, land=None):
    """Drive git_commit_push with a stubbed subprocess.run and a no-op tree_lock.

    `land`, when given, is the refusal text the surgical landing answers with -- the publish
    COMMIT is a landing now (2026-09-08), so that is where a commit-side failure enters.
    """
    import contextlib
    monkeypatch.setattr(prc, "tree_lock", lambda: contextlib.nullcontext())
    monkeypatch.setattr(prc.subprocess, "run", run_side_effect)
    if land is not None:
        monkeypatch.setattr(
            prc, "_land_publish_commit",
            lambda pathspec, msg, git_hash: {"sha": "", "refusal": land, "lost": []})
    return prc.git_commit_push("abc1234", 1_500_000)


def test_commit_timeout_is_caught_and_does_not_crash_the_publish(monkeypatch, tmp_path):
    """THE REGRESSION. A slow hook chain must degrade to "retry next cycle".

    MUTATION: delete the `_gate_was_killed` branch's `return` (let the killed gate fall through
    to the generic refusal) and this still returns False -- so the assertion below is paired with
    `test_commit_timeout_says_so_in_the_log`, which is the leg that fires. The crash this test
    was written for (2026-08-03, an uncaught `TimeoutExpired` out of `git commit`) is now
    structurally impossible: `_land_publish_commit` turns EVERY failure into a value.
    """
    assert _commit_push_with(monkeypatch, lambda argv, **kw: _FakeCompleted(0),
                             land=GATE_KILLED_REFUSAL) is False, \
        "a killed gate must report failure, not crash the publish"


def test_commit_timeout_says_so_in_the_log(monkeypatch, tmp_path):
    """The crash was hard to diagnose because it logged NOTHING between the
    'Committing and pushing' line and the process's death -- the failure has to
    name itself, or the next reader blames the test suite again (R9: evidence
    before narrative).

    MUTATION: make `_gate_was_killed` return False and this fails -- the kill is narrated as an
    ordinary gate refusal, which sends the reader to a test suite that returned no verdict.
    """
    written = []
    monkeypatch.setattr(prc, "log", lambda m: written.append(m))

    assert _commit_push_with(monkeypatch, lambda argv, **kw: _FakeCompleted(0),
                             land=GATE_KILLED_REFUSAL) is False
    joined = "\n".join(written)
    assert "KILLED" in joined, joined
    assert "hook chain" in joined, "the log must point at the hook chain, not the run"
    assert "no test" in joined.lower(), (
        "a killed gate returned NO verdict, and the log has to say so or the reader spends the "
        "next hour on the test suite")


def test_commit_timeout_budget_fits_inside_the_workers_own_cap():
    """A commit cap larger than background_worker's 900s cap on the whole process
    would just move the kill one level up and lose the explaining log line.

    MUTATION: set GIT_COMMIT_HOOK_TIMEOUT_SECONDS above the worker's timeout and
    this fails.
    """
    import re
    from pathlib import Path as _Path
    worker = _Path(prc.__file__).parent / "background_worker.py"
    assert worker.exists(), "background_worker.py is the caller whose cap this must fit"
    src = worker.read_text()
    # The cap that actually applies: the one on the subprocess.run that INVOKES
    # process_run_complete inside process_leftover_run_markers -- not, say,
    # run_ollama_task's unrelated timeout (which this test caught on its first run).
    sweep = src[src.index("def process_leftover_run_markers"):]
    sweep = sweep[:sweep.index("\ndef ", 1)]
    caps = [int(m) for m in re.findall(r"timeout=(\d+)", sweep)]
    assert caps, "could not find the marker sweep's own subprocess timeout"
    assert prc.GIT_COMMIT_HOOK_TIMEOUT_SECONDS < min(caps), (
        "commit cap {}s must fit inside the sweep's own {}s cap on the whole "
        "process".format(prc.GIT_COMMIT_HOOK_TIMEOUT_SECONDS, min(caps)))


def test_the_kills_diagnostic_survives_the_kill_only_when_the_hooks_are_unbuffered():
    """THE REAL-PLATFORM PROOF, not a stub: does a hook's progress line actually reach the
    parent when the hook is killed mid-run?

    Seven commit timeouts have logged "hook output: nothing captured before the kill" and
    named the chain instead of the link (sim-runner-log.md, 2026-08-13 01:30 UTC). The
    capture was never the problem -- python block-buffers stdout into a pipe, so each hook's
    progress died in its own userspace buffer, and the promised "names the SLOW hook" tail
    could not exist on any non-tty run, which is every autonomous run.

    ANTI-TAUTOLOGY (R15): this drives a real child through real buffering rather than
    asserting against a mock's stdout attribute -- a mock would pass either way, which is
    precisely why nothing caught this. The control's subject is the platform.
    """
    import subprocess as _sp
    child = [sys.executable, "-c",
             "print('HOOK: pre_commit_test_gate starting'); import time; time.sleep(60)"]

    def _captured(env):
        try:
            _sp.run(child, capture_output=True, text=True, timeout=3.0, env=env)
        except _sp.TimeoutExpired as exc:
            return prc.stderr_tail(exc.stderr) or prc.stderr_tail(exc.stdout)
        raise AssertionError("the child was supposed to outlive the deadline")

    with_env = _captured(prc._commit_hook_env())
    assert "pre_commit_test_gate starting" in with_env, (
        "the hook's own progress line must reach the parent before the kill -- this is the "
        "diagnostic the timeout branch promises; got {!r}".format(with_env))

    without_env = _captured(None)
    if without_env:
        pytest.skip("this platform no longer block-buffers a piped child's stdout; the "
                    "unbuffered env is then belt-and-braces rather than the fix")


def test_the_commit_runs_its_hook_chain_unbuffered(monkeypatch):
    """THE WIRING. The env above only helps if `git commit` is actually given it -- git
    passes its own environment to every hook, so this one call reaches the whole chain.

    THE SUBJECT IS THE LIVENESS COMMIT NOW (2026-09-08). The content publish is a surgical
    landing, whose gate is a `sh tools/git-hooks/pre-commit` this module does not build the
    environment for; `_commit_and_push_paths` is the `git commit` that remains, it runs the same
    chain, and it is the one that can still be killed blind. Driving this against the content
    path after the route change would have asserted about a call that no longer happens.

    MUTATION: drop `env=_commit_hook_env()` from the `git commit` subprocess.run in
    `_commit_and_push_paths` and this fails, restoring the blind kill.
    """
    seen = {}
    target = Path(prc.PROJECT_DIR) / "site" / "data" / "publish_provenance.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{}")
    monkeypatch.setattr(prc, "_provenance_is_publishable", lambda *a, **k: True)
    monkeypatch.setattr(prc, "_git_add_or_refuse", lambda *a, **k: True)

    def _run(argv, **kw):
        if argv[:2] == ["git", "commit"]:
            seen["env"] = kw.get("env")
        return _FakeCompleted(0)

    monkeypatch.setattr(prc.subprocess, "run", _run)
    prc._commit_and_push_paths([str(target)], "msg", label="Provenance banner",
                               git_hash="abc1234")

    env = seen.get("env")
    assert env is not None, "`git commit` must be given an explicit environment"
    assert env.get(prc.GIT_COMMIT_HOOK_ENV_UNBUFFERED) == "1", (
        "the hook chain must run unbuffered or its progress dies with it; got {!r}".format(
            env.get(prc.GIT_COMMIT_HOOK_ENV_UNBUFFERED)))
    assert "PATH" in env, "the inherited environment must be preserved, not replaced"
    # The builder must never write through to the process it is called from: a publish cycle
    # runs other children (the gate suite among them) whose buffering is not ours to change.
    before = dict(os.environ)
    prc._commit_hook_env()
    assert dict(os.environ) == before, "_commit_hook_env must not mutate os.environ"


def test_commit_timeout_has_real_headroom_over_the_hook_chain():
    """A CONTROL THAT COULD NOT FAIL, REPLACED (2026-08-25).

    This asserted headroom over `measured_hook_chain_seconds = 30`, a figure measured on
    2026-08-03 and hard-coded with its date in a comment. Two things then happened at once: the
    suite grew, and this test kept passing -- 600 is twenty times 30, so the margin looked
    enormous while the real chain crossed 600s and killed TWELVE CONSECUTIVE PUBLISH COMMITS
    across a 12.2-hour outage. The control that exists to stop suite growth re-creating the wedge
    watched it happen and stayed green, because it graded against a number that had stopped
    moving.

    AND THEN BOTH HALVES GRADED THE WRONG SERIES (2026-09-04, the second incident). They were
    keyed to `publish_gate_duration.jsonl` -- the publisher's OWN scoped gate, a different suite
    run under a different deadline (3800s). That was a fair stand-in in August, when the two moved
    together. On 2026-08-31 the hook chain fell 5.4x and the gate did not, and nothing noticed,
    because the ledger built for this deadline on 2026-08-25 was read by no control. The stand-in
    then demanded 894s of an 880s deadline and refused every commit in the tree for ~9 hours --
    grading a number that nothing here bounds. BOTH HALVES NOW READ THE HOOK CHAIN'S OWN LEDGER.

    Two halves, and they fail differently:
      * the COMMITTED half runs everywhere, including a fresh clone and the gate's own HEAD
        checkout, against `MEASURED_COMMIT_HOOK_CHAIN_SECONDS_2026_09_17` -- whose date is in its
        NAME, so a stale measurement is visible in every diff rather than in a comment nobody
        re-reads;
      * the LIVE half runs where there is hook history, against the worst of the last twenty
        recorded chains, so it grows exactly as the chain does.

    MUTATION (must fire): drop the deadline to 150 -- proven in the test below, which also
    records why 600 no longer fires it and why that is the correction, not a loss of teeth.
    """
    assert prc.GIT_COMMIT_HOOK_TIMEOUT_SECONDS >= (
        prc.COMMIT_DEADLINE_HEADROOM * prc.MEASURED_COMMIT_HOOK_CHAIN_SECONDS_2026_09_17), (
        "the commit deadline has under {:.0%} headroom over the last measured hook chain "
        "({}s)".format(prc.COMMIT_DEADLINE_HEADROOM - 1,
                       prc.MEASURED_COMMIT_HOOK_CHAIN_SECONDS_2026_09_17))


#: How many rows the live half grades. ONE NAME, because the transition rule below has to demand
#: the same size window it would be replacing -- two spellings of "twenty" is how a rule that says
#: "a full window" comes to mean "most of a window" without anyone deciding it.
HOOK_CHAIN_WINDOW_ROWS = 20


def _recent_hook_chain_seconds(series=None):
    """The last twenty pre-commit HOOK CHAIN costs this machine actually recorded, PER CHAIN.

    ONE READER, shared by the live half of the headroom control and by the R15 test that proves
    that half can red. Two copies of this window would let the control and its own teeth grade
    different data, which is the exact class of defect being repaired here.

    ONLY ROWS THE DEADLINE COULD HAVE BOUND, and that clause is the 2026-09-16 repair.
    `GIT_COMMIT_HOOK_TIMEOUT_SECONDS` is the `timeout=` on ONE `git commit` subprocess. Since
    2026-09-08 the CONTENT path lands through `surgical_land.land(attempts=PUBLISH_LAND_ATTEMPTS)`,
    which that constant does not bound and which RE-GATES when it loses the compare-and-swap -- so
    one of its rows can hold two full chains. `2c89bd534` recorded 1381.52s that way (the
    publisher's own record: *"lost the race to another writer on all 2 attempt(s)"*), this control
    read it as a single chain costing 1382s, and 1.25 * 1382 = 1727 against a deadline that
    `test_the_deadline_leaves_room_for_the_publish_path_after_the_gate` caps at 900. No deadline
    satisfied both controls; every commit in the tree was refused by an empty intersection.

    THE DISCRIMINATOR IS ALREADY ON THE ROW, so nothing was added to the schema. A run that
    exceeded `ceiling_seconds` AND returned a verdict cannot have been bounded by that ceiling: a
    bounded chain that exceeds it is KILLED and recorded as `outcome: timeout`, which is why that
    label exists. So `duration > ceiling and outcome != "timeout"` is a row that proves, from its
    own fields, that it is not a measurement of the thing this deadline bounds -- and grading the
    deadline against it is the *"a deadline over here against a measurement of something over
    there"* defect this control already carries a scar from.

    THE DIRECTION IS CONSERVATIVE, which is what a headroom control needs. A multi-chain row whose
    TOTAL still fits under the ceiling is kept and read as one chain -- i.e. over-reported -- so
    this can only ever demand more headroom than reality, never less.

    AND SINCE 2026-09-17 A ROW CAN STATE ITS OWN UNIT, which is the repair one notch below that
    conservatism. `chains` is written by `_record_commit_hook_duration` and holds the divisor the
    producer already applied, so a STATED row's `duration_seconds` IS the per-chain cost and must
    not be divided again here. A row with no `chains` key, or a null one, is UNKNOWN-UNIT: it may
    be a total over any number of chains, so it is an UPPER BOUND on the per-chain cost and never
    a measurement of it. `max` over a mixture of measurements and upper bounds is an upper bound,
    which is sound for the headroom assert and unfair to the staleness one -- `666.95s`, two
    chains of ~333s with no count on the row, is what refused every commit in the tree on
    2026-09-16 while missing the staleness bar by seven seconds.

    THE TRANSITION RULE IS "A FULL WINDOW OR NOTHING", and it exists because the obvious rule is
    a sample-size collapse. `max` is monotone in the sample: any subset's worst is <= the whole
    window's worst, so switching to the stated rows can only ever LOWER what this control demands
    -- the fail-open direction. Preferring stated rows the moment the first one lands would grade
    an 880s deadline against a ONE-ROW window and call the result a regime. So the stated reading
    engages only when there are `HOOK_CHAIN_WINDOW_ROWS` stated rows to read, and then it reads
    exactly that many: the sample never shrinks at the changeover, and there is no threshold
    between "one row" and "a window" for anyone to pick. Until then the legacy reading stands,
    over-reporting, which is the direction this control has always been safe in.

    The cost of that rule is that `chains` buys nothing for twenty commits, and that is accepted
    rather than worked around. A rule tuned to make today's red go away is a rule keyed to today's
    answer, and this control has been through that once already.

    Skips -- never returns a degenerate window -- when the chain's cost is UNOBSERVED, which is
    not the same as small. Callers get either a real window or no test.
    """
    import json as _json
    from pathlib import Path as _Path

    # THE REAL REPO, not `prc.PROJECT_DIR`: this directory's conftest isolates that to a tmp tree
    # so no test can write the live one. `series` is overridden ONLY by the controls that prove
    # this reader's own arithmetic, which cannot be shown against a live file whose contents are
    # whatever this machine happened to do -- and it stays ONE reader, which is the point.
    series = _Path(series) if series is not None else (
        _Path(__file__).resolve().parents[2] / "docs" / "observability"
        / "commit_hook_duration.jsonl")
    if not series.is_file():
        pytest.skip("no hook-chain history on this tree -- the deadline cannot be graded against "
                    "a machine that has never run it; the committed half still applies")
    rows = []
    stated = []
    for line in series.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = _json.loads(line)
        except ValueError:
            continue
        if not isinstance(row.get("duration_seconds"), (int, float)):
            continue
        duration = float(row["duration_seconds"])
        ceiling = row.get("ceiling_seconds")
        if (isinstance(ceiling, (int, float)) and duration > ceiling
                and row.get("outcome") != "timeout"):
            # NOT BOUNDED BY THIS DEADLINE, proven by the row itself -- see the docstring. Kept as
            # a hole rather than dropped silently, so the skip below can say how many there were.
            rows.append(None)
            continue
        rows.append(duration)
        # THE ROW'S OWN UNIT, and the same predicate the producer writes it under: a bool is an
        # int in Python, and `chains: true` is a broken caller, not a claim of one chain. No
        # division here -- the producer divided before it wrote the row, and dividing again would
        # turn a stated two-chain row into a quarter of what it cost.
        n_chains = row.get("chains")
        if isinstance(n_chains, int) and not isinstance(n_chains, bool) and n_chains > 0:
            stated.append(duration)
    if not rows:
        pytest.skip("the hook-chain history holds no readable duration")
    if len(stated) >= HOOK_CHAIN_WINDOW_ROWS:
        # A FULL WINDOW OF ROWS THAT STATE THEIR UNIT -- see the docstring for why the changeover
        # is all-or-nothing. Every one of these is a per-chain measurement, so there are no holes
        # to carry and nothing below can skip for want of a gradeable row.
        window = stated[-HOOK_CHAIN_WINDOW_ROWS:]
    else:
        window = rows[-HOOK_CHAIN_WINDOW_ROWS:]
    recent = [r for r in window if r is not None]
    if not recent:
        pytest.skip(
            "every one of the last {} rows ran PAST its own ceiling and still returned a verdict, "
            "so not one of them was produced under the deadline this grades -- there is nothing "
            "here that measures a bounded chain. The committed half still applies.".format(
                len(window)))

    # AN EARLY-EXIT ROW IS A LOWER BOUND, NOT A MEASUREMENT, and a window made only of them would
    # make the control vacuously green -- the fail-open that matters here. A hook that refuses
    # BEFORE the test gate returns in about a second; one that actually runs the gate cannot.
    #
    # CUT FROM THE REGIME CONSTANT ON 2026-09-17. This was
    # `MEASURED_COMMIT_HOOK_CHAIN_SECONDS / 4`, and that tie meant a GROWING REGIME WALKED THE
    # DISCRIMINATOR UP THROUGH THE REAL-CHAIN POPULATION: at the 333s re-measurement the derived
    # floor is 83.25s, above the smallest real chain ever recorded (67.44s), and the effect is not
    # a red -- it is the whole live half SKIPPING, in the direction that reads as health. The two
    # uses pull opposite ways and one number could not serve both, which is why the re-measurement
    # could not safely be taken until they were separated. See
    # `REAL_CHAIN_FLOOR_SECONDS_2026_09_17` for where in the 42.7x empty band it sits and why.
    floor_of_a_real_chain = prc.REAL_CHAIN_FLOOR_SECONDS_2026_09_17
    if max(recent) < floor_of_a_real_chain:
        pytest.skip(
            "every one of the last {} commits short-circuited before the test gate (worst {:.1f}s "
            "against a real chain's {:.0f}s floor), so this machine's chain cost is UNOBSERVED in "
            "this window -- not fast. The committed half still applies.".format(
                len(recent), max(recent), floor_of_a_real_chain))
    return recent


def test_the_deadline_has_headroom_over_what_THIS_MACHINE_actually_costs_today():
    """The live half. `commit_hook_duration.jsonl` is machine-local and untracked, so it is
    ABSENT in a fresh clone and in the gate's own HEAD checkout -- and that is INAPPLICABLE, not
    unavailable. A tree with no hook history cannot be graded against a machine it has never run
    on, and failing closed there would make a first commit impossible. Where the history exists,
    this is the half with teeth: it grows as the chain grows.

    THE SERIES THIS READS IS THE WHOLE POINT (repointed 2026-09-04). It used to read
    `publish_gate_duration.jsonl`, which records the publisher's OWN scoped gate under its OWN
    3800s deadline. `prc.GIT_COMMIT_HOOK_TIMEOUT_SECONDS` bounds neither of those things: it
    bounds the pre-commit hook chain inside `git commit`. Before dividing or comparing two
    numbers, say what each one counts -- this assert compared a deadline over here against a
    measurement of something over there, was right for a month while the two happened to move
    together, and refused every commit in the tree for ~9 hours when they stopped.
    """
    recent = _recent_hook_chain_seconds()
    worst = max(recent)

    assert prc.GIT_COMMIT_HOOK_TIMEOUT_SECONDS >= prc.COMMIT_DEADLINE_HEADROOM * worst, (
        "the commit deadline is {}s against a worst recent HOOK CHAIN of {:.0f}s -- under "
        "{:.0%} headroom, which on 2026-08-25 meant every publish commit died on machine load. "
        "Recent: {}".format(prc.GIT_COMMIT_HOOK_TIMEOUT_SECONDS, worst,
                            prc.COMMIT_DEADLINE_HEADROOM - 1, [round(r) for r in recent[-5:]]))
    # STALENESS, KEYED TO THE DEADLINE'S OWN SCALE, NOT TO A TIGHT MULTIPLE OF THE MEASUREMENT.
    # The obvious form -- `worst <= 1.6 * MEASURED` -- is what this control used to carry, and on
    # this series it would be the tighter of the two asserts and the one that reds: the chain has
    # a PROVEN 5.4x regime step in it (2026-08-31), so a return to the old regime would red the
    # whole tree to report that a comment needs re-dating. That is the shape that caused the
    # outage this control is being repaired from. The committed half only has to be a fair
    # stand-in FOR GRADING THIS DEADLINE, so it goes stale when the live worst gets close to the
    # deadline while the committed figure still says there is room.
    assert worst <= 0.75 * prc.GIT_COMMIT_HOOK_TIMEOUT_SECONDS, (
        "the hook chain now costs {:.0f}s against a {}s deadline and a committed measurement of "
        "{}s -- the committed half of this control has gone stale and must be RE-MEASURED (and "
        "renamed with today's date), or it will keep reporting room that is no longer there"
        .format(worst, prc.GIT_COMMIT_HOOK_TIMEOUT_SECONDS,
                prc.MEASURED_COMMIT_HOOK_CHAIN_SECONDS_2026_09_17))


# --- R10 class closure for the ~4.5h publish wedge: the stub-contract guard -------------------
# (see the fake_completed note at the top of this file for the incident)

def test_fake_completed_models_the_subprocess_return_contract():
    """The shared stub must return what `subprocess.run` actually returns.

    MUTATION: make fake_completed return a bare `MagicMock()` and every assertion here
    fails -- which is the whole point. The wedge happened because nothing checked this.
    """
    text = fake_completed(["git", "status"], text=True)
    assert isinstance(text.stdout, str) and isinstance(text.stderr, str), (
        "text=True promises str; a MagicMock here is the TypeError that wedged the gate"
    )
    raw = fake_completed(["git", "archive", "HEAD"])
    assert isinstance(raw.stdout, bytes) and isinstance(raw.stderr, bytes), (
        "without text=, subprocess.run returns bytes"
    )
    # The specific read that broke: `git rev-parse HEAD` -> written into .git/HEAD.
    sha = fake_completed(["git", "rev-parse", "HEAD"], text=True).stdout.strip()
    assert len(sha) == 40 and all(c in "0123456789abcdef" for c in sha), (
        "rev-parse must answer in the shape of a real SHA, not an empty string -- a "
        "checkout pinned at '' is not a checkout of HEAD"
    )
    assert fake_completed(["git", "commit"], returncode=1, text=True).returncode == 1


def test_every_subprocess_stub_here_models_the_return_contract():
    """No stub in this file may build its own bare MagicMock result.

    This is the class fix, not the instance fix (R10): the three tests that died were
    only the stubs that happened to be on the new code path, and the next one is
    whichever stub a future production read reaches first. Any `fake_*` helper that
    mocks a subprocess result must go through fake_completed, which is contract-checked
    above.

    MUTATION: restore any of the converted stubs to `m = MagicMock(); m.returncode = 0`
    and this fails, naming it.
    """
    import ast

    tree = ast.parse(Path(__file__).read_text())
    offenders = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.name.startswith("fake_") or node.name == "fake_completed":
            continue
        called = {
            c.func.id for c in ast.walk(node)
            if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
        }
        if "MagicMock" in called and "fake_completed" not in called:
            offenders.append("%s (line %d)" % (node.name, node.lineno))

    assert not offenders, (
        "these subprocess stubs build a bare MagicMock instead of using fake_completed, "
        "so their .stdout is not the str/bytes subprocess.run promises: " + ", ".join(offenders)
    )


# ---------------------------------------------------------------------------------------------
# THE REPAIR LANDS BEFORE THE GATE (2026-08-12)
#
# WORKER_FINDING_A_REPAIR_DOWNSTREAM_OF_ITS_OWN_GATE_CANNOT_LAND_2026-08-10: the self-healing
# repair wrote correct bytes every cycle and logged "Committed with this run" 81 times running,
# and was committed by none of them -- the publish path commits only after a GREEN gate, and the
# staleness is what reds the gate. ORDER is the whole finding, so order is what these pin.
# ---------------------------------------------------------------------------------------------

def _repair_harness(monkeypatch, tmp_path, repaired, land):
    """Drive run_fast_tests with the repair, the landing and the gate all recording their turn."""
    import background.derived_artefact_register as dar
    from tools import surgical_land

    events = []
    monkeypatch.setattr(prc, "LAST_TESTED_HASH_FILE", tmp_path / "no-such-stamp")

    @contextlib.contextmanager
    def fake_checkout():
        yield tmp_path

    def fake_repair_from(source_root, write_root=None):
        events.append("repair")
        return {"repaired": list(repaired), "converged": True, "passes": 1, "still_stale": []}

    def fake_land(root, paths, message, *a, **kw):
        events.append(("land", list(paths)))
        return land(root, paths, message)

    monkeypatch.setattr(prc, "_head_checkout", fake_checkout)
    monkeypatch.setattr(dar, "repair_from", fake_repair_from)
    monkeypatch.setattr(surgical_land, "land", fake_land)
    monkeypatch.setattr(prc, "_run_gate_in", lambda *a, **kw: (events.append("gate"), (True, False))[1])
    return events


def test_a_repaired_projection_is_LANDED_and_it_lands_BEFORE_the_gate(monkeypatch, tmp_path):
    """THE NAMED DEFECT, in the only dimension it lived in: WHEN the repair is committed.

    MUTATION: delete the `_land_repaired_artefacts(res["repaired"])` call in
    `_repair_derived_artefacts_in` and this fails -- no "land" event, and the gate runs on the
    unrepaired tree exactly as it did for 81 cycles.
    """
    events = _repair_harness(
        monkeypatch, tmp_path,
        repaired=["docs/design/FORWARD_ATTACHMENT_LEDGER.md"],
        land=lambda root, paths, message: "abc123def456",
    )
    assert prc.run_fast_tests("deadbeef") == (True, False)
    assert events == ["repair", ("land", ["docs/design/FORWARD_ATTACHMENT_LEDGER.md"]), "gate"], (
        "the repair must be COMMITTED before the gate whose red it fixes is run; a landing that "
        "happens after the gate is the deadlock this closes")


def test_nothing_repaired_lands_NOTHING(monkeypatch, tmp_path):
    """Vacuity guard in the other direction: a quiet cycle must not manufacture a commit."""
    events = _repair_harness(
        monkeypatch, tmp_path, repaired=[],
        land=lambda root, paths, message: pytest.fail("landed with nothing repaired"),
    )
    assert prc.run_fast_tests("deadbeef") == (True, False)
    assert events == ["repair", "gate"]


def test_a_REFUSED_landing_leaves_the_cycle_alive_and_says_which_kind_of_red_it_is(
        monkeypatch, tmp_path, caplog):
    """The landing is GATED, so it can refuse -- and a refusal must not be able to stop publishing.

    It also must not read as "the repair worked": a refusal means something OTHER than the
    staleness is red, and the log line has to say so or the next reader repeats the diagnosis.
    """
    from tools import surgical_land

    def refuse(root, paths, message):
        raise surgical_land.LandingRefused("GATE RED on the resulting tree (rc=1)")

    events = _repair_harness(monkeypatch, tmp_path,
                             repaired=["docs/design/FORWARD_ATTACHMENT_LEDGER.md"], land=refuse)
    logged = []
    monkeypatch.setattr(prc, "log", lambda msg, *a, **kw: logged.append(str(msg)))

    assert prc.run_fast_tests("deadbeef") == (True, False)
    assert events[-1] == "gate", "a refused landing must not skip the gate"
    assert any("NOT landed" in m and "not the only thing red" in m for m in logged), logged


def test_an_UNEXPECTED_landing_failure_is_non_fatal(monkeypatch, tmp_path):
    """FAIL-OPEN, same direction as the repair itself: a publish cycle never dies over a commit."""
    def explode(root, paths, message):
        raise RuntimeError("git went missing")

    events = _repair_harness(monkeypatch, tmp_path,
                             repaired=["docs/design/FORWARD_ATTACHMENT_LEDGER.md"], land=explode)
    monkeypatch.setattr(prc, "log", lambda msg, *a, **kw: None)
    assert prc.run_fast_tests("deadbeef") == (True, False)
    assert events[-1] == "gate"


# ── THE EIGHTEEN-HOUR PUBLISH FREEZE (2026-08-13) ────────────────────────────────────────────
#
# Content last reached origin at 2026-08-12 21:28Z. Every publish from 22:29Z on died with
# `git commit` exceeding its hook deadline -- twenty-one consecutive times -- while a
# `chore(liveness)` heartbeat kept landing on origin every thirty minutes, so from outside the
# machine looked healthy and the figures were a day old. Three defects, one test each below.

def _outcome_of(monkeypatch, tmp_path, *, commit):
    """Drive git_commit_push with the landing answering `commit()`, and return the outcome.

    `commit()` returns the REFUSAL TEXT the surgical landing raises. The publish commit stopped
    being a `git commit` subprocess on 2026-09-08; the four outcomes below are unchanged, but the
    observation each one is decided from is now a sentence from `surgical_land` rather than a
    return code and a stream.
    """
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(prc, "tree_lock", lambda *a, **k: contextlib.nullcontext())
    monkeypatch.setattr(prc, "_provenance_is_publishable", lambda *a, **k: True)
    monkeypatch.setattr(prc, "_push_due", lambda: False)  # stop after the commit
    monkeypatch.setattr(prc.subprocess, "run",
                        lambda cmd, **kw: types.SimpleNamespace(
                            returncode=0, stdout="", stderr=""))
    monkeypatch.setattr(
        prc, "_land_publish_commit",
        lambda pathspec, msg, git_hash: {"sha": "", "refusal": commit(), "lost": []})

    outcome = {}
    prc.git_commit_push("abc1234", 1000.0, outcome=outcome)
    return outcome.get("reason")


def test_a_commit_timeout_is_not_recorded_as_nothing_to_commit(tmp_path, monkeypatch):
    """The distinction the whole freeze turned on. `git_commit_push` returns False for six
    different things; two mean 'nothing to publish' and four mean 'the publish FAILED'."""
    def timeout():
        return GATE_KILLED_REFUSAL

    def nothing_changed():
        # `surgical_land._land_once`'s own words. The no-op is decided by comparing the resulting
        # TREE with HEAD's, which is a strictly better discriminator than the sentence git used
        # to print -- but it is still a sentence this classifier has to recognise.
        return ("the named paths are already at HEAD -- the resulting tree is identical, so "
                "there is nothing to land. (If you expected a change, check the pathspec.)")

    def hook_refusal():
        return ("GATE RED on the resulting tree (rc=1). This is the tree the commit WOULD "
                "create, not the working tree.\n[status-honesty] COMMIT REFUSED.")

    assert _outcome_of(monkeypatch, tmp_path, commit=timeout) == prc.COMMIT_TIMEOUT
    assert _outcome_of(monkeypatch, tmp_path, commit=nothing_changed) == prc.NOTHING_TO_COMMIT
    assert _outcome_of(monkeypatch, tmp_path, commit=hook_refusal) == prc.COMMIT_REFUSED

    # And only the no-op ones let the next identical cycle be skipped.
    assert prc.NOTHING_TO_COMMIT in prc.RETRYABLE_PUBLISH_OUTCOMES
    assert prc.COMMIT_TIMEOUT not in prc.RETRYABLE_PUBLISH_OUTCOMES
    assert prc.COMMIT_REFUSED not in prc.RETRYABLE_PUBLISH_OUTCOMES
    assert prc.PUSH_DID_NOT_REACH_ORIGIN not in prc.RETRYABLE_PUBLISH_OUTCOMES
    assert prc.PROVENANCE_REFUSED not in prc.RETRYABLE_PUBLISH_OUTCOMES


def test_a_failed_publish_does_not_write_the_fingerprint(tmp_path, monkeypatch):
    """MUTATION: make `_write_last_fingerprint` unconditional again and this fails.

    That is the exact line that turned one commit timeout into an eighteen-hour freeze -- the
    timeout branch logs 'Nothing committed; retrying next cycle', and the fingerprint then made
    the change-detection gate skip every identical cycle so the retry never came.
    """
    _full_isolation_setup(tmp_path, monkeypatch)
    marker, _ = make_marker(tmp_path)

    def failed_publish(git_hash, net_margin, outcome=None):
        if outcome is not None:
            outcome["reason"] = prc.COMMIT_TIMEOUT
        return False
    monkeypatch.setattr(prc, "git_commit_push", failed_publish)

    # AND IT MUST SAY SO IN ITS EXIT CODE (2026-08-19). This assertion read `== 0` until the
    # publish outcome started reaching the return value, and that pairing is the whole of
    # EXIT_PUBLISH_DID_NOT_LAND: withholding the fingerprint told the PIPELINE to retry, while
    # exiting 0 told the wedge DETECTOR the cycle had published. One outcome, two consequences,
    # and for months only the first of them existed.
    assert prc.main(str(marker)) == prc.EXIT_PUBLISH_DID_NOT_LAND
    assert not prc.LAST_FINGERPRINT_FILE.exists(), (
        "a publish that FAILED recorded the run as processed -- the next identical cycle will "
        "be skipped by the change-detection gate and the promised retry never happens"
    )


def test_a_successful_publish_still_writes_the_fingerprint(tmp_path, monkeypatch):
    """The other direction, and the reason the fingerprint exists: an identical deterministic
    run must still short-circuit. Narrowing the write must not disable the dedup."""
    _full_isolation_setup(tmp_path, monkeypatch)
    marker, _ = make_marker(tmp_path)

    def ok(git_hash, net_margin, outcome=None):
        if outcome is not None:
            outcome["reason"] = prc.PUBLISHED
        return True
    monkeypatch.setattr(prc, "git_commit_push", ok)

    assert prc.main(str(marker)) == 0
    assert prc.LAST_FINGERPRINT_FILE.exists()


def test_liveness_is_never_easier_to_publish_than_content():
    """The asymmetry that made the freeze INVISIBLE (2026-08-13, director).

    Both paths run the same pre-commit hook chain. While the liveness commit had a larger
    deadline than the content commit, there was a band of hook-chain cost in which the site's
    'I am alive' signal published on schedule and its figures could not publish at all -- which
    is precisely the state the director found by eye after eighteen hours.

    THE TWO DEADLINES STOPPED BEING ONE CONSTANT (2026-09-08). Until then both paths ran `git
    commit` and this asserted they read the same name. The content publish is a surgical landing
    now, so its hook chain runs under `surgical_land.GATE_TIMEOUT_SECONDS` while the liveness
    commit still runs under `GIT_COMMIT_HOOK_TIMEOUT_SECONDS` -- two mechanisms, two numbers, and
    the identity assertion is no longer available. What the identity was PROTECTING still is, and
    it is an inequality: the content path must never die on a hook chain the liveness path
    survives. It may be more generous; it may not be less.

    MUTATION: give the liveness path a deadline above `surgical_land.GATE_TIMEOUT_SECONDS` (or
    drop the landing's own timeout below `GIT_COMMIT_HOOK_TIMEOUT_SECONDS`) and this fails.
    """
    import ast
    import inspect

    from tools import surgical_land

    def commit_timeouts(fn):
        """The `timeout=` on every `git commit` subprocess call in fn's source."""
        tree = ast.parse(inspect.getsource(fn).lstrip())
        found = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            argv = node.args[0] if node.args else None
            # The liveness path writes `["git", "commit", ...] + list(paths)`, so unwrap a
            # concatenation before looking for the literal.
            while isinstance(argv, ast.BinOp) and isinstance(argv.op, ast.Add):
                argv = argv.left
            is_commit = isinstance(argv, ast.List) and any(
                isinstance(e, ast.Constant) and e.value == "commit" for e in argv.elts)
            if not is_commit:
                continue
            for kw in node.keywords:
                if kw.arg == "timeout":
                    found.append(ast.unparse(kw.value))
        return found

    liveness = commit_timeouts(prc._commit_and_push_paths)
    assert liveness, "expected a `git commit` call with a timeout on the liveness path"
    assert set(liveness) == {"GIT_COMMIT_HOOK_TIMEOUT_SECONDS"}, liveness
    # THE CONTENT PATH HAS NO `git commit` AT ALL, and that is the thing to assert rather than
    # assume -- if one came back, its deadline would be unbounded by anything here.
    assert not commit_timeouts(prc.git_commit_push), (
        "the content publish shelled out to `git commit` again -- that is the shared-tree hook "
        "chain this route replaced, and its deadline is outside this comparison")
    assert surgical_land.GATE_TIMEOUT_SECONDS >= prc.GIT_COMMIT_HOOK_TIMEOUT_SECONDS, (
        "the content commit's gate ({}s) dies sooner than the liveness commit's ({}s) -- that is "
        "the band in which the site keeps saying 'I am alive' while its figures cannot publish "
        "at all".format(surgical_land.GATE_TIMEOUT_SECONDS,
                        prc.GIT_COMMIT_HOOK_TIMEOUT_SECONDS))


# ── A TEST PROCESS MAY NOT WRITE THE LIVE sim-runner-log (2026-08-21) ─────────────────────────
#
# THE OBSERVED DEFECT, not a hypothetical: on 2026-08-21 between 20:49 and 20:51 UTC the live
# `docs/observability/sim-runner-log.md` took six `[process_run]` lines naming pytest tmp_path
# roots -- `/tmp/pytest-of-rich/pytest-1512/test_a_root_unavailable_scope_0/checkout-that-never-
# materialised` -- each reading "Publish gate: could NOT materialise a clean HEAD checkout --
# not committing". They were fixture output from `tests/background/test_publish_scope.py`
# driving the real `_run_gate_in`, interleaved with the genuine sim-runner rows.
#
# WHY IT MATTERS MORE THAN AN UNTIDY LOG. That file is the one the PUBLISHING DOWN alarm sends
# a human to: "Check sim-runner-log.md for the publish outcome". During a 26-hour publishing
# outage it was reporting fabricated gate failures that no publish attempt ever suffered. Same
# shape as the fabricated LOOP BROKEN rows in the deadman log (0ab42217a) and the fixture book
# that republished the Proof door's payment gap 2.68x low (the guard's own docstring).
#
# CLOSED AT THE CHOKE POINT (R10): `log()` routes its destination through the SAME
# `live_ledger_guard.guard_live_ledger_write` already wired into `deadmans_switch.log` and
# `suite_duration_watch.record`, so there is one rule for the class rather than a third guard.

# THE REAL WRITER, captured at IMPORT -- before any autouse fixture runs.
#
# `tests/background/conftest.py` defaults every test in this directory to a CAPTURED publisher
# log by replacing `prc.log` outright. That isolation is right for the other ~1800 tests here,
# but it means no test in this directory can exercise the real writer -- and a guard that no
# test can reach is a guard nothing proves (R15: an unavailable check is a FAILED check). The
# two tests below are the ones that must see the genuine function, so they restore it.
_REAL_LOG = prc.log


def test_the_live_sim_runner_log_refuses_a_test_process(monkeypatch):
    """The LIVE path is refused -- and refused for being live, not for being absent."""
    from background.live_ledger_guard import LIVE_RECORD_DIR, LiveLedgerWriteUnderTest

    monkeypatch.setattr(prc, "log", _REAL_LOG)
    live = LIVE_RECORD_DIR / "sim-runner-log.md"
    before = live.read_text() if live.exists() else None
    monkeypatch.setattr(prc, "LOG_FILE", live)
    with pytest.raises(LiveLedgerWriteUnderTest) as exc:
        prc.log("Publish gate: could NOT materialise a clean HEAD checkout -- not committing.")
    # The error names the writer to change, not just the fact of refusal: whoever hits this is
    # reading a traceback from a test they did not write.
    assert "process_run_complete.log" in str(exc.value)
    # And nothing reached the record: the refusal is BEFORE the append, not after it.
    assert (live.read_text() if live.exists() else None) == before


def test_a_redirected_sim_runner_log_still_writes(monkeypatch, tmp_path):
    """NULL CONTROL. The same call, one field changed -- the destination -- must SUCCEED.

    This is what stops the refusal being greened by refusing everything. Refuse-always is the
    cheap way to pass the test above, and it would end the publish path's only diagnostic
    channel: `log()` is what every publish-gate verdict, scope decision and wedge reason is
    written through, and the alarm for a publishing outage points a human straight at it."""
    monkeypatch.setattr(prc, "log", _REAL_LOG)
    dest = tmp_path / "sim-runner-log.md"
    monkeypatch.setattr(prc, "LOG_FILE", dest)
    prc.log("Publish gate scope: 6 publish-path source(s) -> 163 blocking test file(s)")
    assert "163 blocking test file(s)" in dest.read_text()


# ── THE STALE INDEX LOCK THAT REPORTED ITSELF AS A PATHSPEC ERROR (2026-08-25) ───────────────
#
# `.git/index.lock`, 1,274,828 bytes, mtime 6,182s old, with NO git process alive. `git add`
# failed with "Unable to create '.git/index.lock': File exists"; its rc was never read and its
# stderr was captured into a variable nobody looked at. Nothing was staged, so the
# `git commit -- <pathspec>` that followed was handed paths the index had never heard of and
# reported a pathspec error about a file that existed, was not ignored, and was perfectly legal
# to add. Nine consecutive publish cycles failed that way; it took 1h43m to find.

_LOCK_STDERR = "fatal: Unable to create '/home/rich/synthetic-enterprise/.git/index.lock': File exists."


def _publish_with_add(monkeypatch, tmp_path, *, add):
    """Drive the BANNER/HEARTBEAT publish with `git add` answering `add()`.

    Returns (landed?, the git subcommands actually attempted, the lines logged).

    THE SUBJECT MOVED, AND THE CLASS DID NOT (2026-09-08). This drove `git_commit_push` until
    the content publish became a surgical landing -- which has no index and therefore no `git
    add` to leave unchecked. `_commit_and_push_paths` (the banner and liveness-heartbeat
    chokepoint) still stages one, so it is where the unchecked-add class now lives, and it is
    the second instance the R10 census below already names. Driving these against the content
    path after the route change would have been an assertion about a `git add` that no longer
    happens: green for every mutation, including the one it names.
    """
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    target = tmp_path / "site" / "data" / "publish_provenance.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{}")
    monkeypatch.setattr(prc, "tree_lock", lambda *a, **k: contextlib.nullcontext())
    monkeypatch.setattr(prc, "_provenance_is_publishable", lambda *a, **k: True)
    logged = []
    monkeypatch.setattr(prc, "log", lambda msg, *a, **kw: logged.append(str(msg)))
    attempted = []

    def fake_run(cmd, **kwargs):
        attempted.append(list(cmd[:2]))
        if list(cmd[:2]) == ["git", "add"]:
            return add()
        return fake_completed(cmd, **kwargs)
    monkeypatch.setattr(prc.subprocess, "run", fake_run)

    landed = prc._commit_and_push_paths([str(target)], "msg", label="Provenance banner",
                                        git_hash="abc1234")
    return landed, attempted, "\n".join(logged)


def test_a_failed_git_add_refuses_the_cycle_and_names_the_lock(tmp_path, monkeypatch):
    """MUTATION: drop the rc check in `_git_add_or_refuse` (return True unconditionally) and
    all three assertions below fail -- which is exactly the pre-fix mechanism.

    `git add` is ALL-OR-NOTHING, so a failed add can only ever be followed by a MISLEADING
    commit error. The publish must therefore stop AT the add, and say the lock's own words.
    """
    def locked():
        return types.SimpleNamespace(returncode=128, stdout="", stderr=_LOCK_STDERR)

    landed, attempted, logged = _publish_with_add(monkeypatch, tmp_path, add=locked)

    # 1. The publish is refused, and says so -- never a silent False.
    assert landed is False
    # 2. `git commit` is never reached. Pre-fix it WAS, and its pathspec complaint is the
    #    wrong diagnosis that cost 1h43m.
    assert ["git", "commit"] not in attempted, (
        "the publish walked into a commit that cannot work: {}".format(attempted))
    # 3. The lock's own message survives to the log, verbatim -- the one line naming the cause.
    assert "index.lock" in logged and "File exists" in logged
    assert "NOTHING IS STAGED" in logged


def test_a_successful_git_add_still_reaches_the_commit(tmp_path, monkeypatch):
    """NULL CONTROL: the same call, one field changed -- the add's return code -- must PROCEED.

    Refusing every cycle is the cheap way to green the test above, and it would be a total
    publishing outage. This moves the SAMPLE (rc 128 -> 0), not the law."""
    def clean():
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    _landed, attempted, logged = _publish_with_add(monkeypatch, tmp_path, add=clean)

    assert ["git", "commit"] in attempted
    assert "NOTHING IS STAGED" not in logged


def test_no_publish_path_git_add_goes_unchecked(tmp_path, monkeypatch):
    """R10 CLASS CLOSURE, and the reason this is a census rather than a third scenario test.

    The finding named ONE unchecked add (the publish surface). There was a second, identical
    one in `_commit_and_push_paths` that nobody had hit yet -- the banner/heartbeat path --
    and fixing only the caught instance is precisely what makes a class recur. The population
    is open-ended: any `git add` added to this module tomorrow is the next instance, and it
    will again surface as a confusing error from the NEXT command rather than as itself.

    So the subject is the module: every `git add` invocation must be lexically inside
    `_git_add_or_refuse`, which is the one place the return code is read.
    """
    import ast

    source = Path(prc.__file__).read_text()
    tree = ast.parse(source)

    # Which function encloses a given line -- innermost wins, so a nested def is attributed
    # to itself rather than to its parent.
    functions = [node for node in ast.walk(tree)
                 if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]

    def enclosing(lineno):
        holders = [f for f in functions if f.lineno <= lineno <= (f.end_lineno or f.lineno)]
        return min(holders, key=lambda f: (f.end_lineno or f.lineno) - f.lineno).name if holders else "<module>"

    offenders = []
    for node in ast.walk(tree):
        # The argv literal itself: ["git", "add", ...], however it is concatenated afterwards.
        if not isinstance(node, ast.List) or len(node.elts) < 2:
            continue
        head = [e.value for e in node.elts[:2]
                if isinstance(e, ast.Constant) and isinstance(e.value, str)]
        if head != ["git", "add"]:
            continue
        where = enclosing(node.lineno)
        if where != "_git_add_or_refuse":
            offenders.append("{} (line {})".format(where, node.lineno))

    assert not offenders, (
        "these `git add` invocations bypass the one place that reads the return code, so a "
        "lock or a bad path there can only surface as a misleading error from the next "
        "command: {}".format(offenders))
    # And the census is not vacuously green: the checked add really is there.
    assert any(f.name == "_git_add_or_refuse" for f in functions)


def test_the_headroom_control_ACTUALLY_REDS_at_a_deadline_below_the_measured_chain(monkeypatch):
    """R15 ON THE CONTROL ITSELF. The version this replaced passed at 600s against a real chain
    that was exceeding it, so "the control is green" has to be shown to mean something.

    WHY THIS NO LONGER PINS 600 (2026-09-04). It used to assert `600 < floor` against a floor of
    1.25 * 674 = 843. That floor was computed from the publisher's scoped gate, which this
    deadline does not bound; against the chain's own ledger the floor was 1.25 * 134 = 168, and
    600 sat comfortably above it. The honest reading is NOT that the control lost its teeth --
    it is that 600 was never the number that mattered, and pinning it was pinning today's answer.
    600 killed twelve commits in August because the chain then cost 837s; at 134s it would not.
    At the 2026-09-17 re-measurement the floor is 1.25 * 333 = 416 and 600 STILL does not fire it
    -- but the margin has gone from 3.6x to 1.4x in a fortnight, which is the reading a pinned 600
    would have hidden completely and a derived floor states on every run.
    The property is "a deadline under the measured chain reds this control", so that is what is
    asserted, with the deadline DERIVED FROM THE LIVE SERIES rather than transcribed. If the
    chain moves again this control moves with it instead of going quietly wrong.

    Both halves are exercised THROUGH THE REAL CONTROL, not re-implemented here: a hand-built
    comparison would prove that `>=` works, not that the module's assert can fail.
    """
    committed_floor = (prc.COMMIT_DEADLINE_HEADROOM
                       * prc.MEASURED_COMMIT_HOOK_CHAIN_SECONDS_2026_09_17)
    assert prc.GIT_COMMIT_HOOK_TIMEOUT_SECONDS >= committed_floor, (
        "the control is not green as shipped")

    # THE COMMITTED HALF must red when the deadline drops below its floor.
    monkeypatch.setattr(prc, "GIT_COMMIT_HOOK_TIMEOUT_SECONDS", int(committed_floor) - 1)
    with pytest.raises(AssertionError):
        test_commit_timeout_has_real_headroom_over_the_hook_chain()

    # THE LIVE HALF must red at a deadline under the worst chain THIS MACHINE has recorded.
    # Derived, not transcribed -- and skipped rather than faked where there is no history, which
    # is the same "inapplicable, not unavailable" the control itself draws.
    try:
        monkeypatch.setattr(prc, "GIT_COMMIT_HOOK_TIMEOUT_SECONDS", 880)
        test_the_deadline_has_headroom_over_what_THIS_MACHINE_actually_costs_today()
    except pytest.skip.Exception:
        pytest.skip("no gradeable hook history on this tree -- the live half is inapplicable "
                    "here, so its teeth cannot be shown; the committed half above was proven")

    worst = max(_recent_hook_chain_seconds())
    monkeypatch.setattr(prc, "GIT_COMMIT_HOOK_TIMEOUT_SECONDS", int(worst) - 1)
    with pytest.raises(AssertionError):
        test_the_deadline_has_headroom_over_what_THIS_MACHINE_actually_costs_today()


def test_the_hook_chain_duration_is_RECORDED_against_its_own_deadline():
    """THE THING THAT TIMES OUT WAS THE ONE THING UNMEASURED. Twelve consecutive publish failures
    produced no record of how long the chain took -- only that it exceeded a number -- while the
    publisher's SEPARATE gate series reported `band: ok, headroom_ratio: 0.85` against a 3800s
    budget the caller never lets it reach.

    MUTATION (must fire): record against `GATE_SUITE_TIMEOUT_SECONDS`, which is what made the
    existing instrument read healthy through the outage.
    """
    import inspect

    source = inspect.getsource(prc._record_commit_hook_duration)

    assert "GIT_COMMIT_HOOK_TIMEOUT_SECONDS" in source
    assert "GATE_SUITE_TIMEOUT_SECONDS" not in source.split('"""')[-1]
    assert prc.COMMIT_HOOK_DURATION_PATH.name == "commit_hook_duration.jsonl", (
        "the hook chain shares a series with the publisher's own gate -- two different subjects "
        "in one file makes both unreadable"
    )


def test_recording_the_hook_duration_can_NEVER_take_the_publish_down(monkeypatch):
    """An observer that can break the thing it observes is itself a defect -- and this one sits
    directly in the publish path, twice."""
    import background.suite_duration_watch as sdw

    def _boom(*a, **k):
        raise RuntimeError("the recorder is broken")

    monkeypatch.setattr(sdw, "record_gate_run", _boom)
    prc._record_commit_hook_duration(12.0, "abc1234", "pass")  # must not raise


def test_the_commit_call_is_TIMED_on_both_paths():
    """A duration recorded only on success would leave the timeout -- the case that actually
    happened twelve times -- unmeasured, which is the state this repairs.

    MUTATION (must fire): record only after a successful commit.
    """
    import ast

    # The content path's commit is a surgical landing since 2026-09-08, and the duration is
    # recorded where that call is made -- on the refusal branch and the success branch both,
    # with the KILL kept as its own label. Read BOTH functions, because the liveness path still
    # commits directly and still has to be measured.
    #
    # FROM THE MODULE'S TEXT, NOT `inspect.getsource(prc._land_publish_commit)`: this file's
    # autouse `_the_landing_lands` fixture has replaced that attribute with a lambda, and
    # `getsource` would read the FIXTURE and report zero -- a control graded on its own stub.
    module_src = Path(prc.__file__).read_text()
    wanted = {"_land_publish_commit", "_commit_and_push_paths"}
    bodies = [ast.get_source_segment(module_src, node) or ""
              for node in ast.parse(module_src).body
              if isinstance(node, ast.FunctionDef) and node.name in wanted]
    assert len(bodies) == len(wanted), "expected both commit sites; found {}".format(len(bodies))
    source = "\n".join(bodies)

    assert source.count("_record_commit_hook_duration(") >= 2
    assert '"timeout"' in source


# ── A ROW THAT OUTRAN ITS OWN CEILING WAS NOT BOUND BY IT (2026-09-16) ───────────────────────
#
# `GIT_COMMIT_HOOK_TIMEOUT_SECONDS` is the `timeout=` on ONE `git commit`. Since 2026-09-08 the
# CONTENT path lands through `surgical_land.land(attempts=PUBLISH_LAND_ATTEMPTS)`, which it does
# not bound and which RE-GATES when it loses the compare-and-swap: the race is detected after the
# gate has returned a verdict, so a lost attempt ran a full chain and the elapsed time holds every
# one of them. `2c89bd534` recorded 1381.52s that way; the live headroom control read it as ONE
# chain and demanded 1.25 * 1382 = 1727s of a deadline that
# `test_the_deadline_leaves_room_for_the_publish_path_after_the_gate` caps at 900s. The
# intersection of the two controls was EMPTY, and every commit in the tree was refused by it.

def test_a_row_that_outran_its_ceiling_and_still_answered_is_not_graded(tmp_path):
    """THE READ, and the property is the row's own contradiction.

    A bounded chain that exceeds its deadline is KILLED and recorded `timeout`. A row that exceeds
    the ceiling and still reports a verdict therefore proves, from its own fields, that it was not
    produced under that ceiling -- so it is not a measurement of what this deadline bounds.

    MUTATION (must fire): drop the `duration > ceiling` clause and the wedge is restored; drop the
    `outcome != "timeout"` clause and a genuine kill stops being gradeable, which is the case the
    control exists for.
    """
    import json as _json

    n = [0]

    def _series(rows):
        n[0] += 1
        p = tmp_path / "s{}.jsonl".format(n[0])
        p.write_text("\n".join(_json.dumps(r) for r in rows) + "\n")
        return p

    # THE LIVE INSTANCE: 1381.52s against an 880s ceiling, verdict returned. Not our subject.
    wedge = _series([{"duration_seconds": 1381.52, "ceiling_seconds": 880, "outcome": "refused"},
                     {"duration_seconds": 333.22, "ceiling_seconds": 880, "outcome": "pass"}])
    assert _recent_hook_chain_seconds(wedge) == [pytest.approx(333.22)]
    assert prc.GIT_COMMIT_HOOK_TIMEOUT_SECONDS >= (
        prc.COMMIT_DEADLINE_HEADROOM * max(_recent_hook_chain_seconds(wedge))), (
        "the window that wedged the tree grades GREEN once the row that was never bounded by this "
        "deadline stops being read as though it were")

    # A KILL IS STILL THE SUBJECT. The deadline is exactly what ended it, so it must be graded --
    # this is the 2026-08-25 case the whole control exists for and it must never be filtered out.
    killed = _series([{"duration_seconds": 900.0, "ceiling_seconds": 880, "outcome": "timeout"}])
    assert _recent_hook_chain_seconds(killed) == [pytest.approx(900.0)]
    assert prc.GIT_COMMIT_HOOK_TIMEOUT_SECONDS < (
        prc.COMMIT_DEADLINE_HEADROOM * max(_recent_hook_chain_seconds(killed)))

    # A SLOW CHAIN THAT STAYED UNDER ITS CEILING IS STILL GRADED, and still reds at 1.25x.
    slow = _series([{"duration_seconds": 800.0, "ceiling_seconds": 880, "outcome": "pass"}])
    assert _recent_hook_chain_seconds(slow) == [pytest.approx(800.0)]
    assert prc.GIT_COMMIT_HOOK_TIMEOUT_SECONDS < (
        prc.COMMIT_DEADLINE_HEADROOM * max(_recent_hook_chain_seconds(slow))), (
        "the repair is about what a row COUNTS, not about tolerating a slow chain")

    # And a window with nothing gradeable in it SKIPS rather than passing -- an unmeasured
    # deadline is inapplicable, never green.
    with pytest.raises(pytest.skip.Exception):
        _recent_hook_chain_seconds(_series([
            {"duration_seconds": 1381.52, "ceiling_seconds": 880, "outcome": "refused"}]))


# ── ONE NUMBER WAS SERVING TWO USES WITH OPPOSITE GRADIENTS (2026-09-17) ─────────────────────
#
# `floor_of_a_real_chain` was `MEASURED_COMMIT_HOOK_CHAIN_SECONDS / 4`. That constant must RISE
# with the regime (it is the representative per-chain cost the committed half grades against);
# the floor must stay BELOW THE SMALLEST REAL CHAIN (it is the early-exit discriminator, and what
# an early exit costs is a property of the hook refusing, not of the suite growing). Tied
# together, re-dating 134 -> 333 puts the floor at 83.25s -- above the smallest real chain ever
# recorded, 67.44s -- and the live half stops grading rather than going red. That is why the
# staleness refusal spent a fortnight naming a re-measurement that could not safely be taken.

def test_the_early_exit_floor_does_not_MOVE_when_the_regime_constant_does(tmp_path, monkeypatch):
    """THE DECOUPLING, and the defect it names is a discriminator dragged by a constant that has
    no business setting it.

    The property under test is INDEPENDENCE, not today's value: a real chain at the smallest cost
    this machine has ever recorded stays gradeable however far the regime constant moves. Keyed
    that way on purpose -- a control pinned to "the floor is 10" goes red the day the floor is
    honestly re-measured and stays green the day the coupling comes back.

    MUTATION (must fire): restore `floor_of_a_real_chain = prc.MEASURED_...  / 4.0` and the last
    leg reds, because 333/4 = 83.25 > 67.44 and the window stops grading.

    AND MY FIRST DRAFT OF THIS TEST COULD NOT FAIL FOR THAT MUTATION. The coupled floor makes the
    reader SKIP, and a bare call here propagated the skip straight out of the test -- which pytest
    reports in a colour indistinguishable from a pass, and the mutation battery duly recorded
    "8 passed" against the one mutation this control is named for. `_must_grade` below converts
    that skip into the failure it always was. A shared skip silencing a whole leg is the class
    this file has been caught by before; it is cheap to write and invisible to read.
    """
    import json as _json

    smallest_real_chain = 67.44          # the live series' minimum over all 195 rows
    worst_early_exit = 1.58              # and its maximum early exit; nothing lies between them
    n = [0]

    def _series(rows):
        n[0] += 1
        p = tmp_path / "s{}.jsonl".format(n[0])
        p.write_text("\n".join(_json.dumps(r) for r in rows) + "\n")
        return p

    def _must_grade(path, why):
        """Read the window, and make a SKIP a failure. The reader skips when it judges the chain
        cost unobserved, which is right on a real machine and is precisely the defect here."""
        try:
            return _recent_hook_chain_seconds(path)
        except pytest.skip.Exception as exc:
            raise AssertionError("{}: the reader refused to grade it -- {}".format(why, exc))

    real = _series([{"duration_seconds": smallest_real_chain, "ceiling_seconds": 880,
                     "outcome": "pass"}])
    early = _series([{"duration_seconds": worst_early_exit, "ceiling_seconds": 880,
                      "outcome": "refused"}])

    # THE FLOOR IS IN THE EMPTY BAND: it separates the two populations as shipped.
    assert _must_grade(real, "the smallest real chain this machine has recorded") == [
        pytest.approx(smallest_real_chain)]
    with pytest.raises(pytest.skip.Exception):
        _recent_hook_chain_seconds(early)

    # AND IT STAYS THERE WHEN THE REGIME MOVES. Both directions, because a coupling is only
    # visible from the side the regime happens to be travelling -- 134 was yesterday's value, 333
    # is today's, and 900 is what a deadline-sized regime would do to a floor tied to it.
    for regime in (134, 333, 900):
        monkeypatch.setattr(prc, "MEASURED_COMMIT_HOOK_CHAIN_SECONDS_2026_09_17", regime)
        assert _must_grade(
            real,
            "a real chain at this machine's smallest recorded cost, with the regime constant at "
            "{}s -- the discriminator is coupled to it again".format(regime)) == [
                pytest.approx(smallest_real_chain)]
        with pytest.raises(pytest.skip.Exception):
            _recent_hook_chain_seconds(early)


def test_the_early_exit_floor_SEPARATES_the_two_populations_it_was_measured_over():
    """The floor's own placement, against the band it was measured in.

    Not a restatement of its value: this asserts the RELATION to the two populations, so an honest
    re-measurement that moves the floor within the band keeps it green and a floor that leaves the
    band reds whatever it is called.

    MUTATION (must fire): `REAL_CHAIN_FLOOR_SECONDS_2026_09_17 = 70.0` reds the upper leg;
    `= 0.5` reds the lower one.
    """
    floor = prc.REAL_CHAIN_FLOOR_SECONDS_2026_09_17
    assert floor > 1.58, (
        "the floor is at or below the worst early exit this machine has recorded (1.58s), so a "
        "window of nothing but early exits reads as a measurement -- the fail-open this "
        "discriminator exists to close")
    assert floor < 67.44, (
        "the floor is at or above the smallest real chain this machine has recorded (67.44s), so "
        "genuine chains are re-labelled early exits and the live half SKIPS -- silently, and in "
        "the direction that reads as health")


# ── A ROW MAY NOW STATE ITS OWN UNIT, AND A SILENT ONE MUST NOT BE READ AS STATING ONE ───────
#
# `chains` landed at `8cb9a6b96`. The producer divides a multi-chain stopwatch down to a per-chain
# cost and writes the divisor onto the row, so a stated row's `duration_seconds` IS per-chain. A
# row with no count is UNKNOWN-UNIT -- an upper bound, never a measurement. 0 of the 195 rows in
# the live series carry one, which is exactly the state this reader has to survive.

def test_a_window_of_stated_rows_is_preferred_and_a_SILENT_row_is_not_read_as_stating_one(
        tmp_path):
    """The unit split, and the transition rule that stops it collapsing the sample.

    WHAT THIS IS DEFENDING. `max` is monotone in the sample, so preferring the stated rows can
    only ever LOWER what the live half demands -- the fail-open direction. A reader that switched
    on the first stated row would grade an 880s deadline against a ONE-ROW window and call it a
    regime. So the changeover needs a FULL window on the other side of it, and the sample never
    shrinks as it crosses.

    MUTATIONS (must fire):
      * read a silent row as `chains == 1` -> the first leg reds; the split is decorative.
      * drop the threshold to `len(stated) >= 1` -> the second leg reds with a one-row window.
      * divide a stated row by its own `chains` -> the third leg reds; the producer already did.
    """
    import json as _json

    n = [0]

    def _series(rows):
        n[0] += 1
        p = tmp_path / "s{}.jsonl".format(n[0])
        p.write_text("\n".join(_json.dumps(r) for r in rows) + "\n")
        return p

    def _row(duration, **extra):
        r = {"duration_seconds": duration, "ceiling_seconds": 880, "outcome": "pass"}
        r.update(extra)
        return r

    # ONE STATED ROW AMONG SILENT ONES DOES NOT TAKE OVER. The silent 800s row is an upper bound
    # and stays in the reading; a reader that preferred the single stated row would report 250.
    mostly_silent = _series([_row(800.0)] * 5 + [_row(250.0, chains=2)])
    assert max(_recent_hook_chain_seconds(mostly_silent)) == pytest.approx(800.0), (
        "one stated row displaced a window of upper bounds -- that is the sample-size collapse "
        "the transition rule exists to stop")

    # A FULL WINDOW OF STATED ROWS DOES take over, and the silent outlier drops out of it.
    #
    # THE SILENT ROW GOES LAST, and that placement is the whole discrimination of this leg. My
    # first draft put it FIRST, where the twenty-row window drops it under BOTH readings -- the
    # assert passed and proved nothing, which is the tautology this file is named for. Last is
    # also the realistic arrival order: a stale module copy still writing countless rows behind a
    # repaired one.
    full = _series([_row(250.0, chains=1)] * HOOK_CHAIN_WINDOW_ROWS + [_row(800.0)])
    assert _recent_hook_chain_seconds(full) == [pytest.approx(250.0)] * HOOK_CHAIN_WINDOW_ROWS, (
        "a full window of rows that state their unit must be read on its own terms")

    # A STATED ROW IS ALREADY PER-CHAIN. The producer divided before writing; dividing again here
    # would turn a two-chain row costing 250s per chain into 125s and under-report by half.
    two_chain = _series([_row(250.0, chains=2)] * HOOK_CHAIN_WINDOW_ROWS)
    assert max(_recent_hook_chain_seconds(two_chain)) == pytest.approx(250.0), (
        "`chains` is the divisor the producer ALREADY applied, not one for this reader to apply")

    # A BAD COUNT IS SILENCE, not a claim of one chain -- the same predicate the producer writes
    # under, because a bool is an int in Python and `chains: true` is a broken caller.
    bad = _series([_row(250.0, chains=True)] * HOOK_CHAIN_WINDOW_ROWS + [_row(800.0)])
    assert max(_recent_hook_chain_seconds(bad)) == pytest.approx(800.0), (
        "`chains: true` is a broken caller and must read as UNSTATED; treating it as a count "
        "lets a bad caller shrink a real cost")

    # AND THE LIVE STATE IS THE ALL-SILENT ONE: 0 of 195 rows carry a count, so the legacy reading
    # must still work unchanged. A repair that only works once the series has turned over is a
    # repair that is untested for as long as it matters.
    legacy = _series([_row(100.0), _row(333.22)])
    assert _recent_hook_chain_seconds(legacy) == [pytest.approx(100.0), pytest.approx(333.22)]


# ── the two-rooms repair runs at the COMMIT, not a cycle upstream of it ───────────────────
#
# THE DEFECT (2026-09-04, measured). `background_worker` runs
# `staging_two_rooms_repair.observe()` once at the TOP of its cycle, then spends the rest of that
# cycle inside `git_commit_push`, which routinely takes forty-five minutes. `finding_classes
# --check` is a PRE-COMMIT gate, so the TWO ROOMS refusal is evaluated at the FAR END of that
# interval. The window in which a duplicate can wedge a publish is therefore exactly the window in
# which the repairer cannot get another turn.
#
# Live: the sweep sat clean at 12:30; two preregistrations were written into both the root and
# `records/` at 13:01 and 13:06; the commit at the end of that same cycle was refused on them.
# `staging_two_rooms_repair.classify` graded BOTH `redundant` -- the repair was one function call
# away for the whole 45 minutes and structurally could not be reached. Eleven run markers queued
# and the published figures did not move for hours.
#
# MUTATION SENSITIVITY (R15) -- proven by reverting the fix, not asserted:
#   * delete the `_clear_two_rooms_before_commit()` call from `git_commit_push` ->
#     `test_a_duplicate_written_during_the_run_is_gone_by_the_time_the_commit_runs` red.
#   * make `_clear_two_rooms_before_commit` return without calling the repairer ->
#     the same test red.
#   * make `classify` return SAFE unconditionally ->
#     `test_a_conflicting_pair_is_shouted_about_and_never_deleted` red.

class TestTheTwoRoomsRepairRunsAtTheCommitRatherThanACycleEarlier:
    """An ORDERING control: the two orders must produce DIFFERENT answers.

    Asserting only that the duplicate is absent at commit time would pass just as well against a
    fixture that never had a duplicate in it -- the reachability trap this project has entered
    repeatedly. So the no-op leg is asserted too, and it is the leg that carries the evidence:
    it shows the fixture CAN show the duplicate present, which is what makes the first leg mean
    anything.
    """

    DUP = "SEAT_PREREG_A_DUPLICATE_WRITTEN_MID_RUN_2026-09-04.md"

    def _wire(self, tmp_path, monkeypatch, *, root_text, records_text):
        """A publish surface with a staging duplicate already in both rooms.

        Returns (observed, logged). `observed` is appended to by the fake `git commit` and
        records whether the ROOT copy still existed AT COMMIT TIME -- the only instant that
        matters, because that is when the gate reads it.
        """
        from contextlib import nullcontext

        _make_resident(tmp_path / "home", monkeypatch)
        monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)

        # The publish surface, so `_commit_pathspec` is non-empty and the commit is attempted.
        (tmp_path / "docs" / "reports").mkdir(parents=True, exist_ok=True)
        (tmp_path / "docs" / "reports" / "ANNUAL_REPORT.md").write_text("# report\n")
        latest = tmp_path / "docs" / "status" / "LATEST.md"
        latest.parent.mkdir(parents=True, exist_ok=True)
        latest.write_text("# latest\n")
        monkeypatch.setattr(prc, "LATEST_MD", latest)

        # The duplicate, in BOTH rooms. `records/` is the room a preregistration belongs in.
        staging = tmp_path / "docs" / "staging"
        (staging / "records").mkdir(parents=True, exist_ok=True)
        root_copy = staging / self.DUP
        root_copy.write_text(root_text)
        (staging / "records" / self.DUP).write_text(records_text)

        monkeypatch.setattr(prc, "tree_lock", lambda *a, **k: nullcontext())
        monkeypatch.setattr(prc, "_divergence_refusal", lambda *a, **k: None)
        monkeypatch.setattr(prc, "_git_add_or_refuse", lambda *a, **k: True)
        monkeypatch.setattr(prc, "_record_commit_hook_duration", lambda *a, **k: None)
        # Returns the list of reds it parsed -- `[]` is "no test was judged", which is exactly
        # the shape a TWO ROOMS (non-test gate) refusal produces.
        monkeypatch.setattr(prc, "_record_commit_refusal_reds", lambda *a, **k: [])
        monkeypatch.setattr(prc, "publish_cause", MagicMock())

        logged = []
        monkeypatch.setattr(prc, "log", lambda m, *a, **k: logged.append(str(m)))

        observed = []

        def fake_land(pathspec, msg, git_hash):
            # THE OBSERVATION, taken at the instant the real gate would read the tree. The
            # landing IS that instant now: `surgical_land` builds the resulting tree from these
            # working-tree paths and runs the hook chain over it, so a duplicate still on disk
            # here is a duplicate the gate sees.
            observed.append(root_copy.exists())
            return {"sha": "", "lost": [],
                    "refusal": "GATE RED on the resulting tree (rc=1). TWO ROOMS."}

        monkeypatch.setattr(prc, "_land_publish_commit", fake_land)
        monkeypatch.setattr(prc.subprocess, "run",
                            lambda argv, **kw: type(
                                "R", (), {"returncode": 0, "stdout": "", "stderr": ""})())
        return observed, logged

    def test_a_duplicate_written_during_the_run_is_gone_by_the_time_the_commit_runs(
            self, tmp_path, monkeypatch):
        """The fix. The root copy is redundant, so it is cleared BEFORE the gate reads it."""
        observed, logged = self._wire(
            tmp_path, monkeypatch, root_text="prediction\n", records_text="prediction\n")

        prc.git_commit_push("abc1234", 1000.0)

        assert observed == [False], (
            "the redundant root copy was still present when the commit ran, so the TWO ROOMS "
            "gate would have refused this publish -- the repair did not reach the point of use")
        assert any("Cleared 1 redundant staging duplicate" in m for m in logged), logged

    def test_without_the_repair_the_same_fixture_shows_the_duplicate_PRESENT(
            self, tmp_path, monkeypatch):
        """THE DISCRIMINATING LEG. Without this, the test above passes on an empty fixture.

        This is the state the publisher was actually in for the whole of 2026-09-04 12:30-13:19:
        a repairable duplicate, sitting in front of a commit, with nothing between them.
        """
        observed, logged = self._wire(
            tmp_path, monkeypatch, root_text="prediction\n", records_text="prediction\n")
        monkeypatch.setattr(prc, "_clear_two_rooms_before_commit",
                            lambda: {"repaired": [], "conflicts": []})

        prc.git_commit_push("abc1234", 1000.0)

        assert observed == [True], (
            "the duplicate vanished with the repair stubbed out, so something OTHER than "
            "`_clear_two_rooms_before_commit` is clearing it and the control above proves "
            "nothing about this fix")
        assert not any("Cleared" in m for m in logged), logged

    def test_a_conflicting_pair_is_shouted_about_and_never_deleted(self, tmp_path, monkeypatch):
        """Timidity is load-bearing: a root copy carrying text the other room lacks is REPORTED.

        The commit is still refused -- this branch cannot fix itself -- but the log says so
        BEFORE the refusal rather than leaving the reader to infer it from a gate banner.
        """
        observed, logged = self._wire(
            tmp_path, monkeypatch,
            root_text="prediction PLUS a correction the archive never saw\n",
            records_text="prediction\n")

        prc.git_commit_push("abc1234", 1000.0)

        assert observed == [True], "a CONFLICT pair must never be deleted"
        assert any("not safely repairable" in m for m in logged), logged
        assert any(self.DUP in m for m in logged), "the shout must name the file"

    def test_the_repair_never_takes_the_publish_down(self, tmp_path, monkeypatch):
        """A publish must not die of its own housekeeping -- the failure being fixed is a
        REFUSED commit, and a crashed publisher is the worse outage."""
        monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path / "does" / "not" / "exist")
        assert prc._clear_two_rooms_before_commit() == {"repaired": [], "conflicts": []}


def test_the_hook_chain_row_STATES_how_many_chains_its_stopwatch_held(tmp_path, monkeypatch):
    """END TO END, PRODUCER TO ROW -- and the link this pins had NO control until 2026-09-17.

    `_record_commit_hook_duration` computes the chain count, divides by it, and hands it to
    `record_gate_run`. Removing the `chains=` argument from THAT call left every control green:
    the recorder's own tests pass `chains` directly and never exercise this caller, and the two
    headroom controls read `duration_seconds` alone. So the one link that actually carries the
    count to the live series was the one link nothing graded -- the shape CLAUDE.md names, a
    mutation that fires nothing because no control sits on the path.

    WHY THE COUNT AND NOT ONLY THE DIVISION. `2c89bd534` (1381.52s) and `b55667741` (666.95s)
    were each a lost compare-and-swap that re-gated, so the stopwatch held two full chains. The
    first was caught by the ceiling discriminator; the second was 667 < 880 and was read as ONE
    chain, reding the headroom control at `worst <= 0.75 * 880` by seven seconds and refusing
    every ordinary commit in the shared tree. A threshold cannot recover a unit. The producer
    always knew it, and now says it.

    MUTATION (must fire, and did not before this test existed): drop `chains=n_chains` from the
    `record_gate_run` call in `_record_commit_hook_duration`.
    """
    series = tmp_path / "commit_hook_duration.jsonl"
    monkeypatch.setattr(prc, "COMMIT_HOOK_DURATION_PATH", series)

    prc._record_commit_hook_duration(666.95, "b55667741", "refused", chains=2)

    rows = [json.loads(ln) for ln in series.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(rows) == 1, "one call, one row"
    assert rows[0]["chains"] == 2, (
        "the row must STATE the divisor -- without it a reader cannot tell this repaired row "
        "from the nine days of totals behind it, which is how 666.95s read as one chain")
    assert abs(rows[0]["duration_seconds"] - 333.48) < 0.01, (
        "and the duration must be PER CHAIN, or the series holds two units at once")


def test_a_hook_chain_row_with_no_stated_count_is_still_recorded_as_one(tmp_path, monkeypatch):
    """THE DEFAULT PATH KEEPS ITS MEANING, AND THE BROKEN-CALLER PATH IS THE HALF WITH TEETH.

    Every ordinary commit records one chain and says so -- `chains: 1` is a CLAIM, and it is the
    claim that lets a later reader trust the row at face value rather than re-infer the unit.

    THE FALLBACK IS REACHED ONLY BY A BROKEN CALLER, WHICH IS WHY THIS TEST CALLS AS ONE. The
    signature is `chains: int = 1`, so an ordinary call never takes the `else` branch at all --
    a defaulted parameter had made that branch unreachable, and a first draft of this test
    asserted a mutation on it that consequently fired NOTHING. Recorded rather than quietly
    fixed: an unreachable branch and a correct one are the same colour from the outside.

    THE DIRECTION IS THE PRODUCER'S STATED FAIL-SAFE: a count that is not a positive int is
    treated as ONE, so a broken caller OVER-reports the per-chain cost (the direction every
    consumer of this series is already safe in) rather than silently shrinking a real one.

    MUTATION (must fire, both legs): make the fallback `None` instead of 1 -- the `chains=None`
    leg below fails on the row's claim. Divide by the raw `chains` instead of `n_chains` -- the
    same leg dies on a TypeError, which is the crash the guard exists to prevent.
    """
    series = tmp_path / "commit_hook_duration.jsonl"
    monkeypatch.setattr(prc, "COMMIT_HOOK_DURATION_PATH", series)

    prc._record_commit_hook_duration(254.85, "abc1234", "pass")
    row = json.loads(series.read_text(encoding="utf-8").splitlines()[-1])
    assert row["chains"] == 1
    assert abs(row["duration_seconds"] - 254.85) < 0.01, "one chain is not divided"

    # A BROKEN CALLER -- the only way into the fallback. `None`, 0 and a bool each reach it.
    for bad in (None, 0, -1, True):
        prc._record_commit_hook_duration(254.85, "abc1234", "pass", chains=bad)
        row = json.loads(series.read_text(encoding="utf-8").splitlines()[-1])
        assert row["chains"] == 1, (
            "chains={!r} is a caller bug, and the fail-safe is to claim ONE chain and "
            "over-report -- never to divide by it or to go silent".format(bad))
        assert abs(row["duration_seconds"] - 254.85) < 0.01, (
            "chains={!r} must not shrink the recorded cost".format(bad))
