**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PRE-REGISTRATION — the sweep for other payload strings with more than one home

**Written 2026-09-08 by the delivery seat, in an isolated worktree, BEFORE the sweep ran.**

The parent finding is
`SEAT_FINDING_A_POINTER_SENTENCE_WITH_TWO_HOMES_IS_FALSE_IN_ONE_OF_THEM_2026-09-08.md`. Its "what is
next" names the generalisable half: **a producer does not know how many homes its output has, so a
sentence that says "here" is unverifiable at the point it is written.** The drawn direction is to
sweep `site/` for other feed strings composed into more than one page region and judge each one's
`here`-relative prose the way
`test_a_sentence_pointing_at_the_band_table_is_true_from_EVERY_region_it_renders_in` now judges the
band-table pointers.

This file exists so the answers below cannot be written after they are known.

---

## The method, fixed before the numbers

Homes are **derived, never declared** — the same rule the parent rung established, generalised off
one page:

1. Every deployed door from `site/live_pixel_verify.all_doors()` (sitemap + `ia_register`), so a
   door added to the IA is swept without editing a list.
2. Each door is driven through its own boot path with `site/_live_harness.mjs` against the **local**
   `site/data/*.json` feeds, giving `{element id: rendered content}` — the regions.
3. Every string value in each feed is walked. A string's HOMES are the element ids whose rendered
   content contains it. Composition is therefore invisible to the method and does not need to be
   modelled: a sentence composed into a headline is found in the headline's region because it is
   *there*, exactly as a reader meets it.
4. A string is a HERE-RELATIVE POINTER when it carries a registered phrase whose referent is the
   point of rendering ("higher up this section", "the table above", "shown below") and no registered
   LANDMARK phrase naming what it is a direction from ("under the headline figure").

## The claim under test

**A here-relative pointer with more than one home is a defect by construction**, whatever today's
page order happens to be — it asserts a direction from a place its producer cannot name. The band
table pointer is the known instance. The question is whether it is the only one.

## Predictions, in order, with what would refute each

**Q1 — how many feed strings (≥40 chars) reach more than one rendered region across all doors?**
Predicted **20–200**. Composition is common on this site — headlines recite panels, summaries recite
entries — so I expect multi-home strings to be ordinary rather than rare. A count in single figures
would mean the harness or the containment match has gone blind, not that the site is clean, and the
witness leg below is what would tell them apart.

**Q2 — how many of those multi-home strings carry here-relative page-position prose?**
Predicted **0 or 1**, outside the already-fixed value_arms pointers. My prior is that the band-table
sentence was unusual: most of this site's prose is written about *subjects* rather than about *the
page*, and the earlier grep over the raw feeds returned mostly non-spatial uses of "above",
"alongside" and "opposite" (a benchmark that a figure is above; a signal added alongside another).
The single candidate I can name in advance is `capabilities_door.json .gaps[1].what`, which opens
"Listed above as coming next" — I do not yet know whether it has one home or two.

**Q3 — will the sweep find a live falsehood, i.e. a here-relative pointer whose direction is wrong
in at least one home?** Predicted **NO** (~0.6 confidence). The parent finding's instance was found
by looking at the one page hardest; a second one at the same depth would say the shape is common,
and I do not believe it is. **If Q3 comes back YES the prediction is refuted and the instance is the
finding**, not this file's tidiness.

**Q4 — is the general rule cheap enough to be a standing control?** Predicted **YES**: one node
render per door, the same work `live_pixel_verify` already does, and no new door knowledge. If the
whole-site render costs more than ~120s the control is scoped to the doors whose feeds carry
directional vocabulary at all, and the scoping is recorded rather than left silent.

## What I will NOT do on the strength of this

Change any published wording that the sweep does not show to be multi-homed. A landmark rewrite of a
single-home sentence is a change with no defect behind it, and the parent finding's own correction
is the reason: the argument about whether a pointer is wrong is settled by the census, never by how
plausible the wrongness sounds.
