"""The supplier-side Capacity Market charge: a levy on demand, read not derived.

WHAT THIS FILE HAD TO CHANGE FOR (2026-09-07, a51-derating-callers-and-the-dsr-cmu-shape). The
module under test carried `_DERATING_FACTOR = 0.92  # Assumed average de-rated supply margin %`
applied to a SUPPLIER obligation -- an invented constant named for a concept that does not apply to
the quantity it multiplied, because de-rating is a haircut on a capacity PROVIDER's capacity and
demand is not de-rated. Beside it, `_CM_OBLIGATION_RATE_BY_YEAR` was a fourth home for the CM
clearing price, ending in a `.get(year, _RATE[2025])` fail-open.

TWO OF THE CONTROLS IN THIS FILE ASSERTED THOSE DEFECTS AS THE CONTRACT, which is why they are gone
rather than adjusted:

  * `test_derating_factor_reduces_obligation` recomputed `gross_kw * 0.92` and asserted the module
    agreed. Keyed to today's answer, so it would have gone red the moment the constant became more
    honest and stayed green for as long as 0.92 was wrong -- exactly backwards.
  * `test_cm_obligation_unknown_year_uses_2025_rate` asserted that an UNRECOGNISED year returns the
    2025 rate, i.e. it pinned the fail-open default as the intended behaviour. A control can make a
    defect permanent by describing it, and this one did.

`test_crisis_year_higher_rate` and `test_cm_obligation_2021_rate` read the deleted price table and
are replaced by legs over the published levy, which is a different series that moves differently --
2022 is the case that matters and it moves the OTHER WAY.

AND SIX MORE WENT ON 2026-09-07 (a52), FOR THE SAME REASON ONE STEP UP. `test_penalty_formula`,
`test_shortfall_when_partial`, `test_delivered_when_firm_capacity_meets_obligation`,
`test_failed_when_no_firm_capacity`, `test_penalty_zero_when_delivered` and
`test_every_delivery_status_branch_is_reachable` all exercised a capacity PROVIDER's delivery
obligation on a supplier. They were not wrong about the code -- every one of them passed, and the
last was written carefully, deriving its fixture from the branch definition precisely so it would
not be fitted to the conclusion. That care went into proving a partition over a quantity that should
not have existed, which is what a suite can do when it takes the module's subject on trust. The
replacement below is keyed to the ABSENCE of the concept, so it holds against a re-introduction that
picks different names.
"""
import dataclasses
import inspect

import pytest

from company.regulatory.capacity_market import (
    _LEVY_GBP_PER_MWH,
    CMObligationResult,
    cm_charge_per_mwh,
    cm_levy_gbp_per_mwh,
    compute_cm_obligation,
)


def test_obligation_structure():
    result = compute_cm_obligation(2024, 10_000_000)
    assert result.year == 2024
    assert result.obligation_kw > 0
    assert result.annual_charge_gbp > 0


def test_annual_charge_scales_with_demand():
    r1 = compute_cm_obligation(2024, 1_000_000)
    r2 = compute_cm_obligation(2024, 2_000_000)
    assert r2.annual_charge_gbp > r1.annual_charge_gbp


def test_cm_charge_per_mwh_positive():
    charge = cm_charge_per_mwh(2024, 5_000_000)
    assert charge > 0


def test_cm_charge_per_mwh_zero_demand():
    charge = cm_charge_per_mwh(2024, 0)
    assert charge == 0.0


# --- The delivery verdict for this module, 2026-09-07 (a52). A supplier's CM obligation is a
# --- payment: it has no delivery status, no shortfall and no non-delivery penalty.

#: The vocabulary a provider's delivery obligation arrives in. Deliberately wider than the four
#: names that were actually deleted, because the failure mode is a re-introduction that picks
#: different words for the same concept -- `met_obligation`, `stress_event_response`, `underdelivery`.
_PROVIDER_DELIVERY_VOCABULARY = (
    "deliver", "shortfall", "penalt", "firm_capacity", "stress", "underdeliver", "non_delivery",
)


def _delivery_words_in(names):
    return {n for n in names if any(w in n.lower() for w in _PROVIDER_DELIVERY_VOCABULARY)}


def test_a_supplier_result_carries_no_delivery_obligation_concept():
    """The defect: a capacity PROVIDER's delivery obligation modelled on a supplier.

    Read off the live dataclass fields and the live signature -- NOT off the module's source text,
    which necessarily quotes `delivery_status`, `shortfall_kw` and `penalty_gbp` in the docstring
    explaining why they are gone. A source-text control here would be reading its own explanation
    and reporting the defect it documents.

    THE POISON LEG IS THE POINT. `_delivery_words_in` is asserted to FIRE on the four names that
    were removed before it is asserted to stay silent on the surface that remains, because
    "found nothing" is otherwise indistinguishable from a matcher that can never match -- and this
    control's whole value is in the years where it correctly finds nothing.
    """
    deleted = {"delivery_status", "shortfall_kw", "penalty_gbp", "firm_capacity_kw"}
    assert _delivery_words_in(deleted) == deleted, (
        "reachability: the matcher must flag the very names this control exists to keep out")

    surface = (
        {f.name for f in dataclasses.fields(CMObligationResult)}
        | set(inspect.signature(compute_cm_obligation).parameters)
    )
    assert surface, "reachability: an empty surface would pass this vacuously"
    assert _delivery_words_in(surface) == set(), (
        f"{_delivery_words_in(surface)} is a capacity PROVIDER's delivery obligation on a "
        "SUPPLIER result. A supplier discharges its CM obligation by paying; the provider side "
        "with a real penalty ledger is company/market/capacity_market.py::CMObligation.")


def test_the_charge_a_supplier_pays_does_not_depend_on_any_capacity_it_holds():
    """The defect: a supplier levy that a contracted capacity could reduce.

    The deleted legs let a caller hand this function a `firm_capacity_kw`, and the concern is not
    only that the field is gone but that no successor may re-enter the money. Keyed to the
    PROPERTY -- the charge is a function of year and volume alone -- so it holds however a future
    edit spells the capacity argument.

    There is a real lever and this is not it: a supplier reduces this charge by moving demand out
    of the winter peak periods the levy is assessed on, which changes the VOLUME term. Owning a
    power station does not.
    """
    assert len(inspect.signature(compute_cm_obligation).parameters) == 2, (
        "compute_cm_obligation takes the obligation year and the volume; a third input to a "
        "levy that is published per MWh supplied is a quantity nobody publishes")
    levy = cm_levy_gbp_per_mwh(2024)
    assert compute_cm_obligation(2024, 5_000_000).annual_charge_gbp == pytest.approx(
        5_000_000 * levy)


# --- The de-rating verdict for this module, 2026-09-07 (a51). The answer was NO FACTOR, because
# --- the concept does not apply to a supplier obligation -- not because none was available.


def test_no_derating_factor_is_applied_to_a_supplier_obligation():
    """The defect: a de-rating factor applied to demand, which is never de-rated.

    Keyed to the PROPERTY -- peak-period demand is the raw peak estimate with no haircut -- rather
    than to any particular factor, so it fails for ANY multiplier a future edit reintroduces,
    including one read legitimately from the published register.
    """
    demand_mwh = 1_000_000
    result = compute_cm_obligation(2024, demand_mwh)
    undiscounted_peak_kw = round((demand_mwh / 8760.0) * 1.8 * 1000, 1)
    assert result.obligation_kw == pytest.approx(undiscounted_peak_kw, abs=1.0), (
        f"obligation_kw {result.obligation_kw} is not the raw peak estimate "
        f"{undiscounted_peak_kw} -- something is de-rating a demand quantity")


def test_the_charge_is_the_published_levy_times_volume_and_nothing_else():
    """The defect: deriving a supplier levy from an auction clearing price.

    The identity is the control. If any factor, peak estimate or price re-enters the money path
    this fails, and it cannot pass vacuously because the levy is asserted non-trivial first.
    """
    levy = cm_levy_gbp_per_mwh(2023)
    assert levy is not None and levy > 1.0, "reachability: the levy must be a real published rate"
    result = compute_cm_obligation(2023, 5_000_000)
    assert result.annual_charge_gbp == pytest.approx(5_000_000 * levy)
    assert cm_charge_per_mwh(2023, 5_000_000) == pytest.approx(levy)
    # ...and the per-MWh charge is volume-invariant, which a peak-times-price route was not.
    assert cm_charge_per_mwh(2023, 50_000) == pytest.approx(cm_charge_per_mwh(2023, 50_000_000))


def test_the_published_levy_falls_in_2022_when_the_clearing_price_hit_its_cap():
    """The defect: a levy modelled off a clearing price gets 2022 backwards.

    The T-1 for delivery year 2022/23 cleared at the GBP75/kW price CAP -- the highest number in
    the whole auction record -- and the supplier levy FELL, because the volume behind that price
    was small and the suspended T-4's replacement T-3 was cheap. This is the single year that
    proves the two series are different quantities rather than one series in different units, and
    the deleted table asserted the opposite (`test_crisis_year_higher_rate`).
    """
    assert cm_levy_gbp_per_mwh(2022) < cm_levy_gbp_per_mwh(2021)
    assert cm_levy_gbp_per_mwh(2022) < cm_levy_gbp_per_mwh(2023)


def test_an_unpublished_year_refuses_instead_of_carrying_the_last_rate_forward():
    """The defect: `.get(year, _RATE[2025])` making an unpublished year look established.

    Both legs: the refusal fires for a year outside the record AND names the record's range, and
    a year inside it still answers -- a guard that refused everything would pass a one-sided test.
    """
    assert cm_levy_gbp_per_mwh(9999) is None
    assert cm_levy_gbp_per_mwh(max(_LEVY_GBP_PER_MWH)) is not None
    with pytest.raises(ValueError) as excinfo:
        compute_cm_obligation(9999, 1_000_000)
    assert str(max(_LEVY_GBP_PER_MWH)) in str(excinfo.value), (
        "a refusal must name the record it is refusing against")


def test_the_module_no_longer_holds_its_own_copy_of_the_clearing_price():
    """The defect: a fourth home for the CM clearing price.

    The register's DY2024 T-4 cleared at GBP18.00/kW and this module used to carry 65.00 under the
    key 2024. Asserted as an ABSENCE of the symbol, because the failure mode is a well-meaning
    edit reinstating a local table 'for convenience'.
    """
    import company.regulatory.capacity_market as mod

    assert not hasattr(mod, "_CM_OBLIGATION_RATE_BY_YEAR")
    assert not hasattr(mod, "_DERATING_FACTOR")
    # ...and the levy it does hold is in GBP/MWh, an order of magnitude away from any GBP/kW
    # clearing price, so a re-introduced price could not masquerade as this series.
    assert all(0.1 < rate < 20.0 for rate in _LEVY_GBP_PER_MWH.values())


def test_a_malformed_commons_raises_rather_than_degrading_to_no_levy(tmp_path, monkeypatch):
    """The defect: a missing or empty artefact falling back to "no levy" instead of refusing.

    ADDED BECAUSE A MUTATION SURVIVED AND THE SURVIVAL WAS AN EQUIVALENCE, NOT A PASS. Replacing
    `_load_levy`'s empty-series `raise` with `return {}` killed nothing, because that branch is
    unreachable while the real artefact is well-formed -- so no test could have exercised it, and
    reading the survival as "the code is fine" would have been the flattering answer rather than
    the true one. This makes the branch reachable.

    Both malformed shapes, because they arrive by different routes: an artefact that is missing
    entirely, and one that is present but carries no series (a truncated write, a schema change).
    """
    import company.regulatory.capacity_market as mod

    absent = tmp_path / "gone.json"
    monkeypatch.setattr(mod, "_COMMONS", absent)
    with pytest.raises(FileNotFoundError, match="no invented default"):
        mod._load_levy()

    empty = tmp_path / "empty.json"
    empty.write_text('{"artefact": "capacity_market_supplier_levy", "levy_gbp_per_mwh": []}')
    monkeypatch.setattr(mod, "_COMMONS", empty)
    with pytest.raises(ValueError, match="carries no series"):
        mod._load_levy()

    # ...and the real artefact still loads, so this is not a guard that refuses everything.
    monkeypatch.undo()
    assert mod._load_levy()


# ---------------------------------------------------------------------------
# a53: the charge now REACHES SOMETHING. Until 2026-09-07 this file was the only
# importer of the module above -- correctly sourced, carefully tested, and wired
# to nothing, which is the `saas/opex_ledger.py` shape where a right number sits
# looking established while production spends a different one. The controls below
# are keyed to the module having a PRODUCTION consumer, not to today's figures.
# ---------------------------------------------------------------------------


def _levy_from_the_commons(year: int) -> float:
    """The published levy, read from the artefact WITHOUT going through the module.

    Deliberately not `cm_levy_gbp_per_mwh(year)`. A control that gets its expected value from
    the subject reads `x == x` for every value of x, so the wiring check below would survive
    the levy being replaced by anything at all as long as both sides changed together.
    """
    import json
    from pathlib import Path

    artefact = (
        Path(__file__).resolve().parents[3]
        / "docs" / "domain_artefact_library" / "regulatory"
        / "capacity_market_supplier_levy.json"
    )
    rows = json.loads(artefact.read_text())["levy_gbp_per_mwh"]
    return float(next(r["gbp_per_mwh"] for r in rows if r["obligation_year"] == year))


def _records_for(years, kwh_per_month):
    return [
        {
            "customer_id": "E-1",
            "settlement_date": f"{y}-{m:02d}-01",
            "consumption_kwh": kwh_per_month,
            "commodity": "elec",
        }
        for y in years
        for m in range(1, 13)
    ]


def test_the_supplier_cm_charge_reaches_the_statutory_return():
    """The defect a53 names: the module computes a correct charge that no caller reads.

    Behavioural, through the real production entry point -- `build_statutory_obligations` is
    what `simulation/run_phase2b.py` calls. Deleting the CM leg, or pointing it at a different
    series, changes the number this asserts. The expected value is built from the commons
    artefact and plain arithmetic, so it cannot agree with the module by construction.
    """
    from company.regulatory.statutory_obligations import build_statutory_obligations

    published_years = ["2019", "2024"]
    kwh = 1_000_000.0  # 1 GWh/month -> 12,000 MWh/yr, well clear of any rounding
    result = build_statutory_obligations(
        settled_records=_records_for(published_years, kwh),
        report_years=published_years,
        ic_elec_customer_ids=set(),
        ic_gas_customer_ids=set(),
    )

    per_year = result.cm_summary["per_year"]
    for yr in published_years:
        expected = 12 * kwh / 1000.0 * _levy_from_the_commons(int(yr))
        assert per_year[yr]["cm_levy_gbp"] == pytest.approx(expected), (
            f"the statutory return's {yr} CM cost is not the published levy times the volume "
            "supplied -- either the leg is gone or it is reading a different series"
        )
    # The two years carry DIFFERENT levies, so this cannot pass with one rate stamped on both.
    assert per_year["2019"]["levy_gbp_per_mwh"] != per_year["2024"]["levy_gbp_per_mwh"]
    assert result.cm_summary["total_cm_levy_gbp"] == pytest.approx(
        sum(per_year[y]["cm_levy_gbp"] for y in published_years)
    )


def test_an_unpublished_year_is_a_gap_in_the_return_and_not_a_zero_or_a_carry_forward():
    """The defect: the return filling a year Ofgem has not published.

    Both fail-open shapes are refused, because they arrive by different routes and read as
    different lies: a ZERO says the levy cost nothing, and a CARRY-FORWARD says last year's
    rate is this year's law. The world's own reading (`simulation/policy_costs`) does carry
    forward, on purpose -- so this is a real difference between the two readings and not a
    detail.

    THE PARTITION IS ASSERTED FIRST. A `_cm_summary` that refused EVERY year would satisfy
    every leg below, so the fixture is checked to produce both kinds of year before either
    kind is examined.
    """
    from company.regulatory.statutory_obligations import build_statutory_obligations

    years = ["2024", "2099"]  # one in the published record, one that never will be
    result = build_statutory_obligations(
        settled_records=_records_for(years, 1_000_000.0),
        report_years=years,
        ic_elec_customer_ids=set(),
        ic_gas_customer_ids=set(),
    )
    cm = result.cm_summary

    assert cm["published_years"] == ["2024"] and cm["unpublished_years"] == ["2099"], (
        "both branches must be reachable in this fixture, or the legs below prove nothing"
    )

    gap = cm["per_year"]["2099"]
    assert gap["cm_levy_gbp"] is None, "an unpublished year must be absent, never a number"
    assert gap["levy_gbp_per_mwh"] is None
    assert gap["cm_levy_gbp"] != 0, "a zero would read as 'this cost nothing'"
    assert gap["levy_gbp_per_mwh"] != cm["per_year"]["2024"]["levy_gbp_per_mwh"], (
        "a carried-forward rate would read as established law"
    )
    assert "2099" in (gap["unpublished_reason"] or ""), "a refusal must name its reason"
    # ...and the volume is still reported, so the year is a GAP in the charge and not a hole
    # in the book. A missing year and a year with no published levy are different facts.
    assert gap["elec_mwh"] > 0

    # The total is the PUBLISHED years only, and says so by matching that year alone.
    assert cm["total_cm_levy_gbp"] == pytest.approx(cm["per_year"]["2024"]["cm_levy_gbp"])


def test_the_run_and_the_report_both_carry_the_statutory_cm_key():
    """The defect: the leg computed, then silently dropped between the run and the page.

    `extract_report_data` is a WHITELIST -- its own comments record a past incident where it
    dropped a computed block and every board surface reading the feed went blind. So the run's
    output key and the whitelist are checked as a pair.

    AST, not a grep. A source-text search counts a comment that quotes the key; this reads the
    dict keys the parser actually sees.
    """
    import ast
    import os

    root = os.path.join(os.path.dirname(__file__), "..", "..", "..")

    def _string_dict_keys(tree) -> set:
        return {
            k.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Dict)
            for k in node.keys
            if isinstance(k, ast.Constant) and isinstance(k.value, str)
        }

    run_tree = ast.parse(
        open(os.path.join(root, "simulation", "run_phase2b.py"), encoding="utf-8").read()
    )
    run_keys = _string_dict_keys(run_tree)
    assert "cm_statutory_summary" in run_keys, (
        "run_phase2b no longer emits the supplier's statutory CM position"
    )
    # Vacuity guard: a parse that produced no keys would pass the line above for free.
    assert "ccl_summary" in run_keys and len(run_keys) > 50

    report_tree = ast.parse(
        open(os.path.join(root, "saas", "reporting", "annual_report.py"), encoding="utf-8").read()
    )
    extract = next(
        n for n in ast.walk(report_tree)
        if isinstance(n, ast.FunctionDef) and n.name == "extract_report_data"
    )
    # The key must be present AND fed from the run output's own key of the same name. A key
    # mapped to the wrong source publishes a real number for the wrong quantity, which no
    # presence check would notice.
    mapping = {
        k.value: ast.unparse(v)
        for node in ast.walk(extract)
        if isinstance(node, ast.Dict)
        for k, v in zip(node.keys, node.values)
        if isinstance(k, ast.Constant) and isinstance(k.value, str)
    }
    assert "ccl_summary" in mapping, "the whitelist could not be read -- vacuity guard"
    assert "cm_statutory_summary" in mapping, (
        "the report's extract whitelist drops the statutory CM position"
    )
    assert "cm_statutory_summary" in mapping["cm_statutory_summary"], (
        "the statutory CM key is fed from something other than the run's own "
        f"cm_statutory_summary: {mapping['cm_statutory_summary']}"
    )
