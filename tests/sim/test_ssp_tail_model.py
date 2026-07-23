"""T1 (tail-fidelity) + T2 (no-goal-seek) for the spike-tail attack plan (SPIKE_TAIL_SSP_RESIDUAL).

The defect: the residual position settles at SSP, but the SIM's SSP generator (sim/price_engine.py's
residual-demand scarcity form) produces a tail that is too thin -- model max GBP574 vs real GBP4,038,
0.013% negative vs 2.241% real -- so the world cannot bite the company the way 2021-22 bit real
suppliers. sim/ssp_tail_target.py gives the REAL target (step 1, landed); sim/ssp_tail_model.py
measures the MODEL tail from the generator (step 3, control-first, this change).

R15 obligations mechanised here:
  T1  tail-fidelity: model {max, neg-fraction, exceedance} must match the real target within tolerance.
      Marked strict xfail because the generator is NOT yet reshaped -- the gap is the defect. When the
      generator IS reshaped to reproduce the real tail, this XPASSES and strict-xfail turns that into a
      FAILURE, forcing the marker's removal and the register close in the same commit (closes_when).
      Killer mutation (the control fires on its own defect): see test_gap_is_real_today below, which
      asserts the truncation exists NOW -- re-introduce a heavy tail and it fails.
  T2  no-goal-seek (R12/R13): the generator + its tail measurement must not import company/saas -- there
      is no company-P&L write-back path into the baseline tail. Killer mutation: add such an import.
  FAIL-CLOSED: an uncomputable model tail RAISES, never returns a silently-zero pass.
"""
import pytest

import sim.ssp_tail_model as model
import sim.ssp_tail_target as tgt


# ---- FAIL-CLOSED (the guard must be able to fire) -------------------------------------------------

def test_model_tail_fail_closed_on_no_rows(monkeypatch):
    monkeypatch.setattr(
        "simulation.run_phase3b_recalibration._build_dataset", lambda: []
    )
    with pytest.raises(ValueError):
        model.model_ssp_series()


def test_shared_tail_stats_rejects_empty():
    # T1 grades both sides through this one function -- it must fail-closed identically for both.
    with pytest.raises(ValueError):
        tgt.tail_stats([])


# ---- SHAPE: the model tail is a real distribution measurement (synthetic, no cache) ----------------

def test_model_tail_stats_shape_from_synthetic():
    stats = tgt.tail_stats([-5.0] * 10 + [50.0] * 85 + [250.0, 250.0, 250.0, 600.0, 600.0])
    assert stats["n"] == 100
    assert stats["frac_negative"] == pytest.approx(0.10)
    assert stats["exceedance_gbp"]["frac_gt_200"] == pytest.approx(0.05)
    fr = [stats["exceedance_gbp"][f"frac_gt_{k}"] for k in (200, 300, 500, 1000, 2000, 3000)]
    assert fr == sorted(fr, reverse=True), "exceedance curve must be monotonically non-increasing"


# ---- T2: no goal-seek / no company-P&L write-back path into the baseline tail (R12/R13) ------------

def test_no_goalseek_path():
    import inspect
    for mod in (model, __import__("sim.price_engine", fromlist=["x"])):
        src = inspect.getsource(mod)
        assert "import company" not in src and "from company" not in src, (
            f"{mod.__name__} imports company.* -- a P&L write-back path into the baseline tail (R13 breach)"
        )
        assert "import saas" not in src and "from saas" not in src, (
            f"{mod.__name__} imports saas.* -- a P&L write-back path into the baseline tail (R13 breach)"
        )


# ---- Real-cache integration (skip if the Elexon caches are absent in this env) --------------------

def _both_tails_or_skip():
    from sim.cache_store import get_cached_prices
    if not get_cached_prices(tgt.MODEL_START_DATE, tgt.MODEL_END_DATE):
        pytest.skip("real Elexon SSP cache not present in this environment")
    try:
        m = model.model_ssp_tail()
    except (FileNotFoundError, ValueError):
        pytest.skip("driver caches (demand/agws/gas) not present in this environment")
    return m, tgt.real_ssp_tail()


def test_gap_is_real_today():
    """The mechanised belief-vs-truth gap: the model tail IS truncated relative to reality RIGHT NOW.
    This is T1's killer-mutation companion -- it fails the moment the generator is reshaped to close the
    tail, forcing the register to `closed` + T1's marker removal in the same commit (closes_when)."""
    m, real = _both_tails_or_skip()
    # real world reaches the multi-thousand-pound scarcity-spike regime; the model does not
    assert real["max"] > 3000.0, "real SSP tail must reach the >GBP3000 spike regime (target sanity)"
    assert real["exceedance_gbp"]["frac_gt_2000"] > 0.0
    assert m["max"] < 1000.0, (
        f"model SSP max is {m['max']:.0f} -- if this now reaches the real tail, the defect is CLOSED: "
        "flip T1 to a real assertion and set SPIKE_TAIL_SSP_RESIDUAL status: closed this commit"
    )
    assert m["exceedance_gbp"]["frac_gt_2000"] == 0.0, "model still starves the scarcity-spike tail"
    assert m["frac_negative"] < 0.005, "model still starves the negative-price tail (real ~2.24%)"


@pytest.mark.xfail(
    strict=True,
    reason="SPIKE_TAIL_SSP_RESIDUAL open: generator tail not yet reshaped (step 3 physics change is a "
           "supervised R13 build). XPASS => tail reproduced => remove marker + close the register.",
)
def test_T1_model_tail_matches_real_within_tolerance():
    m, real = _both_tails_or_skip()
    # max within ~10% of the real GBP4,038 peak
    assert m["max"] == pytest.approx(real["max"], rel=0.10)
    # negative-price fraction within the ledger's stated tolerance of the real ~2.241%
    assert m["frac_negative"] == pytest.approx(real["frac_negative"], abs=0.005)
    # the shape between: the model must spend real time in the scarcity-spike regime, not starve it
    assert m["exceedance_gbp"]["frac_gt_500"] == pytest.approx(
        real["exceedance_gbp"]["frac_gt_500"], abs=0.003
    )
    assert m["exceedance_gbp"]["frac_gt_2000"] > 0.0
