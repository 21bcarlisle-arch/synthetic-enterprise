**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The staleness control compares the two artefacts to each other and never to the world publishing them

**Class:** `figures_on_a_superseded_clock` (primary), `controls_that_cannot_fail` (secondary)
**Filed:** 2026-09-03, delivery seat, Lane 0, claim
`the-baseline-was-beaten-in-a-world-that-no-longer-exists`
**Subject:** `tools/generate_value_arms_data.py::_staleness_caveat`, `site/capabilities/index.html`.

---

## What is true, measured at `0a1441c50`

The `/capabilities/` page publishes the director's baseline claim — *the per-customer arm beat a
flat rule by £12,071* — and the whole page is instrumented for honesty about it. There is an error
bar rendered before the number, a clock declaration, a coverage denominator, a withdrawn-claims
block, a check that the baseline arm IS the supplier the site publishes, and `_staleness_caveat`,
which exists specifically to catch a figure and its bound coming from different worlds.

At the moment of this finding, **`error_bar.staleness_caveat` was `None`** — a clean bill of health
— and the figures were measured two days and two anchor re-fits ago.

`_staleness_caveat` is not broken. It answers its question correctly. Its question is *"do the
error bar and the figure agree with **each other**?"*, and they did: `fe4df178b` and `4240e1478`,
three hours apart on 2026-08-31, with nothing a run can read between them.

**Nothing asked whether either agreed with the tree publishing them.** Between `fe4df178b` and HEAD
there are **137 paths a run can read, 35 of them in `simulation/`, `company/` or `saas/`**, and one
of the 35 is `simulation/departure_level_anchor.py` — re-fitted twice, at `a621edb15` and
`712ae5323`.

## Why that one path is the whole finding

The anchor sets how many households leave. How many leave sets how much book there is to re-win.
How much book there is to re-win **is the entire surface the per-customer arm acts on**. So it is
not a distant dependency of the published claim; it is the denominator of the thing being claimed.

Measured on `c6_second_pass_departure_factors.json` by scoring one capture under both anchor tables
(SVT held fixed, since `level_anchor` multiplies only the three hazards the SVT route builds at
0.0):

**Whole-book expected departure over the eight full years: 13.909% → 15.958%. Expected departures
55.7 → 63.8, a rise of 14.6%.**

The per-year table is in
`SEAT_PREREGISTRATION_WHAT_THE_ARMS_RERUN_ON_THE_LIVE_WORLD_MUST_MOVE_2026-09-03.md` §1.

A baseline beaten in a world with a seventh less churn than this one is not a baseline beaten in
this one. The figure is not wrong — it was honestly measured — but presented bare it answers a
question about a world that no longer exists, and no reader of the page could tell.

## The shape, named

Every control on that page asks whether a figure is **arithmetically right**. None asked whether
**the world it was measured in is still the world**. That is why this recurred three days after
being filed against the same artefact: the previous repair fixed the relationship *between the two
artefacts* and left the relationship *between the artefacts and the tree* unexamined, and a
one-sided repair to a two-sided question reads as complete.

It is also the general form of `_INERT_TO_A_RUN`'s own logic being available and pointed in only
one direction. The machinery to answer the second question was already in the file — the fix reuses
it verbatim.

## What was done — and what of it LANDED, which is not the same thing

**This document and the pre-registration landed. The code did not, and the reason is not a defect
in it.** Read the next section before treating the repair as in place.

`tools/generate_value_arms_data.py::_world_moved_since` — a second, orthogonal leg, published as
`world_currency` and rendered into a new `#arms-world` panel **directly under the headline**, since
a bound met three paragraphs after the number does not undo the impression.

Keyed to the property, not to today's answer: the subject is *the tree the figure was measured on*
against *the tree publishing it*. It names no commit, no year, no anchor and no value, so re-running
the arms at the current tree empties it by construction, and it will fire for the next world change
without anyone remembering to update it.

**It caveats and dates; it does not withdraw.** The figures stay on the page with their world and
their date. They were honestly measured, deletion would destroy the only contrast a re-run can be
graded against, and superseded-with-provenance is the correction.

Four branches, each reachable and distinct, all four exercised:

| feed state | verdict | what a reader meets |
|---|---|---|
| no `producing_commit` | `None` | amber — unknown vintage, never "current" |
| measured at HEAD | `True` | quiet confirmation, so green ≠ broken feed |
| measured earlier | `False` | amber — 137 paths, 35 in the world's layers, anchor named |
| diff unresolvable | `None` | amber — an unanswerable question is not a green answer |

**R15 — the mutation, run and reverted.** Replacing the `#arms-world` assignment with a dead
variable (valid JS, panel never written) reds all five new door tests; reverting greens them. The
first attempt at this mutation produced a **syntax error** instead, which redded the same tests for
the wrong reason and proved nothing — recorded because a malformed mutation that happens to go red
is indistinguishable from a real proof in a log.

The assertions key on the **presence of `figures_are_current`**, not on today's verdict, so deleting
the leg reds rather than skips — a control that skipped when its subject was absent would swallow
the exact mutation it exists to catch.

## Why the code is written and UNLANDED, and what unblocks it

The leg sits finished in the shared tree at `0a1441c50` and is not in any commit. It cannot be
landed on its own, and the reason is worth writing down because the first two readings of it were
both wrong.

`_world_moved_since` calls `background.boot_sha.changed_paths_between` and `_INERT_TO_A_RUN`.
**Neither exists at HEAD.** Both are another lane's uncommitted work, sitting in the same three
files this change touches, along with `_svt_drift_belief` (+148 lines), a full rewrite of
`_staleness_caveat`, and +184 lines of `site/capabilities/index.html`. Of the 803 insertions across
those files, roughly a fifth are mine.

Two wrong readings, corrected in order:

1. *"HEAD is broken — the generator imports a symbol HEAD does not have."* No. The import is the
   other lane's edit too. HEAD is consistent; the working tree is ahead of it on both sides of that
   call.
2. *"Then land the supplier with the consumer."* That was tried, and the gate refused correctly:
   the resulting tree reds 8 tests in `tests/tools/test_generate_value_arms_data.py` and
   `site/test_...reader.py`. Those failures are the other lane's in-flight work meeting fixtures
   stamped `2999-01-01` — the fixtures their own new docstring names as *"a control the tests route
   around by dating a fixture past it"*. They are mid-repair. **None of the 8 is mine**, and
   bundling my leg into their red is how one lane's unfinished work becomes another lane's refused
   commit.

**The symbol-landing gate is what caught this, and it was right twice** — first that the consumer
had no supplier in the tree the commit would create, then that the tree carrying both is red.

**What unblocks it:** the lane holding `_INERT_TO_A_RUN`, `changed_paths_between` and
`_svt_drift_belief` lands its work. `_world_moved_since`, the `#arms-world` panel and the five door
tests then land unchanged on top — they are already written, already mutation-proved, and already
green against the working tree. The next seat should check `git diff HEAD -- tools/generate_value_arms_data.py`
for whether those three symbols are still uncommitted before doing anything else; if they have
landed, this is a re-gate and a commit, not a rebuild.

**What is NOT the answer:** re-implementing `changed_paths_between` or a private inert-path list to
make the leg self-contained. It would duplicate a function that is about to land, and the
write-time gate would be right to ask why.

## What is NOT done, and is the next act

The re-run itself. The figures on the page are still the 2026-08-31 ones; what changed today is that
the page now says so. Four legs on one seed family, ~8 hours, per the pre-registration §3 —
including why this turn did not launch it (a second seat was already on the same item, in a
worktree, and a duplicate 8-hour run would contend with it and with a running suite).

## Residue — not fixed here, filed rather than swept

`site/test_the_baseline_comparison_reaches_the_reader.py::test_an_error_bar_older_than_its_figure_says_so_on_the_page`
skips when `staleness_caveat` is falsy and then asserts `"DEFEND"` — a caveat string from the
2026-08-28 competitor change. With the caveat now `None` it skips unconditionally, so it is a
`pytest.skip` on a **value** that swallows its own subject, and its surviving assertion is pinned to
one historical world event rather than to the property. Not touched here: it is a pre-existing
control with its own subject, and rewriting a control's subject inside a commit that repairs what it
measures is how a moved number becomes unattributable.
