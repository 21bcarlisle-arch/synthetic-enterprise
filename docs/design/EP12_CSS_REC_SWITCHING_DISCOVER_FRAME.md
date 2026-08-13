# EP12 — Switching under the REC: DISCOVER + FRAME

**Atom:** `EP12_adapter_css_rec_switching` · lane `W4_the_wall` · epoch 3 · level 0 → 3 · `loop_stage: idle`
**Draw:** 2026-08-14 worker tick, LANE 3 (DISCOVER/FRAME only). **No BUILD code written** — the atom is
epoch-gated (`block_reason`: director-reserved curriculum sequencing, R13), and EPOCH_GATING_AND_ATOM_AUTHORSHIP
Rule 1 permits DISCOVER/FRAME on a parked atom and forbids BUILD.
**Level:** **HELD at 0.** The deliverable of this atom is an *adapter*; this document is *about* the adapter,
not the adapter. Same call as `EP10_adapter_uk_link_xoserve` (held at 0, 2026-08-13), opposite call to
`EP19_counterparty_qualification_paths` (moved 0→1 the same day, because a register was its own stated
ceiling). The discriminator is the `origin_note`, and EP12's names failure modes of a *process*, not a doc.

Every claim below marked **observed** was run against HEAD this pass; **inferred** is this pass's reasoning;
external facts carry the verification marker of their dated source (R9). No network — autonomous runs have
none — so nothing here is new research.

---

## 0. What the atom says it is

*"Adapter for switching flows: electricity CSS (operated by DCC) and gas Supply Point Switching, both
administered through RECCo under the REC Data Access Matrix, with eligibility confirmed by the REC Code
Manager. Access class GATED; the adapter stays mocked, shaped to REC message flows."*

`gain`: *"Gaining and losing customers becomes an industry **process** with its own failure modes, not a
state change."*

`origin_note`: *"Erroneous transfers, objections and failed switches are the substance — a switching adapter
that only models successful switches has modelled the easy half and left out every case that generates a
complaint, a credit balance and a regulatory obligation. Interacts with `W2_12_change_of_tenancy_debt_physics`,
where a switch and a tenancy change look identical from the company's side until they don't."*

The `gain` is the test this document holds the tree against: **is a gain or a loss a process, or a state
change?** The answer at HEAD is unambiguous, and it is worse than "state change" — see §2.

---

## 1. DISCOVER — the company half is built, in fourteen modules, and nothing calls it

**Observed**, by strict import check at HEAD (`from <module> import` / `import <module>` /
`from <package> import <name>`, over `company/ sim/ simulation/ saas/ tools/ background/`, excluding `tests/`):

| module | lines | non-test importers | test files |
|---|---|---|---|
| `company/market/mpas_standing_data_correction_register.py` | 244 | **0** | — |
| `company/crm/onboarding_journey.py` | 240 | **0** | — |
| `company/market/css_performance_register.py` | 220 | **0** | 1 |
| `company/market/transfer_objection_register.py` | 189 | **0** | 2 |
| `company/crm/switching_cost_model.py` | 176 | **0** | — |
| `company/market/switch_governance.py` | 172 | **0** | 4 |
| `company/crm/css_tracker.py` (see §4 — not this atom) | 170 | **0** | 1 |
| `company/crm/switch_analytics.py` | 129 | **0** | — |
| `company/market/erroneous_transfer.py` | 123 | **0** | 1 |
| `company/crm/cos_process.py` | 123 | **0** | 2 |
| `company/crm/switching_cba.py` | 121 | **0** | — |
| `company/market/mpas_registry.py` | 117 | **0** | 1 |
| `company/crm/switching_report.py` | 112 | **0** | — |
| `company/billing/switching.py` | 106 | **0** | 1 |
| `company/market/dtn_log.py` | 89 | **0** | — |

**2,161 lines across fifteen modules; every one has zero non-test importers.** The single switching-named
module in the tree that *is* live is `company/pricing/switching_recommendation.py` (84 lines, imported by
`company/portal/app.py:30`) — and that is **tariff** switching, the customer moving between the company's
own products. It is not industry switching and is not this atom.

Eight of those modules carry **165 named tests** between them (`test_phase_ga_css_performance` 34,
`test_phase_go_transfer_objection` 26, `test_switching` 21, `test_erroneous_transfer` 19, `test_cos_process` 19,
`test_mpas_registry` 19, `test_switch_governance` 17, `test_transfer_objection_register` 10). Every one of
those tests constructs its subject directly. **Production code never has.**

This is the same population and the same shape as the 2026-08-13 finding *"the gas industry-systems layer is
eleven modules and no callers"* (`WORKER_FINDING_THE_GAS_INDUSTRY_SYSTEMS_LAYER_IS_ELEVEN_MODULES_AND_NO_CALLERS`).
EP12's half is larger. **The first BUILD move on this atom is a wiring decision, not a new-module decision** —
and, as §2 shows, it is not even that, because there is nothing on the world side to wire *to*.

The company's failure half is, on inspection, already modelled in some detail: `cos_process.CoSStage` runs
`SWITCH_REQUESTED → OBJECTION_WINDOW → OBJECTION_CLEARED → FINAL_READ_REQUESTED → FINAL_READ_RECEIVED →
SWITCH_COMPLETE`, with `OBJECTED` as a terminal branch; `erroneous_transfer.ETStatus` runs
`OPEN → INVESTIGATING → RESOLVED_CORRECTED | RESOLVED_ACCEPTED → COMPENSATION_DUE → CLOSED`. **The
`origin_note`'s "modelled the easy half" is therefore not a description of the company's code.** It is a
description of the *world's*, and of the seam between them.

---

## 2. DISCOVER — the world has no switch to be wrong about

**Observed.** The world's entire exit mechanism is one Bernoulli at a term boundary
(`simulation/customer_events.py:139-142`):

```python
retained = roll <= effective_p_retain
home_move_won = False
if not retained:
    win_roll = _random.Random(f"win_{billing_account}_{term_start_str}").random()
    home_move_won = win_roll <= renewal_data["win_probability"]
```

Three facts follow, and each is load-bearing:

1. **There is exactly one exit event.** Not "switched to a competitor" and "moved home" as distinct causes —
   one undifferentiated non-retention, resolved into `churned_ids: set[str]` and `churned_billing_accounts`.
   The `home_move_won` roll is applied to *all* of it, so in this world every departure is a home move the
   company may or may not win. There is no competitive switch as a distinct thing that can happen.
2. **The exit is instantaneous and irreversible.** It has no in-flight period, no gaining counterparty, no
   objection window, no reversal. A switch under the REC is a multi-day process with a contestable outcome;
   `retained = roll <= p` has no state that could be wrong for a fortnight and then corrected.
3. **No failure mode exists on the losing side.** `grep -iE "erroneous|objection|failed switch|rejected_switch"`
   over `simulation/` and `sim/` returns **one hit**, and it is a comment
   (`simulation/acquisition_funnel.py:71`). The world can neither raise an objection nor make an erroneous
   transfer, so the company's `transfer_objection_register` and `erroneous_transfer` have nothing to be right
   or wrong about.

The one place where the world *does* model a switching failure mode is the **gain** side.
`simulation/acquisition_funnel.py` (live: imported by `simulation/run_phase2b.py:79` and
`tools/generate_shadow_html.py:15`) runs `quote → application → credit_check → onboarding → cooling_off`, and
attrites at cooling-off through `ONBOARDING_TO_COOLING_OFF_SURVIVAL` — resi 0.80 pre-reform, 0.92 post. So
**the company can lose a switch it is gaining, and can never lose a switch it is losing.** That asymmetry is
the atom in one sentence.

**COUPLED TRIAD consequence.** The binding rule is that no world/SIM atom reaches L3 until the company has
been tested against it and the gap measured. There is no belief-vs-truth gap available here, because the
truth has no structure: the company's belief would be "this switch is in flight, may be objected, may prove
erroneous" and the world's truth is a boolean. **L3 is structurally unreachable for EP12 until the world
gains a switch event** — the same conclusion EP10 reached about UIG, arrived at from the opposite direction
(EP10's company half was rich and the world had no residue; here the company half is rich and the world has
no process).

---

## 3. DISCOVER — the wall carries the cause of a gain and discards the cause of a loss

**Observed**, `company/interfaces/sim_interface.py`:

```python
def notify_churn(self, account_id, event_date, *, reason="non-renewal",
                 sim_churn_probability=None, company_churn_estimate=None) -> None
def notify_acquisition(self, account_id, event_date, *, channel="market-acquisition",
                       predecessor_id=None) -> None
```

The gain primitive carries **`channel`** (`"home-move-win"` vs `"market-acquisition"`) and **`predecessor_id`**.
The loss primitive carries a free-text `reason` and nothing else — no gaining supplier, no switch reference,
no in-flight state, no reversibility.

**And at the one live production call site the `reason` is a constant.** `simulation/run_phase2b.py:1570-1588`:

```python
sim_interface.notify_churn(billing_account, term_start_str, reason="non-renewal", ...)   # 1570
if event.get("home_move_won"):                                                            # 1577
    successor_id = SUCCESSOR_MAP.get(billing_account)
    if successor_id:
        sim_interface.notify_acquisition(successor_id, term_start_str,
                                         channel="home-move-win", predecessor_id=...)     # 1583
```

`notify_churn` fires at line 1570 with the literal `"non-renewal"`, **unconditionally** — including on the
branch that four lines later establishes the departure *was* a home move. The world knows the cause at that
moment and throws it away on the loss leg while preserving it on the gain leg.

So the `origin_note`'s *"a switch and a tenancy change look identical from the company's side until they
don't"* understates HEAD: **on the loss side they are identical always, and there is no "until".** The company
receives the same six-character string either way.

**This is a fidelity gap, not the epistemic wall working.** A real supplier losing a customer to a competitor
is told so — a registration flow arrives naming a gaining supplier. A real supplier losing a customer to a
house move typically is not told at all, or is told late by the incoming occupier. The two are *distinguishable
with latency and error*, which is precisely the thing EP12 exists to model. Flattening both to `"non-renewal"`
is not the wall protecting the company from simulation internals; it is the wall having nothing to carry.
(**Inferred**, but the asymmetry with `notify_acquisition` — which does carry cause — is the internal evidence:
no wall doctrine distinguishes the two legs.)

---

## 4. DISCOVER — "CSS" means three different things in this tree

**Observed.** Three live modules are named `css_*` and only one of them is this atom:

- `saas/reporting/css_statement.py` (712 lines, **imported by `saas/reporting/annual_report.py:9290,9311`**) —
  **Consolidated Segmental Statement**, Ofgem SLC 19A. Live, published, nothing to do with switching.
- `company/crm/css_tracker.py` (170 lines) — **Customer Satisfaction Survey**, the Ofgem annual league table.
- `company/market/css_performance_register.py` (220 lines, 0 importers) — **Centralised Switching Service**.
  This atom.

A builder grepping `css` on the day EP12 opens hits the segmental statement first — the only one of the three
with live callers. Registering this now is cheaper than the mis-wiring it prevents. **Recommendation
(not executed, no BUILD this lane):** the eventual adapter is named for the *service*, not the acronym.

---

## 5. DISCOVER — the CSS cutover sits inside the replay window, and one constant knows it

**Observed.** The replay window is 2016–2025. The repo's only switching *message* vocabulary is
`company/market/dtn_log.py`, which is the **pre-CSS DTN/D-flow world**: `D0150` supply point registration,
`D0301Z` switch request, `D0001` meter read, `D0010` EAC/AA update. `company/market/mpas_standing_data_correction_register.py`
is the same era (`D0019` corrections, MPAS SLAs).

**External fact, carried from the atom's own dated source** (`docs/design/refs/ADVISOR_RESEARCH_COUNTERPARTY_APIS_EPOCH3_2026-08-05.md`,
marked ✓ verified live 2026-08-05): switching-adjacent APIs are administered through RECCo under the REC Data
Access Matrix, electricity CSS is operated by DCC, and gas Supply Point Switching access also runs through
RECCo. **Inferred by this pass:** a decade replay therefore crosses a *regime boundary* — the pre-reform
MPAS/DTN registration world and the post-reform REC/CSS world are different processes with different
timescales, and an adapter shaped only to REC message flows models the back half of its own replay window.

**The tree already knows this in exactly one place.** `simulation/acquisition_funnel.py:76` carries
`REC_REFORM_DATE = date(2022, 7, 1)` and switches `ONBOARDING_TO_COOLING_OFF_SURVIVAL` from 0.80 to 0.92 for
resi across it, with the module's own note that the reform shortened the objection/win-back window "from
~15-17 working days to next-working-day", confidence M on the regime fact and L on the rates, and explicitly
domestic-only (SME held flat at 0.90). **Observed:** `grep` for that date over `company/ simulation/ sim/ saas/`
finds the constant and its one use, and nothing else in the switching layer references the reform at all.

Two consequences:

- **The regime change is real, dated, and already parameterised — on the gain leg only.** The loss leg has no
  equivalent, which is the §3 asymmetry again in a different costume.
- **The date itself is an open item.** `2022-07-01` is a month-start; this pass did not verify it against the
  actual go-live and has no network to do so. Registered in §8, **not corrected** — correcting it is a BUILD
  edit to a live calibrated constant, out of scope for this lane, and the *shape* of the finding (one constant
  carries the whole regime) is what matters here.

---

## 6. FRAME — what the adapter has to be, and what has to exist first

The atom asks for a mocked adapter "shaped to REC message flows" so that go-live is a transport swap. That
framing is right and is **not the first move**. Ordered by what unblocks what:

**F1 — The world needs a switch event before the adapter has a counterparty.** Today a loss is
`retained = roll <= p`. The smallest world change that makes EP12 buildable is an exit that has a *cause* (a
competitor registration vs an occupier change), a *duration* (requested → effective), and an *outcome that can
be other than success* (objected, withdrawn, erroneous). Without duration there is no objection window;
without cause the `W2_12` coupling has nothing to confuse. **This is world work, not adapter work**, and it is
where the atom's gain actually lives — "an industry process with its own failure modes" is a statement about
the world, not about a client library.

**F2 — The wall's loss primitive needs the same shape its gain primitive already has.** `notify_acquisition`
carries `channel` and `predecessor_id`; `notify_churn` carries a constant string. Making the loss leg carry
its cause is a **seam change**, which is `EP6_wall_protocol_typing` — EP12's declared `depends_on`, **observed
at level 0**. The typed-message shape EP6 exists to introduce is exactly what an in-flight, reversible,
multi-step switch needs and what a single past-tense `notify_churn(...)` call cannot express. **EP12 cannot be
built as a wrapper over the current seam.** The dependency is real and correctly declared.

**F3 — Only then is the adapter the work,** and at that point it is small: the fourteen modules in §1 already
model the company's side of objections, erroneous transfers, CoS staging, MPAS standing data and CSS
performance. The BUILD move is to wire them to a world that produces the events, not to write them again.

**What the adapter does *not* need, and must not wait for.** REC eligibility, the Data Access Matrix, and REC
Code Manager confirmation gate the **transport** — a real authenticated connection to a real switching service.
They do not gate a mocked adapter, a world switch event, or a measured belief-vs-truth gap. The access class
is a reason EP12 cannot reach L3 *as an integration*; it is not a reason its coupled loop cannot be built.
(Same distinction EP10 drew about the Data Services Contract. `EP19_counterparty_qualification_paths` holds
the qualification path itself; nothing here duplicates that register.)

**The coupled pair, named.** WORLD: a switch with a cause, a duration and a failure outcome. COMPANY: its
existing CoS/objection/erroneous-transfer machinery, wired. HARNESS: the gap between *what the company believed
a departure was* and *what it actually was* — which is a measurable quantity the moment the world stops
sending `"non-renewal"` for everything, and is identically zero-information today.

---

## 7. A defect found, registered not fixed (SELF-INTERRUPT DISCIPLINE)

**Observed**, `simulation/run_phase2b.py:1577-1589`:

```python
if event.get("home_move_won"):
    successor_id = SUCCESSOR_MAP.get(billing_account)
    if successor_id:
        ...                      # win the successor
elif mandate_permits_replacement():
    ...                          # go to market for a replacement
```

`home_move_won` is rolled for **every** non-retained account (§2), but `SUCCESSOR_MAP` has **6 keys — `C1`–`C6` —
against 20 customers** (15 electricity, 5 gas; measured by import at HEAD). For the other 14, a `True` roll
takes the outer `if`, finds no successor, does nothing — **and the `elif` is never reached**, so the market
replacement is suppressed too.

The account is therefore lost with *no* successor and *no* replacement, and a `True` win roll produces a
strictly **worse** outcome than a `False` one. The realised home-move-win rate is also below the parameter for
those 14. Registered as a staged worker finding this pass; **not fixed here** — it is world BUILD code, this is
a doc-only lane, and the supply of found defects is infinite (the treadmill).

---

## 8. Open items — named, not glossed (R10)

1. **`REC_REFORM_DATE = date(2022, 7, 1)`** is unverified against the actual reform go-live and is the sole
   carrier of the regime change (§5). Needs network to check; not corrected this pass.
2. **The pre-2022 half of the replay window has no adapter shape at all.** The atom names only REC message
   flows; `dtn_log.py`'s D-flows are the earlier regime and are dead. Whether EP12 owns both regimes or only
   the post-reform one is **undecided and not decidable by this pass** — it is a curriculum question (R13).
3. **The gas half is thinner than the electricity half.** The atom names gas Supply Point Switching alongside
   electricity CSS; §1's fifteen modules are almost entirely electricity-shaped, and EP10 already found the
   gas industry-systems layer dead. The two atoms share a gas problem neither owns.
4. **`W2_12_change_of_tenancy_debt_physics` is at L1 `verify` and its world half is also absent** —
   `simulation/dd_balance_book.py:74-76` states in its own words that `TenancyChangeCoupler` has no production
   caller and the SIM has no tenancy-change stream. So **both sides of the `origin_note`'s coupling are missing
   from the world**, and the confusion the two atoms exist to model is not merely unmeasured but structurally
   impossible today. Whichever of EP12/W2_12 moves first should build the shared exit event, not two.
5. **The 165 tests in §1 are all direct-construction tests.** None of them would fail if the world never
   produced a switch, which is why the layer could sit dead and green. Not a mutation-test claim — no control
   here was mutated this pass — but the population an R15 pass should look at when EP12 opens.
6. **Freshness ceiling 2026-08-05** on every external claim, inherited from the single dated source.

---

## 9. What this pass changed

- Wrote this document.
- **Level HELD at 0**; `loop_stage` unchanged (`idle`); no `docs/design/maturity_map.yaml` edit.
- Appended the consolidation entry and repaired two dead evidence paths in
  `docs/design/simplifications/EP12_adapter_css_rec_switching.yaml` — **appended alongside, never over**
  (the store is append-only; both cited sources had moved, the known "archiving a document breaks every atom
  record that cited it" class).
- Registered the §7 world defect as a staged worker finding. No BUILD code, no world edit, no seam edit.
