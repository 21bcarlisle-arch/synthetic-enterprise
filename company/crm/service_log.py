"""CRM service interaction log (C4 -- Phase 69, persistent Phase 89).

Records every customer service contact: channel, reason, outcome, agent type,
complaint/vulnerability flags. Optional SQLite persistence via db_path.

Usage:
  ServiceLog()                       -- in-memory (tests, ephemeral)
  ServiceLog(db_path=DEFAULT_DB_PATH) -- persistent (production)

THIS MODULE NO LONGER SPELLS ITS OWN VULNERABILITY TERM (atom C32). It held one of the four
renderings of the supplier's vulnerability obligation, and it was the one that enumerated
nothing: `flag_type` was `str`, so the column constrained no value at all. What that bought,
measured in the live store: 4,557 active rows, one distinct `flag_type`, and that value was
`financial_difficulty` -- a term in NONE of the four vocabularies, nearest neighbour
`payment_difficulty` in the operational one. It got there as a hardcoded literal written from
`ServiceEvent.vulnerability_flag`, a BOOLEAN, which carries no term to write.

The term is now `company.crm.vulnerability_register.VulnerabilityFlag` or `None`, and `None`
is what the boolean always meant: flagged, term not recorded. Nothing downstream may read an
absence as a category.
"""

import sqlite3
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

# The ONE operational vocabulary. Imported, not restated: the defect this module carried was
# a second spelling of the same concept, and an import cannot drift from its source.
from company.crm.vulnerability_register import VulnerabilityFlag as OperationalFlag

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
    csat_score: int | None = None


@dataclass
class VulnerabilityFlag:
    """One register row: who, when, and WHICH TERM -- where a term was recorded at all.

    `flag_type` is the shared operational vocabulary or `None`. `recorded_as` keeps exactly
    what the column held, so a legacy value is preserved rather than translated away.
    """

    customer_id: str
    flagged_date: str
    flag_type: OperationalFlag | None
    active: bool = True
    resolved_date: str = ""
    recorded_as: str = ""

    @property
    def term_display(self) -> str:
        """What a surface may print. "Not recorded" is a result and belongs on the page.

        The admin register used to render `flag_type.replace('_', ' ').title()`, which
        turned an off-vocabulary string into a confident-looking English label -- 4,557 rows
        reading "Financial Difficulty" for a term nobody ever chose.
        """
        if self.flag_type is not None:
            return self.flag_type.value.replace("_", " ").title()
        if self.recorded_as:
            return "Not recorded (stored as '{:s}')".format(self.recorded_as)
        return "Not recorded"


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
        notes            TEXT NOT NULL DEFAULT '',
        csat_score       INTEGER
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
    csat = row["csat_score"] if "csat_score" in row.keys() else None
    return ServiceEvent(
        customer_id=row["customer_id"], event_date=row["event_date"],
        channel=row["channel"], contact_reason=row["contact_reason"],
        outcome=row["outcome"], agent_type=row["agent_type"],
        complaint_flag=bool(row["complaint_flag"]),
        vulnerability_flag=bool(row["vulnerability_flag"]),
        notes=row["notes"],
        csat_score=csat,
    )


def _term_from_stored(raw: str) -> OperationalFlag | None:
    """The back-compat read path, and it coerces NOTHING.

    The live store holds `financial_difficulty` on every row. It is tempting to map it to
    `PAYMENT_DIFFICULTY` -- same rough concept, one row of a dict, done. That would be this
    module taking a position the free-text column let it avoid making: the string was written
    from a boolean, so it never named a term, and `fuel_poverty`, `payment_difficulty` and
    `job_loss` are three different operational states it could equally have meant. An
    unreadable value reads as "no term", with the original kept beside it.
    """
    try:
        return OperationalFlag(raw)
    except ValueError:
        return None


def _row_to_vuln(row) -> VulnerabilityFlag:
    raw = row["flag_type"]
    return VulnerabilityFlag(
        customer_id=row["customer_id"], flagged_date=row["flagged_date"],
        flag_type=_term_from_stored(raw), active=bool(row["active"]),
        resolved_date=row["resolved_date"], recorded_as=raw,
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
        # Migrate: add csat_score column if missing (added Phase 105)
        cols = [r["name"] for r in self._conn.execute("PRAGMA table_info(service_events)")]
        if "csat_score" not in cols:
            self._conn.execute("ALTER TABLE service_events ADD COLUMN csat_score INTEGER")
        self._conn.commit()

    def _c(self):
        return self._conn

    def record_contact(
        self,
        event: ServiceEvent,
        *,
        vulnerability_term: OperationalFlag | None = None,
    ) -> None:
        """Record a contact, and a register row where the contact was flagged.

        `vulnerability_term` is keyword-only and optional because `ServiceEvent` carries a
        BOOLEAN. A caller that knows the term passes it; a caller that only ticked the box
        passes nothing and the row stores no term. The literal `financial_difficulty` that
        used to be written here was a term invented from that boolean.
        """
        c = self._c()
        c.execute(
            "INSERT INTO service_events"
            " (customer_id, event_date, channel, contact_reason, outcome,"
            "  agent_type, complaint_flag, vulnerability_flag, notes, csat_score)"
            " VALUES (?,?,?,?,?,?,?,?,?,?)",
            (event.customer_id, event.event_date, event.channel,
             event.contact_reason, event.outcome, event.agent_type,
             int(event.complaint_flag), int(event.vulnerability_flag),
             event.notes, event.csat_score),
        )
        if event.vulnerability_flag:
            c.execute(
                "INSERT INTO vulnerability_flags (customer_id, flagged_date, flag_type)"
                " VALUES (?, ?, ?)",
                (event.customer_id, event.event_date,
                 vulnerability_term.value if vulnerability_term is not None else ""),
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


    def ombudsman_eligible(self) -> list[dict]:
        """Return complaints eligible for Energy Ombudsman referral.

        A complaint is Ombudsman-eligible when resolve_overdue=True:
        it has been unresolved for more than 8 weeks.
        Suppliers are legally required to issue a 'deadlock letter'
        and signpost the Ombudsman at this point.
        """
        return [
            d for d in self.complaint_deadlines()
            if d["resolve_overdue"]
        ]

    def ombudsman_count(self) -> int:
        return len(self.ombudsman_eligible())


    def csat_summary(self) -> dict:
        """Return CSAT score summary across all rated contacts.

        Scores: 1 (very dissatisfied) to 5 (very satisfied).
        Returns count, mean, and percentage of promoters (4-5 stars).
        """
        rated = [
            e.csat_score for e in self.all_contacts()
            if e.csat_score is not None
        ]
        if not rated:
            return {"count": 0, "mean": None, "promoter_pct": None}
        promoters = sum(1 for s in rated if s >= 4)
        return {
            "count": len(rated),
            "mean": round(sum(rated) / len(rated), 2),
            "promoter_pct": round(promoters / len(rated) * 100, 1),
        }

    def rate_contact(self, event_id: int, score: int) -> bool:
        """Record a CSAT score (1-5) for a specific contact by row ID.
        Returns True if the row was found and updated."""
        if score not in range(1, 6):
            raise ValueError(f"CSAT score must be 1-5, got {score}")
        c = self._c()
        n = c.execute(
            "UPDATE service_events SET csat_score=? WHERE id=?",
            (score, event_id)
        ).rowcount
        c.commit()
        return n > 0

    def latest_contact_id(self, customer_id: str) -> int | None:
        """Return the row ID of the most recent contact for a customer."""
        row = self._c().execute(
            "SELECT id FROM service_events WHERE customer_id=? ORDER BY id DESC LIMIT 1",
            (customer_id,)
        ).fetchone()
        return row["id"] if row else None


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
