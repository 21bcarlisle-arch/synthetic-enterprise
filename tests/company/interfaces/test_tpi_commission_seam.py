"""KNIFE pass 3, `A_composition_lift` step 22 (§3q) — the broker-commission door.

One crossing cut: `simulation.run_phase2b` no longer imports
`company.crm.tpi_book`. It hands `company/interfaces/tpi_commission.py` the
settled records and its own I&C roster and reads back the supplier's published
commission summary.

The controls in this file, and what each can actually fail on:

1. READ DIRECTION (behavioural, not a grep) — run the desk module in a clean
   interpreter and ask the import system which world modules it loaded. The
   mutation adds a lazy `simulation` import inside the builder and the SAME
   detector reports it.
2. NO NUMBER MOVES — drive the raw `TPIBook` through the exact pre-cut sequence
   (the literals as `run_phase2b.py` typed them) and the door over the same
   records, then compare the published summary in full, keys and order included.
   This is the control that would fail if the lift changed an answer.
3. ONE NAME, ONE NUMBER (the defect this cut REMOVES) — the published
   `commission_rate_gbp_per_mwh` used to be a second, independent literal `1.5`
   beside the registered rate. The mutation moves the registered rate on a copy
   of the desk and asserts the published rate AND the commission move together;
   against the pre-cut code the published rate would not have moved at all.
4. THE TWO FILTERS STILL FILTER (the defect the lift invites) — the roster
   filter and the zero-consumption filter are now invisible to the caller. Each
   is asserted against a fixture that contains the thing being excluded, and
   mutation-proven by deleting the filter on a copy of the desk.

VACUITY, stated once for the whole file. The record set below contains a
non-brokered customer, a brokered customer with a zero-consumption year, and two
brokered customers with real volume across two years — so controls 2 and 4
compare non-empty books that differ from the unfiltered ones.
`test_the_record_set_is_not_degenerate` asserts all three directly.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import uuid
from datetime import date

import pytest

from company.crm.tpi_book import TPIBook, TPICommissionBasis, TPITier
from company.interfaces import tpi_commission as door

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
IMPL_PATH = os.path.join(REPO_ROOT, "company", "crm", "tpi_commission_desk.py")

# The world's roster: who is I&C electricity. Held by the world, handed over.
IC_IDS = {"IC1", "IC2", "IC3"}
REPORT_YEARS = ["2018", "2019"]


def _rec(cid, settlement_date, kwh, revenue):
    return {
        "customer_id": cid,
        "settlement_date": settlement_date,
        "consumption_kwh": kwh,
        "revenue_gbp": revenue,
    }


SETTLED_RECORDS = [
    _rec("IC1", "2018-03-31", 1_200_000.0, 96_000.0),
    _rec("IC1", "2018-09-30", 800_000.0, 62_400.0),
    _rec("IC1", "2019-03-31", 1_050_000.0, 141_750.0),
    _rec("IC2", "2018-06-30", 430_500.0, 33_100.55),
    _rec("IC2", "2019-06-30", 512_250.0, 68_900.25),
    # A brokered account with a year of zero settled volume — a live meter that
    # consumed nothing. No deal is booked and no commission is owed.
    _rec("IC3", "2019-01-31", 0.0, 0.0),
    # Not on the broker's roster: a domestic account. Its volume must not reach
    # the commission book.
    _rec("R1", "2018-04-30", 3_500.0, 620.0),
    _rec("R1", "2019-04-30", 3_700.0, 810.0),
]


# ---------------------------------------------------------------------------
# The two implementations of the same book: the pre-cut one, and the door.
# ---------------------------------------------------------------------------


def _drive_pre_cut(records=None, ic_ids=None, years=None):
    """The exact sequence `run_phase2b.py::main()` ran before step 22.

    Literals reproduced as they were typed there, INCLUDING the duplicated
    `1.5` in the summary — control 3 is about that duplication.
    """
    records = SETTLED_RECORDS if records is None else records
    ic_ids = IC_IDS if ic_ids is None else ic_ids
    years = REPORT_YEARS if years is None else years

    book = TPIBook()
    book.register(
        tpi_id="TPI-001",
        name="Standard Energy Broker",
        tier=TPITier.PREFERRED,
        commission_basis=TPICommissionBasis.PCT_OF_ANNUAL_CONSUMPTION,
        commission_rate=1.5,
        registered_date=date(2016, 1, 1),
    )
    yearly: dict = {}
    for rec in records:
        if rec.get("customer_id") in ic_ids:
            yearly.setdefault((rec["customer_id"], rec["settlement_date"][:4]), []).append(rec)

    for (cid, yr), recs in sorted(yearly.items()):
        ann_cons_mwh = sum(r.get("consumption_kwh", 0.0) for r in recs) / 1000.0
        ann_rev_gbp = sum(r.get("revenue_gbp", 0.0) for r in recs)
        if ann_cons_mwh > 0:
            book.record_deal(
                tpi_id="TPI-001",
                customer_id=cid,
                annual_consumption_mwh=round(ann_cons_mwh, 3),
                annual_revenue_gbp=round(ann_rev_gbp, 2),
                deal_date=date(int(yr), 1, 1),
            )

    return {
        "total_commission_gbp": book.total_commission_gbp(),
        "commission_rate_gbp_per_mwh": 1.5,
        "per_year": {yr: book.annual_summary(int(yr)) for yr in sorted(years)},
        "active_tpi_count": len(book.active_tpis()),
        "total_deals": len(book._deals),
    }


def _drive_door(records=None, ic_ids=None, years=None, module=door):
    return module.build_tpi_commission(
        settled_records=SETTLED_RECORDS if records is None else records,
        ic_elec_customer_ids=IC_IDS if ic_ids is None else ic_ids,
        report_years=REPORT_YEARS if years is None else years,
    )


def _load_mutated_desk(source: str):
    """Import `source` as a fresh module. Registered in sys.modules BEFORE
    execution because `@dataclass` resolves annotations through the module
    entry — loading it unregistered fails inside `dataclasses` rather than in
    the assertion, which would make the mutation UNAVAILABLE, and an
    unavailable check is a FAILED check (R15)."""
    modname = f"_knife3_step22_tpi_mutant_{uuid.uuid4().hex}"
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, modname + ".py")
        with open(path, "w") as fh:
            fh.write(source)
        spec = importlib.util.spec_from_file_location(modname, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[modname] = module
        try:
            spec.loader.exec_module(module)
        finally:
            sys.modules.pop(modname, None)
    return module


def _impl_source() -> str:
    with open(IMPL_PATH) as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# VACUITY — the fixture must be able to fail the controls that read it.
# ---------------------------------------------------------------------------


def test_the_record_set_is_not_degenerate():
    summary = _drive_door().summary
    assert summary["total_deals"] == 4, (
        "expected four booked customer-years — a different count means the "
        "fixture no longer exercises what controls 2 and 4 claim"
    )
    assert summary["total_commission_gbp"] > 0
    assert any(r["customer_id"] not in IC_IDS for r in SETTLED_RECORDS), (
        "no off-roster record — control 4's roster filter could not fail"
    )
    assert any(
        r["customer_id"] in IC_IDS and r["consumption_kwh"] == 0.0
        for r in SETTLED_RECORDS
    ), "no zero-volume brokered year — control 4's volume filter could not fail"
    assert all(s["deal_count"] > 0 for s in summary["per_year"].values()), (
        "a report year with no deals — control 2 would compare two empties"
    )


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

    m.build_tpi_commission(
        settled_records=[
            {{"customer_id": "IC1", "settlement_date": "2019-03-31",
              "consumption_kwh": 1050000.0, "revenue_gbp": 141750.0}},
        ],
        ic_elec_customer_ids={{"IC1"}},
        report_years=["2019"],
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
        modname = "_knife3_step22_tpi_subject"
        with open(os.path.join(pkgdir, modname + ".py"), "w") as fh:
            fh.write(source)
        probe = _PROBE.format(repo=REPO_ROOT, pkgdir=pkgdir, modname=modname)
        proc = subprocess.run(
            [sys.executable, "-c", probe],
            cwd=pkgdir,
            capture_output=True,
            text=True,
            timeout=300,
        )
    assert proc.returncode == 0, (
        f"the probe itself failed — an unavailable check is a FAILED check, "
        f"never a skip.\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    marker = [ln for ln in proc.stdout.splitlines() if ln.startswith("WALLED_MODULES=")]
    assert len(marker) == 1, f"probe produced no verdict line:\n{proc.stdout}"
    return json.loads(marker[0].split("=", 1)[1])


def test_booking_the_broker_commission_loads_no_world_module():
    assert _walled_modules_loaded_by(_impl_source()) == []


def test_mutation_a_lazy_world_import_is_caught_by_the_same_detector():
    """Perform the defect on a copy of the real source, same detector."""
    mutated = _impl_source()
    anchor = "    brokered = set(ic_elec_customer_ids)"
    assert anchor in mutated, "anchor moved — this mutation is no longer the defect"
    mutated = mutated.replace(
        anchor,
        "    from simulation.policy_costs import get_gas_ccl_per_mwh  # noqa: F401  <-- the defect\n"
        + anchor,
        1,
    )
    assert "simulation.policy_costs" in _walled_modules_loaded_by(mutated), (
        "the mutation did not take — control 1 is not testing what it claims"
    )


# ---------------------------------------------------------------------------
# CONTROL 2 — NO NUMBER MOVES. The whole published summary, both ways.
# ---------------------------------------------------------------------------


def test_the_door_reproduces_the_pre_cut_summary_exactly():
    assert _drive_door().summary == _drive_pre_cut()


def test_the_summary_keys_are_in_the_published_order():
    """`tpi_summary` is read by `saas/reporting/annual_report.py`; its shape is
    part of the contract, not an implementation detail of the desk."""
    assert list(_drive_door().summary) == list(_drive_pre_cut())


def test_the_result_fields_agree_with_the_summary_they_accompany():
    result = _drive_door()
    assert result.total_commission_gbp == result.summary["total_commission_gbp"]
    assert result.deal_count == result.summary["total_deals"]


# ---------------------------------------------------------------------------
# CONTROL 3 — ONE NAME, ONE NUMBER. The published rate IS the charged rate.
# ---------------------------------------------------------------------------


def test_the_published_rate_is_the_charged_rate():
    """Move the supplier's rate and BOTH the headline and the commission move.

    Before this cut the published `commission_rate_gbp_per_mwh` was a separate
    literal in `run_phase2b.py`, so this mutation would have moved the
    commission and left the published rate at 1.5 — a headline contradicting
    the arithmetic beneath it, with nothing to notice.
    """
    mutated_src = _impl_source().replace(
        "TPI_COMMISSION_RATE_GBP_PER_MWH: float = 1.5",
        "TPI_COMMISSION_RATE_GBP_PER_MWH: float = 2.25",
        1,
    )
    assert "2.25" in mutated_src, "the mutation did not take"
    mutant = _load_mutated_desk(mutated_src)

    base = _drive_door().summary
    moved = _drive_door(module=mutant).summary

    assert base["commission_rate_gbp_per_mwh"] == 1.5
    assert moved["commission_rate_gbp_per_mwh"] == 2.25, (
        "the published rate did not follow the registered rate — the two "
        "numbers have drifted apart again"
    )
    # Not exact: commission is rounded to the penny PER DEAL, so scaling the
    # rate does not scale the total to the last penny. The tolerance is on the
    # rounding, not on the relationship.
    assert moved["total_commission_gbp"] == pytest.approx(
        base["total_commission_gbp"] * 1.5, abs=0.02 * base["total_deals"]
    )


def test_a_second_volume_broker_raises_rather_than_averaging_silently():
    """The single-rate headline is only true for one volume-based broker.

    A second one makes it wrong wherever the number came from, so the desk
    refuses instead of publishing a rate that describes neither.
    """
    from company.crm import tpi_commission_desk as impl

    extra = impl.TPIBook()
    for tpi_id in ("TPI-001", "TPI-002"):
        extra.register(
            tpi_id=tpi_id, name=tpi_id, tier=TPITier.PREFERRED,
            commission_basis=TPICommissionBasis.PCT_OF_ANNUAL_CONSUMPTION,
            commission_rate=1.5, registered_date=date(2016, 1, 1),
        )
    with pytest.raises(ValueError, match="exactly one"):
        impl._published_rate(extra.active_tpis())


# ---------------------------------------------------------------------------
# CONTROL 4 — the two filters the caller can no longer see.
# ---------------------------------------------------------------------------


def test_off_roster_volume_never_reaches_the_commission_book():
    with_domestic = _drive_door().summary
    ic_only = _drive_door(
        records=[r for r in SETTLED_RECORDS if r["customer_id"] in IC_IDS]
    ).summary
    assert with_domestic == ic_only, (
        "dropping the non-brokered records changed the answer — domestic volume "
        "is being commissioned to a broker that never introduced it"
    )


def test_mutation_dropping_the_roster_filter_is_caught():
    mutated_src = _impl_source().replace(
        "        if rec.get(\"customer_id\") in brokered:\n",
        "        if True:  # <-- the defect\n",
        1,
    )
    assert "the defect" in mutated_src, "the mutation did not take"
    mutant = _load_mutated_desk(mutated_src)
    assert _drive_door(module=mutant).summary != _drive_door().summary, (
        "commissioning every account changed nothing — the roster filter is "
        "not the thing this control thinks it is"
    )


def test_a_zero_volume_brokered_year_books_no_deal():
    per_customer = {
        cid: _drive_door(
            records=[r for r in SETTLED_RECORDS if r["customer_id"] == cid]
        ).summary["total_deals"]
        for cid in sorted(IC_IDS)
    }
    assert per_customer["IC3"] == 0, (
        "a year with no settled volume booked a deal — commission would be owed "
        "on nothing"
    )
    assert per_customer["IC1"] == 2 and per_customer["IC2"] == 2


def test_mutation_dropping_the_volume_filter_is_caught():
    mutated_src = _impl_source().replace(
        "        if annual_consumption_mwh <= 0:\n            continue\n",
        "        if False:  # <-- the defect\n            continue\n",
        1,
    )
    assert "the defect" in mutated_src, "the mutation did not take"
    mutant = _load_mutated_desk(mutated_src)
    assert _drive_door(module=mutant).summary["total_deals"] == 5, (
        "the zero-volume year still booked no deal — the volume filter is not "
        "where this control says it is"
    )
