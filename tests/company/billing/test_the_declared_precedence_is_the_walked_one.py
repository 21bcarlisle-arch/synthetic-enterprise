"""THE DEFECT THIS CONTROL EXISTS TO CATCH: the annual-consumption estimator
DECLARING a precedence deeper than the one any caller can walk.

Until 2026-09-03 ``BASIS_ORDER`` named four rungs -- ``METERED_HISTORY``,
``REGISTRY_EAC``, ``CUSTOMER_DECLARED``, ``TDCV_TYPICAL`` -- and the sole
production caller (``simulation/run_phase4c_on_phase2b._opening_dd_by_customer``,
through ``company/interfaces/dd_review_outcome.opening_monthly_amount``) passed
``as_of_iso``, ``commodity``, ``registry_eac_kwh`` and ``band``. Two of the four
rungs could not be entered by any account, ever. The top one -- metered history --
is the ONLY rung in that list the company would have had to reason from rather
than be handed, so the branch that never ran was precisely the one carrying the
thesis: *the advantage must come from inference, never from access.*

A precedence whose top branches never execute reports a constant verdict. That is
the failure class this repository catalogues more often than any other, and it
was doing it to the module the direct-debit atom rests on.

WHY THIS IS A CONTROL AND NOT A DOCSTRING
-----------------------------------------
The settlement is an EQUALITY between two sets that live in different places --
what the module declares, and what a caller can reach -- and nothing about the
language makes them move together. Re-adding an ignored ``metered_annual_kwh=``
parameter would restore the exact defect while every existing test stayed green:
no assertion anywhere reads the estimator's signature.

KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. None of these tests pin the current
rungs, the current counts or the current reasons. They assert that the declared
set, the walked set and the excused set partition the enum and that each excused
rung is unreachable by construction. If a declaration ever DOES reach the
registration flow, the honest change is to move ``CUSTOMER_DECLARED`` from
``NOT_REACHABLE_AT_OPENING`` back into ``BASIS_ORDER`` and give it a parameter --
and every test here stays green, because the property held throughout. What
cannot happen without a red is the two sets silently diverging again.

MUTATION-PROVEN under ``python3 -B`` (never a stale .pyc). Four mutations, each
naming the test it turns red:

  1. Re-adding ``metered_annual_kwh: Optional[float] = None`` to
     ``estimate_annual_consumption`` and its branch, with ``BASIS_ORDER``
     unchanged --> ``test_an_excused_rung_has_no_parameter_to_arrive_through``.
  2. Putting ``ConsumptionBasis.METERED_HISTORY`` back at the head of
     ``BASIS_ORDER`` without restoring the parameter --> FOUR legs red, and the
     fourth is the one that matters most:
     ``test_every_declared_rung_is_witnessed_by_a_real_input``,
     ``test_the_declared_rungs_are_walked_in_the_declared_order``,
     ``test_the_enum_is_partitioned_by_walked_excused_and_unavailable`` and
     ``test_the_live_production_route_walks_only_declared_rungs``. The last
     proves the equality is checked against the real book and not only a
     fixture, which is the difference between mutation-proved and ever-ran.
  3. Dropping the ``CUSTOMER_DECLARED`` entry from
     ``NOT_REACHABLE_AT_OPENING`` -->
     ``test_the_enum_is_partitioned_by_walked_excused_and_unavailable``.
  4. Giving both exclusions the same reason string -->
     ``test_the_two_exclusions_do_not_share_one_reason``.
"""
from __future__ import annotations

import inspect
from datetime import date

import pytest

from company.billing.annual_consumption_estimate import (
    BASIS_ORDER,
    NOT_REACHABLE_AT_OPENING,
    ConsumptionBasis,
    estimate_annual_consumption,
)
from company.interfaces.dd_review_outcome import opening_monthly_amount

#: One input set per declared rung that establishes THAT rung and no other. Each
#: is a SOLE WITNESS: a fixture satisfying two branches makes each of them an
#: equivalence, so `registry_eac_kwh` is supplied without a band and the band is
#: supplied without an EAC. `as_of` sits inside the published TDCV series.
SOLE_WITNESS: dict[ConsumptionBasis, dict] = {
    ConsumptionBasis.REGISTRY_EAC: dict(
        as_of=date(2021, 6, 1), commodity="electricity", registry_eac_kwh=3300.0
    ),
    ConsumptionBasis.TDCV_TYPICAL: dict(
        as_of=date(2021, 6, 1), commodity="electricity", band="MEDIUM"
    ),
}


def test_every_declared_rung_is_witnessed_by_a_real_input():
    """Each rung in BASIS_ORDER must be reachable -- a declared rung nothing can
    enter is the defect itself.

    Fails if a rung is added to BASIS_ORDER without a way in (mutation 2). The
    ``SOLE_WITNESS`` table is required to cover BASIS_ORDER exactly, so putting
    METERED_HISTORY back cannot be satisfied by the table simply not mentioning
    it.
    """
    assert set(SOLE_WITNESS) == set(BASIS_ORDER), (
        "SOLE_WITNESS and BASIS_ORDER disagree about the declared rungs: "
        f"declared-not-witnessed={set(BASIS_ORDER) - set(SOLE_WITNESS)}, "
        f"witnessed-not-declared={set(SOLE_WITNESS) - set(BASIS_ORDER)}. A rung "
        "with no input that reaches it does not belong in the precedence."
    )
    for basis, kwargs in SOLE_WITNESS.items():
        est = estimate_annual_consumption(**kwargs)
        assert est.basis is basis, f"{kwargs} reached {est.basis}, not {basis}"
        assert est.is_established, f"{basis} witness established no figure"


def test_the_declared_rungs_are_walked_in_the_declared_order():
    """Supplying a lower rung's input alongside a higher one's must yield the
    HIGHER. Without this the tuple is a list, not a precedence."""
    est = estimate_annual_consumption(
        as_of=date(2021, 6, 1),
        commodity="electricity",
        registry_eac_kwh=3300.0,
        band="MEDIUM",
    )
    assert est.basis is BASIS_ORDER[0], (
        f"both inputs present and the estimator chose {est.basis}, but "
        f"BASIS_ORDER puts {BASIS_ORDER[0]} first"
    )
    assert est.kwh == 3300.0


@pytest.mark.parametrize("excluded", NOT_REACHABLE_AT_OPENING, ids=lambda e: e.basis.value)
@pytest.mark.parametrize(
    "door", [estimate_annual_consumption, opening_monthly_amount], ids=lambda f: f.__name__
)
def test_an_excused_rung_has_no_parameter_to_arrive_through(door, excluded):
    """UNREACHABLE BY CONSTRUCTION, not by a parameter accepted and ignored.

    This is the leg that catches mutation 1, and it is the reason the exclusion
    records ``input_parameter`` rather than only prose. A refusal keyed to a
    signature lifts the moment the signature widens, so the absence itself is
    what gets asserted -- on the estimator AND on the seam door, because a
    parameter restored at either end restores the false advertisement.
    """
    params = inspect.signature(door).parameters
    assert excluded.input_parameter not in params, (
        f"{door.__name__} accepts {excluded.input_parameter!r}, but "
        f"{excluded.basis.value} is not in BASIS_ORDER. Either the rung is "
        "reachable and belongs in the precedence, or the parameter is a branch "
        "that can never execute. It cannot be both."
    )


def test_the_enum_is_partitioned_by_walked_excused_and_unavailable():
    """Every ConsumptionBasis is walked, excused with a reason, or UNAVAILABLE --
    and no member is two of those.

    Fails if a rung is declared without being reachable (mutation 2) or dropped
    from the exclusions without being restored to the precedence (mutation 3).
    This is the assertion that makes "the declared set and the walked set are
    the same set" checkable rather than claimed.
    """
    walked = set(BASIS_ORDER)
    excused = {e.basis for e in NOT_REACHABLE_AT_OPENING}
    sentinel = {ConsumptionBasis.UNAVAILABLE}

    assert walked & excused == set(), (
        f"{walked & excused} is both declared as walked and excused as "
        "unreachable"
    )
    assert (walked | excused) & sentinel == set(), (
        "UNAVAILABLE is the honest-absence sentinel and is neither a source nor "
        "an excused source"
    )
    assert walked | excused | sentinel == set(ConsumptionBasis), (
        "unaccounted-for bases: "
        f"{set(ConsumptionBasis) - (walked | excused | sentinel)}. A basis the "
        "enum names must either be reachable or say why it is not."
    )


def test_every_exclusion_names_a_substantive_reason():
    """An exclusion without a reason is silence with a data structure around it."""
    for excluded in NOT_REACHABLE_AT_OPENING:
        assert excluded.reason.strip(), f"{excluded.basis} is excused with no reason"
        assert len(excluded.reason.split()) >= 20, (
            f"{excluded.basis}'s reason is {len(excluded.reason.split())} words. "
            "It has to say what kind of absence this is and whether it can ever "
            "lift -- that is the difference between a finding and a shrug."
        )


def test_the_two_exclusions_do_not_share_one_reason():
    """DIFFERENT ABSENCES, DIFFERENT REASONS.

    Metered history is definitional and never lifts; a customer declaration is a
    world gap that lifts when the registration flow carries one. Collapsing both
    into one "no data available" is this project's most expensive recurring
    shape -- distinct causes differenced under a single label -- and it would
    take the second rung out of anyone's reach for good, because nothing would
    record that it was ever recoverable.
    """
    reasons = [e.reason.strip() for e in NOT_REACHABLE_AT_OPENING]
    assert len(set(reasons)) == len(reasons), (
        "two rungs are excused with the identical reason, so at least one of "
        "them is not being explained"
    )


def test_the_live_production_route_walks_only_declared_rungs():
    """THE LEG THAT MEASURES PRODUCTION RATHER THAN A FIXTURE.

    Mutation-proved is not the same as ever-ran: the tests above would all pass
    against a module no caller uses. This one drives the REAL book through the
    real caller's argument mapping and asserts two things at once -- nothing
    outside BASIS_ORDER is produced, and every rung IN BASIS_ORDER is produced
    by at least one real account. The second half is what stops the equality
    being restored by declaring a rung nothing reaches.

    It imports the world INSIDE the test on purpose: `tests/` is outside
    `epistemic_wall.WALL_DIRS`, so holding both sides here is legitimate, but a
    module-level import would make an expensive world import the price of
    collecting this file.
    """
    from simulation.run_phase4c_on_phase2b import CUSTOMERS, SUCCESSOR_CUSTOMERS

    seen: dict[ConsumptionBasis, int] = {}
    for c in CUSTOMERS + SUCCESSOR_CUSTOMERS:
        as_of_iso = c.get("acquisition_date")
        if not c.get("customer_id") or not as_of_iso:
            continue
        commodity = c.get("commodity", "electricity")
        # The caller's own mapping, byte for byte: EAC for electricity, AQ for
        # gas, and MEDIUM band only where the registration flow carried neither.
        eac = c.get("eac_kwh") if commodity == "electricity" else c.get("aq_kwh")
        est = estimate_annual_consumption(
            as_of=date.fromisoformat(as_of_iso),
            commodity=commodity,
            registry_eac_kwh=float(eac) if eac else None,
            band="MEDIUM" if not eac else None,
        )
        seen[est.basis] = seen.get(est.basis, 0) + 1

    established = {b: n for b, n in seen.items() if b is not ConsumptionBasis.UNAVAILABLE}
    assert set(established) <= set(BASIS_ORDER), (
        f"the live route produced {set(established) - set(BASIS_ORDER)}, which "
        "BASIS_ORDER does not declare"
    )
    assert set(established) == set(BASIS_ORDER), (
        f"BASIS_ORDER declares {set(BASIS_ORDER) - set(established)} and no "
        f"account on the live book reaches it. Counts walked: "
        f"{ {b.value: n for b, n in seen.items()} }"
    )
