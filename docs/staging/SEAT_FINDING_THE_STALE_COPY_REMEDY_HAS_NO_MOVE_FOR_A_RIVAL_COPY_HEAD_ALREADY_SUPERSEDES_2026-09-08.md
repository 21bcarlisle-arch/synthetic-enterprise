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

---

## ADDENDUM, measured after the wiring landed: the remedy is PER-PATH and at least one of the eight is half a pair

The six Kind-B copies carry genuinely new symbols, so the drawn remedy — isolate the holder's hunks
and land them over HEAD — does apply to them in principle. I checked whether it is **safe**, by
asking of each whether the names its new code references exist at `origin/main`. Five resolve.

**`tests/tools/test_commit_refusal_attribution.py` does not, and the way it fails is the finding.**
Its three new tests call `attr.decompose_outage(...)`. `tools/commit_refusal_attribution.py` is
present at `origin/main` at 1382 lines and **does not define `decompose_outage`**. It is defined in
the shared tree's *uncommitted working copy* of that module.

So the lane holding this stale test copy also holds an uncommitted edit to the module it tests, and
**only the test is in the census's eight** — the module is not stale by rule 1, so nothing names it.
A seat that works the eight path by path, exactly as the refusal text instructs, lands the test
without the function and reds the tree at HEAD for every lane.

That is not a defect in the refusal, which is correct about the eight paths it names. It is a limit
on the **remedy's granularity**: `isolate_hunks` + `surgical_land --content` operate on one path,
the refusal is printed one path at a time, and a lane's work is not path-shaped. Nothing in the
route tells you to look for the other half, and the other half is invisible to the control that
sent you.

**What this adds to "what is next".** The `refresh-to-head` move sketched above is still the answer
for the two Kind-A copies. For the Kind-B six the extra requirement is: before landing any isolated
hunk, resolve the names it introduces against the tree it will land into, and if a name resolves
only in another *uncommitted* file, that file is part of the same landing. A one-leg version of
that check is cheap — `tools/symbol_landing_check.py` already asks whether every first-party
reference resolves in the tree a commit creates, and it is the control that would catch this — but
it is only reachable from the landing door, so it fires *after* a seat has spent the isolation work.
Naming the pair at census time would cost one pass and save the turn.

Recorded, not built: this turn's landed increment is the cheap-door wiring, and the pair-detection
belongs with the `refresh-to-head` work rather than bolted onto a census.

---

## WHAT LANDED, 2026-09-08 (lane 0, isolated worktree): the move exists, the door is named per path, and the pair is named at census time

Three things, and the third was not predicted.

**1. `tools/refresh_to_head.py` — the move.** Three conjunctive preconditions, each computed from
the tree rather than asserted: the copy supplies no name HEAD lacks (`stale_copy_refusal.symbols`);
the stale-copy control actually refuses the copy (`stale_copy_refusal.judge` — without this leg it
reverts any edit you point it at, which IS `git checkout`); and the current bytes are **proven**
recoverable before they are destroyed. The preservation commits onto
`refs/preserved/refresh-to-head/<slug>` through a throwaway `GIT_INDEX_FILE`, so the holder's index
is untouched, and `verify_recoverable` **runs** the `git log --all -S` lookup the tool advertises
rather than printing it — a preserved commit that no ref reaches passes the identity leg happily
and is unfindable by the route anyone would actually use. Default is survey; the line-level losses
a symbol test cannot see are printed before any byte moves. It refuses a staged path, a path HEAD
does not have, a suffix it has no reader for, and a mixed run in which any path is refused.

**2. The refusal names the door PER PATH.** It printed one remedy for both shapes and the wrong
half was the half with no move. `gains_over()` answers which, and returns `None` rather than `()`
when it cannot tell — a door named on a guess is worse than no advice, because one of the two
overwrites bytes. `--census` then **runs the door it names** (`door_verdicts`) instead of claiming
it: the finding this whole class is about is a remedy that refused.

**3. `tools/landing_pair.py`, and it fires at `isolate_hunks` rather than at the landing gate.**
`symbol_landing_check` asks the identical question and would red the commit — but only at the
landing door, after the survey, the selection, the build and the typed command. The resolution rule
is now a single function (`symbol_landing_check.unresolved_kind`) that both callers share, because
a pointer that refuses early where the gate passes late teaches a seat to stop believing it.

### The census's own first live run, against the shared tree, and what it found

    2 paths → refresh_to_head, and the door verdict for BOTH is `refreshable` (the door is OPEN)
    6 paths → isolate_hunks
    1 PAIR   tests/tools/test_commit_refusal_attribution.py needs
             tools.commit_refusal_attribution.decompose_outage, which exists ONLY in the
             UNCOMMITTED copy of tools/commit_refusal_attribution.py

That is the addendum's measured case, reproduced by the mechanism rather than by hand.

**And a ninth state nobody had named.** `tests/tools/test_r1_inference_ceiling.py` references
`tools.r1_inference_ceiling._scores_on_folds` and `honest_point_estimate` — and **no tree supplies
either, committed or not.** That is not a pair and it is deliberately not reported as one: an
unresolved reference with no supplier anywhere is a *worse* state than a pair, not a cleaner one,
and folding the two rows together would have printed the tree's worst case as "no pair found". Its
holder has a copy of that test written against a version of `tools/r1_inference_ceiling.py` that
exists in no tree this machine can see. Isolating its hunks and landing them reds HEAD for every
lane, and unlike the pair there is no other half to land with it.

**What is still open.** Six of the eight remain Kind-B and are the holders' to land; the finding
stays open until they are. What has changed is that each of the eight is now sent somewhere with a
move, and the two whose door was shut have one.
