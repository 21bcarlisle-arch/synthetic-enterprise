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
"""
import ast

import pytest

# C2's file_scope (maturity_map.yaml, atom C2_discovery_through_interfaces).
# These are the belief-layer modules that must build property beliefs ONLY from
# observable events, never from a direct ground-truth read. A new belief-layer
# module added to C2's file_scope must be added here too (the guard is a class
# guard over this list, not a per-file assertion).
C2_FILE_SCOPE = (
    "company/crm/property_model.py",
    "company/crm/property_discovery.py",
    "company/crm/home_registry.py",
    "company/crm/onboarding_journey.py",
    "company/crm/decarb_recommender.py",
)

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
    import company  # noqa: F401 -- anchor to locate the repo root

    from pathlib import Path

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
