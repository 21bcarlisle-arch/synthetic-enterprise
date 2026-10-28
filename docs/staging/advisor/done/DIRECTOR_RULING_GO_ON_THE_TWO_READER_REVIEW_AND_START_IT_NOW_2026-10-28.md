**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-RULING] Go on the two-reader review of risky commits, and start it now (2026-10-28)

**Type:** RULING, through the advisor channel. The director's words, from chat on Wed 28 Oct:

- 06:39 GMT, on the advisor's recommendation to run the narrow reader the 17 Oct trial proposed: "Go, but also and after this answer me why are actions for me not getting flagged better and reminded?"

## What this rules

The proposal raised on 17 Oct as `reading-reviewer-trial-your-08-56-yes` goes ahead as proposed:
- two blind, non-blocking Opus readers;
- only on commits that add a new module or re-implement a rule something else already computes;
- a finding is filed only when both readers raise it, and it is then checked like any finding;
- scored for two weeks through `judge_validation`, and stopped if fewer than half the filed findings are confirmed.

## Why this file exists, when the row was already closed

The row was withdrawn on 26 Oct as "not a G5-reserved action, so not his to rule", and closed "on the seat's own recommendation: the two-reader blind non-blocking review trial as proposed". That close says yes. But the advisor found nothing landed since 26 Oct that runs the readers, and nothing in the record says when it will start. A close that means "do it", with nothing done, is the gap the director's second question is about. If it is running and the advisor missed it, say where, and this file needs nothing more.

## Done means

- The readers have run on the first qualifying commits. A dry list of which commits would have qualified does not count.
- The stretch log names the start date and the first readings.
- The two-week review date is in the record, with the stop rule.

## Risk

Touches: a post-commit reading lane only. No commit gate, and no change to an existing gate.
Blast radius: compute spend of two Opus reads per qualifying commit, inside the P12 pace.
Probable failure mode: the qualifying test is too broad, so the readers run on most commits and the spend balloons. Report the share of commits that qualified in the first readings.
Proportionality: reversible and narrow — just do it.

— Director ruling, 28 Oct 2026, his words above; the drafting is the advisor's.

## Done

*Delivery seat, 2026-10-28.* It was not running. The advisor was right.

- **Started 2026-10-28.** Two blind Opus readers ran on each qualifying commit since 26 Oct. That is 2 of 157 non-merge commits (**1.3%**): `529a6b05a8` and `a3f6926173`. All four verdicts are NEEDS_WORK, recorded in the trust ledger. Five findings were raised by both readers. On my check at HEAD, 4 are confirmed and 1 was partly fixed by a later commit. The worst is that `INV_OPENING_READ` cannot fail: all 1,293 of 1,293 first reads on the 1691 book are a `carried_forward` read on day 0. That is BLOCKING for the correctness stretch's exit leg. Write-up: `docs/staging/done/SEAT_FINDING_THE_TWO_READER_REVIEW_STARTED_AND_BOTH_READERS_FOUND_THE_OPENING_READ_CONTROL_CANNOT_FAIL_2026-10-28.md`.
- **Review date: 2026-11-11.** Stop rule: if fewer than half the filed findings are confirmed, it stops.
- **Residual, dated:** the readers were run by hand from this turn. Making them run automatically on every qualifying commit is the continuation `the-two-reader-review-runs-on-every-qualifying-commit`, **due 2026-10-30**. The mechanical selector covers new modules only. The "re-implements a rule" class has no selector yet, and that gap is stated in the finding.
