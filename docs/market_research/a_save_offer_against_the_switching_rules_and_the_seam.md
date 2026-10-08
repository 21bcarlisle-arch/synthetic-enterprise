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
   a save, or how many accept one.
5. **The seam.** The company is told of a loss only at **17:00 the day before the switch takes
   effect**, once the switch can no longer be cancelled. No decision reads that notice. The world has
   no submission date, no cancellable in-flight switch and no household answer to a save. **So
   the company sees no leaving signal before the loss, and a save could not change the outcome here.**

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
3. **There is no household answer to a save.** Even with an earlier notice, nothing in the world lets a
   household that has signed with a gainer cancel in cooling-off because its old supplier made an
   offer. The only stay-or-go answer the world gives is the renewal-time roll.

**What a real supplier would see**, from §1–§2:

| signal | when | in this world |
|---|---|---|
| CSS Invitation to Intervene (switch Pending) | 1 working day to 28 days before the effective date (from Jul 2022) | **absent**: no submission date (`GAPS`) |
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
