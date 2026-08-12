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
    # 2026-08-10 reviewed (worker tick, backlog-triage Group A: "verify the atom exists; mint if
    # not"). Both classified on their merits, not to clear the gate.
    # AO12 is a MEASUREMENT atom: it runs a bounded 10k-customer probe against a prediction
    # register and reports where the first seam tears. It explicitly forbids itself any fix,
    # substrate adoption or schema work, so it moves no money and touches no revenue flow -- what
    # it produces is knowledge about whether the current shape scales, which is the same
    # close_to_learn class as its 111 H_harness siblings.
    "AO12_scale_probe_10k",
    # A9 is a DESIGN-LAW atom: it makes the portability constraint (no counterparty hardcoded
    # across a seam; market-varying quantities reachable as tables) fail when broken, instead of
    # being a review lens someone remembers. It builds no market and sells nothing; it measures
    # whether an architectural claim already made is still true -- close_to_learn, same class as
    # its A-lane governance siblings A1/A2/A6.
    "A9_market_at_the_seams_design_law",
    # 2026-08-10 reviewed (worker tick, ratified mint per DIRECTOR_NOTE_SUSPECT_LIST_REDERIVATION).
    # H42 changes what an ALARM says, not what the company does: the wedge payload's suspect block
    # is re-derived from the gate's actual red instead of a recency ranking that measured 0/8 for
    # five consecutive episodes. No money moves and no revenue flow is touched -- what improves is
    # whether the machine can say why it is stuck, the same close_to_learn class as H30 (sim_runner
    # discarding child stderr) and its other H_harness siblings.
    "H42_wedge_suspect_list_rederived_from_the_red",
    # 2026-08-11 reviewed (worker tick, mint per DIRECTOR_INSTRUCTION_QUERYABLE_PROJECTIONS).
    # G12/G13 make the company's ALREADY-COMMITTED truth queryable -- they derive nothing new, move
    # no money and touch no revenue flow; a projection that changed a figure would be the second
    # source of truth the atom forbids itself. What they produce is the ability to ASK, which is the
    # same close_to_learn class as their G-lane siblings G1/G2/G3 (score, ledger, inspection chain).
    # Classified on that merit: the alternative streams were each considered and each fails --
    # meter_to_cash/price_to_bill/wholesale_to_price all name a flow these atoms deliberately do not
    # touch. Not placed here to clear the gate; if v1 ever WRITES a figure, this entry is wrong.
    "G12_queryable_projections", "G13_projection_consumers",
    "G1_fidelity_grid_scorer", "G2_fidelity_evidence_ledger", "G3_fidelity_inspection_chain",
    # 2026-07-19 reviewed: Epoch-2 campaign fidelity/measurement atoms authored from their DISCOVER
    # docs (A scoring frame, D cascade estimation) per DIRECTOR_DIRECTIVE_SEAT_WORK_AND_CONTINUITY_PROOF
    # -- same close_to_learn class as their G-fidelity siblings (measure belief-vs-truth, not revenue).
    "A_scope_of_need_scoring_frame", "D_cascade_correlation_estimation",
    "H_forward_discovery_draw",  # 2026-07-19 forward-discovery mechanism atom (harness/close_to_learn)
    # 2026-07-29 reviewed (worker tick, H29 DISCOVER+FRAME): registered in 90cd95039 with
    # value_stream='harness_integrity', a stream that has never been in VALID_STREAMS -- so that
    # commit left this test RED at HEAD and blocked every subsequent commit until now. Classified
    # here on its merits, not to clear the gate: H29 is a test-isolation/harness-integrity atom
    # (a stale module-level secret capture that makes the suite lie about wake-signing), which
    # measures whether the harness can be TRUSTED -- no revenue movement -- putting it in exactly
    # the same close_to_learn class as all 52 of its H_harness siblings.
    "H29_import_time_env_capture_test_isolation",
    # 2026-08-08 reviewed (worker tick, registered from the WORKER_FINDING that diagnosed the sim
    # red loop). Classified on its merits, not to clear the gate: H30 is a DIAGNOSABILITY atom --
    # sim_runner discards its child's stderr, so a failing run's only artefact is an exit code. It
    # moves no money and touches no revenue flow; what it measures is whether the machine can say
    # WHY it failed, which is the same close_to_learn class as its H_harness siblings. The cost is
    # already on the record: eight failures over ~60 minutes produced no diagnosable evidence and
    # the root cause (a one-line NameError) needed a manual re-run to see.
    "H30_sim_runner_discards_child_stderr",
    # 2026-08-08 reviewed (worker tick, found while running tests/background/ + tests/tools/
    # together for H30). Classified on its merits, not to clear the gate: H31 is a TEST-ISOLATION
    # atom -- one test leaves WAKE_HMAC_KEY unset process-wide, so four signing tests pass or fail
    # on collection order alone. It moves no money; what it measures is whether the suite's verdict
    # means anything, which is the same close_to_learn class as H29 (its near-identical sibling:
    # both are import-time env capture defeated by reload/teardown ordering).
    "H31_secret_scrub_test_leaks_wake_key",
    # 2026-08-09 reviewed (worker tick, D16 build, which tripped the ratchet and queued it rather
    # than trimming its own record to satisfy it). Classified on its merits, not to clear the gate:
    # H32 is a HARNESS-INTEGRITY atom -- the map's own size ratchet is red on committed HEAD
    # (464110 bytes vs a 409600 ceiling, measured before this tick's 8865), so a control currently
    # penalises the one behaviour the map exists for, recording work honestly. It moves no money
    # and touches no revenue flow; what it measures is whether the machine's own record can be
    # kept without a control fighting it -- the same close_to_learn class as H29/H30/H31.
    "H32_map_size_ratchet_red_on_head",
    # 2026-08-09 reviewed (worker tick, minting from DIRECTOR_RULING_PUBLISH_GATE_SUBJECT and
    # closing the H_GAP anchor finding). Classified on their merits, not to clear the gate --
    # and this control catching all three at once is it working as designed: the first two were
    # minted earlier the same day by a tick that never ran tests/design/, so they arrived
    # off-grammar AND unreviewed and sat red on HEAD until now (renamed onto the grammar here
    # rather than allowlisted, per the id test's own instruction).
    #   OPS2/OPS3 are PUBLISH-PATH atoms. Under the ruling the gate's subject became a clean
    # checkout of HEAD; what they change is what the machine MEANS by "the code passed" and
    # whether a publish has actually gone out through the new path. Neither moves money nor
    # touches a revenue flow -- what they measure is whether the machine's own verdict can be
    # trusted, the same close_to_learn class as their H_harness siblings.
    #   H33 is an R15 CONTROL-INTEGRITY atom: it asks of every anchored band whether the
    # statistic has a null the threshold is supposed to sit above, after L1.4's band was found
    # sitting UNDER its own null (a day-type-randomised population cleared it with 1.4x margin).
    # It moves no money; what it measures is whether this repo's bands can fail at all.
    "OPS2_publish_gate_head_worktree",
    "OPS3_first_post_ruling_publish",
    "H33_does_this_statistic_have_a_null",
    # 2026-08-09 reviewed (worker tick, H33's own two hits). Classified on their merits, not to
    # clear the gate: both are R15 CONTROL-INTEGRITY atoms of exactly H33's class, minted from
    # its measured output rather than authored.
    #   H34 repairs the one band the sweep found sitting on its own null (L2.3 timing diversity
    # is INSIDE its null at 40/60/90 days and clears it at 120 by 3.8% of the null's own spread),
    # by scoring against the permutation null instead of a constant floor.
    #   H35 closes the other hit: two regime-conditioned texture bands that judge zero and one
    # home at the applied window, so their nulls cannot be measured on the load set they govern.
    # Neither moves money; what both measure is whether this repo's bands can fail at all.
    "H34_score_timing_diversity_against_its_own_null",
    "H35_the_panel_never_exercises_two_of_its_own_bands",
    # 2026-08-09 reviewed (worker tick, H35's own build). H35 widened the coupling panel so
    # the two unexercised bands could be measured; both came back hits, and a third band that
    # had read clean for as long as the panel was all-gas came back INSIDE its own null. H36
    # and H37 are those dispositions, and they are close_to_learn on the same grounds as their
    # parents rather than by default: neither moves money, neither touches a revenue flow, and
    # what each measures is whether a band this repo already ships can fail at all —
    #   H36: both electric texture floors are derived at ONE published typical home and applied
    # at every home size, so a home with twice the assumed heat share is judged by a floor that
    # was never about it (every panel home clears the floor its OWN behavioural share implies).
    #   H37: the away-day signature reads a heat pump as an empty house — an occupied home
    # flagged away on 104 of 120 real days — so L1.3 cannot fail on absence of the structure it
    # certifies once any home's heat lands on the judged meter.
    "H36_the_texture_floor_is_one_number_for_every_home_size",
    "H37_the_away_signature_reads_a_heat_pump_as_an_empty_house",
    # 2026-08-10 reviewed (worker tick, H36's own build). H36 replaced the per-regime texture
    # floors with ONE floor read on the meter net of space heat, which measured the old reading
    # passing five of six electrically heated homes with every appliance event removed from
    # them. Both dispositions below are close_to_learn on the same grounds as their parent —
    # neither moves money, neither touches a revenue flow, and each is about whether a band this
    # repo already ships can fail at all —
    #   H38: taking the space heater out leaves the WATER heater, 36-40% of what L1.1 now calls
    # behaviour, and it fails one drawn home in sixty for owning a second machine.
    #   H39: the surviving floor clears its own null by less than the null's own spread, because
    # the flat-day null preserves each home's mean diurnal profile and the statistic then reads
    # that profile's roughness.
    "H38_the_behavioural_stream_still_carries_the_water_heater",
    "H39_the_texture_floor_sits_inside_the_spread_of_its_own_null",
    # 2026-08-09 reviewed (worker tick, minting the WORK THIS CREATES block of
    # DIRECTOR_RULING_HOOK_BYPASS_AND_SURGICAL_LANDING). Both are harness-integrity work and
    # neither touches a revenue flow: OPS5 executes the expiry the ruling put on the one
    # sanctioned interim bypass shape (an un-executed expiry turns a retro-sanction into the
    # rule), and H38 is the granted full-suite pollution bisect — naming the module that makes
    # tests pass alone and fail together, so the class stops being instance-fixed on a moving
    # target. What each measures is whether this repo's own gate can be trusted to run.
    "OPS5_retire_the_interim_bypass_shape",
    "H40_full_suite_pollution_bisect",
    # 2026-08-10 reviewed (worker tick, PW3 build). H41 is harness-integrity work and touches no
    # revenue flow: the map's own spine ratchet went red again 24h after H32 drained it, and the
    # publish gate -- unlike the pre-commit gate -- runs tests/design/, so the same red is now a
    # wedge. What it measures is whether this repo's record-keeping control can survive the repo
    # keeping its record.
    "H41_the_map_ratchet_has_no_ongoing_drain",
    # 2026-08-08 reviewed (worker tick, D6 CLASS closure). Classified on its merits, not to
    # clear the gate: D9 is a MEASUREMENT-REPORTING atom -- the Proof panel prints the red
    # verdict "worse than blind" from the number alone, a reading D6 refuted for
    # misapplication_gap (there >1 means the minority class is small, not that the company is
    # worse than blind). It moves no money and touches no revenue flow; what it measures is
    # whether a published fidelity figure means what the surface says it means -- the same
    # close_to_learn class as its G-fidelity and H-harness siblings.
    "D9_worse_than_blind_chip_is_metric_blind",
    # 2026-08-08 reviewed (worker tick, absorbing DIRECTOR_PROGRAMME_ARCHITECTED_OUT_2026-08-05
    # into the map). Classified on their merits, not to clear the gate -- and the gate firing on
    # all nine at once is this control working exactly as designed: a programme absorbed in one
    # go is precisely when the dumping-ground default would slip in unnoticed.
    # The programme is "organic in, architected out" -- MAP (capability index + write-time reuse
    # gate) -> NET (join-test tier + executable scale constraints) -> KNIFE (hotspot
    # consolidation) -> RHYTHM (consolidation as a standing epoch duty), plus the target-design
    # document and the two board-scaling atoms. Every one of them acts on HOW THE MACHINE BUILDS
    # ITSELF -- reuse surfaces, test tiers, refactor sequencing, review construction. Not one
    # moves a revenue flow, prices anything, bills anything or settles anything; none could be
    # honestly filed under meter_to_cash, price_to_bill or wholesale_to_price without inventing a
    # customer it does not touch. What they measure is whether the codebase can be described,
    # demonstrated and trusted -- the same close_to_learn class as all 52 of their H_harness
    # siblings and as G's fidelity-method atoms.
    "AO1_capability_index",
    "AO2_write_time_reuse_gate",
    "AO3_join_test_tier",
    "AO4_scale_constraints_executable",
    "AO5_hotspot_consolidation",
    "AO6_consolidation_rhythm",
    "AO7_target_design_doc",
    "AO8_board_batteries_executable",
    "AO9_blind_review_by_restricted_context",
    # 2026-08-08 reviewed (worker tick, minted at AO1 close from the two ruled items that had no
    # atom). Same class as their AO siblings above and classified on their merits: AO10 moves
    # ~4,300 run markers out of the instruction record so governance is readable -- filing, not a
    # revenue flow; AO11 puts an assertion date and a last-verified date on map cells so a stale
    # level is a query rather than a discovery -- registry integrity, and it touches no customer,
    # price or settlement. Filing either under meter_to_cash or price_to_bill would invent a
    # customer neither goes near.
    "AO10_exhaust_separated_from_record",
    "AO11_map_assertion_provenance",
    # 2026-08-09 reviewed (worker tick, minted at AO5 close: the four KNIFE passes the plan in
    # docs/design/KNIFE_HOTSPOT_PASSES.md sequences). Classified on their merits and inheriting
    # nothing from AO5 by default -- the gate refusing all four at once caught exactly that
    # inheritance, which is the defect it exists for. Each moves code structure and no money:
    # KNIFE1 breaks an import cycle between the reporting package and the run that imports it
    # back; KNIFE2 routes 16 SIM reads of the customer module through the existing seam; KNIFE3
    # pays down what remains of the 107 wall crossings; KNIFE4 gives 258 unreferenced company
    # modules a wired/archived/explained verdict. All four are behaviour-preserving by their own
    # exit tests -- a KNIFE pass that changed a bill would have failed its own byte-identical
    # check -- so filing any of them under meter_to_cash or price_to_bill would claim a revenue
    # movement their acceptance criteria explicitly forbid.
    "KNIFE1_reporting_cycle",
    "KNIFE2_customer_straddle",
    "KNIFE3_wall_crossing_paydown",
    "KNIFE4_orphan_disposition",
    # 2026-08-09 reviewed (worker tick, minted from DIRECTOR_STEER_SECOND_PUBLISH_WEDGE_2026-08-09's
    # WORK-THIS-CREATES block). Classified on their merits: all three act on whether the machine can
    # TELL that something is wrong with itself. PW1 redefines a daemon-staleness signal so it can be
    # green and its red means something; PW2 censuses the class where a check's failure overwrites
    # the state its own alarm reads; PW3 watches suite duration against its ceiling. None prices,
    # bills, meters or settles anything -- the only "customer" any of them has is the machine's own
    # operator, so filing them under meter_to_cash or price_to_bill would invent a revenue flow.
    # Same close_to_learn class as the AO and H_harness siblings above.
    "PW1_staleness_is_code_actually_loaded",
    "PW2_failure_clears_its_own_alarm",
    "PW3_suite_duration_watch",
    # 2026-08-09 reviewed (worker tick, at PW2's close). PW4 is the residue of PW2's own census:
    # four state files the derivation judged `real` and PW2 deliberately did NOT guard, because
    # each needs its own answer to "what evidences an episode close". Classified on its merits and
    # not inherited from its parent: it is the same question PW2 asked -- can the machine still
    # tell how long it has been broken -- applied to four more of its own alarms. It moves no
    # money, meters nothing, and bills nobody; the only consumer is the operator reading a page.
    "PW4_guard_remaining_episode_states",
    # 2026-08-08 reviewed (worker tick, minting the EP1-EP20 commitment sets (epochs 2-5) from
    # DIRECTOR_RULING_FUTURE_COMMITMENT_SETS_2026-08-08). Classified on their merits, not to clear
    # the gate -- and as with the AO batch, the gate firing on eleven at once is this control doing
    # exactly its job: a commitment set minted in one go is precisely when the dumping-ground default
    # would slip in unnoticed. The other twelve atoms of that mint are NOT here, because they carry
    # honest revenue-flow streams (collections and the metering/payments/switching adapters are
    # meter_to_cash; pricing, settlement true-ups, the cost-stack and forecast feeds and Elexon are
    # wholesale_to_price) -- which is the check that this list is a classification and not a bucket.
    #
    # EP1_clv_three_horizon: a VALUATION the company forms about a customer. It bills nothing, prices
    # nothing and settles nothing; filing it under price_to_bill would invent a bill it never issues.
    # What it measures is whether the company's belief about customer value survives contact with
    # realised value -- close_to_learn by definition.
    # EP2_variance_learning_loop: literally the "learn" half of the stream's name -- expected-minus-
    # realised decomposed per cohort and fed back into belief. No candidate alternative exists.
    "EP1_clv_three_horizon",
    "EP2_variance_learning_loop",
    # EP6_wall_protocol_typing: the-wall architecture, the same class as W4_1_typed_adapters (already
    # close_to_learn above). It moves no money; it decides the message shapes money later moves in.
    # EP13_adapter_carbon_intensity: an emissions-intensity feed. Carbon is measured and reported here,
    # never charged -- CARBON_NOT_A_TARGET_CONSTRAINT governs the lane -- so there is no revenue flow
    # to file it under, and its sibling E5_carbon_three_ledger sits in the same class.
    "EP6_wall_protocol_typing",
    "EP13_adapter_carbon_intensity",
    # EP16_anchored_generators: world-generation METHOD with its calibration discipline (R13 baseline).
    # It builds the worlds the company is measured in; it is on the far side of the wall from every
    # revenue flow, and the same class as its G-fidelity siblings.
    # EP18_enterprise_value_fitness: the tournament's selection criterion -- the same close_to_learn
    # class as A5_tournament_fitness_mortality and B11_evolutionary_tournament_harness above, and for
    # the same reason: it scores companies, it does not bill customers.
    "EP16_anchored_generators",
    "EP18_enterprise_value_fitness",
    # EP19_counterparty_qualification_paths / EP20_go_live_cutover_analysis: go-live readiness, the same
    # class as H4_go_live_nfr_register above. Both are registers and analyses about whether the
    # machine can be trusted to run for real; neither touches a customer, a price or a settlement.
    "EP19_counterparty_qualification_paths",
    "EP20_go_live_cutover_analysis",
    # FUT1/FUT2/FUT3: the ruling's own machinery -- an attach-hook so findings can name the future
    # they advance, a proposal path for pull-forward, and a visibility check that blocked atoms stay
    # legible to the clocks. All three act on HOW THE MACHINE PLANS ITSELF, the same class as their
    # AO and H_harness siblings. None could be filed under a revenue stream without inventing a
    # customer it does not go near.
    "FUT1_attach_forward_hook",
    "FUT2_pull_forward_proposal",
    "FUT3_blocked_atom_visibility",
    # 2026-07-29 reviewed (worker tick, minted from DIRECTOR_RULING_FIX_DOUBLE_MESSAGING): the
    # residual half-done tmux->systemd cutover on seven daemons. Classified on its merits, not to
    # clear the gate -- it moves no money and touches no revenue flow; it is process-lifecycle
    # integrity, i.e. whether the machine that runs the company can be trusted to run each daemon
    # exactly once. Same close_to_learn class as its OPS1/H_harness siblings.
    "OPS1_launcher_cutover_completion",
    # 2026-07-29 reviewed (worker tick, DIRECTOR_RULING_RIP_OUT_PERMISSION_MACHINERY item 6).
    # Classified on its merits, not to clear the gate: GAP1 is a DRAW-COMPLETENESS / work-accounting
    # atom -- an independent reader that makes the machine's own published gap registers drawable, so
    # a saturation claim is impossible while any register holds an open item. It moves no money and
    # touches no revenue flow; what it measures is whether the machine's account of its own remaining
    # work can be TRUSTED. That is the same close_to_learn class as H_forward_discovery_draw (the
    # sibling drawability-mechanism atom) and all 52 H_harness siblings, and it is GAP1's TRUE stream,
    # not a dumping-ground default.
    "GAP1_gap_registers_as_mint_sources",
    # 2026-08-03 reviewed (worker tick, diagnosed from docs/observability/background-worker-log.md).
    # Classified on its merits, not to clear the gate: the leftover run_complete sweep can never
    # acquire the run lock the producer holds, so it has logged "will retry next cycle" for 404
    # markers, every cycle, without ever succeeding -- a livelock reporting a permanent total
    # failure in the vocabulary of a transient retry. It moves no money and touches no revenue
    # flow; what it measures is whether the machine's own account of its publish queue can be
    # TRUSTED, which is the identical class to OPS1_launcher_cutover_completion (process-lifecycle
    # integrity) and H_forward_discovery_draw. close_to_learn is its TRUE stream, not a default.
    "OPS_run_marker_sweep_livelock",
    # 2026-07-29 reviewed (worker tick): the three atoms minted from SITE1_expert_doors' cold-eyes
    # Expert Hour (BLOCKER-1, MAJOR-3, MAJOR-4/5/6). They were minted with value_stream=
    # 'evidence_surfaces', a stream that has never been in VALID_STREAMS -- so the mint left this
    # test RED on the working tree. Classified on their merits, not to clear the gate: each one is
    # about whether a PUBLISHED figure or claim can be trusted (a segment-mix disclosure behind a
    # headline per-customer margin; a predictions ledger that must be able to record a MISS; one
    # bad-debt series, a margin plausibility band, and part-periods labelled as such). None moves
    # money or touches a revenue flow -- they measure belief-vs-truth on the evidence surfaces of
    # the close, which is the same close_to_learn class as their own parent SITE1_expert_doors and
    # as the G-fidelity/H_harness siblings.
    "SITE_EH1_segment_disclosure",
    "SITE_EH2_predictions_ledger_can_fail",
    "SITE_EH3_figure_reconciliation_and_periods",
    # 2026-08-03 reviewed (worker tick, the R17 consumed-not-absorbed mint of 11 BUILD halves that
    # had been sitting in docs/staging/in_progress/ as "staging noise" while being real designed
    # work). Classified on their merits, one at a time, NOT as a batch to clear this gate -- the
    # other five atoms from the same mint were classified into meter_to_cash / price_to_bill /
    # close_to_learn separately, precisely because "everything I just added is close_to_learn" is
    # the unreviewed default this list exists to catch.
    #  * SP2_2_rng_substream_primitive -- unifies 16 independent substream derivations (5 distinct
    #    formulas, one with a concrete namespace-collision risk) into one canonical primitive. What
    #    it protects is DETERMINISTIC REPLAY (C-S2): whether the machine's own account of its
    #    stochastic world can be trusted when a new draw is added. No revenue flow.
    #  * SP3_size_and_clone_ratchet, SP4_owned_quantity_registry_gate,
    #    SP5_shared_primitive_ensuring_activity -- build-discipline gates. SP4 in particular is a
    #    trust-the-published-number atom of exactly the SITE_EH1 class (it exists because net margin
    #    currently has 4 second-sources including a live ~4.2x dashboard divergence, and carbon has 5
    #    disagreeing emission-factor tables). They cap duplicated CODE and duplicated AUTHORITY over a
    #    figure; neither is a revenue movement.
    #  * H_stop_control_gap_characterisation -- operational safety legibility: what can actually be
    #    stopped, by whom, how fast, and what a stop does NOT stop. Same process-lifecycle-integrity
    #    class as OPS1_launcher_cutover_completion and OPS_run_marker_sweep_livelock.
    #  * SITE_director_window_delta_view -- an evidence-surface/operator-legibility door, same class
    #    as its parent SITE1_expert_doors and the three SITE_EH atoms directly above.
    # 2026-08-03 reviewed (worker tick, dead-fork rescue audit). Classified on its merits: a register
    # OF STALL CLASSES is a self-audit instrument -- it measures whether the machine's own account of
    # when it stopped working can be TRUSTED. It moves no money and touches no revenue flow, which is
    # the identical class to OPS_run_marker_sweep_livelock and OPS1_launcher_cutover_completion.
    "OPS_stall_class_register_adoption",
    "SP2_2_rng_substream_primitive",
    "SP3_size_and_clone_ratchet",
    "SP4_owned_quantity_registry_gate",
    "SP5_shared_primitive_ensuring_activity",
    "H_stop_control_gap_characterisation",
    "SITE_director_window_delta_view",
    "A1_learn_loop_chair", "A2_decision_rights_register", "A3_approval_interface",
    "A4_sim_approver", "A5_tournament_fitness_mortality", "A6_coupled_triad_gap_metric",
    "A7_harm_cost_weights_decision", "A8_experiment_loop_speed",
    # 2026-07-23 reviewed (publish-gate unwedge, DIRECTOR_RULING_UNWEDGE_AND_AXIS3): the harness/
    # gap-measurement leg of the F1 conversations coupled triad -- measures the belief-vs-truth GAP
    # between the SIM customer response (F1a) and the COMPANY's estimated susceptibility (F1b), NOT
    # revenue. Same close_to_learn class as its siblings A6_coupled_triad_gap_metric and
    # F1_epistemic_verifier; close_to_learn is its TRUE stream, not a dumping-ground default.
    "F1c_harness_conversation_gap",
    "ARCH1_internal_seams", "BRAND1_identity_system",
    "E1_ledger_double_entry", "E2_revenue_reconciliation", "E3_accrual_restatement",
    "E4_supplier_reporting_standard",
    "E5_carbon_three_ledger",  # 2026-07-20 v4 mission carbon-ledger candidate (diagnostic, CARBON_NOT_A_TARGET)
    # 2026-07-29 reviewed (BACKLOG Wave-B wiring): the treasury/liquidity leg of the Wave-B coupled pair --
    # a hedge book posting variation margin whose crisis mortality is measured as the accounting-P&L-looks-fine
    # vs cash-is-dying GAP (belief-vs-truth survival learning), NOT a revenue-flow movement. Same close_to_learn
    # class as its E-lane siblings E1-E5; close_to_learn is its TRUE stream, not a dumping-ground default.
    "B6_collateral_cash_death_loop",
    # 2026-07-29 reviewed (BACKLOG->map wiring, director from_rich_20260729_173731 "put all eleven
    # backlog items into the map as real unfinished work items"): the tournament HARNESS -- it reruns a
    # company configuration across the scenario set, scores, ranks and removes, i.e. it MEASURES which
    # configuration survives (belief-vs-truth about the company itself). No revenue-flow movement, so
    # close_to_learn is its TRUE stream, the same class as its A5/A8/H-harness siblings. The fitness
    # function and mortality rules it reads are A5's and stay director-reserved values (category 6).
    "B11_evolutionary_tournament_harness",
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
    "H28_precommit_gate_ambient_cwd_git_discovery",  # 2026-07-28 reviewed: scoped defense-in-depth residual of H24 (gate-run tests discover the real .git by upward-walk from cwd=ROOT) -- same commit/publish-chain-integrity close_to_learn class as H24/H26
    "H25_self_gov_detection_hardening", "H26_core_bare_corruption_guard",
    "H27_phone_act_channel",  # 2026-07-18 reviewed: governance/authority infra (director phone-[ACT] channel) -- shortens the director-decision feedback loop, the same close_to_learn class as its siblings H25/H26/G10/A3
    "H_draw_excludes_external_blocked_atoms",
    "OPS1_operational_layer_rebuild", "OPS1_session_watchdog_collapse",
    "OPS1_tmux_target_qualification", "OPS1_governance_refusal_mutation_test",
    "OPS1_transport_failure_must_be_loud",
    "SITE1_expert_doors",
    # 2026-07-27 minted from DIRECTOR_RULING_HARNESS_INVESTMENT_AND_ITS_EVIDENCE (Problem One):
    # the site evidence pages behind the model-on-a-page nodes -- a method/site atom that makes the
    # harness's own evidence inspectable (belief-vs-truth / does-the-claim-hold), same close_to_learn
    # class as SITE1_expert_doors and the G-fidelity atoms, not a revenue-flow movement.
    "SITE_evidence_pages_behind_nodes",
    # 2026-07-27 minted from DIRECTOR_RULING_HARNESS_EXIT_CRITERION_RATIFIED: the harness
    # exit-criterion counter / stall-set coverage / counter-published atoms -- they MEASURE the
    # harness's own stall behaviour (belief-vs-truth about whether the machine actually stalled),
    # the same close_to_learn class as the H1..H27 harness siblings, not a revenue-flow movement.
    "HX1_exit_criterion_counter_mechanise", "HX2_stall_set_coverage_verdict",
    "HX3_counter_published_and_derivable",
    # 2026-07-27 minted from DIRECTOR_RULING_COHORT_ASSIGNMENT_ACTIVATED (WORK THIS CREATES item 3):
    # marks volume-dependent segmentation capabilities untestable-at-current-book in the FIDELITY
    # ledger -- a belief-vs-truth / claim-status honesty atom, sibling to G2_fidelity_evidence_ledger,
    # close_to_learn is its TRUE stream (it measures what can and cannot yet be validated, not revenue).
    "CA3_segmentation_untestable_ledger_marking",
    "W4_1_typed_adapters", "W4_2_verifier_timing_extension", "W4_3_external_truth_wall",
    # 2026-08-03 reviewed (worker tick, minted from ADVISOR_DISCOVERY_PREMISE_FABRIC_PHYSICS).
    # Classified on its merits, not to clear the gate: this is the HARNESS leg of the fabric
    # coupled triad -- the two-level test (spiky homes, smooth crowds) as a standing failable
    # control, plus the EPC-vs-actual and inferred-vs-actual fabric gap metrics. It measures
    # whether the premise generator's traces can be BELIEVED and how wrong the company's fabric
    # beliefs are; it moves no money and touches no revenue flow. That is the identical class to
    # its sibling harness-gap atoms F1c_harness_conversation_gap and A6_coupled_triad_gap_metric,
    # and close_to_learn is its TRUE stream, not a dumping-ground default.
    "H_GAP_fabric_belief_truth_gap",
    # 2026-08-09 reviewed (worker seat, minted from DIRECTOR_RULING_HOOK_BYPASS_IS_A_WALL).
    # Classified on its merits, not to clear the gate: this is a HARNESS-INTEGRITY atom in the
    # same class as H29/H30/H31 above. It builds the tool that runs the gate against the tree a
    # commit WOULD create, so landing work on a shared dirty index never requires routing around
    # the check. What it measures is whether the machine's own verification can be TRUSTED to
    # have run -- it moves no money and touches no revenue flow, price, meter or bill. The cost
    # is already on the record: on 2026-08-09 the absence of this tool left the operator with
    # only two moves, sweep four other lanes' staged work into a commit or bypass the hook, and
    # the bypass is what happened. close_to_learn is its TRUE stream, not a dumping-ground default.
    "OPS4_surgical_landing_tool",
    # 2026-08-10 reviewed: the three deliverables minted from DIRECTOR_RULING_PUBLISH_DECOUPLING
    # ("THE SITE BREATHES"). All three act on the PUBLISH/EVIDENCE SURFACE -- what the site says
    # about its own freshness and verification -- exactly the class SITE_EH1_segment_disclosure
    # was reclassified into on 2026-07-29 for the same reason. None of them moves money, sets a
    # price, or touches a meter or a bill: OPS6 narrows which reds may block a publish, OPS7
    # stamps provenance on the rendered page, OPS8 keeps last-known-good served under a dated
    # banner. close_to_learn is their TRUE stream, not a dumping-ground default (C3).
    "OPS6_scoped_publish_path_suite",
    "OPS7_provenance_stamps_on_live_pages",
    "OPS8_last_known_good_staleness_banner",
    # 2026-08-12 reviewed (worker tick, minting the WORK THIS CREATES block plus clause 5 of
    # DIRECTOR_RULING_FINDING_SEVERITY_AND_INTERLEAVE). Classified on their merits, not to clear
    # the gate -- and the gate refusing all six at once is it working as designed, since a ruling
    # absorbed in one pass is precisely when the dumping-ground default slips in. Every one acts
    # on HOW THE MACHINE READS ITS OWN FINDINGS and what it may build on top of them: OPS9 gives
    # a finding a machine-readable severity; OPS10 collapses five families of siblings into class
    # documents with instance lists; OPS11 refuses a level-raise in a lane whose instrument is
    # known untrustworthy; OPS12 orders blockers ahead of housekeeping in the draw; OPS13 arms the
    # product interleave and makes its draws visible; OPS14 names staging documents that have aged
    # 72h unopened. Not one prices, bills, meters or settles anything -- OPS13 SCHEDULES product
    # work but builds none of it, so filing it under meter_to_cash or price_to_bill would claim a
    # revenue flow the atom itself does not touch. What all six measure is whether this repo's own
    # verdicts can be trusted and acted on in the right order, the same close_to_learn class as
    # their OPS/H_harness siblings above.
    "OPS9_finding_severity_field",
    "OPS10_finding_class_consolidation",
    "OPS11_blocking_lane_refusal",
    "OPS12_blockers_ahead_of_disposition",
    "OPS13_product_interleave_armed",
    "OPS14_aged_staging_named_daily",
}

# The coupled topology landed in the yaml (C5). Each pair is world<->company as
# the atoms themselves declare (real_world_twin "world twin of"/"company twin
# of", or a "COUPLED" name). Both members must carry couples_with naming the
# other. Kept here as the authority the symmetry check validates against.
EXPECTED_PAIRS = {
    frozenset(("W1_5_premise_demand_shape", "C13_weather_normalisation")),
    frozenset(("W1_6_physics_price_signal", "C13_weather_normalisation")),
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


# Canonical release-condition tokens a `blocked_on` may resolve to
# (unstated_reason_block_impossible DISCOVER §3). A blocked_on RESOLVES iff it
# names one of these (as a substring, so a long-form prose blocked_on that
# carries its releaser still resolves) OR equals an existing atom id; anything
# else is an UNRESOLVABLE release condition -> the block is invalid
# (feedback_nonempty_config_referent_existence: a release condition that
# resolves to nothing is a fail-open we must reject, not wave).
#
# "director_level_up" / "director_build_open" / "build_open" / "front_open" REMOVED 2026-07-29
# (DIRECTOR_RULING_RIP_OUT_PERMISSION_MACHINERY items 1-3): these named the exact permission-gate
# convention the ruling abolishes -- "there is no such thing as needing a build opened", and levels
# are recorded (self-certification suffices, R16), never gated. No atom should be able to declare a
# `blocked_on` that resolves via one of these tokens any more; removing them from the KNOWN vocabulary
# makes check_block_hygiene FLAG (not silently wave) any future attempt to re-introduce this exact
# gate shape -- mechanism, not prose (MAKE_IT_STICK). An atom with real BUILD/level work remaining
# now carries no `blocked_on` at all (drawable) rather than parking on one of these tokens.
KNOWN_RELEASER_TOKENS = (
    "director_live_run",        # released by the director-watched live run
    "director_systemd_deploy",  # released by the director-triggered systemd deploy
    "coupled_triad_measured",   # released when the named coupled-triad gap is measured
    "watching_brief",           # a director-rejected item parked in the forward-discovery register
    "forward_register",         # ditto -- released when the director re-opens it from the register
)
# NOT ADDED 2026-08-08, and the reason is worth keeping: minting the EP2-EP5 commitment sets
# (DIRECTOR_RULING_FUTURE_COMMITMENT_SETS_2026-08-08) looked like it needed an `epoch_unblock`
# releaser, and one was drafted here. It was removed on finding that a releaser-token block is
# unexpressible: test_maturity_map_contract.py::check_edges requires `blocked_on` to be a LIST OF
# EXISTING ATOM IDS, so the only block this map can represent is a dependency on another atom. The
# commitment sets are parked `loop_stage: idle` instead -- the way all 9 pre-existing epoch-4/5
# atoms are parked, and the way CLAUDE.md's epoch-gating rule describes ("parked for BUILD only").
# A token added here with no atom resolving through it would have been an orphan constant that
# nothing compares -- a control that cannot fail.


def _is_blocked(blocked_on) -> bool:
    """A blocked_on is a real block unless it is null/None/empty/whitespace."""
    if blocked_on is None:
        return False
    s = str(blocked_on).strip()
    return bool(s) and s.lower() != "null"


def _block_reason_missing(atom: dict) -> bool:
    r = atom.get("block_reason")
    return not (isinstance(r, str) and r.strip())


def _blocked_on_resolves(blocked_on, known_ids: set) -> bool:
    """RESOLVES iff blocked_on names a canonical releaser token (substring) or an existing atom id."""
    s = str(blocked_on).strip()
    low = s.lower()
    if any(tok in low for tok in KNOWN_RELEASER_TOKENS):
        return True
    return s in known_ids


def check_block_hygiene(atoms: list) -> list:
    """Return violation strings (empty == pass): every atom carrying a `blocked_on` MUST also carry a
    non-empty `block_reason` AND a `blocked_on` that resolves to a known releaser or an existing atom
    id (unstated_reason_block_impossible §3 -- 'every block carries its reason and its release
    condition, or it is not a valid block. ... A block without a recorded reason cannot be escalated,
    unblocked or judged -- it is invisible work wearing a status'). This governs block HYGIENE only,
    never block COUNT (R12: the number of blocked atoms is a diagnostic, never a target).

    R15 posture: FAIL-CLOSED -- a missing/empty/whitespace `block_reason` is treated as NO reason
    (rejected), never as satisfied (the classic fail-open); an unresolvable release condition is
    rejected, not waved. FAIL-SILENT -- a non-dict/unparseable atom entry is itself a violation (an
    unparseable map is a FAILED check, never a pass)."""
    violations = []
    known_ids = {a.get("id") for a in atoms if isinstance(a, dict) and a.get("id")}
    for a in atoms:
        if not isinstance(a, dict):
            violations.append(
                f"non-dict atom entry {a!r} -- map cannot be parsed for block hygiene (FAILED check)"
            )
            continue
        bo = a.get("blocked_on")
        if not _is_blocked(bo):
            continue  # unblocked atom -> block hygiene does not apply
        aid = a.get("id", "<no-id>")
        if _block_reason_missing(a):
            violations.append(
                f"{aid}: blocked_on={str(bo)[:40]!r} but block_reason is missing/empty -- an "
                "unstated-reason block is invisible work wearing a status (§3); state the reason."
            )
        if not _blocked_on_resolves(bo, known_ids):
            violations.append(
                f"{aid}: blocked_on={str(bo)[:60]!r} resolves to no known releaser "
                f"{KNOWN_RELEASER_TOKENS} and no existing atom id -- an unresolvable release "
                "condition cannot be unblocked or judged (§3)."
            )
    return violations


def _load_live_atoms() -> list:
    return yaml.safe_load(MAP_PATH.read_text())


# ── tests over the LIVE map (the phase-close gate itself) ────────────────────

def test_live_map_value_stream_hygiene():
    violations = check_value_stream_hygiene(_load_live_atoms())
    assert not violations, "value_stream hygiene:\n  " + "\n  ".join(violations)


def test_live_map_coupling_topology():
    violations = check_coupling_topology(_load_live_atoms())
    assert not violations, "coupling topology:\n  " + "\n  ".join(violations)


def test_live_map_block_hygiene():
    violations = check_block_hygiene(_load_live_atoms())
    assert not violations, "block hygiene:\n  " + "\n  ".join(violations)


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


# ── R15 mutation tests: check_block_hygiene must FIRE on its named defects ────

def test_block_hygiene_fires_on_reason_less_block():
    # MUTATION: a blocked atom with NO block_reason -> must fire (reverting the check greens this)
    bad = [{"id": "Z1_no_reason", "blocked_on": "coupled_triad_measured"}]
    assert check_block_hygiene(bad), "must fire on a blocked atom with no block_reason"


def test_block_hygiene_fires_on_unresolvable_release_condition():
    # MUTATION: a blocked_on that resolves to no releaser and no atom id -> must fire
    bad = [{"id": "Z2_unresolvable", "blocked_on": "someday_maybe", "block_reason": "we will see"}]
    assert check_block_hygiene(bad), "must fire on an unresolvable release condition"


def test_block_hygiene_fires_on_empty_reason_fail_closed():
    # FAIL-CLOSED: missing / empty / whitespace-only reason is NO reason, never satisfied
    for r in (None, "", "   "):
        bad = [{"id": "Z3_empty", "blocked_on": "coupled_triad_measured", "block_reason": r}]
        assert check_block_hygiene(bad), f"empty/whitespace reason {r!r} must be rejected (fail-closed)"


def test_block_hygiene_fires_on_non_dict_atom_fail_silent():
    # FAIL-SILENT: an unparseable atom entry is a FAILED check, never a silent pass
    assert check_block_hygiene(["not-a-dict"]), "an unparseable atom entry must be a violation"


def test_block_hygiene_passes_a_well_formed_block():
    good = [{"id": "Z4_ok", "blocked_on": "coupled_triad_measured",
             "block_reason": "build complete; the coupled-triad gap is not yet measured against its twin."}]
    assert not check_block_hygiene(good), "a reason + resolvable releaser must pass"


def test_block_hygiene_passes_an_atom_id_release_condition():
    # a blocked_on naming an EXISTING atom id resolves (referent-existence satisfied)
    good = [{"id": "A_waiter", "blocked_on": "B_dependency", "block_reason": "waits on B landing"},
            {"id": "B_dependency"}]
    assert not check_block_hygiene(good), "blocked_on naming an existing atom id must resolve"


def test_block_hygiene_fires_on_atom_id_release_condition_referent_missing():
    # the same, but the named atom does NOT exist -> unresolvable -> must fire
    bad = [{"id": "A_waiter", "blocked_on": "B_ghost", "block_reason": "waits on a ghost"}]
    assert check_block_hygiene(bad), "blocked_on naming a non-existent atom id must fire"


def test_block_hygiene_ignores_unblocked_atoms():
    # governs hygiene, not count: an unblocked atom is never a violation
    assert not check_block_hygiene([{"id": "U", "blocked_on": None},
                                    {"id": "V", "blocked_on": "null"},
                                    {"id": "W", "blocked_on": "  "}])


# ── phase-close CLI entry point ──────────────────────────────────────────────

def _main() -> int:
    atoms = _load_live_atoms()
    violations = (check_value_stream_hygiene(atoms) + check_coupling_topology(atoms)
                  + check_block_hygiene(atoms))
    if violations:
        print("MATURITY-MAP FACET HYGIENE: FAIL")
        for v in violations:
            print("  -", v)
        return 1
    print(f"MATURITY-MAP FACET HYGIENE: PASS ({len(atoms)} atoms)")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
