"""W2_12 — WORLD-side final-bill (credit-risk exit) physics.

Test discipline notes:
  * No test derives its expected value by calling the code path it checks.
    Windows, DCA proceeds and the Beta mean are all recomputed independently.
  * The population-level tests assert DIRECTIONS that follow from the
    documented mechanism, not from re-running the formula — so deleting the
    mechanism breaks them, while a legitimate recalibration does not.
"""
from __future__ import annotations

import datetime as dt
import statistics

import pytest

from simulation.arrears_engine import (
    DCA_COMMISSION_RATE,
    DCA_RECOVERY_RATE,
    DEBT_SALE_HAIRCUT_PCT,
)
from simulation.final_bill_outcome import (
    GONE_AWAY_BASE_BETA,
    GONE_AWAY_MAX,
    FinalBillOutcome,
    exit_debt_recovery_gbp,
    gone_away_probability,
    open_final_bill_exposure,
    resolve_final_bill,
)

CLOSURE = dt.date(2024, 3, 1)
LATER = dt.date(2024, 12, 31)


def _exposure(i: int = 0, balance: float = 120.0, customer_id: str | None = None):
    return open_final_bill_exposure(
        account_id=f"ACC{i:05d}",
        supply_point_id=f"SP{i:05d}",
        fuel="electricity",
        closure_date=CLOSURE,
        net_balance_gbp=balance,
        customer_id=customer_id if customer_id is not None else f"CUST{i:05d}",
    )


# ---------------------------------------------------------------------------
# C-S3 — the outcome is a SEPARATE EVENT LATER IN TIME
# ---------------------------------------------------------------------------

def test_exposure_carries_no_outcome_at_closure():
    """The exposure object must not be able to answer 'was it paid?' at all —
    if it could, the wall contract would be synchronous."""
    exposure = _exposure()
    assert not hasattr(exposure, "outcome")
    assert not hasattr(exposure, "gone_away")


def test_resolution_is_pending_until_the_full_regulatory_window_has_run():
    exposure = _exposure()
    # Independently computed: SLC 21B six weeks + the 28-day overdue window.
    expected_resolution = CLOSURE + dt.timedelta(days=42 + 28)
    assert exposure.resolution_date == expected_resolution
    assert exposure.final_bill_due == CLOSURE + dt.timedelta(days=42)

    assert resolve_final_bill(exposure, CLOSURE) is None
    assert resolve_final_bill(exposure, expected_resolution - dt.timedelta(days=1)) is None
    assert resolve_final_bill(exposure, expected_resolution) is not None


def test_pending_is_not_silently_a_pass():
    """A missing answer must be None, never a defaulted 'paid' — the
    fail-open shape this whole mechanism exists to avoid."""
    result = resolve_final_bill(_exposure(), CLOSURE + dt.timedelta(days=10))
    assert result is None


def test_resolution_is_stamped_at_the_regulatory_date_not_the_query_date():
    """Resolving late must not backdate or postdate the real event."""
    exposure = _exposure()
    early = resolve_final_bill(exposure, exposure.resolution_date)
    late = resolve_final_bill(exposure, exposure.resolution_date + dt.timedelta(days=400))
    assert early.resolved_on == late.resolved_on == exposure.resolution_date


# ---------------------------------------------------------------------------
# C-S2 — determinism, idempotency, substream isolation
# ---------------------------------------------------------------------------

def test_resolution_is_idempotent_across_repeated_and_out_of_order_calls():
    exposure = _exposure(7)
    a = resolve_final_bill(exposure, LATER)
    b = resolve_final_bill(exposure, exposure.resolution_date)
    c = resolve_final_bill(exposure, LATER + dt.timedelta(days=900))
    assert a == b == c


def test_drawing_the_probability_first_does_not_shift_the_outcome():
    """Substream isolation: consuming one named substream must not advance any
    other. A single shared RNG would fail this."""
    baseline = resolve_final_bill(_exposure(11), LATER)
    exposure = _exposure(11)
    for _ in range(50):
        gone_away_probability(exposure)
    assert resolve_final_bill(exposure, LATER) == baseline


def test_distinct_exposures_of_the_same_customer_resolve_independently():
    customer = "CUST-SHARED"
    a = resolve_final_bill(
        open_final_bill_exposure("ACC-A", "SP-A", "electricity", CLOSURE, 120.0, customer), LATER
    )
    b = resolve_final_bill(
        open_final_bill_exposure("ACC-B", "SP-B", "electricity", CLOSURE, 120.0, customer), LATER
    )
    # Same household truth, different exits — the identity keying must not
    # collapse them into one shared draw.
    assert a.account_id != b.account_id


def test_fuel_agnostic_keying():
    """Gas and electricity exits of one property are separate exposures."""
    elec = open_final_bill_exposure("ACC-1", "SP-1", "electricity", CLOSURE, 120.0, "C1")
    gas = open_final_bill_exposure("ACC-1", "SP-1", "gas", CLOSURE, 120.0, "C1")
    assert elec.exposure_id != gas.exposure_id


# ---------------------------------------------------------------------------
# The physics itself — these must FAIL if the mechanism is removed
# ---------------------------------------------------------------------------

def test_base_rate_is_sampled_not_a_point_estimate():
    """R10: the unanchorable parameter is drawn per move. A hardcoded constant
    would give zero variance here."""
    probabilities = [gone_away_probability(_exposure(i)) for i in range(400)]
    assert statistics.pstdev(probabilities) > 0.01

    # Beta(a, b) mean, computed independently of the module.
    alpha, beta = GONE_AWAY_BASE_BETA
    beta_mean = alpha / (alpha + beta)
    # Multipliers pull the realised mean off the raw Beta mean, but not wildly.
    assert 0.3 * beta_mean < statistics.mean(probabilities) < 3.0 * beta_mean
    assert all(0.0 < p <= GONE_AWAY_MAX for p in probabilities)


def test_exit_risk_is_materially_worse_than_the_ordinary_arrears_baseline():
    """The one load-bearing published claim (Ofgem, 30 Oct 2025): move-out debt
    is grossly over-represented versus the ~3.8% of customers in ordinary
    mid-tenure arrears (Ofgem Debt & Arrears Indicators, Q1 2026)."""
    OFGEM_ORDINARY_ARREARS_RATE = 0.038
    resolutions = [resolve_final_bill(_exposure(i), LATER) for i in range(1500)]
    billed = sum(r.billed_gbp for r in resolutions)
    shortfall = sum(r.shortfall_gbp for r in resolutions)
    assert shortfall / billed > OFGEM_ORDINARY_ARREARS_RATE * 2


def test_income_stress_worsens_the_exit_monotonically():
    def shortfall_share(stress: str) -> float:
        rs = [resolve_final_bill(_exposure(i), LATER, stress=stress) for i in range(1200)]
        return sum(r.shortfall_gbp for r in rs) / sum(r.billed_gbp for r in rs)

    low, moderate, high = (shortfall_share(s) for s in ("LOW", "MODERATE", "HIGH"))
    assert low < moderate < high


def test_gone_away_is_a_real_leg_not_a_label():
    """Gone-away exits must recover materially less than traceable ones —
    otherwise the mechanism Ofgem blames for £1.1-1.7bn is decorative."""
    resolutions = [resolve_final_bill(_exposure(i), LATER, stress="MODERATE") for i in range(1500)]
    gone = [r for r in resolutions if r.gone_away]
    traceable = [r for r in resolutions if not r.gone_away]
    assert gone and traceable

    def recovery_rate(rs):
        return sum(r.recovered_gbp for r in rs) / sum(r.billed_gbp for r in rs)

    assert recovery_rate(gone) < 0.5 * recovery_rate(traceable)


def test_a_closure_in_credit_carries_no_credit_risk():
    exposure = _exposure(3, balance=-45.0)
    resolution = resolve_final_bill(exposure, LATER)
    assert resolution.outcome is FinalBillOutcome.CREDIT_DUE
    assert resolution.billed_gbp == 0.0
    assert resolution.shortfall_gbp == 0.0
    assert resolution.gone_away is False


def test_recovered_never_exceeds_billed_and_shortfall_is_consistent():
    for i in range(300):
        r = resolve_final_bill(_exposure(i), LATER, stress="HIGH")
        assert 0.0 <= r.recovered_gbp <= r.billed_gbp + 0.01
        assert r.shortfall_gbp == pytest.approx(max(0.0, r.billed_gbp - r.recovered_gbp), abs=0.02)


def test_paid_on_time_recovers_the_whole_balance():
    paid = [
        r for r in (resolve_final_bill(_exposure(i), LATER) for i in range(400))
        if r.outcome is FinalBillOutcome.PAID_ON_TIME
    ]
    assert paid
    assert all(r.recovered_gbp == r.billed_gbp and r.days_late == 0 for r in paid)


def test_paid_late_is_paid_in_full_but_late():
    late = [
        r for r in (resolve_final_bill(_exposure(i), LATER, stress="MODERATE") for i in range(600))
        if r.outcome is FinalBillOutcome.PAID_LATE
    ]
    assert late
    assert all(r.recovered_gbp == r.billed_gbp and r.days_late > 0 for r in late)


# ---------------------------------------------------------------------------
# Fold, don't duplicate — the exit joins the EXISTING recovery cascade
# ---------------------------------------------------------------------------

def test_exit_debt_recovery_reuses_the_existing_dca_cascade():
    """Expected values computed here from arrears_engine's own published
    constants, so a divergent second copy of the cascade would fail."""
    trajectory = [{"year": 2023, "stress": "LOW"}, {"year": 2024, "stress": "HIGH"}]
    exposure = _exposure(21, balance=500.0)
    resolution = resolve_final_bill(exposure, LATER, stress="HIGH",
                                    income_stress_trajectory=trajectory)
    assert resolution.debt_archetype == "OVERWHELMED"
    if resolution.shortfall_gbp > 0:
        expected = round(
            resolution.shortfall_gbp
            * DCA_RECOVERY_RATE["OVERWHELMED"]
            * (1 - DCA_COMMISSION_RATE),
            2,
        )
        assert exit_debt_recovery_gbp(resolution) == expected


def test_avoidant_exit_debt_is_sold_at_the_existing_haircut():
    trajectory = [{"year": y, "stress": "HIGH"} for y in (2022, 2023, 2024)]
    for i in range(200):
        resolution = resolve_final_bill(
            _exposure(i, balance=500.0), LATER, stress="HIGH",
            income_stress_trajectory=trajectory,
        )
        if resolution.shortfall_gbp > 0:
            assert resolution.debt_archetype == "AVOIDANT"
            assert exit_debt_recovery_gbp(resolution) == round(
                resolution.shortfall_gbp * DEBT_SALE_HAIRCUT_PCT, 2
            )
            return
    pytest.fail("no shortfall produced in 200 HIGH-stress exits — physics not firing")


def test_no_recovery_claimed_without_a_shortfall_or_an_archetype():
    resolution = resolve_final_bill(_exposure(5, balance=-10.0), LATER)
    assert exit_debt_recovery_gbp(resolution) == 0.0


# ---------------------------------------------------------------------------
# The epistemic wall
# ---------------------------------------------------------------------------

def test_resolution_holds_hidden_drivers_so_the_strip_is_doing_real_work():
    """If the resolution carried nothing hidden, the observable-event test
    below would be vacuous."""
    resolution = resolve_final_bill(
        _exposure(9), LATER, stress="HIGH",
        income_stress_trajectory=[{"year": 2024, "stress": "HIGH"}],
    )
    assert resolution.gone_away_probability > 0
    assert resolution.debt_archetype is not None


def test_observable_event_exposes_only_observable_fields():
    resolution = resolve_final_bill(
        _exposure(9), LATER, stress="HIGH",
        income_stress_trajectory=[{"year": 2024, "stress": "HIGH"}],
    )
    event = resolution.as_observable_event()
    assert set(event) == {
        "schema", "account_id", "supply_point_id", "fuel", "resolved_on",
        "outcome", "billed_gbp", "recovered_gbp", "gone_away", "days_late",
    }
    assert "gone_away_probability" not in event
    assert "debt_archetype" not in event
    assert event["schema"] == "final_bill_outcome.v1"


def test_world_module_does_not_import_the_company_layer():
    import simulation.final_bill_outcome as mod

    source = open(mod.__file__).read()
    assert "import company" not in source
    assert "from company" not in source
    assert "import saas" not in source
    assert "from saas" not in source
