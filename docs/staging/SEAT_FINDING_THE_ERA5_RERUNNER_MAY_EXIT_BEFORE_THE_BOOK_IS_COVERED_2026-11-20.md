**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** `W1_14_weather_cells_for_household_heat_load`

# The ERA5 re-runner may stop before the book's cells are covered

`/tmp/era5_loop/run2.sh` stops on its own after 10 days: `deadline=$(( start + 10*86400 ))`. The current
runner (`era5-rerunner.service`) started at 17:25Z on 19 Nov, so it exits at 17:25Z on 29 Nov. That
leaves ten daily passes, 20 Nov to 29 Nov.

**The cells:** 381 of the 596 book cells still need the ERA5 archive after this landing. The first
checkpoint of the 20 Nov 00:05Z pass is landed here; it added 20 cells (R163 to R197). The pass fetches
about one cell a minute. The day before, a pass that started after part of the quota was gone added 14.

**Ten passes cover 381 cells only if each pass averages at least 38 cells.** The first pass on a full
day's quota is still running, so I do not know its yield yet.

**Prediction, written at 00:35Z before that pass ends:** I cannot say whether it will reach 38 cells. If
it ends below 38, the deadline is the binding limit. The fix is to restart the runner with a longer
deadline. It is reversible (`systemctl --user stop era5-rerunner`) and needs nobody's word. If it ends at
38 or more, the deadline does not bind and nothing changes. Whoever draws the next landing reads the
count against this line.

## Correction, 00:45Z on 20 Nov: "ten passes" was wrong

The 00:05Z pass ended at 00:34Z on the **hourly** bucket, not on the daily quota. It added 32 cells, and
the last 12 (R199 to R215) are landed beside this correction. `run2.sh` re-runs at the top of each hour
after an hourly stop. So a day is up to about 24 passes until the daily quota stops it, not one pass.
The ten things left before the deadline are days, not passes.

369 cells are owed. Ten days cover them if each day averages 37 or more. The first hour of today alone
added 32. The deadline therefore binds only if the daily quota cuts each day off soon after its first
hour. That cut-off is still unknown: 19 Nov's daily stop came after a day already partly used. The test
stays the same: read today's total when its "stopped daily" line appears in `/tmp/era5_loop/status`.
At 37 or more, close this finding as not binding.
