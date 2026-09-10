**Severity:** RECORDED · **Lane:** H_harness

# The seat's replies — verbatim record, 2026-09-09

> **These are the DELIVERY SEAT's words, not the director's.** The companion file
> `DIRECTOR_CONSOLE_2026-09-09.md` holds what he typed; this holds what was said back, so a
> reader arriving at an instruction can see the answer without waiting for a stretch
> report to close. Director, 2026-09-07: *"it records what I send and not what you reply
> ... between the two there's a window where my advisor can see the instruction and not
> the answer."*
>
> **Nothing here carries the director's authority.** It is kept under a separate name for
> exactly that reason: the release door reads `DIRECTOR_CONSOLE_*` as his own words, and
> a reply filed under that prefix would be the machine speaking with his voice.

### 2026-09-09T04:33:19.472Z

> Decisions made, measured, and built to. Both of your questions have answers that changed what I was doing.
>
> ## Where the two jobs got to
>
> **Both finished successfully, hours ago.** `rc=0` on each — temperature 156/156 cells complete, wind/cloud 138/156 (the tail hit quota). 57 MB and 46 MB on disk. They completed and I never looked. The mechanism I built doesn't cover them because they were scratch scripts, which is precisely your point about the verdict needing to be somewhere you read.
>
> ## Do we need whole-country grids?
>
> **We needed them once, and the answer isn't the one I expected.** ERA5 against HadUK at the same cells, like for like:
>
> | site | midpoint bias | |
> |---|---:|---|
> | London | **+1.18 °C** | |
> | Manchester | **+1.26 °C** | |
> | Glasgow | **+1.33 °C** | |
> | Cotswolds (rural) | **+0.22 °C** | |
>
> Warm in three cities, flat in the countryside — that's the **urban heat island**, which a 9–31 km reanalysis cannot resolve and a 1 km observational product can. Through a real house it's ~1,800 kWh/year, about 22% of urban space heat, all in the direction of over-predicting.
>
> So the grids bought something real. But they're an **intermediate we don't keep** — they live outside the repo and are now disposable. We should not download nationally again: CEDA's THREDDS answers 403 rather than 404, so a subsetting service exists behind different auth, and establishing that is the route before any future extension.
>
> I also nearly reported a false disagreement — HadUK's `tas` is exactly `(tmin+tmax)/2` while Open-Meteo's is a true 24-hour mean. I caught that and redid it like-for-like; the bias survived, so it's real.
>
> ## 156 cell-series or 20 regime-series?
>
> **Twenty, decisively.** Annual space-heat error against the true per-cell series:
>
> | regimes | mean | worst cell |
> |---:|---:|---:|
> | 1 | 0.46% | 1.80% |
> | 5 | 0.18% | 0.74% |
> | **20** | **0.10%** | **0.55%** |
>
> And the decomposition is the thing: **per-cell level + shared regime anomaly.** The urban heat island is a *scalar per cell* — 156 numbers, not 156 series — so 1 km fidelity survives at negligible cost.
>
> The store is built: **1.1 MB**, 20 series serving 156 cells, reconstructing them to 0.34 °C mean / 0.62 °C worst. It also closes the 18-cell wind gap for free, since a cell without its own wind reads its regime's.
>
> That's the shape the generative case needs, arrived at from the replay side.
>
> ## The three things from outside
>
> Not yet touched — the site not publishing since Monday, the merge re-derivation not catching derived-file collisions, and 35 red tests at HEAD. Those are next, and the reds are almost certainly why the site is stuck. I'll also put the `long_job` verdict where you read it rather than where I have to be asked for it.

### 2026-09-09T05:02:11.343Z

> Twenty regimes is settled for the annual and **not** for the tail — you were right to push.
>
> ## At the extremes
>
> | | bias | worst cell |
> |---|---:|---:|
> | peak half-hour | −0.54% | **−2.08%** |
> | **peak day** | −0.75% | **−8.41%** |
> | annual | −0.32% | −2.39% |
>
> Peak half-hour holds because the boiler saturates — temperature error doesn't propagate to the half-hourly maximum. The peak day doesn't, and the bias is toward **understatement**, which is the wrong direction for a hedge.
>
> Against regime count, on each cell's own coldest day:
>
> | regimes | worst | cells >5% |
> |---:|---:|---:|
> | 20 | −6.77% | 3 |
> | 40 | −4.68% | 0 |
> | 80 | −1.75% | 0 |
>
> **Your split was right: twenty for level, more for extremes — about 60–80.**
>
> But that changed the decision. Under replay, 156 exact cell-series is **7.8 MB**, so there's no reason to accept 8% on a hedging day to save seven megabytes. The store now holds the cells exactly (worst error 0.0000 °C); the regime indirection stays because *generation* needs it, and the measured number a generator needs is 60–80, not the 20 the annual figure suggested.
>
> **One real defect found on the way:** `premise_trace` refused to run, because 310 cell-days had `tmin > tmax`. That's in HadUK itself — it interpolates the three fields independently, so on low-diurnal-range days the surfaces cross. Median inversion 0.25 °C against a normal 6.31 °C range. They're swapped rather than clamped, because `tas` is exactly their midpoint and swapping preserves that.
>
> ## The site
>
> Not a fork condition and not a red test — the publisher's suite was green every time. Five links:
>
> **Archived document → broken citation → red control → control never committed → atom claims a level with no evidence in git → level gate refuses → site stops.**
>
> A document being *filed correctly* broke a citation. The fix is the citation; the debt row stays, because its blocker is still live. Landing now.
>
> The symptom pointed nowhere useful: `blocking_tests: []`, `cause: non_test_gate_refusal` — honest and unhelpful. The refusing gate names its reason in `sim-runner-log.md` and nothing surfaces that where the publish state is read. Same class as the pull that reported success by default.
>
> Still open: the clean-HEAD red census (running), the merge re-derivation not catching derived-file collisions, and putting the `long_job` verdict where you read it.
