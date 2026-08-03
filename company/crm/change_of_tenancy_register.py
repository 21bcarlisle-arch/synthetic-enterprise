"""Change of Tenancy (CoT) Register (Phase GK) + the tenancy-change coupling
layer (W2_12, 2026-07-29).

When a property changes occupant (tenant moves in/moves out, property
sold, landlord re-occupying), the energy supply must transfer.
Debt is associated with the person not the property (SLC 27/SLC 12.2).
New tenant gets a fresh deemed contract supply from day 1 of possession.
Cannot withhold supply due to previous tenant debt.
Abandonment: 3 contact attempts over 28 days with no response.

W2_12 — one tenancy change, three consequences
----------------------------------------------
The director's frame for this atom, verbatim: *"every tenancy change is ONE
credit-risk exit PLUS TWO deemed-rate entries (double jeopardy), and
simultaneously the prime acquisition moment for high-value low-churn
customers."*

Every one of those consequences already had a mechanism in this codebase, and
every one of them fired INDEPENDENTLY of the others — nothing joined a move-out
to the void that follows it, to the occupant who lands after that, to whether
the departing occupant's final bill was ever paid, or to what the landed
occupant is worth. `TenancyChangeCoupler` is that join, and only that join: it
creates no register, no deemed-rate engine, no closure engine and no win-rate
model. It consumes `company/crm/life_events.py` MOVE_IN / MOVE_OUT events and
fans one tenancy change out to the mechanisms that already exist.

Why the deemed legs are TWO. A move-out does not leave the property unsupplied:
supply continues, unbilled to any named person, under what Ofgem calls the
"occupier" account — deemed leg 1, `DeemedSupplyReason.VOID_PERIOD`. When the
new occupant arrives they land on a fresh deemed contract from day 1 of
possession — deemed leg 2, `DeemedSupplyReason.NEW_TENANT`. Ofgem's 30 October
2025 debt review puts £1.1bn-£1.7bn of the UK's £4.4bn historic energy debt
inside exactly that first leg ("bills build up under these anonymous accounts
until the individual contacts a supplier to register"). Modelling one leg and
not the other is what makes the void period invisible, which is precisely the
hole the regulator found.

Epistemic position: this file is COMPANY side. It records the exit's OUTCOME
(paid / partially paid / unpaid / gone away) as observed — it never computes
one. The probability lives in `simulation/final_bill_outcome.py` behind the
wall, keyed off household truth a real supplier cannot read.

C-S1 (event-arrival tolerance) is load-bearing here, not decorative. A void
period IS "MOVE_OUT arrived, MOVE_IN has not" — an incomplete tenancy change is
the normal state, not an error. The coupler therefore assumes nothing about
batch completeness: legs may arrive singly, late, out of order (a customer who
registers only after moving in produces MOVE_IN first, which is the Ofgem
occupier case), or twice (idempotent by event id).

Fuel-agnostic throughout: changes are keyed by (supply_point_id, fuel), never
by MPAN alone. `ChangeOfTenancyRegister`'s `mpan` field name is legacy; the
coupler passes a supply point id into it.
"""
from __future__ import annotations
import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set
from regulation_commons.working_days import add_working_days

_COT_READ_DAYS = 10
_MPAS_NOTIFY_DAYS = 2
_ABANDON_ATTEMPTS = 3
_ABANDON_DAYS = 28


class CoTType(str, Enum):
    NEW_TENANT = "new_tenant"
    NEW_OWNER = "new_owner"
    LANDLORD_RETURNING = "landlord_returning"
    EMPTY_PROPERTY = "empty_property"
    VOID_PERIOD = "void_period"


class CoTStatus(str, Enum):
    NOTIFIED = "notified"
    SUPPLY_TAKEN = "supply_taken"
    SUPPLY_DECLINED = "supply_declined"
    ABANDONED = "abandoned"
    CLOSED = "closed"


_OPEN = frozenset({CoTStatus.NOTIFIED, CoTStatus.SUPPLY_TAKEN})
_TERMINAL = frozenset({CoTStatus.SUPPLY_DECLINED, CoTStatus.ABANDONED, CoTStatus.CLOSED})


@dataclass(frozen=True)
class CoTRecord:
    cot_id: str
    mpan: str
    entry_date: dt.date
    cot_type: CoTType
    status: CoTStatus = CoTStatus.NOTIFIED
    account_id: Optional[str] = None
    entry_meter_read: Optional[float] = None
    contact_attempts: int = 0
    supply_start_date: Optional[dt.date] = None
    closed_date: Optional[dt.date] = None

    @property
    def is_open(self) -> bool:
        return self.status in _OPEN

    @property
    def is_terminal(self) -> bool:
        return self.status in _TERMINAL

    @property
    def mpas_notification_due(self) -> dt.date:
        return add_working_days(self.entry_date, _MPAS_NOTIFY_DAYS)

    @property
    def read_submission_due(self) -> dt.date:
        return add_working_days(self.entry_date, _COT_READ_DAYS)

    def is_abandon_candidate(self, as_of: dt.date) -> bool:
        return (
            self.status == CoTStatus.NOTIFIED
            and self.contact_attempts >= _ABANDON_ATTEMPTS
            and (as_of - self.entry_date).days >= _ABANDON_DAYS
        )

    def cot_summary(self) -> str:
        acct = self.account_id or "unassigned"
        return (
            "CoT " + self.cot_id + " mpan=" + self.mpan
            + " [" + self.cot_type.value + "]"
            + " entry=" + str(self.entry_date)
            + " acct=" + acct
            + " [" + self.status.value + "]"
        )


class ChangeOfTenancyRegister:

    def __init__(self) -> None:
        self._records: List[CoTRecord] = []
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return "COT-" + str(self._counter).zfill(5)

    def notify_cot(
        self,
        mpan: str,
        entry_date: dt.date,
        cot_type: CoTType = CoTType.NEW_TENANT,
        entry_meter_read: Optional[float] = None,
    ) -> CoTRecord:
        record = CoTRecord(
            cot_id=self._next_id(),
            mpan=mpan,
            entry_date=entry_date,
            cot_type=cot_type,
            entry_meter_read=entry_meter_read,
        )
        self._records.append(record)
        return record

    def _update(self, cot_id: str, **kwargs) -> CoTRecord:
        for i, r in enumerate(self._records):
            if r.cot_id == cot_id:
                updated = CoTRecord(
                    cot_id=r.cot_id, mpan=r.mpan, entry_date=r.entry_date,
                    cot_type=r.cot_type,
                    status=kwargs.get("status", r.status),
                    account_id=kwargs.get("account_id", r.account_id),
                    entry_meter_read=kwargs.get("entry_meter_read", r.entry_meter_read),
                    contact_attempts=kwargs.get("contact_attempts", r.contact_attempts),
                    supply_start_date=kwargs.get("supply_start_date", r.supply_start_date),
                    closed_date=kwargs.get("closed_date", r.closed_date),
                )
                self._records[i] = updated
                return updated
        raise KeyError("CoT record " + cot_id + " not found")

    def accept_supply(self, cot_id: str, account_id: str, supply_start_date: dt.date) -> CoTRecord:
        return self._update(cot_id, status=CoTStatus.SUPPLY_TAKEN,
                           account_id=account_id, supply_start_date=supply_start_date)

    def decline_supply(self, cot_id: str) -> CoTRecord:
        return self._update(cot_id, status=CoTStatus.SUPPLY_DECLINED)

    def log_contact_attempt(self, cot_id: str) -> CoTRecord:
        for r in self._records:
            if r.cot_id == cot_id:
                return self._update(cot_id, contact_attempts=r.contact_attempts + 1)
        raise KeyError("CoT record " + cot_id + " not found")

    def mark_abandoned(self, cot_id: str) -> CoTRecord:
        return self._update(cot_id, status=CoTStatus.ABANDONED)

    def close(self, cot_id: str, closed_date: dt.date) -> CoTRecord:
        return self._update(cot_id, status=CoTStatus.CLOSED, closed_date=closed_date)

    def open_cots(self) -> List[CoTRecord]:
        return [r for r in self._records if r.is_open]

    def abandon_candidates(self, as_of: dt.date) -> List[CoTRecord]:
        return [r for r in self._records if r.is_abandon_candidate(as_of)]

    def history_for_mpan(self, mpan: str) -> List[CoTRecord]:
        return [r for r in self._records if r.mpan == mpan]

    def active_supply_for_mpan(self, mpan: str) -> Optional[CoTRecord]:
        taken = [r for r in self._records if r.mpan == mpan and r.status == CoTStatus.SUPPLY_TAKEN]
        return max(taken, key=lambda r: r.entry_date) if taken else None

    def by_type(self, cot_type: CoTType) -> List[CoTRecord]:
        return [r for r in self._records if r.cot_type == cot_type]

    def conversion_rate_pct(self) -> Optional[float]:
        taken = sum(1 for r in self._records if r.status == CoTStatus.SUPPLY_TAKEN)
        terminal = sum(1 for r in self._records if r.is_terminal)
        if terminal == 0:
            return None
        return round(taken / (taken + terminal) * 100, 1)

    def cot_summary(self, as_of: dt.date) -> str:
        n = len(self._records)
        n_open = len(self.open_cots())
        n_abandon = len(self.abandon_candidates(as_of))
        cr = self.conversion_rate_pct()
        cr_str = (str(cr) + "%") if cr is not None else "n/a"
        return (
            "CoT Register (" + str(as_of) + "): " + str(n) + " CoTs ("
            + str(n_open) + " open, " + str(n_abandon) + " abandon candidates). "
            + "Conversion: " + cr_str + "."
        )


# ===========================================================================
# W2_12 — the tenancy-change coupling layer.
# ===========================================================================


class DeemedLeg(str, Enum):
    """The two deemed-rate entries of the director's "double jeopardy"."""

    VOID_OCCUPIER = "void_occupier"   # supply continues, nobody named — Ofgem's "occupier" account
    NEW_OCCUPANT = "new_occupant"     # fresh deemed contract from day 1 of possession


class ExitOutcome(str, Enum):
    """Observed result of the departing occupant's final bill. Values mirror
    `company.billing.account_closure.FinalBillOutcome` by VALUE (typed message,
    not a shared object)."""

    PENDING = "pending"               # C-S3: not resolvable yet, and that is not "paid"
    CREDIT_DUE = "credit_due"
    PAID_ON_TIME = "paid_on_time"
    PAID_LATE = "paid_late"
    PARTIALLY_PAID = "partially_paid"
    UNPAID = "unpaid"

    @property
    def is_shortfall(self) -> bool:
        return self in (ExitOutcome.PARTIALLY_PAID, ExitOutcome.UNPAID)


class AcquisitionOutcome(str, Enum):
    PENDING = "pending"
    WON = "won"
    LOST = "lost"


@dataclass
class TenancyChange:
    """One tenancy change: an exit leg, up to two deemed legs, one acquisition.

    Either leg may be absent. `move_out_date is None` means the incoming
    occupant registered without us ever seeing the outgoing one; `move_in_date
    is None` means the property is still void. Neither is an error state.
    """

    change_id: str
    supply_point_id: str
    fuel: str
    move_out_date: Optional[dt.date] = None
    move_in_date: Optional[dt.date] = None
    outgoing_account_id: Optional[str] = None
    incoming_account_id: Optional[str] = None

    # --- exit leg (credit risk)
    exit_balance_gbp: float = 0.0
    exit_outcome: ExitOutcome = ExitOutcome.PENDING
    exit_resolved_on: Optional[dt.date] = None
    exit_recovered_gbp: float = 0.0
    gone_away: bool = False

    # --- acquisition leg
    acquisition_outcome: AcquisitionOutcome = AcquisitionOutcome.PENDING
    occupant_clv_gbp: float = 0.0

    cot_id: Optional[str] = None
    _event_ids: Set[str] = field(default_factory=set, repr=False)

    # -- leg completeness (C-S1) ------------------------------------------
    @property
    def has_exit(self) -> bool:
        return self.move_out_date is not None

    @property
    def has_entry(self) -> bool:
        return self.move_in_date is not None

    @property
    def is_complete(self) -> bool:
        return self.has_exit and self.has_entry

    @property
    def is_void(self) -> bool:
        """Move-out seen, move-in not. The Ofgem "occupier" account window."""
        return self.has_exit and not self.has_entry

    def void_days(self, as_of: dt.date) -> Optional[int]:
        """Days the property has been (or was) void.

        None when we never saw the move-out — we genuinely do not know when the
        void started, and inventing a start date would be the company reading
        something it cannot see.
        """
        if not self.has_exit:
            return None
        end = self.move_in_date or as_of
        return max(0, (end - self.move_out_date).days)

    # -- the two deemed entries -------------------------------------------
    def deemed_legs(self) -> List[DeemedLeg]:
        """The deemed-rate entries this change has actually generated so far.

        Two once both legs are known — the director's "TWO deemed-rate
        entries". One while void, or when only the entry was ever observed.
        """
        legs: List[DeemedLeg] = []
        if self.has_exit:
            legs.append(DeemedLeg.VOID_OCCUPIER)
        if self.has_entry:
            legs.append(DeemedLeg.NEW_OCCUPANT)
        return legs

    def deemed_start(self, leg: DeemedLeg) -> Optional[dt.date]:
        return self.move_out_date if leg is DeemedLeg.VOID_OCCUPIER else self.move_in_date

    # -- outcomes ----------------------------------------------------------
    @property
    def exit_shortfall_gbp(self) -> float:
        """Observed money not recovered. 0.0 while PENDING — an unresolved exit
        is not a loss; callers wanting "unknown" check `exit_outcome`."""
        if self.exit_outcome is ExitOutcome.PENDING:
            return 0.0
        return round(max(0.0, self.exit_balance_gbp - self.exit_recovered_gbp), 2)

    @property
    def exit_exposure_gbp(self) -> float:
        """Money at risk on an exit we have not had an answer on yet (C-S3)."""
        if self.exit_outcome is not ExitOutcome.PENDING:
            return 0.0
        return round(max(0.0, self.exit_balance_gbp), 2)

    @property
    def is_double_jeopardy(self) -> bool:
        """The director's frame realised in one change: we lost money on the
        way out AND carried deemed-rate supply on the way back in."""
        return self.exit_outcome.is_shortfall and len(self.deemed_legs()) >= 1

    @property
    def net_value_gbp(self) -> float:
        """What this tenancy change was worth: the CLV of whoever we landed,
        less what the departing occupant never paid."""
        won = self.acquisition_outcome is AcquisitionOutcome.WON
        return round((self.occupant_clv_gbp if won else 0.0) - self.exit_shortfall_gbp, 2)


class TenancyChangeCoupler:
    """Joins MOVE_OUT/MOVE_IN life events into tenancy changes and fans each
    one out to the mechanisms that already exist.

    Optionally wired to a `ChangeOfTenancyRegister`: when supplied, an observed
    move raises the corresponding CoT register entry (VOID_PERIOD on the way
    out, NEW_TENANT on the way in) instead of the caller having to remember to
    do it separately — that forgetting is the coupling gap this class closes.
    """

    def __init__(self, register: Optional[ChangeOfTenancyRegister] = None) -> None:
        self._changes: Dict[str, TenancyChange] = {}
        self._by_key: Dict[tuple, List[str]] = {}
        self._counter = 0
        self._register = register

    def _next_id(self) -> str:
        self._counter += 1
        return "TC-" + str(self._counter).zfill(5)

    def _open_change(self, supply_point_id: str, fuel: str) -> TenancyChange:
        change = TenancyChange(
            change_id=self._next_id(), supply_point_id=supply_point_id, fuel=fuel
        )
        self._changes[change.change_id] = change
        self._by_key.setdefault((supply_point_id, fuel), []).append(change.change_id)
        return change

    def _changes_for(self, supply_point_id: str, fuel: str) -> List[TenancyChange]:
        return [self._changes[cid] for cid in self._by_key.get((supply_point_id, fuel), [])]

    def _seen(self, event_id: Optional[str]) -> Optional[TenancyChange]:
        """C-S2 idempotency: a replayed event id is a no-op, returning the
        change it already landed on rather than opening a duplicate."""
        if event_id is None:
            return None
        for change in self._changes.values():
            if event_id in change._event_ids:
                return change
        return None

    # -- ingestion (C-S1: singly, late, out of order, duplicated) ----------

    def observe_move_out(
        self,
        supply_point_id: str,
        fuel: str,
        move_out_date: dt.date,
        account_id: Optional[str] = None,
        exit_balance_gbp: float = 0.0,
        event_id: Optional[str] = None,
    ) -> TenancyChange:
        """Record the departing occupant. Opens the void (deemed leg 1)."""
        already = self._seen(event_id)
        if already is not None:
            return already

        # Attach to an existing change that is still missing its exit leg and
        # whose entry (if known) is not BEFORE this move-out — that is the
        # out-of-order case where MOVE_IN was observed first.
        target = None
        for change in self._changes_for(supply_point_id, fuel):
            if change.has_exit:
                continue
            if change.move_in_date is not None and change.move_in_date < move_out_date:
                continue
            target = change
            break
        if target is None:
            target = self._open_change(supply_point_id, fuel)

        target.move_out_date = move_out_date
        target.outgoing_account_id = account_id
        target.exit_balance_gbp = round(exit_balance_gbp, 2)
        if event_id is not None:
            target._event_ids.add(event_id)

        if self._register is not None and target.cot_id is None:
            record = self._register.notify_cot(
                supply_point_id, move_out_date, CoTType.VOID_PERIOD
            )
            target.cot_id = record.cot_id
        return target

    def observe_move_in(
        self,
        supply_point_id: str,
        fuel: str,
        move_in_date: dt.date,
        account_id: Optional[str] = None,
        cot_type: CoTType = CoTType.NEW_TENANT,
        event_id: Optional[str] = None,
    ) -> TenancyChange:
        """Record the arriving occupant. Raises deemed leg 2 and opens the
        acquisition moment.

        If no move-out was ever observed for this supply point, a change is
        opened with an entry leg only — the customer who registers after
        already living there (Ofgem's "occupier" case), not an error.
        """
        already = self._seen(event_id)
        if already is not None:
            return already

        target = None
        for change in self._changes_for(supply_point_id, fuel):
            if change.has_entry:
                continue
            if change.move_out_date is not None and change.move_out_date > move_in_date:
                continue
            target = change
            break
        if target is None:
            target = self._open_change(supply_point_id, fuel)

        target.move_in_date = move_in_date
        target.incoming_account_id = account_id
        if event_id is not None:
            target._event_ids.add(event_id)

        if self._register is not None:
            if target.cot_id is None:
                record = self._register.notify_cot(supply_point_id, move_in_date, cot_type)
                target.cot_id = record.cot_id
            if account_id is not None:
                self._register.accept_supply(target.cot_id, account_id, move_in_date)
        return target

    # -- outcome observation ------------------------------------------------

    def record_exit_outcome(
        self,
        change_id: str,
        outcome: ExitOutcome,
        resolved_on: dt.date,
        recovered_gbp: float = 0.0,
        gone_away: bool = False,
    ) -> TenancyChange:
        """Record what we OBSERVED happened to the final bill.

        The company never computes this; it arrives from the world side via
        `company.billing.account_closure.record_final_bill_outcome()`, whose
        wall guard has already rejected anything non-observable.
        """
        change = self._changes[change_id]
        change.exit_outcome = outcome
        change.exit_resolved_on = resolved_on
        change.exit_recovered_gbp = round(recovered_gbp, 2)
        change.gone_away = gone_away
        return change

    def record_acquisition_outcome(
        self, change_id: str, won: bool, occupant_clv_gbp: float = 0.0
    ) -> TenancyChange:
        """Record whether we kept the property's supply, and what the landed
        occupant is worth (`saas.home_move_win_rate.home_move_acquisition_value`
        supplies the expectation; this records the realisation)."""
        change = self._changes[change_id]
        change.acquisition_outcome = (
            AcquisitionOutcome.WON if won else AcquisitionOutcome.LOST
        )
        change.occupant_clv_gbp = round(occupant_clv_gbp if won else 0.0, 2)
        if self._register is not None and change.cot_id is not None and not won:
            self._register.decline_supply(change.cot_id)
        return change

    # -- views --------------------------------------------------------------

    def get(self, change_id: str) -> TenancyChange:
        return self._changes[change_id]

    def all_changes(self) -> List[TenancyChange]:
        return list(self._changes.values())

    def void_properties(self, as_of: dt.date) -> List[TenancyChange]:
        return [c for c in self._changes.values() if c.is_void]

    def awaiting_exit_outcome(self) -> List[TenancyChange]:
        return [
            c for c in self._changes.values()
            if c.has_exit and c.exit_outcome is ExitOutcome.PENDING and c.exit_balance_gbp > 0
        ]

    def double_jeopardy_summary(self, as_of: dt.date) -> dict:
        """The director's frame, measured.

        `exit_exposure_gbp` (unanswered) is reported separately from
        `exit_shortfall_gbp` (observed loss) so an unresolved exit is never
        silently booked as either.
        """
        changes = list(self._changes.values())
        void = [c for c in changes if c.is_void]
        void_days = [c.void_days(as_of) for c in void]
        won = [c for c in changes if c.acquisition_outcome is AcquisitionOutcome.WON]
        return {
            "as_of": as_of.isoformat(),
            "tenancy_changes": len(changes),
            "complete": sum(1 for c in changes if c.is_complete),
            "void_now": len(void),
            "mean_void_days": (round(sum(void_days) / len(void_days), 1) if void_days else None),
            "deemed_legs": sum(len(c.deemed_legs()) for c in changes),
            "exit_exposure_gbp": round(sum(c.exit_exposure_gbp for c in changes), 2),
            "exit_shortfall_gbp": round(sum(c.exit_shortfall_gbp for c in changes), 2),
            "gone_away": sum(1 for c in changes if c.gone_away),
            "double_jeopardy": sum(1 for c in changes if c.is_double_jeopardy),
            "acquisitions_won": len(won),
            "acquired_clv_gbp": round(sum(c.occupant_clv_gbp for c in won), 2),
            "net_value_gbp": round(sum(c.net_value_gbp for c in changes), 2),
        }
