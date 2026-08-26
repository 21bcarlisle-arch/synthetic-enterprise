"""R15 proof for the claim deadline.

The defect this exists for: on 2026-08-20 the interactive seat claimed PB3, did not start it,
did not release it, and went silent for 4h23m while twenty commits landed from other lanes.
Every existing watcher was green, because every existing watcher asks whether the machine is
running rather than whether anything CLAIMED has stopped moving.

So the tests that matter are the ones that fire.
"""
from __future__ import annotations

import pytest

from background import seat_work_in_hand as S


@pytest.fixture
def claims(tmp_path):
    return tmp_path / "claims.json"


# ------------------------------------------------------------------ FIRES

def test_a_claim_that_has_not_moved_past_the_deadline_is_stale(claims):
    """The incident, reduced: claimed at T, nothing landed, 4h23m later."""
    S.claim("PB3_book_growth_as_earned_outcome", "starting the growth path",
            path=claims, now=1000.0)
    stale = S.stale_claims(path=claims, now=1000.0 + 4.38 * 3600, head_time=500.0)
    assert [w for w, _, _ in stale] == ["PB3_book_growth_as_earned_outcome"]
    assert stale[0][2] == pytest.approx(4.38 * 3600)


def test_sweeping_releases_the_claim_so_another_lane_can_take_it(claims, tmp_path):
    """Releasing is the POINT. Filing a document and leaving the claim in place would keep
    the work owned by the party that stopped -- the original defect with paperwork on top."""
    S.claim("PB3", "", path=claims, now=0.0)
    released = S.sweep(path=claims, now=S.STALE_AFTER_SECONDS + 1, head_time=0.0,
                       staging_dir=tmp_path)
    assert released == ["PB3"]
    assert S.stale_claims(path=claims, now=1e9, head_time=0.0) == []


def test_the_escalation_names_the_work_and_how_long_it_sat(claims, tmp_path):
    S.claim("PB3", "deferred on context budget", path=claims, now=0.0)
    S.sweep(path=claims, now=5 * 3600, head_time=0.0, staging_dir=tmp_path)
    filed = list(tmp_path.glob("*.md"))
    assert len(filed) == 1, f"expected exactly one filing, got {filed}"
    body = filed[0].read_text()
    assert "PB3" in body
    assert "5.0h" in body
    assert "deferred on context budget" in body, "the stated reason must survive into the record"


# ------------------------------------------------------- DOES NOT FIRE

def test_work_that_is_landing_commits_is_left_alone(claims):
    """A long piece of work that keeps committing is exactly what SHOULD be left alone. Ten
    hours in, with a commit against its paths a minute ago, it is the healthiest thing here."""
    S.claim("EP6", "", path=claims, now=1000.0)
    ten_hours_on = 1000.0 + 10 * 3600
    assert S.stale_claims(path=claims, now=ten_hours_on, head_time=ten_hours_on - 60) == []


def test_ONE_COMMIT_DOES_NOT_BUY_THE_CLAIM_ETERNITY(claims):
    """The unbounded-pass half of the 2026-08-26 defect, and the opposite mistake to the one
    above. `if moved > claimed_at: continue` meant a single commit at minute two exempted the
    claim from the deadline for good -- so a seat that landed one increment and then went
    silent for ten hours was certified as moving by a commit from nine and a half hours ago.
    That is the stall this module exists for, wearing a receipt.

    The deadline RESTARTS at each landing; it is not abolished by one.

    MUTATION (must fire): restore the `continue`.
    """
    S.claim("EP6", "", path=claims, now=1000.0)
    landed = 1001.0
    assert S.stale_claims(path=claims, now=landed + S.STALE_AFTER_SECONDS - 1,
                          head_time=landed) == []
    stale = S.stale_claims(path=claims, now=landed + 10 * 3600, head_time=landed)
    assert [w for w, _, _ in stale] == ["EP6"]
    assert stale[0][2] == pytest.approx(10 * 3600), (
        "the idle time is measured from the claim, not from the last thing that landed, so "
        "the alarm misreports how long the work has actually been still"
    )


def test_a_fresh_claim_is_not_stale(claims):
    S.claim("PB3", "", path=claims, now=1000.0)
    assert S.stale_claims(path=claims, now=1000.0 + 60, head_time=0.0) == []


def test_reclaiming_resets_the_deadline(claims):
    """The escape hatch for genuinely long work, and it costs one call. It must actually
    work, or the deadline becomes something to route around rather than use."""
    S.claim("PB3", "", path=claims, now=0.0)
    S.claim("PB3", "still on it", path=claims, now=S.STALE_AFTER_SECONDS - 1)
    assert S.stale_claims(path=claims, now=S.STALE_AFTER_SECONDS + 1, head_time=0.0) == []


# ------------------------------------------------------- FAILS SAFE

def test_a_corrupt_claims_file_leaves_work_drawable_rather_than_wedging(claims):
    """Fail toward DRAWABLE. The unsafe direction is work invisibly owned by nobody."""
    claims.write_text("{ this is not json")
    assert S.stale_claims(path=claims, now=1e9, head_time=0.0) == []
    S.claim("PB3", "", path=claims, now=0.0)          # must still be usable afterwards
    assert [w for w, _, _ in S.stale_claims(path=claims, now=1e9, head_time=0.0)] == ["PB3"]


def test_progress_is_measured_by_commits_not_by_the_claimant(claims):
    """TAUTOLOGY, R15's first killer pattern. If progress were a heartbeat the seat wrote,
    this control would certify a four-hour stall as healthy for as long as the staller kept
    saying it was fine. The only input that decides staleness is the commit clock."""
    S.claim("PB3", "I am definitely making progress", path=claims, now=0.0)
    assert [w for w, _, _ in S.stale_claims(path=claims, now=1e9, head_time=0.0)] == ["PB3"]


def test_a_claims_bound_SCOPE_CANNOT_GROW_WITHOUT_BOUND(claims):
    """The unbounded pass arriving through a different door. Every path added widens the set of
    commits that can certify the claim as moving, so a scope that grows for ever converges on
    "somebody touched something", which on this shared tree is always true -- the 2026-08-21
    defect rebuilt out of legitimate bindings.

    MUTATION (must fire): drop the cap and take the plain union.
    """
    S.claim("long-runner", "", path=claims, now=0.0)
    S.bind_paths("long-runner", [f"old/{i}.py" for i in range(S.MAX_BOUND_PATHS)], path=claims)
    newest = [f"new/{i}.py" for i in range(10)]
    scope = S.bind_paths("long-runner", newest, path=claims)

    assert len(scope) == S.MAX_BOUND_PATHS
    assert set(newest) <= set(scope), (
        "the cap dropped THIS landing's paths, so the newest evidence of progress is the "
        "evidence the deadline cannot see"
    )


def test_binding_paths_does_NOT_reset_the_deadline(claims):
    """The difference from re-claiming, and it is the anti-tautology property. If binding moved
    `claimed_at`, a tick could hold an item for ever by calling it -- a heartbeat with extra
    steps. Binding hands the deadline a SUBJECT; the commit clock still decides.

    MUTATION (must fire): set `claimed_at` in `bind_paths`.
    """
    S.claim("w", "", path=claims, now=1000.0)
    S.bind_paths("w", ["company/growth/x.py"], path=claims)
    stale = S.stale_claims(path=claims, now=1000.0 + S.STALE_AFTER_SECONDS + 1, head_time=0.0)

    assert [w for w, _, _ in stale] == ["w"]


def test_binding_paths_to_work_that_was_never_claimed_writes_NOTHING(claims):
    S.claim("real", "", path=claims, now=0.0)

    assert S.bind_paths("never-claimed", ["a.py"], path=claims) == []
    assert sorted(S._load(claims)) == ["real"]


def test_the_deadline_is_longer_than_a_fight_with_the_commit_gate(claims):
    """A gate run is ~15 minutes and several of 2026-08-20's commits took three attempts. A
    deadline under that would fire on honest work and get switched off."""
    assert S.STALE_AFTER_SECONDS >= 40 * 60


# ------------------------------------- THE SHARED-TREE HOLE (found 2026-08-21)
# Shipped 2026-08-20 comparing the claim against the TREE's HEAD. This is a shared checkout
# with four other lanes committing into it, so HEAD moves within minutes whatever the seat
# does -- and a live claim was observed reading as MOVING while the seat had done nothing.
# The first version avoided "the seat certifies itself" and landed on "the seat is certified
# by everyone else", which is the same defect wearing the opposite costume.

def test_another_lanes_commit_does_not_count_as_progress_on_my_claim(claims):
    """The exact observed failure: the tree moved, the claimed work did not."""
    S.claim("PB3", "", paths=["company/growth/"], path=claims, now=1000.0)
    # head_time is left to the real per-claim lookup; the claimed path has no commits, so a
    # busy tree cannot rescue it.
    stale = S.stale_claims(path=claims, now=1000.0 + 5 * 3600)
    assert [w for w, _, _ in stale] == ["PB3"], (
        "a claim was credited with work outside its own paths"
    )


def test_a_commit_touching_the_claimed_paths_IS_progress(claims):
    """Five hours past the claim -- long past the deadline, which WOULD have fired -- but a
    commit landed against the claimed paths a minute ago. That is the pass branch, and it has
    to be reachable or the verdict is a constant (the 2026-08-26 Lane 0 defect)."""
    S.claim("PB3", "", paths=["company/growth/"], path=claims, now=1000.0)
    now = 1000.0 + 5 * 3600
    assert S.stale_claims(path=claims, now=now, head_time=now - 60) == []


def test_a_claim_with_no_paths_releases_on_schedule(claims):
    """No paths means no observable progress signal. Releasing is the fail-safe direction:
    work nobody can see moving belongs back in the draw, not held by whoever asked for it."""
    S.claim("PB3", "", path=claims, now=0.0)
    stale = S.stale_claims(path=claims, now=S.STALE_AFTER_SECONDS + 1)
    assert [w for w, _, _ in stale] == ["PB3"]
