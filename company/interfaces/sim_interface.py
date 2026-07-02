"""Company Layer — SIM/Company Interface Seam.

Formal boundary between the simulation and the company layer. The company
layer must only access simulation data through these methods — it cannot
read simulation internals directly.

Phase 8a: stub implementations that return sensible defaults. The point is
to establish the boundary so future company-layer work always goes through
this seam, not to import simulation internals directly.

When the functional separation is built (later phase), these stubs will be
replaced with real implementations that call the simulation layer.
"""

from typing import Any, Optional

from company.crm.churn_model import estimate_churn_probability
from company.crm.enriched_churn_estimate import enriched_churn_estimate
from company.crm.payment_behaviour_analytics import BehaviourScore
from company.pricing.tariff_engine import CompanyTariffEngine


class SimInterface:
    """Formal interface between the company layer and the simulation.

    All methods raise NotImplementedError in the base class. Use
    StubSimInterface for testing and development until functional separation
    is built.
    """

    def get_settlement_data(self, mpan: str, period: str) -> dict[str, Any]:
        """What did this meter consume in the given period?

        mpan: Meter Point Administration Number
        period: ISO date string ('YYYY-MM-DD') or half-hourly period ('YYYY-MM-DD:SP')
        Returns: {mpan, period, consumption_kwh, unit_rate_gbp_per_mwh}
        """
        raise NotImplementedError

    def get_forward_price(self, fuel: str, delivery_date: str, term_months: int = 12) -> float:
        """What is the forward price for this fuel on the delivery date?

        fuel: 'electricity' or 'gas'
        delivery_date: ISO date string
        term_months: contract duration (default 12); longer terms command a term-structure premium
        Returns: forward price in £/MWh
        """
        raise NotImplementedError

    def get_customer_status(self, account_id: str) -> str:
        """Is this customer still on supply?

        Returns: 'active', 'churned', or 'unknown'
        """
        raise NotImplementedError

    def notify_churn(
        self,
        account_id: str,
        event_date: str,
        *,
        reason: str = "non-renewal",
        sim_churn_probability = None,
        company_churn_estimate = None,
    ) -> None:
        """Notify that a customer has left supply.

        account_id: customer identifier
        event_date: ISO date string of the churn event
        reason: human-readable departure reason (default: non-renewal)
        sim_churn_probability: SIM ground-truth churn probability at this renewal
        company_churn_estimate: company observable-data estimate at this renewal
        """
        raise NotImplementedError

    def notify_acquisition(
        self,
        account_id: str,
        event_date: str,
        *,
        channel: str = "market-acquisition",
        predecessor_id = None,
    ) -> None:
        """Notify that a new customer has been activated.

        account_id: customer identifier
        event_date: ISO date string of the activation
        channel: acquisition channel (e.g. home-move-win, market-acquisition)
        predecessor_id: account_id of the account that churned, if applicable
        """
        raise NotImplementedError

    def get_churn_estimate(
        self,
        account_id: str,
        old_rate_gbp_per_mwh: float,
        new_rate_gbp_per_mwh: float,
        tenure_years: float,
        annual_consumption_kwh: float = 0.0,
        *,
        bill_shock_count: int = 0,
        behaviour_score: Optional[BehaviourScore] = None,
        satisfaction_score: Optional[float] = None,
    ) -> float:
        """Company observable-data churn probability estimate for a renewal.

        Combines rate-sensitivity model with payment-behaviour signals (Phase NC).
        Returns max(rate_model, payment_behaviour_model), capped at 0.95.
        All inputs are company observables -- no SIM internals.
        Returns: estimated churn probability in [0.0, 0.95]
        """
        raise NotImplementedError


class StubSimInterface(SimInterface):
    """Stub implementation for testing and development.

    Returns sensible defaults for all interface methods. Tracks notify calls
    so tests can assert on them.
    """

    def __init__(self):
        self._churn_notifications: list[dict] = []
        self._acquisition_notifications: list[dict] = []
        self._retention_notifications: list[dict] = []
        self._customer_statuses: dict[str, str] = {}

    def get_settlement_data(self, mpan: str, period: str) -> dict[str, Any]:
        return {
            "mpan": mpan,
            "period": period,
            "consumption_kwh": 0.0,
            "unit_rate_gbp_per_mwh": 0.0,
            "_stub": True,
        }

    def get_forward_price(self, fuel: str, delivery_date: str, term_months: int = 12) -> float:
        defaults = {"electricity": 120.0, "gas": 50.0}
        return defaults.get(fuel, 100.0)

    def get_customer_status(self, account_id: str) -> str:
        return self._customer_statuses.get(account_id, "active")

    def notify_churn(self, account_id, event_date, *, reason="non-renewal",
                 sim_churn_probability=None, company_churn_estimate=None):
        self._churn_notifications.append({
            "account_id": account_id, "event_date": event_date,
            "reason": reason, "sim_churn_probability": sim_churn_probability,
            "company_churn_estimate": company_churn_estimate,
        })
        self._customer_statuses[account_id] = "churned"

    def notify_acquisition(self, account_id, event_date, *, channel="market-acquisition",
                       predecessor_id=None):
        self._acquisition_notifications.append({
            "account_id": account_id, "event_date": event_date,
            "channel": channel, "predecessor_id": predecessor_id,
        })
        self._customer_statuses[account_id] = "active"


    def get_churn_estimate(
        self,
        account_id: str,
        old_rate_gbp_per_mwh: float,
        new_rate_gbp_per_mwh: float,
        tenure_years: float,
        annual_consumption_kwh: float = 0.0,
        *,
        bill_shock_count: int = 0,
        behaviour_score: Optional[BehaviourScore] = None,
        satisfaction_score: Optional[float] = None,
    ) -> float:
        return enriched_churn_estimate(
            old_rate_gbp_per_mwh, new_rate_gbp_per_mwh, tenure_years, annual_consumption_kwh,
            bill_shock_count=bill_shock_count,
            behaviour_score=behaviour_score,
            satisfaction_score=satisfaction_score,
        )

    def notify_retention_attempt(self, account_id, event_date, company_churn_estimate, discount_pct, outcome='pending'):
        self._retention_notifications.append({
            'account_id': account_id, 'event_date': event_date,
            'company_churn_estimate': company_churn_estimate,
            'discount_pct': discount_pct, 'outcome': outcome,
        })

    @property
    def churn_notifications(self) -> list[dict]:
        return list(self._churn_notifications)

    @property
    def acquisition_notifications(self) -> list[dict]:
        return list(self._acquisition_notifications)

    @property
    def retention_notifications(self) -> list[dict]:
        return list(self._retention_notifications)


class LiveSimInterface(SimInterface):
    """Live SimInterface — company makes all decisions from observable data only.

    Observability audit (Phase 12e) — every value the company receives:

    get_forward_price(fuel, delivery_date, term_months=12)
        OBSERVABLE. Calls CompanyTariffEngine which reads Elexon spot price
        history and NBP TTF proxy — both available to any market participant.
        Uses a 120-day rolling mean + risk premium + term-length premium (Phase 48a).
        No SIM forward curve internals accessed.

    get_settlement_data(mpan, period)
        STUB — returns zeros. In production would be observable (meter reads).

    get_customer_status(account_id)
        STUB — hardcoded "active". In production would be observable (CRM).

    notify_churn(..., sim_churn_probability, company_churn_estimate)
        sim_churn_probability: SIM INTERNAL — passed in for divergence audit
        only. The company stores but does NOT use this value to make decisions.
        company_churn_estimate: OBSERVABLE — derived from rate change % and
        tenure, both known to the company.

    notify_acquisition(..., channel, predecessor_id)
        OBSERVABLE — company records its own customer onboarding events.

    notify_retention_attempt(..., company_churn_estimate, discount_pct)
        OBSERVABLE — company records its own retention decisions.

    get_churn_estimate(account_id, old_rate, new_rate, tenure_years)
        OBSERVABLE — estimate_churn_probability() uses only rate change % and
        customer tenure. No SIM bill-shock model parameters accessed.

    _load_price_records(fuel)
        Uses sim.cache_store / sim.system_prices_history as a data access
        layer for Elexon/NBP data. The UNDERLYING DATA is observable (public
        market data); the access path goes through SIM modules as an
        infrastructure convenience, not for SIM internals.
    """

    def __init__(self):
        from company.crm.event_log import CompanyEventLog
        self._engine = CompanyTariffEngine()
        self._price_cache: dict[str, list[dict]] = {}
        self._event_log = CompanyEventLog()

    @property
    def event_log(self):
        return self._event_log

    def _load_price_records(self, fuel: str) -> list[dict]:
        if fuel not in self._price_cache:
            if fuel == "electricity":
                from sim.cache_store import get_cached_prices
                from sim.system_prices_history import get_system_prices_range
                records = get_cached_prices("2015-11-07", "2025-06-07")
                if records is None:
                    records = get_system_prices_range("2015-11-07", "2025-06-07")
                self._price_cache[fuel] = records
            elif fuel == "gas":
                from sim.gas_prices_history import load_nbp_history
                self._price_cache[fuel] = load_nbp_history()
            else:
                raise ValueError(f"Unknown fuel: {fuel}")
        return self._price_cache[fuel]

    def get_forward_price(self, fuel: str, delivery_date: str, term_months: int = 12) -> float:
        records = self._load_price_records(fuel)
        return self._engine.get_forward_price(fuel, delivery_date, records, term_months=term_months)

    def get_settlement_data(self, mpan: str, period: str) -> dict[str, Any]:
        return {
            "mpan": mpan,
            "period": period,
            "consumption_kwh": 0.0,
            "unit_rate_gbp_per_mwh": 0.0,
            "_stub": True,
        }

    def get_customer_status(self, account_id: str) -> str:
        return "active"

    def notify_churn(self, account_id, event_date, *, reason="non-renewal",
                 sim_churn_probability=None, company_churn_estimate=None):
        from company.crm.event_log import ChurnEvent
        self._event_log.record_churn(ChurnEvent(
            customer_id=account_id,
            event_date=event_date,
            reason=reason,
            sim_churn_probability=sim_churn_probability,
            company_churn_estimate=company_churn_estimate,
        ))

    def notify_acquisition(self, account_id, event_date, *, channel="market-acquisition",
                       predecessor_id=None):
        from company.crm.event_log import AcquisitionEvent
        self._event_log.record_acquisition(AcquisitionEvent(
            customer_id=account_id,
            event_date=event_date,
            channel=channel,
            predecessor_id=predecessor_id,
        ))


    def notify_retention_attempt(self, account_id, event_date, company_churn_estimate, discount_pct, outcome='pending'):
        from company.crm.event_log import RetentionEvent
        self._event_log.record_retention(RetentionEvent(
            customer_id=account_id,
            event_date=event_date,
            company_churn_estimate=company_churn_estimate,
            discount_pct=discount_pct,
            outcome=outcome,
        ))

    def get_churn_estimate(
        self,
        account_id: str,
        old_rate_gbp_per_mwh: float,
        new_rate_gbp_per_mwh: float,
        tenure_years: float,
        annual_consumption_kwh: float = 0.0,
    ) -> float:
        return estimate_churn_probability(old_rate_gbp_per_mwh, new_rate_gbp_per_mwh, tenure_years, annual_consumption_kwh)


def build_sim_interface(live: bool = False) -> SimInterface:
    """Factory function. Returns LiveSimInterface when live=True (Phase 11a+)."""
    if live:
        return LiveSimInterface()
    return StubSimInterface()
