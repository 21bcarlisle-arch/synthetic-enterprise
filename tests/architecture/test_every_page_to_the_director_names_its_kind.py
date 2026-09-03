"""Every call that pages the director must name its `kind`, and the check is static.

THE DEFECT THIS EXISTS FOR (2026-09-03, two instances found within one hour of each other).
`background.notify.notify` has required a keyword-only `kind` since G-N2 -- "an untyped page is
forbidden". A caller that omits it does not send an untyped page; it raises `TypeError` and sends
NOTHING. Both instances were wrapped in an `except` that logged and returned, so both failed
silently, and both were on paths that fire rarely enough that no test and no run had reached them:

  * `tools/bill_validation_comparison.py` -- item 5 of the independent-bill-validation brief, the
    hourly timer that turns a validator that ran once into a control that fires. Its FIRST
    unattended firing, 2026-09-03 09:04:52, had a real delta to report (disagreements 295 -> 293)
    and raised `TypeError: notify() missing 1 required keyword-only argument: 'kind'`. The eight
    firings after it were silent for the honest reason -- no delta -- so nothing looked wrong.

  * `background/delivery_seat.py::_notify` -- the seat's own escalation route, which pages only
    when its direction record was refused or when something is genuinely the director's. It has
    fired TWICE in a month and neither page was sent. `docs/observability/delivery-seat-log.md`
    holds both: 2026-08-28 08:31:31Z (P9 book depth, priced and returned as a curriculum question)
    and 2026-08-30 23:30:30Z, which asked "whether YEAR_LEVEL_ANCHOR should aim at the published
    band's MIDPOINT instead of its high endpoint". That is the reserved class -- a director's
    decision, not a seat's -- and it went to a log file instead of to him.

WHY A STATIC CHECK AND NOT A TEST PER CALLER. The property is exactly "this call site is
well-formed", and the defect's whole shape is that the call site is on a branch nothing exercises.
A test that has to REACH the branch to check it is a test that will be written for the callers
somebody thought of, which is the set that was already fine. One scan reaches all of them,
including the ones added next week.

RESOLUTION IS BY IMPORT, NEVER BY BARE NAME, because the bare name is fail-open in both directions.
`company/interfaces/recorded_sim_interface.py` binds a local `notify = getattr(self._endo,
"notify_retention_attempt", None)` and calls it positionally; `tests/company/crm/test_solr_register.py`
and `tests/company/billing/test_deemed_contract.py` each define their own unrelated `notify`. A
name-only scan reports four defects that are not defects, and a maintainer who then narrows the
scan to silence them is one edit away from narrowing out the real ones. So a call counts only when
the FILE imports `background.notify`; none of those four do, and all four are skipped before any
call in them is looked at.

AND THE REBINDING GUARD WAS DELETED, which is worth recording because it is the more tempting
design. The first draft also dropped any name that its file rebinds, on the theory that a rebound
name cannot be attributed. Run, it dropped three modules -- `background/reconcile_watch.py`,
`background/suite_duration_watch.py`, `tools/surgical_land.py` -- and every one of them was a real
pager that names its kind correctly. All three use the same deliberate idiom: an injection point
(`def alarm(..., *, notify_fn=None)`) whose real import lands in the same name inside the function.
The guard was protecting against a population that the import test had already excluded, and
paying for it by silently skipping three of the tree's four highest-traffic pagers. A call site
must name its `kind` whichever function is injected into it, so the call site is checked and the
binding is not guessed at. `test_the_known_injection_points_are_inside_this_controls_population`
is what stops that narrowing coming back.

THE FLOOR IS THE FAIL-SILENT GUARD. A resolver that stops matching -- because the import style
changed, because the module moved -- would report zero call sites and pass. `MIN_CALL_SITES`
refuses that: this control asserts it examined a population, not merely that it found no
counter-examples in one. It is a floor and never an equality, so wiring a new pager is not a
red.

R15 -- the mutations, each run and reverted:
  * drop `kind="real_alarm"` from `background/delivery_seat.py::_notify` -> red, naming that file.
  * drop `kind="real_alarm"` from `tools/bill_validation_comparison.py::main` -> red, naming it.
  * lower `MIN_CALL_SITES` to 0 and delete every real call site -> still red, on the floor.
  * rename `background.notify` in the resolver so nothing resolves -> red on the floor, NOT a
    vacuous pass. This is the mutation the first draft of this file survived.
  * reinstate the rebinding guard -> `test_the_known_injection_points_are_inside_this_controls
    _population` reds, naming all three modules it would drop.
"""
from __future__ import annotations

import ast
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

#: The module whose `notify` is the director's channel. Not a string built at runtime: a rename
#: must break this file loudly rather than quietly stop resolving anything.
NOTIFY_MODULE = "background.notify"

#: A floor on the population this control actually examined. Measured at 2026-09-03: 93 resolved
#: call sites across the tracked tree, in 29 files. Set well below that so ordinary churn is not a
#: red, and above zero so a resolver that has stopped resolving cannot pass.
MIN_CALL_SITES = 40


def _tracked_python_files() -> list[Path]:
    """TRACKED files only. The shared tree routinely carries a few hundred untracked artefacts
    from concurrent lanes, and a whole-tree scan would let one lane's scratch file wedge another
    lane's commit -- a cost this repo has already paid on the ruff ratchet."""
    out = subprocess.run(
        ["git", "-C", str(REPO), "ls-files", "-z", "*.py"],
        capture_output=True, text=True, check=True,
    ).stdout
    return [REPO / name for name in out.split("\0") if name]


def _notify_names(tree: ast.Module) -> tuple[set[str], set[str]]:
    """Names in this module that reach `background.notify.notify`.

    Returns (direct, module_aliases): `direct` are names bound to the FUNCTION, so `name(...)` is
    a page; `module_aliases` are names bound to the MODULE, so `alias.notify(...)` is a page.
    """
    direct: set[str] = set()
    module_aliases: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == NOTIFY_MODULE:
                for alias in node.names:
                    if alias.name == "notify":
                        direct.add(alias.asname or alias.name)
            elif node.module == NOTIFY_MODULE.rsplit(".", 1)[0]:
                # `from background import notify` binds the MODULE under that name.
                for alias in node.names:
                    if alias.name == NOTIFY_MODULE.rsplit(".", 1)[1]:
                        module_aliases.add(alias.asname or alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == NOTIFY_MODULE:
                    # `import background.notify as n` -> n; `import background.notify` -> the
                    # dotted path, which `_callee_name` reassembles.
                    module_aliases.add(alias.asname or NOTIFY_MODULE)
    return direct, module_aliases


def _callee_name(func: ast.AST) -> str | None:
    """The dotted source spelling of a call's callee, or None for anything not a plain name or
    attribute chain (a subscript, a call result -- neither of which this control attributes)."""
    parts: list[str] = []
    node = func
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return None
    parts.append(node.id)
    return ".".join(reversed(parts))


def _page_call_sites() -> list[tuple[Path, int, ast.Call]]:
    """Every call in the tracked tree whose callee traces back to an import of
    `background.notify`. Nothing is dropped here: a file that does not import the module
    contributes no names, and a file that does has its calls checked whatever else it binds
    that name to (see the module docstring on the deleted rebinding guard)."""
    sites: list[tuple[Path, int, ast.Call]] = []
    for path in _tracked_python_files():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError, OSError):
            continue
        direct, module_aliases = _notify_names(tree)
        if not direct and not module_aliases:
            continue
        callees = set(direct) | {f"{alias}.notify" for alias in module_aliases}
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and _callee_name(node.func) in callees:
                sites.append((path, node.lineno, node))
    return sites


def _names_its_kind(call: ast.Call) -> bool:
    """`kind=` by keyword. A `**kwargs` splat is NOT accepted: it cannot be checked here, and
    accepting it would make this control lift on exactly the edit that hides a defect from it.
    There are none in the tree today, so nothing is being grandfathered."""
    return any(kw.arg == "kind" for kw in call.keywords)


@pytest.fixture(scope="module")
def scan():
    return _page_call_sites()


def test_the_scan_reached_a_population_and_not_an_empty_set(scan):
    """DEFECT: the resolver stops resolving and the control passes on nothing.

    This is the mutation that killed the first draft. Rename the notify module, change the import
    style, move the file -- `_notify_names` returns empty for every file, `_page_call_sites`
    returns `[]`, and a check written as "no call site omits kind" is vacuously green forever.
    """
    sites = scan
    assert len(sites) >= MIN_CALL_SITES, (
        "this control resolved only {} call site(s) to {}.notify, below the floor of {} -- it is "
        "reporting on a population it did not find, which is a FAILED check and never a pass. "
        "Either the import style changed or the module moved; fix the resolver, do not lower the "
        "floor".format(len(sites), NOTIFY_MODULE, MIN_CALL_SITES)
    )


def test_every_page_to_the_director_names_its_kind(scan):
    """DEFECT: a page that raises TypeError into an `except` and sends nothing.

    G-N2 makes `kind` required, so omitting it does not produce an untyped page -- it produces no
    page at all, on a branch that by construction fires rarely. Two such call sites were live on
    2026-09-03; between them they swallowed a delta the hourly validator had correctly found and
    two escalations that were the director's own to decide.
    """
    sites = scan
    untyped = [
        "{}:{}".format(path.relative_to(REPO), lineno)
        for path, lineno, call in sites
        if not _names_its_kind(call)
    ]
    assert not untyped, (
        "these call(s) page the director without naming a `kind`, so notify() raises TypeError "
        "and NOTHING is sent -- into an `except` in every instance found so far:\n  {}".format(
            "\n  ".join(untyped))
    )


#: The three modules that reach the notify function through an INJECTION POINT -- a keyword
#: parameter defaulting to None, with the real import landing in that same name inside the
#: function. Named individually because the first draft of this control silently dropped all
#: three, and a resolver narrowing is invisible unless something names what it must still reach.
INJECTION_POINT_PAGERS = (
    "background/reconcile_watch.py",
    "background/suite_duration_watch.py",
    "tools/surgical_land.py",
)


def test_the_known_injection_points_are_inside_this_controls_population(scan):
    """DEFECT: the resolver narrows, and the modules it stops reaching are the busiest pagers.

    The first draft dropped any name its file rebinds. That is a defensible-sounding rule and it
    excluded `reconcile_watch` (the manifest-divergence page), `suite_duration_watch` (both
    duration alarms) and `surgical_land` (every landing announcement) -- because all three take
    their notify function as an injectable parameter and import the real one into the same name.
    All three were correct, so the narrowing cost nothing that day and would have cost everything
    the day one of them regressed.

    So coverage is asserted by NAME rather than only by count. A floor alone cannot catch this:
    dropping three files out of eighty-seven leaves the floor comfortably met.
    """
    reached = {str(path.relative_to(REPO)) for path, _lineno, _call in scan}
    missing = [name for name in INJECTION_POINT_PAGERS if name not in reached]
    assert not missing, (
        "this control no longer reaches {} -- module(s) that page the director through an "
        "injection point. A resolver that cannot see them reports green on their regressions. "
        "Fix the resolver rather than this list; the list is the witness, not the "
        "subject.".format(", ".join(missing))
    )
