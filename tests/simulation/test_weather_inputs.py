import pytest
from saas.customers import get_customer
from simulation.weather_inputs import (
    load_weather_means,
    lookback_mean_temps,
    weather_means_for_customer,
)


def test_load_weather_means_reads_existing_csv():
    means = load_weather_means("C1")
    assert means["2016-01-01"] == 4.6
    assert means["2016-01-02"] == 9.2


def test_load_weather_means_missing_file_returns_empty():
    assert load_weather_means("DOES_NOT_EXIST") == {}


def test_weather_means_for_customer_resolves_shared_location_to_c1():
    # C5 (SME, London) shares C1's exact location dict — no weather file of
    # its own, so it should resolve to C1's.
    c5_means = weather_means_for_customer(get_customer("C5"))
    c1_means = weather_means_for_customer(get_customer("C1"))
    assert c5_means == c1_means
    assert c5_means["2016-01-01"] == 4.6


def test_weather_means_for_customer_resolves_gas_leg_to_electricity_counterpart():
    c2g_means = weather_means_for_customer(get_customer("C2g"))
    c2_means = weather_means_for_customer(get_customer("C2"))
    assert c2g_means == c2_means


def test_lookback_mean_temps_returns_window_before_term_start():
    weather_means = {"2016-01-01": 1.0, "2016-01-02": 2.0, "2016-01-03": 3.0}
    temps = lookback_mean_temps(weather_means, "2016-01-03", lookback_days=2)
    assert sorted(temps) == [1.0, 2.0]


def test_lookback_mean_temps_returns_none_when_window_has_no_data():
    weather_means = {"2020-01-01": 5.0}
    assert lookback_mean_temps(weather_means, "2016-01-03", lookback_days=2) is None


from simulation.weather_inputs import (_has_archive, _weather_source_customer_id,
                                       weather_source_customers, WEATHER_DATA_DIR)


def test_weather_data_dir_constant():
    assert WEATHER_DATA_DIR == "sim/weather_data"


def test_weather_source_c1_resolves_to_c1():
    from saas.customers import CUSTOMERS
    c1 = next(c for c in CUSTOMERS if c["customer_id"] == "C1")
    assert _weather_source_customer_id(c1) == "C1"


def test_weather_source_c5_resolves_to_london_customer():
    from saas.customers import CUSTOMERS
    c5 = next(c for c in CUSTOMERS if c["customer_id"] == "C5")
    result = _weather_source_customer_id(c5)
    assert result in ("C1", "C2", "C3", "C4")


def test_weather_source_unknown_location_returns_self():
    customer = {"customer_id": "X99", "location": {"lat": 0.0, "lon": 0.0, "region": "Unknown"}}
    result = _weather_source_customer_id(customer)
    assert result == "X99"


def test_load_weather_means_returns_dict():
    means = load_weather_means("C1")
    assert isinstance(means, dict)


def test_lookback_mean_temps_length_matches_window():
    weather_means = {"2016-01-01": 1.0, "2016-01-02": 2.0, "2016-01-03": 3.0}
    temps = lookback_mean_temps(weather_means, "2016-01-03", lookback_days=2)
    assert len(temps) == 2


def test_weather_data_dir_is_string():
    assert isinstance(WEATHER_DATA_DIR, str)


# ---------------------------------------------------------------------------
# W1_14: the weather-source predicate asks the PROPERTY (a CSV on disk), not the
# PROXY (commodity + segment) it read until 2026-09-20.
#
# The first two controls BIND THEIR OWN ROSTER, and that is the whole design. On
# the LIVE supply book the archived ids (C1/C2/C3) precede the un-archived ones
# (C7/C8/C9) at the same three coordinates, so the RESOLUTION the proxy produces
# is right for the wrong reason and all four pre-existing live-roster controls
# stay green when the repair is reverted (measured 2026-09-20, by mutation). The
# discriminating pair is bound so no acquisition, world-repair or reordering can
# take the subject away.
#
# The third IS on the live roster, deliberately, and it fires too — because
# MEMBERSHIP of the source list is observable there even when resolution is not.
# That is the split worth keeping: a live-roster control can see that C9 is named
# a weather source with no file behind it; only a bound pair can see which id a
# premise actually resolves to when both sit at one coordinate.
# ---------------------------------------------------------------------------

LONDON = {"lat": 51.5074, "lon": -0.1278, "region": "London"}


def test_a_premise_with_no_csv_cannot_be_a_weather_source_however_early_it_sits():
    """DEFECT: resolving a premise to a customer_id that holds no archive. That is not an error —
    `load_weather_means` returns an EMPTY DICT for a missing file, so the premise silently gets no
    weather at all, with nothing on any surface saying so."""
    roster = [
        # No CSV, and FIRST — the position C7/C8/C9 do not occupy on the live book.
        {"customer_id": "Z9", "commodity": "electricity", "segment": "resi", "location": LONDON},
        {"customer_id": "C1", "commodity": "electricity", "segment": "resi", "location": LONDON},
    ]
    premise = {"customer_id": "P1", "location": dict(LONDON)}

    # The branch CAN be taken: the proxy this repair replaced would have picked Z9 here...
    proxy_sources = [c for c in roster
                     if c["commodity"] == "electricity" and c["segment"] == "resi"]
    assert proxy_sources[0]["customer_id"] == "Z9", "the bound pair no longer discriminates"
    # ...and Z9 really does yield nothing, silently, which is the harm.
    assert not _has_archive("Z9")
    assert load_weather_means("Z9") == {}

    assert _weather_source_customer_id(premise, roster=roster) == "C1"


def test_an_archived_premise_is_a_source_whatever_its_commodity_and_segment():
    """DEFECT: the mirror — an archive that exists and cannot be reached. Birmingham and Teesside
    each hold two premises at one identical coordinate and neither is resi electricity, so under
    the proxy an archive pulled for the first could never answer the second."""
    roster = [
        {"customer_id": "C1", "commodity": "gas", "segment": "I&C", "location": LONDON},
    ]
    premise = {"customer_id": "P2", "location": dict(LONDON)}

    assert not [c for c in roster
                if c["commodity"] == "electricity" and c["segment"] == "resi"], (
        "the bound roster no longer excludes its source under the proxy"
    )
    assert _has_archive("C1"), "C1's archive is the witness this control needs"
    assert [c["customer_id"] for c in weather_source_customers(roster)] == ["C1"]
    assert _weather_source_customer_id(premise, roster=roster) == "C1"


def test_the_live_book_names_every_source_it_holds_and_no_id_without_a_file():
    """DEFECT: the source list drifting from what is on disk — the two halves above, on the real
    roster. This cannot catch the ORDER defect (that is what the bound pairs are for); what it
    pins is that the list is a statement about files, so a pull landing or a CSV going missing
    moves it."""
    sources = {c["customer_id"] for c in weather_source_customers()}
    assert sources, "the book resolves no weather at all"
    for cid in sources:
        assert _has_archive(cid), f"{cid} is a weather source with no archive on disk"
    for cid in ("C7", "C8", "C9", "C_IC1", "C_IC2"):
        assert not _has_archive(cid) or cid in sources
    assert "C7" not in sources, (
        "C7 is resi electricity and holds no CSV — it is back in the source list, so the proxy "
        "has returned"
    )
