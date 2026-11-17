#!/usr/bin/env python3
"""Trial E-e's golden set: run a fixed seat task in a sealed clone on one CLAUDE.md arm, and grade it.

Director steer, 17 Nov 2026: each golden task runs twice on the full CLAUDE.md and twice on the
minimal draft, and a dropped line comes back if its absence fails a task in EITHER run. The tasks,
their inputs and their pass criteria are fixed in `docs/operations/EFFICIENCY_E_E_GOLDEN_SET.yaml`;
this file only runs and grades them.

    python3 -m tools.claude_md_golden_set --list
    python3 -m tools.claude_md_golden_set --run g06_g5_refusal --arm minimal --rep 1
    python3 -m tools.claude_md_golden_set --report

WHY A SHARED CLONE OF A SANDBOX ORIGIN, not the seat executor's worktree: a worktree shares this
repo's remotes, so a golden task could push. Here origin is a bare `--shared` clone inside the
sandbox with `main` at `base`: `surgical_land` (the habit under test) can land, and lands there.
A first version removed origin; the first run (g06, 17 Nov) then could not land at all, which would
have failed every commit task on both arms. No object copy; deleted after the grade (the transcript
is kept). The hooks are the clone's own `tools/git-hooks`, so a commit meets the real gates.
WHAT IS NOT SEALED: the run shares this machine. It can read the live daemons' state (g06 waited on
the real delivery seat's PID). Both arms share that equally; it is not a route into this repo.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
SET_PATH = REPO / "docs/operations/EFFICIENCY_E_E_GOLDEN_SET.yaml"
RESULTS = REPO / "docs/operations/efficiency_e_e_golden_runs.jsonl"
TRANSCRIPTS = Path.home() / ".cache/claude_md_golden"
ARMS = ("full", "minimal")


def load_set(path: Path = SET_PATH) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _git(cwd: Path, *args: str, check: bool = True) -> str:
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True,
                          check=check).stdout


def prepare(golden: dict, task: dict, arm: str, where: Path, repo: Path = REPO) -> Path:
    """A sealed clone at `base` with the arm's CLAUDE.md and the task's seeds, uncommitted. Its
    origin is a bare repo inside `where`, so a landing lands there and nothing reaches this repo."""
    bare, clone = where / "origin.git", where / "repo"
    subprocess.run(["git", "clone", "--bare", "--shared", "--quiet", str(repo), str(bare)], check=True)
    _git(bare, "update-ref", "refs/heads/main", golden["base"])
    subprocess.run(["git", "clone", "--shared", "--quiet", "--no-checkout", str(bare), str(clone)],
                   check=True)
    _git(clone, "checkout", "--quiet", "-B", "main", golden["base"])
    _git(clone, "config", "core.hooksPath", str(clone / "tools/git-hooks"))
    if arm == "minimal":
        (clone / "CLAUDE.md").write_bytes((clone / golden["minimal_draft"]).read_bytes())
    # Both arms alike: the arm's file is the environment, not the task's work, so git is told to
    # treat it as unchanged. It never shows in the task's diff and no commit can carry it.
    _git(clone, "update-index", "--skip-worktree", "CLAUDE.md")
    for rel, text in (task.get("seeds") or {}).items():
        target = clone / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    for edit in task.get("seeds_edit") or []:
        target = clone / edit["path"]
        body = target.read_text(encoding="utf-8")
        if edit["old"] not in body:
            raise SystemExit(f"seed edit cannot apply: {edit['old']!r} not in {edit['path']} at base")
        target.write_text(body.replace(edit["old"], edit["new"], 1), encoding="utf-8")
    return clone


def run_claude(clone: Path, prompt: str, model: str, timeout_s: int, out: Path) -> int:
    from background.model_tier import HEADLESS_FLAGS, UNATTENDED_TURN_ENDS
    from background.seat_executor import _resolve_claude
    binary = _resolve_claude()
    if binary is None:
        raise SystemExit("no claude binary on this machine")
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(clone)
    with out.open("w", encoding="utf-8") as fh:
        try:
            return subprocess.run(
                [binary, "-p", "--dangerously-skip-permissions", *HEADLESS_FLAGS, "--model", model,
                 "--output-format", "stream-json", "--verbose", prompt + UNATTENDED_TURN_ENDS],
                cwd=str(clone), stdout=fh, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                env=env, timeout=timeout_s).returncode
        except subprocess.TimeoutExpired:
            return 124


# ── the grade ────────────────────────────────────────────────────────────────────────────────────

def read_transcript(path: Path) -> tuple[list[str], str]:
    """(every tool call as 'Name: <json input>', in order; the final result text)."""
    calls: list[str] = []
    final = ""
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "assistant":
            for block in (event.get("message") or {}).get("content") or []:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    calls.append(f"{block.get('name')}: {json.dumps(block.get('input'))}")
        elif event.get("type") == "result":
            final = event.get("result") or ""
    return calls, final


def clone_state(clone: Path, base: str) -> dict:
    """What the run changed: paths (committed or not), the added diff lines per path, commits."""
    bare = clone.parent / "origin.git"
    commits = set(_git(clone, "rev-list", f"{base}..HEAD").split())
    committed = set(_git(clone, "diff", "--name-only", base, "HEAD").split())
    if bare.is_dir():  # a landing goes to the sandbox's own origin, not to the clone's HEAD
        commits |= set(_git(bare, "rev-list", f"{base}..main").split())
        committed |= set(_git(bare, "diff", "--name-only", base, "main").split())
    _git(clone, "add", "--intent-to-add", "--all", check=False)
    diff = _git(clone, "diff", base)
    added: dict[str, list[str]] = {}
    current = None
    for line in diff.splitlines():
        if line.startswith("+++ "):
            current = line[6:] if line.startswith("+++ b/") else None
            added.setdefault(current or "", [])
        elif current and line.startswith("+") and not line.startswith("+++"):
            added[current].append(line)
    changed = set(_git(clone, "diff", "--name-only", base).split()) | committed
    return {"commits": commits, "committed": committed, "changed": changed, "added": added}


def _paths(paths, glob: str) -> list[str]:
    return [p for p in paths if fnmatch.fnmatch(p, glob)]


def check(spec: dict, calls: list[str], final: str, state: dict) -> tuple[bool, str]:
    kind = spec.get("kind")
    if "any_of" in spec:
        legs = [check(leg, calls, final, state) for leg in spec["any_of"]]
        return any(ok for ok, _ in legs), "any_of: " + "; ".join(why for _, why in legs)
    bash = [c[len("Bash: "):] for c in calls if c.startswith("Bash: ")]
    if kind == "bash_any":
        hit = [b for b in bash if re.search(spec["regex"], b)]
        return bool(hit), f"bash_any {spec['regex']!r}: {len(hit)} matching command(s)"
    if kind == "bash_none":
        hit = [b for b in bash if re.search(spec["regex"], b)]
        return not hit, f"bash_none {spec['regex']!r}: " + (hit[0][:160] if hit else "none")
    if kind == "text_any":
        return bool(re.search(spec["regex"], final)), f"text_any {spec['regex']!r}"
    if kind == "text_none":
        m = re.search(spec["regex"], final)
        return m is None, f"text_none {spec['regex']!r}: " + (m.group(0) if m else "none")
    if kind == "changed_any":
        hit = _paths(state["changed"], spec["glob"])
        return bool(hit), f"changed_any {spec['glob']}: {hit[:3]}"
    if kind == "changed_none":
        hit = _paths(state["changed"], spec["glob"])
        return not hit, f"changed_none {spec['glob']}: {hit[:3]}"
    if kind == "committed_none":
        hit = _paths(state["committed"], spec["glob"])
        return not hit, f"committed_none {spec['glob']}: {hit[:3]}"
    if kind == "commits_min":
        return len(state["commits"]) >= spec["n"], f"commits_min {spec['n']}: {len(state['commits'])}"
    if kind == "added_none":
        hit = [ln for p in _paths(state["added"], spec["glob"]) for ln in state["added"][p]
               if re.search(spec["regex"], ln)]
        return not hit, f"added_none {spec['glob']} {spec['regex']!r}: " + (hit[0][:160] if hit else "none")
    if kind == "before":
        first = next((i for i, c in enumerate(calls) if re.search(spec["first"], c)), None)
        then = next((i for i, c in enumerate(calls) if re.search(spec["then"], c)), None)
        ok = then is None or (first is not None and first < then)
        return ok, f"before: first at {first}, then at {then}"
    raise ValueError(f"unknown check kind {kind!r} in the golden set")


def grade(task: dict, calls: list[str], final: str, state: dict) -> dict:
    legs = [check(spec, calls, final, state) for spec in task["checks"]]
    return {"passed": all(ok for ok, _ in legs),
            "checks": [{"ok": ok, "why": why} for ok, why in legs]}


# ── the command line ─────────────────────────────────────────────────────────────────────────────

def run_one(task_id: str, arm: str, rep: int, *, keep: bool = False) -> dict:
    golden = load_set()
    task = next((t for t in golden["tasks"] if t["id"] == task_id), None)
    if task is None:
        raise SystemExit(f"no golden task {task_id!r}")
    if arm not in ARMS:
        raise SystemExit(f"arm must be one of {ARMS}")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    TRANSCRIPTS.mkdir(parents=True, exist_ok=True)
    transcript = TRANSCRIPTS / f"{task_id}.{arm}.{rep}.{stamp}.jsonl"
    where = Path(tempfile.mkdtemp(prefix=f"golden_{task_id}_{arm}_"))
    try:
        clone = prepare(golden, task, arm, where)
        code = run_claude(clone, task["prompt"], golden["model"], golden["timeout_s"], transcript)
        calls, final = read_transcript(transcript)
        result = grade(task, calls, final, clone_state(clone, golden["base"]))
    finally:
        if not keep:
            shutil.rmtree(where, ignore_errors=True)
    row = {"at": stamp, "task": task_id, "arm": arm, "rep": rep, "base": golden["base"],
           "exit": code, "tool_calls": len(calls), "transcript": str(transcript), **result}
    with RESULTS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")
    return row


def report(path: Path = RESULTS) -> str:
    rows = [json.loads(ln) for ln in path.read_text().splitlines() if ln.strip()] if path.exists() else []
    lines = ["| task | arm | rep | passed | failed checks |", "|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r["task"], r["arm"], r["rep"], r["at"])):
        failed = "; ".join(c["why"] for c in r["checks"] if not c["ok"]) or "-"
        lines.append(f"| {r['task']} | {r['arm']} | {r['rep']} | {r['passed']} | {failed} |")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--run")
    ap.add_argument("--arm", choices=ARMS)
    ap.add_argument("--rep", type=int, default=1)
    ap.add_argument("--keep", action="store_true", help="keep the clone for a re-read")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args(argv)
    if a.list:
        for t in load_set()["tasks"]:
            print(f"{t['id']:40s} {t['covers']}")
    elif a.run:
        print(json.dumps(run_one(a.run, a.arm or "full", a.rep, keep=a.keep), indent=1))
    elif a.report:
        print(report())
    else:
        ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
