**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

# PRE-REGISTRATION — what a whole-book re-capture must MOVE, and whether re-capturing can discharge the band leg at all

**Filed 2026-09-02, delivery seat, from an isolated worktree at HEAD `19e68169b`, BEFORE the capture
is run and before any of its output is read.** Grading is appended below, beside each prediction's
filed text, misses kept.

## Why this run, and what is already discharged so it is not re-derived here

The drawn Lane 0 item's "done means" is discharged by earlier ticks and verified this tick from the
artefacts rather than recalled:

* The collision is **answered**, as a PARTITION, at `d374b1977` —
  `docs/design/THE_LEVEL_ANCHOR_COLLISION_ANSWERED_2026-09-02.md`. 2016/2025 fall back (outside the
  fit's comparison window), 2022 is declared unidentified with two independently-scoped causes.
* The block document is **committed** at `9238075d9`, so the "land it first" instruction is
  discharged by verification (`git ls-files` matches, `HEAD...origin/main` is `0 0`), not by re-doing it.
* One table live, one **explicitly retired**: the ten-year block is retired rather than re-cited
  because its stated fit input resolves to a capture produced by its own successor (`ae8e2ec3f`
  further fixed the citation pointing at a document that did not contain it).
* `tools/population_anchor.py`'s 2022 reads **fail closed with named reasons** — the
  `.get("sim_churn_rate", 0.0)` measured zero is gone as of 2026-09-02.
* The disclosure handshake **fired and the register was corrected**, not re-keyed.
* `SEAT_PREREGISTRATION_WHETHER_THE_ANCHOR_CAN_BE_HELD_WITHOUT_A_RECAPTURE_2026-09-02.md` closed the
  "halving every entry leaves the file green" hole with a leg keyed to the property (the capture the
  band verdict is read from was produced by the live table).

**Its own closing paragraph is what this run is for:** *"It does not judge the anchor's value — the
band leg still does, and it is still `xfail(strict)` with the world out of band in 7 of 7 readable
years. The anchor is still band-held in NO year."* The stated discharge, in three separate
documents, is **a re-capture followed by a re-fit**. Nobody has run it.
`tools/capture_departure_factors.py`'s own docstring agrees it is owed: *"Re-running the capture from
this HEAD is now a different experiment from either, and is owed."*

## The reading that makes this more than a chore, stated in advance so the run can refute it

The band leg's subject is `measure_departure_level.world_realised_rate_pct` — **a mean over renewal
DECISIONS**. Post-C1b that is a *selected* sub-population: the households that took a fixed deal.
The published record's own `basis.denominator`, read from the commons artefact this tick, is **"ALL
GB domestic electricity accounts, whether or not the account was at a decision point that year"**.
And the live `YEAR_LEVEL_ANCHOR` was fitted on **account-years**, the union of both departure routes.

**Three different denominators, and the control divides two numbers that do not make a quantity.**
`world_book_rate_pct` — the account-years union — is the comparable column, it is committed, and it
is **not what the band control reads**. It cannot be: `c2_departure_factors.json` has **no
`_svt_segment_decisions.json` sibling** (verified by `ls`; only the `ladder_*` family has one), so
`account_denominator_refusal` refuses and the whole-book column is unreadable.

So there are two candidate explanations for 7-of-7 out of band, and they prescribe opposite repairs:

* **The xfail marker's own diagnosis** — *"the anchor is stale against the capture it is now read
  with"* — for which the repair is re-capture and re-fit.
* **A denominator mismatch** — for which re-capturing changes nothing, because a renewal-decision
  mean compared against a whole-population band is out of band by construction.

This run separates them. **I do not know which it is**, and P6 below is written so that the answer
can go against the reading I have just argued for.

## Method, and the one design decision taken in advance

Clean stem via `git archive HEAD` into a `/tmp` extract (free space checked: 3.0G on `/tmp`), run
under `systemd-run --user --unit=`, waited on with `tools/wait_for.py` naming its subject and
carrying a deadline. All producers are committed at this HEAD — the SVT recorder at `6db30a350` and
the SVT **assignment** at `8bf416115` — which is precisely what makes this run different from the
09-01 clean-tree run that captured zero SVT decisions.

**The capture writes to a NEW filename and does NOT overwrite `docs/reports/c2_departure_factors.json`.**
This is registered as a decision, not an implementation detail: overwriting a committed capture in
place under a stable path is exactly `b46318106`, the commit that made the retired ten-year block's
provenance unfollowable and cost this thread three orientations. A stable path over a moving run is
`figures_on_a_superseded_clock`. The new capture is a new artefact with its own name.

---

## Predictions

Each names the MOVE, with the value it moves **from** and **to**. An invariance is not a prediction.

**P1 — the SVT sibling goes from absent to populated.** From: no `c2_departure_factors_svt_segment_decisions.json`
exists at all, and the 09-01 clean-tree run printed `THE SVT RECORDER RAN AND RECORDED NOTHING` with
0 SVT decisions. To: this run writes a sibling carrying **> 0 rows**, and does not print that banner.
**Refuted** if the sibling is absent, empty, or the banner prints.

**P2 — the whole-book column goes from unreadable to readable.** From: `world_book_rate_pct()` on the
committed capture returns `({}, <refusal>)` — no years, `account_denominator_refusal` firing. To: on
the new capture it returns **≥ 5 years** with `expected_rate_pct is not None` and refusal `None`.
**Refuted** if it still refuses, or reads fewer than 5 years.

**P3 — the direction, and the quantity the whole argument turns on.** For every year readable on
both columns, the whole-book rate **strictly exceeds** the renewal-decision rate, i.e. the move is
**UP**. Reason: the union adds the SVT route's departures to the numerator, and the SVT floor is
high (12.09% at 2022 per `d374b1977`). **Refuted** if the book rate is at or below the renewal rate
in *any* year — which would mean the account denominator grows faster than the union numerator and
my reading of why the band leg fails is wrong. I flag this as the prediction most able to embarrass
the argument above.

**P4 — 2022 becomes readable for the first time, on one column only.** From: 2022 is absent from the
committed capture **entirely** (0 renewal rows; 9 of 10 record years present). To: the new capture
again carries **0 renewal decisions** in 2022 — it is 100% crisis-forced-passive and C1b routes every
passive roll to the SVT table — but **> 0 SVT segment decisions**, so 2022 carries a whole-book rate
where it previously carried nothing. And that rate is **above the published 4.30% ceiling**, since
`build_departure_risks` does not scale `svt_inertia` and no anchor ≥ 0 moves it. **Refuted** if 2022
carries renewal rows, carries no SVT rows, or lands inside its band.

**P5 — the agreement leg survives a legitimate re-capture, which it has never been tested against.**
`test_the_capture_the_band_verdict_is_read_from_was_produced_by_the_live_anchor` landed on the claim
that *"a re-fit that lands with its re-capture moves both sides together and stays green"*. That
claim has never met an actual re-capture. Predicted: the new capture's `sim_level_anchor` column
agrees with live `year_level_anchor(year)` to 1e-6 in **every year present, including 2022 at
`NO_LEVEL_CORRECTION = 1.0`**, where the committed capture has no 2022 row to disagree with.
**Refuted** if any year disagrees — which would make the leg's own stated justification false.

**P6 — re-capturing alone does NOT discharge the band leg, and this is the adversarial one.**
Predicted: on the fresh capture, `world_realised_rate_pct` (renewal decisions) remains **OUTSIDE**
the published band in **≥ 5 of the readable comparison years**. **Refuted** if the fresh capture puts
the renewal-decision rate inside the band in ≥ 5 of 7 years — in which case the xfail marker's own
"the anchor is stale against the capture" diagnosis was right, the denominator argument above is
wrong, and I will report that as a miss rather than reinterpret the prediction.

*Registered consequence, in advance so it cannot be chosen after the fact:* if P6 holds **and** P2/P3
hold, then the honest result is that **the band leg's subject is the wrong column**, and the repair
is to judge the band on `world_book_rate_pct` — not to widen the band, not to re-key the marker, and
not to declare the anchor verified. If P6 is refuted, the repair is an ordinary re-fit and the
denominator argument is withdrawn in writing.

## Constraints — things that must NOT happen, discharged by reading the artefact

1. **No value in `YEAR_LEVEL_ANCHOR` or `UNFITTED_YEARS` is added, edited or deleted by this run.**
2. **No committed capture is overwritten in place.** `docs/reports/c2_departure_factors.json` and the
   `ladder_*` family are read-only to this stretch; the run writes a new filename.
3. **No band is widened, and no `xfail` marker is removed, narrowed, or re-keyed to today's readings.**
   Both strict markers stand exactly as they are.
4. **No fit is landed on a capture whose producers are not all committed.** If the stem's run turns
   out to depend on anything uncommitted, that is a finding and the fit does not land.

Discharged at grading by pasting `git status --porcelain` and `git diff --stat` over `simulation/`,
`docs/reports/` and the marker files — read from the artefact, not recalled.

---

# GRADING

*To be appended after the run. Each prediction graded beside its filed text above; misses kept, not
revised.*
