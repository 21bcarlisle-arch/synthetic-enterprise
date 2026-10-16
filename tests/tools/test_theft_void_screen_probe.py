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


def _fixture_run():
    """Four accounts over 2019-2020, every month an actual read: a flat home, one that follows the
    published profile, one whose winter is far steeper than it, and an incoming occupier whose
    first stub is void."""
    import calendar
    import datetime as dt

    from company.billing.unread_month_estimate import profile_weight

    bills, reads = [], []

    def add(cid, start, end, kwh):
        bills.append({"customer_id": cid, "commodity": "electricity",
                      "period_start": start.isoformat(), "period_end": end.isoformat()})
        reads.append({"customer_id": cid, "period_end": end.isoformat(),
                      "true_consumption_kwh": kwh, "status": "actual"})

    for year in (2019, 2020):
        for month in range(1, 13):
            start = dt.date(year, month, 1)
            end = dt.date(year, month, calendar.monthrange(year, month)[1])
            add("FLAT", start, end, 250.0)
            add("PEAKY", start, end, 600.0 if month in (1, 2, 3, 11, 12) else 60.0)
            add("PROFILE", start, end, 3000.0 * profile_weight("electricity", start, end))
            if (year, month) == (2019, 3):
                add("OCC-fixture", dt.date(2019, 3, 20), end, 0.0)
            elif (year, month) > (2019, 3):
                add("OCC-fixture", start, end, 250.0)
    registry = {"FLAT": 3000.0, "PEAKY": 3000.0, "PROFILE": 3000.0, "OCC-fixture": 3000.0}
    return {"bills": bills, "meter_read_log": reads, "opening_registry_kwh_by_customer": registry}


def test_occupied_homes_flag_by_shape_and_a_void_on_the_incoming_account_is_not_one():
    """Defect: the occupied-home source files the incoming account's void stub as an occupied
    home, flags a flat home, or never reaches the own-reads basis, so the third source the
    voids-and-thefts table omitted is priced from the wrong rows or not at all."""
    from tools.theft_void_screen_probe import occupied_windows

    rows = {a["customer_id"]: a for a in occupied_windows(_fixture_run())}
    flagged = {cid: [m for m in a["monthly"] if _flagged(m["ratio"], 0.65)] for cid, a in rows.items()}
    # Every branch is reachable before any is graded: a void, an opening month, an own-reads month.
    every = [m for a in rows.values() for m in a["monthly"]]
    assert {m["cause"] for m in every} == {"void", "occupied"}
    assert {m["basis"] for m in every} == {"opening", "own_reads"}

    assert [m["cause"] for m in flagged["OCC-fixture"]] == ["void"], flagged["OCC-fixture"]
    # The void ends at the first month with any use; the occupier's months after it are theirs.
    assert [m["cause"] for m in rows["OCC-fixture"]["monthly"]].count("void") == 1
    assert not flagged["FLAT"], flagged["FLAT"]
    # A home that follows the published profile is what the company expects, to the month.
    assert not [m for m in rows["PROFILE"]["monthly"] if _flagged(m["ratio"], 0.9)]
    peaky = flagged["PEAKY"]
    assert peaky and all(m["cause"] == "occupied" and m["basis"] == "own_reads" for m in peaky)
    assert all(4 <= m["month"] <= 10 for m in peaky), peaky
    # The shape error is a month's, not the year's: the annual window does not flag it.
    assert not [y for y in rows["PEAKY"]["annual"] if _flagged(y["ratio"], 0.65)]
