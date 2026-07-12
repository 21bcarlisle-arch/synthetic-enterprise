"""Tests for .claude/hooks/lane_wall_hook.py.

GOVERNED_COMPANY_AND_THREE_LANES.md Part 2 item 1 (pilot, 2026-07-12):
deny cross-wall reads by lane, extending the epistemic wall from runtime
into development. Same real-subprocess-invocation convention as
tests/tools/test_claude_hooks.py.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LANE_WALL_HOOK = REPO_ROOT / ".claude" / "hooks" / "lane_wall_hook.py"
DENIAL_LOG = REPO_ROOT / "docs" / "observability" / "lane_hook_denials.jsonl"


def _run(
    payload: dict, env: dict | None = None, cwd: Path | None = None
) -> subprocess.CompletedProcess:
    import os

    full_env = dict(os.environ)
    full_env.pop("SE_LANE", None)  # never inherit the real session's own lane, if any
    if env:
        full_env.update(env)
    return subprocess.run(
        [sys.executable, str(LANE_WALL_HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd is not None else REPO_ROOT,
        env=full_env,
    )


@pytest.fixture(autouse=True)
def _clean_denial_log():
    """Each test starts and ends with no denial log -- restores whatever
    was there before (or removes it if it didn't exist) so this test file
    doesn't leave permanent evidence artifacts from arbitrary test runs."""
    original = DENIAL_LOG.read_text() if DENIAL_LOG.exists() else None
    if DENIAL_LOG.exists():
        DENIAL_LOG.unlink()
    yield
    if DENIAL_LOG.exists():
        DENIAL_LOG.unlink()
    if original is not None:
        DENIAL_LOG.parent.mkdir(parents=True, exist_ok=True)
        DENIAL_LOG.write_text(original)


class TestLaneWallHook:
    def test_noop_when_se_lane_unset(self):
        result = _run({"tool_name": "Read", "tool_input": {"file_path": "sim/forward_curve.py"}})
        assert result.returncode == 0
        assert not DENIAL_LOG.exists()

    def test_noop_when_se_lane_unrecognized(self):
        result = _run(
            {"tool_name": "Read", "tool_input": {"file_path": "sim/forward_curve.py"}},
            env={"SE_LANE": "not_a_real_lane"},
        )
        assert result.returncode == 0

    def test_supplier_lane_denies_sim_read(self):
        result = _run(
            {"tool_name": "Read", "tool_input": {"file_path": "sim/forward_curve.py"}},
            env={"SE_LANE": "supplier"},
        )
        assert result.returncode == 2
        assert "DENIED" in result.stderr
        assert "lane=supplier" in result.stderr

    def test_supplier_lane_denies_simulation_read(self):
        result = _run(
            {"tool_name": "Read", "tool_input": {"file_path": "simulation/renewals.py"}},
            env={"SE_LANE": "supplier"},
        )
        assert result.returncode == 2

    def test_supplier_lane_allows_company_read(self):
        result = _run(
            {"tool_name": "Read", "tool_input": {"file_path": "company/pricing/tariff_engine.py"}},
            env={"SE_LANE": "supplier"},
        )
        assert result.returncode == 0

    def test_sim_lane_denies_company_read(self):
        result = _run(
            {"tool_name": "Read", "tool_input": {"file_path": "company/pricing/tariff_engine.py"}},
            env={"SE_LANE": "sim"},
        )
        assert result.returncode == 2
        assert "lane=sim" in result.stderr

    def test_sim_lane_denies_saas_read(self):
        result = _run(
            {"tool_name": "Read", "tool_input": {"file_path": "saas/bill_generator.py"}},
            env={"SE_LANE": "sim"},
        )
        assert result.returncode == 2

    def test_sim_lane_allows_sim_read(self):
        result = _run(
            {"tool_name": "Read", "tool_input": {"file_path": "sim/forward_curve.py"}},
            env={"SE_LANE": "sim"},
        )
        assert result.returncode == 0

    def test_denies_grep_by_path(self):
        result = _run(
            {"tool_name": "Grep", "tool_input": {"pattern": "def foo", "path": "sim/forward_curve.py"}},
            env={"SE_LANE": "supplier"},
        )
        assert result.returncode == 2

    def test_denies_glob_by_path(self):
        result = _run(
            {"tool_name": "Glob", "tool_input": {"pattern": "*.py", "path": "simulation/"}},
            env={"SE_LANE": "supplier"},
        )
        assert result.returncode == 2

    def test_ignores_non_path_tool(self):
        result = _run(
            {"tool_name": "Bash", "tool_input": {"command": "cat sim/forward_curve.py"}},
            env={"SE_LANE": "supplier"},
        )
        assert result.returncode == 0, "Bash is out of scope for this pilot -- Read/Grep/Glob only"

    def test_ignores_malformed_json(self):
        result = subprocess.run(
            [sys.executable, str(LANE_WALL_HOOK)],
            input="not json",
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0

    def test_denial_is_logged(self):
        assert not DENIAL_LOG.exists()
        _run(
            {"tool_name": "Read", "tool_input": {"file_path": "sim/forward_curve.py"}},
            env={"SE_LANE": "supplier"},
        )
        assert DENIAL_LOG.exists()
        entry = json.loads(DENIAL_LOG.read_text().strip().splitlines()[-1])
        assert entry["lane"] == "supplier"
        assert entry["tool_name"] == "Read"
        assert entry["path"] == "sim/forward_curve.py"

    def test_allowed_calls_are_not_logged(self):
        _run(
            {"tool_name": "Read", "tool_input": {"file_path": "company/pricing/tariff_engine.py"}},
            env={"SE_LANE": "supplier"},
        )
        assert not DENIAL_LOG.exists()

    # --- REGULATION_COMMONS_DOCTRINE.md (2026-07-12): the commons is shared ---

    def test_domain_artefact_library_readable_from_supplier_lane(self):
        result = _run(
            {"tool_name": "Read", "tool_input": {"file_path": "docs/domain_artefact_library/INDEX.md"}},
            env={"SE_LANE": "supplier"},
        )
        assert result.returncode == 0

    def test_domain_artefact_library_readable_from_sim_lane(self):
        result = _run(
            {"tool_name": "Read", "tool_input": {"file_path": "docs/domain_artefact_library/INDEX.md"}},
            env={"SE_LANE": "sim"},
        )
        assert result.returncode == 0

    def test_shared_readable_paths_never_match_either_lane_deny_pattern(self):
        """Regression guard: a future edit to either deny regex must not
        accidentally start matching a path this doctrine names as commons."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("lane_wall_hook", LANE_WALL_HOOK)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for path in module.SHARED_READABLE:
            for lane, pattern in module._LANE_DENIES.items():
                assert not pattern.match(path.lstrip("./")), (
                    f"{path!r} must stay shared-readable but matches lane {lane!r}'s deny pattern"
                )


# --- PARALLEL_LANES_PROPOSAL.md §3.1: marker-file lane-keying evolution ---


class TestMarkerFileLaneKeying:
    def test_marker_file_activates_supplier_lane(self, tmp_path):
        (tmp_path / ".se_lane").write_text("supplier")
        result = _run(
            {"tool_name": "Read", "tool_input": {"file_path": "sim/forward_curve.py"}},
            cwd=tmp_path,
        )
        assert result.returncode == 2
        assert "lane=supplier" in result.stderr

    def test_marker_file_activates_sim_lane(self, tmp_path):
        (tmp_path / ".se_lane").write_text("sim")
        result = _run(
            {"tool_name": "Read", "tool_input": {"file_path": "company/pricing/tariff_engine.py"}},
            cwd=tmp_path,
        )
        assert result.returncode == 2

    def test_marker_file_allows_own_side(self, tmp_path):
        (tmp_path / ".se_lane").write_text("supplier")
        result = _run(
            {"tool_name": "Read", "tool_input": {"file_path": "company/pricing/tariff_engine.py"}},
            cwd=tmp_path,
        )
        assert result.returncode == 0

    def test_no_marker_file_is_a_noop(self, tmp_path):
        result = _run(
            {"tool_name": "Read", "tool_input": {"file_path": "sim/forward_curve.py"}},
            cwd=tmp_path,
        )
        assert result.returncode == 0

    def test_marker_file_with_unrecognized_lane_is_a_noop(self, tmp_path):
        (tmp_path / ".se_lane").write_text("not_a_real_lane")
        result = _run(
            {"tool_name": "Read", "tool_input": {"file_path": "sim/forward_curve.py"}},
            cwd=tmp_path,
        )
        assert result.returncode == 0

    def test_marker_file_content_is_stripped_of_whitespace(self, tmp_path):
        (tmp_path / ".se_lane").write_text("supplier\n")
        result = _run(
            {"tool_name": "Read", "tool_input": {"file_path": "sim/forward_curve.py"}},
            cwd=tmp_path,
        )
        assert result.returncode == 2

    def test_env_var_wins_when_both_env_and_marker_file_present(self, tmp_path):
        # Marker says sim, env var says supplier -- env var is the more
        # explicit signal and must win.
        (tmp_path / ".se_lane").write_text("sim")
        result = _run(
            {"tool_name": "Read", "tool_input": {"file_path": "sim/forward_curve.py"}},
            env={"SE_LANE": "supplier"},
            cwd=tmp_path,
        )
        assert result.returncode == 2
        assert "lane=supplier" in result.stderr


# --- HARDEN pass (2026-07-12, adversarial red-team): 7 confirmed findings ---


class TestHardenPassFixes:
    def test_absolute_path_bypass_now_denied(self):
        # Finding 1 (most severe): Claude Code's own Read tool spec requires
        # absolute paths -- the old lstrip("./") normalization never
        # touched an absolute path at all, so this was likely dead on
        # arrival against real Read calls, not a contrived edge case.
        abs_path = str(REPO_ROOT / "company" / "pricing" / "tariff_engine.py")
        result = _run(
            {"tool_name": "Read", "tool_input": {"file_path": abs_path}},
            env={"SE_LANE": "sim"},
        )
        assert result.returncode == 2

    def test_directory_traversal_bypass_now_denied(self):
        # Finding 2: a ".."-traversal that resolves back into denied
        # territory, including one disguised behind the commons doctrine's
        # own shared-readable prefix.
        result = _run(
            {"tool_name": "Read", "tool_input": {"file_path": "docs/../company/pricing/tariff_engine.py"}},
            env={"SE_LANE": "sim"},
        )
        assert result.returncode == 2

    def test_traversal_disguised_behind_shared_readable_prefix_denied(self):
        result = _run(
            {
                "tool_name": "Read",
                "tool_input": {
                    "file_path": "docs/domain_artefact_library/../../company/pricing/tariff_engine.py"
                },
            },
            env={"SE_LANE": "sim"},
        )
        assert result.returncode == 2

    def test_case_sensitivity_bypass_now_denied(self):
        # Finding 4.
        result = _run(
            {"tool_name": "Read", "tool_input": {"file_path": "Sim/forward_curve.py"}},
            env={"SE_LANE": "supplier"},
        )
        assert result.returncode == 2
        result2 = _run(
            {"tool_name": "Read", "tool_input": {"file_path": "SIMULATION/renewals.py"}},
            env={"SE_LANE": "supplier"},
        )
        assert result2.returncode == 2

    def test_glob_pattern_only_no_path_key_now_checked(self):
        # Finding 3: Glob's own `pattern` (path-shaped) is now inspected,
        # not just `path`.
        result = _run(
            {"tool_name": "Glob", "tool_input": {"pattern": "sim/**/*.py"}},
            env={"SE_LANE": "supplier"},
        )
        assert result.returncode == 2

    def test_grep_with_explicit_dot_path_denied_outright(self):
        # Finding 3 continued: an explicit "." path is equivalent to no
        # scoping at all and must be denied outright while a lane is active.
        result = _run(
            {"tool_name": "Grep", "tool_input": {"pattern": "forward_curve", "path": "."}},
            env={"SE_LANE": "supplier"},
        )
        assert result.returncode == 2

    def test_grep_with_no_path_at_all_denied_outright(self):
        result = _run(
            {"tool_name": "Grep", "tool_input": {"pattern": "forward_curve"}},
            env={"SE_LANE": "supplier"},
        )
        assert result.returncode == 2

    def test_grep_with_real_scoped_path_still_correctly_checked(self):
        # An explicitly-scoped Grep into the ALLOWED side must still pass.
        result = _run(
            {"tool_name": "Grep", "tool_input": {"pattern": "def foo", "path": "company/"}},
            env={"SE_LANE": "supplier"},
        )
        assert result.returncode == 0

    def test_garbage_env_var_no_longer_nullifies_a_valid_marker_file(self, tmp_path):
        # Finding 5: truthiness, not validity, previously decided
        # precedence -- a typo'd/leftover SE_LANE silently beat a
        # well-formed marker file with zero signal.
        (tmp_path / ".se_lane").write_text("supplier")
        result = _run(
            {"tool_name": "Read", "tool_input": {"file_path": "sim/forward_curve.py"}},
            env={"SE_LANE": "typo_lane"},
            cwd=tmp_path,
        )
        assert result.returncode == 2

    def test_marker_file_mixed_case_now_matches(self, tmp_path):
        # Finding 6.
        (tmp_path / ".se_lane").write_text("Supplier")
        result = _run(
            {"tool_name": "Read", "tool_input": {"file_path": "sim/forward_curve.py"}},
            cwd=tmp_path,
        )
        assert result.returncode == 2

    def test_marker_file_with_extra_line_no_longer_corrupts_lookup(self, tmp_path):
        # Finding 6 continued: only the first line is read.
        (tmp_path / ".se_lane").write_text("supplier\nextra_garbage_line")
        result = _run(
            {"tool_name": "Read", "tool_input": {"file_path": "sim/forward_curve.py"}},
            cwd=tmp_path,
        )
        assert result.returncode == 2

    def test_unreadable_marker_file_still_fails_open_but_now_warns(self, tmp_path):
        # Finding 7: still fails open (this is a soft dev-time pilot, not
        # the runtime wall) but now logs a visible warning rather than
        # silently swallowing the error.
        marker = tmp_path / ".se_lane"
        marker.write_text("supplier")
        marker.chmod(0o000)
        try:
            result = _run(
                {"tool_name": "Read", "tool_input": {"file_path": "sim/forward_curve.py"}},
                cwd=tmp_path,
            )
            assert result.returncode == 0  # still fails open by design
            assert "WARNING" in result.stderr
        finally:
            marker.chmod(0o644)  # restore so tmp_path cleanup can remove it
