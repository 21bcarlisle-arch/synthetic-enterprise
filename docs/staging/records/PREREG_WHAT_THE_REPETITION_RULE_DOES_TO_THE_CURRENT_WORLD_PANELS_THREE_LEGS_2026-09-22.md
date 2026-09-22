# PRE-REGISTRATION — what taking the repetition rule to `_leg_in_this_world` will and will not change

*Written 2026-09-22, BEFORE the rule was written and before the regenerated feed was read. Lane 0,
claim `the-current-world-panel-is-a-second-home-for-the-sign-verdict-and-the-repetition-rule-does-not-reach-it`.*

## The premise, re-measured at draw time

`39330677b` is an ancestor of `origin/main`. It is not spent for this item: its own commit message
hands this gap on in terms — *"`_leg_in_this_world` is a second home for the same verdict and does
not reach this rule -- handed on."* The duplicate-work check named this same id, which is this
draw's own claim and not a rival.

## What I already know (measured before predicting, and this is an INPUT not the answer)

`_draw_repetition` run against `CURRENT_WORLD_NOISE_FLOOR_PATH`
(`value_cycle_ab_s1_noise_floor_20260909b.json`, 9 seeds), per contrast:

| contrast | draws | distinct | `draws_that_repeat_another` | `redundant_draws` |
|---|---|---|---|---|
| `value_advantage_gbp` | 9 | 9 | 0 | 0 |
| `selection_gbp` | 9 | 9 | 0 | 0 |
| `level_advantage_gbp` | 9 | 7 | **4** | 2 |

This is the reachability property the rule needs, and it comes free from one artefact already on
disk: two legs on the PASSING branch and one on the REFUSING branch, same floor, same run. A rule
whose passing branch nothing can reach passes every test of a refusal.

It also refutes the drawn item's own framing on one point, and the correction belongs here beside
the prediction rather than quietly in the code: the item says the current_world selection leg is
*unavailable* today so nothing is published wrong. It is **available** — `bound_available: true` on
all three legs. What is true is the weaker and still sufficient claim: all three verdicts are
already withheld for OTHER reasons (the selection leg for one-draw instability, the level leg for
being measured against a superseded run), so adding this rule moves no verdict today.

## The predictions

1. **No leg's `resolved` changes today.** All three are already `None`. The rule is a second
   independent latch, not a new refusal a reader sees as a changed verdict.
2. **`level_leg.verdict_withheld_because` GAINS a sentence** naming 4 of 9 draws. The value and
   selection legs gain **nothing** — their families repeat none, `_repetition_withholds` returns
   `None`, and a reassuring string is not published in its place.
3. **All three legs gain a `repetition` key** carrying the count, because the evidence that
   qualifies a figure travels with it — the same reason the headline block got one in 39330677b.
   On value and selection that key reads `draws_that_repeat_another: 0`, which is a measurement and
   not a silence.
4. **The mutation that matters:** deleting the `resolved = None` in the new rule will be caught by a
   leg keyed to the LEVEL contrast reaching a stateable verdict. If it is caught by a different
   leg, that is the flattering reading and the control is wrong.

## What would refute me

- Any leg's `resolved` flipping from `None` to a boolean → the rule is inverted.
- The value or selection leg gaining a withholding sentence → `_repetition_withholds` is not
  three-state and treats zero as absent.
- The new rule's mutation dying silently → it is unreachable behind an earlier gate, which is the
  exact shape `_leg_over_its_own_family`'s docstring says a repetition rule must not have.

## What done means (there is no exit test for this item; this is it)

The current_world panel's leg builder asks the repetition question through the SAME producer
(`_draw_repetition`) and the SAME refusal text (`_repetition_withholds`) as the headline block, so
one legal requirement has one implementation and not two; both branches are driven from artefacts on
disk; the refusal reaches the rendered page and not only the feed.
