# Debt realism: three world-fidelity gaps, each written K8-first

**Knowledge:** debt-and-collections

**2026-10-24, delivery seat.** The director's Capabilities steer (24 Oct, section 1, "Debt realism":
"each to start with K8") names three gaps the Debt row of `/capabilities/` shows as *Not yet*:

1. "Write-offs per pound billed are well below a large supplier's";
2. "the world generates no prepayment debt";
3. "payment-failure rates are not yet sourced".

Nearly all the research already exists, so this file does not repeat it. For each gap it collects
the rules, the published evidence (with pointers), what the world does today (read from the code at
`2603b9f61`), what is GAP, and the design choices for the build that follows. Nothing in `simulation/`
changes in this commit except one stale comment. The world builds are named, not started.

Sources this file reads, and does not re-derive:
- `bad_debt_provisioning.md`: Centrica's charge, write-offs and provision matrix; the "One payment
  truth" before-and-after table, and its ranked causes (s. after 1160).
- `debt_and_collections.md`: the population split P1–P8, the price-cap debt allowances, SLC 28B, and
  the gap list in s.8.
- `gb_domestic_bill_payment_failure_and_arrears_prevalence.md`: what "payment failure" is, s.(a)–(f).
- `how_a_gb_supplier_decides_to_write_off_a_failed_payment.md` and `company_debt_management.md`.

---

## 1. Write-offs per pound billed

**What the quantity is.** GBP written off in a period, over GBP billed in the same period, for
residential accounts. It is a **flow over a flow**. It is not the bad-debt *charge*, which is the
movement in the provision plus write-offs, less recoveries (Ofgem App. 2, Dec 2024, s.2.4–2.6). It
is not the arrears *stock* either. The world's `BAD_DEBT_BASIS` is write-offs only (its stayer
provision leg is off), so a write-off rate is the only like-for-like comparison available today.

**Rules.**
- A failed direct debit is re-presented and chased as a live balance. It is not written off
  (`how_a_gb_supplier_decides_to_write_off_a_failed_payment.md`; Bacs re-presentation; British Gas
  stops the DD after a second failure).
- A write-off falls on the balance left unpaid at close, after collection. A stayer's arrears are
  written off only by event: a scheme, redress, or the Limitation Act 1980 s.5 six-year bar, which a
  part-payment restarts (s.29(5)).
- IFRS 9 books the expected loss as a provision long before the write-off, so the charge leads the
  write-off by years (`bad_debt_provisioning.md` s.1).

**Published evidence.**
- Centrica UK and Ireland residential, 2021–2025: write-offs of GBP 58m–113m a year, against
  revenue of about GBP 7.6–12.8bn. That is **about 0.7–1.0% of revenue** (0.76, 0.84, 0.88, 1.04 and
  0.67%; derived from Note 17 and the Audit and Risk Committee's charge-to-revenue share).
- Charge rates (not write-offs) of 1.1–3.1% of revenue at Centrica (2019–2025), and 1.6–3.9% across
  four suppliers in 2023–24.
- The cap's debt allowance by payment method, before July 2025: DD GBP 25 (1.4%), standard credit
  GBP 121 (6.5%), prepayment GBP 10 (0.6%). From July 2025: GBP 71 per dual-fuel customer, or 3.6% of
  bills, allocated DD 57, standard credit 160, prepayment 19. These are bad debt plus administration
  plus working capital, averaged across the industry, so they are a ceiling on write-offs, not an
  estimate of them.
- A gone household pays far less than a live one. Final bills more than 90 days old recover 10–25p
  in the pound (`bad_debt_provisioning.md` s.3.1), and Centrica provides 32–37% against final bills.

**What the world does.** After the one-payment-truth correction (12 Oct), the world writes off about
0.15% of residential billing on 160 founders (14 cases). That is **about 5–7x under** the Centrica
anchor. The arrears **stock** matches Ofgem at the same time (4.4% against 5.1%, MET). So the world
holds about the right amount of debt and almost never loses it. The crisis bad-debt validator reads
the same thing: a behavioural write-off share near 0.1%, against its 1% floor
(`SEAT_FINDING_THE_CRISIS_BAD_DEBT_CONTROL_HAS_SKIPPED...2026-10-14.md`).

**Why "below a large supplier's" is not yet a clean comparison.**
- Centrica's book is heavy on standard credit and legacy accounts. The world's book is 72% direct
  debit and mostly LOW stress. At the cap's ratios, mix alone moves the expected rate several-fold.
- Centrica's figure is for UK *and Ireland*, and revenue is not quite billing (it includes unbilled
  accruals).
- Fewer than twenty write-off cases make the world's factor wide, though not its direction.

**GAPs.**
- **G1.1:** what share of a *closed* account's pre-final-bill arrears (as distinct from its final
  bill) is ever recovered, and how late. Not published. This is a question for a practitioner.
- **G1.2:** how long after close a supplier writes off. It is supplier policy, not published. The
  world uses a declared convention (`WRITE_OFF_DATE_CONVENTION = "final_bill_due_date"`).
- **G1.3:** a write-off rate by payment method for any one supplier. Only the cap's
  industry-average allowance (cost, not write-off) is published.

**Design choices for the build.**
- **Grade, never fit** (R13). The anchor is a range, 0.7–1.0% of revenue, published with the mix
  caveat beside it. The world is not tuned toward it. A build changes only a mechanism the
  evidence says is wrong.
- **First mechanism: cause 1 in `bad_debt_provisioning.md`'s ranking.** A leaver's ordinary arrears
  are repaid after it has gone at the *stayer's* rate, because the triad's later settlement does not
  know the account has closed. The published evidence says a gone household repays 10–25p in the
  pound on an aged final bill. The build gives a closed account's arrears the gone-household
  recovery, carried as a labelled range because of G1.1, not a point.
- **A mix-adjusted comparison before the verdict.** Re-weight Centrica's rate to the world's
  method mix using the cap allowance's relativities, and publish both readings. This is derived
  arithmetic, labelled as such.
- A prediction is filed before the build: the direction is up, and the size is unknown. If the
  write-off share does not move toward the range, cause 1 is not the main cause, and cause 2 (no
  stayer write-off inside the window) is weighed next.

### 1a. The build: a gone household pays no lump after its final bill (2026-10-24)

**What the code does today (read at `cfe4d94be`).** The triad decides at each failed bill's due
date whether and when the household pays it off later (`payment_behaviour_source.
later_settlement_date`, up to 3 + 22 months out), and queues the lump. Nothing tells the queue
that the account has closed since. A lump dated after a leaver's final bill is held until the
run's end, then crossed (`collections_journeys`, forced). The engine nets it against the
closing balance (`arrears_engine.balance_settlement_from_outcomes`). So a household that has gone
repays at the stayer's Centrica live-balance rates. The engine then takes the gone-household
recovery on top: `post_write_off_recovery_share` = 1 − `prov_coverage_final_bill_over_90d`, which is
**10.4–24.5p in the pound, default 12.2p** (Centrica Note 17, 2019, 2024 and 2025).

**The choice, and why it adds no number.** The gone-household recovery already sits in the world, on
the register row, as a labelled range. The defect is that a leaver gets *both*: the stayer's lump
and then the gone household's recovery on what is left. The build removes the first. A lump (or an
early-contact payment) dated **after the closed account's final-bill due date** does not cross to
either company. The balance is written off at close, and the gone-household share is recovered
from it by the path that already exists. Adding a second recovery draw for the lump would count
one collection twice, as `mover_final_bill_outcome`'s docstring already says of the final bill.
"Closed" is the engine's own set (`household.households_whose_account_closed`, by supply point),
so the queue and the P&L cannot disagree on who left. Switch:
`world_payment_truth.GONE_HOUSEHOLD_PAYS_NO_LUMP`, shipped on, as a world correction made before
any supplier result was seen.

**Named limits.** A lump dated between the departure and the final bill's due date still crosses.
The household has gone, but its closing balance has not yet been demanded, and no source separates
the two. A plan instalment after close is not touched by this build. G1.1 stands: the share
recovered is the final-bill complement, applied to the whole closing balance.

**Prediction, filed 2026-10-24T12:46Z, before the after-run and while the before-run had not
finished.** Book: 160 founders, settlement budget 0, the same seed. Code: origin `cfe4d94be` before;
the same plus this build after.
- Residential write-offs per pound billed go **up**, from about 0.15% to **0.2–0.5%**. That is
  still below Centrica's 0.7–1.0%: causes 2 and 3 (no stayer write-off in the window, and the book
  mix) are untouched.
- Write-off cases rise above the baseline's count. No stayer's write-off changes, because the
  statute-bar leg does not read closed accounts' lumps.
- Lumps lost at close: more than 0, and fewer than the lumps delivered before.
- **Refutation:** written off falls, or no lump is lost, or a statute-bar write-off moves.

## 2. Prepayment debt

**What the quantity is.** Before measuring, "prepayment debt" splits into three different things,
with different causes and different rules. They are measured separately:
- **(a) Debt recovered through a meter.** A credit customer's arrears, moved onto a PPM fitted for
  debt (voluntarily or involuntarily) or carried onto one, and repaid by a weekly deduction from
  top-ups. Ofgem's "repaying through prepayment" stock counts this. It is P4 in
  `debt_and_collections.md`.
- **(b) Emergency or friendly credit** used and not yet repaid. It is repaid from the next top-up.
- **(c) Standing charges accrued while off supply** (self-disconnection), recovered when the
  household tops up again.

**Rules.**
- **SLC 28B, involuntary PPM** (Code of Practice 18 Apr 2023, licence from 8 Nov 2023, extended to
  2027). The Debt Trigger is charges outstanding for 3 months or more after the bill, GBP 200 or
  more per fuel, and no plan in place. It also requires at least 10 contact attempts, the SLC 27
  duties, a Site Welfare Visit, and the safe-and-practicable test. It is banned for over-75s with no
  support in the house and for households with children under 2. Warrant costs are capped at GBP 150.
- **SLC 27, ability to pay**, sets the recovery rate. The 2025 means for new PPM-for-debt installs
  were GBP 6.01 a week for electricity and GBP 4.40 for gas, agreed over 365 and 342 weeks
  (`debt_and_collections.md`, P4).
- **SLC 14 and the Debt Assignment Protocol.** A PPM customer under the DAP threshold (GBP 500) may
  take the debt to a new supplier.

**Published evidence.**
- Ofgem's quarterly series: **30–40% of repaying electricity customers repay through a PPM**,
  peaking at 58% in Q4 2023. The series also counts prepayment self-disconnections.
- About 4.3m households are on a PPM (`company_debt_management.md` s.3, secondary sources).
- The cap's PPM debt allowance is the smallest of the three methods (0.6% before July 2025;
  GBP 19 of 71 after), because recovery is automatic while the household tops up. The
  household's remedy is to self-disconnect, not to default.

**What the world does.** About 13% of residential supply points are drawn as prepayment
(`payment_behaviour_source`). A prepayment bill cannot fail (`arrears_engine.PREPAYMENT_METHOD`), and
no meter is changed for debt in a run (`world_payment_truth`, simplification 4). The household's
answer to a PPM-for-debt offer exists (`payment_method_dynamics.answer_prepayment_offer`), but as a
labelled range shipped at 0. So none of (a), (b) or (c) is produced. In the 10 Oct capture, 87 of
667 accounts were prepayment, and none was in either arrears stock on any seed.

**Why it matters.** The world matches Ofgem's *arrears* stock (no plan, over 91 days), which by
definition holds almost no PPM debt. It cannot match the *in debt* stock (repaying under a plan),
of which 30–58% repays through a meter. The supplier also never sees the cheapest recovery route the
cap prices.

**GAPs.**
- **G2.1:** how many PPMs were fitted for debt each year after the 2023 rules. Not found
  (`debt_and_collections.md` scope).
- **G2.2:** what share of households offered a PPM for debt agree to one. Not published. It is the
  existing labelled range at 0.
- **G2.3:** how large (b) and (c) are: emergency-credit balances and accrued standing charges per
  PPM household. Not published as a stock. Self-disconnection counts are published, but the GBP is
  not.
- **G2.4:** the rule source for how standing charges accrue while off supply has not been re-read
  this turn. The licence text must be read before (c) is built.

**Design choices for the build.**
- **Build (a) first.** It is the population Ofgem's stock counts, its rules are fully published
  (the Debt Trigger above), and the route exists on both sides: the company's offer, and the world's
  `move_to_prepayment_for_debt`. Recovery is the published weekly mean, taken at top-up. The
  household's agreement is the existing labelled range. Grade the share of repayers on a PPM
  against Ofgem's 30–40%, never fitting it.
- **(b) and (c) wait** for G2.3 and G2.4. Until then the world says plainly that it produces
  neither. Self-disconnection is the observable that stands in for default, and it is what the
  build would grade.
- **The wall.** The company sees a meter's top-ups and its debt balance, as a real supplier does. It
  never sees the household's reason for self-disconnecting.

**Built, part (a), 2026-10-24.** The route's second half now exists: a meter changed by Consent
(`move_to_prepayment_for_debt`, only when the take-up toggle is on) recovers the debt carried onto it
by a weekly deduction at the published mean (`payment_method_dynamics.meter_recoveries`; GBP 6.01
electricity, 4.40 gas), posted to the company ledger as cash through the collections desk
(`_read_meter_recoveries`) and crossing the seam as `get_meter_recoveries`. Later bills on that
account are paid before use, and a lump settlement of a bill from before the move is withdrawn so the
same arrears are not repaid twice (`HouseholdPlanBook.repays_through_plan`). The shipped world is
unchanged: take-up ships at 0. Named simplifications 5 and 6 in the module (mean not per-household;
never moved back).
- **The grade against 30-40% is circular for take-up.** The toggle's low/high (0.30/0.40) were taken
  FROM that Ofgem range. A run at those settings reproduces the range by construction at the
  offer step, so the share of repayers on a PPM can only grade the OTHER half of the denominator
  (how many debtors reach the 90-day rung and how many repay by plan or lump). Publish it as that,
  with the denominator named, never as validation of take-up.
- **Not yet done:** no engagement-attempt, Site Welfare Visit or involuntary path (Consent only);
  Debt Trigger is not checked on the Consent route, which SLC 28.22 does not require.

## 3. Payment-failure rates

**What the quantity is.** Six different things travel under this name
(`gb_domestic_bill_payment_failure_and_arrears_prevalence.md`, "What each quantity IS"). The world's
draw is the first of them: **a DD return on first presentation, per bill**, before any
re-presentation.

**Rules.** Bacs allows a returned DD to be re-presented up to twice within 30 days. British Gas
re-presents after 14 days, then stops the DD and moves the customer off it. SLC 27 governs what
follows a failure.

**Published evidence.**
- **No published rate by count, for energy, at any segmentation.** This remains true.
- A value bracket for one supplier. GoCardless's Octopus case study gives first-presentation failure
  of at least 0.40% of collections by value, and 0.57–1.8% once the retry recovery share (22–70%,
  vendor figures) is applied. The figures are crisis-era, by value, and self-reported by the
  vendor.
- A survey bound, FCA *Financial Lives*: 2.2% (2020), 3.0% (2022) and 3.4% (2024) of UK adults fell
  behind on electricity at all in six months.

**What the world does.** The Capabilities line "not yet sourced" is now **half stale**.
- **The LOW tier's level is sourced as an ESTIMATE.** It reads the register
  `dd_return_rate_first_presentation` (0.87%, by value, one supplier). Cure is drawn separately, at
  `dd_representation_success_share`.
- **The MODERATE and HIGH relativities are not sourced.** At 4x and 11.7x LOW, they are the old
  3/12/35% ratios. Nothing published segments a return rate by income or stress.
- Every credit method (DD, standing order, card and standard credit) fails at this one DD-derived
  table, and only a DD is re-presented. This is a named simplification.
- **A second, older copy of the table** survives in `simulation/payment_timing.py`
  (`_DD_FAILURE_PROBABILITY`, 3/12/35%, unsourced). No run reaches it: `run_phase2b` imports only
  `stress_bad_debt_multiplier` from that module, and `generate_payment_record` is called only by two
  `tools/couple_w2_*` scripts and tests. It is a concept with two homes. Handed to the
  own-code-review continuation (`own-code-review-unused-duplicated-wall-crossing`) to rule archive
  or merge.

**GAPs.**
- **G3.1:** a return rate by count, and by any household segment (income, arrears or vulnerability
  flag). This sits in suppliers' own data or behind Bacs membership. It is a practitioner question.
- **G3.2:** the failure rate of a standard-credit bill against its own due date. Not published.
- **G3.3:** whether "failed" in the vendor figures includes cancelled mandates.

**Design choices.**
- The Capabilities row should read: *the lowest-stress level is a sourced estimate (one supplier, by
  value); how failure rises with stress is not sourced.* This is a wording correction for the
  continuation that holds `site/capabilities/` (`capabilities-steer-remaining-before-monday`), not
  made here.
- The relativities stay as a named simplification, with direction of error unknown, until G3.1
  is answered. They are graded indirectly: the world's arrears stock is MET against Ofgem, which
  bounds the combined effect of level, relativities and cure, but not each one alone.
- Standard credit gets its own failure table only when G3.2 has an answer. Meanwhile the shared
  table is stated on the page as a simplification.

---

## Corrections made in this commit

- `simulation/arrears_engine.py`, the comment on `STAYER_FAILED_DD_BUCKET_ENV`, said a sim DD
  failure "has no source and no stated basis". Since `c1e3e5105` the LOW level is sourced, and the
  basis is stated as first presentation, gross of re-presentation. What stays open is which
  provision bucket a stayer's *uncured* failure sits in. The comment now says that.
- The debt-and-collections knowledge page's scope note said the simulated payment-failure rates
  "are not sourced". It now says the lowest-stress level is a one-supplier estimate and the
  relativities are not sourced.
