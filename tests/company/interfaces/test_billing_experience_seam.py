"""The billing-experience seam's contract — and the ways this cut could rot silently.

WHY THIS FILE EXISTS (R15: a control must be able to FAIL on its own named defect)
---------------------------------------------------------------------------------
KNIFE pass 3, `A_composition_lift` step 16, moved the supplier's
billing-experience layer out of `simulation/run_phase4c_on_phase2b.py::main()`
into `company/analytics/billing_experience_view.py` behind
`company/interfaces/billing_experience.py` — two wall crossings
(`saas.payment_behaviour`, `saas.contact_model`).

The epistemic-wall ratchet polices the STATIC half: a module-scope
`company.analytics.billing_experience_view -> simulation.*` import is a new
class-(a) edge, the forbidden direction, and reds the suite. Three things it
cannot see:

1. **A lazy import.** The ratchet covers static imports only; an in-function
   `import simulation.…` escapes it. Control 1 is BEHAVIOURAL: it builds a real
   view in a clean interpreter and asks which modules the import system actually
   loaded.

2. **A silently dropped or reshaped builder.** The claim this cut rests on is
   that the two moved calls run with the same argument as the code they
   replaced. Control 2 replicates the PRE-CUT inlined sequence transcribed from
   the source it was lifted out of (not from the module under test, which would
   be a mirror) and asserts both outputs are identical.

3. **THE FILTER, and it is the defect this particular cut invites.** Roughly 120
   lines below the moved call, `close_the_books` partitions these same bills
   through the Tier-1 issuance gate and recognises revenue only against the
   ISSUED half (register §3i). The obvious tidy-up when recomposing is to apply
   the same filter here "for consistency". It would silently change the bad-debt
   provision — a HELD bill is one the supplier has not sent, but the provision
   it books against that customer's credit risk does not vanish, and the pre-cut
   code provisioned against every bill. Nothing static sees it and the effect is
   not a crash, it is a smaller number. Control 3 performs exactly that filter
   with the real `validate_bills` and asserts the view moves, with a vacuity
   guard proving the fixture actually contains a HELD bill.

WHAT THIS FILE DELIBERATELY DOES NOT CONTROL, stated so its absence is not read
as a clean bill. `simulation/contact_centre.py` draws the world's ACTUAL contact
events off the `contact_probability` this view computes — the supplier's belief
constituting the world's outcome, the B2/B3 inversion. That leak pre-dates this
cut and is untouched by it; the implementation docstring records it and §3k
files it. A control here would either pin the leak in place or fail on day one,
and neither is this seam's job.

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

from company.analytics import billing_experience_view as impl
from company.interfaces import billing_experience as door

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RUN_MODULE_PATH = os.path.join(REPO_ROOT, "simulation", "run_phase4c_on_phase2b.py")


# ---------------------------------------------------------------------------
# Fixtures — the smallest bill book that exercises both builders AND control 3.
#
# The bills carry the FULL shape `company/billing/pre_bill_validation.py`
# documents (period_start/end, segment, commodity, consumption, the three
# component amounts, VAT), not the two fields the two builders happen to read.
# That is deliberate: control 3 runs the real Tier-1 gate over this same book,
# and a fixture shaped only to the modules under test would make the gate throw
# rather than judge — a control that errors on its own input proves nothing.
#
# `C3` is `vulnerable` in `CREDIT_RISK_BY_CUSTOMER` and `C1` is `low`, so the
# provision rates differ by 16x across the book; a book at one rate would make a
# dropped bill hard to tell from a re-scaled one. The fourth bill is built to
# FAIL the gate on consumption plausibility, and the vacuity guard below asserts
# that it actually does.
# ---------------------------------------------------------------------------

_VAT_RATE_DOMESTIC = 0.05


def _bill(
    customer_id: str,
    period_start: str,
    period_end: str,
    kwh: float,
    commodity_gbp: float,
    clarity_score: float,
    bill_shock_pct: float | None,
) -> dict:
    """One bill that foots exactly, at the domestic VAT rate — so the Tier-1
    gate's arithmetic, sign, period and VAT checks all pass and the only thing
    that can hold a bill in this book is the one defect we put there."""
    non_commodity_gbp = round(commodity_gbp * 0.25, 2)
    standing_charge_gbp = 18.25
    subtotal = round(commodity_gbp + non_commodity_gbp + standing_charge_gbp, 2)
    vat_gbp = round(subtotal * _VAT_RATE_DOMESTIC, 2)
    return {
        "customer_id": customer_id,
        "period_start": period_start,
        "period_end": period_end,
        "segment": "resi",
        "commodity": "electricity",
        "total_consumption_kwh": kwh,
        "commodity_amount_gbp": commodity_gbp,
        "non_commodity_amount_gbp": non_commodity_gbp,
        "standing_charge_gbp": standing_charge_gbp,
        "vat_gbp": vat_gbp,
        "total_amount_gbp": round(subtotal + vat_gbp, 2),
        "clarity_score": clarity_score,
        "bill_shock_pct": bill_shock_pct,
    }


def _bills() -> list[dict]:
    return [
        _bill("C1", "2024-01-01", "2024-01-31", 280.0, 92.0, 0.9, None),
        _bill("C1", "2024-02-01", "2024-02-29", 300.0, 199.0, 0.4, 1.16),
        _bill("C3", "2024-01-01", "2024-01-31", 340.0, 240.0, 0.7, None),
        # The one built to be HELD: an implausible resi electricity load for a
        # one-month period. Everything else about it foots.
        _bill("C3", "2024-02-01", "2024-02-29", 90_000.0, 310.0, 0.5, 0.6),
    ]


@pytest.fixture()
def view():
    return door.build_billing_experience_view(_bills())


def test_the_fixture_is_not_vacuous(view):
    """Every identity control below compares structures built from this book. An
    empty book would make them compare empty against empty and pass for free —
    the population-control vacuity shape."""
    assert view.payment_behaviour, "no accounts scored — the identity controls are vacuous"
    assert view.contact_model["by_customer"], "no contact records — control 2 is vacuous"
    assert view.contact_model["portfolio"]["avg_complaint_probability"] > 0
    assert (
        sum(
            record["bad_debt_provision_gbp"]
            for records in view.payment_behaviour.values()
            for record in records
        )
        != 0
    )


# ---------------------------------------------------------------------------
# The door
# ---------------------------------------------------------------------------


def test_the_door_re_exports_the_implementation():
    assert door.build_billing_experience_view is impl.build_billing_experience_view
    assert door.BillingExperienceView is impl.BillingExperienceView
    assert set(door.__all__) == {"BillingExperienceView", "build_billing_experience_view"}


def test_the_run_module_reaches_the_view_only_through_the_door():
    """The world imports the seam, not the implementation and not the two
    modules the view was lifted out of."""
    source = open(RUN_MODULE_PATH).read()
    assert (
        "from company.interfaces.billing_experience import build_billing_experience_view"
        in source
    )
    for forbidden in (
        "company.analytics.billing_experience_view",
        "from saas.contact_model import",
        "from saas.payment_behaviour import",
    ):
        assert forbidden not in source, f"{forbidden} is reachable from the run module again"


# ---------------------------------------------------------------------------
# CONTROL 1 — the view must not reach back across the wall, statically OR lazily
# ---------------------------------------------------------------------------


_PROBE = textwrap.dedent(
    """
    import json, sys
    sys.path.insert(0, {root!r})
    from company.interfaces.billing_experience import build_billing_experience_view
    bills = json.loads(sys.stdin.read())
    build_billing_experience_view(bills)
    print(json.dumps(sorted(
        m for m in sys.modules
        if m == "simulation" or m.startswith("simulation.")
        or m == "sim" or m.startswith("sim.")
    )))
    """
)


def _run_probe(probe: str) -> list[str]:
    result = subprocess.run(
        [sys.executable, "-c", probe],
        input=json.dumps(_bills()),
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=300,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout.strip().splitlines()[-1])


def test_building_the_view_loads_no_world_module():
    """Behavioural, not static: a real build in a clean interpreter, then ask
    which modules the import system actually loaded. An in-function
    `import simulation.…` is invisible to the ratchet and visible here."""
    assert _run_probe(_PROBE.format(root=REPO_ROOT)) == []


def test_mutation_a_lazy_world_import_inside_the_view_is_caught():
    """Perform the defect: reach into the world from inside the view, the way a
    convenience default would. The static ratchet stays green; control 1 fires."""
    mutated = _PROBE.format(root=REPO_ROOT).replace(
        "from company.interfaces.billing_experience import build_billing_experience_view",
        "from company.interfaces.billing_experience import "
        "build_billing_experience_view as _b\n"
        "def build_billing_experience_view(*a, **k):\n"
        "    import simulation.contact_centre  # noqa: F401  <- the defect\n"
        "    return _b(*a, **k)",
    )
    loaded = _run_probe(mutated)
    assert loaded, "the lazy world import was not observed — control 1 is blind"
    assert any(m.startswith("simulation") for m in loaded)


# ---------------------------------------------------------------------------
# CONTROL 2 — the moved composition is the composition that was lifted
# ---------------------------------------------------------------------------


def _pre_cut_sequence(bills):
    """The inlined billing-experience layer EXACTLY as
    `simulation/run_phase4c_on_phase2b.py::main()` ran it before step 16 —
    transcribed from that source, not from the module under test, which is what
    makes this a characterization and not a mirror."""
    from saas.contact_model import build_contact_model
    from saas.payment_behaviour import build_payment_behaviour

    payment_behaviour = build_payment_behaviour(bills)
    contact_model = build_contact_model(bills)
    return {"payment_behaviour": payment_behaviour, "contact_model": contact_model}


def test_the_view_is_identical_to_the_sequence_it_replaced(view):
    expected = _pre_cut_sequence(_bills())
    assert view.payment_behaviour == expected["payment_behaviour"]
    assert view.contact_model == expected["contact_model"]


def test_mutation_dropping_a_builder_is_caught():
    """Perform the defect: a recomposition that keeps the door's shape but loses
    one of the two beliefs. The `None` a dropped builder would leave behind is
    not what the pre-cut code produced, and control 2 fires on it."""
    half_built = impl.BillingExperienceView(
        payment_behaviour=_pre_cut_sequence(_bills())["payment_behaviour"],
        contact_model={},
    )
    expected = _pre_cut_sequence(_bills())
    assert half_built.contact_model != expected["contact_model"], (
        "an empty contact model compares equal to the real one — the fixture "
        "produces no contact records and control 2 cannot discriminate"
    )


# ---------------------------------------------------------------------------
# CONTROL 3 — the bill list crosses UNFILTERED, and that is a decision
# ---------------------------------------------------------------------------


def _issued_only(bills: list[dict]) -> list[dict]:
    """The close's own Tier-1 partition, applied to the same book — the exact
    'tidy-up for consistency' this control exists to catch."""
    from company.billing.pre_bill_validation import validate_bills

    issued, _held = validate_bills(bills)
    return issued


def test_the_fixture_actually_contains_a_held_bill():
    """VACUITY GUARD. Control 3 compares a filtered book against the full one; if
    the gate held nothing, the two lists would be identical and the control would
    pass for free while proving nothing. If the issuance rules move and stop
    holding this bill, this fails loudly and the fixture must be rebuilt — not
    the control quietly retired."""
    bills = _bills()
    issued = _issued_only(bills)
    assert len(issued) < len(bills), (
        "the Tier-1 issuance gate held no bill in this fixture — control 3 is "
        "comparing a book against itself"
    )


def test_mutation_filtering_to_the_issued_half_moves_the_view(view):
    """Perform the defect: hand the view the same bills the close recognises
    revenue against. The provision falls silently — no exception, no static
    signal, just a smaller bad-debt number in the run output."""
    filtered = door.build_billing_experience_view(_issued_only(_bills()))

    def _provision(v):
        return sum(
            record["bad_debt_provision_gbp"]
            for records in v.payment_behaviour.values()
            for record in records
        )

    assert _provision(filtered) != _provision(view), (
        "filtering to the issued half left the provision unchanged — control 3 "
        "cannot discriminate on this fixture"
    )
    assert filtered.contact_model != view.contact_model
