"""The fresh-run grade counts a default-tariff bill over the household's ceiling, and only that.

Defect it exists to catch: a grade that counts by "before the first renewal" or ignores the
recorded tariff type, so a fixed bill priced above the cap is counted as an SVT breach (185 such
bills on 8b6fea024), or a grade that refuses everything and reports 0 of N.
"""

from tools.grade_svt_invoices_over_ceiling import grade


def _bill(cid: str, start: str, p_per_kwh_inc_vat: float) -> dict:
    net = 100 * p_per_kwh_inc_vat / 1.05 / 100.0
    return {"customer_id": cid, "period_start": start, "commodity": "electricity",
            "total_consumption_kwh": 100.0, "commodity_amount_gbp": net,
            "non_commodity_amount_gbp": 0.0, "vat_gbp": net * 0.05,
            "total_amount_gbp": net * 1.05, "billing_basis": "estimated"}


def _term(cid: str, tariff_type: str) -> dict:
    return {"customer_id": cid, "billing_account": cid, "term_start": "2019-01-01",
            "term_end": "2019-04-01", "tariff_type": tariff_type}


def test_the_partition():
    run = {
        "account_state_log": [_term("over", "svt"), _term("within", "svt"), _term("fix", "fixed")],
        "bills": [_bill("over", "2019-02-01", 99.0), _bill("within", "2019-02-01", 10.0),
                  _bill("fix", "2019-02-01", 99.0), _bill("no-term", "2019-02-01", 99.0)],
    }
    g = grade(run)
    # Both verdicts reachable, and the fixed and unrecorded bills are outside the denominator.
    assert g["default_tariff_invoices_graded"] == 2
    assert g["above_household_ceiling"] == 1
    assert g["households_above"] == 1
    assert g["outside_epg_windows"] == 1
    assert g["by_year"] == {"2019": 1}
