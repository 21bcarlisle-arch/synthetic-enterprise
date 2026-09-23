#!/usr/bin/env python3
"""Produce a feed AT A COMMIT, so the commit it stamps is the one whose bytes it read.

THE DEFECT THIS CLOSES, measured 2026-09-19 and re-stated 2026-09-23 in
`docs/staging/records/SEAT_RESULT_A_DISPLACED_CLOCK_SEPARATES_THE_FEEDS_THAT_ARE_A_FUNCTION_OF_THEIR_COMMIT_2026-09-23.md`.

`generate_evidence_data` and `generate_capabilities_door` ran in the SHARED working tree, where
several lanes hold dirty copies at any moment, and stamped `git rev-parse HEAD` beside content read
off disk. The commit they named therefore never described the bytes they read. Since d181b062d the
stamp says so rather than lying about it — `read off the working tree, not out of this commit:
docs/observability/test_execution_log.jsonl` — and since 6b4bfdd15 the two controls over it
correctly ACCEPT that self-explained refusal. So the relation was honest and EMPTY:
`published_feed_regeneration_check.COVERED_AT_THEIR_OWN_COMMIT` could never gain a member, and
`check_at_its_own_commit` — the only thing in this repository that can catch a hand-edit made to a
published feed AFTER publication — was switched off in production for want of a standpoint.

**No comparator can repair that, because the defect is at the producer.** There is no commit to
stand at that describes inputs which were never a commit. So the producer moves: the generator runs
in a clean checkout of HEAD, where every input it reads IS that commit's bytes, and the stamp it
makes is true by construction rather than by hope.

WHAT IT COSTS, SAID ON THE SURFACE RATHER THAN IN A FOOTNOTE. A feed that is a function of its
commit is necessarily a feed about COMMITTED state. `capabilities_door.json` reads
`site/data/evidence.json`, `customers.json` and `dashboard.json`, all of which the same publish
cycle regenerates; produced here it reads the copies HEAD holds, so it is one publish cycle
(~30 minutes) behind them rather than current with them. That is the whole trade: the door's
figures lag by a cycle, and in exchange the feed can be checked against the commit it names. The
alternative — reading this cycle's uncommitted siblings — is what made the stamp false, and it is
not an option that also reproduces.

FAIL-CLOSED, AND NOT ON THE EXIT CODE. A generator that dies, times out, or exits zero having
written nothing leaves the PREVIOUS feed in the clean tree, and publishing those bytes would
republish yesterday's feed as today's. So the test is not "did it exit zero" but **does the
produced feed's own provenance stamp name THIS commit and vouch that the commit describes what it
read** — a property of the bytes about to be published, which a leftover feed cannot satisfy
because its stamp names the commit it was produced at, and that is never the one we are standing
at now. The exit code is checked too, and names its own refusal; neither leg is the only one.

Nothing is written into the shared tree unless that test passes, so a refused feed leaves the live
page showing the last feed that WAS honest, and the row says why.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from tools import provenance_stamp  # noqa: E402
from tools.published_feed_regeneration_check import (  # noqa: E402
    DEFAULT_TIMEOUT_S,
    FEED_DIR,
    clean_tree_at,
    scratch_root,
)

#: The feeds the publish path produces this way, and the generator behind each. This is the SAME
#: pairing as `published_feed_regeneration_check.CANDIDATES_AT_THEIR_OWN_COMMIT` and it is asserted
#: to be, by `test_a_feed_is_published_the_way_it_is_checked` — a feed produced here but not
#: checked there, or checked there but produced from the dirty tree, is the two halves of this
#: repair disagreeing about which feeds it covers, which is exactly how the original defect
#: survived three controls.
PUBLISHED_FROM_A_CLEAN_TREE = {
    "capabilities_door.json": "generate_capabilities_door",
    "evidence.json": "generate_evidence_data",
}

#: The SOURCE each of those generators is, spelled as a repo-relative path. Two jobs, and neither
#: is decoration.
#:
#: 1. IT IS THE ROUTE, IN THE ONLY FORM ANYTHING CAN SEE. These generators now run as
#:    `python -m tools.<name>` inside the clean checkout, which is not an import, so no import
#:    graph reaches them. `tools/orphan_ratchet` correctly called both of them orphans the moment
#:    the publish path stopped importing them — "this commit adds work that nothing runs", for two
#:    modules that run every cycle. `capability_index` models a subprocess route as a path string
#:    in code (a `(by path)` caller), so this table is what keeps a live mechanism from reading as
#:    dead work. Freezing them into the ratchet floor instead would have been a lie with a
#:    signature on it.
#: 2. IT IS THE PRE-FLIGHT. A typo'd generator name otherwise costs a clone and comes back as
#:    "the generator failed", which names the wrong thing entirely.
#:
#: `test_every_generator_named_has_a_source_that_exists` holds the two tables together, so the
#: pair cannot drift into one naming a generator the other has never heard of.
GENERATOR_SOURCES = {
    "generate_capabilities_door": "tools/generate_capabilities_door.py",
    "generate_evidence_data": "tools/generate_evidence_data.py",
}


class PublicationRefused(RuntimeError):
    """The publication could not honestly be attempted at all. Never a silently empty sweep."""


def why_it_cannot_be_published(doc, commit: str) -> str | None:
    """The reason these bytes must not be published as a feed produced at `commit`, or None.

    THE FOUR REFUSALS ARE SPELLED SEPARATELY ON PURPOSE. `inputs_are_the_committed_bytes` is
    tri-state — True, False and the honest `None` that `provenance_stamp` returns when git cannot
    say — and the catalogued way this class of guard fails is a declared `None` and a silent `None`
    collapsing into the flattering branch. A missing stamp, a stamp naming someone else's commit, a
    stamp that says no, and a stamp that cannot tell are four different things that happened for
    four different reasons, and a caller reading the row needs to know which.

    `commit` is what the caller stood at. A stamp naming a DIFFERENT commit is the leftover-feed
    case: the generator wrote nothing and the bytes still in the tree are the previous publication,
    whose stamp names the commit IT was produced at. That is what makes this a fail-closed test of
    the bytes rather than a second reading of the exit code.
    """
    if not isinstance(doc, dict):
        return "the generator's output is not a JSON object, so it carries no provenance block"
    stamp = doc.get(provenance_stamp.STAMP_KEY)
    if not isinstance(stamp, dict):
        return (f"no `{provenance_stamp.STAMP_KEY}` block: this generator does not record what it "
                "read, so publishing it would put back the stamp-that-describes-nothing this "
                "module exists to end")
    named = stamp.get("commit")
    if named != commit:
        return (f"the stamp names commit {named!r}, not the {commit[:9]!r} it was produced at — "
                "these are the bytes that were already there, so the generator wrote nothing")
    vouched = stamp.get("inputs_are_the_committed_bytes")
    reason = stamp.get("reason") or "the stamp gave no reason"
    if vouched is None:
        return f"the stamp cannot tell whether the commit describes its inputs: {reason}"
    if vouched is not True:
        return f"the commit does not describe what was read: {reason}"
    return None


def why_the_run_cannot_be_published(produced: bytes | None, err: str, commit: str) -> str | None:
    """The reason this RUN's output must not be published, or None. Every refusal in one place.

    WHY THE EXIT CODE IS ASKED FIRST AND IS NOT REDUNDANT, established by mutation 2026-09-23 and
    recorded here rather than left to the reader. Deleting the `err` leg survived every control,
    because a generator that dies usually leaves the commit's own feed behind and the stamp leg
    refuses THAT for naming an earlier commit. It is not an equivalence: a generator that writes
    its feed and then dies on a later step — `generate_evidence_data` writes the JSON and then
    decides about the HTML page — leaves bytes that DO vouch for this commit, from a run that
    failed. Asking the exit code first is what stops a half-finished run being published, and
    `test_a_run_that_died_after_writing_is_not_published` is the leg that now holds it.

    The `produced is None` leg survived for its own reason and is its own missing test: a feed the
    commit does not carry, whose generator wrote nothing, reaches `json.loads(None)` without it.
    """
    if err:
        return (f"the generator failed and nothing was published: {err}")
    if produced is None:
        return ("the generator wrote no such feed in the clean tree and the commit does not carry "
                "one either, so there are no bytes to publish")
    try:
        doc = json.loads(produced)
    except (ValueError, UnicodeDecodeError) as exc:
        return f"the generator's output does not parse: {str(exc)[:200]}"
    return why_it_cannot_be_published(doc, commit)


def _write_atomically(target: Path, payload: bytes) -> None:
    """Replace `target` in one step. The site lane reads these feeds while we write them, and a
    torn 126KB JSON read by the door harness is a red in a lane that changed nothing."""
    target.parent.mkdir(parents=True, exist_ok=True)
    handle, staging = tempfile.mkstemp(prefix=f".{target.name}.", dir=str(target.parent))
    try:
        with os.fdopen(handle, "wb") as out:
            out.write(payload)
        # `mkstemp` opens 0600. Every other feed in this directory is world-readable and the site
        # lane's readers are not all this process, so the replacement keeps the neighbours' mode
        # rather than quietly narrowing it.
        os.chmod(staging, 0o644)
        os.replace(staging, target)
    except BaseException:
        Path(staging).unlink(missing_ok=True)
        raise


def publish(feeds: dict[str, str] | None = None, root: Path = PROJECT,
            dest: Path | None = None, timeout_s: int = DEFAULT_TIMEOUT_S) -> list[dict]:
    """Produce each feed in a clean checkout of `root`'s HEAD and write the ones that vouch.

    Returns a row per feed — `published`, the commit stood at, the reason if refused, and any OTHER
    feed the generator changed in the clean tree. `also_changed` is reported rather than published:
    a second output would be a feed nobody named, and quietly writing it into the shared tree is a
    wider blast radius than this door is allowed. Quietly DROPPING it would be a silent cap, so it
    is on the row and the publish path logs it.

    `dest` defaults to `root`; separating them is what lets a control drive the real generators
    against the real HEAD without the run touching the shared tree.
    """
    feeds = dict(PUBLISHED_FROM_A_CLEAN_TREE if feeds is None else feeds)
    if not feeds:
        raise PublicationRefused(
            "no feeds named — refusing to report a clean publication over an empty set, which is "
            "how a producer's own filters make it look like everything shipped"
        )
    commit = provenance_stamp.head_commit(root)
    if commit is None:
        raise PublicationRefused(
            "this checkout has no resolvable HEAD, so there is no commit to produce a feed AT — "
            "and producing one anyway is the defect this module was written to close"
        )
    destination = Path(root if dest is None else dest)
    rows: list[dict] = []
    tmp = Path(tempfile.mkdtemp(prefix="publish-clean-", dir=scratch_root()))
    try:
        tree = clean_tree_at(commit, tmp, root)
        for name in sorted(feeds):
            generator = feeds[name]
            row = {"feed": name, "generator": generator, "commit": commit,
                   "published": False, "reason": "", "also_changed": []}
            source = GENERATOR_SOURCES.get(generator)
            if source is None or not (root / source).is_file():
                # Named before the clone is paid for, and named as the table's defect rather than
                # as the generator's: "the generator failed" would send a reader to a module that
                # may not even exist.
                row["reason"] = (f"no source for {generator!r} in GENERATOR_SOURCES, or "
                                 f"{source!r} is not a file in this tree — the table names a "
                                 "generator this tree does not have")
                rows.append(row)
                continue
            # `run` restores the feed directory to the commit's bytes first, so each generator
            # reads the COMMITTED siblings and never a sibling this same loop just produced.
            changed, err = tree.run(generator, timeout_s)
            row["also_changed"] = sorted(set(changed) - {name})
            produced = tree.feeds().get(name)
            why = why_the_run_cannot_be_published(produced, err, commit)
            if why:
                row["reason"] = why
            else:
                _write_atomically(destination / FEED_DIR / name, produced)
                row["published"] = True
                row["reason"] = (f"produced at {commit[:9]}, and its own stamp says that commit "
                                 "holds every input it read")
            rows.append(row)
        return rows
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--feed", action="append", default=None,
                        help="publish only this feed (repeatable); default is all of them")
    parser.add_argument("--dest", default=None,
                        help="write into this tree instead of the repository")
    parser.add_argument("--json", action="store_true", help="print the rows as JSON")
    args = parser.parse_args(argv)
    wanted = (PUBLISHED_FROM_A_CLEAN_TREE if args.feed is None
              else {f: PUBLISHED_FROM_A_CLEAN_TREE[f] for f in args.feed
                    if f in PUBLISHED_FROM_A_CLEAN_TREE})
    try:
        rows = publish(wanted, dest=Path(args.dest) if args.dest else None)
    except (PublicationRefused, KeyError) as exc:
        print(f"PUBLICATION REFUSED (nothing written): {exc}")
        return 1
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        for row in rows:
            mark = "published" if row["published"] else "REFUSED  "
            print(f"{mark} {row['feed']} <- {row['generator']}: {row['reason']}")
            if row["also_changed"]:
                print(f"          also changed but NOT published: {row['also_changed']}")
    return 0 if all(r["published"] for r in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
