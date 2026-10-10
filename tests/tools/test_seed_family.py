"""Controls on the seed-family instrument. No simulation pass runs here; the live controls (same
seed twice, two seeds) are the family's own `same` and `readout` over real members.

Each test names the defect it catches.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from types import SimpleNamespace

import pytest

import tools.seed_family as sf
from simulation.live_population import _DEFAULT_BASE_SEED, founder_book

OTHER = 61001
GOOD = {"run_base_seed": _DEFAULT_BASE_SEED, "sample_rate": 1.0, "foreign_seed": False,
        "rolls_redrawn": 0, "triad_captured": True, "bad_debt_reconciliation_gbp": 0.0}


def test_the_seed_can_change_the_book_through_the_members_rebind():
    """DEFECT: a rebind that never reaches the draw -- every 'seed' is the default book, and a
    family of them reports a between-book spread of zero. Asked FIRST, through the same module
    global the member rebinds, before anything is asserted about what a family measures."""
    code = ("import sys, json\nimport simulation.live_population as lp\n"
            "lp._DEFAULT_BASE_SEED = int(sys.argv[1])\nlp.founder_accounts = lambda: 40\n"
            "print(json.dumps(sorted(json.dumps(r, sort_keys=True, default=str) "
            "for r in lp.founder_book(lp._DEFAULT_BASE_SEED))))\n")
    books = [json.loads(subprocess.run([sys.executable, "-c", code, str(s)], capture_output=True,
                                       text=True, check=True).stdout)
             for s in (_DEFAULT_BASE_SEED, OTHER, _DEFAULT_BASE_SEED)]
    assert books[0] != books[1], "the seed changed nothing about the founder book"
    assert books[0] == books[2], "the same seed drew two different books"
    assert founder_book(_DEFAULT_BASE_SEED)


def test_a_member_whose_run_drew_another_seed_is_refused():
    """DEFECT: a member that silently drew the default book under a foreign seed's label. The
    refusal must be able to pass as well as fire, or it is a refusal of everything."""
    assert sf.member_refusal(_DEFAULT_BASE_SEED, GOOD) is None
    fired = sf.member_refusal(OTHER, GOOD)
    assert fired and "_RUN_BASE_SEED" in fired and str(_DEFAULT_BASE_SEED) in fired


@pytest.mark.parametrize("field,value,says", [
    ("sample_rate", 0.36, "sample rate"),
    ("triad_captured", False, "triad"),
    ("bad_debt_reconciliation_gbp", 12.5, "P&L"),
    ("bad_debt_reconciliation_gbp", None, "P&L"),
])
def test_a_member_that_is_not_every_win_or_not_the_pnl_is_refused(field, value, says):
    """DEFECT: a weighted-sample book, a book with no payment truth, or a debt column that does
    not sum to the P&L, pooled as if it were an analysis book."""
    fired = sf.member_refusal(_DEFAULT_BASE_SEED, {**GOOD, field: value})
    assert fired and says in fired


def test_a_foreign_book_that_redrew_no_rolls_is_refused():
    """DEFECT: a foreign book whose shared founder ids rolled the default book's renewal dice."""
    foreign = {**GOOD, "run_base_seed": OTHER, "foreign_seed": True}
    assert "re-drew 0" in sf.member_refusal(OTHER, foreign)
    assert sf.member_refusal(OTHER, {**foreign, "rolls_redrawn": 7}) is None


def test_the_family_refuses_a_foreign_seed_without_the_directors_record(tmp_path):
    """DEFECT: the launcher running EP17 (a different cast of households) on the seat's say-so.
    And it must refuse BEFORE a unit starts."""
    started = []
    missing = tmp_path / "varied_population_draw_activation.json"
    with pytest.raises(SystemExit) as exc:
        sf.launch([_DEFAULT_BASE_SEED, OTHER], 40, tmp_path, "t", 4, {},
                  launcher=lambda *a, **k: started.append(a), record=missing)
    assert "EP17" in str(exc.value) and not started
    with pytest.raises(SystemExit, match="more than once"):
        sf.launch([_DEFAULT_BASE_SEED, _DEFAULT_BASE_SEED], 40, tmp_path, "t", 4, {},
                  launcher=lambda *a, **k: started.append(a), record=missing)
    sf.launch([_DEFAULT_BASE_SEED], 40, tmp_path, "t", 4, {},
              launcher=lambda job, cmd, **k: started.append((job, cmd, k)), record=missing)
    assert len(started) == 1 and str(_DEFAULT_BASE_SEED) in started[0][1]
    assert started[0][2]["peak_mb"] == sf.MEMBER_PEAK_MB
    # More seeds than may run side by side is refused, not silently queued behind admission.
    record = tmp_path / "ruled.json"
    record.write_text(json.dumps({"_meta": {"authority": "test"}, "activated": {"value": True},
                                  "base_seeds": {"value": [OTHER]}}), encoding="utf-8")
    with pytest.raises(SystemExit, match="waves"):
        sf.launch([_DEFAULT_BASE_SEED, OTHER], 40, tmp_path, "t", 1, {},
                  launcher=lambda *a, **k: started.append(a), record=record)
    assert len(started) == 1


def _lines(write_off=0.0, recovery=0.0, placeholder=0.0):
    return {"write_off_at_close_gbp": write_off, "write_off_statute_barred_gbp": 0.0,
            "stayer_provision_gbp": 0.0, "line_rounding_gbp": 0.0, "unbooked_bad_debt_gbp": 0.0,
            "dca_recovery_gbp": recovery, "unbooked_recovery_gbp": 0.0,
            "placeholder_bad_debt_released_gbp": placeholder}


def _run(lines=None):
    def rec(cid, day, net, bad_debt=0.0):
        return {"customer_id": cid, "settlement_date": day, "net_margin_gbp": net,
                "bad_debt_gbp": bad_debt, "segment": "resi"}
    return {
        "phase2b": {
            "all_records": [rec("C1", "2016-01-01", 6.0), rec("C1", "2019-12-31", 6.0),
                            rec("C1g", "2016-01-02", 5.0),
                            rec("PROS-2017-0001", "2017-03-01", 2.0, bad_debt=36.0)],
            "churned_billing_accounts": ["PROS-2017-0001"],
            "acquisition_funnel_log": [{"billing_account": "PROS-2017-0001", "won": True}],
            "arrears_lines_by_customer": lines or {},
        },
        "cost_to_serve": {"by_customer": {"C1": {"cost_to_serve_gbp": 2.0},
                                          "PROS-2017-0001": {"cost_to_serve_gbp": 4.0}}},
        "bills": [{"customer_id": "C1", "period_end": "2019-12-31"},
                  {"customer_id": "PROS-2017-0001", "period_end": "2018-03-31"}],
    }


def _pay(leg, due, result, days_late=None, settled_on=None):
    # The triad's own shape: `customer_id` is the leg, `account_id` is `ACC-<leg>`.
    return SimpleNamespace(customer_id=leg, account_id=f"ACC-{leg}",
                           due_date=date.fromisoformat(due), result=result,
                           days_late=days_late, settled_on=settled_on)


def test_a_home_folds_its_legs_and_ages_an_unpaid_bill_to_91_days():
    """DEFECT: a dual-fuel household counted as two homes, cost to serve left on the net, or a
    failed bill that never settles read as 0 days behind because it has no payment date."""
    rows, totals = sf.home_rows(
        1, _run({"C1g": _lines(placeholder=3.0),
                 "PROS-2017-0001": _lines(write_off=40.0, recovery=4.0)}),
        [_pay("C1g", "2019-01-14", "success", days_late=30),
         _pay("PROS-2017-0001", "2017-04-14", "failed"),
         _pay("C1", "2019-12-31", "success", days_late=0)],
        founders={"C1"},
        customers=[{"customer_id": "C1", "segment": "resi", "acquisition_date": "2016-01-01"},
                   {"customer_id": "C1g", "segment": "resi", "acquisition_date": "2015-12-01"},
                   {"customer_id": "NEVER-SETTLED", "segment": "resi"}])
    by = {r["home_id"]: r for r in rows}
    # One row per home: the legs fold, a payment keyed by the triad's account folds onto its
    # home, and a supply point that never settled is not a home.
    assert set(by) == {"C1", "PROS-2017-0001"}
    c1, pros = by["C1"], by["PROS-2017-0001"]
    assert c1["net_value_gbp"] == 15.0 and c1["route"] == "founder" and c1["still_supplied"]
    assert c1["first_settled"] == "2016-01-01" and c1["tenure_days"] == 1460
    assert c1["segment"] == "resi" and c1["acquired"] == "2015-12-01"
    assert c1["max_days_behind"] == 30 and not c1["behind_91"]
    assert c1["provisioned_bad_debt_gbp"] == 3.0 and c1["bad_debt_gbp"] == 0.0
    assert pros["route"] == "campaign_win" and not pros["still_supplied"]
    assert pros["net_value_gbp"] == -2.0
    # The home's arrears charge reconciles to the settled rows' own bad debt.
    assert pros["bad_debt_gbp"] == 36.0 == totals["bad_debt_gbp"]
    assert totals["legs_without_cost_to_serve"] == 1
    assert pros["max_days_behind"] == (date(2019, 12, 31) - date(2017, 4, 14)).days
    assert pros["behind_91"]


def test_two_tables_compare_identical_and_a_one_field_change_is_seen():
    """DEFECT: an identity check that reads every pair of books as the same."""
    a, _ = sf.home_rows(1, _run(), [], founders={"C1"})
    b, _ = sf.home_rows(2, _run(), [], founders={"C1"})
    assert sf.tables_identical(a, b) == []
    b[0] = {**b[0], "net_value_gbp": b[0]["net_value_gbp"] + 0.01}
    assert sf.tables_identical(a, b)


def _rows(n, behind_every, debt_every=10):
    return [{"seed": "1", "home_id": f"H{i}", "route": "campaign_win",
             "net_value_gbp": str((i % 50) * 40 - 500),
             "bad_debt_gbp": str(float(i % 7) if i % debt_every == 0 else 0.0),
             "behind_91": str(i % behind_every == 0)} for i in range(n)]


def test_the_readout_says_cannot_yet_tell_when_short_and_powered_when_not():
    """DEFECT: a read-out that publishes a verdict at any n (or refuses at every n)."""
    short = sf.readout(_rows(200, 10))
    assert all(q["verdict"].startswith("cannot yet tell") for q in short["questions"])
    assert all(q["homes_still_needed"] for q in short["questions"])
    big = sf.readout(_rows(60000, 10, debt_every=1))
    assert any(q["verdict"] == "powered" for q in big["questions"])
    lo, hi = big["behind_91"]["wilson_95"]
    assert lo < big["behind_91"]["share"] < hi


def test_the_power_formulae_print_the_textbook_values():
    """DEFECT: a power formula off by a factor (the commonest: a missing 2 for two arms)."""
    # sd = delta: 2 * (1.96 + 0.84)^2 = 15.7 -> 16 per arm.
    assert sf.n_per_arm_mean(1.0, 1.0) == 16
    # 10% -> 12.5% (Fleiss, no continuity correction): 2,507 per arm, worked by hand.
    assert sf.n_per_arm_share(0.10, 0.25) == 2507


def _origin_rows(founder_value, win_value, n=400):
    rows = []
    for i in range(n):
        route = "founder" if i % 4 == 0 else "campaign_win"
        rows.append({"seed": "1", "home_id": f"H{i}", "route": route,
                     "net_value_gbp": str((founder_value if route == "founder" else win_value)
                                          + (i % 10)),
                     "bad_debt_gbp": "0.0", "behind_91": str(i % 5 == 0)})
    return rows + [{"seed": "1", "home_id": "S0", "route": "home_move_successor",
                    "net_value_gbp": "5.0", "bad_debt_gbp": "0.0", "behind_91": "False"}]


def test_every_origin_is_read_alone_and_a_lone_home_says_cannot_yet_tell():
    """DEFECT (director's condition 1): a pooled answer that hides a founder/win split, or a
    one-home group published with an interval it cannot have."""
    out = sf.readout(_origin_rows(100.0, 300.0))
    assert set(out["by_origin"]) == set(sf.ORIGINS)
    assert out["by_origin"]["founder"]["homes"] == 100
    assert out["by_origin"]["campaign_win"]["homes"] == 300
    assert out["by_origin"]["founder"]["questions"]
    assert out["by_origin"]["home_move_successor"]["verdict"].startswith("cannot yet tell")
    assert out["by_origin"]["arrival"]["homes"] == 0


def test_the_mix_check_can_say_changes_and_can_say_it_does_not():
    """DEFECT: a mix check that reads every re-weighting as harmless (or as fatal). Founders
    worth 100 and wins 300 move a quarter-founder pool when the mix is half founders; equal
    values do not move at all."""
    half = {"source": "test", "shares": {"founder": 0.5, "campaign_win": 0.5}}
    split = sf.readout(_origin_rows(100.0, 300.0), [half])["mix_checks"][0]["quantities"][0]
    assert split["verdict"].startswith("CHANGES")
    same = sf.readout(_origin_rows(200.0, 200.0), [half])["mix_checks"][0]["quantities"][0]
    assert same["verdict"] == "does not change it"
    absent = {"source": "test", "shares": {"founder": 0.5, "change_of_tenancy": 0.5}}
    told = sf.readout(_origin_rows(100.0, 300.0), [absent])["mix_checks"][0]["quantities"][0]
    assert told["verdict"].startswith("cannot yet tell") and "change_of_tenancy" in told["verdict"]


def test_a_reference_books_mix_scales_its_sampled_wins_back_to_every_win():
    """DEFECT: the 400-founder book's mix read off its SETTLED homes alone, which under-counts
    the wins a weighted-sample book made by its sample rate."""
    report = {"per_customer_lifetime": {"C1": {}, "C1g": {}, "PROS-2017-0001": {},
                                        "OCC-1": {}},
              "acquisition_funnel_log": []}
    plain = sf.mix_of_report(report, {"C1"})
    assert plain["shares"] == {"founder": round(1 / 3, 4), "campaign_win": round(1 / 3, 4),
                               "change_of_tenancy": round(1 / 3, 4)}
    scaled = sf.mix_of_report(report, {"C1"}, wins_scale=2.0)
    assert scaled["shares"]["campaign_win"] == 0.5
