"""Every panel on the wall exhibit must declare which side of the epistemic wall it is on.

WHY THIS EXISTS, and why it is a module and not three asserts in a test file.

`site/explore/index.html` is the two-sided-wall exhibit (atom `SITE2_two_sided_wall_exhibit`,
minted from Part 2 of DIRECTOR_RULING_THE_PORTAL_IS_A_WALL_EXHIBIT_2026-08-12). It renders three
kinds of figure at once, on purpose:

  customer  what a real account holder holds -- bills, meter reads, their own consumption
  company   what a real supplier knows and does not show them -- cost to serve, lifetime net
  sim       what NOTHING outside a simulation can see -- the household's real churn disposition

The director's ruling keeps all three and makes the layering the exhibit. Its non-negotiable is
the reason for this file, quoted: *"a control that cannot fail is not a control"*. The exhibit
already carried beautiful prose about which side each panel was on. Prose is not a control: it
cannot fail when someone adds a twentieth panel, and it did not fail when `03dd8c49e` retired
`site/customers/index.html` and deleted `test_wall_exhibit.py` (4,828 lines) along with it,
leaving the atom's `file_scope` re-homed to `site/explore/` with no side-declaration mechanism at
all. This module is the mechanism, restored on the page the content moved to.

R15 SHAPE. Every check is a pure function from HTML TEXT to a list of violations, so
`tests/tools/test_explore_wall_sides.py` can feed each one a MUTATED copy of the real page and
prove the check fires -- rather than asserting the live page is clean, which any fail-open
checker also does. The three killer patterns, and how each is refused here:

  TAUTOLOGY    the vocabulary and the named figures are written here, independent of the page.
               A check derived from "whatever sides the page happens to use" would pass for any
               page, including one that declares `side="whatever"`.
  FAIL-OPEN    `parse_panels` returning nothing is a VIOLATION, not a pass (`check_page`), so a
               refactor that renames the helper reds the gate instead of silently checking zero
               panels. Same for an unreadable/missing file.
  FAIL-SILENT  wired into `SITE_SURFACE_TESTS` in tools/pre_commit_test_gate.py, which triggers
               on the `site/` prefix whole-tree. Selecting it per-file would fire when THIS
               module is edited and stay silent on the commit that adds an undeclared panel --
               the exact selection-layer defect the gate's own STORE_CONTRACT_TESTS note records.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXHIBIT = REPO_ROOT / "site" / "explore" / "index.html"

# The wall has exactly three vantages. A figure that cannot be attributed to one of them has no
# business on a page whose whole subject is who can see what.
SIDES = ("customer", "company", "sim")

# The figures the ruling names BY NAME, as they appear in the page source. Exit criterion 3 asks
# for these instances specifically rather than for a general principle, because a general
# principle is what the prose already said.
#
# SIM-only: visible only because the world is synthetic. `sim_truth` is the household's real
# probability of leaving; `journey_state` is its private disposition; satisfaction and the
# wholesale trading margin are named by the ruling and must stay off the page's company side if
# they ever return to it.
SIM_ONLY_FIGURES = (
    "sim_truth",
    "journey_state",
    "satisfaction_score",
    "wholesale_trading_margin",
)
# Company-only: a real supplier holds these and does not put them in front of the household.
COMPANY_ONLY_FIGURES = (
    "cost_to_serve_gbp",
    "lifetime_net_after_cts_gbp",
    "churn_probability",
    "clv_gbp",
    "forecast_profit_gbp",
    "pricing_action",
    "avg_hedge_fraction",
)


def _strip_comments(src: str) -> str:
    """Blank out JS block/line comments, preserving offsets and newlines.

    Offsets are preserved so a violation can still be reported at a real line number, and so a
    comment that merely MENTIONS a figure name (this file's own prose does) never counts as that
    figure being rendered.
    """
    out = list(src)
    i, n = 0, len(src)
    in_s: str | None = None
    while i < n:
        ch = src[i]
        if in_s:
            if ch == "\\":
                i += 2
                continue
            if ch == in_s:
                in_s = None
            i += 1
            continue
        if ch in "\"'":
            in_s = ch
            i += 1
            continue
        if src.startswith("/*", i):
            j = src.find("*/", i + 2)
            j = n if j == -1 else j + 2
            for k in range(i, j):
                if out[k] != "\n":
                    out[k] = " "
            i = j
            continue
        if src.startswith("//", i):
            j = src.find("\n", i)
            j = n if j == -1 else j
            for k in range(i, j):
                out[k] = " "
            i = j
            continue
        i += 1
    return "".join(out)


def _match_paren(src: str, open_idx: int) -> int:
    """Index just past the ')' closing the '(' at `open_idx`, quote-aware. -1 if unbalanced."""
    depth = 0
    i, n = open_idx, len(src)
    in_s: str | None = None
    while i < n:
        ch = src[i]
        if in_s:
            if ch == "\\":
                i += 2
                continue
            if ch == in_s:
                in_s = None
            i += 1
            continue
        if ch in "\"'":
            in_s = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return -1


def _blank_strings(src: str) -> str:
    """Blank the CONTENTS of string literals, preserving offsets, quotes and newlines.

    Used only to LOCATE calls. Without it the helper's own error message -- the string
    "panel() needs a wall side" -- parses as a call site with no literal side, which is a
    false positive of exactly the kind that trains a reader to ignore the checker.
    """
    out = list(src)
    i, n = 0, len(src)
    in_s: str | None = None
    while i < n:
        ch = src[i]
        if in_s:
            if ch == "\\":
                i += 2
                continue
            if ch == in_s:
                in_s = None
            elif ch != "\n":
                out[i] = " "
            i += 1
            continue
        if ch in "\"'":
            in_s = ch
        i += 1
    return "".join(out)


# Calls only: never the `function panel(...)` declaration, never `x.panel(`, never a mention
# inside a string (blanked above).
_CALL = re.compile(r"(?<![\w.])(?<!function )panel\s*\(")


_IDENT = re.compile(r"(?<![\w.$])([A-Za-z_$][\w$]*)")


_VAR_DECL = re.compile(r"(?<![\w.$])var\s+([A-Za-z_$][\w$]*)\s*=")


def _var_table(src: str, locator: str) -> dict[str, str]:
    """Every `var <name> = ...;` in the script, name -> definition text.

    Built ONCE per page rather than re-searched per identifier: the naive form re-scanned the
    whole source for each of ~900 identifiers across 23 panels and took 16s, which is not a
    per-commit control -- a gate slow enough to be worth skipping gets skipped. Definitions
    terminate on the first `;` at bracket depth 0, so a body containing a function
    (`var beliefRows = outcomes.map(function (e) { ... });`) is captured whole.
    """
    table: dict[str, str] = {}
    n = len(locator)
    for m in _VAR_DECL.finditer(locator):
        i, depth = m.end(), 0
        while i < n:
            ch = locator[i]
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                if depth == 0:
                    break
                depth -= 1
            elif ch == ";" and depth == 0:
                break
            i += 1
        # First declaration wins; a name redeclared in two stage functions is expanded to both
        # only if they differ, which would over- rather than under-report.
        prev = table.get(m.group(1), "")
        body = src[m.end() : i]
        table[m.group(1)] = body if not prev else (prev + "\n" + body)
    return table


def _expand_references(table: dict[str, str], text: str, depth: int = 2) -> str:
    """Panel text plus the definitions of the locals it interpolates.

    WHY THIS IS NOT OPTIONAL, and it was found by this module's own mutation test rather than
    reasoned out in advance: the belief-against-truth panel does not mention `sim_truth` in its
    own call text at all. The truth column is built into `beliefRows` a dozen lines above and
    interpolated in. A checker reading only the call text pronounced that panel clean while it
    printed the household's real churn probability -- FAIL-OPEN, in the one place on the page it
    would matter most. Two levels is enough for this page and errs toward a wrongly-RED control,
    which is the safe direction for a control to be wrong in.
    """
    seen: set[str] = set()
    out = [text]
    frontier = [text]
    for _ in range(depth):
        nxt = []
        for chunk in frontier:
            for name in set(_IDENT.findall(chunk)):
                if name in seen:
                    continue
                seen.add(name)
                body = table.get(name, "")
                if body:
                    out.append(body)
                    nxt.append(body)
        frontier = nxt
        if not frontier:
            break
    return "\n".join(out)


def parse_panels(html: str) -> list[dict]:
    """Every `panel(...)` call: its declared side, source line, and full call text.

    `text` is the call PLUS the locals it interpolates -- see `_expand_references`.
    """
    src = _strip_comments(html)
    locator = _blank_strings(src)
    table = _var_table(src, locator)
    panels = []
    for m in _CALL.finditer(locator):
        open_idx = m.end() - 1
        end = _match_paren(src, open_idx)  # offsets are shared: _blank_strings preserves them
        if end == -1:
            continue
        body = src[open_idx:end]
        side_m = re.match(r"\(\s*[\"']([a-z_]*)[\"']", body)
        panels.append(
            {
                "side": side_m.group(1) if side_m else None,
                "line": src.count("\n", 0, m.start()) + 1,
                "text": _expand_references(table, body),
                "call_text": body,
            }
        )
    return panels


def check_declared_sides(html: str) -> list[str]:
    """Each panel() call passes a side literal from the vocabulary."""
    bad = []
    for p in parse_panels(html):
        if p["side"] is None:
            bad.append(f"line {p['line']}: panel() called with a non-literal side")
        elif p["side"] not in SIDES:
            bad.append(
                f"line {p['line']}: panel side {p['side']!r} is not one of {list(SIDES)}"
            )
    return bad


def check_no_handwritten_panels(html: str) -> list[str]:
    """No panel markup is written by hand -- `panel()` is the only way one reaches the page.

    This is the half that FAILS WHEN A NEW PANEL IS ADDED WITHOUT DECLARING A SIDE, which is
    exit criterion 1 in its own words. Checking only that existing panels carry a side would
    pass a page that grew an undeclared twentieth.
    """
    src = _strip_comments(html)
    bad = []
    for m in re.finditer(r'<div class="panel"', src):
        tail = src[m.end() : m.end() + 40]
        # The single legal occurrence is inside the helper, which appends the attribute itself.
        if tail.startswith(" data-side=\"' +") or tail.startswith(' data-side="\' +'):
            continue
        line = src.count("\n", 0, m.start()) + 1
        bad.append(
            f"line {line}: hand-written panel markup with no declared wall side "
            "-- emit it through panel(side, title, body) instead"
        )
    return bad


def check_no_cross_wall_leaks(html: str) -> list[str]:
    """No SIM-only figure under a company panel; no company-only figure under a customer panel.

    Exit criterion 3, against the named instances. The direction matters and is not symmetric:
    a company panel may show a figure the customer also sees (their tariff is on their bill),
    but a CUSTOMER panel showing cost-to-serve is a leak, and a COMPANY panel showing the
    household's real churn truth is the bigger one -- it would assert the supplier can read
    something no supplier can.
    """
    bad = []
    for p in parse_panels(html):
        if p["side"] == "company":
            for fig in SIM_ONLY_FIGURES:
                if fig in p["text"]:
                    bad.append(
                        f"line {p['line']}: SIM-only figure {fig!r} renders under a "
                        "company-attributed panel -- no supplier can read it"
                    )
        if p["side"] == "customer":
            for fig in COMPANY_ONLY_FIGURES:
                if fig in p["text"]:
                    bad.append(
                        f"line {p['line']}: company-only figure {fig!r} renders in the "
                        "customer-eye subset -- no supplier shows a household this"
                    )
            for fig in SIM_ONLY_FIGURES:
                if fig in p["text"]:
                    bad.append(
                        f"line {p['line']}: SIM-only figure {fig!r} renders in the "
                        "customer-eye subset -- nothing outside the simulation can see it"
                    )
    return bad


def check_page(html: str) -> list[str]:
    """Every check, plus the fail-open guard: finding no panels at all is a violation."""
    violations = list(check_no_handwritten_panels(html))
    panels = parse_panels(html)
    if not panels:
        return violations + [
            "no panel() calls found at all -- the checker has been disconnected from the page "
            "(helper renamed?), which is a FAILED check and not a clean one"
        ]
    violations += check_declared_sides(html)
    violations += check_no_cross_wall_leaks(html)
    return violations


def read_exhibit() -> str:
    """The live page source. A missing/unreadable file raises rather than returning ''."""
    return EXHIBIT.read_text(encoding="utf-8")


def main() -> int:
    violations = check_page(read_exhibit())
    for v in violations:
        print(f"{EXHIBIT.relative_to(REPO_ROOT)}: {v}")
    if violations:
        print(f"\n{len(violations)} wall-side violation(s).")
        return 1
    counts = {s: 0 for s in SIDES}
    for p in parse_panels(read_exhibit()):
        counts[p["side"]] += 1
    print(
        "wall sides OK: "
        + ", ".join(f"{counts[s]} {s}" for s in SIDES)
        + f" ({sum(counts.values())} panels)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
