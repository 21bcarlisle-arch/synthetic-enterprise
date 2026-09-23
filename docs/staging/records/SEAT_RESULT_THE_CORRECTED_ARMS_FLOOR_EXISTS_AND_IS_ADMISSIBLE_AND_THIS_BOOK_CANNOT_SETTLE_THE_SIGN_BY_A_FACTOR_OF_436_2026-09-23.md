**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the floor drawn against the corrected arm exists, is admissible on the STRONG rule, and prices the selection sign at 436x this book

*Lane 0 delivery, 2026-09-23. Drawn item: `publish-the-corrected-one-book-baseline-comparison`.*

## What was asked, and what this settles

Re-draw the selection leg's seed floor against the frontier-sharing arm — the 2026-09-18 re-run in
which the flat-at-level arm carries the per-customer arm's own refusal frontier and the two price
ONE book — at the SAME TREE as that run, and publish it. The fallback the item named was: if the
re-drawn floor still cannot give the leg a sign, publish `what_would_settle_the_sign` as the
answer, on the expectation that it reads "91,331 renewals against the 2,035 this book offers — a
factor of forty-five".

**The floor did not need drawing: it is already on disk, and it is admissible.** The expected
factor is wrong, and wrong in the unflattering direction. **It is 436, not 45.**

## The pairing, established rather than assumed

| | run | floor |
|---|---|---|
| artefact | `value_cycle_ab_s1_three_arm_20260918.json` | `value_cycle_ab_s1_noise_floor_next12_at_18327d977.json` |
| `producing_commit` | `b329e702b` | `18327d977` |
| world | `39a192ce04c1eda8` | `39a192ce04c1eda8` |

`value_cycle_ab_s1_three_arm.json` is BYTE-IDENTICAL to the dated 09-18 copy (md5
`e87d3fc4c45db7c13069e018e5656524`) — the corrected run was promoted onto the canonical path by
`756a86272`. Its `decision_population.same_priced_population.answer` is **true**, on zero net
crossed refusals across a 3-renewal denominator gap that is entirely roster divergence. That is
the one-book re-run the page's own withdrawal note has called "not published here yet" for five days.

**The two trees are not the same SHA, and the difference is measured, not waved through.**
`git merge-base b329e702b 18327d977` **is `b329e702b`** — the floor's tree is a DESCENDANT of the
run's, so the whole difference is forward. Over the value-arm path set the producer itself uses
(`simulation/`, `company/`, `saas/`, `tools/run_value_cycle_ab.py`) exactly two files differ:

* `simulation/run_phase2b.py` **+15** — ADDS two artefact keys (`gas_shape_provider_by_customer`,
  `gas_shape_refusals`) out of values the run already computed and printed.
* `tools/run_value_cycle_ab.py` **+71 −10** — renames a DERIVED diagnostic key and adds a census block.

Both are reporting. Neither is on the pricing path.

**Checked on the OUTPUTS, not argued from the diff**, because "diagnostic only" is exactly the
claim a reader cannot verify from a line count. The floor's realised book reproduces the run's book
EXACTLY on all 12 seeds — 154 settled, 136 electricity, 90 gas, 72 dual fuel, 54–55 at end against
the run's 55 — and its level arm prices at 36.25–39.75/MWh around the run's 38.5. The
pre-correction floor at `4e7938f673` answers **164/146/105/87 at a flat 20.0**. Book and level are
pricing-path outputs; identical book and a level inside the run's own band is what "same
instrument" means here, and the 09-10 family shows what it looks like when it is false.

`_floor_admission` agrees independently and was not consulted until after the above:

* `18327d977` x the corrected run → **admitted on `declared_book`, with NO disjoint field.**
* the pair published today (`..._noise_floor_20260909b` x `..._three_arm_20260908`) → admitted only
  on the weak **`stamp_proxy`** rule, because that floor states no realised book at all.

The pairing this finding proposes is better-evidenced than the one on the page.

## The answer

Built through `tools/generate_value_arms_data.py` with the two constants moved together:

| | published today | corrected pairing |
|---|---|---|
| floor seeds | 9 | **12** |
| selection mean | −£1,078.17 | **−£259.29** |
| selection sd | £1,810.50 | **£5,413.58** |
| SEMs from zero | 1.79 | **0.17** |
| bar to state a sign | 2.31 | **2.20** |
| sign stateable? | no | **no, and not close** |

**The bounded reading is RESTORED, not lost** — `bound_available` stays true. What the correction
does not do is hand the leg its sign: the floor drawn against the corrected arm is **three times
wider**, and the leg sits **ten times further from a direction** than it did on the old arm's
narrower family. The 2026-09-18 withdrawal stays beside it.

**The price of the question, on this book:**

| figure priced against | multiple of this book | renewals the world must offer |
|---|---|---|
| the published draw (£4,327.01) | 1.57x | 4,430 |
| **the centre of its own re-draw family (−£259.29)** | **435.9x** | **1,231,930** |

against the **2,824** renewals this book offers. The item's expected 44.9x / 91,331 was computed on
the OLD, three-times-narrower floor and on a 2,035-renewal book; it does not survive the correction.

**And the seed route has NO UPPER BOUND.** `seeds_needed_to_state_a_sign` is `null`, not a large
number: at the point estimate it is 1,677, but the denominator is −£259.29 ± £1,562.77 and **that
interval contains zero**, so the price rises without limit between its ends (37 at one end, 69 at
the other, and the two are not a range). This is the `V/c²` shape — an undetermined sign gives no
upper bound — and the producer's machinery already reports it correctly.

**"This book cannot settle the selection sign, by a factor of 436" is the finding.**

## What landed, and what did not

**LANDED:** a ZeroDivisionError in `_the_shares_own_null` that takes the WHOLE generator down.
`times_the_observed_disagreement` guards `observed > 0`; the `statement` branch three lines below
it did not, and evaluated `null_range / observed` unconditionally. One legal rule, two
implementations, the guard on only one. It is reached whenever the page's two panel constants
resolve to one artefact — **which a promotion onto the canonical path does on its own, with no
constant edited.** Fixed with the two causes of a zero gap kept apart: a run compared with ITSELF
replicated nothing, and two runs returning the same share are a coincidence inside a wide null;
a reader told only "the shares are equal" would take either for a replication. Three mutations
run and reverted, each redding its intended leg.

**NOT LANDED — the publish itself.** Moving `CURRENT_WORLD_THREE_ARM_PATH` onto the corrected run
requires a decision about the OTHER panel, and both routes were built and measured:

* **Leave `THREE_ARM_PATH` on the canonical path.** Both panels become ONE artefact.
  `_what_differs_between_two_runs` returns `the_same_run: true`, `#arms-headline` renders the
  selection figure £4,327 TWICE, and
  `test_the_figure_from_the_world_that_is_live_reaches_the_reader_and_never_as_resolved` refuses —
  correctly, because neither that rung nor a reader can tell which panel a repeated figure belongs
  to. **3 doors red.** `is_the_later_run` also reads TRUE for a run that is not later but
  IDENTICAL: its test is a strict `<` on the two stamps, so "same" falls into the flattering
  branch. It needs a THIRD state, and `_withdraw_a_verdict_stated_from_a_superseded_run` would
  publish the wrong words on it (our run is not superseded, it is the same run).
* **Move `THREE_ARM_PATH` to the dated `_20260908` run**, restoring its documented
  "superseded-with-provenance" role. The two panels are genuinely two runs again,
  `is_the_later_run` is correct and `the_same_run` is false — but `THREE_ARM_PATH` also feeds the
  error-bar and detectability blocks, so **7 doors red**: the error bar, the detectability
  sentence, the pair-stratum attribution, the conditioning column, the inversion attribution and
  two mutation rungs on `arms-legs-first`.

Baseline is green (181 passed) in a clean HEAD worktree, so both counts are attributable to the
move and to nothing else.

**The next increment is the three-state ordering**, not the constants: `is_the_later_run` cannot
express *later* / *earlier* / *same run*, and until it can, the first route publishes a
contradiction and the second is a wider change than the leg it is meant to serve.

## One of the seven origin/main reds is cleared, and its cause was not the one it looked like

`test_every_untied_here_relative_literal_has_a_recipe_that_drives_its_branch` names
`_renewal_stratification`. It is red at HEAD and **invisible to every lane that is not editing
`generate_value_arms_data.py`**, because `pre_commit_test_gate` selects this file by its subject
module's stem — so it blocks whichever lane arrives next, for a sentence that lane did not write.
This is the shape the seven-reds finding describes, and this is one of them.

**It reads GREEN in the shared worktree.** One variable at a time, producer held at HEAD and only
`site/data/value_arms.json` swapped:

| feed on disk | rung |
|---|---|
| the COMMITTED one | **red** |
| the one sitting dirty in the shared tree | green |
| one regenerated from the committed producer seconds earlier | **red** |

The census classifies a literal tied/untied against whatever feed is on disk, so a lane's working
copy and the gate — which builds HEAD plus that lane's own hunks — can reach opposite verdicts.
**Regenerating the feed does not fix it**; that was tried first and it stayed red. The fix is a
recipe, which is what the rung's own message says and what landed.

**And registering the pointer caught a second thing the prose hid.** The refusal said a reader
cannot tell "which of the two concordances **the figures above** are". Probed, the two
concordances and the refusal both render in `#arms-renewal-belief` — the SAME region — so "above"
sent a reader back past a panel they had not passed. Corrected in the producer to "beside this",
which is the same repair, from the same cause, as `_against_the_superseded_panel`'s in September:
**found by registering the referent, never by reading the prose.**

## A trap worth recording

`fork_salvage` committed this invocation's uncommitted edits in a scratch worktree and moved that
worktree's HEAD — `git status` read CLEAN and `git checkout <path>` reported "Updated 0 paths"
while the edits were plainly still in the file. Two `SALVAGE(auto)` commits sat on top of the
detached HEAD. A scratch worktree reading clean is not evidence your edits are gone.

## Not mine, and blocking every lane

`tests/tools/test_generate_maturity_map_data.py` is dirty in the shared tree and has FIXED an I001
without the ratchet baseline being lowered: the census reads 1,305 against a frozen 1,306, and
`test_ruff_baseline_matches_frozen_census` reds for every lane. A clean HEAD worktree passes the
same suite. The owning lane should lower the baseline in the commit that lands the fix.
