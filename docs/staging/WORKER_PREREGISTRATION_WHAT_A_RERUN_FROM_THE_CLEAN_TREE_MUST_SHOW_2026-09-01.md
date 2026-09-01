**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

*RECORDED, not LATENT: a pre-registration refutes nothing on its own. It exists so the measurement
filed beside it can be shown to have been designed before its answer was known. It changes no
published figure; it decides whether the whole-book `YEAR_LEVEL_ANCHOR` block emitted on 2026-09-01
may be adopted, or must stay recorded-not-adopted.*

# PREREGISTRATION — what a re-run of the native SVT capture from a CLEAN tree must show

**Filed 2026-09-01, delivery seat, Lane 0. BEFORE the run. Nothing below is known.**

## Why this run exists

`WORKER_PREREGISTRATION_WHAT_A_NATIVE_SVT_CAPTURE_MUST_SHOW_2026-09-01.md` was graded at
`68ec6825b`. Its **owed item 3** is *"re-run this capture and confirm the block is byte-stable"*.
This is that run. It is also the measurement that settles two things the grading got wrong or left
open, both established by inspection before this file was written:

**(a) P1's provenance refutation grepped the wrong file.** The grading refuted P1's heading clause
*"by a producer in git"* on the evidence that `rolls_active_renewal` has 0 occurrences in
`origin/main:simulation/renewals.py`. That function has never lived in `renewals.py`. It is defined
at `origin/main:simulation/renewal_engagement.py:65`, imported at `run_phase2b.py:181`, and called
at `run_phase2b.py:1772`. The C1b SVT roll itself is `_svt_roll` at `run_phase2b.py:1651`, and
`run_phase2b.py` was **not** in PROVENANCE's dirty list — its sha256 as run matches origin. So the
grep tested a symbol against a file that never held it, and **the refutation it produced is not
established.** This is the class *a grader reading the wrong artefact reports a false refutation*.

**(b) The reproducibility question is real, but it is a different one.** `PROVENANCE.txt` records
`DIRTY-vs-origin: simulation/renewals.py` at run time (HEAD `83946eb44`). The sha256 it recorded,
`b469c78c…`, does **not** match the working tree's `renewals.py` today, `4172e840…`. The tree is now
clean against `origin/main` (`git rev-list --left-right --count HEAD...origin/main` = `0 0`), so the
`renewals.py` that produced the 2026-09-01 capture **exists in no commit and in no working tree**.
Whether that matters is exactly what is unmeasured: it matters only if those differences reach the
captured outputs.

**So the honest state before this run is: P1's provenance clause is UNMEASURED, not refuted.** The
grading recorded it as refuted on the strength of a grep that could not have found what it looked
for.

## What is being run

`python3 -m tools.capture_departure_factors /tmp/svtcap2/c2_marketterm.json`, from the clean tree at
`68ec6825b` == `origin/main`, under `systemd-run --user --unit=svt-rerun-clean` so it outlives its
launcher, waited on with `tools/wait_for.py`. A **new stem** (`/tmp/svtcap2/`, not `/tmp/svtcap/`)
because the 2026-09-01 artefacts are the comparison basis and must survive the run.

**Nothing else changes.** No constant, no band, no clamp, no repair to `population_anchor`.

## The predictions

### R1 — the run completes and writes both files

`EXIT_RC=0`, `c2_marketterm.json` and `c2_marketterm_svt_segment_decisions.json` both written,
neither the "no recorder" nor the "recorded nothing" stderr warning fired.

**Refuted by:** a non-zero exit, a missing file, or either warning on stderr.

Confidence: high. The recorder and its roll are both in `origin/main` — that is (a) above, and it
is inspection, not prediction.

### R2 — the SVT sibling is byte-identical to the 2026-09-01 capture

`sha256sum` of `/tmp/svtcap2/c2_marketterm_svt_segment_decisions.json` equals that of
`/tmp/svtcap/c2_marketterm_svt_segment_decisions.json`: 1373 decisions, 38 departed.

**Refuted by:** any difference in the hash, the row count, or the departed count.

Confidence: **low, and this is the prediction I am least sure of.** The SVT roll is seeded
`f"svt_inertia_{billing_account}_{term_start_str}"` — no global RNG state — so the route is
reproducible *given the same segment set*. But `renewals.py` builds the schedule that decides which
segments exist at all, and it is a different file now. I predict identical because I believe the
lost diff was in the renewal leg, not the SVT leg — **and I have no evidence for that belief**,
which is why it is written down here rather than asserted afterwards.

### R3 — the renewal table is NOT byte-identical

`/tmp/svtcap2/c2_marketterm.json` differs from `/tmp/svtcap/c2_marketterm.json` — a row count other
than 156, or the same count with different values.

**Refuted by:** a byte-identical renewal table.

Confidence: moderate, and **note that R2 and R3 predict opposite outcomes from the same cause.**
That is deliberate: it is the sharpest available test of where the lost `renewals.py` diff lived. If
both hold, the diff was renewal-only and the SVT block is safe to adopt. If both fail — both files
identical — then the lost diff reached neither output and the whole reproducibility worry is void.
**If R2 fails and R3 holds, the block must not be adopted**, and that is the answer that costs the
most, so I am naming it in advance.

### R4 — the whole-book fit still emits, with the same 2022 floor and 2023 anchor

A `YEAR_LEVEL_ANCHOR` block is emitted; 2022's SVT floor prints 2.54%; 2023's anchor prints 2.0539.

**Refuted by:** no block emitted, or either figure moving.

Confidence: conditional on R2. If the SVT sibling is stable these follow; if it is not, this is the
measurement of how far the instability propagates, which is the number that decides whether the
2026-09-01 block is quotable at all.

### R5 — 2022 is still NOT FITTED, on zero renewal decisions

2022 prints `NOT FITTED — no renewal decisions in this year`, over 55 accounts, and its anchor is
`—`.

**Refuted by:** 2022 fitting, or printing a different cause, or a different account count.

Confidence: high, and **I want this one to survive.** The 2026-09-01 grading's most useful finding
was that clearing the SVT floor did not make 2022 reachable, because two independent causes bind. A
re-run that suddenly fits 2022 would mean that finding was an artefact of the lost `renewals.py`,
not a property of the world — so this is the prediction whose refutation would cost the most
elsewhere.

## What must NOT happen when this is scored

1. **No constant adopted into `simulation/departure_level_anchor.py`**, however green. Two captures
   agreeing is not evidence for a level; it is evidence for reproducibility, which is a different
   claim. Adoption remains a separate decision needing separate evidence.
2. **No widened band and no clamp on 2022.** If R5 holds, 2022 stays unfitted with both causes
   named.
3. **`population_anchor._churn_by_year` is not repaired by inserting a `sim_churn_rate` of 0.0.**
   `tools/population_anchor.py` is outside this stretch's pathspec and is not touched here. The
   repair is to fail its five 2022 consumers closed; it stays recorded and owed.
4. **R2 is not re-scored as "close enough".** Byte-identical or not. A hash comparison has no
   judgement in it, and permitting one here is how the next reader gets a block described as stable
   that is not.
5. **If R2 and R3 both fail (both files identical), P1's provenance clause is settled CONFIRMED,
   not quietly dropped.** The clause was filed, wrongly refuted, and is owed a real verdict.

## What this run cannot settle

Whether the *2026-09-01* artefacts are reproducible. They were produced by a file that no longer
exists, and no run from any current tree can recover it. This run establishes whether the **current**
tree produces the same numbers — which is the question that actually governs adoption, but it is a
weaker claim than the grading's owed item 3 implied, and the difference is worth stating: agreement
here means *today's tree agrees with that output*, never *that output has been reproduced*.
