# WORKER FINDING — the drain's refresh command re-takes the measurement on a *different population*

**Severity:** BLOCKING · **Lane:** H_harness
**Discharged:** `tests/background/test_gap_ledger_reconciler.py::test_SUPPORT_CHANGED_IS_NOT_OFFERED_A_COMMAND_so_the_drain_cannot_publish_it`, `background/gap_ledger_reconciler.py` — the reconcile now grades what a row was measured OVER, not only which commit measured it, and a row whose population moved is refused a refresh command instead of being handed one
<!-- DISCHARGED 2026-08-12 by a worker tick drawn at RUNG 1c. Unlike the six discharged earlier
     the same day, this document was genuinely OPEN — it says so in its own Status line
     ("registered, not fixed on sight") and left its close design unbuilt. It is released
     because that design is now BUILT, not because it was already repaired when it was filed.
     Close items 1 and 2 landed; item 3 is a design question this deliberately still does not
     guess, and is restated below as what was NOT closed. The falsifier named above was run
     green, and its seven mutations run, before this line was written. -->

**Date:** 2026-08-10 (worker tick) · **Atom:** `H_GAP_fabric_belief_truth_gap` (RUNG 4b, its own drain)
**Class:** a freshness control whose repair action satisfies the control while silently replacing
the quantity it was protecting.
**Status:** OPEN, queued (SELF_INTERRUPT_DISCIPLINE — registered, not fixed on sight).
**Rank requested:** backlog, behind the declared-defect queue. Nothing is wedged by it.

## The finding, observed with evidence

RUNG 4b (`background/supervisor.py::_stale_gap_row_draw`) drew
`W2_11_payment_behaviour_source` as stale and offered
`python3 -m tools.couple_w2_11_d5 --write-ledger`. That command ran rc=0 and the row now reads
CURRENT. The acceptance test the rung states — *"re-run the reconciler and show the row reading
CURRENT"* — passed exactly as designed.

The number moved, and **the population moved with it**:

```
BEFORE   gap 0.0859375              universe_size 1557    truth_size 31
AFTER    gap 0.013094021461420541   universe_size 12000   truth_size 1215
```

The published row was written **in-run by `run_phase2b`**, over the population that run actually
had. `tools/couple_w2_11_d5.py` has its own CLI defaults, and `refresh_command()` emits the **base
invocation and nothing cleverer** — deliberately, and for a good reason it states: inventing
arguments here would be a second, drifting copy of each tool's CLI.

So the re-run did not *re-take* the measurement. It **took a different one** and wrote it to the
same row. Freshness is now genuinely satisfied — the code that produced this number is the code at
HEAD — but a 6.6x move on a public figure is being carried by the ledger as though it were the
same measurement refreshed, and nothing in the reconcile can tell the two apart.

**This is not an argument for reverting the row.** The old figure was produced by code HEAD no
longer contains; it was ungradeable, which is what `stale` means. Both facts are true at once: the
new number is the honest one *and* it is not comparable with what it replaced.

## It self-healed within six minutes, and that is the sharpest part of the finding

The tool wrote at `13:22:40`. At `13:28:30` a live `run_phase2b` re-wrote the same row from its own
run — back to `gap 0.0859375`, `universe_size 1557`, stamped at the current HEAD — and the
reconcile reads clean at 14 of 14. **The committed ledger carries the in-run figure, not the
tool's**, because the in-run writer is the row's real owner and simply reclaimed it.

That is genuinely reassuring for `W2_11` and it is exactly what makes the class worth filing:

- For a row with a **live in-run writer**, the wrong-population window is minutes, and nobody was
  ever going to see it. The control is effectively self-correcting.
- For a row with **no live writer** — every row produced only by a standalone `couple_*` tool run
  on demand — there is no reclaim. Whatever the drain wrote is what the public door carries until
  someone runs something again.

So the exposure is not uniform across the family, and the reconcile cannot distinguish the two
cases. A row that is re-measured by a running process every few minutes and a row that is
re-measured only when a rung draws it are graded by identical logic and reported with identical
confidence.

**Corollary worth checking separately:** if `run_phase2b` owns `W2_11` and rewrites it on every
run, then that row can only ever go stale *between* runs, and RUNG 4b drawing it is arguably wasted
work — the next run clears it regardless. Whether the drain should skip rows with a live in-run
writer is a real question this finding does not answer.

## Why it matters

This is the `one name, two numbers` shape (`feedback_one_name_two_numbers_across_dimensions`)
arriving through a new door — not two dimensions disagreeing, but one dimension disagreeing with
its own past self across a refresh. The reconciler grades **who measured** (which commit) and is
blind to **what was measured over** (which population). A control that verifies provenance and
ignores support will call a replaced quantity a refreshed one every time.

It also touches R14's spirit: the row carries its clock (`run_git_commit`, `measured_at`) but not
its *support*. A figure whose denominator can change by 8x between two readings of the same row
name wants that denominator recorded beside the clock.

## What would close it (not built here)

1. **Record the support in the row.** `universe_size` / `truth_size` already exist inside
   `components` for this metric family but are not part of the reconcile's contract. Promote a
   support descriptor to a first-class ledger field every writer must set.
2. **Have the reconcile report a support change** as its own status — not `stale`, not `current`,
   but *"this row's population moved between measurements"*, which is a fact about the row and
   wants a human reading rather than a silent republish.
3. **Decide, per row, whether the tool's defaults ARE the row's population.** For rows written by
   a standalone `couple_*` tool they are, by construction. For `W2_11`, written in-run, they are
   not, and that mismatch is the whole finding. This is a design question, deliberately not
   guessed here — the same refusal `WORKER_FINDING_DERIVED_ARTEFACT_STALENESS_IS_A_WEDGE_CLASS`
   applied to re-run ownership.

Do **not** close this by pinning arguments into `refresh_command()`. That rebuilds each tool's CLI
in a second place, which is the defect that function's docstring already refuses.

## Evidence

- `docs/observability/coupled_gap_ledger.json` — `W2_11_payment_behaviour_source`, before/after
  values above, taken this tick.
- `background/gap_ledger_reconciler.py::refresh_command` — the base-invocation rule and its reason.
- `background/supervisor.py::_stale_gap_row_draw` — the acceptance test the re-run satisfied.

---

## CLOSED 2026-08-12 — what was built, and what was deliberately not

**Close item 1 (record the support) — landed, on the READ side.** `row_support()` resolves a
row's population from a first-class `support` field when a writer sets one and otherwise from
declared candidates in `components`, **in that order**. That ordering is the point: promoting
the descriptor to a written field later is a strict upgrade needing no change here and no
re-grading of the rows already carrying it. Nothing was made mandatory of every writer, because
a new required field would grade every historical row ungradeable forever.

**Close item 2 (a status of its own) — landed.** `support_changed`: *"this row's population
moved between measurements"*, distinct from `stale` and from `current`, carrying the moved keys
with before → after. Its sibling `support_ungradeable` is the same question asked of a row that
cannot answer — an unavailable check is a failed check (R15), so a second measurement of a
descriptor-less row may not be landed on the strength of a check that could not run.

**Close item 3 (whose population is the row's?) — NOT closed, and not guessed.** It is a design
question per the finding, and the corollary it raises — whether RUNG 4b should skip rows with a
live in-run writer — is still unanswered. Neither is needed for the above to hold.

**`refresh_command()` was not touched.** No arguments were pinned into it; the defect that
function's docstring refuses was not rebuilt.

## The release has an effect, and it fired on the live tree

Not a label. `SUPPORT_CHANGED`/`SUPPORT_UNGRADEABLE` are refused a command in `refresh_work`,
where `MEASURED_NOT_LANDED` is handed `surgical_land`. Measured at HEAD on the real working
tree, on the very row this finding was found on:

```
HEAD's code:  x [measured_not_landed] W2_11_payment_behaviour_source ...
              -> W2_11_payment_behaviour_source [measured_not_landed]:
                 python3 -m tools.surgical_land -m 'chore(gap-ledger): land the ... measurement'

this change:  x [support_changed] W2_11_payment_behaviour_source: this row's population moved
                 between measurements (truth_size 31 -> 4; universe_size 1557 -> 276) ...
              (no command; 3 rows a re-run would clear, was 4)
```

The finding was **live, not historical**: the working-tree ledger holds a W2_11 re-measurement
on a population 5.6x smaller than the committed one, and the drain was about to publish it as a
refresh. That is the defect reproducing itself, caught by the control built for it.

## What this does NOT catch — stated, not implied

The comparison needs **two measurements**: the committed row and the working-tree row. Once a
support change is committed, HEAD and disk agree and the move is invisible to this — catching it
afterwards needs the row to carry its own previous support, which is a bigger design and is not
here. The window this DOES cover is the one that matters for publication: the drain writes to
disk and a later tick lands it, so the refusal happens before the number reaches the door.

Four live rows — `W1_5`, `W1_6`, `W2_4`, `W2_6` — record no population size at all and therefore
report `support_ungradeable` **if and only if** they are re-measured. A row with one measurement
gets no support verdict, deliberately: without that condition those four would report ungradeable
on every clean reconcile forever, which is an alarm no act can clear.

**R15, seven source mutations, each firing its own named test**, `md5sum -c` byte-clean restore
(`eb0657fd7059fa9d8fd1411d95f87953`): silent removal of the pass (reproduces the shipped state,
6 fire) / the pass skipping `current` rows (the fail-open it exists for) / a missing descriptor
read as an empty support that compares equal / the refusal dropped from `refresh_work` (the
release) / a name-shaped rule instead of the declared register (`caught`, `n_false_flags` read as
population) / the one-measurement guard dropped (always-red) / a vanished key read as agreement.
Not always-red: an honest re-measurement on the same population still reads
`measured_not_landed` and stays drainable.

**Suites:** 53 passed `test_gap_ledger_reconciler` (was 40), 65 with `test_reconcile_watch`,
21 across the consuming draw rungs (`test_stale_gap_row_draw`, `test_rest_ladder_isolation`).

**Note on landing this document:** the first write of this header was reverted to HEAD by a
concurrent writer on the shared tree within minutes, code changes untouched — the
`docs/staging/`-edit sweep this project already has memory of. Re-applied and committed
immediately rather than left on disk.
