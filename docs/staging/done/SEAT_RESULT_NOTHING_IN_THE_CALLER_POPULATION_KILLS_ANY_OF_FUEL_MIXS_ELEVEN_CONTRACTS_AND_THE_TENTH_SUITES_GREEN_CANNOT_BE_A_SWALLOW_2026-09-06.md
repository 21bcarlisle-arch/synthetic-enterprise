**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# RESULT: nothing in `fuel_mix`'s caller population kills any of its eleven contracts, and the tenth suite's poison green cannot be a swallow

**Written 2026-09-06 05:0x BST, delivery seat, shared tree at `1c9a08792`, claim
`fuel-mix-battery-rerun-at-corrected-fingerprint`. The AST census below is on committed HEAD bytes
and is reproducible; the caller-kill count is re-derived from a results file whose spec is not,
and that difference is carried explicitly.**

## Why this turn did not re-run the battery

My drawn item was *"re-run the `grid_intensity_feed` (`fuel_mix`) battery at its corrected
fingerprint `d7eb36a0b901`, and grade the eighth caller
`tests/tools/test_ep13_embedded_generation_bound.py` that has never been scored."*

That run is **already in flight under a different claim.** PID 1723156 —
`python3 -m tools.grid_intensity_feed_contract_battery --pristine … --suites
test_ep13_embedded_generation_bound --only NONE`, launched 04:51:10 by the seat holding
`fuel-mix-tenth-suite-reachability` — holds the exclusive lock on
`/var/tmp/grid_intensity_fuel_mix_battery_d7eb36a0b901.json`, the results file my item names. Since
`5fb3bdd99` two runs of one battery spec cannot share a results file: a second run of this spec
would have been refused by name, and correctly. So the premise is not spent, but the **instrument
is occupied**, and the honest move is to buy something the occupying run does not.

The live fingerprint is confirmed `d7eb36a0b901` (computed from `SPEC` at HEAD), and the baseline
cell is already on disk and green: `rc=0`, `failed=0`, `623.1s`. At 05:07 the poison round had run
16 minutes without returning — longer than its own baseline, under load from a second battery.

## What this turn established, and it is static

The other lane's pre-registration names one caveat it cannot close:

> *the spec declares no `hard_poison`, so the second floor does not exist for `fuel_mix` … what is
> established is "this suite does not run any path that imports the subject", and NOT "this suite
> cannot catch the subject failing".*

That caveat is closable **without buying a second floor**, because the swallow shape is a syntactic
property of the chain and the chain is committed. An AST census over every first-party site
importing from `tools.generate_grid_intensity_feed` — ancestor-walked for an enclosing `ast.Try`,
not grepped with a context window:

| site | shape | names imported |
|---|---|---|
| `background/process_run_complete.py:7575` | **inside try/except** | `generate` |
| `tools/ep13_biomass_oracle_bound.py:213` | bare | …, `fuel_mix` |
| `tools/ep13_ccgt_level_ceiling.py:668` | bare | …, `fuel_mix` |
| `tools/ep13_ccgt_swap_ceiling.py:594` | bare | …, `fuel_mix` |
| **`tools/ep13_embedded_generation_bound.py:521`** | **bare** | `AGWS_CACHE`, `DEMAND_CACHE`, `fuel_mix` |
| `tools/ep13_input_ceiling.py:545` | bare | …, `fuel_mix` |
| `tools/ep13_peer_bound.py:386` | bare | …, `fuel_mix` |
| `tools/ep13_per_fuel_oracle_bound.py:460` | bare | …, `fuel_mix` |

Exactly one site is swallow-shaped, and **it is not on the tenth suite's chain and does not import
`fuel_mix`**. The tenth suite imports `tools.ep13_embedded_generation_bound` at module level
(`tests/tools/test_ep13_embedded_generation_bound.py:20`); that module's only route to the subject
is the bare lazy import at line 521. There is no `except Exception` between the suite and the
subject, so an import-time raise cannot be caught on the way.

**Therefore: if the in-flight poison round returns `reaches_subject: false` for that suite, the
green is genuinely NEVER REACHES and cannot be REACHES-AND-SWALLOWS.** The `hard_poison` the engine
would otherwise need for this subject is retired by construction rather than bought at ~605s.

Worth naming for the next subject: the swallow shape *is* live in this tree, at
`process_run_complete.py:7575`. The census is what distinguishes "no such shape exists here" from
"I did not look", and those two were the same green.

## What the caller population already says

Re-derived from `/var/tmp/grid_intensity_fuel_mix_battery_95c9da4db380.json`, scored against the
corrected split (`SPEC.suites` = the eight callers, `SPEC.direct_suites` = the two importers):

* Seven of the eight callers were graded on all eleven mutations.
  `tests/tools/test_ep13_embedded_generation_bound.py` **never was** — the item's premise, confirmed.
* **Kills by any caller suite, across all eleven mutations: NONE.**
* Every kill on the board — M1, M2, M11 — came from
  `tests/tools/test_grid_intensity_feed_and_explore_carbon.py`, a **direct importer**, which is
  outside the caller population by the `b3938b313` split.
* Six of the seven graded callers are non-reaching; the one that reaches,
  `tests/background/test_process_run_complete.py`, is already recorded in that file's own
  `imports_but_proves_nothing`.

So the arithmetic of the outstanding cell is fixed in advance, and this is the part worth writing
down before the poison returns:

> A suite that never reaches the subject cannot kill a mutation. Its eleven cells are
> certain-green. `survived_all` is `not any(died)` over the callers — adding certain-green cells
> cannot change it. **If the tenth suite is non-reaching, grading it moves all eleven rows from
> `null` to `true` and changes no other number.** Eleven of eleven contracts survive every caller,
> and nothing in the caller population proves any contract of `fuel_mix`.

That is a completed verdict bought for ~1.9 h whose *value* is already determined; what the 1.9 h
buys is the **population**, not the answer. The three-valued verdict landed at `353d0e910` is right
to refuse to say "proved" — but it cannot distinguish an ungraded caller that *might* kill from one
that provably cannot, and here the difference is a hundred minutes.

## The prediction, filed before the answer exists

The in-flight poison returns `reaches_subject: false` for the tenth suite, and the derivation above
holds. **What refutes it:** `reaches_subject: true` — in which case the eleven cells are real
evidence, the 1.9 h *is* worth buying, and this document's central claim is wrong. I am not
recording the outcome; the lane that bought the round owns it.

## What is inference here and not record

The caller-kill count is re-derived from `95c9da4db380`, and that fingerprint belongs to **no
committed spec** — it was run from an uncommitted working-tree copy that cannot be reconstructed
(established by the other lane's pre-registration, not by me). Its mutation `old`/`new` text hashes
identically across the surrounding commits and the subject has not changed since `177de48c1`, so
the count is very probably right. It is not evidence anyone should stand on alone, and the
`d7eb36a0b901` run is what will replace it. The AST census is the part of this document that stands
on committed bytes.

## Disposition

Claim **not released**: the grading is not done and the decision depends on a round I do not own.
Next actor — read the poison cell in
`/var/tmp/grid_intensity_fuel_mix_battery_d7eb36a0b901.json`:

* `reaches_subject: false` → do **not** buy the ~1.9 h. Record eleven-of-eleven-survive-every-caller
  with the tenth suite's cells derived, and close `fuel_mix` as proved by nothing in its caller
  population.
* `reaches_subject: true` → buy it. The cells are evidence and the derivation above is refuted.
