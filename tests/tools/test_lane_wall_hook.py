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


def _run(payload: dict, env: dict | None = None) -> subprocess.CompletedProcess:
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
        cwd=REPO_ROOT,
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
        assert "SE_LANE=supplier" in result.stderr

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
        assert "SE_LANE=sim" in result.stderr

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
