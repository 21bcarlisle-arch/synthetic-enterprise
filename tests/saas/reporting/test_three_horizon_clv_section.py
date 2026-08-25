"""EP1 reaches a reader — the controls on the published three-horizon section.

WHAT THIS SUITE IS FOR. `three_horizon_clv` was computed on every run from the
moment the estimator was wired into the customer-value view, and read by nothing:
the object was built, serialised nowhere, and died with the run process. A
capability whose output no artefact carries is indistinguishable from one that was
never built, so the controls here are about the SEAM and the PAGE, not the
arithmetic — the arithmetic has its own suite next door.

THE FIXTURE IS THE ESTIMATOR'S OWN OUTPUT, NEVER A HAND-WRITTEN DICT. A test that
feeds the renderer a dict a human typed proves the renderer can read that human's
idea of the payload; it cannot notice the day the estimator's shape and the
renderer's expectation part company, which is precisely the failure this seam
exists to have. Every payload below comes out of `estimate_book(...)
.as_published_dict()`.
"""

from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path

from company.analytics.clv_three_horizon import (
    AccountObservables,
    Exclusion,
    Horizon,
    RenewalPoint,
    estimate_book,
)
from saas.reporting.annual_report import (
    _three_horizon_clv_section,
    extract_report_data,
    generate_annual_report,
)

REPO_ROOT = Path(__file__).resolve().parents[3]


def _account(
    account_id: str,
    *,
    still_supplied: bool,
    margin: float | None,
    segment: str = "residential",
) -> AccountObservables:
    return AccountObservables(
        account_id=account_id,
        segment=segment,
        channel="pcw",
        acquisition_year=2020,
        contract_term_years=1.0,
        renewal_history=(
            RenewalPoint(renewal_period="2021-06", churn_probability=0.20),
        ),
        annual_margin_gbp=margin,
        still_supplied=still_supplied,
    )


#: The four-cell population, two of whose cells the live book cannot supply. A
#: supplied account with NO observed margin is the cell that decides whether a
#: structural blank survives to the page or arrives there as £0.00.
BOOK = [
    _account("A_sv", still_supplied=True, margin=100.0),
    _account("A_sb", still_supplied=True, margin=None),
    _account("A_cv", still_supplied=False, margin=100.0),
    _account("G1", still_supplied=False, margin=100.0, segment="gone"),
]


def _rendered() -> str:
    payload = estimate_book(BOOK).as_published_dict()
    return _three_horizon_clv_section({"three_horizon_clv": payload})


def test_the_section_renders_the_estimators_own_payload():
    """DEFECT: the renderer and the estimator disagree about the payload shape.

    Asserted on figures the estimator produced, so a rename or a restructure at the
    seam reds this rather than silently rendering an empty section.
    """
    out = _rendered()
    assert "Customer Lifetime Value — Three Horizons (EP1)" in out
    assert "A_sv" in out and "A_sb" in out
    assert "| Account | Contract term | Tenure expected | Portfolio cohort |" in out


def test_the_published_figure_carries_the_basis_it_was_built_on():
    """DEFECT: a portfolio mean printed with no horizon and no discount rate.

    Every account carries all three horizons, so an aggregate without its basis is
    uninterpretable. The label is READ from the payload, not spelled in the
    renderer — a book aggregated on a different horizon prints a different word.
    """
    on_tenure = _three_horizon_clv_section(
        {"three_horizon_clv": estimate_book(
            BOOK, horizon=Horizon.TENURE_EXPECTED).as_published_dict()}
    )
    on_contract = _three_horizon_clv_section(
        {"three_horizon_clv": estimate_book(
            BOOK, horizon=Horizon.CONTRACT_TERM, discount_rate=0.05
        ).as_published_dict()}
    )
    assert "`tenure_expected` at a 10.0% discount rate" in on_tenure
    assert "`contract_term` at a 5.0% discount rate" in on_contract


def test_a_structural_blank_reaches_the_page_as_a_reason_never_as_zero():
    """DEFECT: the last inch prints £0.00 for 'the company cannot value this'.

    `A_sb` is supplied and carries no observed margin. The page must say WHICH
    blank it is; a reader who sees £0.00 reads 'this customer is worth nothing',
    which is a different and false claim.
    """
    out = _rendered()
    blank_row = next(line for line in out.splitlines() if line.startswith("| A_sb "))
    assert Exclusion.NO_MARGIN_OBSERVED.value in blank_row
    assert "£0.00" not in blank_row
    valued_row = next(line for line in out.splitlines() if line.startswith("| A_sv "))
    assert "£" in valued_row, "a valued account must still print a figure"


def test_an_empty_cohort_prints_no_counted_member_not_a_profitability_verdict():
    """DEFECT: `is_profitable` re-derived at the page as `mean > 0`, so a cohort
    with nobody in it publishes 'no' — 'does not exist' and 'loses money' become
    the same sentence, which is the §5 defect the estimator was built to remove."""
    out = _rendered()
    gone_row = next(line for line in out.splitlines() if line.startswith("| gone "))
    assert "no counted member" in gone_row
    assert "| 0 / 1 |" in gone_row


def test_the_absent_key_is_reported_as_absent_and_never_as_a_zero_book():
    """DEFECT: a run artefact with no `three_horizon_clv` renders an empty section,
    or worse a £0.00 portfolio, and a broken producer becomes invisible.

    The absent sentence is deliberately NOT the generic `NOT_AVAILABLE` wording:
    'this artefact predates the publisher' and 'the estimator produced nothing' are
    different facts about the company and must not share a sentence.
    """
    for data in ({}, {"three_horizon_clv": None}):
        out = _three_horizon_clv_section(data)
        assert "Three Horizons (EP1)" in out
        assert "Not published by this run" in out
        assert "£" not in out


def test_the_section_is_actually_wired_into_the_generated_report():
    """DEFECT: the section exists and nothing calls it — this atom's own history.

    Checked on the AST of `generate_annual_report`, not on a substring of the file:
    a call that had been commented out, or moved into a dead helper, would still
    match a `grep`.
    """
    tree = ast.parse(inspect.getsource(generate_annual_report))
    called = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "_three_horizon_clv_section" in called, (
        "the section is built and dark — nothing in generate_annual_report calls it"
    )


def test_the_run_output_key_survives_extraction_untouched():
    """DEFECT: the reporting layer re-aggregates, rounds or drops the payload.

    `extract_report_data` must forward the estimator's own dict identically. A
    layer that recomputes anything here has forked the implementation, which is how
    this one quantity ended up with six of them.
    """
    payload = estimate_book(BOOK).as_published_dict()
    run_output = {
        # The smallest run output `extract_report_data` will accept. Deliberately
        # EMPTY of settled records: this control is about the forwarding, and a
        # fixture carrying a book would let the assertion pass on a payload the
        # reporting layer had rebuilt from its own inputs.
        "phase2b": {
            "all_records": [],
            "committee_wake_ups": [],
            "hedge_evolution": {},
            "starting_treasury": 0.0,
            "final_treasury": 0.0,
            "total_gross": 0.0,
            "total_capital": 0.0,
            "administration_event": None,
        },
        "three_horizon_clv": payload,
    }
    extracted = extract_report_data(run_output)
    assert extracted["three_horizon_clv"] == payload
    assert extracted["three_horizon_clv"] is payload, "the payload was rebuilt"
    # And an artefact predating the producer forwards the ABSENCE, rather than
    # raising or inventing an empty book.
    del run_output["three_horizon_clv"]
    assert extract_report_data(run_output)["three_horizon_clv"] is None


def test_the_payload_the_run_hands_over_is_json_serialisable():
    """DEFECT: the run dies at the last step of a nine-minute pipeline because a
    dataclass or an Enum reached `json.dump`. Cheap here, expensive there."""
    payload = estimate_book(BOOK).as_published_dict()
    assert json.loads(json.dumps(payload)) == payload


PRODUCER = REPO_ROOT / "simulation" / "run_phase4c_on_phase2b.py"

# EP1's published namespace in the run output. Every key the producer emits under
# this prefix is one of this atom's beliefs; the prefix is the atom's, not this
# test's invention.
_EP1_KEY_PREFIX = "three_horizon_clv"


def _ep1_keys_the_producer_publishes() -> set[str]:
    """Every `three_horizon_clv*` key in the producer's returned dict, read from
    its SOURCE by AST. Imports nothing: the question is what the run module says
    it publishes, and importing it would drag in the whole simulation stack.
    """
    tree = ast.parse(PRODUCER.read_text(encoding="utf-8"))
    return {
        node.value
        for dct in ast.walk(tree)
        if isinstance(dct, ast.Dict)
        for node in dct.keys
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and node.value.startswith(_EP1_KEY_PREFIX)
    }


def test_every_ep1_key_the_producer_publishes_survives_the_reducer():
    """DEFECT (OBSERVED 2026-08-25, and it cost a whole pass): the producer emits an
    EP1 belief key on every run, `extract_report_data` does not name it, and the key
    is dropped between the run and `run_output_latest.json` with no error anywhere.

    THIS IS DELIBERATELY NOT AN ASSERTION ABOUT ONE KEY. Closing the observed
    instance -- `three_horizon_clv_snapshots` -- with a hard-coded assertion would
    leave the CLASS open, and the class has now fired twice on this atom: the
    terminal table was wired to a reducer that carried it, the belief series was
    wired to one that did not, and nothing distinguished the two at the producer.
    R10 requires the class to fail automatically, so the expected key set is read
    from the producer's own source. A pass that adds EP1's third belief key and
    forgets this layer fails HERE, on the day it writes the key, rather than four
    runs later when a grader quietly reports `grades_atom_estimator=False`.

    WHY THE SILENCE IS THE REAL DEFECT. `run_output_latest.json` is this function's
    REDUCED output, not the raw run, so a dropped key is indistinguishable from a
    key the producer never computed -- which is exactly how `tools/couple_clv` came
    to blame `run_predates_ep1_belief_series`, a cause that would never expire.
    """
    published = _ep1_keys_the_producer_publishes()
    # The control must not pass by finding nothing to check (FAIL-OPEN).
    assert published, f"no EP1 keys found in {PRODUCER} -- the AST read is broken"
    assert _EP1_KEY_PREFIX in published, "the terminal table key is missing"

    run_output = {
        "phase2b": {
            "all_records": [],
            "committee_wake_ups": [],
            "hedge_evolution": {},
            "starting_treasury": 0.0,
            "final_treasury": 0.0,
            "total_gross": 0.0,
            "total_capital": 0.0,
            "administration_event": None,
        },
    }
    # A distinct sentinel per key, so a reducer that forwards ONE payload under two
    # names cannot pass: the assertion is per-key identity, not mere presence.
    sentinels = {key: {"sentinel": key} for key in published}
    run_output.update(sentinels)

    extracted = extract_report_data(run_output)
    dropped = sorted(key for key in published if key not in extracted)
    assert not dropped, (
        f"the producer publishes {sorted(published)} but extract_report_data drops "
        f"{dropped} -- the grader reads the REDUCED artefact, so these beliefs "
        f"never reach it"
    )
    for key in published:
        assert extracted[key] is sentinels[key], f"{key} was rebuilt, not forwarded"
