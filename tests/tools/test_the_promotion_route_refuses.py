"""Only a GATED landing reaches `origin/main`, and never by force.

`tools/promote_worktree_landing` is the second half of the isolated-writer route: `surgical_land`
gates and commits inside a worktree (which leaves `main` untouched), and this gets that commit onto
the remote or refuses. It exists as a tool rather than a habit because the sequence had been
hand-rolled twice, and hand-rolled git on a shared tree is where `git stash` nearly swallowed
another lane's parked work on 2026-08-31.

EVERY LEG IS A REFUSAL, AND THAT IS THE SHAPE OF THE THING. The tool's job is to say no; pushing is
what happens when it has run out of reasons. So the controls are mostly "does it refuse when it
should", with one leg holding that it can still say YES — without which every other leg is
satisfied by a tool that refuses everything.

THE LOAD-BEARING ONE IS THE RECEIPT. It makes *only gated commits reach `main`* a property of the
ROUTE rather than of the caller's discipline: a commit made with a hand-rolled `git commit`, or
with `--no-verify`, has no `surgical_land` receipt and cannot be promoted. The wall is enforced
where work leaves the machine, not trusted where it was made.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from tools.promote_worktree_landing import PromotionRefused, promote

PROJECT = Path(__file__).resolve().parents[2]


def _git(cwd, *args):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=300)


@pytest.fixture
def worktree(tmp_path_factory):
    """A real linked worktree at `origin/main`. Nothing here is ever pushed."""
    path = tmp_path_factory.mktemp("promo") / "wt"
    r = _git(PROJECT, "worktree", "add", "--detach", "-q", str(path), "origin/main")
    if r.returncode != 0:
        pytest.skip(f"could not create a worktree: {r.stderr.strip()[:200]}")
    try:
        yield path
    finally:
        _git(PROJECT, "worktree", "remove", "--force", str(path))
        _git(PROJECT, "worktree", "prune")


def test_a_worktree_sitting_on_origin_main_has_NOTHING_to_promote(worktree):
    """The clearest answer, and it must come first or a reader mis-diagnoses.

    Built because the first exercise of this tool hit the *ungated* refusal here instead, which
    read as a defect in the commit rather than "there is no work". Ordering is part of a refusal
    being useful.

    MUTATION: move the already-there check below the receipt check and this fires.
    """
    with pytest.raises(PromotionRefused) as exc:
        promote(worktree, dry_run=True)
    assert "has landed nothing" in str(exc.value)


def test_an_UNGATED_commit_cannot_be_promoted(worktree):
    """The load-bearing leg: the receipt is what makes the route enforce the wall.

    A plain `git commit` — the shape a hand-rolled or `--no-verify` landing would take — carries no
    `surgical_land` receipt and must be refused however clean it otherwise looks.

    MUTATION: drop `_refuse_if_ungated` and this fires.
    """
    _git(worktree, "commit", "-q", "--allow-empty", "--no-verify", "-m", "ungated by hand")
    with pytest.raises(PromotionRefused) as exc:
        promote(worktree, dry_run=True)
    message = str(exc.value)
    assert "receipt" in message and "not gated" in message
    assert "Re-land it through the door" in message


def test_a_DIRTY_worktree_cannot_be_promoted(worktree):
    """Uncommitted tracked work means the landing is not the whole of what was done.

    MUTATION: drop `_refuse_if_dirty`, or stop passing `--untracked-files=no`, and this fires —
    the second would also make every run refuse on the machine's untracked data overlay.
    """
    _git(worktree, "commit", "-q", "--allow-empty", "--no-verify", "-m", "base")
    (worktree / "CLAUDE.md").write_text((worktree / "CLAUDE.md").read_text() + "\n# dirty\n")
    with pytest.raises(PromotionRefused) as exc:
        promote(worktree, dry_run=True)
    assert "uncommitted tracked changes" in str(exc.value)
    assert "CLAUDE.md" in str(exc.value)


def test_an_UNTRACKED_file_is_not_dirtiness(worktree):
    """The machine's data overlay is untracked by design; refusing on it would refuse always.

    MUTATION: remove `--untracked-files=no` and this fires — the tool would become unusable on any
    real machine, which is the failure mode that gets a guard deleted rather than fixed.
    """
    (worktree / "an_untracked_artefact.json").write_text("{}\n")
    with pytest.raises(PromotionRefused) as exc:
        promote(worktree, dry_run=True)
    assert "uncommitted tracked changes" not in str(exc.value), (
        "an untracked file was read as a dirty worktree"
    )


def test_it_can_still_say_YES__so_the_refusals_above_are_not_vacuous(worktree, monkeypatch):
    """Without this, a tool that refused everything would pass every other leg in this file.

    The receipt and fast-forward checks are stubbed here — they are each held by their own leg —
    so what this asserts is that `promote` REACHES a push decision when nothing objects.

    MUTATION: make `promote` raise unconditionally, or never return `would_push`, and this fires.
    """
    import tools.promote_worktree_landing as mod

    _git(worktree, "commit", "-q", "--allow-empty", "--no-verify", "-m", "a landing")
    monkeypatch.setattr(mod, "_refuse_if_ungated", lambda *a, **k: None)
    monkeypatch.setattr(mod, "_refuse_if_not_fast_forward", lambda wt, c: "0" * 40)
    result = mod.promote(worktree, dry_run=True)
    assert result["would_push"] is True
    assert result["pushed"] is False, "a dry run must never push"


def test_the_promoted_paths_are_read_from_the_COMMIT_not_from_the_caller(worktree, monkeypatch):
    """A writer must not be able to under-declare its scope to slip past the duplication check.

    MUTATION: take the paths from an argument instead of `git show --name-only` and this fires.
    """
    import tools.promote_worktree_landing as mod

    (worktree / "CLAUDE.md").write_text((worktree / "CLAUDE.md").read_text() + "\n# x\n")
    _git(worktree, "add", "CLAUDE.md")
    _git(worktree, "commit", "-q", "--no-verify", "-m", "touches CLAUDE.md")
    monkeypatch.setattr(mod, "_refuse_if_ungated", lambda *a, **k: None)
    monkeypatch.setattr(mod, "_refuse_if_not_fast_forward", lambda wt, c: "0" * 40)
    result = mod.promote(worktree, dry_run=True)
    assert "CLAUDE.md" in result["paths"], (
        "the paths did not come from the commit — a caller could then under-declare its scope"
    )


def test_the_route_NEVER_forces():
    """Stated as a property of the source, because a forced push cannot be un-done by a test.

    Every other leg here can be checked by running the thing. This one cannot: by the time a
    `--force` has executed, whatever it overwrote is gone. So it is asserted structurally.

    IT READS THE CODE, NOT THE PROSE, AND THE FIRST DRAFT DID NOT. Written as a substring search
    over the file, it failed on this module's own docstring — which says "Never `--force`, ever"
    for the benefit of the next reader. A scan that cannot tell an argument from a sentence about
    arguments is the same defect as a citation nobody read, and it appeared twice in one day. So
    this walks the AST and inspects only strings that are ARGUMENTS TO A CALL; a docstring is not
    one.

    MUTATION: add `--force` or `--force-with-lease` to any git invocation here, or push a `+`
    refspec, and this fires.
    """
    import ast

    source = (PROJECT / "tools" / "promote_worktree_landing.py").read_text()
    tree = ast.parse(source)
    call_strings = [
        node.value
        for call in ast.walk(tree) if isinstance(call, ast.Call)
        for node in ast.walk(call)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]
    assert call_strings, "no call arguments found — the walk is not reaching the git invocations"
    for argument in call_strings:
        assert "--force" not in argument, (
            f"a git call in the promotion route passes {argument!r}. This route exists so that a "
            "second writer cannot overwrite the first; a force push is that guarantee removed."
        )
        assert not argument.startswith("+"), (
            f"a git call passes the refspec {argument!r} — a leading `+` is a force push wearing "
            "different clothes."
        )


def test_MACHINE_EXHAUST_from_the_gate_is_not_unfinished_work(worktree):
    """Found by the route refusing its own predecessor's output, which is the best kind of finding.

    The pre-commit gate WRITES into the tree it has just gated — observability ledgers, repeating
    alarm documents — so a worktree is dirty the instant a `surgical_land` succeeds. A dirty check
    that counted those would make this route unusable at the only moment it is ever called.

    The exclusion is the SAME list the duplication guard uses, shared rather than copied: both
    readers ask whether churn in these directories carries signal about a writer's work.

    MUTATION: stop excluding `SHARED_BY_DESIGN` and this fires — and the route would then refuse
    every real landing it was built for.
    """
    import tools.promote_worktree_landing as mod
    from background.seat_work_in_hand import SHARED_BY_DESIGN

    _git(worktree, "commit", "-q", "--allow-empty", "--no-verify", "-m", "a landing")
    churned = worktree / "docs" / "observability" / "agent_status.json"
    assert churned.exists(), "fixture assumption: this observability file is tracked"
    churned.write_text(churned.read_text() + "\n")

    monkey_free = mod._refuse_if_dirty(worktree)  # must NOT raise
    assert monkey_free is None

    real = worktree / "CLAUDE.md"
    real.write_text(real.read_text() + "\n# genuinely unfinished\n")
    with pytest.raises(PromotionRefused) as exc:
        mod._refuse_if_dirty(worktree)
    assert "CLAUDE.md" in str(exc.value), "real unfinished work must still be caught"
    assert "agent_status.json" not in str(exc.value), (
        "machine exhaust was reported as unfinished work"
    )
    assert any(str(p).startswith("docs/") for p in SHARED_BY_DESIGN)


# ── A PUSH PROMOTES A RANGE, NOT A TIP (2026-08-31) ──────────────────────────────────────────────
# Found by the first live run of the seat executor. Four minutes after it started its first
# unattended turn, `background/fork_salvage.py` -- a daemon that sweeps worktrees for uncommitted
# work -- committed `SALVAGE(auto): preserve this fork's uncommitted work` INSIDE the executor's
# own worktree, ungated. Had the executor then landed on top of it, HEAD would have carried a valid
# receipt, `_refuse_if_ungated` would have passed, and the fast-forward would have carried the
# salvage commit onto `main` underneath the landing.
#
# The route's whole claim is about what reaches `main`. A push moves a REF, so the subject is
# `origin/main..HEAD` and never the tip alone.

def test_an_ungated_commit_beneath_a_gated_tip_is_refused(tmp_path, monkeypatch):
    """MUTATION: verify only `commit` instead of the range and this fires with the salvage commit
    named. That mutation is the code as shipped this morning."""
    from tools import promote_worktree_landing as promote

    tip = "aaaaaaaaa"
    beneath = "bbbbbbbbb"
    verified: list[str] = []

    def _fake_git_out(cwd, *args):
        if args[:2] == ("rev-parse", "origin/main"):
            return "000000000"
        if args[0] == "rev-list":
            return f"{beneath}\n{tip}"
        raise AssertionError(f"unexpected git call: {args}")

    def _fake_run(argv, **kwargs):
        import subprocess as sp
        candidate = argv[-1]
        verified.append(candidate)
        rc = 0 if candidate == tip else 1
        return sp.CompletedProcess(argv, rc, stdout="", stderr="no receipt")

    monkeypatch.setattr(promote, "_git_out", _fake_git_out)
    monkeypatch.setattr(promote, "_git", lambda cwd, *a: __import__("subprocess").CompletedProcess(
        a, 0, stdout="SALVAGE(auto): preserve this fork's uncommitted work\n", stderr=""))
    monkeypatch.setattr(promote.subprocess, "run", _fake_run)

    with pytest.raises(promote.PromotionRefused) as exc:
        promote._refuse_if_ungated(tmp_path, tip)

    assert beneath[:9] in str(exc.value)
    assert "beneath the tip" in str(exc.value)
    assert "SALVAGE(auto)" in str(exc.value)
    assert beneath in verified, "the commit under the tip was never verified at all"


def test_a_range_of_gated_commits_is_promotable(tmp_path, monkeypatch):
    """The blast-radius leg: widening the subject must not refuse an honest multi-commit landing.

    Landing an increment and then landing again is the shape the charter actively asks for -- *"if
    it is bigger than one turn, land the part you finished"* -- so a route that could only ever
    promote a single commit would refuse the behaviour it teaches."""
    from tools import promote_worktree_landing as promote

    commits = ["111111111", "222222222", "333333333"]

    monkeypatch.setattr(promote, "_git_out", lambda cwd, *a: (
        "000000000" if a[:2] == ("rev-parse", "origin/main") else "\n".join(commits)))
    monkeypatch.setattr(promote.subprocess, "run", lambda argv, **k:
                        __import__("subprocess").CompletedProcess(argv, 0, stdout="", stderr=""))

    promote._refuse_if_ungated(tmp_path, commits[-1])  # must not raise
