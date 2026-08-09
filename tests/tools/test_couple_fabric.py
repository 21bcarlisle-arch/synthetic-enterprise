"""`tools/couple_fabric.py` — the CALLER that closes the H_GAP orphan transition.

The measurement code (`background/fabric_gap_ledger.py`) is tested by
`tests/harness/test_premise_two_level.py`. THIS suite tests the thing that suite
cannot: that something actually RUNS it, that what crosses to the company side is
only what a supplier can see, and that the ledger ids it writes under are real.

WHY A SEPARATE SUITE. A measurement function with a green unit test reads as
"done" to a reviewer while never being invoked by anything. That is the
orphan-transition defect (R11), and it has now happened twice in this codebase
(`write_fabric_gap_entries` here; `generate_evidence_data.generate()` before it).
Testing the runner is how the second half of the transition gets a control.
"""

from __future__ import annotations

import dataclasses
import datetime as dt
import json

import pytest

from background import coupled_triad
from background import fabric_gap_ledger as fgl
from company.pricing import thermal_inference as ti
from tools import couple_fabric as cf

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


@pytest.fixture(scope="module")
def weather():
    """The REAL Open-Meteo archive. If it is missing this suite must FAIL, never
    skip — an unavailable check is a FAILED check (R15)."""
    return cf.load_weather()


@pytest.fixture(scope="module")
def panel(weather):
    return cf.build_panel(weather, seed=17)


@pytest.fixture(scope="module")
def measured(panel, weather):
    return cf.observe(panel, weather)


# ===========================================================================
# §1 THE ORPHAN TRANSITION — the runner exists and reaches the ledger writer
# ===========================================================================


def test_the_ledger_atom_ids_are_REAL_map_atoms():
    """THE BUG THIS TEST WAS BORN FROM. `FABRIC_WORLD_ATOM` was written as
    "W1_11_premise_fabric_physics", which has never been an atom id — the real
    one is `W1_11_fabric_physics_core`. Nothing failed: `write_gap_entry` happily
    writes any key, and the Proof-door panel derives its ROWS from the map, so the
    entry would have been written successfully and rendered nowhere, every run,
    forever. A typo in a string constant is precisely what review reads past.
    """
    import yaml

    atoms = yaml.safe_load(
        (cf.PROJECT_DIR / "docs" / "design" / "maturity_map.yaml").read_text()
    )
    ids = {a["id"] for a in atoms}
    for constant in (fgl.FABRIC_WORLD_ATOM, fgl.GENERATOR_WORLD_ATOM, fgl.FABRIC_TWIN_ATOM):
        assert constant in ids, f"{constant} is not an atom in the maturity map"


def test_the_fabric_pairs_are_REGISTERED_couplings_or_the_panel_cannot_see_them():
    """The second half of the same defect. `build_coupling` DERIVES W1_12->C14
    from C14's depends_on, but assembles the final coupling from
    `_AUTHORITATIVE_COUPLING` ALONE — so a derived-but-unregistered pair is
    silently dropped, and a coupled world atom at L2 with no measured gap never
    trips the "depth nobody copes with" detector. The table reads like a
    cross-check and behaves like a whitelist.
    """
    import yaml

    atoms = yaml.safe_load(
        (cf.PROJECT_DIR / "docs" / "design" / "maturity_map.yaml").read_text()
    )
    coupling = coupled_triad.build_coupling(atoms)
    for world in (fgl.FABRIC_WORLD_ATOM, fgl.GENERATOR_WORLD_ATOM):
        assert coupling.get(world) == fgl.FABRIC_TWIN_ATOM, (
            f"{world} must resolve to {fgl.FABRIC_TWIN_ATOM} in the live coupling, "
            "or its ledger row is invisible to the Proof door and the L3 gate"
        )


def test_the_runner_writes_BOTH_rows_to_the_ledger(measured, tmp_path):
    observations, _ = measured
    path = tmp_path / "coupled_gap_ledger.json"
    written = fgl.write_fabric_gap_entries(
        observations,
        unit_rate_p_per_kwh=cf.DEFAULT_UNIT_RATE_P_PER_KWH,
        measured_at="2026-08-03T00:00:00+00:00",
        two_level=None,
        path=path,
    )
    assert set(written) == {"epc_vs_actual", "inferred_vs_actual"}
    ledger = json.loads(path.read_text())
    assert fgl.FABRIC_WORLD_ATOM in ledger
    assert fgl.GENERATOR_WORLD_ATOM in ledger
    for entry in ledger.values():
        assert entry["twin_atom_id"] == fgl.FABRIC_TWIN_ATOM


# ===========================================================================
# §2 THE WALL — what crosses to the company side, checked not asserted
# ===========================================================================


def test_the_company_receives_NO_fabric_parameter(panel, weather):
    """The inference call must be reachable from register reads, published
    temperature and a certificate ALONE. This is the wall, exercised rather than
    declared: the arguments are built here from scratch and the truth is never
    among them."""
    premise_id, household, trace, commodity, cadence, _lodged = panel[1]
    reads = cf._reads_from_trace(
        trace, commodity, every_n_days=cadence, start=cf.WINDOW_START
    )
    published = [
        ti.PublishedWeatherDay(d.date, d.weather.temperature_mean_c) for d in weather
    ]
    belief = ti.infer_thermal_parameters(
        premise_id=premise_id,
        reads=reads,
        weather=published,
        certificate=cf._certificate_for(trace, household, dt.date(2012, 7, 1)),
        as_of=cf.AS_OF,
        property_type_hint="terraced",
        main_heating_fuel="mains gas",
    )
    assert belief.hlc_kw_per_k > 0.0

    # Nothing handed over may equal the truth: no leak by construction.
    truth = trace.fabric.heat_loss_coefficient_kw_per_k
    assert all(r.cumulative_kwh != truth for r in reads)
    assert belief.hlc_kw_per_k != truth, (
        "an EXACT match would mean the fabric leaked through the seam"
    )


def test_meter_reads_are_CUMULATIVE_and_only_at_the_premises_own_cadence(panel):
    """A supplier holds a running register total at the cadence its meter
    reports. Handing over daily reads for a quarterly-billed premise would
    flatter the company with evidence it does not have."""
    for premise_id, _household, trace, commodity, cadence, _lodged in panel:
        reads = cf._reads_from_trace(
            trace, commodity, every_n_days=cadence, start=cf.WINDOW_START
        )
        values = [r.cumulative_kwh for r in reads]
        assert values == sorted(values), f"{premise_id}: a register never goes backwards"
        if len(reads) > 2:
            spacing = (reads[2].read_date - reads[1].read_date).days
            assert spacing == cadence, f"{premise_id}: expected {cadence}d, got {spacing}d"


def test_the_panel_is_NOT_uniformly_smart_metered(panel):
    """R15 fail-open: a panel read entirely daily would make the company look far
    better than a real book, because C14's error runs 0.2% -> 18% across the
    cadence range. The mix is load-bearing, so it is pinned."""
    cadences = {entry[4] for entry in panel}
    assert len(cadences) >= 3, f"the panel must span meter cadences, got {cadences}"
    assert max(cadences) >= 30, "a real book contains non-smart meters"


def test_a_premise_with_NO_certificate_falls_back_and_is_NOT_actionable(measured):
    """Absence is one of the three register error sources. The stock-class prior
    must never be actionable however tight its band — it contains no information
    about THIS premise."""
    _observations, detail = measured
    stock = [d for d in detail if d["basis"] == "stock_prior"]
    assert stock, "the panel must contain a premise with no certificate"
    for d in stock:
        assert d["is_actionable"] is False


# ===========================================================================
# §3 THE MEASUREMENT — real numbers, and the disagreement worth recording
# ===========================================================================


def test_the_gaps_are_finite_and_on_the_shared_0_to_1_scale(measured):
    observations, _ = measured
    for gap in (fgl.epc_vs_actual_gap(observations), fgl.inferred_vs_actual_gap(observations)):
        assert 0.0 < gap.gap < 2.0, (
            "a gap of exactly 0 would mean the observables leaked the truth (a wall "
            "breach, not a triumph); a gap far above 1 means worse than knowing nothing"
        )


def test_the_EPC_register_UNDERSTATES_heat_loss_on_ALL_BUT_ONE_premise(measured):
    """A real, directional finding and not a tautology: the register's modelled
    fabric is optimistic against what the building physics actually does. It is
    asserted because it is the mechanism behind the result below — C14 corrects
    UPWARD, which is why it can overshoot.

    RE-DERIVED 2026-08-09 (H35), which is what the previous version of this test
    instructed rather than re-stated. It read `== len(observations)` on a
    ten-premise panel of nine gas homes and one heat pump. Widening the panel to
    exercise the resistive and heat-pump texture bands put a fourteenth and
    fifteenth home on it, and ONE of them — H11, a detached 1965-80 home with
    partial insulation — has an EPC prior ABOVE its true HLC (0.2922 vs 0.2688).

    The direction is not noise and it is not a regression: `epc_prior` builds the
    prior from era U-values and an envelope-area ratio per property type, so a
    detached home of that era carries the largest modelled envelope on the panel,
    and the modelling error that is optimistic in a small flat can overshoot in a
    big house. What the finding below actually needs is that the REGISTER IS
    BIASED LOW OVERALL, which is asserted directly rather than inferred from a
    universal quantifier that a fifteenth home can break.

    The exception is pinned BY IDENTITY: a second premise crossing over is a
    different finding and must fail here rather than be absorbed.
    """
    observations, _ = measured
    overstated = {
        o.premise_id for o in observations if o.epc_hlc_kw_per_k >= o.actual_hlc_kw_per_k
    }
    assert overstated == {"H11"}, (
        "the register's optimism is the mechanism behind the result below; if the "
        "set of premises it is NOT optimistic about changes, re-derive the finding "
        f"rather than re-stating it (overstated: {sorted(overstated)})"
    )
    mean_epc = sum(o.epc_hlc_kw_per_k for o in observations) / len(observations)
    mean_actual = sum(o.actual_hlc_kw_per_k for o in observations) / len(observations)
    assert mean_epc < mean_actual, (
        f"the register must be biased LOW across the panel (epc {mean_epc:.4f}, "
        f"actual {mean_actual:.4f}) — that bias is what C14 corrects upward"
    )


def test_INFERENCE_CAN_MAKE_THE_POINT_ESTIMATE_WORSE_WHILE_MAKING_THE_DECISION_BETTER(measured):
    """THE RESULT THIS RUNNER WAS BUILT TO FIND, and it is recorded rather than
    tuned away (R12).

    Measured 2026-08-03 on the 10-premise panel: the EPC-vs-actual gap is 0.205
    and the inferred-vs-actual gap is 0.240 — i.e. C14's posterior is a WORSE
    point estimate than the register prior it started from. On the same panel the
    money consequence runs the other way: deciding a fabric measure on the EPC
    belief misranks 10% of premises (forgoing money and ~2.3 t CO2e/yr), while
    deciding it on the inferred belief misranks NONE.

    The two disagree because they ask different questions. `prediction_gap` is a
    LEVEL statistic (normalised squared error); the decision is an ORDERING one.
    C14 corrects every premise upward toward its true HLC and overshoots on some,
    which costs level accuracy and buys rank accuracy.

    THIS IS THE SAME LESSON THAT CREATED THIS ATOM, one level up: the control SET
    had a hole shaped like the defect. A level-and-sum gap metric, read alone,
    would have reported the company's inference as a REGRESSION and hidden that it
    strictly improved every decision anyone would take on it. Neither number is
    wrong; reporting only one of them would be.
    """
    observations, _ = measured
    epc = fgl.epc_vs_actual_gap(observations).gap
    inferred = fgl.inferred_vs_actual_gap(observations).gap
    assert inferred > epc, (
        "the point estimate got WORSE — if this flips, re-derive the finding "
        f"rather than re-stating it (epc {epc:.4f}, inferred {inferred:.4f})"
    )

    money_epc = fgl.money_consequence(
        observations, unit_rate_p_per_kwh=cf.DEFAULT_UNIT_RATE_P_PER_KWH, belief="epc")
    money_inferred = fgl.money_consequence(
        observations, unit_rate_p_per_kwh=cf.DEFAULT_UNIT_RATE_P_PER_KWH, belief="inferred")
    assert money_inferred.misrank_rate < money_epc.misrank_rate, (
        "...while the DECISION got better. The disagreement IS the finding."
    )
    assert money_epc.forgone_lifetime_gbp > 0.0
    assert money_inferred.forgone_lifetime_gbp <= money_epc.forgone_lifetime_gbp


def test_the_money_consequence_is_AFFINE_in_the_unit_rate_for_a_fixed_decision(measured):
    """R14 — the £ figure is meaningless without its basis, so the basis is proven to
    be exactly what the printout says it is.

    THE OLD CLAIM WAS "LINEAR" AND IT WAS WRONG (corrected 2026-08-09). Forgone value
    is `(saving_best x rate x life_best - capex_best) - (saving_chosen x rate x
    life_chosen - capex_chosen)`. The capex terms do not scale with the rate and do
    not cancel unless the two measures happen to cost the same, so doubling the rate
    cannot double the answer in general — the relationship is AFFINE, with an
    intercept made of the capex difference the wrong decision bought. The previous
    assertion held only for the particular pair of decisions the old choice set
    produced; adding the do-nothing option (whose capex is zero) exposed it
    immediately.

    Affine is testable without knowing the coefficients: three equally-spaced rates
    must satisfy `f(r1) + f(r3) == 2 f(r2)`. It is only a statement about the PRICE
    for a FIXED decision, so the decision vector is asserted unchanged first — a
    version of this test without that guard would be measuring a decision flip and
    calling it a pricing law.
    """
    observations, _ = measured
    # The triple moved 9/10/11 -> 11/12/13 on 2026-08-09 (H35). It is chosen for
    # the ONE property the test needs — that the decision vector is constant
    # across it — and the guard below is what enforces that, so the choice cannot
    # quietly become a choice about the answer. The widened panel puts a decision
    # flip between 10 and 11 p/kWh; measured, not guessed:
    # (9,10,11) -> [(1,6),(1,6),(0,6)], (11,12,13) -> [(0,6),(0,6),(0,6)].
    rates = (11.0, 12.0, 13.0)
    vectors = [
        [
            (
                fgl.money_consequence(observations, unit_rate_p_per_kwh=r, belief="epc").misranked_premises,
                fgl.money_consequence(observations, unit_rate_p_per_kwh=r, belief="epc").declined_where_value_existed,
            )
            for r in rates
        ]
    ][0]
    assert len(set(vectors)) == 1, (
        f"this test needs three rates that produce the SAME decisions: {vectors}"
    )
    f = [
        fgl.money_consequence(observations, unit_rate_p_per_kwh=r, belief="epc").forgone_lifetime_gbp
        for r in rates
    ]
    assert f[0] + f[2] == pytest.approx(2.0 * f[1], rel=1e-9), (
        f"forgone value must be affine in the unit rate for a fixed decision: {f}"
    )
    assert f[2] != pytest.approx(f[0]), "a rate move must change the £ figure at all"

    # Carbon is a PHYSICAL quantity and must not move with the price at all.
    carbon = [
        fgl.money_consequence(observations, unit_rate_p_per_kwh=r, belief="epc").forgone_annual_kg_co2e
        for r in rates
    ]
    assert carbon[0] == pytest.approx(carbon[2], rel=1e-9)


def test_the_two_level_result_rides_along_with_the_gap(panel, weather):
    """The realism of the traces the gap was measured ON is reported beside it,
    not in another file. A fabric gap measured on unrealistic traces is not a
    finding about the company.

    ON THIS PANEL that verdict is INSUFFICIENT rather than green, and that is the
    correct reading of what a panel can support (2026-08-09): a clean sheet over
    fifteen homes rules out a true violation rate no smaller than 20%. Every L1
    cell's problem here is power. The judged verdict comes from `--population`,
    which is what the gap is measured on for the record.

    THE PANEL ALSO BREACHES TWO BANDS. L2.4 is a POPULATION statistic rather than
    a per-home one, so the panel is enough to judge it and it is red — the two
    readings are kept apart below because "under-powered" and "wrong" are
    different states and this panel is both. L1.1 joined it on 2026-08-09 when the
    panel was widened to exercise the resistive and heat-pump texture bands (H35):
    the worst home is H11 at 0.07037 against the 0.07050 heat-pump floor. That
    breach is diagnosed, not tolerated — see the test below and atom
    `H36_the_texture_floor_is_one_number_for_every_home_size`.
    """
    result = cf.two_level(panel, weather)
    assert result.generator.startswith("premise_trace")
    assert {c.statistic for c in result.failed} == {
        "L1.1_half_hourly_texture",
        "L2.4_scale_spread_p90_p10",
    }, result.summary()
    assert result.inconclusive, (
        "fifteen homes cannot clear a control that claims to see a 5% violation rate"
    )
    for cell in result.inconclusive:
        assert cell.resolution == pytest.approx(fgl.RULE_OF_THREE / result.homes)


def _worst_cell_clears_its_own_floor(texture) -> None:
    """THE CLOSURE CONTROL, as a relation rather than a remembered number.

    Extracted so that the R15 mutation below exercises the SAME expression the
    closure test depends on, instead of a re-typed copy of it beside the original
    (a re-implementation proves the copy fires, which is not the claim).

    The band is a FLOOR, so "clears" means at or above it, and the direction is
    asserted rather than assumed — `>=` and `<=` are one character apart and the
    band is the only thing that says which is right.
    """
    assert texture.band.direction == "at_least", texture.band
    assert texture.worst_value >= texture.band.threshold, (
        f"the worst L1.1 cell ({texture.worst_home} at {texture.worst_value:.4f}) fell "
        f"BELOW the {texture.band.threshold} floor it is judged by — the closure has "
        f"regressed: {texture.note}"
    )


def test_the_TEXTURE_CELL_has_ONE_OPEN_BREACH_and_the_band_is_the_diagnosis(panel, weather):
    """RE-STATED AGAIN 2026-08-09 (H35), and the direction is the uncomfortable
    one: this cell was closed, and widening the panel re-opened it.

    WHAT CHANGED. The panel judged one heat-pump home and no resistive home at
    all, so two of the three regime-conditioned texture bands were carried and
    never exercised — L1.1r judged ZERO homes and reported nothing. H35 put three
    heat pumps and three panel-heater homes on it. The gas homes are untouched and
    all nine still clear the untouched 0.15 floor; ONE new home does not clear
    its own: H11 at 0.07037 against the 0.07050 heat-pump floor, a shortfall of
    0.2%.

    WHY THIS IS NOT "THE GENERATOR IS SMOOTH", and the decomposition is asserted
    below rather than argued. Both electric bands are `0.15 x behavioural share`,
    where the share comes from ONE published typical home: Ofgem TDCV medium
    (2,500 kWh behavioural) against a DESNZ/ESC median-SPFH4 heat pump, giving
    47.0%. H11 is a detached 1965-80 home with partial insulation, and its heat is
    62.4% of its own electricity — so the behavioural stream it actually has is
    37.6%, and the floor that follows from the band's OWN arithmetic at H11's own
    share is 0.0564, which H11 clears by 25%. The same holds for every home on the
    panel. The number that does not fit is the band's assumed home, not the trace:
    a fixed floor derived at one home size, applied to a home twice that size, is
    the wrong-load-set shape one level in from the one H35 was minted for.

    WHAT WAS NOT DONE, and this is the part that matters: the floor was not moved,
    H11 was not taken off the panel, and no home was marked UNVALIDATED. Any of
    the three would have turned this suite green in one edit while making the
    measurement worse. The breach is REPORTED and dispositioned as repair-the-
    statistic, on its own atom
    (`H36_the_texture_floor_is_one_number_for_every_home_size`) — a breach is a
    mechanism to diagnose (R4), never a tolerance to raise (R12).

    THE CONTROL IS STILL LIVE. `_worst_cell_clears_its_own_floor` is asserted
    below to RAISE on the real measured cell, so the open breach is held by the
    same expression the R15 mutations exercise — it has not been quietly relaxed
    to accommodate the finding.
    """
    result = cf.two_level(panel, weather)
    texture = result.cell(fgl.TEXTURE_STATISTIC)

    # (a) The original closure still holds where it was closed: the GAS band is
    #     untouched at 0.15 and no home judged by it is in breach.
    assert fgl.BANDS[fgl.TEXTURE_STATISTIC].threshold == 0.15, (
        "the gas floor is the one the original closure rests on and it stays put"
    )
    assert "L1.1_half_hourly_texture=9" in texture.note, texture.note

    # (b) The breach is EXACTLY ONE and it is pinned by identity, not by value.
    #     A second home crossing over, or a different home, is a different finding
    #     and must fail here rather than be absorbed into a remembered count.
    assert texture.homes_violating == 1, texture.note
    assert texture.worst_home == "H11", texture.note
    assert texture.band.statistic == "L1.1e_half_hourly_texture_electric_heat", texture.band
    assert texture.verdict is fgl.Verdict.FAIL, texture.note

    # (c) THE DIAGNOSIS. Every home clears the floor that the band's OWN
    #     arithmetic gives at that home's OWN behavioural share — including the
    #     one in breach. This is what says "the band's assumed home is wrong"
    #     rather than "the traces are smooth", and it is measured here rather
    #     than quoted from the docstring.
    population = fgl.premise_trace_population([entry[2] for entry in panel], weather)
    for index, (home, grid) in enumerate(zip(population.homes, population.grids)):
        total = sum(sum(day) for day in grid)
        heat = sum(sum(day) for day in population.space_heat_grids[index])
        own_floor = fgl.BANDS[fgl.TEXTURE_STATISTIC].threshold * (1.0 - heat / total)
        assert fgl.half_hourly_texture(grid) >= own_floor, (
            f"{home} falls below the floor implied by its OWN behavioural share "
            f"({own_floor:.4f}) — that would be a generator finding, and it is a "
            "different one from the band-scope finding this test records"
        )

    # (d) The control that carries the claim is the live one, and it FIRES on the
    #     breach rather than having been loosened around it.
    with pytest.raises(AssertionError, match="fell"):
        _worst_cell_clears_its_own_floor(texture)


def test_the_CELL_INVENTORY_is_EXACT_so_a_cell_cannot_arrive_or_leave_unnoticed(panel, weather):
    """The set of cells that are REPORTED-BUT-NOT-JUDGED, asserted exactly.

    A cell arriving or leaving unnoticed is the thing this guards, and it has
    caught three real movements: `L1.2h` appeared here before anyone mentioned it
    in a commit message; `L2.4_scale_spread_p90_p10` LEFT the set on 2026-08-09
    when it was anchored on the Low Carbon London panel and went immediately red
    (the opposite of quietly anchoring something that has no anchor, which is why
    the set is exact rather than a superset); and `L2.3_timing_diversity_periods`
    JOINED it on 2026-08-10 (H34) — not a cell losing its threshold to go green,
    but a floor the H33 sweep measured INSIDE its own null at 40, 60 and 90 days,
    replaced in the same commit by the strictly sharper
    `L2.3n_timing_diversity_null_ratio`, which is judged and asserted below.

    `L1.4` stayed, and the reason is a measurement rather than an absence: the
    same panel anchors it, and its own R15 mutation shows the anchor does not
    transfer to this window (`tests/harness/test_premise_two_level.py::
    test_the_L1_4_ANCHOR_DOES_NOT_TRANSFER_to_a_120_day_window`).

    THE L1.1 HISTORY MOVED, it did not disappear: the 2026-08-09 closure of the
    last red texture cell — conditioning the band on heating regime rather than
    moving the 0.15 floor — and the breach the widened panel re-opened in the
    heat-pump regime are both held by
    `test_the_TEXTURE_CELL_has_ONE_OPEN_BREACH_and_the_band_is_the_diagnosis`
    above, which is where those mechanism assertions now live.
    """
    result = cf.two_level(panel, weather)

    unvalidated = {c.statistic for c in result.cells if c.verdict is fgl.Verdict.UNVALIDATED}
    assert unvalidated == {
        "L1.2h_heating_shape_repeatability",
        "L1.4_weekday_weekend_separation",
        "L2.3_timing_diversity_periods",
    }, unvalidated
    assert result.cell("L2.3n_timing_diversity_null_ratio").verdict in (
        fgl.Verdict.PASS, fgl.Verdict.FAIL
    ), "L2.3 became unjudged only because L2.3n judges it — that must stay true here"
    assert result.cell("L2.4_scale_spread_p90_p10").verdict is fgl.Verdict.FAIL
    # ...and L1.2h is not vacuous on this panel: it measures every home whose heat
    # lands on the judged meter, which the H35 widening took from one to six. A
    # reported-not-judged cell measuring NOTHING would be the fail-open shape, so
    # the count is asserted rather than the mere presence of the cell.
    assert result.cell("L1.2h_heating_shape_repeatability").homes_unjudged == 6


def test_the_CLOSURE_CONTROL_still_fires_when_the_JUDGING_BAND_IS_MOVED(panel, weather, monkeypatch):
    """R15 arm one for the control above: the goal-seek move — closing the cell by
    MOVING the band rather than by diagnosing what it judges — must be visible.

    The mutation is applied to the band that ACTUALLY JUDGES the worst cell, which
    since the H35 widening is the heat-pump band rather than the gas one. That
    matters: mutating a band no home is judged by would leave the measurement
    unchanged and prove nothing, which is the same wrong-load-set error one level
    down that H35 was minted for. Dropping the heat-pump floor to 0.05 is exactly
    the edit that would turn today's RED cell green in one line.

    Both halves are asserted: the mutation REACHES the real measurement, and what
    it produces is the green cell the finding above refuses to buy that way.
    """
    electric = "L1.1e_half_hourly_texture_electric_heat"
    published_floor = fgl.BANDS[electric].threshold
    moved = dataclasses.replace(fgl.BANDS[electric], threshold=0.05)
    monkeypatch.setitem(fgl.BANDS, electric, moved)

    texture = cf.two_level(panel, weather).cell(fgl.TEXTURE_STATISTIC)

    # The mutation reached the real measurement...
    assert fgl.BANDS[electric].threshold != published_floor
    # ...and it is what "closes" the cell: the breach the untouched panel reports
    # disappears the moment the floor is lowered under it. That is the whole
    # reason the breach above is recorded rather than edited away.
    assert texture.homes_violating == 0, texture.note
    _worst_cell_clears_its_own_floor(texture)


def test_the_CLOSURE_CONTROL_accepts_a_clearing_cell_and_REJECTS_a_sub_floor_one(panel, weather):
    """R15 arm two: the control must be able to return BOTH answers on a real
    measured cell, or it is a constant wearing an assertion.

    THE MUTATION IS APPLIED TO THE CONTROL'S INPUT, NOT RE-IMPLEMENTED BESIDE IT.
    `_worst_cell_clears_its_own_floor` is the single expression the closure test
    depends on; here it is handed the REAL measured cell with its worst value
    moved above and below its OWN real band. Asserting `0.14 < 0.15` in a test of
    my own writing would prove only that Python compares floats — the tautology
    shape this project keeps finding inside its own R15 evidence.

    The accept arm is CONSTRUCTED rather than measured, and that is a statement
    about the tree rather than about the control: at HEAD the panel's worst
    texture cell is in breach (H11, the open finding above), so there is no
    unmutated cell to demonstrate the pass side with. Constructing it from the
    real cell and the real band keeps both arms on the same expression — and the
    arm above shows the pass side IS reachable from a real measurement.

    Generator-side proof that the real physics can drive this statistic through
    the real band lives one suite over (`tests/harness/test_premise_two_level.py`,
    the `_flatten_blend` mutation).
    """
    texture = cf.two_level(panel, weather).cell(fgl.TEXTURE_STATISTIC)
    floor = texture.band.threshold

    clearing = dataclasses.replace(texture, worst_value=floor + 0.01)
    _worst_cell_clears_its_own_floor(clearing)

    regressed = dataclasses.replace(texture, worst_value=floor - 0.01)
    with pytest.raises(AssertionError, match="fell"):
        _worst_cell_clears_its_own_floor(regressed)


# ===========================================================================
# §4 DETERMINISM — the runner may be re-run and compared
# ===========================================================================


def test_the_measurement_is_DETERMINISTIC_for_a_fixed_seed(weather):
    """C-S2. A gap that moves between identical runs cannot be a diagnostic."""
    a, _ = cf.observe(cf.build_panel(weather, seed=17, limit=5), weather)
    b, _ = cf.observe(cf.build_panel(weather, seed=17, limit=5), weather)
    assert [o.inferred_hlc_kw_per_k for o in a] == [o.inferred_hlc_kw_per_k for o in b]


def test_a_DIFFERENT_seed_moves_the_world_but_the_panel_still_measures(weather):
    """Independence: the finding must not rest on one lucky draw."""
    other, _ = cf.observe(cf.build_panel(weather, seed=99, limit=8), weather)
    assert fgl.epc_vs_actual_gap(other).gap > 0.0
    assert all(o.actual_hlc_kw_per_k > 0.0 for o in other)


# ===========================================================================
# §5 THE DRAWN POPULATION — C14's L3 exit condition
#
# The panel above is composed to span the stock, which is the honest thing to do
# with ten homes and the exact thing that stops ten homes being a finding about a
# book. These tests are about the population NOBODY CHOSE.
# ===========================================================================


@pytest.fixture(scope="module")
def drawn(weather):
    """Small on purpose: these assert the PATH and the WALL, not the numbers.
    The measured population result is 200 premises and lives in the atom's
    evidence, not in a unit test that has to run on every commit."""
    return cf.build_drawn_population(weather, n=12, seed=17, population_seed=17)


def test_the_drawn_population_is_not_the_authored_panel(drawn, panel):
    """A `--population` run that silently fell back to the panel would report a
    population result computed on a chosen population — the precise failure this
    build exists to remove."""
    assert {entry[0] for entry in drawn}.isdisjoint({entry[0] for entry in panel})
    cells = {
        (entry[1].property_type, entry[1].build_era, entry[1].insulation) for entry in drawn
    }
    assert len(cells) > 1, "the drawn population collapsed to one cell"


def test_the_wall_holds_on_a_DRAWN_premise_too(drawn, weather):
    """The wall is a property of the seam, not of the ten homes it was first
    exercised on. Same assertion as §2, on a premise nobody wrote down."""
    premise_id, household, trace, commodity, cadence, lodged = drawn[0]
    reads = cf._reads_from_trace(
        trace, commodity, every_n_days=cadence, start=cf.WINDOW_START
    )
    published = [
        ti.PublishedWeatherDay(d.date, d.weather.temperature_mean_c) for d in weather
    ]
    belief = ti.infer_thermal_parameters(
        premise_id=premise_id,
        reads=reads,
        weather=published,
        certificate=cf._certificate_for(trace, household, lodged),
        as_of=cf.AS_OF,
        property_type_hint=cf._EPC_PROPERTY_TYPE[household.property_type],
        main_heating_fuel="mains gas" if household.is_gas_heated else "air source heat pump",
    )
    assert belief.hlc_kw_per_k > 0.0


def test_a_drawn_population_measures_a_gap_end_to_end(drawn, weather):
    """The orphan-transition rule (R11) applied to the new path: the population
    flag must reach a NUMBER, not merely construct premises."""
    observations, detail = cf.observe(drawn, weather)
    assert len(observations) == len(drawn) == len(detail)
    assert fgl.epc_vs_actual_gap(observations).gap > 0.0
    assert fgl.inferred_vs_actual_gap(observations).gap > 0.0


def test_the_drawn_population_contains_premises_with_NO_certificate(drawn):
    """EPC absence is one of the three error sources C14 models. If a drawn
    population never produced one, the stock-prior branch would be exercised by
    the authored panel alone — i.e. by a hand-placed `None`."""
    assert any(entry[5] is None for entry in drawn)


def test_population_and_premises_flags_are_mutually_exclusive():
    """Two different populations quietly resolved one way would let a run label
    itself with a composition it did not use."""
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "tools/couple_fabric.py", "--population", "5", "--premises", "3"],
        cwd=str(cf.PROJECT_DIR), capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "pick one" in result.stderr
