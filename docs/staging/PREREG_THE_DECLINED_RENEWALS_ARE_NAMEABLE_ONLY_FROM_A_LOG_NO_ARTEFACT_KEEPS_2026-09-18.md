**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# PRE-REGISTRATION — emitting the declined renewals, and what I expect it to cost

**Filed:** 2026-09-18 ~02:4x UTC, before writing any code.
**Claim id:** `the-selection-leg-is-negative-and-nobody-has-asked-which-customers-it-loses-on`

---

## What I established before writing this, by measurement

The drawn item's part THREE assumes *"the per-seed and per-account arm values are ALREADY in the run
artefacts"*. **The per-account half of that is false, and I confirmed it independently rather than
taking the prior turn's word for it:**

| what I checked | how | result |
|---|---|---|
| does any floor artefact carry a per-account figure? | the 18-seed fold's seed rows | one row per seed, 12 scalar fields, no account |
| does any large artefact carry `value_arm_log`? | `json.dumps` scan of `s1_three_arm`, `current_book_2026-09-08`, `fixed_horizon_2026-09-08`, `se-merged-value-arms-20260911` | **`value_arm_log` absent from all four** |
| does the 28MB run log carry the decisions? | `grep -c declin /var/tmp/longjob-value-cycle-ab-20260910.log` | **0** |
| where do the declines exist at all? | `company/pricing/renewal_rate_chain.py:411-420` | built per renewal, extended into `phase2b["value_arm_log"]`, **counted and discarded** by `arm_decision_shape` (`tools/run_value_cycle_ab.py:3327`) |

So the 64 declined accounts are nameable from **no file on this machine**. "Name the customers" is
not answerable off disk today at any effort, and part THREE's decomposition is population-level or
nothing until a run emits the roster.

## The correction I am making to the prior turn's finding, and it changes the sequencing

`WORKER_RESULT_THE_SELECTION_LEG_DIFFERENCES_TWO_ARMS_OVER_DIFFERENT_PRICED_POPULATIONS_...` closes
by recommending exactly this emission, and argues it is safe to land now:

> *"it is a change to `tools/run_value_cycle_ab.py`, not to the pricing arm — so it does not split
> the family and can land while next12 is in flight."*

**That is refuted by this repo's own pairing predicate.** `tools/fold_noise_floor_family.py:365`:

```python
_VALUE_ARM_PATHS = ("simulation/", "company/", "saas/", "tools/run_value_cycle_ab.py")
```

The runner **is** the fourth watched path. Any edit to it makes `_value_arm_pairing` report
`same_value_arm: False` with `differing_paths: ["tools/run_value_cycle_ab.py"]` between a family
drawn before this commit and one drawn after. The claim that the emission is family-neutral is
false as the predicate is written.

**It does not block the work, and here is why I am proceeding anyway rather than escalating.**
`next12` is pinned at `7da627b90`, which the prior finding already measured as differing from the
eighteen's arm in **18 simulation files**. It is unpoolable already, and the drawn item's own
instruction is to read it **alone**. A family of one cannot be split. So the cost of this edit is
zero against the run in flight, and it is paid only by some future attempt to fold a
pre-2026-09-18 family with a post- one — which the eighteen's own provenance already forbids.

**But the predicate now has a false-positive class it did not have, and that is a finding, not a
detail.** `_VALUE_ARM_PATHS` is a *file-set* proxy for a *semantic* question ("were these rows
priced by the same instrument?"). It cannot distinguish the instrument from its instrumentation: a
change to the report assembly, which cannot move a single price, reads identically to a change to
`decide_margin`, which moves all of them. The one control that just caught the real £671 step will
now cry wolf on reporting-only commits, and a control that cries wolf is how the next real step
gets waved through. Filed separately as a finding; **not fixed in this turn**, because narrowing a
predicate that just earned its keep is exactly the asymmetric narrowing this project has a rule
against doing in the same breath as the change that triggered it.

## What I am building

1. **`decision_population` stops attributing the whole denominator gap to churn.** Its
   `the_mechanism` currently says "Sequential A/B roster divergence", and its
   `why_this_is_not_a_defect` says equalising *"would mean pricing renewals for customers who had
   already left"*. The prior finding proved both false for 64 of 67, from the reconciliation
   arithmetic **inside the same block**. The repair is to DERIVE the sentence from the split
   rather than assert it: compute `explained_by_declines` and `explained_by_roster` from the
   funnels, and let the prose name whichever dominates.
2. **A new `declined_renewals` block** naming every renewal the value arm declined, joined to the
   level arm's own decision on that exact renewal (key: customer_id, commodity, term_start).

## The predictions, written before the code runs

1. **The join will hit on most of the 64.** The two arms see the same eligible renewals — the prior
   finding established eligibility is identical — so a renewal the value arm declined should appear
   in the level arm's priced log unless that account had already churned off the level arm's book.
   I predict **≥ 50 of 64 join**, and I do not know the exact number.
2. **I will NOT be able to publish a money figure for what the declines are worth**, because
   `value_arm_entries` carries `chosen_margin_gbp_per_mwh` and no term volume. £/MWh is a rate, not
   money, and the two must not be multiplied by a volume this block does not have. The block will
   carry an honest `None` with that reason named. *If I find myself writing a pounds figure here,
   that is the defect this prediction exists to catch.*
3. **`decision_population.largest_denominator_difference` will not change.** I am changing what the
   block SAYS the gap is, not measuring the gap differently. If the integer moves, I have broken
   something.

## What this turn does NOT settle, stated so it is not read as settled

- **Part ONE is not done and cannot be.** `/var/tmp/value_cycle_ab_s1_noise_floor_next12_20260917.json`
  does not exist; PID 3819244 is still running; ETA 2026-09-18 11:31:24, ~8.5h after this turn. Its
  mean, sem and sems-from-zero are not reported here and are not guessed at.
- **Part THREE's "name the customers" is not delivered by this turn either** — it is *unblocked* by
  it. The roster exists only once a run executes this code. What is delivered is that the next run
  of any kind produces it, and that the artefact stops telling its reader a mechanism that is false
  for 96% of the gap.
- **The exact worth of the declines stays a bound.** Closing it needs term volume on the entry,
  which is a second change to a different writer.
