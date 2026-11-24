**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# An item carries no knowledge check, so a fix can be drawn before its page exists

**Source:** the director's steer of Tue 24 Nov 05:56 GMT, quoted in
`docs/staging/advisor/done/DIRECTOR_STEER_EVERY_PROBLEM_STARTS_WITH_A_KNOWLEDGE_CHECK_IS_IT_THERE_DEEP_BROAD_AND_RIGHT_2026-11-24.md`:
"It should be a check when we get a problem, is the knowledge there, is it deep and broad enough? is it right?"

## What is wrong now (measured in this tree, 24 Nov)

- The item shape (`background/work_items.py`, `items_from_staging` and `items_from_maturity_map`)
  has a single `knowledge_gap` field. Every minter writes `None`, and neither `validate` nor
  `next_item` reads it. A finding can therefore be drawn and fixed with no page beneath it.
- The case that prompted the steer: the weather-to-price chain was built to L4 with no wholesale
  price-formation page beneath it. Its 24 Nov grade loses to a gas-only null in every regime
  (`docs/staging/records/WORKER_RESULT_THE_WEATHER_TO_PRICE_CHAIN_LOSES_TO_A_GAS_ONLY_NULL_AT_THE_MONTH_IN_EVERY_REGIME_2026-11-24.md`).

## The increment (the one work system's next one; not a new mechanism)

1. **Four fields replace `knowledge_gap`:** `present`, `deep`, `broad` and `right`. Each holds the
   page it rests on, or `no page`. "Right" means the 22 Nov second view was applied: a second
   source, a per-unit restatement, an order-of-magnitude check or an identity, plus whether a
   practitioner has read it.
2. **The draw refuses an item whose four fields are empty,** with a named reason, as
   `recommendation_guard` refuses a bare ask. Assert first that the refusal can be passed: one item
   with all four fields filled must be drawn. A refusal that fires on everything passes every
   refusal test.
3. **A "no" mints the knowledge item ahead of the fix** in the same lane (`blocked_by`). The fix
   then cites the page.
4. **Run the check backwards once.** Run it over the open items, and over every world and supplier
   model at L3 or above, world models first, since K8 was never enforced on them. List the ones with
   no page or a thin page, ranked by how much each feeds a published figure.
5. **The learning-loop measure:** problems whose root cause was missing, shallow, narrow or wrong
   knowledge. It is expected to be most of them at first. It sits beside W5's curiosity tally in
   `docs/institutional/ways_of_working.md`.

The cost to watch: about 185 stored items have no answers. Leg 2 must not stop the queue on the
day it lands. Either the backward run (leg 4) fills the fields first, or the refusal applies only
to items opened after the cut. The draw-time design chooses between these and states why.

## Placement

The steer's own words place this work: "in Sunday's review under harness, as part of the one work
system's next increment". It is LATENT, not BLOCKING. BLOCKING would stop all feature work in the
lane, and he ordered it into the review's harness share, not ahead of that share.
