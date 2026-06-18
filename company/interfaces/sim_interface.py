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

from typing import Any


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

    def get_forward_price(self, fuel: str, delivery_date: str) -> float:
        """What is the forward price for this fuel on the delivery date?

        fuel: 'electricity' or 'gas'
        delivery_date: ISO date string
        Returns: forward price in £/MWh
        """
        raise NotImplementedError

    def get_customer_status(self, account_id: str) -> str:
        """Is this customer still on supply?

        Returns: 'active', 'churned', or 'unknown'
        """
        raise NotImplementedError

    def notify_churn(self, account_id: str, event_date: str) -> None:
        """Notify that a customer has left supply.

        account_id: customer identifier
        event_date: ISO date string of the churn event
        """
        raise NotImplementedError

    def notify_acquisition(self, account_id: str, event_date: str) -> None:
        """Notify that a new customer has been activated.

        account_id: customer identifier
        event_date: ISO date string of the activation
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
        self._customer_statuses: dict[str, str] = {}

    def get_settlement_data(self, mpan: str, period: str) -> dict[str, Any]:
        return {
            "mpan": mpan,
            "period": period,
            "consumption_kwh": 0.0,
            "unit_rate_gbp_per_mwh": 0.0,
            "_stub": True,
        }

    def get_forward_price(self, fuel: str, delivery_date: str) -> float:
        defaults = {"electricity": 120.0, "gas": 50.0}
        return defaults.get(fuel, 100.0)

    def get_customer_status(self, account_id: str) -> str:
        return self._customer_statuses.get(account_id, "active")

    def notify_churn(self, account_id: str, event_date: str) -> None:
        self._churn_notifications.append({"account_id": account_id, "event_date": event_date})
        self._customer_statuses[account_id] = "churned"

    def notify_acquisition(self, account_id: str, event_date: str) -> None:
        self._acquisition_notifications.append({"account_id": account_id, "event_date": event_date})
        self._customer_statuses[account_id] = "active"

    @property
    def churn_notifications(self) -> list[dict]:
        return list(self._churn_notifications)

    @property
    def acquisition_notifications(self) -> list[dict]:
        return list(self._acquisition_notifications)


def build_sim_interface(live: bool = False) -> SimInterface:
    """Factory function. Returns StubSimInterface until functional separation is built."""
    if live:
        raise NotImplementedError(
            "Live SimInterface not implemented yet — functional SIM/company separation "
            "is a later-phase deliverable. Use StubSimInterface for now."
        )
    return StubSimInterface()
