# Two director questions the incident begs (QUEUE — steers on existing atoms, not new work)

**Staged:** 2026-07-14 by advisor, relaying the DIRECTOR'S two questions verbatim:
*"Why was it firing /usage? Why isn't the naive organ asking these questions?"*
Both are findings. Answer them with evidence and fold the fixes into the atoms
already in flight (H16 injection class, H11 naive organ). Moratorium note:
below-target fell (49->34), and these are steers on EXISTING atoms.

## Q1 — WHY does a watchdog TYPE /usage into the director's input box?
Advisor's inference (verify it): the session_watchdog polls /usage to
anticipate session/usage limits for its auto-resume function. If so, the design
smell is deeper than the missing gate: **it READS by WRITING — using the
interactive input box as an API.** The doorbell may genuinely need send-keys
(waking a session requires input); **usage polling does not.** Alternatives to
evaluate: passive pane capture (the statusline already shows usage/context),
reading whatever local state Claude Code exposes, or simply detecting the
limit-reached message when it appears. **Requirement: eliminate the /usage
WRITE entirely, not merely gate it.** A robot that must type into the human's
keyboard to ask a question is one bug away from doing exactly what it did.
Report what the watchdog actually needed the number for, and the read-only
mechanism that now supplies it.

## Q2 — WHY didn't the naive organ ask any of this? (two structural gaps)
1. **It is wake-coupled to the system it doubts.** H11 fires on PUBLISH cycles.
   During the blackout there were no publishes — so **the outside view shared
   the inside's heartbeat and died with it.** An independent skeptic on a
   dependent clock is not independent. **Fix: the naive organ runs on its own
   WALL-CLOCK schedule (cron), not on the system's events.** It must be able to
   fire when the system is silent — especially then.
2. **Silence is not in its trigger set.** All seven triggers fire on CLAIMS
   (false health, terminal states, inherence...). This failure was the system
   saying NOTHING. **Add trigger #8: EXPECTED OUTPUT ABSENT** — no commit, no
   digest, no publish inside the normal cadence -> the organ independently
   checks raw state and asks "why is it quiet?" (This overlaps the new deadman
   deliberately: the deadman ALARMS, the organ QUESTIONS — and after a
   fail-silent deadman, one more independent pair of eyes on liveness is cheap.)
3. Meta (already its task, now with a worked example): the organ could not
   question its own coupling. Add this incident to its self-audit: "which
   doubt mechanisms share a failure domain with what they monitor?" The deadman
   refreshing its own clock and the organ waking on the pipeline it audits are
   the SAME defect in two organs.

## DoD
/usage write eliminated (read-only mechanism named and tested); naive organ on
an independent wall-clock with trigger #8 live, mutation-tested against THIS
outage (silent 6h -> organ fires); the shared-failure-domain audit run across
all doubt machinery with results published. One digest line.
