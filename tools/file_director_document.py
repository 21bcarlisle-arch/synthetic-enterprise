"""Add the machine's bookkeeping to a director document, so it is never the director's.

REUSE: tools/file_director_document.py
CLASS: CUSTOM
INDEX: searched "director document", "canon", "severity header", "knowledge declaration", "filer".
       `background/finding_severity.py` owns the severity vocabulary and the refusal, and is
       imported rather than restated -- this is the repair beside that check, not a second opinion
       about what a severity is. `tools/knowledge_layer_gate.py` owns the Knowledge declaration and
       its regex, likewise imported. `tools/staging_migrate_rooms.py` moves documents between rooms
       and decides nothing about their content.

WHY THIS EXISTS
---------------
Two gates refuse a document that lacks a header, and both are right to:

  * an UNCLASSIFIED staging document refuses a level raise in EVERY lane, because its severity could
    be BLOCKING and its lane is unknown, so it cannot show any lane clear;
  * a research document that declares no Knowledge topic is understanding that reaches no reader.

**Neither is something the director has any reason to know about.** He writes a canon in his own
editor and lands it; the machine then silently blocks every lane until a seat happens to attempt a
merge and reads the refusal. That happened FOUR TIMES in two days with the severity header, and the
Knowledge declaration was missing from 51 canon and ruling documents when the gate was finally
pointed at them.

Transcribing it by hand a fifth time is not a fix, it is the same act repeated. **The header is a
machine requirement, so the machine adds it.**

WHAT IS DERIVED AND WHAT IS REFUSED
------------------------------------
**Severity is DERIVED, never chosen.** A director document states its own severity in the `Type:`
block -- *"Severity: LATENT"* -- and that sentence is the director's. This reads it. If the document
does not state one, this REFUSES rather than defaulting: `finding_severity`'s own docstring says
defaulting to LATENT is the anti-pattern of deciding one's own finding is not blocking, and a filer
that quietly picked a severity would be doing exactly that on his behalf.

**Lane is derived from the document's own subject where it can be, and refused where it cannot.**
A guess here would attribute a director's instruction to the wrong lane, which is worse than an
absent header because it looks answered.

**The Knowledge declaration is never invented.** A topic id that does not exist in the graph would
satisfy the gate and reach no reader -- the exact failure the gate exists to catch. Absent an
explicit topic this writes `none -- <reason>`, which is the gate's own honest form.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

#: The director states his own severity inside the `Type:` block. Read, never chosen.
_SEVERITY_IN_TYPE = re.compile(r"Severity:\s*(BLOCKING|LATENT|RECORDED)\b", re.IGNORECASE)

#: Lane from the document's own subject. Deliberately SMALL and deliberately incomplete: a filer
#: that can name a lane for everything is a filer that guesses, and a wrong lane on a director's
#: instruction looks answered while pointing the machine at the wrong work.
_LANE_HINTS = (
    ("W2_customer_generator", ("household", "demand vector", "synthetic book", "premise",
                               "occupancy", "housing", "people")),
    ("W1_market_weather", ("weather", "cell", "temperature", "wind", "irradian")),
    ("D_billing_metering", ("billing", "meter", "read", "tariff", "payment")),
    ("H_harness", ("harness", "gate", "control", "staging", "console")),
)

_HEADER_RE = re.compile(r"^\s*\*\*Severity:\*\*", re.MULTILINE)


class CannotFile(RuntimeError):
    """The document does not say enough about itself to be filed, and guessing is worse."""


def severity_of(text: str) -> str:
    match = _SEVERITY_IN_TYPE.search(text)
    if not match:
        raise CannotFile(
            "the document states no severity in its Type block, and this will not choose one. "
            "`background/finding_severity` names defaulting to LATENT as the anti-pattern of "
            "deciding one's own finding is not blocking -- doing it on the director's behalf is "
            "the same act with his name on it.")
    return match.group(1).upper()


def lane_of(text: str) -> str:
    lowered = text.lower()
    scored = [(sum(lowered.count(word) for word in words), lane) for lane, words in _LANE_HINTS]
    best, lane = max(scored)
    if best == 0:
        raise CannotFile(
            "no lane can be read from the document's subject. A guess here attributes a director's "
            "instruction to the wrong lane, which looks answered and is not -- pass --lane.")
    return lane


def file_document(path: Path, *, lane: str | None = None, knowledge: str | None = None,
                  atom: str = "`unminted`", epoch: int = 3) -> str:
    """Return the document with its header and Knowledge declaration present. Idempotent."""
    from tools.knowledge_layer_gate import declared_knowledge_of

    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    head = text.split("\n## ")[0]

    if not _HEADER_RE.search(head):
        severity = severity_of(text)
        resolved = lane or lane_of(text)
        header = (f"**Severity:** {severity} · **Lane:** {resolved} · **Epoch:** {epoch} · "
                  f"**Atom:** {atom}")
        at = 1 if lines and lines[0].startswith("# ") else 0
        lines.insert(at, "")
        lines.insert(at + 1, header)
        text = "\n".join(lines)

    if not declared_knowledge_of(text.split("\n## ")[0]):
        declaration = f"**Knowledge:** {knowledge}" if knowledge else (
            "**Knowledge:** none -- no topic declared at filing; the seat that acts on this "
            "document names the page its understanding reaches, or says why none")
        lines = text.split("\n")
        at = next(i for i, ln in enumerate(lines) if ln.startswith("**Severity:**"))
        lines.insert(at + 1, "")
        lines.insert(at + 2, declaration)
        text = "\n".join(lines)
    return text


def unfiled(root: Path | None = None) -> list[Path]:
    """Director documents on disk missing either piece of bookkeeping."""
    from tools.knowledge_layer_gate import CANON_PREFIXES, declared_knowledge_of

    staging = (root or PROJECT) / "docs" / "staging"
    out = []
    for directory in (staging, staging / "done", staging / "records", staging / "console"):
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.md")):
            if not path.name.startswith(CANON_PREFIXES):
                continue
            head = path.read_text(encoding="utf-8", errors="replace").split("\n## ")[0]
            if not _HEADER_RE.search(head) or not declared_knowledge_of(head):
                out.append(path)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path", nargs="?", help="the document to file")
    ap.add_argument("--lane", help="override the derived lane")
    ap.add_argument("--knowledge", help="topic id, or 'none -- reason'")
    ap.add_argument("--write", action="store_true", help="write the file back")
    ap.add_argument("--list", action="store_true", help="director documents missing bookkeeping")
    args = ap.parse_args(argv)

    if args.list:
        missing = unfiled()
        print(f"{len(missing)} director document(s) missing a header or a Knowledge declaration")
        for p in missing[:40]:
            print("  -", p.relative_to(PROJECT))
        return 0
    if not args.path:
        ap.print_help(sys.stderr)
        return 2
    path = Path(args.path)
    try:
        filed = file_document(path, lane=args.lane, knowledge=args.knowledge)
    except CannotFile as exc:
        print(f"REFUSED: {exc}")
        return 1
    if args.write:
        path.write_text(filed, encoding="utf-8")
        print(f"filed {path}")
    else:
        print(filed.split("\n## ")[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
