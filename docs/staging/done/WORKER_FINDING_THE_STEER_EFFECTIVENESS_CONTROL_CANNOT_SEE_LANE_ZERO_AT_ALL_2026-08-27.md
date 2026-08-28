**Severity:** LATENT · **Lane:** H_harness · **Rank:** backlog, after the current delivery-lane item · **Epoch:** 3 · **Atom:** `H41_the_map_ratchet_has_no_ongoing_drain`

# The seat's steer-effectiveness control cannot see Lane 0 at all, and two perennial atoms make it report PASS every cycle

**Filed by the worker seat, 2026-08-27, while discharging the Lane 0 claim
`the-world-answered-a-28x-price-rise-with-two-churns`. QUEUED, not fixed on sight
(SELF-INTERRUPT DISCIPLINE): this is a harness control, the drawn work was a measurement that is
already landed and pushed, and the supply of harness findings is infinite.**

## What happened first, because it is the cost and not the defect

The claim `the-world-answered-a-28x-price-rise-with-two-churns` was re-issued to this tick with
`paths: []`. Its work was **already landed and already on origin**:

```
8ac45e32e the world answered a 28x price rise with two churns: neither side is lying,
          they price against different references
          docs/design/THE_VALUE_CYCLE_REALISED_AB.md | 158 +++++++++++++++++++++++++++++
```

The commit subject **is the claim slug**. `git branch -r --contains 8ac45e32e` → `origin/main`.
All four things the direction asked for are in the section (the recovered per-decision belief and
its sum against the realised count, the three-way verdict with arithmetic, what would separate
them, `belief_vs_outcome` read beside it).

`--landed` cannot bind it: commit `1787788137` is **8,729s older** than `claimed_at`
`1787796866`, and `record_landing` refuses a commit not newer than the claim. So the only exit
was `--release`. A whole tick to re-verify finished work — the exact cost
`background/delivery_lane.py`'s own docstring says it was built to stop.

**This is NOT the already-filed alarm.** `WORKER_FINDING_..._LANE_ZERO_PROGRESS_SIGNAL_IS_A_CONSTANT_...`
covers the *claim* side: no paths bound, so a claim is released on the clock rather than on
observation. This is the *orientation* side, and it survives that fix.

## The defect

`delivery_lane.py` states the acceptance test for the whole mechanism:

> DONE IS DERIVED, NOT DECLARED ... The seat RE-ORIENTS every three hours and rewrites focus from
> the state of the tree, so an item that is genuinely done stops appearing.

Nothing in `build_brief` derives that. The only thing that looks at whether focus went anywhere is
`direction.focus_was_drawn`, whose own docstring calls it **"THE CONTROL ON THIS WHOLE MECHANISM,
and the reason it is recorded every cycle rather than assumed."** It is:

```python
drawn = {str(d) for d in (drawn_ids or [])}
hit   = [f for f in focus if f in drawn]
steered = bool(hit)
```

and its `drawn_ids` is `delivery_seat.atoms_drawn_since(since)`, which reads
`docs/observability/.atom_stall_tracker.json` — **keyed by maturity-map atom id.**

A Lane 0 focus id is by construction *not an atom*. That is the module's founding premise: *"A
focus id that is not an atom multiplies nothing."* So a Lane 0 slug is not in that file's key
space and **can never appear in `drawn`.** Observed:

```
tracker keys: 53
sample: ['B4_competitor_field', 'C_supply_start_consumer_routing', 'D26_...', ...]
lane-0 slug present?                      False
any hyphenated-lowercase (lane-0 shaped) key?  []      <- zero, of 53
```

## Why it reports PASS anyway, which is the part that makes it dangerous

`steered` is a **disjunction over a mixed set**. Focus is always some atoms plus some Lane 0
slugs, and the same two atoms are in it nearly every cycle — so the OR is carried by them and the
Lane 0 members' structural invisibility never surfaces. All 11 recorded orientations
(`docs/direction/decisions.jsonl`), last seven shown:

| `steered` | `drawn` | lane-0 ids in focus |
|---|---|---|
| True | `['EP1_clv_three_horizon']` | 4 / 5 |
| True | `['EP13_adapter_carbon_intensity', 'EP1_clv_three_horizon']` | 2 / 4 |
| True | `['EP1_clv_three_horizon', 'EP13_adapter_carbon_intensity']` | 2 / 4 |
| True | `['EP1_clv_three_horizon', 'EP13_adapter_carbon_intensity']` | 2 / 4 |
| True | `['EP1_clv_three_horizon', 'EP13_adapter_carbon_intensity']` | 2 / 4 |
| True | `['EP1_clv_three_horizon']` | 3 / 4 |
| True | `['EP1_clv_three_horizon']` | 3 / 4 |

**`drawn` has never once contained a Lane 0 slug** — across 11 cycles carrying 2–4 of them each.
Every `steered: True` is two atoms that the dial-weighted draw was picking anyway.

The docstring names its own tripwire: *"a run of `drawn: []` against a non-empty focus is a defect
in the steer rather than a quiet fact about the week."* That tripwire is **unreachable while any
atom is in focus** — which is every cycle.

This is R15's fourth shape, from the catalogue: *PASS branch unreachable → the verdict is a
constant*. Here it is worse than a constant `False`, because a mixed subject **masks** it as
`True`. The control built after `d7d36b46a` — two soft guards composing into a no-op while an atom
sat through 1,307 unchanged draws — now has that same defect, for the half of focus the delivery
lane exists to serve.

## Why the test does not catch it

```
tests/background/test_delivery_seat.py:106:    missed = d.focus_was_drawn(("A", "B"), ["C1", "D2"])
tests/background/test_delivery_seat.py:107:    hit    = d.focus_was_drawn(("A", "B"), ["A", "D2"])
```

Both cases use ids that *can* be in the key space, so they prove the set arithmetic and never the
subject. There is no case where a focus id is structurally absent from `drawn_ids`' domain.

## What would fix it (named, not done)

1. **Split the verdict by class.** Report `steered` separately for atom ids and Lane 0 ids. A
   class with no observable draw channel must read `UNKNOWN`, never fold into a PASS.
2. **Give Lane 0 ids a real drawn channel.** `.delivery_lane_claims.json` already records
   `claimed_at`; recording `drawn_at` / `released_at` puts them in a key space the control can
   read, and also lets re-orientation drop a released item instead of re-issuing it.
3. **R15 NULL control:** assert a focus of *only* Lane 0 ids yields `steered: False` regardless of
   what landed. That should red today. Nothing asserts it.

Fix 2 alone would have prevented this tick: the claim was released, and a re-orientation that
could read a release would not have re-issued work whose commit subject is its own slug.

## Not claimed

Whether the seat *should* re-issue an item it cannot observe is a design question for the seat's
owner. This finding asserts only what is measured above: the control's PASS branch is unreachable
for Lane 0 ids, and its reported PASS comes entirely from atom ids.

---

## DISCHARGED 2026-08-28, `df4d83ec5`

All three named fixes landed, in the commit that repaired the sibling defect on the claim side —
`record_landing` comparing against a `claimed_at` that every re-draw rewrites. That was the right
place for it: **the ledger the claim-side fix needs is the drawn channel this finding asked for.**

**Fix 2 — a real drawn channel.** `delivery_lane.DRAW_LEDGER_FILE` records `first_drawn_at` and
`last_drawn_at` per Lane 0 id and outlives the release that ends the claim. `drawn_since()` reads
it. `delivery_seat.focus_drawn_since` unions that with `atoms_drawn_since`, and `build_brief` now
passes the union. Same field name as `.atom_stall_tracker.json` deliberately: one convention for
"when was this last drawn", two key spaces.

**Fix 1 — the verdict is split.** `direction.focus_was_drawn` takes the map's id set and reports
`by_class` with `atom` and `lane_0` graded separately. The top-line `steered` keeps its shape, so
`tools/generate_delivery_page.py` is untouched. Without the id set `by_class` is ABSENT rather
than guessed — an unavailable check reports itself unavailable, it does not report a pass.

**Fix 3 — the R15 null control.** `test_a_LANE_0_SLUG_CAN_REACH_the_drawn_set_at_all` is the case
that did not exist: both prior cases used ids that *can* be in the drawn key space, so they proved
the set arithmetic and never the subject. It reds against the shipped code. Its sibling
`test_the_verdict_is_SPLIT_so_one_dead_channel_cannot_hide_behind_the_other` pins the mask itself
— one atom drawn, two slugs not, and the `lane_0` row must still read `steered: False`.

Four mutations, all fire: drop the union in `focus_drawn_since`; revert the `build_brief` call
site to `atoms_drawn_since`; fold `by_class`'s per-class verdict into the top-line OR; emit
`by_class` without the id set. Full mutation table in `df4d83ec5`'s message.

**What this finding said would follow, and did.** *"Fix 2 alone would have prevented this tick: the
claim was released, and a re-orientation that could read a release would not have re-issued work
whose commit subject is its own slug."* Correct about the channel and about the cost — it was
re-measured twice more the next day (`0850eadcd`, re-drawn 8m39s after it landed; the household
column at 16:56) before it was drawn. The claim-side half of that cost is closed by the same
commit: a re-drawn id can now be credited with the commit that satisfied it.

**Left open, and NOT claimed here.** The finding's own closing paragraph — whether the seat
*should* re-issue an item it cannot observe — is a design question for the seat's owner and is
untouched. What changed is only that the re-issue is now creditable and the steer is now
measurable per class.
