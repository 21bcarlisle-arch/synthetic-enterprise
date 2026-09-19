**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, the
continuation store

# The embargo went on the item that READS the run, and the item that LAUNCHES it stayed drawable

**Filed:** 2026-09-18 · **Claim id:** `re-run-the-noise-floor-over-the-09-18-book-so-the-error-bar-stops-refusing`
**Subject:** `background/seat_continuation.py::undeclared_successors`, `background/delivery_lane.py::successor_note`
**Established against:** `4edfee275` (tree at the 16:43 draw)

---

## The finding in one line

The drawn item's work was **already in flight**, launched twenty-nine minutes earlier by a previous
invocation of this same claim id, and the draw handed the item out anyway with its text unchanged —
*"Re-run the noise floor over the 09-18 book **now**"*. Obeying it would have launched a second
sixteen-hour, twelve-seed run over the same seeds into the same output filename.

## The premise is SPENT, and the measurement that says so

The item cites `18327d977`; the premise check found it an ancestor of `origin/main` and told me to
re-measure. Re-measured:

| what | reading |
|---|---|
| systemd unit | `longjob-floor-next12-at-head-20260918` — **ActiveState=active** |
| liveness verdict | `python3 -m background.launch_liveness --check` → `RUNNING`, answered from the user manager, **outside the job's own cgroup** |
| pid / worktree | 3432960, cwd `/var/tmp/se-floorrun-head-20260918` (detached at `18327d977`) |
| seeds | 3100001–3100012, `--redraw-mode all --redraw-key elasticity` |
| output | `docs/observability/value_cycle_ab_s1_noise_floor_next12_at_18327d977.json`, in that worktree |
| launched / ETA | 16:13:03 local / ≈2026-09-19 08:20Z |

So I did **not** do the work. The correct disposition was `--release`, and this file is the "say so
in `docs/staging/`" half of it.

## How it became drawable, which is the part worth keeping

The sequence, all on 2026-09-18, all readable in
`docs/observability/.seat_continuation.json`:

1. **15:53** — `re-run-the-noise-floor-...` written as a continuation (the LAUNCHER).
2. **16:13** — a tick takes it and launches the twelve-seed floor as a detached systemd job.
3. **16:41** — that tick hands the remainder off as
   `publish-the-floor-at-18327d977-over-the-09-18-book-once-its-run-lands` (the READER), carrying a
   correct `DO NOT DRAW BEFORE 2026-09-19 09:30` stamp. Its `written_while_holding` names the
   launcher. Its `supersedes` is **`None`**.
4. **16:43** — the draw offers the LAUNCHER.

Nothing was broken. `hand_off(supersedes=...)` exists for precisely this, and **its own help text
predicts the consequence of omitting it** — *"live() offers oldest first, so the refuted entry is
drawn FIRST"*. The declaration was simply never made, so the launcher was never superseded, never
retired, and never stamped.

### The generalisable shape

**A long job splits its item into two texts, and the author's attention goes to the wrong one.**
The reader ("the run is in flight; read it when it lands") is the half whose timing is obviously
interesting, so it gets the embargo. The launcher ("re-run it now") is the half that is *expensive*
to obey twice, and it gets nothing. Guarding the reader and leaving the writer drawable is the
wrong way round.

`delivery_lane.claim_dispatched`'s docstring already records two earlier instances of a detached
multi-hour runner re-drawn inside its own shadow (a HadUK-Grid pull on 2026-09-05, a mutation
battery on 2026-09-06). **This is the third — and the first where the claim machinery worked as
designed and the continuation store leaked instead.** That is why the repair is in the continuation
store and not in the claim.

## What the draw could already have known, and did not read

`written_while_holding` is stamped at write time by `hand_off` from the delivery-lane claims the
authoring tick held. A successor naming `work_id` there was, by construction, written by the tick
doing `work_id`. The join existed in the record and **nothing had ever read it** — the same shape
as `expired()` spending a day reporting its only success as its defining failure.

## The repair

`seat_continuation.undeclared_successors(work_id)` answers: which LIVE continuations were written
by a tick holding `work_id` and do **not** declare they replace it. `delivery_lane.successor_note`
renders that for the doorbell, and `doorbell()` now concatenates it alongside `premise_note` and
`rival_note` — three stores, three questions: *has this already landed*, *is somebody else doing it
now*, and **did this item's own tick already do it and write down what was left**.

**It annotates and never refuses**, for `rival_note`'s reason exactly: a tick holding A may hand off
B as genuinely new work while A stays worth doing, and only the two texts side by side can tell that
from a continuation. Auto-superseding on this evidence would withhold live work silently — the
failure `embargoed_until` chose its own fail-open direction to avoid.

### It fires on the case that caused it

Run against the live store for the id I was drawn, before any repair to the store:

```
CONTINUATION CHECK (this item's own store, run at draw time): 1 live continuation(s) were written
BY A TICK HOLDING THIS ITEM and do not declare they replace it -- `publish-the-floor-at-18327d977-
over-the-09-18-book-once-its-run-lands` ("DO NOT DRAW BEFORE 2026-09-19 09:30 ... The 12-seed noise
floor at 18327d977 over the 09-18 book is IN FLIGHT: syst"). READ THE SUCCESSOR BEFORE YOU BUILD.
```

...and is silent when asked about the successor itself.

### The control can fail — three mutations, each on the leg that names it

`tests/background/test_a_long_jobs_launcher_is_named_at_the_draw_by_its_own_successor.py`, 6 passed:

| mutation | leg that reddened |
|---|---|
| drop `successor_note(item)` from `doorbell`'s concatenation | `test_the_DOORBELL_CARRIES_the_note_...` |
| drop the `written_while_holding` test | `test_work_that_merely_SHARED_A_TICK_...` |
| drop the `supersedes` test | `test_a_successor_that_DECLARES_...` **and** the partition control |

The partition leg (`test_BOTH_sides_of_the_partition_are_reachable_on_one_store`) is one control
over the whole partition rather than a leg per branch: a predicate answering "no" to everything
passes every silence leg above and is otherwise indistinguishable from the guard working.

**A defect in my own first draft, caught by running it rather than reading it.** The fixture stamped
`written_at` at 1970, which is outside `live()`'s window, so three legs were green because every
entry was *expired* — measuring expiry while claiming to measure supersession. Rebased onto
`time.time()`; the comment at the constant says why.

## Disposition

- The claim is **released**, not landed-under: the drawn item's own work was done by the previous
  invocation, and its remainder is under `publish-the-floor-at-18327d977-...` (embargoed to
  09-19 09:30).
- The launcher is **superseded by the successor** in the continuation store, which is what step 3
  should have done. `_superseded_ids` is "once superseded, always superseded", so the launcher
  cannot be re-offered by a later re-orientation while its own run is still going.
- **The run is untouched.** It is still `RUNNING` and still due ≈2026-09-19 08:20Z, and the
  decision rule for publishing its artefact was fixed before any seed was readable in
  `docs/staging/records/PREREG_THE_TWELVE_AT_HEAD_OVER_THE_09_18_BOOK_AND_WHAT_WOULD_MAKE_ME_NOT_PUBLISH_THEM_2026-09-18.md`.
  Nothing here touches that rule.

## What this does NOT fix

The note is advisory. A tick that reads *"a successor says the run is IN FLIGHT"* and re-runs it
anyway is not stopped by anything here. The refusal-shaped version would need to tell a
continuation from genuinely-new work, which this evidence cannot do — and a guard that withholds
live work on a guess is the failure mode the whole store is built to avoid. **The honest boundary
is: the draw now says it, and the tick still decides.**
