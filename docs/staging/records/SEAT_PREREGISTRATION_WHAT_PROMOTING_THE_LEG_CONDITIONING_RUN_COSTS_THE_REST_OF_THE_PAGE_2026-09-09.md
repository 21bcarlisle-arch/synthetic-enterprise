**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — grade the per-leg conditioning pre-registration) · **Class:** measurements_that_mirror

# PRE-REGISTRATION — what promoting the leg-conditioning run costs the rest of the page

Filed at 12:45Z on 2026-09-09, **while the run is still executing** (unit
`longjob-three-arm-legcond-20260909b`, launched 12:38:48Z) and therefore before its artefact
exists. It is a second, separate question from
`SEAT_PREREGISTRATION_WHICH_OF_THE_FOUR_BRIDGE_LEGS_ADMIT_THE_DEPARTURES_2026-09-09.md`, whose
P1–P6 are about what `_leg_conditioning` measures. **This one is about what publishing it does to
every other figure on the page**, which is a different funnel and has to be asked separately or
the promotion gets graded on the block it was run for.

## Why it is asked at all

The page's figures come from `THREE_ARM_PATH` (`value_cycle_ab_s1_three_arm.json`) and its bound
from `NOISE_FLOOR_PATH` (`..._noise_floor.json`). They are a **pair**: the canonical constants'
own comment says moving either alone is the defect the pair exists to prevent. Filling the
"Departures this cut can see" column needs a NEW three-arm run and there is no new floor to move
with it — the nine-seed floor another lane launched (`longjob-noise-floor-20260909b`, PID 704091)
is hours from finishing. So the promotion is deliberately half a pair move, and what that costs is
the question.

## What is already established without measuring

Not predictions — checked in git before this file was written, and stated so they are not later
mistaken for findings:

- The 09-09 canonical run's `producing_commit` is `62334dc76`. `git diff 62334dc76 8b846013e --
  simulation/ company/ saas/ sim/` is **empty**, and the only change to
  `tools/run_value_cycle_ab.py` that is not an addition is a three-line hoist of
  `account, term = entry.get(...)` above the `signal_not_a_number` gate. So the world and the book
  the re-run measures are the same ones.
- `error_bar.staleness_caveat` on the live feed is `None` today: floor 06:57:00Z ≥ three-arm
  01:24:34Z.

## The predictions

- **Q1** — every figure the page already publishes reproduces **bit-identically** in the new run:
  the four leg concordances (0.5337857142857143, and the three below it), their intervals, `n` of
  168/124/124/161, `survivorship`'s 40/40/0/0, and `world_identity.digest` `39a192ce04c1eda8`. The
  re-run is the same code on the same world at the same seed apart from an additive block, so a
  difference anywhere is a **defect in the addition**, not news about the book.
- **Q2** — `error_bar.staleness_caveat` flips from `None` to the "THE ERROR BAR IS OLDER THAN THE
  FIGURE IT BOUNDS" sentence, because the promoted point estimate will be stamped later than the
  06:57:00Z floor. This is the cost of the half-pair move and I expect to pay it.
- **Q3** — **that sentence will be false in its causal clause.** It asserts, unconditionally,
  *"and something did, on 2026-08-28: the market gained the ability to DEFEND"*. Nothing changed
  between a floor of 2026-09-09T06:57Z and a three-arm run of 2026-09-09T~14:00Z — same digest,
  and the git diff above is empty. So the ordering test is right and fires correctly, and the
  prose it fires with names an event outside the interval it is describing. **If Q3 holds it is a
  finding and the promotion must not land until the sentence is composed from the two artefacts
  rather than typed.** I am recording it before I see the rendered page so that "I noticed on the
  way past" cannot be claimed afterwards.
- **Q4 — will not move** — `world_provenance.one_world_across_every_figure` stays `true` and
  `runs_measured_in_a_superseded_world` stays empty. Independent of Q2/Q3: that block is keyed to
  the digest and the digests are equal, whereas the caveat is keyed to the stamps and the stamps
  are not. Two different properties, and this is the one I claim is untouched.
- **Q5 — least sure** — a whole-feed sweep of every `.available` flag and every
  `_low`/`_high`/`sem_gbp`/`stdev_gbp` against the pre-promotion feed finds **0 bounds lost**. The
  same sweep shape that graded P4 of the 09-09 promotion. Least sure because the generator reads
  the three-arm artefact in more places than the four legs, and a stamp change is an input to more
  than the caveat.

## The declared limit, before the answer

Whatever Q1 returns, this promotion buys **one column and no new knowledge about the book**. The
numbers are the 09-09 numbers; what is new is that the page can say which of the four cuts is
computed over households that stayed. A result document claiming this run moved a figure would be
claiming an addition changed a measurement, which is exactly the defect Q1 exists to detect.
