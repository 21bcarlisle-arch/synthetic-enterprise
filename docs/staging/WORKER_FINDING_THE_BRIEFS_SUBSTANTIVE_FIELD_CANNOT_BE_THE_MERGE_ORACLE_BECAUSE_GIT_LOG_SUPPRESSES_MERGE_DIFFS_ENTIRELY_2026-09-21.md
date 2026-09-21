**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [WORKER] The brief's `substantive` field is not a merge oracle — it is silence, and it is silent the same way for the 35 and the 12

LATENT, not BLOCKING: it makes the seat's brief blind to what a conflict-resolving merge authored,
which loses orientation content. It does not write a false DONE anywhere.

## What the drawn item assumed, and what is actually true

The Lane 0 item `a-merge-that-authored-nothing-is-not-this-lanes-work` reasoned that the correct
reading of a merge *"is already computed elsewhere in the same brief"* —

> the brief's own `commits[]` field computed that and marked it `files: []`, `substantive: false`

That is true of `f56852e25` and it is true for the wrong reason, which matters because the item's
FINISHED criterion was *"`commit_narrative` and the brief's `substantive` field return the same
verdict for every merge in the last two hundred commits"*. Taking that literally would have forced
the repaired instrument to call **all 47** merges no-work, including the 12 that authored a
resolution. The criterion was a prediction about an instrument, and the instrument does not measure
what the prediction assumed.

`delivery_seat.commits_since` builds its file list from:

```
git log --since=... --pretty=format:%H%x00%s --name-only HEAD origin/main
```

`git log` **suppresses merge diffs entirely** — no `-m`, no `-c`, no `--cc`. It does not print a
merge's paths and then find none; it never asks. So every merge on that route gets `files: []` and
`substantive: false` by construction, exactly as loudly for a merge that resolved a contested file
as for one that took one side here and the other there.

## Measured, this tree, last 200 commits (2026-09-21)

| | count |
|---|---|
| merges | **47** |
| `git log --name-only` printed any path for them | **0** |
| merges whose combined diff (`git diff-tree -c`) is non-empty — they authored something | **12** |
| merges that authored nothing | **35** |
| merges where the two readings DISAGREE | **12, always in the same direction** |

`f0efa1a06` is the shape the brief cannot see: subject *"merge origin/main: automatic
reconciliation in an isolated worktree"*, `--stat` shows three files, and its combined diff is two
staging documents whose merged content is in **neither** parent. The brief reports it as `files:
[]`. The seat is told a commit that authored two documents touched nothing.

## What was repaired today, and what this is not

`background/commit_narrative._carries_work` now asks the combined diff for `len(parents) > 1`
(landed with its control this tick), so the **liveness** question — *did this commit change
anything at all* — is right for all 47. This finding is about the **other** reading beside it:
*were the files worth orienting on*. The two answer different questions and the module docstrings
on both sides already say so; they are not being merged into one.

## The repair, named rather than done

`commits_since` needs a merge's authored paths, which is the same set `commit_narrative` now reads.
Two routes, and choosing between them is a judgement about the seat's orientation cadence, not a
missing clause:

1. **Ask `commit_narrative`.** It already computes `_combined_diff` for the same stretch. The seat
   imports it for `commit_shape` four lines down. This is the no-second-classifier answer, and the
   self-note's own design argument (quoted in `commits_since`) points at it.
2. **Second `git log` pass with `--cc --name-only` for merges only.** Cheaper to write, and it is
   a parallel measurement layer — the thing `commits_since` exists arguing against.

Route 1 is the recommendation.

**Why it is not done in this tick, stated rather than left to be inferred:** `substantive_count`
feeds `is_material`, which decides whether the seat orients *at all*. Giving 12 merges a non-empty
file list can only raise that count, so the seat would orient on stretches it currently skips. That
is probably correct and it is a change to the seat's own cadence, which is a different subject from
the liveness instrument, and attributing a cadence change to the right cause requires it to move
alone.

## The general shape, for the catalogue

**A field that is structurally unable to answer a question agrees with every answer to it.** The
item found `substantive: false` next to the right verdict and read it as corroboration. It was the
absence of a reading, and the check that would have separated the two is one line: ask whether the
field is ever `true` for any member of the class. It is not — 0 of 47.
