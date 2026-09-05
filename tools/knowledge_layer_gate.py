"""Domain understanding lands in the Knowledge layer. Machine findings go to the registers.

REUSE: tools/knowledge_layer_gate.py
CLASS: CUSTOM
INDEX: searched "knowledge", "market research", "domain understanding", "commit message gate",
       "trailer". Third sibling of `tools/write_time_gate.py` (a commit that ADDS a capability
       records what it reused) and `tools/next_step_gate.py` (a commit that ADVANCES an atom
       records what comes next). Same hook, same shape -- a required RECORD, never a required
       decision -- different question: a commit that establishes DOMAIN UNDERSTANDING records
       where a reader will find it. `background/finding_classes` is the other half of the
       director's rule and already exists; nothing here touches it.

WHY THIS EXISTS
---------------
Director console, 2026-09-05:

    "Make that the rule rather than an instruction each time: when a piece of work produces domain
     understanding, it lands in the Knowledge layer with its sources and its gaps stated. Findings
     about the machine go to the registers. Right now we have ten knowledge pages against six class
     registers and hundreds of findings, which is the wrong way round for a project whose value is
     the domain."

MEASURED THE SAME AFTERNOON, and it is worse than the count he used. Of 82 documents in
`docs/market_research/`, **four** are named anywhere in the Knowledge layer. Seventy-eight -- 95% --
have no reader-facing home at all. Over the last 300 commits, 84 new research documents were added
and 16 knowledge pages. The research is being produced roughly five times faster than it is
published, and nothing anywhere could notice, because a research document that reaches no reader
looks exactly like one that does: both are a committed file.

WHAT IS ENFORCED, AND WHAT DELIBERATELY IS NOT
----------------------------------------------
A commit that ADDS a document to `docs/market_research/` must have that document declare where its
understanding lands:

    **Knowledge:** <topic-id>        the page it feeds, live in the topic graph
    **Knowledge:** none -- <reason>  it feeds none, and why

THE DECLARATION LIVES IN THE DOCUMENT, NOT IN THE COMMIT MESSAGE, and that is the one design
choice here worth arguing. Its siblings use a message trailer because their subject IS the commit.
This subject is the DOCUMENT, which outlives its commit and is read on its own for months. A
trailer would answer the question for whoever reads `git log` and leave every future reader of the
file itself no better off -- and it is a future reader who has to decide whether the understanding
ever reached anyone. It also makes the backlog directly countable from the filesystem
(`--report`), with no store to drift.

ONLY ON ADD. Editing a research document does not re-ask the question: 45% of recent commits touch
this directory and a gate firing on all of them would teach every lane to type `none` reflexively,
which destroys the escape count as surely as removing it. That is the same reasoning
`next_step_gate` uses for leaving untrailered commits alone, and for the same reason.

FAILS OPEN, LOUDLY, on an unreadable topic graph -- the registry is not this gate's subject, and a
tree several lanes write at once must not wedge on a JSON parse error. It REFUSES only when the
graph reads fine and the declaration is missing or names a topic that does not exist, because both
of those are answerable by the person making the commit.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
# NO `sys.path` GUARD HERE, DELIBERATELY, AND THE ABSENCE IS THE POINT.
#
# Three modules this session shipped broken because the hook runs gates as SCRIPTS -- `sys.path[0]`
# is `tools/`, not the repo root -- so a `from tools import ...` raised and a fallback swallowed it:
# `next_step_gate` was dead in its hook, `generate_project_state` published a placeholder over a
# live figure, `project_portfolio_to_2026` wrote None onto all 145 accounts. The reflex after three
# is to paste the guard into every gate.
#
# This module imports nothing but the standard library, so the guard would protect nothing, and a
# guard that cannot fail is the exact shape catalogued this morning -- mutation testing proved it:
# removing it left every control green. So it is absent, and
# `test_the_gate_runs_THE_WAY_THE_HOOK_RUNS_IT` stands in its place as a TRIPWIRE rather than a
# proof: add a repo-internal import here without a guard and that control REDS.

RESEARCH_DIR = PROJECT / "docs" / "market_research"
GRAPH = PROJECT / "site" / "data" / "knowledge_wholesale.json"

#: `**Knowledge:** <topic-id>` or `**Knowledge:** none -- <reason>`, anywhere in the document's head.
_DECLARATION_RE = re.compile(r"^\s*\*\*Knowledge:\*\*\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
_NONE_RE = re.compile(r"^none\b\s*[-—:]{1,2}\s*(\S.*)$", re.IGNORECASE)
_HEAD_LINES = 20


class GraphUnavailable(RuntimeError):
    """The topic graph could not be read. Never raised for a missing declaration."""


def topic_ids() -> set[str]:
    try:
        data = json.loads(GRAPH.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise GraphUnavailable(f"cannot read {GRAPH.name}: {exc}") from exc
    ids = {t.get("id") for t in data.get("topics", []) if t.get("id")}
    if not ids:
        raise GraphUnavailable(f"{GRAPH.name} lists no topics")
    return ids


def declared_knowledge_of(text: str) -> str | None:
    """The document's own declaration, read from its HEAD only.

    Head-only on purpose: a research document quotes topic names in its body all the time, and a
    body-wide search would let a passing mention answer the question the header is supposed to.
    """
    head = "\n".join(text.splitlines()[:_HEAD_LINES])
    m = _DECLARATION_RE.search(head)
    return m.group(1) if m else None


def verdict(name: str, text: str, known: set[str]) -> tuple[bool, str]:
    """(passes, explanation). Pure, so the controls drive it without a repo or a commit."""
    declared = declared_knowledge_of(text)
    if declared is None:
        return False, (
            f"{name} is new domain research and does not say where its understanding lands.\n"
            "Add ONE line near the top:\n"
            "    **Knowledge:** <topic-id>        the page it feeds\n"
            "    **Knowledge:** none -- <reason>  it feeds none, and why\n"
            "Topic ids are in site/data/knowledge_wholesale.json. Research that reaches no reader "
            "is indistinguishable from research that does -- both are a committed file -- which is "
            "how 78 of 82 documents here ended up with no knowledge home."
        )
    if _NONE_RE.match(declared):
        return True, "declared none, with a reason"
    if declared in known:
        return True, f"declared `{declared}`"
    return False, (
        f"{name} declares `**Knowledge:** {declared}`, which is not a topic in "
        f"{GRAPH.name}.\nA declaration naming a page that does not exist is the same defect as no "
        "declaration: it still reaches no reader. Mint the topic first, or declare "
        "`none -- <reason>`."
    )


def staged_new_research(cwd: Path | None = None) -> list[str]:
    """Paths this commit ADDS under docs/market_research/. Adds only -- see the docstring."""
    done = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=A", "HEAD", "--",
         "docs/market_research"],
        cwd=str(cwd or PROJECT), capture_output=True, text=True, timeout=60,
    )
    if done.returncode != 0:
        return []
    return [ln for ln in done.stdout.splitlines() if ln.endswith(".md")]


def orphan_research() -> dict:
    """The standing backlog: research documents no Knowledge surface names.

    Derived from the filesystem every time, never stored -- a register of orphans would itself go
    stale, and the question "does any published page name this file" is cheap to re-ask.
    """
    blobs = []
    for rel in ("site/data/knowledge_topics.json", "site/data/knowledge_wholesale.json",
                "site/data/knowledge_price_cap.json"):
        p = PROJECT / rel
        if p.exists():
            blobs.append(p.read_text(encoding="utf-8", errors="replace"))
    for p in (PROJECT / "site" / "knowledge").glob("*/index.html"):
        blobs.append(p.read_text(encoding="utf-8", errors="replace"))
    published = "\n".join(blobs)

    docs = sorted(RESEARCH_DIR.glob("*.md"))
    orphans = [d.name for d in docs if d.stem not in published and d.name not in published]
    declared_none = 0
    for d in docs:
        if d.name not in orphans:
            continue
        got = declared_knowledge_of(d.read_text(encoding="utf-8", errors="replace"))
        if got and _NONE_RE.match(got):
            declared_none += 1
    return {"research": len(docs), "orphans": len(orphans),
            "declared_none": declared_none, "names": orphans}


def main(argv: list[str] | None = None) -> int:
    argv = list(argv if argv is not None else sys.argv[1:])

    if "--report" in argv:
        r = orphan_research()
        named = r["research"] - r["orphans"]
        print(f"[knowledge-gate] {r['research']} research documents; {named} named by a Knowledge "
              f"surface, {r['orphans']} with no home ({r['declared_none']} of those declare "
              f"`none` with a reason).")
        for n in r["names"][:15]:
            print(f"    {n}")
        if len(r["names"]) > 15:
            print(f"    ... and {len(r['names']) - 15} more")
        return 0

    new = staged_new_research()
    if not new:
        return 0
    try:
        known = topic_ids()
    except GraphUnavailable as exc:
        # FAILS OPEN, LOUDLY. The registry is not this gate's subject and a parse error in it must
        # not wedge a tree several lanes are writing.
        print(f"[knowledge-gate] topic graph unreadable, not blocking: {exc}", file=sys.stderr)
        return 0

    bad = []
    for rel in new:
        p = PROJECT / rel
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        ok, why = verdict(rel, text, known)
        if not ok:
            bad.append(why)
    if bad:
        print("[knowledge-gate] COMMIT REFUSED.\n" + "\n\n".join(bad), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
