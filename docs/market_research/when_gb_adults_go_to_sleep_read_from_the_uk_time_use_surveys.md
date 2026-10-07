**Severity:** RECORDED · **Lane:** W1_market_weather · **Atom:** `W1_29_the_worlds_homes_are_drawn_too_alike_in_half_hourly_behaviour`

**Knowledge:** none -- a SIM fidelity anchor for the world's household clock, not a supplier-facing
knowledge page. No knowledge topic covers when a household is awake. Its gap row sits in
`docs/institutional/knowledge_map.md` under Energy Consumption Profiles.

# When GB adults go to sleep, read from the UK time use surveys

**Read 2026-10-07**, worker on the delivery seat's lane-0 draw `w1-29-level-record-then-the-night`,
answering `bebf42253`. That commit found the world's homes nearly dead after midnight (0.11 of their
active mean above base at 00:00, against 0.62 for real London homes) and traced it to an unsourced
`rise.randint(43, 47)` bedtime in `simulation/premise_trace.py`: retire between 21:30 and 23:30.
**Nothing is built here.** Low Carbon London is the comparison, so it is not used as a source.

## What was asked

The share of adults asleep, or of households active, by half hour after 21:00, from the ONS
time-use outputs: UKTUS 2014-15 and the ONS Online Time Use Survey (OTUS) 2020-2023.

## What the published record holds

**UKTUS 2014-15: by-half-hour shares are NOT ESTABLISHED in any published table.** The survey
records 144 ten-minute slots per diary day, so the shares exist in the microdata (UK Data Service
SN 8128, End User Licence). Its CTUR user guide (Version 1, December 2016) documents coding and
imputation and publishes no time-of-day table. The one paper that reads sleep timing from it,
Lamote de Grignon Pérez, Gershuny, Foster & De Vos 2019 (*J Sleep Res* 28(1):e12753,
doi:10.1111/jsr.12753, PMC6378586; 14,197 diaries from 7,126 adults), gives it only as a figure
(Fig. 4) with no clock times in the text. What the text does state: sleep onset in 2015 is about
30 minutes **earlier** than in 1974, a little more on Friday and Saturday nights. Sleep offset is
about 15 minutes later.

**OTUS 2020-2023: NOT ESTABLISHED.** The bulletins (e.g. *Time use in the UK: 23 September to 1
October 2023*) and their dataset publish daily average minutes by activity. They give no
time-of-day breakdown. The microdata is Secure Access (UKDS SN 9204).

**UKTUS 2000-01: ESTABLISHED as means and four points on the onset distribution.** Martín-Olalla
2019 (*Scientific Reports* 9, 2019, doi:10.1038/s41598-019-54990-6; arXiv 1907.04277v2) reads the
ONS/Ipsos-RSL GB microdata. "Sleep onset" there is the last ten-minute slot of the waking cycle,
with the cycle starting at 04:00. Results are per adult diary, summer vs winter. Groups are:
employees = any paid work recorded that day; non-employees = no paid work, aged 20 or over.

| GB 2000-01 (Table 1 sizes; Tables S.1, S.3) | diaries | mean onset, summer / winter | point on the onset CDF, summer / winter |
|---|---|---|---|
| Mon-Fri, employees | 4,081 | 23:16 / 23:13 | 0.65 / 0.67 asleep by 23:20 |
| Mon-Fri, non-employees ≥20 | 3,768 | 23:20 / 23:20 | 0.70 / 0.68 asleep by 23:40 |
| Sat-Sun, employees | 1,378 | 23:43 / 23:49 | 0.28 / 0.22 asleep by 22:30 * |
| Sat-Sun, non-employees ≥20 | 6,473 | 23:24 / 23:28 | 0.90 / 0.87 asleep by 01:00 * |

\* Table S.1 labels its weekend columns "non-employees, employees", the reverse of Tables 1 and S.3
and of the paper's group definitions. The two weekend CDF points are therefore assigned to their
groups by column position, and that assignment is uncertain. The means in S.3 carry no such
ambiguity. SEM on each mean is 2-4 min. The seasonal differences are mostly not significant, so the
season is not a dial here.

What this establishes, and what it does not:

* **An adult's mean bedtime in GB was 23:13-23:49 in 2000-01** in every group, and about a third
  of working-weekday adults were still awake at 23:20.
* **About 1 in 10 adults was still awake at 01:00** on a weekend non-working night (the
  column-assignment caveat above applies).
* **It is per adult, not per household.** A household is active until its last member sleeps,
  so the share of households active after 23:00 is at least the per-adult share. How much higher
  is not established. It needs within-household diaries, which UKTUS 2014-15 has and publishes in
  no table.
* **It predates the run window by fifteen years.** The direction since then is earlier: 2015 is
  about 30 minutes earlier than 1974, but no 2000→2015 difference is stated. The size of the drift
  across 2016-2025 is not established.

## Against the code

The world draws household retire uniformly over 21:30-23:30. Its mean is 22:30, which is 45-80
minutes before the **per-adult** mean in every 2000-01 group, and a household mean must be later
still. *(Corrected 2026-10-07 by the retire-arm pass below: those are the LAST AWAKE slots. `occupancy_at` sleeps a home only when `period > sleep_period`, so onset is uniform over 22:00-24:00 with a mean of 23:00, 15-20 minutes before the weekday per-adult mean, and nobody is awake after 24:00, not 23:30. The contradiction is the missing tail past midnight, more than the mean.)* The world puts nobody awake after 23:30, against about a third of adults on a working weekday
and more at weekends. **The drawn range is contradicted by the record.** A correct replacement is
**not** established: four CDF points and four means from 2000-01 do not make a household
distribution for 2016-2025. `premise_trace.py`'s comment now says both things.

## The one-variable arm, and its prediction (filed before any run)

*Arm:* change only the retire draw. Replace `randint(43, 47)` with a per-household draw whose
per-adult reading matches the 2000-01 table: mean about 23:15 on weekdays, 0.65-0.70 asleep by
23:20-23:40, and 0.87-0.90 asleep by 01:00 at weekends. Hold everything else, and re-read
`bebf42253`'s median profile above base ÷ active mean, from the same draw and seeds (world seed 17,
traces seed 7).

*Prediction:*

1. **00:00 rises from 0.11 to between 0.25 and 0.40.** It stays below LCL's 0.62.
2. **01:00 rises from 0.11 to between 0.13 and 0.20**, against LCL's 0.38.
3. **02:00-04:00 moves by less than 0.03** (world 0.11-0.12, against LCL 0.24-0.29), because 87-90%
   of adults are asleep by 01:00 even on the latest night in the table.
4. **The night-texture median (periods 2-9) moves by less than 0.02.**

**If 3 and 4 hold, a bedtime cannot close the 02:00-04:00 half of the gap**, and that half belongs to
`bebf42253`'s other candidates: (b) load above base while asleep, (c) electric-heated homes in the
"Std" label, or (d) London 2013 against GB. That would make bedtime a remedy for the midnight slot
only. If 3 or 4 fail, the world's sleeping house is more coupled to the retire time than this
reading assumes, and that coupling is the next thing to read.

## The retire arm, run and graded (2026-10-07)

Worker on the lane-0 draw `w1-29-the-one-variable-retire-arm`, in a clean `origin/main` worktree at
`29de32469`. The retire draw alone was replaced, from its own substream, so wake time and weekend shift
are drawn exactly as before. Onset slots follow the weekday table above, read per household with no
last-member correction: 22:00 0.06, 22:30 0.15, 23:00 0.45, 23:30 0.12, 00:00 0.09, 00:30 0.06,
01:00 0.04, 01:30 0.03. That gives a mean of 23:16, with 0.66 asleep by 23:00-23:20. The same 60 homes,
world seed 17 and traces seed 7, were read net of both heating machines.

**Read from the code before the run, and filed beside the four predictions:** the household's awake
window is `[wake, sleep]` inside ONE calendar day. `occupancy_at` clamps `sleep` to period 47, and
every period before `wake`, which includes 00:00-04:00, is asleep. So every onset at or after 24:00
collapses to "awake until 24:00". The arm moves the mean `sleep_period` from 45.05 to 45.28, about 7
minutes, and no bedtime draw of any shape can reach the 00:00 slot.

Median profile above base ÷ active mean, every other half-hour from 00:00:

    LCL    0.62 0.38 0.29 0.25 0.24 0.25 0.34 0.60 0.88 1.05 1.04 0.98 1.01 1.08 1.02 1.02 1.11 1.29 1.57 1.77 1.69 1.60 1.41 1.08
    base   0.11 0.11 0.11 0.12 0.12 0.14 0.22 0.72 0.92 0.81 0.90 0.83 0.82 0.79 0.79 0.84 1.16 1.91 2.21 2.33 2.47 2.46 1.70 0.93
    arm    0.11 0.11 0.11 0.12 0.12 0.14 0.22 0.72 0.93 0.82 0.88 0.81 0.82 0.81 0.79 0.83 1.20 1.94 2.18 2.29 2.45 2.40 1.90 0.90

The base row reproduces `bebf42253`'s row exactly. Across 22:00/22:30/23:00/23:30 the arm reads 1.90/1.44/0.90/0.65,
against 1.70/1.35/0.93/0.62 for base. The night-texture median (periods 2-9) is 0.118, against 0.116.

| filed prediction | result | grade |
|---|---|---|
| 1. 00:00 rises from 0.11 to 0.25-0.40 | 0.11 → 0.11 | **refuted** |
| 2. 01:00 rises from 0.11 to 0.13-0.20 | 0.11 → 0.11 | **refuted** |
| 3. 02:00-04:00 moves by < 0.03 | moves 0.00 | held |
| 4. night-texture median moves by < 0.02 | +0.002 | held |

Predictions 1 and 2 failed for a reason none of the four branches above names. The world's sleeping
house is not more coupled to the retire time than assumed. **It is cut off from it at 24:00 by
construction.** So "move the bedtime" is not a one-variable change in this model. Before any bedtime
distribution can be tested against the midnight slot, an awake window that crosses midnight is needed:
the evening's occupancy has to carry into the first periods of the next day. Whether that window
would close 00:00 and 01:00 stays an open prediction. The table still says 87-90% of adults are asleep
by 01:00, so 02:00-04:00 belongs to `bebf42253`'s (b) load while asleep, (c) electric homes in "Std",
or (d) London against GB, whatever the bedtime does. The arm adds no evidence among those three.

Limits: one world draw, 60 homes. The per-adult table is used as a per-household one, which
understates how late households go to bed. The weekend shift (+30 min to +2 h on top of the weekday
time) was left alone as the held variable, and the table suggests it is itself too large. No code
changed. Scripts: `/tmp/w129r/` (not committed).

## Sources

* Martín-Olalla, J.M. (2019). The long term impact of Daylight Saving Time regulations in daily life
  at several circles of latitude. *Scientific Reports* 9. arXiv:1907.04277v2, Tables 1, S.1, S.3.
  Data: Ipsos-RSL & ONS (2003), *United Kingdom Time Use Survey 2000*, UK Data Archive.
* Lamote de Grignon Pérez, J., Gershuny, J., Foster, R., De Vos, M. (2019). Sleep differences in
  the UK between 1974 and 2015: insights from detailed time diaries. *J Sleep Res* 28(1):e12753.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC6378586/
* CTUR (2016). *United Kingdom Time Use Survey 2014-15*, Version 1, user guide. UKDS SN 8128.
  https://doc.ukdataservice.ac.uk/doc/8128/mrdoc/pdf/8128_ctur_report.pdf
* ONS (2023). *Time use in the UK: 23 September to 1 October 2023*. Daily averages only.
