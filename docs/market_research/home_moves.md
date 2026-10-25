# Home moves: change of tenancy, change of occupier, and what a GB supplier sees of them

**Knowledge:** home-moves

*Written 2026-10-05 as step-1 knowledge work under `docs/staging/done/DIRECTOR_CANON_THE_PRIORITY_ORDER_2026-10-05.md`
(home moves is a step-5 lever). Every figure carries its source. Where the record is silent the figure
is marked **GAP**; no number on this page was chosen to fill a slot.*

---

## 1. What a home move is, from a supplier's view, and its cases

**Definition.** For a supplier, a home move is not one event. It is **a change in who is liable for the
energy at a metering point while the meter, the supply and (usually) the supplier stay put.** The
Retail Energy Code defines Change of Tenancy as the situation where "any occupier responsible for the
payment of energy bills moves out of any property (residential or commercial) and any new occupier
moves in" (as summarised by Ofgem, *Call for input: Tackling Energy Debt in the Supplier Home-Moves
Process*, 9 Dec 2025, ¶2.5). Since REC change R0155 (approved 4 Feb 2025, implemented 27 Jun 2025) the
code term is **Change of Occupier (CoO)**: "a change in the legal entity responsible for a premises"
(BP Consulting summary of R0155; Ofgem acceptance letter for R0155, Apr 2025).

One household's move therefore touches **two premises and possibly two suppliers**: a liability ending
at the old address and a liability starting at the new one. The supplier experiences these as
separate events, often weeks apart, often on different accounts, and usually without knowing they
are the same household. That is why the cases below must be kept apart: they have different
triggers, different counterparties, different money and different remedies.

**The legal frame that makes GB unusual.** "In Great Britain … it is generally accepted that consumers
have access to an energy supply immediately upon moving into a new property … without setting up an
account, agreeing to pay a bill or knowing who their energy supplier is" (Ofgem CfI 2025, executive
summary). Internationally this is unusual: "In countries such as France, Italy, Spain, Portugal,
Brazil and USA the property is disconnected in a change of tenancy event" (CfI ¶1.6 fn 1). The
supply is never interrupted, so a new occupier is supplied whether or not anyone knows they exist.

| Case | Trigger | Counterparty | Contract / price | Money at stake |
|---|---|---|---|---|
| **A. Move-out** (our customer leaves a premises) | Customer notifies, or the supplier discovers it later | The departing named customer | Their contract ends; final bill | Final bill; credit refund; **debt left on a final (closed) account** |
| **B. Move-in, unnamed** (someone new starts using energy at a premises we supply) | Nothing — supply continues | "The Occupier", identity unknown | **Deemed contract** at the supplier's deemed/default rate (price-capped) | Unbilled and uncollected consumption; the largest single source of CoT debt |
| **B'. Move-in, named** (new occupier registers with the incumbent) | Occupier contacts the incumbent | Named new customer | Deemed until they choose a tariff | An acquisition the supplier did not pay for |
| **B''. Move-in, switches away** | New occupier contracts with another supplier; switch request carries the **CoO indicator** | Gaining supplier | Gaining supplier's tariff | A loss the incumbent cannot object to on debt grounds |
| **C. Mover takes us with them** | Departing customer asks to move their account to the new address | Same customer, new premises | Same tariff if the supplier allows the transfer, else new contract | Retention of a customer at the one moment they are most likely to be lost |
| **D. Void** (premises empty between occupiers) | Move-out with no move-in | Owner / landlord | Deemed | Standing charge plus any void consumption |
| **E. Landlord / letting agent** | Agent notifies tenancy changes, or holds the account in voids | Landlord or agent | Deemed or landlord contract | Void liability; a channel to new occupiers |

Sources for the table: deemed contract on move-in — Ofgem *Guidance on Deemed Contracts*, 6 Nov 2023,
¶2.10 ("A Deemed Contract relationship will normally exist in circumstances where any type of customer
moves into new premises, and starts to consume gas and/or electricity, without agreeing a contract with
a supplier"), and statutory basis Gas Act 1986 Sch 2B para 8(1) / Electricity Act 1989 Sch 6 para 3
(¶2.16). Deemed rates capped — same guidance ¶2.19: "deemed rates for domestic customers currently fall
under the price cap requirements, as per SLC 28AD. Whilst the price cap is in effect, Ofgem consider that
compliance with the price cap alone is sufficient to comply with SLC 7.3 and 7.4." Citizens Advice
(*Moving home and dealing with your energy supply*, consumer page, accessed 2026-10-05): "You'll
automatically be put onto a 'deemed contract' with your supplier, which will be for their 'default' or
'standard variable' tariff." CoO indicator and objections — see §3. Landlord liability for voids —
see §2.4 and §6 (partly a gap).

**Liability follows the person, not the premises.** A new occupier is not liable for energy used before
they moved in (Citizens Advice, *Check if you're responsible for paying an energy bill*: "you moved in
after the energy was used"); Ofgem describes the move-in occupier as one who "has not been identified
and is not in debt in respect of energy use at that property" (CfI ¶3.7). The departing customer stays
liable "until 2 days after you told the supplier you were moving" (Citizens Advice, same page). The
statutory locus of the two-day rule was **not** located in Gas Act Sch 2B in this pass (**GAP**: cite
the licence or statutory provision before coding it).

**Other special paths** (named, not sized here): bereavement (estate liability), joint tenants,
name-change-only (no financial boundary), erroneous or fraudulent CoT (the REC R0155 work was driven by
"possible misuse of the Change of Tenancy flag and objection process" in the non-domestic market —
RECCo, *Ongoing progress to improve the Change of Tenancy process*), and legacy prepayment debt left on
a meter, which a new occupier meets at the top-up point until the supplier clears it (Citizens Advice
moving-home page: "Avoid using it until they remove any previous debt").

---

## 2. Scale, per case

### 2.1 How many households move, by tenure (England)

English Housing Survey 2023-24, *Headline Report: demographics and household resilience*, ch. 3
"Household moves" and Figure 3.4 (Annex Table 3.7), base: household reference persons resident less than
a year:

- "approximately **1.8 million households moved home** in the previous 12 months", out of **24.7 million**
  households (ch. 1, Annex Table 1.1). That is **7.3% of households a year** (derived: 1.8 / 24.7).
- Private rented (4.7m households, 19%): **680,000** moved within the sector and **159,000** new households
  moved into it.
- Owner occupied (16.0m, 65%): **331,000** within, **121,000** new households, **155,000** in from private renting.
- Social rented (4.0m, 16%): **138,000** within, **28,000** new households.
- Smaller cross-tenure flows on the figure total about 157,000 (7k, 12k, 17k, 59k, 62k); their directions
  could not be read unambiguously from the PDF text layer, so the rates below are given as a range.

**Derived annual move-in rates by destination tenure** (arithmetic on the EHS counts; lower bound counts
only the flows the text assigns, upper bound adds every unassigned cross-flow to that tenure):

| Destination tenure | Households | Move-ins in the year | Rate |
|---|---|---|---|
| Private rented | 4.7m | 839k – ~996k | **~18% – 21%** |
| Owner occupied | 16.0m | 607k – ~626k | **~3.8% – 3.9%** |
| Social rented | 4.0m | 166k – ~242k | **~4% – 6%** |
| All | 24.7m | 1.8m | **7.3%** |

So a private-rented dwelling changes occupier about **five times as often** as an owner-occupied one.
Tenure, not the household's age or income alone, is the first-order driver of the rate.

Two things the supplier must not conflate:
- **New households** (121k + 28k + 159k = 308k, **17%** of moves) create a move-in at the destination with
  **no** vacated dwelling behind them; the household they left continues.
- **Ended households** (deaths, merging into another household) create a vacated dwelling with **no**
  move-in by that household. The EHS says plainly it "cannot identify the number of households which have
  ended" (Figure 3.4 note 3). **GAP**.

A second, older, GB-wide figure: Ofgem *Consumer Engagement Survey 2016* (TNS BMRB) found **11% of all
consumers** had moved house in the last 12 months (16% of the "Switched on" segment; 25% of the younger
"Unplugged", who "are more likely to live in rented accommodation"). This is a person-level survey answer,
not a household count, and is higher than the EHS household rate; the two are not the same quantity and
should not be averaged. The internal scope brief's "~10% of households move each year"
(`docs/domain_artefact_library/scope_briefs/ADVISOR_SCOPE_BRIEF_CHANGE_OF_TENANCY_2026-08-07.md`) is
unsourced and sits between them; the EHS 7.3% supersedes it for England.

**The next edition agrees.** `simulation/arrival_route.py` already carries the EHS **2024-25** flows
(Annex Tables 1.1 and 3.7, fetched 2026-09-19): owner-occupied 611k / 16.2m ≈ 3.8%, private rented
822k / 4.7m ≈ 17.5%, social 189k / 4.1m ≈ 4.6%, against the same 1.8m headline. Two editions give the
same shape, so the tenure ratio is stable at about 4.5–5× private rented over owner-occupied.

**GAP:** Scotland and Wales mobility by tenure (the EHS is England only); the 2016–2025 time series of
the EHS mover counts (it exists in the EHS annex tables year by year and was not extracted here).

### 2.2 Seasonality of moves

**GAP — no official monthly series located.** Removal-industry marketing pages claim August is the
busiest month (~12% of annual moves) with July and September ~10% each (e.g. Clockwork Removals, *Why
August is the busiest month*). These are unsourced commercial claims and must not be coded. A usable
proxy exists but was not extracted: HMRC *UK monthly property transactions* (owner-occupier purchases
only, completions by month). The private-rented pattern (the majority of moves) has no monthly official
series that this pass found; student lets plausibly concentrate turnover in summer, but that is a
practitioner question, not an established figure.

### 2.3 Move-related churn as a share of supplier losses

**GAP for the supplier-side figure.** No published source gives the share of a supplier's account
losses that are moves. What is published:
- CMA Energy Market Investigation, Final Report (2016), Tables 8.5/8.6: "Home movers" is a named
  acquisition channel for all six large suppliers; every numeric cell is redacted (already recorded in
  `docs/market_research/continuous_behavioural_engagement_w2_14.md` §2c).
- Ofgem *Understanding Consumers' Energy Tariff Choices* (fieldwork Mar–Apr 2024, base 3,235): over the
  previous six months, 6% actively switched supplier and "A small share passively switched to a new
  supplier, e.g., by moving house or a supplier changing hands (**4%**)." Moving and supplier failure are
  bundled; the share due to moving alone is not given.
- Ofgem *Consumer Engagement Survey 2016*: of those who switched, changed or compared tariff, **9%** said
  they were prompted because they moved home (7% in the 2014 baseline); switching without comparing was
  17% among recent movers versus 6% among non-movers.

So moving is a material, passive route out of a supplier's book — of the same order as active switching
over a six-month window in 2024 — but its exact share of losses is not published.

### 2.4 Void consumption

**GAP.** No published source gives domestic void-period length or consumption. Citizens Advice guidance
says only that a departing tenant is not liable once someone else has moved in; the landlord's liability
for voids is common practice (supplier terms; Money Advice Trust response to the CfI, Jan 2026: "at what
point the landlord … becomes liable … We have seen cases [of tenants billed for a] period where the
property is empty and their tenancy has ended") but has no published sizing.

### 2.5 Debt and unbilled energy arising at a change of tenancy

- **20–40% of all domestic energy debt** is associated with change of tenancy / unnamed ("the occupier")
  accounts: "Evidence received back from suppliers suggests that this cohort of consumers may be
  responsible for between 20% to 40% of the overall debt figure" (Ofgem CfI 2025, ¶2.5). The executive
  summary adds that this share "has been stable since before the energy crisis. This suggests that some
  at least of this portion of debt is driven by behavioural factors rather than affordability."
- Scale of the total it is a share of: domestic energy debt reached **£4.43bn** by June 2025, "up 20% from
  the same time in 2024 and 71% since 2023"; nearly three quarters has no repayment plan (CfI ¶2.1). A
  typical consumer pays "around **£52 per year**" towards managing and writing off energy debt (CfI ¶2.2).
  Taken together these imply CoT-associated debt of roughly **£0.9bn–£1.8bn** at June 2025 (derived:
  20–40% × £4.43bn). That is an inference from two Ofgem figures whose definitions may not align (the
  20–40% is supplier-reported and may be on a different debt base); state it with that caveat or not at all.
- **Ofgem asked for, and does not yet have, the numbers that would size it properly**: "the number of
  unnamed accounts, average length of unnamed accounts, average debt and the overall debt associated
  with these accounts" (CfI Q1) and "the average duration for a new householder to set up an account"
  (Q2). These are **GAPs in the public record**, not only in ours. Ofgem's response was due Spring/April
  2026 (CfI ¶1.13); it was not located in this pass.
- Debt on closed accounts is a separately provisioned class: Ofgem's DRS working paper weights provision
  by "account type (Closed or Live)" (Aug 2025 §5.20; see
  `docs/market_research/how_a_gb_supplier_decides_to_write_off_a_failed_payment.md` (b)).

### 2.6 Share of new occupiers who stay on the deemed contract

**GAP.** No published figure. Ofgem says new occupiers "may occupy the property for weeks or even
months before they realise that their debt is accumulating" (CfI exec. summary; ¶2.4), which bounds the
latency qualitatively and no more.

---

## 3. What a real supplier can see (the epistemic wall)

**What it sees.**
- **The meter, not the person.** Registration is per MPAN/MPRN. The supplier's records of who lives
  there are its own account records; the industry does not tell it who the occupier is.
- **A move-out only when the customer tells it**, or when a final bill bounces, a direct debit is
  cancelled, mail is returned, or a new occupier calls. Customers are asked to give "at least 48 hours'
  notice" and a forwarding address (Citizens Advice moving-home page).
- **A move-in only when the new occupier contacts it** (case B'), or **when another supplier's switch
  request arrives carrying the Change of Occupier indicator** (case B''). The CSS reports "domestic
  switches where the Change of Occupier (COO) indicator was set, split between objected and not objected"
  (Ofgem, *CSS Service Definition*, Annex 2, Nov 2019 — the indicator is a defined CSS data item). A
  change-of-tenancy flag "indicates to the incumbent supplier that the customer is a new owner or occupier
  of the premises and the incumbent supplier should have no valid grounds to object to the transfer"
  (Ofgem, *Decision on review of non-domestic objections*, Jul 2016, fn 26 — the definition is written in
  the non-domestic decision; its application to domestic switches is the same CSS indicator). Domestic
  objections are otherwise allowed only for debt (notified and unpaid 28+ days), erroneous switches,
  customer request, or related meter points (Ofgem, *Review of domestic debt objections: our decision*,
  25 Jul 2016), and "the vast majority of objections (well over 90%) in the domestic market" are for debt
  (Ofgem, *Impact assessment on review of domestic objections*, Jul 2016). Under R0155 both suppliers must keep the evidence relied on for a CoO
  for at least one year, and suppliers are "encouraged to pause any billing activity or debt recovery
  while a CoO is under review" (BP Consulting summary of R0155).
- **Reads.** A meter read on move day if the customer gives one; otherwise an estimate. With a smart
  meter in smart mode (about **37 million meters, 64%** of all meters — CfI exec. summary) the supplier
  can take an actual read remotely on the move date. The same read closes one account and opens the next,
  so an estimate at the boundary transfers value between two people who never meet.
- **Consumption continuing after a move-out** with no named customer — a smart supplier sees half-hourly
  or daily usage at an unnamed premises; a non-smart supplier sees nothing until the next read.
- **The previous occupier's consumption history.** The settlement EAC belongs to the metering point, so
  a move-in inherits the previous occupier's EAC (`docs/market_research/how_far_a_settled_eac_sits_from_next_years_use.md`).
  For a supplier this is a trap: its first estimate of a new occupier's usage is another household's
  usage.
- **Third-party data it may buy**: credit reference "footprints" at an address are used by water
  companies to identify and bill unnamed occupiers (CfI Information Box 1); energy suppliers use tracing
  agents and CRAs for final-account debt (practice, not sized here).

**What it cannot see.**
- Who moved in, when, whether the property was empty, the tenure, whether a landlord is involved,
  whether a departing customer is moving or has died, and — critically — **whether a new customer at
  one address is the same household that left another** unless the customer says so.
- That a household is about to move. No industry flow carries an intention to move.

**Industry flows.** Electricity data flows (the D0 series under the DTC) carry reads and registration
data; gas reads go via Xoserve/the CDSP. This pass did **not** establish which specific D-flow or gas
flow carries a change-of-tenancy read or flag in domestic electricity after the July 2022 move to the
CSS, beyond the CSS CoO indicator itself. **GAP** — the internal scope brief's statement that a CoT with
the incumbent is "supplier-internal — no switching flow, no CSS message" is consistent with the record
for case B'; case B'' does carry a CSS indicator.

---

## 4. Practice

**The mover journey (what consumers are told).** Citizens Advice, *Moving home and dealing with your
energy supply*: tell your supplier at least 48 hours before; read meters on move day; give a forwarding
address; the old supplier sends the final bill "within 6 weeks", the customer has "28 days to pay", and
credit is refunded "within 10 working days of sending you the final bill". On a fixed deal, "check
whether an exit fee applies" and ask whether the supplier will "transfer your current tariff to your new
home". On arrival, the new occupier is on a deemed contract at the standard variable tariff and can
switch once responsible for the property. (The licence locus of the 6-week and 10-day timings is not
cited here; **GAP** to the SLC 27 / GSoP text before coding.)

**Home-mover retention ("take us with you").** The industry treats moving as a distinct acquisition
and retention moment — the CMA tables name a home-movers channel and E.ON's included letting-agent
relationships (CMA 2016 §8.161 fn). Whether a supplier lets a fixed tariff travel to the new address
without an exit fee is supplier policy. **GAP:** no published rate at which movers take their supplier
with them, and no published value of a home-mover retention offer.

**Debt prevention at move-out.** The tools in use are: an actual read on the day (smart), a forwarding
address, collecting the final bill by the existing direct debit, tracing agents, and placement with debt
collectors. Their effectiveness is not published.

**Debt prevention at move-in — the live policy change.** Ofgem's Dec 2025 CfI proposes letting suppliers
**switch a SMETS2 meter to prepayment mode when notified that the previous occupier has moved out**, with
guardrails: "pre-loaded credit on the meter, a zero standing charge tariff and an enhanced contact
approach" (¶2.6), credit to cover "a weekend or holiday period" (¶3.15); conditions are an existing SMETS2
meter, notification of the move-out, a deemed contract, and the account in the name of "the occupier"
(¶3.11). A working group was to run monthly from January 2026, with an outcome expected April 2026
(¶1.13–1.14). Consumer bodies pushed back on reliance on the tenant to act and on vulnerable occupiers
left on prepayment (Money Advice Trust response, 20 Jan 2026; Citizens Advice response, 20 Jan 2026,
supports reducing inadvertent debt). **This is a rule change inside the 2016–2025 window's aftermath, not
inside it**: for a run on the historical record the regime is "supply continues, deemed contract, no
remote prepay switch".

**The comparator other utilities use.** Water companies write to "the occupier" and, if there is no
contact, "use credit reference agencies to identify the 'credit footprint' at the property, subsequently
creating an account on behalf of the consumer" (CfI Information Box 1). Broadband simply is not
connected until the occupier contracts.

---

## 5. What our code does

Read-only discovery over `sim/`, `simulation/`, `company/`, `saas/` and staging, 2026-10-05. Line
numbers are at the worktree HEAD of that date.

### 5.1 The world: a "home move" exists only as a relabelling of renewal churn

- **No move event.** `simulation/life_events.py` `EventType` (≈ lines 68–82) has kit, boiler,
  insulation, job loss, baby, retirement, illness and divorce. It has no move-out and no move-in. The
  `dd_balance_book.py` docstring (≈ lines 74–80) says the same: "`simulation/life_events.py` emits no
  move event of any kind -- the SIM has no tenancy-change stream to couple."
- **What is called a home move.** In `simulation/customer_events.py::roll_lifecycle_event` (≈ lines
  1022–1027), *every* account that does not renew at a renewal point rolls a second die,
  `home_move_won = win_roll <= renewal_data["win_probability"]`. If it wins, the run activates a
  "successor" customer at the same premises with the predecessor's EAC (`home_move_disposition`,
  ≈ line 425). `win_probability` comes from `saas/home_move_win_rate.py`, whose docstring says
  churn means "the occupant moves out". It uses `BASE_WIN_PROBABILITY = {"resi": 0.55, "SME": 0.35}`,
  described there as "seed estimates", scaled by an EPC-banded price sensitivity, with a clamp of
  0.05–0.95.
- **Why that is a definitional error, not a tuning error.** It treats *every* departure as a move.
  Moves and switches are opposite events at the premises:
  - A **switcher** stays in the home and takes the supply point to a competitor. Nothing is left
    behind to win.
  - A **mover** leaves the supply point with us. The new occupier lands on our deemed contract by
    default (case B). We lose them only if they switch away (B''), and in the meantime we carry their
    unnamed-account debt risk.

  So the code credits a 55% chance of keeping the premises after price-driven and
  dissatisfaction-driven switches, where reality gives none. It also gives a real move a 45% chance of
  losing the premises *at once*, where reality gives a deemed supply that lasts until the occupier acts.
  Effective retention is overstated for switchers and the deemed-occupier window is missing for movers.
  The 0.55 / 0.35 baselines and the EPC sensitivities have no published source (§2.3: the CMA
  home-mover channel figures are redacted).
- **The cause partition never names a move.** `simulation/departure_risks.py` line 41 says "(C1b adds
  svt_inertia; C6 adds home_move)", but `ORDERED_CAUSES` has no `home_move` and no `CAUSE_HOME_MOVE`
  exists anywhere. Moves therefore run on the renewal clock and on price. In the record they run on
  tenure (§2.1) and the calendar, independent of price and of contract end.
- **The debt objection blocks a "move".** `customer_events.py` (≈ line 1018) makes
  `blocked_by_debt_objection` retain the account. That is right for a switch. A move is not a switch:
  a household in debt can move out and leave a closed-account balance behind. That is the path behind
  20–40% of all domestic debt (§2.5), and the code has no route for it.
- **What is sourced and present.** `simulation/arrival_route.py` carries **EHS 2024-25** move-in
  flows and households by tenure (Annex Tables 1.1, 3.7, fetched 2026-09-19): owner-occupied 0.611m /
  16.2m ≈ 3.8%, private rented 0.822m / 4.7m ≈ 17.5%, social 0.189m / 4.1m ≈ 4.6%. It reconciles them
  against the 1.8m headline as a declared gap (`move_rate_reconciliation`). These agree with the
  2023-24 edition in §2.1. **But the rate is used only to choose the tariff an *arriving* account
  opens on** (`arrival_tariff_type`: deemed/SVT with share m/(m+s)). It does not make any household
  on the book move. Households do carry tenure (`simulation/population_draw.py`,
  `household_segments.py`), so the input a move stream needs already exists in the world.
- **Exit debt in the world.** `simulation/final_bill_outcome.py` resolves whether a final bill is paid
  (paid / late / partial / unpaid, plus `gone_away`), behind the wall. `FinalBillResolution.as_observable_event()`
  (≈ line 328) is the sanctioned crossing, and it omits the probability, archetype, tenure and channel.
  It is sound in shape. *Corrected 2026-10-10: this said it "has no move-out stream to feed it". The
  stream now exists (B7, moves on since ada37371c), but the run still has no caller of
  `OccupancyEnded.final_bill_exposure`, so a mover's final bill never goes through this module.* *Corrected again the same day: a mover's final bill now goes through it, by way of
  `arrears_engine.mover_final_bill_outcome` (below). `OccupancyEnded.final_bill_exposure` still has
  no caller.*
- **That module against the one sourced exit-loss figure (measured 2026-10-10, not wired).** Centrica
  ARA 2025 Note 17 p.175 provisions UK residential **closed-account final bills** at 31.6% / 57.6% /
  87.8% of the gross balance at <30 / 30–90 / >90 days past invoice (2024: 36.8 / 63.6 / 89.6), per
  `knowledge_map.md`'s IFRS 9 row. **What each figure counts, before they are compared (added
  2026-10-10).** Centrica's is a share of VALUE. It is an expected-credit-loss rate applied to the
  gross receivable balance in each age bucket, so it is pounds provided over pounds owed. It is not a
  share of accounts and not a share of the bills that fail. It is a STOCK, the balances still open at
  the reporting date, so a large or old balance weighs more than a small one. It includes the
  supplier's prudence, and it excludes closed accounts in credit. The world's figures below, and the
  0.74% after them, count pounds too: the face value of a final bill not recovered (a part payment
  counts as recovered), after the 12.2% post-write-off recovery, over the face value issued. That is a
  FLOW over bills at issue. Every draw is a £100 bill, so on this basis the share of value equals the
  expected share of each bill lost, and no size weighting is in it. So the comparison is value
  against value, with two known gaps: stock against flow, and Centrica's book mix and prudence. The
  world's comparable figure is the eventual shortfall over the
  balance still outstanding at that invoice age. That age is days past due plus the 28 days to pay.
  The draw used 20,000 £100 debit exposures per cell, with credit closures excluded as Centrica's
  bucket excludes them.

  | world cell | at issue | ≥30 days | ≥90 days |
  |---|---|---|---|
  | LOW stress, no tenure/channel multiplier | 15.4% | 51.8% | 82.1% |
  | MODERATE | 30.2% | 46.9% | 80.0% |
  | HIGH | 44.5% | 47.5% | 61.0% |
  | private renter, standard credit, LOW | 25.9% | 65.8% | 85.5% |
  | owner, direct debit, LOW | 10.7% | 42.9% | 78.6% |

  Both ladders rise with age and meet near the old end. The world reaches 80–86% at 90 days in its
  LOW and MODERATE cells, against 87.8%. **At issue, the LOW tier loses about half of what Centrica
  provides for: 15% against 32–37%.** Only the MODERATE and HIGH cells reach it. Even a private
  renter on standard credit is at 26% at LOW stress, and most of the book is at LOW stress. A provision is one supplier's expected loss, prudence included, on its own book
  mix, so this bounds the world's exit loss and does not set it. It is not yet a defect because the
  module is unwired. It is the number to look at first when it is wired: if the book's final bills
  lose well under 30% at issue, the gone-away base rate (`GONE_AWAY_BASE_BETA`, mean 0.12, an
  admitted choice) is the first suspect, ahead of the multipliers.
- **What the run actually did with a mover's final bill (found 2026-10-10).** Nothing: the mover's
  account never closed. `run_phase2b` keeps movers off `churned_billing_accounts`, rightly, because a
  move is not a registration loss. But phase 4c, the billing ledger and the decision probe built
  their closure roster from that list alone, and the reducer dropped `home_move_outs`. So a mover
  got no SLC 21B final read and no SLC 14 refund of credit, and an unpaid final bill sat as a
  stayer's live arrears, with no write-off. Repaired the same day:
  `simulation.household.households_whose_account_closed` adds the movers, and all three consumers
  read it. The mover's exit now goes through `arrears_engine`'s ordinary close rule, which draws a
  final bill's failure at the **mid-tenure** rate. Measured on the same basis as the table above
  (20,000 draws per cell, after the 12.2% post-write-off recovery): **0.74% at issue at LOW stress,
  3.0% MODERATE, 8.8–9.3% HIGH**, by direct debit or standard credit alike. That is a fortieth of
  Centrica's 32–37% at LOW, and a twentieth of what the unwired module gives. So there are now two
  exit models, and the live one has no exit shape at all. The next step is to fold
  `final_bill_outcome` in as the close-time draw for a mover's final bill, and not add it beside
  the close rule. That would be two implementations of one exit.
- **Folded in, 2026-10-10 (B7 slice 7).** A mover's final bill is now decided by
  `final_bill_outcome`, through `arrears_engine.mover_final_bill_outcome`, which the P&L, the
  billing ledger and the DD book each ask first. A traceable part payment is booked, and the case
  is for the rest. A gone-away balance is booked wholly unpaid, because its 0–20% recovery band is
  the post-close collection that the register's 12.2% already returns. Measured on £100 final bills
  (20,000 per cell, three in four by direct debit, after the 12.2%): **13.4% lost at issue at LOW,
  26.3% MODERATE, 38.6% HIGH.** That replaces the 0.74% / 3.0% / ~9% above. LOW is now about 40% of
  Centrica's 32–37%, not a fortieth of it. The gone-away base rate (`GONE_AWAY_BASE_BETA`, mean
  0.12) is still an admitted choice, and it is the first suspect if the book's exits read low.

### 5.2 The company: a complete change-of-tenancy machine with no input

- `company/crm/change_of_tenancy_register.py` has a `TenancyChangeCoupler`. It joins MOVE_OUT and
  MOVE_IN into a tenancy change, holds two deemed legs (`VOID_OCCUPIER` after move-out,
  `NEW_OCCUPANT` from possession), and routes the exit to `company/billing/account_closure.py`'s
  final-bill outcome. It is event-arrival tolerant: MOVE_IN before MOVE_OUT is treated as the
  "occupier" case. Its design matches §1 well. **It has no production caller.**
  `simulation/dd_balance_book.py` says so, and a grep finds callers only in its tests.
- **A conflation inside it.** The docstring calls the move-out-to-move-in window "the 'occupier'
  account" and puts Ofgem's £1.1bn–£1.7bn inside "exactly that first leg". Ofgem's "the occupier"
  account is the **new occupier who is living there unnamed**: "bills build up under these anonymous
  accounts until the individual contacts a supplier to register" (quoted in the module). That is case
  B, and the energy is a real person's. A **void** (case D) is an empty home with landlord liability,
  little consumption and no debtor in residence. From the supplier's side the two look alike until
  someone makes contact, which is exactly why they must be kept apart in the world. The cross-check is
  still useful: £1.1–1.7bn of £4.4bn is 25%–39%, consistent with the CfI's 20–40%. The 30 October 2025
  Ofgem source the module cites was not re-read in this pass.
- `company/billing/cot.py` sets the deemed rate to "SVT + 20% uplift, capped at Ofgem domestic price
  cap". It uses a hand-typed SVT and cap table, including **cap values for 2016–2018, before the default tariff
  cap existed** (it began 1 Jan 2019; only the prepayment cap applied, from Apr 2017). It also has a "28 days … regulatory trigger to
  place on named SVT", for which this pass found no regulation. Ofgem's guidance (§1) says that while
  the cap is in force, deemed rates are governed by it, and Citizens Advice says the deemed contract is
  the supplier's default/SVT. The 20% uplift, the tables and the 28-day trigger are unsourced. **It has
  no production caller** (only `tests/company/billing/test_cot.py`). It is a dead module carrying
  invented constants. Retire it or point it at the cap source, but do not wire it as it stands.
- `company/crm/life_events.py`, `life_event_impact.py`: MOVE_IN and MOVE_OUT exist as types, mapped
  to "COT process / Final read & bill / New customer assessment". No producer was found.
- `company/crm/porting_loss_register.py` has `SwitchReason.MOVING_HOME`. Check whether it is
  populated from an observable, such as a customer stating it, a forwarding address, or a CoO-flagged
  loss. If it is populated from the world's departure cause, it breaches the wall.
- **What the seam carries for a loss.** `interface/contracts/registration_loss_seam.py` carries a bare
  registration-status notice. Its `FORBIDDEN_TRUTH_FIELDS` exclude the reason. That is correct for a
  switch. For a move, a real supplier usually *does* learn something: the customer calls to give
  notice, or a CoO-flagged switch arrives at the vacated premises. That observable is absent because
  the event is absent.
- **No home-mover retention offer** ("take us to your new home") exists. The only "win" is the
  premises-successor roll above.

### 5.3 Staging

- `docs/staging/SEAT_FINDING_THE_SECOND_FORCED_HOME_MOVE_LEG_REUSES_THE_FIRSTS_FABRIC_TRACES_2026-10-02.md`:
  open, LATENT, test performance only (shared demand traces cut a test leg from 87.6s to 36.2s). No
  domain content.
- `docs/staging/done/SEAT_FINDING_TWO_LIFE_EVENT_RATES_ARE_PER_PERSON_FIGURES_APPLIED_PER_HOUSEHOLD_2026-10-02.md`:
  resolved 2026-10-03 for new_baby and job_loss. **The same check applies to any future move stream**:
  the EHS rates are per household, the 2016 Ofgem 11% is per person, and only the household figure is
  the right unit for a premises event.
- Several `records/` notes (successor with no supply point, a win credited once and rolled again, red
  home-move controls) concern bookkeeping inside the successor path. All of them sit on the
  definitional error in 5.1.

---

## 6. Gaps

**In the published record** (each must stay an explicit `None` with this reason, never a placeholder):
1. The number of unnamed ("the occupier") accounts, how long they stay unnamed, and the average debt
   on one. Ofgem requested these in Dec 2025 (CfI Q1–Q2). Check its Spring 2026 response, and the
   suppliers' published responses, next.
2. The share of new occupiers who stay with the incumbent, and the share who switch at move-in.
3. The share of movers who take their supplier with them.
4. Void length and void consumption for domestic premises.
5. An official monthly seasonality of moves, especially for private renting. HMRC monthly transactions
   is a partial proxy for owner-occupiers only, and was not extracted.
6. The share of a supplier's losses that are moves. Ofgem 2024 bundles moving with supplier failure
   (4%).
7. Scotland and Wales tenure mobility, and the 2016–2025 EHS mover time series.
8. ~~The statutory or licence locus of the two-day liability rule, the 6-week final bill and the
   10-working-day refund.~~ **Two of three closed 2026-10-08 (§8):** the two-day rule is SLC 24.1, and
   the six-week final bill is SLC 27.17. The 10-working-day credit refund is still unlocated.
   **The third closed 2026-10-24 (§8.8):** it is regulation 6D of the Electricity and Gas (Standards
   of Performance) (Suppliers) Regulations 2015, inserted by SI 2019/218. It is not in the SLCs.
9. The domestic D-flow and gas-flow mechanics of a CoT read after CSS go-live (Jul 2022), beyond the
   CSS CoO indicator.

**A practitioner question for the director (the third side):** is it normal for a GB supplier to
**learn of a move-out mostly from the customer**, and of a move-in mostly from the "occupier" letter
cycle or from a CoO-flagged switch? And roughly how long does a typical unnamed account run before
contact? No published source states either, and both set the discovery latency the world should
generate.

**In our code** (from §5):
- G1. No move event in the world. Moves are a relabelling of renewal churn.
- G2. Every churn is treated as a move (the successor "win" roll), on unsourced 0.55 / 0.35 baselines.
- G3. `home_move` is missing from the departure-cause partition, and the debt objection blocks an exit
  that in reality cannot be blocked.
- G4. The company-side CoT coupler, final-bill outcome and deemed legs are built but unfed. `cot.py`
  is dead and carries invented constants, including a cap before 2019.
- G5. The CoT register conflates the void (D) with the unnamed occupier (B).
- G6. There is no move observable at the seam, and no mover retention proposition. (§8 states what that
  observable carries.)

---

## 7. What this says about the order of work

The canon places home moves at step 5 as a lever. The evidence says **the world's half of home moves
is foundational to steps 2 and 3**, and only the company's *proposition* (retention offers, move-out
debt prevention) is a step-5 lever. The proposal, with its reasons:

1. **Move the world's move stream into step 2 (unbilled energy and billing accuracy).** Step 2 says
   "the world must generate unbilled energy the way it arises in reality". By Ofgem's own account the
   largest structural source of unbilled and then unpaid domestic energy is the unnamed new occupier on
   a deemed contract, 20–40% of all debt, stable since before the crisis (§2.5). The other source is
   the estimated read at the boundary, which moves value between two households (§3). Without a
   tenure-driven move-out and move-in stream, step 2 cannot generate that category at all. The inputs
   already exist: the EHS rates in `arrival_route.py` and tenure on every household. The consumer
   already exists: `TenancyChangeCoupler`. So the "four tests" score it high on *rests-on*, *world
   readiness* and *knowledge exists*.
2. **Split departures into switch and move before forward CLV (step 3).** A churn hazard that mixes
   price-driven switches with tenure-driven moves cannot be forecast on held-back history. The two
   respond to different things: moves are roughly 5× more likely in private renting and indifferent to
   price; switches respond to price. The current successor roll also overstates retention for every
   switcher (G2). Step 3's base case would inherit that bias. The fix is small and comes first: remove
   the win roll from non-move departures, and add `home_move` to the cause partition, driven by tenure,
   not by the renewal clock.
3. **Debt (the first step-5 lever) depends on it.** "Debt cashflow forecasting" leads step 5. A fifth
   to two-fifths of the debt stock is born at a change of tenancy, and the current code can never
   create it, because a debtor can only leave by a switch the debt objection blocks (G3). Debt work
   built before the move stream exists would be calibrated on a world missing up to 40% of the
   phenomenon.
4. **Keep in step 5:** the home-mover retention offer, mover-journey communications, and move-out debt
   prevention (actual read on the day, forwarding-address capture, tracing). These are company
   choices, and the public record has no benchmark for their value (gaps 2–3). Note that Ofgem's 2026
   remote-prepay-on-move-out proposal postdates the 2016–2025 record and must not be wired into the
   historical run.

**Cheapest first action, should the seat take the proposal:** retire or source `company/billing/cot.py`
(G4, invented constants, no caller), and write down the switch-versus-move definition beside
`saas/home_move_win_rate.py`, before anything new is built on the successor path.

---

## 8. The move-out notice: what the supplier is told, and what a move-with-us offer is

*Added 2026-10-08 for the director's ruling 3 (home-mover retention as a lever, now that moves are on
in the world, `ada37371c`). The question is narrow. When **our** customer moves out (case A, and case
C if they take us with them), what does the supplier receive, and what may it offer? Primary text:
Ofgem, *Electricity Supply Standard Licence Conditions*, consolidated to 1 August 2025 (the edition
`back_billing_and_liability.md` cites), and Ofgem, *Tackling energy debt when moving home – Call for
Input: Summary of Responses*, June 2026 (OFG1164).*

### 8.1 What a move-out notice is

**Definition.** A move-out notice is **the departing customer telling the supplier that they stop
owning or occupying the premises on a date.** The licence makes that notification the event that
ends the contract. It is the only industry-recognised trigger the departing customer controls. No
registration flow carries it. The supplier stays registered at the meter point, so the Central
Switching Service tells it nothing (§3).

**The licence sets its clock, and not by a lead time picked from guidance.** SLC 24.1 requires every
domestic contract to end:
- (a) "if the Domestic Customer has notified the licensee at least two Working Days before the date
  on which he stops owning or occupying the premises, that date"; or
- (b) without that notice, at "the first to happen of": (i) "the end of the second Working Day after
  the customer has notified the licensee that he has stopped owning or occupying the premises", or
  (ii) "the date on which any other person begins to own or occupy the premises and takes a supply".

SLC 24.2(a): "the Domestic Customer is liable for the supply … until the date on which that contract
ends". (This closes the "two days" locus that §1 and gap 8 left open: it is SLC 24.1, mirrored in the
gas SLCs. Citizens Advice's "at least 48 hours" is the same rule restated in consumer language.)

**What that means for the world we run.** `run_phase2b` ends the mover's liability **on the move
date** (`term_window_under_move`). Under SLC 24.1 that is exactly case (a): the customer gave at
least two Working Days' notice. So the world has *already* decided that every mover notified in time.
The latest notice consistent with that decision is **two Working Days before the move date**. That
date is the notice's clock, and it is set by the licence rule, not by a number we picked. It is the
least warning a supplier gets from a customer who gives notice in time. So it cannot flatter a
retention offer, in the same way that `registration_loss_seam.py` dates every CSS switch on the ASAP
floor.

**Who does not notify, and how often: GAP.** Ofgem's June 2026 summary says accounts "often remain
unnamed for extended periods due to delays in receiving move out and move in notifications from
consumers" (¶2.2), and that "customers often expect the process to be automatic and do not seem to
understand the need to contact their supplier proactively" (¶2.8). Neither paragraph gives a share,
and the consumer bodies had no quantitative data (¶2.4). The late-notice and no-notice paths (24.1(b))
are therefore real and unsized. The world does not draw them, and the notice carries no field for
them. When they are sourced, a late notice changes the liability end (24.1(b)(i)), not only the
notice date, and the world must change both together.

### 8.2 What the notice carries

| Item | Does the supplier learn it? | Source / status |
|---|---|---|
| The account and the meter points | Yes: the customer is identified on contact | The contract is per premises (SLC 24.1 "in relation to the Domestic Premises to which it applies") |
| The date they stop occupying | Yes: it is the content of the notice | SLC 24.1(a) |
| When the notice was given | Yes: the supplier's own contact record | SLC 24.1(a)/(b) turn on it |
| A final meter reading | **Sometimes.** The customer may give one. A smart meter in smart mode can be read remotely on the day; otherwise the read is estimated | §3; Citizens Advice moving-home page. Which reads are actual is a property of the meter, not of the notice, and is not carried on it |
| A forwarding address (for the final bill) | **Only if the customer gives one.** No licence condition obliges the customer to give one, or the supplier to obtain one. SLC 27.17 obliges only "all reasonable steps to send a final Bill … within 6 weeks" | SLC 27.17 (closes §4's 6-week locus). Share of movers who give one: **GAP** |
| **The destination premise** (the meter point they move to) | **Only if the household tells it.** No industry flow links the two premises. A forwarding address is a postal address for a bill and does not identify a meter point the supplier could supply | §3 "whether a new customer at one address is the same household that left another unless the customer says so". Share who tell: **GAP** |
| Why they are moving, tenure, who moves in next, whether the home will be empty | **No** | §3 |

So the minimal honest observable has three fields: the account's meter point, the move-out date, and
the date the notice was received. A destination field may exist only as **absent unless the
household told it**. The world has no sourced rate at which households tell, so it is always absent
for now, with that reason stated.

### 8.3 What a move-with-us offer is under the SLCs

**Definition.** A move-with-us (home-mover retention) offer is the supplier offering to supply the
departing customer **at their new premises**. It is usually done by carrying the current tariff
across and waiving the termination fee that closing the old contract would otherwise trigger.

**What the licence says.**
- **A mover has no licence exemption from a termination fee.** SLC 24.3 lists every exemption: the
  contract is indefinite (a), it is in its indefinite period (b), the supplier has notified a price
  rise or disadvantageous variation (c), or it is a Relevant Fixed Term Default Tariff (d). Moving home
  is not on the list. The 49-day Switching Window protection (24.8(b), 24.17) covers **switching
  supplier**, not ending a contract by moving out. A fee that is charged must be "proportionate" and
  no more than "the direct economic loss to the licensee" (24.3A).
- **So the fee waiver is the supplier's own lever, not a regulatory entitlement.** Consumer guidance
  agrees: Citizens Advice tells movers on a fixed deal to "check whether an exit fee applies" and to
  ask whether the supplier will "transfer your current tariff to your new home" (§4). Supplier
  practice, as reported by comparison sites (Selectra on E.ON and OVO moving pages, accessed
  2026-10-08): most suppliers waive the exit fee if the tariff moves with the customer, and some
  charge it per fuel on closure. These are commercial summaries, not sources for any number.
- **At the destination the incumbent is someone else.** The mover arrives at a premises with its own
  registered supplier and is on that supplier's deemed contract (§1, case B). Taking the old supplier
  with them is therefore a **switch at the new premises**, gained by the old supplier. It runs through
  the ordinary registration route, with the Change of Occupier indicator set (§3, case B''), so the
  destination's incumbent cannot object on debt grounds. Whether a fixed tariff can carry over also
  depends on the new premises' meter and region: a tariff's rates are regional. **GAP:** the licence
  text read here says nothing specific about carrying a tariff to another premises. Whether that is a
  new contract (with fresh SLC 23/25 obligations) or a variation of the old one was not established.
- **Under the 2016–2025 record no regulation prices this offer.** No take-up rate is published (gap 3
  in §6, re-confirmed: the June 2026 summary has none). That is why this section builds no retention
  decision and no take-up rate. It builds only the notice a decision would need to see.

### 8.4 What a real supplier sees, in order

1. **Two Working Days before the move (at latest):** the customer's notice, with the account, the
   move date and possibly a forwarding address. This is **the one moment a retention offer can be
   made before the household is gone**. It is the only observable in this list that arrives before
   the move.
2. **On the move date:** a final read (actual if smart or customer-read, otherwise estimated). The
   contract ends.
3. **Within 6 weeks:** the final bill (SLC 27.17). Then the final-bill outcome (paid, late, partial,
   unpaid or gone away), which the world already resolves behind the wall
   (`simulation/final_bill_outcome.py`).
4. **From the move date, at the vacated premises:** the incoming occupier's deemed supply. It is
   unnamed until someone makes contact (§3, `sim/customer_state_layer.unnamed_until`).

### 8.5 Gaps this section adds or confirms

- G8.1 The share of movers who notify in time, notify late or never notify, and the lead-time
  distribution of those who notify. Not published (OFG1164 ¶2.2, ¶2.4, ¶2.8).
- G8.2 The share of movers who give a forwarding address, and the share who name their destination.
- G8.3 Whether carrying a tariff to a new premises is a new contract or a variation, and how a
  regional tariff is re-rated.
- G8.4 The take-up of a move-with-us offer, and its value (= §6 gap 3). **Re-searched 2026-10-12**
  for the four-principles audit (§2 P1), and still a gap. Nothing published splits movers into
  "took us with them", "stayed on the destination's deemed contract" and "switched again soon
  after". The nearest figures count a different population. Ofgem/Ipsos *Consumer Engagement
  Survey 2019* (p.27, Q161) gives "I moved home" as the prompt for 7% (2017), 7% (2018) and 8%
  (2019) of those who switched or compared. That is engagers who moved, not movers who engaged, and
  no mover denominator is published to invert it. The same report gives 22% for first-time
  switchers, on n=191. The one take-up-shaped figure is still BFY Group's unnamed supplier
  (mover retention raised from ~5% to ~30%; a consultancy case study with no base or price,
  already in `a_save_offer_against_the_switching_rules_and_the_seam.md` §2a). No source compares a
  mover's stay with a renewer's at the same price. So the world's `take_up_scale` k stays a
  labelled range [0, 1]. **A reality check, not an input (canon W8):** at k = 1 the 40-founder run
  of `68793db33` had 9 of 15 offered movers follow (60%). That is twice the best figure any
  supplier has claimed (30%). The evidence leans towards the low half of k, but it is too weak to
  narrow the range.
- G8.5 ~~The 10-working-day credit refund's locus (the remainder of §6 gap 8).~~ Closed 2026-10-24:
  GSoP regulation 6D (§8.8).
- G8.6 Where a mover goes, finer than a region. The same-local-authority share of moves is not
  published at GB level (ONS internal migration excludes within-LA moves). Of moves that change
  local authority, 51.9% stay inside the same ONS region (year ending June 2020), so at least 51.9%
  of all moves stay in-region. That is a lower bound. Source:
  `how_far_gb_households_move_and_what_their_new_home_uses.md` §1.
- G8.7 The ONS-region to electricity-region (GSP group) lookup. It exists (postcode to GSP group) but
  is not in this repo. It binds only where prices are regional (§8.6).
- G8.8 A household's consumption after a move. No before/after panel of movers was found. Across
  households, the dwelling explains more of a home's use (39%) than socio-demographics (24%)
  (Huebner et al. 2015). How fast a mover's use converges to its new home's level is not published.

### 8.6 The move-with-us offer as this world builds it: the rules, the evidence, and the choices

*Added 2026-10-11, before the build, under the director's rule "knowledge before build". Published at
`site/knowledge/home-moves/` (the `home-moves` entry of `site/data/knowledge_topics.json`).*

**What the rules require.**
- The notice: SLC 24.1(a) ends the contract on the move date if the customer gives at least two
  Working Days' notice (§8.1). The world already ends every mover's liability on the move date, so
  every notice is on time and is dated at that latest point.
- The exit fee: SLC 24.3 gives a mover no exemption from a fixed-term fee. Waiving it is the
  supplier's choice (§8.3). This world charges no fee on a move, so the waiver costs nothing here.
  That understates a real waiver's cost; it is a gap in the world, not a choice.
- Retention pricing: SLC 22B's derogation (to 31 March 2027) lets a supplier offer a fixed tariff
  only to existing customers (`a_save_offer_against_the_switching_rules_and_the_seam.md` s.1d). A
  move-with-us offer cuts no price: it carries the price the household already pays. If carrying
  it is a variation of the existing contract, 22B is not engaged. If it is a new contract (G8.3),
  whether a tariff offered only to movers sits inside 22B or its derogation is NOT ESTABLISHED.
  The world does not test it.
- At the new home the incumbent supplier holds the meter. Taking us with them is a switch gained
  there, through the ordinary registration route.

**What published practice and evidence say.** Suppliers commonly waive the exit fee if the tariff
moves with the customer (comparison-site summaries, §8.3; practice, not a number). Most moves stay
local: at least 51.9% stay in-region (G8.6). By tenure, the share moving within 5 miles is 70% for
social renters, 51% for owners and 45% for private renters (EHS 2021-22 Annex 1.5). A dwelling
predicts its consumption better than its occupants do (G8.8).

**What is unknown (GAP).** G8.1 to G8.8 above. G8.4 (how many movers take the offer) is the one the
result turns on.

**The design's choices, and why.**
1. *Who is offered.* Our household on either tariff, wherever the company's own estimate says
   carrying it earns a margin. The estimate is the rate in force, less the forward cost the rate was
   struck against, on the company's billing consumption estimate. A default-tariff household is
   offered our default tariff at its new home. The company reads only the notice, its own book and
   its own Priority Services Register.
2. *How the world answers (k).* No take-up rate exists, so none is invented. The household answers
   on the roll of its NEXT decision with us (its next renewal, or its next default-tariff segment).
   It answers against k times the world's own P(stay) at the tariff it would carry. For a fixed
   term, that P(stay) is the probability the world rolled its renewal onto that tariff against. For
   the default tariff, it is the current segment's stay probability, annualised:
   (1 - p) ** (365.25 / days). k = 0 means no mover takes us; k = 1 means a mover stays as often as
   a household deciding at that price. Both ends are run. A household still in its first fixed term
   has no world P(stay) yet and does not move with us. That can only understate the lever.
3. *Where it goes.* The destination stays in the origin's ONS region with probability
   `q1_move_destination_in_region_share`. The default is 0.519, the derived lower bound (G8.6); the
   range runs up to 0.70, the social-renter within-5-miles share, which is a distance proxy and not a
   region share. Otherwise the destination region is drawn from the world's own regional household
   mix, excluding the origin. That stands in for the ONS flow marginals, which are not carried. The
   address within the region is the world's household siting draw, and the weather follows that
   cell. This world prices nationally (one rate per fuel, no regional tariff), so G8.7 and the
   re-rating half of G8.3 do not bind the run. They would bind once prices are regional.
4. *What the new home uses.* The destination dwelling is drawn by the world's own premise draw
   (`premise_population.draw_premise_from_joint`, keyed on the destination's id). Its demand is that
   dwelling's physics under the household's own occupancy, not the old home's consumption (G8.8: the
   dwelling outweighs the occupants). The household keeps what belongs to it: its EV, its income
   stress, and every trait the world keys by its account. The dwelling's fields, solar and battery
   come from the new home. Its use snaps to the new dwelling on the move date. The timing is not
   published, so that is an assumption, named.
5. *Which legs.* The electricity leg is carried. A dual-fuel household's gas leg leaves at the move,
   as before: a destination gas annual quantity and its heating-degree cell are not built. That can
   only understate the lever.
   *(2026-10-22: the rules and the choice that replace this are §8.7, written before that build.)*
   *(2026-10-24: superseded. §8.7 is built; a dual-fuel follower's gas leg follows it.)*
6. *The stayers.* Every later term of a carried account is held out of the portfolio premium. The
   carried rate and the renewals priced off it would otherwise teach the stayers' prices. This is the
   same set the price-match save uses.
7. *The vacated home* passes to its incoming occupant exactly as for any mover.

### 8.7 A dual-fuel household's gas when it moves with us: the rules, the evidence, and the choices

*Added 2026-10-22, before the build (K8), from the director's steer of 22 Oct (item 4b of
`docs/staging/advisor/done/DIRECTOR_STEER_THE_FRONT_DOOR_SAYS_PUBLISHING_IS_FAILING_AND_IT_IS_NOT_2026-10-22.md`)
and his ruling of 17 Oct that households move as households. It replaces choice 5 of §8.6 once the
build lands. Nothing new was searched for: every rule below is already sourced in this file or in a
sibling page, cited where it is used.*

**What a gas supply is, at a move.** A supply belongs to a meter point, not to a household: an MPAN
for electricity, an MPRN for gas. The gas register is UK Link, run by the CDSP (Xoserve). Nothing
"moves" with a household. A supplier that follows a mover registers the meter points at the new
address, one per fuel. Before 18 July 2022 the gaining supplier sent "two discrete" requests, one to
MPAS and one to UK Link. Since then CSS can link them on "a single, nominated date", with a "one fail /
all fail" option. (Ofgem Switching Programme, cited in
`unbilled_energy_and_revenue_assurance.md`, "What a change of supplier ends on each fuel".)

**What the rules require.**
- *At the vacated home.* The gas meter keeps flowing. Whoever moves in is on the registered gas
  supplier's deemed contract from the day they start to consume, exactly as for electricity: Gas Act
  1986 Sch 2B para 8(1), and Ofgem's guidance ("gas and/or electricity", ¶2.10), at a rate held to
  the cap (¶2.19). The leaver's liability ends under the gas licence's mirror of SLC 24.1 (§8.1).
- *At the new home.* Until the household registers there, it is on the deemed contract of whoever
  supplies each of the new home's meters, one per fuel (case B of §1, at the destination). Taking
  us there is a switch gained on each fuel, through ordinary registration. If we already supply a
  destination meter, that fuel is case B', handled inside the supplier.
- *A new home may have no gas meter.* About 14 to 16% of GB homes have no mains gas supply
  (`mains_gas_is_a_meter_fact_not_a_grid_fact_need_2026.md`: EHS AT3.5, 14.0%; DESNZ 2023, 16%).
  A dual-fuel household moving into one of these homes arrives electricity-only. That is a true
  outcome, not a defect, and no supplier can carry a gas leg there.

**What published practice and evidence say.**
- Inside this run's window, about 90 to 94% of switching homes with gas moved both fuels together
  (`how_a_gb_domestic_book_splits_by_fuel_and_how_a_two_fuel_home_switches.md`). A supplier's
  moving-home journey asks for both fuels (§8.3, practice and no number).
- The gas annual quantity (AQ) belongs to the meter point. Since Project Nexus (UNC432, June 2017) it
  rolls monthly from reads; before that a small site's AQ changed once a year
  (`read_access_and_theft_duties.md`, §2.1). A gaining supplier's first estimate of a new occupier's
  gas use is therefore the previous occupier's AQ. This is the same trap as the electricity EAC (§3).

**What is unknown (GAP).**
- G8.9: how often a mover who takes its supplier along carries one fuel only. Nothing published
  gives it. The switching figure above is for switches, not for moves.
- G8.10: how often the two fuels at a new home start on different dates. Before CSS, two discrete
  registrations could land apart. The share is not published (the same GAP as the dual leaver's in
  `unbilled_energy_and_revenue_assurance.md`).
- G8.11: the previous occupier's AQ at the new meter. The world draws no previous occupier at a
  destination, so the meter point holds no history from before the move.

**The design's choices, and why.**
1. *The household answers once, for every fuel it has.* The answer stays on the decision leg (§8.6,
   choice 2). A household that moves with us is supplied at its new home on every fuel it was supplied
   on and the new home can take, from the same move date. That is the single-nominated-date dual
   switch, and the 90 to 94% both-fuels norm. A one-fuel carry (G8.9) and a split date (G8.10) are not
   built. Both can only move value between the two legs, and neither creates a household.
2. *The gas leg follows only to a home that can hold a gas account.* The test is the one the book
   already uses to give a won home its gas leg (`live_population._gas_leg_for`): the destination
   dwelling's `DrawnPremise.commodity` is "gas", meaning a gas burner on a mains supply, from the
   world's own premise draw. Where it is not, the gas leg ends at the move, as today, and the
   move-with-us log records the named reason.
3. *What the new home burns.* In this world a gas leg's annual quantity is the household's own: its
   TDCV band draw (`live_population._gas_aq_kwh`), scaled by its dwelling's EPC and heating system
   (`household_demand.gas_eac_multiplier_for_date`). Its daily shape spreads that quantity on the
   heating degree days of the premise's cell (`gas_settlement.run_gas_term`), with the heating share
   fitted to the dwelling's own trace (W2_30). Gas demand is not read from the fabric trace. So at the
   new home the band stays the household's, and the multiplier, the cell's weather and the heating share
   become the new dwelling's. The weather changes on the move date. The multiplier and the heating share
   are read once per term, as they already are, so they change from the end of the carried term, not
   on the move date. That is a stated simplification of at most one term.
4. *The company's first volume at the new meter.* The registered AQ stays the household's band draw.
   Because of G8.11 there is no previous occupier's AQ to put there. So the company's first gas
   estimate at the new home is the household's own use, which is kinder to the company than the trap
   described above. That is a stated assumption.
5. *The vacated gas meter* passes to its incoming occupant from the move date, after the void, as it
   already does (`_admit_incoming_occupant`, per fuel).
6. *What the change cannot do.* It adds no household and no offer, because the offer is still asked
   once, on the decision leg. It changes how many supply points the book keeps after a move, and the
   gas revenue and margin those points carry. Value-arms results taken before it are not comparable
   with results after it on any arm where movers follow (k > 0).
7. *A follower is not an exit.* A leg that moves with us stays our customer's account. Its bills after
   the move are not drawn as a departing customer's final-bill exit (`arrears_engine`'s exit draw:
   gone-away, no forwarding address). The household told us where it was going, and we supply it there.
   Read from the code before this build: a carried electricity leg keeps its move-out stamp
   (`run_phase2b._moved_out_on_by_leg`), and the exit draw reads that stamp for every bill from the
   move month on. The build measures what it cost.

**Built 2026-10-24** (`simulation/run_phase2b._carry_gas_leg`, `sim/weather_hdd.relocate_premise_sky`;
control `tests/simulation/test_a_dual_fuel_movers_gas_follows_it.py`). Choices 1 to 5 are built as
written. Choice 7 is built for both legs: a leg that follows drops its move-out stamp, so its later
bills are not drawn as a gone-away final bill. What it cost was not measured separately from the gas
leg; the arm comparison is the place to measure it. Not built, named in the run's log: a household
we supply with gas alone does not follow, because its destination is drawn on the electricity leg
(choice 1 says every fuel; this is a gap, not a choice). First measurement, one arm at k = 1 to
2018-12-31: 22 households answered yes, 9 were supplied at a new home (the rest refused by name,
mostly a destination cell the weather store does not hold), 4 took their gas, 2 arrived
electricity-only at a home with no mains gas, and 3 had no gas leg with us.


### 8.8 A mover's final bill: the closing read, the final bill, the credit and the debt

*Added 2026-10-24, before the build (K8). The build is the move-out kind in
`company/billing/billing_accuracy.py` (`move_out_final_bills`) and the move-out and final-bill
events on the household record (`tools/generate_customer_reaction_chain.py`). Sources: the SLC text
already cited in §8 and in Sources, and SI 2019/218, read 2026-10-24.*

**What the rules require.**

| Step | The rule | Locus |
|---|---|---|
| The closing read | The contract ends on the move date. The supplier takes "all reasonable steps" to get a read for the final bill. It may be the customer's own read on the day, a smart read, or an estimate when neither arrives | SLC 21B (reads, `slc_21b_21ba_reads_and_back_billing.md`). No rule says the closing read must be actual |
| The final bill | "all reasonable steps to send a final Bill or statement of account … within 6 weeks" of the contract ending, whether it ended by a switch or otherwise | SLC 27.17 (p.246, consolidated text) |
| Compensation for a late one | A fixed payment, £30, then £40 for breaches from 2 January 2025 | GSoP 2015 as amended. Ofgem, *Good Energy pay a total of £150k …*, 7 May 2025, and *Octopus Energy pay a total of £1.5m …* (failures to issue final bills to former prepayment customers) |
| The credit | "within 10 working days of issuing a customer's final bill, or if applicable, corrected final bill, refund any outstanding credit balance". It applies where the customer switches under a valid contract or the supplier's responsibility "has otherwise terminated", so a move-out is in scope | GSoP 2015 reg 6D, inserted by SI 2019/218 reg 3. **Correction, 2026-10-24:** the run's `credit_refund_log` and `simulation/credit_refund_events.py` label this "SLC 14". That is the wrong locus. The deadline is the same, so no figure moves |
| The debt | A debt on the final bill is the departing customer's. The supplier pursues them at a forwarding address if it has one. It may not charge the incoming occupier for it | Citizens Advice, *Check if you're responsible for paying an energy bill* (Sources). The licence text that says so was not found: **GAP** |
| Back-billing on the final bill | The 12-month limit applies to a final bill as to any other. A catch-up for energy used more than 12 months before it is barred | SLC 21BA. This is already measured as K3 and the DD money line (`billing_accuracy.py`) |

**Three clocks, not one.** The final bill runs from the move date. The refund runs from the *issue* of
the final bill, in working days. The debt has no deadline in the rules. A measure that puts them on
one axis would grade a refund against the move date, which no rule does.

**What the published evidence says about practice.** The enforcement cases are about missing final
bills, not late ones. In each, closed accounts got no final bill at all, so no refund was ever
triggered. Ofgem: "this money is nonetheless owed to the customer who has accrued the credit and
should be returned" (Good Energy, 2025). The share of final bills sent late, or on an estimated
closing read, is not published: **GAP** (G8.9).

**Gaps this adds.**
- G8.9 The share of a supplier's final bills issued after six weeks, and the share on an estimated
  closing read. Ofgem publishes enforcement totals, not rates.
- G8.10 The licence text for "a debt follows the person, not the premises". Only Citizens Advice
  guidance was found.
- G8.11 The share of a final-bill debt recovered after the move (see §5 for what the world draws
  from Centrica's provisioning).

**The choices the build makes, and why.**
1. *Read the published run, with no new arm.* The measure reads the supplier's own bills (the final
   bill is stamped `final_bill`), the move-out register (`home_move_outs`: the move date a notice or
   a closing read gives) and the refund log. Nothing it reads is the world's truth.
2. *The issue date of a bill is its period end.* `company/billing/invoice.py` sets it that way, and
   the run's bill record carries no other. So the days from move-out to final bill are fixed by
   that rule. The late-final-bill branch cannot fire in this run. That is a property of the model,
   not a performance, and the measure says so beside the count. A test proves the branch fires on a
   bill issued late.
3. *The closing read is graded actual or estimated.* An estimated closing read is not a breach, but
   it is where a mover is most often billed wrongly (§2.5). It is counted, and nothing grades it
   against a rule.
4. *The credit is graded in working days from the final bill's issue* (reg 6D), against 10.
5. *The debt left on the final bill is `None`, with its reason,* until the run publishes each closed
   account's balance at its final bill. The published report has no such field, and a debt guessed
   from the bill's face value would count every paid bill as owed. **Superseded 2026-10-25 by
   §8.8a:** the run now publishes that balance.
6. *The incoming occupier's account names the account it succeeded* at the same meter point. A real
   supplier knows this: a new account opens on a meter point it already supplies. The run publishes it
   as `occupier_successions` from the next run on. A run that has no such record says so.

#### 8.8a The closing balance: what the rules require, what a supplier records, and what the run publishes

*Added 2026-10-25, before the build (K8). The build is `closing_balances` in
`simulation/arrears_engine.py`, published by the run as `closing_balances` and read by
`move_out_final_bills`. Sources: the rows of §8.8 above and `debt_and_collections.md` (P5, SLC 27).*

**What the rules require of the balance.**

| The balance | The rule | Locus |
|---|---|---|
| Stated on the final bill | The final bill is a "Bill or statement of account" (SLC 27.17). A statement of account states the balance. So the closing balance is a figure the supplier has already issued, not one it has to estimate | SLC 27.17 |
| A credit (the customer is owed) | Refunded within 10 working days of the final bill's issue | GSoP reg 6D (§8.8). The credit is net of that contract's own charges: SLC 27.16 defines it as payments in excess of the charges due "under that Domestic Supply Contract", so it is per fuel |
| A debt (the customer owes) | Pursued against the departing customer, never the incoming occupier. Then a DCA, then a sale or a write-off. No supply lever is left | Citizens Advice (§8.8); `debt_and_collections.md` P5 (Centrica 2025: final bills 84% provisioned). The licence text: **GAP** G8.10 |
| How a debt is pursued once they have gone | SLC 27.8 (arrangements that take account of ability to pay) binds the supplier's dealings with a Domestic Customer. Whether it, or the SLC 27 debt-collection conduct rules, still binds the supplier once supply has ended is not stated in any text we hold: **GAP** G8.12 |
| Settled (nothing owed either way) | No rule acts. It is still a result: the measure counts it, so a branch that never fires is seen |

**What a real supplier records.** One signed figure per account at its final bill: the closing balance
on the statement. It is the supplier's own ledger (charges less payments and credits), so it crosses
no wall. Which debts then go to a DCA and when is not published per supplier: **GAP**, already G8.11.

**The choices the build makes, and why.**
1. *One balance, from the book the P&L writes off.* The run settles each bill in
   `arrears_engine.balance_settlement_from_outcomes`: a failed bill is outstanding, a credit bill or an
   overpaid repayment is credit on that fuel's contract, a credit nets the oldest debt first. The
   closing balance is what that walk holds at the final bill's due date, before the write-off at close:
   outstanding less unapplied credit. The write-off at close is that same debt, so the published
   balance and the P&L agree by construction.
2. *Per fuel, because the contract is per fuel.* A leg's `customer_id` is one fuel's account, so the
   balance is keyed by it and never nets across fuels (SLC 27.16).
3. *Owed positive, credit negative,* the sign `move_out_final_bills` already grades.
4. *Named limit: the level direct debit's smoothing balance is not in it.* The engine reads a paid
   bill as paid exactly. A level DD that over- or under-collected against the bills sits in a second
   book, `simulation/dd_balance_book.py`, which already asks the final bill for its own closing
   balance. The two are not summed until they are one ledger (DD3). So the credit count here is credit
   from credit bills and overpaid repayments only, and understates what a DD leaver is owed in a world
   where households pay a level amount. In this run's world they do not: there is one payment truth,
   and a paid bill is paid exactly.
5. *Statute-barred debt is not in the balance.* A bill barred before close was written off on its own
   leg and is no longer recoverable, so it is not carried.

**Gaps this adds.**
- G8.12 Whether SLC 27's debt conduct rules bind a supplier pursuing a former customer.

**The refund reads the same balance (amended 2026-10-25, before the build).** The rule: a credit on
the final bill is refunded within 10 working days (GSoP reg 6D), and a credit is payments in excess of
that contract's charges (SLC 27.16). So the refund and the closing balance are the same figure. The
first printing showed they were not. `simulation/credit_refund_events.py` decided who was in credit
from its own level-DD smoothing balance (the trailing mean of a DD payer's bills less each bill). At
60 founders to 2020-12-31 it refunded 3 move-outs, none of them among the 7 the ledger closes in
credit, and one of them (SYN-2016-052) owes £27.64 on the ledger. That balance was money no household
had paid, because nobody in the run pays a level DD.

The 7 ledger credits, named row by row: 2 are a negative final bill, a true-up on the closing read
(−£37.92 and −£23.32). The other 5 are a credit bill from the middle of the account's life, which the
walk sets only against arrears. With nothing in arrears it waited on the account until the move, for
5 weeks to about 2½ years. That is probably a defect of its own, not a practice. A statement of account
carries the balance forward (SLC 27.17), so a credit would ordinarily come off the next bill's amount
due, and the household would pay that much less. In the walk, each later bill is paid in full beside
the credit. Filed as
`docs/staging/SEAT_FINDING_A_MID_LIFE_CREDIT_BILL_IS_NEVER_SET_AGAINST_THE_NEXT_CHARGE_2026-10-25.md`.
Whatever happens to it in life, the credit is owed at closure.

*Choices.*
6. *The refund fires from `closing_balances`,* not from a balance of its own. A leaver the ledger holds
   in credit is refunded that credit. A leaver it holds in debt, or settled, is not refunded. A leaver
   it holds no balance for is not evaluated, because no balance is not a credit.
7. *Every domestic leaver, whatever it paid by.* Reg 6D binds a domestic credit however it was paid.
   Non-domestic accounts are outside the domestic Standards of Performance and are not graded.
8. *Not DD3 first.* Posting a level DD's over-collection to the ledger needs the world to collect
   level amounts first, and that is a payment-truth change. When DD3 lands, the refund reads it with no
   further change here.
9. *Graded both ways.* `move_out_final_bills` counts `owed_unrefunded` (a ledger credit with no
   refund, which is a reg 6D breach the on-time count cannot see) and `refunded_not_owed` (a refund to
   an account the ledger does not hold in credit).
10. *Named limit: the refund is graded, not booked.* The refund log feeds no cash or P&L line. A credit
    refunded is still not paid out of the company's cash, so the liability it discharges is not
    reduced anywhere. That belongs with DD3.

---

## Sources

- `docs/market_research/how_far_gb_households_move_and_what_their_new_home_uses.md` (this repo,
  2026-10-10): ONS internal migration matrices YE June 2020, EHS 2021-22 Annex 1.5, Huebner et al.
  2015 (G8.6-G8.8, §8.6).
- Ofgem, *Electricity Supply Standard Licence Conditions*, consolidated to 1 August 2025, SLC 24.1-24.3A,
  24.8, 24.17 (pp.216-220) and SLC 27.17 (p.246),
  https://www.ofgem.gov.uk/sites/default/files/2023-03/Electricity%20Supply%20Standard%20Consolidated%20Licence%20Conditions%20-%20Current.pdf
  (fetched 2026-10-08; consolidated text, "not formal Public Register documents").
- The Electricity and Gas (Standards of Performance) (Suppliers) (Amendment) Regulations 2019,
  SI 2019/218, reg 3 inserting reg 6D, https://www.legislation.gov.uk/uksi/2019/218 (read 2026-10-24
  via https://lawplayer.com/uk/act/uksi-2019-218) (§8.8).
- Ofgem, *Good Energy pay a total of £150k to former prepayment meter customers due to a failure to
  issue final bills*, 7 May 2025, https://www.ofgem.gov.uk/decision/good-energy-pay-total-ps150k-former-prepayment-meter-customers-due-failure-issue-final-bills;
  *Octopus Energy pay a total of £1.5m …*, https://www.ofgem.gov.uk/decision/octopus-energy-pay-total-ps15m-former-prepayment-meter-customers-due-failure-issue-final-bills (§8.8).
- Ofgem, *Tackling energy debt when moving home – Call for Input: Summary of Responses*, June 2026,
  ¶2.1-2.8, 3.15, https://www.ofgem.gov.uk/sites/default/files/2026-06/Home-Moves-CFI-Summary-of-Responses.pdf
  (fetched 2026-10-08).
- Selectra, *E.ON moving home* and *OVO moving home* pages (https://selectra.co.uk/energy/providers/eon/moving,
  https://selectra.co.uk/energy/providers/ovo-energy/moving; accessed 2026-10-08): commercial summaries
  of supplier practice, cited for practice only and never for a number.

- Ofgem, *Call for input: Tackling Energy Debt in the Supplier Home-Moves Process*, 9 Dec 2025,
  https://www.ofgem.gov.uk/sites/default/files/2025-12/Tackling-energy-debt-in-home-moves-process-call-for-input.pdf (exec. summary; ¶1.6, 1.13–1.14, 2.1–2.6, 3.5–3.17; Q1–Q2; Information Box 1).
- Ofgem, *Guidance on Deemed Contracts*, 6 Nov 2023, https://www.ofgem.gov.uk/sites/default/files/2023-11/Guidance%20on%20Deemed%20Contracts.pdf (¶2.10–2.19).
- Gas Act 1986 Sch 2B para 8, https://www.legislation.gov.uk/ukpga/1986/44/schedule/2B.
- MHCLG, *English Housing Survey 2023-24 Headline Report: demographics and household resilience* (Annex A), https://assets.publishing.service.gov.uk/media/6746f3242cdbaeed4c527f5f/Annex_A_-_2023-24_EHS_Headline_Report_on_household_demographics_and_resilience.pdf (ch. 1; ch. 3 "Household moves", Fig. 3.4; Annex Tables 1.1, 3.7).
- Ofgem / TNS BMRB, *Consumer engagement in the energy market since the Retail Market Review – 2016 survey findings*, https://www.ofgem.gov.uk/sites/default/files/docs/2016/08/consumer_engagement_in_the_energy_market_since_the_retail_market_review_-_2016_survey_findings.pdf.
- Ofgem, *Understanding Consumers' Energy Tariff Choices* (fieldwork Mar–Apr 2024), https://www.ofgem.gov.uk/sites/default/files/2025-07/understanding-consumers-energy-tariff-choices-%20research-report-2024.pdf.
- Ofgem, *Review of domestic debt objections: our decision*, 25 Jul 2016, https://www.ofgem.gov.uk/sites/default/files/docs/2016/07/decision_on_review_of_domestic_objections.pdf; *Impact assessment*, https://www.ofgem.gov.uk/sites/default/files/docs/2016/07/impact_assessment_on_review_of_domestic_objections.pdf; *Decision on review of non-domestic objections*, Jul 2016, fn 26, https://www.ofgem.gov.uk/sites/default/files/docs/2016/07/decision_on_review_of_non-domestic_objections.pdf.
- Ofgem, *CSS Service Definition* (Annex 2), Nov 2019, https://www.ofgem.gov.uk/sites/default/files/docs/2019/11/annex_2_css_service_definition_0.pdf.
- REC change R0155 (Change of Occupier): Ofgem acceptance, https://epr-2025.ofgem.gov.uk/sites/default/files/2025-04/acceptance-of-R0155-change-of-occupier%20%281%29.pdf; summary, https://bpconsulting.co.uk/the-new-change-of-occupier-coo-process/; RECCo, https://retailenergycode.co.uk/ongoing-progress-to-improve-the-change-of-tenancy-process/.
- Citizens Advice, *Moving home and dealing with your energy supply*, https://www.citizensadvice.org.uk/consumer/energy/energy-supply/moving-home-your-energy-supply/moving-home-dealing-with-your-energy-supply/; *Check if you're responsible for paying an energy bill*, https://www.citizensadvice.org.uk/consumer/energy/energy-supply/problems-with-your-energy-bill/check-if-youre-responsible-for-paying-an-energy-bill/; *Response to Ofgem's CfI*, 20 Jan 2026, https://www.citizensadvice.org.uk/policy/publications/citizens-advice-response-to-ofgems-call-for-input-on-tackling-debt-in-the/.
- Money Advice Trust, *Response to Ofgem: Tackling energy debt in the supplier home moves process*, 20 Jan 2026, https://moneyadvicetrust.org/wp-content/uploads/2026/01/Money-Advice-Trust-response-to-Ofgem-Tackling-energy-debt-in-home-moves-consultation-paper.pdf.
- CMA, *Energy Market Investigation Final Report*, 2016, Tables 8.5–8.6, §8.160–8.161 (via `docs/market_research/continuous_behavioural_engagement_w2_14.md` §2c).
