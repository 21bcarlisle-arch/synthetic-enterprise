"""CRM service interaction log (C4 -- Phase 69, persistent Phase 89).

Records every customer service contact: channel, reason, outcome, agent type,
complaint/vulnerability flags. Optional SQLite persistence via db_path.

Usage:
  ServiceLog()                       -- in-memory (tests, ephemeral)
  ServiceLog(db_path=DEFAULT_DB_PATH) -- persistent (production)
"""

import sqlite3
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

DEFAULT_DB_PATH = Path("company/data/service_log.db")


@dataclass
class ServiceEvent:
    customer_id: str
    event_date: str
    channel: str
    contact_reason: str
    outcome: str
    agent_type: str = "ai"
    complaint_flag: bool = False
    vulnerability_flag: bool = False
    notes: str = ""


@dataclass
class VulnerabilityFlag:
    customer_id: str
    flagged_date: str
    flag_type: str
    active: bool = True
    resolved_date: str = ""


_CREATE_EVENTS = """
    CREATE TABLE IF NOT EXISTS service_events (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id      TEXT NOT NULL,
        event_date       TEXT NOT NULL,
        channel          TEXT NOT NULL,
        contact_reason   TEXT NOT NULL,
        outcome          TEXT NOT NULL,
        agent_type       TEXT NOT NULL DEFAULT 'ai',
        complaint_flag   INTEGER NOT NULL DEFAULT 0,
        vulnerability_flag INTEGER NOT NULL DEFAULT 0,
        notes            TEXT NOT NULL DEFAULT ''
    )
"""

_CREATE_VULNS = """
    CREATE TABLE IF NOT EXISTS vulnerability_flags (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id      TEXT NOT NULL,
        flagged_date     TEXT NOT NULL,
        flag_type        TEXT NOT NULL,
        active           INTEGER NOT NULL DEFAULT 1,
        resolved_date    TEXT NOT NULL DEFAULT ''
    )
"""


def _row_to_event(row) -> ServiceEvent:
    return ServiceEvent(
        customer_id=row["customer_id"], event_date=row["event_date"],
        channel=row["channel"], contact_reason=row["contact_reason"],
        outcome=row["outcome"], agent_type=row["agent_type"],
        complaint_flag=bool(row["complaint_flag"]),
        vulnerability_flag=bool(row["vulnerability_flag"]),
        notes=row["notes"],
    )


def _row_to_vuln(row) -> VulnerabilityFlag:
    return VulnerabilityFlag(
        customer_id=row["customer_id"], flagged_date=row["flagged_date"],
        flag_type=row["flag_type"], active=bool(row["active"]),
        resolved_date=row["resolved_date"],
    )


def _add_working_days(start: date, n: int) -> date:
    """Add n working days (Mon-Fri) to start date."""
    d = start
    added = 0
    while added < n:
        d += timedelta(days=1)
        if d.weekday() < 5:  # 0=Mon, 4=Fri
            added += 1
    return d


class ServiceLog:
    """Append-only service interaction log with optional SQLite persistence.

    ServiceLog()              -- in-memory SQLite (ephemeral; each instance is independent)
    ServiceLog(db_path=path)  -- persistent file-backed SQLite
    """

    def __init__(self, db_path: Path | None = None):
        if db_path is not None:
            db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        else:
            self._conn = sqlite3.connect(":memory:")
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(_CREATE_EVENTS)
        self._conn.execute(_CREATE_VULNS)
        self._conn.commit()

    def _c(self):
        return self._conn

    def record_contact(self, event: ServiceEvent) -> None:
        c = self._c()
        c.execute(
            "INSERT INTO service_events"
            " (customer_id, event_date, channel, contact_reason, outcome,"
            "  agent_type, complaint_flag, vulnerability_flag, notes)"
            " VALUES (?,?,?,?,?,?,?,?,?)",
            (event.customer_id, event.event_date, event.channel,
             event.contact_reason, event.outcome, event.agent_type,
             int(event.complaint_flag), int(event.vulnerability_flag),
             event.notes),
        )
        if event.vulnerability_flag:
            c.execute(
                "INSERT INTO vulnerability_flags (customer_id, flagged_date, flag_type)"
                " VALUES (?, ?, ?)",
                (event.customer_id, event.event_date, "financial_difficulty"),
            )
        c.commit()

    def all_contacts(self) -> list[ServiceEvent]:
        return [_row_to_event(r) for r in self._c().execute("SELECT * FROM service_events")]

    def contacts_for_customer(self, customer_id: str) -> list[ServiceEvent]:
        return [_row_to_event(r) for r in self._c().execute(
            "SELECT * FROM service_events WHERE customer_id = ?", (customer_id,)
        )]

    def complaints(self) -> list[ServiceEvent]:
        return [_row_to_event(r) for r in self._c().execute(
            "SELECT * FROM service_events WHERE complaint_flag = 1"
        )]

    def complaint_rate(self) -> float:
        c = self._c()
        total = c.execute("SELECT COUNT(*) FROM service_events").fetchone()[0]
        comp = c.execute("SELECT COUNT(*) FROM service_events WHERE complaint_flag=1").fetchone()[0]
        return comp / total if total else 0.0

    def complaint_stats(self, year: int | None = None) -> dict:
        c = self._c()
        if year is not None:
            yr = str(year)
            total = c.execute(
                "SELECT COUNT(*) FROM service_events WHERE event_date LIKE ?", (yr + "%",)
            ).fetchone()[0]
            comp = c.execute(
                "SELECT COUNT(*) FROM service_events WHERE complaint_flag=1 AND event_date LIKE ?",
                (yr + "%",),
            ).fetchone()[0]
        else:
            total = c.execute("SELECT COUNT(*) FROM service_events").fetchone()[0]
            comp = c.execute("SELECT COUNT(*) FROM service_events WHERE complaint_flag=1").fetchone()[0]
        return {
            "total_contacts": total,
            "total_complaints": comp,
            "complaint_rate": round(comp / total, 4) if total else 0.0,
        }

    def vulnerability_register(self) -> list[VulnerabilityFlag]:
        return [_row_to_vuln(r) for r in self._c().execute(
            "SELECT * FROM vulnerability_flags WHERE active = 1"
        )]

    def resolve_vulnerability(self, customer_id: str, resolved_date: str) -> int:
        c = self._c()
        n = c.execute(
            "UPDATE vulnerability_flags SET active=0, resolved_date=?"
            " WHERE customer_id=? AND active=1",
            (resolved_date, customer_id),
        ).rowcount
        c.commit()
        return n

    # --- Complaint deadline tracking ---

    def complaint_deadlines(self) -> list[dict]:
        """Compute Ofgem complaint deadlines for all complaint events.

        Acknowledgement: 2 working days from contact.
        Final response: 8 weeks from contact.
        """
        results = []
        for ev in self.complaints():
            contact = date.fromisoformat(ev.event_date)
            ack_by = _add_working_days(contact, 2)
            resolve_by = contact + timedelta(weeks=8)
            resolved = ev.outcome in ("resolved", "closed")
            today = date.today()
            results.append({
                "customer_id": ev.customer_id,
                "contact_date": ev.event_date,
                "contact_reason": ev.contact_reason,
                "outcome": ev.outcome,
                "acknowledge_by": ack_by.isoformat(),
                "resolve_by": resolve_by.isoformat(),
                "resolved": resolved,
                "ack_overdue": (not resolved) and today > ack_by,
                "resolve_overdue": (not resolved) and today > resolve_by,
            })
        return results


    def as_dicts(self) -> list[dict]:
        return [
            {
                "event_type": "service_contact",
                "customer_id": e.customer_id,
                "event_date": e.event_date,
                "channel": e.channel,
                "contact_reason": e.contact_reason,
                "outcome": e.outcome,
                "agent_type": e.agent_type,
                "complaint_flag": e.complaint_flag,
                "vulnerability_flag": e.vulnerability_flag,
                "notes": e.notes,
            }
            for e in self.all_contacts()
        ]
