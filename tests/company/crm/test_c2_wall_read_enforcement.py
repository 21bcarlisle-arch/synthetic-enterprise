"""C2 wall-read enforcement -- the CLASS guard (R10) for the property-discovery wall.

Closes the R15 FAIL-SILENT gap red-teamed on 2026-07-22
(docs/design/C2_DISCOVERY_HARDEN_REDTEAM_2026-07-22.md): C2's wall
("...discovers property truth through observable interfaces, *not a direct read*")
was accessor-enforced only. Its three pre-existing guards were narrow substring
scans over THREE of the five belief-layer modules; the two files that actually
CONSTRUCT and STORE the belief -- home_registry.py and property_model.py -- had
no wall test of any kind, and a scratch mutation injecting a raw
`from saas.property_model import build_properties` read into
`home_registry.register_from_signup` passed the entire suite silently.

This guard makes the whole CLASS fail automatically (R10): it AST-scans EVERY
file in C2's file_scope for any read of the ground-truth property record
(`saas.property_model` / `saas.customers` / `build_properties`) or of sim
internals (`sim` / `simulation`). AST -- not substring -- so a docstring that
merely *names* saas/property_model.py (several of these modules have one) does
not false-positive; only a real import or name reference does.

R15 both-ways is pinned IN-SUITE via `test_guard_fires_on_injected_ground_truth_read`:
the same detector is run over a mutant snippet and MUST flag it. If that test
ever passes clean, the guard has gone fail-silent and is worthless.

The set of files scanned is DERIVED FROM THE LIVE MAP (C2's file_scope in
maturity_map.yaml), not hardcoded -- see the 2026-07-27 HARDEN note on
`C2_FILE_SCOPE` below. A hardcoded copy is the "full-key-set" fail-silent class
(recurred twice on E4): a belief-layer module added to the map's file_scope
would escape a stale hardcoded list unguarded. Deriving from the map closes it.
"""
import ast
from pathlib import Path

import pytest
import yaml

from tools import maturity_map_store as map_store

# C2's file_scope is the AUTHORITATIVE list of belief-layer modules that must
# build property beliefs ONLY from observable events, never from a direct
# ground-truth read. It lives in maturity_map.yaml (atom
# C2_discovery_through_interfaces) and is derived from there at import time --
# NOT hardcoded here.
#
# R15 (2026-07-27 HARDEN red-team): a hardcoded copy is the "aggregate-tie /
# full-key-set" fail-silent class that recurred twice on E4 -- if the map's
# file_scope gains a sixth belief-layer module, a hardcoded tuple would keep
# scanning the stale five and the new file would cross the wall unguarded,
# silently. Deriving the coverage set from the live map makes that drift
# impossible: a file added to C2's file_scope is scanned automatically.
MAP_PATH = (
    Path(__file__).resolve().parents[3] / "docs" / "design" / "maturity_map.yaml"
)
C2_ATOM_ID = "C2_discovery_through_interfaces"


def _c2_file_scope_from_atoms(atoms: list) -> tuple[str, ...]:
    """Extract C2's file_scope from a maturity-map atom list.

    Fails LOUD (not fail-open) if the atom is missing or its file_scope is
    empty -- an unavailable coverage set is a FAILED guard, not a passing one
    (R15 pattern 3). Factored out so the missing/empty cases can be unit-tested
    without mutating the real map file.
    """
    matches = [a for a in atoms if isinstance(a, dict) and a.get("id") == C2_ATOM_ID]
    if not matches:
        raise ValueError(
            f"C2 wall guard cannot find atom {C2_ATOM_ID!r} in the maturity map -- "
            "coverage set is undefined, guard is not evidence for the wall."
        )
    scope = matches[0].get("file_scope") or []
    if not scope:
        raise ValueError(
            f"atom {C2_ATOM_ID!r} has an empty file_scope -- the wall guard would "
            "scan nothing and pass vacuously (fail-open)."
        )
    return tuple(scope)


def _c2_file_scope_from_map() -> tuple[str, ...]:
    # The map is TWO files since 2026-08-26 and C2 sits in the closed half. Reading the live
    # half alone would raise the missing-atom ValueError above -- the guard failing CLOSED on
    # a storage change rather than a wall hole. `load_atoms` is the whole population.
    atoms = map_store.load_atoms(MAP_PATH)
    return _c2_file_scope_from_atoms(atoms)


C2_FILE_SCOPE = _c2_file_scope_from_map()

# Ground-truth property record + sim internals. A company-side belief module
# importing any of these has crossed the wall the atom exists to protect.
# `saas` broadly is NOT forbidden (the belief layer legitimately shares typed
# enums/utilities); only the ground-truth PROPERTY sources are.
_FORBIDDEN_IMPORT_PREFIXES = (
    "saas.property_model",
    "saas.customers",
    "sim",
    "simulation",
)
# Bare ground-truth constructor -- flagged even if reached via an aliased or
# indirect import (e.g. `from saas import property_model as pm; pm.build_properties`).
#
# 2026-08-18 (KNIFE3 step 35, B12): `build_properties` no longer LIVES in
# `saas.property_model` -- it moved to `simulation/dwelling_records.py`. This guard is
# strictly stronger as a result and needed no edit: the name is still forbidden here,
# and its new home is under the `simulation` prefix above, so both the module path and
# the bare name catch a company-side read of it. The prose in this file's docstring
# describing the original 2026-07-22 mutation is kept as written because it records
# what was red-teamed then, not where the symbol lives now.
_FORBIDDEN_NAMES = ("build_properties",)


def _module_matches(module: str | None) -> bool:
    if not module:
        return False
    return any(
        module == p or module.startswith(p + ".") for p in _FORBIDDEN_IMPORT_PREFIXES
    )


def _forbidden_reads_in_source(src: str, filename: str) -> list[str]:
    """Return human-readable violation strings for any ground-truth read in ``src``.

    Detection is AST-based, so comments/docstrings that merely name a forbidden
    module do not register -- only real ``import`` statements and name references.
    """
    violations: list[str] = []
    tree = ast.parse(src, filename=filename)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if _module_matches(alias.name):
                    violations.append(
                        f"{filename}:{node.lineno}: import {alias.name}"
                    )
        elif isinstance(node, ast.ImportFrom):
            # level>0 is a relative import (never crosses to saas/sim); module is None then.
            if node.level == 0 and _module_matches(node.module):
                imported = ", ".join(a.name for a in node.names)
                violations.append(
                    f"{filename}:{node.lineno}: from {node.module} import {imported}"
                )
        elif isinstance(node, ast.Name):
            if node.id in _FORBIDDEN_NAMES:
                violations.append(
                    f"{filename}:{node.lineno}: reference to {node.id}"
                )
        elif isinstance(node, ast.Attribute):
            if node.attr in _FORBIDDEN_NAMES:
                violations.append(
                    f"{filename}:{node.lineno}: attribute .{node.attr}"
                )
    return violations


@pytest.mark.parametrize("relpath", C2_FILE_SCOPE)
def test_belief_layer_file_never_reads_ground_truth_property_record(relpath):
    """Every C2 belief-layer module is free of ground-truth property reads.

    Covers home_registry.py and property_model.py -- the belief-CONSTRUCTION
    files that previously had no wall guard at all -- as well as the three
    already-scanned modules, under one CLASS-level check.
    """
    from pathlib import Path

    import company  # noqa: F401 -- anchor to locate the repo root

    repo_root = Path(company.__file__).resolve().parent.parent
    path = repo_root / relpath
    assert path.exists(), f"C2 file_scope path missing: {relpath}"
    violations = _forbidden_reads_in_source(path.read_text(), relpath)
    assert not violations, (
        "C2 wall breach -- belief-layer module reads the ground-truth property "
        "record directly (must discover via observable events instead):\n  "
        + "\n  ".join(violations)
    )


def test_guard_fires_on_injected_ground_truth_read():
    """R15 both-ways pin: the detector MUST flag the exact defect C2 prevents.

    This is the 2026-07-22 scratch mutation, captured permanently as a snippet
    so the guard's fire-on-defect property is regression-protected without
    mutating production code. If this ever passes clean, the guard is fail-silent.
    """
    mutant = (
        "from dataclasses import replace\n"
        "from saas.property_model import build_properties\n"
        "from saas.customers import CUSTOMERS\n"
        "def register_from_signup(account_id, prop):\n"
        "    gt = build_properties(CUSTOMERS)\n"
        "    if account_id in gt:\n"
        "        prop = replace(prop, epc_rating=gt[account_id]['epc_rating'])\n"
        "    return prop\n"
    )
    violations = _forbidden_reads_in_source(mutant, "home_registry.py[MUTANT]")
    # The saas.property_model import, the saas.customers import, AND the
    # build_properties call must all be caught.
    joined = "\n".join(violations)
    assert "saas.property_model" in joined
    assert "saas.customers" in joined
    assert "build_properties" in joined


def test_guard_catches_reexport_symbol_bypass_that_line_scan_misses():
    """The residual R15 gap this pass closes.

    The pre-existing per-file guard (test_c2_discovery_wired.py::
    _ground_truth_import_violations) keys on the IMPORT-LINE module string --
    it flags a line containing ``saas``/``simulation``/``sim``. A ground-truth
    read reached via a company-side RE-EXPORT of the ground-truth constructor
    (``from company.crm.<shim> import build_properties``) carries no such string
    on its import line, so the line-scan returns clean. This symbol-level AST
    check keys on the forbidden CAPABILITY (the ``build_properties`` ground-truth
    constructor) regardless of the path it arrived by, and catches it.
    """
    bypass = (
        "from company.crm.gt_shim import build_properties\n"
        "def open_belief(cust):\n"
        "    return build_properties(cust)\n"
    )
    violations = _forbidden_reads_in_source(bypass, "victim.py")
    assert any("build_properties" in v for v in violations)


def test_guard_fires_on_plain_import_of_ground_truth_module():
    """R15 subset-coverage pin: the ``ast.Import`` branch fires independently.

    The 2026-07-22 both-ways pin exercises only the ``from X import Y`` form
    (ast.ImportFrom) and the bare-call form (ast.Name). The plain
    ``import saas.property_model`` form is handled by a SEPARATE branch
    (_forbidden_reads_in_source's ``ast.Import`` handler), but was never
    exercised firing -- neutering that branch alone left the whole suite green
    (the A3/E2 subset-coverage FAIL-SILENT class: a source guard whose own half
    is not independently mutation-detectable is not evidence for the wall).

    This input is caught ONLY by the ast.Import branch: it never bare-calls or
    attribute-accesses ``build_properties``, so if that one branch is neutered
    this test reds and nothing else does.
    """
    mutant = (
        "import saas.property_model\n"
        "X = saas.property_model\n"  # attr 'property_model' is not a forbidden NAME
    )
    violations = _forbidden_reads_in_source(mutant, "home_registry.py[PLAIN-IMPORT-MUTANT]")
    assert any("import saas.property_model" in v for v in violations), violations


def test_guard_fires_on_aliased_attribute_access_bypass():
    """R15 subset-coverage pin: the ``ast.Attribute`` branch fires independently.

    ``from saas import property_model as pm`` does NOT trip the import checks --
    the module string is ``saas``, which is deliberately NOT a forbidden prefix
    (the belief layer legitimately shares saas enums). The ONLY thing standing
    between that alias and a ground-truth read is the ``ast.Attribute`` branch
    catching ``pm.build_properties(...)``. The module docstring explicitly
    ADVERTISES this bypass as caught ("...reached via an aliased or indirect
    import (e.g. ``from saas import property_model as pm; pm.build_properties``)"),
    yet neutering that branch alone left the whole suite green -- the advertised
    capability was unproven. This pins it: reds exactly the ast.Attribute
    mutation and nothing else.
    """
    bypass = (
        "from saas import property_model as pm\n"
        "def open_belief(cust):\n"
        "    return pm.build_properties(cust)\n"
    )
    violations = _forbidden_reads_in_source(bypass, "home_registry.py[ALIAS-ATTR-MUTANT]")
    assert any("build_properties" in v for v in violations), violations


def test_coverage_set_is_sourced_from_the_live_map_not_a_hardcoded_copy():
    """R15 anti-drift pin: the scanned set == C2's live file_scope in the map.

    This is the fix for the "full-key-set" fail-silent class (recurred twice on
    E4): a belief-layer module added to C2's file_scope in maturity_map.yaml is
    scanned automatically, with no second list to remember to update. If the
    guard is ever reverted to a hardcoded tuple that drifts from the map, this
    assertion fires.
    """
    atoms = map_store.load_atoms(MAP_PATH)
    map_scope = _c2_file_scope_from_atoms(atoms)
    assert set(C2_FILE_SCOPE) == set(map_scope)
    assert len(C2_FILE_SCOPE) >= 1
    # Every declared belief-layer file must actually exist and be scannable --
    # a file_scope entry pointing at a missing file is itself a wall hole.
    repo_root = MAP_PATH.parents[2]
    for rel in C2_FILE_SCOPE:
        assert (repo_root / rel).exists(), f"C2 file_scope path missing: {rel}"


def test_loader_fails_loud_when_atom_missing():
    """R15 fail-open pin (missing atom): loader must RAISE, never return empty.

    An unavailable coverage set is a failed guard, not a passing one. If the C2
    atom vanished from the map (rename/delete), the guard must break loudly
    rather than silently parametrize over nothing.
    """
    with pytest.raises(ValueError):
        _c2_file_scope_from_atoms([{"id": "SOME_OTHER_ATOM", "file_scope": ["x.py"]}])


def test_loader_fails_loud_when_file_scope_empty():
    """R15 fail-open pin (empty scope): an empty file_scope must RAISE.

    Otherwise the parametrized scan would collect zero cases and pass vacuously
    -- the classic FAIL-OPEN-on-empty pattern.
    """
    with pytest.raises(ValueError):
        _c2_file_scope_from_atoms([{"id": C2_ATOM_ID, "file_scope": []}])


def test_guard_does_not_false_positive_on_docstring_mention():
    """AST-based, so a docstring/comment naming the module is NOT a violation.

    Several C2 modules legitimately reference saas/property_model.py in prose to
    explain what they must NOT read; that must stay clean.
    """
    benign = (
        '"""This module never reads saas.property_model / saas.customers,\n'
        "nor calls build_properties -- it discovers via events. See sim too.\"\"\"\n"
        "# import simulation would be a violation, but this comment is not\n"
        "X = 1\n"
    )
    assert _forbidden_reads_in_source(benign, "benign.py") == []
