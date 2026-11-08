"""Data Aggregator / Data Collector (DA/DC) Contract Register.

UK electricity market (BSC, Balancing and Settlement Code):
- Every metering system must have an appointed DA and DC
- Data Collector (DC): reads meters, validates data, submits to Elexon
- Data Aggregator (DA): aggregates half-hourly data for settlement
- For NHH (non-half-hourly) meters: Profile Class used, single agent often acts as DA+DC
- For HH (half-hourly) meters: separate DA/DC required

Appointment must be notified to Elexon via Market Domain Data (MDD).
Change of agent requires MTC (Meter Technical Code) compliance.

BSC Section S: Settlement metering agents
SVA (Supplier Volume Allocation): each supplier appoints DA/DC per MPAN

This register tracks which agent serves each MPAN, appointment dates,
and whether any MPANs are unregistered (appointment gap = BSC breach risk).

Epistemic: appointment is a company decision/contractual fact.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from enum import Enum


class MeteringAgentType(str, Enum):
    DA = "da"   # Data Aggregator
    DC = "dc"   # Data Collector
    DA_DC = "da_dc"  # Combined (common for NHH)
    MOA = "moa"  # Meter Operator Agent (different role but often same company)


class MeterType(str, Enum):
    NHH = "nhh"  # Non-half-hourly (Profile Classes 1-8)
    HH = "hh"   # Half-hourly (Profile Class 0)
    SMETS2 = "smets2"  # Smart meter (SMETS2; HH-capable)


@dataclass(frozen=True)
class AgentAppointment:
    mpan: str
    agent_type: MeteringAgentType
    agent_name: str
    appointment_date: date
    termination_date: date | None = None

    @property
    def is_active(self) -> bool:
        return self.termination_date is None


class DADCContractRegister:
    """Tracks DA/DC appointments per supply point."""

    _MIN_NOTICE_DAYS = 10  # BSC appointment change notice

    def __init__(self) -> None:
        self._appointments: list[AgentAppointment] = []

    def appoint(self, mpan: str, agent_type: MeteringAgentType, agent_name: str, appointment_date: date) -> AgentAppointment:
        appt = AgentAppointment(mpan=mpan, agent_type=agent_type, agent_name=agent_name, appointment_date=appointment_date)
        self._appointments.append(appt)
        return appt

    def terminate(self, mpan: str, agent_type: MeteringAgentType, termination_date: date) -> None:
        self._appointments = [
            AgentAppointment(
                mpan=a.mpan, agent_type=a.agent_type, agent_name=a.agent_name,
                appointment_date=a.appointment_date, termination_date=termination_date
            ) if a.mpan == mpan and a.agent_type == agent_type and a.is_active else a
            for a in self._appointments
        ]

    @property
    def active_appointments(self) -> list[AgentAppointment]:
        return [a for a in self._appointments if a.is_active]

    def agent_for_mpan(self, mpan: str, agent_type: MeteringAgentType) -> AgentAppointment | None:
        for a in self.active_appointments:
            if a.mpan == mpan and a.agent_type == agent_type:
                return a
        return None

    def mpans_without_dc(self) -> list[str]:
        mpans_with_dc = {a.mpan for a in self.active_appointments if a.agent_type in (MeteringAgentType.DC, MeteringAgentType.DA_DC)}
        all_mpans = {a.mpan for a in self.active_appointments}
        return sorted(all_mpans - mpans_with_dc)

    def mpans_without_da(self) -> list[str]:
        mpans_with_da = {a.mpan for a in self.active_appointments if a.agent_type in (MeteringAgentType.DA, MeteringAgentType.DA_DC)}
        all_mpans = {a.mpan for a in self.active_appointments}
        return sorted(all_mpans - mpans_with_da)

    def agents_by_name(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for a in self.active_appointments:
            result[a.agent_name] = result.get(a.agent_name, 0) + 1
        return result

    def da_dc_summary(self) -> str:
        active = self.active_appointments
        mpans = {a.mpan for a in active}
        no_dc = self.mpans_without_dc()
        no_da = self.mpans_without_da()
        return (
            "DA/DC Contract Register (BSC SVA)\n"
            "Supply points: {:d} | Active appointments: {:d}\n"
            "MPANs missing DC: {:d} | Missing DA: {:d}".format(len(mpans), len(active), len(no_dc), len(no_da))
        )
