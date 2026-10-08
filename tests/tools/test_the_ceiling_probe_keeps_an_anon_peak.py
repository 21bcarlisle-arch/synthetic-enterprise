"""The settlement-ceiling probe's RssAnon leg.

THE DEFECT each test names: `ru_maxrss` counts file pages the kernel can drop, so a slope on it
alone charges the page cache to the book. The probe now polls the child's RssAnon while it runs;
these controls fail if that poll never reads, reads the wrong field, or if a curve measured before
the leg existed has its missing anon figure read as zero.
"""
from __future__ import annotations

import subprocess
import sys

from tools import settlement_ceiling_probe as probe


def test_the_poll_sees_a_childs_anonymous_peak_and_stays_under_ru_maxrss():
    """DEFECT: the poll loop reaps without ever sampling, and every anon peak reads None."""
    held_mb = 200
    child = subprocess.Popen([sys.executable, "-c",
                              f"b = bytearray({held_mb} * 1024 * 1024); import time; "
                              "time.sleep(2.0)"])
    status, usage, peaks = probe._wait_keeping_rss_peaks(child.pid)
    assert status == 0
    anon_mb = peaks["RssAnon"] / 1024.0
    assert anon_mb >= held_mb, f"the child held {held_mb} MB anonymous; the poll saw {anon_mb:.1f}"
    assert anon_mb <= usage.ru_maxrss / 1024.0, "an anon peak above ru_maxrss is a misread field"


def test_a_reaped_pid_reads_as_nothing_not_as_zero():
    child = subprocess.Popen([sys.executable, "-c", "pass"])
    child.wait()
    assert probe._proc_rss_kb(child.pid) == {}


def _point(cy, rss, anon):
    return {"clean": True, "customer_years_committed": cy, "wall_s": cy / 10.0,
            "peak_rss_mb": rss, "peak_rss_anon_mb": anon}


def test_the_anon_slope_is_formed_when_both_points_carry_it_and_is_None_when_one_does_not():
    """Both branches, in one control: a slope that is always None, or always formed (reading a
    pre-leg curve's absent anon as 0 MB), fails one of the two halves."""
    both = probe.marginal_costs([_point(1000, 3000.0, 2500.0), _point(2000, 4300.0, 3700.0)])
    one = probe.marginal_costs([_point(1000, 3000.0, None), _point(2000, 4300.0, 3700.0)])
    assert both[0]["marginal_anon_mb_per_customer_year"] == 1.2
    assert both[0]["marginal_mb_per_customer_year"] == 1.3
    assert one[0]["marginal_anon_mb_per_customer_year"] is None
