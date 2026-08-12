"""The churn-estimation seam's contract — and the ways this cut could rot silently.

WHY THIS FILE EXISTS (R15: a control must be able to FAIL on its own named defect)
---------------------------------------------------------------------------------
KNIFE pass 3, `A_composition_lift` step 20, moved the supplier's churn belief out
of `simulation/run_phase2b.py::main()` into `company/crm/churn_desk.py` behind
`company/interfaces/churn_estimation.py` — three wall crossings
(`company.crm.churn_model`, `company.crm.enriched_churn_estimate`,
`company.analytics.churn_accuracy_report`).

The epistemic-wall ratchet polices the STATIC half: a module-scope
`company.crm.churn_desk -> simulation.*` import is a new class-(a) edge, the
forbidden direction, and reds the suite. Four things it cannot see:

1. **A lazy import.** The ratchet covers static imports only; an in-function
   `import simulation.…` escapes it. The convenience change is real and near at
   hand here: the world now owns `PASSIVE_CHURN_CAP` and
   `rolls_active_renewal` in `simulation/renewal_engagement.py`, one import
   away, and a desk that wanted "the cap" could reach for the world's rather
   than its own. Control 1 is BEHAVIOURAL — it builds a real estimate in a clean
   interpreter and asks which modules the import system actually loaded. Its
   mutation performs the defect on a COPY of the real source and re-runs the
   same detector, so the control is tried rather than trusted (and no repo file
   is edited mid-run, which would corrupt `inspect.getsource` for every other
   test in the session).

2. **A silently reordered, dropped or re-rounded estimate.** The claim this cut
   rests on is that the desk computes what the inlined code computed. Nothing
   static sees a `round()` move to 3dp, a dropped `hedge_fraction=` or a
   `renewal_year` that stopped being threaded — and the effect is not a crash,
   it is a different churn probability on every renewal in the run and a
   different recall figure on the company's own calibration report. Control 2
   replicates the PRE-CUT inlined sequence, transcribed from
   `simulation/run_phase2b.py` as it stood at `7a199defe` (not from the module
   under test, which would be a mirror), and asserts every arm is identical.

3. **THE BRANCH BECOMING A FIELD.** Before the cut, active-versus-passive was a
   BRANCH at the point of use — `if not active_renewal and segment != "I&C"` —
   so the caller could not accidentally estimate a passive roller as an active
   shopper without deleting a visible `if`. Now it is one boolean field on a
   dataclass. A caller that hardcodes `active_renewal=True`, or drops the field
   and takes the default, silently switches 65% of resi renewals onto the wrong
   estimator, and EVERY test in this file that exercises the desk directly would
   stay green because the desk would be given exactly what the caller chose to
   give it. Control 3 is an AST check over the real call site in
   `run_phase2b.py`, with a vacuity guard (a source with no such call would make
   it pass for free) and mutations that perform the defect.

4. **THE TWO ESTIMATORS COLLAPSING INTO ONE.** The pre-cut shape held two
   genuinely different formulas, and folding them behind one door invites the
   simplification `enriched_churn_estimate` for everybody — nothing crashes,
   every arithmetic test on either estimator stays green, and the only symptom
   is that passive rollers stop being inert. Control 4 asserts the door's two
   arms actually diverge on a fixture where they must, and its mutation collapses
   the branch to prove the assertion is not vacuous.

Each `test_mutation_*` performs the named defect rather than asserting it is
impossible.

VACUITY, stated once for the whole file. The fixture is one resi account renewing
on a >20% rate rise with a real bill-shock count and a POOR payment score — a
renewal where the active and passive estimators are REQUIRED to disagree, and
where the payment signal is non-baseline so a dropped keyword changes the answer.
`test_the_fixture_separates_the_two_estimators` asserts that separation directly,
so no control in this file can pass because the fixture is degenerate.
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

from company.analytics.churn_accuracy_report import compute_churn_model_performance
from company.crm import churn_desk as impl
from company.crm.churn_model import (
    CRISIS_HANGOVER_WINDOW_PERIODS,
    estimate_churn_probability,
)
from company.crm.enriched_churn_estimate import (
    INDUSTRY_BASE_CHURN_RATE,
    enriched_churn_estimate,
    enriched_passive_churn_estimate,
)
from company.crm.payment_behaviour_analytics import BehaviourScore
from company.interfaces import churn_estimation as door

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RUN_MODULE_PATH = os.path.join(REPO_ROOT, "simulation", "run_phase2b.py")
IMPL_PATH = os.path.join(REPO_ROOT, "company", "crm", "churn_desk.py")

# The pre-cut commit control 2 transcribes from. Named, and its existence checked,
# because a transcription from a commit that does not contain the block is a
# mirror wearing a citation.
PRE_CUT_COMMIT = "7a199defe"

# One renewal, chosen so the two estimators must disagree — see the vacuity note.
_OLD_RATE = 180.0
_NEW_RATE = 240.0          # +33%, well past the bill-shock threshold
_TENURE = 3.5
_EAC_KWH = 3800.0
_SHOCKS = 2
_SATISFACTION = 41.0
_HEDGE_FRACTION = 0.62
_HANGOVER = 1
_YEAR = 2019


def _observation(**overrides):
    base = dict(
        old_rate_gbp_per_mwh=_OLD_RATE,
        new_rate_gbp_per_mwh=_NEW_RATE,
        tenure_years=_TENURE,
        annual_consumption_kwh=_EAC_KWH,
        bill_shock_count=_SHOCKS,
        behaviour_score=BehaviourScore.POOR,
        satisfaction_score=_SATISFACTION,
        hedge_fraction=_HEDGE_FRACTION,
        hangover_periods_remaining=_HANGOVER,
        segment="resi",
        renewal_year=_YEAR,
        active_renewal=True,
    )
    base.update(overrides)
    return door.RenewalObservation(**base)


# ---------------------------------------------------------------------------
# VACUITY — the fixture must be able to tell the two arms apart.
# ---------------------------------------------------------------------------


def test_the_fixture_separates_the_two_estimators():
    active = door.estimate_renewal_churn(_observation(active_renewal=True))
    passive = door.estimate_renewal_churn(_observation(active_renewal=False))
    assert active != passive, (
        "the fixture cannot distinguish an active shopper from a passive roller — "
        "every control in this file would pass for free"
    )
    assert active > 0.0 and passive > 0.0


def test_the_pre_cut_commit_exists_and_contains_the_block_control_2_transcribes():
    """A citation to a commit that lacks the block is not evidence."""
    proc = subprocess.run(
        ["git", "show", f"{PRE_CUT_COMMIT}:simulation/run_phase2b.py"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, (
        f"pre-cut commit {PRE_CUT_COMMIT} is unreachable — an unavailable check "
        f"is a FAILED check:\n{proc.stderr}"
    )
    src = proc.stdout
    for fragment in (
        "_enriched_passive_churn_estimate(",
        "_enriched_churn_estimate(",
        "_INDUSTRY_BASE_CHURN_RATE",
        "estimate_churn_probability as _est_churn",
        "CRISIS_HANGOVER_WINDOW_PERIODS",
    ):
        assert fragment in src, (
            f"{PRE_CUT_COMMIT} does not contain {fragment!r} — control 2 is "
            f"transcribing from the wrong commit"
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
    from company.crm.payment_behaviour_analytics import BehaviourScore

    obs = m.RenewalObservation(
        old_rate_gbp_per_mwh=180.0,
        new_rate_gbp_per_mwh=240.0,
        tenure_years=3.5,
        annual_consumption_kwh=3800.0,
        bill_shock_count=2,
        behaviour_score=BehaviourScore.POOR,
        satisfaction_score=41.0,
        hedge_fraction=0.62,
        hangover_periods_remaining=1,
        segment="resi",
        renewal_year=2019,
        active_renewal=False,
    )
    m.estimate_renewal_churn(obs)
    m.estimate_renewal_churn(m.RenewalObservation(
        old_rate_gbp_per_mwh=180.0, new_rate_gbp_per_mwh=240.0, tenure_years=3.5,
        active_renewal=True,
    ))
    m.estimate_secondary_fuel_churn(50.0, 62.0, 2.0)
    m.estimate_churn_without_rate_history()
    m.crisis_hangover_periods()
    m.score_churn_estimates([], [], [])

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
        modname = "_knife3_step20_subject"
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


def test_estimating_churn_loads_no_world_module():
    with open(IMPL_PATH) as fh:
        real_source = fh.read()
    assert _walled_modules_loaded_by(real_source) == []


def test_mutation_a_lazy_world_import_is_caught_by_the_same_detector():
    """Perform the defect on a copy of the real source, same detector."""
    with open(IMPL_PATH) as fh:
        mutated = fh.read()
    anchor = "def crisis_hangover_periods() -> int:"
    assert anchor in mutated, "anchor moved — this mutation is no longer the defect"
    mutated = mutated.replace(
        anchor,
        anchor + "\n    from simulation.renewal_engagement import PASSIVE_CHURN_CAP  # noqa: F401  <-- the defect",
        1,
    )
    loaded = _walled_modules_loaded_by(mutated)
    assert "simulation.renewal_engagement" in loaded, (
        "control 1 did not fire on a lazy world import — it cannot fail, so it "
        "is not evidence"
    )


# ---------------------------------------------------------------------------
# CONTROL 2 — identity against the PRE-CUT sequence, transcribed from 7a199defe.
# Not read from the module under test; that would be a mirror.
# ---------------------------------------------------------------------------


def _pre_cut_estimate(active_renewal: bool, segment: str) -> float:
    """The inlined block exactly as `run_phase2b.py` held it at 7a199defe."""
    if not active_renewal and segment != "I&C":
        return round(enriched_passive_churn_estimate(
            _OLD_RATE, _NEW_RATE, _TENURE,
            bill_shock_count=_SHOCKS,
            behaviour_score=BehaviourScore.POOR,
            satisfaction_score=_SATISFACTION,
            renewal_year=_YEAR,
        ), 4)
    return round(enriched_churn_estimate(
        _OLD_RATE, _NEW_RATE, _TENURE,
        _EAC_KWH,
        bill_shock_count=_SHOCKS,
        behaviour_score=BehaviourScore.POOR,
        satisfaction_score=_SATISFACTION,
        hedge_fraction=_HEDGE_FRACTION,
        hangover_periods_remaining=_HANGOVER,
        segment=segment,
        renewal_year=_YEAR,
    ), 4)


@pytest.mark.parametrize(
    "active_renewal,segment",
    [(True, "resi"), (False, "resi"), (True, "I&C"), (False, "I&C")],
)
def test_the_door_reproduces_the_pre_cut_estimate(active_renewal, segment):
    assert door.estimate_renewal_churn(
        _observation(active_renewal=active_renewal, segment=segment)
    ) == _pre_cut_estimate(active_renewal, segment)


def test_the_door_reproduces_the_pre_cut_gas_monitoring_estimate():
    """`round(_est_churn(old, new, tenure, fuel="gas"), 4)` at 7a199defe."""
    assert door.estimate_secondary_fuel_churn(50.0, 62.0, 2.0) == round(
        estimate_churn_probability(50.0, 62.0, 2.0, fuel="gas"), 4
    )


def test_the_door_reproduces_the_pre_cut_no_history_fallback():
    assert door.estimate_churn_without_rate_history() == INDUSTRY_BASE_CHURN_RATE


def test_the_door_reproduces_the_pre_cut_hangover_window():
    assert door.crisis_hangover_periods() == CRISIS_HANGOVER_WINDOW_PERIODS


def test_the_door_reproduces_the_pre_cut_calibration_report():
    events = [
        {"customer_id": "C1", "event_date": "2019-04-01", "event_type": "churned",
         "company_churn_estimate": 0.62},
        {"customer_id": "C2", "event_date": "2019-04-01", "event_type": "renewed",
         "company_churn_estimate": 0.11},
        {"customer_id": "C3", "event_date": "2020-04-01", "event_type": "churned",
         "company_churn_estimate": 0.08},
    ]
    assert door.score_churn_estimates(events, [], []) == compute_churn_model_performance(
        events, [], []
    )


@pytest.mark.parametrize(
    "active_renewal,dropped",
    [
        # Rate-sensitivity inputs — live on the ACTIVE arm.
        (True, {"hedge_fraction": 0.0}),
        (True, {"hangover_periods_remaining": 0}),
        (True, {"renewal_year": None}),
        # Payment/experience inputs — live on the PASSIVE arm. See the note below
        # for why they are NOT checked on the active arm.
        (False, {"bill_shock_count": 0}),
        (False, {"behaviour_score": None}),
        (False, {"satisfaction_score": None}),
    ],
)
def test_mutation_a_dropped_keyword_moves_the_answer(active_renewal, dropped):
    """Control 2's teeth: the fixture is sensitive to the arguments it threads.

    Without this, control 2 would pass identically against a desk that silently
    ignored `hedge_fraction`, `renewal_year` or the payment signal — the
    'donated residual is not a control' shape.

    WHY THE ARM IS PART OF THE CASE, and it is a property of the company's model
    rather than of this fixture. Both estimators combine as
    `max(rate_estimate, payment_estimate)`. On the ACTIVE arm at a +33% rise the
    rate estimate dominates, so bill shocks, behaviour score and satisfaction
    move nothing — the payment signal is MASKED, exactly as `max` implies. It is
    the PASSIVE arm, whose rate sensitivity is deliberately near-inert, where
    those three are load-bearing, which is the whole reason Phase QK extended the
    enriched estimate to passive rollers. Checking each input on the arm where it
    is live is therefore the honest control; checking all six on one arm would
    have forced a fixture chosen to make the assertion pass rather than to test
    the seam.
    """
    full = door.estimate_renewal_churn(_observation(active_renewal=active_renewal))
    assert door.estimate_renewal_churn(
        _observation(active_renewal=active_renewal, **dropped)
    ) != full, (
        f"the estimate is insensitive to {list(dropped)[0]} on the "
        f"{'active' if active_renewal else 'passive'} arm — control 2 cannot "
        f"detect that keyword being dropped in the desk"
    )


# ---------------------------------------------------------------------------
# CONTROL 3 — the branch became a field. AST over the REAL call site.
# ---------------------------------------------------------------------------

_REQUIRED_CALLSITE_KEYWORDS = {
    # keyword on RenewalObservation -> the world variable that must reach it
    "old_rate_gbp_per_mwh": "old_elec_rate",
    "new_rate_gbp_per_mwh": "unit_rate",
    "tenure_years": "tenure_for_est",
    "annual_consumption_kwh": "company_eac",
    "segment": "segment_for_churn",
    "active_renewal": "active_renewal",
}


def _observation_callsites(source: str) -> list[ast.Call]:
    tree = ast.parse(source)
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "RenewalObservation"
    ]


def _callsite_keyword_names(call: ast.Call) -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    for kw in call.keywords:
        if kw.arg is None:
            continue
        out[kw.arg] = kw.value.id if isinstance(kw.value, ast.Name) else None
    return out


def test_the_world_builds_the_observation_from_its_own_named_variables():
    with open(RUN_MODULE_PATH) as fh:
        calls = _observation_callsites(fh.read())
    # VACUITY GUARD — a source with no such call would make every assertion
    # below pass over an empty loop.
    assert len(calls) == 1, (
        f"expected exactly one RenewalObservation construction in run_phase2b.py, "
        f"found {len(calls)} — control 3 is examining the wrong thing"
    )
    names = _callsite_keyword_names(calls[0])
    assert not calls[0].args, "the observation must be built by keyword, never positionally"
    for kw, expected in _REQUIRED_CALLSITE_KEYWORDS.items():
        assert names.get(kw) == expected, (
            f"{kw}= is fed by {names.get(kw)!r}, expected {expected!r} — the "
            f"world is threading the wrong value through the seam"
        )


def test_mutation_the_hardcoded_active_flag_is_caught():
    """The defect: `active_renewal=True` instead of the world's own outcome.

    65% of resi renewals silently switch estimator and nothing else changes.
    """
    with open(RUN_MODULE_PATH) as fh:
        mutated = fh.read().replace(
            "active_renewal=active_renewal,", "active_renewal=True,", 1
        )
    calls = _observation_callsites(mutated)
    assert len(calls) == 1
    names = _callsite_keyword_names(calls[0])
    assert names.get("active_renewal") != "active_renewal", (
        "the mutation did not take — this control is not testing what it claims"
    )


def test_mutation_the_swapped_rates_are_caught():
    """The defect: old and new rate crossing the seam the wrong way round."""
    with open(RUN_MODULE_PATH) as fh:
        mutated = (
            fh.read()
            .replace("old_rate_gbp_per_mwh=old_elec_rate,", "old_rate_gbp_per_mwh=__SWAP__,", 1)
            .replace("new_rate_gbp_per_mwh=unit_rate,", "new_rate_gbp_per_mwh=old_elec_rate,", 1)
            .replace("old_rate_gbp_per_mwh=__SWAP__,", "old_rate_gbp_per_mwh=unit_rate,", 1)
        )
    calls = _observation_callsites(mutated)
    assert len(calls) == 1
    names = _callsite_keyword_names(calls[0])
    assert names["old_rate_gbp_per_mwh"] == "unit_rate"
    assert names["new_rate_gbp_per_mwh"] == "old_elec_rate"
    # and the swap genuinely changes the company's answer, so it is worth catching
    assert door.estimate_renewal_churn(
        _observation(old_rate_gbp_per_mwh=_NEW_RATE, new_rate_gbp_per_mwh=_OLD_RATE)
    ) != door.estimate_renewal_churn(_observation())


def test_the_world_no_longer_branches_on_which_estimator_applies():
    """The lift is only real if the world stopped knowing there are two."""
    with open(RUN_MODULE_PATH) as fh:
        src = fh.read()
    for leaked in (
        "enriched_passive_churn_estimate",
        "enriched_churn_estimate",
        "INDUSTRY_BASE_CHURN_RATE",
        "compute_churn_model_performance",
        "CRISIS_HANGOVER_WINDOW_PERIODS",
    ):
        assert leaked not in src, (
            f"run_phase2b.py still names {leaked!r} — the door is a re-export, "
            f"not a cut"
        )


# ---------------------------------------------------------------------------
# CONTROL 4 — the two estimators must not collapse into one.
# ---------------------------------------------------------------------------


def test_the_passive_arm_is_genuinely_inert_relative_to_the_active_arm():
    """A passive SVT roller facing a 33% rise churns LESS than an active shopper.

    That inertia is the whole point of there being two formulas. If the desk ever
    routes everybody through `enriched_churn_estimate`, this is the assertion that
    reds — nothing else would.
    """
    active = door.estimate_renewal_churn(_observation(active_renewal=True))
    passive = door.estimate_renewal_churn(_observation(active_renewal=False))
    assert passive < active


def test_the_ic_segment_never_takes_the_passive_arm():
    """Brokers shop every renewal — an I&C account has no passive roll."""
    assert door.estimate_renewal_churn(
        _observation(active_renewal=False, segment="I&C")
    ) == door.estimate_renewal_churn(
        _observation(active_renewal=True, segment="I&C")
    )


def test_mutation_collapsing_the_branch_is_caught_by_control_4():
    """Perform the collapse on the real desk's logic and re-run control 4's assertion.

    Re-implemented rather than monkeypatched: the defect is 'the desk stopped
    branching', which is exactly `estimate_renewal_churn` with its `if` removed.
    """
    def _collapsed(observation):
        return round(enriched_churn_estimate(
            observation.old_rate_gbp_per_mwh,
            observation.new_rate_gbp_per_mwh,
            observation.tenure_years,
            observation.annual_consumption_kwh,
            bill_shock_count=observation.bill_shock_count,
            behaviour_score=observation.behaviour_score,
            satisfaction_score=observation.satisfaction_score,
            hedge_fraction=observation.hedge_fraction,
            hangover_periods_remaining=observation.hangover_periods_remaining,
            segment=observation.segment,
            renewal_year=observation.renewal_year,
        ), 4)

    active = _collapsed(_observation(active_renewal=True))
    passive = _collapsed(_observation(active_renewal=False))
    assert not (passive < active), (
        "control 4's assertion survives the branch being collapsed — it cannot "
        "fail on its own named defect, so it is not evidence"
    )


# ---------------------------------------------------------------------------
# The door is the door — every public name resolves to the desk.
# ---------------------------------------------------------------------------


def test_the_door_exports_exactly_the_desk():
    for name in door.__all__:
        assert getattr(door, name) is getattr(impl, name)
    assert sorted(door.__all__) == sorted(impl.__all__)
