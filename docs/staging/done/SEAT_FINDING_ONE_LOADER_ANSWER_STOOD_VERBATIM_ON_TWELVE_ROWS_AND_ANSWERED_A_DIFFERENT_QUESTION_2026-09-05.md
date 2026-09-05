**Severity:** LATENT · **Lane:** H_harness

# One loader answer stood verbatim on twelve census rows, and it answered a different question from the one the field exists for (2026-09-05)

**Type:** [FINDING — measured, with a pre-registration filed before the measurement
(`SEAT_PREREG_TWELVE_CENSUS_ROWS_SHARE_ONE_LOADER_ANSWER_2026-09-05.md`). Severity LATENT: no
verdict in the register moved and nothing published is wrong; the REASONS under eight rows were
unearned, and one carrier can silently swallow a notification.]

---

## 1. What was looked for

The drawn direction was to re-audit every disposition row in
`docs/design/self_clearing_alarm_dispositions.json` whose reason cites a SIBLING row rather than the
code. The named five had already been opened by `9857c0edb` earlier the same day — that pass swept
the `why` field, found seven of eight reasons wrong about their carrier and not one wrong about the
verdict.

It did not sweep the `loader` field. That is where the resemblance had survived, in a form the
earlier pass was not shaped to catch.

## 2. The defect

Not "same as above" on one row. ONE SENTENCE, verbatim, on TWELVE:

> "ASKED AND CLEAN -- measured across the whole partition
> (missing/empty/truncated/null/mapping/list-of-ints/bare-string) against a live prior, no state
> raises and none is a read-modify-write."

`.supervisor_stuck_state.json`, `.atom_stall_tracker.json`, `.boot_announced`,
`.daily_self_note_last_date`, `.maintenance_reminder_sent.json`, `.origin_staging_sync.json`,
`.last_push_time.json`, `.reconcile_watch_state.json`, `.retro_cadence_ntfy_state.json`,
`.last_gate_blocking_tests.json`, `.remainder_annotation.json`, `.product_interleave_state.json`.

**This is worse than "same shape as X", because it does not look inherited.** A row saying "same
shape as X" at least names the row it was graded from — a reader can follow the citation and check
it. A bulk sentence names nothing, so nothing marks it as an answer that was reached once and
applied twelve times. `unasked_loader_rows()`, the rung that made the field mandatory, asks only
that it be non-empty.

## 3. The measurement

The seven-member partition was fed to each of the twelve carriers' own loaders, with each module's
path global repointed at a tmp file first. Results are in each row's rewritten `loader` field.

**"No state raises" — TRUE of all twelve.** That half of the sentence holds.

**"None is a read-modify-write" — FALSE of at least three.** Checkable before any code was read,
against the census's own derivation: nine of the twelve have a writer the census tags
`read-modify-writes its own state`. `.supervisor_stuck_state.json`, `.atom_stall_tracker.json` and
`.product_interleave_state.json` each rewrite the whole record from the loaded one. All three are
safe — and safe for a reason the sentence does not give. `guard_episode` + `prior_unreadable` hold
the first two; an ANNOUNCED reset holds the third. A right answer resting on a false reason is not a
graded row, because the reason is the only part a later reader can check.

**"ASKED AND CLEAN" — answers the wrong question.** `_scope_of_benign` commissioned the `loader`
field to answer one thing: *does the carrier's loader tell ABSENT from PRESENT-BUT-UNREADABLE?* The
shared sentence answers *does anything raise?* On the question the field exists for:

| | rows |
|---|---|
| tells them apart | 3 — `.supervisor_stuck_state.json`, `.atom_stall_tracker.json`, `.product_interleave_state.json` |
| conflates them, argued in its own docstring | 1 — `.last_gate_blocking_tests.json` |
| conflates them, no argument anywhere | **8** |

Seven of the eight fail OPEN — a duplicate boot page, a duplicate daily note, an extra push, a
re-run remainder suite. Loud, and harmless.

**The eighth fails QUIET, and it is the one that matters.** In `background/reconcile_watch.py`,
`_load_last()` returns `[]` for absent AND for every corrupt shape — and `[]` is that carrier's
CLEAN BASELINE. `run()` computes `changed = sig != last`. So with a corrupt state file and a
currently-clean reconcile, `sig == last == []`, `changed` is False, and the drift-**recovery** page
is never sent: the director is left holding the last alarm he received, with nothing anywhere
recording that the all-clear was swallowed. `cleared = not sig and last` is False for the same
reason, so even the tag would have been wrong.

`_load_last`'s docstring *does* name unreadable — and argues only the other direction (a first
clean run must not read as a false transition). That argument is sound and does not reach this case.
Not `real`: no episode is shortened, this alarm's clock lives elsewhere. Filed rather than repaired,
because which way a drift watcher should fail is a judgement belonging with its owner.

**Two more, subtler.** `.seat_continuation.json` and `.weekly_rhythm.json` carried one identical
one-line answer — *"absent and unreadable are told apart, and the unreadable bytes are never
destroyed"*. Both rows were genuinely opened; their `why` fields are thorough and carrier-specific.
But one discriminates at the **writer** (`hand_off` moves the bytes aside; `_load` deliberately
returns `[]` for both, because a lane that can throw takes every other lane down) and the other at
the **loader** (`read_baton` stamps `prior_unreadable` on the rebuilt record). The shared sentence
erased exactly that difference. Same shape as everything else here: the resemblance is asserted
across the axis on which the carriers differ.

## 4. What was changed

All fourteen rows now carry their own measured answer. **No verdict moved** — as in the resemblance
pass before it, and for the same reason: the verdict above a copied reason is right, which is
precisely why nothing would ever have re-asked it.

The rule this leaves is recorded in `_verdicts._scope_of_shared_answers`, and — because a prose rule
with no falsifier is what cost 33 loader annotations nine hours after they landed — it is not left
as prose. A sentence on two rows is either PROVENANCE (when a row was written, by which pass, under
which test) or it is an answer one row did not earn. Provenance is declared in `_shared_provenance`;
anything else shared is refused. Declaring a line there is the act of saying out loud "this is
provenance, not an answer" — the judgement the twelve-row sentence skipped — and it is visible in
the diff for the same reason deleting a row is.

## 5. The generalisation

`_scope_of_resemblance` was written to catch a reason that names its sibling. It could not see the
same defect stated once and applied twelve times, because the defect's signature — a citation —
is absent. **A control that catches inherited answers by looking for the citation is blind to the
inheritance that does not cite.** The cheaper invariant is the one that does not depend on
detecting intent: a claim about one carrier appears on one row.

## Class registration

Belongs to `controls_that_cannot_fail`.

*Declared 2026-09-05 by the delivery seat, on the director's instruction to fold findings into the class registers rather than leave them as individual documents. Classified on the MECHANISM THIS DOCUMENT DESCRIBES (its body), not on its title: the registered classifier greps titles, and the titles have outgrown its vocabulary — which is why 92 findings sat `unclassed` while the six classes held 138 instances. The body carries 4 matches for `controls_that_cannot_fail` against 0 for the runner-up, which is the threshold used; anything below it was left for a reader rather than graded from a sibling.*
