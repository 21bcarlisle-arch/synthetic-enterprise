**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

**Knowledge:** none — this is a harness state, not domain understanding.

# The site wedge's named cause was the page, and one-variable runs put it in the test file

**Found 2026-09-08** working the Lane 0 delivery item on `site/capabilities/index.html`.
**Reproduce:** the three one-variable runs in "The measurement" below.

---

## What was claimed

The standing direction named the cause precisely: the page prints `STATES NO VERDICT` under a
figure the feed marks `resolved`, and the remedy was to drive the page's verdict from
`current_world.resolved` and `current_world.bound` rather than from
`current_world.selection_leg.verdict_withheld_because`. It named two reds:
`test_the_composition_the_page_states_is_the_one_the_feed_established` and
`test_the_figure_from_the_world_that_is_live_reaches_the_reader_and_never_as_resolved`.

Everything in that description was checkable and none of it was the cause.

## The measurement

Three clean HEAD extracts, one working-tree file swapped into each:

| swapped in | result |
|---|---|
| `site/capabilities/index.html` alone | **2 passed** |
| `site/data/value_arms.json` alone | **2 passed** |
| `site/test_the_baseline_comparison_reaches_the_reader.py` alone | **2 failed** |

The page never authored the phrase. It renders `d.headline`, and `STATES NO VERDICT` is composed
by `tools/generate_value_arms_data.py` — **about the selection leg**, while the advantage
resolves. HEAD's feed carries the identical `resolved: True` and the identical headline, and HEAD
is green. Both statements the page makes are correct and both reach the reader.

## What was actually wrong

Two lanes branched from `2a61d1a61` and grew in parallel, and **each side's copy deleted the
other's** — in the test file *and* in the page:

* **HEAD** carried the attribution work (`ff269503e`): `_the_legs_own_regions`,
  `_assert_the_verdict_belongs_to_the_leg_that_earned_it`, `_door_prose`, `_door_gbp`, the
  `arms-redraw` panel, three rungs.
* **The working tree** carried the survivorship and bigger-book work: `_consequence_feed`,
  `_survivorship_feed`, five rungs, the `survivorshipBlock` renderer.

The working tree's copy had lost the region-scoping, so its whole-page `"STATES NO VERDICT" in
rendered` check fired on the **selection leg's** refusal and attributed it to the **advantage**.
A false red — and because the site lane gates every commit touching `site/`, it wedged every
lane for 14 hours (`episode_failures` 19, `last_clean_publish` null).

This is the third time this pair of files has diverged this way; `490f0b7a2` ("both seats'
value-arms work survives the merge") is the previous one.

## Why the doorbell could not have known

A doorbell reads the *working tree*. In the working tree the red is real and the page is the
thing that looks wrong, because the stale test file and the current page genuinely disagree.
Only a one-variable run against HEAD can tell "the page is wrong" from "the copy of the control
in this tree is behind HEAD". **A drawn item's stated cause is a hypothesis measured in the tree,
and the tree is exactly what is broken.**

## What is next

The merge is landed (both sides, 96 tests, none lost, poison round run). What is **not** done:

* Nothing detects this class. Two lanes deleting each other's symbols in one file is invisible
  until a control goes red for a reason that is not its subject. A cheap check exists in
  principle — compare the working-tree copy's symbol set against HEAD's before a site commit and
  refuse on a **deletion** — and it is unbuilt.
* `docs/staging/` holds `SEAT_PREREG_THE_TWO_LEG_HEADLINE_IS_ASSERTED_WHOLE_PAGE_2026-09-08.md`
  in **two rooms** (records and root), which `background/finding_classes --check` names. That is
  another lane's to settle; recorded here because it was found beside this.
