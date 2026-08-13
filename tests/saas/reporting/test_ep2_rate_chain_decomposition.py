"""EP2 sub-atom 3 — the rate chain: one decomposed span per renewal.

Discharges `WORKER_FINDING_TWO_PRICING_LOOPS_EACH_PUBLISH_THE_OTHERS_MOVE_AS_THEIR_OWN_2026-08-13`
(BLOCKING, lane B_commercial). Four writers move one `unit_rate` at renewal — the portfolio
premium, the margin recovery surcharge, the profitability uplift and the Ofgem price cap. Each
used to log a before/after pair as though it were the only writer, so three published figures
were wrong on a board surface:

1. the surcharge table's `Rate after` span straddled the premium's move (28 of 29 rows);
2. the premium table's `Rate after` was an intermediate no customer was charged (29 of 115);
3. the `Emergency reprices` headline was the surcharge count wearing another mechanism's name.

R15: each control below is mutation-proven — the mutation it fires on is named in its docstring.
"""
import ast
import pathlib

import pytest

from saas.reporting.annual_report import (
    _rate_span_is_own,
    _section_dynamic_pricing,
    _section_dynamic_pricing_activity,
    _section_margin_feedback,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
# THE PRODUCER MOVED, and these controls moved with it. Both structural controls
# below have the RATE-CHAIN PRODUCER as their subject — the code that writes the
# per-writer spans and the decomposition. KNIFE step 24 (register §3s) lifted the
# whole chain out of the world's term loop into the supplier's own desk. Left
# pointing at `run_phase2b.py` they would both pass on an absent producer: the
# AST walk would find no `unit_rate_before` dicts to object to, and only the
# cause-name control's string assertion would have caught it. A control whose
# subject has left the file it names is fail-open, not green.
RATE_CHAIN_PRODUCER = REPO_ROOT / "company" / "pricing" / "renewal_rate_chain.py"


# ---------------------------------------------------------------- the span guard


def test_a_pair_that_straddles_another_writers_move_is_not_its_own_span():
    """The published defect, in one row.

    112.2436 -> 153.39 labelled +20.0% is the real 2018-01-31 C_IC1 row: the span carries the
    premium's +13.88% as well. MUTATION: `_rate_span_is_own` returning True unconditionally
    makes this pass — i.e. the guard is what fires, not the fixture.
    """
    straddling = {"unit_rate_before": 112.2436, "unit_rate_after": 153.39}
    assert _rate_span_is_own(straddling, 20.0) is False

    own = {"unit_rate_before": 127.8264, "unit_rate_after": 153.39}
    assert _rate_span_is_own(own, 20.0) is True


@pytest.mark.parametrize(
    "entry",
    [
        {},
        {"unit_rate_before": None, "unit_rate_after": 153.39},
        {"unit_rate_before": 127.8264, "unit_rate_after": None},
        {"unit_rate_before": 0.0, "unit_rate_after": 153.39},
    ],
)
def test_the_span_guard_fails_closed_on_a_missing_end(entry):
    """R15 FAIL-OPEN: an absent/zero end is a FAILED check, never a pass.

    MUTATION: `return True` on the missing-value branch makes every case here pass.
    """
    assert _rate_span_is_own(entry, 20.0) is False


# ---------------------------------------------------------------- the rendered rows


def _mfl_entry(**over):
    e = {
        "customer_id": "C_IC1",
        "commodity": "electricity",
        "term_start": "2018-01-31",
        "prev_margin_gbp": -5651.81,
        "prev_revenue_gbp": 10420.08,
        "surcharge_pct": 20.0,
        "unit_rate_before": 112.2436,   # legacy: the PRE-premium original
        "unit_rate_after": 153.39,      # after BOTH writers
    }
    e.update(over)
    return e


def test_the_surcharge_table_withholds_a_span_it_cannot_reconcile():
    """The board row must not publish a pair that fails its own arithmetic.

    MUTATION: render `unit_rate_before`/`unit_rate_after` unconditionally (the pre-fix renderer)
    and `£112.24/MWh` reappears next to `+20.0%`, which is the finding verbatim.
    """
    out = _section_margin_feedback({"margin_feedback_log": [_mfl_entry()]})
    assert "£112.24/MWh" not in out
    assert "£153.39/MWh" not in out
    assert "—" in out
    assert "Withheld, not repaired" in out


def test_the_surcharge_table_publishes_a_chained_span_and_the_contracted_rate():
    """Once the producer chains the writers, the row reconciles and names the contracted rate."""
    out = _section_margin_feedback({
        "margin_feedback_log": [_mfl_entry(
            unit_rate_before=127.8264,      # the rate as it ENTERS the surcharge
            unit_rate_after=153.3917,
            unit_rate_contracted=153.3917,
        )],
    })
    assert "£127.83/MWh" in out
    assert "£153.39/MWh" in out
    assert "Withheld, not repaired" not in out


def test_the_premium_table_never_calls_its_intermediate_the_contracted_rate():
    """Defect 2: the premium's `Rate after` is a link, not the rate the customer contracted.

    MUTATION: drop the `Contracted` column and the intermediate is the last rate on the row
    again, which is how 29 of 115 rows read as a contracted rate that was never charged.
    """
    dpl = {
        "customer_id": "C_IC1",
        "commodity": "electricity",
        "term_start": "2018-01-31",
        "mean_recent_margin_rate": 0.05,
        "portfolio_premium_pct": 13.88,
        "unit_rate_original": 112.2436,
        "unit_rate_before": 112.2436,
        "unit_rate_after": 127.8264,
        "unit_rate_contracted": 153.3917,
    }
    out = _section_dynamic_pricing({"dynamic_pricing_log": [dpl]})
    assert "Contracted" in out
    assert "£153.39/MWh" in out
    row = [line for line in out.splitlines() if line.startswith("| C_IC1 ")][0]
    assert row.rstrip().endswith("£153.39/MWh |"), row


def test_a_run_without_the_chain_shows_no_contracted_rate_rather_than_guessing():
    """R9/R15: the cap and the uplift are unrecoverable from a legacy run, so the cell is empty
    and the reason is stated. MUTATION: deriving `Contracted` from the surcharge log alone
    publishes a pre-cap rate as the contracted one — a fresh wrong figure to replace the old.
    """
    out = _section_margin_feedback({"margin_feedback_log": [_mfl_entry()]})
    assert "this run predates the decomposed" in out


# ---------------------------------------------------------------- the relabelled column


def _activity_data(with_chain: bool):
    dpl = [{
        "customer_id": "C1", "commodity": "electricity", "term_start": "2018-01-31",
        "unit_rate_original": 100.0, "unit_rate_before": 100.0, "unit_rate_after": 110.0,
    }]
    data = {"dynamic_pricing_log": dpl, "margin_feedback_log": [
        {"customer_id": "C1", "commodity": "electricity", "term_start": "2018-01-31",
         "surcharge_pct": 20.0, "unit_rate_before": 110.0, "unit_rate_after": 132.0},
    ]}
    if with_chain:
        data["rate_decomposition_log"] = [{
            "customer_id": "C1", "commodity": "electricity", "term_start": "2018-01-31",
            "unit_rate_original": 100.0, "unit_rate_contracted": 132.0,
        }]
    return data


def test_the_surcharge_count_is_not_labelled_emergency():
    """Defect 3: `emergency = len(mfl_by_year[yr])` published the surcharge count under another
    mechanism's name, with a caption citing a cost floor `compute_margin_surcharge` does not have.

    MUTATION: restore the `Emergency` header/caption and both assertions below fail.
    """
    out = _section_dynamic_pricing_activity(_activity_data(with_chain=False))
    assert "emergency" not in out.lower()
    assert "cost floor" not in out.lower()
    assert "Margin surcharges" in out
    assert "Margin recovery surcharges: 1 total" in out
    # ...and the caption states the trigger the mechanism actually has, positively.
    assert "prior term's realised net margin" in out
    assert "5% of that term's revenue" in out


def test_the_caption_states_which_span_the_delta_covers():
    """A delta whose span is unstated reads as the whole renewal move when it is one writer's
    link. MUTATION: a fixed caption makes both branches below assert the same string.
    """
    without = _section_dynamic_pricing_activity(_activity_data(with_chain=False))
    assert "portfolio premium only" in without
    assert "+10.0" in without          # the premium's own link

    with_chain = _section_dynamic_pricing_activity(_activity_data(with_chain=True))
    assert "whole renewal move" in with_chain
    assert "+32.0" in with_chain       # original -> contracted, both writers


# ---------------------------------------------------------------- the producer mechanism


def test_no_rate_log_reads_its_before_off_the_never_rebound_term():
    """The defect's mechanism, structurally: a writer's `unit_rate_before` must be the rate
    ENTERING that writer, never the rate the term was struck at. Read it off the struck rate and
    the published span starts before every earlier writer's move.

    THE DEFECT CHANGED SHAPE WHEN THE PRODUCER MOVED, and this control changed with it. In the
    world's loop the never-rebound source was the subscript `term["unit_rate_gbp_per_mwh"]`; in
    the supplier's desk it is the parameter `struck_unit_rate_gbp_per_mwh` and the local
    `rate_original` it is copied to. Keeping only the old spelling would have left a control that
    cannot fail in the file it now names (R15) — so BOTH are named, and the vacuity guard below
    asserts the detector has something to look at either way.

    Subject is the producer source, so this holds at HEAD without waiting for a sim run.
    MUTATION: set any writer's `"unit_rate_before"` to `round(rate_original, 4)` and this fails.
    R15 FAIL-SILENT: an unparseable source fails, not skips.
    """
    NEVER_REBOUND = ("struck_unit_rate_gbp_per_mwh", "rate_original")

    tree = ast.parse(RATE_CHAIN_PRODUCER.read_text())
    offenders = []
    seen = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values):
            if not (isinstance(key, ast.Constant) and key.value == "unit_rate_before"):
                continue
            seen += 1
            src = ast.dump(value)
            if "'term'" in src and "unit_rate_gbp_per_mwh" in src:
                offenders.append(f"line {getattr(value, 'lineno', '?')} (term subscript)")
            elif any(f"'{name}'" in src for name in NEVER_REBOUND):
                offenders.append(f"line {getattr(value, 'lineno', '?')} (struck rate)")
    # VACUITY GUARD — a producer with no `unit_rate_before` at all would make the
    # loop above pass over nothing, which is how this control fail-opens.
    assert seen >= 3, (
        f"found {seen} `unit_rate_before` spans in the producer, expected one per "
        "logging writer — this control is examining the wrong file"
    )
    assert not offenders, (
        "a rate log takes its `unit_rate_before` from a never-rebound source "
        f"instead of the rate entering that writer: {offenders}"
    )


def test_every_rate_writer_contributes_a_named_cause_to_the_chain():
    """All four writers must appear in the decomposition, or the chain is not the whole move.

    MUTATION: delete any one `result.components.append` in the rate-chain producer and the
    missing cause is named here. FAIL-CLOSED on a parse failure or a renamed cause.
    """
    src = RATE_CHAIN_PRODUCER.read_text()
    for cause in ("portfolio_premium", "margin_surcharge", "profitability_uplift", "price_cap"):
        assert f'"cause": "{cause}"' in src, f"no chain component for {cause}"
    assert "result.decomposition = {" in src
