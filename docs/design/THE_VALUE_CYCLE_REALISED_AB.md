# The value cycle — the realised A/B, and why it is the only honest score

**Director, 2026-08-26, handing over the one thing he had reserved:** *"if it passes, start the
value cycle — the per-customer decision engine the whole thesis rests on. That was the one thing
reserved to me and I'm giving it to you now."*

**Entry evidence:** `docs/design/EPOCH2_EVIDENCE_2026-08-26.md` — five of six questions pass; Q4
fails and is recorded as bounding publication rather than construction.

## The thesis, stated as a measurable claim

A supplier deciding customer-by-customer on what it can infer beats a flat-rules baseline
**through better prediction and nothing else.** Three things have to be true for that sentence to
mean anything, and exactly one of them is currently unproven:

| | status |
|---|---|
| A per-customer decision exists | `company/pricing/value_based_renewal.decide_margin` — 263 accounts, 187 distinct margins |
| A baseline exists to beat | `decide_margin(arm=FLAT_RULES)` — this company's own flat £2.00/MWh, imported not restated |
| **The decision beats the baseline** | **not measured, and cannot be measured the way it is currently reported** |

## Why the existing comparison cannot answer it, in the module's own words

`company/pricing/value_based_renewal.py`, closing its own docstring:

> It does not show that pricing on value earns more. It cannot: the objective is built from the
> company's own beliefs, so scoring the arms on EXPECTED value would let the value arm win by
> construction — it maximises the very number it would be judged on, which is R15's tautology
> pattern with money in it. The only honest comparison is REALISED: the same book, the same
> world, run once per arm, scored on what actually happened. That needs two runs and it is the
> next step, not this one.

`tools/couple_value_based_pricing.py` says the same thing from the other side, and it is right to.
Today's artefact (`docs/observability/value_based_pricing_arms.json`) reports **decisions**, never
**earnings**, and refuses to be read as evidence of inference at all while its two sides share a
calibration source.

**So the value cycle is not "wire the arm up". It is "close the loop": decide → act → let the
world answer → score what actually happened.** The decision half is built. The world's answer is
the half that has never been taken.

## The instrument

Run the identical world twice — same seed, same weather, same prices, same population draw — and
change exactly one thing: which arm sets the renewal margin.

```
run A   arm = flat_rules    (today's company, frozen)
run B   arm = value_based   (the same company, deciding per customer)
```

Score on what the world did, not on what the company believed:

- realised net margin, on all three clocks (R14: settled / billed / banked)
- book at end of period, and churn events in between
- bad debt, because a higher price changes who pays
- revenue and volume, so a win can be attributed to price or to retention

**The gap between the two runs is the score, and it is allowed to be negative.** An arm that loses
is a result, not a defect — that is the whole reason a baseline was frozen before it was replaced.

## What the instrument must report beside the score, or the score is not readable

Three things are already known about this arm and each one changes how a realised result must be
read. All three are measured, not suspected, and all three come from
`docs/observability/value_based_pricing_arms.json` and the module's own bound:

1. **165 of 263 accounts had their candidate grid TRIMMED by `max_supported_rate_increase_pct()`
   (+83.1%, the Ofgem cap's own largest published single-step move).** For those accounts the arm
   is not choosing freely; the bound is. A realised win concentrated in trimmed accounts is a
   result about the bound, not about inference, and the report must be able to tell the two apart.
2. **The chosen margins are 15x to 40x the control** (modal region £60–£200/MWh against £2.00).
   This is not a tweak to a price, it is a different price level, and the world's churn response
   to it is the dominant term in any realised outcome.
3. **The control is weak, and by a measured amount.** This company's flat £2.00/MWh is 23.4%–53.6%
   of the EBIT allowance Ofgem grants an efficient supplier
   (`company/pricing/regulated_average_margin.py`, cap period 11a). Beating it is therefore a low
   bar, and any headline must carry that ratio beside it or it flatters the arm by omission.

## What it is NOT allowed to do

- **It may not move `MAX_CHURN_PROBABILITY`, `_MAX_RATE`, either leave-probability cap, or the
  world's switching curve** so the result reads better. R12 makes an output a diagnostic and never
  a target; R13 makes baseline changes fidelity-driven and decided blind to company results. The
  arm losing because the world punishes a 35x margin is the correct behaviour of a faithful world.
- **It may not become the default.** The arm switch defaults to `FLAT_RULES`, so a run that does
  not ask for the experiment is byte-identical to today's. The published figures stay the control's
  until a realised result says otherwise, and even then the change is the director's curriculum
  call, not this experiment's.
- **It may not report a single number.** A realised gap without (1) the trimmed-account split and
  (2) the regulated-allowance ratio is a number that cannot be read, which R14's clock rule already
  refuses for financial figures and this document extends to this one.

## Why this is worth two full runs

~700s each, measured over six consecutive runs on 2026-08-26 — **~23.4 minutes for the pair**, and
~46MB of output. In July the same experiment would have cost the same wall-clock against a
27-account book with no population draw, which is why it was correctly deferred then and is
affordable now. That change is Q3 and Q6 of the evidence pass, and it is the concrete reason the
pass had to be re-run before this document could be written.

## Sequence

1. **The arm switch — as a `DecisionPolicy` FIELD, not a new parameter.** This machine already has
   exactly the seam this needs and it must be reused rather than paralleled:
   `company/policy/decision_policy.DecisionPolicy` is the swappable per-run decision identity
   (`FROZEN_POLICY_BASELINE_DESIGN.md` option B), `simulation/run_phase2b.main(policy=…)` already
   takes it, `CURRENT_POLICY` is the default so every existing caller sees zero behaviour change,
   and `tools/run_frozen_baseline.py` already runs a second arm through it for a comparison the
   project has run before. So the arm is `renewal_margin_arm: str = FLAT_RULES` on that dataclass,
   read at the renewal price path, and nothing new is invented.

   **And the reuse buys the guard, not just the wiring.** `run_phase2b.main` already refuses a run
   whose `policy` and whose `active_policy()` scope disagree, in its own words: *"If those two
   disagree the run is a chimera — naive retention with current dunning letters — and the frozen
   baseline's delta silently attributes an uncontrolled variable to the policy change."* That is
   precisely the failure an A/B on pricing would otherwise be exposed to, already built and
   already fail-closed. A second switch beside it would have had to re-earn that guard, and
   probably would not have.
   **Where the arm ACTS is already decided too, and it is not a new seam either.**
   `company/pricing/renewal_rate_chain.py::decide_renewal_rate` is the ONE door through which
   every rate-moving supplier decision fires — the portfolio learning premium (writer 1), the
   realised-margin recovery surcharge (writer 2), the activity-based uplift for net-negative
   accounts (writer 3) and the Ofgem cap clamp (writer 4) — and its own docstring argues why it
   must be one door: *"the surcharge multiplies what the premium left, the cap clamps what the
   uplift added. Three doors would hand the ordering back to the world."* The value arm is a
   fifth writer in that chain, placed beside writer 3 and BEFORE writer 4, which is load-bearing
   in two ways: it inherits the price-cap clamp rather than needing its own ceiling, and it
   lands in the existing decomposition record (`components`, `chain_entries`) so the A/B can
   attribute a realised difference to this writer rather than to the four it sits among.

   **It takes writer 3's inputs, not `decide_margin`'s.** `renewal_unit_rate_uplift` already
   reaches the account's own settled history from `account_id` + `settled_records`, and
   `decide_renewal_rate` is called at `run_phase2b.py:1329` — BEFORE `tenure_for_est` and
   `company_eac` are computed at 1408/1414. So the arm derives tenure, EAC and cost-to-serve
   itself, inside `company/pricing/`, from the same observables writer 3 uses. That keeps the
   seam narrow (no six new keyword arguments across the wall), keeps the derivation behind the
   wall where a real supplier's would be, and avoids reordering a 3,000-line loop to feed it.

2. **The A/B runner**, shaped on `tools/run_frozen_baseline.py` — two runs, one seed, one world,
   two policies differing in exactly one field, one record. Realised figures only; the
   expected-value numbers stay where they are, in the decisions artefact, clearly labelled as
   decisions.
3. **The score, with its three caveats attached** (above), written where the coupled-gap ledger
   already lives so it is beside the belief-vs-truth record rather than replacing it.
4. **Only then**, a published surface — and only if the coupled record can by then state its own
   provenance, which it currently refuses to.

Steps 1–3 are reversible, cost ~24 minutes of machine time per experiment, and cannot reach a
customer, a pound or a public claim. Step 4 is the one that touches what the company says about
itself, and it stays behind the refusal the coupler already enforces.
