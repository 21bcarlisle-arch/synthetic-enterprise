**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `prune-comment-only-path-edges-and-freeze-the-33-in-one-commit`)

# Pre-registration: pruning comment path edges, and what I expect the floor to do

Written BEFORE the change is implemented or any census is run in this tree. The input finding is
`docs/staging/records/SEAT_FINDING_THIRTY_FOUR_MODULES_ARE_HELD_OUT_OF_THE_ORPHAN_SET_BY_A_COMMENT_AND_THIRTY_THREE_HAVE_NO_GRANDFATHER_2026-09-08.md`,
measured at `46b51ba8a`. This tree is at `cc7452013`, and the shared baseline has moved from the 373
that finding saw to **374**, so its 34/33 split is a premise to re-measure, not a number to carry.

## What I am changing

`tools/capability_index._path_references` regexes the whole source text, so a repo-relative `.py`
path written in prose is a caller edge. The change: **a path token lying inside a comment is not an
edge.** Everything else about the edge model is untouched — a real import, a `subprocess.run`
argument, a path in a config string, and (deliberately, for now) a path in a docstring all remain
edges.

## The rule I will implement, and why it is wider than the finding's

The finding's census used *"every reference in the calling file sits on a line starting `#`"* and
called the result a FLOOR. I will use `tokenize`, which identifies COMMENT tokens properly and so
also catches the **trailing** comment (`RUNNER = "x"  # see tools/foo.py`) that a line-starts-with-`#`
test cannot see. Same rule, honestly applied, rather than a rule shaped to reproduce a number.

Where `tokenize` fails (an unparsed file), I fall back to the finding's line-starts-with-`#` test
rather than dropping every edge in that file — dropping would manufacture orphans out of a parse
error, and an unreadable file is already its own finding.

## Predictions, in order of how much they would cost me to be wrong about

1. **The tokenize rule prunes strictly more edges than the strict rule, and orphans a strict
   superset of its modules.** If it orphans a module the strict rule does not, that module's only
   wiring is a trailing comment. If the two sets are EQUAL, this repo simply never writes a path in
   a trailing comment, which is a finding about the codebase and not a bug in the rule.
2. **Newly-orphaned modules: 34–70.** The finding's 34 is a floor by its own account and I have
   added one class to it. Below 34 means the tree has changed under me or my rule is narrower than
   I think; above 70 means the trailing-comment habit is far commoner than the leading-comment one,
   which I would not believe without looking at the instances.
3. **The 33 named in the finding are all still orphaned by this change**, minus any that were
   genuinely wired between `46b51ba8a` and `cc7452013`. A name on that list that survives as
   reachable has a NEW edge, and I will say which.
4. **The baseline grows; it does not shrink.** New floor ≈ 374 + (newly orphaned). No module leaves
   the floor as a result of this change: pruning edges can only remove reachability.
5. **`module_count` in the frozen baseline will equal this tree's module count** and the
   `BASELINE PROVENANCE` note will be silent afterwards. If it is not silent, I froze from the
   wrong tree.

## What would refute the whole approach

If the pruned edges include a **genuine** subprocess call whose only textual form in the calling
file is inside a comment, then the module really is run and the floor would be recording something
untrue — the exact lie the finding refused when it declined to freeze the 33 without the pruning. I
will read a sample of the newly-orphaned modules' pruned edges and say plainly whether any of them
looked like real wiring rather than provenance prose.

## What done means (this is direction, not an atom, so I am deciding it)

One commit that: prunes comment path edges in the index; freezes the resulting floor with the reason
on the record; carries a control that FAILS if the pruning is reverted; and leaves the orphan
ratchet green for a lane that touched none of it. Both doors proven — the shared-tree `git commit`
path and the clean-extract `surgical_land` path — because this finding's own ancestor incident is a
case of those two disagreeing.
