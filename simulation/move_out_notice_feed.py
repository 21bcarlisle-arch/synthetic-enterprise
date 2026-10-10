"""How our household tells us it is moving out: the move-out notice, framed on the wire.

REUSE: simulation/move_out_notice_feed.py
CLASS: CUSTOM
INDEX: searched "move out", "notice", "home move" under simulation/. `registration_loss_feed` frames
       the registration service's notices of a SWITCH (the household keeps its home); a move-out is
       the household's own contact ending a contract on a move (SLC 24.1), which no registration
       flow carries (home_moves.md s.8.1), so it is a separate sender and stream.

WHO SENDS. The household, two Working Days before its move (`latest_notice_date`; the seam says why
that and not another lead time). The world's move is `sim/customer_state_layer.py`'s; this feed is
handed only the supply points and the move date, so nothing else of the move (its destination, the
tenure, the incoming occupant) can ride on the notice.
"""
from __future__ import annotations

import dataclasses
import datetime as dt
from typing import Sequence

from interface.contracts.move_out_notice_seam import (
    FORBIDDEN_TRUTH_FIELDS,
    MOVE_OUT_NOTIFICATION_TYPE,
    MOVE_OUT_SENDER,
    SCHEMA_VERSION,
    MoveOutNotice,
    latest_notice_date,
    notice_observed_at,
)

#: The stand-in household contact channel's credential. Its digest is pinned in the company's
#: counterparty registry (`company/interfaces/wall_protocol.py::MOVE_OUT_CONTACT_SENDER`).
MOVE_CONTACT_CREDENTIAL = "household-move-contact-01::participant-credential::v1"


def _encode_payload(notice: MoveOutNotice) -> dict:
    body = {f.name: getattr(notice, f.name) for f in dataclasses.fields(notice)}
    leaking = sorted(set(body) & set(FORBIDDEN_TRUTH_FIELDS))
    if leaking:
        raise ValueError(f"move-out notice would carry world truth: {leaking}")
    body["move_out_date"] = notice.move_out_date.isoformat()
    body["notified_on"] = notice.notified_on.isoformat()
    return body


class MoveOutNoticeFeed:
    """One run's move-out notices: a gap-free sequence for the household contact sender."""

    def __init__(self) -> None:
        self._next_sequence = 0

    def wire_notices_for_move(self, supply_points: Sequence[str], move_out_date: dt.date) -> list[dict]:
        """One framed notice per supply point the household holds with us, dated at the latest
        notice SLC 24.1(a) allows for this move date."""
        notified_on = latest_notice_date(move_out_date)
        observed_at = notice_observed_at(notified_on)
        out = []
        for point in sorted(supply_points):
            sequence = self._next_sequence
            self._next_sequence += 1
            notice = MoveOutNotice(supply_point_id=point, move_out_date=move_out_date,
                                   notified_on=notified_on)
            out.append({
                "sender": MOVE_OUT_SENDER,
                "credential": MOVE_CONTACT_CREDENTIAL,
                "handed_over_at": observed_at.isoformat(),
                "envelope": {
                    "notification_id": f"{MOVE_OUT_SENDER}-{sequence}",
                    "notification_type": MOVE_OUT_NOTIFICATION_TYPE,
                    "schema_version": SCHEMA_VERSION,
                    "sender": MOVE_OUT_SENDER,
                    "sequence": sequence,
                    "observed_at": observed_at.isoformat(),
                    "valid_time": move_out_date.isoformat(),
                    "payload": _encode_payload(notice),
                },
            })
        return out
