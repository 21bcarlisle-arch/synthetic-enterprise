"""W2_41: a household cancels its Direct Debit mandate as its own act, and the supplier learns of it
the way Bacs tells it -- an ADDACS 1 record on the next working day, ahead of any failed collection.

Knowledge: docs/market_research/dd_failure_basis_and_live_arrears_provision_rates.md section 4a.
"""
from __future__ import annotations

import dataclasses
import random
from datetime import date

import pytest

import simulation.arrears_engine as ae
import simulation.dd_collection_book as dcb
import simulation.dd_shock_response as d
from simulation import bacs_rails as br
from simulation.payment_method_dynamics import MethodStrengths, own_reasons_cancellation
from tests.simulation.test_dd_shock_response import _book, _dd_ids

FRIDAY = date(2022, 10, 7)
MONDAY = date(2022, 10, 10)


def test_a_cancellation_can_be_drawn_and_can_be_not_drawn():
    """Defect caught: a draw that never fires (or always fires) passes every shape test below."""
    rng = random.Random(41)
    draws = [br.draw_payer_cancellation(f"r{i}", "h1", MONDAY, rng.random(), probability=0.3) for i in range(400)]
    cancelled = [d for d in draws if d is not None]
    assert cancelled and len(cancelled) < len(draws)
    assert 0.2 < len(cancelled) / len(draws) < 0.4


def test_the_unpublished_rate_refuses_by_name_rather_than_drawing_a_number():
    """Defect caught: a placeholder rate standing in for the GAP."""
    assert br.PAYER_CANCELLATION_PROBABILITY is None
    with pytest.raises(ValueError, match="no published rate"):
        br.draw_payer_cancellation("r", "h1", MONDAY, 0.0)


def test_it_crosses_the_seam_only_as_an_addacs_record():
    """Defect caught: the household's act date or private state riding on what the supplier reads."""
    rec = br.draw_payer_cancellation("r1", "h1", FRIDAY, 0.5, probability=1.0)
    assert isinstance(rec, br.AddacsRecord) and not isinstance(rec, br.BacsSubmission)
    assert {f.name for f in dataclasses.fields(rec)} == {
        "reference", "customer_id", "reason_code", "reason", "available_date"}
    assert rec.reason_code == br.ADDACS_PAYER_CANCELLED == 1
    assert "cancelled by payer" in rec.reason.lower()


def test_it_lands_the_next_working_day_before_any_collection_fails():
    """Defect caught: the cancellation found out only through the ARUDD return, a calendar-day lag."""
    rec = br.payer_cancellation("r1", "h1", FRIDAY)
    assert rec.available_date == MONDAY
    # The earliest a collection submitted the same day could come back failed.
    collection = br.submit_collection("c1", "h1", 120.0, FRIDAY)
    returned = br.resolve_submission(collection, "failed", rng=random.Random(0))
    assert rec.available_date < collection.expected_outcome_date <= returned.expected_outcome_date


def test_a_collection_overtaken_by_a_cancel_returns_arudd_1_and_no_other_does():
    """Defect caught: an overtaken collection returned "Refer to Payer", or the flag leaked to a
    collection the payer did not cancel or to a success."""
    collection = br.submit_collection("c1", "h1", 120.0, FRIDAY)
    code = lambda sub, out, cancelled: br.resolve_submission(  # noqa: E731
        sub, out, rng=random.Random(0), instruction_cancelled=cancelled).reason_code
    assert code(collection, "failed", True) == 1
    assert br.ARUDD_REASON_CODES[1] == "Instruction Cancelled"
    assert code(collection, "failed", False) == 0
    assert code(collection, "success", True) is None


def _own_act(cid):
    return own_reasons_cancellation(household=cid, month="2022-04", stress="low",
                                    pays_by_direct_debit=True, already_cancelled=False,
                                    strengths=MethodStrengths(own_cancel_share=1.0))


def test_both_routes_occur_and_the_money_side_and_the_rails_agree_on_every_presented_collection(
        monkeypatch):
    """Defect caught: an own-act cancel found out only through a returned collection (the ARUDD
    route), or the rails and the money side disagreeing on which collections were presented -- two
    homes for one fact. The partition first: the own-act route (ADDACS 1, no failed collection
    before it) AND DD4b's overtaking route (ARUDD 1 then ADDACS 1) both happen on one book."""
    monkeypatch.setattr(br, "REMANDATE_ACCEPTANCE_PROBABILITY", None)
    ids = _dd_ids(12)
    own_ids, shock_ids = ids[:6], ids[6:]
    shock = {"review_month": "2022-04", "cancelled_month": "2022-04", "failure_multiplier": 1.0}
    bills, behavioral = _book(ids, stress="low")
    for cid in ids:
        row = _own_act(cid) if cid in own_ids else dict(shock, household=cid)
        assert row is not None
        behavioral[cid][d.RECORD_KEY] = [row]

    attempts = dcb.build_dd_collection_book(bills, behavioral).all_attempts()
    notices = dcb.supplier_dd_spell_notices(bills, behavioral)
    money = ae._resolve_bills(bills, behavioral, 42)

    # An attempt carries no bill id, so agreement is per household: the rails present exactly the
    # bills the money side resolves on DD, and the bills before the cancel month are those.
    rails = {cid: sorted((a for a in attempts if a.customer_id == cid), key=lambda a: a.attempt_date)
             for cid in ids}
    on_dd = {cid: [r for r in money if r["customer_id"] == cid and r["method"] == "direct_debit"]
             for cid in ids}
    for cid in ids:
        assert len(rails[cid]) == len(on_dd[cid]), cid
        assert all(r["period_end"][:7] <= "2022-04" for r in on_dd[cid]), cid

    for cid in own_ids:
        row = behavioral[cid][d.RECORD_KEY][0]
        assert len(rails[cid]) == 3, "own act: April's collection was presented"
        assert all(a.outcome == "collected" for a in rails[cid]), "own act found out by a return"
        act = date.fromisoformat(row["act_date"])
        assert act.strftime("%Y-%m") == "2022-04"
        assert row["addacs_available"] == br.payer_cancellation("r", cid, act).available_date.isoformat()
        assert notices[cid][0][0] == row["addacs_available"]
        assert row["addacs_available"] < "2022-05-12", "ADDACS lands after April's bill is due"
    for cid in shock_ids:
        assert len(rails[cid]) == 4
        returned = rails[cid][-1]
        assert returned.outcome == "failed" and returned.failure_reason == br.ARUDD_REASON_CODES[1]
        assert notices[cid][0][0] > returned.attempt_date
