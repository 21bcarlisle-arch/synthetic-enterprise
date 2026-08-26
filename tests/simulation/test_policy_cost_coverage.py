"""A rate served from outside its own table's window must SAY SO (2026-08-14).

WORKER_FINDING_THE_COST_STACK_CLAMPS_SILENTLY_INSIDE_ITS_OWN_RUN_WINDOW: all 13 year-keyed
policy/network tables end at 2024, the run bills to 2025-06-07, and seven readers return
`table[max(table)]` for any later date with nothing distinguishing that from a tabulated rate.
The 2025 published stack is £391,531.72 -- 8.09% of the total -- and every pound of it is priced
on at least one clamped table.

These test the INSTRUMENT'S SELF-REPORT, not the rates. Clamping is a defensible modelling
choice; clamping silently is the fail-open shape R15 names.
"""
from __future__ import annotations

from pathlib import Path

from simulation import policy_costs as pc

ROOT = Path(__file__).resolve().parents[2]


def test_the_census_covers_every_registered_table():
    """VACUITY GUARD, and the same census leg the year-basis control already runs. A table that
    slips the registry is invisible to every other test here, so this one is unconditional."""
    assert len(pc.YEAR_KEY_BASIS) >= 13
    for name in pc.YEAR_KEY_BASIS:
        first, last = pc.table_coverage(name)
        assert isinstance(first, int) and isinstance(last, int)
        assert first <= last, f"{name} coverage is inverted"


def test_a_date_inside_the_window_is_not_extrapolated():
    """Non-vacuity: the marker must be capable of saying NO, or it says nothing."""
    for name in pc.YEAR_KEY_BASIS:
        first, last = pc.table_coverage(name)
        inside = f"{(first + last) // 2:04d}-06-15"      # June: same key under either basis
        assert not pc.is_extrapolated(name, inside), name


def test_the_2025_clamp_the_finding_measured():
    """The finding's own table, reproduced from the shipped functions.

    Nine Apr-Mar tables clamp from 2025-04-01; four calendar-keyed ones from 2025-01-01. That
    split is the whole reason the marker is keyed through each table's DECLARED basis: asking the
    wrong basis would misreport exactly the Jan-Mar quarter that the 2026-08-13 network-charge
    defect turned on.

    RE-AIMED 2026-08-26. As written this asserted a CENSUS -- "4 in January, all 13 in
    April" -- which was true on 2026-08-14 and is not now: `_RO_COST_BY_OY_START`,
    `_CCL_ELECTRICITY_RATE_BY_YEAR` and `_GAS_CCL_RATE_BY_YEAR` have since been extended
    to 2025, so 10 clamp in April rather than 13. Three tables getting their real 2025
    rates is the defect being FIXED, and a test that reds on the repair is a test
    asserting the model stays bad. What the finding was actually about is the BASIS
    SPLIT, so that is what is pinned here, derived from the tables on both sides.
    """
    jan, apr = "2025-01-05", "2025-04-05"
    calendar_clamped = set(pc.extrapolated_tables(jan))
    all_clamped = set(pc.extrapolated_tables(apr))

    def _short(basis):
        return {n for n, b in pc.YEAR_KEY_BASIS.items() if b == basis and pc.table_coverage(n)[1] < 2025}

    # January clamps the calendar-keyed tables that stop before 2025, and ONLY those: an
    # Apr-Mar table is still inside obligation year 2024 in January.
    assert calendar_clamped == _short("calendar"), "the January answer is not the calendar set"
    # April additionally clamps the Apr-Mar tables that stop before 2025 -- the Jan-Mar
    # quarter that the 2026-08-13 network-charge defect turned on.
    assert all_clamped == _short("calendar") | _short("apr_mar")
    assert all_clamped > calendar_clamped, "April must clamp strictly more than January"
    # NON-VACUITY: both sides must be non-empty, or the set equality above passes on {} == {}.
    assert calendar_clamped and (all_clamped - calendar_clamped)


def test_the_leading_edge_the_finding_said_did_not_exist():
    """The finding's "Not claimed" section states the clamp "does not affect years before 2025 --
    every other year in the run window is inside every table's coverage". It does.

    January 2016 keys, under the apr_mar basis, to obligation year 2015 -- below the first key of
    all nine Apr-Mar tables. The live run carries 12 bills dated 2016-01-31, so those bills are
    priced on a clamped rate at the LEADING edge. Found because coverage is DERIVED from the
    tables rather than taken from the claim; a forward-only marker would have inherited it.
    """
    assert pc.is_extrapolated("_RO_COST_BY_OY_START", "2016-01-31")
    assert not pc.is_extrapolated("_CFD_LEVY_BY_YEAR", "2016-01-31")   # calendar-keyed: covered

    report = pc.coverage_report("2016-01-31", "2025-06-07")
    leading = [n for n, i in report["tables"].items() if i["clamped_at_start"]]
    assert len(leading) == 9
    assert all(pc.YEAR_KEY_BASIS[n] == "apr_mar" for n in leading)


def test_coverage_is_derived_from_the_tables_not_declared_beside_them():
    """MUTATION: append a year to a table and the coverage must move with it, with nothing else
    edited. A hand-kept first/last pair is a second copy of a fact the dict already states, and
    the copy is wrong the first time somebody extends a table and forgets.

    SUBJECT RE-AIMED 2026-08-26, and the reason is the point of the test. It mutated
    `_RO_COST_BY_OY_START`, which has since been extended to 2025 for real -- so the
    "before" assertion reds not because coverage stopped being derived but because the
    table it picked got fixed. The subject is now CHOSEN from the tables that still stop
    short, so this cannot expire again the next time one is extended.
    """
    name = next(n for n in pc.YEAR_KEY_BASIS if pc.table_coverage(n)[1] < 2025)
    table = getattr(pc, name)
    stop = pc.table_coverage(name)[1]
    probe = f"{stop + 1:04d}-06-07"           # June: same key under either basis
    assert pc.is_extrapolated(name, probe), name
    table[stop + 1] = table[stop]
    try:
        assert not pc.is_extrapolated(name, probe), (
            "extending the table did not move its coverage -- the window is not derived"
        )
        assert pc.table_coverage(name)[1] == stop + 1
    finally:
        del table[stop + 1]
    assert pc.is_extrapolated(name, probe)   # restored


def test_a_fully_covered_window_reports_nothing():
    """R15 both ways: the report must be able to come back clean, or "everything is extrapolated"
    is a constant rather than a measurement."""
    report = pc.coverage_report("2022-01-01", "2023-01-01")
    assert report["any_extrapolated"] is False
    assert report["tables"] == {}


# ── the PUBLISHED half: a measurement nobody can read is not a disclosure ────────────────────

def _note(window=("2016-01-31", "2025-06-07")):
    from saas.reporting.annual_report import _extrapolation_note
    return _extrapolation_note({"policy_cost_coverage": pc.coverage_report(*window)})


def test_the_note_reaches_the_published_report():
    note = _note()
    assert "EXTRAPOLATED RATES" in note
    assert "13 of 13" in note
    assert "2025-04-01" in note and "2025-01-01" in note
    # It states the limitation without claiming the numbers are wrong -- the finding graded this
    # LATENT precisely because it establishes the former and not the latter.
    assert "not a claim that the carried-forward rates are wrong" in note


def test_the_note_is_derived_from_the_tables_not_narrated():
    """MUTATION: extend every table past the window and the note must DISAPPEAR. A note carrying
    a hardcoded "2025" or "13 tables" would be a third copy of the same fact, false the first
    time either moved -- the trap the fuel-mix reconciliation note avoided the same week."""
    # BOTH ends, because the note reports both. Extending only the forward edge leaves the
    # Green Gas Levy (first key 2021) still clamping at the start, so the note correctly survives
    # -- which is what the first draft of this test mistook for narration.
    added = []
    for name in pc.YEAR_KEY_BASIS:
        table = getattr(pc, name)
        first, last = min(table), max(table)
        for y in (last + 1, last + 2):
            table[y] = table[last]
            added.append((table, y))
        for y in range(2014, first):
            table[y] = table[first]
            added.append((table, y))
    try:
        assert _note() == "", "the note survived the tables covering the window -- it is narrated"
    finally:
        for table, y in added:
            del table[y]
    assert "EXTRAPOLATED RATES" in _note(), "restore failed"


def test_the_note_is_silent_when_there_is_nothing_to_say():
    assert _note(("2022-01-01", "2023-01-01")) == ""


def test_the_renderer_cannot_reach_across_the_wall_to_compute_this():
    """The architectural reason the status travels in the run output rather than being computed
    at render time: `saas/` never imports `simulation/`. A renderer that asked the tables directly
    would be the company reading the world's internals in order to describe them."""
    src = (ROOT / "saas" / "reporting" / "annual_report.py").read_text()
    # PARSED, not grepped. Two earlier drafts of this assertion failed on innocent text: the
    # substring "policy_costs" matches the local `_section_policy_costs`, and "from simulation"
    # matches four docstrings that say "from simulation data". A wall check that reds on prose
    # gets deleted by whoever hits it next, which is how a real control becomes an absent one.
    import ast
    imported = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            imported.add(node.module.split(".")[0])
    assert "simulation" not in imported and "sim" not in imported, (
        f"annual_report imports the sim ({sorted(imported & {'simulation', 'sim'})}) -- reaching "
        "into the world's rate tables is an epistemic-wall crossing, and the disclosure note is "
        "exactly the reason someone would try"
    )
    assert 'run_output.get("policy_cost_coverage"' in src, (
        "the coverage block is no longer carried through from the run output, so the report has "
        "nothing to render and the disclosure silently disappears"
    )
