**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `land-the-nine-seed-floor-by-the-three-pointer-recipe-and-own-it-to-the-rendered-selection-leg`) · **Class:** controls_that_cannot_fail

**Subject:** `site/test_the_baseline_comparison_reaches_the_reader.py::_measured_cuts_only` and
`::test_NO_cut_ANYWHERE_in_the_feed_renders_its_number_without_its_OWN_interval`;
the `decisions` field `tools/run_value_cycle_ab.py` writes onto each `pair_strata` stratum.

# FINDING — the decomposition class's reachability leg cannot pass, because every stratum carries a `decisions` count it was not measured over

**Red at `HEAD` and at `origin/main`, and it blocks every lane.** Found while landing the
leg-conditioning promote; it is not that item's subject and it refuses that item's commit, which is
why it is filed rather than folded in.

```
site/test_the_baseline_comparison_reaches_the_reader.py::
test_NO_cut_ANYWHERE_in_the_feed_renders_its_number_without_its_OWN_interval
E  AssertionError: no decomposition term reached the reader, so the obligation above proved nothing
E  assert 0 >= 1
```

## It is not mine, proven rather than asserted

The test builds its subject from `_fh_book()` — a synthetic four-decision fixture — so it never
reads the live feed and no promote can move it. Proven anyway by swapping bytes, because "it uses a
fixture" is an argument and the swap is a measurement:

| tree state | result |
|---|---|
| working tree, `THREE_ARM_PATH` = `09-09c` | FAILED, `assert 0 >= 1` |
| `HEAD` bytes restored on both paths | FAILED, `assert 0 >= 1` |

`git diff --stat HEAD origin/main -- site/` is empty, so `origin/main` is red in the same line.
Introduced by `39065da9d`. It is in **neither** `HEAD_RED_REGISTER.md` nor
`PUBLISH_STANDING_RED_REGISTER.md`.

## The defect

`_measured_cuts_only` sorts every block carrying a `concordance` into three classes, and its own
docstring states the discrimination:

> `decisions` is tested FIRST, because a bridge leg carries both an n and its pair counts and it is
> a measured cut — **the decomposition class is the one with pairs and no sample.**

```python
_SAMPLE_KEYS        = ("decisions", "decisions_scored")
_DECOMPOSITION_KEYS = ("comparable_pairs", "decision_pairs")
```

Every stratum carries **both**. Measured on the fixture the control actually runs against:

```
measured: 10   hypothetical: 12   decomposition: 0
  within_settled  decisions=True  comparable_pairs=True
  within_zero     decisions=True  comparable_pairs=True
  cross           decisions=True  comparable_pairs=True
DECOMPOSITION members: []
```

So the class has **no members by construction**, and `assert strata_on_the_page >= 1` — the leg that
exists to prove the loop above it is not vacuous — cannot pass while the producer emits `decisions`
on a stratum. This is the reachability shape CLAUDE.md names: *a guard that refuses everything
passes every test of whether it refuses correctly.* Here it is the inverse and worse — the control
correctly refuses to be vacuous, and the thing it guards has been emptied out from under it.

## The half that is a real defect in the payload, not in the control

The tempting read is "the control is stale, widen it". That is the narrowing-that-only-hides shape.
The classifier is asking the right question and **the feed is answering it wrongly**: `decisions` on
a stratum is not the sample its concordance was measured over. Measured on the live feed:

```
estimand decisions_scored = 161      comparable_pairs = 12194
  within_settled  decisions=124  comparable_pairs=7606  concordance=0.5130
  within_zero     decisions= 37  comparable_pairs=   0  concordance=None
  cross           decisions=161  comparable_pairs=4588  concordance=0.2686
```

**124 + 37 + 161 = 322, against an estimand of 161.** The strata partition *pairs* (7,606 + 0 +
4,588 = 12,194 — exact), not decisions; a decision participates in more than one stratum, and
`cross` carries the whole 161 because every decision is on one side or the other of a cross pair.
So a stratum's `decisions` is a *participation count*, and the number its concordance was actually
computed over is `comparable_pairs`. A field named for the sample, that is not the sample, is what
put three decomposition terms into the measured class.

This is the same shape as the rule directly above it in CLAUDE.md — *before dividing two numbers,
say out loud what each one counts* — reached one step earlier, at the point where a count is named.

## Why this is BLOCKING and not LATENT

It is a red at `origin/main` in the site lane, and the site lane's reds refuse **every** lane's
commit, not this one's. Nothing on the published page is wrong because of it — the payload is
correct and the strata render correctly — but no lane can land while it stands.

## What is next, and what must NOT be done

1. **Do not relax `assert strata_on_the_page >= 1` and do not add `decisions` to an exception
   list.** The leg is correct; a control keyed to the property is exactly what this one is, and
   deleting it because the class went empty is how a partition stops being covered.
2. The candidate repair is at the **producer**: a stratum's block should not carry a key from
   `_SAMPLE_KEYS` when the concordance was not computed over it — either rename it to what it counts
   (`decisions_participating`) or drop it, since `comparable_pairs` is already the stratum's n and
   is what `_stratum_figure` and the composed sentence both quote.
3. Whichever is chosen, it needs a **poison round before the mutation battery**: assert the
   decomposition class can be non-empty *and* that a stratum wrongly typed as measured still fails,
   because "0 decomposition terms" and "the probe cannot see them" read identically today.
4. Re-measure the three strata against `_measured_cuts_only` after the repair — `within_zero`
   carries `comparable_pairs = 0` and `concordance = None`, so it will exercise a different branch
   from the other two and should be checked separately rather than assumed to follow them.

I did not make the repair: it is a producer change to a block another lane landed this morning
(`2df665040`), it needs the poison round above, and the promote it was blocking is independent of
it.
