"""Tests for Activation Energy Model (Phase ED)."""
import pytest
from company.core.activation_energy import (
    ActionType, ActivationEnergyProfile, ActivationEnergyRegister,
    _BASE_AE, _TENURE_INERTIA_PER_YEAR, _PPM_AE_UPLIFT, _GOOD_RESOLUTION_AE_REDUCTION,
)


def make_profile(account="C1", tenure=1.0, ppm=False, resolutions=0, gri=1.0):
    return ActivationEnergyProfile(
        account_id=account,
        base_ae_switching=100.0,
        tenure_years=tenure,
        is_ppm=ppm,
        good_resolutions=resolutions,
        gri_multiplier=gri,
    )


@pytest.fixture
def reg():
    return ActivationEnergyRegister()


class TestActivationEnergyProfile:
    def test_base_switching_ae(self):
        p = make_profile(tenure=0.0)
        assert p.switching_ae() == pytest.approx(_BASE_AE[ActionType.SWITCH_SUPPLIER])

    def test_tenure_increases_ae(self):
        p1 = make_profile(tenure=1.0)
        p2 = make_profile(tenure=3.0)
        assert p2.switching_ae() > p1.switching_ae()

    def test_tenure_capped_at_40(self):
        p = make_profile(tenure=100.0)  # very long tenure
        p_cap = make_profile(tenure=8.0)  # 8 yrs * 5 = 40 = cap
        assert p.switching_ae() == pytest.approx(p_cap.switching_ae())

    def test_ppm_uplift(self):
        p_normal = make_profile(ppm=False)
        p_ppm = make_profile(ppm=True)
        assert p_ppm.switching_ae() == pytest.approx(p_normal.switching_ae() + _PPM_AE_UPLIFT)

    def test_good_resolution_reduces_ae(self):
        p0 = make_profile(resolutions=0)
        p2 = make_profile(resolutions=2)
        expected_reduction = 2 * _GOOD_RESOLUTION_AE_REDUCTION
        assert p2.switching_ae() == pytest.approx(p0.switching_ae() - expected_reduction)

    def test_gri_crisis_reduces_ae(self):
        p_normal = make_profile(gri=1.0)
        p_crisis = make_profile(gri=0.5)
        assert p_crisis.switching_ae() == pytest.approx(p_normal.switching_ae() * 0.5)

    def test_complaint_ae_lower_than_switching(self):
        p = make_profile()
        assert p.complaint_ae() < p.switching_ae()

    def test_will_act_above_ae(self):
        p = make_profile(tenure=0, ppm=False, gri=1.0)
        # switching AE = 100; utility = 150 > 100
        assert p.will_act(ActionType.SWITCH_SUPPLIER, 150.0)

    def test_will_not_act_below_ae(self):
        p = make_profile(tenure=0, ppm=False, gri=1.0)
        # switching AE = 100; utility = 50 < 100
        assert not p.will_act(ActionType.SWITCH_SUPPLIER, 50.0)

    def test_ae_never_negative(self):
        p = make_profile(resolutions=100, gri=0.01)
        assert p.switching_ae() >= 0.0


class TestActivationEnergyRegister:
    def test_register_and_get(self, reg):
        p = make_profile("C1")
        reg.register(p)
        assert reg.get("C1") is p

    def test_get_missing(self, reg):
        assert reg.get("MISSING") is None

    def test_high_inertia_accounts(self, reg):
        reg.register(make_profile("C1", tenure=5.0, ppm=True))   # high AE
        reg.register(make_profile("C2", tenure=0.0, ppm=False))  # lower AE
        high = reg.high_inertia_accounts(threshold=120.0)
        assert "C1" in high

    def test_low_inertia_accounts(self, reg):
        reg.register(make_profile("C1", tenure=0.0, gri=0.5))  # crisis GRI, low tenure
        reg.register(make_profile("C2", tenure=5.0))
        low = reg.low_inertia_accounts(threshold=80.0)
        assert "C1" in low

    def test_accounts_that_would_switch(self, reg):
        reg.register(make_profile("C1", tenure=0.0, gri=1.0))   # AE=100
        reg.register(make_profile("C2", tenure=0.0, gri=0.4))   # AE=40
        switchers = reg.accounts_that_would_switch(perceived_bill_saving_gbp=60.0)
        assert "C2" in switchers
        assert "C1" not in switchers

    def test_ae_summary(self, reg):
        reg.register(make_profile())
        s = reg.ae_summary()
        assert "Activation Energy" in s

    def test_constants(self):
        assert _BASE_AE[ActionType.SWITCH_SUPPLIER] == pytest.approx(100.0)
        assert _BASE_AE[ActionType.RAISE_COMPLAINT] == pytest.approx(40.0)
        assert _PPM_AE_UPLIFT == pytest.approx(20.0)
        assert _TENURE_INERTIA_PER_YEAR == pytest.approx(5.0)
