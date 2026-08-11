# H27 Expert Hour #15 — the caveat's number was the BOOK's, on two figures that do not share a resolution

**Date:** 2026-08-11 · **Atom:** `H27_payment_belief_gap` (HARDEN, self-refill draw 2→3)
**Subject:** `tools/couple_w2_11_d5.py` · **Reshape minted as:**
`D33_the_collapse_predicate_is_bit_equality` (L0)
**Held at L2.** Fifteen Hours, fifteen defects, and #15 changed the instrument again.

---

## The lead this took

Hour #14 left three. Lead 2:

> **The step check reached exactly one cell.** `published_step_component` is declared on
> `detection_latency`/recon and nowhere else, because it is the only cell whose reading is
> day-linear either way. The other six moving cells have caveats whose numbers are *bands and
> edges*, and nothing checks those against the published figure the way the step now is.

Asked of the two BELIEF cells, the answer is not "the number is a little off". The number is not
either figure's.

## The finding

`belief_resolution_caveat` publishes `measure_belief_window_resolution`'s
`smallest_visible_shortening_days` — **the BOOK's bound**, `headroom + 1`: the smallest window
shortening that drops any observed failure event out of the company's memory — in the sentence

> "…and the smallest memory error **it** can resolve at all is **310d** of forgetting."

"it" is the figure. The bound is a property of the book and knows nothing about which figure is
reading it, and the same function rendered the sentence **byte-identically on both belief
dimensions** (`score_triad` called it twice with no argument distinguishing them).

Measured through each dimension's own shipped scorer, n=300, seeds 7/11/23, at the 4dp every
consumer renders these gaps at:

| | seed 7 | seed 11 | seed 23 | all-seed |
|---|---|---|---|---|
| **book bound** (what the caveat published) | 310 | 309 | 309 | — |
| `belief` **actually resolves** | 310 | **310** | 309 | **310** |
| `belief_population_mix` **actually resolves** | 310 | **314** | **312** | **314** |

So the sentence is **a day out** on one figure and **five days out** on the other, and two figures
whose measured resolution differs by four days carried one number between them. A reader who sees
either figure unchanged and converts that into "the company's memory is right to within 309 days"
is wrong by up to five days on the mix figure — in the direction that *understates* the
instrument's blindness.

Two things make this the "a lead is not a control" shape rather than an oversight:

* `measure_belief_window_resolution`'s own docstring is careful — shortening by more than the
  headroom *"MAY be visible … whether it is depends on whether the dropped events carry an account
  across a severity tier, **which is the organ's business and not this predictor's**"*. Nobody ever
  asked the organ.
* `DIMENSION_DRIFT_RESOLUTION["belief_population_mix"]["own_why"]` already said this dimension was
  blunter — *"a 310d shortening moves `belief` on all three seeds while moving this one on only
  seed 7"*. Nothing turned that into the number the reader gets.

## And why the register could not have found it: the movement predicate is bit-equality

`_measure_collapse_runs` compares readings with `repr()`, and `measure_own_drift_resolution` with
`!=`. So a difference of **1.4e-17** counts as one counterfactual company being told apart from
another. Measured live: `belief_population_mix` at seed 11 "moves" at drifts −310…−313 by
1.4e-17 — a difference no 4dp consumer can render — which is exactly what put its declared
saturation edge at **−309** where the reader's own precision puts it at **−313**.

That is the D28 fail-open in another costume ("an instrument that has stopped reading, counted as
resolution"), and it is upstream of every declared collapse run and saturation edge in this module.
It is **atom D33** and deliberately NOT changed here: re-deriving those declarations moves edges
across two registers, which is a reshape with real blast radius, not a fix on sight.

## Closed at the class (R10)

* **`number_source` on every moving cell of `PUBLISHED_FIGURE_CAVEAT_CONTRACT`, with its SUBJECT
  checked.** D32 caught one wrong subject with one step check; the general rule is that a caveat
  number's source must be *about the figure it is stamped on*. A `DIMENSION_DRIFT_RESOLUTION`
  source must be keyed to THIS dimension (a register keyed by dimension, pointed at a sibling,
  now fails by name); an `ORGAN_QUERY_GRID` source must `feed` this dimension and owes a
  published-figure number if its `headline_key` names a sub-reading; a `BOOK` source — a
  population-side predictor that *cannot* know which figure reads it — owes a per-figure floor.
  A moving cell with no declared source **RAISES**: the fallback IS the defect.
* **`measure_published_resolution_floor` / `check_published_resolution_floor`** — the per-figure
  floor, measured through each dimension's own shipped scorer on a grid derived from the **BOOK**
  (one day *inside* its own provable bound, where a reading would mean something other than the
  memory window is driving the figure, out by the book's own event span). Exact on the D25/D30
  rule. It also keeps the **bit-equality floor as a declared, measured witness**, and requires
  D33 to own the divergence exactly where the divergence is real — a named owner the sweep cannot
  find is a debt entry outliving its debt, and both directions fire.
* **The epsilon is the reader's own precision, not a tolerance.** Half a step of the 4dp both
  belief gaps are rendered at, and `_consumer_render_decimals` reads that back out of the
  consumers' source (`background/gap_metric.py::format_belief_summary` and the live writer's mix
  line), so a consumer that starts publishing 6dp fails the control instead of leaving the epsilon
  stale.
* **The caveat is corrected AT SOURCE** (the D6/D22 precedent, so it lands on every coupled pair
  calling the scorer): each figure states its OWN floor, names the sibling's *as the sibling's*,
  and the book bound is now stated as what it is — "no memory error smaller than Nd can move ANY
  figure here". `measured_resolution_floor_days` and `book_bound_floor_days` ride beside it as
  **components**, because the ledger writer, the live wiring and the dashboard read `components`
  and never the prose. A caller that will not name a figure gets an explicit **refusal**, never a
  default — a silent default would reinstate the defect.

## R15 both ways

The controls fire, by name, on: the **pre-Hour caveat** (the book bound republished as the figure's
resolution); the **sibling's floor** stamped on the mix figure; a floor the **sentence** never
states (a component contradicting its own prose is not a stamped caveat); a **book-sourced cell
with no floor** (the pre-Hour register state); a number sourced from **another dimension's**
register; a **sub-reading** source with no published number; a **declared floor the sweep
contradicts**; a **predicate divergence with no owner** AND an **owner with no divergence**; an
**undeclared or unmeasured** floor (raises); a moving cell with **no `number_source`** (raises); an
**absent floor sweep** (an unavailable check is a failed check); and an **inert probe** / a **book
with no bound** (both raise).

## R12

**No published number moved.** The detection gap, the latency mean, the ageing measures and both
belief figures are bit-identical before and after (`belief` 0.1518987341772152, mix
0.07999999999999997 at seed 7). What moved is what the instrument admits about itself.

## Why still L2

Fifteen Hours, fifteen defects, none predicted by the Hour before it, and this is again the tick
that changed the instrument — the reputation-of-the-old-instrument problem in its purest form.
Hour #4's stated-in-advance criterion of **two consecutive clean Hours** has still not been
approached.

## Hour #16 leads, in order

1. **The reshape itself is D33 and it is unbuilt.** Every declared collapse run, saturation edge
   and band in `ORGAN_QUERY_GRID` and `DIMENSION_DRIFT_RESOLUTION` is derived at bit-equality.
   `belief_population_mix`'s ceiling is measurably one of the readings that changes (−309 vs
   −313); how many of the other declared edges move at the reader's precision has **not** been
   measured, and until it is, every band in this instrument is a claim about a predicate no
   consumer shares.
2. **The floor check reached the two BOOK-sourced cells.** The four `DIMENSION_DRIFT_RESOLUTION`-
   sourced cells pass the new subject check because their register is keyed by dimension — which
   proves the *source* is about the right figure, **not** that the numbers in their sentences match
   what the published figure does. That is the same coverage question one level further in, and it
   is now the only unasked half of Hour #14's lead 2.
3. **Carried forward, still untaken:** the interior collapses have no owner of their own (Hour
   #11's lead 1, three times deferred); and Hour #8's two — the pinned generated value
   `assert c["n_recon_detected_undated"] == 0`, and whether the other dimensions' normalisation
   notes have the same gap between what they DENY and what they ESTABLISH.
