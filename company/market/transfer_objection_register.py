"""Transfer Objection Register (Phase GO).

When a customer initiates a switch to a new supplier, the losing
supplier can raise an objection through the Central Switching Service
(CSS). Source: REC Schedule 23 "Registration Services" v2.2 (effective
27 February 2026), fetched 2026-10-03 from recportal.co.uk
(/documents/20121/5829638857/Registration+Services+Current.pdf):

  * CSS went live on 18 July 2022 (the schedule's v1.0 implementation
    date). Before that, switching ran on MPAS/UK Link and the D-flows;
    this register models the CSS rule only.
  * Para 6.2: the Objection Window ends at 17:00 on the 1st Working Day
    (Domestic Premises) or the 2nd Working Day (Non-Domestic Premises)
    AFTER THE DAY THE GAINING SUPPLIER SUBMITTED THE SWITCH REQUEST --
    or earlier, when the losing supplier's validated response says it is
    not objecting (not modelled here). It is counted from the request,
    never from the day this supplier raised its objection.

Objection grounds. REC para 6.1 permits an objection only "where it is
permitted to do so in accordance with its Energy Supply Licence"; the
grounds are the licence's, not REC's, and para 6.3 adds only that an
objection to a request flagged as a Change of Occupier must have its
evidence kept for at least 12 months. The former citation "CSS Rules
Section 14" does not hold up: Section 14 of this schedule is Registration
Deactivation Requests, and it lists no grounds. The five grounds below, and the claim
that debt alone never blocks a switch (formerly cited as SLC 14.5),
are NOT ESTABLISHED from a source in this tree -- checking them against
the Standard Licence Conditions (SLC 14) text is a named gap:

  UNPAID_DEBT, METER_DISPUTE, CONTRACT_DISPUTE, COOLING_OFF,
  REGULATORY_RESTRICTION.

THE DEBT OBJECTION IS THE COMPANY'S DECISION (EP12, 2026-10-25). `decide_debt_objection` reads
this supplier's own ledger at the switch request and answers it under `DebtObjectionPolicy`; the
world only completes or cancels the switch. Grounds and figures: the Knowledge page
`docs/market_research/switching_mechanics_2026-10-25.md` section 2, and the rows of
`docs/market_research/domestic_debt_objection_rates_gb.md` cited at each constant. SLC 14.4(a)
does establish the debt ground, so UNPAID_DEBT is no longer among the unestablished grounds above.

Connects to: css_performance_register.py (overall CSS performance),
erroneous_transfer.py (wrongful transfers).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from company.compliance.working_days import add_working_days

#: REC Schedule 23 v2.2 para 6.2(a)/(b): the window ends on the Nth working day after the day
#: the gaining supplier submitted the switch request -- 1st for domestic premises, 2nd for
#: non-domestic -- at 17:00 (`OBJECTION_WINDOW_CLOSES_AT`).
_OBJECTION_WINDOW_WD = {"domestic": 1, "non_domestic": 2}
OBJECTION_WINDOW_CLOSES_AT = dt.time(17, 0)


class ObjectionGround(str, Enum):
    UNPAID_DEBT = "unpaid_debt"
    METER_DISPUTE = "meter_dispute"
    CONTRACT_DISPUTE = "contract_dispute"
    COOLING_OFF = "cooling_off"
    REGULATORY_RESTRICTION = "regulatory_restriction"


class ObjectionStatus(str, Enum):
    RAISED = "raised"
    VALID = "valid"
    INVALID = "invalid"
    RESOLVED = "resolved"
    WITHDRAWN = "withdrawn"


_OPEN = frozenset({ObjectionStatus.RAISED, ObjectionStatus.VALID})


@dataclass(frozen=True)
class TransferObjectionRecord:
    objection_id: str
    mpan: str
    switch_ref: str
    objection_date: dt.date
    ground: ObjectionGround
    status: ObjectionStatus = ObjectionStatus.RAISED
    resolution_date: Optional[dt.date] = None
    notes: str = ""
    #: The day the gaining supplier submitted the switch request -- what the window counts from.
    switch_request_submitted: Optional[dt.date] = None
    domestic: bool = True

    @property
    def is_open(self) -> bool:
        return self.status in _OPEN

    @property
    def objection_deadline(self) -> dt.date:
        """The last day an objection may be raised (until `OBJECTION_WINDOW_CLOSES_AT`).

        Counted from the switch request's submission (REC Schedule 23 para 6.2), so a record
        that does not carry it cannot say -- refused rather than counted from the wrong day."""
        if self.switch_request_submitted is None:
            raise ValueError(
                f"objection {self.objection_id}: the window is counted from the day the gaining "
                "supplier submitted the switch request (REC Schedule 23 para 6.2), and this "
                "record does not carry that date"
            )
        window = _OBJECTION_WINDOW_WD["domestic" if self.domestic else "non_domestic"]
        return add_working_days(self.switch_request_submitted, window)

    @property
    def objection_window_closes(self) -> dt.datetime:
        return dt.datetime.combine(self.objection_deadline, OBJECTION_WINDOW_CLOSES_AT)

    def resolution_days(self, as_of: dt.date) -> int:
        end = self.resolution_date if self.resolution_date is not None else as_of
        return (end - self.objection_date).days

    def objection_summary(self) -> str:
        return (
            "OBJ " + self.objection_id + " mpan=" + self.mpan
            + " switch=" + self.switch_ref
            + " ground=" + self.ground.value
            + " [" + self.status.value + "]"
        )


class TransferObjectionRegister:

    def __init__(self) -> None:
        self._records: List[TransferObjectionRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return "OBJ-" + str(self._counter).zfill(5)

    def raise_objection(
        self, mpan: str, switch_ref: str, objection_date: dt.date,
        ground: ObjectionGround, notes: str = "",
        *, switch_request_submitted: Optional[dt.date] = None, domestic: bool = True,
    ) -> TransferObjectionRecord:
        record = TransferObjectionRecord(
            objection_id=self._next_id(),
            mpan=mpan, switch_ref=switch_ref,
            objection_date=objection_date,
            ground=ground, notes=notes,
            switch_request_submitted=switch_request_submitted, domestic=domestic,
        )
        self._records.append(record)
        return record

    def _update(self, objection_id: str, **kwargs) -> TransferObjectionRecord:
        for i, r in enumerate(self._records):
            if r.objection_id == objection_id:
                updated = TransferObjectionRecord(
                    objection_id=r.objection_id,
                    mpan=r.mpan, switch_ref=r.switch_ref,
                    objection_date=r.objection_date,
                    ground=r.ground,
                    status=kwargs.get("status", r.status),
                    resolution_date=kwargs.get("resolution_date", r.resolution_date),
                    notes=kwargs.get("notes", r.notes),
                    switch_request_submitted=r.switch_request_submitted,
                    domestic=r.domestic,
                )
                self._records[i] = updated
                return updated
        raise KeyError("Objection " + objection_id + " not found")

    def mark_valid(self, objection_id: str) -> TransferObjectionRecord:
        return self._update(objection_id, status=ObjectionStatus.VALID)

    def mark_invalid(self, objection_id: str) -> TransferObjectionRecord:
        return self._update(objection_id, status=ObjectionStatus.INVALID)

    def resolve(self, objection_id: str, resolution_date: dt.date) -> TransferObjectionRecord:
        return self._update(objection_id, status=ObjectionStatus.RESOLVED,
                           resolution_date=resolution_date)

    def withdraw(self, objection_id: str) -> TransferObjectionRecord:
        return self._update(objection_id, status=ObjectionStatus.WITHDRAWN)

    def open_objections(self) -> List[TransferObjectionRecord]:
        return [r for r in self._records if r.is_open]

    def invalid_objections(self) -> List[TransferObjectionRecord]:
        return [r for r in self._records if r.status == ObjectionStatus.INVALID]

    def by_ground(self, ground: ObjectionGround) -> List[TransferObjectionRecord]:
        return [r for r in self._records if r.ground == ground]

    def by_switch(self, switch_ref: str) -> List[TransferObjectionRecord]:
        return [r for r in self._records if r.switch_ref == switch_ref]

    def average_resolution_days(self, as_of: dt.date) -> Optional[float]:
        resolved = [r for r in self._records
                    if r.status in (ObjectionStatus.RESOLVED, ObjectionStatus.INVALID,
                                   ObjectionStatus.WITHDRAWN)]
        if not resolved:
            return None
        return round(sum(r.resolution_days(as_of) for r in resolved) / len(resolved), 1)

    def invalid_rate_pct(self) -> Optional[float]:
        terminal = [r for r in self._records
                    if r.status not in (ObjectionStatus.RAISED, ObjectionStatus.VALID)]
        if not terminal:
            return None
        invalid = sum(1 for r in terminal if r.status == ObjectionStatus.INVALID)
        return round(invalid / len(terminal) * 100, 1)

    def objection_register_summary(self, as_of: dt.date) -> str:
        n = len(self._records)
        n_open = len(self.open_objections())
        n_invalid = len(self.invalid_objections())
        return (
            "Transfer Objection Register (" + str(as_of) + "): "
            + str(n) + " objections ("
            + str(n_open) + " open, "
            + str(n_invalid) + " invalid)."
        )


#: SLC 14: no debt objection for a charge outstanding 28 days or fewer since the customer was told
#: of it in writing. The bill is the written notice, so the clock is days since the bill.
#: Source: docs/market_research/domestic_debt_objection_rates_gb.md row 17.
SLC14_MIN_DAYS_SINCE_NOTICE = 28

#: Debt Assignment Protocol: a prepayment customer's debt below GBP 500 moves with them, so it is
#: no ground to object. Source: docs/market_research/domestic_debt_objection_rates_gb.md row 19
#: (the 2016 figure; not re-verified for later years, page row 145).
PREPAYMENT_DAP_CEILING_GBP = 500.0

#: Published supplier practice: informal de-minimis thresholds "ranging up to GBP 200 per fuel",
#: below which many suppliers let the transfer go. This company takes the top of that published
#: range; the page gives no other point in it. Source:
#: docs/market_research/domestic_debt_objection_rates_gb.md row 16 (Ofgem decision letter p.3).
DE_MINIMIS_GBP_PER_FUEL = 200.0


@dataclass(frozen=True)
class DebtObjectionPolicy:
    """This supplier's own objection policy. `de_minimis_gbp_per_fuel=None` objects on any debt
    the licence permits."""
    de_minimis_gbp_per_fuel: Optional[float] = DE_MINIMIS_GBP_PER_FUEL


@dataclass(frozen=True)
class DebtObjectionDecision:
    objected: bool
    #: Why, in words a refusal can be checked against.
    reason: str
    #: Debt on bills older than the SLC 14 clock -- what an objection could be raised for.
    objectionable_debt: float
    record: Optional[TransferObjectionRecord] = None


def decide_debt_objection(
    register: TransferObjectionRegister, supply_point_id: str, switch_ref: str,
    request_day: dt.date, unpaid_bills_by_age, *, prepayment: bool, fuels: int,
    policy: DebtObjectionPolicy = DebtObjectionPolicy(),
) -> DebtObjectionDecision:
    """Answer one domestic switch request on the debt ground, from this company's own ledger.

    `unpaid_bills_by_age` is `(unpaid GBP, days since the bill)` per bill still owed on the
    account, as the company's ledger holds it on `request_day` (`None`: never billed). `fuels`
    is how many fuels the account carries.

    THE DE-MINIMIS IS PER FUEL AND THE LEDGER IS PER ACCOUNT, so a dual-fuel account is objected
    to only when its objectionable debt exceeds the threshold times its fuels: then at least one
    fuel's share must exceed it. One fuel over the line with the other clear is let go, so this
    can only object less often than a per-fuel ledger would. An accepted objection on either fuel
    cancels both under CSS's one-fail-all-fail, so one decision answers the account.
    """
    owed = sum(gbp for gbp, days in (unpaid_bills_by_age or ())
               if days > SLC14_MIN_DAYS_SINCE_NOTICE)
    owed = round(owed, 2)
    if owed <= 0:
        return DebtObjectionDecision(False, "no debt outstanding more than "
                                     f"{SLC14_MIN_DAYS_SINCE_NOTICE} days since its bill", owed)
    if prepayment and owed < PREPAYMENT_DAP_CEILING_GBP:
        return DebtObjectionDecision(False, "prepayment debt under the Debt Assignment Protocol "
                                     f"ceiling of GBP {PREPAYMENT_DAP_CEILING_GBP:.0f} moves "
                                     "with the customer", owed)
    if (policy.de_minimis_gbp_per_fuel is not None
            and owed <= policy.de_minimis_gbp_per_fuel * max(fuels, 1)):
        return DebtObjectionDecision(False, f"GBP {owed:.2f} is within the de-minimis of GBP "
                                     f"{policy.de_minimis_gbp_per_fuel:.0f} per fuel", owed)
    record = register.raise_objection(
        supply_point_id, switch_ref, request_day, ObjectionGround.UNPAID_DEBT,
        notes=f"GBP {owed:.2f} outstanding more than {SLC14_MIN_DAYS_SINCE_NOTICE} days",
        switch_request_submitted=request_day, domestic=True)
    return DebtObjectionDecision(True, f"GBP {owed:.2f} outstanding more than "
                                 f"{SLC14_MIN_DAYS_SINCE_NOTICE} days since its bill", owed, record)
