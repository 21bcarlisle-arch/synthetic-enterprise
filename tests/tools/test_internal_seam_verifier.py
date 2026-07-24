"""Tests for the ARCH1 internal seam verifier.

Covers, per R15 (a control must be able to FAIL):
  * the current tree PASSES (no false positives on shipped code),
  * MUTATION: a freshly planted cross-domain import is FLAGGED,
  * FAIL-CLOSED: an unreadable/unparseable file raises, never silently passes,
  * the seam contracts are well-formed (versioned, no silent baseline entries).
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from company.interfaces import internal_seams as seams
from tools import internal_seam_verifier as verifier

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


# --------------------------------------------------------------------------
# The control does its job on the real tree.
# --------------------------------------------------------------------------
def test_current_tree_passes():
    """No NEW cross-domain violations on the shipped tree (the two pre-seam
    crossings are documented in BASELINE_ALLOWLIST)."""
    violations = verifier.verify(verifier._all_domain_files())
    assert violations == [], "\n".join(str(v) for v in violations)


# --------------------------------------------------------------------------
# R15 MUTATION: the control fires on its own named defect.
# --------------------------------------------------------------------------
def test_mutation_planted_cross_domain_import_is_flagged(tmp_path, monkeypatch):
    """Plant a PRICING file that imports BILLING internals NOT in the baseline;
    the verifier MUST flag it. If this ever passes, the control is dead."""
    # A pricing file (classified PRICING via the company/pricing/ prefix) that
    # reaches directly into billing internals -- exactly what the seam forbids.
    planted = REPO_ROOT / "company" / "pricing" / "_seam_mutation_probe.py"
    planted.write_text(
        textwrap.dedent(
            """\
            from company.billing.payments import reconcile_payment  # noqa
            """
        ),
        encoding="utf-8",
    )
    try:
        violations = verifier.check_file(planted)
    finally:
        planted.unlink()

    assert len(violations) == 1
    v = violations[0]
    assert v.importing_domain == "pricing"
    assert v.imported_domain == "billing"
    assert v.imported_module == "company.billing.payments"


@pytest.mark.parametrize(
    "import_line, expected_module, expected_domain",
    [
        # `from PKG import submodule` -- module string is the bare package
        # `company.billing`, whose file-form `company/billing.py` matched no
        # DOMAIN_PATHS entry, so this crossing was previously INVISIBLE
        # (a FAIL-OPEN gap, R15). It must now be flagged.
        ("from company.billing import invoice", "company.billing", "billing"),
        # ... and resolved to the SPECIFIC domain when the name is a submodule
        # that lives in a different domain (collections inside billing/).
        (
            "from company.billing import collections",
            "company.billing.collections",
            "collections",
        ),
        # plain `import PKG` of a guarded package directory.
        ("import company.billing", "company.billing", "billing"),
    ],
)
def test_mutation_package_form_cross_domain_import_is_flagged(
    import_line, expected_module, expected_domain
):
    """R15 regression: the package-import forms that previously slipped past
    classify_path's file-only matching are now caught. A pricing file reaching
    into billing/collections via any of these forms MUST be flagged."""
    planted = REPO_ROOT / "company" / "pricing" / "_seam_pkgform_probe.py"
    planted.write_text(import_line + "  # noqa\n", encoding="utf-8")
    try:
        violations = verifier.check_file(planted)
    finally:
        planted.unlink()
    assert len(violations) == 1, [str(v) for v in violations]
    v = violations[0]
    assert v.importing_domain == "pricing"
    assert v.imported_domain == expected_domain
    assert v.imported_module == expected_module


def test_classify_module_resolves_package_form():
    """Unit-level guard for the resolver that closes the gap: a bare guarded
    package classifies to its domain (file-only classify_path returns None)."""
    assert seams.classify_path(seams.module_to_relpath("company.billing")) is None
    assert seams.classify_module("company.billing") is seams.Domain.BILLING
    assert seams.classify_module("company.pricing") is seams.Domain.PRICING
    # A specific submodule still resolves most-specifically.
    assert seams.classify_module("company.billing.collections") is seams.Domain.COLLECTIONS
    # A non-guarded package is still None.
    assert seams.classify_module("company.trading") is None


def test_mutation_removing_baseline_entry_reintroduces_violation():
    """Independence check: the real pricing->billing crossing is a violation
    when NOT allowlisted -- proving the baseline is what suppresses it, and the
    detector itself is live."""
    target = REPO_ROOT / "company" / "pricing" / "switching_recommendation.py"
    key = (
        "company/pricing/switching_recommendation.py",
        "company.billing.contract",
    )
    saved = seams.BASELINE_ALLOWLIST.pop(key)
    try:
        violations = verifier.check_file(target)
        assert any(
            v.imported_module.startswith("company.billing.contract")
            for v in violations
        ), "detector did not fire once the baseline entry was removed"
    finally:
        seams.BASELINE_ALLOWLIST[key] = saved
    # And it is suppressed again with the entry restored.
    assert verifier.check_file(target) == []


# --------------------------------------------------------------------------
# R15 MUTATION: the baseline allowlist matches on a dotted-component boundary,
# not a raw string prefix -- a sibling module sharing the prefix is NOT
# silently grandfathered (that would widen the seam past the one named crossing
# and re-open the fail-closed guarantee).
# --------------------------------------------------------------------------
def test_baseline_does_not_over_permit_sibling_prefix():
    """The pricing->billing baseline grandfathers `company.billing.contract`.
    A crossing into a SIBLING that merely shares the string prefix
    (`company.billing.contract_termination`, `company.billing.contractZZZ`) is a
    NEW, undocumented crossing and MUST NOT be allowed -- only the exact module
    and its true submodules are baseline-covered."""
    f = "company/pricing/switching_recommendation.py"
    # The documented crossing and its submodules ARE allowed.
    assert verifier._is_baseline_allowed(f, "company.billing.contract")
    assert verifier._is_baseline_allowed(f, "company.billing.contract.renewal_summary")
    # String-prefix siblings are NOT (this returned True before the fix).
    assert not verifier._is_baseline_allowed(f, "company.billing.contract_termination")
    assert not verifier._is_baseline_allowed(f, "company.billing.contractZZZ")


def test_mutation_sibling_prefix_crossing_is_flagged_end_to_end(monkeypatch):
    """End-to-end through check_file, with the baseline genuinely IN PLAY for the
    probed file (a monkeypatched entry keyed to the probe path). The documented
    crossing `company.billing.contract` is grandfathered, but a sibling
    (`company.billing.contract_settlement`) is a NEW undocumented crossing and
    MUST still be flagged. Under the loose-prefix bug the sibling was swallowed
    by the baseline and check_file returned [] -- this test would have RED then."""
    probe_rel = "company/pricing/_seam_sibling_probe.py"
    monkeypatch.setitem(
        seams.BASELINE_ALLOWLIST,
        (probe_rel, "company.billing.contract"),
        "TEST baseline entry: grandfathers company.billing.contract only.",
    )
    planted = REPO_ROOT / "company" / "pricing" / "_seam_sibling_probe.py"
    # Two crossings: the grandfathered one (must be silent) and its sibling
    # sharing the string prefix (must be flagged despite the baseline).
    planted.write_text(
        "from company.billing.contract import renewal_summary  # noqa\n"
        "from company.billing.contract_settlement import settle  # noqa\n",
        encoding="utf-8",
    )
    try:
        violations = verifier.check_file(planted)
    finally:
        planted.unlink()
    assert len(violations) == 1, [str(v) for v in violations]
    v = violations[0]
    assert v.importing_domain == "pricing"
    assert v.imported_domain == "billing"
    assert v.imported_module == "company.billing.contract_settlement"


# --------------------------------------------------------------------------
# Fail-closed, not fail-open / fail-silent.
# --------------------------------------------------------------------------
def test_unparseable_file_raises_not_passes(tmp_path):
    """A file that cannot be parsed must RAISE (fail-closed), never return []
    silently. classify_path needs a domain path, so probe within a domain."""
    bad = REPO_ROOT / "company" / "pricing" / "_seam_badsyntax_probe.py"
    bad.write_text("def (:\n", encoding="utf-8")  # invalid syntax
    try:
        with pytest.raises(SyntaxError):
            verifier.check_file(bad)
    finally:
        bad.unlink()


def test_non_domain_file_is_ignored():
    """A file outside the four domains classifies to None and is skipped."""
    assert seams.classify_path("company/trading/gas_market_monitor.py") is None
    assert seams.classify_path("tools/internal_seam_verifier.py") is None


# --------------------------------------------------------------------------
# Domain classification: most-specific-first (collections inside billing).
# --------------------------------------------------------------------------
def test_collections_files_classify_as_collections_not_billing():
    assert seams.classify_path("company/billing/collections.py") is seams.Domain.COLLECTIONS
    assert seams.classify_path("company/billing/debt_referral.py") is seams.Domain.COLLECTIONS
    assert seams.classify_path("company/billing/ppm_debt_loading.py") is seams.Domain.COLLECTIONS
    # A plain billing file stays BILLING.
    assert seams.classify_path("company/billing/invoice.py") is seams.Domain.BILLING


def test_settlement_files_classify_as_settlement():
    assert seams.classify_path("company/market/imbalance_ledger.py") is seams.Domain.SETTLEMENT
    assert seams.classify_path("company/market/bm_unit_log.py") is seams.Domain.SETTLEMENT
    # A non-settlement market file is not a guarded domain.
    assert seams.classify_path("company/market/rate_comparison.py") is None


# --------------------------------------------------------------------------
# Seam contracts are well-formed.
# --------------------------------------------------------------------------
def test_every_seam_message_is_versioned():
    for _src, _dst, msg in seams.SEAM_MESSAGES:
        assert hasattr(msg, "SCHEMA_VERSION")
        assert isinstance(msg.SCHEMA_VERSION, str) and msg.SCHEMA_VERSION


def test_seam_messages_cover_the_four_domains():
    domains_touched = set()
    for src, dst, _msg in seams.SEAM_MESSAGES:
        domains_touched.add(src)
        domains_touched.add(dst)
    assert domains_touched == set(seams.Domain)


def test_no_silent_baseline_entries():
    """Every allowlisted crossing carries a non-empty reason (no silent cap)."""
    for key, reason in seams.BASELINE_ALLOWLIST.items():
        assert isinstance(reason, str) and reason.strip(), key


def test_baseline_entries_are_real_crossings():
    """Each baseline entry must actually correspond to a cross-domain import in
    the tree -- a stale allowlist entry would silently widen the seam."""
    for (file_rel, module_prefix) in seams.BASELINE_ALLOWLIST:
        importing_domain = seams.classify_path(file_rel)
        imported_domain = seams.classify_path(seams.module_to_relpath(module_prefix))
        assert importing_domain is not None, file_rel
        assert imported_domain is not None, module_prefix
        assert importing_domain != imported_domain, (file_rel, module_prefix)
