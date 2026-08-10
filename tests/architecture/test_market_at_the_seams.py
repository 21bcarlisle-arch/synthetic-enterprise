"""A9 — a second market must fit behind the seams that already exist.

Atom `A9_market_at_the_seams_design_law`, minted 2026-08-10 from
`docs/design/refs/ADVISOR_ANALYSIS_MARKET_PORTABILITY_2026-08-07.md`.

The analysis splits Poesys four ways — INVARIANT (harness, wall, bitemporal spine),
PARAMETERISE (cost-stack lines, tariffs, calendars — *tables*, not code),
ADAPTER-SWAP (settlement body, metering, registry, payment rails — the seam's
second dividend), REBUILD (compliance organs, local law). This module owns the
**middle two**, as the design law they imply:

  RULE 1  No counterparty identity is hardcoded across a seam.
  RULE 2  Every market-varying quantity is reachable as a table, not a literal.

**Why a test and not a review lens.** `docs/design/PORTABILITY_DEBT.md` already
*records* breaches in shipped code, under remediation-on-touch: never retrofit
speculatively, log instead. A register that only logs is a cleanup, not a control —
it grows monotonically and nothing stops the next breach. This module is the half
that makes a **NEW** breach fail. The existing rows are the baseline; the register
is the allowlist; adding a breach means editing the register in the same change,
which is what that file's own maintenance rule already demands and has never been
able to enforce.

**What this does NOT do.** It builds no second market and no second segment (GB
SME/I&C is the analysis's recommended first extension and is a separate draw). It
does not sweep-rename the 58 baseline sites — remediation-on-touch stands. It says
nothing about the four RESERVED classes, the epistemic wall, or scale debt
(C-S1..C-S5, a different axis, tracked at its own touch points).

**R15.** Every control below names the mutation that must make it fire, and the
mutation tests at the bottom run those mutations against the scanner rather than
asserting that they would work. Three failure shapes are guarded explicitly:

  TAUTOLOGY   — the truth side (an AST scan of real seam code) and the allowlist
                side (a hand-maintained markdown table) share no source. Neither
                is derived from the other; a wrong register cannot make the scan
                agree with it.
  FAIL-OPEN   — an empty seam surface, an unparseable register, a missing baseline
                block, or a syntactically broken seam module all FAIL. A check that
                cannot see its subject is a failed check, not a passed one.
  FAIL-SILENT — the baseline is exact in BOTH directions. An entry that no longer
                corresponds to live code fails as loudly as a new breach does; that
                is the register's drain, without which the ratchet is a cleanup.
"""

from __future__ import annotations

import ast
import re
from collections import Counter
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTER = REPO_ROOT / "docs" / "design" / "PORTABILITY_DEBT.md"

BEGIN_MARKER = "<!-- BEGIN market-at-the-seams baseline -->"
END_MARKER = "<!-- END market-at-the-seams baseline -->"

# ---------------------------------------------------------------------------
# The seam surface. DERIVED, never hand-listed: a hand-list is fail-open by
# omission — the next seam file simply is not on it, and the control passes by
# not looking. The derivation is the project's own two conventions: the declared
# boundary packages, plus the `*seam*.py` naming used for every contract module
# on either side of the wall.
# ---------------------------------------------------------------------------
SEAM_PACKAGES = ("company/interfaces", "interface/contracts")
PRODUCTION_ROOTS = ("company", "interface", "saas", "sim", "simulation")

# The declared SIM/company boundary (CLAUDE.md) — if the derivation ever stops
# returning this file, the derivation is broken, not the codebase.
SEAM_SURFACE_ANCHOR = "company/interfaces/sim_interface.py"
SEAM_SURFACE_FLOOR = 10

# ---------------------------------------------------------------------------
# RULE 1 vocabulary: GB market institutions and the identity schemes they issue.
# A market-varying counterparty by definition — every one of these has a
# different-named equivalent in AEMO/ERCOT/Elhub/SEM, which is exactly why a seam
# must not spell it. Deliberately excludes ambiguous three-letter GB acronyms
# (SSP/SBP/GSP) whose words collide with ordinary code.
# ---------------------------------------------------------------------------
COUNTERPARTY_WORDS = frozenset(
    {
        "elexon",
        "neso",
        "ngeso",
        "ofgem",
        "mpan",
        "mpans",
        "mprn",
        "mprns",
        "bmrs",
        "bmu",
        "xoserve",
        "ecoes",
        "gemserv",
        "nbp",
        "bsc",
    }
)

# RULE 2 vocabulary: a market-varying quantity baked in as a literal. Currency is
# the register's own deepest row (#1) — `*_gbp` names put the currency in the
# field name, so a second currency cannot be represented without touching every
# arithmetic site. `48` is settlement granularity (register row #3): true for GB
# and IE, false for ERCOT-15min and NEM-5min.
CURRENCY_WORDS = frozenset({"gbp", "sterling", "pence", "pounds"})
MARKET_LITERALS = {48: "48"}
CURRENCY_SYMBOL = "£"
CURRENCY_SYMBOL_TOKEN = "gbp_symbol"

KIND_COUNTERPARTY = "counterparty"
KIND_MARKET_QUANTITY = "market_quantity"

_WORD = re.compile(r"[A-Z]+(?![a-z])|[A-Z][a-z]+|[a-z]+|[0-9]+")
_ALPHA = re.compile(r"[A-Za-z]+")


def _words(identifier: str) -> list[str]:
    """Split `unit_rate_gbp_per_mwh` / `loadNbpHistory` / `MPAN` into words.

    Word-splitting rather than a substring or `\\b` regex on the raw identifier:
    `\\b` does not fire inside `unit_rate_gbp_per_mwh` (underscore is a word
    character), so a substring search is the only alternative — and a substring
    search matches `dcc` inside `reconciliation_dcc_free` and every other
    accidental trigram. Splitting first makes the match exact-word by
    construction, which is why the baseline below has no false positives to
    exempt.
    """
    return [w.lower() for w in _WORD.findall(identifier)]


def _docstring_node_ids(tree: ast.AST) -> set[int]:
    """String constants that are docstrings, by node identity.

    Prose is EXCLUDED, on purpose and narrowly. "This seam carries what Elexon
    publishes" is documentation of provenance; it is not a counterparty identity
    hardcoded across the seam. The contract surface — names, arguments, payload
    keys, non-docstring string constants — is what a second market has to live
    with, so that is what is policed. `test_prose_is_not_a_breach_but_a_payload_key_is`
    proves the exclusion is this narrow and no narrower.
    """
    ids: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(
            node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            if ast.get_docstring(node) is not None:
                ids.add(id(node.body[0].value))  # type: ignore[attr-defined]
    return ids


def scan_source(path: str, source: str) -> Counter[tuple[str, str, str]]:
    """Breaches in one seam module, keyed `(kind, path, token)` → site count.

    Keyed by token and counted, never keyed by line number: line numbers churn on
    every edit above them, so a line-keyed baseline would red on unrelated changes
    and get bulk-refreshed, which is how a ratchet stops being read. Counting
    means an EXTRA `mpan` in an already-exempt file still fails — an exemption is
    for the debt that was logged, not a standing licence for that file.
    """
    tree = ast.parse(source)  # a seam that will not parse is a failed check
    docstrings = _docstring_node_ids(tree)
    found: Counter[tuple[str, str, str]] = Counter()

    def hit(kind: str, token: str) -> None:
        found[(kind, path, token)] += 1

    def classify(word: str) -> None:
        if word in COUNTERPARTY_WORDS:
            hit(KIND_COUNTERPARTY, word)
        if word in CURRENCY_WORDS:
            hit(KIND_MARKET_QUANTITY, word)

    for node in ast.walk(tree):
        identifiers: list[str] = []
        if isinstance(node, ast.Name):
            identifiers.append(node.id)
        elif isinstance(node, ast.arg):
            identifiers.append(node.arg)
        elif isinstance(node, ast.Attribute):
            identifiers.append(node.attr)
        elif isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            identifiers.append(node.name)
        elif isinstance(node, ast.keyword) and node.arg:
            identifiers.append(node.arg)

        for identifier in identifiers:
            for word in _words(identifier):
                classify(word)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, str) and id(node) not in docstrings:
                for word in _ALPHA.findall(node.value):
                    classify(word.lower())
                if CURRENCY_SYMBOL in node.value:
                    hit(KIND_MARKET_QUANTITY, CURRENCY_SYMBOL_TOKEN)
            elif not isinstance(node.value, bool) and node.value in MARKET_LITERALS:
                hit(KIND_MARKET_QUANTITY, MARKET_LITERALS[node.value])

    return found


def seam_surface() -> list[Path]:
    files: set[Path] = set()
    for root in PRODUCTION_ROOTS:
        root_dir = REPO_ROOT / root
        if not root_dir.is_dir():
            continue
        for path in root_dir.rglob("*.py"):
            if "seam" in path.name:
                files.add(path)
    for package in SEAM_PACKAGES:
        package_dir = REPO_ROOT / package
        if not package_dir.is_dir():
            continue
        files.update(package_dir.glob("*.py"))
    return sorted(files)


def scan_seam_surface() -> Counter[tuple[str, str, str]]:
    found: Counter[tuple[str, str, str]] = Counter()
    for path in seam_surface():
        rel = path.relative_to(REPO_ROOT).as_posix()
        found.update(scan_source(rel, path.read_text(encoding="utf-8")))
    return found


def parse_baseline(register_text: str) -> Counter[tuple[str, str, str]]:
    """The allowlist, read from the register's fenced baseline block.

    Fails closed on a missing/duplicated/malformed block. A baseline that cannot
    be read is not an empty baseline — an empty baseline would silently exempt
    nothing and red every row at once, which reads as "the control is broken" and
    gets bypassed; a parse error names itself instead.
    """
    if register_text.count(BEGIN_MARKER) != 1 or register_text.count(END_MARKER) != 1:
        raise ValueError(
            f"exactly one {BEGIN_MARKER} / {END_MARKER} pair required in the register"
        )
    body = register_text.split(BEGIN_MARKER, 1)[1].split(END_MARKER, 1)[0]

    baseline: Counter[tuple[str, str, str]] = Counter()
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("```"):
            continue
        fields = line.split()
        if len(fields) != 4:
            raise ValueError(f"baseline row needs 4 fields, got {len(fields)}: {raw!r}")
        kind, path, token, count = fields
        if kind not in (KIND_COUNTERPARTY, KIND_MARKET_QUANTITY):
            raise ValueError(f"unknown breach kind {kind!r} in baseline row: {raw!r}")
        if not count.isdigit() or int(count) < 1:
            raise ValueError(f"baseline count must be a positive integer: {raw!r}")
        key = (kind, path, token)
        if key in baseline:
            raise ValueError(f"duplicate baseline row for {key}")
        baseline[key] = int(count)
    return baseline


def _fmt(keys) -> str:
    return "\n".join(f"    {kind:16} {path:52} {token}" for kind, path, token in keys)


# ---------------------------------------------------------------------------
# Vacuity guards. These run first because every control below is meaningless if
# the scanner is looking at nothing.
# ---------------------------------------------------------------------------


def test_the_seam_surface_is_derived_non_empty_and_contains_the_declared_boundary():
    """MUTATION (must fire): rename `company/interfaces/` or drop the `*seam*.py`
    convention, so the derivation returns a short or empty list.

    A population control with no population passes. This is the guard that makes
    "no new breach found" mean "none exists" rather than "nothing was read".
    """
    surface = [p.relative_to(REPO_ROOT).as_posix() for p in seam_surface()]
    assert len(surface) >= SEAM_SURFACE_FLOOR, (
        f"seam surface collapsed to {len(surface)} files (floor {SEAM_SURFACE_FLOOR}) — "
        "the derivation is broken, so this module is not policing anything:\n"
        + "\n".join(f"    {p}" for p in surface)
    )
    assert SEAM_SURFACE_ANCHOR in surface, (
        f"the declared SIM/company boundary {SEAM_SURFACE_ANCHOR} is not in the derived "
        "seam surface — fix the derivation before trusting any result here"
    )


def test_the_baseline_block_parses_and_is_non_empty():
    """MUTATION (must fire): delete the baseline block from the register.

    Documents the fail-closed contract of `parse_baseline` against the real file.
    """
    baseline = parse_baseline(REGISTER.read_text(encoding="utf-8"))
    assert baseline, "the register's baseline block is empty — see parse_baseline()"


# ---------------------------------------------------------------------------
# RULE 1 — no counterparty identity hardcoded across a seam.
# ---------------------------------------------------------------------------


def test_no_new_counterparty_identity_is_hardcoded_across_a_seam():
    """MUTATION (must fire): add `def get_bsc_settlement(self, mpan: str)` to any
    seam module, or add `"elexon_ref"` as a payload key.
    Run live by `test_scanner_fires_on_a_new_counterparty_at_a_seam`.

    RULE 1 of the design law. GB institutions and their identity schemes may be
    NAMED in a seam's prose; they may not be spelled into its contract.
    """
    found = scan_seam_surface()
    baseline = parse_baseline(REGISTER.read_text(encoding="utf-8"))
    new = {
        key: count
        for key, count in found.items()
        if key[0] == KIND_COUNTERPARTY and count > baseline.get(key, 0)
    }
    assert not new, (
        "a counterparty identity is hardcoded across a seam beyond the recorded debt:\n"
        + "\n".join(
            f"    {path} — {token} × {count} (register allows "
            f"{baseline.get((kind, path, token), 0)})"
            for (kind, path, token), count in sorted(new.items())
        )
        + "\n\nEither keep the seam regime-neutral, or — if the breach is genuinely "
        f"unavoidable now — add the row to the baseline block in {REGISTER.name} IN "
        "THE SAME CHANGE. That register's own maintenance rule already requires it; "
        "this control is what makes it true."
    )


# ---------------------------------------------------------------------------
# RULE 2 — every market-varying quantity reachable as a table, not a literal.
# ---------------------------------------------------------------------------


def test_no_new_market_varying_quantity_is_baked_into_a_seam():
    """MUTATION (must fire): add `price_gbp: float` to a seam payload, or a bare
    `48` half-hour count to a seam contract.
    Run live by `test_scanner_fires_on_a_new_market_quantity_at_a_seam`.

    RULE 2 of the design law. Currency in a field name (register row #1) and
    settlement granularity as a literal (row #3) are the two shapes that actually
    occur here; both are quantities a second market changes, so both belong in a
    table the adapter supplies.
    """
    found = scan_seam_surface()
    baseline = parse_baseline(REGISTER.read_text(encoding="utf-8"))
    new = {
        key: count
        for key, count in found.items()
        if key[0] == KIND_MARKET_QUANTITY and count > baseline.get(key, 0)
    }
    assert not new, (
        "a market-varying quantity is baked into a seam beyond the recorded debt:\n"
        + "\n".join(
            f"    {path} — {token} × {count} (register allows "
            f"{baseline.get((kind, path, token), 0)})"
            for (kind, path, token), count in sorted(new.items())
        )
        + f"\n\nMake it a table the adapter supplies, or record the row in {REGISTER.name} "
        "in the same change."
    )


# ---------------------------------------------------------------------------
# The drain. Without this the baseline is a cleanup, not a ratchet.
# ---------------------------------------------------------------------------


def test_the_baseline_does_not_overstate_the_debt_it_records():
    """MUTATION (must fire): bump any baseline count by one, or leave a row in
    after remediating the code it describes.
    Run live by `test_scanner_reports_a_departed_baseline_entry`.

    A subset register cannot fail on a DEPARTED entry: if exemptions only ever
    have to be >= reality, a remediated breach leaves a standing licence behind,
    and the next breach lands inside it for free. Exact in both directions —
    fixing a seam means shrinking this register in the same change.
    """
    found = scan_seam_surface()
    baseline = parse_baseline(REGISTER.read_text(encoding="utf-8"))
    stale = {
        key: (allowed, found.get(key, 0))
        for key, allowed in baseline.items()
        if found.get(key, 0) < allowed
    }
    assert not stale, (
        "the baseline claims debt that is no longer in the code — drain it:\n"
        + "\n".join(
            f"    {path} — {token}: register says {allowed}, code has {actual}"
            for (kind, path, token), (allowed, actual) in sorted(stale.items())
        )
        + "\n\nShrink (or delete) the row and mark the register table entry CLOSED with "
        "the commit that remediated it. Never widen the row to match."
    )


# ---------------------------------------------------------------------------
# R15 mutation tests — the controls above are asserted to FIRE, not assumed to.
# ---------------------------------------------------------------------------

_CLEAN_SEAM = '''
"""A regime-neutral seam. Elexon and MPANs are discussed here in prose only."""


class MeterReadRequest:
    def __init__(self, supply_point_id: str, amount_minor: int) -> None:
        self.supply_point_id = supply_point_id
        self.amount_minor = amount_minor
'''


def test_the_clean_seam_fixture_is_actually_clean():
    """The negative control. If this fixture scanned dirty, every mutation test
    below would pass for the wrong reason.
    """
    assert scan_source("fixture/clean_seam.py", _CLEAN_SEAM) == Counter()


def test_scanner_fires_on_a_new_counterparty_at_a_seam():
    """The named defect for RULE 1, run rather than described."""
    # A method name, an argument, a payload key and a literal value — the four
    # places a counterparty actually gets into a contract.
    mutated = _CLEAN_SEAM + '''
    def elexon_settlement(self, mpan: str) -> dict:
        return {"mpan": mpan, "source": "ELEXON"}
'''
    found = scan_source("fixture/clean_seam.py", mutated)
    assert found[(KIND_COUNTERPARTY, "fixture/clean_seam.py", "elexon")] == 2  # def, value
    assert found[(KIND_COUNTERPARTY, "fixture/clean_seam.py", "mpan")] == 3  # arg, key, use


def test_scanner_fires_on_a_new_market_quantity_at_a_seam():
    """The named defect for RULE 2, run rather than described."""
    mutated = _CLEAN_SEAM + '''

    def price(self) -> float:
        unit_rate_gbp = 0.0
        periods_per_day = 48
        return unit_rate_gbp * periods_per_day
'''
    found = scan_source("fixture/clean_seam.py", mutated)
    assert found[(KIND_MARKET_QUANTITY, "fixture/clean_seam.py", "gbp")] == 2
    assert found[(KIND_MARKET_QUANTITY, "fixture/clean_seam.py", "48")] == 1


def test_prose_is_not_a_breach_but_a_payload_key_is():
    """The false-positive boundary, asserted in both directions.

    A control that reds on innocent prose gets bypassed, and a control that
    excuses everything string-shaped is blind. The line is: docstrings are
    documentation, every other string constant is contract.
    """
    prose_only = '''
"""Settlement observables sourced from Elexon; keys are MPAN-shaped upstream."""


def read(supply_point_id: str) -> dict:
    """Elexon publishes this; the MPAN stays on the far side of the seam."""
    return {"supply_point_id": supply_point_id}
'''
    assert scan_source("fixture/prose.py", prose_only) == Counter()

    payload_key = prose_only.replace(
        '{"supply_point_id": supply_point_id}', '{"mpan": supply_point_id}'
    )
    assert scan_source("fixture/prose.py", payload_key)[
        (KIND_COUNTERPARTY, "fixture/prose.py", "mpan")
    ] == 1


def test_scanner_reports_a_departed_baseline_entry():
    """The named defect for the drain: a register row whose code is gone."""
    baseline = parse_baseline(
        f"{BEGIN_MARKER}\ncounterparty fixture/clean_seam.py mpan 3\n{END_MARKER}"
    )
    found = scan_source("fixture/clean_seam.py", _CLEAN_SEAM)
    stale = {k: v for k, v in baseline.items() if found.get(k, 0) < v}
    assert stale, "the drain cannot see a fully departed entry"


def test_an_extra_site_in_an_already_exempt_file_still_fires():
    """An exemption is for the debt that was logged, not a licence for the file.

    MUTATION: add a second `mpan` argument to a file the register already lists.
    """
    baseline = parse_baseline(
        f"{BEGIN_MARKER}\ncounterparty fixture/seam.py mpan 1\n{END_MARKER}"
    )
    source = "def read(mpan: str, other_mpan: str) -> None:\n    return None\n"
    found = scan_source("fixture/seam.py", source)
    key = (KIND_COUNTERPARTY, "fixture/seam.py", "mpan")
    assert found[key] > baseline[key]


@pytest.mark.parametrize(
    "text",
    [
        "",  # no block at all
        f"{BEGIN_MARKER}\n{END_MARKER}\n{BEGIN_MARKER}\n{END_MARKER}",  # duplicated
        f"{BEGIN_MARKER}\ncounterparty two fields\n{END_MARKER}",  # wrong arity
        f"{BEGIN_MARKER}\nnot_a_kind a/b.py mpan 1\n{END_MARKER}",  # unknown kind
        f"{BEGIN_MARKER}\ncounterparty a/b.py mpan zero\n{END_MARKER}",  # bad count
        f"{BEGIN_MARKER}\ncounterparty a/b.py mpan 0\n{END_MARKER}",  # zero row
        f"{BEGIN_MARKER}\ncounterparty a/b.py mpan 1\ncounterparty a/b.py mpan 2\n{END_MARKER}",
    ],
)
def test_an_unreadable_register_fails_closed(text: str):
    """FAIL-OPEN guard. An unavailable check is a FAILED check (R15): a register
    that cannot be read must not resolve to "nothing is exempt, nothing to see".
    """
    with pytest.raises(ValueError):
        parse_baseline(text)


def test_a_seam_module_that_cannot_be_parsed_fails_rather_than_being_skipped():
    """FAIL-SILENT guard: a scanner that swallowed a SyntaxError would report a
    broken seam as clean, which is the exact shape a breach hides behind.
    """
    with pytest.raises(SyntaxError):
        scan_source("fixture/broken.py", "def f(:\n")
