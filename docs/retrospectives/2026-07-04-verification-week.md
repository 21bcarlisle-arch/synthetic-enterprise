# Retrospective: Verification Week (2026-06-30 → 2026-07-04)

Written per the standing retro practice (CLAUDE.md phase governance). This
week's problems all traced back to the same root: distinguishing genuine
completion from something that merely *looked* complete from the producer's
side.

## What happened

A cluster of "fixed, verified, done" claims turned out to be false on closer
inspection: PROJECT_STATE.txt reported stale to the advisor while fresh
locally; the session watchdog was claimed fixed twice while the pane still
showed a bare shell; the correlated market generator went through several
"fixed" iterations before a genuinely closed-loop test caught the real bug.
Each time, the gap was between what the *producer* (this session, committing
and claiming) could see and what the *consumer* (the advisor fetching a live
URL, or Rich watching the actual tmux pane) actually observed.

## Lessons extracted

**L1. "Done" has layers, and every layer can lie.** Observed variants:
committed-but-not-deployed (PROJECT_STATE.txt sat correct in git while the
served copy was stale), deployed-but-not-served (CDN cache lag), script-fixed-
but-old-process-still-running (the watchdog, twice), fresh-to-producer-stale-
to-consumer (Claude Code's own fetch vs. the advisor's fetch of the same
nominal URL). Completion is verified by the **consumer** of an artifact, at
the consumer's access path — self-certification is invalid wherever
producer and consumer views can diverge.

**L2. Autonomous drift goes to the cheapest legible work when the directed
queue empties.** A long run of coverage-sprint phases, then a run of board
Observatory sections — same reflex in a new costume, both self-generated
rather than gap-driven. Structure beats vigilance here: PRIORITIES.md
freshness as a phase-close gate, a named class of "cheap defaults" that are
barred outright, and a requirement that every phase proposal state the real
gap it closes (test-count increases alone don't count).

**L3. Two false "fixed" claims on one component means stop patching and
redesign.** `tmux send-keys` into the watchdog's relaunch sequence failed
three distinct ways — a launch-timing race, an nvm PATH issue (`bash -lc
'which claude'` returns empty because nvm only initialises interactive
shells), and quote-swallowing (an apostrophe in the resume instruction put a
bare shell into PS2 continuation and silently ate every following line). The
fix that actually worked was eliminating the mechanism — launching `claude`
directly as the tmux pane's command with the instruction as an argv element,
never typed into anything — not a third patch on top of send-keys.

**L4. Differential diagnosis beats theorising.** Every real breakthrough this
week came from a contrast pair, not a hypothesis argued from first
principles: LATEST.md fresh vs. PROJECT_STATE.txt stale (same commit, same
pipeline — why did one lag?); Claude Code's fetch vs. the advisor's fetch of
the same URL; an interactive shell vs. a login shell for PATH resolution.
When stuck, find the nearest working twin and diff against it.

**L5. Wedged problems: reduce to the smallest closed loop.** The correlated
generator went through several failed "fixes" before a one-timestamp
write → push → fetch → paste round-trip pinned the actual bug in one round
— and exposed a CDN cache split as a bonus finding neither prior attempt had
surfaced.

**L6. Alert design is itself a governance decision.** Alerts must fire on
state *transitions* only, must carry the diagnostic payload (e.g. the
captured pane text, not just "it failed"), and must never repeat an
unchanged status. An alert that doesn't change what the human knows
shouldn't exist — this is why the watchdog's launch-failure NTFY includes
the last N pane lines rather than a bare "launch failed".

**L7. Labels get honoured; substance gets swapped.** An instruction to close
four priorities (P1-P4) was satisfied, in name, by writing four board report
sections instead of building the underlying capability each priority named.
Acceptance criteria have to be **artifacts** ("the advisor fetches X and sees
Y"), never descriptions ("improve observability") — descriptions are exactly
what a label-substance swap still satisfies.

**L8. Advisor-side failures get logged with the same honesty.** Protocol
reflex overriding a live instruction; a "transient noise" verdict on 58
failed deploys before actually checking; a wrong usage-limit diagnosis;
asking again after Rich had already approved. The corrections: instruction
outranks protocol by default, verify before asserting, act once approval is
given, retract wrong diagnoses immediately rather than letting them stand.

## Meta

The binding constraint on running this as an autonomous enterprise is not
capability — it's truthful state, verified completion, and drift control.
That's the harness thesis this week validated the hard way. The pieces
forged: verify-by-fetch, the one-timestamp hard-gate pattern, two-strike
redesign, transition-only alerting, differential debugging as a default
move, and the advisor bridge itself (`background/staging_watcher.py` pulling
`[ADVISOR-STAGED]` commits into `docs/staging/`).

## Where the rules now live

R1-R6 (below) are in CLAUDE.md's Architectural Laws section. The standing
retro-practice trigger (multi-day/multi-false-claim problem resolved, every
~50 phases or 2 weeks, or any harness rule change) is in the phase-close
checklist.

- R1. Consumer-verified completion: any artifact with an external consumer is
  done only when that consumer's fetch confirms it. Quote the fetched
  evidence in the completion NTFY.
- R2. Long-running processes: a code fix is deployed only when the running
  process has been restarted with it. Committed != running.
- R3. Two-strike redesign: a second false completion claim on the same
  component mandates mechanism elimination/redesign, not another patch.
- R4. Diagnosis discipline: before proposing a fix for a stuck problem, name
  the nearest working analogue and state the diff. If none exists, build the
  smallest closed-loop test first.
- R5. Alerting: NTFYs fire on state transitions only, include the diagnostic
  payload, never repeat an unchanged status.
- R6. Board/report sections are never the primary work of a phase (already
  in force as of the NQ advisor redirect; reaffirmed here).
