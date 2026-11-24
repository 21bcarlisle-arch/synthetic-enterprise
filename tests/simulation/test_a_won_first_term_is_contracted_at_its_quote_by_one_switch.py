"""A won account's first fixed term is contracted on the strike it was quoted, by one switch, and the
switch is off.

`live_population.CONTRACT_THE_FIRST_TERM_AT_THE_QUOTED_STRIKE` carries the campaign's quote onto the
won electricity leg, and `renewals.contracted_first_term` contracts the first term on it
(`docs/staging/records/SEAT_PREREG_THE_FIRST_TERM_CONTRACTED_AT_ITS_QUOTE_2026-11-24.md`).

Each test names the defect it catches.
"""

from __future__ import annotations

from types import SimpleNamespace

from simulation import live_population as lp
from simulation import renewals

KEY = lp.QUOTED_FIRST_TERM_RATE_KEY
QUOTED = 175.6
NOTICE_DATE_STRIKE = 231.0  # the 2021 shape: the notice-date strike far above the quote


def _outcome() -> dict:
    """One dual-fuel winner the campaign quoted, and one it did not."""
    def prospect(cid):
        return SimpleNamespace(
            customer_id=cid, premise=SimpleNamespace(commodity="gas"),
            to_customer_dict=lambda: {"customer_id": cid, "segment": "resi", "eac_kwh": 2900,
                                      "tariff_type": None, "consumption_band": "MEDIUM"})
    import datetime as dt
    return {"base_seed": 1, "quoted_strikes": {"PROS-A": QUOTED},
            "winners": [(prospect("PROS-A"), dt.date(2021, 10, 1)),
                        (prospect("PROS-B"), dt.date(2021, 10, 1))]}


def _won(monkeypatch, switch: bool) -> dict[str, dict]:
    monkeypatch.setattr(lp, "_won_fuel_arrangement", lambda prospect, seed: "dual")
    monkeypatch.setattr(lp, "CONTRACT_THE_FIRST_TERM_AT_THE_QUOTED_STRIKE", switch)
    return {c["customer_id"]: c for c in lp._won_customer_dicts(_outcome())}


def _first_term(monkeypatch, quoted) -> dict:
    """The builder's first term with the notice-date strike stubbed, so only the carry is tested."""
    monkeypatch.setattr(renewals, "price_fixed_term", lambda *a, **k: {
        "customer_id": a[0], "acquisition_date": a[1].isoformat(),
        "unit_rate_gbp_per_mwh": NOTICE_DATE_STRIKE, "tariff_type": "fixed",
        "term_end": a[3].isoformat()})
    terms = renewals.build_renewal_schedule(
        "PROS-A", "2021-10-01", "2021-10-01", [], 2900, tariff_type="fixed",
        quoted_first_term_unit_rate_gbp_per_mwh=quoted)
    assert len(terms) == 1, terms
    return terms[0]


def test_the_switch_is_off_until_the_post_s12g_book_has_been_read(monkeypatch):
    """Catches the switch taken before its book: B8's five grades read the post-s.12g book, and two
    changes in one book cannot be told apart. Off, no won leg carries a quote."""
    assert lp.CONTRACT_THE_FIRST_TERM_AT_THE_QUOTED_STRIKE is False
    monkeypatch.setattr(lp, "_won_fuel_arrangement", lambda prospect, seed: "dual")
    assert not any(KEY in c for c in lp._won_customer_dicts(_outcome()))


def test_taking_the_switch_carries_the_quote_onto_the_quoted_electricity_leg_only(monkeypatch):
    """Catches a switch that cannot be taken (`_won_customer_dicts` never reads it, or reads a copy
    bound at import); a quote copied onto the gas leg, which was never quoted, because `_gas_leg_for`
    copies the electricity dict; and a quote given to a winner the campaign did not price."""
    off, taken = _won(monkeypatch, False), _won(monkeypatch, True)
    assert set(off) == set(taken) == {"PROS-A", "PROS-Ag", "PROS-B", "PROS-Bg"}
    assert taken["PROS-A"][KEY] == QUOTED
    assert [cid for cid, c in taken.items() if KEY in c] == ["PROS-A"]
    assert {k: v for k, v in taken["PROS-A"].items() if k != KEY} == off["PROS-A"]


def test_a_carried_quote_is_the_first_terms_contracted_rate(monkeypatch):
    """Catches the builder dropping the carried quote and billing the notice-date strike nobody
    was shown, which is the defect the switch exists to end."""
    term = _first_term(monkeypatch, QUOTED)
    assert term["unit_rate_gbp_per_mwh"] == QUOTED
    assert term["notice_date_unit_rate_gbp_per_mwh"] == NOTICE_DATE_STRIKE
    assert term["struck_by"] == "first_term_quote"


def test_no_quote_leaves_the_notice_date_strike_byte_for_byte(monkeypatch):
    """Catches the switch-off book moving: with no quote the term is the notice-date offer's own."""
    assert _first_term(monkeypatch, None) == {
        "customer_id": "PROS-A", "acquisition_date": "2021-10-01",
        "unit_rate_gbp_per_mwh": NOTICE_DATE_STRIKE, "tariff_type": "fixed",
        "term_end": "2021-10-02"}
    assert renewals.contracted_first_term({"unit_rate_gbp_per_mwh": 1.0}, None) == {
        "unit_rate_gbp_per_mwh": 1.0}


def test_the_quote_is_recorded_without_changing_what_the_funnel_reads():
    """Catches the recorder altering the offer the funnel decides the win on, and recording a
    declined or unpriced prospect as quoted."""
    store: dict = {}
    replies = {"A": {"quoted": True, "price_differential_pct": -0.05, "unit_rate_per_mwh": QUOTED},
               "B": {"quoted": False, "reason": "above_default"}, "C": None}
    offer = lp._quote_recorder(lambda p, day: replies[p.customer_id], store)
    for cid, reply in replies.items():
        assert offer(SimpleNamespace(customer_id=cid), None) is reply
    assert store == {"A": QUOTED}
    assert lp._quote_recorder(None, store) is None


def test_the_switch_does_not_reach_a_renewal(monkeypatch):
    """Catches the quote applied at a renewal boundary: only term 0 was quoted."""
    monkeypatch.setattr(renewals, "rolls_active_renewal", lambda *a, **k: True)
    monkeypatch.setattr(renewals, "price_fixed_term", lambda *a, **k: {
        "customer_id": a[0], "acquisition_date": a[1].isoformat(),
        "unit_rate_gbp_per_mwh": NOTICE_DATE_STRIKE, "tariff_type": "fixed",
        "term_end": a[3].isoformat()})
    terms = renewals.build_renewal_schedule(
        "PROS-A", "2020-10-01", "2021-10-01", [], 2900, tariff_type="fixed",
        quoted_first_term_unit_rate_gbp_per_mwh=QUOTED)
    assert [t["unit_rate_gbp_per_mwh"] for t in terms if t.get("tariff_type") == "fixed"][:2] == [
        QUOTED, NOTICE_DATE_STRIKE], terms
