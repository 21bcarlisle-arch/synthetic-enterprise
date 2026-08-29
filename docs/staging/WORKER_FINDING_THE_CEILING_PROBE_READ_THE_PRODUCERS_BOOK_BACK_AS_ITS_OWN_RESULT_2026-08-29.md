**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `A46_book_depth_is_a_curriculum_question`

# The ceiling probe read the live producer's book back as its own result, and the ceiling's own cost note is 36% stale

Direction of 2026-08-29 (lane 0): re-measure `SETTLEMENT_CUSTOMER_YEAR_BUDGET`, set it from what
the probe supports, and re-run the live campaign. Full write-up and the re-run specification:
`docs/design/SETTLEMENT_CEILING_REMEASURED_2026-08-29.md`.

**The ceiling did not move and this document says why.** Three results, in the order they matter.

## 1. The mirror — this class, `measurements_that_mirror`

The 2,000-budget point reported `customer_years_committed = 1199.9, wins = 45, refused = 335`:
**byte-identical to the live 1,200-budget record.** Its own verdict — *"the funnel, not the
ceiling, bounds this range"* — was coherent, publishable and false.

The tell was internal. The same point's wall clock and peak RSS had **more than doubled**
(1,018.7s → 2,223.6s, 4,193 MB → 7,323 MB). A 2,000 ceiling cannot book fewer accounts than a
1,200 one while costing twice as much to settle. Two of one run's own fields disagreed and only
one was wrong.

**Mechanism:** the child read its campaign back from
`docs/observability/book_growth_campaign.json`. `live_population._resolve_campaign` writes that
path **absolutely**, from every process that assembles a book, and the live producer assembles one
every ~25 minutes. Producer pid 3859950 wrote it mid-run and the probe adopted the producer's book.

**Ask who WRITES each side.** Fixed by reading `LAST_CAMPAIGN` in-process, where no other writer
can reach. The file is still compared (`campaign_record_agrees`) so a future divergence is
*reported* rather than adopted, and `cleanliness()` fails closed — a point carrying none of the
contamination fields is unclean with `reason: not recorded`, never clean by default.

**The wider hazard, which outlives this probe:** any tool that measures a run by reading the run's
canonical artefacts is measuring whatever wrote them last, on a box with a producer on a cadence.
`tools/couple_pb3_book_growth.py` reads the same file by path.

## 2. The ceiling's recorded cost is 36% low, and nothing reported the drift

At the same 1,200 budget, measured this week on the live path's own compute:

| | recorded 2026-08-24 | measured 2026-08-29 |
|---|---|---|
| customer-years committed | 796.1 | **1,200.0** |
| wall clock | 746.8s | **1,018.7s** |
| peak RSS | 3,117 MB | **4,193 MB** |

Nothing regressed. **The August figure was taken while the ceiling was SLACK** — the campaign
reached 796.1 of its 1,200 — and the founder book made it TAUT. A cost note taken at a budget the
run never reached is a note about a different run, and it went stale the day the founder book
landed with nothing watching.

## 3. The time bound the ceiling is argued against is circular

The constant reasons *"12.4 minutes leaves seventeen for the publisher's gate inside the half-hour
cycle"*. The cadence is 1,500s not 1,800s (re-measured 2026-08-26, two days *after* that note).
Worse, `suite_duration_watch.PUBLISH_CADENCE_SECONDS` is by its own definition *"a measurement of
how often runs actually arrive"* — so **raising this ceiling raises the cadence that is supposed to
bound it**, and lengthening the run also widens the interval `absolute_band()` checks the gate's
speed against, buying silence from that alarm too. Memory against the guest is the only bound here
that is evidence.

## 4. The published note a reader sees was wrong about its own arithmetic

The runtime note rendered onto the book-growth page said 1,200 was *"60% of the 465 measured in
AO12's scale probe"*. **60% of 465 is 279** — the constant's value when the string was written. It
survived 279 → 600 → 1200 untouched while the module's header note was corrected in place on
2026-08-24. A citation duplicated between a comment and a rendered string has two half-lives, and
only one of them has a reader who would notice. Fixed; the rendered note now cites the artefact.

## WHAT THIS CREATES

1. **The re-run, specified in §6 of the design doc** — three clean points with the producer stood
   down, and a *chosen* publish interval (3,600s, already priced in P9 Option 2) rather than the
   measured cadence. There is no idle window on this box large enough for a 2,000-budget point
   beside a live producer, which is why point 2 collided and point 3 was skipped.
2. **Unchanged and stated as such:** gradable ladder population **16**, R6 headroom **£316,009**,
   published net **£164,542**. The ceiling did not move, so nothing downstream of it did.
3. **The ladder's 16 will not scale with the book**, and must not be projected from win counts:
   rung 2.0 prices its customers away and has no book left after 2019, so only the 2017–2018 slice
   of any new wins reaches the intersection. Two mechanisms compose and I do not know in which
   proportion.
