# What a GB supplier's conversion decision at a default-tariff boundary actually is

**Knowledge:** acquisition-and-retention-economics

**Filed 2026-09-19, delivery seat, claim `what-a-conversion-decision-is-at-a-cap-boundary`.**
Knowledge artefact. **No code, no constant, no arm change was made under this item** — it establishes
what the decision IS, from the published record, before anything is built that assumes it.

**Row in** `docs/institutional/knowledge_map.md`, *SVT→fixed conversion at a cap boundary*.

---

## 0. The answer in five lines, and the verdict the item asked for

1. **The decision is a TARGETING decision, not a pricing one** — from April 2022 (SLC 22B). Before
   that it was targeting *and* pricing. The 2016–2025 window is two regimes.
2. **The company may know all four fields the published record says targeting conditions on** — but
   by three different routes with three different epistemic standings, and only one of them is the
   `sim_interface` wall. §2.
3. **The response rate is a NAMED GAP inside a published TWO-SIDED BAND**, not a number:
   `SVT_INTERNAL_CONVERSION_RATE = None`; **0.0449 ≤ J_svt ≤ 0.2659** per SVT household per six
   months, and **the floor is the live side**. §3.
4. **The cost to perform is a GAP with no reachable citation at all**, and the repo already carries
   an uncited cost table that disagrees with the uncited research table. §4.
5. **VERDICT: a conversion desk is a NEW capability beside the standing decision, not a
   contradiction of it** — and the 2026-09-18 refusal is **discharged by its own stated condition**,
   which was met on 2026-09-19. §5.

---

## 1. Q1 — What a supplier may lawfully do at a cap boundary, and what it owes

**Established, confidence H.** Sources are the licence conditions themselves, already read into this
repo; this section points rather than re-derives.

| the act | permitted? | what is owed |
|---|---|---|
| Change the SVT rate at the boundary | **Not the supplier's act.** 2019 onward the rate is the Ofgem default tariff cap, set per region, payment method and consumption level | nothing — no notice, no offer, no struck rate |
| Approach an SVT household with a fixed deal | **Yes** | see the two constraints below |
| Move that household onto the fixed deal | **No, not unilaterally** | SLC 22A: **no auto-rollover**; must default to cheapest SVT. Conversion needs the household's **active consent** |
| Offer it a rate not open to new customers | **No, from April 2022** | SLC 22B (Ban on Acquisition-only Tariffs) |

**The April 2022 split is the finding of this question and it is easy to get backwards.** The BAT's
Market-wide Derogation permits retention-only deals **at end of fixed term**. An SVT household is
*not* at the end of a fixed term — the conversion decision happens away from that moment — so the
derogation does not reach it. From April 2022 any fixed tariff the supplier offers must be open to
its own SVT book too.

**Therefore: discretion survives over WHOM to approach, WHEN, and through WHICH CHANNEL — and not
over the rate.** A desk trained across 2016–2025 without the regime split would learn a price lever
that ceased to exist in April 2022.

Pre-2019 SVT rates were supplier discretion, but a *published tariff-level* rate per supplier and
region (Ofgem SVT league tables) — never a per-household strike
(`svt_rates_active_passive_2016_2025.md` §1, confidence M, ±15%).

**One status carried as the register reports it, not upgraded:**
`docs/domain_artefact_library/regulatory/pricing_differentiation_permissions.md` §D1 was read for a
prohibition on differentiating *the approach itself* and carries **none** — withholding a low-margin
fixed tariff from a poor credit risk has **no prohibition found** (SLC 27.1 governs payment METHODS,
not products), constrained in practice by SLC 0.3 fairness. That is `UNSOURCED`-adjacent.

Fuller working: `docs/staging/WORKER_FINDING_THE_SVT_CONVERSION_DECISION_IS_REAL_AND_THIS_WORLD_HAS_NO_EDGE_THAT_CAN_EXPRESS_ITS_OUTCOME_2026-09-18.md` §2.3.

---

## 2. Q2 — What the company may OBSERVE about that household at that moment

This is the epistemic-wall question. **Measured at HEAD on 2026-09-19 against the real files, not
quoted from a prior document.**

The published record says targeting is worth ~3× across four fields a supplier holds
(`what_a_supplier_can_observe_about_switching_propensity_cim_w6.md` §3; Ofgem CIM w6 Table 56
demographic banner, against a 5.3% population base rate for having switched supplier in six months):

| field | reading | vs base |
|---|---|---|
| tariff type — **variable** | 2.5% | **0.47×** |
| tariff type — fixed | 7.0% | 1.32× |
| payment method — traditional PPM | 1.7% | 0.32× |
| payment method — direct debit | 5.6% | 1.06× |
| arrears — "getting harder" | 6.8% | 1.28× |
| **satisfaction — DISSATISFIED** | **3.0%** | **0.57×** |

**All four are reachable company-side. The wall is not the binding constraint here — but the four
arrive by three different routes and conflating them is how this gets built wrong:**

| field | route | epistemic standing |
|---|---|---|
| **tariff type** | the company's **own CRM record** — `company/crm/customer_registry.py:98`, a `tariff_type` column on the account table | **Strongest. It does not cross the wall at all**, and should not: a supplier knows what product it sold. Asking the world would be the defect |
| **payment method** | **crosses the wall** — `company/interfaces/sim_interface.py:175` `get_payment_method` | Explicitly justified in its own docstring: *"a supplier SET THIS ARRANGEMENT UP… A supplier that could not see its own payment channels could not bill."* Ofgem's cap is itself set per payment method |
| **arrears** | company-side billing — `company/billing/arrears_engine.py`, `account_ledger.py`, `crm/affordability_inference.py`, `crm/credit_scoring.py` | Company's own ledger. Does not cross the wall |
| **satisfaction, tenure, consumption, bill-shock count** | **arguments** to `get_churn_estimate` (`sim_interface.py:231–241`) | Weakest. The seam does **not fetch** these — the caller must already hold them. A door that takes a field is not a door that supplies it |

**The seam gap that a conversion desk would actually hit, and it is not an observation gap:**
there is **no door on the base `SimInterface` contract to record a conversion approach or its
outcome.** `notify_retention_attempt` is defined on `StubSimInterface` (line 378) and
`LiveSimInterface` (line 562) and is **absent from the base class** (lines 141–300, whose full
method list is `get_settlement_data`, `get_forward_price`, `get_customer_status`,
`get_payment_method`, `notify_churn`, `notify_acquisition`, `get_churn_estimate`, `enrol_flex`,
`flex_enrolment_book`, `get_flex_settlement_lines`). The act the desk exists to perform has two
implementations and no declared contract.

**And the satisfaction row runs BACKWARDS.** Dissatisfied households switch at little more than half
the rate of satisfied ones (3.0% vs a 5.3% base). A conversion desk built on the naive relation —
"approach the unhappy ones" — would target exactly the households least likely to move.

**Two cautions carried from that note's own §5 rather than discovered later:** these are
**marginals, not a model** — tariff-type and payment-method populations overlap heavily and the
banner cannot say how much of the 2.8× and 3.4× is one variation counted twice; and **six months is
not a year, on one wave.**

---

## 3. Q3 — How such households respond when approached, and over what population

**This is a NAMED GAP inside a published TWO-SIDED BAND. The rate itself is not established and no
point estimate is offered here.**

```
tools/published_route_split.py:1443   SVT_INTERNAL_CONVERSION_RATE = None
tools/published_route_split.py:1453   svt_internal_conversion_floor()
tools/published_route_split.py:1546   svt_internal_conversion_ceiling()
```

Run at HEAD, 2026-09-19 — the per-wave floors, and the binding one:

| wave | fieldwork | internal rate, 6mo, all households | ceiling on the renewal route | floor on J_svt |
|---|---|---|---|---|
| W1 | March 2022 | 0.1318 | 0.070 | 0.0687 |
| W2 | July 2022 | 0.1248 | 0.070 | 0.0609 |
| W3 | Nov/Dec 2022 | 0.1449 | 0.070 | 0.0832 |
| **W4** | **July 2023** | **0.1104** | **0.070** | **0.0449 ← binding** |
| W5 | January 2024 | 0.1159 | 0.070 | 0.0510 |

**`binding_floor = 0.0449`. State it with its population or do not state it:** it is a **derived
lower bound**, per **SVT household**, per **six months**, being the minimum across waves — the rate
*every* wave independently establishes. It is **not** an annual rate, **not** a per-boundary
conversion probability, and **not** a measured response-to-approach.

**The band is two-sided, and which side is live has already inverted once — so do not carry only
the floor.** `svt_internal_conversion_ceiling()` takes the same identity
(`I = s·J_svt + (1−s)·0.35·(1−φ)` ⇒ `J_svt ≤ I/s`) at φ=1, with **every conservative choice
inverted** — smallest default share not largest, max across waves not min:

| bound | value | unit | binding at | notes |
|---|---|---|---|---|
| floor | **0.0449** | per SVT household / 6 months | W4 (Jul 2023) | min across waves |
| ceiling | **0.2659** | per SVT household / 6 months | W6 | **un-annualised, and therefore NOT a valid ceiling per household-YEAR** |
| ceiling, tariff-banner | **0.2389** | per SVT household / 6 months | — | Table 109 records tariff type *after* the move; that contamination runs the SAFE way for an upper bound only |

**The floor is the live side.** The world sits at 1.11–4.14× the floor against 0.35–0.70 of the
ceiling. The six-month convention also inverts the verdict's direction: *below the ceiling* is an
established verdict and *above* establishes nothing, so the world's above-ceiling years are where
the bound is live rather than where it has fired.

**Both are CHECKS on what a world produces, never values to set one to.**

**What the underlying instrument counts, before anything is divided.** Ofgem's *Consumer Impacts of
Market Conditions* survey question C4 carries **"I/we have switched tariff with the same supplier"**
as its own response code, on the same base as **"I/we have switched to a new supplier"** (wave-6
data tables, sheet `W2W Tables`, Table 108 — `gb_domestic_switcher_split_cim_2022_2025.md` §1–§2).
At W1 the internal code ran **13.18%** against the external **9.32%** — internal switching is the
**larger** of the two and is **reported behaviour, not intention**. But:

> **13.18% counts respondents reporting an internal switch in six months, on the CIM base of ALL
> domestic respondents. It is not a rate over SVT households and it is not an annual rate.**

The floor above is what you get *after* dividing that population down onto the SVT segment by the
largest published default share and the renewal-route ceiling — which is why the floor (0.0449) and
the survey reading (0.1318) are different quantities and must never be swapped for each other.

**The population the decision applies to is separately established:** ~65% of a domestic book rolls
to SVT by default rather than actively renewing, pre-crisis (`svt_rates_active_passive_2016_2025.md`
§2, M on the 35/65 split, H on the direction); all-domestic default share ran ~58–90% across
2016–2025 (`gb_domestic_default_tariff_share_2016_2025.md`, per-year bands; **2020 and 2021 a
declared gap**).

**What is NOT established and is named here as a gap:** the **response rate to a supplier-initiated
approach**. Every figure above measures households that *switched*, by whatever prompting. Nothing
in the published record isolates "we contacted this household and it converted". The floor bounds
the behaviour, not the campaign.

---

## 4. Q4 — What the act costs to perform

**GAP. There is no citation in this repository reachable from any cost figure for a customer
contact, and the two tables that exist disagree.** Recorded as an honest `None` with a named reason
rather than a plausible number.

**What exists, and why neither is admissible:**

1. `docs/market_research/company_customer_comms.md` §7 — "Cost per contact (**UK benchmark**)":
   phone/agent £5–£12, webchat/email £2–£5, self-serve £0.10–£0.50. The document carries a
   **doc-level** source line ("Ofgem SLC 22A/22B, Ofgem Consumer Standards Dec 2023, Energy UK,
   Citizens Advice, KPMG CLV"). **None of those attaches to this table**, and no per-row citation
   exists. By this item's own insufficiency test — *"quotes a cost with no citation reachable from
   the row"* — quoting these figures would fail the artefact. So they are not quoted as established.

2. `company/crm/contact_journey.py:71` `_CHANNEL_COST_PENCE` — EMAIL 0.2p, SMS 4.0p, POST 80.0p,
   **PHONE 350.0p**, IN_APP 0.0, WEB_PORTAL 0.0. **No origin comment. No production caller** — the
   only importers in the tree are `tests/company/crm/test_contact_journey.py` and
   `tests/company/test_phase_iq_coverage_expansion.py`.

**These two disagree, and the disagreement is the evidence neither is sourced.** £3.50 for a phone
contact sits **below** the £5–£12 "benchmark" in the research note. Two uncited numbers for one
quantity, differing by ~1.4× to ~3.4×, reached by no production code.

**The one adjacent figure that IS sourced is not this quantity and must not be substituted for it:**
Ofgem's cap operating-cost allowance of **£97/customer/year** (2025 decision) is a *whole-year,
all-activity* allowance, not a per-contact cost. Dividing it by a contact count would be a quantity
that counts nothing — the shape this project has published before.

**So: cost-to-perform is `None`, reason "no per-row citation exists in the commons or the research
layer for a GB domestic customer contact cost; two uncited repo figures disagree."** A conversion
desk that needs this number needs it *researched first*, and it is the cheapest of the four
questions to close.

---

## 5. The verdict: NEW capability, not a contradiction — and the refusal is discharged

The item required a plain answer. **A conversion desk is a NEW capability beside
`SEAT_DECISION_AN_SVT_HOUSEHOLD_IS_NOT_A_DECISION_THIS_ARM_DECLINES_2026-09-07.md` §3. It does not
contradict it, and §3 was the document that NAMED it.**

- §3 says `renewal_margin_uplift` has no decision to make at an SVT boundary and its refusal there
  is **correct**, because that arm moves a *struck unit rate* and no such rate exists on SVT. That
  stands, untouched. A conversion desk does not move a struck rate; it decides **whom to approach**.
  **Different desk, different object, no conflict.**
- §5 item 4 of that same decision filed the conversion desk as **owed work** — *"an owed desk: the
  SVT conversion decision… the single largest unexercised commercial surface in the run."*
- **`UPLIFTABLE_TARIFF_TYPES` is not to be relaxed** and nothing here asks for it. That remains
  refused by §6 of the 09-07 decision: it moves a divisor on a page and nothing the company does.

**The 2026-09-18 refusal to BUILD the desk is now discharged, by the condition it set itself.** That
finding refused on three independently sufficient grounds, the decisive one (§3.3) being that SVT
was an **absorbing state** with no reverse edge, so no household could convert even if offered. It
wrote its own release: *"If the world lane lands the SVT → fixed edge on fidelity grounds, this
refusal is discharged."*

**Re-measured at HEAD, 2026-09-19 — the edge landed, on fidelity grounds, in the world lane:**

| commit | ancestor of HEAD | what it did |
|---|---|---|
| `05684780e` | **yes** (verified) | *feat(world): the household that ARRIVED on the default tariff gets the same exit the rolled one has* |
| `b721b6acf` | **yes** (verified) | *knowledge(J_svt): the rate a default household converts at is a named gap, and the record still establishes a floor* |

The landed implementation splits `product` from `tariff_type` so that the arrival fact is not
overwritten — and `b721b6acf` is where `SVT_INTERNAL_CONVERSION_RATE = None` and the floor in §3
come from. **§3.3's "absorbing state" is FALSE at HEAD and this document says so beside the claim
rather than quietly dropping it.**

**What that does and does not license.** It discharges the refusal's decisive ground. It does
**not** discharge the other two, which are separate work and are restated here as owed:

1. **§3.1 — no offer is emitted at an SVT segment boundary.** `build_svt_schedule` emits one segment
   per cap period and contains no `request_renewal_offer` call. A company arm still has no seam at
   which to hand this household anything.
2. **§3.2 — `retention_offer_retained_fraction` is arithmetically inert on the SVT branch.** It
   multiplies `CAUSE_PRICE_POSITION` and nothing else, and the SVT branch passes
   `price_response=0.0`. Driven across its whole range the departure probability was identical to
   six decimal places, including at a total offer.
3. **Plus the seam gap this document adds: `notify_retention_attempt` is on no base contract** (§2).

**Explicitly NOT licensed, because each is a shortcut this project has paid for:**

- **Do not wire `retention_offer_retained_fraction` into the SVT branch to make §3.2 go away.** It
  would make an offer *look* effective by lowering a hazard, which is a company lever with no
  outcome behind it.
- **Do not split the 0.10/0.20 SVT inertia anchor into internal and external legs by applying the
  CIM 9.32/13.18 ratio.** One wave, six months, all domestic respondents, against a structural
  inference over the SVT segment — two populations, two instruments. Differencing them would mint
  exactly the constant this file exists to avoid.
- **Do not set the world to the floor.** `svt_internal_conversion_floor`'s own docstring: *"NOT a
  parameter to set the world to."* It is a CHECK, and a check that reached the thing it judges would
  stop being evidence of anything.

---

## 6. What a reader can now say, and what remains unanswered

**Can say:** the decision is *whom to approach, when, through which channel* (and, before April
2022, at what rate); the company may know tariff type from its own CRM, payment method across the
wall, arrears from its own ledger, and satisfaction only if a caller already holds it; the desk is a
new capability the 09-07 decision itself named as owed.

**Named gaps, each an honest `None` rather than a number:**

| # | gap | why it is not a number |
|---|---|---|
| G1 | **response rate to a supplier-initiated approach** | Published record measures households that switched, not campaigns that converted. The band 0.0449–0.2659/SVT household/6mo bounds the behaviour, not the approach |
| G2 | **cost per contact** | No per-row citation anywhere; two uncited repo figures disagree (§4) |
| G3 | **default share 2020, 2021** | Declared gap in `gb_domestic_default_tariff_share_2016_2025.md` |
| G4 | **whether SVT inertia 0.10/0.20 was ever meant to count supplier-to-supplier losses only** | Its source is headed "Structural Inference" and cites engagement surveys, not a loss series. A world-lane question on fidelity grounds |
| G5 | **offer-emission seam and outcome-recording contract** | §5 items 1 and 3 — engineering, not research |

**G2 is the cheapest to close and the most likely to be invented under time pressure.** It is the
£150-CAC shape exactly: a number picked because a number was needed.

## 7. Not a target

R12. None of the counts here is a thing to improve. The default share, the 65/35 passive/active
split and the internal-switching rate are readings of GB's market, which are published facts and not
results of this company. The floor is a check on the world's fidelity, not a level to reach.
