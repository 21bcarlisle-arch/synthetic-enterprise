#!/usr/bin/env python3
"""THE LAB: SQL-shaped access to the company's own committed truth
(atom `G13_projection_consumers`, deliverable 3 of DIRECTOR_INSTRUCTION_QUERYABLE_
PROJECTIONS_2026-08-10 -- "the advisor's lab and the director's exploration get SQL-shaped
access to the company's own truth").

    python3 -m tools.lab_query --list                  # the named questions
    python3 -m tools.lab_query blocked-deps            # answer one
    python3 -m tools.lab_query wip --json
    python3 -m tools.lab_query --sql "SELECT lane, COUNT(*) FROM atoms GROUP BY lane"

REUSE: tools/lab_query.py
CLASS: CUSTOM
INDEX: searched "query", "sql", "store", "lab", "advisor".
       `tools/build_projections.py` (G12) is REUSED WHOLE for both the rebuild and the
       read-only connection; this module holds no schema knowledge beyond the SQL text of its
       own questions and computes nothing the store does not already carry.
       `tools/build_projections.py --query` exists and is NOT what this is: that is a raw
       escape hatch with no rebuild, no staleness discipline and no named questions. It stays
       as the builder's own debug path; this is the consumer.

WHY NAMED QUESTIONS AND NOT JUST A SQL PROMPT
---------------------------------------------
A bare SQL prompt makes every reader re-derive the same joins, and a join re-derived by hand
is where a wrong answer comes from -- `depends_on` is a JSON array in a TEXT column, and the
obvious `LIKE '%X%'` against it is wrong for any atom id that is a prefix of another. The
named questions carry the joins once, correctly, and `--sql` stays open for everything else.

THE STORE IS REBUILT BEFORE EVERY ANSWER, AND THERE IS NO FLAG TO SKIP IT
------------------------------------------------------------------------
A lab that answers today's question off last week's store is the derived-artefact-staleness
disease with a query interface bolted on. So every invocation rebuilds first (0.3s, from
committed blobs only), and if the rebuild fails closed the query fails closed with it -- an
UNKNOWN source is never answered as an empty result set. There is deliberately no
`--no-rebuild`: that door is the whole defect wearing a flag (G12's own words about
`--allow-unknown`, and the same reasoning applies here).

`--rev` is NOT that door. It derives the store from a NAMED commit and every answer is
stamped with the sha it came from, so asking "what did the board look like at X" is a
different question honestly labelled, not the current question answered stale.

READ-ONLY IS ENFORCED TWICE, ON PURPOSE
---------------------------------------
The connection is opened `mode=ro` (SQLite refuses the write at the driver), AND the statement
text must be a single `SELECT`/`WITH` with no second statement. Either alone would do for an
honest caller; the pair is what stops `ATTACH`-shaped mischief reaching a file outside the
store. Nothing here can write to the store even if it tried -- and if it could, the next
rebuild would destroy the edit anyway (G12 property 2).
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path

from tools import build_projections as bp

PROJECT = Path(__file__).resolve().parents[1]

#: A statement we will run: one SELECT (or CTE), nothing after it. Comments and semicolons
#: that would chain a second statement are refused rather than stripped -- stripping is how a
#: sanitiser becomes the bypass.
_READ_ONLY = re.compile(r"^\s*(?:SELECT|WITH)\b", re.IGNORECASE)


class NotReadOnly(Exception):
    """The statement is not a single read."""


@dataclass(frozen=True)
class LabQuestion:
    """One real question, its SQL, and what an answer means."""

    name: str
    question: str
    sql: str
    columns: tuple[str, ...]
    reading: str


QUESTIONS: tuple[LabQuestion, ...] = (
    LabQuestion(
        name="wip",
        question="How much work is in progress, by loop_stage?",
        sql="SELECT loop_stage, COUNT(*) FROM atoms GROUP BY loop_stage ORDER BY COUNT(*) DESC",
        columns=("loop_stage", "atoms"),
        reading="Inventory, not velocity. A large `build` bucket is a queue, not progress.",
    ),
    LabQuestion(
        name="shortfall",
        question="Which lane carries the most undelivered level (target minus current)?",
        sql=(
            "SELECT lane, SUM(level_target - level_current) AS shortfall, COUNT(*) AS atoms "
            "FROM atoms WHERE level_target > level_current "
            "GROUP BY lane ORDER BY shortfall DESC"
        ),
        columns=("lane", "shortfall", "atoms"),
        reading="A DIAL (R12): shortfall ranks where work remains, it is never a thing to drive to zero.",
    ),
    LabQuestion(
        name="blocked-deps",
        question="Which build-stage atoms depend on an atom that has not reached level 2?",
        # `depends_on` is a JSON array in a TEXT column. json_each is the correct join;
        # a LIKE against the raw text mis-matches every id that is a prefix of another.
        sql=(
            "SELECT a.id, a.lane, dep.value AS depends_on, d.level_current AS dep_level "
            "FROM atoms a "
            "JOIN json_each(a.depends_on) dep "
            "JOIN atoms d ON d.id = dep.value "
            "WHERE a.loop_stage = 'build' AND d.level_current < 2 "
            "ORDER BY a.lane, a.id"
        ),
        columns=("atom", "lane", "depends_on", "dep_level"),
        reading="Each row is an atom the draw can pick whose ground is not yet built under it.",
    ),
    LabQuestion(
        name="unhardened",
        question="Which atoms sit AT their target level having never faced an Expert Hour?",
        sql=(
            "SELECT lane, COUNT(*) AS atoms FROM atoms "
            "WHERE level_current >= level_target AND level_current > 0 "
            "AND expert_hour_status = 'not_attempted' "
            "GROUP BY lane ORDER BY atoms DESC"
        ),
        columns=("lane", "atoms"),
        reading="Level reached is a self-certification; an unattempted Expert Hour means nobody has tried to break it.",
    ),
    LabQuestion(
        name="gap",
        question="Where is the company's belief furthest from the world's truth?",
        sql=(
            "SELECT atom_id, twin_atom_id, metric, gap, measured_at FROM coupled_gaps "
            "ORDER BY ABS(COALESCE(gap, 0)) DESC LIMIT 10"
        ),
        columns=("atom", "twin", "metric", "gap", "measured_at"),
        reading="The COUPLED TRIAD score. A gap is allowed to be large; it is not allowed to be unmeasured.",
    ),
    LabQuestion(
        name="runs",
        question="What has net margin done across the last ten recorded runs?",
        sql=(
            "SELECT position, generated_at, net_margin_pct, total_churned, survived "
            "FROM runs ORDER BY position DESC LIMIT 10"
        ),
        columns=("position", "generated_at", "net_margin_pct", "churned", "survived"),
        reading="R12: margin is a DIAGNOSTIC. A move out of band is a cue to diagnose (R4), never to tune.",
    ),
    LabQuestion(
        name="envelope",
        question="What size of book has actually been measured, and where does it tear?",
        sql=(
            "SELECT seam, role, ceiling_customers, graduation_trigger_customers, "
            "observed_tear_n, tear_outcome, mem_cap_mb FROM scale_envelope ORDER BY role"
        ),
        columns=("seam", "role", "ceiling", "graduation_trigger", "tear_at", "tear_outcome", "mem_cap_mb"),
        reading="Read from the AO12 probe's own report, never re-derived. Postgres at product-time stays ruled.",
    ),
    LabQuestion(
        name="sources",
        question="What did the store actually read, and did every source come back?",
        sql="SELECT name, path, status, row_count FROM source_status ORDER BY name",
        columns=("source", "path", "status", "rows"),
        reading="A source that is not `ok` means the store failed closed and this answer is from the PREVIOUS build.",
    ),
)

BY_NAME = {q.name: q for q in QUESTIONS}


def assert_read_only(sql: str) -> None:
    """Raise unless `sql` is a single SELECT/WITH statement."""
    if not _READ_ONLY.match(sql):
        raise NotReadOnly("only SELECT / WITH statements are allowed in the lab")
    # One statement. A trailing `;` is fine; anything after it is a second statement.
    if sql.strip().rstrip(";").count(";"):
        raise NotReadOnly("only ONE statement is allowed -- a second statement is refused, not stripped")


def run_sql(sql: str, repo: Path | None = None, rev: str = "HEAD") -> tuple[list[tuple], dict]:
    """Rebuild the store from `rev`, then answer `sql`. Returns (rows, store provenance).

    Raises `bp.SourceUnreadable` if the rebuild fails closed -- an UNKNOWN source is never
    answered as an empty result set.
    """
    assert_read_only(sql)
    repo = PROJECT if repo is None else repo

    report = bp.build(repo=repo, rev=rev)
    if report.get("status") != "ok":
        unknown = ", ".join(f"{u['name']} ({u['path']}): {u['reason']}" for u in report.get("unknown", []))
        raise bp.SourceUnreadable(f"store rebuild failed closed -- {unknown or 'no reason recorded'}")

    store = repo / bp.STORE_RELPATH
    conn = sqlite3.connect(f"file:{store}?mode=ro", uri=True)
    try:
        rows = list(conn.execute(sql))
        meta = dict(conn.execute("SELECT key, value FROM build_meta"))
    finally:
        conn.close()
    return rows, dict(head_sha=meta.get("head_sha"), rev=rev,
                      head_committed_at=meta.get("head_committed_at"))


def ask(name: str, repo: Path | None = None, rev: str = "HEAD") -> dict:
    """Answer one named question. The answer carries the sha it is true of (R14)."""
    if name not in BY_NAME:
        raise KeyError(f"no such question: {name} (try --list)")
    q = BY_NAME[name]
    rows, provenance = run_sql(q.sql, repo=repo, rev=rev)
    return dict(
        name=q.name,
        question=q.question,
        columns=list(q.columns),
        rows=[list(r) for r in rows],
        reading=q.reading,
        store=provenance,
    )


def _render(answer: dict) -> str:
    out = [answer["question"], ""]
    cols = answer["columns"]
    rows = answer["rows"]
    if not rows:
        out.append("(no rows — the query ran and matched nothing; this is not an unread source, "
                   "see `sources`)")
    else:
        widths = [max(len(str(c)), *(len(str(r[i])) for r in rows)) for i, c in enumerate(cols)]
        out.append("  ".join(str(c).ljust(w) for c, w in zip(cols, widths)))
        out.append("  ".join("-" * w for w in widths))
        for r in rows:
            out.append("  ".join(str("" if v is None else v).ljust(w) for v, w in zip(r, widths)))
    out += ["", f"— {answer['reading']}",
            f"— answered off the projection store at {str(answer['store']['head_sha'])[:9]} "
            f"({answer['store']['rev']}), rebuilt from committed blobs for this query"]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("question", nargs="?", help="a named question (see --list)")
    ap.add_argument("--list", action="store_true", help="list the named questions")
    ap.add_argument("--sql", metavar="SQL", help="a single read-only SELECT/WITH of your own")
    ap.add_argument("--json", action="store_true", help="emit the answer as JSON")
    ap.add_argument("--rev", default="HEAD", help="derive the store from this commit (default: HEAD)")
    args = ap.parse_args(argv)

    if args.list or (not args.question and not args.sql):
        for q in QUESTIONS:
            print(f"{q.name:<14} {q.question}")
        return 0

    try:
        if args.sql:
            rows, provenance = run_sql(args.sql, rev=args.rev)
            answer = dict(name="--sql", question=args.sql,
                          columns=[f"c{i}" for i in range(len(rows[0]))] if rows else [],
                          rows=[list(r) for r in rows],
                          reading="Your own statement; nothing here interpreted it.",
                          store=provenance)
        else:
            answer = ask(args.question, rev=args.rev)
    except NotReadOnly as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    except KeyError as exc:
        print(str(exc).strip('"'), file=sys.stderr)
        return 2
    except (bp.SourceUnreadable, sqlite3.Error) as exc:
        print(f"FAILED CLOSED -- {exc}", file=sys.stderr)
        return 2

    print(json.dumps(answer, indent=2) if args.json else _render(answer))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
