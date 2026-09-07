"""W1_14: the derived weather cells reach the world, and the world says what they cost it.

Each test names the defect it exists to catch. The defect this FILE exists to catch is the one the
delivery seat found: five derivation modules in `tools/`, at level 3, imported by nothing in
`simulation/`, `company/` or `saas/` — so the world's household heat load was driven by none of it.
"""

import json
import math

import pytest

from simulation import weather_cell_siting as wcs
from simulation.weather_inputs import _WEATHER_SOURCE_CUSTOMERS, _weather_source_customer_id

LONDON = {"lat": 51.5074, "lon": -0.1278, "region": "London"}
BIRMINGHAM = {"lat": 52.4862, "lon": -1.8904, "region": "Birmingham"}
TEESSIDE = {"lat": 54.5973, "lon": -1.1049, "region": "Teesside"}
WITNESS = {"lat": 50.4689, "lon": -4.1492, "region": "Cornish coast"}


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

    The witness is ~300 km from London on the opposite coast. A mechanism that matched on distance
    would refuse it; one that matched on the derived cells accepts it, because the derivation puts
    the two in the same cell on all three drivers. So this also pins WHICH property is being
    tested — swapping the cell comparison for a nearest-site rule turns this red.

    2026-09-07: this went red when the artefact was re-cut on the UPRN placement, because the old
    witness cell stopped sharing all three of London's — leaving the accept branch with NO witness,
    which is the very R15 failure the witness exists to prevent, reintroduced by a re-derivation
    rather than by a code change. The witness was re-measured, not the assertion relaxed. The
    distance is asserted as a DISTANCE now rather than as per-axis deltas, one of which was passing
    by 0.02 degrees and would have failed the next re-cut for a reason that is not the property.
    """
    assert wcs.cell_matched_site(WITNESS) == "C1"

    sited = wcs.cells_for_location(WITNESS)
    london = wcs.cells_for_location(LONDON)
    assert sited["cells"] == london["cells"]

    # ...and it really is far away, so "same cell" cannot be read as "next door".
    lat1, lon1 = math.radians(sited["lat"]), math.radians(sited["lon"])
    lat2, lon2 = math.radians(london["lat"]), math.radians(london["lon"])
    a = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    assert 6371.0 * 2 * math.asin(math.sqrt(a)) > 250


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

    2026-09-07 — the subject was replaced when the artefact was re-cut over the whole occupied grid,
    and the REPLACEMENT is stronger than what it replaced. This used to use (52.0000, -1.0000),
    which is inland Warwickshire: it was unsited only because the table held seven locations, so it
    tested the table's SIZE and not the refusal. It now resolves, correctly. Two subjects take its
    place and neither can ever be closed by widening the artefact:

      * a coordinate 0.0002° (~22 m) off a real land cell centre — the TIGHTEST possible case, and
        the one a nearest-cell fallback would answer while looking entirely reasonable;
      * a coordinate that is not GB land at all.

    The near-miss leg is the one that matters. Every other refusal control here would still pass
    against a mechanism that snapped to the nearest cell; this one is red the moment it does.
    """
    on_grid = next(iter(wcs.load_land_cells()[1]))
    lat, lon = (float(v) for v in on_grid.split(","))
    assert wcs.cells_for_location({"lat": lat, "lon": lon}) is not None, (
        "the near-miss leg below proves nothing unless the cell it misses is really sited"
    )

    near_miss = {"lat": round(lat + 0.0002, 4), "lon": lon, "region": "22 m off a land cell"}
    assert wcs.cells_for_location(near_miss) is None, (
        "a coordinate 22 m off a land cell centre was sited — the lookup has acquired a "
        "nearest-cell fallback, which is proximity standing in for climate"
    )
    assert wcs.cell_matched_site(near_miss) is None

    unsited = {"lat": 48.8566, "lon": 2.3522, "region": "nowhere in particular"}
    assert wcs.cells_for_location(unsited) is None
    assert wcs.cell_matched_site(unsited) is None
    # Keyed to the PROPERTY, not the wording (which was rewritten 2026-09-07 when the refusal was
    # found to be prescribing a remedy that cannot reach this case): the refusal must say the
    # coordinate is absent from the artefact AND must not offer proximity as a way out.
    refusal = wcs.siting_refusal(unsited)
    assert "not in the derived artefact" in refusal
    assert "nearest" in refusal, "the refusal must explicitly rule out the fallback it is tempting"

    # A premise with no coordinates at all — every drawn customer under the DEFAULT placeholder
    # region, and none of them once `draw_region=True` (W2_18, 2026-09-07).
    assert wcs.cell_matched_site({"lat": None, "lon": None, "region": "GB"}) is None


def test_a_premise_with_no_coordinate_is_refused_for_that_reason_and_not_told_to_re_derive():
    """DEFECT: a refusal naming a remedy that cannot work.

    A location with `lat: None` and an unsited real coordinate both came back "regenerate with
    `--derive`" until 2026-09-06. They are different failures with opposite fixes: re-deriving the
    GB grid can site a real coordinate and can NEVER site a missing one. Every household the world
    draws is the second case, so the seam's most common refusal pointed at the wrong lane.

    Keyed to the PROPERTY (the two refusals are distinguishable and the no-coordinate one does not
    prescribe `--derive`), not to today's wording, so it stays honest if the text is rewritten and
    goes red if the branches are ever collapsed back together.

    2026-09-07 — THIS CONTROL WAS HALF WRONG, and the half is kept beside its correction. It used to
    assert `"--derive" in siting_refusal(unsited)`, on the reasoning that re-deriving fixes a real
    unsited coordinate. It does not: `derive()` sites only the locations it is handed and the CLI
    hands it the same seven, so bare `--derive` reaches no drawn household. The wrong leg survived
    because at the time NO real coordinate reached that branch — it was asserting a remedy against
    an empty population. It now asserts the opposite property: the unsited refusal must NOT sell
    bare `--derive` as sufficient.
    """
    no_coordinate = {"lat": None, "lon": None, "region": "UNKNOWN_SYNTHETIC"}
    unsited = {"lat": 48.8566, "lon": 2.3522, "region": "nowhere in particular"}

    bare = wcs.siting_refusal(no_coordinate)
    unsited_refusal = wcs.siting_refusal(unsited)
    assert unsited_refusal != bare, "two different failures, one refusal"
    # 2026-09-07, and the superseded assertion is kept beside it because it was RIGHT when written
    # and is wrong now for a reason worth reading. It asserted `"locations=" in unsited_refusal` —
    # that the refusal name re-cutting the artefact as the remedy. The artefact HAS been re-cut,
    # over all 175,188 occupied land cells, so a coordinate that still fails to site is not one a
    # wider artefact can reach: it is not GB land. A refusal still prescribing `derive(locations=)`
    # would now be sending the reader to do work that cannot help, which is the same defect the
    # `--derive` leg above was corrected for — one lane later.
    assert "occupied 1 km land cells" in unsited_refusal, (
        "the unsited refusal must say the coordinate is not a land cell of the derivation, which "
        "is the only thing left that it can be"
    )
    assert "locations=" not in unsited_refusal, (
        "the refusal is prescribing a re-cut that has already happened and cannot reach this case"
    )
    assert "coordinate" in bare and "None" in bare
    assert "draw" in bare.lower(), "the refusal must name the lane that can actually fix it"
    assert not bare.startswith(f"{no_coordinate['region']!r} has not been sited"), (
        "the no-coordinate case is answering through the unsited branch again"
    )


def test_a_drawn_household_has_a_coordinate_and_the_artefact_resolves_it():
    """DEFECT (the seat's own, 2026-09-07): a tripwire that could not see the event it was built for.

    Its predecessor — `test_no_household_in_this_world_can_reach_the_cell_substitution_branch` —
    said in its own docstring that "a coordinate at the draw breaks it … delete it and move W1_14's
    level". W2_18 then landed a coordinate at the draw (`ec8a18710`) and it stayed GREEN, because
    its drawn-population leg called `draw_population(...)` with the DEFAULT placeholder region,
    which is the one region `household_siting` correctly refuses to site. The capability arrived on
    the non-default branch and the control was measuring the default one. R15: a control keyed to
    today's CONFIGURATION is blind to the branch the work actually lands on.

    So this is rewritten to the property rather than deleted, because the claim it guards did NOT
    become true — it changed shape. Three legs, each fixed by a different lane:

      1. every resi premise in the supply book answers at step 1, so it never consults step 2 —
         the two un-archived locations hold only I&C premises (unchanged, 2026-09-06);
      2. with `draw_region=True` every drawn household DOES carry a coordinate — W2_18's delivery,
         and this leg goes red if it ever regresses;
      3. and every one of them RESOLVES, because the artefact is now cut over all 175,188 occupied
         land cells rather than over the seven locations `derive()` was handed.

    Leg 3 was written as its own opposite ("and none of them resolves"), deliberately shaped to go
    red when the world got better, with the instruction to replace rather than weaken it. It went
    red on 2026-09-07 and this is the replacement. It is not a weaker control: the frame and the
    artefact are built from the same two expressions over the same HadUK grid, so anything less
    than 100% means they have diverged, which is a defect and not a coverage gap.
    """
    from company.interfaces.supply_book import registered_supply_points
    from simulation.population_draw import draw_population

    resi = [p for p in registered_supply_points() if p["segment"] == "resi"]
    assert resi, "the supply book holds no households at all — this measures nothing"
    for premise in resi:
        # The claim is about which STEP answers, not which CSV it lands on. Asserting the
        # destination would pass if the cell branch started answering and returned the same site,
        # which is precisely the change this control exists to notice.
        assert any(s["location"] == premise["location"] for s in _WEATHER_SOURCE_CUSTOMERS), (
            f"{premise['customer_id']} no longer has an exact-location archive, so it now reaches "
            "the cell branch — W1_14's household gap has begun to close and this control has done "
            "its job"
        )
        assert _weather_source_customer_id(premise) in ("C1", "C2", "C3", "C4")

    # draw_region=True is the SHARP configuration and the reason this control was blind: with the
    # default placeholder region there is no household distribution to draw from, so an unsited
    # household there proves nothing about whether a coordinate exists.
    drawn = [c.to_customer_dict() for c in
             draw_population(7, acquisitions_per_year_lambda=40.0, draw_region=True)]
    assert len(drawn) > 100, "too few drawn households for this to say anything"

    # Leg 2 — W2_18 delivered. Red if the coordinate regresses.
    unsited = [c for c in drawn if c["location"]["lat"] is None]
    assert not unsited, (
        f"{len(unsited)} of {len(drawn)} drawn households lost their coordinate — W2_18 regressed"
    )

    # Leg 3 — EVERY drawn household now resolves. This leg was the inverse assertion until
    # 2026-09-07 ("and none of them resolves"), written to go red the moment the artefact was cut
    # over the drawn population, with its own instruction not to weaken it but to replace it. This
    # is that replacement, and it is the same property read the other way round: the drawn
    # population and the artefact's key space either agree or they do not.
    unresolved = [c for c in drawn if wcs.cells_for_location(c["location"]) is None]
    assert not unresolved, (
        f"{len(unresolved)} of {len(drawn)} drawn households no longer resolve in the derived "
        "cells. The frame draws HadUK land cell coordinates and the artefact is cut over all of "
        "them, so this can only mean the two have stopped being built the same way — do not add a "
        "nearest-cell fallback, find the divergence"
    )


def test_the_two_artefacts_were_cut_by_the_same_partition():
    """DEFECT: the JSON's archive sites and the CSV's 175,188 land cells cut by DIFFERENT k-means
    runs, so a premise and the site it matches carry labels that do not mean the same thing. That
    would be invisible everywhere — both files parse, every lookup answers, and the substitution it
    licences is simply wrong.

    Four legs, and the last is the one with teeth: it RE-SITES all seven named locations out of the
    CSV alone and checks the answer against the JSON, cells and distance. The two artefacts are not
    keyed alike — a named location is keyed on the PREMISE's coordinate (London's
    `km_to_cell_centre` is 0.42 km, so 51.5074,-0.1278 is not a cell centre and is deliberately not
    a row of the CSV), so a key-equality check would be looking for something that should not be
    there. Reproducing the nearest-cell siting is the check that actually binds the two.
    """
    import numpy as np

    data = wcs.load()
    drivers, cells = wcs.load_land_cells()

    assert list(drivers) == data["drivers"], "the CSV's columns are not the JSON's drivers"
    assert len(cells) == data["occupied_land_cells"], (
        f"the land cell table holds {len(cells):,} cells and the JSON says the partition was cut "
        f"over {data['occupied_land_cells']:,} — one of them was regenerated without the other"
    )
    for labels in cells.values():
        assert all(0 <= c < data["cells_per_driver"] for c in labels)

    keys = list(cells)
    cell_lat = np.array([float(k.split(",")[0]) for k in keys])
    cell_lon = np.array([float(k.split(",")[1]) for k in keys])
    for named in data["locations"].values():
        i, km = wcs._nearest_land_cell(named["lat"], named["lon"], cell_lat, cell_lon)
        # Not equality: the CSV stores the cell coordinate to 4 dp and the JSON's distance was
        # measured against the unrounded one, so the two differ by the quantisation — 11 m per
        # axis, ~16 m on the diagonal. 20 m is that bound and not a fitted tolerance; a genuine
        # grid disagreement is a whole cell, 1 km, and clears it by fifty times.
        assert abs(km - named["km_to_cell_centre"]) < 0.02, (
            f"{named['name']} sits {km:.3f} km from the nearest cell in the land table and the "
            f"JSON recorded {named['km_to_cell_centre']} km — further apart than the 4 dp key can "
            "explain, so the two artefacts were cut over different grids"
        )
        assert dict(zip(drivers, cells[keys[i]])) == named["cells"], (
            f"{named['name']} carries different cells in the two artefacts — they were cut by "
            "different partitions and every substitution across them is unsound"
        )


def test_both_legs_of_the_substitution_are_reachable_from_the_population_that_uses_it():
    """DEFECT (R15, the trap CLAUDE.md names as entered three times in one afternoon): a rare
    branch that no member of the real population can take, guarded by refusal tests that all pass
    against a mechanism refusing everything.

    `test_the_accept_branch_is_reachable...` proves the accept leg fires — but it fires for the
    REACHABILITY WITNESS, a coordinate this module places into the artefact itself precisely so the
    branch can be exercised. That is a control over the mechanism, not over the world: it would
    stay green in a world where no household the draw can produce ever matched an archive site.

    So this asserts the partition over the DRAWN population instead, both legs at once, which is
    the one-control-over-the-whole-partition shape rather than a leg per branch. If the accept leg
    empties, the substitution branch is unreachable for every real household and W1_14's mechanism
    buys nothing — that is a finding to record and a witness to re-establish, NOT a control to
    relax, exactly as `REACHABILITY_WITNESS`'s own note says.
    """
    from simulation.population_draw import draw_population

    drawn = [c.to_customer_dict()["location"] for c in
             draw_population(7, acquisitions_per_year_lambda=40.0, draw_region=True)]
    matched = [loc for loc in drawn if wcs.cell_matched_site(loc) is not None]
    refused = [loc for loc in drawn if wcs.cell_matched_site(loc) is None]

    assert matched, (
        f"none of {len(drawn)} drawn households matches an archive site on all three drivers, so "
        "the accept branch is unreachable from the world's own population and only the planted "
        "witness can fire it"
    )
    assert refused, (
        f"all {len(drawn)} drawn households match an archive site — four CSVs cannot cover a "
        "21-cell partition, so the comparison has been loosened off the all-three AND"
    )
    # The refusal a drawn household receives must be the ARCHIVE one, not the artefact one.
    reason = wcs.siting_refusal(refused[0])
    assert "shares no archive site's cells" in reason, (
        "a resolved household is being refused as though its coordinate were missing — the "
        "artefact gap and the archive gap have been collapsed into one refusal again"
    )


def test_the_refusal_names_the_driver_that_disagreed():
    """DEFECT: a bare None, which makes an ARCHIVE gap look like a coordinate typo and gives the
    next pull nothing to prioritise on. A refusal that says why is how the refusal itself gets
    found to be wrong."""
    reason = wcs.siting_refusal(TEESSIDE)
    assert "Teesside" in reason
    for site in ("C1", "C2", "C3", "C4"):
        assert site in reason, f"{site} is an archive site and the refusal did not price it"
    assert "winter_temp" in reason
    # Keyed to the ARTEFACT's own figure, not to the literal "3.5%" this asserted until 2026-09-07.
    # That literal went red when the artefact was re-cut on the UPRN placement — a control pinned to
    # today's answer going red because the code became MORE honest, which is exactly backwards.
    coverage = wcs.load()["coverage"]["all_three"]
    assert f"{coverage * 100:.1f}% of GB households" in reason


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

    # ONE pass for both artefacts, because that is how `--derive` writes them: deriving them
    # separately here would grade a shape the CLI cannot produce, and would cost a second 7 s read.
    fresh, fresh_land = wcs._derived()
    committed = json.loads(wcs.ARTEFACT.read_text())
    assert fresh["coverage"] == committed["coverage"]
    assert fresh["archive_sites"] == committed["archive_sites"]
    assert fresh["locations"] == committed["locations"]

    # And the 4.3 MB bulk table, which is otherwise the largest unfalsifiable claim in the tree:
    # 175,188 rows nobody could regenerate would be numbers with no derivation behind them.
    drivers, committed_land = wcs.load_land_cells()
    assert len(fresh_land) == len(committed_land)
    assert {f"{lat:.4f},{lon:.4f}": tuple(cells) for lat, lon, *cells in fresh_land} == (
        committed_land
    ), "the committed land cell table is not what the derivation produces"
