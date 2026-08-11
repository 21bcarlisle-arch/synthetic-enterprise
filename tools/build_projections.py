#!/usr/bin/env python3
"""Rebuild the internal query store from COMMITTED truth (atom `G12_queryable_projections`).

    python3 tools/build_projections.py                    # rebuild the store
    python3 tools/build_projections.py --report           # rebuild, then emit the build report as JSON
    python3 tools/build_projections.py --query "SELECT ..."  # read the store back

WHAT THIS IS, AND WHAT IT IS DELIBERATELY NOT
---------------------------------------------
This is a *projection* store: a single SQLite file derived from artefacts that are
already the book of record, rebuilt from scratch on every run. It is never a second
source of truth, because it cannot outlive one rebuild. Three properties carry that,
and each is proven by a mutation test in `tests/tools/test_build_projections.py`:

1. **COMMITTED, not working-tree.** Every source is read with `git cat-file blob
   HEAD:<path>` — never off disk. A source edited but not committed does not reach the
   store. This is the fail-open shape the capability index already fell into (an index
   that reads the working tree grades a thing nobody else can see).

2. **REBUILT, not mutated.** `_open_new_store()` opens a brand-new database beside the
   store and the finished file is swapped in with `os.replace`. Nothing ever opens the
   live store for writing, so a hand-edit to it survives exactly until the next build.

3. **FAIL-CLOSED, not empty.** A source that cannot be read, parsed, or that is missing
   a field a projection needs, is an UNKNOWN — recorded as such, and the build REFUSES
   to promote. It never publishes that source's table as zero rows, which would read
   downstream as "measured, and there is nothing there". There is deliberately no
   `--allow-unknown`: a door like that is the whole defect, wearing a flag.

SCOPE (`docs/staging/in_progress/DIRECTOR_INSTRUCTION_QUERYABLE_PROJECTIONS_2026-08-10.md`
is the anchor of record — the `DATA_LAKE_OBSERVABILITY.md` it cites has never existed in
this repo). INTERNAL queryability only. This does not contradict
`docs/architecture/SAAS_COVERAGE_MAP.md`'s bucket-A row eliminating BI/data-warehouse:
that row's claim is that board-grade analytics need no separate warehouse/ETL, and it
stays true as written — `tools/generate_dashboard_data.py` still computes every published
figure directly off the operational model, and nothing here feeds a published figure.
See `docs/design/simplifications/G12_queryable_projections.yaml` for that reconciliation.

THE SCALE ENVELOPE IS READ, NEVER RE-DERIVED
--------------------------------------------
`scale_envelope` is copied verbatim out of the AO12 10k probe's own report artefact
(`docs/design/scale_probe_10k_report.json`). This module computes no scale figure of its
own and holds no ceiling constant; a missing field there fails the build closed rather
than defaulting, because a stage the probe never reached is an UNKNOWN cost and not a
zero. Postgres at product-time stays ruled: the graduation trigger is recorded here so
the decision is made against a measurement, not a feeling.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
STORE_RELPATH = Path("docs/observability/projections.sqlite")

#: The probe artefact whose MEASURED figures set the envelope. Read, never re-derived.
SCALE_PROBE_RELPATH = "docs/design/scale_probe_10k_report.json"

#: The seam whose measurements bound THIS store. The store materialises committed run
#: outputs, so `run_output_serialize` is the probe stage it actually shares a shape with;
#: the pipeline-wide first tear is recorded alongside it rather than instead of it, so a
#: reader can see both the store's envelope and the simulation's.
STORE_SEAM = "run_output_serialize"

SCHEMA_VERSION = 1


class SourceUnreadable(Exception):
    """A source could not be read, parsed, or was missing a field a projection needs."""


@dataclass(frozen=True)
class Source:
    name: str
    path: str
    table: str
    columns: tuple[str, ...]
    extract: Callable[[Any], list[tuple]]
    parse: Callable[[bytes], Any]


# --------------------------------------------------------------------------- git


def read_committed(repo: Path, relpath: str, rev: str = "HEAD") -> bytes:
    """Return the bytes of `relpath` AS COMMITTED at `rev`. Never touches the tree."""
    proc = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "blob", f"{rev}:{relpath}"],
        capture_output=True,
    )
    if proc.returncode != 0:
        detail = proc.stderr.decode("utf-8", "replace").strip() or f"rc={proc.returncode}"
        raise SourceUnreadable(f"not readable at {rev}: {detail}")
    return proc.stdout


def head_commit(repo: Path, rev: str = "HEAD") -> tuple[str, str]:
    proc = subprocess.run(
        ["git", "-C", str(repo), "log", "-1", "--format=%H%n%cI", rev],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise SourceUnreadable(f"no commit at {rev}: {proc.stderr.strip()}")
    sha, _, committed_at = proc.stdout.strip().partition("\n")
    return sha, committed_at


# ------------------------------------------------------------------- extractors


def _parse_json(blob: bytes) -> Any:
    return json.loads(blob.decode("utf-8"))


def _parse_yaml(blob: bytes) -> Any:
    return yaml.safe_load(blob.decode("utf-8"))


def _require(mapping: Any, *keys: str) -> Any:
    """Walk `keys` through `mapping`, raising SourceUnreadable on the first miss.

    A projection that needs a field and does not find it is an UNKNOWN. Returning a
    default here is how a store ends up publishing structure it never measured.
    """
    cursor = mapping
    walked: list[str] = []
    for key in keys:
        if not isinstance(cursor, dict) or key not in cursor:
            trail = ".".join(walked) or "<root>"
            raise SourceUnreadable(f"missing field {'.'.join(keys)!r} (absent at {trail})")
        walked.append(key)
        cursor = cursor[key]
    return cursor


def _atoms(doc: Any) -> list[tuple]:
    if not isinstance(doc, list):
        raise SourceUnreadable(f"expected a list of atoms, got {type(doc).__name__}")
    rows = []
    for entry in doc:
        if not isinstance(entry, dict) or "id" not in entry:
            continue
        expert_hour = entry.get("expert_hour") or {}
        rows.append(
            (
                entry["id"],
                entry.get("title"),
                entry.get("lane"),
                entry.get("value_stream"),
                entry.get("epoch"),
                entry.get("level_current"),
                entry.get("level_target"),
                entry.get("loop_stage"),
                entry.get("dial_inherited"),
                entry.get("provenance"),
                json.dumps(entry.get("depends_on") or []),
                json.dumps(entry.get("couples_with") or []),
                json.dumps(entry.get("file_scope") or []),
                (expert_hour or {}).get("status") if isinstance(expert_hour, dict) else None,
                entry.get("real_world_twin"),
            )
        )
    if not rows:
        raise SourceUnreadable("no atom records found — refusing to publish an empty register")
    return rows


def _runs(doc: Any) -> list[tuple]:
    if not isinstance(doc, list):
        raise SourceUnreadable(f"expected a list of runs, got {type(doc).__name__}")
    rows = []
    for position, entry in enumerate(doc):
        if not isinstance(entry, dict):
            continue
        metrics = entry.get("headline_metrics") or {}
        financial = metrics.get("financial") or {}
        customers = metrics.get("customers") or {}
        operations = metrics.get("operations") or {}
        risk = metrics.get("risk") or {}
        rows.append(
            (
                position,
                entry.get("git_hash"),
                entry.get("generated_at"),
                entry.get("net_margin_gbp"),
                financial.get("revenue_gbp"),
                financial.get("gross_margin_gbp"),
                financial.get("net_margin_pct"),
                customers.get("total_churned"),
                customers.get("enterprise_value_gbp"),
                operations.get("bills_total"),
                risk.get("survived"),
                entry.get("executive_summary"),
                json.dumps(metrics, sort_keys=True),
            )
        )
    if not rows:
        raise SourceUnreadable("no run records found — refusing to publish an empty history")
    return rows


def _coupled_gaps(doc: Any) -> list[tuple]:
    if not isinstance(doc, dict):
        raise SourceUnreadable(f"expected a mapping of atom -> gap, got {type(doc).__name__}")
    rows = []
    for atom_id, entry in sorted(doc.items()):
        if not isinstance(entry, dict):
            continue
        rows.append(
            (
                atom_id,
                entry.get("twin_atom_id"),
                entry.get("metric"),
                entry.get("gap"),
                entry.get("raw_gap"),
                entry.get("g0"),
                entry.get("baseline"),
                entry.get("measured_at"),
                entry.get("run_git_commit"),
                entry.get("note"),
                json.dumps(entry.get("components") or {}, sort_keys=True),
            )
        )
    if not rows:
        raise SourceUnreadable("no coupled-gap records found — refusing to publish an empty ledger")
    return rows


SOURCES: tuple[Source, ...] = (
    Source(
        name="maturity_map",
        path="docs/design/maturity_map.yaml",
        table="atoms",
        columns=(
            "id TEXT PRIMARY KEY",
            "title TEXT",
            "lane TEXT",
            "value_stream TEXT",
            "epoch INTEGER",
            "level_current INTEGER",
            "level_target INTEGER",
            "loop_stage TEXT",
            "dial_inherited INTEGER",
            "provenance TEXT",
            "depends_on TEXT",
            "couples_with TEXT",
            "file_scope TEXT",
            "expert_hour_status TEXT",
            "real_world_twin TEXT",
        ),
        extract=_atoms,
        parse=_parse_yaml,
    ),
    Source(
        name="run_history",
        path="docs/observability/run_history.json",
        table="runs",
        columns=(
            "position INTEGER PRIMARY KEY",
            "git_hash TEXT",
            "generated_at TEXT",
            "net_margin_gbp REAL",
            "revenue_gbp REAL",
            "gross_margin_gbp REAL",
            "net_margin_pct REAL",
            "total_churned INTEGER",
            "enterprise_value_gbp REAL",
            "bills_total INTEGER",
            "survived INTEGER",
            "executive_summary TEXT",
            "headline_metrics_json TEXT",
        ),
        extract=_runs,
        parse=_parse_json,
    ),
    Source(
        name="coupled_gap_ledger",
        path="docs/observability/coupled_gap_ledger.json",
        table="coupled_gaps",
        columns=(
            "atom_id TEXT PRIMARY KEY",
            "twin_atom_id TEXT",
            "metric TEXT",
            "gap REAL",
            "raw_gap REAL",
            "g0 REAL",
            "baseline TEXT",
            "measured_at TEXT",
            "run_git_commit TEXT",
            "note TEXT",
            "components_json TEXT",
        ),
        extract=_coupled_gaps,
        parse=_parse_json,
    ),
)

BUILD_META_COLUMNS = ("key TEXT PRIMARY KEY", "value TEXT")

SOURCE_STATUS_COLUMNS = (
    "name TEXT PRIMARY KEY",
    "path TEXT",
    "status TEXT",
    "reason TEXT",
    "sha256 TEXT",
    "row_count INTEGER",
    "blob_bytes INTEGER",
)

SCALE_ENVELOPE_COLUMNS = (
    "seam TEXT PRIMARY KEY",
    "role TEXT",
    "unit TEXT",
    "ceiling_customers INTEGER",
    "graduation_trigger_customers INTEGER",
    "observed_tear_n INTEGER",
    "tear_outcome TEXT",
    "marginal_rss_kb_per_customer REAL",
    "mem_cap_mb INTEGER",
    "source_path TEXT",
    "source_sha256 TEXT",
    "probe_generated_at TEXT",
)


def scale_envelope_rows(report: Any) -> list[tuple]:
    """Copy the envelope out of the probe report. Every figure below is READ.

    `ceiling_customers` is the largest ladder rung the seam SURVIVED; the graduation
    trigger is the probe's own projected tear. Both are the probe's numbers, in the
    probe's unit (customers). A seam the probe never measured is not defaulted — it
    raises, and the build fails closed.
    """
    per_stage = _require(report, "analysis", "per_stage")
    first_seam = _require(report, "analysis", "first_seam_to_tear")
    mem_cap_mb = _require(report, "config", "mem_cap_mb")
    generated_at = _require(report, "generated_at")

    wanted = [(STORE_SEAM, "store_envelope"), (first_seam, "pipeline_first_tear")]
    rows = []
    seen: set[str] = set()
    for seam, role in wanted:
        if seam in seen:
            continue
        seen.add(seam)
        stage = _require(per_stage, seam)
        rows.append(
            (
                seam,
                role,
                "customers",
                _require(stage, "survived_max_n"),
                _require(stage, "projected_tear_n"),
                _require(stage, "tear_n"),
                _require(stage, "tear_outcome"),
                _require(stage, "marginal_rss_kb_per_customer"),
                mem_cap_mb,
                SCALE_PROBE_RELPATH,
                None,  # filled in by the caller, which holds the blob
                generated_at,
            )
        )
    return rows


# ------------------------------------------------------------------------ store


def _open_new_store(store: Path) -> tuple[sqlite3.Connection, Path]:
    """Open a BRAND-NEW database beside `store`, to be swapped in when it is complete.

    The live store is never opened for writing. This is the single seam that carries
    "rebuilt, not mutated" — `test_build_projections.py` mutates exactly this function
    into the in-place variant and proves the hand-edit then survives.
    """
    target = store.with_name(store.name + ".rebuilding")
    if target.exists():
        target.unlink()
    target.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(target)), target


def _create(conn: sqlite3.Connection, table: str, columns: Iterable[str]) -> None:
    conn.execute(f"CREATE TABLE {table} ({', '.join(columns)})")


def _insert(conn: sqlite3.Connection, table: str, columns: Iterable[str], rows: list[tuple]) -> None:
    width = len(list(columns))
    placeholders = ", ".join("?" * width)
    conn.executemany(f"INSERT INTO {table} VALUES ({placeholders})", rows)


def build(repo: Path | None = None, rev: str = "HEAD") -> dict:
    """Rebuild the store from committed truth. Returns the build report.

    On any UNKNOWN source the report's `status` is `"failed_closed"`, the live store is
    left exactly as it was, and no table for that source is published.
    """
    repo = REPO_ROOT if repo is None else repo
    store = repo / STORE_RELPATH
    report: dict[str, Any] = {
        "status": "ok",
        "store": str(STORE_RELPATH),
        "rev": rev,
        "schema_version": SCHEMA_VERSION,
        "sources": [],
        "unknown": [],
        "rows_total": 0,
    }

    try:
        head_sha, head_committed_at = head_commit(repo, rev)
    except SourceUnreadable as exc:
        report["status"] = "failed_closed"
        report["unknown"] = [{"name": "<rev>", "path": rev, "reason": str(exc)}]
        return report

    report["head_sha"] = head_sha
    report["head_committed_at"] = head_committed_at

    # Read and extract EVERYTHING before opening the store, so a late UNKNOWN cannot
    # leave a half-built database behind.
    extracted: list[tuple[Source, list[tuple], str, int]] = []
    for source in SOURCES:
        try:
            blob = read_committed(repo, source.path, rev)
            rows = source.extract(source.parse(blob))
        except SourceUnreadable as exc:
            report["unknown"].append({"name": source.name, "path": source.path, "reason": str(exc)})
            continue
        except Exception as exc:  # a parse error is an UNKNOWN, not an empty table
            report["unknown"].append(
                {"name": source.name, "path": source.path, "reason": f"{type(exc).__name__}: {exc}"}
            )
            continue
        extracted.append((source, rows, hashlib.sha256(blob).hexdigest(), len(blob)))

    try:
        probe_blob = read_committed(repo, SCALE_PROBE_RELPATH, rev)
        probe_sha = hashlib.sha256(probe_blob).hexdigest()
        envelope = [
            row[:-2] + (probe_sha,) + row[-1:] for row in scale_envelope_rows(_parse_json(probe_blob))
        ]
    except SourceUnreadable as exc:
        report["unknown"].append(
            {"name": "scale_probe_10k", "path": SCALE_PROBE_RELPATH, "reason": str(exc)}
        )
        envelope = []
        probe_sha = None
    except Exception as exc:
        report["unknown"].append(
            {
                "name": "scale_probe_10k",
                "path": SCALE_PROBE_RELPATH,
                "reason": f"{type(exc).__name__}: {exc}",
            }
        )
        envelope = []
        probe_sha = None

    if report["unknown"]:
        report["status"] = "failed_closed"
        return report

    conn, target = _open_new_store(store)
    try:
        _create(conn, "build_meta", BUILD_META_COLUMNS)
        _create(conn, "source_status", SOURCE_STATUS_COLUMNS)
        _create(conn, "scale_envelope", SCALE_ENVELOPE_COLUMNS)
        _insert(conn, "scale_envelope", SCALE_ENVELOPE_COLUMNS, envelope)

        rows_total = 0
        statuses = []
        for source, rows, sha, blob_bytes in extracted:
            _create(conn, source.table, source.columns)
            _insert(conn, source.table, source.columns, rows)
            statuses.append((source.name, source.path, "ok", None, sha, len(rows), blob_bytes))
            rows_total += len(rows)
            report["sources"].append(
                {
                    "name": source.name,
                    "path": source.path,
                    "table": source.table,
                    "rows": len(rows),
                    "sha256": sha,
                }
            )
        statuses.append(
            ("scale_probe_10k", SCALE_PROBE_RELPATH, "ok", None, probe_sha, len(envelope), len(probe_blob))
        )
        _insert(conn, "source_status", SOURCE_STATUS_COLUMNS, statuses)
        rows_total += len(envelope)

        _insert(
            conn,
            "build_meta",
            BUILD_META_COLUMNS,
            [
                ("schema_version", str(SCHEMA_VERSION)),
                ("head_sha", head_sha),
                ("head_committed_at", head_committed_at),
                ("rev", rev),
                ("rows_total", str(rows_total)),
                ("builder", "tools/build_projections.py"),
                ("derived_from", "committed blobs only (git cat-file), never the working tree"),
            ],
        )
        conn.commit()
    finally:
        conn.close()

    os.replace(target, store)
    report["rows_total"] = rows_total
    return report


def query(sql: str, repo: Path | None = None) -> list[tuple]:
    store = (REPO_ROOT if repo is None else repo) / STORE_RELPATH
    if not store.exists():
        raise SourceUnreadable(f"{STORE_RELPATH} has not been built — run this tool with no arguments")
    conn = sqlite3.connect(f"file:{store}?mode=ro", uri=True)
    try:
        return list(conn.execute(sql))
    finally:
        conn.close()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--report", action="store_true", help="emit the build report as JSON")
    ap.add_argument("--query", metavar="SQL", help="read the store back instead of rebuilding it")
    ap.add_argument("--rev", default="HEAD", help="the commit to derive from (default: HEAD)")
    args = ap.parse_args(argv)

    if args.query:
        try:
            for row in query(args.query):
                print("\t".join("" if cell is None else str(cell) for cell in row))
        except SourceUnreadable as exc:
            print(f"UNKNOWN: {exc}", file=sys.stderr)
            return 2
        return 0

    report = build(rev=args.rev)
    if args.report:
        print(json.dumps(report, indent=2, sort_keys=True))
    if report["status"] != "ok":
        for unknown in report["unknown"]:
            print(
                f"UNKNOWN source {unknown['name']} ({unknown['path']}): {unknown['reason']}",
                file=sys.stderr,
            )
        print(
            f"FAILED CLOSED — {STORE_RELPATH} left untouched. An unreadable source is an "
            "UNKNOWN, never an empty table.",
            file=sys.stderr,
        )
        return 2
    if not args.report:
        print(
            f"{STORE_RELPATH}: {report['rows_total']} rows from "
            f"{len(report['sources']) + 1} committed sources at {report['head_sha'][:9]}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
