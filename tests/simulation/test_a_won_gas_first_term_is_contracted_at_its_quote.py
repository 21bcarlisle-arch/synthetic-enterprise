"""A won gas first term is contracted on the gas rate the household was quoted (27 Nov).

The dual-fuel quote strikes gas on its own, on the same day as electricity
(`docs/market_research/cheapest_fix_against_the_default_tariff_gb_2016_2025.md` §14). The strike is
recorded under the gas leg's `<id>g`, carried onto that leg behind S1's
`CONTRACT_THE_FIRST_TERM_AT_THE_QUOTED_STRIKE`, and contracted by `_build_gas_renewal_schedule`.

Each test names the defect it catches.
"""

from __future__ import annotations

import datetime as dt
from types import SimpleNamespace

from simulation import live_population as lp
from simulation import run_phase2b

KEY = lp.QUOTED_FIRST_TERM_RATE_KEY
ELEC_QUOTE, GAS_QUOTE, NOTICE_DATE_GAS = 175.6, 41.2, 118.29


def _outcome(strikes: dict) -> dict:
    def prospect(cid):
        return SimpleNamespace(
            customer_id=cid, premise=SimpleNamespace(commodity="gas"),
            to_customer_dict=lambda: {"customer_id": cid, "segment": "resi", "eac_kwh": 2900,
                                      "tariff_type": None, "consumption_band": "MEDIUM"})
    return {"base_seed": 1, "quoted_strikes": strikes,
            "winners": [(prospect("PROS-A"), dt.date(2021, 10, 1)),
                        (prospect("PROS-B"), dt.date(2021, 10, 1))]}


def _won(monkeypatch, arrangement: str, switch: bool = True) -> dict[str, dict]:
    monkeypatch.setattr(lp, "_won_fuel_arrangement", lambda prospect, seed: arrangement)
    monkeypatch.setattr(lp, "CONTRACT_THE_FIRST_TERM_AT_THE_QUOTED_STRIKE", switch)
    strikes = {"PROS-A": ELEC_QUOTE, "PROS-Ag": GAS_QUOTE, "PROS-B": ELEC_QUOTE}
    return {c["customer_id"]: c for c in lp._won_customer_dicts(_outcome(strikes))}


def test_each_leg_of_a_dual_home_carries_its_own_fuels_quote(monkeypatch):
    """Catches the gas leg left on a strike nobody quoted (S2's 47 terms), the electricity strike
    copied onto gas through `_gas_leg_for`, and a gas quote given to a home whose gas was not
    quoted (PROS-B)."""
    won = _won(monkeypatch, "dual")
    assert {cid: c.get(KEY) for cid, c in won.items()} == {
        "PROS-A": ELEC_QUOTE, "PROS-Ag": GAS_QUOTE, "PROS-B": ELEC_QUOTE, "PROS-Bg": None}
    assert won["PROS-Ag"]["commodity"] == "gas"


def test_a_gas_only_home_carries_the_gas_quote_and_the_switch_off_carries_none(monkeypatch):
    """Catches a gas-only home's account (no `g` suffix) losing its gas strike, or taking the
    electricity one; and the off arm still carrying a quote."""
    won = _won(monkeypatch, "gas")
    assert won["PROS-A"]["commodity"] == "gas" and won["PROS-A"][KEY] == GAS_QUOTE
    assert not any(KEY in c for c in _won(monkeypatch, "dual", switch=False).values())


def test_the_recorder_files_the_gas_half_under_the_gas_leg_without_changing_the_offer():
    """Catches the gas strike recorded under the electricity id (which would overwrite the
    electricity quote), recorded for a declined prospect, or the reply the funnel reads altered."""
    store: dict = {}
    replies = {"A": {"quoted": True, "price_differential_pct": -0.05,
                     "unit_rate_per_mwh": ELEC_QUOTE, "gas_unit_rate_per_mwh": GAS_QUOTE},
               "B": {"quoted": True, "price_differential_pct": -0.05,
                     "unit_rate_per_mwh": ELEC_QUOTE, "gas_unquoted_because": "cap_constrained"},
               "C": {"quoted": False, "reason": "above_default", "gas_unit_rate_per_mwh": GAS_QUOTE}}
    offer = lp._quote_recorder(lambda p, day: replies[p.customer_id], store)
    for cid, reply in replies.items():
        assert offer(SimpleNamespace(customer_id=cid), None) is reply
    assert store == {"A": ELEC_QUOTE, "Ag": GAS_QUOTE, "B": ELEC_QUOTE}


def _gas_schedule(monkeypatch, quoted, *, report_end="2021-10-01", tariff_type="fixed"):
    monkeypatch.setattr(run_phase2b, "generate_forward_price", lambda *a, **k: 50.0)
    monkeypatch.setattr(run_phase2b, "rolls_active_renewal", lambda *a, **k: True)
    monkeypatch.setattr(run_phase2b, "strike_gas_fixed_term", lambda c, start, notice, end, *a, **k: {
        "customer_id": c["customer_id"], "acquisition_date": start,
        "unit_rate_gbp_per_mwh": NOTICE_DATE_GAS, "tariff_type": "fixed", "term_end": end})
    return run_phase2b._build_gas_renewal_schedule(
        {"customer_id": "PROS-Ag", "acquisition_date": "2020-10-01", "aq_kwh": 11500.0,
         "segment": "resi"},
        [], report_end=report_end, tariff_type=tariff_type,
        quoted_first_term_unit_rate_gbp_per_mwh=quoted)


def test_the_gas_first_term_is_contracted_at_its_quote_and_only_the_first(monkeypatch):
    """Catches the gas builder dropping the carried quote (the defect), applying it at a renewal
    boundary that nobody quoted, and moving the no-quote book."""
    terms = _gas_schedule(monkeypatch, GAS_QUOTE)
    assert len(terms) >= 2, terms
    assert terms[0]["unit_rate_gbp_per_mwh"] == GAS_QUOTE
    assert terms[0]["notice_date_unit_rate_gbp_per_mwh"] == NOTICE_DATE_GAS
    assert terms[0]["struck_by"] == "first_term_quote"
    assert [t["unit_rate_gbp_per_mwh"] for t in terms[1:]] == [NOTICE_DATE_GAS] * (len(terms) - 1)
    assert all("struck_by" not in t for t in _gas_schedule(monkeypatch, None))


def test_the_run_hands_the_gas_leg_its_quote():
    """Catches the gas call site in `run_phase2b` not passing the key, which would leave every
    other test here green and the book unchanged."""
    import inspect

    src = inspect.getsource(run_phase2b)
    call = src[src.index("gas_schedules[c[\"customer_id\"]] = _build_gas_renewal_schedule("):]
    assert "quoted_first_term_unit_rate_gbp_per_mwh=c.get(QUOTED_FIRST_TERM_RATE_KEY)" in call[:400]
