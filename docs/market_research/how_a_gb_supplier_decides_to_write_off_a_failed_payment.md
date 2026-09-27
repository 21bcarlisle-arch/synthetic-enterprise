# How a GB domestic supplier decides to write off a failed payment

**Knowledge:** none -- no knowledge page covers supplier debt and collections; the nearest, price-cap, carries the bad-debt ALLOWANCE and not the write-off practice this note answers

**2026-09-27. Research only, and done before anything in `simulation/` changes.** It asks what the
world does, so `simulation/arrears_engine.compute_emergent_bad_debt` can be judged against it on
fidelity grounds alone. What prompted the question was a company result: the selection figure's
sign is decided by this rule
(`docs/staging/SEAT_FINDING_A_FAILED_BILL_IS_WRITTEN_OFF_IN_FULL_IFF_THE_CUSTOMER_EVER_LEAVES_2026-09-27.md`).
The baseline split does not let that result justify a change, so the case below has to stand
without it. The design that follows from this note is
`docs/staging/SEAT_DESIGN_THE_WRITE_OFF_RULE_RE_KEYED_TO_THE_BALANCE_AT_CLOSE_2026-09-27.md`.

## What a write-off is, first

Three things get conflated here, and they are different quantities.

- **A failed payment** is a collection event. A direct debit returns unpaid, or a standard-credit
  bill passes its due date.
- **Arrears / debt** is a standing BALANCE on an account. Ofgem's indicators count an account as *in
  arrears* when a bill has gone unpaid for more than 91 days with no arrangement, and *in debt* when
  a formal repayment arrangement exists (Ofgem, *Debt and arrears indicators*, methodology).
- **The bad debt charge** is the P&L line. Ofgem defines it as *"costs of write-offs and provisions
  in supplier's accounts from customers' energy bills that are never paid"*. *"Suppliers make
  estimates (known as provisions) for the amount which will never be paid. They then adjust these
  estimates over time and eventually finalise them through write-offs. Write-offs can take some time
  to crystalise as suppliers attempt to recover the debt."* (Ofgem, *Price cap consultation,
  Appendix 2: Debt-related costs*, Dec 2024, §2.4, §2.6.)

**So the P&L cost of bad debt is recognised when it is PROVISIONED, and the write-off only
finalises it.** On Ofgem's definition, the sim's `bad_debt_gbp`, which is built from write-offs
alone, is a narrower quantity than the one the cap allowance and every supplier's accounts carry.
The question below is about the write-off. The design has to say which of the two quantities it
models.

## (a) Is a failed direct debit re-presented and chased rather than written off? — ESTABLISHED: YES

- **Bacs scheme.** A returned DD may be re-presented up to twice (three attempts in all), within 30
  days of the original presentation, for the same amount, with the payer notified in advance. It
  may not be re-presented where the ARUDD reason is "no instruction". These are the scheme rules as
  bureaux publish them (Movimo, *Re-presenting unpaid Direct Debits*; Access PaySuite, *How to
  recover failed Direct Debit payments*). The Bacs rulebook itself is members-only and was not read
  directly, and that is the one soft edge on this answer.
- **A supplier's own published practice.** British Gas: *"When a payment is not received, we will
  try again 14 calendar days later."* If the second attempt also fails, the Direct Debit is
  stopped and the customer is moved *"over to another payment option"*, which means leaving the DD
  rate (British Gas, *Setting up an energy Direct Debit*, help page, read 2026-09-27).
- **What happens to the money.** It stays on the account as a balance, and the supplier's licence
  duties then start. SLC 27 requires the supplier to identify payment difficulty, offer a repayment
  arrangement based on ability to pay, and escalate only after that (see
  `company_debt_management.md` §1, §6). Ofgem's indicators then count the balance as arrears or
  debt on a live account. Nothing in the regulatory sequence treats the failed payment as a loss
  event.

**Verdict.** A failed DD is a collection event that leaves a chased balance on a live account. It
is not a write-off. The sim's `arrears_stages` path (`WRITTEN_OFF` at due+90d, for the whole bill
amount, per bill) has no counterpart in what is published. Separately: +90d is the IFRS 9
rebuttable 90-days-past-due *default* presumption (IFRS 9 B5.5.37), which is a PROVISIONING
trigger and not a write-off date. That is probably where the number came from, and it answers a
different question.

## (b) Is the write-off the balance still unpaid at account close, after collection? — THE AMOUNT: ESTABLISHED. THE CLOCK: NOT.

**Established:**

- Ofgem classifies unrecovered debt by **age, payment method and live/final**, and states that the
  proportion unlikely to be recovered depends on those three (Appendix 2, Dec 2024, §3.14). The
  Debt Relief Scheme working paper weights supplier provisioning rates by payment method AND
  *"account type (Closed or Live)"*, arriving at an average weighted provisioning rate of about
  75% on 2022–24 debt (Ofgem, *DRS policy update working paper*, Aug 2025, §5.20). **Debt on a
  closed account is a recognised, separately provisioned class.**
- Closing is where a large share of unrecoverable debt arises. Suppliers tell Ofgem that change-of-
  tenancy / unnamed accounts may account for **20–40% of all domestic debt** (Ofgem, *Call for
  input: Tackling energy debt in the supplier home-moves process*, Dec 2025, §2.5).
- What sits on a final account is the final-bill balance: whatever on-supply collection did not
  recover. That is the quantity the DRS calls closed-account debt.

**Not established, and deliberately left as a gap:**

- **The time from close to write-off.** Ofgem records that suppliers differ in *"how long they
  chase up bad debt before writing it off"* (Appendix 2, Dec 2024, §2.22, "Impacted by
  supplier assumptions") and that *"there are also differences in when debt is written off"* (Ofgem, *Call
  for Input on the allowance for debt-related costs*, Apr 2023, §4.4). It is supplier policy, and no
  published source gives an industry clock.
- **The order of DCA placement and write-off.** `company_debt_management.md` §1 puts external DCA
  referral at around 60–90 days after internal collection fails, which is BEFORE write-off. The sim
  runs `WRITTEN_OFF → PLACED_WITH_DCA → RECOVERED/SOLD` the other way round
  (`ASSUMPTIONS.md` already flags the +30d placement as unbenchmarked). Some suppliers do write off
  and then sell, so the published record does not settle the order either way.

**Verdict.** Keying the write-off to the unpaid balance at close is supported. No published source
supports a date for it.

## (c) Are a stayer's persistent arrears ever written off, and on what clock? — THE COST: YES, THROUGH PROVISION. A WRITE-OFF CLOCK: NONE PUBLISHED.

**Established:**

- Live-account debt is provisioned. The DRS weighting is explicitly Closed *and* Live (§5.20
  above). The bad-debt charge on a stayer's aged arrears therefore reaches the P&L while they stay,
  through provision growth, whether or not anything is ever written off.
- Provision follows age. Energy UK's supplier data puts the recovery rate on debt and arrears older
  than 12 months at about **31% / 15% / 9%** (2022-23 / 2023-24 / 2024-25), against **60% / 56% /
  38%** for debt under 12 months. Aged arrears grew from 52% to 65% of arrears between 2023 and 2025
  (Energy UK, *Energy debt: Everyone pays*, Feb 2026, Fig. 5 and p.6). *These figures are read off a
  bar chart; the pairing of bar to series follows the legend order and should be re-checked against
  the source before any of them becomes a constant.*
- Live-account write-offs do happen, as EVENTS rather than on a clock:
  - **Scheme write-off.** Ofgem's Debt Relief Scheme phase 1 writes off about £0.5bn of arrears
    accrued 1 Apr 2022 – 31 Mar 2024 for customers on means-tested benefits who owe £100 or more,
    and live accounts are included (Ofgem, *DRS statutory consultation*, Nov 2025; home-moves CFI
    p.3).
  - **Redress write-off.** British Gas wrote off £70m of vulnerable customers' debt in the 2023
    warrant settlement (`company_debt_management.md` §3).
  - **Statute bar.** Limitation Act 1980 s.5 bars recovery six years after the cause of action, but
    s.29(5) restarts the clock on any part-payment or written acknowledgement. A stayer who is still
    paying something towards the account rarely reaches it.

**Not established:** any voluntary supplier write-off of a live, still-billed account at a given
age. None of the sources above describes one.

**Verdict.** "Persistent-arrears write-off for stayers", as a clock, is not supported. What the
published record supports is that a stayer's aged arrears **cost money while they stay, through
provision**, and are written off only by an external event (scheme, redress, statute bar). **This
partly revises the frame put to the director**: the seat's recommendation there assumed a stayer
write-off rule, and the evidence points at a provision instead.

## What the sim does against this

`compute_emergent_bad_debt` books a failed bill's full face value as bad debt if and only if the
customer is in `churned_ids` at the end of the run, dated due+90d, and books nothing for a stayer.

| Published practice | Sim |
|---|---|
| failed DD → re-presented, then a chased balance | every failed bill is a terminal case |
| loss recognised by provision on age × method × live/final | loss recognised only at write-off |
| write-off = balance unpaid at close, after collection | write-off = every failed bill of an eventual leaver, dated while still on supply |
| stayer's aged arrears cost money via provision | stayer's arrears cost nothing, ever |

Both directions are wrong. A leaver is over-charged, because bills that were cured or would have
been cured are written off. A stayer is under-charged, because persistent arrears never reach the
P&L. **That makes the size of the gap between a leaver and a stayer an artefact of the rule**, and
that gap is exactly what the selection figure differences.

## Sources

- Ofgem, *Consultation – Appendix 2: Debt-related costs*, Dec 2024 —
  <https://www.ofgem.gov.uk/sites/default/files/2024-12/Appendix_2_Debt_related_costs.pdf> §2.3–2.6, §2.22, §3.14
- Ofgem, *Price cap – Call for Input on the allowance for debt-related costs*, Apr 2023 —
  <https://www.ofgem.gov.uk/publications/price-cap-call-input-allowance-debt-related-costs> §1.1, §4.4–4.5
- Ofgem, *Debt Relief Scheme (DRS): Policy update working paper*, Aug 2025 —
  <https://www.ofgem.gov.uk/sites/default/files/2025-08/DRS-working-paper-final.pdf> §3.20, §5.20–5.22
- Ofgem, *Call for input: Tackling energy debt in the supplier home-moves process*, Dec 2025 —
  <https://www.ofgem.gov.uk/sites/default/files/2025-12/Tackling-energy-debt-in-home-moves-process-call-for-input.pdf> §2.1–2.5
- Ofgem, *Debt and arrears indicators* (methodology) — <https://www.ofgem.gov.uk/data/debt-and-arrears-indicators>
- Energy UK, *Energy debt: Everyone pays*, Feb 2026 —
  <https://www.energy-uk.org.uk/wp-content/uploads/2026/02/Energy-UK_Energy-Debt-Everyone-Pays_February-2026.pdf> Fig. 5
- British Gas, *Setting up an energy Direct Debit* — <https://www.britishgas.co.uk/help-and-support/bills-and-payments/setting-up-a-direct-debit>
- Movimo, *Re-presenting unpaid Direct Debits* — <https://movimo.co.uk/resources/re-presenting-unpaid-direct-debits/>;
  Access PaySuite — <https://www.accesspaysuite.com/blog/how-to-recover-failed-direct-debit-payments-with-smart-represents/>
- IFRS 9 *Financial Instruments* §5.4.4 (write-off when there is no reasonable expectation of
  recovery), B5.5.37 (90-days-past-due default presumption)
- Limitation Act 1980 ss.5, 29(5)
