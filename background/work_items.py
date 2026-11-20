"""The one work system, increment 1: the item store, the one rule that picks, and the staging
findings as its first source, run in SHADOW beside the old ladder.

Built to `docs/design/ONE_WORK_SYSTEM_DECISION_MAP_2026-11-20.md` (D1, D2, D6, D9). The practice it
rests on is `docs/market_research/one_backlog_and_flow_practice_2026-11-20.md` (K8).

What this increment is and is not:

* **The store (D1, D2).** One YAML file per item at `docs/work/items/<id>.yaml`. `validate()` is
  the shape; `write_item`/`read_item` round-trip it.
* **The pick (D6).** `next_item()` is the whole ranking rule. It returns the item AND the reason,
  because a pick nobody can audit afterwards is one nobody can disagree with.
* **The first source (D9 step 2).** `items_from_staging()` turns each classified finding in the
  staging root into an item whose evidence is the document. While the cut-over flag
  (`docs/work/cutover.yaml`) reads `shadow`, those items are DERIVED on every read and never
  written: writing 185 files now would make a second store of the same work that drifts from the
  staging root within the hour, which is the exact failure the steer is about. The files are
  written at cut-over (`--migrate --write`), in the commit that stops the staging root being a
  queue.
* **Side by side (D9 step 2).** `shadow_record()` is called by the supervisor's draw with the
  ladder's own string; it logs what `next_item()` would have picked next to it and changes nothing.
  `--compare` reads the day back.

Not yet here, and where each goes: the claim (D5) replaces the delivery-lane and seat claim stores
in the migration that deletes them; the draw-count park needs that claim; the dials (D7) wait for
the director's answer on the for_the_director row `the-one-work-system-s-decision-map` and only
matter once atom steps are a source, which none is yet.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

PROJECT_DIR = Path(__file__).resolve().parent.parent
ITEMS_DIR = PROJECT_DIR / "docs" / "work" / "items"
CUTOVER_FILE = PROJECT_DIR / "docs" / "work" / "cutover.yaml"
PRIORITY_ORDER = PROJECT_DIR / "docs" / "direction" / "priority_order.yaml"
STAGING_ROOT = PROJECT_DIR / "docs" / "staging"

#: Gitignored; in the shared tree whatever tree the caller stands in, beside the claim stores.
SHADOW_LOG_NAME = ".work_items_shadow.jsonl"

LANES = ("world", "supplier", "building")
KINDS = ("correctness", "feature", "knowledge", "trial", "harness")
CLASSES = ("stop_the_line", "dated", "standard")
SEVERITIES = ("BLOCKING", "LATENT", "RECORDED")
SOURCES = ("finding", "gate_breach", "cold_read", "knowledge_gap", "steer", "question",
           "seam_gap", "alarm", "atom_step", "census_red")
STATES = ("open", "chosen", "done", "parked", "obsolete")
DECIDERS = ("machine", "director")
CUTOVER_MODES = ("off", "shadow")

REQUIRED = ("id", "title", "lane", "kind", "class", "severity", "source", "evidence", "decider",
            "state", "opened_at")

_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")

#: The finding header's lane (`finding_severity.LANES`) to the item's side (D4). W1-W3 and W5 are
#: the world. W4 is the epistemic wall's verifier, which guards the seam and is built by the
#: harness, so it is building. A (strategy and governance) and H (harness) are how the work is
#: done, so building. B-G are the supplier's departments.
FINDING_LANE_TO_SIDE = {
    "A_strategy_governance": "building",
    "B_commercial": "supplier",
    "C_customer_ops": "supplier",
    "D_billing_metering": "supplier",
    "E_finance_treasury": "supplier",
    "F_risk_compliance": "supplier",
    "G_data_learning": "supplier",
    "H_harness": "building",
    "W1_market_weather": "world",
    "W2_customer_generator": "world",
    "W3_industry_systems": "world",
    "W4_the_wall": "building",
    "W5_banking_payment_rails": "world",
}


# ---------------------------------------------------------------------------------------------
# The store (D1, D2)
# ---------------------------------------------------------------------------------------------

def validate(item: dict) -> list[str]:
    """Every way `item` departs from the D2 shape, as sentences. Empty means valid."""
    errors = [f"missing {k}" for k in REQUIRED if item.get(k) in (None, "")]
    if errors:
        return errors
    if not _ID_RE.match(str(item["id"])):
        errors.append(f"id {item['id']!r} is not a kebab slug")
    for field, allowed in (("lane", LANES), ("kind", KINDS), ("class", CLASSES),
                           ("severity", SEVERITIES), ("source", SOURCES), ("state", STATES),
                           ("decider", DECIDERS)):
        if item[field] not in allowed:
            errors.append(f"{field} {item[field]!r} not one of {'/'.join(allowed)}")
    if item["class"] == "dated" and not item.get("due"):
        errors.append("class dated carries no due date")
    if item["state"] == "done" and not item.get("done_evidence"):
        errors.append("done without done_evidence")
    if item["state"] == "parked":
        parked = item.get("parked") or {}
        if not parked.get("reason") or not parked.get("revisit"):
            errors.append("parked without a reason and a revisit date")
    if item["state"] == "obsolete" and not item.get("obsolete"):
        errors.append("obsolete without a reason")
    if item["state"] == "chosen" and not item.get("chosen_by"):
        errors.append("chosen without chosen_by")
    if not isinstance(item["evidence"], list) or not item["evidence"]:
        errors.append("evidence must be a non-empty list")
    return errors


def write_item(item: dict, items_dir: Path = ITEMS_DIR) -> Path:
    errors = validate(item)
    if errors:
        raise ValueError(f"item {item.get('id')!r} refused: {'; '.join(errors)}")
    items_dir.mkdir(parents=True, exist_ok=True)
    path = items_dir / f"{item['id']}.yaml"
    path.write_text(yaml.safe_dump(item, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path


def read_item(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def stored_items(items_dir: Path = ITEMS_DIR) -> list[dict]:
    if not items_dir.is_dir():
        return []
    return [read_item(p) for p in sorted(items_dir.glob("*.yaml"))]


# ---------------------------------------------------------------------------------------------
# The first source: staging findings (D3 row 1, D9 step 2)
# ---------------------------------------------------------------------------------------------

_DATE_IN_NAME_RE = re.compile(r"_(\d{4}-\d{2}-\d{2})\.md$")
_TITLE_RE = re.compile(r"(?m)^# +(.+)$")
_ATOM_RE = re.compile(r"\*\*Atom:?\*\*:?\s*`([A-Za-z0-9_]+)`")


def _slug(name: str) -> str:
    stem = _DATE_IN_NAME_RE.sub("", name).removesuffix(".md")
    return re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")


def items_from_staging(staging_root: Path = STAGING_ROOT) -> tuple[list[dict], list[str]]:
    """One item per classified finding in the staging root, and the documents refused, by reason.

    `kind` is not in the finding header, so it is set by a stated rule rather than read: a finding
    reports something wrong, so it is `correctness`, and on the building side `harness`. Triage
    corrects it per item. `affects` is not stated by the header either and is left `None`, which a
    reader can see is unassessed; an empty list would assert it affects nothing. `opened_at` is the
    date in the filename (every finding carries one), else the file's mtime.
    """
    from background.finding_severity import scan_staging_root

    items: list[dict] = []
    refused: list[str] = []
    for parsed in scan_staging_root(staging_root):
        if parsed.path.suffix != ".md":
            refused.append(f"{parsed.path.name}: not a markdown finding")
            continue
        if not parsed.is_classified:
            refused.append(f"{parsed.path.name}: {parsed.reason}")
            continue
        side = FINDING_LANE_TO_SIDE.get(parsed.lane or "")
        if side is None:
            refused.append(f"{parsed.path.name}: lane {parsed.lane!r} has no side")
            continue
        text = parsed.path.read_text(encoding="utf-8", errors="replace")
        title = _TITLE_RE.search(text)
        atom = _ATOM_RE.search(text)
        dated = _DATE_IN_NAME_RE.search(parsed.path.name)
        opened = (dated.group(1) + "T00:00:00+00:00" if dated else
                  datetime.fromtimestamp(parsed.path.stat().st_mtime, timezone.utc).isoformat())
        items.append({
            "id": _slug(parsed.path.name),
            "title": (title.group(1).strip() if title else parsed.path.stem),
            "lane": side,
            "kind": "harness" if side == "building" else "correctness",
            "affects": None,
            "class": "standard",
            "severity": parsed.severity,
            "source": "finding",
            # The staging root is always <repo>/docs/staging, so this is the repo-relative path.
            "evidence": [parsed.path.relative_to(staging_root.parent.parent).as_posix()],
            "knowledge_gap": None,
            "insight": None,
            "decider": "machine",
            "director_rank": None,
            "atom": (atom.group(1) if atom and atom.group(1) != "unminted" else None),
            "blocked_by": [],
            "occurrences": 1,
            "state": "open",
            "opened_at": opened,
            "chosen_at": None,
            "closed_at": None,
            "chosen_by": None,
            "done_evidence": None,
            "parked": None,
            "obsolete": None,
            "finding_lane": parsed.lane,
        })
    return items, refused


def cutover_mode(path: Path = CUTOVER_FILE) -> str:
    """The staging-findings cut-over flag. An unreadable or unknown value reads `off`, by name."""
    try:
        mode = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("staging_findings")
    except (OSError, yaml.YAMLError):
        return "off"
    return mode if mode in CUTOVER_MODES else "off"


def all_items(staging_root: Path = STAGING_ROOT, items_dir: Path = ITEMS_DIR) -> list[dict]:
    """The store as the pick reads it: written items, plus staging-derived ones not yet written."""
    stored = stored_items(items_dir)
    seen = {i["id"] for i in stored}
    derived, _ = items_from_staging(staging_root)
    return stored + [i for i in derived if i["id"] not in seen]


# ---------------------------------------------------------------------------------------------
# The one rule that picks (D6)
# ---------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Pick:
    item: dict | None
    reason: str


def load_shares(path: Path = PRIORITY_ORDER) -> dict[str, float]:
    """The weekly review's share table (`weekly_split:` in priority_order.yaml), as fractions."""
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    split = (data.get("weekly_split") or {}).get("shares") or {}
    return {row: float(pct) / 100.0 for row, pct in split.items()}


def share_row(item: dict) -> str:
    """The share-table row an item lands in. The rows are the 16 Nov review's §4."""
    kind = item["kind"]
    if kind in ("correctness", "knowledge"):
        return kind
    if kind == "harness" or item["lane"] == "building":
        return "harness"
    return f"{item['lane']}_feature"


def _parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    try:
        ts = datetime.fromisoformat(str(value))
    except ValueError:
        return None
    return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)


def _revisit_passed(item: dict, today: date) -> bool:
    revisit = (item.get("parked") or {}).get("revisit")
    try:
        return revisit is not None and date.fromisoformat(str(revisit)) <= today
    except ValueError:
        return False


def _eligible(item: dict, done_ids: set[str], today: date) -> bool:
    state = item["state"]
    if state == "parked":
        if not _revisit_passed(item, today):
            return False
    elif state != "open":
        return False
    return item.get("decider") == "machine" and all(b in done_ids for b in item.get("blocked_by") or [])


def _median_cycle_days(items: list[dict], row: str) -> float | None:
    days = []
    for i in items:
        if i["state"] == "done" and share_row(i) == row:
            a, c = _parse_ts(i.get("chosen_at") or i.get("opened_at")), _parse_ts(i.get("closed_at"))
            if a and c:
                days.append((c - a).total_seconds() / 86400)
    return statistics.median(days) if days else None


def _within_row_key(item: dict, cycle_days: float | None, today: date) -> tuple:
    rank = item.get("director_rank")
    due_soon = 1
    if item["class"] == "dated" and item.get("due"):
        try:
            due = date.fromisoformat(str(item["due"]))
        except ValueError:
            due = None
        # With no cycle time measured for the row yet, every dated item counts as due soon:
        # erring toward the date is the side a missed deadline cannot be argued back from.
        if due is not None and (cycle_days is None or due <= today + timedelta(days=cycle_days)):
            due_soon = 0
    opened = _parse_ts(item.get("opened_at")) or datetime.max.replace(tzinfo=timezone.utc)
    return (rank is None, rank if rank is not None else 0, due_soon,
            SEVERITIES.index(item["severity"]), opened, item["id"])


def next_item(items: list[dict], shares: dict[str, float], *, now: datetime | None = None,
              wip_limit: int | None = None) -> Pick:
    """D6, in order. Deterministic: the same store and clock always give the same pick."""
    now = now or datetime.now(timezone.utc)
    today = now.date()
    done_ids = {i["id"] for i in items if i["state"] == "done"}
    chosen = [i for i in items if i["state"] == "chosen"]
    if wip_limit is not None and len(chosen) >= wip_limit:
        return Pick(None, f"WIP limit: {len(chosen)} chosen of {wip_limit} admitted")
    eligible = [i for i in items if _eligible(i, done_ids, today)]
    if not eligible:
        return Pick(None, "rest: no item is eligible")

    # Step 2: stop-the-line first, across lanes, WIP 1.
    expedite = [i for i in eligible if i["class"] == "stop_the_line"]
    expedite_running = any(i["class"] == "stop_the_line" for i in chosen)
    if expedite and not expedite_running:
        top = min(expedite, key=lambda i: _within_row_key(i, None, today))
        return Pick(top, f"stop the line: {top['id']}")

    # Step 4 first as a filter: a lane holding an open BLOCKING item takes no feature work.
    blocked_lanes = {i["lane"] for i in items
                     if i["severity"] == "BLOCKING" and i["state"] in ("open", "chosen")}
    candidates = [i for i in eligible if i["class"] != "stop_the_line"
                  and not (i["kind"] in ("feature", "trial") and i["lane"] in blocked_lanes)]
    if not candidates:
        return Pick(None, "rest: every eligible item is a feature in a lane with an open BLOCKING item")

    # Step 3: the row furthest below its share, on items landed this week. Items carry no points
    # field (D2 has none), so the measure is landed COUNT until they do.
    week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0,
                                                               microsecond=0)
    landed: dict[str, int] = {}
    for i in items:
        closed = _parse_ts(i.get("closed_at"))
        if i["state"] == "done" and closed and closed >= week_start:
            landed[share_row(i)] = landed.get(share_row(i), 0) + 1
    total = sum(landed.values())
    rows = {share_row(i) for i in candidates}
    unshared = sorted(r for r in rows if r not in shares)
    if unshared:
        return Pick(None, f"refused: share table has no row for {', '.join(unshared)}")

    def deficit(row: str) -> tuple:
        got = landed.get(row, 0) / total if total else 0.0
        return (-(shares[row] - got), -shares[row], row)

    row = min(rows, key=deficit)
    cycle = _median_cycle_days(items, row)
    top = min((i for i in candidates if share_row(i) == row),
              key=lambda i: _within_row_key(i, cycle, today))
    got = landed.get(row, 0)
    return Pick(top, f"row {row} furthest below its share ({shares[row]:.0%}, {got} of {total} "
                     f"landed this week); then rank, date, {top['severity']}, age: {top['id']}")


# ---------------------------------------------------------------------------------------------
# Side by side with the old ladder (D9 step 2)
# ---------------------------------------------------------------------------------------------

def shadow_log_path() -> Path:
    from background import seat_continuation
    return seat_continuation.shared_tree_dir() / "docs" / "observability" / SHADOW_LOG_NAME


def shadow_record(ladder: str | None, *, log_path: Path | None = None,
                  cutover_path: Path = CUTOVER_FILE, staging_root: Path = STAGING_ROOT,
                  priority_path: Path = PRIORITY_ORDER, items_dir: Path = ITEMS_DIR,
                  now: datetime | None = None) -> dict | None:
    """Log what `next_item()` would pick beside what the ladder drew. Changes nothing.

    Returns the record, or None when the flag is off. `ladder_names_pick` says whether the
    ladder's string names the picked finding's document, which is the one difference the day
    exists to count: a pick the old draw would never have made.
    """
    if cutover_mode(cutover_path) != "shadow":
        return None
    path = log_path
    if path is None:
        # A test process that reaches the live log is refused here, before the staging read, so
        # a fixture's draw can never become a row of the day being compared.
        from background.live_ledger_guard import guard_live_ledger_write
        path = guard_live_ledger_write(shadow_log_path(), writer="work_items.shadow_record")
    now = now or datetime.now(timezone.utc)
    items = all_items(staging_root, items_dir)
    pick = next_item(items, load_shares(priority_path), now=now)
    evidence = (pick.item or {}).get("evidence") or []
    finding_names = {Path(e).name for i in items for e in i.get("evidence") or []}
    record = {
        "at": now.isoformat(timespec="seconds"),
        "pick": (pick.item or {}).get("id"),
        "pick_lane": (pick.item or {}).get("lane"),
        "pick_severity": (pick.item or {}).get("severity"),
        "reason": pick.reason,
        "ladder_head": (ladder or "")[:300],
        "ladder_names_pick": bool(ladder and any(Path(e).name in ladder for e in evidence)),
        # How often the old ladder draws a staging finding at all; without it a low
        # ladder_names_pick cannot be told from a ladder that simply draws atoms.
        "ladder_names_any_finding": bool(ladder and any(n in ladder for n in finding_names)),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")
    return record


def compare(log_path: Path | None = None) -> str:
    path = log_path or shadow_log_path()
    if not path.exists():
        return f"no shadow log at {path}: the flag has not been on through a draw"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    if not rows:
        return "shadow log is empty"
    named = sum(r["ladder_names_pick"] for r in rows)
    any_finding = sum(r.get("ladder_names_any_finding", False) for r in rows)
    picks: dict[str, int] = {}
    for r in rows:
        picks[r["pick"] or "(none)"] = picks.get(r["pick"] or "(none)", 0) + 1
    lines = [f"{len(rows)} draws from {rows[0]['at']} to {rows[-1]['at']}",
             f"the ladder named the new pick's document in {named} of {len(rows)}",
             f"the ladder named any staging finding in {any_finding} of {len(rows)}",
             "new picks:"]
    lines += [f"  {n:>4}  {pid}" for pid, n in sorted(picks.items(), key=lambda kv: -kv[1])]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--pick", action="store_true", help="print what next_item() picks now")
    parser.add_argument("--migrate", action="store_true",
                        help="print the staging findings as items, and the documents refused")
    parser.add_argument("--write", action="store_true",
                        help="with --migrate: write the items (the cut-over step; not in shadow)")
    parser.add_argument("--compare", action="store_true", help="read the side-by-side log back")
    args = parser.parse_args(argv)
    if args.compare:
        print(compare())
        return 0
    if args.migrate:
        items, refused = items_from_staging()
        if args.write:
            if cutover_mode() == "shadow":
                print("refused: the flag reads shadow; items are derived, not written, until "
                      "cut-over", file=sys.stderr)
                return 2
            for item in items:
                write_item(item)
        by_lane: dict[str, int] = {}
        for i in items:
            by_lane[i["lane"]] = by_lane.get(i["lane"], 0) + 1
        print(f"{len(items)} items {by_lane}; {len(refused)} refused")
        for r in refused:
            print(f"  refused {r}")
        return 0
    pick = next_item(all_items(), load_shares())
    print(pick.reason)
    return 0


if __name__ == "__main__":
    from background._seat import refuse_if_foreign

    refuse_if_foreign("work_items")
    sys.exit(main())
