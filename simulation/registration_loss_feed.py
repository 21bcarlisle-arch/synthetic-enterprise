"""The world's registration services, as a losing supplier hears them.

When a household leaves this supplier, every supply point it held is registered
by someone else, and the registration service tells the loser -- one notice per
supply point, in the shape `interface/contracts/registration_loss_seam.py`
declares, handed over framed and on the wire exactly as the payment bureau's
ADDACS advices are (`simulation/payment_seam_adapter.py`). This module is the
producer of that stream and nothing more: it does not decide WHETHER or WHEN a
household leaves (that is the departure roll in `simulation/customer_events.py`).

The caller hands this module a household's supply points and a date, never the
departure event, so no field of the event is reachable from here; the belt below
refuses one anyway, because a payload field added tomorrow would not be.

THE COUNTERPARTY MAY NOT IMPORT `company.*`, so the wire form is built here from
the published contract rather than through the company's codec -- the same rule
`simulation/conversation_response.py` follows.
"""
from __future__ import annotations

import dataclasses
import datetime as dt
from typing import Mapping, Sequence

from interface.contracts.registration_loss_seam import (
    CSS_SENDER,
    ELECTRICITY,
    FORBIDDEN_TRUTH_FIELDS,
    GAS,
    PRE_CSS_ELECTRICITY_SENDER,
    PRE_CSS_GAS_SENDER,
    SCHEMA_VERSION,
    RegistrationLossNotice,
    loss_notice_observed_at,
    loss_notice_sender,
    loss_notice_type,
)
from simulation.household import household_of

# Stand-in participants' synthetic credentials: world state, not configuration, with no
# real-world counterparty and no route to one. The company holds only sha256 of each
# (`company/interfaces/wall_protocol.py::COUNTERPARTY_REGISTRY`).
CSS_PROVIDER_CREDENTIAL = "css-provider-01::participant-credential::v1"
MPAS_CREDENTIAL = "mpas-01::participant-credential::v1"
UK_LINK_CREDENTIAL = "uk-link-01::participant-credential::v1"
PARTICIPANT_CREDENTIALS: Mapping[str, str] = {
    CSS_SENDER: CSS_PROVIDER_CREDENTIAL,
    PRE_CSS_ELECTRICITY_SENDER: MPAS_CREDENTIAL,
    PRE_CSS_GAS_SENDER: UK_LINK_CREDENTIAL,
}


def supply_points_on_supply(
    household: str,
    as_of: str,
    electricity_schedules: Mapping[str, Sequence[Mapping]],
    gas_schedules: Mapping[str, Sequence[Mapping]],
) -> list[tuple[str, str]]:
    """(supply point, fuel) for each of the household's points whose supply had begun by `as_of`.

    A point whose first term starts later was never registered to this supplier on the day the
    household left, so no loss can be notified for it.
    """
    held = []
    for fuel, by_point in ((ELECTRICITY, electricity_schedules), (GAS, gas_schedules)):
        for point, terms in by_point.items():
            if household_of(point) == household and any(
                t["acquisition_date"] <= as_of for t in terms
            ):
                held.append((point, fuel))
    return sorted(held)


def _encode_payload(notice: RegistrationLossNotice) -> dict:
    """The notice's wire form, refusing any field the contract forbids to cross."""
    body = {f.name: getattr(notice, f.name) for f in dataclasses.fields(notice)}
    leaking = sorted(set(body) & set(FORBIDDEN_TRUTH_FIELDS))
    if leaking:
        raise ValueError(f"registration-loss notice would carry world truth: {leaking}")
    body["supply_effective_from_date"] = notice.supply_effective_from_date.isoformat()
    return body


class RegistrationLossFeed:
    """One run's registration-loss streams: a gap-free sequence per sender."""

    def __init__(self) -> None:
        self._next_sequence: dict[str, int] = {}

    def wire_notices_for_departure(
        self, supply_points: Sequence[tuple[str, str]], supply_effective_from: str,
    ) -> list[dict]:
        """One framed wire message per (supply point, fuel), handed over when observed."""
        sefd = dt.date.fromisoformat(supply_effective_from)
        observed_at = loss_notice_observed_at(sefd)
        out = []
        for point, fuel in supply_points:
            sender = loss_notice_sender(sefd, fuel)
            sequence = self._next_sequence.get(sender, 0)
            self._next_sequence[sender] = sequence + 1
            notice = RegistrationLossNotice(
                registration_ref=f"{point}@{sefd.isoformat()}",
                supply_point_id=point,
                supply_effective_from_date=sefd,
            )
            envelope = {
                "notification_id": f"{sender}-{sequence}",
                "notification_type": loss_notice_type(sefd),
                "schema_version": SCHEMA_VERSION,
                "sender": sender,
                "sequence": sequence,
                "observed_at": observed_at.isoformat(),
                "valid_time": sefd.isoformat(),
                "payload": _encode_payload(notice),
            }
            out.append({
                "sender": sender,
                "credential": PARTICIPANT_CREDENTIALS[sender],
                "handed_over_at": observed_at.isoformat(),
                "envelope": envelope,
            })
        return out
