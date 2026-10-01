"""The world's price-cap ceiling and the rate it clamps must sit on the same
side of VAT.

Filed as WORKER_FINDING_THE_PRICE_CAP_IS_ENFORCED_AGAINST_A_RATE_ON_THE_WRONG_SIDE_OF_VAT
(2026-08-24), repaired 2026-08-25.

THE DEFECT. `simulation/hedged_settlement.run_deemed_term` clamped an EX-VAT
unit rate against the published cap level, which the commons artefact declares
INCLUSIVE of VAT at 5%. The ceiling the world enforced was therefore 5% above the
one the law sets, for every domestic deemed period since the clamp was written,
always in the supplier's favour. The docstring on the accessor had said "including
VAT at 5%" under an R14 heading the whole time. It was right, and being right in a
docstring stopped nothing.

WHY THE CONTROL IS SHAPED THIS WAY. Two of these tests are about the instance and
one is about the class:

  * the instance is arithmetic, and it is checked at the OUTCOME — what rate came
    out of the shipped settlement function — not at the accessor, because the
    accessor was never wrong;
  * the class is that a published figure can be read into a comparison without its
    basis at all, and the fix for that is that the number cannot be obtained
    without naming the basis. That is R14 (`no financial figure without its
    clock`) with VAT in the place of the clock, and it is enforced below by AST,
    not by asking the next author to remember.

R15: every control here names the mutation that must make it fire.
"""

from __future__ import annotations

import ast
import json
from datetime import date
from pathlib import Path

import pytest

from simulation.hedged_settlement import run_deemed_term
from simulation.price_cap_enforcement import (
    DOMESTIC_VAT_RATE,
    binding_cap_unit_rate_gbp_per_mwh_ex_vat,
    binding_cap_unit_rate_gbp_per_mwh_inc_vat,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
WORLD_READING = REPO_ROOT / "simulation" / "price_cap_enforcement.py"
ARTEFACT = (
    REPO_ROOT / "docs" / "domain_artefact_library" / "regulatory"
    / "ofgem_default_tariff_cap_windows.json"
)

#: Inside the Oct-2021 window — the crisis one, where spot ran far above the
#: ceiling and the clamp is the only thing between the book and the law.
PROBE_DATE = "2022-02-15"


def _published_ceiling_inc_vat(fuel_key: str, on_date: str) -> float:
    """The published level, read from the artefact by a path that does not go
    through the module under test.

    ANTI-TAUTOLOGY: deriving the expected ceiling from
    `binding_cap_unit_rate_gbp_per_mwh_inc_vat` would check the settlement clamp
    against the same arithmetic the settlement clamp uses, and would pass with
    both sides multiplied by any constant at all — including 1.05.
    """
    raw = json.loads(ARTEFACT.read_text())
    windows = [w for w in raw["windows"] if w["from"] <= on_date <= w["to"]]
    assert len(windows) == 1, f"expected exactly one published window covering {on_date}"
    window = windows[0]
    epg = window.get(f"{fuel_key}_epg")
    return min(window[fuel_key], epg) if epg is not None else float(window[fuel_key])


def _prices(dates, price):
    return [
        {"settlementDate": d, "settlementPeriod": p, "systemSellPrice": price}
        for d in dates for p in range(1, 49)
    ]


def test_the_artefact_still_declares_the_basis_this_repair_assumes():
    """MUTATION (must fire): change the artefact's `vat` basis to "EXCLUDING VAT"
    without changing the code.

    The repair below divides the published level by 1.05. That is only correct
    while the published level is inc-VAT, and the artefact is where that is
    stated. If the commons is ever re-sourced on an ex-VAT basis — which is a
    perfectly reasonable thing for a future ingest to do — the division becomes a
    5% error in the OTHER direction, and nothing else in the tree would notice.
    An assumption that is load-bearing and unasserted is the fail-silent pattern
    wearing a data hat.
    """
    basis = json.loads(ARTEFACT.read_text())["basis"]
    assert "INCLUDING VAT" in basis["vat"].upper(), (
        f"the cap commons no longer declares an inc-VAT basis ({basis['vat']!r}); "
        "simulation/price_cap_enforcement.binding_cap_unit_rate_gbp_per_mwh_ex_vat "
        "de-VATs the published number and is now wrong"
    )
    assert "5%" in basis["vat"], (
        f"the cap commons declares a VAT rate this module does not use ({basis['vat']!r}); "
        f"DOMESTIC_VAT_RATE is {DOMESTIC_VAT_RATE}"
    )


def test_a_capped_deemed_rate_grossed_up_by_vat_equals_the_published_ceiling():
    """THE INSTANCE, checked at the outcome of the shipped function.

    MUTATION (must fire): restore the pre-repair clamp — swap
    `binding_cap_unit_rate_gbp_per_mwh_ex_vat` for `..._inc_vat` at
    `simulation/hedged_settlement.py`. The billed rate then equals the inc-VAT
    ceiling, so grossing it up overshoots the published level by exactly 5% and
    this fires.

    A domestic customer charged the billed (ex-VAT) rate pays that rate plus VAT.
    THAT is the number the law caps, so that is the number checked — not the
    accessor's return value, which was never the thing that was wrong.
    """
    ceiling_inc_vat = _published_ceiling_inc_vat("elec", PROBE_DATE)

    records = run_deemed_term(
        customer_id="VAT-PROBE",
        term_start_date=PROBE_DATE,
        term_end_date="2022-02-16",
        deemed_premium=0.20,
        consumption_shape=lambda date_str: [1.0] * 48,
        # Far above any published ceiling, so the clamp certainly binds.
        system_price_records=_prices([PROBE_DATE], price=1000.0),
        segment="resi",
        commodity="electricity",
    )

    assert records, "no settlement records produced for the probe day"
    # VACUITY GUARD: a clamp that never bound would satisfy any assertion about
    # what the clamp produces.
    assert all(r["cap_bound"] for r in records), (
        "the probe spot price did not bind against the cap, so this test proves "
        "nothing about the ceiling"
    )

    for record in records:
        customer_facing = record["unit_rate_gbp_per_mwh"] * (1.0 + DOMESTIC_VAT_RATE)
        assert customer_facing == pytest.approx(ceiling_inc_vat), (
            f"a capped domestic rate of {record['unit_rate_gbp_per_mwh']:.4f} GBP/MWh "
            f"ex-VAT bills the customer {customer_facing:.4f} GBP/MWh inc-VAT, against "
            f"a published ceiling of {ceiling_inc_vat:.4f}. The world is enforcing a "
            "ceiling that is not the law."
        )


def test_the_two_accessors_differ_by_exactly_vat_and_agree_on_where_there_is_no_cap():
    """MUTATION (must fire): make `..._ex_vat` return the inc-VAT number
    unchanged, or make it swallow a `None` into a float.

    The second half is the fail-open case with teeth. Both accessors return None
    to mean "no cap existed", and the caller reads None as "do not clamp". If the
    ex-VAT wrapper turned None into 0.0 it would clamp every domestic rate to
    zero; if it turned None into the raw window level it would apply a ceiling in
    years that had none. The two must agree on WHERE the answer exists, and
    differ only in the units of the answer.
    """
    probe = date.fromisoformat(PROBE_DATE)
    inc = binding_cap_unit_rate_gbp_per_mwh_inc_vat("electricity", probe)
    ex = binding_cap_unit_rate_gbp_per_mwh_ex_vat("electricity", probe)
    assert inc is not None and ex is not None
    assert ex < inc, "the ex-VAT ceiling must be the lower of the two"
    assert ex * (1.0 + DOMESTIC_VAT_RATE) == pytest.approx(inc)

    for fuel, when in (
        ("electricity", date(2015, 1, 1)),   # before the first published window
        ("gas", date(2015, 1, 1)),
        ("hydrogen", probe),                 # not a domestically capped fuel
    ):
        assert binding_cap_unit_rate_gbp_per_mwh_inc_vat(fuel, when) is None
        assert binding_cap_unit_rate_gbp_per_mwh_ex_vat(fuel, when) is None, (
            f"the ex-VAT accessor invented a ceiling for ({fuel}, {when}) where the "
            "inc-VAT accessor says there is none"
        )


def test_the_worlds_ceiling_cannot_be_obtained_without_naming_its_vat_basis():
    """THE CLASS, enforced by AST rather than by prose.

    MUTATION (must fire): add
    `binding_cap_unit_rate_gbp_per_mwh = binding_cap_unit_rate_gbp_per_mwh_inc_vat`
    to `simulation/price_cap_enforcement.py` — the obvious back-compatibility
    kindness, and the exact shape that let this defect exist for as long as it
    did.

    The class is not "someone divided by the wrong number". It is that a
    published figure carrying a basis in its metadata can be read into a
    comparison that carries none, and the comparison looks fine. Every repair
    that stops at the arithmetic leaves the next author one autocomplete away
    from repeating it, so the repair is that the number has no basis-less name to
    reach for.

    DELIBERATELY SCOPED TO THE WORLD. `company/pricing/ofgem_price_cap.py` still
    exposes basis-less accessors and `company/pricing/renewal_rate_chain.py` still
    clamps an ex-VAT rate against an inc-VAT ceiling. That is left standing on
    purpose (finding §3): the company's cap arithmetic is a BELIEF, the world's is
    the LAW, and leaving the belief wrong while the truth is right converts a
    silent shared error into a visible belief-versus-truth gap — the coupled triad
    working as designed. Extending this ratchet across the wall would erase the
    gap and would also be the company reading the world's opinion of what a good
    name is.
    """
    tree = ast.parse(WORLD_READING.read_text())
    offenders = []
    for node in tree.body:
        names: list[str] = []
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names = [node.name]
        elif isinstance(node, ast.Assign):
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names = [node.target.id]
        for name in names:
            if name.startswith("_") or "cap_unit_rate" not in name:
                continue
            if not (name.endswith("_inc_vat") or name.endswith("_ex_vat")):
                offenders.append(name)

    assert offenders == [], (
        f"{WORLD_READING.relative_to(REPO_ROOT)} exposes cap accessor(s) whose name does "
        f"not declare a VAT basis: {offenders}. The published cap levels are inc-VAT and "
        "every rate this codebase settles is ex-VAT, so a caller that does not have to "
        "choose will pick wrong exactly as `run_deemed_term` did until 2026-08-25. Name "
        "it `..._inc_vat` or `..._ex_vat`."
    )


def test_every_logged_SVT_position_reads_a_struck_rate_on_the_published_basis():
    """The switching reference's sixth implementation of the VAT rule (2026-10-01). The world
    logs a struck rate's position against the SVT in three places: the customer event's
    `price_differential_vs_svt`, `churn_basis_risk`'s `rate_vs_svt_pct`, and the price ladder's
    reconciler of the first. Each differenced an ex-VAT rate against the inc-VAT SVT, so a household
    paying exactly the SVT read 4.8% cheaper than it.

    PARITY IS THE PROBE: the ex-VAT rate a household sees as the SVT must read 0 at all three.
    MUTATION (must fire): drop `household_price_inc_vat` at any one site and that leg reads -4.76.
    """
    from simulation.customer_events import _svt_position
    from simulation.run_phase2b import _build_churn_basis_risk
    from simulation.svt_rates import get_svt_elec_rate_charged_to_household_gbp_per_mwh
    from tools.run_price_ladder import _svt_position_pct

    when = "2024-01-01"
    at_parity = get_svt_elec_rate_charged_to_household_gbp_per_mwh(when) / (1.0 + DOMESTIC_VAT_RATE)
    [record] = _build_churn_basis_risk([{
        "customer_id": "C1", "event_date": when, "commodity": "electricity",
        "unit_rate_gbp_per_mwh": at_parity,
        "company_churn_estimate": 0.1, "churn_estimate_error_pct": 0.0, "churn_probability": 0.1,
    }])

    assert _svt_position(at_parity, when, commodity="electricity") == pytest.approx(0.0, abs=1e-4)
    assert _svt_position_pct(at_parity, when, commodity="electricity") == pytest.approx(0.0, abs=1e-6)
    assert record["rate_vs_svt_pct"] == pytest.approx(0.0, abs=0.01)


def test_a_gas_offer_is_read_against_the_GAS_default_tariff_at_every_site(monkeypatch):
    """Until 2026-10-01 every one of these read the ELECTRICITY SVT whatever the leg, so a gas
    offer at the gas SVT read about 80% cheaper than the market -- past the departure curve's
    -0.30 saturation, so no gas price the company could charge reached the departure roll.

    PARITY ON THE GAS SVT IS THE PROBE, at all six readings: the churn roll's differential, the
    level it was taken against, the logged SVT position, the ladder's reconciler and
    `churn_basis_risk`. A rival ledger is passed and must not move the gas reference: the rival is
    anchored and floored on electricity, and a gas leg has no rival yet.

    THE SAME RATE ON THE OTHER FUEL MUST NOT READ PARITY, which is the control that the fuel
    argument is reached at all -- every site reading one fuel for both would pass the parity legs
    for whichever fuel it read. MUTATION (must fire): answer `gas` with the electricity accessor in
    `_household_svt_gbp_per_mwh`, or drop `commodity` at any one call site, or let a gas leg reach
    the rival.

    THE CHASE IS PINNED AT 1.0 because at the shipped 0.5 the rival guard is an EQUIVALENCE, not a
    tested branch: half-way between the electricity SVT and any positive gas rate is always above
    the gas SVT, so `min(rival, gas SVT)` returns the gas SVT with or without the guard. Measured
    when this landed: removing the guard went green at 0.5. A full chase on a no-floor call lets
    the rival read below the gas SVT, which is the only state in which the guard decides anything.
    """
    from simulation import competitor_reference
    from simulation.competitor_reference import CompanyPositionLedger
    from simulation.customer_events import (
        _market_reference_gbp_per_mwh,
        _price_differential_vs_market,
        _svt_position,
    )
    from simulation.run_phase2b import _build_churn_basis_risk
    from simulation.svt_rates import (
        get_svt_elec_rate_charged_to_household_gbp_per_mwh,
        get_svt_gas_rate_charged_to_household_gbp_per_mwh,
    )
    from tools.run_price_ladder import _svt_position_pct

    when = "2024-01-01"
    gas_svt = get_svt_gas_rate_charged_to_household_gbp_per_mwh(when)
    elec_svt = get_svt_elec_rate_charged_to_household_gbp_per_mwh(when)
    at_parity = gas_svt / (1.0 + DOMESTIC_VAT_RATE)
    ledger = CompanyPositionLedger()
    ledger.observe("2023-11-15", at_parity * 0.5)   # a rival that saw a deep undercut last quarter
    monkeypatch.setattr(competitor_reference, "aggression",
                        lambda: {"chase_per_quarter": 1.0, "min_retail_margin_pct": 0.03})

    [record] = _build_churn_basis_risk([{
        "customer_id": "C1", "event_date": when, "commodity": "gas",
        "unit_rate_gbp_per_mwh": at_parity,
        "company_churn_estimate": 0.1, "churn_estimate_error_pct": 0.0, "churn_probability": 0.1,
    }])

    assert _price_differential_vs_market(
        at_parity, when, commodity="gas", position_ledger=ledger,
    ) == pytest.approx(0.0, abs=1e-9)
    assert _market_reference_gbp_per_mwh(
        when, commodity="gas", position_ledger=ledger) == pytest.approx(gas_svt)
    assert _svt_position(at_parity, when, commodity="gas") == pytest.approx(0.0, abs=1e-4)
    assert _svt_position_pct(at_parity, when, commodity="gas") == pytest.approx(0.0, abs=1e-6)
    assert record["rate_vs_svt_pct"] == pytest.approx(0.0, abs=0.01)
    assert record["svt_rate_gbp_per_mwh"] == pytest.approx(gas_svt)

    # The fuel is reached: the same rate on the other fuel is nowhere near parity.
    assert gas_svt < 0.5 * elec_svt
    assert _price_differential_vs_market(at_parity, when, commodity="electricity") < -0.40
    assert _svt_position(at_parity, when, commodity="electricity") < -0.40


def test_a_fuel_with_no_published_default_tariff_is_refused_by_name():
    """A refusal that names its reason, rather than answering with one of the two series."""
    from simulation.customer_events import _svt_position

    with pytest.raises(ValueError, match="'heat'"):
        _svt_position(100.0, "2024-01-01", commodity="heat")
