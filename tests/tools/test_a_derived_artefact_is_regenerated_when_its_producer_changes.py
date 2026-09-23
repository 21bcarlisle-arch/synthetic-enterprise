"""A derived artefact must be regenerated when the producer that writes it changes.

THE DEFECT THIS EXISTS FOR, and the two days it cost. `tools/churn_belief_size_response.py` was
edited in place on 2026-09-21 with a new origin sentence;
`docs/observability/churn_belief_size_response.json` was never re-run and stayed exactly at HEAD;
`site/data/value_arms.json` was then regenerated FROM that stale intermediate and carried the old
caveat under a fresh `generated_at`. The site lane's own new test leg failed against the lane's own
stale output, and a red `site/**` test refuses EVERY commit in the site lane — including the
publisher's, which is nobody's commit. `episode_clean_publishes` sat at 0 and `last_clean_publish`
was frozen from 2026-09-21 19:15.

WHY ITS SIBLING FILE CANNOT SEE THIS. `test_a_published_feed_matches_what_its_generator_would_
produce` stands at HEAD, which is right for the question "were these committed bytes hand-edited"
and STRUCTURALLY unable to see this one: at HEAD the producer edit does not exist, so the pair
agrees there. The publisher gates the WORKING TREE and that check gates HEAD — two trees, and only
one of them can refuse a commit.

AND WHY THE OBVIOUS FIX WAS REFUTED BEFORE IT WAS BUILT. The remedy filed as settled — "give that
module a working-tree mode and add the chain" — was measured in `be6b67b98` and would have been
GREEN for the whole outage it was meant to catch: `generate_value_arms_data` derives the sentence
with a bare `knee.get(...)` pass-through, so regenerating from any standpoint in any tree re-reads
the same stale intermediate and reproduces byte-identical output. The broken relation is one link
UPSTREAM of any pair that module compares, which is what this file controls instead.

EVERY FAILING CASE HERE IS CONSTRUCTED, NONE HARVESTED. The live instance was discharged in the
shared tree at 09:04 on 2026-09-23 — within the hour, exactly as `be6b67b98` predicted — so a leg
keyed to that pair's verdict would have been unmutatable before it was written. The one leg that
names the real pair is keyed to the PROPERTY (the pair is attributable) and never to its verdict.
"""
from __future__ import annotations

import os
import pathlib
import subprocess

import pytest

from tools.published_feed_regeneration_check import (
    DERIVED_RED_VERDICTS,
    RegenerationCheckRefused,
    check_derived_artefacts,
    derived_artefact_producers,
)

PROJECT = pathlib.Path(__file__).resolve().parents[2]


WRITER_SOURCE = '''
from pathlib import Path
PROJECT = Path(__file__).resolve().parent.parent
ARTEFACT = PROJECT / "docs" / "observability" / "{stem}.json"
def generate(out_path=None):
    dest = ARTEFACT if out_path is None else out_path
    dest.write_text("{payload}")
'''

READER_SOURCE = '''
from pathlib import Path
PROJECT = Path(__file__).resolve().parent.parent
UPSTREAM = PROJECT / "docs" / "observability" / "{stem}.json"
def read_it():
    return UPSTREAM.read_text()
'''


def _fixture_repo(root: pathlib.Path, pairs: dict[str, str]) -> pathlib.Path:
    """A git repository with one writer module and one artefact per `pairs` entry, all committed."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "tools").mkdir()
    (root / "docs" / "observability").mkdir(parents=True)
    env = {"PATH": "/usr/bin:/bin", "HOME": str(root),
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    subprocess.run(["git", "init", "-q", str(root)], check=True, env=env)
    for stem, payload in pairs.items():
        (root / "tools" / f"{stem}.py").write_text(
            WRITER_SOURCE.format(stem=stem, payload=payload))
        (root / "docs" / "observability" / f"{stem}.json").write_text(payload)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True, env=env)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "fixture"], check=True, env=env)
    return root


def _verdict_for(rows: list[dict], stem: str) -> str:
    return next(r["verdict"] for r in rows
                if r["artefact"] == f"docs/observability/{stem}.json")


def test_the_wedge_shape_reds_a_producer_edited_with_its_artefact_left_at_head(tmp_path):
    """The exact 2026-09-21 shape: producer edited in place, artefact never re-run.

    This is the defect that held the publisher for two days and that standing at HEAD is
    STRUCTURALLY unable to see — at HEAD the edit does not exist and the pair agrees.
    """
    repo = _fixture_repo(tmp_path / "wedge", {"belief": "old"})
    (repo / "tools" / "belief.py").write_text(
        WRITER_SOURCE.format(stem="belief", payload="new"))   # artefact deliberately NOT re-run
    rows = check_derived_artefacts(repo)
    assert _verdict_for(rows, "belief") == "NOT_REGENERATED_SINCE_ITS_PRODUCER_CHANGED"
    assert _verdict_for(rows, "belief") in DERIVED_RED_VERDICTS


def test_regenerating_the_artefact_clears_the_red(tmp_path):
    """The remedy the row names actually discharges it — otherwise the red is one nobody can clear.

    That failure mode is the whole reason the publisher wedge cost two days, so it is controlled
    rather than assumed.
    """
    repo = _fixture_repo(tmp_path / "cleared", {"belief": "old"})
    (repo / "tools" / "belief.py").write_text(
        WRITER_SOURCE.format(stem="belief", payload="new"))
    assert _verdict_for(check_derived_artefacts(repo), "belief") in DERIVED_RED_VERDICTS
    (repo / "docs" / "observability" / "belief.json").write_text("new")
    assert _verdict_for(check_derived_artefacts(repo), "belief") not in DERIVED_RED_VERDICTS


def test_the_relation_reaches_every_verdict_it_defines_and_they_are_distinct(tmp_path):
    """One control over the WHOLE partition, asserting DISTINCTNESS and not four separate legs.

    A per-branch leg cannot see two shapes collapsing onto one verdict, which is how a partition
    control goes quietly blind. Four shapes in, four different verdicts out.
    """
    repo = _fixture_repo(tmp_path / "partition", {
        "untouched": "v1", "notrerun": "v1", "clock": "v1", "fresh": "v1"})
    # producer edited, artefact left at HEAD
    (repo / "tools" / "notrerun.py").write_text(
        WRITER_SOURCE.format(stem="notrerun", payload="v2"))
    # both dirty, producer written LAST
    (repo / "docs" / "observability" / "clock.json").write_text("v2")
    (repo / "tools" / "clock.py").write_text(WRITER_SOURCE.format(stem="clock", payload="v2"))
    # both dirty, artefact written last — the correct order
    (repo / "tools" / "fresh.py").write_text(WRITER_SOURCE.format(stem="fresh", payload="v2"))
    (repo / "docs" / "observability" / "fresh.json").write_text("v2")
    # The two orderings are stamped EXPLICITLY rather than written in sequence and trusted. Measured
    # on this box: two writes one statement apart come back with byte-identical `st_mtime_ns`, so a
    # sequence-and-hope fixture would have tested the filesystem's clock granularity instead of the
    # leg's logic — and it would have done it by silently taking the forgiving branch.
    for rel, newer in (("tools/clock.py", True), ("docs/observability/fresh.json", True)):
        other = ("docs/observability/clock.json" if newer and "clock" in rel
                 else "tools/fresh.py")
        os.utime(repo / other, (1_000_000, 1_000_000))
        os.utime(repo / rel, (2_000_000, 2_000_000))

    rows = check_derived_artefacts(repo)
    seen = {stem: _verdict_for(rows, stem)
            for stem in ("untouched", "notrerun", "clock", "fresh")}
    assert seen["untouched"] == "PRODUCER_UNCHANGED"
    assert seen["notrerun"] == "NOT_REGENERATED_SINCE_ITS_PRODUCER_CHANGED"
    assert seen["clock"] == "PRODUCER_NEWER_BY_CLOCK"
    assert seen["fresh"] == "REGENERATED_AFTER_ITS_PRODUCER"
    assert len(set(seen.values())) == 4, f"two shapes collapsed onto one verdict: {seen}"


def test_a_module_that_only_reads_an_artefact_is_not_named_as_its_producer(tmp_path):
    """The discrimination the whole relation rests on, and the measured reason a name match fails.

    Measured 2026-09-23 across the real tree: 16 artefacts are NAMED by more than one module
    because readers name the path too — `generate_value_arms_data.py` names the churn artefact
    precisely because it consumes it. Attributing by name would have accused the reader.
    """
    repo = _fixture_repo(tmp_path / "reader", {"upstream": "v1"})
    (repo / "tools" / "consumer.py").write_text(READER_SOURCE.format(stem="upstream"))
    producers, _ = derived_artefact_producers(repo)
    assert producers["docs/observability/upstream.json"] == "tools/upstream.py"

    # ...and the reader's presence must not turn the artefact into an ambiguous gap either.
    (repo / "tools" / "upstream.py").write_text(
        WRITER_SOURCE.format(stem="upstream", payload="v2"))
    assert _verdict_for(check_derived_artefacts(repo),
                        "upstream") == "NOT_REGENERATED_SINCE_ITS_PRODUCER_CHANGED"


def test_an_artefact_no_writer_resolves_is_a_named_gap_and_never_a_row(tmp_path):
    """Silence about an artefact must be reported as silence. A control over what is regenerated
    must not go green because it could not find out — the rule the first relation states above."""
    repo = _fixture_repo(tmp_path / "gap", {"known": "v1"})
    (repo / "docs" / "observability" / "orphan.json").write_text("{}")
    producers, gaps = derived_artefact_producers(repo)
    assert "docs/observability/orphan.json" not in producers
    assert "docs/observability/orphan.json" in gaps
    assert "NO_PRODUCER_RESOLVED" in gaps["docs/observability/orphan.json"]
    assert not any(r["artefact"] == "docs/observability/orphan.json"
                   for r in check_derived_artefacts(repo))


def test_two_writers_of_one_artefact_are_a_gap_not_an_arbitrary_pick(tmp_path):
    """Picking one of two writers would attribute an edit to a module that may not have made it."""
    repo = _fixture_repo(tmp_path / "ambiguous", {"shared": "v1"})
    (repo / "tools" / "other_writer.py").write_text(
        WRITER_SOURCE.format(stem="shared", payload="v1"))
    producers, gaps = derived_artefact_producers(repo)
    assert "docs/observability/shared.json" not in producers
    assert "AMBIGUOUS_PRODUCER" in gaps["docs/observability/shared.json"]


def test_the_clock_leg_is_evidence_and_is_not_spelled_like_the_decided_one():
    """`PRODUCER_NEWER_BY_CLOCK` rests on an mtime a `git checkout` can reorder, so it may not
    refuse a commit — this control gates the publisher, and a red nobody can discharge is the
    failure it exists to end. The decided, content-based verdict is the only red."""
    assert "PRODUCER_NEWER_BY_CLOCK" not in DERIVED_RED_VERDICTS
    assert DERIVED_RED_VERDICTS == {"NOT_REGENERATED_SINCE_ITS_PRODUCER_CHANGED"}


def test_no_derived_artefact_resolving_is_refused_not_reported_clean():
    """An empty sweep is the shape that agrees with every answer."""
    with pytest.raises(RegenerationCheckRefused):
        check_derived_artefacts(PROJECT, producers={})


def test_the_chain_the_publisher_wedge_happened_on_is_attributable():
    """Keyed to the PROPERTY — that the pair resolves — and NOT to its verdict today.

    The instance was discharged at 09:04 on 2026-09-23. Pinning the verdict would red this leg the
    moment the tree became honest, which is exactly backwards.
    """
    producers, gaps = derived_artefact_producers()
    artefact = "docs/observability/churn_belief_size_response.json"
    assert producers.get(artefact) == "tools/churn_belief_size_response.py", (
        f"the pair the relation was built for is unattributable: {gaps.get(artefact)}")
