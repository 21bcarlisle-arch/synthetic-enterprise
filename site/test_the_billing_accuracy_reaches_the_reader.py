"""D48's billing-accuracy measure must reach the RENDERED /capabilities/ page, not just the feed.

THE DEFECT IT SERVES. `company/billing/billing_accuracy.py` was computed on every run from
2026-10-05 (`simulation/run_phase4c_on_phase2b.py` key `billing_accuracy`) and read by nothing:
`saas/reporting/annual_report.py` did not carry it into the run output, so no page could show it.

The subject is the DOM the door's own script builds, driven through `site/_live_harness.mjs`, as
in `test_the_opening_direct_debit_comparison_reaches_the_reader.py`.

R15 -- the mutations, each run and reverted:
  * render the snapshot share without its interval -> `test_the_snapshot_reaches_the_reader_with_its_bound_and_verdict` reds.
  * drop the verdict text -> the same test reds.
  * drop the `billacc-yearend` render -> `test_the_year_end_grades_reach_the_reader` reds.
  * drop the `billacc-example` render -> `test_one_named_account_reaches_the_reader` reds.
The null rung, `test_an_unavailable_feed_renders_an_absence_and_never_a_zero`, stays green
through all four.
"""
from __future__ import annotations

import html as html_lib
import json
import re
import subprocess
from pathlib import Path

import pytest
from test_the_published_bytes_reader import published_file, published_json

SITE = Path(__file__).resolve().parent
HARNESS = SITE / "_live_harness.mjs"
DOOR_REL = "site/capabilities/index.html"
FEED_REL = "site/data/billing_accuracy.json"
PANELS = ("billacc-fuels", "billacc-snapshot", "billacc-yearend", "billacc-example", "billacc-note")


def _text(fragment: str) -> str:
    return re.sub(r"\s+", " ", html_lib.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def _render(feed: dict) -> dict:
    if not HARNESS.is_file():
        pytest.fail("site/_live_harness.mjs is missing -- the render check is UNAVAILABLE (R15)")
    payload = {
        "../data/billing_accuracy.json": feed,
        "../data/engagement_separation.json": published_json("site/data/engagement_separation.json"),
        "../data/dd_opening_arms.json": published_json("site/data/dd_opening_arms.json"),
        "../data/value_arms.json": published_json("site/data/value_arms.json"),
        "../data/book_growth.json": published_json("site/data/book_growth.json"),
        "../data/capabilities_door.json": published_json("site/data/capabilities_door.json"),
    }
    proc = subprocess.run(
        ["node", str(HARNESS), str(published_file(DOOR_REL))],
        input=json.dumps(payload), capture_output=True, text=True, timeout=180,
    )
    assert proc.returncode == 0, "the render harness failed: {}".format(proc.stderr[-2000:])
    out = json.loads(proc.stdout)
    meta = out.get("_meta") or {}
    assert not meta.get("unresolved"), "the door asked for an unsupplied feed: {}".format(
        meta.get("unresolved"))
    assert not meta.get("scriptError"), "the door's own script threw: {}".format(
        meta.get("scriptError"))
    return {p: _text((out.get(p) or {}).get("innerHTML") or "")
            or _text((out.get(p) or {}).get("textContent") or "") for p in PANELS}


def _feed() -> dict:
    """An available feed in the shape `published_view` writes: the decade capture's electricity
    snapshot (2 of 48) and one year-end grade."""
    from company.billing.billing_accuracy import published_view

    fuel = {
        "accounts": 111, "billed_kwh": 2039363.0, "estimated_kwh": 1185868.0, "true_ups": 871,
        "true_up_kwh": 29142.0, "undercharge_kwh": 140228.0, "overcharge_kwh": 111086.0,
        "barred_kwh": 2180.0, "barred_true_ups": 17, "open_estimated_kwh": 36140.0,
        "snapshot_accounts": 48, "snapshot_no_read_bill_in_12": 2,
        "K2_estimated_share_of_billed_kwh": 0.5815, "K2_snapshot_share_no_read_bill_in_12": 2 / 48,
        "K3_barred_share_of_undercharge_kwh": 0.0155,
    }
    grade = {"as_of": "2024-12", "outstanding_gbp": 16232.7, "outstanding_bills": 128,
             "graded_runs": 24, "never_read_runs": 8, "graded_net_true_up_share": -0.0602,
             "graded_gross_true_up_share": 0.1342}
    account = {"account_id": "SYN-2016-052", "fuel": "electricity", "bills": 108,
               "estimated_bills": 87, "longest_run_without_read_bill": 22, "true_ups": 16,
               "true_up_kwh": 820.0, "undercharge_kwh": 6784.0, "overcharge_kwh": 5964.0,
               "barred_kwh": 1401.0}
    return published_view({"kinds": {"K2": "k2"}, "snapshot_month": "2025-06",
                           "by_fuel": {"electricity": fuel},
                           "K1_year_end_grades": {"electricity": [grade]},
                           "accounts": [account]}, "run_output_test.json")


@pytest.fixture(scope="module")
def shown() -> dict:
    return _render(_feed())


def test_the_snapshot_reaches_the_reader_with_its_bound_and_verdict(shown):
    text = shown["billacc-snapshot"]
    assert "2 of 48, 4.2% (95% 1.2% to 14.0%)" in text
    assert "cannot be told apart from the median supplier" in text
    assert "5.2% to 5.6%" in text


def test_the_estimated_share_and_barred_energy_reach_the_reader(shown):
    assert "58.1% of 2,039,363 kWh" in shown["billacc-fuels"]
    assert "2,180 kWh (1.6% of undercharge, 17 corrections)" in shown["billacc-fuels"]


def test_the_year_end_grades_reach_the_reader(shown):
    assert "2024-12 £16,233 24 8 -6.0% 13.4%" in shown["billacc-yearend"]


def test_one_named_account_reaches_the_reader(shown):
    assert "SYN-2016-052" in shown["billacc-example"]
    assert "1,401 kWh could not be billed" in shown["billacc-example"]


def test_an_unavailable_feed_renders_an_absence_and_never_a_zero():
    live = published_json(FEED_REL)
    feed = live if not live.get("available") else {"available": False, "reason": "test absence"}
    shown = _render(feed)
    assert "absent rather than empty" in shown["billacc-note"]
    assert not any(shown[p] for p in PANELS if p != "billacc-note")
