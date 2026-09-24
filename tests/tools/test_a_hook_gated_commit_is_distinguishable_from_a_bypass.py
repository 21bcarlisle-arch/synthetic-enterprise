"""THE DEFECT: a hook-gated commit and a `--no-verify` one were byte-identical to the promotion door.

`promote_worktree_landing._refuse_if_ungated` refused every commit without a `surgical_land` receipt,
and had to, because nothing on an ordinary `git commit` said its 232-second pre-commit chain had run.
Measured 2026-09-24 (`f1791deca`): `13203ed91` and `61b67fa0d` were both fully gated, both refused,
and ONE such commit on the shared tree makes the entire ahead leg unpromotable until a seat spends a
~10 minute cycle finding out why.

`tools/hook_gate_mark` is the discriminator. These are its falsifiers, and the pair that matters is
the FIRST test: the mark must appear on the gated commit AND be absent on the bypass. A mark that
appeared on both would read exactly like this working while closing nothing, and a door keyed to it
would have reopened the 2026-08-31 `fork_salvage` hole.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from tools import hook_gate_mark

PROJECT = Path(__file__).resolve().parents[2]


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A throwaway repo with BOTH hooks installed in hook position.

    Deliberately not a linked worktree of this project: the subject is the hook handoff, and other
    lanes are committing in the shared tree right now. A `--no-verify` arm needs real hooks, so a
    monkeypatched unit test cannot reach the property this file exists to check.
    """
    path = tmp_path / "r"
    path.mkdir()
    assert _git(path, "init", "-q", ".").returncode == 0
    _git(path, "config", "user.email", "t@example.invalid")
    _git(path, "config", "user.name", "t")
    hooks = path / ".git" / "hooks"
    call = (
        f"import sys; sys.path.insert(0, {str(PROJECT)!r})\n"
        "from pathlib import Path\n"
        "from tools import hook_gate_mark as m\n"
    )
    (hooks / "pre-commit").write_text(
        f'#!/bin/sh\n{sys.executable} -c "$(cat <<\'PY\'\n{call}'
        f"m.record(Path({str(path)!r}))\nPY\n)\"\n",
        encoding="utf-8")
    (hooks / "commit-msg").write_text(
        f'#!/bin/sh\n{sys.executable} -c "$(cat <<\'PY\'\n{call}'
        f"import sys as s; m.stamp(Path(s.argv[1]), Path({str(path)!r}))\nPY\n)\" \"$1\"\n",
        encoding="utf-8")
    (hooks / "pre-commit").chmod(0o755)
    (hooks / "commit-msg").chmod(0o755)
    return path


def _commit(repo: Path, name: str, message: str, *extra: str) -> str:
    (repo / name).write_text(name, encoding="utf-8")
    assert _git(repo, "add", name).returncode == 0
    proc = _git(repo, "commit", "-m", message, *extra)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return _git(repo, "rev-parse", "HEAD").stdout.strip()


def test_the_gated_commit_is_marked_and_the_bypass_is_not(repo):
    """THE WHOLE POINT, and it needs both arms or it is not a discriminator.

    MUTATION: make `stamp` ignore its staleness check and return a trailer unconditionally, and the
    bypass arm still passes (hooks do not run under `--no-verify`) — but make `record`/`stamp` write
    the trailer from anywhere else, such as a post-commit hook or a `git log` filter, and the second
    assertion fires. The arm that actually kills a tautology here is the third assertion: rc 2, not
    rc 0, for the unmarked commit.
    """
    gated = _commit(repo, "a.txt", "gated: the hooks ran")
    bypass = _commit(repo, "b.txt", "bypass: hooks skipped", "--no-verify")

    assert hook_gate_mark.verify(repo, gated)[0] == 0, "the gated commit is not recognised as gated"
    assert hook_gate_mark.parse(
        _git(repo, "log", "-1", "--pretty=%B", bypass).stdout) is None, (
        "the --no-verify commit carries a mark — the discriminator discriminates nothing and the "
        "fork_salvage hole is open again")
    assert hook_gate_mark.verify(repo, bypass)[0] == 2


def test_a_mark_copied_onto_another_commit_is_falsified(repo):
    """ANTI-TAUTOLOGY: `verify` must check the mark is ABOUT this commit, not merely present.

    Without this the mark is a "gated: yes" string, and copying it is a one-line edit — which is
    exactly the failure `surgical_land.verify` was built to refuse for receipts.

    MUTATION: drop the tree comparison in `verify` and this fires. Drop only the parent comparison
    and it still fires on the tree, so the parent leg has its own test below.
    """
    gated = _commit(repo, "a.txt", "gated: the hooks ran")
    stolen = _git(repo, "log", "-1", "--pretty=%B", gated).stdout

    (repo / "c.txt").write_text("c", encoding="utf-8")
    _git(repo, "add", "c.txt")
    assert _git(repo, "commit", "--no-verify", "-m", stolen).returncode == 0
    thief = _git(repo, "rev-parse", "HEAD").stdout.strip()

    rc, text = hook_gate_mark.verify(repo, thief)
    assert rc == 1, f"a stolen mark verified as honest: {text}"
    assert "FALSIFIED" in text


def test_a_mark_naming_the_right_parent_and_the_wrong_tree_is_falsified(repo):
    """THE TREE LEG ON ITS OWN, and it was missing until a mutation round found it green.

    Deleting the tree comparison in `verify` left all eleven other tests passing: the copied-mark
    test above breaks the tree AND the parent, so the parent leg caught that mutation and the result
    read as the tree check working. It is the flattering reading of a green mutation every time.

    The tree is the leg that matters most — it is the only field that says the mark describes THIS
    CONTENT, so without it a mark survives any amendment to what is being committed.

    MUTATION: replace `if mark.get("tree") != actual_tree:` with `if False:` and this fires, alone.
    """
    _commit(repo, "a.txt", "gated: the hooks ran")
    marked_message = _git(repo, "log", "-1", "--pretty=%B", "HEAD").stdout
    original_tree = _git(repo, "rev-parse", "HEAD^{tree}").stdout.strip()

    # Amend keeps the PARENT and changes the TREE, carrying the original mark forward verbatim.
    (repo / "extra.txt").write_text("smuggled", encoding="utf-8")
    _git(repo, "add", "extra.txt")
    assert _git(repo, "commit", "--amend", "--no-verify", "-m", marked_message).returncode == 0
    amended = _git(repo, "rev-parse", "HEAD").stdout.strip()

    mark = hook_gate_mark.parse(marked_message)
    assert mark is not None and mark["tree"] == original_tree
    assert _git(repo, "rev-parse", "HEAD^{tree}").stdout.strip() != original_tree, (
        "the amend did not change the tree, so this test cannot see the tree leg at all")

    rc, text = hook_gate_mark.verify(repo, amended)
    assert rc == 1, f"a mark describing a different tree verified as honest: {text}"
    assert "tree" in text


def test_a_mark_naming_the_right_tree_and_the_wrong_parent_is_falsified(repo):
    """The parent leg on its own. A tree sha can recur — an empty tree, a revert that restores an
    earlier tree exactly — so tree equality alone is not identity.

    MUTATION: remove the parent comparison in `verify` and this fires while the test above stays
    green, which is why both exist.
    """
    gated = _commit(repo, "a.txt", "gated: the hooks ran")
    mark = hook_gate_mark.parse(_git(repo, "log", "-1", "--pretty=%B", gated).stdout)
    assert mark is not None

    tree = _git(repo, "rev-parse", f"{gated}^{{tree}}").stdout.strip()
    forged = "wrong parent\n\n{}\ntree: {}\nparent: {}\ngate: sh x (chain completed)\n".format(
        hook_gate_mark.MARK_HEADER, tree, "0" * 40)
    _git(repo, "commit", "--amend", "--no-verify", "-m", forged)
    amended = _git(repo, "rev-parse", "HEAD").stdout.strip()

    rc, text = hook_gate_mark.verify(repo, amended)
    assert rc == 1 and "parent" in text, f"the parent was never checked: {text}"


def test_a_stale_pre_commit_record_cannot_stamp_a_different_tree(repo):
    """The handoff's safety. `pre-commit` and `commit-msg` are separate processes, and a commit can
    pass pre-commit then ABORT in a message gate — leaving the record on disk. The next commit must
    not inherit it.

    MUTATION: make `stamp` skip the `payload["tree"] != tree` comparison and this fires. That
    mutation is the obvious first draft of this module, and it would mark an ungated tree as gated.
    """
    _commit(repo, "a.txt", "first")
    (repo / "b.txt").write_text("b", encoding="utf-8")
    _git(repo, "add", "b.txt")
    recorded, why = hook_gate_mark.record(repo)
    assert recorded, why

    (repo / "c.txt").write_text("c", encoding="utf-8")  # the index moves on after the gate passed
    _git(repo, "add", "c.txt")

    msg = repo / "MSG"
    msg.write_text("a message\n", encoding="utf-8")
    stamped, why = hook_gate_mark.stamp(msg, repo)
    assert not stamped, "a stale record stamped a tree the gate never judged"
    assert "STALE" in why
    assert hook_gate_mark.MARK_HEADER not in msg.read_text(encoding="utf-8")


def test_the_writer_never_reds_a_green_gate(tmp_path, monkeypatch):
    """FAIL-SOFT AT THE WRITER, FAIL-CLOSED AT THE DOOR. A mark that cannot be written must not turn
    a passing gate into a refusal: the commit is gated either way and the missing mark is already the
    conservative state. `surgical_land` runs this hook in an extract with no repository at all, so
    this branch is taken on every single landing through the main door.

    MUTATION: make `main("--record")` return 1 when nothing was recorded and this fires — and every
    `surgical_land` landing in the project starts failing its own gate.
    """
    monkeypatch.chdir(tmp_path)  # not a repository
    assert hook_gate_mark.record(tmp_path)[0] is False
    assert hook_gate_mark.main(["--record"]) == 0
    assert hook_gate_mark.main(["--stamp", str(tmp_path / "nope")]) == 0


def test_a_message_with_no_mark_parses_to_None_rather_than_an_empty_mark():
    """`parse` must not return `{}`: a falsy-but-not-None mark makes `verify` compare missing fields
    against real shas and the branch it lands in depends on truthiness, which is how a fail-closed
    check becomes fail-open.

    MUTATION: return `fields` unconditionally instead of `fields or None` and this fires.
    """
    assert hook_gate_mark.parse("an ordinary message\n\nwith a body\n") is None
    assert hook_gate_mark.parse(f"x\n\n{hook_gate_mark.MARK_HEADER}\nnot-a-field\n") is None


# ── THE DOOR: TWO KINDS OF EVIDENCE, ONE PROPERTY ────────────────────────────────────────────────

def test_the_door_promotes_a_hook_marked_commit_that_has_no_receipt(tmp_path, monkeypatch):
    """The reason this work exists. A gated daemon commit with no receipt must stop blocking the leg.

    MUTATION: delete the `hook_gate_mark.verify` branch in `_refuse_if_ungated` and this fires —
    that mutation is the code as it stood this morning, and it is what wedged the tree.
    """
    from tools import promote_worktree_landing as promote

    commit = "aaaaaaaaa"
    monkeypatch.setattr(promote, "_git_out", lambda cwd, *a: (
        "000000000" if a[:2] == ("rev-parse", "origin/main") else commit))
    monkeypatch.setattr(promote.subprocess, "run", lambda argv, **k:
                        subprocess.CompletedProcess(argv, 2, stdout="", stderr="no receipt"))
    monkeypatch.setattr(promote.hook_gate_mark, "verify", lambda root, c: (0, "marked"))

    promote._refuse_if_ungated(tmp_path, commit)  # must not raise


def test_the_door_still_refuses_a_commit_with_neither_receipt_nor_mark(tmp_path, monkeypatch):
    """THE HOLE STAYS SHUT. `--no-verify` and `commit-tree` run no hooks, so a genuine bypass
    arrives with neither kind of evidence and is still refused by name.

    MUTATION: accept on `mark_rc != 1` (i.e. treat "no mark" as fine) and this fires. That is the
    plausible-looking relaxation, and it would promote every `fork_salvage` SALVAGE commit.
    """
    from tools import promote_worktree_landing as promote

    commit = "aaaaaaaaa"
    monkeypatch.setattr(promote, "_git_out", lambda cwd, *a: (
        "000000000" if a[:2] == ("rev-parse", "origin/main") else commit))
    monkeypatch.setattr(promote, "_git", lambda cwd, *a: subprocess.CompletedProcess(
        a, 0, stdout="SALVAGE(auto): preserve this fork's uncommitted work\n", stderr=""))
    monkeypatch.setattr(promote.subprocess, "run", lambda argv, **k:
                        subprocess.CompletedProcess(argv, 2, stdout="", stderr="no receipt"))
    monkeypatch.setattr(promote.hook_gate_mark, "verify", lambda root, c: (2, "no mark"))

    with pytest.raises(promote.PromotionRefused) as exc:
        promote._refuse_if_ungated(tmp_path, commit)
    assert "SALVAGE(auto)" in str(exc.value)
    assert "no hook-gate mark" in str(exc.value), (
        "the refusal does not mention the mark, so a reader cannot tell this from the pre-2026-09-24 "
        "state where absence of a receipt was all the door could observe")


def test_the_door_names_a_falsified_mark_as_worse_than_an_absent_one(tmp_path, monkeypatch):
    """A present-but-wrong mark is a claim, not a gap, and the refusal must say so — otherwise the
    reader re-lands a commit whose message is actively lying about what it is.

    MUTATION: collapse the `mark_rc == 1` wording to the generic text and this fires.
    """
    from tools import promote_worktree_landing as promote

    commit = "aaaaaaaaa"
    monkeypatch.setattr(promote, "_git_out", lambda cwd, *a: (
        "000000000" if a[:2] == ("rev-parse", "origin/main") else commit))
    monkeypatch.setattr(promote, "_git", lambda cwd, *a: subprocess.CompletedProcess(
        a, 0, stdout="a subject\n", stderr=""))
    monkeypatch.setattr(promote.subprocess, "run", lambda argv, **k:
                        subprocess.CompletedProcess(argv, 2, stdout="", stderr="no receipt"))
    monkeypatch.setattr(promote.hook_gate_mark, "verify",
                        lambda root, c: (1, "mark tree X != actual Y"))

    with pytest.raises(promote.PromotionRefused) as exc:
        promote._refuse_if_ungated(tmp_path, commit)
    assert "DOES NOT DESCRIBE IT" in str(exc.value)


def test_a_receipt_alone_is_still_sufficient_and_the_mark_is_not_consulted(tmp_path, monkeypatch):
    """BLAST RADIUS. Every `surgical_land` landing has a receipt and no mark (its gate runs in a
    repository-less extract). If the door started requiring both, the main door would stop working.

    MUTATION: ask for the mark unconditionally instead of only after the receipt fails, and this
    fires — the mark verifier must never even be reached for a receipted commit.
    """
    from tools import promote_worktree_landing as promote

    commit = "aaaaaaaaa"
    asked: list[str] = []
    monkeypatch.setattr(promote, "_git_out", lambda cwd, *a: (
        "000000000" if a[:2] == ("rev-parse", "origin/main") else commit))
    monkeypatch.setattr(promote.subprocess, "run", lambda argv, **k:
                        subprocess.CompletedProcess(argv, 0, stdout="", stderr=""))
    monkeypatch.setattr(promote.hook_gate_mark, "verify",
                        lambda root, c: (asked.append(c), (2, "no mark"))[1])

    promote._refuse_if_ungated(tmp_path, commit)  # must not raise
    assert asked == [], "a receipted commit had its mark consulted -- ordering regressed"


def test_both_hooks_actually_invoke_the_mark_module():
    """THE WIRING IS THE CONTROL. Every test above exercises the module; none of them proves the
    repo's own hooks call it. An unwired mark is a module with passing tests that marks nothing, and
    `_refuse_if_ungated` would then refuse every ordinary commit exactly as it does today.

    MUTATION: delete either hook line and this fires.
    """
    pre = (PROJECT / "tools" / "git-hooks" / "pre-commit").read_text(encoding="utf-8")
    msg = (PROJECT / "tools" / "git-hooks" / "commit-msg").read_text(encoding="utf-8")

    assert "tools.hook_gate_mark --record" in pre
    assert "tools.hook_gate_mark --stamp" in msg
    # POSITION IS THE PASS. The chain is `cmd || exit 1`, so recording anywhere but the end would
    # record a gate run that had not finished. MUTATION: move the line up and this fires.
    body = [ln.strip() for ln in pre.splitlines() if ln.strip() and not ln.startswith("#")]
    assert body[-1] == "python3 -m tools.hook_gate_mark --record", (
        "the record line is no longer the last command in the chain, so it can be reached with "
        f"gates below it still unrun -- last line is {body[-1]!r}")
