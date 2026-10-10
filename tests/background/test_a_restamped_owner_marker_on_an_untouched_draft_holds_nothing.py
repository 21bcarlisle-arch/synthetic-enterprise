"""A fresh owner marker is a lease, not evidence of work: the draw's held-path refusal must not fire
on a worktree whose diff nobody has touched, however recently its marker was restamped.

THE DEFECT (2026-10-10). `considered-renewals-falling-from-53-to-3-is-explained` was refused 128
times by drafts untouched since 2026-10-03. A session's renewer loop touched all ~105 of its markers
every ten minutes, and `_live_holders` read a fresh marker naming a live pid as a holder. Measured on
the box the same evening: 105 marker-live worktrees before, 3 holders after -- each with a live
process working inside it.

MUTATIONS (each must fire):
  * drop the process leg of `editing_now` -- the with-a-process arm stops refusing.
  * drop the claim-window leg -- the freshly-written arm stops refusing.
  * drop the changed-since-refusal leg -- the changed arm stops refusing.
  * make `editing_now` return a reason unconditionally (the old marker-only behaviour) -- the
    untouched-draft arm refuses again.
"""

from __future__ import annotations

import os
import subprocess
import time

import pytest

from background import delivery_lane as dl
from background import seat_work_in_hand as claims_mod

ITEM = {"id": "explain-the-renewal-fall",
        "what": "Change `company/renewals.py` so the fall is explained."}
OLD = time.time() - 7 * 86400


@pytest.fixture
def draft(tmp_path, monkeypatch):
    """A worktree with a freshly stamped marker naming a live pid and a diff last written a week ago."""
    from background import launch_liveness

    repo = tmp_path / "wt"
    (repo / "company").mkdir(parents=True)
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    for args in (["init", "-q"], ["config", "core.hooksPath", "/dev/null"]):
        subprocess.run(["git", *args], cwd=repo, check=True, env=env)
    edited = repo / "company" / "renewals.py"
    edited.write_text("RATE = 1\n")
    subprocess.run(["git", "add", "."], cwd=repo, check=True, env=env)
    subprocess.run(["git", "commit", "-qm", "base"], cwd=repo, check=True, env=env)
    edited.write_text("RATE = 2\n")
    os.utime(edited, (OLD, OLD))
    (repo / ".se_worktree_owner").write_text(f"{os.getpid()}\n")  # fresh, live

    monkeypatch.setattr(launch_liveness, "live_units", lambda: [])
    monkeypatch.setattr(dl, "CLAIMS_FILE", tmp_path / "claims.json")
    real_git = dl._git
    monkeypatch.setattr(dl, "_git", lambda *a, cwd=None: (
        f"worktree {repo}\nHEAD 0\n" if a[:2] == ("worktree", "list") else real_git(*a, cwd=cwd)))
    return repo


def _refuses() -> bool:
    hit, _context = dl.held_grade(ITEM, dl._live_holders(), vocabulary=({}, 1))
    return hit is not None


def _record_refusal(repo, digest: str) -> None:
    claims_mod._save({"earlier": {"last_refused_at": time.time() - 3600, "artefact": str(repo),
                                  "diff_digest": digest}},
                     dl._refusals_path(dl.CLAIMS_FILE))


def test_an_untouched_draft_with_a_fresh_marker_refuses_only_with_a_process_inside(draft):
    holders = dl._live_holders()
    assert holders == [], "a restamped marker on an untouched draft held the subject"
    assert not _refuses()

    inside = subprocess.Popen(["sleep", "60"], cwd=draft / "company")
    try:
        assert _refuses(), "a live process working inside the worktree did not hold it"
        assert f"pid {inside.pid}" in dl._live_holders()[0]["editing"]
    finally:
        inside.kill()
        inside.wait()


def test_a_diff_unchanged_since_the_previous_refusal_holds_nothing_and_a_changed_one_holds(draft):
    copies: dict = {}
    dl._worktree_subject(draft, copies)
    _record_refusal(draft, dl._diff_digest(copies))
    assert not _refuses(), "a diff unchanged since its last refusal was refused again"

    _record_refusal(draft, "a-digest-from-before-the-diff-moved")
    assert _refuses(), "a diff changed since its previous refusal did not hold"


def test_a_write_inside_the_claim_window_holds_even_after_its_refusal_was_recorded(draft):
    edited = draft / "company" / "renewals.py"
    edited.write_text("RATE = 3\n")
    copies: dict = {}
    dl._worktree_subject(draft, copies)
    _record_refusal(draft, dl._diff_digest(copies))  # a watchdog read already recorded it
    assert _refuses(), "an edit written minutes ago was released by its own recorded refusal"


def test_the_refusal_records_the_digest_the_next_draw_compares(draft):
    """The chain, not the leg: a refusal written by `record_held_refusals` is what `editing_now`
    reads back, so an untouched draft refuses at most once per change."""
    inside = subprocess.Popen(["sleep", "60"], cwd=draft)
    try:
        holders = dl._live_holders()
    finally:
        inside.kill()
        inside.wait()
    assert holders and holders[0]["diff_digest"]
    dl.record_held_refusals([(ITEM, holders[0], "holds company/renewals.py")])
    assert dl._last_refused_digests() == {str(draft): holders[0]["diff_digest"]}
    assert not _refuses()
