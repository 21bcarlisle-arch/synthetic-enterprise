"""The world draws a Debt Respite (Breathing Space) moratorium and writes the start notice the
Secretary of State sends the household's energy creditor (SI 2020/1311 reg 25(2)(b), W2_44).

REUSE: simulation/debt_respite_draw.py
CLASS: CUSTOM
INDEX: searched "moratorium", "breathing space", "debt respite", "notice feed" under simulation/.
       `move_out_notice_feed.py` and `registration_loss_feed.py` are the nearest: framed
       notification producers for one counterparty each. This is the same shape for a different
       counterparty (the Breathing Space register) with its own draw, so it is its own module rather
       than a branch in either.

Knowledge: `docs/market_research/debt_and_collections.md`, "Breathing Space", sub-section "The entry
rate (E9, 2026-11-15)". The law is the commons artefact
`docs/domain_artefact_library/regulatory/debt_respite_breathing_space_moratorium.json`.

WHO IS AT RISK. A household whose bill this period went unpaid in the world's own truth
(`PaymentEvent.is_unresolved`). That is the world's reading of "in arrears with its energy
supplier", the population the rate's denominator counts (Ofgem's domestic electricity accounts in
arrears or repaying). The company's ledger is never read here: a world draw keyed to company state
would let the company's books decide the world.

THE RATE PER INDEBTED ACCOUNT-YEAR is `registrations x energy share / indebted accounts`, per
calendar year:
  * registrations: Insolvency Service, Individual insolvencies (England and Wales, standard
    moratoria only, long-run CSV read in the Aug 2026 release). 2021 counts from 4 May, so it is
    annualised over 242 days; 2026 is Jan-Aug, annualised over 8 months.
  * indebted accounts: Ofgem debt and arrears indicators, Q4 of the year (Q2 for 2026), electricity
    accounts in arrears with no plan plus those repaying on one. GB, while the registrations are
    E&W: spread across a GB population, the expected total is the E&W total, which is right if the
    world's households are GB. The world does not hold a household's nation, so Scottish
    households (a different scheme, the moratorium on diligence) are drawn too. Stated, not fixed.
  * energy share: StepChange Statistics Yearbook 2025 (Mar 2026), "% of clients in arrears",
    SUM: energy, 40% (2024) and 37% (2025) of new clients. StepChange registers 56-59% of all
    moratoria, and its client mix is taken for all registrants. The point is 0.37. The low end is
    0.27, StepChange's count of 44,519 clients behind on energy in 2025 (Plugging the gap, Apr 2026)
    over 163,916 new clients, which may be on different bases. The share is assumed to hold for
    2021-2023, where no yearbook was read.
A registration is per person, and one debtor's notice names every qualifying debt. A household
with two fuels is drawn once (the electricity count is the denominator).

WHAT IS NOT DRAWN, each named:
  * The mental health crisis moratorium (1.5-1.7% of registrations). Its end is keyed to a
    treatment end no source sizes, and a register with no end notice must treat it as in force, so
    a drawn one would never end. An under-draw of about 1 in 60 moratoria.
  * Cancellation at the midway review (day 25-35). No source counts cancellations. Omitting them
    holds every moratorium the full 60 days, which over-protects: it can only constrain the company.
  * Added-debt notices (reg 15). The start notice names the one energy account.
  * The end notice (reg 26(3)(b)). The company's register ends a standard moratorium on day 60
    itself; nothing the world would say changes that.

THE 12-MONTH BAR (Insolvency Service guidance s.2.3): a debtor who had a standard moratorium in the
previous 12 months cannot have another. The drawer holds each household's last start.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from datetime import datetime, time
from typing import Dict, Optional, Set, Tuple

from interface.contracts.debt_respite_seam import (
    BREATHING_SPACE_REGISTER_SENDER,
    FORBIDDEN_TRUTH_FIELDS,
    MORATORIUM_START_NOTIFICATION_TYPE,
    SCHEMA_VERSION,
    MoratoriumStartNotice,
    MoratoriumType,
    NotifiedDebt,
)
from simulation.rng_substream import substream

STREAM_NAMESPACE = "W2_44_debt_respite"

#: The stand-in register's credential. Its digest is pinned in the company's counterparty registry
#: (`company/interfaces/wall_protocol.py::BREATHING_SPACE_REGISTER_SENDER`).
REGISTER_CREDENTIAL = "breathing-space-register-01::participant-credential::v2"

#: Scheme in force from (reg 1(2)). No moratorium starts before it.
SCHEME_IN_FORCE_FROM = dt.date(2021, 5, 4)

#: Standard registrations, E&W, per calendar year, annualised where the year is partial.
_STANDARD_REGISTRATIONS_PER_YEAR: Dict[int, float] = {
    2021: 40_502 * 365 / 242,
    2022: 69_571,
    2023: 86_926,
    2024: 87_732,
    2025: 87_813,
    2026: 39_240 * 12 / 8,
}

#: Ofgem, domestic electricity accounts in arrears (no plan) plus repaying (plan), Q4 (Q2 2026).
_INDEBTED_ELECTRICITY_ACCOUNTS: Dict[int, int] = {
    2021: 775_721 + 979_224,
    2022: 778_598 + 877_337,
    2023: 1_005_350 + 753_887,
    2024: 1_045_302 + 810_544,
    2025: 1_146_497 + 829_275,
    2026: 1_187_788 + 888_824,
}

#: StepChange 2025 yearbook, new clients in energy arrears. The range is (0.27, 0.40); see above.
ENERGY_SHARE = 0.37
ENERGY_SHARE_RANGE = (0.27, 0.40)

#: Guidance s.2.3: no second standard moratorium within 12 months of the last.
_REPEAT_BAR_DAYS = 365


def annual_rate(year: int, energy_share: float = ENERGY_SHARE) -> float:
    """P(a standard moratorium naming this supplier starts) per indebted account-year.

    Zero before the scheme. A year past the table takes the last year in it: the series is flat
    from 2023 and the run never reaches past 2026."""
    if year < SCHEME_IN_FORCE_FROM.year:
        return 0.0
    y = min(year, max(_STANDARD_REGISTRATIONS_PER_YEAR))
    return _STANDARD_REGISTRATIONS_PER_YEAR[y] * energy_share / _INDEBTED_ELECTRICITY_ACCOUNTS[y]


def monthly_hazard(year: int, energy_share: float = ENERGY_SHARE) -> float:
    """The annual rate as a monthly hazard, `1 - (1 - r)^(1/12)`: one draw per billed month."""
    return 1.0 - (1.0 - annual_rate(year, energy_share)) ** (1.0 / 12.0)


def _encode_payload(notice: MoratoriumStartNotice) -> dict:
    """The notice as wire values. The seam's second belt on the world side: a payload carrying a
    world-truth field is refused before it is sent."""
    body = {
        "register_entry_ref": notice.register_entry_ref,
        "moratorium_type": notice.moratorium_type.value,
        "start_date": notice.start_date.isoformat(),
        "debtor_full_name": notice.debtor_full_name,
        "debtor_date_of_birth": (None if notice.debtor_date_of_birth is None
                                 else notice.debtor_date_of_birth.isoformat()),
        "debtor_address": notice.debtor_address,
        "debts": [{"creditor_account_ref": d.creditor_account_ref} for d in notice.debts],
    }
    leaking = sorted(set(body) & set(FORBIDDEN_TRUTH_FIELDS))
    if leaking:
        raise ValueError(f"moratorium start notice would carry world truth: {leaking}")
    return body


@dataclass
class MoratoriumDrawer:
    """The world's Breathing Space applications for one run, and the notices they send.

    `draw` is asked once per (household, billed month). Each draw is its own substream keyed on the
    household and the month, so asking or not asking one household moves no other draw."""

    energy_share: float = ENERGY_SHARE
    _last_start: Dict[str, dt.date] = field(default_factory=dict)
    _asked: Set[Tuple[str, int]] = field(default_factory=set)
    _sequence: int = 0

    def draw(self, customer_id: str, account_ref: str, period_index: int, on: dt.date,
             in_arrears: bool) -> Optional[dict]:
        """The framed start notice if this household's adviser registers one on `on`, else None.

        The register entry is made on `on`; the moratorium starts the next day (reg 26(1)); an
        electronic notice is deemed received the day it is sent (reg 37(4)(a)), so it is observed
        on `on`. `account_ref` is the supplier's account the notice names: the creditor matches on
        it (the contract's `NotifiedDebt`)."""
        if not in_arrears or on < SCHEME_IN_FORCE_FROM:
            return None
        # One draw per household-month: a dual-fuel household's two legs ask the same question.
        if (customer_id, period_index) in self._asked:
            return None
        self._asked.add((customer_id, period_index))
        last = self._last_start.get(customer_id)
        if last is not None and (on - last).days < _REPEAT_BAR_DAYS:
            return None
        rng = substream(STREAM_NAMESPACE, f"{customer_id}::{period_index}", 0)
        if rng.random() >= monthly_hazard(on.year, self.energy_share):
            return None
        start = on + dt.timedelta(days=1)
        self._last_start[customer_id] = start
        sequence = self._sequence
        self._sequence += 1
        notice = MoratoriumStartNotice(
            register_entry_ref=f"BS-{customer_id}-{start.isoformat()}",
            moratorium_type=MoratoriumType.STANDARD,
            start_date=start,
            debtor_full_name=None,
            debtor_date_of_birth=None,
            debtor_address=None,
            debts=(NotifiedDebt(creditor_account_ref=account_ref),),
        )
        observed_at = datetime.combine(on, time(12, 0)).isoformat()
        return {
            "sender": BREATHING_SPACE_REGISTER_SENDER,
            "credential": REGISTER_CREDENTIAL,
            "handed_over_at": observed_at,
            "envelope": {
                "notification_id": f"{BREATHING_SPACE_REGISTER_SENDER}-{sequence}",
                "notification_type": MORATORIUM_START_NOTIFICATION_TYPE,
                "schema_version": SCHEMA_VERSION,
                "sender": BREATHING_SPACE_REGISTER_SENDER,
                "sequence": sequence,
                "observed_at": observed_at,
                "valid_time": start.isoformat(),
                "payload": _encode_payload(notice),
            },
        }

    @property
    def notices_sent(self) -> int:
        return self._sequence
