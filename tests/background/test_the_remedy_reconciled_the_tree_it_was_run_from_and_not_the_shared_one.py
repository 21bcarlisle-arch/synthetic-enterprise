"""The publisher's own remedy must reconcile the SHARED tree, wherever it was invoked from.

THE DEFECT (2026-09-08, Lane 0). `process_run_complete` writes
`python3 -m background.origin_reconcile` into its own `cause_evidence` as the remedy for
`behind_origin`. The delivery seat's executor is instructed to work in an isolated linked worktree,
so that is where the remedy gets run — and `origin_reconcile.PROJECT_DIR` is
`Path(__file__).resolve().parent.parent`, i.e. whichever tree the module was imported from.

Measured at 2026-09-08T22:30Z from `/var/tmp/se-seat-executor`: `commits_behind()` returned 0 and
`reconcile()` returned `LEVEL: local and origin/main agree; nothing to reconcile` with exit code 0,
while the shared tree was 2 commits behind origin/main and the publisher running from it had
`last_clean_publish: null` and 30 consecutive failures. The remedy reported success about a tree
nothing publishes from, so a seat following the refusal's own instruction would take LEVEL as proof
the wedge was cleared.

It is not only the level comparison: `reconcile` threads `project` into `gate_is_running` and
`advance_shared_tree` too, so the gate-lock guard read a lock path no gate ever writes.

WHY A NEW FILE. Every other `origin_reconcile` control in `tests/background/` is named for the
defect it pins, and none of them touches subject SELECTION — they all inject `project` explicitly,
which is exactly the parameter whose default was wrong, so none could have caught this.

THE SECOND DEFECT IN THE SAME DOOR (2026-09-25), controlled here because it is the same failure at
the same output: `--check` said something a reader could not tell from agreement. It reported the
BEHIND leg only, and `commits_ahead` — whose own docstring says "Reconcile has to mean BOTH
directions or it does not mean agreement" — had been live in `reconcile` since 2026-09-02 and was
never asked here. One requirement, two implementations, fixed in one. Measured: the 85h publish
wedge closed, the publish commit landed with its push deferred on a 30-minute throttle, and
`--check` answered `{"behind": 0}` rc=0 about a tree holding a landing that had never left the
machine. `1 if behind else 0` also made an UNREADABLE leg exit 0 — the code for agreement.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from background import origin_reconcile as R


def _repo_with_a_linked_worktree(tmp_path: Path) -> tuple[Path, Path]:
    """A real main worktree and a real linked worktree — git's own answer, not a fake's.

    A FAKE WOULD BE MORE PERMISSIVE THAN ITS SUBJECT here: the whole question is what
    `git rev-parse --git-common-dir` says from inside a linked worktree, so a stubbed git would
    be asserting the fixture's opinion of the answer rather than git's.
    """
    main = tmp_path / "main"
    main.mkdir()
    def git(cwd: Path, *args: str) -> None:
        subprocess.run(["git", *args], cwd=str(cwd), check=True,
                       capture_output=True, text=True)
    git(main, "init", "--quiet", "-b", "main")
    git(main, "config", "user.email", "t@example.com")
    git(main, "config", "user.name", "t")
    (main / "a.txt").write_text("a\n")
    git(main, "add", "a.txt")
    git(main, "commit", "--quiet", "-m", "one")
    linked = tmp_path / "linked"
    git(main, "worktree", "add", "--quiet", "--detach", str(linked))
    return main, linked


def test_the_subject_is_the_main_worktree_even_when_invoked_from_a_linked_one(tmp_path):
    """Resolved from git, so it holds from either side and is not a property of where pytest ran.

    THE PARTITION IN ONE ASSERT. Both directions matter and only asserting the linked one would
    pass on a function that returns the main tree unconditionally by accident of the fixture. A
    bare-repo/unreadable subject is the third state, asserted below.

    Fires on: returning `start` (or `PROJECT_DIR`) instead of resolving `--git-common-dir`.
    """
    main, linked = _repo_with_a_linked_worktree(tmp_path)
    from_linked = R.shared_tree(linked)
    from_main = R.shared_tree(main)
    assert from_linked == main and from_main == main, (
        "the remedy's subject depends on which tree it was invoked from, so run from a linked "
        "worktree it reconciles that worktree and reports on it: "
        "from_linked={} from_main={} main={}".format(from_linked, from_main, main))
    # AND IT IS NOT THE LINKED TREE, said separately because the equality above would also hold if
    # a future change made both sides return the linked path and the fixture's `main` moved.
    assert from_linked != linked


def test_an_unreadable_subject_REFUSES_and_never_falls_back_to_the_importing_tree(tmp_path):
    """`None`, not `PROJECT_DIR`. A fallback restores the defect exactly where git cannot answer.

    Fires on: `return start` / `return PROJECT_DIR` on the error branch.
    """
    not_a_repo = tmp_path / "bare"
    not_a_repo.mkdir()
    assert R.shared_tree(not_a_repo) is None, (
        "a subject that could not be established was defaulted rather than refused, so the "
        "reconciler would act on whichever tree this module was imported from")


def test_main_ASKS_ABOUT_the_shared_tree_and_names_it(monkeypatch, capsys, tmp_path):
    """The wiring, not the helper. A correct `shared_tree` nothing calls fixes nothing.

    `--check` is used because it is the one entry path that reads state without moving a tree, and
    the question here is only WHICH TREE is asked about.

    Fires on: `main` calling `commits_behind()` / `reconcile()` with no subject, which is exactly
    what it did.
    """
    main, linked = _repo_with_a_linked_worktree(tmp_path)
    monkeypatch.setattr(R, "PROJECT_DIR", linked)
    asked: list = []

    def spy(project=None):
        asked.append(project)
        return 3

    monkeypatch.setattr(R, "commits_behind", spy)
    rc = R.main(["--check"])

    assert asked == [main], (
        "`--check` asked about {} while the shared tree is {}, so the answer describes a tree "
        "nothing publishes from".format(asked, main))
    assert rc == 1, "3 commits behind reported as nothing to do"
    payload = json.loads(capsys.readouterr().out)
    # THE SUBJECT IS PRINTED. A caller who cannot see which tree was answered about cannot tell a
    # true LEVEL from this defect, which is how it survived: the output was indistinguishable.
    assert payload["subject"] == str(main) and payload["behind"] == 3


def _check(monkeypatch, capsys, main: Path, *, behind, ahead):
    """Run `--check` over one real tree with both legs injected, and return (rc, payload).

    The legs are injected rather than built, because the states this partition needs — unreadable
    origin, a tree ahead but not behind — are states about a REMOTE, and a fixture that fetches
    would be asserting the network's opinion of them. The TREE is real, so subject selection is
    still git's answer and not the fixture's.
    """
    monkeypatch.setattr(R, "PROJECT_DIR", main)
    monkeypatch.setattr(R, "commits_behind", lambda project=None: behind)
    monkeypatch.setattr(R, "commits_ahead", lambda project=None: ahead)
    rc = R.main(["--check"])
    return rc, json.loads(capsys.readouterr().out)


def test_the_fork_report_names_BOTH_legs_and_an_unpushed_landing_is_not_agreement(
        monkeypatch, capsys, tmp_path):
    """The whole partition in one control, so no state can quietly become unreachable.

    `LEVEL` is asserted alongside the three non-agreeing states deliberately: a door that refuses
    EVERYTHING passes every refusal leg written for it, and this door's rc is the only thing a
    caller reads. Asserting the four verdicts together is what makes the refusals mean something.

    Fires on: dropping `ahead` from the payload; `return 1 if behind else 0` (ahead-only and both
    -unreadable states go green); keying the rc to either leg alone.
    """
    main, _linked = _repo_with_a_linked_worktree(tmp_path)
    level_rc, level = _check(monkeypatch, capsys, main, behind=0, ahead=0)
    ahead_rc, ahead_only = _check(monkeypatch, capsys, main, behind=0, ahead=1)
    behind_rc, _behind_only = _check(monkeypatch, capsys, main, behind=2, ahead=0)
    unreadable_rc, unreadable = _check(monkeypatch, capsys, main, behind=None, ahead=None)

    assert (level_rc, ahead_rc, behind_rc, unreadable_rc) == (0, 1, 1, 1), (
        "the fork report's four states do not separate: level={} ahead_only={} behind_only={} "
        "unreadable={}. An ahead-only tree holds a landing that never left the machine, and an "
        "unreadable leg is the one state this door KNOWS it cannot answer -- neither is "
        "agreement.".format(level_rc, ahead_rc, behind_rc, unreadable_rc))
    # THE PAYLOAD, NOT ONLY THE CODE. A reader who cannot see the ahead leg cannot tell which of
    # the two forks they have, which is how the one-leg report survived: rc and text agreed.
    assert level["ahead"] == 0 and ahead_only["ahead"] == 1, (
        "`--check` does not name the AHEAD leg, so `behind: 0` reads as reconciled while the tree "
        "holds unpushed commits of its own: {} / {}".format(level, ahead_only))
    assert unreadable["behind"] is None and unreadable["ahead"] is None, (
        "an unreadable leg was rendered as a number, so 'could not tell' is published as a "
        "measurement: {}".format(unreadable))
