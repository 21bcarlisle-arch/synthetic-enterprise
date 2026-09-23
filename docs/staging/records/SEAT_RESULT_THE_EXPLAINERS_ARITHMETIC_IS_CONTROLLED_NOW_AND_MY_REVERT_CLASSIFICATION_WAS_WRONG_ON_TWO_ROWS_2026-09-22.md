**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** `W1_14_weather_cells_for_household_heat_load`

# The explainer's arithmetic is controlled now, and my own revert classification was wrong on two rows

**Filed:** 2026-09-22 · **Claim id:** `land-the-weather-hdd-pile-written-twice-and-committed-never`
**Lands:** `tests/tools/test_explain_premise_year.py` — the only artefact of this turn that was not
already on origin by the time it was ready.

---

## What happened, plainly

I drew the Lane 0 item, separated the pile, gated and committed the HDD repair as `92b156770`, and
`promote_worktree_landing` refused: a rival lane had landed `a2145439a` carrying the same work. All
seven paths were **byte-identical**, including the same `I001 1307 -> 1306` ratchet remedy. I
discarded mine. I then built and committed the remaining stranded piece — `tools/explain_premise_year.py`,
its orphan-baseline freeze, a finding and a result note — as `6698ff588`, and promotion refused
again: `ce4a60430` had landed the tool and the identical baseline row meanwhile.

Two independent lanes converged on the same separation and the same remedies twice in one night. That
is worth recording as evidence the split was the obvious one once the diffs were read — and as
evidence that reading them is the whole job, which is why the item's own framing was dangerous.

**Nothing I wrote about the revert class is being landed**, because
`WORKER_RESULT_FIVE_OF_THE_EIGHT_FILES_THE_ITEM_CALLED_A_FINISHED_PILE_WERE_REVERTS_OF_FIXES_ALREADY_AT_HEAD_2026-09-22.md`
is already on origin, is BLOCKING, and is better than my draft. A duplicate finding is noise.

## Where I was WRONG, and the other lane was right

I classified `simulation/premise_population.py` and `tests/simulation/test_premise_population.py` as
**"the settlement-ceiling/cgroup lane's live work"** — a different subject, not a revert, which a
pathspec would have swept. That is wrong. They are **reverts**, exactly like the three 09-17 files:
the working copies delete `WHOLE_RUN_RSS_CURVE_GLOB` and the cgroup-anchored constants landed by
`9c84f054d`, and offer the earlier `SETTLEMENT_CEILING_SLOPE_DIR` draft in their place. The test
sibling deletes `test_the_customer_year_ceiling_prices_the_RUN_and_not_a_data_structure`, the control
written hours earlier for precisely that.

**How I got it wrong is the reusable part.** I found the three 09-17 reverts by reading diff
DIRECTION, then confirmed them with mtime against the last commit to touch the file. For
`premise_population.py` I read the diff, recognised vocabulary from the ceiling lane, concluded
"different subject", and **never ran the mtime check on it** — I applied my own instrument only to
the files I had already convicted by another route. A test that is only run where you already suspect
the answer is not an instrument; it is a confirmation. The one-line check is cheap enough to run over
every path in a pile before choosing any of them, and that is how it should be used.

The direction cue that misled me: seeing `SETTLEMENT_CEILING_SLOPE_DIR` **added** and
`WHOLE_RUN_RSS_CURVE_GLOB` **deleted** reads as "new work arriving" unless you already know which of
the two names is the newer. Vocabulary cannot tell you that. Only the clock can.

## What this lands, and why it is worth a commit on its own

`tests/tools/test_explain_premise_year.py`. The explainer answers the director's phase-one ask —
*"look at a household's half-hourly gas and electricity for a year and believe it, and be able to say
why it looks like that"* — and it went onto origin with **nothing checking its arithmetic**. A tool
that prints four plausible paragraphs satisfies that sentence and establishes nothing.

Two legs, in one test on purpose:

1. **The reconciliation CLOSES.** `HLC x degree-days x 24 h`, less the gains covered, lands on the
   heat delivered, to within 1 kWh on an ~8,000 kWh gross — the rounding in the tool's own output and
   nothing more. The fuel side is bound too: delivered / space-heat fuel must equal the published
   boiler efficiency.
2. **2018 and 2022 DISAGREE.** This is the leg that matters and the reason the two are not separate
   tests. A degree-day total computed off `REFERENCE_MONTHLY_HDD` closes its identity perfectly and
   is still climatology — and it is *the same number in every year*. Separately, each leg passes
   against a normal. Only together can they fail. Measured: 2,037 degree-days in 2018 against 1,891
   in 2022, and the colder year must be the larger.

Keyed to the property, never to today's figure: a more faithful fabric model must move every term and
still pass. **Mutation-proven, each mutation firing on the leg written for it and not on a
neighbour** — degree-days pinned to a constant fires the disagreement leg; gains no longer subtracted
fires the identity leg (residual 1,965.1 kWh); a cause dropped from the rendering fires the rendering
leg. The tool was restored byte-identical after each.

It does **not** make the module non-orphan — the index walks `DECLARED_ROOTS`, so a test is not a
caller — and `tools.explain_premise_year` is already recorded as deliberately dormant in
`docs/design/orphan_baseline.json` by `ce4a60430`. Correctly: it is a hand-run CLI and no schedule
should run it.

## A second thing I read wrong, kept because it wears a pass's colour

With the new files still **untracked**, `orphan_ratchet --report` said *orphans 545, baseline 545*,
and I took that for "reachable". It is not: `_git_known_paths` filters the orphan set to paths git
knows, so an untracked module is **not measured**, not **not an orphan**. After `git add` the same
command said 546 against 545 and refused. The filter is documented in that function's own docstring,
which I had read. The number that means anything is the one taken after staging.

## Owed next

The mechanism both notes stop short of building: **`surgical_land` should refuse a path whose
working-copy mtime predates the commit that last touched it, naming that commit.** It is one leg, it
would have fired on all five reverting files in this pile, and it needs no register — the other lane
called the check "cheap enough to run before any pathspec is chosen", and a check that cheap belongs
in the door rather than in a habit. In-lane for `H_harness`.

The five stale working copies are still uncommitted in `/home/rich/synthetic-enterprise`, so the next
lane to draw this item meets the same trap.
