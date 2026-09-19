# C33_collections_reads_the_registers_it_already_has — FRAME (canonical per-atom, doc-only)

**Atom** `C33_collections_reads_the_registers_it_already_has` · lane `C_customer_ops` · value stream
`meter_to_cash` · epoch 3 · dial 45 · `level_current: 0` → `level_target: 2` · `loop_stage: idle`.

**Measured at** `3bd9e95ed`, 2026-09-19. **DISCOVER/FRAME output only** — no BUILD code is written
here (`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1: parking gates BUILD, never thought). This atom
is authorship-gated, not epoch-gated: agent-authored, so BUILD waits on the director's ranking.

---

## 0. What this doc is

C33 was split out of C29 by the C29 FRAME (§5, "HALF B — arithmetic and legality") as the ungated
half: three defects that make no selection claim and are refutable against a flat world. C29's FRAME
measured them at `c1609e374`. This pass re-asks them at HEAD, carries them to their own level
definitions, and reports two things the parent pass did not have.

**The headline: both halves of C33 are correct as defects and neither is a live compliance breach
today, because the code they sit in has no production caller at all.** That does not shrink the
atom — it changes what "done" has to mean, and it is the reason §4's level definitions are keyed to
the *property* rather than to an outcome that is currently vacuous.

---

## 1. The re-ask, and how much of it is genuine

The parent FRAME's Half-B claims are **all three re-confirmed at HEAD**, but the honest statement of
*why* matters: 68 commits separate `c1609e374` from `3bd9e95ed`, and

```
git diff --name-only c1609e374..HEAD -- company/billing/ company/crm/ tests/company/
```

returns **nothing**. Not one commit in that range touched the atom's scope. So the re-confirmation
is by construction, not by independent re-reading, and it buys only the knowledge that the window
is clean. Everything below was re-read anyway, and §2 and §3 are what that re-reading found.

---

## 2. The enforcement half — confirmed, and inert, and those answer opposite ways

### 2a. The conditional layer: the selector cannot see a moratorium

`company/billing/arrears_engine.py` selects a dunning step through exactly two functions:

```python
def current_dunning_step(segment: Segment, days_overdue: int) -> Optional[DunningStep]
def select_dunning_step(items: Sequence[AgedItem], segment: Segment) -> tuple
```

Neither takes an account id. `AgedItem` carries an amount, a due date and a `disputed` flag. There
is **no parameter through which a Breathing Space moratorium could be seen**, so the enforcement
steps in the resi and micro-SME paths —

| Segment | Step | Trigger |
|---|---|---|
| RESIDENTIAL | `final_notice` | day 56 |
| RESIDENTIAL | `prepayment_or_debt_agency` | day 90 |
| MICRO_SME | `disconnection_warning_or_agency` | day 75 |

— are reachable on days-overdue alone. The module's own docstring already says so, as NAMED
SIMPLIFICATION (4): *"there is no live recall of an SLC-27 hold here."* That note is honest and it
is **narrower than the defect**. SLC 27 is a licence condition about ability-to-pay. The Debt Respite
Scheme (Breathing Space Moratorium and Mental Health Crisis Moratorium) Regulations 2020
(SI 2020/1311), which `company/billing/breathing_space_register.py` cites in its first line, is
*statute*, and during a moratorium enforcement is prohibited outright — it is not a factor to weigh.
A simplification note naming only the SLC-27 hold leaves the statutory prohibition undocumented.

### 2b. The production layer: nothing selects a dunning step

```
grep -rn "current_dunning_step\|select_dunning_step\|dunning_path\|collections_snapshot" \
     --include=*.py company/ saas/ simulation/ tools/ background/
```

returns **zero rows outside `arrears_engine.py` itself**. The one production importer of the module,
`company/billing/payment_observation_consumer.py:144`, takes `AgedItem`, `age_balance`,
`age_open_items`, `ageing_buckets` — the ageing half — and no part of the dunning half.

`company/billing/breathing_space_register.py` (184 lines, 10 tests in
`tests/company/billing/test_breathing_space_register.py` plus
`test_phase_fy_breathing_space.py`) has **zero production callers**. It is complete: `register_entry`,
`records_for_account`, `is_active_as_of`, `active_records`, the two moratorium types with their
durations. Everything a gate needs already exists; nothing composes it.

**Both layers must be stated together or the atom is mis-read.** Conditionally: the path can enforce
through a moratorium. Productionally: no path enforces anything. Reporting only the first overstates
a live compliance hole; reporting only the second reads as "nothing to do" and is how the gate stays
unbuilt right up to the moment a caller appears.

### 2c. Why that makes the work *more* urgent, not less

The gate is cheapest to install while there is no caller to retrofit, and the wiring atom that will
add the caller is the one that will be under pressure to ship. A statutory prohibition that arrives
after its first consumer arrives has to be threaded back through a live path.

---

## 3. The retention half — confirmed, and sharper than stated

`company/crm/customer_retention.py:78`:

```python
@property
def expected_retention_value_gbp(self) -> float:
    """Net benefit if customer is retained: margin saved minus cost of offer."""
    if not self.is_offer_made:
        return 0.0
    return round(self.net_margin_gbp - self.offer_value_gbp, 2)
```

That is a **conditional** value — the benefit *given* retention — published under the word
*expected*. The docstring says "if customer is retained" and the name does not. It is summed by
`total_expected_retention_value_gbp` and published by `retention_summary()`.

**The parent FRAME said the probability is absent. It is worse: the probability is handed in and
dropped.** `generate_offer(risk: CustomerChurnRisk, ...)` receives an object carrying
`churn_probability`, and `RetentionOffer` stores `churn_risk_band` — the *banded* form — discarding
the continuous value on the way past. The fix is not to go and find a probability; it is to stop
discarding one already in hand.

**And the correct form is already written, one module away.**
`company/crm/portfolio_churn_risk.py:75`:

```python
@property
def expected_loss_gbp(self) -> float:
    return round(self.churn_probability * self.annual_revenue_gbp, 2)
```

So the tree holds one correct and one incorrect use of *expected*, in two modules, where the
incorrect one **consumes the object carrying the correct one**. This is the "before measuring a
thing, say what it is" failure in its cleanest form: two quantities, one word.

`CustomerRetentionBook` likewise has **zero production callers** — grep for `CustomerRetentionBook`,
`retention_summary` and `expected_retention_value` over `*.py` outside the module and `tests/`
returns nothing, and over `site/`, `docs/market_data/` and `tools/` returns nothing. **The mis-named
figure reaches no reader today.** Same two-layer shape as §2, same consequence.

---

## 4. Levels 0 → 2 (this atom carried none)

C29's L1 was "Half B landed". C33 *is* Half B, so it needs its own ladder. Written to be satisfiable
on a world where nothing calls the code, because that is the world.

- **L0 — today.** Enforcement steps select on `(segment, days_overdue)`. The moratorium register and
  the ability-to-pay organs have no caller. `expected_retention_value_gbp` is a conditional value
  named as an expectation.
- **L1 — the arithmetic is honest.** The retention figure either carries `churn_probability` and
  becomes an expectation, or is renamed to what it computes (`retention_value_if_retained_gbp`) with
  the conditional stated at every call site and in the summary key. Decided, not left to the reader.
- **L2 — the enforcement path cannot refuse to look.** Dunning selection takes the account's
  moratorium status as a required input, and an enforcement step cannot be returned without it.

**L2 is keyed to the property, not to today's answer.** The tempting control — "no account is dunned
through an active moratorium" — passes today on an empty world and would pass on a register that
always returns "no moratorium". It is a control that cannot fail (`CONTROLS_THAT_CANNOT_FAIL.md`).
The control that can fail asserts over the whole partition: that the selector *can* return an
enforcement step, *can* return a held step, and that a moratorium flips it — one control, three
legs, with the reachability leg first. Writing the refusal leg alone reproduces the trap
CLAUDE.md records being entered three times in one afternoon.

---

## 5. The organ question — the parent FRAME's direction is refuted

C29 FRAME §5 item 3 asks to "wire `capacity_to_pay` into the SLC 27 day-28 `repayment_plan_offer`
step", noting that deciding between the two live ability-to-pay organs is part of the work "because
two is the defect". Agreed on the defect. **The evidence at HEAD points at the other organ.**

| | `company/billing/capacity_to_pay.py` | `company/crm/affordability_inference.py` |
|---|---|---|
| Size | 98 lines | 12,565 bytes |
| Production callers | **none** | `tools/couple_w2_4_c6.py` |
| Has a map atom | no | `C6_affordability_inference`, **closed at `level_current: 2`** |
| Coupled to a SIM organ | no | yes — `W2_4_household_budget`, `W2_2_population_draw` |
| Measured (belief-vs-truth gap) | no | yes — `raw_gap: 0.298` in `docs/observability/coupled_gap_ledger.json`, with the ledger's own note that the gap is floored non-zero because the observable channel is strictly coarser than the hidden budget |
| Shape | plan months, minimum payment | banded assessment inferred from payment observations |

`capacity_to_pay` is an orphan with tests and no atom. `affordability_inference` is the organ the
project has already coupled, measured, carried to its target level and closed. Wiring the orphan
into a live path would make the closed, measured organ the
second implementation of a live rule — the VAT shape CLAUDE.md names as the seat's own recurring
defect (one requirement, five implementations, a fix landed in one and still live in another).

**FRAME position: `affordability_inference` is the organ; `capacity_to_pay` is a candidate for
retirement, not for wiring.** That is a claim about which organ, not a decision to delete anything,
and it is stated here so the BUILD pass inherits it as a question already asked rather than
re-deciding it under delivery pressure. It is refutable: if `capacity_to_pay`'s plan-months
arithmetic is what the day-28 step needs and `affordability_inference` cannot produce it, this is
wrong and the record should say so.

---

## 6. A knowledge-layer gap, filed rather than filled

`docs/domain_artefact_library/regulatory/` holds twelve artefacts, including
`psr_eligibility_and_disconnection_protection.md`. **None of them mentions Breathing Space, the Debt
Respite Scheme, or a moratorium** (grep over `domain_artefact_library/`, `institutional/` and
`market_research/`: zero files). Meanwhile `breathing_space_register.py` carries the regime as module
constants:

```python
_BREATHING_SPACE_START_DATE = dt.date(2021, 5, 4)   # scheme commencement
_STANDARD_DURATION_DAYS = 60
_MH_POST_TREATMENT_DAYS = 30                          # extra days after MH treatment
```

Three statutory numbers, cited only by an inline comment, with no commons entry any other lane can
read. This is the shape the knowledge-first rule exists for, and it is why the L2 control above must
be written against a commons artefact rather than against these literals: a control that re-reads
the module's own constants proves the module agrees with itself.

**Owed, and not done here** (it is DISCOVER work on a published source, and this pass's scope was the
atom's own code): a `debt_respite_breathing_space.md` artefact in the regulatory commons carrying
SI 2020/1311's durations, the two moratorium types, and — the part that actually binds the code —
the enumeration of what a creditor may not do during a moratorium. Until it exists, L2 is blocked on
evidence rather than on permission, and that is a better place for it to be blocked than where it
was.

---

## 7. What this FRAME buys

1. The two defects are **confirmed at HEAD** and both are **productionally inert** — the conditional
   and production layers answer opposite ways and both belong in the record.
2. The retention defect is **larger than claimed**: the probability is discarded, not missing, and
   the correct form of the same arithmetic is already written one module away.
3. The organ choice is **refuted in direction**: the coupled, measured organ is
   `affordability_inference`, not the orphan the parent FRAME named.
4. A **commons gap** is filed: a statutory regime lives in module constants with no artefact.
5. Levels 0→2 exist, keyed to the property, with the reachability leg named so the BUILD pass does
   not write a guard that refuses everything.

**Not done here, deliberately:** no BUILD code, no map level move, no constant change, no commons
artefact. The atom stays `level_current: 0`, `loop_stage: idle`, awaiting the director's ranking
(agent-authored atom).
