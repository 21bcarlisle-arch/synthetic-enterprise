"""R15 falsifiers for the record-landing-claim control, both ways.

The control's named defect is the one that survived five consecutive EP6 passes: an atom's
own store record asserts that a symbol landed at a location, and the tree does not carry it
there. Every test builds a REAL git repository -- never a mock -- because the entire subject
is what git plumbing reports about a tree, and a control mocked on both sides is a pair that
agrees while the seam is broken.

The fixture's shape IS the finding. `include_schema_version` is present in `tools/port.py`
and absent from `simulation/run.py`, which is exactly the real repo's state at `d1d1e1fc5`:
a control asking "does the tree carry this symbol?" is GREEN on the real defect, and only a
scoped question can be red. `test_mutation_ignoring_the_scope...` builds that mutant beside
the control and shows it passing on the same bytes.

Scratch repos go under `/var/tmp`, not `gettempdir()`: `/tmp` on this box is a tmpfs backed
by the same RAM the suites need, and repo-shaped extracts under it are what filled it on
2026-08-14.
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

from tools.record_landing_claim_check import (  # noqa: E402
    added_lines,
    asserts_landing_in_record,
    is_symbol_like,
    landing_claims,
    run_at_tree,
    symbol_is_in_scope,
)

SCRATCH_ROOT = Path("/var/tmp")

RECORD = "docs/design/simplifications/EP6_wall_protocol_typing.yaml"

# The three sentences the real EP6 records used. `landed_manifest_check.asserts_landing`
# returns False on every one of them, which is why this control extends the predicate rather
# than importing it alone.
REAL_EP6_ASSERTIONS = (
    "LANDED VIA A WORKTREE SWAP -- this commit's tree is HEAD plus the three EP6 hunks.",
    "ACTUALLY LANDS PASSES 12-14",
    "Pass 10 LANDED the L2 that pass 9 earned and never committed",
)

BASE_RECORD = """atom: EP6_wall_protocol_typing
notes:
  - pass 11 measured the hole and did not claim to have closed it.
"""


def _git(repo: Path, *args: str) -> str:
    out = subprocess.run(
        ["git", *args], cwd=str(repo), capture_output=True, text=True, check=False
    )
    assert out.returncode == 0, f"git {' '.join(args)} rc={out.returncode}: {out.stderr}"
    return out.stdout.strip()


@pytest.fixture
def repo():
    """A repo whose shape is the real defect: symbol in `tools/`, absent from `simulation/`."""
    with tempfile.TemporaryDirectory(prefix="reclaim-", dir=str(SCRATCH_ROOT)) as tmp:
        r = Path(tmp)
        _git(r, "init", "-q", "-b", "main")
        _git(r, "config", "user.email", "t@example.com")
        _git(r, "config", "user.name", "t")
        (r / "tools").mkdir()
        (r / "simulation").mkdir()
        (r / "docs" / "design" / "simplifications").mkdir(parents=True)
        (r / "docs" / "staging").mkdir(parents=True)
        (r / "tools" / "port.py").write_text(
            "def to_log_entry(self, include_schema_version: bool = False):\n"
            "    return {}\n"
        )
        (r / "simulation" / "run.py").write_text(
            "log = [m.to_log_entry() for m in msgs]\n"
        )
        (r / RECORD).write_text(BASE_RECORD)
        _git(r, "add", "-A")
        _git(r, "commit", "-qm", "base")
        yield r


def _env(repo: Path) -> dict:
    return os.environ.copy()


def _tree_after(repo: Path, edits: dict[str, str]) -> str:
    """Write `edits`, stage them, and return the tree the commit WOULD create."""
    for rel, body in edits.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
        _git(repo, "add", "--", rel)
    return _git(repo, "write-tree")


def _head_tree(repo: Path) -> str:
    return _git(repo, "rev-parse", "HEAD^{tree}")


def _run(repo: Path, tree: str):
    return run_at_tree(tree, _head_tree(repo), root=repo, env=_env(repo))


CLAIM = "  - LANDED: `include_schema_version` in `simulation/`\n"
LANDED_CALL_SITE = "log = [m.to_log_entry(include_schema_version=True) for m in msgs]\n"


# --------------------------------------------------------------------------------------
# THE NAMED DEFECT, and its null control.
# --------------------------------------------------------------------------------------

def test_a_claim_scoped_to_simulation_is_red_while_the_symbol_only_lives_in_tools(repo):
    """The real instance: five records said this and no tree ever carried it."""
    tree = _tree_after(repo, {RECORD: BASE_RECORD + CLAIM})
    findings, report = _run(repo, tree)
    assert len(findings) == 1, findings
    assert "include_schema_version" in findings[0]
    assert "simulation/" in findings[0]
    assert report["claims_checked"] == 1


def test_the_null_control_is_the_same_claim_with_the_call_site_actually_landed(repo):
    """Move the SAMPLE, not the law: land the code and the identical claim goes green."""
    tree = _tree_after(
        repo,
        {RECORD: BASE_RECORD + CLAIM, "simulation/run.py": LANDED_CALL_SITE},
    )
    findings, report = _run(repo, tree)
    assert findings == []
    assert report["claims_checked"] == 1


def test_mutation_ignoring_the_scope_makes_the_real_instance_green(repo):
    """The mutant built beside the control: a symbol-anywhere question cannot fire here.

    This is not hypothetical. At `d1d1e1fc5` the real repo carried `include_schema_version`
    in three port modules and their tests, so an unscoped control was green through every
    false record. The scope is the whole control.
    """
    tree = _tree_after(repo, {RECORD: BASE_RECORD + CLAIM})
    unscoped = symbol_is_in_scope(tree, "include_schema_version", ".", repo, _env(repo))
    scoped = symbol_is_in_scope(
        tree, "include_schema_version", "simulation/", repo, _env(repo)
    )
    assert unscoped is True, "the mutant must PASS on the defect, or it is not the mutant"
    assert scoped is False, "the shipped control must refuse the same bytes"


def test_mutation_reading_the_working_tree_would_make_it_green(repo):
    """Independence from the worktree, which is the class's whole aetiology.

    On 2026-08-19 at 22:49:00 a concurrent lane restored the EP6 files to their HEAD
    contents while HEAD never moved. A control reading the worktree is reading a surface
    another process rewrites underneath it.
    """
    tree = _tree_after(repo, {RECORD: BASE_RECORD + CLAIM})
    # The symbol is now on DISK and not in the tree the commit creates.
    (repo / "simulation" / "run.py").write_text(LANDED_CALL_SITE)
    on_disk = (repo / "simulation" / "run.py").read_text()
    assert "include_schema_version" in on_disk
    findings, _ = _run(repo, tree)
    assert len(findings) == 1, "the worktree must not be able to satisfy the claim"


# --------------------------------------------------------------------------------------
# CLAUSE 1 -- the anti-fail-open. An opt-in syntax nobody uses is not a control.
# --------------------------------------------------------------------------------------

def test_prose_that_shouts_landed_without_a_checkable_claim_is_red(repo):
    tree = _tree_after(
        repo, {RECORD: BASE_RECORD + f"  - {REAL_EP6_ASSERTIONS[0]}\n"}
    )
    findings, report = _run(repo, tree)
    assert len(findings) == 1, findings
    assert "states no falsifiable claim" in findings[0]
    assert report["records_claiming_a_landing"] == 1


def test_mutation_dropping_clause_one_makes_every_real_ep6_record_green(repo):
    """Each real sentence must trip the predicate; the imported one missed all three."""
    from tools.landed_manifest_check import asserts_landing

    for sentence in REAL_EP6_ASSERTIONS:
        assert asserts_landing_in_record(sentence) is True, sentence
        assert asserts_landing(sentence) is False, (
            "if the imported predicate ever catches this, delete the extension "
            "rather than carrying two rules"
        )


def test_a_record_that_only_discusses_is_not_billed(repo):
    """Null control for clause 1: no assertion, no claim required."""
    tree = _tree_after(
        repo, {RECORD: BASE_RECORD + "  - pass 16 measured the gap and drew no conclusion.\n"}
    )
    findings, report = _run(repo, tree)
    assert findings == []
    assert report["records_claiming_a_landing"] == 0


def test_an_unparsed_landed_line_reaches_the_findings_not_the_floor(repo):
    """A claim the parser cannot read is REPORTED -- dropping it is the fail-open."""
    tree = _tree_after(
        repo, {RECORD: BASE_RECORD + "  - LANDED: three call sites in simulation\n"}
    )
    findings, report = _run(repo, tree)
    assert len(findings) == 1, findings
    assert "no checkable (symbol, scope) pair" in findings[0]
    assert report["unparsed_claims"] == 1


# --------------------------------------------------------------------------------------
# SCOPE -- added lines, store records, and nothing else.
# --------------------------------------------------------------------------------------

def test_a_records_own_history_is_not_re_billed(repo):
    """Quoting a past false claim is how findings get written; it must stay free.

    The record already contains the shouted assertion at HEAD. A later commit that adds an
    unrelated line must not be charged for it.
    """
    poisoned = BASE_RECORD + f"  - {REAL_EP6_ASSERTIONS[0]}\n"
    (repo / RECORD).write_text(poisoned)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "history")
    tree = _tree_after(repo, {RECORD: poisoned + "  - pass 17 renamed a field.\n"})
    findings, _ = _run(repo, tree)
    assert findings == []


def test_a_document_outside_the_store_is_not_this_controls_population(repo):
    """`docs/staging/` is the sibling control's room; two controls on one subject is churn."""
    tree = _tree_after(repo, {"docs/staging/NOTE.md": "LANDED: `nope_not_here` in `simulation/`\n"})
    findings, report = _run(repo, tree)
    assert findings == []
    assert report["records_changed"] == 0


def test_an_archive_roll_is_not_billed_for_relocating_its_own_history(repo):
    """Measured on `8233f3629`, whose archive file's five added lines are RELOCATED text.

    Under the added-lines rule a roll reads as newly authored throughout, so an archived note
    that once said LANDED would refuse the roll -- and the committer could not comply without
    falsifying the archive.
    """
    rolled = "docs/design/simplifications/archive/EP6_wall_protocol_typing.004.yaml"
    tree = _tree_after(repo, {rolled: BASE_RECORD + f"  - {REAL_EP6_ASSERTIONS[0]}\n" + CLAIM})
    findings, report = _run(repo, tree)
    assert findings == []
    assert report["records_changed"] == 0


def test_a_deleted_record_makes_no_claim(repo):
    _git(repo, "rm", "-q", "--", RECORD)
    tree = _git(repo, "write-tree")
    findings, report = _run(repo, tree)
    assert findings == []
    assert report["records_changed"] == 0


# --------------------------------------------------------------------------------------
# FAIL-CLOSED (R15): an unavailable check is a FAILED check.
# --------------------------------------------------------------------------------------

def test_a_plumbing_failure_raises_rather_than_reading_as_a_clean_absence(repo):
    with pytest.raises(RuntimeError):
        symbol_is_in_scope("not-a-tree", "include_schema_version", "simulation/", repo, _env(repo))


def test_a_bogus_since_tree_raises_rather_than_reporting_no_changed_records(repo):
    tree = _tree_after(repo, {RECORD: BASE_RECORD + CLAIM})
    with pytest.raises(RuntimeError):
        run_at_tree(tree, "not-a-tree", root=repo, env=_env(repo))


# --------------------------------------------------------------------------------------
# Pure parsing, where the sibling control's false-positive lesson is inherited.
# --------------------------------------------------------------------------------------

def test_a_path_is_not_a_symbol():
    assert is_symbol_like("include_schema_version") is True
    for token in ("simulation/run.py", "tests/x.py::test_y", "a sentence", "-flag", ""):
        assert is_symbol_like(token) is False, token


def test_claims_are_deduplicated_and_ordered():
    claims, unparsed = landing_claims(
        "LANDED: `a_symbol` in `simulation/`\n"
        "LANDED: `a_symbol` in `simulation/`\n"
        "LANDED: `b_symbol` in `company/`\n"
    )
    assert claims == [("a_symbol", "simulation/"), ("b_symbol", "company/")]
    assert unparsed == 0


def test_added_lines_carries_no_context_from_neighbouring_passes(repo):
    tree = _tree_after(repo, {RECORD: BASE_RECORD + CLAIM})
    added = added_lines(tree, _head_tree(repo), RECORD, repo, _env(repo))
    assert "LANDED:" in added
    assert "pass 11 measured the hole" not in added
