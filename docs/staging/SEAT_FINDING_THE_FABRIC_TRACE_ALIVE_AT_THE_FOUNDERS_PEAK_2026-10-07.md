**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `founders-slope-trace-alive-at-peak`

# Is the fabric demand trace alive at the founders-only RSS peak?

Follows "Still open, handed on" in `SEAT_FINDING_THE_FOUNDERS_SLOPE_UNRETURNED_015_BY_TYPE_2026-10-07.md`
(`26b1122eb`). The question decides whether a trace layout that is returnable to the OS (above
512 bytes per year, so glibc rather than pymalloc) could move the *peak*, or only the residue after it.

## Disposition at draw (2026-10-07 23:45 BST)

The duplicate-work note named this id itself. `ps` showed one process holding it, this one, so the
"other writer" is the draw's own write. No rival probe was running. The earlier `alive40/160.json`
(22:55) answered a different question: at the RETURN of `run_phase2b`, 0 series and 0 arrays are
alive in both legs. They do not say when the peak falls.

## Pre-registration (written before either leg)

Instrument: `/var/tmp/scale-shape-ctl/ctl0_peak.py N OUT`, untraced, at `26b1122eb` (= origin/main).
A 0.5 s sampler thread logs RssAnon, VmSwap, series alive and day-arrays alive. Each
`FabricDemandSeries` goes into a WeakSet at construction (class `__new__`), and a finalizer stamps
its free. No `gc.get_objects()` and no id-set, so nothing in the instrument grows with the book
except the sample list.

**Definition.** "Alive at the peak" means the sample with the highest RssAnon + VmSwap has
`series_alive > 0`. RssAnon alone is not used, because swap is 97% full on this box and a page
swapped out leaves RssAnon. A second reading also counts: pymalloc keeps freed trace blocks as
slack, so a peak AFTER the free can still have been set by the trace. Therefore, record the anon+swap at
the last free too. If the later peak exceeds it by less than the trace's own size, the trace still
governs the peak.

Reading `run_phase2b`: `fabric_series_by_customer` is a local that the daily settlement loop reads
(line ~3592), and the records accumulate during that loop.

- **P1.** In both legs the series are alive at the anon+swap peak (`series_alive` = all built).
- **P2.** The peak sample falls before `phase2b_return`, and the last series is freed within 2 s
  of `phase2b_return` (it is a local, with no cycle).
- **P3.** anon+swap after the last free never exceeds the maximum while the series are alive by
  more than 10 MB in either leg.

**Void if:** no series are built; `alive_at_return` ≠ 0, which disagrees with `alive40/160.json`;
or the sampler's largest gap exceeds 3 s around the peak (a GIL-starved sampler cannot place it).

**Conditions not met:** `tools.run_value_cycle_ab` (another lane, 6.4 GB, started about 4 h
earlier) and a pytest gate were running. Neither is mine to stop. The question is about timing,
not level, so the legs run anyway, and swap is recorded so pressure can be seen.

Done means: P1–P3 graded in both legs, and a one-line verdict on whether a trace layout change can
move the peak.

**Instrument fault, fixed before any reading.** The first launch crashed at the first construction.
A frozen dataclass hashes its fields, and `WeakSet.add` hashed the object inside `__new__`, before
`__init__` had set them. The fix keeps an id-keyed dict of weakrefs. No sample was taken, so the
pre-registration stands unchanged.

## Result (`peak40.json` 89 s, `peak160.json` 342 s, `26b1122eb`, sequential)

| | 40 | 160 |
|---|---|---|
| series built / freed | 30 / 30 | 94 / 94 |
| book series alive through the loop | 21 | 60 |
| short-lived series (gas-fit build, freed before the loop) | 9 | 34 |
| last series built (s) | 37.9 | 88.9 |
| anon RSS when the build ends | 1,442.7 | 1,560.4 |
| **peak anon RSS (s, MB)** | **86.9 s, 1,527.5** | **334.2 s, 1,893.6** |
| series alive / day-arrays alive at the peak | **21 / 92,043** | **60 / 262,980** |
| last free (s) / `phase2b_return` (s) | 87.62 / 87.63 | 334.65 / 334.67 |
| max anon after the last free | 1,506.5 | 1,864.6 |
| swap at the peak | 0.0 | 0.0 |
| largest sampler gap | 0.66 s | 0.75 s |

Not void: series were built, `alive_at_return` = 0 in both legs (as `alive40/160.json` read), and
the sampler never went more than 0.75 s without a reading.

- **P1 holds, with one correction to its wording.** At the peak, every series the settlement loop
  reads is alive (21 and 60). "All built" was wrong: the gas-fit path
  (`build_fabric_series_for_site` at `run_phase2b` ~1582) builds further short-lived series, 9
  and 34, which are freed before the loop. The pre-registration did not know about them.
- **P2 holds.** The peak falls 0.7 s and 0.5 s before `run_phase2b` returns, and the last series is
  freed 0.01–0.02 s before the return. RSS climbs through the whole loop, because records
  accumulate, and the peak is the loop's last sample.
- **P3 holds.** After the free, RSS falls only 21 and 29 MB and never climbs again.

**The trace's own size at the peak:** each day-array is 464 bytes (`getsizeof(array('d', 48))`,
under 512, so pymalloc). That is 40.7 MB at 40 and 116.4 MB at 160, a slope of **0.227 MB/scy**.
This matches the 0.245 pymalloc slack that the residue finding attributed to the freed trace, so
that slack is the trace's own bytes, still resident.

## Verdict

**The trace is alive at the peak, and the peak is the end of the settlement loop.** Two
consequences for the next decision:

1. **A layout that only makes the trace *returnable* (above 512 B, so glibc) does not move the
   peak.** The free comes after the peak, by 0.5 s. Such a layout changes the post-peak residue and
   nothing else.
2. **A layout that makes the trace *smaller* moves the peak by the bytes it saves, at most 0.227
   MB/scy** (about 116 MB of 1,894 at 160 founders). The records' 0.57 MB/scy is the larger lever.
   A trace change is worth doing only if it is cheap. One example: float32 days (`array('f')`, 256
   B, so the 272 class) would save about 41% of the trace, about 0.09 MB/scy, if a half-hourly kWh
   holds at 7 significant figures. That is untested here.

A third option is untested and not costed: free each customer's trace once their last settlement
day has passed. The trace and the records would then stop peaking together. The loop runs by day
across all customers, though, so the trace stays alive to the window's end for every customer.
That makes this a restructure, not a tweak.

**Conditions:** `run_value_cycle_ab` (another lane, 6.4 GB) ran throughout. Swap read 0 at both
peaks, so pressure did not hide our pages. The timing reading does not depend on it.
