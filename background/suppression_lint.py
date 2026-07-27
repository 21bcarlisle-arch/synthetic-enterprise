"""R10 SUPPRESSION SWEEP -- the registration-hole lint (DIRECTOR_RULING_SWEEP_VERDICT
2026-07-27, section 1: "Close the registration hole -- the sweep's own honest gap").

WHY THIS EXISTS
---------------
`suppression_register.py` enforces the standing consequence on every *registered*
suppression (each must declare `what_still_pages` + its re-arm). But its own SCOPE-HONESTY
note names the hole: *registering* a newly-written suppression remained a **convention**.
That is the identical shape as every failure of the sweep week -- a sound mechanism with an
optional path into it. This lint closes that path: it discovers suppression-shaped code in
`background/**` and FAILS when such code is not accounted for by the register (or by an
explicit, reasoned `not-a-suppression` waiver).

THE FAILURE DIRECTION IS NOISE, BY DESIGN (LAW A, director-verbatim)
-------------------------------------------------------------------
*"It will produce false positives, and that is correct."* A developer who trips the lint
must either (a) register the mechanism -- with its `what_still_pages` and re-arm -- or
(b) state, at the code site, why it is not a suppression. Either outcome is the goal.
**Do not tune this lint toward quiet to reduce its noise; add register entries or reasoned
waivers instead.** A silence-biased mechanism that names no pager is exactly what LAW A
forbids, so the safe direction here is to REFUSE the un-accounted-for site (fail-closed
toward a page), never to wave it through.

FAIL-CLOSED / R15 (an unavailable check is a FAILED check)
----------------------------------------------------------
A background source file that cannot be tokenised, or a register that cannot be loaded, is a
VIOLATION -- never a silent pass. Both ways are mutation-proven in
`tests/background/test_suppression_lint.py`: an unregistered suppression added in a fixture
FAILS the gate; the live tree (every site registered or reasoned-waived) PASSES; removing a
load-bearing `code_markers` token re-reds the site it covered.

SCOPE HONESTY (R9), same discipline as the register module
----------------------------------------------------------
"Suppression-shaped" is detected by MARKER TOKENS in *code positions only* -- identifier
(`NAME`) tokens, never comments or string literals, so prose *about* suppression never trips
it. The marker vocabulary (cooldown / throttle / suppress / silence / fold / quiet /
proven_rest / nothing_to_do) is the director's own list from the ruling. This catches the
named shapes; it does not claim to catch every conceivable early-return-on-a-gate-path (a
purely structural detector is a separate, larger job). What it DOES guarantee: no code
carrying one of those marker tokens can live in `background/**` un-accounted-for. The
partial-ness is named here rather than dressed up as total.

ACCOUNTING -- two explicit, greppable sources (never a heuristic quiet-list):
  1. REGISTER `code_markers`: a registered suppression lists the exact identifier tokens it
     owns; every such token must also actually EXIST in the tree (no dead pointer at deleted
     code -- register/code drift is itself a violation).
  2. IN-FILE WAIVER: `# suppression-lint: not-a-suppression <token> -- <reason>` (reason
     required, non-empty). Declares that <token> in THIS file is a false positive and says
     why (a functional `fold`/reduce, a `contextlib.suppress`, a var that RAISES on silence).
"""
from __future__ import annotations

import io
import re
import tokenize
from pathlib import Path
from typing import Any

from background.suppression_register import load_register

PROJECT_DIR = Path(__file__).resolve().parent.parent
BACKGROUND_DIR = PROJECT_DIR / "background"

# The director's marker vocabulary (ruling section 1), matched as a substring of an
# identifier NAME token. NOTE: matched ONLY against `tokenize.NAME` tokens -- never comments
# or string literals -- so a docstring discussing suppression does not trip the lint.
_MARKER_RE = re.compile(
    r"(cooldown|throttle|suppress|silence|_fold|fold_|_quiet|quiet_|proven_rest|nothing_to_do)",
    re.IGNORECASE,
)

# `# suppression-lint: not-a-suppression <token> -- <reason>`  (reason required).
_WAIVER_RE = re.compile(
    r"#\s*suppression-lint:\s*not-a-suppression\s+(?P<token>\S+)\s*--\s*(?P<reason>.+?)\s*$"
)

# Files that legitimately contain the marker vocabulary as their SUBJECT, not as live
# suppressions -- the register/gate/lint machinery itself. Excluded from the scan (they would
# otherwise self-flag on their own variable names, e.g. `_MARKER_RE`, `validate_suppression_*`).
_EXCLUDED_NAMES = {"suppression_register.py", "suppression_lint.py"}


def _iter_background_files(root: Path | None = None):
    base = root or BACKGROUND_DIR
    for p in sorted(base.rglob("*.py")):
        if "__pycache__" in p.parts:
            continue
        if p.name in _EXCLUDED_NAMES:
            continue
        yield p


def _scan_file(path: Path) -> tuple[list[tuple[int, str]], set[str], list[str]]:
    """Return (sites, waived_tokens, errors) for one file.

    sites          -- [(lineno, identifier)] for every NAME token matching a marker.
    waived_tokens  -- {token} explicitly waived in-file with a non-empty reason.
    errors         -- fatal tokenise/read errors (an un-tokenisable file is a FAILED check).
    """
    sites: list[tuple[int, str]] = []
    waived: set[str] = set()
    errors: list[str] = []
    try:
        src = path.read_bytes()
    except OSError as exc:
        return [], set(), [f"{path}: unreadable ({exc})"]
    # Waivers live in COMMENT tokens; sites live in NAME tokens. One tokenise pass gets both.
    try:
        for tok in tokenize.tokenize(io.BytesIO(src).readline):
            if tok.type == tokenize.NAME and _MARKER_RE.search(tok.string):
                sites.append((tok.start[0], tok.string))
            elif tok.type == tokenize.COMMENT:
                m = _WAIVER_RE.search(tok.string)
                if m and m.group("reason").strip():
                    waived.add(m.group("token"))
    except (tokenize.TokenError, IndentationError, SyntaxError) as exc:
        errors.append(f"{path}: could not tokenise -- an unscannable file is a FAILED check ({exc})")
    return sites, waived, errors


def _registered_markers(register: dict[str, Any]) -> set[str]:
    markers: set[str] = set()
    for e in register.get("entries", []):
        cm = e.get("code_markers")
        if isinstance(cm, list):
            markers.update(str(t) for t in cm)
    return markers


def lint_suppression_registration(root: Path | None = None,
                                  register: dict[str, Any] | None = None) -> list[str]:
    """Return a list of violation strings (EMPTY == the gate passes).

    A suppression-shaped site (a marker-bearing identifier in code) is a VIOLATION unless it
    is accounted for by a register `code_markers` token OR an in-file `not-a-suppression`
    waiver. Additionally, every `code_markers` token the register declares must actually
    appear in the tree (a dead pointer is register/code drift). Fail-closed: an unscannable
    file or an unloadable register is itself a violation, never a silent pass.
    """
    reg = register if register is not None else load_register()
    registered = _registered_markers(reg)
    base = root or BACKGROUND_DIR

    violations: list[str] = []

    # (1) SITE COVERAGE -- over the scanned root (tests override `root` with a fixture tree).
    for path in _iter_background_files(base):
        rel = path.relative_to(base)
        sites, waived, errors = _scan_file(path)
        violations.extend(errors)
        for lineno, token in sites:
            if token in registered:
                continue
            if token in waived:
                continue
            violations.append(
                f"{rel}:{lineno}: suppression-shaped identifier {token!r} is neither in the "
                f"register's `code_markers` nor waived (`# suppression-lint: not-a-suppression "
                f"{token} -- <reason>`). Register the mechanism with its `what_still_pages` "
                f"+ re-arm, or state why it is not a suppression -- do not tune the lint quiet."
            )

    # (2) REGISTER -> CODE INTEGRITY -- a declared code_marker that matches no live identifier
    # is a dead pointer at deleted/renamed code. This is about register <-> REAL-code drift, so
    # it always checks the real BACKGROUND_DIR, independent of the (test-overridable) site root.
    real_tokens: set[str] = set()
    for path in _iter_background_files(BACKGROUND_DIR):
        for _lineno, token in _scan_file(path)[0]:
            real_tokens.add(token)
    for token in sorted(registered):
        if token not in real_tokens:
            violations.append(
                f"register: `code_markers` token {token!r} matches no suppression-shaped "
                f"identifier in background/** -- dead register/code pointer (the code it named "
                f"was deleted or renamed; update the register)."
            )
    return violations


def registration_is_clean(root: Path | None = None) -> bool:
    """True iff every suppression-shaped site in `background/**` is registered or reasoned-waived,
    and every declared `code_markers` token still exists. Raises (never silently True) if the
    register itself is unavailable."""
    return not lint_suppression_registration(root=root)
