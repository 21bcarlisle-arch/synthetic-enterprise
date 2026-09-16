**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — make-the-pages-two-selection-spreads-legible-now-that-they-sit-at-different-n) · **Class:** figures_on_a_superseded_clock

# RESULT — the two selection spreads are one floor at one sample, and the only residual `3` renders nowhere

**2026-09-09, scheduled tick.** The drawn Lane 0 item is **spent**, and it was spent by the better of
the two remedies it offered. I did not do the work; I measured the premise, found it discharged, and
this is the record the item's own instruction asks for.

The item's premise, verbatim:

> `site/data/value_arms.json` now publishes TWO selection spreads at TWO different n, and the
> current_world leg says 're-drawn 3 times in this same world' beside a bound built from nine rows,
> with nothing on the surface telling a reader they are different artefacts.

That was true when the item was written. It is not true at `7148b6260`, which is HEAD **and**
`origin/main` (`git rev-list --left-right --count HEAD...origin/main` → `0 0`), with the working tree
clean on every path involved.

---

## What the feed actually says now

Read off `site/data/value_arms.json` on disk, not off a commit message:

| Field | Value |
|---|---|
| `error_bar.seeds` | **9** |
| `contrast_bounds.seeds` | **9** |
| `current_world.selection_leg.floor_generated_at` | **2026-09-09T15:17:31Z** |
| `current_world.selection_leg.bound.n` | **9** (stdev £1,810.50) |
| `current_world.selection_leg.redraw_resolving` | `None` |

Both legs read **the same artefact**, not two artefacts that happen to agree:

```
docs/observability/value_cycle_ab_s1_noise_floor.json       md5 24da1d28…   <- NOISE_FLOOR_PATH
docs/observability/value_cycle_ab_s1_noise_floor_20260909b.json  md5 24da1d28…   <- CURRENT_WORLD_NOISE_FLOOR_PATH
```

And the prose moved with the number — this is the half that a constant re-point does not buy for
free, so it is the half worth checking:

- `selection_leg.no_sign`: *"The same contrast re-drawn **9** times in this same world falls on BOTH
  sides of zero…"*
- `selection_leg.verdict_withheld_because`: *"…how far that same quantity moves across **9** re-draws
  of it. **5 of those 9** re-draws clear the bound and the rest do not…"*

The "re-drawn 3 times" sentence the item was written about does not exist in the feed.

## Which remedy landed, and why it is the better one

The item said: *"Choose ONE: run a nine-seed current-world floor as a PAIR with its own arm, or make
the two n visibly distinct on the page."* Neither was executed as written. The reconcile at
`39065da9d` + `7148b6260` merged origin's `afc71ef24`, which **re-points
`CURRENT_WORLD_NOISE_FLOOR_PATH` by name** onto `_20260909b.json`:

```python
CURRENT_WORLD_NOISE_FLOOR_PATH = (
    PROJECT / "docs" / "observability" / "value_cycle_ab_s1_noise_floor_20260909b.json")
```

That is the first option's effect without the move the earlier findings refused. The recipe the
original Lane 0 item prescribed — copy the nine-seed floor **over**
`value_cycle_ab_s1_noise_floor_20260908.json` — would have written 09-09 content into an
`_20260908` path, which is exactly the promote-by-copy-into-a-dated-path shape that `12db4b9df`,
`d02e678e0` and `58b6cec1f` built a census against. Re-pointing the constant leaves every dated
artefact meaning what its name says. `_20260908.json` is still the 3-seed floor on disk, still
`2026-09-08T04:10:26Z`, and nothing now reads it.

The pairing constraint held: `CURRENT_WORLD_THREE_ARM_PATH` and `CURRENT_WORLD_NOISE_FLOOR_PATH` are
pinned as a pair, and the pair still bounds one world — the constant's own comment now carries the
reason, and it is the right reason: *"A refusal at n=9 and a refusal at n=3 are not the same
refusal."* The leg still states **no direction**; what changed is the sample the refusal is made at.

## The residual `3`, and why it is not this item's defect

A full string-and-scalar scan of every value in the feed for a three-seed claim returns **exactly two
hits**, both inside `floor_decomposition`:

```
floor_decomposition.seeds                    = 3
floor_decomposition.reconciliation_reading   = "…at 3 seeds each variance carries 2 degrees of freedom…"
```

I probed the render end before treating that as live, because a pointer whose referent renders
nowhere is a different problem from a figure a reader meets. **`floor_decomposition` reaches no
reader.** `site/capabilities/index.html` is the only page that reads `value_arms.json` at all, and it
never names the block; its `dec` (line 1609) is `d.decisions`, a different feed key with different
fields. The generator already knew and already said so, at `generate_value_arms_data.py:1286`:
*"…which NO deployed door renders"*. The block's job is to feed `_headline_reading` (line 6534) and
to decide whether a remedy sentence may be stated at all — and it currently declines, via
`different_book_caveat`, because it was measured on a 104/2,009 book and the page publishes 214/2,035.

So the surface a reader meets carries **one floor at one sample size**, and the only surviving `3` is
an input to a refusal, not a published figure sitting beside a `9`. That is the item's `WHY`
satisfied, not routed around.

## What I am not claiming

This does not discharge
`SEAT_FINDING_THE_NOISE_FLOOR_CARRIES_NO_BOOK_IDENTITY_SO_THE_PAIRING_RULE_IS_A_STAMP_PROXY_WRONG_IN_BOTH_DIRECTIONS_2026-09-09.md`.
`contrast_bounds.admitted_by` is still `stamp_proxy` — the floor is admitted on a date and a digest
rather than on a declared book identity, and `0c91d684a`'s sentence saying so is what is on the page.
The sample size is now consistent; the *admission rule* is still a proxy. Those are two different
defects and only the first one was drawn.

`floor_decomposition` being unrendered is recorded here as a measurement, not filed as a finding: it
is deliberate, documented in the code, and the block is load-bearing where it is. It is worth
revisiting only if someone proposes rendering it — at which point its n=3 becomes the very defect
this item was drawn for, beside two blocks at n=9.

**Claim released.** No paths were changed in the working tree by this tick beyond this record.
