"""N13 (gas) and N17 (electricity): a measured month a year after another is not the same number.

Every leg of both rows is reached before any is asserted, so an evaluator that breaches
everything, or nothing, cannot pass. The bounds come from the committed file, not from here."""
import math

from tools import domain_invariant_runner as runner

GAS = "INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR"
ELEC = "INV_ELEC_MONTHLY_USE_MOVES_YEAR_ON_YEAR_LIKE_A_HOUSEHOLD"
ROWS = {i["id"]: i for i in runner.load_invariants() if i["id"] in (GAS, ELEC)}


def _leg(cid, fuel, kwh, years=(2018, 2019, 2020, 2021), read_type="A"):
    """One account; `kwh(year, month)` gives each whole calendar month's use, read at both ends."""
    periods, reading = [], 1000.0
    for y in years:
        for m in range(1, 13):
            start = runner.date(y, m, 1)
            end = runner._month_end(start)
            use = round(kwh(y, m), 1)
            periods.append({
                "commodity": fuel, "period_start": start.isoformat(), "period_end": end.isoformat(),
                "days_in_period": (end - start).days + 1, "meter_serial": "M" + cid,
                "mprn": "2" if fuel == "gas" else None, "mpan": "1" if fuel == "electricity" else None,
                "reads": [{"register_id": "1", "read_date": start.isoformat(), "read_kwh": reading,
                           "read_type": "carried_forward"},
                          {"register_id": "1", "read_date": end.isoformat(), "read_kwh": reading + use,
                           "read_type": read_type}]})
            reading = round(reading + use, 1)
    return cid, {"customer_id": cid, "segment": "resi", "periods": periods, "payments": []}


def _season(m):
    return 1.0 + 0.8 * math.cos((m - 1) / 12 * 2 * math.pi)


def _moving(y, m):
    """A home whose month moves by several percent a year, differently each month."""
    return 300.0 * _season(m) * (1 + 0.1 * math.sin(2 * y + 3 * m))


def _grade(inv_id, *accounts):
    return runner.run([ROWS[inv_id]], dict(accounts))[0]


def test_every_leg_of_both_rows_is_reachable_and_the_bounds_come_from_the_file():
    """MUTATION -- delete any `tally.hit` in either evaluator and its leg below goes CLEAN."""
    def repeats(months):
        return lambda y, m: 300.0 * _season(m) if m in months else _moving(y, m)

    gas = {
        "moving": _grade(GAS, _leg("G1", "gas", _moving)),
        "three_repeats": _grade(GAS, _leg("G2", "gas", lambda y, m: 50.0 if (y, m) in
                                         {(2018, 7), (2019, 7), (2020, 7), (2021, 7)} else _moving(y, m))),
        "two_repeats": _grade(GAS, _leg("G3", "gas", lambda y, m: 50.0 if (y, m) in
                                       {(2019, 7), (2020, 7), (2020, 8), (2021, 8)} else _moving(y, m))),
        "winter_run": _grade(GAS, _leg("G4", "gas", lambda y, m: 900.0 if (y, m) in
                                      {(2019, 1), (2020, 1), (2021, 1)} else _moving(y, m))),
        "winter_still": _grade(GAS, _leg("G5", "gas", lambda y, m: 300 * _season(m) * (1 + 0.003 * (y - 2018) * (1 if m in runner._WINTER else 30)))),
        "estimated": _grade(GAS, _leg("G6", "gas", repeats(set(range(1, 13))), read_type="E")),
    }
    flat = _leg("E2", "electricity", lambda y, m: 250.0 + m)
    # half the months repeat exactly, half move 15%: the median is in band, the zero bunch is not
    bunched = _leg("E3", "electricity", lambda y, m: 250.0 + m if m % 2 else
                   (250.0 + m) * (1.15 if y % 2 else 1.0))
    elec = {
        "moving": _grade(ELEC, _leg("E1", "electricity", _moving)),
        "flat": _grade(ELEC, flat),
        "bunched": _grade(ELEC, bunched),
    }
    got = {"gas " + k: (r["status"], sorted({e["side"].split(" 20")[0] for e in
                                               r.get("breach_examples", []) + r.get("flag_examples", [])}))
           for k, r in gas.items()}
    got.update({"elec " + k: (r["status"], sorted({e["side"] for e in r.get("breach_examples", [])}))
                for k, r in elec.items()})
    assert got == {
        "gas moving": ("CLEAN", []),
        "gas three_repeats": ("BREACHED", ["book repeat share", "repeats"]),
        "gas two_repeats": ("BREACHED", ["book repeat share", "exactly two repeats"]),
        "gas winter_run": ("BREACHED", ["book repeat share", "winter run"]),
        "gas winter_still": ("FLAGGED", ["winter dispersion below floor"]),
        "gas estimated": ("UNREACHED", []),
        "elec moving": ("CLEAN", []),
        "elec flat": ("BREACHED", ["above chance", "below"]),
        "elec bunched": ("BREACHED", ["above chance"]),
    }, got
    assert elec["flat"]["book"]["band"] == [ROWS[ELEC]["lower"], ROWS[ELEC]["upper"]]


def test_a_repeat_is_held_to_the_records_one_decimal_place():
    """0.1 kWh apart is two readings, not one: 0.05 is the half-unit either side."""
    near = _grade(GAS, _leg("G7", "gas", lambda y, m: 50.0 + 0.1 * (y == 2020) if (y, m) in
                            {(2019, 7), (2020, 7), (2021, 7)} else _moving(y, m)))
    assert near["status"] == "CLEAN", near
