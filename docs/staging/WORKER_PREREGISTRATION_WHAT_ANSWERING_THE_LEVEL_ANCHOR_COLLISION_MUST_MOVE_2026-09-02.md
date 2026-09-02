**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

# PRE-REGISTRATION — what answering the level-anchor collision must MOVE

**Filed 2026-09-02, delivery seat, BEFORE any run and before reading any run's output.** Written
after reading `docs/design/UNLANDED_WHOLE_BOOK_LEVEL_ANCHOR_BLOCK_2026-09-01.md`, the finding and
its correction, and the live code — and after **re-measuring the capture provenance independently**
(below), because a correction taken on trust is not evidence.

Every prediction below names the MOVE, with the number it moves from and to. Predictions are graded
beside their filed text in this file, misses kept.

---

## Established BEFORE the predictions, by measurement, not by citation

I re-derived the block ordering from the `sim_level_anchor` column rather than from the correction
that asserts it. `python3` over every capture on disk carrying that column:

| artefact | mtime | `sim_level_anchor` | ⇒ ran under |
|---|---|---|---|
| `ladder_churn_factors_svt_segment_decisions.json` | 08-31 16:44 | ten-year values in all 10 years | **ten-year** |
| `c2_departure_factors_svt_segment_decisions.json` | 08-31 20:54 | seven-year values; **2016, 2022, 2025 all `3.053619`** | **seven-year** |

`3.053619` is the seven-year block's 2024 entry and `MULTIPLIER_REFERENCE_YEAR` is 2024, so those
three years reading it is the reference-year fallback firing under a block that omits them. That is
the seven-year block's signature and nothing else produces it. **The correction is confirmed: the
tree's seven-year block is HEAD's SUCCESSOR, not its predecessor.**

Renewal rows per year, counted independently:

| capture | n | 2016 | 2022 | 2025 |
|---|---|---|---|---|
| `c2_departure_factors.json` | 148 | 1 | **absent** | 16 |
| `ladder_churn_factors.json` | 144 | 1 | **absent** | 15 |
| `c3_shown_price_departure_factors.json` | 459 | 3 | **53** | 35 |

**Capture scope, stated as the direction requires:** "2022 has zero renewal decisions" is true of the
`c2`/`ladder`/native family and **false** of `c3`. It is a property of that capture family, not of
the world. The SVT-floor reason (12.09% against a published 4.30% ceiling, with
`build_departure_risks` deliberately not scaling `svt_inertia`) is the one that binds independently
of which capture is in front of you.

---

## The decision this registers, stated before it is run

**The question as posed — refuse or fall back — has a false premise, and the premise is the same
defect the guard at `9fd700366` was built to fix, one set over.**

That guard replaced the fallback's condition "absent from the FITTED TABLE" with "absent from the
PUBLISHED RECORD", and its own docstring names the class: *the condition and the justification were
two different sets*. But the fit's declared scope is **neither**. It is
`tools.measure_departure_level.COMPARISON_YEARS = range(2017, 2025)`. **Three sets, not two** — fitted
table, published record (2016–2025), comparison window (2017–2024) — and the guard picked the second
when the fit is scoped by the third.

So the three absences are answered separately, as the direction requires:

* **2016 and 2025 FALL BACK, and the guard is what is wrong, not the fit.** They are outside the
  declared comparison window, excluded there for a stated and corroborable reason (2016 carries 1–3
  renewals, 2025 is partial — re-counted above). A fit that never claimed them is not failing to
  identify them. The reference-year fallback's existing justification holds for them unchanged.
* **2022 REFUSES — but the refusal belongs to the FIT and the SURFACE, not to the accessor's control
  flow.** Refusing in the accessor crashes `run_phase2b` on three hot-path call sites; falling back
  silently is the catalogued 1.98x defect. **Neither is the answer: the answer is a PARTITION**, the
  shape `realised_rate_coverage` already uses one file over. A comparison year is *fitted*, or
  *unfitted with a declared cause the artefact corroborates*. An unfitted comparison year with **no**
  declared cause still raises — the guard survives and can still fire.
* **2022's fallback is NOT the reference year's value.** HEAD's own committed docstring already
  establishes that borrow is wrong here: 1.98x, on the record's lowest year, in the direction that
  ADDS departures. The declared value is **1.0 — no level correction applied** — the identity of the
  parameter and `build_departure_risks`'s own default, which is the arithmetic form of "no
  calibration is identified" rather than a calibration borrowed from another year's population.

**I flag the direction of this one against myself:** 1.0 is *lower* than both 1.524110 (committed)
and 3.053619 (the borrow), so it removes departures, which is the flattering direction and therefore
the one to distrust. The defence is that 2022's whole-book floor is already ~12.09% against a 4.30%
published ceiling, so the year is ~2.8x **above** the record before the anchor touches it; and that
the reason for 1.0 is that it is the identity, not that it moves toward the record. If a reader
thinks that defence fails, the entry is one line and it is declared, not buried.

---

## Predictions

### P1 — the crash is real, and it is 2016 and 2025, not 2022
Composing HEAD's guard with the seven-year block, **`year_level_anchor(2016)` and `(2025)` raise
`ValueError` and `(2022)` also raises**; 2024 returns `3.053619`. If any of the three does NOT raise,
the collision as described does not exist and everything below is void.

### P2 — after the re-key, the accessor is TOTAL over the record and nothing raises
`year_level_anchor(y)` returns a float for **all ten** years 2016–2025, and for a synthetic year
(2030). **Predicted values, from → to:**

| year | HEAD (ten-year) | after | ratio | why |
|---|---|---|---|---|
| 2016 | 4.597312 | **3.053619** | 0.664 | outside window → reference-year fallback |
| 2017 | 4.256902 | **4.547299** | 1.068 | whole-book fit |
| 2018 | 3.345826 | **2.882178** | 0.861 | whole-book fit |
| 2019 | 3.228064 | **4.803900** | 1.488 | whole-book fit |
| 2020 | 4.425742 | **6.412007** | 1.449 | whole-book fit |
| 2021 | 3.219914 | **4.488202** | 1.394 | whole-book fit |
| 2022 | 1.524110 | **1.000000** | 0.656 | declared unidentified → no correction |
| 2023 | 2.091517 | **0.364038** | 0.174 | whole-book fit |
| 2024 | 3.020806 | **3.053619** | 1.011 | whole-book fit |
| 2025 | 2.118624 | **3.053619** | 1.441 | outside window → reference-year fallback |

Seven of ten move by more than 6%; 2023 moves by 5.7x downward and 2020 by 1.45x upward. **If the
table comes out identical to HEAD's anywhere except 2024 (which moves 1.011), the block did not
land.**

### P3 — the guard survives and can still fire, and it cannot be lifted by naming
Two mutations, both under `python3 -B`:
* **(a) THE GUARD.** Delete 2020 from `YEAR_LEVEL_ANCHOR` **and** from the declared unfitted causes →
  `year_level_anchor(2020)` **raises**, naming 2020 and the comparison window.
* **(b) THE CORROBORATION, which is the leg that matters.** Delete 2020 from `YEAR_LEVEL_ANCHOR` and
  **declare it unfitted with a cause** → the control must **still go red**, because 2020 is inside the
  window, is not crisis-forced-passive, and the capture carries 17–18 renewal decisions for it. If
  (b) passes, the fit lane can retire any inconvenient year by naming it, which is the catalogued
  *refusal names a cause the checker never observed*, and the whole partition is theatre.

### P4 — the band leg does NOT move, and that is a claim about the read path
`test_the_worlds_realised_departure_rate_is_inside_the_published_band` stays `xfail(strict)` and does
**not** turn green. Its subject is the STORED capture, whose `sim_level_anchor` column is fixed at the
seven-year values already; the module is not in its read path. **The anchor reaches that control only
through a re-capture.** If it flips to XPASS, my account of the read path is wrong and P4 is refuted.

### P5 — `population_anchor`'s published measured zero moves to a named absence
`tools/population_anchor.py:490` resolves `yr2022.get("sim_churn_rate", 0.0)` on a capture with no
2022, publishing `2022_sim_rate_pct: 0.0` and `2022_ratio_vs_ofgem: 0.0` — a measured zero for the
crisis year. After the repair the field is **`None` with a named reason**, `insufficient_data`
becomes **True**, and `absolute_divergence_flag` becomes **False for a stated cause rather than by
arithmetic on a fabricated zero**. Predicted move: `0.0 → None` on `2022_sim_rate_pct`.

### P6 — the disclosure handshake fires, and correcting it is not re-keying
`4871e53ee`'s handshake is armed: `_HELD_INDIRECTLY` asserts things about the anchor that landing a
fit changes. **Predicted: at least one register/disclosure leg in
`tests/architecture/test_switching_rate_commons.py` goes RED on this commit**, and the repair is to
correct the register's text to match the new table — never to re-key the leg to today's readings and
never to assert the holder stays broken.

---

## Constraints, to be discharged by READING THE ARTEFACT and not by recalling my own behaviour

1. **No year is added to `YEAR_LEVEL_ANCHOR` that `fit_year_anchor_on_book` did not emit.** Discharged
   by pasting `git diff -U0` filtered to the block.
2. **The published band is not widened and 2022 is not clamped or interpolated.** Discharged by
   pasting `git status --porcelain docs/domain_artefact_library/`.
3. **No `--no-verify`, no `git checkout <path>`, no `git stash`.** Discharged by pasting the commit's
   provenance.

---

# GRADING — filled in after the runs, beside the filed text above

**Graded 2026-09-02, same tick, after the runs. 4 CONFIRMED, 1 CONFIRMED WITH A MISS ON THE
MECHANISM, 1 SPLIT. Misses kept.**

### P1 — CONFIRMED, exactly
Composing HEAD's guard with the seven-year block, in-process under `python3 -B`:
```
2016 -> ValueError: no fitted level anchor for 2016, which is INSIDE the published switchi...
2022 -> ValueError: ...
2025 -> ValueError: ...
2024 -> 3.053619       2030 -> 3.053619
```
All three predicted years raise; both predicted returns return. The collision is real.

### P2 — CONFIRMED, all ten rows to six decimals
Every predicted value matched the measured one exactly, including both fallback cases and the 5.7x
downward move on 2023. `anchor_coverage()` returns `fitted=[2017,2018,2019,2020,2021,2023,2024]`,
`unfitted=[2016,2022,2025]`, and 2030 still returns the reference year's `3.053619`.

### P3 — CONFIRMED on both mutations, with a MISS on which leg catches (a)
Both fire under `python3 -B`; the fixture restores and the control returns green.
* **(a)** fires — but at **leg (b), the partition**, not at leg (c)'s `pytest.raises` as I implied.
  Removing 2020 from the fit without declaring it puts it in *neither* side of the partition, and
  that assertion runs first. **The red is true and for a true reason** — the year left the subject
  silently — but I predicted the raise would be what reported, and it is not. Leg (c) is still
  driven on every green run (victim 2023, 8.39x), so the raise is not untested; it is just not what
  speaks first. Recorded rather than smoothed over: I predicted the message, not only the verdict.
* **(b)** fires at the corroboration leg, which is the whole point — declaring 2020 unfitted with a
  plausible sentence suppresses leg (c)'s raise entirely and the control **still** goes red, because
  2020 is inside the window and is not in `CRISIS_PASSIVE_YEARS`. The escape cannot be opened by
  naming.

### P4 — CONFIRMED, and it is the load-bearing negative
`tests/architecture/test_switching_rate_commons.py` reports **`2 xfailed`** after the block landed:
the band leg did not flip to XPASS. The anchor module is not in its read path — it reads the stored
capture — so **this commit moves no band verdict, and the live block's band performance is untested.**
That is on the register and in the decision document, not in a footnote.

### P5 — CONFIRMED, `0.0 → None`, and no collateral damage
Before: `2022_sim_rate_pct: 0.0`, `2022_ratio_vs_ofgem: 0.0`, `insufficient_data: False` — a measured
zero for the crisis year, with the divergence check reading GREEN on a year it never observed.
After: `None`, `None`, `insufficient_data: True`, plus a named `2022_unavailable_reason`. The
still-measurable case is unchanged and still fires (2022 at 30% → ratio 8.3, `absolute_divergence_flag:
True`), so the repair did not buy its fail-closed by severing the check.

### P6 — SPLIT, and the half I got wrong is the more interesting one
* **Confirmed:** a register leg went RED on this commit —
  `test_every_discovered_switching_level_candidate_is_registered_or_classified`, naming
  `FIT_COMPARISON_WINDOW`, `UNFITTED_YEARS` and `_unfitted_anchor`.
* **MISS:** I predicted the handshake would fire because *landing a fit* changes what the register
  asserts. It fired for a different reason — the discovery scanner found three **new symbols** that
  no register held. The disclosure legs proper
  (`test_a_register_entry_naming_a_holder_discloses_whether_that_holder_is_holding` and the read-path
  leg) **stayed green throughout**, because the band leg remained xfail and the read path did not
  move, so the entries' existing disclosures were still accurate. My model of *which* mechanism was
  armed was wrong; the mechanism that actually caught the change was a scanner I had not predicted at
  all. The register was corrected either way — nine-of-ten → seven-of-ten, the 2022 entry kept in the
  past tense beside what replaced it — and neither leg was re-keyed to today's readings.

### An unpredicted finding, filed because nothing predicted it
`tools/population_anchor.py`'s **second** `.get("sim_churn_rate", 0.0)` site, in
`_multiplier_alignment`, looks like the same defect and **is not one**. Driven rather than inferred: a
year absent from `churn_by_year` never enters `years`, so it produces no transition and the default
was unreachable that way; it is reachable only for a year present with the key missing, which
`_build_churn_by_year` never emits. It is an **equivalence** under today's producer. The fail-closed
guard was kept as a guard against a future producer and the comment now says so, because the first
draft of that comment asserted a live defect that does not exist — "it looked like the one next to
it" is how a defensive edit gets written up as a fix.

### Constraints, discharged by reading the artefact
1. **No year added that the fit did not emit.** `git diff -U0` on the block shows the ten-year table
   deleted and the seven-year table added verbatim from
   `UNLANDED_WHOLE_BOOK_LEVEL_ANCHOR_BLOCK_2026-09-01.md`; no year line was authored here. The one
   value that is *not* from the fit is `NO_LEVEL_CORRECTION = 1.0`, which is declared as the
   parameter's identity, is named in the decision document, and is not an entry in
   `YEAR_LEVEL_ANCHOR`.
2. **Band not widened, 2022 not clamped or interpolated.**
   `git status --porcelain docs/domain_artefact_library/` → empty.
3. **No `--no-verify`, no `git checkout <path>`, no `git stash`.** None run this tick; the block was
   taken from the committed design document, not from a checkout.
