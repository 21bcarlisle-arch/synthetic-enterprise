#!/usr/bin/env python3
"""
REUSE: tools/lane_formation.py
CLASS: CUSTOM
INDEX: searched "lane", "formation", "draw shape", "breadth", "concentration", "lane balance".
       Eleven rows mention lanes and every one of them answers "MAY this be drawn" -- the
       coupled-triad gate, the file_scope gate, the blocked-atom probe, the pass ceiling landed
       today. Not one answers "what WAS drawn, and in what proportion". That is the gap the
       director named on 2026-08-19: "Nothing currently measures the shape of the draw across
       lanes, only what may be drawn."
       The closest row is `tools/discovery_pass_ceiling.py`, written hours earlier, and it is
       genuinely adjacent -- both read the map and join it against history to find work that has
       stopped paying. It is not extended because it answers a per-ATOM question (has THIS atom
       stopped moving) and this answers a cross-LANE one (is the whole draw pooling). An atom can
       be perfectly healthy by the ceiling's test while the formation is collapsing around it,
       which is precisely today's state: no atom is individually alarming and one lane holds 47%.
       `tools/effort_calibration.py` reads the same map fields and is a different subject again
       (how LONG work takes, not WHERE it goes). Reused rather than reimplemented: the map read
       and the short-prefix attribution idea both follow the shape those two already use.

THE SHAPE OF THE DRAW ACROSS LANES -- made visible, so formation slip can be acted on.

Director ruling, 2026-08-19, granting epoch latitude WITH a guard:

    "Crossing epochs to scout or type interfaces is fine ... The failure I care about is a
     single lane going deeper and deeper across multiple epochs while the rest stands still --
     depth without breadth. Nothing currently measures the shape of the draw across lanes, only
     what may be drawn. Make that visible, act on it yourself when formation slips."

WHAT THIS IS, AND THE ONE THING IT MUST NEVER BECOME. This is a DIAGNOSTIC (R12). It reports
where the draw actually went. It does NOT weight the draw, veto a lane, or hand the supervisor a
quota to satisfy -- and the reason is R12 itself rather than modesty: the moment a lane share
becomes a target, the cheapest way to satisfy it is to commit something small in a starved lane,
which produces the SHAPE of breadth with none of the substance. A measure that can be gamed by
the thing it measures is worse than no measure. So this prints, alarms, and stops. The acting is
the director's or mine, in the open.

FAIL-CLOSED DIRECTION: toward UNAVAILABLE, never toward "formation held". A formation report that
cannot read git or the map must say so loudly. "The lanes look balanced", computed from sources
nobody could read, is the reading that would let a collapse run for another week -- and this
project has already had one control (`resource_headroom`) that was silent because it never ran at
all. Silence must never be indistinguishable from health.

THE ATTRIBUTION IS PARTIAL AND SAYS SO. Commit subjects name atoms by SHORT PREFIX (`EP16`,
`SITE4`), not by full id, and many commits name no atom at all. On the 2026-08-12..19 window
that leaves ~32% of commits attributable. That is a real limit on the numbers, not a rounding
detail, so `formation()` returns `coverage` alongside every share and the CLI prints it on the
same screen. A share computed from a third of the evidence is still the best available signal
about pooling -- it is not a precise account of effort, and nothing here should be read as one.
"""
from __future__ import annotations

import collections
import json
import re
import subprocess
from pathlib import Path
from typing import Any

PROJECT_DIR = Path(__file__).resolve().parents[1]
MAP_PATH = PROJECT_DIR / "docs" / "design" / "maturity_map.yaml"
STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".lane_formation_state.json"

DEFAULT_WINDOW_DAYS = 7

# THE TWO SLIP CONDITIONS. Both are R12 sanity flags -- they trigger DIAGNOSIS (R4), never a
# correction applied to the draw. They are set where today's real, measured state trips them,
# deliberately: a threshold placed just outside the current reading is a threshold chosen to stay
# quiet, and this project has shipped one of those before (the RO clamp test).
POOLING_SHARE = 0.40      # one lane holding more than this much of the attributed draw
STARVED_LANE_FLOOR = 1    # a lane with buildable atoms and fewer than this many draws is starved
STARVED_LANE_COUNT = 3    # this many starved lanes at once is a formation slip, not noise


class FormationUnavailable(RuntimeError):
    """The shape could not be computed. NEVER silently a healthy reading."""


def _atoms() -> list[dict]:
    try:
        import yaml
        loaded = yaml.safe_load(MAP_PATH.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise FormationUnavailable(f"the maturity map could not be read: {exc}") from exc
    atoms = loaded if isinstance(loaded, list) else (loaded or {}).get("atoms", [])
    atoms = [a for a in atoms if isinstance(a, dict) and a.get("id")]
    if not atoms:
        raise FormationUnavailable("the maturity map parsed to zero atoms")
    return atoms


def _subjects(window_days: int) -> list[str]:
    try:
        r = subprocess.run(
            ["git", "log", f"--since={window_days} days ago", "--pretty=%s"],
            cwd=str(PROJECT_DIR), capture_output=True, text=True, timeout=60,
        )
    except Exception as exc:  # noqa: BLE001
        raise FormationUnavailable(f"git log failed: {exc}") from exc
    if r.returncode != 0:
        raise FormationUnavailable(f"git log exited {r.returncode}: {r.stderr.strip()[:200]}")
    subjects = [s for s in r.stdout.splitlines() if s.strip()]
    if not subjects:
        raise FormationUnavailable(
            f"no commits in the last {window_days} days -- that is a stall to investigate, "
            "not a formation reading"
        )
    return subjects


def _prefix_index(atoms: list[dict]) -> tuple[dict[str, str], set[str]]:
    """short prefix -> atom id, plus the prefixes that COLLIDE.

    `H27_payment_belief_gap` and `H27_phone_act_channel` share the prefix `H27`, so a subject
    beginning "H27 " cannot be attributed to one of them. Collisions are RETURNED rather than
    silently resolved to whichever came first, because a caller reporting per-atom counts needs
    to know which are unreliable. Lane-level counts survive a collision when both atoms sit in
    the same lane, which is the common case and why the lane view is the trustworthy one.
    """
    seen: dict[str, str] = {}
    collided: set[str] = set()
    for a in atoms:
        p = str(a["id"]).split("_")[0]
        if p in seen and seen[p] != a["id"]:
            collided.add(p)
        seen.setdefault(p, a["id"])
    return seen, collided


def formation(window_days: int = DEFAULT_WINDOW_DAYS) -> dict[str, Any]:
    """The measured shape of the draw. Raises FormationUnavailable rather than guessing."""
    atoms = _atoms()
    subjects = _subjects(window_days)
    prefix_to_id, collided = _prefix_index(atoms)
    by_id = {a["id"]: a for a in atoms}
    keys = sorted(prefix_to_id, key=len, reverse=True)

    per_lane: collections.Counter = collections.Counter()
    per_epoch: collections.Counter = collections.Counter()
    per_atom: collections.Counter = collections.Counter()
    attributed = 0
    for subj in subjects:
        hit = next((k for k in keys if re.match(rf"^{re.escape(k)}\b", subj)), None)
        if hit is None:
            continue
        atom = by_id[prefix_to_id[hit]]
        per_lane[atom.get("lane", "?")] += 1
        per_epoch[atom.get("epoch")] += 1
        per_atom[atom["id"]] += 1
        attributed += 1

    if not attributed:
        raise FormationUnavailable(
            f"{len(subjects)} commits in the window and NONE names an atom -- the attribution "
            "rule is broken or the loop has stopped naming its work; either way this is not a "
            "formation reading"
        )

    # Lanes that COULD have been drawn -- a lane with nothing buildable is not starved, it is done.
    buildable_lanes = {
        a.get("lane", "?") for a in atoms
        if a.get("loop_stage") == "build"
        and (a.get("level_current") or 0) < (a.get("level_target") or 0)
    }
    starved = sorted(lane for lane in buildable_lanes if per_lane[lane] < STARVED_LANE_FLOOR)
    shares = {lane: n / attributed for lane, n in per_lane.items()}
    top_lane, top_n = per_lane.most_common(1)[0]

    reasons: list[str] = []
    if top_n / attributed > POOLING_SHARE:
        reasons.append(
            f"POOLING: {top_lane} holds {top_n / attributed:.1%} of the attributed draw "
            f"(> {POOLING_SHARE:.0%})"
        )
    if len(starved) >= STARVED_LANE_COUNT:
        reasons.append(
            f"STARVATION: {len(starved)} lane(s) with buildable atoms took no draw at all "
            f"({', '.join(starved)})"
        )

    return {
        "window_days": window_days,
        "commits": len(subjects),
        "attributed": attributed,
        "coverage": attributed / len(subjects),
        "collided_prefixes": sorted(collided),
        "lanes": dict(per_lane),
        "shares": shares,
        "epochs": {str(k): v for k, v in per_epoch.items()},
        "top_lane": top_lane,
        "top_share": top_n / attributed,
        "buildable_lanes": sorted(buildable_lanes),
        "starved_lanes": starved,
        "slipped": bool(reasons),
        "reasons": reasons,
        "busiest_atoms": per_atom.most_common(10),
    }


def observe(window_days: int = DEFAULT_WINDOW_DAYS) -> dict[str, Any]:
    """R5: report only on a TRANSITION of the verdict, so a standing slip is not re-announced
    every tick and muted. An UNAVAILABLE reading is itself a state and alarms on entry."""
    try:
        shape = formation(window_days)
        verdict = "SLIPPED" if shape["slipped"] else "HELD"
    except FormationUnavailable as exc:
        shape, verdict = {"error": str(exc)}, "UNAVAILABLE"

    previous = None
    try:
        previous = json.loads(STATE_FILE.read_text(encoding="utf-8")).get("verdict")
    except Exception:  # noqa: BLE001
        pass

    changed = previous != verdict
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps({"verdict": verdict}, indent=2), encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass

    out = {"verdict": verdict, "changed": changed, **shape}
    if changed and verdict == "SLIPPED":
        out["alarm"] = "FORMATION SLIPPED: " + "; ".join(shape.get("reasons", []))
    elif changed and verdict == "UNAVAILABLE":
        out["alarm"] = f"FORMATION UNREADABLE: {shape.get('error')}"
    return out


def main() -> int:
    try:
        s = formation()
    except FormationUnavailable as exc:
        print(f"FORMATION UNAVAILABLE: {exc}")
        return 2
    print(f"Draw shape over {s['window_days']} days: {s['attributed']} of {s['commits']} "
          f"commits attributed to an atom ({s['coverage']:.0%} coverage).")
    if s["collided_prefixes"]:
        print(f"  per-atom counts unreliable for shared prefixes: "
              f"{', '.join(s['collided_prefixes'])}")
    print()
    for lane, n in sorted(s["lanes"].items(), key=lambda kv: -kv[1]):
        bar = "#" * int(s["shares"][lane] * 50)
        print(f"  {lane:26s} {n:4d}  {s['shares'][lane]:5.1%}  {bar}")
    print()
    for lane in s["starved_lanes"]:
        print(f"  STARVED (buildable, no draw): {lane}")
    print()
    print("FORMATION SLIPPED" if s["slipped"] else "FORMATION HELD")
    for r in s["reasons"]:
        print(f"  - {r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
