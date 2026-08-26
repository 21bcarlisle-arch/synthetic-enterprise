"""R15 falsifiers for the landed-manifest control, both ways.

The control's own named defect is: a document claims a path LANDED and no tree carries that
path's content. Every test here builds a REAL git repository with the shape under test --
never a mock -- because the whole subject is what git plumbing reports about a tree and an
index, and both sides mocked is a pair that passes while the seam is broken.

Scratch repos go under `/var/tmp`, not `gettempdir()`. `/tmp` on this box is a 7.8G tmpfs
backed by the same RAM the suites need, and repo-shaped extracts under it are what filled it
on 2026-08-14 (`WORKER_FINDING_THE_LANDING_TOOL_EXTRACTS_INTO_THE_TMPFS_THE_GATE_WAS_MOVED_OFF`).
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools.landed_manifest_check import (  # noqa: E402
    asserts_landing,
    is_path_like,
    manifest_paths,
    run_at_tree,
)

SCRATCH_ROOT = Path("/var/tmp")

REAL_INSTANCE = (
    REPO / "docs" / "staging"
    / "WORKER_FINDING_A_PATHSPEC_COMMIT_LANDED_THE_CONSUMER_AND_LEFT_THE_SUPPLIER_STAGED_2026-08-14.md"
)


def _git(repo: Path, *args: str) -> str:
    out = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True, check=False)
    assert out.returncode == 0, f"git {' '.join(args)} rc={out.returncode}: {out.stderr}"
    return out.stdout.strip()


@pytest.fixture
def repo():
    """A real repo with one commit, `tools/supplier.py` tracked, and a staging room."""
    with tempfile.TemporaryDirectory(prefix="landedman-", dir=str(SCRATCH_ROOT)) as tmp:
        r = Path(tmp)
        _git(r, "init", "-q", "-b", "main")
        _git(r, "config", "user.email", "t@example.com")
        _git(r, "config", "user.name", "t")
        (r / "tools").mkdir()
        (r / "docs" / "staging").mkdir(parents=True)
        (r / "tools" / "supplier.py").write_text("OLD = 1\n")
        _git(r, "add", "-A")
        _git(r, "commit", "-qm", "base")
        yield r


def _write_doc(repo: Path, name: str, body: str) -> str:
    rel = f"docs/staging/{name}"
    (repo / rel).write_text(body)
    return rel


def _tree_of_index(repo: Path) -> str:
    return _git(repo, "write-tree")


def _head_tree(repo: Path) -> str:
    return _git(repo, "rev-parse", "HEAD^{tree}")


CLAIM = "## What landed this tick\n\nThe supplier half: `tools/supplier.py`.\n"


# ---------------------------------------------------------------- FIRES (the control works)

def test_fires_when_a_claimed_path_is_absent_from_the_tree(repo):
    """Clause 1: claimed LANDED, in no tree at all."""
    doc = _write_doc(repo, "F_absent.md", "# f\n\n## What landed this tick\n\n`tools/ghost.py`.\n")
    _git(repo, "add", doc)
    findings, report = run_at_tree(_tree_of_index(repo), since_tree=_head_tree(repo), root=repo)
    assert any("tools/ghost.py" in f and "ABSENT" in f for f in findings), findings
    assert report["paths_checked"] == 1


def test_fires_on_the_2026_08_14_shape_staged_but_not_carried(repo):
    """Clause 2, THE historical shape: the path exists at HEAD, the claimed content is in the
    index, and this commit's pathspec excludes it. Path-existence alone is blind here --
    `tools/simplifications_store.py` existed at parent 75290668f (blob 4ec6f9bf) and the
    finding was still false."""
    (repo / "tools" / "supplier.py").write_text("NEW = 2\n")   # the 'landed' content...
    _git(repo, "add", "tools/supplier.py")                      # ...staged only
    doc = _write_doc(repo, "F_staged.md", "# f\n" + CLAIM)
    _git(repo, "add", doc)

    # The tree this commit WOULD create if it carried the doc alone: HEAD + the doc.
    head = _head_tree(repo)
    tree = _git(repo, "rev-parse", f"{head}")  # start from HEAD's tree
    # Build a pathspec-shaped tree: HEAD plus only the document.
    idx = repo / ".git" / "pathspec-index"
    env_tree = subprocess.run(
        ["git", "read-tree", head], cwd=str(repo), capture_output=True, text=True,
        env={**dict(__import__("os").environ), "GIT_INDEX_FILE": str(idx)}, check=False)
    assert env_tree.returncode == 0, env_tree.stderr
    subprocess.run(["git", "update-index", "--add", doc], cwd=str(repo), check=True,
                   env={**dict(__import__("os").environ), "GIT_INDEX_FILE": str(idx)})
    tree = subprocess.run(["git", "write-tree"], cwd=str(repo), capture_output=True, text=True,
                          env={**dict(__import__("os").environ), "GIT_INDEX_FILE": str(idx)},
                          check=True).stdout.strip()

    findings, _ = run_at_tree(tree, since_tree=head, root=repo)
    assert any("tools/supplier.py" in f and "INDEX" in f for f in findings), findings


def test_mutation_the_control_is_green_when_the_claim_is_true(repo):
    """The other way: the same commit that makes the claim also lands the path. A control
    that reds here would refuse every honest landing, which is how a gate gets disabled."""
    (repo / "tools" / "supplier.py").write_text("NEW = 2\n")
    doc = _write_doc(repo, "F_ok.md", "# f\n" + CLAIM)
    _git(repo, "add", "tools/supplier.py", doc)
    findings, report = run_at_tree(_tree_of_index(repo), since_tree=_head_tree(repo), root=repo)
    assert findings == [], findings
    assert report["paths_checked"] == 1


def test_mutation_an_edited_but_not_git_added_path_this_commit_carries_is_green(repo):
    """The false positive this control refused its OWN announcing commit with.

    `git commit -- <pathspec>` builds the resulting tree from the WORKING TREE, so a path
    that was edited and never `git add`ed reads index(==HEAD) != tree(new content). That is
    the commit LANDING the claim, not a claim about content no tree carries. Red here and
    the control refuses the ordinary edit-then-commit-by-pathspec shape, which is most of
    them. The discriminator is `staged != at_head`, and the 2026-08-14 shape above -- where
    the index held content HEAD did not -- must keep firing; both tests must pass together
    or the discrimination is a tautology in one direction.
    """
    (repo / "tools" / "supplier.py").write_text("NEW = 2\n")   # edited, NOT `git add`ed
    doc = _write_doc(repo, "F_wt.md", "# f\n" + CLAIM)

    head = _head_tree(repo)
    idx = repo / ".git" / "wt-index"
    env = {**os.environ, "GIT_INDEX_FILE": str(idx)}
    subprocess.run(["git", "read-tree", head], cwd=str(repo), check=True, env=env)
    subprocess.run(["git", "update-index", "--add", doc, "tools/supplier.py"],
                   cwd=str(repo), check=True, env=env)
    tree = subprocess.run(["git", "write-tree"], cwd=str(repo), capture_output=True,
                          text=True, check=True, env=env).stdout.strip()

    findings, _ = run_at_tree(tree, since_tree=head, root=repo)
    assert findings == [], findings


def test_mutation_a_path_landed_in_an_earlier_commit_and_clean_is_green(repo):
    """`tools/supplier.py` landed in the base commit; a later document claiming it is honest."""
    doc = _write_doc(repo, "F_prior.md", "# f\n" + CLAIM)
    _git(repo, "add", doc)
    findings, _ = run_at_tree(_tree_of_index(repo), since_tree=_head_tree(repo), root=repo)
    assert findings == [], findings


# ---------------------------------------------------------------- the three killer patterns

def test_fail_open_a_claim_with_no_parseable_path_is_NAMED_not_skipped(repo):
    """R15 FAIL-OPEN. A document asserting a landing whose manifest names only SYMBOLS must
    reach the report as `unchecked`. Silently dropping it makes the control's population
    'documents that happen to use the heading I grepped for' -- a population chosen by the
    parser rather than by the subject. This is not hypothetical: it is the shape of the real
    2026-08-14 instance (see the tripwire below)."""
    doc = _write_doc(repo, "F_symbols.md",
                     "# f\n\n## What landed this tick\n\n`atom_name` + `name` in `NOTE_FIELDS`.\n")
    _git(repo, "add", doc)
    findings, report = run_at_tree(_tree_of_index(repo), since_tree=_head_tree(repo), root=repo)
    assert report["documents_claiming_a_landing"] == 1
    assert doc in report["unchecked_documents"], report
    assert findings == []


def test_tautology_the_control_reads_the_TREE_not_the_working_tree(repo):
    """R15 TAUTOLOGY. After staging a false claim, blank the WORKING-TREE copy. The control
    must still red, because its subject is the document the commit publishes."""
    doc = _write_doc(repo, "F_taut.md", "# f\n\n## What landed this tick\n\n`tools/ghost.py`.\n")
    _git(repo, "add", doc)
    tree = _tree_of_index(repo)
    (repo / doc).write_text("# f\n\nnothing to see here\n")   # desk is now green
    findings, _ = run_at_tree(tree, since_tree=_head_tree(repo), root=repo)
    assert any("tools/ghost.py" in f for f in findings), \
        "control read the working tree, which is the tree that was already green"


def test_fail_silent_the_control_has_an_automated_caller_in_the_gate():
    """R15 FAIL-SILENT. A control invoked only by someone typing it is permanently
    unavailable and therefore permanently passing (CLASS_NO_CALLER_AND_NEVER_RUNS)."""
    gate = (REPO / "tools" / "pre_commit_test_gate.py").read_text()
    assert "landed_manifest_check" in gate, "no automated caller: the control never runs"
    assert "run_at_tree" in gate


def test_a_backticked_token_is_not_a_path():
    """The parser must not read prose, test node ids or globs as repo paths."""
    assert is_path_like("tools/supplier.py")
    for junk in ("atom_name", "NOTE_FIELDS", "tests/x.py::test_y", "docs/**/*.md",
                 "https://example.com/a.md", "the supplier half", "-x"):
        assert not is_path_like(junk), junk


# ---------------------------------------------------------------- the real-instance tripwire

@pytest.mark.skipif(not REAL_INSTANCE.is_file(), reason="the real instance document is untracked")
def test_tripwire_the_real_instances_manifest_names_symbols_not_the_supplier_path():
    """THE SPEC'S NAMED MUTATION DOES NOT REPRODUCE, and that is pinned here rather than
    tuned away.

    `WORKER_FINDING_A_FINDING_RECORDED_ITS_OWN_INSTANCE_AS_FIXED...` specifies: re-run the
    control against the pathspec finding at parent `75290668f`; it must red on
    `tools/simplifications_store.py`. It cannot. That document's "What landed this tick"
    section claims the SYMBOL half (`atom_name`, `name` in `NOTE_FIELDS`) and never names
    the supplier path inside the manifest at all -- the path appears only in the evidence
    block, where the document is correctly reporting that it never landed.

    Widening the parser until that evidence line reads as a claim would be reading prose as
    a manifest, which is the defect this repo has already paid for. So the honest split is:
    this control owns the PATH shape, and `tools/symbol_landing_check.py` owns the SYMBOL
    shape. Neither alone covers the instance; the class's discharge must cite both.

    This test fails if the document is ever edited to name the supplier path in its
    manifest -- at which point the spec's mutation becomes reachable and should be built.
    """
    text = REAL_INSTANCE.read_text()
    assert asserts_landing(text)

    lines = text.splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.strip().lower().startswith("## what landed"))
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("#")), len(lines))
    section = "\n".join(lines[start:end])
    assert "simplifications_store" not in section, (
        "the manifest now names the supplier path: the spec's mutation is reachable, build it"
    )

    paths = manifest_paths(text)
    assert "tools/simplifications_store.py" not in paths
    assert "tools/migrate_atom_names.py" in paths

    assert (REPO / "tools" / "symbol_landing_check.py").is_file(), \
        "the SYMBOL half of this class has no owner"


# ---------------------------------------------------------------------------
# a path outside the repository is not a claim about the repository (2026-08-26)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("token", [
    "/tmp/claude-1000/-/c6cee6e9/scratchpad/land.sh",
    "/home/rich/synthetic-enterprise/tools/x.py",
    "~/scratch/apply_neso.py",
    "../outside-the-repo/thing.py",
])
def test_a_path_outside_the_repo_is_not_a_landing_claim(token):
    """THE DEFECT, AND ITS BLAST RADIUS. `DIRECTOR_CONSOLE_2026-08-20.md` mentions
    `/tmp/claude-1000/.../scratchpad/land.sh` in backticks -- honest prose about a wrapper
    script that really existed outside the tree. `is_path_like` called it a repo path, the
    caller ran `git ls-tree <tree> -- /tmp/...`, git answered rc=128 "Invalid path", and the
    checker RAISED.

    So it refused every commit touching `docs/staging` -- which is every commit that would
    have cleared the 419-file archive backlog, for six days. Fail-closed is right for "this
    path is missing from the tree" and wrong for "this token was never about the tree": the
    refusal named a crash, not a false LANDED, and a checker that cannot read its input is
    not reporting the thing it exists to report.
    """
    assert is_path_like(token) is False


@pytest.mark.parametrize("token", [
    "tools/landed_manifest_check.py",
    "docs/design/SURGICAL_LANDING.md",
    "simulation/run_phase2b.py",
    "tests/tools/test_landed_manifest_check.py",
])
def test_a_real_repo_path_is_still_a_landing_claim(token):
    """THE PARTNER, and the one that matters most. A guard that excluded too much would
    make every false LANDED invisible -- which is the defect this whole module exists to
    catch, reintroduced by its own repair."""
    assert is_path_like(token) is True


def test_the_checker_survives_a_document_that_mentions_a_scratch_path():
    """End to end on the real shape: a document making a landing claim about a genuine repo
    path AND mentioning an absolute scratch path must yield exactly the repo path."""
    text = (
        "# A finding\n\n"
        "**status:** LANDED\n"
        "`tools/landed_manifest_check.py` carries the fix; "
        "`/tmp/claude-1000/-/abc/scratchpad/land.sh` was the wrapper that found it.\n\n"
        "## Discussion\n\nprose\n"
    )
    assert asserts_landing(text)
    assert manifest_paths(text) == ["tools/landed_manifest_check.py"]


# ---------------------------------------------------------------------------
# a document with no sections has no header block (2026-08-26)
# ---------------------------------------------------------------------------

def test_a_document_with_no_sections_does_not_treat_its_whole_body_as_a_manifest():
    """THE SECOND DEFECT IN THIS CONTROL, same shape as the first, one step further out.

    The design says the claim surface is "the HEADER BLOCK (everything before the first
    `##` section), which is where `**status:** ... LANDED` lives" — a handful of lines. In a
    document with NO `##` heading that rule swallows the entire file, so every backticked
    path anywhere becomes a landing claim.

    `DIRECTOR_CONSOLE_2026-08-26.md` is exactly that shape, and the line it was billed for
    reads "`tests/simulation/test_policy_cost_coverage.py` remains uncommitted" — the
    OPPOSITE of a landing claim, quoted from a handover summary. The control refused the
    archive commit for six days over a sentence saying the file had NOT landed.
    """
    text = (
        "# A console note\n\n"
        "**status:** LANDED\n\n"
        "> Pending: `tests/simulation/test_policy_cost_coverage.py` remains uncommitted.\n"
        "> Also mentioned in passing: `tools/couple_clv.py`.\n"
    )
    assert manifest_paths(text) == []


def test_a_document_WITH_sections_still_claims_from_its_header_block():
    """THE PARTNER, and the one that protects the control. Narrowing that also silenced the
    normal shape would make every false LANDED invisible — this module's whole purpose."""
    text = (
        "# A finding\n\n"
        "**status:** LANDED\n"
        "`tools/couple_clv.py` carries the fix.\n\n"
        "## Discussion\n\n"
        "Elsewhere `simulation/run_phase2b.py` is only mentioned.\n"
    )
    assert manifest_paths(text) == ["tools/couple_clv.py"]


def test_a_what_landed_section_still_claims_even_without_any_double_hash_heading():
    """A document whose only heading is a `#### what landed` must still be read: the
    manifest-section rule is independent of the header-block one, and the fix above must not
    have coupled them."""
    text = (
        "# note\n\n"
        "#### What landed\n\n"
        "- `tools/couple_clv.py`\n"
    )
    assert manifest_paths(text) == ["tools/couple_clv.py"]
