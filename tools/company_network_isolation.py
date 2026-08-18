#!/usr/bin/env python3
"""The company layer has no route to a real endpoint — enforced, not requested.

DIRECTOR RULING, 2026-08-18:

    "the supplier doesn't seek approval — it's refused by construction. If company-side
     code has to ask, someone eventually says yes, and the breach arrives as a reasonable
     decision. It should have no route to a real endpoint at all."

WHY THIS IS A DIFFERENT AXIS FROM THE WALL NEXT DOOR, and why the existing control could
not have caught it. `tools/epistemic_wall.py` asks *may these two modules talk to each
other* — company to sim, sim to company — and exempts the sanctioned seam,
`company.interfaces`. That question has nothing to say about the real world. The breach
this module was written for lives AT the seam, on an edge the wall correctly permits:

    company/interfaces/sim_interface.py::_load_price_records
        records = get_cached_prices(...)          # sim.cache_store
        if records is None:
            records = get_system_prices_range(...)  # sim.system_prices_history -> Elexon

`get_system_prices_range` is a live HTTP client (a module-level `requests.Session()`
against data.elexon.co.uk), and `get_cached_prices` returns None on a partial cache
expressly "so the caller falls back to the live API". So the supplier reaches the real
world **on a cache miss**. Nobody approves it. Delete one cache file and company-side code
is talking to Elexon — which is worse than the failure the ruling guards against, because
there is no moment at which anyone could have said no.

CAPABILITY, NOT HOSTS — and this is the part that survives go-live. An allowlist names
hosts, so it must be RELAXED at go-live, exactly when it matters most. This names a
CAPABILITY: company-side code may not open a socket, ever. At go-live nothing here
changes — the company still never opens a socket; what changes is what sits behind the
seam. A rule that has to be loosened at the worst moment is not a rule.

TRANSITIVE, BECAUSE THE REAL BREACH IS. `company/` contains zero direct networking
imports and always has. The route runs company -> sim module -> `requests`. A control that
only looked for `import requests` under `company/` would have been green on the day it
shipped, over a live route, which is the vacuous-control shape this project keeps finding
in its own instruments.

THE REPAIR IS NAMED, AND IT IS NOT "ADD AN EXCEPTION": the seam asks for prices; the SIM
decides whether that means cache, fetch, or refuse. Company-side code stops carrying a
fallback it should never have owned. Until that lands this control is RED, deliberately --
a green control here would prove nothing, since the property it asserts is currently false.
"""
from __future__ import annotations

import argparse
import ast
import os
import sys
from collections import deque
from pathlib import Path

REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.epistemic_wall import (  # noqa: E402
    COMPANY_PACKAGES, WALL_DIRS, build_edges, top_package,
)

#: Modules that ARE the network. Anything importing one of these can open a socket, and
#: anything importing THAT can too, and so on. `subprocess` is deliberately included: a
#: `curl` shelled out of company code is the same capability wearing a different hat, and
#: leaving it out would make the control easy to walk around without noticing.
HTTP_MODULES = frozenset({
    "requests", "urllib", "urllib3", "http", "httplib2", "httpx", "aiohttp",
    "socket", "ssl", "ftplib", "telnetlib", "smtplib", "websockets",
})

#: `subprocess` is a route to ANY capability, including the network -- but only when it is
#: actually pointed at one. Counting every `subprocess` import as a network route would fail
#: `saas.reporting.annual_report`, which shells `git`, and a control that cries wolf is one
#: people learn to route around. Counting none of them would have missed
#: `company.compliance.internal_audit`, which shells `curl` at a URL held in a module
#: constant -- a real route out, found only because subprocess was considered at all.
#: So: a shell counts iff the module also names a network binary.
NETWORK_BINARIES = ("curl", "wget", "nc", "ncat", "ssh", "scp", "rsync", "telnet")
SHELL_MODULES = frozenset({"subprocess", "os"})

#: Scanned for the capability graph. Wider than the wall's own dirs, because the route out
#: of the company can run through any package it can import.
SCAN_DIRS = tuple(sorted(set(WALL_DIRS) | {"tools", "background"}))


#: THE FOUR ROUTES THAT EXIST TODAY, frozen so the tree is not held hostage to them while
#: the seam repair is designed -- and shrink-only, so they cannot become permanent. A NEW
#: route fails immediately; a frozen entry that is no longer a route ALSO fails, because a
#: baseline that keeps discharged entries stops being countable. Same shape as the site
#: register's orphan debt and the orphan ratchet itself: freeze the standing set, fail the
#: growth. Every entry names the route, so removing one is a checkable claim.
KNOWN_ROUTES: dict[str, str] = {
    "company.compliance.internal_audit":
        "shells curl at OLLAMA_URL, a module constant -- nothing stops it pointing outward",
    "company.interfaces.sim_interface":
        "the price fallback: cache miss -> sim.system_prices_history (Elexon) and "
        "sim.gas_prices_history (wget, FRED)",
    "company.interfaces.recorded_sim_interface":
        "inherits the seam's route by importing it",
    "company.portal.app":
        "inherits the seam's route by importing it",
}


class IsolationUnavailable(RuntimeError):
    """The check could not be performed. NOT a pass."""


def _module_of(root: str, path: str) -> str:
    rel = os.path.relpath(path, root)
    parts = rel[:-3].split(os.sep)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def network_capable_directly(root: str = REPO_ROOT,
                             dirs: tuple[str, ...] = SCAN_DIRS) -> dict[str, str]:
    """Modules that reach the network themselves, mapped to HOW."""
    found: dict[str, str] = {}
    for d in dirs:
        base = os.path.join(root, d)
        if not os.path.isdir(base):
            continue
        for dirpath, _dirnames, filenames in os.walk(base):
            if "__pycache__" in dirpath:
                continue
            for fn in filenames:
                if not fn.endswith(".py"):
                    continue
                path = os.path.join(dirpath, fn)
                try:
                    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
                except (OSError, SyntaxError):
                    continue
                src = Path(path).read_text(encoding="utf-8")
                imported: set[str] = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported.update(a.name.split(".")[0] for a in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                        imported.add(node.module.split(".")[0])
                if imported & HTTP_MODULES:
                    found[_module_of(root, path)] = "http client"
                elif imported & SHELL_MODULES:
                    named = [b for b in NETWORK_BINARIES
                             if f'"{b}"' in src or f"'{b}'" in src]
                    if named:
                        found[_module_of(root, path)] = f"shells {'/'.join(named)}"
    if not found:
        raise IsolationUnavailable(
            "no module in the repository imports the network -- the scan found nothing, "
            "which means it is looking in the wrong place, not that the repo is offline"
        )
    return found


def capability_graph(root: str = REPO_ROOT, dirs: tuple[str, ...] = SCAN_DIRS) -> dict[str, set[str]]:
    """module -> the in-repo modules it imports. Reuses the wall's own edge builder so
    there is one import-graph implementation in this repository, not two."""
    present = tuple(d for d in dirs if os.path.isdir(os.path.join(root, d)))
    graph: dict[str, set[str]] = {}
    # `submodule_targets=True` matters here: `from sim import system_prices_history`
    # imports a MODULE, and recording only the `sim` package would lose the hop that
    # carries the capability -- which is the hop this control exists to find.
    for edge in build_edges(root, present, submodule_targets=True):
        graph.setdefault(edge.src, set()).add(edge.dst)
    if not graph:
        raise IsolationUnavailable("the import graph is empty -- the scan found no edges")
    return graph


def network_reachable(root: str = REPO_ROOT, dirs: tuple[str, ...] = SCAN_DIRS) -> dict[str, list[str]]:
    """Every module that can reach the network, mapped to the shortest path proving it.

    Breadth-first from the directly-capable set, backwards along imports.
    """
    direct = network_capable_directly(root, dirs)
    graph = capability_graph(root, dirs)
    importers: dict[str, set[str]] = {}
    for src, dsts in graph.items():
        for dst in dsts:
            importers.setdefault(dst, set()).add(src)

    paths: dict[str, list[str]] = {m: [m] for m in direct}
    queue = deque(sorted(direct))
    how = dict(direct)
    while queue:
        mod = queue.popleft()
        for importer in sorted(importers.get(mod, ())):
            if importer not in paths:
                paths[importer] = [importer] + paths[mod]
                how[importer] = how[mod]
                queue.append(importer)
    return {m: {"path": p, "how": how[m]} for m, p in paths.items()}


def violations(root: str = REPO_ROOT, dirs: tuple[str, ...] = SCAN_DIRS) -> list[dict]:
    """Company-side modules with any route to a real endpoint. Empty is the target state."""
    reachable = network_reachable(root, dirs)
    out = []
    for module, info in sorted(reachable.items()):
        if top_package(module) in COMPANY_PACKAGES:
            path = info["path"]
            out.append({
                "module": module,
                "path": path,
                "how": info["how"],
                "via": path[1] if len(path) > 1 else "(reaches the network itself)",
                "endpoint_module": path[-1],
                "hops": len(path) - 1,
            })
    return out


def gate_violations(root: str = REPO_ROOT, dirs: tuple[str, ...] = SCAN_DIRS) -> list[str]:
    """What a commit must fail on: a NEW route, or a frozen one that is no longer real."""
    found = {v["module"] for v in violations(root, dirs)}
    problems = []
    for module in sorted(found - set(KNOWN_ROUTES)):
        problems.append(
            f"NEW ROUTE OUT OF THE COMPANY: {module} can reach a real endpoint. The company "
            f"layer must have no route at all (director ruling, 2026-08-18). Ask the seam for "
            f"the data instead, and let the sim decide whether that means cache, fetch or refuse."
        )
    for module in sorted(set(KNOWN_ROUTES) - found):
        problems.append(
            f"STALE BASELINE: {module} is frozen as a known route but no longer has one. "
            f"Remove it from KNOWN_ROUTES -- a baseline that keeps discharged entries stops "
            f"being countable."
        )
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--gate", action="store_true",
                    help="commit gate: fail only on a NEW route or a stale baseline entry")
    args = ap.parse_args(argv)
    if args.gate:
        problems = gate_violations()
        if problems:
            print("company-network-isolation: COMMIT REFUSED.")
            for p_ in problems:
                print(f"  - {p_}")
            return 1
        print(f"company-network-isolation: no new route out of the company "
              f"({len(KNOWN_ROUTES)} known, frozen, shrink-only).")
        return 0
    found = violations()
    if args.json:
        import json
        print(json.dumps({"violations": found, "count": len(found)}, indent=2))
        return 1 if found else 0
    if not found:
        print("company-network-isolation: the company layer has no route to a real endpoint.")
        return 0
    print(f"company-network-isolation: {len(found)} company-side module(s) can reach a real endpoint.\n")
    for v in found:
        print(f"  {v['module']}  [{v['how']}]")
        if v["hops"]:
            print(f"      -> {' -> '.join(v['path'][1:])}")
    print("\nThe company layer must have NO route to a real endpoint (director ruling,")
    print("2026-08-18). Not an exception list -- the absence of a route. The repair is the")
    print("seam's job: company code asks for data, and the SIM decides whether that means")
    print("cache, fetch, or refuse.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
