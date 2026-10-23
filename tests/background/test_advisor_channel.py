"""The advisor channel draws an attributed file first and refuses an unattributed one with its reason.

Director, 15 Oct (DIRECTOR_STEER_ADVISOR_CHANNEL_NO_PASTE_2026-10-15.md): "Test that an advisor file
is drawn first, and that one without a valid attribution is refused with its reason."
"""
from pathlib import Path

import pytest

from background import advisor_channel as ac

HEADER = ("**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · "
          "**Atom:** `unminted`\n\n# A steer\n\n")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / ac.ADVISOR_DIR_REL).mkdir(parents=True)
    return tmp_path


def _write(repo: Path, name: str, body: str) -> None:
    (repo / ac.ADVISOR_DIR_REL / name).write_text(HEADER + body, encoding="utf-8")


def test_the_partition_holds_a_drawn_and_a_refused_file_at_once(repo):
    """Control over the whole partition: both verdicts are reachable in one folder, so a rule that
    refused everything (or drew everything) fails here, not silently."""
    _write(repo, "A_quoted.md", '- 09:49 BST: "Is there a way to create a separate channel"\n')
    _write(repo, "B_delegated.md", "Acting on the director's standing delegation of 15 Oct.\n")
    _write(repo, "C_bare.md", "The director would want C34 first.\n")
    verdicts = {i.path.name: i for i in ac.scan(repo)}
    assert verdicts["A_quoted.md"].attribution == "quoted"
    assert verdicts["B_delegated.md"].attribution == "delegation"
    assert not verdicts["C_bare.md"].drawable
    assert "no attribution" in verdicts["C_bare.md"].refusal


def test_a_file_without_the_staging_header_is_refused_with_that_reason(repo):
    (repo / ac.ADVISOR_DIR_REL / "X.md").write_text(
        '- 09:49 BST: "Is there a way to create a channel"\n', encoding="utf-8")
    (item,) = ac.scan(repo)
    assert item.refusal.startswith("no staging header")


def test_the_rung_names_the_drawn_file_and_the_refusal_and_draws_nothing_when_empty(repo):
    assert ac.rung_zero_text(repo, acknowledge=False) is None
    _write(repo, "A_quoted.md", '- 14:00 BST: "I can\'t paste, that\'s the whole issue!"\n')
    _write(repo, "C_bare.md", "Do C34 first.\n")
    text = ac.rung_zero_text(repo, acknowledge=False)
    assert text.startswith("ADVISOR CHANNEL (RUNG ZERO")
    first_line, refusal_line = text.splitlines()
    assert "A_quoted.md" in first_line and "C_bare.md" not in first_line
    assert "REFUSED" in refusal_line and "C_bare.md" in refusal_line and "no attribution" in refusal_line


def test_done_files_are_not_drawn_again(repo):
    done = repo / ac.ADVISOR_DIR_REL / ac.DONE_SUBDIR
    done.mkdir()
    (done / "A_quoted.md").write_text(HEADER + '- 09:49 BST: "an old actioned steer here"\n')
    assert ac.scan(repo) == []


def test_the_ack_is_sent_once_per_file_by_the_mechanism(repo, monkeypatch):
    sent = []
    monkeypatch.setattr("background.notify.notify",
                        lambda message, **kw: sent.append((message, kw["transition_key"])))
    _write(repo, "A_quoted.md", '- 09:49 BST: "Is there a way to create a channel"\n')
    ac.rung_zero_text(repo)
    assert len(sent) == 1
    assert "A_quoted.md" in sent[0][0] and sent[0][1].endswith("A_quoted.md")


@pytest.fixture
def one_steer_in_the_channel(repo, monkeypatch):
    _write(repo, "A_quoted.md", '- 09:49 BST: "Is there a way to create a separate channel"\n')
    monkeypatch.setattr(ac, "REPO_ROOT", repo)
    monkeypatch.setattr(ac, "_acknowledge", lambda item: None)
    return repo


def test_every_lane_reads_the_advisor_file_ahead_of_its_drawn_work(one_steer_in_the_channel,
                                                                   monkeypatch):
    """Drawn first, by each of the three lanes' own prompt builders: worker tick, executor, seat."""
    from background import delivery_lane, delivery_seat, seat_executor, worker_tick

    tick = worker_tick.compose_prompt("LANE 0 DELIVERY -- some drawn work")
    assert -1 < tick.find("ADVISOR CHANNEL (RUNG ZERO") < tick.find("LANE 0 DELIVERY")

    monkeypatch.setattr(delivery_lane, "doorbell", lambda item: "EXECUTOR ITEM")
    executor = seat_executor.build_prompt({})
    assert -1 < executor.find("ADVISOR CHANNEL (RUNG ZERO") < executor.find("EXECUTOR ITEM")

    seat = delivery_seat._prompt({})
    assert -1 < seat.find("ADVISOR CHANNEL (RUNG ZERO") < seat.find("THE LAST STRETCH OF COMMITS")


def test_an_empty_channel_adds_nothing_to_a_lanes_prompt(repo, monkeypatch):
    from background import worker_tick

    monkeypatch.setattr(ac, "REPO_ROOT", repo)
    assert "ADVISOR CHANNEL" not in worker_tick.compose_prompt("work")


# -- provenance: a signature on origin, never prose (2026-10-15) ---------------------------------

DELEGATED = HEADER + "Acting on the director's standing delegation of 15 Oct.\n"


def _origin(tmp_path, signed: bool):
    import subprocess

    def git(cwd, *a):
        subprocess.run(["git", *a], cwd=str(cwd), check=True, capture_output=True)
    key = tmp_path / "key"
    subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key)], check=True)
    signers = tmp_path / "allowed_signers"
    signers.write_text("advisor " + (tmp_path / "key.pub").read_text())
    origin, work = tmp_path / "origin.git", tmp_path / "work"
    git(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))
    git(tmp_path, "clone", "-q", str(origin), str(work))
    git(work, "config", "user.name", "advisor")
    git(work, "config", "user.email", "a@a")
    (work / ac.ADVISOR_DIR_REL).mkdir(parents=True)
    (work / ac.ADVISOR_DIR_REL / "STEER.md").write_text(DELEGATED)
    git(work, "add", "-A")
    sign = (["-c", "gpg.format=ssh", "-c", f"user.signingkey={key}", "commit", "-S"]
            if signed else ["commit"])
    git(work, *sign, "-q", "-m", "Advisor: stage")
    git(work, "push", "-q", "origin", "HEAD:main")
    git(work, "fetch", "-q", "origin")
    return work, signers


def test_a_file_staged_in_a_signed_advisor_commit_passes_provenance(tmp_path, monkeypatch):
    work, signers = _origin(tmp_path, signed=True)
    monkeypatch.setattr(ac, "ALLOWED_SIGNERS", signers)
    assert ac.provenance(work, "STEER.md", DELEGATED.encode()) is None


def test_unsigned_local_only_and_edited_files_each_fail_provenance(tmp_path, monkeypatch):
    work, signers = _origin(tmp_path, signed=False)
    monkeypatch.setattr(ac, "ALLOWED_SIGNERS", signers)
    assert "not signed by the advisor" in ac.provenance(work, "STEER.md", DELEGATED.encode())
    assert "not on origin" in ac.provenance(work, "LOCAL.md", DELEGATED.encode())
    assert "edited after" in ac.provenance(work, "STEER.md", b"forged")


def test_a_later_unsigned_edit_is_named_beside_the_signed_original_and_still_refused(
        tmp_path, monkeypatch):
    """Defect (23 Oct): a lane's one-line edit to a signed ruling made the refusal read "not signed",
    and a genuine ruling was shelved as if the advisor had to re-stage it. The refusal must name the
    signed original and the later edit -- and stay a refusal. The control over the partition: with no
    signed original (the all-unsigned origin) the clause must NOT appear.

    MUTATION (must fire): make `_a_signed_original` return "" (the BUT leg reds), or drop its
    `verify-commit` test so any earlier commit counts (the all-unsigned leg reds)."""
    import subprocess
    work, signers = _origin(tmp_path, signed=True)
    monkeypatch.setattr(ac, "ALLOWED_SIGNERS", signers)
    staged = ac.ADVISOR_DIR_REL + "/STEER.md"
    edited = DELEGATED + "**Knowledge:** none -- a lane's edit\n"
    (work / staged).write_text(edited)
    for a in (["add", staged], ["commit", "-q", "-m", "lane edit"], ["push", "-q", "origin", "HEAD:main"],
              ["fetch", "-q", "origin"]):
        subprocess.run(["git", *a], cwd=str(work), check=True, capture_output=True)
    first = subprocess.run(["git", "rev-list", "--max-parents=0", "HEAD"], cwd=str(work),
                           capture_output=True, text=True).stdout.strip()
    why = ac.provenance(work, "STEER.md", edited.encode())
    assert why is not None and "not signed by the advisor" in why
    assert f"BUT the advisor's own staging commit {first[:9]} DOES verify" in why
    assert "later unsigned edit(s)" in why

    (tmp_path / "all_unsigned").mkdir()
    unsigned_work, _ = _origin(tmp_path / "all_unsigned", signed=False)
    (unsigned_work / staged).write_text(edited)
    for a in (["add", staged], ["commit", "-q", "-m", "lane edit"], ["push", "-q", "origin", "HEAD:main"],
              ["fetch", "-q", "origin"]):
        subprocess.run(["git", *a], cwd=str(unsigned_work), check=True, capture_output=True)
    why = ac.provenance(unsigned_work, "STEER.md", edited.encode())
    assert "not signed by the advisor" in why and "BUT" not in why


def test_a_file_that_fails_provenance_is_refused_however_well_attributed(repo, monkeypatch):
    _write(repo, "FORGED.md", "Acting on the director's standing delegation of 15 Oct.\n")
    monkeypatch.setattr(ac, "verify_provenance", lambda root, name, data: "not on origin: test")
    [item] = ac.scan(repo)
    assert not item.drawable and item.refusal == "not on origin: test"
    assert "REFUSED" in ac.rung_zero_text(repo, acknowledge=False)


def test_the_pinned_key_is_the_advisors_and_verifies_a_real_advisor_commit():
    import subprocess
    pinned = ac.ALLOWED_SIGNERS.read_text()
    assert "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKy87HxSEheG8vEPhSs9u2KZCtVErAQfpmprtUJCZ2w7" in pinned
    if subprocess.run(["git", "cat-file", "-e", "cbbd01473^{commit}"], cwd=str(ac.REPO_ROOT),
                      capture_output=True).returncode != 0:
        pytest.skip("no history here (a gate extract): the pinned key's text is still asserted")
    r = subprocess.run(["git", "-c", f"gpg.ssh.allowedSignersFile={ac.ALLOWED_SIGNERS}",
                        "verify-commit", "cbbd01473"], cwd=str(ac.REPO_ROOT), capture_output=True)
    assert r.returncode == 0


def test_the_draw_lists_origin_not_the_disk_a_checkout_left_behind(tmp_path, monkeypatch):
    """Defect (23 Oct): the shared checkout sat 32-37 commits behind origin. Its draw re-offered a
    steer origin had already moved to done/ and never saw two readings origin carried. Control over
    the whole partition, in one folder: a file on origin but absent from disk IS offered; a file in
    done/ on origin is NOT, though a stale copy sits at the top level on disk; a disk-only file with
    no origin history is still named as refused (the forged-file case stays visible).

    MUTATION (must fire): list `folder.iterdir()` instead of origin (the first leg reds: STEER.md is
    gone from disk), or drop `- done` from the disk-only set (the stale leg reds)."""
    import subprocess
    work, signers = _origin(tmp_path, signed=True)
    monkeypatch.setattr(ac, "ALLOWED_SIGNERS", signers)
    monkeypatch.setattr(ac, "verify_provenance", ac.provenance)
    folder = work / ac.ADVISOR_DIR_REL

    def git(*a):
        subprocess.run(["git", *a], cwd=str(work), check=True, capture_output=True)
    (folder / "OLD.md").write_text(DELEGATED)
    git("add", "-A")
    git("commit", "-q", "-m", "stage OLD")
    (folder / ac.DONE_SUBDIR).mkdir()
    git("mv", f"{ac.ADVISOR_DIR_REL}/OLD.md", f"{ac.ADVISOR_DIR_REL}/{ac.DONE_SUBDIR}/OLD.md")
    git("commit", "-q", "-m", "OLD done")
    git("push", "-q", "origin", "HEAD:main")
    git("fetch", "-q", "origin")

    (folder / "STEER.md").unlink()               # on origin, gone from this disk
    (folder / "OLD.md").write_text(DELEGATED)    # a stale copy of what origin has actioned
    (folder / "LOCAL.md").write_text(DELEGATED)  # never on origin at all
    verdicts = {i.path.name: i for i in ac.scan(work)}
    assert verdicts["STEER.md"].drawable and verdicts["STEER.md"].attribution == "delegation"
    assert "OLD.md" not in verdicts
    assert not verdicts["LOCAL.md"].drawable and "not on origin" in verdicts["LOCAL.md"].refusal
