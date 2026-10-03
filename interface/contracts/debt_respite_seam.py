"""The debt-respite seam -- the Insolvency Service's Breathing Space notices,
as a creditor receives them.

WHAT CROSSES: the three notices SI 2020/1311 (The Debt Respite Scheme
(Breathing Space Moratorium and Mental Health Crisis Moratorium) (England and
Wales) Regulations 2020, https://www.legislation.gov.uk/uksi/2020/1311/made,
read 2026-10-03) obliges the Secretary of State to send a creditor:

  * START   -- regs 25(2)(b) (breathing space) and 31(2)(b) (mental health
               crisis): "send a notification of the start of the ... moratorium
               to those creditors and agents whose contact details have been
               provided". It names the creditor's debts: reg 14(2) obliges a
               creditor to report any debt "that was not included in the
               notification".
  * END     -- reg 26(3)(b) (a breathing space moratorium running its 60 days)
               and reg 21(5) (the debtor's death), which says the notice must
               "specify the date on which the moratorium ended, and ... state
               the reason for the end".
  * CANCELLATION -- regs 18(8), 27(12) and 34(8): the notice must "state the
               reason for the cancellation, and ... specify the date on which
               the cancellation takes effect".

What a register entry holds is reg 36(1): the debtor's full name, date of
birth and usual residential address (which reg 38 lets be withheld), any
business trading name and address, the start date, and the end or
cancellation date. Notices go electronically, by hand or by post (reg 37(2));
an electronic one is deemed received the day it is sent (reg 37(4)(a)).

WHY A SEAM OF ITS OWN, not a payload on the payment seam: the sender is a
different counterparty (the Secretary of State's register, run by the
Insolvency Service), not the Bacs bureau, and `WallNotification` names one
sender per stream.

UNSOLICITED BY CONSTRUCTION. The company never asks for these; the register
pushes them. So the only envelope specialisations below are
`WallNotification`s -- there is no request leg to declare.

THE EPISTEMIC WALL. Every field is printed on a notice a real creditor
receives, or held on the register entry the notice concerns. None of these
types may carry the household's true financial position, why it sought debt
advice, or anything about a moratorium the creditor was not notified of.

NO PRODUCER YET, AND THAT IS THE FINDING, not an omission. The world
(`simulation/`) has no moratorium events: no household ever applies for one,
and the commons
(`docs/domain_artefact_library/regulatory/debt_respite_breathing_space_moratorium.json`,
NOT_ESTABLISHED) records that no source splits the Insolvency Service's monthly
registration counts by creditor type, so no sourced entry rate exists to draw
one from. This module is the shape a producer must fill when one exists; the
company's register (`company/billing/breathing_space_register.py`) stays empty
until then.

NO SIM/GENERATOR/COMPANY SYMBOL: pure contract, checked by
`tests/interface/test_debt_respite_seam.py`.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum

from interface.contracts.wall_envelope import WallNotification

# v1: the seam's first release. Not yet in `tools/wall_channel_census.py::SURFACE_PINS`:
# the census scores a seam once a module outside `interface/` imports it, and
# nothing does yet. The first producer or consumer to import it must pin it.
SCHEMA_VERSION = 1


class MoratoriumType(str, Enum):
    """The two moratoria the SI defines: Part 2 (breathing space, 60 days,
    reg 26) and Part 3 (mental health crisis, no fixed end, reg 32). The
    notice is the start notification of one Part or the other, so the type is
    what the notice itself says."""

    STANDARD = "standard"
    MENTAL_HEALTH_CRISIS = "mental_health_crisis"


@dataclass(frozen=True)
class NotifiedDebt:
    """One debt owed to this creditor that the start notice names (reg 14(2)
    implies the notice lists debts; the debt advice provider supplies them,
    reg 25(1)(b)-(c)).

    NO AMOUNT, deliberately. The SI says the notice names the debts; it does
    not say it states a balance, and nothing here establishes that the
    Insolvency Service prints one. A field the real notice may not carry is
    not added as a None -- that would assert the notice has the field. The
    creditor holds the balance on its own ledger; which part of it is
    moratorium debt (owed when the application was made, reg 6) is the
    company's reading, not the notice's."""

    creditor_account_ref: str


@dataclass(frozen=True)
class MoratoriumStartNotice:
    """The start notification (regs 25(2)(b), 31(2)(b)).

    `register_entry_ref` is THIS SEAM's key for the register entry the notice
    concerns, so the end or cancellation notice can be matched to it. The SI
    requires the entry (reg 25(2)(a)) and requires notices about the same
    moratorium; it does not specify a printed reference format, and none is
    claimed here."""

    register_entry_ref: str
    moratorium_type: MoratoriumType
    start_date: dt.date
    debtor_full_name: str | None
    debtor_date_of_birth: dt.date | None
    debtor_address: str | None
    debts: tuple[NotifiedDebt, ...]


@dataclass(frozen=True)
class MoratoriumEndNotice:
    """The end notification (regs 26(3)(b), 21(5)). `reason_text` is None for
    a breathing space moratorium that ran its course: reg 26(3) requires a
    notice that it ended and specifies no reason, so none is invented."""

    register_entry_ref: str
    end_date: dt.date
    reason_text: str | None


@dataclass(frozen=True)
class MoratoriumCancellationNotice:
    """The cancellation notification (regs 18(8), 27(12), 34(8)): the reason,
    and the date the cancellation takes effect."""

    register_entry_ref: str
    cancellation_effective_date: dt.date
    reason_text: str


MoratoriumStartWallNotification = WallNotification[MoratoriumStartNotice]
MoratoriumEndWallNotification = WallNotification[MoratoriumEndNotice]
MoratoriumCancellationWallNotification = WallNotification[MoratoriumCancellationNotice]

#: The notification_type each notice is stamped with -- one spelling, for the
#: producer/consumer drift reason `payment_observable_seam` gives.
MORATORIUM_START_NOTIFICATION_TYPE = "moratorium_start"
MORATORIUM_END_NOTIFICATION_TYPE = "moratorium_end"
MORATORIUM_CANCELLATION_NOTIFICATION_TYPE = "moratorium_cancellation"

UNSOLICITED_PAYLOAD_TYPES: tuple[type, ...] = (
    MoratoriumStartNotice,
    MoratoriumEndNotice,
    MoratoriumCancellationNotice,
)

# THE CLOSED OBSERVABLE FIELD SET, declared rather than derived, for the reason
# `payment_observable_seam.OBSERVABLE_PAYLOAD_FIELDS` gives: a set computed from
# the dataclasses widens with them and can never catch a widening.
OBSERVABLE_PAYLOAD_FIELDS: dict[str, tuple[str, ...]] = {
    "NotifiedDebt": ("creditor_account_ref",),
    "MoratoriumStartNotice": (
        "register_entry_ref", "moratorium_type", "start_date", "debtor_full_name",
        "debtor_date_of_birth", "debtor_address", "debts",
    ),
    "MoratoriumEndNotice": ("register_entry_ref", "end_date", "reason_text"),
    "MoratoriumCancellationNotice": (
        "register_entry_ref", "cancellation_effective_date", "reason_text",
    ),
}

#: Every field a notice may carry as None, and why. A None with no entry here
#: is a field the contract never decided about.
NONE_MEANS: dict[str, str] = {
    "MoratoriumStartNotice.debtor_full_name": (
        "held on the register (reg 36(1)(a)(i)); the world models households "
        "without personal identity, so a stand-in producer cannot fill it -- the "
        "creditor matches on creditor_account_ref"
    ),
    "MoratoriumStartNotice.debtor_date_of_birth": (
        "held on the register (reg 36(1)(a)(i)); not modelled by the world"
    ),
    "MoratoriumStartNotice.debtor_address": (
        "held on the register (reg 36(1)(a)(i)) but may be withheld under reg 38 "
        "(risk of violence) -- absent in the real world too; not modelled by the world"
    ),
    "MoratoriumEndNotice.reason_text": (
        "reg 26(3) requires notice that a breathing space moratorium ended and "
        "specifies no reason; reg 21(5) (death) does require one"
    ),
}

# THE SECOND BELT: names of world-side truth that must never ride on a notice.
# ANTICIPATED, not measured -- no world-side moratorium producer exists to
# read attribute names from (see the header), so these are spellings of the
# classes the header forbids.
FORBIDDEN_TRUTH_FIELDS: tuple[str, ...] = (
    "hardship_tier",
    "income_stress",
    "stress",
    "ability",
    "willingness",
    "quadrant",
    "true_reason",
    "true_debt",
    "data_regime",
    "period_index",
)
