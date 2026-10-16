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


def test_the_launch_command_follows_every_member_to_its_end(monkeypatch, tmp_path):
    """DEFECT (director's condition 3, 2026-10-10: "Every job you queue must wake you when it
    finishes"): a launch that returns when the units are scheduled, so nothing ends with them."""
    import background.launch_long_job as llj
    followed = []
    monkeypatch.setattr(sf, "launch", lambda *a, **k: [{"unit": "u1", "artefact": "a1"},
                                                       {"unit": "u2", "artefact": "a2"}])
    monkeypatch.setattr(llj, "follow_unit", lambda unit, art, **k: followed.append(unit) or 0)
    argv = ["launch", "--seeds", "1,2", "--tag", "t", "--out", str(tmp_path)]
    assert sf.main(argv) == 0 and followed == ["u1", "u2"]
    followed.clear()
    assert sf.main(argv + ["--detach"]) == 0 and followed == []


def test_a_member_with_no_room_yet_queues_instead_of_stranding_the_family(tmp_path):
    """DEFECT: a family refused mid-launch for room, leaving the members already started running
    with nothing following them and the rest never launched."""
    from background.launch_long_job import NoRoom
    calls, slept = [], []

    def launcher(job, cmd, **k):
        calls.append(job)
        if len(calls) == 2:
            raise NoRoom("no room for the second member yet")
        return {"unit": job, "artefact": k["artefact"]}
    record = tmp_path / "ruled.json"
    record.write_text(json.dumps({"_meta": {"authority": "test"}, "activated": {"value": True},
                                  "base_seeds": {"value": [OTHER, OTHER + 1]}}), encoding="utf-8")
    entries = sf.launch([OTHER, OTHER + 1], 40, tmp_path, "t", 4, {}, launcher=launcher,
                        record=record, sleep=slept.append)
    assert [e["unit"] for e in entries] == [f"seed-family-t-{OTHER}", f"seed-family-t-{OTHER + 1}"]
    assert len(slept) == 1


def test_a_founders_only_book_that_settled_a_win_is_refused():
    """DEFECT (director, 2026-10-11): a 'back book' that quietly settled campaign wins -- a
    budget that let wins through, or a table carrying a won home -- read as founders only. And the
    shape's own mechanism: a zero budget, which leaves the campaign no headroom to settle into."""
    back = {**GOOD, "shape": "founders_only", "sample_rate": 0.0, "wins_settled": 0,
            "campaign_win_homes": 0}
    assert sf.member_refusal(_DEFAULT_BASE_SEED, back) is None
    assert "settled 3" in sf.member_refusal(_DEFAULT_BASE_SEED, {**back, "wins_settled": 3})
    assert "2 campaign-win" in sf.member_refusal(_DEFAULT_BASE_SEED,
                                                 {**back, "campaign_win_homes": 2})
    # The all-wins shape is unchanged: it still demands every win.
    assert "sample rate" in sf.member_refusal(_DEFAULT_BASE_SEED, {**GOOD, "sample_rate": 0.0})
    assert sf.SHAPES["founders_only"] == {"founders": 400, "budget": 0.0}


def test_a_zero_budget_settles_no_win_through_the_campaigns_own_settlement():
    """The mechanism, asked of `settle_within_budget` itself: with founders already committed and
    a zero budget, the headroom is 0 and no candidate is booked."""
    from simulation.net_new_acquisition import settle_within_budget
    out = settle_within_budget([(2017, None, None, 1.0), (2018, None, None, 2.0)],
                                           committed_cy=500.0, customer_year_budget=0.0)
    assert out["sample_rate"] == 0.0
    assert sum(out["booked_by_year"].values()) == 0 and not out["winners"]
    # ...and the same call with room books both, so the zero is the budget's doing.
    room = settle_within_budget([(2017, None, None, 1.0), (2018, None, None, 2.0)],
                                committed_cy=500.0, customer_year_budget=1e9)
    assert sum(room["booked_by_year"].values()) == 2


# --- B11: the policy door and the measures the flat-against-per-customer prereg reads ----------

def _valued_run(psr=True):
    def rec(cid, day, kwh, revenue, fuel=None):
        r = {"customer_id": cid, "settlement_date": day, "consumption_kwh": kwh,
             "revenue_gbp": revenue, "wholesale_cost_gbp": revenue / 2, "margin_gbp": revenue / 2,
             "net_margin_gbp": revenue / 4, "bad_debt_gbp": 0.0, "segment": "resi"}
        if fuel:
            r["commodity"] = fuel
        return r
    run = {"phase2b": {
        "all_records": [rec("C1", "2018-01-01", 1000.0, 150.0, "electricity"),
                        rec("C1g", "2018-01-01", 2000.0, 60.0, "gas"),
                        rec("C2", "2018-01-01", 500.0, 80.0),
                        rec("C3", "2018-01-01", 100.0, 20.0),
                        rec("C3", "2019-01-01", 100.0, 20.0)],
        "churned_billing_accounts": [], "acquisition_funnel_log": [],
        "arrears_lines_by_customer": {}}}
    if psr:
        run["phase2b"]["psr_registrations"] = [{"account_id": "C1g",
                                                "registration_date": "2018-01-01",
                                                "categories": []}]
    return run


def _rate(day, fuel):
    """£/MWh: electricity 200, gas 40; no published rate for 2019."""
    if day.year == 2019:
        return None
    return {"electricity": 200.0, "gas": 40.0}[fuel]


def test_a_home_carries_its_saving_kwh_per_fuel_gas_leg_and_our_flag():
    """DEFECT: the legs' saving or kWh not folded onto the home, gas kWh counted as electricity,
    a home with a year we could not value given a partial saving, or a flag on the gas leg alone
    missing its home."""
    rows, _ = sf.home_rows(1, _valued_run(), [], founders=set(), svt_rate_for=_rate)
    by = {r["home_id"]: r for r in rows}
    c1, c2, c3 = by["C1"], by["C2"], by["C3"]
    # (1 MWh x 200 - 150) + (2 MWh x 40 - 60) = 50 + 20
    assert c1["household_saving_gbp"] == 70.0
    assert c1["kwh_elec"] == 1000.0 and c1["kwh_gas"] == 2000.0 and c1["has_gas_leg"]
    assert c1["company_vulnerability_flag"] is True
    # A record naming no fuel is electricity, as the value view reads it.
    assert c2["household_saving_gbp"] == 20.0 and c2["kwh_elec"] == 500.0
    assert c2["kwh_gas"] == 0.0 and not c2["has_gas_leg"]
    assert c2["company_vulnerability_flag"] is False
    # 2019 has no published rate, so C3's saving is unknown, not its 2018 half.
    assert c3["household_saving_gbp"] is None and c3["kwh_elec"] == 200.0
    assert set(sf.COLUMNS) >= {"household_saving_gbp", "kwh_elec", "kwh_gas", "has_gas_leg",
                               "company_vulnerability_flag"}


def test_no_register_reads_unknown_and_an_unvalued_home_reads_no_saving():
    """DEFECT: a run with no register read as nobody flagged, or a home the view could not
    value at all read as saving nothing."""
    rows, _ = sf.home_rows(1, _valued_run(psr=False), [], founders=set(),
                           svt_rate_for=lambda d, f: None)
    assert {r["company_vulnerability_flag"] for r in rows} == {None}
    assert {r["household_saving_gbp"] for r in rows} == {None}


def test_an_unknown_fuel_is_refused_not_guessed():
    run = _valued_run()
    run["phase2b"]["all_records"][0]["commodity"] = None
    with pytest.raises(ValueError, match="fuel None"):
        sf.home_rows(1, run, [], founders=set(), svt_rate_for=_rate)


@pytest.mark.parametrize("name", sorted(sf.POLICY_NAMES))
def test_every_policy_a_member_can_take_resolves_to_the_policy_of_that_name(name):
    assert sf.policy_named(name).name == name


def test_the_book_runs_under_the_policy_both_entered_and_passed(monkeypatch):
    """DEFECT: the policy passed but not entered (the collections tone stays current's), or
    entered but not passed (the run loop prices and offers as current)."""
    import simulation.run_phase4c_on_phase2b as p4
    from company.policy.decision_policy import CURRENT_POLICY, active_policy
    seen = {}
    monkeypatch.setattr(p4, "main", lambda policy=None, **k: seen.update(
        passed=policy, active=active_policy()) or {})
    flat = sf.policy_named("flat_supplier")
    sf.run_book(flat)
    assert seen == {"passed": flat, "active": flat}
    assert active_policy() is CURRENT_POLICY


def test_a_launch_hands_each_member_its_policy(tmp_path):
    argvs = []
    sf.launch([_DEFAULT_BASE_SEED], 40, tmp_path, "t", 1, {},
              launcher=lambda name, argv, **k: argvs.append(argv) or {"unit": name},
              policy="flat_supplier")
    assert argvs[0][argvs[0].index("--policy") + 1] == "flat_supplier"
    argvs.clear()
    sf.launch([_DEFAULT_BASE_SEED], 40, tmp_path, "t", 1, {},
              launcher=lambda name, argv, **k: argvs.append(argv) or {"unit": name})
    assert argvs[0][argvs[0].index("--policy") + 1] == "current"


def test_members_of_one_policy_pool_and_of_two_are_refused():
    """The partition: a refusal that fired on every pool would pass the refusing leg. A record
    from before the stamp ran under current."""
    assert sf.mixed_policy_refusal([{"seed": 1, "policy": "current"}, {"seed": 2}]) is None
    why = sf.mixed_policy_refusal([{"seed": 1, "policy": "flat_supplier"}, {"seed": 2}])
    assert why and "flat_supplier: seeds [1]" in why and "current: seeds [2]" in why


def test_the_readout_refuses_directories_run_under_two_policies(tmp_path, capsys):
    rows, _ = sf.home_rows(_DEFAULT_BASE_SEED, _valued_run(), [], founders=set(),
                           svt_rate_for=_rate)
    for d, policy in (("a", "current"), ("b", "flat_supplier")):
        (tmp_path / d).mkdir()
        (tmp_path / d / f"member_{_DEFAULT_BASE_SEED}.json").write_text(json.dumps(
            {**GOOD, "seed": _DEFAULT_BASE_SEED, "policy": policy}))
        sf.write_table(rows, tmp_path / d / f"homes_{_DEFAULT_BASE_SEED}.csv")
    assert sf.main(["readout", str(tmp_path / "b")]) == 0
    assert json.loads(capsys.readouterr().out)["policy"] == "flat_supplier"
    assert sf.main(["readout", str(tmp_path / "a"), str(tmp_path / "b")]) == 2
    assert "REFUSED: members ran under 2 policies" in capsys.readouterr().out


# --- B11 item 4: the flat-at-level member, at the level its own seed's value arm chose ----------

def _value_member(tmp_path, over=None, seed=_DEFAULT_BASE_SEED):
    meta = {**GOOD, "seed": seed, "policy": "value_arm", "commit": "c0", "refused": None,
            "value_arm_median_margin_gbp_per_mwh": 44.5, **(over or {})}
    (tmp_path / f"member_{seed}.json").write_text(json.dumps(meta))
    return tmp_path


def test_a_value_arm_member_of_this_seed_and_commit_sets_the_level_and_every_other_source_is_refused(
        tmp_path):
    """DEFECT: a level arm held at a number this book did not produce. The admitting leg is asked
    FIRST: a check refusing every source passes all the refusing legs below."""
    s = _DEFAULT_BASE_SEED
    assert sf.level_source_refusal(s, _value_member(tmp_path), "c0") is None
    assert sf._level_of(s, tmp_path) == 44.5
    assert "no --level-from" in sf.level_source_refusal(s, None, "c0")
    assert "does not exist" in sf.level_source_refusal(s + 1, tmp_path, "c0")
    assert "ran at 'c0'" in sf.level_source_refusal(s, tmp_path, "c1")
    for over, why in (({"refused": "x"}, "was refused"), ({"policy": "current"}, "not value_arm"),
                      ({"seed": OTHER}, "records seed"),
                      ({"value_arm_median_margin_gbp_per_mwh": None}, "chose no level")):
        assert why in sf.level_source_refusal(s, _value_member(tmp_path, over), "c0"), over
    (tmp_path / f"member_{s}.json").write_text(json.dumps(
        {k: v for k, v in {**GOOD, "seed": s, "commit": "c0",
                           "value_arm_median_margin_gbp_per_mwh": 44.5}.items()}))
    assert "not value_arm" in sf.level_source_refusal(s, tmp_path, "c0"), "unstamped = current"


def test_the_level_policy_is_the_flat_supplier_renewing_everyone_at_the_level():
    """DEFECT: the level arm built on CURRENT_POLICY (per-customer retention back in, which is
    `run_value_cycle_ab --level-arm`'s arm, not the prereg's) or at a defaulted level."""
    from dataclasses import fields

    from company.policy.decision_policy import FLAT_SUPPLIER_POLICY
    from company.pricing.value_based_renewal import FLAT_AT_LEVEL
    level = sf.policy_named(sf.LEVEL_POLICY, 44.5)
    differ = {f.name for f in fields(level)
              if getattr(level, f.name) != getattr(FLAT_SUPPLIER_POLICY, f.name)}
    assert differ == {"name", "renewal_margin_arm", "renewal_margin_flat_level_gbp_per_mwh"}
    assert (level.name, level.renewal_margin_arm, level.renewal_margin_flat_level_gbp_per_mwh) == (
        sf.LEVEL_POLICY, FLAT_AT_LEVEL, 44.5)
    with pytest.raises(SystemExit, match="needs the level"):
        sf.policy_named(sf.LEVEL_POLICY)


def test_a_member_stamps_the_median_its_value_arm_chose(tmp_path):
    """DEFECT: the value-arm member records no median, so no level member can ever run."""
    run = {"phase2b": {"value_arm_log": [{"chosen_margin_gbp_per_mwh": m} for m in (3.0, 44.5, 60.0)]
                       + [{"declined": True}]}}
    stamp = sf.level_stamp(run, None, None)
    assert stamp["value_arm_median_margin_gbp_per_mwh"] == 44.5
    assert (stamp["value_arm_priced"], stamp["value_arm_declined"]) == (3, 1)
    assert sf.level_stamp({"phase2b": {}}, None, None)["value_arm_median_margin_gbp_per_mwh"] is None
    assert sf.level_stamp(run, 44.5, tmp_path)["level_from"] == str(tmp_path)


def test_a_level_launch_reads_every_source_first_and_hands_each_member_its_directory(
        tmp_path, monkeypatch):
    """DEFECT: a level family half-launched behind a missing value-arm member, or members launched
    without the directory their level comes from."""
    monkeypatch.setattr(sf, "_head", lambda: "c0")
    argvs = []
    sf.launch([_DEFAULT_BASE_SEED], 40, tmp_path / "out", "t", 1, {},
              launcher=lambda name, argv, **k: argvs.append(argv) or {"unit": name},
              policy=sf.LEVEL_POLICY, level_from=_value_member(tmp_path))
    assert argvs[0][argvs[0].index("--level-from") + 1] == str(tmp_path.resolve())
    argvs.clear()
    with pytest.raises(SystemExit, match="does not exist"):
        sf.launch([_DEFAULT_BASE_SEED, 61101], 40, tmp_path / "out", "t", 2, {},
                  launcher=lambda name, argv, **k: argvs.append(argv) or {"unit": name},
                  record=None, policy=sf.LEVEL_POLICY, level_from=tmp_path)
    assert argvs == []
