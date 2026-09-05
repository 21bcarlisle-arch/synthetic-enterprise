"""Which caller suite is each converged module's contract standing on?

THE QUESTION THIS EXISTS TO RANK, and it is not "is this module tested". `38871422b` measured one
converged mechanism (`background/register_low_water.py`, four callers) and found the shared module
inherits whichever caller suite happened to be strongest: one contract proved by NO suite, two by
one. `befe26b7e` found the harder sibling at `background/ops_repo.py` -- three callers, and the
shared function had never been executed by a test at all, because every caller's suite patched it
BY NAME in the caller's namespace. Both were invisible to a reader counting call sites, who sees
one helper and three callers and concludes one mechanism, well factored.

CONVERGENCE MOVES THE CODE AND DOES NOT MOVE THE EVIDENCE. This module is the standing LOOK for
that, and the two columns that carry the whole point are the last two:

  * `direct` -- suites that IMPORT the module. They can name its contracts.
  * `reaching` -- suites whose transitive import closure REACHES it. They execute its body as a
    side effect of testing something else, and they are what a converged module's contracts are
    usually standing on. A module with many `reaching` and zero `direct` reads as well-covered by
    every count this project keeps, and no test anywhere has ever asserted one of its contracts.

IT IS AN INSTRUMENT AND NOT A GATE, deliberately. It has no pass/fail, no register, no residue,
and nothing calls it on a diff -- the seat runs it to decide which subject to spend a mutation
battery on next, and the battery is what actually grades a contract. A screen cannot: "has a
dedicated suite" does not mean each contract is proved (the low-water case had four caller suites
and still a contract proved by nothing), and "no dedicated suite" does not mean unproved. RANKING
IS THE JOB. Any exit code here would be a control keyed to today's answer.

WHAT IT IS BLIND TO, and both blindnesses are one-directional. It reads static imports, so a
caller reached by subprocess or by dynamic dispatch is not counted -- the caller count is a LOWER
bound. And a name that appears in a test only as a STRING (a parameterised table of
`("background.direction", "read_decisions")` pairs) is not an importer, though `grep -rl` says it
is -- so a grep-built importer list is an UPPER bound and the two must not be mixed.

CLI:
    python3 -m tools.converged_contract_screen              # ranked: no dedicated suite first
    python3 -m tools.converged_contract_screen --all        # every converged module
    python3 -m tools.converged_contract_screen --module background.direction
    python3 -m tools.converged_contract_screen --json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools.select_impacted_tests import ROOT, TEST_ROOT, build_graph

#: A module is CONVERGED at three first-party callers. Not a tuned number and nothing optimises
#: it: two callers is a pair, and the failure this screens for -- a shared contract standing on
#: whichever caller suite happened to be strongest -- needs a set to choose the strongest FROM.
#: Both measured instances (`register_low_water` at four, `ops_repo` at three) sit at or above it.
CONVERGED_AT = 3


def _is_test(rel: str) -> bool:
    return rel.split("/", 1)[0] == TEST_ROOT


def _reverse(forward: dict[str, set[str]]) -> dict[str, set[str]]:
    back: dict[str, set[str]] = {rel: set() for rel in forward}
    for src, deps in forward.items():
        for dep in deps:
            back.setdefault(dep, set()).add(src)
    return back


def _reaches(forward: dict[str, set[str]], start: str) -> set[str]:
    """Every file whose transitive import closure reaches `start`.

    Walks the REVERSED graph from the target rather than the forward closure of every test, which
    is the same answer for one subject and does not build 26k closures to get it.
    """
    back = _reverse(forward)
    seen: set[str] = set()
    stack = [start]
    while stack:
        cur = stack.pop()
        for importer in back.get(cur, ()):
            if importer not in seen:
                seen.add(importer)
                stack.append(importer)
    return seen


def screen(root: Path = ROOT, converged_at: int = CONVERGED_AT) -> list[dict]:
    """One row per converged module. Sorted: no dedicated suite first, then by caller count."""
    module_to_file, forward = build_graph(root)
    file_to_module = {v: k for k, v in module_to_file.items()}
    back = _reverse(forward)

    rows = []
    for module, rel in sorted(module_to_file.items()):
        if _is_test(rel):
            continue
        importers = back.get(rel, set())
        callers = sorted(i for i in importers if not _is_test(i))
        if len(callers) < converged_at:
            continue
        direct = sorted(i for i in importers if _is_test(i))
        reaching = sorted(i for i in _reaches(forward, rel) if _is_test(i))
        stem = module.rsplit(".", 1)[-1]
        dedicated = sorted(
            t for t in direct
            if stem in Path(t).stem
            or {d for d in forward[t] if not _is_test(d)} <= {rel}
        )
        rows.append({
            "module": module,
            "n_callers": len(callers),
            "callers": [file_to_module.get(c, c) for c in callers],
            "n_direct": len(direct),
            "direct": direct,
            "n_reaching": len(reaching),
            "reaching": reaching,
            "dedicated": dedicated,
        })
    rows.sort(key=lambda r: (bool(r["dedicated"]), -r["n_callers"], r["module"]))
    return rows


def _print(rows: list[dict], show_all: bool) -> None:
    no_ded = [r for r in rows if not r["dedicated"]]
    no_direct = [r for r in no_ded if not r["direct"]]
    print(f"converged modules (>={CONVERGED_AT} first-party callers)   {len(rows)}")
    print(f"of those, with NO dedicated suite                {len(no_ded)}")
    print(f"of those, with no test importer at all           {len(no_direct)}")
    print()
    print(f"{'callers':>7} {'direct':>7} {'reaching':>9}  module")
    for r in (rows if show_all else no_ded):
        flag = "  <-- NO TEST IMPORTER" if not r["direct"] else ""
        print(f"{r['n_callers']:>7} {r['n_direct']:>7} {r['n_reaching']:>9}  "
              f"{r['module']}{flag}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--all", action="store_true",
                    help="every converged module, not only those with no dedicated suite")
    ap.add_argument("--module", help="one module, with its caller and suite lists in full")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    rows = screen()
    if args.module:
        rows = [r for r in rows if r["module"] == args.module]
        if not rows:
            print(f"{args.module!r} is not a converged module "
                  f"(<{CONVERGED_AT} first-party callers, or not a repo module)")
            return 0
        if not args.json:
            for r in rows:
                print(f"{r['module']}  --  {r['n_callers']} callers, "
                      f"{r['n_direct']} direct importer(s), {r['n_reaching']} reaching suite(s)")
                for key in ("callers", "direct", "reaching", "dedicated"):
                    print(f"  {key}:")
                    for v in r[key] or ["(none)"]:
                        print(f"    {v}")
            return 0
    if args.json:
        print(json.dumps(rows, indent=2))
        return 0
    _print(rows, args.all)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
