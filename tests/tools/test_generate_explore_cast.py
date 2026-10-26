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
        if slot_id in gen.EMPTY_REASONS:
            continue
        assert any(g is not None for g in got), "{} fills for nobody in the real book".format(slot_id)
        assert any(g is None for g in got), "{} fills for everybody -- it is not a rule".format(slot_id)


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
    f["coverage"]["empty"] = ["debt"]
    red = gen.coverage_verdict(f, tmp_path)["red"]
    assert len(red) == 1 and "slot debt" in red[0] and "no open finding" in red[0], red


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
