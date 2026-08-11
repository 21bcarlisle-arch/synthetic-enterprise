# WORKER FINDING — the atom's own headline changes SIGN with the population, and the default command reports the chosen one

**Date:** 2026-08-11 (worker tick) · **Atom:** `H_GAP_fabric_belief_truth_gap` (residual (e), Expert Hour)
**Class:** a measurement whose headline is decided by a population choice the artefact does not record.
**Status:** finding 1 FIXED (class-level, R15 both ways, landed). Findings 2–4 OPEN, queued
(SELF_INTERRUPT_DISCIPLINE — registered, not fixed on sight).
**Rank requested:** backlog, behind the declared-defect queue. Nothing is wedged.

This is the Expert Hour that residual (e) has carried as `not_attempted` for six ticks. It was
drawn and not delivered on 2026-08-10 (the tick forked the cold-eyes skill into a site-wide walk
instead of an Hour on this atom's subject). Delivered here on the atom's own subject: the
two-level test, the EPC-vs-actual and inferred-vs-actual fabric gap metrics, and their money
consequence.

Every number below was produced by RUNNING the tool, not by reading it — the ninth time this atom
has surfaced something that way.

---

## Finding 1 — the refresh command could not reproduce the row it refreshes (FIXED)

`tools/couple_fabric.py` defaults to the **AUTHORED 15-premise panel**. The ledger row it writes,
`W1_11_fabric_physics_core`, was measured on **200 premises DRAWN from published stock marginals**.
The two disagree on the **sign** of the atom's headline:

| population | `epc_vs_actual` | `inferred_vs_actual` | `inference_improvement` |
|---|---|---|---|
| AUTHORED panel (15, the tool's default) | 0.2184 | 0.2624 | **−0.0440** (inference LOSES) |
| DRAWN (200, `population_seed=17`) | 0.4269 | 0.4042 | **+0.0227** (inference WINS) |
| DRAWN (200, `population_seed=23`) | 0.4459 | 0.4033 | **+0.0426** (inference WINS) |

`gap_ledger_reconciler.refresh_command` emitted the BASE invocation, so RUNG 4b's acceptance test
— *"the row reads CURRENT afterwards"* — would have been satisfied by
`python3 -m tools.couple_fabric --write-ledger` measuring 15 authored premises over a row measured
on 200 drawn ones, **inverting a published claim about whether inference beats the EPC register**
and calling it freshness.

This is the class filed on 2026-08-10
(`WORKER_FINDING_THE_REFRESH_COMMAND_CAN_CHANGE_THE_POPULATION`) against `W2_11`, where a live
in-run writer reclaimed the row within six minutes. **The fabric row is the variant that finding
explicitly flagged as unprotected** — produced only by an on-demand standalone tool, so nothing
reclaims it. There the exposure is not a six-minute window; it is until someone runs something.

**Fixed at the cause, class-wide.** The tool now records the arguments that reproduce its
measurement (`refresh_args`, plus a human-readable `composition`) into the row, and the reconciler
reads them back. That is *not* the drifting CLI copy `refresh_command`'s docstring rightly rejects
— nothing in the reconciler knows what `--population` means; it concatenates what the run declared.
Rows with no declaration keep the base invocation exactly as before, so no other tool regresses.

`safe_refresh_args` whitelists flags and bare numbers only. The ledger is **data** and this output
is **run by a tick**, so a row may not inject a path, a `--flag=value` pair, an env assignment or a
shell metacharacter; anything else is refused whole and falls back to the base invocation.

R15 both ways — four SOURCE mutations, each firing its own named test, md5 byte-clean restore
(`5b584b68…`), baseline 42 green: (1) ignore the declaration → the reproduce test fires; (2) drop
the whitelist → the injection test fires; (3) stop looking the declaration up → the reproduce test
fires; (4) remove the non-list guard → the malformed-field test fires *and* three neighbours.

**Landed in the same tick as the fix, deliberately.** Editing `background/fabric_gap_ledger.py`
makes it a changed producer of both fabric rows, i.e. the fix's own commit marks them stale — and
the very next drain would have offered the wrong-population command. The re-take on the row's own
population (`--population 200 --population-seed 17`) reproduced **every figure exactly** (gap
0.4269/0.4042, forgone £548,919/£451,832, misranked 10/11, declined 89/73); the entire diff is
`measured_at`, `run_git_commit` and the new fields. Ledger now reconciles clean at 14 of 14.

---

## Finding 2 — both gap headlines are diluted by rows where the two arms are identical (OPEN)

`inference_improvement` is averaged over premises where **the inference never ran**. A premise with
no meter history (`epc_only`) or no certificate (`stock_prior`) has `inferred == epc` to the bit:

- AUTHORED panel: **7 of 15 (47%)** are ties.
- DRAWN population: **164–166 of 200 (82–83%)** are ties.

So on the population the ledger publishes, ~83% of rows carry **zero information** about the thing
the metric is named after, and the headline is ~1/6 of the effect size on the rows where inference
actually happened. Two consequences, neither currently visible on the door:

1. The published `+0.0227` **understates** what inference buys where it operates, by roughly the
   tie fraction — the number is a blend of "inference helped" and "nothing was asked of it".
2. The headline **moves when EPC lodgement coverage moves**, with nothing about the inference
   having changed. A stock with better certificate coverage would print a different
   "inference improvement" for an identical estimator. That is the dominant-subpopulation shape
   this repo already has memory of, sitting inside this atom's own headline.

Shape of the fix: report the metric **conditioned on basis** (`meter_and_epc` vs the tie set)
alongside the population figure, and carry the tie fraction in the row so a reader cannot mistake
coverage for skill.

---

## Finding 3 — the gap metric is a magnitude and is blind to a systematic sign (OPEN)

The gap is `|belief − actual|`-shaped, so it cannot distinguish *noisy but unbiased* from
*consistently wrong in one direction* — and the latter is the one that tilts every retrofit
decision the same way. Measured on the authored panel:

- **EPC signed error: 14 of 15 UNDER-estimate** heat loss (signed mean −0.0171). That is a bias,
  not noise. It is also real-world plausible (RdSAP under-stating loss), which is exactly why it
  should be *measured* rather than absorbed into a magnitude.
- **The inference revises EPC upward in 8 of 8** meter-armed premises (signed mean +0.0228).

A one-signed belief error is a different animal from a symmetric one: it means the company is not
merely imprecise about houses, it is wrong about *the housing stock* in a fixed direction. The
ledger carries `bias_model` but the headline the door renders does not.

---

## Finding 4 — the money verdict is flattered by that agreement of signs (OPEN)

On the authored panel the atom's two headline numbers **point in opposite directions and are
reported side by side without noting it**:

- accuracy: inference is **worse** (0.2624 vs 0.2184)
- money: inference is **better** — £18,603 vs £43,983 forgone, declined-where-value-existed **6 → 3**

The mechanism is Finding 3. An upward-biased heat-loss belief recommends *more* measures; on a
panel where truth exceeds EPC in 14 of 15 cases, recommending more is right more often. So the
money advantage is bought by a **bias that happens to point the panel's way**, not by accuracy.

This is testable and currently untested: compose a panel of homes whose EPC **over**-states loss
(new-build over-rating, post-retrofit certificates never re-lodged — both real), and the same
estimator should push the money verdict the other way. Until that is run, "inference saves
£25k of forgone value" is a statement about the panel as much as about the estimator.

Note the drawn population does **not** rescue this: it is 63% actual-above-EPC against the panel's
93%, so it is less one-sided, not two-sided.

**Shape of the fix (R10, class not instance):** a standing control that measures the money verdict
on a **sign-mirrored** population and fails when the ranking is composition-decided. That is a
harness construction, not a curriculum change — R13 is not engaged, and R12 is respected because
nothing is tuned toward a band.

---

## What did NOT move, and why

`level_current` stays **2**. Residual (e) is now delivered rather than deferred, but the Hour's own
output is new residual: an atom whose headline is composition-dependent (2), direction-blind (3)
and whose two headline numbers disagree without saying so (4) does not have an L3 story. Recording
that plainly is cheaper than a level that has to come back down.

Residuals (a) L1.4 magnitude and (b) L1.2h heating-shape repeatability are unchanged and unchanged
in reason (both blocked on data this repo does not hold). (c) remains W1_12's.
