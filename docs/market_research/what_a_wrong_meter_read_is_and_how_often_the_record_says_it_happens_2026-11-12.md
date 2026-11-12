# What a wrong meter read is, and how often the published record says it happens (2026-11-12)

**Knowledge:** none -- no published Knowledge page covers read errors yet; this is item 1 of the front-line-gaps steer (`DIRECTOR_STEER_KNOWLEDGE_FIRST_FRONT_LINE_GAPS_2026-11-10.md`). It sits beside `meter_read_latency_estimation_2026.md`, which covers whether a read *arrives*; this page covers whether an arrived read is *right*.

**The question.** The steer asks how often customer self-reads are wrong (transposed digits, misread dials, the
wrong register), how often registers roll over, how common crossed meters are, and what the Ombudsman says about
disputed usage. It also asks whether the item matters, and where it lives (world, company or both).

**The answer in one paragraph.** The published GB rules name every kind of read error precisely: BSCP504 for
electricity and the UNC Validation Rules for gas. They also say what a data collector does about each one. **No
published source gives a frequency for any of them.** That includes the share of customer reads that are wrong,
the share rejected by validation, crossed meters, and register rollovers. Billing is the largest category of
Energy Ombudsman cases in every year read (56-74%), but the Ombudsman does not split billing into reads,
estimates and meters. **So the world cannot yet draw read errors "at the published rates", because there are
none.** Under the knowledge-first rule the world build waits on a sourced rate. The company side (validation
rules) can be built from the published rules, but it has nothing to catch until the world makes an error. Meter
*accuracy* disputes are measured, and they are too rare to matter at our book's size (section 5).

**Sources.** All were fetched and read on 12 Nov 2026 unless marked otherwise. Quotes are verbatim. Two of them
were re-fetched independently and checked word for word: BSCP504 4.2(5) and 4.6(3)/(4), and the OPSS accuracy-dispute
page.
- Elexon, BSCP504 *Non Half Hourly Data Collection for SVA Metering Systems registered in SMRS* v53.0 (effective 1 Oct 2024; since superseded by v54.0, which was not read). <https://bscdocs.elexon.co.uk/bsc-module/bsc-procedures/bscp504-non-half-hourly-data-collection-for-sva-metering-systems-registered-in-smrs/v-53-0/id-66f6cb1c02d68a93ba93b17e>
- Joint Office, *Uniform Network Code Validation Rules* v9.0 (live 24 Feb 2024). <https://www.gasgovernance.co.uk/sites/default/files/related-files/2024-03/uniform_network_code_validation_rules_v9.0live_-_implementation_in_line_with_0811s_24_february_2024.pdf>
- Xoserve, *Guidelines for Submitting Gas Meter Readings* v3.0 (Jul 2025). <https://umbraco.xoserve.com/media/31np45bc/submission-of-meter-readings-guidelines-v3.pdf>
- Joint Office PAC, *Performance Assurance Framework Document* v5.6, PARR Appendix 1 (Mar 2026 PAC pack).
- Energy Ombudsman (Ombudsman Services / Trust Alliance Group) annual reports 2016, 2017, 2018, 2019, 2023, 2024, 2025; metering case study "Consumer was being billed to neighbour's meter" (18 Nov 2022). <https://www.energyombudsman.org/case-studies/metering>
- Citizens Advice, "How to read your energy meter" and "Find out if your energy meter is faulty" (consumer pages, undated).
- OPSS, "Electricity meter accuracy disputes" (gov.uk, updated 2 Jul 2018) and "Gas meter readings and bill calculation" (updated 10 Jun 2014); OPSS Delivery Reports 2022/23, 2023/24, 2024/25.
- Meters (Certification) Regulations 1998 (SI 1998/1566); Gas (Meters) Regulations 1983 (SI 1983/684), as made.

## 1. The kinds of wrong read, as the industry rules name them

BSCP504 s.4.6, "Manual Adjustment of Meter Reading(s)", lets the electricity data collector correct a read "where
the NHHDC is able to establish beyond reasonable doubt" one of the following. This is the error taxonomy, written
by the people who correct the errors:

| # | Error | BSCP504 s.4.6 wording | Correction |
|---|---|---|---|
| 1 | Register swap (day and night on an Economy 7 meter, for example) | "Meter register readings were incorrectly allocated to the Meter register identifiers by the customer or Meter reader" | Reallocate the readings to the right registers |
| 3 | The tenths digit appended | "the 'one tenth kWh' register digit has been incorrectly added to the end of the Meter register reading" | Remove the digit (the read is about 10x too large) |
| 4 | Adjacent digits transposed | "two adjacent register digits have been erroneously transposed by the customer or the Meter reader" | "re-order these two register digits" |
| 5 | Dial rounding | "one or more of the dials on an analogue Meter register has been rounded up rather than down, or vice versa" | Correct the dial |

Citizens Advice's reading guide shows where a lay reader goes wrong:
- "If there's an 'N' on the label this will stand for 'normal' - it doesn't stand for 'night'" (the register swap);
- "ignore any red dials or dials marked 1/10" (the tenths digit);
- a pointer between 9 and 0 means "reduce the number you've underlined by 1" (dial rounding).

Reading **the wrong meter** is a different error. It is caught by the serial-number check (BSCP504 4.2(1); Xoserve
rejection code MRE00419, serial mismatch), not corrected in place.

## 2. What validation does with a read (electricity and gas)

**Electricity (BSCP504 s.4.2, minimum steps).**
1. The serial number matches the one the meter operator holds.
2. The read date is after the last valid read.
3. Zero consumption is checked.
4. A negative advance is checked "for Meter rollover" and for a deemed previous read.
5. "Check consumption/generation does not exceed **twice the expected advance**" (expected = EAC x profile
   coefficient). A read above that "will fail validation", except for a seasonal register.

A failed read can still be set valid "where good reason exists". The annualised advance is also checked against
Profile Class tolerances held in Market Domain Data. Those values are GSP-group specific and are not in BSCP504
itself, and a breach there is only a warning.

**Gas (UNC Validation Rules v9.0, s.8.2, Class 3 and 4 after an actual read).** Each read is checked against a
percentage of (AQ/365 x days elapsed), banded by AQ:

| AQ band (kWh) | Accepted | Accepted only with an override flag (Inner Tolerance) | Rejected by the CDSP (Outer Tolerance, "Market Breaker") |
|---|---|---|---|
| 1,001-5,000 | 0-400% | 401-7,000% | >7,000% |
| 5,001-10,000 | 0-200% | 201-2,000% | >2,000% |
| 10,001-20,000 | 0-150% | 151-1,100% | >1,100% |

For a typical domestic gas AQ (5,001-20,000 kWh), the industry only *rejects* a read that implies 11 to 20 times
the average daily use. A transposed digit in a high place passes the industry check unless the supplier's own
validation catches it. s.2.5.1(a) adds that the CDSP does not apply the Inner Tolerance to Class 3 reads, except
for check reads after a site visit. Xoserve's rejection codes include:
- MRE00457, a read lower than the previous one;
- MRE01026 and MRE01027, the lower and upper Outer Tolerance;
- MRE01029, the lower Inner Tolerance without an override.

## 3. Rollover

- **Electricity.** A negative advance is checked for rollover first (BSCP504 4.2(4.1)). Both mistakes are named
  and recoverable: "failing to recognise a Meter register rollover or incorrectly assuming a rollover from a
  negative advance". The read stays valid and the advance is recalculated. If the error reached settlement, it is
  corrected by Gross Volume Correction.
- **Gas ("Round the Clock", UNC Validation Rules Appendix A).** "For meters with 5 or more dials the reading will
  assumed to have gone forward unless the previous reading is an estimate." The more-than-one-revolution test
  applies only to 4-dial meters, or where the previous read is an estimate. "A customer reading will be treated as
  an actual reading for the purpose of this test."
- **How many digits GB meters have.** Electricity has "5 or more dials", or 5 digits plus red ones. Gas has "4 or
  more dials", or 4 digits plus 2 red ones on imperial and 5 on metric (Citizens Advice). OPSS says "a significant
  number of imperial gas meters ... are still used for billing". **No published stock split by digit count, or of
  imperial against metric, was found: GAP.**

At domestic use, a rollover is rare by arithmetic, not by evidence. A 5-digit kWh register wraps after 100,000
kWh, which is about 37 years at a typical 2,700 kWh a year. A 4-digit imperial gas register wraps after 10,000
hcf, about 283,000 m3, so decades at domestic use. This is a bound, not a sourced frequency. It is enough to say
rollover is not a decade-scale event for our book.

## 4. Crossed meters

**What it is.** The registration points the meter record at a meter that is not the one wired to the premise.
The Energy Ombudsman's case "Consumer was being billed to neighbour's meter" (2022) is the mechanism, in a block of
flats. The meter labelled flat 11 matched the record, but a filmed burn test showed flat 12's meter was the one
connected. The supplier "had not effectively investigated the issue over a long period". The Ombudsman required a
re-bill on the correct meter's reads and a "significant time and trouble award".

**How often: GAP**, already recorded as row 60 of
`unbilled_energy_what_suppliers_do_and_what_customers_meet_2026-10-30.md` ("No Ofgem or Elexon count found"). It is
re-confirmed here. No RECCo, Ofgem, Citizens Advice or Elexon count was found. The REC Metering Operations
documents that would carry the resolution process and timescales returned 404 when fetched directly, so that is a
GAP too.

## 5. Meter accuracy disputes

- **Legal tolerance.**
  - Electricity: "an error not exceeding plus 2.5 per cent. or minus 3.5 per cent." (SI 1998/1566). Whether that
    is also the in-service limit for MID-approved meters was not traced.
  - Gas diaphragm meters: within 2% across the working flow range (SI 1983/684, as made; later amendments not
    checked).
- **The process.** An OPSS independent examiner tests the meter in the supplier's presence. The meter is replaced
  and lab-tested. The test is free, but "you may have to pay your energy supplier for organising it if your meter
  is found to be working correctly, which was the case for the vast majority of meters tested in 2021". Citizens
  Advice puts that charge at "around £200" and says "Meter faults are rare".
- **How many.** OPSS ran about 1,000 independent dispute tests in 2022/23 (a 27% rise), 1,286 in 2023/24 and 782 in
  2024/25. "The overwhelming majority" of meters were within limits. The fail share is not quantified in the
  report text, and the statistical annex was not read: GAP.
- **Does it matter for us?** The numerator is GB disputed-meter tests a year (about 800-1,300). The denominator is
  GB meters: 57.9m domestic and smaller non-domestic at end 2024 (DESNZ). That is about 1.4 to 2.2 tests per
  100,000 meters a year, and most find the meter accurate. On a book of about a thousand supply points over ten
  years, the expected number of *disputes* is about 0.2, and the expected number of meters *found faulty* is
  smaller still. **It does not matter at our scale.** The page recommends no build for meter accuracy.

## 6. What the Ombudsman says about disputed usage

| Year | Billing share of cases | Note |
|---|---|---|
| 2016 | 74% | 88,255 initial contacts |
| 2017 | 57% | |
| 2018 | "over 60%" | "most issues relating to estimated billing and loss of smart meter communications" |
| 2019 | not quantified | "the most frequent complaint type" |
| 2020-2022 | not found | the text layer of those reports carries no category table: GAP |
| 2023 | not quantified | top categories, in order: Billing, Smart Meters, Customer services, Payments/Debt, Meters |
| 2024 | 58% | "Many of these cases involved consumers questioning the amount of gas or electricity they had been charged for"; 92,938 cases |
| 2025 | 56% | 45,293 of 80,256 accepted; also Smart Meters 11%, Standard Meters 2% |

Billing is never split into wrong reads, estimates and meter faults: GAP. The Xoserve PAC monthly
meter-read-validation report defines an industry rejection percentage per shipper (codes MRE01026-01030, logic
and value failures). It is the likeliest source of a real rejection rate, but the published framework document
carries only the template. The data is in PAC packs or the Xoserve Data Discovery Platform, which were not
reachable.

## 7. Where it lives, and what our code does today

- **World.** `simulation/meter_reads.py::simulate_read` returns an `actual` read whose quantity is exactly the true
  consumption. **No read the world gives is ever wrong.** A wrong read is a world fact: the household or the meter
  reader makes it, and the supplier sees only the number. So any error draw belongs in the world.
- **Seam.** Only the read value and its source cross: customer, meter reader or smart. The fact that the read is
  wrong, and why, never crosses. The company may know only what validation and the read history let it infer
  (BSCP504's "beyond reasonable doubt").
- **Company.** `company/billing/meter_read_validation.py` exists, but it is reached only by name, from
  `company/compliance/obligations_register.py`, and is wired into no run. Read against the published rules, it has
  three defects:
  - its "transposition" check moves the *last digit to the front*, which is a rotation. BSCP504's error is "two
    adjacent register digits ... transposed";
  - it rejects above **3x** the expected daily use. BSCP504 4.2(5) fails a read above **2x** the expected advance,
    and gas uses the banded UNC tolerances in section 2, not one multiple;
  - it has no serial-number check, no register-swap check and no appended-tenths check.

  It is latent, because nothing runs it. These are recorded here for the build slice, not filed as a finding.

## 8. Recommendation, and what the build slice is

1. **World read errors: held on a GAP, not closed.** The steer's slice ("World draws read errors at the published
   rates") cannot be built honestly, because no published rate exists. The next question goes, in order, to:
   - the Xoserve PAC rejection data (gas);
   - Elexon Performance Assurance reporting on NHH reads failing validation (not yet searched);
   - the practitioner (K4): "what share of customer-submitted reads does a supplier's validation reject or
     correct?"

   Until one answers, the world's reads stay exact, and the honest statement is that our estimate-to-actual
   true-ups never meet a wrong actual.
2. **Company validation: buildable from the published rules, but ordered behind (1).** The validator can be
   corrected to BSCP504 4.2 and 4.6 and the UNC bands without inventing a number. But a validator facing a world
   that never errs is a control that cannot fail in the run. So it should land in the same slice as the world's
   error draw, not ahead of it.
3. **Rollover and meter accuracy: no build.** Both are too rare at our book's scale (sections 3 and 5), and the
   page says so, which closes them under the steer's own rule.
4. **Crossed meters: GAP.** Its first build would be a world fact (a supply point whose reads come from another
   household's meter), and it needs a prevalence first.

## Reverse

Delete this file, its ASSUMPTIONS.md rows and its knowledge_map row.
