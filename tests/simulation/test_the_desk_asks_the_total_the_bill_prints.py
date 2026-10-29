"""The collections desk chases the total the issued bill prints, not the biller's unrounded total.

The defect this names: `payer_ask_gbp` took `bill["total_amount_gbp"]`, the biller's full-precision
sum, while the printed bill derives its total from its lines, each rounded to the penny
(`saas.money.foot_components_to_total`). The two round apart by up to a penny a bill, so on the
209c3350ab book the desk printed an overdue figure 1p to 7p above what the household's pages said
it owed on 2,328 collections steps (INV_OVERDUE_WITHIN_PAGE_BALANCE), one penny per open bill.
"""
from company.interfaces.bill_assembly import printed_total
from simulation import arrears_engine as ae


def _bill(**money):
    # OCC-17ff099218d5g's September 2020 gas bill on the 209c3350ab run, as the biller made it.
    return {"customer_id": "OCC-17ff099218d5g", "period_start": "2020-09-01",
            "period_end": "2020-09-30", "segment": "resi", "commodity": "gas", **money}


SEPT_2020 = dict(commodity_amount_gbp=5.40825, non_commodity_amount_gbp=2.66376,
                 standing_charge_gbp=7.8126, vat_gbp=0.7942305, total_amount_gbp=16.6788405)


def test_the_ask_is_the_printed_total_where_the_two_round_apart():
    bill = _bill(**SEPT_2020)
    # The control can fail: rounded once, the unrounded total is a penny above the printed bill.
    assert round(bill["total_amount_gbp"], 2) == 16.68
    assert printed_total(bill) == 16.67
    assert ae.payer_ask_gbp(bill) == 16.67


def test_a_catch_up_line_is_in_the_printed_total():
    bill = _bill(**dict(SEPT_2020, catchup_applied=True, catchup_adjustment_gbp=-3.004,
                        total_amount_gbp=SEPT_2020["total_amount_gbp"] - 3.004))
    assert printed_total(bill) == 13.67
    assert ae.payer_ask_gbp(bill) == 13.67


def test_an_occupier_share_is_taken_of_the_printed_total():
    bill = _bill(**dict(SEPT_2020, occupier_share=0.5))
    assert ae.payer_ask_gbp(bill) == round(16.67 * 0.5, 2)
