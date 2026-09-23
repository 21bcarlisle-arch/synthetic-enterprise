"""A published feed must be what its generator produces — checked, not assumed.

THE DEFECT THIS EXISTS FOR, repaired as ONE INSTANCE in `1d5642c35` on 2026-09-19. A false
regulatory citation — `Ofgem SLC 27B`, a regulation that does not exist — was corrected by hand in
`site/data/simplified.json` and `site/data/dashboard.json` on 2026-09-03, and never in
`docs/design/simplifications/DD_seasonal_cashflow_physics.yaml`, which
`tools/generate_simplified_data` copies BYTE-IDENTICALLY. The correction was right and the source it
came from was never touched, so it survived sixteen days as hand-edited committed bytes and the
first regeneration reverted it. Nothing anywhere compared a published feed against what its
generator would produce, so the edit was correct on disk, reverted at the next run, and
unobservable in between. This file is that comparison, over the feeds where it means something.

WHY NOT EVERY FEED — MEASURED 2026-09-19, NOT ASSUMED. Regenerating all 61 published feeds and
demanding equality reds 24 of the 31 that run, and almost none of those from a hand-edit. They
diverge because the feed is a function of things that are not in the commit: the live git log
(`phases.json`'s commit count, `evidence.json`'s hash), the live staging directory
(`method.json`, `system_status.json`), a gitignored Elexon cache (`sim_data.json`, which
regenerates to zero records without it), or a run artefact (`dashboard.json`, `supplier.json`,
`proof.json`). A control that reds on those is red the day it lands and muted by the end of the
week, which is worse than no control. So the assertion is scoped to the feeds that ARE a function
of their commit, and the rest are reported by the instrument as named gaps rather than quietly
dropped.

THE COVERED SET IS NOT ALLOWED TO BE TODAY'S ANSWER. A list of feeds pinned to what passed on the
day it was written is exactly the shape this project has been burned by — it goes green when the
claim rots. Three legs stop that here. `test_a_feed_that_became_checkable_must_be_promoted` sweeps
every cheap generator and reds if ANY feed outside the covered set now reproduces, so the set can
only ever grow and the exclusion can never be silently kept.
`test_a_covered_feed_that_is_not_a_function_of_its_commit_must_be_demoted` is the same question in
the direction the promotion leg cannot see, and it is the one that was missing: membership can be
wrong by a feed being IN the set that never belonged. And
`test_the_instrument_can_return_all_three_verdicts` asserts over the whole partition, because an
instrument that answered AGREES to everything would pass every other test in this file.

WHY A DEMOTION LEG HAD TO EXIST — MEASURED 2026-09-23, and it is the defect three of this file's
tests reddened for. `knowledge_review.json` was covered for four days and was never a function of
its commit: it publishes `age_days`, which is `date.today()` minus a committed date. It got in
because the determinism probe is ordinarily only built when the first tree DISAGREES, so a feed
whose committed bytes are fresh is promoted without the one question that would have refused it —
and because both probe runs happen seconds apart, which cannot see a quantity that changes once a
day. The module now displaces the probe's clock by 400 days and the fixture here forces the probe
even on agreement, so the membership rule is measured rather than inherited.

WHAT IS NOT COVERED, stated rather than left to be discovered. Three generators sit outside the
promotion sweep on cost alone, and `TOO_SLOW_TO_SWEEP` carries each one's measured seconds rather
than the word "slow". None of the three writes a feed that reproduces today, so the exclusion costs
no coverage — but that is a fact about today, and the figures are there so the next reader can
re-decide it rather than inherit it.
"""
from __future__ import annotations

import json
import pathlib
import subprocess

import pytest

from tools import provenance_stamp
from tools.published_feed_regeneration_check import (
    _SCRATCH_NEEDS_MB,
    CANDIDATES_AT_THEIR_OWN_COMMIT,
    COVERED_AT_THEIR_OWN_COMMIT,
    COVERED_FEEDS,
    NOT_A_FUNCTION_OF_ITS_COMMIT,
    RegenerationCheckRefused,
    _free_mb,
    _verdict,
    _why_the_clone_failed,
    check,
    check_at_its_own_commit,
    covered_generators,
    head_resolves,
    recorded_publication_commit,
    scratch_root,
)

PROJECT = pathlib.Path(__file__).resolve().parents[2]

#: The covered set has ONE home, in the module under test — the publish path in
#: `background/process_run_complete` reads the same table to name what a regeneration is about to
#: revert, and a second copy here would drift invisibly.
COVERED = COVERED_FEEDS

#: Measured per-generator cost in a clone on 2026-09-19, in seconds. Excluded from the promotion
#: sweep on cost alone — named here with the figure, because a bound nobody states reads as a sweep
#: that covered everything. These three are 76% of the sweep between them; without them it is ~50s.
#: None of the three writes a feed that reproduces today, so excluding them costs no coverage now —
#: but that is a fact about today, which is why they are named rather than deleted.
TOO_SLOW_TO_SWEEP = {
    "generate_provisional_plan_data": 251,   # `git log --reverse --follow` over the whole history
    "generate_test_mix_data": 117,           # collects the suite
    "generate_weather_cells_data": 95,
}


def _committed_feed_doc(feed: str) -> dict:
    """A published feed as HEAD holds it — never as the working tree holds it.

    Several lanes hold dirty copies of `site/data/` at any moment in the shared tree, so a leg that
    read disk would be asking about another lane's unfinished edit. Same baseline as the module
    under test, reached independently of it.
    """
    return json.loads(subprocess.run(
        ["git", "-C", str(PROJECT), "show", f"HEAD:site/data/{feed}"],
        capture_output=True, text=True, check=True).stdout)


def _account_in(block) -> str | None:
    """The reason a provenance block gives for its feed having no standpoint, or None.

    WHY THIS IS NOT A RESTATEMENT OF THE MODULE. `recorded_publication_commit` composes the same
    facts and returns a prose reason; asserting that its prose contains a phrase would be a control
    typed against its own subject's current output. This reads the reserved provenance block
    directly — a different route to the same property — so the two can disagree, which is the only
    way either of them can be wrong.

    A feed that says its stamped commit DOES describe its inputs is not self-explaining an absent
    standpoint; it is contradicting one, and that must stay red. Kept pure and separate from the
    git read below so the whole partition can be driven —
    `test_a_self_explained_refusal_is_told_apart_from_an_unexplained_one`.
    """
    if not isinstance(block, dict) or provenance_stamp.describes_its_inputs(block):
        return None
    reason = block.get("reason")
    return reason if isinstance(reason, str) and reason.strip() else None


def _the_feeds_own_account_of_having_no_standpoint(feed: str) -> str | None:
    """`_account_in` over a feed's COMMITTED provenance block."""
    return _account_in(_committed_feed_doc(feed).get(provenance_stamp.STAMP_KEY))


@pytest.fixture(scope="module")
def covered_rows():
    # DETERMINISM IS PROBED EVEN WHERE THE FIRST TREE AGREED, which is what membership in `COVERED`
    # actually claims. `knowledge_review.json` was covered for four days because the second tree is
    # ordinarily only built on disagreement, so the one question that would have refused it was
    # never asked of it. Doubles this fixture's cost and is the point of it.
    return check(covered_generators(), always_probe_determinism=True)


def test_every_covered_feed_is_what_its_generator_produces(covered_rows):
    """THE DEFECT: the SLC-27B citation, corrected in `simplified.json` and never in the .yaml the
    generator copies. Any hand-edit to a covered feed reds here on the day it is made."""
    by_feed = {r["feed"]: r for r in covered_rows if r["feed"]}
    divergent = {
        feed: row["detail"].get("changed", [])[:3]
        for feed, row in by_feed.items()
        if feed in COVERED and row["verdict"] == "DIVERGES"
    }
    assert not divergent, (
        "a published feed is not what its generator produces — the committed bytes were edited "
        "downstream of the source, and the next regeneration will revert them:\n"
        + json.dumps(divergent, indent=1)
    )


def test_every_covered_feed_was_actually_reached(covered_rows):
    """THE DEFECT THIS CATCHES: a generator that stops writing its feed, or is renamed, leaves the
    feed unchecked while every assertion above still passes — an empty evidence set reading as no
    complaint. The check is that each covered feed was REACHED, not that nothing complained."""
    reached = {r["feed"] for r in covered_rows if r["feed"]}
    missing = sorted(set(COVERED) - reached)
    assert not missing, (
        f"{len(missing)} covered feed(s) were never produced by the generator that owns them, so "
        f"nothing above graded them: {missing}"
    )


def test_a_covered_feed_that_is_not_a_function_of_its_commit_must_be_demoted(covered_rows):
    """THE DEFECT THIS CATCHES, and it is the one that actually happened — membership in `COVERED`
    being wrong in the DIRECTION the promotion leg cannot see.

    `test_a_feed_that_became_checkable_must_be_promoted` makes the set unable to shrink silently.
    Nothing made it unable to GROW wrongly, and on 2026-09-19 it did: `knowledge_review.json`
    publishes `date.today()` minus a committed date, agreed with its fresh committed bytes on the
    day it was added, and reds two days later for no fault of anybody's. A control that must be
    re-greened daily is not a control.

    Keyed to the property the table claims — "this feed is a function of its commit" — and measured
    by the fixture's displaced-clock probe rather than by knowing which feed it was."""
    not_a_function = {
        r["feed"]: r["detail"].get("run_to_run")
        for r in covered_rows
        if r["feed"] in COVERED and r["verdict"] == "NONDETERMINISTIC"
    }
    assert not not_a_function, (
        f"{len(not_a_function)} covered feed(s) are not a function of their commit, so comparing "
        "them against committed bytes says nothing and they will red on a clock nobody edited. "
        "Demote them and record the reason in `NOT_A_FUNCTION_OF_ITS_COMMIT`:\n"
        + json.dumps(not_a_function, indent=1)
    )


def test_the_feed_the_defect_happened_on_is_covered():
    """A covered set that shrank to the feeds nobody edits would pass every test here. The feed the
    SLC-27B edit was actually made on is the one that must be in it.

    THE FLOOR, RE-DERIVED 2026-09-23 RATHER THAN DECREMENTED. It used to read `len(COVERED) >= 8`,
    which was a count of what passed on 2026-09-19. When `knowledge_review.json` was correctly
    demoted — for a measured reason, by the leg above — the only way to keep that line green was to
    edit the 8 down to a 7, and a floor you edit to fit is not a floor: it would have gone green for
    a set gutted one feed at a time.

    What the count was standing in for is that the set may only shrink through a NAMED door. Covered
    plus named-and-explained demotions is monotone non-decreasing whatever happens to either side,
    so this ratchet never needs editing downward — which is the property, rather than today's 7."""
    assert "simplified.json" in COVERED
    assert len(COVERED) + len(NOT_A_FUNCTION_OF_ITS_COMMIT) >= 8, (
        "the covered set shrank without the departing feed being recorded — a set that can shrink "
        "silently is not a control"
    )
    both = sorted(set(COVERED) & set(NOT_A_FUNCTION_OF_ITS_COMMIT))
    assert not both, f"a feed is both covered and recorded as uncheckable: {both}"
    unexplained = sorted(f for f, why in NOT_A_FUNCTION_OF_ITS_COMMIT.items()
                         if not (isinstance(why, str) and why.strip()))
    assert not unexplained, (
        f"a feed left the covered set with no reason beside it, which is indistinguishable from a "
        f"feed deleted to make a red go away: {unexplained}"
    )


def test_a_hand_edit_to_a_covered_feed_is_caught():
    """THE MUTATION. The 2026-09-03 edit, replayed: change the published prose and leave the source
    alone. If this returns anything but DIVERGES the control above cannot fail."""
    committed = json.dumps({"generated_at": "A", "notes": ["Ofgem SLC 27.15 duty -- corrected"]})
    regenerated = json.dumps({"generated_at": "B", "notes": ["Ofgem SLC 27B +/-5pct variance"]})
    verdict, detail = _verdict(committed.encode(), regenerated.encode(), regenerated.encode())
    assert verdict == "DIVERGES", f"the hand-edit was not caught: {verdict} {detail}"
    assert detail["n_changed"] == 1


def test_the_instrument_can_return_all_three_verdicts():
    """THE CONTROL OVER THE WHOLE PARTITION. Every test above asks "does it refuse correctly", and
    an instrument that answered DIVERGES — or AGREES — to everything would pass all of them. This
    asserts the three verdicts are each REACHABLE, which is the leg that catches a comparator
    neutered into a constant."""
    same = json.dumps({"generated_at": "A", "v": 1}).encode()
    clock_moved = json.dumps({"generated_at": "B", "v": 1}).encode()
    changed = json.dumps({"generated_at": "B", "v": 2}).encode()
    changed_again = json.dumps({"generated_at": "C", "v": 3}).encode()

    assert _verdict(same, clock_moved, None)[0] == "AGREES", "the clock alone is not a divergence"
    assert _verdict(same, changed, changed)[0] == "DIVERGES"
    assert _verdict(same, changed, changed_again)[0] == "NONDETERMINISTIC", (
        "a feed that differs run-to-run is not evidence about its committed bytes"
    )


def test_an_unparseable_feed_is_never_a_pass():
    """FAIL CLOSED. A feed that cannot be read must not collapse into the flattering branch: a
    control over committed bytes may not go green because it could not find out what they were."""
    verdict, _ = _verdict(b"{not json", b"{}", None)
    assert verdict == "UNPARSEABLE"
    verdict, _ = _verdict(b"{}", b"{not json", b"{}")
    assert verdict in {"UNPARSEABLE", "DIVERGES"}


def test_naming_no_generator_is_refused_not_reported_clean():
    """An empty sweep agrees with every claim ever made. It must refuse, not return []."""
    with pytest.raises(RegenerationCheckRefused):
        check([])


def test_a_feed_that_became_checkable_must_be_promoted():
    """THE DEFECT THIS CATCHES: `COVERED` silently becoming a record of what passed on 2026-09-19.

    A feed drops out of the covered set only because it is not a function of its commit. The moment
    that stops being true — a generator stops reading the live git log, a cache gets committed — the
    feed is checkable and leaving it out is a gap nobody would ever notice. This sweeps every cheap
    generator and reds if any feed outside `COVERED` now reproduces, so the set can only grow.

    THE SWEEP IS CHEAP AND THE PROMOTION IS NOT. The wide pass runs with the determinism tree off,
    because AGREES is settled on the first tree and paying for a second over 51 generators to tell
    apart two verdicts this pass treats alike is not worth the wall clock. But AGREES from that
    pass is exactly what promoted `knowledge_review.json` on 2026-09-19 — a clock-dependent feed
    whose committed bytes happened to be fresh — so anything it proposes is CONFIRMED against the
    displaced-clock probe before it is demanded. The confirmation runs over whatever the wide pass
    found, which is normally nothing.
    """
    cheap = sorted(
        p.stem for p in (PROJECT / "tools").glob("generate_*.py")
        if p.stem not in TOO_SLOW_TO_SWEEP
    )
    rows = check(cheap, separate_nondeterminism=False)
    # NON-VACUITY. A sweep that reached nothing proposes nothing and agrees with every claim ever
    # made, which is how the assertion below would go green on a broken clone or an emptied glob.
    reached = {r["feed"] for r in rows if r["feed"]}
    assert set(COVERED) <= reached, (
        f"the sweep did not even reach the covered feeds, so it can propose nothing and says "
        f"nothing: {sorted(set(COVERED) - reached)}"
    )
    proposed = sorted({
        r["generator"] for r in rows
        if r["feed"] and r["verdict"] == "AGREES" and r["feed"] not in COVERED
    })
    confirmed = check(proposed, always_probe_determinism=True) if proposed else []
    promotable = sorted({
        r["feed"] for r in confirmed
        if r["verdict"] == "AGREES" and r["feed"] not in COVERED
    })
    assert not promotable, (
        f"{len(promotable)} feed(s) now reproduce from their commit but are not in COVERED, so "
        f"nothing checks them: {promotable}. Add them to COVERED with their generator."
    )


def test_the_real_2026_09_03_hand_edit_reds_the_whole_pipeline(tmp_path):
    """THE MUTATION, END TO END — the one that proves the CONTROL can fail and not just its
    comparator.

    `test_a_hand_edit_to_a_covered_feed_is_caught` mutates `_verdict` alone, so it establishes the
    comparator works and says nothing about the clone, the generator run, or the baseline. Here the
    2026-09-03 edit is replayed for real: a covered feed's published prose is changed and COMMITTED
    in a private clone, its source left alone, and the full path is asked. A control that regenerated
    into the wrong tree, or compared the output against itself, would be green here.
    """
    if not head_resolves(PROJECT):
        pytest.skip("no HEAD here — this is the landing checkout, which cannot be cloned from")
    clone = tmp_path / "mutated"
    done = subprocess.run(["git", "clone", "--shared", "--quiet", str(PROJECT), str(clone)],
                          capture_output=True, text=True, check=False)
    if done.returncode != 0:
        pytest.fail(f"could not build the mutation tree: {done.stderr.strip()[-300:]}")

    feed = clone / "site" / "data" / "simplified.json"
    published = json.loads(feed.read_text())
    lane = published["lanes"][0]["atoms"][0]
    lane["atom_name"] = "Ofgem SLC 27B +/-5pct variance"
    feed.write_text(json.dumps(published, indent=2))
    env = {"PATH": "/usr/bin:/bin", "HOME": str(tmp_path),
           "GIT_AUTHOR_NAME": "mutation", "GIT_AUTHOR_EMAIL": "mutation@invalid",
           "GIT_COMMITTER_NAME": "mutation", "GIT_COMMITTER_EMAIL": "mutation@invalid"}
    subprocess.run(["git", "-C", str(clone), "commit", "-q", "-am", "replay the hand-edit"],
                   check=True, env=env, capture_output=True)

    rows = check(["generate_simplified_data"], root=clone)
    verdicts = {r["feed"]: r["verdict"] for r in rows}
    assert verdicts.get("simplified.json") == "DIVERGES", (
        f"the replayed 2026-09-03 hand-edit was not caught end to end: {rows}"
    )


def test_the_scratch_tree_is_not_built_where_there_is_no_room_for_it(tmp_path, monkeypatch):
    """THE DEFECT THIS EXISTS FOR, 2026-09-19: this control cloned into `/tmp`, which on this
    machine is a 12 GB **tmpfs**. One afternoon's runs left ~5.6 GB of abandoned checkouts in RAM,
    took it to 94%, and the next `git clone` could not write a working tree. The gate then reported
    a feed-comparison refusal, so the reader was sent to the published feeds while the machine was
    out of memory — and the merge to origin was blocked by it for hours.

    Two things have to hold and they are separate. The root must be somewhere with measured room,
    and when there is none the refusal must name the DISK. A refusal that merely said "could not
    clone" would satisfy the first and still cost the next reader their turn, which is what it did.
    """
    roomy = scratch_root()
    assert roomy.is_dir()
    assert _free_mb(roomy) >= _SCRATCH_NEEDS_MB, (
        f"the chosen scratch root {roomy} has less room than a run needs, so the check builds "
        "trees where they cannot fit"
    )

    cramped = tmp_path / "cramped"
    cramped.mkdir()
    monkeypatch.setenv("SE_FEED_CHECK_SCRATCH", str(cramped))
    monkeypatch.setattr(
        "tools.published_feed_regeneration_check._free_mb", lambda path: 10)
    with pytest.raises(RegenerationCheckRefused) as refusal:
        scratch_root()
    said = str(refusal.value)
    assert "THE DISK, NOT THE FEEDS" in said and "10 MB" in said, (
        f"a refusal caused by space did not name the space, so it reads as a statement about the "
        f"published feeds: {said}"
    )


def test_a_failed_checkout_for_want_of_space_names_the_space():
    """The other half of the same defect: git reports a full disk as `unable to write file <path>`
    and says nothing about space. Wrapped unchanged in a `RegenerationCheckRefused` that is only
    ever raised about feeds, it misattributes itself. Keyed to what git actually printed on
    2026-09-19, and the ordinary failure must NOT claim the disk or the next real clone error is
    misattributed the other way."""
    full = _why_the_clone_failed(
        "error: unable to write file tools/write_time_gate.py\n"
        "fatal: unable to checkout working tree\n"
        "warning: Clone succeeded, but checkout failed.\n", pathlib.Path("/var/tmp"))
    assert full.startswith("THE DISK, NOT THE FEEDS")
    assert "MB free" in full

    ordinary = _why_the_clone_failed("fatal: repository 'x' does not exist\n",
                                     pathlib.Path("/var/tmp"))
    assert "THE DISK, NOT THE FEEDS" not in ordinary, (
        "every clone failure was blamed on the disk, so naming the disk carries no information"
    )


def test_a_feed_naming_many_commits_or_none_yields_no_standpoint():
    """THE DEFECT THIS CATCHES: picking a standpoint out of a feed's SUBJECT MATTER.

    `value_arms.json` records fifteen commits of this repository — which tree each floor leg ran on,
    which commit a bias was measured against, which commit a pre-registration was written at. Every
    one is content. An observer that took "the newest ancestor" or "the first one found" would grade
    the feed against a commit chosen arbitrarily out of what it is ABOUT, and would do it silently.
    `phases.json` is the other direction: it records a commit COUNT and no sha, so it has not said.

    Both must return no standpoint WITH a reason, and the two reasons must differ — a single "cannot
    tell" covering both would hide that one of them is one reserved key away from being answerable.
    """
    many = {"legs": [{"ran_on": "HEAD~1"}, {"ran_on": "HEAD~2"}], "published_from": "HEAD~3"}
    resolved = [
        subprocess.run(["git", "-C", str(PROJECT), "rev-parse", ref],
                       capture_output=True, text=True, check=False).stdout.strip()
        for ref in ("HEAD~1", "HEAD~2", "HEAD~3")
    ]
    if not all(resolved):
        pytest.skip("no HEAD~3 here — this checkout has no history to name")
    many = {"legs": [{"ran_on": resolved[0]}, {"ran_on": resolved[1]}],
            "published_from": resolved[2]}

    sha, ambiguous = recorded_publication_commit(many)
    assert sha is None, f"a feed naming three commits was given a standpoint anyway: {sha}"
    assert "more than one" in ambiguous

    sha, silent = recorded_publication_commit({"total_commits": 10706, "commits_by_day": []})
    assert sha is None
    assert "no commit" in silent
    assert ambiguous != silent, (
        "naming fifteen commits and naming none returned the same reason, so a feed that is one "
        "reserved key away from being checkable reads exactly like one that is not"
    )

    one = {"git_commit": resolved[0], "note": "deadbeef is not a commit here"}
    assert recorded_publication_commit(one)[0] == resolved[0], (
        "a feed naming exactly one commit got no standpoint, so the observer can never say yes "
        "and every refusal above is vacuous"
    )


def test_a_candidate_standpoint_is_observed_from_the_feed_not_asserted():
    """A feed→commit table written down here would be a record of where things were published on
    the day it was typed. The standpoint is re-derived from each candidate's committed bytes, so
    this asserts the PROPERTY that makes it a candidate rather than today's sha.

    WHAT THAT PROPERTY IS, CORRECTED 2026-09-23. This used to demand a resolved sha, and it reddened
    when the code got MORE honest: `d181b062d` taught both producers to publish a provenance stamp
    saying whether the commit they name describes the bytes they read, and both now answer no
    (they read `site/data/customers.json` off a dirty working tree). `recorded_publication_commit`
    correctly refuses to stand at a commit that was never going to reproduce, and this leg failed it
    for that.

    Being a candidate is about HAVING SAID, not about the answer being yes: the feed names one
    commit of this repository in the reserved place, and then either that commit describes its
    inputs — a standpoint — or the feed itself says why it does not. A feed that stops stamping, or
    stamps a sha that is not a commit here, still reds."""
    if not head_resolves(PROJECT):
        pytest.skip("no HEAD here — nothing to resolve a standpoint against")
    for feed in CANDIDATES_AT_THEIR_OWN_COMMIT:
        doc = _committed_feed_doc(feed)
        block = doc.get(provenance_stamp.STAMP_KEY)
        assert isinstance(block, dict) and block.get("commit"), (
            f"{feed} is a candidate but its committed bytes carry no "
            f"{provenance_stamp.STAMP_KEY!r} commit, so nothing observed from the feed says where "
            f"it came from: {block!r}"
        )
        sha, why = recorded_publication_commit(doc)
        if sha:
            continue
        assert _the_feeds_own_account_of_having_no_standpoint(feed), (
            f"{feed} has no standpoint and does not say why — an unexplained refusal is "
            f"indistinguishable from a dead stamp: {why}"
        )


def test_a_self_explained_refusal_is_told_apart_from_an_unexplained_one():
    """THE CONTROL OVER THE WHOLE PARTITION for the clause the two legs above lean on.

    Both of them now accept a candidate that has no standpoint PROVIDED the feed says why. That
    acceptance is only worth having if it can refuse — a discriminator that returned a reason for
    everything would make `WROTE_NOTHING`, a dead generator and an emptied filter all read as
    honest refusals, which is the fail-open those legs were written to prevent and exactly what
    accepting them naively would have reintroduced.

    So every shape a block can take is driven here rather than a leg per branch, because a
    discriminator that refused EVERYTHING would also pass a per-branch test of each refusal."""
    explains = {"inputs_are_the_committed_bytes": False, "tree_was_clean": False,
                "reason": "read off the working tree, not out of this commit: site/data/x.json"}
    assert _account_in(explains) == explains["reason"]

    # Each of these is a DIFFERENT way of not having said, and every one must read as silence.
    assert _account_in({**explains, "inputs_are_the_committed_bytes": True,
                        "tree_was_clean": True}) is None, (
        "a stamp claiming its commit DOES describe its inputs is contradicting an absent "
        "standpoint, not explaining one"
    )
    assert _account_in({**explains, "reason": ""}) is None
    assert _account_in({**explains, "reason": "   "}) is None
    assert _account_in({k: v for k, v in explains.items() if k != "reason"}) is None
    assert _account_in({**explains, "reason": None}) is None
    assert _account_in(None) is None
    assert _account_in("the tree was dirty") is None, "a bare string is not a provenance block"


def test_a_feed_checkable_at_its_own_commit_is_promoted():
    """THE DEFECT THIS CATCHES: `COVERED_AT_THEIR_OWN_COMMIT` staying empty after the thing that
    keeps it empty has been repaired.

    Measured 2026-09-19, neither candidate reproduces at the commit it records, and the reason is a
    PRODUCER defect: the generator stamps `git rev-parse HEAD` and reads its inputs off the working
    tree, so the stamped commit does not describe what it read. The day a generator stamps what it
    actually read, its feed starts reproducing here and leaving it out would be a gap nobody would
    notice. So this reds on a feed that reproduces and is not promoted — the set can only grow, and
    the empty set is never itself the evidence.

    It asserts over the whole candidate set rather than a count, so a candidate quietly deleted to
    keep this green fails `test_a_candidate_standpoint_is_observed_from_the_feed_not_asserted`.
    """
    if not head_resolves(PROJECT):
        pytest.skip("no HEAD here — this is the landing checkout, which has no commit to stand at")
    rows = check_at_its_own_commit(dict(CANDIDATES_AT_THEIR_OWN_COMMIT))
    # REACHED MEANS COMPARED OR SELF-EXPLAINED, NOT MENTIONED. A row exists for every candidate
    # whatever happens — `WROTE_NOTHING`, `NO_STANDPOINT`, a generator that died — and every one of
    # those leaves `promotable` empty below. Checking only that a row came back would make this
    # green by the control's own filters emptying its evidence, which is the failure it is here to
    # prevent.
    #
    # CORRECTED 2026-09-23: demanding every candidate be GRADED reddened when the tree got more
    # honest. A feed whose provenance stamp says its commit does not describe the bytes it read has
    # answered the question — the answer is "there is no standpoint here, and here is which input
    # moved" — and no comparator can improve on that. Accepting it keeps the whole defect this
    # guards: an ungraded candidate that does NOT self-explain (a dead generator, an emptied
    # filter, a stamp that vanished) is still a red, and the account is read off the feed's own
    # bytes rather than out of the refusal's prose.
    graded = {r["feed"] for r in rows if r["verdict"] in {
        "AGREES_AT_ITS_OWN_COMMIT", "DIVERGES_AT_ITS_OWN_COMMIT", "NONDETERMINISTIC"}}
    self_explained = {
        r["feed"] for r in rows
        if r["feed"] not in graded and r["verdict"] == "NO_STANDPOINT"
        and _the_feeds_own_account_of_having_no_standpoint(r["feed"])
    }
    ungraded = {r["feed"]: (r["verdict"], r["detail"].get("reason") or r["detail"].get("stderr"))
                for r in rows if r["feed"] not in graded | self_explained}
    assert not ungraded and graded | self_explained == set(CANDIDATES_AT_THEIR_OWN_COMMIT), (
        "a candidate was neither compared against its published bytes nor able to say why not, so "
        f"the sweep below is over an empty set and says nothing: {json.dumps(ungraded, indent=1)}"
    )
    promotable = sorted({
        r["feed"] for r in rows
        if r["verdict"] == "AGREES_AT_ITS_OWN_COMMIT"
        and r["feed"] not in COVERED_AT_THEIR_OWN_COMMIT
    })
    assert not promotable, (
        f"{len(promotable)} feed(s) now reproduce at the commit they record but are not in "
        f"COVERED_AT_THEIR_OWN_COMMIT, so nothing checks them: {promotable}. Promote them."
    )


def test_the_weaker_verdict_is_never_spelled_like_the_stronger_one():
    """THE DEFECT: `AGREES_AT_ITS_OWN_COMMIT` says the bytes are what the generator produced BACK
    THERE. `AGREES` says they are what it produces NOW. A caller that switched on the verdict alone
    would read a merely-stale feed as a current one if the two shared a word, and this project's
    most expensive recurring shape is exactly that — two correct things under one name."""
    verdicts = {r["verdict"] for r in check_at_its_own_commit(
        dict(CANDIDATES_AT_THEIR_OWN_COMMIT), root=PROJECT)} if head_resolves(PROJECT) else set()
    assert "AGREES" not in verdicts and "DIVERGES" not in verdicts, (
        f"the at-its-own-commit check returned `check()`'s own words: {sorted(verdicts)}"
    )


def test_standing_at_a_commit_is_refused_where_there_is_no_history(tmp_path):
    """FAIL CLOSED. `tools/surgical_land` grades a checkout with no resolvable HEAD. There is no
    commit to stand at there, and returning "nothing diverged" would be a control going green
    because it could not find out — the exact shape this module refuses everywhere else."""
    bare = tmp_path / "nohistory"
    (bare / "site" / "data").mkdir(parents=True)
    (bare / "site" / "data" / "x.json").write_text("{}")
    with pytest.raises(RegenerationCheckRefused):
        check_at_its_own_commit({"x.json": "generate_nothing"}, root=bare)
    with pytest.raises(RegenerationCheckRefused):
        check_at_its_own_commit({})


def test_a_hand_edit_after_publication_reds_at_the_feeds_own_commit(tmp_path):
    """THE MUTATION, END TO END — the leg that proves this check can fail at all.

    The 2026-09-03 shape, replayed against the new standpoint: take a feed that DOES reproduce,
    stamp the commit it was published from into it, edit its published prose, commit both. The
    feed now names a standpoint, and at that standpoint the generator produces the un-edited text.
    A check that stood at the wrong commit, compared the output against itself, or took the
    standpoint from the caller rather than the bytes would be green here.
    """
    if not head_resolves(PROJECT):
        pytest.skip("no HEAD here — this is the landing checkout, which cannot be cloned from")
    clone = tmp_path / "stamped"
    done = subprocess.run(["git", "clone", "--shared", "--quiet", str(PROJECT), str(clone)],
                          capture_output=True, text=True, check=False)
    if done.returncode != 0:
        pytest.fail(f"could not build the mutation tree: {done.stderr.strip()[-300:]}")
    env = {"PATH": "/usr/bin:/bin", "HOME": str(tmp_path),
           "GIT_AUTHOR_NAME": "mutation", "GIT_AUTHOR_EMAIL": "mutation@invalid",
           "GIT_COMMITTER_NAME": "mutation", "GIT_COMMITTER_EMAIL": "mutation@invalid"}
    published_from = subprocess.run(["git", "-C", str(clone), "rev-parse", "HEAD"],
                                    capture_output=True, text=True, check=True).stdout.strip()

    feed = clone / "site" / "data" / "simplified.json"
    published = json.loads(feed.read_text())
    # The feed now says where it came from -- which is the whole premise of this check -- and its
    # published prose is edited downstream of the .yaml the generator copies.
    published["published_from_commit"] = published_from
    published["lanes"][0]["atoms"][0]["atom_name"] = "Ofgem SLC 27B +/-5pct variance"
    feed.write_text(json.dumps(published, indent=2))
    subprocess.run(["git", "-C", str(clone), "commit", "-q", "-am", "stamp and hand-edit"],
                   check=True, env=env, capture_output=True)

    rows = check_at_its_own_commit({"simplified.json": "generate_simplified_data"}, root=clone)
    assert rows[0]["recorded_commit"] == published_from, (
        f"the standpoint was not read off the feed: {rows}"
    )
    assert rows[0]["verdict"] == "DIVERGES_AT_ITS_OWN_COMMIT", (
        f"a hand-edit made after publication was not caught at the feed's own commit: {rows}"
    )


def test_an_unreachable_recorded_commit_is_a_refusal_not_a_pass(tmp_path):
    """THE DEFECT: a feed whose recorded sha is a lie. A hand-edited or garbage-collected commit
    must not fall through to AGREES — and it must not fall through to a silent skip either, which
    wears a pass's colour. The observer refuses it as a standpoint, and the row says so by name."""
    sha, why = recorded_publication_commit({"git_commit": "0" * 40})
    assert sha is None and "no commit" in why, (
        "a forty-character sha that names no commit of this repository was accepted as a standpoint"
    )


def test_an_uncommitted_working_copy_edit_does_not_move_the_verdict(tmp_path):
    """THE DEFECT: in this shared tree several lanes hold dirty working copies at any moment, so a
    control that graded the working copy would compare a generator against another lane's unfinished
    edit. It would also have been GREEN throughout the sixteen days the SLC-27B edit was live —
    on disk the two sides agreed, and only the committed bytes disagreed with the source.

    So the baseline is asserted behaviourally, not by reading the module's own text for the word
    "clone": a covered feed is edited in a clone's WORKING COPY and left uncommitted. If the verdict
    moves, the control is grading disk.
    """
    if not head_resolves(PROJECT):
        pytest.skip("no HEAD here — this is the landing checkout, where disk IS the graded tree")
    clone = tmp_path / "dirty"
    done = subprocess.run(["git", "clone", "--shared", "--quiet", str(PROJECT), str(clone)],
                          capture_output=True, text=True, check=False)
    if done.returncode != 0:
        pytest.fail(f"could not build the dirty tree: {done.stderr.strip()[-300:]}")

    feed = clone / "site" / "data" / "simplified.json"
    published = json.loads(feed.read_text())
    published["lanes"][0]["atoms"][0]["atom_name"] = "an uncommitted edit by another lane"
    feed.write_text(json.dumps(published, indent=2))

    rows = check(["generate_simplified_data"], root=clone)
    verdicts = {r["feed"]: r["verdict"] for r in rows}
    assert verdicts.get("simplified.json") == "AGREES", (
        "an UNCOMMITTED working-copy edit moved the verdict, so the baseline is the working copy "
        f"and not HEAD: {rows}"
    )
