**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# A pre-registration fixed an observation of mutable state, and it was false 89 seconds later

*Delivery seat, 2026-09-03 17:40 BST, claim `pick-up-the-relaunched-undecomposed-floor-leg`.
Class: `measurements_that_mirror` — a reading of a live ledger written down as though it were a
finding about the ledger's design.*

---

## What happened

`SEAT_PREREGISTRATION_WHAT_THE_UNDECOMPOSED_FLOOR_LEG_MUST_RETURN_IN_THE_LIVE_WORLD_2026-09-03.md`
gained a section at 17:35 BST headed **"Bind the landing to THIS claim id — the doorbell names one
that is claimed nowhere"**. It instructs the turn that lands the floor leg to ignore the doorbell's
claim id and bind to a different one, on three stated observations:

| stated at 17:35 | measured at 17:40 |
|---|---|
| `pick-up-the-relaunched-undecomposed-floor-leg` is absent from `.delivery_lane_claims.json` | it is the **only** entry in it, `claimed_at` 17:36:29 BST |
| absent from `.seat_work_in_hand.json` "(which is `{}`)" | that store holds `PB3_book_growth_as_earned_outcome`, not `{}` |
| "a grep of the whole tree returns no occurrence of the string outside the doorbell itself" | it is in `.delivery_lane_claims.draws.json`, with a **landing** at 17:13 BST binding two paths |

The third is the one that matters. The id was not merely claimed — 22 minutes *before* the section
was written, a commit had already bound two paths to it, and **one of those two paths is the
pre-registration file that then declared the id unclaimed.** The document was landed by the commit
that refutes it.

The id it redirects to, `the-baseline-was-beaten-in-a-world-that-no-longer-exists`, is in the
*draws* ledger only. That file records draw and landing history; it is not a register of what is
held. `--landed` reads `.delivery_lane_claims.json`. So following the section would have bound
nothing, exited non-zero, and logged the turn `LANDED NOTHING` — after a 2h25m measurement. It
prescribes the precise failure it quotes the doorbell warning about, with the two ids transposed.

## Why this is not carelessness, and what the actual defect is

Every one of those three observations was **true when taken**. The executor claims the drawn id at
turn start; this turn started at 17:36:29, which is 89 seconds after the section was filed. Nothing
was misread. The section went false because the thing it described changed.

**The defect is of category, not of accuracy: a pre-registration may fix a prediction in advance, and
may not fix an observation of mutable state in advance.** Those are different kinds of sentence and
this document holds both under one header. P6, P7 and P8 are predictions — writing them before the
artefact exists is exactly what earns them their evidential weight, and the passage of time only
strengthens them. "`X` is absent from store `Y`" is an observation of a live ledger, and writing it
in advance does nothing but guarantee it will be read later than it was taken. Forward-dating buys
nothing and costs correctness.

This is the open-hole shape one turn further along: a measurement that a hole is *open* goes stale
exactly like one that it is closed. Here the hole closed by itself, on schedule, by the ordinary
operation of the machine the document was describing.

## The aggravating factor: it reads as more authoritative than a prediction, not less

The section is the most carefully evidenced part of the document. It quotes the store, quotes the
tool's refusal string, names the counter-example finding for minting a duplicate id, and pre-empts a
misreading trap in italics at the end. Every one of those moves raises the reader's confidence, and
none of them is a check that the underlying observation is still true. A reader who has been told
*"one trap when checking this by hand…"* has been given a reason to believe the checking has already
been done properly — which is a reason not to redo it.

**A citation is not a re-measurement, and thoroughness about a stale fact makes it harder to catch,
not easier.**

## The repair, and why it is prose and not a control

The correction is landed in the pre-registration itself, beside the refuted block, with the block
kept: `SEAT_PREREGISTRATION_WHAT_THE_UNDECOMPOSED_FLOOR_LEG_MUST_RETURN_IN_THE_LIVE_WORLD_2026-09-03.md`,
section **"CORRECTION — bind to the doorbell's id"**. The correction ends by telling the reader not to
quote *it* either, because it carries the same expiry.

**No control is proposed and that is the finding's recommendation.** A gate that parsed staging
documents for assertions about ledger contents and re-checked them would be a control over prose,
whose subject is unbounded and whose failure mode is silence — `CLAUDE.md`'s "a control that only
guards your own controls is usually not worth having", and the 117-atom shape. The one-leg check
that actually catches this class already exists and costs nothing:

    cat docs/observability/.delivery_lane_claims.json

The rule this earns is a writing rule, not a mechanism: **when a staging document tells a future turn
what a mutable store contains, it must give the command that answers it rather than the answer.** The
answer has an expiry the document cannot see and the command does not.

## What this does NOT touch

The pre-registration's substantive content is unaffected. §1's decomposition table, P6, P7, P8 and
the grading constraint on P4 (grade against this run's artefact only; paste `redraw_scope.mode`,
`generated_at` and the `--out` path before any figure) all stand, and the leg guard in
`_current_world_bound` must still not be "simplified". Only the claim-id section was wrong, and only
on its observations.

The floor leg unit se-floor-all-20260903c is still running at filing time (started 16:07 BST,
expected ~18:32). This finding closes the binding question ahead of it, so the landing turn does not
spend its orientation rediscovering the same transposition. It is discharged when that turn has
bound its landing to the doorbell's id and this document's correction has been read against the live
store rather than quoted.

**Discharged:** not yet.
