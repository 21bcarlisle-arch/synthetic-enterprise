"""The publisher grades a run's bills before it publishes them, and says so when it will not.

Defect it exists to catch: 8b6fea024 (19 Oct) billed 5,488 of 18,398 default-tariff bills above the
cap ceiling and was published, because nothing between the run and the page graded a bill; and
then the page said nothing. A refusal that cannot be taken passes every test of what it refuses,
so both sides of the partition are asserted in one place.
"""

import json

from background import process_run_complete as prc
from background import publish_provenance as prov


def test_the_refusal_partition_clean_defective_and_unrunnable():
    assert prc.billing_grade_refusal({}, grade_fn=lambda run: []) is None
    named = prc.billing_grade_refusal({}, grade_fn=lambda run: ["30 of 100 bills over"])
    assert named == "its bills fail the over-ceiling grade: 30 of 100 bills over"

    def broken(run):
        raise KeyError("bills")
    assert "could not run (KeyError" in prc.billing_grade_refusal({}, grade_fn=broken)


def test_the_real_grader_is_what_the_publisher_reads():
    """The default grade_fn is the grader itself: an empty run passes and an over-cap one refuses."""
    assert prc.billing_grade_refusal({"bills": [], "account_state_log": []}) is None
    over = {"customer_id": "o", "period_start": "2019-02-01", "commodity": "electricity",
            "total_consumption_kwh": 100.0, "commodity_amount_gbp": 94.29,
            "non_commodity_amount_gbp": 0.0, "vat_gbp": 4.71, "total_amount_gbp": 99.0,
            "billing_basis": "estimated"}
    run = {"bills": [over], "account_state_log": [
        {"customer_id": "o", "billing_account": "o", "term_start": "2019-01-01",
         "term_end": "2019-04-01", "tariff_type": "svt"}]}
    assert "over the household's ceiling" in prc.billing_grade_refusal(run)


def test_the_run_shown_gets_a_caveat_once_and_only_when_its_own_bills_fail(tmp_path, monkeypatch):
    p = tmp_path / "publish_provenance.json"
    monkeypatch.setattr(prov, "PROVENANCE_FILE", p)
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    (tmp_path / "docs" / "reports").mkdir(parents=True)
    run_id = "run_output_8b6fea024_20261019T033010Z.json"
    (tmp_path / "docs" / "reports" / run_id).write_text(json.dumps({"bills": []}))
    prov.record_verified(run_id=run_id, git_commit="8b6fea024", generated_at="2026-10-19T08:55:40Z",
                         population={"accounts": 1, "bills": 1, "total_revenue_gbp": 1.0}, path=p)

    assert prc._caveat_for_the_run_shown(grade_fn=lambda run: []) is None
    caveat = prc._caveat_for_the_run_shown(grade_fn=lambda run: ["5,488 of 18,398 bills over"])
    assert caveat.startswith("The billing, customer and debt figures shown come from run "
                             "8b6fea024 of 2026-10-19, and its bills fail")
    prov.record_figures_caveat("The seat's own sentence.", path=p)
    assert prc._caveat_for_the_run_shown(grade_fn=lambda run: ["x"]) is None


def test_the_publish_path_asks_it_before_anything_is_regenerated():
    """Without the call in `_process`, both functions above are true and nothing is refused."""
    import inspect
    src = inspect.getsource(prc._process)
    assert "billing_grade_refusal(data)" in src
    assert src.index("billing_grade_refusal(data)") < src.index("run_fast_tests(")
