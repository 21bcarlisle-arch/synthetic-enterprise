"""The LATEST.md results block, the one figure the publisher used to compute inline (OPS6).

It lives in a declared publish-path source so that its guard blocks a publish while the
publisher's bookkeeping tests only annotate. The last test is what holds that: if the module
leaves the declaration, or the publisher writes the block itself again, this file leaves the
blocking scope and the test says so."""
from __future__ import annotations

from datetime import datetime, timezone

from background import publish_content, publish_scope

DATA = {
    "total_net_gbp": -8317.21, "total_gross_gbp": -7089.58, "total_capital_gbp": 1228.0,
    "starting_treasury_gbp": 29846.0, "final_treasury_gbp": 11131.0,
    "committee_wake_ups_total": 323, "bills_total": 1117, "enterprise_value_gbp": -20661.90,
    "net_margin_after_cost_to_serve_gbp": -23569.0,
    "retention_log": [{"outcome": "retained"}, {"outcome": "lost"}],
    "no_offer_churn_log": [{}] * 3, "churned_billing_accounts": ["C1", "C2"],
}
NOW = datetime(2026, 11, 9, 8, 0, tzinfo=timezone.utc)


def test_the_block_is_replaced_in_place_and_its_neighbours_survive(tmp_path):
    latest = tmp_path / "LATEST.md"
    latest.write_text("Last updated: 2026-01-01T00:00:00Z\n\n"
                      "**Latest simulation results (2016-2025)** - old:\n- Net margin: old data\n\n"
                      "**Some other section** here\n")
    created = publish_content.write_latest_results(latest, DATA, 1870.0, "abc1234", now=NOW)
    text = latest.read_text()
    assert not created
    assert "Net margin: \xa3-8,317.21" in text and "old data" not in text
    assert "1/2 retained | 3 no-offer churns | 2 total churned accounts" in text
    assert "**Some other section** here" in text
    assert "Last updated: 2026-11-09T08:00:00Z" in text


def test_the_block_carries_its_run_and_date(tmp_path):
    """The only live £ on the status page; undated, it cannot be told from earlier runs'."""
    latest = tmp_path / "LATEST.md"
    latest.write_text("Last updated: x\n")
    assert publish_content.write_latest_results(latest, DATA, 1870.0, "abc1234", now=NOW)
    assert "// run abc1234, 2026-11-09:" in latest.read_text()


def test_the_publisher_writes_the_block_through_this_module(tmp_path, monkeypatch):
    """The publisher's wrapper still writes to the path tests patch on it."""
    from background import process_run_complete as prc
    latest = tmp_path / "LATEST.md"
    latest.write_text("Last updated: x\n")
    monkeypatch.setattr(prc, "LATEST_MD", latest)
    monkeypatch.setattr(prc, "log", lambda msg: None)
    calls = []
    real = publish_content.write_latest_results
    monkeypatch.setattr(publish_content, "write_latest_results",
                        lambda *a, **k: calls.append(a[0]) or real(*a, **k))
    prc.update_latest_md(DATA, 60.0, "abc1234")
    assert calls == [latest] and "Net margin: \xa3-8,317.21" in latest.read_text()


def test_this_guard_blocks_the_publish():
    scope = publish_scope.resolve_scope()
    assert not scope["full_suite"], scope["reason"]
    assert "tests/background/test_publish_content.py" in scope["tests"], (
        "the LATEST.md figure's guard is outside the blocking scope: a wrong results block "
        "would publish")
