"""Pre-commit TEST GATE selection logic (director P0, 2026-07-17).

The gate's job: whenever a CODE/config file is staged, run the safety-control set + the tests for
each changed source file, and ABORT the commit on any failure -- so a red commit is structurally
impossible. These test the SELECTION logic (which tests run for which changeset); the end-to-end
"a commit with a failing test is REFUSED" is proven live against the real git hook.
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GATE_PATH = ROOT / "tools" / "pre_commit_test_gate.py"

spec = importlib.util.spec_from_file_location("pre_commit_test_gate", GATE_PATH)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def test_pure_docs_or_data_commit_runs_NOTHING():
    # A commit touching only status/report/site/observability cannot break a control -> skip.
    assert gate.select_targets(["docs/status/LATEST.md"]) == []
    assert gate.select_targets(["site/data/dashboard.json", "docs/reports/ANNUAL_REPORT.md"]) == []


def test_any_code_change_runs_the_safety_control_set():
    # Even a code change with no dedicated test file still runs the always-on control set.
    targets = gate.select_targets(["saas/some_new_module.py"])
    assert set(gate.CONTROL_TESTS) <= set(targets)


def test_changed_source_pulls_in_its_own_test_file():
    targets = gate.select_targets(["background/supervisor.py"])
    assert "tests/background/test_supervisor.py" in targets
    assert set(gate.CONTROL_TESTS) <= set(targets)


def test_changed_test_file_maps_to_itself():
    assert gate.tests_for("tests/background/test_fork_reconciler.py") == \
        ["tests/background/test_fork_reconciler.py"]


def test_non_python_file_maps_to_no_tests():
    assert gate.tests_for("docs/status/LATEST.md") == []
    assert gate.tests_for("background/process_manifest.yaml") == []


def test_config_change_triggers_the_control_set_even_without_a_mapped_test():
    # A YAML/config under a code prefix still triggers the gate (it can break a control's inputs).
    targets = gate.select_targets(["background/process_manifest.yaml"])
    assert set(gate.CONTROL_TESTS) <= set(targets)


def test_control_test_files_all_exist():
    # The always-on set must reference real files, or the gate silently protects nothing.
    for t in gate.CONTROL_TESTS:
        assert (ROOT / t).exists(), f"control test missing: {t}"


# ── THE LEVEL SURFACE gate (director P0, 2026-07-21): a level/ledger change is DATA but its ──────
# effects must be caught at COMMIT time. R15: these prove the mapping FIRES (a maturity-map or
# ledger change with NO code file runs the level-sensitive set) -- delete the level_surface branch
# in select_targets and both fail.

def test_maturity_map_change_runs_the_level_sensitive_set():
    # A level ratification touches ONLY docs/design/maturity_map.yaml (not under CODE_PREFIXES).
    # It must still run the level-sensitive tests -- the exact hole that wedged the publish gate
    # twice on 2026-07-21 (a level-dependent proof count went stale, uncaught at commit).
    targets = gate.select_targets(["docs/design/maturity_map.yaml"])
    assert targets != []                                        # NOT skipped as "pure data"
    assert set(gate.LEVEL_SENSITIVE_TESTS) <= set(targets)
    assert "tests/tools/test_generate_proof_coupled_gaps.py" in targets  # the test that escaped
    assert "tests/background/test_gate_authorization.py" in targets      # the level-RECORD control


def test_ledger_change_runs_the_level_sensitive_set():
    targets = gate.select_targets(["docs/observability/gate_authorizations.jsonl"])
    assert set(gate.LEVEL_SENSITIVE_TESTS) <= set(targets)


def test_level_surface_and_code_change_runs_both_sets():
    targets = gate.select_targets(["docs/design/maturity_map.yaml", "background/supervisor.py"])
    assert set(gate.CONTROL_TESTS) <= set(targets)
    assert set(gate.LEVEL_SENSITIVE_TESTS) <= set(targets)


def test_level_sensitive_test_files_all_exist():
    for t in gate.LEVEL_SENSITIVE_TESTS:
        assert (ROOT / t).exists(), f"level-sensitive test missing: {t}"


def test_staged_mint_marker_runs_the_hygiene_set():
    # A PLANNER_MINTED_*.md parked in in_progress/ is pure DATA (not under CODE_PREFIXES); staging one
    # must still run the mint-block-hygiene test so a reason-less/unresolvable block cannot be committed
    # (unstated_reason_block_impossible §3 -- the sibling of the level-surface hole).
    targets = gate.select_targets(
        ["docs/staging/in_progress/PLANNER_MINTED_something_2026-07-28.md"]
    )
    assert targets != []                                          # NOT skipped as "pure data"
    assert set(gate.MINT_HYGIENE_TESTS) <= set(targets)


def test_non_mint_staging_doc_is_still_pure_data():
    # a director/advisor SOURCE doc or a from_rich note in staging is NOT a mint marker -> stays fast
    assert gate.select_targets(["docs/staging/in_progress/DIRECTOR_RULING_FOO.md"]) == []
    assert gate.select_targets(["docs/staging/from_rich_123.md"]) == []


def test_mint_hygiene_test_files_all_exist():
    for t in gate.MINT_HYGIENE_TESTS:
        assert (ROOT / t).exists(), f"mint-hygiene test missing: {t}"


def test_pytest_subprocess_env_strips_GIT_star(monkeypatch):
    # H24 regression: during a `git commit` the hook inherits GIT_INDEX_FILE/GIT_DIR/GIT_WORK_TREE
    # pointing at the in-progress commit. If those leak into the pytest subprocess, git-touching
    # tests corrupt the REAL worktree index (observed: phantom deletions, once a tree-deleting
    # commit; likely the core.bare=true setter). The gate MUST run pytest with GIT_* scrubbed.
    monkeypatch.setattr(gate, "staged_files", lambda: ["background/supervisor.py"])
    monkeypatch.setattr(gate, "select_targets", lambda files: ["tests/background/test_supervisor.py"])
    for k in ("GIT_INDEX_FILE", "GIT_DIR", "GIT_WORK_TREE", "GIT_PREFIX"):
        monkeypatch.setenv(k, "/should/not/leak")
    captured = {}

    class _R:
        returncode = 0

    def _fake_run(cmd, *a, **kw):
        captured["env"] = kw.get("env")
        return _R()

    monkeypatch.setattr(gate.subprocess, "run", _fake_run)
    assert gate.main() == 0
    env = captured["env"]
    assert env is not None, "the pytest subprocess must be given an explicit (scrubbed) env"
    leaked = sorted(k for k in env if k.startswith("GIT_"))
    assert leaked == [], f"GIT_* leaked into the gate's pytest subprocess: {leaked}"


def test_gitless_env_strips_all_GIT_star_directly():
    # Direct unit proof of the helper the shipped fix actually calls: no GIT_* survives, and
    # everything else passes through untouched.
    fake_env = {
        "GIT_DIR": "/fake/.git",
        "GIT_INDEX_FILE": "/fake/.git/index",
        "GIT_WORK_TREE": "/fake",
        "GIT_PREFIX": "",
        "PATH": "/usr/bin:/bin",
        "HOME": "/home/nobody",
    }
    result = gate._gitless_env(fake_env)
    assert [k for k in result if k.startswith("GIT_")] == []
    assert result["PATH"] == "/usr/bin:/bin"
    assert result["HOME"] == "/home/nobody"


def _run_git(args, cwd, env):
    return subprocess.run(
        ["git", *args], cwd=cwd, env=env, capture_output=True, text=True,
    )


def _make_isolated_repo(clean_env):
    """A throwaway repo in its own tempdir -- NEVER the real .git. Returns its path with an
    initial commit (so it has a real index/HEAD) and core.bare confirmed false."""
    repo = tempfile.mkdtemp(prefix="h24_isolated_repo_")
    _run_git(["init", "-q"], cwd=repo, env=clean_env)
    _run_git(["config", "user.email", "h24-test@example.invalid"], cwd=repo, env=clean_env)
    _run_git(["config", "user.name", "H24 Mutation Test"], cwd=repo, env=clean_env)
    (Path(repo) / "seed.txt").write_text("seed\n")
    _run_git(["add", "seed.txt"], cwd=repo, env=clean_env)
    _run_git(["commit", "-q", "-m", "initial"], cwd=repo, env=clean_env)
    baseline_bare = _run_git(
        ["config", "--get", "core.bare"], cwd=repo, env=clean_env
    ).stdout.strip()
    assert baseline_bare == "false", "isolated repo fixture must start non-bare"
    return repo


def _repo_core_bare(repo, clean_env):
    return _run_git(["config", "--get", "core.bare"], cwd=repo, env=clean_env).stdout.strip()


def test_r15_scrub_prevents_leaked_git_dir_corruption__mutation_proof():
    """R15 mutation proof (CONTROLS_THAT_CANNOT_FAIL): prove the GIT_* scrub in
    tools/pre_commit_test_gate.py::_gitless_env is the thing standing between a leaked
    GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE and a corrupted repo -- in BOTH directions -- entirely
    against a throwaway isolated repo, never the real worktree.

    Named defect (H26/H24 incident): a gate-run test inherits GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE
    pointing at an in-progress commit; an unscrubbed subprocess env lets a stray `git` invocation
    obey those leaked vars and mutate that repo's state (e.g. flip core.bare) regardless of its own
    cwd -- observed as index corruption / a tree-deleting commit / core.bare=true in the real
    incident.
    """
    clean_env = gate._gitless_env(dict(os.environ))  # our own test process must not leak either
    isolated_repo = _make_isolated_repo(clean_env)

    # A neutral cwd that is NOT a git repo at all (and is neither the isolated repo nor the real
    # worktree) -- so the only way `git config` can succeed is by obeying a leaked GIT_DIR.
    neutral_cwd = tempfile.mkdtemp(prefix="h24_neutral_cwd_")

    leaked_env = dict(clean_env)
    leaked_env["GIT_DIR"] = str(Path(isolated_repo) / ".git")
    leaked_env["GIT_WORK_TREE"] = isolated_repo
    leaked_env["GIT_INDEX_FILE"] = str(Path(isolated_repo) / ".git" / "index")

    # --- WITH the shipped scrub (the real code path: gate._gitless_env applied to the leak) ---
    scrubbed_env = gate._gitless_env(leaked_env)
    assert [k for k in scrubbed_env if k.startswith("GIT_")] == []
    with_scrub = _run_git(
        ["config", "core.bare", "true"], cwd=neutral_cwd, env=scrubbed_env,
    )
    assert with_scrub.returncode != 0, (
        "with GIT_* scrubbed and a non-repo cwd, `git config` must FAIL -- if it succeeds, "
        "the leaked GIT_DIR is still reaching it somehow"
    )
    assert _repo_core_bare(isolated_repo, clean_env) == "false", (
        "the scrub must leave the isolated repo untouched"
    )

    # --- WITHOUT the scrub (the mutation: same leak, but passed straight through unscrubbed,
    # exactly what the pre-fix gate did) -- this must REPRODUCE the corruption, proving the
    # defect is real and the scrub is what prevents it. ---
    without_scrub = _run_git(
        ["config", "core.bare", "true"], cwd=neutral_cwd, env=leaked_env,
    )
    assert without_scrub.returncode == 0, (
        "expected the unscrubbed leaked GIT_DIR to let `git config` succeed against the "
        "isolated repo -- if it didn't, this test can't demonstrate the defect"
    )
    assert _repo_core_bare(isolated_repo, clean_env) == "true", (
        "the unscrubbed leak must reproduce the corruption (core.bare flipped) on the "
        "ISOLATED repo -- proving the named H24/H26 defect is real"
    )


def _staged_deletions(repo, clean_env):
    """Index-vs-HEAD staged changes for the isolated repo (read with a clean env)."""
    return _run_git(["diff", "--cached", "--name-status"], cwd=repo, env=clean_env).stdout.strip()


def test_r15_scrub_prevents_leaked_index_phantom_deletion__mutation_proof():
    """R15 mutation proof for the SECOND named corruption mode of the H24/H26 incident:
    INDEX PHANTOM-DELETIONS (the mode that actually wedged the publish/commit chain), distinct
    from the core.bare flip already covered by
    test_r15_scrub_prevents_leaked_git_dir_corruption__mutation_proof.

    Named defect: during a `git commit` the hook inherits GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE
    pointing at the in-progress commit's index; an unscrubbed gate-run test that stages a removal
    (`git rm --cached ...`) from its own neutral cwd then obeys those leaked vars and phantom-deletes
    a file from the REAL index -- observed in the incident as "index phantom-deletions" and a
    tree-deleting commit. Proven in BOTH directions against a throwaway isolated repo, never the real
    worktree. Complements the core.bare proof so the control is measured against more than one of the
    corruption modes it actually caused (R15 CONTROLS_THAT_CANNOT_FAIL: a control proven on only one
    of its defect's faces is under-proven).
    """
    clean_env = gate._gitless_env(dict(os.environ))
    isolated_repo = _make_isolated_repo(clean_env)  # has a committed seed.txt, clean index
    assert _staged_deletions(isolated_repo, clean_env) == "", "fixture must start with a clean index"

    # A neutral cwd that is NOT a git repo -- so the only way `git rm --cached` can touch an index
    # is by obeying the leaked GIT_DIR/GIT_INDEX_FILE, exactly the commit-time leak vector.
    neutral_cwd = tempfile.mkdtemp(prefix="h24_idx_neutral_cwd_")

    leaked_env = dict(clean_env)
    leaked_env["GIT_DIR"] = str(Path(isolated_repo) / ".git")
    leaked_env["GIT_WORK_TREE"] = isolated_repo
    leaked_env["GIT_INDEX_FILE"] = str(Path(isolated_repo) / ".git" / "index")

    # --- WITH the shipped scrub (the real code path) --- must FAIL, index untouched ---
    scrubbed_env = gate._gitless_env(leaked_env)
    assert [k for k in scrubbed_env if k.startswith("GIT_")] == []
    with_scrub = _run_git(["rm", "--cached", "seed.txt"], cwd=neutral_cwd, env=scrubbed_env)
    assert with_scrub.returncode != 0, (
        "with GIT_* scrubbed and a non-repo cwd, `git rm --cached` must FAIL -- if it succeeds, "
        "the leaked GIT_INDEX_FILE is still reaching the isolated repo's index"
    )
    assert _staged_deletions(isolated_repo, clean_env) == "", (
        "the scrub must leave the isolated repo's index untouched (no phantom deletion)"
    )

    # --- WITHOUT the scrub (the mutation: leak passed straight through, the pre-fix gate) ---
    # must REPRODUCE the phantom deletion, proving the defect is real and the scrub is what stops it.
    without_scrub = _run_git(["rm", "--cached", "seed.txt"], cwd=neutral_cwd, env=leaked_env)
    assert without_scrub.returncode == 0, (
        "expected the unscrubbed leaked GIT_INDEX_FILE to let `git rm --cached` succeed against the "
        "isolated repo -- if it didn't, this test can't demonstrate the phantom-deletion defect"
    )
    assert _staged_deletions(isolated_repo, clean_env) == "D\tseed.txt", (
        "the unscrubbed leak must reproduce the INDEX phantom-deletion (seed.txt staged for removal) "
        "on the ISOLATED repo -- proving the second named H24/H26 corruption mode is real"
    )


def _head_sha(repo, clean_env):
    return _run_git(["rev-parse", "HEAD"], cwd=repo, env=clean_env).stdout.strip()


def _head_tree_names(repo, clean_env):
    """Files present in HEAD's committed tree (read with a clean env)."""
    return _run_git(["ls-tree", "--name-only", "HEAD"], cwd=repo, env=clean_env).stdout.strip()


def test_r15_scrub_prevents_leaked_tree_deleting_commit__mutation_proof():
    """R15 mutation proof for the THIRD and most destructive named corruption mode of the
    H24/H26 incident: a LEAKED TREE-DELETING COMMIT -- a gate-run test that not only stages a
    removal but COMMITS it, landing a new commit on the real repo's HEAD whose tree has the file
    deleted ("once producing a commit that deleted the whole tree").

    This is distinct from the two faces already proven:
      - core.bare flip (test_r15_scrub_prevents_leaked_git_dir_corruption__mutation_proof) mutates
        CONFIG;
      - index phantom-deletion (test_r15_scrub_prevents_leaked_index_phantom_deletion__mutation_proof)
        mutates the INDEX but stops before a commit is written.
    The third face proves the failure reaches HEAD itself: an unscrubbed leak lets a `git rm --cached`
    + `git commit` sequence from a neutral cwd advance the isolated repo's HEAD to a commit whose tree
    is EMPTY. R15 CONTROLS_THAT_CANNOT_FAIL: a control is under-proven while any face of its named
    defect is unmeasured -- all three incident faces now fire against the scrub, both directions, on a
    throwaway isolated repo, never the real worktree.
    """
    clean_env = gate._gitless_env(dict(os.environ))
    isolated_repo = _make_isolated_repo(clean_env)  # committed seed.txt, clean index, HEAD present
    baseline_head = _head_sha(isolated_repo, clean_env)
    assert _head_tree_names(isolated_repo, clean_env) == "seed.txt", "fixture HEAD must hold seed.txt"

    # A neutral cwd that is NOT a git repo -- so the only way a commit can reach ANY repo is by
    # obeying the leaked GIT_DIR/GIT_INDEX_FILE, exactly the commit-time leak vector.
    neutral_cwd = tempfile.mkdtemp(prefix="h24_commit_neutral_cwd_")

    leaked_env = dict(clean_env)
    leaked_env["GIT_DIR"] = str(Path(isolated_repo) / ".git")
    leaked_env["GIT_WORK_TREE"] = isolated_repo
    leaked_env["GIT_INDEX_FILE"] = str(Path(isolated_repo) / ".git" / "index")

    def _stage_and_commit(env):
        _run_git(["rm", "--cached", "seed.txt"], cwd=neutral_cwd, env=env)
        return _run_git(
            ["commit", "-q", "-m", "leaked tree-deleting commit"], cwd=neutral_cwd, env=env,
        )

    # --- WITH the shipped scrub (the real code path) --- HEAD + tree must be untouched ---
    scrubbed_env = gate._gitless_env(leaked_env)
    assert [k for k in scrubbed_env if k.startswith("GIT_")] == []
    _stage_and_commit(scrubbed_env)
    assert _head_sha(isolated_repo, clean_env) == baseline_head, (
        "with GIT_* scrubbed the leaked commit must NOT land -- HEAD must be unmoved"
    )
    assert _head_tree_names(isolated_repo, clean_env) == "seed.txt", (
        "the scrub must leave the isolated repo's committed tree intact (seed.txt still present)"
    )

    # --- WITHOUT the scrub (the mutation: leak passed straight through, the pre-fix gate) ---
    # must REPRODUCE the tree-deleting commit: HEAD advances to a commit whose tree is empty.
    res = _stage_and_commit(leaked_env)
    assert res.returncode == 0, (
        "expected the unscrubbed leaked env to let `git commit` succeed against the isolated repo "
        f"-- if it didn't, this test can't demonstrate the tree-deleting-commit defect: {res.stderr}"
    )
    assert _head_sha(isolated_repo, clean_env) != baseline_head, (
        "the unscrubbed leak must LAND A NEW COMMIT on the isolated repo's HEAD"
    )
    assert _head_tree_names(isolated_repo, clean_env) == "", (
        "the unscrubbed leaked commit must DELETE THE WHOLE TREE (HEAD tree now empty) -- proving "
        "the third named H24/H26 corruption mode is real and the scrub is what prevents it"
    )


def _make_isolated_repo_with_worktree(clean_env):
    """A throwaway MAIN repo plus a linked worktree -- NEVER the real .git. Returns
    (main_repo, worktree_gitdir, common_dir). The worktree's gitdir lives under
    main/.git/worktrees/<name> and shares main/.git as its GIT_COMMON_DIR, exactly the layout
    this project's own .claude/worktrees/* commits run under."""
    main_repo = _make_isolated_repo(clean_env)  # committed seed.txt, clean index, core.bare=false
    wt_path = tempfile.mkdtemp(prefix="h24_linked_wt_")
    # `git worktree add` needs a fresh path; it created wt_path already, so let git own a subdir.
    linked = str(Path(wt_path) / "wt")
    add = _run_git(["worktree", "add", "-q", linked, "-b", "h24wtbranch"], cwd=main_repo, env=clean_env)
    assert add.returncode == 0, f"worktree add must succeed to set up the fixture: {add.stderr}"
    worktree_gitdir = str(Path(main_repo) / ".git" / "worktrees" / "wt")
    common_dir = str(Path(main_repo) / ".git")
    assert Path(worktree_gitdir).is_dir(), "the linked worktree's gitdir must exist under main/.git/worktrees"
    return main_repo, worktree_gitdir, common_dir


def test_r15_scrub_prevents_leaked_worktree_common_dir_corruption__mutation_proof():
    """R15 mutation proof for the WORKTREE face of the H24/H26 incident -- the vector most likely
    to have produced its "repeated core.bare=true", because this project commits from linked
    worktrees (.claude/worktrees/*) constantly.

    Distinct from the three faces already proven, which all leak a SINGLE-repo GIT_DIR. During a
    `git commit` inside a LINKED worktree, git additionally sets GIT_COMMON_DIR pointing at the MAIN
    repo's shared .git. A config write (like `core.bare`) then lands on the SHARED common config --
    corrupting the main repo -- even though GIT_DIR points at the worktree's own private gitdir. None
    of the earlier proofs set GIT_COMMON_DIR, so this real leak vector was previously unmeasured
    (R15 CONTROLS_THAT_CANNOT_FAIL: a control is under-proven while any face of its named defect is
    unmeasured). Proven in BOTH directions against a throwaway repo, never the real worktree.
    """
    clean_env = gate._gitless_env(dict(os.environ))
    main_repo, worktree_gitdir, common_dir = _make_isolated_repo_with_worktree(clean_env)
    assert _repo_core_bare(main_repo, clean_env) == "false", "fixture main repo must start non-bare"

    # A neutral cwd that is NOT a git repo -- so the only way `git config` can reach the shared
    # common config is by obeying the leaked worktree-commit env (GIT_DIR + GIT_COMMON_DIR).
    neutral_cwd = tempfile.mkdtemp(prefix="h24_wt_neutral_cwd_")

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
    # REPRODUCE the corruption on the SHARED common config, proving the worktree vector is real. ---
    without_scrub = _run_git(["config", "core.bare", "true"], cwd=neutral_cwd, env=leaked_env)
    assert without_scrub.returncode == 0, (
        "expected the unscrubbed leaked worktree env to let `git config` succeed against the shared "
        "common dir -- if it didn't, this test can't demonstrate the worktree defect"
    )
    assert _repo_core_bare(main_repo, clean_env) == "true", (
        "the unscrubbed leaked GIT_COMMON_DIR must flip core.bare on the SHARED main config -- "
        "proving the worktree corruption vector (the likeliest source of the incident's repeated "
        "core.bare=true) is real and the scrub is what prevents it"
    )


def test_committed_hook_invokes_the_gate_and_aborts_on_failure():
    # Reconstruct-from-repo: the committed hook itself must call the gate and abort on non-zero.
    hook = (ROOT / "tools" / "git-hooks" / "pre-commit").read_text()
    assert "tools/pre_commit_test_gate.py" in hook
    assert "exit 1" in hook                                   # a gate failure ABORTS the commit
    # and the installer that makes it reconstruct-from-repo exists + sets core.hooksPath
    installer = (ROOT / "tools" / "install_git_hooks.sh").read_text()
    assert "core.hooksPath" in installer and "tools/git-hooks" in installer


def _load_facets_module():
    """Load tests/design/test_maturity_map_facets.py by path (no relative imports),
    the module the gate runs when maturity_map.yaml is staged."""
    fp = ROOT / "tests" / "design" / "test_maturity_map_facets.py"
    spec = importlib.util.spec_from_file_location("_facets_for_gate_proof", fp)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_gate_refuses_an_unparseable_maturity_map__mutation_proof():
    # R15 / CONTROLS_THAT_CANNOT_FAIL for the H24 SIBLING GAP (registered 2026-07-18, real incident:
    # a flow-style ", " join fused mid block-sequence produced an invalid maturity_map.yaml that the
    # test-gate PASSED and pushed to origin, breaking every map consumer). The closure is transitive
    # (map ∈ LEVEL_SURFACE_FILES -> the gate runs test_maturity_map_facets.py -> its loader parses
    # the on-disk map -> a ParserError errors the test -> pytest rc!=0 -> commit refused). That
    # closure was never PROVEN, so a refactor (drop the facet test from the level set, or wrap the
    # loader in try/except) could silently re-open it. This locks it in, both directions.
    import yaml

    # Part A -- WIRING: a maturity_map.yaml change MUST pull in the parse-checking facet test.
    # (Non-vacuous: remove test_maturity_map_facets.py from LEVEL_SENSITIVE_TESTS and this reds.)
    targets = gate.select_targets(["docs/design/maturity_map.yaml"])
    assert "tests/design/test_maturity_map_facets.py" in targets, (
        "a maturity_map.yaml change must run the facet test that parses the map -- without it an "
        "unparseable map commits green (the 2026-07-18 sibling-gap incident)"
    )

    # Part B -- NON-VACUITY: that selected test's loader must REFUSE an unparseable map and ACCEPT a
    # valid one. (Non-vacuous: wrap _load_live_atoms's yaml.safe_load in try/except-return-[] and the
    # unparseable-map assertion reds.) Points the loader at throwaway temp files; never the real map.
    facets = _load_facets_module()
    orig = facets.MAP_PATH
    bad = Path(tempfile.mkdtemp(prefix="h24_badmap_")) / "maturity_map.yaml"
    # the exact defect class from the incident: a flow-style ", " join fused into a block sequence
    bad.write_text("- id: x\n  simplifications:\n  - a', 'b\n    unclosed: [1, 2\n")
    good = Path(tempfile.mkdtemp(prefix="h24_goodmap_")) / "maturity_map.yaml"
    good.write_text("- id: x\n  level_current: 1\n")
    try:
        facets.MAP_PATH = bad
        raised = False
        try:
            facets._load_live_atoms()
        except yaml.YAMLError:
            raised = True
        assert raised, (
            "the facet loader must raise a YAMLError on an unparseable map -- if it swallows the "
            "parse error the gate would pass a broken map (sibling gap re-opened)"
        )
        facets.MAP_PATH = good
        assert isinstance(facets._load_live_atoms(), list), (
            "a valid map must still parse clean -- else the guard is a tautology that always fires"
        )
    finally:
        facets.MAP_PATH = orig


def test_scrub_does_NOT_close_ambient_cwd_upward_walk__known_residual_boundary():
    """RED-TEAM boundary test (H24 harden pass, 2026-07-27): mark, as a permanent executable fact,
    exactly WHERE the GIT_* scrub's protection ends -- so the twice-queued-but-never-captured residual
    (decision_log 2026-07-27) stops evaporating (consumed != absorbed).

    The scrub removes the ACUTE vector: an inherited GIT_DIR/GIT_INDEX_FILE that lets a stray `git`
    obey the in-progress commit's index from ANY cwd. The two mutation proofs above cover that.

    But the real gate runs its pytest subprocess with cwd=ROOT (pre_commit_test_gate.main). A gate-run
    test that shells `git` from that inherited cwd WITHOUT pointing at its own repo still DISCOVERS the
    real .git by upward directory-walk -- GIT_* being absent does not stop discovery-by-location. This
    is LATENT, not active: every H24 control/gate-run test uses a throwaway tmp repo with an explicit
    cwd, so none actually exercises this path. Closing it (e.g. GIT_CEILING_DIRECTORIES) risks
    regressing control tests that legitimately read the real repo, so it needs its own scoped atom +
    which-tests analysis (SELF_INTERRUPT_DISCIPLINE) -- NOT a fix-on-sight here.

    STRICTLY READ-ONLY against the real repo: `git rev-parse` only, never a mutating command.
    """
    scrubbed_env = gate._gitless_env(dict(os.environ))
    assert [k for k in scrubbed_env if k.startswith("GIT_")] == []

    # (a) scrub + a neutral NON-repo cwd -> git finds no repo at all. This is the vector the scrub
    #     DOES close (same asymmetry the mutation proofs rely on).
    neutral_cwd = tempfile.mkdtemp(prefix="h24_residual_neutral_")
    at_neutral = _run_git(["rev-parse", "--show-toplevel"], cwd=neutral_cwd, env=scrubbed_env)
    assert at_neutral.returncode != 0, (
        "with GIT_* scrubbed and a non-repo cwd, git must resolve NO repository -- the scrub closes "
        "the leaked-env vector"
    )

    # (b) scrub + cwd=ROOT (the gate's REAL subprocess cwd) -> git STILL resolves the real repo by
    #     upward-walk. This is the residual: scrubbing GIT_* does not make gate-run tests location-blind
    #     to the real .git. Documented here so a future careless mutating command from cwd=ROOT is a
    #     KNOWN, tested boundary rather than a surprise re-run of the H24/H26 incident.
    at_root = _run_git(["rev-parse", "--show-toplevel"], cwd=str(ROOT), env=scrubbed_env)
    assert at_root.returncode == 0 and Path(at_root.stdout.strip()) == ROOT, (
        "with GIT_* scrubbed but cwd=ROOT, git still discovers the REAL repo via upward-walk -- if "
        "this ever stops being true the scoped ambient-cwd hardening atom has landed; update this "
        "boundary marker to assert the new (closed) behaviour"
    )
    at_root_bare = _run_git(["rev-parse", "--is-bare-repository"], cwd=str(ROOT), env=scrubbed_env)
    assert at_root_bare.stdout.strip() == "false", "sanity: the real worktree must never read as bare"


import re


def _hook_gate_modules() -> list[Path]:
    """Every `python3 tools/<name>.py` gate the committed pre-commit hook chains, in order.

    Reconstruct-from-repo: derived from the hook TEXT, so a future gate added to the chain is
    picked up automatically -- the whole point of a class guard.
    """
    hook = (ROOT / "tools" / "git-hooks" / "pre-commit").read_text()
    rels = re.findall(r"python3\s+(tools/\w+\.py)", hook)
    return [ROOT / r for r in dict.fromkeys(rels)]  # dedupe, preserve order


def test_every_hook_gate_that_spawns_pytest_scrubs_GIT_star__class_guard():
    """R10/H24 CLASS closure (audit-the-sibling-half): the H24 root cause was a commit-time hook
    step spawning a git-touching pytest subprocess under the inherited GIT_INDEX_FILE/GIT_DIR/
    GIT_WORK_TREE, corrupting the SHARED .git. Fixed instance-by-instance in pre_commit_test_gate.py
    AND its sibling site_lane_gate.py. This guards the CLASS instead of the two instances: EVERY
    gate the committed hook chains that spawns a `pytest` subprocess MUST scrub GIT_* from that
    subprocess's env. A future 7th gate that runs tests without scrubbing reds THIS test at write
    time -- the class fails automatically, per R10 (a class defect is closed by an invariant, not an
    instance fix), rather than waiting to re-corrupt the repo like H24/H26 did.

    The read-only gates (level_promotion, moap_coherence, ruling_archive_question) run only their
    OWN `git show`/`git diff --cached` -- read-only, cannot corrupt -- and deliberately KEEP
    GIT_INDEX_FILE so `git show :<path>` inspects the in-progress commit's staged blob. They are
    correctly out of scope here; the invariant targets ONLY gates that spawn arbitrary subprocesses.
    """
    gates = _hook_gate_modules()
    assert gates, "parsed ZERO gates from the hook -- the regex/hook drifted (fail-closed, not open)"

    checked_spawners: list[str] = []
    for path in gates:
        assert path.exists(), f"hook references a non-existent gate: {path}"
        src = path.read_text()
        spawns_pytest = '"pytest"' in src        # pytest as a subprocess argv literal (not a docstring)
        if not spawns_pytest:
            continue
        checked_spawners.append(path.name)
        scrubs_git = 'startswith("GIT_")' in src
        assert scrubs_git, (
            f"{path.name} spawns a pytest subprocess but does NOT scrub GIT_* from its env -- this is "
            f"the exact H24 corruption class (a git-touching test inherits the commit's GIT_INDEX_FILE/"
            f"GIT_DIR and writes the SHARED .git). Filter os.environ through a `_gitless_env` that drops "
            f"every key starting 'GIT_' and pass it as subprocess env=."
        )

    # R15 -- this guard must be able to FAIL, so it must actually EXERCISE the known spawners rather
    # than silently pass by matching none. If the two known pytest gates aren't both seen, the
    # detector (or the hook chain) has drifted and the class is no longer being guarded.
    assert {"pre_commit_test_gate.py", "site_lane_gate.py"}.issubset(set(checked_spawners)), (
        f"expected both known pytest-spawning gates to be checked; saw {checked_spawners}. The "
        f"detector or the hook chain drifted -- the class guard is not covering what it claims."
    )
