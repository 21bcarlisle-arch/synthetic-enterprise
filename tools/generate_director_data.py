#!/usr/bin/env python3
"""Director-window DELTA generator -- "what changed since you last looked".

PURPOSE
    The Director's Window (site/director/) renders full state: the reserved
    queue, the daemon table, the twin counters, the plan headline. Reading it
    costs the director a full-page diff-by-eye every visit. This generator
    computes the DELTA between the window's CURRENT state and its state as of
    a recorded LAST LOOK, so the page can lead with what moved.

    The page already carries a per-browser localStorage marker (section
    "This browser's last visit"). That marker is per-device and dies with the
    browser profile. This generator adds the DURABLE half: a stamp committed
    to the repo (site/data/director_last_look.json) that survives a publish,
    a new device, and a cleared browser.

GUARANTEES (each one has a test that FAILS when it is broken -- R15)
    G1  A plain regeneration NEVER advances the stamp. The stamp moves ONLY on
        an explicit `--mark-seen` run. This is the whole feature: a delta view
        whose baseline silently re-bases on every regeneration always reports
        "nothing changed" (or, symmetrically, "everything is new") and is
        therefore worthless. Regenerating the delta is not looking at it.
    G2  A stamp that is missing / empty / unreadable / malformed / of a
        different version yields stamp_status != "ok", changed=None and
        counts=None. The generator NEVER fabricates a delta from a lost stamp
        -- neither "everything is new" nor "nothing changed". The page renders
        that state as a visible failure block, distinguishable from a quiet
        interval. A lost stamp is a FAILED check, not a passed one.
    G3  Key presence is checked, not just truthiness: a stamp carrying
        `state: {}` (or missing `reserved_ids`) is MALFORMED, not "a look at
        which nothing existed". That empty-state-reads-as-everything-new shape
        is the exact fail-open this feature must not have.
    G4  The delta records the source stamps of the feeds it was computed from,
        so the page can independently detect that this feed has gone stale
        against the feeds it actually fetched (an unwired/frozen generator is
        otherwise silent).

WHY THIS SHAPE
    The delta is derived from the feeds the director page ALREADY renders
    (decisions.json, director_reserved.json, agent_status.json,
    director_twin.json, provisional_plan.json). No new state model, no new
    write affordance, no server-side read receipt of the director's browsing.
    R12: these counts are a diagnostic, never a target.

USAGE
    python3 tools/generate_director_data.py               # recompute the delta
    python3 tools/generate_director_data.py --mark-seen   # record a look NOW
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
SITE_DATA = PROJECT / "site" / "data"

STAMP_NAME = "director_last_look.json"
DELTA_NAME = "director_delta.json"

STAMP_VERSION = 1

# Must match HEALTH_STALE_HOURS in site/director/index.html -- the delta's idea
# of "stale" is the same one the health table renders.
HEALTH_STALE_HOURS = 6.0

# Every one of these must be PRESENT in a stamp's state for it to count as
# readable. Presence, not truthiness (G3).
REQUIRED_STATE_KEYS = (
    "latest_decision_ts",
    "decision_count",
    "reserved_ids",
    "daemon_status",
    "twin_fidelity",
    "open_atoms",
)

FIDELITY_KEYS = ("answered", "routed_to_director", "overturned", "canon_version")

HOW_THE_STAMP_ADVANCES = (
    "The last-look stamp advances ONLY on an explicit `--mark-seen` run "
    "(tools/generate_director_data.py --mark-seen). Regenerating this feed "
    "never moves it -- a baseline that re-bases on every regeneration would "
    "make the panel permanently say 'nothing changed'."
)


# --------------------------------------------------------------------------- #
# Feed loading
# --------------------------------------------------------------------------- #
FEED_FILES = {
    "decisions": "decisions.json",
    "reserved": "director_reserved.json",
    "health": "agent_status.json",
    "twin": "director_twin.json",
    "plan": "provisional_plan.json",
}


def load_feeds(site_data: Path) -> dict:
    """Read the feeds the director page renders. A missing feed reads as {} --
    that degrades a FIELD of the delta, and is visible in source_stamps; it is
    never allowed to silently look like a change (see snapshot_state)."""
    feeds = {}
    for key, name in FEED_FILES.items():
        path = site_data / name
        try:
            feeds[key] = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            feeds[key] = {}
    return feeds


def _parse_ts(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _age_seconds(value, now: datetime):
    ts = _parse_ts(value)
    if ts is None:
        return None
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return (now - ts).total_seconds()


# --------------------------------------------------------------------------- #
# The comparable state
# --------------------------------------------------------------------------- #
def snapshot_state(feeds: dict, now: datetime) -> dict:
    """The canonical, comparable director-window state.

    Every key in REQUIRED_STATE_KEYS is always present, so a stamp written by
    this function is never malformed by construction."""
    decisions = (feeds.get("decisions") or {}).get("decisions") or []
    stamps = [d.get("timestamp") for d in decisions if d.get("timestamp")]
    latest_decision_ts = max(stamps) if stamps else None

    reserved_items = (feeds.get("reserved") or {}).get("items") or []
    reserved_ids = sorted(
        str(it.get("item_id")) for it in reserved_items if it.get("item_id")
    )

    daemon_status = {}
    for agent in (feeds.get("health") or {}).get("agents") or []:
        name = agent.get("name")
        if not name:
            continue
        status = str(agent.get("status") or "").lower()
        if status == "retired":
            daemon_status[str(name)] = "retired"
            continue
        age = _age_seconds(agent.get("last_heartbeat"), now)
        daemon_status[str(name)] = (
            "stale" if (age is None or age > HEALTH_STALE_HOURS * 3600) else "live"
        )

    fidelity = (feeds.get("twin") or {}).get("fidelity") or {}
    twin_fidelity = {k: fidelity.get(k) for k in FIDELITY_KEYS}

    open_atoms = ((feeds.get("plan") or {}).get("concurrency") or {}).get(
        "total_open_atoms"
    )

    return {
        "latest_decision_ts": latest_decision_ts,
        "decision_count": len(decisions),
        "reserved_ids": reserved_ids,
        "daemon_status": daemon_status,
        "twin_fidelity": twin_fidelity,
        "open_atoms": open_atoms,
    }


def source_stamps(feeds: dict) -> dict:
    """The provenance of the feeds this delta was computed from. The page
    compares these against the feeds IT fetched -- an independent check that
    this generator has not frozen (G4)."""
    return {
        "reserved_generated_at": (feeds.get("reserved") or {}).get("generated_at"),
        "health_last_updated": (feeds.get("health") or {}).get("last_updated"),
        "decisions_generated_at": (feeds.get("decisions") or {}).get("generated_at"),
    }


# --------------------------------------------------------------------------- #
# The stamp
# --------------------------------------------------------------------------- #
def load_stamp(path: Path):
    """Return (status, stamp_or_None, problem_or_None).

    status is one of: ok | missing | empty | unreadable | malformed |
    version_mismatch. Anything but "ok" means the delta CANNOT be computed --
    the caller must not invent one (G2/G3)."""
    if not path.exists():
        return "missing", None, "no last-look stamp file at {}".format(path.name)
    try:
        raw = path.read_text(encoding="utf-8")
    except Exception as exc:
        return "unreadable", None, "stamp could not be read: {}".format(exc)
    if not raw.strip():
        return "empty", None, "stamp file is empty"
    try:
        stamp = json.loads(raw)
    except Exception as exc:
        return "unreadable", None, "stamp is not valid JSON: {}".format(exc)
    if not isinstance(stamp, dict):
        return "malformed", None, "stamp is not an object"
    if stamp.get("stamp_version") != STAMP_VERSION:
        return (
            "version_mismatch",
            None,
            "stamp version {!r} != expected {}".format(
                stamp.get("stamp_version"), STAMP_VERSION
            ),
        )
    state = stamp.get("state")
    if not isinstance(state, dict):
        return "malformed", None, "stamp carries no state object"
    missing = [k for k in REQUIRED_STATE_KEYS if k not in state]
    if missing:
        return (
            "malformed",
            None,
            "stamp state is missing required keys: {}".format(", ".join(missing)),
        )
    if not stamp.get("recorded_at"):
        return "malformed", None, "stamp carries no recorded_at"
    return "ok", stamp, None


def write_stamp(path: Path, state: dict, now: datetime, recorded_by: str) -> dict:
    stamp = {
        "stamp_version": STAMP_VERSION,
        "recorded_at": now.isoformat(),
        "recorded_by": recorded_by,
        "note": HOW_THE_STAMP_ADVANCES,
        "state": state,
    }
    path.write_text(json.dumps(stamp, indent=2) + "\n", encoding="utf-8")
    return stamp


# --------------------------------------------------------------------------- #
# The delta
# --------------------------------------------------------------------------- #
def compute_delta(prev: dict, cur: dict, feeds: dict) -> dict:
    """Delta over the fields the director page already renders."""
    prev_latest = prev.get("latest_decision_ts")
    decisions = (feeds.get("decisions") or {}).get("decisions") or []
    new_decisions = [
        {"timestamp": d.get("timestamp"), "what": d.get("what")}
        for d in decisions
        if d.get("timestamp") and (not prev_latest or d["timestamp"] > prev_latest)
    ]
    new_decisions.sort(key=lambda d: d["timestamp"], reverse=True)

    prev_reserved = list(prev.get("reserved_ids") or [])
    cur_reserved = list(cur.get("reserved_ids") or [])
    added_reserved = [i for i in cur_reserved if i not in prev_reserved]
    cleared_reserved = [i for i in prev_reserved if i not in cur_reserved]

    prev_daemons = dict(prev.get("daemon_status") or {})
    cur_daemons = dict(cur.get("daemon_status") or {})
    newly_stale = sorted(
        n
        for n, s in cur_daemons.items()
        if s == "stale" and prev_daemons.get(n) not in (None, "stale")
    )
    recovered = sorted(
        n
        for n, s in cur_daemons.items()
        if s == "live" and prev_daemons.get(n) == "stale"
    )
    appeared = sorted(n for n in cur_daemons if n not in prev_daemons)
    disappeared = sorted(n for n in prev_daemons if n not in cur_daemons)

    prev_fid = dict(prev.get("twin_fidelity") or {})
    cur_fid = dict(cur.get("twin_fidelity") or {})
    fidelity_moves = [
        {"field": k, "from": prev_fid.get(k), "to": cur_fid.get(k)}
        for k in FIDELITY_KEYS
        if prev_fid.get(k) != cur_fid.get(k)
    ]

    headline_moves = []
    if prev.get("open_atoms") != cur.get("open_atoms"):
        headline_moves.append(
            {
                "field": "total_open_atoms",
                "from": prev.get("open_atoms"),
                "to": cur.get("open_atoms"),
            }
        )

    counts = {
        "new_decisions": len(new_decisions),
        "reserved_changed": len(added_reserved) + len(cleared_reserved),
        "reserved_added": len(added_reserved),
        "reserved_cleared": len(cleared_reserved),
        "daemons_flipped": len(newly_stale) + len(recovered),
        "daemons_newly_stale": len(newly_stale),
        "daemons_recovered": len(recovered),
        "daemons_appeared": len(appeared),
        "daemons_disappeared": len(disappeared),
        "headline_moves": len(fidelity_moves) + len(headline_moves),
    }

    changes = []
    if new_decisions:
        changes.append(
            "{} new decision(s) logged, latest: {}".format(
                len(new_decisions), new_decisions[0].get("what") or "(no summary)"
            )
        )
    if added_reserved:
        changes.append(
            "reserved queue: {} added ({})".format(
                len(added_reserved), ", ".join(added_reserved)
            )
        )
    if cleared_reserved:
        changes.append(
            "reserved queue: {} cleared ({})".format(
                len(cleared_reserved), ", ".join(cleared_reserved)
            )
        )
    if newly_stale:
        changes.append(
            "{} daemon(s) went stale: {}".format(len(newly_stale), ", ".join(newly_stale))
        )
    if recovered:
        changes.append(
            "{} daemon(s) recovered: {}".format(len(recovered), ", ".join(recovered))
        )
    if appeared:
        changes.append("{} new daemon(s): {}".format(len(appeared), ", ".join(appeared)))
    if disappeared:
        changes.append(
            "{} daemon(s) left the table: {}".format(
                len(disappeared), ", ".join(disappeared)
            )
        )
    for move in fidelity_moves:
        changes.append(
            "twin {}: {} -> {}".format(move["field"], move["from"], move["to"])
        )
    for move in headline_moves:
        changes.append("{}: {} -> {}".format(move["field"], move["from"], move["to"]))

    return {
        "counts": counts,
        "changes": changes,
        "detail": {
            "new_decisions": new_decisions[:10],
            "reserved_added": added_reserved,
            "reserved_cleared": cleared_reserved,
            "daemons_newly_stale": newly_stale,
            "daemons_recovered": recovered,
            "daemons_appeared": appeared,
            "daemons_disappeared": disappeared,
            "fidelity_moves": fidelity_moves,
            "headline_moves": headline_moves,
        },
    }


def build_payload(feeds: dict, stamp_status: str, stamp, problem, now: datetime) -> dict:
    cur = snapshot_state(feeds, now)
    payload = {
        "generated_at": now.isoformat(),
        "stamp_version": STAMP_VERSION,
        "stamp_file": "director_last_look.json",
        "stamp_status": stamp_status,
        "stamp_problem": problem,
        "how_the_stamp_advances": HOW_THE_STAMP_ADVANCES,
        "last_look_at": None,
        "last_look_recorded_by": None,
        "changed": None,
        "counts": None,
        "changes": [],
        "detail": None,
        "current_state": cur,
        "source_stamps": source_stamps(feeds),
    }
    if stamp_status != "ok":
        # G2: no delta is invented from a lost stamp. changed stays None --
        # which is neither "nothing changed" (False) nor "everything is new".
        return payload

    payload["last_look_at"] = stamp.get("recorded_at")
    payload["last_look_recorded_by"] = stamp.get("recorded_by")
    delta = compute_delta(stamp["state"], cur, feeds)
    payload["counts"] = delta["counts"]
    payload["changes"] = delta["changes"]
    payload["detail"] = delta["detail"]
    payload["changed"] = bool(delta["changes"])
    return payload


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #
def generate(site_data: Path = SITE_DATA, mark_seen: bool = False,
             recorded_by: str = "explicit-mark-seen", now: datetime = None) -> dict:
    now = now or datetime.now(timezone.utc)
    site_data = Path(site_data)
    stamp_path = site_data / STAMP_NAME
    out_path = site_data / DELTA_NAME

    feeds = load_feeds(site_data)

    if mark_seen:
        # The ONLY path that advances the baseline (G1).
        write_stamp(stamp_path, snapshot_state(feeds, now), now, recorded_by)

    stamp_status, stamp, problem = load_stamp(stamp_path)
    payload = build_payload(feeds, stamp_status, stamp, problem, now)
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--mark-seen",
        action="store_true",
        help="record a look NOW -- the only thing that advances the stamp",
    )
    parser.add_argument(
        "--by",
        default="explicit-mark-seen",
        help="who/what recorded the look (written into the stamp, for honesty)",
    )
    parser.add_argument("--site-data", default=str(SITE_DATA))
    args = parser.parse_args(argv)

    payload = generate(
        site_data=Path(args.site_data),
        mark_seen=args.mark_seen,
        recorded_by=args.by,
    )
    print(
        "Generated {} (stamp_status={}, changed={}, {} change line(s))".format(
            Path(args.site_data) / DELTA_NAME,
            payload["stamp_status"],
            payload["changed"],
            len(payload["changes"]),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
