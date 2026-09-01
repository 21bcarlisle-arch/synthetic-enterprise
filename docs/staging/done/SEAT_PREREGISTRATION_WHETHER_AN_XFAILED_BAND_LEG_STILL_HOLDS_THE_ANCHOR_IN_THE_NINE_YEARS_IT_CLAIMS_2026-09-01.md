# PRE-REGISTRATION — does the corrected `_HELD_INDIRECTLY` claim still hold, now that the leg it names is XFAIL?

**Severity:** MEDIUM · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`
A register entry claiming accountability, not a live wrong figure.
**Filed in `done/` because it is graded** — the follow-on (the anchor re-fit) is a separate item.
**Filed:** 2026-09-01, by the delivery seat, BEFORE running the measurement below.
**Subject:** `tests/architecture/test_switching_rate_commons.py::_HELD_INDIRECTLY`,
entry `simulation.departure_level_anchor:YEAR_LEVEL_ANCHOR`.
**Base:** clean `git archive HEAD` stem at `f7714a3566`.

## Why this is being asked

`f97c34eb0` corrected the entry from an unconditional claim to "NINE YEARS OF TEN", naming 2022 as
held by nothing. That correction is right and is mutation-proven below the fold. But it corrects the
claim's **denominator** while leaving the claim's **mechanism** sentence untouched:

> It is held through its EFFECT -- the world's realised departure rate, which is `_PRINCIPAL_SUBJECT`
> above and is band-checked every run.

On the same day, in `f97c34eb0`'s own tree, that band check —
`test_the_worlds_realised_departure_rate_is_inside_the_published_band` — became `xfail(strict)`,
because the world is out of band in 7 of 7 readable years. A strict xfail fires when the leg
unexpectedly PASSES. So it can still see the world coming back INTO the band, which is the loud
signal it was held open to give.

The question it cannot answer by inspection is the other direction: while the world sits outside the
band, does any leg in this file constrain what `YEAR_LEVEL_ANCHOR` actually is? If not, then for the
nine years the entry still claims, the indirection is currently holding nothing either — and the
correction understates its own finding.

This is the catalogued shape one level up from the one just repaired: not *a control over an emptied
subject*, but *a quantity held indirectly through a control whose verdict is held open*.

## The prediction, written before the run

Scaling every `YEAR_LEVEL_ANCHOR` entry by **0.5** — a 2x error in the world's departure level, and
larger than the 1.98x fallback that started this whole thread — will leave
`tests/architecture/test_switching_rate_commons.py` **entirely green: 29 passed, 2 xfailed**, with no
leg firing.

Reasoning: the readings sit BELOW their bands today (the xfail records margins of -1.10 to -15.90pp).
Halving the anchor moves them further below, so the band leg stays "expected fail" and the strict
marker is satisfied. Every other leg in the file is about shape, units, printing, registration or
partition coverage — none carries an independent expectation of the anchor's magnitude.

**If that is what happens, the honest statement is: the indirection named in `_HELD_INDIRECTLY` is
not holding `YEAR_LEVEL_ANCHOR` in ANY year at present — 2022 is the year where it can never hold,
and the other nine are years where it does not hold until the world is back in band.** The entry
should say so, and the leg that restores the holding is the anchor re-fit, not an edit to this file.

**Refuted if:** any leg fires under the 0.5 mutation. That would mean an independent expectation of
the anchor's magnitude exists somewhere in the file and the indirection is live.

**Also recorded, and NOT the same question:** scaling by a factor large enough to push the world back
INTO the band should fire the strict xfail. That direction is expected to work and is not evidence
the indirection holds; it is evidence the marker is doing its "break loudly on repair" job.

---

## GRADED, 2026-09-01, same session — OUTCOME CONFIRMED, MECHANISM MIS-ATTRIBUTED

Kept beside the claim rather than revised, because the mis-attribution is the more useful half.

**The number was exactly right.** Halving every `YEAR_LEVEL_ANCHOR` entry on a clean `git archive
HEAD` stem, run under `python3 -B`: **29 passed, 2 xfailed** — the predicted string, no leg fired. A
2x error in the world's departure level is invisible to the file that exists to hold it.

**The reason I gave was wrong, and the file already said so.** I predicted the halving would pass
*because the band leg is xfail and a halved anchor moves further outside the band*. The actual first
cause is simpler and stronger: **the anchor module is not in the control's read path at all.** The
leg's subject is the stored capture `docs/reports/c2_departure_factors.json`, which carries the
`sim_level_anchor` of the run that produced it, so editing the module moves nothing until
`tools/capture_departure_factors.py` runs again. The holder's own docstring has recorded this since
2026-08-31 — *"this is a drift detector over a stored measurement, not a live assertion about the
module"* — forty lines below the register entry that claims `band-checked every run`.

I should have read the docstring before predicting. That it produced the right number by a wrong
route is the ordinary way a confirmed prediction still misleads, and it is why the mechanism, not
just the outcome, has to be written down in advance.

**So there are TWO defeats of the indirection, not one, and neither is 2022:**

1. **The read path.** Held once per RE-CAPTURE, not once per run. (Not conditional; always true.)
2. **The XFAIL.** Even on re-capture, the verdict is held open, so only the return-into-band
   direction can fire. Any anchor that keeps the world outside passes silently. (Conditional; ends
   when the re-fit lands.)

The second half of the pre-registration — that pushing the world back INTO the band fires the strict
marker — was **not run**, and is recorded as not run rather than assumed. A single global scale
cannot do it (the years need factors from ~1.07 to ~1.41 and the anchor was fitted to band ceilings
on a different capture), so the check needs a per-year construction and belongs with the re-fit.

## What was done about it

`_HELD_INDIRECTLY` now states both defeats, and the disclosure is no longer prose anyone can let rot:
`test_a_register_entry_naming_a_holder_discloses_whether_that_holder_is_holding` fails if the entry
stops disclosing an xfailed holder (MUT-A, fired) **and** fails if the marker comes off and the entry
still claims it (MUT-B, fired). Both mutation-proven under `python3 -B` on a clean stem.

Symmetry is the point: the leg never asserts the holder is broken, so it will not go red on the day
the re-fit repairs it — it goes red if the register lies in either direction.

## What this pre-registration does NOT license

No repair to the band, no re-keying of any leg to today's readings, and no anchor re-fit in this
lane. The result is a statement about a register entry, filed beside it.
