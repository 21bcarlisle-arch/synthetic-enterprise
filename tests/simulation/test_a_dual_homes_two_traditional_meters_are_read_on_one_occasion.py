"""Cold read N30: a dual-fuel home's two traditional meters were read on independent draws, so one
fuel was estimated beside the other's actual read in 89% of periods with any read.

The defects these tests name:
  * the coupling never taken (a share the code ignores reads 0.89 at every setting);
  * the coupling bought by moving a fuel's read rate, which would break the 12-month no-read
    calibration each leg is solved against;
  * the electricity leg's reads disturbed by a change that is only the gas leg's.
"""
from __future__ import annotations

from unittest import mock

from simulation import meter_reads as m

MONTHS = [f"{2018 + i // 12}-{i % 12 + 1:02d}-28" for i in range(12)]


def _book(share, homes=3000):
    with mock.patch.object(m, "DUAL_FUEL_READ_TOGETHER_SHARE", share):
        out = []
        for h in range(homes):
            for pe in MONTHS:
                e = m.simulate_read(f"N{h}", pe, "traditional", 100.0, 0)
                g = m.simulate_read(f"N{h}g", pe, "traditional", 500.0, 0, commodity="gas")
                out.append((e, g))
        return out


def _one_only(book):
    both = sum(e.status == g.status == "actual" for e, g in book)
    one = sum((e.status == "actual") != (g.status == "actual") for e, g in book)
    return one / (one + both)


def test_the_share_moves_the_one_only_share_across_the_whole_range():
    apart, together, always = _book(0.0), _book(m.DUAL_FUEL_READ_TOGETHER_SHARE), _book(1.0)
    # Independence gives ~0.886, the register's 0.8 gives ~0.286, full coupling leaves only the
    # read classes' disagreement. Each must be reachable, or the control cannot tell them apart.
    assert _one_only(apart) > 0.85 and 0.2 < _one_only(together) < 0.36 and _one_only(always) < 0.05


def test_each_fuels_read_rate_and_the_electricity_reads_do_not_move():
    apart, always = _book(0.0), _book(1.0)
    rate = lambda book, k: sum(pair[k].status == "actual" for pair in book) / len(book)  # noqa: E731
    assert abs(rate(apart, 1) - rate(always, 1)) < 0.015
    assert [e for e, _ in apart] == [e for e, _ in always]


def test_an_electricity_point_and_a_gas_draw_off_the_occasion_keep_their_own_id():
    assert m.read_occasion_id("N7", "2019-01-28", together_share=1.0) == "N7"
    assert m.read_occasion_id("N7g", "2019-01-28", together_share=1.0) == "N7"
    assert m.read_occasion_id("N7g", "2019-01-28", together_share=0.0) == "N7g"
