# B7 — The customer state layer: house moves, income shocks, household composition

**Atom:** `B7_customer_state_layer_moves_and_shocks` (lane `W2_customer_generator`, dial 3, epoch 3,
`loop_stage: idle`)
**Stage:** DISCOVER + FRAME, lane-3 fork, 2026-07-29. **No BUILD code written** (epoch gating).
**Level proposed:** held at **0**. Nothing was built; `MATURITY_MAP.md` §3 sets the L1 bar at
"been BUILT in any form". Saturation comes from this artefact being evidence-listed, not from a
level bump — same disposition as `B8_discovered_price_sensitivity_holdout` on the same day.

Every claim below is labelled `observed` (read off disk this tick, cited `file:line`) or `inferred`
(R9). Nothing here is recalled from a spec doc; where a spec doc and the disk disagree, the disk wins
and the disagreement is reported as a finding.

---

## 1. DISCOVER — what actually exists on disk

### 1.1 The world emits no house move at all `observed`

`simulation/life_events.py:68-82` — the `EventType` Literal has thirteen members:
`solar_install, ev_acquired, boiler_replaced, heat_pump_installed, battery_installed,
smart_meter_installed, insulation_upgraded, job_loss, income_recovery, new_baby,
retirement_starts, illness, divorce`. **None is a move.** `_LIFE_EVENT_SUBSTREAMS`
(`:250-263`) registers twelve named substreams; none is a move. The generator loop (`:407-596`)
emits nothing move-shaped, and `apply_events` (`:601-693`) has no move branch.

So the atom's premise is confirmed at the source: W2_5 is at target (L3/3) and structurally cannot
emit the transition B7 exists to add.

### 1.2 `home_move_won` is not a home move `observed`

This is the finding that most contradicted expectation. `simulation/customer_events.py:136-141`:

```python
home_move_won = False
if not retained:
    win_roll = _random.Random(f"win_{billing_account}_{term_start_str}").random()
    home_move_won = win_roll <= renewal_data["win_probability"]
```

The `retained` decision at `:134` is rolled against a probability assembled from bill shock
(`saas.churn_model`), market switching conditions (`:109-111`), income stress (`:115-119`),
satisfaction (`:120-123`) and a retention offer (`:131-133`). **Not one of those is a house move.**
The "did we win the home-mover" roll then fires on *every* churn regardless of cause. The field name
asserts a causal story the mechanism never establishes.

`saas/home_move_win_rate.py:4-11` makes the conflation explicit in prose: it describes
`churn_model`'s output as "the probability that an account *doesn't* renew at each annual renewal
point — i.e. **the occupant moves out** ("churns")". So the codebase simultaneously holds that
100% of churn is a home move (for win-rate purposes) and that 0% of churn is a home move
(everywhere else). Both cannot be right, and neither is.

`inferred`: this is not a bug to patch in place. It is the absence B7 fills — once moves are a real
transition, the win roll becomes conditional on an actual move rather than on any churn.

### 1.3 The un-catchable-churn carve-out is unreachable in production — a live FAIL-OPEN `observed`

`simulation/churn_journey.py:56` defines `ChurnJourneyState.HOME_MOVE_CHURNED`, and `:152-165`:

```python
def record_home_move(self, as_of): ...          # sets HOME_MOVE_CHURNED
def is_catchable(self) -> bool:
    """False for home-move churns.
    A real supplier could never predict these from behavioral precursors,
    so they must be excluded from any recall/precision metric
    (docs/design/PROCESS_MODEL.md Section 2)."""
    return self.state != ChurnJourneyState.HOME_MOVE_CHURNED
```

`record_home_move` has **zero non-test callers**. The only invocations in the whole tree are
`tests/simulation/test_churn_journey.py:145,154`. The live run uses the register at
`simulation/run_phase2b.py:940, 1219-1226, 1370-1383, 1397` and never records a move.

Consequence, and it is a measurement defect rather than a cosmetic one: `is_catchable()` returns
`True` for **100% of live churns**. A carve-out designed to stop the company's churn-prediction
model being scored against churn nobody could predict is inert, so the model *is* being scored
against un-catchable churn — and the score is silently pessimistic by an unknown amount. This is the
textbook R15 **FAIL-OPEN** shape: a filter that passes vacuously because its target set is empty.
It is also the strongest single argument for B7: the harness already has the carve-out designed and
is waiting for a world that produces the thing it carves out.

### 1.4 The W2_12 DISCOVER doc's trigger claim is false, and the whole CoT chain is sourceless `observed`

`docs/design/W2_12_CHANGE_OF_TENANCY_DEBT_PHYSICS_DISCOVER.md:28` records:

> | **The trigger** — move events | `company/crm/life_events.py` (`LifeEventType.MOVE_IN` /
> `MOVE_OUT`; W2_5 dependency) | **Built.** Emits the events; nothing consumes them into the CoT
> debt/revenue path. |

Two errors, both load-bearing:

1. `company/crm/life_events.py:18-19` is on the **company** side of the wall. It is not W2_5;
   W2_5 is `simulation/life_events.py`, which (§1.1) has no move type. `maturity_map.yaml:569`
   accordingly records `depends_on: [W2_5_life_event_stream]` for W2_12 — a dependency satisfied by
   a module that cannot supply the trigger.
2. It does not *emit*. `company/crm/life_events.py:71-77` — `LifeEventLog.record` is a passive
   append the company calls; nothing in the tree generates a `MOVE_IN`/`MOVE_OUT` into it.

`inferred`: W2_12's DISCOVER concluded "all five components already exist separately" and named the
seam as a fan-out from an existing trigger. Four of the five do exist; the *trigger* does not, and
naming a company-side log as the world-side source is precisely the wall inversion the project
guards against — the company would be authoring ground truth about the world.

### 1.5 Five built CoT engines, zero live invocations `observed`

Grep for callers outside `tests/` of `change_of_tenancy_register`, `occupancy_register`,
`deemed_contract`, `account_closure`, `record_move_in`, `record_move_out` returns exactly two
non-test hits, neither of which is a call:

- `company/billing/credit_refund.py:12` — `ACCOUNT_CLOSURE = "account_closure"`, a reason string.
- `simulation/run_phase4c_on_phase2b.py:313` — a comment referencing `account_closure.py`.

The modules themselves are real and tested: `company/crm/change_of_tenancy_register.py`,
`company/crm/occupancy_register.py` (`:40,48` `record_move_in`/`record_move_out`),
`company/billing/cot.py` (`:51,69`), `company/billing/deemed_contract.py`,
`company/billing/account_closure.py`, each with a green test file. The pipe is built end-to-end
downstream of a source that does not exist. This is the **FAIL-SILENT** pattern in its purest form
— five engines, a full green suite, and nothing running.

### 1.6 The sim has no premise identity — the structural prerequisite is missing `observed`

`simulation/household.py:87-120` — `Household` is keyed by `customer_id` and carries no `mpan`,
`premise_id` or `supply_point` field. Grep across `simulation/household.py`,
`simulation/premise_demand.py`, `simulation/live_population.py`, `simulation/household_demand.py`,
`simulation/population_draw.py` finds no premise key anywhere in the world layer. The docstring at
`household.py:81-84` describes it as "Physical attributes of a customer's premises" — customer and
premise are one object.

By contrast `company/crm/occupancy_register.py:21,40` is keyed by **`mpan`**: the company side
already assumes a premise key that persists across occupants, and the world cannot supply one.

`inferred`: this is the single hard prerequisite for B7. A house move is by definition the event
where premise identity persists and occupant identity does not. It cannot be expressed against a
schema in which they are the same field. Everything else in this atom is downstream of that split.

### 1.7 Household composition is not modelled `observed`

`simulation/household.py:88-120` has `bedrooms` (a property attribute, not an occupancy one) and no
`occupants` / `household_size` / adults / children. The cohort axes actually drawn in
`simulation/population_draw.py:704-732` are `accommodation`, `cars`, `nssec`, `heating_fuel`, plus
`region` (`:614`) and `tenure_owner_split` (`:459`) — **no composition axis**.

`W2_13_occupancy_consumption_volume_shape` (`maturity_map.yaml:571-589`, L0, `loop_stage: discover`,
`blocked_on: director_level_up`) is the atom that would add a people-count response, and its own
DISCOVER records that occupancy today is a 3-category *shape-only* multiplier
(`simulation/demand_model.py:93,174-175`) that redistributes load without scaling volume.

`inferred`: B7's "household composition change" third cannot be built as a *change* until there is a
composition state to change. B7 and W2_13 must not each invent one. Ownership boundary proposed in
§4.

### 1.8 Income shock: the state exists, but 3-valued, single-cause, magnitude-free `observed`

`simulation/household.py:70-73` — `IncomeStress` is `LOW / MODERATE / HIGH`. There is no income
level, no shock magnitude, no duration. Six event types collapse into this one dial
(`life_events.py:508-595`), and `illness` explicitly shares `job_loss`'s recovery transition —
`life_events.py:196-203`: *"Recovery shares job_loss's own income_recovery transition (income_stress
is a single state variable in this model, not tracked per-cause)"*.

The dial is, however, already well-wired downstream — this matters, because it means B7's income half
is a *depth* problem, not a plumbing problem:

| Consumer | Cite | Effect |
|---|---|---|
| Arrears / debt archetype | `simulation/arrears_engine.py:75-95, 397, 428` | archetype classified from the `income_stress_trajectory` **shape** |
| Bad-debt multiplier | `simulation/payment_timing.py:48-53` | payment-outcome weighting |
| Switching propensity | `simulation/customer_events.py:115-119` | churn probability adjustment (with tenure) |
| Satisfaction | `simulation/sim_satisfaction.py:81-82` | score delta |
| Survey response | `simulation/feedback_survey.py:58-59` | response-propensity multiplier |

So "income shocks drive switching, arrears and consumption" is *partly true today* — switching and
arrears yes, consumption no (nothing in the demand path reads `income_stress`; the nearest thing is
`simulation/self_rationing.py`, a separate atom). B7 must add magnitude and duration, and the
consumption leg, without re-registering the wiring that exists.

### 1.9 C-S2 substream audit — W2_5 is compliant; two gaps `observed`

**W2_5 is clean.** `life_events.py:266-277` derives each substream from
`sha256(f"{base_seed}:{name}")`, per event type, per household, with a stable base seed
(`:280-288`, md5 of `customer_id`, explicitly not Python's salted `hash()`). The 01:09Z
shared-econ-RNG incident is structurally fixed there, and the module says so (`:33-40`). Adding a
name cannot shift an existing stream.

Two gaps found, neither previously registered:

- **Un-namespaced key space.** `life_events.py:276` keys on bare `f"{base_seed}:{name}"` with no
  stream-name prefix. Compare `population_draw.py:152` (`f"{STREAM_NAME}:{salt}:{base_seed}"`) and
  `:400` (`f"{COHORT_STREAM_NAME}::{axis}::{customer_id}::{base_seed}"`). Any future module that
  seeds on the bare pattern with a colliding name silently shares W2_5's stream. `inferred`: not a
  live defect (no such module exists today), but it is a trap B7 must not walk into — B7 namespaces.
- **Ad-hoc seeds outside any registry.** `customer_events.py:98,140` construct
  `_random.Random(f"{billing_account}_{term_start_str}")` and `f"win_{...}"` inline. These are
  isolated by construction (a fresh `Random` per call, and `Random(str)` seeds stably rather than via
  `hash()`), so there is no cross-contamination — but they are enumerable by no test and registered
  in no substream tuple, so the C-S2 *contract* does not cover the churn roll or the win roll. B7
  touches this call site and should bring it into the registry on touch (remediation-on-touch, not a
  speculative retrofit).

### 1.10 The generation-order vs date-order defect applies to moves, and worse `observed`

`life_events.py:407-596` evaluates event types in a fixed within-year order, mutating a running
`income_stress` as it goes, then date-sorts only at `:597`. `apply_events` re-sorts by date
(`:620`). So a `job_loss` whose random date lands in November still gates off a `new_baby` whose
date would have been March — the generator's *evaluation* order is not its *chronological* order.
This is the queued latent already flagged on W2_5's row.

`inferred`: a move is strictly worse than this class, not merely an instance of it. A move
**terminates** an occupancy, so every event the generator already emitted for that occupant later in
the same year becomes retro-invalid — not merely mis-gated. A move cannot be added as a fourteenth
peer inside the same yearly loop. It must sit *above* the life-event generator and define the window
within which life events are generated at all. That is the design consequence §3 turns into
structure.

---

## 2. What EXISTS vs what does NOT — summary

| Capability | Status | Cite |
|---|---|---|
| Physical-adoption events (solar/EV/HP/boiler/insulation/battery) | **Exists**, named substreams | `life_events.py:409-506` |
| Economic events (job loss/recovery/baby/retirement/illness/divorce) | **Exists**, residential-gated, named substreams | `life_events.py:508-595` |
| `income_stress` → arrears, switching, satisfaction, survey | **Exists** | §1.8 table |
| `income_stress` → **consumption** | **Does not exist** | no demand-path reader |
| Income shock **magnitude / duration / income level** | **Does not exist** | `household.py:70-73` |
| Household **composition state** | **Does not exist** | §1.7 |
| **Premise identity** distinct from customer identity | **Does not exist** | §1.6 |
| **House move** as a world event | **Does not exist** | §1.1 |
| Move → credit exit (final bill, non-payment risk) | Engine exists, **no source** | §1.5 |
| Move → two deemed entries | Engine exists, **no source** | §1.5 |
| Move → CoT register fan-out | Engine exists, **no source, false trigger claim** | §1.4, §1.5 |
| Home-move **win** roll | Exists but **fires on all churn** | §1.2 |
| Un-catchable-churn carve-out | Exists but **unreachable → fail-open** | §1.3 |
| Company-side move DETECTION hook | `metering_changed` flag exists, **never set True** | `company/crm/life_event_detector.py:89-90` |

---

## 3. FRAME — the mechanism

### 3.1 The identity split (the load-bearing move)

Introduce two identities where there is currently one:

- **`premise_id`** — persistent, immortal, carries the physical `Household` attributes
  (property type, build era, EPC, heating, insulation, solar/battery/EV where they are fixtures),
  the MPAN/MPRN, and the consumption physics. **A premise never moves.**
- **`occupancy_id`** — mortal. Carries the *people*: `income_stress` and its new magnitude/duration
  fields, composition, tenure, behavioural attitudes, the billing relationship. An occupancy has a
  start date and (usually) an end date.

`customer_id` becomes the *billing account* for one occupancy at one premise, not a synonym for
either. Portability lens (`PORTABILITY_DESIGN_CONSTRAINTS`): the split is by function, not by fuel
or market — a second market plugs in behind the same seam, and a dual-fuel or multi-product occupancy
holds several supply points under one occupancy without a second engine.

**Migration is the risk, and it is a real one.** Today's roster keys everything on `customer_id`
(`household.py:87`, `population_draw`, `household_demand`, the settlement path). `inferred`: the
cheapest honest route is that a premise with exactly one lifetime occupancy is *byte-identical* to
today — `premise_id == occupancy_id == customer_id` — so the existing 24-customer authored roster
and every current run reproduce exactly, and only a premise that actually experiences a move
diverges. That is the same "default is byte-identical to no change" discipline
`life_events.py:346-355` used for the adoption multiplier, and it must be a test, not an intention.

### 3.2 The move transaction — one exit, two entries

A move at premise **P** at date **d**, for occupancy **O**:

1. **`occupancy_ended(O, P, d)`** — the **credit exit**. Final read (or an estimate, if no read is
   taken — the interesting case), final bill, and a modelled outcome for whether that final bill is
   ever paid. This is the "credit-risk exit" half of the director's double jeopardy.
2. **`occupancy_started(O', P, d + void_gap)`** — a new occupancy at the **vacated** premise,
   drawn fresh from `population_draw` (never copied from `O` — the incoming occupant is a stranger).
   Lands on a **deemed contract** until they contract or switch. `void_gap` may be zero, positive
   (a genuine void period, where the premise consumes with nobody contracted), or negative-ish in
   the sense of overlapping paperwork — the void case is the one that generates the
   settlement-volume-vs-billed-volume discrepancy the company must discover.
3. **`occupancy_started(O, P', d)`** — the mover's **new home**. Whether `P'` is in the company's
   book at all is a draw: mostly it is a premise served by someone else (out of book, so from the
   company's view the customer simply vanished), sometimes it is another premise on the book (the
   high-value acquisition moment W2_12 names). Also lands on a deemed contract.

Two `occupancy_started` events per move ⇒ **two deemed entries**, one credit exit. That is exactly
the BACKLOG B7 exit test and the director's verbatim W2_12 frame, and it falls out of the identity
split rather than being asserted.

**The `home_move_won` roll is re-founded, not deleted.** After B7, "did we win the mover's business"
is a question about event (3) — did the mover's *new* premise land on our book — and "did we keep
the premise" is a question about event (2) — did the *incoming* occupant stay deemed with us or
switch away. Today one roll (`customer_events.py:140`) stands for both, on a churn that was not a
move. `saas/home_move_win_rate.py:38-41`'s `BASE_WIN_PROBABILITY` finally gets a real event to be
scored against instead of being the thing that defines the event.

### 3.3 Life events live *inside* an occupancy window

Per §1.10, the move layer sits **above** `simulation/life_events.py`, not inside it. The generator is
called with the occupancy's `[start, end)` window and emits only within it. A new occupancy gets its
own event stream from its own base seed. This resolves the retro-invalidity problem structurally
rather than by ordering care, and it means B7 **must not** append a fourteenth name to
`_LIFE_EVENT_SUBSTREAMS` (`life_events.py:250-263`) — that tuple is per-customer-per-year physical
and economic events, a different layer.

### 3.4 Income shock as a first-class transition

Keep `IncomeStress` (five consumers depend on it, §1.8; breaking them is not this atom's job) and add
beside it, on the occupancy:

- **magnitude** — the proportional income drop, so a reduced-hours shock and a redundancy are not
  the same event;
- **duration** — drawn at onset, so recovery is a *scheduled* transition rather than an independent
  annual 50% coin-flip (`life_events.py:177-178` `_INCOME_RECOVERY_ANNUAL_PROB = 0.50`, which
  produces a geometric spell length that is a simplification, not a fact about UK unemployment
  spells);
- **the consumption leg** — the missing wiring from §1.8: a severe, sustained shock changes kWh
  (self-rationing already exists as its own atom, `simulation/self_rationing.py`, so B7 supplies the
  *shock signal* and must not duplicate the rationing physics).

`IncomeStress` is then a *derived view* of (magnitude, duration) rather than the primitive — which
keeps every existing consumer working unchanged while giving the harness something with resolution
to measure a belief against.

### 3.5 Household composition change

Ownership boundary, to stop B7 and W2_13 each inventing a schema: **W2_13 owns
composition → consumption volume and shape** (it has the DESNZ NEED / EFUS anchors already in its
DISCOVER). **B7 owns composition as a state that *transitions*** — the household forms, grows,
shrinks, dissolves. B7 therefore defines the composition field on the occupancy and the transition
events; W2_13 reads it. If W2_13 builds first, B7 adds transitions to its field. Neither should
proceed without checking the other, and this paragraph is the check.

---

## 4. R13 — BASELINE vs CURRICULUM

**BASELINE** (fidelity-to-reality only; changeable *only* blind to company P&L; every one of these
must be externally sourced at BUILD and must **not** be invented — this FRAME deliberately states no
numbers):

- annual move hazard **by tenure** (private rent ≫ social rent > owner-occupier — the mechanism
  matters more than the level, and `population_draw.py:459` already draws tenure, so the join exists)
- the void-gap distribution between occupancies
- p(final bill never paid) at move-out, and its dependence on prior payment behaviour
- the notification-lag distribution — how long before the supplier is told, **including the fraction
  never told at all** (this is the parameter the whole detection gap hangs on)
- deemed-period duration before a new occupant contracts or switches
- income-shock magnitude and duration distributions
- household formation/dissolution rates
- the consumption response at a premise across a change of occupant

**CURRICULUM** (director-reserved; the agent must not choose a value, and must not adjust one because
company results look wrong):

- the tenure mix of the book — a 60%-private-rent book has several times the move rate of an
  owner-occupier book, so the *population draw* is the real difficulty dial here, and it is already
  a curriculum instrument (`live_population.py:17`, `population_draw.py:51`)
- any named scenario that dials move rates or income-shock severity (a recession replay, a
  rental-churn spike)
- **whether the move layer is ACTIVE in a live run at all.** Precedent is explicit and on-point:
  `life_events.py:346-355` holds live-run wiring of the adoption multiplier as director-reserved
  curriculum, "matching the precedent on W2_2_population_draw's maturity-map history — this parameter
  is the tested MECHANISM, item 5 is the activation". B7 builds the mechanism; activation is a
  separate, director-facing step.

**Neither** (flagged so it is not silently reclassified): `saas/home_move_win_rate.py:38-41`
`BASE_WIN_PROBABILITY` and `:47-55` `PRICE_SENSITIVITY_BY_EPC` are **company-side competitive
assumptions**, not world physics — currently imported into the world's roll by
`customer_events.py:89`, which the module's own docstring (`:17-22`) admits as a deliberate
cross-seam import. `inferred`: after B7 the *outcome* (does the incoming occupant stay?) should be
world physics informed by the company's observable price position, and the saas constant should be
the company's *belief* about that outcome — i.e. a thing to be scored, not the scorer. Logged as
portability/seam debt for remediation-on-touch, not fixed speculatively here.

---

## 5. C-S2 — named RNG substreams

Stream namespace `customer_state` (a module-level `STREAM_NAME`, following
`population_draw.py:152` rather than `life_events.py:276`, per §1.9). Every substream is keyed
**per-premise or per-occupancy, not sequentially**, so the layer is callable standalone, in any
order, for any premise — the `_cohort_substream` pattern (`population_draw.py:390-401`) that has
already survived contact:

| Substream key | Draws |
|---|---|
| `customer_state::move_hazard::<premise_id>::<occupancy_seq>::<base_seed>` | does this occupancy end in year Y |
| `customer_state::move_date::<premise_id>::<occupancy_seq>::<base_seed>` | when within the year |
| `customer_state::move_destination::<occupancy_id>::<base_seed>` | mover lands in-book / out-of-book |
| `customer_state::incoming_occupant::<premise_id>::<occupancy_seq>::<base_seed>` | attributes of the new occupancy (delegated to `population_draw`, never copied from the outgoing one) |
| `customer_state::void_gap::<premise_id>::<occupancy_seq>::<base_seed>` | days the premise sits unoccupied/uncontracted |
| `customer_state::final_bill_outcome::<occupancy_id>::<base_seed>` | paid / partial / never paid |
| `customer_state::notification_lag::<occupancy_id>::<base_seed>` | days until the supplier is told, incl. never |
| `customer_state::deemed_duration::<occupancy_id>::<base_seed>` | time on deemed before contracting/switching |
| `customer_state::income_shock_onset::<occupancy_id>::<base_seed>` | does a shock start |
| `customer_state::income_shock_magnitude::<occupancy_id>::<base_seed>` | how deep |
| `customer_state::income_shock_duration::<occupancy_id>::<base_seed>` | how long (recovery is scheduled, not re-rolled annually) |
| `customer_state::composition_change::<occupancy_id>::<base_seed>` | formation / growth / shrink / dissolution |

Binding constraints, each falsifiable:

1. **Never extend `_LIFE_EVENT_SUBSTREAMS`.** §3.3 — different layer, and a move terminates the
   stream rather than joining it.
2. **Namespaced keys.** A B7 substream name must never be constructible as `f"{seed}:{name}"`
   (§1.9), or it shares W2_5's key space.
3. **Onset and magnitude are separate substreams.** Folding magnitude into the onset draw means
   changing the magnitude distribution shifts *which customers* get a shock — the 01:09Z incident's
   exact shape, one level down.
4. **A test enumerates the registry** and asserts that adding a name leaves every other stream's
   first N draws byte-identical — the `test_substream_isolation_*` pattern
   (`population_draw.py:39`).

---

## 6. Epistemic wall — what the company can and cannot see

**CAN observe** (all real supplier-side records):

- a final meter read, *if one is taken* — and the estimate used when one is not
- an inbound contact: "I'm moving out on the 14th" (the notification, subject to lag and to never)
- a cancelled direct debit
- a consumption discontinuity at an MPAN
- an unpaid final bill, and the age of it
- a new named person registering at a premise it already serves
- **settled volume at a premise with nobody contracted** — how a supplier discovers a void it was
  never told about
- an industry change-of-supplier flow when the incoming occupant switches away

**CANNOT observe:**

- the move date, until told (and sometimes never)
- *why* the occupant moved
- the departing occupant's forwarding address unless given — so it cannot tell "moved and defaulted"
  from "moved and we never billed them"
- the incoming occupant's income, composition, tenure or attitudes — it must re-discover all of it,
  which is precisely what makes a move the prime acquisition moment
- whether a premise with no read for three months is void, vacant, or simply unread
- the income shock — only its shadow in payment behaviour, months later

**Seam contract.** The move crosses as a typed observable on a new `premise_occupancy_seam`,
modelled on `interface/contracts/conversation_seam.py` / `payment_observable_seam.py`, carrying a
`FORBIDDEN_TRUTH_FIELDS` tuple that must include at minimum: `move_date`, `move_reason`,
`occupancy_id`, `income_shock_magnitude`, `income_shock_duration`, `household_size`,
`outgoing_occupant_id`, `void_gap`.

The company-side hook already exists and is inert: `company/crm/life_event_detector.py:89-90`
declares `metering_changed: bool  # A metering / MPAN change occurred (change of tenancy, occupancy
change)` and nothing in the tree ever sets it `True`. B7 is what makes that field mean something.

**The company is allowed to be wrong**, and the wrongness is the point: bill the wrong occupant,
chase a departed customer's debt against the new one (the double-jeopardy harm), miss a void for
months, treat a move-out as a price-driven churn and waste a retention offer on someone who has
already left the country.

---

## 7. COUPLED TRIAD

**SIM depth** (this atom, `W2_customer_generator`): premise/occupancy identity split; move hazard by
tenure; the one-exit-two-entry transaction with void gaps and final-bill outcomes; income shock with
magnitude and duration; composition transitions. All behind the wall, all on named substreams, all
deterministically replayable.

**COMPANY discovery through the wall** (couples to `C7_life_event_detection` and to W2_12's CoT
stack, which finally acquires a source): the company must infer from observables alone that a
premise has changed hands — final-read request, DD cancellation, consumption discontinuity,
unbilled-but-consuming premise, inbound call — and then run its own CoT process
(`company/crm/change_of_tenancy_register.py`, `company/billing/cot.py`,
`deemed_contract.py`, `account_closure.py`). Its detection will be late, incomplete and sometimes
wrong. **Nothing in `company/` may import the move stream.**

**HARNESS gap measurement** — a `tools/couple_b7_c7.py` in the existing `tools/couple_*` family
(placed in `tools/` so the epistemic verifier does not scan it as company code), reporting three
numbers via `background/gap_metric.py`:

1. **Detection lag** — days between the world's move date and the company's CoT registration, plus
   the never-detected fraction. Family `detection` (`gap_metric.py:39,333`).
2. **Misattribution harm** — £ of final-bill debt pursued against the wrong occupancy. Asymmetric
   and signed: chasing an innocent incoming occupant is a Consumer Duty harm, not a clerical error,
   so it is scored through `gap_metric.py:162 harm_cost` with a **stated, derived** harm ratio, not
   a declared one.
3. **Catchability honesty** — the fraction of churn the company's prediction model is scored on that
   was genuinely un-catchable. This is exactly the number `churn_journey.is_catchable()`
   (`:158-165`) was built to produce and today cannot (§1.3). Closing this is arguably the highest-
   value single output of the atom, because it corrects a *currently published* company metric.

Triad rule check: no world atom reaches L3 until the company has been tested against it and the gap
measured. B7 therefore cannot reach L3 on world depth alone — legs 2 and 3 above are part of the
atom, not a follow-on.

---

## 8. R15 — controls, and how each must be made to FAIL

Every control below is stated with its named defect and the concrete mutation that must turn it RED.
A control without a passing mutation test is not evidence.

### TAUTOLOGY risks

- **Detection-gap fed by the truth.** If the seam carries `move_date`, the company's "belief" about
  the move date is the world's move date and the lag is identically zero. *Mutation:* add
  `move_date` to the seam payload — the `FORBIDDEN_TRUTH_FIELDS` test must fire. *Second leg,
  because an import-only wall test is fail-open against a value laundered through a caller
  argument* (the exact hole B8's FRAME identified at `run_phase2b.py:1163-1172`): an
  identical-observations-identical-belief test — two runs with different hidden move dates but
  identical observables must produce identical company beliefs.
- **Two-deemed-entries asserted against its own constructor.** A test that counts the deemed
  entries the move function just created proves only that the function ran. *Mutation:* have the
  transaction create the entry objects but bill neither at a deemed rate — a self-counting test
  stays green. The real assertion is on the **billing outcome**: two accounts billed at deemed rates
  over the correct, non-overlapping windows, reconciling to the premise's settled volume.
- **Harm ratio declared rather than derived.** Set the misattribution harm ratio to 1.0 and the
  ranking of outcomes must change; if it does not, the ratio is decorative.

### FAIL-OPEN risks

- **The vacuous carve-out — this class is already live, §1.3.** Any control of the form "all
  home-move churns are excluded from recall" passes trivially when zero moves exist. *Mutation:*
  run with the move layer emitting zero moves — the control must go **RED**, which requires it to
  assert the move set is non-empty *before* asserting anything about its contents. This one control
  would have caught the current defect.
- **Reconciliation with no rows.** "Final bills reconcile to premise consumption" passes when there
  are no final bills. Same fix: non-emptiness is part of the assertion.
- **Non-finite / missing dates.** A `None` or NaN move date must be rejected **explicitly and
  first**, never left to a comparison guard — NaN compares False both ways and sails through.
  `life_events.py:370-384` is this project's own worked precedent for the fix, and its comment
  explains why operand order made the original safe only by luck.
- **Malformed hazard parameters.** A negative or >1 move probability must fail closed (no moves),
  not clamp silently to something plausible.

### FAIL-SILENT risks

- **The layer inactive while every test is green — the current state of the entire CoT stack
  (§1.5).** The control must be an **invocation check on real run output** (moves emitted per run
  > 0 whenever the layer is active, asserted against the run artefact, not a unit fixture), because
  five green test files and zero live calls is the observed status quo, not a hypothetical.
  *Mutation:* disable the layer's call site while leaving its tests intact — the run-output check
  must go RED and every unit test must stay green, demonstrating that only the run-level control
  catches it.
- **Silent RNG degrade.** If the substream module import fails, any `try/except` fallback to a
  shared or global RNG must be a hard error. *Mutation:* make the registry import raise — the run
  must abort, not proceed non-deterministically.
- **Replay divergence unmeasured.** *Mutation:* introduce one wall-clock or unseeded draw into the
  move path — a replay-determinism test over a full run must go RED.

---

## 9. Other standing constraints

- **C-S1 (event-arrival tolerance):** the company's CoT process must behave correctly if the final
  read, the notification and the new registration arrive singly, late, and out of order — which is
  the *normal* case for a move, not an edge case. No company-side logic may assume it learns of the
  three parts together.
- **C-S3 (asynchronous wall contracts):** the notification and the company's response are separate
  events in time. A move must never resolve same-step.
- **C-S4:** occupancy state persists via the append-only event-log abstraction.
- **C-S5 (time-scale invariance):** move hazards are annual and the settlement clock is half-hourly.
  Any L3+ claim must state whether the move layer is time-scale invariant, or register the exception
  as a named simplification (R10).
- **R12:** detection lag and misattribution harm are **diagnostics**. No detection threshold may be
  tuned to make the lag look shorter, and the move rate may never be adjusted because bad debt came
  out too high.

---

## 10. Open questions for BUILD (registered, not answered)

1. Does the identity split land inside `simulation/household.py` or in a new
   `simulation/premise_occupancy.py`? The FRAME's byte-identical-default requirement (§3.1) is
   satisfiable either way; the migration blast radius decides it.
2. Do the four uninvoked CoT engines (§1.5) get wired by B7, or does B7 emit the events and W2_12
   own the wiring? W2_12 is `blocked_on: director_level_up` at L0, so B7 must not assume it moves
   first. Recommendation `inferred`: B7 emits and provides the seam; W2_12 consumes. Registering the
   dependency direction now prevents both atoms building the same fan-out.
3. Should `home_move_won` (`customer_events.py:182`) be renamed at the same time? It is a published
   field name asserting a false cause. `inferred`: yes, but as a separate touch — renaming a field
   in the run artefact has its own consumers.
4. Sourcing for every BASELINE parameter in §4 remains **entirely open**. This FRAME states no
   numbers on purpose; inventing a move rate would be exactly the fabrication R13 exists to prevent.
