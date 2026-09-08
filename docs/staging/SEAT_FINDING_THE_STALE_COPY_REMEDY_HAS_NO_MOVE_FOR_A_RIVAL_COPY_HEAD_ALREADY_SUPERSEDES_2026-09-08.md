**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The stale-copy refusal names the right paths and its stated remedy has no legal move for two of them

**Filed 2026-09-08 by the delivery seat (lane 0), while wiring the guard into the cheap door. The
measurement is in `PREREG_ARE_THE_EIGHT_STALE_COPIES_PURE_CHECKOUTS_OR_DO_THEY_CARRY_HOLDER_WORK_2026-09-08.md`,
whose first three predictions this refutes.**

## What landed this turn, first, so this finding is not read as a stall

`tools/stale_copy_refusal` is now wired into `tools/git-hooks/pre-commit` as `--staged`. Until
today it was reachable from `tools/surgical_land.py` **only** — the careful door was guarded and
`git commit -- <path>`, the cheaper and commoner habit, was not. That was the wrong way round and it
is closed. Seven tests, six source mutations, each killed by its own named leg; the skip that keeps
`surgical_land`'s `--drops` escape hatch alive is keyed to a re-derived tree sha rather than a
boolean, and a token naming any other tree buys nothing.

## The finding

The refusal text tells a refused lane exactly what to do:

> `python3 -m tools.isolate_hunks --survey <path>` shows the hunks, `--keep N` builds
> HEAD-plus-your-hunks-only, and `surgical_land --content <path>=<file>` lands those bytes.

**For two of the eight copies that remedy has no legal application, and `isolate_hunks` is right to
refuse it.** Those two supply *zero* symbols HEAD does not have. Every hunk in them is either the
same code reworded or a strictly weaker version of what HEAD carries:

- **`tools/promote_worktree_landing.py`** holds `_bind_to_claim(commit, work_id)` — the version
  *without* the `since` argument, i.e. the code as it stood before `b06fa3528`. `since` is what
  makes the binding's subject "what does this commit add to `origin/main`" rather than "what did it
  add against its first parent", and its absence is the defect that bound four of another lane's
  paths and printed a plausible success line. There is nothing here to keep.
- **`simulation/policy_costs.py`** holds alternative wording for two error strings, and is missing
  the 2026-27 RO rate and the 2026/2027 electricity and gas CCL rates outright.

Select a hunk and you land a revert. Select none and `isolate_hunks` refuses, correctly: *"landing
HEAD's own bytes back over itself is an empty change wearing a commit's clothes."* Both branches are
right. There is no third one.

## Why this is not a defect in `isolate_hunks`

It is a defect in the **census's model of what a stale copy is**, which the tool's own docstring
states plainly and which today's measurement contradicts. The model is *your copy is HEAD-as-it-was,
plus your edits*. The reality on this tree is a third thing neither the tool nor the direction that
drew me here had named: a **rival copy**, where another lane wrote the same feature independently,
worded it differently throughout, and never pulled the landing. Zero of the eight is byte-identical
to any ancestor blob on its path. They are not behind; they are *beside*.

For the six that carry genuinely new symbols the drawn remedy is exactly right and should be used.
For a rival copy HEAD strictly supersedes, the repair is *"replace these bytes with HEAD's"*, and:

- `surgical_land --content` **never writes the working tree** — that is the property that makes it
  safe for a two-lane file, and it is why the guard could stop the ninth instance while repairing
  none of the eight.
- `git checkout <path>` and `git stash` are forbidden by `CLAUDE.md`, **for this exact class's
  sake**: they discard the holder's work. The prohibition is right in general. On a Kind-A copy,
  where the holder's work is provably nil, it forbids the only move that would help.

So the class has an armed guard, a correct refusal, a named remedy — and for this shape, no door.
That is the same structure as the ruling that produced `surgical_land` itself: *a rule that leaves no
legal move evaporates*, and the pressure it creates points at `git checkout`, which is the wall.

## What is next, and why not this turn

**The move to build is a sanctioned `refresh-to-head`** — something that writes HEAD's bytes over a
working copy *after* preserving the current bytes where `git log --all -S` can find them, and
refuses unless the copy supplies no symbol HEAD lacks. The refusal is what stops it becoming
`git checkout` with a nicer name: it can only ever run on a copy that has provably nothing to lose,
and it says out loud what it preserved and where. The repo already has the preservation idiom —
`e8f3a2618 preserved shared-tree worktree state before ff to origin/main`.

I did not build it this turn, deliberately. It is a **write into another lane's uncommitted tree**,
which is the one thing the isolation this seat runs under exists to make impossible, and inventing
that authority inside a bounded turn is not a reversible call in the way the rest of this work is.
The eight copies are dangerous but not urgent in the next hour — the guard now covers both doors, so
instance nine cannot land through either.

## Correction to the direction that drew me here

The drawn item states `tools/promote_worktree_landing.py` "is missing all 14 lines of
`_bind_to_claim`, the binding repair". It is missing the fourteen lines commit `b06fa3528` added —
which is the `since` repair *inside* `_bind_to_claim`, not the function. The census's own wording is
exact; the paraphrase reads as "the function is gone" and sends a reader looking for the wrong
thing. Recorded here rather than fixed silently: the paraphrase is what I acted on for the first
twenty minutes of the turn.
