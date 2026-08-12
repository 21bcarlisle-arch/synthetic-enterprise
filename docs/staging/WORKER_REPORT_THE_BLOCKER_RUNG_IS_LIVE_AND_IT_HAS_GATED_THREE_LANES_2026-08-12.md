# WORKER REPORT — the blocker rung is live, and its first act was to gate three lanes

**Date:** 2026-08-12
**Atom:** `OPS12_blockers_ahead_of_disposition` — level 0 → 2, `loop_stage` build → harden
**Commits:** `0a392bc28` (mechanism + tests), `e5290ac4c` (map cell + ledger row). Pushed; `origin/main` at `e5290ac4c`.

## What landed

RUNG 1c in `background/supervisor.py`. `_blocking_lane_draw()` reads OPS9's severity parse
(`background.finding_severity.blocking_by_lane` over the real staging root) and returns
`(reason, blocked_lanes)`. `_self_refill_draw` filters the BUILD, SITE and DISCOVERY candidate
lists by `blocked_lanes` — same-lane only — and prepends the reason to whatever the cycle draws;
where a blocker excluded everything else, it returns alone rather than falling through to the
campaign/backlog/forward-discovery rungs. `_is_drained_and_gated` mirrors it, so rest cannot be
declared beside a live blocker.

Against the atom's own five exit criteria:

1. **Ordering read from the OPS9 parse, not a second list** — the module import is the only source; there is no hand-kept register to drift from it.
2. **NON-BLOCKING ELSEWHERE** — the filter is `a.get("lane") not in blocked_lanes`; another lane's draw is untouched in the same cycle.
3. **The reason names the blocker** — filenames are in the returned string, not only the log, so a queue-jumping tick is auditable from the reason alone.
4. **R15 both ways** — `tests/background/test_supervisor_blocker_precedence.py`, 10 passed. `test_a_blocked_lane_atom_is_excluded_from_the_draw` dies on a mutation restoring arrival/recency order; `test_an_unblocked_lane_atom_still_draws_the_same_cycle` dies on one letting a blocker starve every other lane.
5. **Fail-open is visible** — an unreadable index returns a reason that *says* the index was unreadable with an **empty** `blocked_lanes`, so the ordinary draw order resumes but never silently. A `None` on both paths would have been exactly the silent fallback the criterion forbids, which is why the two cases are distinguishable.

It was already running from the working tree when this tick was woken — the doorbell that drew
this work was produced by the rung itself. What was missing was the landing: the mechanism and
its ten tests were uncommitted and untracked. They are committed now.

## The consequence, stated plainly

Over the live staging root (88 findings parsed): **17 BLOCKING**, 52 LATENT, 19 RECORDED.
The blocking ones sit in three lanes:

| lane | live BLOCKING findings |
|---|---|
| `H_harness` | 15 |
| `W2_customer_generator` | 1 |
| `W4_the_wall` | 1 |

Until those are dispositioned, **BUILD/SITE/DISCOVERY draws in those three lanes are excluded**
and the blocking findings draw in their place. Every other lane is unaffected — that is the
"drain proceeds around it" half, and it is tested.

A narrowed draw in `H_harness` over the coming ticks is therefore the rung working, not a
draw-blindness defect. The way out is disposition of the 17, not a dial.

## What this report does not claim

The 17 have not been triaged for whether each *deserves* BLOCKING. The severity field is OPS9's
parse of what each document declares about itself; this atom consumes that judgement and does not
second-guess it. If a document is over-declared, the fix is in the document, and it will show up
as a lane that stays gated on something that turned out not to be broken.
