**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

# Nothing asks whether a BLOCKING finding's own falsifiers are already green, so a stale severity grade freezes a lane behind finished work

Filed from the re-grade of
`docs/staging/done/SEAT_FINDING_ORIGIN_MAIN_CARRIES_SEVEN_REDS_THAT_NO_COMMITS_GATE_SELECTION_REACHES_2026-09-22.md`
(commit `44e7141e4`), which promised this class would be filed rather than fixed on sight.

## The instance, priced

That finding's work landed on 2026-09-22 in `943b9b4f9` and `b305119b1`. Its closing record,
`docs/staging/records/SEAT_RESULT_THE_SEVEN_REDS_ARE_GREEN_AND_THREE_WERE_DETECTORS_OVER_MATCHING_2026-09-22.md`,
opens with *"Closes the Lane 0 item `origin-main-carries-seven-reds-that-no-commits-gate-selection-reaches`"*
and was itself archived into `records/`. **The finding's severity header stayed BLOCKING for two
days.**

Under OPS12 clause 3 a live BLOCKING finding draws ahead of its lane's general disposition queue,
latent findings and all new feature work. So the stale grade froze `A_strategy_governance` behind
work that was already done, and the 2026-09-24 draw spent an invocation re-deriving it — the
measurement was worth taking (it confirmed both halves two trunk commits later, which no prior run
had) but the *freeze* bought nothing.

## Why no control saw it

Two instruments look adjacent and neither asks this question:

- `background/staging_rooms.py` reports **RECORDED findings in the root** as archivable-not-drawable.
  That is the already-downgraded case. A BLOCKING document is never a candidate.
- `background/finding_severity.py --by-construction` names **non-BLOCKING documents whose own text
  says an instrument is wrong** — i.e. it hunts grades that are too LOW.

Both run in the flattering direction. The expensive direction — a grade that is too HIGH, which
costs a whole lane rather than one document — has no reader. This is the repository's own
fail-open shape: the check that exists is the one whose failure is cheap.

## The candidate one-leg remedy, so the next lane does not re-derive it

"Are its falsifiers green" is not cheaply decidable — it means running them. But the instance above
was decidable from the filesystem and git alone, on 09-22, by a much narrower property:

> **A finding graded BLOCKING whose own document name is cited by a record in `docs/staging/records/`
> or `docs/staging/done/` that claims to close it.**

The closing record existed, was archived, and named the finding. One `git grep` over two rooms would
have fired the day the grade went stale. That is a one-leg check over a real population, not a
register — and it is why this is filed rather than turned into a new watcher.

**Keyed to the property, not to today's answer:** the leg must compare *grade* against *the existence
of a closing record*, never against a pinned list of today's eleven BLOCKING documents — a literal
bound goes absent the moment the population grows, which is the failure this project has already
paid for in `records/`.

**What is NOT claimed here.** I have not established how many of the other ten live BLOCKING
findings are in this state. The census is the first half of the work and it is not done; one instance
plus two instruments that provably look the other way is what this document rests on.
