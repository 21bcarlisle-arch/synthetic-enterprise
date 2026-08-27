"""The embedded-generation adapter's controls, and the defect each one names.

The defect this file exists for was REAL and was caught by a population count, not by reasoning:
NESO publishes SETTLEMENT_DATE in three different forms across the per-year resources of ONE
dataset, an ISO-only reader silently dropped five years of eight, and the fetch log still said
17,520 records for every one of them because it counted RAW rows one layer upstream of the loss.
Every test here is aimed at that class rather than at the instance.
"""

from __future__ import annotations

import json

import pytest

from sim import neso_embedded_generation as embedded


class TestTheThreeDateFormats:
    """All three forms NESO actually publishes, measured from the pinned resources."""

    def test_iso_form_2018_2024_2025(self):
        assert embedded._normalise_date("2018-01-01", "2018") == "2018-01-01"

    def test_upper_case_four_digit_year_form_2019_to_2022(self):
        assert embedded._normalise_date("01-JAN-2019", "2019") == "2019-01-01"
        assert embedded._normalise_date("28-FEB-2020", "2020") == "2020-02-28"

    def test_two_digit_year_form_2023(self):
        assert embedded._normalise_date("01-Jan-23", "2023") == "2023-01-01"
        assert embedded._normalise_date("31-Dec-23", "2023") == "2023-12-31"

    def test_a_naive_ten_character_slice_would_have_corrupted_not_dropped(self):
        """THE REASON THE REFUSAL MATTERED. `'01-JAN-2019'[:10]` is `'01-JAN-201'` -- a
        plausible-looking key that joins to nothing. A reader that truncated instead of refusing
        would have produced a full-length series with zero overlap against demand, and the
        measurement downstream would have reported an honest-looking answer on an empty join."""
        assert "01-JAN-2019"[:10] == "01-JAN-201"
        assert embedded._normalise_date("01-JAN-2019", "2019") == "2019-01-01"


class TestTheResourceYearIsAControlNotJustAHint:
    """The check that would catch NESO re-pointing a resource, or the pinned ids drifting."""

    def test_a_record_whose_year_disagrees_with_its_resource_is_refused(self):
        # The exact shape of a re-pointed resource: real, well-formed, and from the wrong year.
        assert embedded._normalise_date("01-JAN-2019", "2023") is None

    def test_a_two_digit_year_disagreeing_with_its_resource_is_refused(self):
        assert embedded._normalise_date("01-Jan-23", "2019") is None

    def test_a_two_digit_year_with_no_resource_label_is_refused_not_guessed(self):
        """No pivot-year heuristic. A guess that is right for this decade and silently wrong
        later is the same class of defect as the format drift it would be absorbing."""
        assert embedded._normalise_date("01-Jan-23", None) is None

    def test_an_unknown_month_is_refused(self):
        assert embedded._normalise_date("01-XXX-2019", "2019") is None

    def test_an_impossible_month_is_refused(self):
        assert embedded._normalise_date("2019-13-01", "2019") is None


class TestMissingIsNotZero:
    """The fail-open shape: 'we did not look' and 'nothing was generated' must not share a bin."""

    def _record(self, **overrides):
        base = {
            "SETTLEMENT_DATE": "2024-06-01",
            "SETTLEMENT_PERIOD": 25,
            "EMBEDDED_WIND_GENERATION": 1000,
            "EMBEDDED_SOLAR_GENERATION": 2000,
            "EMBEDDED_WIND_CAPACITY": 6000,
            "EMBEDDED_SOLAR_CAPACITY": 16000,
            "_resource_year": "2024",
        }
        base.update(overrides)
        return base

    def test_a_present_reading_is_kept(self):
        series = embedded.to_settlement_periods([self._record()])
        assert series[("2024-06-01", 25)]["total_mw"] == 3000.0

    def test_an_absent_reading_is_dropped_not_zeroed(self):
        series = embedded.to_settlement_periods(
            [self._record(EMBEDDED_SOLAR_GENERATION=None)]
        )
        assert series == {}

    def test_a_genuine_zero_is_kept(self):
        """Night. A real reading of zero is data and must survive, which is precisely what
        makes dropping the ABSENT one load-bearing rather than pedantic."""
        series = embedded.to_settlement_periods(
            [self._record(EMBEDDED_SOLAR_GENERATION=0)]
        )
        assert series[("2024-06-01", 25)]["total_mw"] == 1000.0

    def test_a_negative_model_artefact_is_clamped_to_zero(self):
        series = embedded.to_settlement_periods(
            [self._record(EMBEDDED_WIND_GENERATION=-5)]
        )
        assert series[("2024-06-01", 25)]["wind_mw"] == 0.0

    def test_an_out_of_range_period_is_refused(self):
        assert embedded.to_settlement_periods([self._record(SETTLEMENT_PERIOD=99)]) == {}


class TestTheCoverageControlFiresOnItsOwnNamedDefect:
    """R15 MUTATION: restore the ISO-only reader and the per-year population check must FAIL.

    This is the control that would have caught the real incident. It is exercised by putting the
    defect back rather than by asserting that the fixed code works.
    """

    def _rows(self, date_form: str, year: str) -> list[dict]:
        return [
            {
                "SETTLEMENT_DATE": date_form,
                "SETTLEMENT_PERIOD": p,
                "EMBEDDED_WIND_GENERATION": 100,
                "EMBEDDED_SOLAR_GENERATION": 50,
                "EMBEDDED_WIND_CAPACITY": 6000,
                "EMBEDDED_SOLAR_CAPACITY": 16000,
                "_resource_year": year,
            }
            for p in (1, 2, 3)
        ]

    def test_the_shipped_reader_parses_the_non_iso_year(self):
        assert len(embedded.to_settlement_periods(self._rows("01-JAN-2019", "2019"))) == 3

    def test_an_iso_only_reader_yields_zero_periods_from_rows_that_fetched_fine(
        self, monkeypatch
    ):
        """THE MUTATION. The rows fetch; a raw-record count reports 3; the parsed count is 0.
        That gap is exactly what the shipped `main` now refuses to cache over."""

        def iso_only(raw, resource_year=None):
            text = str(raw).strip()
            if len(text) >= 10 and text[4] == "-" and text[7] == "-":
                return text[:10]
            return None

        monkeypatch.setattr(embedded, "_normalise_date", iso_only)
        rows = self._rows("01-JAN-2019", "2019")
        assert len(rows) == 3
        assert embedded.to_settlement_periods(rows) == {}

    def test_main_refuses_to_cache_a_year_that_parsed_to_nothing(
        self, monkeypatch, tmp_path
    ):
        """FAIL-CLOSED, and on the real entry point rather than on a helper."""

        def iso_only(raw, resource_year=None):
            text = str(raw).strip()
            if len(text) >= 10 and text[4] == "-" and text[7] == "-":
                return text[:10]
            return None

        monkeypatch.setattr(embedded, "_normalise_date", iso_only)
        monkeypatch.setattr(embedded, "CACHE_PATH", tmp_path / "cache.json")
        monkeypatch.setattr(
            embedded, "fetch_year", lambda year, **kw: self._rows("01-JAN-2019", year)
        )
        with pytest.raises(SystemExit) as caught:
            embedded.main(["2019"])
        assert "REFUSING TO CACHE" in str(caught.value)
        assert not (tmp_path / "cache.json").exists()

    def test_main_caches_when_every_requested_year_parses(self, monkeypatch, tmp_path):
        """THE OTHER SIDE OF THE MUTATION -- a control that only ever refuses is not a control."""
        monkeypatch.setattr(embedded, "CACHE_PATH", tmp_path / "cache.json")
        monkeypatch.setattr(
            embedded, "fetch_year", lambda year, **kw: self._rows("01-JAN-2019", year)
        )
        assert embedded.main(["2019"]) == 0
        written = json.loads((tmp_path / "cache.json").read_text())
        assert len(written) == 3


class TestUnavailableIsNotZero:
    def test_a_missing_cache_raises_rather_than_returning_empty(self, tmp_path):
        with pytest.raises(embedded.EmbeddedGenerationUnavailable):
            embedded.load_cached(tmp_path / "absent.json")

    def test_an_unpinned_year_raises_rather_than_fetching_nothing(self):
        with pytest.raises(embedded.EmbeddedGenerationUnavailable):
            embedded.fetch_year("1999")


class TestTheRealCacheCarriesEveryYearItClaims:
    """A POPULATION ASSERTION ON THE REAL ARTEFACT, which is what was missing the first time.

    Skipped rather than failed when the cache is absent, because it is a fetched artefact and
    not every checkout will have run the fetch -- but where it exists, the years it holds are
    asserted per year and not in total. A total would have passed the original defect: eight
    years of rows were fetched and the sum looked healthy while five years held nothing.
    """

    def test_each_pinned_year_present_in_the_cache_carries_a_full_year_of_half_hours(self):
        try:
            records = embedded.load_cached()
        except embedded.EmbeddedGenerationUnavailable:
            pytest.skip("no fetched cache in this checkout")
        series = embedded.to_settlement_periods(records)
        by_year: dict[str, int] = {}
        for date_str, _period in series:
            by_year[date_str[:4]] = by_year.get(date_str[:4], 0) + 1
        assert by_year, "cache parsed to no settlement periods at all"
        for year, count in sorted(by_year.items()):
            # 48 half hours x 365 days, less the clock-change day; leap years and the current
            # part-year run over and under. The bar is deliberately loose on size and STRICT on
            # the thing that actually broke: a year present at all is a year nearly complete.
            assert count > 17000, f"{year} parsed only {count} half hours"
