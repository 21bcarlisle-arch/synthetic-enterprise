"""Does the work follow the director's priority order, or only the dials?

DIRECTOR, 2026-10-05: "Verify the draw follows this order, not just the dials. On 4 September a
re-ranking changed the weights and the work did not move, because the dials were not what was
choosing." So this asks two different questions, and they must be read apart:

  LIVE      the share of the BUILD draw each step holds NOW, from the supervisor's own selection
            (`_maturity_map_draw_concurrent`, its candidate filter and its weights, captured, not
            re-implemented). A later step holding more of the draw than an earlier one is a
            violation; a step whose atoms are not drawable at all is named with what blocks it.
  OUTCOME   where the LANDED work went since the order took effect: each non-merge commit on
            origin/main is attributed to the steps whose atoms' `file_scope` covers a path it
            touched. This is the leg that catches the 4 September failure, because most work does
            not arrive through the atom draw at all (Lane 0, continuations), and whichever channel
            chose, the commit lands somewhere.

The step-to-atom expression is `docs/direction/priority_order.yaml`; the order itself is the
canon's. Work in no step is reported, not judged: harness and fidelity work is real work outside
the order, and how much of it there is is the number the director needs to see.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
ORDER = ROOT / "docs" / "direction" / "priority_order.yaml"
MAP = ROOT / "docs" / "design" / "maturity_map.yaml"


def load_order(path: Path = ORDER) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {"since": str(data.get("since") or ""),
            "steps": {int(k): v for k, v in (data.get("steps") or {}).items()}}


def step_of(order: dict) -> dict[str, int]:
    return {a: k for k, v in order["steps"].items() for a in (v.get("atoms") or [])}


def live_draw() -> tuple[list[dict], list[dict], list[float]]:
    """What the supervisor's BUILD draw would use now, captured from it: every surviving candidate,
    the pool the priority order lets the primary come from, and that pool's weights. Since the draw
    began reading the order (2026-10-05) these differ: a later step's atom can be a candidate and
    still be outside the pool, and only the candidates say whether a step is drawable at all."""
    os.environ.setdefault("SE_NTFY_TOPIC", "draw-follows-the-order-dry-run")
    from background import supervisor

    captured: dict = {}
    tier = getattr(supervisor, "_follow_the_priority_order", None)

    def _seen(cands, steps, in_flight):
        captured["all"] = list(cands)
        return tier(cands, steps, in_flight)

    class _Capture:
        def choices(self, cands, weights=None, k=1):
            captured["c"], captured["w"] = list(cands), list(weights)
            return [cands[0]]

    if tier is not None:
        supervisor._follow_the_priority_order = _seen
    try:
        # THE SUPERVISOR LOGS TO STDOUT, so its gate lines would precede this tool's JSON and make
        # `--json` unparseable; measured on the first live run. Swallowed here, never re-printed.
        with contextlib.redirect_stdout(io.StringIO()):
            supervisor._maturity_map_draw_concurrent(rng=_Capture(), exclude_stalled=False)
    finally:
        if tier is not None:
            supervisor._follow_the_priority_order = tier
    pool = captured.get("c", [])
    return captured.get("all", pool), pool, [float(w) for w in captured.get("w", [])]


def live_shares(cands: list[dict], weights: list[float], steps: dict[str, int]) -> dict:
    total = sum(weights) or 1.0
    share = Counter()
    for a, w in zip(cands, weights):
        share[steps.get(a.get("id"), 0)] += w / total
    return dict(share)


def violations(shares: dict, order: dict, atoms_by_id: dict, drawable: set[str]) -> list[str]:
    """A later step outweighing an earlier one, or a step with no drawable atom (named, with why)."""
    out = []
    ranked = [k for k in sorted(order["steps"]) if order["steps"][k].get("atoms")]
    for k in ranked:
        ids = order["steps"][k]["atoms"]
        if not any(i in drawable for i in ids):
            why = []
            for i in ids:
                a = atoms_by_id.get(i)
                if a is None:
                    why.append(f"{i} is not on the map")
                elif (a.get("level_current") or 0) >= (a.get("level_target") or 0):
                    why.append(f"{i} is at target")
                elif a.get("loop_stage") == "idle":
                    why.append(f"{i} is idle ({str(a.get('block_reason') or '')[:60]})")
                elif a.get("depends_on") or a.get("blocked_on"):
                    why.append(f"{i} waits on {a.get('depends_on') or a.get('blocked_on')}")
                else:
                    why.append(f"{i} is filtered out by the supervisor's guards this cycle "
                               "(coupled-triad, pass ceiling, stall, or unmerged-work overlap)")
            out.append(f"step {k} has no drawable atom: " + "; ".join(why))
    for i, k in enumerate(ranked):
        for later in ranked[i + 1:]:
            if shares.get(later, 0.0) > shares.get(k, 0.0) and shares.get(k, 0.0) > 0:
                out.append(f"step {later} holds {shares[later]:.0%} of the draw, more than step "
                           f"{k}'s {shares[k]:.0%}")
    return out


#: A file_scope entry covering more tracked files than this names a TREE, not a subject, and
#: cannot attribute a commit to a step. Measured 2026-10-05: C30's scope lists `tests` (1,946 files)
#: and `simulation` (109), W1_10's lists `docs/design` (928), and between them they credited step 5
#: with 137 of the 252 Lane 0 items drawn in the week, harness work included. The largest
#: directory an ordered atom names that IS its subject is `company/crm` (C29), at 95.
SUBJECT_MAX_FILES = 100


def names_a_subject(scope: str) -> bool:
    out = subprocess.run(["git", "ls-files", "--", scope], cwd=str(ROOT), capture_output=True,
                         text=True)
    return len(out.stdout.splitlines()) <= SUBJECT_MAX_FILES


def outcome(order: dict, atoms_by_id: dict, since: str, ref: str = "origin/main") -> dict:
    """Landed non-merge commits since `since`, attributed to steps by file_scope coverage."""
    steps = step_of(order)
    scopes = {}
    for aid, a in atoms_by_id.items():
        if aid not in steps:
            continue
        scopes[aid] = [s for s in (str(p).rstrip("/") for p in (a.get("file_scope") or []) if p)
                       if names_a_subject(s)]
    # A BARE DATE IS READ AS THAT DATE AT THE CURRENT TIME OF DAY by git's approxidate, which
    # silently drops every commit earlier in the day; measured empty on the canon's own date.
    since = since if " " in since else since + " 00:00"
    out = subprocess.run(["git", "log", "--no-merges", f"--since={since}", "--format=\x01%h",
                          "--name-only", ref], cwd=str(ROOT), capture_output=True, text=True)
    tally = Counter()
    for block in out.stdout.split("\x01")[1:]:
        paths = [p for p in block.splitlines()[1:] if p.strip()]
        hit = set()
        for aid, sc in scopes.items():
            if aid in steps and any(p == s or p.startswith(s + "/") for p in paths for s in sc):
                hit.add(steps[aid])
        for k in hit or {0}:
            tally[k] += 1
    return dict(tally)


def report() -> dict:
    order = load_order()
    atoms = yaml.safe_load(MAP.read_text(encoding="utf-8"))
    atoms = atoms.get("atoms", atoms) if isinstance(atoms, dict) else atoms
    atoms_by_id = {x["id"]: x for x in atoms if isinstance(x, dict) and x.get("id")}
    cands, pool, weights = live_draw()
    shares = live_shares(pool, weights, step_of(order))
    return {
        "live_share_by_step": {str(k): round(v, 3) for k, v in sorted(shares.items())},
        "violations": violations(shares, order, atoms_by_id, {c.get("id") for c in cands}),
        "landed_commits_by_step_since": {"since": order["since"],
                                         **{str(k): v for k, v in sorted(
                                             outcome(order, atoms_by_id, order["since"]).items())}},
        "step_0_means": "work in no step of the order (harness, fidelity, unmapped atoms)",
    }


def render() -> str:
    """The check as the Monday step reads it."""
    r = report()
    live = ", ".join(f"step {k} {float(v):.0%}" for k, v in r["live_share_by_step"].items())
    landed = r["landed_commits_by_step_since"]
    done = ", ".join(f"step {k}: {v}" for k, v in landed.items() if k != "since")
    lines = [f"- **Live BUILD draw:** {live or 'no candidates'}.",
             f"- **Landed commits since {landed['since']}:** {done or 'none'} (step 0 is work in "
             "no step).",
             "- **Measured by** `python3 -m tools.draw_follows_the_order`."]
    lines += [f"- **VIOLATION:** {v}" for v in r["violations"]] or ["- The order holds."]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    ap.parse_args(argv)
    r = report()
    print(json.dumps(r, indent=1))
    return 1 if r["violations"] else 0


if __name__ == "__main__":
    sys.exit(main())
