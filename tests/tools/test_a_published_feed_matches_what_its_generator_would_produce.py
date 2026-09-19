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

THE COVERED SET IS NOT ALLOWED TO BE TODAY'S ANSWER. A list of eight feeds pinned to what passed on
the day it was written is exactly the shape this project has been burned by — it goes green when the
claim rots. Two legs stop that here. `test_a_feed_that_became_checkable_must_be_promoted` sweeps
every cheap generator and reds if ANY feed outside the covered set now reproduces, so the set can
only ever grow and the exclusion can never be silently kept. And
`test_the_instrument_can_return_all_three_verdicts` asserts over the whole partition, because an
instrument that answered AGREES to everything would pass every other test in this file.

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

from tools.published_feed_regeneration_check import (
    COVERED_FEEDS,
    RegenerationCheckRefused,
    _verdict,
    check,
    covered_generators,
    head_resolves,
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


@pytest.fixture(scope="module")
def covered_rows():
    return check(covered_generators())


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


def test_the_feed_the_defect_happened_on_is_covered():
    """A covered set that shrank to the feeds nobody edits would pass every test here. The feed the
    SLC-27B edit was actually made on is the one that must be in it."""
    assert "simplified.json" in COVERED
    assert len(COVERED) >= 8, "the covered set has shrunk — a set that can only shrink is not a control"


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

    It asks for AGREES only, which the first tree settles on its own, so the determinism tree is
    switched off here: it would double the sweep to tell apart two verdicts this leg treats alike.
    """
    cheap = sorted(
        p.stem for p in (PROJECT / "tools").glob("generate_*.py")
        if p.stem not in TOO_SLOW_TO_SWEEP
    )
    rows = check(cheap, separate_nondeterminism=False)
    promotable = sorted({
        r["feed"] for r in rows
        if r["feed"] and r["verdict"] == "AGREES" and r["feed"] not in COVERED
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
