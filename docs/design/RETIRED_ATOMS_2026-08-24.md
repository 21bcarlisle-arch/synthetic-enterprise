# Nineteen atoms retired, and the closed subgraph they formed

**Date:** 2026-08-24. **Authority:** director console, same morning — *"I'm handing you the
machinery, not asking permission back… If the structure is producing work nobody needs, change
the structure. Delete atoms that shouldn't exist."*
**Undo:** `git revert` of the commit carrying this file. Every row deleted below is recoverable
verbatim from `docs/design/maturity_map.yaml` at its parent commit. No code was deleted with
any of them — a map row is a work item, not an implementation, and everything these atoms had
already shipped is still shipped and still tested.

## The measurement that prompted it

`H_harness` held **135 of the map's 316 atoms** — 43% of the entire work queue was the harness
as its own subject. 91 of those were already at target; the 44 below target were 39% of all
remaining work in the project.

Cross-cut by provenance, 62 of the 135 were `provenance: proposal` — atoms the agent authored
for itself under the standing licence in `EPOCH_GATING_AND_ATOM_AUTHORSHIP.md`. Twenty-three of
those were below target. Their dependency edges were checked before deletion and **not one
non-harness atom depends on, or is blocked on, any of them.** They were a closed subgraph: work
the machine had given itself, whose only consumer was the machine.

## The rule applied, so the next reader can check it rather than trust it

An atom was deleted when **all** of these held:

1. lane `H_harness`;
2. `provenance: proposal` — agent-authored, never a director ruling, steer, programme or mandate,
   and never an advisor artefact;
3. `level_current < level_target` — nothing at target was touched, so no shipped capability is
   demoted or disowned;
4. every path in `file_scope` under `tools/`, `background/`, `tests/`, `.claude/`,
   `docs/design/` or `docs/observability/` — nothing a reader, a customer, a domain expert or
   the simulated world ever sees;
5. no dependent outside the deleted set.

Two atoms met (1)–(3) and were **kept** because they failed (4): `SITE1_expert_doors` and
`D9_worse_than_blind_chip_is_metric_blind` reach surfaces a reader opens. That exception is the
whole point of criterion 4 and is why it is stated as scope rather than as taste.

## Deleted (19)

| atom | stage | level | passes |
|---|---|---|---|
| `A8_experiment_loop_speed` | idle | 2/3 | 7 |
| `B11_evolutionary_tournament_harness` | idle | 0/3 | 2 |
| `H17_autonomous_build_executor` | idle | 0/3 | 2 |
| `H18_harness_self_mutation_audit` | idle | 0/2 | 3 |
| `H20_parallel_maintenance_lane` | idle | 0/3 | 2 |
| `H21_self_contained_escalation` | idle | 0/3 | 2 |
| `H22_scheduled_housekeeping` | idle | 0/3 | 3 |
| `H25_self_gov_detection_hardening` | idle | 1/3 | 6 |
| `H27_phone_act_channel` | idle | 0/3 | 4 |
| `H28_precommit_gate_ambient_cwd_git_discovery` | idle | 0/3 | 2 |
| `H29_import_time_env_capture_test_isolation` | idle | 0/2 | 4 |
| `HX1_exit_criterion_counter_mechanise` | harden | 2/3 | 6 |
| `HX2_stall_set_coverage_verdict` | harden | 2/3 | 7 |
| `HX3_counter_published_and_derivable` | build | 0/3 | 2 |
| `H_forward_discovery_draw` | idle | 1/3 | 9 |
| `OPS1_governance_refusal_mutation_test` | idle | 2/3 | 3 |
| `OPS1_launcher_cutover_completion` | idle | 0/3 | 8 |
| `OPS_stall_class_register_adoption` | harden | 2/3 | 3 |
| `SP4_owned_quantity_registry_gate` | build | 0/3 | 2 |

**`H27_phone_act_channel` deserves its own line.** It is a work item for a *phone act channel* —
a second authority channel for the director. The entire permission apparatus, including every
authority seam, was deleted on 2026-07-29, and `test_the_permission_surface_is_gone` fails if any
of it returns. This atom was the deleted machinery's ghost, sitting in the queue as drawable work
for four passes after the thing it existed to build had been ruled out of existence.

**`H_forward_discovery_draw` is the one to read twice.** Its `expert_hour` field carries a real,
correctly-diagnosed FAIL-OPEN defect in `supervisor.py` — the draw keys on Fn-header *presence*
rather than open/closed *status*, so with all tracks complete (the permanent real state) the
supervisor never rests and re-grants a turn every ~2 minutes. That finding is true and stays true.
Deleting the atom does not delete the defect or the code; it deletes the standing intention to
take a scheduler-internal to level 3. The defect is now a one-line repair on a live module, which
is what it always was, rather than a three-level programme in the queue.

## Retargeted, not deleted (3)

These have a real subject and had simply run out of road at their filed target. Retargeting is
recorded here rather than left to a level ledger entry because *lowering* a target is the move a
reader is most entitled to be suspicious of.

- **`EP6_wall_protocol_typing` 3 → 2.** Fifty-five passes since its level last moved, the single
  largest sink in the project. The atom's own exit-criterion record says two of its seven
  outstanding criteria (Q9, Q15) need an act in a RESERVED class, so level 3 was unreachable in
  this epoch *however much was built* — and holding the target there is precisely what kept
  fifty-five further passes lawful. The five payable criteria remain real work at level 2.
- **`H27_payment_belief_gap` 3 → 2.** Forty-three passes since its move; the remaining move needs
  an instrument this seat does not have.
- **`SP3_size_and_clone_ratchet` 3 → 2.** Seven passes since its move, on a code-duplication gate.

## What replaces the faucet

Deleting rows fixes today's queue and nothing about tomorrow's. The mechanism is a ratchet in
`tests/design/test_maturity_map_contract.py`: the count of `H_harness` atoms with
`provenance: proposal` may never rise above the post-deletion figure. Per CLAUDE.md's own decay
rule — *convert policy to mechanism, or accept it will evaporate* — a prose instruction not to
mint harness work for oneself would have lasted about a week. A new harness atom is still
mintable; it just has to arrive with a director ruling, a steer, or an advisor artefact behind
it, or displace one that is already there.

## What this is not

It is not a claim that harness work is worthless. The harness is how this project knows anything,
and 91 `H_harness` atoms sit at target having earned it. It is a claim about **proportion**: a
queue in which two of every five remaining items are the machine's own controls is a queue that
will keep choosing them, because they are always available, always tractable, and never finished.
