"""Pre-commit TEST GATE selection logic (director P0, 2026-07-17).

The gate's job: whenever a CODE/config file is staged, run the safety-control set + the tests for
each changed source file, and ABORT the commit on any failure -- so a red commit is structurally
impossible. These test the SELECTION logic (which tests run for which changeset); the end-to-end
"a commit with a failing test is REFUSED" is proven live against the real git hook.
"""
from __future__ import annotations

import ast
import importlib.util
import os
import subprocess
import tempfile
from pathlib import Path

from tools import maturity_map_store as map_store  # noqa: E402

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


def test_aspect_named_test_files_are_selected_not_just_the_exact_stem():
    """R15, and it fires on THE defect that wedged publishing on 2026-08-09.

    `simulation/live_population.py` is covered ONLY by `test_live_population_seam.py`. The gate
    globbed the exact stem, mapped the module to zero tests, and let a change land that reddened
    that very file on the next publish cycle. Asserted against the REAL repo layout rather than a
    fixture, because the defect was precisely that the real layout disagreed with the glob.
    """
    selected = gate.tests_for("simulation/live_population.py")
    assert "tests/simulation/test_live_population_seam.py" in selected, (
        "the gate must select an aspect-named test file for the module it covers; "
        f"got {selected}"
    )


def test_the_stem_glob_does_not_over_match_a_longer_module_name():
    """The suffix widening must not make the mapping promiscuous: `test_<stem>_*.py` may only
    match tests of THIS module, never tests of a DIFFERENT module that merely starts with the
    same stem. Without this, a module named `foo` would drag in every `foo_bar` test and the
    gate's cost would grow without bound."""
    # `supervisor.py` must not pull in a test named for a different module entirely.
    selected = gate.tests_for("background/supervisor.py")
    assert all(
        Path(t).name.startswith("test_supervisor") for t in selected
    ), f"selection leaked past the supervisor stem: {selected}"


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


# ── THE LINT RATCHET's selection hole (2026-08-26) ───────────────────────────────────────────
# R15 on the SELECTION layer. The shrink-only ruff ratchet lints the WHOLE REPO but was selected
# by filename stem, so only a commit touching its own file could run it. It was found red at HEAD
# four times (08-10, 08-12, 08-14, 08-26); the last found 22 violations across 8 codes that had
# each landed green. This pins the repair: an ORDINARY .py commit, one that does not touch the
# ratchet and has no test file of its own, must still select it.
#
# The assertion deliberately uses a path that CANNOT map to the ratchet by stem, because a stem
# match would prove nothing about the always-on set -- which is the whole defect being fixed.

RUFF_RATCHET = "tests/architecture/test_static_quality_ratchet.py"


def test_an_ordinary_code_commit_selects_the_lint_ratchet():
    targets = gate.select_targets(["saas/some_new_module.py"])
    assert RUFF_RATCHET in targets, (
        "a commit that can move the repo-wide ruff census must RUN the ratchet that "
        "forbids raising it; stem selection alone reaches it only from its own file, which "
        "is how 22 violations landed green past a shrink-only floor"
    )
    # The subject really is repo-wide, so the selection hole really was total: assert the
    # ratchet's own scope rather than trusting the comment above it.
    ratchet_src = (ROOT / RUFF_RATCHET).read_text()
    assert 'ruff_counts_for(makefile_lint_scope(), REPO_ROOT)' in ratchet_src, (
        "the ratchet no longer lints the Makefile scope from the repo root; if its subject "
        "narrowed to something a stem selector can reach, this entry can leave CONTROL_TESTS"
    )


def test_mutation_dropping_the_ratchet_from_the_control_set_is_visible():
    """The control can FAIL: with the entry removed, an ordinary commit stops selecting it."""
    without = [t for t in gate.CONTROL_TESTS if t != RUFF_RATCHET]
    assert len(without) == len(gate.CONTROL_TESTS) - 1, "the ratchet is not in CONTROL_TESTS"
    original = gate.CONTROL_TESTS
    try:
        gate.CONTROL_TESTS = without
        assert RUFF_RATCHET not in gate.select_targets(["saas/some_new_module.py"])
    finally:
        gate.CONTROL_TESTS = original
    # ...and restoring it brings the selection back, so the assertion above tracks the list
    # rather than some unrelated always-on path.
    assert RUFF_RATCHET in gate.select_targets(["saas/some_new_module.py"])


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


# ── THE PER-ATOM STORE surface (2026-08-10, the fourteenth publish wedge). A MINT declares ───────
# `records_rehomed`/`notes_rehomed` from a template while never writing
# docs/design/simplifications/<id>.yaml, so the map claims a store file that does not exist. The
# two store-contract tests fire on precisely that, but nothing MAPPED them to a map change -- so
# four mints in three days each landed red on committed HEAD and were found hours later by the
# publish gate. The literal paths are asserted, not gate.STORE_CONTRACT_TESTS: a test that reads
# the constant it is checking cannot fail when the constant empties.

def test_a_map_change_runs_the_store_contract_tests():
    targets = gate.select_targets(["docs/design/maturity_map.yaml"])
    assert "tests/design/test_atom_notes_store.py" in targets
    assert "tests/design/test_atom_records_store.py" in targets


def test_a_store_file_change_alone_runs_the_store_contract_tests():
    # The other direction: deleting or renaming a store file falsifies a declaration living in a
    # file this commit never touches. docs/design/simplifications/ is under no CODE_PREFIX.
    targets = gate.select_targets(["docs/design/simplifications/A9_market_at_the_seams.yaml"])
    assert targets != []                                          # NOT skipped as "pure data"
    assert "tests/design/test_atom_notes_store.py" in targets
    assert "tests/design/test_atom_records_store.py" in targets


def test_a_non_store_design_doc_is_still_pure_data():
    # Non-vacuity: the prefix must not swallow docs/design at large, or every design-doc commit
    # pays the contract suite and the fast path is gone.
    # The two paths are ASSEMBLED, not written as literals: since the data surface landed
    # (2026-08-12) a path spelled out here would appear in THIS file's source, `git grep` would
    # find it, and the selector would correctly select this very test -- a fixture refuting itself
    # rather than a defect in the selection.
    assert gate.select_targets(["docs/design/" + "THE_STANDARD" + ".md"]) == []
    # The store README is no longer "pure data", and that is the data surface being RIGHT rather
    # than this test being weakened: tests/design/test_simplifications_store.py opens by naming
    # this file as the source of the invariants it enforces, so its content can red that test.
    # The intent this test exists for is unchanged and still asserted -- the STORE prefix must not
    # swallow docs/design at large, i.e. no contract SUITE, only what actually reads the file.
    readme = gate.select_targets(["docs/design/simplifications/" + "README" + ".md"])
    assert readme == ["tests/design/test_simplifications_store.py"]
    # 2026-08-14: this line used to read `not set(STORE_CONTRACT_TESTS) & set(readme)` and had been
    # RED at HEAD since `test_simplifications_store.py` was added to STORE_CONTRACT_TESTS the same
    # day -- it contradicted the assertion directly above it, which requires exactly that file, and
    # so refused every commit touching this gate. The intent the comment above states is that the
    # README must not pull the whole contract SUITE, "only what actually reads the file". That is a
    # STRICT SUBSET claim, not a disjointness one; disjointness became unsatisfiable the moment the
    # file that reads the README joined the suite. Asserted as intended, and non-vacuously:
    assert set(readme) < set(gate.STORE_CONTRACT_TESTS), (
        "the README must select only the test that reads it, never the whole store suite"
    )


def test_store_contract_test_files_all_exist():
    for t in gate.STORE_CONTRACT_TESTS:
        assert (ROOT / t).exists(), f"store-contract test missing: {t}"


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
    # assembled, not literal -- see test_a_non_store_design_doc_is_still_pure_data
    assert gate.select_targets(["docs/staging/in_progress/" + "DIRECTOR_RULING_FOO" + ".md"]) == []
    assert gate.select_targets(["docs/staging/" + "from_rich_123" + ".md"]) == []


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
    # The wall-crossing step (2026-08-13) runs BEFORE the pytest launch and shells out to
    # `git write-tree`, so the blanket `subprocess.run` fake below reaches it and it fails
    # closed -- correctly, and on a subject that is not this test's. Neutralised HERE rather
    # than exempted THERE: this test's subject is the pytest subprocess's environment, and a
    # sibling refusal must not be allowed to answer it. Its own env contract (which is the
    # OPPOSITE one -- GIT_INDEX_FILE must be INHERITED) is proven in
    # tests/tools/test_pre_commit_gate_wall_register.py::test_index_tree_honours_GIT_INDEX_FILE.
    monkeypatch.setattr(gate, "_wall_crossing_landed_check", lambda staged: (True, ""))
    # The symbol-landing step (2026-08-14) is the third sibling with this property and is
    # neutralised for the identical reason: it shells out to `git write-tree` and
    # `git cat-file` before the pytest launch, so the blanket fake below reaches it and it
    # fails closed on a subject that is not this test's. Its own contract -- including the
    # fail-closed behaviour being suppressed here -- is proven in
    # tests/tools/test_symbol_landing_check.py, which is where it belongs.
    monkeypatch.setattr(gate, "_symbol_landing_check", lambda staged: (True, ""))
    # The wall-channel census step (2026-08-19) is the fourth sibling with this property, and is
    # neutralised for the identical reason: it shells out to `git write-tree` and `git archive`
    # before the pytest launch. Its own contract, fail-closed branches included, is proven in
    # tests/tools/test_wall_channel_census.py.
    monkeypatch.setattr(gate, "_wall_channel_census_check", lambda staged: (True, ""))
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
        # Since 2026-08-26 the loader goes through `tools.maturity_map_store`, which wraps a
        # parse failure in MapStoreError so the message can say WHICH half of the two-file map
        # broke. What this test pins is unchanged and is the only thing it ever pinned: the
        # loader RAISES rather than swallowing. Both types are accepted so the assertion cannot
        # be greened by a future loader that catches the parse error and returns [].
        except (yaml.YAMLError, map_store.MapStoreError):
            raised = True
        assert raised, (
            "the facet loader must RAISE on an unparseable map -- if it swallows the parse "
            "error the gate would pass a broken map (sibling gap re-opened)"
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


import re  # noqa: E402


def _hook_gate_modules() -> list[Path]:
    """Every `python3 tools/<name>.py` gate the committed pre-commit hook chains, in order.

    Reconstruct-from-repo: derived from the hook TEXT, so a future gate added to the chain is
    picked up automatically -- the whole point of a class guard.
    """
    hook = (ROOT / "tools" / "git-hooks" / "pre-commit").read_text()
    rels = re.findall(r"python3\s+(tools/\w+\.py)", hook)
    return [ROOT / r for r in dict.fromkeys(rels)]  # dedupe, preserve order


_SPAWN_FUNCS = frozenset({"run", "Popen", "call", "check_call", "check_output"})


def _argv_mentions_pytest(node) -> bool:
    """True if this AST node is an argv literal containing the element "pytest"."""
    if isinstance(node, ast.BinOp):  # ["git", "ls-files"] + [...]
        return _argv_mentions_pytest(node.left) or _argv_mentions_pytest(node.right)
    if isinstance(node, (ast.List, ast.Tuple)):
        return any(isinstance(el, ast.Constant) and el.value == "pytest" for el in node.elts)
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return "pytest" in node.value.split()  # shell-string form: "... -m pytest ..."
    return False


def _spawns_pytest_subprocess(src: str) -> bool:
    """Does this module actually SPAWN pytest, as opposed to merely mentioning the word?

    WHY THIS IS NOT `'"pytest"' in src` (the previous detector, 2026-08-12):
    that substring matched any occurrence of the quoted token anywhere in the file, including a
    DATA literal. `tools/orphan_ratchet.py` carries
    `_RUNNERS = frozenset({"uvicorn", ..., "pytest"})` -- a set of runner NAMES it looks for when
    deciding whether a module has a caller -- and spawns nothing but a read-only `git ls-files`.
    The guard reported it as an unscrubbed pytest spawner and had been RED at HEAD, telling
    everyone to fix a file that was never broken. A control that fires on mentions rather than
    uses spends the credibility it needs for the day it is right.

    So the detector is now structural: an argv literal containing the element "pytest", passed to
    a subprocess spawn call -- either inline, or through a simple local name bound to such a
    literal.

    FAIL DIRECTION IS TOWARDS FLAGGING. An unparseable gate returns True: we cannot show it is
    safe, and "could not tell" must not read as "does not spawn pytest" (R15).

    RESIDUAL, stated rather than left to be discovered: an argv assembled fully dynamically
    (appended in a loop, read from config) is not statically decidable and would slip past. The
    vacuity assertion at the end of the test -- both known spawners must actually be detected --
    is the backstop that catches the detector silently matching nothing at all.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return True

    pytest_names = {
        target.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign) and _argv_mentions_pytest(node.value)
        for target in node.targets
        if isinstance(target, ast.Name)
    }

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
        if name not in _SPAWN_FUNCS:
            continue
        candidates = list(node.args[:1]) + [kw.value for kw in node.keywords if kw.arg == "args"]
        for arg in candidates:
            if _argv_mentions_pytest(arg):
                return True
            if isinstance(arg, ast.Name) and arg.id in pytest_names:
                return True
    return False


def test_the_spawn_detector_reads_uses_not_mentions():
    """R15 for the detector itself, both directions.

    The 2026-08-12 false positive is pinned as a named case: a data literal of runner names must
    NOT read as a spawn, and a real spawn must still read as one.
    """
    mention_only = 'RUNNERS = frozenset({"uvicorn", "pytest"})\nsubprocess.run(["git", "ls-files"])\n'
    assert not _spawns_pytest_subprocess(mention_only), "a data literal is not a spawn"

    inline = 'subprocess.run([sys.executable, "-m", "pytest", "-q"], env=e)\n'
    assert _spawns_pytest_subprocess(inline), "an inline pytest argv is a spawn"

    via_name = 'argv = [sys.executable, "-m", "pytest"]\nsubprocess.run(argv, env=e)\n'
    assert _spawns_pytest_subprocess(via_name), "a name bound to a pytest argv is a spawn"

    assert _spawns_pytest_subprocess("def broken(:\n"), "unparseable must fail CLOSED (flagged)"

    # And the real files, which is what the class guard actually runs against.
    assert _spawns_pytest_subprocess((ROOT / "tools" / "pre_commit_test_gate.py").read_text())
    assert _spawns_pytest_subprocess((ROOT / "tools" / "site_lane_gate.py").read_text())
    assert not _spawns_pytest_subprocess((ROOT / "tools" / "orphan_ratchet.py").read_text())


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
        spawns_pytest = _spawns_pytest_subprocess(src)
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


# ---------------------------------------------------------------------------
# THE DATA SURFACE (2026-08-12) -- discharging
# WORKER_FINDING_THE_PRE_COMMIT_GATE_MAPS_NO_TESTS_TO_A_DATA_FILE_2026-08-09.md
# ---------------------------------------------------------------------------

def test_a_data_file_selects_the_tests_of_the_modules_that_READ_it__mutation_proof():
    """R15 / CONTROLS_THAT_CANNOT_FAIL. `tests_for()` returned [] for every non-`.py` path, so a
    behaviour-determining data file selected ZERO tests even when tests with tight coverage of it
    existed. The named instance is the one that caused it: a `background/process_manifest.yaml`
    edit passed this gate and wedged the publish gate on the next cycle, while
    `tests/background/test_process_reconciler.py` -- which asserts exact sets computed from that
    very file -- was never selected.

    Part A is the WIRING (does the selection reach the test), Part B is the NON-VACUITY (can that
    test actually fail on a bad manifest). Both are needed: a selection that reaches a test which
    cannot fail on this file's content would be the same defect wearing the fix's coat.
    """
    # Part A -- WIRING. (Non-vacuous: delete the data-surface branch from select_targets and this reds.)
    targets = gate.select_targets(["background/process_manifest.yaml"])
    assert "tests/background/test_process_reconciler.py" in targets, (
        "a change to the manifest that everything else DERIVES from must run the tests of the "
        f"modules that read it; got {targets}"
    )

    # Part B -- NON-VACUITY: the selected test's own loader must REFUSE a manifest that breaks its
    # schema and ACCEPT a valid one. Points the loader at throwaway temp files; never the real
    # manifest.
    from background import process_reconciler as R

    bad = Path(tempfile.mkdtemp(prefix="datasurface_bad_")) / "process_manifest.yaml"
    bad.write_text("version: 2\nprocesses:\n  - {session: x}\n")
    raised = False
    try:
        R.load_manifest(bad)
    except Exception:
        raised = True
    assert raised, (
        "the selected test's loader must reject a schema-breaking manifest -- if it swallows it, "
        "selecting the test buys nothing and the gate still cannot fail on its own named defect"
    )
    assert R.load_manifest(), "a valid live manifest must still load -- else the guard is a tautology"


def test_the_data_surface_reaches_the_wider_class_not_just_the_named_instance():
    """R10: the finding says the gap is wider than one YAML -- every `.json` config and every
    `docs/design/*.yaml` the code loads sits in the same blind spot. Closing only the instance
    would be the instance-fix R10 forbids."""
    targets = gate.select_targets(["docs/design/maturity_map.yaml"])
    assert "tests/design/test_maturity_map_facets.py" in targets
    # A data file read by a named module selects that module's tests, whatever its suffix.
    assert gate.data_surface_tests("background/process_manifest.yaml"), "yaml under a code root"
    # A design yaml with NO hand-kept surface of its own -- which is the case this test is about.
    # It used to read `maturity_map.yaml` here, and that path acquired a curated list and a
    # narrowing on 2026-08-13 (see CURATED_SURFACE_PATHS), so asserting on it would now be
    # asserting the opposite of the narrowing rather than the breadth of the derivation.
    assert gate.data_surface_tests("docs/design/CAMPAIGN_REGISTER.yaml"), "uncurated design yaml"


def test_the_data_surface_does_NOT_narrow_to_a_hand_kept_list():
    """The five existing surfaces (level, mint, canon, store, site) are hand-kept lists, each added
    after its own incident. This selection is DERIVED from what the repo actually reads, so a data
    file nobody has had an incident about is still covered."""
    src = GATE_PATH.read_text()
    assert "def data_surface_tests" in src
    # derived by asking the repo what references the path, not by a literal membership test
    assert "git" in src and "grep" in src


def test_a_genuinely_inert_data_file_still_selects_NOTHING():
    """The other direction, and the one that keeps the loop's cadence: a staging document or a
    published report that no module names must not drag tests into a docs commit. Without this the
    fix would trade a fail-open control for a gate nobody can afford to run."""
    # The path is ASSEMBLED at runtime on purpose. Written as a literal it would appear in this
    # file's own source, `git grep` would find it, and the test would then be asserting that the
    # selector is blind to a reference it can genuinely see -- a fixture refuting itself.
    absent = "docs/" + "staging/" + "NO_SUCH_FINDING_" + "ZZZ" + ".md"
    assert gate.data_surface_tests(absent) == []
    assert gate.select_targets(["docs/reports/ANNUAL_REPORT.md"]) == []


def test_the_published_output_exclusion_is_bounded_by_another_gate():
    """The data surface excludes the publisher's own output roots because deriving them costs 111s
    on the loop's most frequent commit. That is a RECORDED LIMITATION, and a recorded limitation
    has to state what still covers the ground -- otherwise "accepted" is indistinguishable from
    "forgotten". This reds if either named gate stops covering its root, so the exclusion can never
    quietly become an uncovered hole.
    """
    # site/ -- its own lane gate, plus the whole-tree SITE_SURFACE trigger in this gate.
    assert (ROOT / "tools" / "site_lane_gate.py").exists()
    assert gate.SITE_SURFACE_PREFIX == "site/"
    assert gate.select_targets(["site/proof/some_new_page.html"]) != []

    # docs/reports, docs/status -- the publish gate's subject at HEAD. Named where it is decided.
    assert "site/" in gate.PUBLISHED_OUTPUT_ROOTS
    for root in gate.PUBLISHED_OUTPUT_ROOTS:
        assert gate.data_surface_tests(root + "anything.json") == []

    # And the exclusion is EXACTLY those roots: a data file elsewhere is still derived.
    assert gate.data_surface_tests("background/process_manifest.yaml") != []


def test_a_curated_surface_path_keeps_its_curated_tests():
    """The narrowing drops the DERIVED tail and never the hand-kept list (2026-08-13).

    `docs/design/maturity_map.yaml` is staged by every auto-process publish, and deriving it
    selected 50 test files -- including a full simulation run the publish gate itself `--ignore`s
    -- which is what put the commit past its 300s hook deadline for eighteen hours. Narrowing it
    is only honest if the tests somebody deliberately chose for it still fire. Each of these was
    added to LEVEL_SENSITIVE_TESTS after its own incident, so this is the list that must survive.
    """
    selected = gate.select_targets(["docs/design/maturity_map.yaml"])

    # The derived tail is gone ...
    assert gate.data_surface_tests("docs/design/maturity_map.yaml") == []
    # ... and every curated test still runs.
    for curated in gate.LEVEL_SENSITIVE_TESTS:
        if (ROOT / curated).exists():
            assert curated in selected, f"{curated} was dropped by the narrowing"

    # The specific cost that forced this: a full sim run is no longer selected by a publish commit.
    assert "tests/simulation/test_run_phase4c_on_phase2b.py" not in selected


def test_every_curated_surface_narrowing_has_a_surface_list():
    """R15 / no-orphan-transitions: the narrowing is justified ONLY by the curated list that
    replaces it, so a path narrowed here whose surface list was later emptied or deleted is an
    uncovered hole wearing an accepted-limitation label. This reds on exactly that."""
    assert gate.CURATED_SURFACE_PATHS, "a narrowing set that is empty narrows nothing"
    # THERE ARE TWO HAND-KEPT SURFACES NOW, not one (2026-08-27). This read
    # `path in gate.LEVEL_SURFACE_FILES`, which was exact while the curated set WAS the level
    # surface. CLAUDE.md joined it carrying the CANON list, which has covered it since the
    # 2026-08-12 decay audit -- so the assertion is widened to "on a hand-kept surface", which is
    # what the docstring above always said, rather than to one specific list.
    #
    # NOT A LOOSENING: the teeth are the next line, and they are untouched. A path narrowed to
    # nothing still reds, and every one of the five currently resolves to 6-8 targets.
    hand_kept = tuple(gate.LEVEL_SURFACE_FILES) + tuple(gate.CANON_SURFACE_FILES)
    for path in gate.CURATED_SURFACE_PATHS:
        assert path in hand_kept, (
            f"{path} is narrowed but is not on a hand-kept surface -- name the list that covers it"
        )
        assert gate.select_targets([path]), f"{path} is narrowed to NOTHING -- that is a hole"

    # And the narrowing is EXACTLY those paths: another data file is still derived.
    assert gate.data_surface_tests("background/process_manifest.yaml") != []


# ---------------------------------------------------------------------------
# THE RULEBOOK IS CURATED, NOT DERIVED (2026-08-27)
# ---------------------------------------------------------------------------
# `data_surface_tests` asks "which .py files name this path". That is right for a config a module
# LOADS and wrong for a document a third of the repository CITES: of 136 .py files containing the
# text `CLAUDE.md`, 111 carry it only in a docstring or comment. The derived sweep returned 120
# test files, so adding one line to the rulebook selected 150 files and most of a fifteen-minute
# commit gate -- on the one file every rule change touches by definition.

def test_a_rulebook_edit_does_not_drag_in_every_module_that_CITES_the_rulebook():
    """The win, asserted as a bound rather than an exact count so ordinary churn does not trip
    it. Before: 120 derived targets. The curated list is six."""
    selected = gate.select_targets(["CLAUDE.md"])
    assert len(selected) <= 20, (
        "a CLAUDE.md edit selects {} test files -- the derived sweep is back, and every rule "
        "change pays for it: {}".format(len(selected), selected[:10]))
    assert gate.data_surface_tests("CLAUDE.md") == [], (
        "CLAUDE.md is on CURATED_SURFACE_PATHS, so the derived route must short-circuit")


def test_a_rulebook_edit_STILL_runs_the_parser_that_reads_the_rulebook():
    """THE PARTNER, and the one that matters: narrowing must not become blindness.

    `generate_dashboard_data._derive_build_from_claude_md` parses the build count out of
    CLAUDE.md, and CLAUDE.md's own line says so -- "This figure is PARSED, not decorative ...
    never delete it (2026-08-12 audit deleted it as a stale fact and broke the parser)". If that
    parse can break without the gate noticing, this narrowing traded a slow gate for a blind one.
    """
    selected = set(gate.select_targets(["CLAUDE.md"]))
    for owed in ("tests/tools/test_generate_dashboard_data.py",
                 "tests/tools/test_generate_project_state.py",
                 "tests/tools/test_claude_md_integrity.py"):
        assert owed in selected, "{} is no longer selected by a CLAUDE.md edit".format(owed)


def test_an_ordinary_data_file_is_STILL_derived_not_curated():
    """The narrowing must reach the rulebook and stop there. A config a module actually loads
    keeps the derived sweep, which is the behaviour the whole data surface exists for."""
    assert gate.data_surface_tests("background/process_manifest.yaml") != []
    assert "background/process_manifest.yaml" not in gate.CURATED_SURFACE_PATHS


# ---------------------------------------------------------------------------
# A FULL RULEBOOK IS A REFUSAL, NOT A STALL (2026-08-27)
# ---------------------------------------------------------------------------
# Director: "a commit refused because the file is full should say so, not look like a stalled
# session. That single confusion has cost us days of my attention across the last fortnight."
#
# The rule was already enforced -- `test_real_claude_md_within_hard_limit` is on
# CANON_SURFACE_TESTS and reds. But it reds as a pytest assertion inside a gate run of several
# minutes, so from outside the only symptom is a session that went quiet. A refusal that cannot
# be told apart from a hang is the same shape as a waiter whose subject has died (R18), and it
# costs the same thing: somebody's attention, spent working out whether anything is happening.

def test_a_canon_file_over_its_limit_is_refused_and_the_file_is_NAMED(monkeypatch):
    from background import claude_md_integrity as integrity
    monkeypatch.setattr(integrity, "MAX_CHARS", 100)
    ok, detail = gate._canon_size_check(["CLAUDE.md"])
    assert ok is False
    assert "CLAUDE.md" in detail
    assert "over the" in detail, "the refusal must say BY HOW MUCH, not merely that it failed"


def test_a_healthy_rulebook_passes():
    """The partner. A check that refused unconditionally would stop every commit that touches
    CLAUDE.md, which is every rule change."""
    assert gate._canon_size_check(["CLAUDE.md"]) == (True, "")


def test_a_commit_that_does_not_touch_the_rulebook_is_not_checked(monkeypatch):
    """Scope. A full rulebook must not refuse a commit that has nothing to do with it -- the
    gate would then be unbypassable for everyone until somebody made room."""
    from background import claude_md_integrity as integrity
    monkeypatch.setattr(integrity, "MAX_CHARS", 100)
    assert gate._canon_size_check(["tools/wait_for.py"]) == (True, "")


def test_an_unreadable_canon_file_FAILS_CLOSED(monkeypatch, tmp_path):
    """A canon file the gate cannot READ is not thereby within its limit. Same standing rule as
    the landing checkers, learned the expensive way."""
    monkeypatch.setattr(gate, "ROOT", tmp_path)  # CLAUDE.md does not exist here
    ok, detail = gate._canon_size_check(["CLAUDE.md"])
    assert ok is False
    assert "could not be read" in detail


def test_the_size_is_measured_on_the_TREE_THE_COMMIT_CREATES_not_the_working_one():
    """`ROOT`, not `claude_md_integrity.PROJECT_DIR`, and the difference is the whole gate.

    `surgical_land` runs this inside a throwaway checkout of the tree the commit WOULD create;
    `PROJECT_DIR` is pinned to the real working tree. Measuring the second would let a commit
    that trims CLAUDE.md be refused for the untrimmed copy still on disk -- and, worse, let a
    commit that BLOATS it pass because the working copy happened to be clean. The first draft of
    this check used PROJECT_DIR and would have done exactly that, on top of not importing at all
    inside the checkout.
    """
    import inspect
    src = inspect.getsource(gate._canon_size_check)
    assert "path = ROOT / rel" in src
    assert "PROJECT_DIR" not in src


def test_the_banner_says_it_is_a_refusal_and_not_a_hang():
    """THE DIRECTOR'S ACTUAL ASK, asserted rather than assumed. The wording IS the deliverable."""
    banner = gate.rulebook_full_banner("  - CLAUDE.md is 35,190 chars")
    assert "REFUSAL, not a hang" in banner
    assert "no test failed" in banner


def test_the_banner_forbids_raising_the_limit_and_names_the_decay_audit():
    """The remedy has to travel with the refusal, or the next reader reaches for the ceiling --
    which is the move the director ruled out by name."""
    banner = gate.rulebook_full_banner("  - CLAUDE.md is 35,190 chars")
    assert "DO NOT RAISE THE LIMIT" in banner
    assert "python3 -m background.claude_md_integrity" in banner


def test_the_banner_carries_the_measurement_it_was_given():
    """A banner that dropped its detail would tell a reader the file is full and not which file
    or by how much."""
    assert "35,190 chars" in gate.rulebook_full_banner("  - CLAUDE.md is 35,190 chars")
