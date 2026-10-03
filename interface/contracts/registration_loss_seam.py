"""The registration-loss seam -- how a losing supplier learns a supply point has
been switched away from it.

WHAT CROSSES: one notice per Registrable Measurement Point (RMP: an MPAN or an
MPRN) that another supplier has registered. Under the Central Switching
Service it is the Losing Supplier's *Registration Secured Inactive
Notification*, REC Schedule 23 (Registration Services) v2.2, effective 27
February 2026, para 13.4.2: "Issue Notification that the Losing Supplier's
Registration is Secured Inactive", CSS Provider -> Losing Supplier, CSS API.
Source: https://recportal.co.uk/documents/20121/0/Registration+Services+v2.0.pdf
(fetched 2026-10-03; the file served is v2.2 despite the URL).

WHEN IT IS SENT is the schedule's own rule, which is why this notice and not an
earlier one is the first to cross: a Registration becomes Secured Active when
"the deadline by which the proposed Registration can be Cancelled has passed
(being 17.00 hours on the day before the Supply Effective From Date)" (para
1.4(d)); the Secured Inactive notice to the loser is issued on that transition
(para 13.4). So the notice's clock is a pure function of the switch's
effective date, and no lead time had to be chosen.

The regime boundary is CSS go-live, 18 July 2022: Schedule 23's change history
records version 1.0 implemented on "18 July 2022" with the Switching SCR
modification. Before it, an electricity loss was notified through MPAS
(Master Registration Agreement) and a gas loss through UK Link; neither flow's
catalogue was reachable from this build (the DTC host does not resolve), so
the pre-CSS notice keeps the shape below with its timing carried as a named
gap -- see `GAPS["pre_css_timing"]`.

WHAT THE LOSING SUPPLIER IS NOT TOLD, and so what may never ride here: why the
household left, what the gaining supplier charges, the world's departure
probability or roll, the household's engagement or stress. A CSS notice
reports a registration's status, and nothing else. `FORBIDDEN_TRUTH_FIELDS`
holds the world's own spellings of those, measured from the departure events
the producer is called beside.

THE SEAM DOES NOT YET MODEL A PROCESS, and that is the next step, named rather
than implied. A CSS switch reaches the loser twice before this notice -- the
'Invitation to Intervene' when the request is Pending (para 7.1.9), which
opens an Objection Window that for a domestic premises ends "at 17.00 hours on
the 1st Working Day after the day on which the Gaining Supplier submitted the
Switch Request" (para 6.2(a)) -- and can end Cancelled, Withdrawn or Annulled
instead (paras 6.7, 9, 10). The world has no submission date and no failed
switch, so none of that can be emitted without inventing it. `GAPS` names each.

NO SIM/GENERATOR/COMPANY SYMBOL: pure contract, checked by
`tests/interface/test_registration_loss_seam.py`.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

from interface.contracts.wall_envelope import WallNotification

# The seam's FIRST release, numbered 2 rather than 1: a seam's version is also the wire
# dialect its envelopes are read in (`company/interfaces/wall_protocol.py::
# WIRE_VOCABULARY_BY_VERSION`), and dialect 1 has no notification at all. Pinned in
# `tools/wall_channel_census.py::SURFACE_PINS` in the commit that gave it both ends.
SCHEMA_VERSION = 2

#: CSS go-live. REC Schedule 23 v2.2 change history: version 1.0, implementation
#: date "18 July 2022", reason "Switching SCR Modification". Fetched 2026-10-03.
#: (`simulation/acquisition_funnel.REC_REFORM_DATE` carries 2022-07-01 for the
#: same reform; that is its own reading, not this seam's.)
CSS_GO_LIVE = dt.date(2022, 7, 18)

#: Para 1.4(d): Secured Active at "17.00 hours on the day before the Supply
#: Effective From Date". A calendar day, not a working day.
SECURED_ACTIVE_HOUR = 17


@dataclass(frozen=True)
class RegistrationLossNotice:
    """The loser's notice that one of its registrations is ending.

    `supply_point_id` is the RMP the company held -- an MPAN or MPRN on the
    real wire. This world mints no MPxNs, so the producer sends the supply
    point id the company registered (`C1`, `C1g`), which is the company's own
    key for the meter point and plays the MPxN's part exactly.

    `supply_effective_from_date` is the gaining supplier's Supply Effective
    From Date: the first day this company does not supply. Schedule 23 para
    2.4-2.5 has the gainer propose it in the Switch Request; it is the date
    the Secured Active deadline is reckoned from (para 1.4(d)), so the notice
    that deadline triggers is about it.

    `registration_ref` is THIS SEAM's key for the registration the notice
    concerns. CSS identifies registrations; Schedule 23 does not print the
    format, and none is claimed (`GAPS["data_item_spelling"]`)."""

    registration_ref: str
    supply_point_id: str
    supply_effective_from_date: dt.date


RegistrationLossWallNotification = WallNotification[RegistrationLossNotice]

#: The notification_type each regime's notice is stamped with -- one spelling,
#: for the producer/consumer drift reason `payment_observable_seam` gives.
CSS_SECURED_INACTIVE_NOTIFICATION_TYPE = "css_registration_secured_inactive"
PRE_CSS_LOSS_NOTIFICATION_TYPE = "pre_css_registration_loss"

#: The counterparty each notice comes from. `WallNotification.sequence` is a
#: position in ONE sender's stream, so each is its own stream. CSS serves both
#: fuels (Schedule 23 para 13 carries rows "in the case of a gas RMP" and "an
#: electricity RMP" for one CSS Provider); before it, electricity registration
#: ran in MPAS and gas in UK Link -- two services, two senders.
CSS_SENDER = "CSS-PROVIDER-01"
PRE_CSS_ELECTRICITY_SENDER = "MPAS-01"
PRE_CSS_GAS_SENDER = "UK-LINK-01"
LOSS_NOTICE_SENDERS: tuple[str, ...] = (CSS_SENDER, PRE_CSS_ELECTRICITY_SENDER, PRE_CSS_GAS_SENDER)

ELECTRICITY = "electricity"
GAS = "gas"

UNSOLICITED_PAYLOAD_TYPES: tuple[type, ...] = (RegistrationLossNotice,)

# THE CLOSED OBSERVABLE FIELD SET, declared rather than derived, for the reason
# `payment_observable_seam.OBSERVABLE_PAYLOAD_FIELDS` gives.
OBSERVABLE_PAYLOAD_FIELDS: dict[str, tuple[str, ...]] = {
    "RegistrationLossNotice": (
        "registration_ref", "supply_point_id", "supply_effective_from_date",
    ),
}

#: No field of this notice may be None: each is established by Schedule 23 as
#: a property of the registration the notice concerns.
NONE_MEANS: dict[str, str] = {}

# THE SECOND BELT: world truth that must never ride on a notice. MEASURED, not
# anticipated: each is a key `simulation/customer_events.py` or the run loop
# writes on a departure event (2026-10-03). The live-run control goes further
# and asserts no notice field shares a name with ANY key of ANY departure event
# the run produced, so a new world key colliding with a notice field reds.
FORBIDDEN_TRUTH_FIELDS: tuple[str, ...] = (
    "random_roll",
    "effective_retention_probability",
    "realized_churn_probability",
    "churn_probability",
    "win_probability",
    "departure_cause",
    "departure_occasion",
    "home_move_won",
    "home_move_win_undelivered",
    "engagement_level",
    "market_switching_multiplier",
    "price_differential_vs_market_reference",
)
# NOT `market_reference_gbp_per_mwh`, though the world writes it on a departure: a currency-named
# token here reads as a market quantity baked into the seam (tests/architecture/
# test_market_at_the_seams.py). The live-run control asserts no notice field shares a name with ANY
# departure-event key, which covers it.

#: What a real loser is told that this seam does not carry, and what it does
#: not yet know how to time. Each is a gap, not a decision.
GAPS: dict[str, str] = {
    "invitation_to_intervene": (
        "Schedule 23 para 7.1.9 sends the loser an 'Invitation to Intervene' when a Switch "
        "Request is Pending, opening the Objection Window (para 6.2(a): domestic, ends 17:00 on "
        "the 1st Working Day after submission). Its date is the request's submission date, which "
        "para 2.5 bounds (the effective date is at least one complete Working Day and at most 28 "
        "days after it) but does not fix, and the world draws no submission date. Not emitted."
    ),
    "failed_switch_outcomes": (
        "Cancelled (objection, para 6.7), Withdrawn (para 9) and Annulled (para 10) "
        "registrations each notify the loser (paras 13.2.16, 13.3.5). The world's departure is "
        "a single roll that always succeeds, so no failed switch exists to notify."
    ),
    "gaining_supplier_identity": (
        "Whether the loser's notices name the gaining supplier is not established by Schedule 23; "
        "the message data items live in the REC Data Specification (EMAR), which did not resolve "
        "from this build on 2026-10-03. Not carried, and not to be added as None."
    ),
    "change_of_occupier_flag": (
        "A Switch Request may state a Change of Occupier (para 2.7) and the loser's objection "
        "rules depend on it (para 6.3), so the loser sees it on the Pending registration. The "
        "world has no change-of-occupier departure to flag, and it belongs on the Invitation."
    ),
    "data_item_spelling": (
        "Field names here are this seam's. The CSS data item names and the registration "
        "identifier format are in the REC Data Specification, not fetched."
    ),
    "pre_css_timing": (
        "Before 18 July 2022 the loser learned of an electricity loss through MPAS and of a gas "
        "loss through UK Link, in advance of the transfer; the advance is not established here. "
        "A pre-CSS notice is therefore observed on the effective date itself -- the timing the "
        "company had before this seam existed -- and claims no advance warning."
    ),
    "go_live_transition": (
        "How a switch whose Secured Active deadline straddles go-live was notified is not "
        "established. A notice is CSS when its Secured Active moment falls on or after "
        "CSS_GO_LIVE, and pre-CSS otherwise."
    ),
}


def secured_active_at(supply_effective_from_date: dt.date) -> dt.datetime:
    """17:00 on the calendar day before the effective date (para 1.4(d))."""
    day_before = supply_effective_from_date - dt.timedelta(days=1)
    return dt.datetime.combine(day_before, dt.time(SECURED_ACTIVE_HOUR))


def is_css(supply_effective_from_date: dt.date) -> bool:
    """Whether this switch ran through CSS (`GAPS["go_live_transition"]`)."""
    return secured_active_at(supply_effective_from_date).date() >= CSS_GO_LIVE


def loss_notice_observed_at(supply_effective_from_date: dt.date) -> dt.datetime:
    """When the loser is told, by regime. CSS: the Secured Active moment.
    Pre-CSS: midnight on the effective date (`GAPS["pre_css_timing"]`)."""
    if is_css(supply_effective_from_date):
        return secured_active_at(supply_effective_from_date)
    return dt.datetime.combine(supply_effective_from_date, dt.time(0))


def loss_notice_sender(supply_effective_from_date: dt.date, fuel: str) -> str:
    """Which registration service tells the loser, by regime and fuel."""
    if fuel not in (ELECTRICITY, GAS):
        raise ValueError(f"fuel must be {ELECTRICITY!r} or {GAS!r}, got {fuel!r}")
    if is_css(supply_effective_from_date):
        return CSS_SENDER
    return PRE_CSS_ELECTRICITY_SENDER if fuel == ELECTRICITY else PRE_CSS_GAS_SENDER


def loss_notice_type(supply_effective_from_date: dt.date) -> str:
    """The notification_type stamped on the notice, by regime."""
    if is_css(supply_effective_from_date):
        return CSS_SECURED_INACTIVE_NOTIFICATION_TYPE
    return PRE_CSS_LOSS_NOTIFICATION_TYPE
