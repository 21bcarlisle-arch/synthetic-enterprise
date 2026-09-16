**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, "point the arm at the renewals that are genuinely reachable"

# The last 158 refused renewals are 18 gas-only accounts, and no account without an electricity leg can leave this world

Delivery seat, 2026-09-16. The drawn item said: *take the 158 renewals whose `tariff_type` the
world settled as `None` — our defect, a term with no decided product — and make them priceable; fix
whatever leaves a settled term without a decided product rather than widening
`UPLIFTABLE_TARIFF_TYPES` to swallow them.*

The first half of that is right and the repair is one line. **The second half is what this
document is for: the one-line repair is refused, and the reason was not visible from the funnel.**

---

## What the 158 actually are, measured

**One measurement, on one population — the live roster at HEAD.** Not a join between two trees:

| `simulation.run_phase2b`, imported at HEAD | count |
|---|---|
| gas supply points on the roster | 90 |
| …carrying `tariff_type` **absent**, so `.get(..., "fixed")` works → `fixed` | 72 |
| …carrying the key **present with value `None`**, so the default is defeated | **18** |
| of those 18, belonging to a household that ALSO holds an electricity supply point | **0** |
| of the 72, belonging to a household that also holds one | **72** |

So at HEAD the unlabelled gas legs and the gas-only households are one set, and the split is total:
every dual-fuel gas leg is labelled, every gas-only one is not. That is the whole finding and it is
a single census, not two figures agreeing.

**Stated separately, because it is a different tree and must not be read as the same measurement.**
The artefact the page is published from (`value_cycle_ab_s1_three_arm.json`, run 2026-09-10 at
`9cf9d16ed`) reports a book of 164 settled billing accounts — 146 with an electricity leg, 105 with
a gas leg, 87 dual-fuel, hence **18 gas-only** — and a funnel refusal breakdown of
`{"'svt'": 1347, "None": 158}`. The gas-only count matches HEAD's unlabelled count and the
mechanism is the same one, but that run's book is not this roster (105 gas-leg accounts against 90
gas supply points here), so what carries is the MECHANISM and not a set identity. The claim this
document rests on is the HEAD census above; the artefact is corroboration, and a re-run is what
would turn it into a measurement.

On that reading the funnel's 1,505 decomposes as 1,347 electricity SVT segments — a product with no
renewal to price, the arm's real ceiling, untouched here — and 158 renewal terms of gas legs whose
product was never decided, on households that hold no electricity supply point.

`resolved_tariff_type` (`simulation/run_phase2b.py:573`) resolves electricity as
`record.get("tariff_type") or "fixed"` and gas as `record.get("tariff_type", "fixed")`. A drawn
record renders the key unconditionally (`population_draw.to_customer_dict`), so the gas default is
never reached. The function's own docstring already says the gas branch is a defect owed a
determination and files it rather than answering it. **This is that determination.**

## The 18 are the exact prize that was named in advance

`docs/staging/done/SEAT_PREDICTION_WHAT_ADMITTING_GAS_TO_THE_ARM_WILL_AND_WILL_NOT_BUY_2026-09-07.md`,
written before the gas commodity gate was widened:

> A dual-fuel household's gas renewal is a SECOND decision on a customer the arm already prices on
> the electricity leg — it adds a decision, but not an independent one. **The gain worth publishing
> is accounts, not renewals**, and I expect the headline temptation to be the other way round.

That prediction held, and it holds sharper than it was written: the gas admission delivered the 87
dual-fuel legs, which are the decisions-without-accounts half. The accounts half — the 18 gas-only
billing accounts, the whole of the gain that prediction said was worth having — is precisely what
the `None` refusal still holds back. The page needs 96 scored accounts to resolve its own observed
0.0443 excess and has 73. These 18 are more than a fifth of the gap.

**So the temptation is real, it is large, it arrives with a correct argument attached, and the
one-line repair delivers it.** That is why what follows is a refusal and not an omission.

## Why the one-line repair is refused

`simulation/run_phase2b.py` books a departure at exactly two sites — `churned_billing_accounts.add`
at lines 1895 and 2354 — and **both are lexically inside `if commodity == "electricity"`**.
Established by walking the module's AST, not by reading the branches:

```
add at line 1895 -> electricity guards at [1783]   # the SVT-segment inertia roll
add at line 2354 -> electricity guards at [1982]   # the renewal decision
```

There is no third route. An account whose only supply point is gas is **never rolled for departure
at all**. Those 18 accounts are settled, renewed and billed across the whole 2016–2025 window and
the world never once offers them the chance to go.

Now put that beside what the 158 would be used for. `tools/run_value_cycle_ab._survivorship`
publishes that `method_skill.concordance` **is conditioned on survival** — the decisions it cannot
score are the renewals the world recorded as departures. Admitting the 158 adds 158 decisions whose
accounts survive **by construction rather than by being priced well**, into the one instrument this
company has for asking whether it knows anything about a household. The survivorship block would go
on saying the concordance is bounded by the departures it can see, while a fifth of its accounts
had no departure to be bounded by, and nothing anywhere would be able to notice.

This is the same shape as the 1,347 `svt` renewals the direction correctly ruled out of bounds:
reaching for them moves a number without creating anything. The difference is only that the svt
half announces itself in the funnel and this half does not.

**Refused, then: widening `UPLIFTABLE_TARIFF_TYPES` (already refused by the direction), spelling the
gas read `or "fixed"` on its own, and admitting the 158 by any other route.** Not because the read
is right — it is wrong — but because the read is not what is holding them out.

## What is owed, in the order it is owed

**1. A departure route for an account with no electricity leg.** The fidelity claim is not
delicate: a household that buys its gas from us and its electricity from someone else can switch
gas supplier like anyone else. Until that route exists, **18 of 164 accounts — 11% of the book —
are immortal**, and a book of immortal households earns more than a real one.
`simulation/svt_product.py` wrote that interlock against itself in August and it applies here
unchanged. (The size of the population, not half the book: 47% of accounts are single-fuel, but 59
of those are electricity-only and depart normally. It is the 18 that have no route.)

**2. Then the gas `tariff_type` read, and as the C1b roll, not as a label.** The 2026-08-28
determination (`DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md`) refused a blanket `fixed`
against a published domestic fixed share of roughly one third. Electricity got the honest version
on 2026-08-30: opening term `fixed` because an account arrives by taking a deal, and every boundary
after decided by the household's own engagement roll. Gas must get the same mechanism, which needs
`svt_product.build_svt_schedule` fuel-parameterised — `simulation/svt_rates.get_svt_gas_rate_gbp_per_mwh`
already carries the gas cap at the same granularity as electricity, so the product side is close.

Note the consequence, recorded as a consequence and not as a reason: repair 2 done honestly puts
roughly a third of the 72 already-labelled gas legs' terms onto SVT too, which **shrinks** the
priced population before the 158 enlarge it. The net sign is not predicted here.

## The 252 acquisition terms — the dial, and the seat's decision

The direction offered this as a dial the seat may turn: 252 renewals classed
`acquisition_term`/`deliberate_scope`, *"the arm was never pointed at them"*.

**Decision: do not turn it. The arm stays off term 0.** Reasoning, recorded either way as asked:

- **There is no prior rate to move.** `renewal_margin_uplift` moves a locked margin; at term 0
  `prev_fixed_unit_rate` is `None` by construction. Pointing the arm here is not turning a dial, it
  is building the acquisition desk — the same desk the funnel already names as unbuilt for the
  1,505.
- **It would make the verdict worse, not better, and for the flattering reason.** At term 0 the
  company holds no settled history for that household, so the per-customer method has nothing to
  infer *from*. Those decisions would carry no information by construction and would pull the
  concordance toward 0.5 while inflating `n` — which moves the null interval in and the estimate
  down at the same time. **Enlarging `n` with decisions the method cannot inform is the one way to
  make "cannot tell" look resolved without learning anything.**
- **The funnel's own classification is right.** `deliberate_scope` is not a euphemism here. An
  acquisition is a different decision with a different information set, and the mission's test —
  value created, then shared — is not met by pricing a household we know nothing about.

This decision is reversible the day an acquisition-pricing desk exists and can be scored on its own
terms. It should not be reversed by widening the renewal arm's population.

## What landed with this document

`tests/simulation/test_a_departure_is_booked_only_on_an_electricity_leg.py` — three legs, each
mutation-proven:

- the AST walk and the source text agree on WHICH lines book a departure (proven by respelling one
  site so they disagree — without it the guard leg goes green over one site and reads as two);
- every booking sits under an electricity guard (proven by dedenting line 1895 out of its block);
- the book still holds gas-only accounts, so the finding has a subject (a control that outlives its
  population is furniture).

**It is meant to go red.** Leg two is green on the defect and red on the repair, which is the same
contract `tests/simulation/test_the_tariff_type_read_has_one_home.py` writes for the sibling defect
on the same 18 accounts. When the gas-only departure route lands, that file and this document are
deleted together. What it buys until then is that **nobody admits the 158 without first meeting the
18.**

## Where this leaves the drawn item

The done-condition was `method_skill` stating a side rather than `cannot_tell`. It does not state
one yet and this turn does not make it. What this turn establishes is that the route the item
proposed to it is closed, why, and what has to land first — and that the 252 half of the item is
answered and shut, with its reasoning on the record rather than in a commit message.

The honest summary of the arithmetic: the page's own curve needs 222 scored decisions / 96 scored
accounts for the excess it observed. The 158 are worth 18 accounts of the 23 missing. They are not
free, and the two repairs above are what they cost.
