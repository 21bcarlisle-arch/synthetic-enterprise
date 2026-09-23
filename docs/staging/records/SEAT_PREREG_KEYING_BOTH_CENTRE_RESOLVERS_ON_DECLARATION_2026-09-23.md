# PRE-REGISTRATION — keying both centre-resolvers on DECLARATION, and what that does to the refusal

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_13`

**Filed** 2026-09-23, BEFORE any of the measurements below were run and before a line of
`simulation/demand_model.py` was changed. Claim id
`centre-resolvers-key-on-different-tests-so-an-all-zero-children-book-gets-two-centres`.

## The premise, re-measured at draw time

The item cites `7b792426d`, which the draw grades an ancestor of `origin/main` — and it is HEAD
here. That commit is the **motive**, not the work: it landed the children draw and *filed* the
divergence rather than fixing it (`SEAT_RESULT_THE_CHILDREN_DRAW_IS_THE_CENSUS_CONDITIONAL...`,
§"FILED, NOT FIXED"). The forward change — re-keying `population_mean_volume_factor` and
re-justifying the refusal — is untouched at HEAD: line 854 still reads
`if children_reference is None and any(children_counts):`. **The premise is NOT spent.**

The duplicate-work note names this same id as "ALREADY HELD" in `.seat_work_in_hand.json`. That
file does not exist in this worktree and the id is the one this draw issued, so the holder is this
draw. No rival.

## The change, stated before it is made

`population_mean_volume_factor` resolves `children_reference` on `any(children_counts)` — the
book's realised VALUES. The production call site `demand_model.build_demand_shape` resolves it on
`"children_count" in property` — the record's DECLARATION. Re-key the aggregate to declaration
(`children_counts is not None`, captured before the `[0] * n` default overwrites the distinction).

**The refusal moves with it, and that is the part with its own argument.** Widening to declaration
means a book that declares all-zero children with no reference **starts refusing where it used to
answer**. My position, to be defended or abandoned below: that is the FAIL-CLOSED direction and
the old behaviour was flattering. The centre is a property of the POPULATION a book is drawn from,
not of the book's own realisation. A 144-home book drawn from the Census population that happens
to contain no child is a rare sample, and it *should* read below 1.0 against the Census centre —
"this book is short of its population" is the true statement. Answering ~1.0 against the all-adult
centre says "unbiased" about a book that is not, which is the same variable-divisor defect the
call-site comment refuses one level down, merely aggregated.

## Predictions

| | prediction |
|---|---|
| **P1** | With the source present, an all-zero *declared* book's mean factor MOVES under the re-key, and moves UP — the Census centre is below the all-adult centre (1.4047 vs the size-only normaliser) while an all-zero book's numerators are unchanged, so a smaller divisor raises the ratio. Size: **+2.5% to +3.2% electricity, +1.8% to +2.5% gas**. |
| **P2** | Exactly **2** existing test legs go red from the re-key, both asserting `children_counts=[0, 0]` ANSWERS under a withdrawn source: `test_w2_13_occupancy_volume_shape.py:547` and `:647`. Both are mis-worded as "a book WITHOUT children" — the repair is `children_counts=None`, which is what that sentence actually describes. No other leg in the repo reds. |
| **P3** | No PRODUCTION caller passes `children_counts`; every caller of `population_mean_volume_factor` outside `tests/` is zero in number, so the live book is untouched and no dashboard/site figure moves. |
| **P4** | Reverting the key to `any(children_counts)` (M1) reds **at least one** leg written here, and reverting only the REFUSAL's key while leaving the resolution keyed on declaration (M2 — the half-change) reds **at least one** leg too. If M2 is silent, the refusal's widening is untested and I say so rather than claiming it. |

P4's second half is the one I expect to be hardest to make bite, because with the source present
the refusal is unreachable and with it withdrawn the resolution and the refusal are keyed by the
same expression one line apart. If I cannot make M2 red I will report an equivalence with its
argument, not a pass.

## What done means

Both resolvers key on declaration; the refusal's message no longer says "0 of N households declare
children" on an all-zero book; the partition control counts the shape it actually has; mutations
run and recorded with their reds; landed and promoted.
