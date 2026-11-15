# Who is eligible for the Priority Services Register, and when a supplier may not disconnect

**Type:** REGULATION COMMONS artefact. The regulatory TEXT is a shared commons readable by every
lane, because law is published in reality (`docs/design/REGULATION_COMMONS_DOCTRINE`). Each lane's
*reading* of it stays independently owned; what is recorded here is the text and the citation, not
an interpretation anyone is bound to.

**Why it exists.** `company/crm/` and `company/regulatory/` between them hold five separate
vocabularies for one Ofgem obligation, disagreeing on every overlapping term and on the numeric
weight attached to it (`SEAT_FINDING_ONE_OFGEM_OBLIGATION_HAS_TWO_VULNERABILITY_SCORERS_THAT_DISAGREE_AND_THE_DEAD_ONE_DECIDES_DISCONNECTION_2026-09-05.md`,
census corrected from two to five in
`SEAT_RESULT_THE_OBLIGATION_HAS_FIVE_IMPLEMENTATIONS_AND_THE_ONE_MATCHING_THE_REGULATOR_HAS_NO_CALLER_2026-09-05.md`).
Choosing between them by picking whichever enum was written first is exactly the failure CLAUDE.md
names. **Which terms carry priority-services registration and disconnection protection, and on what
thresholds, is a published question.** This file answers the published part of it, and is explicit
about the part the published record does not answer.

**Fetched, not recalled, 2026-09-05.** Where a claim could not be sourced it is marked `UNSOURCED`
and carries no citation rather than a plausible one.

| # | source | what was read |
|---|---|---|
| S1 | Ofgem, *Gas Supply Standard Consolidated Licence Conditions* (ofgem.gov.uk/sites/default/files/2025-08/Gas-Supply-Standard-Consolidated-Licence-Conditions.pdf) | SLC 26 is the Priority Services Register condition; SLC 27 is *Payments, Security Deposits, Disconnections and final Bills*. **The condition text itself could not be extracted** — the fetch returned Ofgem's navigation hub, not the PDF body. Structure below is therefore sourced from S2–S5, and the licence-condition numbering from S2/S4 rather than from the instrument. |
| S2 | Ofgem, *Priority Services Register Review — Final Proposals* and *statutory consultation* (ofgem.gov.uk/sites/default/files/docs/psr_final_proposals_final_0.pdf; .../2016/06/priority_services_register_statutory_consultation_and_proposals.pdf) | SLC 26 replaced the former "Services for specific Domestic Customer groups" condition in 2016; draft SLC 26.1(a) refers to *"a vulnerable situation"*; standardised industry **needs codes**; needs codes are agreed via the ENA Customer Safeguarding Working Group and must stay consistent across the industry |
| S3 | Uswitch, *Priority Services Register (PSR)* guide (uswitch.com/gas-electricity/guides/priority-services-register/) | the eligibility category list, the core services list, and the explicit absence of any scoring system |
| S4 | Citizens Advice / adviser guidance and UK Parliament written answers reached via search (citizensadvice.org.uk; questions-statements.parliament.uk/written-questions/detail/2022-03-23/145819) | winter months are October–March; the pensionable-age winter prohibition is cited to SLC 27.10 |
| S5 | Energy UK, *Vulnerability Commitment* / "Safety Net" as described by S4 and Changeworks (changeworks.org.uk) | a **voluntary** supplier pledge, not a licence condition: never knowingly disconnect where welfare cannot be safeguarded due to age, health, disability or severe financial insecurity |
| S6 | Ofgem press release, *More customers in vulnerable situations to receive help under the Priority Services Register*, **25 October 2016** (ofgem.gov.uk/press-release/more-customers-vulnerable-situations-receive-help-under-priority-services-register) | **fetched 2026-09-06**, closing the `UK_PSR_RATE_PCT` gap opened in §4. Verbatim: *"Around 3.6 million electricity and 3 million gas customers (13% of customers for both fuels) are signed up to suppliers' Priority Services Register."* Ofgem's *Consumer impacts of market conditions* survey (Jan–Feb 2024, reported in the Consumer Vulnerability Strategy Refresh consultation, Sept 2024) separately finds **~40% of households could access PSR support but have not signed up**. The 2025 Consumer Vulnerability Strategy decision PDF defeated automated extraction, as the licence conditions did — no current registered rate is sourced here. |
| S8 | Ofgem, *Modification direction for the insertion of standard licence condition 27.11(A) in the gas and electricity supply licences*, 15 Sep 2010, effective 1 Oct 2010 (ofgem.gov.uk/sites/default/files/docs/2010/09/modification-direction-for-insertion-of-standard-licence-condition-27.11%28a%29-in-the-gas-and-electricity-supply-licences.pdf) | **fetched and read in the instrument 2026-11-14.** Its Schedule 1 prints SLC 27.10, 27.11 and 27.11(A) as modified, for gas (p. 3) and electricity (p. 4). Verbatim, electricity: *"27.11 The licensee must take all reasonable steps to avoid Disconnecting, in Winter, a Domestic Premises at which the Domestic Customer has not paid Charges for the Supply of Electricity if the occupants of the premises include a person who is of Pensionable Age, disabled or chronically sick and to whom paragraph 27.10 does not apply."* 27.11(A): before exercising any right to disconnect, *"take all reasonable steps to ascertain whether"* 27.10 or 27.11 applies. The 15 Jul 2010 notice records Ofgem declining to require reconnection before Winter of a vulnerable household disconnected at another time of year. |

---

## 1. PSR eligibility — SLC 26

Eligibility is expressed as **categorical needs codes**, standardised across the industry so a
customer's record can be shared with the network operator and with other utilities. The categories
read from S2/S3:

| needs category | notes from the source |
|---|---|
| of pensionable age | the criterion is *pensionable age*, not a fixed birth-year or a fixed age number |
| disability | |
| chronic illness / long-term medical condition | |
| medical equipment dependency | reliance on electrically-powered medical equipment |
| hearing or visual impairment, or other communication needs | |
| children under five in the household | ENA agreed to **remove the `pregnancy` code** and keep a single "families with children < 6" need code — so the published boundary has moved and the sources disagree between "under five" and "under six" |
| a mental health condition causing difficulty understanding the bill | |
| unable to top up a prepayment meter due to injury | |
| temporary need arising from extenuating circumstances | the "vulnerable situation" limb of SLC 26.1(a) — explicitly **non-permanent** |

### 1a. The industry needs-code list (added 2026-10-08)

**Source S7:** Ofgem, *Consumer Vulnerability Strategy*, Apr 2025, Appendix 6, PDF pp. 61–62
(ofgem.gov.uk/sites/default/files/2025-04/Final%20CVS%2015042025-20250414111309.pdf). Fetched
2026-10-08. This answers C32 Expert Hour finding EH-3, which said the needs-code list was not in the
commons. Codes 5–7, 11, 13, 16 and 21 are absent from the published list.

| code | need | code | need |
|---|---|---|---|
| 1 | Nebuliser and apnoea monitor | 22 | Chronic/serious illness |
| 2 | Heart, lung & ventilator | 23 | Medically dependent showering/bathing |
| 3 | Dialysis, feeding pump and automated medication | 24 | Careline/telecare system |
| 4 | Oxygen concentrator | 25 | Medicine refrigeration |
| 8 | Blind | 26 | Oxygen use |
| 9 | Partially sighted | 27 | Poor sense of smell/taste |
| 10 | Do Not Use | 28 | Restricted hand movement |
| 12 | Stair lift, hoist, electric bed | 29 | Families with young children 5 or under |
| 14 | Pensionable age | 30 | Mental health |
| 15 | Physical impairment | 31 | Additional presence preferred |
| 17 | Unable to communicate in English | 32 | Temporary – Life changes |
| 18 | Developmental condition | 33 | Temporary – Post hospital recovery |
| 19 | Unable to answer door | 34 | Temporary – Young adult householder (<18) |
| 20 | Dementia(s)/Cognitive impairment | 35 | Hearing impairment (inc. Deaf) |
| | | 36 | Speech impairment |
| | | 37 | Water dependent |

The same document says the PSR's codes are *"limited/specific ... relevant to safety and off supply
situations, many circumstances or characteristics are not captured by the PSR"*. Financial
vulnerability has no code. Prevalence, registration and the arrears overlap are in
`docs/market_research/debt_and_collections.md` §10.

### 1b. From a needs code to a needs category (added 2026-11-14, C32 Expert Hour re-take)

**This is a reading, not published text.** S7 publishes code names. It does not publish a mapping
to the nine categories in §1, and none was found. The rule applied here is the one
`needs_code_for` already applies to agents' flags. A code establishes a category only where its
published name is that category's concept. Where the concept overlaps but the name does not
establish the criterion, the grade is "cannot determine", with the missing criterion named. Codes
that match no category stay PSR needs: the household is still on the register, but the code
carries no category term.

| grade | codes → category | why |
|---|---|---|
| establishes | 14 → pensionable age; 29 → child 5 or under; 30 → mental health; 35 → hearing impairment; 8, 9 → visual impairment; 17 → language support; 32 → temporary life changes; 1, 2, 3, 4 → electrically-powered medical equipment | The code name is the concept. Codes 1 to 4 each name a device that runs on mains power. |
| cannot determine | 22 → chronic illness | "Chronic/serious": a serious acute illness is not established to be chronic, which is the same grade as the `serious_illness` flag. |
| cannot determine | 15, 18, 20 → disability | Physical impairment, developmental condition and dementia/cognitive impairment overlap disability. The code does not establish that the licence's term "disabled" applies. |
| cannot determine | 12, 23, 24, 25, 26 → medical equipment | Each names a dependency. None establishes electrically-powered *medical* equipment: 12 is mobility equipment and 26 is oxygen use, not a concentrator. |
| no category | 19, 27, 28, 31, 33, 34, 36, 37 | A PSR need with no category term. 36 (speech) is covered by §1's "other communication needs", which the supplier's ten categories do not hold. |
| refused | 10 ("Do Not Use"), and 5–7, 11, 13, 16, 21 (absent from S7) | Not a live published code. |

**A registration that names no code** establishes registration, not a need. S7's note that PSR
codes concern "safety and off supply situations" makes registration itself a reason to believe
the household has some need. Which need cannot be read from it. **Design choice, not published:**
the supplier treats a registered household with no recorded need as "cannot determine" for
disconnection, never as "not established". A blind practitioner (2026-11-14) would map bereavement
to code 32 as routine. That is K4's starting point, not a source, so the grade stays.

Core services conferred by registration (S3): alternative billing formats (large print, Braille,
audio); advance notice of supply interruption; priority reconnection after an interruption;
quarterly meter readings; free annual gas safety check; password scheme; nominee arrangements.

## 2. Disconnection protection — SLC 27, plus a voluntary commitment

- **Winter months are October, November, December, January, February and March** (S4).
- A supplier **must not** disconnect a domestic customer of pensionable age during the winter
  months where that customer lives alone, or lives only with others of pensionable age or under 18
  (S4, cited there to **SLC 27.10**).
- Outside that prohibition the duty is weaker in kind: **all reasonable steps** to avoid
  disconnecting, **in Winter**, premises whose occupants include a person who is disabled,
  chronically sick, or of pensionable age (SLC 27.11, read in the instrument, S8). **Both licence
  limbs are winter duties.** From April to September the licence sets no disconnection protection
  on these grounds; what protects such a household then is the voluntary Safety Net below.
  *(Corrected 2026-11-14: this bullet, from S4, gave the limb no season, and the code applied it
  all year.)*
- Before any disconnection the supplier must take all reasonable steps to find out whether 27.10 or
  27.11 applies (SLC 27.11(A), S8, in force from 1 Oct 2010). That is the licence ground for the
  code's rule that "cannot determine" blocks disconnection: an unasked question is an unmet duty.
  **Holding no evidence is not having asked** *(corrected 2026-11-15, C32 seventh pass)*. The
  code had read this duty only where something was on record. On 15 Jan 2024 it permitted
  disconnecting a household it held nothing on: no registration, no flag, no birth date. Such a
  household may be an 80-year-old living alone, whom 27.10 prohibits disconnecting. The company
  has no ascertainment step and keeps no record of one. So in a winter month, any household not
  already protected reads "cannot determine" under 27.11(A). From April to September, 27.10 and
  27.11 do not apply, so 27.11(A) has nothing to ascertain and the licence sets no bar.
- Disconnection for unpaid charges is in any case only available once repayment options have been
  offered and the available means of recovering the debt exhausted (S4).
- **Energy UK Vulnerability Commitment / "Safety Net"** (S5): a **voluntary** pledge, all year
  round, not to knowingly disconnect a customer who cannot safeguard their own or their
  household's welfare due to age, health, disability or severe financial insecurity. It is a
  commitment, not a licence condition, and a supplier that has not signed it is not bound by it.

## 2a. What "pensionable age" is, and what it means at a given date (C32 EH-5, added 2026-11-13)

**Read on 2026-11-13. Each line below is marked with how it was read.**

- **The licence defers to statute (S9, from a search snippet; not read in the instrument).** The
  supply SLC definitions give "Pensionable Age" as, in relation to any person, pensionable age within the meaning
  given by **section 48(2B) of the Gas Act 1986**. This wording appears in Ofgem's consolidated
  electricity and gas supply conditions (2020 and 2024 copies, found via search). The §4 caveat
  still applies: no clause text was read in the instrument.
- **The statute (S8, fetched verbatim from legislation.gov.uk/ukpga/1986/44/section/48,
  revised to 13 Nov 2026).** s.48(2B): *"A person is of pensionable age for the purposes of this
  Part if— (a) he has attained pensionable age (within the meaning given by the rules in paragraph 1
  of Schedule 4 to the Pensions Act 1995); or (b) in the case of a man born before [6th December
  1953], he is the same age as a woman who has attained pensionable age (within the meaning so
  given)."* The bracketed date was substituted by the Pensions Act 2011 (in force 3.1.2012).
- **What follows from that text, as strong logic and not as a published reading:**
  1. **It is a date-of-birth rule, judged on the decision date.** No fixed age number is
     correct across 2016–2025. The commons already refuted 75; any constant 65 or 66 is refuted
     the same way.
  2. **Limb (b) makes the licence age lower than a man's own State Pension age** for older
     cohorts. A man born before 6 Dec 1953 qualifies when he reaches the age at which a woman of
     his birth date would. Under that rule a man born in 1953 became protected somewhere between
     about 63 and 65, depending on his birth month, while his own State Pension age was 65. (The
     exact months need the Schedule 4 tables, which were not transcribed.) A rule written as "the customer's State Pension
     age" therefore **under-protects** him, in the direction that removes protection.
  3. **It is monotone.** Once a person is of pensionable age they stay so: a later Act moves the
     age only for cohorts that have not reached it yet. So a code-14 flag that was correct when
     set never expires. Age only matters for a household not yet flagged.
- **The timetable across the run window (S10, from the Pensions Act 2011 explanatory notes and
  a gov.uk policy paper, reached by search; the Schedule 4 cohort tables themselves were not
  transcribed):** women's State Pension age rose from 60 to 65 by **November 2018**. Men's and
  women's then rose together to **66 by October 2020**. The Pensions Act 2014 rise to 67 runs
  2026–2028, outside the window. So in 2016–2018 the youngest person of pensionable age was a
  woman (or, by limb (b), a man born before 6 Dec 1953) in her early-to-mid sixties. From
  October 2020 to the end of 2025 the threshold is 66 for everyone.
- `GAP` **Whether a supplier holds date of birth.** Nothing in the published record read here
  says a supplier must or does hold DOB for every domestic customer. The industry carrier for
  this circumstance is **needs code 14, "Pensionable age"** (S7), which is a flag on disclosure,
  not a birth date. The one internal mention
  (`which_supplier_observable_recovers_precarity_understanding_society_2026-11-09.md`, O5) says
  "held where the customer gave a date of birth", which is a design assumption, not a source.
  **Design consequence for `company/`:** the decider reads the code-14 flag (point 3 makes that
  sound). Where a DOB is held, a computed flag must use the s.48(2B) rule *including limb (b)*.
  Where neither is held, the answer is CANNOT_DETERMINE, never "not pensionable".
  *Code, 2026-11-14 (C32 EH-5):* `priority_services_register.pensionable_age_from_birth_date`
  encodes only the bounds this section establishes (never below 60; always from 66; the floor
  rises to 65 from Dec 2018 and 66 from Nov 2020) and answers CANNOT_DETERMINE inside the band,
  which holds a disconnection wherever the answer would change it. **The last sentence above is
  NOT yet what the decider does:** a customer with no flag and no DOB still reads "not
  established", as before EH-5, because applying it would hold every winter disconnection in the
  book. Whether that is right turns on whether the SLC 27 prohibition is limited to customers the
  supplier knows (or should know) are of pensionable age, which is the clause-text gap in §4.

## 3. What the published record does NOT establish — and this is the load-bearing part

**No published source read here assigns a numeric severity weight, score, or ranking to any of
these categories.** S3 states it directly: no numeric scoring or ranking system is applied; the
assessment is of individual circumstances, and suppliers have discretion about what support fits.

Three consequences, each of which decides a live question in the code:

1. **Every weight in `company/` is ours, and none of them is a regulatory determination.**
   `vulnerability_register._FLAG_SEVERITY_WEIGHT` (1–5) and the deleted
   `vulnerability_index._INDICATOR_SCORE` (10–60) are both unsourced. They are not two readings of
   a published scale; there is no published scale. They may order our own triage queue. They may
   not decide a regulatory outcome.
2. **The regulatory outcomes are categorical, and one of them is seasonal.** PSR eligibility is
   membership of a needs category. Disconnection protection turns on the category, the household
   composition, **and the date** — a rule no numeric band can express. `vulnerability_index`
   derived `disconnection_protected` from `band == CRITICAL`, i.e. from a score of 60, reached by
   `HOME_OXYGEN` alone or by any combination summing to 60. That is not the published rule and does
   not resemble it; it has no seasonal term at all.
3. **Two invented thresholds are refuted, not merely unsourced.** `ELDERLY_75` (score 20) asserts an
   age threshold of 75: the published criterion is *pensionable age*, which is neither 75 nor a
   fixed number. And promoting `MEDICAL_EQUIPMENT` to automatic disconnection protection all year
   is *stronger* than SLC 27.10 and *weaker* than the Energy UK commitment, matching neither.

## 4. Named gaps — questions this artefact opened and did not close

- `UNSOURCED`: the SLC 26 and SLC 27 condition text itself, **except 27.10, 27.11 and 27.11(A),
  read 2026-11-14 in the 2010 modification direction (S8)**. Whether that wording was amended
  between 2016 and 2025 is not read: the 2022 written answer (S4) still cites 27.10 for the winter
  prohibition, which is consistent with no change, and is not proof of it. Other numbering rests
  on secondary sources (S2, S4). The consolidated PDF is 600+ pages and defeated automated extraction; reading
  it is real work and is not done. **Nothing should quote a clause number from this file as if it
  had been read in the instrument.**
- ~~`UNSOURCED`: whether the child needs code is "under 5" or "under 6"~~ — **CLOSED 2026-10-08.**
  The current published list (S7, code 29) reads *"Families with young children 5 or under"*.
  That includes a five-year-old, so it means under six, which matches S2's ENA agreement. S3's
  "under five" is the consumer guide's loose wording. A child qualifies up to and including age 5.
- `UNSOURCED`: **Warm Home Discount eligibility is a separate obligation and was not researched.**
  `warm_home_discount.whd_eligible_customers` currently treats *any* active vulnerability flag of
  *any* type as WHD-eligible. WHD Core and Broader Group eligibility are defined by benefit receipt
  and property cost, not by PSR need — so that function is almost certainly wrong, and it decides
  a real payment on the live portal. It is named here as the next research question, not answered.
- ~~`UNSOURCED`: `PriorityServicesRegister.UK_PSR_RATE_PCT = 31.0`~~ — **CLOSED 2026-09-06, and the
  number was wrong.** No published figure supports 31% of domestic customers being *registered*.
  The sourced registered share is **13%** at 25 Oct 2016 (S6); the nearest thing to a 31 in the
  record is the ~40% who *could* access PSR support and have not signed up, which is the **eligible**
  share, not the registered one. Two different quantities, and the constant was named for neither —
  the *before dividing two numbers, say what each one counts* shape, in the form of a benchmark
  whose subject was never stated. Replaced by `UK_PSR_REGISTERED_PCT_2016` carrying
  `UK_PSR_REGISTERED_PCT_AS_OF`, and reached by `penetration_against_published`, which returns the
  date and a staleness flag beside the figure so the nine-year gap cannot be dropped in transit.
- **Partly closed 2026-10-08:** the latest admin count found is end-2018, 6,703,753 electricity
  (24%) and 5,646,740 gas (24%) (Ofgem, *Vulnerable consumers in the energy market: 2019*, p. 16).
  Ofgem's 2024 survey has 16% self-reporting registration. Post-2018 admin counts are still a GAP;
  see `debt_and_collections.md` §10.2.
- ~~`UNSOURCED`, opened 2026-11-14: whether the all-reasonable-steps limb is winter-only.~~
  **CLOSED the same day: it is.** SLC 27.11 reads "in Winter" in the instrument (S8). Two blind
  practitioners read it that way, on 14 Nov and on the third pass. The code had applied it all year
  and called that "the published rule". **Design choice:** the decider returns the licence's
  answer. Outside winter, disabled, chronically sick and pensionable age establish no licence
  protection, and the reason string names the voluntary Safety Net (S5) as ~~not modelled~~ applied by the company in its own layer (corrected 2026-11-14). Medical
  equipment alone follows the same counterfactual: its "cannot determine" asked whether the
  household is also disabled or chronically sick, which outside winter changes nothing. Whether
  this supplier should adopt the Safety Net is a policy question for the company, not a reading of
  the licence. ~~It is not decided here.~~ **Decided 2026-11-14, C32's fourth blind pass:** the
  company adopts it, in its own layer (`WinterMoratoriumRegister.can_disconnect`), not in the
  licence decider. Grounds: canon M3, "Comfort and health are a floor, not a weight: no gain ...
  justifies a breach", and the fourth reviewer's practitioner prior that every large supplier
  operates the Safety Net (S5), so a supplier without it is less protective than the market it is
  modelled on. Operationalised as: outside winter, a household holding disability, chronic illness,
  pensionable age or medical-equipment dependence is not disconnected. S5's wider ground, "severe
  financial insecurity", is a welfare judgement with no category; it is **not modelled** (GAP).
  The licence decider still returns the licence's answer, so the two stay separately readable.
  **Amended 2026-11-14, before C32's fifth pass:** as first built, the net read established
  categories only. The counterfactuals that make a hint block (an undetermined needs code or agent
  flag, a registration naming no need, a birth date) ran against the licence alone. So in July a
  household whose only evidence was code 26 "oxygen use", code 22, a no-need registration, a
  `serious_illness` or `elderly` flag, or a birth date making it 80 was permitted. **Design
  choice:** the company's decider (`winter_moratorium.safety_net_protection`, licence then net)
  runs the same counterfactuals. A hint that would fall under the net, if established, reads
  "cannot determine" all year and blocks. A birth date that establishes pensionable age falls
  under the net, and one in the untranscribed band reads "cannot determine". `can_disconnect`
  takes the household's record. This is strong logic from the §2 rule that "cannot determine"
  blocks, applied to the company's own policy; no source sets it.
  **Amended again 2026-11-14, C32's fifth pass, item 5.** S5 is a *welfare test* ("cannot
  safeguard ... due to age, health, disability or severe financial insecurity"), not membership of
  a category. Any categorical reading diverges from it in both directions. The divergence, named:
  - **Over-protection.** Every household holding a net category is refused, with no assessment of
    whether it can safeguard its welfare. A fit 67-year-old is refused.
  - **Under-protection.** A household on none of those categories, but unable to safeguard its
    welfare, is not caught. Sensory impairment, language, temporary life changes and the eight
    uncategorised needs (for example post-hospital recovery) are outside the net. So is severe
    financial insecurity (GAP).
  - **The design choice.** Mental health joins the net on the "health" ground, which is the plain
    reading of S5's words. A child five or under joins on the "age" ground, as a stated belief that
    errs toward protection on canon M3's floor. No source maps S5 to needs codes.
  - **What it costs.** It is reversible by deleting the two categories from
    `SAFETY_NET_CATEGORIES`.
  - **Not built.** A welfare assessment, which is what S5 actually asks for, is not built. It is the
    practitioner question for the collections atom.
  **Amended again 2026-11-14, C32's sixth pass, items 1 to 3.** The fifth pass's widening still
  read S5 as a list, so the under-protection it named was real harm, not just a disclosed gap.
  Measured on 15 Jul 2024, before this change, the company permitted disconnection for:
  - blind or partially sighted (codes 8, 9), hearing impairment (35), language (17) and
    temporary life change (32);
  - every uncategorised need, including post-hospital recovery;
  - agent flags bereavement, job loss, payment difficulty, fuel poverty and PPM
    self-disconnection.

  The reviewer's ground: a supplier that names an S5 gap and still disconnects on it "has written
  down a Safety Net breach in advance". Job loss, payment difficulty and fuel poverty are S5's own
  fourth ground, financial insecurity, as the supplier's own agents recorded it.

  **Design choice.** S5 is a welfare test, and the company has no welfare assessment. So any
  vulnerability evidence the company holds is reason to believe that test is live, and it cannot
  answer it. That means any Priority Services registration at all (any category, any needs code,
  or none named) and any agent flag. The company's answer for such a household is
  "cannot determine", in every month, and that blocks disconnection.

  This is the §2 rule that "cannot determine" blocks, applied to the company's own commitment.
  It is strong logic, not a source.

  The six categories above stay "prohibited", not "cannot determine". A future welfare
  assessment may clear the second answer and never the first.

  - **The permit branch is still reachable.** It applies only where the company holds no
    vulnerability evidence: no registration, no flag, and a birth date that is absent or
    establishes non-pensionable age.
  - **What it costs.** Nearly every debt household an agent has spoken to becomes
    undisconnectable until a welfare assessment is built. That agrees with the published record:
    debt disconnections have been in single digits since 2017 and zero since Q1 2023
    (`docs/market_research/debt_and_collections.md`, Ofgem's debt data).
  - **Still under-protected.** A household the company holds nothing on, but which cannot
    safeguard its welfare, is not caught. That includes financial insecurity no agent recorded,
    which is the debt itself. Closing that needs the welfare assessment or an ability-to-pay step
    before any disconnection (S4's "means exhausted"), and that belongs to the collections atom.
  - **Reversible.** Delete `_held_evidence` from `winter_moratorium.safety_net_on_record`.
  **Amended again 2026-11-15, C32's seventh pass, items 2 and 4.** The reviewer asked whether "no
  evidence" means "asked and found none" or "never asked". In winter the licence answers this, and
  the code did not. 27.11(A) requires reasonable steps to ascertain before disconnecting (§2). No
  company path holds a birth date or an ascertainment record. So every household the company held
  nothing on was permitted in January, including any 27.10 household it had never asked.
  - **Design choice.** In a winter month, the licence decider's "no protection established" now
    reads "cannot determine", naming 27.11(A). This follows from the instrument's text (S8): it is
    not a policy choice, and it applies whatever the supplier's own Safety Net reading.
  - **The permit branch is still reachable,** but only from April to September, and only for a
    household on which the company holds no evidence.
  - **What it costs.** No winter disconnection at all until an ascertainment step (contact, a visit)
    is built. That step belongs to the collections atom, which owns the pre-disconnection sequence.
    This agrees with the published record of near-zero debt disconnections.
  - **Still open, and summer only.** The Safety Net's "knowingly" sets no duty to ask, so a summer
    household the company never asked stays permitted. The fifth and sixth passes named this gap.
  - **Reversible.** Remove the winter leg at the end of
    `priority_services_register._disconnection_protection`.
- **Amended 2026-11-15 (eighth pass, item 1): a Consent prepayment offer is a route to loss of supply,
  and it read nothing.** At the 90-day rung the desk asked every household to take a prepayment meter
  by Consent, without the safe-and-reasonably-practicable finding that 27.6(a)(iii) requires. The
  reviewer's point was that a take-up share of 0 is not a control. Now the offer is made only where a
  positive finding is held. No company path records a finding yet, so live, every offer is withheld
  with that reason. Rules, design choice and reversal: `docs/market_research/company_debt_management.md`,
  "Amendment (2026-11-15)". Self-disconnection monitoring on prepayment (27A, guidance §9.1) is still
  not built. It belongs to the self-rationing atom, not this decider.
- `UNSOURCED`, opened 2026-11-14 (fourth pass, item 1): whether Ofgem treats a summer disconnection
  of a known-vulnerable household as a breach of the Standards of Conduct (SLC 0). SLC 0 has not
  been read in the instrument here; nothing in the code cites it.
- `UNSOURCED`, opened here: **the current registered rate.** The register has grown since 2016 and
  Ofgem broadened eligibility again from January; the 2025 strategy PDF would answer it and did not
  extract. Nothing in `company/` may quote a present-day PSR rate until it does.
