#!/usr/bin/env python3
"""R15 proof for class debt — the register's cost, and what it buys in the draw.

Director, 2026-09-01: *"Each class register carries a cumulative cost and nothing reads it.
Wire it in ... A class with eight instances and hours of outage each is a debt that should beat
new features until it's closed."*

THE MUTATIONS THAT MATTER HERE ARE NOT "does it add up". They are the two directions in which
this mechanism becomes worse than not having it:

  1. THE REGISTERS TAKE THE HEAD OF THE DRAW AND NEVER LEAVE. That is the exact state the
     2026-08-28 room migration was built to end (six standing documents that can never drain,
     sorted ahead of the director's guidance). If a decision does not remove a register from
     the queue, this change has re-created it with extra steps.
  2. A DECISION BECOMES A SILENCER. An `ACCEPTED` that cannot be overtaken by evidence, or a
     `CLOSED` naming a mechanism that no longer exists, turns a class off permanently while
     reading as handled. That is `controls_that_cannot_fail` committed by the channel that
     switches those very controls off, which is the one place this project cannot afford it.

Plus the measured false positives that shaped the cost extractor: the wide net was run over
the whole corpus and accepted seven wrong figures, and those exact sentences are pinned below
so a later widening has to defeat them on purpose.
"""
from __future__ import annotations

import datetime as dt

import pytest

from background import class_debt as cd
from background import staging_rooms as sr

TODAY = dt.date(2026, 9, 1)

#: A real register name, so a rename of the class breaks this file rather than silently
#: testing a document that no longer exists.
REGISTER = "CLASS_NO_CALLER_AND_NEVER_RUNS_2026-08-12.md"
HEADER = "**Severity:** LATENT · **Lane:** H_harness\n"


def _instance(root, name, body=""):
    """One live finding that classifies into `no_caller_and_never_runs` by its title."""
    path = root / name
    path.write_text(
        f"# [WORKER FINDING] {name.replace('_', ' ')}\n\n{HEADER}\n{body}\n",
        encoding="utf-8",
    )
    return path


def _register(root, disposition="", listed=()):
    path = root / REGISTER
    lines = [
        "# [CLASS] No caller, never runs",
        "",
        HEADER,
        "**Instances:** %d · **Class:** `no_caller_and_never_runs`" % len(listed),
        "",
        "## The instances",
        "",
    ]
    lines += [f"- `{name}` — LATENT" for name in listed]
    lines += ["", disposition, ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _accruing(root, n=3, day=30):
    """`n` instances inside the accrual window, which is what makes a class drawable."""
    for i in range(n):
        _instance(root, f"WORKER_FINDING_A_CONTROL_HAS_NO_CALLER_{i}_2026-08-{day:02d}.md")


def _debt(root, class_id="no_caller_and_never_runs"):
    return next(d for d in cd.compute(root, today=TODAY) if d.class_id == class_id)


# ---------------------------------------------------------------------------
# THE COST EXTRACTOR — T2, and the seven measured false positives
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("sentence,days", [
    ("the front door's machine claim was false for six days", 6.0),
    ("the publish path served a frozen artefact for four days", 4.0),
    ("`resource_headroom` sat unwired for nine days after being built", 9.0),
    ("the code/artefact gap was unguarded again for five days", 5.0),
    ("publishing stayed wedged for 31 hours", 31 / 24),
])
def test_a_span_something_stayed_wrong_for_is_a_cost(sentence, days):
    """The true positives, verbatim from the corpus. Each says a WRONG STATE persisted, which
    is the director's "it invalidates whatever was built on top of it in between"."""
    spans = cd.persisted_spans(sentence, "x.md")
    assert spans, f"missed a real cost: {sentence!r}"
    assert spans[0].days == pytest.approx(days, rel=1e-3)


@pytest.mark.parametrize("sentence", [
    # A RECURRENCE RATE. Four of these are in the publish-gate class and the wide net billed
    # every one of them as damage.
    "it is the fifth instance of the mechanism in three days",
    "built 2026-08-10 after three instances in three days of a level being declared",
    # A MODEL PARAMETER. Two of these put a spurious 42 days on a class with no measured cost
    # at all, which would have moved it up the draw on nothing.
    "a supplier that forgets a failed collection after three weeks and one that never remembers",
    "this instrument cannot tell that supplier from one three weeks out",
    # AN OFFSET between two artefacts, not a duration anything was wrong for.
    "the wedge cross-check predates it by two days and was never told",
    # A REQUIREMENT for future work.
    "once ≥2 weeks of uncensored ticks exist, re-derive the bound",
    # AN AGE, which is a property of a document and not a cost.
    "That document has genuinely sat undispositioned since 2026-08-06. It is six days aged",
])
def test_MUTATION_a_duration_that_is_not_a_span_of_wrongness_is_not_a_cost(sentence):
    """THE MEASURED CASE, and why the extractor is governed by `for` rather than by a wide net.

    Run over the whole corpus, a "duration near a damage word" rule accepted fifteen figures
    of which SEVEN were these. A cost register exists to argue for spending real attention;
    inflating it with recurrence rates and model parameters is the same defect the register
    catalogues, committed by the instrument that ranks it. A later widening has to make these
    pass on purpose."""
    assert cd.persisted_spans(sentence, "x.md") == []


def test_MUTATION_one_document_states_its_span_twice_and_is_billed_once():
    """Same rule and same reason as `finding_classes.worst_per_instance`: a finding that
    restates its own episode must not double it."""
    text = "wedged for 10 days. Inside that, it was wrong for 3 days."
    worst = cd.worst_persisted_per_instance(cd.persisted_spans(text, "one.md"))
    assert [s.days for s in worst] == [10.0]


def test_a_span_with_no_damage_word_anywhere_near_it_is_not_a_cost():
    """The window still has to say something went wrong. Without this the rule would bill
    every scheduling sentence in the corpus."""
    assert cd.persisted_spans("the routine has run for three days on this cadence", "x.md") == []


# ---------------------------------------------------------------------------
# THE DRAW — accrual decides membership, and a decision removes it
# ---------------------------------------------------------------------------

def test_an_accruing_undecided_class_is_work(tmp_path):
    _accruing(tmp_path)
    _register(tmp_path)
    debt = _debt(tmp_path)
    assert debt.still_accruing and debt.drawable
    assert REGISTER in [i.name for i in sr.work_queue(tmp_path)]


def test_MUTATION_a_decided_class_leaves_the_queue(tmp_path):
    """THE STATE THIS MUST NOT RE-CREATE. Before 2026-08-28 the six standing registers sat in
    the work channel permanently, so the queue could never reach zero and could never signal
    "drained" — which is how that folder reached 49 items. A register is allowed to be work
    only because a DECISION takes it out again. If it does not, this mechanism is that defect
    with a cost column bolted on."""
    _accruing(tmp_path)
    _register(tmp_path, disposition=(
        "## Disposition\n\n"
        "**Decision:** ACCEPTED\n"
        "**Taken:** 2026-09-01\n"
        "**At:** 3 instances\n"
        "**Because:** small and static\n"
    ))
    assert not _debt(tmp_path).drawable
    assert REGISTER not in [i.name for i in sr.work_queue(tmp_path)]


def test_MUTATION_an_acceptance_is_re_opened_by_two_further_instances(tmp_path):
    """An `ACCEPTED` that no evidence can overtake is a mute, not a decision. Two instances is
    R10's own bar for a repetition becoming a class, so two arriving AFTER "we will live with
    this" is a class's worth of evidence against it."""
    _accruing(tmp_path, n=3)
    _register(tmp_path, disposition=(
        "## Disposition\n\n**Decision:** ACCEPTED\n**Taken:** 2026-08-25\n"
        "**At:** 3 instances\n**Because:** small\n"
    ))
    assert not _debt(tmp_path).drawable
    _accruing(tmp_path, n=5)  # two more arrive
    debt = _debt(tmp_path)
    assert debt.instances == 5
    assert debt.drawable, "an acceptance that survives its own evidence is a silencer"
    assert "re-opened" in debt.draw_verdict()[1]


def test_MUTATION_an_acceptance_with_no_instance_count_cannot_be_overtaken_so_it_is_drawn(tmp_path):
    """The same defect one level down: an acceptance that never records what it was accepted
    AT can never be SHOWN to have been overtaken, so it would silence the class forever while
    passing every check above."""
    _accruing(tmp_path)
    _register(tmp_path, disposition=(
        "## Disposition\n\n**Decision:** ACCEPTED\n**Taken:** 2026-08-25\n**Because:** small\n"
    ))
    debt = _debt(tmp_path)
    assert debt.drawable
    assert "no instance count" in debt.draw_verdict()[1]


def test_MUTATION_a_closure_whose_mechanism_does_not_resolve_goes_loud(tmp_path):
    """`stall_class_register`'s G2 guarantee, at the address where it matters most. A closure
    is the one thing here that turns a class off permanently; one pointing at a control that
    has since been renamed or deleted actively tells every reader the class is handled."""
    _accruing(tmp_path)
    _register(tmp_path, disposition=(
        "## Disposition\n\n**Decision:** CLOSED\n**Taken:** 2026-08-25\n"
        "**Mechanism:** `tools/a_control_that_was_deleted.py`\n**Because:** repaired\n"
    ))
    debt = _debt(tmp_path)
    assert debt.drawable
    assert "does not resolve" in debt.draw_verdict()[1]


def test_a_closure_naming_a_control_that_exists_removes_the_class(tmp_path):
    _accruing(tmp_path)
    _register(tmp_path, disposition=(
        "## Disposition\n\n**Decision:** CLOSED\n**Taken:** 2026-08-25\n"
        "**Mechanism:** `background/class_debt.py`\n**Because:** this file\n"
    ))
    assert not _debt(tmp_path).drawable


def test_MUTATION_one_instance_is_not_a_recurrence(tmp_path):
    """Accrual is what puts a class in front of other work, and it uses R10's bar rather than
    a threshold on cost — because a threshold on cost would be a number picked because a
    number was needed. One instance is not a class and is not a recurrence either."""
    _instance(tmp_path, "WORKER_FINDING_A_CONTROL_HAS_NO_CALLER_X_2026-08-30.md")
    _register(tmp_path)
    assert not _debt(tmp_path).drawable


def test_a_class_that_stopped_recurring_is_not_drawn_however_expensive_it_was(tmp_path):
    """Size does not put a class in the draw; ACCRUAL does. A class that has stopped happening
    is a limitation being lived with, and this module does not manufacture a decision nobody
    took — it just stops billing attention for it."""
    for i in range(9):
        _instance(
            tmp_path,
            f"WORKER_FINDING_A_CONTROL_HAS_NO_CALLER_{i}_2026-08-01.md",
            body="It was wrong for 20 days.",
        )
    _register(tmp_path)
    debt = _debt(tmp_path)
    assert debt.instances == 9 and debt.persisted_days > 0
    assert not debt.drawable


# ---------------------------------------------------------------------------
# RANK — against other work, and among themselves
# ---------------------------------------------------------------------------

def test_an_accruing_class_outranks_a_finding_and_yields_to_a_persons_ask(tmp_path):
    """The ruling's own argument: "a class with a live instance list is the artefact that can
    win a draw; twenty siblings filed separately cannot." And it still yields to the director,
    who is the one thing that outranks everything."""
    _accruing(tmp_path)
    _register(tmp_path)
    (tmp_path / "DIRECTOR_RULING_SOMETHING_2026-08-31.md").write_text(
        f"# ask\n\n{HEADER}", encoding="utf-8")
    queue = [i.name for i in sr.work_queue(tmp_path)]
    assert queue[0].startswith("DIRECTOR_RULING_")
    assert queue.index(REGISTER) < queue.index(
        "WORKER_FINDING_A_CONTROL_HAS_NO_CALLER_0_2026-08-30.md")


def test_MUTATION_the_order_key_does_not_let_any_hours_beat_any_days():
    """The defect this key was written with. A lexicographic key over two units asserts that
    ANY quantity of the first beats any quantity of the second — which is adding hours to days
    with the addition hidden inside a sort. It put a 25-hour class above a 14-persisted-day
    one on this corpus."""
    hours = cd.ClassDebt(finding_class=cd.fc.CLASSES[0], instances=8, recorded_hours=25.0)
    days = cd.ClassDebt(finding_class=cd.fc.CLASSES[1], instances=8, persisted_days=14.0)
    assert hours.order_key()[1:] != days.order_key()[1:]
    assert hours.order_key()[0] == days.order_key()[0], (
        "instances must lead: the count is measured for 100% of the population and every cost "
        "term for 15% of it, so a cost-led rank ranks classes by measurement habit"
    )


# ---------------------------------------------------------------------------
# FAILING OPEN, AND THE FLOOR
# ---------------------------------------------------------------------------

def test_MUTATION_a_broken_class_debt_does_not_empty_the_work_queue(tmp_path, monkeypatch):
    """A draw that cannot rank its work must still SEE it. Losing the promotion is a
    degradation; losing the queue is a stall, and this project has paid for stalls."""
    _accruing(tmp_path)
    _register(tmp_path)

    def boom(*a, **k):
        raise RuntimeError("corpus unreadable")

    monkeypatch.setattr(cd, "drawable", boom)
    queue = [i.name for i in sr.work_queue(tmp_path)]
    assert "WORKER_FINDING_A_CONTROL_HAS_NO_CALLER_0_2026-08-30.md" in queue
    assert REGISTER not in queue


def test_MUTATION_an_emptied_corpus_is_loud_and_not_a_clean_bill(tmp_path):
    """The dated population floor. Without it this module reports "no debt" identically
    whether the classes are clean or the scan lost its subject — and a control keyed to a
    structure that moved goes QUIET, which is how five emptied subjects were found in one
    day."""
    assert cd.floor_violations(cd.compute(tmp_path, today=TODAY)), (
        "an empty staging root must violate the floor, not read as zero debt"
    )


def test_the_live_corpus_is_above_its_floor():
    """The other half: the floor has to be satisfiable, or it is a control that only ever
    fails, which is as useless as one that never can."""
    assert cd.floor_violations(cd.compute(today=TODAY)) == []


def test_MUTATION_a_re_render_does_not_delete_a_decision_somebody_made(tmp_path):
    """`finding_classes --render` rewrites the whole register. Without carry-through, the
    first re-render after a decision was taken would silently delete it and put the class back
    at the head of the draw — and the register would then read as though nobody had ever
    decided, which is worse than reading as undecided, because it is unrecoverable.

    Same argument the renderer already makes for `archived` (a re-render must ADD the
    sixteenth instance, not forget the first fifteen), at the one place where the thing being
    forgotten is a judgement a person made."""
    from background import finding_classes as fc

    _accruing(tmp_path)
    _register(tmp_path, disposition=(
        "## Disposition\n\n**Decision:** ACCEPTED\n**Taken:** 2026-09-01\n"
        "**At:** 3 instances\n**Because:** small and static\n"
    ))
    assert not _debt(tmp_path).drawable

    membership = fc.derive_memberships(tmp_path)["no_caller_and_never_runs"]
    (tmp_path / REGISTER).write_text(
        fc.render_class_document(membership, tmp_path), encoding="utf-8")

    assert "**Decision:** ACCEPTED" in (tmp_path / REGISTER).read_text(encoding="utf-8")
    assert not _debt(tmp_path).drawable, "the re-render ate the decision"


def test_MUTATION_carrying_the_decision_through_does_not_carry_the_footer_with_it(tmp_path):
    """Caught on the first real re-render. The generated footer is `---` followed by prose and
    carries no HEADING, so a section regex whose lookahead knew only about headings ran to
    end-of-file, swallowed the footer into the disposition, and the renderer then appended a
    second one. Six registers grew a duplicate footer in one pass.

    The general shape is worth the test rather than the fix alone: a carry-through that
    preserves MORE than it was asked to is as wrong as one that preserves less, and it is the
    harder one to notice because nothing is missing."""
    from background import finding_classes as fc

    _accruing(tmp_path)
    _register(tmp_path, disposition=(
        "## Disposition\n\n**Decision:** ACCEPTED\n**Taken:** 2026-09-01\n"
        "**At:** 3 instances\n**Because:** small\n"
    ))
    membership = fc.derive_memberships(tmp_path)["no_caller_and_never_runs"]
    text = fc.render_class_document(membership, tmp_path)
    (tmp_path / REGISTER).write_text(text, encoding="utf-8")

    membership = fc.derive_memberships(tmp_path)["no_caller_and_never_runs"]
    twice = fc.render_class_document(membership, tmp_path)

    assert twice.count("Generated by `background/finding_classes.py`") == 1
    assert twice.count("**Decision:** ACCEPTED") == 1
    assert twice == text, "rendering is not idempotent once a decision is present"
