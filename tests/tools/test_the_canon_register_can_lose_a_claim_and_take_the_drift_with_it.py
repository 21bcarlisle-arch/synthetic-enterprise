"""THE CANON REGISTER'S LOW-WATER MARK — `removed_claims()`.

THE THIRD QUESTION, asked of the claim register because it was asked of the alarm census's
register on 2026-09-05 (`dc5fcbbc8`) and the answer generalises. Every control in
`canon_drift_check` iterates `load_register(...)`, so the register IS the subject set: a claim in
it is checked, and a claim that has left is the subject of nothing.

The defect each test names is a claim that left the register itself. The sharpest leg is
`test_deleting_the_drifting_claim_no_longer_CURES_the_refusal` — the replay of the measurement
that motivated this, which was run on the live register BEFORE any of this existed: fifteen claims
with one drifting exits 1, and deleting the drifting claim exits 0 reporting "all HOLD".

WHY `test_the_live_register_membership_is_pinned_literally` (one file over) IS NOT THIS CONTROL.
It pins a LITERAL id set, so it is keyed to today's answer rather than to the property. It reds
when a claim is legitimately ADDED, and when a claim is deleted its cure is to delete the id from
the literal — a two-line diff travelling in the same commit as the deletion, asked for no reason
at all. This rung measures against HEAD and demands an authored sentence.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from background import register_low_water
from tests.tools.test_canon_drift_check import (
    CHANNEL_CLAIM,
    NO_CHANNEL_CLAIM,
    _mini_repo,
)
from tools import canon_drift_check as drift
from tools.canon_drift_check import RETIRED_SECTION, main, removed_claims, run

# ── the control itself ──


def test_a_claim_that_left_the_register_without_a_reason_is_refused():
    """The whole point. MUTATION: return [] for an id absent from `current` and this fires.

    The refusal now names its REGISTER as well as its id, because the shared mechanism this rung
    was re-pointed at on 2026-09-05 also speaks for the alarm census, the class register and the
    maturity map, and a line in a mixed report that names no register is a line a reader cannot
    act on. Asserted as both facts rather than as a `startswith` on the id: the old assertion was
    keyed to today's formatting, and the property is that the line identifies WHICH ROW OF WHICH
    REGISTER.
    """
    # 2026-09-05: the docstring above already argued for this and the code still said
    # `startswith(DEFAULT_REGISTER + ":")` -- an assertion keyed to WHERE in the sentence the
    # register is named, which goes red the day the shared mechanism reorders its own wording and
    # says nothing about whether the line is actionable. The property is that the refusal
    # identifies which row of which register; both facts, neither position.
    out = removed_claims(current={"stays"}, retired={}, baseline={"stays", "gone"})
    assert len(out) == 1
    assert drift.DEFAULT_REGISTER in out[0], f"must say WHICH register lost it: {out[0]}"
    assert "gone" in out[0], f"must name the claim that left, or nobody can act on it: {out[0]}"
    assert "was in the register at HEAD and is not in it now" in out[0]


def test_a_claim_still_in_the_register_is_not_a_removal():
    """The negative leg. Without it a control that refuses EVERYTHING passes every test above."""
    assert removed_claims(current={"stays"}, retired={}, baseline={"stays"}) == []


def test_a_claim_ADDED_since_head_is_not_a_removal():
    """Keyed to the PROPERTY, not to today's answer — the failure mode of the literal pin one file
    over, which reds when the register legitimately GROWS. A register that gains a claim is the
    canon becoming MORE watched, and a control that goes red for that is backwards."""
    assert removed_claims(current={"stays", "brand_new"}, retired={}, baseline={"stays"}) == []


def test_a_removal_is_admitted_ONLY_WHEN_retired_SAYS_WHY():
    """The leg that stops this being keyed to today's answer.

    A page genuinely withdrawn SHOULD be removable, or this control goes red precisely when the
    canon becomes more honest. The escape hatch is authored, in git, and reviewable.
    """
    assert removed_claims(
        current={"stays"},
        retired={"gone": "the page was withdrawn in abc1234; the capability is gone from the code"},
        baseline={"stays", "gone"}) == []


@pytest.mark.parametrize("reason", ["", "   ", None])
def test_an_EMPTY_OR_NULL_retired_reason_does_not_open_the_hatch(reason):
    """`str(None)` is "None", which is TRUTHY: a `_retired` entry carrying an explicit YAML null
    would satisfy a naive truth test and the mandatory-reason requirement falls open. The same slip
    was live in three rungs of the census until 2026-09-05, so this hatch is born with the
    treatment. MUTATION: drop the `or ""` and the None case survives."""
    out = removed_claims(current=set(), retired={"gone": reason}, baseline={"gone"})
    assert len(out) == 1, "an unreasoned removal must not be admitted, whatever shape the null is"


def test_an_UNESTABLISHABLE_baseline_is_a_REFUSAL_not_a_clean_result(monkeypatch):
    """`_claim_ids_at_head()` returns None, never set(), and the two are opposite claims.

    An empty set would say "HEAD's register held no claims, so nothing can have been removed" and
    report CLEAN on every tree where git is unavailable — the fail-silent shape. Demand a refusal,
    not a zero. MUTATION: make the None branch return [] and this fires.
    """
    monkeypatch.setattr(drift, "_claim_ids_at_head", lambda register: None)
    out = removed_claims(drift.REPO_ROOT / drift.DEFAULT_REGISTER, current=set(), retired={})
    assert len(out) == 1 and "could not be established" in out[0]
    assert "refusal, not a clean result" in out[0]


def test_THE_HEAD_READER_ITSELF_returns_None_and_never_an_empty_set():
    """The helper's OWN contract, driven on a real git failure rather than through a monkeypatch.

    `test_an_UNESTABLISHABLE_baseline_is_a_REFUSAL...` patches `_claim_ids_at_head` out, so it
    proves the CALLER handles None and says nothing about what the reader actually returns. Both
    legs are needed and this one was missing: mutating the reader's `return None` to `return set()`
    passed every other test in this file. An empty set is the fail-silent claim "HEAD's register
    held no claims", which reports clean on every tree where git cannot answer.

    An in-repo path that HEAD does not carry makes `git show` exit non-zero for real.
    """
    absent = drift.REPO_ROOT / "docs/design/__no_such_claim_register__.yaml"
    assert drift._claim_ids_at_head(absent) is None, (
        "a register git cannot resolve at HEAD must be UNESTABLISHABLE, never an empty baseline"
    )


def test_an_UNPARSEABLE_or_SHAPELESS_register_at_head_is_unestablishable(monkeypatch):
    """The reader's other two failure legs, which the returncode leg does not cover: HEAD's copy
    parses to something that is not a mapping with a `claims` list. Same direction — None, not an
    empty baseline that would silently admit every removal."""
    class _Proc:
        returncode = 0

        def __init__(self, stdout):
            self.stdout = stdout

    # Patched on the SHARED reader, which is where the `git show` now lives. `canon_drift_check`
    # no longer imports subprocess at all: after the 2026-09-05 convergence its head reader is a
    # named seam onto `register_low_water.keys_at_head`, and a patch aimed at the old home would
    # be an AttributeError rather than a quietly ineffective test.
    for payload in ("claims: [[[", "just a string", "claims: 7", "other_key: 1"):
        monkeypatch.setattr(register_low_water.subprocess, "run",
                            lambda *a, _p=payload, **k: _Proc(_p))
        assert drift._claim_ids_at_head(drift.REPO_ROOT / drift.DEFAULT_REGISTER) is None, (
            f"HEAD's copy {payload!r} is unusable as a baseline and must refuse, not read empty"
        )


def test_a_register_OUTSIDE_the_repo_is_NOT_APPLICABLE_rather_than_a_refusal(tmp_path):
    """NOT APPLICABLE and CANNOT ESTABLISH are different claims, and collapsing them would cost
    this rung either its teeth or its usability. A register with no committed copy — every
    `tmp_path` fixture — has no high-water mark to fall from. An IN-REPO register git cannot answer
    for is the fail-silent case and refuses above; this asserts the two branches are distinct."""
    reg = tmp_path / "register.yaml"
    reg.write_text(yaml.safe_dump({"claims": [CHANNEL_CLAIM]}), encoding="utf-8")
    assert removed_claims(reg) == []


def test_BOTH_baseline_branches_are_reachable(tmp_path, monkeypatch):
    """THE PARTITION, over the whole set rather than a leg per branch. A guard that refuses
    EVERYTHING passes every refusal test above, and a guard that refuses NOTHING passes every
    negative one; this asserts the rung can produce all three outcomes, so no single mutation can
    make one branch unreachable while the others still look exercised."""
    reg = tmp_path / "register.yaml"
    reg.write_text(yaml.safe_dump({"claims": [CHANNEL_CLAIM]}), encoding="utf-8")
    not_applicable = removed_claims(reg)
    refused = removed_claims(current=set(), retired={}, baseline={"gone"})
    admitted = removed_claims(current=set(), retired={"gone": "withdrawn, see abc1234"},
                              baseline={"gone"})
    assert not_applicable == [] and admitted == [] and refused, (
        "the rung must be able to say NOT APPLICABLE, ADMITTED and REFUSED — "
        f"got {not_applicable!r}, {admitted!r}, {refused!r}"
    )
    assert "could not be established" not in "".join(refused), (
        "the refusal here must be the REMOVAL branch, not the unestablishable-baseline branch"
    )


def test_THE_RULE_COMES_FROM_THE_SHARED_MECHANISM_AND_IS_NOT_A_LOCAL_COPY(monkeypatch):
    """CONVERGENCE, asserted rather than asked for in a comment.

    RESTORED 2026-09-05 after a merge dropped it. Two lanes converged this rung onto
    `register_low_water` twelve minutes apart (cbfb12f1b locally, 029c21452 on origin) and the
    resolution took origin's file wholesale on the belief that it was the superset. It was not:
    origin held nothing this side lacked, and this control plus the extractor's own were the
    price. The check that would have caught it is comparing the resolution against the side that
    was DROPPED, since diffing against the side you adopted proves only that you adopted it.

    Why it matters more than the count: origin's version asserts the convergence in a COMMENT.
    A comment saying "call the shared one" is an exhortation, and the next lane will not read it --
    which is precisely the shape both commits existed to remove, reproduced inside the fix for it.
    This drives the routing instead: replace the shared mechanism and the rung must speak with its
    voice. MUTATION: re-inline the loop here, keeping every other test in this file green, and this
    fires.
    """
    monkeypatch.setattr(drift.register_low_water, "removed_rows",
                        lambda **kw: [f"SHARED SPOKE for {sorted(kw['baseline'] - set(kw['current']))}"])
    out = removed_claims(current={"stays"}, retired={}, baseline={"stays", "gone"})
    assert out == ["SHARED SPOKE for ['gone']"], (
        "the low-water rule must reach this register through `register_low_water.removed_rows`, "
        "not through a fourth hand-rolled copy of it"
    )


# ── the replay: what motivated the rung ──


def test_deleting_the_drifting_claim_no_longer_CURES_the_refusal(tmp_path):
    """THE MEASUREMENT, REPLAYED. Every verdict this register produces is a refusal ON A ROW, and
    `main()` exits non-zero for it — so before this rung, deleting the row cleared its own refusal.
    A red clearable by deleting the evidence is a fail-open with an extra step.

    MUTATION: give `removed_claims` the tempting "allow it if the page is gone or the anchor no
    longer resolves anyway" exception and this fires — which is exactly why it is not there.
    """
    # A register whose second claim DRIFTS: the page says green_stance is read by nothing, and the
    # mini repo gives it a reader.
    root, reg = _mini_repo(tmp_path, green_channel=True,
                           claims=[CHANNEL_CLAIM, NO_CHANNEL_CLAIM])
    verdicts, report = run(root, reg)
    assert [d["id"] for d in report["drift"]] == ["no_channel"], "the fixture must actually drift"

    # Now delete the drifting claim — the cure that used to work.
    reg.write_text(yaml.safe_dump({"claims": [CHANNEL_CLAIM]}), encoding="utf-8")
    _, cured = run(root, reg)
    assert cured["drift"] == [] and cured["claims_checked"] == 1, (
        "deleting the row must still clear the DRIFT verdicts — that is the defect, not a bug"
    )

    # ...and the removal rung picks the subject straight back up.
    assert removed_claims(reg, current={"channel_exists"}, retired={},
                          baseline={"channel_exists", "no_channel"}), (
        "claim-deletion must not be a route out of the drift refusal"
    )


def test_the_note_names_a_REMOVAL_rather_than_reporting_ALL_HOLD(monkeypatch):
    """The sentence this rung exists to stop being printed. A removed claim cannot appear in
    `drift` — there is no row left to give a verdict to — so a naive note reports the survivors
    "all HOLD" beside a silent loss. MUTATION: drop the `removed` branch from `note_line` and this
    fires on the reassuring sentence."""
    monkeypatch.setattr(drift, "removed_claims",
                        lambda *a, **k: ["C1_gone -- this claim was in the register at HEAD"])
    line = drift.note_line(write_report=False)
    assert "LEFT the register" in line and "C1_gone" in line
    assert "all HOLD" not in line, "a removal must not be reported as a clean canon"


# ── wiring and the live tree ──


def test_the_removal_check_is_WIRED_INTO_the_exit_code(tmp_path, monkeypatch, capsys):
    """MUTATION-PROVED IS NOT WIRED. The function can be perfect and never consulted; this drives
    `main()` on a register where NOTHING ELSE is wrong and asserts the exit code and the banner."""
    root, reg = _mini_repo(tmp_path, claims=[CHANNEL_CLAIM])
    monkeypatch.setattr(drift, "removed_claims",
                        lambda *a, **k: ["no_channel -- this claim was in the register at HEAD"])
    code = main(["--root", str(root), "--register", str(reg)])
    out = capsys.readouterr().out
    assert "0 drifting" in out, "nothing but the removal may be wrong in this fixture"
    assert code == 1, "a claim that left must fail the check exactly as a claim that drifted does"
    assert "CLAIMS THAT LEFT THE REGISTER" in out and "no_channel" in out


def _is_a_git_tree() -> bool:
    """Whether this checkout is a repository at all — NOT whether the rung likes what it finds.

    Read from the filesystem rather than from the rung's own output, which would be the tautology
    of asking the control whether the control should apply. `.git` is a directory in a normal
    checkout and a FILE in a linked worktree; both are repositories and both must take the
    asserting branch below.
    """
    return (drift.REPO_ROOT / ".git").exists()


def test_the_live_register_has_lost_no_claim_since_head():
    """The live rung, against the real tree and the real git baseline. This is the leg that would
    have gone red on the commit that dropped a claim.

    BOTH ENVIRONMENTS ARE ASSERTED, and it is not a skip. This project proves a red is
    pre-existing by running a `git archive HEAD` extract, which is a tarball with no `.git` — so a
    test that simply failed there would be a trap for exactly the technique used to diagnose
    traps, and a `skipif` would be a fail-open that reports nothing in the environment it skips.
    The rung's own NOT-APPLICABLE / CANNOT-ESTABLISH split already names the distinction: with no
    repository there is no committed baseline, and the honest answer is the refusal, not silence.
    """
    if not _is_a_git_tree():
        out = removed_claims()
        assert out and "could not be established" in out[0], (
            "outside a repository the rung must REFUSE, naming itself — never report clean"
        )
        return
    assert removed_claims() == [], (
        "a claim has left docs/design/canon_claims.yaml since HEAD without a `"
        + RETIRED_SECTION + "` reason"
    )


def test_the_live_report_carries_the_removal_key():
    """The report is what the daily note and any later reader consume; a rung absent from it is a
    rung nobody downstream can see. Asserted in both environments for the reason above — the KEY
    must be present either way, and only its contents depend on there being a baseline."""
    _, report = run(drift.REPO_ROOT, drift.REPO_ROOT / drift.DEFAULT_REGISTER)
    assert "removed" in report, "the rung must reach the report even when it cannot answer"
    if not _is_a_git_tree():
        assert report["removed"] and "could not be established" in report["removed"][0]
        return
    assert report["removed"] == []
