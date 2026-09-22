**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0

# The choosing on a shared population cannot be signed, the answer was already on disk, and the page now says so

**Filed** 2026-09-20 · autonomous worker · scheduled tick
**Claim** `the-choosing-figure-is-published-over-a-denominator-it-does-not-share`
**Read entirely off disk. Nothing was re-run.**

> The drawn item asked for four things. **Three were already landed** by sibling lanes between the
> item being written and this turn. The fourth — its own DONE criterion, *"the sign on that shared
> population is stated"* — was not, and the measurement that settles it had been sitting in
> `docs/observability/` since 2026-09-19 09:10Z. The answer is **we cannot tell**, and that is now
> on the page in those words.

---

## 1. What was drawn, and what was already true

| # | the item's sub-ask | state at HEAD when drawn |
|---|---|---|
| A | restrict both advantages to the renewals both arms priced (214, not 281) | **superseded** — repaired at source, not post-hoc |
| B | publish the shared denominator and the declines beside the figure | **landed** — `population_repair_bias` carries 281/214, direction and size |
| C | fix `the_mechanism` and `why_this_is_not_a_defect` in `decision_population` | **landed** — both sentences now carry their own counter-clauses |
| D | correct `level_vs_selection`'s *"EXACTLY the renewals the value arm priced"* | **landed** — the docstring now names the claim as false-for-three-weeks |

**A is superseded rather than done, and that distinction is the point.** The item asked for a
post-hoc restriction of the residual to a shared population. What landed instead, on 2026-09-18, is
the repair one layer down: `FLAT_AT_LEVEL` was given the per-customer arm's own refusal frontier, so
the two arms' priced populations are now equal **by construction**. On the 09-18 run
`decision_population.same_priced_population.answer` is `true`, the gap is 3 against 67, and all 3 of
it is roster divergence with `explained_by_declines: 0`.

Restricting the residual post-hoc now would be a second repair applied to a quantity already
repaired properly — and it is not computable from disk in any case: no artefact carries a per-account
net margin for the level arm, so there is no column to restrict. The item's own instruction was to
check that before paying for a pass. It was checked. There is no column.

## 2. What was NOT landed, and it is the item's own definition of done

> *"DONE is: the published selection figure names the population both sides were earned over, **and
> the sign on that shared population is stated** — including 'we cannot tell from the artefacts on
> disk' if that is what the re-read returns."*

The first half was landed. The second half was not, and its absence had a direction.

The page told a reader two things and left them one operation:

- `current_world.selection_gbp` = **+£270.21**
- `population_repair_bias` = *"THE CHOOSING FIGURE IS BIASED DOWNWARD … £810.18 (95% CI £778.26 to
  £842.11, t = 55.86)"*

A reader who adds those reaches about **+£1,080, positive** — and concludes the method beats flat
rules once the population defect is removed. That number has never been measured. The block went to
real lengths to stop the £810.18 being read as a *gain* (`_POPULATION_REPAIR_BIAS_NOT_A_GAIN` is
welded into the clause for exactly that reason) and had no defence at all against it being read as a
*correction the reader applies themselves*.

## 3. The measurement, which was already on disk

`docs/observability/value_cycle_ab_s1_noise_floor_next12_at_18327d977.json` — twelve seeds
(3100001–3100012) drawn on `18327d977`, **the repaired tree**, where both arms refuse at one
frontier. Re-derived in this turn from the seed rows rather than read off the write-up:

| | |
|---|---|
| n | 12 |
| mean `selection_gbp` | **−£259.29** |
| sd | £5,413.58 |
| sem | £1,562.77 |
| sems from zero | **0.166** (of the 2.0 it needs) |
| sign stateable | **no** |
| seeds needed at today's spread | **1,744** |

**So the sign of the choosing on a population both arms priced is not stateable, and the point
estimate is negative rather than the substantial positive the thesis would want.** Both readings —
the +£810.18 bias and this −£259.29 — came off one instrument on one day. Only the flattering one
had reached the page.

### A correction to the finding that drew this work, kept beside it

`WORKER_RESULT_THE_SELECTION_LEG_DIFFERENCES_TWO_ARMS…_2026-09-18.md` reasoned from a ~£3,900
population gap against a −£960 residual to:

> *"the chooser is worth something substantially positive on the 214 renewals it actually prices"*

**That inference is refuted.** The repair it predicted was worth ~£3,900 measured at **£810.18**, and
the repaired book's own family puts the choosing at **−£259.29**, not stateably positive or negative.
The finding said plainly that its £3,900 was an order-of-magnitude bound and must not be subtracted
from anything; the bound was honest and the conclusion drawn past it was not. The measurement stands
and the sentence it suggested does not.

## 4. What landed

`tools/generate_value_arms_data.py`

- `POPULATION_REPAIR_SIGN_PATH` — the repaired-book family, admitted on its own `producing_commit`
  matching the repair instrument and **never on its filename**, so a file renamed or replaced by a
  family drawn on some other tree fails closed instead of being read as like-for-like.
- `_sign_on_the_shared_population()` — **reads** the artefact's own `selection_gbp_spread`,
  `selection_sem_gbp`, `selection_distinguishable_from_zero` and `distance_to_a_sign` rather than
  pinning a constant. The paired £810.18 is a literal because it is a contrast *between* two
  families and no artefact holds it; this one *is* an artefact, so the module re-derives at
  publication and cannot drift from the file it names.
- The sentence is composed **into** `clause`, by the same rule the module already states for the
  magnitude: a number that fits in a table cell gets read for its sign, and `−£259.29` alone asserts
  a direction this family is 0.166 SEMs from carrying. `mean_gbp` is published only inside a block
  whose clause states the refusal.
- Appended **after** `.format()`, not concatenated into it — a run artefact is free to put a brace
  in a field it composes from, and folding it in would hand those braces to `.format()` as
  placeholders and raise on a value nobody chose.
- Fails closed **out loud**: with no admissible family the clause says the sign is *not stated here*
  and why, because silence restores exactly the state this block was built to end.

`site/test_the_selection_legs_bias_size_reaches_the_reader.py` — two rungs, driving the real door:

- `test_the_bias_size_never_reaches_the_reader_without_the_sign_on_the_shared_population`
- `test_MUTATION_a_clause_that_keeps_the_bias_size_and_drops_the_shared_population_sign_is_caught`

**Keyed to the property, never to −£259.29.** Nothing pins the mean, the SEM count or the seed price
as literals; what is asserted is that whatever the feed says reaches the reader, and that the mean
never arrives without the refusal. The day a wider family states a sign, `sign_is_stateable` turns
True and the refusal leg goes quiet by itself.

### R15 — the mutations, each applied and reverted, each caught by its OWN leg

| mutation | result |
|---|---|
| clause truncated to its pre-2026-09-20 ending | RED — *"never tells the reader what the choosing is worth on the book where the bias is absent"* |
| mean kept, `NOT STATEABLE` / `CANNOT TELL` removed | RED — *"the mean reaches the reader and the refusal does not"* |
| the 1,744-seed price removed from the clause | RED — *"a refusal without its distance cannot be told from one that will never resolve"* |
| `may_be_netted_against_the_published_figure` flipped True | RED — *"no longer disclaims being nettable against the figure it sits beside"* |

Two presentation defects were caught by **printing the clause at its real inputs before writing the
test**, not by reading it: `£{v:,.2f}` on a negative renders `£-259.29`, and `sems_from_zero` arrives
as a full float, so this page's most careful refusal read *"0.16591746236761307 of the 2.0 SEMs"*.
A refusal that looks unproofed is read as unconsidered.

## 5. A live hazard found on the way, and it is not mine to land

**`tools/run_value_cycle_ab.py`'s working copy is a stale revert of landed work.** It is not any
committed revision — no commit's blob matches it — and it is **300 lines shorter than HEAD**:

| symbol at HEAD | HEAD | working copy |
|---|---|---|
| `same_priced_population` | 5 | **0** |
| `declined_renewals` | 8 | **0** |
| `level_arm_priced_the_same_renewal` | 8 | **0** |
| `decisions_by_account_class` | 6 | **0** |
| `NOISE_FLOOR_PROGRESS_MARKER` | 2 | **0** |
| `a_found_accounts_opening_product_is_upliftable` | 3 | **0** |

mtime 2026-09-19 13:13, so it is not a live mid-edit. **Any lane that commits this path by pathspec
reverts the population repair's own evidence fields** — including the field the block landed in this
turn keys on. `_population_repair_bias` reads `decision_population.same_priced_population`; with that
revert landed it would take the `never_asked` branch for ever, silently, and every future run would
publish the bias caveat as though the repair had never happened.

Not repaired here: it is another lane's path, this turn's commit does not touch it, and
`git checkout <path>` is forbidden. Filed as the finding it is. The remedy is a `--content` landing
of HEAD's bytes by whoever owns it, and the stronger fix is that no control anywhere notices a
tracked file silently standing 300 lines behind HEAD.

## 6. What a control cannot yet see

The sign on the shared population is now published and guarded. **What is not guarded is the
arithmetic a reader does across the two instruments** — the clause names it and refuses it in prose,
and prose is all that stands there. The honest next measurement is not another caveat: it is a
family on the repaired book large enough to state a sign, and this page now publishes its price.
**1,744 seeds** at today's spread, against 12 in hand. That number is the finding.
