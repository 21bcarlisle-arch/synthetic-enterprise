# WORKER FINDING (QUEUED) — the only Proof-door pair a test process can re-publish is this atom's own, and until this tick nothing compared any door figure to the ledger it derives from

**Severity:** BLOCKING · **Lane:** H_harness · **Disposition:** PARTIALLY BUILT (the detecting control is landed; two named repairs are QUEUED, both outside this atom's `file_scope`)

**Found by:** H27 Expert Hour #33, the 2026-08-17 worker tick, drawn as
`H27_payment_belief_gap` 2->3 HARDEN. Hour #31 pre-committed the promotion condition ("an
Hour that ends with no BLOCKING finding against the corrected instrument") before #32 ran,
and #32 failed it with three. This is the fifth consecutive Hour on this instrument to end
with a real defect, and by that same pre-committed rule **the level does not move.**

## Observed, with evidence

### 1. One of fourteen pairs moved, and it was this one

`site/data/proof.json` was regenerated in the working tree at `2026-08-17T15:54:44Z`.
Comparing all fourteen `coupled_gaps.pairs` against `HEAD` and against the deployed door:

| pair | HEAD | working tree | live (fetched) |
|---|---|---|---|
| `W2_11_payment_behaviour_source` | 0.0833907649896623 | **0.0311284046692607** | 0.0833907649896623 |
| the other 13 | — | bit-identical | bit-identical |

The whole book moved with it: `caught` 31→4, `flagged_size` 391→35, `n_negatives` 1451→257,
`n_excluded` 118→15, `n_false_flags` 242→16, `universe_size` 1600→276,
`false_flag_rate` 0.166782→0.062257. **A 2.68x understatement of the company's own payment
belief-vs-truth gap**, published into the door's payload.

### 2. Why it was this pair, and only this pair — the mechanism, not the incident

This pair's ledger entry is the only one of the fourteen written as a **side effect of
running the simulation**: `simulation/run_phase2b.py:2448` calls
`LivePaymentTriad.measure_and_write(run_git_commit=_triad_head)` with `ledger_path` defaulted,
so `background.gap_metric.write_gap_entry` resolves it to the real
`docs/observability/coupled_gap_ledger.json`. Every other pair's entry is written by its own
`tools/couple_*.py --write-ledger` invocation, which no test runs.

`grep -rln run_phase2b tests/` returns **ten-plus test modules**. Each one, on every run,
overwrites the live payment-gap measurement with its fixture book. At `15:38:56Z` the live
ledger held a 276-invoice book; the 15:54 regeneration read the working-tree ledger and
published it.

**Observed twice in this tick, not inferred.** Running
`pytest tests/tools/test_couple_w2_11_d5.py` moved the live ledger's `measured_at`
16:34:19 → 16:42:56 while the run was in flight (md5 `825330de9…` → `e56aa515c…`). That
particular write was harmless to the figures — this module measures the full 1600-invoice
book, so `gap` stayed bit-identical at 0.0833907649896623 — but it is the same write path,
from a test process, into the supplier of a public door.

### 3. Nothing could see it, because the defect is only in the RELATION

The door agrees with itself. The ledger agrees with itself. The generator did exactly what
it was asked. The scorer is not involved at all. Every existing control on this instrument
reads one side, and the substitution is invisible to all of them — including the SITE-lane
control Hour #32 built, which deliberately excludes the ledger as a subject.

### 4. The committed pair has ALSO never agreed — measured here for the first time

This was recorded narratively as RECORDED 7 of the 2026-08-15 finding. Running the new
control against `git show HEAD:` on both files makes it exact:

> committed door `value` **0.0833907649896623** (generated 2026-08-17T15:13:08Z) vs
> committed ledger `gap` **0.0859375** (measured 2026-08-12T06:10:09Z);
> `n_negatives` 1451 vs 1408, `universe_size` 1600 vs 1557, `false_flag_rate` 0.166782 vs 0.171875

The file the public door nominally derives from is not the file it was generated from, and
has not been for five days.

## What this tick BUILT

`check_published_door_reproduces_the_ledger` + `measure_published_door_against_the_ledger`
in `tools/couple_w2_11_d5.py`, wired into `main()` on the default path with its verdict
rendered (the R10 lesson this instrument has now paid for four times), and 11 tests in
`tests/tools/test_couple_w2_11_d5.py`.

**R15 both ways, proven against real history rather than a fixture.** RED on the poisoned
working-tree door as found — 9 violations, the headline and 8 components. GREEN once that
door was restored. **Four source mutations, all proven to fire:**

| mutation | pattern | reds |
|---|---|---|
| unreadable file caught into `{}` | FAIL-SILENT | `test_an_absent_artefact_is_a_failed_check_never_a_clean_one` |
| compare the headline, skip the components | wrong subject | `test_a_headline_that_agrees_while_the_book_underneath_does_not_fires` |
| drop the vacuity guard | TAUTOLOGY | `test_a_pair_sharing_no_comparable_component_is_a_violation` |
| absent door pair treated as a skip | FAIL-OPEN | `test_a_side_that_has_stopped_carrying_this_pair_fires` |

The component population is not hand-picked: `test_the_component_population_is_not_a_hand_picked_subset`
derives the set that actually moved in the incident and asserts none of it falls outside the
control's subject.

**R12: no number this instrument computes was touched.** The only figure that moved is the
door's, and it moved *back* — `git checkout HEAD -- site/data/proof.json` restored the
regenerated door to the value the deployed site and the current ledger both carry
(0.0833907649896623). Reversal is the corrupted payload, preserved at
`/tmp/h33_proof_poisoned.json`.

## What this tick did NOT build, and why — named so the next tick does not re-derive it

1. **The write itself is not stopped.** The fix is at `simulation/run_phase2b.py:2448`
   (default `ledger_path` → redirect or refuse under a test process). That file is outside
   this atom's `file_scope` **and is carrying another lane's uncommitted hunks at :160 and
   :834** in this tree, so landing a hunk there would sweep work whose record I do not have
   — the two-lanes-one-file shape filed on 2026-08-15. SELF-INTERRUPT DISCIPLINE: queued.
2. **The SITE-lane live tripwire is not shipped, and the reason is finding 4.** The natural
   home for a gating version of this control is `site/proof/`, whose gate fires on a
   `site/data` change — exactly when a substitution lands. It was not shipped because
   **it would be born RED**: the committed pair already diverges at HEAD (finding 4), so
   landing it wedges the publish gate on a condition this atom cannot fix. Repairing that
   divergence means regenerating and committing the ledger, which moves published figures
   and is live territory for the publish lane this same day
   (`WORKER_FINDING_THE_PUBLISH_PATH_COMMITS_THE_DOOR_AND_NOT_THE_RECORD_IT_RENDERED_2026-08-17.md`).
   A control that must wedge a shared gate to be honest is a sequencing problem, not a
   reason to weaken the control — so it is written down at full strength and left owed.

## A second, independent defect this Hour hit while recording the first

**This atom's own record had become unwritable, and the roll cannot drain it.** Appending
Hour #33 to `map_notes.level_hold_note` took it to 54,930 chars — 81% of
`docs/design/simplifications/H27_payment_belief_gap.yaml`, whose size went to 67,812 B
against `store.ROLL_WATERMARK` = 65,536 B. The pre-commit gate refused the commit on
`tests/design/test_simplifications_store.py::test_the_live_store_has_roll_headroom`, which is
exactly the wedge that control exists to catch, caught one entry before it cost a publish.

`roll_for_atom("H27_payment_belief_gap")` returns **0**: the roll chunks LIST entries, and
this is a single string field it cannot split. Thirty-three Hours appending to one field is
the cause; Hour #33 only tipped it.

**Repaired here, on the store's own stated contract** — `set_note_for_atom`'s docstring: *"A
note is a CURRENT statement about the atom … revision is the correct semantics; the durable
history of what changed lives in git."* The note was compacted 54,930 → 7,123 chars (store
file 67,812 → 19,856 B), keeping the hold reason, the pre-committed exit condition, the
per-Hour defect rate that is the evidence for the hold, Hour #33, the ranked owed work, and
the disclosed non-blockers. Hours #3–#32's individual narratives are in this file's git
history and in the commit that landed Hour #33 — nothing is deleted. Full pre-compaction text
also at `/tmp/h33_level_hold_note_full.txt`. Store battery: **84 passed**.

**Owed, not taken:** the roll has no path for an oversized *note* field, so this recurs. The
fix is either a size bound on notes with an archive path of their own, or every Hour compacts
as it writes. This tick chose the second because the first is a store change outside this
atom.

## Not established, flagged rather than asserted (R9)

* **Which** test module wrote the 276-invoice book at 15:38:56Z is **not identified**. What
  is observed is the population's size and shape, that `run_phase2b` is the only live writer
  of this key, and that ten-plus test modules invoke it. The mechanism does not depend on
  which one.
* Whether the 15:54 regeneration was a deliberate act by another lane is **not checked**. It
  produced a door no ledger on disk supported either way.
* No reader was served the fixture book. The deployed payload (fetched this tick, HTTP 200,
  776,446 bytes, `generated_at` 2026-08-17T15:13:08Z) carries 31/391/1451/1600. The harm was
  one broad-pathspec commit away, which is the same distance Hour #32's finding 1 measured.

## One disclosure about this Hour's own footprint

This Hour's own test runs moved the live ledger's `measured_at` (16:34:19 → 16:42:56 →
later), for the reason the finding describes. **The ledger is deliberately NOT in this
tick's pathspec**: committing it would publish a timestamp from a test process as the
measurement of record, which is the defect. Snapshot of the pre-Hour state at
`/tmp/h33_ledger_before.json`.

Separately: running the source-mutation battery on the module while an 8:56 suite was still
in flight produced **7 false reds**, all of them `inspect.getsource(pair.main)` tests reading
a file mid-swap. They are an artefact of this Hour's method, not a finding. The clean run is
the one reported in the record.
