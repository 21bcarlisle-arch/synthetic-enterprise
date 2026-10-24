**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Estimate the cost of work to come, forecast the backlog in weeks, and learn from the misses (2026-10-24)

**Type:** STEER, through the advisor channel. The director's words, from chat on Sat 24 Oct:

- 11:09 BST: "Ok. So how.much.work has it got to do lined up and in backlog? Do we estimate the token cost of work to come?"
- 11:13 BST, on the advisor's proposal below: "Yes"

## What the advisor told him (origin, 24 Oct)

**The backlog, as it stands:**
- **Advisor queue:** five director steers.
- **Open work:** 106 open atoms with 218 level-steps outstanding. 98 of those steps are world lanes. 44 atoms are in build, 5 in harden and 57 idle. 265 atoms have closed since June.
- **Staging:** 110 files at the root (68 seat, 40 worker), 36 in progress (15 of them director documents), and 27 console files.
- **Owed:** 11 items still open on the owed list.

**What is measured today:** only backward cost. `tick_burn_rate --routes` gives USD per landed result by route, and a point costs about USD 10. Nothing forecasts the cost of queued work.

**The tier, measured against what was used:**
- The new tier gives about 88 points a week at about USD 10 each, roughly USD 880.
- Last week's actual spend was about USD 1,000.
- So the cut against real use is about 10–15%, consistent with your own 1.3–1.7 times.

## What to build (his "Yes")

1. **A cost estimate on every drawable item.** Cover atoms, direction items, advisor files and open findings. Give it in usage points with a range, taken from your own measured history for that kind of work: a site page, a K8 page, a world rebuild, a pre-registered grading run, a supplier build, a fix of a class. Keep the classes few and named. Where the history is thin, say so and use a wide range, not a guess.
2. **A rolling forecast, at every publish and every relayed reading:**
   - what the rest of this week can afford;
   - what in the priority order fits and what does not;
   - the backlog's size in weeks at the current allowance;
   - which large items should be split before they start.

   Show it in the stretch log and in the pace section of How it's built, in plain words.
3. **Learn from the misses.** When an item lands, record its actual cost beside its estimate. Report the error by work class each week, and refit the class costs. An estimate that runs badly wrong is a finding.
4. **Draw with cost in view, within the priority order** (P1, P3). Priority stays the director's and comes first:
   - if two items are of equal value, take the cheaper one;
   - flag any item expected to take more than about 10% of a week before it starts;
   - if something expensive is drawn and can't finish in the week, split it, or say plainly why not.

   This is sequencing, not a change to what matters (P8).
5. **Keep it cheap.** The estimator runs as a script on records you already keep. It must cost a negligible share of the week it forecasts.

## Report

One stretch-log entry with:
- the work classes, their fitted costs and how good the fits are;
- the first forecast: the backlog in weeks, and what fits next week;
- the first estimate-against-actual comparison as items land.

— Director steer, 24 Oct 2026, his words above; the proposal summarised as he read it; drafting is the advisor's.
