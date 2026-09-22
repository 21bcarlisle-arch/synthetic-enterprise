**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, claim `a-published-site-feed-is-never-compared-against-what-its-generator-would-produce`

# Only eight of sixty-one published feeds can be reproduced from their commit, and no second hand-edit exists

*The class control the SLC-27B finding asked for is built and landed. The measurement it was built
to make refutes two of my own pre-registered predictions and the drawn item's literal design.
Pre-registration, written before the first extract:
`SEAT_PREREG_WHAT_A_REGENERATE_AND_COMPARE_CONTROL_WILL_FIND_ACROSS_THE_PUBLISHED_FEEDS_2026-09-19.md`.*

---

## What was asked, and why it could not be built as written

The item: *regenerate every `site/data/*.json` into a temp location, compare each against the
committed bytes ignoring only the timestamp keys, land it red-if-divergent.*

Built exactly that way it reds **24 of the 31 feeds that run**, on the day it lands. Almost none of
those 24 is a hand-edit. They diverge because the feed is not a function of its commit at all:

| why it diverges | feeds |
|---|---|
| live git log / HEAD identity | `phases.json` (commit count), `evidence.json` (hash), `capabilities_door.json`, `value_arms.json` |
| live staging directory | `method.json`, `system_status.json`, `delivery.json`, `decisions.json` |
| gitignored cache | `sim_data.json` (regenerates to **zero** records), `market.json`, `explore_carbon.json` |
| a run artefact | `dashboard.json`, `supplier.json`, `margin_bridge.json`, `customer_sample.json`, `proof.json`, `customers.json` |

A control red on 24 rows the day it lands is muted within the week, which is worse than no control.
So the assertion is scoped, and the scope is **measured on every run rather than listed** — see
below. The drawn item's literal design is refuted; its intent is delivered.

## The three-way verdict, which is the actual mechanism

`tools/published_feed_regeneration_check.py` clones the tree at HEAD (`git clone --shared`, ~1s),
runs a generator with `cwd` inside the clone — so no `OUT_PATH` is redirected and the shared tree is
never written — and grades each feed the generator actually wrote:

- **NONDETERMINISTIC** — two clones of the *same commit* produce two different files, so no
  comparison against committed bytes means anything. A named gap, never a pass, never a red.
- **DIVERGES** — deterministic at this commit, and its output is not the committed bytes. The
  SLC-27B shape. **RED.**
- **AGREES** — deterministic, and the committed bytes are what it produces.

The second clone is built only when the first disagrees, so the green path costs one clone. Which
feed a generator owns is **observed from what it writes**, never declared, so no feed→generator
table can go stale.

## The answer

**8 of 61 published feeds reproduce from the commit that published them**: `company`,
`explore_hh_days`, `fidelity`, `knowledge_review`, `premise_demand`, `regulatory`, `simplified`,
`world`. Those eight are the covered set, and the whole set is graded in ~7s.

**There is no second SLC-27B.** Every one of the 24 divergences was traced to an input outside the
commit. The nearest miss was `proof.json`, whose *prose* differs — which is the hand-edit signature
— but the changed text is generated prose with run figures inside it (`543 observed failure events`
against `717`), not an edit.

## The predictions, kept beside the result

| # | predicted | outcome |
|---|---|---|
| 1 | 15–30 generators run clean | **CONFIRMED** — 28 wrote a feed |
| 2 | 1–3 hand-edit divergences beyond SLC-27B | **REFUTED** — zero. I reasoned that a hand-edit to two feeds at once was a habit rather than an incident. On this evidence it was an incident. |
| 3 | a divergence would be in a *copy-style* feed | **REFUTED** — all eight copy-style feeds agree; every divergence is compute-style |
| 4 | 2–6 nondeterministic generators | **CONFIRMED** — 6 |
| 5 | the extract trap would bite | **CONFIRMED** — in a `git archive` extract five generators fail with `not a git repository` and nothing else. That is artefact locality, not a defect in the tree. The design moved to a clone *because of* this measurement; the extract was tried first and discarded. |

Prediction 2 is the one worth keeping. The control is still worth its cost — it makes the next
hand-edit visible on the day it is made instead of sixteen days later by accident — but I predicted
it would find something and it found nothing, and the register should say so.

## How the covered set is stopped from being today's answer

A list of eight feeds pinned to what passed on 2026-09-19 is exactly the shape that goes green when
the claim rots. Two legs stop it. `test_a_feed_that_became_checkable_must_be_promoted` sweeps every
cheap generator and **reds if any feed outside the covered set now reproduces**, so the set can only
grow and an exclusion can never be silently kept. `test_the_instrument_can_return_all_three_verdicts`
asserts over the whole partition, because an instrument that answered AGREES to everything would
pass every other test in the file.

The control is mutation-proven twice, and the two are not the same proof: once at the comparator,
and once **end to end** — the real 2026-09-03 edit replayed into a private clone, committed there,
and the full clone→regenerate→compare path asked. It returns `DIVERGES`. A control that regenerated
into the wrong tree, or compared the output against itself, would be green on the second and is not.

## What is NOT covered, stated rather than left to be discovered

Three generators are outside the promotion sweep on cost alone, each named with its measured
seconds: `generate_provisional_plan_data` (251s — `git log --reverse --follow` over the whole
history), `generate_test_mix_data` (117s), `generate_weather_cells_data` (95s). None writes a feed
that reproduces today, so the exclusion costs no coverage now — but that is a fact about today,
which is why the figures are recorded rather than the word "slow".

The 23 feeds that do not reproduce are **not** made safe by this work. They are exactly as
hand-editable as they were, and the reason each one cannot be checked is a live gap. The nearest
existing work on that is
`tests/tools/test_a_published_surface_is_reproducible_from_its_committed_input`, which establishes
for one pair that shipping an output without its input is real and costly. This measurement says
that shape holds for **23 of 31 runnable feeds**, which is a larger finding than the one this turn
was drawn for and is left minted, not closed.
