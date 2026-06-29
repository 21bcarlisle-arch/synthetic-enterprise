"""EV ToU Rate Card Optimiser -- Phase Y.

Given Phase X decision (whether to launch ToU), designs the optimal rate
structure for an EV ToU tariff. Evaluates candidate rate cards against:
  - Margin retained by supplier
  - Customer saving vs flat rate
  - Acceptable margin loss threshold

Builds on Phase P (overnight shape), Phase T (profitability), Phase X (decision).
All inputs company-observable. Epistemic-compliant.

Real-world analogue: Octopus Go tariff design. Overnight rate must be low enough
that EV customers gain vs flat, but supplier must retain margin from overnight
wholesale savings minus product discount.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from company.pricing.tou_tariff_assessor import (
    DemandShapeClass,
    ToURateStructure,
    ToUTariffAssessorBook,
    WholesaleBandRates,
)


@dataclass(frozen=True)
class ToURateCandidate:
    """A candidate ToU rate structure (p/kWh for each band)."""
    overnight_p_per_kwh: float
    standard_p_per_kwh: float
    peak_p_per_kwh: float

    def __post_init__(self) -> None:
        if self.overnight_p_per_kwh <= 0 or self.standard_p_per_kwh <= 0 or self.peak_p_per_kwh <= 0:
            raise ValueError("All rate bands must be positive")
        if not (self.overnight_p_per_kwh < self.standard_p_per_kwh < self.peak_p_per_kwh):
            raise ValueError("Rate bands must be ordered: overnight < standard < peak")

    def to_tou_rate_structure(self) -> ToURateStructure:
        return ToURateStructure(
            overnight_p_per_kwh=self.overnight_p_per_kwh,
            standard_p_per_kwh=self.standard_p_per_kwh,
            peak_p_per_kwh=self.peak_p_per_kwh,
        )

    @classmethod
    def octopus_go_style(cls) -> "ToURateCandidate":
        """Octopus Go-inspired EV tariff (7.5p/28.5p/45p)."""
        return cls(7.5, 28.5, 45.0)

    @classmethod
    def aggressive_ev(cls) -> "ToURateCandidate":
        """Aggressive overnight discount to attract EV customers (5p/26p/42p)."""
        return cls(5.0, 26.0, 42.0)

    @classmethod
    def conservative_ev(cls) -> "ToURateCandidate":
        """Conservative overnight discount, protecting margin (10p/30p/48p)."""
        return cls(10.0, 30.0, 48.0)


@dataclass(frozen=True)
class RateCardEvaluation:
    """Evaluation of one ToU rate candidate against EV customer economics."""
    candidate: ToURateCandidate
    flat_rate_p_per_kwh: float
    annual_kwh: float
    year: int
    supplier_margin_tou_gbp: float
    supplier_margin_flat_gbp: float
    customer_saving_gbp: float
    margin_loss_pct: float
    is_viable: bool

    @property
    def margin_delta_gbp(self) -> float:
        return round(self.supplier_margin_tou_gbp - self.supplier_margin_flat_gbp, 2)

    @property
    def is_margin_positive(self) -> bool:
        return self.supplier_margin_tou_gbp > 0

    @property
    def is_customer_positive(self) -> bool:
        return self.customer_saving_gbp > 0

    @property
    def viability_reason(self) -> str:
        if not self.is_customer_positive:
            return "no_customer_saving"
        if not self.is_margin_positive:
            return "negative_supplier_margin"
        if not self.is_viable:
            return "margin_loss_exceeds_threshold"
        return "viable"


class ToURateCardOptimiser:
    """Generates and evaluates candidate ToU rate cards for an EV tariff.

    Usage::
        optimiser = ToURateCardOptimiser()
        optimiser.evaluate(
            candidate=ToURateCandidate.octopus_go_style(),
            flat_rate_p_per_kwh=28.5,
            annual_kwh=8000,
            year=2024,
            wholesale_band_rates=WholesaleBandRates.normal(),
        )
        best = optimiser.optimal_rate()
    """

    def __init__(self) -> None:
        self._evaluations: list[RateCardEvaluation] = []

    def evaluate(
        self,
        candidate: ToURateCandidate,
        flat_rate_p_per_kwh: float,
        annual_kwh: float,
        year: int,
        wholesale_band_rates: WholesaleBandRates,
        max_margin_loss_pct: float = 20.0,
    ) -> RateCardEvaluation:
        """Evaluate one rate card candidate.

        max_margin_loss_pct: acceptable margin loss vs flat rate as a percentage
            of flat-rate margin. E.g. 20 = up to 20% margin reduction is viable.
        """
        book = ToUTariffAssessorBook()
        flat_cmp = book.assess(
            account_id="optimiser_ref",
            year=year,
            annual_kwh=annual_kwh,
            shape_class=DemandShapeClass.OVERNIGHT_HEAVY,
            flat_rate_p_per_kwh=flat_rate_p_per_kwh,
            wholesale_band_rates=wholesale_band_rates,
            tou_rates=candidate.to_tou_rate_structure(),
        )

        supplier_margin_flat = flat_cmp.flat_margin_gbp
        supplier_margin_tou = flat_cmp.tou_margin_gbp
        customer_saving = flat_cmp.customer_saving_gbp

        margin_loss_pct = 0.0
        if supplier_margin_flat > 0:
            margin_loss_pct = max(0.0, (supplier_margin_flat - supplier_margin_tou) / supplier_margin_flat * 100)

        is_viable = (
            customer_saving > 0
            and supplier_margin_tou > 0
            and margin_loss_pct <= max_margin_loss_pct
        )

        evaluation = RateCardEvaluation(
            candidate=candidate,
            flat_rate_p_per_kwh=flat_rate_p_per_kwh,
            annual_kwh=annual_kwh,
            year=year,
            supplier_margin_tou_gbp=round(supplier_margin_tou, 2),
            supplier_margin_flat_gbp=round(supplier_margin_flat, 2),
            customer_saving_gbp=round(customer_saving, 2),
            margin_loss_pct=round(margin_loss_pct, 2),
            is_viable=is_viable,
        )
        self._evaluations.append(evaluation)
        return evaluation

    @property
    def all_evaluations(self) -> list[RateCardEvaluation]:
        return list(self._evaluations)

    def viable_rates(self) -> list[RateCardEvaluation]:
        return [e for e in self._evaluations if e.is_viable]

    def optimal_rate(self) -> Optional[RateCardEvaluation]:
        """Viable rate with highest supplier margin."""
        viable = self.viable_rates()
        if not viable:
            return None
        return max(viable, key=lambda e: e.supplier_margin_tou_gbp)

    def best_customer_rate(self) -> Optional[RateCardEvaluation]:
        """Viable rate with greatest customer saving."""
        viable = self.viable_rates()
        if not viable:
            return None
        return max(viable, key=lambda e: e.customer_saving_gbp)

    def optimiser_summary(self) -> dict:
        viable = self.viable_rates()
        optimal = self.optimal_rate()
        return {
            "candidates_evaluated": len(self._evaluations),
            "viable_count": len(viable),
            "optimal_overnight_p": optimal.candidate.overnight_p_per_kwh if optimal else None,
            "optimal_margin_gbp": optimal.supplier_margin_tou_gbp if optimal else None,
            "optimal_customer_saving_gbp": optimal.customer_saving_gbp if optimal else None,
        }
