**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, "the here-relative census registers only the first direction in a literal that claims two"

# The census registered one direction per literal and the vocabulary now has fourteen nouns, so a second direction was invisible to every rung that imports it

**Delivery seat, 2026-09-19, claim
`the-here-relative-census-registers-only-the-first-direction-in-a-literal-that-claims-two`.**

---

## 1. The premise, re-measured before any work

The drawn item cited `2957c2cc9`, which is an ancestor of `origin/main`. That is the commit that
**filed** the finding, not one that repaired it — so an ancestor check alone does not spend the
premise. The mechanism was re-measured directly at HEAD `52f572916`:

```
>>> pub._here_relative_phrase('the figures above are from the run above it')
'figures above'
>>> [m.group(0) for m in pub._HERE_RELATIVE.finditer('the figures above are from the run above it')]
['figures above', 'run above']
```

**Live, and the item's named witness is real.** Sweeping the producer census at HEAD:

```
literals registered: 27
--- generate_value_arms_data.py 10984 registered='figures above' all=['figures above', 'run above']
multi-direction literals: 1
```

`_current_world_contrast`'s `how_to_read_this`, the not-the-later-run branch. **And it is TIED** —
measured against `site/data/`, not assumed: its interpolation-stable fragments appear in a published
feed, so it is a byte a reader can fetch today, not a branch nobody reaches.

### The duplicate-work check, answered

Two live claims were named at draw time.
`churn-truncation-destroys-the-decision-surface-before-the-arm-is-asked` was said to already hold
`tests/tools/test_the_value_arms_pages_undriven_pointers.py`; read live from
`docs/observability/.delivery_lane_claims.json`, its `paths` is `[]` and it holds nothing. It is
different work on a neighbouring subject. The second id is this one, held by this invocation. **No
disposition is owed; the work is this item's.**

---

## 2. Pre-registration, written before the census was widened

Filed here before running anything, so the answers below can refute it.

**P1.** Widening the census to `finditer` exposes **exactly one** second direction across all 27
registered literals: `generate_value_arms_data.py:10984`, phrase `run above`.

**P2.** Because that literal is TIED, the new subject `("_current_world_contrast", "run above")`
reds **`test_every_tied_here_relative_pointer_is_true_from_the_region_it_lands_in`** — not the
undriven leg — with `_direction_defects`' unregistered-subject refusal ("register it in
`_REFERENTS` with what it points at"). The fail-closed shape is the whole point: a direction the
rung has never been told about is refused, not passed on silence.

**P3.** Registering it as `(".headline", "above")` — the SAME referent `("_current_world_contrast",
"figures above")` already carries, because both clauses name the canonical run's figures — turns the
leg green. The direction was **true**; what was wrong was that nothing could ask.

**P4.** No other rung reds. The published-feed sweeps ask a boolean ("does this sentence claim a
direction at all") that first-vs-all cannot change, and `_here_relative_phrase` is kept as
`phrases[0] if phrases else None` so its own control tests judge the same vocabulary they did.

**P5.** The proof page's `_phrases()` gains nothing today: its second-direction surface is the
page-scoped `_EXTRA_PHRASES`, which it already scanned with `in`, and `generate_proof_data.py` owns
no literal claiming two registered directions.

---

## 3. What was built

**One plural in the vocabulary's own module, and the singular defined from it.**
`site/test_a_here_relative_pointer_has_one_home.py` gains `_here_relative_phrases()` —
`finditer`, de-duplicated case-insensitively, landmark still taking the whole sentence out — and
`_here_relative_phrase()` becomes `phrases[0] if phrases else None`. One landmark rule, one
vocabulary, no second copy to drift.

**The census row carries `phrases` and no longer carries `phrase`.** `_producer_literals()` is the
one census three rungs import. Leaving a singular `phrase` beside the plural would have left every
consumer a flattering field to read that answers the old, narrower question — which is the same
shape as the defect. Removing it makes a consumer that has not been widened a `KeyError`, not a
silent first-only judgement. Seven call sites were moved: two in the producer sweep, five in the
value-arms rung.

**The exposed second direction is registered, not reworded.** `("_current_world_contrast", "run
above") → (".headline", "above")`. The clause is true and stays in the vocabulary so the claim goes
on being re-asked — the choice `_departures` and `_against_the_superseded_panel` already got, and
for the same reason.

---

## 4. Results against the pre-registration

Baseline before any edit: **31 passed** across all four rungs, 49s. Nothing was red.

| | prediction | measured |
|---|---|---|
| **P1** | exactly one second direction, `10984` `run above` | **held.** 27 literals, one multi-direction: `generate_value_arms_data.py:10984`, `['figures above', 'run above']` |
| **P2** | reds the TIED leg with the unregistered-subject refusal | **held, verbatim.** `1 failed, 30 passed` — `test_every_tied_here_relative_pointer_is_true_from_the_region_it_lands_in`: *"'run above' in `_current_world_contrast` is not a pointer this rung knows what to check … register it in `_REFERENTS`"* |
| **P3** | registering `(".headline", "above")` turns it green | **held.** 31 passed. The direction was TRUE — this was the census going blind, not the page misdirecting |
| **P4** | no other rung reds | **held.** Same 31 green as the baseline, no other file touched by the widening |
| **P5** | the proof page gains nothing today | **held.** `generate_proof_data.py` owns no two-direction literal; `_phrases()` was widened anyway, because its list shape was carrying only the page-scoped axis and the registered axis arrived singular |

**Four for four, and the fifth by construction.** That is a weaker result than it looks, which is
§5.

---

## 5. The finding this turn's own work produced: the repair was unmutatable

**Reverting `_here_relative_phrases` to `search` left all 31 rungs GREEN.** Measured, not
reasoned: the widening, the `_REFERENTS` row, the five moved call sites — every visible part of the
repair — could have been undone and nothing in the tree would have said so. The new row simply
stops being reached; the rungs go on judging the one direction they always judged.

**Why no existing leg could see it.** The homes rules fire on whether a sentence claims a direction
AT ALL, which is a boolean the narrow read answers correctly. The per-page direction rungs judge
direction, but only over subjects the census hands them. **A dropped direction is not a wrong
answer anywhere — it is an absent question**, and no assertion about the site's prose can reach one.
That is the same shape as the parent finding, one layer out: the instrument was widened and nothing
held the widening open.

`test_the_census_registers_EVERY_direction_a_literal_claims_and_not_just_the_first` is the leg that
now does. **The instrument is subtraction**, which is what makes it failable rather than a
restatement of `_producer_literals`: each registered phrase is struck from the literal once and the
vocabulary asked again, and anything it still finds is a direction the census dropped.

### Both legs proven to fail, separately, and the flattering reading refused

The first run of the mutation was caught by the **instrument** leg, not the census leg — which is
the shape R15 warns about, because the instrument assertion aborts before the census leg runs. So a
second, independent mutation was driven to establish each leg owns its own defect:

| mutation | what fires |
|---|---|
| `_here_relative_phrases` → first match only (vocabulary) | the **instrument** leg: *"the vocabulary reports `['figures above']` for a sentence claiming two directions"* |
| `_producer_literals` → `phrases[:1]`, vocabulary untouched (census) | the **census** leg: *"`generate_value_arms_data.py:10984` registered `'figures above'` and still claims `'run above'`"* |

**And under each mutation, exactly ONE of 32 tests failed.** That number is the finding: it is the
direct measurement that every other rung is blind to this class, and therefore that the control was
worth its lines rather than a guard over a guard.

The instrument leg is also driven the other way — a one-direction sentence must come back as one —
because a plural read that returned everything would pass the two-direction leg while demanding a
`_REFERENTS` row for pointers no producer wrote.

### The vacuity the leg is not allowed to have

The census half is vacuously green on a day no producer writes a two-direction sentence. That is
the fail-silent shape, so the instrument half is in the SAME test rather than beside it: it drives a
literal through the vocabulary and cannot go quiet. Nothing in the leg names `10984`,
`_current_world_contrast` or `generate_value_arms_data.py` — repairing that sentence to claim one
direction leaves it green, and the next two-direction literal reds it wherever it is written.

---

## 6. What the next lane should know

**The singular `phrase` key is gone from the census, deliberately.** `_producer_literals()` returns
`phrases: list[str]` and nothing else. A rung that has not been widened now raises `KeyError`
rather than quietly judging the first direction and reporting a clean sentence — which is the
difference between this defect being loud and it being what it was.

`_here_relative_phrase()` survives, defined as `phrases[0] if phrases else None`, because four
callers ask a BOOLEAN of a sentence ("does this claim a direction at all") whose answer cannot
change with how many it claims. **If you are judging a direction, you want the plural.** The two
multi-home refusals were moved to print every direction even though the rule needs only one to
fire: a repairer acts on what the refusal names, and naming the first is how a sentence gets
half-repaired and stays false the other way.

