**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `every-surface-that-still-says-our-advantage-is-selection-must-answer-the-nine-seed-floor`) · **Class:** measurements_that_mirror

# FINDING — one live surface in sixteen still stated the selection claim, and forty-five feeds reach no reader at all

Graded against `docs/staging/records/SEAT_PREREGISTRATION_WHICH_LIVE_SURFACES_STILL_ASSERT_SELECTION_WITHOUT_THE_NINE_SEED_BAND_2026-09-09.md`,
filed before `explore/`, `knowledge/`, `delivery.json`, `proof.json` and the four remaining
capabilities feeds were read. **P1, P2 and P4 hold. P3 holds for one of its two subjects and is
refuted for the other, and the refutation is the more useful half.**

## Why this sweep existed

The nine-seed floor
(`docs/staging/records/SEAT_RESULT_THE_SELECTION_LEG_READS_THE_NINE_SEED_FLOOR_AND_THE_PREREGS_IMPOSSIBLE_NARROWING_DROPPED_A_DIVISOR_2026-09-09.md`)
says the per-customer engine's contribution is **£319 inside a ±£1,811 band**, that the same
contrast re-drawn nine times falls on **both sides of zero**, and that the price level accounts for
**98%** of the per-customer arm's advantage. Any surface still telling a reader our edge comes from
per-customer selection is contradicting our own best measurement, and reads as evidence while doing
it. This is reconciliation of work already landed, not new measurement.

## First, what "live" means — and it is a much smaller set than the directory

`site/data/` holds **61** top-level JSON files. The five pages a reader can open fetch **16** distinct
ones (`explore_carbon.json` is fetched by two pages, which is why the table below lists 17 rows of
feed against 16 files).

| Page | Feeds it fetches |
|---|---|
| `site/index.html` | `dashboard`, `explore_carbon`, `moap_node_atoms`, + hand-authored hero/thesis prose |
| `site/capabilities/index.html` | `book_growth`, `capabilities_door`, `dd_opening_arms`, `value_arms` |
| `site/explore/index.html` | `customers`, `explore_carbon`, `explore_hh_days`, `weather` |
| `site/harness/index.html` | `delivery`, `director_delta`, `director_reserved`, `proof` |
| `site/knowledge/index.html` | `knowledge_review`, `knowledge_wholesale` |

**Forty-five feeds are fetched by nothing.** That is P1 and it matters to this sweep's method:
`simplified.json` carries **130** selection-word hits, `proof.json` 45, `company.json`,
`capabilities.json`, `world.json` and `method.json` more. Reading those as claims would have
produced a large, urgent-looking and entirely fictitious remediation list. **They are not honest and
they are not dishonest — they are unrendered**, and the next pass must be able to tell the
difference, which is why the table below carries UNRENDERED as a verdict of its own.

## Every surface checked, and its verdict

Sixteen live surfaces. **The already-honest ones are listed on purpose** — a clean surface and an
unchecked one look identical from outside, and this table is the only thing that separates them.

| # | Surface | What it says about where the advantage comes from | Verdict |
|---|---|---|---|
| 1 | `site/index.html` — `.thesis` hand-authored prose | *"you create value fastest by knowing each household well"*, with `NOT YET MEASURED` attached to the **carbon** score, not the money leg | **DEFECT — FIXED HERE** |
| 2 | `site/index.html` — `.hero` / mission sentence | quotes the director's mission verbatim ("automating ways to find individual customers we can create value for") | NO CLAIM — a mission, not a measurement |
| 3 | `site/index.html` — `.bookmix` | whose book this is; a revenue **share**, no direction | NO CLAIM |
| 4 | `site/index.html` — `livefigs` (`dashboard.json`) | account count, years settled, coverage % | NO CLAIM |
| 5 | `site/capabilities/index.html` — `#value-arms` (`value_arms.json`) | renders `selection_leg.verdict_withheld_because`, the nine-draw band table from `verdict_stability.*`, and `current_world.composition` — **every figure fetched, none authored** | **ALREADY HONEST** |
| 6 | `value_arms.json.headline` | states £319 inside ±£1,811 across 9 re-draws and "CANNOT RESOLVE ... in either direction" | **ALREADY HONEST** |
| 7 | `value_arms.json.inference_claim` | "on whether the method works we cannot tell"; refuses the belief-vs-truth gap as evidence of skill | **ALREADY HONEST** |
| 8 | `value_arms.json.method_skill` | 0.534 inside the 0.449–0.550 a no-information signal reaches on 168 decisions | **ALREADY HONEST** |
| 9 | `value_arms.json.decisions` | counts and denominators, each naming what it counts | NO CLAIM |
| 10 | `site/capabilities/index.html` above the fold | four section ledes: capability state, seams, boundary, book growth | NO CLAIM |
| 11 | `book_growth.json` | the growth bound is a **compute** budget, said so | NO CLAIM |
| 12 | `capabilities_door.json`, `dd_opening_arms.json` | zero selection-word hits | NO CLAIM |
| 13 | `site/explore/index.html` (`customers`, `explore_hh_days`, `weather`, `explore_carbon`) | zero hits across all four feeds and the page | NO CLAIM |
| 14 | `site/knowledge/index.html` (`knowledge_review`, `knowledge_wholesale`) | zero hits | NO CLAIM |
| 15 | `site/harness/index.html` — `delivery.json` | `what_it_decided.thesis_read` and `focus[].why`, **both rendered** at `site/harness/index.html:572,575`: *"the arm beat it by £17,444 — of which 98% is the price LEVEL and £319 is the choosing, inside the noise"*; `the_number_the_programme_rests_on.statement` opens *"WE CANNOT TELL"* | **ALREADY HONEST, at both ends** |
| 16 | `site/harness/index.html` — `proof.json` | see below | **UNRENDERED, not honest** |

## P3's refutation, and it is the half worth keeping

The pre-registration predicted `delivery.json` **and** `proof.json` would both be already-honest,
and named its own risk: *"the honest sentence is in a field no renderer reads"*. That risk landed,
on the second subject.

`proof.json` carries **45** selection-word hits. Every one of them that touches the direction of the
advantage is in `verification.honest_holds[].note`. The harness page's `proof.json` consumer reads
`control_killlist`, `corrections`, `coupled_gaps`, `deployment`, `generated_at`, `git_commit`,
`not_proven`, `test_count` and `timeline` — **`verification` is not among them.** Of the fields that
*are* rendered, `not_proven`, `corrections`, `control_killlist`, `timeline` and `deployment` have
zero directional hits, and `coupled_gaps` has four, all of them honest-shaped (selection **bias** as
a trap to discover, and a CLV belief carrying *less* information than a mean).

So `proof.json` is neither the pass P3 predicted nor a defect. It is a third state, and the
distinction is load-bearing: **had this sweep graded it by reading the file rather than by checking
both ends of the pointer, it would have been recorded as forty-five honest surfaces, and a
forty-sixth note added tomorrow asserting the opposite would have inherited that clean bill.**

## The one defect, and why the remedy carries no number

The front door stated the personalisation claim as an open hypothesis. Its `NOT YET MEASURED` tag
is about £/tCO₂e. So a reader met *"you create value fastest by knowing each household well"* with
no signal that the money side had been run and had returned *we cannot tell*. **A hypothesis a
reader cannot tell has been tested reads as one nobody has tested yet** — the more flattering of
the two readings, and the wrong one. It is the front door, so it is also the most-read surface on
the site.

`site/index.html` now carries a paragraph stating the three runs, that the choosing leg falls on
both sides of zero across nine re-draws, that the book cannot yet say whether deciding household by
household is worth anything in either direction, and that almost all of the advantage it does show
is the price level — value moved rather than made. It links to `/capabilities/#value-arms`.

**It carries no figure, and that is a decision this finding owns rather than an omission.** The
drawn item asked for "the ±£1,811 band" on each surface. Two standing rules say not here:

1. **RC7** (`DIRECTOR_RULING_IDEA_FIRST_EXTERNAL_REGISTER`, 2026-07-24) — no cohort-derived pound
   aggregate leads a public surface, *"a share of revenue and an account count, never a total"*.
   The selection leg and its band are both cohort-derived pound totals. This is a director ruling
   and this seat does not get to trade it against a delivery instruction.
2. **One fact, one home.** `/capabilities/#value-arms` **retired its own prose copy of this band on
   2026-09-08** precisely because a fact with two homes gets edited on two days for two reasons —
   this repository's named VAT shape. Re-typing the band on the front door would rebuild the shape
   that page had just demolished, and a hand-authored figure beside a generated one is the defect
   this project files against itself most often.

So the verdict goes on the front door and the figures stay on Capabilities. Where the instruction
and the ruling disagreed, the ruling won and the departure is written here rather than made
silently.

## What stops the new paragraph rotting

A sentence about the *current state of the evidence* rots, and this one rots in the **flattering**
direction if left alone: a page still refusing to name a direction after the evidence resolved is
understating what we know, and **nobody files a defect against modesty.**

So it is keyed to the property, not to today's answer. `data-selection-verdict="withheld"` is the
machine-readable form, and `tools/generate_dashboard_data.py::_check_front_door_selection_verdict`
holds it against `value_arms.json`'s own `current_world.selection_leg.resolved` on **every publish,
in both directions** — red if the leg resolves and the page still refuses, red if the page names a
direction the run does not support. Same mechanism and same reason as `data-mix-claim` two sections
above it on the same page. It is declared in `PUBLISH_VERDICT_CHECKS` naming `/` as the page it
guards, so the reachability ratchet can see it.

**The grammar says both words from the day it ships.** `withheld` and `resolved` are both writable.
That is not symmetry for its own sake: this file's sibling gate offered only `gt` for six days in
August while the book was domestic, so the true claim was *unwritable* and the refusal read as
"you typed it wrong" when the answer was "the vocabulary cannot say what is true".

## The control, and its poison round first

`tests/tools/test_the_front_doors_selection_verdict_cannot_rot.py`, 25 assertions green.
`test_the_gate_is_reachable_at_all` runs **before** any direction is asserted: it passes the gate
against the real front door and real feed, then flips **only** the feed's verdict and requires red.
Without it, "the gate passed" means two opposite things — the page agrees with the feed, or the
gate is reading neither side. The rest covers both agreeing directions, both disagreeing
directions, three unparseable-claim shapes, three unreadable-feed shapes and both missing-file
shapes; every failure branch is fail-closed, because if a missing attribute read as a pass then
deleting the attribute would be the cheapest way to silence the gate while the paragraph went on
making its claim to every reader.

**What this control does NOT do:** it controls the gate, not the render. Whether the paragraph is
on a page a reader can open is `test_publish_blockers_guard_a_reachable_page.py`'s question, and
that control parses the conjunction out of `generate()`'s source — so it, not a copy of the list
kept here, is what fails if this check is ever dropped from the verdict.

## What is next, and it is not more of this

1. **Forty-five unrendered feeds are a standing hazard, not a tidiness problem.** `simplified.json`
   alone holds 130 selection-word claims that no reader meets and no gate guards. The question is
   not "are they honest" — it is *why a publish cycle is still generating them*. That is a
   generator-cost and a rot-surface question, and it is the next thing this seat should ask.
2. **`proof.json.verification.honest_holds` reaches nobody.** 140+ notes describing what holds
   honestly, published nowhere. Either they get a reader or they stop being written; today they are
   the shape a false clean bill is issued from.
3. **The `.hypo` paragraph's own claim is still unmeasured on two of three currencies.** Carbon is
   designed and unwired, time does not exist. The front door already says so. Nothing owed here.
4. Not owed: re-running the decomposition on the current book. `value_arms.json.headline` already
   states that the floor decomposition was measured where the arm priced 104 of 2,009 renewals
   against the published run's 214 of 2,035, and declines to state a remedy in units the page no
   longer has. That refusal is correct and this sweep does not disturb it.
