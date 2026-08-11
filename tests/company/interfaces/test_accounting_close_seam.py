"""The accounting-close seam's contract — and the ways this cut could rot silently.

WHY THIS FILE EXISTS (R15: a control must be able to FAIL on its own named defect)
---------------------------------------------------------------------------------
KNIFE pass 3, `A_composition_lift` step 14, moved the supplier's month-end close
out of `simulation/run_phase4c_on_phase2b.py::main()` into
`company/finance/accounting_close.py` behind `company/interfaces/accounting_close.py`
— three wall crossings (`company.billing.pre_bill_validation`, `saas.ledger`,
`company.compliance.domain_invariants`).

The epistemic-wall ratchet polices the STATIC half: a module-scope
`company.finance.accounting_close -> simulation.*` import is a new class-(a)
edge, the forbidden direction, and reds the suite. Three things it cannot see:

1. **A lazy import.** The ratchet covers static imports only; an in-function
   `import simulation.…` escapes it. The natural convenience change here is to
   let the close reach for the run's own record set instead of being handed it.
   So control 1 is BEHAVIOURAL — it runs a real close in a clean interpreter and
   asks which modules got loaded.

2. **A silently reordered close.** The claim this cut rests on is that the five
   moved steps run in the same order with the same arguments as the code they
   replaced. Nothing static can see a step being dropped or reordered, and the
   effect of dropping the issuance gate is not a crash — it is a slightly larger
   revenue figure. Control 2 replicates the PRE-CUT inlined sequence from the
   HEAD source it was lifted from and asserts the door's output is identical.

3. **THE TAUTOLOGY, and it is the interesting one.** The billed-clock invariant
   asks whether the ledger's recognised revenue reconciles with the bills that
   fed it, and BOTH sides are now computed inside one function, four lines
   apart. Feed `bills` (the unfiltered list) to `build_ledger` *and* to
   `check_billed_clock_reconciles` and the invariant still returns True — it
   would be comparing a population against itself, which is exactly the R15
   TAUTOLOGY pattern (checked value derived from the same source it checks).
   The defect it exists to catch — a HELD bill's revenue recognised before
   issuance — would sail through green. Before the move, the two calls sat in
   different paragraphs of a 419-line run module; now they are adjacent, so the
   mistake is one keystroke away. Control 3 fires on it independently, by asking
   the EVENTS whether the held bill's money is in the books at all.

Each `test_mutation_*` performs the named defect rather than asserting it is
impossible.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap

import pytest

from company.compliance.domain_invariants import check_billed_clock_reconciles
from company.finance import accounting_close as impl
from company.interfaces import accounting_close as door

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


# ---------------------------------------------------------------------------
# Fixtures — the smallest input that exercises every moved step.
# ---------------------------------------------------------------------------


def _record(customer_id: str, date: str, period: int) -> dict:
    return {
        "customer_id": customer_id,
        "settlement_date": date,
        "settlement_period": period,
        "commodity": "electricity",
        "wholesale_cost_gbp": 3.25,
        "consumption_kwh": 40.0,
        "unit_rate_gbp_per_mwh": 81.25,
        "capital_cost_gbp": 0.4,
    }


def _bill(customer_id: str, start: str, end: str, total: float) -> dict:
    """A bill that PASSES the Tier-1 issuance gate: it foots, its line items are
    non-negative, its period is sane, and its VAT is the rate the gate's
    `vat_by_segment` check expects for a `resi` account (5%, the UK domestic
    reduced rate). `total` is the NET of VAT; the gross is derived."""
    commodity = round(total * 0.70, 2)
    non_commodity = round(total * 0.20, 2)
    standing = round(total - commodity - non_commodity, 2)
    vat = round((commodity + non_commodity + standing) * 0.05, 2)
    total = round(commodity + non_commodity + standing + vat, 2)
    return {
        "customer_id": customer_id,
        "segment": "resi",
        "commodity": "electricity",
        "period_start": start,
        "period_end": end,
        "total_consumption_kwh": 300.0,
        "commodity_amount_gbp": commodity,
        "non_commodity_amount_gbp": non_commodity,
        "standing_charge_gbp": standing,
        "vat_gbp": vat,
        "total_amount_gbp": total,
    }


def _held_bill() -> dict:
    """A bill the Tier-1 gate HOLDS: the declared total does not foot to its own
    components. Held means NOT ISSUED, so its money must never be recognised."""
    bill = _bill("C_HELD", "2024-03-01", "2024-03-31", 500.00)
    bill["total_amount_gbp"] = 9_999.00  # does not foot — HELD
    return bill


class _NoProvisionModel:
    """The supplier's payment model, stubbed to provision nothing.

    Deliberate: a non-zero provision makes `build_ledger` write a real
    `CREDIT_COLLECTIONS_POLICY` entry to the decision log, and a unit test has no
    business appending to the company's audit trail. The provisioning path is
    exercised separately in `test_provisioning_path_is_reached_through_the_door`
    with the log write patched out.
    """

    CREDIT_RISK_BY_CUSTOMER: dict[str, str] = {}
    DEFAULT_CREDIT_RISK = "low"

    @staticmethod
    def bad_debt_provision_gbp(credit_risk, amount_gbp):  # noqa: ARG004
        return 0.0

    @staticmethod
    def expected_payment_date(period_end, credit_risk):  # noqa: ARG004
        return period_end


def _inputs():
    records = [
        _record("C1", "2024-01-15", 1),
        _record("C1", "2024-01-15", 2),
        _record("C2", "2024-02-15", 1),
    ]
    bills = [
        _bill("C1", "2024-01-01", "2024-01-31", 120.00),
        _bill("C2", "2024-02-01", "2024-02-29", 240.00),
        _held_bill(),
    ]
    acquisition = [
        {
            "transaction_id": "acq-2024-01",
            "event_type": "acquisition_spend_event",
            "timestamp": "2024-01-01",
            "month": "2024-01",
            "amount_gbp": -50.0,
        }
    ]
    fixed = [
        {
            "transaction_id": "fix-2024-01",
            "event_type": "fixed_cost_event",
            "timestamp": "2024-01-01",
            "month": "2024-01",
            "amount_gbp": -30.0,
        }
    ]
    cts = [{"month": "2024-01", "amount_gbp": 12.5}, {"month": "2024-02", "amount_gbp": 11.0}]
    return records, bills, acquisition, fixed, cts


def _close(**overrides):
    records, bills, acquisition, fixed, cts = _inputs()
    kwargs = dict(
        acquisition_spend_events=acquisition,
        fixed_cost_events=fixed,
        cost_to_serve_ledger_events=cts,
        payment_model=_NoProvisionModel,
    )
    kwargs.update(overrides)
    return door.close_the_books(records, bills, **kwargs)


# ---------------------------------------------------------------------------
# The door
# ---------------------------------------------------------------------------


def test_the_door_re_exports_the_implementation():
    assert door.close_the_books is impl.close_the_books
    assert door.AccountingClose is impl.AccountingClose
    assert set(door.__all__) == {"AccountingClose", "close_the_books"}


def test_the_run_module_reaches_the_close_only_through_the_door():
    """The world imports the seam, not the implementation and not the three
    modules the close was lifted out of."""
    source = open(os.path.join(REPO_ROOT, "simulation", "run_phase4c_on_phase2b.py")).read()
    assert "from company.interfaces.accounting_close import close_the_books" in source
    for forbidden in (
        "company.finance.accounting_close",
        "company.billing.pre_bill_validation",
        "company.compliance.domain_invariants",
        "saas.ledger",
    ):
        assert forbidden not in source, f"{forbidden} is reachable from the run module again"


# ---------------------------------------------------------------------------
# CONTROL 1 — the close must not reach back across the wall, statically OR lazily
# ---------------------------------------------------------------------------


_PROBE = textwrap.dedent(
    """
    import json, sys
    sys.path.insert(0, {root!r})
    from company.interfaces.accounting_close import close_the_books
    inputs = json.loads(sys.stdin.read())

    class M:
        CREDIT_RISK_BY_CUSTOMER = {{}}
        DEFAULT_CREDIT_RISK = "low"
        @staticmethod
        def bad_debt_provision_gbp(r, a): return 0.0
        @staticmethod
        def expected_payment_date(p, r): return p

    close_the_books(
        inputs["records"], inputs["bills"],
        acquisition_spend_events=inputs["acquisition"],
        fixed_cost_events=inputs["fixed"],
        cost_to_serve_ledger_events=inputs["cts"],
        payment_model=M,
    )
    print(json.dumps(sorted(
        m for m in sys.modules
        if m == "simulation" or m.startswith("simulation.")
        or m == "sim" or m.startswith("sim.")
    )))
    """
)


def _run_probe(probe: str) -> list[str]:
    records, bills, acquisition, fixed, cts = _inputs()
    payload = json.dumps(
        {
            "records": records,
            "bills": bills,
            "acquisition": acquisition,
            "fixed": fixed,
            "cts": cts,
        }
    )
    result = subprocess.run(
        [sys.executable, "-c", probe],
        input=payload,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=300,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout.strip().splitlines()[-1])


def test_closing_the_books_loads_no_world_module():
    """Behavioural, not static: a real close in a clean interpreter, then ask
    which modules the import system actually loaded. An in-function
    `import simulation.…` is invisible to the ratchet and visible here."""
    assert _run_probe(_PROBE.format(root=REPO_ROOT)) == []


def test_mutation_a_lazy_world_import_inside_the_close_is_caught():
    """Perform the defect: reach for the world from inside the close, the way a
    convenience default would. The static ratchet stays green; control 1 fires."""
    mutated = _PROBE.format(root=REPO_ROOT).replace(
        "from company.interfaces.accounting_close import close_the_books",
        "from company.interfaces.accounting_close import close_the_books as _c\n"
        "def close_the_books(*a, **k):\n"
        "    import simulation.meter_reads  # noqa: F401  <- the defect\n"
        "    return _c(*a, **k)",
    )
    loaded = _run_probe(mutated)
    assert loaded, "the lazy world import was not observed — control 1 is blind"
    assert any(m.startswith("simulation") for m in loaded)


# ---------------------------------------------------------------------------
# CONTROL 2 — the moved sequence is the sequence that was lifted
# ---------------------------------------------------------------------------


def _pre_cut_sequence(records, bills, acquisition, fixed, cts, payment_model):
    """The inlined close EXACTLY as `simulation/run_phase4c_on_phase2b.py::main()`
    ran it before step 14 — transcribed from that source, not from the module
    under test, which is what makes this a characterization and not a mirror."""
    from company.billing.pre_bill_validation import validate_bills
    from saas.ledger import build_ledger, derive_pnl, ledger_summary, make_cost_to_serve_event

    extra_events = (
        acquisition
        + fixed
        + [make_cost_to_serve_event(e["month"], e["amount_gbp"]) for e in cts]
    )
    issued_bills, _held = validate_bills(bills)
    ledger_events = build_ledger(
        records, issued_bills, payment_model, extra_events=extra_events or None
    )
    ledger_pnl = derive_pnl(ledger_events)
    ledger_meta = ledger_summary(ledger_events)
    ledger_meta["billed_clock_reconciles_with_issued_bills"] = check_billed_clock_reconciles(
        ledger_pnl.get("total_billed_gbp", 0.0), issued_bills
    )
    return ledger_events, ledger_pnl, ledger_meta


def test_the_close_is_identical_to_the_sequence_it_replaced():
    records, bills, acquisition, fixed, cts = _inputs()
    want_events, want_pnl, want_meta = _pre_cut_sequence(
        records, bills, acquisition, fixed, cts, _NoProvisionModel
    )
    got = _close()
    assert got.events == want_events
    assert got.pnl == want_pnl
    assert got.meta == want_meta


def test_mutation_dropping_the_issuance_gate_is_caught():
    """Perform the defect: post every bill, held ones included. Revenue rises and
    nothing crashes — control 2 is what notices."""
    records, bills, acquisition, fixed, cts = _inputs()
    want_events, _, _ = _pre_cut_sequence(
        records, bills, acquisition, fixed, cts, _NoProvisionModel
    )
    from saas.ledger import build_ledger

    mutated = build_ledger(records, bills, _NoProvisionModel, extra_events=None)
    assert mutated != want_events, "dropping the gate changed nothing — the fixture is inert"


def test_mutation_reordering_the_extra_events_is_caught():
    """Perform the defect: merge the extra events in a different order.

    Stating the limit first, because it decides how this control is built.
    `build_ledger` sorts by `(timestamp, settlement_period, event_type)` with
    Python's STABLE sort, so swapping the acquisition and fixed-cost schedules
    is genuinely unobservable — those two differ in `event_type`, so the sort is
    total over them and the merge order carries no information. A control built
    on that swap would be a control that cannot fail.

    Order is observable exactly where the sort key TIES. Two acquisition events
    in the same month tie on all three components, so their relative order
    survives into the ledger — and that is the fixture used here.
    """
    records, bills, acquisition, fixed, cts = _inputs()

    twin = dict(acquisition[0])
    twin["transaction_id"] = "acq-2024-01-b"
    twin["amount_gbp"] = -75.0
    tied = [acquisition[0], twin]

    want_events, _, _ = _pre_cut_sequence(
        records, bills, tied, fixed, cts, _NoProvisionModel
    )
    swapped, _, _ = _pre_cut_sequence(
        records, bills, list(reversed(tied)), fixed, cts, _NoProvisionModel
    )
    assert swapped != want_events, (
        "the reorder was not observable — this control cannot fail and must be "
        "rebuilt before it is trusted"
    )

    # ...and the door reproduces the ORDER, not merely the set.
    got = _close(acquisition_spend_events=tied)
    assert got.events == want_events


# ---------------------------------------------------------------------------
# CONTROL 3 — the billed-clock invariant is a TAUTOLOGY on its own, and this is
# the independent check that is not
# ---------------------------------------------------------------------------


def test_a_held_bills_money_never_reaches_the_books():
    """Independent of the invariant: ask the EVENTS. The held bill's £9,999 must
    not appear as a billing event, and the held half must come back so the
    caller knows a bill was withheld."""
    closed = _close()
    billed = [e for e in closed.events if e["event_type"] == "billing_event"]
    assert all(e["amount_gbp"] != pytest.approx(9_999.00) for e in billed)
    assert "C_HELD" not in {b["customer_id"] for b in closed.issued_bills}
    assert len(closed.held_bills) == 1
    assert closed.meta["billed_clock_reconciles_with_issued_bills"] is True


def test_mutation_feeding_both_sides_the_same_population_leaves_the_invariant_green():
    """THE TAUTOLOGY, performed. Post the UNFILTERED bills and reconcile against
    the UNFILTERED bills: the held bill's £9,999 is now recognised revenue — a
    real accounting error — and `check_billed_clock_reconciles` still says True.

    This is not a bug in the invariant; it is the shape R15 names. The invariant
    is only a control while its two sides come from different populations, and
    after step 14 both calls sit four lines apart in one function. The assertion
    below is the reason `test_a_held_bills_money_never_reaches_the_books` asks
    the events rather than trusting the flag.
    """
    from saas.ledger import build_ledger, derive_pnl

    records, bills, _, _, _ = _inputs()
    tautological_events = build_ledger(records, bills, _NoProvisionModel, extra_events=None)
    tautological_pnl = derive_pnl(tautological_events)

    assert check_billed_clock_reconciles(
        tautological_pnl.get("total_billed_gbp", 0.0), bills
    ), "the tautology did not reproduce — re-derive this control before trusting it"

    # ...and the same books fail the moment the check is given the population
    # that SHOULD have fed them.
    issued = [b for b in bills if b["customer_id"] != "C_HELD"]
    assert not check_billed_clock_reconciles(
        tautological_pnl.get("total_billed_gbp", 0.0), issued
    )


# ---------------------------------------------------------------------------
# The provisioning path, and the default the world no longer supplies
# ---------------------------------------------------------------------------


def test_the_default_payment_model_is_the_companys_own():
    """The world used to hand `saas.payment_behaviour` in. It no longer does, and
    the default must be that same module — not None, which would silently drop
    every payment and bad-debt event from the ledger."""
    import saas.payment_behaviour

    assert impl._default_payment_model is saas.payment_behaviour


def test_provisioning_path_is_reached_through_the_door(monkeypatch):
    """With a provisioning model the close must emit payment and bad-debt events.
    The decision-log write is patched out — a unit test does not append to the
    company's audit trail — and the patch is asserted to have FIRED, so this
    cannot pass by the path never being reached."""
    import saas.ledger as ledger_module

    calls = []
    monkeypatch.setattr(
        ledger_module, "log_decision_event", lambda *a, **k: calls.append(k)
    )

    class Provisioning(_NoProvisionModel):
        @staticmethod
        def bad_debt_provision_gbp(credit_risk, amount_gbp):  # noqa: ARG004
            return round(amount_gbp * 0.05, 2)

    closed = _close(payment_model=Provisioning)
    types = {e["event_type"] for e in closed.events}
    assert "payment_received_event" in types
    assert "bad_debt_event" in types
    assert calls, "the decision-log write never fired — the provisioning path was not reached"
