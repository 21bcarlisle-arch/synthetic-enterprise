**Severity:** MEDIUM · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`
**Class:** `controls_that_cannot_fail` — born archived, per the class protocol.

# A register claiming indirect cover cannot see its own holder being xfailed

Filed by the delivery seat, 2026-09-01, while **verifying** the Lane 0 item
*"the only control holding the level anchor is red and reports a constant pass"*. The drawn repair
was already landed at HEAD (`f97c34eb0`); this is what verifying it turned up.

## First: the drawn item was done, and it was done well

The brief predicted `2 failed, 24 passed, 1 xfailed` at clean HEAD. A `git archive HEAD` stem at
`f7714a3566` gives **29 passed, 2 xfailed** — the brief was written against `f97c34eb0`'s parent and
that commit landed at 23:24 the same day. Verified rather than assumed, on a clean stem, `python3 -B`:

| Mutation | Result |
|---|---|
| M1 — `realised_rate_coverage` silently drops 2019 (neither read nor refused) | **FIRES** on all three coverage legs, with the property message, not a count |
| M2 — fabricate a refusal for 2020, a year the capture demonstrably carries decisions for | **FIRES** on the corroboration leg |
| M3 — the refusal reason stops reaching stdout, the count line stays | **FIRES** on the surface leg |

The cause of the emptying is named, dated and attributable (`b46318106` swapped a 465-row capture
for a 148-row one; 2022 is crisis-forced-passive and C1b routes those rolls to the SVT table, so the
world produces no 2022 renewal decision). The legs are keyed to the property. The refusal names the
year and its reason on the surface. Nothing below reduces that.

## The finding: the correction fixed the denominator and left the mechanism

`f97c34eb0` corrected `_HELD_INDIRECTLY` from an unconditional claim to *"NINE YEARS OF TEN"*, naming
2022 as held by nothing. It left this sentence standing:

> It is held through its EFFECT — the world's realised departure rate, which is `_PRINCIPAL_SUBJECT`
> above and is **band-checked every run**.

Both halves of that are false at HEAD, for two independent reasons, **neither of which is 2022**:

**(i) The holder is XFAIL.** In the same commit, `test_the_worlds_realised_departure_rate_is_inside_
the_published_band` was marked `xfail(strict)` — the world is out of band in 7 of 7 readable years.
A held-open verdict fires only on the world coming *back into* the band. Every anchor value that
keeps it outside passes silently. So the indirection constrains the anchor in one direction only,
and the direction it cannot see is the one it exists to catch.

**(ii) `band-checked every run` overstates the path**, and the holder's own docstring has said so
since 2026-08-31: the control's subject is the **stored capture** `docs/reports/c2_departure_
factors.json`, which carries the `sim_level_anchor` of the run that produced it. The module is not in
its read path. It is band-checked once per **RE-CAPTURE**, not once per run.

Measured, pre-registered before the run
(`docs/staging/done/SEAT_PREREGISTRATION_WHETHER_AN_XFAILED_BAND_LEG_STILL_HOLDS_THE_ANCHOR_IN_THE_NINE_YEARS_IT_CLAIMS_2026-09-01.md`):
**halving every `YEAR_LEVEL_ANCHOR` entry — a 2x error in the world's departure level, larger than
the 1.98x fallback that started this thread — leaves the whole file green, 29 passed, 2 xfailed.**

The prediction's *number* was right and its *mechanism* was wrong: I attributed the pass to the xfail
when the first cause is the read path, which the file already documented forty lines below the entry
that contradicted it. That mis-attribution is graded in the pre-registration beside the claim rather
than revised away.

**So the honest statement the direction asked for: the indirection named in `_HELD_INDIRECTLY` is
holding `YEAR_LEVEL_ANCHOR` in no year at all right now.** 2022 is the year where it can never hold;
the other nine are years where it does not hold until the re-fit lands and a fresh capture is taken.
Naming a gap is not holding it — and that was true of nine more years than the correction said.

## The general shape, which is why this is filed as a class instance

**A quantity classified as held INDIRECTLY is held by exactly as much as its holder is holding, and
nothing told the dependants when the holder was xfailed.** The register and the marker were edited in
the same commit, by the same author, minutes apart, and still came apart — because no route existed
by which one could see the other. This is one level up from the emptied subject that was just
repaired: not *a control over an emptied subject reports a constant PASS*, but *a register over a
suspended control reports cover that does not exist*.

## Second, smaller finding: two of three document citations did not resolve

- The `xfail(strict)` reason's **discharge instruction** ended `Finding: docs/staging/done/WORKER_
  FINDING_A_SCOPE_ASSERTION_WAS_STANDING_IN_FRONT_OF_A_SEVEN_OF_SEVEN_OUT_OF_BAND_VERDICT_2026-09-01.md`
  — **a filename never written**. The finding it means landed in that very commit as
  `..._THE_ANCHORS_ONLY_ACCOUNTABILITY_ROUTE_HAS_BEEN_BLIND_TO_2022_SINCE_THE_CAPTURE_WAS_SWAPPED_...`.
  The reader sent there is, by construction, the one about to repair the control.
- The module docstring's `Opened by:` pointed into `docs/staging/` for a finding since archived to
  `docs/staging/done/` — a correct citation that rots when the filing system does its job.

**Why nothing caught it:** the first path is assembled from two adjacent string literals, so it never
appears contiguously in the source. No grep, diff review or link check over the file's text could see
it. The check has to run on the **assembled** string.

## What was done

All in `tests/architecture/test_switching_rate_commons.py` — the drawn pathspec. No producer change;
nothing under `saas/reporting/` or `tools/generate_dashboard_data.py`.

1. `_HELD_INDIRECTLY` now states both defeats and drops `band-checked every run`.
2. **`test_a_register_entry_naming_a_holder_discloses_whether_that_holder_is_holding`** — symmetric,
   so it cannot become a control asserting the model stays bad: xfail the holder and the entry must
   disclose it (MUT-A, fired); take the marker off and an entry still claiming XFAIL fails (MUT-B,
   fired). The second branch is the one that costs, because stale-in-the-flattering-direction is how
   a closed finding gets re-opened and an open one gets forgotten.
3. **`test_every_document_this_file_cites_is_a_document_that_exists`** — walks the loaded module's
   docstrings, marker reasons and registers, so it reads assembled paths. Refuses an empty citation
   set. (MUT-C, fired; and it fired unprompted on a fake path in its own first docstring.)
4. Both stale citations corrected.

`31 passed, 2 xfailed` at HEAD-plus-this-file. All three mutations run under `python3 -B` on a fresh
`git archive HEAD` stem.

## What is still owed, and it is not in this lane

The re-fit of `YEAR_LEVEL_ANCHOR` against the committed capture, which is what discharges the xfail
and restores the indirection — excluding 2022, which is unidentified. **Not** by widening the band
and **not** by re-keying the leg to today's readings. When it lands, leg 2 above fires until the
register is corrected, which is the intended handshake.

Also not run, and recorded as not run rather than assumed: the confirmation that pushing the world
back *into* the band fires the strict marker. A single global scale cannot do it (years need factors
from ~1.07 to ~1.41), so it needs a per-year construction and belongs with the re-fit.
