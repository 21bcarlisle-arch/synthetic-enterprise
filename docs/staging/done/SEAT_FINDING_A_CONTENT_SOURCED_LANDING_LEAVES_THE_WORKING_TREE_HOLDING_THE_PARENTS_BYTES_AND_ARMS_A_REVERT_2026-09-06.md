**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** uncommitted_and_orphaned_work

# A content-sourced landing leaves the working tree holding the parent's bytes, and the revert it arms fired within the hour

**Found 2026-09-06 by the delivery seat, starting the fifth subject of the convergence-evidence
sweep. Not looked for: the battery imported the wrong engine and that is how it surfaced.**

---

## The mechanism

`tools/surgical_land.py` builds the resulting tree, commits it, and then brings the real index
into line for exactly the landed paths — `_refresh_index_for` (line 1089), whose docstring is
explicit about why that is not optional: *"the index would still hold the PARENT's content for
those paths, so `git status` would show the landing as a staged REVERT and the next commit would
undo it."*

It also has `_write_worktree_from_tree` (line 1052), which puts those paths on disk as the
resulting tree has them. **That call is reached only on the merge branch** (line 1229, inside
`if dispositions is not None`). A pathspec landing takes the `else` at line 1231 and refreshes the
index alone.

For an ordinary pathspec landing that is correct and there is nothing to do: the tree was built
*from* the working tree, so the working tree already holds the landed bytes.

**`--content` is the case where it is not.** Its whole purpose is to commit bytes that came from
outside the repo, precisely *because* the working-tree copy cannot be trusted — a dirty file
another lane is holding, or an artefact recomputed in a clean extract. So after a `--content`
landing the working tree still holds the parent's version of every content-sourced path, `git
status` reports the landing as a modification undoing itself, and the exact sentence
`_refresh_index_for` was written to prevent is true of the disk instead of the index.

Nothing clears it. There is no route by which it ever clears.

## The revert that fired

`e1143b8ea` landed four paths via `--content` about an hour before this was written. Two of them
were tracked files that already existed:

| path | state now |
|---|---|
| `tools/contract_battery.py` | ` M`, working-tree bytes identical to `3359a8ce0`'s version (HEAD~1) |
| `docs/design/orphan_baseline.json` | ` M`, working-tree bytes identical to `3359a8ce0`'s version (HEAD~1) |

`orphan_baseline.json` is the clean causal case: it was clean at `3359a8ce0`, the landing changed
it in git, and the disk was left behind. `contract_battery.py` was *already* stale before the
landing — that staleness is why `--content` was used — and the landing neither caused nor cleared
it, which is the same outcome by a different route.

**What the stale engine cost, concretely.** The version left on disk was HEAD minus the
`spec_fingerprint` guard, which had landed 15 minutes earlier at `3359a8ce0`. That guard exists
because a battery adopted another lane's results file and published eight survivals it never
applied. The first run of this subject's battery therefore executed *without it*, and wrote to
`/var/tmp/company_data_battery_results.json` — the pre-guard default path, the subject-name-keyed
one the guard replaced precisely because two specs for one subject collide on it. The run was
interrupted before it produced rows, so no false verdict was published. That is luck, not a
control.

## The tree-wide census

Every dirty tracked file, tested against its own content at each of the last 40 commits — the
question being *does the disk hold a committed revision that is not HEAD*, which is the "silent
revert armed" state and nothing else:

```
dirty tracked files scanned: 180
holding an older committed revision: 5
  HEAD~1    3359a8ce0  docs/design/orphan_baseline.json
  HEAD~10   423203aa5  docs/staging/SEAT_RESULT_NO_CONTRACT_ON_THE_BUSIEST_..._2026-09-06.md
  HEAD~31   1cfc48c01  docs/staging/reference/CLASS_FIGURES_ON_A_SUPERSEDED_CLOCK_2026-08-28.md
  HEAD~31   1cfc48c01  docs/staging/reference/CLASS_MEASUREMENTS_THAT_MIRROR_2026-08-12.md
  HEAD~31   1cfc48c01  docs/staging/reference/CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md
```

`tools/contract_battery.py` is absent from that list only because this session restored it to
HEAD before running the census; it was the sixth. Two of the three `CLASS_*` rows have been
holding a 31-commit-old revision, which says this is not a fresh condition and not specific to
`--content` — `--content` is one producer of a state the tree already accumulates and nothing
drains.

## Why this is worse than an ordinary dirty file

A dirty file usually holds work someone wants. This one holds work someone already *replaced*, and
it is indistinguishable from the first by `git status`. Both read ` M`.

That matters because of the rule the seat actually follows: **commit by pathspec, never `-A`** — a
pathspec stages the *working-tree* copy. The discipline that stops you sweeping another lane's
files is the same mechanism that, aimed at one of these five paths, reverts a landed change while
reporting success. `isolate_hunks.py` is the escape and it only helps a lane that already knows
the file is contested.

## What I am doing about it, and what I am not

**Done:** restored `tools/contract_battery.py` to HEAD before running the battery, having first
proved the overwrite was lossless — the only line the disk held that HEAD did not was the
pre-guard `--out` default, i.e. the guard's own removal. Nothing was destroyed and the check is
the point: *prove the working-tree copy holds nothing HEAD lacks, then overwrite* is the safe form
of a repair that `git checkout <path>` would do blind, which is why that command is banned here.

**Not done, deliberately:** no new register, no daemon, no gate. The seat has 34 alarm documents
and the standing instruction is to prefer doing the work to building the thing that watches the
work. The census above is nine lines of throwaway Python and it answers the question completely
whenever anyone asks it.

**The one thing worth building, if this recurs:** `surgical_land` already knows exactly which
paths were content-sourced — it names them in the receipt (`content-sourced:`). The honest fix is
for a `--content` landing to say so on the way out: *"N paths landed from bytes outside the repo;
the working tree still holds the parent's copy of each; a pathspec commit of any of them will
revert this landing."* One printed sentence at the site that creates the state, not a register
that watches for it afterwards. It is not built in this turn because the turn's work is the
battery, and a second instance is what would justify it.

## What this cannot establish

The census covers tracked files dirty *right now* against the last 40 commits. A path that was
left behind and has since been re-landed by another lane, or reverted and re-reverted, does not
appear. So five is a floor on the standing count and says nothing about how often the state has
been entered and left.
