**Severity:** LATENT · **Lane:** W2_customer_generator · **Atom:** the value arm's reach

# The SVT conversion decision is a real per-household decision — and this world has no edge that can express its outcome, so the desk would have been a company arm the world cannot register

**Answered:** 2026-09-18, delivery seat, claim
`the-svt-conversion-decision-is-the-population-the-thesis-needs`.

**The question, as drawn.** Over the 2,490 renewals `decisions.why_the_rest_were_not_priced`
classes as `product_not_upliftable` (all 2,490 on `svt`, 88.17% of the renewals the world offered
— `site/data/value_arms.json`), establish **(a)** whether the SVT-to-fixed CONVERSION decision is
one a real UK supplier makes per-household on observables, from the published record rather than
from reasoning; and **(b)** whether THIS world can answer it, by naming the code path through which
an SVT household's behaviour responds to an offer, or stating plainly that no such path exists.

**Prior art, followed rather than re-derived.**
`docs/staging/done/SEAT_DECISION_AN_SVT_HOUSEHOLD_IS_NOT_A_DECISION_THIS_ARM_DECLINES_2026-09-07.md`
§3 NAMED this desk and §5 item 4 filed it as owed. It did not establish either half. This document
is that establishment, and it does not disturb §3's ruling: the arm's refusal at an SVT boundary
is still correct and `UPLIFTABLE_TARIFF_TYPES` is not to be relaxed.

---

## 1. The answer in one paragraph

**(a) YES — and the decision splits in two at April 2022, which the drawn item did not anticipate.**
Internal switching (taking a deal with your existing supplier) is a separately-coded, separately-
measured GB behaviour running *larger* than external switching, and the targeting of it conditions
on fields a supplier already holds. But SLC 22B removed the supplier's per-household discretion over
the PRICE from April 2022, leaving discretion over WHO TO CONTACT and nothing else. So the desk a
real supplier runs post-2022 is a **targeting desk, not a pricing desk**.

**(b) NO PATH EXISTS — and not for one reason but for three, each independently sufficient, the
deepest of which is that the OUTCOME has no representation.** An SVT household in this world cannot
be offered anything, cannot respond to an offer if one were fabricated, and — decisively — cannot
end up on a fixed term, because `tariff_type` is resolved once per customer at schedule-build time
and SVT is an absorbing state with no reverse edge.

**Decision recorded in §5: DO NOT BUILD THE DESK.** The world-side edge is prior to it, belongs to
the world lane, and must be decided on fidelity grounds blind to company results (R13).

---

## 2. (a) What a real supplier decides — from the published record

### 2.1 The behaviour exists, is measured, and is the LARGER half

Ofgem's *Consumer Impacts of Market Conditions* survey question C4 carries **"I/we have switched
tariff with the same supplier"** as its own response code, on the same base as **"I/we have switched
to a new supplier"**. Read from the wave-6 data tables, sheet `W2W Tables`, Table 108
(`docs/market_research/gb_domestic_switcher_split_cim_2022_2025.md` §1–§2):

| wave | fieldwork | switched **supplier** | switched **tariff, same supplier** |
|---|---|---|---|
| W1 | March 2022 | 9.32% | **13.18%** |

Internal switching is not a residual or an inference. It is the bigger of the two codes in the first
wave, on a base of all respondents, and it is **reported behaviour, not intention** — the wave-6
intention series is deliberately not used here, for the reason §1 of that note gives.

The conversion decision's population is likewise established and large: ~65% of a domestic book
rolls to SVT by default rather than actively renewing, pre-crisis
(`svt_rates_active_passive_2016_2025.md` §2, M on the specific 35/65 split, H on the direction), and
the all-domestic default share ran ~58–90% across 2016–2025
(`gb_domestic_default_tariff_share_2016_2025.md`, per-year bands; 2020 and 2021 a declared gap).

### 2.2 What is per-household on observables: the TARGETING, and it is worth ~3×

`what_a_supplier_can_observe_about_switching_propensity_cim_w6.md` §3 reads the same workbook's
demographic banner (Table 56) restricted to fields a GB supplier holds on its own book. Against a
5.3% population base rate for having switched supplier in the past six months:

| field the supplier holds | reading | vs base |
|---|---|---|
| tariff type — **variable** | 2.5% | **0.47×** |
| tariff type — fixed | 7.0% | 1.32× |
| payment method — traditional PPM | 1.7% | 0.32× |
| payment method — direct debit | 5.6% | 1.06× |
| arrears — "getting harder" | 6.8% | 1.28× |
| **satisfaction — DISSATISFIED** | **3.0%** | **0.57×** |

So yes: propensity varies by ~3× across things a supplier meters or sets rather than infers, which
is what makes targeting a per-household decision rather than a broadcast. Two cautions carried from
that note's own §5 rather than discovered later: these are **marginals, not a model** — tariff-type
and payment-method populations overlap heavily and the banner cannot say how much of the 2.8× and
3.4× is one variation counted twice; and six months is not a year, on one wave.

**And the satisfaction row runs backwards.** Dissatisfied households switch at little more than half
the rate of satisfied ones. A conversion desk built on the naive relation would target exactly the
households least likely to move.

### 2.3 What is NOT per-household after April 2022: the price

`docs/institutional/knowledge_map.md`, row *Retention offers (SLC 22B)*, H confidence:

> A retention offer is a TARIFF, not a cash payment: margin sacrificed, landing in revenue. Ofgem's
> Ban on Acquisition-only Tariffs (SLC 22B) has since **April 2022** barred new-customer-only fixed
> deals; retention-only deals are permitted by the BAT's **Market-wide Derogation at end of fixed
> term.** MSC ended 31 Mar 2024; BAT extended annually, proposed to 31 Mar 2027.

Read against this population, that has a consequence the drawn item did not anticipate and it is the
finding of half (a):

- **An SVT household is not at the end of a fixed term.** The derogation that permits a
  retention-only deal is keyed to that moment, and the conversion decision happens away from it.
- **So any fixed tariff the supplier offers must be open to its own SVT book too.** Post-April-2022
  the supplier's discretion is over *whom it approaches, when, and through which channel* — not over
  the rate it approaches them with.
- **The 2016–2025 window is therefore two regimes for this desk, not one**, and a desk trained
  across it without the split would learn a price lever that ceased to exist in April 2022. The
  knowledge map's own gap column already says the sim "applies one set of retention physics across
  2016-2025 and does not model the 2022 discontinuity".

One more binding constraint, same file, row *Customer comms and renewal lifecycle* (SLC 22A): a
supplier **cannot auto-rollover a household to a new fixed deal — it must default to the cheapest
SVT**. Conversion requires the household's active consent. The supplier proposes; it cannot move
anyone.

`docs/domain_artefact_library/regulatory/pricing_differentiation_permissions.md` was read for a
prohibition on differentiating the *approach* itself and carries none: §D1 records that withholding
a low-margin fixed tariff from a poor credit risk has **no prohibition found** (SLC 27.1 governs
payment METHODS, not products), constrained in practice by SLC 0.3 fairness. That is a
`UNSOURCED`-adjacent status and is reported as the register reports it, not upgraded.

---

## 3. (b) The code path, named — and there is none

Three reasons. Each alone is sufficient; they are given in increasing order of how hard they are to
repair.

### 3.1 No offer is emitted at an SVT segment boundary

`simulation/svt_product.py:224` `build_svt_schedule` emits one segment per cap period, and its own
docstring says what each field is for (lines 28–32, 247–252):

> *"…is a price change, not an expiry: nothing is renewed, **nothing is offered**, and the household
> …"* · *"`notice_date` equals the segment start; there is nothing to give notice of."* ·
> *"`unit_rate_gbp_per_mwh` is the published cap rate for the period, not a struck price. No company
> module is asked to price it, because no supplier prices a capped default tariff."*

There is no `request_renewal_offer` call anywhere in the module. `run_phase2b.build_customer_schedule`
returns `build_svt_schedule(...)` wholesale at lines 708–712 and never enters the term loop that
would strike a rate. **A company arm has no seam at which to hand this household anything.**

### 3.2 Even if an offer were fabricated, the parameter carrying it is arithmetically inert here

`simulation/departure_risks.py:343–346` — `retention_offer_retained_fraction` multiplies
`CAUSE_PRICE_POSITION` **and nothing else**, deliberately (P6: "a discount cannot retain a
service-driven churner"). The SVT branch at `run_phase2b.py:2010–2018` passes `price_response=0.0`,
`bill_shock_base=0.0`, `dissatisfaction_response=0.0` and `svt_inertia=_svt_hazard`, so the only
hazard the offer can reach is identically zero.

Driven at the branch's own inputs (`action_propensity=0.8635`, the book's measured mean;
`level_anchor=2.5`; `svt_inertia=0.0547`, one real 92-day cap quarter), **before writing anything**:

```
  retained_fraction=1.0    p_depart=0.047233   {bill_shock 0.0, price_position 0.0, dissatisfaction 0.0, svt_inertia 0.047233}
  retained_fraction=0.75   p_depart=0.047233
  retained_fraction=0.5    p_depart=0.047233
  retained_fraction=0.25   p_depart=0.047233
  retained_fraction=0.0    p_depart=0.047233
```

Identical to six decimal places across the entire range, including a total offer
(`retained_fraction=0.0`). The same parameter on the renewal route, for contrast — same anchor, a
neutral household:

```
  retained_fraction=1.0    p_depart=0.141621
  retained_fraction=0.5    p_depart=0.126457
  retained_fraction=0.0    p_depart=0.111293
```

**The two live call sites are disjoint and no caller in the tree passes both arguments.**
`simulation/customer_events.py:733,743` passes `retention_offer_retained_fraction` and takes
`svt_inertia`'s 0.0 default; `simulation/run_phase2b.py:2010` passes `svt_inertia` and takes
`retention_offer_retained_fraction`'s 1.0 default. The offer machinery and the SVT machinery have
never been in the same call.

### 3.3 The OUTCOME has no representation — SVT is an absorbing state

This is the one that decides the build question, and it is prior to the other two: even a fully
wired offer with a live behavioural response could not produce the thing the desk exists to produce.

- `tariff_type` is resolved **once per customer**, at schedule-build time, from the population draw:
  `run_phase2b.py:1571` / `:1591` call `resolved_tariff_type(c)` and hand the answer to
  `build_customer_schedule`. Nothing downstream rewrites it; `run_phase2b.py:2154` stamps
  `term_tariff_type` onto the settled record from the term the builder already emitted.
- The **fixed → SVT** edge exists mid-tenure: `run_phase2b.py:747–759`, a resi fixed household that
  fails `rolls_active_renewal` has its remaining decade rebuilt by `build_svt_schedule`.
- **There is no reverse edge.** `build_svt_schedule`'s loop (`svt_product.py:309–363`) runs
  `while segment_start <= report_end` emitting `"tariff_type": SVT_TARIFF_TYPE` on every segment and
  returns. No branch inside it can emit a fixed term, and no caller re-enters the term builder for a
  household already on SVT.

**So "this household accepted our fixed deal" is not a state this world has.** The best a perfectly
instrumented conversion desk could achieve is to lower a hazard; it could never move a household
onto the product that makes it a renewal decision in the first place — which is precisely the thing
that would grow the 279-row decision population the arm is measured on.

### 3.4 A consequence worth naming separately, because it is a fidelity reading

The world's `CAUSE_SVT_INERTIA` is an **unconditional departure**: the household leaves the book.
There is no state in which an SVT household leaves the SVT *product* and stays with the company.
`SVT_INERTIA_ANNUAL_RECENT = 0.20` / `_LONG_STAYER = 0.10` come from
`svt_rates_active_passive_2016_2025.md` §4, whose own heading is "SVT Churn Rates (**Structural
Inference**)" — "Direct published SVT vs fixed churn rates by tariff type are not available",
confidence M on every row, and the basis column cites engagement surveys rather than a loss series.

Against §2.1, where the published instrument separates the two codes and reports the internal one as
the larger: **this world routes the entire drift off SVT to one absorbing exit.** Whether the 0.10 /
0.20 anchor was ever meant to count only supplier-to-supplier losses is not settled by its source,
and that is stated rather than resolved here — it is a world-lane question, on fidelity grounds, and
I am not the lane that gets to answer it.

---

## 4. What each number counts, before anything is divided

Stated because this population has been mis-divided twice already (`SEAT_DECISION…2026-09-07` §4):

- **2,490** counts *term boundaries emitted by `build_svt_schedule`* — cap revisions. It is not a
  count of households, not a count of offers declined, and not a count of decisions.
- **13.18%** counts *respondents reporting an internal switch in six months*, on the CIM base of all
  domestic respondents. It is not an annual rate and not a per-boundary conversion probability.

These two do not divide into each other in either direction, and nothing below rests on their ratio.

---

## 5. The decision, with its reason

**REFUSE. Do not build the SVT conversion desk, and do not schedule it.**

The drawn item anticipated this outcome and said why it is worth more than the desk: it stops us
building a better-instrumented null, which is what `C29`'s own `block_reason` warns of. §3.3 makes
that concrete rather than cautionary. A conversion desk built today would emit per-household
targeting decisions into a world in which:

1. no household can be handed an offer (§3.1),
2. no household's hazard would move if one were (§3.2), and
3. **no household could convert even if it did** (§3.3).

Its measured lift would be exactly zero by construction, on every seed, forever — and an arm whose
null is structural is worse than no arm, because its zero reads as a result about the method.

**What is prior to the desk, and whose it is.** One world-side edge: an SVT household must be able
to reach a fixed term. That is a **fidelity** question about the baseline world, decided blind to
company results under R13 and the baseline/curriculum split, and it belongs to the world lane and
not to a company arm. The published warrant for opening it is §2.1 — the GB record separates
internal from external switching and reports the internal half as the larger, while this world's
internal-switch rate is structurally 0.0 and cannot be otherwise. **That warrant is recorded here;
the determination is not mine to make and is not made here.**

**What is NOT to be done as a shortcut**, stated because each is the shape this project has paid for
before:

- Do not relax `UPLIFTABLE_TARIFF_TYPES` so the SVT book counts. `SEAT_DECISION…2026-09-07` §6
  already refuses this; it moves a divisor on a page and nothing the company does.
- Do not wire `retention_offer_retained_fraction` into the SVT branch to make §3.2 go away. It would
  make an offer *look* effective by lowering a hazard while §3.3 still holds, which is a company
  lever with no outcome behind it — an unmodelled world, not a harder one.
- Do not treat §3.4 as licence to split the 0.10 / 0.20 anchor into internal and external legs by
  applying the CIM 9.32 / 13.18 ratio. That ratio is one wave, six months, all domestic respondents,
  and the anchor is a structural inference over the SVT segment. Two populations, two instruments;
  differencing them would mint exactly the kind of constant this file exists to avoid.

**Reversal.** Nothing was built, so there is nothing to reverse. If the world lane lands the SVT →
fixed edge on fidelity grounds, this refusal is discharged and the desk becomes an ordinary question
of sequencing — re-read §2.3 first, because the desk it would then be is a targeting desk from April
2022 onward and a targeting-and-pricing desk before it.

---

## 6. Not a target

R12. The 2,490 is not a number to reduce and 88.17% is not a share to improve. Both are readings of
GB's product mix, which is a published fact about the market and not a result of this company.
