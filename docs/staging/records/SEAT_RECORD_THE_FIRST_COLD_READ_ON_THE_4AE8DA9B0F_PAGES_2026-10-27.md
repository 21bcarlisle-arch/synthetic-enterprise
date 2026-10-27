# The first cold read on what is live: the 4ae8da9b0f pages (2026-10-27)

**What this is.** Step 6 of the director's ruling of 26 Oct
(`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`). This is
the first cold read of the live Explore page and the third leg of the correctness stretch's exit
test.

**Run the pages came from:** `4ae8da9b0f` (run generated 2026-10-26T12:01:01Z). The cast was
published 2026-10-26T18:53:19Z, 752 households. `site/explore/index.html`,
`site/data/explore_cast.json` and `site/data/customers.json` were byte-identical to `origin/main`
when the read was taken.

**Independence: false.** The reader is the same model family as the builder. The blindfold gives
blindness, not independence (cold-eyes-walk, "the honest limit").

## 1. The eight Explore slots

| slot | state | household or the check that empties it |
|---|---|---|
| The switch-in | filled, 0 breaches | PROS-2025-0022 |
| The renewal | filled, 0 breaches | SYN-2016-031 |
| The estimate trap | filled, 0 breaches | PROS-2017-0264 |
| The mover | **honestly empty**, 0 matched | No move-out event, no final-bill marker, and no link from an OCC- account to the household it replaced. |
| The debt journey | filled, 0 breaches | SYN-2016-356 |
| The EV home | **honestly empty**, 21 matched, 0 pass | Fails: no full year either side of the car (16 of 21); stated effect outside 1,750–3,300 kWh (5); no rise of 1,750–3,300 kWh after the car (3); prepayment sent estimated credit bills (3); no electricity supply (1). |
| Storage heating | **honestly empty**, 96 matched, 0 pass | Fails: no profile class 2 meter on record (96 of 96); no full calendar year (34); uses less than a home that does not heat with it (27); prepayment sent credit bills (10); no winter rise (5); account id not public format (6); gas or electricity outside the 1st–99th percentile (3, 1). |
| The 2022 shock | filled, 0 breaches | PROS-2019-0246 |

Five slots are filled and three are empty, each with its failing checks named. The book carries 36
households of 752 above the cap, and none of them is shown.

**"Filled, 0 breaches" means the suite as it stood.** Section 3 shows that every filled slot carries
at least one objection the suite could not then see. So the slots are validly filled only against
the suite, not against an energy reader.

## 2. How the read was taken

1. The live page was served from `site/` and rendered in headless Chromium (Playwright from the
   main checkout's `node_modules`). For each of the eight cast tabs, every moment was clicked and the
   stage's rendered text kept. Six accounts were drawn at random from `customers.json` with
   `random.Random(20261027).sample(ids, 6)`: OCC-f6813bf9f05e, OCC-52fbc3104c5f, OCC-c40aa0e30192,
   PROS-2017-0049, SYN-2016-395 and PROS-2017-0036. Each was selected in the account picker, and the
   six stages' rendered text kept. The packet ran to 103,155 characters of page text. Its only code
   path was one the page itself prints (a carbon basis line).
2. A fresh agent (Opus) was told it was a twenty-year GB retail-energy professional. It was allowed
   to read only that packet file: no code, no repo, no commands. It wrote its priors before opening
   the file, then listed objections with a citation, a two-sided rule where one exists, and a
   severity.
3. The seat checked the quotes against the packet and then the data, after the read returned. 12 of
   14 key quotes matched verbatim. The other two ("True chance of leaving 0.0%" and the supply-point
   number) are split across lines on the page and are real. The 11-digit MPAN was confirmed in the
   record (`mpan.bottom_line = 19494047720`). The missing EBSS credit was confirmed: on this book it
   reaches no named household, and only the occupier's deemed account (d2be04371d, after this run).
4. The seat's own three observations were held back from the reader's brief: the £45.43 against
   £33.57 credit, 12 estimates in six months, and about 3.2p/kWh gas in Feb 2018. The reader found
   all three unprompted (O15, O14, O2).

## 3. What it found: 37 objections, and where each went

**New classes, written to `docs/design/DOMAIN_INVARIANTS.yaml`.** There are eight rows, each with
its source and the objection that raised it. All are `checkable: false` with the gap named, so the
runner reports UNCHECKABLE and never clean.

| invariant | objections |
|---|---|
| `INV_SVT_ONE_PRICE_PER_REGION_METHOD_WINDOW` | O1, O2: two autumn-2016 SVT electricity accounts at 13.30p and 10.16p, with the same standing charge |
| `INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23` | O22: no £400 credit on any named account |
| `INV_RENEWAL_NOTICE_42_TO_49_DAYS` | O6: renewal decided and taken on the expiry date (SLC 22C.4(a)) |
| `INV_OVERDUE_WITHIN_BALANCE` | O10, O16, O18: overdue larger than owed, and a debt stage with no miss |
| `INV_ESTIMATE_RUN_WITHIN_TENURE` | O14: 12 estimated gas bills in six months |
| `INV_COLLECTIONS_EVENTS_ORDERED` | O17: payment plan dated before the missed payment |
| `INV_STATUTE_BARRED_WRITE_OFF_AGE` | O19: whole sum barred on one date, including bills due after it (per-bill form; Limitation Act ss.5, 29(5)) |
| `INV_MPAN_CORE_FORMAT` | O31: 11-digit MPAN cores |

**Existing classes, which the suite already names, with a bound that is too loose or a finding
already open:**

- **O3**, gas SVT before 2019 at 2.67–2.96p ex-VAT. `INV_UNIT_RATE_SVT_GAS_PRE_CAP` floors at the
  commodity cost alone (1.66p for winter 2017/18), so the rate passes. The floor should take network
  and policy too, as `SEAT_FINDING_THE_DEFAULT_TARIFF_FLOOR_NOW_COVERS_GAS_AND_NETWORK_AND_POLICY_2026-10-27.md`
  does after 2019. The pre-cap rows are the next amendment.
- **O5**, a fixed rate printed as a single £/MWh for both fuels, with bills that do not follow it.
  This is `SEAT_FINDING_THE_PRINTED_RATE_AGAINST_THE_CONTRACTED_TARIFF_2026-10-26.md`.
- **O36** (from the empty-slot text): prepayment accounts sent estimated credit bills. This is
  `INV_PPM_NOT_CREDIT_BILLED`, and the slot checks are already refusing on it.
- **O19**, book-wide early write-offs. This is
  `SEAT_FINDING_A_STATUTE_BARRED_WRITE_OFF_LANDS_BEFORE_SIX_YEARS_AND_REPEATS_MONTHLY_2026-10-26.md`.
- **O33**, the smart share (17%). This is
  `SEAT_FINDING_TWO_SMART_METER_SERIES_AND_A_DISPUTED_R2_DATE_2026-10-25.md`.

**Not ranges, filed as one finding:**
`docs/staging/SEAT_FINDING_THE_FIRST_COLD_READ_FINDS_PAGE_ARITHMETIC_THAT_DOES_NOT_RECONCILE_AND_A_MARGIN_NOBODY_DEFINED_2026-10-27.md`.
It covers O4, O7–O9, O11–O13, O15, O20, O21, O23–O30, O32, O34, O35 and O37.

## 4. The verdict for the exit test

**This read found new classes: eight of them.** The exit test's third leg, "one cold read finds no
new class of error", is **not met**. This is the first read and not the last. The next read comes
after the eight rows have evaluators and a fresh run has been graded by them.

## 5. The reader's priors (P1–P11), kept as written before the read

TDCV elec 1,800/2,700/4,100 kWh and gas 7,500/11,500/17,000. Cap DD rates by window from Jan 2019 to
Jul 2025. Monthly dual-fuel bills by year, with EBSS. The SLC 21B read duty and the 12-month SLC 21BA
back-billing limit. The DD set at 1/12 of forecast, and no half-month DD. The dunning order and
Limitation Act 6 years (5 in Scotland). The SLC 22C renewal window of 42–49 days. Prepayment billing
by statement only. An E7 night share of 35–45%. An EV adding 2,000–3,500 kWh. Switching in 21 days
before CSS and about 5 days after. The full text is in the agent's return. Its plausible-checked list
covers VAT at 5%, gas carbon, T&D factors, the Feb 2025 gas bills and 2021–22 electricity bills at
the cap/EPG, most annual volumes, seasonality, hedge fractions, and the EV band.
