"""A HOOK-GATED COMMIT MUST BE DISTINGUISHABLE FROM A BYPASS (2026-09-24).

THE DEFECT THIS EXISTS TO CLOSE. `tools/promote_worktree_landing._refuse_if_ungated` refuses every
commit in `origin/main..HEAD` that carries no verifying `surgical_land` receipt. That refusal is
right and must stay, because until today a hook-gated commit and a `--no-verify` one were
BYTE-IDENTICAL to the verifier: both are ordinary commits with an ordinary message. Relaxing the
refusal would reopen the hole of 2026-08-31, when `background/fork_salvage.py` committed
`SALVAGE(auto)` inside the seat executor's own worktree with an explicit `--no-verify`
(`fork_salvage.py`, the `git commit --no-verify` call) and a landing on top of it would have carried
it to `main` underneath a valid receipt.

But the two populations are NOT the same population, and that was measured, not assumed (landed
2026-09-24, `f1791deca`): the receiptless commits blocking the seat -- `13203ed91`, `61b67fa0d` --
each ran the full pre-commit chain, 232 seconds of it. They are gated. They are refused anyway, and
ONE of them on the shared tree makes the whole ahead leg unpromotable until someone spends a ~10
minute gate cycle discovering why, while costing the daemon that made it nothing.

A MARK IS THE ONLY THING THAT SEPARATES THEM. `--no-verify` and `commit-tree` do not run hooks, by
definition -- that is what they mean. So a mark that only the hook chain can leave, bound to the
exact tree the chain judged, is exactly the discriminator the door was missing.

WHAT THIS PROVES, AND WHAT IT DOES NOT. Precisely the standard `surgical_land.verify` already sets
for its receipt, and the same sentence applies here: it does not prove the gate was green at the
time -- nothing can, after the fact -- it proves the mark is ABOUT THIS COMMIT. A trailer naming a
tree that is not the commit's tree is refused, so a mark cannot be copied from one commit to
another, which is the whole failure mode a bare "gated: yes" string would have.

It is NOT unforgeable against someone who sets out to forge it: a session that hand-writes the
trailer with the right tree sha onto a `--no-verify` commit gets past this, exactly as one that
hand-writes a receipt gets past `--verify`. That is not the threat model and pretending otherwise
would be the more dangerous claim. The threat model is a DAEMON taking the documented bypass without
thinking about promotability -- which is what actually happened, twice, and what this now separates.
A forger has `--no-verify` and no reason to bother.

WHY TWO HOOKS. The mark cannot be written by one of them alone:
  * `pre-commit` is the only place that knows the gate chain PASSED (it is a `cmd || exit 1` chain,
    so reaching the end IS the pass) -- but the commit message does not exist yet, so it cannot
    stamp anything onto it.
  * `commit-msg` is the only place that can edit the message -- but it runs before the remaining
    message gates and knows nothing about whether the 232-second chain ran.
So pre-commit records what it judged into the git dir, and commit-msg promotes that record to a
trailer only if the index still writes out to the same tree. The tree equality is what makes the
handoff safe: a record left behind by an ABORTED commit cannot stamp a later, different one.

THE WRITER IS FAIL-SOFT AND THE DOOR IS FAIL-CLOSED, which is the right way round and is not an
oversight. A mark that cannot be written must never turn a green gate red -- the commit is gated
either way and refusing it would punish the honest path for a filesystem hiccup. The cost of a
missing mark is already the conservative outcome: `_refuse_if_ungated` refuses, as it does today.
So both CLI verbs exit 0 always, and absence is simply the state the door already handles.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MARK_HEADER = "[hook-gate mark]"
HOOK_REL = "tools/git-hooks/pre-commit"
# Lives in the GIT DIR, never the work tree: it is a fact about one commit being made by one
# worktree, it must never be committable, and `git rev-parse --git-dir` already resolves to
# `.git/worktrees/<name>` inside a linked worktree, so each worktree gets its own without asking.
MARK_FILENAME = "hook-gate-mark.json"


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True)


def _git_dir(root: Path) -> Path | None:
    proc = _git(root, "rev-parse", "--git-dir")
    if proc.returncode != 0:
        return None
    return (root / proc.stdout.strip()).resolve()


def _index_tree(root: Path) -> str | None:
    """The tree the commit in flight will carry.

    `git write-tree` is the subject for the same reason `stale_copy_refusal.staged` gives: during a
    hook the INDEX is what is being committed, and the working tree is not. Both hooks re-derive it
    independently and the pair is only trusted when they agree.
    """
    proc = _git(root, "write-tree")
    return proc.stdout.strip() if proc.returncode == 0 and proc.stdout.strip() else None


def _first_parent(root: Path) -> str:
    """`HEAD` at hook time is the commit's first parent. Empty string on a root commit, which is a
    real state (a fresh repo) and not an error -- so it is recorded as such rather than aborting."""
    proc = _git(root, "rev-parse", "--verify", "--quiet", "HEAD")
    return proc.stdout.strip() if proc.returncode == 0 else ""


def record(root: Path = ROOT) -> tuple[bool, str]:
    """pre-commit, LAST LINE: record the tree the chain just finished judging.

    There is deliberately NO `gate_rc` field, though the brief for this work asked for one. This
    line is only reached when every `|| exit 1` above it passed, so an rc field could hold exactly
    one value -- a constant dressed as evidence, which is the shape this project keeps paying for.
    What is falsifiable is the TREE, and that is what is written.
    """
    git_dir = _git_dir(root)
    if git_dir is None or not git_dir.is_dir():
        # `surgical_land.run_gate` runs this hook inside a clean extract with `GIT_*` scrubbed and
        # no repository at all. That landing gets a receipt, which is the stronger evidence, so
        # there is nothing to do and nothing wrong.
        return False, "no git dir -- not a repository (the surgical_land extract does this)"
    tree = _index_tree(root)
    if tree is None:
        return False, "the index would not write out as a tree -- nothing to bind a mark to"
    payload = {"tree": tree, "parent": _first_parent(root), "hook": HOOK_REL}
    try:
        (git_dir / MARK_FILENAME).write_text(json.dumps(payload), encoding="utf-8")
    except OSError as exc:
        return False, f"could not write the mark: {exc}"
    return True, f"gate chain completed on tree {tree[:9]}"


def stamp(msg_path: Path, root: Path = ROOT) -> tuple[bool, str]:
    """commit-msg, LAST LINE: promote the pre-commit record to a trailer on the real message.

    Only if the index STILL writes out to the tree pre-commit recorded. That equality is the whole
    safety of the handoff: a record left by a commit that then aborted in a message gate cannot
    stamp the next, different commit, and a `--no-verify` commit never reaches this code at all.
    """
    git_dir = _git_dir(root)
    if git_dir is None:
        return False, "no git dir"
    try:
        payload = json.loads((git_dir / MARK_FILENAME).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False, "no pre-commit record -- the gate chain did not complete for this commit"
    tree = _index_tree(root)
    if tree is None or payload.get("tree") != tree:
        return False, (
            "the pre-commit record names tree {} and the index now writes {} -- STALE, not "
            "stamping".format(str(payload.get("tree"))[:9], (tree or "nothing")[:9]))
    try:
        message = msg_path.read_text(encoding="utf-8")
    except OSError as exc:
        return False, f"could not read the message: {exc}"
    if MARK_HEADER in message:
        return False, "already marked"
    block = "\n".join([
        MARK_HEADER,
        f"tree: {tree}",
        f"parent: {payload.get('parent', '')}",
        f"gate: sh {payload.get('hook', HOOK_REL)} (chain completed)",
    ])
    try:
        msg_path.write_text(message.rstrip("\n") + "\n\n" + block + "\n", encoding="utf-8")
    except OSError as exc:
        return False, f"could not write the message: {exc}"
    return True, f"marked as hook-gated on tree {tree[:9]}"


def parse(message: str) -> dict | None:
    """Read a mark off a commit message. `None` when there is none -- never `{}`, because an empty
    dict reads as a mark with missing fields and would compare equal to nothing rather than
    refusing."""
    if MARK_HEADER not in message:
        return None
    fields: dict[str, str] = {}
    for line in message.split(MARK_HEADER, 1)[1].splitlines():
        line = line.strip()
        if not line:
            continue
        if ":" not in line:
            break
        key, _, value = line.partition(":")
        key = key.strip()
        if key not in {"tree", "parent", "gate"}:
            break
        fields[key] = value.strip()
    return fields or None


def verify(root: Path, commit: str) -> tuple[int, str]:
    """Is this commit's mark ABOUT this commit? rc 0 consistent, 1 FALSIFIED, 2 no mark.

    The rc vocabulary matches `surgical_land.verify` deliberately, so the door can treat the two
    kinds of evidence the same way and a reader of one already knows the other.
    """
    message = _git(root, "log", "-1", "--pretty=%B", commit).stdout
    mark = parse(message)
    if mark is None:
        return 2, f"no hook-gate mark on {commit[:9]}"
    actual_tree = _git(root, "rev-parse", f"{commit}^{{tree}}").stdout.strip()
    problems = []
    if mark.get("tree") != actual_tree:
        problems.append(
            f"mark tree {mark.get('tree')} != actual {actual_tree}")
    # `%P` is every parent; the first is the one the hook saw as HEAD. A merge's later parents were
    # never HEAD, so asking for them would falsify honest merges.
    parents = _git(root, "log", "-1", "--pretty=%P", commit).stdout.split()
    expected_parent = parents[0] if parents else ""
    if (mark.get("parent") or "") != expected_parent:
        problems.append(
            f"mark parent {mark.get('parent') or '(none)'} != actual {expected_parent or '(none)'}")
    if problems:
        return 1, "hook-gate mark on {} is FALSIFIED: {}".format(commit[:9], "; ".join(problems))
    return 0, "hook-gate mark on {} is about this commit (tree {})".format(
        commit[:9], actual_tree[:9])


def main(argv: list[str]) -> int:
    if len(argv) >= 1 and argv[0] == "--record":
        ok, why = record()
        print(f"[hook-gate-mark] {'recorded' if ok else 'not recorded'}: {why}")
        return 0  # FAIL-SOFT BY DESIGN -- see the module docstring.
    if len(argv) >= 2 and argv[0] == "--stamp":
        ok, why = stamp(Path(argv[1]))
        print(f"[hook-gate-mark] {'stamped' if ok else 'not stamped'}: {why}")
        return 0  # FAIL-SOFT BY DESIGN -- see the module docstring.
    if len(argv) >= 2 and argv[0] == "--verify":
        rc, text = verify(ROOT, argv[1])
        print(f"[hook-gate-mark] {text}")
        return rc
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
