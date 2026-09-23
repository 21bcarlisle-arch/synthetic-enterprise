**Severity:** ADVISORY · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
**Class:** `publish_gate_and_wedge`

# Pre-registration: how is a derived artefact's producer OBSERVED rather than declared?

**Claim:** `the-regeneration-check-clones-at-head-so-it-cannot-see-the-producer-edit-that-wedges-the-publisher`
**Written before the measurement.** The answers below are not known to me when I write this.

## Why there is a question at all

`SEAT_RESULT_THE_REMEDY_A_LIVE_CONTINUATION_NAMES_WOULD_HAVE_BEEN_GREEN…_2026-09-23.md` (landed
`be6b67b98`) refuted this item's own filed remedy and specified the replacement: a second relation
kind — *a derived artefact whose producer is NEWER than it, anywhere in the tree, working-tree
standpoint.* It did not say how the (producer, artefact) PAIR is to be found, and that is the whole
design. `published_feed_regeneration_check` states its own rule for the relation it already has:

> WHICH FEED A GENERATOR OWNS IS OBSERVED, NEVER DECLARED. […] A feed→generator table written down
> here would go stale the first time a generator learned to write a second feed, and it would go
> stale silently.

It observes by RUNNING the generator in a clone and reading what changed. For this second relation
that route is unavailable: running 100+ producers is not a commit-time control, and the artefacts
are not confined to `site/data`. So the pair must be observed some other way, or declared — and if
declared, the module's own stated defect applies to it.

Two candidate routes, and I do not yet know which is right:

* **STEM CONVENTION** — `tools/<x>.py` ↔ `docs/observability/<x>.json`. Cheap. Already measured at
  **20 pairs** (that measurement is done and is not what this prereg covers).
* **PATH LITERAL** — walk each `tools/*.py` for a `Path` expression that resolves under
  `docs/observability/`, e.g. `PROJECT / "docs" / "observability" / "<name>.json"`. Observes what
  the module actually writes; needs an AST walk over `/` chains, not a string grep.

## Predictions

**P1.** The path-literal route finds **more** pairs than the stem convention's 20.

**P2.** The path-literal route finds at least one pair the stem convention **cannot** find — an
artefact whose name differs from its producer's module name. If P2 is false the stem convention is
sufficient and the AST walk is unjustified complexity.

**P3.** The stem convention produces at least one pair the path-literal route does **not** confirm —
a same-stem coincidence where the tool does not write that artefact. If P3 is true, the stem
convention is not merely incomplete but **wrong**, and a control built on it would name an innocent
file.

**P4.** Measured in the SHARED tree right now, the content leg (producer differs from HEAD ∧
artefact identical to HEAD) reports **zero** stale pairs — because the instance this item was
raised for was discharged there at 09:04 (intermediate now NEWER than the 07:25 producer edit).
A first leg keyed to today's instance would therefore already be unmutatable, which is the trap
`be6b67b98` named and this prereg exists to avoid walking into.

## What the answers change

If P1 ∧ P2 hold, the pair is observed from the producer's source and the stem convention is not
used. If P2 is false, the convention is enough and I build the cheaper thing. If P3 holds, the
convention is disqualified regardless of P1/P2. P4 governs how the control's own test is keyed:
zero live instances means the failing case must be CONSTRUCTED in a fixture, never harvested.
