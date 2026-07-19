"""Tests for background/fidelity_inspection_chain.py -- atom G3, the
four-layer fidelity-evidence inspection chain (Epoch-2 G_data_learning
lane, HARNESS-side).

Per R15 ("a control that cannot fail is worse than none"), the load-bearing
controls here are each proven with a MUTATION test: introduce the named
defect and assert the control fires, remove it and assert clean -- not just
a happy-path acceptance test.

    * `assert_no_belief_leak` -- the wall-discipline control: a BELIEF_ACTION
      record carrying a non-null `truth_ref` must be caught.
    * `validate_links` -- a dangling link (edge referencing a missing node)
      must be caught, fail-closed.
    * `causes_of` / `consequences_of` -- correctness proven on a small
      hand-built chain, including a mutation that REVERSES a link's
      direction and asserts the traversal result actually changes (proof
      the traversal respects edge direction rather than being a tautology).
"""

import pytest

from background import fidelity_inspection_chain as fic


# ---------------------------------------------------------------------------
# Fixtures / helpers -- one small, hand-built, fully-linked chain matching
# S4's canonical worked example: a weather-cascade relationship (EVIDENCE)
# drives a WORLD series, which the company observes into a BELIEF/ACTION,
# which is bent by a CONSTRAINT that in turn cites back to the EVIDENCE it
# prevented exploitation of (closing the canonical cycle).
# ---------------------------------------------------------------------------

def _evidence(rel_id="D1_temp_wind_winter_lowtail", **overrides):
    rel = {
        "kind": "joint_tail_lift",
        "strength": {"stat": "L", "value": 2.34, "u": 0.10, "ci": [1.7, 3.1]},
        "provenance": "estimated_from_data",
        "series_ref": "W1_3 4pt proxy",
        "independent_anchor": "NESO low-wind-cold stress",
        "simplification_id": None,
    }
    rel.update(overrides)
    return fic.EvidenceRecord(rel_id=rel_id, relationship=rel)


def _world(world_series_ref="W_2019_01_cold_snap", driven_by=("D1_temp_wind_winter_lowtail",)):
    return fic.WorldRecord(
        world_series_ref=world_series_ref,
        variables=("temperature_mean", "wind_speed_mean"),
        regime_label="crisis_low_wind_cold",
        driven_by=driven_by,
    )


def _belief(belief_id="B_A2_G3_2019W03", observed_world_ref="W_2019_01_cold_snap",
            cites_evidence=("D1_temp_wind_winter_lowtail",), truth_ref=None):
    return fic.BeliefActionRecord(
        belief_id=belief_id,
        cell="A2_G3",
        belief={"expected_shortfall_risk": "moderate"},
        action={"hedge_cover": 0.87},
        gap=0.21,
        as_of="2019-01-28T00:00:00+00:00",
        observed_world_ref=observed_world_ref,
        cites_evidence=cites_evidence,
        truth_ref=truth_ref,
    )


def _constraint(constraint_id="C_collateral_2019W03", bends_action="B_A2_G3_2019W03",
                 prevents_evidence=("D1_temp_wind_winter_lowtail",)):
    return fic.ConstraintRecord(
        constraint_id=constraint_id,
        binding_constraint="collateral_capacity",
        naive_optimum={"hedge_cover": 0.92},
        trade_off="hedged to 0.87 not naive VaR-min 0.92 because collateral capacity bound",
        shadow_price=12.5,
        transversal_pressure="cash",
        bends_action=bends_action,
        prevents_evidence=prevents_evidence,
    )


def _full_chain():
    chain = fic.InspectionChain()
    chain.add_evidence(_evidence())
    chain.add_world(_world())
    chain.add_belief_action(_belief())
    chain.add_constraint(_constraint())
    return chain


def _dag_chain():
    """The same EVIDENCE/WORLD/BELIEF_ACTION trio as `_full_chain`, but
    WITHOUT the CONSTRAINT layer -- so there is no `prevents_exploitation_of`
    edge closing the cycle back to EVIDENCE. This is a plain DAG (EVIDENCE
    -> WORLD -> BELIEF_ACTION, plus the direct EVIDENCE -> BELIEF_ACTION
    `cites_evidence` edge), used where a test wants an EXACT, non-cyclic
    reachability set rather than `_full_chain`'s fully-connected cycle."""
    chain = fic.InspectionChain()
    chain.add_evidence(_evidence())
    chain.add_world(_world())
    chain.add_belief_action(_belief())
    return chain


# ===========================================================================
# Record types -- basic construction / validation
# ===========================================================================

def test_evidence_record_node_id_is_namespaced():
    rec = _evidence()
    assert rec.node_id == "EVIDENCE::D1_temp_wind_winter_lowtail"


def test_world_record_node_id_is_namespaced():
    rec = _world()
    assert rec.node_id == "WORLD::W_2019_01_cold_snap"


def test_belief_action_record_node_id_is_namespaced():
    rec = _belief()
    assert rec.node_id == "BELIEF_ACTION::B_A2_G3_2019W03"


def test_constraint_record_node_id_is_namespaced():
    rec = _constraint()
    assert rec.node_id == "CONSTRAINT::C_collateral_2019W03"


def test_evidence_record_rejects_empty_rel_id():
    with pytest.raises(ValueError):
        fic.EvidenceRecord(rel_id="", relationship={})


def test_belief_action_record_requires_as_of_pit_stamp():
    with pytest.raises(ValueError):
        fic.BeliefActionRecord(
            belief_id="b1", cell="A2_G3", belief={}, action={}, gap=0.1, as_of="",
        )


def test_a_world_and_evidence_id_that_share_a_string_do_not_collide():
    """Namespacing (S4's node-id design) must prevent a WORLD ref and an
    EVIDENCE rel_id that happen to be the same raw string from colliding
    into one graph node."""
    chain = fic.InspectionChain()
    chain.add_evidence(fic.EvidenceRecord(rel_id="shared_name", relationship={"kind": "x"}))
    chain.add_world(fic.WorldRecord(
        world_series_ref="shared_name", variables=(), regime_label=None, driven_by=(),
    ))
    assert len(chain.nodes) == 2
    assert "EVIDENCE::shared_name" in chain.nodes
    assert "WORLD::shared_name" in chain.nodes


# ===========================================================================
# Link graph construction -- the canonical five edges auto-derived
# ===========================================================================

def test_add_world_derives_produces_edge_from_evidence():
    chain = fic.InspectionChain()
    chain.add_evidence(_evidence())
    chain.add_world(_world())
    kinds = {(l.cause_id, l.consequence_id, l.kind) for l in chain.links}
    assert ("EVIDENCE::D1_temp_wind_winter_lowtail", "WORLD::W_2019_01_cold_snap", "produces") in kinds


def test_add_belief_action_derives_observed_by_and_cites_edges():
    chain = fic.InspectionChain()
    chain.add_evidence(_evidence())
    chain.add_world(_world())
    chain.add_belief_action(_belief())
    kinds = {(l.cause_id, l.consequence_id, l.kind) for l in chain.links}
    assert ("WORLD::W_2019_01_cold_snap", "BELIEF_ACTION::B_A2_G3_2019W03", "observed_by") in kinds
    assert ("EVIDENCE::D1_temp_wind_winter_lowtail", "BELIEF_ACTION::B_A2_G3_2019W03", "cites_evidence") in kinds


def test_add_constraint_derives_bent_by_and_prevents_edges():
    chain = _full_chain()
    kinds = {(l.cause_id, l.consequence_id, l.kind) for l in chain.links}
    assert ("BELIEF_ACTION::B_A2_G3_2019W03", "CONSTRAINT::C_collateral_2019W03", "bent_by") in kinds
    assert ("CONSTRAINT::C_collateral_2019W03", "EVIDENCE::D1_temp_wind_winter_lowtail",
            "prevents_exploitation_of") in kinds


# ===========================================================================
# causes_of / consequences_of -- correctness on the hand-built chain
# ===========================================================================

def test_consequences_of_evidence_reaches_every_downstream_layer():
    """S4's 'relationship -> consequences' query: an EVIDENCE rel_id ->
    forward through WORLD -> BELIEF/ACTION -> CONSTRAINT (and, via the
    canonical cycle, back to EVIDENCE itself is excluded -- see
    `_traverse`'s `dst != start_id` guard)."""
    chain = _full_chain()
    result = chain.consequences_of("EVIDENCE::D1_temp_wind_winter_lowtail")
    assert result == {
        "WORLD::W_2019_01_cold_snap",
        "BELIEF_ACTION::B_A2_G3_2019W03",
        "CONSTRAINT::C_collateral_2019W03",
    }


def test_causes_of_belief_action_reaches_world_and_evidence():
    """S4's 'odd output -> cause' query, on the DAG variant (no CONSTRAINT
    layer, so no cycle back to EVIDENCE): a BELIEF/ACTION gap -> back to
    the WORLD it observed and the EVIDENCE it cites, exactly."""
    chain = _dag_chain()
    result = chain.causes_of("BELIEF_ACTION::B_A2_G3_2019W03")
    assert result == {
        "WORLD::W_2019_01_cold_snap",
        "EVIDENCE::D1_temp_wind_winter_lowtail",
    }


def test_causes_of_world_is_exactly_its_evidence():
    chain = _dag_chain()
    assert chain.causes_of("WORLD::W_2019_01_cold_snap") == {
        "EVIDENCE::D1_temp_wind_winter_lowtail",
    }


def test_full_chain_is_strongly_connected_via_the_canonical_cycle():
    """`_full_chain` closes the cycle EVIDENCE->WORLD->BELIEF_ACTION->
    CONSTRAINT->EVIDENCE (via the `prevents_exploitation_of` edge) --
    correctly, this makes the four nodes strongly connected, so BOTH
    causes_of and consequences_of of ANY node reach every OTHER node (you
    can walk all the way round the cycle in either direction). This is the
    concrete form of S4's own worked example: starting from the CONSTRAINT
    layer, forward traversal legitimately reaches back to the EVIDENCE
    whose exploitation it prevented (and, transitively, everything that
    evidence in turn drives)."""
    chain = _full_chain()
    all_ids = set(chain.nodes.keys())
    for node_id in all_ids:
        others = all_ids - {node_id}
        assert chain.causes_of(node_id) == others
        assert chain.consequences_of(node_id) == others


def test_traversal_is_cycle_safe_and_terminates():
    """The canonical EVIDENCE->WORLD->BELIEF_ACTION->CONSTRAINT->EVIDENCE
    cycle must not infinite-loop; both directions from any node must
    terminate and never include the start node itself."""
    chain = _full_chain()
    for node_id in chain.nodes:
        causes = chain.causes_of(node_id)
        consequences = chain.consequences_of(node_id)
        assert node_id not in causes
        assert node_id not in consequences


def test_mutation_reversing_a_link_direction_changes_traversal_result():
    """R15 graph-correctness mutation: build a plain 3-node chain
    A -> B -> C. causes_of(C) must be {A, B} and consequences_of(A) must be
    {B, C}. Reversing the B->C edge to C->B must CHANGE the result --
    proof that causes_of/consequences_of genuinely respect edge direction
    rather than returning something direction-independent (a tautological
    'connected component' check would pass this mutation undetected)."""
    chain = fic.InspectionChain()
    chain.add_evidence(fic.EvidenceRecord(rel_id="A", relationship={"kind": "x"}))
    chain.add_world(fic.WorldRecord(
        world_series_ref="B", variables=(), regime_label=None, driven_by=("A",),
    ))
    chain.add_belief_action(fic.BeliefActionRecord(
        belief_id="C", cell="cell1", belief={}, action={}, gap=0.0,
        as_of="2019-01-01T00:00:00+00:00", observed_world_ref="B",
    ))

    # Before mutation: correct direction.
    assert chain.causes_of("BELIEF_ACTION::C") == {"EVIDENCE::A", "WORLD::B"}
    assert chain.consequences_of("EVIDENCE::A") == {"WORLD::B", "BELIEF_ACTION::C"}

    # Mutate: reverse the WORLD->BELIEF_ACTION edge (B->C becomes C->B).
    reversed_chain = fic.InspectionChain()
    reversed_chain.add_node(fic.EvidenceRecord(rel_id="A", relationship={"kind": "x"}))
    reversed_chain.add_node(fic.WorldRecord(
        world_series_ref="B", variables=(), regime_label=None, driven_by=(),
    ))
    reversed_chain.add_node(fic.BeliefActionRecord(
        belief_id="C", cell="cell1", belief={}, action={}, gap=0.0,
        as_of="2019-01-01T00:00:00+00:00",
    ))
    reversed_chain.link("EVIDENCE::A", "WORLD::B", kind="produces")
    reversed_chain.link("BELIEF_ACTION::C", "WORLD::B", kind="observed_by_REVERSED")

    # The reversal MUST be caught: causes_of(C) no longer includes B (or A),
    # and consequences_of(A) no longer reaches C.
    assert reversed_chain.causes_of("BELIEF_ACTION::C") == set()
    assert reversed_chain.consequences_of("EVIDENCE::A") == {"WORLD::B"}
    assert "BELIEF_ACTION::C" not in reversed_chain.consequences_of("EVIDENCE::A")


# ===========================================================================
# validate_links -- dangling-link fail-closed guard (R15)
# ===========================================================================

def test_validate_links_passes_on_fully_linked_chain():
    chain = _full_chain()
    fic.validate_links(chain)  # must not raise


def test_R15_validate_links_reds_on_dangling_cause():
    chain = fic.InspectionChain()
    chain.add_node(fic.WorldRecord(
        world_series_ref="B", variables=(), regime_label=None, driven_by=(),
    ))
    chain.link("EVIDENCE::missing_rel", "WORLD::B", kind="produces")
    with pytest.raises(fic.DanglingLink):
        fic.validate_links(chain)


def test_R15_validate_links_reds_on_dangling_consequence():
    chain = fic.InspectionChain()
    chain.add_node(fic.EvidenceRecord(rel_id="A", relationship={"kind": "x"}))
    chain.link("EVIDENCE::A", "WORLD::missing_series", kind="produces")
    with pytest.raises(fic.DanglingLink):
        fic.validate_links(chain)


def test_R15_validate_links_clears_once_dangling_node_is_registered():
    """Same scenario as the dangling-cause test, but the missing node is
    then registered -- the check must go from red to clean, proving it
    isn't just permanently red / tautologically broken."""
    chain = fic.InspectionChain()
    chain.add_node(fic.WorldRecord(
        world_series_ref="B", variables=(), regime_label=None, driven_by=(),
    ))
    chain.link("EVIDENCE::missing_rel", "WORLD::B", kind="produces")
    with pytest.raises(fic.DanglingLink):
        fic.validate_links(chain)

    chain.add_node(fic.EvidenceRecord(rel_id="missing_rel", relationship={"kind": "x"}))
    fic.validate_links(chain)  # now clean


# ===========================================================================
# assert_no_belief_leak -- THE load-bearing wall-discipline control (R15)
# ===========================================================================

def test_R15_belief_leak_is_caught_when_truth_ref_present():
    chain = fic.InspectionChain()
    chain.add_belief_action(_belief(truth_ref="SIM_ANSWER_KEY::A2_G3::2019W03"))
    with pytest.raises(fic.BeliefLeakError):
        fic.assert_no_belief_leak(chain)


def test_R15_belief_leak_clears_once_truth_ref_removed():
    """The SAME belief record, with truth_ref stripped, must validate
    clean -- proof the control fires on the specific defect and clears
    when it's gone, not a permanently-red or permanently-green check."""
    chain = fic.InspectionChain()
    chain.add_belief_action(_belief(truth_ref="SIM_ANSWER_KEY::A2_G3::2019W03"))
    with pytest.raises(fic.BeliefLeakError):
        fic.assert_no_belief_leak(chain)

    clean_chain = fic.InspectionChain()
    clean_chain.add_belief_action(_belief(truth_ref=None))
    fic.assert_no_belief_leak(clean_chain)  # must not raise


def test_belief_leak_check_names_the_offending_belief_id():
    chain = fic.InspectionChain()
    chain.add_belief_action(_belief(belief_id="B_bad", truth_ref="leaked"))
    with pytest.raises(fic.BeliefLeakError, match="B_bad"):
        fic.assert_no_belief_leak(chain)


def test_belief_leak_check_ignores_evidence_and_world_layers():
    """Only BELIEF_ACTION records are policed for truth_ref -- EVIDENCE and
    WORLD are harness-side by design and legitimately carry no such
    restriction. A chain with only those layers must validate clean even
    though it says nothing about company observability."""
    chain = fic.InspectionChain()
    chain.add_evidence(_evidence())
    chain.add_world(_world())
    fic.assert_no_belief_leak(chain)  # must not raise -- no BELIEF_ACTION nodes at all


def test_validate_chain_runs_both_fail_closed_checks():
    chain = _full_chain()
    fic.validate_chain(chain)  # clean chain: must not raise

    chain.add_belief_action(_belief(belief_id="B_leaky", truth_ref="leak"))
    with pytest.raises(fic.BeliefLeakError):
        fic.validate_chain(chain)
