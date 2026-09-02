**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

# Pre-registration: what a control on the anchor module's retired-table citation must show

**Filed 2026-09-02, worker tick, BEFORE writing the control and BEFORE running it.** Every
prediction below is written against a state I have read (the current citation) and an outcome I have
not (what each leg does when executed). Graded beside its filed text; misses kept.

## The subject

`simulation/departure_level_anchor.py:88-89` says, of the live seven-year block:

> The retired ten-year table and the working is in
> `docs/design/UNLANDED_WHOLE_BOOK_LEVEL_ANCHOR_BLOCK_2026-09-01.md`.

That document exists. It contains the **seven-year block** — the one that is now LIVE — preserved on
2026-09-01 when it was in no commit. It does not contain the retired ten-year table. The retired
table is in `docs/design/THE_LEVEL_ANCHOR_COLLISION_ANSWERED_2026-09-02.md`, whose ten rows match
`71242c941`'s block exactly.

So the paragraph immediately above this citation — *"THE PROVENANCE IS MEASURED, NOT CITED, because
the block this replaced could not be followed"* — sits above a citation that cannot be followed. Same
class, one line down.

## Why the obvious control is fail-open here, which is the whole reason to pre-register

The reflex control is *"every document path cited in this module exists"*. **That control is GREEN on
this defect.** The cited document is real, committed, and on origin. A path-existence check cannot
distinguish "points at the right document" from "points at the wrong real document", and the
catalogued shape it lands in is *a control whose PASS branch cannot see the failure it is named for*.

The claim is not *a file exists*. The claim is *this document holds the retired table*. A control has
to read the document for the values.

## Predictions

**P1 — the containment leg is RED at HEAD's current citation.** Written before the control exists: a
leg asserting that the document cited as holding the retired ten-year table contains that table's
values will FAIL against HEAD as it stands, and its message will name the cited document.

**P2 — the same leg is GREEN after re-citing to `THE_LEVEL_ANCHOR_COLLISION_ANSWERED_2026-09-02.md`,
and green for the right reason** — because all ten retired values are found in it, not because the
subject went empty. If the leg passes while matching zero values, that is a MISS and is recorded as
one.

**P3 — the weaker control cannot fire, and this is the load-bearing prediction.** A path-existence-only
version of the check, run against the UNCORRECTED citation, PASSES. If it fails, my account of why
this defect survived is wrong and I will say so: it would mean the defect was reachable by the cheap
check all along and nobody ran it.

**P4 — MUTATION, the leg can fail for its own reason.** Removing any single year's value from the
retired table in the cited document turns the leg red, naming that year. Proven under `python3 -B`.
A leg that stays green on a nine-of-ten document is asserting "some numbers are present", not "the
retired table is here".

**P5 — the fix moves no run.** Correcting a comment cannot change `YEAR_LEVEL_ANCHOR`,
`year_level_anchor` or `anchor_coverage`. `tests/architecture/test_switching_rate_commons.py` and
`tests/simulation/test_departure_risks.py` stand at their current verdicts — 33 passed / 2 xfailed on
the former. **Specifically: both xfails stay xfail.** If either flips, the change was not what I
described and I stop and attribute it before landing.

## What this does NOT claim

It does not claim the live block's provenance is now followable — the live block states its
provenance as *measured from the `sim_level_anchor` column*, deliberately not as a filename, and this
control says nothing about that choice. It does not re-open the collision decision, which is answered
at `d374b1977`. It does not touch either xfail marker, and it must not: the band leg is held open
STRICT on purpose and P5 is what proves I left it alone.

---

# GRADING, 2026-09-02, same tick. Five predictions, five hits, and one of them was worth the filing.

**P1 — HIT.** Probed before the control was written, against HEAD's citation:
`UNLANDED_WHOLE_BOOK_LEVEL_ANCHOR_BLOCK_2026-09-01.md` carries **0 of 10** retired values (every
year 2016-2025 missing). Reproduced afterwards through the finished leg as MUTATION 1 — re-pointing
the citation back at that document fails with `assert not [2016, 2017, ..., 2025]`.

**P2 — HIT, and green for the stated reason, not an empty subject.**
`THE_LEVEL_ANCHOR_COLLISION_ANSWERED_2026-09-02.md` carries **10 of 10**, matching `71242c941`'s
block exactly. The leg passes with a non-empty match set; `_document_cited_for_the_retired_table`
refuses an absent marker and an absent citation rather than passing over either.

**P3 — HIT, and this is the one the pre-registration earned its place for.** `path.is_file()` on the
**uncorrected** citation returns `True`. A path-existence control is GREEN on this defect. Had I
written the reflex control, it would have passed, I would have recorded the citation as held, and
the claim would have rotted under a green light. The leg keeps the existence assertion — it is
cheap and it catches the never-written-path case — but it is explicitly not what does the work here.

**P4 — HIT, both directions, `python3 -B`.** (i) Citation re-pointed at another real document in the
tree → red, naming all ten years. (ii) 2020's `4.425742` removed from the cited document → red,
naming `[2020]`. Both restored and re-verified green; `git diff --stat` after restore shows only the
intended module edit.

**P5 — HIT.** `tests/simulation/test_departure_risks.py` + `tests/architecture/test_switching_rate_commons.py`
together: **56 passed, 2 xfailed**. The commons file stands at its prior 33 passed / 2 xfailed.
**Both xfails stayed xfail** — the band leg is still held open STRICT and the whole-book leg with it.
Neither marker was touched, re-keyed, or discharged, which is what P5 existed to prove.

## Unpredicted, and recorded rather than acted on

The `#:` comment block is not the only place this class can live, and I checked only the one module.
`anchor_coverage()` has no consumer outside `tests/simulation/test_departure_risks.py` — no published
surface asks which years are fits, so the partition the collision decision produced is currently
readable only by a test. That is not a defect in this lane's scope and I am not fixing it here, but
it is the next thing to look at if the anchor's coverage is ever meant to reach a reader: a
disclosure nobody reads is one step from the constant PASS this file's controls are about.
