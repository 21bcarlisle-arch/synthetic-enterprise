**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

# FINDING — the 2022 anchor slot is provably INERT, which settles `NO_LEVEL_CORRECTION = 1.0` and simultaneously makes it the one entry no control can ever hold

**Found 2026-09-02, delivery seat, isolated worktree `/var/tmp/se-seat-executor`.** Adopted onto
`d374b1977`, which answered the collision. **This document does not re-answer it and does not
disagree with it.** It supplies one measurement that commit did not make, which closes a worry its
author raised against themselves — and then names the forward hazard the same measurement creates.

---

## 0. First: this lane duplicated `d374b1977`, and the record should say so

Two seats worked the level-anchor collision concurrently from separate worktrees. `d374b1977`
(04:34Z) landed the whole item — the partition, the module change, the guard re-key with a
corroboration leg, the register correction, the graded prereg. This lane landed a pre-registration at
`a314067f2` (04:39Z) and a decision at `604ad4e24`, **both after theirs and neither aware of it**,
having last fetched at the start of the stretch.

**Resolved by ADOPTING, not by merging.** `origin/main` is taken wholesale; this lane's duplicate
`tools/population_anchor.py` and decision document are **discarded**, not reconciled. The superseded
work is preserved at `refs/preserved/seat-executor-level-anchor-2026-09-02` so this account can be
checked. `git status --porcelain tools/population_anchor.py` is empty — their module is byte-identical
and untouched by this commit.

**And their reasoning was better than mine in the place it counted.** I wrote up
`_multiplier_alignment`'s `.get("sim_churn_rate", 0.0)` as a live defect that "manufactured a
direction" and scored GREEN. They **drove** it and established it is an **equivalence** under today's
producer: `_build_churn_by_year` sets the key on every year it emits, and a year absent from
`churn_by_year` never enters `years` at all. I took the more dramatic reading of two available ones
without establishing which was true, which is exactly what *a mutation that does not fire is either a
missing test or an equivalence — establish which* exists to prevent. Their comment says so in the
code. Recorded here because the corrected claim is mine, not theirs.

**This is the catalogued class** *an isolated worktree can duplicate a whole item another lane lands
concurrently*, and the standing remedy — fetch origin before starting **and** before landing — would
have caught it at the second point but not the first. Both lanes were already running when the item
was drawn.

---

## 1. The measurement `d374b1977` did not make

That commit sets 2022's declared value to `NO_LEVEL_CORRECTION = 1.0` and flags the choice against
itself, verbatim from its own pre-registration:

> *"I flag the direction of this one against myself: 1.0 is lower than both 1.524110 (committed) and
> 3.053619 (the borrow), so it removes departures, which is the flattering direction and therefore
> the one to distrust."*

That is the right instinct and the worry is **empirically void**. Pre-registered at `a314067f2` as P2
before the run, with P1 as its null rung:

```
P1  NULL RUNG — sweep YEAR_LEVEL_ANCHOR[2020], renewal route
      anchor= 0.4426 (x0.1 ) -> total departure p = 0.052416649
      anchor= 4.4257 (x1.0 ) -> total departure p = 0.446535225
      anchor=44.2574 (x10.0) -> total departure p = 0.999875000
      monotone: True    span factor = 19.08x

P2  SUBJECT — sweep the 2022 slot, SVT route (every 2022 roll is forced passive)
      anchor=    0.000000 -> 0.140000000000
      anchor=    1.000000 -> 0.140000000000      <- NO_LEVEL_CORRECTION
      anchor=    1.524110 -> 0.140000000000      <- the retired ten-year entry
      anchor=    3.053619 -> 0.140000000000      <- the reference-year borrow
      anchor= 1000.000000 -> 0.140000000000
      max |delta| across sweep = 0.000e+00
```

> **The 2022 slot does not move the world by any amount, at any value, over six orders of
> magnitude — while the same apparatus moves 19.08x on a year where movement is possible.**

So `1.0` is not the flattering choice. It is not a choice with a direction at all: `1.0`,
`1.524110` and `3.053619` produce **bit-identical** worlds. The self-flagged concern can be
discharged, and it should be discharged **on this measurement** rather than on the identity argument
the commit actually gives — "1.0 is the arithmetic form of no calibration" is a good reason to prefer
it, but it is an argument about taste between three values that were never distinguishable.

**And the mechanism says this is permanent, not a property of a capture.**
`renewal_engagement.CRISIS_PASSIVE_YEARS = {"2022"}` forces every 2022 roll passive; C1b routes
passive rolls to the SVT segment table; `departure_risks.py:408` keeps `level_anchor` off the
`svt_inertia` line, deliberately. There is no run, on any population, at any seed, in which the 2022
slot multiplies anything. **No re-capture can change this**, which is a stronger statement than the
capture-scoped "zero renewal decisions in the `c2`/`ladder`/native family" — and stronger than the
SVT-floor argument too, which establishes that no anchor *reaches the record*, not that no anchor
*changes anything*.

---

## 2. The hazard the same measurement creates, which is the actual finding

An inert slot cannot be got wrong today. It also **cannot be held by anything, ever**, and it is
sitting in a table whose other seven entries are all fitted, validated and drift-detected.

`_HELD_INDIRECTLY` already says 2022 is held by **nothing**. What it does not say — because until now
nobody had measured it — is that **no control can be written that would hold it**, because a control
must be able to fail and there is no input to this slot that changes any output. The band leg cannot
see it. The corroboration leg added at `d374b1977` checks that the *declaration* is honest, which is
the right thing and a real control, but it grades the **sentence**, not the **number**.

**So the forward hazard is a change elsewhere silently making the number load-bearing:**

1. any change putting `level_anchor` onto the `svt_inertia` line in `build_departure_risks`;
2. any change removing `"2022"` from `CRISIS_PASSIVE_YEARS`;
3. any change to C1b's routing of passive rolls.

Each is a legitimate fidelity change someone may well make. On the day any of them lands, `1.0`
stops being inert and starts setting the crisis year's departure level — **and every control in the
tree stays green**, because none of them was ever able to fire on this value. The number would be
read as a fitted entry by anyone reading the table, since it sits in `YEAR_LEVEL_ANCHOR`'s
neighbourhood and carries six decimals of company.

This is the shape *a control keyed to today's answer* inverted: not a control that goes red when the
code becomes more honest, but **a value that no control can go red about, in a table where every
neighbour is held.**

## What I did NOT build, and why

**No control, and no register entry.** The honest mechanism here is a coupling test — "if
`level_anchor` ever reaches `svt_inertia`, or 2022 leaves `CRISIS_PASSIVE_YEARS`, then the 2022 slot
must be re-fitted or re-declared". That is buildable. It is also *a control that only guards our own
controls*, on a hazard with no current instance, and CLAUDE.md is explicit that such a thing is
usually not worth having. **Filed rather than built**, per the standing rule, with the three trigger
conditions named above so the next lane touching any of them can find this by grep on
`CRISIS_PASSIVE_YEARS`.

**I did not touch `simulation/departure_level_anchor.py`.** `d374b1977`'s answer stands; nothing here
contradicts it, and the one thing this measurement changes is *which argument* discharges the
self-flagged direction worry.

---

## 3. A second constraint on re-founding the table, measured and not previously recorded

`d374b1977` retires the ten-year block as un-re-citable — `b46318106` overwrote its fit input in
place. Correct. **There is a live temptation it does not close.**

| capture | n | 2016 | 2022 | 2025 | all ten years? | post-C1b? |
|---|---|---|---|---|---|---|
| `c3_shown_price_departure_factors.json` | 459 | 3 | **53** | 35 | **YES** | **NO** |
| `c2_departure_factors.json` | 148 | 1 | 0 | 16 | no | yes |
| `ladder_churn_factors.json` | 144 | 1 | 0 | 15 | no | yes |

**c3 is the only capture on disk covering all ten record years**, and it is the obvious thing to
reach for when someone wants the ten-year block back. **It must not be used.** Measured: its 53 rows
in 2022 carry `departure_cause` in `{dissatisfaction, bill_shock, price_position}` and **none** in
`svt_inertia`, with `sim_level_anchor` uniformly `1.52411`. It is a **pre-C1b, renewal-route-only**
capture. Fitting on it would anchor a whole-population published rate onto the households that
demonstrably shop — the exact selected-sub-population defect the account-years denominator was built
to remove — and would produce a *followable citation for a known-wrong denominator*, which is worse
than the unfollowable one being retired, because it would look repaired.

> **Neither table is founded yet, and the constraint is now two-sided: the only ten-year capture is
> disqualified by its denominator, and the only correctly-denominated captures are thin at the window
> edges (2016: 1 row; 2025: 15–16) and empty at 2022 forever.** Discharge is a post-C1b re-capture
> deep enough to carry 2016 and 2025 — not a re-fit on anything currently on disk.

---

## 4. What landed with this document

**Controls for `d374b1977`'s fail-closed 2022 reads, which landed without any.** That commit gated
green on 455 tests, but `tests/tools/test_population_anchor.py` is untouched by it and contains no
reference to `2022_unavailable_reason` or `rag: "UNAVAILABLE"` — **both new branches were green by
never being driven.** Three legs added, mutation-proven under `python3 -B` against their
implementation, which is byte-identical and unmodified:

```
MUT 1  restore .get("sim_churn_rate", 0.0)   -> test_an_absent_2022_..._measured_zero      FAILED
                                                test_a_present_2022_still_reads_...        passed
MUT 2  restore the , 0.0 defaults            -> test_a_transition_..._not_scored_green     FAILED
restored (git status on their module: empty) -> 26 passed
```

The pass-branch leg is deliberate: without it the refusal leg could be a constant verdict, and a
fail-closed repair that bought its safety by severing the check would read identically.

The third leg covers the site their commit correctly calls an **equivalence** rather than a defect.
It is tested anyway, and its docstring says why: an equivalence is exactly what rots silently: the
day a producer starts emitting a year without the key is the day an undriven guard is discovered to
have been deleted.

**Also landed: this lane's pre-registration**, restored from the preserved ref. It was filed at
`a314067f2`, **04:39:11Z**, before any of the measurements above ran and before their output was
read. Its P1 is a **kept miss** — I predicted ≥20x and measured 19.08x, having assumed a near-linear
response on a quantity `_clip_hazard` saturates at the top of the sweep. The stated refutation
condition (<2x, or non-monotone) was not met, so the null rung stands and P2 is readable; the point
prediction was still wrong and is kept beside the result.
