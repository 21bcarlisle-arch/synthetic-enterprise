# C32's expert hour fails on the outcome, not the vocabulary — and one of its findings was a live fail-open, fixed in the same turn

**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 3 · **Atom:** `C32_one_obligation_one_vulnerability_scorer` · **Claim:** released on landing

*Worker tick, 2026-10-07. Atom `C32_one_obligation_one_vulnerability_scorer`, L2, loop_stage harden.
The row said it was "one cold-eyes pass away". The pass was run and it failed. The level stays at 2.*

## What was run

A blind pass, using `tools/blind_review.py`, recorded in `docs/observability/blind_review_ledger.jsonl`
with `independence: false`.
- **Persona:** a veteran of GB PSR and debt-and-disconnection operations.
- **What it was given:** a plain-words restatement of the capability, and nothing else. The packet's
  own description was refused as NO_DESCRIPTION, so the restatement is recorded as `restated`.
- **What it produced:** priors first, then 13 battery questions.
- **Verdict:** FAIL, with six MAJORs.

The builder context was consulted only after that, to adjudicate each MAJOR against the code.

## Adjudication

| # | Reviewer's MAJOR | Against the code | Status |
|---|---|---|---|
| EH-1 | The decider reads only the register, not what the supplier has reason to believe; ambiguous flags must block | **CONFIRMED, live shape.** `VulnerabilityRecord.disconnection_protection` passed only EVIDENCED categories to the decider and dropped every undetermined term. An agent's `elderly` flag in mid-January read `NOT_ESTABLISHED`, `may_disconnect=True`. `serious_illness` did the same. "We have not asked their age" became "not protected" — the fail-open the decider's own `may_disconnect` docstring exists to refuse. | **FIXED this turn** |
| EH-2 | No single decider for involuntary prepayment (warrant / remote mode switch), which is the outcome that actually harms people in GB | **CONFIRMED.** `billing/ppm_warrant_register.VulnerabilityCheck` is another rendering of vulnerability: five booleans, with `has_psr_flag` never read by `is_clear_to_proceed`, deciding a protected action outside the decider. It has no production caller, so it is pre-load-bearing, as the five rows in the 2026-09-05 census were. The post-2023 involuntary-PPM categories are **not in the commons**. | open: knowledge first |
| EH-3 | The PSR vocabulary is 9 categories; the industry needs-code list is ~30–36, including temporary "life changes" and a "vulnerable situation" catch-all. Bereavement and mental health are mis-mapped as a result | **PLAUSIBLE, unestablished.** The commons holds no industry needs-code list. The reviewer's memory is not a source. | open: knowledge gap |
| EH-4 | Four flags (payment difficulty, job loss, fuel poverty, PPM self-disconnection) are inert | **REFUTED in code.** `_REQUIRED_ACTIONS_BY_FLAG` routes each to `payment_plan`/`debt_advice`/`offer_emergency_credit`/`whd_assessment`. The packet's wording — "confer nothing" — caused the misreading. It is a reads-as finding against the packet, not the capability. | closed |
| EH-5 | Pensionable age must be state pension age at the decision date (65→66 moved inside 2016–2025) | **CONFIRMED gap.** `PENSIONABLE_AGE` is categorical; nothing computes it from a date of birth. Whether the company holds DOB is the prior question. | open |
| EH-6 | The Energy UK Safety Net is the de facto norm, so a "permitted" answer overstates what a real supplier does | Stated as not modelled in the decider's reason string; no surface shows it. | open, minor |

The reviewer also questioned whether the "all reasonable steps" limb is winter-scoped. The commons (§2, S4) says all-year, and the decider follows the commons. That leaves one open knowledge question: the SLC 27 clause text itself. The commons notes that the licence PDFs defeated extraction.

## And the outcome had more deciders than the census counted

The pass prompted a direct look at who answers "may this household be disconnected". The
2026-09-05 census counted vocabularies. It could not see three uncalled `can_disconnect` methods in
`company/billing/`, because a month comparison is not a vocabulary:

- **`winter_moratorium.py`** held a second winter, **November–March**. That is one month short of
  the published October–March, in the direction that removes protection. It also held a blanket "no
  domestic disconnection in winter" rule, which no licence condition states, and a docstring
  claiming PSR confers year-round prohibition. Its `is_vulnerable` argument was accepted and never
  read. Its own test asserted `October is not winter`.
- **`disconnection_warning.py`**'s docstring restated the same wrong rule. Its `can_disconnect`
  checks the warning sequence only, which is correct for it, and that is now what it says.

**Fixed:**
- `winter_moratorium.can_disconnect` now asks `disconnection_protection` and adds only the
  supplier's own holds.
- `categories` is keyword-required, so a caller that does not know must say `()` rather than
  inherit "nobody here is protected".
- `is_winter_period` reads `WINTER_MONTHS`.
- The October test now asserts the published winter.
- A new control, `test_the_winter_is_defined_once`, with a detector self-test, reds any
  disconnection-related `company/` module that restates which months are winter.

## Mutations — six, all killed

1. The old `winter_moratorium` restored: the winter-once control reds.
2. Delegation removed (`return True`): 2 partition legs red.
3. The decider's winter shortened to Nov–Mar: the October leg reds.
4. Refuse-everything (`return False`): the partition's permitted leg reds.
5. The old drop-undetermined wrapper restored: the new partition control reds.
6. Block on *any* undetermined term, with no counterfactual: the `child_dependent` permitted leg
   reds.

## What would move the level

EH-2 first. Before any code goes near involuntary prepayment, the post-2023 involuntary-PPM rules
(Ofgem's code of practice and its licence form) go into the commons. Then
`ppm_warrant_register.VulnerabilityCheck` is routed through one decider, or deleted.

EH-3 and EH-5 are knowledge-layer items. A re-take of the expert hour follows once the commons
holds them.
