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
    observations, detail, _no_belief = cf.observe(panel, weather)
    return observations, detail


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
    from tools import maturity_map_store as map_store

    # Whole map: these constants name atoms that are FINISHED, so they live in the closed
    # half. Reading the live half alone would fail this on storage, not on a real typo.
    atoms = map_store.load_atoms(
        cf.PROJECT_DIR / "docs" / "design" / "maturity_map.yaml"
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
    from tools import maturity_map_store as map_store

    atoms = map_store.load_atoms(
        cf.PROJECT_DIR / "docs" / "design" / "maturity_map.yaml"
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


def test_a_premise_with_NO_certificate_yields_NO_belief_AT_ALL(panel, weather):
    """SUPERSEDES `test_a_premise_with_NO_certificate_falls_back_and_is_NOT_actionable`
    (2026-08-12, §2c). That test asserted the stock-class fallback was never
    actionable — true, and it was checking the wrong thing: the fallback was only
    reachable because `observe` handed the company `property_type_hint` computed
    from the SIM's own household object, for a premise the register has no
    certificate for. The Director's ruling is that suppliers know very little about
    the property, so the honest answer is not a weak prior, it is NO prior.

    `epc_prior`'s "no certificate and no property type" refusal was live code that
    could never fire in the only run that exercises it. It fires here.
    """
    observations, detail, no_belief = cf.observe(panel, weather)
    uncertificated = {entry[0] for entry in panel if entry[5] is None}
    assert uncertificated, "the panel must contain a premise with no certificate"

    assert {n["premise_id"] for n in no_belief} == uncertificated
    for n in no_belief:
        assert "no fabric prior for this premise at all" in n["reason"]

    # And it is GONE from the measured population, not silently carrying a prior.
    assert not (uncertificated & {o.premise_id for o in observations})
    assert not (uncertificated & {d["premise_id"] for d in detail})
    assert not [d for d in detail if d["basis"] == "stock_prior"], (
        "a stock-class prior can now only come from a property attribute the "
        "company was handed off the truth object"
    )


def test_the_reader_is_TOLD_the_gap_was_measured_on_a_subset(panel, weather):
    """THE CAVEAT IS THE POINT, and it is a control because the number moved the
    FLATTERING way. Closing the side door made the company strictly worse — it now
    declines every premise it knows nothing about — and the drawn-population gap
    FELL, 0.4269 -> 0.1979, because the premises that left the measurement are
    exactly the ones it was worst about. A gap that halves on the commit that took
    the company's information away, published bare, reads as an improvement.

    R15 both ways: at full coverage the sentence must be absent, or its presence
    carries no information.
    """
    observations, _detail, no_belief = cf.observe(panel, weather)
    assert no_belief, "the authored panel must contain an uncertificated premise"
    caveats = fgl.headline_caveats(
        observations,
        unit_rate_p_per_kwh=cf.DEFAULT_UNIT_RATE_P_PER_KWH,
        premises_without_belief=len(no_belief),
    )
    subset = [c for c in caveats if c.startswith("MEASURED ON A SUBSET")]
    assert len(subset) == 1
    assert f"{len(observations)} of {len(observations) + len(no_belief)}" in subset[0]

    for absent in (0, None):
        full = fgl.headline_caveats(
            observations,
            unit_rate_p_per_kwh=cf.DEFAULT_UNIT_RATE_P_PER_KWH,
            premises_without_belief=absent,
        )
        assert not any(c.startswith("MEASURED ON A SUBSET") for c in full)


def test_the_company_is_handed_NO_ATTRIBUTE_OFF_THE_TRUTH_OBJECT(panel, weather, monkeypatch):
    """THE CLASS CONTROL (R10), not the instance. The finding named
    `property_type_hint`; `main_heating_fuel` was crossing the same way on the same
    line, and the next one would too. So this pins the WHOLE argument set the
    coupling run may hand the company, and any future argument computed from
    `household` fails it whatever it is called.

    R15 both ways: restoring `property_type_hint=_EPC_PROPERTY_TYPE[household.
    property_type]` to `observe` makes this fail on the extra key, and
    `test_a_premise_with_NO_certificate_yields_NO_belief_AT_ALL` fail on the
    premise that reappears.
    """
    ALLOWED = {"premise_id", "reads", "weather", "certificate", "as_of"}
    seen: list[set[str]] = []
    real = ti.infer_thermal_parameters

    def spy(**kwargs):
        seen.append(set(kwargs))
        return real(**kwargs)

    monkeypatch.setattr(cf.ti, "infer_thermal_parameters", spy)
    cf.observe(panel, weather)

    assert seen, "the spy never ran — this control would pass on a tool that does nothing"
    for keys in seen:
        assert keys == ALLOWED, (
            f"the company was handed {sorted(keys - ALLOWED)} — anything about the "
            "premise must arrive ON the certificate, never computed from the "
            "simulation's household object"
        )


def test_closing_the_side_door_moved_NOTHING_about_a_CERTIFICATED_premise(panel, weather):
    """The claim that made dropping both arguments safe rather than a rewrite:
    for a premise that HAS a certificate the two dropped values are identical to
    what the certificate already carries (`epc_prior` reads
    `certificate.property_type`; `_certificate_for` sets `main_heating_fuel=
    _register_fuel(household)`). If that ever stops being true, this change
    silently moved every certificated premise's belief and this test says so.
    """
    published = [
        ti.PublishedWeatherDay(d.date, d.weather.temperature_mean_c) for d in weather
    ]
    checked = 0
    for premise_id, household, trace, commodity, cadence, lodged in panel:
        if lodged is None:
            continue
        certificate = cf._certificate_for(trace, household, lodged)
        reads = cf._reads_from_trace(
            trace, commodity, every_n_days=cadence, start=cf.WINDOW_START
        )
        common = dict(
            premise_id=premise_id, reads=reads, weather=published,
            certificate=certificate, as_of=cf.AS_OF,
        )
        now = ti.infer_thermal_parameters(**common)
        before = ti.infer_thermal_parameters(
            **common,
            property_type_hint=cf._EPC_PROPERTY_TYPE[household.property_type],
            main_heating_fuel=cf._register_fuel(household),
        )
        assert now.hlc_kw_per_k == before.hlc_kw_per_k
        assert now.prior.hlc_kw_per_k == before.prior.hlc_kw_per_k
        assert now.relative_sd == before.relative_sd
        checked += 1
    assert checked >= 10, f"only {checked} certificated premises exercised"


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

    THE PANEL ALSO BREACHES ONE BAND. L2.4 is a POPULATION statistic rather than
    a per-home one, so the panel is enough to judge it and it is red — the two
    readings are kept apart below because "under-powered" and "wrong" are
    different states and this panel is both.

    L1.1 JOINED IT ON 2026-08-09 AND LEFT AGAIN ON 2026-08-10, and the exit is
    worth the sentence because of HOW. The H35 widening put H11 in breach at
    0.07037 against a 0.07050 heat-pump floor; H36 diagnosed the floor as one
    fixed number applied to every home size and repaired the STATISTIC — L1.1 is
    read net of space heat and judged by the single untouched 0.15 floor, on which
    every home on the panel clears. Nothing was tuned to get here: see
    `test_the_TEXTURE_CELL_BREACH_CLOSED_when_the_LOAD_SET_WAS_REPAIRED` and the
    fail-open the old reading is measured to have had.
    """
    result = cf.two_level(panel, weather)
    assert result.generator.startswith("premise_trace")
    assert {c.statistic for c in result.failed} == {
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


def _flatten_to_own_mean_profile(behavioural):
    """MUTATION — every day becomes the home's own mean behavioural profile,
    rescaled to that day's own behavioural total.

    The realistic smooth-by-construction defect, and deliberately NOT a flat day:
    the home keeps its level, its diurnal shape and its daily totals, and loses
    every appliance event. It is the same construction as the sweep's own
    `_flat_behavioural_day_null`, written out here so this file's evidence does
    not depend on a private helper in another module.
    """
    days = len(behavioural)
    mean = [sum(behavioural[d][p] for d in range(days)) / days for p in range(48)]
    total = sum(mean)
    return [
        [v / total * sum(day) for v in mean] if total > 0 else [0.0] * 48
        for day in behavioural
    ]


def population_homes(panel):
    return [entry[0] for entry in panel]


def panel_systems(panel):
    """The panel's REGISTER heating systems, read off the household record rather
    than inferred from the trace — the same fact the cell is keyed on."""
    return [str(getattr(entry[2].source.system, "value", entry[2].source.system))
            for entry in panel]


def test_the_TEXTURE_CELL_BREACH_CLOSED_when_the_LOAD_SET_WAS_REPAIRED(panel, weather):
    """CLOSED 2026-08-10 (H36), and the direction is the one that has to be
    argued for: this cell was RED, and it went green without the floor moving.

    WHAT WAS RED. The H35 widening put three heat pumps and three panel-heater
    homes on the panel, and H11 read 0.07037 against the 0.07050 heat-pump floor —
    a shortfall of 0.2%. The diagnosis recorded then was that the number that did
    not fit was the BAND'S ASSUMED HOME: both electric floors were `0.15 x
    behavioural share` at one published typical home, and the panel's homes run
    0.30-0.74 behavioural share, so one fixed number was 25% too strict for H11.

    WHAT CHANGED, AND WHY IT IS NOT THE GOAL-SEEK MOVE. The floor was not raised,
    lowered or rescaled: there is one texture floor, still 0.15, still the gas
    number this cell was born with. What moved is the LOAD SET — L1.1 is read on
    the meter net of space heat, which is the denominator its 0.15 was always an
    argument about. Read there, every home on the panel clears it, the nine gas
    homes are bit-for-bit unchanged (their heat is on the other meter, so the
    netting is the identity on them), and the electrically heated homes stop being
    judged on a number that includes their boiler.

    AND IT IS A STRENGTHENING, WHICH IS THE PART THAT MATTERS —
    `test_the_OLD_WHOLE_METER_reading_was_FAIL_OPEN_on_a_BEHAVIOURALLY_FLAT_home`
    below measures the old reading passing five of these six homes with every
    appliance event removed from them.
    """
    result = cf.two_level(panel, weather)
    texture = result.cell(fgl.TEXTURE_STATISTIC)

    # (a) The floor is UNTOUCHED and it is the only judged one.
    assert fgl.BANDS[fgl.TEXTURE_STATISTIC].threshold == 0.15, (
        "the closure rests on the floor NOT having moved"
    )
    assert texture.band.statistic == fgl.TEXTURE_STATISTIC
    assert texture.band.threshold == 0.15

    # (b) Every home is judged — none excluded to get here — and none is in
    #     breach. Pinned by identity as well as by count: a different worst home
    #     is a different measurement and must be read, not absorbed.
    assert (texture.homes_judged, texture.homes_unjudged) == (15, 0), texture.note
    assert texture.homes_violating == 0, texture.note
    # H38 (2026-08-10) moved the worst home OFF the electrically heated set: with
    # the water heater out of the denominator too, the panel's marginal home is a
    # GAS home the netting never touched. That is the same tell the drawn 60 gives,
    # and it is the shape a load-set repair leaves behind.
    assert texture.worst_home == "D7", texture.note
    assert texture.worst_value == pytest.approx(0.1782, abs=5e-4), texture.note
    assert "net of space AND water heat" in texture.note
    electric = {
        home for home, system in zip(population_homes(panel), panel_systems(panel))
        if fgl.HEAT_ON_THE_JUDGED_METER.get(system, False)
    }
    assert texture.worst_home not in electric, (
        "after both machines come out, the marginal home must be one whose meter "
        "the netting is the identity on — otherwise this is a rescaling"
    )

    # (c) The verdict is INSUFFICIENT rather than PASS, and that is the honest
    #     reading: fifteen homes cannot rule out a 5% violation rate. The breach
    #     is gone; the power was never there.
    assert texture.verdict is fgl.Verdict.INSUFFICIENT, texture.note

    # (d) THE GAS HOMES ARE UNCHANGED BY THE REPAIR, which is what makes it a
    #     load-set correction rather than a rescaling of everybody. Measured, not
    #     asserted: a home whose heat is on the other meter contributes a stream
    #     of zeros and its reading is bit-for-bit what it was.
    population = fgl.premise_trace_population([entry[2] for entry in panel], weather)
    for index, (home, grid) in enumerate(zip(population.homes, population.grids)):
        heat = fgl.machine_draw(
            [list(day) for day in population.space_heat_grids[index]],
            [list(day) for day in population.water_heat_grids[index]],
        )
        grid = [list(day) for day in grid]
        if not any(any(day) for day in heat):
            assert fgl.half_hourly_texture(grid, machines=heat) == (
                fgl.half_hourly_texture(grid)
            ), f"{home} carries no heat on this meter and must be untouched"

    # (e) The control that carries the claim is the live one and it PASSES on the
    #     real measured cell — the arm that was unreachable while the breach was
    #     open.
    _worst_cell_clears_its_own_floor(texture)


def test_the_OLD_WHOLE_METER_reading_was_FAIL_OPEN_on_a_BEHAVIOURALLY_FLAT_home(
    panel, weather
):
    """THE EVIDENCE THAT H36 IS A STRENGTHENING AND NOT A CONVENIENCE, measured on
    the six homes it is about.

    THE MUTATION. Each home's behaviour is replaced by its own mean behavioural
    profile — level, diurnal shape and daily totals all preserved, every appliance
    event gone — and its heating machine is put back on top, untouched. This is
    the smooth-by-construction generator the L1.1 floor exists to catch, in a
    house that still has a real heat pump in it.

    THE RESULT. Read on the WHOLE meter against the rescaled floors that used to
    judge these homes (0.0705 heat pump, 0.0363 resistive), FIVE of the six PASS:
    the machine's own period-to-period movement stands in for the behaviour that
    was removed, and the rescaled floor is low enough to let it. Read net of space
    heat against 0.15, all six fail. A control that cannot fail on its own named
    defect is worse than none (R15), and that is what the previous reading was for
    an electrically heated home.
    """
    population = fgl.premise_trace_population([entry[2] for entry in panel], weather)
    # The floors that used to judge these homes, re-derived here from the published
    # figures rather than imported — the functions are gone, and the point of this
    # test is what they USED to accept.
    old_floors = {
        "heat_pump_air": 0.15 * (2500.0 / (2500.0 + (9500.0 * 0.825) / 2.78)),
        "electric_direct": 0.15 * (2500.0 / (2500.0 + (9500.0 * 0.825) / 1.0)),
    }
    assert old_floors["heat_pump_air"] == pytest.approx(0.0705, abs=1e-4)
    assert old_floors["electric_direct"] == pytest.approx(0.0363, abs=1e-4)

    passed_the_old_floor = []
    heated = 0
    for index, home in enumerate(population.homes):
        regime = population.heating_systems[index]
        if not fgl.HEAT_ON_THE_JUDGED_METER[regime]:
            continue
        heated += 1
        grid = [list(day) for day in population.grids[index]]
        heat = [list(day) for day in population.space_heat_grids[index]]
        behavioural = fgl.meter_net_of_machines(grid, heat)
        flat = _flatten_to_own_mean_profile(behavioural)
        mutated = [
            [b + h for b, h in zip(flat_day, heat_day)]
            for flat_day, heat_day in zip(flat, heat)
        ]
        if fgl.half_hourly_texture(mutated) >= old_floors[regime]:
            passed_the_old_floor.append(home)
        # The reading the cell takes now fails every one of them.
        assert fgl.BANDS[fgl.TEXTURE_STATISTIC].judge(
            fgl.half_hourly_texture(mutated, machines=heat)
        ) is fgl.Verdict.FAIL, home

    assert heated == 6, "the six homes the H35 widening put on the panel"
    assert sorted(passed_the_old_floor) == ["E13", "E14", "E15", "H10", "H12"], (
        "the fail-open this repair closed has moved — five of six is the measured "
        f"figure on the record, got {sorted(passed_the_old_floor)}"
    )


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
    """R15 arm one for the control above: the mutation must REACH the real
    measurement, through the real band, on the real panel.

    RE-AIMED BY H36, and the direction flipped with the cell. While the cell was
    in breach the goal-seek move was to DROP the floor under the failing home, so
    the mutation dropped it and watched the breach disappear. The cell is green
    now, so the mutation that proves the same wiring is the other way up: raise
    the one judged floor above what the panel actually reads, and the closure
    control must fire. Both mutations exercise the same path — cell value read off
    the live population, band read off the live table — and neither is a
    re-implementation of the control beside it.

    Raising the floor is NOT a proposal about the band. It is the only mutation
    available that changes the verdict without touching the traces, which is
    exactly what makes it the test of whether the control is wired to the band at
    all.
    """
    published_floor = fgl.BANDS[fgl.TEXTURE_STATISTIC].threshold
    moved = dataclasses.replace(fgl.BANDS[fgl.TEXTURE_STATISTIC], threshold=0.20)
    monkeypatch.setitem(fgl.BANDS, fgl.TEXTURE_STATISTIC, moved)

    texture = cf.two_level(panel, weather).cell(fgl.TEXTURE_STATISTIC)

    # The mutation reached the real measurement...
    assert fgl.BANDS[fgl.TEXTURE_STATISTIC].threshold != published_floor
    assert texture.band.threshold == 0.20
    # ...and the cell it produces is one the control refuses. Every home on the
    # panel reads between 0.153 and 0.288, so a 0.20 floor puts real homes in
    # breach rather than an invented one.
    assert texture.homes_violating > 0, texture.note
    with pytest.raises(AssertionError, match="fell"):
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

    THE ACCEPT ARM IS REAL AGAIN SINCE H36 (2026-08-10). While the panel's worst
    texture cell was in breach there was no unmutated cell to demonstrate the pass
    side with, and it had to be constructed from the real cell and the real band.
    The cell clears now, so the pass arm below is asserted on the measurement
    itself first and the constructed one is kept as the boundary check.

    Generator-side proof that the real physics can drive this statistic through
    the real band lives one suite over (`tests/harness/test_premise_two_level.py`,
    the `_flatten_behaviour` mutation), and the fail-open the old reading had is
    measured above.
    """
    texture = cf.two_level(panel, weather).cell(fgl.TEXTURE_STATISTIC)
    floor = texture.band.threshold

    _worst_cell_clears_its_own_floor(texture)          # the measured cell itself

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
    a, _, _ = cf.observe(cf.build_panel(weather, seed=17, limit=5), weather)
    b, _, _ = cf.observe(cf.build_panel(weather, seed=17, limit=5), weather)
    assert [o.inferred_hlc_kw_per_k for o in a] == [o.inferred_hlc_kw_per_k for o in b]


def test_a_DIFFERENT_seed_moves_the_world_but_the_panel_still_measures(weather):
    """Independence: the finding must not rest on one lucky draw."""
    other, _, _ = cf.observe(cf.build_panel(weather, seed=99, limit=8), weather)
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
    # A CERTIFICATED premise, chosen by the register rather than by position: since
    # §2c an uncertificated draw reaches the company as nothing at all, so `drawn[0]`
    # would be testing the refusal, not the wall.
    premise_id, household, trace, commodity, cadence, lodged = next(
        entry for entry in drawn if entry[5] is not None
    )
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
    )
    assert belief.hlc_kw_per_k > 0.0


def test_a_drawn_population_measures_a_gap_end_to_end(drawn, weather):
    """The orphan-transition rule (R11) applied to the new path: the population
    flag must reach a NUMBER, not merely construct premises."""
    observations, detail, no_belief = cf.observe(drawn, weather)
    # THE POPULATION IS ACCOUNTED FOR IN FULL. Since §2c a premise may leave the
    # measured set, and the one thing that must never happen is a premise leaving
    # it and being counted nowhere — that is the shape in which a gap quietly
    # becomes a gap on the homes the register happens to describe.
    assert len(observations) == len(detail)
    assert len(observations) + len(no_belief) == len(drawn)
    assert no_belief, "a 200-premise draw must contain uncertificated premises"
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
