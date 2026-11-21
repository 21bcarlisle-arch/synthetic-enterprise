# Fixing a smart meter that has stopped communicating: the rules, the evidence, and time to restore

**Knowledge:** smart-meters-and-half-hourly-settlement

**Drawn as** delivery-lane item `supplier-resolves-a-non-communicating-smart-meter-measured-on-time-to-restore`
(source: `customer_voice_theme_map_gb_energy_2026-11-21.md` §3 row "Smart meter", §4 V-T2, §5).
K8 page: it comes before any build. Researched 2026-11-21. It extends the non-communicating section
of `smart_meters_and_half_hourly_settlement_2026-10-25.md` §1 and gap 9 of
`read_access_and_theft_duties.md`, and does not restate them.

**How figures are marked.** **[H]** means read this session in the primary text named. **[S]** means
a secondary report. **[R]** means one consultation respondent's claim, as reported by the government.
**GAP** means not established.

## 1. What a supplier must do

### 1.1 Inside the record (2016–2025)

- **The operational licence condition.** Electricity SLC 49 and gas SLC 33 require the supplier to
  "take all reasonable steps" to establish and keep smart operation for meters already installed.
  There was **no time limit** inside the window. DESNZ (10 Mar 2026): "Suppliers are already
  required to take all reasonable steps to fix smart meters that are not working as they should."
  [H, gov.uk news story "Tough new rules force suppliers to fix faulty smart meters"]. The DESNZ
  post-2025 government response names the gas condition SLC 33. An earlier secondary summary said
  SLC 43. **Correction, beside the claim:** the response's own wording is the one used here [H].
- **No GSOP for a smart meter.** Until 23 Feb 2026 no Guaranteed Standard covered smart-meter
  operation. The Faulty Meters standard (regulation 4: action within 5 working days) is about a
  meter **recording outside its margins of error**, not one that has stopped sending reads. Ofgem's
  decision says this explicitly (§3.29) [H].
- **Enforcement, not compensation.** Ofgem pursued the rollout and operation duties through
  compliance engagement. In 2025 it opened engagement with British Gas, EDF, E.ON, Octopus, OVO and
  Scottish Power, and separately with Ecotricity, So Energy and Tomato Energy [S, ofgem.gov.uk
  publication titles]. The terms are not read here.

So **in the 2016–2025 world, a supplier's fault path is a matter of its own discretion**. The only
limits are a duty of effort and the regulator's attention. That is why handling can differ by
supplier, and the dispute share differs four times over (§3).

### 1.2 After the record (2026). These are dates the company cannot see.

| Instrument | What it requires | Clock and deadline | Payment | In force |
|---|---|---|---|---|
| **GSOP 1**, installation appointment | offer a first-time install appointment within six weeks of the request | 6 weeks from request | automatic; £40 [S, press] | 23 Feb 2026 [H] |
| **GSOP 2**, failed installation | an install fails "due to a fault within the energy supplier's control" | per event | automatic; £40 [S] | 23 Feb 2026 [H] |
| **GSOP 3**, new **regulation 5A** "Investigation of smart meters not operating as intended" | an initial assessment (meter, IHD or both), an action that helps identify the fault, and an offer of written confirmation | **5 working days** from the customer's report | automatic; £40 [S] | 23 Feb 2026 [H] |
| **GSOP 4**, a meter not in smart mode for over 90 days | compensation if a meter is still in traditional mode after 90 days (as proposed) | 90 days | proposed; **not decided** | Ofgem "decided not to make a final decision on GSOP 4"; decisions are due "in the latter half of 2026" [H §2.8, §2.14] |
| **Amended SLC 49 / SLC 33** (DESNZ post-2025 framework) | "all reasonable steps to ensure smart meters in traditional mode are back working in smart mode… as soon as possible and no later than 90 days from the date energy suppliers are first aware" | 90 days from first awareness. The news story says "after they are notified" | none; enforcement only ("fines or legal action") | announced 10 Mar 2026; "in place in 2026"; no exact commencement date was found [H] |

Read from Ofgem, *Decision on the introduction of smart meter Guaranteed Standards of Performance*
(Jan 2026, `ofgem.gov.uk/sites/default/files/2026-01/final-decision-smart-meter-GSOPs.pdf`): the
Statutory Instrument was signed 27 Jan 2026; monitoring starts Q2 2026; GSOPs 1–3 are reviewed in
Q1 2027 [H §4.3–4.4].

**Four things the 2026 rules settle that bear on design inside the window:**

1. **The duty has two clocks, and they are different events.** GSOP 3's clock starts when **the
   customer reports** a problem, and it requires assessment, not resolution (§3.30: "focused on
   initial engagement and assessment, rather than the full resolution"). The 90-day clock starts
   when **the supplier is first aware**: failed commissioning, a customer report, a change of
   supplier, lost remote reads, or a DCC report [S, summary of the government response]. So a
   supplier that watches its own read failures starts the 90 days *before* the customer calls.
2. **Time to restore is the measured quantity**, not time to respond. The 2026 licence wording is
   "back working in smart mode… no later than 90 days".
3. **The DCC owns part of the fault.** GSOP 4 stalled on whether WAN and comms-hub faults belong to
   the supplier. No supplier–DCC cost-recovery mechanism exists (§2.9–2.10 [H]). The proposed GSOP 4
   gave 30 extra days for comms-hub and WAN issues. Most respondents agreed more time was needed,
   views differed on how much, and the drafting was called "not practical" (decision, consultation
   summary Q10 and Q12 [H]). Suppliers also asked for the customer exemption to be worded around a
   customer *not* answering a request for a visit (Q12 [H]). Operationally, then, a visit route
   stalls on access.
4. **"All reasonable steps" is not defined**, and there are no formal exemptions. The government
   says the test "already provides sufficient flexibility" [S, summary of the government response].

## 2. What is published about the faults themselves

| Quantity | Value | Grade |
|---|---|---|
| Smart and advanced meters in traditional mode, end Sep 2025 | 8.3% (91.7% in smart mode) | [H] Ofgem decision, executive summary |
| Smart meters not fully functioning, 2023 | 3m (9%); "about half" had "transitory" issues | [S] POST, citing the PAC (already on the smart-meters page) |
| SMETS1 meters losing smart mode on switching, before DCC enrolment | 70% | [S] POST |
| Homes outside WAN coverage, 2023 | 0.75% | [S] POST |
| Share of issues fixable remotely | "at least a third" | **[R]**, one respondent; the government gives no figure of its own |
| Time left for triage, if a visit is booked in the six-week window | about 48 of the 90 days | [S], the government's own arithmetic |
| Gas against electricity, out of smart mode | about twice as likely | [R]; consistent with DESNZ Q4 2024 (14.2% gas, 6.8% electricity), already in `simulation/meter_reads.py` |
| Smart households giving manual reads at least monthly | 17–29% across the six largest suppliers | [P], Citizens Advice *Fully Operational*, 2026 (theme map §1.3) |
| Told "can't be resolved for now / passed to another organisation" | 22% of those who contacted their supplier about a smart problem | [P, second-hand], ECSS Jan 2026 p.62 (theme map §1.2) |
| Smart Meters' share of each large supplier's accepted Ombudsman disputes, Q1 2025 | 5%–21% | [P], theme map §1.1 |

**GAP S1, the exit hazard.** How long a meter stays out of smart mode once it has dropped out is
not published. Neither is the probability it returns by itself, by a remote fix, or by a visit.
DESNZ and Ofgem publish **stocks**: 2.3m (Q1 2019), just under 4.0m (end 2019), about 4.5m (end
2020), 4.18m domestic (end 2021), 3.2m (end 2022), 3.857m (Q1 2024). A stock is the entry rate
times the mean duration. With neither published, the stock alone cannot separate them.
"About half transitory" says the distribution is **two-humped**: one group of faults clears quickly
and another lasts. It does not give either hump's time.

**GAP S2, the cost of a fix.** No published cost was found for a remote reconfiguration, a comms-hub
swap or a meter exchange visit. A visit's cost belongs with the read-visit GAP in
`read_access_and_theft_duties.md` §2.9 and should be shared, not given a second number.

**GAP S3, handling against outcome.** No source links a supplier's fault-handling practice to its
smart dispute share. Citizens Advice reads the spread as handling, not hardware (theme map §3),
and the 15–27% spread excluding London supports that. That reading is an inference, not a
measurement.

## 3. What we have built (discovery, origin/main at 2026-11-21)

- **World.** `simulation/meter_reads.is_not_in_smart_mode` draws the state once per account, from
  `q6_smart_not_in_smart_mode_share` split by fuel, and **holds it for the life of the account**.
  It deliberately does not invent an exit rate (GAP S1). An HH-settled meter is always
  communicating. A silent meter's reads fall back to the traditional delay and read classes.
- **Supplier.** **Nothing.** Grep over `company/` and `saas/` finds no non-communicating register,
  no fault instruction and no restore action. `company/regulatory/gsop.py` has no smart types,
  which is correct inside the window. The nearest precedent is the read-duty route:
  `company/billing/read_duty_register.read_instruction_due` names a bill, and
  `simulation/meter_reads.ReadArrivalFeed.instructed_read_for` answers it. The company asks; the
  world decides what happens.
- **So time to restore is currently undefined.** Every silent meter is censored at account end,
  whatever the supplier does. A desk with a different fault path cannot produce a different smart
  dispute share, so **V-T2 is unreachable by construction**.

## 4. Design choices for the build, and why

1. **The supplier observes silence, not the state.** A real supplier sees its scheduled DCC reads
   fail. It does not see `is_not_in_smart_mode`. Across the seam: the run of billing periods on a
   smart account with no smart-transmitted read. "First aware" is the first such period, which is
   what the 2026 licence clock would read.
2. **The supplier's lever is an instruction, and the world answers it** (the read-instruction
   pattern). The instruction names a route: a remote reconfiguration, or a visit. The world decides
   whether the meter returns and when. The supplier never sets the outcome.
3. **The world's exit needs the two humps, carried as a stated belief with a range** (CLAUDE.md:
   "model it as a stated belief with a range"), not as a single number. The beliefs:
   - a share of faults is transitory, at about one half [S, PAC];
   - a share of the remainder is remotely fixable, at least a third of all faults [R];
   - the rest need a visit, which must meet the read-access machinery that already exists (no
     access, no fix).
   The *time* of each hump stays **GAP S1** and becomes an assumption-toggle row with
   `default_reason` and a low–high sweep. It is not a constant in code.
4. **Without an instruction, the existing behaviour is the floor.** A run with no fault path must
   bill exactly as today: a silent meter is held for life, except for the transitory share. Whether
   the transitory share belongs in the floor is the first question the build must answer, because
   adding it changes every current book. **F11 decides it: add it only behind a flag that defaults
   off**, so this build cannot move a published figure by the back door.
5. **Measured on time to restore**: days from first observed silence to first smart read again,
   per account, with censored accounts counted and published as censored. A median over the
   restored accounts alone would flatter the desk. It is published beside the share still silent at
   90 days. That share is the 2026 licence's test, a diagnostic and never a target (outputs are
   diagnostics).
6. **V-T2 is graded ordinally**, as the theme map sets it: two desks with different fault paths must
   be able to show different smart-meter complaint or dispute shares. That needs a channel the
   world already has, from a silent meter to an estimated bill, a catch-up and a complaint
   (`simulation/contact_propensity.py`). The build must check that this channel exists before
   claiming V-T2. Done for V-T2 is that the spread *can* appear, not that it matches 4×.
7. **No 2026 rule enters the company's 2016–2025 decisions.** The 90-day figure is published as a
   diagnostic line ("share silent beyond 90 days"), labelled as a standard from after the window.
   GSOP payments for smart meters are **not** added to `gsop.py`.

## 5. What done means for the delivery item

- **Increment 1 (this page).** The rules, the evidence, the GAPs and the design are published.
- **Increment 2.** World: a restore answer to an instruction, with the S1 toggle rows. Supplier: a
  silence register (first-aware date, days silent) and a fault instruction. Both behind a default-off
  flag, mutation-proven on the property "an instructed meter can be restored; an uninstructed one
  is unchanged".
- **Increment 3.** A two-desk run, one instructing at first silence and one never instructing.
  Publish time to restore with censoring, the share silent beyond 90 days, and the V-T2 ordinal
  reading. Write down beforehand the prediction that the instructing desk shows a lower smart
  complaint share.

## Sources

- Ofgem, *Decision on the introduction of smart meter Guaranteed Standards of Performance*, January
  2026: https://www.ofgem.gov.uk/sites/default/files/2026-01/final-decision-smart-meter-GSOPs.pdf [H]
- DESNZ, "Tough new rules force suppliers to fix faulty smart meters", 10 March 2026:
  https://www.gov.uk/government/news/tough-new-rules-force-suppliers-to-fix-faulty-smart-meters [H]
- DESNZ, *Smart metering policy framework post-2025: government response*:
  https://www.gov.uk/government/consultations/smart-metering-policy-framework-post-2025/outcome/smart-metering-policy-framework-post-2025-government-response-accessible-webpage--2
  [H for the executive summary and the quoted Q7 and Q15 text; S for the rest, read via a
  summarised fetch]
- Ofgem, compliance engagement on smart meter obligations (2025):
  https://www.ofgem.gov.uk/publications/british-gas-edf-eon-octopus-ovo-and-scottish-power-smart-meter-issues [S, title only]
- The £40 figure: press reports of the decision (MoneySavingExpert, GB News, Jan–Mar 2026) [S]. The
  Statutory Instrument's text was not read. **V1:** read SI regulation 5A and the payment amounts
  in the instrument itself.
