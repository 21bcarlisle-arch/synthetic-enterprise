**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# Two controls over the R1 panel were green because the committed feed predated the fields they grade, and one leg of each was unsatisfiable the moment it did not

**Found:** 2026-09-07, delivery seat, claim `a49-publishes-the-r3-and-r4-ceilings-on-harness`.
Found by accident, while publishing R3's and R4's ceilings — regenerating `site/data/delivery.json`
is what turned both green legs red.

## What happened

`site/test_harness_delivery_record.py` holds two controls over the R1 ceiling panel:

- `test_the_WHOLE_BOOK_magnitude_and_its_disagreeing_verdict_reach_the_reader`
- `test_WHICH_RUNG_THE_PROGRAMME_IS_GATED_ON_reaches_the_reader`

Each takes the **live committed feed**, overrides one sub-field, re-renders the real door, and
asserts on the reader's string. Each has a LEG 2 asserting that when its rung *refuses* a magnitude,
no magnitude is rendered — spelled `assert "0.2513" not in refused`.

Both passed at `bfd450a32`. Both fail the moment the feed is regenerated. Neither the page nor the
generator changed.

## The cause, and it is two faults stacked

**1. The committed feed was stale relative to its own committed artefact.**
`site/data/delivery.json` at HEAD was generated from an older R1 run and carried
`the_whole_book_rung: null` and `the_a49_gate: null` — while
`docs/observability/r1_inference_ceiling.json`, committed in the same tree, carried both. So the two
blocks these controls exist to grade **rendered nothing at all**, and every assertion about them —
positive and negative — was answered by the overrides alone.

| field | committed `delivery.json` | committed `r1_inference_ceiling.json` |
|---|---|---|
| `run_output` | `run_output_23cbe058b_…` | `run_output_5a256cd6d_…` |
| `the_a49_gate` | absent | present, gates `whole_book_pair_rung` |
| `the_whole_book_rung` | absent | present, magnitude `+0.2513` |
| `corrected_verdict` | `true` (clears) | `false` (we cannot tell) |

The last row is the one worth reading twice: the committed feed said the R1 ceiling **clears** while
the committed artefact behind it said **we cannot tell**.

**2. The negative assertion was keyed to a figure the block does not own.**
`+0.2513` appears in three places on that one panel: the `the_whole_book_rung` block, the
`the_a49_gate` block (which renders the magnitude of whichever rung it gates on — on this book, that
same rung), and `on_the_magnitude`, a **sentence lifted verbatim from the instrument's artefact**.

So `"0.2513" not in refused` is not a statement about the block under test. It is a statement about
the whole panel, and it is **unsatisfiable** on any tree whose feed is current — whatever the block
renders. It could only ever have passed while both siblings were blank.

This is the R15 catalogue's shape from a new door: not a control keyed to today's answer, but a
control keyed to a *number it does not own*, where the discriminator is shared with a sibling
surface **and with the source artefact's own prose**.

## The repair

Two parts, and the second is load-bearing:

1. Each test blanks the sibling block, so the panel holds one rendering of the rung under test.
2. Each LEG 2 asserts on the **block's own answered-branch wording** rather than on the number:
   `"carry the three-way split the headline rung cannot"` and
   `"while its own selected-maximum verdict"`. Both phrases are emitted only when that block renders
   an estimate, so the mutation each test names — supplying a magnitude for a rung that refused one —
   still fires, and prose can no longer reintroduce the discriminator.

Proven by poison, not asserted: five mutations were applied and each fired on exactly the control
that names it (unwire the renderer; render an unmeasured arm as `£0.00`; drop the share curve; drop
the two-sided block; blank the missing-tariff explanation).

## What is NOT established, and I am not claiming it

**Whether the live site published the stale reading.** `tools.generate_delivery_page` is reachable
from the committed schedule, so the deployed feed is very likely regenerated rather than served from
the committed copy. I did not measure the live page, and this finding does not claim the director
ever saw "it clears" where the artefact said "we cannot tell". What is established is that the
**committed** feed said it, and that two controls were green over blocks that were not rendering.

**The general case.** I checked one feed. Every other `site/data/*.json` generated from an artefact
has the same failure mode available to it: a control that reads the committed feed as its fixture
grades whatever that feed last happened to contain. That is a class, and this is one instance of it.
I have not censused the rest.

## The one-line lesson

**A control whose fixture is a committed generated artefact grades the artefact's age, not the
code.** When the fixture is stale enough, the surface under test is absent, and absence answers
positive and negative assertions alike.
