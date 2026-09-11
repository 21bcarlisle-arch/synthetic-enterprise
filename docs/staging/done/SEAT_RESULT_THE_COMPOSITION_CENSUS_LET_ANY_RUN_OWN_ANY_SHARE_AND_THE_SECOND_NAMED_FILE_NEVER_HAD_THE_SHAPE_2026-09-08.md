**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** the-same-whole-page-attribution-shape-in-the-remaining-value-arms-rungs

# The census let any run own any share, and the second named file never had the shape

**2026-09-08. Lane 0 delivery.** Claim:
`the-same-whole-page-attribution-shape-in-the-remaining-value-arms-rungs`.

The drawn direction: `ff269503e` measured the presence-is-not-attribution class on the arms
headline, closed the one instance it found, and never enumerated the population. Sweep the rest.

---

## The premise was live, and the population is one more instance, not none

`ff269503e` is an ancestor of `origin/main`, as the doorbell's premise check said. It is not
spent: what it closed was the **headline**, and what it did not do was enumerate. The direction
named two places to look. One had the shape. One never did.

## `_composition_defects` had it, and the poison was run first

The composition panel states a share of **one** quantity **once per run** — the published run, then
every later run over the same world, as rows of one table — plus the superseded panel's share of
the same quantity in the closing prose. Three or more shares of one number on one surface. Every
rung over it asked only whether a share was *somewhere on the panel*.

**Poison, applied to the door and reverted** (run BEFORE the fix, because "survived" means two
opposite things). Swap which run each share is attributed to: the feed says the published run
found 6.8% and a later run 93.9%; the page prints the published run at 93.9% and the later one at
6.8%. Nothing else moved.

> `DEFECTS FOUND BY THE LIVE CONTROL: NONE -- the swap is invisible`

Every figure was still on the panel. Only what they were said **about** had reversed — and a
reader was told the published run found the opposite of what it found, on the one panel whose
subject is the mission's own question: value **made** or value **moved**.

## What landed

`_the_runs_own_regions` cuts the panel into the lead's own region and one region per run, anchored
on that run's artefact name taken from the same census **the door builds its rows from** — the
sibling table's `_the_bands_own_rows` is cut the same way for the same reason. Every share and
date is now asserted in its own row. `_the_census_the_door_builds` states the attribution that had
no owner before: the published row's share **is** `level_share_of_advantage`, the panel's headline
number.

**The last row is bounded, and that is not tidiness.** Left running to the end of the panel it
swallows the closing `against_the_superseded_panel` prose, which states the superseded panel's
share of this very quantity — so the last row would be handed a second share to satisfy itself
with. That is the fail-open this helper exists to close, reintroduced at the bottom of the table.

**Fail-closed, in those words**: a census the page does not render, renders out of the feed's
order, or renders an anchor twice, refuses rather than falling back to the whole panel and quietly
becoming the control it replaced.

The rung is `test_MUTATION_a_census_that_swaps_two_runs_shares_is_caught_and_both_orders_are_
reachable`. It poisons via **two feeds**, not the door, because a test may not edit production:
two feeds differing in nothing but which run holds which share, each page must satisfy its own
feed, and page B checked against feed A's claims must not. Its two self-legs are the reachability
half — a helper that refused everything would fail them, and "refuses correctly" is what a guard
that refuses *all* of its partition also passes.

**Mutation-proven.** Putting the three checks back on the whole panel, changing nothing else, reds
the new rung on `assert []` — the old control saw nothing — while both pre-existing composition
rungs stay green. That is the evidence they were the blind ones. 91 passed, 1 skipped, from a
clean HEAD extract.

## The second named file never had the shape — a negative result, stated

`tests/tools/test_generate_value_arms_data.py` carries **no** instance. All 13 of its occurrences
of "rendered" are prose in comments and failure messages; it has no rendered page as a subject at
all. Its one multi-figure block assertion is already field-scoped
(`assert "78.7%" in block["against_the_superseded_panel"]`, ~line 3408), which is the attributed
form, not the whole-object one. It tests the feed, and the class is a *page* class.

So the population the direction asked me to enumerate is: the headline (closed by `ff269503e`),
the composition census (closed here), and nothing in the producer's tests.

---

## What is next, in order

1. **The refusal branches' prose is still whole-panel.** `_door_prose(said)[:80] not in rendered`
   on the `readable is False` and `readable is None` branches renders into the lead region and is
   asserted over the whole panel. It is the same shape, one branch along, and it is *not* measured
   — I did not poison it, so I am not claiming it is exploitable, only that it is unenumerated.
   Left deliberately: the collision risk on long prose is low and the change is not free.
2. **The superseded panel's share reaches the reader with no control at all.**
   `superseded_panel_share` (78.7%) is in the feed and rendered in the closing prose, and nothing
   asserts it. It is the collision source the last-row bound now defends against; a control over
   it would defend the figure itself.
3. **The blocker below, which is not mine to resolve.**
