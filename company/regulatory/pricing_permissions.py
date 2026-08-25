"""What this supplier's own reading of the licence lets it differentiate a price on.

REUSE: company/regulatory/pricing_permissions.py
CLASS: CUSTOM
INDEX: searched "obligation", "licence", "SLC", "compliance", "permission", "consumer duty",
       "ability to pay". `company/compliance/obligations_register.py` came back and is the
       closest sibling -- it is NOT this and is deliberately not extended. That register
       risk-TIERS obligations for a compliance function: impact x likelihood, which control,
       how often tested. This answers a different question that nothing answered:
       MAY THIS PRICE BE OFFERED. `company/billing/disconnection_warning.py` already owns the
       SLC 27 warning sequence and is untouched. `company/regulatory/statutory_obligations.py`
       was read and covers statutory duties, not pricing latitude.

WHY IT EXISTS. Director, 2026-08-25: *"Establish what's actually allowed rather than assuming,
and use the sources ... Record what is explicitly permitted, what is prohibited, and what is
tolerated-but-unwritten, with citations. That register is what the pricing arm should be
constrained by -- not my recollection and not yours."*

THE TEXT IS IN THE COMMONS, THE READING IS HERE, and that split is the regulation-commons
doctrine rather than a filing preference. `docs/domain_artefact_library/regulatory/
pricing_differentiation_permissions.md` carries the licence text verbatim with its citations,
readable by every lane because law is published in reality. This module is the COMPANY's reading
of it -- a supplier's own compliance interpretation, which a real supplier owns, is free to get
wrong, and gets fined for getting wrong. The world is free to read the same text differently.

WHAT THE SOURCES ACTUALLY SAID, and it moved the pricing arm in the director's direction rather
than mine. I had imposed a floor: never price a household in payment difficulty above the flat
rule. Reading SLC 27 shows that is a stronger rule than the text supports.

  * SLC 27.8 -- "must take all reasonable steps to ascertain the Domestic Customer's ability to
    pay and must take this into account when CALCULATING INSTALMENTS". It is a debt-repayment
    duty. It does not govern the unit rate, and reading it as though it did is the assumption
    the director told me to stop making.
  * SLC 27.2A -- a payment-method difference "shall reflect the costs to the supplier of the
    different payment methods". Explicitly PERMITTED, and two-sided: as much a ceiling on a
    direct-debit discount as on a prepayment premium.
  * SLC 7.4 -- the one real margin test, and it has a COMPARATOR: a deemed-contract class whose
    revenue "significantly exceeds the licensee's costs ... by significantly more than the
    licensee's revenue exceeds its costs of supplying ... the generality of its ... Customers"
    is unduly onerous.
  * SLC 27.8A(a)(ii) -- credit management must link "staff incentives to successful customer
    outcomes not the value of repayment rates". Written for humans; it applies with more force
    to an optimiser, which is a staff incentive with no discretion.

So the floor goes and the constraints that are actually in the text arrive.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

COMMONS_ARTEFACT = (
    Path(__file__).resolve().parent.parent.parent
    / "docs" / "domain_artefact_library" / "regulatory"
    / "pricing_differentiation_permissions.md"
)

#: SLC 7.4 says "significantly" and does not define it. THIS NUMBER IS THIS LANE'S READING AND
#: NOT THE LAW, and it is named so that a reader can disagree with the reading without having to
#: disagree with the licence. Two times the book's general margin is chosen because the test is
#: comparative and doubling is the smallest multiple a reasonable person would call significant;
#: Ofgem has published no threshold and none was found.
#:
#: A LOWER number would be safer for the company and is not therefore better: an over-tight
#: reading of a comparative test makes every differentiated price look unlawful, which would
#: quietly reinstate the flat rule under a compliance banner.
UNDULY_ONEROUS_CLASS_MARGIN_MULTIPLE = 2.0

#: Late Payment of Commercial Debts (Interest) Act 1998, as set by the Rate of Interest (No. 3)
#: Order 2002: the Bank of England official dealing rate "plus 8 per cent". NON-DOMESTIC ONLY --
#: the Act reaches qualifying COMMERCIAL debts and no further.
STATUTORY_INTEREST_OVER_BASE = 0.08

#: s.5A fixed compensation for recovery costs, by debt size. Statutory and non-excludable.
STATUTORY_RECOVERY_SUMS_GBP = ((1_000.0, 40.0), (10_000.0, 70.0), (float("inf"), 100.0))

#: Segments the 1998 Act reaches. A domestic customer is not a commercial debtor and no
#: affirmative permission to charge them late-payment interest was found anywhere in the licence.
COMMERCIAL_DEBT_SEGMENTS = ("SME", "I&C")


class PricingNotPermitted(Exception):
    """The offer would breach this supplier's own reading of the licence. Raised, never
    downgraded to a warning -- a compliance check that returns a flag nobody reads is the
    fail-open pattern with a regulator on the other end."""


@dataclass(frozen=True)
class PermissionVerdict:
    """Whether an offer may be made, and which condition decided it."""

    permitted: bool
    condition: str | None = None
    reason: str | None = None


def statutory_recovery_sum_gbp(debt_gbp: float, segment: str) -> float:
    """The fixed sum recoverable on a late commercial debt, or 0.0 where the Act does not reach.

    Returns ZERO for a domestic customer rather than raising, because "no entitlement" is a real
    and common answer here -- but it is zero for a stated reason and not by omission: the Act
    covers qualifying commercial debts (s.1), and nothing read in the supply licence gives a
    supplier an equivalent domestic entitlement.
    """
    if segment not in COMMERCIAL_DEBT_SEGMENTS:
        return 0.0
    for ceiling, amount in STATUTORY_RECOVERY_SUMS_GBP:
        if debt_gbp < ceiling:
            return amount
    return STATUTORY_RECOVERY_SUMS_GBP[-1][1]


def statutory_interest_rate(base_rate: float, segment: str) -> float:
    """Base + 8% for a commercial debtor, 0.0 for a domestic one. Same reasoning as above."""
    if segment not in COMMERCIAL_DEBT_SEGMENTS:
        return 0.0
    return float(base_rate) + STATUTORY_INTEREST_OVER_BASE


def check_payment_method_difference(
    *, difference_gbp_per_mwh: float, cost_difference_gbp_per_mwh: float,
    tolerance_gbp_per_mwh: float = 0.25,
) -> PermissionVerdict:
    """SLC 27.2A: a price difference between payment methods must REFLECT the cost difference.

    TWO-SIDED ON PURPOSE. The obvious reading is "do not overcharge prepayment", and that is only
    half of it: a direct-debit discount larger than the cost saving is the same breach with the
    sign flipped, and it is the one a supplier is tempted into. The check is on the MAGNITUDE of
    the gap between the price difference and the cost difference, in either direction.

    `tolerance` exists because "reflect" is not "equal" and a rounded tariff is not a breach.
    """
    gap = abs(float(difference_gbp_per_mwh) - float(cost_difference_gbp_per_mwh))
    if gap <= tolerance_gbp_per_mwh:
        return PermissionVerdict(True, "SLC 27.2A")
    return PermissionVerdict(
        False, "SLC 27.2A",
        "a payment-method price difference of {:.2f} GBP/MWh against a cost difference of "
        "{:.2f} does not reflect the cost of the payment methods ({:+.2f} unexplained). SLC "
        "27.2B makes price a 'term' for this purpose.".format(
            difference_gbp_per_mwh, cost_difference_gbp_per_mwh,
            difference_gbp_per_mwh - cost_difference_gbp_per_mwh),
    )


def check_class_margin(
    *, class_margin_gbp_per_mwh: float, book_general_margin_gbp_per_mwh: float | None,
    is_deemed_contract: bool,
    multiple: float = UNDULY_ONEROUS_CLASS_MARGIN_MULTIPLE,
) -> PermissionVerdict:
    """SLC 7.3/7.4: deemed-contract terms must not be unduly onerous, judged against the book.

    THE COMPARATOR IS THE POINT and it is why this is not a price cap. SLC 7.4 does not forbid a
    high margin; it forbids a CLASS margin significantly above what the licensee earns from "the
    generality" of its customers, on a DEEMED contract. A supplier whose whole book earns a wide
    margin is not caught by it; one that singles out a class is.

    NOT APPLIED TO A NEGOTIATED CONTRACT, because the condition does not reach one. That is a
    real difference in the law and flattening it would be inventing an obligation -- the same
    error, in the opposite direction, as the floor this replaces.

    UNKNOWN COMPARATOR IS NOT PERMISSION. With no book margin to compare against, the test cannot
    run, and an unavailable check is a FAILED check (R15) -- not a quiet pass.
    """
    if not is_deemed_contract:
        return PermissionVerdict(True, "SLC 7.4", "not a deemed contract; the condition does not reach it")
    if book_general_margin_gbp_per_mwh is None:
        return PermissionVerdict(
            False, "SLC 7.4",
            "the book's general margin is unknown, so the comparative test in SLC 7.4 cannot be "
            "run. An unavailable compliance check is a failed one, never a permission.",
        )
    if book_general_margin_gbp_per_mwh <= 0.0:
        return PermissionVerdict(
            False, "SLC 7.4",
            "the book's general margin is {:.2f} GBP/MWh, so the comparative test has no "
            "denominator and any class margin would pass it".format(book_general_margin_gbp_per_mwh),
        )
    ratio = class_margin_gbp_per_mwh / book_general_margin_gbp_per_mwh
    if ratio <= multiple:
        return PermissionVerdict(True, "SLC 7.4")
    return PermissionVerdict(
        False, "SLC 7.4",
        "a deemed-contract class margin of {:.2f} GBP/MWh is {:.1f}x the book's general margin "
        "of {:.2f}. SLC 7.4 makes a class margin that exceeds costs by significantly more than "
        "the generality of customers unduly onerous; {:.1f}x is this lane's reading of "
        "'significantly' and is not itself the law.".format(
            class_margin_gbp_per_mwh, ratio, book_general_margin_gbp_per_mwh, multiple),
    )


#: The boundary this module refuses to cross, stated as code so it cannot be forgotten.
INSTALMENTS_ARE_NOT_PRICED_HERE = (
    "SLC 27.8 governs how a DEBT is repaid -- the instalment amount -- and requires the "
    "supplier to ascertain and use the customer's ability to pay. It does not govern the unit "
    "rate, and this module deliberately offers no function that would set a repayment amount. "
    "SLC 27.8A(a)(ii) is the reason to keep it that way: credit management must link incentives "
    "to 'successful customer outcomes not the value of repayment rates', and an optimiser is a "
    "staff incentive with no discretion to ignore it."
)
