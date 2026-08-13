"""KNIFE pass 3, `A_composition_lift` step 21 (§3p) — the customer-experience door.

Four crossings cut: `simulation.run_phase2b` no longer imports
`company.crm.satisfaction_accumulator`, `company.crm.nps_tracker`,
`company.crm.complaints` or `company.crm.payment_behaviour_analytics`. It hands
`company/interfaces/customer_experience.py` four observations and reads back the
company's own beliefs.

The controls in this file, and what each can actually fail on:

1. READ DIRECTION (behavioural, not a grep) — run the desk module in a clean
   interpreter and ask the import system which world modules it loaded. The
   mutation adds a lazy `simulation` import inside a method and the SAME
   detector reports it.
2. NO NUMBER MOVES — drive the four raw books through the pre-cut sequence and
   the desk through the door, over the same event stream, and compare every
   published read: satisfaction, its trajectory, the NPS and complaint annual
   summaries, the payment score/metrics/miss buckets, and the whole
   `behavioural_record` dict that the Sim tab charts. This is the control that
   would fail if the lift changed an answer.
3. INSTRUMENT ROUTING AT THE REAL CALL SITE (the invited defect) — the cut
   turned two visibly-different call sites into one door with an `instrument`
   FIELD, so a caller can now post CSAT answers into the published NPS without
   writing anything that looks wrong. An AST check over the REAL constructions
   in `simulation/run_phase2b.py`, with a vacuity guard on how many it found,
   and two mutations that perform the defect (the swap; a hardcoded instrument).
4. THE ARMS DO NOT COLLAPSE (the mirror-image defect, inside the desk) — a desk
   that posted every survey to both books would satisfy control 3 and still be
   wrong. The disjointness is asserted on a live desk, and the mutation builds
   the collapsed desk and shows the assertion failing on it.
5. THE DECAY RUNS BEFORE THE SHOCK — the order inside `observe_renewal` is now
   invisible to the caller. The mutation swaps the two statements; a term's
   worth of mean-reversion would silently damp every bill shock.

VACUITY, stated once for the whole file. The event stream below is one account
that answers both surveys, complains once and is resolved on time, misses
payments, and renews twice with a shock on the second — chosen so satisfaction
is OFF baseline when the decay runs (otherwise control 5 cannot fail), the
payment score is non-EXCELLENT (otherwise control 2 compares two defaults) and
both survey books are non-empty (otherwise control 4 compares two empties).
`test_the_event_stream_is_not_degenerate` asserts all three directly.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import textwrap
from datetime import date

import pytest

from company.crm.complaints import ComplaintBook, ComplaintCategory
from company.crm.nps_tracker import NPSTracker
from company.crm.payment_behaviour_analytics import BehaviourScore, PaymentBehaviourAnalytics
from company.crm.satisfaction_accumulator import CustomerSatisfactionAccumulator
from company.interfaces import customer_experience as door

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RUN_MODULE_PATH = os.path.join(REPO_ROOT, "simulation", "run_phase2b.py")
IMPL_PATH = os.path.join(REPO_ROOT, "company", "crm", "customer_experience_desk.py")

CID = "C7"
ACCOUNT = "ACC-C7"
SEGMENT = "resi"
CHANNEL = "renewal"

# One account's year, in the order the run loop produces it.
_RENEWALS = [
    (2018, False),
    (2019, True),      # the shocked renewal
]
_SURVEYS = [
    ("csat", 9, date(2018, 4, 1)),
    ("nps", 10, date(2018, 4, 1)),
    ("csat", 2, date(2019, 4, 1)),
    ("nps", 3, date(2019, 4, 1)),
]
_CONTACTS = [
    (date(2019, 4, 1), True, True),   # about a bill shock, resolved on time
    (date(2019, 9, 1), False, False),  # routine, not resolved on time
]
_PAYMENTS = [
    (date(2018, 6, 28), "ON_TIME", 0),
    (date(2018, 7, 28), "LATE", 11),
    (date(2019, 6, 28), "DD_FAILED", 0),
    (date(2019, 7, 28), "LATE", 4),
    (date(2019, 8, 28), "ON_TIME", 0),
]
_AMOUNT = 88.40
_YEARS = [2018, 2019]


# ---------------------------------------------------------------------------
# The two implementations of the same stream: the pre-cut one, and the door.
# ---------------------------------------------------------------------------


def _drive_pre_cut():
    """The exact sequence `run_phase2b.py::main()` ran before step 21."""
    sat = CustomerSatisfactionAccumulator()
    nps = NPSTracker()
    complaints = ComplaintBook()
    payments = PaymentBehaviourAnalytics()

    for instrument, score, on in _SURVEYS[:2]:
        if instrument == "csat":
            sat.record_css_score(CID, score)
        else:
            nps.record(ACCOUNT, score, on, segment=SEGMENT, channel=CHANNEL)
    for due, result, days_late in _PAYMENTS[:2]:
        payments.record_payment(CID, {
            "customer_id": CID, "due_date": due, "result": result,
            "days_late": days_late, "amount_gbp": _AMOUNT,
        })
    for year, shock in _RENEWALS:
        sat.apply_monthly_decay(CID, months=12)
        if shock:
            sat.record_bill_shock(CID)
        sat.record_year_snapshot(CID, year)
    for instrument, score, on in _SURVEYS[2:]:
        if instrument == "csat":
            sat.record_css_score(CID, score)
        else:
            nps.record(ACCOUNT, score, on, segment=SEGMENT, channel=CHANNEL)
    for on, about_shock, resolved in _CONTACTS:
        complaints.raise_complaint(
            ACCOUNT, ComplaintCategory.BILLING, on,
            description="bill-shock-driven contact" if about_shock else "routine contact",
        )
        sat.record_complaint_raised(CID)
        if resolved:
            sat.record_complaint_resolved(CID)
    for due, result, days_late in _PAYMENTS[2:]:
        payments.record_payment(CID, {
            "customer_id": CID, "due_date": due, "result": result,
            "days_late": days_late, "amount_gbp": _AMOUNT,
        })
    return sat, nps, complaints, payments


def _drive_desk(desk=None):
    """The same stream, through the door."""
    desk = desk if desk is not None else door.CustomerExperienceDesk()
    for instrument, score, on in _SURVEYS[:2]:
        desk.observe_survey_response(_survey(instrument, score, on))
    for due, result, days_late in _PAYMENTS[:2]:
        desk.observe_payment(_payment(due, result, days_late))
    for year, shock in _RENEWALS:
        desk.observe_renewal(door.RenewalReached(
            customer_id=CID, account_id=ACCOUNT, renewal_year=year, bill_shock=shock,
        ))
    for instrument, score, on in _SURVEYS[2:]:
        desk.observe_survey_response(_survey(instrument, score, on))
    for on, about_shock, resolved in _CONTACTS:
        desk.observe_contact(door.CustomerContact(
            customer_id=CID, account_id=ACCOUNT, contacted_on=on,
            about_bill_shock=about_shock, resolved_on_time=resolved,
        ))
    for due, result, days_late in _PAYMENTS[2:]:
        desk.observe_payment(_payment(due, result, days_late))
    return desk


def _survey(instrument, score, on, desk_module=door):
    return desk_module.SurveyResponse(
        customer_id=CID,
        account_id=ACCOUNT,
        instrument=(
            desk_module.SurveyInstrument.CSAT if instrument == "csat"
            else desk_module.SurveyInstrument.NPS
        ),
        score_0_10=score,
        responded_on=on,
        segment=SEGMENT,
        channel=CHANNEL,
    )


def _payment(due, result, days_late, desk_module=door):
    return desk_module.PaymentOutcome(
        customer_id=CID, due_date=due, result=result,
        days_late=days_late, amount_gbp=_AMOUNT,
    )


# ---------------------------------------------------------------------------
# VACUITY — the stream must be able to fail the controls that read it.
# ---------------------------------------------------------------------------


def test_the_event_stream_is_not_degenerate():
    sat, nps, complaints, payments = _drive_pre_cut()
    assert sat.get_satisfaction(CID) != 0.70, (
        "satisfaction sits exactly on baseline — control 5 could not fail"
    )
    assert payments.get_score(CID) is not BehaviourScore.EXCELLENT, (
        "the payment score is the empty-history default — control 2 would compare "
        "two defaults"
    )
    assert nps.annual_summary(2019)["responses"] > 0
    assert complaints.annual_summary(2019)["total"] > 0
    assert len(sat.get_trajectory(CID)) == len(_YEARS)


# ---------------------------------------------------------------------------
# CONTROL 1 — the company module must not reach back into the world, statically
# OR lazily. Behavioural: what did the import system actually load?
# ---------------------------------------------------------------------------

_PROBE = textwrap.dedent(
    """
    import json, sys
    from datetime import date
    sys.path.insert(0, {repo!r})
    sys.path.insert(0, {pkgdir!r})
    import {modname} as m

    desk = m.CustomerExperienceDesk()
    desk.observe_survey_response(m.SurveyResponse(
        customer_id="C7", account_id="ACC-C7",
        instrument=m.SurveyInstrument.CSAT, score_0_10=9,
        responded_on=date(2019, 4, 1), segment="resi", channel="renewal",
    ))
    desk.observe_survey_response(m.SurveyResponse(
        customer_id="C7", account_id="ACC-C7",
        instrument=m.SurveyInstrument.NPS, score_0_10=3,
        responded_on=date(2019, 4, 1), segment="resi", channel="renewal",
    ))
    desk.observe_renewal(m.RenewalReached(
        customer_id="C7", account_id="ACC-C7", renewal_year=2019, bill_shock=True,
    ))
    desk.observe_contact(m.CustomerContact(
        customer_id="C7", account_id="ACC-C7", contacted_on=date(2019, 4, 1),
        about_bill_shock=True, resolved_on_time=False,
    ))
    desk.observe_payment(m.PaymentOutcome(
        customer_id="C7", due_date=date(2019, 6, 28), result="LATE",
        days_late=4, amount_gbp=88.40,
    ))
    desk.satisfaction_score("C7")
    desk.payment_behaviour_score("C7")
    desk.nps_annual_summary(2019)
    desk.complaint_annual_summary(2019)
    desk.behavioural_record("C7")

    walled = sorted(
        n for n in sys.modules
        if n in ("sim", "simulation") or n.startswith(("sim.", "simulation."))
    )
    print("WALLED_MODULES=" + json.dumps(walled))
    """
)


def _walled_modules_loaded_by(source: str) -> list[str]:
    """Run `source` as the impl module in a clean interpreter; report sim loads.

    THE detector, used unchanged by both the real test and its mutation.
    """
    with tempfile.TemporaryDirectory() as pkgdir:
        modname = "_knife3_step21_subject"
        with open(os.path.join(pkgdir, modname + ".py"), "w") as fh:
            fh.write(source)
        probe = _PROBE.format(repo=REPO_ROOT, pkgdir=pkgdir, modname=modname)
        proc = subprocess.run(
            [sys.executable, "-c", probe],
            cwd=pkgdir,
            capture_output=True,
            text=True,
            timeout=300,
        )
    assert proc.returncode == 0, (
        f"the probe itself failed — an unavailable check is a FAILED check, "
        f"never a skip.\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    marker = [ln for ln in proc.stdout.splitlines() if ln.startswith("WALLED_MODULES=")]
    assert len(marker) == 1, f"probe produced no verdict line:\n{proc.stdout}"
    return json.loads(marker[0].split("=", 1)[1])


def test_keeping_the_experience_book_loads_no_world_module():
    with open(IMPL_PATH) as fh:
        real_source = fh.read()
    assert _walled_modules_loaded_by(real_source) == []


def test_mutation_a_lazy_world_import_is_caught_by_the_same_detector():
    """Perform the defect on a copy of the real source, same detector."""
    with open(IMPL_PATH) as fh:
        mutated = fh.read()
    anchor = "    def observe_payment(self, event: PaymentOutcome) -> None:"
    assert anchor in mutated, "anchor moved — this mutation is no longer the defect"
    mutated = mutated.replace(
        anchor,
        anchor + "\n        from simulation.feedback_survey import dispatch_nps_survey  # noqa: F401  <-- the defect",
        1,
    )
    loaded = _walled_modules_loaded_by(mutated)
    assert "simulation.feedback_survey" in loaded, (
        "the mutation did not take — control 1 is not testing what it claims"
    )


# ---------------------------------------------------------------------------
# CONTROL 2 — NO NUMBER MOVES. Every published read, both implementations.
# ---------------------------------------------------------------------------


def test_the_door_reproduces_the_pre_cut_satisfaction_and_trajectory():
    sat, _, _, _ = _drive_pre_cut()
    desk = _drive_desk()
    assert desk.satisfaction_score(CID) == sat.get_satisfaction(CID)
    assert desk.behavioural_record(CID)["satisfaction_score_trajectory"] == sat.get_trajectory(CID)


def test_the_door_reproduces_the_pre_cut_payment_reads():
    _, _, _, payments = _drive_pre_cut()
    desk = _drive_desk()
    assert desk.payment_behaviour_score(CID) == payments.get_score(CID)
    record = desk.behavioural_record(CID)
    metrics = payments.get_metrics(CID)
    assert record["payment_behaviour_score"] == payments.get_score(CID).value
    assert record["payment_behaviour_metrics"] == {
        "on_time_rate": metrics["on_time_rate"],
        "late_rate": metrics["late_rate"],
        "dd_fail_rate": metrics["dd_fail_rate"],
    }
    assert record["payment_miss_trajectory"] == payments.get_miss_trajectory(CID)


@pytest.mark.parametrize("year", _YEARS)
def test_the_door_reproduces_the_pre_cut_annual_summaries(year):
    _, nps, complaints, _ = _drive_pre_cut()
    desk = _drive_desk()
    assert desk.nps_annual_summary(year) == nps.annual_summary(year)
    assert desk.complaint_annual_summary(year) == complaints.annual_summary(year)


def test_the_behavioural_record_keys_are_in_the_published_order():
    """The record is spliced into `per_customer_behavioral` between the world's
    own trajectories; its key order is part of the contract the Sim tab reads."""
    assert list(_drive_desk().behavioural_record(CID)) == [
        "payment_behaviour_score",
        "payment_behaviour_metrics",
        "company_satisfaction_score",
        "satisfaction_score_trajectory",
        "payment_miss_trajectory",
    ]


# ---------------------------------------------------------------------------
# CONTROL 3 — the invited defect, at the REAL call site.
# ---------------------------------------------------------------------------


def _survey_callsites(source: str) -> list[ast.Call]:
    tree = ast.parse(source)
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "SurveyResponse"
    ]


def _instrument_of(call: ast.Call) -> str | None:
    """The dotted `SurveyInstrument.X` an instrument= keyword names, or None."""
    for kw in call.keywords:
        if kw.arg != "instrument":
            continue
        if isinstance(kw.value, ast.Attribute) and isinstance(kw.value.value, ast.Name):
            return f"{kw.value.value.id}.{kw.value.attr}"
        return None
    return None


def _score_source_of(call: ast.Call) -> str | None:
    """The attribute expression feeding score_0_10=, e.g. `_csat_result.score_0_10`."""
    for kw in call.keywords:
        if kw.arg != "score_0_10":
            continue
        if isinstance(kw.value, ast.Attribute) and isinstance(kw.value.value, ast.Name):
            return f"{kw.value.value.id}.{kw.value.attr}"
        return None
    return None


def _routing_pairs(source: str) -> set[tuple[str | None, str | None]]:
    """(instrument, the result object its score came from) for each construction."""
    return {(_instrument_of(c), _score_source_of(c)) for c in _survey_callsites(source)}


def test_the_world_routes_each_survey_to_its_own_instrument():
    with open(RUN_MODULE_PATH) as fh:
        source = fh.read()
    calls = _survey_callsites(source)
    # VACUITY GUARD — a source with no such call would make the assertion below
    # pass over an empty set.
    assert len(calls) == 2, (
        f"expected exactly two SurveyResponse constructions in run_phase2b.py, "
        f"found {len(calls)} — control 3 is examining the wrong thing"
    )
    assert _routing_pairs(source) == {
        ("SurveyInstrument.CSAT", "_csat_result.score_0_10"),
        ("SurveyInstrument.NPS", "_nps_result.score_0_10"),
    }


def test_mutation_the_swapped_instrument_is_caught():
    """The defect: CSAT answers posted into the published NPS and vice versa.

    Nothing else in the run changes and every desk test stays green, because the
    desk did exactly what it was told.
    """
    with open(RUN_MODULE_PATH) as fh:
        mutated = (
            fh.read()
            .replace("instrument=SurveyInstrument.CSAT,", "instrument=__SWAP__,", 1)
            .replace("instrument=SurveyInstrument.NPS,", "instrument=SurveyInstrument.CSAT,", 1)
            .replace("instrument=__SWAP__,", "instrument=SurveyInstrument.NPS,", 1)
        )
    pairs = _routing_pairs(mutated)
    assert pairs != {
        ("SurveyInstrument.CSAT", "_csat_result.score_0_10"),
        ("SurveyInstrument.NPS", "_nps_result.score_0_10"),
    }, "the mutation did not take — control 3 is not testing what it claims"


def test_mutation_a_hardcoded_instrument_is_caught():
    """The defect: both constructions naming the same instrument."""
    with open(RUN_MODULE_PATH) as fh:
        mutated = fh.read().replace(
            "instrument=SurveyInstrument.NPS,", "instrument=SurveyInstrument.CSAT,", 1
        )
    pairs = _routing_pairs(mutated)
    assert len(calls_instruments := {i for i, _ in pairs}) == 1, (
        f"the mutation did not take — instruments are still {calls_instruments}"
    )


# ---------------------------------------------------------------------------
# CONTROL 4 — the mirror-image defect, INSIDE the desk: the arms collapsing.
# ---------------------------------------------------------------------------


def _load_mutated_desk(mutated_source: str, tag: str):
    """Import a mutated COPY of the real desk source as its own module.

    Registered in `sys.modules` before execution because `@dataclass` resolves
    its field annotations through the module entry; loading it unregistered
    fails inside dataclasses rather than in the assertion, which would make this
    mutation unavailable — and an unavailable check is a FAILED check.
    """
    name = f"_knife3_step21_{tag}"
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, name + ".py")
        with open(path, "w") as fh:
            fh.write(mutated_source)
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        try:
            spec.loader.exec_module(module)
        except BaseException:
            sys.modules.pop(name, None)
            raise
    return module


def _arms_are_disjoint(desk_module) -> bool:
    """THE detector: a CSAT answer must not reach the NPS book, and an NPS
    answer must not move satisfaction. Used unchanged by test and mutation."""
    csat_only = desk_module.CustomerExperienceDesk()
    csat_only.observe_survey_response(_survey("csat", 10, date(2019, 4, 1), desk_module))
    nps_only = desk_module.CustomerExperienceDesk()
    baseline = nps_only.satisfaction_score(CID)
    nps_only.observe_survey_response(_survey("nps", 10, date(2019, 4, 1), desk_module))
    csat_left_nps_empty = csat_only.nps_annual_summary(2019)["responses"] == 0
    nps_left_satisfaction_alone = nps_only.satisfaction_score(CID) == baseline
    return csat_left_nps_empty and nps_left_satisfaction_alone


def test_the_two_survey_arms_do_not_collapse():
    assert _arms_are_disjoint(door)


def test_mutation_a_desk_that_posts_every_survey_to_both_books_is_caught():
    with open(IMPL_PATH) as fh:
        source = fh.read()
    anchor = "        if event.instrument is SurveyInstrument.CSAT:"
    assert anchor in source, "anchor moved — this mutation is no longer the defect"
    mutated = source.replace(
        anchor,
        "        if True:  # <-- the defect: every survey takes the CSAT arm too\n"
        "            self._nps.record(\n"
        "                event.account_id, event.score_0_10, event.responded_on,\n"
        "                segment=event.segment, channel=event.channel,\n"
        "            )\n" + anchor,
        1,
    )
    collapsed = _load_mutated_desk(mutated, "collapsed")
    assert not _arms_are_disjoint(collapsed), (
        "the mutation did not take — control 4 is not testing what it claims"
    )


# ---------------------------------------------------------------------------
# CONTROL 5 — the order inside observe_renewal, now invisible to the caller.
# ---------------------------------------------------------------------------


def _satisfaction_after_a_shocked_renewal(desk_module) -> float:
    """THE detector: push the score above baseline, then renew with a shock.

    Decay-then-shock lands below baseline; shock-then-decay is absorbed by the
    headroom the good CSAT bought and lands ON baseline.
    """
    desk = desk_module.CustomerExperienceDesk()
    desk.observe_survey_response(_survey("csat", 10, date(2018, 4, 1), desk_module))
    desk.observe_renewal(desk_module.RenewalReached(
        customer_id=CID, account_id=ACCOUNT, renewal_year=2019, bill_shock=True,
    ))
    return desk.satisfaction_score(CID)


def test_the_decay_runs_before_the_shock():
    assert _satisfaction_after_a_shocked_renewal(door) == pytest.approx(0.65)


def test_mutation_swapping_the_decay_and_the_shock_is_caught():
    with open(IMPL_PATH) as fh:
        source = fh.read()
    decay = (
        "        self._satisfaction.apply_monthly_decay(\n"
        "            event.customer_id, months=_RENEWAL_DECAY_MONTHS\n"
        "        )\n"
    )
    shock = (
        "        if event.bill_shock:\n"
        "            self._satisfaction.record_bill_shock(event.customer_id)\n"
    )
    assert decay + shock in source, "anchor moved — this mutation is no longer the defect"
    swapped = _load_mutated_desk(source.replace(decay + shock, shock + decay, 1), "swapped")
    assert _satisfaction_after_a_shocked_renewal(swapped) != pytest.approx(0.65), (
        "the mutation did not take — control 5 is not testing what it claims"
    )


# ---------------------------------------------------------------------------
# The door is a door: it re-exports the desk and adds no logic of its own.
# ---------------------------------------------------------------------------


def test_the_door_exports_exactly_the_desk():
    from company.crm import customer_experience_desk as impl

    for name in door.__all__:
        assert getattr(door, name) is getattr(impl, name), (
            f"{name} on the door is not the desk's — the seam has grown a second "
            f"implementation"
        )


def test_the_world_no_longer_opens_the_companys_books():
    with open(RUN_MODULE_PATH) as fh:
        source = fh.read()
    for gone in (
        "CustomerSatisfactionAccumulator",
        "NPSTracker",
        "ComplaintBook",
        "ComplaintCategory",
        "PaymentBehaviourAnalytics",
    ):
        assert gone not in source, (
            f"run_phase2b.py still names {gone} — the crossing was re-exported, "
            f"not cut"
        )
