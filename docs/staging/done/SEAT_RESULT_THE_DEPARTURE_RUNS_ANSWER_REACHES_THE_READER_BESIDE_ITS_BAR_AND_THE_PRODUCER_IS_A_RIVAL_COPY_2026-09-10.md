**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — read-the-departure-runs-answer-it-finished-ninety-minutes-ago-and-is-untracked)

# The departure run's answer reaches the reader beside its bar, and its producer is a rival copy

**2026-09-10, scheduled tick.** The drawn item asked for three things. Two were already spent when
this tick measured them, and saying so is the first half of this record.

| Leg | Item says | Real state at draw time | Verdict |
|---|---|---|---|
| 1. Land `docs/observability/value_cycle_ab_s1_three_arm_departure_20260909.json` | untracked on disk | **tracked and clean**, landed at `dd9dc9451` | **spent** |
| 2. Grade P7–P10 against the predictions at `8a1164c5e` | ungraded | **graded in the same commit** — P7 refuted on both legs and in the opposite direction, P8 confirmed, P9 reported, P10 met by a route it did not anticipate | **spent** |
| 3. Carry the reading to `site/data/value_arms.json` beside the leg it explains | not carried | **the feed had no second draw of the choosing leg at all** | **done here** |

The premise check printed on the item was right about the mechanism and wrong about what was left:
`8a1164c5e` is an ancestor of `origin/main` because it is the PREDICTIONS commit, which the grading
is measured *against* — not because the grading had landed. It had, at `dd9dc9451`, ninety minutes
later. Leg 3 was the whole remaining item.

---

## What a reader now meets

`#arms-errorbar` on `site/capabilities/` — the panel that already carries `£319` and the
`±£1,811` — now renders, immediately after the sentence naming the figure the bar bounds:

> A SECOND DRAW, WITH THE OBJECTIVE CHANGED. The same book, the same world and the same seed,
> re-run once after the renewal objective was made to pay for the departures it causes, puts the
> choosing leg at **-£335** instead of **£319** — the price level explaining 102% of the arm's
> advantage instead of 98%. That move is **£655** on a quantity whose own 9-seed spread in this
> same world is **£1,811**, so it is ONE DRAW inside the bar above and not a change in the answer.
> It changes no sign, because there is no sign to change: the same figure re-drawn across those
> seeds falls on BOTH sides of zero, and both of these draws sit inside that family. This page
> stated no direction for the choosing leg before the re-run and states none after it.

…followed by the two readings that explain the size of the move: **139 of 215** priced renewals
still had their margin set by a bound, so a changed objective can reach at most 76 of them; and the
method's ranking sits inside the no-information interval on **both** runs (0.5338 → 0.5442), so the
re-run distinguishes the method from chance in neither direction.

**Placement is the point and it is what the door rung asserts.** Both draws, the spread and the
one-draw claim must render in the SAME element; "beside the figure" and "in a footnote" are the
same feed and different pages.

## The four things established before the two runs were differenced

Two figures from two runs are not a quantity until they are. `_departure_term_rerun` refuses to
state a move unless all four hold, and publishes the two figures side by side without a difference
when they do not: **same world** (`39a192ce04c1eda8` on both), **same clock** (settled-realised),
**same book** (the control arm's settled counts, which no arm's pricing can move), and a **tree
difference that is actually the objective**.

The fourth is the one worth writing down. The artefact carries **no field saying its objective had
a departure term** — the two runs' `arm_identity` blocks are identical, and the only thing that
says "departure" is the FILENAME. A filename is not evidence, and this project published a subject
inferred from two figures agreeing four days ago. So the difference is established by parsing
`company/pricing/value_based_renewal.py` **at each run's own producing commit** and asking whether
`expected_value_gbp` takes a `departure_cost_gbp` argument at all: `8b846013e` no, `e1895d6c8` yes.

**The poison round came first, because "returns False" has two causes.** The baseline tree's copy
of that module contains the word `departure` — in a docstring about a null interval — 1 time, and
the re-run's contains it 27 times. A substring scan answers this question by counting prose and
gets the baseline WRONG. `test_the_objective_difference_is_read_from_the_TREES_and_never_from_the
_filename` asserts the word is present before asserting the answer is False, so the day the
docstring goes away the control says its own round is spent rather than passing vacuously.

## Keyed to the family, not to today's answer

`changes_no_sign` is true **because the nine-seed family straddles zero** and for no other reason.
Not because the two draws have opposite signs — two draws of opposite sign are what a straddling
family produces, so reading the sign question off the draws would answer it with itself. A floor
whose family lands wholly on one side of zero stops the no-sign sentence, which is exactly when it
should stop: `test_a_seed_family_wholly_on_ONE_side_of_zero_stops_the_no_sign_claim` is that leg,
and it reds under the draws-based mutation.

## The finding: the producer in the shared tree is a rival copy of a newer lane

Measured on real disk this tick, and it is the reason this landing went in by `--content`:

```
HEAD:tools/generate_value_arms_data.py                  7,366 lines, has _published_dashboard_net
working tree copy (another lane, uncommitted)           ~7,450 lines, has NEITHER of HEAD's two
                                                        published-run identity functions
HEAD:build(three_arm, floor, published_run, decomposition, current_three_arm, current_floor)
worktree:build(three_arm, floor, decomposition, current_three_arm, current_floor)
```

Both copies are live work; the working-tree one is a **second sitting on the published-supplier
check dated today**, not a stale checkout. The consequences, each measured rather than reasoned:

* **Two door controls are red in the shared tree and green in a clean HEAD extract** —
  `test_MUTATION_an_unbounded_current_figure_is_never_rendered_bare` and its sibling. Their fixture
  calls `build` with six positional arguments, which the working copy's five-parameter signature
  binds to the wrong slots, so the current-world block reads "no re-run was readable". Neither red
  is about this work and neither is about their work being wrong: it is one file at two revisions.
* **Regenerating `site/data/value_arms.json` in the shared tree publishes the OTHER lane's
  half-finished producer.** This tick did exactly that before it noticed. The feed landed here was
  regenerated from a clean `git archive HEAD` extract with this lane's hunks applied to HEAD's
  copy — HEAD + mine, and nothing of theirs.
* **A pathspec land of these paths reverts `ec16e98f5`.** Which is why all five paths were landed
  with `--content` from files kept outside the repo.

**What is NOT done and is owed:** the two lanes' hunks in `tools/generate_value_arms_data.py` are
left co-resident in the shared working copy on purpose, so that whichever lane lands next carries
both rather than deleting one. That is a mitigation, not a fix — if the other lane lands by
pathspec from a tree it refreshed to HEAD, this block goes with it. The class is
`SEAT_FINDING_THE_WHOLE_VALUE_ARMS_CLUSTER_IS_TWO_LANES_IN_FIVE_FILES_AND_A_PATHSPEC_LAND_DELETES_EITHER_HALF_2026-09-08.md`,
which is still live and now has a fifth instance.

## What this does not settle

The same thing the run did not settle. One world, one seed, 215 priced decisions. The move is a
third of a standard deviation on a family that spans zero, and the page says so where the reader
meets it. **The ranked next step is unchanged by this landing and sharpened by the run behind it:**
while 65% of the arm's answers are set by the lawful cap, no change to the objective can be
measured on the book — and moving that is a fidelity change that must be decided blind to what it
does to this delta.
