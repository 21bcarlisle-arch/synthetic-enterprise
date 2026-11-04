"""INV_CAST_TARIFF_LABEL_IS_THE_BILLED_TERM (seventh cold read, N16): the tariff an Explore moment
prints is the contracted term the leg's bills record for the moment's date.

Defect this catches: the cast published with the 0a6391d186 book printed "Standard variable" beside
every joining household's fixed first term, and a long-ended fix ("Fixed from 28 Apr 2019") on a
household billed on the default tariff in Dec 2022; a rebuilt cast printed gas "Fixed" where the gas
bill recorded the default tariff. Mutations, each reds this file: a label graded on one panel only;
an unprefixed label read for one leg only; a fuel-prefixed label read for the other fuel; the SVT stay
dated by its cap-window term rather than its unbroken run; the boundary-day reading as a breach.
"""
from __future__ import annotations

import json

from tools import domain_invariant_runner as runner

ROW = "INV_CAST_TARIFF_LABEL_IS_THE_BILLED_TERM"


def _terms(start, end, kind):
    return {"tariff_effective_from": start, "tariff_effective_to": end, "tariff_type": kind,
            "unit_rate_p_per_kwh": 15.0}


def _leg(cid, fuel):
    """A 2020 leg: fixed from 1 Jan to 30 Jun, then the default tariff, cut at the October cap window."""
    periods = []
    for m in range(1, 13):
        start = "2020-{:02d}-01".format(m)
        end = runner._month_end(runner._d(start)).isoformat()
        term = (_terms("2020-01-01", "2020-07-01", "fixed") if m <= 6 else
                _terms("2020-07-01", "2020-10-01", "svt") if m <= 9 else _terms("2020-10-01", None, "svt"))
        periods.append({"commodity": fuel, "period_start": start, "period_end": end, "reads": [],
                        "contracted_terms": [term]})
    return {"customer_id": cid, "billing_account_id": "H", "segment": "resi", "periods": periods,
            "payments": []}


def _cast(tmp_path, *moments):
    slots = [{"household": "H", "fuels": ["electricity", "gas"], "moments": [
        {"iso": iso, "kind": "bill", "supplier": [{"k": "Tariff", "v": label}],
         "portal": {"tariff": portal or label}} for iso, label, portal in moments]}]
    path = tmp_path / "explore_cast.json"
    path.write_text(json.dumps({"slots": slots}))
    return path


def _grade(tmp_path, iso, label, portal=None):
    t = runner.grade_cast_tariff_labels(_cast(tmp_path, (iso, label, portal)),
                                        {"H": _leg("H", "electricity"), "Hg": _leg("Hg", "gas")})
    return t.checked, sorted(b["side"] for b in t.breaches), sorted(f["side"] for f in t.flags)


def test_every_leg_of_the_row_can_be_taken(tmp_path):
    assert _grade(tmp_path, "2020-03-01", "Fixed from 1 Jan 2020") == (2, [], [])
    assert _grade(tmp_path, "2020-03-01", "Standard variable") == (2, ["kind", "kind"], [])
    assert _grade(tmp_path, "2020-03-01", "Fixed from 1 Feb 2020") == (2, ["fixed start", "fixed start"], [])
    # The default tariff since 1 Jul, across the October cap-window cut: one stay.
    assert _grade(tmp_path, "2020-11-01", "Standard variable since 1 Jul 2020") == (2, [], [])
    assert _grade(tmp_path, "2020-11-01", "Standard variable since 1 Oct 2020") == (2, [], ["svt since"] * 2)
    assert _grade(tmp_path, "2020-07-01", "Fixed from 1 Jan 2020") == (2, [], ["term boundary"] * 2)
    assert _grade(tmp_path, "2020-03-01", "Something else") == (2, [], ["label not read"] * 2)


def test_either_panel_and_each_fuel_are_graded(tmp_path):
    assert _grade(tmp_path, "2020-03-01", "Fixed from 1 Jan 2020", "Standard variable") == (2, ["kind", "kind"], [])
    split = "Electricity: Fixed from 1 Jan 2020; Gas: Standard variable since 1 Jan 2020"
    assert _grade(tmp_path, "2020-03-01", split) == (2, ["kind"], [])


def test_after_the_last_supplied_day_the_term_it_ended_on_is_graded(tmp_path):
    assert _grade(tmp_path, "2021-02-01", "Standard variable since 1 Jul 2020") == (2, [], [])
    assert _grade(tmp_path, "2021-02-01", "Fixed from 1 Jan 2020") == (2, ["kind", "kind"], [])


def test_a_book_read_without_a_cast_is_never_clean(tmp_path):
    book = {"H": _leg("H", "electricity")}
    assert runner.run([{"id": ROW}], book)[0]["status"] == "NOT_IN_EXPORT"
    book["H"]["cast_tariffs"] = runner.load_cast_tariffs(_cast(tmp_path, ("2020-03-01", "Standard variable", None)))["H"]
    assert runner.run([{"id": ROW}], book)[0]["status"] == "BREACHED"
