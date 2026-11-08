# ARCHIVED LEGS of tests/tools/test_weather_driver_sensitivity.py (archive increment 3b). The tests here reach a module
# under archive/unhooked_supplier/; the live legs stay at tests/tools/test_weather_driver_sensitivity.py.
"""What each driver is for, each test named by the defect it exists to catch.

The question this module answers decides whether a cell count is worth paying, so the failure that
matters is a plausible ratio between two effects that were not measured over the same thing.
"""
from __future__ import annotations

import re

import pytest

from tools import weather_driver_sensitivity as wds
















def test_the_PV_CURVE_starts_at_the_NATIONAL_number_the_company_actually_uses():
    """`cells=1` is not a mathematical limit here, it is the company's live behaviour:
    `seg_export_estimator` applies one kWh/kWp figure to every household. If that ever stops being
    true this test should fail, because the 3.4% headline is a statement about a real defect."""
    from company.regulatory import seg_export_estimator as seg

    assert isinstance(seg.ANNUAL_YIELD_KWH_PER_KWP, float), (
        "the national yield figure has moved or become geographic; the '1 cell today' claim needs "
        "re-checking before it is published again")

    curve = wds.pv_yield_error(cells=(1, 5))
    rows = {r["cells"]: r for r in curve["curve"]}
    assert rows[1]["yield_rms"] > rows[5]["yield_rms"] * 2, (
        "five cells must materially beat one; if they do not, the curve is flat and the "
        "recommendation is unfounded")
    assert 0.0 < curve["elasticity_of_irradiation_to_sunshine"] < 1.0










