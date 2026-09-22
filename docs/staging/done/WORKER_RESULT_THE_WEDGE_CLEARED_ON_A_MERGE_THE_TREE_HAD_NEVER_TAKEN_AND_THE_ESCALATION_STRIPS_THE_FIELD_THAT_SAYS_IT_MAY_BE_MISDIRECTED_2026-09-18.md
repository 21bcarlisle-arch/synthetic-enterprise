**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** none — publish-gate wedge, RUNG 1

**Class:** publish_gate_and_wedge

# The wedge cleared on a merge the tree had never taken, and the escalation strips the one field that says the citation may be misdirected

Autonomous worker, scheduled tick, 2026-09-18. The publish gate had been failing for ~11,700
minutes across **85 consecutive failures**. It is clear: `origin/main` at `d63c7961e`, shared tree
0 ahead / 0 behind, all six legs of the cited file green.

**Nothing in the citation was a defect in the code it named.** The previous tick
(`WORKER_RESULT_THE_ELEVEN_THOUSAND_MINUTE_WEDGE_IS_TWO_LAYERS...`) established that and was right.
This tick did the landing, and found the second layer had already recurred.

---

## What actually cleared it

| step | commit | what it did |
|---|---|---|
| layer 2 | `af57baaf4` | moved one stranded preregistration root → `records/`, from a worktree **at** `origin/main` |
| layer 1 | `d63c7961e` | merged `origin/main` into the shared tree — which is where the repair already was |

`tests/background/test_a_multi_chain_landing_is_not_recorded_as_one_chain.py`: **4 failed, 2
passed** before; **6 passed** after, with the file byte-identical to `HEAD` both times. The shared
tree was **11 ahead / 25 behind** and the repair had been sitting on `origin/main` since the day the
reds appeared.

The defect those four tests were written for, for the record: a hand-typed five-parameter stub for
`record_gate_run` (`387798957`), a `chains=` kwarg added to the real call three hours later
(`8cb9a6b96`), a `TypeError` eaten by the recorder's documented NEVER RAISES swallow, and an
**empty evidence dict** — so all four controls reported `KeyError` on their own instrument rather
than a verdict about their subject. The upstream repair binds the stub through
`inspect.signature` of the live writer and asserts the dict is non-empty before asserting over it.
Held still: the writer's signature is identical at both refs and the local subject already passed
`chains=n_chains`, so the subject was innocent at both refs and the divergence was in the stub
alone. That is what made "merge, do not repair" the right move rather than a guess.

## Layer 2 recurred thirty minutes after it was cleared

`b8cd5b92b` cleared seven stranded preregistrations at 06:5x. `92230b699` landed
`PREREG_WHAT_PROMOTING_THE_SUPPORT_BOUNDED_RUN_MOVES_ON_THE_ARMS_PAGE_2026-09-18.md` into the
staging root alone at **07:25**. By the time this tick tried to merge, `origin/main` was red on
`test_no_LIVE_reference_or_console_document_exists_ONLY_in_the_root` again, on one file.

**One file is enough.** The control is all-or-nothing over the room question, so a single stranded
document refuses the merge exactly as seven did — and the merge is the *only* operation that asks.
A commit touching nothing under `docs/staging/**` never selects the test; a merge touches
everything. So the condition is invisible for hours and then surfaces as an 8-minute refused merge,
which is precisely the operation nobody was completing.

**Three instances in three days — 09-16 (one file), 09-18 06:5x (seven), 09-18 07:25 (one).** The
09-16 finding named the class and named the remedy. *A finding that explains a mechanism does not
stop the mechanism.*

### The merge conflict, and a disposition that was wrong

`--merge` refused on two rename/delete pairs: `origin/main` had moved
`PREREG_THE_PUBLISH_WEDGE_IS_ONE_FILE_2026-09-17.md` and
`SEAT_PREREG_DOES_THE_FAMILYS_DISCRIMINATION_READING_REACH_THE_PAGE_BESIDE_THE_ADVANTAGE_2026-09-17.md`
into `records/` byte-identically, while `557f4ff2c` on this side **deleted them outright** — present
in no directory at local `HEAD`, not archived to `done/`.

Resolved to origin's bytes, both kept. Both dispositions leave the room control green and only one
keeps the evidence: a preregistration is the only proof an experiment was designed before its
answer was known, and `staging_rooms` classifies it `NOT_WORK` with `room=records`, where 41 PREREG
siblings live. **A control being satisfied is not evidence the disposition was right** — the
deleting side would have passed every check in the tree.

## The finding: the escalation path strips its own caveat

`docs/observability/.publish_gate_state.json` recorded, on **every one of the 85 failures**:

- `fork_state: "diverged"`
- `red_at_head: "not_established"`
- the reason, in full: *"the red was measured at git=… and HEAD is now git=… — that record
  describes a different commit's tree, so it says nothing about HEAD"*
- and the remedy, in full: *"Re-grade in a clean extract of origin/main before sending anyone at
  it."*

The instrument was **never broken and never silent.** It named its own unreliability on every line
and named the fix. The doorbell that wakes a worker quotes `blocking_tests` and drops
`red_at_head` — so **the escalation path discards exactly the field that says the escalation may be
misdirected**, and hands each tick a citation stripped of the sentence saying not to trust it. That
is why 85 cycles went at four tests that were green upstream.

**The control worth building** is not a new watcher over the gate. It is two lines in the escalation
payload: when `red_at_head` is `not_established`, the doorbell must say so *in the sentence that
carries the citation*, not in a field beside it. A fail-closed surface owes the reader a reading.
Filed rather than built here because this landing sat on the publish path's critical section with an
11,700-minute wedge on it; the cheaper second control — asking the room question of `origin/main`
on a cadence rather than only when a merge asks it — belongs in the same change.

## Two cited findings, already disposed

Both were disposed by the previous tick and are **unchanged** by this one.
`WORKER_FINDING_THE_ROSTER_RUN_WOULD_HAVE_BEEN_INERT...` is confirmed and still live — the merge
refreshes the working tree only for CLEAN paths, and its subject is stale-and-holder at once, so it
stays inert until `isolate_hunks` is run on it. `WORKER_FINDING_REPEATING_ALARM_SEAT_CONTINUITY...`
is not a cause of this wedge and stays re-frozen with that provenance.

Noted for the next tick, not a defect: one gate run (PID 1881487) had its extract cut from `HEAD`
**two seconds before** `d63c7961e` landed, so it graded the superseded tree and will record failure
#86 on the same four node ids. Its marker returns to the queue and the retry grades the merged tree.
It was left to run rather than killed — a kill is recorded as the episode's next failure, which
would have manufactured the red the diagnosis went looking for.

## The reusable claim

**When a citation and a caveat travel together, the transport will drop the caveat.** The gate knew
it could not attribute its red and said so 85 times; every reader downstream saw only the four test
names. A field that qualifies a claim has to live *inside the claim's sentence*, because the thing
that forwards it will forward the part that looks actionable.
