"""Controls for `tools/director_document_gate.py`, each named for the defect it exists to catch.

Driven against REAL temporary git repos, with the gate run AS A SCRIPT from the repo's top -- the
way `tools/git-hooks/commit-msg` runs it and the way `surgical_land.run_message_gate` runs it --
because `next_step_gate` shipped one wiring dead in production with nine in-process controls green.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from tools import director_document_gate as gate

PROJECT = Path(__file__).resolve().parents[2]
GATE = PROJECT / "tools" / "director_document_gate.py"
CANON = "docs/staging/DIRECTOR_CANON_THE_THING_2026-10-01.md"
CONSOLE = "docs/staging/console/DIRECTOR_CONSOLE_2026-10-01.md"
MISSION_CLAUDE = (
    "# CLAUDE.md\n\nintro\n\n---\n\n## The mission\n\n> We create value.\n\n---\n\n"
    "## What you are\n\nThe seat.\n"
)
CANON_TEXT = "# A canon\n\n" + "".join(f"His sentence number {i} about the thing.\n" for i in range(40))


def _env(tmp_path: Path) -> dict:
    return {"PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(tmp_path),
            "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


def _git(repo: Path, env: dict, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, env=env, check=True,
                          capture_output=True, text=True).stdout


@pytest.fixture
def repo(tmp_path: Path):
    """A repo whose HEAD holds a canon, a console transcript, an unrelated file and a CLAUDE.md."""
    r = tmp_path / "r"
    r.mkdir()
    env = _env(tmp_path)
    _git(r, env, "init", "-q", "-b", "main", ".")
    for rel, text in ((CANON, CANON_TEXT), (CONSOLE, "his words\n"), ("tools/x.py", "x = 1\n"),
                      ("CLAUDE.md", MISSION_CLAUDE)):
        (r / rel).parent.mkdir(parents=True, exist_ok=True)
        (r / rel).write_text(text)
    _git(r, env, "add", "-A")
    _git(r, env, "commit", "-q", "-m", "base")
    return r, env


def _write(repo: Path, env: dict, rel: str, text: str) -> None:
    (repo / rel).parent.mkdir(parents=True, exist_ok=True)
    (repo / rel).write_text(text)
    _git(repo, env, "add", "--", rel)


def _run(repo: Path, env: dict, message: str) -> subprocess.CompletedProcess:
    msg = repo / ".git" / "COMMIT_EDITMSG"
    msg.write_text(message)
    return subprocess.run([sys.executable, str(GATE), str(msg)], cwd=repo, env=env,
                          capture_output=True, text=True, timeout=120)


# --- the rule ----------------------------------------------------------------------------------

def test_an_UNMARKED_edit_to_a_director_canon_is_refused_and_told_where_intent_goes(repo):
    """Defect: a seat rewrites what the director MEANT and lands it as an ordinary commit."""
    r, env = repo
    _write(r, env, CANON, CANON_TEXT + "A sentence he never wrote.\n")
    done = _run(r, env, "tidy the canon\n")
    assert done.returncode == 1, done.stderr
    assert CANON in done.stderr
    assert "SEAT_PROPOSAL_" in done.stderr and "director_concerns --raise" in done.stderr
    assert "for_the_director" in done.stderr


@pytest.mark.parametrize("trailer", [
    "Director-doc: correction -- it said 2021; the record says 2022 (Ofgem cap table)",
    "Director-doc: his-words -- console 2026-10-01, appended verbatim",
    "Director-doc: record -- header classification only, no sentence of his changed",
])
def test_each_of_the_THREE_marked_kinds_lands(repo, trailer):
    """Defect: the gate refuses the factual correction the director explicitly handed over."""
    r, env = repo
    _write(r, env, CANON, CANON_TEXT + "corrected.\n")
    done = _run(r, env, f"correct the canon\n\n{trailer}\n")
    assert done.returncode == 0, done.stderr


def test_a_trailer_with_an_EMPTY_reason_is_refused(repo):
    """Defect: `Director-doc: correction --` with nothing after it reads as a record and says nothing."""
    r, env = repo
    _write(r, env, CANON, CANON_TEXT + "x\n")
    assert _run(r, env, "c\n\nDirector-doc: correction --\n").returncode == 1
    assert _run(r, env, "c\n\nDirector-doc: correction --   \n").returncode == 1


def test_an_unknown_kind_and_TWO_trailers_are_refused():
    """Defect: a malformed or doubled record satisfies the gate while recording nothing usable."""
    owed = ["M " + CANON]
    assert gate.verdict("x\n\nDirector-doc: tweak -- it read better\n", owed)[0] is False
    two = "x\n\nDirector-doc: record -- a\nDirector-doc: correction -- b\n"
    assert gate.verdict(two, owed)[0] is False


# --- the traffic that must pass untouched ------------------------------------------------------

def test_an_R100_archive_move_into_done_passes_with_no_trailer(repo):
    """Defect: every archival `git mv` of a ruling is refused -- the commonest director-doc traffic."""
    r, env = repo
    (r / "docs/staging/done").mkdir(exist_ok=True)
    _git(r, env, "mv", CANON, "docs/staging/done/" + Path(CANON).name)
    assert _run(r, env, "archive the canon\n").returncode == 0


def test_a_move_split_into_D_plus_A_passes_but_a_bare_D_is_refused(repo):
    """Defect: git pairs a move as D+A when the archive copy diverged, and the gate reads a deletion.

    The bare-D leg is the same branch's other side: a D that is NOT half of a move must still ask."""
    r, env = repo
    _git(r, env, "rm", "-q", CANON)
    _write(r, env, "docs/staging/done/" + Path(CANON).name, "# archived\n\nentirely different body\n")
    changes = gate.parse_name_status(_git(r, env, "diff", "--cached", "-M", "--name-status", "-z",
                                          "HEAD"))
    assert {c.status for c in changes} == {"D", "A"}, "the fixture must exercise the D+A shape"
    assert _run(r, env, "archive\n").returncode == 0

    _git(r, env, "rm", "-q", "--cached", "docs/staging/done/" + Path(CANON).name)
    done = _run(r, env, "drop the canon\n")
    assert done.returncode == 1 and "no archive copy" in done.stderr


def test_a_rename_that_ALSO_EDITS_is_a_content_change(repo):
    """Defect: an edit hidden inside an archive move (R<100) lands as if it were a pure move."""
    r, env = repo
    (r / "docs/staging/done").mkdir(exist_ok=True)
    _git(r, env, "mv", CANON, "docs/staging/done/" + Path(CANON).name)
    _write(r, env, "docs/staging/done/" + Path(CANON).name, CANON_TEXT + "a new closing line\n")
    done = _run(r, env, "archive\n")
    assert done.returncode == 1 and "renamed AND edited" in done.stderr


def test_a_NEW_director_document_needs_no_trailer(repo):
    """Defect: recording his words for the first time is treated as changing them."""
    r, env = repo
    _write(r, env, "docs/staging/DIRECTOR_RULING_NEW_2026-10-04.md", "# his ruling\n")
    assert _run(r, env, "file his ruling\n").returncode == 0


def test_a_DIRECTOR_CONSOLE_transcript_edit_passes(repo):
    """Defect: every console capture append asks for a trailer, teaching the reflexive `record`."""
    r, env = repo
    _write(r, env, CONSOLE, "his words\nmore of his words\n")
    assert _run(r, env, "capture console\n").returncode == 0


def test_an_unrelated_file_passes(repo):
    """Defect: the gate's scope leaks to every commit in the tree."""
    r, env = repo
    _write(r, env, "tools/x.py", "x = 2\n")
    assert _run(r, env, "change x\n").returncode == 0


def test_CLAUDE_md_outside_the_mission_block_passes_and_INSIDE_it_is_refused(repo):
    """Defect: either all of CLAUDE.md is reserved (the seat cannot keep its own file) or none is
    (the mission statement is rewritable by an ordinary commit)."""
    r, env = repo
    _write(r, env, "CLAUDE.md", MISSION_CLAUDE + "\n## New section\n\nseat prose\n")
    assert _run(r, env, "seat edits its file\n").returncode == 0

    _write(r, env, "CLAUDE.md", MISSION_CLAUDE.replace("We create value.", "We create margin."))
    done = _run(r, env, "sharpen the mission\n")
    assert done.returncode == 1 and "mission statement" in done.stderr


def test_the_scope_function_is_the_one_definition():
    assert gate.is_director_document("docs/design/DIRECTOR_CANON.md")
    assert gate.is_director_document("docs/staging/done/DIRECTOR_RULING_X_2026-09-01.md")
    assert gate.is_director_document("docs/design/THE_MODEL_ON_A_PAGE.md")
    assert not gate.is_director_document("docs/staging/console/DIRECTOR_CONSOLE_2026-09-01.md")
    assert not gate.is_director_document("docs/staging/console/SEAT_REPLY_2026-09-07.md")
    assert not gate.is_director_document("CLAUDE.md")
    assert not gate.is_director_document("tools/DIRECTOR_x.md")
    assert not gate.is_director_document("docs/staging/DIRECTOR_RULING_X.yaml")


def test_a_MERGE_is_not_asked_about_a_change_its_other_parent_carries(repo):
    """Defect: every `origin_reconcile` merge is refused for a canon amendment the trunk already
    landed -- the wedge `write_time_gate` and `next_step_gate` each paid for separately."""
    r, env = repo
    _git(r, env, "checkout", "-q", "-b", "side")
    _write(r, env, CANON, CANON_TEXT + "his amendment\n")
    _git(r, env, "commit", "-q", "-m", "amend\n\nDirector-doc: his-words -- console 2026-10-02")
    _git(r, env, "checkout", "-q", "main")
    _write(r, env, "tools/x.py", "x = 3\n")
    _git(r, env, "commit", "-q", "-m", "unrelated")
    _git(r, env, "merge", "-q", "--no-commit", "--no-ff", "side")
    assert _run(r, env, "merge side\n").returncode == 0

    # The control's other side: a merge that writes its OWN content into the canon is still asked.
    _write(r, env, CANON, CANON_TEXT + "his amendment\nand the merge's own sentence\n")
    assert _run(r, env, "merge side\n").returncode == 1


# --- the partition -----------------------------------------------------------------------------

def test_EVERY_branch_of_the_partition_is_reachable(repo):
    """A gate that refuses everything passes every 'does it refuse' test; one that refuses nothing
    passes every 'does it pass' test. One control over the whole partition."""
    r, env = repo
    seen = set()
    _write(r, env, CANON, CANON_TEXT + "edit\n")
    if _run(r, env, "edit\n").returncode == 1:
        seen.add("refuse")
    if _run(r, env, "edit\n\nDirector-doc: record -- header only\n").returncode == 0:
        seen.add("pass-by-trailer")
    _git(r, env, "reset", "-q", "HEAD", "--", CANON)
    _write(r, env, "tools/x.py", "x = 9\n")
    if _run(r, env, "edit\n").returncode == 0:
        seen.add("pass-by-scope")
    assert seen == {"refuse", "pass-by-trailer", "pass-by-scope"}


# --- failure, reporting, wiring ----------------------------------------------------------------

def test_an_unreadable_git_fails_OPEN_and_LOUDLY(tmp_path):
    """Defect: a broken git wedges every lane -- or fails open in silence, indistinguishable from
    'nothing in scope'. Run outside any repo: git cannot answer, and the gate must say so."""
    msg = tmp_path / "MSG"
    msg.write_text("x\n")
    done = subprocess.run([sys.executable, str(GATE), str(msg)], cwd=tmp_path, env=_env(tmp_path),
                          capture_output=True, text=True, timeout=60)
    assert done.returncode == 0
    assert "git unreadable, not blocking" in done.stderr


def test_the_report_counts_each_kind_from_the_commit_record(repo, monkeypatch):
    """Defect: the escape is prevented in name and uncounted in fact."""
    r, env = repo
    for i, trailer in enumerate(("correction -- wrong year, Ofgem table", "record -- header",
                                 "record -- lane", "his-words -- console 2026-10-01")):
        _write(r, env, "tools/x.py", f"x = {i + 10}\n")
        _git(r, env, "commit", "-q", "-m", f"c{i}\n\nDirector-doc: {trailer}\n")
    monkeypatch.chdir(r)
    got = gate.trailer_report(window=50)
    assert got["counts"] == {"correction": 1, "his-words": 1, "record": 2}
    assert sorted(reason for _, _, reason in got["reasons"]) == [
        "header", "lane", "wrong year, Ofgem table"]


def test_the_gate_FIRES_through_a_real_git_commit_via_core_hooksPath(repo, tmp_path):
    """Defect: a gate correct in isolation and never reached by `git commit`."""
    r, env = repo
    hooks = tmp_path / "hooks"
    hooks.mkdir()
    hook = hooks / "commit-msg"
    hook.write_text(f'#!/bin/sh\n"{sys.executable}" "{GATE}" "$1" || exit 1\n')
    hook.chmod(0o755)
    _git(r, env, "config", "core.hooksPath", str(hooks))
    _write(r, env, CANON, CANON_TEXT + "edit\n")
    refused = subprocess.run(["git", "commit", "-q", "-m", "edit"], cwd=r, env=env,
                             capture_output=True, text=True)
    assert refused.returncode != 0 and "COMMIT REFUSED" in refused.stderr
    landed = subprocess.run(["git", "commit", "-q", "-m",
                             "edit\n\nDirector-doc: correction -- typo in his date, console shows 2026-10-01"],
                            cwd=r, env=env, capture_output=True, text=True)
    assert landed.returncode == 0, landed.stderr


def test_the_gate_FIRES_through_surgical_lands_message_runner(repo, tmp_path):
    """Defect: the sanctioned landing door builds an extract the gate cannot read (wrong cwd, a
    leaked GIT_* env, HEAD not the parent) and every landing passes unasked."""
    from tools import surgical_land as sl

    r, env = repo
    parent = _git(r, env, "rev-parse", "HEAD").strip()
    checkout = tmp_path / "extract"
    checkout.mkdir()
    sl._make_standalone_repo(r, checkout, parent)
    hook = checkout / sl.MSG_HOOK_REL
    hook.parent.mkdir(parents=True)
    hook.write_text(f'"{sys.executable}" "{GATE}" "$1" || exit 1\n')
    (checkout / CANON).parent.mkdir(parents=True, exist_ok=True)
    (checkout / CANON).write_text(CANON_TEXT + "edit\n")
    subprocess.run(["git", "add", "--", CANON], cwd=checkout, env=sl._gitless_env(env), check=True)

    rc, _, err = sl.run_message_gate(checkout, "edit the canon\n")
    assert rc == 1 and "COMMIT REFUSED" in err
    rc, _, err = sl.run_message_gate(checkout, "edit\n\nDirector-doc: record -- header only\n")
    assert rc == 0, err


def test_the_REAL_hook_runs_the_gate_before_the_mark_is_stamped():
    """Defect: the gate exists and the hook never calls it, or calls it after the mark claims the
    whole chain completed."""
    text = (PROJECT / "tools" / "git-hooks" / "commit-msg").read_text()
    call = 'python3 tools/director_document_gate.py "$1" || exit 1'
    assert call in text
    assert text.index(call) < text.index("hook_gate_mark --stamp")


def test_the_reconciler_NAMES_this_gate_when_it_refuses_a_merge():
    """Defect: a reconcile merge refused here is logged as anonymous boilerplate, the shape
    `origin_reconcile._classify_merge_failure` was rebuilt to stop for the two sibling gates."""
    from background import origin_reconcile as orc

    out = "MESSAGE GATE RED (rc=1). boilerplate\n[director-doc-gate] COMMIT REFUSED.\nThis commit..."
    _, said = orc._classify_merge_failure(out)
    assert "tools/director_document_gate.py" in said
