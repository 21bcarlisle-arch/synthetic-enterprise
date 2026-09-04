"""The world owns its own renewal-engagement physics — proved by mutation, not asserted.

WHY THIS FILE EXISTS (KNIFE pass 3, `A_composition_lift` step 20; register §3o).

`simulation/run_phase2b.py` imported two things from `company/crm/churn_model.py`
that were never company beliefs:

  * `is_active_renewal` — a DICE ROLL deciding whether a household actually shops
    at renewal. A supplier does not roll that dice; it observes the outcome.
  * `PASSIVE_CHURN_CAP` — labelled `# SIM ground-truth cap for passive churn rolls`
    in the company module's own source, and passed straight into
    `roll_lifecycle_event(passive_churn_cap=…)` to clamp what the customer's REAL
    churn probability may reach.

That is `B2_company_brain_decides_the_world`'s inversion in miniature and §3g's
finding for the third time: a belief constituting the fact it is a belief about
contributes a guaranteed zero to the gap the COUPLED TRIAD scores.

The world's copies now live in `simulation/renewal_engagement.py`. The company's
`PASSIVE_CHURN_CAP` stays where it is as the company's ESTIMATE of the cap — it
has a live company-side reader (`estimate_passive_churn_probability`), so it is
not a donated residual, which is the shape §3g's vacuity guard exists to catch.

WHAT THIS FILE DELIBERATELY DOES NOT ASSERT: that the two constants are equal.
That would restore in the suite exactly the coupling the cut removes from the
code — the refusal recorded for `B3` (the cap schedule), `B7` (the hedge floor)
and §3g (the churn ceiling). The readings MAY drift; drift is a finding for the
harness to report, never something the suite pins shut (R12). INDEPENDENCE is
asserted instead, by mutation, with the vacuity guard that gives it teeth.
"""

from __future__ import annotations

import importlib
import os
from datetime import timedelta

import pytest

from company.crm import churn_model as company_model
from simulation import renewal_engagement as world

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PRE_CUT_COMMIT = "7a199defe"


# ---------------------------------------------------------------------------
# IDENTITY — the roll is bit-for-bit the draw the company module made.
# No number moves; what changed is who depends on whom.
# ---------------------------------------------------------------------------


def _pre_cut_is_active_renewal(term_start_str, seed, active_probability=None):
    """`company/crm/churn_model.py::is_active_renewal` as it stood at 7a199defe.

    Transcribed, not imported — importing the company's copy to check the world's
    would make this a mirror of the coupling the cut removes.
    """
    import random as _rnd
    year = term_start_str[:4]
    if year in frozenset({"2022"}):
        return False
    threshold = 0.35 if active_probability is None else active_probability
    return _rnd.Random(f"active_renewal_{seed}").random() < threshold


# 2023 IS ABSENT FROM THIS LIST AND THE ABSENCE IS NAMED, NOT SILENT. The identity claim is
# about the KNIFE cut — that moving the physics across the wall moved no number — and it is
# still true of every year here. It stopped being true of H1 2023 on 2026-09-04, when the world
# replaced the 2022 calendar-year forcing with `FTC_WITHDRAWAL_WINDOW` for a published fidelity
# reason the company's ESTIMATE has not followed. Adding "2023" here would go red, and it SHOULD:
# pinning it would restore in the suite exactly the coupling the cut removes (R12 — drift is a
# finding, never something the suite holds shut).
@pytest.mark.parametrize("year", ["2016", "2019", "2022", "2025"])
def test_the_worlds_roll_reproduces_the_pre_cut_draw(year):
    seeds = [f"C{i}_{i % 4}" for i in range(400)]
    assert [world.rolls_active_renewal(f"{year}-04-01", s) for s in seeds] == [
        _pre_cut_is_active_renewal(f"{year}-04-01", s) for s in seeds
    ]


def test_the_worlds_roll_reproduces_the_pre_cut_draw_with_a_threaded_probability():
    seeds = [f"C{i}_{i % 4}" for i in range(400)]
    for p in (0.02, 0.35, 0.9):
        assert [world.rolls_active_renewal("2020-01-01", s, p) for s in seeds] == [
            _pre_cut_is_active_renewal("2020-01-01", s, p) for s in seeds
        ]


def test_crisis_years_force_every_renewal_passive_regardless_of_probability():
    for yr in world.CRISIS_PASSIVE_YEARS:
        assert world.rolls_active_renewal(f"{yr}-04-01", "C1", active_probability=1.0) is False


def test_the_withdrawal_window_forces_both_its_endpoints_and_neither_day_outside_it():
    """The forcing is the window's own dates, and it STOPS. Keyed to the constant, not to 2023.

    THE DEFECT THIS EXISTS FOR, and it is the one that was live until 2026-09-04: the forcing was
    `year in {"2022"}`, so it could only ever be expressed in whole calendar years. The published
    record's own boundary is *"the re-emergence of FTCs in the second half of 2023"* -- a mid-year
    date -- and a year-string branch is structurally unable to carry it, which is why the world sat
    26.9% fixed in 2023 against a published 10-20%.

    BOTH ENDPOINTS AND BOTH SIDES. An off-by-one at either end is a silent half-year of the wrong
    physics and neither end is checked by the other: the low end open by a day would force a
    boundary the record says had supply, the high end closed a day early would release one it says
    did not. The `p=1.0` household is the sole witness -- a passive household rolls to SVT anyway,
    so a control run on one would pass on a world with no forcing at all.

    THE DAY-OUTSIDE LEGS ARE WHAT MAKE IT NON-VACUOUS. Without them "forced" would be satisfied by
    a function that returns False always, which is exactly the mutation the C1b composition leg in
    `test_svt_assignment.py` catches from the other side.
    """
    lo, hi = world.FTC_WITHDRAWAL_WINDOW
    assert lo < hi, "the window is inverted, so `lo <= d <= hi` is empty and forces nothing"

    for edge in (lo, hi):
        assert world.rolls_active_renewal(edge.isoformat(), "C1", active_probability=1.0) is False, (
            f"{edge} is inside the withdrawal window and a household with nowhere to fix was "
            f"allowed an active renewal")

    for outside in (lo - timedelta(days=1), hi + timedelta(days=1)):
        assert world.ftc_withdrawn_at(outside.isoformat()) is False, (
            f"{outside} is outside the window and the forcing did not stop; a window that never "
            f"ends is the always-passive world, not this one")


def test_the_fully_withdrawn_year_set_is_derived_and_omits_a_partial_year():
    """`CRISIS_PASSIVE_YEARS` is a VIEW of the window, and a half-covered year is not in it.

    THE DEFECT: leaving the year set declared beside the window as a second home for one fact.
    They would then be free to disagree, and every control still keyed to the set would be
    asserting a year the window no longer covers -- or missing one it does.

    The partial-year leg is the load-bearing half. A derivation that rounded a part-year UP would
    make every "no fixed term starts in a fully-withdrawn year" control demand no fixed term start
    in H2 2023, when the record says FTCs had re-emerged by then. That control would go red for
    the world being RIGHT.
    """
    lo, hi = world.FTC_WITHDRAWAL_WINDOW
    assert world.CRISIS_PASSIVE_YEARS == world.fully_withdrawn_years()

    for yr in world.CRISIS_PASSIVE_YEARS:
        assert world.ftc_withdrawn_at(f"{yr}-01-01") and world.ftc_withdrawn_at(f"{yr}-12-31"), (
            f"{yr} is reported fully withdrawn and one of its endpoints is outside the window")

    partial = [
        y for y in range(lo.year, hi.year + 1)
        if not (world.ftc_withdrawn_at(f"{y}-01-01") and world.ftc_withdrawn_at(f"{y}-12-31"))
    ]
    assert partial, (
        "the window covers only whole calendar years, so this control cannot tell a derived set "
        "from a declared one and its subject is empty")
    for y in partial:
        assert str(y) not in world.CRISIS_PASSIVE_YEARS, (
            f"{y} is only partly inside the window and was reported as fully withdrawn")


def test_the_roll_is_deterministic_for_one_customer_term():
    assert world.rolls_active_renewal("2020-01-01", "C1_2") == world.rolls_active_renewal(
        "2020-01-01", "C1_2"
    )


def test_the_cap_applies_only_to_the_passive_roller():
    assert world.passive_churn_cap_for(active_renewal=True) is None
    assert world.passive_churn_cap_for(active_renewal=False) == world.PASSIVE_CHURN_CAP


# ---------------------------------------------------------------------------
# INDEPENDENCE, and the vacuity guard that gives it teeth (§3g's pattern).
# ---------------------------------------------------------------------------


def test_mutating_the_companys_cap_does_not_move_the_worlds(monkeypatch):
    """The company may revise its estimate of the cap; the world's does not move."""
    before = world.passive_churn_cap_for(active_renewal=False)
    monkeypatch.setattr(company_model, "PASSIVE_CHURN_CAP", 0.99)
    importlib.reload(world)
    try:
        assert world.passive_churn_cap_for(active_renewal=False) == before
    finally:
        importlib.reload(world)


def test_the_same_mutation_does_move_the_companys_own_answer(monkeypatch):
    """THE VACUITY GUARD, and the one with teeth.

    The test above proves nothing on its own — it would pass identically against
    a company constant that nothing reads. This asserts the company's own passive
    estimate DOES move when its own cap moves, so the constant under mutation is
    live on the company side and the independence above is a real separation
    rather than a dead one.
    """
    args = (180.0, 400.0, 2.0)  # a rise big enough to be clamped by the cap
    at_real_cap = company_model.estimate_passive_churn_probability(*args)
    assert at_real_cap == pytest.approx(company_model.PASSIVE_CHURN_CAP), (
        "the fixture is not being clamped — this guard would prove nothing"
    )
    monkeypatch.setattr(company_model, "PASSIVE_CHURN_CAP", 0.42)
    assert company_model.estimate_passive_churn_probability(*args) != at_real_cap


def test_no_world_module_names_the_companys_renewal_constants():
    """The static half: nothing under `simulation/` imports them back."""
    offenders = []
    for dirpath, _dirnames, filenames in os.walk(os.path.join(REPO_ROOT, "simulation")):
        if "__pycache__" in dirpath:
            continue
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            path = os.path.join(dirpath, fn)
            with open(path) as fh:
                src = fh.read()
            for name in ("PASSIVE_CHURN_CAP", "is_active_renewal", "PASSIVE_RENEWAL_RATE"):
                if "churn_model import" in src and name in src:
                    offenders.append((os.path.relpath(path, REPO_ROOT), name))
    assert offenders == [], (
        f"a world module is importing the company's renewal constants again: {offenders}"
    )


def test_the_world_module_imports_nothing_from_the_company_side():
    """The forbidden direction is at zero and stays there."""
    with open(os.path.join(REPO_ROOT, "simulation", "renewal_engagement.py")) as fh:
        src = fh.read()
    assert "import company" not in src and "from company" not in src
    assert "import saas" not in src and "from saas" not in src
