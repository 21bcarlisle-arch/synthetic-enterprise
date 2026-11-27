"""A term that starts inside a bill carries the Day/Night pair its rate line was settled on.

Kept apart from `test_the_validator_checks_the_printed_rate_against_the_contracted_tariff.py`, whose
live-book reader stays red on the 6af7fd0bfd ledger until the next publish regenerates it with this fix.
"""
from __future__ import annotations


def test_a_term_that_starts_inside_a_bill_carries_the_pair_its_rate_line_was_settled_on():
    """A fixed term rolling to the SVT on the 8th: the SVT stub is no bill's `term_of_bill`, so
    its pair is read from the crossing bill's rate line. Left flat, the contract bound's ceiling
    sat under the Day rate the stub was charged at, and the 6af7fd0bfd book's 3 crossing bills
    read DISAGREED. MUTATION: drop the rate-line read in `_tou_terms` and the stub's pair is None."""
    from tools.generate_billing_ledger import _contracted_terms, _tou_terms

    terms = {"A": [{"term_start": "2017-08-01", "term_end": "2017-09-08", "tariff_type": "fixed",
                    "unit_rate_gbp_per_mwh": 101.548},
                   {"term_start": "2017-09-08", "term_end": "2017-10-01", "tariff_type": "svt",
                    "unit_rate_gbp_per_mwh": 147.619}]}
    regs = [{"label": "Day"}, {"label": "Night"}]
    lines = [{"term_start": "2017-08-01", "time_of_use": True},
             {"term_start": "2017-09-08", "time_of_use": True}]
    crossing = {"customer_id": "A", "period_start": "2017-09-01", "period_end": "2017-09-30",
                "registers": regs, "rate_lines": lines}
    out = _contracted_terms(terms, crossing, _tou_terms(terms, [crossing]))
    assert [t["tariff_type"] for t in out] == ["fixed", "svt"]
    assert all(t["tou_unit_rates"] for t in out), out
    # The partition: a stub line the biller settled flat keeps its flat rate.
    flat = dict(crossing, rate_lines=[lines[0], dict(lines[1], time_of_use=False)])
    out = _contracted_terms(terms, flat, _tou_terms(terms, [flat]))
    assert out[0]["tou_unit_rates"] and out[1]["tou_unit_rates"] is None


def test_a_crossing_bill_that_prints_no_registers_still_carries_its_pair_legs_pair():
    """A flat SVT stub then a fixed term settled on the pair: the bands hold only part of the kWh,
    so the bill withholds its registers. The fixed leg must still carry its pair, or it is checked
    at its flat rate and reads DISAGREED (PROS-2023-0135 Jun 2025, 601887d76a book).
    MUTATION: gate the rate-line read on `registers` again and the fixed term's pair is None."""
    from tools.generate_billing_ledger import _contracted_terms, _tou_terms

    terms = {"A": [{"term_start": "2025-04-01", "term_end": "2025-06-05", "tariff_type": "svt",
                    "unit_rate_gbp_per_mwh": 249.49},
                   {"term_start": "2025-06-05", "term_end": "2025-06-08", "tariff_type": "fixed",
                    "unit_rate_gbp_per_mwh": 196.518}]}
    lines = [{"term_start": "2025-04-01", "time_of_use": False},
             {"term_start": "2025-06-05", "time_of_use": True}]
    crossing = {"customer_id": "A", "period_start": "2025-06-01", "period_end": "2025-06-07",
                "registers": None, "rate_lines": lines}
    out = _contracted_terms(terms, crossing, _tou_terms(terms, [crossing]))
    assert out[0]["tou_unit_rates"] is None
    assert [b["register_label"] for b in out[1]["tou_unit_rates"]] == ["Peak", "Off-peak"]
