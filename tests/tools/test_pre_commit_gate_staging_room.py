"""R15 proofs for the MISSING CALLER of `finding_classes.self_refuelling_root_documents`.

THE PREDICATE IS NOT THE SUBJECT HERE, and is deliberately not re-derived. It was written on
2026-09-04, its reachability pair is proven in
`tests/background/test_only_work_is_in_the_work_channel.py`, and it is IMPORTED by the step this
file tests. What is proven here is the thing it did not have: a caller on the write that arms
the defect.

THE LOOP, which that predicate's own docstring names and which was live when this was written:

  1. a channel COMMITS a pre-registration into `docs/staging/` — the WORK QUEUE;
  2. a disposition moves it to `records/`, where its kind belongs;
  3. the root path is still TRACKED, so the next restore of a tracked-but-deleted path brings
     it back (the gate does that itself, to judge the tree a commit would create);
  4. `room_collisions` sees both rooms and refuses EVERY lane's commit and the publisher's;
  5. `staging_two_rooms_repair` clears it — but `git rm` is a STAGED deletion, so step 3 undoes
     it. It sticks only when a seat commits the deletion by hand.

Measured live 2026-09-18: five instances in both rooms refusing the whole tree, cleared by the
repair at 17:21, and back on disk with one shared mtime at 17:23:15. The same shape cost publish
cycles on 2026-09-04 and 2026-09-16.

WHY THE PREDICATE COULD NOT REACH STEP 1. Its only reader was a TEST asking `git ls-files` — the
INDEX — which is green for exactly as long as the deletion is staged and uncommitted, i.e.
throughout the loop; and being a test, the gate reaches it only by subject-module selection, so a
commit touching nothing but `docs/staging/**` never runs it. That is the commit that files a
pre-registration.

WHAT HAS TO BE PROVEN, and each of these injects the defect rather than asserting today's tree:

  1. IT RUNS on a staging-only commit — the commit that selects no test targets is exactly the
     commit that files a document, which is the early-return trap its sibling class-checker
     test was written for.
  2. IT REFUSES, naming the document, its room, and the `git mv` that fixes it.
  3. A DELETION IS NOT A FILING. The subject is the tree the commit would create, and the
     backlog is disposed of by a commit that removes root copies while they are still on disk.
     Read the working tree instead and this control refuses its own remedy.
  4. IT IS SCOPED. A document already in its room, and a commit touching no staging path, pass.
  5. FAIL-CLOSED on its own unavailability (R15 killer pattern 3).
"""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools import pre_commit_test_gate as gate  # noqa: E402

PREREG = "PREREG_WHAT_THE_PER_TERM_GATE_CENSUS_MOVES_ON_THE_ARMS_PAGE_2026-09-18.md"
IN_ROOT = f"docs/staging/{PREREG}"
IN_ROOM = f"docs/staging/records/{PREREG}"


def _git(repo: Path, *args: str) -> str:
    out = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True,
                         timeout=60)
    assert out.returncode == 0, f"git {' '.join(args)} -> {out.returncode}: {out.stderr}"
    return out.stdout.strip()


@pytest.fixture()
def repo(tmp_path: Path, monkeypatch) -> Path:
    """A REAL git repository, because the discrimination under test is a real one.

    The check asks git whether the path is in the tree THIS COMMIT WOULD CREATE, and the case
    that matters — a root copy present on disk and staged for deletion — cannot be simulated by
    a stubbed `cat-file`: a stub answers whatever the test wants and the fail-open direction
    would go unnoticed. `_index_tree` is stubbed (it resolves the repo from a default argument
    bound at import); everything below it runs against this index for real.
    """
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "t@t")
    _git(tmp_path, "config", "user.name", "t")
    (tmp_path / "docs" / "staging" / "records").mkdir(parents=True)
    (tmp_path / "seed.txt").write_text("seed\n")
    _git(tmp_path, "add", "seed.txt")
    _git(tmp_path, "commit", "-q", "-m", "seed")
    monkeypatch.setattr(gate, "ROOT", tmp_path)
    monkeypatch.setattr(gate, "_index_tree", lambda: _git(tmp_path, "write-tree"))
    return tmp_path


# ── 1. IT RUNS: the early-return trap ────────────────────────────────────────

def test_a_staging_only_commit_still_asks_the_question(monkeypatch, capsys):
    """DEFECT: the check is wired after `main()`'s pure-docs early return.

    A commit touching only `docs/staging/**` selects no test targets and returns 0 long before
    the test run — and that commit is precisely the one that files a pre-registration. Wired
    below the return, this control would be green on every commit that could ever break it.
    """
    monkeypatch.setattr(gate, "staged_files", lambda: [IN_ROOT])
    monkeypatch.setattr(gate, "select_targets", lambda files: [])
    monkeypatch.setattr(gate, "_class_consolidation_check", lambda: (True, "ok"))
    monkeypatch.setattr(gate, "_landed_manifest_check", lambda staged: (True, ""))
    monkeypatch.setattr(gate, "_staging_severity_check", lambda staged: (True, ""))
    asked = []
    monkeypatch.setattr(gate, "_staging_room_check",
                        lambda staged: (asked.append(list(staged)), (True, ""))[1])
    gate.main()
    assert asked == [[IN_ROOT]], (
        "a staging-only commit never reached the room check -- the early-return trap, on the "
        "one commit shape that arms the wedge")


def test_a_commit_touching_no_staging_path_never_asks(monkeypatch):
    """MUTATION: the scope is real, not 'always on'. A code commit pays nothing for this."""
    monkeypatch.setattr(gate, "staged_files", lambda: ["saas/customers.py"])
    monkeypatch.setattr(gate, "select_targets", lambda files: [])
    asked = []
    monkeypatch.setattr(gate, "_staging_room_check",
                        lambda staged: (asked.append(1), (True, ""))[1])
    gate.main()
    assert asked == [], "a commit with no staging path ran the staging-room check"


# ── 2. IT REFUSES, and the refusal names a document ──────────────────────────

def test_a_preregistration_filed_into_the_queue_is_REFUSED_by_name(repo):
    """DEFECT: the wedge is armed and nothing says so until it refuses every lane.

    The refusal has to carry three things, because the point of firing here rather than at the
    two-rooms detector is that the author can fix it in one move: WHICH document, WHICH room,
    and the command.
    """
    (repo / IN_ROOT).write_text("# prereg\n")
    _git(repo, "add", IN_ROOT)

    ok, detail = gate._staging_room_check([IN_ROOT])

    assert not ok, (
        "a pre-registration committed into the WORK QUEUE was allowed -- this is step 1 of the "
        "loop that ends with every lane's commit refused and only a seat turn able to clear it")
    assert PREREG in detail, "the refusal does not name the document it is about"
    assert "docs/staging/records/" in detail, "the refusal does not name the room"
    assert f"git mv {IN_ROOT} {IN_ROOM}" in detail, (
        "the refusal does not carry the one command that fixes it, so it costs a reader a "
        "lookup to obey")


# ── 3. A DELETION IS NOT A FILING ────────────────────────────────────────────

def test_removing_a_root_copy_that_is_still_on_disk_is_NOT_a_filing(repo):
    """DEFECT: the control refuses its own remedy, and the backlog can never be disposed of.

    This is the live shape, not a hypothetical. The two-rooms repair `git rm`s the root copy and
    the gate re-materialises it from HEAD, so at the moment a seat commits the disposal the
    file IS ON DISK and IS staged for deletion. A check reading the working tree refuses that
    commit -- which would leave the wedge with no legal exit at all, one rung worse than the
    state it was built to fix.
    """
    (repo / IN_ROOT).write_text("# prereg\n")
    _git(repo, "add", IN_ROOT)
    _git(repo, "commit", "-q", "-m", "the misfiling, as it was committed before this control")
    _git(repo, "rm", "-q", "--cached", IN_ROOT)
    assert (repo / IN_ROOT).is_file(), (
        "fixture wrong: the whole point is that the root copy is STILL ON DISK while its "
        "deletion is staged")

    ok, detail = gate._staging_room_check([IN_ROOT])

    assert ok, (
        f"the commit that DISPOSES of a misfiled pre-registration was refused for filing it: "
        f"{detail}")


# ── 4. SCOPE: the room, and the rooms below it ───────────────────────────────

def test_a_preregistration_in_its_ROOM_passes(repo):
    """MUTATION: the queue is the FLAT root. Refusing `records/` too would refuse everything."""
    (repo / IN_ROOM).write_text("# prereg\n")
    _git(repo, "add", IN_ROOM)
    ok, _ = gate._staging_room_check([IN_ROOM])
    assert ok, "a pre-registration in records/ -- its room -- was refused"


def test_a_FINDING_in_the_queue_root_passes(repo):
    """MUTATION: the work queue still takes work.

    The expensive failure direction. A widening that caught findings would refuse the channel
    this project runs on, and it would look exactly like this control working.
    """
    finding = "docs/staging/WORKER_FINDING_SOMETHING_REAL_2026-09-18.md"
    (repo / finding).write_text("# finding\n")
    _git(repo, "add", finding)
    ok, _ = gate._staging_room_check([finding])
    assert ok, "a finding filed into the work queue was refused as misfiled"


# ── 5. FAIL-CLOSED on its own unavailability ─────────────────────────────────

def test_an_unavailable_classifier_is_a_FAILED_check(monkeypatch):
    """DEFECT (R15 killer pattern 3): a check skipped because its import broke reads as a pass.

    Proven by making the import raise, which is the only failure mode that could otherwise be
    silent -- everything else in this step either returns a verdict or raises into the caller.
    It matters more here than for most steps: the predicate spent five months with no caller at
    all, and a caller that goes quiet when its import breaks is that state wearing a green tick.
    """
    import builtins
    real_import = builtins.__import__

    def _boom(name, *args, **kwargs):
        if name == "background.finding_classes":
            raise ImportError("simulated: the predicate is gone")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _boom)
    monkeypatch.delitem(sys.modules, "background.finding_classes", raising=False)

    ok, detail = gate._staging_room_check([IN_ROOT])
    assert not ok, "an unimportable predicate let the commit through -- a skipped check is not a pass"
    assert "UNAVAILABLE" in detail


# ── 6. THE CHAIN (H45): a work item FILED by this commit names its lane, epoch and atom ──────

_UNCHAINED = "**Severity:** LATENT · **Lane:** H_harness\n\n# a finding\n"
_CHAINED = ("**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · "
            "**Atom:** `unminted`\n\n# a finding\n")


def test_the_chain_step_can_both_refuse_and_pass_and_an_edit_is_not_a_filing(repo):
    """DEFECT: 28 of 96 work items filed in a week carried no epoch or atom, and nothing refused.

    One control over the whole partition, so a step that refuses EVERYTHING and one that
    refuses NOTHING both go red here: a NEW unchained finding is refused by name; a new chained
    one, an EDIT to a legacy unchained one already at the parent, and a director's directive
    all pass. `unassigned`/`unminted` count as answers -- absence is the defect, not "not yet".
    """
    legacy = "docs/staging/SEAT_FINDING_LEGACY_UNCHAINED_2026-09-01.md"
    (repo / legacy).write_text(_UNCHAINED)
    _git(repo, "add", legacy)
    _git(repo, "commit", "-q", "-m", "a legacy gap, filed before this control")
    (repo / legacy).write_text(_UNCHAINED + "\nan edit\n")

    new_bad = "docs/staging/SEAT_FINDING_NEW_UNCHAINED_2026-09-30.md"
    new_good = "docs/staging/SEAT_FINDING_NEW_CHAINED_2026-09-30.md"
    directive = "docs/staging/DIRECTOR_INSTRUCTION_SOMETHING_2026-09-30.md"
    (repo / new_bad).write_text(_UNCHAINED)
    (repo / new_good).write_text(_CHAINED)
    (repo / directive).write_text("# the director's words\n")
    _git(repo, "add", legacy, new_bad, new_good, directive)

    refused, detail = gate._staging_chain_check([new_bad])
    passed = [gate._staging_chain_check([p])[0] for p in (new_good, legacy, directive)]

    assert not refused and passed == [True, True, True], (
        f"partition wrong: new-unchained refused={not refused}, "
        f"[chained, legacy edit, directive] passed={passed}")
    assert "SEAT_FINDING_NEW_UNCHAINED" in detail and "epoch, atom" in detail, (
        f"the refusal does not name the document and what it lacks: {detail}")


def test_an_edit_may_not_strip_a_chain_the_item_carried(repo):
    """DEFECT: on 2026-10-01 a register re-render rewrote the header with Severity + Lane only,
    wiping a chain stamped a day earlier, and the filing check could not see it -- an edit is
    not a filing. Whole partition on one commit: stripping a carried chain is refused by name;
    an edit that keeps it passes; a legacy gap edited in place still passes (it had no chain to
    lose), so a step that refuses every edit and one that refuses none are both red here.
    """
    stamped = "docs/staging/SEAT_FINDING_STAMPED_2026-09-01.md"
    kept = "docs/staging/SEAT_FINDING_KEPT_2026-09-01.md"
    legacy = "docs/staging/SEAT_FINDING_LEGACY_UNCHAINED_2026-09-01.md"
    for p, text in ((stamped, _CHAINED), (kept, _CHAINED), (legacy, _UNCHAINED)):
        (repo / p).write_text(text)
    _git(repo, "add", stamped, kept, legacy)
    _git(repo, "commit", "-q", "-m", "three items already in the queue")

    (repo / stamped).write_text(_UNCHAINED)  # the re-render: Severity + Lane only
    (repo / kept).write_text(_CHAINED + "\nan edit\n")
    (repo / legacy).write_text(_UNCHAINED + "\nan edit\n")
    _git(repo, "add", stamped, kept, legacy)

    refused, detail = gate._staging_chain_check([stamped])
    passed = [gate._staging_chain_check([p])[0] for p in (kept, legacy)]

    assert not refused and passed == [True, True], (
        f"partition wrong: stripping edit refused={not refused}, [kept, legacy] passed={passed}")
    assert "SEAT_FINDING_STAMPED" in detail and "epoch, atom" in detail, (
        f"the refusal does not name the document and what the edit removed: {detail}")


def test_a_chain_refusal_reaches_main_and_stops_the_commit(monkeypatch, capsys):
    """R15 both-ways at the CALLER, on the staging-only commit that selects no targets."""
    monkeypatch.setattr(gate, "staged_files", lambda: ["docs/staging/WORKER_FINDING_X.md"])
    monkeypatch.setattr(gate, "select_targets", lambda files: [])
    monkeypatch.setattr(gate, "_class_consolidation_check", lambda: (True, "ok"))
    monkeypatch.setattr(gate, "_landed_manifest_check", lambda staged: (True, ""))
    monkeypatch.setattr(gate, "_staging_severity_check", lambda staged: (True, ""))
    monkeypatch.setattr(gate, "_staging_room_check", lambda staged: (True, ""))
    monkeypatch.setattr(gate, "_staging_chain_check",
                        lambda staged: (False, "  - docs/staging/W.md: missing epoch, atom"))
    assert gate.main() == 1, "an unchained filing did not refuse the commit"
    err = capsys.readouterr().err
    assert "COMMIT REFUSED" in err and "missing epoch, atom" in err
    assert "**Epoch:**" in err, "the refusal did not tell the author what to write"
