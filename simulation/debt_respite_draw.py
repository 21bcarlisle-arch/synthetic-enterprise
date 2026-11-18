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

THE MENTAL HEALTH CRISIS MORATORIUM (W2_45, Part 3). Drawn at its own published count, through
the same energy share and denominator: E&W registrations of that type per year, read from the same
CSV (1.5-1.7% of all registrations). One uniform per household-month decides both types: below the
standard hazard is a standard moratorium, as it was before W2_45, so no standard draw moved; the
next band, of the MHCM hazard's width, is an MHCM. No 12-month bar applies to it (G2.3). Neither
type is drawn while one is in force.
  ITS END. Reg 32(2)(a): it ends at "the end of the period of 30 days beginning with the day on
  which the debtor stops receiving mental health crisis treatment", so its last protected day is
  the treatment's last day plus 30. No source counts how long an MHCM runs. The treatment still to
  run when the moratorium starts is a STATED BELIEF, drawn uniformly on 13-42 days:
    * 13 days: the median crisis resolution home treatment (CRHT) episode in a UK service audit,
      which put the 2017 national survey's typical episode at about 21 days;
    * 42 days: the top of the RCPsych CRHTT practice guidelines' "three to six weeks" (2022);
    * inside the range: NHS Benchmarking's 33.4-day mean adult acute inpatient stay (2016), for a
      detained debtor.
  Taking the start as the start of the treatment over-states what is left of it. The error runs
  toward a longer hold, which only constrains the company. Sources and gap:
  `docs/market_research/debt_and_collections.md`, "The mental health crisis moratorium's length".
  The register sends the end notice (`MoratoriumEndNotice`, reason "crisis treatment ended") BEFORE
  the end day: the adviser learns at a reg 33 check, and regs 32(4) and 32(6) add two business days
  (`mhcm_end_notice_day`; corrected the same day from "on the end day"). `end_notices_due` hands
  it over once the world's clock reaches that day.

WHAT IS NOT DRAWN, each named:
  * The MHCM's other end, reg 32(2)(b)-(c): 30 days after the nominated contact fails to answer the
    adviser's check. No source counts it, and it can only end one earlier, so leaving it out
    over-protects.
  * Cancellation at the midway review (day 25-35). No source counts cancellations. Omitting them
    holds every moratorium the full 60 days, which over-protects: it can only constrain the company.
  * Added-debt notices (reg 15). The start notice names the one energy account.
  * The standard end notice (reg 26(3)(b)). The company's register ends a standard moratorium on
    day 60 itself; nothing the world would say changes that.

THE 12-MONTH BAR (Insolvency Service guidance s.2.3): a debtor who had a standard moratorium in the
previous 12 months cannot have another. The drawer holds each household's last start.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from datetime import datetime, time
from typing import Dict, List, Optional, Set, Tuple

from interface.contracts.debt_respite_seam import (
    BREATHING_SPACE_REGISTER_SENDER,
    FORBIDDEN_TRUTH_FIELDS,
    MORATORIUM_END_NOTIFICATION_TYPE,
    MORATORIUM_START_NOTIFICATION_TYPE,
    SCHEMA_VERSION,
    MoratoriumEndNotice,
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

#: Standard registrations, E&W, per calendar year, annualised where the year is partial. Pinned by the
#: year-keyed rate census to `insolvency_service_breathing_space_registrations.json` (Oct 2026 edition).
_STANDARD_REGISTRATIONS_PER_YEAR: Dict[int, float] = {
    2021: 40_502 * 365 / 242,
    2022: 69_571,
    2023: 86_926,
    2024: 87_732,
    2025: 87_813,
    2026: 49_785 * 12 / 10,
}

#: Mental health crisis registrations, E&W, same CSV and the same annualising (W2_45).
_MHCM_REGISTRATIONS_PER_YEAR: Dict[int, float] = {
    2021: 624 * 365 / 242,
    2022: 1_216,
    2023: 1_464,
    2024: 1_288,
    2025: 1_317,
    2026: 1_321 * 12 / 10,
}

#: Reg 32(2)(a): the MHCM ends at the end of 30 days beginning with the day treatment stops.
MHCM_POST_TREATMENT_DAYS = 30

#: STATED BELIEF, not a sourced count: crisis treatment still to run at the MHCM's start, in days,
#: drawn uniformly on this range (CRHT median episode 13; RCPsych's "three to six weeks" top, 42).
MHCM_TREATMENT_DAYS_RANGE = (13, 42)

#: What the end notice says. Reg 32(2)(a) is the limb the world draws; the reg 26(3)/21(5) reason
#: wording the Insolvency Service prints is not published, so this is the limb's own phrase.
MHCM_END_REASON = "crisis treatment ended"

#: Ofgem, domestic electricity accounts in arrears (no plan) plus repaying (plan), Q4 (Q2 2026).
#: Pinned to `ofgem_domestic_electricity_indebted_accounts.json` by the same census.
_INDEBTED_ELECTRICITY_ACCOUNTS: Dict[int, int] = {
    2021: 775_721 + 979_224,
    2022: 778_598 + 877_337,
    2023: 1_005_350 + 753_887,
    2024: 1_045_302 + 810_544,
    2025: 1_146_497 + 829_275,
    2026: 1_187_788 + 888_824,
}

#: StepChange 2025 yearbook, new clients in energy arrears. EVIDENCE RANGE (0.27, 0.40): both ends
#: are StepChange figures, named in the module docstring.
ENERGY_SHARE = 0.37
#: EVIDENCE RANGE, the two StepChange ends above.
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


def mhcm_annual_rate(year: int, energy_share: float = ENERGY_SHARE) -> float:
    """P(a mental health crisis moratorium naming this supplier starts) per indebted
    account-year: the same derivation as `annual_rate`, over the MHCM count."""
    if year < SCHEME_IN_FORCE_FROM.year:
        return 0.0
    y = min(year, max(_MHCM_REGISTRATIONS_PER_YEAR))
    return _MHCM_REGISTRATIONS_PER_YEAR[y] * energy_share / _INDEBTED_ELECTRICITY_ACCOUNTS[y]


def mhcm_monthly_hazard(year: int, energy_share: float = ENERGY_SHARE) -> float:
    return 1.0 - (1.0 - mhcm_annual_rate(year, energy_share)) ** (1.0 / 12.0)


def mhcm_end_date(start: dt.date, treatment_days: int) -> dt.date:
    """The MHCM's last protected day (reg 32(2)(a)). Treatment runs `treatment_days` from the start,
    so its last day is `start + treatment_days - 1`; the 30 days begin with the day after that,
    the day it "stops"."""
    stops = start + dt.timedelta(days=treatment_days)
    return stops + dt.timedelta(days=MHCM_POST_TREATMENT_DAYS - 1)


#: Reg 33: the adviser asks the nominated contact between day 20 and day 30 of the moratorium, then
#: every 20-30 days. Taken at the middle of each window.
MHCM_CONTACT_CHECK_EVERY_DAYS = 25

#: Reg 32(4) then 32(6): the adviser tells the Secretary of State by the end of the next business
#: day, and the Secretary of State tells the creditor by the end of the one after. Taken as 2 days.
MHCM_END_NOTICE_LAG_DAYS = 2


def mhcm_end_notice_day(start: dt.date, treatment_days: int) -> dt.date:
    """The day the creditor is sent the end notice (reg 32(4), 32(6)(b), 33). The adviser learns
    the treatment has stopped at the first reg 33 check on or after the day it stops, then two
    business days pass. Checks are 25 days apart and the moratorium runs 29 days past the stop, so
    the notice always comes BEFORE the end it names."""
    checks = -(-max(treatment_days, 1) // MHCM_CONTACT_CHECK_EVERY_DAYS)
    learned = start + dt.timedelta(days=checks * MHCM_CONTACT_CHECK_EVERY_DAYS)
    return learned + dt.timedelta(days=MHCM_END_NOTICE_LAG_DAYS)


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
    #: customer -> last protected day of the moratorium in force (either type).
    _in_force_until: Dict[str, dt.date] = field(default_factory=dict)
    #: MHCM end notices not yet handed over: (end_date, customer_id, register_entry_ref).
    # (the day the notice is sent, the end it names, customer, register entry ref)
    _pending_ends: List[Tuple[dt.date, dt.date, str, str]] = field(default_factory=list)
    mhcm_started: int = 0
    mhcm_ended: int = 0
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
        in_force = self._in_force_until.get(customer_id)
        if in_force is not None and on <= in_force:
            return None
        rng = substream(STREAM_NAMESPACE, f"{customer_id}::{period_index}", 0)
        u = rng.random()
        h_std = monthly_hazard(on.year, self.energy_share)
        last = self._last_start.get(customer_id)
        barred = last is not None and (on - last).days < _REPEAT_BAR_DAYS
        start = on + dt.timedelta(days=1)
        ref = f"BS-{customer_id}-{start.isoformat()}"
        if u < h_std and not barred:
            kind = MoratoriumType.STANDARD
            self._last_start[customer_id] = start
            self._in_force_until[customer_id] = start + dt.timedelta(days=59)
        elif h_std <= u < h_std + mhcm_monthly_hazard(on.year, self.energy_share):
            kind = MoratoriumType.MENTAL_HEALTH_CRISIS
            ref = f"MHCM-{customer_id}-{start.isoformat()}"
            lo, hi = MHCM_TREATMENT_DAYS_RANGE
            treatment = substream(STREAM_NAMESPACE, f"{customer_id}::{period_index}::mhcm_treatment",
                                  0).randint(lo, hi)
            end = mhcm_end_date(start, treatment)
            self._in_force_until[customer_id] = end
            self._pending_ends.append(
                (mhcm_end_notice_day(start, treatment), end, customer_id, ref))
            self.mhcm_started += 1
        else:
            return None
        notice = MoratoriumStartNotice(
            register_entry_ref=ref,
            moratorium_type=kind,
            start_date=start,
            debtor_full_name=None,
            debtor_date_of_birth=None,
            debtor_address=None,
            debts=(NotifiedDebt(creditor_account_ref=account_ref),),
        )
        return self._frame(MORATORIUM_START_NOTIFICATION_TYPE, on, start,
                           _encode_payload(notice))

    def end_notices_due(self, on: dt.date) -> List[dict]:
        """Every MHCM end notice whose sending day has come by `on`, each handed over once, oldest
        first. It is sent BEFORE the end it names (`mhcm_end_notice_day`, regs 32(4), 32(6), 33)
        and deemed received that day (reg 37(4)(a)). A caller whose clock passes the day late
        delivers it late. The company's register holds a completed record in force through its end
        date, so an early notice does not cut protection short."""
        due = sorted(e for e in self._pending_ends if e[0] <= on)
        self._pending_ends = [e for e in self._pending_ends if e[0] > on]
        out = []
        for sent_on, end, _customer, ref in due:
            notice = MoratoriumEndNotice(register_entry_ref=ref, end_date=end,
                                         reason_text=MHCM_END_REASON)
            body = {"register_entry_ref": notice.register_entry_ref,
                    "end_date": notice.end_date.isoformat(), "reason_text": notice.reason_text}
            leaking = sorted(set(body) & set(FORBIDDEN_TRUTH_FIELDS))
            if leaking:
                raise ValueError(f"moratorium end notice would carry world truth: {leaking}")
            self.mhcm_ended += 1
            out.append(self._frame(MORATORIUM_END_NOTIFICATION_TYPE, sent_on, end, body))
        return out

    def _frame(self, notification_type: str, sent_on: dt.date, valid_on: dt.date,
               payload: dict) -> dict:
        sequence = self._sequence
        self._sequence += 1
        observed_at = datetime.combine(sent_on, time(12, 0)).isoformat()
        return {
            "sender": BREATHING_SPACE_REGISTER_SENDER,
            "credential": REGISTER_CREDENTIAL,
            "handed_over_at": observed_at,
            "envelope": {
                "notification_id": f"{BREATHING_SPACE_REGISTER_SENDER}-{sequence}",
                "notification_type": notification_type,
                "schema_version": SCHEMA_VERSION,
                "sender": BREATHING_SPACE_REGISTER_SENDER,
                "sequence": sequence,
                "observed_at": observed_at,
                "valid_time": valid_on.isoformat(),
                "payload": payload,
            },
        }

    @property
    def notices_sent(self) -> int:
        """Start notices sent (either type). End notices share the sequence and are not counted."""
        return self._sequence - self.mhcm_ended
