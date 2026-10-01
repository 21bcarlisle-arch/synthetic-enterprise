"""The reconciler's merge message, run through the REAL `commit-msg` chain on a fork shaped like
the one that wedged the shared tree on 2026-10-01.

From 09:43 UTC that day every `origin_reconcile` cycle was refused by the message chain: origin's
`c42bae117` moved H49 0 -> 2 (with its own `NEXT:` trailer), and `next_step_gate` read the merge's
index against `HEAD` alone, so it charged the automatic merge for a level move the other parent
already carried. `write_time_gate` had been taught the same subtraction on 09-25; this gate had not.

The fork is built in a scratch git dir that borrows this repo's object store READ-ONLY through
`alternates`, and the hook is run with `GIT_DIR` pointing at it -- so the shared index and the
shared `.git` (where a stray `MERGE_HEAD` would turn another lane's next commit into a merge) are
never opened. The hook is the repo's own file, run the way `surgical_land.run_message_gate` runs it.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

from background.origin_reconcile import _MERGE_MESSAGE, _classify_merge_failure

PROJECT = Path(__file__).resolve().parents[2]
MAP_REL = "docs/design/maturity_map.yaml"
NEW_MODULE_REL = "tools/zz_reconciler_merge_probe.py"
LOCAL_DOC_REL = "docs/zz_reconciler_merge_probe.md"


def _git(args, env, data=None):
    r = subprocess.run(["git", *args], cwd=str(PROJECT), env=env, input=data,
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, f"git {args}: {r.stderr}"
    return r.stdout.strip()


def _tree_with(base, files, env):
    _git(["read-tree", base], env)
    for rel, text in files.items():
        blob = _git(["hash-object", "-w", "--stdin"], env, data=text)
        _git(["update-index", "--add", "--cacheinfo", f"100644,{blob},{rel}"], env)
    return _git(["write-tree"], env)


def _fork(tmp_path, with_merge_head: bool) -> dict:
    """A fork off HEAD: the ORIGIN leg moves a level and adds a module, the LOCAL leg adds a doc.
    Returns the env a hook run needs, with the merge result staged in the scratch index."""
    common = Path(subprocess.run(["git", "rev-parse", "--path-format=absolute",
                                  "--git-common-dir"], cwd=str(PROJECT), capture_output=True,
                                 text=True, check=True).stdout.strip())
    gitdir = tmp_path / "scratch.git"
    subprocess.run(["git", "init", "-q", "--bare", str(gitdir)], check=True)
    (gitdir / "objects" / "info" / "alternates").write_text(str(common / "objects") + "\n")
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_DIR=str(gitdir), GIT_INDEX_FILE=str(tmp_path / "index"),
               GIT_AUTHOR_NAME="probe", GIT_AUTHOR_EMAIL="probe@invalid",
               GIT_COMMITTER_NAME="probe", GIT_COMMITTER_EMAIL="probe@invalid")
    base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(PROJECT), capture_output=True,
                          text=True, check=True).stdout.strip()
    old_map = _git(["show", f"{base}:{MAP_REL}"], env) + "\n"
    new_map = old_map.replace("level_current: 0", "level_current: 1", 1)
    assert new_map != old_map, "no atom at level 0 to move: the fork would carry no level move"
    origin_files = {MAP_REL: new_map, NEW_MODULE_REL: '"""probe."""\n'}
    local_files = {LOCAL_DOC_REL: "probe\n"}
    origin = _git(["commit-tree", _tree_with(base, origin_files, env), "-p", base,
                   "-m", "origin leg\n\nNEXT: none -- probe"], env)
    local = _git(["commit-tree", _tree_with(base, local_files, env), "-p", base,
                  "-m", "local leg"], env)
    _tree_with(base, {**origin_files, **local_files}, env)  # the merge result, left staged
    (gitdir / "HEAD").write_text(local + "\n")
    if with_merge_head:
        (gitdir / "MERGE_HEAD").write_text(origin + "\n")
    msg = tmp_path / "COMMIT_EDITMSG"
    msg.write_text(_MERGE_MESSAGE, encoding="utf-8")
    return {"env": env, "msg": msg}


def _run_chain(fork) -> subprocess.CompletedProcess:
    return subprocess.run(["sh", "tools/git-hooks/commit-msg", str(fork["msg"])],
                          cwd=str(PROJECT), env=fork["env"], capture_output=True, text=True,
                          timeout=300)


def test_the_reconcilers_merge_message_passes_the_chain_on_a_fork_whose_other_leg_moved_a_level(
        tmp_path):
    """Mutation-proven 2026-10-01: with `moves_no_parent_carried` returning `moved` unchanged
    (the gate as it stood at 09:43), this reds with `[next-step-gate] COMMIT REFUSED`."""
    done = _run_chain(_fork(tmp_path, with_merge_head=True))
    assert done.returncode == 0, (
        f"the reconciler's own merge was refused by the commit-msg chain:\n{done.stderr}")


def test_the_same_staged_tree_IS_refused_when_it_is_not_a_merge(tmp_path):
    """The control above can fail: drop `MERGE_HEAD` and the identical index is an ordinary commit
    that adds a module and moves a level with no record -- the chain must refuse it."""
    done = _run_chain(_fork(tmp_path, with_merge_head=False))
    assert done.returncode == 1, done.stderr
    assert "[write-time-gate]" in done.stderr or "[next-step-gate]" in done.stderr, done.stderr


def test_a_message_gate_refusal_names_the_gate_and_quotes_its_text():
    """The 400-character cut used to keep `surgical_land`'s boilerplate and drop the verdict."""
    header = ("MESSAGE GATE RED (rc=1). This is the `commit-msg` chain -- the REUSE record and the "
              "`NEXT:` trailer -- and NOTHING here says a test failed: " + "x" * 400 + "\n"
              "  gate stdout (the verdict, and the tail the refusing gate wrote):\n"
              "<the gate produced no output to quote>\n  gate stderr:\n")
    for tag, said in (("[next-step-gate]", "COMMIT REFUSED.\nThis commit advances H49_x"),
                      ("[write-time-gate]", "COMMIT REFUSED -- AO2\n  • tools/new.py")):
        status, detail = _classify_merge_failure(
            "[surgical-land] refused: " + header + tag + " " + said)
        assert status == "REFUSED_GATE"
        assert tag in detail and said.splitlines()[-1] in detail, detail
