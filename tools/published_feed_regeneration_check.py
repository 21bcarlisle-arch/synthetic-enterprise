#!/usr/bin/env python3
"""Does a published `site/data/*.json` still match what its generator would produce?

THE DEFECT THIS EXISTS FOR, found by accident on 2026-09-19 and repaired as ONE INSTANCE in
`1d5642c35`. A false regulatory citation — `Ofgem SLC 27B`, a regulation that does not exist — was
corrected by hand in `site/data/simplified.json` and `site/data/dashboard.json` on 2026-09-03, and
never in `docs/design/simplifications/DD_seasonal_cashflow_physics.yaml`, which
`tools/generate_simplified_data` copies BYTE-IDENTICALLY. The correction was right; the source it
came from was not touched. It survived sixteen days purely as hand-edited committed bytes, and the
first regeneration reverted it — which is how anyone found out.

Nothing in this repository compared a published feed against what its generator would produce, so
that edit was correct on disk, reverted at the next run, and unobservable in between. This module is
that comparison.

HOW IT AVOIDS THE TRAP IT IS MADE OF. The obvious implementation — point a generator's `OUT_PATH` at
a temp file — fails two ways this project has already paid for: most generators compute
`PROJECT = Path(__file__).resolve().parent.parent` and take no output argument at all, and the ones
that do have a trailing `print(path.relative_to(PROJECT))` that raises AFTER a correct write. So no
path is redirected here. Instead the whole tree is CLONED at HEAD (`git clone --shared`, ~1s, no
object copy) and the generator is run with `cwd` inside the clone, where its own `__file__` makes
every relative path resolve to the clone. The shared tree is never written.

WHY A CLONE AND NOT `git archive`. Measured, not assumed: in a `git archive | tar -x` extract there
is no `.git`, and five generators fail there for that reason alone — `not a git repository` — which
is this project's catalogued "a red from an extract is artefact locality" trap. A `--shared` clone
carries the full history for ~1s and none of those five fail. The extract was tried first and
discarded on the measurement.

THE THREE-WAY VERDICT, AND WHY IT IS NOT A HAND-MAINTAINED ALLOWLIST. Regenerating everything and
demanding equality does not work: measured across all 61 feeds on 2026-09-19, 24 of the 31 that run
diverge, and almost none of them from a hand-edit. They diverge because the feed is a function of
things that are not in the commit — the live git log, the live staging directory, a gitignored
Elexon cache, a run artefact. A control that reds on those is red on the day it lands and muted by
the end of the week.

So the membership rule is MEASURED on every run rather than listed:

  NONDETERMINISTIC  two clones of the SAME commit produce two different files, so the feed is not a
                    function of the commit and no comparison against committed bytes means anything.
                    Reported as a named gap — never as a pass, and never as a red.
  DIVERGES          the generator IS deterministic at this commit and its output is not the
                    committed bytes. This is the SLC-27B shape. RED.
  AGREES            deterministic, and the committed bytes are what it produces.

The second clone is only built when the first disagrees, so the green path costs one clone.

WHICH FEED A GENERATOR OWNS IS OBSERVED, NEVER DECLARED. The generator is run and the files it
actually changed are read off the disk. A feed→generator table written down here would go stale the
first time a generator learned to write a second feed, and it would go stale silently.

THE SECOND QUESTION: DOES IT REPRODUCE AT THE COMMIT IT SAYS IT WAS PUBLISHED FROM? Standing at
HEAD leaves 23 of the 31 runnable feeds uncheckable, and for most of them that is not a defect —
the feed was published earlier and its inputs (the git log, another committed feed) have moved since.
`check_at_its_own_commit` stands instead at the commit the feed ITSELF records, observed from its
bytes by `recorded_publication_commit` and never passed in. It answers a strictly WEAKER question
than `check()` — "are the published bytes what the generator produced back there", which catches a
hand-edit made after publication and is silent about staleness — so its verdicts are spelled
differently (`AGREES_AT_ITS_OWN_COMMIT`) and cannot be read as the stronger ones by a caller
glancing at a verdict.

AND WHAT THAT MEASUREMENT FOUND, WHICH IS WHY IT PROMOTES NOTHING TODAY. A feed's git stamp is not a
description of what produced it. `generate_capabilities_door` stamps `git rev-parse HEAD` and then
reads `site/data/customers.json` off the WORKING TREE, where several lanes hold dirty copies at any
moment. Standing at the stamped commit brings `git_commit` right and leaves `as_of` wrong, because
the published feed read a `customers.json` newer than that commit ever committed. There is no
commit to stand at that describes those inputs, because the inputs were never a commit. That is a
producer defect, it is recorded in `PROVENANCE_IS_NOT_THE_INPUT_DESCRIPTION`, and no comparator can
repair it — which is the finding, not a gap in this module.

READ AS COMMITTED, NEVER AS EDITED — with one named exception. The baseline is `HEAD`'s bytes, not
the working tree's: in this shared tree several lanes hold dirty copies at any moment, and a
working-tree read would compare a generator against another lane's unfinished edit. The exception is
a checkout with no resolvable HEAD, which is what `tools/surgical_land` builds to grade the tree a
commit WOULD create (`git archive | tar -x` then a fresh `git init`). There the files on disk ARE
the tree being graded, so they are the baseline — the same property reached by a different route,
exactly as `tests/tools/test_a_published_surface_is_reproducible_from_its_committed_input` handles
it. Any OTHER git failure is a refusal, not a fallback: a control over what is committed must not go
green because it could not find out.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
FEED_DIR = "site/data"

#: Per-generator ceiling. The slowest real generator measured 2026-09-19 is
#: `generate_provisional_plan_data` at 251s (`git log --reverse --follow` over the whole history).
DEFAULT_TIMEOUT_S = 300

#: The feeds that ARE a function of their commit, and the generator that writes each. Membership is
#: a PROPERTY — "regenerating this at its own commit reproduces the committed bytes" — measured
#: 2026-09-19 across all 61 published feeds, and re-derived on every run by
#: `tests/tools/test_a_published_feed_matches_what_its_generator_would_produce`'s promotion leg,
#: which reds if any feed OUTSIDE this table now reproduces. So the set can only grow, and it cannot
#: quietly become a record of what happened to pass on the day it was written.
#:
#: ONE HOME, because there are two readers: the commit-time control, and the publish path in
#: `background/process_run_complete`, which uses it to name what a regeneration is about to revert.
#: A second copy would drift, and the drift would be invisible in exactly the way this module exists
#: to prevent. The whole set grades in ~7s.
COVERED_FEEDS = {
    "company.json": "generate_company_data",
    "explore_hh_days.json": "generate_explore_hh_day",
    "fidelity.json": "generate_fidelity_data",
    "knowledge_review.json": "generate_knowledge_review",
    "premise_demand.json": "generate_premise_demand_data",
    "regulatory.json": "generate_regulatory_data",
    "simplified.json": "generate_simplified_data",
    "world.json": "generate_world_data",
}


#: The feeds asked the SECOND question below — "does this reproduce at the commit it says it was
#: published from?" — and the generator that writes each. A CANDIDATE list, not a covered set:
#: membership here says only that the feed records exactly one commit, which is a property of its
#: bytes, re-derived by `recorded_publication_commit` on every run. What it REPRODUCES is measured.
#:
#: Measured 2026-09-19: neither of these reproduces at its own recorded commit, and the reason is
#: recorded beside it rather than as the word "no". Both reasons are that the stamp does not
#: describe the bytes the generator read — see `PROVENANCE_IS_NOT_THE_INPUT_DESCRIPTION` below.
CANDIDATES_AT_THEIR_OWN_COMMIT = {
    "capabilities_door.json": "generate_capabilities_door",
    "evidence.json": "generate_evidence_data",
}

#: Promoted out of the candidates above: reproduces at its own recorded commit, so a hand-edit to
#: the published bytes reds. EMPTY IS THE MEASURED ANSWER, NOT AN UNFINISHED LIST — and it is why
#: the empty set is never swept as evidence: `test_a_feed_checkable_at_its_own_commit_is_promoted`
#: asserts over the CANDIDATES and reds when one starts reproducing, so nothing here is graded by
#: an empty set agreeing with everything.
COVERED_AT_THEIR_OWN_COMMIT: dict[str, str] = {}

#: WHY A FEED'S GIT STAMP IS NOT A DESCRIPTION OF WHAT PRODUCED IT — measured 2026-09-19, and the
#: reason the "stand at the commit it records" route promotes nothing today.
#:
#: `generate_capabilities_door` stamps `git rev-parse HEAD` and reads `site/data/customers.json`
#: from the WORKING TREE. In this shared tree several lanes hold dirty copies at any moment, so the
#: two describe different states. Measured: `capabilities_door.json` records `be7311e35`, and
#: regenerated in a clone standing AT `be7311e35` its `git_commit` comes right and
#: `/scale/figures[0]/as_of` does not — the published feed read a `customers.json` NEWER than the
#: one `be7311e35` committed. The stamp names a commit whose bytes the generator never read.
#:
#: That is a producer defect and no comparator or standpoint can repair it: there is no commit to
#: stand at that describes the inputs, because the inputs were never a commit.
PROVENANCE_IS_NOT_THE_INPUT_DESCRIPTION = (
    "a feed that stamps `git rev-parse HEAD` beside content read from the working tree records a "
    "commit that does not describe its inputs, so standing at that commit cannot reproduce it"
)


def covered_generators() -> list[str]:
    """The generators behind `COVERED_FEEDS`, deduplicated and ordered."""
    return sorted(set(COVERED_FEEDS.values()))


def _is_ancestor_commit(root: Path, sha: str) -> bool:
    """Is `sha` a commit of THIS repository, reachable from HEAD?

    Both halves matter. A value that resolves to a blob or a tag is not a standpoint, and a commit
    that is not an ancestor of HEAD is not somewhere this tree was ever published from — it is a
    commit named as CONTENT (which arm ran on which tree), and treating it as provenance would pick
    a standpoint at random out of a feed's subject matter.
    """
    if _git(root, "cat-file", "-t", sha).stdout.strip() != "commit":
        return False
    return _git(root, "merge-base", "--is-ancestor", sha, "HEAD").returncode == 0


def _scalars(doc):
    """Every leaf of a decoded feed, in no particular order."""
    if isinstance(doc, dict):
        for value in doc.values():
            yield from _scalars(value)
    elif isinstance(doc, list):
        for value in doc:
            yield from _scalars(value)
    else:
        yield doc


def recorded_publication_commit(doc, root: Path = PROJECT) -> tuple[str | None, str]:
    """The one commit a feed records about its own publication — OBSERVED, never declared.

    Returns `(sha, reason)`; `sha` is None whenever the feed does not settle the question, and the
    reason is always named.

    WHY EXACTLY ONE, AND WHY THAT IS THE WHOLE RULE. A feed that names a single commit of this
    repository is saying where it was published from. A feed that names fifteen is not: measured
    2026-09-19, `value_arms.json` carries fifteen — which tree each floor leg ran on, which commit a
    bias was measured against, which commit the pre-registration was written at. Those are its
    SUBJECT, and picking one of them as a standpoint would be choosing arbitrarily among content.
    A feed that names none — `phases.json` records a commit COUNT and no sha — has not said.

    So the rule refuses in both directions rather than guessing, and it needs no per-feed table: the
    day `value_arms.json` stamps its publishing commit in one reserved place and stops scattering
    the rest, it becomes answerable here with nobody editing a list.
    """
    seen: list[str] = []
    for value in _scalars(doc):
        if (isinstance(value, str) and 7 <= len(value) <= 40
                and all(c in "0123456789abcdef" for c in value) and value not in seen
                and _is_ancestor_commit(root, value)):
            seen.append(value)
            if len(seen) > 1:
                break
    if not seen:
        return None, "the feed records no commit of this repository, so it has not said where it "\
                     "was published from"
    if len(seen) > 1:
        return None, (
            "the feed records more than one commit of this repository, so which of them is the "
            "publication standpoint and which is its subject cannot be told apart from the bytes"
        )
    return seen[0], "the one commit this feed records"


class RegenerationCheckRefused(RuntimeError):
    """The check could not be performed. Never a pass, never a red — a refusal."""


#: A checkout of this repository measured ~400 MB on 2026-09-19, and a run holds up to two trees at
#: once (three when a candidate is graded at its own commit and needs a determinism tree). The
#: scratch directory must have room for several, plus what a generator writes.
_A_CHECKOUT_MB = 400
_SCRATCH_NEEDS_MB = _A_CHECKOUT_MB * 4


def _free_mb(path: Path) -> int:
    try:
        usage = shutil.disk_usage(path)
    except OSError:
        return 0
    return usage.free // (1024 * 1024)


def scratch_root() -> Path:
    """Where to build the private trees — CHOSEN BY MEASURED FREE SPACE, never by default.

    THE DEFECT THIS EXISTS FOR (2026-09-19, `WORKER_FINDING_THE_FEED_REGENERATION_CONTROL_LEAKS_ITS
    _CLONES_INTO_TMP_AND_THEN_REDS_FOR_LACK_OF_THE_SPACE_IT_TOOK`). `tempfile.mkdtemp()` defaults to
    `/tmp`, which on this machine is a **12 GB tmpfs** — RAM. One afternoon's runs of this control
    left ~5.6 GB of abandoned clones in it, took it to 94% full, and the next run's `git clone`
    could not write a working tree. The gate then reported a feed-comparison refusal, so the reader
    was sent to the published feeds while the actual fault was a full disk, and the merge to origin
    was blocked by it. **A control whose cost grows with how often it has run is not a control that
    can hold.**

    So the root is picked by asking each candidate how much room it has, largest first, and the
    repository's own filesystem is a candidate — it had 705 GB free while `/tmp` had 798 MB. A leak
    there costs disk, which is abundant, instead of memory, which is the binding figure on this box.

    KEYED TO THE PROPERTY, NOT TO `/var/tmp`. Nothing here asserts that `/tmp` is small or that
    `/var/tmp` is big; it asserts that the tree is built somewhere with room for it. The day `/tmp`
    is a real disk it is eligible again with nobody editing a list.
    """
    named = os.environ.get("SE_FEED_CHECK_SCRATCH")
    # An explicit root is THE root, not another candidate: a caller who says where to build must be
    # able to be refused there, or the space check below can never be reached and never proven.
    candidates = ([Path(named)] if named
                  else [Path(p) for p in ("/var/tmp", str(PROJECT.parent),
                                          tempfile.gettempdir())])
    usable = [(c, _free_mb(c)) for c in candidates if c.is_dir()]
    usable.sort(key=lambda pair: pair[1], reverse=True)
    if not usable:
        raise RegenerationCheckRefused(
            f"no scratch directory exists out of {[str(c) for c in candidates]}"
        )
    best, free = usable[0]
    if free < _SCRATCH_NEEDS_MB:
        raise RegenerationCheckRefused(
            f"THE DISK, NOT THE FEEDS: the roomiest scratch directory available ({best}) has "
            f"{free} MB free and a run of this check needs about {_SCRATCH_NEEDS_MB} MB "
            f"({_A_CHECKOUT_MB} MB per tree). Nothing has been measured about any published feed."
        )
    return best


def _git(root: str | Path, *args: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", "-C", str(root), *args],
                          capture_output=True, text=True, check=False, env=env)


def head_resolves(root: Path = PROJECT) -> bool:
    """Does this checkout have a commit to read? The landing checkout does not."""
    try:
        return _git(root, "rev-parse", "--verify", "HEAD").returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def _why_the_clone_failed(stderr: str, tmp: Path) -> str:
    """Name the DISK when it was the disk. See `scratch_root` for what this cost once.

    `git clone` reports a failed working-tree checkout as `unable to write file <path>` and
    `warning: Clone succeeded, but checkout failed` — with no mention of space. Wrapped in a
    `RegenerationCheckRefused`, that reads as a statement about the published feeds, and on
    2026-09-19 it sent a reader to the feeds while the machine was out of RAM. So the free space is
    re-measured at the moment of the failure and put in front of the git text, not behind it.
    """
    said = stderr.strip()[-300:]
    free = _free_mb(tmp)
    if "unable to write file" in stderr or "checkout failed" in stderr or "No space" in stderr:
        return (
            f"THE DISK, NOT THE FEEDS: git could not write the working tree into {tmp}, which has "
            f"{free} MB free. Nothing has been measured about any published feed. git said: {said}"
        )
    return f"could not clone the tree under test ({free} MB free in {tmp}): {said}"


class _Tree:
    """A private, writable copy of the tree under test, at the committed bytes.

    A clone when HEAD resolves; a file copy of the working tree when it does not (see the module
    docstring's named exception). Either way, writing in it cannot reach the shared tree.
    """

    def __init__(self, root: Path, tmp: Path, ordinal: int, at_commit: str | None = None):
        self.path = tmp / f"tree{ordinal}"
        self._cloned = head_resolves(root)
        if at_commit and not self._cloned:
            raise RegenerationCheckRefused(
                f"asked to stand at {at_commit} in a checkout with no resolvable HEAD — there is "
                "no history here to stand in, and grading the disk instead would answer a "
                "different question under the same name"
            )
        if self._cloned:
            done = subprocess.run(
                ["git", "clone", "--shared", "--quiet", str(root), str(self.path)],
                capture_output=True, text=True, check=False,
            )
            if done.returncode != 0:
                raise RegenerationCheckRefused(_why_the_clone_failed(done.stderr, tmp))
        else:
            # No HEAD: the disk IS the tree being graded. Copy it rather than read it in place,
            # because the generators write.
            shutil.copytree(root, self.path, symlinks=True,
                            ignore=shutil.ignore_patterns(".git"))
        if at_commit:
            done = _git(self.path, "checkout", "--quiet", "--detach", at_commit)
            if done.returncode != 0:
                raise RegenerationCheckRefused(
                    f"could not stand at {at_commit}: {done.stderr.strip()[-300:]}"
                )
        if not (self.path / FEED_DIR).is_dir():
            raise RegenerationCheckRefused(
                f"the tree under test has no {FEED_DIR}/ — refusing to measure an empty feed "
                "set, because an empty set agrees with every claim ever made"
            )

    def restore_feeds(self) -> None:
        """Put the feed directory back to the committed bytes."""
        if self._cloned:
            done = _git(self.path, "checkout", "--", FEED_DIR)
            if done.returncode != 0:
                raise RegenerationCheckRefused(
                    f"could not restore {FEED_DIR} in the tree under test: {done.stderr.strip()}"
                )

    def feeds(self) -> dict[str, bytes]:
        return {p.name: p.read_bytes() for p in sorted((self.path / FEED_DIR).glob("*.json"))}

    def run(self, generator: str, timeout_s: int) -> tuple[dict[str, bytes], str]:
        """Run `tools.<generator>` inside this tree; return the feeds it CHANGED, and any error."""
        self.restore_feeds()
        before = self.feeds()
        env = dict(os.environ)
        env["PYTHONPATH"] = str(self.path)
        try:
            done = subprocess.run([sys.executable, "-m", f"tools.{generator}"],
                                  cwd=str(self.path), env=env, capture_output=True,
                                  text=True, timeout=timeout_s, check=False)
            err = "" if done.returncode == 0 else (done.stderr or "")[-400:].strip()
        except subprocess.TimeoutExpired:
            return {}, f"timed out after {timeout_s}s"
        except OSError as exc:
            return {}, f"could not run the generator: {exc}"
        after = self.feeds()
        return {n: after[n] for n in after if before.get(n) != after[n]}, err


def _verdict(committed: bytes, first: bytes, second: bytes | None) -> tuple[str, dict]:
    """AGREES / DIVERGES / NONDETERMINISTIC / UNPARSEABLE, with the diff that decided it."""
    from tools.artefact_rerun_diff import compare  # local: keeps import cost off the green path
    try:
        was, now = json.loads(committed), json.loads(first)
    except (ValueError, UnicodeDecodeError) as exc:
        return "UNPARSEABLE", {"error": str(exc)[:200]}
    against_committed = compare(was, now)
    if not (against_committed["changed"] or against_committed["removed"]):
        return "AGREES", {}
    if second is not None:
        try:
            again = json.loads(second)
        except (ValueError, UnicodeDecodeError) as exc:
            return "UNPARSEABLE", {"error": str(exc)[:200]}
        run_to_run = compare(now, again)
        if run_to_run["changed"] or run_to_run["removed"] or run_to_run["added"]:
            return "NONDETERMINISTIC", {
                "run_to_run": [list(map(str, c)) for c in run_to_run["changed"][:5]],
            }
    return "DIVERGES", {
        "changed": [list(map(str, c)) for c in against_committed["changed"][:10]],
        "removed": against_committed["removed"][:10],
        "n_changed": len(against_committed["changed"]),
        "n_removed": len(against_committed["removed"]),
    }


def check(generators, root: Path = PROJECT, timeout_s: int = DEFAULT_TIMEOUT_S,
          separate_nondeterminism: bool = True) -> list[dict]:
    """Regenerate each generator's feeds in a private tree and grade them against committed bytes.

    Returns one row per FEED the generator actually wrote — observed, not declared. A generator that
    writes nothing gets a single `WROTE_NOTHING` row, which is a gap and not a pass.

    `separate_nondeterminism=False` skips the second tree, so a feed that does not reproduce is
    reported as DIVERGES without establishing WHY. That is the wrong reading for grading a feed and
    the right one for the only question a caller may ask without it — "does this feed reproduce?",
    where AGREES is decided on the first tree alone. It roughly halves the sweep, and it may never
    be used to justify a red: DIVERGES from this mode does not distinguish a hand-edit from a
    generator that reads the clock.
    """
    generators = list(generators)
    if not generators:
        raise RegenerationCheckRefused(
            "no generators named — refusing to report a clean sweep over an empty set"
        )
    rows: list[dict] = []
    tmp = Path(tempfile.mkdtemp(prefix="feed-regen-", dir=scratch_root()))
    try:
        first = _Tree(root, tmp, 1)
        second: _Tree | None = None
        committed = first.feeds()
        for generator in generators:
            written, err = first.run(generator, timeout_s)
            if not written:
                rows.append({"generator": generator, "feed": None,
                             "verdict": "WROTE_NOTHING", "detail": {"stderr": err}})
                continue
            # Only pay for the determinism tree when something actually disagrees.
            needs_second = separate_nondeterminism and any(
                committed.get(n) != b for n, b in written.items())
            again: dict[str, bytes] = {}
            if needs_second:
                if second is None:
                    second = _Tree(root, tmp, 2)
                again, _ = second.run(generator, timeout_s)
            for name in sorted(written):
                if name not in committed:
                    rows.append({"generator": generator, "feed": name,
                                 "verdict": "NOT_COMMITTED", "detail": {}})
                    continue
                verdict, detail = _verdict(committed[name], written[name], again.get(name))
                if err:
                    detail = {**detail, "stderr": err}
                rows.append({"generator": generator, "feed": name,
                             "verdict": verdict, "detail": detail})
        return rows
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _committed_feed(root: Path, name: str) -> bytes | None:
    """The bytes of `site/data/<name>` at `root`'s HEAD, or None if HEAD does not carry it."""
    done = subprocess.run(["git", "-C", str(root), "show", f"HEAD:{FEED_DIR}/{name}"],
                          capture_output=True, check=False,
                          env={k: v for k, v in os.environ.items() if not k.startswith("GIT_")})
    return done.stdout if done.returncode == 0 else None


def check_at_its_own_commit(feeds: dict[str, str], root: Path = PROJECT,
                            timeout_s: int = DEFAULT_TIMEOUT_S) -> list[dict]:
    """Does each feed reproduce at the commit IT RECORDS having been published from?

    THE QUESTION THIS ASKS, AND THE WEAKER ONE IT ANSWERS. `check()` stands at HEAD, so a feed whose
    content is a function of its commit — the git log, another committed feed — diverges there for
    no fault of anybody's: it was published at an earlier commit and it still says so. Measured
    2026-09-19, that is why 23 of the 31 runnable feeds cannot be checked at all. This stands
    instead at the commit the feed itself names, where those inputs are back to what they were.

    The verdicts are deliberately NOT the same words as `check()`'s. `AGREES_AT_ITS_OWN_COMMIT` is a
    strictly weaker statement than `AGREES`: it says the published bytes are what the generator
    produced AT THE COMMIT THE FEED NAMES, which catches a hand-edit made after publication and says
    nothing about whether today's generator would still produce them. A feed that is merely STALE
    agrees here. Sharing the word `AGREES` would let the weaker claim be read as the stronger one by
    any caller that only looked at the verdict, which is this project's most-repeated way of
    publishing something misleading out of two correct parts.

    The standpoint is OBSERVED from the feed (`recorded_publication_commit`) and never passed in, so
    a feed cannot be graded against a commit chosen by whoever ran the check.
    """
    if not feeds:
        raise RegenerationCheckRefused(
            "no feeds named — refusing to report a clean sweep over an empty set"
        )
    if not head_resolves(root):
        raise RegenerationCheckRefused(
            "this checkout has no resolvable HEAD, so there is no published commit to stand at"
        )
    rows: list[dict] = []
    tmp = Path(tempfile.mkdtemp(prefix="feed-own-commit-", dir=scratch_root()))
    try:
        for name in sorted(feeds):
            generator = feeds[name]
            row = {"feed": name, "generator": generator, "recorded_commit": None}
            committed = _committed_feed(root, name)
            if committed is None:
                rows.append({**row, "verdict": "NOT_COMMITTED", "detail": {}})
                continue
            try:
                doc = json.loads(committed)
            except (ValueError, UnicodeDecodeError) as exc:
                rows.append({**row, "verdict": "UNPARSEABLE", "detail": {"error": str(exc)[:200]}})
                continue
            sha, why = recorded_publication_commit(doc, root)
            row["recorded_commit"] = sha
            if sha is None:
                rows.append({**row, "verdict": "NO_STANDPOINT", "detail": {"reason": why}})
                continue
            try:
                tree = _Tree(root, tmp, len(rows) + 1, at_commit=sha)
            except RegenerationCheckRefused as exc:
                # A recorded sha that cannot be stood at is a refusal, never a pass: a control over
                # what was published must not go green because it could not find out.
                rows.append({**row, "verdict": "UNREACHABLE_STANDPOINT",
                             "detail": {"reason": str(exc)[:300]}})
                continue
            written, err = tree.run(generator, timeout_s)
            if name not in written:
                rows.append({**row, "verdict": "WROTE_NOTHING",
                             "detail": {"stderr": err,
                                        "wrote_instead": sorted(written)[:5]}})
                continue
            # Only pay for the determinism tree when something disagrees — and pay for it at the
            # SAME standpoint, because a generator that reads the clock must not be reported as a
            # divergence from the published bytes. NONDETERMINISTIC is never a red here either.
            again: bytes | None = None
            if committed != written[name]:
                second = _Tree(root, tmp, len(rows) + 1000, at_commit=sha)
                again = second.run(generator, timeout_s)[0].get(name)
            verdict, detail = _verdict(committed, written[name], again)
            verdict = {"AGREES": "AGREES_AT_ITS_OWN_COMMIT",
                       "DIVERGES": "DIVERGES_AT_ITS_OWN_COMMIT"}.get(verdict, verdict)
            if err:
                detail = {**detail, "stderr": err}
            rows.append({**row, "verdict": verdict, "detail": detail})
        return rows
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("generators", nargs="*",
                        help="generator module stems, e.g. generate_simplified_data. "
                             "Default: every tools/generate_*.py in the tree.")
    parser.add_argument("--json", action="store_true", help="emit the rows as JSON")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_S)
    parser.add_argument("--at-its-own-commit", action="store_true",
                        help="stand at the commit each candidate feed records rather than at HEAD. "
                             "Takes feed names, or defaults to CANDIDATES_AT_THEIR_OWN_COMMIT.")
    args = parser.parse_args(argv)

    if args.at_its_own_commit:
        feeds = ({n: CANDIDATES_AT_THEIR_OWN_COMMIT[n] for n in args.generators}
                 if args.generators else dict(CANDIDATES_AT_THEIR_OWN_COMMIT))
        rows = check_at_its_own_commit(feeds, timeout_s=args.timeout)
        if args.json:
            print(json.dumps(rows, indent=1))
        else:
            for row in rows:
                print(f"{row['verdict']:<28} {row['feed']:<28} "
                      f"at {row['recorded_commit'] or '-'}")
        return 1 if any(r["verdict"] == "DIVERGES_AT_ITS_OWN_COMMIT" for r in rows) else 0

    names = args.generators or sorted(p.stem for p in (PROJECT / "tools").glob("generate_*.py"))
    rows = check(names, timeout_s=args.timeout)
    if args.json:
        print(json.dumps(rows, indent=1))
    else:
        for row in rows:
            print(f"{row['verdict']:<16} {row['feed'] or '-':<28} {row['generator']}")
        counts: dict[str, int] = {}
        for row in rows:
            counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
        print("\n" + "  ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    return 1 if any(r["verdict"] == "DIVERGES" for r in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
