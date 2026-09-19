#!/usr/bin/env python3
"""A generator's provenance stamp must describe the bytes it READ, not where the tree stood.

THE DEFECT, measured 2026-09-19 and recorded in
`docs/staging/SEAT_RESULT_A_FEEDS_GIT_STAMP_IS_NOT_A_DESCRIPTION_OF_WHAT_PRODUCED_IT_SO_NO_STANDPOINT_REPRODUCES_IT_2026-09-19.md`.

`generate_capabilities_door` stamped `git rev-parse HEAD` into `git_commit` and then read
`site/data/customers.json` off the WORKING TREE. In this shared tree several lanes hold dirty
copies at any moment, so the two describe different states of the world. Standing in a clone
checked out at `be7311e35` — the commit the published feed itself names — and regenerating:

    DIVERGES_AT_ITS_OWN_COMMIT  capabilities_door.json  at be7311e35
        /scale/figures[0]/as_of | 2026-09-19T06:53:33Z -> 2026-09-19T04:39:13Z

`git_commit` came right. `as_of` did not, and could not: the published feed read a
`customers.json` NEWER than `be7311e35` ever committed. **There is no commit to stand at that
describes those inputs, because the inputs were never a commit.** The feed asserted its own
provenance falsely, in the one field a reader would trust to settle exactly that question.

This is the same class as `tests/tools/test_the_published_provenance_names_the_run_not_the_generator.py`
(`meta.git_commit` named the commit the GENERATOR ran at, not the one the RUN did) and
`tests/tools/test_published_provenance_is_real.py` (`git_commit: "latest"`). Each time, a real
value belonging to a DIFFERENT thing satisfied every presence check that existed. A sha is not a
referent either, if it refers to a state nobody read.

WHAT THIS MODULE SAYS INSTEAD, AND WHY IT IS ONE SENTENCE AND NOT A SHA. The honest question a
reader of a feed wants settled is not *"what was HEAD"* — it is:

    **If I stood at this commit and read these inputs, would I get the bytes this generator got?**

So the stamp carries the commit AND that answer, measured rather than assumed, with the paths that
make it `false` named on the face of it. A generator publishing from a dirty tree is not stopped
and is not lied about: it records `inputs_are_the_committed_bytes: false` and names which input
moved. A reader — and `published_feed_regeneration_check.check_at_its_own_commit` — can then refuse
by a named reason instead of standing at a commit that was never going to reproduce and calling the
result a divergence.

THE KEY IS RESERVED, AND THAT IS THE POINT, NOT DECORATION. `recorded_publication_commit` observes
a feed's standpoint from its bytes by scanning every scalar for a commit of this repository, and
refuses when it finds more than one — `value_arms.json` carries fifteen, and they are its SUBJECT
(which tree each floor leg ran on), not its standpoint. One reserved key is what lets a feed say
which of its shas is the standpoint without anybody maintaining a per-feed table. A feed that also
keeps a legacy short sha elsewhere would otherwise read as TWO commits and lose its standpoint
entirely — so the reserved key is consulted FIRST and short-circuits the scan.

FAIL-CLOSED, IN THE TWO PLACES IT MATTERS:

  * `stamp([])` RAISES. A stamp over no inputs would answer `inputs_are_the_committed_bytes: true`
    vacuously — the catalogued shape where a control's own filters empty the evidence set and the
    guard reads empty as no complaint. A stamp with nothing to describe is not a weak stamp, it is
    a fail-open, so it is refused at the producer.
  * git unreachable or HEAD unresolvable gives `commit: None` and
    `inputs_are_the_committed_bytes: None` — "we cannot tell", never `true`, and never the silent
    `None` that collapses into the flattering branch: `reason` always names which it is.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Iterable

PROJECT = Path(__file__).resolve().parent.parent

#: THE ONE KEY a generated feed records its publication standpoint under. Reserved: a sha anywhere
#: else in a feed is its subject, not its standpoint. Consulted first by
#: `published_feed_regeneration_check.recorded_publication_commit`.
STAMP_KEY = "published_from"

#: The per-input verdicts. The question each answers is the SAME one — would reading this path at
#: `commit` give the bytes the generator got — so the two "both absent" and "byte-identical" cases
#: are reproducible and the other three are not. Spelling them separately rather than as a bool is
#: what lets a reader see WHY, and what stops "absent from a feed that tolerates absence" being
#: read as a defect.
COMMITTED = "committed"                       # reproducible: working bytes == blob at the commit
ABSENT_AT_BOTH = "absent_at_both"             # reproducible: nothing read, nothing committed
MODIFIED = "modified"                         # tracked at the commit, working bytes differ
NOT_IN_THE_COMMIT = "not_in_the_commit"       # read from disk, no blob at the commit
DELETED_SINCE_THE_COMMIT = "deleted_since_the_commit"  # committed there, absent on disk now

#: The states under which standing at `commit` and reading the input reproduces what was read.
REPRODUCIBLE_STATES = frozenset({COMMITTED, ABSENT_AT_BOTH})


class ProvenanceStampRefused(ValueError):
    """A stamp that could not honestly be made. Never a stamp that quietly describes nothing."""


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *args],
                          capture_output=True, timeout=30)


def head_commit(root: Path = PROJECT) -> str | None:
    """The full 40-hex commit this tree stands at, or None if git cannot say.

    None rather than the literal `"unknown"` that two earlier provenance defects shipped: a string
    satisfies every presence check a caller might write, and `None` cannot.

    THE SHAPE CHECK BELOW IS AN EQUIVALENCE, NOT A MISSING TEST, and it is recorded rather than
    left to the reader. Mutation-tested 2026-09-19: replacing its `None` with `"unknown"` is caught
    by no leg of `test_a_generators_stamp_describes_the_bytes_it_read`. That is because no real git
    state reaches it — `rev-parse HEAD` in a repository with no commits, or outside one, exits
    non-zero and returns above; when it exits zero the output is always 40 hex. It is kept as a
    shape guard against a spoofed or corrupted `git` on PATH, and it is deliberately not given a
    test that would have to shim `git` to reach it.
    """
    try:
        out = _git(root, "rev-parse", "HEAD")
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    sha = out.stdout.decode("utf-8", "replace").strip()
    return sha if len(sha) == 40 and all(c in "0123456789abcdef" for c in sha) else None


def tree_was_clean(root: Path = PROJECT) -> bool | None:
    """Did EVERY path in this tree match the commit — not only the inputs a generator named?

    WHY BOTH QUESTIONS, AND WHY THIS ONE IS THE SUFFICIENT ONE. A declared input list is a
    diagnostic: it says WHICH input moved, which is what a reader needs to act. It is not a
    complete account of what a generator read, and enumerating one would go stale silently —
    `generate_capabilities_door.wall_position` shells out to a register that walks the whole of
    `company/`, and `generate_evidence_data` counts `def test_` across every test file. Neither is
    a fixed list of paths and neither ever will be.

    So the complete answer is the coarse one: if nothing in the tree differed from the commit,
    then nothing the generator could possibly have read differed from it either. `None` when git
    cannot say — never `True`. Measured 14ms on this ~400MB tree, so asking it costs nothing.

    Untracked files count as dirty ON PURPOSE. A new, uncommitted test file is invisible to a
    tracked-only diff and moves `generate_evidence_data`'s `def test_` count all the same.
    """
    try:
        out = _git(root, "status", "--porcelain", "--untracked-files=normal")
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return not out.stdout.decode("utf-8", "replace").strip()


def _blob_at(root: Path, commit: str, rel: str) -> bytes | None:
    """The committed bytes of `rel` at `commit`, or None if the commit has no such file."""
    try:
        out = _git(root, "cat-file", "blob", f"{commit}:{rel}")
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout if out.returncode == 0 else None


def input_state(path: Path, commit: str, root: Path = PROJECT) -> str:
    """Would reading `path` at `commit` give the bytes on disk now? One of the five states above.

    A path OUTSIDE the repository — which `generate_evidence_data`'s redirectable sources become
    under a `tmp_path` test — is `not_in_the_commit`, via `_rel`'s fallback and `cat-file` finding
    no blob. That is the honest answer, not an error: a source the commit does not contain is a
    source standing at the commit would not reproduce. An earlier draft raised `ValueError` here
    and reddened six unrelated tests that redirect a source into `tmp_path`.
    """
    committed = _blob_at(root, commit, _rel(path, root))
    try:
        on_disk: bytes | None = Path(path).read_bytes()
    except OSError:
        on_disk = None
    if on_disk is None:
        return ABSENT_AT_BOTH if committed is None else DELETED_SINCE_THE_COMMIT
    if committed is None:
        return NOT_IN_THE_COMMIT
    return COMMITTED if committed == on_disk else MODIFIED


def stamp(inputs: Iterable[Path | str], root: Path = PROJECT) -> dict:
    """The provenance block a generator publishes under `STAMP_KEY`.

    `inputs` are the paths the generator ACTUALLY READ — not everything it might have. Passing
    none is refused rather than answered, because an empty input set makes the answer vacuously
    flattering.

    The returned block is the whole claim and carries its own qualification, so a reader never has
    to go elsewhere to learn whether the commit describes the run:

        {"commit": <40-hex or None>,
         "tree_was_clean": True | False | None,
         "inputs_are_the_committed_bytes": True | False | None,
         "inputs": [{"path": "site/data/customers.json", "state": "modified"}, ...],
         "reason": "<always named>"}
    """
    paths = [Path(p) for p in inputs]
    if not paths:
        raise ProvenanceStampRefused(
            "a provenance stamp over no inputs describes nothing and would answer "
            "inputs_are_the_committed_bytes=true vacuously — name the paths the generator read"
        )
    commit = head_commit(root)
    if commit is None:
        return {
            "commit": None,
            "tree_was_clean": None,
            "inputs_are_the_committed_bytes": None,
            "inputs": [{"path": _rel(p, root), "state": None} for p in paths],
            "reason": "git could not resolve HEAD here, so there is no standpoint to compare the "
                      "inputs against and whether they were the committed bytes cannot be told",
        }
    rows = [{"path": _rel(p, root), "state": input_state(p, commit, root)} for p in paths]
    moved = [r["path"] for r in rows if r["state"] not in REPRODUCIBLE_STATES]
    clean = tree_was_clean(root)
    if moved:
        reason = ("read off the working tree, not out of this commit: " + ", ".join(sorted(moved))
                  + " — standing at this commit will not reproduce this feed")
    elif clean is False:
        reason = ("every input named here matches this commit, but the tree carried other "
                  "uncommitted changes, and this generator reads more than the paths it names — "
                  "so standing at this commit may still not reproduce this feed")
    elif clean is None:
        reason = ("every input named here matches this commit; whether the rest of the tree did "
                  "could not be established")
    else:
        reason = "every input read here is byte-identical to what this commit holds, and nothing "\
                 "else in the tree differed from it either"
    return {
        "commit": commit,
        "tree_was_clean": clean,
        "inputs_are_the_committed_bytes": not moved,
        "inputs": rows,
        "reason": reason,
    }


def _rel(path: Path, root: Path) -> str:
    try:
        return str(Path(path).resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def describes_its_inputs(block) -> bool:
    """Does this stamp claim the commit describes what was read? False for anything malformed.

    BOTH halves are required, and the coarse one is why. The named-input list is a diagnostic and
    is never a complete account of what a generator read (see `tree_was_clean`), so a caller that
    asked only `inputs_are_the_committed_bytes` would be told "yes, reproducible" by a stamp whose
    tree held an uncommitted change to something the list does not name. That is the exact shape
    this module exists for, one level up.

    The only place a caller should ask the question, so that a missing key, a `None` and an
    explicit `false` cannot be told apart by accident in three different callers' `.get()` chains.
    """
    return (isinstance(block, dict)
            and block.get("inputs_are_the_committed_bytes") is True
            and block.get("tree_was_clean") is True)
