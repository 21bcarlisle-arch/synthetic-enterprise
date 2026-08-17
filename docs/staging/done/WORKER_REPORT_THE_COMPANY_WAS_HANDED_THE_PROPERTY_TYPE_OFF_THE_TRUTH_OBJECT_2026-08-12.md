# WORKER REPORT — the side door is closed, and the gap that halved is the population moving

**Severity:** RECORDED (§2c built; §2a/§2b stay open under the finding itself, parked
`BLOCKING` in `docs/staging/in_progress/`) · **Lane:** W2_customer_generator · **Answers:**
`ADVISOR_FINDINGS_REGISTER_ERROR_CHANNELS_ARE_INERT_2026-08-09.md` §1d / §2c
(the `[ACT]`-first wall item). §2a and §2b remain open and are stated below.

---

## 1. What was drawn and why this part first

The finding's own proportionality note takes §2c first: it is a **wall** item — truth
crossing to the company side without an interface — while §2a (age-driven certificate
error) and §2b (absence correlated with the home) both rest on a published anchor that
the finding itself marks `domain-knowledge, to be verified by an agent with network
access, NOT to be built on as stated`. This seat has no network. Building a magnitude
without its anchor is the finding's own **probable failure mode 1** ("an invented
constant becomes the answer"), so §2a/§2b were left where the finding put them.

## 2. What was wrong, verified on the tree, not from the document

`tools/couple_fabric.py::observe` passed **two** arguments into the company's inference
call computed from `household` — the simulation's own truth object — *unconditionally*,
outside the `certificate is None` branch:

```
property_type_hint=_EPC_PROPERTY_TYPE[household.property_type],
main_heating_fuel=_register_fuel(household),
```

The finding named the first. The second was crossing the same way on the same call and
is now closed with it — R10: the class, not the instance.

Two consequences, both `observed-with-evidence`:

1. For the premises the register has **no certificate** for, the company was still handed
   the property type straight off the truth, and `epc_prior` used it to select the stock
   prior's centre and floor area. It knew more than a real supplier does.
2. `epc_prior`'s refusal — *"no certificate and no property type — the company has no
   fabric prior for this premise at all"* — was live code that **could not fire** in the
   only run that exercises it. A dead failure path.

The `--audit-wall` output asserted in prose that the hint was "a register field". For an
uncertificated premise it was not. The audit was printed, never checked.

## 3. What landed

* `tools/couple_fabric.py::observe` passes **neither** argument. It hands the company
  `premise_id`, `reads`, `weather`, `certificate`, `as_of` — nothing else.
* Premises with no belief are returned as their **own population** (third return value),
  printed above the fold with their count, share and ids, and excluded from every figure
  **loudly**. Dropping them quietly would measure the gap on the homes the register
  happens to describe — the register as the selector, proposed and rejected by the
  Director in the same session (finding §3.3).
* `background/fabric_gap_ledger.py`: `write_fabric_gap_entries` takes
  `premises_without_belief` and carries `premises_without_belief` + `premises_drawn` in
  the row, because `premises` counts only the rows that HAVE a belief.
* A new `MEASURED ON A SUBSET` headline caveat, computed from the coverage shortfall
  rather than from any named commit, so any future shortfall gets it too. `None`
  coverage is not reported as full coverage — an unmeasured coverage claiming 100% is
  the fail-open shape.
* The wall-audit text now states what does **not** cross, with the run's own count.

## 4. Why nothing about a certificated premise moved, and it is a test not a claim

Both dropped values are identical by construction to what the certificate already
carries: `epc_prior` reads `certificate.property_type`, and `_certificate_for` sets
`main_heating_fuel=_register_fuel(household)` from the same map. `test_closing_the_side_
door_moved_NOTHING_about_a_CERTIFICATED_premise` computes each belief both ways and
asserts equality on the point estimate, the prior and the spread across all 14
certificated panel premises. If that ever stops holding, the test says so.

## 5. THE NUMBER MOVED THE FLATTERING WAY — read this before quoting it

Drawn population, `--population 200 --population-seed 17 --seed 17`, same command that
produced the live ledger row:

| | before | after |
|---|---|---|
| premises carrying a belief | 200 of 200 | **126 of 200** |
| EPC-vs-actual gap | 0.4269 | **0.1979** |
| inferred-vs-actual gap | 0.4042 | **0.1860** |
| inference improvement | +0.0227 | +0.0119 |

**The company got strictly worse and the measured gap halved.** Both are true and they
are not in tension: the 74 premises that left the measurement are exactly the ones the
company was worst about, because it was holding a stock-class prior selected by the
truth. The company does not "not have" those premises — it **declines every one of
them**. A gap that halves on the commit that removed the company's information, quoted
bare, reads as the fabric belief improving. That is what the new caveat exists to stop
and what `test_the_reader_is_TOLD_the_gap_was_measured_on_a_subset` keeps firing.

Authored panel, for the record: 14 of 15 carry a belief (S6 has no certificate);
EPC gap 0.2054, inferred 0.2545, improvement −0.0491.

## 6. R15 — the controls fail on their own named defect

Restoring the exact deleted line to `observe` and re-running the suite:

```
FAILED test_a_premise_with_NO_certificate_yields_NO_belief_AT_ALL
FAILED test_the_reader_is_TOLD_the_gap_was_measured_on_a_subset
FAILED test_the_company_is_handed_NO_ATTRIBUTE_OFF_THE_TRUTH_OBJECT
FAILED test_a_drawn_population_measures_a_gap_end_to_end
4 failed, 23 passed
```

Clean: `27 passed` (`tests/tools/test_couple_fabric.py`), plus `337 passed, 4 xfailed`
(`test_premise_two_level.py`, `test_thermal_inference.py`) and `247 passed` across the
reconciler, fabric-physics, fabric-demand-path, fabric-intervention and band-null-sweep
suites. Nothing was `--no-verify`'d.

The superseded test — `test_a_premise_with_NO_certificate_falls_back_and_is_NOT_
actionable` — asserted the stock fallback was never actionable. True, and the wrong
subject: the fallback was only reachable *because* of the side door.

## 7. What is deliberately NOT done, and what unblocks each

1. **The published ledger row was not refreshed.** The row is a number on a public door,
   and `site/proof/index.html` renders `value` large with `components` (where the caveat
   lives) collapsed behind a `<details>`. Publishing a gap that fell by half with the
   explanation folded away is the defect §5 describes. **Unblocked by:** surfacing belief
   coverage beside the value on the Proof door, then
   `python3 -m tools.couple_fabric --seed 17 --unit-rate 7.4 --population 200
   --population-seed 17 --write-ledger`. The reconciler reports staleness and emits the
   refresh command; it does not execute it, so nothing refreshes this behind anyone's back.
2. **The no-belief group's money consequence is not priced.** They are unconditional
   declines; `declined_where_value_existed` counts only premises that reached
   `money_consequence`, so the forgone value of 74 declined premises is in no figure. The
   honest fix reuses `_premise_forgone`'s truth arm rather than writing a second
   definition of what a premise forgoes, which is a change inside
   `background/fabric_gap_ledger.py` and is not free.
3. **§2a and §2b** — unchanged, and open on their published anchors (finding §3, open
   items 1–5). A discovery pass with network access is the next real move on them.
