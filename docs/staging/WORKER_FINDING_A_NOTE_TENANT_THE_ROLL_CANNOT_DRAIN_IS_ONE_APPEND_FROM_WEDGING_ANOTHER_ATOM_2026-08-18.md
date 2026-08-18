# WORKER FINDING — a note tenant the roll cannot drain is one append from wedging another atom

**Severity:** LATENT · **Lane:** H_harness

LATENT states what this pass FOUND, not what it left: a real wedge that had not yet fired — no
published figure and no control's verdict depended on it — but which sat one append from firing on
`OPS2_publish_gate_head_worktree`, so it was never a mere accepted limitation. The discharge below
then releases it to RECORDED, which is that field working as designed: the defect was repaired in
the same document, and the release is machine-checked against named falsifiers rather than taken on
the word "landed". The OPS2 debt it leaves behind is declared separately and is NOT discharged.

**Found:** 2026-08-18, worker tick, H27_payment_belief_gap self-refill 2→3 HARDEN draw (Hour #37)
**Class:** a bounded control over a monotonic append-only record wedges the lane that keeps the record
**Discharged:** `tests/design/test_simplifications_store.py::test_a_note_write_over_the_budget_is_refused_and_damages_nothing`, `tests/design/test_simplifications_store.py::test_no_live_atom_carries_a_note_tenant_the_roll_cannot_rescue`, `tests/design/test_simplifications_store.py::test_the_roll_cannot_drain_a_note_which_is_why_the_ratchet_exists`, `tools/simplifications_store.py` — the growth path is refused at the sole note writer, the live store is measured by a standing control, and the premise itself is held as a test so the ratchet cannot outlive its reason. The declared OPS2 debt below is NOT discharged.

## The claim, and its evidence label

`observed-with-evidence` unless marked otherwise.

## What was drawn, and what was already known

H27's own ranked owed list carried item (B), written by Expert Hour #33 after this atom's
`level_hold_note` reached 54,930 B and made the atom's record unwritable:

> THE NOTE-FIELD ROLL — the roll chunks LIST entries and cannot split one string field, so this
> note wedges again if Hours resume appending; every Hour must compact as it writes until notes
> get a size bound and an archive path of their own, a store change outside this atom.

That is a convention, and a convention is the class of rule this project has repeatedly measured
as evaporating. It was the last MECHANISM gap on the list.

## Observed: the premise reproduces

`observed-with-evidence`. On a fixture with three list entries and one 70,000-byte note field:

| measure | value |
|---|---|
| live file | 73,071 B |
| `ROLL_WATERMARK` | 65,536 B |
| over the watermark by | 7,535 B |
| `roll_for_atom(...)` | **0** |
| file size after a forced roll | 73,071 B (unchanged) |

`_roll` drains the list tenant, then finds no candidate: it moves whole entries, and a note is one
string. Past `MAX_FILE_BYTES` the write raises — the atom's record becomes literally unwritable —
and the message names the **file** bound, not the note, so the writer is handed no route out.

## The finding: the class had a second, larger member nobody was watching

`observed-with-evidence`. Measured across the live store — 297 atoms carry notes, mean tenant
1,595 B, p90 4,233 B — and one atom is already past the point of rescue:

| `OPS2_publish_gate_head_worktree` | |
|---|---|
| file | 62,301 B |
| note tenant | 60,906 B (**98% of the file**) |
| largest single note (`build_note`) | 56,846 B |
| live list entries | **0** |
| headroom to `ROLL_WATERMARK` | **3,235 B** |

The next paragraph appended to that note wedges the file, and the roll has *nothing whatever* to
drain. H27's owed item was filed as H27's risk. The class's largest member was one append from the
same wedge, on an atom nobody was looking at — the R10 shape, where the instance fix was never the
closure.

## Built

`NOTE_TENANT_MAX_BYTES` (32 KiB) + `note_tenant_bytes`, enforced in `set_note_for_atom` as a
**ratchet, not a cap**: a note write is refused only if it leaves the tenant over budget **and
larger than it found it**.

The direction is the whole design. A flat cap in `_write_tenants` would have refused every write to
an already-over atom — including appending to its register, which is the record-keeping the store
exists for — wedging the lane in the name of unwedging it, and locking the only remedy (writing a
smaller note) behind the bound that demands it. Under the ratchet: growth is impossible everywhere
at once; compaction is always available however far over budget an atom already is; every other
tenant of an over-budget atom writes exactly as before. The existing stock is therefore
monotonically non-increasing **without anyone editing another lane's narrative record**, which is
why this needed no exemption list.

The number is derived, not fitted, and the derivation is held as a test so it cannot be raised
without being re-checked: `_roll` reaches the watermark only by draining lists to one live entry
each, so the irreducible body is the note tenant plus one entry per list tenant — three tenants at
5.4 KB mean ≈ 16 KB, and half the watermark leaves 2×. Checked against reality afterwards: 296 of
297 live tenants already fit, and it is ~8× the p90.

## R15 — both ways

Source mutation on an **isolated copy**; the live module is imported by running daemons, so
mutating it in the shared tree is a hazard this project already has a rule about. Unmutated: green.

| mutation | verdict |
|---|---|
| control deleted | CAUGHT |
| WRONG SUBJECT — measure the field written, not the tenant | CAUGHT |
| FAIL-OPEN — bound loosened to the file cap | CAUGHT |
| FAIL-SILENT — measurement swallowed to 0 | CAUGHT |
| RATCHET INVERTED — refuse compaction instead of growth | CAUGHT |

The last one is the one that matters: it proves the *direction* is load-bearing rather than
incidental. The standing control `check_note_tenant_budget` is R15'd in-test both ways (fires on an
undeclared offender, and on a declared one that **grew**), reads each file with a plain yaml load
rather than through the store's own readers (a control that measures its subject through the code
under test is the tautology pattern), and carries a vacuity guard asserting that emptying the
declaration turns it RED naming OPS2 — so its pass on the live store is bought by the declaration,
not by the reader finding no data.

Verified against the real record, not only fixtures: on a copy of the live OPS2 file, appending one
sentence to `build_note` is REFUSED (60,906 → 60,935 B) and a compaction to 24,060 B is ACCEPTED,
with the live store file untouched at 62,301 B. 41 passed in the store module, 110 across
`tests/design/`.

## The declared debt

`OPS2_publish_gate_head_worktree` is declared in `_KNOWN_OVER_BUDGET_NOTE_TENANTS` at its measured
60,906 B. **Declared, not exempted** — the write-path ratchet makes it monotonically non-increasing,
and the control reds if it grows. The alternative was to compact that 56,846-byte `build_note` in
this commit, which is another lane's evidence trail; rewriting someone else's record to green my own
control is the laundering this store was built to refuse. **Owed to that lane:** compact it, and
lower the declared ceiling when you do.

## Refused, deliberately, so it is not read as an oversight

Item (B) asked for a size bound **and "an archive path of their own"**. The archive half was NOT
built. A note is a CURRENT statement whose history lives in git — the store's own contract, and what
Hour #33 relied on when it compacted H27's note — so a per-revision note archive would be a new
monotonic append-only flow growing once per Hour forever. That is exactly the class this store
exists to bound: building it would have made this the fourth drain that leaves a fifth flow running.
The bound alone closes the wedge; the archive would have re-opened it one level down. Reversible —
the constant and the declaration are two named symbols.

## Not claimed

- The level does **not** move. H27 stays at `level_current: 2`. Hour #31 pre-committed the promotion
  condition before #32 ran: a **fresh cold-eyes** Expert Hour ending with no BLOCKING finding. This
  was a targeted HARDEN build worked from the atom's own memory, so it is not that Hour, and a build
  pass cannot be its own confirmation.
- No figure this instrument computes moved (R12).

## Encountered in passing, not caused here

`inferred` as to cause, `observed-with-evidence` as to state:
`tests/tools/test_map_assertion_provenance.py::test_the_live_store_carries_no_stale_hold_record` is
RED, reporting that H27's register records Hour #36 while the latest Hour **answered** is #28, so
the hold record "hands the next promoter leads already taken". H27's store file is byte-identical to
HEAD and the failing checker reaches it only through readers (`for_atom`, `records_for_atom`,
`notes_for_atom`) that this tick did not change — so this is a HEAD-state red about record
*content*, discovered by this run rather than caused by it. Queued, not fixed on sight
(SELF_INTERRUPT_DISCIPLINE); it belongs to the record-content lane.
