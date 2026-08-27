"""The support bound is DOMESTIC, and it is applied to every segment. This is the tripwire.

`value_based_renewal.max_supported_rate_increase_pct()` derives the largest price step the
company's churn belief has evidence for from **the Ofgem DOMESTIC cap's own largest step**
(+83.1%, 1 Oct 2022). Every sentence of its justification is domestic: GB domestic switching
behaviour, a domestic cap, domestic customers never having been observed responding to a bigger
one-step rise.

`decide_margin` applies it to whatever it is handed. SME and I&C are not on the domestic cap, and
`company/crm/churn_model.py` branches them to a different curve entirely -- `IC_BASE_CHURN_RATE`
0.20 against 0.10, `IC_RATE_SENSITIVITY` 1.5 against 0.8, and no bill-stress term. The bound
defends nothing about a business account.

WHY IT IS LEFT APPLIED, and why this file is a threshold rather than a fix. Measured 2026-08-27:
the served book is 417 resi and 2 SME, with no I&C at all while the director's suspension stands.
At 0.5% both alternatives are worse than the flaw. Refusing non-domestic accounts would raise
`MarginDecisionUnavailable` on every SME renewal -- removing two real accounts from the arm to
fix a category error affecting two real accounts. Inventing a non-domestic frontier would be the
picked number that function exists not to be: there is no non-domestic Ofgem cap to derive from,
because the 2022 non-domestic intervention was a SUBSIDY and not a cap, so the shared commons
artefact does not carry the step the derivation needs.

WHAT THIS FILE IS FOR. An accepted limitation that nothing measures is how a 0.5% exposure
becomes a 20% one without anybody deciding to let it. This reds when the non-domestic share of
the priceable book grows, and the remedy in its message is to derive a non-domestic bound -- NOT
to raise the threshold.

It also reds if the SUSPENSION LIFTS: I&C returning puts five large accounts, whose churn curve
is the one the domestic evidence least describes, straight under a domestic bound.
"""
from __future__ import annotations

import pytest

from company.crm.churn_model import IC_SEGMENT, RESI_SEGMENT, SME_SEGMENT
from company.pricing.value_based_renewal import max_supported_rate_increase_pct

#: The share of the priceable book that may sit under a bound derived from domestic evidence
#: while that remains an accepted limitation rather than a defect. Measured at 0.5% on
#: 2026-08-27 (2 SME of 419). Set well above it so ordinary churn does not trip the wire, and
#: far below the point at which "a rounding error on the edge of the book" stops being true.
MAX_NON_DOMESTIC_SHARE_UNDER_A_DOMESTIC_BOUND = 0.05

#: I&C separately, and as a COUNT not a share: these accounts are individually enormous (one was
#: 3.9 GWh), so five of them is not five rounding errors even at 1% of headcount. Zero while the
#: director's 2026-08-24 suspension stands.
MAX_INDUSTRIAL_ACCOUNTS_UNDER_A_DOMESTIC_BOUND = 0


def _priceable_book():
    """Electricity accounts the arm can actually price, by segment.

    Electricity only: the renewal desk prices the supply point that carries the contract, and a
    gas leg is billed under the same account (`test_the_two_legs_are_one_billing_account`).
    Counting legs would double every dual-fuel home and dilute the very share this measures.
    """
    from simulation.live_population import live_population
    return [c for c in live_population() if c.get("commodity") == "electricity"]


def test_the_bound_really_is_derived_from_the_domestic_cap():
    """Non-vacuity. If this ever stops being the domestic step, the whole premise of this file
    changes and it should be rewritten rather than left asserting a threshold about nothing."""
    from company.pricing.ofgem_price_cap import _CAP_WINDOWS

    steps, previous = [], None
    for window in _CAP_WINDOWS:
        level = window.get("elec")
        if previous and level:
            steps.append(100.0 * (level - previous) / previous)
        previous = level or previous
    assert max_supported_rate_increase_pct() == pytest.approx(max(steps))
    assert max(steps) > 50.0, (
        "the largest published domestic cap step is now {:.1f}% -- if the schedule no longer "
        "carries the 2022 move, this bound is derived from something else".format(max(steps)))


def test_the_non_domestic_share_under_a_domestic_bound_stays_small():
    """THE TRIPWIRE. Derive a non-domestic bound; do not raise the threshold."""
    book = _priceable_book()
    assert book, "no priceable electricity accounts -- this measure is vacuous"
    non_domestic = [c for c in book if c.get("segment") != RESI_SEGMENT]
    share = len(non_domestic) / len(book)
    assert share <= MAX_NON_DOMESTIC_SHARE_UNDER_A_DOMESTIC_BOUND, (
        "{:.1%} of the priceable book ({} of {}) is non-domestic and is being priced under a "
        "bound derived from the Ofgem DOMESTIC cap, which defends nothing about a business "
        "account. Derive a non-domestic bound -- do NOT raise this threshold."
        .format(share, len(non_domestic), len(book)))


def test_no_industrial_account_sits_under_the_domestic_bound():
    """The suspension is what keeps this true, so this reds the day it lifts.

    That is the intent, not a nuisance: I&C accounts are individually enormous and their churn
    curve is the one the domestic evidence least describes. Un-suspending them without deriving
    a non-domestic bound would put the largest accounts on the book under the weakest
    justification on it.
    """
    industrial = [c for c in _priceable_book() if c.get("segment") == IC_SEGMENT]
    assert len(industrial) <= MAX_INDUSTRIAL_ACCOUNTS_UNDER_A_DOMESTIC_BOUND, (
        "{} industrial account(s) are on the priceable book: {}. The domestic support bound now "
        "governs the accounts it describes least. Derive a non-domestic bound before serving "
        "I&C again.".format(len(industrial), sorted(c["customer_id"] for c in industrial)))


def test_MUTATION_a_book_that_went_non_domestic_reds(monkeypatch):
    """R15: the tripwire fires on its own named defect, rather than being green because today's
    book happens to be domestic. Without this, both thresholds above would pass on a control
    that had stopped measuring anything."""
    fake = ([{"commodity": "electricity", "segment": RESI_SEGMENT, "customer_id": f"R{i}"}
             for i in range(10)]
            + [{"commodity": "electricity", "segment": SME_SEGMENT, "customer_id": f"S{i}"}
               for i in range(10)])
    monkeypatch.setattr(
        "tests.company.pricing.test_the_support_bound_is_domestic._priceable_book",
        lambda: fake)
    book = _priceable_book()
    share = len([c for c in book if c["segment"] != RESI_SEGMENT]) / len(book)
    assert share > MAX_NON_DOMESTIC_SHARE_UNDER_A_DOMESTIC_BOUND, (
        "a half-SME book must exceed the threshold, or the threshold is not a tripwire")


def test_MUTATION_an_unsuspended_industrial_book_reds():
    """The partner for the I&C count: prove the assertion discriminates."""
    industrial = [{"commodity": "electricity", "segment": IC_SEGMENT, "customer_id": "C_IC1"}]
    assert len(industrial) > MAX_INDUSTRIAL_ACCOUNTS_UNDER_A_DOMESTIC_BOUND
