"""R15 proofs for the zero-unclassified control's pre-commit caller.

`background/finding_severity.py` has implemented the zero-unclassified control since
OPS9 -- its `main()` returns 1 on any unclassified document and its own module comment
calls it "the zero-unclassified control". NOTHING RAN IT. It was reachable only by
typing the command, or by tripping over its consequence much later.

The consequence is not local. `background/gate_authorization.py` refuses a level raise
in EVERY lane while any staging document is unclassified -- deliberately, because an
unclassified document's severity could be BLOCKING and its lane is unknown, so it
cannot show any lane clear. On 2026-08-15 two documents with no severity header held
level-recording in all 13 lanes:
`DIRECTOR_DECISION_PENDING_RATE_REBASELINE_AND_SPLIT_APPROVAL_2026-08-14` and
`WORKER_REPORT_THE_LEAK_IS_MARKED_SWEPT_AND_TESTED_BOTH_WAYS_2026-08-14`. Both were
written by this machine; neither author was told.

Per R10 the two header lines that cleared it do NOT close the class. This file proves
`tools/pre_commit_test_gate._staging_severity_check` makes the class fail automatically,
and proves it in both directions -- every test here injects a defect and asserts the
gate goes red on it, or injects the legal shape and asserts it stays green. Sibling of
`test_pre_commit_gate_class_checker.py`, which closed the identical no-caller defect for
the class checker.

THE ONE THAT MATTERS MOST is `test_a_headered_working_file_does_not_excuse_an_unheadered
_blob`: the subject must be the tree the commit would create, never the working tree
(`WORKER_FINDING_THE_SITE_LANE_GATES_THE_WORKING_TREE_NOT_THE_COMMIT_2026-08-13`).
"""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools import pre_commit_test_gate as gate  # noqa: E402

HEADER = "**Severity:** LATENT · **Lane:** H_harness"


def _run(repo: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=True,
    )
    return done.stdout.strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A real git repo -- the check reads blobs with `git cat-file`, so a fake will not do."""
    _run(tmp_path, "init", "-q", "-b", "main")
    _run(tmp_path, "config", "user.email", "t@example.com")
    _run(tmp_path, "config", "user.name", "t")
    (tmp_path / "docs" / "staging" / "done").mkdir(parents=True)
    (tmp_path / "docs" / "staging" / "in_progress").mkdir(parents=True)
    return tmp_path


def _stage(repo: Path, rel: str, body: str) -> str:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    _run(repo, "add", "--", rel)
    return rel


def _check(monkeypatch, repo: Path, staged: list[str]):
    """Point the gate at `repo` and judge the tree its index would create."""
    monkeypatch.setattr(gate, "ROOT", repo)
    tree = _run(repo, "write-tree")
    monkeypatch.setattr(gate, "_index_tree", lambda root=None: tree)
    return gate._staging_severity_check(staged)


# ── 1. BOTH DIRECTIONS ON THE PARSE ──────────────────────────────────────────

def test_an_unheadered_document_refuses_the_commit(monkeypatch, repo):
    """THE NAMED DEFECT. The exact shape of the two documents that held all 13 lanes:
    a real finding, real prose, no severity line."""
    rel = _stage(repo, "docs/staging/WORKER_FINDING_X_2026-08-15.md",
                 "# WORKER FINDING — something\n\nProse with no severity line.\n")
    ok, detail = _check(monkeypatch, repo, [rel])
    assert not ok, "an unheadered staging document was allowed into the tree"
    assert "no severity header" in detail
    assert rel in detail, "the refusal did not name the offending file -- unactionable"


def test_a_headered_document_passes(monkeypatch, repo):
    """THE FAIL-DANGEROUS DIRECTION. Without this the check could be `return False`
    and every test above would still pass."""
    rel = _stage(repo, "docs/staging/WORKER_FINDING_Y_2026-08-15.md",
                 f"# WORKER FINDING — something\n\n{HEADER}\n\nProse.\n")
    ok, detail = _check(monkeypatch, repo, [rel])
    assert ok, f"a correctly headered document was refused: {detail}"
    assert "1 staging document(s)" in detail, "the count is the control's own error bar"


@pytest.mark.parametrize("bad,reason", [
    ("**Severity:** URGENT · **Lane:** H_harness", "not one of"),
    ("**Severity:** LATENT", "lane missing"),
    ("**Severity:** LATENT · **Lane:** Q_not_a_lane", "not a known lane"),
])
def test_a_malformed_header_is_refused_like_a_missing_one(monkeypatch, repo, bad, reason):
    """Three ways to write a header that parses to UNCLASSIFIED. Each holds every lane
    exactly as a missing one does, so each must refuse here too -- otherwise 'has a
    severity line' becomes the check, which is not the property that matters."""
    rel = _stage(repo, "docs/staging/WORKER_FINDING_Z_2026-08-15.md",
                 f"# WORKER FINDING — z\n\n{bad}\n\nProse.\n")
    ok, detail = _check(monkeypatch, repo, [rel])
    assert not ok, f"a header parsing to UNCLASSIFIED was accepted: {bad}"
    assert reason in detail


def test_a_severity_buried_below_the_header_block_does_not_count(monkeypatch, repo):
    """The parser requires the header BLOCK (before the first `## `, ≤40 lines in), and
    this check must inherit that rather than grepping the whole file -- a severity in §7
    is not one its own reader would ever see."""
    body = f"# WORKER FINDING — buried\n\nProse.\n\n## Section\n\n{HEADER}\n"
    rel = _stage(repo, "docs/staging/WORKER_FINDING_BURIED_2026-08-15.md", body)
    ok, detail = _check(monkeypatch, repo, [rel])
    assert not ok, "a severity below the header block was treated as a header"


# ── 2. THE SUBJECT IS THE COMMIT'S TREE, NOT THE WORKING TREE ────────────────

def test_a_headered_working_file_does_not_excuse_an_unheadered_blob(monkeypatch, repo):
    """THE REGRESSION THIS FILE EXISTS FOR, and the one a lazier check would miss.

    Stage the unheadered version, then fix the file ON DISK without staging it. A
    working-tree read now sees a valid header while the commit would land the broken
    blob. `git commit -- <pathspec>` makes this an ordinary Tuesday on this shared tree,
    not a contrived case
    (`WORKER_FINDING_THE_SITE_LANE_GATES_THE_WORKING_TREE_NOT_THE_COMMIT_2026-08-13`).
    """
    rel = _stage(repo, "docs/staging/WORKER_FINDING_RACE_2026-08-15.md",
                 "# WORKER FINDING — race\n\nNo severity line.\n")
    (repo / rel).write_text(f"# WORKER FINDING — race\n\n{HEADER}\n\nFixed on disk.\n",
                            encoding="utf-8")  # NOT staged
    ok, detail = _check(monkeypatch, repo, [rel])
    assert not ok, "the check read the working tree, not the tree the commit would create"
    assert "no severity header" in detail


# ── 3. VACUITY GUARDS: the population boundary is real in both directions ────

def test_a_doorbell_is_not_required_to_carry_a_header(monkeypatch, repo):
    """`run_complete_*` / `run_pending_*` / `from_rich_*` are machine-generated and
    archived minutes later. Requiring a severity on them would make this control flap red
    on the ordinary operation of the machine, and an alarm that fires on normal behaviour
    is one nobody reads. The prefix list is IMPORTED from the parser, never re-typed, so
    the two populations cannot drift."""
    rel = _stage(repo, "docs/staging/run_complete_20260815.md", "# run complete\n\nno header\n")
    ok, detail = _check(monkeypatch, repo, [rel])
    assert ok, f"a doorbell was billed for a severity header: {detail}"


@pytest.mark.parametrize("room", ["done", "in_progress"])
def test_a_subdirectory_document_is_outside_the_classified_population(monkeypatch, repo, room):
    """`classifiable_documents` globs `*.md` and never recurses, so `done/` and
    `in_progress/` are outside the population the hold is computed over. If this check
    billed them it would refuse the ARCHIVE MOVE -- making the routine way to close a
    finding the thing that cannot be committed."""
    rel = _stage(repo, f"docs/staging/{room}/WORKER_FINDING_OLD.md", "# old\n\nno header\n")
    ok, detail = _check(monkeypatch, repo, [rel])
    assert ok, f"a document in {room}/ was billed for a header: {detail}"


def test_archiving_a_document_is_not_refused_for_its_missing_blob(monkeypatch, repo):
    """The `done/` move DELETES the root copy. `git cat-file` finds no blob, and there is
    nothing left to classify -- a deletion must skip, not fail closed. Fail-closed on a
    deletion would wedge exactly the commits that drain the room."""
    rel = "docs/staging/WORKER_FINDING_GONE_2026-08-15.md"
    _stage(repo, rel, f"# gone\n\n{HEADER}\n")
    _run(repo, "commit", "-q", "-m", "seed")
    (repo / rel).unlink()
    _run(repo, "add", "-A", "--", "docs/staging")
    ok, detail = _check(monkeypatch, repo, [rel])
    assert ok, f"a deletion (the archive move) was refused: {detail}"


def test_a_non_staging_commit_is_not_billed(monkeypatch, repo):
    """The scope is real, not 'always on'."""
    rel = _stage(repo, "saas/customers.py", "x = 1\n")
    ok, detail = _check(monkeypatch, repo, [rel])
    assert ok and detail == "", "a commit touching no staging document paid for the check"


def test_a_non_markdown_staging_file_is_not_billed(monkeypatch, repo):
    """The room carries JSON registers and symlinks too; only `*.md` is classifiable."""
    rel = _stage(repo, "docs/staging/register.json", "{}\n")
    ok, detail = _check(monkeypatch, repo, [rel])
    assert ok and detail == "", "a non-markdown staging file was billed for a header"


# ── 4. FAIL-CLOSED: R15's third killer pattern ───────────────────────────────

def test_an_unimportable_parser_fails_closed(monkeypatch, repo):
    """An unavailable check is a FAILED check. A check skipped because its module did not
    import is a check that PASSED, which is how a control quietly stops existing."""
    import builtins
    real_import = builtins.__import__

    def _boom(name, *a, **kw):
        if name == "background.finding_severity":
            raise ImportError("injected")
        return real_import(name, *a, **kw)

    monkeypatch.setattr(builtins, "__import__", _boom)
    monkeypatch.delitem(sys.modules, "background.finding_severity", raising=False)
    ok, detail = _check(monkeypatch, repo, ["docs/staging/WORKER_FINDING_X.md"])
    assert not ok, "an unimportable severity parser passed the gate"
    assert "UNAVAILABLE" in detail


def test_an_unusable_index_fails_closed(monkeypatch, repo):
    """If the tree this commit would create cannot be determined, there is no subject to
    judge -- refuse rather than judge nothing and report success."""
    rel = _stage(repo, "docs/staging/WORKER_FINDING_X_2026-08-15.md", f"# x\n\n{HEADER}\n")
    monkeypatch.setattr(gate, "ROOT", repo)

    def _explode(root=None):
        raise RuntimeError("injected: index.lock exists")

    monkeypatch.setattr(gate, "_index_tree", _explode)
    ok, detail = gate._staging_severity_check([rel])
    assert not ok, "an unreadable index passed the gate"
    assert "injected" in detail


# ── 5. WHERE: the early-return trap the class checker was wired around ───────

def test_a_staging_only_commit_still_runs_the_check(monkeypatch, capsys):
    """A commit touching only `docs/staging/**` selects NO test targets and takes
    `main()`'s pure-docs `return 0`. That commit is EXACTLY the one that files an
    unheadered document, so wiring the check after that return would have missed the
    whole class -- the same trap `test_staging_only_commit_still_runs_the_checker`
    pins for the class checker."""
    monkeypatch.setattr(gate, "staged_files", lambda: ["docs/staging/WORKER_FINDING_X.md"])
    monkeypatch.setattr(gate, "select_targets", lambda files: [])
    monkeypatch.setattr(gate, "_class_consolidation_check", lambda: (True, "ok"))
    monkeypatch.setattr(gate, "_landed_manifest_check", lambda staged: (True, ""))
    seen = []
    monkeypatch.setattr(gate, "_staging_severity_check",
                        lambda staged: (seen.append(staged), (True, "2 doc(s) ok"))[1])
    assert gate.main() == 0
    assert seen, "staging-only commit did not run the severity check (early-return trap)"
    assert "2 doc(s) ok" in capsys.readouterr().out


def test_a_refusal_reaches_stderr_and_stops_the_commit(monkeypatch, capsys):
    """R15 both-ways at the CALLER: a red check must refuse with rc 1 and carry its
    reason, not warn and continue."""
    monkeypatch.setattr(gate, "staged_files", lambda: ["docs/staging/WORKER_FINDING_X.md"])
    monkeypatch.setattr(gate, "select_targets", lambda files: [])
    monkeypatch.setattr(gate, "_class_consolidation_check", lambda: (True, "ok"))
    monkeypatch.setattr(gate, "_landed_manifest_check", lambda staged: (True, ""))
    monkeypatch.setattr(gate, "_staging_severity_check",
                        lambda staged: (False, "  - docs/staging/W.md: no severity header"))
    assert gate.main() == 1, "an unheadered document did not refuse the commit"
    err = capsys.readouterr().err
    assert "COMMIT REFUSED" in err
    assert "no severity header" in err, "the reason was swallowed -- an unactionable refusal"
    assert "**Severity:**" in err, "the refusal did not tell the author what to write"
