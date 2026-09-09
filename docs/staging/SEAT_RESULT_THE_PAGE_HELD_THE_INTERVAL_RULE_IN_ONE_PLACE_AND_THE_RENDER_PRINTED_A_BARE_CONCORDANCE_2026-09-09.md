**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — promote-the-09-08b-pair-and-give-the-fixed-horizon-cut-its-own-interval) · **Class:** controls_that_cannot_fail

# RESULT — the interval rule was held upstream only, and the render printed a bare concordance

Grading `docs/staging/records/SEAT_PREREGISTRATION_WHETHER_THE_RENDER_ITSELF_REFUSES_A_BARE_CONCORDANCE_2026-09-09.md`,
written before the probe was run.

The drawn item asked for the fixed-horizon cut's own permutation null and *"a door test keyed to
the property and not to tonight's number: no concordance of any cut renders anywhere on the page
without an interval computed on that cut's own sample."* The null itself was built and landed at
`4e853a83e`; this document is about the second half, and about a defect found while writing it.

---

## The premise, re-measured first — and most of the item was already spent

| the item's deliverable | state on arrival |
|---|---|
| promote the 09-08b pair to the canonical paths | **done.** `value_cycle_ab_s1_three_arm.json` and `..._noise_floor.json` are byte-identical (`md5 77521039…`, `c92ac37a…`) to the `_20260908b` pair |
| regenerate `site/data/value_arms.json` | **done** |
| grade `SEAT_PREREGISTRATION_WHAT_PROMOTING_THE_09_08b_RUN_...` | **done**, in `SEAT_RESULT_THE_09_08b_PAIR_IS_PROMOTED_AND_THE_PAGES_PROSE_WAS_PINNED_TO_THE_RUN_IT_REPLACED_2026-09-09.md` |
| one selection figure, not two | **done** at `77d92e0d1` |
| the survivorship split on the page | **done** |
| a permutation null on the fixed-horizon cut's own n and tie structure | **built** at `4e853a83e`; renders when a run carrying it is promoted |
| **a door test keyed to the property** | **this is the piece that was not there** |

**The item's stated blocker is still real and still in flight.** The 09-09 pair cannot be promoted
until its floor lands: unit `longjob-noise-floor-20260909`, PID 4064918, 50 minutes elapsed at
05:44Z against the 09-08b run's 1h58m. `value_cycle_ab_s1_noise_floor_20260909.json` does not exist
yet. **Nothing here relaunches it.** (The PID the item names, 2900491, is the *09-08b* floor and
finished; its artefact is on disk and promoted.)

## What was found, which was not what the item expected to find

Two controls already held the interval rule, and both name their subject:
`test_the_method_number_never_appears_without_its_interval` (the survivor headline) and
`test_NO_CUT_of_the_bridge_reaches_the_reader_without_the_interval_its_own_n_earns` (the bridge
legs). Both drive the surface **through the producer**, and `_horizon_leg_published` moves a
number to `concordance_withheld` whenever its `null_spread` is absent. So every feed that had ever
reached the door was already refused upstream.

Nothing asked what the *render* does with a leg the producer did not refuse. It does this:

```
0.4210   no interval on this cut’s own n   161   every decision the arm priced, in pounds
```

`fixedHorizonBlock`'s `row()` set `figure` from the concordance alone and gated its withheld
branch on `c === null`. Its own comment read *"A leg with a number and no interval cannot occur —
the row above withholds the number"*. That was a true statement about `_horizon_leg_published` and
was never a statement about `row()`. **The property was held in exactly one place, upstream, and
the page inherited it** — the arrangement that ends with a lane relaxing the producer and nothing
going red.

## The three predictions, graded

| | Predicted | Measured | |
|---|---|---|---|
| **P1** | the render prints the number to 4dp with an amber "no interval" cell; the figure reaches the reader | printed `0.4210` beside `no interval on this cut’s own n` | **CONFIRMED** |
| **P2** | neither existing door test fires on that feed | both **green** on the unrepaired render | **CONFIRMED** |
| **P3 — will not move** | the live page is byte-identical | render sha `bcfbdc058e1ee7e3` before and after, identical | **CONFIRMED** |

P3 was independent rather than merely conceptually separate, and the reason it holds is worth
keeping: the live feed's `fixed_horizon` is `available: false, withheld: true`, because the
promoted 09-08b artefact predates the per-leg spread. `fixedHorizonBlock` returns before reaching
`row()`. **The repair changes no rendered byte today and takes effect the moment the 09-09 pair
promotes** — which is the correct order, since that is the run that first puts four intervals on
this table.

## The repair, and the control that holds it

**The surface refuses it too.** `row()` gains a branch: a leg with a number and no interval renders
`withheld` with its reason, on the same fail-closed shape the producer uses. The producer's refusal
stays — it is right, and it is not enough on its own.

**`test_NO_cut_ANYWHERE_in_the_feed_renders_its_number_without_its_OWN_interval`.** Two things make
it more than a third copy of the controls above it:

* **The cuts are discovered, not named.** It walks the feed for every block carrying a
  `concordance`, so a cut losing its interval fires without the test being edited.
* **The subject bypasses the producer**, which is an input `_skill_fixed_horizon` cannot emit and
  the bridge control therefore cannot construct.

**Mutation-proven both ways**: red against the unrepaired render on the poison assertion, green
against the repaired one, and the full 112-test door suite passes.

### Two things the first draft got wrong, kept here because they are the useful part

**1. `concordance` names two different quantities in this feed.** The walker collected
`what_it_could_have_detected.floor[]` and demanded an interval for each. A floor row is the effect
size you would *need*, paired with `decisions_needed` — a requirement, not a measurement, with no
sample to compute an interval on. This is the project's own shape: *one reader over a
heterogeneous field reads blind*.

The discrimination is on the **sample**, not the path: a measured cut carries the n it was computed
over (`decisions`, or `decisions_scored`); a hypothetical carries `decisions_needed`. Censused: **6
measured, 12 hypothetical, nothing in neither class.** Because a narrowing that kills a false
positive can only hide things, this one **fails rather than skips** on a block fitting neither
shape — that is the branch a future block arrives on.

**2. The render is NOT generic over `legs`, and the docstring claimed it was.** It names its four
rows in four `row(...)` calls. The first poison round injected a leg under a *new* name, which
rendered nothing and went **green against the unrepaired page** — a control that would have shipped
proving nothing. The poison now strips the interval from a leg the page actually draws, and its
value is asserted absent from the clean render first so a hit is attributable to the poison.
The docstring now states the limit rather than the claim: a leg added under a new name reaches no
reader and is not covered until a `row()` call draws it.

## What is next

1. **When `value_cycle_ab_s1_noise_floor_20260909.json` lands, promote the 09-09 pair** to the
   canonical paths and regenerate `site/data/value_arms.json`. That is when the fixed-horizon
   concordance and its own bound reach the reader, and when this repair first changes a rendered
   byte. **Check the artefact and the unit before relaunching anything.**
2. The estimand that then publishes is **0.4210 on 161 decisions, below its own 95% null
   [0.4458, 0.5540] at p = 0.0045** — graded in
   `SEAT_RESULT_THE_FIXED_HORIZON_CUT_IS_BELOW_ITS_OWN_NULL_AND_THE_CONTROL_LEG_AGREED_TOO_EXACTLY_2026-09-09.md`,
   whose own honest limit — the permutation treats 161 clustered decisions as exchangeable, so the
   true interval is wider — renders with the figure.
3. `fixedHorizonBlock` naming its four legs is a live limit, not a defect today: the producer emits
   exactly those four. It becomes one the day a fifth leg is added, and the control's docstring is
   where that is written down.
