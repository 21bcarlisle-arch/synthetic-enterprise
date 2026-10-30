"""One meter serial names one physical meter, so it sits on one supply point (fifth cold read, N10).

Defect this catches: the ledger minted the serial as a sum of the id's character codes, which ignores
their order. Ids share one format, so the sums fell in a narrow band: the 3dc5a92948 book's 1,293
pages carried 127 serials, 96 of them on 2 to 34 supply points in different regions.

Mutations, each reds this file: the ledger minting its own serial again (any order-blind sum);
`meter_serial` dropping the supply point or the fuel from its key; the evaluator not keying on the
supply point, or keying on the account.
"""
import copy
import datetime as dt
import json

from company.crm.customer_registry import meter_serial
from saas.bill_generator import generate_bill
from simulation.hedged_settlement import run_hedged_term
from simulation.settlement_daily import fold_to_days
from tools import domain_invariant_runner as runner
from tools.generate_billing_ledger import generate as generate_ledger

#: Two supply points whose ids are permutations of each other, as the run's ids often are.
PERMUTED = ("SYN-2016-476", "SYN-2016-467")


def _ids():
    yield from ("SYN-2016-%03d" % i for i in range(1000))
    yield from ("PROS-%d-%04d" % (y, i) for y in range(2016, 2026) for i in range(400))
    yield from ("OCC-%012x" % (i * 7919) for i in range(1000))


def test_permuted_supply_points_get_distinct_serials_on_the_ledger(tmp_path):
    d = dt.date(2023, 1, 1)
    prices = [{"settlementDate": (d + dt.timedelta(days=i)).isoformat(), "settlementPeriod": p,
               "systemSellPrice": 120.0} for i in range(31) for p in range(1, 49)]
    recs = run_hedged_term("SYN-T", "2023-01-01", "2023-02-01", 280.0, 120.0, 0.8, 0.0,
                           lambda ds: [0.25] * 48, prices)
    bills = [copy.deepcopy(generate_bill(cid, fold_to_days(recs), "fixed_1yr", None, "resi", "electricity"))
             for cid in PERMUTED]
    path = tmp_path / "run.json"
    path.write_text(json.dumps({"bills": bills, "per_customer_behavioral": {},
                                "churned_billing_accounts": [], "occupier_successions": []}))
    customers = generate_ledger(path, tmp_path / "ledger.json")["customers"]
    serials = [customers[cid]["invoices"][0]["meter_serial"] for cid in PERMUTED]
    assert serials == [meter_serial(cid, "electricity") for cid in PERMUTED]
    assert serials[0] != serials[1]


def test_serials_are_distinct_across_the_runs_id_formats_and_fuels():
    points = [(sp, fuel) for sp in _ids() for fuel in ("electricity", "gas")]
    serials = [meter_serial(sp, fuel) for sp, fuel in points]
    assert len(set(serials)) == len(points)
    assert all(s[0] == "M" and s[1:].isdigit() and len(s) == 11 for s in serials)


def _period(cid, sp, start, end, serial="M1", fuel="electricity"):
    return {"customer_id": cid, "segment": "resi", "periods": [{
        "commodity": fuel, "period_start": start, "period_end": end, "meter_serial": serial,
        "mpan": sp if fuel == "electricity" else None, "mprn": sp if fuel == "gas" else None}]}


def _grade(*accounts):
    book = [runner.Account("A%d" % i, a) for i, a in enumerate(accounts)]
    t = runner.ev_meter_serial_one_supply_point(None, book)
    return sorted({h["side"] for h in t.breaches}), sorted({h["side"] for h in t.flags}), t.checked


def test_every_leg_of_the_one_serial_one_supply_point_row_is_reachable():
    """Each leg is reached before any is asserted, so an evaluator that refuses everything, or
    nothing, cannot pass."""
    legs = {
        # successive occupiers on one supply point share its meter: lawful, whatever the account
        "occupiers": _grade(_period("A", "1000000000110", "2020-01-01", "2020-06-30"),
                            _period("B", "1000000000110", "2020-07-01", "2020-12-31")),
        "simultaneous": _grade(_period("A", "1000000000110", "2020-01-01", "2020-06-30"),
                               _period("B", "1000000000220", "2020-06-01", "2020-12-31")),
        "two_regions": _grade(_period("A", "1000000000110", "2020-01-01", "2020-06-30"),
                              _period("B", "1500000000110", "2020-07-01", "2020-12-31")),
        "same_region": _grade(_period("A", "1000000000110", "2020-01-01", "2020-06-30"),
                              _period("B", "1000000000220", "2020-07-01", "2020-12-31")),
        # the proxy: a new meter on the earlier point and the old one leaving the later point
        "exchanged": _grade(_period("A", "1000000000110", "2020-01-01", "2020-06-30"),
                            _period("C", "1000000000110", "2020-07-01", "2020-12-31", serial="M2"),
                            _period("D", "1500000000110", "2020-01-01", "2020-06-30", serial="M3"),
                            _period("B", "1500000000110", "2020-07-01", "2020-12-31")),
        "gas_moves": _grade(_period("A", "2001", "2020-01-01", "2020-06-30", fuel="gas"),
                            _period("B", "9001", "2020-07-01", "2020-12-31", fuel="gas")),
        "fuels_apart": _grade(_period("A", "1000000000110", "2020-01-01", "2020-12-31"),
                              _period("B", "2001", "2020-01-01", "2020-12-31", fuel="gas")),
    }
    assert legs == {
        "occupiers": ([], [], 2),
        "simultaneous": (["simultaneous_two_supply_points"], [], 2),
        "two_regions": (["two_regions_no_exchange"], [], 2),
        "same_region": ([], ["sequential_same_region_no_exchange"], 2),
        "exchanged": ([], [], 4),
        "gas_moves": ([], ["sequential_same_region_no_exchange"], 2),
        "fuels_apart": ([], [], 2),
    }


def test_the_row_is_checkable_and_graded_by_the_runner():
    import yaml
    row = next(i for i in yaml.safe_load(runner.INVARIANTS_PATH.read_text())["invariants"]
               if i["id"] == "INV_METER_SERIAL_ONE_SUPPLY_POINT")
    assert row.get("checkable", True) is True
    (result,) = runner.run([row], {"A": _period("A", "1000000000110", "2020-01-01", "2020-06-30"),
                                   "B": _period("B", "1500000000110", "2020-01-01", "2020-06-30")})
    assert result["status"] == "BREACHED", result
