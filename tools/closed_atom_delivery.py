""""Closed" tells a reader nothing about whether the code runs. This says which.

REUSE: tools/closed_atom_delivery.py
CLASS: CUSTOM
INDEX: searched "closed atom", "delivered", "prior art", "importer", "dead code", "reachability".
       `background/finding_classes` classes FINDINGS, not atoms. `tools/capability_index` answers
       "what capability exists" from the live map and never opens the closed half.
       `tests/architecture/test_a_cited_constant_has_a_caller.py` asks the reachability question of
       one constant, not of an atom's whole file_scope. Nothing existed that could answer "is the
       ground this closed atom names actually running", which is the question a session asks before
       building on it.

WHY THIS EXISTS
---------------
Director console, 2026-09-05:

    "31 of 227 closed atoms never built anything and nothing separates them from the 70 that did.
     'Closed' tells a reader nothing about whether code runs. Make that visible before stage 1
     builds on top of another one -- W2_12 nearly cost us exactly that."

`maturity_map_closed.yaml` admits an atom on `level_current >= level_target`, so it holds two
different things under one word. `W2_12_change_of_tenancy_debt_physics` sits there having framed
the change-of-tenancy physics and built no emitter: 1,537 lines across three modules with no
production caller, and a live run that emits no move event at all. Stage 1's people work covers the
same ground, and the only thing that stopped it being built twice was the director asking.

WHAT "REACHED" MEANS, AND THE TWO WRONG ANSWERS THAT PRECEDED IT
----------------------------------------------------------------
A module is REACHED if non-test code imports it, or an execution context invokes it. Both halves
are necessary and each was learned by getting it wrong:

  * IMPORTERS ONLY called 34 atoms dead. Most were tools the commit hook runs as scripts --
    `python3 tools/write_time_gate.py` has no importer anywhere and certainly runs.
  * ANY PATH-SHAPED STRING called none of them dead. A path in a docstring counts, and so does one
    in a registry list -- which is exactly how `change_of_tenancy_register` read as "2 production
    callers" when the real number is zero.

So an invocation counts only from somewhere that could execute it: a shell script, a systemd unit,
a git hook, or a line that also mentions `subprocess`/`sys.executable`/`python3`. `CALIBRATION`
pins three answers established by hand, and its test drives them -- a scan this easy to get wrong
in both directions must be measured against known truth, not trusted.

THE VERDICTS
------------
    DELIVERED  a build target (>=2), and something it names is imported or invoked
    UNREACHED  a build target, and NOTHING it names is reached -- the W2_12 shape
    FRAMED     target below 2: it reached DISCOVER and never claimed to build
    NO-CODE    names no python at all (a design or governance atom)

FRAMED IS NOT A CRITICISM. An atom whose target was 1 did what it was asked. The defect is that
the file says only "closed", so a reader cannot tell it from one that shipped.
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

CLOSED_MAP = PROJECT / "docs" / "design" / "maturity_map_closed.yaml"

#: A build target. Below this an atom reached DISCOVER and never claimed to build anything.
BUILD_TARGET = 2

#: Lines that could actually execute a path. A path seen anywhere else is a mention.
_EXEC_HINT = re.compile(r"subprocess|sys\.executable|python3?\s|check_call|check_output|Popen")
_PY_PATH = re.compile(r"([A-Za-z_][\w/]*\.py)\b")
_DASH_M = re.compile(r"-m[\s\"']+([A-Za-z_][\w.]*)")
_EXEC_SUFFIXES = (".sh", ".service", ".timer")

#: THREE ANSWERS ESTABLISHED BY HAND on 2026-09-05, one per failure mode this scan has. Its test
#: drives them: a reachability scan that is easy to get wrong in both directions must be measured
#: against known truth rather than believed.
CALIBRATION = {
    # verified by reading all three call sites: a path in a registry list, a docstring, a dict key
    "company/crm/change_of_tenancy_register.py": None,
    # imported by simulation/run_phase2b.py, the live run loop
    "simulation/demand_model.py": "imported",
    # no importer anywhere; run as a script by tools/git-hooks/commit-msg
    "tools/write_time_gate.py": "invoked",
}


def _scan(root: Path) -> tuple[dict, set]:
    """(module -> importers, {invoked paths}). One pass; the tree is large."""
    imports: dict[str, set[str]] = {}
    invoked: set[str] = set()
    for p in root.rglob("*"):
        rel = str(p.relative_to(root))
        if rel.startswith("tests/") or ".git/" in rel or "site-packages" in rel:
            continue
        if not p.is_file() or p.suffix not in (".py", "") + _EXEC_SUFFIXES:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        executable_file = p.suffix in _EXEC_SUFFIXES or "git-hooks" in rel
        for line in text.splitlines():
            if not (executable_file or _EXEC_HINT.search(line)):
                continue
            invoked.update(m.group(1) for m in _PY_PATH.finditer(line))
            invoked.update(m.group(1).replace(".", "/") + ".py" for m in _DASH_M.finditer(line))
        if p.suffix == ".py":
            try:
                tree = ast.parse(text)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                mods = []
                if isinstance(node, ast.Import):
                    mods = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    mods = [node.module]
                for m in mods:
                    imports.setdefault(m, set()).add(rel)
    return imports, invoked


def reached(rel: str, imports: dict, invoked: set) -> str | None:
    """"imported" / "invoked" / None. A module's own file never counts as its own reacher."""
    module = rel[:-3].replace("/", ".")
    for name, importers in imports.items():
        if (name == module or name.startswith(module + ".")) and (importers - {rel}):
            return "imported"
    return "invoked" if rel in invoked else None


def classify(root: Path | None = None) -> list[dict]:
    """One row per closed atom: id, verdict, and the modules it names."""
    import yaml
    root = root or PROJECT
    data = yaml.safe_load((root / "docs" / "design" / "maturity_map_closed.yaml")
                          .read_text(encoding="utf-8"))
    atoms = data if isinstance(data, list) else next(
        v for v in data.values() if isinstance(v, list))
    imports, invoked = _scan(root)

    rows = []
    for atom in atoms:
        target = atom.get("level_target") or 0
        mods = [f for f in (atom.get("file_scope") or [])
                if isinstance(f, str) and f.endswith(".py") and (root / f).exists()]
        if target < BUILD_TARGET:
            verdict = "FRAMED"
        elif not mods:
            verdict = "NO-CODE"
        elif any(reached(m, imports, invoked) for m in mods):
            verdict = "DELIVERED"
        else:
            verdict = "UNREACHED"
        rows.append({"id": atom.get("id"), "verdict": verdict, "modules": mods,
                     "level_target": target,
                     # PER-MODULE, because the atom-level verdict hides the difference that
                     # matters. W2_12 and W2_13 are both FRAMED; W2_13's two modules are imported
                     # by the live run loop and three of W2_12's five are reached by nothing. A
                     # reader deciding whether to build on either needs the second fact, and the
                     # verdict alone would send them the same answer for both.
                     "reach": {m: reached(m, imports, invoked) for m in mods}})
    return rows


def prior_art(needle: str, rows: list[dict] | None = None) -> list[dict]:
    """Closed atoms whose id or file_scope mentions `needle`, with what they actually delivered.

    THE QUESTION THAT WOULD HAVE SAVED W2_12: before minting on ground a closed atom names, ask
    what that atom delivered. Matching on the id as well as the paths is deliberate -- the housing
    and people atoms collided by NUMBER first, and the number is how a reader notices at all.
    """
    rows = rows if rows is not None else classify()
    n = needle.lower()
    return [r for r in rows
            if n in (r["id"] or "").lower() or any(n in m.lower() for m in r["modules"])]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--report", action="store_true", help="the census, by verdict")
    ap.add_argument("--prior-art", metavar="NEEDLE",
                    help="what closed atoms on this ground actually delivered")
    args = ap.parse_args(argv)

    rows = classify()
    if args.prior_art:
        hits = prior_art(args.prior_art, rows)
        if not hits:
            print(f"[closed-atoms] no closed atom names `{args.prior_art}` -- new ground.")
            return 0
        print(f"[closed-atoms] {len(hits)} closed atom(s) name `{args.prior_art}`:")
        for r in hits:
            print(f"  {r['verdict']:<10} {r['id']}")
            for m in r["modules"]:
                how = r["reach"].get(m)
                print(f"      {'reached: ' + how if how else 'NOT REACHED':<18} {m}")
        return 0

    import collections
    counts = collections.Counter(r["verdict"] for r in rows)
    print(f"[closed-atoms] {len(rows)} closed atoms:")
    for k in ("DELIVERED", "UNREACHED", "FRAMED", "NO-CODE"):
        print(f"  {k:<10} {counts[k]:>3}")
    print('\n"Closed" means level_current >= level_target, so it covers an atom that shipped and '
          'one that only ever framed.\nUNREACHED and FRAMED are the ones a reader must not take '
          'for delivered.')
    for r in rows:
        if r["verdict"] == "UNREACHED":
            print(f"\n  UNREACHED {r['id']}")
            for m in r["modules"]:
                print(f"      {m}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
