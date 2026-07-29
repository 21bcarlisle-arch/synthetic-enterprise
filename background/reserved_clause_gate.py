"""Reserved-clause gate -- exit-criterion §4 of PLANNER_MINTED_reversible_draws_dont_
queue_for_permission (source ruling DIRECTOR_RULING_WORK_AT_RISK_DEFAULT_2026-07-29.md).

WHY THIS EXISTS (OPERATIONAL_COHERENCE -- purpose/guarantee/why first):
The 2026-07-29 ruling names the failure mode directly (§2, the "ratchet"): a governance
system accretes *reserved clauses* -- "returns for ratification", "queues for permission",
"requires director approval" -- one reasonable clause at a time, until the machine must ask
permission to move. Ruling §4 (verbatim): "No new reserved clause may be staged without
justifying it against the §2 test in the same document. If the advisor writes 'returns for
ratification' and cannot say why the act is irreversible, the clause is invalid and the
machine should say so rather than obey it."

WHAT THIS GUARANTEES: a staged reserved clause is VALID only if the same paragraph carries an
explicit §2 (irreversibility) justification -- a machine-readable `[§2: <reason>]` tag or a
recognised irreversibility phrase. A reserved clause with NO justification is reported as a
violation. It does NOT block (report-only: it cannot jam the publishing pipeline -- see the
"control false-positive jams pipeline" hazard); its consumer is a human/digest reading the
report and either justifying the clause or dropping it.

WHY NOT classify_action AS THE ORACLE: classify_action's door LIST is narrow keyword-pattern
matching over a short action description. On free prose it FAILS to recognise legitimate doors
-- e.g. "changing the egress allowlist requires director approval" and "editing a safety
control returns to the director" both classify as NOT-a-door (verified 2026-07-29). Using it as
the §2 oracle here would falsely reject legitimate reserved clauses (fail-noisy). The oracle is
therefore a machine-readable justification the clause author writes, not an inference over prose.

REVERSAL: git revert; report-only, no external state, no live gate touched.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Reserved-clause TRIGGER phrasings -- a clause that reserves an act to the director / makes it
# queue for permission. Case-insensitive. Deliberately conservative (a false miss is safe; the
# gate is report-only and a real omission surfaces on the next authored clause).
_RESERVED_CLAUSE_PATTERNS: tuple[str, ...] = (
    r"returns?\s+(?:to\s+the\s+director\s+)?for\s+ratification",
    r"queues?\s+for\s+permission",
    r"requires?\s+director\s+(?:approval|ratification|sign-?off|consent)",
    r"reserved\s+(?:for|to)\s+the\s+director",
    r"must\s+(?:ask|await)\s+(?:the\s+)?director",
    r"director[-\s]reserved",
)

# §2 JUSTIFICATION markers -- what makes a reserved clause VALID. Either the explicit machine-
# readable tag `[§2: ...]` (`[S2: ...]` ASCII fallback) or a recognised irreversibility phrase.
_JUSTIFICATION_PATTERNS: tuple[str, ...] = (
    r"\[\s*(?:§2|s2)\s*:",
    r"one-way\s+door",
    r"provably\s+irreversible",
    r"irreversible\s+because",
    r"cannot\s+be\s+(?:reversed|undone|retracted)",
    r"no\s+reversible\s+form",
)

_RESERVED_RE = re.compile("|".join(_RESERVED_CLAUSE_PATTERNS), re.IGNORECASE)
_JUSTIFY_RE = re.compile("|".join(_JUSTIFICATION_PATTERNS), re.IGNORECASE)

# NEGATION guard: a clause DENIED ("does not queue for permission", "never returns for
# ratification") is DISCUSSING the mechanism, not staging a reserved clause -- don't flag it.
# This is a cheap local heuristic, not full context-awareness (that robustness is the proper-
# design follow-on noted in the atom's FRAME); it kills the obvious false positives only.
_NEGATION_RE = re.compile(r"(?:\bnot\b|n't\b|\bnever\b|\bno\b|\bwithout\b)[^.\n]{0,30}$", re.IGNORECASE)


def has_section2_justification(paragraph: str) -> bool:
    """True iff the paragraph carries a §2 (irreversibility) justification marker.
    This is the INDEPENDENT oracle -- author-written, not inferred from the clause text."""
    return bool(_JUSTIFY_RE.search(paragraph or ""))


def _paragraphs_with_lines(text: str) -> list[tuple[int, str]]:
    """Split into blank-line-separated paragraphs, each tagged with the 1-based line number
    of its first line, so a violation can point the author at the clause."""
    paras: list[tuple[int, str]] = []
    cur: list[str] = []
    start = 1
    for i, line in enumerate(text.splitlines(), start=1):
        if line.strip() == "":
            if cur:
                paras.append((start, "\n".join(cur)))
                cur = []
        else:
            if not cur:
                start = i
            cur.append(line)
    if cur:
        paras.append((start, "\n".join(cur)))
    return paras


def scan_reserved_clauses(text: str | None) -> list[dict]:
    """Return a list of violations: reserved clauses staged WITHOUT a §2 justification in the
    same paragraph. Each violation: {line, clause, paragraph_excerpt}.

    FAIL-SAFE: empty/None/non-str text -> [] (never crashes a caller). Report-only -- the
    return value is data for a human/digest, never a block."""
    if not text or not isinstance(text, str):
        return []
    violations: list[dict] = []
    for start_line, para in _paragraphs_with_lines(text):
        if has_section2_justification(para):
            continue
        for m in _RESERVED_RE.finditer(para):
            # skip a DENIED clause ("does not queue for permission") -- discussion, not a clause
            if _NEGATION_RE.search(para[: m.start()]):
                continue
            offset = para[: m.start()].count("\n")
            clause_line = para.splitlines()[offset].strip()
            violations.append(
                {
                    "line": start_line + offset,
                    "clause": m.group(0),
                    "paragraph_excerpt": clause_line[:200],
                }
            )
            break  # one violation per paragraph is enough to prompt the author
    return violations


def scan_path(path: str | Path) -> list[dict]:
    """Scan a single staged doc; violations carry the file path. Fail-safe on unreadable file."""
    p = Path(path)
    try:
        text = p.read_text(encoding="utf-8")
    except OSError:
        return []
    out = scan_reserved_clauses(text)
    for v in out:
        v["file"] = str(p)
    return out


def scan_staging(staging_dir: str | Path = "docs/staging") -> list[dict]:
    """CONSUMER (report-only): scan every staged .md for unjustified reserved clauses."""
    d = Path(staging_dir)
    out: list[dict] = []
    try:
        files = sorted(d.rglob("*.md"))
    except OSError:
        return []
    for f in files:
        # skip archived/actioned lanes -- the gate is about clauses being NEWLY staged
        if any(part in {"done", "fyi", "drafts"} for part in f.parts):
            continue
        out.extend(scan_path(f))
    return out


if __name__ == "__main__":  # pragma: no cover - human/digest consumer
    target = sys.argv[1] if len(sys.argv) > 1 else "docs/staging"
    findings = scan_path(target) if Path(target).is_file() else scan_staging(target)
    if not findings:
        print("reserved_clause_gate: no unjustified reserved clauses found")
    else:
        print(f"reserved_clause_gate: {len(findings)} unjustified reserved clause(s) "
              "(ruling §4 -- justify against the §2 test or drop):")
        for v in findings:
            loc = f"{v.get('file', '?')}:{v['line']}"
            print(f"  {loc}  {v['clause']!r}  -- {v['paragraph_excerpt']}")
