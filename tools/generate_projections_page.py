#!/usr/bin/env python3
"""Feed a site page from the PROJECTION STORE instead of a hand-refreshed file
(atom `G13_projection_consumers`, deliverable 3 of DIRECTOR_INSTRUCTION_QUERYABLE_
PROJECTIONS_2026-08-10: "at least one site page and one lab query consuming it,
as the proof-of-caller").

    python3 -m tools.generate_projections_page            # rebuild the store, write the feed
    python3 -m tools.generate_projections_page --report   # ... and print the report as JSON
    python3 -m tools.generate_projections_page --check    # exit 1 if the feed is not current

REUSE: tools/generate_projections_page.py
CLASS: CUSTOM
INDEX: searched "projection", "site data generator", "wip", "store consumer".
       `tools/build_projections.py` (G12) is the store and is REUSED WHOLE -- this module
       computes no projection of its own, it calls `build()` and then reads the store back.
       `tools/generate_wip_flow_data.py` (G7) owns the WIP-flow door's feed and its lane /
       stage vocabulary is IMPORTED rather than copied, because both feeds now render into
       ONE page and two drifting label sets on one surface is a defect waiting to happen.
       Its own `_wip()` is deliberately NOT reused: it reads `docs/design/maturity_map.yaml`
       off the WORKING TREE, and reading committed truth instead is the entire point here.

WHAT THIS REPLACES, NAMED
-------------------------
`site/data/wip_flow.json` -- specifically its `wip` block (`total_atoms`, `by_stage`,
`by_lane`, `concurrent_build_wip`, `harden_wip`, `idle_count`). That file is HAND-REFRESHED:
`tools/generate_wip_flow_data.py` appears in no publish path (`background/process_run_complete.py`
runs 40-odd generators and not that one), so its `wip` block is correct only for as long as
nobody moves an atom -- and moving atoms is the machine's normal metabolism. That is the
derived-artefact-staleness shape (WORKER_FINDING_DERIVED_ARTEFACT_STALENESS_IS_A_WEDGE_CLASS_
2026-08-09) pointed at a site surface instead of at the publish gate.

After this module, `site/wip-flow/index.html` takes its WIP block from
`site/data/projections.json`, which is REBUILT FROM HEAD every time it is written and carries
the sha it was derived from on its face. The rest of the door (cycle time, throughput) still
comes from `wip_flow.json`: those figures are mined from git history by `effort_calibration`
and are not in the store, so claiming them here would be a lie about provenance.

THE FEED CANNOT BE STALE, BECAUSE IT IS NOT REFRESHED -- IT IS REBUILT
---------------------------------------------------------------------
Writing the feed ALWAYS rebuilds the store first. There is no "use the store as you find it"
path and no `--no-rebuild` flag: a flag like that is the staleness this atom exists to end,
wearing a bypass. If the rebuild fails closed (an unreadable source is an UNKNOWN, never an
empty table -- G12 property 3), this module writes NOTHING and exits non-zero. The previous
feed is left byte-identical rather than being replaced by a plausible-looking empty one.

FAIL-VISIBLE ON THE PAGE, NOT FAIL-SILENT
-----------------------------------------
If `projections.json` is missing or 404s at read time, the page does NOT silently fall back to
the hand-refreshed numbers and pretend. It renders the `wip_flow.json` block so the door is not
blank, and stamps a RED note saying the store was unavailable and which file the numbers came
from instead. An unavailable check is a failed check (R15); an unavailable *source* must be
visible as one.

R14: every figure here carries its clock. The WIP inventory's clock is `head_sha` -- the commit
the numbers are true of -- which is a strictly stronger stamp than a generation timestamp,
because a timestamp tells you when someone looked and a sha tells you what they looked at.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from tools import build_projections as bp
from tools.generate_wip_flow_data import LANE_NAMES, STAGE_LABEL, STAGE_ORDER

PROJECT = Path(__file__).resolve().parents[1]
OUT_PATH = PROJECT / "site" / "data" / "projections.json"

#: The file whose `wip` block this feed takes over. Named in the artefact itself so a reader
#: of the JSON can see what was replaced without reading this module.
REPLACES = "site/data/wip_flow.json"
REPLACES_BLOCK = "wip"

#: R14. The clock the WIP inventory is measured on -- a commit, not a wall-clock stamp.
WIP_BASIS = "committed_state_at_head_sha"


class StoreUnavailable(Exception):
    """The store could not be rebuilt or read. Nothing is written when this is raised."""


def _wip_from_store(conn: sqlite3.Connection) -> dict:
    """The WIP inventory, counted from the store's `atoms` table.

    Same shape `site/wip-flow/index.html::renderWip` already consumes, so the page's render
    path does not move -- only where the numbers come from does.
    """
    rows = list(conn.execute("SELECT lane, loop_stage FROM atoms"))
    if not rows:
        # Fail-closed, not zero. An empty atoms table downstream is indistinguishable from
        # "we counted, and the board is empty" -- which has never been true and never will be.
        raise StoreUnavailable("the store's `atoms` table is empty; refusing to publish a zero board")

    by_stage: Counter = Counter()
    by_lane: defaultdict = defaultdict(Counter)
    for lane, stage in rows:
        stage = stage or "unknown"
        by_stage[stage] += 1
        by_lane[lane or "unassigned"][stage] += 1

    stages = [
        dict(stage=st, label=STAGE_LABEL.get(st, st), count=by_stage[st])
        for st in STAGE_ORDER
        if st in by_stage
    ]
    stages += [
        dict(stage=st, label=STAGE_LABEL.get(st, st), count=n)
        for st, n in sorted(by_stage.items())
        if st not in STAGE_ORDER
    ]

    lanes = [
        dict(
            lane=lane,
            lane_name=LANE_NAMES.get(lane, lane.replace("_", " ")),
            total=sum(counts.values()),
            build=counts.get("build", 0),
            harden=counts.get("harden", 0),
            idle=counts.get("idle", 0),
        )
        for lane, counts in sorted(by_lane.items(), key=lambda kv: -sum(kv[1].values()))
    ]

    return dict(
        total_atoms=len(rows),
        by_stage=stages,
        by_lane=lanes,
        concurrent_build_wip=by_stage.get("build", 0),
        harden_wip=by_stage.get("harden", 0),
        idle_count=by_stage.get("idle", 0),
        basis=WIP_BASIS,
    )


def _store_provenance(conn: sqlite3.Connection, report: dict) -> dict:
    meta = dict(conn.execute("SELECT key, value FROM build_meta"))
    sources = [
        dict(name=n, path=p, status=s, rows=r)
        for n, p, s, r in conn.execute(
            "SELECT name, path, status, row_count FROM source_status ORDER BY name"
        )
    ]
    return dict(
        head_sha=meta.get("head_sha"),
        head_committed_at=meta.get("head_committed_at"),
        schema_version=int(meta.get("schema_version", bp.SCHEMA_VERSION)),
        rows_total=int(meta.get("rows_total", report.get("rows_total", 0))),
        builder=meta.get("builder"),
        derived_from=meta.get("derived_from"),
        store=str(bp.STORE_RELPATH),
        sources=sources,
    )


def generate(repo: Path | None = None) -> dict:
    """Rebuild the store, then build the feed payload from it. Never reads the working tree.

    Raises `StoreUnavailable` if the rebuild fails closed -- the caller writes nothing.
    """
    repo = PROJECT if repo is None else repo
    report = bp.build(repo=repo)
    if report.get("status") != "ok":
        unknown = ", ".join(f"{u['name']} ({u['path']}): {u['reason']}" for u in report.get("unknown", []))
        raise StoreUnavailable(f"store rebuild failed closed -- {unknown or 'no reason recorded'}")

    store = repo / bp.STORE_RELPATH
    conn = sqlite3.connect(f"file:{store}?mode=ro", uri=True)
    try:
        wip = _wip_from_store(conn)
        provenance = _store_provenance(conn, report)
    finally:
        conn.close()

    return dict(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        consumer="site/wip-flow/index.html",
        replaces=dict(file=REPLACES, block=REPLACES_BLOCK,
                      why="that file's generator is in no publish path, so its WIP block is "
                          "correct only until the next atom moves"),
        store=provenance,
        wip=wip,
    )


def write(repo: Path | None = None) -> Path:
    payload = generate(repo=repo)
    out = (PROJECT if repo is None else repo) / "site" / "data" / "projections.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n")
    return out


def _current(repo: Path | None = None) -> tuple[bool, str]:
    """Is the written feed derived from the CURRENT head? Returns (ok, reason)."""
    out = (PROJECT if repo is None else repo) / "site" / "data" / "projections.json"
    if not out.is_file():
        return False, f"{out.relative_to(PROJECT if repo is None else repo)} has never been written"
    try:
        payload = json.loads(out.read_text())
    except json.JSONDecodeError as exc:
        return False, f"feed does not parse: {exc}"
    head, _ = bp.head_commit(PROJECT if repo is None else repo)
    written = (payload.get("store") or {}).get("head_sha")
    if written != head:
        return False, f"feed derived from {str(written)[:9]}, HEAD is {head[:9]}"
    return True, f"feed is current at {head[:9]}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--report", action="store_true", help="print the written payload as JSON")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the feed is not derived from the current HEAD")
    args = ap.parse_args(argv)

    if args.check:
        ok, reason = _current()
        print(("OK: " if ok else "STALE: ") + reason, file=sys.stdout if ok else sys.stderr)
        return 0 if ok else 1

    try:
        out = write()
    except (StoreUnavailable, bp.SourceUnreadable) as exc:
        print(f"FAILED CLOSED -- {exc}", file=sys.stderr)
        print(f"{OUT_PATH.relative_to(PROJECT)} left untouched.", file=sys.stderr)
        return 2

    payload = json.loads(out.read_text())
    if args.report:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            f"{out.relative_to(PROJECT)}: {payload['wip']['total_atoms']} atoms "
            f"from {payload['store']['head_sha'][:9]} "
            f"(replaces the `{REPLACES_BLOCK}` block of {REPLACES})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
