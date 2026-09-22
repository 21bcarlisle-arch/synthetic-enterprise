**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, "land the orphaned SVT conversion edge"

# `f0bc1e057` was dropped by a judgement that landed, not stranded by a race, and the only thing that dies with it is an equivalence proof

**Delivery seat, 2026-09-19, claim `land-the-orphaned-svt-conversion-edge`. No code landed, and
that is the result.** The drawn item ordered a replay of an unreferenced commit onto main. Replaying
it would have re-landed an implementation its own author had already rejected in a commit that is an
ancestor of HEAD.

---

## 1. The disposition, first

**Do not replay `f0bc1e057`.** Its premise is spent by `04ab33216` (ancestor of HEAD, landed
2026-09-19 01:54, eight minutes after the orphan was written). That commit is the same author's
disposition of the same object: it names the sha, states that it "is not an ancestor of anything",
and itemises file-by-file why each part was dropped.

The item's check-first instruction was *"if another lane has since landed the same content under a
different sha, say so, record that the object is redundant, and stop."* The real answer is one step
off that: the content was not re-landed under another sha — it was **deliberately dropped, with the
parts worth keeping re-landed in better form.** Redundant by judgement, not by duplicate landing.
The instruction's spirit applies and I stopped.

## 2. Every factual claim the item made about the tree, re-asked

| the item said | measured at HEAD `2957c2cc9` |
|---|---|
| "it carries eleven files" | **nine.** Three simulation modules, three test modules, one knowledge-map edit, three staging docs — nine paths in `git show --name-status` |
| "no ref anywhere points at it, so it is invisible to every lane and to every future orientation" | **the first clause is true, the conclusion is false.** `04ab33216`'s message and its staging doc both name `f0bc1e057` in prose that is at HEAD. It is visible to any lane that greps the subject — which is how it was found |
| "the map row is the only place the switching-rate gap it names is recorded" | **false.** The orphan's own gap constant `SVT_TO_FIXED_CONVERSION_RATE` appears nowhere in the tree; the gap's single home is `tools/published_route_split.SVT_INTERNAL_CONVERSION_RATE = None` with `SVT_INTERNAL_CONVERSION_RATE_GAP` and the derived `svt_internal_conversion_floor()` (0.0449/SVT household/six months). Re-landing the orphan's constant would **create the second home** |
| "the three staging documents … are how the next reader knows why the edge exists" | **two of the three are already at HEAD**, landed by `04ab33216`: the two-home-move finding and the pre-registration. Only `SEAT_RESULT_..._THE_RECORDS_OWN_DOOR` is absent, and it was superseded by the same author's rewrite, `SEAT_RESULT_THREE_LANES_ONE_SVT_EDGE_...`, which is at HEAD |
| "expect conflicts in the three simulation modules and resolve them by reading both sides" | the conflicts are not mergeable-both-ways. `05684780e` (ancestor) does the same repair by **splitting `product` from `tariff_type`**; the orphan rebinds `tariff_type = "fixed"`, overwriting the arrival fact. Its own author called theirs "better on the axis mine was weakest" |
| "its author measured the baseline world's output is byte-identical because every live `ELEC_CUSTOMERS` record carries `tariff_type: None`" | **true, and it is the one claim that held.** |

So the item was right that the object exists and is unreferenced, and wrong about what that means.

## 3. What replaying it would have cost

Three defects this repo has named rules against, in one landing:

1. **A second home for a gap that has one.** `SVT_TO_FIXED_CONVERSION_RATE` next to
   `SVT_INTERNAL_CONVERSION_RATE`, the second with a published floor attached and the first without.
2. **A rejected implementation restored over its successor.** The `tariff_type = "fixed"` rebind
   overwrites the fact that the household arrived on the default tariff.
3. **Two staging documents duplicated**, and a third published whose §1 narrates a disposition that
   is false at HEAD.

## 4. The one asset that dies with the object, preserved here

`renewal_engagement.converts_off_the_cap` was **not** superseded. It is filed as owed in
`SEAT_RESULT_THREE_LANES_ONE_SVT_EDGE_...` §4, and the reason for deferring it is sound: one call to
`rolls_active_renewal` answers two different household decisions (off a FIXED term — re-fix or roll
onto the cap, which the 35% active-renewal anchor is cut on; off an SVT STINT — stay on the cap or
take a fixed deal, an *internal switch*), and CIM wave 6 Table 56 reads the two populations at 2.5%
and 7.0%. Naming the second in `simulation/` needs a seam first, because `simulation/` cannot import
the module where the floor lives (§5).

**What the orphan proved, and what a future closer would otherwise rebuild.** The split was
demonstrated an equivalence rather than asserted one — recorded here because the successor document
compresses it to a single clause and the proof itself is reachable from no ref:

- **The reading, before and after, identical:** `134` resi electricity customers / `116` ever held an
  SVT term / `68` held one and later a fixed term / `94` SVT→fixed transitions.
- **The sweep:** `test_the_conversion_split_moved_no_number_the_day_it_landed` — 200
  (date, probability) pairs across 2016–2025, holding the two paths equal while the constant is `None`.
- **The gap's widening leg:**
  `test_the_conversion_off_the_cap_is_a_named_decision_with_an_unestablished_rate` pairs the `is None`
  assertion with a widening — it sets the constant to certainty and *requires the answer to change* —
  because a `None` no caller can act on makes the gap unclosable by filling it in and the bare
  assertion unfalsifiable. **That is the shape to keep** whenever the seam is designed.
- **The mutation results, observed not intended:** reverting the electricity repair → 1 red;
  stamping the opening stint `fixed` → 2 red (and the author recorded that the reachability leg fired
  on the opening assertion rather than the route back, i.e. the *weaker* evidence, rather than taking
  the flattering reading); `converts_off_the_cap` ignoring the constant → 1 red; using
  `PASSIVE_RENEWAL_RATE` instead of the household's own → 2 red; reverting the gas repair → 1 red
  **by raising `ValueError` out of `generate_forward_price`, not on the property** — the old wholesale
  delegation had no guard for the price history running out while every other gas path `break`s on it;
  gas builder keeping `rolls_active_renewal` at the SVT boundary → 1 red.

Recovering those seven bytes-worth of design costs one `git show f0bc1e057` while the object
survives; rebuilding the proof costs a turn. Recorded as prose here so it survives a `git gc`.

## 5. A citation correction, because the next reader will follow it

`SEAT_RESULT_THREE_LANES_ONE_SVT_EDGE_...` §4 cites
`test_the_published_check_band_cannot_be_read_by_the_world_it_judges` as the wall keeping
`tools/published_*` out of `simulation/`. **That test scans for `tools.published_tariff_mix`**
(`tests/architecture/test_switching_rate_commons.py:3416`) — not the module where the floor actually
lives.

The wall that holds `tools.published_route_split` out of `simulation/` is a **second, unnamed
assertion block at line 3769, inside a test named for the opposite direction**:
`test_the_route_split_does_not_read_the_worlds_clipped_constants`. The substance of §4's claim is
correct — the wall exists and is live — but a guard whose function name describes the reverse edge is
one a reader checking "can `simulation/` reach the floor?" will not find by name. The honest summary:
**both directions are walled, in one test named for one of them.**

`simulation/run_phase2b.py:715` references `svt_internal_conversion_floor` in a **comment**, which
the guard deliberately does not fire on ("a mention in a comment or docstring — which is how the rule
gets explained — does not fire it"). That is the declared borrow §4 describes, and it is intact.

## 6. What closes the owed item

Unchanged from §4 of the successor, restated so it is not lost: decide whether the SVT-side decision
gets a world-side constant of its own, and if so how the published floor reaches it across the wall —
**before** naming the decision in code. The proof design in §4 above is reusable as written.

## 7. Reversal

Nothing to reverse. One document added; no code, no map cell, no feed. `f0bc1e057` is untouched and
remains readable by sha for as long as it survives — this document is what makes that no longer
necessary.
