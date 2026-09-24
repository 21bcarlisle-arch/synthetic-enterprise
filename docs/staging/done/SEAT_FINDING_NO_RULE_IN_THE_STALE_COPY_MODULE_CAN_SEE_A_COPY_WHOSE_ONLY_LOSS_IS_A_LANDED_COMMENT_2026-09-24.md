**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# FINDING — no rule in `stale_copy_refusal` can see a copy whose only loss is a landed COMMENT, and `refresh_to_head` reports that blindness as "no complaint"

*Filed by the delivery seat from an isolated worktree, 2026-09-24. Surfaced by the refutation of
prediction 2 in `docs/staging/records/PREREG_THE_STASH_CLOCK_REPAIR_2026-09-24.md`; it is not what
that item predicted and it is not the clock.*

## The instrument says something it has not measured

`tools/refresh_to_head` on the shared tree, against `origin/main`:

```
tests/background/test_a_swept_row_names_the_sibling_that_holds_its_windows_commit.py
  [refused_head_does_not_supersede_it]
    the stale-copy control has NO complaint about this copy against origin/main: it does not
    predate the last landing there and it deletes no name. Refreshing it would discard an
    ordinary edit, which is `git checkout <path>` with a nicer name -- and that is forbidden
    here for this exact reason.
```

It is not an ordinary edit. The working copy **reverts a six-line comment block that
`8d84c67b5` landed**, and puts back the four-line comment that landing superseded:

```
-    # THE STUB TRACKS THE REAL SHAPE, and it had drifted on BOTH axes: `_window_hits` returns
-    # (paths, hits, liveness_only) and each hit is (sha, when, subject, touched). This stub still
-    # returned a 2-tuple of 3-wide hits, so the test died in `_landed_by_sibling`'s own unpack
-    # before reaching a single one of the three readings it exists to assert -- red at HEAD, which
-    # makes the whole module uneditable by any lane. A stub of the function under test is only
-    # evidence while it can still be SUBSTITUTED for that function; this one could not.
+    # The third element is `_window_hits`' liveness-only list (2026-09-19). Empty here on purpose:
+    # ... (the superseded 2026-09-19/09-22 pair)
```

That comment is the entire written record of why the stub was red at HEAD — a BLOCKING finding's
own explanation, landed twelve minutes before the copy that deletes it.

## Why every rule in the module is structurally blind to it

Measured, not inferred:

| rule | why it cannot see this |
|---|---|
| rule 1 (`judge`, distinctive lines) | `distinctive_lines` calls `_trivial(line, comments_are_evidence=False)`, so `8d84c67b5` yields **2** distinctive lines and both are code the copy CARRIES. `missing` is **0**. |
| rule 1a (older-clock leg) | `if missing and taken_before(...)` — `taken_before` is **True** here (and was True before the 2026-09-24 stash-clock repair, by mtime alone), but `missing` is 0, so the leg never runs. |
| rule 2 (strict symbol subset) | the copy deletes no name — a comment is not a symbol. |
| rule 4 (`clock_judge`) | returns at its first line: `.py` is in `READABLE`, so this suffix is rule 1's and never reaches here. |

So the copy is vouched for by construction, and the door prints a positive claim — "deletes no
name", "an ordinary edit" — where the honest answer is *this control has no reader for what you
are about to discard*. **That is the fail-silent shape this module has already banked twice**
(`committed_at`'s declared `None`, `distinctive_lines`' silent `()`), arriving through a third
door: not a failed call read as a negative, but a POPULATION excluded at parse time and reported as
an answer.

## Why the obvious fix is not taken here

`comments_are_evidence=True` already exists as a parameter. Flipping it at this call site is one
character and is **wrong without a measurement**: every reformat, every docstring edit and every
`# noqa` churn becomes a distinctive line, and this module's own record says clock-staleness is the
normal resting state of a shared checkout. The 2026-09-22 measurement that settled the clock's
width — 47 of 358 paths, nineteen of them positively vouched — is exactly the shape this needs and
nobody has run it for comments.

**The next lane's job, in this order:**

1. Measure, on the live shared tree, how many tracked-modified `.py` paths gain a `judge` complaint
   when `distinctive_lines` counts comments. Pre-register the count first.
2. If the answer is wide, the remedy is not the flag — it is a THIRD reading that asks only whether
   the copy deletes a comment block the landing ADDED, which is a narrower question than "comments
   are evidence" and does not fire on a reformat.
3. Either way, `refresh_to_head`'s `refused_head_does_not_supersede_it` text must stop asserting
   "deletes no name … an ordinary edit" for a suffix whose comments it never read. An honest
   "this control has no reader for prose inside a `.py` file" is a verdict; the present one is a
   claim.

## What this blocks, concretely

`checkout_drift()` on `/home/rich/synthetic-enterprise` is
`{"behind": 22, "ahead": 0, "contains_origin": false, "gap_paths": 29}` — a pure fast-forward now
that `origin_reconcile` has closed the ahead leg. Ten gap paths are dirty or untracked, and this
one is among the two `.py` copies no door will admit. The other is
`tests/background/test_publish_gate_wedge_draw.py` (`refused_supplies_names_head_lacks`, `prc`),
which is holder work and wants `isolate_hunks`, not this.

**Do NOT close this with `--base-wins`.** That door is admitted only where the stale-copy control
has already returned `predates_landing` or `predates_landing_by_clock`, and the whole finding is
that it returns neither — using it here would be substituting an operator's word for the clock,
which is the one thing that door refuses to be.
