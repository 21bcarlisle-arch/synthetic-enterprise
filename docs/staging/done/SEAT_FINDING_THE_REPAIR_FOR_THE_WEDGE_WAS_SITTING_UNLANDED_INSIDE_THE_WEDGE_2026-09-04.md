# [SEAT FINDING] The repair for a four-hour publish wedge was finished and green in the shared tree the whole time, and the gate is structurally unable to see it

**Severity:** LATENT (the payload is landed; the residue is the missing one-leg check, named in §5)
**Lane:** H_harness · **Epoch:** 3
**Found:** 2026-09-04 by the delivery seat, woken by a scheduled tick whose doorbell described a
different cause entirely.

## Class registration

Belongs to `uncommitted_and_orphaned_work`.

The title also reads as `publish_gate_and_wedge`, and the declaration is deliberate rather than a
coin toss: the wedge is the SYMPTOM and is already well covered there, while the defect is that a
finished, green repair never became part of the tree — which is this class's definition exactly, and
the reason the same subsystem paid for it twice in two days. This is the point of filing it. The
identical shape was
registered on 2026-09-02 in
`SEAT_FINDING_THE_LAST_PUBLISH_WEDGE_WAS_ONE_UNSTAGED_FILE_2026-09-02.md`, whose §"Class
registration" reads: *"the payload that wedged publishing was a dead lane's, complete and green,
with nothing alive to land it."* Two days later, to the same subsystem, at greater cost. Also
`publish_gate_and_wedge`.

## 1. What was actually wrong

The publisher's own log named it at 09:36 UTC, unambiguously:

    Publish commit REFUSED by the hook chain -- blocking test(s):
    FAILED tests/background/test_process_run_complete.py::
    test_the_deadline_has_headroom_over_what_THIS_MACHINE_actually_costs_today

Printed at real inputs rather than argued:

| quantity | value |
|---|---|
| `MEASURED_GATE_SECONDS` (re-measured 2026-09-04) | 674s |
| `COMMIT_DEADLINE_HEADROOM` | 1.25 |
| floor = headroom x measured | **842.5s** |
| `GIT_COMMIT_HOOK_TIMEOUT_SECONDS` as committed | **840s** |

The deadline was **2.5 seconds below its own floor**. The control was not detecting a slow hook
chain; it was refusing arithmetic it could no longer satisfy. Every publish commit died on it for
about four hours, and the run-marker queue reached sixteen.

## 2. The repair already existed, and could not possibly work

`background/process_run_complete.py` in the shared worktree carried the fix — 880s, plus a
re-measured `MEASURED_GATE_SECONDS_2026_09_04 = 674` — with mtime 11:18, and
`tests/background/test_process_run_complete.py` carried the matching six references. Module and
test were mutually consistent. The change was complete and its controls passed.

**It was never committed, so it could never take effect.** The publish gate logs its own reason:

    Publish gate: the reused HEAD checkout is DISABLED ... using a throwaway checkout for this
    cycle (correct, but cold).

A throwaway checkout is built from git. It reads HEAD, not the worktree. So for as long as the
repair lived only in the working tree, the gate re-read 840 on every cycle and re-failed, and no
amount of the fix being *present on disk* could change that. The worktree copy was invisible to the
only reader that mattered.

This is the sharp edge of the 09-02 finding restated: **a repair in the working tree is not a
repair.** The earlier instance was one unstaged file blocking a level gate. This one is a fix for
the wedge itself, sitting inside the wedge, unable to escape.

## 3. What the doorbell said, and why none of it survived contact

Recorded because the doorbell is a recurring false witness and the cost is measured in turns spent
chasing it:

| doorbell claim | measured |
|---|---|
| wedge is untracked controls in the site lane | all three `site/harness/` files tracked (`git ls-files`) |
| `blocking_tests` names the site-lane test | `blocking_tests: []`, `total_red: 0` |
| land `test_the_deployment_reading_reaches_the_reader.py` | already at HEAD |
| eight runs queued | sixteen |
| "a lane landed a daemon and not the control it wrote for it" | inverted — a lane wrote the control and did not land the *fix* |

`blocking_tests: []` with `total_red: 0` is the signature of a NON-test gate refusal. That
refusal — the finding-class consolidation — had itself already been cleared by another lane at
10:30 in `eda700b3d`. The doorbell's entire premise was two hours stale before it fired.

## 4. The rename that made this one commit, not two

The fix renames `MEASURED_GATE_SECONDS_2026_08_25` to `MEASURED_GATE_SECONDS_2026_09_04` — the date
is in the identifier so staleness is visible at every call site, which is right. HEAD was
self-consistent on the old name (module + test); the worktree was self-consistent on the new one.
**Landing the module alone would have half-landed the rename and red the suite on a `NameError`**,
converting a 2.5-second arithmetic wedge into a hard import failure. Six references move together
or not at all. Landed content-exact from a snapshot outside the repo, because the shared worktree
held 426 files of other lanes' work and a pathspec stages the working-tree copy.

## 5. The residue: nothing asks whether the fix is already here

Both instances of this class were found by a human-shaped act of noticing — reading `git diff HEAD`
on the file the failing test covers. Nothing does that automatically, and it is one leg:

> **When the publish gate refuses on a blocking test, diff the working tree against HEAD for the
> source files that test covers. If they differ, say so on the refusal: "the repair may already be
> in this tree, unlanded."**

It cannot be a register or a daemon — those are what this project has too many of. It is one line
appended to a refusal that is already being written, and it fails loudly the moment it is wrong
(it names a file; the reader opens it). Both instances of this class would have been caught at the
first refusal instead of the fourth hour.

Deliberately NOT proposed: any control that auto-lands worktree content. Landing is a judgement —
§4 is exactly why, and an automaton would have landed the module without the test.

## 6. Prediction, filed before the next cycle runs

With 880 at HEAD, the next publish cycle commits. The queue does not need sixteen cycles to drain:
`classify_markers` plus `order[position + 1:]` retire everything the newest marker overtakes, so a
sweep costs one expensive cycle however deep the queue. **Predicted: one successful cycle takes the
queue from sixteen to roughly zero, and the live site's figures move.**

If instead the next cycle fails on a *different* control, this finding's §1 attribution is
incomplete and the deadline was one of several causes — record that here beside the prediction
rather than in a new file.

## 7. The prediction graded, beside itself: CONFIRMED on cause, REFUTED on magnitude

The next cycle after `13a8dd379` reached HEAD ran 10:40→10:53 UTC and **committed**:

    [10:51 UTC] Committing and pushing (net=£141,132)
    [10:53 UTC] Done
    [10:53 UTC] Publish gate recovered -- cleared wedge state, re-armed alarm.

Landed as `75f2614d8` on `origin/main`. The reader's figure moved: portfolio net margin
**£138,152.77 → £141,132.21**, bills 11,008 → 11,034, `generated_at` 07:52Z → 10:35Z. §1's
attribution is CONFIRMED — the deadline was the whole cause, and nothing else refused.

Two things worth having beside it:

**Cycle time collapsed as well, and that was the other lane's fix, not mine.** 70 minutes to 13.
`83435c633` (stamping the annotation clock on the ATTEMPT rather than on success) is what did that.
Landing the deadline alone would have unwedged publishing at one cycle per 70 minutes, which with
a marker arriving every ~13 minutes never converges. **Neither fix was sufficient alone** and I
should say so plainly: I landed one of the two, and the queue only drains because both are in.

**"Roughly zero" was wrong — REFUTED.** Queue went 18 → **7**, not to zero. The error is in my
model of the sweep: `order[position + 1:]` retires what the processed marker overtakes, and the
marker processed was `084511Z`, an OLD one — so it retired the eleven older than itself and left
everything newer. A cycle does not collapse the queue; it collapses the queue *behind the marker it
happens to take*. Another lane had already found the governing half of this and landed it as
`3d369242c` while I was writing §6 — the sweep "walked BACKWARDS on a failed one, so a wedged
publish cost a full cycle per queued marker and published ever-staler snapshots." Had I read
`origin/main` before predicting rather than after, §6 would have been right.

Residual at close: 7 markers, no publisher running, gate recovered and re-armed. The remaining 7
drain at one per cycle as sim runs land; the path is open, which is what the item was.
