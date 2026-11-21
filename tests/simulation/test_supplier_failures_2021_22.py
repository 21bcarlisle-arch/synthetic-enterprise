"""The 2021-22 SoLR failures: each test names the defect it exists to catch.

Knowledge page: docs/market_research/gb_supplier_failures_and_solr_transfers_2021_22.md.

R15 mutations, 21 Nov 2026. Each was applied to the module in place and reverted, and each turned
at least one test red: Avro moved to Oct-21 (2 red); Hub's SoLR changed to EDF (1); move lands on
"fixed" (1); membership drawn at 0.5 not the month's share (1); `lo` arm deems every read (1);
unseeded RNG (1).
"""
from __future__ import annotations

from collections import defaultdict

import pytest

from simulation import supplier_failures_2021_22 as sf
from simulation.svt_product import SVT_TARIFF_TYPE


def test_the_secondary_counts_still_RECONCILE_with_NAO_figure_5_solr_by_solr():
    """Defect: a row is added, dropped or mis-assigned (Green Network Energy, a pre-window failure,
    or Neo/UKEIH, a post-May-2022 one) and the list stops being the NAO's 28. The secondary counts
    are trusted only because they sum to Figure 5. Tolerance: Figure 5 rounds to the nearest 1,000."""
    by_solr = defaultdict(int)
    for f in sf.FAILURES:
        by_solr[f.solr] += f.customers
    assert set(by_solr) == set(sf.NAO_FIGURE_5_BY_SOLR)
    for solr, nao in sf.NAO_FIGURE_5_BY_SOLR.items():
        assert abs(by_solr[solr] - nao) <= 6_500, (solr, by_solr[solr], nao)
    assert len(sf.FAILURES) == sf.NAO_SOLR_FIRMS
    assert sum(f.business_only for f in sf.FAILURES) == sf.NAO_BUSINESS_ONLY_FIRMS
    assert 2_350_000 <= sum(f.customers for f in sf.FAILURES) < 2_400_000  # "nearly 2.4 million"


def test_every_failure_is_dated_INSIDE_the_NAO_window_and_bulb_moves_nobody():
    """Defect: a failure dated outside July 2021 to May 2022, or Bulb (a SAR) slipped in as a move."""
    lo, hi = sf.WINDOW
    for f in sf.FAILURES:
        assert lo <= f.month_bounds[0] <= f.month_bounds[1] <= hi, f
        assert f.month is None or f.month_bounds == (f.month, f.month)
    assert "Bulb Energy" not in {f.supplier for f in sf.FAILURES}
    assert sf.BULB_SAR["moves_anyone_here"] is False


def test_the_peak_month_is_SEPTEMBER_2021_and_quiet_months_move_nobody():
    """Defect: the dates are lost or shifted, so the move lands in the wrong month or nowhere.
    September 2021 (Avro, People's, Green, Utility Point, Igloo) is the record's largest month."""
    shares = {m: sf.solr_move_share(m, "lo") for m in
              ("2021-09", "2021-10", "2021-11", "2021-12", "2022-01", "2022-02")}
    assert max(shares, key=shares.get) == "2021-09"
    assert 0.04 < shares["2021-09"] < 0.06  # c. 1.73m of 28.9m accounts, either arm
    assert sf.solr_move_share("2021-06", "lo") == 0.0
    assert sf.solr_move_share("2023-09", "hi") == 0.0
    for m, s in shares.items():
        assert sf.solr_move_share(m, "hi") >= s


def test_the_domestic_share_is_an_ARM_never_a_picked_point():
    """Defect: someone sets a single domestic share to make a number land. Both arms come from NAO
    note 3, and an unknown arm is refused."""
    assert sf.domestic_share("lo") < sf.domestic_share("hi") <= 1.0
    with pytest.raises(ValueError):
        sf.domestic_share("mid")


def test_a_moved_household_lands_on_the_DEFAULT_tariff_at_a_SOLR_of_that_month():
    """Defect: the move lands on a fixed deal, or picks a firm that did not fail that month, or a
    business-only firm. Drawn over enough households to see moves at September's c. 5%."""
    transfers = [t for i in range(4000)
                 if (t := sf.solr_transfer_for(f"hh{i}", "2021-09", "hi")) is not None]
    assert 120 < len(transfers) < 320
    sept = {f.supplier: f for f in sf.failures_in("2021-09")}
    for t in transfers:
        assert t.arrives_on == SVT_TARIFF_TYPE
        assert t.failed_supplier in sept and sept[t.failed_supplier].solr == t.solr
        assert t.opening_read == "deemed" and t.data_regime == "historical"
    assert "Avro Energy" in {t.failed_supplier for t in transfers}
    assert sf.solr_transfer_for("hh1", "2021-06", "hi") is None


def test_the_opening_read_share_is_a_GAP_under_lo_and_says_so():
    """Defect: the unpublished share of customers who supplied an opening read is filled in, so C2
    looks measured when it is a bound."""
    assert sf.OPENING_READ_SUPPLIED_SHARE is None
    t = next(t for i in range(4000)
             if (t := sf.solr_transfer_for(f"hh{i}", "2021-09", "lo")) is not None)
    assert t.opening_read is None
    assert t.opening_read_reason == sf.OPENING_READ_GAP


def test_the_draw_is_DETERMINISTIC_per_household_and_month():
    """Defect: a move that changes between replays is a world that cannot be frozen (W7)."""
    a = [sf.solr_transfer_for(f"hh{i}", "2021-11", "hi") for i in range(500)]
    b = [sf.solr_transfer_for(f"hh{i}", "2021-11", "hi") for i in range(500)]
    assert a == b


def test_the_C2_first_read_comes_from_the_ORDINARY_read_cycle_after_the_move():
    """Defect: the SoLR's first actual read is placed before the move it follows."""
    t = next(t for i in range(4000)
             if (t := sf.solr_transfer_for(f"hh{i}", "2021-09", "hi")) is not None)
    first = sf.first_actual_read_after_transfer(t, "traditional")
    assert first is None or first >= "2021-09-30"
