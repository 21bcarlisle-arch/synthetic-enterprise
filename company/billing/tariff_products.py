"""Green tariff product catalogue.

UK energy suppliers maintain a named product catalogue used on comparison sites and renewal
packs. Green products require REGO backing before making "100% renewable" marketing claims
(Fuel Mix Disclosure Regulations 2005). This module defines products and computes REGO
obligations from observable data only.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TariffProduct:
    """A named tariff product available to customers."""
    code: str                       # e.g. "GREEN_FIX_1YR"
    name: str                       # e.g. "Green Fix 1 Year"
    commodity: str                  # "electricity" | "gas" | "dual"
    segment: str                    # "resi" | "sme" | "ic" | "all"
    term: str                       # "fixed_1yr" | "fixed_2yr" | "variable"
    is_green: bool                  # makes 100% renewable claim
    rego_required_pct: float        # fraction of supply needing REGO (0.0–1.0)
    unit_rate_premium_pct: float    # premium above base renewal rate (e.g. 0.02 = +2%)
    launch_date: str                # YYYY-MM-DD; product first available
    withdrawal_date: Optional[str] = None   # None = still active


# Realistic UK tariff product catalogue spanning 2016–2025.
# Premium products demand more REGO coverage; standard products are cost-only.
_PRODUCTS: tuple[TariffProduct, ...] = (
    TariffProduct(
        code="STD_FIX_1YR",
        name="Standard Fix 1 Year",
        commodity="electricity",
        segment="resi",
        term="fixed_1yr",
        is_green=False,
        rego_required_pct=0.0,
        unit_rate_premium_pct=0.0,
        launch_date="2016-01-01",
    ),
    TariffProduct(
        code="STD_FIX_2YR",
        name="Standard Fix 2 Year",
        commodity="electricity",
        segment="resi",
        term="fixed_2yr",
        is_green=False,
        rego_required_pct=0.0,
        unit_rate_premium_pct=0.005,    # +0.5% term-length premium
        launch_date="2016-01-01",
    ),
    TariffProduct(
        code="STD_VAR",
        name="Standard Variable",
        commodity="electricity",
        segment="resi",
        term="variable",
        is_green=False,
        rego_required_pct=0.0,
        unit_rate_premium_pct=0.025,    # SVT premium (no price certainty for customer)
        launch_date="2016-01-01",
    ),
    TariffProduct(
        code="GREEN_FIX_1YR",
        name="Green Fix 1 Year",
        commodity="electricity",
        segment="resi",
        term="fixed_1yr",
        is_green=True,
        rego_required_pct=1.0,          # 100% REGO-backed
        unit_rate_premium_pct=0.015,    # +1.5% green premium
        launch_date="2018-04-01",       # launched after REGO market matured
    ),
    TariffProduct(
        code="GREEN_FIX_2YR",
        name="Green Fix 2 Year",
        commodity="electricity",
        segment="resi",
        term="fixed_2yr",
        is_green=True,
        rego_required_pct=1.0,
        unit_rate_premium_pct=0.02,     # +2.0% (green + term length)
        launch_date="2018-04-01",
    ),
    TariffProduct(
        code="SME_FIXED",
        name="Business Fixed 1 Year",
        commodity="electricity",
        segment="sme",
        term="fixed_1yr",
        is_green=False,
        rego_required_pct=0.0,
        unit_rate_premium_pct=0.0,
        launch_date="2016-01-01",
    ),
    TariffProduct(
        code="SME_GREEN",
        name="Business Green Fix 1 Year",
        commodity="electricity",
        segment="sme",
        term="fixed_1yr",
        is_green=True,
        rego_required_pct=1.0,
        unit_rate_premium_pct=0.012,    # lower premium — SME more price-sensitive
        launch_date="2019-01-01",
    ),
    TariffProduct(
        code="IC_BASELOAD",
        name="I&C Baseload Fixed",
        commodity="electricity",
        segment="ic",
        term="fixed_1yr",
        is_green=False,
        rego_required_pct=0.0,
        unit_rate_premium_pct=0.0,
        launch_date="2016-01-01",
    ),
    TariffProduct(
        code="IC_GREEN_CERT",
        name="I&C Green Certified",
        commodity="electricity",
        segment="ic",
        term="fixed_1yr",
        is_green=True,
        rego_required_pct=0.5,          # 50% REGO — I&C green claims often partial
        unit_rate_premium_pct=0.008,
        launch_date="2020-01-01",
        withdrawal_date="2023-12-31",   # withdrawn as REGO prices spiked post-crisis
    ),
)


class TariffCatalogue:
    """Read-only access to the company's tariff product catalogue."""

    @staticmethod
    def active_products(date_str: str | None = None) -> list[TariffProduct]:
        """Products available on or after date_str (YYYY-MM-DD). None = all non-withdrawn."""
        result = []
        for p in _PRODUCTS:
            if date_str is not None:
                if p.launch_date > date_str:
                    continue
                if p.withdrawal_date is not None and p.withdrawal_date < date_str:
                    continue
            else:
                if p.withdrawal_date is not None:
                    continue
            result.append(p)
        return result

    @staticmethod
    def products_for_segment(segment: str, date_str: str | None = None) -> list[TariffProduct]:
        """Active products for a given segment ("resi" | "sme" | "ic").
        Products with segment="all" are always included.
        """
        return [
            p for p in TariffCatalogue.active_products(date_str)
            if p.segment == segment or p.segment == "all"
        ]

    @staticmethod
    def green_products(date_str: str | None = None) -> list[TariffProduct]:
        """Active products that make a 100% renewable / green claim."""
        return [p for p in TariffCatalogue.active_products(date_str) if p.is_green]

    @staticmethod
    def get_by_code(code: str) -> TariffProduct | None:
        """Look up a product by its code. Returns None if not found."""
        for p in _PRODUCTS:
            if p.code == code:
                return p
        return None

    @staticmethod
    def rego_requirement_mwh(consumption_kwh: float, product_code: str) -> float:
        """REGOs required (MWh) to back one customer's consumption under this product.

        Returns 0.0 for non-green products. For green products:
            requirement_mwh = consumption_kwh / 1000 * rego_required_pct
        """
        product = TariffCatalogue.get_by_code(product_code)
        if product is None or not product.is_green:
            return 0.0
        return round(consumption_kwh / 1000.0 * product.rego_required_pct, 4)

    @staticmethod
    def summary(date_str: str | None = None) -> dict:
        """Catalogue snapshot: counts by segment and green status."""
        active = TariffCatalogue.active_products(date_str)
        green = [p for p in active if p.is_green]
        by_segment: dict[str, int] = {}
        for p in active:
            by_segment[p.segment] = by_segment.get(p.segment, 0) + 1
        return {
            "active_count": len(active),
            "green_count": len(green),
            "by_segment": by_segment,
        }
