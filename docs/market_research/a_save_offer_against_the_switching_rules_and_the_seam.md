# Can a GB supplier make a save offer to a household that is leaving, and would it see the leaving in time?

**Knowledge:** acquisition-and-retention-economics

**Read 2026-10-08** for the director's open row `b8-no-uniform-renewal-cut-from-2`
(`docs/direction/DIRECTION.yaml`, `for_the_director`), claim
`b8-a-save-offer-is-sourced-against-the-switching-rules-and-the-seam`. This answers only the
factual half. It does not build the save-offer decision set; whether to build it is his decision.

His question, verbatim: *"Real retention offers are, as far as I know, SAVE offers made to a customer
who has started to leave, not blanket renewal discounts. Is that how a GB supplier actually does it,
and does it see the leaving signal (a switch notification) in time to make one?"*

## 0. The answer in five lines

1. **When the loser hears.** Under CSS (from 18 July 2022) the losing supplier gets an *Invitation to
   Intervene* when the switch request goes Pending. The effective date must be **at least one complete
   working day and at most 28 days** after the request. So the notice comes 1 working day to 28 days
   ahead. The typical lead time is **not established**.
2. **May it make an offer on that notice?** **Yes. Nothing read forbids contacting the household or
   making an offer.** It may **not block the switch** on the strength of a save. A domestic objection is
   allowed only for outstanding charges, or where the household says it never signed with the new
   supplier (SLC 14.4). Ofgem's 2007 policy shut the "re-contract in the objection window, then object"
   route. So a save works only if the household cancels with the gaining supplier itself, or comes back
   after the switch.
3. **What price may a save carry (from 14 April 2022)?** Only a **fixed-term retention tariff**, under
   the SLC 22B market-wide derogation. A price offered only to existing customers is otherwise barred
   by SLC 22B.1.
4. **What industry does.** Both shapes are on the record. Targeted win-back after a loss is documented
   (British Gas, 2012, a staff member's account; London Electricity, 2003). Proactive retention tariffs
   for existing customers whose fixed terms are ending are, in Ofgem's own 2025 words, the instrument the
   derogation exists for. **In the published record the regulated main channel is targeted
   retention at the end of the term, not a reactive save.** No source gives the share of leavers who get
   a save, or how many accept one. *(Corrected 2026-10-08: the switching process's own 2016 data bound
   it, pre-CSS, at about 0–4% of domestic switches, with 0.4–1.3% stopped through the losing supplier
   (§5).)*
5. **The seam.** The company is told of a loss only at **17:00 the day before the switch takes
   effect**, once the switch can no longer be cancelled. No decision reads that notice. The world has
   no submission date, no cancellable in-flight switch and no household answer to a save. **So
   the company sees no leaving signal before the loss, and a save could not change the outcome here.**
   *(Corrected 2026-10-08: the CSS Invitation to Intervene now crosses at the ASAP floor, one
   working day or so before Secured Inactive (§1b). It is filed, nothing reads it, and the world still
   has no household answer to a save.)*

---

## 1. The switching rules: when the loser learns, and what it may do

### 1a. Sources read this pass (fetched and extracted 2026-10-08, not recalled)

| # | source | read |
|---|---|---|
| R1 | Ofgem, *Electricity Supply Standard Licence Conditions, consolidated to 1 August 2025* (611 pp; ofgem.gov.uk/sites/default/files/2023-03/Electricity Supply Standard Consolidated Licence Conditions - Current.pdf) | SLC 14 in full, SLC 14A in full, SLC 22B in full |
| R2 | Ofgem, *REC Schedule — Registration Services*, updated draft published for transparency, Spring 2021 consultation (ofgem.gov.uk/sites/default/files/docs/2021/03/rec_schedule_-_registration_services_210323_for_consultation.pdf) | paras 2.6, 6.1–6.2, 7.1.8–7.1.10, 12.1 |
| R3 | REC Schedule 23 *Registration Services* v2.2, effective 27 Feb 2026, as extracted 2026-10-03 into `interface/contracts/registration_loss_seam.py` and `company/market/transfer_objection_register.py` | paras 1.4(d), 6.2, 7.1.9, 13.4 |
| R4 | Ofgem, letter of 17 April 2007 on re-contracting during the objection period (ofgem.gov.uk/sites/default/files/docs/2007/04/objections-consultation-letter-170407.pdf) | paras 2–14 |
| R5 | Ofgem, letter of July 2007 *Modifying the arrangements for the use of objections in the non-domestic market* (ofgem.gov.uk/sites/default/files/docs/2007/07/non-domestic-objections.pdf) | the proposal and its reasoning |
| R6 | Ofgem, *Market-wide derogation from SLC 22B for Fixed Retention Tariffs*, decision and Directions, 3 February 2023 (ofgem.gov.uk/sites/default/files/2023-02/Market-wide derogation (ELEC AND GAS).pdf) | the Direction text, paras 3, 6, 7 |
| R7 | Ofgem, *Decision Renewing the Ban on Acquisition-only Tariffs (BAT) after March 2026*, November 2025 (ofgem.gov.uk/sites/default/files/2025-11/Final_BAT_Renewal_Decision_Document,_November_2025.pdf) | §3 |
| R8 | Ofgem, *Supplier Guaranteed Standards of Performance for Switching: GS 6ZA amendment*, decision letter, Feb 2024 (ofgem.gov.uk/sites/default/files/2024-02/Switching GSoP 6ZA amendment - decision letter.pdf); DCC, *Price Control 2023: CRS performance report*, 31 Jul 2023 (smartdcc.co.uk/media/qmmf3u4t/central-registration-service.pdf); Energy UK, *Switching report November 2025* | read in full for submission-to-effective-date timings; none found (§1b) |
| R9 | MoneySavingExpert help, *How long does it take to switch energy suppliers?*, 17 Sep 2025; Octopus Energy, *Switching energy suppliers just got faster and easier*, 4 Aug 2022, and *How switching works*, 11 Dec 2019 | the timing choices and one gainer's stated default (§1b) |

R1 carries Ofgem's own caveat: *"Consolidated conditions are not formal Public Register documents
and should not be relied on."* R2 is a 2021 consultation draft. On every paragraph this note quotes,
it agrees with R3, the in-force v2.2 extracted on 2026-10-03. This pass could not re-fetch R3: the
REC portal now serves an HTML page in place of the PDF. **Only the 28-day upper bound (R2 para 2.6)
is read from the draft alone**, so it should be re-read against v2.2 before anything depends on it.

### 1b. When the losing supplier learns of a switch (CSS, from 18 July 2022)

The sequence for a domestic premises:

| moment | what the losing supplier receives | source |
|---|---|---|
| the gaining supplier submits the Switch Request; it validates and goes **Pending** | an *Invitation to Intervene*, issued "at the same time as" the Pending notification | R2 7.1.8–7.1.9; R3 7.1.9 |
| 17:00 on the **1st working day** after submission | the Objection Window closes | R2 6.2(a); R3 6.2(a) |
| 17:00 on the **day before** the Supply Effective From Date | the cancellation deadline passes; the loser's registration becomes **Secured Inactive** and it is told so | R2 12.1; R3 1.4(d), 13.4 |
| the Supply Effective From Date | the switch takes effect | |

**The lead time is set by the gaining supplier, within bounds.** The proposed effective date must be
*"no more than 28 days after (but not including) the day on which the Switch Request is submitted;
and … in the case of a Domestic Premises … at least one complete Working Day (starting at midnight)
after the day on which the Switch Request is submitted"* (R2 2.6).

What fixes when the gainer submits is the licence. It must complete the transfer *"within five Working
Days of the Relevant Date"* (R1 SLC 14A.1). For a domestic household that has not asked to start
inside its cooling-off period, it must do so within five working days of the earlier of the cooling-off
expiry and *"the period of 14 days from entering into the Contract"* (R1 14A.3(f), 14A.4A). **So a
domestic switch usually takes effect about 14 days plus up to 5 working days after sign-up.** The
loser hears when the request is submitted, at some point in that span, no later than one working day
before the effective date.

**NOT ESTABLISHED: the distribution of that lead time.** Neither the licence nor the REC says when in
the window the gainer submits. Whether a typical domestic loser hears inside the household's cooling-off
period (so the household can still cancel for free) or after it is not published. The one practitioner
account (§2a) says that before CSS, British Gas was "notified of the switch after the cool off period
has passed".

**Re-searched 2026-10-08 for the distribution itself, and it is still not established.** Read for it:
Ofgem's GSoP 6ZA amendment decision letter (Feb 2024: the guaranteed standard cut from 15 to 5
working days, no timing data); DCC's *CRS performance report* (July 2023: delivery milestones and
margin, no switch timings); the Energy UK monthly switching report (Nov 2025: counts only); Ofgem's
*Average switching time for domestic customers* chart (now 404; its series is recorded as ending
September 2022, and it measures sign-up to switch, not submission to effective date, so it would not
answer this even if read). No RECCo or ElectraLink publication of submission-to-effective-date timings
was found. What the record does give is the **shape of the choice**, not its weights:

- **The household chooses among three timings** (MoneySavingExpert, 17 Sep 2025): *"ASAP"*, which the
  gainer must complete within five working days; *after the cooling-off period*; or *"a chosen date up
  to four weeks later. Not all providers offer this."*
- **One large gainer's stated default is ASAP.** Octopus, 4 Aug 2022: *"Domestic customers in 2 working
  days"* … *"You still have a 14 day cooling off period, regardless of your start date"*. Its pre-CSS
  page (11 Dec 2019) said *"usually 17 days after you sign up"*. That is one supplier's policy, not a
  market share.

**What that bounds, and what it does not.** If ASAP is the common route, the gainer submits at or
near sign-up and the loser's Pending notice arrives about **1 to 4 working days** before the effective
date, that is, only days before the Secured Inactive notice this world already sends. If after-cooling-
off is common, it arrives up to about 14 days earlier than that. The share of each route is not
published, so the distribution is **not established**
(`assumption_toggles.yaml::q4_css_switch_route_share_asap`, null). The question that would settle it
is a practitioner one: *of a supplier's domestic gains under CSS, what share are ASAP, after cooling
off, and dated later?* It is asked in the director's row `the-save-offer-needs-two-practitioner-figures`.

**What is built meanwhile: the ASAP floor (director's direction, 2026-10-08).** The world now sends
the Invitation to Intervene for every CSS switch, dated at the latest submission the rules allow:
the day before the last working day before the effective date, so one complete working day lies
between (`registration_loss_seam.latest_submission_date`). It is observed at the end of that day. For
a Wednesday switch that is the start of Tuesday, 17 hours before Secured Inactive; for a Monday
switch, the start of Friday. That is the least warning any route gives, so no save the company later wins is
flattered by warning a real loser would not have had. Bank holidays are counted as working days,
which can only shorten the warning. The toggle's reader refuses a set share until the other two
routes have a submission date.

**Before CSS (the 2016 – 17 July 2022 part of our window)**, electricity losses were notified by MPAS
under the MRA (the D0058 flow), with an objection window of *"five working days"*. Gas losses came
through UK Link under the UNC, with *"seven business days"* (R4 footnote 1; R5 footnote 2; both 2007).
Whether those windows held through 2016–2022 is not re-read here. The seam already carries pre-CSS
timing as a named gap (`registration_loss_seam.GAPS["pre_css_timing"]`).

### 1c. Whether it may make a save offer on that notice

**Contacting the household and making an offer: no prohibition found.** Neither SLC 14 nor SLC 14A
restricts what a losing supplier says to its customer. Ofgem's 2007 letter records the industry's
view and its own: *"it is widely accepted regarding the terms of the MRA, that a supplier may
re-contract during the objection period in circumstances where it has been alerted to the customer's
intention to switch by the customer himself"*. On the loss data itself it says: *"There are no
obstacles to suppliers doing what they think is necessary to help them manage their relationships
with their customers in this way. In our view, the real issue raised by the appeal is less to do with
the use of the loss notification data"* (R4 paras 9, 13). The 2007 appeal had found that British Gas
Trading *"could reasonably believe"* the MRA let it use the loss notification to re-contract (R4 para 4).
**Whether the REC, which replaced the MRA, has a data-use clause on the Invitation to Intervene was not
found. It is NOT ESTABLISHED, not established-absent.**

**Using a save to stop the switch: not allowed.** For a domestic customer the licence permits an
objection in only two cases (R1 SLC 14.4). Paragraphs (b), (d) and (e) are all "(not used)":

> **14.4(a)** — "if at the time the request is made Outstanding Charges are due to the licensee from
> that Domestic Customer" (limited by 14.5 and 14.7: not for an assignable prepayment debt, not for a
> wholly disputed or supplier-error amount);
>
> **14.4(c)** — "the customer informs the licensee that he has not entered into a Contract with the
> proposed new Electricity Supplier and asks the licensee to prevent the Proposed Supplier Transfer".

A domestic save offer accepted on the phone creates neither ground. 14.4(c) covers a household that
never signed with the gainer, not one that signed and changed its mind. For non-domestic customers the
contract ground exists, but it is pinned to the contract in force *"at the time the licensee receives
Notice"* of the switch (R1 14.2(a)). That wording carries out Ofgem's 2007 policy against
re-contracting to object (R5):

> "The objection window was not intended to be used for commercial negotiation to allow the outgoing
> supplier to retain the customer. … we do think that suppliers should not re-contract, or in any other
> way alter their commercial position towards the customer during the objection window in order to
> prevent a transfer that would otherwise have gone ahead."

R5 also says the household's route back is a second switch: *"If the customer subsequently changes
their mind or the outgoing supplier wants to make a new offer, the customer may be able to switch
supplier again once the existing transfer has been completed."*

**So a save made on the notice can work in only two ways, and in both the household acts:**

- **It cancels with the gaining supplier inside the cooling-off period.** The gainer must then *"take
  all reasonable steps to prevent a Supplier Transfer from having effect"* (R1 14A.13). If it fails, it
  must keep supplying on the old terms with no termination fee (14A.14). A household returning this way
  must be offered an *Equivalent Terms Contract* by the old supplier for at least 16 working days
  (14A.18–19). That is a duty on the loser, not a save price.
- **It lets the switch complete and switches back.** That is a win-back, not a save. It is
  re-acquisition, with whatever acquisition costs apply.

### 1d. What price a save may carry: SLC 22B, from 14 April 2022

> **SLC 22B.1** — "the licensee must ensure that all its Tariffs are available to, and are capable of
> being entered into by, both new and existing Domestic Customers." The exception at **22B.2(d)** is for
> tariffs offered to a group defined by criteria that "do not in any way relate to whether or not the
> Domestic Customer is a new or existing Domestic Customer" (R1).

"A household that has started to leave us" is a criterion about being an existing customer. Without
a derogation, a price offered only to leavers would be barred. The derogation (R6, a Direction under
22B.3) lifts 22B.1 for **"Fixed Retention Tariffs"**:

> "domestic, tariffs of fixed term duration, which are only available to Existing Customers with the
> aim of retaining the loyalty of those customers" — where "Existing Customers" are "Domestic Customers
> that already have a Contract or Deemed Contract with the Licensee". The licensee must notify the
> Authority, in advance or within 5 days, that it relies on it (R6 paras 3, 7).

The BAT and the derogation run to **31 March 2027** (R7).

**Correction to the knowledge map, made beside its claim.** The row *Retention offers (SLC 22B)* in
`docs/institutional/knowledge_map.md` says the derogation is "keyed to *end of fixed term*" and "does
not reach an SVT household". **The Direction's text has no end-of-term condition.** It requires a
fixed-term tariff, existing customers and a retention aim, and nothing more. The end-of-term framing is
Ofgem's description of how the derogation is used: *"Suppliers are currently permitted to offer
exclusive 'retention-only' tariffs to their existing customers nearing the end of fixed-term contracts
via a Market-wide Derogation"* (R7 §3(i)). In R7 §3.7 suppliers asked Ofgem for *"clarity on the types
of deals and customers that are eligible for these tariffs"*. **So whether a fixed retention tariff
offered to an SVT household, or to a household mid-switch, sits inside the derogation is NOT
ESTABLISHED. Read literally, the text allows it, and the regulator's account of use does not
describe it.** A save priced as a *variable* discount has no derogation and must be open to new
customers too.

**Before 14 April 2022** there was no BAT. The 2014–2017 Retail Market Review tariff rules
(`next_best_action_and_cross_sell.md` line 340 names their ban on most discounts) were **not re-read in
this pass**. What a save could carry in 2016–2017 is NOT ESTABLISHED here. Whether a cash credit (as in
§2a) counts as a "Tariff" under 22B is also NOT ESTABLISHED.

---

## 2. Practitioner record: save offers, blanket renewal discounts, and who gets them

### 2a. What was found

| shape | evidence | to whom | grade |
|---|---|---|---|
| **Reactive win-back after the loss notice**, domestic | MSE forum thread *"Inducements to stay – one for the reps"*, 17 Nov 2012. Poster TIMMY85, stating they work for British Gas and post personally: "BG are notified of the switch after the cool off period has passed. This will then trigger a 'sorry you are leaving us' letter/email asking the customer to call". Winback agents "may offer a credit after a period of time if the customer returns", which may require staying on the tariff signed up for. The poster says it is not offered to every leaver (their spouse was not contacted). Another forumite claims winbacks got "£200 on top of their tariff". | **targeted**: leavers, selectively | one practitioner's word, unverified, pre-CSS. The £200 is an unsourced claim. |
| **Reactive re-contract on the loss notice**, non-domestic, pre-2007 | R4 para 2 describes the practice: on receiving the D0058 "there is an opportunity within the period allowed … for the existing supplier to contact the customer and offer to enter into a new contract", then object on the new contract. BizzEnergy's 2007 response: "The existing supplier acts on the loss notification flow by contacting the customer." | **targeted**: leavers | regulator-documented. **Its blocking leg was closed** (§1c). |
| **Win-back to past customers** | Ofgem, Competition Act decision, 12 Sept 2003: London Electricity offered domestic customers who had switched away "up to £75 over one year" in vouchers. Found not to infringe s.18. | **targeted**: former customers | regulator-documented |
| **Retention-only fixed tariffs for existing customers whose fixed terms are ending** | R7 §3(i)–(ii): "by allowing suppliers to offer tailored retention deals, we expect customers nearing contract end to benefit from lower priced tariffs"; all eight responding suppliers backed keeping it (§3.5). R7 §3.3: Ofgem had "not seen any substantial evidence to date of the Market-wide Derogation's impact on pricing and tariffs". | **targeted by timing**: existing customers at the end of a term, before any leaving signal | regulator-documented, 2022 onward |
| **Blanket loyalty reward for fixing** | MoneySavingExpert, 26 July 2017: Co-op Energy offered **all** existing Co-op and GB Energy customers up to £150 (dual fuel) or £75 (single) to move to named fixes by 31 July 2017, paid after a year. MSE judged many would still save more by switching. | **blanket**: the whole book | press report of a live offer |
| **Retention for home movers** | BFY Group case study, 1 Sept 2023, unnamed "large energy supplier": retention of customers moving in or out of a property raised from ~5% to ~30% through journey, communications and training changes, with "~£25m" a year of benefit opportunity. No offer price is stated. | **targeted**: a life event | consultancy marketing, unnamed client |
| Industry-level verdict | Utility Week, 15 Sept 2017, Gavriel Hollander: *"Suppliers not fighting to retain switching customers"* | — | **headline only**: the article is paywalled and was not read |

### 2b. What this says about his question

- **Both his frame and ours are on the record.** Reactive saves and win-backs on the loss notice exist
  in documented practice. So do proactive retention offers. In the 2022–2025 part of the window, the
  proactive offer is the one the regulator wrote a rule for, defended, and described as "tailored". It
  is made to existing customers *nearing contract end*, before they have shown any sign of leaving.
- **"Blanket renewal discount" describes neither well.** The Co-op 2017 case is blanket. The
  derogation's retention tariff is **targeted by timing** (term end) and may be targeted further by
  whatever the supplier chooses. 22B constrains *who may be offered a price* by new versus existing
  status only. Our B8 decision prices a uniform cut for every renewal. Real practice, as far as the
  record goes, sits **between** a blanket cut and a reactive save.
- *Corrected 2026-10-08 (§5): this pass missed the switching process's own data. Ofgem's 2016 RFI
  bounds customer-initiated stops at 0.4–1.3% of domestic switches through the losing supplier and
  ≈2.8% through the gainer (§5c), and repeat switching bounds win-back (§5d). What follows is still
  true of the save share within those bounds.*
- **NOT ESTABLISHED, and no source found:** the share of leavers who get a save or win-back contact;
  the acceptance rate; how deep offers are; whether GB domestic retention desks today act on the CSS
  Invitation to Intervene at all. The knowledge map already lists "how deep real retention offers are"
  as unpublished. **This is the "too obvious to write down" kind of fact that CLAUDE.md sends to the
  director as the practitioner. His own trade knowledge is the best evidence available on how common
  reactive saves are.**

---

## 3. The seam: does the company see a leaving signal before the loss?

Read from `company/interfaces/sim_interface.py`, `interface/contracts/registration_loss_seam.py`,
`simulation/registration_loss_feed.py`, `simulation/run_phase2b.py` and `company/crm/cos_process.py` at
`bad869939`.

**What crosses, and when.** At every site that adds a household to `churned_billing_accounts`, the run
calls `_notify_registration_loss(billing_account, term_start_str)` (`run_phase2b.py` ~2152, 2679, 3301).
That sends one wire notice per supply point to the company's `CoSRegister`. The notice is the CSS
*Registration Secured Inactive Notification*. Its `observed_at` is `secured_active_at(SEFD)`, which is
17:00 on the day before the effective date. Before CSS it is midnight on the effective date
(`loss_notice_observed_at`). It carries only the point and the date. `FORBIDDEN_TRUTH_FIELDS` keeps the
reason, the gainer's price and the world's probability off it.

**What the company does with it: files it.** `CoSRegister.receive_loss_wire` opens a process at
`OBJECTION_CLEARED`, and the run reports `losses_notified()` and `loss_exceptions()` in its output.
**No pricing, retention or decision module reads it.** `SimInterface.notify_churn` is declared on the
seam, but outside tests its only caller is `RecordedSimInterface`, which forwards it. The B8 holdout
rows (`HOLDOUT_OBSERVABLE_FIELDS`) give the company `stayed` as an outcome, after the decision.

**Why no save is possible in this world, which is three things and not one:**

1. **The signal arrives too late.** The one notice that crosses is sent at the moment the switch can
   no longer be cancelled (R3 1.4(d)). It is a loss notice, not a leaving signal.
2. **The earlier signal is not emitted because the world has nothing to emit it from.** The seam's own
   docstring names this: the Invitation to Intervene at Pending (R3 7.1.9) and the objection window
   *"cannot be emitted without inventing it"*, because *"the world has no submission date and no failed
   switch"*. A departure is decided by one roll at the term boundary
   (`docs/design/EP12_CSS_REC_SWITCHING_DISCOVER_FRAME.md` §2: *"The exit is instantaneous and
   irreversible. It has no in-flight period, no gaining counterparty, no objection window, no
   reversal"*).
   *(Corrected 2026-10-08: a submission date is now set at the ASAP floor and the Invitation to
   Intervene crosses for every CSS switch (§1b). A failed switch is still not emitted.)*
3. **There is no household answer to a save.** Even with an earlier notice, nothing in the world lets a
   household that has signed with a gainer cancel in cooling-off because its old supplier made an
   offer. The only stay-or-go answer the world gives is the renewal-time roll.

**What a real supplier would see**, from §1–§2:

| signal | when | in this world |
|---|---|---|
| CSS Invitation to Intervene (switch Pending) | 1 working day to 28 days before the effective date (from Jul 2022) | **present at the ASAP floor** (2026-10-08): dated at the latest submission the rules allow, filed in `pending_switches_notified()`; nothing reads it. The route share is not published (§1b) |
| Pre-CSS loss notice (D0058 / UK Link) | before the effective date, with a 5 working day (elec) or 7 business day (gas) objection window, per 2007 sources | **absent**: pre-CSS timing is a named gap; the notice is stamped at midnight on the effective date |
| Secured Inactive (cannot be cancelled now) | 17:00 the day before the effective date | **present**, and filed; nothing reads it |
| The household calls to leave or asks for an exit quote | any time | **absent**: the world has no such contact |
| Silence at the renewal window (no response to the renewal notice) | the weeks before term end | not assessed in this pass |

---

## 4. What this means for his row, stated as evidence and not as a decision

- **"Is that how a GB supplier actually does it?"** Partly. Reactive saves and win-backs are on the
  record. They are lawful as offers, they cannot block a switch, and from April 2022 they are
  price-limited to fixed retention tariffs. The regulator's account of 2022–2025 practice is a
  **retention tariff targeted at term end**, which is our renewal frame made *targeted* rather than
  uniform. How common reactive saves are is not published.
- **"Does it see the leaving signal in time?"** In reality, yes, 1 working day to 28 days ahead under
  CSS. A save then only works if the household cancels with the gainer, which is free inside cooling-off.
  **In this world, no.** The only notice crosses after the switch can no longer be cancelled, and the
  world has no in-flight switch or household answer that a save could change. Grading a save-offer
  decision set here would need world build first: a submission date, a cooling-off cancellation path
  and a response to a save. All three would have to come from published rates, and those are not
  established.
- **His proposal's "if blanket renewal offers are real practice" branch** is the closer match to the
  regulated 2022–2025 instrument, if "blanket" is read as *offered at renewal* and the offer is allowed
  to be *targeted by who is renewing*. The slope he is already sourcing
  (`retention_slope_per_pound_of_renewal_cut.md`) is needed under either reading.

---

## 5. The switching-outcomes family: how often a started switch does not end as a plain switch

**Read 2026-10-08** on the director's instruction of the same day: *"Your research missed the obvious
source: the switching process's own data. A save is a switch cancelled during or after cooling-off, a
win-back is a switch-back soon after a loss, and both sit alongside cancellations, rejections,
objections, withdrawals, annulments, erroneous transfers and disputes."* He is right. The Switching
Programme's own impact assessments carry a 2016 measurement of most of this family, from a January 2017
Request for Information to suppliers. §2b said no source gives the share of leavers who are saved. That
was too strong: a ceiling and the nearest proxy are published (§5c). The share itself is still not.

### 5a. Sources read this pass (fetched and extracted 2026-10-08, not recalled)

| # | source | what it gives |
|---|---|---|
| S1 | Ofgem, *Moving to reliable next-day switching*, consultation appendices, June 2014 (ofgem.gov.uk/sites/default/files/docs/2014/06/fast_and_reliable_switching_con_doc_-_appendicies40_0.pdf) | App. 1 paras 1.25–1.29, 1.42–1.44, fn 10–11: objection grounds and rates; causes of ETs; change-of-tenancy flag |
| S2 | Ofgem, *Delivering faster and more reliable switching: impact assessment*, Nov 2017 (…/docs/2017/11/delivering_faster_and_more_reliable_switching_impact_assessment.pdf) | paras 1.13–1.24, 4.4–4.11 and the table at 4.8: 2016 volumes of ETs, abandoned, rejected and delayed switches |
| S3 | Ofgem, *Impact assessment assumptions log*, Sept 2017 (…/docs/2017/09/impact_assessment_assumptions_log.xlsx), rows 111–146 | the rates behind S2: CRO rate, registration-withdrawal rate, abandonment, rejections |
| S4 | Ofgem Switching Programme, *Policy issue update papers: Objections* and *Customer Requested Objections* (BPD i03), 19 and 6 Sept 2017 (…/docs/2017/09/policy_update_objections.pdf) | paras 7–12 and 22–24: how CROs, withdrawals and annulments work; the RFI count of CROs |
| S5 | Ofgem, *Switching Programme: Outline Business Case*, Feb 2018 (…/docs/2018/02/switching_programme_outline_business_case_and_blueprint_phase_decision.pdf) | para 2.12: ET rate, domestic and non-domestic, 2016 |
| S6 | Ofgem, *Supplier Guaranteed Standards of Performance: approach to impact assessment*, June 2018 (…/docs/2018/06/supplier_guaranteed_standards_of_performance_approach_to_impact_assessment_on_introducing_switching_compensation_for_publn.pdf), and its IA of Nov 2018 (…/docs/2018/11/impact_assessment.pdf), Table 1 | paras 1.5, 1.8: 9% of switches delayed in 2017; ETs "steady at approximately 0.96% … since 2016" |
| S7 | Ofgem Switching Programme, *Erroneous transfers policy issues paper* (DA i13), 12 Aug 2016 (…/docs/2016/08/erroneous_transfers-policy_issue_paper.pdf) | paras 20–21: ETs ~0.5% at the six large suppliers; some recorded ETs are customers who changed their mind |
| S8 | Ofgem, *Decision on review of domestic objections* and its IA, July 2016 | read in full in `domestic_debt_objection_rates_gb.md`; the objection rows below come from there |
| S9 | ElectraLink Energy Market Insights at electralink.co.uk: *6.2 million switches in 2020* (Jan 2021); *Switching requests plummet* (Nov 2021); *91k switches in May, all-time low* (June 2022); *Switching nosedives in 2022* (Feb 2023); *Switching increases 78% in 2023* (Jan 2024) | electricity changes of supplier "started" and "completed"; MPANs switching more than once |
| S10 | Ofgem, *Results of research on unreliable switching* (qualitative, 2017) (…/docs/2017/09/consumer_research_unreliable_switching.pdf) | retention attempts during delayed switches; ET households' experience |
| S11 | Energy UK, *Energy Switch Guarantee* page (energy-uk.org.uk/our-work/energy-switch-guarantee/), read 2026-10-08 | CSS-era signatory switch-speed results only |
| S12 | Ofgem, *Centralised Registration Service decision*, Nov 2024 (…/2024-11/Centralised Registration Service Decision.pdf); DCC news, *Ofgem confirms successful switching service to stay with DCC* (smartdcc.co.uk) | CSS era: 27.5m successful switches since go-live, para 1.51 "missing registrations … erroneous, delayed, or failed switches"; no outcome rates |

**Search limits this pass.** The session's web-search budget ran out at the first query. The work was
done by fetching named documents directly and through a rate-limited search engine. Three places that
should hold CSS-era rates could not be read: the REC Portal's switching performance reports (login
only); the DCC's CSS operational reporting to REC parties (not on the public site, whose dashboard
carries smart-meter series only); and the Ofgem Retail Market Indicators page (JavaScript-rendered, as
`domestic_debt_objection_rates_gb.md` already records). Energy UK publishes only speed, final-bill and
refund percentages for the Switch Guarantee, with no outcome counts. **Where a cell below is blank, it
means "not found in what could be read", not "not published".**

### 5b. The family, one row per outcome

Unit: a domestic **meter-point switch** (a dual-fuel move counts twice), unless the row says otherwise.
The 2016 base is Ofgem's own figure of **7.76m domestic switches** (S3 row 111; S2 uses 7.7m). "Post"
means after CSS go-live on 18 July 2022.

| outcome | what it is | pre-CSS rate (year) | post-CSS rate | denominator | source |
|---|---|---|---|---|---|
| **Objection** (all grounds) | losing supplier blocks the registration in the objection window | **6% elec, 5% gas** of domestic transfers (Mar 2016); 6–7% over 2013–15. In 2014, "around 7% of domestic and 25% of non-domestic gas transfers and 14% of electricity transfers" were blocked | **GAP** | attempted transfers | S8; S1 App. 1 para 1.29 |
| ↳ debt objection | over 90% of domestic objections; blocks ~28% of indebted switchers | ~170,000 customers a year blocked (2013–15) | **GAP** | indebted domestic switch attempts | S8; `domestic_debt_objection_rates_gb.md` row 9 |
| **Customer Requested Objection (CRO)** | household tells the losing supplier it has no contract with the gainer, and the loser blocks the switch (SLC 14.4(c)) | **1.28%** of domestic switches away from a supplier, ~98,560 (2016). See the consistency flag in §5c: possibly ~0.4% | **GAP**. The one-working-day CSS window was expected to leave little time for one (S4 para 9) | domestic switches | S3 row 115; S4 para 7 |
| **Registration withdrawal** | gaining supplier withdraws its own request, both for its own errors and for **customers cooling off** | **3.2%** of domestic switches (2016). About 13% of these (range 9–15%, three suppliers sampled) stopped an ET | **GAP** | domestic switches | S3 rows 113–115 |
| **Cooling-off cancellation** | household cancels with the gainer within 14 days | not separated. Bounded above by withdrawals net of ET-prevention: **≈2.8%** of domestic switches (2016). A consumer survey found **~7% of consumers** cancelled part-way (Consumer Futures, *Switched on*, Jan 2013, as cited at S2 para 1.24; not read directly) | **GAP** | domestic switches / surveyed switchers | S3 row 115 (derived: 3.2% × 0.87); S2 para 1.24 |
| **Abandoned switch** | given up by the household or the gainer before the switch takes effect, mostly over address or meter-point mismatch | ~140,000 domestic (≈1.8%); "1.8% of gas switches and 1.9% of electricity switches" from data quality (2016). Non-domestic 7,000 | **GAP** | domestic switches | S2 paras 1.16, 4.8; S3 row 129 |
| **Rejection** | central system (MPAS or UK Link) refuses the registration | **gas 385,000** (≈5.0% of all domestic switches) and **elec 57,750** (≈0.7%) (2016). Non-domestic rejection rate 8.9% gas, 2.4% elec. "The majority are known to be down to an invalid transfer date"; 90% are re-submitted successfully (central case) | **GAP** | count over all 7.76m domestic switches (the per-fuel denominator is not given) | S2 para 4.8; S3 rows 130, 133–135, 144–145 |
| **Annulment** | losing supplier cancels a pending switch at the household's request | did not exist. It is a CSS feature, designed in 2017 as an "emergency brake" against ETs (S4 paras 22–24, option 2) | **GAP** | — | S4 |
| **Erroneous transfer (ET)** | wrong meter point switched, or a cancelled contract's switch goes ahead | **0.96%** of domestic switches, ~74,000 (2016), "steady … since 2016" (~89,000 on 2017 volumes). Non-domestic **1.5%** (5,800). The 2016 paper gave ~0.5% at the six large suppliers. ~85% are the wrong MPxN; **13% are "contract withdrawals not actioned"** | **GAP**. Ofgem forecast 25,200 fewer domestic ETs a year from CSS; that is a forecast, not a measurement | domestic switches | S5 para 2.12; S6 para 1.8; S7 para 20; S3 rows 111, 121, 122; S2 p.60 |
| ↳ ET prevented in the window | stopped by a CRO or a withdrawal before it takes effect | ~130,000 (≈1.7%) (2016) | **GAP** | domestic switches | S3 row 115 |
| **Delayed switch** | not completed within 21 days without a valid reason | ~105,000 (≈1.4%, 2016); **9%** of switches in 2017 on Ofgem's monitoring definition | Energy UK signatories completed **99.32–99.71%** of valid switches within 5 working days, Apr 2025–Mar 2026 | switches | S2 para 1.15; S6 para 1.5; S11 |
| **Started but not completed** (everything above, electricity) | a valid change of supplier raised that never completes | **≈18%**: 7.55m raised, 6.2m completed (2020); **≈16%** in 2019, derived from the same release's year-on-year percentages. ElectraLink's May 2022 forecast: 120,000 started → ~93,000 completed (≈22%) | **GAP**: "Due to the introduction of the Central Switching Service in July 2022, ElectraLink is no longer able to provide data on CoS started" | electricity MPAN changes of supplier, domestic and non-domestic, voluntary only | S9 |
| **Dispute** | a contested ET, or a complaint about the switch | **GAP**. The 2017 qualitative research found ET households "made far more calls to each of the suppliers, than the suppliers made themselves" | **GAP** | — | S10 |
| **Win-back / switch-back** | the lost household switches back to its old supplier | **GAP** for the switch-back itself. Upper bound: MPANs switching twice or more in the year, "just shy of 600,000" in 2020 against ~6.2m switches (≈10%) | 2022: "fewer than 50,000" MPANs switched more than once, of 5.62m unique MPANs. 2023: "94 percent did so only once", "consistent … with figures from previous years" (≈6% switched twice or more) | electricity MPANs that switched in the calendar year | S9 |

**Two things the table does not say.** (1) The rows overlap and do not add up. A rejected switch is
usually re-submitted and so counted again as a start. An objected switch can be retried. ElectraLink's
"started" counts every attempt. So "18% not completed" means 18% of *raised registrations*, not 18% of
*households who tried*. (2) The 2016 figures are supplier RFI returns used in an impact assessment, and
Ofgem labels several of them as its own analysis, not audited statistics.

**A correction to the director's quote of 2014, made beside the claim.** The 2014 appendix reads
"around 7% of domestic and 25% of non-domestic gas transfers and 14% of electricity transfers are
blocked". The **14% covers all electricity transfers**, domestic and non-domestic together. It is not a
domestic electricity rate. In 2016 Ofgem gave domestic electricity alone as 6%.

### 5c. Saves: the customer-initiated share after contact from the losing supplier

**What is published.** The 2016 RFI measured both routes by which a household stops a switch it
started (S3 row 115):

- **Through the losing supplier: CROs, 1.28% of domestic switches.** The 2017 objections paper describes
  how a CRO happens. On notification the loser sends a "Sorry To See You Go" letter or email, and the
  household responds by asking the loser to block the switch (S4 paras 8, 23). **This is the closest
  published measure of "customer-initiated cancellation after losing-supplier contact".** It is not a
  save rate. The licence ground is that the household *has no contract with the gainer*, and Ofgem
  counts every CRO as a *prevented erroneous transfer*. Against that, the 2014 appendix says the
  "prevent an unintended switch" ground covers a consumer who "has changed their mind" (S1 para 1.25),
  and the 2016 ET paper says some recorded ETs are customers who "switched but want to return to
  their original supplier, and both suppliers agree" (S7 para 21). How much of the 1.28% was a household
  persuaded to stay is not published.
- **Through the gaining supplier: cooling-off withdrawals, ≈2.8% of domestic switches.** This is the 3.2%
  withdrawal rate less the ~13% that prevent ETs. The cancellation goes to the gainer, so the data
  cannot show whether the losing supplier played any part.

**A consistency flag.** S4 para 7 says CROs and co-operative objections together came to "approximately
100,000 … during 2016, of which around two thirds related to non-domestic sites". S3 row 115 applies
1.28% to the *domestic* 7.7m alone and gets 98,560 domestic CROs. Both figures come from the same
January 2017 RFI, and both cannot be right. If S4 is right, domestic CROs were ~33,000, about 0.4%. **So
the CRO rate lies between 0.4% and 1.28% of domestic switches.** This pass cannot settle which.

**What the published record says about the save rate on a loss notice, pre-CSS:**

| bound | rate | what it assumes |
|---|---|---|
| floor | ~0 | every CRO is a genuine no-contract case, as Ofgem's ET accounting treats them |
| proxy | 0.4%–1.3% | every customer-initiated stop through the loser is a save |
| ceiling | ≈4.1% (≈1.3% + ≈2.8%); a survey puts all part-way cancellations at ~7% | every customer-initiated stop on either route is a save |

**Post-CSS: GAP, though the direction of pressure is known.** Under CSS the loser still hears at Pending
(§1b). But the objection window is one working day and the switch can take effect 1–5 working days
later, so the 2017 design work expected little time for a block started by the household (S4 paras 9,
15). The annulment was built for this case: the loser can cancel at the household's request up to gate
closure (S4 para 16). The cooling-off route through the gainer is unchanged: the household has 14 days,
and the gainer must try to stop the transfer (SLC 14A.13). No CSS-era rate for CROs, annulments or
withdrawals was found.

### 5d. Win-back: what bounds it

No GB source found publishes the share of lost households who switch back to the supplier they left.
ElectraLink counts repeat switching but not where the second switch goes. That makes repeat switching an
upper bound, with three other things inside it: a move on to a third supplier; an ET reversal (≈1%, which
is itself a switch back); and some SoLR and trade-sale movement. The bound was ≈10% of switching MPANs in
2020, and ≈6% in 2023, a level ElectraLink calls "consistent" with earlier years. It was <1% in 2022,
when there was nothing to switch for. The documented win-back practice is in §2a (a British Gas winback
desk in 2012; London Electricity vouchers in 2003), and neither source gives a rate.

### 5e. What this sets, and what stays a gap

- `assumption_toggles.yaml::q4_save_rate_on_loss_notice` is set from §5c as an **ESTIMATE from
  published switching-outcome data**: default 0.013, low 0.0, high 0.041. It is pre-CSS and domestic. The
  director's practitioner figure overrides it when he gives one.
- `q4_winback_rate_after_loss` is added from §5d the same way: default 0.03, low 0.01, high 0.10. The
  default is **not** a measurement. It is a point inside a published ceiling whose internal split is not
  known, and the row says so.
- `q4_save_offer_cost_share_of_annual_bill` stays null, because nothing in this family prices a save.
- **GAPS that a world build would need closed before a save could be graded here** (§3): every CSS-era
  rate in §5b; the save share within CROs and within cooling-off withdrawals; where second switches go;
  and the lead time from Pending to the effective date.

## 6. The rules a save or retention offer must meet today (read 2026-10-08)

The director asked (2026-10-08) whether SLC 22B and its retention carve-out are still in force,
and whether any other current GB rule constrains save or retention offers. Read from primary
documents on 2026-10-08:

- **SLC 22B, the ban on acquisition-only tariffs, is in force to 31 March 2027.** Ofgem, *Decision:
  Renewing the Ban on Acquisition-only Tariffs (BAT) after March 2026*, 13 November 2025
  (ofgem.gov.uk/sites/default/files/2025-11/Final_BAT_Renewal_Decision_Document,_November_2025.pdf).
  Every domestic tariff must be open to new and existing customers alike (SLC 22B.1).
- **The retention carve-out is in force with it, its text unchanged.** The Market-wide Derogation
  (Directions in force since 14 April 2022) permits **Fixed Retention Tariffs**: domestic,
  fixed-term, open only to existing customers, "with the aim of retaining the loyalty of those
  customers". The supplier must notify Ofgem it relies on it. **So a save offer must take the form
  of a fixed retention tariff, not an ad hoc discount on a variable tariff.** Ofgem's stated
  reason runs against cross-subsidy: without the derogation "acquisition costs [would be] spread
  across all tariffs", and it expects "cheaper deals for vulnerable or indebted customers".
- **A permanent ban is a separate workstream.** Its statutory consultation was unpublished at the
  November 2025 decision. **GAP:** whether it has landed since.
- **The Market Stabilisation Charge** (April 2022) was removed in April 2024.
- **SLC 14/14A objections** limit a losing supplier's grounds (debt, Customer Requested Objection,
  related meters). A save is not a ground to object (§1 above).
- **SLC 0, the Standards of Conduct,** require fair treatment and particular care for vulnerable
  customers.
- **SLC 27** requires payment-method cost-reflectivity.
- **SLC 28AD** (the price cap) reaches default and deemed contracts only, not a chosen fixed
  retention tariff.
- **The DMCC Act 2024,** in force 6 April 2025 with direct CMA enforcement, reaches the offer's
  script and price presentation: Schedule 20 para 7 bans false urgency or limited-time claims, and
  s.230 bans drip pricing.
- **No rule forbids paying for saves out of stayers' prices.** The director's own condition
  (2026-10-08) is stricter: a save offer must never be paid for by raising the price of customers
  who stay. **GAP:** the Energy Switch Guarantee's text on post-loss-notice contact (both candidate
  URLs returned 404).

**Bottom line.** A save offer on a loss notice is lawful as a Fixed Retention Tariff notified under
the derogation, without false urgency. The director has ruled that it may vary by acquisition
route or time on the default tariff, that renewal prices may not, and that stayers must not pay
for it. A retention fix offered near term end is the derogation's own named case.

---

## 7. The size of a save: what is published, and what the build chose (2026-10-11)

Read on the director's instruction after `afd818b22` built `company/crm/save_offer.py::price_match_save_rate`:
*"is 'match the market's best published deal' grounded in the save-offer page? If not, add the
reasoning and evidence, or say it's a design choice with no published basis."*

### 7a. Rules on a retention tariff's price

**NOT ESTABLISHED.** SLC 22B's market-wide derogation (§1d, §6 above; R6) sets *who* a Fixed
Retention Tariff may be sold to (existing customers, fixed term, a retention aim) and a notification
duty. It names no price formula, no floor, no ceiling and no reference price. Ofgem's own November
2025 renewal decision says the same from the other side: *"we have not seen any substantial evidence
to date of the Market-wide Derogation's impact on pricing and tariffs"* (R7 §3.3) — the regulator does
not itself monitor how deep a retention tariff runs. **ESTABLISHED: a retention tariff's depth is
unregulated.** Re-read for this pass: R6, R7 (both already in §1d/§6); no new Ofgem text on retention
pricing was found.

### 7b. Published practice and evidence on how saves are sized

| finding | shape | source, date | energy or analogous |
|---|---|---|---|
| Retention tariffs (actively renegotiated) priced **25–36% below rollover tariffs for electricity, 25–28% for gas**, and 66–116% below deemed tariffs, 2012–2014, Six Large Energy Firms + independents | a discount off the **supplier's own default/rollover tariff**, not a competitor's price | CMA, *Energy Market Investigation, final report, Summary*, 23 Jun 2016, §279 (gov.uk/cma-cases/energy-market-investigation; fetched 2026-10-11) | **energy**, microbusiness, not domestic |
| The domestic AEC's detriment is sized as the gap between the actual (SVT/default) price and a **competitive benchmark price**, not a named rival's tariff | a benchmark-gap framing, same shape as a price match in spirit, never applied to a save offer | CMA, same report, §124–§280 (detriment methodology) | **energy**, domestic, context only — this prices the *market failure*, not a *remedy a supplier chooses to offer* |
| A reactive win-back credit of **"£200 on top of their tariff"**, British Gas, pre-CSS | a flat cash add-on, not a rate cut, not sized against any published reference | MSE forum, 17 Nov 2012 (already §2a) | energy, domestic, one unsourced practitioner claim |
| CMA/Citizens Advice "loyalty penalty" work (cash savings, mortgages, insurance, mobile, broadband) quantifies a **total loyalty penalty of ~£4bn/yr** across those five markets and recommends disclosure duties | names the detriment, not a save-offer sizing rule; no "save desk" pricing formula found | CMA, *CMA tackles loyalty penalty charges*, 19 Dec 2018 (gov.uk/government/news/cma-tackles-loyalty-penalty-charges; fetched 2026-10-11) | analogous, **not energy** — and does not reach retention-offer sizing even there |
| Ofcom's "best tariff"/end-of-contract notification remedy, telecoms (expected to require disclosing the provider's own best deals to out-of-contract customers) | would be the closest analogous price-match-style rule if confirmed | **not retrieved this pass** — `ofcom.org.uk` pages probed returned 404; not re-tried past one attempt per source | analogous, candidate only |
| Which?/Citizens Advice "haggling with your energy supplier" consumer guidance | would speak directly to what a household can extract informally | **not retrieved this pass** — both probed pages returned 404 (page moved/paywalled); not found in what could be read | energy, candidate only |

### 7c. GAPs, labelled

- **GAP — no GB source, energy or analogous, prescribes pricing a save/retention offer as a match to
  a *specific competitor's* published price.** The nearest published shape (CMA §279) discounts off
  the supplier's *own* default, not off the market's cheapest deal.
- **GAP — the telecoms "best tariff"/end-of-contract analogy was not retrieved this pass.** The
  Ofcom and Which?/Citizens Advice pages probed were 404 or paywalled; this is "not found in what
  could be read," not "not published" (per the existing doc's own convention, §5a). Re-attempting
  with a different URL or a cached copy is a cheap next step, not yet done.

### 7d. What the build chose and why

**A DESIGN CHOICE WITH NO PUBLISHED BASIS**, for the specific mechanism `price_match_save_rate`
implements: matching the market's best published deal (default x (1 − Ofgem's published best-deal
gap share), floored at the company's own cost). No rule or documented practice found in §7a–§7b
prices a save this way. The two things grounded in the published record are narrower than the
mechanism: (i) that a retention tariff may legally be priced below the default at all (SLC 22B's
derogation, §1d) and (ii) that real retention tariffs, where measured, do run materially below the
default (CMA's 25–36%/25–28% figures, §7b) — but as a discount off the supplier's *own* tariff, not
as a match to a *named rival's* price. **Correction to the knowledge map's adjacent claim, made
beside it:** `cheapest_fix_against_the_default_tariff_gb_2016_2025.md` establishes the *size of the
gap* the build matches (H confidence, Ofgem's own series) but that document answers "how far below
the default was the market's cheapest deal", not "is matching that gap how a save should be sized" —
the two questions were conflated in the build's docstring reasoning and should not be.

**The practitioner reasoning for the choice, stated as such and not as a finding:** a household on a
loss notice is, by construction, leaving for something cheaper; matching the gap to the cheapest deal
on the market is the smallest move that answers the reason given, and the cost floor stops that move
from being a guaranteed loss. This is sound commercial logic and is the reasoning a retention desk
would plausibly use — but it is the discovery agent's and the build's inference, not a sourced
industry norm, and §7a–§7b found nothing that confirms or contradicts it directly.

**What alternative sizes the evidence would allow**, ranked by how directly they are supported:
1. **A fixed discount off the company's own default** (CMA's 25–36%/25–28% precedent, §7b) — the
   best-evidenced shape, though it is a microbusiness, 2012–14 figure, not domestic or current.
   2. **The company's own cheapest generally-available tariff** (distinct from price-matching a named
   competitor; nothing found rules this in or out).
3. **No standing size at all**, leaving `cut_share` at `None` until a practitioner figure is given —
   the position `save_offer.py`'s own docstring held before `afd818b22`, and the one the §2b/§5e GAPs
   in this document already support most directly.

**Action warranted:** keep `price_match_save_rate` as a labelled design choice in the code's own
docstring (it already is, partially) rather than as a grounded rule, and route the open question —
whether GB retention desks price-match a named rival or discount off their own book — to the
director as a practitioner question per `the-save-offer-needs-two-practitioner-figures`, alongside
the telecoms analogy gap in §7c.

## 8. When the renewal already sits at its cost floor: one margin, two claims on it (2026-10-14)

Written first under K8 for next week's P1. On fresh seeds the save never fires, because 21 of 28
held renewals already sit at the company's own cost floor to the penny (82e84e4a4). The renewal
cut stays on risk tiers (d5ba38b12). This section says what is settled, what our code does, and
what nobody has published, before any design changes.

### 8a. What the rules settle

- **No licence floor under a domestic fixed tariff.** The default tariff cap is a ceiling on
  default products. SLC 22B's market-wide derogation sets who a fixed retention tariff may be sold
  to, not its price (§7a). **ESTABLISHED: a retention price below cost is lawful.**
- **SLC 4B (Financial Responsibility Principle)** is about risk and capital: managing the costs that
  would be mutualised if the supplier failed. It does not forbid a below-cost tariff. It makes
  plain who pays if a supplier makes a habit of one (knowledge topic acquisition-and-retention-economics,
  quoting ofgem_licence_readiness.md §1).
- So the floor is **the supplier's own rule**, and this one states it once: an undercut "may cost
  margin, it may never force a sale below cost" (company/pricing/renewal_desk.py, the through-cost
  floor).

### 8b. What our code does (discovery, not evidence about the market)

*Re-framed before landing by `SEAT_FINDING_RENEWALS_SIT_AT_THEIR_COST_FLOOR_BECAUSE_THE_FLOOR_CARRIES_THE_STANDING_CHARGES_NETWORK_..._2026-10-14.md`
(d30dafffe, 05:45 today). My first draft said that the price the desk meets sits below what it
costs us to serve the household. That finding shows the reverse: **the floor overstates the cost.***

- Writer 1, the renewal re-fix, meets the market and is clamped up to the term's cost floor. On
  all four fresh seeds, 21 of 21 held electricity renewals sit there to the penny.
- **The floor counts cost the standing charge already recovers.** The electricity floor is forward +
  policy + network, with the whole network allowance charged per MWh. Ofgem's cap construction puts
  only the per-kWh share of network cost in the unit rate. The fixed share is recovered once,
  through the standing charge (about GBP 187 a year ex-VAT in 2025), which the floor ignores. The
  floor's policy plus network is GBP 127-130/MWh, against 109-123 of *total* non-commodity cost in
  the cap's own unit rate.
- **Writer 1's margin counts the standing charge as profit**, because settlement adds it to revenue
  and margin with no cost to serve deducted.
- So a renewal at the floor is **not loss-making in the world**. The market's best deal on those rows
  sits above the true per-kWh cost and below our inflated floor. The tier cut and the save do draw
  on one margin, but most of what blocks them is the floor's definition, not the market.
- Since 2026-10-13, writer 1 and the save read **two different floors** (capital-inclusive and not).
  The finding predicts held renewals now sit GBP 2.2-4.5 above the save's floor.

### 8c. What is not published (GAPs)

- **GAP: how real retention desks split margin between proactive renewal pricing and a reactive
  save reserve.** Nothing read for §2, §5 or §7 addresses it. This is a practitioner question,
  for the director.
- **GAP: what the 8% margin target counts, set against the cap's EBIT allowance.** It is named by
  the finding as the K8 page owed before writer 1's margin basis changes.
- Settled since the first draft: **whether our floor is right.** It is not, on the cap's own
  construction (above).

### 8d. What follows, in the finding's order

1. **Company (B12):** writer 1's margin is measured on the unit-rate margin, with standing-charge
   revenue net of the cost it recovers, after the K8 page on the 8% target. The save then takes
   writer 1's floor (`pre_margin_unit_rate`), so there is one floor.
2. **World, separately (W3_3):** the electricity network schedule splits into per-kWh and per-day
   shares (Ofgem's model, the TCR from April 2023). It moves every settled figure, so it is never
   bundled with (1). It is decided for fidelity, blind to company results.
3. **The save is re-graded only after (1).** Until then its inertness says nothing about its design.

**Design choices this page makes:** none. Capping the tier cut to keep a save reserve is not
proposed while the floor itself is wrong.

## 9. How often a retention offer keeps a household that would have left (2026-10-22)

Written first under K8, before the retention guard learns to weigh its own save odds
(`docs/staging/records/SEAT_PREREG_THE_PER_CUSTOMER_SWITCHES_ON_TOGETHER_AGAINST_FLAT_2026-10-21.md` §13).
No new source was fetched for this section. It gathers what §2, §5, §7 and the sibling pages already
established, and labels the rest.

### 9a. The quantity, stated before any figure

> Of the households that would have left at this renewal without an offer, the share that stay
> because of one.

This is a save rate **conditional on would-have-left**. Two figures nearby are not it.
- **P(stay | offered)** counts every household that would have stayed anyway. Reading that as a save
  rate is the error that let `churn_model_performance.prevented_churn_saves` report 76 saves where
  §7 of the prereg found 0 at the roll.
- **The lift in any switching from a contact** (EFTC) counts internal re-fixes. A re-fix with the
  same supplier is not a household kept from leaving.

### 9b. What is published

| finding | what it measures | source | bearing on 9a |
|---|---|---|---|
| A supplier's own end-of-fix letter moved switching from 19% to 28%. Internal went 14% → 23%; **external stayed at 6% in both arms** | a contact's effect on where a household goes, n = 19,553, one supplier, 2019 | Ofgem EFTC trial §4.1 (`how_households_respond_to_supplier_contact.md` §2.1) | **The only randomised figure for a supplier contact at a fixed-term end, and it shows no fall in external loss.** The letter carried no discount, so it bounds a contact, not an offer. |
| Retention tariffs ran 25–36% (electricity) and 25–28% (gas) below rollover, 2012–14 | how deep a negotiated retention price was | CMA EMI final report §279 (§7b above) | microbusiness; a depth, not a rate of saves |
| Customer-initiated stops through the losing supplier: 0.4–1.3% of domestic switches | a save on a loss notice, pre-CSS, at most | Ofgem 2016 RFI (§5c above) | a reactive save after the switch has started, not a proactive offer at the roll |
| A home-mover retention programme raised retention from ~5% to ~30% | a journey redesign for movers | BFY Group case study, 2023 (§2a above) | a different journey (moving home) and consultancy marketing |

### 9c. GAPs, labelled

- **GAP: the save rate of a proactive, discounted retention offer at a domestic fixed-term end.**
  No GB source found reports it with a counterfactual. It is not established by any row in 9b.
- **GAP: whether the rate differs between a fixed term ending and a default-tariff stint.** EFTC
  splits its effect by previous tariff (fixed 0.130, SVT 0.105 woken share, §2.2 of the sibling page),
  but that is the woken share of any switch, not a save.
- **GAP (practitioner):** what a GB retention desk counts as a save, and over what window. The
  outcome-window question is already open on the knowledge map's *retention outcome window* row.

### 9d. What the build chooses, and why

- **The company learns its own save rate, because nothing published sets one.** Per type of term
  ending, over offers made in years before the roll, it reads observed losses among the accounts it
  offered against the losses its own belief predicted for them. The save rate is one minus that
  ratio, with Jeffreys' correction on the losses, and it is never below zero. This is the
  observed-over-expected the ending-term multiplier already uses
  (`company/crm/competitive_pressure.py`), asked only of the offered accounts.
- **What this cannot separate, said plainly.** Without a holdout, a save and a belief that
  under-reads its offered tail look the same. The offers are selected on belief above 0.30 and on a
  cut being available. If the belief under-reads that tail, the save rate reads low and the guard
  offers less. That is the safe direction (F11). The company's own holdout
  (`RetentionHoldout`) is the instrument that would separate the two, and it closes no row while
  `RETENTION_OUTCOME_WINDOW_DAYS` is `None`.
- **No prior is used, and no published rate is borrowed.** EFTC's external 6% → 6% is a contact
  without a discount. Using it as a prior of zero would decide the question before any evidence
  arrived. Where a type has no closed offers yet, the guard stays as it was, so the evidence can
  accrue. That is a fall-back with a named reason, not a value.
- **The decision.** An offer is made only where the belief at the roll × the save rate × the value
  the guard already protects (the term contribution, net of the bad-debt charge and plus the
  replacement cost avoided where those switches are on) exceeds the offer's cost. The field is default off.

### 9e. Measuring a retention offer against a randomised hold-out (2026-10-22)

Written under K8 before the save-rate holdout was built
(`docs/staging/records/SEAT_PREREG_THE_PER_CUSTOMER_SWITCHES_ON_TOGETHER_AGAINST_FLAT_2026-10-21.md` §15).
Why it is needed: on §12's run, the §9d save rate read 0.19 while the world kept 0 of the 32 offers
it was asked about. The only money the offers made came from moving stayers onto fixes, which M2
calls transfer.

**What published practice says.**

| finding | source | bearing |
|---|---|---|
| Targeting retention by **churn risk** can be ineffective. The customers most likely to leave are not the ones an intervention moves most. Targeting by **lift**, measured as treated churn against a randomised untreated group, reduces churn more than targeting by risk. Shown on a wireless carrier and a membership organisation. | Ascarza, "Retention Futility: Targeting High-Risk Customers Might Be Ineffective", *Journal of Marketing Research* 55(1), 2018 (AMA 2023 Weitz–Winer–O'Dell award) | **This is the company's position.** The belief ranks leavers (AUC 0.806), and the save rate it multiplies cannot be read from offered accounts alone. |
| A proactive retention contact can **raise** churn. In a randomised field experiment where some customers were sent plan recommendations and some were not, 6% of the control churned in the next three months against 10% of the treated. | Ascarza, Iyengar & Schleicher, "The Perils of Proactive Churn Prevention Using Plan Recommendations", *JMR* 53(1), 2016 | An offer's effect has no floor at zero, so only a comparison can tell its sign. The build floors the save rate at 0 for the guard, and reports the signed difference in its reason. |
| GB energy itself measures supplier contacts this way. Ofgem's EFTC and CMOC trials randomised which households received a supplier's letter or offer, and they report treated against control. | Ofgem EFTC 2019 §4.1; CMOC 2019 (`how_households_respond_to_supplier_contact.md` §2) | The regulator's own standard for "did the contact move switching" is a randomised control. The company holding out its own customers is that design, run on its own book. |

**GAPs, labelled.**
- **GAP: what share a GB energy retention desk holds out, if it holds any out.** No published source
  found. The share below is derived, not borrowed.
- **GAP: whether withholding a discretionary retention discount from a random group meets SLC 0
  (Standards of Conduct, fair treatment).** §6 records the Fixed Retention Tariff derogation, which
  permits a retention fix for existing customers. No rule found obliges a supplier to offer one. Ofgem's own trials randomised contacts. No Ofgem decision found addresses
  a supplier-run holdout. A practitioner question if it ever leaves the simulation, and it cannot
  leave it (G5).

**What the build chooses (`retention_save_rate_learned_against_holdout`, default off).**
- **Who is held out.** Only renewals the save-odds guard would offer on. The coin is the company's
  own: a hash of the account id and the roll date (`competitive_pressure.save_holdout_draws`). It is
  salted apart from B8's `holdout_arm`, so the two coins are independent. Both groups are chosen by
  the same guard, so they share one belief distribution, and their difference is the offer's effect.
- **The rate.** Per ending-term type, over closed years: the holdout's loss rate h minus the offered
  loss rate o, both Jeffreys-corrected, as a share of h: `(h − o)/h`, never below 0. It is a share
  and not the bare difference because the guard multiplies it by this household's belief.
  belief × (h − o)/h is the saves expected of one offer, so the per-customer ranking survives. It
  returns `None` with its reason until both groups have closed renewals of that type. The belief
  no longer enters the rate.
- **The share, derived.** The comparison must resolve the break-even difference in one year. An
  offer pays where belief × save × value > cost, so the save rate it must clear is cost ÷ (belief ×
  value). On §12's run that is 0.83 in aggregate over the 83 offers of 2017, the one year the guard
  offered in volume (34 of them were lost; later years run 1 to 24 offers). The difference to resolve
  is h × 0.83, with h taken as the offered loss rate 34/83. If offers save, that is the lower of the
  two rates, so the share errs larger, towards learning. At the two-sided 5% / 80% convention
  (z = 2.80), the variance `h(1−h)/N × (1/s + 1/(1−s))` must be at most (0.83h/2.80)². That gives
  **s = 0.27** at N = 83. At N = 300 it would be 0.06. At N ≤ about 65 no share resolves it in one
  year, and the even split (0.5), which gets there soonest, is used. This is in code as
  `save_holdout_share` and is printed by its test, so a new book moves it by its inputs, not by
  hand.
- **What it says plainly.** A break-even save rate of 0.83 means an offer must keep five in six of
  the losses the company predicts to pay. Little survives that bar. The holdout is how the company
  would learn this from its own book rather than from its belief.
