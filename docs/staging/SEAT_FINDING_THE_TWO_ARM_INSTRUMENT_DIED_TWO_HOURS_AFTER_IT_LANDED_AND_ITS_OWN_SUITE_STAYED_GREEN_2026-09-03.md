**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing`

# The two-arm instrument died two hours after it landed, and its own suite stayed green

*Delivery seat, 2026-09-03, lane-0, claim `the-dd-estimate-changes-no-published-number`. Grades
`PREREG_WHETHER_REPAIRING_THE_DEAD_TWO_ARM_INSTRUMENT_MOVES_ANY_PUBLISHED_FIGURE_2026-09-03.md`
(P1–P4), filed before the instrument was re-run.*

---

## 1. What happened

`e07449df5` (04:30) landed `tools/dd_opening_arms.py` — the instrument that answers whether the
opening direct-debit estimate has any consequence — and published its comparison to
`site/capabilities/index.html`. `4e1502524` (06:09) narrowed `estimate_annual_consumption` from four
parameters to the two rungs the opening instant can actually reach, removing `metered_annual_kwh`
and `declared_annual_kwh`.

**The narrowing was right. Nothing re-ran the instrument under it.** From 06:09 until this repair,
every invocation of `python3 -m tools.dd_opening_arms` died:

```
TypeError: estimate_annual_consumption() got an unexpected keyword argument 'metered_annual_kwh'
  tools/dd_opening_arms.py:130
```

`tools/dd_opening_arms.py` was the **only** broken caller — the sole other tree hits for the two
removed names are the seam door's own docstring and the control that keeps them removed. So the
narrowing's blast radius was one file, and that one file was the measuring instrument for the claim
the narrowing was part of.

## 2. Why nothing noticed — the control shape, which is the transferable part

`tests/tools/test_dd_opening_arms.py` was **6 passed in 0.06s**. All six are green and all six are
sound; not one crosses into `run()`, `_basis_and_rate_by_customer` or `estimate_opening_by_customer`.
They test the flat arm, the credit/debit split, the bound, the matched population and the diff — every
*component* — and nothing asserts the instrument can be *invoked*.

**A suite of unit controls over an instrument's parts is silent about whether the instrument runs.**
The 0.06s is the tell: a comparison over 10,906 bills cannot be exercised in 0.06s, and nobody read
the runtime as evidence of what was not covered. This is the fail-silent class from a new direction —
not a control that cannot fail, but a *complete-looking suite whose subject is the parts and whose
claim is the whole*.

Repaired with `test_the_estimate_arm_can_actually_call_the_live_door`, which calls the company-side
entry with two real customer records and asserts the *key* it gets back, not the value. Mutation M1
(re-add `metered_annual_kwh=None`) → **RED**.

## 3. What the reader was being shown, which is worse than the crash

The crash froze the artefact. The stale prose kept publishing.

`publish_view` said: *"Which of SLC 27.15's **four** sources each estimate came from. **Three of the
four** are unreached by the live call site."* `site/capabilities/index.html` carried its own
hard-coded four-name order and rendered `our own meter reads 0`, `what the customer told us 0`.

After `4e1502524` those two rungs are not *unreached*. They are **excluded by construction**, with no
parameter left to arrive through, for reasons of **two different kinds**:

* `METERED_HISTORY` — definitional and permanent. The account is being opened; 0 of 257 supply points
  hold prior metering of ours at their acquisition date.
* `CUSTOMER_DECLARED` — a world gap that lifts the day the registration flow carries a declaration.

**A rendered `0` is a measurement: it says the supplier looked and found none.** The truth is that
there is nothing to look at, and one of the two will never be lookable. `NOT_REACHABLE_AT_OPENING`
was written precisely to keep those two reasons apart, and the page collapsed both into the same
zero as the rung that was genuinely available and scored nothing (`tdcv_typical`, 0 accounts).

**P3 CONFIRMED.** Both the note and the page were false, and had been for the whole publish.

## 4. The repair is keyed to the property, not to today's answer

**P4** required this and it is the reason the fix is not a one-word edit. The old sentence rotted
because "four" was authored as prose; replacing it with "two" would rot identically the day a rung
returns. `basis_precedence_view()` now **derives** the published block from `BASIS_ORDER` and
`NOT_REACHABLE_AT_OPENING`, and the page renders what the feed sends:

* a walked rung carries a **count**; an unreachable rung carries its **own reason** and no count;
* a basis the run resolves to that the precedence does not name surfaces as `unaccounted_for` rather
  than being dropped — a disagreement between the organ and its contract is exactly what silent
  filtering hides;
* returning `CUSTOMER_DECLARED` to `BASIS_ORDER` changes the page with nobody editing the page.

Mutations M2 (fold the exclusions into `walked` as zeros) and M3 (hard-code the precedence) → **RED**,
M2 at both the tool and, after republishing the mutated feed, at the reader's rendered page.

## 5. A published provenance field with no producer

Found while diffing the republished feed. `site/data/dd_opening_arms.json` carried
`substrate_sha256: 214e79d3…` and **no code anywhere in the tree emitted it** — zero hits outside the
feed itself. Some lane computed it in an uncommitted `publish_view` and landed the *output* without
the *producer*.

The value is correct: it reproduces byte for byte against `docs/reports/run_output_latest.json`. That
is what made it dangerous. `run_output_latest.json` is a **moving name**, rewritten every publish, so
the fingerprint is the only thing tying this comparison to the book it was measured over — and the
next honest republish would have deleted a true provenance field, with the diff reading as a
deliberate removal.

Given a producer rather than dropped: `run()` now records the hash, `publish_view` **carries** it
through and never recomputes it (recomputing would stamp today's substrate onto a measurement made
against a different one). Mutation M4 → **RED**.

## 6. P1/P2 — the repair moves no measured number

Predicted before re-running, and this is the claim that matters for the lane: both removed arguments
were passed `None`, and `estimate_annual_consumption` treats an absent value as establishing nothing,
so the walk was already `REGISTRY_EAC → TDCV_TYPICAL`.

Whole-artefact leaf diff, committed vs re-run: **317 leaves, 0 differing.** After adding the
fingerprint, exactly **1** leaf differs and it is `clock.substrate_sha256: None → 214e79d3…`.

**P1 CONFIRMED exactly. P2 CONFIRMED** — `basis_split` is still `{"registry_eac": 142}`.

So the headline finding of `SEAT_FINDING_THE_OPENING_DD_ESTIMATE_WORKS_AND_NOTHING_PUBLISHED_CAN_SEE_IT`
stands unchanged: 3 of 104 keys move, 96 matched households, the estimate ends year one closer to
square for 80 of them, mean change in absolute drift **−£201.93 (95% −£257.57 to −£143.50)**. Nothing
here revises that. What changed is that the instrument behind it can be run again.

## 7. The constraint, discharged by reading the artefact

The prereg forbade touching the company modules — the narrowing was correct and is held by
`tests/company/billing/test_the_declared_precedence_is_the_walked_one.py`. If the repair had found
itself widening the door's signature back, it had misdiagnosed which side was wrong.

```
$ git status --porcelain company/billing/annual_consumption_estimate.py \
                        company/interfaces/dd_review_outcome.py
(no output)
```

Neither file is modified. **Constraint held.**

## 8. What is still owed

* **The suite still cannot run the whole instrument.** The new control reaches the company door; it
  does not build both arms over a book, because that needs the 10,906-bill substrate and belongs in a
  slower selection than the per-module gate. The instrument dying on the *arm-building* half would
  still be caught only by running it. Named here rather than left as an implied "covered".
* **`tdcv_typical` is a walked rung with 0 accounts** — genuinely available, genuinely unexercised,
  because every account this world draws carries a registration EAC. That zero is now correctly
  distinguished from the two exclusions, but it means the precedence is still exercised at **one**
  value, and a fallback that never fires is a branch nobody has watched work.
* **Whoever lands the artefact must land the producer.** §5 is the second instance of that shape on
  this one file in two days.
