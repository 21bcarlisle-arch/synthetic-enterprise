#!/usr/bin/env python3
"""The module-graph census: every non-test module, every internal import, every boundary crossing.

One definition serving two readers -- the site's module-graph door (director instruction,
`DIRECTOR_INSTRUCTION_MODULE_GRAPH_DOOR_WEEKLY_2026-10-09.md`) and any advisor census of the
import graph (`ADVISOR_FINDINGS_IMPORT_GRAPH_CENSUS_2026-10-09.md`) -- so the two never disagree
by construction.

WHAT IT STANDS ON, AND WHAT IT ADDS. Nothing here parses an import or decides what a crossing is:

  * the edges are `tools/select_impacted_tests.build_graph`'s -- this repo's one static import
    graph, file -> repo files it imports, with its longest-prefix resolution;
  * the boundary is `tools/epistemic_wall`'s -- `is_company_module`, `is_sim_module`,
    `under_seam` -- the same predicates the wall ratchet and the verifier ask, so a bypass on this
    page is a bypass to the ratchet. A private copy of that question is the drift
    `epistemic_wall` was extracted to end;
  * the committed tree is `epistemic_wall.head_export`'s, so the figures are HEAD's and an
    uncommitted edit in the shared tree never reaches the page.

What this adds is only what neither has an opinion about: which LAYER a module is in, its SIZE
in lines, and the KIND of each edge.

THE DEFINITION THE ADVISOR'S FIRST READING YIELDS TO (2026-10-09). The advisor counted 49
"world -> company imports bypassing any interface". Resolved against the wall's own seam, 45 of
those import `company.interfaces` -- the seam itself -- and 4 go round it; the 4 are exactly the
ratchet's dated legacy allowlist. So "bypass" here means what the wall means: a crossing whose
company-side endpoint is NOT under the seam. Direction is kept, because the two directions are
not equally serious: the company reading the world's internals is the forbidden one.

A DIAGNOSTIC (R12). No gate, reward or draw reads this. `test_module_graph_census.py` holds that
the only production importer is the weekly publish step.

LIMITS, carried into the payload so the page states them: static imports only; a dynamic import,
a subprocess call or a shared data file couples two modules invisibly here; a module with no
import edges is not thereby dead.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import epistemic_wall as wall  # noqa: E402
from tools import select_impacted_tests as graph  # noqa: E402

OUTPUT = ROOT / "site" / "data" / "module_graph.json"

# The layers are the import graph's own roots less its test root: one list, so a root added
# there is a layer here without an edit.
LAYERS = tuple(r for r in graph.ANALYSED_ROOTS if r != graph.TEST_ROOT)

LIMITS = (
    "Static imports only: an import statement the parser can read.",
    "Dynamic imports, subprocess calls and shared data files couple modules invisibly here.",
    "A module with no import edges is not thereby dead: it may be run as a script, "
    "loaded by name, or started by a timer.",
    "Test modules are excluded; the site's own scripts are outside the layers counted.",
)

EDGE_KINDS = ("internal", "seam", "bypass")


def _is_test(rel: str) -> bool:
    name = rel.rsplit("/", 1)[-1]
    return (rel.startswith(graph.TEST_ROOT + "/") or "/tests/" in rel
            or name.startswith("test_") or name.endswith("_test.py") or name == "conftest.py")


def edge_kind(src: str, dst: str) -> tuple[str, str | None]:
    """(kind, direction) of one import edge between two dotted modules.

    `direction` is "company_reads_world" or "world_reads_company" for a crossing, else None.
    A crossing is `seam` when its company-side endpoint is under the seam package, `bypass`
    otherwise -- the wall's own reading, asked through the wall's own predicates.
    """
    if wall.is_company_module(src) and wall.is_sim_module(dst):
        return ("seam" if wall.under_seam(src) else "bypass"), "company_reads_world"
    if wall.is_sim_module(src) and wall.is_company_module(dst):
        return ("seam" if wall.under_seam(dst) else "bypass"), "world_reads_company"
    return "internal", None


def census(root: Path) -> dict:
    """The census of the tree at `root`. Parameterised by root so a fixture tree can drive it."""
    root = Path(root)
    module_to_file, forward = graph.build_graph(root)
    file_to_module = {f: m for m, f in module_to_file.items()}
    files = sorted(f for f in forward
                   if f.split("/", 1)[0] in LAYERS and not _is_test(f))
    if not files:
        # An empty tree confirms every claim -- zero bypasses included.
        raise RuntimeError(f"no non-test modules under {list(LAYERS)} at {root}")
    index = {f: i for i, f in enumerate(files)}

    nodes = []
    for f in files:
        try:
            loc = len((root / f).read_text(encoding="utf-8").splitlines())
        except (OSError, UnicodeDecodeError):
            loc = None
        nodes.append({"module": file_to_module[f], "layer": f.split("/", 1)[0], "loc": loc})

    edges = []
    kinds: Counter = Counter()
    bypass_list = []
    for f in files:
        targets = {g for g in forward[f] if g in index}
        for g in sorted(targets):
            # `from pkg import mod` reaches pkg/__init__.py AND pkg/mod.py in `build_graph`, so one
            # statement is two edges and one crossing is counted twice. The package edge is kept
            # only when nothing inside the package was imported -- an edge is "A imports B".
            if g.endswith("/__init__.py"):
                pkg = g[: -len("__init__.py")]
                if any(t != g and t.startswith(pkg) for t in targets):
                    continue
            src, dst = file_to_module[f], file_to_module[g]
            kind, direction = edge_kind(src, dst)
            kinds[kind] += 1
            if direction:
                kinds[f"{kind}:{direction}"] += 1
            if kind == "bypass":
                bypass_list.append({"from": src, "to": dst, "direction": direction})
            edges.append([index[f], index[g], EDGE_KINDS.index(kind)])

    degree: Counter = Counter()
    for s, d, _k in edges:
        degree[s] += 1
        degree[d] += 1
    for i, n in enumerate(nodes):
        n["edges"] = degree[i]

    layers = {}
    for layer in LAYERS:
        members = [n for n in nodes if n["layer"] == layer]
        if members:
            layers[layer] = {"modules": len(members),
                             "loc": sum(n["loc"] or 0 for n in members)}

    return {
        "modules": len(nodes),
        "edges": len(edges),
        "loc": sum(n["loc"] or 0 for n in nodes),
        "crossings": {
            "seam": kinds["seam"],
            "bypass": kinds["bypass"],
            "seam_company_reads_world": kinds["seam:company_reads_world"],
            "seam_world_reads_company": kinds["seam:world_reads_company"],
            "bypass_company_reads_world": kinds["bypass:company_reads_world"],
            "bypass_world_reads_company": kinds["bypass:world_reads_company"],
        },
        "bypass_edges": bypass_list,
        "unwired_modules": sum(1 for n in nodes if n["edges"] == 0),
        "layers": layers,
        "edge_kinds": list(EDGE_KINDS),
        "nodes": nodes,
        "edge_list": edges,
        "limits": list(LIMITS),
        "definition": {
            "layers": list(LAYERS),
            "company_side": sorted(wall.COMPANY_PACKAGES),
            "world_side": sorted(wall.SIM_PACKAGES),
            "seam": wall.SEAM_PACKAGE,
            "bypass": "a crossing whose company-side endpoint is not under the seam",
            "edge": "module A imports module B; an import of a package's module does not also "
                    "count an edge to the package itself",
        },
    }


def census_at_head(repo: Path = ROOT, rev: str = "HEAD") -> dict:
    """The census of the COMMITTED tree at `rev` -- what a fresh clone would show."""
    sha = subprocess.run(["git", "-C", str(repo), "rev-parse", rev], capture_output=True,
                         text=True, check=True).stdout.strip()
    with wall.head_export(str(repo), dirs=LAYERS, rev=rev) as tree:
        out = census(Path(tree))
    out["commit"] = sha
    return out


def _delta(new: dict, old: dict | None) -> dict | None:
    if not old or old.get("commit") == new.get("commit"):
        return (old or {}).get("week_on_week")
    keys = ("modules", "edges", "loc")
    d = {k: new[k] - old.get(k, 0) for k in keys}
    d["bypass"] = new["crossings"]["bypass"] - (old.get("crossings") or {}).get("bypass", 0)
    d["since_commit"] = old.get("commit")
    d["since"] = old.get("generated_at")
    return d


def write(path: Path = OUTPUT, repo: Path = ROOT) -> dict:
    """Regenerate the door's feed from HEAD, carrying a week-on-week delta from the last one."""
    try:
        previous = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        previous = None
    out = census_at_head(repo)
    out["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out["week_on_week"] = _delta(out, previous)
    path.write_text(json.dumps(out, separators=(",", ":")) + "\n", encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--write", action="store_true", help=f"regenerate {OUTPUT.relative_to(ROOT)}")
    args = ap.parse_args(argv)
    out = write() if args.write else census_at_head()
    c = out["crossings"]
    print(f"{out['modules']} modules, {out['edges']} edges, {out['loc']} lines at "
          f"{out['commit'][:9]}; crossings: {c['seam']} through the seam, {c['bypass']} bypassing "
          f"({c['bypass_company_reads_world']} company->world, "
          f"{c['bypass_world_reads_company']} world->company)")
    for b in out["bypass_edges"]:
        print(f"  bypass {b['direction']}: {b['from']} -> {b['to']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
