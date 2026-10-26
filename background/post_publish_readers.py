#!/usr/bin/env python3
"""After a publish lands, run the tests that READ what it published, and say if any went red.

WHY (the 2248e3baf publish, 2026-10-13). That publish rewrote `docs/state/billing_ledger.json` and
`docs/reports/run_output_latest.json.gz`, and three real-book controls went red on the new bytes.
Nothing saw it for three days, because every check that could have seen it was structurally
unable to:

- the publish gate tests HEAD BEFORE the new artefacts exist, so it grades the previous book;
- the post-publish remainder is the whole suite and is skipped before it starts (4 of 4 attempts
  timed out; `run_remainder_annotation_step`);
- the nightly census runs the whole suite too, and did not complete 10-12 to 10-15 (deferred by
  headroom twice, timed out once).

The tests that read the published book take ~tens of seconds. They do not need the whole suite's
budget; they needed a run of their own, keyed to the event that changes their input.

THE SET IS DERIVED, NOT LISTED. A hand list rots the day a new control starts reading the ledger.
Two hops, both textual and cheap (no import, no collection):

1. a test file that names an artefact's repo path (`docs/state/billing_ledger.json`, or the
   `"state" / "billing_ledger.json"` join);
2. a test file that names a module which binds a module-level constant to that path AND names the
   constant (`sx.LEDGER_PATH` in the statement control is the case hop 1 missed: that file never
   spells the path).

A file a hop admits may still only read a fixture; running it costs seconds and cannot red falsely
for that reason, so the hops err wide. What they can MISS is a test reaching the artefact through
a function default three calls deep -- said here rather than discovered.

A SEPARATE OBSERVATION, ON PURPOSE. This writes its own store and never
`.head_red_observed.json`: the census store is a whole-suite observation, and folding a partial run
into it would read every red this run never reached as fixed. The reds reach a reader through
`doorbell_clause()`, which the supervisor puts beside the head-red register's own clause.
"""
from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from tools.python_code_text import searchable

PROJECT_DIR = Path(__file__).resolve().parent.parent

#: The real-book artefacts a publish rewrites and controls read. Named by the PLAIN json path,
#: which is what readers spell (the committed `.json.gz` is read through `run_output_store`).
ARTEFACTS = ("docs/state/billing_ledger.json", "docs/reports/run_output_latest.json")

#: Readers whose subject is every published PAGE rather than one artefact, so no path in their
#: text predicts them: a publish rewrites pages and the feeds they render, and what a phone reader
#: meets is a property of the laid-out page (director's steer, 26 Oct 2026: "Add the hscroll=false
#: at 390 px check for every published page to the post-publish readers"). Named, not derived,
#: and `test_post_publish_readers` holds each to a file that exists.
PAGE_READERS = ("site/test_no_published_page_scrolls_sideways_on_a_phone.py",)

#: Untracked machine state (see `.gitignore`), dot-prefixed like its neighbours.
OBSERVED_PATH = PROJECT_DIR / "docs" / "observability" / ".post_publish_reader_reds.json"

#: The run's own ceiling. Measured 2026-10-16 at badd57e8e: the 38 derived files run in 153s as one
#: pytest (the two controls that went red take ~4s between them). Before docstrings were
#: ignored the derivation admitted 57 and the run took 899.5s, half a second under this ceiling --
#: which is what a reader-set that has started admitting bystanders looks like from here.
TIMEOUT_SECONDS = 900

#: Where hop 2 looks for constants. Tests are excluded: a test's own constant is hop 1's business.
SOURCE_DIRS = ("background", "company", "saas", "sim", "simulation", "tools")

RAN = "ran"
TIMED_OUT = "timed_out"
UNAVAILABLE = "unavailable"


def _path_patterns(rel: str) -> list[re.Pattern]:
    """The two spellings of one repo path: the slashed literal and the `/`-joined parts."""
    parts = rel.split("/")
    joined = r'\s*/\s*'.join('"{}"'.format(re.escape(p)) for p in parts[-2:])
    return [re.compile(re.escape(rel)), re.compile(joined)]


def _module_name(path: Path, root: Path) -> str:
    return ".".join(path.relative_to(root).with_suffix("").parts)


def _candidates(root: Path, needles, dirs, glob: str) -> list[Path]:
    """Files under `dirs` containing any needle's basename -- a fixed-string prefilter so the
    regexes and the parse run over tens of files, not thousands. `git grep` when it can (tracked
    files, fast); a plain walk when `root` is not a checkout (the tests' tmp trees)."""
    words = sorted({Path(n).name for n in needles})
    argv = ["git", "grep", "-l", "-F"] + [a for w in words for a in ("-e", w)] + ["--", *dirs]
    try:
        res = subprocess.run(argv, cwd=str(root), capture_output=True, text=True, timeout=60)
        if res.returncode in (0, 1) and (root / ".git").exists():
            return sorted(root / line for line in res.stdout.splitlines()
                          if Path(line).match(glob))
    except (OSError, subprocess.SubprocessError):
        pass
    out = []
    for d in dirs:
        for path in sorted((root / d).rglob(glob)):
            try:
                text = searchable(path.read_text(errors="replace"))
            except OSError:
                continue
            if any(w in text for w in words):
                out.append(path)
    return out


def artefact_constants(artefacts=ARTEFACTS, root: Path = PROJECT_DIR) -> dict[str, set[str]]:
    """{dotted module: {CONSTANT, ...}} for every module-level name bound to an artefact path."""
    pats = [p for rel in artefacts for p in _path_patterns(rel)]
    found: dict[str, set[str]] = {}
    for d in SOURCE_DIRS:
        for path in _candidates(root, artefacts, (d,), "*.py"):
            if "tests" in path.relative_to(root).parts:
                continue
            try:
                text = path.read_text(errors="replace")
            except OSError:
                continue
            if not any(p.search(searchable(text)) for p in pats):
                continue
            try:
                tree = ast.parse(text)
            except SyntaxError:
                continue
            for node in tree.body:
                targets = (node.targets if isinstance(node, ast.Assign)
                           else [node.target] if isinstance(node, ast.AnnAssign) else [])
                names = [t.id for t in targets if isinstance(t, ast.Name)]
                # A bare string is a repo-RELATIVE name, joined to whatever root the caller holds
                # (`wall_channel_census.ARTEFACT_REL` is joined to a tmp git tree in all 259 of
                # its tests). A Path expression is the real file.
                if not names or (isinstance(node.value, ast.Constant)
                                 and isinstance(node.value.value, str)):
                    continue
                # The value's string parts joined as a path: `PROJECT / "docs" / "state" /
                # "billing_ledger.json"` and `Path("docs/state/billing_ledger.json")` both read
                # `.../docs/state/billing_ledger.json` -- asked of the parse tree, not the text.
                # Sorted by position: `ast.walk` is breadth-first, so a `/` chain comes out reversed.
                consts = sorted((n for n in ast.walk(node.value)
                                 if isinstance(n, ast.Constant) and isinstance(n.value, str)),
                                key=lambda n: (n.lineno, n.col_offset))
                parts = "/".join(n.value for n in consts)
                if any(rel in parts for rel in artefacts):
                    found.setdefault(_module_name(path, root), set()).update(names)
    return found


def reader_tests(artefacts=ARTEFACTS, root: Path = PROJECT_DIR) -> list[str]:
    """Repo-relative test files that read an artefact, by either hop. Sorted, deduplicated."""
    pats = [p for rel in artefacts for p in _path_patterns(rel)]
    consts = artefact_constants(artefacts, root)
    # The LAST component, matched on an import line, not the dotted name: `from company.billing
    # import statement_export as sx` never spells `company.billing.statement_export`, and that is
    # the case hop 2 exists for. On an IMPORT line because `company/portal/app.py` binds one, and
    # a bare `\bapp\b` is in half the suite.
    hop2 = [(re.compile(r"(?m)^\s*(?:from|import)\s[^\n]*\b{}\b".format(
                re.escape(mod.rsplit(".", 1)[-1]))),
             re.compile(r"\b(?:{})\b".format("|".join(map(re.escape, sorted(names))))))
            for mod, names in consts.items()]
    # The prefilter needs only what EVERY match must contain: an artefact name (hop 1) or a
    # constant's name (hop 2).
    names = set(artefacts) | {c for cs in consts.values() for c in cs}
    out = []
    for path in _candidates(root, sorted(names), ("tests",), "test_*.py"):
        try:
            # Docstrings and comments blanked: a file that only TALKS about the ledger is not a
            # reader. `test_generate_value_arms_data` names the run output five times, all in
            # prose, and cost 300s+ of a run it had no business in.
            text = searchable(path.read_text(errors="replace"))
        except OSError:
            continue
        if any(p.search(text) for p in pats) or any(
                m.search(text) and c.search(text) for m, c in hop2):
            out.append(str(path.relative_to(root)))
    return out


def _default_runner(argv, timeout):
    env = dict(os.environ)
    env["SIM_FAST_MODE"] = "1"
    return subprocess.run(argv, cwd=str(PROJECT_DIR), env=env, timeout=timeout,
                          capture_output=True, text=True, errors="replace")


def run(git_hash: str | None, parse_reds, *, runner=None, timeout: float = TIMEOUT_SECONDS,
        files=None, path: Path | None = None, now=None) -> dict:
    """Run the readers, write the observation, return it. Never raises: it observes a publish
    that has already landed and must not be able to affect it.

    `parse_reds` is HANDED IN, and it is always `process_run_complete._parse_failed_node_ids` so
    this run and the gate read a red the same way. It is not imported here because the supervisor
    imports this module for its doorbell, and a supervisor that reaches the publish path makes
    every test that imports the supervisor block publishing (`test_publish_scope`)."""
    path = path or OBSERVED_PATH
    started = time.monotonic()
    state = {"checked_at": (now or datetime.now(timezone.utc)).replace(microsecond=0).isoformat(),
             "git_hash": git_hash, "artefacts": list(ARTEFACTS)}
    try:
        # The page readers join AFTER the emptiness check: an empty derivation is still the
        # derivation broken, and must not read as a run because the named readers filled it.
        derived = files is None
        files = reader_tests() if derived else list(files)
        if files and derived:
            files += [f for f in PAGE_READERS if f not in files]
        state["files"] = len(files)
        if not files:
            # Zero readers found is the derivation breaking, not a clean bill: say so.
            state.update(outcome=UNAVAILABLE, rc=None, reds=[],
                         reason="no reader test was derived; the derivation itself is broken")
        else:
            argv = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                    "-o", "addopts=", *files]
            result = (runner or _default_runner)(argv, timeout)
            reds = parse_reds(getattr(result, "stdout", "") or "")
            if result.returncode not in (0, 5) and not reds:
                # A failed run with no summary is unreadable, never clean (OOM kills look like this).
                reds = ["UNREADABLE: the reader run exited rc={} with no pytest summary".format(
                    result.returncode)]
            state.update(outcome=RAN, rc=result.returncode, reds=reds[:64])
    except subprocess.TimeoutExpired:
        state.update(outcome=TIMED_OUT, rc=None, reds=[],
                     reason="did not finish inside {:.0f}s".format(timeout))
    except Exception as exc:  # noqa: BLE001 -- an observer that can red its subject is a defect
        state.update(outcome=UNAVAILABLE, rc=None, reds=[], reason=str(exc)[:400])
    state["seconds"] = round(time.monotonic() - started, 1)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state, indent=2) + "\n")
    except OSError:
        pass
    return state


def load(path: Path | None = None) -> dict | None:
    try:
        return json.loads((path or OBSERVED_PATH).read_text())
    except (OSError, ValueError):
        return None


def doorbell_clause(state: dict | None = None, *, path: Path | None = None) -> str | None:
    """One line when the last post-publish reader run went red or could not run; else None.

    Silent only on a run that RAN and found nothing. No store at all is also silent: on a box that
    has never published since this landed there is nothing yet to report, and the publish path is
    what writes it."""
    state = load(path) if state is None else state
    if not state:
        return None
    sha = str(state.get("git_hash") or "?")[:9]
    when = str(state.get("checked_at") or "?")[:16]
    if state.get("outcome") != RAN:
        return ("POST-PUBLISH READERS did not run on publish {} ({}): {} -- the published book "
                "is UNGRADED, not green".format(sha, when, state.get("reason") or state.get("outcome")))
    reds = state.get("reds") or []
    if not reds:
        return None
    names = [re.sub(r"^(?:FAILED|ERROR) ", "", r).split(" - ", 1)[0] for r in reds[:3]]
    store = Path(path or OBSERVED_PATH)
    try:
        store = store.relative_to(PROJECT_DIR)
    except ValueError:
        pass
    return ("POST-PUBLISH READERS: {} red on publish {} ({}) -- {}{} (store {})".format(
        len(reds), sha, when, ", ".join(names), ", ..." if len(reds) > 3 else "", store))


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list", action="store_true", help="print the derived reader tests and exit")
    ap.add_argument("--run", action="store_true", help="run them now against this tree")
    args = ap.parse_args(argv)
    if args.list:
        print("\n".join(reader_tests() + list(PAGE_READERS)))
        return 0
    if args.run:
        # The CLI is never the supervisor's path; importing the publisher here is what lets the
        # supervisor's import of this module stay off it (see `run`).
        import importlib
        parse = importlib.import_module("background.process_run_complete")._parse_failed_node_ids
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(PROJECT_DIR),
                              capture_output=True, text=True).stdout.strip() or None
        state = run(head, parse)
        print(json.dumps({k: v for k, v in state.items() if k != "reds"}, indent=2))
        for r in state.get("reds") or []:
            print(r)
        return 1 if state.get("reds") or state.get("outcome") != RAN else 0
    print(doorbell_clause() or "post-publish readers: nothing to report")
    return 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/post_publish_readers.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("post_publish_readers")
    sys.exit(main())
