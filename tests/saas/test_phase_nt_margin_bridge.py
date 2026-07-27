"""Tests for saas/reporting/margin_attribution.py -- Phase NT."""

import pytest
import dataclasses

from saas.reporting.margin_attribution import (
    MarginBridge,
    build_margin_bridge_series,
    dominant_driver,
    residual_is_material,
    residual_breaks_reconciliation,
    _direction,
    _FLAT_THRESHOLD_GBP,
    _RESIDUAL_MATERIALITY_GBP,
)


def _year(net=100_000, gross=300_000, bad_debt=50_000, capital=20_000,
          policy_cost=80_000, gas_policy_cost=10_000,
          network_cost=30_000, gas_network_cost=10_000,
          active_ids=None):
    return {
        "net_gbp": net,
        "gross_gbp": gross,
        "bad_debt_gbp": bad_debt,
        "capital_gbp": capital,
        "policy_cost_gbp": policy_cost,
        "gas_policy_cost_gbp": gas_policy_cost,
        "network_cost_gbp": network_cost,
        "gas_network_cost_gbp": gas_network_cost,
        "active_customer_ids": active_ids or [],
    }


def _run_data(*year_dicts):
    keys = [str(2020 + i) for i in range(len(year_dicts))]
    return {"years": dict(zip(keys, year_dicts))}


class TestMarginBridge:
    def test_net_delta_correct(self):
        run = _run_data(_year(net=100_000), _year(net=130_000))
        bridges = build_margin_bridge_series(run)
        assert bridges[0].net_delta_gbp == pytest.approx(30_000)

    def test_gross_delta_correct(self):
        run = _run_data(_year(gross=300_000), _year(gross=350_000))
        bridges = build_margin_bridge_series(run)
        assert bridges[0].gross_delta_gbp == pytest.approx(50_000)

    def test_bad_debt_delta_negative_when_cost_rose(self):
        # bad_debt rose from 50k to 100k -- margin contribution is negative
        run = _run_data(_year(bad_debt=50_000), _year(bad_debt=100_000))
        bridges = build_margin_bridge_series(run)
        assert bridges[0].bad_debt_delta_gbp == pytest.approx(-50_000)

    def test_capital_delta_negative_when_cost_rose(self):
        run = _run_data(_year(capital=20_000), _year(capital=60_000))
        bridges = build_margin_bridge_series(run)
        assert bridges[0].capital_delta_gbp == pytest.approx(-40_000)

    def test_policy_cost_delta_sums_both_components(self):
        # policy_cost 80k->90k and gas_policy_cost 10k->15k => delta = -(90+15 - 80-10) = -15k
        run = _run_data(
            _year(policy_cost=80_000, gas_policy_cost=10_000),
            _year(policy_cost=90_000, gas_policy_cost=15_000),
        )
        bridges = build_margin_bridge_series(run)
        assert bridges[0].policy_cost_delta_gbp == pytest.approx(-15_000)

    def test_network_cost_delta_sums_both_components(self):
        run = _run_data(
            _year(network_cost=30_000, gas_network_cost=10_000),
            _year(network_cost=50_000, gas_network_cost=20_000),
        )
        bridges = build_margin_bridge_series(run)
        assert bridges[0].network_cost_delta_gbp == pytest.approx(-30_000)

    def test_residual_near_zero(self):
        run = _run_data(_year(), _year(net=150_000, gross=350_000))
        bridges = build_margin_bridge_series(run)
        assert abs(bridges[0].residual_gbp) < 0.01

    def test_portfolio_change_positive_on_growth(self):
        run = _run_data(
            _year(active_ids=["A", "B"]),
            _year(active_ids=["A", "B", "C"]),
        )
        bridges = build_margin_bridge_series(run)
        assert bridges[0].portfolio_change == 1

    def test_portfolio_change_negative_on_churn(self):
        run = _run_data(
            _year(active_ids=["A", "B", "C"]),
            _year(active_ids=["A"]),
        )
        bridges = build_margin_bridge_series(run)
        assert bridges[0].portfolio_change == -2

    def test_year_label_format(self):
        run = _run_data(_year(), _year())
        bridges = build_margin_bridge_series(run)
        assert "2020" in bridges[0].year_label
        assert "2021" in bridges[0].year_label


class TestDirection:
    def test_improvement_above_threshold(self):
        assert _direction(_FLAT_THRESHOLD_GBP + 1) == "IMPROVEMENT"

    def test_deterioration_below_threshold(self):
        assert _direction(-_FLAT_THRESHOLD_GBP - 1) == "DETERIORATION"

    def test_flat_within_threshold(self):
        assert _direction(0) == "FLAT"
        assert _direction(_FLAT_THRESHOLD_GBP) == "FLAT"
        assert _direction(-_FLAT_THRESHOLD_GBP) == "FLAT"


class TestBuildSeries:
    def test_returns_n_minus_1_bridges(self):
        run = _run_data(_year(), _year(), _year())
        bridges = build_margin_bridge_series(run)
        assert len(bridges) == 2

    def test_returns_empty_for_single_year(self):
        run = _run_data(_year())
        bridges = build_margin_bridge_series(run)
        assert bridges == []

    def test_returns_empty_for_no_years(self):
        assert build_margin_bridge_series({}) == []

    def test_bridges_sorted_chronologically(self):
        run = _run_data(_year(), _year(), _year())
        bridges = build_margin_bridge_series(run)
        assert bridges[0].year_from < bridges[1].year_from


class TestDominantDriver:
    def test_bad_debt_dominates(self):
        # gross_delta=10k, bad_debt_delta=-200k => bad debt wins
        run = _run_data(_year(bad_debt=10_000), _year(bad_debt=210_000, gross=310_000))
        bridges = build_margin_bridge_series(run)
        assert dominant_driver(bridges[0]) == "bad debt"

    def test_gross_margin_dominates(self):
        run = _run_data(_year(gross=100_000), _year(gross=400_000))
        bridges = build_margin_bridge_series(run)
        assert dominant_driver(bridges[0]) == "gross margin"


def _bridge_with_residual(residual, named_max=1_000):
    """A MarginBridge with an arbitrary residual injected -- the exact symptom of
    a cost line entering net margin without a matching bridge driver. `named_max`
    is the largest named-driver magnitude so we can test the strict-dominance
    boundary."""
    return MarginBridge(
        year_from=2020, year_to=2021,
        net_delta_gbp=named_max + residual,
        gross_delta_gbp=named_max,
        bad_debt_delta_gbp=0.0,
        capital_delta_gbp=0.0,
        policy_cost_delta_gbp=0.0,
        network_cost_delta_gbp=0.0,
        portfolio_change=0,
        residual_gbp=residual,
        direction="FLAT",
    )


class TestResidualReconciliationControl:
    """R15 mutation tests: the reconciliation control must FIRE on its own named
    defect (a materially non-zero residual = a driver silently dropped from the
    bridge) and stay green on a well-reconciled bridge."""

    def test_control_green_on_reconciled_bridge(self):
        # Real, healthy state: residual ~0, drivers fully explain net movement.
        assert residual_is_material(_bridge_with_residual(0.0)) is False

    def test_control_fires_on_material_dominant_residual(self):
        # MUTATION: inject a large unexplained residual (as a dropped/renamed cost
        # line would). Control must fire -- this is the defect it exists to catch.
        b = _bridge_with_residual(500_000, named_max=1_000)
        assert residual_is_material(b) is True

    def test_control_does_not_fire_below_materiality_floor(self):
        # A residual under the floor is noise, not a break -- must stay green even
        # if it nominally exceeds a tiny named driver.
        b = _bridge_with_residual(_RESIDUAL_MATERIALITY_GBP - 1, named_max=0.0)
        assert residual_is_material(b) is False

    def test_control_requires_strict_dominance_over_named_drivers(self):
        # Residual material in absolute terms but NOT larger than the dominant
        # named driver -> the bridge still explains most of the movement, no fire.
        b = _bridge_with_residual(10_000, named_max=50_000)
        assert residual_is_material(b) is False

    def test_dominant_driver_reads_unexplained_when_residual_dominates(self):
        # The consumer effect (no orphan control, R11): the rendered Driver column
        # tells the truth instead of naming a minority contributor.
        b = _bridge_with_residual(500_000, named_max=1_000)
        assert dominant_driver(b) == "other (unexplained)"

    def test_dominant_driver_still_names_driver_when_reconciled(self):
        b = _bridge_with_residual(0.0, named_max=1_000)
        assert dominant_driver(b) == "gross margin"

    def test_control_works_on_renderer_reconstructed_object(self):
        # The report renderer rebuilds bridges as plain attribute-only objects
        # (type("B", (), dict)()), which lack the dataclass property. The control
        # must still work there -- guards against an AttributeError regression.
        b = _bridge_with_residual(500_000, named_max=1_000)
        plain = type("B", (), dataclasses.asdict(b))()
        assert residual_is_material(plain) is True
        assert dominant_driver(plain) == "other (unexplained)"

    def test_reconciliation_control_fires_on_break_masked_by_larger_driver(self):
        # THE FAIL-OPEN this control closes: a materially dropped cost line (£500k
        # residual) that is masked because a LARGER legitimate driver (£600k gross
        # swing) co-occurs in the same year. residual_is_material fails open here
        # (residual does not DOMINATE the £600k driver); the reconciliation control
        # must still fire -- a break is a break regardless of co-occurring drivers.
        b = MarginBridge(
            year_from=2020, year_to=2021,
            net_delta_gbp=100_000,
            gross_delta_gbp=600_000,      # larger legitimate driver
            bad_debt_delta_gbp=0.0, capital_delta_gbp=0.0,
            policy_cost_delta_gbp=0.0, network_cost_delta_gbp=0.0,
            portfolio_change=0,
            residual_gbp=-500_000,        # dropped cost line, does NOT dominate
            direction="FLAT",
        )
        assert residual_is_material(b) is False        # fails open (documented)
        assert residual_breaks_reconciliation(b) is True  # closes the gap

    def test_reconciliation_control_green_on_reconciled_bridge(self):
        assert residual_breaks_reconciliation(_bridge_with_residual(0.0)) is False

    def test_reconciliation_control_green_below_floor(self):
        assert residual_breaks_reconciliation(
            _bridge_with_residual(_RESIDUAL_MATERIALITY_GBP - 1, named_max=0.0)
        ) is False

    def test_reconciliation_control_fires_even_when_dominant(self):
        # The dominant case is a strict subset -- must also fire here.
        b = _bridge_with_residual(500_000, named_max=1_000)
        assert residual_breaks_reconciliation(b) is True

    def test_reconciliation_control_works_on_reconstructed_object(self):
        b = _bridge_with_residual(500_000, named_max=600_000)
        b = dataclasses.replace(b, net_delta_gbp=b.gross_delta_gbp + b.residual_gbp)
        plain = type("B", (), dataclasses.asdict(b))()
        assert residual_breaks_reconciliation(plain) is True

    def test_real_pipeline_bridges_reconcile(self):
        # The whole point of the tautology finding: on data built through the real
        # net = gross - (policy+gas_policy) - (network+gas_network) - capital
        # - bad_debt identity, every residual is ~0. If this ever fails, a driver
        # has been dropped from the bridge. Year A: 300 - 90 - 40 - 20 - 50 = 100.
        # Year B: 360 - 95 - 40 - 20 - 60 = 145.
        run = _run_data(
            _year(net=100_000),
            _year(net=145_000, gross=360_000, bad_debt=60_000, policy_cost=85_000),
        )
        for b in build_margin_bridge_series(run):
            assert abs(b.residual_gbp) < 0.01
            assert residual_is_material(b) is False
            assert residual_breaks_reconciliation(b) is False


def _series_dict(**kw):
    """A serialised margin-bridge row exactly as `margin_bridge_series` carries it
    into the report renderer (which reconstructs each via `type("B", (), d)()`)."""
    d = dict(year_from=2020, year_to=2021, net_delta_gbp=0.0,
             gross_delta_gbp=0.0, bad_debt_delta_gbp=0.0, capital_delta_gbp=0.0,
             policy_cost_delta_gbp=0.0, network_cost_delta_gbp=0.0,
             residual_gbp=0.0, portfolio_change=0, direction="FLAT")
    d.update(kw)
    return d


def _driver_cell(rendered: str) -> str:
    """Extract the Driver-column cell of the single 2020->2021 data row from the
    rendered Net Margin Bridge section. Asserting on the ROW (not a substring of
    the whole section) is essential: the static explanatory note below the table
    itself contains the words 'unreconciled' and 'other (unexplained)', so a bare
    `'unreconciled' in rendered` would be true even for a perfectly reconciled
    bridge (verified: it is)."""
    for line in rendered.splitlines():
        # A data row: starts with the year label, ends with the RAG cell. The
        # note/header lines never start "| 2020".
        if line.startswith("| 2020→") or line.startswith("| 2020-"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            # ... | Driver | RAG |  -> Driver is the penultimate cell.
            return cells[-2]
    raise AssertionError(f"no data row found in:\n{rendered}")


class TestNetMarginBridgeRendersReconciliationBreak:
    """R11 no-orphan / R15 fail-silent guard on the CONSUMER layer. The control
    primitives above are unit-tested, but the release effect the atom's harden
    notes claim -- the report actually RENDERING a 'RECONCILIATION BREAK' banner
    and a per-row 'unreconciled' tag -- had no regression test. A refactor could
    drop the banner/tag branch in _section_net_margin_bridge while every control
    unit test stayed green and the visible warning silently vanished. These tests
    fail if that render effect regresses (mutation-proven)."""

    def _render(self, *rows):
        # Imported lazily: annual_report pulls a heavy dependency graph.
        from saas.reporting.annual_report import _section_net_margin_bridge
        return _section_net_margin_bridge({"margin_bridge_series": list(rows)})

    def test_clean_bridge_renders_no_break_banner_or_tag(self):
        clean = _series_dict(net_delta_gbp=100_000, gross_delta_gbp=100_000,
                             residual_gbp=0.0, direction="IMPROVEMENT")
        out = self._render(clean)
        assert "RECONCILIATION BREAK" not in out          # no banner
        assert "⚠ unreconciled" not in _driver_cell(out)   # no per-row tag
        assert _driver_cell(out) == "gross margin"

    def test_masked_break_renders_banner_and_per_row_tag(self):
        # The FAIL-OPEN case: a -£500k dropped cost line masked by a larger +£600k
        # legitimate gross swing. dominant_driver still names 'gross margin' (the
        # residual does not dominate), so the ONLY way the break becomes visible is
        # the reconciliation banner + the per-row 'unreconciled' tag.
        masked = _series_dict(net_delta_gbp=100_000, gross_delta_gbp=600_000,
                              residual_gbp=-500_000)
        out = self._render(masked)
        assert "RECONCILIATION BREAK" in out              # banner rendered
        assert _driver_cell(out) == "gross margin ⚠ unreconciled"

    def test_dominant_residual_renders_banner_and_unexplained_driver(self):
        # Residual dominates every named driver -> Driver reads 'other
        # (unexplained)' (no separate tag needed) AND the banner still fires.
        dom = _series_dict(net_delta_gbp=501_000, gross_delta_gbp=1_000,
                           residual_gbp=500_000)
        out = self._render(dom)
        assert "RECONCILIATION BREAK" in out
        assert _driver_cell(out) == "other (unexplained)"
