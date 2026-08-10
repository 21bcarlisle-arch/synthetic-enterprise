"""The bill-assembly seam's contract — and the two ways this cut could rot silently.

WHY THIS FILE EXISTS (R15: a control must be able to FAIL on its own named defect)
---------------------------------------------------------------------------------
KNIFE pass 3, `A_composition_lift` step 11, moved monthly bill assembly out of
`simulation/run_phase4c_on_phase2b.py` into `company/billing/monthly_bill_assembly.py`
behind `company/interfaces/bill_assembly.py`. What made that a CUT rather than a
file move is an INVERSION: the company does not import the world's meter-read
physics, it receives a `ReadArrivalFeed` from whoever runs the billing.

The epistemic-wall ratchet already polices the STATIC half of that claim — a
module-scope `company.billing.monthly_bill_assembly -> simulation.*` import is a
new class-(a) edge, the strictly-forbidden direction, and reds the suite with no
grandfathering to hide behind. That check carries its own mutation proof.

Two things it CANNOT see, both of which this cut is specifically exposed to:

1. **A lazy import.** The ratchet's own docstring states the limit in terms:
   it covers static imports only, and `importlib`/in-function imports escape it.
   The most natural convenience change here is exactly that shape — make
   `read_feed` optional and fall back to constructing the world's feed inside
   the function, so callers "don't have to bother". That would re-cross the wall
   in the forbidden direction and every static instrument in the tree would stay
   green. So the control below is BEHAVIOURAL: it runs the real billing run in a
   clean interpreter and asks which modules got loaded.

2. **A reordered feed.** `ReadArrivalFeed` is a `runtime_checkable` Protocol, and
   `runtime_checkable` checks method PRESENCE only — never signatures. That is a
   documented fail-open in the stdlib, and it bites here because
   `build_monthly_bills` calls every feed method POSITIONALLY. Swap two
   parameters in the world-side adapter and `isinstance()` still says True while
   a kWh float arrives where a trailing-actuals list was expected. So the second
   control compares parameter names AND order, and its mutation proves the
   `isinstance` check alone would have waved the defect through.

Each `test_mutation_*` performs the named defect rather than asserting it is
impossible.
"""

from __future__ import annotations

import inspect
import json
import os
import subprocess
import sys
import textwrap

import pytest

from company.billing import monthly_bill_assembly
from company.billing.monthly_bill_assembly import ReadArrivalFeed
from company.interfaces import bill_assembly
from simulation.meter_reads import SimulatedReadFeed

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

_FEED_METHODS = ("meter_type_for", "read_for", "final_read_for")


# --------------------------------------------------------------------------
# The seam re-export.
# --------------------------------------------------------------------------

def test_the_seam_exports_the_live_billing_run_not_a_copy_of_it():
    """`is`, not "callable and named right".

    The seam is a rename (`build_monthly_bills` -> `assemble_monthly_bills`).
    If someone later wraps it — to log, to default an argument, to "adapt" —
    the world would call the wrapper while every test that reaches
    `monthly_bill_assembly.build_monthly_bills` directly would exercise the
    unwrapped function, and the two could drift with nothing to say so.
    """
    assert bill_assembly.assemble_monthly_bills is monthly_bill_assembly.build_monthly_bills, (
        "company.interfaces.bill_assembly.assemble_monthly_bills must BE "
        "company.billing.monthly_bill_assembly.build_monthly_bills, not a wrapper "
        "around it."
    )


def test_the_seam_exports_the_read_feed_contract_itself():
    """The Protocol the world implements must be the one the company checks."""
    assert bill_assembly.ReadArrivalFeed is monthly_bill_assembly.ReadArrivalFeed
    assert bill_assembly.ReadArrival is monthly_bill_assembly.ReadArrival


# --------------------------------------------------------------------------
# CONTROL 1 — the billing run never reaches the world, at call time.
# --------------------------------------------------------------------------

_PROBE = textwrap.dedent(
    '''
    import json, sys

    sys.path.insert(0, {repo!r})
    {extra_path}
    from company.interfaces.supply_book import registered_supply_points
    from {module} import {symbol} as build_monthly_bills

    # A REGISTERED supply point, taken from the live roster: `build_monthly_bills`
    # looks its customer up through the supply-book seam and reads contract_type /
    # segment / commodity off the result, so an invented id would crash the probe
    # for a reason that has nothing to do with what it measures.
    roster = registered_supply_points()
    assert roster, "no registered supply points — the probe has nothing to bill"
    CUSTOMER_ID = roster[0]["customer_id"]


    class _Read:
        status = "actual"
        estimated_consumption_kwh = None
        consecutive_estimated_count = 0


    class _Feed:
        """A caller-supplied feed with no world in it — the go-live shape."""

        def meter_type_for(self, customer):
            return "traditional"

        def read_for(self, customer_id, period_end, meter_type, true_consumption_kwh,
                     trailing_actuals_kwh, consecutive_estimated_count):
            return _Read()

        def final_read_for(self, customer_id, period_end, meter_type, true_consumption_kwh):
            return _Read()


    def _record(customer_id, settlement_date, kwh, rate=200.0):
        return {{
            "customer_id": customer_id,
            "settlement_date": settlement_date,
            "settlement_period": 1,
            "consumption_kwh": kwh,
            "unit_rate_gbp_per_mwh": rate,
            "revenue_gbp": (kwh / 1000) * rate,
            "wholesale_cost_gbp": 0.0,
            "margin_gbp": 0.0,
        }}


    records = [
        _record(CUSTOMER_ID, "2024-01-15", 300.0),
        _record(CUSTOMER_ID, "2024-02-15", 280.0),
    ]
    bills = build_monthly_bills(records, _Feed())
    world = sorted(
        name for name in sys.modules
        if name in ("sim", "simulation") or name.startswith(("sim.", "simulation."))
    )
    print(json.dumps({{"bills": len(bills), "world": world}}))
    '''
)


def _run_probe(module: str, symbol: str, extra_path: str = "") -> dict:
    """Run one billing run in a CLEAN interpreter and report what it loaded.

    A clean interpreter is the point: in-process, `simulation.*` is already in
    `sys.modules` from the rest of the suite, so a lazy import would be served
    from cache and leave no trace. This sensor cannot be fooled that way.
    """
    script = _PROBE.format(
        repo=REPO_ROOT, module=module, symbol=symbol, extra_path=extra_path
    )
    proc = subprocess.run(
        [sys.executable, "-c", script],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=300,
    )
    assert proc.returncode == 0, (
        f"probe against {module} did not run:\n{proc.stdout}\n{proc.stderr}"
    )
    return json.loads(proc.stdout.strip().splitlines()[-1])


def test_the_billing_run_loads_no_world_module_at_call_time():
    """The inversion, verified by running it rather than by reading imports."""
    result = _run_probe("company.interfaces.bill_assembly", "assemble_monthly_bills")
    assert result["bills"] == 2, (
        "the probe must actually build bills — a run that produced nothing would "
        "report an empty world for the trivial reason that it did no work."
    )
    assert result["world"] == [], (
        "assembling the supplier's own bills pulled in simulation/sim modules: "
        f"{result['world']}. The company receives a ReadArrivalFeed; it must never "
        "import the world's read physics, statically OR lazily (see the seam "
        "module's 'WHY THE READ FEED GOES THE OTHER WAY')."
    )


def test_mutation_a_lazy_world_import_in_the_same_source_is_caught(tmp_path):
    """Perform the defect the static ratchet cannot see, and prove this sensor reds.

    The mutant is the REAL module's source with one line added inside
    `build_monthly_bills` — the exact convenience change the docstring names.
    """
    source_path = os.path.join(REPO_ROOT, "company", "billing", "monthly_bill_assembly.py")
    with open(source_path, encoding="utf-8") as handle:
        source = handle.read()

    anchor = "    churned_ids = churned_ids or set()\n"
    assert source.count(anchor) == 1, (
        "the mutation anchor moved; this test must be re-pointed rather than left "
        "to inject nothing and pass vacuously."
    )
    mutant_source = source.replace(
        anchor, anchor + "    import simulation.meter_reads  # THE DEFECT\n", 1
    )
    assert mutant_source != source

    mutant = tmp_path / "mutant_monthly_bill_assembly.py"
    mutant.write_text(mutant_source, encoding="utf-8")

    result = _run_probe(
        "mutant_monthly_bill_assembly",
        "build_monthly_bills",
        extra_path=f"sys.path.insert(0, {str(tmp_path)!r})",
    )
    assert result["world"], (
        "a lazy `import simulation.meter_reads` inside build_monthly_bills went "
        "UNDETECTED by this probe. The control is blind and the clean run above "
        "proves nothing."
    )
    assert "simulation.meter_reads" in result["world"]


# --------------------------------------------------------------------------
# CONTROL 2 — the world's feed matches the contract parameter for parameter.
# --------------------------------------------------------------------------

def _positional_names(func) -> list[str]:
    return [
        name for name, param in inspect.signature(func).parameters.items()
        if param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD)
    ]


@pytest.mark.parametrize("method", _FEED_METHODS)
def test_the_world_feed_matches_the_protocol_parameter_for_parameter(method):
    """Names AND order — because every call site passes positionally.

    `build_monthly_bills` calls `read_for(customer_id, period_end, meter_type,
    true_consumption_kwh, trailing_actuals_kwh, consecutive_estimated_count)`
    with no keywords. A reorder in either the Protocol or the adapter therefore
    swaps arguments silently rather than raising.
    """
    expected = _positional_names(getattr(ReadArrivalFeed, method))
    actual = _positional_names(getattr(SimulatedReadFeed, method))
    assert actual == expected, (
        f"simulation.meter_reads.SimulatedReadFeed.{method} takes {actual} but the "
        f"company's ReadArrivalFeed contract declares {expected}. The call sites are "
        "positional, so this mismatch does not raise — it mis-binds."
    )


def test_mutation_isinstance_alone_would_wave_a_reordered_feed_through():
    """Why the signature check exists: the Protocol check is fail-open on order.

    This is not a hypothetical about `typing` — it is the reason a presence check
    was not sufficient evidence for this seam.
    """

    class ReorderedFeed:
        """Same three methods; `read_for`'s last two parameters swapped."""

        def meter_type_for(self, customer):
            return "traditional"

        def read_for(self, customer_id, period_end, meter_type, true_consumption_kwh,
                     consecutive_estimated_count, trailing_actuals_kwh):
            raise AssertionError("not called")

        def final_read_for(self, customer_id, period_end, meter_type, true_consumption_kwh):
            raise AssertionError("not called")

    assert isinstance(ReorderedFeed(), ReadArrivalFeed), (
        "premise of this test: runtime_checkable Protocols check method presence "
        "only. If typing ever starts checking signatures, delete this test and say "
        "so — do not weaken the assertion."
    )
    assert _positional_names(ReorderedFeed.read_for) != _positional_names(
        ReadArrivalFeed.read_for
    ), "the reordering must actually differ, or the mutation proves nothing"
