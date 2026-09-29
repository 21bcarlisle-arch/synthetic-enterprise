#!/usr/bin/env python3
"""The director's one-word dial over the three routes that spend model tokens.

REUSE: background/tick_mode.py
CLASS: CUSTOM
INDEX: searched "tick mode", "cadence", "slow down", "timer", "restore". The kill switch
       (`.build_executor_enabled`) is director-reserved and all-or-nothing; the per-lane dials only
       re-weight and may never zero a lane (Rule 0); `~/.cache/synthetic-enterprise/restore_tick.sh`
       and `timer_backup_20260925/` were the hand-edited slowdown this replaces. The product/harness
       split is NOT restated here: `supervisor._is_product_atom` is the one definition.

    python3 -m background.tick_mode                       # show the mode in force and why
    python3 -m background.tick_mode slow --for 36h        # reverts to normal by itself
    python3 -m background.tick_mode product-only --until 2026-09-28T02:50Z
    python3 -m background.tick_mode normal

WHAT SPENDS, MEASURED BEFORE THIS WAS DESIGNED (docs/staging/SEAT_FINDING_WHICH_ROUTES_SPEND_TOKENS_
2026-09-27.md). Only three unattended routes start a `claude` session: worker-tick, seat-executor,
delivery-seat. Reconciliations, heartbeats, the publisher and every other daemon spend no model
tokens at all, so they are not gated here and slowing them would buy nothing. The worker tick's
doorbell carries the reactive reasons (unprocessed staging, the HEAD-red register, publish) on
almost every tick, which is why product-only cannot be a filter on the atom draw alone: it has to
decide the SPAWN, or the reactive reasons keep every tick alive.

THE MODE OWNS THE CADENCE, NOT THE TIMER FILES. The three systemd timers stay at their normal
schedule and act as a base clock; each route asks `gate()` before it spawns, and a mode stretches
the minimum spacing between SPAWNS (a stand-down is a cheap Python read). So a slowdown edits no
unit file and its restore is a comparison at read time: a mode set with an expiry has reverted the
moment the expiry passes, with no timer, script or daemon that has to fire for it to happen.

The mode is the director's to set. Nothing here reads a usage figure or infers a budget -- the
allowance is not readable from inside the machine.
"""
from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

MODE_FILE = Path.home() / ".config" / "synthetic-enterprise" / "tick_mode.json"
SPAWN_FILE = Path.home() / ".cache" / "synthetic-enterprise" / "tick_mode_spawns.json"
HISTORY_FILE = Path.home() / ".cache" / "synthetic-enterprise" / "tick_mode_history.jsonl"

ROUTES = ("worker-tick", "seat-executor", "delivery-seat")
MODES = ("normal", "slow", "product-only", "fold-only", "off")
DEFAULT = "normal"

H = 3600
#: Minimum seconds between SPAWNS per route. 0 = the timer's own cadence; None = never spawns.
#: `slow` is the director's own slowdown of 2026-09-06 and 2026-09-25, as the hand-edited timers
#: set it (restore_tick.sh records the pair): worker tick every 4h, executor every 4h, delivery
#: seat every 12h.
CADENCE = {
    "normal":       {"worker-tick": 0,    "seat-executor": 0,    "delivery-seat": 0},
    "slow":         {"worker-tick": 4 * H, "seat-executor": 4 * H, "delivery-seat": 12 * H},
    "product-only": {"worker-tick": 0,    "seat-executor": 0,    "delivery-seat": 0},
    "fold-only":    {"worker-tick": None, "seat-executor": 0,    "delivery-seat": None},
    "off":          {"worker-tick": None, "seat-executor": None, "delivery-seat": None},
}


def _read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _write_json(path: Path, data) -> None:
    from background.live_ledger_guard import guard_live_ledger_write
    path = guard_live_ledger_write(path, writer="tick_mode._write_json")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def current(now: float | None = None, path: Path | None = None) -> dict:
    """The mode in force: {mode, until, set_at, reverted_from, why}.

    An unreadable or unknown mode reads as `normal` WITH the reason, never silently: a dial that
    broke into `off` would stop the machine and nobody would know why.
    """
    now = time.time() if now is None else now
    p = path or MODE_FILE
    raw = _read_json(p, None)
    if not isinstance(raw, dict):
        return {"mode": DEFAULT, "until": None, "set_at": None, "reverted_from": None,
                "why": "mode file unreadable -- reading normal" if p.exists() else "no mode set"}
    mode = raw.get("mode")
    if mode not in MODES:
        return {"mode": DEFAULT, "until": None, "set_at": raw.get("set_at"), "reverted_from": None,
                "why": f"unknown mode {mode!r} in the file -- reading normal"}
    until = raw.get("until")
    if isinstance(until, (int, float)) and now >= until:
        then = raw.get("then") if raw.get("then") in MODES else DEFAULT
        return {"mode": then, "until": None, "set_at": raw.get("set_at"), "reverted_from": mode,
                "why": f"{mode} expired at {_iso(until)}; reverted to {then}"}
    return {"mode": mode, "until": until, "set_at": raw.get("set_at"), "reverted_from": None,
            "why": f"set at {_iso(raw.get('set_at'))}" + (f", reverts at {_iso(until)}" if until else "")}


def set_mode(mode: str, *, until: float | None = None, then: str = DEFAULT,
             now: float | None = None, path: Path | None = None,
             history: Path | None = None) -> dict:
    if mode not in MODES:
        raise ValueError(f"unknown mode {mode!r}; one of {', '.join(MODES)}")
    if then not in MODES:
        raise ValueError(f"unknown revert mode {then!r}")
    now = time.time() if now is None else now
    if until is not None and until <= now:
        raise ValueError(f"expiry {_iso(until)} is not in the future")
    rec = {"mode": mode, "set_at": now, "until": until, "then": then}
    _write_json(path or MODE_FILE, rec)
    from background.live_ledger_guard import guard_live_ledger_write
    h = guard_live_ledger_write(history or HISTORY_FILE, writer="tick_mode.set_mode")
    h.parent.mkdir(parents=True, exist_ok=True)
    with h.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


def note_spawn(route: str, now: float | None = None, path: Path | None = None) -> None:
    """Record that `route` started a model session. Called by the route at the spawn."""
    p = path or SPAWN_FILE
    data = _read_json(p, {})
    if not isinstance(data, dict):
        data = {}
    data[route] = time.time() if now is None else now
    try:
        _write_json(p, data)
    except OSError:
        pass  # a lost stamp only lets the next spawn come sooner; it never stops one


def gate(route: str, now: float | None = None, *, mode_path: Path | None = None,
         spawn_path: Path | None = None) -> tuple[bool, str, str]:
    """(may_spawn, mode, reason). The reason names the mode on BOTH answers, so a log reads why."""
    if route not in ROUTES:
        raise ValueError(f"unknown route {route!r}")
    now = time.time() if now is None else now
    cur = current(now, mode_path)
    mode = cur["mode"]
    spacing = CADENCE[mode][route]
    if spacing is None:
        return False, mode, f"tick mode {mode}: {route} does not spawn ({cur['why']})"
    if spacing:
        last = _read_json(spawn_path or SPAWN_FILE, {})
        last = last.get(route) if isinstance(last, dict) else None
        if isinstance(last, (int, float)) and now - last < spacing:
            return (False, mode, f"tick mode {mode}: {route} spawns at most every "
                    f"{spacing // H}h; last spawn {_iso(last)}, next from {_iso(last + spacing)}")
    return True, mode, f"tick mode {mode} ({cur['why']})"


# ── product-only and fold-only: what each route may take ────────────────────────────────────────

_PRODUCT_ONLY_BLOCK = ("tick mode product-only: a machinery lane is not drawn while the mode is "
                       "set")


def product_draw() -> str | None:
    """The worker tick's draw under product-only.

    ANYTHING THAT BLOCKS A LANDING GOES THROUGH WHOLE: the supervisor's priority-zero rungs (a wedged
    publish gate, a dead producer, a persistent operational red) return the ordinary draw. Then the
    director's own staged words. Then ONE maturity-map atom from a product lane, drawn by the
    supervisor's own weighted pick over a view of the map in which every harness atom is blocked --
    a block, not a removal, so a product atom's dependency on a harness atom is judged exactly as
    before. The reactive reasons (findings, the HEAD-red register) are not offered at all.
    """
    import types

    from background import supervisor as s
    if s._priority_zero_active():
        return s._self_refill_draw()
    director = [d for d in (s._real_staged_instructions() or [])
                if Path(str(d)).name.startswith(("DIRECTOR_", "from_rich"))]
    if director:
        return "TICK MODE product-only -- the director's staged words: " + s._differentiated_staging(director)
    real = s.map_store

    def load_atoms(*a, **k):
        out = []
        for atom in real.load_atoms(*a, **k):
            if isinstance(atom, dict) and not s._is_product_atom(atom):
                atom = {**atom, "blocked_on": _PRODUCT_ONLY_BLOCK}
            out.append(atom)
        return out

    view = types.SimpleNamespace(**{k: getattr(real, k) for k in dir(real) if not k.startswith("__")})
    view.load_atoms = load_atoms
    s.map_store = view
    try:
        pick = s._maturity_map_draw()
    finally:
        s.map_store = real
    return f"TICK MODE product-only -- one product-lane atom from the maturity map: {pick}" if pick else None


_ATOM_PREFIX = re.compile(r"\b([A-Z][A-Z0-9]{0,4}_\d+[a-z]?)(?:_|\b)")
_PRODUCT_ROOTS = ("company/", "saas/", "simulation/", "sim/", "site/", "interface/",
                  "docs/market_research/", "docs/institutional/", "docs/domain_artefact_library/")


#: Where any work leaves evidence (a staging record, an observability artefact, a scratch path
#: outside the repo) or a directory that holds both sides (`tools/` carries the arms runners and
#: the landing doors alike). Naming one says nothing about which side the work is on.
_NEUTRAL_ROOTS = ("docs/staging/", "docs/observability/", "tools/", "/")


def _item_text(item: dict) -> str:
    return " ".join(str(item.get(k) or "") for k in ("id", "what", "why", "done_means"))


def item_is_product(item: dict, atoms: list | None = None) -> tuple[bool, str]:
    """Is a seat-executor item product work? Items carry no lane, so this reads what they NAME.

    Map atoms named in the text decide first (by full id, or the `W2_19`-style prefix), then lane
    names, then paths. An item that names nothing classifiable is NOT product, with that reason:
    under a mode the director set to stop machinery, the unknown is the side that waits.
    """
    from background import supervisor as s
    lane = item.get("lane")
    if lane:
        return (lane not in s.HARNESS_LANES), f"declares lane {lane}"
    text = _item_text(item)
    if atoms is None:
        from tools import maturity_map_store as ms
        atoms = ms.load_live_atoms()
    named = []
    prefixes = set(_ATOM_PREFIX.findall(text))
    for a in atoms:
        aid = str(a.get("id") or "") if isinstance(a, dict) else ""
        if aid and (aid in text or any(aid == p or aid.startswith(p + "_") for p in prefixes)):
            named.append(a)
    if named:
        harness = [a["id"] for a in named if not s._is_product_atom(a)]
        if harness:
            return False, f"names harness atom(s) {', '.join(harness[:3])}"
        return True, f"names product atom(s) {', '.join(a['id'] for a in named[:3])}"
    if any(lane in text for lane in s.HARNESS_LANES):
        return False, "names a harness lane"
    lanes = {a.get("lane") for a in atoms if isinstance(a, dict) and s._is_product_atom(a)}
    hit = sorted(lane for lane in lanes if lane and lane in text)
    if hit:
        return True, f"names product lane(s) {', '.join(hit)}"
    paths = [p for p, _v in ((item.get("path_reading") or {}).get("paths") or [])]
    paths += re.findall(r"[\w./-]+\.(?:py|md|json|yaml|html|js)\b", text)
    paths = [p for p in paths if not p.startswith(_NEUTRAL_ROOTS)]
    if paths:
        prod = [p for p in paths if p.startswith(_PRODUCT_ROOTS)]
        if prod and len(prod) == len(paths):
            return True, f"names only product paths ({prod[0]}...)"
        return False, f"names machinery path(s) ({next(p for p in paths if not p.startswith(_PRODUCT_ROOTS))})"
    return False, "names no atom, lane or path, so it cannot show it is product work"


# suppression-lint: not-a-suppression item_is_fold -- classifies whether an item grades an in-flight long job (fold-only mode decides what a tick draws, not whether anything pages)
def item_is_fold(item: dict, records: list | None = None) -> tuple[bool, str]:
    """fold-only: the item is grading an in-flight long job iff it names one in the launch register."""
    if records is None:
        from background import launch_liveness
        records = launch_liveness.load()
    text = _item_text(item)
    for r in records:
        for key in ("job", "unit", "artefact"):
            v = str(r.get(key) or "")
            if v and (v in text or (key == "artefact" and Path(v).name in text)):
                return True, f"names long job {r.get('job')}"
    return False, "names no long job in the launch register"


def item_allowed(mode: str, item: dict) -> tuple[bool, str]:
    if mode == "product-only":
        return item_is_product(item)
    if mode == "fold-only":
        return item_is_fold(item)
    return True, ""


# ── operator surface ────────────────────────────────────────────────────────────────────────────

def _iso(ts) -> str:
    if not isinstance(ts, (int, float)):
        return "never"
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def _parse_for(s: str) -> float:
    m = re.fullmatch(r"(\d+(?:\.\d+)?)([mhd])", s.strip())
    if not m:
        raise ValueError(f"--for wants e.g. 90m, 36h, 2d; got {s!r}")
    return float(m.group(1)) * {"m": 60, "h": H, "d": 24 * H}[m.group(2)]


def _parse_until(s: str) -> float:
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        raise ValueError("--until needs a timezone (e.g. 2026-09-28T02:50Z)")
    return dt.timestamp()


def describe(now: float | None = None) -> str:
    cur = current(now)
    lines = [f"tick mode: {cur['mode']} -- {cur['why']}"]
    for r in ROUTES:
        ok, _m, why = gate(r, now)
        lines.append(f"  {r:14s} {'may spawn' if ok else 'held'}: {why}")
    return "\n".join(lines)


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mode", nargs="?", choices=MODES)
    ap.add_argument("--for", dest="for_", help="expire after e.g. 90m, 36h, 2d")
    ap.add_argument("--until", help="expire at an ISO time with zone, e.g. 2026-09-28T02:50Z")
    ap.add_argument("--then", default=DEFAULT, choices=MODES, help="mode to revert to (default normal)")
    a = ap.parse_args(argv)
    if a.mode:
        until = None
        try:
            if a.for_ and a.until:
                raise ValueError("give --for or --until, not both")
            if a.for_:
                until = time.time() + _parse_for(a.for_)
            elif a.until:
                until = _parse_until(a.until)
            set_mode(a.mode, until=until, then=a.then)
        except ValueError as e:
            print(f"refused: {e}", file=sys.stderr)
            return 2
    print(describe())
    return 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/tick_mode.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("tick_mode")
    sys.exit(main())
