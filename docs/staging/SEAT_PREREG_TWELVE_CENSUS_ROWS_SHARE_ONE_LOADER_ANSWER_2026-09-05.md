**Severity:** LATENT · **Lane:** H_harness

# [PRE-REGISTRATION] — Twelve census rows share one verbatim loader answer (2026-09-05)

**Type:** [PRE-REGISTRATION — written BEFORE the measurement, so the prediction can refute the
predictor. Severity LATENT: the rows' VERDICTS are not in question, the REASONS under them are.]

---

## The subject

`docs/design/self_clearing_alarm_dispositions.json`. The 2026-09-05 resemblance re-audit
(`9857c0edb`) opened eight rows whose `why` deferred to a sibling. It did not look at the `loader`
field, and that is where the resemblance survived — not as "same as above" on one row, but as ONE
SENTENCE COPIED ONTO TWELVE:

> "ASKED AND CLEAN -- measured across the whole partition
> (missing/empty/truncated/null/mapping/list-of-ints/bare-string) against a live prior, no state
> raises and none is a read-modify-write."

Verbatim on: `.supervisor_stuck_state.json`, `.atom_stall_tracker.json`, `.boot_announced`,
`.daily_self_note_last_date`, `.maintenance_reminder_sent.json`, `.origin_staging_sync.json`,
`.last_push_time.json`, `.reconcile_watch_state.json`, `.retro_cadence_ntfy_state.json`,
`.last_gate_blocking_tests.json`, `.remainder_annotation.json`, `.product_interleave_state.json`.

This is the same defect as "same as above" and a worse one, because it does not LOOK inherited. A
row saying "same shape as X" at least names the row it was graded from; a bulk sentence names
nothing, so nothing marks it as an answer that was reached once and applied twelve times. Twelve
carriers cannot all have the same loader unless somebody checked, and `unasked_loader_rows()` — the
rung that made these fields mandatory — asks only that the field be NON-EMPTY.

## Why it is checkable and not merely suspicious

The sentence makes two claims a machine can contradict:

1. **"no state raises"** — a claim about a partition of seven inputs against each carrier's loader.
2. **"none is a read-modify-write"** — and the census DERIVES this. `_failure_reason` tags a writer
   `"read-modify-writes its own state (a failure outcome overwrites the episode)"`. If the census's
   own `failure_writers[].why` says read-modify-write for a path whose row says none is, the row
   contradicts the artefact it is a disposition OF.

## The predictions, before the measurement

- **P1.** At least **3** of the 12 rows carry a claim in that sentence that is FALSE against the
  carrier's own code.
- **P2.** **Zero** verdicts flip (`benign`↔`real`). The re-audit found 7 of 8 reasons wrong and 0
  verdicts wrong; the reason a wrong reason survives is that the verdict above it is right.
- **P3.** At least **1** of the 12 has a census-derived read-modify-write failure writer, directly
  contradicting "none is a read-modify-write" — checkable mechanically, before any code is read.

## What "done" is for this direction

Every one of the 12 opened against its carrier's loader and writer; each row's `loader` replaced by
what its OWN code does, or explicitly marked as verified with the evidence that verified it; and —
because a prose rule with no falsifier is what cost 33 annotations nine hours after they landed — a
rung that can SEE a shared answer, so the thirteenth copy lands red.

*Result appended below this line after the measurement, whichever way it goes.*

---

## RESULT (appended 2026-09-05, after the measurement)

**P1 — CONFIRMED, and by a wider margin than predicted.** Predicted ≥3 rows carrying a false claim.
"No state raises" is TRUE of all twelve. "None is a read-modify-write" is FALSE of three
(`.supervisor_stuck_state.json`, `.atom_stall_tracker.json`, `.product_interleave_state.json` — all
whole-record rewrites, all safe for a reason the sentence does not give). And the headline verdict
"ASKED AND CLEAN" is unearned on **eight**, because it answers a different question from the one
`_scope_of_benign` commissioned the field for: on *does the loader tell ABSENT from
PRESENT-BUT-UNREADABLE*, only three of twelve answer yes.

**P2 — CONFIRMED.** Zero verdicts moved. Fourteen rows rewritten, every `benign`/`real` unchanged.
The third such pass in a row to find the reasons wrong and the verdicts right.

**P3 — CONFIRMED, 9 of 12 rather than the predicted ≥1.** The census's own `failure_writers[].why`
tags a read-modify-write on nine of the twelve paths whose rows say none is one. Settled
mechanically, before a line of carrier code was read.

**WHAT THE PREDICTION MISSED, recorded because it is the part worth keeping.** All three predictions
were about the sentence being FALSE. The sentence's real defect is that its true half is an answer
to the wrong question — "nothing raises" is not "the loader tells absent from unreadable", and
twelve rows recorded the first as though it settled the second. A prediction framed as
*is-this-claim-true* could not have found that; it took running the partition and reading what
`_scope_of_benign` actually asks for.

**AND ONE THE SWEEP FOUND THAT THE PRE-REGISTRATION DID NOT SCOPE.** Two further rows,
`.seat_continuation.json` and `.weekly_rhythm.json`, shared a one-line answer. Both were genuinely
opened — but one discriminates at the WRITER and the other at the LOADER, and the identical sentence
erased that. The pre-registration named twelve rows; the property (a claim about one carrier belongs
on one row) found fourteen. Keyed to the property, not to today's answer.

Full write-up:
`SEAT_FINDING_ONE_LOADER_ANSWER_STOOD_VERBATIM_ON_TWELVE_ROWS_AND_ANSWERED_A_DIFFERENT_QUESTION_2026-09-05.md`.
