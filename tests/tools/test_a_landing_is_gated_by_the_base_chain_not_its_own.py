"""GAP-2 of `docs/market_research/gates_judged_from_the_base_2026-11-20.md`: the chain a landing
faces is HEAD's blob of `tools/git-hooks/pre-commit`, never the change's own copy.

THE DEFECT EACH TEST NAMES. Until 27 Nov `surgical_land.run_gate` ran `sh <hook>` from the extract,
i.e. the hook the CHANGE carries. A change that deleted a line of the chain -- the base-judged
enforce line above all -- was therefore judged without that line on its own landing, and the
judge it silenced was the one that exists to catch exactly that.

  * `test_deleting_a_refusing_line_from_the_hook_does_not_silence_it_for_its_own_landing`
    reds if `run_gate` runs the extract's copy again (mutation: `["sh", hook_rel]`).
  * `test_a_base_with_no_hook_blob_refuses_rather_than_running_the_changes_copy` reds if the
    missing-blob branch falls back to the change's file (the FAIL-OPEN direction).
  * `test_the_base_hook_is_not_left_inside_the_checkout` reds if the blob is written into the
    tree, where every staging/tree-reading gate would see an untracked file.
  * `test_a_non_repo_checkout_still_runs_its_own_file` keeps the bare `hook.sh` unit path alive
    (the other run_gate tests depend on it); it is a contract, not a control.
"""
from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path

import pytest

from tools import surgical_land as sl

HOOK_REL = "tools/git-hooks/pre-commit"

BASE_HOOK = textwrap.dedent(
    """\
    #!/bin/sh
    if [ "$(cat gate_verdict)" = "red" ]; then
        echo "the BASE chain refuses: gate_verdict is red"
        exit 1
    fi
    echo "1 passed"
    """
)

WEAKENED_HOOK = "#!/bin/sh\necho '1 passed'\n"

MSG_HOOK = "#!/bin/sh\nexit 0\n"


def _run(repo: Path, *args: str) -> subprocess.CompletedProcess:
    r = subprocess.run(args, cwd=str(repo), capture_output=True, text=True)
    assert r.returncode == 0, "{} failed: {}".format(args, r.stderr)
    return r


def _repo(tmp_path: Path, with_hook: bool = True) -> Path:
    r = tmp_path / "repo"
    (r / "tools" / "git-hooks").mkdir(parents=True)
    _run(r.parent, "git", "init", "-q", "-b", "main", str(r))
    _run(r, "git", "config", "user.email", "t@example.com")
    _run(r, "git", "config", "user.name", "T")
    if with_hook:
        (r / HOOK_REL).write_text(BASE_HOOK)
    (r / "tools" / "git-hooks" / "commit-msg").write_text(MSG_HOOK)
    (r / "gate_verdict").write_text("green")
    _run(r, "git", "add", "-A")
    _run(r, "git", "commit", "-q", "--no-verify", "-m", "base")
    return r


def _head(repo: Path) -> str:
    return _run(repo, "git", "rev-parse", "HEAD").stdout.strip()


def test_deleting_a_refusing_line_from_the_hook_does_not_silence_it_for_its_own_landing(
        tmp_path: Path):
    repo = _repo(tmp_path)
    (repo / HOOK_REL).write_text(WEAKENED_HOOK)
    (repo / "gate_verdict").write_text("red")
    before = _head(repo)

    with pytest.raises(sl.LandingRefused, match="BASE chain refuses"):
        sl.land(repo, [HOOK_REL, "gate_verdict"], "weaken the chain and land red under it")

    assert _head(repo) == before


def test_a_hook_change_still_lands_when_the_base_chain_passes_it(tmp_path: Path):
    """Not vacuous: the same weakening on a green tree lands, so the refusal above is the base
    chain reading the red verdict and not the tool refusing every hook edit."""
    repo = _repo(tmp_path)
    (repo / HOOK_REL).write_text(WEAKENED_HOOK)
    before = _head(repo)

    sha = sl.land(repo, [HOOK_REL], "edit the chain on a green tree")

    assert sha != before


def test_a_base_with_no_hook_blob_refuses_rather_than_running_the_changes_copy(tmp_path: Path):
    repo = _repo(tmp_path, with_hook=False)
    (repo / HOOK_REL).write_text(WEAKENED_HOOK)
    before = _head(repo)

    with pytest.raises(sl.LandingRefused, match="UNAVAILABLE.*read from HEAD"):
        sl.land(repo, [HOOK_REL], "introduce a chain the base never had")

    assert _head(repo) == before


def test_the_base_hook_is_not_left_inside_the_checkout(tmp_path: Path):
    repo = _repo(tmp_path)
    (repo / HOOK_REL).write_text(
        "#!/bin/sh\n"
        "[ -z \"$(git status --porcelain --untracked-files=all)\" ] || {\n"
        "  echo \"untracked in the checkout: $(git status --porcelain)\"; exit 1; }\n"
        "echo '1 passed'\n")
    _run(repo, "git", "add", "-A")
    _run(repo, "git", "commit", "-q", "--no-verify", "-m", "a hook that reads the checkout")
    checkout = tmp_path / "extract"
    subprocess.run(["git", "clone", "-q", str(repo), str(checkout)], check=True)

    rc, out, _err = sl.run_gate(checkout, HOOK_REL)

    assert rc == 0, out


def test_a_non_repo_checkout_still_runs_its_own_file(tmp_path: Path):
    (tmp_path / "hook.sh").write_text("#!/bin/sh\necho ran-the-file\n")

    rc, out, _err = sl.run_gate(tmp_path, "hook.sh")

    assert rc == 0 and "ran-the-file" in out
