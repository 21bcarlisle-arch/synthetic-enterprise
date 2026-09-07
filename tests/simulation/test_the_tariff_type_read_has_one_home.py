"""The defect: three copies of "what `tariff_type` does this record resolve to", two of them stale.

`population_draw.to_customer_dict` renders `"tariff_type"` unconditionally, so a drawn or won
record carries the key PRESENT and `None` and `record.get("tariff_type", "fixed")` never reaches
its default. That was established on 2026-08-28
(`docs/design/DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md`) and repaired on 2026-08-30 -- at
ONE of the three places the read was spelled out.

What the other two then published, for eight days, in one artefact:

  * `renewal_funnel.value_arm.product_not_upliftable_by_tariff_type` -> `{"'svt'": 1350,
    "None": 158}`. The 158 are the terms of 18 curriculum-drawn GAS legs, refused because the gas
    call site still spelled the read the defeated way.
  * `renewal_funnel.value_arm.product_label_by_account_class` -> 137 electricity legs at
    `resolved_tariff_type: null, the_guard_admits_it: false`. The builder labels those `fixed` and
    the guard admits them. The census had restated the pre-repair spelling in order to report it.

Two blocks of one file disagreeing about one read, and each internally consistent, is what a
restated spelling buys. So the read now has one home and these controls hold it there.

KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. Nothing here asserts that gas resolves to `None`.
`test_the_two_commodities_are_read_differently_and_that_is_the_finding` asserts they DIFFER and
names which is which; when the gas fidelity determination lands and the difference goes away, that
control goes red and is deleted with the finding it records, rather than silently passing on a
world that got better.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

from simulation.run_phase2b import _build_gas_renewal_schedule, resolved_tariff_type

_REPO = pathlib.Path(__file__).resolve().parents[2]
_WORLD = _REPO / "simulation" / "run_phase2b.py"
_CENSUS = _REPO / "tools" / "run_value_cycle_ab.py"

#: The two schedule builders whose `tariff_type` argument decides what every term carries.
_SCHEDULE_BUILDERS = {"build_renewal_schedule", "_build_gas_renewal_schedule"}


def _called_name(node: ast.Call) -> str:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return ""


def test_every_schedule_building_call_site_routes_through_the_one_read():
    """The defect this fires on: a call site spelling the resolution inline again.

    Reaches the CALLER rather than the helper. Restoring either historical spelling --
    `c.get("tariff_type") or "fixed"` at the electricity site, `c.get("tariff_type", "fixed")` at
    the gas one -- puts a non-`resolved_tariff_type` expression back on the keyword and fails
    here, which is the only reason this control is worth having: calling the helper and asserting
    what it returns would have survived the entire eight days.
    """
    tree = ast.parse(_WORLD.read_text())
    seen: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or _called_name(node) not in _SCHEDULE_BUILDERS:
            continue
        for kw in node.keywords:
            if kw.arg != "tariff_type":
                continue
            seen.append(_called_name(kw.value) if isinstance(kw.value, ast.Call) else
                        type(kw.value).__name__)

    # The partition control: assert the call sites EXIST before asserting what they do. A repo
    # where the builders were renamed would otherwise pass this with an empty list.
    assert len(seen) >= 2, (
        f"expected at least two schedule-building call sites passing `tariff_type`, found {seen}")
    assert set(seen) == {"resolved_tariff_type"}, (
        f"a schedule-building call site spells the tariff_type read inline: {seen}")


def test_the_census_calls_the_read_rather_than_respelling_it():
    """The defect this fires on: `product_label_by_account_class` restating the world's spelling.

    That restatement is what published `the_guard_admits_it: false` for 137 legs the guard admits.
    """
    tree = ast.parse(_CENSUS.read_text())
    census = next(
        (n for n in ast.walk(tree)
         if isinstance(n, ast.FunctionDef) and n.name == "product_label_by_account_class"),
        None)
    assert census is not None, "product_label_by_account_class is gone -- repoint this control"

    resolved_from = [
        _called_name(n.value) if isinstance(n.value, ast.Call) else type(n.value).__name__
        for n in ast.walk(census)
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "resolved" for t in n.targets)
    ]
    assert resolved_from == ["resolved_tariff_type"], (
        f"the census derives `resolved` from {resolved_from}, not from the world's own read")


def test_the_two_commodities_are_read_differently_and_that_is_the_finding():
    """A drawn record carries the key PRESENT and unset, and the two builders disagree on it.

    Both legs of the partition in one control, because a function that returned `None` for
    everything and one that returned `"fixed"` for everything would each pass a single-leg test.
    """
    drawn_elec = {"customer_id": "PROS-2016-0067", "commodity": "electricity", "tariff_type": None}
    drawn_gas = {"customer_id": "PROS-2016-0067-G", "commodity": "gas", "tariff_type": None}

    assert resolved_tariff_type(drawn_elec) == "fixed"
    # NOT a statement that this is right. It is the live gas defect, held visible so that the
    # determination which closes it also deletes this control.
    assert resolved_tariff_type(drawn_gas) is None


def test_a_successor_leg_is_read_off_its_call_site_not_its_record():
    """The successor call site passes no `tariff_type`, so the record's value is never consulted.

    A census that read the record would report `flex` for a leg the builder strikes as `fixed`.
    """
    successor = {"customer_id": "C1_2", "commodity": "electricity", "tariff_type": "flex"}
    assert resolved_tariff_type(successor, successor=True) == "fixed"
    assert resolved_tariff_type(successor) == "flex"


@pytest.mark.parametrize("tariff_type", [None, "fixed"])
def test_what_the_read_returns_is_what_the_builder_stamps_on_every_term(tariff_type):
    """The link the funnel counts: the resolved value lands on each term, unchanged.

    Without this, the two AST controls above prove only that one name is called, not that the
    value it returns is the one `decide_renewal_rate` is later handed.
    """
    records = [{"settlementDate": f"2016-{m:02d}-01", "systemSellPrice": 50.0}
               for m in range(1, 13)]
    records += [{"settlementDate": f"2015-{m:02d}-01", "systemSellPrice": 50.0}
                for m in range(10, 13)]
    customer = {"customer_id": "PROS-2016-0067-G", "commodity": "gas",
                "aq_kwh": 12000, "acquisition_date": "2016-01-01",
                "tariff_type": tariff_type}

    schedule = _build_gas_renewal_schedule(
        customer, sorted(records, key=lambda r: r["settlementDate"]),
        report_end="2016-12-31", tariff_type=resolved_tariff_type(customer))

    assert schedule, "no terms built -- this control would pass vacuously"
    assert {term["tariff_type"] for term in schedule} == {resolved_tariff_type(customer)}
