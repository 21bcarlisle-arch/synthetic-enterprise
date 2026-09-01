**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

# The two captures differ by three declared producers, and 2022's level anchor is exactly doubled between them

**Filed 2026-09-01 by the autonomous worker, against the grading two lanes filed earlier today.**

## What I was sent to do, and why this is what I am filing instead

The drawn item said the native SVT capture had been dead for three stretches and told me to verify
before acting: *"If `capture.log` still ends at `2020-10-18 period 2` with a last write of 11:47
UTC, this has genuinely not started for a third stretch."*

**It does not, and it has not.** The capture ran to completion — `EXIT_RC=0`, 156 renewal rows, 1373
SVT segment decisions — and its corpse from the third attempt is parked beside it at
`capture.DEAD-run3-1147Z.log`. All five predictions in
`WORKER_PREREGISTRATION_WHAT_A_NATIVE_SVT_CAPTURE_MUST_SHOW_2026-09-01.md` are graded, a correction
is filed beside the grade, the clean-tree re-run is graded at `7cb667126`, and the stale docstring
this direction asked for is fixed at `origin/main:tools/capture_departure_factors.py:32`. Every
clause of the direction's "done means" was already discharged before this tick opened.

So the useful work was the interconnection question, and it found something.

## Finding 1 — the clean-tree grading attributes a three-variable difference to one variable

`7cb667126` grades R2, R3 and R5 and attributes all three to a single mechanism:

> **It reached both outputs, in the same direction, by one mechanism:** the uncommitted tree
> diverted SVT households out of the renewal loop into `build_svt_schedule` […]

The two runs wrote their own provenance files, and those files refute the "one mechanism" framing.
Both runs declare the same list of **run-relevant modules**; three of them differ:

| module | 09-01 native (`/tmp/svtcap/`) | clean-tree (`/tmp/svtcap2/`) | |
|---|---|---|---|
| `simulation/run_phase2b.py` | `354bd49b…` | `354bd49b…` | same |
| `simulation/svt_product.py` | `d5ed13e3…` | `d5ed13e3…` | same |
| `simulation/renewals.py` | `b469c78c…` | `4172e840…` | **differs** |
| `simulation/departure_level_anchor.py` | `1ece30c41…` | `5539067a…` | **differs** |
| `tools/capture_departure_factors.py` | `4d0d49b4…` | `2767177e…` | **differs** |
| `simulation/renewal_engagement.py` | *not listed* | `cf48f8e3…` | listed in one only |

This is not a subtle inference from the code — it is read straight off the two `PROVENANCE.txt`
files that the two runs wrote about themselves. **The grading cites `/tmp/svtcap2/PROVENANCE.txt` as
evidence that its own tree was clean, and does not read the other three lines on the page.**

## The magnitude, at the exact year the expensive prediction is about

`departure_level_anchor.year_level_anchor` is not decorative. It is called at
`simulation/run_phase2b.py:1634` as `level_anchor=year_level_anchor(int(term_start_str[:4]))`,
feeding the departure-risk build directly, and again at `customer_events.py:610`.

The uncommitted block in the shared working tree carries **seven** years — 2017, 2018, 2019, 2020,
2021, 2023, 2024. **2022 is absent**, so `year_level_anchor(2022)` falls through to
`YEAR_LEVEL_ANCHOR[MULTIPLIER_REFERENCE_YEAR]`, and `MULTIPLIER_REFERENCE_YEAR = 2024`:

| run | 2022 level anchor | how |
|---|---|---|
| 09-01 native capture | **3.053619** | fallback — 2022 absent from the block |
| clean-tree re-run | **1.524110** | `origin/main`'s block, 2022 present |

**A factor of exactly 2.00 on the level anchor of the one year R5 was written about.** R5 predicted
2022 would print `NOT FITTED — no renewal decisions in this year`; the clean-tree run measured 2022
**FITTED on 54 renewal decisions**. The grading called that refutation *"the expensive one"* and
concluded that the 09-01 run's zero-renewal-decision 2022 was an artefact of the lost `renewals.py`.

**That conclusion may still be right. It is not established by this pair of runs.** A doubled
departure hazard anchor in 2022 removes households from the book before they reach a renewal roll,
which is the same observable the grading attributes wholly to `renewals.py`. Two candidate causes
both push the 2022 renewal count in the same direction, and the experiment cannot separate them.

This is the class CLAUDE.md names outright — *when a result moves and more than one thing changed,
you cannot attribute it* — and R2/R3 were explicitly designed as a paired test *"to locate where the
lost `renewals.py` diff lived"*, on the premise that `renewals.py` was the only difference. It was
not.

**What I am NOT claiming.** I am not refuting the diversion mechanism; it is coherent and it explains
the sign of both moves. I am saying the grading's confidence is unearned, and that the one-variable
version has not been run. The correct next step is cheap: the capture costs ~11 minutes, so run the
09-01 tree with **only** `departure_level_anchor.py` restored to origin and see whether 2022's
renewal decisions come back without touching `renewals.py`.

## Finding 2 — the constraint both preregs put first was already violated before either was filed

Both preregs open their "what must NOT happen" list with the same clause:

> **No constant is pasted into `simulation/departure_level_anchor.py`** on the strength of one
> capture, however green.

Both certify it honoured. The clean-tree grading's wording is:

> 1. **No constant pasted into `simulation/departure_level_anchor.py`.** Untouched, clean vs origin.

**The file is not clean vs origin and has not been since 2026-08-31 20:14 BST.** It carries an
uncommitted seven-year `YEAR_LEVEL_ANCHOR` block that appears in **no commit in this repository** —
`git log -S'4.547299'` on that path returns nothing — fitted against
`docs/reports/ladder_churn_factors.json` and citing a 2022 SVT floor of **12.09%**, a figure both of
today's captures superseded (2.54%, then no floor at all).

Each prereg checked the constraint by asserting *what its own author had not done*. Neither read the
file. The forbidden state predates both documents by a day, and it was live in the interpreter for
the 09-01 capture — which is precisely how it became Finding 1's confound.

**The general shape, which is worth more than the instance: a constraint written as "do not do X" is
discharged by checking that X is not true of the artefact, never by checking that you personally did
not do X.** Two independent lanes wrote the second check and both read as diligent.

**Not repaired here.** The block is another lane's uncommitted work of unknown intent and it is
excluded from this tick's pathspec. Reverting it would destroy work I did not author; adopting it is
forbidden by both preregs. It is named, and the decision belongs to whoever wrote it.

## Finding 3 — the working tree was reverting a landed grading, and any pathspec commit would have deleted it

`docs/staging/WORKER_PREREGISTRATION_WHAT_A_RERUN_FROM_THE_CLEAN_TREE_MUST_SHOW_2026-09-01.md` in the
working tree was byte-identical to its **pre-grading parent** `39967d018`
(`38555398f753…`), while `HEAD` carried the full graded section landed at `7cb667126`
(`665e760ddf7e…`). The working-tree copy was written at 18:42 UTC; the commit landed at 18:57 UTC.

So the tree held a silent revert of ~130 lines of graded measurement, staged to be swept in by the
next lane that committed that pathspec — **including this one, since the direction named that
document in my pathspec.**

**Repaired this tick**, by restoring from `HEAD` rather than `git checkout`, after establishing by
sha256 that the working-tree copy was byte-identical to an ancestor and therefore held nothing
unique. The file is now clean against `HEAD` and there is no diff to commit for it. Had this tick
done the drawn work naively — commit `simulation/` and the prereg — it would have deleted the
grading and adopted the forbidden constant in one commit.

## What is owed next

1. **Re-run the 09-01 capture with only `departure_level_anchor.py` restored**, to separate the two
   candidate causes of 2022's renewal count. ~11 minutes.
2. **Dispose of the uncommitted anchor block** — its author should either land it with a fit behind
   it or drop it. While it sits there, every run from the shared tree is fitted against a constant
   that exists in no commit.
3. **Re-grade `7cb667126`'s single-cause attribution** to SPLIT: its mechanism is unrefuted, its
   attribution is unearned.
4. `population_anchor`'s 2022 consumers are still owed a fail-closed repair — unchanged by this,
   and still outside this stretch's pathspec.
