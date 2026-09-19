"""The sweep can see a finding that names its own claim id, and cannot be fooled by one that
merely mentions it.

THE DEFECT. Every reading `tree_verdict` had of a closed window joined on a PATH or on a CLOCK,
and both are inferences. `_claim_paths` returns the paths the item's own prose predicted before
any work was done; `_window_attributable_paths` returns whatever anybody wrote during the same
hours. So a swept row's evidence line read *"N path(s) elsewhere in the tree hold uncommitted
bytes written INSIDE this window -- ATTRIBUTED BY TIME AND NOT BY NAME"*, and the reader was sent
to look at a list that might be another lane's entirely.

The discriminator was already in the artefacts and nothing read it: a filed finding's header
carries `**Claim id:** <id>` -- the turn saying, in the document, which claim it was working.
Exact, free, and eleven weeks of swept rows went out without it.

WHY THE FIELD FORM AND NOT A SUBSTRING, measured on the shared tree 2026-09-19 on the id this
repair was directed under. `docs/staging/WORKER_FINDING_REPEATING_ALARM_DELIVERY_LANE_STRANDED_
2026-09-18.md` names `reconcile-the-fork-and-take-the-repair-that-is-already-on-the-branch` four
times -- title, quoted alarm body, signature line -- and it is an ALARM ABOUT that claim, filed by
`background/alarm_repetition.py` *because the claim delivered nothing*. A substring reader would
publish it as evidence the work had moved. That is not a hypothetical: it is the artefact that was
in the tree on the turn this was written, and `test_a_document_that_only_MENTIONS_the_id_is_not_
evidence_the_work_moved` is it, reproduced.

WHAT THIS FILE GRADES. That the leg CAN fire, that it fires only on the field form, that a claim
with no such artefact still falls through and still sweeps, and that it did not eat the readings
that were already there.
"""

from __future__ import annotations

import os
import subprocess

import pytest

from background import delivery_lane as dl
from background import seat_continuation
from background import seat_work_in_hand as claims_mod


def _git(repo, *args):
    return subprocess.run(("git",) + args, cwd=repo, check=True,
                          capture_output=True, text=True).stdout.strip()


#: The draw instant every case below is placed around. A FIXED number, not `time.time()`: every
#: assertion here is an offset from a draw, and a fixture whose clock moves makes a failure
#: unreproducible on the second run.
DRAWN = 1_700_000_000.0

#: The id under test. Long and hyphenated like a real one, because the trailing-boundary leg below
#: is about ids that share a prefix and a short name cannot express that.
CLAIM = "the-sweep-cannot-see-a-finding-that-names-its-own-claim-id"


@pytest.fixture
def lane(tmp_path, monkeypatch):
    """A real repo plus a real ledger, with BOTH of the lane's trees pointed at it.

    Patched SEPARATELY, as the sibling file does: commits are read from `PROJECT_DIR` and
    working-tree bytes from `seat_continuation.shared_tree_dir()`. A fixture that patched one and
    let the other fall through would grade THIS machine's uncommitted state -- and this machine
    genuinely has 215 dirty artefacts under the two roots being scanned, so the leak would not be
    subtle, it would be a test that passes on somebody else's work.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    (repo / "docs" / "staging").mkdir(parents=True)
    (repo / "tools").mkdir()
    (repo / "docs" / "seed.md").write_text("seed\n")
    _git(repo, "add", "docs/seed.md")
    subprocess.run(("git", "commit", "-m", "seed"), cwd=repo, check=True,
                   capture_output=True, text=True)

    claims = tmp_path / "claims.json"
    monkeypatch.setattr(dl, "PROJECT_DIR", repo)
    monkeypatch.setattr(dl, "CLAIMS_FILE", claims)
    monkeypatch.setattr(seat_continuation, "shared_tree_dir", lambda *a, **k: repo)
    # The item's prose is the fallback path source; every row below stamps `named_paths`, so
    # nothing here reaches back into the live direction record.
    monkeypatch.setattr(dl, "_item_text", lambda fid: "")
    return repo, claims


def _row(claims, focus_id, named_paths, *, drawn=DRAWN, **extra):
    ledger_path = dl._ledger_path(claims)
    ledger = claims_mod._load(ledger_path) if ledger_path.exists() else {}
    ledger[focus_id] = {"first_drawn_at": drawn, "last_drawn_at": drawn,
                        "named_paths": list(named_paths), **extra}
    claims_mod._save(ledger, ledger_path)


def _now():
    """Long enough after the draw that every window below has closed."""
    return DRAWN + dl.CLAIM_STALE_SECONDS + 100_000


def _artefact(repo, name, body, *, when=DRAWN + 60):
    """An untracked finding under `docs/staging/`, with a placed mtime.

    The mtime is set even though the by-name leg has no time clause, precisely so that a
    regression which ADDS one is visible: `when` sits inside the window, so a mistaken
    `mtime <= window_closed` would still pass and a mistaken `drawn <= mtime` would too, while the
    deliberately-late artefact in `test_the_leg_has_no_time_clause` would not.
    """
    path = repo / "docs" / "staging" / name
    path.write_text(body)
    os.utime(path, (when, when))
    return path


#: The header a turn actually writes, wrapped the way `docs/staging/` actually wraps it: the field
#: marker ends a line and the id sits alone on the next. The commonest shape in the live tree, and
#: the one a line-by-line reader is blind to.
WRAPPED_HEADER = (
    "**Severity:** LATENT · **Lane:** H_harness\n\n"
    "# The sweep cannot see a finding that names its own claim id\n\n"
    "**Filed:** 2026-09-19 · **Claim id:**\n"
    "`{}`\n\n"
    "## What was done\n\nThe leg was written.\n"
)


# -------------------------------------------------------------------------------------------
# THE LEG CAN FIRE. Read this one first.
# -------------------------------------------------------------------------------------------

def test_an_artefact_carrying_the_claim_id_IS_read_as_the_work_having_moved(lane):
    """The row's own named paths are clean and git never saw a commit -- and the tree still says
    the work exists, because the artefact says whose it is.

    THIS IS THE LEG. Before it, this exact geometry produced STRAND_CANDIDATE at best and silence
    at worst, and the finding sitting in `docs/staging/` with the claim's id at the top of it was
    read by nothing.

    MUTATION: delete the `by_name` block in `tree_verdict`. This fires, and so does
    `test_the_leg_has_NO_time_clause_and_that_is_deliberate` -- both rest on the leg existing, and
    both were run to check it rather than reasoned about. The sibling file's partition control
    does NOT fire, which is the point of taking an existing verdict: STRANDED stays reachable by
    its other route, so nothing over there can substitute for this assertion.
    """
    repo, claims = lane
    _artefact(repo, "WORKER_RESULT_THE_LEG_FIRED_2026-09-19.md", WRAPPED_HEADER.format(CLAIM))
    _row(claims, CLAIM, ["background/delivery_lane.py"])

    verdict = dl.tree_verdict(CLAIM, now=_now(), path=claims)

    assert verdict and verdict["verdict"] == dl.STRANDED, (
        "a dirty artefact carrying this claim's id in its own header is the turn saying the work "
        "exists. If this is None or STRAND_CANDIDATE the by-name leg is dead and the lane is back "
        "to attributing by clock. Got: {}".format(verdict))
    assert verdict["paths"] == ["docs/staging/WORKER_RESULT_THE_LEG_FIRED_2026-09-19.md"], (
        "the verdict must name the ARTEFACT, which is where the bytes are -- not the path the "
        "item's prose predicted, which is what was wrong in the first place")
    assert "ATTRIBUTED BY NAME" in verdict["evidence"], (
        "the evidence line is the whole deliverable: a reader who has spent weeks being told "
        "ATTRIBUTED BY TIME will skim an identical sentence and do nothing")
    assert "ATTRIBUTED BY TIME" not in verdict["evidence"], (
        "the two attributions ask for opposite actions -- land these, versus look at those -- and "
        "a line carrying both says neither")


def test_the_named_paths_the_prose_predicted_are_still_reported_beside_the_artefact(lane):
    """The prediction is kept, because the gap between it and the artefact is the finding.

    A reader looking at why the strand was invisible needs both halves: what the item said it
    would touch, and what it actually wrote. Dropping `named_paths` would leave the verdict true
    and unexplainable.
    """
    repo, claims = lane
    _artefact(repo, "WORKER_RESULT_ELSEWHERE_2026-09-19.md", WRAPPED_HEADER.format(CLAIM))
    _row(claims, CLAIM, ["background/delivery_lane.py", "docs/design/maturity_map.yaml"])

    verdict = dl.tree_verdict(CLAIM, now=_now(), path=claims)

    assert verdict["named_paths"] == ["background/delivery_lane.py",
                                      "docs/design/maturity_map.yaml"]


# -------------------------------------------------------------------------------------------
# AND CANNOT FIRE ON A MENTION. This is the half that makes the leg worth having.
# -------------------------------------------------------------------------------------------

def test_a_document_that_only_MENTIONS_the_id_is_not_evidence_the_work_moved(lane):
    """The live alarm artefact, reproduced. It names the id four times and means the opposite.

    `background/alarm_repetition.py` files this document BECAUSE the claim landed nothing, so
    reading it as evidence the work moved would make the strand alarm silence itself the moment it
    fired -- a control that clears its own condition by existing.

    MUTATION: replace `_names_claim_in_field`'s regex with `focus_id in flat`. This fires -- and
    so does `test_an_id_that_is_a_PREFIX_of_the_field_value_does_not_match`, which is not what was
    written here before the mutation was actually run. Corrected beside the claim: a substring
    reader loses BOTH discriminations, the field-versus-mention one and the where-the-id-stops
    one, because a bare `in` has neither a left anchor nor a right boundary. Two legs firing on
    one mutation is the honest reading of one predicate doing two jobs, and it is recorded rather
    than tidied because the flattering version of this sentence was the first draft.
    """
    repo, claims = lane
    _artefact(repo, "WORKER_FINDING_REPEATING_ALARM_DELIVERY_LANE_STRANDED_2026-09-19.md",
              "**Severity:** LATENT · **Lane:** H_harness · **Atom:** `unminted`\n\n"
              "# [SEAT] {claim} was claimed, landed NOTHING, and its work is SITTING IN THE "
              "SHARED TREE\n\n"
              "**Filed automatically by `background/alarm_repetition.py`, not by a person.**\n\n"
              "```\n[SEAT] {claim} was claimed, landed NOTHING\n"
              "then `python3 -m background.delivery_lane --landed {claim}`.\n```\n\n"
              "- Signature: `delivery-lane-stranded:{claim}`\n".format(claim=CLAIM))
    _row(claims, CLAIM, ["background/delivery_lane.py"])

    verdict = dl.tree_verdict(CLAIM, now=_now(), path=claims)

    assert not (verdict and verdict["verdict"] == dl.STRANDED
                and "ATTRIBUTED BY NAME" in verdict.get("evidence", "")), (
        "an alarm ABOUT a claim is not the claim's work. Reading it by substring makes the "
        "stranding alarm extinguish itself on its second sweep. Got: {}".format(verdict))


def test_an_id_that_is_a_PREFIX_of_the_field_value_does_not_match(lane):
    """Ids here share prefixes by construction -- `_dispatch_spelling` exists because the dispatch
    capture truncates them at different points -- so a boundary-free match would credit one claim
    with a differently-stopped sibling's artefact, silently, and only ever upward.

    MUTATION: drop the `(?![\\w-])` lookahead. This fires.
    """
    repo, claims = lane
    _artefact(repo, "WORKER_RESULT_THE_LONGER_ID_2026-09-19.md",
              WRAPPED_HEADER.format(CLAIM + "-and-then-some-more-words"))
    _row(claims, CLAIM, ["background/delivery_lane.py"])

    verdict = dl.tree_verdict(CLAIM, now=_now(), path=claims)

    assert not (verdict and "ATTRIBUTED BY NAME" in verdict.get("evidence", "")), (
        "`{}` is a prefix of the field value, not the field value. Got: {}".format(CLAIM, verdict))


def test_an_artefact_carrying_ANOTHER_claims_id_is_not_read_as_this_ones(lane):
    """Several lanes file findings into `docs/staging/` every hour. A leg that answered from any
    of them would report every stale claim as delivered -- the fail-open direction, and the one
    with no symptom.
    """
    repo, claims = lane
    _artefact(repo, "WORKER_RESULT_SOMEBODY_ELSES_2026-09-19.md",
              WRAPPED_HEADER.format("a-completely-different-claim-that-another-lane-holds"))
    _row(claims, CLAIM, ["background/delivery_lane.py"])

    verdict = dl.tree_verdict(CLAIM, now=_now(), path=claims)

    assert not (verdict and "ATTRIBUTED BY NAME" in verdict.get("evidence", "")), (
        "another lane's artefact is not this claim's work. Got: {}".format(verdict))


# -------------------------------------------------------------------------------------------
# AND THE ROWS IT MUST NOT CHANGE.
# -------------------------------------------------------------------------------------------

def test_a_claim_with_NO_such_artefact_still_falls_through_and_still_sweeps(lane):
    """The other side of the partition, and the one the direction named explicitly.

    A leg that speaks for every row is a leg that discriminates nothing, and the sweep's actual
    job -- returning abandoned claims to the pool -- must survive it. Both are asserted here
    because either one alone can be satisfied by a broken reading: silence alone is satisfied by a
    leg that never fires, and a sweep alone is satisfied by a leg that fires on everything.
    """
    repo, claims = lane
    _artefact(repo, "WORKER_RESULT_UNRELATED_2026-09-19.md",
              "**Filed:** 2026-09-19\n\n# Something else entirely\n\nNo claim field at all.\n")
    _row(claims, CLAIM, ["background/delivery_lane.py"])
    claims_mod.claim(CLAIM, note="n", path=claims, now=DRAWN)

    verdict = dl.tree_verdict(CLAIM, now=_now(), path=claims)
    assert not (verdict and "ATTRIBUTED BY NAME" in verdict.get("evidence", "")), (
        "no artefact carries this id, so the by-name leg has nothing to say and must say "
        "nothing. Got: {}".format(verdict))

    swept = dl.sweep_stale(now=_now(), path=claims)
    assert CLAIM in swept, (
        "the sweep's job is returning abandoned claims to the pool, and a tree reading that "
        "stopped it doing that would be a worse defect than the one this file repairs. "
        "Got: {}".format(swept))


def test_the_leg_has_NO_time_clause_and_that_is_deliberate(lane):
    """An artefact written well after the window closed is still this claim's work.

    `_stranded_paths` needs `mtime <= window_closed` because "these paths are dirty" is true of
    the shared tree almost always and the clock is all that stands between it and a false alarm
    every sweep. Here the NAME does that work. Adding an mtime filter -- which looks like
    consistency and reads like tidying -- throws away the one property that makes this reading
    stronger than the time-attributed one it sits above.

    MUTATION: add `if mtime > window_closed: continue` to `_artefacts_naming_claim`. This fires;
    nothing else in this file does, because every other artefact here sits inside the window.
    """
    repo, claims = lane
    late = DRAWN + dl.CLAIM_STALE_SECONDS + 50_000      # long past the window AND its grace
    _artefact(repo, "WORKER_RESULT_LATE_BUT_OURS_2026-09-19.md",
              WRAPPED_HEADER.format(CLAIM), when=late)
    _row(claims, CLAIM, ["background/delivery_lane.py"])

    verdict = dl.tree_verdict(CLAIM, now=_now(), path=claims)

    assert verdict and "ATTRIBUTED BY NAME" in verdict["evidence"], (
        "the id in the header is exact whenever it was written; a time clause here would re-lose "
        "exactly the work this leg exists to find. Got: {}".format(verdict))


def test_a_landed_commit_still_outranks_the_artefact(lane):
    """Order is the guard on the strong claim. A row whose work is IN A REF is delivered, and
    telling its reader to go and land an artefact would send them to commit bytes that are
    already published.
    """
    repo, claims = lane
    _artefact(repo, "WORKER_RESULT_ALSO_PRESENT_2026-09-19.md", WRAPPED_HEADER.format(CLAIM))
    path = repo / "background" / "delivery_lane.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("landed\n")
    _git(repo, "add", "background/delivery_lane.py")
    stamp = "@{:.0f} +0000".format(DRAWN + 60)
    subprocess.run(("git", "commit", "-m", "land the repair"), cwd=repo, check=True,
                   capture_output=True, text=True,
                   env=dict(os.environ, GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp))
    _row(claims, CLAIM, ["background/delivery_lane.py"])

    verdict = dl.tree_verdict(CLAIM, now=_now(), path=claims)

    assert verdict and verdict["verdict"] == dl.CREDITED, (
        "a commit inside the window on the claim's own paths is a landing, and the by-name leg "
        "must not be able to demote it to a strand. Got: {}".format(verdict))
