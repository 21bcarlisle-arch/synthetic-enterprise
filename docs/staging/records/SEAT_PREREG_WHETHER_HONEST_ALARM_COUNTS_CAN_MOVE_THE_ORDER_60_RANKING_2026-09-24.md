**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# PRE-REGISTRATION — whether honest alarm counts can move the ORDER 60 draw ranking

Drawn as `check-whether-honest-alarm-counts-move-the-order-60-draw-ranking` (Lane 0, director
direction). Written **before** reading the ranking code or diagnosing the repair path, so that the
predictions below are refutable rather than decorative.

## What this is answering

`SEAT_FINDING_THREE_ALARM_FAMILIES_BYPASS_NOTIFY_AND_HARDCODE_REPEATS_1` claimed the understatement
was *"a plausible partial answer to why the alarm backlog was never drawn, and it is checkable
against the draw log rather than assumed"*. `SEAT_FINDING_THE_HEADER_IS_STAMPED_ONCE_AND_NEVER_RE_DERIVED`
(landed `22ec75803`, 2026-09-24 00:56) then said explicitly: *"Not that the ORDER 60 ranking will now
move. ... still a plausible partial answer and still unchecked."* This is that check.

## The premise, re-measured at draw

**Not spent, but its stated METHOD is already refuted by observation.** `22ec75803` is an ancestor of
`origin/main` as the draw said. The duplicate-work check named this claim's own id — my own draw, not
a rival's.

The item instructs: *"the documents repair themselves on each family's next firing, so wait for
that, then compare draw positions."* Measured on the SHARED tree at 01:19, before any prediction
below:

- **Ten** live alarm documents (my worktree, 8 commits behind, carries only nine — it lacks
  `OPERATIONAL_LAYER_SIGNAL`).
- **Zero** carry the repaired block (`grep -c 'separate day(s)'` = 0 in all ten).
- **Four were written AFTER the fix landed**: `STRETCH_LOG` 01:01, `DEADMAN_LAUNCH_ARTEFACT_UNLANDED`
  01:07, `DEADMAN_ORIGIN_FORK` 01:07, `DEADMAN_WORKTREE_UNDECLARED` 01:09.

So the waiting the item prescribes has already happened four times over and produced no repair.
**Waiting longer is not the experiment.** The question is why, and that is a prediction.

## Predictions — cause of the non-repair

**P1 (leading). The daemon is running a module it imported before the fix landed.** The writers are
long-lived processes; `background/alarm_repetition.py` changed at 00:56; a process started before
that holds the pre-fix code in memory and will keep writing pre-fix headers until restarted. If so,
the fix is correct and its DELIVERY claim ("no migration to run — they repair themselves") is what is
wrong, because it silently assumed a cold start.

**P2. The writes at 01:01–01:09 did not go through `_refresh_counts()` at all** — they came from the
re-ask's annotation path (`reask(apply=True)`, running every 30s in `staging_watcher`) rather than
from `escalate()`. `_refresh_counts` is called on `escalate()`'s two branches; if the re-ask appends
a still-live line by another route, then the repair is wired to a writer that is not the one actually
touching these files, and P1 would be the flattering reading.

P1 and P2 are not exclusive and I expect the honest answer to name which writes belong to which.

## Predictions — the ranking itself

**P3 (the item's actual question). The honest counts do NOT move the ORDER 60 ranking, and the
finding's "plausible partial answer" is REFUTED as a cause rather than left unconfirmed.** My reason
for expecting this before looking: both code comments that mention ORDER 60 describe the ten as
*"unrankable against each other — there is no reading of any of them that says whether anyone has
looked since it was filed"*. That is a statement about the ranker having no term for these documents
at all, not about a term reading a number too small. A ranker with no term cannot be moved by making
the number honest.

**P4. ORDER 60 is assigned from the document's CLASSIFICATION — filename prefix, severity band, or
lane — and no term in the ranking function reads `repeats`, `days` or `members` from the body
prose.** Falsified if any ranking term parses a count out of the document text.

**P5. The tie-break among the ten at ORDER 60 is positional (mtime, filename or directory order) and
is therefore still arbitrary after the repair.** If P4 holds and P5 holds, then honest counts are
necessary-but-not-sufficient: the numbers become true and the queue still cannot order them.

**P6. If P3 is right, the residual value of `22ec75803` is NOT ranking but READABILITY** — a human or
a draw reading one document learns its real scale. That is worth having and is a different claim from
the one the original finding made. I register it now so I cannot retro-fit it as a success.

## What would refute each

| prediction | refuted by |
|---|---|
| P1 | writer process start time is AFTER 00:56 and it still wrote a stale header |
| P2 | the 01:01–01:09 writes are reached through `escalate()` and `_refresh_counts()` ran |
| P3 | draw position of any alarm document changes when its counts become honest |
| P4 | a ranking term parses a count from document text |
| P5 | the ORDER 60 tie is broken by a content-derived quantity |
| P6 | nothing downstream reads the derived block |

## What done means for this turn

Not "the ranking moved". Done is: **the causal question is settled with evidence either way, and the
mechanism that made the item's own method impossible is either fixed or filed as a finding with its
severity header.** A refuted prediction kept beside its result is the deliverable; so is a landed
repair if the cause turns out to be fixable in one turn.
