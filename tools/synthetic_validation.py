"""Phase PY: Statistical Equivalence Gate for CorrelatedGeneratorAdapter.

Validates that the bivariate OU synthetic generator reproduces the statistical
properties of 2016-2025 UK energy market data (NBP gas + Elexon SSP electricity).

Ten checks across three categories:
  - Distributional moments: long-run mean, return volatility
  - Cross-commodity structure: elec-gas correlation, crisis regime frequency
  - Time-series structure: mean reversion (ACF), fat tails (excess kurtosis)

Run standalone: python3 -m tools.synthetic_validation
Gate output: docs/market_research/findings/synthetic_equivalence_gate.json
"""
from __future__ import annotations
import datetime, json, math, os
from dataclasses import dataclass, asdict
from typing import List, Optional

HISTORICAL_BENCHMARKS = {
    "gas_long_run_mean_gbp_per_mwh": 54.0,
    "elec_long_run_mean_gbp_per_mwh": 85.0,
    "gas_return_vol_annual_lo": 0.30,
    "gas_return_vol_annual_hi": 0.80,
    "elec_return_vol_annual_lo": 0.35,
    "elec_return_vol_annual_hi": 0.95,
    "elec_gas_corr_lo": 0.55,
    "elec_gas_corr_hi": 0.85,
    "crisis_freq_lo": 0.04,
    "crisis_freq_hi": 0.14,
}

_MEAN_TOLERANCE = 0.20


@dataclass
class EquivalenceCheck:
    name: str
    passed: bool
    value: float
    benchmark: str
    message: str


@dataclass
class EquivalenceGate:
    overall_pass: bool
    checks: List[EquivalenceCheck]
    model_params: dict
    n_steps: int
    timestamp: str


def _pearson_r(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs) / n)
    sy = math.sqrt(sum((y - my) ** 2 for y in ys) / n)
    return cov / (sx * sy) if sx * sy > 0.0 else 0.0


def _lag1_acf(xs):
    n = len(xs)
    if n < 3:
        return 0.0
    mean = sum(xs) / n
    var = sum((x - mean) ** 2 for x in xs) / n
    if var == 0.0:
        return 0.0
    cov1 = sum((xs[i] - mean) * (xs[i - 1] - mean) for i in range(1, n)) / n
    return cov1 / var


def _excess_kurtosis(xs):
    n = len(xs)
    if n < 4:
        return 0.0
    mean = sum(xs) / n
    m2 = sum((x - mean) ** 2 for x in xs) / n
    m4 = sum((x - mean) ** 4 for x in xs) / n
    return (m4 / m2 ** 2 - 3.0) if m2 > 0.0 else 0.0


def _annualised_return_vol(prices):
    if len(prices) < 2:
        return 0.0
    returns = [math.log(prices[i] / prices[i - 1])
               for i in range(1, len(prices))
               if prices[i] > 0 and prices[i - 1] > 0]
    if not returns:
        return 0.0
    mean_r = sum(returns) / len(returns)
    var_r = sum((r - mean_r) ** 2 for r in returns) / len(returns)
    return math.sqrt(var_r * 12.0)


def run_gate(seed=0, n_steps=5000):
    """Run the statistical equivalence gate against CorrelatedGeneratorAdapter."""
    from tools.market_adapters.synthetic_generator import (
        CorrelatedGeneratorAdapter,
        GAS_LONG_RUN_MEAN_GBP_PER_MWH, ELEC_LONG_RUN_MEAN_GBP_PER_MWH,
        GAS_MEAN_REVERSION_SPEED, ELEC_MEAN_REVERSION_SPEED,
        GAS_VOL_NORMAL, ELEC_VOL_NORMAL, ELEC_GAS_CORR, CRISIS_REGIME_PROB,
    )
    adapter = CorrelatedGeneratorAdapter(seed=seed, regime="normal")
    gas_prices, elec_prices = [], []
    crisis_count = 0
    for _ in range(n_steps):
        summary = adapter.get_market_summary()
        gas_prices.append(summary["gas_spot_gbp_per_mwh"])
        elec_prices.append(summary["elec_spot_gbp_per_mwh"])
        if adapter._is_crisis:
            crisis_count += 1

    gas_mean = sum(gas_prices) / n_steps
    elec_mean = sum(elec_prices) / n_steps
    gas_vol = _annualised_return_vol(gas_prices)
    elec_vol = _annualised_return_vol(elec_prices)
    corr = _pearson_r(gas_prices, elec_prices)
    crisis_freq = crisis_count / n_steps

    gas_returns = [math.log(gas_prices[i] / gas_prices[i - 1])
                   for i in range(1, len(gas_prices))
                   if gas_prices[i] > 0 and gas_prices[i - 1] > 0]
    elec_returns = [math.log(elec_prices[i] / elec_prices[i - 1])
                    for i in range(1, len(elec_prices))
                    if elec_prices[i] > 0 and elec_prices[i - 1] > 0]

    gas_acf1 = _lag1_acf(gas_returns)
    elec_acf1 = _lag1_acf(elec_returns)
    gas_kurt = _excess_kurtosis(gas_returns)
    elec_kurt = _excess_kurtosis(elec_returns)

    b = HISTORICAL_BENCHMARKS
    gas_mu_tgt = b["gas_long_run_mean_gbp_per_mwh"]
    elec_mu_tgt = b["elec_long_run_mean_gbp_per_mwh"]
    gas_mean_lo = gas_mu_tgt * (1.0 - _MEAN_TOLERANCE)
    gas_mean_hi = gas_mu_tgt * (1.0 + _MEAN_TOLERANCE)
    elec_mean_lo = elec_mu_tgt * (1.0 - _MEAN_TOLERANCE)
    elec_mean_hi = elec_mu_tgt * (1.0 + _MEAN_TOLERANCE)
    gvlo = b["gas_return_vol_annual_lo"]
    gvhi = b["gas_return_vol_annual_hi"]
    evlo = b["elec_return_vol_annual_lo"]
    evhi = b["elec_return_vol_annual_hi"]
    clo = b["elec_gas_corr_lo"]
    chi = b["elec_gas_corr_hi"]
    cflo = b["crisis_freq_lo"]
    cfhi = b["crisis_freq_hi"]

    checks = [
        EquivalenceCheck(
            name="gas_long_run_mean",
            passed=gas_mean_lo <= gas_mean <= gas_mean_hi,
            value=round(gas_mean, 2),
            benchmark="[%.1f, %.1f] GBP/MWh" % (gas_mean_lo, gas_mean_hi),
            message="gas mean %.2f vs target %.1f +/-20pct" % (gas_mean, gas_mu_tgt),
        ),
        EquivalenceCheck(
            name="elec_long_run_mean",
            passed=elec_mean_lo <= elec_mean <= elec_mean_hi,
            value=round(elec_mean, 2),
            benchmark="[%.1f, %.1f] GBP/MWh" % (elec_mean_lo, elec_mean_hi),
            message="elec mean %.2f vs target %.1f +/-20pct" % (elec_mean, elec_mu_tgt),
        ),
        EquivalenceCheck(
            name="gas_return_vol",
            passed=gvlo <= gas_vol <= gvhi,
            value=round(gas_vol, 4),
            benchmark="[%.2f, %.2f]" % (gvlo, gvhi),
            message="gas annualised vol %.3f (target ~0.35)" % gas_vol,
        ),
        EquivalenceCheck(
            name="elec_return_vol",
            passed=evlo <= elec_vol <= evhi,
            value=round(elec_vol, 4),
            benchmark="[%.2f, %.2f]" % (evlo, evhi),
            message="elec annualised vol %.3f (target ~0.45)" % elec_vol,
        ),
        EquivalenceCheck(
            name="elec_gas_correlation",
            passed=clo <= corr <= chi,
            value=round(corr, 4),
            benchmark="[%.2f, %.2f]" % (clo, chi),
            message="Pearson r %.3f vs target 0.70" % corr,
        ),
        EquivalenceCheck(
            name="crisis_freq",
            passed=cflo <= crisis_freq <= cfhi,
            value=round(crisis_freq, 4),
            benchmark="[%.2f, %.2f]" % (cflo, cfhi),
            message="crisis fraction %.3f vs target %.2f" % (crisis_freq, CRISIS_REGIME_PROB),
        ),
        EquivalenceCheck(
            name="gas_mean_reversion",
            passed=gas_acf1 < 0.0,
            value=round(gas_acf1, 4),
            benchmark="< 0.0",
            message="gas returns lag-1 ACF %.4f" % gas_acf1,
        ),
        EquivalenceCheck(
            name="elec_mean_reversion",
            passed=elec_acf1 < 0.0,
            value=round(elec_acf1, 4),
            benchmark="< 0.0",
            message="elec returns lag-1 ACF %.4f" % elec_acf1,
        ),
        EquivalenceCheck(
            name="gas_fat_tails",
            passed=gas_kurt > 0.0,
            value=round(gas_kurt, 4),
            benchmark="> 0.0",
            message="gas excess kurtosis %.4f" % gas_kurt,
        ),
        EquivalenceCheck(
            name="elec_fat_tails",
            passed=elec_kurt > 0.0,
            value=round(elec_kurt, 4),
            benchmark="> 0.0",
            message="elec excess kurtosis %.4f" % elec_kurt,
        ),
    ]

    return EquivalenceGate(
        overall_pass=all(c.passed for c in checks),
        checks=checks,
        model_params={
            "gas_mu": GAS_LONG_RUN_MEAN_GBP_PER_MWH,
            "elec_mu": ELEC_LONG_RUN_MEAN_GBP_PER_MWH,
            "gas_kappa": GAS_MEAN_REVERSION_SPEED,
            "elec_kappa": ELEC_MEAN_REVERSION_SPEED,
            "gas_vol_normal": GAS_VOL_NORMAL,
            "elec_vol_normal": ELEC_VOL_NORMAL,
            "corr": ELEC_GAS_CORR,
            "crisis_prob": CRISIS_REGIME_PROB,
        },
        n_steps=n_steps,
        timestamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )


def write_gate_json(gate, path=None):
    """Serialise gate to JSON. Returns path used."""
    if path is None:
        path = os.path.join(
            os.path.dirname(__file__),
            "..", "docs", "market_research", "findings",
            "synthetic_equivalence_gate.json",
        )
    with open(path, "w") as fh:
        json.dump(asdict(gate), fh, indent=2)
    return path


if __name__ == "__main__":
    gate = run_gate()
    status = "PASS" if gate.overall_pass else "FAIL"
    print("Synthetic Equivalence Gate: %s  (%d steps, seed=0)" % (status, gate.n_steps))
    for c in gate.checks:
        tick = "OK" if c.passed else "FAIL"
        print("  [%s] %s: %s" % (tick, c.name, c.message))
    out = write_gate_json(gate)
    print("Gate written to: %s" % out)
