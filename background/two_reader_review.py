#!/usr/bin/env python3
"""Two blind readers on every origin/main commit that adds a module; a finding is filed only when both raise it.

WHY (director ruling, 28 Oct 2026, 06:39 "Go", in docs/staging/advisor/done/DIRECTOR_RULING_GO_ON_
THE_TWO_READER_REVIEW_AND_START_IT_NOW_2026-10-28.md): two blind, non-blocking Opus readers on
commits that add a new module; a finding filed only when both readers raise it, then checked like
any finding; scored through `judge_validation` until the 11 Nov review, and stopped if fewer than
half the filed findings are confirmed. The seat ran it by hand on 28 Oct over 2 of 157 commits. A
manual start is not a running trial, so this is the lane that runs it.

    python3 -m background.two_reader_review --status   # what qualifies, what is read, what waits
    python3 -m background.two_reader_review --tick     # read the oldest unread qualifying commit

WHAT A READER CAN SEE. One `git archive` extract of the commit's own tree (no `.git`, so no later
history and no verdict written after it), and a packet beside it: the commit message as the
statement of intent, the stat, and the `.py` diff. Both readers share the one extract (629 MB at
28 Oct, so it lives on disk under ~/.cache, not on the RAM-backed /tmp). Each reader runs
`claude -p --restricted --tools Read Grep Glob` with that scratch dir as cwd. Measured before this
was written: such a session reads inside the dir, is refused a path outside it, and has no write or
shell tool. The director_twin incident of 12 Jul is why a reader never gets Bash or this repo as
its cwd: a tooled headless session in the shared tree once committed and pushed on its own.

WHAT "BOTH RAISE IT" MEANS. Each reader ends with a JSON block of findings. A third, tool-less call
sees only the two finding lists and pairs a finding of A with the finding of B that names the same
defect. The pairs are validated against the ids that exist (each id pairs at most once). The vote
is a judgement, so the matcher's pairs are written beside the claims they join and the seat can
undo any of them.

WHAT IS FILED. One staging finding per commit with at least one pair, capped at MAJOR. The vote is
an unchecked claim; the seat's check at HEAD is what can make it BLOCKING. Findings only one reader
raised go in that reader's trust-ledger notes, so the 11 Nov review can see what the vote discarded.

GAP, stated rather than hidden: the ruling's second class, a commit that "re-implements a rule
something else already computes", has no mechanical selector. Only module-adding commits are read.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from background import judge_validation as jv  # noqa: E402
from background import trust_ledger as tl  # noqa: E402
from background.secrets_location import scrub_model_facing_env  # noqa: E402

#: The trial window the ruling set: the hand run counted from 26 Oct, and the review is 11 Nov.
#: After the review date nothing new is selected until a decision there moves this line.
TRIAL_START = "2026-10-26T00:00:00Z"
REVIEW_DATE = "2026-11-11"

SUBJECT_PREFIX = "reading-review-live"
EVALUATOR = "phase-close-evaluator"
ROUTE = "two-reader-review"
MODEL = "opus"
READER_TIMEOUT_S = 25 * 60
MATCHER_TIMEOUT_S = 5 * 60
#: A commit whose readers fail this many times is given up on and the reason recorded; retrying
#: forever would hold the queue behind one commit the readers cannot read.
MAX_ATTEMPTS = 3

SCRATCH_ROOT = Path.home() / ".cache" / "synthetic-enterprise" / "two_reader_review"
#: Untracked machine state (see `.gitignore`): every attempt, with both raw reader outputs.
READINGS_PATH = PROJECT_DIR / "docs" / "observability" / ".two_reader_readings.jsonl"
STAGING_DIR = PROJECT_DIR / "docs" / "staging"
AGENT_BRIEF = Path(".claude") / "agents" / "phase-close-evaluator.md"
LEDGER_REPO_PATH = "docs/observability/trust_ledger.json"

SEVERITIES = ("MINOR", "MAJOR", "BLOCKING")
FILED_CEILING = "MAJOR"


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=str(PROJECT_DIR), capture_output=True, text=True,
                          check=True, timeout=300).stdout


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ── selection ───────────────────────────────────────────────────────────────────────────────────

def is_module(path: str) -> bool:
    """A non-test Python module: the ruling's mechanical class."""
    p = Path(path)
    return (p.suffix == ".py" and "tests" not in p.parts and not p.name.startswith("test_")
            and p.name != "conftest.py")


def qualifying_commits(ref: str = "origin/main", since: str = TRIAL_START, git=_git) -> list[dict]:
    """Oldest first: every non-merge commit on `ref` since `since` that ADDS a non-test module."""
    out = git("log", "--no-merges", "--reverse", f"--since={since}", "--diff-filter=A",
              "--name-only", "--format=@%H %cI", ref)
    commits, cur = [], None
    for line in out.splitlines():
        if line.startswith("@"):
            sha, when = line[1:].split(" ", 1)
            cur = {"sha": sha, "committed": when, "modules": []}
            commits.append(cur)
        elif line.strip() and cur is not None and is_module(line.strip()):
            cur["modules"].append(line.strip())
    return [c for c in commits if c["modules"]]


def _ledger_entries(ref: str = "origin/main", git=_git) -> list[dict]:
    """The working-tree ledger AND the one committed on `ref`. The shared tree can lag origin by
    tens of commits (51 when this was written), and a reading recorded on origin but missing here
    would otherwise be bought twice."""
    texts = []
    try:
        texts.append(tl.LEDGER_PATH.read_text())
    except OSError:
        pass
    try:
        texts.append(git("show", f"{ref}:{LEDGER_REPO_PATH}"))
    except subprocess.SubprocessError:
        pass
    entries = []
    for text in texts:
        try:
            data = json.loads(text)
        except ValueError:
            continue
        if isinstance(data, list):
            entries.extend(e for e in data if isinstance(e, dict))
    return entries


def read_shas(entries: list[dict] | None = None) -> set[str]:
    """Short shas with BOTH arms in the ledger, hand-run or automatic."""
    arms: dict[str, set[str]] = {}
    for e in _ledger_entries() if entries is None else entries:
        m = re.match(rf"{SUBJECT_PREFIX}-[\d-]+:([0-9a-f]+):arm([AB])$", str(e.get("subject", "")))
        if m:
            arms.setdefault(m.group(1), set()).add(m.group(2))
    return {s for s, a in arms.items() if a == {"A", "B"}}


def _is_read(sha: str, shas: set[str]) -> bool:
    return any(sha.startswith(s) for s in shas)


def _attempts(path: Path = READINGS_PATH) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    try:
        lines = path.read_text().splitlines()
    except OSError:
        return out
    for line in lines:
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        out.setdefault(rec.get("sha", ""), []).append(rec)
    return out


def queue(commits: list[dict], shas: set[str], attempts: dict[str, list[dict]]) -> dict:
    """{'read': [...], 'given_up': [...], 'waiting': [...]} over the qualifying commits."""
    read, given_up, waiting = [], [], []
    for c in commits:
        if _is_read(c["sha"], shas):
            read.append(c)
        elif len(attempts.get(c["sha"], [])) >= MAX_ATTEMPTS:
            given_up.append(c)
        else:
            waiting.append(c)
    return {"read": read, "given_up": given_up, "waiting": waiting}


# ── the readers ─────────────────────────────────────────────────────────────────────────────────

def _brief(tree: Path) -> str:
    """The evaluator's own brief, as it stood in the commit's tree, without its frontmatter."""
    try:
        text = (tree / AGENT_BRIEF).read_text()
    except OSError:
        return ""
    return re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)


def reader_prompt(brief: str) -> str:
    return f"""{brief}

---

## This reading

You are one of two blind readers of ONE commit. You will never see the other reader.

- `./tree` is the commit's own tree, extracted with `git archive` (no history). Paths the brief
  above names are under `./tree`.
- `./packet/message.txt` is the commit message: its statement of intent.
- `./packet/stat.txt` is its stat; `./packet/diff.patch` is its Python diff.
- You have Read, Grep and Glob only. Where the brief above asks you to run git or any command, to
  start your reply with a bare verdict, or to record your verdict yourself, skip it: the packet
  replaces git, and the lane records your verdict from the json block below.

Read the diff and the code it touches. Judge whether the commit does what its message claims, and
whether what it added is correct: a control that cannot fail, a quantity that is not what it says,
a rule that disagrees with another copy of itself, an edge the tests never reach. You have read-only
tools. Fix nothing. Name the input that shows each defect.

End your answer with exactly one fenced json block, and nothing after it:

```json
{{"verdict": "PASS or NEEDS_WORK",
  "findings": [{{"id": 1, "severity": "BLOCKING or MAJOR or MINOR", "file": "path under tree",
                "line": 123, "claim": "the defect, and the input that shows it"}}]}}
```
"""


MATCHER_PROMPT = """Two readers reviewed the same commit independently. Below are their findings.

Pair a finding of reader A with the finding of reader B that names the SAME defect: the same code
doing the same wrong thing. The same file or the same topic is not enough. Each finding pairs at
most once. Most findings will have no pair.

Reader A:
{a}

Reader B:
{b}

Answer with exactly one fenced json block and nothing else:

```json
{{"pairs": [[a_id, b_id]]}}
```
"""


def _claude_bin() -> str | None:
    for c in (os.environ.get("CLAUDE_BIN"), shutil.which("claude"),
              str(Path.home() / ".nvm/versions/node/v24.16.0/bin/claude")):
        if c and Path(c).exists():
            return c
    return None


def run_claude(prompt: str, cwd: Path, tools: tuple[str, ...], timeout: int) -> tuple[int, str]:
    """One restricted `claude -p` session, prompt on stdin (`--tools` is variadic and would eat a
    positional prompt). `tools=()` disables every tool."""
    binary = _claude_bin()
    if binary is None:
        return 127, "no claude binary on this machine"
    tool_args = ["--tools", *tools] if tools else ["--tools="]
    try:
        res = subprocess.run([binary, "-p", "--model", MODEL, "--restricted", *tool_args],
                             input=prompt, cwd=str(cwd), capture_output=True, text=True,
                             timeout=timeout, env=scrub_model_facing_env(os.environ.copy()))
    except subprocess.TimeoutExpired:
        return 124, f"timed out after {timeout}s"
    return res.returncode, res.stdout if res.returncode == 0 else (res.stdout + res.stderr)[-2000:]


def last_json_block(text: str):
    blocks = re.findall(r"```json\s*\n(.*?)```", text, flags=re.S)
    if not blocks:
        return None
    try:
        return json.loads(blocks[-1])
    except ValueError:
        return None


def parse_reading(text: str) -> dict | None:
    """{'verdict': 'PASS'|'NEEDS_WORK', 'findings': [...]} or None when the reader broke format.
    A NEEDS_WORK with no findings is accepted (the verdict stands); a finding with no claim is not."""
    data = last_json_block(text)
    if not isinstance(data, dict) or data.get("verdict") not in ("PASS", "NEEDS_WORK"):
        return None
    findings = data.get("findings") or []
    if not isinstance(findings, list):
        return None
    clean, ids = [], set()
    for f in findings:
        if not isinstance(f, dict) or not isinstance(f.get("id"), int) or f["id"] in ids:
            return None
        if not str(f.get("claim", "")).strip():
            return None
        ids.add(f["id"])
        sev = str(f.get("severity", "")).upper()
        clean.append({"id": f["id"], "severity": sev if sev in SEVERITIES else "MINOR",
                      "file": str(f.get("file", "")), "line": f.get("line"),
                      "claim": str(f["claim"]).strip()})
    return {"verdict": data["verdict"], "findings": clean}


def valid_pairs(raw, a: list[dict], b: list[dict]) -> list[tuple[int, int]]:
    """The matcher's pairs that name ids which exist, each id used once. Anything else is dropped."""
    if not isinstance(raw, dict) or not isinstance(raw.get("pairs"), list):
        return []
    a_ids, b_ids = {f["id"] for f in a}, {f["id"] for f in b}
    used_a, used_b, out = set(), set(), []
    for p in raw["pairs"]:
        if (isinstance(p, list) and len(p) == 2 and p[0] in a_ids and p[1] in b_ids
                and p[0] not in used_a and p[1] not in used_b):
            used_a.add(p[0])
            used_b.add(p[1])
            out.append((p[0], p[1]))
    return out


def task_class(modules: list[str]) -> tl.TaskClass:
    """Coarse, from where the new module lives. The enum is the ledger's, and registering a finer
    class is a decision this lane does not take."""
    tops = {Path(m).parts[0] for m in modules}
    if "site" in tops:
        return tl.TaskClass.SITE_PRESENTATION
    if tops & {"company", "saas", "sim", "simulation"}:
        return tl.TaskClass.BILLING
    if tops <= {"docs"}:
        return tl.TaskClass.DOCS_DISCOVERY
    return tl.TaskClass.HARNESS_SUPERVISOR


# ── one reading ─────────────────────────────────────────────────────────────────────────────────

def _extract(sha: str, dest: Path) -> None:
    (dest / "tree").mkdir(parents=True)
    (dest / "packet").mkdir()
    archive = subprocess.Popen(["git", "archive", sha], cwd=str(PROJECT_DIR), stdout=subprocess.PIPE)
    subprocess.run(["tar", "-x", "-C", str(dest / "tree")], stdin=archive.stdout, check=True)
    archive.stdout.close()
    if archive.wait() != 0:
        raise RuntimeError(f"git archive {sha} failed")
    (dest / "packet" / "message.txt").write_text(_git("log", "-1", "--format=%B", sha))
    (dest / "packet" / "stat.txt").write_text(_git("show", "--stat", "--format=", sha))
    (dest / "packet" / "diff.patch").write_text(_git("show", "--format=", sha, "--", "*.py"))


def _filed_severity(pairs, a: list[dict], b: list[dict]) -> str:
    by_a, by_b = {f["id"]: f for f in a}, {f["id"]: f for f in b}
    rank = {s: i for i, s in enumerate(SEVERITIES)}
    agreed = [min(rank[by_a[i]["severity"]], rank[by_b[j]["severity"]]) for i, j in pairs]
    return SEVERITIES[min(max(agreed), rank[FILED_CEILING])]


def finding_text(commit: dict, pairs, a: dict, b: dict, today: str) -> str:
    sha10 = commit["sha"][:10]
    by_a, by_b = {f["id"]: f for f in a["findings"]}, {f["id"]: f for f in b["findings"]}
    rows = []
    for n, (i, j) in enumerate(pairs, 1):
        fa, fb = by_a[i], by_b[j]
        rows.append(f"{n}. **A#{i} ({fa['severity']}) `{fa['file']}:{fa['line']}`** {fa['claim']}\n"
                    f"   **B#{j} ({fb['severity']}) `{fb['file']}:{fb['line']}`** {fb['claim']}")
    paired_a, paired_b = {i for i, _ in pairs}, {j for _, j in pairs}
    single = [f"- A#{f['id']} ({f['severity']}): {f['claim']}" for f in a["findings"]
              if f["id"] not in paired_a]
    single += [f"- B#{f['id']} ({f['severity']}): {f['claim']}" for f in b["findings"]
               if f["id"] not in paired_b]
    return f"""**Severity:** {_filed_severity(pairs, a['findings'], b['findings'])} · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Both blind readers raise {len(pairs)} finding(s) on {sha10} ({today})

*Written by `background/two_reader_review.py`, the automatic lane of the two-reader trial
(director ruling 28 Oct, review {REVIEW_DATE}). Nothing here has been checked. Check each pair at
HEAD like any other finding, and record the outcome for the review. Severity is capped at
{FILED_CEILING} until a check confirms more.*

- **Commit:** `{commit['sha']}`, committed {commit['committed']}.
- **Modules it added:** {', '.join(f'`{m}`' for m in commit['modules'])}.
- **Verdicts:** A {a['verdict']}, B {b['verdict']} (trust ledger,
  `{SUBJECT_PREFIX}-{today}:{sha10}:arm{{A,B}}`).

## Raised by both (pairs from the tool-less matcher; undo any that do not name one defect)

{chr(10).join(rows)}

## Raised by one reader only (not filed under the vote)

{chr(10).join(single) or '- none'}
"""


def _slug(sha10: str, n: int, today: str) -> str:
    return f"WORKER_FINDING_BOTH_BLIND_READERS_RAISE_{n}_ON_{sha10.upper()}_{today}.md"


def _ledger_notes(reading: dict, paired: set[int], other: str) -> str:
    claims = "; ".join(f"#{f['id']}{'*' if f['id'] in paired else ''} {f['claim'][:160]}"
                       for f in reading["findings"])
    return (f"TWO-READER REVIEW, automatic lane. {len(reading['findings'])} raised, {len(paired)} "
            f"shared with arm {other} (*). {claims}")[:1500]


def _append(rec: dict, path: Path = READINGS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")


def read_commit(commit: dict, *, claude=run_claude, record=jv.record_close_verdict,
                staging: Path = STAGING_DIR, readings: Path = READINGS_PATH) -> dict:
    """Two readers, the matcher, both verdicts recorded, the finding filed. Returns the record."""
    today = _now().date().isoformat()
    sha10 = commit["sha"][:10]
    rec = {"sha": commit["sha"], "at": _now().isoformat(timespec="seconds"), "outcome": None}
    SCRATCH_ROOT.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix=f"{sha10}_", dir=str(SCRATCH_ROOT)))
    try:
        return _read_in(commit, scratch, rec, today, claude=claude, record=record,
                        staging=staging, readings=readings)
    except Exception as exc:  # noqa: BLE001 -- an unlogged failure could never reach MAX_ATTEMPTS
        rec.update(outcome="error", error=f"{type(exc).__name__}: {exc}"[:1000])
        _append(rec, readings)
        return rec
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def _read_in(commit, scratch, rec, today, *, claude, record, staging, readings) -> dict:
    """The reading itself; `read_commit` logs any way out of it, an exception included."""
    sha10 = commit["sha"][:10]
    _extract(commit["sha"], scratch)
    prompt = reader_prompt(_brief(scratch / "tree"))
    raw, parsed = {}, {}
    for arm in ("A", "B"):
        rc, out = claude(prompt, scratch, ("Read", "Grep", "Glob"), READER_TIMEOUT_S)
        raw[arm] = out
        parsed[arm] = parse_reading(out) if rc == 0 else None
        if parsed[arm] is None:
            rec.update(outcome="unreadable", arm=arm, rc=rc, raw=raw)
            _append(rec, readings)
            return rec
    a, b = parsed["A"], parsed["B"]
    pairs = []
    if a["findings"] and b["findings"]:
        rc, out = claude(MATCHER_PROMPT.format(a=json.dumps(a["findings"], indent=1),
                                               b=json.dumps(b["findings"], indent=1)),
                         scratch, (), MATCHER_TIMEOUT_S)
        if rc != 0:
            rec.update(outcome="matcher_failed", rc=rc, raw=raw, matcher=out)
            _append(rec, readings)
            return rec
        raw_pairs = last_json_block(out)
        if not isinstance(raw_pairs, dict) or not isinstance(raw_pairs.get("pairs"), list):
            # rc 0 with prose is a failed match, not "no pairs": read as [] it would record both
            # verdicts and drop the commit from the queue with nothing filed, for good.
            rec.update(outcome="matcher_failed", rc=rc, raw=raw, matcher=out)
            _append(rec, readings)
            return rec
        pairs = valid_pairs(raw_pairs, a["findings"], b["findings"])
        rec["matcher"] = out
    tc = task_class(commit["modules"])
    for arm, other, reading, side in (("A", "B", a, 0), ("B", "A", b, 1)):
        record(tc, "pass" if reading["verdict"] == "PASS" else "needs_work", EVALUATOR,
               f"{SUBJECT_PREFIX}-{today}:{sha10}:arm{arm}", evaluated_at=today,
               notes=_ledger_notes(reading, {p[side] for p in pairs}, other))
    filed = None
    if pairs:
        filed = staging / _slug(sha10, len(pairs), today)
        filed.write_text(finding_text(commit, pairs, a, b, today))
    rec.update(outcome="read", verdicts=[a["verdict"], b["verdict"]], pairs=pairs,
               readings=parsed, raw=raw, filed=str(filed.relative_to(PROJECT_DIR)) if filed
               and filed.is_relative_to(PROJECT_DIR) else (str(filed) if filed else None))
    _append(rec, readings)
    return rec


# ── the tick ────────────────────────────────────────────────────────────────────────────────────

def tick(*, gate=None) -> str:
    """Read at most ONE waiting commit; returns the line the journal keeps."""
    if _now().date().isoformat() > REVIEW_DATE:
        return f"trial past its review date {REVIEW_DATE}: nothing selected until the review moves it"
    if gate is None:
        from background import tick_mode
        gate = tick_mode.gate
    ok, _mode, why = gate(ROUTE)
    if not ok:
        return f"held: {why}"
    q = queue(qualifying_commits(), read_shas(), _attempts())
    if not q["waiting"]:
        return f"nothing waiting: {len(q['read'])} read, {len(q['given_up'])} given up"
    from background import tick_mode
    tick_mode.note_spawn(ROUTE)
    rec = read_commit(q["waiting"][0])
    return (f"{rec['sha'][:10]}: {rec['outcome']}"
            + (f", {len(rec.get('pairs', []))} shared, filed {rec.get('filed')}"
               if rec["outcome"] == "read" else "")
            + f"; {len(q['waiting']) - 1} still waiting")


def status() -> str:
    commits = qualifying_commits()
    attempts = _attempts()
    q = queue(commits, read_shas(), attempts)
    n = sum(1 for c in _git("log", "--no-merges", f"--since={TRIAL_START}", "--format=%H",
                            "origin/main").splitlines() if c)
    lines = [f"two-reader review, {TRIAL_START[:10]} to {REVIEW_DATE}: {len(commits)} of {n} "
             f"non-merge commits qualify ({len(commits) / n:.1%})" if n else "no commits",
             f"read {len(q['read'])}, waiting {len(q['waiting'])}, given up {len(q['given_up'])}"]
    for c in q["waiting"] + q["given_up"]:
        tries = attempts.get(c["sha"], [])
        last = tries[-1]["outcome"] if tries else "never tried"
        lines.append(f"  {c['sha'][:10]} {c['committed'][:10]} {len(tries)} tries ({last}) "
                     f"{', '.join(c['modules'])}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="two_reader_review", description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--tick", action="store_true")
    g.add_argument("--status", action="store_true")
    args = ap.parse_args(argv)
    print(tick() if args.tick else status())
    return 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/two_reader_review.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("two_reader_review")
    sys.exit(main())
