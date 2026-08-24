"""Governance-registry CONTRACT for ``docs/design/maturity_map.yaml``.

``maturity_map.yaml`` is the machine-read governance registry: ~185 atoms whose
``id`` / lane / level / dependency fields drive the supervisor draw, the level
ledger, and the published /proof surface. It has never had a schema, and it has
drifted -- ids off the naming grammar, atom numbers reused within a lane,
dependency edges holding prose instead of atom ids, a required field left null.

This module is the contract test that FREEZES today's drift and makes any NEW
drift of the same class fail at ``pytest`` time. It follows the sibling
``tests/design/test_maturity_map_facets.py`` convention (same ``MAP_PATH`` idiom,
same "pure ``*_violations`` function + R15 mutation test" shape).

RATCHET DOCTRINE
----------------
Every known-drift instance is captured on a dated ``LEGACY_*`` allowlist defined
at the top of this file. The allowlists are RATCHETS: **they may only ever
shrink.** Cleaning up an atom (renaming it onto the grammar, renumbering a
collision, filling a missing field) means DELETING its allowlist entry -- and the
``*_allowlist_has_no_stale_entries`` tests below FAIL if an allowlist still lists
something that is no longer a violation, so a fix is not complete until its
entry is removed. Nothing may be ADDED to an allowlist to make a new violation
pass; a new violation is a red suite, which is the whole point.

R15 (controls must be able to FAIL): every ``check_*`` here has a paired
``test_*_mutation_*`` that injects the exact defect it guards and proves the
check fires, plus a restored-input case proving it passes when clean. A control
that cannot fail is worse than none.

Run as pytest, or standalone::

    python3 -m pytest tests/design/test_maturity_map_contract.py
"""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

import pytest
import yaml

PROJECT = Path(__file__).resolve().parent.parent.parent
MAP_PATH = PROJECT / "docs" / "design" / "maturity_map.yaml"

# ── the grammar (check a) ───────────────────────────────────────────────────
# LANE-prefix (upper alpha) + NUMBER (digits) + "_" + lower-snake slug.
ID_GRAMMAR = re.compile(r"^[A-Z]+[0-9]+_[a-z0-9_]+$")

# ── the lane+number key (check b) ───────────────────────────────────────────
# The number for a collision is the FULL leading numeric-token run after the
# alpha prefix -- digits, each optionally carrying one trailing letter (``6b``),
# joined by underscores. This deliberately treats the W-lane's hierarchical
# sub-numbering as DISTINCT (``W1_2`` -> "1_2", ``W1_3`` -> "1_3": not a
# collision) while catching genuine reuse (``H23_x`` and ``H23_y`` both -> "23").
_LANE_NUMBER = re.compile(r"^([A-Z]+)((?:[0-9]+[a-z]?)(?:_[0-9]+[a-z]?)*)")

REQUIRED_FIELDS = ("lane", "epoch", "level_current", "level_target")
EDGE_FIELDS = ("depends_on", "blocked_on")

# ============================================================================
# RATCHET ALLOWLISTS -- measured 2026-08-05 against the file at that commit.
# EACH MAY ONLY EVER SHRINK. See "RATCHET DOCTRINE" in the module docstring.
# Adding an entry to pass a NEW violation is forbidden; removing one when the
# underlying atom is cleaned up is required (enforced by the stale-entry tests).
# ============================================================================

# (a) ids that predate / break the LANE+NUMBER_slug grammar (25, 2026-08-05).
LEGACY_IDS = frozenset({
    "A_scope_of_need_scoring_frame",
    "C_supply_start_consumer_routing",
    "C_supply_start_semantic_separation",
    "DD_seasonal_cashflow_physics",
    "D_cascade_correlation_estimation",
    "D_money_boundary_reconciliation",
    "D_opening_dd_seasonal_sizing",
    "D_payments_maturity_audit",
    "D_printed_figure_rederivation",
    "F1a_sim_customer_response",
    "F1b_company_comms",
    "F1c_harness_conversation_gap",
    "H_GAP_fabric_belief_truth_gap",
    "H_draw_excludes_external_blocked_atoms",
    "H_stop_control_gap_characterisation",
    "OPS_run_marker_sweep_livelock",
    "SITE_EH1_segment_disclosure",
    "SITE_EH2_predictions_ledger_can_fail",
    "SITE_EH3_figure_reconciliation_and_periods",
    "SITE_director_window_delta_view",
    "SITE_evidence_pages_behind_nodes",
    "SPINE_1_scenario_world_state",
    "SPINE_3_gas_storage_crisis_regime",
})

# (b) atom NUMBERS reused within a lane (12 lane+number groups, 2026-08-05).
# Keyed by (lane_prefix, number) -> the EXACT set of ids currently colliding on
# that key. A collision passes only if its key is listed AND its current id-set
# is a subset of the listed set, so a NEW id joining an existing group (a 7th
# OPS1, say) or a brand-new group both fail.
LEGACY_NUMBER_COLLISIONS = {
    ("B", "3"): frozenset({
        "B3_hedge_tariff_alignment",
        "B3_published_forecast_error_horizons",
    }),
    ("B", "4"): frozenset({
        "B4_competitor_field",
        "B4_traded_product_ladder",
    }),
    ("B", "5"): frozenset({
        "B5_regional_basis_risk",
        "B5_shaped_cost_benchmark_value_add",
    }),
    ("F", "5"): frozenset({
        "F5_ofgem_licence_readiness",
        "F5_vat_control_independent_signal",
    }),
    ("G", "1"): frozenset({
        "G1_fidelity_grid_scorer",
        "G1_test_progression_metrics",
    }),
    ("G", "2"): frozenset({
        "G2_event_log_shared_with_spine",
        "G2_fidelity_evidence_ledger",
    }),
    ("G", "3"): frozenset({
        "G3_fidelity_inspection_chain",
        "G3_method_ip_worktree_retro",
    }),
    ("H", "23"): frozenset({
        "H23_frame_saturation_draw_marker",
        "H23_publish_gate_scope_marker",
    }),
    ("H", "24"): frozenset({
        "H24_precommit_gate_git_env_isolation",
        "H24_worktree_dir_autoreap",
    }),
    # ("H", "27") entry deleted 2026-08-24: `H27_phone_act_channel` was retired
    # (docs/design/RETIRED_ATOMS_2026-08-24.md) and the number no longer collides.
    ("OPS", "1"): frozenset({
        "OPS1_operational_layer_rebuild",
        "OPS1_session_watchdog_collapse",
        "OPS1_tmux_target_qualification",
        "OPS1_transport_failure_must_be_loud",
    }),
    ("W", "2"): frozenset({
        "W2_non_dd_miss_vocabulary",
        "W2_payment_channel_dd_consistency_invariant",
        "W2_sme_segment_case_normalisation",
    }),
}

# (e) atoms missing / null on a required field. Keyed by field -> ids.
# 2026-08-05: exactly one -- D_opening_dd_seasonal_sizing carries no ``epoch``.
LEGACY_MISSING_REQUIRED = {
    "epoch": frozenset({"D_opening_dd_seasonal_sizing"}),
}


# ============================================================================
# Loading + pure check helpers (take an atom list, return violations).
# Kept side-effect-free so the R15 mutation tests can feed synthetic atoms.
# ============================================================================

def load_atoms(path: Path = MAP_PATH) -> list:
    with open(path) as fh:
        data = yaml.safe_load(fh)
    assert isinstance(data, list), "maturity_map.yaml must be a top-level list of atoms"
    return data


def _lane_number_key(atom_id: str):
    """(lane_prefix, number) for the collision check, or None if id has no number."""
    m = _LANE_NUMBER.match(atom_id)
    return (m.group(1), m.group(2)) if m else None


def check_grammar(atoms) -> list:
    """(a) ids off the grammar that are not on the LEGACY_IDS allowlist."""
    return [
        a["id"] for a in atoms
        if not ID_GRAMMAR.match(a["id"]) and a["id"] not in LEGACY_IDS
    ]


def check_number_collisions(atoms) -> list:
    """(b) lane+number groups that collide but are not (fully) allowlisted.

    Returns ``(key, sorted_ids)`` tuples for each un-allowlisted collision.
    """
    buckets: dict = defaultdict(list)
    for a in atoms:
        key = _lane_number_key(a["id"])
        if key is not None:
            buckets[key].append(a["id"])

    violations = []
    for key, group in buckets.items():
        if len(group) < 2:
            continue  # unique -> fine
        allowed = LEGACY_NUMBER_COLLISIONS.get(key)
        if allowed is None or not set(group) <= allowed:
            violations.append((key, sorted(group)))
    return violations


def check_edges(atoms, id_set) -> list:
    """(c) depends_on/blocked_on, when given, must be a LIST of existing ids.

    A missing field or an explicit ``null`` means "no edge" and is fine. Any
    other shape (a bare string, i.e. prose) or a member that is not an atom id
    is a violation. Returns ``(atom_id, field, offending)`` tuples.
    """
    violations = []
    for a in atoms:
        for field in EDGE_FIELDS:
            if field not in a or a[field] is None:
                continue
            value = a[field]
            if not isinstance(value, list):
                violations.append((a["id"], field, value))  # prose / scalar edge
                continue
            for member in value:
                if member not in id_set:
                    violations.append((a["id"], field, member))
    return violations


def check_field_types(atoms) -> dict:
    """(d) every field must carry a SINGLE non-null type across all atoms.

    ``null`` and "absent" are allowed to coexist with a typed value (optional
    fields), but a field that is an ``int`` on one atom and a ``str`` on another
    is drift. Returns ``{field: {typenames}}`` for every field with >1 type.
    """
    seen: dict = defaultdict(set)
    for a in atoms:
        for field, value in a.items():
            if value is not None:
                seen[field].add(type(value).__name__)
    return {f: t for f, t in seen.items() if len(t) > 1}


def check_required_fields(atoms) -> list:
    """(e) lane/epoch/level_current/level_target present & non-null, minus allowlist.

    Returns ``(atom_id, field)`` tuples for each un-allowlisted missing/null.
    """
    violations = []
    for a in atoms:
        for field in REQUIRED_FIELDS:
            if a.get(field) is None:  # covers both absent and explicit null
                if a["id"] in LEGACY_MISSING_REQUIRED.get(field, frozenset()):
                    continue
                violations.append((a["id"], field))
    return violations


# ============================================================================
# CONTRACT TESTS -- run against the real, live map. Must be GREEN today and go
# RED the moment a new violation of any class is introduced.
# ============================================================================

@pytest.fixture(scope="module")
def atoms():
    return load_atoms()


@pytest.fixture(scope="module")
def id_set(atoms):
    ids = [a["id"] for a in atoms]
    assert len(ids) == len(set(ids)), "atom ids must be globally unique"
    return set(ids)


def test_a_every_id_matches_grammar_or_is_allowlisted(atoms):
    bad = check_grammar(atoms)
    assert bad == [], (
        "id(s) off the ^[A-Z]+[0-9]+_[a-z0-9_]+$ grammar and not on LEGACY_IDS "
        f"(rename onto the grammar, do NOT extend the allowlist): {bad}"
    )


def test_b_numeric_part_unique_per_lane_or_allowlisted(atoms):
    bad = check_number_collisions(atoms)
    assert bad == [], (
        "lane+number collision(s) not covered by LEGACY_NUMBER_COLLISIONS "
        f"(renumber, do NOT extend the allowlist): {bad}"
    )


def test_c_dependency_edges_are_lists_of_existing_ids(atoms, id_set):
    bad = check_edges(atoms, id_set)
    assert bad == [], (
        "depends_on/blocked_on holding prose or a non-existent id "
        f"(edges must be lists of atom ids): {bad}"
    )


def test_d_field_types_are_consistent_across_atoms(atoms):
    bad = check_field_types(atoms)
    assert bad == {}, f"field(s) carrying more than one non-null type: {bad}"


def test_e_required_fields_present_and_non_null(atoms):
    bad = check_required_fields(atoms)
    assert bad == [], (
        "atom(s) missing/null on a required field and not allowlisted "
        f"(lane/epoch/level_current/level_target): {bad}"
    )


# ============================================================================
# RATCHET-TIGHTNESS -- an allowlist may only ever shrink. These go RED if an
# allowlist still lists something that is no longer a violation, forcing the
# entry to be deleted when the underlying atom is cleaned up.
# ============================================================================

def test_legacy_ids_allowlist_has_no_stale_entries(atoms, id_set):
    present = {a["id"] for a in atoms}
    for legacy in LEGACY_IDS:
        assert legacy in present, f"LEGACY_IDS lists a vanished atom -- remove it: {legacy}"
        assert not ID_GRAMMAR.match(legacy), (
            f"LEGACY_IDS still lists {legacy}, which now MATCHES the grammar -- "
            "the ratchet may only shrink: delete this entry."
        )


def test_number_collision_allowlist_has_no_stale_entries(atoms):
    buckets: dict = defaultdict(set)
    for a in atoms:
        key = _lane_number_key(a["id"])
        if key is not None:
            buckets[key].add(a["id"])
    for key, allowed in LEGACY_NUMBER_COLLISIONS.items():
        current = buckets.get(key, set())
        assert allowed <= current, (
            f"LEGACY_NUMBER_COLLISIONS[{key}] lists id(s) no longer present -- "
            f"remove them: {sorted(allowed - current)}"
        )
        assert len(current) >= 2, (
            f"LEGACY_NUMBER_COLLISIONS[{key}] no longer collides (only {sorted(current)}) "
            "-- the ratchet may only shrink: delete this entry."
        )


def test_missing_required_allowlist_has_no_stale_entries(atoms):
    by_id = {a["id"]: a for a in atoms}
    for field, ids in LEGACY_MISSING_REQUIRED.items():
        for atom_id in ids:
            assert atom_id in by_id, (
                f"LEGACY_MISSING_REQUIRED[{field}] lists a vanished atom -- remove it: {atom_id}"
            )
            assert by_id[atom_id].get(field) is None, (
                f"LEGACY_MISSING_REQUIRED[{field}] still lists {atom_id}, which now HAS "
                f"{field} -- the ratchet may only shrink: delete this entry."
            )


# ============================================================================
# R15 MUTATION TESTS -- each control proven to FIRE on its own named defect,
# and to PASS when the defect is removed. Synthetic atoms only.
# ============================================================================

def _atom(**kw):
    """A minimal well-formed atom; override any field via kwargs."""
    base = {
        "id": "X1_ok", "lane": "H_harness", "epoch": 2,
        "level_current": 0, "level_target": 3,
    }
    base.update(kw)
    return base


def test_grammar_mutation_fires_and_restores():
    clean = [_atom(id="H1_clean")]
    assert check_grammar(clean) == []
    dirty = [_atom(id="not-a-valid-id")]  # off-grammar, not allowlisted
    assert check_grammar(dirty) == ["not-a-valid-id"]


def test_grammar_allowlisted_id_does_not_fire():
    legacy = next(iter(LEGACY_IDS))
    assert check_grammar([_atom(id=legacy)]) == []


def test_number_collision_mutation_fires_and_restores():
    # Two fresh ids sharing lane+number "Z9" -- not on the allowlist -> fires.
    dirty = [_atom(id="Z9_alpha"), _atom(id="Z9_beta")]
    bad = check_number_collisions(dirty)
    assert bad and bad[0][0] == ("Z", "9")
    # Distinct hierarchical sub-numbers do NOT collide (the W-lane case).
    clean = [_atom(id="Z9_1_alpha"), _atom(id="Z9_2_beta")]
    assert check_number_collisions(clean) == []


def test_number_collision_new_member_of_allowlisted_group_fires():
    # A 3rd H23 id -- the group is allowlisted for exactly two, so a new member fails.
    atoms = [_atom(id=i) for i in LEGACY_NUMBER_COLLISIONS[("H", "23")]]
    atoms.append(_atom(id="H23_a_brand_new_marker"))
    bad = check_number_collisions(atoms)
    assert bad and bad[0][0] == ("H", "23")


def test_edge_mutation_fires_on_prose_and_on_unknown_id_and_restores():
    ids = {"A1_a", "B1_b"}
    real = [_atom(id="A1_a"), _atom(id="B1_b", depends_on=["A1_a"], blocked_on=None)]
    assert check_edges(real, ids) == []
    prose = [_atom(id="A1_a", blocked_on="director_systemd_deploy")]  # scalar prose
    assert check_edges(prose, ids) == [("A1_a", "blocked_on", "director_systemd_deploy")]
    dangling = [_atom(id="A1_a", depends_on=["Z9_ghost"])]  # id not in set
    assert check_edges(dangling, ids) == [("A1_a", "depends_on", "Z9_ghost")]


def test_field_type_mutation_fires_and_restores():
    consistent = [_atom(id="A1_a", epoch=1), _atom(id="A2_b", epoch=2)]
    assert check_field_types(consistent) == {}
    mixed = [_atom(id="A1_a", epoch=1), _atom(id="A2_b", epoch="two")]  # int vs str
    assert "epoch" in check_field_types(mixed)


def test_field_type_null_coexists_with_a_typed_value():
    # An optional field: null on one atom, typed on another -> NOT a violation.
    mixed = [_atom(id="A1_a", blocked_on=None), _atom(id="A2_b", blocked_on=["A1_a"])]
    assert "blocked_on" not in check_field_types(mixed)


def test_required_field_mutation_fires_and_restores():
    clean = [_atom(id="A1_a")]
    assert check_required_fields(clean) == []
    missing = [_atom(id="A1_a")]
    del missing[0]["epoch"]
    assert check_required_fields(missing) == [("A1_a", "epoch")]
    explicit_null = [_atom(id="A1_a", level_current=None)]
    assert check_required_fields(explicit_null) == [("A1_a", "level_current")]


def test_required_field_allowlisted_atom_does_not_fire():
    field, ids = next(iter(LEGACY_MISSING_REQUIRED.items()))
    atom_id = next(iter(ids))
    atom = _atom(id=atom_id)
    del atom[field]
    assert check_required_fields([atom]) == []


# ============================================================================
# (f) THE SELF-MINT RATCHET -- 2026-08-24
# ============================================================================
#
# WHY THIS IS A CONTRACT CLAUSE AND NOT A NOTE IN CLAUDE.md. On 2026-08-24 `H_harness`
# held 135 of the map's 316 atoms and 44 of the 112 still below target: two of every five
# remaining work items in the project were the harness as its own subject. Sixty-two of the
# 135 were `provenance: proposal` -- authored by the agent, for the agent, under the standing
# licence in EPOCH_GATING_AND_ATOM_AUTHORSHIP.md -- and of the 23 below target NOT ONE had a
# dependent outside that set. Nineteen were deleted (docs/design/RETIRED_ATOMS_2026-08-24.md).
#
# Deleting rows fixes today's queue and nothing about tomorrow's, and CLAUDE.md's own decay
# rule is explicit that the difference between a rule that holds and a rule that evaporates
# is whether it is a mechanism: "every rule that DECAYED was an exhortation; every rule that
# HELD was a MECHANISM". So the count is a RATCHET, in the same doctrine as the LEGACY_*
# allowlists above: it may only ever shrink.
#
# WHAT IT DOES NOT FORBID, which is the reason it keys on provenance rather than on lane. A
# new harness atom carrying a director ruling, steer, programme or mandate, or an advisor
# artefact, is unaffected -- the director asking for harness work has never been the problem.
# What needs a bound is the agent commissioning it from itself, because that supply is
# infinite by construction and always tractable, which is exactly the combination that wins
# draws forever. Displacing an existing self-minted atom is also unaffected: close one, mint
# one.
SELF_MINTED_HARNESS_CEILING = 43


def check_self_minted_harness_ceiling(atoms) -> int | None:
    """(f) count of agent-authored H_harness atoms, or None when within the ratchet."""
    n = sum(
        1 for a in atoms
        if a.get("lane") == "H_harness" and a.get("provenance") == "proposal"
    )
    return n if n > SELF_MINTED_HARNESS_CEILING else None


def test_self_minted_harness_atoms_are_at_or_below_the_ratchet():
    n = check_self_minted_harness_ceiling(load_atoms())
    assert n is None, (
        f"{n} agent-authored (provenance: proposal) H_harness atoms, ceiling is "
        f"{SELF_MINTED_HARNESS_CEILING}. A new one needs a director ruling/steer/programme "
        f"or an advisor artefact behind it, or it has to displace one already there. "
        f"Lowering the ceiling to match a genuine cleanup is the ONLY edit this line takes."
    )


def test_MUTATION_one_atom_over_the_ratchet_fires():
    """R15: the control fires on its own named defect -- one self-minted atom too many."""
    atoms = [
        _atom(id=f"H{i}_x", lane="H_harness", provenance="proposal")
        for i in range(SELF_MINTED_HARNESS_CEILING + 1)
    ]
    assert check_self_minted_harness_ceiling(atoms) == SELF_MINTED_HARNESS_CEILING + 1


def test_MUTATION_a_director_provenance_harness_atom_does_NOT_count():
    """The null control on the subject set, and the clause that keeps this from being a lane cap.

    Same lane, same count, different provenance. If this ever reds, the ratchet has started
    refusing the director his own harness work, which is not what it was measured to fix.
    """
    atoms = [
        _atom(id=f"H{i}_x", lane="H_harness", provenance="director_ruling")
        for i in range(SELF_MINTED_HARNESS_CEILING * 2)
    ]
    assert check_self_minted_harness_ceiling(atoms) is None


def test_MUTATION_a_self_minted_atom_on_a_WORLD_lane_does_NOT_count():
    """The other null control: the ratchet is about the harness, not about self-authorship.

    Agent-authored atoms on the world and company lanes are the project working as designed
    -- they are where the fortnight's measurement said the project was UNDER-spending.
    """
    atoms = [
        _atom(id=f"W1_{i}_x", lane="W1_market_weather", provenance="proposal")
        for i in range(SELF_MINTED_HARNESS_CEILING * 2)
    ]
    assert check_self_minted_harness_ceiling(atoms) is None


if __name__ == "__main__":  # pragma: no cover
    import sys
    _atoms = load_atoms()
    _ids = {a["id"] for a in _atoms}
    problems = {
        "grammar": check_grammar(_atoms),
        "number_collisions": check_number_collisions(_atoms),
        "edges": check_edges(_atoms, _ids),
        "field_types": check_field_types(_atoms),
        "required_fields": check_required_fields(_atoms),
        "self_minted_harness": check_self_minted_harness_ceiling(_atoms),
    }
    live = {k: v for k, v in problems.items() if v}
    if live:
        print("CONTRACT VIOLATIONS:")
        for k, v in live.items():
            print(f"  {k}: {v}")
        sys.exit(1)
    print(f"maturity_map.yaml: {len(_atoms)} atoms, contract clean.")
