"""Judge the pre-commit gates from the BASE, not from the change: observe mode.

The hook runs each gate as `python3 -m tools.<gate>` from the committing tree's root, so a change
that weakens a gate (or a module it imports) is judged by its own weakened copy -- demonstrated in
docs/staging/records/SEAT_RECORD_A_GATE_IS_JUDGED_BY_ITS_OWN_EDITED_COPY_2026-11-20.md. Design and
GAPs: docs/market_research/gates_judged_from_the_base_2026-11-20.md.

What this does, per commit:
  1. read the base hook (HEAD:tools/git-hooks/pre-commit) and its gate lines;
  2. walk each gate's import closure FROM THE BASE blobs;
  3. rerun only the gates whose closure the change stages, or whose hook line the change altered;
  4. run each such gate twice in identical shadow trees -- one carrying the base's closure files,
     one the change's -- with every other path a symlink into the change's root (data from the
     change, code from the base);
  5. log both exit codes; a base refusal the change's copy passes is the case enforce will refuse.

OBSERVE MODE: always exits 0. The hook calls it as `git show HEAD:tools/base_judged_gates.py |
python3 -P -`, so the observer itself is never the change's copy. Stdlib only, for the same reason.
"""
from __future__ import annotations

import ast
import calendar
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HOOK_REL = "tools/git-hooks/pre-commit"
LOG_NAME = "base_judged_gates.jsonl"
#: Not a domain constant: bounds how long observe mode may extend a commit per gate side.
RERUN_TIMEOUT_SECONDS = 1200

_GATE_LINE = re.compile(
    r"^\s*python3\s+(?:-m\s+(?P<mod>[\w.]+)|(?P<script>[\w/]+\.py))(?P<args>[^|]*)\|\|\s*exit\s+1\s*$")
#: Gates that run pytest. Their import closures are ~440 files (the test gate reaches
#: simulation/run_phase2b.py through background/staging_rooms.py), and two extra runs of a ~15-minute
#: gate on every commit touching any of them is not an observe-mode cost. They are rerun only when the
#: change touches the gate's own file or a module it imports DIRECTLY; otherwise the record says
#: `deferred`, so observe mode still counts how often the deep closure is touched (GAP-6).
SLOW_GATES = frozenset({"tools/pre_commit_test_gate.py", "tools/site_lane_gate.py"})
_GATE_DATA = re.compile(r"(baseline|\.mode$|frozen)", re.I)


def _git(root: Path, *args: str, check: bool = True) -> str:
    r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError("git {} failed: {}".format(" ".join(args), r.stderr.strip()))
    return r.stdout


class Base:
    """The base tree's file list and blobs, read once through one `cat-file --batch` process."""

    def __init__(self, root: Path, rev: str = "HEAD") -> None:
        self.root, self.rev = root, rev
        self.files = set(_git(root, "ls-tree", "-r", "--name-only", rev).splitlines())
        self._cache: dict[str, bytes | None] = {}

    def read(self, rel: str) -> bytes | None:
        if rel not in self.files:
            return None
        if rel not in self._cache:
            self._cache.update(self._batch([rel]))
        return self._cache.get(rel)

    def _batch(self, rels: list[str]) -> dict[str, bytes | None]:
        """One `cat-file --batch` per call: a subprocess per blob cost 10 s on a 700-file walk."""
        spec = "".join("{}:{}\n".format(self.rev, r) for r in rels).encode()
        out = subprocess.run(["git", "cat-file", "--batch"], cwd=self.root, input=spec,
                             capture_output=True).stdout
        found, pos = {}, 0
        for rel in rels:
            nl = out.index(b"\n", pos)
            header = out[pos:nl].split()
            if len(header) < 3 or header[1] == b"missing":
                found[rel], pos = None, nl + 1
                continue
            size = int(header[2])
            found[rel], pos = out[nl + 1:nl + 1 + size], nl + 1 + size + 1
        return found

    def prefetch(self, rels: list[str]) -> None:
        want = [r for r in rels if r in self.files and r not in self._cache]
        if want:
            self._cache.update(self._batch(want))


def gate_lines(hook_text: str) -> dict[str, dict]:
    """Every `python3 -m X ... || exit 1` / `python3 path.py ... || exit 1` line, keyed by line."""
    out = {}
    for line in hook_text.splitlines():
        m = _GATE_LINE.match(line)
        if not m:
            continue
        if m.group("mod"):
            entry = m.group("mod").replace(".", "/") + ".py"
        else:
            entry = m.group("script")
        out[line.strip()] = {"entry": entry, "module": m.group("mod"),
                             "args": m.group("args").split()}
    return out


def _candidates(dotted: str) -> list[str]:
    parts = dotted.split(".")
    out = []
    for i in range(1, len(parts) + 1):
        stem = "/".join(parts[:i])
        out += [stem + ".py", stem + "/__init__.py"]
    return out


def _imports_of(rel: str, source: bytes) -> set[str]:
    """Dotted names a module reaches by import. NOT string literals: a first cut counted any string
    naming a tool as a shell-out, and the test gate's list of producers then pulled 467 files of
    company/ and sim/ into its closure. A gate that shells out to another tool is GAP-3."""
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
        return set()
    pkg = rel.rsplit("/", 1)[0].replace("/", ".") if "/" in rel else ""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                up = pkg.split(".")[: len(pkg.split(".")) - node.level + 1] if pkg else []
                base = ".".join(p for p in [*up, base] if p)
            names.add(base)
            names.update("{}.{}".format(base, a.name) for a in node.names if base)
    if pkg:  # script-form sibling imports: `import foo` from tools/x.py means tools/foo.py
        names.update("{}.{}".format(pkg, n) for n in list(names) if "." not in n)
    return names


def closure(base: Base, entry: str) -> set[str]:
    """Repo files the gate at `entry` is built from, read from the BASE."""
    seen: set[str] = set()
    todo = [entry]
    while todo:
        base.prefetch(todo)
        rel = todo.pop()
        if rel in seen or rel not in base.files:
            continue
        seen.add(rel)
        src = base.read(rel)
        if src is None:
            continue
        for name in _imports_of(rel, src):
            todo.extend(c for c in _candidates(name) if c in base.files and c not in seen)
    return seen


def staged_paths(root: Path) -> set[str]:
    return set(_git(root, "diff", "--cached", "--name-only", "--no-renames").splitlines())


def affected_gates(base: Base, root: Path, staged: set[str]) -> list[dict]:
    """The gates whose base-vs-change verdict could differ, each with the reason it was picked."""
    base_hook = (base.read(HOOK_REL) or b"").decode("utf-8", "replace")
    change_hook_path = root / HOOK_REL
    change_hook = change_hook_path.read_text(errors="replace") if change_hook_path.is_file() else ""
    base_gates, change_gates = gate_lines(base_hook), gate_lines(change_hook)
    picked = []
    for line, gate in base_gates.items():
        files = closure(base, gate["entry"])
        touched = sorted(files & staged)
        dropped = line not in change_gates
        if touched or dropped:
            direct = {gate["entry"]} | {c for n in _imports_of(gate["entry"],
                                                                base.read(gate["entry"]) or b"")
                                        for c in _candidates(n) if c in base.files}
            deferred = (gate["entry"] in SLOW_GATES and not dropped
                        and not set(touched) & direct)
            picked.append({**gate, "line": line, "closure": files, "touched": touched,
                           "dropped_from_change_hook": dropped, "deferred": deferred})
    return picked


def build_shadow(root: Path, dest: Path, files: dict[str, bytes | None]) -> None:
    """`dest` mirrors `root` by symlink, except `files`, written as real files (None = absent).

    Only the directories on the way to a closure file are real; everything else is ONE symlink, so
    the cost is proportional to the closure, not the tree."""
    real_dirs = {""}
    for rel in files:
        parts = rel.split("/")[:-1]
        real_dirs.update("/".join(parts[:i]) for i in range(1, len(parts) + 1))
    for d in sorted(real_dirs, key=len):
        (dest / d).mkdir(parents=True, exist_ok=True)
        src_dir = root / d
        if not src_dir.is_dir():
            continue
        for child in src_dir.iterdir():
            rel = "{}/{}".format(d, child.name) if d else child.name
            if rel in real_dirs or rel in files or child.name == "__pycache__":
                continue
            (dest / rel).symlink_to(child)
    for rel, data in files.items():
        if data is not None:
            (dest / rel).write_bytes(data)


def run_gate(gate: dict, shadow: Path, root: Path) -> dict:
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    env.update(PYTHONPATH=str(shadow), PYTHONDONTWRITEBYTECODE="1")
    if gate["module"]:
        argv = [sys.executable, "-P", "-m", gate["module"], *gate["args"]]
    else:
        argv = [sys.executable, str(shadow / gate["entry"]), *gate["args"]]
    t0 = time.monotonic()
    try:
        r = subprocess.run(argv, cwd=root, env=env, capture_output=True, text=True,
                           timeout=RERUN_TIMEOUT_SECONDS)
        rc, tail = r.returncode, (r.stdout + r.stderr).strip().splitlines()[-3:]
    except subprocess.TimeoutExpired:
        rc, tail = None, ["timeout after {}s".format(RERUN_TIMEOUT_SECONDS)]
    return {"rc": rc, "seconds": round(time.monotonic() - t0, 2), "tail": tail}


def judge(gate: dict, base: Base, root: Path) -> dict:
    """Base side and change side of one gate, in identical shadows."""
    head = {"gate": gate["module"] or gate["entry"], "touched": gate["touched"],
            "dropped_from_change_hook": gate["dropped_from_change_hook"]}
    if gate.get("deferred"):
        return {**head, "deferred": True, "would_refuse": None}
    base_files = {rel: base.read(rel) for rel in gate["closure"]}
    change_files = {}
    for rel in gate["closure"]:
        p = root / rel
        change_files[rel] = p.read_bytes() if p.is_file() else None
    with tempfile.TemporaryDirectory(prefix="base-judged-") as tmp:
        b, c = Path(tmp, "base"), Path(tmp, "change")
        build_shadow(root, b, base_files)
        build_shadow(root, c, change_files)
        base_run = run_gate(gate, b, root)
        if gate["dropped_from_change_hook"]:
            change_run = {"rc": 0, "seconds": 0.0, "tail": ["line absent from the change's hook"]}
        else:
            change_run = run_gate(gate, c, root)
    return {**head, "deferred": False, "base": base_run, "change": change_run,
            "would_refuse": base_run["rc"] not in (0, None) and change_run["rc"] == 0}


def log_path(root: Path) -> Path:
    """The REAL repo's common dir, even from surgical_land's standalone extract, whose objects are
    lent by an alternates line -- a log written inside the extract dies with it."""
    common = Path(root, _git(root, "rev-parse", "--git-common-dir").strip()).resolve()
    alternates = common / "objects" / "info" / "alternates"
    if alternates.is_file():
        first = alternates.read_text().splitlines()[0].strip()
        if first:
            common = Path(first).resolve().parent
    return common / LOG_NAME


def observe(root: Path) -> dict:
    t0 = time.monotonic()
    base = Base(root)
    staged = staged_paths(root)
    gates = affected_gates(base, root, staged)
    record = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "base": _git(root, "rev-parse", "HEAD").strip(), "mode": "observe",
              "staged": len(staged), "gate_data_touched": sorted(p for p in staged
                                                                  if _GATE_DATA.search(p)),
              "results": [judge(g, base, root) for g in gates]}
    # One line per commit, reruns or none: a log written only on a rerun cannot tell a week of
    # commits that touched no gate from an observer that never ran, and enforce's cost (GAP-6) is
    # this whole duration, not only the reruns'.
    record["observer_seconds"] = round(time.monotonic() - t0, 2)
    with log_path(root).open("a") as fh:
        fh.write(json.dumps(record) + "\n")
    for r in record["results"]:
        if r["would_refuse"]:
            print("[base-judged] OBSERVE: the base copy of {} refuses this change and the change's "
                  "own copy passes it -- enforce mode would refuse. Logged to {}.".format(
                      r["gate"], LOG_NAME), file=sys.stderr)
    return record


#: The steer's own condition for the flip: a week of real commits, read before enforcing.
OBSERVE_DAYS = 7


def summarise(records: list[dict]) -> dict:
    """What the enforce decision reads: how often enforce would have refused, how often a deep
    pytest closure was touched but not rerun, how often gate DATA was staged (GAP-1), and what
    the observer cost. `ready` is the week's span, not a count -- a busy afternoon is not a week."""
    if not records:
        return {"commits": 0, "ready": False}
    stamps = sorted(r["at"] for r in records)
    first, last = (calendar.timegm(time.strptime(t, "%Y-%m-%dT%H:%M:%SZ"))
                   for t in (stamps[0], stamps[-1]))
    span_days = (last - first) / 86400
    results = [r for rec in records for r in rec.get("results", [])]
    secs = sorted(rec.get("observer_seconds", 0.0) for rec in records)
    per_gate: dict[str, dict] = {}
    for r in results:
        g = per_gate.setdefault(r["gate"], {"rerun": 0, "deferred": 0, "would_refuse": 0})
        g["deferred" if r.get("deferred") else "rerun"] += 1
        g["would_refuse"] += bool(r.get("would_refuse"))
    return {
        "commits": len(records), "first": stamps[0], "last": stamps[-1],
        "span_days": round(span_days, 2), "ready": span_days >= OBSERVE_DAYS,
        "commits_with_a_rerun": sum(1 for rec in records if rec.get("results")),
        "would_refuse": sum(1 for r in results if r.get("would_refuse")),
        "deferred": sum(1 for r in results if r.get("deferred")),
        "gate_data_touched_commits": sum(1 for rec in records if rec.get("gate_data_touched")),
        "observer_seconds": {"median": secs[len(secs) // 2], "max": secs[-1],
                             "total": round(sum(secs), 1)},
        "per_gate": per_gate,
    }


def main(argv: list[str]) -> int:
    root = Path(_git(Path.cwd(), "rev-parse", "--show-toplevel").strip())
    if "--report" in argv:
        p = log_path(root)
        if not p.is_file():
            print("no base-judged commits logged yet ({})".format(p))
        elif "--raw" in argv:
            print(p.read_text())
        else:
            print(json.dumps(summarise([json.loads(x) for x in p.read_text().splitlines()
                                        if x.strip()]), indent=2))
        return 0
    try:
        observe(root)
    except Exception as exc:  # observe mode: a broken observer must never red a commit
        print("[base-judged] observer failed, nothing judged: {}".format(exc), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
