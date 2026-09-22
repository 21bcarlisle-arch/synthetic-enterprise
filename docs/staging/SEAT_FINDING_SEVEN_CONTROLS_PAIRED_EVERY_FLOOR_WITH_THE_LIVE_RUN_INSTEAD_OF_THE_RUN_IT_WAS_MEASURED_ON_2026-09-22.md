**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
**Discharged:** `tests/tools/test_every_leg_of_the_advantage_reaches_a_sentence.py::test_each_fixture_pair_is_admitted_for_a_stated_reason`,
`tests/tools/test_every_leg_of_the_advantage_reaches_a_sentence.py::test_the_published_pair_is_graded_by_the_bounds_rule_and_by_nothing_else`,
`tools/generate_value_arms_data.py` — BLOCKING as found: seven controls red on the trunk, reding
any lane that touched the producer. Repaired in commit b33af985e, and the two nodes above are the
falsifiers that make the defect non-recurring: the first reds **by name** when the pairing premise
goes, the second reds if the legs block ever grades a pairing the bounds rule refused. Both were
mutation-proven before this discharge was written — see the mutation table.

*This field was filed empty in b33af985e and added afterwards, because the discharge rule asks the
LANDED copy for the node: a falsifier that exists only in a working tree is not a landed falsifier,
so a finding that repairs its own defect can never discharge itself in the commit that repairs it.
Note also that the rule reads **every backticked token in the field** as an artefact path — a
commit sha or a branch name in backticks here voids the whole discharge.*

# Seven controls went red when the code became more honest, and the fixture defect underneath them is a mis-paired artefact, not a stale number

**Claim:** `the-error-bar-and-the-point-estimate-measured-different-books-and-seven-controls-assert-they-agree`
**Subject:** `tests/tools/test_every_leg_of_the_advantage_reaches_a_sentence.py` · **Date:** 2026-09-22

This is an instance of the *controls that cannot fail* family — specifically its "keyed to today's
answer" sub-shape, the twenty-eighth. It is named in prose rather than in a `**Class:**` header on
purpose: that header routes a document into
`docs/staging/reference/CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md`, whose own rule requires
every listed instance to be ARCHIVED and absent from the staging root. A live finding cannot
satisfy both, and a header that forced it would make this document unconsolidatable rather than
classified. It is consolidated when it is archived, not when it is written.

## The refusal is correct and the controls were wrong

`gva._legs_on_one_bar` returns `available: false` on the live pairing, naming its reason: the
published floor (`folded18_single_arm_20260917`, stamped 2026-09-17T21:39:28Z) is older than the
figure it bounds (`THREE_ARM_PATH`, 2026-09-18T05:43:40Z), and the graver half — the two artefacts
did not measure the same BOOK. That refusal is the bounds rule working.

Seven controls in the file above indexed `block["legs"]` and `block["the_verdicts"]` and asserted
`available is True`. They were red on origin/main and would red any lane that touched
`generate_value_arms_data`.

## What the fixture defect actually was, and it is not the one the item named

The file named two floors — `UNANIMOUS_FLOOR` and `SPLIT_FLOOR` — and then bolted **both** onto
whatever `THREE_ARM_PATH` carried on the day the test ran. A noise floor bounds **the run it was
measured on**; pairing a 2026-09-10 floor with a 2026-09-18 figure asks a different question from
the one the file's own docstring says it asks, and it asks a question the bounds rule is right to
refuse. **The fixture was a bare floor where the subject is a PAIR.** The stamp in the assertion
was never the defect; the missing second half of the fixture was.

So the repair is not a re-run and is not a softened assertion. Each floor is now paired with the
three-arm run it was contemporaneous with — both frozen, committed artefacts:

| pair | admitted | value leg | level leg | selection leg |
|---|---|---|---|---|
| `noise_floor.json` (09-10 23:03) × `three_arm_20260910` (09-10 14:04) | yes | +17,645.76 @ 22.71σ | +19,395.23 @ 49.45σ | −1,749.47 @ 2.85σ, **negative** |
| `noise_floor_20260910b` (09-10 21:34) × same run | yes | +18,988.74 @ 34.39σ | +19,158.83 @ 39.10σ | −170.09 @ 0.55σ, **uncallable** |
| `folded18_single_arm_20260917` × `three_arm.json` (live) | **no** | — | — | — |

Both families the file needs — one unanimous, one split — are real, are on this disk, and are now
asked the question they can answer. Nothing was constructed.

## The measurement the item warned about, answered

The item said: *"the nearest floor on the figure's own book states NEITHER a sign NOR a price, so
re-running is not guaranteed to produce agreement — do not assume the repair ends green."* That was
the right warning and the corpus already answers it. Two floors on the live run's own side of the
ordering rule **do** exist and **are** admitted — `noise_floor_next12_20260917` (09-18 11:07) and
`noise_floor_next12_at_18327d977` (09-19 09:10). Graded against the live figure they read:

| admitted live floor | value leg | level leg | selection leg |
|---|---|---|---|
| `next12_20260917` | +7,395.85 @ 7.42σ | +8,465.32 @ 5.24σ | −1,069.48 @ **0.69σ** |
| `next12_at_18327d977` | +7,395.85 @ 7.42σ | +7,655.14 @ 4.73σ | −259.29 @ **0.17σ** |

**The "reads against the company" verdict does not survive onto the figure's own book.** The level
leg replicates — positive, clears its bar, on every family here. The selection leg does not: it is
−1,749 at 2.85σ on one 9-seed floor and −170 at 0.55σ on another 9-seed floor **from the same day**,
and −1,069/−259 at under 0.7σ on the twelve. The negative sign is a property of *which* floor was
drawn, not of the book. Anyone reading the 09-10 unanimity as evidence the choosing destroys value
is reading one draw of a noise-dominated quantity.

That is a finding about the substance, not about the harness, and it belongs in the knowledge layer
rather than pinned in a test — so no control below asserts it. The controls assert the grader
discriminates; this document asserts what the corpus currently says.

## Pre-registration (written before the repaired file was run)

**Prediction:** re-pairing the fixtures makes all eight controls pass with **zero** change to
`tools/generate_value_arms_data.py`. If the production code has to move to make this green, the
diagnosis above is wrong and the refusal is reaching further than the ordering rule.

**Result: CONFIRMED.** 10 passed, `git diff --stat` over `tools/generate_value_arms_data.py` empty.
The refusal reaches exactly as far as the ordering-and-book rule and no further; every control that
was red was red because of its fixture.

## Mutation evidence — these controls can fail

Four mutations applied to `generate_value_arms_data.py` one at a time, module restored clean after
each (`git diff --stat` empty):

| mutation | reds | written for |
|---|---|---|
| grade legs even when the bounds rule refused | 2 (`..._bounds_nothing...`, `..._published_pair_is_graded...`) | the new control, and it caught it |
| every leg at the selection leg's family | 4 | `..._own_familys_bar_and_over_its_own_rows` |
| drop a leg from the loop | 5 | `..._every_bounded_contrast_reaches_a_reading...` |
| invert the ordering rule `floor_at >= point_at` | 8, **`..._each_fixture_pair_is_admitted...` among them** | the new premise control |

The fourth is the one that matters for the defect being fixed: a rule change that stops admitting
these pairs now reds a control that **names the pairing** as the cause, instead of surfacing as
seven assertions that each look like a defect in a leg. That is the failure mode that produced this
finding.

Not mutatable from here, by design: deleting the ordering rule outright makes the live pair
admissible and every control below keeps its meaning, because they assert the block AGREES with the
rule. The rule itself is owned by `test_an_error_bar_older_than_its_figure_says_so_on_the_page` in
the site lane. That separation is deliberate — a control that pinned `available is False` would be
the same defect one branch over.

## What done means here

Not "green". Done is: every control in the file is keyed to a property that holds regardless of
which run `THREE_ARM_PATH` carries tomorrow; the refusing branch is exercised over a **real**
refused pair and not only over a hand-mutated one; and the pairing premise each fixture rests on is
asserted rather than assumed, so a rule change that stops admitting these pairs reds here with a
legible cause instead of at seven unrelated assertions.
