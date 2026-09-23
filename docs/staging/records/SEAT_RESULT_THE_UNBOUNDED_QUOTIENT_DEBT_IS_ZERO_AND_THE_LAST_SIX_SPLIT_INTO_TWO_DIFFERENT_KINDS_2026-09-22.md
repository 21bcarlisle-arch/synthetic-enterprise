**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The unbounded-quotient debt is ZERO, and the last six were not six of one thing

**Severity note:** all six sites published a plan-grammar count over a denominator nobody had
classified. None of the six was WRONG on today's record — every published figure is unchanged by
this repair, verified byte-for-byte against the regenerated artefact — so nothing downstream was
misinformed. What was missing is the statement of which kind of denominator each one divides by,
and that absence is what the class control exists to refuse. No instrument in this area is left
untrustworthy by this document.
**Filed:** 2026-09-22, delivery seat.
**Claim:** `the-unbounded-quotient-six-remaining-debt-sites-and-the-page-that-renders-empty`

---

## The premise was LIVE, against the draw's warning

The draw flagged all three cited commits as already ancestors of `origin/main` and named a rival
claim holding this very id. I re-measured both before building:

* `python3 -m tools.unbounded_quotient_census` on my base read **6 DEBT** — the work was not spent.
  The landed commits are the *class control* (`d93b8fb88`, `08c696269`, `5973f923b`), which
  lowered the ceiling to 6 and explicitly left the six as "a real list rather than a residue".
* The "rival claim" is **my own draw**. `.seat_work_in_hand.json` does not exist on the shared
  tree at all, so there is no second holder. This is the known shape where the duplicate-work
  check cites the drawing session back to itself.
* My worktree is exactly `origin/main` (0 ahead, 0 behind after fetch), so the draw's
  `[stale-copy]` base caveat and its five `already landed` / one `predates landing` verdicts
  describe the SHARED tree and not this one. I read my own copies, which are HEAD's.

## The six are TWO KINDS, and that is the result

The item called them "6 remaining undeclared-quotient sites". They are not six instances of one
thing, and grading them all the same way would have been the easy wrong answer:

| Site | Denominator | Grade | Why |
|---|---|---|---|
| `fit_year_level_anchor:992` `required_over_re_referenced_recent` | `SVT_INERTIA_ANNUAL_RECENT` × a ratio of two OBSERVED departure rates | **BOUNDED** | chosen constant × closed-record observable |
| `fit_year_level_anchor` ×2 `hazard_multiple_still_required_at_band_low` | the world's MEASURED SVT hazard | **GATED** | no lower bound; needs a real bar |
| `run_value_cycle_ab:7209/7210` `priced_decisions_needed`, `independent_draws_needed` | `contrast² − v_except` | **GATED** | bar existed, 230 lines away |
| `run_value_cycle_ab:7236` `..._on_the_published_floor` | `contrast² − (1−share)·v_all` | **GATED** | bar existed, unnamed |

**Printed at real inputs before anything was written**, per the rule that caught two wrong drafts
of the competitor model. The BOUNDED claim is measured, not asserted: across the whole 2016–2025
record the site-1 denominator runs 0.0388 (2022, the crisis trough) to 0.2077 (2020). Reaching
zero needs an observed GB departure rate of exactly zero in a year of the record, which is not a
state the record can enter. That is a property, not today's answer.

## The hardest one, and the trap I nearly walked into

`hazard_multiple_still_required_at_band_low` already had a guard: `if svt_pp > 0 else None`. The
census grades it DEBT anyway, and it is right to — its own docstring names the reason: *a guard
against a degenerate input and a withholding on a failed bar are different statements that
collapse into the flattering one the moment you only ask whether `None` is possible.*

The tempting repair was to rename a variable so `svt_pp > 0` matched `GRADE_VOCAB` and add a
sibling reason key. **That is gaming the control**, and it would have produced a green ratchet over
a site nothing had classified. I did not do it.

Instead I established what the denominator IS. The algebra collapses:

```
svt_pp = pp_of_book × (target / world_share)  ==  100 × world_hazard × target
```

verified numerically (2017: 8.2183 / 0.6195 / 100 = 0.13265 = `world_svt_pp_of_book` /
`world_svt_account_day_share` / 100). So the denominator is the world's **measured SVT hazard**,
and `target` is bounded by a `raise ValueError` three lines above the site. The multiple is
`required_hazard / world_hazard` — the same family as site 1, dividing by a measured quantity
where site 1 divides by a published one. That is exactly the distinction the enclosing function's
own docstring already warns about: *"quoting one as the other is how two correct figures become a
quantity that is not one."*

**The bar is this file's own, and nothing here chose a threshold.**
`_SVT_FACTOR_CEILINGS["hazard"] = WORLD_MAX_CHURN_PROBABILITY`, already established, and
`years_a_factor_could_close_alone` already divides by it. A multiple putting the hazard above that
ceiling is not a plan, because no world runs that hazard. Corroboration that this is the right
quantity rather than a convenient one: `tools/published_route_split.py:1127` already forms
`H_joint = world_hazard × hazard_multiple_still_required_at_band_low` — the downstream consumer
was already multiplying these two together.

Priced before it was written:

| year | world hazard | ceiling multiple | required (min..max) | headroom |
|---|---|---|---|---|
| 2017 | 0.13265 | 7.16 | 1.455 .. 1.664 | ×4.3 |
| 2018 | 0.19081 | 4.98 | 1.464 .. 1.617 | ×3.1 |
| 2019 | 0.19719 | 4.82 | 1.650 .. 1.894 | ×2.5 |
| 2023 | 0.09355 | 10.16 | 0.722 .. 0.937 | ×10.8 |
| 2024 | 0.11456 | 8.29 | 1.041 .. 1.239 | ×6.7 |

The ceiling multiples 4.82–10.16 reproduce the file's own line 825 ("a multiple of 4.8 to 10.2")
exactly, which is the check that I am using its quantity and not a new one.

## The gate withholds NOTHING today, which is why the partition control comes first

Green on all twenty rows. A suite that only asked the published artefact would be equally green
against a gate wired shut and against no gate at all — this project's most-repeated trap, entered
three times in one afternoon through three different doors. So
`test_the_partition_is_WHOLE` asserts a published row, a ceiling-withheld row and a no-hazard row
all come out of one call, **before** any leg asserts what either side does.

`test_the_gate_turns_on_the_HAZARD_and_not_on_the_multiple_alone` is the one that keys it to the
property: the same required multiple of 6 is a plan at a hazard of 0.09 and is not one at 0.19.
A threshold pinned to the multiple could not tell those apart, and would publish the second.

## Mutation-proven, including one that survived

| Mutation | Verdict |
|---|---|
| gate removed (always publish) | KILLED |
| gate wired shut (never publish) | KILLED |
| ceiling comparison inverted | KILLED |
| point estimate dropped to the gated value | KILLED |
| no-hazard refusal gutted to `"withheld"` | **SURVIVED** → missing leg, now killed |
| ceiling number dropped from the refusal | KILLED |
| ceiling refusal's first sentence reworded | **SURVIVED** → equivalence, established below |

The fifth was a real weakening: asserting only that the two refusal reasons *differ* passes a
refusal gutted to one word. The leg that kills it asserts each names its own cause. Recorded here
rather than silently patched, because the first control could not fail in that dimension.

The seventh is a genuine **equivalence for the property under control**, and I established that
rather than assuming the flattering reading: the mutation rewords prose while preserving both
format slots, so the refusal still names its cause and still carries both numbers a reader needs
to check it. The adjacent mutation that *does* remove the ceiling number is KILLED, which is what
makes the equivalence claim checkable rather than an excuse.

## What landed

* Six sites declared; **debt 6 → 0**, ceiling lowered to 0 in the same commit as the repair.
* `_composition_accounting` — one helper for both accountings, so a gate cannot be added to one
  and missed on the other. That is why the population moved 27 → 26: two sites became one.
  `POPULATION_FLOOR` was deliberately NOT raised to match, or the next honest de-duplication reds.
* `DECLARED_BOUNDED` — a second pinned set. A `#: DENOMINATOR BOUNDED:` comment is deletable in a
  tidy-up with no count moving, and swapping a gate for a bounded declaration is a silent
  weakening (a gate withholds, a declaration publishes) that a merged set would grade as no change.
* **No published figure moved.** Regenerated `svt_composition_vs_published.json` and diffed: 0 of
  20 rows changed their multiple; three declaration keys added, none removed.

## Filed, not fixed

**ZERO IS NOT "FINISHED", and the ceiling comment now says so.** The census resolves names one
function deep; a count assembled across two functions or through a dict round-trip is INVISIBLE to
it rather than clean. `scored_decisions_needed` is one such site. A zero on this ratchet says every
site the scan CAN see has been classified — which is the claim it is entitled to make and no more.

**Two pre-existing reds in `tools/run_value_cycle_ab.py`'s neighbourhood, NOT mine.** Reproduced on
a clean `git archive HEAD` extract before I blamed my diff:

* `test_every_promote_target_producer_declares_its_run_identity[tools/run_value_cycle_ab.py-producing_commit]`
  — lines 5784, 5817 write a promote-by-copy artefact without `run_identity_fields`. My edits are
  at ~6990 and ~7209 and cannot reach it.
* `test_the_requirement_is_stated_in_both_units_and_they_are_not_the_same_number` — `times_this_run`
  is `None` in `tools/generate_value_arms_data.py`, a file my diff does not touch.
