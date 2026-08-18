# WORKER FINDING — D27's note tenant sits 8 bytes under its budget, so the three resume triggers its own pause note declares have nowhere to be written

**Severity:** LATENT · **Lane:** H_harness · **Disposition:** QUEUED (not fixed on sight)

**Found:** 2026-08-18, verifying a DISCOVER fork's landed commit `145a1490f` on
`D27_belief_window_saturates_on_this_book`.
**Class:** a bound that is satisfied and a record that is nonetheless closed — the remedy the bound
deliberately leaves open collides with a different convention governing the same file.
**Measured at:** HEAD `145a1490f`. Everything in §1 is `observed-with-evidence` (R9); §3 is reasoning
from those observations and is labelled where it is inferred.

## 1. The measurement

`D27_belief_window_saturates_on_this_book`'s note tenant is **32,760 of 32,768 bytes — 8 bytes of
headroom** (`tools.simplifications_store.note_tenant_bytes` over the atom's eight `map_notes` fields).

Tested on a **scratch copy** of the store (`shutil.copytree` into a tempdir; the live store was never
written), calling the shipped `set_note_for_atom` unmodified:

* Adding a **new** note field of realistic size — a one-sentence resume record — is **REFUSED**:
  `ValueError: note write to 'resume_note' would take ... to 32825 bytes (from 32760), over the
  32768-byte note budget.`
* **Compacting an existing** note is **ACCEPTED**.

So the ratchet is behaving exactly as its own design comment says it should
(`tools/simplifications_store.py`, "THE MECHANISM IS A RATCHET, NOT A CAP … COMPACTING one is always
available, however far over it already is — the remedy can never be locked behind the bound").
**This finding is not that the control is wrong.** The control is right, and it fired correctly.

## 2. Why it still matters

The note that consumed the last of the budget is D27's own `discover_pause_note`, landed in
`145a1490f`, and it ends by declaring what would restart the atom: *"RESUME ON: BUILD opening, a
D29/D30 edge move reopening the origin question, or a director/advisor steer."*

D29 and D30 both hold live DISCOVER work today, so that middle trigger is not hypothetical. If any of
the three fires, the fact that it fired **cannot be recorded as a new note on this atom** without
first compacting one of the six prior passes' notes — and those six are prose written by six separate
passes under a store convention this repo states repeatedly and enforces in `append_for_atom`
("append-only: existing notes are never rewritten — the register is honest history").

That is the shape R11 names as an orphan transition: a declared release whose effect has nowhere to
go. The atom can still be *worked*; what it cannot do is *say so in the place its own note points to*.

## 3. What is actually in tension (inferred, not observed)

Two rules in this repo both hold, and for this atom they point opposite ways:

* the note ratchet's escape hatch is **compaction** — rewrite an existing note smaller;
* the store's honest-history convention is **append-only** — never rewrite an existing note.

The ratchet's design comment resolves this in the general case by observing that 296 of 297 atoms sit
comfortably inside the budget, so compaction is a rare act. D27 is the case where it is not rare, and
where the compaction candidates are six independently-authored measurement records rather than one
accreted narrative. **Which of the two conventions should yield is a judgment I am explicitly not
making here** — that is the point of filing rather than fixing.

## 4. Why this is filed rather than fixed

`SELF_INTERRUPT_DISCIPLINE`. Nothing is blocked right now: no published figure is wrong, no lane is
held, and D27 is correctly paused at L0 with `loop_stage: idle`. Compacting another pass's note to buy
headroom is precisely the "fix on sight because it is in front of me" move the discipline forbids, and
it would rewrite honest history to satisfy a bound — the trade that needs ranking, not reflex.

This is also **the second recorded instance of the class**, which is what makes it worth a document
rather than a shrug: `tools/simplifications_store.py`'s own docstring records the first two
(`H27_payment_belief_gap` wedged at 54,930 B on 2026-08-17, and `OPS2_publish_gate_head_worktree` at
60,906 B with zero live list entries to drain). The ratchet was built in response and it works; what
it does not do — because it was never asked to — is give an atom that reaches the bound *legitimately*
anywhere to put its next record.

## 5. Suggested shape, recorded not asked (`NEVER_ASK_WITHOUT_RECOMMENDING`)

1. **Do nothing to D27 now.** It is paused; the trigger has not fired. Acting before it fires is
   spending attention on a hypothetical.
2. **When a resume trigger does fire**, the cheapest honest move is a *new dated DISCOVER doc* under
   `docs/design/` (unbounded, already this atom's convention for the substance of every pass) with a
   one-line pointer, and to buy that pointer's bytes by compacting `discover_pause_note` — the newest
   note, authored by this tick, so no other pass's record is touched. Recorded here so the next pass
   does not have to rediscover the constraint under time pressure.
3. **The general question worth ranking** (not built here, single-instance evidence): whether a note
   tenant at the bound should be able to *roll a whole note field* into an archive chunk the way list
   tenants roll entries. `_roll` refuses this today for a stated reason — chopping a string is
   coercion — but moving an entire field is not chopping, and would give the ratchet an escape that
   does not require rewriting anyone's prose. `OPS2` (98% one note, zero drainable entries) is the
   case that would test it.
