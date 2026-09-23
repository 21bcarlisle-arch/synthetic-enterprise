**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
`W2_34_the_company_has_one_piece_of_advice_that_costs_the_customer_nothing` · **Class:**
no_caller_and_never_runs

**Knowledge:** none consumed. One knowledge GAP is sharpened below and it is the L3 blocker.

# The advice leg is live for thirteen households, and the health floor costs the ledger nothing

**W2_34 L1 → L2, 2026-09-21.** Drawn as LANE 1 BUILD. Built inline rather than forked: one atom,
one lane, and the file scope is four files.

---

## What was wrong, and why nine green controls could not see it

The atom sat at L1 on **reachability, not correctness**. `turn_down` was in the offer book at zero
capex; the health floor was proven over the whole A–G partition; nine controls were green. And
`decide(epc_band=...)` defaulted to `None` with **no production caller passing one**, so every real
decision reached the fail-closed branch and **no household was ever offered the measure**.

Every control on the RULE stays green while that is true. That is the shape worth carrying forward:
a measure can be correct, proven over its whole input partition, and offered to nobody, and only a
control on the CHAIN can tell you.

## What landed

`thermal_inference.EpcCertificate` gains `efficiency_band` — the certificate's most public field,
and the one thing this record did not carry (it held `build_era_band`, an AGE band). It crosses at
`tools/couple_fabric._certificate_for` **only where the register has a certificate**, which is the
whole epistemic content of the field: a band is a fact about a certificate, so an uncertificated
premise has none and the floor fails closed on it exactly as designed.

The band is **passed through from `simulation.premise_population`'s published draw** (EHS 2022-23
AT1_2, raked into the type × era joint), never derived. The two derivations sitting right there in
`_certificate_for`'s own arguments — the insulation string and the trace's true heat-loss
coefficient — are the two the atom forbids, and both are now refuted by a control rather than by a
comment.

`FabricObservation` carries it; `fabric_gap_ledger._premise_forgone` hands it to **both** arms.

## Measured at real inputs, before the controls were written

| | |
|---|---|
| bands reaching a `FabricObservation` (n=40 draw) | D 19, C 16, AB 2, E 2 |
| clear the 18 °C floor | 18 of 39 |
| **actually offered a turn-down by the production rule** | **13 of 39** |
| authored panel | `None` for all ten — see below |
| money figures moved | **none** |

**The authored panel gets no band and that is the honest value, not a gap.** Its ten premises were
composed — a type, an era, an insulation level chosen to span the stock — and nobody assigned them
a certificate band. Deriving one from the insulation column would move the numbers most figures are
quoted over, on a constant this repo invented.

## The finding inside the result: the advice leg is invisible to the money consequence

`turn_down` **never wins the ranking** at ordinary consumption — printed across the real range
before anything was written, a one-year behaviour is always outranked by a thirty-year fabric
measure. It is surfaced in `Recommendation.zero_capital_measure`, and `_premise_forgone` compares
`.measure`. **So making the band live moved no money figure at all.**

That is correct rather than a defect, and the reason is worth stating: the gap ledger's subject is
BELIEF ERROR, and the turn-down is not belief-sensitive — it turns on a band both arms read off the
same public register. The floor cancels out of the forgone figure exactly. **It is also why both
arms are handed the same band on purpose:** give the truth arm a band the company lacks and this
codebase books a refusal that protects cold households as *money the company's ignorance cost
them*. `test_BOTH_LEDGER_ARMS_ARE_HANDED_THE_SAME_BAND...` is the control for that, on a
zero-belief-error population where a non-zero forgone figure has no other source left.

`turn_down` **does** win where every capital measure destroys value — a 1,000 kWh household at
7.4 p/kWh is recommended a turn-down with a band and declined outright without one. That is the
population the whole finding was about, and it is what stops the control above being a tautology.

## The controls, and the one that was wrong first

`tests/company/test_the_epc_band_reaches_the_floor_from_the_register.py` — six legs, **six
mutations, each caught by the leg written for it**, run in a throwaway worktree so the shared tree
never carried a mutation:

| mutation | leg that fired |
|---|---|
| `observe` stops carrying the band | `..._REACHED_BY_A_PRODUCTION_CALLER...` |
| band derived from insulation at the seam | `..._IS_NOT_DERIVED_FROM_THE_FABRIC` |
| certificate issued with no lodgement | `..._CARRIES_NO_BAND` |
| truth arm loses the band | `..._BOTH_LEDGER_ARMS...` |
| company arm loses the band | `..._BOTH_LEDGER_ARMS...` |
| the floor stops removing the measure | `..._CAN_CHANGE_THE_DECISION_AT_ALL...` |

**The first draft of the not-derived control was itself the defect it hunts.** It read the band off
the population tuple rather than off the certificate `_certificate_for` built, so the
derive-from-insulation mutation sailed straight through it and was caught by a *different* leg — the
flattering reading. A control that pins the READER is blind to what the WRITER did. Repaired to
read the certificate, and the mutation then fired on its own leg.

## What is NOT done — the L3 exit, still blocked, and now blocked more precisely

**Flow temperature.** It is the measure that actually answers this atom's title: zero capital, and
it does not make the home one degree colder, so it never meets this floor at all. Two things the
next lane should not have to rediscover:

1. **The only figure in this repository is not a source.** `docs/market_research/gas_demand_what_
   drives_it_and_the_term_the_model_is_missing.md` carries 6–10%, and reading it in context it is
   **the director's own remark recorded in a discovery document**, not a citation. Building on it
   would be the exact shape CLAUDE.md names — a number picked because a number was needed.
2. **It is a different quantity that shares a number.** That 6–10% is a **boiler efficiency** loss
   from running at 80 °C rather than ~55 °C. `TURN_DOWN_DEMAND_REDUCTION` is 0.06 and is a
   **demand** reduction. Reading the two as one is how this gets built wrong, and it would be
   invisible afterwards because the arithmetic would look right.

**And it needs its own gate, not this floor.** A flow-temperature drop applies only to a condensing
wet system: a heat pump, a non-condensing boiler or a storage-heater home must be refused, and
`HeatingSystem` can answer that where the health floor cannot.

## Two owed reds had to be fixed to land this, and both were pinned to today's answer

The gate selects by subject module stem, so **any** change to `tools/couple_fabric.py` runs
`tests/tools/test_couple_fabric.py`, which carried two reds from the head-red register — the
longest-standing had stood since 2026-09-02. They were not incidental to this work; they were a
hard blocker on it. Both turned out to be the same defect class, and it is this project's most
expensive recurring one.

**1. `test_the_money_consequence_is_AFFINE_in_the_unit_rate_for_a_fixed_decision` — an AGGREGATE
standing in for a VECTOR.** The affine law holds only for a fixed decision, and the test says so:
its docstring states *"the decision vector is asserted unchanged first — a version of this test
without that guard would be measuring a decision flip and calling it a pricing law."* The guard
compared **two aggregate counts**. At 13 p/kWh premise **S9**'s truth arm moved `insulate` →
`heat_pump` while its classification stayed `declined_with_value`: identical counts, £6,000 of capex
intercept different, affine identity broken by **£367.33**, guard green. The test had become the
thing its own docstring warned against.

Repaired by giving `PremiseForgone` the two measures the ledger already computed **and threw away**
(`chosen_measure`, `best_measure`), so the guard reads the ledger's own decision instead of a
recomputed copy — the drift surface that dataclass was split out to close. The rate triple moved
11/12/13 → 14/15/16, **chosen by the strengthened guard rather than by the answer**: it is the first
triple where every premise's `(chosen, best)` pair is genuinely constant. Proven by putting the old
triple back — the new guard refuses it and names S9's flip; the old one accepted it.

**2. `test_the_OLD_WHOLE_METER_reading_was_FAIL_OPEN_on_a_BEHAVIOURALLY_FLAT_home` — a pin on a
counterfactual about deleted code.** It asserted the exact five homes that passed thresholds whose
functions no longer exist, recomputed over a panel that moves whenever the world moves for fidelity
reasons. It read three by 2026-09-02. **That membership could only ever drift**, and drifting down
means the world got less smooth — not that this control's subject changed. Repaired to the property:
the fail-open existed at all (non-empty), and the current reading closes it (the loop, over all six
homes, unchanged — that is the leg with something to lose). Proven by neutering
`half_hourly_texture` so nothing can pass: the leg fires.

## Pre-existing reds left standing, named so they are not read as this commit's

Two remain red at HEAD and are untouched here — both in
`tests/company/billing/test_the_statement_shows_how_each_bill_reached_its_number.py`
(`test_every_issued_bill_agrees_with_the_sum_of_its_own_printed_components`,
`test_the_vat_charged_on_every_catchup_bill_matches_the_NET_base_across_the_real_book`), confirmed
in a HEAD worktree. They are in a different lane and are not selected by this commit.

**Suites run:** `tests/tools/test_couple_fabric.py`, `tests/company/`,
`tests/harness/test_band_null_sweep.py`, `tests/background/test_gap_ledger_reconciler.py` —
15,238 passed, and the two couple_fabric reds above now green.
