# [WORKER-FINDING] The only legal landing move leaks 150MB every time it is killed, and it refuses itself at 500MB (2026-08-14)

**Severity:** BLOCKING · **Lane:** H_harness · **Status:** measured, and the leaked space reclaimed;
the leak itself is NOT repaired — filed per `SELF_INTERRUPT_DISCIPLINE` (this tick's draw was the
D37..D45 mint).

Found by tripping over it, not looked for: a `tools.surgical_land` run was killed at a 10-minute
harness timeout against a gate that takes ~9m24s, and the next thing anyone would have measured is
why the tool refused.

## What was on disk, `observed-with-evidence`

    $ du -sh /tmp/surgical-land-* | wc -l        ->  24  (before this tick's own kill made 25)
    $ du -sh /tmp/surgical-land-* | head -1      ->  152M
    $ df -h /tmp                                  ->  7.8G total, 6.7G used, 1.2G free, 86%
    $ ps aux | grep [s]urgical_land               ->  (nothing)

Twenty-four abandoned extracts, ~150MB each, ~3.6GB total, timestamped `08-12 23:55` through
`08-14 06:18` — a day and a half of accumulation. **No live process held any of them.** After
removal: `7.8G total, 3.0G used, 4.9G free, 38%`.

`/tmp` on this box is a **tmpfs** (`reference_the_box_has_15g_ram_and_tmp_is_a_tmpfs`), so this is
not idle disk — it is 3.6GB of the 15GB the suite runs in.

## Why it happens, `observed-with-evidence` in the source

`tools/surgical_land.py:467` makes the extract with `tempfile.mkdtemp(prefix="surgical-land-")` and
removes it in a `finally:` at `:477-478`. There is **no `signal` handler and no `atexit`** in the
file (`grep -n "signal\|atexit" tools/surgical_land.py` → empty). A `finally:` runs for exceptions;
it does not run for `SIGTERM` or `SIGKILL`. So **every abnormally-terminated run leaks its whole
extract**, and abnormal termination is the *routine* case here: the gate runs ~9m24s and any caller
with a 10-minute bound kills it.

## Why this is BLOCKING rather than housekeeping

The tool refuses itself on exactly this resource, and fail-closed is correct:

    tools/surgical_land.py:119   MIN_FREE_MB = 500
    tools/surgical_land.py:265   if free is not None and free < MIN_FREE_MB:
                                     "REFUSED on DISK, not on code: {}MB free where the extract
                                      needs ~{}MB, so the gate could not have run"

At 1.2GB free, **four more killed runs** (~600MB) crosses that line. `surgical_land` is not one tool
among several: `DIRECTOR_RULING_HOOK_BYPASS_IS_A_WALL_2026-08-09` made hook bypass a WALL and made
this the *only legal move* for landing a pathspec against a dirty shared index — which is this
tree's normal state. So the failure mode is: **the repo-wide landing path refuses every lane, for a
reason that is not in any repo, and the refusal is louder about disk than about the leak that ate
it.** Nothing sweeps `/tmp`, nothing measures it, and the leak is invisible to every check that
walks the working tree.

There is an irony worth keeping, because it is the general lesson. The module's own docstring
explains why it does not use `git worktree add`: *"it registers state in the real repo that survives
a SIGKILL."* It avoided repo-visible state that outlives a kill and replaced it with **tmpfs state
that outlives a kill in a place nothing looks** — the same defect relocated to where no control can
see it. Moving a leak out of the audited surface is not removing it.

## What is owed, and it is small

1. An `atexit` + `SIGTERM`/`SIGINT` handler around the extract, so the routine kill cleans up. Not
   sufficient alone (`SIGKILL` takes no handler), which is why (2) is not optional.
2. A **sweep of stale `surgical-land-*` extracts at startup** — any prefixed directory with no live
   holder is by definition abandoned, since the tool creates one per run and removes it on success.
   That is the half `SIGKILL` needs, and it is the half that would have kept this tick's own kill
   from being the 25th.
3. R15 both ways: a mutation that removes the sweep must leave a planted stale extract standing, and
   an extract belonging to a **live** run must survive the sweep — the fail-dangerous direction, a
   sweep that deletes the tree a concurrent lane is being gated in.
4. The free-space refusal should say what it found (`N stale extracts, M MB`), because a refusal
   that names only the symptom sent this tick looking at the wrong thing first.

**Not taken here:** it is a change to the landing tool itself, and a landing tool cannot safely be
edited by the tick that is mid-landing through it.
