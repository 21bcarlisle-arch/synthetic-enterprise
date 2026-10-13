"""The hedge volume reads only what a supplier holds: arrived meter reads and the registry figure.

Until 2026-10-11 `simulation/run_phase2b._company_eac_estimate` summed the settled fold's TRUE kWh
for the twelve months before a term -- months the company billed as estimates included -- and its
first-term fallback, and every gas term, multiplied the registry figure by the household's own
multipliers (`household_demand_register.eac_multiplier_for_date`, `gas_eac_multiplier_for_date`).
Finding: docs/staging/SEAT_FINDING_SEVERAL_CONSUMPTION_FORECASTS_A_WALL_LEAK_IN_HEDGE_VOLUME_AND_THE_CAPITAL_TARGET_IS_115_2026-10-11.md.

Each test names the defect it reds on:
  * the volume sums settled kWh again -> `test_a_year_of_estimated_months_leaves_the_company_on_the_registry`
  * a read that arrives after the term starts is counted -> `test_a_read_arriving_after_the_term_starts_is_not_held`
  * the hedge is handed a world multiplier or a settled figure -> `test_every_hedge_volume_in_the_run_is_the_companys_estimate`
  * the hedge books at the company's own forward belief, not the market's quote ->
    `test_every_hedge_the_run_books_is_struck_at_the_markets_forward_quote`
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import pytest

import simulation.run_phase2b as p2
from company.billing.unread_month_estimate import annualised_advance_kwh
from company.interfaces.sim_interface import supplier_annual_volume_kwh
from simulation.settlement_fold import SettlementFold

CID = "C_HEDGE_VOLUME_TEST"
REGISTRY = 3_100.0


@dataclass
class _Event:
    status: str
    delay_days: int


class _Feed:
    """Every month's read arrives (or none does), `delay` days after the month's last day."""

    def __init__(self, arrives: bool, delay: int = 0):
        self.arrives, self.delay = arrives, delay

    def meter_type_for(self, customer):
        return "traditional"

    def read_for(self, cid, period_end, meter_type, kwh, consecutive):
        return _Event("actual" if self.arrives else "estimated", self.delay)


def _fold(start=date(2018, 1, 1), days=760, kwh_per_day=10.0):
    fold = SettlementFold()
    fold.add([{"customer_id": CID, "settlement_date": (start + timedelta(days=i)).isoformat(),
               "consumption_kwh": kwh_per_day} for i in range(days)])
    return fold


@pytest.fixture
def registry(monkeypatch):
    monkeypatch.setitem(p2.EFFECTIVE_EAC_KWH, CID, REGISTRY)
    monkeypatch.setattr(p2, "get_customer", lambda cid: {"customer_id": cid, "aq_kwh": 12_000})


def test_the_partition_both_branches_are_reachable(registry):
    """A guard that always answers the registry passes every refusal test, so first: with reads
    arriving, the volume is NOT the registry; without them, it is."""
    fold = _fold()
    read = p2._company_eac_estimate(CID, "2019-07-01", fold, read_feed=_Feed(True))
    unread = p2._company_eac_estimate(CID, "2019-07-01", fold, read_feed=_Feed(False))
    assert read != pytest.approx(REGISTRY) and unread == pytest.approx(REGISTRY)


def test_a_year_of_estimated_months_leaves_the_company_on_the_registry(registry):
    """Eighteen settled months, none read: the settled fold holds ~5,500 kWh for the year, and the
    company has seen none of it."""
    assert p2._company_eac_estimate(CID, "2019-07-01", _fold(), read_feed=_Feed(False)) == \
        pytest.approx(REGISTRY)
    assert p2._company_eac_estimate(CID, "2019-07-01", _fold(), commodity="gas",
                                    read_feed=_Feed(False)) == pytest.approx(12_000)


def test_with_every_read_arriving_the_volume_is_the_annualised_advance(registry):
    """10 kWh a day settled, read monthly: the advance closes on 2019-12-31 and opens a year
    earlier, so the profile weight is exactly one and the volume is 3,650 kWh."""
    assert p2._company_eac_estimate(CID, "2020-01-15", _fold(), read_feed=_Feed(True)) == \
        pytest.approx(3_650.0)


def test_a_read_arriving_after_the_term_starts_is_not_held(registry):
    """A December read 20 days late is not on the desk on 15 January; November's is."""
    reads = p2._company_held_register_reads(CID, "2020-01-15", _fold(), _Feed(True, delay=20))
    assert reads[-1][0] == date(2019, 11, 30)


def test_the_advance_opens_on_the_read_nearest_a_year_and_refuses_under_six_months():
    reads = [(date(2018, 12, 31), 0.0), (date(2019, 6, 30), 1_000.0),
             (date(2019, 12, 31), 3_000.0)]
    kwh, opened, closed = annualised_advance_kwh("electricity", reads)
    assert (opened, closed, kwh) == (date(2018, 12, 31), date(2019, 12, 31), pytest.approx(3_000.0))
    assert annualised_advance_kwh("electricity", reads[1:2] + [(date(2019, 9, 30), 2_000.0)]) is None


def test_the_seam_answers_the_registry_only_without_an_advance():
    assert supplier_annual_volume_kwh("gas", [], 11_000)["basis"] == "registry"
    assert supplier_annual_volume_kwh("gas", [], None) == \
        {"kwh": 0.0, "basis": "none", "from": None, "to": None}
    assert supplier_annual_volume_kwh(
        "gas", [(date(2018, 12, 31), 0.0), (date(2019, 12, 31), 9_000.0)], 11_000)["basis"] == \
        "annualised_advance"


# ── the run's own call sites ────────────────────────────────────────────────────────────────

_RUN = Path(p2.__file__)
_WORLD_READS = {"consumption_kwh_between", "total_consumption_kwh", "eac_multiplier_for_date",
                "gas_eac_multiplier_for_date", "household_demand_register"}


def _assigned_from(tree: ast.Module, name: str) -> list[ast.expr]:
    return [node.value for node in ast.walk(tree)
            if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == name for t in node.targets)]


def _called(expr: ast.expr) -> str | None:
    return expr.func.id if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name) else None


def test_every_hedge_volume_in_the_run_is_the_companys_estimate():
    """Every `volume_kwh=` the run hands the desk is a name assigned only from
    `_company_eac_estimate`, and neither that function nor the reader beneath it touches the
    settled fold's totals or a household multiplier. Pointing the gas leg back at the multiplied
    `aq_kwh` reds the first half; summing the fold again inside the estimate reds the second."""
    tree = ast.parse(_RUN.read_text())
    volumes = [kw.value for node in ast.walk(tree) if isinstance(node, ast.Call)
               and isinstance(node.func, ast.Attribute)
               and node.func.attr in ("decide_term_hedge", "open_term_hedge")
               for kw in node.keywords if kw.arg == "volume_kwh"]
    assert len(volumes) >= 3, "the desk's call sites moved: re-point this control at them"
    for v in volumes:
        assert isinstance(v, ast.Name), ast.unparse(v)
        sources = _assigned_from(tree, v.id)
        assert sources and all(_called(e) == "_company_eac_estimate" for e in sources), (
            f"`volume_kwh={v.id}` is assigned from {[ast.unparse(e) for e in sources]}: the desk "
            "may be handed only the company's own estimate")
    funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    for fname in ("_company_eac_estimate", "_company_volume_reading"):
        touched = {n.attr if isinstance(n, ast.Attribute) else n.id
                   for n in ast.walk(funcs[fname]) if isinstance(n, (ast.Attribute, ast.Name))}
        assert not touched & _WORLD_READS, f"{fname} reads {touched & _WORLD_READS}"


def test_the_published_demand_error_grades_the_year_that_followed():
    """`demand_estimation_log.error_pct` used to set the trailing settled year against the run's
    mean settled year: two backward reads of one fold. It now grades the twelve months FROM the
    term start, and a term whose year the run never finished settling stays ungraded."""
    fold = SettlementFold()
    fold.add([{"customer_id": CID, "settlement_date": (date(2018, 1, 1) + timedelta(days=i)).isoformat(),
               "consumption_kwh": 10.0 if i < 365 else 12.0} for i in range(800)])
    log = [{"customer_id": CID, "term_start": "2019-01-01", "company_eac_kwh": 3650},
           {"customer_id": CID, "term_start": "2019-06-01", "company_eac_kwh": 3650}]
    p2._grade_demand_estimates_against_the_year_ahead(log, fold)
    assert log[0]["true_eac_kwh"] == 4380 and log[0]["error_pct"] == pytest.approx(-16.67)
    assert log[1].get("error_pct") is None and log[1]["ungraded_reason"]


def test_every_hedge_the_run_books_is_struck_at_the_markets_forward_quote():
    """A counterparty executes at its own quote, never at the supplier's private forecast
    (docs/market_research/a_hedge_executes_at_the_markets_quote_not_the_companys_own_forward_estimate_2026-10-12.md).
    Every `forward_price_gbp_per_mwh=` handed to `open_term_hedge` is a name assigned only from
    the term's PIT market forward, `term["forward_price_gbp_per_mwh"]`. Pointing the booking back
    at `company_fwd` reds it; `decide_term_hedge` is free to size off the company's belief."""
    tree = ast.parse(_RUN.read_text())
    prices = [kw.value for node in ast.walk(tree) if isinstance(node, ast.Call)
              and isinstance(node.func, ast.Attribute) and node.func.attr == "open_term_hedge"
              for kw in node.keywords if kw.arg == "forward_price_gbp_per_mwh"]
    assert prices, "the run books no hedge: re-point this control at the booking call"
    for v in prices:
        assert isinstance(v, ast.Name), ast.unparse(v)
        sources = _assigned_from(tree, v.id)
        assert sources and all(
            isinstance(e, ast.Subscript) and isinstance(e.slice, ast.Constant)
            and e.slice.value == "forward_price_gbp_per_mwh" for e in sources), (
            f"`forward_price_gbp_per_mwh={v.id}` is assigned from "
            f"{[ast.unparse(e) for e in sources]}: a hedge books at the market's quote")
