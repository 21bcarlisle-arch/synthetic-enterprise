**Knowledge:** vulnerability-and-the-psr

# Wiring the world's precarity state to what a supplier can see: the K8 page before the build (2026-11-09)

This is the knowledge page that K8 requires before the world's financial-vulnerability state (V2, concept
`vuln.ability_to_pay`) is wired to anything. The evidence is now in: the UKDS order closed in `959e8d102` (the
predictions) and `759ddc4c1` (the results). **No world or supplier value changes on this page.** Building it is world
feature work, so it waits for the correctness stretch to exit (director ruling of 26 Oct,
`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`). This page does not wait.

What the world and company do is **read from code at origin `f2f110263`, not run**.

## 1. What the rules require (the supplier side, unchanged)

As on the published page (`site/knowledge/vulnerability-and-the-psr`, sources in
`vulnerability_psr_and_ability_to_pay_2026-10-25.md`):

- **SLC 27.8A/B (from 15 Dec 2020):** repayment set by ability to pay, and re-engagement after a failed arrangement.
- **SLC 27.5B (from 14 Dec 2023):** contact no later than after two missed monthly payments, consider repayment
  pauses, and free contact for customers who are struggling.
- **The involuntary prepayment code (Nov 2023):** never for some groups, and only after a welfare visit.

No rule tells a supplier to infer hardship from tenure, age or postcode. A supplier is told to *identify* customers in
vulnerable situations and to act on ability to pay. In practice it does this from what it holds: payment method,
arrears, contact, and what the customer tells it. **So the world must make that inference exactly as hard as life
makes it.** That is what this wiring is for.

## 2. Before measuring: what "precarity" is here. There are three constructs, not one

| Construct | Definition | Prevalence | Where it lives |
|---|---|---|---|
| **V2, the world's state** | CIM W5 segmentation, "financially vulnerable or highly vulnerable": cannot save or absorb an unexpected expense | 30% (toggle `vuln_financial_prevalence`, 0.26-0.32) | `simulation/vulnerability_state.py`. Drawn, and drives nothing |
| **T, the 6614 target** | Reference person finds it quite or very difficult to get by, **or** the home cannot be kept adequately warm | 20.7% | `which_supplier_observable_recovers_precarity_understanding_society_2026-11-09.md` |
| **The precarity factor** | One latent factor loading on arrears, difficulty, cold, prepayment and not owning | (a score, not a share) | `precarity_affluence_and_life_stage_on_one_record_understanding_society_2026-11-09.md` |

**The measured strengths belong to T, not to V2.** V2 is broader (30% against 20.7%), and "cannot absorb an
unexpected expense" includes households that pay every bill and keep warm. Carrying T's strengths onto V2 is a
transfer between constructs. The table below prints what the transfer does at real inputs. It holds each flag's odds
ratio from 6614, the world's own flag share, and the prevalence it is put on:

| Flag (world share) | OR on T | At 20.7% (T): precision / recall | At 30% (V2): precision / recall |
|---|---|---|---|
| Prepayment (14% of electricity households) | 3.20 | 40% / 27% | 53% / 25% |
| Renting (35%) | 4.23 | 37% / 62% | 50% / 58% |

Recall barely moves. **Precision rises by 13 points on the broader construct.** So a world that draws V2 at 30% with
T's odds ratios would make a flag-reading supplier look more right than the evidence shows. That flatters the
company's inference, which is the unsafe direction (F11). So the transfer is not made silently. It is the first GAP
(§5, G1).

**Corrected by measurement, 9 Nov (G1 closed):** on a V2-shaped target (cannot save or replace broken goods, or
cannot meet a £200 unexpected expense: 27.8%), prepayment's precision is **55.2% [53.3, 57.4]** at recall 25.8%,
odds ratio 4.00. The transfer did not flatter the supplier; it slightly understated prepayment. The worry above was
the right question and the wrong guess. `v2_shaped_precarity_strengths_and_the_payment_tenure_cells_understanding_society_2026-11-09.md`.

## 3. What the evidence says the wiring must reproduce

From 6614 wave 14 (weighted, n = 17,389 complete households), against T:

| Observable | Does the world draw it today? | Measured relation to T | Wire? |
|---|---|---|---|
| **Prepayment** | Yes: `household_segments.payment_channel_for_customer`. 72% DD; half the rest prepay, so 14% (6614: 12.9%) | precision 40.6%, recall 25.5%, OR 3.2 | **Yes** |
| **Renting** (social / private) | Yes: `household_segments.tenure_for_customer`. 65 / 19 / 16 (6614: 37.2% renting, 19.3% social) | precision 35.7%, recall 64.5%, OR 4.2. Strongest single flag | **Yes** |
| **Behind on bills** | It is an *outcome* of the world (`arrears_engine`), not a drawn trait | precision 68.2%, recall 33.4% (all household bills, not energy) | **Not as an input.** V2 drives arrears, and arrears then carries the association (§4) |
| **Age 65+** | **No.** The world draws no occupant age | 0.43 times the rate of the rest (OR 0.36) | **Cannot.** GAP G3 |
| **Income** | **No.** The world has `income_stress` (event-driven), not an income level | moderate: income quintile alone AUC 0.65; adds 0.018 to the supplier set | **No.** Nothing to key on, and the evidence says it is not the missing key |
| **Means-tested benefit / WHD match** | No. The company's WHD register has no caller | precision 44.0%, recall 41.5% (an upper bound on what matching shows) | Later, through a seam notice, not here |

**The acceptance target is recoverability, not the flags.** In life, a supplier holding prepayment and arrears ranks T
at AUC 0.68 (in-sample). Adding renting takes it to 0.74. Once the build is wired, the world's hidden state, scored
by the company-visible flags, should land near those figures. It should not land well above them: a world in which
prepayment identifies precarity better than it does in life is a world the company cannot be defeated by. It should
not land well below either, or the world hides what a real supplier can see.

**The crisis cut (SERL SN 8963) bounds what the precarity state must NOT do.** Weather-adjusted gas fell 7-13% in the
EPG winter. In percent, the most deprived IMD quintile cut as much as the least (+1.6 points [-0.4, +3.6]), and social
renters cut as much as owners. The world's `simulation/price_response.py` draws no income or deprivation gradient
today. That agrees with the evidence at area level, so **V2 must not scale the percentage price response.** The
absolute cut follows use (IMD 5 cut 8.2 kWh/day, IMD 1 cut 6.1), and the world's per-household draw scaling the
household's own kWh already gives that shape. Private renters cut 3.9 points more [+1.2, +6.6]. That is one contrast
on a 420-home group in a changing panel. It is recorded as a lead, not wired.

## 4. The design, and why each choice

1. **One state, one definition, and the strengths measured on it.** Before the build, re-fit the 6614 proxy with a
   **V2-shaped target** (unable to meet an unexpected expense, or no savings, from the same wave's material-deprivation
   and saving items), so that the strengths and the state are the same construct (closes G1). If no V2-shaped item is
   on the EUL file, the fallback is to redefine the world's state as T at 20.7%. That fallback moves
   `vuln_financial_prevalence` and the arrears relative risk together, and the page will say so. It will not put T's
   odds ratios on a 30% V2.
2. **Draw V2 conditionally on the cell the world already draws, and leave the cell's own draws alone.** The payment
   channel and tenure draws keep their streams and marginals byte-for-byte. V2 keeps its own substream
   (`vulnerability_hidden_state`, `financial::<household>`). Only its threshold becomes P(V2 | payment method ×
   tenure), read from a 6614 cross-tab of 2 × 3 cells (G2), and renormalised so that the population share stays at
   the toggle. This adds a known joint without moving any other draw. Revert is one function.
3. **V2 drives arrears through the relative risk measured on energy bills, and the book's arrears rate does not
   move.** `vuln_financial_arrears_relative_risk` = 3.6 [2.8, 4.6] (CIM W5 table 159: 15.2% against 4.2% behind on
   *energy* bills). The 6614 equivalent, 4.5, counts all household bills and is the wrong quantity for an energy
   ledger. The arrears engine keeps `income_stress` as the time-varying trigger, and V2 multiplies the per-bill
   failure hazard. The two hazards are renormalised so that the population arrears share stays where it is
   calibrated (just under 5-7%, Ofgem). **Only who is in arrears moves, not how many.** That makes the build a
   one-variable change that can be attributed. The re-key is a fidelity change, so its constants are fixed before any
   company result is read.
4. **V1 and V2 stay independent.** The age evidence pulls both ways. Pensionable age is a PSR needs-code circumstance
   (V1), and the 65+ are precarious at 0.43 times the rate of the rest. Disability and chronic illness pull the other
   way. The net sign of the V1-V2 relation is not established (G4), so independence stays as the named absence of a
   number.
5. **Nothing crosses the seam that does not cross today.** V2 stays world truth (`ability_to_pay` is already on the
   payment seam's forbidden list, `interface/contracts/payment_observable_seam.py`). The company keeps reading its
   own payment method and its own arrears, and it learns tenure only if a customer says so. What the wiring changes
   is how much those observables *mean*. The company's `company/crm/affordability_inference.py` then meets a world
   in which its signals carry the measured strength and no more.

## 5. What is not known (GAP)

- **G1. V2's own strengths. CLOSED 9 Nov.** Prepayment OR 4.00, renting 4.80, on a V2-shaped target at 27.8%
  (`v2_shaped_precarity_strengths_and_the_payment_tenure_cells_understanding_society_2026-11-09.md`). The world's
  30% is inside its range, so the fallback (redefine V2 as T) is not needed.
- **G2. The joint cell table P(state | payment method × tenure).** The 6614 page publishes each flag alone. The six
  cells are not published, and multiplying single-flag odds ratios assumes no interaction, which is not measured.
  **CLOSED 9 Nov:** the six cells are published (smallest 482 households), by age band too. The flags are
  sub-multiplicative within renting and super-multiplicative for prepaying owners (35.5% observed, 27.0% from main
  effects), so the build draws the cells, not multiplied odds ratios. Under F11 its default is the under-65
  (single-instrument) structure, renormalised to the toggle; the pooled cells are the upper arm.
- **G3. Occupant age.** The world draws none, so the strongest inverse relation (65+) cannot be expressed. Drawing
  age is its own world build (it touches V1, demand and the PSR), and this page does not license it.
- **G4. The V1-V2 joint.** It needs a survey with both PSR-type circumstance and financial vulnerability on one
  record (CIM microdata, not fetched).
- **G5. Energy-specific arrears against prepayment.** The share of prepayment households carrying energy debt
  against DD households in Ofgem's debt and arrears data would be a direct check on what the wired world produces.
  It is not yet extracted.
- **G6. The direction of causation for prepayment.** In life, some households are precarious *because* they were
  moved to prepayment for debt, and some prepay *because* they are precarious. The world draws the initial channel
  as a trait, and `simulation/payment_method_dynamics.py` moves households to prepayment for debt later. Conditioning
  V2 on the initial channel captures the cross-section and does not separate the two.
- **G7. The two deprivation instruments.** Wave 14 asks working-age households about savings and replacing goods
  (36.2% V) and pensioners about a £200 unexpected expense (7.6%). Pooling them inflates prepayment's odds ratio
  from 3.24 to 4.00, because pensioners rarely prepay. How much of the age gap is the household and how much is
  the question is not separable on this file. A wave that asks one item of every age would close it.

## 6. Done means, for the build that follows (not for this page)

- With the wiring OFF, the world is byte-identical (the activation file and the draw already guarantee this).
- With it ON: the payment-channel and tenure marginals are unchanged, the V2 share equals its toggle, and the book's
  arrears share is unchanged within sampling. P(V2 | prepayment) / P(V2 | not), P(V2 | renting) / P(V2 | owner) and
  the arrears relative risk land within the intervals of their sources.
- The AUC of V2 on the company-visible (prepayment, own arrears) pair is printed with its interval and set against the
  6614 band (§3). If it is well above the band, the world is too easy, and that is a finding.
- No percentage price response varies with V2 (§3, SERL).
