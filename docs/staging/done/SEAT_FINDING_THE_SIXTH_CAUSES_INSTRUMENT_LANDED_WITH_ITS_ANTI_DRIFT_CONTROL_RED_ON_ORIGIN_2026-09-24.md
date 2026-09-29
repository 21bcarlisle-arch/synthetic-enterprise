**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# FINDING — the sixth publish cause landed with its own anti-drift control RED on origin/main, and the item that would have unblocked the checkout would have REVERTED it

Drawn as
`the-checkout-fast-forward-is-blocked-on-two-contested-files-not-on-a-judgement`.

## The premise, re-measured at draw — MOVED, and the item's instruction inverts

The item's two cited commits (`90d42eb21`, `9cc23ad81`) are ancestors of `origin/main`: the
measurement landed. The instruction built on it did not survive re-measurement.

| The item said | Measured 2026-09-24 on the shared tree |
|---|---|
| shared tree is `ahead=0`, a PURE FAST-FORWARD | `3 ahead, 11 behind` — a genuine fork, not a FF |
| 12 gap paths, 2 of them dirty | **19** gap paths, **3** dirty |
| land the two dirty copies with `surgical_land --content` | that would **revert** the trunk |

The third contested gap path is `background/delivery_lane.py`, which the item does not name.

### `surgical_land --content` on those bytes REVERTS the very instrument the item wants present

The item's stated aim is that "the sixth-cause instrument (`EXIT_SCOPED_GATE_REFUSED` /
`scoped_suite_red` / `scoped_gate_unjudged`) is present for the first time". That instrument is
`"scoped_gate_unjudged"` in `supervisor.WEDGE_KINDS_NO_TEST_JUDGED`, added by the cited commits —
i.e. **it is already on origin/main**. The shared tree's dirty copy of `background/supervisor.py`
forked from a HEAD that predates it, so the copy does **not** contain it:

```
$ grep -c scoped_gate_unjudged  origin/main:background/supervisor.py   -> 1
$ grep -c scoped_gate_unjudged  <shared working copy>                  -> 0
```

`--content` lands bytes without reading the file. Walking that door would have deleted the
instrument in the same commit that claimed to install it. This is the base caveat the draw itself
printed — *"a copy the trunk ALREADY supersedes reads as HOLDER WORK"* — landing on a real case:
the holder-work reading was computed against a HEAD 11 commits behind, and the door it named was
the wrong one.

**The right door was a 3-way merge**, base = the blob the lane forked from, ours = `origin/main`,
theirs = the shared working copy. It merged clean (`rc=0`, no conflict), and the result is
`origin/main` + the lane's hunks — both facts kept.

### `site/test_the_book_is_bounded_by_compute_reaches_the_reader.py` — the ask is SPENT

That copy is **byte-identical to `origin/main`**. It is "dirty" only because the shared checkout
is 11 behind; there is nothing in it to land, and nothing would be lost by advancing it. The
item's third named path, `background/process_run_complete.py`, the draw already graded spent.

## THE FINDING — a standing red on origin/main, on the publish path, that nobody's copy fixes

Running the trunk's own controls against the merged file surfaced **one** failure, and it is
**pre-existing at pristine `origin/main`** — proven by the one-variable control (restore
`origin/main:background/supervisor.py`, run the single test, same red in 0.13s):

```
test_the_publishers_kinds_and_the_supervisors_set_have_not_drifted
  `scoped_gate_unjudged` is no longer written by the publisher -- this set is
  describing a producer that has moved.
```

It is not describing a producer that has moved. The producer passes it. The **reader** could not
see the spelling it was passed in. `_kinds_written_by` resolved a `kind=` argument only as a
string literal or as a module-level `NAME = "literal"` binding, and the sixth cause arrived in
neither shape:

* `SCOPED_GATE_UNJUDGED_KIND = publish_cause.SCOPED_GATE_UNJUDGED` — an **alias** to a constant in
  the module both readers share, so the publisher and the supervisor cannot disagree about the
  spelling. Not a literal.
* `kind="test_regression" if judged else SCOPED_GATE_UNJUDGED_KIND` — reached through a
  **conditional**. Not a bare argument.

**This is the same defect the function's own docstring records itself acquiring on 2026-09-17**,
one spelling further out. That time it was a text grep blind to a named constant; this time an
AST walk blind to an alias and a ternary. Both times the control punished the producer for being
written the way this repository asks.

### And the fix sitting uncommitted on the shared tree does NOT close it

The shared tree carries an in-place rewrite of this control (+97/−66) which replaces the resolver
with a `getattr(prc, ...)` lookup. Measured by applying that copy and running the one test: **it
still fails** — it resolves the alias but is equally blind to the conditional. So the red is
unfixed everywhere, and landing the lane's rewrite would not have cleared it. That rewrite also
**deletes** `test_the_kind_reader_sees_a_named_constant_and_not_only_a_literal`, the leg that
fails if the resolver reverts to a grep.

### Why this is BLOCKING and not LATENT

A red in this file holds the publish gate shut. The sixth cause exists to stop a publish outage
being misread as `test_regression` — and it arrived by making the publish gate red through its
own control instead. Every publish repair that ships stays inert while it stands, which is
exactly the condition the drawn item's WHY describes, arriving by a route the item did not name.

## What landed

`_kinds_written_by` now understands **two more spellings and exactly two**: a module-level
`NAME = other.ATTR` alias, followed **one hop, statically**, into `other.py` beside the module (no
import — importing a daemon to read a label is a side effect for a string); and a `kind=` whose
value is a conditional, which contributes **both** branches. Everything else still resolves to
nothing and the caller's assertion still FAILS: the widening is of the spellings understood, never
of where they are looked for.

**Three mutations, each run, each biting:**

| Mutation | Reds |
|---|---|
| drop the `ast.IfExp` branch | the drift control **and** the new conditional/alias leg |
| drop the alias hop (`consts.setdefault`) | the drift control **and** the new conditional/alias leg |
| answer with what the module **defines** (`consts.values()`) rather than what it **passes** | the drift control, the named-constant leg, **and** the new negative leg |

The third is the one that matters: it is the shape a widening rots into, and
`test_the_kind_reader_still_refuses_a_kind_the_publisher_never_passes` exists to catch it. Its two
negatives are `scoped_suite_red` (a real constant reached for by name *in the very call that
passes the sixth kind*, never passed as a kind, because where a test really was judged red the
publisher passes `test_regression`) and `PUBLISH_GATE_ITEM_ID` (a module-level string literal
sitting in the resolver's own constants table, one careless line from being returned, and not a
kind at all). Each leg guards its own premise and says so rather than passing vacuously if the
producer's spelling changes.

Landed beside it, from the same 3-way merge: the other lane's **single implementation of the pass
ceiling** (`supervisor._under_pass_ceiling`), which the director's 2026-08-19 ruling needed and
which until now was enforced only in `_idle_discover_frame_draw` — *a function no production path
calls*. Lane 3 draws through `_idle_discover_frame_draw_concurrent`, which consulted no ceiling at
all. Its two controls came with it and are written over the **partition** (both entry points,
parametrised) rather than over the one member the original was written against. 64 green.

## What is NOT closed, and who carries it

The checkout still cannot fast-forward. Three gap paths remain dirty on the shared tree:

1. `background/supervisor.py` — residue is now **one** subject, not two: the lane's revert of
   `shared_tree_live_record(...)` on `_publish_gate_wedge_active`'s two reads. It is coupled to
   the unfinished control rewrite above and is **its author's to land**, not mine to guess at. Not
   landed here on purpose: a half-understood revert of a live publish-path read is the shape
   CLAUDE.md names as the short-term fix that comes undone when it meets the rest of the system.
2. `background/delivery_lane.py` — needs the same 3-way merge treatment (working copy is HEAD+151,
   trunk added ~61 lines it lacks). This is the subject of the live continuation
   `ask-the-landed-unbound-join-before-the-draw-not-only-after-the-sweep`.
3. `site/test_the_book_is_bounded_by_compute_reaches_the_reader.py` — **nothing to land**;
   identical to `origin/main`. It blocks the FF nominally and costs nothing to advance.

The supervisor was **not** restarted, per the item's own ordering and for the recorded reason:
restarting before the checkout advances makes the drift detector agree with itself and hides the
gap.

## The generalisation

**A draw's path verdicts are computed against a base the trunk may have moved past, and the
holder-work reading inverts when it has.** `dirty` is a claim about *HEAD*, and when HEAD is 11
behind, a copy the trunk already supersedes reads as work to land — and the door that reading
names (`--content`) is precisely the one that would land it *over* the trunk. The draw prints this
caveat. It is not decoration: here it separated "install the instrument" from "delete the
instrument", and the two were the same command.
