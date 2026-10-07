"""A bill missed on a rail with no Direct Debit is MISSED, not DD_FAILED -- and every distress
reader must still see it as a missed bill.

Relabelling alone would be worse than the mislabel it fixes: the score, the life-event detector,
affordability inference and SME credit risk all read DD_FAILED as their unpaid signal, so a new
label they did not know would make a standard-credit or corporate customer's misses stop
registering as distress. Each reader is held to "MISSED reads exactly as DD_FAILED did" and,
first, to "that reading is not zero", so a reader that ignores both cannot pass.
"""
from datetime import date

from company.compliance.domain_invariants import record_asserts_dd_failure
from company.crm import affordability_inference, life_event_detector
from company.crm.payment_behaviour_analytics import (
    PaymentBehaviourAnalytics,
    compute_payment_metrics,
    score_payment_history,
)
from saas import sme_credit_risk


def _window(unpaid_label):
    return [{"result": "ON_TIME", "days_late": 0}] * 6 + [{"result": unpaid_label, "days_late": 0}] * 4


def test_every_distress_reader_scores_a_missed_bill_as_it_scored_a_returned_direct_debit():
    readers = {
        "affordability": affordability_inference._bad_rate,
        "life_event": life_event_detector._bad_rate,
        "sme_credit": sme_credit_risk._bad_rate,
    }
    for name, read in readers.items():
        assert read(_window("DD_FAILED")) > 0, name
        assert read(_window("MISSED")) == read(_window("DD_FAILED")), name
    assert score_payment_history(_window("DD_FAILED")) == score_payment_history(_window("MISSED"))
    assert score_payment_history(_window("MISSED")).value == "CRITICAL"
    assert sme_credit_risk._avg_days_late(_window("MISSED")) is not None


def test_a_missed_bill_is_a_miss_and_not_a_direct_debit_failure():
    m = compute_payment_metrics(_window("MISSED"))
    assert m["miss_rate"] == 0.4
    assert m["dd_fail_rate"] == 0.0
    returned = compute_payment_metrics(_window("DD_FAILED"))
    assert returned["miss_rate"] == returned["dd_fail_rate"] == 0.4


def test_a_non_dd_customers_behavioural_record_carries_no_direct_debit_artefact():
    pba = PaymentBehaviourAnalytics()
    for month in range(1, 5):
        pba.record_payment("C8", {"result": "MISSED", "due_date": date(2020, month, 28)})
    record = {"payment_channel": "standard_credit",
              "dd_fail_rate": pba.get_metrics("C8")["dd_fail_rate"],
              "payment_miss_trajectory": pba.get_miss_trajectory("C8")}
    assert pba.get_miss_trajectory("C8")[0]["missed"] == 4
    assert not record_asserts_dd_failure(record)
    pba.record_payment("C8", {"result": "DD_FAILED", "due_date": date(2020, 6, 28)})
    record["payment_miss_trajectory"] = pba.get_miss_trajectory("C8")
    assert record_asserts_dd_failure(record)
