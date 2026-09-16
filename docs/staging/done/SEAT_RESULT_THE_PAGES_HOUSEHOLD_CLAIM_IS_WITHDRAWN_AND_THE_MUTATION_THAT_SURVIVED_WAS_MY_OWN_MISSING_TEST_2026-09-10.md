**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the value-arms page must stop claiming per-household inference it cannot evidence) · **Class:** measurements_that_mirror

# RESULT — the page's household claim is withdrawn, and the mutation that survived was my own missing test

Three legs, one landing, over `tools/generate_value_arms_data.py`, `site/capabilities/index.html`,
`site/data/value_arms.json` and a new door control.

---

## The premise was LIVE, not spent

The draw's own premise check said the cited commit `8b846013e` is already an ancestor of
`origin/main` and warned the work might have landed by another route. **It had not, and the check
was reading the wrong thing.** `8b846013e` being an ancestor is not evidence the defect is fixed —
it is the *producing commit stamped inside the artefact*, and the whole point of leg (c) is that it
is OLD. Re-measured at HEAD `04a7e5a57` before starting:

```
git show 8b846013e:company/pricing/value_based_renewal.py | grep -c departure_cost_gbp   ->  0
git show HEAD:company/pricing/value_based_renewal.py      | grep -c departure_cost_gbp   ->  9
```

So the page's book was priced by an arm that charged nothing for a departure, the live arm charges
the sourced replacement cost, and nothing on the page said so. Premise confirmed live.

## Leg (a) — the household claim, withdrawn

Reproduced the finding's figures exactly from the canonical artefact before writing any code:

| | unstratified | within-year |
|---|---|---|
| concordance | 0.6270 | **0.4440** |
| pairs | 3,320 | **402 (12%)** |
| null 95% | 0.391–0.609 | **0.376–0.619** |
| two-sided p | 0.023 | **0.375** |
| inside null | no | **yes** |

The arithmetic is **imported, not restated**: `run_value_cycle_ab._concordance` is the same call
that computes `discrimination_auc` itself, and over the whole population it returns the artefact's
own figure to full precision (`0.6269578313253013`). Stratifying is a subset of that call, so the
page and the artefact cannot hold two answers to one question.

**What changed for the reader.** The sentence *"so on this population the belief carried real
information about who stays"* is gone as a claim. It is now gated on the stratified figure: a run
whose belief ranks households within their own year gets it back, with nobody editing a string.
The words are kept, quoted, as the fifth `withdrawn_claim` row.

**What is NOT claimed.** 0.444 inside its null means the sample cannot tell *in either direction*.
A control asserts the page never says the belief is uninformative — that is the same overclaim
mirrored, and it is the one a page correcting itself is most tempted into.

## Leg (b) — the leg is not the value of choosing

Measured from the artefact rather than taken from the item: the cap binds **143 of the value arm's
214** priced decisions and **0 of the level arm's 281**. Both artefacts agree, which is exactly why
reading the wrong one would have gone unnoticed. The block reads the **current-world re-run**,
because that is the run `current_world.selection_leg` is drawn from — my first fixture bent the
canonical run and asserted on the re-run's block, and the null control caught it.

The confound is in the **estimand**, not the sample: no larger book removes it. `what_would_remove_it`
names the exogenous bound flag that would.

## Leg (c) — the objective is named

`producing_commit.objective` reads both blobs and reports whether the renewal objective moved. It is
keyed to the property, not to `8b846013e`: pinning the answer would leave the caveat on the page,
stale and now false, the day a post-departure run is promoted. Unreadable blob → `established:
false`, never a `False` that would publish "charged nothing for a departure" off a failed subprocess.

---

## THE FINDING I DID NOT GO LOOKING FOR — two of my own controls were tautological

The suite went green at 13/13. **The poison round is the only reason it is not still green and
worthless.**

**P1 — dropping `_within_year_clause` from the reading fired ONE of the four tests that name it.**
The other three passed because `withdrawn_claim.note` renders into `arms-note` and contains the
words "WITHDRAWN", "same year" and "either way" *in its own right*. A whole-page substring check was
therefore satisfied by the withdrawal RECORD while the READING stayed completely uncorrected —
green from a different mechanism than the one the test named. Every reading-level assertion is now
scoped to the element that carries the reading (`arms-decisions`), not the page.

**P6 — deleting the second `<strong>` from the door survived all 13.** The reading's prose repeats
the same numbers ("the concordance is 0.444 … on those 402 pairs"), so a substring check cannot
tell a *rendered figure* from a *mention*. That distinction is the entire deliverable: a reader
weighs the bold numbers and skims the sentence, which is how 0.627 became the page's claim in the
first place. Per CLAUDE.md — *a mutation that does not fire is either a missing test or an
equivalence, establish which* — this was a **missing test**. `test_the_stratified_figure_renders_AS_A_FIGURE_and_not_only_inside_the_prose`
now asserts the markup.

Final battery, all firing: 7 poisons, 7 distinct reds, 14 green at rest.

## What I did NOT do, and why

`tools/generate_value_arms_data.py` carried **another lane's uncommitted rework** of the published
supplier check (hunks 3–9, 22–24 — the `run_output_latest.json` → `dashboard.json` move written up
in `SEAT_RESULT_THE_PUBLISHED_SUPPLIER_CHECK_NOW_READS_ONLY_COMMITTED_BYTES_…_2026-09-10.md`). A
pathspec would have carried their half inside mine. Landed via `isolate_hunks` + `surgical_land
--content` — HEAD plus my 14 hunks only. Their work is untouched in the working tree.

The feed was regenerated **from the isolated producer**, not the working-tree one, so it does not
carry their uncommitted changes. Verified purely additive against HEAD's committed feed: 57 keys
added, **0 removed**.

## What is next

1. **`is_the_published_supplier` still oscillates** at HEAD — my feed carries whatever today's disk
   says, which is the defect the other lane is mid-fix on. Not mine, not made worse, but it means
   this path will keep flipping until their work lands.
2. **Promote the departure run to canonical** — remedy (1) in the objective finding. Naming the
   objective was explicitly the smaller move that fails closed; it does not replace promoting.
3. **Carry `ceiling_bound` onto `belief_vs_outcome.scored_decisions`** — one field, and it makes the
   belief-side bound question answerable from the artefact with no new instrument.
