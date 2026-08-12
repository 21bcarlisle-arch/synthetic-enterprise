# WORKER FINDING — adding the second error direction is the easy half; its DENOMINATOR is the measure

**Severity:** LATENT · **Lane:** H_harness

**Date:** 2026-08-09 · **Found by:** worker tick building `D11_detection_gap_is_recall_only`
**Advances:** D12_detection_cell_grid_is_recall_only
**Class:** R15 denominator defect · **Status:** caught in-build, before it published

## The mistake, in one line

D11's brief was "copy D7 — two error directions on their own denominators". The first draft did
exactly that, and the second denominator was **wrong**, by a factor of ten.

| draft | false-flag denominator | measured wrongful-dunning rate (seed 7) |
|---|---|---|
| 1 | `universe − truth_set` — "everything that did not fail" | **0.2834** |
| 2 | cases a flag would be **wrong** on | **0.0269** |

Same company, same world, same flagged set. The whole difference is which cases the denominator
was willing to call an error.

## Why the obvious denominator is wrong (observed, R9)

`truth_set` on this triad is `result == 'failed'`. Its complement therefore contains every invoice
that **eventually** succeeded — including one paid three weeks late. But the company's detector
fires at `due + grace`, and at that moment the money genuinely had not arrived. Flagging it was
**correct**.

So `universe − truth_set` charges the company for being right, and it does so in exactly the
direction that makes the new measure look impressive: a large, mostly-blameless denominator produces
a rate that moves dramatically on populations where late payment is common. On the live-run fixture
the split is stark — 900 cases, 347 true failures, **498 late-past-grace**, and only **55** cases a
flag would actually be wrong on. The naive denominator would have been **nine times** the honest one.

## The general shape

> A two-directional metric has **three** populations, not two: must-flag, must-not-flag, and
> **neither**. Anything eventually-resolved, disputed, or unknown is usually in the third. Deriving
> the second population as the complement of the first silently asserts that no third exists.

This is the same family as D6's prevalence normaliser and D7's ageing scalar — a denominator making
a claim its numerator never checked — arriving one dimension later and disguised as the *fix*.

## What was mechanised (not just noticed)

* `detection_measures` takes the negative population **explicitly**. It defaults to the complement
  only when the caller says so, and the default is documented as right *only* when every non-truth
  case is one a flag would be wrong on.
* **The exclusion is published, not silent** (D10's rule, now enforced rather than exhorted): cases
  in neither population are counted in `n_excluded`, the reason travels in `components` all the way
  to the ledger the Proof door reads, and **omitting the reason raises**. An unexplained exclusion is
  the cheapest possible way to make either direction look better than it is.
* The universe is passed as a **set, not a count**. A count cannot notice a flag landing outside the
  scored population — a join-key drift — which would shrink a denominator with nothing firing.
* R15 mutation, in the test suite: collapse the excluded population back into the negatives and the
  measured rate must move **5×**, or the distinction is decorative and the exclusion is a no-op.

## The second lesson, from the same build

`missed_failure_rate` is **0.0000** on every population this repo scores — reconciliation catches
every truly-failed invoice at `due + grace`. That is a real property of this world, not a broken
measure, but **a direction that is always 0 cannot be evidence by observation alone**. It is proven
able to fire by deleting the reconciliation channel, and the residual is registered on D11's own
harden note rather than dressed up: half of this headline is currently carrying the measurement.

The world that would make it move is a world atom. Building one so the metric looks busier would be
the goal-seeking R12 forbids.
