"""THE DEFECT: a feed stamped `git rev-parse HEAD` and read its inputs off the WORKING TREE.

Measured 2026-09-19 (`docs/staging/SEAT_RESULT_A_FEEDS_GIT_STAMP_IS_NOT_A_DESCRIPTION_OF_WHAT_
PRODUCED_IT_SO_NO_STANDPOINT_REPRODUCES_IT_2026-09-19.md`): `capabilities_door.json` recorded
`be7311e35`; regenerated in a clone standing AT `be7311e35`, `git_commit` came right and
`/scale/figures[0]/as_of` did not, because the published feed had read a `customers.json` newer
than that commit ever committed. The feed asserted its own provenance falsely in the one field a
reader would trust to settle exactly that question.

WHAT EACH TEST BELOW FIRES ON, because a guard that cannot fail is the thing this project pays for
most often:

  * `test_a_stamp_over_no_inputs_is_refused` — the fail-open. An empty input list makes
    `inputs_are_the_committed_bytes` vacuously true; the producer refuses rather than answers.
  * `test_a_modified_input_is_named_not_summarised` — the original defect, reproduced in a real
    git repository: dirty the input, and the stamp must say `false` AND name the path.
  * `test_every_state_is_reachable` — one control over the WHOLE partition rather than a leg per
    branch, because a classifier that returned `MODIFIED` for everything would pass every
    single-branch assertion written above it.
  * `test_the_coarse_question_catches_what_the_named_list_cannot` — the mutation that matters:
    drop `tree_was_clean` from `describes_its_inputs` and a stamp whose NAMED inputs are clean but
    whose tree is dirty reads as reproducible. That is this module's own defect one level up.
  * `test_a_feed_that_says_its_inputs_moved_yields_no_standpoint` — the comparator half. The
    refusal must be NO_STANDPOINT with the feed's reason, never a divergence blamed on the bytes.
  * `test_a_back_compatible_short_sha_does_not_cost_the_standpoint` — why the reserved key is read
    FIRST. `evidence.json` keeps a short `git_hash` beside the full stamp, and the scan would count
    the two forms as two commits and refuse a feed that had finally declared its standpoint.
  * `test_both_repaired_generators_publish_the_stamp` — binds the two real generators, so deleting
    the call from either reds here rather than being discovered by a future measurement.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from tools import provenance_stamp as ps
from tools.published_feed_regeneration_check import recorded_publication_commit

PROJECT = Path(__file__).resolve().parents[2]


def _repo(tmp_path: Path) -> Path:
    """A real git repository, because the whole subject is what git says about bytes on disk."""
    root = tmp_path / "repo"
    root.mkdir()
    run = lambda *a: subprocess.run(["git", "-C", str(root), *a], check=True,  # noqa: E731
                                    capture_output=True)
    run("init", "--quiet")
    run("config", "user.email", "t@t")
    run("config", "user.name", "t")
    (root / "input.json").write_text('{"as_of": "committed"}\n')
    (root / "other.txt").write_text("unrelated\n")
    run("add", "-A")
    run("commit", "--quiet", "-m", "seed")
    return root


def test_a_stamp_over_no_inputs_is_refused(tmp_path):
    """FIRES ON: a stamp that describes nothing and therefore answers `true` to everything."""
    root = _repo(tmp_path)
    with pytest.raises(ps.ProvenanceStampRefused) as exc:
        ps.stamp([], root)
    assert "vacuously" in str(exc.value)


def test_a_modified_input_is_named_not_summarised(tmp_path):
    """FIRES ON: the 2026-09-19 defect itself — an input read off the working tree.

    MUTATION: make `input_state` return COMMITTED whenever a blob exists at the commit (i.e. drop
    the `committed == on_disk` comparison) and this reds, because the dirtied path stops being
    named and the boolean flips to true.
    """
    root = _repo(tmp_path)
    (root / "input.json").write_text('{"as_of": "read off the working tree"}\n')

    block = ps.stamp([root / "input.json"], root)

    assert block["inputs_are_the_committed_bytes"] is False
    assert ps.describes_its_inputs(block) is False
    assert block["inputs"] == [{"path": "input.json", "state": ps.MODIFIED}]
    # The PATH is on the face of the refusal. A reader who only gets "false" cannot act on it.
    assert "input.json" in block["reason"]


def test_every_state_is_reachable(tmp_path):
    """ONE control over the WHOLE partition, not a leg per branch.

    A classifier stuck on any single value passes every single-state assertion that could be
    written above it. This asserts the five states are all reachable from real repository states,
    which is the assertion a stuck classifier cannot survive.
    """
    root = _repo(tmp_path)
    commit = ps.head_commit(root)
    assert commit is not None
    # COMMITTED is read BEFORE the tree is disturbed, out of the same repository as the other four
    # — a second repository would make this five readings of five worlds rather than one partition.
    committed_state = ps.input_state(root / "input.json", commit, root)

    (root / "dirty.json").write_text("x\n")            # present here, absent at the commit
    (root / "other.txt").write_text("changed\n")       # tracked, moved
    (root / "input.json").unlink()                     # committed there, gone now

    states = {
        ps.input_state(root / "input.json", commit, root),
        ps.input_state(root / "other.txt", commit, root),
        ps.input_state(root / "dirty.json", commit, root),
        ps.input_state(root / "never_existed.json", commit, root),
        committed_state,
    }

    assert states == {ps.COMMITTED, ps.MODIFIED, ps.NOT_IN_THE_COMMIT,
                      ps.DELETED_SINCE_THE_COMMIT, ps.ABSENT_AT_BOTH}
    assert ps.REPRODUCIBLE_STATES < states, (
        "the reproducible states must be a strict subset — if every state counted as reproducible "
        "the stamp could never say no"
    )


def test_the_coarse_question_catches_what_the_named_list_cannot(tmp_path):
    """FIRES ON: this module's own defect one level up — a partial input list read as complete.

    The named inputs are clean and something ELSE in the tree is not. Both generators repaired here
    read more than the paths they name (`wall_position` shells out over all of `company/`;
    `generate_evidence_data` counts `def test_` across every test file), so a stamp that answered
    only over its list would say "reproducible" about a run that is not.

    MUTATION: drop the `tree_was_clean` conjunct from `describes_its_inputs` and this reds.
    """
    root = _repo(tmp_path)
    (root / "other.txt").write_text("a lane this generator does not name\n")

    block = ps.stamp([root / "input.json"], root)

    assert block["inputs_are_the_committed_bytes"] is True, "the NAMED input really is clean"
    assert block["tree_was_clean"] is False, "and the tree really is not"
    assert ps.describes_its_inputs(block) is False, (
        "a stamp whose named inputs are clean but whose tree is dirty is not evidence the commit "
        "describes the run"
    )
    assert "uncommitted changes" in block["reason"]
    assert "other.txt" not in block["reason"], (
        "the coarse question names no path and must not appear to — a reader given a path would "
        "go and look at a file the generator never read"
    )


def test_an_untracked_file_counts_as_dirty(tmp_path):
    """FIRES ON: `git status` without `--untracked-files`.

    A new, uncommitted test file is invisible to a tracked-only diff and still moves
    `generate_evidence_data`'s `def test_` count. If untracked files did not count, the tree would
    read clean at exactly the moment a new test landed.
    """
    root = _repo(tmp_path)
    assert ps.tree_was_clean(root) is True
    (root / "brand_new.py").write_text("def test_x(): pass\n")
    assert ps.tree_was_clean(root) is False


def test_a_tree_git_cannot_read_is_cannot_tell_never_true(tmp_path):
    """FIRES ON: a `except: return False` or a `"unknown"` string where the answer is not known.

    Both earlier provenance defects in this repository shipped a STRING (`"latest"`, `"unknown"`)
    that satisfied every presence check forever. A silence must not be spellable as an answer.
    """
    not_a_repo = tmp_path / "bare"
    not_a_repo.mkdir()
    (not_a_repo / "input.json").write_text("{}\n")

    assert ps.head_commit(not_a_repo) is None
    assert ps.tree_was_clean(not_a_repo) is None
    block = ps.stamp([not_a_repo / "input.json"], not_a_repo)
    assert block["commit"] is None
    assert block["inputs_are_the_committed_bytes"] is None
    assert ps.describes_its_inputs(block) is False
    assert "cannot be told" in block["reason"]


def test_a_feed_that_says_its_inputs_moved_yields_no_standpoint(tmp_path):
    """FIRES ON: standing at a commit the feed has already said will not reproduce it.

    The comparator half of the repair. `recorded_publication_commit` must return the feed's OWN
    reason, so the outcome is a named refusal rather than a divergence blamed on the bytes.

    READ AGAINST A TMP REPOSITORY, NOT `PROJECT`. This first ran `ps.head_commit(PROJECT)` and
    skipped when it was None — which is silent in a `git archive` extract, where there is no
    `.git`. Mutation-tested 2026-09-19: with that skip in place, gutting the
    `describes_its_inputs` branch in `recorded_publication_commit` was caught by NO leg, and the
    run read `10 passed, 2 skipped`. A skip wears a pass's colour.
    """
    root = _repo(tmp_path)
    head = ps.head_commit(root)
    assert head is not None

    honest = {ps.STAMP_KEY: {"commit": head, "tree_was_clean": True,
                             "inputs_are_the_committed_bytes": True, "reason": "clean"}}
    sha, why = recorded_publication_commit(honest, root)
    assert sha == head, why

    moved = {ps.STAMP_KEY: {"commit": head, "tree_was_clean": True,
                            "inputs_are_the_committed_bytes": False,
                            "reason": "read off the working tree: site/data/customers.json"}}
    sha, why = recorded_publication_commit(moved, root)
    assert sha is None
    assert "site/data/customers.json" in why, (
        "the refusal must carry the feed's own reason — a refusal that does not say why is how "
        "this project discovers the refusal was wrong"
    )

    # And the SAME feed with the stamp's qualification deleted is accepted — which is what makes
    # the branch load-bearing rather than decoration. Without this leg the refusal above could be
    # coming from anything else in the function.
    unqualified = {ps.STAMP_KEY: {"commit": head, "tree_was_clean": True,
                                  "inputs_are_the_committed_bytes": True, "reason": "clean"}}
    assert recorded_publication_commit(unqualified, root)[0] == head


def test_a_back_compatible_short_sha_does_not_cost_the_standpoint(tmp_path):
    """FIRES ON: reading the reserved key AFTER the scan instead of before.

    `evidence.json` publishes a short `git_hash` for a human reader beside the full stamp. Both
    resolve to commits of this repository, so the all-scalars scan counts them as TWO and refuses
    — losing the standpoint of the one feed that had finally declared it.

    MUTATION: move the reserved-key branch below the `seen` loop and this reds.
    """
    root = _repo(tmp_path)
    head = ps.head_commit(root)
    assert head is not None

    both = {"git_hash": head[:9],
            ps.STAMP_KEY: {"commit": head, "tree_was_clean": True,
                           "inputs_are_the_committed_bytes": True, "reason": "clean"}}
    sha, why = recorded_publication_commit(both, root)
    assert sha == head, why

    # And the scan WOULD have refused it — which is what makes the ordering load-bearing rather
    # than a preference. Same two shas, no reserved key.
    scanned, scan_why = recorded_publication_commit({"git_hash": head[:9], "git_commit": head},
                                                    root)
    assert scanned is None and "more than one" in scan_why


def test_a_reserved_key_naming_a_commit_this_repo_does_not_have_is_refused(tmp_path):
    """FIRES ON: trusting the reserved key's contents because it is in the reserved place.

    A declared standpoint is still a claim about this repository. `"latest"` in the reserved key
    must refuse exactly as loudly as `"latest"` anywhere else did.
    """
    root = _repo(tmp_path)
    sha, why = recorded_publication_commit(
        {ps.STAMP_KEY: {"commit": "latest", "tree_was_clean": True,
                        "inputs_are_the_committed_bytes": True, "reason": "clean"}}, root)
    assert sha is None
    assert "not a commit of this repository" in why


@pytest.mark.parametrize("module,builder", [
    ("tools.generate_capabilities_door", "build"),
    ("tools.generate_evidence_data", "build_payload"),
])
def test_both_repaired_generators_publish_the_stamp(module, builder):
    """BINDS THE TWO REAL GENERATORS. Deleting the call from either reds here.

    The named inputs are asserted non-empty because that is the half a refactor silently loses: a
    stamp still present, still shaped right, and describing nothing.
    """
    import importlib

    payload = getattr(importlib.import_module(module), builder)()
    block = payload.get(ps.STAMP_KEY)
    assert isinstance(block, dict), f"{module} publishes no {ps.STAMP_KEY!r} block"
    assert block["inputs"], "a stamp naming no inputs describes nothing"
    assert set(block) == {"commit", "tree_was_clean", "inputs_are_the_committed_bytes",
                          "inputs", "reason"}
    assert block["reason"], "a stamp must always name its reason"


def test_the_published_feeds_carry_the_stamp_once_regenerated():
    """The DOOR leg: is the repair reaching the published bytes, or only the function?

    A generator repaired and never run is a repair nobody gets. This is deliberately tolerant of
    the feed being older than the repair — it names that state rather than reding on it, because
    the publish cycle runs every ~30 minutes and a commit-time red on "not yet republished" is a
    control keyed to today's answer.
    """
    for name in ("capabilities_door.json", "evidence.json"):
        path = PROJECT / "site" / "data" / name
        if not path.exists():
            pytest.skip(f"{name} is not published in this tree")
        doc = json.loads(path.read_text(encoding="utf-8"))
        block = doc.get(ps.STAMP_KEY)
        if block is None:
            continue  # published before the repair; the next cycle carries it
        assert isinstance(block, dict) and "commit" in block and "reason" in block, (
            f"{name} carries a {ps.STAMP_KEY!r} that is not a provenance stamp"
        )
