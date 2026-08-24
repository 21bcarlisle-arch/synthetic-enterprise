# The belief was right, and the number is worse than he put it — 2026-08-24

Answering `docs/staging/DIRECTOR_CONSOLE_2026-08-24.md` (05:42Z): *"A belief for you to test, not
accept: we have been spinning our wheels… You hold the measurements. Test it properly and tell me
if I'm wrong."* This is that record, and it is the disposition of that console capture — the
capture is verbatim and is never edited, so the judgement lives here and cites it.

Every figure below is derived from a store already on disk, named with the file it came from, so
each is re-derivable by the reader rather than taken on this document's word.

## 1. Level moves per day

Source: `docs/observability/gate_authorizations.jsonl`, counting DISTINCT `(atom, level)` pairs on
`LEVEL_UP*` actions — so an atom re-recorded three times in a day counts once.

| day | distinct level moves | ticks spawned |
|---|---|---|
| 2026-08-19 | 8 | 85 |
| 2026-08-20 | **0** | 88 |
| 2026-08-21 | **0** | 57 |
| 2026-08-22 | **0** | 22 |
| 2026-08-23 | **0** | 6 |
| 2026-08-24 | **0** | 2 |

Tick counts: `docs/observability/model_tier_log.jsonl`. **The last level move on the record is
2026-08-19.** Five days, 175 ticks, zero.

This makes the weekend evidence stronger than the director put it. His reading was that a 90% cut
in tick spawns cost almost nothing of value. The measurement says the cut could not have cost a
level move, because **the two full-cadence days immediately before it (145 ticks) produced none
either**. The stand-down did not reduce output; it revealed that output was already zero.

## 2. What proportion of draws end in shipped capability

Over the window the tick log covers (2026-08-12 → 2026-08-24): **32** distinct atom-level moves
against **1,113** ticks = **2.9%**. Excluding 2026-08-15's anomalous 552-tick day, 32 against 561
= **5.7%**. The honest statement is a band, 3–6%, and it is **0 of 175 for the last five days**.

## 3. How much of the queue is the machine's own findings about its own controls

Staging root, 18 actionable files: **15 (83%)** are the machine writing about itself — 10
`WORKER_FINDING_*` and 5 `CLASS_*` documents. Of those 10 findings, **9 are re-mints of just 3
alarm signatures** across three consecutive days (`deadman_open_mint`, `deadman_hard_rest`,
`selfdrawable_mint`), filed by `background/alarm_repetition.py`. Three conditions, nine documents,
each one a doorbell that draws a full context.

## 4. Where the passes actually went

Source: `tools/discovery_pass_ceiling.survey()`, passes since each atom's level last moved.

    EP6_wall_protocol_typing        55   build
    H27_payment_belief_gap          43   harden
    SITE2_two_sided_wall_exhibit    18   build

**One atom, EP6, consumed 55 passes — more than the entire map recorded level moves (32) over the
same fortnight.** It was drawable throughout because the pass ceiling shipped on 2026-08-19
exempted `build`, on a premise stated as a design decision and never measured: *"for a saturated
build atom, drawing it again IS the promote path the ceiling demands."* Fifty-five passes is not a
promote path being attempted.

## 5. What changed today, and it is a change to how work gets chosen

The `build` exemption is gone. `tools.discovery_pass_ceiling.core_draw_exclusions()` now gates the
core draw at each candidate's own stage — `harden` at 5 passes, `build` at `BUILD_CEILING` (10) —
and `supervisor._exclude_saturated_from_core_draw` applies whatever it returns. The 2x asymmetry
survives as a DIAL, not an exemption, because a build pass CAN move a level and a harden pass
cannot: build gets double the rope, not unlimited rope.

Live effect at the moment of landing — 7 atoms now excluded from the core draw:
`EP6_wall_protocol_typing`, `SITE2_two_sided_wall_exhibit`, `H27_payment_belief_gap`,
`HX2_stall_set_coverage_verdict`, `W3_1b_intra_year_price_cap_granularity`,
`D_money_boundary_reconciliation`, `W2_payment_channel_dd_consistency_invariant`. Still drawable
and deliberately so: `SP3` (7), `EP1_clv_three_horizon` (6), `SITE1_expert_doors` (5), `G4` (5).

R15: `tests/background/test_harden_rung_pass_ceiling.py`, 12 passed. Four mutation nodes plus the
null control `test_a_saturated_BUILD_atom_UNDER_the_build_ceiling_survives` — without that pin the
two ceilings collapse into one and the asymmetry dies silently. Fails OPEN on a broken ceiling and
keeps the full set if the exclusion would empty it (Rule 0 structurally, not by comment).

**SITE is left ungated on purpose**, and the measurement is the reason: it is the one lane whose
output a reader sees, and it is where the fortnight says the project was UNDER-spending. This
ceiling exists to stop unbounded investigation, not to stop pages being finished.

## 6. What this tick did NOT do, named rather than left to be discovered

- **The 9 duplicate alarm documents are still in the staging root.** They should not have been
  filed and the fix belongs in `alarm_repetition.py` (suppress a mint whose class document already
  covers the signature — the director's own instruction). Not done here: a bulk staging archive
  wedged publishing for three hours on 2026-08-23 (commit `f4c44f195`), and a concurrent lane was
  mid-archive on this tree while this tick ran. Queued, not fixed on sight.
- **Both `DIRECTOR_CONSOLE_*` files stay in the staging root**, because the brief they carry is
  live until Friday. `DIRECTOR_CONSOLE_2026-08-22.md` item 2 (72 tests newly failing at HEAD) has
  not been re-verified by this tick and is not claimed as closed.
- **The reader-visible test is not met yet.** By Friday the site has to show something a customer
  or a domain expert would care about that is not there today. Nothing on this tick's record
  reaches a reader; this tick changed what the draw is allowed to hand out, which is the
  precondition for the next ones reaching one.
