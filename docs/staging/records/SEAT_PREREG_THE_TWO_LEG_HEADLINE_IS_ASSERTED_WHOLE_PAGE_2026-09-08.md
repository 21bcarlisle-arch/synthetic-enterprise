**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

**Knowledge:** none — this is a control's reach, not domain understanding.

# PRE-REGISTRATION — the current-world headline now carries TWO legs and every rung asserts on the WHOLE page

RECORDED and not BLOCKING: the fail-open is closed in the same commit that files this, and nothing
published was ever wrong. What was wrong is that the control could not have noticed if it became
wrong — `controls_that_cannot_fail`, on a live public page.

**Written BEFORE the measurement below was run.** 2026-09-08, delivery seat, isolated worktree at
`7bdd322fc`.

## What is already true, and is not the finding

The Lane 0 floor re-point landed. `CURRENT_WORLD_NOISE_FLOOR_PATH` points at
`docs/observability/value_cycle_ab_s1_noise_floor_20260908.json`, `site/data/value_arms.json`
carries the bound again (n=3, stdev £1,522.47, £17,262.07–£20,002.33 around the £17,738.64
headline), and both suites named in the direction are green at HEAD:
`site/test_the_baseline_comparison_reaches_the_reader.py` 89 passed / 1 skipped,
`tests/tools/test_generate_value_arms_data.py` 118 passed. The two site controls the direction
listed as "what is left" were repaired in `490f0b7a2`. **The drawn item is spent.**

## The finding: the repair changed WHICH whole-page check fires, not that it is whole-page

`_current_world_clause` composes ONE string holding TWO legs with two different verdicts:

* the ADVANTAGE (`£17,739`), lead `IN THE WORLD AS IT IS NOW…`, `resolved=True`,
  `verdict_withheld_because=None` — renders `That figure CLEARS the £1,522 …`;
* the SELECTION leg (`£270`), lead `OF THAT, … IS THE LEG THAT COULD BE VALUE CREATED …`,
  withheld — renders `THIS PAGE STATES NO VERDICT ON THAT FIGURE. …`.

Every assertion in `test_the_figure_from_the_world_that_is_live_reaches_the_reader_and_never_as_resolved`
takes the WHOLE headline as its subject and asks only whether a phrase is present *somewhere*:

| line | assertion | subject |
|---|---|---|
| 2632 | `"STATES NO VERDICT" in rendered` | whole page |
| 2655 | `("CLEARS" in rendered) is bool(cw["resolved"])` | whole page |
| 2598–2600 | each leg's re-draw band edges `in rendered` | whole page |
| 2645 | the selection leg's reversing edges `in rendered` | whole page |

While both legs withheld, presence and attribution were the same question. They are not the same
question any more, and the file's own comment at 2615 records the repair as being about exactly
this — one leg along.

## THE PREDICTION, filed before it was run

Swap the two legs' clauses in `_leg_clause`'s caller — render the ADVANTAGE's `CLEARS` sentence
under the SELECTION leg's lead and the SELECTION leg's `STATES NO VERDICT` sentence under the
ADVANTAGE's lead — so the page tells the reader the **opposite** of the feed about each leg,
while every phrase, every figure and every band edge still appears somewhere on the page.

**I predict `site/test_the_baseline_comparison_reaches_the_reader.py` stays FULLY GREEN.**

If it reds, this finding is wrong and I will say so here rather than revise it.

## What would fix it, and why it is a page property and not prose coupling

Assert each leg's verdict inside that leg's OWN REGION of the headline, where the boundary is
found from the FEED's own selection figure (`_gbp(selection_leg.figure_gbp)`) and not from a copy
of the page's prose. The fail-closed leg is the one that matters: if the page stops marking where
one leg's statement ends and the other's begins, the rung refuses — because at that point **the
reader cannot attribute either verdict either**. That is a property of the page, not of today's
answer, and it stays right on the day the selection leg resolves and the advantage withholds.

## THE RESULT, written beside the prediction and not in place of it

**The prediction held.** The swap was applied to `site/data/value_arms.json` — the page then read
`IN THE WORLD AS IT IS NOW, the same comparison gives £17,739 … THIS PAGE STATES NO VERDICT ON
THAT FIGURE` and handed the `£270` selection leg the `CLEARS` sentence — and the suite returned
**89 passed, 1 skipped**. Every figure, every phrase and every band edge was still on the page;
only what they were said ABOUT had been reversed, and nothing in the file could see it.

## What landed

`_the_legs_own_regions` and `_assert_the_verdict_belongs_to_the_leg_that_earned_it` in
`site/test_the_baseline_comparison_reaches_the_reader.py`, wired into the live rung, plus
`test_MUTATION_a_verdict_rendered_under_the_other_legs_lead_is_caught_and_the_mirror_is_reachable`.
The stdev, the `SMALLER advantage` clause and both re-draw bands are now asserted in the leg's own
region rather than anywhere on the page. Poison round, each applied and reverted:

| poison | before | after |
|---|---|---|
| swap the two legs' verdict sentences | green | reds on the advantage's own band |
| add the refusal to the RESOLVED leg's sentence only | **green** | reds on attribution |
| render the boundary figure twice | green | reds, fail-closed, in those words |
| state a direction for the WITHHELD leg | green | reds on that leg's region |
| neuter the attribution helper | — | the mirror rung reds (`DID NOT RAISE`) |

The second row is the one that matters: it is invisible to any whole-page presence check, so it is
the poison that separates the new rungs from the ones they replace. The mirror leg — advantage
withheld, selection leg resolved, composed by the PRODUCER and driven through the real door —
asserts the same rungs PASS, so they cannot pass by refusing everything.

Suite after: **90 passed, 1 skipped**.

## What is NOT claimed

The page is correct today. `_current_world_clause` attributes both verdicts properly. This is a
control that cannot fail, not a defect a reader can see.
