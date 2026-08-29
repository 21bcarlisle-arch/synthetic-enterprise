# The settlement ceiling, re-measured: its evidence has drifted, its time bound is circular, and I do not yet have the number

**Direction, 2026-08-29 (LANE 0 DELIVERY):** *"Re-run AO12's probe on this machine, at the run
shape the live path actually uses… Then set the ceiling from what the probe supports… if the probe
says 1200 is right, say so and the finding is that the ceiling is real, which is a different and
equally useful answer."*

**This is neither of those answers.** The probe ran, one point is clean, and it says the ceiling's
recorded cost is **36% wrong in wall clock and 35% wrong in memory** at its own budget. The second
point was contaminated by a defect in my own probe, which I caught because two of its fields
disagreed, and a slope needs two clean points. **The ceiling therefore does not move in this
commit, and the reason is stated rather than the number guessed.**

The instrument is `tools/settlement_ceiling_probe.py`. It is re-runnable, and the run that would
settle this is specified in §6.

---

## 1. The premise the direction was given had already expired, twice over

The direction says *"its own note says it is 60% of the 465 measured in AO12's scale probe — so the
ceiling has provenance, and the question is whether that provenance is still true."*

**The module's own note has said the opposite since 2026-08-24**, in the constant's header:
*"SET FROM WALL CLOCK, MEASURED, 2026-08-24 — not from the scale probe any more, and the correction
matters."* The scale-probe derivation was retired five days ago because it priced profile-class
households at the half-hourly settlement rate.

**But the note a READER sees still said it**, and that is the part that mattered. The string in
`plan_growth_campaign` — rendered into `book_growth_campaign.json` and onto the published
book-growth page, ten times in the live run — read:

> *1200.0 customer-years is THIS MACHINE's budget (60% of the 465 measured in AO12's scale probe)*

**60% of 465 is 279.** That was the constant's value when the string was written. It survived
279 → 600 → 1200 untouched, so by the time the direction quoted it the parenthetical was wrong
about its method AND arithmetically false about its own subject. The direction was reading the
project's own published note back to it, which is exactly what a published note is for; the note
was the thing that was broken.

Fixed in this commit, and the comment above it names the class rather than the instance: **a
citation duplicated between a comment and a rendered string has two half-lives, and only one of
them has a reader who would notice.** The rendered one now cites the artefact path, so the next
correction lands where it is read.

## 2. What was measured

One child process per budget, running the live path's own compute —
`tools.run_annual_report._run_and_extract(report_end=None)`, the same call
`background/sim_runner.py` makes, full 2016–2025 window, **not** `--fast`. Wall clock and peak RSS
are taken parent-side (`os.wait4`'s `ru_maxrss`); the campaign figures are read in-process.

| | 2026-08-24, recorded in the constant | **2026-08-29, measured** | move |
|---|---|---|---|
| budget | 1,200 | 1,200 | — |
| customer-years actually committed | 796.1 | **1,200.0** | +51% |
| wall clock | 746.8s (12.4 min) | **1,018.7s (17.0 min)** | **+36%** |
| peak RSS | 3,117 MB | **4,193 MB** | **+35%** |
| wins booked / funnel wins | — | 46 / 386 | — |
| wins refused by this ceiling | — | **340** | — |

Guest at the time of measurement: `total_mb` 24,032.1, `available_mb` 10,786–12,943 across the run,
`oom_kills_total` 157 and unmoved by the probe. Read these live —
`background.resource_headroom.sample()` — never from this table.

**The drift is not a surprise once stated: the founder book made the ceiling actually bind.** In
August the 1,200 budget was a ceiling the campaign never reached (it committed 796.1). Today the
campaign spends 1,199.9 of it and is `settlement_engine`-bound in nine of ten years. The constant
did not change; **what changed is that it went from slack to taut, and its cost note was measured
while it was slack.** That is the answer to "is the provenance still true": no, and it stopped
being true the day the founder book landed, without anything reporting it.

## 3. The time bound the ceiling is argued against is circular

The constant reasons: *"12.4 minutes leaves seventeen for the publisher's gate inside the half-hour
cycle."* Two things are wrong with that sentence and the second is structural.

**The cadence is 1,500s, not 1,800s.** It was re-measured 2026-08-26 — two days *after* the ceiling
note was written — and the ceiling note was never revisited.

**And the cadence cannot bound this ceiling, because the ceiling sets the cadence.**
`background/suite_duration_watch.PUBLISH_CADENCE_SECONDS` says so in its own comment: *"it is not a
budget anyone chose; it is a measurement of how often runs actually arrive"* — the median
inter-arrival of `run_complete_*` markers. Run duration is what sets marker inter-arrival. So:

> raise the ceiling → the run gets slower → markers arrive further apart → the *measured cadence*
> rises → the allowance a ceiling "argued against the cadence" is checked against gets bigger.

The quantity moves with the answer, and it moves in the flattering direction. It is the same shape
as a variance evaluated at the estimate, and it has a second edge: **a slower run silences the
gate-speed alarm**, because `absolute_band()` asks whether the gate is faster than the interval
between runs, and lengthening the run widens that interval. A settlement ceiling that raises itself
past its own alarm is not a ceiling.

`recommend()` in the probe therefore treats time as a **chosen** publish interval, passed in and
named, and marks the bound `chosen: false` when nobody chose one. **Memory is the only bound here
that is evidence** — the guest's size is a fact this process cannot influence, and
`oom_kills_total` is the record of what happens when a run exceeds it.

## 4. My own probe manufactured a false finding, and here is how it was caught

The 2,000-budget point reported `customer_years_committed = 1199.9, wins = 45, refused = 335` —
**byte-identical to the live 1,200-budget record.** The probe's own verdict was coherent and
publishable: *"the funnel, not the ceiling, is what bounds this range."* It was false.

The tell was that the same point's wall clock and peak RSS had **more than doubled** — 2,223.6s and
7,322.7 MB. A 2,000 ceiling cannot book fewer accounts than a 1,200 one while costing twice as much
to settle. **Two of one run's own fields disagreed, and only one of them was wrong.**

The mechanism: the child read the campaign back from
`docs/observability/book_growth_campaign.json`. `live_population._resolve_campaign` writes that path
on an **absolute** path from every process that assembles a book, and the live producer assembles
one every ~25 minutes. Producer pid 3859950 wrote it mid-run and the probe adopted the producer's
book as its own result.

**Ask who WRITES each side.** The fix is to read `LAST_CAMPAIGN` in-process, where no other writer
can reach, and to keep comparing the file so a future divergence is *reported* rather than adopted
(`campaign_record_agrees`). Two further guards landed with it:

* the child records whether a producer was in flight at **start and end** — the parent's guard only
  checked before a point began, and a producer arriving mid-run was exactly the case that happened;
* `cleanliness()` fails **closed**: a point carrying none of these fields is unclean with
  `reason: not recorded`, never clean by default. Both recorded points were re-judged under it.

The two existing points are annotated in the artefact with `annotation_provenance` saying plainly
that the contamination fields were added by investigation afterwards and what evidence established
each — including the positive evidence that the 1,200 point is clean: **its figures (1200.0 / 46 /
340) differ from the live record's (1199.9 / 45 / 335)**, which is how you can tell it read its own
campaign.

## 5. What this does NOT change, said because the direction asked for these three numbers

The ceiling did not move, so **nothing downstream of it moved**, and reporting movement here would
be reporting the noise of a re-run:

| | before | after this commit |
|---|---|---|
| gradable ladder population (`slopes.common_population`) | **16** | **16, unchanged** |
| R6 headroom to the first collateral demand | **£316,009** | **£316,009, unchanged** |
| published net figure | £164,542 | unchanged |

One thing worth recording ahead of the re-run, because it is a bound the ceiling lift will *not*
lift: the ladder's 16 is confined to term starts 2016–2018 not only by book size but because **rung
2.0 prices its customers away and has no book left after 2019** (`B10`, 2026-08-29). Lifting the
ceiling adds accounts across 2017–2025; only the 2017–2018 slice reaches the intersection. **The
ladder must be re-run to state the new number and it must not be projected from the win counts** —
the two mechanisms compose, and I do not know in which proportion.

## 6. The run that settles this, specified so it is not re-derived

The blocker is contention, not method. A 1,200 run is ~1,019s, the publish gate is ~500s, and the
producer arrives every ~1,500s: **there is no idle window on this box large enough for a
2,000-budget point**, which is why point 2 collided and point 3 was skipped outright. Sequential
points cannot be measured beside a live producer.

    # with the producer stood down for the duration, and restored afterwards
    python3 -m tools.settlement_ceiling_probe --budgets 1200 2000 2800 \
        --publish-interval 3600 --time-share 0.9

* **Three clean points**, `clean: true` on each, or the tool refuses a slope and says so.
* **A chosen publish interval, not the measured cadence** (§3). 3,600s is the value already priced
  and argued in `SEAT_TO_DIRECTOR_P9_BOOK_DEPTH_PRICED_2026-08-28` Option 2, where the cost of a
  30→60 minute cadence is set out and the observation recorded that *"publish frequency was never
  what was binding progress"*. Using an interval from an existing argued document is the difference
  between a chosen bound and a number invented to fill a slot.
* **The memory bound is the one to believe.** At 4,193 MB against a 24,032 MB guest whose lowest
  observed availability during the probe was 10,786 MB, there is real room — and the honest share
  is a judgement to state, not a measurement to take, so it is a CLI argument with a default and
  not a constant in the module.
* **2,800 is the top of the useful range**: the campaign's own maximum demand is roughly 2,780
  customer-years (80 founders ≈ 800, plus the 386 funnel wins at their tenures), so a ceiling above
  that buys no accounts. `recommend()` reports `funnel_supply_customer_years` when a point refuses
  nothing, so the tool can say this rather than the reader inferring it.

**Whatever it returns, the report must say in terms that the change is the ceiling lifting and not
the method working.** Those are the two things a reader will otherwise confuse, and the published
net figure moving is not evidence for either until they are separated.

---

## What I got wrong, kept beside the claim

I predicted, on launching the probe, that three points would fit in the tick and that the answer
would be a raised ceiling. Both were wrong, and for the same unexamined reason: **I checked the box
was idle once, at the start, and treated that as a property of the next hour.** The producer's own
cadence was in front of me — I had just read it off `publish_gate_duration.jsonl` — and I did not
apply it to my own plan. The guard I wrote had the same blind spot as my planning, which is not a
coincidence.
