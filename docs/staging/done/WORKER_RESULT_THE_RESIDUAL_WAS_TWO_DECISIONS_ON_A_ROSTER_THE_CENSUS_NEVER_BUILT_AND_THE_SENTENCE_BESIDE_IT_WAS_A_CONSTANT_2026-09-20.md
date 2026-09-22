**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, claim `finish-the-churn-truncation-residual-the-census-is-computing-now`

# The residual was two decisions on a roster the census never built, and the sentence beside it was a constant

**The disagreement this was drawn to settle.** The first assembly of
`docs/observability/churn_truncation_census_2026-09-19.json` published
`reconciliation.residual: -2` beside `reconciliation.residual_means` whose first word was
**"zero:"** — *"zero: every decision-eligible term the schedules built is accounted for"*. Two
adjacent keys in one artefact, contradicting each other, and the prose is the half a reader
believes.

Both halves are now settled, and they are settled the way the brief's first branch asks: **the
residual and the prose agree at 0**, and the two terms that produced the −2 are **named as
instances** beside them rather than absorbed into a signed integer.

---

## 1. What the −2 actually was

Not "two terms the census cannot account for". The subtraction was

```
schedule decision-eligible terms (299) − decisions that existed (114) − withheld-and-eligible (187) = −2
```

and the defect is in the **middle** term. `decisions_that_existed` counts every decision the value
arm made. `run_phase2b` walks `live_population()` **and** the Phase 7e successor legs;
`tools/svt_refusal_census` builds schedules for `live_population()` **alone**. So an activated
successor leg's renewal is a real decision on a leg the schedule census never built a schedule
for — it was being subtracted from a population it was never in.

Two such decisions exist in this world, both on `C5_2` electricity, both `priced`:

| household | commodity | term_start | term_index | tariff | stage |
|---|---|---|---|---|---|
| C5_2 | electricity | 2017-12-31 | 1 | fixed | priced |
| C5_2 | electricity | 2018-12-31 | 2 | fixed | priced |

The repaired subtraction runs over the census's own roster —
`decisions_that_existed_on_the_census_population` = **112** — and

```
299 − 112 − 187 = 0
```

The two off-roster decisions are published in full under
`reconciliation.decisions_on_terms_the_schedule_census_never_built`, each carrying *why* it is
outside the population. `decisions_that_existed` (114) is **still published**, so nothing is
hidden: the artefact states that a reader comparing 114 against 299 directly, rather than 112,
will be short by exactly two.

## 2. The sentence was a constant, and is now derived

`residual_means` was a hardcoded string. It asserted a value it never read, which is why it could
sit beside −2 for the whole life of the first artefact while its own *next clause* correctly
described what a negative residual would mean.

The remedy was **not a softer sentence**. Accepting a non-zero residual in prose converts a
discrepancy into a tolerance, which is how a reconciliation stops being one. `_residual_means` now
**derives the sentence from the number**, so the two cannot disagree — four distinct sentences for
`residual == 0 and no off-roster decisions`, `residual == 0 with them`, positive, and negative.

`what_a_non_zero_residual_would_mean` is published unconditionally as a constant beside the
residual **even when it is zero**, so a run whose residual is zero does not leave the next reader
reconstructing the rule from a sentence about zero.

## 3. What replicated, and what did not

The re-run is the **same measurement**, not a second opinion — the thing that would have made this
un-attributable:

- `world_identity`, `report_end`, `what_this_is` — **identical**
- `renewal_funnel` — **identical** (2,943 renewals offered, 111 priced, 3 declined)
- `terms_never_offered` — **identical** (2,410 rows; 2,308 churned, 102 successor-gated)
- `schedule_census` — identical on **every shared key**, gaining only `decision_eligible_term_keys`

Only `producing_commit` (`40d54b46e` → `0bd90d7e0`), `pass_seconds` (1469.5 → 1418.8) and
`schedule_census_seconds` (128.3 → 131.4) moved. The artefact **rebuilds byte-identical** from its
own raw material via `--from-raw` with no world drawn and no clock read — verified this turn,
and pinned by `test_the_artefact_rebuilds_from_the_runs_raw_material_without_a_world`.

## 4. The pre-registration, kept beside the result

`docs/staging/records/PREREG_HOW_MANY_DECISION_ELIGIBLE_TERMS_NEVER_REACH_THE_ARM_...` was filed
before the run with the artefact absent from disk. **All five numeric predictions held:**

| key | predicted | measured | |
|---|---|---|---|
| `terms_lost_to_prior_churn` | 150–200, largest term | **187**, largest | ✓ |
| `reconciliation.residual` | 0 to +20 | **0** | ✓ |
| eligible `successor_term_not_activated` | 0 | **0** | ✓ |
| `account_already_churned.by_tariff_type` | majority `svt` | **2,115 svt / 193 fixed** | ✓ |
| `terms_never_offered_total` | 1,000+ | **2,410** | ✓ |

**And one thing in it was wrong, which is why it was written down.** §3 listed what would refute
me, and the negative-residual clause said: *"negative means I counted a withheld term the
schedules never built."* The tripwire **fired** — the first assembly was −2 — and the cause was
**the other side of the subtraction**, a *decision* on a leg outside the roster, which that
sentence does not name. My enumeration of what a negative residual could mean was one cause
short. `RESIDUAL_RULE` in the module now names **both** paths explicitly, and
`test_a_decision_on_a_leg_outside_the_census_roster_is_named_and_not_subtracted` and
`test_a_withheld_term_the_schedules_never_built_shows_as_a_negative_residual` hold one each.

The prediction that the 187 are **class 1 — decisions genuinely extinguished because the customer
left** — stands: zero eligible terms came from the assembly rule this company wrote.

## 5. The count, stated in its own unit

**187 of 299 decision-eligible terms (62.54%) never reached the value arm because the account had
already churned.** Numerator and denominator are the same unit, on the same population, from one
process, in one interpreter. It is a **count**, not the bound the gate finding could state — and
it replaces *"at least 187"*, which was a difference between two artefacts run minutes apart.

R12: a diagnostic. Neither exclusion is to be relaxed so the decision population grows, and no
money figure comes out of a decision count.

## 6. A failure mode that is published at zero

`roster_legs_the_census_map_lost_to_a_shared_key: 0`. The reconciliation's forward map is keyed
`(household, commodity)`; two legs sharing that string would let the map hold only one, and a
decision on the other would be misreported as outside the population — *silently*. It is zero on
every roster measured, and it is published **because the map is silent about it and nothing else
in the artefact would show it**.

## 7. Controls

20 in `tests/tools/test_churn_truncation_census.py`, each naming the defect it catches. The leg
written for this defect — `test_the_residual_prose_is_derived_from_the_residual` — was
**mutation-proven this turn**: reverting `_residual_means` to the constant string reds it, along
with three others. The mutation was applied to a scratch copy's original and the file restored
under checksum.

## 8. What this does not settle

The decision surface is **112 on the census roster, 114 in the world**. That the surface is small
because customers left, rather than because an assembly rule withheld them, is what presses
`EP17_varied_population_draw`: more rosters is the only route to more decisions, and no relaxation
here yields any. That ask is **not taken in this document** — it is a lane decision, recorded here
as the consequence the count supports.

The raw material is `/var/tmp/churn_truncation_raw_2026-09-19.json` (1.5 MB) and is **not
committed**; `/var/tmp` is ephemeral, so the artefact's reproducibility from raw is a property
that will expire with the machine's next clear. The artefact itself is self-contained and carries
its producing commit.
