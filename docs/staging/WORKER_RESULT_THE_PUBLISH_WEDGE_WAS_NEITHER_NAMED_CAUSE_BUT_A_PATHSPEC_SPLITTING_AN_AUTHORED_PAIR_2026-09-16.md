**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the publisher has published nothing in 140 hours and 30 consecutive attempts)

# The publish wedge was neither of the two named causes: a publish pathspec swept half of an authored pair and reded the half it left behind

**2026-09-16, scheduled tick, worker seat.** The item named two causes and asked which one released
the wedge. The answer is neither: both were already gone when the turn opened, and the live cause
was a third one nothing in the draw described. The wedge is 146 hours and 34 consecutive failures.

## The two named causes were both dead on arrival

The draw is a set of un-re-asked predictions about the tree, and both of its factual claims had
expired:

| named cause | the draw's claim | measured at turn start |
|---|---|---|
| the fork | "HEAD is one commit ahead of `origin/main`" | **0 ahead, 3 behind.** No fork. A plain fast-forward, and `origin_reconcile` has nothing to reconcile. |
| the orphan ratchet | "that path is dirty in the working tree right now" | **`docs/design/orphan_baseline.json` is clean.** `git status --porcelain` on it returns nothing. |

So neither prescribed remedy — `background.origin_reconcile`, a re-freeze from a clean HEAD extract
— had a subject. Running either would have been work against a premise that had already been
discharged by another lane.

## What was actually holding it

The state file names one red and says, correctly and in its own words, that it cannot attribute it:

    "blocking_tests": ["FAILED site/knowledge/test_index_reflects_the_record.py::test_the_card_copy_is_quoted_from_the_record"]
    "red_at_head": "not_established"
    "red_at_head_reason": "the red was measured at git=dbd92cedc and HEAD is now git=c2d8ac167"

That honesty is the mechanism landed in `7a9e4c117` working exactly as intended, and it is what made
this turn cheap. The three-tree measurement:

| tree | result |
|---|---|
| shared working tree | **GREEN** — 1 passed |
| clean `git archive HEAD` extract | **GREEN** — 12 passed, whole file |
| HEAD extract **+ the working tree's `site/data/knowledge_wholesale.json` only** | **RED** — `carbon-price card blurb ... != record ...`, the exact recorded node id |

The red exists in no tree anybody looks at. It exists only in the tree the publish commit
*constructs*, and it is a **split pair**.

Two files in the working tree hold one piece of finished, internally consistent knowledge work:

- `site/data/knowledge_wholesale.json` — four `reviewed` records filled in with sources and dates,
  and the carbon-price `blurb`/`scope` corrected (CPS is levied per unit of **fuel** inside the
  Climate Change Levy, not per tonne emitted).
- `site/knowledge/index.html` — the carbon-price card blurb, updated to quote the corrected record.

The test's COPY leg grades exactly this: the card blurb must be quoted from the record. The pair
agrees at HEAD and agrees in the working tree. It disagrees only when something takes one side and
not the other — and the publisher does precisely that, as its own comment at
`background/process_run_complete.py:276` states:

> Because a publish stages `site/data/**`, `site_lane_gate` takes its BROAD branch …

`site/data/knowledge_wholesale.json` is under `site/data/**`; `site/knowledge/index.html` is not. So
every publish cycle sweeps the working-tree copy of the feed into its candidate tree, leaves HEAD's
stale index beside it, and reds on the mismatch it just manufactured. It is not a flake and it does
not decay: the same node id, every cycle, 34 times.

**A pathspec stages the working-tree copy** — the rule that protects other lanes' *files* is the
same rule that splits another lane's *pair* when only one side falls inside the glob.

## The attribution, from mtimes nobody had looked at

    wedge_since               1789011039
    site/knowledge/index.html 1789004805   (1.73h BEFORE the wedge opened)
    knowledge_wholesale.json  1789012589   (0.43h AFTER it opened)

Neither file has been touched in the 146 hours since. This is not a lane mid-edit that would have
cleared itself; it is finished work stranded half-visible, and the wedge began the moment the second
half of it hit the disk.

## The repair

Land the pair. With both committed, HEAD's index quotes the corrected record, and the publish
pathspec may go on sweeping the feed because there is no longer a stale side to leave behind.

Measured before landing, in a clean HEAD extract with **both** working copies applied:
`site/knowledge/` — **126 passed**.

No control was added and no watchdog was built. The item asked for that restraint explicitly and it
is the right call: the class already has a register (`CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md`),
and what this instance wanted was two files committed.

## What is worth generalising, and what is not

Not worth a new mechanism: the split-pair shape is a special case of a rule this repo already knows
and states in `CLAUDE.md`.

Worth recording, because it inverts that rule's usual reading: a pathspec is normally described as
the thing that stops you sweeping other lanes' work. Here the pathspec swept *part* of another
lane's work and the damage was done by the part it **left**. A glob that cuts through a
consistency-checked pair is a wedge generator, and the cut is invisible from both endpoints — which
is why six days of `red_at_head: not_established` could not name it and a three-tree measurement
could.
