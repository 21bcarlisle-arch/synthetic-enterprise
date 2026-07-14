"""Tests for the PreToolUse lifecycle hooks in .claude/hooks/.

HARNESS_BEST_PRACTICE_ADOPTION.md item 1: sudo ban (1b), the unevidenced-
claim pixel rule (1c), and the point-in-time-read flag (1a, director-
authorized 2026-07-10). Each hook is a standalone script reading a Claude
Code PreToolUse JSON payload on stdin and signalling block via exit code 2
(per the verified real hooks schema, docs/design/
HARNESS_BEST_PRACTICE_ASSESSMENT.md).
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BLOCK_SUDO = REPO_ROOT / ".claude" / "hooks" / "block_sudo.py"
BLOCK_CLAIM = REPO_ROOT / ".claude" / "hooks" / "block_unevidenced_claim.py"
BLOCK_PIT_READ = REPO_ROOT / ".claude" / "hooks" / "block_point_in_time_read.py"


def _run(script: Path, payload: dict, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=cwd,
    )


class TestBlockSudo:
    def test_blocks_plain_sudo(self):
        result = _run(BLOCK_SUDO, {"tool_name": "Bash", "tool_input": {"command": "sudo apt-get install foo"}})
        assert result.returncode == 2
        assert "sudo is banned" in result.stderr

    def test_blocks_sudo_after_chain_operator(self):
        result = _run(BLOCK_SUDO, {"tool_name": "Bash", "tool_input": {"command": "cd /tmp && sudo rm -rf /"}})
        assert result.returncode == 2

    def test_allows_normal_command(self):
        result = _run(BLOCK_SUDO, {"tool_name": "Bash", "tool_input": {"command": "ls -la"}})
        assert result.returncode == 0
        assert result.stderr == ""

    def test_allows_word_containing_sudo_substring(self):
        # "pseudocode" contains "sudo" as a substring but not as a command word.
        result = _run(BLOCK_SUDO, {"tool_name": "Bash", "tool_input": {"command": "echo pseudocode"}})
        assert result.returncode == 0

    def test_ignores_non_bash_tool(self):
        result = _run(BLOCK_SUDO, {"tool_name": "Read", "tool_input": {"file_path": "sudo_readme.txt"}})
        assert result.returncode == 0

    def test_ignores_malformed_json(self):
        result = subprocess.run(
            [sys.executable, str(BLOCK_SUDO)],
            input="not json",
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0


def _git(cwd: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
        env={
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@t",
            "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_CONFIG_SYSTEM": "/dev/null",
            "PATH": __import__("os").environ.get("PATH", ""),
            "HOME": str(cwd),
        },
    )
    return proc.stdout.strip()


@pytest.fixture
def git_repo(tmp_path):
    """A working repo with an origin remote.

    Yields (work_dir, pushed_sha, unpushed_sha) where:
      * pushed_sha IS reachable on origin/main (genuinely published)
      * unpushed_sha is committed locally but NOT on origin
    This lets a mutation test prove the hook fires on its named defect
    (a false claim citing a commit that never reached origin).
    """
    origin = tmp_path / "origin.git"
    work = tmp_path / "work"
    origin.mkdir()
    work.mkdir()
    _git(origin, "init", "--bare", "-b", "main")
    _git(work, "init", "-b", "main")
    _git(work, "remote", "add", "origin", str(origin))
    (work / "a.txt").write_text("a\n")
    _git(work, "add", "a.txt")
    _git(work, "commit", "-m", "first")
    _git(work, "push", "origin", "main")
    _git(work, "fetch", "origin")
    pushed_sha = _git(work, "rev-parse", "HEAD")
    # A second commit that is committed locally but never pushed.
    (work / "b.txt").write_text("b\n")
    _git(work, "add", "b.txt")
    _git(work, "commit", "-m", "second (unpushed)")
    unpushed_sha = _git(work, "rev-parse", "HEAD")
    yield work, pushed_sha, unpushed_sha


def _ntfy(message: str) -> dict:
    cmd = (
        "python3 -c \"from background.ntfy_utils import send_ntfy; "
        f"send_ntfy('{message}')\""
    )
    return {"tool_name": "Bash", "tool_input": {"command": cmd}}


class TestBlockUnevidencedClaim:
    # --- R15 MUTATION TEST: the control must FAIL on its named defect --------
    def test_passes_claim_citing_sha_genuinely_on_origin(self, git_repo):
        """Legitimate case: the cited SHA really is on origin -> hook PASSES."""
        work, pushed_sha, _ = git_repo
        result = _run(BLOCK_CLAIM, _ntfy(f"Bug fixed and deployed, commit {pushed_sha}"), cwd=work)
        assert result.returncode == 0, result.stderr

    def test_blocks_claim_citing_sha_not_on_origin(self, git_repo):
        """MUTATION: a claim citing a committed-but-unpushed SHA is the named
        defect (false 'fixed/deployed'). The hook MUST fire -- proves it is
        not a tautology satisfiable by a local artifact the agent controls."""
        work, _, unpushed_sha = git_repo
        result = _run(BLOCK_CLAIM, _ntfy(f"Bug fixed and deployed, commit {unpushed_sha}"), cwd=work)
        assert result.returncode == 2
        assert "origin" in result.stderr

    def test_blocks_claim_citing_bogus_sha(self, git_repo):
        """A fabricated SHA is not a real object on origin -> BLOCK."""
        work, _, _ = git_repo
        result = _run(BLOCK_CLAIM, _ntfy("Fixed and confirmed live, commit deadbeefcafe1234"), cwd=work)
        assert result.returncode == 2

    def test_blocks_claim_with_no_sha(self, git_repo):
        """Claim word but no verifiable evidence token -> fail closed."""
        work, _, _ = git_repo
        result = _run(BLOCK_CLAIM, _ntfy("Bug fixed and confirmed live"), cwd=work)
        assert result.returncode == 2
        assert "commit SHA" in result.stderr

    def test_blocks_when_no_origin_ref_resolvable(self, tmp_path):
        """FAIL-SILENT guard: if the origin tracking ref cannot be resolved
        (check unavailable) the hook must BLOCK, never pass by default."""
        lonely = tmp_path / "lonely"
        lonely.mkdir()
        _git(lonely, "init", "-b", "main")
        (lonely / "x.txt").write_text("x\n")
        _git(lonely, "add", "x.txt")
        _git(lonely, "commit", "-m", "only")
        sha = _git(lonely, "rev-parse", "HEAD")  # a real local commit, but no origin
        result = _run(BLOCK_CLAIM, _ntfy(f"Fixed and live, commit {sha}"), cwd=lonely)
        assert result.returncode == 2

    # --- pass-through behaviour (unchanged contract on non-claims) -----------
    def test_allows_non_claim_ntfy_message(self, git_repo):
        work, _, _ = git_repo
        result = _run(BLOCK_CLAIM, _ntfy("Status update: still investigating"), cwd=work)
        assert result.returncode == 0

    def test_ignores_non_send_ntfy_bash_command(self, git_repo):
        work, _, _ = git_repo
        cmd = "echo 'this is fixed and live'"
        result = _run(BLOCK_CLAIM, {"tool_name": "Bash", "tool_input": {"command": cmd}}, cwd=work)
        assert result.returncode == 0

    def test_ignores_non_bash_tool(self):
        result = _run(BLOCK_CLAIM, {"tool_name": "Write", "tool_input": {"content": "fixed and live"}})
        assert result.returncode == 0

    def test_allows_prose_describing_send_ntfy_without_calling_it(self):
        # Regression: a git commit message *describing* the hook (e.g. "blocks
        # a send_ntfy() call claiming fixed/live/deployed") must not itself
        # trip the hook -- it never imports or invokes send_ntfy for real.
        cmd = (
            "git commit -m 'Add hook that blocks a send_ntfy() call claiming "
            "fixed/live/deployed/confirmed/verified unless evidence exists'"
        )
        result = _run(BLOCK_CLAIM, {"tool_name": "Bash", "tool_input": {"command": cmd}})
        assert result.returncode == 0


class TestBlockPointInTimeRead:
    def test_flags_all_records_in_company_file_without_as_of_bound(self):
        result = _run(BLOCK_PIT_READ, {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "company/finance/example.py",
                "content": "def compute(all_records):\n    return sum(r['revenue_gbp'] for r in all_records)\n",
            },
        })
        assert result.returncode == 2
        assert "hedge-volatility bug" in result.stderr

    def test_flags_run_settlement_call_in_saas_file(self):
        result = _run(BLOCK_PIT_READ, {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "saas/reporting/example.py",
                "old_string": "pass",
                "new_string": "records = run_settlement(start, end)\n",
            },
        })
        assert result.returncode == 2

    def test_allows_when_as_of_bound_present(self):
        result = _run(BLOCK_PIT_READ, {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "company/finance/example.py",
                "content": (
                    "def compute(all_records, as_of_date):\n"
                    "    bounded = bisect_slice(all_records, as_of_date)\n"
                    "    return sum(r['revenue_gbp'] for r in bounded)\n"
                ),
            },
        })
        assert result.returncode == 0

    def test_allows_when_bisect_evidence_present(self):
        result = _run(BLOCK_PIT_READ, {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "company/finance/example.py",
                "content": "records = bisect.bisect_right(all_records, cutoff)\n",
            },
        })
        assert result.returncode == 0

    def test_ignores_files_outside_company_saas(self):
        result = _run(BLOCK_PIT_READ, {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "simulation/run_phase2b.py",
                "content": "def compute(all_records):\n    return sum(r['revenue_gbp'] for r in all_records)\n",
            },
        })
        assert result.returncode == 0

    def test_ignores_non_edit_write_tool(self):
        result = _run(BLOCK_PIT_READ, {
            "tool_name": "Bash",
            "tool_input": {"command": "cat company/finance/example.py"},
        })
        assert result.returncode == 0

    def test_ignores_content_without_dangerous_pattern(self):
        result = _run(BLOCK_PIT_READ, {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "company/finance/example.py",
                "content": "def compute(bills):\n    return sum(b['total_amount_gbp'] for b in bills)\n",
            },
        })
        assert result.returncode == 0

    def test_ignores_malformed_json(self):
        result = subprocess.run(
            [sys.executable, str(BLOCK_PIT_READ)],
            input="not json",
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0
