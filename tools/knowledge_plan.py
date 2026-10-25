"""The forward knowledge plan: what knowledge to write next, in order, and what it will cost.

Director steer of 24 Oct, item 5 (`docs/staging/advisor/DIRECTOR_STEER_THE_MAP_ONE_CONCEPT_REGISTER_FOUR_SPINES_AND_A_KNOWLEDGE_PLAN_2026-10-24.md`,
"Do that"): "Rank the next knowledge from the priority order's next items; the unanchored constants the
production run reads, in impact order; the Capabilities uses waiting on truth; the open owed
knowledge. Give each its cost estimate ... Keep knowledge one step ahead of builds, and report a
lagging measure of builds drawn before their knowledge."

Nothing is typed here. Each source is read from the file that already holds it:

  priority  -- `docs/direction/priority_order.yaml`, steps 2 onward, in step order. An atom HAS its
               knowledge when a published page names it: a `knowledge_wholesale.json` topic's
               `atoms`, or its id anywhere in a `knowledge_topics.json` page record. Only the atoms
               with none become rows; that is "one step ahead of builds" made checkable.
  owed      -- `docs/design/the_map/note_rulings.yaml` `owed` (a domain with notes and no page, not
               yet written), and `docs/direction/director_asks.yaml` rows not shipped whose ask names
               a knowledge page.
  constants -- `docs/design/world_constant_anchor_register.txt`, grouped by module, ordered by the
               19 Oct production-run screen's gross-revenue move per module
               (`docs/design/world_constant_impact_ranking.md`, the settlement-loop table). A module
               the screen did not move ranks after every measured one, as `unmeasured` -- not zero.
  waiting   -- `site/data/capabilities_door.json` use cases that wait, split into the truths each
               waits on, ordered by how many uses one truth unblocks.
  re-check  -- pages `tools.generate_knowledge_review` grades due or never checked: the freshness
               sweep, priced like any other knowledge session.

THE COST of each row is one landed knowledge session, priced by `tools.work_cost_estimate`'s fit of
what landed knowledge-page sessions cost (its `knowledge_page` class, low-median-high). One session
per row is this module's choice, and the plan says so on its face: a page has taken one landed
session in the record, but a module of 40 constants is a page-sized research pass only if its
constants share a source, which nobody has measured. The constant rows therefore carry their count,
so a reader can see which are likely to take more.

THE LAGGING MEASURE: of the world and supplier build commits on origin/main in the window whose
message names a priority-order atom, how many name one that has no page today. Every build on such
an atom was drawn before its knowledge, so the count is exact for those atoms; an atom that has a
page today may still have been built before it, so the figure is a LOWER BOUND, and says so.

    python3 -m tools.knowledge_plan            # the plan, as text
    python3 -m tools.knowledge_plan --json     # the plan, as data
    python3 -m tools.knowledge_plan --token-saving   # steer item 6, measured before it is built

Reporting only: it decides nothing and exits 0 whatever it finds. Priority stays the director's.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

import yaml

from tools import work_cost_estimate as wce

ROOT = Path(__file__).resolve().parent.parent
PRIORITY = "docs/direction/priority_order.yaml"
ASKS = "docs/direction/director_asks.yaml"
RULINGS = "docs/design/the_map/note_rulings.yaml"
REGISTER = "docs/design/world_constant_anchor_register.txt"
RANKING = "docs/design/world_constant_impact_ranking.md"
CAPABILITIES = "site/data/capabilities_door.json"
WHOLESALE = "site/data/knowledge_wholesale.json"
TOPICS = "site/data/knowledge_topics.json"
CLASS = "knowledge_page"

_SCREEN_ROW = re.compile(r"^\| `((?:sim|simulation)/[\w/]+\.py)` \| (\d+) \| ([\d.]+)% \|", re.M)
_SCREEN_HEAD = "## The production-run screen, settlement loop"
_PAGE_ASK = re.compile(r"knowledge page", re.I)


def _read(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def _cost(fit: dict | None) -> dict:
    est = wce.estimate(CLASS, fit, sessions=1)
    if "refused" in est:
        return est
    return {k: round(est[k], 2) for k in ("points", "low", "high")}


def atoms_with_a_page(root: Path = ROOT) -> set[str]:
    named = set()
    for t in json.loads(_read(root, WHOLESALE)).get("topics", []):
        if isinstance(t.get("atoms"), list):
            named.update(t["atoms"])
    topics = _read(root, TOPICS)
    return named | {a for a in _priority_atoms_ids(root) if a in topics}


def _priority_atoms(root: Path = ROOT) -> list[tuple[int, str, str]]:
    steps = yaml.safe_load(_read(root, PRIORITY))["steps"]
    out = []
    for n in sorted(steps):
        if n < 2:
            continue
        for a in steps[n].get("atoms") or []:
            out.append((n, steps[n]["name"], a))
    return out


def _priority_atoms_ids(root: Path) -> list[str]:
    return [a for _, _, a in _priority_atoms(root)]


def priority_rows(root: Path, has_page: set[str]) -> list[dict]:
    return [{"source": "priority", "subject": a, "why": f"step {n}, {name}: no published page names it"}
            for n, name, a in _priority_atoms(root) if a not in has_page]


def owed_rows(root: Path) -> list[dict]:
    rows = []
    pages = json.loads(_read(root, TOPICS))["pages"]
    for page, notes in (yaml.safe_load(_read(root, RULINGS)).get("owed") or {}).items():
        if page in pages or (root / "site" / "knowledge" / page).is_dir():
            continue
        rows.append({"source": "owed", "subject": page,
                     "why": f"{len(notes)} research note(s) ruled owed this page"})
    for ask in yaml.safe_load(_read(root, ASKS)).get("asks") or []:
        if ask.get("status") in ("partly", "not_started", "open") and _PAGE_ASK.search(ask.get("ask", "")):
            rows.append({"source": "owed", "subject": ask["id"],
                         "why": ask.get("next_step") or ask.get("missing") or ask["ask"]})
    return rows


def screen_impact(root: Path) -> dict[str, float]:
    text = _read(root, RANKING)
    start = text.find(_SCREEN_HEAD)
    if start < 0:
        return {}
    section = text[start:text.find("\n## ", start + 1)]
    return {m.group(1): float(m.group(3)) for m in _SCREEN_ROW.finditer(section)}


def constant_rows(root: Path) -> list[dict]:
    by_module = Counter(ln.split("::")[0] for ln in _read(root, REGISTER).splitlines()
                        if ln.strip() and not ln.startswith("#"))
    impact = screen_impact(root)
    order = sorted(by_module, key=lambda m: (m not in impact, -impact.get(m, 0.0), -by_module[m], m))
    return [{"source": "constants", "subject": m, "count": by_module[m],
             "why": (f"{by_module[m]} bare constant(s); the screen moved gross {impact[m]}% at x1.1"
                     if m in impact else f"{by_module[m]} bare constant(s); unmeasured by the screen")}
            for m in order]


def waiting_rows(root: Path) -> list[dict]:
    uses = json.loads(_read(root, CAPABILITIES)).get("use_cases") or {}
    unblocks: dict[str, list[str]] = defaultdict(list)
    for g in uses.get("gates") or []:
        for u in g.get("items") or []:
            if u.get("testable_now"):
                continue
            for truth in u.get("waits_on") or []:
                unblocks[truth].append(u["name"])
    order = sorted(unblocks, key=lambda t: (-len(unblocks[t]), t))
    return [{"source": "waiting", "subject": t, "count": len(unblocks[t]),
             "why": "unblocks " + "; ".join(unblocks[t])} for t in order]


def recheck_rows(root: Path) -> list[dict]:
    from tools import generate_knowledge_review as gkr
    report = gkr.build(root / WHOLESALE)
    return [{"source": "re-check", "subject": r["id"], "why": f"{r['state']}: {r.get('detail', '')}"}
            for r in report["topics"] if r["state"] in ("due", "unchecked")]


def builds_before_knowledge(root: Path, has_page: set[str], days: int = 30) -> dict:
    atoms = {a: wce._atom_pattern(a) for a in _priority_atoms_ids(root)}
    log = subprocess.run(
        ["git", "log", "origin/main", f"--since={days}.days", "--no-merges", "--name-only",
         "--format=\x1e%H\x1f%s%n%b\x1f"], cwd=root, capture_output=True, text=True).stdout
    builds = before = 0
    unled: Counter = Counter()
    for rec in log.split("\x1e")[1:]:
        _, msg, paths = (rec.split("\x1f") + ["", ""])[:3]
        if wce.classify(paths.split()) not in ("world_build", "supplier_build"):
            continue
        named = [a for a, pat in atoms.items() if pat.search(msg)]
        if not named:
            continue
        builds += 1
        if any(a not in has_page for a in named):
            before += 1
            unled.update(a for a in named if a not in has_page)
    return {"days": days, "builds_naming_a_priority_atom": builds, "drawn_before_knowledge": before,
            "bound": "lower", "atoms": dict(unled.most_common())}


def build(root: Path = ROOT, fit: dict | None = None) -> dict:
    fit = wce.load_fit() if fit is None else fit
    has_page = atoms_with_a_page(root)
    rows = (priority_rows(root, has_page) + owed_rows(root) + constant_rows(root)
            + waiting_rows(root) + recheck_rows(root))
    cost = _cost(fit)
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    totals = {}
    if "refused" not in cost:
        totals = {k: round(cost[k] * len(rows), 1) for k in ("points", "low", "high")}
    by_source = Counter(r["source"] for r in rows)
    return {"cost_per_row": cost, "cost_basis": f"one landed {CLASS} session per row",
            "rows": rows, "by_source": dict(by_source), "total_points": totals,
            "lagging": builds_before_knowledge(root, has_page)}


def report(plan: dict, limit: int = 12) -> str:
    c = plan["cost_per_row"]
    head = [f"Forward knowledge plan: {len(plan['rows'])} rows {plan['by_source']}",
            (f"cost per row {c['points']} points ({c['low']}-{c['high']}), {plan['cost_basis']}; "
             f"all rows {plan['total_points']['points']} ({plan['total_points']['low']}-"
             f"{plan['total_points']['high']})") if "refused" not in c else f"cost: {c['refused']}"]
    lag = plan["lagging"]
    head.append(f"builds drawn before their knowledge, last {lag['days']} days: "
                f"{lag['drawn_before_knowledge']} of {lag['builds_naming_a_priority_atom']} "
                f"(a lower bound) {lag['atoms']}")
    out = head
    for src in ("priority", "owed", "constants", "waiting", "re-check"):
        sel = [r for r in plan["rows"] if r["source"] == src]
        out.append(f"\n{src} ({len(sel)})")
        out += [f"  {r['rank']:>3}. {r['subject']} -- {r['why']}" for r in sel[:limit]]
        if len(sel) > limit:
            out.append(f"       ... {len(sel) - limit} more")
    return "\n".join(out)


_SEARCH_CMD = re.compile(r"(^|[\s|;&(])(grep|rg|find|ls|git grep|git ls-files)\b")
TRANSCRIPTS = Path.home() / ".claude" / "projects" / "-home-rich-synthetic-enterprise"


def token_saving(days: float = 7.0, transcripts: Path = TRANSCRIPTS, root: Path = ROOT,
                 file_chars: int | None = None) -> dict:
    """Steer item 6 (it lives here, beside item 5, so `tools/the_map.py` stays the register's reader), "give each turn the register and its links as one cheap file ... measure the
    token saving per turn", measured before it is built.

    What a turn spends: in each session that went on to edit, the characters of every search result
    (Grep, Glob, or a Bash grep/find/ls) it read BEFORE its first Edit or Write. What the map could
    replace: the part of that whose search named one of the register's terms -- a search for
    anything else the map cannot answer. What the file costs: the characters of `report()`. Both are
    characters, not tokens, because the ratio is what decides and it needs no conversion; and both
    are re-read on every later call of the turn, so caching scales them alike.
    """
    import statistics
    import time

    from tools import the_map
    reg = the_map.load_register(root)
    pats = [the_map._term_pattern(t) for c in reg["concepts"] for t in the_map._terms(c)]
    cut = time.time() - days * 86400
    per_turn = []
    for path in transcripts.glob("*.jsonl"):
        if path.stat().st_mtime < cut:
            continue
        pending: dict[str, bool] = {}
        spent = answerable = 0
        edited = False
        for line in path.read_text(errors="replace").splitlines():
            try:
                content = (json.loads(line).get("message") or {}).get("content")
            except (ValueError, AttributeError):
                continue
            for b in content if isinstance(content, list) else []:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "tool_use" and not edited:
                    name, inp = b.get("name"), b.get("input") or {}
                    if name in ("Edit", "Write", "NotebookEdit"):
                        edited = True
                    elif name in ("Grep", "Glob") or (
                            name == "Bash" and _SEARCH_CMD.search(inp.get("command", ""))):
                        asked = json.dumps(inp).lower()
                        pending[b["id"]] = any(p.search(asked) for p in pats)
                elif b.get("type") == "tool_result" and b.get("tool_use_id") in pending:
                    body = b.get("content")
                    n = len(body if isinstance(body, str) else json.dumps(body))
                    spent += n
                    answerable += n if pending.pop(b["tool_use_id"]) else 0
        if edited:
            per_turn.append((spent, answerable))
    if not per_turn:
        return {"refused": f"no session in the last {days:g} days edited anything"}
    file_chars = len(the_map.report(the_map.build(root))) if file_chars is None else file_chars
    mean_answerable = statistics.mean(a for _, a in per_turn)
    return {"days": days, "turns": len(per_turn), "concepts": len(reg["concepts"]),
            "search_chars_median": statistics.median(s for s, _ in per_turn),
            "answerable_chars_median": statistics.median(a for _, a in per_turn),
            "answerable_chars_mean": round(mean_answerable),
            "map_file_chars": file_chars,
            "saving_chars_per_turn": round(mean_answerable - file_chars)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--token-saving", action="store_true", help="measure steer item 6")
    a = ap.parse_args(argv)
    if a.token_saving:
        print(json.dumps(token_saving(), indent=1))
        return 0
    plan = build()
    print(json.dumps(plan, indent=1) if a.json else report(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
