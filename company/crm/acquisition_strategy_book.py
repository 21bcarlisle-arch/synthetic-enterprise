"""Acquisition Strategy Intelligence Book.

Synthesises CAC (by channel), CLV (by segment), and win rate data to produce
acquisition ROI analysis. Answers: which channel/segment combination delivers
best return? What's the minimum CLV to justify acquisition spend?

Company-observable: CAC data from industry benchmarks; CLV from billing history.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


# CAC benchmarks by channel from company/crm/acquisition_cost.py
_TYPICAL_CAC_GBP: dict[str, float] = {
    "pcw": 55.0,      # Price Comparison Website (uSwitch etc)
    "direct": 30.0,   # Own website / advertising
    "broker": 160.0,  # Third Party Intermediary (I&C)
    "referral": 20.0, # Existing customer referral
    "winback": 37.0,  # Former customer returned
}

# Typical expected tenure by segment in years (from CMA 2016; Phase M renewal data)
_TYPICAL_TENURE_YEARS: dict[str, float] = {
    "resi": 3.2,
    "SME": 2.8,
    "I&C": 4.5,
}


@dataclass(frozen=True)
class ChannelROIAnalysis:
    channel: str
    segment: str
    cac_gbp: float
    expected_clv_gbp: float
    payback_months: Optional[float]
    roi_pct: Optional[float]
    is_viable: bool  # CLV > CAC × 3 (standard 3× hurdle)
    recommendation: str

    @property
    def net_value_gbp(self) -> float:
        return round(self.expected_clv_gbp - self.cac_gbp, 2)


@dataclass(frozen=True)
class PortfolioGrowthScenario:
    target_new_customers: int
    channel: str
    segment: str
    total_cac_spend_gbp: float
    expected_total_clv_gbp: float
    net_value_gbp: float
    payback_months: Optional[float]
    win_rate_assumption_pct: float
    required_attempts: int


class AcquisitionStrategyBook:
    """Computes acquisition ROI by channel/segment combination."""

    def __init__(self, win_rate_by_segment: Optional[dict[str, float]] = None) -> None:
        # Default win rates from industry (CMA 2016 / Ofgem switching data)
        self._win_rates = win_rate_by_segment or {
            "resi": 0.20,   # 20% of PCW presentations convert
            "SME": 0.12,    # Slower purchasing cycle
            "I&C": 0.08,    # Competitive tender process
        }

    def analyse_channel(
        self,
        channel: str,
        segment: str,
        expected_annual_margin_gbp: float,
        expected_tenure_years: Optional[float] = None,
        cac_override_gbp: Optional[float] = None,
    ) -> ChannelROIAnalysis:
        """Compute ROI for a given channel/segment combination."""
        cac = cac_override_gbp if cac_override_gbp is not None else _TYPICAL_CAC_GBP.get(channel, 50.0)
        tenure = expected_tenure_years or _TYPICAL_TENURE_YEARS.get(segment, 3.0)
        clv = round(expected_annual_margin_gbp * tenure, 2)
        if expected_annual_margin_gbp <= 0 or clv <= 0:
            return ChannelROIAnalysis(
                channel=channel, segment=segment, cac_gbp=cac,
                expected_clv_gbp=clv, payback_months=None, roi_pct=None,
                is_viable=False, recommendation="AVOID: negative expected margin",
            )
        payback_months = round(cac / (expected_annual_margin_gbp / 12), 1)
        roi_pct = round((clv - cac) / cac * 100, 1) if cac > 0 else None
        is_viable = clv >= cac * 3
        if is_viable:
            if channel == "referral":
                rec = "PRIORITISE: best ROI with lowest CAC"
            elif payback_months < 6:
                rec = "STRONG: payback <6 months"
            else:
                rec = "VIABLE: positive ROI within tenure"
        elif clv > cac:
            rec = "MARGINAL: positive but below 3× hurdle"
        else:
            rec = "AVOID: CLV below CAC"
        return ChannelROIAnalysis(
            channel=channel, segment=segment, cac_gbp=cac,
            expected_clv_gbp=clv, payback_months=payback_months,
            roi_pct=roi_pct, is_viable=is_viable, recommendation=rec,
        )

    def rank_channels(
        self,
        segment: str,
        expected_annual_margin_gbp: float,
        expected_tenure_years: Optional[float] = None,
    ) -> list[ChannelROIAnalysis]:
        """Rank all acquisition channels by ROI for a given segment."""
        results = []
        for channel in _TYPICAL_CAC_GBP:
            r = self.analyse_channel(
                channel=channel, segment=segment,
                expected_annual_margin_gbp=expected_annual_margin_gbp,
                expected_tenure_years=expected_tenure_years,
            )
            results.append(r)
        return sorted(results, key=lambda x: (x.roi_pct or -999), reverse=True)

    def model_growth_scenario(
        self,
        target_new_customers: int,
        channel: str,
        segment: str,
        expected_annual_margin_gbp: float,
        expected_tenure_years: Optional[float] = None,
        win_rate_override: Optional[float] = None,
    ) -> PortfolioGrowthScenario:
        """Model total spend and expected value for a growth target."""
        win_rate = win_rate_override or self._win_rates.get(segment, 0.15)
        required_attempts = round(target_new_customers / win_rate) if win_rate > 0 else 9999
        cac = _TYPICAL_CAC_GBP.get(channel, 50.0)
        total_cac = round(required_attempts * cac, 2)
        tenure = expected_tenure_years or _TYPICAL_TENURE_YEARS.get(segment, 3.0)
        total_clv = round(target_new_customers * expected_annual_margin_gbp * tenure, 2)
        net_value = round(total_clv - total_cac, 2)
        payback_months = round(cac / (expected_annual_margin_gbp / 12), 1) if expected_annual_margin_gbp > 0 else None
        return PortfolioGrowthScenario(
            target_new_customers=target_new_customers,
            channel=channel, segment=segment,
            total_cac_spend_gbp=total_cac,
            expected_total_clv_gbp=total_clv,
            net_value_gbp=net_value,
            payback_months=payback_months,
            win_rate_assumption_pct=round(win_rate * 100, 1),
            required_attempts=required_attempts,
        )

    def minimum_viable_clv(self, channel: str, hurdle_multiple: float = 3.0) -> float:
        """Minimum CLV needed to justify acquisition on this channel."""
        cac = _TYPICAL_CAC_GBP.get(channel, 50.0)
        return round(cac * hurdle_multiple, 2)

    def strategy_summary(
        self,
        segment: str,
        expected_annual_margin_gbp: float,
    ) -> str:
        ranked = self.rank_channels(segment, expected_annual_margin_gbp)
        viable = [r for r in ranked if r.is_viable]
        best = ranked[0] if ranked else None
        lines = [
            f"Acquisition Strategy Intelligence — {segment} segment",
            f"Expected annual margin: £{expected_annual_margin_gbp:,.0f} | Viable channels: {len(viable)}/{len(ranked)}",
        ]
        if best and best.roi_pct is not None:
            lines.append(f"Best channel: {best.channel} (ROI {best.roi_pct:.0f}%, "
                         f"payback {best.payback_months:.0f} months)")
        for r in ranked[:3]:
            lines.append(f"  {r.channel}: {r.recommendation} (CLV £{r.expected_clv_gbp:,.0f}, CAC £{r.cac_gbp:.0f})")
        return "\n".join(lines)
