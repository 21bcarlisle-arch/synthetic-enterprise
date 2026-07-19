"""Phase-close hygiene check for the maturity-map VIEW FACETS
(ONE_FRAMEWORK.md §7 sub-step 1, C3 + C5).

This is a phase-close-style CHECK (the two pure `check_*` functions) plus its
own R15 mutation tests (a control is only real if it can FAIL on its named
defect). It guards two facets that are VIEW-ONLY -- the draw never reads them:

  (a) value_stream hygiene (C3): every atom carries a real value-stream, and
      `close_to_learn` is only ever a REVIEWED classification, never the
      unreviewed default a new atom inherits. Any atom sitting at
      `close_to_learn` that is not on the curated reviewed list is a violation
      -- which is exactly what forces a newly-registered atom to be classified.

  (b) couples_with topology (C5): the coupled world<->company pairs the atoms
      themselves declare are present and SYMMETRIC, and no atom whose own
      name/twin declares a coupling and targets L3+ is left without a twin
      (the registration defect COUPLED_TRIAD_DESIGN §4 names).

Run as a phase-close gate:  python3 -m tests.design.test_maturity_map_facets
(exits non-zero and prints the violations). Or as pytest (the tests below).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parent.parent.parent
MAP_PATH = PROJECT / "docs" / "design" / "maturity_map.yaml"

VALID_STREAMS = {"meter_to_cash", "price_to_bill", "wholesale_to_price", "close_to_learn"}

# The genuinely-close_to_learn atoms, reviewed 2026-07-18 (ONE_FRAMEWORK §7
# sub-step 1). These are the finance-CLOSE (E), governance/strategy (A),
# risk/compliance-assurance (F), data/learning-method (G), harness/ops/method
# (H), and the-wall architecture (W4) atoms -- none is a revenue-flow movement,
# so `close_to_learn` is their TRUE stream, not a dumping-ground default.
# A `close_to_learn` atom absent from this set = the unreviewed default = a
# violation (this is the mechanism that forces every new atom to be classified).
REVIEWED_CLOSE_TO_LEARN = {
    "G1_fidelity_grid_scorer", "G2_fidelity_evidence_ledger", "G3_fidelity_inspection_chain",
    "A1_learn_loop_chair", "A2_decision_rights_register", "A3_approval_interface",
    "A4_sim_approver", "A5_tournament_fitness_mortality", "A6_coupled_triad_gap_metric",
    "A7_harm_cost_weights_decision", "A8_experiment_loop_speed",
    "ARCH1_internal_seams", "BRAND1_identity_system",
    "E1_ledger_double_entry", "E2_revenue_reconciliation", "E3_accrual_restatement",
    "E4_supplier_reporting_standard",
    "F1_epistemic_verifier", "F2_sanity_daemon", "F3_obligations_register",
    "F4_company_internal_authz", "F5_ofgem_licence_readiness",
    "F5_vat_control_independent_signal", "F6_bill_integrity_structural",
    "F7_obligations_register_coverage", "F8_control_gap_fixes_kl4_kl8",
    "G1_test_progression_metrics", "G2_event_log_shared_with_spine",
    "G3_method_ip_worktree_retro", "G4_unified_failure_register",
    "G5_effort_sizing_discipline", "G6_method_lens_audit", "G7_wip_cycle_time_dashboard",
    "G8_constraint_identification_ritual", "G9_error_budget_toil_tracking",
    "G10_definition_of_ready_gate", "G11_activity_cost_utilisation",
    "H1_supervisor_turn_granting", "H2_tree_lock_concurrency",
    "H3_production_readiness_nfr_evidence", "H4_go_live_nfr_register",
    "H5_security_profiles", "H6_lane_wall_development_pilot", "H7_skills_and_rules",
    "H8_harness_bootstrap_dr", "H9_map_write_serialisation", "H10_worktree_isolation",
    "H11_naive_organ", "H12_mutation_test_controls", "H14_judge_validation",
    "H15_publish_gate_failure_alert", "H16_idle_detection_stability_gate",
    "H17_autonomous_build_executor", "H18_harness_self_mutation_audit",
    "H19_escalation_ntfy_route_around", "H20_parallel_maintenance_lane",
    "H21_self_contained_escalation", "H22_scheduled_housekeeping",
    "H23_frame_saturation_draw_marker", "H23_publish_gate_scope_marker",
    "H24_precommit_gate_git_env_isolation", "H24_worktree_dir_autoreap",
    "H25_self_gov_detection_hardening", "H26_core_bare_corruption_guard",
    "H27_phone_act_channel",  # 2026-07-18 reviewed: governance/authority infra (director phone-[ACT] channel) -- shortens the director-decision feedback loop, the same close_to_learn class as its siblings H25/H26/G10/A3
    "H_draw_excludes_external_blocked_atoms",
    "OPS1_operational_layer_rebuild", "OPS1_session_watchdog_collapse",
    "OPS1_tmux_target_qualification", "OPS1_governance_refusal_mutation_test",
    "OPS1_transport_failure_must_be_loud",
    "SITE1_expert_doors",
    "W4_1_typed_adapters", "W4_2_verifier_timing_extension", "W4_3_external_truth_wall",
}

# The coupled topology landed in the yaml (C5). Each pair is world<->company as
# the atoms themselves declare (real_world_twin "world twin of"/"company twin
# of", or a "COUPLED" name). Both members must carry couples_with naming the
# other. Kept here as the authority the symmetry check validates against.
EXPECTED_PAIRS = {
    frozenset(("W1_5_premise_demand_shape", "C13_weather_normalisation")),
    frozenset(("W1_8_zonal_locational_pricing", "B5_regional_basis_risk")),
    frozenset(("W2_4_household_budget", "C6_affordability_inference")),
    frozenset(("W2_2_population_draw", "C6_affordability_inference")),
    frozenset(("W2_5_life_event_stream", "C7_life_event_detection")),
    frozenset(("W2_6_sme_distress_twin", "C8_sme_credit_risk")),
    frozenset(("W2_7_willingness_classification", "C9_cantpay_wontpay_classifier")),
    frozenset(("W2_8_self_rationing", "C10_self_rationing_detection")),
    frozenset(("W2_9_segment_debt_tnc", "C11_segment_debt_policy")),
    frozenset(("W2_10_dd_attribution_confound", "C12_channel_attribution_analytics")),
}

# An atom "declares a coupling" if its own text says so. Such an atom targeting
# L3+ MUST carry a couples_with twin (else it can never reach its own target --
# COUPLED_TRIAD §4 registration defect).
_DECLARES_COUPLING = re.compile(r"COUPLED|world twin of W|company twin of W")


# ── pure checks (feedable synthetic atoms for mutation testing) ──────────────

def check_value_stream_hygiene(atoms: list) -> list:
    """Return a list of human-readable violation strings (empty == pass)."""
    violations = []
    for a in atoms:
        if not isinstance(a, dict):
            continue
        aid = a.get("id", "<no-id>")
        vs = a.get("value_stream")
        if vs not in VALID_STREAMS:
            violations.append(
                f"{aid}: value_stream={vs!r} is not one of {sorted(VALID_STREAMS)}"
            )
            continue
        if vs == "close_to_learn" and aid not in REVIEWED_CLOSE_TO_LEARN:
            violations.append(
                f"{aid}: value_stream=close_to_learn but NOT in the reviewed "
                "close_to_learn list -- classify it to its true value-stream, "
                "or add it to REVIEWED_CLOSE_TO_LEARN once genuinely reviewed "
                "(this is the default-dumping-ground defect, C3)."
            )
    return violations


def check_coupling_symmetry(atoms: list) -> list:
    """Every EXPECTED pair present in the map, both members naming each other.
    Meaningful over the full map (validates the landed topology)."""
    violations = []
    by_id = {a["id"]: a for a in atoms if isinstance(a, dict) and a.get("id")}
    for pair in EXPECTED_PAIRS:
        a_id, b_id = tuple(pair)
        for x, y in ((a_id, b_id), (b_id, a_id)):
            atom = by_id.get(x)
            if atom is None:
                violations.append(f"expected coupled atom {x} missing from map")
                continue
            cw = atom.get("couples_with") or []
            if y not in cw:
                violations.append(
                    f"{x}: couples_with={cw} does not name its declared twin {y} "
                    "(asymmetric/absent coupling topology, C5)."
                )
    return violations


def check_orphaned_coupled_targets(atoms: list) -> list:
    """No L3+ atom whose own text declares a coupling may lack a couples_with
    twin. Works over any atom set (the generic registration rule, COUPLED_TRIAD
    §4)."""
    violations = []
    for a in atoms:
        if not isinstance(a, dict):
            continue
        lt = a.get("level_target")
        if not isinstance(lt, int) or lt < 3:
            continue
        text = f"{a.get('name', '')} {a.get('real_world_twin', '')}"
        if _DECLARES_COUPLING.search(text) and not (a.get("couples_with") or []):
            violations.append(
                f"{a.get('id')}: level_target={lt} and its text declares a coupling, "
                "but couples_with is empty -- a world/company atom that cannot "
                "reach L3 without a measured twin gap (COUPLED_TRIAD §4)."
            )
    return violations


def check_coupling_topology(atoms: list) -> list:
    """Both coupling checks, for the phase-close gate over the live map."""
    return check_coupling_symmetry(atoms) + check_orphaned_coupled_targets(atoms)


def _load_live_atoms() -> list:
    return yaml.safe_load(MAP_PATH.read_text())


# ── tests over the LIVE map (the phase-close gate itself) ────────────────────

def test_live_map_value_stream_hygiene():
    violations = check_value_stream_hygiene(_load_live_atoms())
    assert not violations, "value_stream hygiene:\n  " + "\n  ".join(violations)


def test_live_map_coupling_topology():
    violations = check_coupling_topology(_load_live_atoms())
    assert not violations, "coupling topology:\n  " + "\n  ".join(violations)


def test_reviewed_list_has_no_stale_ids():
    """Every id on the reviewed list must still exist in the map AND still be
    close_to_learn -- a stale allowlist would silently pass a re-classified
    atom. (Keeps the mechanism honest as the map evolves.)"""
    by_id = {a["id"]: a for a in _load_live_atoms() if isinstance(a, dict)}
    stale = [i for i in REVIEWED_CLOSE_TO_LEARN
             if i not in by_id or by_id[i].get("value_stream") != "close_to_learn"]
    assert not stale, f"stale REVIEWED_CLOSE_TO_LEARN ids: {stale}"


# ── R15 mutation tests: the check must FIRE on its own named defects ─────────

def test_value_stream_check_fires_on_unreviewed_default():
    # a NEW atom defaulting to close_to_learn (not on the reviewed list) -> fail
    bad = [{"id": "Z9_freshly_registered", "value_stream": "close_to_learn",
            "level_target": 2, "name": "n", "real_world_twin": "t"}]
    assert check_value_stream_hygiene(bad), "must fire on an unreviewed close_to_learn default"


def test_value_stream_check_fires_on_missing_or_bad_stream():
    assert check_value_stream_hygiene([{"id": "X", "value_stream": None}])
    assert check_value_stream_hygiene([{"id": "Y", "value_stream": "not_a_stream"}])


def test_value_stream_check_passes_a_reviewed_close_to_learn_atom():
    good_id = next(iter(REVIEWED_CLOSE_TO_LEARN))
    assert not check_value_stream_hygiene(
        [{"id": good_id, "value_stream": "close_to_learn"}]
    )


def test_value_stream_check_passes_a_classified_atom():
    assert not check_value_stream_hygiene(
        [{"id": "whatever", "value_stream": "meter_to_cash"}]
    )


def test_coupling_check_fires_on_l3_declared_twinless_atom():
    # an atom that declares a coupling and targets L3 but has no couples_with
    bad = [{"id": "W9_new_world", "name": "COUPLED thing",
            "real_world_twin": "world twin of W9", "level_target": 3,
            "couples_with": []}]
    assert check_orphaned_coupled_targets(bad), \
        "must fire on an L3 coupling-declaring twinless atom"


def test_coupling_check_fires_on_broken_symmetry():
    # W1_5 names its twin but the twin does NOT name it back -> asymmetry
    atoms = [
        {"id": "W1_5_premise_demand_shape", "couples_with": ["C13_weather_normalisation"],
         "level_target": 3, "name": "", "real_world_twin": ""},
        {"id": "C13_weather_normalisation", "couples_with": [],
         "level_target": 3, "name": "", "real_world_twin": ""},
    ]
    viol = check_coupling_symmetry(atoms)
    assert any("C13_weather_normalisation" in v for v in viol)


def test_coupling_check_ignores_solo_l3_atom():
    # a plain L3 atom that declares no coupling must NOT be forced to have a twin
    solo = [{"id": "E1_ledger_double_entry", "name": "Double-entry ledger",
             "real_world_twin": "a real supplier's statutory accounts",
             "level_target": 3, "couples_with": []}]
    assert not check_orphaned_coupled_targets(solo)


# ── phase-close CLI entry point ──────────────────────────────────────────────

def _main() -> int:
    atoms = _load_live_atoms()
    violations = check_value_stream_hygiene(atoms) + check_coupling_topology(atoms)
    if violations:
        print("MATURITY-MAP FACET HYGIENE: FAIL")
        for v in violations:
            print("  -", v)
        return 1
    print(f"MATURITY-MAP FACET HYGIENE: PASS ({len(atoms)} atoms)")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
