"""The priority-services registration seam -- a household telling its supplier it has a
needs-code circumstance.

WHAT CROSSES: a registration notice -- the supply point it concerns (one the supplier holds), the day it was made, and
the needs codes the household named. Nothing else. A real supplier learns of a circumstance
"almost exclusively" by customer disclosure (debt_and_collections.md s.10.5), so the sender is
the household's own disclosure channel.

UNSOLICITED BY CONSTRUCTION. The supplier does not ask each household whether it is vulnerable
and receive an answer; the household tells it, or does not. So the only envelope specialisation
is a `WallNotification`.

THE EPISTEMIC WALL. The world draws two latent states (`simulation/vulnerability_state.py`): the
needs-code kind and the financial kind. Neither crosses. A household that never discloses sends
nothing at all, so the supplier cannot count the households it does not know about; and the
financial kind has no notice in any form -- it is inferred from payments, or not at all.

NO SIM/GENERATOR/COMPANY SYMBOL: pure contract, checked by
`tests/interface/test_psr_registration_seam.py`.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

from interface.contracts.wall_envelope import WallNotification

# 2: the seam's first release, numbered 2 because the wall's dialect 1 has no notification
# (the same reason `registration_loss_seam` gives).
SCHEMA_VERSION = 2

#: The one spelling of the sender and the notification type, for the producer/consumer drift
#: reason `payment_observable_seam` gives.
REGISTRATION_SENDER = "HOUSEHOLD-DISCLOSURE-01"
REGISTRATION_NOTIFICATION_TYPE = "priority_services_registration"


@dataclass(frozen=True)
class PriorityServicesRegistrationNotice:
    """`needs_codes` are the industry needs codes the household named (commons s.1a). An EMPTY
    tuple is a real value, not a missing one: the world draws no code while the code mix is a
    GAP, and the supplier then holds a registration with no category."""

    supply_point_id: str
    registered_on: dt.date
    needs_codes: tuple[int, ...]


PriorityServicesRegistrationWallNotification = WallNotification[PriorityServicesRegistrationNotice]

UNSOLICITED_PAYLOAD_TYPES: tuple[type, ...] = (PriorityServicesRegistrationNotice,)

#: THE CLOSED OBSERVABLE FIELD SET, declared rather than derived: a set computed from the
#: dataclass widens with it and can never catch a widening.
OBSERVABLE_PAYLOAD_FIELDS: dict[str, tuple[str, ...]] = {
    "PriorityServicesRegistrationNotice": ("supply_point_id", "registered_on", "needs_codes"),
}

#: World-side truth that must never ride on a notice -- the latent states' own attribute names.
FORBIDDEN_TRUTH_FIELDS: tuple[str, ...] = (
    "psr_type_vulnerable",
    "financially_vulnerable",
    "discloses_psr",
    "needs_code_unknown_reason",
    "income_stress",
    "household",
)


def registration_observed_at(registered_on: dt.date) -> dt.datetime:
    """When the supplier learns of a registration: the day it is made, because disclosure is a
    conversation with the supplier itself."""
    return dt.datetime.combine(registered_on, dt.time())
