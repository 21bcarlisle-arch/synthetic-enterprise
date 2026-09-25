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
    # CORRECTED 2026-09-25, beside the claim it used to make. This line read
    # `assert "reconciler" in text` -- pinned to the one fixed remedy sentence the report printed
    # in every state. That sentence was wrong in two of the four provenance states (see
    # `provenance_lines`), so the literal went red the moment the report became honest: a control
    # keyed to today's answer reddening because the code got BETTER, which is exactly backwards.
    # Keyed to the property instead: a fault is never published without something to do about it,
    # and a path that cannot know the remedy must say so rather than guess.
    assert "REMEDY" in text, "the report must name the remedy, not only the fault"
    assert "reconciler" not in text, (
        "`compare()` cannot reach git, so it cannot know the live bytes are a snapshot of this "
        "checkout -- naming the reconciler here would be picking one of four remedies blind")
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


# ---------------------------------------------------------------------------------------------
# PROVENANCE: which revision the live bytes came from, which is a different question from
# whether they match the reference, and the one the REMEDY follows from.
# ---------------------------------------------------------------------------------------------

def _provenance_repo(tmp_path):
    """A repo whose hooks dir is INSIDE it, as the real one is, with three revisions of the hook.

    Returns (repo, blobs) where `blobs` maps a label to the text committed at that revision:
      `old`  -- an ancestor of the repo's HEAD
      `head` -- what HEAD says the hook is
      `side` -- a revision on a branch HEAD cannot reach, standing in for `origin/main`
    """
    repo = tmp_path / "repo"
    hooks = repo / "tools" / "git-hooks"
    hooks.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    subprocess.run(["git", "config", "core.hooksPath", str(hooks)], cwd=repo, check=True)

    def commit(text, message):
        (hooks / "pre-commit").write_text(text)
        subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
        subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm",
                        message, "--no-verify"], cwd=repo, check=True)

    texts = {"old": TRUNK,
             "head": TRUNK + "python3 -m tools.added_at_head\n",
             "side": TRUNK + "python3 -m tools.added_on_the_side\n"}
    commit(texts["old"], "old")
    commit(texts["head"], "head")
    subprocess.run(["git", "checkout", "-q", "-b", "side", "HEAD~1"], cwd=repo, check=True)
    commit(texts["side"], "side")
    subprocess.run(["git", "checkout", "-q", "main"], cwd=repo, check=True)
    (hooks / "pre-commit").write_text(texts["head"])
    return repo, texts


def test_all_four_provenance_states_are_reachable_over_ONE_repo_and_none_collapse(tmp_path):
    """THE DEFECT THIS NAMES: a provenance verdict that can only ever return one value looks
    identical to a working one, and every per-state test below would pass against a function
    that answered `head` unconditionally.

    Written as ONE control over the WHOLE partition rather than a leg per state, because this
    project has entered that trap by the other door: four separate tests each asserting their own
    state are all green against an implementation where two of the states are the same state.
    The assertion is that the four labels are FOUR, not that each one appears somewhere.

    MUTATION: collapse `PROV_OFF_HEAD` into `PROV_BEHIND` (drop the `merge-base --is-ancestor`
    branch and always return `PROV_BEHIND`) and this reds on the set size. Dropping the
    `PROV_MIXTURE` return reds it too.
    """
    repo, texts = _provenance_repo(tmp_path)
    hook = repo / "tools" / "git-hooks" / "pre-commit"
    seen = {}
    for label, text in [("head", texts["head"]), ("behind", texts["old"]),
                        ("off-head", texts["side"]), ("mixture", texts["head"] + "# hand edit\n")]:
        hook.write_text(text)
        seen[label] = lhd.live_provenance(hook, repo)

    assert all(p.undetermined is None for p in seen.values()), seen
    verdicts = [p.verdict for p in seen.values()]
    assert len(set(verdicts)) == 4, (
        f"four distinct conditions collapsed to {sorted(set(verdicts))} -- a partition that does "
        "not separate them cannot carry four different remedies")
    assert seen["head"].verdict == lhd.PROV_HEAD
    assert seen["behind"].verdict == lhd.PROV_BEHIND
    assert seen["off-head"].verdict == lhd.PROV_OFF_HEAD
    assert seen["mixture"].verdict == lhd.PROV_MIXTURE
    # The two that FOUND a commit must name it; a verdict of `behind` with no commit to restore
    # from is an accusation with no evidence.
    assert seen["behind"].commit and seen["off-head"].commit
    assert seen["mixture"].commit is None


def test_the_provenance_of_the_SHARED_hooks_is_the_same_from_a_linked_worktree(tmp_path):
    """THE DEFECT THIS NAMES, and it was live in this leg's first draft, caught by printing the
    verdict from the seat's own worktree before writing this test.

    `core.hooksPath` is an ABSOLUTE path into the shared tree and resolves to that same path from
    every linked worktree. A provenance leg that asks `HEAD` of the CALLER's tree is therefore
    asking about one checkout and answering about another's working copy. The first draft did
    exactly that and called the shared tree's hooks `behind`, telling the reader `git status`
    would show the path as modified -- false in both trees at once, and the kind of claim a lane
    acts on by restoring somebody else's file.

    The control is a DIFFERENTIAL over the same bytes: the answer must not depend on where the
    question was asked from. That is a property, not today's answer, so it survives every future
    change to what the states are called.

    MUTATION: drop the `owner = owning_checkout(...)` / `root = owner` lines in `live_provenance`
    and this reds -- the worktree is detached at HEAD~1, so its HEAD carries the `old` blob and
    the naive read grades the live copy `off-head` instead of `head`.
    """
    repo, texts = _provenance_repo(tmp_path)
    hook = repo / "tools" / "git-hooks" / "pre-commit"
    linked = tmp_path / "linked"
    subprocess.run(["git", "worktree", "add", "-q", "--detach", str(linked), "HEAD~1"],
                   cwd=repo, check=True)
    assert lhd.live_hooks_dir(linked) == hook.parent, "the premise: same hooks dir from both"

    from_owner = lhd.live_provenance(hook, repo)
    from_worktree = lhd.live_provenance(hook, linked)
    assert from_owner.verdict == lhd.PROV_HEAD, from_owner
    assert from_worktree.verdict == from_owner.verdict, (
        f"the same bytes graded {from_worktree.verdict!r} from the worktree and "
        f"{from_owner.verdict!r} from the owning tree -- the verdict is about the caller, not "
        "about the file")
    assert from_worktree.commit == from_owner.commit


def test_an_exhausted_scan_budget_is_undetermined_and_NOT_a_finding_of_mixture(tmp_path):
    """FAIL-CLOSED, on the leg where the flattering reading is the dangerous one. `mixture` sends
    a reader to hand-repair a file that no git operation will reconcile; "I ran out of budget
    before I found it" must never be published as that.

    MUTATION: return `Provenance(verdict=PROV_MIXTURE)` unconditionally at the end of
    `live_provenance` (dropping the budget check) and this reds.
    """
    repo, texts = _provenance_repo(tmp_path)
    hook = repo / "tools" / "git-hooks" / "pre-commit"
    hook.write_text(texts["old"])
    # The premise: with budget, these bytes ARE found. Without it, the answer must not flip to a
    # claim that they are in no commit.
    assert lhd.live_provenance(hook, repo, limit=10).verdict == lhd.PROV_BEHIND
    starved = lhd.live_provenance(hook, repo, limit=1)
    assert starved.verdict is None
    assert starved.undetermined and "NOT a finding of `mixture`" in starved.undetermined


def test_a_hooks_dir_outside_any_working_tree_is_undetermined_rather_than_a_verdict(tmp_path):
    """`core.hooksPath` may point anywhere. Outside a repo there is no HEAD the bytes could be a
    snapshot OF, and the honest answer is that the question cannot be asked -- not `mixture`,
    which would be the same words used for a genuine hand-edit.

    MUTATION: drop the `owner is None` branch and this reds (or errors) instead of reporting.
    """
    repo = _repo_with_hooks(tmp_path)          # this fixture puts the live dir OUTSIDE the repo
    d = lhd.drift(repo, reference="HEAD")
    assert d.provenance is not None, "the leg must be reached even when it cannot answer"
    assert d.provenance.verdict is None
    assert "not inside any git working tree" in (d.provenance.undetermined or "")
    assert "CANNOT TELL which revision" in lhd.report(d)


def test_a_copy_HAND_PATCHED_from_the_reference_reads_byte_identical_and_is_STILL_qualified(
        tmp_path):
    """THE DEFECT THIS NAMES, and it is the whole reason the provenance leg exists. Measured on
    the shared tree 2026-09-25: a lane wrote `origin/main`'s hook blobs into the working copy by
    hand (`8e40bb205`'s own commit body records it), leaving the checkout exactly as far behind as
    it was. For the thirty minutes that patch survived, the byte comparison would have reported
    the chain was the reference's "byte for byte" -- its cleanest verdict -- while the condition
    this module exists to detect was untouched underneath. Then the checkout advanced and the
    patch was gone, silently.

    So the byte-identical branch must NOT be an unqualified pass, and its remedy must not be the
    advance that destroys the patch.

    MUTATION: drop `*provenance_lines(d.provenance)` from the `d.clean and not d.bytes_differ`
    return in `report` and this reds -- the report goes back to one unqualified green sentence.
    """
    repo, texts = _provenance_repo(tmp_path)
    hook = repo / "tools" / "git-hooks" / "pre-commit"
    hook.write_text(texts["side"])             # the hand-patch: another revision's bytes, verbatim
    d = lhd.drift(repo, reference="side")      # graded against the revision it was copied from

    assert d.clean and not d.bytes_differ, (
        "the premise: a hand-patch from the reference IS byte-identical to it, which is why the "
        "byte comparison alone cannot see this condition")
    text = lhd.report(d)
    assert "byte for byte" in text, "the premise must still be reported truthfully"
    assert "CANNOT REACH" in text, (
        "a green byte verdict over bytes belonging to no reachable commit must be qualified on "
        "the same surface, not left to be read as a clean bill")
    assert "remedy is NOT to advance" in text, (
        "advancing the checkout is what DISCARDS a hand-patch -- the one remedy the old report "
        "printed unconditionally is the one that is wrong here")


def test_the_landing_door_does_not_go_SILENT_on_the_very_state_the_provenance_leg_is_for(
        tmp_path):
    """THE DEFECT THIS NAMES, found by reading the call site after the report was already right.

    `surgical_land._report_live_hook_drift` returned early on `verdict.clean`. A working copy
    hand-patched from the trunk is clean BY CONSTRUCTION -- it is the trunk's own bytes -- so the
    door printed nothing at all in the condition this whole leg exists to surface. The
    qualification was reaching `report()` and dying one frame above it.

    Graded at the PROPERTY the door asks, not at the door's source text: `needs_reader` must be
    true for a clean-but-unreachable copy and false for a clean snapshot of HEAD, because those
    are the two readings that used to be the same reading.

    MUTATION: restore `needs_reader` to `return not self.clean` and this reds on the first
    assertion. Making it `return True` unconditionally reds on the second -- that arm is why the
    quiet case is asserted here too, rather than trusted.
    """
    repo, texts = _provenance_repo(tmp_path)
    hook = repo / "tools" / "git-hooks" / "pre-commit"

    hook.write_text(texts["side"])                      # the hand-patch
    patched = lhd.drift(repo, reference="side")
    assert patched.clean and not patched.bytes_differ, "the premise: it IS clean"
    assert patched.needs_reader, (
        "a clean chain over bytes from an unreachable commit still has something to tell a lane "
        "about to trust a green gate -- this is the leg the landing door used to skip")

    hook.write_text(texts["head"])                      # an ordinary, honest snapshot
    snapshot = lhd.drift(repo, reference="main")
    assert snapshot.provenance is not None
    assert snapshot.provenance.verdict == lhd.PROV_HEAD
    assert not snapshot.needs_reader, (
        "a snapshot of HEAD matching the trunk must stay QUIET -- a door that speaks on every "
        "landing is a door nobody reads, which is the mistake this one already paid for once")


def test_the_landing_door_asks_needs_reader_and_not_clean():
    """The wiring leg. The property above can be perfect while the door goes on asking the old
    question, and nothing else in the tree compares the two.

    Read from the module's own source because the door's early return has no return value to
    observe -- it prints or it does not, from inside a function that takes a live repo. The
    function's presence is asserted BEFORE its body is sliced: `str.split` on a name that is not
    there yields an empty tail, and `"verdict.clean" not in ""` is green forever.

    MUTATION: put `if verdict.clean and not verdict.bytes_differ: return` back and this reds.
    """
    # CODE only: `code_text` blanks comments and prose strings, so the comment beside the door
    # explaining the fix cannot be what satisfies this test.
    src = python_code_text.code_text(
        (ROOT / "tools" / "surgical_land.py").read_text(encoding="utf-8"))
    assert src is not None
    assert "_say_which_hook_chain_the_other_door_runs" in src, (
        "the door was renamed -- this control grades a function by name and must be repointed "
        "rather than left passing on an empty slice")
    door = src.split("def _say_which_hook_chain_the_other_door_runs")[1].split("\ndef ")[0]
    assert "needs_reader" in door, "the landing door must ask the question that sees the patch"
    assert "verdict.clean" not in door, (
        "asking `clean` here is the defect: a hand-patch is clean and the reader hears nothing")


def test_a_DIVERGED_checkout_is_told_the_advance_it_is_waiting_for_will_never_run(tmp_path):
    """THE DEFECT THIS NAMES. Every remedy this module prints for a stale checkout ends in "the
    reconciler advancing the SHARED checkout". `advance_shared_tree` fast-forwards, and git
    refuses to fast-forward a diverged branch -- so for a tree holding local commits the trunk
    does not have, the remedy is an operation that is structurally refused, every time, forever.
    The reader waits for something that cannot happen and the missing gate goes on not running.

    Measured on the shared tree the day this landed: 9 ahead, `merge-base --is-ancestor HEAD
    origin/main` false, and the ahead leg itself unpromotable on one receiptless commit.

    Keyed to the PROPERTY (can this checkout fast-forward onto the reference?) and not to a count,
    so it does not go red the day the shared tree is levelled -- it goes QUIET, which is correct.

    MUTATION: `return None` at the top of `advance_blocked_reason` and this reds on the diverged
    arm. Returning the reason unconditionally reds the levelled arm below, which is why both are
    asserted.
    """
    repo, texts = _provenance_repo(tmp_path)

    # LEVEL FIRST: `side` is reachable from nothing this branch has diverged onto, so main can
    # still fast-forward nowhere -- use main against itself for the quiet arm.
    assert lhd.advance_blocked_reason(repo, "main") is None, (
        "a checkout that IS the reference blocks nothing, and a line printed here would be the "
        "alarm-on-every-run this module already paid for once")

    # NOW DIVERGED: `side` has a commit main does not, and main has one side does not.
    blocked = lhd.advance_blocked_reason(repo, "side")
    assert blocked is not None, "a diverged checkout cannot fast-forward and must be told so"
    assert "DIVERGED" in blocked and "ff-only" in blocked
    assert "will NOT close on its own" in blocked, (
        "the reader's actual question is whether waiting works; the answer is no and it must be "
        "in the words, not inferable from them")

    # BOTH REPORT BRANCHES, and the second one is here because the first draft of this control
    # did not have it: `report` returns early when the chain is clean, so an assertion made only
    # over a clean verdict was satisfied by the early branch and stayed GREEN when the append was
    # deleted from the other one. A mutation that does not fire is a missing test until proven an
    # equivalence, and these two appends are not equivalent -- they are two literals in two
    # returns, and deleting either leaves a diverged reader unwarned in half the states.
    hook = repo / "tools" / "git-hooks" / "pre-commit"

    hook.write_text(texts["side"])                      # clean: the early, byte-identical return
    clean_text = lhd.report(lhd.drift(repo, reference="side"))
    assert lhd.drift(repo, reference="side").clean, "the premise: this branch IS the clean one"
    assert "ADVANCE IS NOT AVAILABLE" in clean_text, (
        "the blocker must reach the same surface as the remedy it overrides -- a caveat in a "
        "different place from the claim it qualifies is a caveat nobody reads")

    hook.write_text(texts["old"])                       # differs: a gate the reference declares
    differs = lhd.drift(repo, reference="side")
    assert not differs.clean and differs.missing, "the premise: this branch is the differing one"
    assert "ADVANCE IS NOT AVAILABLE" in lhd.report(differs), (
        "the branch that reports a MISSING gate is the one whose reader is most likely to go and "
        "wait for the advance, so it is the branch that least affords losing this line")
