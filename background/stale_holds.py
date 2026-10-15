"""Holds whose named premise has already been met: a map row held on an atom that is done.

Known issue `a-hold-condition-is-not-reasked-when-its-premise-moves` (41 listings). A held row says
what it waits for in prose -- "sequenced behind B10" -- and nothing re-read it when the premise
moved: C29 carried that hold for five weeks after B10 reached its target (15a9703ae), and the stale
hold kept PB4 off L3 until it was fixed by hand (59c53d8a7).

This re-asks every hold each orientation. A row is HELD when it carries a `block_reason` or a
`blocked_on`. Each atom the hold names -- a full id, or the short id prose uses ("B10", matched to
the one live or closed id that begins "B10_") -- is MET when it has reached its level target or
closed. A hold naming a met atom is listed in the seat's brief. It REPORTS and never releases: a
named atom is not always the premise (a hold can cite one as history), so the seat reads each and
decides, which is what the finding's DONE asks for.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

PROJECT_DIR = Path(__file__).resolve().parent.parent
MAP = PROJECT_DIR / "docs" / "design" / "maturity_map.yaml"
CLOSED = PROJECT_DIR / "docs" / "design" / "maturity_map_closed.yaml"

#: A short atom id as prose writes it: capitals, digits, an optional suffix (B10, W2_29, EP17, C34).
_SHORT = re.compile(r"(?<![\w-])([A-Z][A-Z0-9]*\d+(?:_\d+)?[a-z]?)(?![\w-])")


def _rows(path: Path) -> list[dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    rows = data if isinstance(data, list) else data.get("atoms", [])
    return [r for r in rows if isinstance(r, dict) and r.get("id")]


def _met(row: dict) -> bool:
    try:
        return float(row.get("level_current") or 0) >= float(row.get("level_target") or 0) > 0
    except (TypeError, ValueError):
        return False


def _context(reason: str, atom: str, blocked: list) -> str:
    """Where the hold names `atom`: `blocked_on`, or the prose around its short id, so the seat can
    tell a premise ("sequenced behind B10") from a citation ("near PB1 scale") at a glance."""
    if atom in [str(b) for b in blocked]:
        return "blocked_on"
    short = atom.split("_")[0] if not atom.startswith(("W1_", "W2_", "W3_")) else "_".join(atom.split("_")[:2])
    i = reason.find(short)
    return reason[max(0, i - 70):i + 50].replace("\n", " ") if i >= 0 else reason[:120]


def stale_holds(live: list[dict], closed: list[dict]) -> list[dict]:
    """[{atom, named, met}] for every held row that names an atom already at target or closed."""
    by_id = {r["id"]: r for r in live}
    closed_ids = {r["id"] for r in closed}
    every = list(by_id) + sorted(closed_ids - set(by_id))

    def resolve(token: str) -> str | None:
        if token in by_id or token in closed_ids:
            return token
        hits = [i for i in every if i.startswith(token + "_")]
        return hits[0] if len(hits) == 1 else None

    out = []
    for row in live:
        reason = str(row.get("block_reason") or "")
        blocked = row.get("blocked_on") or []
        blocked = [blocked] if isinstance(blocked, str) else list(blocked)
        if not reason and not blocked:
            continue
        named = {resolve(str(b)) for b in blocked} | {resolve(t) for t in _SHORT.findall(reason)}
        named = {n for n in named if n and n != row["id"]}
        met = sorted(n for n in named if n in closed_ids or _met(by_id.get(n, {})))
        if met:
            out.append({"atom": row["id"], "met": met,
                        "where": {m: _context(reason, m, blocked) for m in met}})
    return out


def report(map_path: Path = MAP, closed_path: Path = CLOSED) -> dict:
    """The brief's reading: the stale holds, or why they could not be read (never a silent [])."""
    try:
        return {"stale": stale_holds(_rows(map_path), _rows(closed_path) if closed_path.exists() else [])}
    except Exception as exc:  # noqa: BLE001 -- an unread map is reported, not read as "none stale"
        return {"stale": None, "unavailable_because": f"{type(exc).__name__}: {exc}"}
