"""With home moves on (director, 2026-10-08), phase 4c must see the accounts a move supplies.

Defect: `_get_all_customers()` listed founders, successors and wins only, so the first full run
with moves on raised KeyError on OCC-* in `saas.cost_to_serve` after settlement had completed.
"""
from company.interfaces import supply_book
from simulation import run_phase4c_on_phase2b as p4


def test_an_incoming_occupant_admitted_by_the_run_is_in_phase_4cs_customer_list(monkeypatch):
    occupant = {"customer_id": "OCC-test", "segment": "resi", "commodity": "electricity"}
    monkeypatch.setattr(supply_book, "INCOMING_OCCUPANT_CUSTOMERS", [occupant])
    ids = {c["customer_id"] for c in p4._get_all_customers()}
    assert "OCC-test" in ids
    monkeypatch.setattr(supply_book, "INCOMING_OCCUPANT_CUSTOMERS", [])
    assert "OCC-test" not in {c["customer_id"] for c in p4._get_all_customers()}
