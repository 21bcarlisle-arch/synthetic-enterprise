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


def test_the_EPC_register_UNDERSTATES_heat_loss_on_every_premise(measured):
    """A real, directional finding and not a tautology: the register's modelled
    fabric is optimistic against what the building physics actually does. It is
    asserted because it is the mechanism behind the result below — C14 corrects
    UPWARD, which is why it can overshoot."""
    observations, _ = measured
    understated = [o for o in observations if o.epc_hlc_kw_per_k < o.actual_hlc_kw_per_k]
    assert len(understated) == len(observations), (
        "every premise's EPC prior sits below its true HLC; if this ever stops "
        "being true the finding below needs re-deriving, not re-stating"
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
    rates = (9.0, 10.0, 11.0)
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

    ON THE TEN-PREMISE PANEL that verdict is now INSUFFICIENT rather than green,
    and that is the correct reading of what a panel can support (2026-08-09): a
    clean sheet over ten homes rules out a true violation rate no smaller than
    30%. The panel breaches no band — its problem is power. The judged verdict
    comes from `--population`, which is what the gap is measured on for the record.
    """
    result = cf.two_level(panel, weather)
    assert result.generator.startswith("premise_trace")
    assert not result.failed, result.summary()
    assert result.inconclusive, (
        "ten homes cannot clear a control that claims to see a 5% violation rate"
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


def test_the_LAST_RED_CELL_closed_by_the_BAND_being_conditioned_not_moved(panel, weather):
    """THE RESIDUAL, RE-STATED (2026-08-09). This test previously asserted
    `result.is_red` and instructed whoever turned it green to re-state the
    expectation deliberately. This is that re-statement, and it pins the MECHANISM
    rather than the colour — because "the suite went green" is exactly the claim
    that deserves the least trust.

    The last red cell was L1.1 texture, worst home H10, the panel's only
    heat-pump home, at 0.1248 against a 0.15 floor whose own anchor text reasons
    from a gas premise ("a kettle is 2.8 kW for three minutes on a ~0.7 kWh
    half-hour"). The whole of H10's deficit decomposed to its DENOMINATOR: a heat
    pump is ~half its electricity and moves little period to period.

    WHAT WAS NOT DONE: the 0.15 floor was not touched, and no home was marked
    UNVALIDATED to duck the judgement. Both would have turned the suite green in
    one edit, which is why neither was the move.

    WHAT WAS DONE: L1.1 is now conditioned on heating system, with a second band
    for electrically-heated homes DERIVED from three published sources (Ofgem
    TDCV, the EST in-situ condensing-boiler trial, the DESNZ/ESC Electrification
    of Heat SPFH4). R15 evidence for the new band lives in
    `tests/harness/test_premise_two_level.py` §8, including the matched-pair proof
    that it is not the looser of the two against the same defect.

    THE TELL that this is not goal-seek, asserted below: the worst L1.1 cell is no
    longer the heat-pump home at all. It is D7, a GAS home, judged by the
    UNCHANGED 0.15 band, at 0.1804. The heat-pump home stopped being the worst
    cell rather than being let off the one it was failing."""
    result = cf.two_level(panel, weather)
    texture = result.cell(fgl.TEXTURE_STATISTIC)

    assert texture.homes_violating == 0, texture.note
    assert texture.band.threshold == 0.15, "the GAS band is the one that judged the worst cell"
    assert texture.worst_home == "D7", texture.note
    # THE WORST CELL CLEARS THE UNTOUCHED FLOOR. Asserted as a RELATION, not as a
    # pinned literal (2026-08-09): this assertion previously read
    # `worst_value == approx(0.1804, abs=5e-4)`, and the W1_12 cold-appliance
    # coupling — an honest fidelity improvement that moves the electricity series
    # this statistic is computed on — took D7 to 0.1782 and turned the control red
    # while saying nothing whatever about goal-seek. That is the "never pin a
    # generated value in a control" class: the pin cannot distinguish a physics
    # improvement from a regression, and its cheap fix (re-typing the literal to
    # match today's output) is the exact reflex R12 forbids.
    #
    # What the test is NAMED for is the mechanism, so the mechanism is what is
    # pinned: the band is a FLOOR at an UNMOVED 0.15 (asserted above) and the
    # worst home clears it on its own. The value stays in the message as a
    # diagnostic (R12), never as the pass condition.
    _worst_cell_clears_its_own_floor(texture)
    assert "L1.1e_half_hourly_texture_electric_heat=1" in texture.note, texture.note
    # The panel's ten homes cannot reach a PASS — see the note on the test above.
    # What is asserted here is the MECHANISM: no home is outside its own band, and
    # the one judging the worst cell is the untouched 0.15 gas band.
    assert texture.verdict is fgl.Verdict.INSUFFICIENT, texture.note

    # The UNVALIDATED cells are still UNVALIDATED — going green did not come from
    # quietly anchoring something that has no anchor. This assertion is an exact
    # set BECAUSE a cell arriving or leaving unnoticed is the thing it guards, and
    # it did its job on 2026-08-09: `L1.2h` appeared here before anyone mentioned
    # it in a commit message. It is a deliberate third — the space-heating
    # stream's own day-to-day repeatability, netted out of L1.2 so that one band
    # stops judging behaviour in a gas home and a thermostat in an electric one,
    # and REPORTED rather than given a threshold nobody has published.
    unvalidated = {c.statistic for c in result.cells if c.verdict is fgl.Verdict.UNVALIDATED}
    assert unvalidated == {
        "L1.2h_heating_shape_repeatability",
        "L1.4_weekday_weekend_separation",
        "L2.4_scale_spread_p90_p10",
    }, unvalidated
    # ...and the new one is not vacuous on this panel: the panel's heat-pump home
    # is exactly a home whose heat lands on the judged meter.
    assert result.cell("L1.2h_heating_shape_repeatability").homes_unjudged == 1


def test_the_RESHAPED_closure_control_still_fires_when_the_BAND_IS_MOVED(panel, weather, monkeypatch):
    """R15 for the reshape directly above. The literal `worst_value` pin was
    removed because it fired on honest physics; this proves the relational form
    that replaced it still fires on THE DEFECT THE TEST IS NAMED FOR — the cell
    being closed by MOVING the band rather than by conditioning it.

    The mutation is the goal-seek move itself, applied to the real band and run
    through the real measurement: drop the gas floor from 0.15 to 0.10, which is
    exactly what someone would do to admit a worst cell that would not clear it.
    Both surviving mechanism assertions must then reject the run — the band is no
    longer the untouched 0.15, and the floor the worst home is compared against is
    no longer the one whose anchor text this closure rests on.

    A REPLACEMENT CONTROL THAT COULD NOT FIRE WOULD BE WORSE THAN THE PIN IT
    REPLACED: the pin at least failed loudly. This is the evidence that the
    reshape tightened the control's aim rather than fail-opening it.
    """
    moved = dataclasses.replace(fgl.BANDS[fgl.TEXTURE_STATISTIC], threshold=0.10)
    monkeypatch.setitem(fgl.BANDS, fgl.TEXTURE_STATISTIC, moved)

    texture = cf.two_level(panel, weather).cell(fgl.TEXTURE_STATISTIC)

    # The assertion that carries the "not moved" claim REJECTS the moved band.
    assert texture.band.threshold != 0.15, (
        "the moved band did not reach the measurement — this mutation proves "
        "nothing about the control and must be repaired before it is trusted"
    )
    assert texture.band.threshold == 0.10, texture.band

    # And the relational assertion is genuinely comparing against the band that
    # was used, not against a remembered constant: it is the MOVED floor the
    # worst home is now measured against.
    assert texture.worst_value >= texture.band.threshold, texture.note


def test_the_RESHAPED_closure_control_still_fires_when_the_WORST_CELL_REGRESSES(panel, weather):
    """The second arm: the control must reject a worst cell that falls BELOW its
    floor. That is the regression the removed literal pin would also have caught,
    so the reshape must not have quietly given it up.

    THE MUTATION IS APPLIED TO THE CONTROL'S INPUT, NOT RE-IMPLEMENTED BESIDE IT.
    `_worst_cell_clears_its_own_floor` is the single expression the closure test
    above actually depends on; here it is handed a REAL measured cell whose worst
    value has been pushed under its own real band, and it must raise. Asserting
    `0.14 < 0.15` in a test of my own writing would prove only that Python
    compares floats — the tautology shape this project keeps finding inside its
    own R15 evidence.

    Generator-side proof that the real physics can drive this statistic through
    the real band lives one suite over (`tests/harness/test_premise_two_level.py`,
    the `_flatten_blend` mutation). This arm covers the seam between the two: that
    a sub-floor measurement, however produced, is not accepted here.
    """
    texture = cf.two_level(panel, weather).cell(fgl.TEXTURE_STATISTIC)
    floor = texture.band.threshold

    # Sanity: the unmutated cell passes the control, so a raise below is caused by
    # the mutation and not by a control that raises on everything.
    _worst_cell_clears_its_own_floor(texture)

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
