"""W1_14: the derived weather cells reach the world, and the world says what they cost it.

Each test names the defect it exists to catch. The defect this FILE exists to catch is the one the
delivery seat found: five derivation modules in `tools/`, at level 3, imported by nothing in
`simulation/`, `company/` or `saas/` — so the world's household heat load was driven by none of it.
"""

import json

import pytest

from simulation import weather_cell_siting as wcs
from simulation.weather_inputs import _weather_source_customer_id

LONDON = {"lat": 51.5074, "lon": -0.1278, "region": "London"}
BIRMINGHAM = {"lat": 52.4862, "lon": -1.8904, "region": "Birmingham"}
TEESSIDE = {"lat": 54.5973, "lon": -1.1049, "region": "Teesside"}
WITNESS = {"lat": 50.5392, "lon": -4.2371, "region": "Cornish coast"}


def test_the_sim_imports_the_derivation_rather_than_reimplementing_it():
    """DEFECT: the world grows its own cell partition, and the published curve and the settled
    weather drift apart with nothing able to notice.

    `derive` must reach `tools.weather_cell_derivation` for the driver list and the same k-means
    settings the published per-driver curve used. This asserts the seam exists as an IMPORT, which
    is the whole of W1_14's gap.
    """
    src = (wcs.PROJECT / "simulation" / "weather_cell_siting.py").read_text()
    assert "from tools.weather_cell_derivation import DRIVERS" in src
    assert "from tools import weather_cell_drivers" in src
    assert "from tools import weather_cell_weights" in src

    from tools.weather_cell_derivation import DRIVERS

    assert wcs.load()["drivers"] == list(DRIVERS), (
        "the committed siting was cut on a different driver list from the published derivation"
    )


def test_the_accept_branch_is_reachable_and_it_matches_climate_not_proximity():
    """DEFECT (R15, the trap entered three times in one afternoon): a substitution rule whose
    accept branch cannot fire. Every refusal test below passes against a mechanism that refuses
    EVERYTHING, so the accept branch must be proved reachable before any of them mean anything.

    The witness is 304 km from London on the opposite coast. A mechanism that matched on distance
    would refuse it; one that matched on the derived cells accepts it, because the derivation puts
    the two in the same cell on all three drivers. So this also pins WHICH property is being
    tested — swapping the cell comparison for a nearest-site rule turns this red.
    """
    assert wcs.cell_matched_site(WITNESS) == "C1"

    sited = wcs.cells_for_location(WITNESS)
    london = wcs.cells_for_location(LONDON)
    assert sited["cells"] == london["cells"]

    # ...and it really is far away, so "same cell" cannot be read as "next door".
    assert abs(sited["lat"] - london["lat"]) > 0.9
    assert abs(sited["lon"] - london["lon"]) > 4.0


def test_one_driver_disagreeing_refuses_the_whole_substitution():
    """DEFECT: taking a site's temperature while quietly taking its wind and cloud too.

    The archive CSV carries all three drivers in one row, so a substitution is all-or-nothing.
    Birmingham is the case that proves the AND is load-bearing rather than decorative: it shares
    Manchester's wind cell (19) and neither its temperature cell nor its sunshine cell. Relaxing
    the comparison to any-driver-matches turns this red.
    """
    sited = wcs.cells_for_location(BIRMINGHAM)
    manchester = wcs.load()["archive_sites"]["Manchester"]

    assert sited["cells"]["annual_wind"] == manchester["cells"]["annual_wind"]
    assert sited["cells"]["winter_temp"] != manchester["cells"]["winter_temp"]
    assert sited["cells"]["annual_sun"] != manchester["cells"]["annual_sun"]

    assert wcs.cell_matched_site(BIRMINGHAM) is None


def test_an_unsited_coordinate_is_refused_and_never_placed_by_nearest_anything():
    """DEFECT: the fabrication `fabric_physics.latitude_for_weather_site` refuses one layer down —
    resolving a premise the derivation has never seen by falling back to something plausible.

    A coordinate absent from the artefact must come back None, not the nearest site.
    """
    unsited = {"lat": 52.0000, "lon": -1.0000, "region": "nowhere in particular"}
    assert wcs.cells_for_location(unsited) is None
    assert wcs.cell_matched_site(unsited) is None
    assert "has not been sited" in wcs.siting_refusal(unsited)

    # A premise with no coordinates at all — every drawn population customer, today.
    assert wcs.cell_matched_site({"lat": None, "lon": None, "region": "GB"}) is None


def test_the_refusal_names_the_driver_that_disagreed():
    """DEFECT: a bare None, which makes an ARCHIVE gap look like a coordinate typo and gives the
    next pull nothing to prioritise on. A refusal that says why is how the refusal itself gets
    found to be wrong."""
    reason = wcs.siting_refusal(TEESSIDE)
    assert "Teesside" in reason
    for site in ("C1", "C2", "C3", "C4"):
        assert site in reason, f"{site} is an archive site and the refusal did not price it"
    assert "winter_temp" in reason
    assert "3.5% of GB households" in reason


def test_the_archive_covers_a_small_measured_share_and_the_figure_carries_its_partition():
    """DEFECT (the seat's own finding): reading 'the cells are derived' as 'the world has them'.

    Four sites against a decision of 21 per driver. The joint figure is what the fabric path
    actually depends on, because a substitution takes all three drivers at once. Keyed to the
    PROPERTY — the joint share cannot exceed any single-driver share, and the archive cannot cover
    more cells than it has sites — so it stays honest when a fifth pull lands and goes red if
    someone widens the partition without re-deriving.
    """
    data = wcs.load()
    cov = wcs.archive_coverage()

    assert data["cells_per_driver"] == wcs.CELLS_PER_DRIVER == 21
    assert len(data["archive_sites"]) == len(wcs.ARCHIVE_SITES) == 4

    for driver in data["drivers"]:
        assert 0.0 < cov[driver] < 1.0
        assert cov["all_three"] <= cov[driver], (
            f"the joint share exceeds {driver} alone, which is arithmetically impossible — "
            "the coverage masks are not being intersected"
        )

    # Four sites can occupy at most four of the 21 cells on each driver.
    for driver in data["drivers"]:
        occupied = {s["cells"][driver] for s in data["archive_sites"].values()}
        assert len(occupied) <= 4


def test_the_seam_answers_the_two_uncovered_locations_the_supply_book_actually_holds():
    """DEFECT: wiring a seam the world never reaches. Birmingham and Teesside are real supply
    points with real coordinates and no weather CSV — they are the premises this mechanism exists
    for, and it must reach them (and, today, refuse them) rather than never being called."""
    from company.interfaces.supply_book import registered_supply_points

    regions = {c["region"] for c in (p["location"] for p in registered_supply_points())}
    assert {"Birmingham", "Teesside"} <= regions, (
        "the supply book no longer holds the uncovered locations this seam was built for"
    )
    for location in (BIRMINGHAM, TEESSIDE):
        assert wcs.cells_for_location(location) is not None, "a real premise went unsited"
        assert wcs.cell_matched_site(location) is None


def test_the_seam_did_not_move_any_customer_that_was_already_settling():
    """DEFECT: a fidelity change that silently repoints a live customer's weather. Step 1 (exact
    location identity) must still answer first, so every premise that settled before this seam
    existed settles on the same CSV after it."""
    from company.interfaces.supply_book import registered_supply_points

    expected = {
        "C1": "C1", "C2": "C2", "C3": "C3", "C4": "C4",
        "C5": "C1", "C6": "C2", "C7": "C1", "C8": "C2", "C9": "C3",
        "C1g": "C1", "C2g": "C2", "C3g": "C3", "C4g": "C4",
        "C_IC4": "C2",
    }
    for customer in registered_supply_points():
        cid = customer["customer_id"]
        if cid in expected:
            assert _weather_source_customer_id(customer) == expected[cid]

    # And the uncovered ones still fall through to their own id, which has no CSV — the refusal
    # `fabric_demand_path` already makes, now with a reason available beside it.
    for cid in ("C_IC1", "C_IC2", "C_IC3", "C_IC3g"):
        customer = next(c for c in registered_supply_points() if c["customer_id"] == cid)
        assert _weather_source_customer_id(customer) == cid


def test_a_hand_edited_artefact_cannot_quietly_widen_the_claim():
    """DEFECT: the committed answer drifting from the derivation with nothing able to tell. The
    artefact is data, so it is editable; this pins that the READER honours what it says rather than
    what the module's constants say."""
    data = json.loads(wcs.ARTEFACT.read_text())
    data["archive_sites"]["Manchester"]["cells"] = dict(
        data["locations"]["52.4862,-1.8904"]["cells"]
    )
    fixture = wcs.PROJECT / "sim" / "weather_cells" / "_test_widened.json"
    fixture.write_text(json.dumps(data))
    try:
        # With Manchester's cells forced onto Birmingham's, the accept branch fires — proving the
        # live refusal comes from the DERIVED cells and not from a hardcoded list of four ids.
        assert wcs.cell_matched_site(BIRMINGHAM, path=fixture) == "C2"
        assert wcs.cell_matched_site(BIRMINGHAM) is None
    finally:
        fixture.unlink()


def test_derive_reproduces_the_committed_artefact():
    """DEFECT (the worktree-extract trap): an artefact nobody can regenerate, so its numbers are
    unfalsifiable. SKIPS with a named reason when the HadUK/census caches are absent rather than
    passing vacuously — a skip is a result, a vacuous pass is a lie.

    UNMARKED and unguarded by any `--slow` opt-in on purpose: the whole derivation is 5.3 s, and
    a control gated behind a flag nobody passes is a control that never runs.
    """
    from tools.weather_cell_drivers import CACHE as HADUK
    from tools.weather_cell_weights import ONSPD_CSV

    if not HADUK.exists() or not ONSPD_CSV.exists():
        pytest.skip(f"needs the HadUK normals ({HADUK}) and the ONSPD pull ({ONSPD_CSV})")

    fresh = wcs.derive()
    committed = json.loads(wcs.ARTEFACT.read_text())
    assert fresh["coverage"] == committed["coverage"]
    assert fresh["archive_sites"] == committed["archive_sites"]
    assert fresh["locations"] == committed["locations"]
