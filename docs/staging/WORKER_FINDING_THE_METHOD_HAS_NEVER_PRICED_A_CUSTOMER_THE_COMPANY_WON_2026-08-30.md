**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `SITE13_the_baseline_comparison_carries_its_bound`

# The method has never priced a customer the company won, and it is a gate rather than a book size

Drawn as lane-0 delivery on 2026-08-30. The direction asked one question a reader can check:
**is there any book size at which a won household reaches the per-customer arm, or does a won
household fail a gate it can never pass?**

**The answer is a gate.** It is named below, it is not fixed here, and the world was not opened to
let the arm through.

## The decomposition the funnel could not do

`docs/observability/value_cycle_ab_s1_three_arm.json` → `renewal_funnel.value_arm` says where
1,349 unpriced renewals went, stage by stage. It could not say **whose** they were. Split by how
each billing account joined the book — the world's own `acquisition_type`, not the shape of the id:

| population | billing accounts | elec legs | gas legs | `tariff_type` on the elec record |
|---|---|---|---|---|
| founder, hand-authored (`C1 … C9`, + the `C1_2` successor) | 9 | 9 | 4 | **key absent** → `.get(…, "fixed")` returns `"fixed"` |
| won by the acquisition funnel (`PROS-*`) | 90 | 90 | 86 | **present, `None`** |
| drawn by the curriculum (`SYN-*`) | 69 | 51 | 18 | **present, `None`** |
| | **168** | **150** | **108** | |

Those three columns are the artefact's own `billing_accounts_settled_in_window` (168),
`with_an_electricity_leg` (150) and `with_a_gas_leg` (108) exactly, so the census is of the book
the run actually had and not of a fresh draw.

Attributing the stages:

| stage | count | whose |
|---|---|---|
| `acquisition_term` (term 0) | 258 | one per leg: 13 founder, 176 won, 69 drawn |
| `not_the_arms_commodity` (gas) | 429 | the gas legs' later terms, all three populations |
| `product_not_upliftable` | 662 | **100% `tariff_type = None`, so 0 founder — every one is won or drawn** |
| **priced** | **20** | **100% founder** — `C1, C1_2, C2 … C9`, ten accounts |

The last two rows are exact rather than apportioned. A founder electricity record has **no
`tariff_type` key**, so it cannot produce a `None`; the artefact's own
`product_not_upliftable_by_tariff_type` is `{'None': 662}` with no other label. And
`accounts_the_arm_priced` names ten accounts, every one of them founding.

**158 of the 168 accounts the world offered a renewal to have never had one reach the arm.**

## The gate, named

Three lines, in the order they fire:

1. `simulation/population_draw.py` — `SyntheticCustomer.tariff_type: Optional[str] = None`, and
   `to_customer_dict()` renders `"tariff_type": self.tariff_type` **unconditionally**. The key is
   present with value `None`. The acquired (`PROS-*`) electricity book carries the same.
2. `simulation/run_phase2b.py:1170` — `tariff_type=c.get("tariff_type", "fixed")`. The default
   exists to prevent exactly this and is **dead on 141 of the book's 150 electricity legs**,
   because `.get` only defaults on an ABSENT key. `build_renewal_schedule` then stamps `None`
   onto every term.
3. `company/pricing/value_based_renewal.py` —
   `if tariff_type not in UPLIFTABLE_TARIFF_TYPES: return … STAGE_PRODUCT_NOT_UPLIFTABLE`, where
   `UPLIFTABLE_TARIFF_TYPES = frozenset({"fixed", "pass_through"})`
   (`company/crm/customer_profitability.py:219`).

`None` is not in that set and nothing between the draw and the guard can put it there.
**So the sentence is: no number of won households changes what that guard reads, and there is no
book size at which the first one is priced.** It is structural, and the founding nine pass only
because they predate the draw and their record omits the field.

## What is NOT owed

Not a relaxed guard, and not an assignment to the field. That was ruled on two days earlier, on
fidelity evidence and blind to what it does to `n`:
`docs/design/DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md` (settled 2026-08-28). Setting the
won book to `"fixed"` would assert a 100%-fixed domestic book against a published fixed share
centred near one third — a fidelity regression dressed as a correction whose only beneficiary is
this experiment's sample size.

What is owed is a **standard-variable product in the world**, from the published year-by-year
domestic fixed/SVT split. That is a curriculum question, it is registered as owed, and it goes to
the director as one rather than being executed here. When it lands honestly the in-scope surface
gets **smaller as a share of the book**, not bigger.

## Why this is on the page and not in an observability file

The mission says the enterprise value is the automated method of **finding** individual customers
we can create value for. The A/B exists to evidence that. Right now the method has inferred over
ten customers and every one of them is a customer the company was founded with — so every argument
this project is having about book depth, seeds, error bars and settlement ceilings is downstream of
a claim the artefact could not test. *"The method has never priced a customer the company won"* is
a fact about the enterprise value claim.

## What landed

- `tools/run_value_cycle_ab.py` — `account_class_map()` and `funnel_by_account_class()`; every
  future run's `renewal_funnel.*` carries `by_account_class` with the exact split, counted from
  the log rather than derived here, plus
  `accounts_the_company_won_or_drew_that_the_arm_priced` as a single number.
- `tools/generate_value_arms_data.py` — `_who_the_method_has_priced()`, three-way and **derived**:
  `structural` while no won or drawn account has been priced AND the product gate's whole refusal
  is the unset label; `reached` the moment one is priced; `unresolved` when the gate refuses under
  more than one label, because a refusal that names a cause it never observed is the wrong repair
  waiting to happen.
- `site/capabilities/index.html` — the sentence in `#arms-decisions`, amber, beside the decision
  count that has always been there.
- Controls, each naming its own mutation:
  `tests/tools/test_the_renewal_funnel.py` (4 — including the null rung that prices a won account,
  because a counter only ever observed at zero cannot be told from one that cannot leave zero),
  `tests/tools/test_generate_value_arms_data.py` (4),
  `site/test_the_baseline_comparison_reaches_the_reader.py` (3, on the rendered string).

## The classification is keyed to the world, not to the id

`by_account_class` reads `acquisition_type` — written by the roster that minted the account —
rather than testing for a `PROS-`/`SYN-` prefix. A prefix rule is a control pinned to today's
naming: rename the ids and every won account reads as a founder account, in the flattering
direction, silently. The page keeps a prefix fallback for artefacts predating the block and says
in `classification_basis` which of the two it used.
