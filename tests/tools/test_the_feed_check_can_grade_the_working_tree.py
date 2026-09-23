"""The feed-regeneration check must be able to grade the tree that can refuse a commit.

THE DEFECT THIS EXISTS FOR, measured 2026-09-23 after it had held the publisher for two days.
`tools/published_feed_regeneration_check` clones the tree AT HEAD and regenerates there — on
purpose, so it never writes the shared tree. That is the right standpoint for the question it was
built for ("were these committed bytes hand-edited downstream of their source") and it is
STRUCTURALLY unable to see the opposite defect: **a producer edited in the working tree whose
derived artefact was never re-run.** At HEAD the edit does not exist, so the producer and the
artefact agree there and the sweep comes back clean — about a tree nobody is about to commit.

THE INSTANCE. `tools/churn_belief_size_response.py` was edited in place with a new origin sentence;
`docs/observability/churn_belief_size_response.json` was never regenerated and stayed exactly at
HEAD; `site/data/value_arms.json` was then regenerated FROM that stale intermediate and carried the
old caveat under a fresh `generated_at`. The lane's own new site leg failed against the lane's own
stale output, and a red `site/**` test refuses EVERY commit in the site lane — including the
publisher's, which is nobody's commit. `episode_clean_publishes` sat at 0 and `last_clean_publish`
was frozen from 2026-09-21 19:15. **The publisher gates the working tree and the check gated HEAD:
two trees, and only one of them can refuse a commit.**

AND THE CHAIN WAS NOT WALKED AT ALL. `grep -c churn_belief` on the check was 0, because the stale
file is `docs/observability/churn_belief_size_response.json` — an INTERMEDIATE, a published feed's
input rather than a published feed. Watching only `site/data` would have seen `value_arms.json`
diverge and named `generate_value_arms_data`, which was working perfectly.

WHY THIS IS A SEPARATE FILE FROM `test_a_published_feed_matches_what_its_generator_would_produce`,
stated because the obvious place is beside those legs. Its subject is a different standpoint, not a
wider version of the same one: every leg there grades COMMITTED bytes and every leg here grades
bytes no commit carries, and the two modes give deliberately OPPOSITE answers on the same tree. The
fixtures differ for the same reason — these build a whole throwaway repository per leg, because a
working-tree defect cannot be staged inside a tree that has no working copy of its own.
"""
from __future__ import annotations

import json
import pathlib
import subprocess

import pytest

from tools.published_feed_regeneration_check import (
    _OVERLAY_FILE_CAP_BYTES,
    COVERED_DERIVED_ARTEFACTS,
    WATCHED_DERIVED_ARTEFACTS,
    RegenerationCheckRefused,
    _Tree,
    check,
    head_resolves,
    main,
)

PROJECT = pathlib.Path(__file__).resolve().parents[2]



def _producer(caveat: str) -> str:
    """A generator that writes one published feed out of one sentence it carries itself.

    Deliberately the smallest thing that can hold the defect: the feed's only content is a sentence
    in the producer, so "the producer moved and the feed did not" is the ONLY way its output can
    disagree with its committed bytes. A bigger fixture would let a green result be explained by
    something other than the property under test.

    IT STAMPS A CLOCK, and that is not decoration. `_Tree.run` reports the files a generator
    CHANGED, observed off the disk — so a generator whose output is byte-identical to what is
    already there changes nothing and is correctly reported as `WROTE_NOTHING`, which is a gap and
    not a pass. Every real feed here moves a `generated_at` on every run and `_verdict` looks
    through it. A fixture without one cannot reach AGREES at all, so the HEAD-mode half of the leg
    below would have been asserting on the wrong verdict — found by writing it that way first.
    """
    return (
        "import json, pathlib, time\n"
        f"CAVEAT = {caveat!r}\n"
        "OUT = pathlib.Path(__file__).resolve().parent.parent / 'site' / 'data' / 'x.json'\n"
        "OUT.write_text(json.dumps({'generated_at': repr(time.time()), 'caveat': CAVEAT},\n"
        "                          indent=1) + '\\n')\n"
    )


def _feed_bytes(caveat: str) -> str:
    return json.dumps({"generated_at": "published", "caveat": caveat}, indent=1) + "\n"


def _consistent_repo(root: pathlib.Path, caveat: str) -> None:
    """A committed tree where the producer and its published feed agree."""
    (root / "tools").mkdir(parents=True)
    (root / "site" / "data").mkdir(parents=True)
    (root / "tools" / "__init__.py").write_text("")
    (root / "tools" / "generate_x.py").write_text(_producer(caveat))
    (root / "site" / "data" / "x.json").write_text(_feed_bytes(caveat))
    run = lambda *a: subprocess.run(["git", "-C", str(root), *a], check=True,  # noqa: E731
                                    capture_output=True)
    run("init", "-q")
    run("config", "user.email", "fixture@invalid")
    run("config", "user.name", "fixture")
    run("add", "-A")
    subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "consistent"], check=True,
                   capture_output=True,
                   env={"PATH": "/usr/bin:/bin", "HOME": str(root),
                        "GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@invalid",
                        "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@invalid"})


def test_a_producer_edited_in_the_working_tree_with_a_stale_artefact_is_caught(tmp_path):
    """THE DEFECT THIS EXISTS FOR, and it held the publisher for two days from 2026-09-21.

    `tools/churn_belief_size_response.py` was edited in place with a new origin sentence and
    `docs/observability/churn_belief_size_response.json` was never re-run. HEAD mode cannot see
    that by construction — at HEAD the edit does not exist, so the producer and the artefact agree
    there and the sweep comes back clean about a tree nobody is about to commit. The publisher
    gates the WORKING tree; this check gated HEAD; only one of those two trees can refuse a commit.

    BOTH SIDES ARE ASSERTED AND THAT IS THE POINT. A working-tree mode that simply reds more often
    would pass a one-sided leg, and so would one that ignored the `working_tree` argument entirely
    and always graded the working tree — the existing HEAD-mode tests would still be green and this
    one would be too. The claim is that the two modes give DIFFERENT and OPPOSITE answers on the
    same tree, so the AGREES half is not a courtesy: it is what makes the DIVERGES half mean
    anything.

    Fires on: `working_tree` being dropped on the floor, the overlay copying nothing, the baseline
    still being taken from HEAD's bytes while the producer comes from the working tree (which would
    make the AGREES half red), and the second determinism tree being built without the overlay
    (which would make the divergence read as NONDETERMINISTIC).
    """
    repo = tmp_path / "repo"
    _consistent_repo(repo, "NOT ESTABLISHED -- no reading named")
    # The edit, exactly as it was made: the producer changes, the feed is not re-run.
    (repo / "tools" / "generate_x.py").write_text(_producer("NOT ESTABLISHED -- see the reading"))

    at_head = {r["feed"]: r["verdict"] for r in check(["generate_x"], root=repo)}
    assert at_head.get("x.json") == "AGREES", (
        "HEAD mode saw a working-tree-only edit, so it is not standing at HEAD and every claim "
        f"the default mode makes about committed bytes is about some other tree: {at_head}"
    )

    in_tree = {r["feed"]: r for r in check(["generate_x"], root=repo, working_tree=True)}
    assert in_tree["x.json"]["verdict"] == "DIVERGES", (
        "the producer was edited and its feed was never regenerated, and working-tree mode did not "
        f"catch it — which is the state that wedged the publisher: {in_tree}"
    )
    changed = in_tree["x.json"]["detail"]["changed"]
    assert changed and changed[0][0] == "/caveat", (
        f"the divergence was reported somewhere other than the edited sentence: {changed}"
    )


def test_the_working_tree_overlay_carries_a_deletion_and_not_only_an_edit(tmp_path):
    """THE TRAP: an overlay built out of `git status`'s STATUS LETTERS rather than out of what is
    on disk.

    A path can be reported as added (`AD` — added to the index, deleted from the tree) and not
    exist; a rename reports two paths and only one of them has bytes. An overlay that copied
    whatever git called an addition would fail on the first of those and silently keep HEAD's copy
    of the other, which is the tree it was built to stop grading. The rule is that EXISTENCE on
    disk decides, and this is the leg that can fail if it ever becomes anything else.
    """
    repo = tmp_path / "repo"
    _consistent_repo(repo, "a caveat")
    (repo / "site" / "data" / "x.json").unlink()

    rows = {r["feed"]: r["verdict"] for r in check(["generate_x"], root=repo, working_tree=True)}
    assert rows.get("x.json") == "NOT_COMMITTED", (
        "the feed was deleted in the working tree and the graded tree still had HEAD's copy, so "
        f"the overlay is reading status letters rather than the disk: {rows}"
    )


def test_a_file_the_overlay_skipped_is_reported_and_never_silent(tmp_path):
    """NO SILENT CAPS. The overlay skips a large file that is not itself a watched artefact —
    measured 2026-09-23, seventeen append-only logs are 540 MB of this tree's 600 MB of dirty
    bytes and `docs/observability/supervisor-log.md` alone is 350 MB. A cap nobody states reads as
    a sweep that covered everything, so every skip comes back as a row.

    The second half is the one that can rot: the cap must NOT apply to the population being graded.
    A 3 MB published feed left at HEAD's bytes would take the baseline from one tree and the
    regeneration from the other and report the difference as a divergence — a red keyed to a file's
    size. `site/data/simplified.json` is 3.5 MB and dirty right now, so this is not hypothetical.
    """
    repo = tmp_path / "repo"
    _consistent_repo(repo, "a caveat")
    filler = "x" * (_OVERLAY_FILE_CAP_BYTES + 1024)
    (repo / "big_log.md").write_text(filler)
    # A feed OVER the cap, edited in the working tree: the population is never skipped.
    (repo / "site" / "data" / "big.json").write_text(json.dumps({"pad": filler}) + "\n")

    rows = check(["generate_x"], root=repo, working_tree=True)
    partial = [r for r in rows if r["verdict"] == "WORKING_TREE_PARTIAL"]
    assert partial, (
        f"a file was left out of the graded tree and no row said so: {rows}"
    )
    skipped = {s["path"] for s in partial[0]["detail"]["skipped"]}
    assert "big_log.md" in skipped, f"the skipped file was not named: {partial[0]['detail']}"
    assert not any(s.startswith("site/data/") for s in skipped), (
        "a published feed was skipped for being large, so the baseline and the regeneration come "
        f"from different trees and the size of a file decides the verdict: {skipped}"
    )


def test_the_working_tree_and_a_published_standpoint_are_refused_together(tmp_path):
    """Two different trees, and answering one question under the other's name is the defect this
    whole module is built around. `check_at_its_own_commit` stands where a feed says it was
    published from; working-tree mode stands on bytes no commit carries. A caller who asked for
    both would be silently given one of them, and the verdict would be spelled the same either way.

    Refused at BOTH surfaces, because they are reachable independently: the CLI, where the two
    flags can be typed together, and `_Tree`, where a future caller could pass `at_commit` and
    `working_tree` without going through `main` at all.
    """
    with pytest.raises(SystemExit):
        main(["--working-tree", "--at-its-own-commit"])

    tmp = tmp_path / "scratch"
    tmp.mkdir()
    with pytest.raises(RegenerationCheckRefused) as refusal:
        _Tree(PROJECT, tmp, 1, at_commit="HEAD", working_tree=True)
    assert "two" in str(refusal.value).lower(), (
        f"the refusal does not say why, so it cannot be discovered to be wrong: {refusal.value}"
    )


def test_the_churn_belief_chain_is_actually_walked():
    """THE SECOND HALF OF THE 2026-09-23 REPAIR: the chain that wedged the publisher was not walked
    at all, because its derived artefact is not in `site/data`.

    `grep -c churn_belief tools/published_feed_regeneration_check.py` was 0 on 2026-09-23 and the
    check reported `WROTE_NOTHING` for its producer — a gap wearing a clean sweep's colour. The
    intermediate is what goes stale: `site/data/value_arms.json` copies its churn-belief block
    through byte for byte, so a stale `docs/observability/churn_belief_size_response.json`
    republishes as a fresh-looking feed with a moved `generated_at` and an unmoved caveat.

    Keyed to the PROPERTY — the artefact is reached and compared — not to today's verdict, which is
    DIVERGES for a reason recorded in `COVERED_DERIVED_ARTEFACTS` and asserted nowhere here.
    """
    assert "docs/observability/churn_belief_size_response.json" in WATCHED_DERIVED_ARTEFACTS
    if not head_resolves(PROJECT):
        pytest.skip("no HEAD here — this is the landing checkout, which cannot be cloned from")
    rows = check(sorted(set(WATCHED_DERIVED_ARTEFACTS.values())), separate_nondeterminism=False)
    reached = {r["path"]: r["verdict"] for r in rows if r.get("path")}
    assert set(reached) == set(WATCHED_DERIVED_ARTEFACTS), (
        "a watched derived artefact was never produced by the generator that owns it, so nothing "
        f"compared it and the sweep below is over an empty set: {rows}"
    )


def test_a_watched_derived_artefact_that_reproduces_must_be_promoted():
    """THE DEFECT THIS CATCHES: `COVERED_DERIVED_ARTEFACTS` staying empty after the thing that
    keeps it empty has been repaired.

    It is empty because the one watched artefact does not reproduce at HEAD — and mostly not for
    the working-tree edit. Regenerated in a clone on 2026-09-23 it diverges on 35 keys, and the
    weight of them is that `/knee/by_rate[*]/knee_kwh` is 20000.5 / 12000.1 / 7500.6 in the
    committed bytes and 1.0 at every probe rate now. The published "the knee is a bill at GBP
    3,000" is refuted by the tree it is published from. Putting it in the covered set today would
    red every lane for a defect in none of them.

    The day it is regenerated it starts reproducing, and leaving it uncovered then is a gap nobody
    would notice. So this reds on promotion being owed — the covered set can only grow, and the
    empty set is never itself the evidence.
    """
    if not head_resolves(PROJECT):
        pytest.skip("no HEAD here — this is the landing checkout, which cannot be cloned from")
    rows = check(sorted(set(WATCHED_DERIVED_ARTEFACTS.values())), separate_nondeterminism=False)
    promotable = sorted({
        r["path"] for r in rows
        if r["verdict"] == "AGREES" and r.get("path") in WATCHED_DERIVED_ARTEFACTS
        and r["path"] not in COVERED_DERIVED_ARTEFACTS
    })
    assert not promotable, (
        f"{len(promotable)} watched derived artefact(s) now reproduce from their commit but are "
        f"not in COVERED_DERIVED_ARTEFACTS, so nothing reds when one is hand-edited: {promotable}"
    )
