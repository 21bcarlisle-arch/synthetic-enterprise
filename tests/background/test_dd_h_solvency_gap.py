"""DD-H (atom DD_seasonal_cashflow_physics) -- closed-loop tests for the
solvency belief-vs-truth GAP organ, background/dd_h_solvency_gap.py.

R15 both-ways is mandatory here (the gap is a control on a decision-relevant
tell). The three killer patterns each get a test:
  * FAIL-OPEN  -- a non-finite / silently-zeroed input must REJECT, never read
                  as "perfectly solvent".
  * FAIL-SILENT-- an absent DD3 block must yield an explicit not-measurable row,
                  never a fabricated gap=0.
  * TAUTOLOGY  -- the gap is belief-minus-truth cross-checked against held
                  credit; a block whose held-credit field was altered must
                  refuse to score, not trust the derived single figure.
Plus the positive direction: a real held credit against real equity MUST move
the normalised gap off zero, and held credit exceeding believed equity MUST fire
the cash-rich-but-insolvent tell (gap >= 1).
"""

import json
import math

import pytest

from background import dd_h_solvency_gap as ddh
from background.dd_h_solvency_gap import (
    SolvencyGapUnmeasurable,
    compute_solvency_gap,
    measure_from_run_output,
    record_gap,
    retro_gap_line,
)


def _block(naive, true, held, month="2020-10"):
    """A minimal DD3 balance_sheet_with_held_credit block (only the fields the
    organ reads)."""
    return {
        "naive_total_equity_gbp": naive,
        "true_total_equity_gbp": true,
        "customer_credit_held_gbp": held,
        "as_at_month": month,
        "peak_month": month,
    }


# --------------------------------------------------------------------------
# Positive direction -- the organ measures the real gap.
# --------------------------------------------------------------------------

def test_healthy_supplier_small_positive_gap_no_tell():
    # The real latest run: peak held credit £1,949.51 against ~£4.24M equity.
    row = compute_solvency_gap(_block(4_240_000.0, 4_238_050.49, 1_949.51))
    assert row["held_credit_gbp"] == 1_949.51
    assert row["gap_gbp"] == pytest.approx(1_949.51, abs=0.01)
    assert 0.0 < row["gap_normalised"] < 0.001  # tiny but non-zero
    assert row["cash_rich_but_insolvent"] is False


def test_held_credit_moves_gap_off_zero_FAILOPEN_GUARD():
    # R15 FAIL-OPEN guard: a sustained-credit position must move the gap off
    # zero. A variant that ignored held credit would leave it at 0.0.
    honest = compute_solvency_gap(_block(1_000_000.0, 1_000_000.0, 0.0))
    assert honest["gap_normalised"] == 0.0
    assert honest["cash_rich_but_insolvent"] is False

    with_credit = compute_solvency_gap(_block(1_000_000.0, 900_000.0, 100_000.0))
    assert with_credit["gap_normalised"] == pytest.approx(0.1, abs=1e-6)
    assert with_credit["gap_gbp"] == pytest.approx(100_000.0)


def test_cash_rich_but_insolvent_tell_fires_at_gap_ge_one():
    # Held credit EXCEEDS believed equity -> true equity negative -> the tell
    # fires and the normalised gap crosses 1.0 at exactly that boundary.
    row = compute_solvency_gap(_block(80_000.0, -20_000.0, 100_000.0))
    assert row["cash_rich_but_insolvent"] is True
    assert row["gap_normalised"] >= 1.0

    # And it must NOT fire when believed equity comfortably covers held credit.
    covered = compute_solvency_gap(_block(500_000.0, 400_000.0, 100_000.0))
    assert covered["cash_rich_but_insolvent"] is False
    assert covered["gap_normalised"] < 1.0


def test_tell_recomputed_not_copied_from_block():
    # Independence: even if the block carried a LYING flag, the organ recomputes
    # the tell from the equities. (The organ ignores any block-level flag.)
    lying = _block(500_000.0, 400_000.0, 100_000.0)
    lying["cash_rich_but_insolvent"] = True  # false claim in the block
    row = compute_solvency_gap(lying)
    assert row["cash_rich_but_insolvent"] is False  # truth from the equities


def test_belief_non_positive_gap_normalised_none_but_raw_reported():
    # Company already believes itself worthless -> normalisation undefined, but
    # the raw gap and the tell are still reported (no divide-by-zero artefact).
    row = compute_solvency_gap(_block(0.0, -5_000.0, 5_000.0))
    assert row["gap_normalised"] is None
    assert row["gap_gbp"] == pytest.approx(5_000.0)


# --------------------------------------------------------------------------
# R15 FAIL-CLOSED -- non-finite inputs REJECT.
# --------------------------------------------------------------------------

@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf"), None, "oops"])
def test_non_finite_belief_rejected_FAILCLOSED(bad):
    with pytest.raises(SolvencyGapUnmeasurable):
        compute_solvency_gap(_block(bad, 1.0, 0.0))


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), None])
def test_non_finite_truth_rejected_FAILCLOSED(bad):
    with pytest.raises(SolvencyGapUnmeasurable):
        compute_solvency_gap(_block(1_000.0, bad, 0.0))


def test_negative_held_credit_rejected():
    # Held credit is a positive-balances-only aggregate; a negative net is a
    # corrupt block, never coerced to zero.
    with pytest.raises(SolvencyGapUnmeasurable):
        compute_solvency_gap(_block(1_000.0, 1_100.0, -100.0))


# --------------------------------------------------------------------------
# R15 TAUTOLOGY guard -- belief-truth must match held credit.
# --------------------------------------------------------------------------

def test_inconsistent_block_rejected_TAUTOLOGY_GUARD():
    # belief-truth = 100k but the held-credit field says 5k: one was altered.
    # The organ must refuse to score rather than trust the single derived figure.
    with pytest.raises(SolvencyGapUnmeasurable):
        compute_solvency_gap(_block(1_000_000.0, 900_000.0, 5_000.0))


def test_penny_rounding_within_tolerance_accepted():
    # DD3 rounds each field to the penny; ~1p of drift is legitimate.
    row = compute_solvency_gap(_block(1_000_000.00, 900_000.01, 100_000.00))
    assert row["gap_normalised"] == pytest.approx(0.09999999, abs=1e-6)


# --------------------------------------------------------------------------
# FAIL-SILENT guard -- absent block yields not-measurable, never gap=0.
# --------------------------------------------------------------------------

def test_absent_block_is_not_measurable_not_zero(tmp_path):
    p = tmp_path / "run_output.json"
    p.write_text(json.dumps({"some_other_key": 1}), encoding="utf-8")
    row = measure_from_run_output(p)
    assert row["measurable"] is False
    assert "gap_normalised" not in row  # crucially NOT a fabricated 0.0
    assert "no dd3_held_credit_balance_sheet" in row["reason"]


def test_unreadable_run_output_not_measurable(tmp_path):
    row = measure_from_run_output(tmp_path / "does_not_exist.json")
    assert row["measurable"] is False
    assert "unreadable" in row["reason"]


def test_measure_finds_nested_block(tmp_path):
    # The block lives nested under a report-data section in the real output.
    p = tmp_path / "run_output.json"
    p.write_text(json.dumps({
        "report_data": {"dd3_held_credit_balance_sheet": _block(500_000.0, 400_000.0, 100_000.0)}
    }), encoding="utf-8")
    row = measure_from_run_output(p)
    assert row["measurable"] is True
    assert row["gap_gbp"] == pytest.approx(100_000.0)


def test_malformed_present_block_propagates(tmp_path):
    # A present-but-corrupt block is a defect to surface, not swallow.
    p = tmp_path / "run_output.json"
    p.write_text(json.dumps({
        "dd3_held_credit_balance_sheet": _block(1_000_000.0, 900_000.0, 5_000.0)
    }), encoding="utf-8")
    with pytest.raises(SolvencyGapUnmeasurable):
        measure_from_run_output(p)


# --------------------------------------------------------------------------
# retro_gap_line -- pure, fail-closed digest string.
# --------------------------------------------------------------------------

def test_retro_line_measurable(tmp_path):
    p = tmp_path / "run_output.json"
    p.write_text(json.dumps({
        "dd3_held_credit_balance_sheet": _block(4_240_000.0, 4_238_050.49, 1_949.51)
    }), encoding="utf-8")
    line = retro_gap_line(p)
    assert "solvency belief-vs-truth gap" in line
    assert "1,950" in line or "1,949" in line  # held credit rendered
    assert "INSOLVENT" not in line.upper() or "CASH-RICH" not in line.upper()


def test_retro_line_fires_tell(tmp_path):
    p = tmp_path / "run_output.json"
    p.write_text(json.dumps({
        "dd3_held_credit_balance_sheet": _block(80_000.0, -20_000.0, 100_000.0)
    }), encoding="utf-8")
    line = retro_gap_line(p)
    assert "CASH-RICH-BUT-INSOLVENT" in line


def test_retro_line_not_measurable_is_honest(tmp_path):
    p = tmp_path / "run_output.json"
    p.write_text(json.dumps({"nope": 1}), encoding="utf-8")
    line = retro_gap_line(p)
    assert "not yet measurable" in line
    # Never a number implying solvency when we could not measure.
    assert "0.000" not in line


def test_retro_line_malformed_is_red_not_crash(tmp_path):
    p = tmp_path / "run_output.json"
    p.write_text(json.dumps({
        "dd3_held_credit_balance_sheet": _block(1_000_000.0, 900_000.0, 5_000.0)
    }), encoding="utf-8")
    line = retro_gap_line(p)
    assert "NOT MEASURABLE" in line


# --------------------------------------------------------------------------
# record_gap -- dated history append, determinism (no clock in the organ).
# --------------------------------------------------------------------------

def test_record_gap_appends_dated_row(tmp_path):
    run_p = tmp_path / "run_output.json"
    run_p.write_text(json.dumps({
        "dd3_held_credit_balance_sheet": _block(500_000.0, 400_000.0, 100_000.0)
    }), encoding="utf-8")
    ledger = tmp_path / "ledger.json"
    row = record_gap(measured_at="2026-07-29T06:00+00:00", run_git_commit="deadbeef",
                     run_output_path=run_p, ledger_path=ledger)
    assert row["measured_at"] == "2026-07-29T06:00+00:00"
    assert row["run_git_commit"] == "deadbeef"
    saved = json.loads(ledger.read_text())
    assert len(saved) == 1 and saved[0]["gap_gbp"] == pytest.approx(100_000.0)

    # A second record appends, not overwrites -- history accumulates.
    record_gap(measured_at="2026-07-30T06:00+00:00", run_git_commit="cafef00d",
               run_output_path=run_p, ledger_path=ledger)
    assert len(json.loads(ledger.read_text())) == 2


def test_record_gap_logs_not_measurable_row(tmp_path):
    # Honest absence is recorded, not silently skipped.
    run_p = tmp_path / "run_output.json"
    run_p.write_text(json.dumps({"nope": 1}), encoding="utf-8")
    ledger = tmp_path / "ledger.json"
    row = record_gap(measured_at="2026-07-29T06:00+00:00", run_output_path=run_p,
                     ledger_path=ledger)
    assert row["measurable"] is False
    assert len(json.loads(ledger.read_text())) == 1


def test_organ_calls_no_clock():
    # Determinism (C-S2): the module must never import a wall-clock. A crude but
    # effective guard -- the source names no datetime/time construction.
    src = (ddh.__file__)
    with open(src, encoding="utf-8") as f:
        text = f.read()
    assert "datetime.now" not in text
    assert "time.time" not in text


def test_module_severed_from_draw():
    # SEVERANCE: the organ must not import the supervisor / draw. Mirrors
    # daily_self_note §2 -- no path into the draw.
    with open(ddh.__file__, encoding="utf-8") as f:
        text = f.read()
    assert "import supervisor" not in text
    assert "from background.supervisor" not in text
