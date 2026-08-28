**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `A45_the_canon_is_a_standing_subject`

# C1, C2 and C3 answered on the evidence: two confirmed, one superseded by work that landed the day before the guidance was written

Filed against `DIRECTOR_GUIDANCE_THE_WORLD_MUST_PRESS_2026-08-28.md`, WORK THIS CREATES item 1:
*"C1, C2 and C3 confirmed, corrected or rejected on the evidence, and the page brought into
line with what is true."* Filed under the canon's own binding reading rule — where the page and
the built reality disagree, surface the disagreement as a finding.

Each verdict below is `observed-with-evidence` and names the file and line it was read from
(R9). Nothing here is inferred from the page.

---

## C1 — "coupled hidden traits" — **PARTLY CONFIRMED, PARTLY SUPERSEDED**

The guidance says the three drawn traits are *"read by no live module… Mutual information is
zero, not small."* That is **true of two of the three and false of the third**, and the third
stopped being true on **2026-08-27**, the day before the guidance was drafted.

**`price_sensitivity` — SUPERSEDED. A channel exists.**
`simulation/customer_events.py` calls `price_elasticity_for_customer(billing_account,
run_base_seed())` inside the churn decision and weights the price differential by it. Two
households identical in company-observable terms and opposite in trait now churn at different
rates. The comment block at that call records the change and dates it 2026-08-27, and
`tests/simulation/test_price_sensitivity_reaches_the_price_response.py` pins it, including the
mutation that points the noise floor at the retired `price_sensitivity_for_customer` and must
go red.

**`green_stance` and `channel_pref` — CONFIRMED. No channel exists.**
Both appear in exactly three modules: `simulation/population_draw.py` (drawn),
`simulation/population_coverage.py` (coverage-tested), and
`company/analytics/cohort_discovery.py` — which is the COMPANY's inference side and reads its
own observables, never the drawn truth (`_infer_price_sensitivity(interaction_obs.
churn_estimate)`). Nothing in the world's response functions reads either. For these two the
guidance's sentence stands word for word.

**AND THE CORRECTION DOES NOT RESCUE THE CLAIM, which is the part that matters.** The channel
that now exists carries almost nothing. This seat measured overnight that the published
price-weight heterogeneity is **1.26×** between the most and least price-focused subgroups
(the director's own P3), and that price sensitivity is **structurally unlearnable** on the
current book. So the trait EXPRESSES and the expression is beneath the noise floor. "Coupled
hidden traits" is still an overstatement of what a company could ever discover — the reason has
moved from *no channel* to *a channel with no signal in it*, which is a different repair.

**What the page should say:** three traits drawn; one wired to a behaviour and two not; the
wired one carrying a between-group spread of 1.26× and no demonstrated within-household
variance. Naming the gap in the same breath as the capability is the page's own convention.

---

## C2 — "the market does not compete" — **CONFIRMED IN FULL**

Every clause checks out, and the third is the one with teeth.

- **No competitor module.** `find . -iname "*competitor*"` returns eleven paths and every one is
  a document: `docs/design/COMPETITOR_FIELD_FRAME.md`,
  `docs/design/B10_COMPETITOR_SWITCHING_RESPONSE_FRAME.md`,
  `docs/design/simplifications/B4_competitor_field.yaml`,
  `docs/market_research/f5_simulated_competitor_field.md` and seven more. No `.py` file models a
  rival supplier. The frames exist; the mechanism does not.
- **The comparison price is a published series read by date.** `simulation/svt_rates.py` is a
  literal `dict[tuple[int, int], float]` of Ofgem Default Tariff Cap quarterly rates, 2016
  onward, keyed `(year, quarter_start_month)`. It is the real published record — which is why
  it is right as HISTORY and cannot be a competitor: a table cannot respond.
- **Market position is a single run-level constant.** `simulation/customer_events.py:43` —
  `PRICE_DIFFERENTIAL_PCT = 0.0`, restated identically at
  `simulation/run_phase4c_on_phase2b.py:110`.

**One refinement the guidance's own evidence does not yet carry, and it narrows the claim
slightly rather than weakening it.** The run-level constant is now a FALLBACK, not the live
path: `customer_events` derives the differential per customer from that customer's own offered
rate against the published SVT, and only falls back to `PRICE_DIFFERENTIAL_PCT` when no rate is
to hand. So the company's own pricing does reach the churn decision per household. What still
does not exist is anything that reacts: the SVT series is fixed by date whatever the company
charges, nobody undercuts it, nobody defends, nobody targets its book. **The consequence the
guidance draws is therefore exactly right and is not softened by this** — over-pricing carries
no competitive consequence, so an expected-value maximiser correctly discovers that charging
more is close to free.

**This is the one that invalidates measurements taken before it**, including this seat's own
published baseline comparison. See "What this does to the published figures" below.

---

## C3 — "SURVIVE means not guaranteed to live" — **CONFIRMED, and it is a definition the code
cannot currently satisfy**

The director's clarification is a change to what the score MEANS, so it is not a claim to be
checked — but the sentence that follows it is: *"no mechanism that converts a bad quarter into
a liquidity constraint."* That checks out.

Collateral exists in the world as a **cost line, sized once, fixed for the term**:
`simulation/hedged_settlement.py` — *"capital cost is a term-level figure (collateral is sized
once, at term start)"*, `monthly_cost_of_capital_gbp` fixed for the term's duration. It is
subtracted from margin. It is never **called**. There is no event in which the world demands
cash at a moment the company does not control.

The company-side organs that would model the consequence —
`company/risk/counterparty_collateral_desk.py`, `company/risk/liquidity_stress_test.py`,
`company/risk/capital_adequacy.py` — exist and are imported only by
`company/interfaces/counterparty_collateral.py`. Nothing in `simulation/` imports any of them.
They are a company that can measure a squeeze in a world that cannot apply one.

So of the three mechanisms the director names, **hedging** has its cost but not its call,
**competition** is blocked entirely by C2, and **debt** is the only one with any live path — and
arrears do not currently arrive coupled to wholesale peaks. EARN has been the only leg the world
can press on, exactly as stated.

---

## What this does to the published figures, said plainly rather than found later

The guidance names one genuine cul-de-sac: *"P1 invalidates measurements taken before it."*
That bites immediately and it bites on this seat's own work, so it is stated here rather than
in a footnote.

The baseline comparison published on `/capabilities/` — flat rules £153,245, per-customer
£157,913, the level explaining 102.4% and the choosing worth −£175 with an error bar 25× the
estimate — is **a valid internal comparison between two policies and is not evidence about a
supplier's performance**. It was taken against an opponent that cannot move. Publishing it was
right; leaving it on the site without that sentence beside it would not be.

**Action taken:** it is minted as `SITE13_the_baseline_comparison_carries_its_bound` rather than asserted here, because it is
a change to a live published surface and R11 says done means the rendered value says so.

---

## WORK THIS CREATES

1. `A45_the_canon_is_a_standing_subject` — a mechanism that asks each orientation what the page claims that the
   code no longer supports. This finding was produced by hand; the guidance's own §"One addition
   to the delivery seat's subjects" says that is the director's job only because nothing does it.
2. the page edit, landed in this commit — the page edited to carry C1's split verdict, C2 in the
   `"moneyness trigger absent — known"` form the page already uses, and C3's replacement of the
   mortality framing.
3. `SITE13_the_baseline_comparison_carries_its_bound` — the published comparison states, on the
   rendered page, that it compares two internal policies in a market that could not react.

## Still live

---

## DISPOSITION — 2026-08-28, scheduled tick (all three WORK THIS CREATES items closed or minted)

1. **`A45_the_canon_is_a_standing_subject` — BUILT, level 0→2.** `tools/canon_drift_check.py` +
   the claim register `docs/design/canon_claims.yaml` + 32 tests
   (`tests/tools/test_canon_drift_check.py`), wired into the daily self-note so something other
   than the director asks the question each morning. Nine claims registered: C1's three, C2's two,
   C3's two, and two against the RENDERED schematic. R15 both ways —
   `test_a_channel_that_disappears_reports_over_claim` and
   `test_a_channel_that_appears_reports_superseded`; the second is the mutation a one-directional
   check cannot pass, and it is C1's own shape.
2. **The page edit — LANDED** (and then immediately corrected again, see below).
3. **`SITE13_the_baseline_comparison_carries_its_bound` — minted**, unchanged, still open.

**The check's first live run found this finding's own C2 verdict already stale.**
`simulation/competitor_reference.py` landed the same day and is wired into
`customer_events` — a rival that follows a company down over quarters, floored at its own cost
stack, on a lag the company does not control. So "no module models a rival supplier" was
SUPERSEDED within hours of being confirmed in full, exactly the direction this finding warned a
one-directional drift check would miss. THE_MODEL_ON_A_PAGE.md now reads "the market DEFENDS but
does not yet CONTEST", and keeps the part that did not change: the company still cannot price
above the cap, so over-pricing still carries no competitive consequence, and every pricing
measurement taken before 2026-08-28 was taken against an opponent that could not move.

**Second live finding, minted as `SITE14_the_front_door_schematic_carries_the_corrected_model`:**
the canon page carries C1 and C3; `site/index.html` — what a reader actually sees — still says
"coupled hidden traits" and "it can be wrong, and it can die". Both OVER_CLAIM. The check stays
RED on those two until the schematic is regenerated, deliberately and not wired to any gate: a
red pre-commit control here would wedge the tree, and this one is an orientation instrument.
