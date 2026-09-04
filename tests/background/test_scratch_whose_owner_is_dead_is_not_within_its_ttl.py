"""A TTL cannot bound scratch whose maker died in the first hour.

2026-09-04, and it is the same shape as `test_an_empty_git_dir_made_scratch_immortal` one rule
along. `/tmp` — a 12 GB **tmpfs, which on this box is RAM** — held ~3.2 GB of abandoned 288 MB
`git archive HEAD` extracts from finished seat turns. The DISK CRITICAL alarm had fired at 383 MB
free against a 2,048 MB floor and said it *"needs a person"*. A person freed 2.0 GB by hand
(83% -> 66%). The reaper had already run, and its verdict was:

    "reaped": "nothing reapable (all scratch in use or within TTL)"

True, and useless. The extracts carry no `.git`, sit in no process's cwd, and are **younger than
the 6 h `REPO_COPY_TTL`** — measured at 0.7 h, 1.4 h, 2.8 h and 3.9 h. The TTL is a proxy for
*"a probe that is still running is not abandoned"*, calibrated against a multi-hour KNIFE or EP6
lane; a seat turn's comparison stem is dead within the hour and the proxy has no way to know.

So where the maker is RECORDED, ask whether it is alive instead of waiting out the proxy. The only
record is the directory name, and the rule ONLY EVER ADDS reapability — `test_the_change_is_monotone`
pins that, because a rule that started SPARING things would quietly undo the repair above it.

WHAT IT DOES NOT REACH is asserted here too (`test_an_anonymous_extract_still_waits_out_its_ttl`),
because a silent cap reads as coverage: three of the four measured extracts record no owner at all.
"""
from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

import pytest

# `_repo_copy` is REUSED, not re-fixtured: this is the sibling control over the same function, and
# the cross-module test import is this repo's own idiom (`tests.simulation.test_premise_trace`,
# `tests.system.chains`). Two builders of a fake repo copy would drift, and the one that drifted
# would be the one proving my own change.
from background import disk_headroom as dh
from tests.background.test_an_empty_git_dir_made_scratch_immortal import _repo_copy

YOUNG = 1 * 3600          # comfortably INSIDE REPO_COPY_TTL (6 h) -- the whole point
OLD = 200 * 3600


def _a_dead_pid() -> int:
    """A pid that is certainly not running. Searched, never assumed: a hard-coded number is one
    `fork` away from being a live process and this test's whole subject is that distinction."""
    for candidate in range(4_000_000, 3_000_000, -7):
        if candidate <= dh._pid_max() and not Path(f"/proc/{candidate}").exists():
            return candidate
    pytest.skip("no dead pid could be established on this box")


def _victims(root: Path) -> dict[str, str]:
    """name -> the reason the reaper gives for taking it."""
    return {Path(v["path"]).name: v.get("reason", "")
            for v in dh.repo_copy_scratch(roots=(root,), project_dir=root / "nope")}


# ── THE DEFECT ──────────────────────────────────────────────────────────────────────────────
def test_a_young_extract_whose_owner_is_dead_is_reapable(tmp_path):
    """THE LIVE DEFECT: 288 MB, 1 h old, maker gone, and the reaper said it had nothing to do.

    MUTATION: restore the bare `if age < REPO_COPY_TTL: continue` and this fails.
    """
    dead = _repo_copy(tmp_path, f"bisect_daemon_{_a_dead_pid()}", age_s=YOUNG)

    victims = _victims(tmp_path)
    assert dead.name in victims, (
        "scratch whose owning pid is dead is still being spared as 'within TTL' -- this is the "
        "3.2 GB of RAM that needed a person")
    assert victims[dead.name].startswith("dead-owner"), (
        "the receipt does not say WHICH rule took it, so a reader cannot tell the new rule from "
        f"the TTL: {victims[dead.name]}")


# ── THE NULL CONTROLS: what must STILL be spared ────────────────────────────────────────────
def test_an_anonymous_extract_still_waits_out_its_ttl(tmp_path):
    """REACHABILITY, and the honest bound. A fix that simply reaped young scratch would pass the
    test above and delete a live lane's work; this is what stops it.

    It also states the residue in an assertion rather than a comment: `headext`, `headx` and
    `prereg_3d36` — ~865 MB of the measured population — record no owner and are NOT covered.
    """
    for name in ("headext", "headx", "prereg_3d36"):
        _repo_copy(tmp_path, name, age_s=YOUNG)

    assert _victims(tmp_path) == {}, (
        "a directory recording no owner was reaped inside its TTL -- the rule is reaping by AGE, "
        "not by death")


def test_a_trailing_number_that_cannot_be_a_pid_is_not_an_owner_claim(tmp_path):
    """Keyed to the kernel's `pid_max`, so the bound is the system's and not one I chose."""
    _repo_copy(tmp_path, f"run-{dh._pid_max() + 1}", age_s=YOUNG)
    _repo_copy(tmp_path, "split-repro10", age_s=YOUNG)      # `10` is not a suffix, it is the name

    assert _victims(tmp_path) == {}


def test_a_live_owner_spares_its_scratch(tmp_path):
    """The recycled-pid direction, which must fail SAFE: alive spares."""
    _repo_copy(tmp_path, f"seat-extract-{os.getpid()}", age_s=YOUNG)
    assert _victims(tmp_path) == {}


def test_a_dead_owner_does_not_override_the_git_exclusion(tmp_path):
    """The exclusions ABOVE this rule still run first. A dead maker says nothing about whether the
    directory holds committed work that exists nowhere else -- and that exclusion, unlike the TTL,
    is protecting something irreplaceable."""
    holds_work = _repo_copy(tmp_path, f"lane-tree-{_a_dead_pid()}", age_s=YOUNG)
    subprocess.run(["git", "init", "-q", str(holds_work)], check=True, capture_output=True)
    (holds_work / "f.txt").write_text("uncommitted work that exists nowhere else")
    subprocess.run(["git", "-C", str(holds_work), "add", "f.txt"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(holds_work), "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-qm", "x"], check=True, capture_output=True)
    stamp = time.time() - YOUNG
    os.utime(holds_work, (stamp, stamp))

    assert _victims(tmp_path) == {}, "a dead owner overrode the exclusion that protects real work"


def test_the_change_is_monotone_and_both_reasons_are_attainable(tmp_path):
    """ONE control over the whole partition. Everything reapable BEFORE is still reapable, the new
    rule adds a second population, and the receipt tells them apart -- so neither rule can be
    silently swallowing the other."""
    past_ttl = _repo_copy(tmp_path, "wouldbe", age_s=OLD)
    dead_young = _repo_copy(tmp_path, f"extract-{_a_dead_pid()}", age_s=YOUNG)
    spared = _repo_copy(tmp_path, "headext", age_s=YOUNG)

    victims = _victims(tmp_path)
    assert victims.get(past_ttl.name) == "past-ttl", "the pre-existing TTL rule stopped firing"
    assert victims.get(dead_young.name, "").startswith("dead-owner")
    assert spared.name not in victims
    assert len(victims) == 2
