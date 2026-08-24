<!-- MOVED TO in_progress/ 2026-08-24 (worker tick, publish-gate unwedge). The still-open
  sub-item is the ONE below under "Not done": re-wire `site/data/projections.json` into a
  surviving door (`/harness/`, recommended) or unwire the producer. Nothing here is archived.
  UNBLOCKED BY: nothing — it is drawable now; it was ranked below the census reds and those
  are cleared by this tick's landing.

  CORRECTION TO THIS DOCUMENT'S OWN "Done" CLAIM, 2026-08-24. It said the four
  door-driving tests in `tests/tools/test_generate_projections_page.py` were removed and
  "4 census reds cleared". THAT WORK WAS NEVER COMMITTED. Measured at HEAD a21b90d8f in a
  detached scratch worktree: those four tests are still present and still RED (4 failed,
  9 passed); the repair existed only in the shared working tree, and THIS FINDING FILE was
  itself untracked. It is landed in the same commit as this move — which makes the finding
  an instance of the class it was filed to describe (a producer kept, its consumer lost)
  wearing the other class's coat as well (CLASS_UNCOMMITTED_AND_ORPHANED_WORK). The file
  was not in the publish gate's 161-file blocking scope, so it wedged commits selecting
  that stem rather than the public surface. -->

**Severity:** LATENT · **Lane:** G_data_learning

**Rank:** after the remaining census reds.

# The projection feed is rewritten every publish cycle for no reader

`observed-with-evidence` unless marked otherwise (R9).

## What is true

`background/process_run_complete.py:3380` calls `tools.generate_projections_page.generate()`
on **every publish cycle** — roughly every 25 minutes, all night, every night. It writes
`site/data/projections.json`.

**Nothing reads it.** Measured, not assumed:

```
grep -rn "projections\.json" --include=*.html site/   ->  0 hits
grep -rn "wip_flow\.json"    --include=*.html site/   ->  0 hits
grep -rln "projections\.json" --include=*.py --include=*.mjs .
   ->  tools/generate_projections_page.py, tests/tools/test_generate_projections_page.py,
       background/process_run_complete.py     (producer + its own tests, no consumer)
```

`site/data/wip_flow.json` — the hand-refreshed file the feed was built to supersede — has not
been written since 2026-08-20 07:48 and has no reader either.

## What produced it

`03dd8c49e` (2026-08-20, *"The five tabs are the site now: eleven pages deleted"*) deleted
`site/wip-flow/index.html` and `site/wip-flow/_render_harness.mjs` along with ten other pages.
That door was the feed's only reader. The producer was left running.

This is the **third instance this week** of one class — a deletion the tests never followed:

| # | Instance | Disposition |
|---|----------|-------------|
| 1 | 34 page-reading tests (`58fcdc2e6`, 2026-08-22) | fixed; subject sets DERIVED from disk |
| 2 | Defect 4's reader-facing half (`WORKER_FINDING_THE_FIVE_TAB_CONSOLIDATION_DROPPED_DEFECT_4S_READER_FACING_HALF_2026-08-22.md`) | filed |
| 3 | this one | filed here |

It is the instructive instance because the other two lost a *check*. This one lost a
**consumer** and kept the *producer*, so the machine is doing real work on a real cadence
that reaches nobody, and no control noticed — the feed is still generated, still stamped,
still correct, and still unread.

## Why it matters to an atom, not just to a file

Atom `G13_projection_consumers` (level_current 2, target 2, `provenance: director_ruling`)
states its own gain as:

> *"A store with no reader is the same design-with-no-caller this instruction was written to
> end; the caller **IS** the deliverable."*

G13 shipped **two** callers: a site page and a lab query. The site page is gone. The lab
query is alive and green — `tests/tools/test_lab_query.py`, 23 passed at HEAD `13d567d8f`.

So **level 2 is not unbacked and is not being demoted here**: the atom keeps a real reader.
It is half of what it was, and the half that went is the reader-facing one. `inferred`: a
level whose deliverable is "the caller" ought to have a control that fires when a caller
count drops, and none exists — that is the generalisable gap, not this instance.

## What was done in this pass, and what was not

**Done** (`tests/tools/test_generate_projections_page.py`): the four tests driving the deleted
door are removed and the loss is named in a comment where they stood, with the re-point
attempt recorded as measured-and-unavailable. 9 tests remain green; 4 census reds cleared.

**Not done, and it is the actual decision:** whether to re-wire the feed into a surviving
door (`/explore/` or `/harness/` are the candidates) or to unwire the producer. Both are
reversible; neither is a one-liner; and doing it inside a weekend token stand-down would be
building beside a thing rather than reading it first. Recommendation, to act on unless
countermanded: **re-wire into `/harness/`** — the WIP-flow board is harness content, the
director's 2026-08-21 priority named Harness content directly, and unwiring the producer
would spend G13's remaining ground to save ~25 minutes of compute a day.

## Reversal

`git revert` of the landing commit restores all four tests and the constants; the deleted
door is at `03dd8c49e^:site/wip-flow/`.
