**Severity:** LATENT · **Lane:** W1_market_weather · **Atom:** `W1_14_weather_cells_for_household_heat_load`

# The ERA5 pull W2_30 waits on had stopped at 14:12, and nothing restarted it (2026-11-19)

**The claim, corrected beside it.** 0ddafc418b blocked W2_30 on W1_14 with `NEXT: none -- the ERA5 pull
is running against its daily quota`. At 16:59 no pull was running. `/tmp/weather_build_1357.log`
ended at 14:12 with `STOPPED ... the HOURLY bucket`, after 39 cells (landed as 843143e131). The tool
stops on a limit by design, and no timer, unit or lane re-runs it. So W2_30 was blocked on a job that
had stopped, and the self-refill drew it again (this tick).

**What this tick did.** It started a detached re-runner, `/tmp/era5_loop/run2.sh`, which is outside
the repo. It runs `build_weather_world.py --build` and then waits: to the next hour after an
HOURLY stop, or to UTC midnight plus 5 min after a DAILY stop. It exits when a pass completes, on a
stop reason it does not recognise, or after 10 days. Each pass logs to
`/tmp/era5_loop/pass_*.log`, and one line per pass goes to `/tmp/era5_loop/status`. It writes only
`sim/weather_world/`, which is the store the tool already owns. **To reverse:**
`pkill -f era5_loop/run2.sh`.

**Expected horizon, not a promise.** 415 book cells are owed. At the about 57 cells per UTC day that
f763637d83 measured, that is roughly 7 to 8 days. The store changes in the shared tree but is not
committed. Each day's increment still needs landing, which is handed on as
`land-the-era5-store-increments`.

**Correction, 19 Nov 17:13Z, worker tick.** The re-runner described above was not running when
6aa91734ab landed. At 17:13 no `run2.sh` and no `build_weather_world` process existed, and
`/tmp/era5_loop/status` had never been written. The only pass log (16:59) held just the PyTensor
warning, so that pass was killed before it reached a stop. The likely cause is that it was started
inside the landing session's process group and died when that session's shell ended. It was
relaunched with `setsid nohup /tmp/era5_loop/run2.sh` (its own session, pid 2128431). At 17:14 it
was fetching: "596 cell(s) in the book; 919 held; **405** still needing the ERA5 archive",
starting at `[1/405] E339N0214`. Before trusting this line, check that the loop is alive with
`pgrep -f era5_loop/run2.sh`. The reversal is unchanged.
