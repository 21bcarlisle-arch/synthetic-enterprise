"""A CLASS REPAIRED ON SIGHT TWENTY TIMES HAS HAPPENED TWENTY TIMES.

Director, 2026-09-02: *"a class repaired on sight twenty times reading as zero debt is the exact
thing the measure exists to prevent."*

`finding_classes.derive_memberships` drops RECORDED documents, and its reason is correct for what it
was written for: *"a RECORDED document is a landed record with nothing owed … folding reports of
FIXES into a class of DEFECTS would inflate every instance list with work already done."* A class
register must not archive a fix report under a defect heading.

It is the wrong population for the question `class_debt` asks. Recurrence is *how often the shape
happens*, and whether someone repaired it within the hour has no bearing on that. Measured:
`no_caller_and_never_runs` took three instances on 2026-09-01 and three more on 2026-09-02, every
one RECORDED, and its count moved by **zero**.

This is the same distinction the out-of-lane fix already drew one level down — consolidation is
lane-scoped, accrual is not — arriving again at SEVERITY instead of LANE. One population answering
two questions, and only one of them its own.

**And the exclusions are the load-bearing half.** Counting the archive WITHOUT the two exclusions
the register's own rules already apply gave 119 additions where the honest figure is 88, and
produced a published claim about the draw re-ordering that was wrong. That is
`a correct refusal is not a population`, committed inside the finding about it. So the tests below
spend more on what is EXCLUDED than on what is counted.
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest

from background import class_debt as cd
from background import finding_classes as fc

TODAY = dt.date(2026, 9, 2)


@pytest.fixture
def corpus(tmp_path):
    """A staging root with a root, an archive and a reference room."""
    (tmp_path / fc.ARCHIVE_DIRNAME).mkdir(parents=True)
    (tmp_path / "reference").mkdir(parents=True)
    return tmp_path


def _doc(folder: Path, name: str, class_id: str, severity: str = "RECORDED") -> Path:
    p = folder / name
    p.write_text(
        "# [WORKER FINDING] a thing\n\n"
        "**Severity:** {sev} · **Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted\n\n"
        "## Class registration\n\nBelongs to `{cid}`.\n".format(sev=severity, cid=class_id))
    return p


CID = "no_caller_and_never_runs"


# ── the population that was missing ─────────────────────────────────────────────────────────
def test_a_recorded_fix_report_in_the_root_counts_as_a_recurrence(corpus):
    """THE DIRECTOR'S CASE, in one assertion. A finding filed and fixed in the same turn is
    invisible to the consolidated count and must not be invisible to recurrence.

    MUTATION: scan only the archive in `recurrence_paths` and this fails.
    """
    _doc(corpus, "WORKER_FINDING_FIXED_ON_SIGHT_2026-09-02.md", CID, severity="RECORDED")
    assert [p.name for p in cd.recurrence_paths(corpus, CID, set())] == [
        "WORKER_FINDING_FIXED_ON_SIGHT_2026-09-02.md"]


def test_an_archived_instance_counts_as_a_recurrence(corpus):
    _doc(corpus / fc.ARCHIVE_DIRNAME, "WORKER_FINDING_OLD_ONE_2026-08-20.md", CID)
    assert len(cd.recurrence_paths(corpus, CID, set())) == 1


def test_a_document_already_consolidated_is_not_counted_twice(corpus):
    """`already` is the consolidated set. Double-counting would inflate every class."""
    name = "WORKER_FINDING_LISTED_2026-08-20.md"
    _doc(corpus / fc.ARCHIVE_DIRNAME, name, CID)
    assert cd.recurrence_paths(corpus, CID, {name}) == []


# ── THE EXCLUSIONS, which are where the published error came from ───────────────────────────
def test_an_externally_authored_document_is_out_of_population(corpus):
    """An advisor pointer or a director ruling is another party's ask, not an instance of
    anything. The register already refuses to consolidate them; counting them for recurrence
    would be reading a correct refusal as a population.

    MUTATION: drop the `EXTERNALLY_AUTHORED_PREFIXES` guard and this fails — 10 such documents
    re-enter the real corpus.
    """
    prefix = fc.EXTERNALLY_AUTHORED_PREFIXES[0]
    _doc(corpus / fc.ARCHIVE_DIRNAME, prefix + "SOMETHING_2026-08-20.md", CID)
    assert cd.recurrence_paths(corpus, CID, set()) == []


def test_a_self_clearing_alarm_is_out_of_population(corpus):
    """A live alarm document is not an instance either, and there are 29 of them in the archive —
    the single largest source of the 119-vs-88 error.

    MUTATION: drop the `SELF_CLEARING_ALARM_PREFIXES` guard and this fails.
    """
    prefix = fc.SELF_CLEARING_ALARM_PREFIXES[0]
    _doc(corpus / fc.ARCHIVE_DIRNAME, prefix + "SOMETHING_2026-08-20.md", CID)
    assert cd.recurrence_paths(corpus, CID, set()) == []


def test_a_class_register_is_never_an_instance_of_itself(corpus):
    """The mirror trap: a register counting itself would rise every time it is re-rendered."""
    _doc(corpus / "reference", fc.CLASS_DOC_PREFIX + "SOMETHING_2026-08-12.md", CID)
    _doc(corpus, fc.CLASS_DOC_PREFIX + "STRAY_2026-08-12.md", CID)
    assert cd.recurrence_paths(corpus, CID, set()) == []


# ── what recurrence is ALLOWED to change, and what it is not ────────────────────────────────
def test_recurrence_can_only_ever_be_at_least_the_consolidated_count():
    """A floor, on the real corpus. Recurrence adds documents and removes none, so a class whose
    recurrence is BELOW its instance count means the two populations have diverged."""
    for d in cd.compute(Path("docs/staging"), today=TODAY):
        assert d.recurrence >= d.instances, d.finding_class.id


def test_accrual_can_only_ever_see_more_never_less():
    """`still_accruing` takes `max(recent_instances, recent_recurrence)`, so a class that was
    accruing before this change cannot stop because of it. A measure that could turn a drawn
    register OFF would be a silencer wearing an improvement's clothes."""
    import inspect
    src = inspect.getsource(cd.ClassDebt.still_accruing.fget)
    assert "max(" in src


def test_the_re_arm_reads_recurrence_so_a_fixed_on_sight_class_can_overturn_an_acceptance():
    """P4, and the whole justification for the change. An ACCEPTED decision is overtaken by the
    shape HAPPENING AGAIN; whether it was repaired within the hour has no bearing on that.

    MUTATION: key the re-arm back to `self.instances` and this fails — the acceptance survives
    evidence that should have overturned it, which is what an acceptance is FOR.
    """
    debt = cd.ClassDebt(finding_class=fc.CLASSES[0], instances=7, recurrence=20)
    debt.disposition = cd.Disposition(
        decision=cd.ACCEPTED, taken="2026-08-20", at_instances=7, because="small")
    drawn, why = debt.draw_verdict()
    assert drawn is True and "now 20" in why


def test_the_draw_order_still_leads_with_the_deliberate_count():
    """Recurrence carries a measured ~25% misclassification bias; the consolidated count is a set
    of deliberate assignments. Ranking the draw on the noisier number would pay for reach with
    accuracy, so `order_key` is deliberately unchanged — and the pre-registration was wrong to
    call these one order."""
    import inspect
    src = inspect.getsource(cd.ClassDebt.order_key)
    assert "recurrence" not in src


def test_the_recurrence_scan_carries_its_own_dated_floor():
    """Its subject is two folders and two exclusions, and any of the four can silently stop
    matching. A scanning control without a dated floor is the defect found five times in one day,
    and inheriting the instances floor would leave the archive half unwatched.

    MUTATION: delete the recurrence floor and this fails.
    """
    thin = [cd.ClassDebt(finding_class=c, instances=100, recurrence=1) for c in fc.CLASSES]
    violations = " ".join(cd.floor_violations(thin))
    assert "FLOOR recurrence" in violations
    assert str(cd.FLOOR_RECURRENCE) in violations


def test_the_real_corpus_is_above_every_floor():
    assert cd.floor_violations(cd.compute(Path("docs/staging"), today=TODAY)) == []
