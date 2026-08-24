"""Explore's second clock: one dated day, half hour by half hour, and no invented numbers.

THE GAP. `site/explore/index.html`'s stage 3 is titled *"Two clocks: gas across the years,
electricity across a day"* and rendered electricity BY YEAR, in the same bar table as gas. The
director's brief §5.3 asks for what the copy already promised — *"electricity across one day,
half-hourly"* — because *"the switch between them is the point"*.

WHAT IS UNDER TEST is mostly the HONESTY of the panel, not its prettiness:
  * ONE REAL DAY, named. A mean of 872 winter days would be smoother, more flattering, and a
    figure this project authored rather than one the run produced.
  * A meter with no half-hourly record produces an ABSENCE that says why, never a flat line.
  * The claim "for an HH meter the supplier sees what the world sees" is MEASURED against the
    company's own published feed, not asserted.

R15 mutation sensitivity — each proven by reverting, not asserted:
  * average the days instead of picking one -> `test_a_panel_is_ONE_REAL_DAY_out_of_the_record`.
  * zero-fill an unparseable row -> `test_a_broken_row_is_dropped_not_zero_filled`.
  * compare the company's feed against every date it holds -> `test_the_corroboration_compares
    _one_day_against_the_same_day`.
  * report `available: True` when the feed carries nothing -> `test_an_unmeasured_agreement_is
    _reported_as_unmeasured`.
  * put a meter with no record into `accounts` -> `test_a_meter_with_no_record_is_named_as_an
    _absence`.
"""
from __future__ import annotations

import csv
import json

from tools import generate_explore_hh_day as hh

WINTER = [0.2] * 12 + [0.4] * 20 + [3.0] + [0.5] * 15          # 48, peak at period 33
SUMMER = [0.1] * 48


def _csv(tmp_path, account, rows):
    path = tmp_path / "{}.csv".format(account)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["date"] + ["p{}".format(i + 1) for i in range(48)])
        for date, periods in rows:
            w.writerow([date] + list(periods))
    return path


def _book(*groups):
    return {"customers": [{"customer_group": g, "legs": {"electricity": {"cid": g}}}
                          for g in groups]}


def _detail(account, has_hh=True, meter="Smart"):
    return {"account_id": account, "meter_type": meter,
            "consumption": {"has_hh_data": has_hh}}


def _build(tmp_path, rows, *, feed=None, has_hh=True):
    path = _csv(tmp_path, "C7", rows)
    return hh.build(_book("C7"), {"C7": _detail("C7", has_hh=has_hh)}, feed, {"C7": path})


def test_a_panel_is_ONE_REAL_DAY_out_of_the_record(tmp_path):
    """THE LOAD-BEARING PROPERTY. Every one of the 48 numbers must be a metered value that
    appeared on a named date, so a reader can go and check it. An average of many days would
    match none of them and would be this project authoring a figure on its own site."""
    hot = [v * 2 for v in WINTER]
    out = _build(tmp_path, [("2021-02-11", hot), ("2021-02-12", WINTER),
                            ("2021-07-01", SUMMER), ("2021-07-02", SUMMER)])

    day = out["accounts"]["C7"]["hardest_day"]
    assert day["date"] == "2021-02-11", "the panel is not the highest-consumption day"
    assert day["periods"] == [round(v, 4) for v in hot], (
        "the periods rendered are not the ones on that date — an averaged or smoothed series "
        "is a number this page invented"
    )
    assert day["peak_period"] == 33 and day["peak_clock"] == "16:00"


def test_the_summer_panel_is_the_median_summer_day_and_says_so(tmp_path):
    out = _build(tmp_path, [("2021-02-11", WINTER),
                            ("2021-06-01", [0.05] * 48),
                            ("2021-07-01", SUMMER),
                            ("2021-08-01", [0.3] * 48)])

    summer = out["accounts"]["C7"]["summer_day"]
    assert summer["date"] == "2021-07-01"
    assert "median summer day" in summer["chosen_by"], (
        "the rule that chose the day is not stated, so a reader cannot tell a representative "
        "day from a cherry-picked one"
    )


def test_a_broken_row_is_dropped_not_zero_filled(tmp_path):
    """A zero is a reading that says the household used nothing. Forty-eight of them under the
    word 'metered' is a claim, and it is the wrong one."""
    path = tmp_path / "C7.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["date"] + ["p{}".format(i + 1) for i in range(48)])
        w.writerow(["2021-02-11"] + list(WINTER))
        w.writerow(["2021-02-12"] + ["", "x"] + [""] * 46)

    days = hh.read_days(path)

    assert [d["date"] for d in days] == ["2021-02-11"]


def test_a_meter_with_no_record_is_named_as_an_absence_not_shown_as_a_flat_line(tmp_path):
    """The profile-class household is the POINT of this stage, not a gap in it: the supplier
    cannot draw its day either."""
    out = _build(tmp_path, [("2021-02-11", WINTER)], has_hh=False)

    assert out["accounts"] == {}
    assert [a["customer_group"] for a in out["accounts_without_half_hourly"]] == ["C7"]
    assert out["available"] is False
    assert "0 of 1 households" in out["coverage_statement"]


def test_the_coverage_statement_moves_with_the_book(tmp_path):
    """Said in the data rather than hard-coded in the page, so it does not go stale the first
    time a meter is upgraded."""
    path = _csv(tmp_path, "C7", [("2021-02-11", WINTER)])
    out = hh.build(_book("C7", "C1"),
                   {"C7": _detail("C7"), "C1": _detail("C1", has_hh=False, meter="Profile")},
                   None, {"C7": path})

    assert "1 of 2 households" in out["coverage_statement"]


# ── the measured claim ───────────────────────────────────────────────────────────────────────

def _feed(*records):
    return {"records": list(records)}


def test_the_corroboration_compares_one_day_against_the_same_day(tmp_path):
    """The company's feed has carried TWO dates per account. Comparing every record it holds
    against one day's periods produced 96 'comparisons' of 48 periods and a difference that was
    really two different days — a divergence nobody had, published as if measured."""
    out = _build(
        tmp_path,
        [("2025-06-06", SUMMER), ("2025-06-07", [0.9] * 48)],
        feed=_feed(*(
            [{"customer_id": "C7", "date": "2025-06-06", "period": i + 1, "kwh": 0.1}
             for i in range(48)]
            + [{"customer_id": "C7", "date": "2025-06-07", "period": i + 1, "kwh": 0.9}
               for i in range(48)]
        )),
    )

    c = out["accounts"]["C7"]["corroboration"]
    assert c["available"] is True
    assert c["date"] == "2025-06-07", "the newest day the feed carries is the one to check"
    assert c["periods_compared"] == 48, "more than one day's records were folded into one check"
    assert c["max_abs_difference_kwh"] == 0.0


def test_a_real_disagreement_is_published_rather_than_smoothed(tmp_path):
    """R15 null control on the check above: if it always reported 0.0 it would be decoration."""
    out = _build(
        tmp_path, [("2025-06-07", SUMMER)],
        feed=_feed(*[{"customer_id": "C7", "date": "2025-06-07", "period": i + 1,
                      "kwh": 0.1 + (0.25 if i == 3 else 0.0)} for i in range(48)]),
    )

    assert out["accounts"]["C7"]["corroboration"]["max_abs_difference_kwh"] == 0.25


def test_an_unmeasured_agreement_is_reported_as_unmeasured(tmp_path):
    """FAIL-CLOSED. The page says the supplier's picture and the world's are the same artefact
    here; where that has not been checked it must not read as though it had been."""
    out = _build(tmp_path, [("2021-02-11", WINTER)], feed=_feed())

    c = out["accounts"]["C7"]["corroboration"]
    assert c["available"] is False
    assert c["why"]


def test_the_generator_writes_the_file_and_survives_a_missing_source(tmp_path):
    out_path = tmp_path / "explore_hh_days.json"
    hh.generate(out_path=out_path)
    written = json.loads(out_path.read_text(encoding="utf-8"))

    assert "coverage_statement" in written
    assert isinstance(written.get("accounts"), dict)


def test_the_generator_is_WIRED_into_the_publish_cycle():
    """The class this project keeps finding: a generated surface with no caller freezes against
    its live source, and this one exists precisely to track two of them."""
    from pathlib import Path

    src = Path(hh.__file__).resolve().parent.parent / "background" / "process_run_complete.py"
    text = src.read_text(encoding="utf-8")
    assert "from tools.generate_explore_hh_day import generate as gen_hh_day" in text
    assert "gen_hh_day()" in text


def test_clock_of_covers_the_whole_day():
    assert hh.clock_of(1) == "00:00"
    assert hh.clock_of(37) == "18:00"
    assert hh.clock_of(48) == "23:30"
