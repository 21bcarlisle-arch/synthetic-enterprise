"""The ratio screen's flags, graded by the world's cause (W2_36). Defect named per test."""

from collections import Counter

from sim.customer_state_layer import TenureType
from tools.theft_void_screen_probe import CUTS, _flagged, premise_windows

PREMISES = [f"PREM-test-{i}" for i in range(40)]


def _flags(tenure, window, cut, setting="default"):
    counts = Counter()
    for p in PREMISES:
        for row in premise_windows(p, tenure, setting=setting)[window]:
            if _flagged(row["ratio"], cut):
                counts[row["cause"] or "neither"] += 1
    return counts


def test_a_private_void_shorter_than_a_month_never_empties_one_and_a_theft_does():
    """Defect: the screen's empty-month flags filed to voids a void too short to empty a month,
    or the probe's thefts or voids never arise, so the comparison is vacuous."""
    empty_month = _flags(TenureType.PRIVATE_RENTER, "monthly", CUTS[0])
    loose = _flags(TenureType.PRIVATE_RENTER, "monthly", 0.65)
    # Both causes can be reached before either is compared.
    assert empty_month["theft"] > 0 and loose["void"] > 0, (empty_month, loose)
    assert empty_month["void"] == 0, empty_month
    assert empty_month["neither"] == 0 and loose["neither"] == 0, "flat use flagged on its own"


def test_a_void_barely_dents_a_year_so_annual_flags_are_thefts():
    """Defect: a void of under five weeks is counted as an annual shortfall the screen flags."""
    annual = _flags(TenureType.SOCIAL_RENTER, "annual", 0.65)
    assert annual["theft"] > 0, annual
    assert annual["void"] == 0, annual


def test_the_owners_void_is_carried_as_a_gap_not_as_none():
    """Defect: the owner rows print no voids and nothing says the void length is unpublished."""
    assert premise_windows(PREMISES[0], TenureType.OWNER_OCCUPIER)["void_gap"]
    assert premise_windows(PREMISES[0], TenureType.PRIVATE_RENTER)["void_gap"] is None
