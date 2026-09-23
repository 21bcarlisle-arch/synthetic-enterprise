**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `OPS_stale_copy_and_landing_doors`

# The publish path's stale-producer door was scoped to one root and one function, and a producer the census refuses TODAY ran outside both

Drawn as `restore-the-six-live-reverts-before-anything-regenerates-from-them`. The item had two
halves. The first was spent before it was drawn. The second was landed — and **had a blind spot
that contained a live instance of the exact defect it was built for**.

## Half one was spent, and the disposition is recorded here rather than acted on

The item names two copies to restore. Both are **byte-identical to HEAD** on the shared tree:
`simulation/net_new_acquisition.py` and `tools/generate_value_arms_data.py`. The draw's own path
check graded 6 of its 7 resolvable paths `already landed`, and the census agrees — neither file
appears in `stale_copy_refusal --census` any more. The 209-line coin-flip withdrawal and the
"MEMORY IS NOT WHAT BINDS … slack by 4.5x" reinstatement are both gone.

**The item's "done means the census comes back empty on the tree" is not an achievable state, and
should not be carried forward as one.** The census returns **17** paths on the shared tree right
now, and `stale_copy_refusal`'s own docstring establishes why that is the resting state rather
than a defect: `surgical_land` never writes the working tree — by design, because that is what
makes it safe for a two-lane file — so every landing leaves every other lane's copy clock-stale.
The module measured this itself: a clock-only rule refuses 13.1% of tracked-modified paths, and
rule 1 positively vouches for nineteen of them. An empty census would mean no lane had anything
open.

Those 17 are other lanes' **live working copies**. This turn ran in an isolated worktree, where
touching them is forbidden and would in any case destroy in-progress edits; and the commit door
already refuses every one of them. So half one needed no work, and attempting it would have been
the harmful move.

## Half two was landed — and the door had two blind spots, with a live instance inside both

`cc5cc0032` landed `refuse_stale_producers`, `_site_producers`, `refused_to_run`,
`producer_refusal`, `StaleProducer` and a six-control suite. All of it is real and all of it is
armed (mutation evidence below). But its subject was **narrower in two independent dimensions
than the publish path it names**:

**1. The register was scoped to one root.** `_site_producers` filtered imports on the prefix
`tools.`. `background/publish_scope.py`'s `PUBLISH_PATH_SOURCES` — the repo's own declaration of
"if this module is wrong, a figure on the live site is wrong" — names
`simulation/publish_market_feed.py` and `simulation/publish_consumption_data.py`. Both are
imported and run by `_process`; both write `docs/market_data/*.json`; **neither could be seen by
a `tools.`-prefix register.** This is the silently-scoped-guard shape: the guard looked total and
covered one root of three.

**2. The wrapper was scoped to one function.** `refuse_stale_producers` wrapped
`generate_dashboard_json` only. That covers `_generate_dashboard_json`'s ~40 generators and then
**lifts the stand-ins on the way out** — correctly, since a refusal that outlives its reason is a
wedge. But `_process` (`background/process_run_complete.py:9703`) calls
`generate_dashboard_json` at line 9814 and then imports and runs **six more producers of its own
after it returns**: `tools.revenue_sanity_check` (9827), `simulation.publish_market_feed` (9836),
`simulation.publish_consumption_data` (9844), `tools.generate_grid_intensity_feed` (9861),
`tools.generate_explore_carbon`, and `tools.couple_value_based_pricing`.

**The live instance.** Measured on the shared tree this turn:

```
tools/couple_value_based_pricing.py is a working copy that predates commit c4809c5fc
(predates_landing), so regenerating from it would republish over that landing.
```

That module is imported by `_process`, outside the wrapper's scope, in **both** blind spots'
intersection. The census refuses it; the door as landed would have run it. The defect the door
was built for was alive inside the door's own blind spot on the day the door landed.

This is why it is BLOCKING rather than informational: it is not a hypothetical widening, it is a
refused producer with a live reader.

## What landed

* `_PRODUCER_ROOTS = ("tools", "simulation", "saas")` replaces the `tools.` prefix, with all
  three import shapes generalised over it. **`background` is deliberately excluded and the
  reason is in the code**: those are the publisher's own machinery rather than producers of a
  figure, most are bound at module load before the guard can run (so poisoning them is inert
  theatre), and `background.notify` is the channel that REPORTS a refusal — poisoning the alarm
  path to protect a feed trades a wrong number for a silent one.
* `main` now holds `refuse_stale_producers()` across the **whole cycle**, so `_process`'s own
  producers are graded too. Nesting with the existing inner wrapper is safe and deliberate: the
  inner one saves and restores whatever it finds, so an already-poisoned producer is handed back
  unchanged, and `generate_dashboard_json` keeps its own guard when called directly.
* Two controls, each written over a **partition** so a guard scoped to a minority cannot pass:
  `test_the_register_spans_every_first_party_root_the_publisher_runs` asks all four roots of one
  parse at once (tools-only fails the simulation and saas legs; "every first-party import" fails
  the background leg), and
  `test_the_refusal_is_held_over_the_producers_process_runs_after_the_dashboard` is keyed to what
  `_process` SEES at body time, not to the wrapper's text — for the reason its sibling already
  records, that a control grepping for `refuse_stale_producers` is satisfied by a docstring.

## Mutation evidence — all seven die, each on its intended leg

Pre-registered in `PREREG_IS_THE_PUBLISH_PATHS_STALE_PRODUCER_REFUSAL_ACTUALLY_ARMED_2026-09-22.md`
before any of it was run.

| Mutation | Killed by | Predicted? |
|---|---|---|
| `refused_to_run` → `{}` (refuses nothing) | partition test + the naming test | yes |
| `refused_to_run` → refuses everything | partition test (dirty/clean legs) | yes |
| `_site_producers` → `{}` (empty register) | the register test | yes |
| entry-point wrapper removed | the entry-point test | yes |
| **roots narrowed back to `("tools",)`** | **the new root-partition test** | new |
| **cycle-wide wrapper removed** | **the new scope test** | new |
| **roots widened to include `background`** | **the new root-partition test** + sibling | new |

**Where I was wrong, kept beside the result.** I predicted the four original mutations would die
on legs that do *not* monkeypatch `refused_to_run`, so that the production wiring would be shown
to be graded by something other than its own stub. **Half refuted.** The entry-point test *does*
monkeypatch `scr.refused_to_run`. On inspection that is not the stub-proves-the-stub shape — the
monkeypatch supplies the *input* (a deterministic stale verdict) while the subject under
assertion is the wrapper's real wiring, which is not stubbed — but my prediction as written was
wrong and the distinction is finer than I had it when I wrote it down.

**The second prediction was confirmed, and it is a coverage fact worth keeping.** With
`refused_to_run` fully neutered, **all 65 tests in `tests/tools/test_stale_copy_refusal.py`
stayed green**. Exactly one file in the tree grades this rule. That is not a defect — the
production chain *is* controlled, which the wrapper mutations prove — but anyone editing that
file should know it is the only thing holding the rule up.

## What this leaves open

The nesting means the census now shells out to git twice per cycle over ~60 paths. Measured cost
is small against a 25-minute publish and it buys independence between the two wrappers, but if a
later lane finds it on the critical path, the fix is a re-entrancy check and not a removal of
either wrapper.
