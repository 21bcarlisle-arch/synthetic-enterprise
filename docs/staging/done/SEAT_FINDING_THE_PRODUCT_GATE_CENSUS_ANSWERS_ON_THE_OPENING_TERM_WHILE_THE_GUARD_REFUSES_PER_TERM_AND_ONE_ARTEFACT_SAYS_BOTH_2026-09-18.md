**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

*BLOCKING, and the severity is a sequencing claim rather than an alarm: the false verdict is on the
very page this lane is about to republish, so republishing first would entrench it under a fresh
`generated_at`. Fix the unit, then republish.*

# The product-gate census answers on the opening term while the guard refuses per term, and one artefact publishes both

**Filed:** 2026-09-18 · **Claim id:**
`the-republish-is-blocked-on-six-controls-and-a-dead-tariff-branch`
**Supersedes the remedy in:**
`docs/staging/SEAT_FINDING_THE_UNLABELLED_TARIFF_BRANCH_IS_DEAD_AND_THREE_CONTROLS_PINNED_TO_IT_HAVE_REDDENED_HEAD_2026-09-18.md`

---

## The domain question was asked and it is already answered in this repository

That finding said the choice between deleting the dead `None` branch and restoring a reachable
unlabelled state *"is a question for the domain, not the code"*, and recommended asking it first.
**It has been asked and ruled on, and the ruling has already been implemented.**

`docs/design/DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md` (settled 2026-08-28, against Ofgem /
CMA / DESNZ anchors at H-confidence) rules that `tariff_type is None` **is the symptom, not the
state**: an unresolvable product is not a thing a real supplier has, because a supplier that cannot
name the product cannot bill. The field was unset *because the world had only one domestic product
to offer*. What the determination registered as owed was **a standard variable tariff** — no locked
rate, no term boundary, no renewal decision, cap-bounded from Jan 2019.

**That product landed on 2026-09-16.** `simulation/svt_product.py` holds `SVT_TARIFF_TYPE = "svt"`
and `build_svt_schedule`; `simulation/renewals.build_renewal_schedule` delegates to it rather than
branching, and `run_phase2b` indexes it. So the answer to "is an unresolvable product real" is **no,
and the real state it stood in for now exists under its own name**. Option (2) is refuted — restoring
an unlabelled state would restore the symptom the determination refused. Option (1) is right about
the dead branch and wrong about the consequence: the product gate is **not** an abolished diagnostic.
It is a live, load-bearing refusal, and the 09-18 run measures it at **2,490 of 2,824 offered
renewals (88%), every one of them `'svt'`**.

## The defect: two blocks of one artefact, one read, opposite answers

`value_cycle_ab_s1_three_arm_20260918.json`, `renewal_funnel.value_arm`:

| block | what it says about the product gate |
|---|---|
| `product_not_upliftable_by_tariff_type` | `{"'svt'": 2490}` — the gate is where 88% of the book stops |
| `product_label_by_account_class.legs` | all 232 legs `resolved_tariff_type: "fixed"`, `the_guard_admits_it: true` — **every leg** |
| `product_label_by_account_class.a_found_account_can_reach_the_product_gate` | `true`, 145 found accounts admitted |

Both are computed correctly. **They are not the same census, because they are not counted over the
same unit.** `product_label_by_account_class` reads `resolved_tariff_type(record)` — the product the
record's schedule builder stamps on its **opening** term, which since the 2026-09-16 gas repair is
`"fixed"` for every record on the roster. The guard is applied per **term**, and every boundary after
the opening one is decided by the household's own engagement roll: a passive roll settles the next
term as `svt`, which the guard refuses.

So the census's derived verdict — the field **the live page's sentence turns on**, per
`tests/tools/test_the_renewal_funnel.py`'s own null-rung docstring — answers a question no reader
asks. "Can a found account reach the product gate" is `true` for all 145, while the same artefact
records that the gate is the single largest refusal in the funnel.

**This is the 2026-08-30 addendum's defect a second time, from a different cause.** That one was a
restated *spelling* going stale, and the census's docstring was written to end it: *"Two blocks of
one file disagreeing about one read is what a restated spelling buys."* This one is a restated
**unit** — per-record where the guard is per-term — and the same docstring cannot see it, because
the census does call the world's own function. It reads the right function over the wrong population.

**Before dividing two numbers, say what each one counts.** Neither of these blocks says what its
unit is, and that is why one file can carry both.

## Why it is ACTIVE and not latent

`a_found_account_can_reach_the_product_gate` is rendered. While it reads `true` with 145 accounts,
the page tells a reader that the product gate is not what stands between the found book and being
priced — when it is exactly that, for 88% of the renewals the world offered. The direction this
licenses is the wrong one: *grow the book* rather than *the reachable surface is a third of a
domestic book and that is market structure*, which is the determination's own closing paragraph and
is the honest enterprise-value claim.

## The remedy

Census the product **per term**, over the same population the funnel counts, and keep the per-record
read as a separate, named block if it earns its place. The two must not share a verdict field. The
guard's own unit is the term; anything reported as "what the guard reads" that is not counted per
term is not what the guard reads.

**Not attempted in this turn, deliberately.** It changes a published field on the live page, and the
value-arms republish is already blocked on six controls; landing a verdict change underneath that
would make the republish unattributable. It is the next piece and it is handed on.

## What I landed instead, and what it does not claim

The three `test_the_renewal_funnel.py` legs that had been red at HEAD since 2026-09-16 are repaired
and green, re-keyed off the dead `None` and onto `svt` — a product the world genuinely settles and a
refusal the guard genuinely makes. Four mutations proven to fire (census restates `.get`, census
assumes the label, guard admits every product, reachability drops its found-class clause).

The repair **does not** fix the unit mismatch and must not be read as having done so: it restores the
null rung on a verdict that is now measured over the wrong population. The control's docstring says
this in place, beside the assertion, and points here.

**One honest limit on the bound fixture.** No *live* record carries `svt`, because the world decides
svt per term rather than on the record — so the discriminating pair in the repaired control is bound
rather than found. That is the repair, not a weakness of it: this control lost its subject to a
world-repair three times (2026-08-30, 2026-09-07, 2026-09-16) precisely because it looked for the
pair on the live roster. Its subject is the census's behaviour, which the fixture owns. Once the
remedy above lands, the live roster carries the pair again at the term level and the leg can be
re-keyed to find it.

## What would refute this

A reader of `product_label_by_account_class` that already re-counts per term downstream, or a term
population for which `svt` terms are excluded before the guard sees them. I checked the second on the
09-18 artefact and it does not hold: `product_not_upliftable_by_tariff_type` is keyed on the term's
own `tariff_type` and reports `'svt'` and nothing else. I have **not** enumerated every reader of the
census block, so the first is open.
