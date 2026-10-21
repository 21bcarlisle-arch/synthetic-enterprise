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
  * drop the largest-run or the net-without-it column -> `test_the_year_end_net_reaches_the_reader_with_the_run_that_sets_it` reds.
  * drop the `billacc-example` render -> `test_one_named_account_reaches_the_reader` reds.
  * render the DD money line without its intervals -> `test_the_dd_money_line_reaches_the_reader_with_its_bound` reds.
  * render the DD barred money in the fuels table -> `test_the_dd_money_line_is_never_a_row_of_the_k3_table` reds.
  * drop the `billacc-readduty` render, or count prepayment rows as the duty's -> `test_the_read_duty_register_reaches_the_reader_beside_the_snapshot` reds.
  * drop the visit cost or its bound, charge instructions not visits, or type the prices into the
    page -> `test_the_read_visit_cost_reaches_the_reader_with_its_bound` reds; render a missing or
    unknown visit count as a figure -> `test_a_feed_without_a_visit_count_renders_its_absence_and_never_a_zero` reds.
  * drop the open-exposure or the barred-plus-open column of `billacc-ddarms`, or the step-up
    columns -> `test_both_review_arms_reach_the_reader_with_the_exposure_beside_the_share` and
    `test_the_published_feeds_review_arms_reach_the_reader` red.
  * drop the `billacc-k2split` render, or either meter's column, or the DESNZ comparator ->
    `test_the_estimated_share_by_year_and_meter_reaches_the_reader` reds; render a feed without
    the split as a figure -> `test_a_feed_without_the_meter_split_renders_its_absence_and_never_a_zero` reds.
  * drop the `billacc-unbilled` render, or its held-on-a-read column ->
    `test_the_unbilled_accrual_reaches_the_reader_and_never_inside_the_estimate_tables` and
    `test_the_published_feeds_unbilled_accrual_reaches_the_reader` red.
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
PANELS = ("billacc-fuels", "billacc-k2split", "billacc-dd", "billacc-ddarms", "billacc-snapshot", "billacc-readduty", "billacc-yearend",
          "billacc-unbilled", "billacc-example", "billacc-note")


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


_DD_LINE = {
    "available": True, "seek_balance_at_review": False, "dd_accounts": 129,
    "accounts_met_recovery_action": 45, "accounts_barred": 27, "barred_gbp": 15446.94,
    "share_barred": 0.6, "share_barred_ci95": [0.4545, 0.7298], "mean_barred_gbp": 343.27,
    "mean_barred_gbp_ci95": [165.21, 521.32], "open_accounts": 84, "open_exposure_gbp": 27538.58,
}


def _year_unread(cid: str, channel: str, visit_sent: bool | None = None) -> list[dict]:
    """Twelve estimated bills in a row on one account: one register row. With `visit_sent`, the
    12th bill's period carries the read instruction the 11th raised, as `build_monthly_bills`
    writes it (the fixture keeps the run unread either way, so the register row stands)."""
    bills = [{"customer_id": cid, "commodity": "electricity", "billing_basis": "estimated",
              "period_end": f"2024-{m:02d}-28", "consecutive_estimated_count": m,
              "payment_channel": channel} for m in range(1, 13)]
    if visit_sent is not None:
        bills[-1].update(read_instruction_raised="2024-11-28", read_instruction_outcome="no_access",
                         read_instruction_visit_sent=visit_sent)
    return bills


def _arms() -> dict:
    """Two books over the same bills: the review that seeks asks more accounts and loses less."""
    def acct(cid, closed, met, barred, exposure):
        return {"customer_id": cid, "closed": closed, "met_recovery_action": met,
                "barred_gbp": barred, "exposure_gbp": exposure}
    never = {"accounts": [acct("A", True, True, 100.0, 0.0), acct("B", True, True, 0.0, 0.0),
                          acct("C", False, False, 0.0, 400.0), acct("D", False, False, 0.0, 0.0)],
             "bar_actions": [{"customer_id": "A", "date": "2023-05-01", "amount_gbp": 100.0,
                              "action": "final_bill"}],
             "review_step_ups": []}
    seeks = {"accounts": [acct("A", True, True, 60.0, 0.0), acct("B", True, True, 0.0, 0.0),
                          acct("C", False, True, 30.0, 0.0), acct("D", False, True, 20.0, 0.0)],
             "bar_actions": [{"customer_id": "A", "date": "2022-05-01", "amount_gbp": 60.0,
                              "action": "review"},
                             {"customer_id": "C", "date": "2023-02-01", "amount_gbp": 30.0,
                              "action": "review"},
                             {"customer_id": "D", "date": "2023-03-01", "amount_gbp": 20.0,
                              "action": "review"}],
             "review_step_ups": [{"customer_id": c, "date": d, "step_up_gbp": v}
                                 for c, d, v in (("A", "2023-01-01", 10.0), ("C", "2023-02-01", 55.0),
                                                 ("D", "2023-03-01", 70.0), ("B", "2023-04-01", 0.0))]}
    return {"never_seeks": never, "seeks": seeks}


def _accrual() -> dict:
    """Through the company's own accrual: a closed account's held estimate (400 kWh, over a year
    old by 2023-06), and a held read whose catch-up went out with nobody (300 + 50 - 10 kWh)."""
    from company.billing.billing_accuracy import unbilled_accrual

    def bill(cid, end, basis, kwh, total, vat, **extra):
        return {"customer_id": cid, "period_end": end, "billing_basis": basis, "commodity": "electricity",
                "total_consumption_kwh": kwh, "total_amount_gbp": total, "vat_gbp": vat, **extra}
    bills = [bill("C2", "2022-03-31", "estimated", 400.0, 60.0, 3.0),
             bill("C3", "2023-05-31", "actual", 300.0, 90.0, 4.0, catchup_applied=True,
                  read_true_up_kwh=50.0, read_true_up_barred_kwh=10.0),
             bill("C3", "2023-06-30", "actual", 280.0, 80.0, 4.0)]
    held = {("C2", "2022-03-31"), ("C3", "2023-05-31")}
    return {"available": True, "unit_kwh": "kwh", "unit_gbp": "gbp_net_of_vat",
            "month_ends": [unbilled_accrual(bills, held, "2023-06")]}


def _meter_split() -> dict:
    """Through the company's own split: one smart account (1 of 4 billed on estimates) and one
    traditional (3 of 4), in 2024."""
    from company.billing.billing_accuracy import estimated_share_by_year_and_meter

    bills, types = [], {}
    for cid, kind, bases in (("S", "smart", "eaaa"), ("T", "traditional", "eeea")):
        for m, basis in enumerate(bases, start=1):
            end = f"2024-{m:02d}-28"
            bills.append({"customer_id": cid, "period_end": end, "commodity": "electricity",
                          "billing_basis": "estimated" if basis == "e" else "actual",
                          "total_consumption_kwh": 100.0})
            types[(cid, end)] = kind
    return estimated_share_by_year_and_meter(bills, types)


def _feed(dd_line: dict | None = _DD_LINE, read_duty: bool = True,
          arms: dict | None = None, accrual: bool = True) -> dict:
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
             "graded_gross_true_up_share": 0.1342, "graded_largest_run_account": "C7",
             "graded_largest_run_share_of_net": 1.29, "graded_net_true_up_share_without_largest_run": -0.0246}
    account = {"account_id": "SYN-2016-052", "fuel": "electricity", "bills": 108,
               "estimated_bills": 87, "longest_run_without_read_bill": 22, "true_ups": 16,
               "true_up_kwh": 820.0, "undercharge_kwh": 6784.0, "overcharge_kwh": 5964.0,
               "barred_kwh": 1401.0}
    from company.billing.read_duty_register import read_duty_summary

    view = published_view({"kinds": {"K2": "k2"}, "snapshot_month": "2025-06",
                           "by_fuel": {"electricity": fuel},
                           "K1_year_end_grades": {"electricity": [grade]},
                           "accounts": [account], "direct_debit_money_line": dd_line},
                          "run_output_test.json")
    from company.billing.billing_accuracy import dd_review_arms

    view["direct_debit_review_arms"] = dd_review_arms(_arms() if arms is None else arms or None)
    if accrual:
        view["K1_unbilled_accrual"] = _accrual()
    view["K2_by_year_and_meter_type"] = _meter_split()
    if read_duty:
        # Set beside the view rather than handed in as `bills`, which would re-grade K1 above.
        view["read_duty_register"] = read_duty_summary(
            _year_unread("A", "direct_debit", visit_sent=True)
            + _year_unread("B", "standard_credit", visit_sent=False)
            + _year_unread("P", "prepayment"))
    return view


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


def test_the_year_end_net_reaches_the_reader_with_the_run_that_sets_it(shown):
    """One unread EV home set electricity's year-end net for four years and was read as a
    population bias (2026-10-16). Fires on: either column dropped, or the account unnamed."""
    assert "-6.0% 13.4% 129.0% (C7) -2.5%" in shown["billacc-yearend"]
    assert "the net without that run is the population's" in shown["billacc-note"]


def test_one_named_account_reaches_the_reader(shown):
    assert "SYN-2016-052" in shown["billacc-example"]
    assert "1,401 kWh could not be billed" in shown["billacc-example"]


def test_an_unavailable_feed_renders_an_absence_and_never_a_zero():
    live = published_json(FEED_REL)
    feed = live if not live.get("available") else {"available": False, "reason": "test absence"}
    shown = _render(feed)
    assert "absent rather than empty" in shown["billacc-note"]
    assert not any(shown[p] for p in PANELS if p != "billacc-note")


def test_the_dd_money_line_reaches_the_reader_with_its_bound(shown):
    text = shown["billacc-dd"]
    assert "27 of 45 direct-debit accounts" in text
    assert "60.0% (95% 45.5% to 73.0%)" in text
    # TWO MEANS, EACH SAYING WHAT IT COUNTS (D48 Expert Hour, 2026-10-14): the sentence names the
    # accounts that lost money, so a bare "an account" was read as their mean when it was the mean
    # over every account asked. Fires on: either mean dropped, or the denominators unnamed.
    assert "£15,447 in all: £343 averaged over all 45 accounts asked (95% £165 to £521)" in text
    assert "or £572 for each account that lost some" in text
    assert "84 accounts are still open, with £27,539" in text and "exposure, not a loss" in text


def test_the_dd_money_line_is_never_a_row_of_the_k3_table(shown):
    assert "£" not in shown["billacc-fuels"] and "15,447" not in shown["billacc-fuels"]
    assert "2,180 kWh" in shown["billacc-fuels"]  # K3's own energy is still there


def test_a_feed_without_the_dd_line_renders_its_absence_and_never_a_zero():
    text = _render(_feed(dd_line=None))["billacc-dd"]
    assert "absent rather than zero" in text and "appear at the next run" in text
    assert "£" not in text


def test_the_read_duty_register_reaches_the_reader_beside_the_snapshot(shown):
    """K2's snapshot asks of one month; the SLC 21B.4 register counts every year a run of estimates
    passed without a read (2026-10-16). Fires on: the panel dropped, the prepayment rows counted as
    the duty's, or their count unshown."""
    text = shown["billacc-readduty"]
    assert "electricity: 2 times, on 2 accounts" in text
    assert "SLC 21B.4" in text and "(1 electricity)" in text


def test_the_read_visit_cost_reaches_the_reader_with_its_bound(shown):
    """026b3c650 charges each read visit sent at an area round, with an appointment as the bound,
    and no page showed either (2026-10-21). Fires on: the cost dropped, the bound dropped, the
    instructions charged rather than the visits, or the prices typed into the page instead of read
    from the feed."""
    text = shown["billacc-readduty"]
    assert "instructed 2 reads" in text and "and 1 sent a visit" in text
    assert "at £3.00: £3.00" in text and "at £17.50, it would be £17.50" in text
    assert "account 6100" in text and "not charged" in text
    assert "keeps no record of any step" not in text


@pytest.mark.parametrize("cost, shows, never", [
    (None, "not in this feed, so absent rather than zero", "account 6100"),
    ({"instructions": 0, "visits": 0, "charged_gbp": 0.0, "upper_bound_gbp": 0.0,
      "price_gbp_per_visit": 3.0, "upper_price_gbp_per_visit": 17.5},
     "instructed no read", "account 6100"),
    ({"instructions": 582, "visits": None, "reason": "these bills predate 2026-10-21"},
     "582 read instructions were raised", "£"),
])
def test_a_feed_without_a_visit_count_renders_its_absence_and_never_a_zero(cost, shows, never):
    """A published run from before the visit flag says which instructions sent a visit for none of
    them, and a run with the instruction off sent none; neither is a cost of zero visits. The
    second arm also proves the old no-step sentence is still reachable."""
    feed = _feed()
    if cost is None:
        feed["read_duty_register"].pop("visit_cost")
    else:
        feed["read_duty_register"]["visit_cost"] = cost
    text = _render(feed)["billacc-readduty"]
    assert shows in text and never not in text
    assert ("keeps no record of any step" in text) == (cost is None or cost["instructions"] == 0)


def test_a_feed_without_the_read_duty_register_renders_its_absence_and_never_a_zero():
    from company.billing.billing_accuracy import published_view

    feed = _feed(read_duty=False)
    assert feed["read_duty_register"]["available"] is False  # no bills handed to the publish
    text = _render(feed)["billacc-readduty"]
    assert "absent rather than zero" in text and "times" not in text
    assert published_view(None)["available"] is False


def test_both_review_arms_reach_the_reader_with_the_exposure_beside_the_share(shown):
    """Seeking the balance at the review raises the barred SHARE (more accounts asked) while it
    lowers the money lost (D48, 2026-10-16). Fires on: the open exposure or the sum dropped, so the
    share reads alone, or the step-up by year dropped."""
    text = shown["billacc-ddarms"]
    # never: 1 of 2 asked, £100 barred, £400 open -> £500. seeks: 3 of 4, £110, nothing open.
    assert "Never asks (as run) 2 1 50.0%" in text and "£100 £400 £500" in text
    assert "Asks at each review 4 3 75.0%" in text and "£110 £0 £110" in text
    # 2023: never bars £100 on A; seeks bars £50 on C and D; three reviews found a debit (B's
    # zero step-up is not one): median £55, mean £45, p90 £70.
    assert "2023 £100 (1) £50 (2) 3 £55.00 £45.00 £70.00" in text
    assert "2022 £0 (0) £60 (1) 0" in text


def test_a_feed_without_the_review_arms_renders_their_absence_and_never_a_zero():
    text = _render(_feed(arms={}))["billacc-ddarms"]
    assert "absent rather than zero" in text and "£" not in text


def test_the_published_feeds_review_arms_reach_the_reader():
    """The real feed, not a fixture: whatever the published run's two arms say is what the reader
    meets, each arm's share beside its open exposure and their sum."""
    live = published_json(FEED_REL)
    arms = (live.get("direct_debit_review_arms") or {})
    if not arms.get("available"):
        pytest.fail("the published billing feed carries no review arms: {}".format(
            arms.get("reason", "the key is absent")))
    text = _render(live)["billacc-ddarms"]
    for name in ("never_seeks", "seeks"):
        x = arms["arms"][name]
        assert "{:,} {:,}".format(x["accounts_met_recovery_action"], x["accounts_barred"]) in text
        assert "£{:,} £{:,} £{:,}".format(*(round(x[k]) for k in (
            "barred_gbp", "open_exposure_gbp", "barred_plus_open_exposure_gbp"))) in text
    stepped = [y for y in arms["by_year"] if y["step_up_median_gbp"] is not None]
    assert stepped, "no year carries a step-up, so the household's side cannot be shown"
    assert "£{:.2f}".format(stepped[-1]["step_up_median_gbp"]) in text


def test_the_unbilled_accrual_reaches_the_reader_and_never_inside_the_estimate_tables(shown):
    """Energy no issued bill charged (D48, 2026-10-20). Fires on: the panel dropped, a column
    dropped, or the accrual's energy shown inside the billed-on-estimate tables it is never
    added to."""
    text = shown["billacc-unbilled"]
    assert "electricity 2023-06 2 1 1 740 kWh £143 400 kWh 400 kWh" in text
    assert "never added to the figure open on estimate" in text
    assert "740 kWh" not in shown["billacc-yearend"] and "740 kWh" not in shown["billacc-fuels"]


def test_a_feed_without_the_accrual_renders_its_absence_and_never_a_zero():
    from company.billing.billing_accuracy import published_view

    feed = _feed(accrual=False)
    assert feed["K1_unbilled_accrual"]["available"] is False  # the view was handed no bills
    text = _render(feed)["billacc-unbilled"]
    assert "absent rather than zero" in text and "kWh" not in text
    assert published_view(None)["available"] is False


def test_the_published_feeds_unbilled_accrual_reaches_the_reader():
    """The real feed: whatever the published run's accrual is at its last month end is what the
    reader meets, every column of it."""
    live = published_json(FEED_REL)
    accrual = live.get("K1_unbilled_accrual") or {}
    if not accrual.get("available"):
        pytest.fail("the published billing feed carries no unbilled accrual: {}".format(
            accrual.get("reason", "the key is absent")))
    last = accrual["month_ends"][-1]
    x = last["by_fuel"]["electricity"]
    row = "electricity {} {:,} {:,} {:,} {:,} kWh £{:,} {:,} kWh {:,} kWh".format(
        last["as_of"], x["accounts"], x["held_estimates"], x["held_actuals"], round(x["kwh"]),
        round(x["gbp"]), round(x["older_than_12_months_kwh"]), round(x["closed_account_kwh"]))
    assert row in _render(live)["billacc-unbilled"]


def test_the_estimated_share_by_year_and_meter_reaches_the_reader(shown):
    text = shown["billacc-k2split"]
    # Year, accounts, blended, traditional share of accounts, smart, traditional.
    assert "2024 2 50.0% 50.0% 25.0% 75.0%" in text
    assert "Nationally 35.8% of domestic electricity meters" in text


def test_a_feed_without_the_meter_split_renders_its_absence_and_never_a_zero():
    feed = _feed()
    del feed["K2_by_year_and_meter_type"]
    text = _render(feed)["billacc-k2split"]
    assert "absent rather than zero" in text and "next publish" in text
    assert "%" not in text
