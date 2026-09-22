# A published here-relative pointer's direction is now judged, and the live one was wrong

**Severity:** LATENT · **Lane:** H_harness

One published sentence on `/capabilities/` claims a direction it cannot support, and the class it
belongs to — a here-relative pointer in a string the feed already publishes — is judged by nothing
in this tree. LATENT rather than BLOCKING: no figure moves, no control's verdict is invalidated,
and the measurement below establishes that the sentence reaches no rendered region, so no reader
has been misdirected by it. The untied half of the class has been judged since `76c72e1e2`; the
tied half is the half a reader can meet, and eleven of its twelve members remain unjudged after
this landing.

**Claim:** `the-direction-of-a-published-here-relative-pointer-is-judged-by-nothing-in-this-tree`
(Lane 0, drawn 2026-09-19). Premise re-measured at draw: `76c72e1e2` is an ancestor of
`origin/main`, and the STILL OWED paragraph of its message is verbatim this item. Not spent.

---

## PRE-REGISTRATION — written before any measurement below was run

Filed first, and the results are written underneath it whichever way they come out.

**P1 — the live instance.** `.method_skill.the_sample_size_explanation.what_this_is` says
*"the explanation for the figure above being unreadable"*. I predict the sentence renders in
`#arms-method` and the figure it names — the `"we cannot tell"` statement the block explains,
`.method_skill.cannot_tell` — renders in `#arms-method` **too**, so the true direction is `same`
and the published claim `above` is a misdirection. This is `76c72e1e2`'s claim, not mine; I am
re-asking it rather than inheriting it, because a claim about the tree carried in a commit message
is an un-re-asked prediction.

**P2 — how big the tied set is.** I have not counted. I predict `generate_value_arms_data.py` owns
**between 3 and 8** TIED here-relative literals (a literal whose stable fragments appear in a
string `site/data/value_arms.json` publishes today). The design below is chosen on the assumption
that the number is small enough for one `_REFERENTS` row each; if it is much larger, a row-per-
literal table is the wrong instrument and I will say so here rather than quietly widening it.

**P3 — how many of the tied ones are WRONG.** I predict **exactly one** — `what_this_is` — and that
every other tied pointer is true from where it lands. The untied census found 3 wrong out of 13
across two runs, so a second live defect would not be surprising; predicting one is predicting that
the published half has had more eyes on it, not that it is safe.

**P4 — what the repair costs downstream.** Repairing `what_this_is` moves a published byte, so
`site/data/value_arms.json` is regenerated. I predict the regeneration changes **only** that one
string and nothing else in the feed.

---

## RESULTS

*(written after the measurements; each is answered against its prediction above)*

### P1 — REFUTED IN ITS SECOND HALF, and the refutation changes what the repair is

The sentence renders in **no region at all**. Measured two ways that agree:

* marking `.method_skill.the_sample_size_explanation.what_this_is` in a real `build()` and driving
  `/capabilities/` down its own boot path returns **zero homes** — run once with that field alone
  marked, because a batch of markers can be its own cause, and once inside a batch of twenty-four.
  Its sibling `.sentence` returns `['arms-method']` in the same renders, so the probe is not blind.
* the door's source agrees: `site/capabilities/index.html` reads
  `msk.the_sample_size_explanation.sentence` on the available branch and `.reason` on the other,
  and **never** `what_this_is`. The three `what_this_is` renderers on that page belong to other
  blocks.

So the claim `76c72e1e2` filed — and the drawn item repeated — that this is *"the live instance and
it is wrong on the page right now"* is **wrong about the page**. It is wrong in the *feed*; no
reader has ever met it. The defect is real and the severity is unchanged, but its CLASS is not the
one the item named. It is not the misdirection `_departures` had (a direction that points the wrong
way from a region a reader stands in). It is the state `_population_repair_bias`'s cleared branch
was in: **a direction claimed from a place no reader stands**, which is a claim nothing can check.

That is also why the item's first proposed remedy could not have closed the class. A DIRECTION leg
on `site/test_a_here_relative_pointer_has_one_home.py` derives homes from what renders; a sentence
with zero homes is invisible to it by construction. The live instance would have survived the fix
written for it.

**The repair follows the class, not the item.** `"beside this"` — the repair one field away — would
have been false here in the same way `above` was: there is no *this*. The sentence now names its
subject absolutely (*"the concordance figure's own 'we cannot tell'"*), which is true from anywhere
and leaves the here-relative vocabulary altogether — confirmed: `_here_relative_phrase` returns
`None` on the new wording, and the producer's census drops from 29 literals to 28.

### P2 — REFUTED. Twelve, not three to eight

`tools/generate_value_arms_data.py` owns **29** here-relative literals, of which **12 are TIED**
(their stable fragments appear in a string `site/data/value_arms.json` publishes today) and 17
untied. The untied 17 are what `tests/tools/test_the_value_arms_pages_undriven_pointers.py` judges.
The tied 12 are judged by nothing.

Four of the twelve are already registered in that rung's `_REFERENTS` under their `(symbol, phrase)`
key — registered for the untied half and unused, because the census filters tied literals out
before the table is consulted. Eight are unregistered. Twelve is too many for the prediction I
filed and not too many for a row each, so the instrument choice below stands; I am recording that I
was wrong about the size rather than that the size did not matter.

### P3 — NOT YET ANSWERED, and the measurement says it will not be "one"

Homes of all ten distinct landing fields, against the real door (reading order read off the door,
`arms-legs-first` = 0 … `arms-note` = 17):

| landing field | home | position |
|---|---|---|
| `.current_world.selection_leg.verdict_withheld_because` | `#arms-legs-first` | 0 |
| `.current_world.selection_leg.population_repair_bias.clause` | `#arms-redraw` | 2 |
| `.current_world.how_to_read_this` | `#arms-redraw` | 2 |
| `.departure_level.statement` | `#arms-departure` | 6 |
| `.current_world.composition.against_the_superseded_panel` | `#arms-composition` | 9 |
| `.error_bar.discrimination_across_the_family.reading` | `#arms-errorbar` | 11 |
| `.method_skill.fixed_horizon.the_control_leg_agreement.sentence` | `#arms-method` | 14 |
| `.withdrawn_claim.note` | `#arms-note` | 17 |
| `.method_skill.the_sample_size_explanation.what_this_is` | **none** | — |
| `.decisions.auc_attribution.independent_grade.what_it_settles` | **none** | — |

Two of the ten render nowhere, so two tied pointers claim a direction from a place no reader
stands — `what_this_is`, repaired in this landing, and `_auc_attribution`'s `"beside this"`, which
is a second live instance of the same class and is **not** repaired here.

Three more are suspicious on arithmetic alone and are **not yet judged**, because judging them
needs a referent registered for each and that is the second increment:

* `_leg_in_this_world` says `"The figure above is a single realisation"` from `#arms-legs-first`,
  which is **position 0** — the first region the door declares. Nothing is above it.
* `WITHDRAWN_CLAIMS` says `"the choosing figure below"` from `#arms-note`, which is **position 17**
  — the last region the door declares. Nothing is below it.
* `_control_leg_agreement` says `"The control row above"` from `#arms-method`, and the control row
  it names is published inside that same block.

I am not calling these defects yet. "Nothing is above region 0" is an argument from the reading
order, and the referent could render in a region this table does not list; the rung's own rule is
that both sides are measured, and only one side is measured here. What I will say is that **P3's
"exactly one" is already refuted** — `what_it_settles` is a second, and the arithmetic above makes
one is not the number.

### P4 — REFUTED. The regeneration also moves the publish stamps

Regenerating `site/data/value_arms.json` through the real `tools.generate_value_arms_data` changed
nine lines: the repaired sentence, and eight provenance fields — `generated_at`, the
`publishing_tree_commit` and its composed `reading` in two places, `published_from.commit`, and the
published-supplier check's `last_verified_run_id`/`last_verified_commit`, which advance from
`9a1d6591e` to the `f8a54c985` run the dashboard already names. No substantive figure moved. That
is what a publish does and I should have predicted it; "only that one string" was the wrong
prediction and the diff is in the landing.

---

## WHAT IS LANDED HERE, AND WHAT IS OWED

**Landed:** the live instance repaired in the producer, and the feed republished so the byte a
reader could fetch matches it.

**Owed, and it is the class-closing half:** the tied census. The instrument is the value_arms rung,
not the published-feed sweep, and the reason is P1 — a direction leg keyed to rendered homes cannot
see a pointer with no home, and two of the twelve have none. The rung already owns every part
needed (`_REFERENTS`, `_reading_order`, `_direction_defects`, `_referent_homes`, `_homes_of`); what
it lacks is a census over the tied half and a referent row for each of the eight unregistered
`(symbol, phrase)` pairs. Its zero-homes leg
(`test_a_sentence_no_door_renders_is_reported_rather_than_read_as_clean`) must extend to the tied
half too, or `what_it_settles` stays unjudged for the same reason `what_this_is` was.

That increment cannot be split: `pre_commit_test_gate.tests_for` maps a changed test file to
ITSELF with no pre-existing-red allowance, so extending the census means every tied defect it finds
is repaired in the same landing — the same all-or-nothing `76c72e1e2` hit with its three recipes.

---

## INCREMENT 2 — the tied half of the census now exists, and it judges HOMES, not yet DIRECTION

Landed after the increment above, against the tree it created.

### What was built

`_here_relative_census` in `tests/tools/test_the_value_arms_pages_undriven_pointers.py` replaces
`_untied_literals`' private walk and returns BOTH halves from one pass. `_untied_literals` stays as
a name because the proof page's rung imports it. The tied half gets a fixture that builds over the
real artefacts — nothing is patched, because a tied sentence is on the page already and forcing a
branch would measure a payload the producer did not compose — reads each literal's landing fields
out of that build by stable-fragment match, marks every landing field with its own marker in ONE
build, and drives `/capabilities/` once.

Four legs, and what each refuses:

* `test_the_census_puts_every_here_relative_literal_in_exactly_one_half` — counts the halves
  against the whole, and requires a witness in each. Without it, a fragment lookup that went blind
  would drop every literal into the untied half and the tied legs would pass over an empty list.
* `test_every_tied_here_relative_literal_is_found_in_the_build_that_publishes_it` — tied-ness is
  read off `site/data/`, landing fields off `build()`, and the two diverge whenever the committed
  feed is older than the producer. Then homes come back empty for a reason that is not about the
  door, and the rule below would red naming the wrong cause.
* `test_no_tied_here_relative_pointer_is_published_into_a_field_no_door_renders` — **the rule.**
* `test_MUTATION_the_tied_probe_tells_a_rendered_field_from_an_unrendered_one` — both halves of the
  partition against the real door, plus the witness that the census itself reached it.

### The rule fired on a second live instance before it was repaired

Run against the unrepaired tree, the rule red naming exactly one row and nothing else:

```
_auc_attribution:7451 'beside this'
```

`.decisions.auc_attribution.independent_grade.what_it_settles` said *"The polarity branch is closed
by `polarity_check` beside this block"*. The door composes its own prose for that block out of
`oracle_ceiling_auc`, `renewals` and `tool` and never reads `what_it_settles`, so the sentence is a
byte a reader can fetch and a direction claimed from a place no reader stands — the identical state
`what_this_is` was in, found by the instrument written for `what_this_is`, which is the only
evidence worth having that the instrument generalises. Repaired the same way: name
`polarity_check`, claim no direction.

### What the tied half still does NOT judge, and the obstacle is concrete

Direction. Eleven tied literals; four already carry a `_REFERENTS` row that had never been
consulted, because the census filtered tied literals out before the table was reached. Measured
against the door's own reading order, **all four are true today** — `_family_discrimination`
(`#arms-errorbar` → `#arms-errorbar`, `same`), `_departure_statement` (`#arms-departure` →
`#arms-realised`, `below`), `_against_the_superseded_panel` (`#arms-composition` →
`#arms-realised`, `above`), `_current_world_contrast` (`#arms-redraw` → `#arms-headline`, `above`).
So switching the direction leg on for those four is free.

The other seven need a referent each, and **five of them name a NUMBER** —
`current_world.selection_gbp`, the choosing figure. Both halves of this file locate a referent by
prefixing its value with a string marker and looking for the marker in the rendered DOM. Prefixing
a float changes what the door does with it (`toFixed`, `toLocaleString`, the `gbp()` formatter), so
the probe would be measuring a page nobody publishes — the exact objection `_polarity_reason` and
`_family_never_asked` were written against. A numeric referent needs its own probe: perturb the
value to a distinctive one and search the rendered text for its FORMATTED forms.

That is the next increment, and it is written down rather than half-built. Three of those seven are
suspicious on arithmetic already and remain **unjudged, not cleared**: `_leg_in_this_world` says
"the figure above" from `#arms-legs-first`, position 0; `WITHDRAWN_CLAIMS` says "the choosing figure
below" from `#arms-note`, position 17; `_control_leg_agreement` says "the control row above" from
`#arms-method`, where the control row is published inside that same block. Each is one side of a
two-sided measurement, and this rung's own rule is that both sides are measured.
