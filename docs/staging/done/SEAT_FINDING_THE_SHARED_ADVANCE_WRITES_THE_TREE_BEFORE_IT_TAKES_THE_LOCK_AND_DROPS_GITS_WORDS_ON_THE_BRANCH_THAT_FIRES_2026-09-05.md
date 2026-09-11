**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# FINDING: the shared advance writes the tree before it takes the lock, and drops git's own words on the one refusal branch that actually fires

**Measured 2026-09-05, delivery seat, from an isolated worktree at `origin/main` = `ac29c832e`.
Found while making `process_run_complete._advance_to_origin_or_say_why` a CALLER of
`origin_reconcile.advance_shared_tree` instead of a second hand-rolled copy of it — the Lane 0
direction. Both defects belong to the helper, not to the caller, and neither was visible from
either side alone.**

---

## One: the removal is under the lock and the fast-forward that precedes it is not

`advance_shared_tree`'s own docstring states the property, and it is right about the leg it
describes:

> THE REMOVAL AND THE ADVANCE ARE UNDER ONE TREE LOCK. Between them the tree is missing files it
> is about to be given back; another writer landing in that window would see a tree that never
> legitimately existed.

The lock is taken at `background/origin_reconcile.py:320`. The **first** `_ff()` — line 279, the
one that runs on every call and succeeds on every clean cadence — is above it. So the ordinary,
overwhelmingly common path (`{"advanced": True, "cleared": []}`, "fast-forwarded onto origin/main
with nothing in the way") writes the shared working tree with no lock held at all.

That is not a smaller window than the one the docstring guards. A fast-forward rewrites every
tracked path this tree has not modified — the same act the removal leg is locked *for* — and it
runs on the deadman cadence every five minutes against a tree CLAUDE.md says routinely has three
lanes with uncommitted work in it.

**Why it has not bitten yet, and why that is not reassurance.** `git merge --ff-only` refuses on
any path a local writer has modified, so the collision that would corrupt something is mostly
refused by git rather than serialised by us. Mostly: git's refusal is computed from the index at
the moment the merge starts, and a writer that stages between that read and the checkout is
exactly what the lock exists to exclude. This is a fail-open guard whose apparent success is
supplied by a *different* mechanism — the shape this repo has a catalogue for.

**Not repaired here, and the reason is scope, not doubt.** The publish path's own control
(`test_the_advance_writes_the_shared_tree_under_the_tree_lock`) demands the merge be under the
lock, so the caller I landed today takes `tree_lock()` across the whole call and passes
`locker=nullcontext` in — the helper's own seam for "the caller holds it". That closes the window
for the publisher and leaves it open for `reconcile`'s two call sites
(`origin_reconcile.py:587`, `:628`), which are another lane's live daemon path and not something to
change in the same turn that changed the caller. **The remedy is one line**: hoist `first = _ff()`
inside the `with _lock():` block, keeping `_lock` defaulted for those two callers.

## Two: five refusal branches, two of them quote git, and the one a dirty tree takes is not among them

`advance_shared_tree` returns a `reason` on five distinct refusals. Only two carry git's own
stdout/stderr:

| branch | quotes git |
|---|---|
| blockers unreadable | no |
| nothing local collides | **yes** |
| twins unreadable | no |
| *N of M blocking paths are NOT byte-identical* | **no** |
| twins removed and git still refused | **yes** |

The fourth row is the one that fires on a shared tree with an `FF_MODIFIED` path, which is the
ordinary wedge — measured on this tree 2026-09-04/05: nine advance attempts, zero fires, every one
of them refused by a tracked file a lane was holding.

**This was caught by a control, in the intended direction.** The first draft of the caller built
its refusal from the helper's `reason` alone, and
`test_the_refusal_names_the_path_the_remedy_and_gits_own_words` went red on `"overwritten" in
reason` — git's words are the ground truth the verdict is *derived from*, so a refusal that
replaces them with the derivation is unfalsifiable. The caller now keeps the merge's own
`CompletedProcess` and quotes it itself, which is stronger than depending on the helper: it cannot
be lost again by a branch added inside the helper later.

**The helper's own readers still lose it.** The reconciler's log line on that branch names the held
paths and nothing else. **Remedy**: carry `(first.stderr or first.stdout)` on all five, as two of
them already do.

---

## Disposition

Both are LATENT: nothing published is invalidated, and no control's verdict is wrong — the
publisher's two exposures are closed at the caller as of `ac29c832e` and the commit that follows
it. What remains open is `reconcile`'s two call sites for **One**, and every reader of the
reconciler's log for **Two**.

Neither was findable from one side. The lock gap reads as satisfied from inside the helper (its
docstring describes the leg it does guard) and as satisfied from outside (there is a `tree_lock`
in there). It became visible only in composing them, when the caller had to decide where its own
lock went — which is the seat-level interconnection review CLAUDE.md says a bounded tick cannot
do, arriving on exactly the schedule that argument predicts.
