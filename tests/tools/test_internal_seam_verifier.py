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
