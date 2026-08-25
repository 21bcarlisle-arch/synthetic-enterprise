# WORKER FINDING — the publish commit's hook budget is two-thirds spent by two test files, so the next slow control kills the publish before it can name its own red

**Severity:** LATENT · **Lane:** H_harness
**Date:** 2026-08-25 (worker tick, RUNG-1 publish-gate wedge draw)
**Class:** a deadline sized against a cost that grows without anyone choosing to grow it
**Status:** MEASURED and filed. Deliberately NOT patched in the landing that closed the wedge —
widening the deadline would have hidden both of the reds that landing found.

No forward attachment is declared: this is a harness-headroom finding, not evidence toward a
parked atom. The `Advances:` key is deliberately absent rather than set to a placeholder — the
attachment ledger parses that field as an atom id, so `Advances: none declared` renders two
`unknown_atom` violations and reds the very gate this finding is about. Caught here, on this
document, before it landed.

## What was observed

Ten consecutive publish failures ended in `rc=77 commit_did_not_land`, outcome `commit_timeout`:
the `git commit` in `background/process_run_complete.py::git_commit_push` hit
`GIT_COMMIT_HOOK_TIMEOUT_SECONDS = 600` and `TimeoutExpired` was raised, caught, and correctly
degraded to "retry next cycle".

The two reds that actually refused the commit are fixed elsewhere. This finding is about the
number that made them invisible for eight hours.

`tools/pre_commit_test_gate.py` selects test files by filename stem from the staged pathspec and
runs them as one `pytest` invocation at `cwd=ROOT`. A publish commit selected 7 files in one
cycle and 15 in another. Measured directly, on this machine, `SIM_FAST_MODE=1`:

```
tests/background/test_blocked_atom_visibility.py
tests/background/test_derived_artefact_register.py
  -> 2 failed, 37 passed in 393.27s
```

**393s of a 600s budget for the first two files of fifteen.** The 15-file run reached 16% of its
collected set before the kill. So the gate did not merely fail to pass — it never reached the end
of the file list, and the progress line it had emitted (`...F............F...`) was the only
statement of the cause that survived, buried in a log tail.

## Why this is the shape that matters, not just "it is slow"

The comment above `GIT_COMMIT_HOOK_TIMEOUT_SECONDS` already anticipates this class in the
neighbouring case, and says so in its own words: the old 30s cap "silently became a function of
how many tests exist rather than of whether the commit is healthy". The same sentence is true of
600s. Nobody chose 393s for two files; it accreted. `select_targets` widens with the pathspec,
and the publish pathspec widens with the site — so the cost of a publish commit's gate is a
function of how much the site publishes, and it grows on a schedule nobody reviews.

The failure mode is not "commits get slower". It is **the gate loses the ability to report its own
verdict**. A red found at 30% of the file list is a red the log can name; a red found at 105% of
the budget is a `TimeoutExpired` whose diagnosis points at the hook chain, which is what the
RUNG-1 doorbell then said for eight hours. That is why the timeout is worth treating as a defect
even on the cycles where the tests would have failed anyway.

## What is NOT the fix

- **Raising the deadline.** It restores publishing while leaving the reporting failure intact,
  and the next accretion re-creates it at the new number. It would also have hidden both reds
  this draw found: with 900s the 15-file run would have completed, printed `2 failed`, and been
  refused — better, but only until the file list grows again.
- **`-x` on the gate's pytest.** Fail-fast makes the FIRST red cheap and every subsequent one
  invisible, which is the `red_census: fail_fast_only` state the wedge detector already records
  and already cannot act on.

## The two candidates, and the recommendation

1. **Bound the gate by its own clock and report what it got through.** Give the gate's pytest a
   budget strictly inside the commit deadline, and on expiry print the file list it did NOT
   reach. A partial verdict that says so is worth more than a kill, and it makes the difference
   between "slow" and "red" legible without changing either.
2. **Cost the selection.** `select_targets` has no notion of what a target costs. The two files
   above are 393s because they shell out to `--check` subprocesses per artefact
   (`derived_artefact_register.stale_in` runs one process per registered artefact) and rebuild
   the live map (`blocked_atom_visibility.build_report`). Both are legitimately expensive and
   both are legitimately blocking.

**Recommendation: (1) first**, because it is small, it is reversible, and it converts every
future instance of this class from a silent kill into a named partial result — which is the
property that was missing today. (2) is the real headroom work and should be drawn on its own
evidence, not bundled into a wedge repair.

## Reproduce

```
SIM_FAST_MODE=1 python3 -m pytest tests/background/test_blocked_atom_visibility.py \
    tests/background/test_derived_artefact_register.py -q --no-header
```

Cross-check the budget it is spent against:
`background/process_run_complete.py::GIT_COMMIT_HOOK_TIMEOUT_SECONDS`.

---

# 2026-08-25, later: the budget was raised, it landed at 837s of 840s, and the duplication is now PROVEN rather than suspected

**Severity unchanged (LATENT). What changed is that the cause is no longer a hypothesis.**

## What happened after this was filed

The deadline was raised 600 → 840 (`a4d8a7e32`), against this document's own explicit advice that
raising it is not the fix. That was my call and it was the right emergency move and the wrong
permanent one: publishing had been down twelve hours, and the raise plus
`_record_commit_hook_duration` — added in the same commit, because the thing that timed out was
the one thing nobody was measuring — turned an invisible kill into a number.

The number, from `docs/observability/commit_hook_duration.jsonl`:

    2026-08-25T19:12:58   804s   refused   tight
    2026-08-25T19:43:59   825s   refused   tight
    2026-08-25T21:21:59   837s   pass      tight     <- the publish that ended a 15-hour outage

**Three seconds of headroom on the commit that recovered publishing.** The delivery seat read the
same series an hour earlier and called it: *"Second strike (R3): stop raising the deadline …
decide whether that second gate checks anything the first did not, and remove the duplication."*

## The decisive measurement this document was missing

`background/publish_scope.resolve_scope()` returns the publisher's own scoped gate list. It
CONTAINS `tests/background/test_derived_artefact_register.py`.

So on every publish cycle that file runs **twice**: once in the publisher's own scoped gate (517s
for 2,426 tests, green, before the commit is attempted) and again inside the `git commit` hook
chain, where it costs 348–385s on its own. The second run is against the tree the commit would
create rather than the working tree, which is a real difference — but it is a difference that has
never once been the thing that failed, and it is being paid for at 40% of the entire commit
deadline.

That is the duplication, named and sized. It was inferred before; it is measured now.

## What I fixed, and it is the small half

`head_checkout` extracted a **~130 MB `git archive HEAD`** per fixture instance — a cost this
document's own reproduce section led me to expect would dominate. It does not. Narrowing the
archive to exclude bulk data no registered artefact's `--check` reads (`site/data`, `site/state`,
`docs/state`, `sim/hh_data`, `docs/reports` — 89 MB of 160 MB tracked) moved the file from **385s
to 348s: ten percent.** Landed because it is free, green and also relieves the `/tmp` exhaustion
this fixture's own comment records — but it is not the answer and saying so is the point of this
section.

The remaining ~348s is inside the artefact renderings themselves: `--check` recomputes the full
rendering, and `blocked_atom_visibility`'s clock probe shells out to `git blame` per atom across
298 atoms in a cold checkout. **That** is where the time is.

## What would actually close this, and why I did not do it tonight

Not a third number, and not making the tests faster either — both leave a full duplicate suite
inside the commit. The shape that removes the cost is a **gate receipt keyed on the exact tree
hash the commit creates**: the publisher gates the tree it is about to commit, and the hook, on
finding a green verdict recorded against that same tree hash, does not re-run what it has just
been shown. It is NOT `--no-verify` — the hook still runs and still decides — and the receipt
cannot go stale by construction, because a different tree is a different hash.

It touches the commit gate, which CLAUDE.md names a WALL, and it needs its own design and its own
R15 controls (a receipt for a different tree must not release; a receipt with no verdict must not
release; an unreadable receipt store must FAIL CLOSED). That is a piece of work, not a tail-end
patch, and it is now LANE 0 focus item 2 — drawable by any tick, with this measurement in hand
rather than a hypothesis.

## Evidence

- `docs/observability/commit_hook_duration.jsonl` — 804/825/837s against an 840s deadline.
- `python3 -c "from background.publish_scope import resolve_scope; print(resolve_scope()['tests'])"`
  — contains `tests/background/test_derived_artefact_register.py`.
- `SIM_FAST_MODE=1 python3 -m pytest tests/background/test_derived_artefact_register.py -q` —
  385s before the archive narrowing, 348s after, 13 passed both times.
