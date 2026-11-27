**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: the 7,700 cy point re-measured at origin, and the bisect it triggers (2026-11-27)

Written BEFORE the measurement. The run has not started: at 13:33Z it sits in the long-job
admission queue. Work id `production-memory-growth-is-attributed`. The decision it feeds is the
director's row `your-20-oct-stop-rule-fired-production` (`docs/direction/DIRECTION.yaml`): R8
streaming or R6 index-once cannot be chosen until the growth is attributed. Measure only. Build
nothing.

## 1. The reference point

`docs/observability/settlement_ceiling_slope_20261025.json`, point `budget 7700`: **5,555.9 MB**
peak child RSS (`ru_maxrss`), 7,699.3 cy committed, 205 wins, 3,566.9 s, clean. Code `7a692b47ae`
(origin, 25 Oct 14:57Z), `founder_unit: households`, 400 founder homes.

## 2. The run (already queued by an earlier tick of this item; not re-launched)

- Unit `longjob-memgrowth-7700-origin-9176b1c0b3`, queued 11:48Z 27 Nov.
- Worktree `/var/tmp/se-memgrowth-probe-20261127` at `9176b1c0b3` (origin, 27 Nov 11:40Z).
  The one edit is `founder_unit: supply_points -> households` in `docs/design/FOUNDER_BOOK.yaml`.
  That restores the 25 Oct shape, which `311939bb7e` reverted on 27 Nov. Between `7a692b47ae` and
  `9176b1c0b3`, `FOUNDER_BOOK.yaml` changed only in that revert, and the budget constant changed
  only in that revert. The probe passes the budget itself (`--budgets 7700`).
- Command: `python3 -m tools.settlement_ceiling_probe --budgets 7700 --force --json
  /var/tmp/se-memgrowth-out/point_7700_origin.json`. This is the same instrument and the same
  live-path compute as the 25 Oct point.
- Artefact: `/var/tmp/se-memgrowth-out/point_7700_origin.json`.
- Origin has moved past `9176b1c0b3` to `c9b9979659`. No file under `simulation/ sim/ company/
  saas/` changed in between, so the point still measures today's runtime code.

## 3. The prior, taken from the record and not a measurement

Production's own peaks (sim-runner journal, `/var/tmp/se-memgrowth-out/journal_peaks.txt`). These
were runs at households and 7,700, but their committed cy was NOT read:

| Window | Peaks (MB) | Centre |
|---|---|---|
| 25 Oct (probe vs. production) | 5,555.9 / 5,595.3 | ~5,575 |
| 16-20 Nov (7 runs) | 5,637-5,894 | ~5,880 |
| 24-27 Nov (8 runs) | 5,920-6,524 | ~6,050 |

The record points to two rises: about +300 MB somewhere between 25 Oct and 16 Nov, and about
+170 MB between `6a588a832f` (20 Nov 13:29Z) and `f2c6979d01` (24 Nov 21:58Z). The second window
holds 384 commits, 52 of which touch `simulation/ sim/ company/ saas/`. The two 6,2xx-6,5xx peaks
(`2100f84f85`, `601887d76a`) sit outside both bands. They may not be code at all.

**Prediction:** the re-measured point lands at 6,050 MB ± 150. That is a gap of about +500 MB, so
the bisect fires, and the prediction is that it ends as a **spread** (no single commit carries
half the gap), with the 20-24 Nov window holding the largest single step. If the gap comes back
under 300 MB, the prediction is wrong in a useful direction: production's growth would then be in
its inputs (book, swap, co-residency), not in the code at this shape.

## 4. Decision rule (fixed now)

Noise is taken as ±50 MB. The basis: the 25 Oct probe and production at the same code agreed to
40 MB. No repeat at the same code has ever been run, and that is a stated assumption.

1. **Gap = new − 5,555.9.** If gap < 300 MB, there is no bisect. The finding reads "not the code
   at this shape", gives the MB, and the director's row cites it.
2. **Gap ≥ 300 MB.** Bisect over first-parent origin commits `7a692b47ae..9176b1c0b3`, measuring
   each step with the same command in a fresh worktree carrying the same one-word edit. A step is
   "high" if its peak is above the midpoint (5,555.9 + new) / 2, and "low" otherwise. Each step is
   its own long job, waited on with `tools/wait_for.py` and a deadline of 3 h (2× the 75-minute
   expectation). The range is 1,568 first-parent commits, so about 11 steps, or roughly 14 h of
   runs. Each step is handed on as a gated continuation, never waited on inside a turn.
3. **The verdict at the end of the bisect.** Take the adjacent pair (L, H) and their delta
   d = H − L.
   - d ≥ 0.5 × gap: **that commit carries the step**, named with its MB.
   - Otherwise: **spread**. The bisect's own points are published as a curve over commit dates,
     with the windows that carry the most named. Measuring more points does not turn a spread
     into a commit.
4. A step whose run is unclean (`clean: false`, exit ≠ 0, or committed cy outside 7,650-7,700)
   is re-run once. A second unclean run stops the bisect, and the finding reports that.
5. Nothing in this pre-registration moves the budget, the unit or the 0.25 share. Building the
   fix stays behind the director's row.

## 5. Where the answer goes

A finding at `docs/staging/SEAT_FINDING_<...>_2026-11-2x.md`, carrying the commit or the spread
and the measured MB. Its path and figures are appended to the `evidence` field of
`your-20-oct-stop-rule-fired-production`, and to nothing else on that row.
