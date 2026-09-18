**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# The page paired its error bar on a curriculum setting and called it the book

**Filed:** 2026-09-18 · **Claim id:** `re-run-the-noise-floor-over-the-09-18-book-so-the-error-bar-stops-refusing`
**Pre-registration:** `docs/staging/records/PREREG_THE_TWELVE_AT_HEAD_OVER_THE_09_18_BOOK_AND_WHAT_WOULD_MAKE_ME_NOT_PUBLISH_THEM_2026-09-18.md`
**Found by:** re-measuring a drawn item's premise before starting it. The item said the floor was
STALE. It is, and that is the weaker half.

---

## The defect

`_floor_admission` in `tools/generate_value_arms_data.py` answers the question every directional
claim on the arms page is gated on — *was this spread drawn over the book this figure is made
of* — and it reports one of two named rules to the reader. On the live pair it reported the strong
one, `declared_book`, `admitted: true`.

It pairs on the **declared** half of the book identity, which on this feed is:

```
served_segments: ["resi", "SME"]   served_segments_resolved_from: "curriculum"
```

**Every run this company has ever done declares that.** As a discriminator it is a constant, so
the rule named for the book cannot separate any two runs of this world, and the page has been
telling a reader the book decided while nothing about the book was being compared.

What it let through, live, on the promoted 09-18 pair:

| | settled billing accounts in window |
|---|---|
| `NOISE_FLOOR_PATH`, all 18 seed rows | **164** |
| `THREE_ARM_PATH`, control / value / level arm | **154 / 155 / 154** |

A spread over a 164-account book, published as the error bar on a figure from a 154-account one,
under a field saying the book admitted it.

## Why nobody used the half that could see it

The producer's `floor_book_identity` writes the realised counts and instructs consumers not to
pair on them:

> *"Pair on `declared` and never on `realised_across_seeds`. The declared half is the book the run
> was given; the realised half is what the seed's own churn did to it, so two floors of the SAME
> book differ there by construction. A consumer that compared the counts would refuse every honest
> re-run."*

`_floor_admission` quoted that reason back, and `tests/tools/test_generate_value_arms_data.py`
asserted it as a control — `test_the_pairing_is_on_the_DECLARED_half_and_never_on_the_realised_counts`.

**The reason is true of one of the five realised fields.** Measured across the only two real
families this page has:

| field | next12, 12 seeds, 1 tree | folded eighteen, 18 seeds, 2 trees |
|---|---|---|
| `billing_accounts_settled_in_window` | 154 .. 154 | 164 .. 164 |
| `with_an_electricity_leg` | 136 .. 136 | *(seed rows carry only the first)* |
| `with_a_gas_leg` | 90 .. 90 | |
| `dual_fuel` | 72 .. 72 | |
| `accounts_at_end_of_window` | **54 .. 55** | |

Re-drawing elasticity moves who is still on supply at the window's edge. It does not move who
appeared in the window at all — so four of five did not move by a single account across twelve
seeds, or across eighteen drawn by two different code trees. **One field's behaviour was
generalised to five, and the working discriminator was thrown out with the broken one.** This is
the project's recurring shape: a concept named once, differenced, published, and treated as a
driver, without anyone saying which of several things it was.

## The repair

A realised leg that tests **disjoint ranges**, not equality, ANDed with the declared one.

- It names no field as stable and no count as correct. A field that moves within either side
  widens its own range and stops being able to prove anything — the fail-closed direction.
- The floor side reads `realised_across_seeds` **or the seed rows**. The live floor is a fold, and
  a fold declares the realised summary unavailable while all eighteen of its rows carry the count.
  A guard reading only the summary would have answered "not askable" on the one pair where the
  answer was in front of it eighteen times.
- The run side is a range **across arms**, because they legitimately differ: pricing a renewal
  moves who renews and therefore who settles, which is the 154-vs-155 above.
- It adds a refusal and removes none, in both admission branches — including the stamp-proxy
  branch, where a floor with no declared book may still carry counts and nothing else is looking.

Measured, both legs of the partition reachable from this feed's own artefacts:

```
published folded eighteen (164 book)  ->  admitted False, refusal names 164 vs 154-155
next12 on disk (154 book)             ->  admitted True, on all five fields
```

**The honest re-run the old reason was protecting is admitted, on every field.** That claim was
the assumption; it is now the measurement.

`_staleness_caveat`'s published sentence is corrected in the same commit. It told the reader *"the
noise floor names no book identity of its own, so nothing here can show that this spread was drawn
over the decisions the figure is made of"* — true when typed, false on the live pair, and a refusal
whose stated reason is false is worse than no refusal because the reason is the part a reader acts
on. It now composes from what the two artefacts say: books provably different, books agreed and the
objection is the order alone, or the question genuinely unaskable — three distinguishable sentences.

## What it does NOT fix, and the run that does

The page still refuses, and it should: the floor is over the wrong book, and a guard is not a
substitute for a measurement. The floor re-run over the 09-18 book at `18327d977` was launched this
turn and is in flight — twelve seeds, ETA 2026-09-19 08:20Z, pre-registered above with its decision
rule. **This finding closes when that floor lands and is admitted on the book rather than waved
through on a curriculum setting.**

One consequence worth stating plainly: had the repair not landed first, that new floor would have
been admitted under `declared_book` **whether or not** prediction 2 of the pre-registration held.
The guard that was supposed to check my own run could not have checked it.

## Eleven, then twelve

Four fixtures in the producer's test file bound the floor's STAMP to the run (`_stamped_after`,
written 2026-09-09 after ten controls reported the failure of a guard they did not name) and left
its BOOK to whatever was on disk. The 09-18 promotion made that a 164-versus-154 mismatch, so the
new guard refused five controls whose subject is something else entirely. `_booked_like` binds the
second property the same way, for the same reason. **A twelfth helper beats a twelfth diagnosis.**
