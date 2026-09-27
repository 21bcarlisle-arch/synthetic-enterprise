"""A drawn household's coordinate — W2_18. Each test named by the defect it exists to catch.

THE DEFECT THIS WHOLE FILE IS ABOUT (measured 2026-09-06,
`docs/staging/SEAT_FINDING_W1_14_WAITED_ON_THE_WRONG_GAP_2026-09-06.md`): 210 of 210 drawn
households carried `lat: None, lon: None`, with ten real GB regions drawn, so every one of them was
refused by the derived weather cells and the world's household heat load was driven by none of the
derivation. The remedy is a coordinate SOURCED from where households actually are — and the failure
mode this file mostly guards is the cheap thing that looks identical from the outside: a fabricated
coordinate, or one point per region, both of which render as a perfectly good `lat`.
"""
from __future__ import annotations

import csv

import pytest

from simulation import household_siting as hs
from simulation.population_draw import _PLACEHOLDER_REGION, draw_population

_LAMBDA = 40.0
_SEED = 7


@pytest.fixture()
def frame_csv(tmp_path):
    """A two-region frame with a deliberately lopsided household weight, so a uniform draw and a
    weighted one give different answers rather than the same one by luck."""
    path = tmp_path / "frame.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        out = csv.writer(fh)
        out.writerow(["region", "lat", "lon", "households"])
        out.writerow(["London", "51.5000", "-0.1000", "9000.000"])
        out.writerow(["London", "51.6000", "-0.2000", "1000.000"])
        out.writerow(["Wales", "51.4800", "-3.1800", "500.000"])
    return path


@pytest.fixture(autouse=True)
def _no_cached_frame():
    """The module caches the frame per process and every test here loads a different one."""
    hs._frame_cache = hs._frame_cache_path = None
    hs._oa_cache = hs._oa_cache_path = None
    yield
    hs._frame_cache = hs._frame_cache_path = None
    hs._oa_cache = hs._oa_cache_path = None


def test_a_region_with_no_household_distribution_is_refused_by_name_and_never_sited(frame_csv):
    """DEFECT: siting a region the frame does not cover by falling back to anything at all — a
    national centroid, the nearest region, the first row. Every one of those renders as a
    coordinate and none of them is sourced. The refusal must name its reason (R15)."""
    assert hs.coordinate_for_customer("C_X", 7, _PLACEHOLDER_REGION, path=frame_csv) is None
    refusal = hs.siting_refusal(_PLACEHOLDER_REGION, path=frame_csv)
    assert refusal is not None
    assert _PLACEHOLDER_REGION in refusal
    assert "draw_region=True" in refusal, "the refusal must name the remedy, not just the problem"
    assert hs.siting_refusal("London", path=frame_csv) is None


def test_an_absent_frame_refuses_rather_than_siting_everyone_nowhere(tmp_path):
    """DEFECT (fail-open): treating a missing frame as an empty one, which would return None for
    every household and read exactly like the honest placeholder answer."""
    with pytest.raises(FileNotFoundError):
        hs.load_frame(tmp_path / "not-built.csv")


def test_an_empty_frame_refuses_rather_than_passing_as_a_built_one(tmp_path):
    """DEFECT: a frame whose build wrote a header and no rows. It is a real file, it parses, and
    every household it sites is None — indistinguishable from the placeholder unless this fails."""
    path = tmp_path / "frame.csv"
    path.write_text("region,lat,lon,households\n", encoding="utf-8")
    with pytest.raises(ValueError):
        hs.load_frame(path)


def test_a_household_is_sited_inside_its_own_region_and_never_another(frame_csv):
    """DEFECT: drawing from the whole frame rather than the region's slice of it. Every coordinate
    would still be a real GB household cell, and a Welsh household would be in London."""
    london = {(51.5, -0.1), (51.6, -0.2)}
    for i in range(200):
        assert hs.coordinate_for_customer(f"C_{i}", 7, "London", path=frame_csv) in london
        assert hs.coordinate_for_customer(f"C_{i}", 7, "Wales", path=frame_csv) == (51.48, -3.18)


def test_the_draw_is_household_weighted_and_not_uniform_over_the_cells(frame_csv):
    """DEFECT: siting uniformly over a region's cells. The output is the same SHAPE — real cells,
    right region — and it over-represents the empty countryside, which is the exact direction the
    weather-cell derivation exists to avoid (`weather_cell_weights`: an unweighted fit spends its
    cells on the sparse, cold, windy end).

    The fixture's London is 90/10, so a uniform draw gives 50/50 and this control is what tells the
    two apart. The tolerance is a sampling bound, not a fudge: 2,000 draws at p=0.9 has a standard
    error of 0.7 percentage points, so ±3 points is four sigma from the truth and forty from 50%.
    """
    n = 2000
    dense = sum(hs.coordinate_for_customer(f"C_{i}", 7, "London", path=frame_csv) == (51.5, -0.1)
                for i in range(n))
    assert 0.87 <= dense / n <= 0.93, (
        f"{dense / n:.3f} of households landed in the cell holding 90% of them — a uniform draw "
        "over the region's cells would give 0.5")


def test_the_siting_of_one_household_does_not_depend_on_any_other(frame_csv):
    """DEFECT (C-S2): drawing the coordinate from the acquisition sequence's own rng, which makes
    a household's location depend on how many customers were drawn before it — and makes adding
    the field shift every other drawn attribute."""
    first = hs.coordinate_for_customer("C_042", 7, "London", path=frame_csv)
    for other in ("C_001", "C_999", "C_042"):
        hs.coordinate_for_customer(other, 7, "London", path=frame_csv)
    assert hs.coordinate_for_customer("C_042", 7, "London", path=frame_csv) == first
    assert hs.coordinate_for_customer("C_042", 8, "London", path=frame_csv) is not None


def test_the_frame_covers_every_region_the_curriculum_draws():
    """DEFECT: a frame that covers most of the curriculum's regions. The households drawn into the
    missing one go back to `lat: None` — for that slice alone, silently, in a book where every
    other household is sited. This is the control that makes that impossible to miss.

    COVERAGE, NOT EQUALITY, SINCE 2026-09-07, AND THE DOCSTRING ABOVE IS WHY: the defect this test
    names is a MISSING region, and equality also refused an EXTRA one — which is not that defect
    and is what kept Scotland's 2.5 M sourced households discarded, because the frame was not
    allowed to carry a real GB region until the world agreed to draw from it. The extra direction
    is still guarded, by name rather than by count, one layer down in
    `household_siting_frame.CARRIED_AHEAD_OF_THE_CURRICULUM`, so a MISSPELT region cannot hide in
    the slack this relaxation creates."""
    from tools.household_siting_frame import CARRIED_AHEAD_OF_THE_CURRICULUM, expected_regions

    drawn, covered = expected_regions(), hs.regions()
    assert not drawn - covered, (
        f"the curriculum draws {sorted(drawn - covered)} and the frame cannot site them; those "
        "households go back to lat: None while every other household in the book has a coordinate")
    assert not covered - drawn - CARRIED_AHEAD_OF_THE_CURRICULUM, (
        f"the frame carries {sorted(covered - drawn - CARRIED_AHEAD_OF_THE_CURRICULUM)}, which "
        "nothing draws and nothing names -- a region no household reaches refuses nothing, so a "
        "misspelt one is silent")


def test_a_drawn_household_carries_a_coordinate_when_it_carries_a_real_region():
    """DEFECT — THE ONE THIS ATOM EXISTS FOR: `to_customer_dict` rendering `lat: None` for 100% of
    drawn households, so the derived weather cells drive nothing.

    Keyed to the PROPERTY (every household with a real region has a coordinate), never to today's
    coordinates, so it stays green when the frame is rebuilt on a newer census and goes red the
    moment a region stops being sited."""
    drawn = [c.to_customer_dict() for c in draw_population(
        _SEED, acquisitions_per_year_lambda=_LAMBDA, draw_region=True)]
    assert len(drawn) > 100, "too few drawn households for this to say anything"
    unsited = [c for c in drawn if c["location"]["lat"] is None]
    assert not unsited, (
        f"{len(unsited)} of {len(drawn)} drawn households carry a real region and no coordinate: "
        f"{sorted({c['location']['region'] for c in unsited})}")
    for c in drawn:
        # GREAT BRITAIN, NOT ENGLAND AND WALES, since 2026-09-07. The bound was 56.0N when the
        # world could not place a Scottish household at all -- the stock joint was SELECTED from
        # NEED, which has no Scottish dwellings, so the cell filter excluded S92000003 by name.
        # Households are now GENERATED from a fitted joint raked onto Scotland's own published
        # stock, so a household at 57.16N in Aberdeen is the world working rather than a defect.
        # The northern bound is Unst at 60.85N; the western is St Kilda at -8.65.
        assert -8.7 <= c["location"]["lon"] <= 2.0 and 49.8 <= c["location"]["lat"] <= 61.0, (
            f"{c['customer_id']} is sited outside Great Britain at {c['location']}")


def test_the_default_draw_stays_honestly_unsited_rather_than_guessing(frame_csv):
    """DEFECT: siting the placeholder region by inventing a point for it — the fabrication
    `fabric_physics.latitude_for_weather_site` refuses one layer down and
    `test_region_is_explicit_placeholder_not_fabricated` protects one layer up. A coordinate for
    `UNKNOWN_SYNTHETIC` would be a coordinate for a place that does not exist."""
    drawn = [c.to_customer_dict() for c in draw_population(
        _SEED, acquisitions_per_year_lambda=_LAMBDA)]
    assert len(drawn) > 100
    assert {c["location"]["region"] for c in drawn} == {_PLACEHOLDER_REGION}
    assert all(c["location"]["lat"] is None and c["location"]["lon"] is None for c in drawn)


def test_the_siting_draw_does_not_perturb_the_acquisition_stream(monkeypatch):
    """DEFECT (C-S2, and the one this project has paid for before): a new per-customer field drawn
    from the acquisition rng, which silently re-rolls every segment, band and payment method that
    follows it. Proven by making the siting answer something completely different and checking
    every OTHER field is byte-identical."""
    from simulation import household_siting

    def rendered():
        return [(c.customer_id, c.segment, c.commodity, c.payment_method, c.consumption_band,
                 c.eac_kwh, c.region, c.smart_meter, c.acquisition_date)
                for c in draw_population(_SEED, acquisitions_per_year_lambda=_LAMBDA,
                                         draw_region=True)]

    before = rendered()
    monkeypatch.setattr(household_siting, "coordinate_for_customer",
                        lambda *a, **k: (54.321, -1.234))
    after = rendered()
    assert after == before
    assert len(before) > 100


def test_a_sited_household_is_spread_across_its_region_and_not_stacked_on_one_point():
    """DEFECT: one point per region — the cheap alternative, and the one that renders identically.
    It would put every household in a region into a single derived weather cell, which collapses
    the 21-cell partition the whole derivation priced. Keyed to the SPREAD, not to any coordinate:
    a region's households must occupy many distinct cells, as the census says they do."""
    drawn = [c.to_customer_dict() for c in draw_population(
        _SEED, acquisitions_per_year_lambda=_LAMBDA, draw_region=True)]
    by_region: dict[str, set] = {}
    for c in drawn:
        loc = c["location"]
        by_region.setdefault(loc["region"], set()).add((loc["lat"], loc["lon"]))
    biggest = max(by_region.items(), key=lambda kv: len(kv[1]))
    assert len(biggest[1]) > 1, (
        f"every household drawn into {biggest[0]} is at the same point — that is a centroid, not a "
        "household distribution")


def test_the_weather_seam_no_longer_refuses_a_drawn_household_for_want_of_a_coordinate():
    """DEFECT: closing the coordinate gap in the draw and leaving the seam still saying there is
    one. This is the seam-level statement of what W2_18 was drawn to move — and it is deliberately
    NOT a claim that the household is sited in the cells, which is W1_14's next step and a separate
    refusal with a separate reason."""
    from simulation import weather_cell_siting as wcs

    drawn = [c.to_customer_dict() for c in draw_population(
        _SEED, acquisitions_per_year_lambda=_LAMBDA, draw_region=True)]
    assert drawn
    for c in drawn[:25]:
        assert "carries no coordinate" not in wcs.siting_refusal(c["location"])


# ---------------------------------------------------------------------------
# W2_19 layer one: the sited cell carries its output area
# ---------------------------------------------------------------------------

def _oa_frame(tmp_path, rows):
    import gzip

    path = tmp_path / "oa.csv.gz"
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        fh.write("region,lat,lon,output_area,households\n")
        for row in rows:
            fh.write(",".join(row) + "\n")
    return path


def test_the_output_area_lies_in_the_cell_the_coordinate_names_and_is_drawn_by_its_share(
        frame_csv, tmp_path):
    """DEFECT: an area drawn from anywhere but the sited cell (a region-wide pick, or a second cell
    draw), so the home's address and its coordinate name different places. Also: a flat pick among
    the cell's areas, which ignores how many households each holds. The lopsided 9:1 shares make a
    flat draw and a weighted one disagree."""
    oa = _oa_frame(tmp_path, [
        ("London", "51.5000", "-0.1000", "E_BIG", "8100.0"),
        ("London", "51.5000", "-0.1000", "E_SMALL", "900.0"),
        ("London", "51.6000", "-0.2000", "E_NORTH", "1000.0"),
        ("Wales", "51.4800", "-3.1800", "W_ONLY", "500.0"),
    ])
    in_cell = {(51.5, -0.1): {"E_BIG", "E_SMALL"}, (51.6, -0.2): {"E_NORTH"}}
    picks: dict[str, int] = {}
    for n in range(2000):
        cid = f"C{n}"
        lat, lon = hs.coordinate_for_customer(cid, 7, "London", path=frame_csv)
        area = hs.output_area_for_customer(cid, 7, "London", path=frame_csv, output_area_path=oa)
        assert area in in_cell[(lat, lon)], f"{cid} sited at {(lat, lon)} but given {area}"
        picks[area] = picks.get(area, 0) + 1
    # EVERY BRANCH REACHABLE before any branch is weighed: both areas of the shared cell are drawn.
    assert picks.get("E_BIG") and picks.get("E_SMALL") and picks.get("E_NORTH")
    assert 6 < picks["E_BIG"] / picks["E_SMALL"] < 14, picks
    assert hs.output_area_for_customer("C1", 7, _PLACEHOLDER_REGION, path=frame_csv,
                                       output_area_path=oa) is None


def test_a_sited_cell_the_output_area_frame_lacks_refuses_rather_than_giving_no_area(
        frame_csv, tmp_path):
    """DEFECT (fail-silent): a home sited in a cell the output-area frame does not carry, returned
    with no area. It would take the national headcount and nothing would say the two frames had
    been built from different cells."""
    oa = _oa_frame(tmp_path, [("London", "51.6000", "-0.2000", "E_NORTH", "1000.0")])
    with pytest.raises(KeyError, match="does not carry"):
        for n in range(200):
            hs.output_area_for_customer(f"C{n}", 7, "London", path=frame_csv, output_area_path=oa)


def test_an_absent_output_area_frame_refuses_rather_than_leaving_every_home_unconditioned(
        tmp_path):
    """DEFECT (fail-open): a missing frame read as an empty one. Every home would carry no area and
    draw nationally, which looks exactly like the book before W2_19."""
    with pytest.raises(FileNotFoundError, match="build-output-areas"):
        hs.load_output_area_frame(tmp_path / "absent.csv.gz")


def test_every_sited_england_and_wales_home_in_the_live_book_carries_its_output_area():
    """DEFECT: the built prior getting no input, the state measured on 2026-09-25 (0 of 231 homes
    carried an area). A sited home in England or Wales with no area, or with an area TS017 does
    not publish, reds here. Scotland is national BY CONSTRUCTION (TS017 is E&W), so a Scottish
    home must carry its S00 area and read national.

    The partition is checked first: the live book must reach BOTH the local and the national branch.
    A book where every home is national would pass the per-home legs below vacuously."""
    from simulation import dwelling_records as dr
    from simulation.live_population import live_drawn_households, live_dwellings, live_population

    book = {c["customer_id"]: c for c in live_population()}
    dwellings = live_dwellings()
    households = live_drawn_households()
    assert len(dwellings) > 100, f"population floor: only {len(dwellings)} drawn homes"
    sources = {cid: dr.people_count_source(d.get("output_area")) for cid, d in dwellings.items()}
    assert "output_area" in sources.values() and "national" in sources.values(), sources

    wrong = []
    for cid, dwelling in dwellings.items():
        location = book[cid]["location"]
        area = dwelling.get("output_area")
        if location["lat"] is None:
            continue
        if area != location.get("output_area") or area != households[cid].output_area:
            wrong.append((cid, "three carriers disagree", area))
        elif location["region"] == "Scotland":
            if not (area or "").startswith("S00") or sources[cid] != "national":
                wrong.append((cid, "Scottish home not S00/national", area))
        elif sources[cid] != "output_area":
            wrong.append((cid, "sited E&W home not conditioned on its area", area))
    assert not wrong, f"{len(wrong)} of {len(dwellings)} homes: {wrong[:5]}"
