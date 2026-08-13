# EP4 — The collections journey: missed payment to resolution

**Atom:** `EP4_collections_journey` (lane `C_customer_ops`, value stream `meter_to_cash`,
dial 3, epoch 2, `level_current: 0`, `loop_stage: idle`)
**Stage:** DISCOVER + FRAME, lane-3 draw, 2026-08-13. **No BUILD code written** (epoch gating,
`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1).
**Level proposed:** held at **0**. Nothing was built; `MATURITY_MAP.md` §3 sets the L1 bar at
"been BUILT in any form". Saturation comes from this artefact being evidence-listed on the atom
record, not from a level bump — same disposition as `B7_customer_state_layer_moves_and_shocks`.

Every claim below is labelled `observed` (read off disk this tick, cited `file:line`) or
`inferred` (R9). Where a design doc and the disk disagree, the disk wins and the disagreement is
reported as a finding.

---

## 1. DISCOVER — what actually exists on disk

### 1.1 The WORLD operates the entire journey already `observed`

`simulation/arrears_engine.py` runs the full road end to end:

| Stage | Function | Line |
|---|---|---|
| stress → payment outcome | `payment_outcome` | `:370` |
| opening arrears position | `opening_arrears_stage` | `:452` |
| the dated stage cascade | `arrears_stages` / `ic_arrears_stages` | `:470` / `:498` |
| DCA recovery | `dca_recovered_amount` | `:253` |
| debt sale | `debt_sale_proceeds` | `:258` |
| post-write-off stages | `_post_writeoff_stages` | `:278` |
| emergent bad debt | `compute_emergent_bad_debt` / `apply_emergent_bad_debt` | `:519` / `:570` |
| recovery | `compute_debt_recovery` / `apply_debt_recovery` | `:612` / `:673` |

It also carries `debt_archetype` (`:205`) and a `_tone_for_bill` (`:338`) that reads the
company's collections tone back across the seam.

`inferred`: the world side of EP4 is not the gap. The world already decides, per customer, how
the arrears road ends.

### 1.2 The COMPANY observes the balance and never walks the journey `observed`

`company/billing/arrears_engine.py` (842 lines) is **half-wired**, and a module-level caller
count hides this. Function-level liveness, non-test callers only:

| Function | Line | Live caller |
|---|---|---|
| `age_open_items` | `:97` | `payment_observation_consumer.py:674,719` ✅ |
| `ageing_buckets` | `:216` | `payment_observation_consumer.py:723` ✅ |
| `dunning_path` | `:275` | **none** (tests only) |
| `current_dunning_step` | `:279` | only `arrears_engine.py:487`, itself unreached |
| `select_dunning_step` | `:470` | only `arrears_engine.py:826`, inside `collections_snapshot` |
| `collections_snapshot` | `:791` | **none** (tests only) |
| `build_write_off_event` | `:753` | **none** (tests only) |
| `build_interest_event` | `:685` | **none** (tests only) |

`collections_snapshot` is the function that assembles the company's whole collections view —
ageing buckets *plus* the current dunning step *plus* the undisputed overdue total
(`:798-800`). It is reachable only from tests. Its sole caller of `select_dunning_step`, and
that function's sole caller of `current_dunning_step`, form a chain whose head nothing pulls.

**So: the arithmetic half of the company's arrears engine is live; the decision half is dead.**
The company ages a balance in every run and places an account on a ladder in none.

This also means the module's substantial invariant library — `assert_dunning_requires_an_item`
(`:490`), `assert_dunning_path_valid` (`:530`), `assert_dunning_path_scope_valid` (`:550`),
`assert_write_off_audited` (`:615`), `assert_interest_is_b2b_only` (`:575`) — guards a code
path no run executes. `inferred`: these are R15 **FAIL-OPEN by vacuity** — they cannot fire,
because their subject set is empty in production. They are not wrong; they are waiting.

### 1.3 Six fully-built collections modules have zero non-test callers `observed`

Verified by import search (`from X import` / `import X`) excluding the module itself, then
re-checked with a loose name grep to catch indirect use:

| Module | Lines | Non-test importers |
|---|---|---|
| `company/billing/payment_plan.py` | 124 | **0** |
| `company/crm/vulnerability_index.py` | 122 | **0** |
| `company/finance/bad_debt_provision.py` | 105 | **0** |
| `company/billing/debt_referral.py` | 119 | **0** |
| `company/finance/debt_collection.py` | 122 | **0** |
| `company/finance/debt_age_analysis.py` | 105 | **0** |

The only non-test *mentions* of `bad_debt_provision.py` and `debt_collection.py` are **string
literals** in `company/finance/bad_debt_reconciliation.py:76,88` — the bridge names them as
paths, in data, and never imports or calls them (§1.4).

`PaymentPlan` / `PaymentPlanBook` / `PaymentPlanStatus` appear **nowhere** outside their own
module and its test. `inferred`: the payment arrangement — the single most important customer
outcome in a real collections operation, and the thing an Ofgem ability-to-pay assessment turns
on — exists as a class and has never been offered to a customer in any run.

### 1.4 The reconciliation bridge has already written EP4's contract `observed`

`company/finance/bad_debt_reconciliation.py:73-99` defines `UNWIRED_METHODS`, naming the two
dead provisioning methods and stating **exactly** what each needs to become reconcilable:

- `aging_matrix` → *"aged arrears positions per customer as_of a date (`ArrearsLedgerItem`:
  `outstanding_gbp` + `days_outstanding`), which no run currently emits — the arrears cascade in
  `simulation.arrears_engine` carries stage DATES but no aged open-balance snapshot the company
  observes."*
- `stage_recovery` → *"debt records by dunning stage (`DebtRecord`: `amount_gbp` + `DebtStage` +
  `stage_date`), i.e. a live dunning ladder placing accounts into
  initial_reminder/warning/pre_legal/DCA/legal/write_off — the ladder module has zero live
  callers, so no run produces stage-classified records."*

`inferred`: this is EP4's acceptance criterion, already written down by another lane and needing
no invention here. EP4 is done, in the part that matters to finance, when those two `needs`
strings are satisfied by a real run and `UNWIRED_METHODS` can be emptied. That the bridge
records its own blind spot in data — rather than fabricating inputs to fill it — is the pattern
to preserve, not to replace.

### 1.5 The obligations register asserts collections coverage by file existence `observed`

`company/compliance/obligations_register.py` carries the three physical-harm obligations this
journey generates:

- `ppm_self_disconnection` (`:408`)
- `winter_disconnection_moratorium` (`:425`) — tracker `company/billing/winter_moratorium.py`
- `disconnection_conduct` (`:441`) — *"ability-to-pay assessment, warning steps, PSR check before
  disconnection"*, Ofgem SLC 27, tracker `company/billing/disconnection_warning.py`

Coverage is computed at `:296-298`:

```python
if not obligation.tracker_paths:
    return False
return all(os.path.exists(os.path.join(_REPO_ROOT, p)) for p in obligation.tracker_paths)
```

Both named trackers exist on disk and **both have zero non-test importers** `observed`.

The register is honest about this — its own docstring at `:44` says `tracker_paths` are
*"repo-relative paths that must exist on disk"*. So this is **not** a concealed defect, and
should not be written up as one. It is a precise statement of scope: the register measures
tracker **presence**, never tracker **execution**. `inferred`: for most obligations those are
near-equivalent; for the collections obligations they are currently very far apart, because no
run takes a collections action at all. Closing that distance is EP4's compliance-side prize, and
§2.5 is where R10 attaches.

### 1.6 FINDING — the atom's own name misstates the evidence it cites `observed`

`docs/design/maturity_map.yaml:4138` says: *"D6/D7: wrongful-dunning exposure is ~10x the miss
rate"*. `docs/design/simplifications/D7_ageing_gap_metric_reshape.yaml:3` reports the live
400-customer / seed-7 measures as:

- `understated_arrears_rate` = **0.0725** (10 of 138 truly-overdue) — the miss rate
- `overstated_arrears_rate` = **0.0951** (101 of 1062 truly-current) — the wrongful-dunning exposure

The claim appears at **two** sites, not one `observed` — the second is the atom's own
`origin_note` in `docs/design/simplifications/EP4_collections_journey.yaml:3`: *"D7 already
measured that exposure at ten times the miss rate"*. Fixing only the map would leave the store
mirror asserting it.

The **counts** are 101 vs 10 → 10.1×. The **rates** are 0.0951 vs 0.0725 → **1.31×**. The two
measures sit on deliberately different denominators — that split is the whole point of the D7
reshape — so "10× the miss *rate*" attaches a count ratio to the noun "rate". D7's own wording is
correct and weaker: wrongful-dunning exposure *"exceeds its miss rate"*.

`inferred`: the substantive claim survives — overstatement is the larger exposure on either
reading, so EP4's motivation is undamaged. But the map's headline is off by ~8× as written, and
it is the sentence a reader meets first. This is the "one name, one number" class: a ratio taken
across two different denominators.

**Disposition: OPEN, deliberately not landed this tick.** The correction is a one-line edit to
`name` in `docs/design/maturity_map.yaml:4138`, replacing *"~10x the miss rate"* with
*"exceeds the miss rate (rates 0.0951 vs 0.0725; the 10x is a count ratio, 101 vs 10)"*. It was
**not** made, because `maturity_map.yaml` already carries another lane's **staged** hunk — an
`H_fabric`-family `level_current: 2 -> 3` move with a new `infeasible_here` block — and a
pathspec commit of that file would carry that lane's level move into this commit. R16 forbids
landing a `level_current` change whose self-certification this tick has not verified in
`gate_authorizations.jsonl`. Correcting an 8× error in a prose field does not justify that.
Whichever lane lands the staged hunk should make this edit alongside it; no code depends on the
string, so it can wait.

The second site (`EP4_collections_journey.yaml:3` `origin_note`) is editable without touching
the map, but was left alone too, on purpose: splitting the fix would leave the two mirrors
disagreeing, which is worse than both being wrong in the same way. **Fix both or neither** — and
both is a single small commit once the map is free.

---

## 2. FRAME — what EP4 has to be

### 2.1 The shape of the gap

The COUPLED TRIAD statement for this atom, in one line:

> **The world operates the journey; the company measures the balance; nothing in between exists.**

D5/D6/D7 built the company's *sensing* of arrears and the harness's measure of how wrong that
sensing is. EP4 is the *acting* half — and it is the half that generates every regulated harm.

### 2.2 The journey EP4 must make real, company-side

States, each of which must be a thing an account can BE, with a dated transition into and out of it:

```
 current ──miss──> overdue ──reminder──> dunning(ladder step N)
                                  │
                                  ├──cured──────────────> current
                                  ├──arrangement────────> paying-to-plan ──kept──> cured
                                  │                                       └─broken─> dunning
                                  ├──vulnerability hold─> held (ladder STOPPED, clock running)
                                  ├──referral───────────> DCA / debt sale
                                  └──write-off──────────> closed
```

Non-negotiable properties, each traceable to something already on disk:

1. **Placement is observable-only.** The ladder step is chosen from what the company can see —
   its own ledger, its own bills, its own bank feed — never from `simulation.*`. The seam is
   `company/interfaces/collections_communication.py` (already the one place the world may read
   the company's collections tone, `:83`).
2. **Every stage is dated.** `stage_date` is what `stage_recovery` needs (§1.4).
3. **The aged open-balance snapshot is emitted.** `ArrearsLedgerItem(outstanding_gbp,
   days_outstanding)` as-of a date — what `aging_matrix` needs (§1.4).
4. **A hold genuinely stops the ladder.** Not a flag that is read nowhere: R11's no-orphan-
   transitions rule — a hold whose release triggers nothing is a defect.
5. **The company may be WRONG.** It will dun customers who have paid (D7 measured 101 such
   accounts). That is allowed and is the point; the harness measures it.

### 2.3 What EP4 must NOT do

- **D5's sensing-only carve-out.** `DIRECTOR_STEER_DUNNING_DEBT_PROVISIONING_2026-07-25.md`
  records *"D5 stands: detection stays SENSING-ONLY, no collections action."* EP4 is exactly the
  atom that would lift that. `inferred`: the carve-out was scoped to D5's own build, not to all
  future work, but it is the closest thing to a standing constraint on this atom and the FRAME
  must not quietly assume it away. **Recommendation:** treat lifting it as EP4's first BUILD
  step, recorded via `decision_log`, not as an unstated side effect — it is reversible and
  simulation-internal, so it is not a wall.
- **No BUILD code this draw** (epoch gating).
- **Do not rebuild the six dead modules.** They are built and tested (§1.3). EP4 is a **wiring
  and journey** atom, matching the steer's own §0 verdict: *"mostly reconciliation and wiring,
  not new construction."* Anything that rewrites `payment_plan.py` rather than calling it should
  be challenged in review.
- **Do not tune to the D7 numbers.** R12: those are diagnostics, never targets.

### 2.4 Candidate decomposition (proposals, not mints)

| # | Sub-atom | Deliverable | Unblocks |
|---|---|---|---|
| 1 | ladder placement | `collections_snapshot` called in a real run; accounts carry a dated stage | `stage_recovery` |
| 2 | aged position emission | `ArrearsLedgerItem` snapshot as-of a date | `aging_matrix` |
| 3 | arrangement | `PaymentPlan` offered, kept/broken tracked | ability-to-pay evidence |
| 4 | vulnerability hold | PSR/`vulnerability_index` gates ladder progression | SLC 27 conduct |
| 5 | exits | cured / referral / write-off as dated terminal transitions | provision realisation |

`inferred`: 1 and 2 are the compounding pair — they are what `UNWIRED_METHODS` is blocked on, so
they convert two dead provisioning methods into live reconcilable ones. **They go first**
(COMPOUNDING_WORK_FIRST).

### 2.5 R10 — the class hook, as the origin_note demands

The atom's `origin_note` binds R10: an absurdity here (dunning a customer who has paid) is closed
by extending the obligations register so the CLASS fails, never by fixing the instance. Concretely
that means EP4 adds a **wrongful-dunning obligation** whose validator asserts, over the whole
population, that no dunning communication was issued against an account with no undisputed
overdue item — the invariant `assert_dunning_requires_an_item` (`:490`) already states, and which
today cannot fire because nothing dunning-shaped runs (§1.2).

`inferred` and important: that obligation must be validated by **execution, not presence** —
§1.5 shows the register's current coverage test is `os.path.exists`, which would pass on a
tracker nothing calls. An obligation added by EP4 that inherits only the existence check would
reproduce the exact vacuity EP4 exists to remove.

### 2.6 Exit tests (proposed, for the eventual BUILD)

1. A real run emits accounts at ≥3 distinct dunning stages, with dates. *(kills §1.2)*
2. `UNWIRED_METHODS` is empty, and the bridge reconciles all four provisioning methods. *(kills §1.4)*
3. At least one account reaches each terminal exit — cured, arrangement-kept, referral, write-off.
4. R15 mutation: an account with no undisputed overdue item that receives a dunning
   communication makes the wrongful-dunning obligation **fail**, proven on a mutant.
5. R15 mutation: a vulnerability hold that does not stop ladder progression **fails** a control.
6. The coupled gap for the EP4 pair is measured and published — the company's ladder placement
   vs the world's true arrears stage.

---

## 3. Disposition

- Level **held at 0**; nothing built.
- This artefact is evidence-listed on `docs/design/simplifications/EP4_collections_journey.yaml`.
- §1.6's map correction is **OPEN**, with the exact replacement text written down and the reason
  it was not landed recorded there. It is the one loose end this draw leaves.
- §2.3's D5 sensing-only question is named, recommended, and left for the BUILD draw to record
  via `decision_log` — it is not escalated, because it is reversible and simulation-internal
  (`one_way_door` defaults to act).
