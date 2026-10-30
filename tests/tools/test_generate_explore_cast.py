"""Explore's cast: the supplier view never looks ahead, and each feature rule can both fill and fail.

Keyed to the property, never to today's cast: which household fills a slot is supposed to move
with every run. What must hold whatever the run is: no supplier row reads a record dated after its
moment, every slot is either filled or says why not, and each coverage rule fires on a household
that breaks it and stays quiet on one that does not.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from tools import generate_explore_cast as gen

FEED = gen.OUT_PATH


@pytest.fixture(scope="module")
def real():
    if not gen.SAMPLE_PATH.is_file() or not any(gen.CUSTOMERS_DIR.glob("*.json")):
        pytest.skip("no published run on disk")
    customers = gen._load_customers(gen.CUSTOMERS_DIR)
    sample = json.loads(gen.SAMPLE_PATH.read_text(encoding="utf-8"))
    return customers, sample, gen._cap_windows()


@pytest.fixture(scope="module")
def feed(real):
    return gen.build(*real)


def _look_ahead(feed) -> list[str]:
    bad = []
    for s in feed["slots"]:
        for m in s.get("moments", []):
            for r in m["supplier"]:
                if r["drawn_from"] > m["iso"]:
                    bad.append("{} {} {}: '{}' drawn from {}".format(s["id"], s["household"], m["iso"], r["k"], r["drawn_from"]))
    return bad


def test_no_supplier_row_reads_a_record_dated_after_its_moment(feed):
    rows = [r for s in feed["slots"] for m in s.get("moments", []) for r in m["supplier"]]
    assert rows, "no supplier rows at all -- this control would be vacuous"
    assert not _look_ahead(feed), _look_ahead(feed)[:5]


def _decided_after_outcome(feed) -> list[str]:
    """A decision moment must not show the outcome of the decision it is making, even same-day."""
    bad = []
    for s in feed["slots"]:
        for m in s.get("moments", []):
            if m["kind"] != "renewal_decision":
                continue
            if "outcome" in m["decision"].lower() or any(r["k"] == "Tariff" and r["drawn_from"] == m["iso"] for r in m["supplier"]):
                bad.append("{} {} {}".format(s["id"], s["household"], m["iso"]))
    return bad


def test_a_decision_moment_does_not_show_the_outcome_it_is_deciding(feed):
    decisions = [m for s in feed["slots"] for m in s.get("moments", []) if m["kind"] == "renewal_decision"]
    assert decisions, "no renewal decision in the cast -- this control would be vacuous"
    assert not _decided_after_outcome(feed), _decided_after_outcome(feed)


def test_MUTATION_a_decision_moment_shown_its_same_day_outcome_is_caught(real, monkeypatch):
    monkeypatch.setattr(gen, "_before_outcome", lambda ev, iso: ev)
    assert _decided_after_outcome(gen.build(*real)), "a decision shown its own outcome passed the control"


def test_MUTATION_a_supplier_view_given_the_whole_record_is_caught(real):
    """Swap the as-of filter for the identity: every later record now reaches the supplier view."""
    leaky = gen.build(*real, known_by=lambda records, iso: list(records))
    assert _look_ahead(leaky), "a supplier view reading the whole record passed the no-look-ahead control"


def test_every_slot_is_filled_or_names_why_not(feed):
    assert feed["slots"], "the cast has no slots"
    for s in feed["slots"]:
        if s["filled"]:
            assert s["moments"] and 0 <= s["opening"] < len(s["moments"]), s["id"]
            assert len(s["moments"]) <= 6, s["id"]
        else:
            assert len(s.get("reason", "")) > 40, "{} is empty and does not say why".format(s["id"])


def test_the_cast_is_chosen_by_rule_and_no_household_plays_two_parts(feed):
    ids = [s["household"] for s in feed["slots"] if s["filled"]]
    assert len(ids) == len(set(ids)), ids
    assert all(s["rule"] for s in feed["slots"])


def test_every_filled_slots_moments_are_its_own_households(real, feed):
    customers = real[0]
    for s in feed["slots"]:
        if s["filled"]:
            assert s["household"] in customers, s["household"]


def test_the_page_carries_the_feed_written_at_publish(feed):
    """The opening moment is in the page's markup, so a reader without JavaScript meets the cast."""
    html = gen.static_html(feed)
    for s in feed["slots"]:
        assert s["feature"] in html
        if not s["filled"]:
            assert gen.html.escape(s["reason"][:30]) in html


# ── the coverage rules: each can fire, and each stays quiet on a household that keeps it ──────


def _hh(invoices, timeline=(), gas=None, gas_timeline=()):
    legs = {"electricity": {"account_id": "T1", "commodity": "electricity", "acquisition_date": "2019-01-01",
                            "invoices": list(invoices), "timeline": list(timeline), "ledger": {"entries": []},
                            "reaction_chain": []}}
    if gas is not None:
        legs["gas"] = {"account_id": "T1g", "commodity": "gas", "acquisition_date": "2019-01-01",
                       "invoices": list(gas), "timeline": list(gas_timeline), "ledger": {"entries": []},
                       "reaction_chain": []}
    hh = {"id": "T1", "legs": legs}
    return hh, gen._events(hh)


def _inv(d, kwh, energy, vat_rate=0.05, **kw):
    net = energy + 10.0
    return {"date": d, "period_start": d[:8] + "01", "consumption_kwh": kwh, "commodity_amount_gbp": energy,
            "non_commodity_amount_gbp": 0.0, "standing_charge_gbp": 10.0, "vat_gbp": round(net * vat_rate, 2),
            "amount_gbp": round(net * (1 + vat_rate), 2), "read_type": "A", **kw}


WINDOWS = [{"from": "2022-10-01", "to": "2022-12-31", "elec": 518.9, "gas": 147.6, "elec_epg": 340.0, "gas_epg": 103.2}]


def test_the_cap_rule_can_fire_and_stays_quiet_under_the_ceiling():
    over = _hh([_inv("2022-11-30", 500, 500 * 0.50 / 1.05)])  # 50p inc VAT against a 34p ceiling
    under = _hh([_inv("2022-11-30", 500, 500 * 0.33 / 1.05)])
    assert [b["rule"] for b in gen.coverage_breaches(*over, WINDOWS, "resi")] == ["above_cap"]
    assert gen.coverage_breaches(*under, WINDOWS, "resi") == []


def test_the_cap_rule_reads_the_EPG_where_it_was_in_force_not_the_ofgem_level():
    """51.9p is exactly the Ofgem cap for Oct-Dec 2022 and 18p above what the household could be charged."""
    at_ofgem = _hh([_inv("2022-11-30", 500, 500 * 0.5189 / 1.05)])
    assert gen.coverage_breaches(*at_ofgem, WINDOWS, "resi"), "a bill at the Ofgem level passed under the EPG"


def test_the_cap_rule_skips_a_bill_after_a_fixed_renewal_and_a_business_account():
    renewed = [{"date": "2022-06-01", "type": "renewed", "detail": "Tariff renewed at 300 £/MWh"}]
    fixed = _hh([_inv("2022-11-30", 500, 500 * 0.50 / 1.05)], timeline=renewed)
    assert gen.coverage_breaches(*fixed, WINDOWS, "resi") == []
    sme = _hh([_inv("2022-11-30", 500, 500 * 0.50 / 1.05)])
    assert gen.coverage_breaches(*sme, WINDOWS, "sme") == []


def test_the_cap_rule_grades_the_recorded_term_not_the_renewal_proxy():
    """Same 50p bill, no renewal on the timeline: the recorded verdict decides, both ways."""
    over = dict(term_tariff_type="svt", default_tariff_excess_p_per_kwh=16.0)
    fixed = dict(term_tariff_type="fixed", default_tariff_excess_p_per_kwh=0.0)
    unrecorded = dict(term_tariff_type=None, default_tariff_excess_p_per_kwh=None)
    bill = (500, 500 * 0.50 / 1.05)
    assert [b["rule"] for b in gen.coverage_breaches(*_hh([_inv("2022-11-30", *bill, **over)]), WINDOWS, "resi")] == ["above_cap"]
    assert gen.coverage_breaches(*_hh([_inv("2022-11-30", *bill, **fixed)]), WINDOWS, "resi") == []
    assert gen.coverage_breaches(*_hh([_inv("2022-11-30", *bill, **unrecorded)]), WINDOWS, "resi") == []


def test_the_cap_rule_trusts_an_svt_verdict_even_after_a_renewal_dated_earlier():
    """A default term after a renewal (a fix that lapsed to SVT) is capped; the proxy would skip it."""
    renewed = [{"date": "2022-06-01", "type": "renewed", "detail": "x"}]
    svt = dict(term_tariff_type="svt", default_tariff_excess_p_per_kwh=16.0)
    hh = _hh([_inv("2022-11-30", 500, 500 * 0.50 / 1.05, **svt)], timeline=renewed)
    assert gen.coverage_breaches(*hh, WINDOWS, "resi")


def test_the_backbill_rule_can_fire_and_respects_the_cap_when_applied():
    catch = dict(catchup_applied=True, catchup_direction="debit", catchup_period_start="2021-01-01")
    late = _hh([_inv("2022-11-30", 500, 100, **catch)])
    capped = _hh([_inv("2022-11-30", 500, 100, **catch, catchup_back_billing_cap_applied=True)])
    recent = _hh([_inv("2022-11-30", 500, 100, **{**catch, "catchup_period_start": "2022-06-01"})])
    assert [b["rule"] for b in gen.coverage_breaches(*late, [], "resi")] == ["backbill_beyond_12_months"]
    assert gen.coverage_breaches(*capped, [], "resi") == []
    assert gen.coverage_breaches(*recent, [], "resi") == []


def test_the_gas_left_behind_rule_can_fire_and_stays_quiet_when_both_leave():
    left = [{"date": "2022-01-15", "type": "churned", "detail": "Churned"}]
    gas = [_inv("2022-01-31", 900, 50), _inv("2022-06-30", 300, 20)]
    behind = _hh([_inv("2021-12-31", 300, 60)], timeline=left, gas=gas)
    together = _hh([_inv("2021-12-31", 300, 60)], timeline=left, gas=gas[:1], gas_timeline=left)
    assert [b["rule"] for b in gen.coverage_breaches(*behind, [], "resi")] == ["gas_left_behind"]
    assert gen.coverage_breaches(*together, [], "resi") == []


def test_each_scorer_can_fill_its_slot_and_can_refuse(real):
    """A rule meant to fire rarely must be shown able to fire at all: over the real book, every
    scorer that is not a declared empty returns a household for at least one, and None for at
    least one. A scorer that refuses everything would pass every 'refuses correctly' test."""
    customers, sample, _ = real
    people = sample["customers"]
    hhs = gen.households(customers)
    for slot_id, _feature, _rule, scorer in gen._cast_rules():
        got = [scorer(hh, gen._events(hh), people.get(hh["id"]) or {}) for hh in hhs]
        if slot_id == "storage_heating":
            continue  # no two-register bill on the record; the synthetic test below shows it can fire
        assert any(g is not None for g in got), "{} fills for nobody in the real book".format(slot_id)
        assert any(g is None for g in got), "{} fills for everybody -- it is not a rule".format(slot_id)


def _mover_book(closing_gbp=0.0, successor=True, read_type="A"):
    """A two-account book: SYN-2016-001 moves out on 5 Feb 2021 and OCC-0001-1 opens on its meter point."""
    def acc(aid, acq, bills, entries, timeline=(), **kw):
        return {"account_id": aid, "commodity": "electricity", "segment": "resi", "acquisition_date": acq,
                "invoices": bills, "ledger": {"entries": entries}, "timeline": list(timeline),
                "reaction_chain": [], **kw}

    def bill(aid, n, start, end, days, rt="A"):
        return {"id": "{}-INV{}".format(aid, n), "date": end, "period_start": start, "period_end": end,
                "days_in_period": days, "consumption_kwh": 8.0 * days, "amount_gbp": 2.0 * days, "read_type": rt}

    old = [bill("SYN-2016-001", 1, "2020-12-01", "2020-12-31", 31), bill("SYN-2016-001", 2, "2021-01-01", "2021-01-31", 31),
           bill("SYN-2016-001", 3, "2021-02-01", "2021-02-04", 4, read_type)]
    owed = 8.0 - closing_gbp
    entries = [{"date": "2021-01-03", "type": "invoice_raised", "invoice_number": 1, "amount_gbp": 62.0, "running_balance_gbp": 62.0},
               {"date": "2021-01-10", "type": "payment_received", "invoice_number": 1, "amount_gbp": -62.0,
                "method": "direct_debit", "running_balance_gbp": 0.0},
               {"date": "2021-02-02", "type": "invoice_raised", "invoice_number": 2, "amount_gbp": 62.0, "running_balance_gbp": 62.0},
               {"date": "2021-02-05", "type": "invoice_raised", "invoice_number": 3, "amount_gbp": 8.0, "running_balance_gbp": 70.0},
               {"date": "2021-02-20", "type": "payment_received", "invoice_number": 3, "amount_gbp": -(62.0 + owed),
                "method": "direct_debit", "running_balance_gbp": round(8.0 - owed, 2)}]
    moved = [{"type": "final_bill", "date": "2021-02-04", "detail": "Final bill",
              "effect": "Closing read {}; billed £8.00".format("actual" if read_type == "A" else "estimated")},
             {"type": "moved_out", "date": "2021-02-05", "detail": "Moved out"}]
    new = [bill("OCC-0001-1", 1, "2021-02-05", "2021-02-28", 24), bill("OCC-0001-1", 2, "2021-03-01", "2021-03-31", 31)]
    # Joined before the switch-in rule's window, so that slot (drawn first) does not claim it.
    customers = {"SYN-2016-001": acc("SYN-2016-001", "2016-01-15", old, entries, moved)}
    if successor:
        customers["OCC-0001-1"] = acc("OCC-0001-1", "2021-02-05", new, [], predecessor_account_id="SYN-2016-001")
    return customers, {"customers": {}, "meta": {}}, WINDOWS


def _mover_slot(book):
    return next(s for s in gen.build(*book)["slots"] if s["id"] == "mover")


def test_the_mover_slot_can_fill_on_a_book_with_a_mover():
    """DEFECT: `_score_mover` was `return None`, so 'no household qualifies' was a constant, not a
    count, and a reason saying the record carried no move-out stood over pages that carried 259.
    Can-fill first: a book whose one mover settles on an actual closing read and whose meter point
    opens to a new account fills the slot. Only then, what it shows."""
    slot = _mover_slot(_mover_book())
    assert slot["filled"], slot.get("reason")
    assert slot["household"] == "SYN-2016-001"
    kinds = [m["kind"] for m in slot["moments"]]
    assert {"moved_out", "final_bill", "settled", "new_occupant"} <= set(kinds), kinds
    assert slot["moments"][slot["opening"]]["kind"] == "final_bill"
    occ = next(m for m in slot["moments"] if m["kind"] == "new_occupant")
    assert "OCC-0001-1" in occ["story"] and occ["iso"] == "2021-02-05"


@pytest.mark.parametrize("book, check", [
    (dict(closing_gbp=-5.0), "its closing credit is not shown refunded"),
    (dict(closing_gbp=5.0), "its closing balance is still owed"),
    (dict(successor=False), "no later account on its meter point names it"),
    (dict(read_type="E"), "its closing read is estimated, so the final bill's use is not observed"),
])
def test_the_mover_slot_refuses_a_move_that_does_not_close_and_names_why(book, check):
    slot = _mover_slot(_mover_book(**book))
    assert not slot["filled"] and slot["matched"] == 1 and check in slot["failed_checks"], slot


def test_the_mover_empty_reason_is_shown_only_when_no_household_moves():
    book = _mover_book()
    for c in book[0].values():
        c["timeline"] = [e for e in c["timeline"] if e["type"] != "moved_out"]
    slot = _mover_slot(book)
    assert not slot["filled"] and slot["matched"] == 0 and slot["reason"] == gen.MOVER_EMPTY_REASON


def test_the_storage_rule_fires_on_a_two_register_bill():
    """The storage slot is empty on this run because no bill has two registers; the rule itself
    must still be able to see one, or 'empty' would be the scorer's blindness, not the run's."""
    two = _inv("2022-11-30", 500, 100, registers=[{"label": "Day"}, {"label": "Night"}])
    hh, ev = _hh([two])
    assert gen._score_storage(hh, ev, {}) is not None
    hh, ev = _hh([_inv("2022-11-30", 500, 100, registers=[{"label": "Anytime"}])])
    assert gen._score_storage(hh, ev, {}) is None


def test_the_published_feed_matches_a_fresh_build_in_shape(feed):
    if not FEED.is_file():
        pytest.skip("feed not yet generated")
    on_disk = json.loads(FEED.read_text(encoding="utf-8"))
    assert [s["id"] for s in on_disk["slots"]] == [s["id"] for s in feed["slots"]]
    assert on_disk["coverage"]["of"] == feed["coverage"]["of"]


# ── The Monday verdict: a feature that stops working reds the build (steer item 4) ─────────────


def _gapless(feed):
    f = copy.deepcopy(feed)
    for s in f["slots"]:
        s["filled"] = True
    f["coverage"]["empty"] = []
    f["coverage"]["book_breaches"] = {}
    return f


def test_every_gap_the_cast_finds_is_accounted_for_by_an_open_finding(feed):
    """The build-reddening leg: a fresh build over the published run, graded against the open rooms.
    DEFECT: a slot that stops filling, or a rule that starts breaching, with nothing open on it."""
    v = gen.coverage_verdict(feed)
    assert not v["red"], "\n".join(v["red"])


def test_the_verdict_can_be_green_and_can_be_red(feed, tmp_path):
    """The whole partition, so a verdict that reds everything (or nothing) is caught."""
    clean = gen.coverage_verdict(_gapless(feed), tmp_path)
    assert not clean["red"] and not clean["accounted"] and clean["spent"]
    assert gen.coverage_verdict(feed, tmp_path)["red"]


def test_MUTATION_a_filled_slot_that_empties_reds(feed, tmp_path):
    f = _gapless(feed)
    # A slot no finding names: "debt" was this slot until an empty debt slot got its own finding.
    assert "renewal" not in gen.ACCOUNTED_BY
    f["coverage"]["empty"] = ["renewal"]
    red = gen.coverage_verdict(f, tmp_path)["red"]
    assert len(red) == 1 and "slot renewal" in red[0] and "no open finding" in red[0], red


def test_MUTATION_a_rule_that_starts_breaching_reds(feed, tmp_path):
    f = _gapless(feed)
    f["coverage"]["book_breaches"] = {"gas_left_behind": {"households": 3, "of": 550}}
    red = gen.coverage_verdict(f, tmp_path)["red"]
    assert len(red) == 1 and "gas_left_behind" in red[0], red


def test_MUTATION_a_closed_finding_with_its_gap_still_live_reds(feed, tmp_path):
    (tmp_path / "in_progress").mkdir()
    f = _gapless(feed)
    f["coverage"]["book_breaches"] = {"above_cap": {"households": 1, "of": 550}}
    assert "no longer open" in gen.coverage_verdict(f, tmp_path)["red"][0]
    (tmp_path / "in_progress" / gen.ACCOUNTED_BY["above_cap"]).write_text("x")
    assert not gen.coverage_verdict(f, tmp_path)["red"]


def test_MUTATION_a_dropped_slot_or_a_broken_feed_is_red_not_clean(feed, tmp_path):
    f = _gapless(feed)
    f["slots"] = [s for s in f["slots"] if s["id"] != "ev"]
    assert any("slot ev" in r for r in gen.coverage_verdict(f, tmp_path)["red"])
    assert gen.coverage_verdict({}, tmp_path)["red"]
    assert gen.coverage_verdict(None, tmp_path)["red"]


# ── Validity (the director's steer of 26 Oct: every example must make sense to an energy reader) ──


def _candidates(real, slot_id):
    customers, sample, _ = real
    hhs = gen.households(customers)
    events = {hh["id"]: gen._events(hh) for hh in hhs}
    bands = gen.use_bands(hhs, events)
    scorer = next(r[3] for r in gen._cast_rules() if r[0] == slot_id)
    out = {}
    for hh in hhs:
        got = scorer(hh, events[hh["id"]], sample["customers"].get(hh["id"]) or {})
        if got:
            out[hh["id"]] = gen.validity_failures(slot_id, hh, events[hh["id"]], got[1], bands)
    return out


def test_no_filled_slot_holds_a_household_its_checks_refuse(real, feed):
    """DEFECT: a slot filled by the run's most extreme case when that case is an error (a gas-only
    EV home, a 100 kWh "storage-heated" January). Every filled slot's household passes its checks."""
    customers, *_ = real
    hhs = {hh["id"]: hh for hh in gen.households(customers)}
    bands = gen.use_bands(list(hhs.values()), {k: gen._events(v) for k, v in hhs.items()})
    for s in feed["slots"]:
        if not s["filled"]:
            continue
        assert not gen._common_failures(hhs[s["household"]], gen._events(hhs[s["household"]]), bands), s["id"]


def test_the_checks_can_refuse_and_can_pass(real):
    """A check that refuses everything empties every slot and passes every 'refuses correctly' test.
    Over the real book the checks must both refuse some rule-matching household and pass another,
    on some slot -- and on the EV slot they refuse the published gas-only home."""
    ev = _candidates(real, "ev")
    trap = _candidates(real, "estimate_trap")
    assert any(ev.values()) and any(not v for v in trap.values()) and any(trap.values())
    assert "it holds no electricity supply with us" in ev.get("SYN-2016-476", []), ev.get("SYN-2016-476")


def test_an_empty_slot_with_matches_names_the_checks_that_failed(feed):
    for s in feed["slots"]:
        if not s["filled"] and s.get("matched"):
            assert s["failed_checks"] and "passes this example's checks" in s["reason"], s["id"]


def test_MUTATION_checks_that_pass_everything_put_the_gas_only_ev_home_back(real, monkeypatch):
    monkeypatch.setattr(gen, "validity_failures", lambda *a: [])
    ev = next(s for s in gen.build(*real)["slots"] if s["id"] == "ev")
    assert ev["filled"] and "electricity" not in ev["fuels"], "the mutation did not restore the 4ae8da9b0f defect"


def test_the_default_account_is_an_ordinary_full_record(real, feed):
    """DEFECT: the six-stage section opened on C1, a non-public id with four bills."""
    customers, *_ = real
    d = feed["meta"]["default_account"]
    assert d and gen._PUBLIC_ID.fullmatch(d)
    assert len(customers[d]["invoices"]) >= 12


def test_a_bill_the_page_shows_is_owed_until_the_ledger_says_it_was_paid():
    """Cold read O13 (PROS-2025-0022): the first bills, dated at their period end, totalled GBP 186.20
    beside "Nothing owed", because the ledger raises a bill on issue a few days later and the balance
    was read from the ledger alone. On the bill's date it is owed; once paid, nothing is."""
    bill = {"id": "X-INV1", "date": "2025-02-28", "fuel": "electricity", "amount_gbp": 85.79}
    raised = {"date": "2025-03-03", "type": "invoice_raised", "fuel": "electricity", "amount_gbp": 85.79,
              "running_balance_gbp": 85.79}
    paid = {"date": "2025-03-17", "type": "payment_received", "fuel": "electricity", "amount_gbp": -85.79,
            "running_balance_gbp": 0.0}
    ev = {"invoice": [bill], "ledger": [raised, paid]}
    for iso, owed in (("2025-02-28", 85.79), ("2025-03-03", 85.79), ("2025-03-17", 0.0)):
        got, _ = gen._owed(gen._known_by(ev["invoice"], iso), gen._known_by(ev["ledger"], iso))
        assert round(got, 2) == owed, (iso, got)


def test_the_cast_balance_is_billed_less_paid_on_every_moment(feed, real):
    """Every "Balance on the books" a moment prints equals its bills less its other ledger movements
    as known that day. A balance read from the ledger's running total alone reds on the first-bill
    moment, where the ledger has not raised the bill yet."""
    customers = real[0]
    by_hh = {h["id"]: h for h in gen.households(customers)}
    checked, wrong = 0, []
    for s in feed["slots"]:
        hh = by_hh.get(s.get("household"))
        if not hh:
            continue
        ev = gen._events(hh)
        for m in s.get("moments", []):
            row = next((r for r in m["supplier"] if r["k"] == "Balance on the books"), None)
            if row is None:
                continue
            known = gen._before_outcome(ev, m["iso"])
            bills = gen._known_by(known["invoice"], m["iso"])
            billed = sum(i.get("amount_gbp") or 0 for i in bills)
            # A bill's own scheme credit comes off with the bill, whenever the ledger posts it (N1).
            keys = {(i["fuel"], i.get("invoice_number")) for i in bills if i.get("invoice_number") is not None}
            own = [r for r in known["ledger"]
                   if r.get("type") == "scheme_credit" and (r["fuel"], r.get("invoice_number")) in keys]
            moved = sum(r.get("amount_gbp") or 0 for r in gen._known_by(known["ledger"], m["iso"])
                        if r.get("type") != "invoice_raised" and r not in own)
            owed = billed + moved + sum(r.get("amount_gbp") or 0 for r in own)
            want = ("{} owed".format(gen._fmt_gbp(owed)) if owed > 0.005 else
                    "{} in credit".format(gen._fmt_gbp(-owed)) if owed < -0.005 else "Nothing owed")
            checked += 1
            if row["v"] != want:
                wrong.append((s["id"], m["iso"], row["v"], want))
    assert checked, "no balance rows at all -- this control would be vacuous"
    assert not wrong, wrong[:5]


# ── INV_ESTIMATE_RUN_WITHIN_TENURE, checked where it lives: on the page (O14, O28) ──────────────
# The raw export is one fuel per account, so a run of estimated bills there is a sub-run of that
# leg's own bills and the invariant holds by construction. The page is where it broke: "12 gas bills
# in a row were estimated" printed on 28 Feb 2018 for a household that joined on 30 Aug 2017.


def _calendar_months(since: str, until: str) -> int:
    a, b = since[:7].split("-"), until[:7].split("-")
    return (int(b[0]) - int(a[0])) * 12 + int(b[1]) - int(a[1]) + 1


def _estimate_runs_longer_than_their_bills(feed) -> list[str]:
    """Each estimate-run moment's count against the bills its fuel can have had by that moment.
    The company bills each fuel once per calendar month (first and last part-months included), so
    a fuel has at most one bill per calendar month touched since the household joined."""
    bad = []
    for s in feed["slots"]:
        for m in s.get("moments", []):
            if m["kind"] != "estimate_run":
                continue
            n = int(m["story"].split()[0])
            since = next(r["drawn_from"] for r in m["supplier"] if r["k"] == "Customer since")
            if n > _calendar_months(since, m["iso"]):
                bad.append("{} {}: {} on {}, {} calendar months after joining on {}".format(
                    s["id"], s["household"], m["story"], m["iso"], _calendar_months(since, m["iso"]), since))
    return bad


def _has_estimate_run(feed) -> bool:
    return any(m["kind"] == "estimate_run" for s in feed["slots"] for m in s.get("moments", []))


def test_an_estimate_run_is_no_longer_than_the_bills_its_fuel_has_had(feed):
    if not _has_estimate_run(feed):
        pytest.skip("no estimate run on this book, so this control has nothing to read")
    assert not _estimate_runs_longer_than_their_bills(feed), _estimate_runs_longer_than_their_bills(feed)


def test_the_published_page_carries_no_estimate_run_longer_than_its_bills():
    """The committed feed is what a reader sees, so it is graded too, not only a fresh build."""
    if not FEED.is_file():
        pytest.skip("feed not yet generated")
    on_disk = json.loads(FEED.read_text(encoding="utf-8"))
    assert not _estimate_runs_longer_than_their_bills(on_disk), _estimate_runs_longer_than_their_bills(on_disk)


def test_MUTATION_an_estimate_run_shown_at_its_midpoint_is_caught(feed):
    """The O14 shape: the whole run's count, dated one month after joining."""
    if not _has_estimate_run(feed):
        pytest.skip("no estimate run on this book")
    f = copy.deepcopy(feed)
    m = next(m for s in f["slots"] for m in s.get("moments", []) if m["kind"] == "estimate_run")
    since = next(r["drawn_from"] for r in m["supplier"] if r["k"] == "Customer since")
    m["story"] = "12" + m["story"][m["story"].index(" "):]
    m["iso"] = since
    assert _estimate_runs_longer_than_their_bills(f)


# ── The debt slot reads the page's own record (third cold read, SYN-2016-356 on 129e7de698) ──────


def _debt_hh(earlier_journey=False, notice_before=False, nothing_missed=False, agency_unshown=False, no_due_date=False):
    """SYN-2016-356's shape: four bills paid by direct debit, then the desk's journey opens on the
    15 Dec 2016 bill and ends written off as statute-barred in 2024. Each flag puts back one thing
    the third cold read found its page contradicting; with none set the story agrees with its record."""
    bills = [{"invoice_number": n, "date": "2016-{:02d}-30".format(m), "period_start": "2016-{:02d}-01".format(m),
              "due_date": "2016-{:02d}-15".format(m + 1), "days_in_period": 30, "consumption_kwh": 240.0,
              "amount_gbp": 40.0, "read_type": "A"} for n, m in enumerate(range(7, 12), start=1)]
    led = [{"date": "2016-{:02d}-15".format(m + 1), "type": "payment_received", "invoice_number": n,
            "amount_gbp": -40.0, "method": "direct_debit"} for n, m in enumerate(range(7, 11), start=1)]
    if no_due_date:  # a page exported before the bill carried its due date (the 4ae8da9b0f book)
        for b in bills:
            del b["due_date"]
    if not nothing_missed:
        led.append({"date": "2016-11-15", "type": "payment_failed", "invoice_number": 4, "amount_gbp": 0.0,
                    "method": "direct_debit"})
    rc = [{"date": "2016-12-14", "event_type": "collections_cured", "description": "Overdue balance cleared"},
          {"date": "2016-12-15", "event_type": "collections_missed_payment", "description": "A bill is unpaid"},
          {"date": "2016-12-21", "event_type": "collections_reminder", "description": "Reminder sent"},
          {"date": "2017-01-11", "event_type": "collections_repayment_plan_offer", "description": "Payment plan offered"},
          {"date": "2024-07-17", "event_type": "collections_write_off",
           "description": "Written off: the debt is statute-barred (Limitation Act 1980 s.5) -- GBP912.82"}]
    if earlier_journey:  # a decision of a journey the desk closed before this one opened
        rc.append({"date": "2016-11-25", "event_type": "collections_repayment_plan_offer", "description": "Payment plan offered"})
    if notice_before:
        rc.append({"date": "2016-11-25", "event_type": "arrears_first_notice", "description": "First overdue notice"})
    if agency_unshown:
        rc.append({"date": "2018-09-30", "event_type": "arrears_placed_with_dca",
                   "description": "Debt placed with third-party debt collection agency"})
    acc = {"account_id": "SYN-2016-356", "commodity": "electricity", "segment": "resi", "acquisition_date": "2016-07-01",
           "invoices": bills, "ledger": {"entries": sorted(led, key=lambda r: r["date"])}, "timeline": [],
           "reaction_chain": sorted(rc, key=lambda r: r["date"])}
    hh = {"id": "SYN-2016-356", "legs": {"electricity": acc}, "successors": {}}
    ev = gen._events(hh)
    got = gen._score_debt(hh, ev, {})
    assert got, "the debt scorer must take this book, or the checks below grade nothing"
    return gen.validity_failures("debt", hh, ev, got[1], {})


NOTICE = "the page shows an overdue notice dated before the missed payment its story opens on"
COUNTERS = "its payment record shows nothing missed or returned beside a moment that says a payment was not made"
AGENCY = "its record places the debt with an agency, and no moment of the story shows it"
NO_DUE = "its bills carry no due date, so its payment record cannot count a payment missed"


def test_the_debt_slot_refuses_the_story_syn_2016_356s_record_contradicts():
    """DEFECT: the debt slot's predicate passed SYN-2016-356 on 129e7de698 while its page dated
    "First overdue notice" (25 Nov) before the story's "Missed a payment" (15 Dec), printed "4 of 4
    bills paid, 0 returned, 0 missed" at that moment, and held an agency placement (30 Sep 2018) no
    moment showed. Can-pass first: the same journey with its record agreeing passes, so a predicate
    that refuses every debt story cannot pass this test."""
    assert _debt_hh() == []
    assert set(_debt_hh(notice_before=True, nothing_missed=True, agency_unshown=True)) == {NOTICE, COUNTERS, AGENCY}


@pytest.mark.parametrize("flag, check", [("notice_before", NOTICE), ("nothing_missed", COUNTERS),
                                         ("agency_unshown", AGENCY), ("no_due_date", NO_DUE)])
def test_each_debt_page_check_refuses_alone(flag, check):
    assert _debt_hh(**{flag: True}) == [check]


def test_a_decision_from_an_earlier_closed_desk_journey_is_history_not_a_split_clock():
    """DEFECT: 162 of the 217 'notice before the miss' refusals on 209c3350ab were a payment-plan offer
    from a journey the desk had cleared before the next opened. Can-refuse beside it: the old engine's
    notice in the same place still refuses, so the exemption is not a blanket."""
    assert _debt_hh(earlier_journey=True) == []
    assert _debt_hh(notice_before=True) == [NOTICE]


def _cleared_hh(caught_up, credit_note=False):
    """SYN-2016-550's page on 209c3350ab: the first bill is never paid, each later bill is paid on its
    due date, and the desk's story ends "Debt cleared" on a due date. `caught_up` pays the first bill
    before that ending, so the page's balance agrees with it. `credit_note` instead offsets it with a
    credit invoice raised before the ending and printed with a due date after it."""
    bills, led, bal = [], [], 0.0
    for n, m in enumerate(range(1, 6), start=1):
        due = "2024-{:02d}-15".format(m)
        bills.append({"invoice_number": n, "date": "2024-{:02d}-01".format(m), "period_start": "2023-12-01",
                      "due_date": due, "days_in_period": 30, "consumption_kwh": 240.0, "amount_gbp": 100.0,
                      "read_type": "A"})
        bal += 100.0
        led.append({"date": "2024-{:02d}-01".format(m), "type": "invoice_raised", "invoice_number": n,
                    "amount_gbp": 100.0, "running_balance_gbp": bal})
        if n == 1:
            led.append({"date": due, "type": "payment_failed", "invoice_number": n, "amount_gbp": 0.0,
                        "method": "standard_credit", "running_balance_gbp": bal})
            continue
        for amount in ((100.0, 100.0) if caught_up and n == 5 else (100.0,)):
            bal -= amount
            led.append({"date": due, "type": "payment_received", "invoice_number": n, "amount_gbp": -amount,
                        "method": "standard_credit", "running_balance_gbp": bal})
    if credit_note:
        bills.append({"invoice_number": 6, "date": "2024-05-08", "period_start": "2024-04-01", "due_date": "2024-05-25",
                      "days_in_period": 30, "consumption_kwh": 0.0, "amount_gbp": -100.0, "read_type": "A"})
        bal -= 100.0
        led.append({"date": "2024-05-08", "type": "invoice_raised", "invoice_number": 6, "amount_gbp": -100.0,
                    "running_balance_gbp": bal})
        led.sort(key=lambda r: r["date"])
        bal = 0.0
        for r in led:
            bal += r["amount_gbp"]
            r["running_balance_gbp"] = bal
    rc = [{"date": "2024-01-16", "event_type": "collections_missed_payment", "description": "A bill is unpaid"},
          {"date": "2024-01-22", "event_type": "collections_reminder", "description": "Reminder sent"},
          {"date": "2024-02-12", "event_type": "collections_repayment_plan_offer", "description": "Payment plan offered"},
          {"date": "2024-05-15", "event_type": "collections_cured", "description": "Overdue balance cleared"}]
    acc = {"account_id": "SYN-2016-550", "commodity": "electricity", "segment": "resi", "acquisition_date": "2016-07-01",
           "invoices": bills, "ledger": {"entries": led}, "timeline": [], "reaction_chain": rc}
    hh = {"id": "SYN-2016-550", "legs": {"electricity": acc}, "successors": {}}
    ev = gen._events(hh)
    got = gen._score_debt(hh, ev, {})
    assert got, "the debt scorer must take this book, or the check below grades nothing"
    return gen.validity_failures("debt", hh, ev, got[1], {})


def test_the_debt_slot_refuses_a_cleared_ending_over_a_balance_its_page_still_holds():
    """DEFECT: SYN-2016-550 on 209c3350ab ended its story "Debt cleared" on 15 Dec 2024 while its page
    held GBP 71.31 (electricity) and GBP 187.53 (gas) unpaid. Can-pass first: the same story with the
    old bill paid before the ending passes, so a check that refuses every cleared ending cannot."""
    assert gen.CLEARED_WHILE_OWED not in _cleared_hh(caught_up=True)
    assert gen.CLEARED_WHILE_OWED in _cleared_hh(caught_up=False)


def test_a_credit_note_not_yet_due_is_not_added_back_to_what_is_owed():
    """DEFECT: SYN-2016-016 on 3dc5a92948 was refused "cleared while owed" (GBP 33.95) on 21 Mar 2018: a
    GBP -36.70 credit invoice printed due 24 Mar was taken off as a bill not yet due, which adds it back.
    A credit is available when raised; the desk read the same day as 3 days before anything was due.
    Can-refuse beside it: the same story without the credit note still refuses."""
    assert gen.CLEARED_WHILE_OWED not in _cleared_hh(caught_up=False, credit_note=True)
    assert gen.CLEARED_WHILE_OWED in _cleared_hh(caught_up=False)
