"""C30: a woken default-tariff household that stays can re-fix with us (research doc §7.5a).

Short real runs of the 2016-01 .. 2017-02 window, as `test_a_run_reaches_the_svt_contact_response`
does, because the splice lives inside the run loop. Three arms: the switch on with a contact sent,
the switch on with nothing sent, and the switch off with the same contact.
"""
from __future__ import annotations

from dataclasses import replace

import pytest

import simulation.contact_response as contact_response
from company.policy.decision_policy import CURRENT_POLICY, policy_scope

_END = "2017-02-28"
_INSTRUMENT = "collective_switch"


def _run(policy, refix: bool, tmp_path_factory, monkeypatch_module):
    from simulation.run_phase2b import main

    monkeypatch_module.setattr(contact_response, "A_WOKEN_SVT_STAYER_REFIXES", refix)
    with policy_scope(policy):
        return main(report_end=_END, policy=policy,
                    gap_ledger_path=tmp_path_factory.mktemp("gap") / "coupled_gap_ledger.json")


@pytest.fixture(scope="module")
def _arms(tmp_path_factory):
    contacted = replace(CURRENT_POLICY, name="svt_refix_test", svt_contact_instrument=_INSTRUMENT)
    with pytest.MonkeyPatch.context() as mp:
        return {
            "on": _run(contacted, True, tmp_path_factory, mp)["svt_decisions"],
            "on_uncontacted": _run(CURRENT_POLICY, True, tmp_path_factory, mp)["svt_decisions"],
            "off": _run(contacted, False, tmp_path_factory, mp)["svt_decisions"],
        }


def _key(row):
    return row["customer_id"], row["event_date"]


def test_the_refix_band_can_be_reached_and_a_refixed_household_leaves_the_default(_arms):
    """DEFECT: the band is computed but no draw ever lands in it (a guard that refuses every
    household passes every other test here), or a re-fixed household keeps rolling default
    segments inside the fix it was struck.

    MUTATION: returning `{"refused": ...}` unconditionally from `_splice_a_refix` empties `fixed`;
    dropping the withdrawal (`all_terms[:] = ...`) leaves SVT rows inside the fix window.
    """
    rows = _arms["on"]
    fixed = [r for r in rows if (r.get("sim_refix") or {}).get("fix_start")]
    assert fixed, "no woken stayer re-fixed in the window: the branch is unreachable"
    for r in fixed:
        assert r["event_type"] == "stayed"
        assert r["realized_churn_probability"] <= r["random_roll"]
        fix = r["sim_refix"]
        assert r["event_date"] < fix["fix_start"] < fix["fix_end"]
        assert fix["default_segments_withdrawn"] >= 1
        inside = [o for o in rows if o["customer_id"] == r["customer_id"]
                  and fix["fix_start"] <= o["event_date"] < fix["fix_end"]]
        assert not inside, f"{r['customer_id']} rolled default segments inside its fix: {inside}"


def test_an_uncontacted_household_never_refixes_with_the_switch_on(_arms):
    """DEFECT: the re-fix fires on a draw no contact produced, so the switch alone changes the
    world. MUTATION: dropping `_svt_churn_if_choosing is not None` from the band's guard."""
    assert _arms["on_uncontacted"]
    assert not any("sim_refix" in r for r in _arms["on_uncontacted"])


def test_off_writes_nothing_and_on_matches_off_until_the_first_fix_starts(_arms):
    """DEFECT: the switch off still writes the re-fix field, or turning it on moves a draw,
    probability or outcome before any household re-fixed. MUTATION: writing `sim_refix` with the
    switch off reds the first assert; reseeding the roll reds the paired equality."""
    assert not any("sim_refix" in r for r in _arms["off"])
    # A fix moves the book every household is priced and hedged against, so the pairing stops at
    # the run's first fix starting, not each household's.
    first_fix = min((r["sim_refix"]["fix_start"] for r in _arms["on"]
                     if (r.get("sim_refix") or {}).get("fix_start")), default="9999")
    off = {_key(r): r for r in _arms["off"]}
    paired = 0
    for r in _arms["on"]:
        if r["event_date"] >= first_fix:
            continue
        base = off.get(_key(r))
        if base is None:
            continue
        paired += 1
        for k in ("random_roll", "realized_churn_probability", "event_type", "departure_cause"):
            assert r[k] == base[k], (k, _key(r))
    assert paired
