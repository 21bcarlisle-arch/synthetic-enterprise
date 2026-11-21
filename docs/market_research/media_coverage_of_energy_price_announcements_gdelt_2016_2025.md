# Media coverage of GB energy price announcements, counted per week, 2016–2025

**Knowledge:** how-households-behave-toward-a-supplier

**Written 2026-11-21** by the delivery seat. It fills gap **G1** and gap **G5** of
`how_households_respond_to_bill_shock_by_family_moment_and_payment_method_2026-11-21.md` (§6), for
item 3 of the director's bill-shock steer of 21 Nov
(`docs/staging/advisor/done/DIRECTOR_STEER_BILL_SHOCK_RESPONSES_EMERGE_FROM_HOUSEHOLD_BEHAVIOUR_AND_ARE_CHECKED_AGAINST_HISTORY_2026-11-21.md`):
"The biggest spike is media coverage."

**What this is, and what it is not.** A count of UK national news articles about household energy
prices, per week, from an open news archive. It is a proxy for how loudly each price announcement
reached households. It does not say how many households read a story, nor what they did next.
It is documentation and a dated series for the world build to cite. **The company never reads it
(W6).**

Series: `media_coverage_energy_price_gdelt_weekly_2016_2025.json`. Counter:
`tools/fetch_gdelt_energy_price_coverage.py`. Tests: 
`tests/tools/test_gdelt_energy_price_coverage_counts_what_a_gb_reader_saw.py`.

---

## 1. What is counted

**The quantity.** For each week (Monday to Sunday):

- **`energy_price_articles`**: the number of distinct articles, by URL, on a fixed list of UK
  national outlets, that are about the price of household energy;
- **`rise_articles`**: the subset whose URL says the price went up (rise, hike, increase, soar,
  jump, put up, and so on). Reported beside the first count, never instead of it. A cut or a
  freeze is still coverage of a price announcement;
- **`national_urls`**: every distinct URL from the same outlets that GDELT saw that week. This is
  the denominator;
- **`per_1000_national_urls`**: the first count per 1,000 of the third. GDELT's monitoring of an
  outlet changes over the decade, and this ratio does not move when it does. **Compare weeks
  across years on the ratio, not the count.**

**What makes an article "about the price of household energy".** Either leg is enough:

1. **The slug leg.** The URL path names an energy word (energy, gas, electricity, power, heating,
   dual-fuel) and a price word (bill, price, tariff, cap) in the same segment, or says
   `price-cap`.
2. **The theme leg.** GDELT tagged the article with an electricity-price or gas-price theme
   (`ECON_ELECTRICALPRICE`, `ECON_NATGASPRICE`) **and** named Ofgem or an energy supplier in it.
   BBC URLs carry no slug, so this is the only way a BBC story counts.

Stories filed under another country's section (`/world/`, `/australia-news/`, `/us-news/`, and
similar) are excluded. The first test pull found The Guardian's Australian edition covering
Australian power prices on the same day as a British Gas rise.

**The outlets** (a domain matches itself and its subdomains): bbc.co.uk, bbc.com,
theguardian.com, telegraph.co.uk, independent.co.uk, dailymail.co.uk, thisismoney.co.uk,
mirror.co.uk, express.co.uk, thesun.co.uk, thetimes.co.uk, standard.co.uk, inews.co.uk,
metro.co.uk, news.sky.com, itv.com, ft.com.

## 2. The source, and why this one

**GDELT 1.0 Global Knowledge Graph, daily files** (`data.gdeltproject.org/gkg/YYYYMMDD.gkg.csv.zip`).
GDELT reads world news continuously and records, for each article, its URL, the organisations it
names and the themes it touches. These files are open data, free for any use, cited as the GDELT
Project. They run unbroken from 2013, so one method covers 2016–2025.

**Routes tried and not taken, recorded so they are not tried again:**

- **GDELT's DOC 2.0 API** is the obvious tool: one query returns a whole timeline. On 21 Nov
  2026 it answered every request from this machine with HTTP 429, even the first request and
  with minutes between tries. It also starts in January 2017, so it cannot cover 2016.
- **The Guardian's Open Platform API** needs a registered key. Its public test key now answers
  `Unauthorized`. The site's own archive pages were not read: theguardian.com's `robots.txt`
  disallows Claude agents (`ClaudeBot`, `Claude-User`, `anthropic-ai`) site-wide, and that is
  respected here.
- **Licensed press indexes** (Factiva, Nexis) are not held.

**Cost.** Each daily file is 25–55 MB. At the ~5 MB/s this machine gets, the decade is roughly
3,650 files and 10–15 hours of download. The counter reads each file streamed, keeps only the
per-day counts and matched URLs (`~/.cache/synthetic-enterprise/gdelt_energy_coverage/`), and
discards the file. It pulls the days nearest each announcement first. A pull that is cut short
therefore still holds every announcement and the weeks around it, and a re-run resumes.

## 3. The announcements, dated (fills G5)

Table: `energy_price_announcements_gb_2016_2025.json`. It has 46 rows: 24 Big Six SVT changes,
2016–2018; 21 Ofgem cap levels, from the first (announced 6 Nov 2018) to the October 2025 cap
(announced 27 Aug 2025); and the Energy Price Guarantee (announced 8 Sep 2022). Each row gives
who, announcement date, effective date, the change, the source, and a **date basis** grade:

- **Announcer's own document.** An Ofgem letter or release, or the supplier's own release.
  This covers all 21 cap rows: the date is the "Date:" line of Ofgem's cap letter.
- **Article date.** A dated news article reporting the announcement. It can trail the
  announcement by a day.
- **Unverified.** One secondary source only.
- **Not found.** Carried as `null` and never guessed. Three 2016–17 rows are in this state:
  E.ON's and ScottishPower's early-2016 gas cuts, and EDF's December 2016 gas cut and March 2017
  electricity rise. Their effective dates are known.

**What the 2016–2018 table says about T2b's pre-cap months.** These replace "British Gas
+5.5% in 2018, effective date unverified" on the bill-shock page:

- **2016 was a year of cuts, not rises.** All six cut gas by about 5%, announced Jan–Feb and
  effective Feb–Mar.
- **The 2017 round** was announced 3 Feb – 13 Mar, effective 1 Mar – 28 Apr. EDF then rose again
  (effective 21 Jun) and British Gas announced alone on 1 Aug, effective 15 Sep.
- **2018 had two rounds.** The first was announced 2 Mar – 30 May, effective 19 Apr – 11 Jul.
  The second was announced 19 Jun – 23 Aug, effective 16 Aug – 8 Oct. British Gas's 2018 rise was
  announced 10 Apr (Centrica's own release) and took effect **29 May**, so the bill-shock page's
  May–Jul 2018 ratios (1.08, 1.12, 1.09) span BG's effective month and the announcement and
  effective months of four other suppliers. **A month cannot separate the moments in 2018;
  the weekly series can.**
- **Not found:** a second 2018 rise by npower or SSE. That is not evidence there was none.

**Disagreements between sources, kept:**

- Ofgem's August 2020 letter restates earlier cap levels on new typical consumption. The April
  2020 level reads £1,162 in its own letter and £1,126 restated, and the April 2019 level
  £1,254 becomes £1,217. The table carries each level **as announced**, because the
  announcement is what was covered.
- The May 2023 press release is dated 25 May and its letter 26 May. The table uses 25 May.
- SSE's April 2017 effective date reads 28 Apr in SSE's release and 29 Apr in one secondary
  source. The table uses SSE's own date.

## 4. Coverage on each announcement day (first reading, 21 Nov 2026)

**The quantity** is the announcement **day** only: articles that day on the national outlets,
and the same count per 1,000 national-outlet articles GDELT saw that day. **Read across years on
the share**. GDELT saw anywhere from about 800 national-outlet URLs a day (weekends) to
3,600 over the decade, and the yearly median falls from about 3,100 (2017–18) to 1,400 (2022)
(161 days measured so far). A row
whose date basis is "article date" or "unverified" may sit a day off its announcement, which
can halve the day count (ScottishPower, 23 Aug 2018, reads 0). The week against its baseline
is in §4a.

| Announced | Who | Change | Articles that day | Per 1,000 national articles |
|---|---|---|---|---|
| 2016-01-28 | SSE | gas -5.3% | 8 | 2.9 |
| 2016-02-08 | npower | gas -5.2% | 5 | 2.0 |
| 2016-02-11 | British Gas | gas -5.1% | 9 | 3.2 |
| 2016-02-11 | EDF | gas -5% | 9 | 3.2 |
| 2017-02-03 | npower | dual +9.8% (electricity +15%, gas +4.8%) | 13 | 4.1 |
| 2017-02-10 | ScottishPower | dual +7.8% (electricity +10.8%, gas +4.7%) | 14 | 4.4 |
| 2017-03-07 | E.ON | dual +8.8% (electricity +13.8%, gas +3.8%) | 7 | 2.3 |
| 2017-03-13 | SSE | dual +6.9% (electricity +14.9%, gas 0%) | 10 | 3.3 |
| 2017-04-12 | EDF | dual +7.2% | 7 | 2.4 |
| 2017-08-01 | British Gas | electricity +12.5%, dual +7.3%, gas unchanged | 34 | 12.6 |
| 2018-03-02 | E.ON | dual about +2.7% (discount removed, unit rates unchanged) | 8 | 2.6 |
| 2018-04-10 | British Gas | dual +5.5% | 21 | 6.4 |
| 2018-04-12 | EDF | dual +1.4% | 10 | 3.0 |
| 2018-04-20 | ScottishPower | dual +5.5% | 11 | 3.5 |
| 2018-05-11 | npower | average +5.3% | 11 | 3.5 |
| 2018-05-30 | SSE | +6.7% (+7.8% with paperless discount lost) | 6 | 1.7 |
| 2018-06-19 | E.ON | dual +4.8% | 2 | 0.6 |
| 2018-07-05 | EDF | dual +6% | 5 | 1.7 |
| 2018-08-08 | British Gas | dual +3.8% | 18 | 5.6 |
| 2018-08-23 | ScottishPower | dual +3.7% | 0 | 0.0 |
| 2018-11-06 | Ofgem | £1,137, first cap | 10 | 3.6 |
| 2019-02-07 | Ofgem | £1,254 (+£117) | 13 | 5.1 |
| 2019-08-07 | Ofgem | £1,179 (-6%) | 13 | 6.0 |
| 2020-02-07 | Ofgem | £1,162 (-1%) | 9 | 4.3 |
| 2020-08-07 | Ofgem | £1,042 (-7%) | 5 | 2.4 |
| 2021-02-05 | Ofgem | £1,138 (+9%) | 15 | 7.6 |
| 2021-08-06 | Ofgem | £1,277 (+12%) | 13 | 9.3 |
| 2022-02-03 | Ofgem | £1,971 (+54%) | 32 | 22.4 |
| 2022-08-26 | Ofgem | £3,549 (+80%) | 54 | 38.8 |
| 2022-09-08 | Government | typical bill held at £2,500 | 31 | 21.3 |
| 2022-11-24 | Ofgem | £4,279 (+21%) | 7 | 4.6 |
| 2023-02-27 | Ofgem | £3,280 (-23%) | 13 | 9.4 |
| 2023-05-25 | Ofgem | £2,074 (-37%) | 41 | 16.7 |
| 2023-08-25 | Ofgem | £1,923 (-7%) | 36 | 16.4 |
| 2023-11-23 | Ofgem | £1,928 (+5%) | 29 | 14.0 |
| 2024-02-23 | Ofgem | £1,690 (-12%) | 31 | 14.5 |
| 2024-05-24 | Ofgem | £1,568 (-7%) | 26 | 12.7 |
| 2024-08-23 | Ofgem | £1,717 (+10%) | 31 | 17.4 |
| 2024-11-22 | Ofgem | £1,738 (+1%) | 28 | 14.5 |
| 2025-02-25 | Ofgem | £1,849 (+6%) | 27 | 12.9 |
| 2025-05-23 | Ofgem | £1,720 (-7%) | 18 | 11.0 |
| 2025-08-27 | Ofgem | £1,755 (+2%) | 30 | 18.1 |

## 4a. The announcement week against the weeks before it (second reading, 21 Nov 2026, 13:30)

**The quantity.** `week_vs_baseline` is the articles per counted day in the 7 days from the
moment, divided by the articles per counted day in the 28 days that end a week before it
(day −35 to day −8). 1.0 means the week was no louder than the month before it. It answers what
the day count in §4 cannot: how far a moment rose **above** the coverage already running. The
"effective" column is the same ratio from the effective date. The effective column was filled on
21 Nov 2026 from the complete decade (every day 2016–2025 cached); a dash now means only that the
row has no baseline.

| Announced | Who | Week articles | Baseline per day | Week vs baseline | Effective | Effective week vs baseline |
|---|---|---|---|---|---|---|
| 2016-01-28 | SSE | 22 | — | **—** | 2016-03-29 | 0.1 |
| 2016-02-08 | npower | 29 | 2.29 | **1.8** | 2016-03-28 | 0.1 |
| 2016-02-11 | British Gas | 21 | 2.64 | **1.1** | 2016-03-16 | 0.3 |
| 2016-02-11 | EDF | 21 | 2.64 | **1.1** | 2016-03-24 | 0.3 |
| 2017-02-03 | npower | 30 | 1.71 | **2.5** | 2017-03-16 | 1.0 |
| 2017-02-10 | ScottishPower | 38 | 1.43 | **3.8** | 2017-03-31 | 0.7 |
| 2017-03-07 | E.ON | 25 | 3.93 | **0.9** | 2017-04-26 | 1.5 |
| 2017-03-13 | SSE | 35 | 3.36 | **1.5** | 2017-04-28 | 0.6 |
| 2017-04-12 | EDF | 14 | 2.79 | **0.7** | 2017-06-21 | 1.6 |
| 2017-08-01 | British Gas | 80 | 1.93 | **5.9** | 2017-09-15 | 0.9 |
| 2018-03-02 | E.ON | 25 | 1.14 | **3.1** | 2018-04-19 | 1.3 |
| 2018-04-10 | British Gas | 52 | 1.07 | **6.9** | 2018-05-29 | 1.1 |
| 2018-04-12 | EDF | 27 | 0.79 | **4.9** | 2018-06-07 | 0.8 |
| 2018-04-20 | ScottishPower | 23 | 1.86 | **1.8** | 2018-06-01 | 0.6 |
| 2018-05-11 | npower | 29 | 3.21 | **1.3** | 2018-06-17 | 0.7 |
| 2018-05-30 | SSE | 17 | 2.07 | **1.2** | 2018-07-11 | 1.5 |
| 2018-06-19 | E.ON | 11 | 1.96 | **0.8** | 2018-08-16 | 0.6 |
| 2018-07-05 | EDF | 19 | 1.57 | **1.7** | 2018-08-31 | 1.0 |
| 2018-08-08 | British Gas | 25 | 2.32 | **1.5** | 2018-10-01 | 0.8 |
| 2018-08-23 | ScottishPower | 16 | 3.32 | **0.7** | 2018-10-08 | 0.7 |
| 2018-11-06 | Ofgem | 22 | 1.29 | **2.4** | 2019-01-01 | 1.7 |
| 2019-02-07 | Ofgem | 35 | 2.0 | **2.5** | 2019-04-01 | 1.5 |
| 2019-08-07 | Ofgem | 21 | 0.75 | **4.0** | 2019-10-01 | 1.0 |
| 2020-02-07 | Ofgem | 22 | 1.18 | **2.7** | 2020-04-01 | 1.2 |
| 2020-08-07 | Ofgem | 11 | 0.68 | **2.3** | 2020-10-01 | 0.8 |
| 2021-02-05 | Ofgem | 28 | 1.04 | **3.9** | 2021-04-01 | 0.8 |
| 2021-08-06 | Ofgem | 18 | 1.14 | **2.3** | 2021-10-01 | 1.6 |
| 2022-02-03 | Ofgem | 72 | 5.04 | **2.0** | 2022-04-01 | 1.3 |
| 2022-08-26 | Ofgem | 137 | 7.75 | **2.5** | 2022-10-01 | 0.5 |
| 2022-09-08 | Government | 79 | 13.04 | **0.9** | 2022-10-01 | 0.5 |
| 2022-11-24 | Ofgem | 18 | 3.89 | **0.7** | 2023-01-01 | 1.1 |
| 2023-02-27 | Ofgem | 32 | 2.93 | **1.6** | 2023-04-01 | 1.5 |
| 2023-05-25 | Ofgem | 84 | 2.29 | **5.2** | 2023-07-01 | 1.5 |
| 2023-08-25 | Ofgem | 52 | 4.04 | **1.8** | 2023-10-01 | 2.2 |
| 2023-11-23 | Ofgem | 43 | 2.96 | **2.1** | 2024-01-01 | 0.9 |
| 2024-02-23 | Ofgem | 47 | 1.82 | **3.7** | 2024-04-01 | 1.6 |
| 2024-05-24 | Ofgem | 32 | 1.64 | **2.8** | 2024-07-01 | 1.9 |
| 2024-08-23 | Ofgem | 53 | 1.64 | **4.6** | 2024-10-01 | 2.1 |
| 2024-11-22 | Ofgem | 45 | 2.07 | **3.1** | 2025-01-01 | 0.9 |
| 2025-02-25 | Ofgem | 49 | 2.5 | **2.8** | 2025-04-01 | 0.8 |
| 2025-05-23 | Ofgem | 27 | 2.32 | **1.7** | 2025-07-01 | 0.5 |
| 2025-08-27 | Ofgem | 47 | 1.61 | **4.2** | 2025-10-01 | 1.1 |

**What the second reading says.**

- **The pre-registered prediction held.** §5 predicted the 7 Feb 2019 cap week would rise less
  above its baseline than British Gas's 1 Aug 2017 week. It reads **2.5 against 5.9**.
- **For a supplier, the announcement is the media moment and the effective date is not.** Over
  the 19 supplier changes with both windows, the announcement week's median ratio is **1.5** and
  the effective week's **0.8**. The announcement week is the louder of the two in 15 of 19, with
  one tie. Only 4 of the 19 effective weeks exceed 1.2. (Over the first 15 rows this read 1.5
  against 0.7. The four rows added on 21 Nov read 0.9, 1.0, 0.8 and 0.7.) Caution: a 2016–18
  effective week's baseline often holds another supplier's announcement in the same round, which
  pulls the ratio down.
- **For a cap, the effective date is a second, smaller media moment.** Over the 21 caps, the
  announcement week's median is **2.5** and the effective week's **1.2** (0.5 to 2.2). The
  announcement is louder in 19 of 21; the exceptions are 1 Jan 2023 (1.1 against 0.7, while the
  Guarantee held prices) and 1 Oct 2023 (2.2 against 1.8). 10 of the 21 cap effective weeks
  exceed 1.2, against 4 of 19 for suppliers. This is not caused by baseline overlap. From Aug
  2022 the quarterly cap is announced 33–40 days before it takes effect, so the effective week's
  baseline (day −35 to −8) holds part of the announcement week, which pulls the ratio *down*. The
  8 earlier caps, announced 53–57 days ahead with clean baselines, read a median of 1.25; the 13
  later ones read 1.1. Both medians are above 1.0. One reading, *not tested here*: a cap takes
  effect on one national date that the press already knows ("bills rise today"). Supplier changes
  take effect on staggered dates of their own. The lowest cap effective weeks, 1 Oct 2022 (0.5,
  cap and Guarantee together) and 1 Jul 2025 (0.5), are measured against a loud month: the
  record late summer of 2022, and a baseline that is missing 10 of its 28 days at source
  (below).
- **Against its own background, a cap week rises about as far as a loud supplier rise.** The 21
  cap announcements have a median ratio of **2.5** (0.7 to 5.2). British Gas 2018 (6.9), British
  Gas 2017 (5.9) and EDF April 2018 (4.9) rise further than any cap. The loudest cap weeks above
  baseline are 25 May 2023 (5.2, the first cut that reached bills after the Guarantee), Aug 2024
  (4.6) and Aug 2025 (4.2), not 2022. **Absolute loudness and rise above background are
  different quantities.** 26 Aug 2022 is the loudest day of the decade (38.8 per 1,000) but its
  week is only 2.5× the August that came before it, because that whole summer was already loud.
  A world media term must say which of the two it uses.
- **The Guarantee weeks did not rise above their background:** 8 Sep 2022 reads 0.9 and 24 Nov
  2022 reads 0.7. This agrees with §5. Coverage tracked the price households would pay.
- **Loudest complete weeks of the decade, on the per-1,000 share** (515 of 523 weeks complete,
  the whole decade): w/c 22 Aug 2022 (18.2), 5 Sep 2022 (13.5), 29 Aug 2022 (10.2), 8 Aug 2022
  (10.1), **20 Sep 2021 (8.9)**, 31 Jan 2022 (8.4). Four of the top five are the 2022 summer. The
  fifth is w/c 20 Sep 2021, the week of the autumn 2021 supplier failures and the wholesale gas
  spike. **No price announcement falls in that week.** So a media term keyed only to price
  announcements misses the fifth-loudest week of the decade. Supplier failure is its own media
  moment, and the world build must name it as an event rather than infer it from tariffs.
- **The 8 incomplete weeks** are the two partial calendar weeks at the ends of the decade
  (w/c 28 Dec 2015 and 29 Dec 2025) and 20 days for which GDELT publishes no daily file (HTTP 404).
  Those 20 days are single days in Nov 2022, Feb, Mar and May 2023, and a run from 14 to 29 Jun
  2025, which empties w/c 16 and 23 Jun 2025. The rates are per counted day, so a missing day
  thins a window but does not bias it.

## 5. What the first reading says, and what it cannot say yet

These readings are from announcement days alone, without the baseline. They describe how loud
the day was, not how far it rose above the coverage already running. Through 2022–2025 the
background coverage of energy bills was itself high.

- **Before the cap, one rise was loud and the rest were quiet.** British Gas on 1 Aug 2017 is
  the largest pre-2022 day, at 12.6 per 1,000. Every other 2017–18 supplier rise sits at
  0.0–4.4 (the 0.0 is ScottishPower's unverified 23 Aug 2018 date), around the 2016 *cuts*
  (2.0–3.2). British Gas's two 2018 rises (6.4 and
  5.6) are the loudest of their rounds. Coverage follows the announcer's size, not the rise's.
- **The cap's first three years did not out-shout British Gas 2017.** The days run from 2.4
  (Aug 2020, −7%) to 9.3 (Aug 2021, +12%).
- **From February 2022, cap days are loud, except while the Guarantee held prices.** Cap days
  run from 11.0 to 38.8 per 1,000, the peak being 26 Aug 2022 (+80%). The two lowest are the
  two caps announced while the Energy Price Guarantee held the typical bill at £2,500, so that
  neither moved any household's price: **24 Nov 2022 (+21%) at 4.6** and **27 Feb 2023 (−23%)
  at 9.4**. The next cap, announced 25 May 2023, fell below the Guarantee and so did move
  prices; it reads 16.7. The coverage counted the change to households, not the change to the cap. The world
  build should key its media term to the price a household will pay, not to a cap headline.
- **Which moment drives switching: I cannot yet say.** The bill-shock page (§3.2) found the
  largest 2016–19 switching excess in the *effective* month of the April 2019 cap rise (1.23),
  not its announcement month. Its announcement day here (7 Feb 2019, 5.1 per 1,000) is less than
  half British Gas's August 2017 day (12.6). BG's effective month, Sep 2017, showed only 1.07.
  On these two observations, louder coverage did not mean more switching. That is n = 2, read
  on day counts without a baseline, and it decides nothing.

**Prediction, filed before the weekly windows exist (21 Nov 2026).** When the pull reaches the
28-day baselines, the announcement week's ratio to its baseline (`week_vs_baseline`) will be
**lower for 7 Feb 2019 than for 1 Aug 2017**. If it is not, the day counts above have misled me,
and that will be recorded here beside this line.

**Graded 21 Nov 2026, 13:30: held.** 7 Feb 2019 reads 2.5 and 1 Aug 2017 reads 5.9 (§4a).

**Second prediction, filed 21 Nov 2026 after the pull wrote its last day and before `--aggregate`
was rerun on it.** The cap effective weeks will behave like the supplier ones: their median
`week_vs_baseline` will be **below 1.0**, and the announcement week will be the louder of the
two for **at least 17 of the 21** cap rows that have both. If the cap effective median is 1.0 or
above, the effective moment is a media moment for caps where it was not for suppliers, and the
world's media term needs a second pulse at the effective date.

**Graded 21 Nov 2026: half refuted.** The cap effective median is **1.2**, not below 1.0, so the
first half failed. The announcement week was the louder in **19 of 21**, so the second half held.
For caps, the effective date is a second pulse about half the height of the announcement pulse
(§4a). For suppliers it is not a pulse at all (median 0.8).

## 6. Status, limits and gaps

**Status.** First landing: every announcement **day** counted. Second landing (21 Nov, 13:30,
1,715 days cached): every announcement **window**, 35 days before to 6 days after, is counted.
Third landing (21 Nov): **the whole decade is pulled**. 3,653 of 3,653 days are cached, and 20 of
them are missing at source. 515 of 523 weeks are complete, and every cap effective window is
filled (§4a). The pull has ended, and its unit is gone. The weekly series carries `days_counted` and `complete` on every week. A week that
is not complete is not a zero. The pull launched 21 Nov runs as the transient user unit
`poesys-gdelt-energy-coverage` (log: `~/.cache/synthetic-enterprise/gdelt_energy_coverage_runner/pull.log`),
so it outlives the session that started it; `systemctl --user status poesys-gdelt-energy-coverage`
says whether it is still going. If it died, resume it, then rebuild the series:

```
python3 -I tools/fetch_gdelt_energy_price_coverage.py --workers 4 --priority $(python3 -c "import json;print(' '.join(sorted({r['announced'] for r in json.load(open('docs/market_research/energy_price_announcements_gb_2016_2025.json'))['announcements'] if r['announced']})))")
python3 -I tools/fetch_gdelt_energy_price_coverage.py --aggregate
```

**Limits, each a direction of error:**

- **Precision was hand-coded on a seeded sample of 50 matched URLs: 47 were about GB household
  energy prices.** The three misses: a US petrol-price wire story (now excluded: `/wires/ap/`),
  an Australian gas story filed under The Guardian's `/environment/` section, and a pub's
  business energy bill. Expect a few per cent of noise, roughly constant across weeks.
- **Recall is not measured.** No ground truth exists. A story whose slug names neither an energy
  word nor a price word ("big-six-..."), and which GDELT did not tag, is missed. This is
  probably steady over time, so it biases the level more than the shape.
- **The BBC counts only through the theme leg.** BBC articles carry no slug, so the largest
  single news source is under-counted.
- **Print reach, broadcast and social are not counted.** The News at Six, radio phone-ins and
  social feeds reach households that never open a news site. This is a count of articles, not
  of eyeballs.
- **GDELT's own monitoring moves.** Its national-outlet volume halves between 2018 and 2022. The
  per-1,000 share removes the level change, not any change in which kinds of story GDELT keeps.

**Gaps that stay open:**

- **G1a.** Reach: how many households saw the coverage. Ofcom's News Consumption in the UK
  survey gives shares per platform, not per story. No route yet.
- **G5a.** Announcement days not found for four 2016–17 supplier changes (§3), and no second
  2018 rise found for npower or SSE.

## 7. What this changes

- **Code: no runtime code reads this.** The counter is harness-side. The world build that
  gives the announcement moment a media term (bill-shock page §7) cites this page and the series,
  and must take a coverage term at the announcement and effective moments from it, not invent one.
- **The bill-shock page's G1 is filled for announcement days, for the effective weeks and for
  a complete weekly series.** The media term has two cap pulses: the announcement (median 2.5×
  baseline) and the effective date (1.2×). Supplier changes have one pulse, the announcement
  (1.5×; the effective date reads 0.8×). The term also needs a supplier-failure event, which no
  price row carries (§4a, w/c 20 Sep 2021). Its G5 is
  filled except for the rows named in G5a. That page's §6 now points here.
