**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
claim `close-the-fork-that-has-refused-eleven-publishes`

# The advance held on a question nobody had asked, and the two paths left are both judgements

*The drawn item's premise was spent: the fork it names was closed at origin yesterday (`995fd0d85`,
`6a9f49cf9`) and this checkout reads **0 ahead / 14 behind**, which is not a fork. What is still
live is the item's last clause — `episode_clean_publishes` is still **0** — and that is held by the
shared tree's advance. Of the eleven paths holding the fast-forward, **six were refused by a
sentence about the reader rather than about the file**, and one of those six was holding the other
ten hostage. That is repaired. The **two** paths left are both genuine judgements, and neither was
this tick's to force.*

---

## 1. The premise, re-measured before anything was built

The doorbell says "8 ahead / 7 behind" and eleven `behind_origin` refusals. Measured at draw time:

| the item's ask | state | evidence |
|---|---|---|
| fix the guard refusing the merge on a false reading | **DONE** 2026-09-20 | `995fd0d85` |
| close the fork / merge | **DONE** | `6a9f49cf9`; `origin/main...HEAD` = 0 ahead / 14 behind |
| confirm a publish cycle lands | **NOT DONE** | `episode_clean_publishes: 0`, `episode_failures: 12` |

So one clause of four survived, and the doorbell's own ahead/behind figures were stale in both
directions. The prior tick's `WORKER_RESULT_THE_FORK_IS_CLOSED_AT_ORIGIN_...` §3 named the
remaining blocker as two paths; both are still there, and **the reason one of them was unanswerable
was not a property of that path at all.**

## 2. The defect, and it is the 2026-09-18 class one door over

`advance_shared_tree` asks five classes of every blocker. The third —
`refresh_to_head.judge_copy`, the losslessness judgement — answered **six of eleven** paths:

> *"this control has no reader for `.json` files, so it CANNOT establish that the copy has nothing
> to lose. An unavailable check is a failed check."*

Fail-closed and correct. It is also **permanently unresolvable**, and that is the whole finding: the
sentence is about the READER, not the file, so no producer run, no landing by any lane and no
passage of time can ever turn it into a verdict. Under the all-or-nothing rule — a safety property,
not tidiness — one permanently unresolvable path refuses every class beside it.

Five of the six were rescued, and only by accident of scope: `generated_output_verdicts`, the fifth
class added 2026-09-18 for **exactly this shape**, happened to know their producer. Its own fixture
left the gap in writing — *"a path the oracles do not know is authored work and stays refused"* —
and the sixth path, `docs/design/self_clearing_alarm_dispositions.json`, is authored. No producer
knows it, so it held the tree on a question nobody had asked.

**Repaired:** `symbols()` gains a JSON reader (`DATA_SUFFIXES`), consumed by the advance's door
only. Re-measured on the live tree afterwards, all five remaining `.json` blockers **still refuse**
— correctly; each really does supply leaves origin lacks — but with a reason that names the leaves
instead of naming the reader's absence.

**The leaf name carries a digest of its VALUE, and that is the design, not a detail.** Keyed on the
key-path alone — the obvious reading — a copy that rewrote values while keeping the shape supplies
no name the base lacks and reads as strictly superseded. Mutation-measured on the live shape (stale
**and** edited, which is this very blocker's diff): verdict `refreshable`, rc 0, **the unlanded edit
destroyed**. That leg is `test_a_stale_copy_carrying_a_rewritten_value_does_not_lose_the_rewrite`,
and it is the only leg here that proves data loss rather than a wrong label.

**The commit guard is deliberately unchanged.** `violations()`/`judge()` gate on `READABLE` and run
on every commit in a tree three lanes write, where a daemon rewriting a `.json` ledger between two
commits is ordinary operation. Widening that set reds every lane for a carrier's normal churn —
a class this project has already banked. `test_the_commit_guards_readable_set_did_not_widen` is the
leg that fails if a later hand "tidies" the two constants into one, and **nothing else would notice:
every verdict leg would stay green.**

One sibling leg went red and it was asserting the lie: `test_stale_copy_refusal.py`'s vacuity
control used `.json` as its example of an unreadable suffix. Its example moved to `.csv`; its
`.json` assertion became the one that now matters — an empty document must still not be the empty
set, or the vacuity it forbids walks back in through the new reader.

## 3. WHAT IS NOT DONE, and why neither was this tick's to force

Both remaining paths are judgements, and this is recorded as unmet rather than worked around.

* **`background/process_run_complete.py`** — verdict REPLACEMENT: *"supplies 1 name origin lacks,
  and EVERY hunk carrying one also deletes a name origin has"*. The name is
  `EARLY_EXIT_CEILING_SECONDS_2026_09_17`, and **`git log -S` over `origin/main` finds it nowhere**
  — it exists only in this working copy. Origin meanwhile landed `bfbc2b4e9`, *"one constant was
  setting an early-exit discriminator and a growing regime figure, and those pull opposite ways"*,
  which introduced `REAL_CHAIN_FLOOR_SECONDS_2026_09_17`. So this is two lanes splitting the same
  conflated constant and naming the halves differently — *two implementations of one property*,
  which the verdict correctly says neither door may decide. **And the file was EXECUTING while this
  was written** (PID 48010, the publisher itself, started 12:30 on `run_complete_20260921T110603Z`).
  Forcing it would have destroyed an unlanded constant out from under a running publisher.
* **`docs/design/self_clearing_alarm_dispositions.json`** — measured leaf by leaf against origin,
  and the working copy is **strictly worse than what it would replace**. It supplies 7 leaves, of
  which the only content on no ref anywhere is a `.standing_red.json` disposition row; **that row
  names `background/standing_red.py`, and no such module exists in this tree.** The census agrees
  from the other side — *".standing_red.json — dispositioned, but the census no longer resolves the
  path at all"*. Beside that, the copy **deletes** the `.publish_landing_in_flight.json` row origin
  carries, which the census reports twice over as `UNDISPOSITIONED HITS` and as a row *"removed
  from the register without a reason"*. The remaining 2 leaves are a rival draft of a row origin
  graded and landed at `76e74f854`.

  The honest disposition is therefore **preserve-and-restore**, not land: its unique content is a
  row for a module that is not here. That is a deliberate write over another lane's bytes and is
  left for a tick that is not also holding a gate run.

## 4. My own prediction, refuted, kept beside the result

Written before §3 was measured: *P1 — the dispositions copy is 5 days stranded, so its unique
content is recoverable authored work and landing it clears the path.* **Refuted.** The unique
content is a disposition row for a module that does not exist, and landing it would have published
a claim about `background/standing_red.py` — which I only asked for after writing the prediction
down. The 5-day mtime was evidence of stranding and I read it as evidence of *value*, which it is
not.

## 5. Owed

* The REPLACEMENT judgement on `process_run_complete.py`: decide which half of the split constant
  survives, land the winner, and do it when the publisher is not mid-run.
* The preserve-and-restore of the dispositions register, with the `.publish_landing_in_flight.json`
  row restored — or `_retired[...]` naming what took the subject out of the tree, which is what the
  census's own refusal asks for.
* `episode_clean_publishes` is still 0 and **the claim's stated `done` remains unmet**. What
  changed is that the reason is no longer a control refusing on a question it could never answer.
