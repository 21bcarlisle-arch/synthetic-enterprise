"""CLASS GUARD (R10) -- a coupled pair whose TRUTH requires the subject to have
ENDED is grading a population selected on the quantity it predicts.

Sibling of `tests/test_gap_metric_misapplication_class.py`, and the same argument:
the defect belongs to the SHAPE, not to the instance where it was found, so it may
not be closed at that instance.

WHAT WAS FOUND (2026-08-26,
`docs/staging/done/WORKER_FINDING_THE_CLV_GAP_IS_GRADED_ONLY_ON_THE_CUSTOMERS_WHO_LEFT_2026-08-26.md`).
`EP1_clv_three_horizon` grades a forward CLV against realised lifetime margin. A
realised LIFETIME is only knowable once the customer has gone, so the graded
population is exactly the accounts that left -- 2.96x below the still-supplied book
like-for-like -- while the no-skill divisor is the mean of that same selected set. A
calibrated estimator scores as a uniform five-fold over-estimate there, and the
published `best_single_scale 0.204` was read as an estimator fault for a whole
stretch of work before anyone asked what the population was.

THE SIGNATURE, stated so a future author can check their own pair against it: the
truth side cannot be observed until the subject TERMINATES. Lifetime value, total
tenure at churn, whole-relationship margin. Contrast the pairs that are fine and why:

  * `couple_supply_start` predicts tenure-TO-DATE, observable on a live account, so
    nothing is excluded for being unfinished.
  * `couple_value_based_pricing` grades a departure PROBABILITY against the world's
    counterfactual probability -- no realised outcome enters, so no outcome selects.
  * `couple_pb3_book_growth` excludes on `is_machine_bound`, a property of the
    BELIEF, and normalises against a per-row naive predictor rather than a fitted
    population mean. Both halves of the defect are absent by construction.

So the register below currently holds ONE entry, and that is the finding rather than
a reason to skip the guard: this test exists so the SECOND one cannot land silently.

WHAT THIS GUARD COMPELS, AND WHAT IT DOES NOT. It compels the LOOK and the ROW --
the same rule `tools/write_time_gate.py` operates under, for the same reason. It
never rules on whether a pair SHOULD grade a terminated population; usually there is
no alternative, and censoring the truth is not a defect. Publishing the ratio without
saying what the selection does to it is.

DIRECTIONS THE RATCHET HOLDS (all three, or it is theatre):
  * a NEW coupler that censors and publishes no selection row  -> FAILS
  * a register entry that has STOPPED censoring                -> FAILS (stale)
  * a register entry whose row is CODED but not PUBLISHED      -> FAILS (R11)
"""
from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
COUPLERS = sorted(REPO_ROOT.glob("tools/couple_*.py"))
LEDGER = REPO_ROOT / "docs/observability/coupled_gap_ledger.json"

#: The vocabulary that marks a pair whose truth needs the subject to have ended.
#: Deliberately broad and answerable: a coupler that merely DISCUSSES censoring is
#: caught, and the answer is to publish the row, not to reword the docstring.
CENSORING_MARKERS = ("censor", "right-censored", "lifetime completed")

#: The component key every censoring coupler must publish.
SELECTION_COMPONENT = "population_selection"

#: Couplers known to grade a population selected on termination. One entry is not
#: an argument against the guard -- see the module docstring.
COUPLERS_GRADING_A_TERMINATED_POPULATION = {
    "couple_clv": "EP1_clv_three_horizon",
}


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _censors(path: Path) -> bool:
    lowered = _source(path).lower()
    return any(marker in lowered for marker in CENSORING_MARKERS)


def _ledger() -> dict:
    if not LEDGER.exists():
        pytest.skip("no coupled gap ledger on this tree")
    return json.loads(LEDGER.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# the three directions
# ---------------------------------------------------------------------------

def test_a_new_censoring_coupler_cannot_land_unregistered():
    """DIRECTION 1. The whole point: the second instance must not arrive quietly."""
    censoring = {path.stem for path in COUPLERS if _censors(path)}
    unregistered = censoring - set(COUPLERS_GRADING_A_TERMINATED_POPULATION)
    assert not unregistered, (
        f"{sorted(unregistered)} grade a population that can only be observed once "
        "the subject has ENDED. Register them above and publish a "
        f"`{SELECTION_COMPONENT}` component saying what that selection does to the "
        "ratio -- see the module docstring for what reading one without the other "
        "cost on 2026-08-26."
    )


def test_a_register_entry_that_has_stopped_censoring_is_struck_off():
    """DIRECTION 2. A stale register is a register nobody trusts, and an entry that
    no longer describes its module makes every other entry unreadable."""
    stems = {path.stem: path for path in COUPLERS}
    for name in sorted(COUPLERS_GRADING_A_TERMINATED_POPULATION):
        assert name in stems, f"{name} is registered but no longer exists"
        assert _censors(stems[name]), (
            f"{name} no longer grades a terminated population -- strike it off the "
            "register rather than leaving an entry that has stopped being true."
        )


def test_every_registered_coupler_publishes_the_selection_component_in_its_source():
    """DIRECTION 3a, the code. Cheap, and catches a deletion at review time."""
    stems = {path.stem: path for path in COUPLERS}
    for name in sorted(COUPLERS_GRADING_A_TERMINATED_POPULATION):
        assert SELECTION_COMPONENT in _source(stems[name]), (
            f"{name} censors its truth and never publishes `{SELECTION_COMPONENT}`"
        )


def test_every_registered_coupler_publishes_the_row_into_the_live_ledger():
    """DIRECTION 3b, the artefact (R11 -- verify to the rendered value).

    Coded is not published. This reads the ledger a consumer actually consults,
    because a component built in `measure()` and dropped before `write_gap_entry`
    would satisfy the source check above and leave every reader with the one-sided
    story anyway.
    """
    ledger = _ledger()
    for name, key in sorted(COUPLERS_GRADING_A_TERMINATED_POPULATION.items()):
        entry = ledger.get(key)
        if entry is None:
            pytest.skip(f"{key} not measured on this tree yet")
        components = entry.get("components") or {}
        assert SELECTION_COMPONENT in components, (
            f"{key} is published without `{SELECTION_COMPONENT}`: the ratio is "
            "readable and what the population does to it is not"
        )
        row = components[SELECTION_COMPONENT]
        assert row.get("available") is True, (
            f"{key} publishes `{SELECTION_COMPONENT}` as unavailable "
            f"({row.get('reason')}) -- a named blank is better than silence, but a "
            "reader still has only the one side. THE REMEDY IS TO RE-MEASURE, not "
            "to weaken this assertion: `python3 -m tools.couple_clv --write-ledger` "
            "against a run output that carries `per_customer_lifetime`. This row "
            "derives from a field every run publishes, so a blank one means the "
            "artefact regressed, and a published gap whose selection is unstated is "
            "exactly the defect this guard exists for."
        )


# ---------------------------------------------------------------------------
# R15 -- the classifier itself must be able to be wrong in both directions
# ---------------------------------------------------------------------------

def test_the_classifier_fires_on_a_censoring_module(tmp_path):
    module = tmp_path / "couple_fake.py"
    module.write_text(
        '"""Excludes every live subject as RIGHT-CENSORED."""\n', encoding="utf-8")
    assert _censors(module) is True


def test_the_classifier_stays_quiet_on_a_module_that_does_not_censor(tmp_path):
    """The partner. A classifier that returns True for everything registers the
    whole family and stops meaning anything."""
    module = tmp_path / "couple_fake.py"
    module.write_text(
        '"""Grades a probability against the world\'s counterfactual."""\n',
        encoding="utf-8")
    assert _censors(module) is False


def test_the_classifier_is_actually_discriminating_on_the_real_family():
    """Measured, not asserted: if this scan classified every coupler the same way
    it would be a constant wearing a predicate's clothes."""
    verdicts = {path.stem: _censors(path) for path in COUPLERS}
    assert len(COUPLERS) >= 10, "the coupler family shrank; re-check this guard"
    assert any(verdicts.values()), "no coupler classified as censoring at all"
    assert not all(verdicts.values()), (
        "every coupler classified as censoring -- the marker list has stopped "
        "discriminating and the register would be meaningless"
    )


def test_the_register_guard_fires_on_an_unregistered_censoring_coupler(tmp_path):
    """R15 on the guard itself, not only on its classifier.

    `test_a_new_censoring_coupler_cannot_land_unregistered` passes today because
    the family happens to contain exactly one censoring module. That is what a
    guard looks like when it is working AND what it looks like when it is broken,
    so the distinguishing evidence has to be manufactured: a second censoring
    coupler that is not on the register must red it.
    """
    intruder = tmp_path / "couple_intruder.py"
    intruder.write_text(
        '"""Excludes every live account as right-censored."""\n', encoding="utf-8")
    family = COUPLERS + [intruder]

    censoring = {path.stem for path in family if _censors(path)}
    unregistered = censoring - set(COUPLERS_GRADING_A_TERMINATED_POPULATION)
    assert unregistered == {"couple_intruder"}, (
        "the register guard did not notice a new censoring coupler")


def test_the_register_guard_stays_quiet_on_a_new_non_censoring_coupler(tmp_path):
    """The partner: adding an ordinary coupler must NOT red the register, or the
    guard becomes a tax on every new pair and gets deleted."""
    innocent = tmp_path / "couple_ordinary.py"
    innocent.write_text(
        '"""Grades a forecast against a contemporaneous observation."""\n',
        encoding="utf-8")
    family = COUPLERS + [innocent]

    censoring = {path.stem for path in family if _censors(path)}
    assert censoring - set(COUPLERS_GRADING_A_TERMINATED_POPULATION) == set()


def test_the_registered_coupler_still_imports_and_exposes_its_ledger_key():
    """The register maps module -> ledger key by hand. This is the check that the
    hand-written half has not drifted from the module's own constant."""
    for name, key in sorted(COUPLERS_GRADING_A_TERMINATED_POPULATION.items()):
        module = importlib.import_module(f"tools.{name}")
        assert getattr(module, "LEDGER_KEY", None) == key, (
            f"tools.{name}.LEDGER_KEY is {getattr(module, 'LEDGER_KEY', None)!r}, "
            f"register says {key!r}"
        )
