"""Tests for OPS14_aged_staging_named_daily -- clause 5 of
DIRECTOR_RULING_FINDING_SEVERITY_AND_INTERLEAVE_2026-08-12: any document in
the staging ROOT untouched for 72 hours is named in the daily digest --
filename, age in days, and one line of what it asks for -- every day, until
dispositioned. VISIBILITY ONLY: it stops nothing, refuses nothing, grants no
priority.

Exit criteria tested here (numbered as in docs/design/maturity_map.yaml,
OPS14_aged_staging_named_daily):
  1. a document staged and then ignored appears in the digest on day three
     with its CORRECT age, and keeps appearing on later days.
  2. the known fail-silent path is closed: a fresh finding firing its own
     NTFY this cycle must not suppress the aged-staging line.
  3. the clock is the last commit touching the path, not filesystem mtime
     (mtime is perturbed by concurrent daemons on this shared tree).
  4. R15 both ways -- a mutation letting the digest go quiet with an aged
     document present, and one skewing the age computation, each kill a
     named test here.
  5. the four documents that motivated the clause are flagged aged against
     the REAL staging root.
"""
import os
import subprocess
import time

from background import sanity_daemon


def _write_doc(staging_dir, name, body="# a staged document\nsomething to disposition\n"):
    staging_dir.mkdir(parents=True, exist_ok=True)
    doc = staging_dir / name
    doc.write_text(body)
    return doc


# --- Criterion 1: correct age on day three, keeps appearing ---

def test_aged_document_appears_on_day_three_with_correct_age_and_keeps_appearing(tmp_path, monkeypatch):
    staging = tmp_path / "staging"
    doc = _write_doc(staging, "WORKER_FINDING_IGNORED.md", "# a finding nobody opened\nsomething concerning\n")
    monkeypatch.setattr(sanity_daemon, "STAGING_ROOT", staging)

    t0 = 1_000_000.0
    monkeypatch.setattr(sanity_daemon, "_last_touched_epoch", lambda p: t0)

    # Day 3: 73 hours later, past the 72h threshold.
    day3 = t0 + 73 * 3600
    entries = sanity_daemon._aged_staging_entries(now=day3)
    assert len(entries) == 1
    assert entries[0]["filename"] == doc.name
    assert abs(entries[0]["age_days"] - 73 / 24) < 0.01
    assert "finding nobody opened" in entries[0]["summary"]

    # Day 4: it keeps appearing, and the age has advanced correctly (not
    # frozen at first sighting, not reset).
    day4 = t0 + 97 * 3600
    entries2 = sanity_daemon._aged_staging_entries(now=day4)
    assert len(entries2) == 1
    assert abs(entries2[0]["age_days"] - 97 / 24) < 0.01


def test_threshold_boundary_just_under_72h_excluded_at_72h_included(tmp_path, monkeypatch):
    staging = tmp_path / "staging"
    _write_doc(staging, "DOC.md")
    monkeypatch.setattr(sanity_daemon, "STAGING_ROOT", staging)
    t0 = 1_000_000.0
    monkeypatch.setattr(sanity_daemon, "_last_touched_epoch", lambda p: t0)

    just_under = t0 + 71 * 3600
    assert sanity_daemon._aged_staging_entries(now=just_under) == []

    at_threshold = t0 + 72 * 3600
    entries = sanity_daemon._aged_staging_entries(now=at_threshold)
    assert len(entries) == 1


def test_a_fresh_document_is_never_flagged(tmp_path, monkeypatch):
    staging = tmp_path / "staging"
    _write_doc(staging, "JUST_STAGED.md")
    monkeypatch.setattr(sanity_daemon, "STAGING_ROOT", staging)
    monkeypatch.setattr(sanity_daemon, "_last_touched_epoch", lambda p: time.time())
    assert sanity_daemon._aged_staging_entries() == []


def test_subdirectories_of_staging_root_are_excluded(tmp_path, monkeypatch):
    """done/, in_progress/ etc are each owned by a different mechanism (the
    48h auto-archive, the misparked scanners) -- clause 5 is about the root
    only, where a document nobody has opened at all still sits."""
    staging = tmp_path / "staging"
    staging.mkdir()
    (staging / "done").mkdir()
    _write_doc(staging / "done", "OLD_BUT_ARCHIVED.md")
    (staging / "in_progress").mkdir()
    _write_doc(staging / "in_progress", "OLD_BUT_IN_PROGRESS.md")
    monkeypatch.setattr(sanity_daemon, "STAGING_ROOT", staging)
    monkeypatch.setattr(sanity_daemon, "_last_touched_epoch", lambda p: time.time() - 10 * 24 * 3600)
    assert sanity_daemon._aged_staging_entries() == []


# --- Criterion 2: the known fail-silent path is closed ---

def test_digest_carries_aged_staging_even_when_a_fresh_finding_fired_this_cycle(tmp_path, monkeypatch):
    """Before OPS14, _maybe_send_daily_digest's whole body lived inside
    `if not any_new_this_cycle:` -- a fresh NTFY firing this cycle silently
    dropped the digest (and, after this atom exists, the aged-staging line
    with it) for the entire UTC day. The aged block must survive that
    branch: a mutation re-nesting it inside `if not any_new_this_cycle:`
    must fail this test."""
    staging = tmp_path / "staging"
    _write_doc(staging, "OLD_DOC.md", "# stale finding\nplease look\n")
    monkeypatch.setattr(sanity_daemon, "STAGING_ROOT", staging)
    monkeypatch.setattr(sanity_daemon, "_last_touched_epoch", lambda p: time.time() - 10 * 24 * 3600)
    monkeypatch.setattr(sanity_daemon, "LAST_DIGEST_DATE_FILE", tmp_path / ".last_digest_date")

    calls = []
    monkeypatch.setattr(sanity_daemon, "_digest", lambda msg: calls.append(msg))
    monkeypatch.setattr(sanity_daemon, "LOG_FILE", tmp_path / "log.md")

    # any_new_this_cycle=True is exactly the branch that used to skip the
    # digest body entirely.
    sanity_daemon._maybe_send_daily_digest(any_new_this_cycle=True)

    assert len(calls) == 1
    assert "AGED STAGING" in calls[0]
    assert "OLD_DOC.md" in calls[0]


def test_digest_still_dedupes_to_once_per_day_with_aged_docs_present(tmp_path, monkeypatch):
    """The per-day cadence is retained -- clause 5 asks for 'named daily',
    not renotified every 30-minute cycle."""
    staging = tmp_path / "staging"
    _write_doc(staging, "OLD_DOC.md")
    monkeypatch.setattr(sanity_daemon, "STAGING_ROOT", staging)
    monkeypatch.setattr(sanity_daemon, "_last_touched_epoch", lambda p: time.time() - 10 * 24 * 3600)
    monkeypatch.setattr(sanity_daemon, "LAST_DIGEST_DATE_FILE", tmp_path / ".last_digest_date")
    monkeypatch.setattr(sanity_daemon, "LOG_FILE", tmp_path / "log.md")
    calls = []
    monkeypatch.setattr(sanity_daemon, "_digest", lambda msg: calls.append(msg))

    sanity_daemon._maybe_send_daily_digest(any_new_this_cycle=False)
    sanity_daemon._maybe_send_daily_digest(any_new_this_cycle=False)
    sanity_daemon._maybe_send_daily_digest(any_new_this_cycle=False)
    assert len(calls) == 1

    sanity_daemon.LAST_DIGEST_DATE_FILE.unlink()
    sanity_daemon._maybe_send_daily_digest(any_new_this_cycle=False)
    assert len(calls) == 2  # a new day -- named again, not silence forever


def test_no_digest_at_all_when_nothing_is_aged_and_nothing_is_open(tmp_path, monkeypatch):
    """The aged block must not manufacture a digest out of nothing -- it is
    additive to the existing behaviour, not a standing heartbeat."""
    staging = tmp_path / "staging"
    staging.mkdir()
    monkeypatch.setattr(sanity_daemon, "STAGING_ROOT", staging)
    monkeypatch.setattr(sanity_daemon, "LAST_DIGEST_DATE_FILE", tmp_path / ".last_digest_date")
    monkeypatch.setattr(sanity_daemon, "LOG_FILE", tmp_path / "log.md")
    from company.compliance import sanity_adjudication
    monkeypatch.setattr(sanity_adjudication, "LEDGER_PATH", tmp_path / "ledger.json")
    calls = []
    monkeypatch.setattr(sanity_daemon, "_digest", lambda msg: calls.append(msg))

    sanity_daemon._maybe_send_daily_digest(any_new_this_cycle=False)
    assert calls == []


# --- Criterion 3: the clock is commit time, not mtime ---

def test_last_touched_epoch_uses_commit_time_not_a_perturbed_mtime(tmp_path, monkeypatch):
    """Builds a tiny real git repo, commits a document with an explicit old
    commit date, then rewrites its mtime to right now -- simulating a
    concurrent daemon touching the file without anyone opening it. The
    computed 'touched' time must reflect the OLD commit, never the fresh
    mtime -- a mutation swapping git-log for path.stat().st_mtime must fail
    this test."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    doc = repo / "OLD_DOC.md"
    doc.write_text("# an old document\nsomething to disposition\n")

    old_commit_epoch = time.time() - 10 * 24 * 3600  # 10 days ago
    env = dict(os.environ)
    env["GIT_AUTHOR_DATE"] = f"{int(old_commit_epoch)} +0000"
    env["GIT_COMMITTER_DATE"] = f"{int(old_commit_epoch)} +0000"
    subprocess.run(["git", "add", "OLD_DOC.md"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "stage old doc"], cwd=repo, check=True, env=env)

    # A daemon rewrites the file's mtime to "now" without anyone reading it.
    now = time.time()
    os.utime(doc, (now, now))

    monkeypatch.setattr(sanity_daemon, "PROJECT_DIR", repo)
    touched = sanity_daemon._last_touched_epoch(doc)
    assert touched is not None
    assert abs(touched - old_commit_epoch) < 5  # the commit time, to the second
    assert now - touched > 9 * 24 * 3600  # decisively NOT the fresh mtime


def test_last_touched_epoch_falls_back_to_mtime_for_a_never_committed_file(tmp_path, monkeypatch):
    """The one case mtime is a safe signal: a file with no commit history at
    all (staged but never committed) -- git has never seen it, so no daemon
    rewrite can have perturbed a 'touched' time that does not yet exist."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    doc = repo / "NEVER_COMMITTED.md"
    doc.write_text("# never committed\n")
    monkeypatch.setattr(sanity_daemon, "PROJECT_DIR", repo)
    assert sanity_daemon._last_touched_epoch(doc) is None  # caller applies the mtime fallback


# --- Criterion 5: the four motivating documents are flagged, against the REAL root ---

def test_the_four_documents_that_motivated_clause_5_are_flagged_aged():
    """Runs against the REAL docs/staging root (no monkeypatch) -- these are
    real, currently unopened documents named in the ruling itself, not test
    fixtures: the money-core characterisation, the CLAUDE.md decay audit,
    the seat cutover/DR proposal, and the failure-modes/birth-certificate-law
    retro (the ruling's 'oldest a week old' document). If one has since been
    dispositioned (moved out of the staging root), it is skipped rather than
    failed -- dispositioning is the intended exit from this mechanism's own
    visibility, not a defect in it."""
    motivating = [
        "ADVISOR_FINDINGS_MONEY_CORE_CHARACTERIZATION_2026-08-06.md",
        "ADVISOR_FINDINGS_CLAUDE_MD_DECAY_AUDIT_2026-08-07.md",
        "ADVISOR_PROPOSAL_SEAT_CUTOVER_AND_DR_2026-08-07.md",
        "ADVISOR_RETRO_FAILURE_MODES_AND_BIRTH_CERTIFICATE_LAW_2026-08-05.md",
    ]
    still_staged = [f for f in motivating if (sanity_daemon.STAGING_ROOT / f).is_file()]
    assert still_staged, "all four motivating documents have been dispositioned -- nothing left to check"

    aged_names = {e["filename"] for e in sanity_daemon._aged_staging_entries()}
    for f in still_staged:
        assert f in aged_names, (
            f"{f} should be flagged aged (>=72h untouched) but was not -- "
            f"the mechanism may be looking at the wrong population"
        )
