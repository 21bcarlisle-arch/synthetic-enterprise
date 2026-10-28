"""A successor's page and invoices print the meter point its predecessor printed.

Defect this catches: the MPAN, the MPRN and the meter serial were hashed from the ACCOUNT, so on
1691ec0ecd 253 of 253 incoming occupiers printed a different meter number from the account they
succeeded "at the same meter point" (home_moves.md §8.8, choice 6). A supply belongs to a meter point,
not to a household (home_moves.md, "What a gas supply is, at a move"). The same book's gas page header
and its invoices carried two different MPRN schemes, and the ledger's put 586 gas accounts on 164.

Each control is over the partition: a successor (and a successor of a successor) matches, and an
account at another point does not, so a key that collapsed every account onto one number also fails.

Mutations, each reds this file: either generator minting from `cid` again; `supply_point_of` returning
its argument; the ledger's `_mprn` reverting to its own scheme.
"""
import copy
import datetime as dt
import json

import tools.generate_customer_data as gcd
from company.crm.customer_registry import mprn, supply_point_of
from saas.bill_generator import generate_bill
from simulation.hedged_settlement import run_hedged_term
from simulation.settlement_daily import fold_to_days
from tools.generate_billing_ledger import generate as generate_ledger

#: predecessor <- successor <- its successor, per fuel leg, and one account at another meter point.
CHAIN = (("SYN-1", "OCC-a", "OCC-b"), ("SYN-1g", "OCC-ag", "OCC-bg"))
OTHER = ("SYN-2", "SYN-2g")
SUCCESSIONS = [{"account_id": s, "predecessor_account_id": p, "account_opened": "2023-02-01"}
               for leg in CHAIN for p, s in zip(leg, leg[1:])]


def _commodity(cid):
    return "gas" if cid.endswith("g") else "electricity"


def _pages(tmp_path, monkeypatch):
    lifetime = {cid: {"segment": "resi", "commodity": _commodity(cid), "revenue_gbp": 1.0}
                for cid in (*CHAIN[0], *CHAIN[1], *OTHER)}
    run = {"per_customer_lifetime": lifetime, "by_billing_account": {}, "per_cid_comm_pnl": {},
           "occupier_successions": SUCCESSIONS}
    path = tmp_path / "run.json"
    path.write_text(json.dumps(run))
    monkeypatch.setattr(gcd, "OUT_DIR", tmp_path / "out")
    monkeypatch.setattr(gcd, "_retire_departed_artefacts", lambda index: [])
    monkeypatch.setattr(gcd, "_meter", lambda cid, segment: "Traditional")
    gcd.generate(str(path))

    def number(cid):
        page = json.loads((tmp_path / "out" / (cid + ".json")).read_text())
        return page["mprn"] if cid.endswith("g") else page["mpan"]["bottom_line"]
    return number


def _ledger(tmp_path):
    d = dt.date(2023, 1, 1)
    prices = [{"settlementDate": (d + dt.timedelta(days=i)).isoformat(), "settlementPeriod": p,
               "systemSellPrice": 120.0} for i in range(31) for p in range(1, 49)]
    recs = run_hedged_term("SYN-T", "2023-01-01", "2023-02-01", 280.0, 120.0, 0.8, 0.0,
                           lambda ds: [0.25] * 48, prices)
    bills = []
    for cid in (CHAIN[0][0], CHAIN[0][1], CHAIN[0][2], OTHER[0]):
        bill = copy.deepcopy(generate_bill(cid, fold_to_days(recs), "fixed_1yr", None, "resi",
                                           "electricity"))
        bills.append(bill)
        gas = copy.deepcopy(bill)
        gas.update(customer_id=cid + "g", commodity="gas")
        bills.append(gas)
    run = {"bills": bills, "per_customer_behavioral": {}, "churned_billing_accounts": [],
           "occupier_successions": SUCCESSIONS}
    path = tmp_path / "ledger_run.json"
    path.write_text(json.dumps(run))
    customers = generate_ledger(path, tmp_path / "ledger.json")["customers"]

    def number(cid):
        (inv, *_) = customers[cid]["invoices"]
        return (inv["mprn"] if cid.endswith("g") else inv["mpan"]), inv["meter_serial"]
    return number


def test_a_successor_page_prints_its_predecessors_meter_number(tmp_path, monkeypatch):
    number = _pages(tmp_path, monkeypatch)
    for leg, other in zip(CHAIN, OTHER):
        assert len({number(cid) for cid in leg}) == 1, leg
        assert number(other) != number(leg[0]), "an account at another meter point printed the same"


def test_a_successor_invoice_prints_its_predecessors_meter_number_and_serial(tmp_path):
    number = _ledger(tmp_path)
    for leg, other in zip(CHAIN, OTHER):
        assert len({number(cid) for cid in leg}) == 1, leg
        assert number(other)[0] != number(leg[0])[0]


def test_the_page_header_and_the_invoices_print_one_number(tmp_path, monkeypatch):
    page, invoice = _pages(tmp_path, monkeypatch), _ledger(tmp_path)
    for cid in (*CHAIN[0], *CHAIN[1], *OTHER):
        assert page(cid) == invoice(cid)[0], cid


def test_a_chain_resolves_to_its_first_holder_and_a_loop_terminates():
    predecessor_of = {s["account_id"]: s["predecessor_account_id"] for s in SUCCESSIONS}
    assert supply_point_of("OCC-b", predecessor_of) == "SYN-1"
    assert supply_point_of("SYN-2", predecessor_of) == "SYN-2"
    assert supply_point_of("X", {"X": "Y", "Y": "X"}) in ("X", "Y")


def test_mprns_are_distinct_ten_digit_numbers():
    numbers = [mprn("SYN-%04dg" % i) for i in range(2000)]
    assert len(set(numbers)) == len(numbers)
    assert all(n.isdigit() and len(n) == 10 and n[0] != "0" for n in numbers)


def test_the_registry_seeds_a_home_movers_successor_on_its_predecessors_meter_point(tmp_path):
    """`saas.customers.SUCCESSOR_CUSTOMERS`: "same property as the predecessor"."""
    from company.crm.customer_registry import get_account, seed_from_customers
    db = tmp_path / "registry.db"
    seed_from_customers([{"customer_id": "C1", "commodity": "dual"},
                         {"customer_id": "C1_2", "commodity": "dual", "successor_of": "C1"},
                         {"customer_id": "C2", "commodity": "dual"}], db)
    c1, c1_2, c2 = (get_account(cid, db) for cid in ("C1", "C1_2", "C2"))
    assert (c1_2["mpan"], c1_2["mprn"]) == (c1["mpan"], c1["mprn"])
    assert c2["mpan"] != c1["mpan"] and c2["mprn"] != c1["mprn"]
