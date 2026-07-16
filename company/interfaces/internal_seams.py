"""Typed internal seams between the company's core financial domains (ARCH1).

The company's money-handling logic lives in four conceptual domains:

    PRICING     -> what a unit of energy is sold for (tariffs, price cap, ToU)
    BILLING     -> turning consumption + price into invoices and payments
    SETTLEMENT  -> reconciling metered/settled volumes and cost to the market
    COLLECTIONS -> pursuing overdue balances (arrears, debt referral, PPM debt)

In a real supplier these are *separate systems with separate owners* that talk
through defined interfaces, not by reaching into each other's tables. We model
the same discipline INTERNALLY, enforced the same way the SIM/company epistemic
wall is enforced (a static verifier): a domain may only cross into another
domain through the **typed, versioned messages declared here** -- never by
importing the other domain's internal modules directly.

This is the internal analogue of ``company/interfaces/sim_interface.py`` and the
typed-flow-seam preference (CLAUDE.md): new boundary crossings prefer a typed,
versioned-message adapter over a direct call, so the boundary is the seam a real
integration would swap behind.

WHY the domains do not map 1:1 to directories today (declared architectural
debt, not hidden):
  * COLLECTIONS currently lives *inside* ``company/billing/`` (collections.py,
    debt_referral.py, ppm_debt_loading.py) rather than as its own package.
  * SETTLEMENT logic is embedded in ``company/market/`` (imbalance_ledger.py,
    bm_unit_log.py, mhhs_tracker.py) rather than a ``company/settlement/``
    package.
``DOMAIN_PATHS`` records where each domain's code *actually* lives so the seam
verifier can enforce the boundary in place, without first requiring a large
package move. Moving them to top-level packages is future work (a higher level
of this atom); the boundary is enforceable now.

Enforcement lives in ``tools/internal_seam_verifier.py`` and is mutation-tested
(R15: a control that cannot fail is worse than none).
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from datetime import date


class Domain(enum.Enum):
    """The four core financial domains guarded by the internal seam."""

    PRICING = "pricing"
    BILLING = "billing"
    SETTLEMENT = "settlement"
    COLLECTIONS = "collections"


# ---------------------------------------------------------------------------
# Where each domain's code actually lives, most-specific-first.
#
# The verifier classifies a file into a domain by walking this list IN ORDER
# and taking the first prefix/exact-path that matches. COLLECTIONS files sit
# inside company/billing/, so they MUST be listed before the BILLING directory
# prefix or they would be mis-classified as BILLING.
#
# Each entry is (Domain, matcher). A matcher ending in "/" is a directory
# prefix; otherwise it is an exact repo-relative file path.
# ---------------------------------------------------------------------------
DOMAIN_PATHS: list[tuple[Domain, str]] = [
    # COLLECTIONS -- embedded in company/billing/ today (declared debt).
    (Domain.COLLECTIONS, "company/billing/collections.py"),
    (Domain.COLLECTIONS, "company/billing/debt_referral.py"),
    (Domain.COLLECTIONS, "company/billing/ppm_debt_loading.py"),
    # SETTLEMENT -- embedded in company/market/ today (declared debt).
    (Domain.SETTLEMENT, "company/market/imbalance_ledger.py"),
    (Domain.SETTLEMENT, "company/market/bm_unit_log.py"),
    (Domain.SETTLEMENT, "company/market/mhhs_tracker.py"),
    # BILLING -- everything else under company/billing/.
    (Domain.BILLING, "company/billing/"),
    # PRICING -- company/pricing/.
    (Domain.PRICING, "company/pricing/"),
]

# The one module every domain is allowed to import across the boundary: this
# seam. Analogue of sim_interface.APPROVED_SEAM.
APPROVED_SEAM_MODULE = "company.interfaces.internal_seams"


# ---------------------------------------------------------------------------
# Baseline allowlist: cross-domain imports that PRE-DATE the seam.
#
# CLAUDE.md doctrine (typed-flow-seam preference, portability/scale-readiness
# addenda): do NOT retrofit already-shipped code speculatively -- apply at next
# real touch, log the gap as debt otherwise. These crossings are that debt,
# registered here explicitly so the verifier fails-closed on NEW violations
# without a big-bang refactor. Every entry carries a reason (no silent
# allowlisting -- a silent cap reads as "clean" when it isn't).
#
# Key: (importing_file_repo_relpath, imported_module_prefix) -> reason.
# The verifier allows an import if the imported module starts with the prefix.
# ---------------------------------------------------------------------------
BASELINE_ALLOWLIST: dict[tuple[str, str], str] = {
    (
        "company/pricing/switching_recommendation.py",
        "company.billing.contract",
    ): (
        "PRICING->BILLING: switching advice reads contract/renewal summary. "
        "Pre-seam debt; remediate-on-touch to a typed seam message."
    ),
    (
        "company/billing/collections.py",
        "company.billing.invoice",
    ): (
        "COLLECTIONS->BILLING: collections shares billing's invoice DB "
        "schema/path (DEFAULT_DB_PATH, create_schema). Pre-seam debt; "
        "remediate-on-touch."
    ),
}


# ---------------------------------------------------------------------------
# Typed, versioned seam messages -- the ONLY sanctioned way a domain hands
# state to another domain. Each is frozen (immutable) and carries a
# schema_version so the wire contract is explicit and evolvable (C-S3:
# request/response are events in time; portability: no counterparty hardcoded).
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PriceCardIssued:
    """PRICING -> BILLING. The effective tariff billing must bill against.

    Billing bills against THIS; it must not reach into pricing internals to
    re-derive rates (that would couple billing to the price-cap / ToU engine).
    """

    SCHEMA_VERSION = "1.0.0"

    account_id: str
    tariff_code: str
    unit_rate_gbp_per_mwh: float
    standing_charge_gbp_per_day: float
    effective_from: date
    schema_version: str = SCHEMA_VERSION


@dataclass(frozen=True)
class SettlementPosition:
    """SETTLEMENT -> BILLING. Settled volume/cost feeding cost-to-serve.

    The settlement run type (e.g. 'SF', 'R1', 'R2', 'R3', 'RF') is carried so
    billing knows how firm the position is -- initial vs reconciliation runs.
    """

    SCHEMA_VERSION = "1.0.0"

    account_id: str
    settlement_date: date
    settled_volume_mwh: float
    settled_cost_gbp: float
    run_type: str
    schema_version: str = SCHEMA_VERSION


@dataclass(frozen=True)
class OverdueInvoiceReferred:
    """BILLING -> COLLECTIONS. An overdue invoice handed to collections."""

    SCHEMA_VERSION = "1.0.0"

    account_id: str
    invoice_id: str
    amount_outstanding_gbp: float
    due_date: date
    days_overdue: int
    schema_version: str = SCHEMA_VERSION


class CollectionsResult(enum.Enum):
    PAYMENT_PLAN = "payment_plan"
    PAID = "paid"
    WRITTEN_OFF = "written_off"
    REFERRED_DCA = "referred_dca"  # referred to a debt collection agency


@dataclass(frozen=True)
class CollectionsOutcome:
    """COLLECTIONS -> BILLING. Outcome of a collections action on an account."""

    SCHEMA_VERSION = "1.0.0"

    account_id: str
    invoice_id: str
    outcome: CollectionsResult
    amount_recovered_gbp: float
    schema_version: str = SCHEMA_VERSION


# Registry of sanctioned directed seam messages: (source, target, message).
# The verifier does not (yet) enforce that crossings USE these -- that is a
# higher level of this atom -- but declaring them fixes the target contract and
# lets callers depend on a stable type instead of a foreign domain's internals.
SEAM_MESSAGES: list[tuple[Domain, Domain, type]] = [
    (Domain.PRICING, Domain.BILLING, PriceCardIssued),
    (Domain.SETTLEMENT, Domain.BILLING, SettlementPosition),
    (Domain.BILLING, Domain.COLLECTIONS, OverdueInvoiceReferred),
    (Domain.COLLECTIONS, Domain.BILLING, CollectionsOutcome),
]


def classify_path(repo_relpath: str) -> Domain | None:
    """Classify a repo-relative file path into a Domain, or None if it is not
    part of any guarded domain. Most-specific match wins (see DOMAIN_PATHS)."""

    p = repo_relpath.replace("\\", "/")
    for domain, matcher in DOMAIN_PATHS:
        if matcher.endswith("/"):
            if p.startswith(matcher):
                return domain
        elif p == matcher:
            return domain
    return None


def module_to_relpath(module: str) -> str:
    """Map a dotted module ('company.billing.invoice') to its repo-relative
    .py path ('company/billing/invoice.py'). Package imports
    ('company.billing') map to the package __init__ path for classification."""

    return module.replace(".", "/") + ".py"
