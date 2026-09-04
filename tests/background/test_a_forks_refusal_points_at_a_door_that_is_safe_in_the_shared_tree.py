"""THE DEFECT: the publish path refused a real fork and told its reader to run, in the SHARED
TREE, the one act every module around it argues is unsafe there.

The refusal's remedy line read *"Reconcile first: `python3 -m tools.surgical_land --merge
origin/main`"* -- and `_divergence_refusal`'s own docstring, four lines above the string, gives the
reason that is wrong: *"there are routinely three lanes with uncommitted work in this tree. A
daemon that merged unattended would be deciding, every twelve minutes, to move other people's
work."* A `surgical_land --merge` run in the shared tree opens the shared index and does exactly
that. The refusal declined to do it automatically **for a reason that does not stop being true
when a person types it**, and then named it as the remedy.

It was written before `background/origin_reconcile` existed. That module solved the same problem by
doing the gated merge in an ISOLATED worktree -- *"a throwaway worktree has its OWN index, so the
two objections dissolve rather than being overridden"* -- and the refusal never moved. Nothing
opened the claim: `grep` over `tests/` for the remedy string returned nothing before this file, so
a refusal that had made a checkable claim was never checked.

MEASURED 2026-09-04, delivery seat, and the numbers are why this is a WORDING fix and not a
mechanism one (`SEAT_FINDING_THE_PUBLISHER_MEETS_A_REAL_FORK...`): over 659 deadman
`ORIGIN FORK` verdicts the reconciler stood down for the gate on 27.6% of passes and reached the
real-fork branch 47 times, closing 41 of them unaided. The fork HAS an owner and the owner works.
What was broken was the refusal's account of who that owner is.

WHAT IS ASSERTED HERE, and it is keyed to the PROPERTY, not to today's wording: no refusal the
publish path produces may send a reader to a bare shared-tree merge. Naming `surgical_land --merge`
is allowed only alongside the door that runs it in isolation, so this control survives a rewrite of
every sentence and fires on a revert to the old one.
"""
from __future__ import annotations

import pytest

from background import process_run_complete as prc

#: The act that opens the SHARED index. Matched as a substring because the hazard is the
#: instruction, however it is spelled around it.
SHARED_TREE_MERGE = "surgical_land --merge"

#: The door that does the same merge with its own index. Either spelling counts: the module path
#: is what a reader runs, the word is what a reader understands.
ISOLATED_DOOR = ("origin_reconcile", "isolated")


def _names_a_safe_door(text: str) -> bool:
    """Does this refusal avoid sending a reader to a bare shared-tree merge?

    True when it never mentions the shared-tree merge at all, or mentions it alongside the
    isolated door. The question is asked of the WHOLE string deliberately -- a refusal that names
    the hazard in one sentence and the door in the next is fine; one that names only the hazard
    is the defect.
    """
    if SHARED_TREE_MERGE not in text:
        return True
    return any(marker in text for marker in ISOLATED_DOOR)


def _divergence_reasons(monkeypatch) -> dict:
    """Every string `_divergence_refusal` can produce, across its whole partition."""
    out = {}
    for label, ahead in (("level", 0), ("unreadable", None), ("behind", 3)):
        monkeypatch.setattr(prc, "_commits_origin_is_ahead_by", lambda _a=ahead: _a)
        out[label] = prc._divergence_refusal()
    return out


def _real_fork_reason() -> str:
    """The `ahead > 0` branch of the advance -- the one the direction asked to be decided.

    Injected through the function's own seams. The fetch is stubbed to SUCCEED so the branch under
    test is reached: a stub that failed would return the fetch refusal and this control would pass
    while never seeing the real-fork string at all.
    """
    def runner(argv, timeout):
        assert argv[:2] == ["git", "fetch"], argv
        return type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    result = prc._advance_to_origin_or_say_why(ahead_fn=lambda _p: 2, runner=runner)
    assert result["advanced"] is False, "a tree holding its own commits must never be advanced"
    return result["reason"]


def test_the_partition_is_reachable_before_anything_is_asserted_about_it(monkeypatch):
    """THE NULL CONTROL, and it is first on purpose.

    Every assertion below is of the form "this string does not say X". A function that returned
    the empty string, or one whose branches had become unreachable, would satisfy all of them --
    which is this project's most-repeated way of shipping a control that cannot fail. So: assert
    the partition is genuinely three DIFFERENT answers, and that the real-fork branch is reachable
    at all, before asking what any of them says.
    """
    reasons = _divergence_reasons(monkeypatch)
    assert reasons["level"] is None, "a level tree must not be refused"
    assert reasons["unreadable"] and reasons["behind"], "both refusals must produce a reason"
    assert reasons["unreadable"] != reasons["behind"], (
        "an unreadable origin and a real fork are different states and a reader is sent to "
        "different places -- one string for both is the defect this project keeps re-finding"
    )
    assert "REAL" in _real_fork_reason(), "the ahead>0 branch was never reached"


@pytest.mark.parametrize("leg", ["unreadable", "behind"])
def test_no_divergence_refusal_sends_a_reader_to_a_bare_shared_tree_merge(monkeypatch, leg):
    """THE DEFECT ITSELF. Reverting the remedy line to `surgical_land --merge origin/main` alone
    fires this."""
    reason = _divergence_reasons(monkeypatch)[leg]
    assert _names_a_safe_door(reason), (
        "this refusal names the shared-tree merge without the isolated door that makes it safe; "
        "the reason it refuses to merge automatically is that other lanes hold uncommitted work "
        "in this tree, and that does not stop being true when a person types the command:\n"
        + reason
    )


def test_the_real_fork_refusal_names_the_owner_that_actually_closes_it():
    """A refusal for a state something else OWNS must say so, or it reads as a call to action.

    Measured: the reconciler closed 41 real forks unaided. A refusal that names no owner sends a
    reader to reconcile by hand a fork that a daemon was already closing.
    """
    reason = _real_fork_reason()
    assert _names_a_safe_door(reason), reason
    assert "origin_reconcile" in reason, (
        "the real-fork branch must name the module that owns this state:\n" + reason
    )


def test_the_property_holds_over_every_refusal_the_publish_path_can_emit(monkeypatch):
    """ONE CONTROL OVER THE WHOLE SURFACE, so a refusal added later is covered without a new leg.

    The per-leg tests above say which string broke; this says the rule holds everywhere, and is
    what stops the next branch from reintroducing the defect somewhere neither leg looks.
    """
    every = [r for r in _divergence_reasons(monkeypatch).values() if r] + [_real_fork_reason()]
    assert len(every) == 3, "the surface changed shape -- re-derive what this control covers"
    offenders = [r for r in every if not _names_a_safe_door(r)]
    assert not offenders, "refusal(s) pointing at a bare shared-tree merge:\n" + "\n--\n".join(
        offenders
    )
