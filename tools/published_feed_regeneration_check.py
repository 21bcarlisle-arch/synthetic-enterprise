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

────────────────────────────────────────────────────────────────────────────────────────────────
THE SECOND RELATION KIND: A DERIVED ARTEFACT AND THE PRODUCER THAT WRITES IT
────────────────────────────────────────────────────────────────────────────────────────────────

WHY THE RELATION ABOVE CANNOT SEE THE DEFECT THIS ONE EXISTS FOR. Everything above compares a feed
against ITS OWN GENERATOR, which means the pair is only ever as fresh as the weakest link BETWEEN
them. On 2026-09-21 `tools/churn_belief_size_response.py` was edited in place with a new origin
sentence; `docs/observability/churn_belief_size_response.json` was never re-run;
`site/data/value_arms.json` was then regenerated FROM that stale intermediate. The publisher was
refused every cycle for two days (`episode_clean_publishes` 0, `wedge_since` 2026-09-21T20:40).

The obvious fix — "give this module a working-tree mode and add the chain" — was filed as settled,
measured, and REFUTED before it was built (`SEAT_RESULT_THE_REMEDY_A_LIVE_CONTINUATION_NAMES_WOULD_
HAVE_BEEN_GREEN_THROUGHOUT_THE_OUTAGE_IT_IS_MEANT_TO_CATCH_2026-09-23.md`, landed `be6b67b98`).
`generate_value_arms_data` derives that sentence with a bare `knee.get(...)` pass-through, so
regenerating the feed from ANY standpoint in ANY tree re-reads the same stale intermediate and
reproduces byte-identical output. Feed and generator AGREE. A working-tree mode would have been
GREEN for the whole outage it was meant to catch — a control that cannot fail, built on purpose.
The broken relation is ONE LINK UPSTREAM of any pair the first relation compares.

WHAT THIS RELATION ACTUALLY DECIDES, AND WHAT IT REFUSES TO CLAIM. It does NOT claim staleness.
Whether a producer edit would change the artefact's bytes is undecidable without running the
producer, and running 100+ producers is not a commit-time control. What IS decidable is strictly
weaker and is what the verdict is named for: `NOT_REGENERATED_SINCE_ITS_PRODUCER_CHANGED`. A
comment-only edit to a producer trips it and re-running is a no-op — that is a true positive for
the property actually asserted, and the remedy (run the producer) is cheap and total either way.
Naming it `STALE` would have been the overclaim this repository files under "before dividing two
numbers, say out loud what each one counts".

THE PAIR IS OBSERVED FROM THE PRODUCER'S SOURCE, NEVER DECLARED — same rule as `COVERED_FEEDS`
above, reached by a different route because this one may not run anything. `_artefact_roles` walks
each `tools/*.py` with `ast`, resolves `PROJECT / "docs" / "observability" / "<name>.json"` chains
and their module-level aliases, and classifies each by HOW THE PATH IS USED: `.write_text` /
`open(…, "w")` is a WRITER, `.read_text` / `json.load` is a READER.

THAT DISCRIMINATION IS THE WHOLE DESIGN, AND A NAMING CONVENTION WAS MEASURED AND REJECTED. Measured
2026-09-23 (pre-registered in `SEAT_PREREG_HOW_IS_A_DERIVED_ARTEFACTS_PRODUCER_OBSERVED…`, all
predictions confirmed): the stem convention `tools/<x>.py ↔ docs/observability/<x>.json` finds 20
pairs, the source walk finds 57, 39 of which the convention cannot see — and 2 of the convention's
own 20 are same-stem coincidences it would have named an innocent file for. Worse, 16 artefacts are
NAMED by more than one module, because READERS name the path too: `generate_value_arms_data.py`
names the churn artefact precisely because it reads it. A name match is not a producer. With the
role walk, 18 artefacts resolve to exactly one writer and NONE resolve to two.

THE OTHER 36 ARE A NAMED GAP AND NEVER A PASS. A module whose write target this walk cannot resolve
(built at runtime, passed in as an argument, written through a helper) yields
`NO_PRODUCER_RESOLVED`, which is reported and is not green. An artefact named by two writers yields
`AMBIGUOUS_PRODUCER`. Neither is silent, because a control over what is regenerated must not go
green because it could not find out — the same rule the first relation states above.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

if str(Path(__file__).resolve().parent.parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools import provenance_stamp  # noqa: E402

PROJECT = Path(__file__).resolve().parent.parent
FEED_DIR = "site/data"

#: Per-generator ceiling. The slowest real generator measured 2026-09-19 is
#: `generate_provisional_plan_data` at 251s (`git log --reverse --follow` over the whole history).
DEFAULT_TIMEOUT_S = 300

#: HOW FAR THE DETERMINISM PROBE'S SECOND TREE MOVES THE WALL CLOCK, and why it has to move at all.
#:
#: MEASURED 2026-09-23. `knowledge_review.json` sat in `COVERED_FEEDS` for four days and reds two
#: days after any regeneration, because it publishes `age_days` — `date.today()` minus a committed
#: date — which is not a function of its commit at all. Two things let it in, and only the second
#: was in the finding that named it:
#:
#:   * THE SECOND TREE IS ONLY BUILT WHEN THE FIRST DISAGREES. A feed whose committed bytes are
#:     fresh AGREES on the first tree and is never asked the determinism question, so the probe that
#:     would have refused it never ran. `always_probe_determinism=True` is that repair.
#:   * THE PROBE'S RESOLUTION WAS SHORTER THAN THE PERIOD IT HUNTS. Both runs happen seconds apart,
#:     and a quantity that changes once a day is byte-identical across them, so a clock-dependent
#:     feed reads as deterministic. An instrument blind to intervals shorter than its own tick
#:     returning a clean answer rather than "cannot tell" is this project's catalogued shape.
#:
#: So the second tree runs its generator under a DISPLACED clock. 400 days moves day, month, quarter
#: and year at once, so a period of any of those lengths is caught by one extra run rather than by
#: waiting for it. It is not a system `faketime` — nothing outside this repository is required — and
#: it redirects no output path, which is the failure mode the module docstring already refuses.
#:
#: WHY THIS IS NOT JUST MEASURING THE INSTRUMENT: `artefact_rerun_diff.compare` excludes exactly one
#: key by name, `generated_at`, whose whole purpose is to differ. So a displaced clock trips
#: `NONDETERMINISTIC` only when the clock reaches a field that is NOT the publication timestamp —
#: which is precisely the question `COVERED_FEEDS` membership asks.
_CLOCK_DISPLACEMENT_DAYS = 400

#: Patched as a `sitecustomize`, which CPython imports before any user module, so a generator's
#: own `from datetime import date` binds the displaced class rather than the real one. Only
#: pure-Python clock reads are intercepted, which is all any generator here does.
_CLOCK_OFFSET_ENV = "SE_FEED_CHECK_CLOCK_OFFSET_S"

_CLOCK_SHIM = '''"""A displaced wall clock for the feed-regeneration determinism probe.

Written into a scratch directory and put on PYTHONPATH by
`tools/published_feed_regeneration_check`. Never installed anywhere persistent.

The offset comes from the environment and is NOT defaulted: a shim that silently displaced
nothing would make every clock-dependent feed read as deterministic, which is the exact defect
this exists to catch. Missing means the interpreter refuses to start, which is visible.
"""
import datetime as _dt
import os as _os
import time as _time

_OFFSET_S = float(_os.environ["SE_FEED_CHECK_CLOCK_OFFSET_S"])

_real_time = _time.time
_real_gmtime = _time.gmtime
_real_localtime = _time.localtime

_time.time = lambda: _real_time() + _OFFSET_S
_time.gmtime = lambda secs=None: _real_gmtime(_time.time() if secs is None else secs)
_time.localtime = lambda secs=None: _real_localtime(_time.time() if secs is None else secs)


class _Date(_dt.date):
    @classmethod
    def today(cls):
        return cls.fromtimestamp(_time.time())


class _DateTime(_dt.datetime):
    @classmethod
    def now(cls, tz=None):
        return cls.fromtimestamp(_time.time(), tz)

    @classmethod
    def utcnow(cls):
        return cls.utcfromtimestamp(_time.time())

    @classmethod
    def today(cls):
        return cls.fromtimestamp(_time.time())


_dt.date = _Date
_dt.datetime = _DateTime
'''


def _clock_shim_dir(tmp: Path) -> Path:
    """A scratch directory holding the displaced-clock `sitecustomize`, created once per sweep."""
    shim = tmp / "clockshim"
    if not (shim / "sitecustomize.py").exists():
        shim.mkdir(parents=True, exist_ok=True)
        (shim / "sitecustomize.py").write_text(_CLOCK_SHIM, encoding="utf-8")
    return shim


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
    "premise_demand.json": "generate_premise_demand_data",
    "regulatory.json": "generate_regulatory_data",
    "simplified.json": "generate_simplified_data",
    "world.json": "generate_world_data",
}

#: REMOVED FROM THE SET ABOVE, with the measurement that removed it — because a feed deleted from a
#: covered set without a reason beside it is indistinguishable from a feed deleted to make a red go
#: away, and this project has paid for that difference.
#:
#: MEASURED 2026-09-23 with `always_probe_determinism=True` and the clock displaced 400 days
#: (pre-registered in `WORKER_PREREG_WHAT_A_DISPLACED_CLOCK_MEASURES_ABOUT_THE_COVERED_FEED_SET`):
#: of the eight feeds then covered, seven still AGREE and exactly one moves —
#: `knowledge_review.json`, whose `/topics[*]/age_days` went 26 → 426 and whose `/tally` swung
#: 16 fresh / 0 due to 0 fresh / 16 due. It publishes `date.today()` minus a committed date, so it
#: is not a function of its commit and never satisfied this table's membership rule.
#:
#: IT IS NOT LISTED AS AN EXCLUSION ANYWHERE THAT A SWEEP CONSULTS, and that is deliberate: the
#: demotion leg re-measures it on every run, so if `generate_knowledge_review` ever stops reading
#: the wall clock the promotion leg puts it straight back with nobody editing a list. This note is
#: the record of why it left, not a rule that keeps it out.
NOT_A_FUNCTION_OF_ITS_COMMIT = {
    "knowledge_review.json": (
        "publishes `age_days` — `date.today()` minus a committed `last_checked` — so its bytes are "
        "a function of the day it was published on, not of the commit it was published from"
    ),
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
#:
#: REPAIRED AT THE PRODUCER, 2026-09-19 — and the repair does not make these feeds reproduce, it
#: makes them SAY SO. Both generators now publish `provenance_stamp.STAMP_KEY`, carrying the commit
#: AND whether the bytes they read were that commit's. `recorded_publication_commit` reads it first
#: and returns NO_STANDPOINT with the feed's own reason when the answer is no, rather than standing
#: at a commit that was never going to reproduce and reporting the difference as a divergence. A
#: feed published from a clean tree becomes checkable here with nobody editing a list; a feed
#: published from a dirty one is uncheckable and now names which input moved.
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

    THAT DAY ARRIVED 2026-09-19 AND THE RESERVED KEY IS CONSULTED FIRST. `provenance_stamp.STAMP_KEY`
    is the one place a feed may say which of its shas is the standpoint. Reading it before the scan
    is not an optimisation: `capabilities_door.json` keeps a back-compatible `git_commit` beside the
    stamp and `evidence.json` a SHORT `git_hash`, and the scan would count the short form and the
    full form as TWO commits and lose the standpoint of a feed that had finally declared it.
    """
    if isinstance(doc, dict):
        block = doc.get(provenance_stamp.STAMP_KEY)
        if isinstance(block, dict) and "commit" in block:
            sha = block.get("commit")
            if not (isinstance(sha, str) and _is_ancestor_commit(root, sha)):
                return None, (
                    f"the feed's reserved {provenance_stamp.STAMP_KEY!r} names "
                    f"{sha!r}, which is not a commit of this repository reachable from HEAD"
                )
            if not provenance_stamp.describes_its_inputs(block):
                # A NAMED REFUSAL, NOT A DIVERGENCE. The feed itself says the commit does not
                # describe the bytes it read, so standing there cannot reproduce it and reporting
                # the difference as a red would blame the comparator for a producer's honesty.
                return None, (
                    f"the feed records {sha[:9]} but says the bytes it read were not that "
                    f"commit's — {block.get('reason') or 'no reason given'}"
                )
            return sha, (f"the commit the feed declares under {provenance_stamp.STAMP_KEY!r}, "
                         "which also says its inputs were that commit's bytes")
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

    def run(self, generator: str, timeout_s: int,
            displace_clock: bool = False) -> tuple[dict[str, bytes], str]:
        """Run `tools.<generator>` inside this tree; return the feeds it CHANGED, and any error.

        `displace_clock` moves the generator's wall clock forward by `_CLOCK_DISPLACEMENT_DAYS`
        via a `sitecustomize` shim, WITHOUT touching this tree's bytes or its commit. That makes
        the pair of runs a probe of "is this feed a function of its commit" rather than only of
        "did anything move in the last two seconds" — see `_CLOCK_DISPLACEMENT_DAYS`.
        """
        self.restore_feeds()
        before = self.feeds()
        env = dict(os.environ)
        env["PYTHONPATH"] = str(self.path)
        if displace_clock:
            shim = _clock_shim_dir(self.path.parent)
            env["PYTHONPATH"] = os.pathsep.join([str(shim), str(self.path)])
            env[_CLOCK_OFFSET_ENV] = str(_CLOCK_DISPLACEMENT_DAYS * 86400.0)
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


def _second_observation(second: "_Tree", generator: str, timeout_s: int,
                        wanted: set[str]) -> tuple[dict[str, bytes], str | None]:
    """The determinism tree's run, under a displaced clock, with a named fallback.

    THE HAZARD THIS HANDLES, and it is the one the pre-registration called the costly one. A
    generator that CRASHES under the displaced clock writes nothing, and the caller's
    `again.get(name)` would then be None — which `_verdict` reads as "no determinism evidence" and
    reports as DIVERGES. A widening of the probe must never be able to manufacture a red.

    So a displaced run that did not produce every feed wanted is retried undisplaced, and the
    probe's own degradation is RETURNED rather than swallowed: the row says the widening did not
    run for this generator instead of quietly answering the narrower question under the same name.
    """
    again, _ = second.run(generator, timeout_s, displace_clock=True)
    if wanted <= set(again):
        return again, None
    missed = sorted(wanted - set(again))
    narrow, _ = second.run(generator, timeout_s)
    return {**narrow, **again}, (
        f"the displaced-clock probe did not reproduce {missed}, so determinism was decided by two "
        f"runs seconds apart — which cannot see a quantity whose period is longer than that"
    )


def check(generators, root: Path = PROJECT, timeout_s: int = DEFAULT_TIMEOUT_S,
          separate_nondeterminism: bool = True,
          always_probe_determinism: bool = False) -> list[dict]:
    """Regenerate each generator's feeds in a private tree and grade them against committed bytes.

    Returns one row per FEED the generator actually wrote — observed, not declared. A generator that
    writes nothing gets a single `WROTE_NOTHING` row, which is a gap and not a pass.

    `separate_nondeterminism=False` skips the second tree, so a feed that does not reproduce is
    reported as DIVERGES without establishing WHY. That is the wrong reading for grading a feed and
    the right one for the only question a caller may ask without it — "does this feed reproduce?",
    where AGREES is decided on the first tree alone. It roughly halves the sweep, and it may never
    be used to justify a red: DIVERGES from this mode does not distinguish a hand-edit from a
    generator that reads the clock.

    `always_probe_determinism=True` builds the second tree even when the first AGREES. That is the
    only way to ask the membership question of a feed whose committed bytes happen to be fresh, and
    it is how `knowledge_review.json` got into `COVERED_FEEDS` unasked — see
    `_CLOCK_DISPLACEMENT_DAYS`. It doubles the sweep, so it is off for the ordinary grading pass
    and on wherever membership itself is being decided.
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
            # Only pay for the determinism tree when something actually disagrees — unless
            # membership itself is the question, in which case an AGREES that was never probed is
            # the defect (see `always_probe_determinism`).
            needs_second = separate_nondeterminism and (always_probe_determinism or any(
                committed.get(n) != b for n, b in written.items()))
            again: dict[str, bytes] = {}
            probe_degraded: str | None = None
            if needs_second:
                if second is None:
                    second = _Tree(root, tmp, 2)
                again, probe_degraded = _second_observation(
                    second, generator, timeout_s, set(written))
            for name in sorted(written):
                if name not in committed:
                    rows.append({"generator": generator, "feed": name,
                                 "verdict": "NOT_COMMITTED", "detail": {}})
                    continue
                verdict, detail = _verdict(committed[name], written[name], again.get(name))
                if err:
                    detail = {**detail, "stderr": err}
                if needs_second:
                    detail = {**detail, "probe": probe_degraded or (
                        f"a second tree at the same commit with the wall clock displaced by "
                        f"{_CLOCK_DISPLACEMENT_DAYS} days")}
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
                again = _second_observation(second, generator, timeout_s, {name})[0].get(name)
            verdict, detail = _verdict(committed, written[name], again)
            verdict = {"AGREES": "AGREES_AT_ITS_OWN_COMMIT",
                       "DIVERGES": "DIVERGES_AT_ITS_OWN_COMMIT"}.get(verdict, verdict)
            if err:
                detail = {**detail, "stderr": err}
            rows.append({**row, "verdict": verdict, "detail": detail})
        return rows
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


#: Where the second relation kind looks for derived artefacts. Not `FEED_DIR`: the defect this
#: relation exists for lives in an INTERMEDIATE, one link upstream of anything published.
DERIVED_DIR = "docs/observability"

#: Attribute calls that decide a path's role. The classification is by USE, not by name, because 16
#: artefacts are named by a module that only reads them (see the module docstring).
_WRITE_CALLS = frozenset({"write_text", "write_bytes"})
_READ_CALLS = frozenset({"read_text", "read_bytes"})


def _artefact_path(node: ast.AST) -> str | None:
    """The `docs/observability/*.json` path an AST node denotes, or None.

    Handles the two shapes producers actually use: a `PROJECT / "docs" / "observability" / "x.json"`
    division chain, and a bare string. A chain with any non-literal segment resolves to None rather
    than to a guess — an unresolvable path is a gap this module reports, never one it invents.
    """
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        parts: list[str | None] = []
        cur: ast.AST = node
        while isinstance(cur, ast.BinOp) and isinstance(cur.op, ast.Div):
            right = cur.right
            parts.append(right.value if isinstance(right, ast.Constant)
                         and isinstance(right.value, str) else None)
            cur = cur.left
        if None in parts:
            return None
        joined = "/".join(reversed([p for p in parts if p is not None]))
        marker = f"{DERIVED_DIR}/"
        if marker in joined and joined.endswith(".json"):
            return joined[joined.index(marker):]
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        value = node.value
        if value.startswith(f"{DERIVED_DIR}/") and value.endswith(".json"):
            return value
    return None


def _artefact_roles(source: Path) -> dict[str, set[str]]:
    """Every derived-artefact path this module NAMES, mapped to how it uses it: `W` and/or `R`.

    A path named with neither role resolved maps to an empty set, which is a gap and not a pass.
    """
    try:
        tree = ast.parse(source.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return {}

    bound: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            path = _artefact_path(node.value)
            if path:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        bound[target.id] = path
    # Alias chains — `dest = DEFAULT_ARTEFACT if out is None else out` is the idiom producers use,
    # so a walk that only saw direct assignment would resolve no role for the commonest shape.
    for _ in range(3):
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            value = node.value
            candidates: list[str] = []
            if isinstance(value, ast.Name):
                candidates = [value.id]
            elif isinstance(value, ast.IfExp):
                candidates = [b.id for b in (value.body, value.orelse) if isinstance(b, ast.Name)]
            resolved = [bound[c] for c in candidates if c in bound]
            if resolved:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        bound.setdefault(target.id, resolved[0])

    def denoted(node: ast.AST) -> str | None:
        direct = _artefact_path(node)
        if direct:
            return direct
        return bound.get(node.id) if isinstance(node, ast.Name) else None

    roles: dict[str, set[str]] = {}
    for path in bound.values():
        roles.setdefault(path, set())
    for node in ast.walk(tree):
        path = _artefact_path(node)
        if path:
            roles.setdefault(path, set())
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Attribute):
            target = denoted(node.func.value)
            if target and node.func.attr in _WRITE_CALLS:
                roles.setdefault(target, set()).add("W")
            if target and node.func.attr in _READ_CALLS:
                roles.setdefault(target, set()).add("R")
        name = (node.func.id if isinstance(node.func, ast.Name)
                else node.func.attr if isinstance(node.func, ast.Attribute) else None)
        if name == "open" and node.args:
            target = denoted(node.args[0])
            mode = "r"
            if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                mode = str(node.args[1].value)
            for kw in node.keywords:
                if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                    mode = str(kw.value.value)
            if target:
                roles.setdefault(target, set()).add(
                    "W" if ("w" in mode or "a" in mode) else "R")
    return roles


def derived_artefact_producers(root: Path = PROJECT) -> tuple[dict[str, str], dict[str, str]]:
    """`(artefact -> the one module that writes it, artefact -> why no producer was resolved)`.

    Observed from source, never declared. Both halves are returned because the gaps are reported
    beside the covered set rather than dropped: an artefact nothing here can attribute is a thing
    this control cannot speak about, and silence would read as a pass.
    """
    named: dict[str, set[str]] = {}
    writers: dict[str, list[str]] = {}
    for source in sorted((root / "tools").glob("*.py")):
        for path, roles in _artefact_roles(source).items():
            named.setdefault(path, set()).update(roles)
            if "W" in roles:
                writers.setdefault(path, []).append(source.relative_to(root).as_posix())

    producers: dict[str, str] = {}
    gaps: dict[str, str] = {}
    for artefact in sorted(p.relative_to(root).as_posix()
                           for p in (root / DERIVED_DIR).glob("*.json")):
        found = writers.get(artefact, [])
        if len(found) == 1:
            producers[artefact] = found[0]
        elif len(found) > 1:
            gaps[artefact] = (f"AMBIGUOUS_PRODUCER: {len(found)} modules write it — "
                              + ", ".join(sorted(found)))
        elif artefact in named:
            gaps[artefact] = ("NO_PRODUCER_RESOLVED: named in tools/ but only ever read, or its "
                              "write target is built at runtime")
        else:
            gaps[artefact] = "NO_PRODUCER_RESOLVED: no tools/*.py names this path literally"
    return producers, gaps


def _differs_from_head(root: Path, rel: str) -> bool | None:
    """Does the working-tree copy of `rel` differ from HEAD's? None when git cannot say."""
    done = _git(root, "diff", "--quiet", "HEAD", "--", rel)
    if done.returncode == 0:
        return False
    if done.returncode == 1:
        return True
    return None


def check_derived_artefacts(root: Path = PROJECT,
                            producers: dict[str, str] | None = None) -> list[dict]:
    """Has each derived artefact been regenerated since the producer that writes it last changed?

    THE WORKING TREE IS THE SUBJECT HERE, AND DELIBERATELY SO — the opposite standpoint to `check()`
    above, for a reason that is the whole point of this relation. The publisher gates the WORKING
    TREE; `check()` gates HEAD. Two trees, and only one of them can refuse a commit. A producer
    edited in place and not yet committed does not exist at HEAD, so at HEAD everything agrees while
    the publisher is refused every cycle. That is not a tuning choice, it is the defect.

    Two legs, spelled differently because they establish different things and the weaker one must
    not be read as the stronger:

      NOT_REGENERATED_SINCE_ITS_PRODUCER_CHANGED  the producer differs from HEAD and the artefact is
                                                  byte-identical to HEAD. DECIDED BY CONTENT, so a
                                                  checkout's mtime churn cannot fabricate it. RED.
      PRODUCER_NEWER_BY_CLOCK                     both differ from HEAD and the producer's mtime is
                                                  the later. Evidence, not proof — mtime is the only
                                                  ordering available once both sides are dirty.

    THE CLOCK LEG CANNOT ORDER TWO WRITES IN THE SAME KERNEL TIMESTAMP TICK, measured here rather
    than assumed: a file written and a second file written immediately after it come back with
    BYTE-IDENTICAL `st_mtime_ns` on this box, because the inode timestamp is taken from a coarse
    kernel clock and not from a fresh reading. The comparison is therefore strict (`>`), and an
    equal pair falls to `REGENERATED_AFTER_ITS_PRODUCER` — the FORGIVING side, deliberately, since
    the leg is evidence that never refuses a commit. Real instances are minutes apart (the wedge's
    were 45), so this costs nothing that matters; it is stated because a leg whose resolution
    nobody names reads as one that can order anything.

    Neither claims the artefact's CONTENT is wrong; see the module docstring. `git` failing to
    answer is `UNDECIDABLE`, never a pass.
    """
    producers = derived_artefact_producers(root)[0] if producers is None else producers
    if not producers:
        raise RegenerationCheckRefused(
            "no derived artefacts resolved to a producer — refusing to report a clean sweep over "
            "an empty set"
        )
    rows: list[dict] = []
    for artefact in sorted(producers):
        producer = producers[artefact]
        row = {"artefact": artefact, "producer": producer}
        artefact_dirty = _differs_from_head(root, artefact)
        producer_dirty = _differs_from_head(root, producer)
        if artefact_dirty is None or producer_dirty is None:
            rows.append({**row, "verdict": "UNDECIDABLE",
                         "detail": {"reason": "git could not compare one of the pair against HEAD"}})
            continue
        if not producer_dirty:
            rows.append({**row, "verdict": "PRODUCER_UNCHANGED", "detail": {}})
            continue
        if not artefact_dirty:
            rows.append({**row, "verdict": "NOT_REGENERATED_SINCE_ITS_PRODUCER_CHANGED",
                         "detail": {"remedy": f"python3 -m {producer[:-3].replace('/', '.')}"}})
            continue
        try:
            producer_mtime = (root / producer).stat().st_mtime
            artefact_mtime = (root / artefact).stat().st_mtime
        except OSError as exc:
            rows.append({**row, "verdict": "UNDECIDABLE", "detail": {"reason": str(exc)[:200]}})
            continue
        if producer_mtime > artefact_mtime:
            rows.append({**row, "verdict": "PRODUCER_NEWER_BY_CLOCK",
                         "detail": {"producer_mtime": producer_mtime,
                                    "artefact_mtime": artefact_mtime,
                                    "remedy": f"python3 -m {producer[:-3].replace('/', '.')}"}})
            continue
        rows.append({**row, "verdict": "REGENERATED_AFTER_ITS_PRODUCER", "detail": {}})
    return rows


#: The verdicts of the second relation that refuse a commit. `PRODUCER_NEWER_BY_CLOCK` is NOT here:
#: it is evidence from a clock that a `git checkout` can reorder, and this control gates the
#: publisher — the failure mode it exists to end is a red nobody can discharge.
DERIVED_RED_VERDICTS = frozenset({"NOT_REGENERATED_SINCE_ITS_PRODUCER_CHANGED"})


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
    parser.add_argument("--derived-artefacts", action="store_true",
                        help=f"the second relation: has each {DERIVED_DIR}/*.json been regenerated "
                             "since the producer that writes it changed? Working-tree standpoint, "
                             "no clone, nothing is run.")
    args = parser.parse_args(argv)

    if args.derived_artefacts:
        rows = check_derived_artefacts()
        gaps = derived_artefact_producers()[1]
        if args.json:
            print(json.dumps({"rows": rows, "gaps": gaps}, indent=1))
        else:
            for row in rows:
                print(f"{row['verdict']:<44} {row['artefact']:<52} {row['producer']}")
            counts: dict[str, int] = {}
            for row in rows:
                counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
            print("\n" + "  ".join(f"{k}={v}" for k, v in sorted(counts.items())))
            # The gaps are printed with the verdicts, never under a separate flag: an artefact this
            # walk cannot attribute is the part of the tree the control is silent about, and a
            # reader who saw only the covered rows would read that silence as coverage.
            print(f"unattributed={len(gaps)} "
                  f"(of {len(rows) + len(gaps)} artefacts in {DERIVED_DIR}/)")
        return 1 if any(r["verdict"] in DERIVED_RED_VERDICTS for r in rows) else 0

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
