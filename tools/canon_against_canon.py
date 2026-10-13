"""Canon against canon: the standing pages say what canon says, in canon's words.

Canon v4 alignment steer, step 6a (director, 2026-10-12). Beside `tools/canon_drift_check.py`, which
holds canon against the code, this holds the standing pages against canon itself. Three conditions
fail it:
  1. MISQUOTED  -- a quoted line, on a line that cites a canon id, that is not verbatim in
                   docs/design/DIRECTOR_CANON.md ("A second wording of a canon line is the defect");
  2. NO SUCH ID -- a cited canon id that canon does not define;
  3. SUPERSEDED -- a phrase canon §16 marks superseded, presented on a standing page with no word
                   saying it is retired.
It is read in the Monday step (background/weekly_rhythm.py) and reports; `--check` exits 1 on any.

REUSE: tools/canon_against_canon.py
CLASS: CUSTOM
INDEX: searched "canon", "verbatim", "quote" -- tools/canon_drift_check.py holds canon CLAIMS
       against CODE through docs/design/canon_claims.yaml; nothing compares the standing pages'
       wording with the canon text.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANON = ROOT / "docs" / "design" / "DIRECTOR_CANON.md"
STANDING_PAGES = ("CLAUDE.md", "docs/design/THE_MODEL_ON_A_PAGE.md", "docs/PROJECT_OVERVIEW.md",
                  "docs/operations/OPERATING_MODEL.md")
_FAMILIES = r"(?:CO|M|V|W|F|K|P|C|X|G|D|H|R|O)"
#: An EXPLICIT citation: "canon X1" / "canon v4 X1". Only these can fail NO SUCH ID, because the atom
#: ids of the maturity map (C34, D48, H45 ...) share canon's letter families and appear bare.
_EXPLICIT = re.compile(r"\bcanon(?: v4)?\s+(" + _FAMILIES + r"\d{1,2})\b")
#: Any form that ATTRIBUTES nearby words to canon, counted only when the id is one canon defines.
_ATTRIB = re.compile(r"(?:\bcanon(?: v4)?\s+|\*\*|\()(" + _FAMILIES + r"\d{1,2})\b")
_QUOTE = re.compile(r"[\"“]([^\"”]{25,}?)[\"”]")
_RETIRED_WORDS = ("supersed", "retire", "replaced", "corrected", "was ", "→", "no longer", "void")
#: How far a quote may sit from the canon id it is attributed to: the same paragraph line, or the
#: line either side (a quote wrapped across the page's own line breaks).
_NEAR = 1


def _norm(text: str) -> str:
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    text = text.replace("**", "").replace("`", "")
    return " ".join(text.split())


def canon_ids(canon_text: str) -> set[str]:
    return set(re.findall(r"^\*\*(" + _FAMILIES + r"\d{1,2})\. ", canon_text, re.M)) | set(
        re.findall(r"^- \*\*(R\d{1,2})\*\*", canon_text, re.M))


def superseded_phrases(canon_text: str) -> list[str]:
    """The quoted phrase that opens each §16 chain: the first wording, which a later one replaced."""
    try:
        section = canon_text[canon_text.index("## 16."):]
        section = section[:section.index("\n## ", 5)] if "\n## " in section[5:] else section
    except ValueError:
        return []
    out = []
    for line in section.splitlines():
        if "→" not in line:
            continue
        head = line.split("→", 1)[0]
        out += [q.strip() for q in _QUOTE.findall(head)]
    return out


def problems(root: Path = ROOT, pages=STANDING_PAGES) -> list[str]:
    return scan(root, pages)[0]


def scan(root: Path = ROOT, pages=STANDING_PAGES) -> tuple[list[str], int]:
    """(problems, attributed quotes compared). The count is the denominator: 0 problems over 0
    quotes compared is not a clean bill of health."""
    canon_text = (root / "docs" / "design" / "DIRECTOR_CANON.md").read_text(encoding="utf-8")
    ids, flat = canon_ids(canon_text), _norm(canon_text)
    if not ids:
        return ["canon defines no ids, so nothing can be checked against it (fail-closed)"], 0
    retired = superseded_phrases(canon_text)
    out, checked = [], 0
    for rel in pages:
        path = root / rel
        if not path.is_file():
            out.append(f"{rel}: the standing page is missing")
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        for n, line in enumerate(lines, 1):
            for cid in _EXPLICIT.findall(line):
                if cid not in ids:
                    out.append(f"{rel}:{n}: NO SUCH ID -- {cid} is cited and canon defines no {cid}")
            near = " ".join(lines[max(0, n - 1 - _NEAR):n + _NEAR])
            if any(cid in ids for cid in _ATTRIB.findall(near)) and (
                    re.search(r"\bcanon\b", near, re.I) or rel == "CLAUDE.md"
                    or rel.endswith("OPERATING_MODEL.md")):
                for q in _QUOTE.findall(line):
                    checked += 1
                    if _norm(q) not in flat:
                        out.append(f"{rel}:{n}: MISQUOTED -- \"{q[:70]}\" is attributed to canon "
                                   "and is not verbatim in DIRECTOR_CANON.md")
            low = line.lower()
            for phrase in retired:
                if _norm(phrase).lower() in _norm(line).lower() and not any(
                        w in low for w in _RETIRED_WORDS):
                    out.append(f"{rel}:{n}: SUPERSEDED -- \"{phrase[:60]}\" is presented as current; "
                               "canon §16 retires it")
    return out, checked


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="exit 1 on any problem")
    args = ap.parse_args(argv)
    found, checked = scan()
    for line in found:
        print(line)
    print(f"canon against canon: {len(found)} problem(s); {checked} attributed quote(s) compared "
          f"across {len(STANDING_PAGES)} standing page(s)")
    return 1 if ((found or not checked) and args.check) else 0


if __name__ == "__main__":
    sys.exit(main())
