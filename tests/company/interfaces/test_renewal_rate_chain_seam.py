"""KNIFE pass 3, `A_composition_lift` step 24 (§3s) — the renewal rate chain.

Three crossings cut: `simulation.run_phase2b` no longer imports
`company.pricing.tariff_engine`, `company.pricing.margin_feedback` or
`company.pricing.ofgem_price_cap`. It hands
`company/interfaces/renewal_rate_chain.py` the renewal as it happened and
records the contracted rate that comes back.

The controls in this file, and what each can actually fail on:

1. NO NUMBER MOVES — `_drive_pre_cut` is the exact sequence `run_phase2b.py`'s
   term loop ran before this step, transcribed with its literals and its
   guards, driven over a fixture that reaches all four writers. The door is
   driven over the same inputs and the WHOLE result is compared: rate, spans,
   and every per-writer log entry, keys and order included. This is the control
   that would fail if the lift changed an answer.
2. READ DIRECTION (behavioural, not a grep) — run the desk module in a clean
   interpreter and ask the import system which world modules it loaded. The
   mutation adds a lazy `simulation` import inside the decision and the SAME
   detector reports it.
3. THE ORDER IS NOW A SIGNATURE (the defect this cut REMOVES) — before the cut
   the sequence premium -> surcharge -> uplift -> cap was four separate blocks
   in a 2,800-line function and nothing asserted it. Mutating the desk to run
   the cap before the surcharge changes the contracted rate, and the control
   catches it.
4. THE FOUR ELIGIBILITY RULES STILL GATE (the defect the lift invites) — each
   writer's "does this renewal qualify" test is now invisible to the caller.
   Each is asserted against a fixture that contains the case being excluded,
   and mutation-proven by deleting the guard on a copy of the desk.

VACUITY, stated once for the whole file. `test_the_fixture_is_not_degenerate`
asserts directly that the reference renewal fires all four writers and that
each excluded case is present, so no control below compares two empties.
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

from company.crm.customer_profitability import renewal_unit_rate_uplift
from company.interfaces import renewal_rate_chain as door
from company.pricing.margin_feedback import compute_margin_surcharge
from company.pricing.ofgem_price_cap import get_cap_unit_rate_for_date
from company.pricing.tariff_engine import (
    PORTFOLIO_PREMIUM_LOOKBACK,
    compute_portfolio_premium,
)

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
IMPL_PATH = os.path.join(REPO_ROOT, "company", "pricing", "renewal_rate_chain.py")

# A domestic fixed electricity account, on its second term, whose previous term
# lost the supplier money on a book that has been under-earning, renewing inside
# a cap window. Every one of the four writers has something to do.
REFERENCE = dict(
    customer_id="C1",
    billing_account="C1",
    commodity="electricity",
    term_start="2021-06-01",
    tariff_type="fixed",
    term_index=2,
    struck_unit_rate_gbp_per_mwh=200.0,
    portfolio_margin_rates=[-0.04, -0.03, 0.0, 0.01, 0.02],
    prior_term_margin_gbp=-380.0,
    prior_term_revenue_gbp=1_500.0,
    is_domestic=True,
)


def _settled(cid: str) -> list[dict]:
    """One settled, net-negative prior term for the reference account.

    The uplift door reads these under its own point-in-time bound (settlement
    strictly before the renewal's term start), needs `term_start` to group a
    term and at least `MIN_RECORDS_FOR_JUDGEMENT` of them to form a view. A
    customer with no settled loss gets no uplift, which is what makes control
    4's uplift case non-vacuous.
    """
    return [
        {
            "customer_id": cid,
            "settlement_date": f"2020-{mm}-28",
            "term_start": "2020-06-01",
            "consumption_kwh": 300.0,
            "revenue_gbp": 34.0,
            "cost_gbp": 52.0,
            "net_margin_gbp": -18.0,
            "commodity": "electricity",
        }
        for mm in ("07", "08", "09", "10")
    ]


SETTLED_RECORDS = _settled("C1")


# ---------------------------------------------------------------------------
# The two implementations of the same chain: the pre-cut one, and the door.
# ---------------------------------------------------------------------------


def _drive_pre_cut(**over):
    """The exact sequence `run_phase2b.py::main()` ran before step 24.

    Transcribed with its own guards and literals, including `term_index >= 1`
    spelled at two sites and the cap's `tariff_type == "fixed"` test. Returns
    the same five things the door does, so control 1 can compare in full.
    """
    args = {**REFERENCE, "settled_records": SETTLED_RECORDS, **over}
    cid = args["customer_id"]
    billing_account = args["billing_account"]
    commodity = args["commodity"]
    term_start_str = args["term_start"]
    term_tariff_type = args["tariff_type"]
    term_index = args["term_index"]
    unit_rate = args["struck_unit_rate_gbp_per_mwh"]
    _portfolio_rates = args["portfolio_margin_rates"]
    prev_margin = args["prior_term_margin_gbp"]
    prev_revenue = args["prior_term_revenue_gbp"]
    all_records = args["settled_records"]

    dynamic_pricing_log: list[dict] = []
    margin_feedback_log: list[dict] = []
    profitability_uplift_log: list[dict] = []
    rate_decomposition_log: list[dict] = []

    rate_original = unit_rate
    rate_components: list[dict] = []
    rate_chain_entries: list[dict] = []

    if unit_rate is not None and term_index >= 1 and len(_portfolio_rates) >= 1:
        lookback = _portfolio_rates[-PORTFOLIO_PREMIUM_LOOKBACK:]
        portfolio_prem = compute_portfolio_premium(lookback)
        if abs(portfolio_prem) > 1e-6:
            rate_before = unit_rate
            unit_rate *= (1.0 + portfolio_prem)
            _entry = {
                "customer_id": cid,
                "commodity": commodity,
                "term_start": term_start_str,
                "recent_margin_rates": [round(r, 4) for r in lookback],
                "mean_recent_margin_rate": round(sum(lookback) / len(lookback), 4),
                "portfolio_premium_pct": round(portfolio_prem * 100, 2),
                "unit_rate_original": round(rate_original, 4),
                "unit_rate_before": round(rate_before, 4),
                "unit_rate_after": round(unit_rate, 4),
            }
            dynamic_pricing_log.append(_entry)
            rate_chain_entries.append(_entry)
            rate_components.append({
                "cause": "portfolio_premium",
                "basis": "pct",
                "magnitude": round(portfolio_prem * 100, 4),
                "rate_before": round(rate_before, 4),
                "rate_after": round(unit_rate, 4),
            })

    if unit_rate is not None and term_index >= 1 and prev_margin is not None:
        surcharge = compute_margin_surcharge(prev_margin, prev_revenue)
        if surcharge > 0:
            rate_before = unit_rate
            unit_rate *= (1.0 + surcharge)
            _entry = {
                "customer_id": cid,
                "commodity": commodity,
                "term_start": term_start_str,
                "prev_margin_gbp": round(prev_margin, 4),
                "prev_revenue_gbp": round(prev_revenue, 4),
                "surcharge_pct": round(surcharge * 100, 2),
                "unit_rate_original": round(rate_original or 0.0, 4),
                "unit_rate_before": round(rate_before, 4),
                "unit_rate_after": round(unit_rate, 4),
            }
            margin_feedback_log.append(_entry)
            rate_chain_entries.append(_entry)
            rate_components.append({
                "cause": "margin_surcharge",
                "basis": "pct",
                "magnitude": round(surcharge * 100, 4),
                "rate_before": round(rate_before, 4),
                "rate_after": round(unit_rate, 4),
            })

    pnl_uplift = renewal_unit_rate_uplift(
        account_id=billing_account,
        commodity=commodity,
        tariff_type=term_tariff_type,
        term_index=term_index,
        term_start=term_start_str,
        locked_unit_rate=unit_rate,
        settled_records=all_records,
    )
    if pnl_uplift > 0:
        rate_before = unit_rate
        unit_rate += pnl_uplift
        _entry = {
            "customer_id": billing_account,
            "commodity": commodity,
            "term_start": term_start_str,
            "uplift_gbp_per_mwh": round(pnl_uplift, 4),
            "unit_rate_original": round(rate_original or 0.0, 4),
            "unit_rate_before": round(rate_before, 4),
            "unit_rate_after": round(unit_rate, 4),
        }
        profitability_uplift_log.append(_entry)
        rate_chain_entries.append(_entry)
        rate_components.append({
            "cause": "profitability_uplift",
            "basis": "gbp_per_mwh",
            "magnitude": round(pnl_uplift, 4),
            "rate_before": round(rate_before, 4),
            "rate_after": round(unit_rate, 4),
        })

    if (unit_rate is not None
            and args["is_domestic"]
            and term_tariff_type == "fixed"):
        _cap = get_cap_unit_rate_for_date(
            commodity, date.fromisoformat(term_start_str[:10])
        )
        if _cap is not None:
            if _cap < unit_rate:
                rate_components.append({
                    "cause": "price_cap",
                    "basis": "gbp_per_mwh",
                    "magnitude": round(_cap - unit_rate, 4),
                    "rate_before": round(unit_rate, 4),
                    "rate_after": round(_cap, 4),
                })
            unit_rate = min(unit_rate, _cap)

    if rate_components:
        _contracted = round(unit_rate, 4)
        for _e in rate_chain_entries:
            _e["unit_rate_contracted"] = _contracted
        rate_decomposition_log.append({
            "customer_id": cid,
            "billing_account": billing_account,
            "commodity": commodity,
            "term_start": term_start_str,
            "unit_rate_original": round(rate_original or 0.0, 4),
            "unit_rate_contracted": _contracted,
            "components": rate_components,
        })

    return {
        "unit_rate": unit_rate,
        "components": rate_components,
        "dynamic_pricing": dynamic_pricing_log,
        "margin_feedback": margin_feedback_log,
        "profitability_uplift": profitability_uplift_log,
        "decomposition": rate_decomposition_log[0] if rate_decomposition_log else None,
    }


def _drive_door(module=door, **over):
    result = module.decide_renewal_rate(
        **{**REFERENCE, "settled_records": SETTLED_RECORDS, **over}
    )
    return {
        "unit_rate": result.unit_rate_gbp_per_mwh,
        "components": result.components,
        "dynamic_pricing": result.dynamic_pricing_entries,
        "margin_feedback": result.margin_feedback_entries,
        "profitability_uplift": result.profitability_uplift_entries,
        "decomposition": result.decomposition,
    }


def _load_mutated_desk(source: str):
    """Import `source` as a fresh module, registered in sys.modules BEFORE
    execution because `@dataclass` resolves annotations through the module
    entry — loading it unregistered fails inside `dataclasses` rather than in
    the assertion, which would make the mutation UNAVAILABLE, and an
    unavailable check is a FAILED check (R15)."""
    modname = f"_knife3_step24_rate_chain_mutant_{uuid.uuid4().hex}"
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


def test_the_fixture_is_not_degenerate():
    result = _drive_door()
    causes = [c["cause"] for c in result["components"]]
    assert causes == [
        "portfolio_premium",
        "margin_surcharge",
        "profitability_uplift",
        "price_cap",
    ], (
        f"the reference renewal fired {causes} — a control below would be "
        "comparing a chain that never ran"
    )
    assert result["unit_rate"] != REFERENCE["struck_unit_rate_gbp_per_mwh"]
    assert get_cap_unit_rate_for_date(
        "electricity", date.fromisoformat(REFERENCE["term_start"])
    ) is not None, "the fixture term start is outside every published cap window"


# ---------------------------------------------------------------------------
# CONTROL 1 — NO NUMBER MOVES. The whole chain, both ways.
# ---------------------------------------------------------------------------


def test_the_door_reproduces_the_pre_cut_chain_exactly():
    assert _drive_door() == _drive_pre_cut()


def test_every_per_writer_entry_keeps_its_published_key_order():
    """These log dicts are read by `saas/reporting/annual_report.py`; their
    shape is part of the contract, not an implementation detail of the desk."""
    door_result, pre_cut = _drive_door(), _drive_pre_cut()
    for log in ("dynamic_pricing", "margin_feedback", "profitability_uplift"):
        assert [list(e) for e in door_result[log]] == [list(e) for e in pre_cut[log]], log
    assert list(door_result["decomposition"]) == list(pre_cut["decomposition"])


def test_the_contracted_rate_is_stamped_onto_every_writers_own_entry():
    result = door.decide_renewal_rate(
        **{**REFERENCE, "settled_records": SETTLED_RECORDS}
    )
    contracted = result.decomposition["unit_rate_contracted"]
    assert result.chain_entries, "no writer entries to stamp"
    for entry in result.chain_entries:
        assert entry["unit_rate_contracted"] == contracted, (
            "a per-writer entry published a rate that is not the one the "
            "customer contracted at — the defect the chain exists to remove"
        )


@pytest.mark.parametrize(
    "over",
    [
        {"struck_unit_rate_gbp_per_mwh": None, "tariff_type": "flex"},
        {"term_index": 0},
        {"is_domestic": False},
        {"tariff_type": "pass_through"},
        {"portfolio_margin_rates": []},
        {"prior_term_margin_gbp": None},
        {"commodity": "gas"},
        {"settled_records": []},
        {"term_start": "2016-04-01"},
    ],
)
def test_the_door_matches_the_pre_cut_code_on_every_excluded_case(over):
    """Identity is claimed for the cases that DON'T fire too, not just the one
    that does — an eligibility rule copied slightly wrong shows up here."""
    assert _drive_door(**over) == _drive_pre_cut(**over)


# ---------------------------------------------------------------------------
# CONTROL 2 — the company module must not reach back into the world, statically
# OR lazily. Behavioural: what did the import system actually load?
# ---------------------------------------------------------------------------

_PROBE = textwrap.dedent(
    """
    import json, sys
    sys.path.insert(0, {repo!r})
    sys.path.insert(0, {pkgdir!r})
    import {modname} as m

    m.decide_renewal_rate(
        customer_id="C1", billing_account="C1", commodity="electricity",
        term_start="2022-06-01", tariff_type="fixed", term_index=2,
        struck_unit_rate_gbp_per_mwh=140.0,
        portfolio_margin_rates=[-0.04, -0.03, 0.0, 0.01, 0.02],
        prior_term_margin_gbp=-380.0, prior_term_revenue_gbp=1500.0,
        is_domestic=True, settled_records=[],
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
        modname = "_knife3_step24_rate_chain_subject"
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


def test_deciding_the_renewal_rate_loads_no_world_module():
    assert _walled_modules_loaded_by(_impl_source()) == []


def test_mutation_a_lazy_world_import_is_caught_by_the_same_detector():
    """Perform the defect on a copy of the real source, same detector."""
    mutated = _impl_source()
    anchor = "    unit_rate = struck_unit_rate_gbp_per_mwh\n"
    assert anchor in mutated, "anchor moved — this mutation is no longer the defect"
    mutated = mutated.replace(
        anchor,
        "    from simulation.policy_costs import get_gas_ccl_per_mwh  # noqa: F401  <-- the defect\n"
        + anchor,
        1,
    )
    assert "simulation.policy_costs" in _walled_modules_loaded_by(mutated), (
        "the mutation did not take — control 2 is not testing what it claims"
    )


# ---------------------------------------------------------------------------
# CONTROL 3 — THE ORDER IS NOW A SIGNATURE, not four blocks nothing compares.
# ---------------------------------------------------------------------------


def test_the_cap_is_the_last_writer_and_the_order_is_load_bearing():
    """Clamp before the surcharge instead of after and the customer contracts
    at a different rate. Before this cut the four writers were four separate
    blocks in a 2,800-line function and nothing anywhere asserted their order.
    """
    src = _impl_source()
    # A pure REORDER, not a change of arithmetic: lift writer 3 (the uplift) out
    # from between the surcharge and the cap, and run it after the clamp. Every
    # expression is identical; only the order moves. A supplier that adds £5/MWh
    # to a domestic fixed renewal AFTER clamping it is charging above the cap.
    start = src.index("    # WRITER 3 —")
    # ENDS AT WRITER 3b, NOT AT WRITER 4 (retargeted 2026-08-26, when 3b gained the ceiling it
    # searches under). The mutation this control describes is "lift writer 3 out and run it after
    # the clamp"; bounding it at writer 4 used to mean the same thing and now sweeps 3b along with
    # it, which moves three writers instead of one and takes `cap_ceiling`'s definition past its
    # own use. A mutant that dies of `UnboundLocalError` proves nothing about ORDER.
    end = src.index("    # WRITER 3b —")
    uplift_block = src[start:end]
    assert "pnl_uplift" in uplift_block, "block bounds moved — this is no longer the defect"
    close = "    # Close the chain."
    assert close in src, "anchor moved — this mutation is no longer the defect"
    mutated = (src[:start] + src[end:]).replace(
        close, uplift_block + "    # <-- the defect: the uplift now escapes the cap\n" + close, 1
    )
    assert "the defect" in mutated, "the mutation did not take"
    mutant = _load_mutated_desk(mutated)

    capped = _drive_door()["unit_rate"]
    escaped = _drive_door(module=mutant)["unit_rate"]
    assert escaped != capped, (
        "running the uplift after the clamp changed nothing — the chain's "
        "order is not the thing this control thinks it is"
    )
    cap = get_cap_unit_rate_for_date(
        "electricity", date.fromisoformat(REFERENCE["term_start"])
    )
    assert capped <= cap < escaped, (
        "the reordered chain did not breach the cap, so this control is not "
        "measuring what it claims"
    )


# ---------------------------------------------------------------------------
# CONTROL 4 — the eligibility rules the caller can no longer see.
# ---------------------------------------------------------------------------


def test_the_cap_binds_domestic_fixed_only():
    assert "price_cap" in [c["cause"] for c in _drive_door()["components"]]
    for over in ({"is_domestic": False}, {"tariff_type": "pass_through"}):
        causes = [c["cause"] for c in _drive_door(**over)["components"]]
        assert "price_cap" not in causes, (
            f"the cap clamped a renewal it does not bind ({over})"
        )


def test_mutation_dropping_the_cap_eligibility_rule_is_caught():
    """RETARGETED 2026-08-26, and the control got STRONGER rather than moved.

    The eligibility rule used to live on writer 4's own `if`. It now lives one block earlier, on
    `cap_ceiling`, because writer 3b — the value arm — has to SEARCH under the same ceiling writer
    4 applies rather than be clamped by it afterwards. So there is one read of the rule where
    there were nearly two, and dropping it now breaks both the arm's ceiling and the clamp
    together, which is exactly the coupling that makes a single read worth having.
    """
    mutated = _impl_source().replace(
        "    if is_domestic and tariff_type in CAPPED_TARIFF_TYPES:",
        "    if True:  # <-- the defect",
        1,
    )
    assert "the defect" in mutated, "the mutation did not take"
    mutant = _load_mutated_desk(mutated)
    causes = [c["cause"] for c in _drive_door(module=mutant, is_domestic=False)["components"]]
    assert "price_cap" in causes, (
        "an I&C renewal still escaped the cap — the eligibility rule is not "
        "where this control says it is"
    )


def test_a_first_term_learns_from_nothing():
    causes = [c["cause"] for c in _drive_door(term_index=0)["components"]]
    assert "portfolio_premium" not in causes and "margin_surcharge" not in causes


def test_mutation_dropping_the_first_term_guard_is_caught():
    mutated = _impl_source().replace(
        "MIN_TERM_INDEX_FOR_LEARNED_ADJUSTMENT = 1",
        "MIN_TERM_INDEX_FOR_LEARNED_ADJUSTMENT = 0  # <-- the defect",
        1,
    )
    assert "the defect" in mutated, "the mutation did not take"
    mutant = _load_mutated_desk(mutated)
    causes = [c["cause"] for c in _drive_door(module=mutant, term_index=0)["components"]]
    assert "portfolio_premium" in causes, (
        "a first term still learned nothing — the guard is not where this "
        "control says it is"
    )


def test_a_term_with_no_locked_rate_is_left_alone():
    result = _drive_door(struck_unit_rate_gbp_per_mwh=None, tariff_type="flex")
    assert result["unit_rate"] is None
    assert result["components"] == []
    assert result["decomposition"] is None


def test_a_customer_with_no_prior_term_pays_no_recovery_surcharge():
    causes = [c["cause"] for c in _drive_door(prior_term_margin_gbp=None)["components"]]
    assert "margin_surcharge" not in causes
    # ...and a prior term that broke exactly even is NOT the same case as no
    # prior term at all: `None` is absence, `0.0` is a completed term.
    assert _drive_door(prior_term_margin_gbp=0.0)["margin_feedback"] == []


# ---------------------------------------------------------------------------
# The door's own surface: no engine, no cap table, no coefficient.
# ---------------------------------------------------------------------------


def test_the_door_exposes_only_the_decision_and_its_result():
    assert sorted(door.__all__) == ["RenewalRateChain", "decide_renewal_rate"]
    for leaked in (
        "CompanyTariffEngine",
        "compute_portfolio_premium",
        "compute_margin_surcharge",
        "get_cap_unit_rate_for_date",
        "PORTFOLIO_PREMIUM_LOOKBACK",
    ):
        assert not hasattr(door, leaked), (
            f"{leaked} is reachable through the door — the world can call the "
            "pricing machinery directly again without creating a wall edge"
        )


def test_the_door_takes_no_object_through_which_the_engine_could_be_supplied():
    import inspect

    params = inspect.signature(door.decide_renewal_rate).parameters
    assert all(p.kind is inspect.Parameter.KEYWORD_ONLY for p in params.values())
    assert not any(
        name in params for name in ("desk", "engine", "chain", "policy", "module")
    ), "a convenience argument would restore the dependency without a wall edge"
