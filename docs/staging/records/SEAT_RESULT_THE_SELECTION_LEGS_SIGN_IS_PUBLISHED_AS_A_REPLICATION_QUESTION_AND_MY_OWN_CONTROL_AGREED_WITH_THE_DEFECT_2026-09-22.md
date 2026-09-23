**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The selection leg's sign is published as a replication question now, and two of my own controls agreed with the defect they were written for

**Claim:** `the-selection-legs-sign-is-a-property-of-which-floor-was-drawn-and-four-same-world-families-disagree`
**Subject:** `tools/generate_value_arms_data.py` · `site/capabilities/index.html` · **Date:** 2026-09-22
**Pre-registration:** `docs/staging/records/PREREG_THE_SIGN_ACROSS_FOUR_SAME_WORLD_FAMILIES_IS_PUBLISHED_AS_A_REPLICATION_QUESTION_2026-09-22.md`

## The item's premise was half wrong, and the half that was wrong made the defect worse

The item said *"the page's verdict clause calls the selection leg negative off ONE floor"*. It does
not, and has not since the seven-controls repair landed: `error_bar.legs_on_one_bar` is **refused**
on the live publish, so the page published no sign for any leg at all. The strongest claim about the
choosing was not being over-stated — it was **absent**, along with the two legs that replicate.

That is the more expensive version of the same defect, not a reason to close the item. The page
answered "we cannot tell" by pointing at one refused pair while four same-world families on this
disk grade the same three contrasts. They **agree** on the value and level legs and **disagree** on
the selection leg. A page holding four graded families and publishing the reading of none is
publishing less than it knows, in the direction that happens to read safe.

## What now reaches the reader

`_the_sign_across_families` grades every same-world family against the run it was **measured on**
— the pairing rule the seven-controls finding established — through `_legs_on_one_bar` itself and
through no second grader. It renders on the **refusing** branch as well as the admitted one, which
is the branch it exists for.

| family (× the run it was measured on) | value leg | level leg | selection leg |
|---|---|---|---|
| 9-seed floor, 09-10 23:03 × `three_arm_20260910` | 22.71σ positive | 49.45σ positive | 2.85σ **negative** |
| 9-seed floor, 09-10 21:34 × same run | 34.39σ positive | 39.10σ positive | 0.55σ no sign |
| 12-seed floor, 09-18 11:07 × live | 7.42σ positive | 5.24σ positive | 0.69σ no sign |
| 12-seed floor, 09-19 09:10 × live | 7.42σ positive | 4.73σ positive | 0.17σ no sign |

Published verdicts, **derived from the signs and not written beside them**: value leg `replicates`,
level leg `replicates`, selection leg `not_settled` — a sign on 1 of 4. The same seed rows that
reach 49.5 standard errors on the legs that replicate cannot call the choosing on three of four,
which is what refutes "these floors are simply too noisy to grade anything".

## Predictions, including the two that were refuted

**P1 — the verdict is derived. CONFIRMED, and over real bytes.** The first entry of the production
pair tuple alone reaches `replicates` on every leg with no string edited. Both sides of the
partition are reachable without a mutation.

**P2 — all three legs graded. CONFIRMED.**

**P3 — at least 3 mutations red, at least one by name on the verdict. CONFIRMED,** 6 of 7 red. But
the interesting result is the two that were silent on the first sweep, because **both silences were
defects in my own controls**:

| mutation | reds (final) | first sweep |
|---|---|---|
| M1 `contested` → `not_settled` | `..._classifier_reaches_all_three_of_its_own_outcomes` | **SILENT** |
| M2 count an ungradable family as gradable | 2 | 2 |
| M3 drop a leg from the census | 3 | 3 |
| M4 re-type the derived `49.5` as a literal | `..._strength_..._measured_and_not_typed` | **SILENT** |
| M5 unreadable family loses its reason | `..._neither_agreement_nor_disagreement` | **SILENT** |
| M6 grade every floor against the LIVE run | 3 | 3 |
| M7 pass `point_clock=None` | — | equivalence, established below |

**M1 was an unreachable branch, not an equivalence.** No two families on disk state *opposite*
signs — every sign stated is `negative` — so nothing in the corpus can tell "the floors disagree"
from "some floor cannot say". Those are different claims and collapsing them flatters the milder
one. The distinction is kept and its reachability is now asserted over the classifier's own
partition rather than left to a corpus that cannot exercise it.

**M4 is the one worth carrying forward: my control agreed with the defect because the literal WAS
today's value.** The control asserted the sentence quotes `_strongest_sems(...)`. Re-typing that
number as `49.5` satisfied it exactly, because 49.5 is what the rows currently reach. A control
keyed to today's answer cannot detect a literal keyed to today's answer — they agree by
construction. The repair is two pair sets whose strongest leg differs: a hard-coded number can
satisfy at most one, a derived one satisfies both.

**M7 IS an equivalence, and it was established rather than assumed.** `point_clock` reaches exactly
one field of the grader's output — `single_run` — which this census deliberately does not publish,
each family's single run being the neighbouring block's subject. Verified by driving the census
with the argument nulled: rows byte-identical; full grader output differs only in `single_run`.

**P4 — the existing door goes green unchanged. CONFIRMED**, 904 passed across the whole site lane,
with 3 new door controls green against the page's own JavaScript.

## The gate caught a third defect I had not predicted, and it was the same shape again

The first landing attempt was refused by
`test_NO_TWO_KEYS_in_the_payload_answer_the_clears_zero_question_oppositely`. `error_bar` holds a
registry of every key bearing on *"does the selection family's mean clear zero"*, and a net that
catches any boolean-or-null leaf whose name carries `sign`, `stateable`, `clears`, `agree` or
`distinguishable`. My census had republished `sign` and `sign_is_stateable` **per family** — five
unclassified new homes for that question.

The tempting repair was to classify them and move on. That would have been wrong twice over: these
rows answer the question for a **different family**, so filing them under the published family's
registry would make the registry say something false; and the registry's `_at` walks dicts only, so
list-nested paths would then report as keys the payload no longer publishes.

The actual defect was mine and the gate named it precisely: **a per-family copy of the verdict
machinery is a second home in the plain sense.** `per_leg` already carries the counts and the signs
stated. So each row now states its side as a STRING (`what_this_family_states`), which is never a
boolean or a null, and `sign_if_it_replicates` — redundant with `verdict` + `signs_stated`, and
readable as "the sign" by a consumer that never checked the verdict beside it — is **deleted**.

A declared `"no sign at its own bar"` is also not a silent `None`, which is the collapse this
project has paid for elsewhere: a family that was graded and could not call its side has said
something, and it now says it in words.

The refactor changed the mechanism every control keys on, so the sweep was re-run rather than
assumed: M1, M4 and M6 still red by name, and the string sentinel bought a new one (M8 — treating a
no-sign family as stating a sign reds two controls).

**P5 — runtime. 0.12s** for four extra `_legs_on_one_bar` calls over committed artefacts.
Immaterial, as suspected but not asserted in advance.

## What is still owed, and it is not this item

The one-variable run the `NOISE_FLOOR_PATH` block has owed since 2026-09-18 — these twelve seeds at
`4e7938f673` — still separates the instrument from the seed set, and nothing here substitutes for
it. What changed is that a reader no longer meets a single refusal where four families disagree;
they meet the disagreement, with each floor named beside the run it bounds.
