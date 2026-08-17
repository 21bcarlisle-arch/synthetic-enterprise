"""Tests for tools/generate_customer_data.py pure helpers."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

import json

from tools.generate_customer_data import (
    _tariff, _meter, _base_id, _mpan, _mprn, _mpan_check_digit, _timeline,
    _forecast_cashflow, generate,
)
import tools.generate_customer_data as gcd_module


def test_tariff_ic_segment():
    assert _tariff("I&C", "electricity") == "Half-Hourly Industrial and Commercial"


def test_tariff_resi_electricity():
    assert _tariff("resi", "electricity") == "Standard Variable (Electricity)"


def test_tariff_resi_gas():
    assert _tariff("resi", "gas") == "Standard Variable (Gas)"


def test_tariff_sme():
    assert _tariff("SME", "electricity") == "Standard Variable (Electricity)"


def test_meter_ic_is_hh():
    assert _meter("C_IC1", "I&C") == "HH"


def test_meter_reflects_real_smart_meter_status():
    """Was a hardcoded "always Smart" placeholder for every non-I&C
    customer (Rich-flagged 2026-07-09: let C1 show "Smart" on the site while
    its actual meter-read data behaved like a traditional meter). Now
    resolves the real per-customer status via saas.customers +
    simulation.meter_reads.meter_type_for_customer -- C1 is genuinely smart,
    C3 genuinely is not (saas/property_model.py's ASSET_PROFILE_BY_CUSTOMER)."""
    assert _meter("C1", "resi") == "Smart"
    assert _meter("C3", "resi") == "Traditional"


def test_meter_gas_twin_inherits_electricity_siblings_status():
    assert _meter("C1g", "resi") == "Smart"
    assert _meter("C3g", "resi") == "Traditional"


def test_meter_sme_without_known_profile_defaults_traditional():
    # C5/C6 (SME) have no ASSET_PROFILE_BY_CUSTOMER entry and no explicit
    # smart_meter/metering flag -- meter_type_for_customer's own documented
    # default applies.
    assert _meter("C5", "SME") == "Traditional"


def test_base_id_strips_gas_suffix():
    assert _base_id("C1g") == "C1"


def test_base_id_strips_ic_gas_suffix():
    assert _base_id("C_IC3g") == "C_IC3"


def test_base_id_no_suffix():
    assert _base_id("C1") == "C1"


def test_base_id_single_char():
    assert _base_id("g") == "g"


def test_tariff_unknown_segment_defaults_to_resi():
    result = _tariff("unknown", "electricity")
    assert isinstance(result, str)
    assert len(result) > 0


def test_meter_unknown_customer_defaults_to_traditional():
    result = _meter("unknown_customer_id", "resi")
    assert result == "Traditional"


def test_base_id_strips_trailing_g_only():
    assert _base_id("Cgg") == "Cg"


def test_mpan_bottom_line_is_11_digits():
    m = _mpan("C1", "resi")
    assert len(m["bottom_line"]) == 11
    assert m["bottom_line"].isdigit()


def test_mpan_top_line_is_7_digits():
    m = _mpan("C1", "resi")
    assert len(m["top_line"]) == 7


def test_mpan_deterministic():
    assert _mpan("C1", "resi") == _mpan("C1", "resi")


def test_mpan_differs_by_account():
    assert _mpan("C1", "resi") != _mpan("C2", "resi")


def test_mpan_ic_uses_profile_class_05():
    m = _mpan("C_IC1", "I&C")
    assert m["top_line"][:2] == "05"


def test_mpan_resi_uses_profile_class_01():
    m = _mpan("C1", "resi")
    assert m["top_line"][:2] == "01"


def test_mpan_check_digit_matches_published_algorithm():
    core = "00012345"
    weights = [3, 5, 7, 13, 17, 19, 23, 29]
    expected = str((sum(int(d) * w for d, w in zip(core, weights)) % 11) % 10)
    assert _mpan_check_digit(core) == expected


def test_mprn_is_8_digits():
    assert len(_mprn("C1g")) == 8
    assert _mprn("C1g").isdigit()


def test_mprn_deterministic():
    assert _mprn("C1g") == _mprn("C1g")


def test_timeline_merges_and_sorts_by_date():
    run = {
        "customer_events": [
            {"customer_id": "C1", "event_date": "2018-01-01", "commodity": "electricity",
             "event_type": "renewed", "unit_rate_gbp_per_mwh": 100.0},
            {"customer_id": "C1", "event_date": "2016-01-01", "commodity": "electricity",
             "event_type": "renewed", "unit_rate_gbp_per_mwh": 90.0},
        ],
        "per_customer_behavioral": {
            "C1": {"life_event_history": [{"date": "2017-01-01", "event_type": "new_baby"}]},
        },
    }
    tl = _timeline(run, "C1")
    assert [e["date"] for e in tl] == ["2016-01-01", "2017-01-01", "2018-01-01"]
    assert tl[1]["type"] == "life_event"
    assert tl[1]["detail"] == "New baby"


def test_timeline_includes_gas_twin_events():
    run = {
        "customer_events": [
            {"customer_id": "C1g", "event_date": "2019-01-01", "commodity": "gas",
             "event_type": "churned"},
        ],
        "per_customer_behavioral": {},
    }
    tl = _timeline(run, "C1")
    assert len(tl) == 1
    assert tl[0]["commodity"] == "gas"


def test_timeline_empty_when_no_data():
    assert _timeline({}, "C1") == []


class TestForecastCashflow:
    def test_zero_margin_returns_empty(self):
        assert _forecast_cashflow(0, 5.0, 0.10) == []

    def test_zero_lifetime_returns_empty(self):
        assert _forecast_cashflow(1000.0, 0, 0.10) == []

    def test_negative_lifetime_returns_empty(self):
        assert _forecast_cashflow(1000.0, -1.0, 0.10) == []

    def test_whole_year_lifetime_row_count(self):
        rows = _forecast_cashflow(1000.0, 3.0, 0.10)
        assert len(rows) == 3
        assert [r["year_offset"] for r in rows] == [1, 2, 3]

    def test_fractional_lifetime_rounds_up_row_count(self):
        rows = _forecast_cashflow(1000.0, 2.5, 0.10)
        assert len(rows) == 3

    def test_fractional_final_year_is_partial_weight(self):
        rows = _forecast_cashflow(1000.0, 2.5, 0.10)
        assert rows[0]["undiscounted_gbp"] == pytest.approx(1000.0)
        assert rows[1]["undiscounted_gbp"] == pytest.approx(1000.0)
        assert rows[2]["undiscounted_gbp"] == pytest.approx(500.0)

    def test_capped_at_ten_years(self):
        rows = _forecast_cashflow(1000.0, 25.0, 0.10)
        assert len(rows) == 10

    def test_discounted_less_than_undiscounted_for_positive_rate(self):
        rows = _forecast_cashflow(1000.0, 3.0, 0.10)
        for r in rows:
            assert r["discounted_gbp"] < r["undiscounted_gbp"]

    def test_discounted_sum_reconciles_with_clv_annuity(self):
        # Same math as saas/clv_model.py's annuity_factor -- the discounted
        # sum here should equal avg_annual_margin * annuity_factor(lifetime, rate).
        avg_margin = 1000.0
        lifetime = 4.0
        rate = 0.10
        rows = _forecast_cashflow(avg_margin, lifetime, rate)
        total_discounted = sum(r["discounted_gbp"] for r in rows)
        whole = int(lifetime)
        expected = sum(avg_margin / (1.0 + rate) ** k for k in range(1, whole + 1))
        assert total_discounted == pytest.approx(expected, abs=0.01)

    def test_later_years_discounted_less_than_earlier(self):
        rows = _forecast_cashflow(1000.0, 5.0, 0.10)
        discounted = [r["discounted_gbp"] for r in rows]
        assert discounted == sorted(discounted, reverse=True)


class TestAvgHedgeFractionThreadedIntoOutput:
    """2026-07-11, HARDEN sweep (harden_sweep:live_site:B3_hedge_tariff_alignment):
    avg_hedge_fraction was computed in per_customer_lifetime but never reached
    a per-customer site JSON file -- this proves the full thread."""

    def test_field_present_and_correct_when_computed(self, tmp_path, monkeypatch):
        run = {
            "per_customer_lifetime": {
                "C1": {
                    "segment": "resi", "commodity": "electricity",
                    "acquisition_date": "2016-01-01",
                    "revenue_gbp": 100.0, "gross_gbp": 20.0, "net_gbp": 15.0,
                    "cost_to_serve_gbp": 5.0, "pricing_action": "NONE",
                    "avg_hedge_fraction": 0.6667,
                },
            },
            "by_billing_account": {}, "per_cid_comm_pnl": {},
        }
        run_path = tmp_path / "run.json"
        run_path.write_text(json.dumps(run))
        out_dir = tmp_path / "out"
        monkeypatch.setattr(gcd_module, "OUT_DIR", out_dir)

        generate(run_json_path=run_path)

        obj = json.loads((out_dir / "C1.json").read_text())
        assert obj["avg_hedge_fraction"] == 0.6667

    def test_field_none_when_not_computed(self, tmp_path, monkeypatch):
        run = {
            "per_customer_lifetime": {
                "C1": {
                    "segment": "resi", "commodity": "electricity",
                    "acquisition_date": "2016-01-01",
                    "revenue_gbp": 100.0, "gross_gbp": 20.0, "net_gbp": 15.0,
                    "cost_to_serve_gbp": 5.0, "pricing_action": "NONE",
                    "avg_hedge_fraction": None,
                },
            },
            "by_billing_account": {}, "per_cid_comm_pnl": {},
        }
        run_path = tmp_path / "run.json"
        run_path.write_text(json.dumps(run))
        out_dir = tmp_path / "out"
        monkeypatch.setattr(gcd_module, "OUT_DIR", out_dir)

        generate(run_json_path=run_path)

        obj = json.loads((out_dir / "C1.json").read_text())
        assert obj["avg_hedge_fraction"] is None


class TestRetireDepartedArtefacts:
    """WORKER_FINDING_THE_PRINTED_FOOTING_CONTROL_RUNS_ON_A_SMALLER_POPULATION_THAN_THE_PAGE
    (2026-08-12): generate() wrote a file per account in the population and never removed
    the file of an account that LEFT it. The successor accounts C1_2/C2_2/C5_2 activate
    only when the predecessor churns and we win the home-mover competition; they
    activated in earlier runs and not in this one, so their artefacts stayed on the
    publish path -- fetchable, unrefreshed for 33-35 days, and still carrying pre-RJ
    fabricated invoice amounts in which 30 invoices did not foot.
    """

    def _populate(self, out_dir, accounts, index=None):
        out_dir.mkdir(parents=True, exist_ok=True)
        for a in accounts:
            (out_dir / (a + ".json")).write_text(json.dumps({"account_id": a}))
        (out_dir / "_index.json").write_text(json.dumps(index if index is not None else accounts))
        return out_dir

    def test_a_departed_account_loses_its_artefact(self, tmp_path, monkeypatch):
        out_dir = self._populate(tmp_path / "out", ["C1", "C2", "C2_2", "C5_2"])
        monkeypatch.setattr(gcd_module, "OUT_DIR", out_dir)

        retired = gcd_module._retire_departed_artefacts(["C1", "C2"])

        assert retired == ["C2_2", "C5_2"]
        assert not (out_dir / "C2_2.json").exists()
        assert not (out_dir / "C5_2.json").exists()

    def test_a_present_account_keeps_its_artefact(self, tmp_path, monkeypatch):
        out_dir = self._populate(tmp_path / "out", ["C1", "C2"])
        monkeypatch.setattr(gcd_module, "OUT_DIR", out_dir)

        assert gcd_module._retire_departed_artefacts(["C1", "C2"]) == []
        assert (out_dir / "C1.json").exists() and (out_dir / "C2.json").exists()

    def test_the_index_itself_is_never_retired(self, tmp_path, monkeypatch):
        out_dir = self._populate(tmp_path / "out", ["C1"])
        monkeypatch.setattr(gcd_module, "OUT_DIR", out_dir)

        gcd_module._retire_departed_artefacts(["C1"])

        assert (out_dir / "_index.json").exists()

    def test_an_empty_population_retires_nothing(self, tmp_path, monkeypatch):
        """Fails CLOSED: an empty run is a broken run, not an instruction to wipe the
        publish path. Without this, one bad run deletes every published account."""
        out_dir = self._populate(tmp_path / "out", ["C1", "C2", "C3"])
        monkeypatch.setattr(gcd_module, "OUT_DIR", out_dir)

        assert gcd_module._retire_departed_artefacts([]) == []
        assert len(list(out_dir.glob("*.json"))) == 4

    def test_generate_retires_a_departed_account_end_to_end(self, tmp_path, monkeypatch):
        """The finding's own shape: an artefact present on disk, absent from the run."""
        run = {
            "per_customer_lifetime": {
                "C1": {
                    "segment": "resi", "commodity": "electricity",
                    "acquisition_date": "2016-01-01",
                    "revenue_gbp": 100.0, "gross_gbp": 20.0, "net_gbp": 15.0,
                    "cost_to_serve_gbp": 5.0, "pricing_action": "NONE",
                },
            },
            "by_billing_account": {}, "per_cid_comm_pnl": {},
        }
        run_path = tmp_path / "run.json"
        run_path.write_text(json.dumps(run))
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        (out_dir / "C1_2.json").write_text(json.dumps({"account_id": "C1_2"}))
        monkeypatch.setattr(gcd_module, "OUT_DIR", out_dir)

        generate(run_json_path=run_path)

        assert not (out_dir / "C1_2.json").exists(), (
            "a departed account's artefact survived a full generate() -- the finding's defect"
        )
        assert (out_dir / "C1.json").exists()
        assert json.loads((out_dir / "_index.json").read_text()) == ["C1"]


class TestForwardLookingAttribution:
    """W2_17_dual_fuel_leg_clv_attribution: all five published gas accounts (C1g, C2g,
    C3g, C4g, C_IC3g) carried clv_gbp 0, churn_probability 0, expected_lifetime_periods 0
    and forecast_annual_profit_gbp 0, beside electricity legs carrying real values -- so
    the published record could not distinguish a MEASURED zero from a field that was never
    populated, and the site rendered a structural blank as a company belief about half of
    every dual-fuel household.

    CLV and churn are billing-account quantities (saas.clv_model.build_clv sums both legs'
    net margin under saas.customer_reaction._billing_account_id), so the gas leg's value is
    already inside its electricity sibling's figure. The fix publishes null and names the
    account that carries it, rather than fabricating a zero.
    """

    def _run(self, bba, pcl_extra=None):
        pcl = {
            "C1": {
                "segment": "resi", "commodity": "electricity",
                "acquisition_date": "2016-01-01",
                "revenue_gbp": 100.0, "gross_gbp": 20.0, "net_gbp": 15.0,
                "cost_to_serve_gbp": 5.0, "pricing_action": "NONE",
            },
            "C1g": {
                "segment": "resi", "commodity": "gas",
                "acquisition_date": "2016-01-01",
                "revenue_gbp": 60.0, "gross_gbp": 12.0, "net_gbp": 9.0,
                "cost_to_serve_gbp": 3.0, "pricing_action": "NONE",
            },
        }
        pcl.update(pcl_extra or {})
        return {"per_customer_lifetime": pcl, "by_billing_account": bba,
                "per_cid_comm_pnl": {}}

    def _generate(self, run, tmp_path, monkeypatch):
        run_path = tmp_path / "run.json"
        run_path.write_text(json.dumps(run))
        out_dir = tmp_path / "out"
        monkeypatch.setattr(gcd_module, "OUT_DIR", out_dir)
        generate(run_json_path=run_path)
        return lambda cid: json.loads((out_dir / (cid + ".json")).read_text())

    _VALUED = {"C1": {"clv_gbp": 2840.5, "latest_churn_probability": 0.23,
                      "expected_lifetime_periods": 14.94,
                      "avg_annual_net_margin_gbp": 374.18}}

    # --- direction 1: the blank is published as a blank, and says where the value went

    def test_a_gas_leg_publishes_null_not_zero(self, tmp_path, monkeypatch):
        """THE finding. Every forward-looking field on the gas leg is null -- 0 was a
        company belief the company does not hold."""
        read = self._generate(self._run(self._VALUED), tmp_path, monkeypatch)
        gas = read("C1g")
        blank = {k: gas[k] for k in ("clv_gbp", "churn_probability",
                                     "expected_lifetime_periods",
                                     "forecast_annual_profit_gbp")}
        assert all(v is None for v in blank.values()), (
            f"the gas leg still publishes fabricated figures {blank} -- a reader cannot "
            "tell these from a household measured to be worth nothing"
        )
        assert gas["forecast_cashflow"] == []

    def test_a_gas_leg_names_the_account_that_carries_its_value(self, tmp_path, monkeypatch):
        """A null alone still does not tell the reader the value EXISTS, on the sibling
        leg. Without this, the fix trades a false zero for an unexplained gap."""
        gas = self._generate(self._run(self._VALUED), tmp_path, monkeypatch)("C1g")
        assert gas["forward_looking_basis"] == gcd_module.BASIS_BILLING_ACCOUNT
        assert gas["forward_looking_account_id"] == "C1"

    def test_an_account_with_no_billing_row_is_distinguishable_from_a_gas_leg(
            self, tmp_path, monkeypatch):
        """SYN-2021-001's real shape: in per_customer_lifetime, absent from
        by_billing_account. It is blank for a DIFFERENT reason than a gas leg, and
        collapsing the two loses the reason."""
        extra = {"SYN-2021-001": {
            "segment": "resi", "commodity": "electricity",
            "acquisition_date": "2021-01-01",
            "revenue_gbp": 10.0, "gross_gbp": 2.0, "net_gbp": 1.0,
            "cost_to_serve_gbp": 1.0, "pricing_action": "NONE"}}
        read = self._generate(self._run(self._VALUED, extra), tmp_path, monkeypatch)
        syn = read("SYN-2021-001")
        assert syn["clv_gbp"] is None
        assert syn["forward_looking_basis"] == gcd_module.BASIS_NO_BILLING_ACCOUNT
        assert syn["forward_looking_basis"] != read("C1g")["forward_looking_basis"]

    def test_an_unmodelled_clv_keeps_the_churn_belief_it_really_has(
            self, tmp_path, monkeypatch):
        """build_clv excludes accounts with no renewal points, and accounts the caller
        reports as no longer supplied, while churn_model still records their churn belief
        -- the live run's C1/C3/C4/C5/C6 shape. Blanking the whole record on a null CLV
        would delete a belief the company genuinely holds."""
        bba = {"C1": {"clv_gbp": None, "expected_lifetime_periods": None,
                      "avg_annual_net_margin_gbp": None,
                      "latest_churn_probability": 0.23}}
        elec = self._generate(self._run(bba), tmp_path, monkeypatch)("C1")
        assert elec["forward_looking_basis"] == gcd_module.BASIS_ACCOUNT
        assert elec["clv_gbp"] is None
        assert elec["expected_lifetime_periods"] is None
        assert elec["churn_probability"] == 0.23, (
            "the churn belief was blanked along with the unmodelled CLV -- these are "
            "separate figures with separate provenance"
        )

    def test_a_null_clv_row_does_not_crash_the_generator(self, tmp_path, monkeypatch):
        """The live defect this fix also closes: by_billing_account rows carry
        `clv_gbp: null` for every excluded account, and `round(None, 2)` raised
        TypeError -- generate() could not run at all against the current run output,
        which is why the published artefacts were stale."""
        bba = {"C1": {"clv_gbp": None, "expected_lifetime_periods": None,
                      "avg_annual_net_margin_gbp": None,
                      "latest_churn_probability": 0.23}}
        read = self._generate(self._run(bba), tmp_path, monkeypatch)
        assert read("C1")["forecast_cashflow"] == []

    # --- direction 2: a value that WAS computed still publishes, including a real zero

    def test_a_valued_electricity_leg_still_publishes_its_figures(
            self, tmp_path, monkeypatch):
        """Inverse. An 'always null' generator would satisfy every test above while
        deleting the company's entire lifetime-value book."""
        elec = self._generate(self._run(self._VALUED), tmp_path, monkeypatch)("C1")
        assert elec["forward_looking_basis"] == gcd_module.BASIS_ACCOUNT
        assert elec["forward_looking_account_id"] == "C1"
        assert elec["clv_gbp"] == 2840.5
        assert elec["churn_probability"] == 0.23
        assert elec["expected_lifetime_periods"] == 14.94
        assert elec["forecast_annual_profit_gbp"] == 374.18
        assert elec["forecast_cashflow"], "a valued account lost its cashflow forecast"

    def test_a_measured_zero_is_published_as_zero_not_as_a_blank(
            self, tmp_path, monkeypatch):
        """The distinction the finding is ABOUT, in the direction that is easy to lose.
        An account the model really valued at zero must publish 0.0 under
        BASIS_ACCOUNT. Both `round(row.get(k, 0), n)` (the original defect) and any
        `row.get(k) or None` rewrite fail this: the first cannot represent the blank,
        the second cannot represent the zero."""
        bba = {"C1": {"clv_gbp": 0.0, "expected_lifetime_periods": 0.0,
                      "avg_annual_net_margin_gbp": 0.0,
                      "latest_churn_probability": 0.0}}
        elec = self._generate(self._run(bba), tmp_path, monkeypatch)("C1")
        assert elec["forward_looking_basis"] == gcd_module.BASIS_ACCOUNT
        assert elec["clv_gbp"] == 0.0 and elec["clv_gbp"] is not None
        assert elec["expected_lifetime_periods"] == 0.0
        assert elec["forecast_annual_profit_gbp"] == 0.0
        assert elec["churn_probability"] == 0.0

    def test_every_record_carries_a_basis(self, tmp_path, monkeypatch):
        """No record may be silent about which account its figures belong to -- a
        missing basis reads as 'account of record' to any consumer using .get()."""
        read = self._generate(self._run(self._VALUED), tmp_path, monkeypatch)
        for cid in ("C1", "C1g"):
            assert read(cid)["forward_looking_basis"] in (
                gcd_module.BASIS_ACCOUNT, gcd_module.BASIS_BILLING_ACCOUNT,
                gcd_module.BASIS_NO_BILLING_ACCOUNT)


def test_base_id_agrees_with_the_clv_models_own_billing_account_rule():
    """_base_id decides which records are attributed away; saas.clv_model keys the value
    it attributes them TO. If the two rules ever disagree, this generator would blank a
    leg whose value was never folded into any sibling -- the finding's defect, silently
    restored. A comment asserting the two agree is not a mechanism; this is."""
    from saas.customer_reaction import _billing_account_id
    population = ["C1", "C1g", "C2", "C2g", "C3", "C3g", "C4", "C4g", "C5", "C6",
                  "C7", "C8", "C9", "C_IC1", "C_IC2", "C_IC3", "C_IC3g", "C_IC4",
                  "SYN-2021-001", "C1_2", "C2_2", "C5_2"]
    disagree = [c for c in population if _base_id(c) != _billing_account_id(c)]
    assert not disagree, (
        f"_base_id and saas.customer_reaction._billing_account_id disagree on {disagree} "
        "-- the generator would attribute a leg's value to an account that never received it"
    )
