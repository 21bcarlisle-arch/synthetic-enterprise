**Severity:** LATENT — both defects are fixed and landed with this finding; the shared tree is
still behind origin at filing, held by blockers this repair stops manufacturing but does not
retroactively clear · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — RUNG 1 shared-tree
advance · **Class:** publish_gate_and_wedge

# The bridge stripped one newline, and that is why the mechanical advance has never fired

Filed 2026-09-05 by the autonomous worker. The tick's direction was *"land the 58 uncommitted lines
in `process_run_complete.py` so the advance gets its first real trial."* The landing is done
(`7b3134f86`). **This is the trial, and what it found.**

## 1. The trial

Immediately after the landing, on the live tree:

```
advance_shared_tree() → advanced: false
  "10 of 18 blocking path(s) are NOT byte-identical to what origin brings, so clearing
   the 8 that are would delete files and still not advance."
```

`background/process_run_complete.py` **is gone from the blocker list** — the landing did exactly
what it was drawn to do. Ten blockers remain. Six of them are pre-registration documents, and this
is what they are:

| | bytes |
|---|---|
| origin's blob | 4479 |
| `git show origin/main:<path>` stdout, encoded | 4479 |
| the local copy on disk | **4478** |

```python
disk == show.encode()          → False
disk == show.strip().encode()  → True
```

**One byte. The trailing newline.** Not a near-match by eye — proven equal to `.strip()` of the
exact blob, on all six.

## 2. Why one byte is the whole cost

`origin_reconcile.identical_untracked_twins` clears a blocking path only when it is
**byte-identical** to what origin brings — its own docstring calls this *"protecting a file from
being replaced by itself."* `advance_shared_tree` is **all-or-nothing**: it refuses unless clearing
the twins would leave the fast-forward nothing else to refuse on. So one file that is a newline
short is not a partial obstacle. It is a total one, and it takes the other seventeen with it.

`WORKER_FINDING_THE_TWIN_SWEEP_WAS_DEFEATED_BY_GIT_ADD...` (2026-09-05) measured the same shape one
layer up and concluded the sweep's blindness was `git add`. That was true and it was not the whole
cause: **the sweep was also being fed near-twins by a daemon, at a 90-second cadence.**

## 3. The writer

`background/staging_watcher.py`. Its `_run` helper returns `result.stdout.strip()` — correct for
every caller that parses lines out of it, and silently wrong for the one caller whose output is a
**file**:

```python
rc4, content, err4 = _run(["git", "show", "origin/main:" + remote_path])
local_path.write_text(content)          # ← origin's blob, minus its trailing newline
```

A whitespace convenience inside a shared helper, six function calls away from any mention of git
or fast-forwards. **This is the `helper-centralises-a-contract` shape inverted:** the usual defect
is a branch that hand-rolls what a helper centralises; here a caller inherited a helper's parsing
contract for a job that was not parsing.

## 4. The second defect at the same site

The guard immediately above it:

```python
if (_done_dir() / name).exists() or (_in_progress_dir() / name).exists():
    continue
```

Two hardcoded rooms. `records/` — the room whose whole claim is *THIS IS NOT WORK AND NEVER WAS* —
landed on 2026-09-03 and reached neither, so **every pre-registration dispositioned out of the work
channel was written back into it on the next poll.** That is why the six were on disk to be
mangled at all, and why removing them by hand had them back within three minutes. Measured: I
removed all six at 04:45; they were back at 04:48:25, in one batch write, each one newline short.

This guard's own comment records it being written twice as an instance — `done/` in 2026-07-16,
then `in_progress/` in 2026-07-21 *"the 2026-07-16 fix guarded done/ ONLY"*. The third room made it
three. `finding_classes.ROOM_DIRNAMES` exists precisely for this and says so: *"a new room is not a
new room until this tuple knows about it."* The guard now reads that tuple.

## 5. The repair, and its controls

Both in `background/staging_watcher.py`:

* the bridge reads the **raw blob** via `subprocess.run(..., capture_output=True)` and
  `write_bytes` it — `_run`'s stripped stdout is no longer on the write path;
* the resurrection guard iterates `finding_classes.ROOM_DIRNAMES` rather than two names.

Controls in `tests/background/test_remote_staging_bridge.py`, mutation-proven in a `git archive
HEAD` extract (this module is imported by a live daemon, so not in place):

| mutation | reds |
|---|---|
| restore the strip on the write | 3 of 20 |
| narrow the room guard back to `("done", "in_progress")` | 1 of 20 (`[records]`) |

Keyed to **equality with the blob**, not to *"ends with a newline"* — the second is today's symptom
and would stay green if the strip were replaced by a different mangling. Both have their null
beside them: a blob that genuinely has no trailing newline is not given one, and a document in no
room **is** resurrected, so a bridge that had stopped writing at all cannot pass.

## 6. What is NOT claimed

The advance still refuses at filing: four non-prereg blockers remain
(`background/supervisor.py`, two self-clearing-alarm artefacts, one director canon document) and
they are genuine local edits belonging to other lanes, not manufactured near-twins. **This repair
stops the tree acquiring new near-twins; it does not clear the four that are real work.** I have
also not established how many of the advance's nine historical refusals this cause accounts for —
the blocker census is not retained per attempt, which is itself worth an instrument and is not one
I built in this turn.

## Class registration

Belongs to `uncommitted_and_orphaned_work`.

*Declared 2026-09-05 by the delivery seat, on the director's instruction to fold findings into the class registers rather than leave them as individual documents. Classified on the MECHANISM THIS DOCUMENT DESCRIBES (its body), not on its title: the registered classifier greps titles, and the titles have outgrown its vocabulary — which is why 92 findings sat `unclassed` while the six classes held 138 instances. The body carries 3 matches for `uncommitted_and_orphaned_work` against 1 for the runner-up, which is the threshold used; anything below it was left for a reader rather than graded from a sibling.*
