# Home moves: change of tenancy, change of occupier, and what a GB supplier sees of them

**Knowledge:** home-moves

*Written 2026-10-05 as step-1 knowledge work under `docs/staging/DIRECTOR_CANON_THE_PRIORITY_ORDER_2026-10-05.md`
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
  It is sound in shape but has no move-out stream to feed it.

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
8. The statutory or licence locus of the two-day liability rule, the 6-week final bill and the
   10-working-day refund.
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
- G6. There is no move observable at the seam, and no mover retention proposition.

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

## Sources

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
