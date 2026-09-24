**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# PRE-REGISTRATION — recovering `--staged-too`, orphaned by the base-wins enactment

LATENT and not BLOCKING: a landed refusal with no exit, whose only implementation is in a git ref
nothing points at. It invalidates no published figure and no control's verdict — the STAGED refusal
is *correct*, it simply has no door — so nothing already claimed is wrong. What it costs is a
capability that silently ceased to exist, which no control in the tree can notice.

**Written 2026-09-24, BEFORE the measurement below was run.** Item:
`enact-the-four-path-base-wins-decision-on-the-shared-tree`.

---

## What was already true when this was written (measured, not predicted)

The item's headline ask is **SPENT**. All four contested shared-tree working copies were preserved
and the base-wins enactment written over them, by another lane, at 19:42 today:

* `refs/preserved/base-wins-four-2026-09-24` = `92b6629dc`, committed 19:42:14, parent
  `63356067f`. Its message names all four paths and says "before the base-wins enactment".
* The four working copies were rewritten at 19:42:26 — twelve seconds later — and now read
  `disk == index == shared HEAD` on every one. The 15:02:31 stash-pop mtime the item cites is gone.

So the enactment is not owed. What the item ALSO asked for, and what is still owed, is this:

> *"Those two need the hunks read against 777c4adb8/c72c41e4c by hand and either dropped or
> re-authored on the current base."*

That hand-read had not been done. `--base-wins` discarded the copies wholesale into the ref.

## The gap that read created

Reading the preserved hunks against the current base (`62abd5e49`, = `origin/main` tip) splits them
cleanly in two:

**(a) Revert-shaped — the older draft of a restructure already in. Correctly dropped.**
The preserved copy *deletes* `_clock_disclosure` (landed `95ec3faa3`), *deletes* the
`unread_populations` "no complaint names what it read" branch (rule 1b, `777c4adb8`), reverts
`_probe` to its pre-repair signature (repaired by `62abd5e49`), and collapses the
`noqa: PLC0414` re-export blocks `777c4adb8` deliberately created. Landing any of it reverts
those four commits. The item was right about this half.

**(b) A genuinely novel feature, superseded by nothing, reachable from no commit.** `--staged-too`:
`STAGED_DISAGREES`, `_index_bytes`, the STAGED-branch relaxation, `_clear_index_entry`, the write-side
index clear, and the CLI flag — plus **seven** tests.

Measured on the trunk:

* `git grep staged_too\|staged-too origin/main` → **zero matches in any code or test file.** The
  only four matches anywhere are prose mentions inside staging documents.
* `origin/main:tools/refresh_to_head.py` still carries `STAGED = "refused_holder_has_it_staged"`,
  referenced in exactly **three** places: the constant, and the one refusal that returns it.
  **Nothing relaxes it.** It is a terminal refusal.
* Exactly one test asserts the refusal fires. None asserts it can be escaped — because it cannot.

**That is a refusal with no exit, and the repo's own rule says so:** *"A refusal with no exit is a
wedge."* No other door reaches an index entry — `isolate_hunks` separates by author not by age, and
`surgical_land --content` would land the revert. The shared tree has staged entries right now
(`docs/direction/DIRECTION.yaml`, `docs/direction/decisions.jsonl`), so the state is live, not
hypothetical.

---

## THE PREDICTIONS — filed before running

**P1.** All six feature pieces re-author onto `62abd5e49` with no semantic conflict against the four
landed commits, because none of those four touches the `if path in staged:` branch.
*Confidence: high.*

**P2.** Of the seven recovered tests, **five to seven pass unmodified** once the feature is in.
*Confidence: moderate — this is the one I expect to be wrong if any is.*

**P3 — the named risk, and what I expect the cause to be.** If a test fails, I predict it is
`test_the_staged_partition_stays_three_distinct_answers` (which expects a staged `RIVAL_KIND_A`
with the flag on to grade `REFRESHABLE`) or
`test_staged_too_clears_the_index_entry_as_well_as_the_working_copy`, and that **the cause is a
MOVED FIXTURE GRADE, not a defect in the recovered feature** — rule 1b and `_clock_disclosure` both
landed after these tests were written, and both can change what a rival copy grades. A fixture
whose grade moved is a test to re-author, not a feature to abandon.

**P4.** The existing `test_a_path_the_holder_has_staged_is_refused` stays green, because it asserts
`verdict.state == rth.STAGED` and not the refusal's text — and the recovered feature keeps that
state for the default (flag-off) case.

**What would refute the whole recovery:** the feature turning out to be reachable on the trunk under
another name (P-zero: refuted above, zero code matches), or `--staged-too` proving to require any
part of half (a) to work. Either one and the right answer is to drop it and file the gap instead.

**Falsifiable either way:** the result is recorded beside these predictions in the RESULT note, in
whichever direction it came out.
