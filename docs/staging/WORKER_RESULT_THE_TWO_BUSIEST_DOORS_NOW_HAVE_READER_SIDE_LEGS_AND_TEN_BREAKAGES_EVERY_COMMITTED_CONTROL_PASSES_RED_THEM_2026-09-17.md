**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** —

# The two doors that grade the most sentences now have reader-side legs, and ten breakages every committed control passes red them

Autonomous worker, 2026-09-17. Claim
`the-per-door-browser-legs-name-one-doors-own-sections-and-twenty-three-doors-still-have-none`.

Class: controls_that_cannot_fail. RECORDED rather than BLOCKING: the two legs are landed and
mutation-proven, and what is still owed is the same shape for the twenty-one remaining doors, which
is ordinary queued work rather than a live defect.

---

## The premise, re-measured before starting

The item cites `407ec5930` (the class-level sweep, `site/test_every_door_element_a_reader_meets.py`)
and the draw's own check reported it already an ancestor of `origin/main`. **That is the
precondition, not a spent premise** — the item asks for the per-door half that the sweep explicitly
does not cover, so the sweep having landed is what makes the work possible. Confirmed ancestor of
both `origin/main` and local `HEAD`.

The duplicate-work note named
`the-publisher-has-never-graded-a-clean-publish-and-the-site-lane-is-red-right-now` as possibly this
work. It is not: that claim's own note is about
`site/test_the_site_lane_runs_no_untracked_control.py` refusing on three controls in no commit. That
red is **already cleared** — the module passes in 0.04 s at this HEAD and all four files it named
(`site/_browser_probe.mjs`, `site/test_the_browser_reading.py`,
`site/harness/test_the_deployment_reading_is_visible_to_a_browser.py`,
`site/test_every_door_element_a_reader_meets.py`) are tracked. Different work on the same subject,
so no disposition taken on that claim; this note is the record of the check.

## What was built

| Door | Module | Legs |
|---|---|---|
| `/capabilities/` | `site/capabilities/test_the_capabilities_reading_is_visible_to_a_browser.py` | 7 |
| `/explore/` | `site/explore/test_the_explore_reading_is_visible_to_a_browser.py` | 7 |

Both take one chromium launch over the **published (index) bytes** served on an ephemeral port, via
`published_site` / `published_site_server` and `assert_visible_reading` from
`site/test_the_browser_reading.py`. **14 legs, 4.5 s together** — cheap enough to stay in the commit
path, which is the only place a control catches a breakage before it deploys.

## The measurement that justifies the file existing

The sweep's docstring names its own residual gap: *an element deleted from BOTH the markup and the
script is outside its subject entirely*, because its id list comes from what the door's script asked
for on the run. That was tested rather than taken on trust. Ten breakages were constructed in an
isolated `git archive` extract (git-initialised, `node_modules` symlinked so the browser legs ran
rather than skipped — a skip is the same colour as a pass):

| # | Breakage | Per-door leg | Class sweep | vm door suite |
|---|---|---|---|---|
| 1 | `#gaps` deleted from **both** markup and script | **RED** | green (6 passed) | green (44 passed) |
| 2 | arms feed renamed → the page's own `.catch()` publishes a load failure | **RED** | — | — |
| 3 | `setWall` stops writing `#wall-truth`, so the markup `—` survives | **RED** | green (6 passed) | — |
| 4 | spine renders `STAGES.slice(0, -1)` — reader never learns stage 6 exists | **RED** | green (6 passed) | — |
| 5 | `#bookcount` claims `length - 1` over the list it heads | **RED** | green (6 passed) | — |
| 6 | `panel()` drops `data-side` — eyes toggle dead, counter reads 0 panels | **RED** | — | — |
| 7 | tally strips render `<div class="fig-v"></div>` — labels, no figures | **RED** | — | — |
| 8 | stamp drops the commit it was generated at | **RED** | — | — |
| 9 | stage 1 drops its `Clock:` line | **RED** | — | — |
| 10 | `../data/customers.json` renamed → `#stage` publishes a load failure | **RED** | — | — |

**Every leg in both modules fired on a defect written for it.** Five of the ten were run against the
class sweep as well, and it passed all five; the vm door suite was run against #1 and passed its 44
legs. So the gap is real in the direction that matters — not "the sweep is weak", but "the sweep and
the per-door leg are different questions", which is what the item said.

Breakage #3 is the one worth naming. `#wall-truth` and `#wall-belief` ship as `—` in the markup and
`#bookcount` ships as the word `This`, so a render that never runs leaves a **visible element
containing readable characters**. Exists passes, visible passes, and "carries words" passes too. The
reader meets an em-dash where the world's ground truth belongs, on the one door built to show the
epistemic wall. Only a leg that names the section and says what kind of sentence belongs in it can
see that.

## One correction, kept beside the claim

The first draft of the capabilities clock leg asserted per element — `#arms-note` must contain
"clock" — and **went red on a page that states every clock it has**. The arms chain publishes on two
clocks (`settled-realised`, `settled-provisioned`) and names them on the two table headers, because
one note could not carry both. That is a control pinned to a layout rather than to the property. It
now asks per CHAIN: the clock must reach the reader somewhere they meet that chain's figures. The
comment in the module records this so the next session does not re-narrow it.

## Two notes for whoever writes the next door's legs

**Nothing is pinned to today's answer.** Not £16,792, not 154 households, not 2 panels. Each leg
asserts a shape the sentence must have whatever the record says — the comparison names both of its
sides, the money chain names its clock, the spine offers every stage the script defines, the
population headline counts the list it heads. A control pinned to the current figure goes red the
day the company gets better and stays green the day the page starts lying.

**The join that has the most teeth is the one that needs no list.** `published_site` yields the
docroot as well as the URL, so the explore spine leg reads `var RENDER = [...]` out of the published
script and asserts the reader is offered exactly that many stages. A stage added to the journey is
covered the same day; nothing is hand-kept. Where a hand-kept list was unavoidable — the named
sections — it is deliberately the quotable readings only, not all 41 ids, because re-stating the
sweep with a list that will rot buys nothing.

## What is still owed

Twenty-one doors have no per-door leg. The two built here are the ones whose suites grade the most
sentences, which is where the item pointed; the remainder are ordinary queued work, and the pattern
to copy is these two plus `site/harness/test_the_deployment_reading_is_visible_to_a_browser.py`.

## One thing measured in passing, and not repaired here

`tests/architecture/test_static_quality_ratchet.py::test_ruff_baseline_matches_frozen_census` is RED
in the shared working tree (`{'I001': 1307} != {'I001': 1308}`) and GREEN both at `HEAD` and on the
tree this commit creates. The census went DOWN by one, so it is another lane's in-flight working-tree
edit that fixed an `I001` without moving the baseline — not this work, and not something to commit
around. Named here so the next lane to meet it does not re-derive the attribution.
