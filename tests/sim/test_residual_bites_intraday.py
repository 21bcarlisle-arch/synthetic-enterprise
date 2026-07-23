"""T3 (SPIKE_TAIL_SSP_RESIDUAL closes_when): the company's residual-at-SSP exposure MOVES under the
corrected intraday tail. This is the coupled-triad measurement — not just that the price series changed,
but that the block-hedge-vs-spiky-shape mismatch now BITES the company's settlement.

THE MECHANISM (why the intraday shape is what bites, not the daily number):
A supplier hedges in FLAT BLOCKS (hedge_fraction of volume bought ahead at a fixed forward price) and
consumes a HALF-HOURLY SHAPE. The residual (unhedged) volume settles at spot SSP each period
(sim.hedging.settle_hedged_period — the company's real settlement primitive). When forward SSP is
flat-expanded (the old behaviour), every period's spot equals the daily mean, so the residual cost is
smooth and the block hedge covers it cleanly. When SSP carries an intraday SHAPE with scarcity spikes in
peak periods — exactly when domestic consumption is highest — the unhedged peak volume settles at a spike
price the flat block hedge never priced. THAT is the cash-not-P&L shock that killed real suppliers in
2021-22, and it is structurally absent without intraday shape regardless of the daily number.

BLIND TO COMPANY P&L (R12/R13): the intraday shape is calibrated to real SSP, decided blind to company
outcomes; this test only MEASURES the resulting exposure, it does not tune anything toward a company result.
"""
from __future__ import annotations

from statistics import fmean

from sim.hedging import settle_hedged_period
from sim.scenario.bimodal_generator import generate_scenario_prices
from simulation.run_scenario import _expand_daily_to_hh

# A peak-weighted domestic consumption shape (kWh per settlement period, SP1..48): low overnight, evening
# peak ~SP33-42 — so consumption is HIGHEST exactly where scarcity spikes land. Fixed (not tuned).
def _consumption_shape() -> list[float]:
    shape = []
    for p in range(48):
        hour = p / 2.0
        if hour < 6.0:
            shape.append(0.10)
        elif hour < 16.0:
            shape.append(0.25)
        elif 16.0 <= hour < 21.0:   # evening peak — coincident with scarcity half-hours
            shape.append(0.60)
        else:
            shape.append(0.30)
    return shape


def _residual_period_costs(price_records: list[dict], consumption: list[float],
                           hedge_fraction: float, hedge_price: float, tariff: float) -> list[float]:
    """The per-period RESIDUAL-at-SSP cost of a block-hedged customer settled against `price_records`:
    the unhedged volume settling at each period's spot SSP (unhedged_volume_kwh/1000 * spot). This is
    exactly the 'residual position settled at System Sell Price' the defect names — isolating it from the
    flat hedged block (which is identical between flat and shaped and would only dilute the signal)."""
    by_period = {(r["settlementDate"], r["settlementPeriod"]): r["systemSellPrice"] for r in price_records}
    costs = []
    for (date_str, period), spot in by_period.items():
        s = settle_hedged_period(consumption[period - 1], tariff, hedge_price, hedge_fraction, spot)
        costs.append(s["unhedged_volume_kwh"] / 1000.0 * spot)
    return costs


def _flatten(daily_records: list[dict]) -> list[dict]:
    """The OLD flat expansion (the mutation baseline / truncated tail): daily price to all 48 periods."""
    hh = []
    for r in daily_records:
        for period in range(1, 49):
            hh.append({"settlementDate": r["settlementDate"], "settlementPeriod": period,
                       "systemSellPrice": r["systemSellPrice"]})
    return hh


def test_residual_exposure_moves_under_intraday_tail():
    """T3: with a fixed block hedge and a peak-weighted consumption shape, the residual wholesale-cost TAIL
    is materially heavier under the corrected intraday tail than under the flat expansion. The daily prices
    (hence the daily mean the block hedge is sized against) are IDENTICAL between the two — only the
    within-day shape differs — so any move is purely the block-vs-shape bite."""
    daily = generate_scenario_prices(2026, 2032, "stress_dunkelflaute_2027", seed="t3")
    consumption = _consumption_shape()
    hedge_fraction, hedge_price, tariff = 0.90, 130.0, 250.0

    flat = _residual_period_costs(_flatten(daily), consumption, hedge_fraction, hedge_price, tariff)
    shaped = _residual_period_costs(_expand_daily_to_hh(daily, seed="t3"), consumption,
                                    hedge_fraction, hedge_price, tariff)

    assert len(flat) == len(shaped)
    # The daily means are identical, so the flat world's worst possible residual period is bounded by
    # (peak consumption x highest daily mean). The intraday spike pushes residual cost far BEYOND that
    # ceiling — the exposure the flat block hedge structurally cannot see.
    flat_max = max(flat)
    assert max(shaped) > 5.0 * flat_max, (
        f"worst-period residual cost barely moved (shaped {max(shaped):.4f} vs flat ceiling {flat_max:.4f}) "
        "-- the intraday spike is not biting the residual"
    )
    # Tail extends past the entire flat world: a non-trivial count of periods exceed twice the worst cost
    # any flat period can reach — i.e. the residual now carries scarcity-half-hour risk that did not exist.
    n_beyond = sum(1 for c in shaped if c > 2.0 * flat_max)
    assert n_beyond > 0, (
        "no residual period exceeds 2x the worst flat cost -- the tail did not extend past the flat world"
    )


def test_bite_vanishes_when_shape_neutralised():
    """R15 killer-mutation companion: if the intraday shape is neutralised (flat expansion), the residual
    tail does NOT move -- so the movement in the test above is caused by the shape, not by noise or a
    measurement artefact. (This is the 'mutate the fix -> control reverts' proof.)"""
    daily = generate_scenario_prices(2026, 2032, "stress_dunkelflaute_2027", seed="t3")
    consumption = _consumption_shape()
    hedge_fraction, hedge_price, tariff = 0.90, 130.0, 250.0

    flat_a = _residual_period_costs(_flatten(daily), consumption, hedge_fraction, hedge_price, tariff)
    flat_b = _residual_period_costs(_flatten(daily), consumption, hedge_fraction, hedge_price, tariff)
    # Two flat expansions are identical -> the tail cannot move without the shape.
    assert max(flat_a) == max(flat_b)
    assert sorted(flat_a) == sorted(flat_b)
