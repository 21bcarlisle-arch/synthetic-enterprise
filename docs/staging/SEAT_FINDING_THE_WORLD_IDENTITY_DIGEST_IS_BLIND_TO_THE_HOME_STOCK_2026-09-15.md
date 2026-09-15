**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** (Lane 0 delivery — note the base beside every filed figure that is a statistic about the homes)

# `world_identity.digest` answers "same departure surface", and it is read as "same world" — it cannot see the homes at all

**Filed 2026-09-15, delivery seat.** Found while noting the base beside the home statistics in the
09-11 and 09-15 result files, which is the second time in two days that going after one thing has
surfaced something nobody was looking for.

---

## The claim that is made on it

`SEAT_RESULT_ON_GROSS_MARGIN_THE_CHOSEN_BOOK_IS_INSIDE_THE_BLIND_SPREAD_AND_ON_NET_MARGIN_IT_IS_BELOW_EVERY_BLIND_ARM_2026-09-11.md`
opens its evidence with:

> `world_identity.digest` is **`39a192ce04c1eda8` on all five**, so these are directly comparable and
> not five runs of five worlds.

That inference is **sound for what it was written to do** — five arms on one base — and it is the
natural handle for a reader to reach for when asking a different and much more common question:
*is the world this was measured in still the world?* `world_level_identity`'s own docstring poses
exactly that question, in those words, as the defect it exists for.

## What it actually digests

`simulation/departure_level_anchor.world_level_identity` (line 406) digests
`year_level_anchor(year)` for every year in the published switching record, and **nothing else**:

```python
record = sorted(_published_departure_rates())
anchors = {year: year_level_anchor(year) for year in record}
canonical = json.dumps({str(y): f"{v:.6f}" for y, v in sorted(anchors.items())}, ...)
return {"digest": hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16], ...}
```

It is keyed to the property it names, which is the right shape and is not the defect. The docstring
is careful and correct throughout: *"the departure LEVEL the world was running at"*. The defect is
that the field is called **`world_identity`** at the top level of every run artefact, and its own
`what_this_identifies` string says *"two runs sharing this digest ran over the same departure
surface"* in a sentence that ends *"different worlds however close their timestamps, and no figure
from one bounds a figure from the other."* A reader who takes the converse — same digest, so one
figure does bound the other — is reading the name and the second half of the sentence, and the name
is the one on the page.

## The proof that it is blind, and it is not hypothetical

The home stock demonstrably changed between `3957ba848` and this tree: `0d86d6dfe` — *"the world's
homes are drawn from the fitted joint now, and the insulation ceiling the company sells against was
understated by a third"* — is **not an ancestor of `3957ba848`**, and arrived through the
fork-closing merge `2212d0eed`. Re-measured at seed 42 by `tools/settlement_per_axis_gain.py`, the
candidate population holds **105** distinct fabric vectors against the 109 filed on 09-11, and
worst-axis KS moves 0.12798 / 0.08241 → 1.553× to 0.09765 / 0.05878 → 1.661×
(`SEAT_RESULT_P1B_IS_STILL_UNGRADEABLE_BECAUSE_THE_FILED_EVIDENCES_WORLD_IS_GONE_2026-09-15.md`).

Across that change:

```
filed at 3957ba848 (09-11, all five arms)   world_identity.digest = 39a192ce04c1eda8
measured on this tree, 2026-09-15            world_level_identity()["digest"] = 39a192ce04c1eda8
git diff 3957ba848 HEAD -- simulation/departure_level_anchor.py   (empty)
```

**One digest value spans both home populations.** The anchor module is byte-identical to its
`3957ba848` copy, so the digest could not have moved, and the homes moved anyway. A matching world
digest is not evidence that two runs saw the same homes, and on the only occasion this tree has had
to find that out, it was found by a route that had nothing to do with the digest.

## Why this is LATENT and not BLOCKING

**Nothing is published on it today that is wrong.** The digest is doing its stated job wherever it
is read — `tools/generate_dashboard_data` (2295), `tools/published_route_split`,
`tools/fit_year_level_anchor`, `tools/generate_value_arms_data` (6777, 8370) all compare a live
departure surface against a filed one, which is exactly what it can answer. The 09-11 sentence that
leans on it is *also* correct, because its five arms shared a base. The defect is the gap between
what the field is named and what it covers, and it will be load-bearing the first time someone
compares two runs across a base and concludes from a matching digest that the homes are the same.

## The remedy, and what is deliberately NOT proposed

The honest fix is **not** a second digest over the home stock added on spec. That is a control built
to watch a control, and the stock is resolved by a multi-minute world resolve that no artefact
header can afford to do.

What the evidence supports is narrower and cheaper: **`world_identity` is the wrong name for a
departure-surface digest, and `run_identity_fields` in `tools/run_annual_report.py` (314) names
`world_identity.digest` as *the* run identity.** Renaming the published key is a feed change with
eighteen binders and is not a one-turn job; naming the limit where it is read is. Until then this
finding is the record, and the five result files noted on 2026-09-15 each name their base commit
directly rather than relying on the digest to do it.

**What would refute this finding:** a reader showing that `year_level_anchor` is itself a function
of the home stock, so that a re-draw must move the digest. It is not — `_published_departure_rates`
is the published switching record, which is observed history and does not know what houses the
company's world contains.

---

## CORRECTION, 2026-09-15, beside the claim it corrects — the remedy section above was wrong

The section headed *"The remedy, and what is deliberately NOT proposed"* declined a home digest on
the grounds that *"the stock is resolved by a multi-minute world resolve that no artefact header can
afford to do"*. **That cost was never measured, and it is wrong by three orders of magnitude.**

It is true of resolving a RUN's population and false of a fixed probe. `simulation/world_home_identity.py`
draws 96 homes through `net_new_acquisition.year_premise_stock` — the function the world's homes
actually come from — and through the fabric physics, and digests what comes out:

```
96 homes, whole chain, cold   0.62 s
96 homes, warm                0.009 s
```

So the objection is retracted and the instrument is built. The other half of the section stands: the
NAME is still wrong, `run_identity_fields` still calls the whole block `world_identity`, and renaming
the published key is still an eighteen-binder feed change that was not attempted here.

**What the widening establishes, measured on this tree today:**

```
departure digest, live world                     39a192ce04c1eda8
departure digest, pre-2026-09-10 home stock      39a192ce04c1eda8   <- blind, as this finding said
home digest,      live world                     35f8efe8ff02f245
home digest,      pre-2026-09-10 home stock      0db8badd7b8dc608   <- the two are now told apart
```

The two populations are not a fixture: `net_new_acquisition.STOCK_FROM_FITTED_JOINT` still builds
both, and the `False` side is the stock the 09-11 arms ran on.
`tests/simulation/test_the_world_identity_can_tell_two_home_stocks_apart.py` asserts the pair —
sighted on one side, provably blind on the other — and is mutation-proven both ways.

**Consequence on the page, today:** `tools.generate_value_arms_data._blind_envelope` now refuses to
publish the blind-span block, because all five arms carry no home stamp at all. The capabilities page
says so in a reader's words. That is the correct state and not a regression: it was publishing a
position from a world this tree does not have, and nothing could notice.

**What is still open:** re-running the five arms in this world and stamping them. Until that lands,
the page states an absence.
