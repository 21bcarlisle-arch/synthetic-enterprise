"""Controls over the by-episode price shape instrument and the cap unit-rate composition reader.

Each test is named for the defect it exists to catch. The fixtures are SYNTHETIC on purpose: the
Elexon MID caches and the Ofgem cap level workbooks are both gitignored source data, so a suite that
reached for them would pass vacuously in every clean worktree extract and every mutation of these
modules would survive. The tests that do touch the live tree skip EXPLICITLY when the data is
absent, and say so, rather than going quiet.
"""
from __future__ import annotations

import json

import pytest

from tools.ofgem_cap_unit_rate_composition import (
    CAP_IN_FORCE_FROM,
    CROSS_CHECK_TOLERANCE,
    VAT_MULTIPLIER,
    CapModelUnavailable,
    _period_start,
    cross_check,
    latest_model,
)
from tools.tou_price_shape_episode import (
    EPISODES,
    EpisodeUnavailable,
    arc_response,
    attribute,
    cap_share_by_period,
    share_for,
    verdict,
)

#: The Arcturus 2.0 primary specification, as the landed artefact carries it. Restated here so a
#: mutation of the module's reading is caught against the PAPER, not against whatever the module
#: happens to load today.
PRIMARY = {"constant": -0.011, "ln_price_ratio": -0.065, "ln_price_ratio_x_technology": -0.046}
OPT_OUT = {"constant": -0.028, "ln_price_ratio": -0.058, "ln_price_ratio_x_technology": -0.047,
           "opt_out_binary": 0.039}


class TestTheArcReader:
    """If the arc is misread, every response figure downstream is wrong and none of it looks it."""

    @pytest.mark.parametrize("ratio,tech,expected", [
        (2, False, 0.0561), (4, False, 0.1011), (2, True, 0.0879), (4, True, 0.1649),
    ])
    def test_it_reproduces_the_papers_own_four_stated_points(self, ratio, tech, expected):
        """Faruqui & Sergici state these four in prose: at 2:1 households 'consume 95%', at 4:1
        '90%', and with enabling technology '91%' and '84%'. A reader that flipped a sign, dropped
        the technology interaction or used the opt-out column would miss at least one."""
        assert arc_response(ratio, PRIMARY, opt_out=False, tech=tech) == pytest.approx(
            expected, abs=0.0005)

    def test_the_opt_out_penalty_reduces_the_response_and_does_not_raise_it(self):
        """+0.039 is percentage points of peak usage RETAINED. A reader that added it to the
        reduction instead of subtracting would make opt-out households look MORE responsive than
        volunteers, which is backwards and would flatter every figure this book publishes."""
        volunteers = arc_response(2.88, PRIMARY, opt_out=False)
        moved_book = arc_response(2.88, OPT_OUT, opt_out=True)
        assert moved_book < volunteers
        assert moved_book == pytest.approx(0.050, abs=0.0005)
        assert volunteers == pytest.approx(0.080, abs=0.0005)

    def test_the_intercept_survives_a_flat_price_and_that_is_an_artefact_not_a_response(self):
        """PINS A KNOWN ARTEFACT SO IT CANNOT BE MISTAKEN FOR A RESULT. The primary specification's
        constant is -0.011, so at a ratio of exactly 1:1 -- no price difference at all -- the arc
        returns a 1.1% peak reduction. That is a regression intercept fitted over a sample starting
        at 2:1, and any company value read at zero pass-through is reading it rather than a
        response. The opt-out column happens to clip to zero instead, which is a coincidence of two
        published coefficients and not a design; both are pinned so neither drifts unnoticed."""
        assert arc_response(1.0, PRIMARY, opt_out=False) == pytest.approx(0.011, abs=1e-9)
        assert arc_response(1.0, OPT_OUT, opt_out=True) == 0.0

    def test_a_dearer_off_peak_window_clips_to_zero_rather_than_a_negative_response(self):
        """Below a ratio of about 0.84 the raw expression goes negative. Publishing a negative
        reduction as a response would put a value-DESTROYING tariff on the sharing frontier and it
        would look like an ordinary small number on the way past."""
        assert arc_response(0.5, PRIMARY, opt_out=False) == 0.0

    def test_the_response_rises_with_the_ratio(self):
        """The whole claim of the instrument is that a wider price ratio buys more shifting. A
        sign error on ln_price_ratio would invert it and still return plausible small numbers."""
        values = [arc_response(r, PRIMARY, opt_out=False) for r in (1.5, 2.0, 3.0, 5.0, 10.0)]
        assert values == sorted(values)
        assert values[0] < values[-1]

    def test_a_non_positive_ratio_refuses_rather_than_raising_a_bare_math_error(self):
        assert isinstance(pytest.raises(EpisodeUnavailable,
                                        arc_response, 0.0, PRIMARY, False).value,
                          EpisodeUnavailable)


class TestTheCommodityShareSchedule:
    """`s` is a step function of the cap period. Getting the lookup wrong silently reprices
    every day in the panel."""

    SCHEDULE = [("2019-01-01", 0.44, True), ("2021-04-01", 0.42, True),
                ("2023-01-01", 0.81, True)]

    def test_a_date_inside_a_period_takes_that_periods_share_not_the_next_ones(self):
        """A lookup that rounded forward instead of back would apply January 2023's crisis share
        to days in 2021, which is the single biggest lever on the faced ratio in this whole book."""
        assert share_for("2021-06-15", self.SCHEDULE)[0] == 0.42
        assert share_for("2022-12-31", self.SCHEDULE)[0] == 0.42
        assert share_for("2023-01-01", self.SCHEDULE)[0] == 0.81

    def test_it_is_a_step_and_never_interpolated(self):
        """A cap period's allowance applies to the whole period and changes on its boundary.
        Interpolating would invent a share the law never carried on any day."""
        assert share_for("2021-04-01", self.SCHEDULE)[0] == 0.42
        assert share_for("2022-11-30", self.SCHEDULE)[0] == 0.42

    def test_a_date_before_every_published_period_is_flagged_as_not_the_law(self):
        """THE RARE BRANCH, asserted reachable before it is asserted correct. Days before the cap
        existed can only rest on Ofgem's own back-cast; a lookup that returned in_force=True there
        would let a suite claim the whole panel rests on published law when part of it does not."""
        share, in_force = share_for("2016-09-12", self.SCHEDULE)
        assert share == 0.44
        assert in_force is False

    def test_both_legs_of_the_in_force_partition_are_reachable(self):
        """A guard that answered False for every date would pass every test above that only
        checks the back-cast leg. One control over the whole partition."""
        mixed = [("2016-01-01", 0.37, False), ("2019-01-01", 0.44, True)]
        assert share_for("2016-06-01", mixed)[1] is False
        assert share_for("2020-06-01", mixed)[1] is True

    def test_an_empty_schedule_refuses_rather_than_defaulting_a_share(self):
        """A default `s` invented here would be exactly the picked-number failure the artefact
        this reads was built to end."""
        with pytest.raises(EpisodeUnavailable):
            cap_share_by_period({"by_payment_method": {"direct_debit": {"periods": []}}})


class TestTheCapPeriodParser:
    def test_it_parses_both_dash_forms_ofgem_uses(self):
        """The model mixes a hyphen and an en dash between the two dates. A parser that handled
        only one would silently drop every period using the other, and the cross-check would then
        pass on a subset nobody declared."""
        assert _period_start("April 2015 – September 2015") == "2015-04-01"
        assert _period_start("October 2022 - December 2022") == "2022-10-01"
        assert _period_start("January 2023 - March 2023") == "2023-01-01"

    def test_a_non_period_label_returns_none_rather_than_a_wrong_date(self):
        assert _period_start("Charging year:") is None
        assert _period_start("2023") is None

    def test_the_in_force_boundary_is_the_date_the_cap_actually_started(self):
        """Ofgem's model carries pre-2019 columns it labels 'for illustration only', several of
        which fall below 0.40. Treating them as cap periods would make the headline claim false in
        the FLATTERING direction, which is the direction that never gets caught by reading."""
        assert _period_start("October 2016-March 2017") < CAP_IN_FORCE_FROM
        assert _period_start("January 2019 - March 2019") >= CAP_IN_FORCE_FROM


class TestTheCrossCheckCanFail:
    """The cross-check is the only evidence the benchmark-minus-nil decomposition is right. A
    check that cannot fail is worth nothing, so its failure is what is tested."""

    def test_a_decomposition_that_misses_the_published_level_refuses_to_publish(self):
        """Mutating the subtraction, the benchmark kWh or the component set would move the derived
        unit rate away from Ofgem's published headline. This is the control that notices."""
        wrong = [{"cap_period": "October 2021 - March 2022", "starts": "2021-10-01",
                  "unit_rate_p_per_kwh_ex_vat": 40.0}]
        with pytest.raises(CapModelUnavailable, match="published cap level"):
            cross_check(wrong)

    def test_a_correct_decomposition_passes_the_same_check(self):
        """The other leg of the partition. A cross-check that refused everything would pass the
        test above while making the tool permanently unable to publish anything."""
        published = json.loads(
            (__import__("pathlib").Path("docs/domain_artefact_library/regulatory"
                                        "/ofgem_default_tariff_cap_windows.json")).read_text())
        window = next(w for w in published["windows"] if w["from"] == "2021-10-01")
        derived = window["elec"] / 10.0 / VAT_MULTIPLIER
        result = cross_check([{"cap_period": "October 2021 - March 2022", "starts": "2021-10-01",
                               "unit_rate_p_per_kwh_ex_vat": derived}])
        assert result["periods_checked"] == 1
        assert result["worst_relative_error"] < CROSS_CHECK_TOLERANCE

    def test_no_matchable_period_refuses_rather_than_reporting_a_vacuous_pass(self):
        """Zero periods checked is 'measured nothing', not 'measured, found nothing wrong'. A
        cross-check that returned a clean result on an empty match set is the fail-open."""
        with pytest.raises(CapModelUnavailable, match="no cap period"):
            cross_check([{"cap_period": "April 2099 - September 2099", "starts": "2099-04-01",
                          "unit_rate_p_per_kwh_ex_vat": 20.0}])


class TestTheVerdictIsKeyedToThePropertyNotTodaysAnswer:
    """A verdict pinned to the number we measured today goes red when the code becomes more
    honest and stays green when the claim rots. It is keyed to the evidence floor instead."""

    @staticmethod
    def _episode(median: float, faced: float, level: float) -> dict:
        return {"available": True,
                "raw_price_shape": {"within_day_wholesale_ratio": {"median": median},
                                    "level_mean_day_price_gbp_per_mwh": level},
                "faced_ratio_and_response": [{"alpha": 1.00, "faced_ratio_p50": faced}]}

    def test_a_faced_ratio_below_the_evidence_floor_does_not_reach_it(self):
        answer = verdict(self._episode(1.77, 1.28, 44.7), self._episode(1.79, 1.40, 135.9), 2.0)
        assert answer["answer"] == "DOES NOT REACH THE EVIDENCE RANGE"

    def test_a_faced_ratio_above_the_evidence_floor_DOES_reach_it(self):
        """THE BRANCH THAT HAS NEVER FIRED ON REAL DATA, asserted reachable. A verdict that
        answered 'does not reach' unconditionally would pass the test above and would go on
        passing it after the market changed enough to make the product real."""
        answer = verdict(self._episode(1.77, 1.28, 44.7), self._episode(4.10, 2.60, 135.9), 2.0)
        assert answer["answer"] == "REACHES THE EVIDENCE RANGE"

    def test_an_unavailable_episode_says_unmeasured_rather_than_not_reached(self):
        """'We could not measure' and 'we measured and it fell short' are opposite claims, and
        collapsing them is how an absence of data comes to read as a finding about the market."""
        answer = verdict(self._episode(1.77, 1.28, 44.7),
                         {"available": False, "why": "no days"}, 2.0)
        assert answer["answer"] == "UNMEASURED"


class TestTheAttributionSeparatesLevelFromAmplitude:
    """The whole finding rests on this split. If it were wrong, a level event would be published
    as a change in the price shape — this project's most expensive recurring mistake."""

    @staticmethod
    def _days(shape_peak: float, shape_off: float, years: tuple[str, ...]) -> dict:
        out = {}
        for year in years:
            for day in range(1, 29):
                base = [10.0] * 48
                for period in range(34, 40):
                    base[period] = 10.0 * shape_peak
                for period in range(0, 6):
                    base[period] = 10.0 * shape_off
                out[f"{year}-01-{day:02d}"] = base
        return out

    def test_scaling_every_price_by_a_constant_leaves_the_attribution_unmoved(self):
        """A LEVEL event. The ratio is scale-free, so tripling every half hour must move the
        faced ratio by exactly nothing. An instrument that reported a shape change here would
        have published the gas crisis as a change in the shape of the day."""
        flat = self._days(1.6, 0.6, EPISODES[0][1])
        tripled = {d: [p * 3.0 for p in v] for d, v in self._days(1.6, 0.6, EPISODES[1][1]).items()}
        schedule = [("2015-01-01", 0.5, True)]
        result = attribute({**flat, **tripled}, 6, schedule)
        assert result["available"]
        assert result["measured_2021_2023"] == pytest.approx(result["baseline_2016_2020"], abs=1e-6)
        assert result["new_shape_with_old_commodity_share"] == pytest.approx(
            result["baseline_2016_2020"], abs=1e-6)

    def test_a_genuinely_wider_shape_does_move_the_shape_column(self):
        """The other leg. An attribution that returned 'the shape did nothing' for every input
        would pass the test above and would have been the finding regardless of the data."""
        narrow = self._days(1.2, 0.9, EPISODES[0][1])
        wide = self._days(2.5, 0.4, EPISODES[1][1])
        result = attribute({**narrow, **wide}, 6, [("2015-01-01", 0.5, True)])
        assert result["new_shape_with_old_commodity_share"] > result["baseline_2016_2020"] * 1.1

    def test_a_higher_commodity_share_alone_moves_the_share_column(self):
        """The third leg: same shape both sides, different `s`. This is the one that actually
        fired on the real data, and a control that could not distinguish it from the shape column
        would have let the finding attribute the move to the wrong cause."""
        same = {**self._days(1.6, 0.6, EPISODES[0][1]), **self._days(1.6, 0.6, EPISODES[1][1])}
        schedule = [("2015-01-01", 0.40, True), ("2021-01-01", 0.80, True)]
        result = attribute(same, 6, schedule)
        assert result["commodity_share_2021_2023"] > result["commodity_share_2016_2020"]
        assert result["old_shape_with_new_commodity_share"] > result["baseline_2016_2020"] * 1.05
        assert result["new_shape_with_old_commodity_share"] == pytest.approx(
            result["baseline_2016_2020"], abs=1e-6)


class TestItFailsClosedWhereTheDataIsGitignored:
    """An instrument that goes quiet where its data is absent reports 'measured nothing' as
    'measured, found nothing'. Those are opposite claims."""

    def test_the_cap_model_reader_refuses_when_the_workbooks_are_absent(self, monkeypatch, tmp_path):
        monkeypatch.setattr("tools.ofgem_cap_unit_rate_composition.MODEL_DIR", tmp_path / "gone")
        with pytest.raises(CapModelUnavailable, match="NOT a finding"):
            latest_model()

    def test_an_unversioned_workbook_directory_refuses_rather_than_picking_arbitrarily(
            self, monkeypatch, tmp_path):
        """Choosing by mtime would mean a cache refetched in a different order silently changed
        which version of the law was read."""
        (tmp_path / "something.xlsx").write_bytes(b"")
        monkeypatch.setattr("tools.ofgem_cap_unit_rate_composition.MODEL_DIR", tmp_path)
        with pytest.raises(CapModelUnavailable, match="no versioned"):
            latest_model()

    def test_the_price_reader_refuses_when_no_mid_cache_is_present(self, monkeypatch, tmp_path):
        from tools import tou_price_shape_episode as module
        monkeypatch.setattr(module, "CACHE_DIR", tmp_path)
        with pytest.raises(EpisodeUnavailable, match="NOT a finding"):
            module.load_prices()


class TestAgainstTheLiveTreeWhenItsDataIsPresent:
    """These skip explicitly rather than going quiet — a silent skip is how a suite comes to
    report a pass over data it never read."""

    def test_the_landed_panel_is_reproduced_by_this_code_path(self):
        """THE CONTROL THAT LICENSES THE WHOLE COMPARISON. The 2016-2020 episode is re-measured
        here rather than quoted from the landed artefact; if the two disagree, the new episodes are
        a different construction sharing a name with the old one and the comparison is void."""
        from pathlib import Path
        artefact = Path("docs/observability/tou_price_shape_by_episode.json")
        landed = Path("docs/observability/tou_sharing_ceiling.json")
        if not artefact.exists() or not landed.exists():
            pytest.skip("the episode artefact or the landed ceiling is absent from this tree")
        episodes = json.loads(artefact.read_text())["episodes"]
        panel = next(e for e in episodes if e["episode"] == "2016-2020")
        ceiling = json.loads(landed.read_text())
        assert panel["raw_price_shape"]["days"] == ceiling["price_series"]["days"]
        assert panel["raw_price_shape"]["created_value_gbp_per_household_year"] == pytest.approx(
            ceiling["created_value"]["gbp_per_household_year"], abs=0.02)

    def test_the_published_commodity_share_is_above_the_landed_bridges_best_supported_row(self):
        """The landed bridge called s = 0.40 best-supported and predicted from the denominators
        that the true value was higher. This control is keyed to that PROPERTY, not to today's
        0.408 — it stays meaningful if Ofgem republishes and the number moves."""
        from pathlib import Path
        path = Path("docs/domain_artefact_library/regulatory/ofgem_cap_unit_rate_composition.json")
        if not path.exists():
            pytest.skip("the cap unit-rate composition artefact is absent from this tree")
        headline = json.loads(path.read_text())["headline"]
        assert headline["min_share"] > 0.40
        assert headline["max_share"] > headline["min_share"], "s would not be a range at all"
