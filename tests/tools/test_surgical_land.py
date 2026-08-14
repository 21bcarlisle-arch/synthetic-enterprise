"""R15 contract for the surgical-landing tool (atom OPS4).

WHY THESE TESTS AND NOT OTHERS. The tool's whole claim is that it makes "bypass" unnecessary,
so the only interesting question is whether it can FAIL. A landing tool that quietly commits
when its gate is missing, or when the gate is red, is strictly worse than the bypass it
replaces -- it launders an ungated commit as a gated one. So every check here fires on the
tool's OWN named defect (R15 doctrine: TAUTOLOGY / FAIL-OPEN / FAIL-SILENT), and the
happy-path test exists mainly to prove the failing tests are not vacuously passing.

The fixture is a real throwaway git repo with its own `tools/git-hooks/pre-commit`, because
every property under test is a property of git's actual behaviour (index isolation, tree
construction, ref compare-and-swap) and a mocked git would prove nothing about any of them.

THE DEFECT THIS TOOL EXISTS TO CATCH is reproduced literally in
`test_a_partial_landing_is_gated_on_the_commit_not_the_working_tree`: a two-part change whose
committed half is red and whose working tree is green. That is the 2026-08-09 wedge in
miniature, and it is the one test that would still pass if the tool merely shelled out to
`git commit -- <paths>`, so it is written to distinguish the two.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

import pytest

from tools import surgical_land as sl

# A hook that reads a marker file IN THE TREE IT IS RUN AGAINST. That indirection is the whole
# point: it lets a test make the working tree green and the resulting tree red at the same time,
# which no gate reading only the working tree can distinguish.
HOOK = textwrap.dedent(
    """\
    #!/bin/sh
    if [ -f gate_verdict ] && [ "$(cat gate_verdict)" = "red" ]; then
        echo "1 failed, 0 passed"
        exit 1
    fi
    echo "3 passed in 0.01s"
    exit 0
    """
)


def _run(repo: Path, *args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    r = subprocess.run(args, cwd=str(repo), capture_output=True, text=True, input=stdin)
    assert r.returncode == 0, "{} failed: {}".format(args, r.stderr)
    return r


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    r = tmp_path / "repo"
    (r / "tools" / "git-hooks").mkdir(parents=True)
    _run(r.parent, "git", "init", "-q", "-b", "main", str(r))
    _run(r, "git", "config", "user.email", "t@example.com")
    _run(r, "git", "config", "user.name", "T")
    (r / "tools" / "git-hooks" / "pre-commit").write_text(HOOK)
    (r / "gate_verdict").write_text("green")
    (r / "code.py").write_text("VALUE = 1\n")
    (r / "other_lane.txt").write_text("another lane's work\n")
    _run(r, "git", "add", "-A")
    _run(r, "git", "commit", "-q", "-m", "base")
    return r


def _head(repo: Path) -> str:
    return _run(repo, "git", "rev-parse", "HEAD").stdout.strip()


def _index_blob(repo: Path, path: str) -> str:
    """The sha the REAL index holds for `path` -- the byte-level thing a landing must not move
    for anyone else's file."""
    out = _run(repo, "git", "ls-files", "-s", "--", path).stdout.strip()
    return out.split()[1] if out else ""


# --------------------------------------------------------------------------------------------
# It works at all (so the refusal tests below are not vacuous).
# --------------------------------------------------------------------------------------------

def test_a_green_landing_commits_exactly_the_named_paths(repo: Path):
    (repo / "code.py").write_text("VALUE = 2\n")
    (repo / "unrelated.py").write_text("NOT PART OF THIS LANDING\n")
    before = _head(repo)

    sha = sl.land(repo, ["code.py"], "land the code change")

    assert sha != before
    changed = _run(repo, "git", "diff", "--name-only", before, sha).stdout.split()
    assert changed == ["code.py"], "the landing swept in something it was not asked to commit"
    assert "NOT PART" not in _run(repo, "git", "show", sha + ":code.py").stdout
    assert (repo / "unrelated.py").read_text() == "NOT PART OF THIS LANDING\n", \
        "the working tree was mutated"


def test_the_landed_paths_are_clean_afterwards_so_the_next_commit_does_not_revert_them(
        repo: Path):
    """Leaving the index at the PARENT for a landed path is not neutrality -- it stages a
    revert, and the next commit undoes the landing. Same post-state as `git commit -- <paths>`."""
    (repo / "code.py").write_text("VALUE = 2\n")
    sl.land(repo, ["code.py"], "land it")

    status = _run(repo, "git", "status", "--porcelain", "--", "code.py").stdout
    assert status.strip() == "", "code.py is not clean after landing: {!r}".format(status)


# --------------------------------------------------------------------------------------------
# THE DEFECT THE TOOL EXISTS FOR: gate the commit, not the tree.
# --------------------------------------------------------------------------------------------

def test_a_partial_landing_is_gated_on_the_commit_not_the_working_tree(repo: Path):
    """The 2026-08-09 wedge in miniature. `code.py` and `gate_verdict` are two halves of one
    change; landing only the half that makes the gate red must REFUSE, even though the working
    tree -- which contains both halves -- is green."""
    # HEAD carries the red marker; the fix for it sits UNSTAGED in the working tree.
    (repo / "gate_verdict").write_text("red")
    _run(repo, "git", "add", "gate_verdict")
    _run(repo, "git", "commit", "-q", "--no-verify", "-m", "HEAD is red")
    before = _head(repo)
    (repo / "gate_verdict").write_text("green")   # the unstaged half that makes the TREE green
    (repo / "code.py").write_text("VALUE = 2\n")  # the half about to be landed alone

    # The premise, asserted rather than assumed: a tree-scoped gate would admit this commit.
    assert subprocess.run(["sh", "tools/git-hooks/pre-commit"], cwd=str(repo),
                          capture_output=True).returncode == 0, \
        "premise broken -- the working tree must be GREEN for this test to mean anything"

    with pytest.raises(sl.LandingRefused, match="GATE RED"):
        sl.land(repo, ["code.py"], "land only the half that leaves HEAD red")
    assert _head(repo) == before, "a red resulting tree still produced a commit"


def test_it_refuses_and_commits_nothing_when_the_gate_is_red(repo: Path):
    (repo / "gate_verdict").write_text("red")
    (repo / "code.py").write_text("VALUE = 2\n")
    before = _head(repo)

    with pytest.raises(sl.LandingRefused, match="GATE RED"):
        sl.land(repo, ["code.py", "gate_verdict"], "should not land")

    assert _head(repo) == before


# --------------------------------------------------------------------------------------------
# FAIL-CLOSED: an unavailable check is a FAILED check.
# --------------------------------------------------------------------------------------------

def test_a_missing_gate_refuses_rather_than_landing_ungated(repo: Path):
    """The FAIL-SILENT direction. If this returned 0 the tool would launder ungated commits as
    gated ones -- strictly worse than the bypass it replaces."""
    (repo / "code.py").write_text("VALUE = 2\n")
    before = _head(repo)

    with pytest.raises(sl.LandingRefused, match="UNAVAILABLE"):
        sl.land(repo, ["code.py"], "no hook", hook_rel="tools/git-hooks/does-not-exist")

    assert _head(repo) == before


def test_deleting_the_hook_IN_THE_LANDING_is_caught_because_the_gate_runs_on_the_result(
        repo: Path):
    """A landing that removes the gate is judged by the tree it creates, where the gate is
    already gone -- so it refuses. A tool gating the WORKING TREE (which still has the hook)
    would happily commit away its own check."""
    (repo / "tools" / "git-hooks" / "pre-commit").unlink()
    before = _head(repo)

    with pytest.raises(sl.LandingRefused, match="UNAVAILABLE"):
        sl.land(repo, ["tools/git-hooks/pre-commit"], "remove the gate")

    assert _head(repo) == before


def test_it_refuses_a_no_op_rather_than_writing_an_empty_commit(repo: Path):
    with pytest.raises(sl.LandingRefused, match="nothing to land"):
        sl.land(repo, ["code.py"], "no change")


def test_it_refuses_an_empty_pathspec(repo: Path):
    with pytest.raises(sl.LandingRefused, match="names its paths explicitly"):
        sl.land(repo, [], "nothing named")


def _racing_gate(repo: Path, lose_until: int, calls: list[int]):
    """A gate that lands a colleague's commit from inside the gate call -- exactly when a real
    concurrent writer's commit arrives -- for the first `lose_until` attempts, then runs clean.

    Each colleague commit writes a DISTINCT file, so attempt N+1's race is a genuinely new HEAD
    move rather than an empty commit that git would refuse."""
    real_run_gate = sl.run_gate

    def gate(checkout, hook_rel=sl.HOOK_REL):
        calls.append(len(calls) + 1)
        rc, out = real_run_gate(checkout, hook_rel)
        if len(calls) <= lose_until:
            name = "colleague_{}.txt".format(len(calls))
            (repo / name).write_text("landed mid-gate\n")
            _run(repo, "git", "add", name)
            _run(repo, "git", "commit", "-q", "--no-verify", "-m", "colleague {}".format(
                len(calls)))
        return rc, out

    return gate


def test_head_moving_under_the_gate_refuses_instead_of_landing_a_stale_verdict(
        repo: Path, monkeypatch: pytest.MonkeyPatch):
    """The shared-tree race: a concurrent writer moves HEAD while the gate runs, so the gated
    tree is no longer the tree this commit would create. Simulated by moving HEAD from inside
    the gate call, which is exactly when a real colleague's commit would land.

    Pinned at `attempts=1` deliberately: this is the property of the compare-and-swap ITSELF,
    and it must stay assertable independently of how many times the retry loop above it spends."""
    (repo / "code.py").write_text("VALUE = 2\n")
    calls: list[int] = []
    monkeypatch.setattr(sl, "run_gate", _racing_gate(repo, lose_until=99, calls=calls))
    with pytest.raises(sl.LandingRefused, match="HEAD moved"):
        sl.land(repo, ["code.py"], "stale base", attempts=1)
    assert _run(repo, "git", "log", "-1", "--format=%s").stdout.strip() == "colleague 1", \
        "the stale-base landing overwrote the colleague's commit"
    assert calls == [1], "attempts=1 must run the gate exactly once"


# --------------------------------------------------------------------------------------------
# THE REFUSAL NEEDED A MOVE THAT TERMINATES
# (WORKER_FINDING_THE_LANDING_GATE_CANNOT_WIN_THE_RACE_AGAINST_HEAD_2026-08-13: three
# consecutive refusals, none for a red test, gate ~9m24s against a 3.5-10min HEAD cadence.)
#
# The retry is only defensible because of what it does NOT retry, so both halves are pinned:
# a lost race is recomputed, a red gate is final, and exhaustion commits nothing.
# --------------------------------------------------------------------------------------------

def test_a_lost_race_is_re_gated_against_the_new_base_and_lands(
        repo: Path, monkeypatch: pytest.MonkeyPatch):
    """The finding's own shape: HEAD moves under the first two gates, the third wins.

    The assertions that make this a repair rather than a loop: the gate ran ONCE PER ATTEMPT (no
    verdict was carried across a HEAD move), and the landed commit's parent is the COLLEAGUE'S
    commit -- so the mover's work is preserved by the retry, not reverted by it."""
    (repo / "code.py").write_text("VALUE = 2\n")
    calls: list[int] = []
    monkeypatch.setattr(sl, "run_gate", _racing_gate(repo, lose_until=2, calls=calls))

    sha = sl.land(repo, ["code.py"], "lands on the third", attempts=3)

    assert len(calls) == 3, "the gate must re-run per attempt, not be reused across a HEAD move"
    parent = _run(repo, "git", "rev-parse", sha + "^").stdout.strip()
    assert _run(repo, "git", "log", "-1", "--format=%s", parent).stdout.strip() == "colleague 2", \
        "the retry did not rebase onto the mover's commit"
    for n in (1, 2):
        assert (repo / "colleague_{}.txt".format(n)).exists(), "the retry reverted the mover"
        assert _run(repo, "git", "cat-file", "-e",
                    "{}:colleague_{}.txt".format(sha, n)).returncode == 0, \
            "the colleague's file is missing from the landed tree"
    assert _run(repo, "git", "show", sha + ":code.py").stdout == "VALUE = 2\n"


def test_a_RED_gate_is_never_retried_however_many_attempts_are_allowed(
        repo: Path, monkeypatch: pytest.MonkeyPatch):
    """THE SAFETY HALF, and the reason `BaseMoved` is a subclass rather than a message match.

    Retrying a red tree until a flaky test flips green is the laundering this whole tool exists
    to prevent, so a red gate must be terminal on attempt ONE even with attempts=5."""
    (repo / "gate_verdict").write_text("red")
    (repo / "code.py").write_text("VALUE = 2\n")
    before = _head(repo)
    real_run_gate = sl.run_gate
    calls: list[int] = []

    def counting_gate(checkout, hook_rel=sl.HOOK_REL):
        calls.append(len(calls) + 1)
        return real_run_gate(checkout, hook_rel)

    monkeypatch.setattr(sl, "run_gate", counting_gate)
    with pytest.raises(sl.LandingRefused, match="GATE RED"):
        # BOTH paths, so the RESULTING tree carries the red marker -- landing `code.py` alone
        # would leave HEAD's green `gate_verdict` in the tree under judgement and pass.
        sl.land(repo, ["code.py", "gate_verdict"], "red tree", attempts=5)
    assert calls == [1], "a red gate was retried: {} gate runs".format(len(calls))
    assert _head(repo) == before


def test_exhausting_the_attempts_refuses_and_commits_nothing(
        repo: Path, monkeypatch: pytest.MonkeyPatch):
    """The bound must be a REFUSAL, never a bypass -- and the message must name every lost base,
    because reconstructing the cadence from `git log` by hand is what the finding had to do."""
    (repo / "code.py").write_text("VALUE = 2\n")
    calls: list[int] = []
    monkeypatch.setattr(sl, "run_gate", _racing_gate(repo, lose_until=99, calls=calls))
    seen: list[tuple[int, str]] = []

    with pytest.raises(sl.LandingRefused, match="on all 3 attempt") as caught:
        sl.land(repo, ["code.py"], "never wins", attempts=3,
                on_lost=lambda n, exc: seen.append((n, exc.observed)))

    assert calls == [1, 2, 3]
    assert [n for n, _ in seen] == [1, 2, 3], "the lost attempts were not reported as they lost"
    assert str(caught.value).count("attempt ") >= 3, str(caught.value)
    assert _run(repo, "git", "log", "-1", "--format=%s").stdout.strip() == "colleague 3", \
        "an exhausted landing committed anyway"
    assert "code.py" not in _run(repo, "git", "show", "--name-only", "--format=",
                                 "HEAD").stdout


def test_zero_attempts_refuses_rather_than_landing_ungated(repo: Path):
    """The fail-open corner of the new knob: `--attempts 0` must not become a landing that skipped
    the gate. An unrun gate is a FAILED gate (R15)."""
    (repo / "code.py").write_text("VALUE = 2\n")
    before = _head(repo)
    with pytest.raises(sl.LandingRefused, match="no gate at all"):
        sl.land(repo, ["code.py"], "ungated", attempts=0)
    assert _head(repo) == before


# --------------------------------------------------------------------------------------------
# It must not touch anyone else's staged work -- the property that makes it the legal move.
# --------------------------------------------------------------------------------------------

def test_another_lanes_staged_work_is_byte_identical_after_a_landing(repo: Path):
    """The originating incident: `git merge` refused because 35 paths of other lanes' staged
    work sat in the shared index, and sweeping them in was the alternative sin."""
    (repo / "other_lane.txt").write_text("another lane's UNCOMMITTED, STAGED work\n")
    _run(repo, "git", "add", "other_lane.txt")
    staged_before = _index_blob(repo, "other_lane.txt")
    (repo / "code.py").write_text("VALUE = 2\n")
    before = _head(repo)

    sha = sl.land(repo, ["code.py"], "land mine only")

    assert _index_blob(repo, "other_lane.txt") == staged_before, \
        "the other lane's staged entry moved"
    assert "other_lane.txt" not in _run(
        repo, "git", "diff", "--name-only", before, sha).stdout, \
        "the other lane's work was swept into the commit"
    assert (repo / "other_lane.txt").read_text().endswith("STAGED work\n")


def test_a_refused_landing_leaves_the_index_untouched_too(repo: Path):
    (repo / "other_lane.txt").write_text("staged elsewhere\n")
    _run(repo, "git", "add", "other_lane.txt")
    staged_before = _index_blob(repo, "other_lane.txt")
    (repo / "gate_verdict").write_text("red")
    (repo / "code.py").write_text("VALUE = 2\n")

    with pytest.raises(sl.LandingRefused):
        sl.land(repo, ["code.py", "gate_verdict"], "refused")

    assert _index_blob(repo, "other_lane.txt") == staged_before


def test_a_deletion_lands_as_a_deletion(repo: Path):
    """A tool that could only ADD would leave the deleting half of a two-part change silently
    uncommitted -- the shape of the wedge, in the other direction."""
    (repo / "other_lane.txt").unlink()
    before = _head(repo)

    sha = sl.land(repo, ["other_lane.txt"], "delete it")

    assert _run(repo, "git", "diff", "--name-status", before, sha).stdout.split()[0] == "D"
    assert _run(repo, "git", "status", "--porcelain", "--", "other_lane.txt").stdout.strip() == ""


# --------------------------------------------------------------------------------------------
# The receipt has to be falsifiable, or it is decoration.
# --------------------------------------------------------------------------------------------

def test_the_receipt_names_the_tree_the_parent_and_every_path(repo: Path):
    (repo / "code.py").write_text("VALUE = 2\n")
    parent = _head(repo)
    sha = sl.land(repo, ["code.py"], "land it")

    receipt = sl.parse_receipt(_run(repo, "git", "log", "-1", "--format=%B", sha).stdout)
    assert receipt["parent"] == parent
    assert receipt["tree"] == _run(repo, "git", "rev-parse", sha + "^{tree}").stdout.strip()
    assert receipt["paths"] == ["code.py"]
    assert receipt["gate-rc"] == "0"
    assert "passed" in receipt["tests"], "the receipt carries no evidence the gate ran tests"


def test_verify_accepts_a_real_landing(repo: Path):
    (repo / "code.py").write_text("VALUE = 2\n")
    sha = sl.land(repo, ["code.py"], "land it")
    rc, text = sl.verify(repo, sha)
    assert rc == 0, text


def test_verify_FALSIFIES_a_receipt_copied_onto_a_different_commit(repo: Path):
    """The attack the receipt must survive: a hand-rolled commit wearing a real receipt to claim
    a gate run it never had."""
    (repo / "code.py").write_text("VALUE = 2\n")
    sha = sl.land(repo, ["code.py"], "land it")
    stolen = _run(repo, "git", "log", "-1", "--format=%B", sha).stdout

    (repo / "code.py").write_text("VALUE = 999  # ungated\n")
    _run(repo, "git", "add", "code.py")
    _run(repo, "git", "commit", "-q", "--no-verify", "-m", stolen)

    rc, text = sl.verify(repo, "HEAD")
    assert rc == 1, "a stolen receipt was accepted: {}".format(text)
    assert "FALSIFIED" in text


def _forge(repo: Path, tree: str | None = None, paths: list[str] | None = None) -> None:
    """Put a receipt on HEAD that is TRUE in every field except the one under test.

    `--amend` preserves the tree and the parent and rewrites only the message, so the receipt
    can name the commit's real shas while lying about exactly one thing. Without this, a forgery
    that gets several fields wrong is caught by whichever check runs first, and the others are
    never exercised -- which is how two of these checks initially survived mutation.
    """
    real_parent = _run(repo, "git", "rev-parse", "HEAD^").stdout.strip()
    real_tree = _run(repo, "git", "rev-parse", "HEAD^{tree}").stdout.strip()
    real_paths = _run(repo, "git", "diff", "--name-only", "HEAD^", "HEAD").stdout.split()
    receipt = sl.build_receipt(real_parent, tree or real_tree,
                               paths if paths is not None else real_paths,
                               0, "3 passed", sl.HOOK_REL)
    _run(repo, "git", "commit", "-q", "--amend", "--no-verify", "-m", "claimed gated\n\n" + receipt)


def test_verify_FALSIFIES_a_receipt_whose_only_lie_is_the_TREE(repo: Path):
    """Isolates the tree check. Parent and path set are true; only the tree sha is wrong -- the
    shape of a receipt copied from a sibling commit that touched the same files."""
    (repo / "code.py").write_text("VALUE = 999  # ungated\n")
    _run(repo, "git", "add", "code.py")
    _run(repo, "git", "commit", "-q", "--no-verify", "-m", "ungated")
    _forge(repo, tree="0" * 40)

    rc, text = sl.verify(repo, "HEAD")
    assert rc == 1, "a receipt naming the wrong tree was accepted: {}".format(text)
    assert "tree" in text


def test_verify_FALSIFIES_a_receipt_whose_only_lie_is_the_PATH_SET(repo: Path):
    """Isolates the path-set check, and it is the likelier forgery: a receipt whose shas are all
    genuine on a commit that quietly carries MORE than the receipt names."""
    (repo / "code.py").write_text("VALUE = 999\n")
    (repo / "other_lane.txt").write_text("swept in without being named\n")
    _run(repo, "git", "add", "code.py", "other_lane.txt")
    _run(repo, "git", "commit", "-q", "--no-verify", "-m", "ungated")
    _forge(repo, paths=["code.py"])

    rc, text = sl.verify(repo, "HEAD")
    assert rc == 1, "a receipt understating what it committed was accepted: {}".format(text)
    assert "other_lane.txt" in text


def test_verify_FALSIFIES_a_receipt_whose_only_lie_is_the_PARENT(repo: Path):
    """Isolates the parent check -- the field that makes 'gated against THIS base' meaningful."""
    (repo / "code.py").write_text("VALUE = 999\n")
    _run(repo, "git", "add", "code.py")
    _run(repo, "git", "commit", "-q", "--no-verify", "-m", "ungated")
    real_tree = _run(repo, "git", "rev-parse", "HEAD^{tree}").stdout.strip()
    receipt = sl.build_receipt("0" * 40, real_tree, ["code.py"], 0, "3 passed", sl.HOOK_REL)
    _run(repo, "git", "commit", "-q", "--amend", "--no-verify", "-m", "claimed\n\n" + receipt)

    rc, text = sl.verify(repo, "HEAD")
    assert rc == 1, "a receipt naming the wrong base was accepted: {}".format(text)
    assert "parent" in text


def test_verify_reports_no_receipt_distinctly_from_a_falsified_one(repo: Path):
    """Two different facts -- "not made with the tool" and "lying about it" -- must not collapse
    into one exit code, or the check cannot be acted on."""
    rc, text = sl.verify(repo, "HEAD")
    assert rc == 2
    assert "no surgical-land receipt" in text


# --------------------------------------------------------------------------------------------
# The extract really is a repo (the R10 lesson already paid for once in the publish gate).
# --------------------------------------------------------------------------------------------

def test_the_gate_runs_in_a_real_repo_so_git_asking_tests_do_not_die(repo: Path):
    """A checkout with no `.git` fails every history-reading test with `fatal: not a git
    repository` -- a failure about the harness, not the code, which is indistinguishable from a
    real red at the exit code. Proven by a hook that asks git a question."""
    (repo / "tools" / "git-hooks" / "pre-commit").write_text(
        "#!/bin/sh\ngit rev-parse HEAD >/dev/null || exit 1\n"
        "git diff --cached --name-only | grep -qx code.py || exit 1\n"
        "echo '1 passed'\n"
    )
    _run(repo, "git", "add", "-A")
    _run(repo, "git", "commit", "-q", "--no-verify", "-m", "git-asking hook")
    (repo / "code.py").write_text("VALUE = 2\n")

    sha = sl.land(repo, ["code.py"], "land under a git-asking gate")
    assert sha != ""


def test_the_extract_stages_exactly_this_commit_so_staging_aware_gates_see_it(repo: Path):
    """Several real gates (size ratchet, level surface, mint hygiene) are staging-aware: they
    read `git diff --cached` and pay nothing for an out-of-scope commit. If the extract staged
    everything, every landing would drag every gate in and the tool would be unusable."""
    (repo / "tools" / "git-hooks" / "pre-commit").write_text(
        "#!/bin/sh\n[ \"$(git diff --cached --name-only)\" = 'code.py' ] || {\n"
        "  echo \"staged set was: $(git diff --cached --name-only | tr '\\n' ' ')\"; exit 1; }\n"
        "echo '1 passed'\n"
    )
    _run(repo, "git", "add", "-A")
    _run(repo, "git", "commit", "-q", "--no-verify", "-m", "staged-set hook")
    (repo / "code.py").write_text("VALUE = 2\n")
    (repo / "other_lane.txt").write_text("not mine\n")

    assert sl.land(repo, ["code.py"], "one path only") != ""


def test_the_untracked_overlay_is_symlinked_AFTER_staging_not_before(
        repo: Path, monkeypatch: pytest.MonkeyPatch):
    """On the real tree the overlay is a ~291MB Elexon/NESO cache and `node_modules`. Symlinking
    it in BEFORE the extract's `git add` would stage the whole thing and hand every staging-aware
    gate a fabricated scope -- so the ORDER, not the pathspec, is what has to hold. (The pathspec
    alone is behaviourally equivalent here and is documented as such rather than claimed as a
    control.)"""
    (repo / "sim" / "cache").mkdir(parents=True)
    (repo / "sim" / "cache" / "big.json").write_text("{}\n")
    (repo / ".gitignore").write_text("sim/cache/\n")
    _run(repo, "git", "add", ".gitignore")
    (repo / "tools" / "git-hooks" / "pre-commit").write_text(
        "#!/bin/sh\n"
        "git diff --cached --name-only | grep -q 'sim/cache' && {\n"
        "  echo 'the overlay was staged'; exit 1; }\n"
        "test -e sim/cache/big.json || { echo 'overlay missing entirely'; exit 1; }\n"
        "echo '1 passed'\n"
    )
    _run(repo, "git", "add", "-A")
    _run(repo, "git", "commit", "-q", "--no-verify", "-m", "overlay-checking hook")
    monkeypatch.setattr(sl, "UNTRACKED_DATA_OVERLAY", ("sim/cache",))
    (repo / "code.py").write_text("VALUE = 2\n")

    assert sl.land(repo, ["code.py"], "land with an overlay present") != ""


def test_the_script_entrypoint_can_reach_the_repo_packages_it_defers_to():
    """The one caller no other test here exercises: the tool run as a SCRIPT.

    Every test above calls `sl.land()` in-process, where pytest has already put the repo root on
    `sys.path` -- so `background.tree_lock`, which `_write_lock` reaches for, resolves for free.
    Run the way the usage string shows (`python3 tools/surgical_land.py ...`), `sys.path[0]` is
    `tools/` and that import raises `ModuleNotFoundError`. The suite was green through the whole
    of it, because the defect lives strictly between the entry point and the code under test.

    Where it bit is what makes it worth a test rather than a fix: `_write_lock` is the LAST step
    of `land()`, so the crash arrived AFTER the full pre-commit gate had run against the extract
    -- minutes of work, nothing landed, and the legal move unavailable at the exact moment a seat
    reaches for it. That is the pressure toward `--no-verify` that this tool exists to remove.

    R15: this fires ALONE on its own defect -- delete the `sys.path.insert` in surgical_land.py
    and this reds while every other test in the file stays green. `cwd` is a foreign directory and
    PYTHONPATH is cleared so the repo root cannot arrive by either accident.
    """
    import os
    import sys

    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    script = Path(sl.__file__).resolve()
    r = subprocess.run([sys.executable, str(script), "--help"],
                       cwd=str(script.parent.parent.parent), capture_output=True, text=True,
                       env=env)
    assert r.returncode == 0, (
        "the tool cannot even print its usage when run as a script: {}".format(r.stderr.strip()))
    assert "ModuleNotFoundError" not in r.stderr


# --------------------------------------------------------------------------------------------
# WORKER_FINDING_THE_ONLY_LEGAL_LANDING_MOVE_LEAKS_150MB_A_KILL_2026-08-14: `sweep_stale_
# extracts` is what turns "no live process held any of them" into "removed". Each test below
# points `base=` at a scratch `tmp_path` dir, never the real system tempdir -- sweeping the
# actual box's `/tmp` from a test would risk deleting a concurrent lane's live extract, which is
# exactly the property direction 2 (`test_a_live_extract_survives_the_sweep`) exists to protect.
# --------------------------------------------------------------------------------------------

def _make_extract(base: Path, name: str, marker: str | None) -> Path:
    d = base / name
    d.mkdir(parents=True)
    (d / "some_extracted_file.txt").write_text("x" * 1024)  # gives freed_mb something to count
    if marker is not None:
        (d / sl.OWNER_MARKER).write_text(marker)
    return d


def test_sweep_removes_a_markerless_legacy_extract(tmp_path: Path):
    """Every extract made before this fix has no marker at all -- the 24-directory backlog the
    finding measured. R15 direction 1: plant exactly that shape and confirm the sweep fires."""
    d = _make_extract(tmp_path, "surgical-land-abc123", marker=None)

    removed, freed_mb = sl.sweep_stale_extracts(base=str(tmp_path))

    assert removed == 1
    assert freed_mb >= 0
    assert not d.exists()


def test_sweep_removes_a_dead_extract(tmp_path: Path):
    """A marker naming a PID that is provably not alive -- spawn a subprocess, wait for it to
    exit, use its now-dead PID. R15 direction 1, the case the marker mechanism was built for."""
    proc = subprocess.Popen([sys.executable, "-c", "pass"])
    dead_pid = proc.pid
    assert proc.wait() == 0
    # Confirm it is actually gone before trusting the test.
    with pytest.raises(ProcessLookupError):
        os.kill(dead_pid, 0)
    d = _make_extract(tmp_path, "surgical-land-dead", marker=str(dead_pid))

    removed, freed_mb = sl.sweep_stale_extracts(base=str(tmp_path))

    assert removed == 1
    assert freed_mb >= 0
    assert not d.exists()


def test_a_live_extract_survives_the_sweep(tmp_path: Path):
    """R15 direction 2, the fail-dangerous one: a marker naming THIS test process's own PID
    (guaranteed alive for the duration of the call) must not be removed, even though it matches
    the same glob and sits in the same directory as the dead ones above."""
    live = _make_extract(tmp_path, "surgical-land-live", marker=str(os.getpid()))
    proc = subprocess.Popen([sys.executable, "-c", "pass"])
    dead_pid = proc.pid
    assert proc.wait() == 0
    _make_extract(tmp_path, "surgical-land-dead", marker=str(dead_pid))

    removed, freed_mb = sl.sweep_stale_extracts(base=str(tmp_path))

    assert live.exists(), "a live extract was deleted out from under its own process"
    assert removed == 1  # only the dead one
    assert freed_mb >= 0


def test_sweep_ignores_the_index_tempfile_and_unrelated_directories(tmp_path: Path):
    """The index tempfile prefix (`surgical-land-index-`) overlaps the checkout prefix by name
    but is a FILE (unlinked immediately in `build_resulting_tree`) -- confirm the glob's `is_dir`
    guard actually excludes it rather than the file simply never existing in this fixture."""
    (tmp_path / "surgical-land-index-xyz").write_text("not a directory")
    unrelated = tmp_path / "not-ours-at-all"
    unrelated.mkdir()

    removed, freed_mb = sl.sweep_stale_extracts(base=str(tmp_path))

    assert removed == 0
    assert freed_mb == 0
    assert (tmp_path / "surgical-land-index-xyz").exists()
    assert unrelated.exists()


def test_a_landing_writes_the_owner_marker_before_anything_else_can_fail(repo: Path):
    """Every checkout `_land_once` creates must be self-identifying from the instant it exists --
    that ordering is what lets a concurrent sweep (this process's own next attempt, or another
    lane's) tell it apart from an abandoned one. Assert the CONTRACT (materialise receives real
    swept-stats, not a placeholder) by checking a real landing still succeeds with the sweep
    wired in ahead of it -- the integration point `test_sweep_removes_a_dead_extract` et al.
    exercise in isolation."""
    (repo / "code.py").write_text("VALUE = 2\n")
    sha = sl.land(repo, ["code.py"], "land with the sweep wired in")
    assert sha != ""
    # No leftover checkout for THIS run either -- the marker did not prevent its own cleanup.
    leftovers = list(Path(tempfile.gettempdir()).glob("surgical-land-*"))
    ours = [p for p in leftovers if p.is_dir() and (p / sl.OWNER_MARKER).exists()
            and (p / sl.OWNER_MARKER).read_text().strip() == str(os.getpid())]
    assert ours == []


def test_a_disk_refusal_names_what_the_sweep_found(repo: Path, monkeypatch: pytest.MonkeyPatch):
    """WORKER_FINDING point 4: a refusal that names only the symptom (bytes free) sent that
    finding looking at the wrong thing first. Force the free-space refusal and confirm the
    message states the swept count/MB rather than silently discarding it."""
    (repo / "code.py").write_text("VALUE = 2\n")
    monkeypatch.setattr(sl, "MIN_FREE_MB", 10**9)  # unreachable -- forces the refusal path

    with pytest.raises(sl.LandingRefused, match=r"Swept \d+ stale surgical-land extract"):
        sl.land(repo, ["code.py"], "should refuse on disk")
