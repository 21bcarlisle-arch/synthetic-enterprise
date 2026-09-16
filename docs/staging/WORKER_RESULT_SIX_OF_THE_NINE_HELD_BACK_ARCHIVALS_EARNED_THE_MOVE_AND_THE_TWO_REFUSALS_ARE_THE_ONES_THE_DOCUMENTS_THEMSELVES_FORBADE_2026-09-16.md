**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — nine-held-back-staging-paths-each-need-their-own-decision-not-a-re-run-of-the-archival)

# Six of the nine held-back archivals earned the move, and both refusals are refusals the documents themselves had written down in advance

**2026-09-16, scheduled tick, delivery seat.** Closes the Lane 0 direction that held nine staging
paths back from the archival landed on `dc8303203`, on the ground that an archival is a discharge:
`finding_severity.classifiable_documents` globs the staging root non-recursively, and
`false_discharges` iterates that same root-only list, so the one control that checks a discharge
claim against the filesystem goes blind at the exact moment the discharge happens. Nine documents
therefore had to be decided one at a time rather than re-run as a batch.

The decisions, and the measurement behind each:

| # | document | decision | what settled it |
|---|---|---|---|
| 1 | decomposition class's reachability leg (A) | **REFUSED**, severity corrected BLOCKING → LATENT | red gone, payload defect live, and the control leg was deleted |
| 2 | nine-seed floor's stated publish path (A) | LANDED with a discharge field | three controls green; selection leg now reads n=9 beside `contrast_bounds` |
| 3 | Lane 0 pair move's remaining third (A) | LANDED with a discharge field | all three legs spent; leg 3 made unnecessary rather than executed |
| 4 | departure headline, mean over shoppers (A) | **REFUSED** | the half the document says was NOT fixed is still the live page's headline |
| 5 | producer's named witness vs the control's real one (W2) | LANDED with a discharge field | the later-panel control exists and is green |
| 6 | proof page told a reader a larger figure was smaller (G) | LANDED with a discharge field | the partition-reachability control is green; the clause is derived, not stated |
| 7 | `REPEATING_ALARM` SEAT_CLAIM ledger (H) | LANDED | the `done/` copy is a strict SUPERSET, +9 lines, −0 |
| 8 | `REPEATING_ALARM` SEAT_CONTINUITY ledger (H) | LANDED, after repairing the copy | the `done/` copy was 47 committed lines BEHIND; landed from the root bytes instead |
| 9 | run-reducer `done/` document (W2) | LANDED with its own claim refuted in place | it reached no ref at all, and neither half of its "landed" claim is at HEAD |

Three lanes were holding on four BLOCKING documents between them. Two of those four are discharged
with a named, checkable falsifier; two stay live. So the lane holds did not all clear, and that is
the result rather than a shortfall in it — the direction's own premise was that landing nine unread
would turn every surface green while burying six live findings.

---

## The two refusals, because they are the load-bearing half

Both are refusals the documents wrote down before the answer was known, which is the only reason
they were catchable at all.

**The decomposition class (`#1`) named the repair that must not be made, and it is the repair that
was made.** Item 1 of its "what is next" reads: *"do not relax `assert strata_on_the_page >= 1` and
do not add `decisions` to an exception list ... deleting it because the class went empty is how a
partition stops being covered."* At HEAD today, `_DECOMPOSITION_KEYS` is gone from
`site/test_the_baseline_comparison_reaches_the_reader.py`, `_measured_cuts_only` splits
measured / hypothetical / unclassifiable only, and `strata_on_the_page` appears nowhere in `site/`,
`tools/` or `tests/`. Meanwhile `tools/run_value_cycle_ab.py` still writes `"decisions"` beside
`"comparable_pairs"` on all three strata — the payload half, which the document was careful to
separate from the control half.

So the red cleared and the defect did not, and the control that noticed the defect is the one that
went. **A control keyed to today's answer goes green when the claim rots**, and here the severity
field had the same defect as a control would: the document's entire stated reason for BLOCKING was
*"it is a red at `origin/main` in the site lane"*, which is now false. The severity is corrected to
LATENT in the document, beside the original, with the falsifier's green run quoted. The finding
itself stays live and stays on the queue.

**The departure headline (`#4`) is still on the published page.** The document splits itself into
FIXED (the `denominator` field, and the comparable whole-book reading published alongside) and NOT
FIXED (which of the two is the headline). Measured on `site/data/value_arms.json` as it ships:
`departure_level.world_mean_pct` is 28.08 — the renewal-decision reading — and `statement` still
instructs the reader that *"every retention, churn and lifetime-value figure below reads LOW by
roughly that factor"* at 1.63x, while `bounding_statement` in the same block says the comparable
whole-book figure is 1.14x. One page, two blocks, disagreeing about the discount a reader should
apply to every money figure on it. Archiving that would have recorded a published instruction to
misread a page as repaired.

## What the four landed discharges are, and what they deliberately are not

Each of the four carries a `**Discharged:**` field naming a falsifier that is landed and was run in
this tree this tick, which is the two-step check `b6a147bb7` established: the field must parse
released, and the cited node must actually pass. Five distinct nodes across
`tests/tools/test_generate_value_arms_data.py`, all green.

Each field also names what it does **not** discharge, rather than letting the archival imply
closure:

* the nine-seed floor leg still states no direction at n=9 — the selection question is open, and it
  is the atom's, not the finding's;
* the promote-by-copy census (*"if the bytes at this path were replaced by a newer run of the same
  shape, would any sentence on the page become false"*) is asked by two of the four and belongs to
  **one** new atom, not to two archived findings.

## The two alarm ledgers were not symmetrical, and the held-back reading had it backwards

The direction described both `REPEATING_ALARM` ledgers as having a `done/` copy older than HEAD's
root copy. Measured, that is true of one and false of the other:

* **SEAT_CLAIM** — `done/` is a strict superset: +9 lines (two 2026-09-10/09-11 occurrence lines and
  seven claim rows), −0. Landing it loses nothing.
* **SEAT_CONTINUITY** — `done/` is 47 lines behind and 0 ahead. What it was missing is a whole
  2026-09-15 15:09 UTC occurrence: its claim row, its repetition line, and the full
  what-to-do-with-it block. Landed from the committed root bytes instead of the stale disk copy.

An append-only ledger archived from a stale copy loses precisely the most recent thing that happened
to it, at the moment the filesystem check stops reading it. Both conditions still have live homes in
the staging root (`..._SEAT_CLAIM_2026-09-15.md`, `..._SEAT_CONTINUITY_2026-09-15.md`), so what was
archived is a spent record and not a live alarm.

## The ninth document is the finding's own subject, happening to the finding

`WORKER_FINDING_THE_RUN_REDUCER_FORWARDED_THE_DEPARTURE_COUNT_AND_DROPPED_THE_POPULATION_IT_CAME_FROM_2026-08-31.md`
existed in no committed ref, in either staging room, for sixteen days. Its line 7 asserts *"Control
landed with it"*. Neither half of that is at HEAD: the control file is on disk and in no commit, and
`HEAD`'s copy of `saas/reporting/annual_report.py` contains no occurrence of `svt_decisions` at all.

The document's own subject is *a repair forwarded a numerator and left the denominator behind*. The
same thing then happened to the record of the repair. It is committed — a record nobody can reach is
the defect this whole archival landing exists to end — with the claim left standing and refuted in
place rather than edited away, and the live work named as still owed by `W2_customer_generator`.

## What is next

1. **The two refused findings go back on the queue as ordinary work**, in `A_strategy_governance`:
   the producer rename on `pair_strata.decisions` (with the poison round item 3 of that document
   asks for), and the departure-headline re-siting (with the preregistration item 1 of that document
   asks for). Neither is this tick's work and neither is blocked on anything.
2. **One atom for the promote-by-copy census**, not two. Both `#5` and `#6` file the same question
   from opposite ends of the same file, and minting it twice is how a class gets two half-owners.
3. **The blind spot this direction was written about is unrepaired.** `false_discharges` still
   iterates the root-only list, so it still cannot see a document at the moment that document is
   discharged. Every check in this tick was done by hand because of that. The cheapest honest
   version is to have it read both rooms and grade a `done/` document's discharge field once, on
   arrival — filed as the next step rather than built here, because it is a control over the
   controls and CLAUDE.md is explicit that those usually are not worth having. This one might be:
   nine documents needed a seat to adjudicate them precisely because nothing could.
