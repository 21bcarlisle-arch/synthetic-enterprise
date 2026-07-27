"""Site-lane pre-commit gate (Campaign A debt E, SITE_TEST_COVERAGE_SEAM_FRAME.md, mechanism B+C).

The gate closes a FAIL-OPEN seam: the publish gate runs `tests/` only, so a red `site/**` test
cannot wedge it and slips onto the director's window. This suite proves the SELECTION logic (B
broad-trigger + C direct-edit mapping) AND -- the R15 requirement -- that the gate can actually
FAIL: a real red site test really BLOCKS the commit, neutering the gate lets it through, a
tests/-only change does NOT false-fire, and a missing node fails closed (never a silent skip-pass).
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GATE_PATH = ROOT / "tools" / "site_lane_gate.py"

spec = importlib.util.spec_from_file_location("site_lane_gate", GATE_PATH)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


# --- B: broad trigger (whole-suite) selection -------------------------------------------------
def test_site_data_change_triggers_the_full_suite():
    assert gate.plan(["site/data/dashboard.json"]) == ("full", None)


def test_site_data_producer_triggers_the_full_suite():
    # tools/generate_*_data.py regenerates a site/data/*.json the doors render.
    assert gate.plan(["tools/generate_proof_data.py"]) == ("full", None)


def test_site_consumed_ledger_triggers_the_full_suite():
    # The exact class that bit this session: a derived value the site RENDERS changing with no
    # site/ file staged (docs/observability/coupled_gap_ledger.json -> Proof-door panel).
    assert gate.plan(["docs/observability/coupled_gap_ledger.json"]) == ("full", None)
    assert "docs/observability/coupled_gap_ledger.json" in gate.SITE_CONSUMED_LEDGERS


def test_decision_log_ledger_triggers_the_full_suite():
    # The decision ledger (docs/observability/decision_log.jsonl) drives the Journey door's
    # Decisions tab via tools/generate_decisions_data.py -- same class as coupled_gap_ledger.json:
    # a derived value the site RENDERS can change with no site/ file staged.
    assert gate.plan(["docs/observability/decision_log.jsonl"]) == ("full", None)
    assert "docs/observability/decision_log.jsonl" in gate.SITE_CONSUMED_LEDGERS


def test_broad_trigger_wins_over_targeted():
    # A change set with BOTH a direct site edit and a broad trigger runs the whole suite.
    assert gate.plan(["site/proof/index.html", "site/data/proof.json"]) == ("full", None)


# --- C: direct-edit changed-file -> sibling test mapping --------------------------------------
def test_direct_site_html_edit_pulls_in_sibling_tests():
    tests = gate.site_tests_for("site/proof/index.html")
    assert "site/proof/test_coupled_gaps_panel.py" in tests
    assert "site/proof/test_proof_door.py" in tests
    assert all(t.startswith("site/proof/test_") for t in tests)


def test_changed_site_test_file_maps_to_itself():
    assert gate.site_tests_for("site/proof/test_proof_door.py") == ["site/proof/test_proof_door.py"]


def test_site_data_json_is_not_a_direct_source_edit():
    # site/data/*.json goes through the BROAD trigger, not the sibling map.
    assert gate.site_tests_for("site/data/proof.json") == []


def test_non_site_file_maps_to_no_site_tests():
    assert gate.site_tests_for("tests/tools/test_site_lane_gate.py") == []
    assert gate.site_tests_for("company/billing/engine.py") == []


def test_direct_edit_only_selects_targeted_not_full():
    mode, targets = gate.plan(["site/proof/index.html"])
    assert mode == "targeted"
    assert "site/proof/test_proof_door.py" in targets


# --- the gate does NOT false-fire on a non-site change ----------------------------------------
def test_tests_only_change_is_skipped():
    assert gate.plan(["tests/background/test_supervisor.py"]) == (None, None)


def test_pure_company_change_is_skipped():
    assert gate.plan(["company/billing/engine.py", "docs/status/LATEST.md"]) == (None, None)


def test_main_skips_and_returns_0_on_non_site_change(monkeypatch):
    monkeypatch.setattr(gate, "staged_files", lambda: ["tests/background/test_supervisor.py"])
    # If it wrongly ran pytest, this would blow up (no such call is set up); assert clean skip.
    called = {"pytest": False}
    monkeypatch.setattr(gate.subprocess, "run",
                        lambda *a, **k: called.__setitem__("pytest", True))
    assert gate.main() == 0
    assert called["pytest"] is False, "a tests/-only change must NOT invoke the site suite"


# --- R15: the gate must be able to FAIL (mutation proof, both directions) ----------------------
def _write_red_test() -> str:
    """A throwaway, node-INDEPENDENT red test file (plain assert) in its own tmpdir -- never under
    the real site/ tree."""
    d = tempfile.mkdtemp(prefix="site_lane_r15_")
    p = Path(d) / "test_r15_probe.py"
    p.write_text("def test_deliberately_red():\n    assert False, 'R15 probe: this MUST block'\n")
    return str(p)


def test_r15_real_red_site_test_BLOCKS_the_commit__and_neutering_lets_it_through(monkeypatch):
    """R15 (CONTROLS_THAT_CANNOT_FAIL): prove the gate is load-bearing in BOTH directions with a
    REAL red test really run through pytest.

    FIRES: a site-touching change whose site tests include a red one -> main() returns 1 (commit
    REFUSED). NEUTERED: make the gate blind to the site change (plan -> skip) and the SAME red test
    is never run -> main() returns 0 (the red slips through) -- proving the trigger detection is
    exactly what stands between a red site test and a clean commit.
    """
    if gate.shutil.which("node") is None:
        # node absent -> main() fails closed before pytest; this direction is covered by the
        # fail-closed test below. Skip so this test only ever measures the red-blocks path.
        import pytest
        pytest.skip("node absent; fail-closed path covered separately")

    red = _write_red_test()
    monkeypatch.setattr(gate, "staged_files", lambda: ["site/proof/index.html"])

    # FIRES: the site lane runs the red test -> blocks.
    monkeypatch.setattr(gate, "plan", lambda files: ("targeted", [red]))
    assert gate.main() == 1, "a real red site test MUST refuse the commit"

    # NEUTERED: gate blind to the site change -> the same red test never runs -> commit passes.
    monkeypatch.setattr(gate, "plan", lambda files: (None, None))
    assert gate.main() == 0, "neutering the trigger must let the red slip -- proving it was load-bearing"


def test_r15_fail_closed_when_node_missing(monkeypatch):
    """R15 FAIL-CLOSED: the .mjs render harnesses SKIP (not fail) when node is absent, so a
    green-with-skips run is a FALSE pass. With a site-touching change and node missing, the gate
    must REFUSE the commit (an unavailable check is a FAILED check) and must NOT reach pytest."""
    monkeypatch.setattr(gate, "staged_files", lambda: ["site/proof/index.html"])
    monkeypatch.setattr(gate.shutil, "which", lambda _name: None)
    reached_pytest = {"yes": False}
    monkeypatch.setattr(gate.subprocess, "run",
                        lambda *a, **k: reached_pytest.__setitem__("yes", True))
    assert gate.main() == 1, "missing node with a site change must fail closed"
    assert reached_pytest["yes"] is False, "must fail closed BEFORE running an unverifiable suite"


def test_r15_fail_closed_does_NOT_fire_when_no_site_change(monkeypatch):
    """The fail-closed node check must itself not false-fire: a non-site change with node missing is
    still a clean skip (the site lane has nothing to guard)."""
    monkeypatch.setattr(gate, "staged_files", lambda: ["company/billing/engine.py"])
    monkeypatch.setattr(gate.shutil, "which", lambda _name: None)
    assert gate.main() == 0


# --- env isolation (same H24 hazard as the tests/ gate) ---------------------------------------
def test_gitless_env_strips_all_GIT_star():
    result = gate._gitless_env({"GIT_DIR": "/x", "GIT_INDEX_FILE": "/y", "PATH": "/bin"})
    assert [k for k in result if k.startswith("GIT_")] == []
    assert result["PATH"] == "/bin"


def test_pytest_subprocess_gets_gitless_env(monkeypatch):
    monkeypatch.setattr(gate, "staged_files", lambda: ["site/data/proof.json"])
    monkeypatch.setattr(gate.shutil, "which", lambda _name: "/usr/bin/node")
    for k in ("GIT_INDEX_FILE", "GIT_DIR", "GIT_WORK_TREE"):
        monkeypatch.setenv(k, "/should/not/leak")
    captured = {}

    class _R:
        returncode = 0

    monkeypatch.setattr(gate.subprocess, "run",
                        lambda cmd, *a, **k: (captured.__setitem__("env", k.get("env")), _R())[1])
    assert gate.main() == 0
    assert [k for k in captured["env"] if k.startswith("GIT_")] == []


# --- R15 mutation proof: the scrub is LOAD-BEARING against real corruption, not just a filter ---
# The two tests above only assert the STRING-FILTERING property (GIT_* keys removed). Per R15
# (CONTROLS_THAT_CANNOT_FAIL) a control is proven only when it is measured against its NAMED
# DEFECT -- here, actual repo corruption. This gap matters MORE on the site lane than on the
# tests/ gate: L2 SITE work commits from LINKED WORKTREES (.claude/worktrees/*, THREE_LANES), so
# the GIT_COMMON_DIR shared-main-repo corruption vector -- the likeliest source of the incident's
# repeated core.bare=true -- is MOST likely to fire through THIS gate. The higher-risk path had
# the weaker proof; this closes that sibling gap (feedback_audit_sibling_half_for_hardened_class).
def _run_git(args, cwd, env):
    return subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True)


def _repo_core_bare(repo, clean_env):
    return _run_git(["config", "--get", "core.bare"], cwd=repo, env=clean_env).stdout.strip()


def _make_isolated_repo(clean_env):
    """A throwaway repo in its own tempdir -- NEVER the real .git -- with one commit and
    core.bare confirmed false."""
    repo = tempfile.mkdtemp(prefix="sitelane_isolated_repo_")
    _run_git(["init", "-q"], cwd=repo, env=clean_env)
    _run_git(["config", "user.email", "sitelane-test@example.invalid"], cwd=repo, env=clean_env)
    _run_git(["config", "user.name", "Site Lane Mutation Test"], cwd=repo, env=clean_env)
    (Path(repo) / "seed.txt").write_text("seed\n")
    _run_git(["add", "seed.txt"], cwd=repo, env=clean_env)
    _run_git(["commit", "-q", "-m", "initial"], cwd=repo, env=clean_env)
    assert _repo_core_bare(repo, clean_env) == "false", "isolated repo fixture must start non-bare"
    return repo


def _make_isolated_repo_with_worktree(clean_env):
    """A throwaway MAIN repo plus a linked worktree -- NEVER the real .git. Returns
    (main_repo, worktree_gitdir, common_dir): the worktree's gitdir lives under
    main/.git/worktrees/<name> and shares main/.git as GIT_COMMON_DIR, exactly the layout the
    site lane's own .claude/worktrees/* commits run under."""
    main_repo = _make_isolated_repo(clean_env)
    wt_path = tempfile.mkdtemp(prefix="sitelane_linked_wt_")
    linked = str(Path(wt_path) / "wt")
    add = _run_git(["worktree", "add", "-q", linked, "-b", "sitelanewtbranch"],
                   cwd=main_repo, env=clean_env)
    assert add.returncode == 0, f"worktree add must succeed to set up the fixture: {add.stderr}"
    worktree_gitdir = str(Path(main_repo) / ".git" / "worktrees" / "wt")
    common_dir = str(Path(main_repo) / ".git")
    assert Path(worktree_gitdir).is_dir(), "linked worktree gitdir must exist under main/.git/worktrees"
    return main_repo, worktree_gitdir, common_dir


def test_r15_scrub_prevents_leaked_worktree_common_dir_corruption__mutation_proof():
    """R15 mutation proof (CONTROLS_THAT_CANNOT_FAIL) for the site lane's own _gitless_env, in BOTH
    directions, against a throwaway repo -- never the real worktree.

    Named defect (H24/H26): during a `git commit` inside a LINKED worktree git sets GIT_COMMON_DIR
    at the MAIN repo's shared .git; an unscrubbed subprocess env lets a stray `git config` write
    land on the SHARED common config (flipping core.bare on the main repo) even though GIT_DIR
    points at the worktree's own private gitdir. Because the site lane commits from linked worktrees,
    this is the vector most likely to fire HERE. The scrub must strip GIT_COMMON_DIR and prevent it.
    """
    clean_env = gate._gitless_env(dict(os.environ))  # our own test process must not leak either
    main_repo, worktree_gitdir, common_dir = _make_isolated_repo_with_worktree(clean_env)
    assert _repo_core_bare(main_repo, clean_env) == "false", "fixture main repo must start non-bare"

    # A neutral cwd that is NOT a git repo -- so the only way `git config` can reach the shared
    # common config is by obeying the leaked worktree-commit env (GIT_DIR + GIT_COMMON_DIR).
    neutral_cwd = tempfile.mkdtemp(prefix="sitelane_wt_neutral_cwd_")

    leaked_env = dict(clean_env)
    leaked_env["GIT_DIR"] = worktree_gitdir            # the worktree's PRIVATE gitdir
    leaked_env["GIT_COMMON_DIR"] = common_dir          # the SHARED main .git (worktree-only var)
    leaked_env["GIT_INDEX_FILE"] = str(Path(worktree_gitdir) / "index")

    # --- WITH the shipped scrub (the real code path) --- must FAIL, shared config untouched ---
    scrubbed_env = gate._gitless_env(leaked_env)
    assert [k for k in scrubbed_env if k.startswith("GIT_")] == [], (
        "the scrub must strip GIT_COMMON_DIR too -- it is a GIT_* var like any other"
    )
    with_scrub = _run_git(["config", "core.bare", "true"], cwd=neutral_cwd, env=scrubbed_env)
    assert with_scrub.returncode != 0, (
        "with GIT_* scrubbed and a non-repo cwd, `git config` must FAIL -- if it succeeds, the "
        "leaked worktree common-dir is still reaching the shared config"
    )
    assert _repo_core_bare(main_repo, clean_env) == "false", (
        "the scrub must leave the shared main config untouched"
    )

    # --- WITHOUT the scrub (the mutation: leaked worktree env passed straight through) --- must
    # REPRODUCE the corruption on the SHARED common config, proving the vector is real. ---
    without_scrub = _run_git(["config", "core.bare", "true"], cwd=neutral_cwd, env=leaked_env)
    assert without_scrub.returncode == 0, (
        "expected the unscrubbed leaked worktree env to let `git config` succeed against the shared "
        "common dir -- if it didn't, this test can't demonstrate the defect"
    )
    assert _repo_core_bare(main_repo, clean_env) == "true", (
        "the unscrubbed leaked GIT_COMMON_DIR must flip core.bare on the SHARED main config -- "
        "proving the site-lane worktree corruption vector is real and the scrub is what prevents it"
    )


# --- reconstruct-from-repo: the committed hook actually invokes the gate -----------------------
def test_committed_hook_invokes_the_site_lane_gate_and_aborts_on_failure():
    hook = (ROOT / "tools" / "git-hooks" / "pre-commit").read_text()
    assert "tools/site_lane_gate.py" in hook, "the pre-commit hook must invoke the site-lane gate"
    # it must abort the commit on a non-zero gate result
    assert "site_lane_gate.py || exit 1" in hook
