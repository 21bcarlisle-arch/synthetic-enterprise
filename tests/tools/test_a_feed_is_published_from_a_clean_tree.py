"""Controls over `tools/publish_from_a_clean_tree`.

THE DEFECT THE MODULE CLOSES, and what these legs each have to be able to catch. Two published
feeds stamped `git rev-parse HEAD` beside content read off the SHARED working tree, so the commit
each named never described the bytes it read, and the whole at-its-own-commit relation —
`published_feed_regeneration_check.check_at_its_own_commit`, the only thing in this repository that
can catch a hand-edit made to a published feed AFTER publication — was switched off in production
for want of a standpoint.

The repair is at the producer: run the generator in a clean checkout of HEAD. The thing that can go
wrong with THAT is the republication of a leftover: a generator that dies, times out, or exits zero
having written nothing leaves the previous feed sitting in the clean tree, and writing those bytes
out would publish yesterday's feed under today's commit while every exit code read fine. So the
publisher's test is a property of the BYTES, and the legs below are keyed to that property rather
than to today's two feeds.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

PROJECT = pathlib.Path(__file__).resolve().parents[2]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from tools import provenance_stamp  # noqa: E402
from tools.publish_from_a_clean_tree import (  # noqa: E402
    GENERATOR_SOURCES,
    PUBLISHED_FROM_A_CLEAN_TREE,
    PublicationRefused,
    publish,
    why_it_cannot_be_published,
    why_the_run_cannot_be_published,
)
from tools.published_feed_regeneration_check import (  # noqa: E402
    CANDIDATES_AT_THEIR_OWN_COMMIT,
)

A_COMMIT = "0" * 40
ANOTHER_COMMIT = "1" * 40


def _stamped(**overrides) -> dict:
    """A feed whose provenance block vouches for `A_COMMIT`, with named fields overridden."""
    block = {"commit": A_COMMIT, "tree_was_clean": True,
             "inputs_are_the_committed_bytes": True,
             "inputs": [{"path": "site/data/customers.json", "state": "committed"}],
             "reason": "every input read here is byte-identical to what this commit holds"}
    block.update(overrides)
    return {"generated_at": "2026-09-23T00:00:00Z", provenance_stamp.STAMP_KEY: block}


def test_only_a_stamp_that_vouches_for_this_commit_may_be_published():
    """THE DEFECT: the guard accepting a feed whose stamp does not settle the question.

    Five ways it fails to settle it, and they are asserted DISTINCT rather than merely refused. A
    partition control that only counts refusals passes a guard that refuses everything for one
    reason, and this project has walked into that exact shape through three different doors: the
    caller needs to know WHICH of the five happened, because a dead generator, a dirty tree and a
    git that cannot answer are three different next actions.
    """
    assert why_it_cannot_be_published(_stamped(), A_COMMIT) is None, (
        "a stamp naming this commit and vouching for its inputs is the whole point — if this "
        "refuses, nothing is ever publishable and the relation stays empty a different way"
    )
    refusals = {
        "not an object": why_it_cannot_be_published(["a list"], A_COMMIT),
        "no stamp at all": why_it_cannot_be_published({"generated_at": "now"}, A_COMMIT),
        "someone else's commit": why_it_cannot_be_published(
            _stamped(commit=ANOTHER_COMMIT), A_COMMIT),
        "says no": why_it_cannot_be_published(
            _stamped(inputs_are_the_committed_bytes=False,
                     reason="read off the working tree: site/data/customers.json"), A_COMMIT),
        "cannot tell": why_it_cannot_be_published(
            _stamped(inputs_are_the_committed_bytes=None, commit=A_COMMIT,
                     reason="git could not be reached"), A_COMMIT),
    }
    assert all(refusals.values()), f"a shape that settles nothing was accepted: {refusals}"
    assert len(set(refusals.values())) == len(refusals), (
        "two of the five refusals came back word-for-word identical, so the row cannot tell a "
        f"reader which one happened: {json.dumps(refusals, indent=1)}"
    )


def test_a_tri_state_no_and_a_tri_state_cannot_tell_do_not_collapse():
    """THE DEFECT: `inputs_are_the_committed_bytes` is True/False/None, and the catalogued way this
    class of guard fails is a declared `None` and a silent `None` landing in the same branch — the
    flattering one. `provenance_stamp` returns None when git cannot answer, on purpose, and a
    publisher that read that as "false, near enough" would be right today and wrong the day the
    distinction mattered. Both refuse, and each says which it was."""
    says_no = why_it_cannot_be_published(
        _stamped(inputs_are_the_committed_bytes=False, reason="the tree was dirty"), A_COMMIT)
    cannot_tell = why_it_cannot_be_published(
        _stamped(inputs_are_the_committed_bytes=None, reason="git was unreachable"), A_COMMIT)
    assert says_no and cannot_tell and says_no != cannot_tell
    assert "cannot tell" in cannot_tell, cannot_tell
    assert "does not describe" in says_no, says_no


def test_a_stamp_from_another_commit_is_refused_even_though_it_vouches():
    """THE DEFECT, AND IT IS THE ONE THAT MAKES THIS A TEST OF THE BYTES AND NOT OF THE EXIT CODE.

    A generator that exits zero and writes nothing leaves the PREVIOUS publication sitting in the
    clean tree. Those bytes are a perfectly honest feed — their stamp vouches, truthfully, for the
    commit they were produced at. Publishing them would republish an old feed under today's commit
    with every status check green. The commit named must be the commit we stood at."""
    refused = why_it_cannot_be_published(_stamped(commit=ANOTHER_COMMIT), A_COMMIT)
    assert refused and ANOTHER_COMMIT in refused and "wrote nothing" in refused, refused


def test_a_run_that_died_after_writing_is_not_published():
    """THE DEFECT: publishing bytes from a run that FAILED, because the bytes themselves vouch.

    Established by mutation on 2026-09-23 — deleting the exit-code leg survived every other
    control, because a dead generator normally leaves the commit's own feed behind and the stamp
    leg refuses that for naming an earlier commit. This is the case where it does not:
    `generate_evidence_data` writes its JSON and then decides about the HTML page, so a run can
    die AFTER producing a feed that truthfully vouches for this very commit. Nothing downstream
    would ever know it came from a broken run."""
    honest_bytes = json.dumps(_stamped()).encode()
    assert why_the_run_cannot_be_published(honest_bytes, "", A_COMMIT) is None, (
        "the same bytes from a clean run must publish, or this leg is passing for the wrong reason"
    )
    refused = why_the_run_cannot_be_published(
        honest_bytes, "Traceback: OSError writing site/evidence/index.html", A_COMMIT)
    assert refused and "the generator failed" in refused, refused


def test_a_feed_that_exists_in_neither_the_commit_nor_the_run_is_refused_not_crashed():
    """THE DEFECT: a feed the commit does not carry, whose generator wrote nothing, reaching
    `json.loads(None)`. Also established by mutation — the branch survived because the two feeds
    covered today are both committed, so no control reached it. A first publication of a NEW feed
    whose generator fails is exactly that state, and a TypeError out of the publisher takes every
    feed after it down with it instead of leaving one row saying what happened."""
    refused = why_the_run_cannot_be_published(None, "", A_COMMIT)
    assert refused and "no such feed" in refused, refused


def test_unparseable_output_is_refused_by_its_own_name():
    """THE DEFECT: a generator writing truncated or non-JSON bytes and the publisher either
    crashing or — worse — treating an unreadable feed as one with no provenance block, which reads
    in the row as a generator that simply does not stamp yet."""
    refused = why_the_run_cannot_be_published(b"{not json", "", A_COMMIT)
    assert refused and "does not parse" in refused, refused


def test_every_generator_named_has_a_source_that_exists():
    """THE DEFECT, AND THE GATE CAUGHT IT ON THIS COMMIT'S FIRST LANDING ATTEMPT. These generators
    are run as `python -m tools.<name>` inside a clean checkout — not imported — so no import graph
    reaches them, and `tools/orphan_ratchet` refused the landing with "this commit adds work that
    nothing runs" naming two modules that run every cycle. `GENERATOR_SOURCES` is the route spelled
    as a path, which is the form `capability_index` models as a caller, and it is also the
    pre-flight that names a typo'd generator before a clone is paid for.

    So the two tables have to stay together: one naming a generator the other has never heard of
    would either strand a feed or put a dead path in the register that keeps a live module alive."""
    assert set(GENERATOR_SOURCES) == set(PUBLISHED_FROM_A_CLEAN_TREE.values()), (
        "the generator table and the source table name different generators: "
        f"sources={sorted(GENERATOR_SOURCES)} published={sorted(set(PUBLISHED_FROM_A_CLEAN_TREE.values()))}"
    )
    for generator, source in GENERATOR_SOURCES.items():
        assert source == f"tools/{generator}.py", (
            f"{generator} is run as `python -m tools.{generator}` but its registered source is "
            f"{source} — the path that keeps it out of the orphan set is not the file that runs"
        )
        assert (PROJECT / source).is_file(), f"{source} is not in this tree"


def test_naming_no_feeds_is_refused_not_reported_as_a_clean_publication():
    """THE DEFECT: an empty feed set making `all(r["published"] for r in rows)` true vacuously —
    a producer's own filters emptying the evidence, which reads to every caller as everything
    having shipped."""
    with pytest.raises(PublicationRefused):
        publish({}, root=PROJECT)


def test_a_feed_is_published_the_way_it_is_checked():
    """THE DEFECT: the two halves of this repair covering different feeds. A feed produced from the
    clean tree but absent from `CANDIDATES_AT_THEIR_OWN_COMMIT` is never checked against the commit
    it can now name; a candidate still produced from the dirty tree can never be checked at all.
    Either way the repair looks done from one side and is not, which is how the original defect
    survived three controls."""
    assert PUBLISHED_FROM_A_CLEAN_TREE == dict(CANDIDATES_AT_THEIR_OWN_COMMIT), (
        "the set published at a commit and the set checked at its own commit have diverged: "
        f"published={sorted(PUBLISHED_FROM_A_CLEAN_TREE)} "
        f"checked={sorted(CANDIDATES_AT_THEIR_OWN_COMMIT)}"
    )


def test_the_published_bytes_vouch_for_the_commit_they_were_produced_at(tmp_path):
    """THE DEFECT: the whole module being right in its unit legs and unable to produce a single
    honest feed from the real generators against the real HEAD — which is precisely the state the
    two feeds were in for four days while three controls over them stayed green.

    Runs the REAL generators in a clean checkout of the REAL HEAD and writes into `tmp_path`, so
    the claim is measured end to end without the run touching the shared tree."""
    rows = publish(root=PROJECT, dest=tmp_path)
    refused = {r["feed"]: r["reason"] for r in rows if not r["published"]}
    assert not refused, f"a feed could not be produced honestly at HEAD: {json.dumps(refused, indent=1)}"
    for row in rows:
        written = tmp_path / "site" / "data" / row["feed"]
        stamp = json.loads(written.read_text(encoding="utf-8"))[provenance_stamp.STAMP_KEY]
        assert stamp["commit"] == row["commit"]
        assert stamp["inputs_are_the_committed_bytes"] is True, stamp["reason"]
        assert stamp["tree_was_clean"] is True, (
            "the tree the feed was produced in was not clean, so the stamp is vouching for a "
            f"standpoint that will not reproduce: {stamp['reason']}"
        )


def test_a_refused_feed_is_not_written_and_its_other_output_is_named(tmp_path):
    """THE DEFECT, TWO OF THEM, AND BOTH END TO END.

    First: a refusal must leave the destination alone. The previous feed stays live and the page
    keeps showing the last bytes that WERE honest — the fail-closed posture both generators' own
    raises already had, which a publisher writing unconditionally would have quietly removed.

    Second: a generator that produces a feed nobody named must have it REPORTED. Publishing it
    would widen this door's blast radius past what anyone asked for; dropping it silently would be
    a cap that reads as coverage. So it goes on the row.

    Arranged out of real parts rather than a stub: the door generator is asked for `evidence.json`,
    which it does not write, so the bytes left in the clean tree are the committed evidence feed —
    an honest feed stamped at an EARLIER commit, which is exactly the leftover shape."""
    sentinel = tmp_path / "site" / "data" / "evidence.json"
    sentinel.parent.mkdir(parents=True)
    sentinel.write_text('{"this": "is the feed that was already live"}\n', encoding="utf-8")
    rows = publish({"evidence.json": "generate_capabilities_door"}, root=PROJECT, dest=tmp_path)
    assert len(rows) == 1
    row = rows[0]
    assert row["published"] is False
    assert "wrote nothing" in row["reason"], row["reason"]
    assert row["also_changed"] == ["capabilities_door.json"], (
        "the generator wrote a feed nobody named and the row did not say so, so the only record "
        f"of it is that it vanished: {row}"
    )
    assert json.loads(sentinel.read_text(encoding="utf-8")) == {
        "this": "is the feed that was already live"
    }, "a refused publication overwrote the feed that was live, which is the fail-open this guards"
    assert not (tmp_path / "site" / "data" / "capabilities_door.json").exists(), (
        "an unnamed second output was written into the destination anyway"
    )
