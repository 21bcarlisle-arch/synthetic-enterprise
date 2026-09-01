"""The public page said "verified, showing run X" for a month, and X was in no commit.

WHAT WAS PUBLISHED. `site/data/publish_provenance.json` on `origin/main`:

    verification_state: "verified"
    showing_run.run_id: "run_output_5ccc0e0c8_20260831T130500Z.json"

**That file is in no commit.** The newest run artefact the tree tracks is dated 18 June; the newest
publish commit carrying one is 2026-07-29. Meanwhile the derived surfaces kept moving — they ride
into commits as incidental churn, because they are small — so `site/data/customers.json` publishes
**251 households** while `docs/reports/run_output_latest.json` in the same commit holds **19**, and
those 19 are a fossil of a different era of the simulation (12 resi, 2 SME, 5 I&C; the live book is
249 resi and 2 SME).

WHAT THE EXISTING GUARD CHECKED, AND THE SHAPE OF THE HOLE. `publishable_violations` already
refused a `run_id` that was fixture vocabulary, a `git_commit` that was not a sha, and a
`git_commit` naming no commit in the repo — *"an unavailable git reads as absent, fail-closed"*. It
asked whether the run's NAME was well-formed and whether the COMMIT existed. **It never asked
whether the RUN existed**, which is the one thing the sentence on the page is about.

WHY THE FIX IS NOT "RETAIN THE RUN". The live artefact is **27 MB**. One per publish is a gigabyte
of machine output in git within a month, which is exactly why no pathspec sweeps it and why no
amount of discipline would have changed anything. So the stamp carries the run's POPULATION —
three numbers — and the claim becomes falsifiable without the artefact: the surfaces shipped beside
it must agree with the run they are attributed to. Strictly weaker than reproducing the run,
strictly stronger than citing a file nobody can open.
"""
from __future__ import annotations

import json
import pathlib

import pytest

from background import publish_provenance as prov

PROJECT = pathlib.Path(__file__).resolve().parents[2]
PROVENANCE = PROJECT / "site" / "data" / "publish_provenance.json"
CUSTOMERS = PROJECT / "site" / "data" / "customers.json"


def _stamp(**over):
    base = {
        "run_id": "run_output_b8e6ba32d_20260831T130500Z.json",
        "git_commit": "b8e6ba32d",   # a real-shaped sha: `abc1234` is fixture vocabulary
                             # the guard already refuses, and my first draft used it
        "generated_at": "2026-08-31T13:05:00Z",
        "verified_at": "2026-08-31T13:32:35Z",
        "population": {"accounts": 251, "bills": 10948, "total_revenue_gbp": 801199.0},
        "run_retained": False,
    }
    base.update(over)
    return base


def test_a_stamp_that_says_nothing_about_its_run_is_refused():
    """The defect itself. A name with no population behind it is a citation, not a claim.

    MUTATION: drop the `population` branch from `publishable_violations` and this fires.
    """
    bad = {"showing_run": _stamp(population=None), "last_verified": _stamp()}
    violations = prov.publishable_violations(bad, check_commit_exists=False)
    assert any("population is missing" in v for v in violations), violations


def test_a_stamp_must_say_whether_the_run_can_be_opened():
    """`run_retained` is a stated fact, never an assumption.

    A reader who is told "showing run X" and nothing else will assume X is somewhere they could
    look. It is not, and it never will be at 27 MB a publish. Saying so is the difference between
    a citation and a false one.

    MUTATION: drop the `run_retained` branch and this fires.
    """
    incomplete = _stamp()
    incomplete.pop("run_retained")
    violations = prov.publishable_violations(
        {"showing_run": incomplete}, check_commit_exists=False)
    assert any("run_retained is unstated" in v for v in violations), violations


def test_a_publish_of_nothing_is_not_a_verification():
    """Zero accounts is the shape a broken or empty run takes, and it must not read as verified."""
    violations = prov.publishable_violations(
        {"showing_run": _stamp(population={"accounts": 0, "bills": 0, "total_revenue_gbp": 0.0})},
        check_commit_exists=False)
    assert any("accounts is zero" in v for v in violations), violations


def test_a_complete_stamp_publishes():
    """The leg that stops every other one being satisfied by a guard that refuses everything.

    A stamp naming an unretained run is PUBLISHABLE — that is the honest state of this project and
    refusing it would wedge publishing for ever. What is refused is publishing it *silently*.
    """
    assert prov.publishable_violations(
        {"showing_run": _stamp(), "last_verified": _stamp()},
        check_commit_exists=False) == []


def test_the_banner_says_what_the_run_held_and_whether_it_survives():
    """The sentence a visitor reads has to carry both, or the page is back where it started."""
    line = prov.banner_line({"verification_state": prov.STATE_VERIFIED,
                             "showing_run": _stamp()})
    assert "251 accounts" in line
    assert "10,948 bills" in line
    assert "not retained" in line

    kept = prov.banner_line({"verification_state": prov.STATE_VERIFIED,
                             "showing_run": _stamp(run_retained=True)})
    assert "not retained" not in kept, "a retained run must not be described as missing"


def test_run_retention_is_read_from_disk_and_absence_is_not_presence(tmp_path):
    """MUTATION: make `run_is_retained` return True on a missing file and this fires."""
    assert prov.run_is_retained("nothing_like_a_run.json", root=tmp_path) is False
    (tmp_path / "run_output_b8e6ba32d_20260831T130500Z.json").write_text("{}")
    assert prov.run_is_retained("run_output_b8e6ba32d_20260831T130500Z.json", root=tmp_path) is True
    # An unusable id is not a retained run, however the caller got it there.
    assert prov.run_is_retained(None, root=tmp_path) is False
    assert prov.run_is_retained("", root=tmp_path) is False


def test_the_population_counts_what_it_says_it_counts():
    """Three numbers, each named for the thing it counts. A `bills` that counted accounts would
    make every downstream reconciliation quietly wrong and nothing else would notice."""
    pop = prov.population_of({
        "per_customer_lifetime": {"C1": {}, "C2": {}, "C3": {}},
        "bills": [{}, {}, {}, {}],
        "total_revenue_gbp": 1234.567,
    })
    assert pop == {"accounts": 3, "bills": 4, "total_revenue_gbp": 1234.57}
    # A run missing a section reads as zero rather than raising: the publisher must be able to
    # stamp a degenerate run and have the ZERO refused above, not crash before it gets there.
    assert prov.population_of({}) == {"accounts": 0, "bills": 0, "total_revenue_gbp": 0.0}


@pytest.mark.skipif(not PROVENANCE.exists() or not CUSTOMERS.exists(),
                    reason="the published surfaces are not in this tree")
def test_THE_LIVE_PAGE_agrees_with_the_run_it_claims():
    """THE POINT OF ALL OF IT: the figures on the page must reconcile to the run named beside them.

    This is what a reader can now do and could not before. It is deliberately a reconciliation
    between two PUBLISHED files rather than against the run artefact, because the artefact is not
    retained — which is the whole reason the population is published in the first place.

    It SKIPS while the live provenance predates this change, and says so. That is not the check
    going quiet: a stamp without a population cannot be published at all once `record_verified`
    starts refusing it, so the skip window closes on the next publish and cannot reopen.
    """
    state = json.loads(PROVENANCE.read_text())
    showing = state.get("showing_run") or {}
    pop = showing.get("population")
    if not isinstance(pop, dict) or not pop.get("accounts"):
        pytest.skip(
            "the live provenance predates the population stamp — it names "
            f"{showing.get('run_id')!r} and says nothing about it, which is the defect this "
            "module was written for. The next publish closes this."
        )

    published = json.loads(CUSTOMERS.read_text())
    legs = sum(len(c.get("legs") or {}) for c in published.get("customers", []))
    assert legs == pop["accounts"], (
        f"the page publishes {legs} customer legs while claiming to show a run of "
        f"{pop['accounts']} accounts. One of the two is from a different run, which is exactly "
        "the drift that let 251 households be published from a tree holding 19."
    )
