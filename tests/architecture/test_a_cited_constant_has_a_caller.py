"""A money constant that cites a published source must be REACHED by live code.

THE DEFECT THIS EXISTS FOR (2026-08-28,
WORKER_FINDING_THE_SOURCED_ACQUISITION_MODEL_IS_UNWIRED_AND_THE_INVENTED_ONE_IS_LIVE.md).
`saas/opex_ledger.py` held the researched cost of acquiring a customer -- £55 dual-fuel PCS
commission, £27.50 single fuel, and a per-kWh broker trail for business -- cited to
`docs/market_research/B2_CATEGORY6_CAC_ANCHORS.md` and thence to the CMA's energy market
investigation. It was written on 2026-07-10, it was unit-tested, and for seven weeks the only
code that called it was its own tests. What the live campaign actually spent was
`saas.growth_mandate.COST_PER_ACQUISITION = {"resi": 150.0, "SME": 400.0}` -- two numbers with
no source behind them, chosen because a number was needed.

    A sourced number that exists and is not wired should not be able to sit quietly beside an
    unsourced one that is.  -- director, 2026-08-28

Nothing could see it. Both modules imported cleanly, both were covered by tests, and
`docs/institutional/knowledge_map.md` recorded the sourced figure at confidence H while listing
the same subject among its top three gaps, in one file. The failure is not that a rule was
broken; it is that being sourced-but-unreached had no observable consequence anywhere.

WHY THIS IS ONE LEG AND NOT A REGISTER. The first draft of this control was a register of priced
quantities: every money constant declaring its source, its implementing symbol and its call
sites, with duplicate-quantity detection across the register. The director's standing instruction
the same day -- "prefer the smallest mechanism that can fail ... when in doubt, do the work rather
than build the thing that watches the work" -- retired it before it was written. The register
needs 176 hand-authored entries to say what this file says in one scan, and the one scan is what
actually fires on the defect. There is no YAML here on purpose.

WHAT IT CHECKS. Exactly one thing, and it is deliberately narrow:

    a module-level money constant whose own comment block cites a file under `docs/` must be
    reachable from outside its defining module by non-test code.

REACHABILITY IS TRANSITIVE, and it has to be. `CAC_ONE_OFF_GBP_PER_DUAL_FUEL_CUSTOMER` is never
named outside `saas/opex_ledger.py` even now that it is wired -- the accessor
`acquisition_cost_gbp()` is what callers import. A check that looked only for direct references
to the constant would call the repaired tree broken, which is the "keyed to today's answer"
failure this project has paid for repeatedly. So: a symbol is LIVE if some *other* in-scope
module imports its module and names it, or if a LIVE symbol in the same module references it, to
a fixpoint.

THE COLLISION GUARD, which is where the first version of this walker was FAIL-OPEN. Attributing
a reference by bare name alone means any module anywhere that happens to use the identifier
`ACQUISITION_COST` marks every constant of that name in the repo as reached. `_external_referrers`
therefore requires the referring module to actually IMPORT the defining module before its
references count. `test_a_bare_name_collision_does_not_count_as_reaching` pins it.

WHAT THIS DOES NOT CATCH, stated rather than implied:
  * an unsourced constant on the live path. This control is silent about `COST_PER_ACQUISITION`
    itself -- it fires on the *other* half of the pair, the sourced module sitting unused. That
    is the half that has no other symptom; an unsourced live constant at least shows up in the
    numbers it produces.
  * a constant that is reached but reached WRONGLY -- charged at the wrong time, to the wrong
    account, or in the wrong shape. R2 of the same roadmap is exactly that defect and no scan
    would have found it.
  * a constant declared directly beneath another one, sharing its comment block. The walker
    stops at the previous statement, so the second constant reads as uncited and is skipped --
    which is exactly what happens to `CAC_ONE_OFF_GBP_PER_SINGLE_FUEL_CUSTOMER`, unwired at the
    same commit as its dual-fuel twin and invisible here. Give a constant its own comment.
  * a sourced figure that is reached by reporting code only, never by the ledger. Distinguishing
    "printed in a table" from "spent" needs a curated list of ledger entry points, and a
    curated enumerator is what made the predecessor controls blind (see
    `test_year_keyed_rate_table_census.py`: "a register of unverified constants inherits the
    blindness of its own enumerator").
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

#: Where a money constant may live. `tools/` and `background/` are referrers but not subjects:
#: harness code is allowed to hold a number nobody spends.
SUBJECT_SCOPE = ("saas", "company", "simulation")
REFERRER_SCOPE = ("saas", "company", "simulation", "tools", "background")

#: A constant NAME that denominates money or a money rate. Deliberately a name test rather than a
#: value test: `0.0125` is not visibly a broker commission, but `BROKER_COMMISSION_GBP_PER_KWH`
#: is. Missing an oddly-named constant costs coverage; a value test would cost precision on every
#: probability and ratio in the repo.
_MONEY_NAME = re.compile(
    r"(GBP|_COST|COST_|_PRICE|PRICE_|_FEE|FEE_|COMMISSION|_CAC\b|CAC_|_SPEND|TARIFF|CHARGE)"
)

#: A citation: a path into one of the three places this project keeps published evidence.
#: The final character class is load-bearing -- a path at the end of a sentence would otherwise
#: swallow the full stop and every citation would resolve to a file that does not exist, which
#: is a control that fails LOUDLY for the wrong reason on its first run against the real tree.
_CITATION = re.compile(
    r"docs/(?:market_research|domain_artefact_library|institutional)/"
    r"[A-Za-z0-9_./-]*[A-Za-z0-9_]"
)

# ═══════════════════════════════════════════════════════════════════════════════════════════
# THE DATED FLOORS. A tree scan that finds nothing passes every assertion it makes, so the
# population is asserted before anything is asserted about it. Measured 2026-08-28 on the tree
# that carried the defect; these may rise, and a fall means the walker stopped seeing the repo
# rather than that the repo got cleaner.
# ═══════════════════════════════════════════════════════════════════════════════════════════
MONEY_CONSTANT_FLOOR = 150          # measured: 174
CITED_CONSTANT_FLOOR = 5            # measured: 7

#: The last commit before R1 wired the researched acquisition model — the tree the finding was
#: written against. Pinned as a SHA rather than `HEAD~n` so it keeps naming the same tree as the
#: branch moves on.
_PRE_R1_COMMIT = "a1aefccaf"

#: THERE IS NO ALLOWLIST, and that is a measurement rather than a boast.
#:
#: The first draft of this file carried four named exceptions, taken from a probe that attributed
#: reachability by DIRECT reference to the constant's own name. Every one of the four was wrong:
#: `INFRASTRUCTURE_COST_LINES`, `GOVERNANCE_COST_LINES`,
#: `OFGEM_BUNDLED_ALLOWANCE_GBP_PER_YEAR_DUAL_FUEL` and `_NETWORK_COST_RESI_SME_BY_YEAR` are all
#: read by an accessor in their own module that does have external callers, which the transitive
#: walker sees and the probe could not. A debt list built on the weaker measurement would have
#: recorded four repairs that were never needed and quietly widened the hole by four.
#:
#: So the live tree has ZERO sourced-and-unwired money constants -- once R1 gave
#: `acquisition_cost_gbp()` its first caller outside `saas/opex_ledger.py`. Before that commit it
#: had exactly one, and `test_it_fires_on_the_real_pre_r1_tree` runs this walker against that
#: commit to show the control is green because the defect was fixed, not because it is blind.


# ═══════════════════════════════════════════════════════════════════════════════════════════
# DISCOVERY
# ═══════════════════════════════════════════════════════════════════════════════════════════

def _module_name(path: Path, root: Path) -> str:
    """`saas/opex_ledger.py` -> `saas.opex_ledger`."""
    return ".".join(path.relative_to(root).with_suffix("").parts)


def _py_files(root: Path, scope: tuple[str, ...]) -> list[Path]:
    files: list[Path] = []
    for pkg in scope:
        d = root / pkg
        if not d.is_dir():
            continue
        files.extend(
            p for p in sorted(d.rglob("*.py"))
            if "__pycache__" not in p.parts and ".claude" not in p.parts
        )
    return files


def _comment_block(lines: list[str], node: ast.stmt) -> str:
    """The comment block immediately above an assignment, plus its own source lines.

    Walks upward through `#` lines and stops at the first blank line that follows one, so a
    constant's own commentary is read and the previous constant's is not.
    """
    block: list[str] = []
    i = node.lineno - 2
    while i >= 0:
        stripped = lines[i].strip()
        if stripped.startswith("#"):
            block.append(lines[i])
        elif stripped == "":
            if block:
                break
        else:
            break
        i -= 1
    block.extend(lines[node.lineno - 1: getattr(node, "end_lineno", node.lineno)])
    return "\n".join(block)


def _money_constants(root: Path) -> list[tuple[str, str, str | None]]:
    """Every module-level money constant in subject scope, as (relpath, name, citation|None)."""
    found: list[tuple[str, str, str | None]] = []
    for path in _py_files(root, SUBJECT_SCOPE):
        try:
            src = path.read_text(encoding="utf-8")
            tree = ast.parse(src)
        except (OSError, SyntaxError):  # pragma: no cover - a file that will not parse
            continue
        lines = src.splitlines()
        for node in tree.body:
            if isinstance(node, ast.Assign):
                names = [t.id for t in node.targets if isinstance(t, ast.Name)]
                value = node.value
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                names, value = [node.target.id], node.value
            else:
                continue
            is_number = (
                isinstance(value, ast.Constant)
                and isinstance(value.value, (int, float))
                and not isinstance(value.value, bool)
            )
            if not (is_number or isinstance(value, ast.Dict)):
                continue
            for name in names:
                if not name.isupper() or not _MONEY_NAME.search(name):
                    continue
                cite = _CITATION.search(_comment_block(lines, node))
                found.append((
                    str(path.relative_to(root)), name, cite.group(0) if cite else None,
                ))
    return found


# ═══════════════════════════════════════════════════════════════════════════════════════════
# REACHABILITY
# ═══════════════════════════════════════════════════════════════════════════════════════════

def _top_level_symbols(tree: ast.Module) -> dict[str, ast.stmt]:
    out: dict[str, ast.stmt] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out[node.name] = node
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    out[t.id] = node
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            out[node.target.id] = node
    return out


def _names_used(node: ast.AST) -> set[str]:
    """Every identifier referenced in a subtree, as a bare name or an attribute."""
    used: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Name):
            used.add(child.id)
        elif isinstance(child, ast.Attribute):
            used.add(child.attr)
        elif isinstance(child, ast.ImportFrom):
            used.update(a.name for a in child.names)
    return used


def _imported_modules(tree: ast.Module) -> set[str]:
    """Dotted module names this file imports, however the import is spelled."""
    mods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            mods.add(node.module)
            mods.update(f"{node.module}.{a.name}" for a in node.names)
    return mods


def live_symbols(root: Path) -> dict[str, set[str]]:
    """{module: symbols reachable from outside that module}, to a fixpoint.

    Two legs, and the second is why this is not a grep:
      (a) SEED -- a symbol another in-scope module imports this module and then names.
      (b) CLOSURE -- a symbol referenced by an already-live symbol of the same module. This is
          what makes a constant read only by its own module's accessor count as reached, once
          that accessor has a caller.
    """
    parsed: dict[str, tuple[str, ast.Module]] = {}
    for path in _py_files(root, REFERRER_SCOPE):
        try:
            parsed[_module_name(path, root)] = (
                str(path.relative_to(root)), ast.parse(path.read_text(encoding="utf-8")),
            )
        except (OSError, SyntaxError):  # pragma: no cover
            continue

    symbols = {mod: _top_level_symbols(tree) for mod, (_, tree) in parsed.items()}
    imports = {mod: _imported_modules(tree) for mod, (_, tree) in parsed.items()}
    whole_file_names = {mod: _names_used(tree) for mod, (_, tree) in parsed.items()}

    live: dict[str, set[str]] = {}
    for mod, defs in symbols.items():
        seed = set()
        for other, other_imports in imports.items():
            if other == mod:
                continue
            # THE COLLISION GUARD: a bare name match is not a reference unless the referring
            # module actually imports the defining one.
            if not any(i == mod or i.startswith(mod + ".") for i in other_imports):
                continue
            seed |= defs.keys() & whole_file_names[other]
        live[mod] = seed

    for mod, defs in symbols.items():
        frontier = list(live[mod])
        while frontier:
            current = frontier.pop()
            node = defs.get(current)
            if node is None:
                continue
            for name in _names_used(node):
                if name in defs and name not in live[mod]:
                    live[mod].add(name)
                    frontier.append(name)
    return live


def unreached_cited_constants(root: Path) -> list[tuple[str, str, str]]:
    """The finding, computed: (relpath, name, citation) for every sourced-and-unwired constant."""
    live = live_symbols(root)
    out: list[tuple[str, str, str]] = []
    for rel, name, cite in _money_constants(root):
        if cite is None:
            continue
        mod = rel[:-3].replace("/", ".")
        if name not in live.get(mod, set()):
            out.append((rel, name, cite))
    return out


# ═══════════════════════════════════════════════════════════════════════════════════════════
# THE POPULATION FLOORS — asserted first, because a walker that sees nothing passes everything
# ═══════════════════════════════════════════════════════════════════════════════════════════

def test_the_walker_still_sees_the_repo():
    constants = _money_constants(ROOT)
    cited = [c for c in constants if c[2]]
    assert len(constants) >= MONEY_CONSTANT_FLOOR, (
        f"only {len(constants)} money constants found, floor is {MONEY_CONSTANT_FLOOR}. "
        "The name pattern or the scope has stopped matching the tree -- this control is now "
        "passing because it is blind, not because the tree is clean."
    )
    assert len(cited) >= CITED_CONSTANT_FLOOR, (
        f"only {len(cited)} constants carry a docs/ citation, floor is {CITED_CONSTANT_FLOOR}. "
        "Either citations were deleted or the citation pattern stopped matching them."
    )


def test_every_citation_resolves_to_a_file_that_exists():
    """A citation to a file that is not there is worse than no citation: it reads as evidence."""
    dangling = [
        (rel, name, cite) for rel, name, cite in _money_constants(ROOT)
        if cite and not (ROOT / cite).exists()
    ]
    assert dangling == [], (
        "money constants cite source files that do not exist:\n" +
        "\n".join(f"  {rel}::{name} -> {cite}" for rel, name, cite in dangling)
    )


# ═══════════════════════════════════════════════════════════════════════════════════════════
# THE LEG
# ═══════════════════════════════════════════════════════════════════════════════════════════

def test_a_cited_money_constant_is_reached_by_live_code():
    """The one thing this file exists to say."""
    new = sorted(unreached_cited_constants(ROOT))
    assert new == [], (
        "A money constant cites published evidence and no live code reaches it.\n\n"
        "This is the shape of the 2026-08-28 finding: the researched acquisition cost sat in\n"
        "`saas/opex_ledger.py` for seven weeks, called by nothing but its own tests, while an\n"
        "invented £150 was what the campaign spent. A sourced number that is not wired will be\n"
        "replaced by an unsourced one, because the work still needs a number.\n\n"
        "Wire it, or delete it and say in the commit message why the evidence was not used:\n"
        + "\n".join(f"  {rel}::{name}\n    cites {cite}" for rel, name, cite in new)
    )


def test_it_fires_on_the_real_pre_r1_tree():
    """The strongest available evidence: run the walker against the commit that carried the bug.

    A mutation on a synthetic tree proves the SHAPE fires. This proves the real thing did. The
    subject is `HEAD` -- R1 is uncommitted work in the tree at the time of writing, so the
    committed tree is still the one where `saas/opex_ledger.acquisition_cost_gbp()` has no caller
    outside its own module and `COST_PER_ACQUISITION` is what the campaign spends.

    SKIPPED, never silently passed, if the checkout is unavailable (shallow clone, no git, an
    export). An unavailable check is a failed check, and a skip says so out loud; asserting
    nothing would let this read as evidence it is not.
    """
    import subprocess
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp)
        try:
            archive = subprocess.run(
                ["git", "archive", _PRE_R1_COMMIT, "saas", "company", "simulation",
                 "tools", "background", "docs/market_research", "docs/institutional",
                 "docs/domain_artefact_library"],
                cwd=ROOT, capture_output=True, timeout=120, check=True,
            ).stdout
            subprocess.run(["tar", "-x", "-C", str(dest)], input=archive,
                           capture_output=True, timeout=120, check=True)
        except (OSError, subprocess.SubprocessError) as exc:
            pytest.skip(f"cannot materialise {_PRE_R1_COMMIT}: {exc}")

        unreached = {(rel, name) for rel, name, _ in unreached_cited_constants(dest)}

    assert ("saas/opex_ledger.py", "CAC_ONE_OFF_GBP_PER_DUAL_FUEL_CUSTOMER") in unreached, (
        "this control does NOT fire on the tree that carried the defect it was written for, "
        f"so it is not evidence of anything. Unreached at {_PRE_R1_COMMIT}: {sorted(unreached)}"
    )
    # AND ITS TWIN IS ABSENT, which is a limit of the walker rather than a second finding.
    # `CAC_ONE_OFF_GBP_PER_SINGLE_FUEL_CUSTOMER` is equally unwired at this commit -- both dicts
    # are read only by `acquisition_cost_gbp()` -- but it is declared immediately below the
    # dual-fuel dict with no comment of its own, so `_comment_block` stops at that dict's closing
    # brace and reads it as uncited. Recorded here rather than papered over: a constant that
    # shares its neighbour's citation is invisible to this control. The £55 figure the finding
    # actually named is the one that fires, so the control is evidence for the claim made of it.
    assert ("saas/opex_ledger.py", "CAC_ONE_OFF_GBP_PER_SINGLE_FUEL_CUSTOMER") not in unreached


# ═══════════════════════════════════════════════════════════════════════════════════════════
# MUTATIONS — R15. Each proves a named defect makes this control fire.
# ═══════════════════════════════════════════════════════════════════════════════════════════

def _write_tree(root: Path, files: dict[str, str]) -> None:
    for rel, body in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")


def test_it_fires_on_the_historical_defect(tmp_path):
    """The pre-R1 tree, in miniature: sourced module unwired, invented one live.

    This is the mutation that matters. If this passes, the control would not have caught the
    thing it was built for.
    """
    _write_tree(tmp_path, {
        "docs/market_research/B2_CATEGORY6_CAC_ANCHORS.md": "CMA App 8.3: PCS commission ~£55.\n",
        "saas/__init__.py": "",
        "saas/opex_ledger.py": (
            "# Sourced to docs/market_research/B2_CATEGORY6_CAC_ANCHORS.md.\n"
            "CAC_ONE_OFF_GBP_PER_DUAL_FUEL_CUSTOMER = {'pcs_aggregator': 55.0}\n"
            "\n\ndef acquisition_cost_gbp(channel):\n"
            "    return CAC_ONE_OFF_GBP_PER_DUAL_FUEL_CUSTOMER.get(channel, 0.0)\n"
        ),
        "saas/growth_mandate.py": "COST_PER_ACQUISITION = {'resi': 150.0}\n",
        "company/__init__.py": "",
        "company/desk.py": (
            "from saas.growth_mandate import COST_PER_ACQUISITION\n"
            "def budget(seg):\n    return COST_PER_ACQUISITION.get(seg, 150.0)\n"
        ),
    })
    unreached = unreached_cited_constants(tmp_path)
    assert [(r, n) for r, n, _ in unreached] == [
        ("saas/opex_ledger.py", "CAC_ONE_OFF_GBP_PER_DUAL_FUEL_CUSTOMER")
    ], "the control did not fire on the defect it was built for"


def test_it_goes_green_when_the_accessor_gains_a_caller(tmp_path):
    """R1, in miniature — and the reason reachability has to be transitive.

    The constant is STILL named nowhere outside its own module. What changed is that the
    function reading it now has an external caller. A direct-reference check would call this
    tree broken, which is the "keyed to today's answer" failure.
    """
    _write_tree(tmp_path, {
        "docs/market_research/B2_CATEGORY6_CAC_ANCHORS.md": "CMA App 8.3.\n",
        "saas/__init__.py": "",
        "saas/opex_ledger.py": (
            "# Sourced to docs/market_research/B2_CATEGORY6_CAC_ANCHORS.md.\n"
            "CAC_ONE_OFF_GBP_PER_DUAL_FUEL_CUSTOMER = {'pcs_aggregator': 55.0}\n"
            "\n\ndef acquisition_cost_gbp(channel):\n"
            "    return CAC_ONE_OFF_GBP_PER_DUAL_FUEL_CUSTOMER.get(channel, 0.0)\n"
        ),
        "company/__init__.py": "",
        "company/desk.py": (
            "from saas.opex_ledger import acquisition_cost_gbp\n"
            "def budget(seg):\n    return acquisition_cost_gbp('pcs_aggregator')\n"
        ),
    })
    assert unreached_cited_constants(tmp_path) == []


def test_a_bare_name_collision_does_not_count_as_reaching(tmp_path):
    """FAIL-OPEN, and this walker's first draft had it.

    Another module defines and uses its OWN constant of the same name, and does not import the
    sourced module at all. Attributing by bare name would mark the sourced one reached and this
    whole file would pass on the defect it exists for.
    """
    _write_tree(tmp_path, {
        "docs/market_research/B2_CATEGORY6_CAC_ANCHORS.md": "CMA App 8.3.\n",
        "saas/__init__.py": "",
        "saas/opex_ledger.py": (
            "# Sourced to docs/market_research/B2_CATEGORY6_CAC_ANCHORS.md.\n"
            "ACQUISITION_COST_GBP = 55.0\n"
        ),
        "company/__init__.py": "",
        "company/elsewhere.py": (
            "ACQUISITION_COST_GBP = 150.0\n"
            "def budget():\n    return ACQUISITION_COST_GBP\n"
        ),
    })
    assert [(r, n) for r, n, _ in unreached_cited_constants(tmp_path)] == [
        ("saas/opex_ledger.py", "ACQUISITION_COST_GBP")
    ], "a same-named constant in an unrelated module was counted as reaching this one"


def test_a_test_only_caller_does_not_count_as_reaching(tmp_path):
    """`tests/` is not in referrer scope, and that is the whole point.

    The unwired model WAS tested. Being tested is what made it look alive.
    """
    _write_tree(tmp_path, {
        "docs/market_research/B2_CATEGORY6_CAC_ANCHORS.md": "CMA App 8.3.\n",
        "saas/__init__.py": "",
        "saas/opex_ledger.py": (
            "# Sourced to docs/market_research/B2_CATEGORY6_CAC_ANCHORS.md.\n"
            "CAC_ONE_OFF_GBP_PER_DUAL_FUEL_CUSTOMER = {'pcs_aggregator': 55.0}\n"
        ),
        "tests/__init__.py": "",
        "tests/test_opex_ledger.py": (
            "from saas.opex_ledger import CAC_ONE_OFF_GBP_PER_DUAL_FUEL_CUSTOMER\n"
            "def test_it():\n    assert CAC_ONE_OFF_GBP_PER_DUAL_FUEL_CUSTOMER\n"
        ),
    })
    assert [(r, n) for r, n, _ in unreached_cited_constants(tmp_path)] == [
        ("saas/opex_ledger.py", "CAC_ONE_OFF_GBP_PER_DUAL_FUEL_CUSTOMER")
    ]


def test_an_uncited_constant_is_not_this_controls_business(tmp_path):
    """Scope, pinned: this file is silent about the unsourced half of the pair.

    `COST_PER_ACQUISITION` is unsourced AND live and this control says nothing about it. Stating
    that in a test rather than a comment, because a reader who assumes otherwise will believe
    the unsourced constants are covered.
    """
    _write_tree(tmp_path, {
        "saas/__init__.py": "",
        "saas/growth_mandate.py": "COST_PER_ACQUISITION = {'resi': 150.0}\n",
    })
    assert unreached_cited_constants(tmp_path) == []
    assert [n for _, n, _ in _money_constants(tmp_path)] == ["COST_PER_ACQUISITION"]


@pytest.mark.parametrize("citation", [
    "docs/market_research/DOES_NOT_EXIST.md",
    "docs/domain_artefact_library/regulatory/not_here.json",
])
def test_a_dangling_citation_is_caught(tmp_path, citation):
    """A citation is evidence to a reader; one pointing at nothing is worse than none."""
    _write_tree(tmp_path, {
        "saas/__init__.py": "",
        "saas/thing.py": f"# Sourced to {citation}.\nTHING_COST_GBP = 1.0\n",
    })
    dangling = [
        (rel, name, cite) for rel, name, cite in _money_constants(tmp_path)
        if cite and not (tmp_path / cite).exists()
    ]
    assert dangling == [("saas/thing.py", "THING_COST_GBP", citation)]
