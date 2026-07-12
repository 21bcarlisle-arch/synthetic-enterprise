---
name: incident-retro
description: The retrospective format that has produced this project's R-rules (docs/retrospectives/). Use when a phase-close closed a multi-day/multi-false-claim problem, ~50 phases or 2 weeks have passed since the last retro, a harness rule changed, or a real self-caught incident (a security-relevant mistake, a false completion claim, a stale-process bug) needs writing up.
when_to_use: Invoke at the phase-close checklist's own retro-check trigger, or immediately after catching yourself in an error worth generalising (not just fixing the instance).
---

# Incident / retrospective format

File at `docs/retrospectives/<date>-<short-name>.md`. Real examples:
`2026-07-04-verification-week.md`, `2026-07-08-test-suite-tmux-leak.md`,
`2026-07-12-director-twin-unrestricted-spawn.md`.

## Structure

1. **Title + date range.** What period or single incident this covers.
2. **Claim discipline up front (R9):** state explicitly that every claim below is labelled
   `observed-with-evidence` or `inferred`, evidence before narrative. If a claim implies an external
   actor, compromise, or blame, it must be checked against the most direct available evidence (the
   actual channel history, the actual process list, the actual commit timestamps) BEFORE being
   asserted — not after. If that check hasn't been done, say so rather than presenting an inferred
   narrative as established.
3. **What happened.** Concrete, not abstracted — what was claimed, what was actually true, and the
   gap between them. Name the specific files/commits/timestamps, not "some issue arose."
4. **Root cause, not the instance.** Trace back to the ONE mechanism producing the class of failure
   (R4: name the nearest working analogue and state the diff). A "found and fixed a bug" is not a
   retro; a retro explains WHY that class of bug was possible at all.
5. **The fix, verified not asserted.** If the fix can be demonstrated (a real adversarial test, a
   live re-run, a re-fetch), do it and quote the result. "Should be fixed now" is not a retro-grade
   claim.
6. **The class-level lesson (R10).** An absurdity-class or systemic defect may not be closed with an
   instance fix — extend the invariant library, a standing rule, or a mechanism (per MAKE_IT_STICK:
   mechanism, not memory) so the entire class fails automatically thereafter, or is structurally
   impossible.
7. **What was NOT lost / genuine scope of harm.** Distinguish "this was embarrassing" from "this
   corrupted data / leaked a secret / took an unauthorised external action" — don't let the retro's
   own narrative overstate or understate the real consequence.
8. **Follow-up, done inline if cheap.** If the retro's own lesson suggests an audit (e.g. "check
   every other caller of this pattern"), do that audit as part of writing the retro, not as a vague
   TODO — a follow-up left unstarted is exactly the kind of thing that recurs.

## When this produces a new R-rule

If the lesson is genuinely general (applies beyond this one incident), add it to CLAUDE.md as the
next `R<N>` — with a one-line reference back to the retro doc, not a full re-explanation. This is how
R1-R14 were produced; a retro that doesn't generalise into a rule was either too narrow to need one,
or the generalisation step was skipped and should be reconsidered before closing.
