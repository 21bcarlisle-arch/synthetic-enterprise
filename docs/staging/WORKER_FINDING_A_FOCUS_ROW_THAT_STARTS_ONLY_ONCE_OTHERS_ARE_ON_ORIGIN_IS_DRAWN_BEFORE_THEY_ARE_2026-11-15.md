**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# A focus row that starts only once others are on origin is drawn before they are (2026-11-15)

**What happened.** The worker tick of 15 Nov drew `c32-tenth-blind-pass-grades-the-table-in-operation`.
Its first sentence is "Start only once W2_43, C36 and focus item 2 are all on origin". At draw time
only W2_43 was on origin (55faf525c, a6a354275):

- C36 was being built in `/var/tmp/se-seat-executor` (pid 1355301, 19 minutes in, with
  `collections_journey.py` and `sim_interface.py` modified).
- `the-company-can-stop-recovery-through-the-meter` is queued behind C36. The draw itself refused
  it on that holder in the same doorbell.
- `recovery_through_the_meter` is still unrouted on origin (`company/billing/winter_moratorium.py:576`).

So the tick read the condition, did not run the pass, and spent its turn finding that out. The pass
was not run because the item's own WHY says a pass run early "re-finds them at an hour's cost".

**Why it will recur.** The draw honours two embargo grammars (`background/delivery_lane.py`
`_EMBARGO` and `_EMBARGO_PATH`): a dated time, or an absolute path existing. Neither can express
"after these ids land", so the row is drawable now. The claim is swept back in 100 minutes, so
every tick until C36 and the meter door land can draw it again, and each one re-derives this.

**Recommendation (seat).** At the next orientation, either drop the row from focus until both
predecessors are on origin, or reword its start as a grammar the draw reads. A third embargo form,
`DO NOT DRAW BEFORE <commit-ish or id> IS ON ORIGIN`, would be the general fix. It belongs in
`delivery_lane` beside `_EMBARGO_PATH`, with a control that the row is refused while the id is
off origin and drawn once it is on. I did not build it: it is the seat's draw, and dropping the
row is the smaller move.

**Also this tick.** The advisor channel's refusal of the 15 Nov usage-efficiency steer was false.
His words were in a `>` blockquote under a timed lead-in, and the guard accepted only `-`/`*`
bullets. The guard is fixed with a test, and the steer stays in staging, not done/.
