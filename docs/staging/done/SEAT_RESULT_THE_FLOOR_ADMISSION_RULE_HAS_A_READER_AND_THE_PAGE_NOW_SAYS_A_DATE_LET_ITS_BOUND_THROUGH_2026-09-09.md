**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — floor-book-identity-has-no-reader-so-the-stamp-proxy-still-gates-every-directional-claim) · **Class:** controls_that_cannot_fail

# RESULT — the floor admission rule has a reader, and the page now says a DATE let its bound through

Discharges the drawn Lane 0 item, which named its own defect exactly: `run_value_cycle_ab.floor_book_identity`
had **one caller and no reader**, so the repair its own commit message described was still live on the
published page. Built, not wired — the shape the seat named as its own error one stretch ago.

## What the page said before, and what it says now

The value-arms page gates every directional claim it makes on a noise floor being *paired* to the
figure it bounds. The only pairing rule that existed was `_staleness_caveat`: a comparison of two
`generated_at` stamps. The question a bound has to answer is **was this spread drawn over the book
this figure is made of**, and a stamp cannot see a book at all.

`site/data/value_arms.json` now carries, on the live feed:

```
error_bar.floor_admission.rule       = "stamp_proxy"
error_bar.floor_admission.admitted   = true
contrast_bounds.admitted_by          = "stamp_proxy"
```

and the rendered page carries the sentence, in amber, above the fold of the error bar:

> THE BOUND ON THIS FIGURE WAS ADMITTED BY ITS DATE, NOT BY THE BOOK IT WAS DRAWN OVER: this noise
> floor carries no book identity of its own — it was drawn before its producer recorded one. A date
> is a proxy for that question and it is wrong in BOTH directions — measured on this page's own
> artefacts, it has refused a pair proven to be the same world, and admitted a floor drawn over a
> different one on a single second of stamp order. […] A noise floor produced since
> `run_value_cycle_ab.floor_book_identity` landed declares its own population, and this page pairs on
> that instead the moment one reaches it.

That is the fail-closed fallback the item asked for, **on the page and not in a comment**. No floor
on disk carries a `book_identity` (checked: all fourteen `value_cycle_ab_s1_noise_floor*.json`), so
the proxy branch is the live one and the page now says so rather than letting a reader take a
pairing by date for a pairing by population.

## What was built

| Where | What |
|---|---|
| `tools/generate_value_arms_data.py` | `_floor_admission`, `_the_runs_declared_book`, `_admitted_on_a_stamp_proxy`, `_comparable`, and the two named rules `ADMITTED_ON_THE_DECLARED_BOOK` / `ADMITTED_ON_A_STAMP_PROXY` |
| …`_error_bar` | publishes `floor_admission` unconditionally on the available branch — states, never refuses, the split `world_measured_in` already makes |
| …`_seed_spreads` | **refuses** when the declared books disagree, and publishes `admitted_by` on the admitting branch. This is where a DIRECTION is taken |
| `site/capabilities/index.html` | renders `why_this_rule` (muted when admitted on the book, amber on a proxy) and `refusal` in amber |
| `tests/tools/test_generate_value_arms_data.py` | seven controls, including the whole-partition reachability leg |
| `site/test_the_baseline_comparison_reaches_the_reader.py` | the live-feed leg and the three-way render partition |

**It adds a refusal and removes none.** `_staleness_caveat` is untouched and still gates: "were these
two runs contemporaneous" and "were they drawn over the same population" are different questions, and
passing the second is no evidence about the first.

**It pairs on the DECLARED half only** — the producer's own instruction in
`how_a_consumer_should_pair_this`, not this consumer's choice. Two floors of the same book differ in
their realised account counts by construction, because moving the price-sensitivity draw moves who
churns and therefore who settles. `test_the_pairing_is_on_the_DECLARED_half_and_never_on_the_realised_counts`
is the control; a consumer that got this wrong would refuse every honest re-run.

**No second copy of the field list.** The declared field names come from the floor artefact's own
`declared` block, so `BOOK_DECLARED_FIELDS` stays in one place and the consumer cannot drift from it.

## The poison round, before the mutation battery

*"Survived" means two opposite things, so reachability was proved first.*

| Poison | Result |
|---|---|
| `_floor_admission` returns the proxy branch unconditionally | 3 producer controls red, including the partition leg |
| the admission render dropped from `index.html` | both door controls red |
| the render styled muted on every branch | the styling leg red, the text leg green — which is why the styling leg exists |
| all three restored | 271 passed, 1 skipped across both suites |

## What I did NOT do, and why it mattered

`WORKER_FINDING_THE_LANE_0_PAIR_MOVE_IS_TWO_THIRDS_SPENT…` names the hazard this turn walked into:
this tree is **7 ahead / 16 behind `origin/main`**, and `NOISE_FLOOR_PATH` here held the **3-seed**
floor while origin's copy is the **9-seed** one landed at `8d7693d92`. Regenerating and landing
`site/data/value_arms.json` from this tree as-is would have taken `contrast_bounds.seeds` from 9 back
to 3 — an atomic, invisible revert inside a commit that reads as an improvement.

The move made instead is **convergent, not a promotion**: `value_cycle_ab_s1_noise_floor_20260909b.json`
(untracked here, committed at origin) is byte-identical to `origin/main:…noise_floor.json`
(md5 `24da1d28…`), so copying it onto the canonical path here **reproduces origin's landed state
exactly** and lands nothing origin does not already have. Verified by `diff` against
`git show origin/main:` before regenerating. The regenerated feed reads `seeds = 9`, agreeing with
origin, plus the new block.

**The divergence itself is not discharged** and is not this item's: `origin/main` is 16 ahead, no
local commit is duplicated there, and the recorded remedy is `reset --mixed` + re-land, never a merge.

## Pre-existing reds, proved in a clean extract and not caused here

`tests/tools/test_the_value_arms_pages_undriven_pointers.py` is red at HEAD — 3 failures in a clean
`git archive HEAD` extract, 2 in this tree (`_current_world_bound`'s here-relative literal, a
different lane's subject). It is already carried in
`docs/staging/reference/HEAD_RED_REGISTER.md`. This change reduces the count by one and adds none.

## What is next

1. The declared-book branch is **reachable but unvisited in production** until a noise floor is run
   after `floor_book_identity` landed. That run is not this item's — the item said not to re-run
   anything — but the day it lands, `floor_admission.rule` flips to `declared_book` with no code
   change, and both live controls are keyed to the property so neither reds for it.
2. `_current_world_bound`'s own floor (`CURRENT_WORLD_NOISE_FLOOR_PATH`) goes through the same
   `_staleness_caveat` and has no admission rule wired to it yet. Same defect, second consumer.
