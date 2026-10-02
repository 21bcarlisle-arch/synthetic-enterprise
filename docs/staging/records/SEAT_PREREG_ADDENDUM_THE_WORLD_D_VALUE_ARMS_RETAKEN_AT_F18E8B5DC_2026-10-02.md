**Severity:** ADVISORY · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# Addendum to the world-D retake pre-registration: the run moved to `f18e8b5dc`

**Claim:** `publish-the-world-d-value-arms-retaken-at-0bac2b8be`
**Written 2026-10-02T05:10Z, about seven minutes after launch and before either run had written
output.** It amends
`SEAT_PREREG_THE_WORLD_D_VALUE_ARMS_RETAKEN_AT_HEAD_0BAC2B8BE_2026-10-02.md`. The 23:50Z stamp on
that file was really about 23:42Z. Both times are before any output.

## Why the original pair is not run

- `longjob-arms-d-head-1002` was **OOM-killed** at 00:41:39Z after 1h 0m. Its cgroup peak was 8G
  plus 1.0G of swap. It wrote nothing.
- 19 seconds later, `longjob-floor-d-head-1002-s123` was **refused by its own headroom check**. It
  needed 11,200 MB and only 8,277 MB was available. It left a stub at its out path that says
  `floor_run_refused: true`.

So neither artefact exists at `0bac2b8be`.

## Why the retake is at `f18e8b5dc` and not `0bac2b8be`

The two commits now at the top of origin, `cbe8d18a4` and `f18e8b5dc`, withdraw the current-world
headline and verdict whenever the arms or the floor ran code that differs from the publishing HEAD
in `simulation/` or `company/`. The only exception is a path argued in
`docs/design/value_arms_substrate_exemptions.json`, which is empty. Between `0bac2b8be` and
`f18e8b5dc` five such paths moved, across six commits (`1cd4b03dc`, `9cfb1817f`, `6aa3653d7`, `3b7a2ae19`,
`f243bd573`, `ed7e89d0e`). A retake at `0bac2b8be` would therefore be withdrawn on the page it
was meant to fill. One unit runs the same two 10-01 commands in sequence, from the locked clean
worktree `/var/tmp/wt-arms-retake-1002b` at `f18e8b5dc`:

- `longjob-arms-floor-d-head-1002b` (launched 05:03:26Z): first the three-arm run, then
  `--noise-floor-seeds 11111,22222,33333 --redraw-mode all`. The floor only starts if the arms exit
  0, so the two never hold memory at the same time. The out paths are
  `value_cycle_ab_s1_three_arm_20261002b.json` and `value_cycle_ab_s1_noise_floor_20261002b.json`.

## The predictions stand as written, with one note on P3

P0 to P4 are unchanged. The tree now also carries `9cfb1817f`, which takes a chosen fixed renewal
out of the price cap. That weakens P3's mechanism, "a binding cap clips the arm that prices
higher", for the fixed-renewal share of the book. **P3 is held weaker still**, and more than one
thing has changed, so a P3 miss cannot be attributed to any single commit. P0, P1, P2 and P4 are
signs or identities, and they are graded as written.

## Fallback, already in force

If this run also fails, the 10-05 publish does not carry the stale reading anyway. Regenerating
`site/data/value_arms.json` at `f18e8b5dc` today gives `why_the_headline_omits_it` = "the run
executed 0407ce0e3 and this page is published from f18e8b5dc; 16 path(s) … differ", and
`resolved: null` on all three legs. The item's "take the world-D reading off" is therefore done by
`cbe8d18a4` + `f18e8b5dc` at the next publish. In that case this pre-registration is graded "not
run".

## What the landing must expect (interconnection, not a prediction)

The run will finish around 09:30Z. Origin moves `simulation/` and `company/` several times a day.
By the time the paths move and the change publishes, HEAD will probably differ from `f18e8b5dc`
on some path, and the page will withdraw this run exactly as it withdraws the `0407ce0e3` run
today. There are two legal remedies, and both are recorded rather than assumed. One is an entry
in `docs/design/value_arms_substrate_exemptions.json` arguing why each changed path cannot move
the arms. The entry is keyed to run commit, path and head blob, so it is falsifiable. The other
is another retake. A path whose change reaches renewal pricing, churn, or the settled book cannot
be argued. Re-run instead.
