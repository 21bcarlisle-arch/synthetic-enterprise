**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_13`

# Both centre-resolvers key on declaration now — and the refusal widened with them

RECORDED rather than LATENT because the thing that made its predecessor LATENT is the thing this
turn closed. `population_mean_volume_factor` and `build_demand_shape` now resolve
`children_reference` by the same test, the partition control counts the shape that used to hide
between them, and both halves are mutation-proven on the legs written for them.

**Claim id** `centre-resolvers-key-on-different-tests-so-an-all-zero-children-book-gets-two-centres`.
**Pre-registration** `docs/staging/records/SEAT_PREREG_KEYING_BOTH_CENTRE_RESOLVERS_ON_DECLARATION_2026-09-23.md`,
filed before a line was changed and before any of the four measurements below was run.

## The premise, re-measured

**Not spent.** The draw graded `7b792426d` an ancestor of `origin/main` and it is HEAD here — but
that commit is the MOTIVE, not the work. It landed the children draw and *filed* this divergence
rather than fixing it. At HEAD, line 854 of `simulation/demand_model.py` still read
`if children_reference is None and any(children_counts):`. The forward change was untouched.

The duplicate-work note named this same id as "ALREADY HELD" in `.seat_work_in_hand.json`. That
file does not exist in this worktree; the holder is this draw. No rival.

**The path check's one verdict was wrong, and its own caveat says why.** It graded
`SEAT_RESULT_THE_CHILDREN_DRAW_IS_THE_CENSUS_CONDITIONAL...` *"[untracked] on disk and at no HEAD
blob — wholly new, nothing to revert"*. It is tracked at HEAD (`git ls-files --error-unmatch`
resolves it): `7b792426d` committed it. The verdict was computed against a base three commits
behind the trunk, and the caveat that ships with it — *"NOT ONE path those commits touched is in
the population below"* — is the claim that was false, because `7b792426d` is precisely one of the
three and this file is precisely one of its paths. Harmless here (the remedy was to edit it, not
to revert it) and worth recording, because the caveat is what licenses walking the remedies.

## What changed

1. **`population_mean_volume_factor` keys on declaration.** `children_declared = children_counts is
   not None`, captured BEFORE the `[0] * n` default erases the distinction — one statement later
   the all-zero declared book and the non-declaring book are the same object.
2. **The refusal widened with it**, and its message no longer says *"0 of 144 households declare
   children"* on an all-zero book, which is what the old wording would have produced.
3. **The partition control counts five shapes, not four**, and shape 5 — declares, all zero — is
   asserted DISTINCT from shape 1 rather than merely present.
4. Two existing legs said `children_counts=[0, 0]` and called it *"a book WITHOUT children"*. That
   is the conflation itself, written into the controls that were supposed to catch it. Both now
   say `children_counts=None`, which is what the sentence beside them always described.

## Why declaration, and why the refusal follows it

The centre is a property of the POPULATION a book is drawn from, never of the book's realisation.
Keying on `any(children_counts)` makes the DIVISOR a function of the sample: two books drawn from
one population, one of which happens to contain no child, get two different centres and neither can
tell. That is the variable-divisor defect the per-cut-set rule exists to close, moved up one level
from the household to the book — the call site already refuses it in the other direction and says so
in a comment.

**The widened refusal is fail-CLOSED, not a capability lost.** An all-zero declared book with the
source withdrawn used to answer ~1.0 against the all-adult centre: *"this response is neutral over
this book"*. The true statement is the opposite — a rare draw from a population that mostly has
children genuinely IS short of its population, and should read BELOW 1.0 against the Census centre.
The old answer was flattering in sign as well as wrong in centre.

## Predictions, against results

| | prediction | result | |
|---|---|---|---|
| **P1** | an all-zero DECLARED book's factor moves UP under the re-key, by 2.5–3.2% electricity / 1.8–2.5% gas | **+2.9135%** electricity, **+2.1714%** gas | **HELD** |
| **P2** | exactly 2 existing legs red, both asserting `[0, 0]` ANSWERS under a withdrawn source; no other leg in the repo | exactly those 2, by one-variable control (new `demand_model.py` against a pristine HEAD extract's tests) | **HELD** |
| **P3** | no production caller passes `children_counts`; the live book and every published figure are untouched | 0 callers outside `tests/` and `demand_model.py` itself | **HELD** |
| **P4** | M1 (revert the key) reds ≥1 leg, and M2 (the half-change — resolution on declaration, refusal back on `any()`) reds ≥1 too | both red, **each on the leg written for it** | **HELD** |

P1's direction was derivable before measuring and is worth keeping as the reason: the Census centre
(1.4047 electricity) sits BELOW the size-only centre (1.4456), and an all-zero book's numerators are
identical under both, so the smaller divisor raises the ratio. The measurement was run to get the
size, not the sign.

P4's second half is the one I said would be hardest to make bite, because with the source present
the refusal is unreachable and with it withdrawn the resolution and the refusal sit one line apart
keyed by the same expression. It bit:

| mutation | reds | on which leg |
|---|---|---|
| **M1** resolution back on `any(children_counts)` | 1 | `assert all_zero_declared != never_declared` — collapsed to `1.1521357114867532 != 1.1521357114867532`, shape 5 folded into shape 1 |
| **M2** resolution on declaration, REFUSAL back on `any()` | 1 | `DID NOT RAISE UnanchoredReferencePopulation` on the all-zero declared book under withdrawal |

They are different legs, which is the reading that was available to be flattering and is not: M2
leaves shape 5's distinctness untouched (the source is present there) and is caught only by the
widened refusal. Had both mutations landed on the same assertion, the refusal's widening would have
been untested and this table would say so.

## Reds, and none of them mine

The wider sweep (every test file importing `demand_model` — 518 tests) reports 9 failures. All 9
reproduce in a pristine `git archive HEAD` extract with no edit of mine in it, and all 9 are already
in `docs/staging/reference/HEAD_RED_REGISTER.md`: 8 in `tests/harness/test_premise_two_level.py`
(registered 2026-09-09) and `test_ons_shares_agree_across_the_wall` (registered 2026-09-18). The
W2_13 suites themselves are 78/78 green with the change and 56/56 on the volume-shape file alone.

The extract was rebuilt from scratch for that check. The first one was not: it had my
`demand_model.py` copied in for the P2 control and then "restored" from a snapshot taken after the
copy, so it was never pristine. Caught before it was used as evidence, recorded because a probe
tree that quietly stops being the baseline is how a one-variable control becomes a no-variable one.

## What is still open

- **The RESPONSE half of R10 GAP (a)** is untouched here, as it was by the predecessor.
  `CHILD_ADULT_EQUIVALENT_RANGE` (0.35–0.85) stays a sampled interval.
- **The sibling composition census still matches loosely.** The predecessor filed that
  `'"pensioner")'` and `'"employed")'` are matched as bare substrings one block above the children
  census, green today by luck of vocabulary. Still true, still not this turn's subject.
- **`volume_factor_is_unbiased` over a declared all-zero book now RAISES where it returned a bool.**
  No caller does this today (P3), but it is a signature-level behaviour change for any future one,
  and it is the reason this result is RECORDED rather than silent.
