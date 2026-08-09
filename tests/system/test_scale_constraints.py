"""The five scale constraints as STANDING CHECKS — `AO4_scale_constraints_executable`.

Design: `docs/design/SCALE_CONSTRAINT_CHECKS.md`.
Constraints: `docs/staging/done/PRODUCTION_READINESS_SCALE_ADDENDUM.md` C-S1..C-S5.

Each test is one line of work: call the probe, run the assertion. Both live in
`scale_constraints.py` and are imported *verbatim* by the mutation proofs, so the
assertion these tests ship is the assertion R15 proves can fire.

These checks MEASURE the repository as it is, so one can go red because the
codebase is genuinely in breach — the atom's own origin_note predicts exactly
that. Softening a check because it went red would be R12: the output is a
diagnostic, never a target. That is what the report-only landing is for.

As landed, one residual is outstanding (C-S3's same-instant answer, carried as a
strict xfail so it fails the day it is fixed). The breach the registration
predicted — C-S4, money state in duplicate — turned out on correct measurement
not to be one; the mis-measurement that nearly reported it as one is worth
reading in `SCALE_CONSTRAINT_CHECKS.md` §3.
"""

import pytest

from tests.system import scale_constraints as sc

pytestmark = pytest.mark.scale_report_only

#: FROZEN. The company-side atoms already at L3+ when this check landed
#: (2026-08-09), pinned here so the register's own amnesty list cannot grow
#: silently — adding a name to the YAML without editing this set fails, which is
#: what stops a new undeclared L3+ atom from being parked in the amnesty.
FROZEN_CS5_BASELINE = {
    "A1_learn_loop_chair",
    "A2_decision_rights_register",
    "A6_coupled_triad_gap_metric",
    "B1_margin_bridge",
    "B2_opex_cost_to_serve",
    "C10_self_rationing_detection",
    "C12_channel_attribution_analytics",
    "C13_weather_normalisation",
    "C14_thermal_parameter_inference",
    "C1_segment_layers",
    "C3_satisfaction_heterogeneity",
    "C7_life_event_detection",
    "C9_cantpay_wontpay_classifier",
    "C_supply_start_semantic_separation",
    "D1_bill_correctness",
    "D3_catchup_rebilling",
    "D5_account_hierarchy_payments",
    "E1_ledger_double_entry",
    "E2_revenue_reconciliation",
    "E4_supplier_reporting_standard",
    "F1_epistemic_verifier",
    "F2_sanity_daemon",
    "F3_obligations_register",
}


# ── C-S1 — event-arrival tolerance ───────────────────────────────────────────

def test_cs1_a_bill_does_not_depend_on_the_order_its_events_arrived_in():
    sc.assert_arrival_order_tolerance(sc.probe_bill_arrival_order())


def test_cs1_a_late_event_is_resolved_by_transaction_time_not_append_order():
    sc.assert_late_arrival_tolerance(sc.probe_late_arrival_visibility())


# ── C-S2 — idempotency, replay, RNG substream discipline ─────────────────────

def test_cs2_delivering_the_same_event_twice_is_harmless():
    sc.assert_duplicate_delivery_is_harmless(sc.probe_duplicate_delivery())


def test_cs2_no_subsystem_draws_from_the_process_global_random_stream():
    sc.assert_no_global_rng_draws(sc.probe_global_rng_users())


def test_cs2_the_global_rng_scan_actually_reaches_the_stochastic_code():
    """NON-VACUITY for the guard above, stated against the REAL tree rather than
    inside the assertion: an empty offender set is only meaningful if the scan
    genuinely covered the packages where the draws live.

    A scan that silently resolved to nothing would report 'compliant' forever —
    an unavailable check is a FAILED check (R15).
    """
    record = sc.probe_global_rng_users()
    assert record["modules_scanned"] > 500, (
        "the global-RNG scan covered only "
        f"{record['modules_scanned']} modules across {sc.STOCHASTIC_PACKAGES} — far "
        "fewer than this codebase has. The scan is not reaching the code it audits."
    )


def test_cs2_adding_draws_to_one_subsystem_leaves_another_bit_identical():
    """A1's property, which the addendum's own DoD item 4 left open."""
    sc.assert_substream_independence(sc.probe_substream_independence())


# ── C-S3 — asynchronous wall contracts ───────────────────────────────────────

def test_cs3_a_request_and_its_answer_are_separate_events_in_time():
    sc.assert_request_and_response_are_separate_events(sc.probe_request_response_split())


@pytest.mark.xfail(
    strict=True,
    reason=(
        "KNOWN RESIDUAL, C-S3. The governed-decision mechanism REPRESENTS the pending "
        "interval but does not REQUIRE one: resolve_decision_request() accepts "
        "resolved_at == submitted_at and records a 0.0s latency, so A4's named "
        "exemplar (DD mandate submit-and-resolve in the same step) is still writable "
        "against the very mechanism built to replace it. Out of this atom's file_scope "
        "(tests/system/ + the design doc) — registered, not fixed on sight, per "
        "SELF_INTERRUPT_DISCIPLINE. strict=True so this test FAILS the day the "
        "mechanism is fixed, forcing the xfail off rather than leaving a green lie."
    ),
)
def test_cs3_a_same_instant_answer_is_rejected():
    sc.assert_same_step_resolution_is_rejected(sc.probe_same_step_resolution())


# ── C-S4 — persistence behind an interface ───────────────────────────────────

def test_cs4_durable_state_is_not_forked_across_copies():
    """The director-cited FINDING 2 (money state exists in duplicate) measured
    rather than described, against the REAL repo's HEAD. See
    SCALE_CONSTRAINT_CHECKS.md §C-S4 for what the measurement answered."""
    sc.assert_durable_state_is_not_forked(sc.probe_durable_state_duplication())


def test_cs4_the_published_reader_reads_the_commit_not_the_working_tree():
    """NON-VACUITY + INDEPENDENCE for the reader the check depends on.

    `_read_published` is the whole reason this check is stable, so it needs its own
    proof that it is doing what it claims: a path that exists in the commit
    resolves, and a path that exists ONLY in the working tree does not. Without
    this, a reader that silently fell back to reading files off disk would
    reintroduce the mid-publish window the design specifically excludes, and every
    test above would still pass.
    """
    # CLAUDE.md deliberately, not one of this atom's own new files: those are
    # untracked until the landing commit, so pinning one would make this test fail
    # in the pre-commit gate that is supposed to let it land.
    assert sc._read_published("CLAUDE.md") is not None, (
        "the published reader could not resolve a committed file — it is not "
        "reading HEAD at all"
    )
    assert sc._read_published("docs/state/no_such_file_ever.json") is None, (
        "the published reader resolved a path that is not in HEAD — it is falling "
        "back to the working tree, which is exactly the mid-publish window this "
        "check exists to exclude"
    )


def test_cs4_the_mirror_register_is_the_only_declared_duplication():
    """The containment half: the register is imported from the real mirror tool, so
    a new duplicated durable-state file that nobody declared shows up as undeclared
    rather than being quietly absorbed."""
    record = sc.probe_durable_state_duplication()
    assert record["undeclared_duplicates"] == {}, (
        "durable state is duplicated outside the mirror register: "
        f"{record['undeclared_duplicates']}"
    )


# ── C-S5 — time-scale invariance declaration ─────────────────────────────────

def test_cs5_every_company_side_l3_atom_has_answered_the_question():
    sc.assert_time_scale_declarations_cover_the_population(
        sc.probe_time_scale_declarations(), frozen_baseline=FROZEN_CS5_BASELINE
    )


def test_cs5_the_owed_population_is_derived_from_the_map_not_from_the_register():
    """INDEPENDENCE (R15 tautology check). The population that owes a declaration
    must come from the maturity map, not from the register that answers it —
    otherwise the register defines its own scope and can never be incomplete."""
    record = sc.probe_time_scale_declarations()
    assert record["owed"], "no company-side L3+ atoms found — the population is empty"
    assert record["owed"] - record["baseline"] - record["declared"] - record["exceptions"] \
        == set(), "unexpected: uncovered atoms (the coverage test above should have failed)"
    # The register carries an entry for an atom that is NOT in the owed population
    # (a W-lane exception). If the population were being read from the register,
    # that entry would appear in `owed`.
    assert record["exceptions"] - record["owed"], (
        "the register's exceptions are all inside the owed population, so this "
        "independence check cannot distinguish 'derived from the map' from 'derived "
        "from the register' — seed the register with an out-of-population entry"
    )
