"""The company's SVT drift belief may be RECORDED and GRADED. It may not yet DECIDE anything.

Pre-registration and result:
`docs/staging/WORKER_PREREGISTRATION_WHAT_THE_SVT_DRIFT_BELIEF_MUST_SHOW_2026-08-31.md`.

Measured on its first run: **0.6054 uncorrected, but 0.4691 per exposure-day, inside its null
[0.4164, 0.5834]** — while the world's own hazard on the same route clears offset at 0.6091. So
there IS per-household signal on the SVT route and this belief is not finding it. What it orders is
**how long the cap period ran**, which is the billing calendar and not a property of the customer.

WHY A CONTROL AND NOT A NOTE. A pre-registered withdrawal condition was written for this run, its
named legs fired, and its stated premise ("a wrong belief invites action") turned out not to hold
because nothing consumes the number. That is the second time in one day an argument was made for
keeping something past its own withdrawal condition, and a pattern of escaping pre-registrations on
premise failures is exactly what a pre-registration exists to prevent. **So the judgement is
replaced by a mechanism**: if anyone wires this belief to a decision while it still reads inside its
null, this reds and names the reading.

WHAT WOULD MAKE THIS CONTROL CORRECT TO DELETE: the belief clearing its null AFTER the exposure
offset. Then it discriminates households rather than calendars, and wiring it becomes a legitimate
question rather than a refused one. Deleting it for any other reason is removing the guard without
removing the cause.
"""
from __future__ import annotations

import ast
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[3]

#: The one site allowed to call it: the world records the belief beside the SVT decision, AFTER the
#: roll, so it cannot influence what happened. That recording is what makes it gradable at all.
ALLOWED_CALLERS = {
    "simulation/run_phase2b.py",
    "company/crm/churn_desk.py",
    "company/interfaces/churn_estimation.py",
}

#: Everything a company DECISION could live in. A belief reaching any of these is being acted on.
DECISION_TREES = ("company", "saas")

SYMBOLS = ("estimate_svt_drift", "SvtSegmentObservation")


def _callers_of(symbol: str) -> set[str]:
    """Every non-test file under the decision trees that names `symbol`."""
    hits = set()
    for tree in DECISION_TREES:
        for path in (PROJECT / tree).rglob("*.py"):
            if "__pycache__" in path.parts or path.name.startswith("test_"):
                continue
            try:
                source = path.read_text(encoding="utf-8")
            except OSError:
                continue
            if symbol in source:
                hits.add(str(path.relative_to(PROJECT)))
    return hits


def test_the_svt_drift_belief_is_not_wired_to_any_decision():
    """It is recorded and graded, and it reaches nothing that acts.

    MUTATION: import `estimate_svt_drift` into any pricing, retention or CRM decision module and
    this fires, naming the reading that says why it must not be there yet.
    """
    for symbol in SYMBOLS:
        callers = _callers_of(symbol)
        unexpected = callers - ALLOWED_CALLERS
        assert not unexpected, (
            f"`{symbol}` has reached {sorted(unexpected)}. The company's SVT drift belief reads "
            "0.4691 per exposure-day, INSIDE its null [0.4164, 0.5834] — it cannot be told from "
            "chance once exposure is divided out, and what it orders is how long the cap period "
            "ran. A supplier targeting on that is targeting its own billing calendar. It may be "
            "recorded and graded; it may not decide anything until it clears its null AFTER the "
            "exposure offset."
        )


def _recording_site_is_in_this_tree() -> bool:
    """Does `run_phase2b` carry the recording site yet?

    IT LANDS IN TWO HALVES AND THAT IS NOT A CHOICE. The company side of this belief is
    committable today; the SITE that records it sits in `simulation/run_phase2b.py`, on top of
    C1b's uncommitted interlock across five simulation files, which has been another lane's
    in-flight work for two days. Adopting five files of someone else's active work to ship one
    recording line is the trade that goes wrong, so the halves land separately.

    THIS IS NOT A FAIL-OPEN. The two legs below assert one of two COHERENT states -- both halves
    present, or neither -- and red on any mixture. A belief recorded by the world with no company
    function behind it, or a company function whose recording site vanished, both fire.
    """
    return "estimate_svt_drift" in (PROJECT / "simulation" / "run_phase2b.py").read_text()


def test_the_belief_IS_still_reachable__so_this_guard_cannot_pass_by_deletion():
    """The other direction, and without it the guard is satisfied by removing the belief entirely.

    A control that only forbids is green when its subject vanishes — the failure that let three of
    four mutations survive on the domain-constant gate. This is the floor under it.

    IT IMPORTS AND CALLS RATHER THAN GREPS, AND THE FIRST DRAFT DID NOT. Written as a text search
    for the symbol, this leg SURVIVED the mutation it exists for: deleting `estimate_svt_drift`
    outright left the name in this module's own section comment and docstring, so the grep still
    matched and the control read green over a belief that no longer existed. A scan that cannot
    tell a definition from a mention of one is the same defect as a citation nobody read. The
    forbidding leg above still greps — there the question genuinely is "does this name appear in a
    decision module", and prose mentioning it is worth a red too.

    MUTATION: delete the belief from `churn_desk`, or drop it from the door's `__all__`, and this
    fires.
    """
    from company.crm import churn_desk as desk
    from company.interfaces import churn_estimation as door

    for module, where in ((desk, "the desk"), (door, "the door")):
        for symbol in SYMBOLS:
            assert hasattr(module, symbol), (
                f"`{symbol}` is gone from {where} — the belief has been deleted rather than kept "
                "unwired, and 'the company forms no belief on this route' is back"
            )
            assert symbol in getattr(module, "__all__", []), (
                f"`{symbol}` is no longer exported by {where}; the door and the desk must mirror"
            )
    probe = desk.estimate_svt_drift(desk.SvtSegmentObservation(years_on_svt=0.0, segment_days=92))
    assert 0.0 < probe < 1.0, (
        f"the belief returns {probe!r} for a real segment — it has been stubbed rather than kept"
    )


def test_the_two_halves_are_COHERENT__recorded_by_the_world_iff_the_company_forms_it():
    """Both halves present, or neither. Any mixture is a defect and reds here.

    MUTATION: record `company_svt_drift_estimate` in `run_phase2b` without the company function,
    or vice versa, and this fires — which is exactly what a half-landed pair looks like.
    """
    recorder = (PROJECT / "simulation" / "run_phase2b.py").read_text()
    calls_it = "estimate_svt_drift" in recorder
    records_it = "company_svt_drift_estimate" in recorder
    assert calls_it == records_it, (
        "`run_phase2b` records the SVT drift belief without calling the company for it, or calls "
        "it without recording it. The world must not invent a company belief, and a belief nothing "
        "records cannot be graded."
    )


def test_the_belief_is_computed_AFTER_the_roll_and_cannot_seed_it():
    """The tautology that makes `build_churn_risk`'s 0.6815 unusable must not reach this one.

    `roll_lifecycle_event` seeds `effective_p_retain` from a company number and is then graded
    against the roll it seeded, which is why its capture ratio is refused. This belief is recorded
    beside the outcome instead. Asserted structurally: the call must sit after the roll is drawn.

    SKIPS ONLY WHEN THE RECORDING SITE IS ABSENT ENTIRELY, and the coherence leg above is what
    makes that safe — a tree with no recording site has no company belief in the world at all, so
    there is nothing that could seed anything. The moment the site lands, this asserts.

    MUTATION: move the `estimate_svt_drift` call above the roll and feed it into `_svt_p_depart`,
    and this fires.
    """
    if not _recording_site_is_in_this_tree():
        import pytest as _pytest
        _pytest.skip(
            "the recording site is not in this tree yet — it lands with C1b's interlock. The "
            "coherence leg above holds that the world records no SVT belief while that is true."
        )
    source = (PROJECT / "simulation" / "run_phase2b.py").read_text()
    tree = ast.parse(source)
    call_lines = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "estimate_svt_drift"
    ]
    assert call_lines, "the recording site is present but the belief is never computed"
    roll_line = next(
        i for i, line in enumerate(source.splitlines(), 1) if "_svt_roll = random.Random(" in line
    )
    hazard_line = next(
        i for i, line in enumerate(source.splitlines(), 1) if "_svt_p_depart = " in line
    )
    for lineno in call_lines:
        assert lineno > roll_line and lineno > hazard_line, (
            f"`estimate_svt_drift` is called at line {lineno}, before the roll ({roll_line}) or "
            f"the hazard ({hazard_line}). A belief computed before the outcome can seed it, and a "
            "belief graded against a roll it seeded measures the world reading back its own input."
        )
