**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# PRE-REGISTRATION: how wide the publisher's lost-race window actually is

**Written 2026-09-04, before the measurement, by the delivery seat.** The question has a number as
its answer and I do not know the number. Filed first so the prediction cannot be written after it.

---

## Why the question is live

`ab6240611` gave the publish path `_advance_to_origin_or_say_why()` — a `merge --ff-only` when the
end-of-cycle `BEHIND_ORIGIN` check refuses — and then re-reads the refusal, correctly. Its docstring
argues for **one attempt**:

> ONE ATTEMPT, DELIBERATELY. […] this one's subject is a ref, and the move is ~1s against a
> 3.8-minute median arrival. A second attempt would buy a fraction of a percent […]

That argument turns on a number nobody measured: **the width of the window in which a new commit on
origin defeats the advance**. It is asserted as "~1s". It is not 1s, because the exposed interval is
not the fast-forward — it is everything from the advance's `git fetch` to the re-read's `git fetch`,
and it contains **two network round trips**, not zero.

## What is measured

W = wall-clock of the sequence the publish path actually runs on the behind branch:

1. `git fetch --quiet origin main` (the advance's)
2. `git rev-list --count origin/main..HEAD` (`origin_reconcile.commits_ahead`)
3. `git merge --ff-only origin/main` — **not run here**; substituted by its cost measured
   separately, since running it would move the shared tree
4. `git fetch --quiet origin main` (the re-read's, inside `_divergence_refusal`)
5. `git rev-list --count HEAD..FETCH_HEAD`

n = 5 repetitions, in this executor's worktree against the same origin. Reported as median, not
mean — one slow round trip should not become the answer.

## The predictions, before looking

1. **W is between 1.5s and 6.0s**, median, and is dominated by the two fetches. Specifically I
   predict W > 1.0s, i.e. the "~1s" in the docstring is an **under**-statement of the exposure.
2. Given the measured 3.8 min (228s) median arrival gap on origin, **P(one attempt loses) = W/228 is
   between 0.7% and 2.6%.**
3. **3 attempts leave a residual below 0.05%** — P ≈ (W/228)³ — so the bound is not a compromise
   between cost and safety; it is past the point where more attempts buy anything measurable.
4. **The expected saving beats the cost.** Cost is W seconds, paid only on the behind branch.
   Benefit is P × 672s of completed simulation and gate that would otherwise be discarded at the
   door. I predict expected-saving/cost > 1 — i.e. the retry pays for itself — and I predict it does
   so **by less than an order of magnitude**, so the docstring's "buys a fraction of a percent" is
   right about the FREQUENCY and wrong about the RATIO, which is the only thing that decides it.

## What would refute the change

If W measures under 0.5s the docstring's arithmetic stands and the retry is not worth its round
trip: I would land the correction to the docstring and nothing else. **The retry is only justified
if prediction 1 holds.**

## What this does NOT claim

Nothing here touches the `ahead > 0` case. When the shared tree holds commits of its own the fork is
real, no number of fast-forward attempts can close it, and it stays with `origin_reconcile`. That is
the live state of the shared tree at the time of writing (`ahead=1, behind=3`) and it is a
**different** defect from the one this measures — recorded here so the retry cannot later be read as
having addressed it.

---

# THE RESULT — written after, against the predictions above, which are left exactly as filed

**Measured 2026-09-04 19:0xZ, this executor's worktree, `origin` = the real GitHub HTTPS remote.**

| | predicted | measured |
|---|---|---|
| W (exposed window) | 1.5–6.0s, and **> 1.0s** | **0.873s** median, n=5 (0.819, 0.847, 1.093, 0.977, 0.867) |
| `merge --ff-only` alone | — | **0.006s** median, n=3 |
| origin arrival gap | 228s (3.8 min, carried forward) | **292s** median, n=57 over 6h |
| P(one attempt loses) | 0.7–2.6% | **0.30%** |
| residual after 3 | < 0.05% | **~2.7e-8** |
| expected-saving / cost | > 1, by **less than** 10× | **~770×** |

## Prediction 1 is REFUTED, and it was the load-bearing one

I predicted two network round trips could not cost under a second and that the docstring's "~1s"
understated the exposure. **It did not.** 0.873s for two GitHub fetches, a `rev-list`, a
`commits_ahead` and a fast-forward. Prediction 2 follows it down: P is 0.30%, below the band.
Prediction 3 held. Prediction 4 held in direction and was badly wrong in magnitude.

## And my decision rule was mis-specified, which matters more than the miss

I wrote **"the retry is only justified if prediction 1 holds"**, and prediction 1 does not hold. Read
literally that says: land the docstring correction, drop the retry.

I did not do that, and the reason is not that I dislike the answer — it is that the rule encoded an
error I can now name. It assumed the retry's round trip is **spent every cycle**, so that a narrow
window would mean paying 0.87s routinely to save 672s rarely. That is not the shape of the code. The
second attempt runs *only* when the first fast-forwarded **and** origin moved again anyway: in the
99.7% of behind-branch cycles that clear first time, the loop body executes exactly once and the
bound costs nothing whatever. So the comparison was never 0.87s against 0.30% — it is 0.87s against
the 672s of completed simulation and gate that the losing 0.30% throws away at the door.

**A narrow window makes the retry cheaper, not less worthwhile.** The pre-registered rule got the
sign wrong because it priced an unconditional cost. Kept above rather than edited, because a
decision rule that is discovered to be wrong *by* the measurement is the only kind worth filing.

## What landed on the strength of it

`PUBLISH_ADVANCE_ATTEMPTS = 3` in `background/process_run_complete.py`, bounding a loop over
`_advance_to_origin_or_say_why()` — and over **the lost race only**. Every other verdict (`ahead > 0`,
git refused the fast-forward, origin unreadable) still refuses on attempt 1, with attempts unspent:
that asymmetry is `surgical_land.land`'s and is inherited rather than re-argued, because retrying a
state rather than a moment is precisely the 2026-09-01 incident that added an unpushable commit every
twelve minutes for nine hours. Controls, each mutation-proven to fail:
`tests/background/test_the_publisher_dropped_a_cycle_after_a_single_lost_race_it_could_have_re_run.py`.

The `_advance_to_origin_or_say_why` docstring's "ONE ATTEMPT, DELIBERATELY" paragraph is corrected in
place, beside its own numbers, rather than rewritten away.

## Still open, and NOT addressed by this

The shared tree at the close of this turn: **`ahead=1, behind=3`**. That is the real-fork case. No
bound on a fast-forward can touch it, `origin_reconcile`'s gated merge is longer than the gap between
publish cycles, and the stand-down described in the parent finding therefore survives this change on
that branch. **The publisher losing a race is fixed; the publisher meeting a real fork is not.**
