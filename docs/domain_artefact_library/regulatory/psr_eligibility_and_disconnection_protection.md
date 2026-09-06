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

Core services conferred by registration (S3): alternative billing formats (large print, Braille,
audio); advance notice of supply interruption; priority reconnection after an interruption;
quarterly meter readings; free annual gas safety check; password scheme; nominee arrangements.

## 2. Disconnection protection — SLC 27, plus a voluntary commitment

- **Winter months are October, November, December, January, February and March** (S4).
- A supplier **must not** disconnect a domestic customer of pensionable age during the winter
  months where that customer lives alone, or lives only with others of pensionable age or under 18
  (S4, cited there to **SLC 27.10**).
- Outside that prohibition the duty is weaker in kind: **all reasonable steps** to avoid
  disconnecting premises whose occupants include a person who is disabled, chronically sick, or of
  pensionable age (S4).
- Disconnection for unpaid charges is in any case only available once repayment options have been
  offered and the available means of recovering the debt exhausted (S4).
- **Energy UK Vulnerability Commitment / "Safety Net"** (S5): a **voluntary** pledge, all year
  round, not to knowingly disconnect a customer who cannot safeguard their own or their
  household's welfare due to age, health, disability or severe financial insecurity. It is a
  commitment, not a licence condition, and a supplier that has not signed it is not bound by it.

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

- `UNSOURCED`: the SLC 26 and SLC 27 condition text itself. Numbering here rests on secondary
  sources (S2, S4). The consolidated PDF is 600+ pages and defeated automated extraction; reading
  it is real work and is not done. **Nothing should quote a clause number from this file as if it
  had been read in the instrument.**
- `UNSOURCED`: whether the child needs code is "under 5" or "under 6" — S3 says five, S2 records
  the ENA agreeing on under-six. The sources genuinely disagree and the disagreement is not
  resolved here.
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
- `UNSOURCED`, opened here: **the current registered rate.** The register has grown since 2016 and
  Ofgem broadened eligibility again from January; the 2025 strategy PDF would answer it and did not
  extract. Nothing in `company/` may quote a present-day PSR rate until it does.
