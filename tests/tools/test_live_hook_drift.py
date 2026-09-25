"""The detector that says whether the gates git RUNS are the gates the trunk DECLARES.

WHY THIS CONTROL EXISTS (2026-09-25). `core.hooksPath` resolves to the shared tree's WORKING
COPY of `tools/git-hooks/`. When that checkout falls behind, a gate added to the trunk chain
runs NOWHERE, and every commit made afterwards reports a green gate that never contained it.
`934343669` landed `hook_gate_mark --record` into the chain and it was inert on the day it
landed. Nothing in the tree could notice; the seat found it by grepping the live hook by hand.

WHAT IS GRADED HERE AND WHAT DELIBERATELY IS NOT. These tests grade the DETECTOR against
synthetic hook texts, never the live checkout's current state. A control pinned to "the shared
tree is 49 behind today" would go green the moment somebody ran the reconciler and could never
go red again for the right reason -- and in the meantime it would red every lane for a condition
no lane can fix from inside its own commit. The live reading belongs on a loud surface
(`surgical_land`, `--explain`), which is where it is. One test does read the real hook, and it
reads it for REACHABILITY -- that the parser finds gates in real bytes at all -- not for a
verdict.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools import live_hook_drift as lhd
from tools import python_code_text

ROOT = Path(__file__).resolve().parents[2]

#: A hook the trunk might declare. Four gates, two invocation shapes (`-m` and a script path),
#: and a shell tail on each, because the real hook has all of those.
TRUNK = """#!/bin/sh
set -e
# a comment that mentions python3 but is not a command
python3 -m tools.stale_copy_refusal --staged || exit 1
python3 tools/pre_commit_test_gate.py || exit 1
python3 -m tools.company_network_isolation --gate || exit 1
python3 -m tools.hook_gate_mark --record
"""


def _repo_with_hooks(tmp_path, *, committed: str | None = TRUNK,
                     live: str | None = TRUNK):
    """A whole repository whose hooks dir and committed hook are both under this test's control.

    WHY THESE TESTS DO NOT USE THE REAL TREE, and it was learned by landing this file. The first
    draft called `drift(root=ROOT)` and asserted on the reason it got back. Inside
    `surgical_land`'s gate the extract is a STANDALONE repo with its own empty `.git/hooks` and no
    `origin/main`, so both refusal legs were reachable there in the wrong order and each test
    passed on the OTHER one's reason -- green in the worktree, red in the gate, and green again
    for the wrong cause if the order had been different. A control keyed to where pytest happened
    to run grades the environment, not the code.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    tracked = repo / "tools" / "git-hooks"
    tracked.mkdir(parents=True)
    (tracked / "pre-commit").write_text(committed if committed is not None else "#!/bin/sh\n")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "hooks",
                    "--no-verify"], cwd=repo, check=True)
    live_dir = tmp_path / "live-hooks"
    live_dir.mkdir()
    if live is not None:
        (live_dir / "pre-commit").write_text(live)
    subprocess.run(["git", "config", "core.hooksPath", str(live_dir)], cwd=repo, check=True)
    return repo


def _without(text: str, needle: str) -> str:
    return "\n".join(ln for ln in text.splitlines() if needle not in ln) + "\n"


def test_a_gate_the_trunk_declares_and_the_live_chain_omits_is_named_missing():
    """THE DEFECT THIS NAMES: the live chain has fallen behind and a whole gate is simply not
    run, so a green result from that chain does not mean the gate passed.

    MUTATION: drop the `d.missing = [...]` assignment in `compare` and this reds.
    """
    d = lhd.compare(_without(TRUNK, "hook_gate_mark"), TRUNK)
    assert d.missing == ["hook_gate_mark"]
    assert not d.clean, "a chain missing a declared gate is not a clean comparison"


def test_the_three_verdicts_are_each_reachable_in_one_comparison():
    """One control over the WHOLE partition rather than a leg per branch.

    A verdict builder that returned three empty lists would pass every single-branch test that
    only asks `not d.retired`. This asserts all three states are ENTERED by one live text, so a
    collapse of any one of them into "nothing here" reds.

    MUTATION: make `altered` (or `retired`, or `missing`) unconditionally `[]` and this reds.
    """
    live = """#!/bin/sh
python3 -m tools.stale_copy_refusal --staged || exit 1
python3 tools/pre_commit_test_gate.py || exit 1
python3 -m tools.company_network_isolation --check || exit 1
python3 -m tools.a_gate_the_trunk_deleted || exit 1
"""
    d = lhd.compare(live, TRUNK)
    assert d.missing == ["hook_gate_mark"]
    assert d.retired == ["a_gate_the_trunk_deleted"]
    assert [s for s, _, _ in d.altered] == ["company_network_isolation"]
    subject, live_argv, ref_argv = d.altered[0]
    assert "--check" in live_argv and "--gate" in ref_argv, (
        "an ALTERED verdict must carry BOTH argvs -- a reader cannot act on 'it differs'")
    assert not d.clean


def test_an_identical_chain_is_clean_so_green_is_reachable():
    """THE ANTI-TAUTOLOGY ARM. A detector that called every comparison dirty would pass all
    three tests above and be worthless. Keyed to the SAME attribute they assert false.

    MUTATION: make `Drift.clean` return False unconditionally and this reds.
    """
    d = lhd.compare(TRUNK, TRUNK)
    assert d.clean is True
    assert d.missing == [] and d.retired == [] and d.altered == []


def test_a_chain_that_differs_only_in_COMMENTS_is_still_clean():
    """The control must not shout on the 805 bytes of prose that make up most of a hook diff.

    MUTATION: compare raw bytes instead of invocations in `compare` and this reds.
    """
    d = lhd.compare(TRUNK + "# a later comment nobody needs to be warned about\n", TRUNK)
    assert d.clean is True


def test_a_reference_that_parses_to_no_gates_is_undetermined_and_NOT_clean():
    """THE FAIL-CLOSED LEG, and it guards the direction that actually kills this class. If the
    reader breaks, both sides parse to nothing, every comparison is trivially true and the
    control reports a clean bill forever while the chain rots.

    MUTATION: delete the `if not ref_commands` guard in `compare` and this reds -- without it the
    verdict is `clean is True`, which is the exact failure.
    """
    d = lhd.compare(TRUNK, "#!/bin/sh\necho no gates here\n")
    assert d.undetermined is not None
    assert "vacuously green" in d.undetermined
    assert d.clean is False, "an unmade comparison is NOT a clean one"


def test_an_unresolvable_reference_is_undetermined_and_NOT_clean(tmp_path):
    """`git show <rev>:<path>` failing must be a named refusal, never an absent problem.

    The live hook is READABLE here, so the only thing that can refuse is the reference. That is
    the point: a test that let both legs be reachable would pass on whichever fired first.

    MUTATION: return `Drift()` without setting `undetermined` on the `_show` failure and this
    reds on `clean`.
    """
    repo = _repo_with_hooks(tmp_path)
    d = lhd.drift(root=repo, reference="refs/heads/a-branch-that-does-not-exist")
    assert d.undetermined is not None
    assert "does not resolve" in d.undetermined
    assert d.clean is False


def test_a_resolvable_reference_over_the_same_fixture_is_CLEAN():
    """The arm that proves the two tests above are not passing because the fixture is broken.

    Same builder, same repo shape, a reference that resolves and a live hook that matches: the
    verdict must be clean. Without this, a `_repo_with_hooks` that silently produced an unusable
    repo would make every refusal leg green for the wrong reason.

    MUTATION: have `_repo_with_hooks` write a different live hook and this reds.
    """
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        repo = _repo_with_hooks(Path(tmp))
        d = lhd.drift(root=repo, reference="HEAD")
    assert d.undetermined is None, d.undetermined
    assert d.clean is True


def test_an_unreadable_live_hook_is_undetermined_and_NOT_clean(tmp_path):
    """An unreadable gate chain is a FAILED reading. The same rule `surgical_land.run_gate`
    already applies to a missing hook, applied to the question of WHICH hook.

    The reference RESOLVES here, so the only thing that can refuse is the hook -- the mirror of
    the test above, and the pair is what stops either passing on the other's reason.

    MUTATION: swallow the `OSError` and fall through to `compare` and this reds.
    """
    repo = _repo_with_hooks(tmp_path, live=None)
    d = lhd.drift(root=repo, reference="HEAD")
    assert d.undetermined is not None
    assert "could not be read" in d.undetermined
    assert d.clean is False


def test_the_hooks_dir_is_asked_of_git_so_core_hookspath_is_honoured(tmp_path):
    """THE DEFECT THIS NAMES, and it is the one the whole module rests on: a hand-built
    `<root>/.git/hooks` gives the WRONG answer whenever `core.hooksPath` is set, and this
    repository's entire problem is that the right answer is a directory somewhere else.

    Both halves are exercised: an unset `core.hooksPath` must give the private hooks dir, and a
    set one must give the configured directory, or the reader is keyed to today's config rather
    than to what git does.

    MUTATION: replace `live_hooks_dir` with `root / ".git" / "hooks"` and the second half reds.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    default = lhd.live_hooks_dir(repo)
    assert default.name == "hooks", f"unset config should give a hooks dir, got {default}"

    elsewhere = tmp_path / "somewhere-else"
    elsewhere.mkdir()
    subprocess.run(["git", "config", "core.hooksPath", str(elsewhere)], cwd=repo, check=True)
    assert lhd.live_hooks_dir(repo) == elsewhere
    assert lhd.live_hooks_dir(repo) != default


def test_the_hooks_dir_resolved_from_a_LINKED_WORKTREE_is_the_configured_one(tmp_path):
    """The case that made this a defect rather than a curiosity. Every seat runs in a linked
    worktree, and from there the naive expression resolves to the worktree's OWN private hooks
    dir -- which is empty, and would make this control report a clean bill from the one place
    the seat actually works.

    MUTATION: as above; this is the leg that reds when `--git-path` is replaced by a hand-built
    path, because the worktree's git dir is not the repo's.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    (repo / "seed").write_text("seed\n")
    subprocess.run(["git", "add", "seed"], cwd=repo, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "seed",
                    "--no-verify"], cwd=repo, check=True)
    shared_hooks = repo / "tools" / "git-hooks"
    shared_hooks.mkdir(parents=True)
    subprocess.run(["git", "config", "core.hooksPath", str(shared_hooks)], cwd=repo, check=True)

    linked = tmp_path / "linked"
    subprocess.run(["git", "worktree", "add", "-q", "--detach", str(linked)], cwd=repo, check=True)
    assert lhd.live_hooks_dir(linked) == shared_hooks
    assert lhd.live_hooks_dir(linked) != linked / ".git" / "hooks"


def test_the_parser_finds_gates_in_the_REAL_hook_so_the_control_is_reachable():
    """REACHABILITY ON REAL BYTES, not a verdict on them. If this module's parser could not read
    the repository's own hook, every synthetic test above would still pass and the live report
    would be a permanent, silent all-clear.
    """
    text = subprocess.run(["git", "show", f"HEAD:{lhd.HOOK_REL}"], cwd=ROOT,
                          capture_output=True, text=True, check=True).stdout
    commands = lhd.hook_invocations(text)
    assert len(commands) >= 15, (
        f"only {len(commands)} python3 invocations parsed out of the real hook -- the reader is "
        "broken, not the hook")
    subjects = [lhd.invocation_subject(c) for c in commands]
    assert len(set(subjects)) >= 15
    assert all(s and not s.startswith("-") for s in subjects), subjects


def test_a_command_with_no_subject_raises_rather_than_returning_a_falsy_key():
    """A parser that returned `""` for an unparseable line would silently collapse several gates
    into one key and report them as neither missing nor present.

    MUTATION: `return ""` instead of raising and this reds.
    """
    with pytest.raises(ValueError):
        lhd.invocation_subject("python3 -m")


def test_the_report_NAMES_the_missing_gate_and_the_remedy():
    """A refusal that does not name its reason is how this class stayed invisible. The report is
    the whole product here -- the module blocks nothing by default -- so its content is the
    behaviour under test, not decoration.

    MUTATION: drop the `MISSING` loop from `report` and this reds.
    """
    text = lhd.report(lhd.compare(_without(TRUNK, "hook_gate_mark"), TRUNK))
    assert "hook_gate_mark" in text
    assert "MISSING" in text
    assert "reconciler" in text, "the report must name the remedy, not only the fault"
    assert "restart" in text, "and must name the remedy that is WRONG, which was tried first"


def test_the_report_of_an_undetermined_verdict_does_not_read_as_a_PASS():
    """'We cannot tell' is a result and it belongs on the surface. A report that printed the
    clean sentence when the comparison failed would be the worst outcome available here.

    MUTATION: return the clean sentence for an undetermined verdict and this reds.
    """
    text = lhd.report(lhd.Drift(undetermined="the reference did not resolve"))
    assert "CANNOT TELL" in text
    assert "IS origin/main's" not in text


def test_the_reporter_IS_REACHED_from_the_landing_door_and_not_only_from_the_hook():
    """THE DEFECT THIS NAMES, and it is the one that would make every test above worthless: every
    control on a detector stays green while no production caller reaches it.

    The hook line is NOT sufficient on its own and cannot be, because it is read from the working
    copy it grades -- so a wiring check that only looked at `tools/git-hooks/pre-commit` would be
    satisfied by the inert half. `tools/surgical_land.py` is resolved from the COMMITTING tree on
    every landing, which is the channel the outage cannot silence, so that is the caller asserted
    here.

    MUTATION: delete the `_say_which_hook_chain_the_other_door_runs(root)` call from `land` and
    this reds. Deleting the hook line reds the OTHER leg below, separately, so the two wirings
    cannot cover for one another.
    """
    # CODE, NOT TEXT, and the census that refused the first draft of this test was right to.
    # `tools/surgical_land.py` explains this whole mechanism in a comment beside `HOOK_REL`, so a
    # substring read of the raw bytes is satisfied by the PROSE -- deleting the call would have
    # left this green. `searchable()` blanks comments and docstrings, so what is asserted below is
    # the call.
    source = python_code_text.searchable(
        (ROOT / "tools" / "surgical_land.py").read_text(encoding="utf-8"))
    assert "live_hook_drift" in source, "surgical_land no longer imports the reporter"
    assert "_say_which_hook_chain_the_other_door_runs(root)" in source, (
        "the reporter is imported and never called from `land` -- a detector with no production "
        "caller is green forever and tells nobody anything")


def test_the_hook_line_exists_and_cannot_refuse_a_commit():
    """The other half of the wiring, and its SHAPE is the assertion rather than its presence.

    A bare `python3 -m tools.live_hook_drift` under this hook would abort every commit the moment
    the chain drifted -- which is precisely the state no lane can fix from inside its own commit,
    and the fastest route to the line being deleted. The `|| true` is what makes it a report.

    MUTATION: drop the `|| true`, or delete the line, and this reds.
    """
    hook = (ROOT / "tools" / "git-hooks" / "pre-commit").read_text(encoding="utf-8")
    lines = [ln.strip() for ln in hook.splitlines()
             if ln.strip().startswith("python3") and "live_hook_drift" in ln]
    assert lines, "the hook does not run the reporter at all"
    assert all(ln.endswith("|| true") for ln in lines), lines
    assert not any("--gate" in ln for ln in lines), (
        "the hook must not pass --gate: that turns a condition the committing lane cannot fix "
        "into a refusal it will switch off")


def test_an_UNCONFIGURED_repo_is_its_own_verdict_and_not_a_permanent_alarm(tmp_path):
    """THE DEFECT THIS NAMES, and it was found by this module's own second landing: a repository
    with no `core.hooksPath` has no working copy to be behind, and `<git-dir>/hooks/pre-commit`
    is missing in every repo that never installed one -- so the unreadable-hook refusal claimed
    that state and shouted CANNOT TELL. `surgical_land` builds a standalone extract per landing,
    so that would have fired on EVERY landing this repository ever makes. A fail-closed message
    that is correct and permanent is a message nobody reads by the third one.

    It is a third state rather than a silence: an ordinary clone that never ran
    `install_git_hooks.sh` is running NO gates, and a reader wants that told plainly once.

    MUTATION: delete the `configured_hooks_path(root) is None` short-circuit in `drift` and this
    reds -- the verdict becomes `undetermined`, which is the alarm that cried wolf.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    assert lhd.configured_hooks_path(repo) is None

    d = lhd.drift(root=repo)
    assert d.unconfigured is True
    assert d.undetermined is None, (
        "an unconfigured repo is NOT an unmade comparison -- there is nothing to compare")
    assert d.clean is False, "and it is not a clean bill either; it is its own state"

    text = lhd.report(d)
    assert "core.hooksPath is NOT set" in text
    assert "install_git_hooks.sh" in text, "the report must name what to do about it"
    assert "CANNOT TELL" not in text


def test_a_CONFIGURED_repo_over_the_same_shape_still_reaches_the_comparison(tmp_path):
    """The arm that keeps the short-circuit above from swallowing every reading. Same builder,
    `core.hooksPath` set: the verdict must be a real comparison, not `unconfigured`.

    MUTATION: make `configured_hooks_path` return None unconditionally and this reds.
    """
    repo = _repo_with_hooks(tmp_path, live=_without(TRUNK, "hook_gate_mark"))
    assert lhd.configured_hooks_path(repo) is not None
    d = lhd.drift(root=repo, reference="HEAD")
    assert d.unconfigured is False
    assert d.missing == ["hook_gate_mark"]
