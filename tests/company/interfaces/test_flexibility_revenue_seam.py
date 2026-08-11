"""The flexibility-revenue seam's contract — and the ways this cut could rot silently.

WHY THIS FILE EXISTS (R15: a control must be able to FAIL on its own named defect)
---------------------------------------------------------------------------------
KNIFE pass 3, `A_composition_lift` step 18, moved the supplier's domestic and
I&C flexibility revenue books out of `simulation/run_phase2b.py::main()` into
`company/market/flexibility_revenue.py` behind
`company/interfaces/flexibility_revenue.py` — two wall crossings
(`company.market.flexibility_revenue_book`,
`company.market.ic_flexibility_revenue`).

The import count understates what moved. `FlexibilityRevenueBook.compute_year`
took the world's `HouseholdDemandRegister` and called `.dynamic_assets()` on it,
so a company module held a live SIM object and pulled from it at will. Deleting
the import while still passing the object would have moved the edge, not cut it.

The epistemic-wall ratchet polices the STATIC half: a module-scope
`company.market.flexibility_revenue -> simulation.*` import is a new class-(a)
edge, the forbidden direction, and reds the suite. Four things it cannot see:

1. **A lazy import.** The ratchet covers static imports only; an in-function
   `import simulation.…` escapes it. The natural convenience change here is for
   the builder to reach for the world's register again rather than be handed a
   snapshot. So control 1 is BEHAVIOURAL: it builds a real `FlexibilityRevenue`
   in a clean interpreter and asks which modules the import system actually
   loaded. Its mutation performs the defect on a COPY of the real source and
   re-runs the same detector, so the control is tried rather than trusted (and
   no repo file is edited mid-run, which would corrupt `inspect.getsource` for
   every other test in the session).

2. **A silently reordered, dropped or re-rounded block.** The claim this cut
   rests on is that the composition computes what the inlined code computed.
   Nothing static sees the DFS launch gate go, or the two totals stop being
   summed; the effect is not a crash but a different revenue figure. Control 2
   replicates the PRE-CUT inlined sequence, transcribed from the source it was
   lifted out of at git `8dd04db1d` — not from the module under test, which
   would be a mirror — and asserts all four outputs are identical.

3. **THE ROSTER DEFECT, and it is the one this cut actually introduces.** Before
   the cut the `segment == "I&C"` filter sat at the point of use, inside
   `main()`, three lines from the book that consumed it. Now the roster is built
   by a named helper and handed through one signature: drop the filter and every
   non-I&C customer above the 200 MWh eligibility floor is offered to a DSR
   aggregator, changing the flexibility total — while every test exercising
   `ICFlexibilityRevenueBook` directly stays green, because the book would be
   given exactly what the caller chose to give it. Controls 3 and 4 cover the
   two halves of that: 4 is behavioural on the helper, 3 is an AST check over the
   REAL call site with a vacuity guard (a source with no such call would make it
   pass for free).

4. **A snapshot filed under the wrong year.** This one is closed BY
   CONSTRUCTION rather than by a control, and control 5 proves the construction
   rather than asserting it. The book derives its own `YYYY-12-31` query date
   from the year it is pricing; a snapshot keyed by anything else (a year int, a
   list position) would let 2021's assets be served while the book believed it
   was pricing 2023, silently. So the snapshot is keyed by the same date string
   the book asks for and the adapter LOOKS IT UP — a misaligned snapshot raises
   at the first customer. On the world's side one variable serves as both key
   and query, so the two cannot drift.

Each `test_mutation_*` performs the named defect rather than asserting it is
impossible.

VACUITY, stated once for the whole file. The fixture years are 2021 and 2023,
chosen because DFS revenue is zero in 2021 and non-zero in 2023 (NESO launched
it in October 2022) and the I&C Capacity Market clearing price differs between
them (£8.40 vs £15.97/kW/yr). A fixture wholly before 2022 would pass control 2
with the DFS block deleted; one wholly after would pass with the launch gate
deleted. The fixture also carries a NON-I&C customer ABOVE the 200 MWh
eligibility floor — without one, dropping the segment filter would add nothing
and control 4's mutation could not fail. The guards below assert all three
properties rather than leaving them to the reader.
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
import tempfile
import textwrap

import pytest

from company.interfaces import flexibility_revenue as door
from company.market import flexibility_revenue as impl
from company.market.flexibility_revenue_book import FlexibilityRevenueBook
from company.market.ic_flexibility_revenue import (
    _CM_DELIVERY_GBP_PER_KW_YR,
    _IC_MIN_EAC_KWH,
    ICFlexibilityRevenueBook,
)

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RUN_MODULE_PATH = os.path.join(REPO_ROOT, "simulation", "run_phase2b.py")
IMPL_PATH = os.path.join(REPO_ROOT, "company", "market", "flexibility_revenue.py")

FIXTURE_YEARS = ["2021", "2023"]


# ---------------------------------------------------------------------------
# Fixtures — the smallest book that exercises both sides of the door, both
# sides of the DFS launch gate, and both sides of the segment filter.
# ---------------------------------------------------------------------------


def _elec_customers() -> list[dict]:
    return [
        # Eligible I&C: above the aggregator floor.
        {"customer_id": "E-IC-1", "segment": "I&C"},
        # I&C but below the floor — exercises the book's own eligibility test.
        {"customer_id": "E-IC-2", "segment": "I&C"},
        # NOT I&C but ABOVE the floor: this is the customer that makes control
        # 4's mutation able to fail at all.
        {"customer_id": "E-SME-1", "segment": "SME"},
        {"customer_id": "E-RESI-1", "segment": "resi"},
    ]


def _eac_by_cid() -> dict:
    return {
        "E-IC-1": 2_000_000.0,
        "E-IC-2": 100_000.0,
        "E-SME-1": 400_000.0,
        "E-RESI-1": 3_500.0,
    }


# Asset flags per customer per year end. E-RESI-1 gains a battery in 2023, so a
# snapshot frozen at one year would produce a different answer from a live one.
_ASSETS: dict[str, dict[str, dict]] = {
    "2021-12-31": {
        "E-IC-1": {},
        "E-IC-2": {},
        "E-SME-1": {},
        "E-RESI-1": {"ev": True},
    },
    "2023-12-31": {
        "E-IC-1": {},
        "E-IC-2": {},
        "E-SME-1": {"ashp": True},
        "E-RESI-1": {"ev": True, "battery": True},
    },
}


class _FakeHouseholdRegister:
    """Stands in for the world's register. Records what it was asked."""

    def __init__(self) -> None:
        self.queried_dates: list[str] = []

    def dynamic_assets(self, customer_id: str, date_str: str) -> dict:
        self.queried_dates.append(date_str)
        return _ASSETS[date_str][customer_id]


def _elec_cids() -> list[str]:
    return [c["customer_id"] for c in _elec_customers()]


def _ic_roster(customers: list[dict], eac: dict) -> list[tuple]:
    return [
        (c["customer_id"], eac.get(c["customer_id"], 0.0))
        for c in customers
        if c.get("segment") == "I&C"
    ]


def _build() -> impl.FlexibilityRevenue:
    return impl.build_flexibility_revenue(
        report_years=FIXTURE_YEARS,
        domestic_assets_by_date=_ASSETS,
        ic_elec_roster=_ic_roster(_elec_customers(), _eac_by_cid()),
    )


# ---------------------------------------------------------------------------
# The fixture's own properties — the vacuity guards the file's docstring names.
# ---------------------------------------------------------------------------


def test_fixture_is_not_vacuous_dfs_gate_cm_prices_and_a_non_ic_above_the_floor():
    built = _build()

    per_year = built.domestic_summary["per_year"]
    assert per_year[2021]["dfs_gbp"] == 0.0, "2021 must sit BEFORE the DFS launch gate"
    assert per_year[2023]["dfs_gbp"] > 0.0, "2023 must sit AFTER the DFS launch gate"

    assert _CM_DELIVERY_GBP_PER_KW_YR[2021] != _CM_DELIVERY_GBP_PER_KW_YR[2023], (
        "the two fixture years share a CM clearing price — control 2 would pass "
        "with the year threaded through wrongly"
    )

    non_ic_above_floor = [
        c["customer_id"]
        for c in _elec_customers()
        if c.get("segment") != "I&C" and _eac_by_cid()[c["customer_id"]] >= _IC_MIN_EAC_KWH
    ]
    assert non_ic_above_floor, (
        "no non-I&C customer clears the aggregator floor — dropping the segment "
        "filter would change nothing and control 4 could not fail"
    )

    assert built.domestic_summary["total_flexibility_revenue_gbp"] > 0
    assert built.ic_summary["total_ic_flex_revenue_gbp"] > 0
    assert built.total_revenue_gbp > 0
    assert set(built.domestic_revenue_by_year) == set(FIXTURE_YEARS)


def test_the_door_re_exports_the_implementation():
    assert door.build_flexibility_revenue is impl.build_flexibility_revenue
    assert door.FlexibilityRevenue is impl.FlexibilityRevenue


# ---------------------------------------------------------------------------
# CONTROL 1 — the company module must not reach back into the world, statically
# OR lazily. Behavioural: what did the import system actually load?
# ---------------------------------------------------------------------------

_PROBE = textwrap.dedent(
    """
    import json, sys
    sys.path.insert(0, {repo!r})
    sys.path.insert(0, {pkgdir!r})
    import {modname} as m

    m.build_flexibility_revenue(
        report_years=["2023"],
        domestic_assets_by_date={{"2023-12-31": {{"E-RESI-1": {{"ev": True}}}}}},
        ic_elec_roster=[("E-IC-1", 2000000.0)],
    )

    walled = sorted(
        n for n in sys.modules
        if n in ("sim", "simulation") or n.startswith(("sim.", "simulation."))
    )
    print("WALLED_MODULES=" + json.dumps(walled))
    """
)


def _walled_modules_loaded_by(source: str) -> list[str]:
    """Run `source` as the impl module in a clean interpreter; report sim loads.

    THE detector, used unchanged by both the real test and its mutation.
    """
    with tempfile.TemporaryDirectory() as pkgdir:
        modname = "_knife3_step18_subject"
        with open(os.path.join(pkgdir, modname + ".py"), "w") as fh:
            fh.write(source)
        probe = _PROBE.format(repo=REPO_ROOT, pkgdir=pkgdir, modname=modname)
        proc = subprocess.run(
            [sys.executable, "-c", probe],
            cwd=pkgdir,
            capture_output=True,
            text=True,
            timeout=180,
        )
    assert proc.returncode == 0, (
        f"the probe itself failed — an unavailable check is a FAILED check, "
        f"never a skip.\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    marker = [ln for ln in proc.stdout.splitlines() if ln.startswith("WALLED_MODULES=")]
    assert len(marker) == 1, f"probe produced no verdict line:\n{proc.stdout}"
    return json.loads(marker[0].split("=", 1)[1])


def test_booking_flexibility_revenue_loads_no_world_module():
    with open(IMPL_PATH) as fh:
        real_source = fh.read()
    assert _walled_modules_loaded_by(real_source) == []


def test_mutation_a_lazy_world_import_is_caught_by_the_same_detector():
    """Perform the defect on a copy of the real source, same detector."""
    with open(IMPL_PATH) as fh:
        mutated = fh.read()
    anchor = "    domestic_book = FlexibilityRevenueBook()"
    assert anchor in mutated, "anchor moved — this mutation is no longer the defect"
    mutated = mutated.replace(
        anchor,
        "    import simulation.household_demand  # noqa: F401  <-- the defect\n" + anchor,
        1,
    )
    loaded = _walled_modules_loaded_by(mutated)
    assert "simulation.household_demand" in loaded, (
        "control 1 did not fire on a lazy world import — it cannot fail, so it "
        "is not evidence"
    )


# ---------------------------------------------------------------------------
# CONTROL 2 — behaviour identity against the PRE-CUT sequence, transcribed from
# simulation/run_phase2b.py as it stood before step 18 (git 8dd04db1d), NOT from
# the module under test.
# ---------------------------------------------------------------------------


def _pre_cut_flexibility(
    household_demand_register,
    _all_years: list[str],
    ELEC_CUSTOMERS: list[dict],
    EFFECTIVE_EAC_KWH: dict,
) -> tuple[dict, dict, dict, float]:
    # Phase AF: DSR/Capacity Market flexibility revenue.
    _flex_book = FlexibilityRevenueBook()
    _elec_cids = [c["customer_id"] for c in ELEC_CUSTOMERS]
    _flex_by_year: dict[str, dict[str, float]] = {}
    if household_demand_register is not None:
        for _yr_str in _all_years:
            _yr_int = int(_yr_str)
            _by_cid = _flex_book.compute_year(_yr_int, household_demand_register, _elec_cids)
            _flex_by_year[_yr_str] = _by_cid
    flexibility_revenue_summary = _flex_book.flexibility_summary()
    total_flexibility_revenue = _flex_book.total_revenue_all_years()

    # Phase NX: I&C Demand Response Enrollment (CM/DFS for process flexibility).
    _ic_flex_book = ICFlexibilityRevenueBook()
    _ic_elec_customers = [c for c in ELEC_CUSTOMERS if c.get("segment") == "I&C"]
    _ic_flex_input = [
        (c["customer_id"], EFFECTIVE_EAC_KWH.get(c["customer_id"], 0.0))
        for c in _ic_elec_customers
    ]
    for _yr_str in _all_years:
        _ic_flex_book.compute_year(int(_yr_str), _ic_flex_input)
    ic_flexibility_summary = _ic_flex_book.flexibility_summary()
    total_flexibility_revenue += _ic_flex_book.total_revenue_all_years()

    return (
        flexibility_revenue_summary,
        ic_flexibility_summary,
        _flex_by_year,
        total_flexibility_revenue,
    )


def test_the_moved_composition_is_identical_to_the_pre_cut_sequence():
    domestic, ic, by_year, total = _pre_cut_flexibility(
        _FakeHouseholdRegister(),
        FIXTURE_YEARS,
        _elec_customers(),
        _eac_by_cid(),
    )
    built = _build()
    assert built.domestic_summary == domestic
    assert built.ic_summary == ic
    assert built.domestic_revenue_by_year == by_year
    assert built.total_revenue_gbp == total


def test_the_domestic_book_is_skipped_when_the_world_has_no_register():
    """The `household_demand_register is None` branch survived the move."""
    domestic, ic, by_year, total = _pre_cut_flexibility(
        None, FIXTURE_YEARS, _elec_customers(), _eac_by_cid()
    )
    built = impl.build_flexibility_revenue(
        report_years=FIXTURE_YEARS,
        domestic_assets_by_date=None,
        ic_elec_roster=_ic_roster(_elec_customers(), _eac_by_cid()),
    )
    assert built.domestic_summary == domestic
    assert built.domestic_revenue_by_year == by_year == {}
    assert built.ic_summary == ic
    assert built.total_revenue_gbp == total
    assert total > 0, "the I&C half must still book — otherwise this proves nothing"


def test_mutation_dropping_the_dfs_launch_gate_breaks_the_identity():
    """The identity control fires when the moved code stops matching."""
    # The defect: DFS revenue booked in every year, launch gate ignored — the
    # shape of a transcription slip in a year-conditional block.
    from company.market.flexibility_potential import (
        _estimate_capacity_revenue,
        _estimate_dfs_revenue,
        _estimate_flex_kw,
    )

    mutated_total = 0.0
    for year_str in FIXTURE_YEARS:
        for cid in _elec_cids():
            assets = _ASSETS[f"{int(year_str)}-12-31"][cid]
            has_ev = bool(assets.get("ev", False))
            has_ashp = bool(assets.get("ashp", False))
            has_battery = bool(assets.get("battery", False))
            if not (has_ev or has_ashp or has_battery):
                continue
            flex_kw = _estimate_flex_kw(has_ev, has_ashp, has_battery)
            mutated_total += round(_estimate_capacity_revenue(flex_kw), 2)
            mutated_total += round(_estimate_dfs_revenue(flex_kw), 2)  # <-- ungated

    real_total = _build().domestic_summary["total_flexibility_revenue_gbp"]
    assert round(mutated_total, 2) != real_total, (
        "booking DFS revenue before its launch year did not move the domestic "
        "figure — control 2 could not fail on this fixture"
    )


# ---------------------------------------------------------------------------
# CONTROL 3 — the call site hands the world's own rosters to the right door
# parameters, and the segment filter is still in the helper it moved into.
# ---------------------------------------------------------------------------

_CALL_NAME = "build_flexibility_revenue"
_ROSTER_HELPER = "_ic_flex_roster"
_SNAPSHOT_HELPER = "_domestic_flex_assets_by_date"


def _call_site_findings(source: str) -> tuple[list[str], int]:
    """Findings about the seam's call site and its two helpers.

    THE checker, used unchanged by the real test and all three mutations. The
    second element is the vacuity guard's subject: zero calls examined means
    every finding list is empty for free.
    """
    findings: list[str] = []
    examined = 0
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
        if name != _CALL_NAME:
            continue
        examined += 1
        kwargs = {kw.arg: kw.value for kw in node.keywords if kw.arg}
        for param, helper in (
            ("ic_elec_roster", _ROSTER_HELPER),
            ("domestic_assets_by_date", _SNAPSHOT_HELPER),
        ):
            if param not in kwargs:
                findings.append(f"{param} is not passed by keyword")
                continue
            expr = ast.dump(kwargs[param])
            if f"id='{helper}'" not in expr:
                findings.append(
                    f"{param} does not read {helper} — the rosters may have been "
                    "swapped or the helper bypassed"
                )

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == _ROSTER_HELPER:
            if "'I&C'" not in ast.dump(node):
                findings.append(
                    f"{_ROSTER_HELPER} does not filter on segment == 'I&C' — it "
                    "would offer the whole electricity book to an aggregator"
                )

    return findings, examined


def test_the_call_site_hands_each_roster_to_its_own_parameter():
    with open(RUN_MODULE_PATH) as fh:
        source = fh.read()
    findings, examined = _call_site_findings(source)
    assert examined == 1, (
        f"expected exactly one {_CALL_NAME} call site in run_phase2b.py, found "
        f"{examined} — with zero, this control passes for free"
    )
    assert findings == [], findings


def test_mutation_swapping_the_two_rosters_is_caught():
    with open(RUN_MODULE_PATH) as fh:
        source = fh.read()
    mutated = source.replace(
        "ic_elec_roster=_ic_flex_roster(ELEC_CUSTOMERS, EFFECTIVE_EAC_KWH),",
        "ic_elec_roster=_domestic_flex_assets_by_date(\n"
        "            household_demand_register, _all_years, _elec_cids\n"
        "        ),",
        1,
    )
    assert mutated != source, "the swap mutation did not apply — anchor moved"
    findings, examined = _call_site_findings(mutated)
    assert examined == 1
    assert any("swapped" in f for f in findings), (
        f"control 3 did not fire on a swapped roster: {findings}"
    )


def test_mutation_bypassing_the_roster_helper_is_caught():
    with open(RUN_MODULE_PATH) as fh:
        source = fh.read()
    mutated = source.replace(
        "ic_elec_roster=_ic_flex_roster(ELEC_CUSTOMERS, EFFECTIVE_EAC_KWH),",
        "ic_elec_roster=ELEC_CUSTOMERS,",
        1,
    )
    assert mutated != source, "the bypass mutation did not apply — anchor moved"
    findings, examined = _call_site_findings(mutated)
    assert examined == 1
    assert any("bypassed" in f for f in findings), (
        f"control 3 did not fire on a bypassed helper: {findings}"
    )


def test_mutation_dropping_the_ic_filter_from_the_helper_is_caught():
    with open(RUN_MODULE_PATH) as fh:
        source = fh.read()
    mutated = source.replace(
        "        for c in elec_customers\n        if c.get(\"segment\") == \"I&C\"\n",
        "        for c in elec_customers\n",
        1,
    )
    assert mutated != source, "the filter mutation did not apply — anchor moved"
    findings, examined = _call_site_findings(mutated)
    assert examined == 1
    assert any("I&C" in f for f in findings), (
        f"control 3 did not fire on a dropped segment filter: {findings}"
    )


# ---------------------------------------------------------------------------
# CONTROL 4 — behavioural half of the same defect: the filter actually changes
# the money, so control 3 is guarding something rather than a spelling.
# ---------------------------------------------------------------------------


def test_mutation_a_roster_without_the_segment_filter_moves_the_money():
    customers, eac = _elec_customers(), _eac_by_cid()
    real = _build().ic_summary["total_ic_flex_revenue_gbp"]

    unfiltered = [(c["customer_id"], eac.get(c["customer_id"], 0.0)) for c in customers]
    book = ICFlexibilityRevenueBook()
    for year_str in FIXTURE_YEARS:
        book.compute_year(int(year_str), unfiltered)

    assert book.total_revenue_all_years() != real, (
        "dropping the segment filter did not move the I&C flexibility figure — "
        "control 3 is guarding a spelling, not a number"
    )


# ---------------------------------------------------------------------------
# CONTROL 5 — the snapshot key IS the query date, proved rather than asserted.
# ---------------------------------------------------------------------------


def test_the_worlds_snapshot_is_keyed_by_the_dates_it_queried():
    from simulation.run_phase2b import _domestic_flex_assets_by_date

    register = _FakeHouseholdRegister()
    snapshot = _domestic_flex_assets_by_date(register, FIXTURE_YEARS, _elec_cids())

    assert set(snapshot) == {f"{int(y)}-12-31" for y in FIXTURE_YEARS}
    assert set(register.queried_dates) == set(snapshot), (
        "the world queried dates it did not file under, or filed dates it did "
        "not query — the two would be free to drift"
    )
    for year_end, by_cid in snapshot.items():
        assert list(by_cid) == _elec_cids(), (
            f"customer order was not preserved for {year_end} — the book prices "
            "in the order it is given"
        )


def test_a_snapshot_missing_the_books_query_date_raises_rather_than_repricing():
    """The adapter is not fail-open: a misfiled year is loud, not silent."""
    misaligned = {"2021-12-31": _ASSETS["2021-12-31"]}
    with pytest.raises(KeyError):
        impl.build_flexibility_revenue(
            report_years=FIXTURE_YEARS,  # asks for 2023-12-31 too
            domestic_assets_by_date=misaligned,
            ic_elec_roster=_ic_roster(_elec_customers(), _eac_by_cid()),
        )
