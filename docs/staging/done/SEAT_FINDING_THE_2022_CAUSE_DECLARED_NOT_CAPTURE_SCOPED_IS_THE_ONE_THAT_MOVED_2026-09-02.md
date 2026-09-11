**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

# FINDING — 2022's two declared causes were separated by scope, and the one declared NOT capture-scoped is the one that moved when the capture changed

**Found 2026-09-02, delivery seat, Lane 0, on a whole-book re-capture run from a clean
`git archive HEAD` stem of `19e68169b` with every producer committed.** Pre-registered at
`docs/staging/SEAT_PREREGISTRATION_WHAT_A_WHOLE_BOOK_RECAPTURE_MUST_MOVE_2026-09-02.md`, landed at
`f753f6252` **before the capture ran**; graded there beside its own filed text, misses kept.

The capture is committed as an artefact under its own name, `docs/reports/c4_whole_book_departure_factors.json`
(sha256 `bd6ad1da…`) and its SVT sibling (sha256 `c2db315c…`). It is **not** an overwrite of any
existing capture: overwriting a committed capture in place under a stable path is `b46318106`, the
commit that made the retired ten-year block's provenance unfollowable.

---

## What was declared

`simulation/departure_level_anchor.UNFITTED_YEARS[2022]` gives two causes, and **separates them by
scope on purpose** — the separation is the entry's whole point, restated in
`docs/design/THE_LEVEL_ANCHOR_COLLISION_ANSWERED_2026-09-02.md` and in the drawn direction:

> (i) … the `c2`/`ladder`/native capture family therefore carries ZERO 2022 renewal decisions …
> **THAT REASON IS CAPTURE-SCOPED**…
> (ii) **The reason that is NOT capture-scoped**: its SVT floor is 12.09% against a published 4.30%
> ceiling, and `build_departure_risks` deliberately does not scale `svt_inertia`, so **NO anchor >= 0
> brings 2022 to the record.**

Cause (ii) is the one carrying the weight. The collision document calls it *"the one that binds"*.
It is why 2022 is declared unidentified rather than merely unfitted, and why the entry says *"not a
gap a re-fit closes"*.

## What the fresh capture measures

Both figures below are `departure_population.union_by_year`'s `expected_rate_pct` for 2022 — the same
function, the same denominator (**55 accounts in both**), read from two captures:

| capture | era | 2022 decisions | 2022 `expected_rate_pct` |
|---|---|---|---|
| `ladder_churn_factors.json` | retired **ten-year** block | 198 SVT, 0 renewal | **12.80%** |
| `c4_whole_book_departure_factors.json` | live **seven-year** block, clean HEAD | 213 SVT, 0 renewal | **2.54%** |

Published 2022 band: **2.9–4.3%**.

**Cause (i) reproduces — 2022 still carries zero renewal decisions.** That half stands, and it was
the half declared capture-scoped.

**Cause (ii) does not reproduce.** The ~12% floor is a property of the `ladder`-era capture, not of
the mechanism. On the current world 2022's whole-book expected departure rate is **2.54%** — and the
direction of the miss is **reversed**: 2022 is now **below its band's floor**, not above its ceiling.

## Why this matters more than a stale number

The declared conclusion — *"NO anchor >= 0 brings 2022 to the record"* — was true because the floor
sat 7.8pp **above** the published ceiling. At 2.54% against a 2.9% floor, **an anchor greater than 1
would raise 2022 into its band.** The claim that 2022 has no lever is not merely unsupported by the
current capture; the current capture points the other way.

That does **not** mean 2022 should now be fitted. It means the entry rests on a figure this world
does not produce, and the standing conclusion built on it needs re-establishing rather than
re-citing. This is the catalogued shape *a measurement that a hole is open goes stale exactly like
one that it is closed* — the ~12% floor has been carried forward, unre-measured, through the
correction, the collision document and the drawn direction alike, each in good faith.

**The scope labels are exactly inverted against what the artefacts show.** The cause declared
capture-scoped survived a capture change; the cause declared capture-independent did not.

## An open question this raises and does not answer

`build_departure_risks` deliberately does not scale `svt_inertia`, so the level anchor should not
reach the SVT route at all. Yet the SVT route's rate moved on **every** year between the two
captures, and 2022 moved most (12.80% → 2.54%, ~5x, against 2023's 12.66% → 7.02% and 2019's
16.76% → 15.81%). An indirect path is plausible — the anchor scales the renewal route, which changes
who remains on the book, which changes the SVT population — but 2022's magnitude is an outlier
against every other year and I have **not** established the mechanism. Filed as a question, not
answered, and it should not be assumed benign.

## The other result, which belongs on the surface rather than in a footnote

Three documents state that the anchor is band-held in no year and that the discharge is a
re-capture. **The re-capture has now run, and it does not discharge the band leg on either column.**

| yr | renewal-decision % | whole-book % | band | book in band? |
|---|---|---|---|---|
| 2017 | 15.30 | 11.09 | 13.5–14.0 | OUT |
| 2018 | 22.97 | 18.97 | 19.5–20.0 | OUT |
| 2019 | 26.98 | 20.48 | 20.7–21.3 | OUT |
| 2020 | 40.32 | 24.62 | 22.5–23.0 | OUT (above) |
| 2021 | 21.74 | 16.96 | 17.9–18.4 | OUT |
| 2022 | — | 2.54 | 2.9–4.3 | OUT |
| 2023 | 2.90 | 7.92 | 8.9–12.5 | OUT |
| 2024 | 22.87 | 13.84 | 12.5–16.1 | **IN** |

**"We cannot tell yet" has become "we can now tell, and the answer is no."** The live seven-year
block puts the world inside its published band in **one year of eight** on the record's own
denominator. Six years sit below their band and one above. That is a re-fit's subject — and a re-fit
is now possible for the first time, because the whole-book column is readable for the first time.

**The denominator argument I filed in advance is refuted and I am keeping the miss.** I predicted
(P3) that the whole-book rate would exceed the renewal-decision rate, on the reasoning that the union
adds SVT departures to the numerator. It is **lower in 6 of 7** years. The union adds 1,373 SVT
decisions carrying 38 departures — a far *lower* departure rate than the renewal route's 36 over 156
— so the SVT route dilutes the book rate rather than lifting it. Switching the band control's subject
to the whole-book column would therefore **not** have discharged the leg either, which is the
conclusion I had registered as following if P6 held. P6 held; the consequence I attached to it does
not.

## What I did NOT do

1. **No value in `YEAR_LEVEL_ANCHOR` or `UNFITTED_YEARS` added, edited or deleted.** 2022's entry
   still says what it says. A finding against a declaration is not a licence to rewrite it in the
   same stretch that found it, and the re-fit this points to is a separate decision on evidence.
2. **No band widened, no `xfail` marker removed, narrowed, or re-keyed.** Both strict markers stand.
3. **No committed capture overwritten.** The new capture has its own name.
4. **2022 not fitted, not clamped, not interpolated.**

## What is owed next

1. **Re-establish or retire 2022's cause (ii).** Either measure the SVT floor on the current world
   and re-state the entry with the figure and the capture it came from, or withdraw the "no lever"
   conclusion. It must not be re-cited at ~12%.
2. **Re-fit `YEAR_LEVEL_ANCHOR` on the c4 capture's whole-book column**, which is the first time the
   account-years quantity the block claims to be fitted on has been readable in the same artefact the
   band is judged from. Then re-capture, per the block's own capture → fit → capture iteration.
3. **Establish why the SVT route moved between captures** when the anchor is declared not to scale it.

---

# CORRECTION 2026-09-02, same seat, on merging with `origin/main` at `35750ea46`

*Kept above rather than revised. The measurement stands and was reached independently; the
attribution above is incomplete, and a sibling lane got to the same void first by a different route.*

## A sibling lane found the same inversion, earlier, and by a better route

`fe11e3703` — *"the binding half of 2022's refusal was voided by a term that landed the day before"* —
landed while my capture was running. It reaches the same conclusion and **attributes it, which the
finding above does not**: on 2026-09-01 `c628cb37d` gave `svt_inertia_hazard` a required
`market_switching_multiplier`, and re-driving stored rows through the new hazard drops the floor.

**That is the better route, and I record it as better.** Mine measures a *fresh run* and so cannot
separate "the mechanism changed" from "the population changed"; theirs re-drives the *same rows*
through the new hazard, holding the population fixed, and therefore isolates the cause. My open
question above — *"why did the SVT route move when the anchor is declared not to scale it"* — is
answered by their finding: it was not the anchor, it was the market term entering the hazard.

The two measurements corroborate each other across independent routes: **2.54%** (fresh capture) and
**2.33%** (retired `ladder` pair re-driven). Both are far below the 12.09% carried forward, and both
put 2022 **below** its 2.9–4.3% band. The substantive conclusion is robust to which route you take.

## But their control was RED AT CLEAN HEAD from the instant it landed, and it wedged every lane

`test_every_declared_svt_floor_reproduces_under_the_hazard_the_world_actually_runs` read
`svt_sibling(instrument.DEFAULT_TABLE)` — the SVT sibling of `c2_departure_factors.json`. **That file
is in no commit and never has been**: the run that produced `c2` carried no SVT recorder. Measured,
not inferred:

```
$ git archive origin/main | tar -x -C /tmp/omcheck     # clean extract of 35750ea46
$ cd /tmp/omcheck && python3 -B -m pytest tests/architecture/test_switching_rate_commons.py -q -k svt_floor
E  FileNotFoundError: '/tmp/omcheck/docs/reports/c2_departure_factors_svt_segment_decisions.json'
1 failed, 36 deselected
```

This is the catalogued *green at HEAD and red in the shared tree from the instant it lands* — the
**same class this whole thread opened on**, one file over, and running the same way round. The
authoring worktree held an untracked sibling. Re-driving the `ladder` sibling reproduces their stated
**2.34%** to three decimals (2.331%), which identifies what the untracked file was.

**Every lane whose commit selects this test file was wedged on a red it did not cause.**

## What I did about it, and why it was mine to do

I hold the artefact that repairs it: `c4_whole_book_departure_factors.json` and its sibling are the
first capture pair on disk describing **one run with every producer committed**. So the repair landed
in this commit:

* `_FLOOR_CAPTURE` points the floor leg at the c4 pair, with the reasoning recorded at the constant.
  The band leg is deliberately **left** on `DEFAULT_TABLE` — moving a control's subject inside the
  commit that repairs a *different* control is how a moved number becomes unattributable.
* Pairing `c2`'s renewal rows with a foreign sibling was considered and **rejected**:
  `capture_departure_factors`'s own docstring forbids differencing a cell across two runs, and the
  account denominator is exactly such a cell.
* A named assertion replaces the bare `read_text()`, so a missing sibling fails **on its subject**
  instead of on a `FileNotFoundError`.
* The declared figure moves `2.34% → 2.54%` to match the capture the leg now re-drives, beside its
  superseded text, exactly as the leg's own failure message instructs. Their entry's claim that the
  figure came from *"the committed capture"* is corrected: it did not.

**Mutation-proven under `python3 -B` on a throwaway stem, both sides:**
- restore `2.34%` → fires on the value (`states an SVT floor of 2.34% … give 2.54%`);
- point `_FLOOR_CAPTURE` back at `c2` → fires on the **named** sibling assertion, not a
  `FileNotFoundError`;
- unmutated → green. The pass branch is reachable and the verdict is not constant.

## What this does NOT do

It does not fit 2022, widen a band, or touch either `xfail`. And it does not make the anchor
band-verified: **one year of eight** remains the reading, and the re-fit named in "what is owed"
below is still owed.
