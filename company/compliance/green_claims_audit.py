"""Green tariff REGO compliance audit.

UK Fuel Mix Disclosure Regulations 2005 require suppliers to hold REGOs equal
to the renewable electricity they claim to supply. Ofgem can void green claims
and impose penalties when coverage falls short.

This module bridges TariffCatalogue (Phase 142) and RegoPortfolio (Phase 139):
  1. compute_obligation() sums REGO requirements across all green product usage
  2. audit() compares obligation against the portfolio and returns a status

The company cannot see which SIM customers hold which tariffs. It uses its own
billing data -- total kWh billed per product code -- to compute obligation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from company.billing.tariff_products import TariffCatalogue
from company.market.rego_portfolio import RegoPortfolio


# Ofgem enforcement: green mis-selling penalty estimate per MWh shortfall.
# Based on typical enforcement orders (back-billing + carbon offset costs).
_OFGEM_PENALTY_PER_MWH: float = 50.0


@dataclass
class GreenClaimsAuditResult:
    year: int
    obligation_mwh: float           # REGOs the company must hold for green claims
    rego_held_mwh: float            # available + retired in this scheme year
    coverage_pct: float             # 100 * held / obligation (capped at 100 if >100)
    # NOT_APPLICABLE (R15 KL-7 fix): no REGO obligation was computed because no
    # green claim was made -- distinct from COMPLIANT ("claims made and backed").
    status: Literal["COMPLIANT", "AT_RISK", "NON_COMPLIANT", "NOT_APPLICABLE"]
    shortfall_mwh: float            # max(0, obligation - held)
    green_products_active: int      # distinct active green product codes with consumption
    penalty_estimate_gbp: float     # rough enforcement cost if non-compliant


class GreenClaimsAuditor:
    """Audits the company's REGO coverage against its green marketing claims.

    Args:
        rego_portfolio: live RegoPortfolio instance
    """

    _COMPLIANT_THRESHOLD = 100.0
    _AT_RISK_THRESHOLD = 90.0

    def __init__(self, rego_portfolio: RegoPortfolio) -> None:
        self._portfolio = rego_portfolio

    def compute_obligation(
        self,
        product_consumption_kwh: dict[str, float],
        date_str: str,
    ) -> tuple[float, int]:
        """Compute total REGO obligation and count of active green products with usage.

        Args:
            product_consumption_kwh: {product_code: total_kwh_billed_this_year}
            date_str: audit date (YYYY-MM-DD) -- determines active green products

        Returns:
            (obligation_mwh, green_product_count)
        """
        obligation = 0.0
        active_green_codes = {
            p.code for p in TariffCatalogue.green_products(date_str)
        }
        green_in_use: set[str] = set()
        for code, kwh in product_consumption_kwh.items():
            if code in active_green_codes and kwh > 0:
                green_in_use.add(code)
                obligation += TariffCatalogue.rego_requirement_mwh(kwh, code)
        return round(obligation, 4), len(green_in_use)

    def audit(
        self,
        year: int,
        product_consumption_kwh: dict[str, float],
        date_str: str | None = None,
    ) -> GreenClaimsAuditResult:
        """Run a REGO compliance audit for the given scheme year.

        Args:
            year: REGO scheme year (April-March; typically == calendar year)
            product_consumption_kwh: {product_code: total_kwh_billed_this_year}
            date_str: date string for active-product filter; defaults to "{year}-12-31"
        """
        if date_str is None:
            date_str = f"{year}-12-31"

        obligation_mwh, green_count = self.compute_obligation(
            product_consumption_kwh, date_str
        )

        held_mwh = self.portfolio_held_mwh(year)

        shortfall_mwh = round(max(0.0, obligation_mwh - held_mwh), 4)

        # R15 (KL-7 fix, 2026-07-13): a zero obligation used to short-circuit to
        # 100% COMPLIANT -- a FAIL-OPEN. Two distinct zero-obligation cases:
        #   (a) no green product was in use (green_count == 0): a genuine
        #       "no green claims made" -> NOT_APPLICABLE, NOT COMPLIANT. Absence
        #       of a claim is not evidence the claim is backed.
        #   (b) a green product WAS in use (green_count > 0) yet the obligation
        #       still computed to zero: the obligation/detection path is broken
        #       (green tariffs selling but nothing required). Fail CLOSED ->
        #       NON_COMPLIANT so a broken detector can never read compliant.
        if obligation_mwh == 0.0:
            coverage_pct = 0.0
            if green_count > 0:
                status = "NON_COMPLIANT"
            else:
                status = "NOT_APPLICABLE"
        else:
            coverage_pct = round(min(100.0, 100.0 * held_mwh / obligation_mwh), 2)
            if coverage_pct >= self._COMPLIANT_THRESHOLD:
                status = "COMPLIANT"
            elif coverage_pct >= self._AT_RISK_THRESHOLD:
                status = "AT_RISK"
            else:
                status = "NON_COMPLIANT"

        penalty_gbp = (
            round(shortfall_mwh * _OFGEM_PENALTY_PER_MWH, 2)
            if status in ("AT_RISK", "NON_COMPLIANT")
            else 0.0
        )

        return GreenClaimsAuditResult(
            year=year,
            obligation_mwh=obligation_mwh,
            rego_held_mwh=round(held_mwh, 4),
            coverage_pct=coverage_pct,
            status=status,
            shortfall_mwh=shortfall_mwh,
            green_products_active=green_count,
            penalty_estimate_gbp=penalty_gbp,
        )

    def portfolio_held_mwh(self, year: int) -> float:
        """Total REGOs held (available + already retired) for a scheme year."""
        return self._portfolio.available_mwh(year) + self._portfolio.retired_mwh(year)

    def summary_lines(self, result: GreenClaimsAuditResult) -> list[str]:
        """Human-readable summary for annual report inclusion."""
        lines = [
            f"Green claims audit {result.year}: {result.status}",
            f"  REGO obligation: {result.obligation_mwh:.1f} MWh "
            f"({result.green_products_active} green product(s))",
            f"  REGO held:       {result.rego_held_mwh:.1f} MWh "
            f"({result.coverage_pct:.1f}% coverage)",
        ]
        if result.shortfall_mwh > 0:
            lines.append(
                f"  Shortfall:       {result.shortfall_mwh:.1f} MWh "
                f"(penalty estimate \xa3{result.penalty_estimate_gbp:,.0f})"
            )
        return lines
