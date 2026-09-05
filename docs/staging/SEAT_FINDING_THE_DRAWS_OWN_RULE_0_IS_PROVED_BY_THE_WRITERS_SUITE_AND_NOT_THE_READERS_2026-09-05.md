**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# FINDING: the draw's own Rule 0 is proved by the suite of the module that WRITES direction, not the one that READS it

**Graded 2026-09-05 against the predictions filed in
`SEAT_PREREG_WHICH_CALLER_SUITE_IS_EACH_DIRECTION_CONTRACT_STANDING_ON_2026-09-05.md`, which were
fixed before any of this was run. Claim id `direction-contract-battery-per-caller`. Harness:
`tools/direction_contract_battery.py`.**

**Status: ~~three of the four caller suites graded. The fourth (`tests/background/test_supervisor.py`,
~670s a pass, ~100 minutes for a baseline and eight mutations) is running and is NOT reported here.
The standing prediction therefore has NO VERDICT YET and is not claimed either way below.~~**
**Superseded 2026-09-06 00:20 BST by §10 — kept above rather than revised, because the whole point
of §5 and §9 is that they were written while this said what it says. ALL FOUR COLUMNS ARE NOW
GRADED. §5 is CONFIRMED, §9's poison round returned the exact pair that confirms it, and the
standing prediction is CONFIRMED by M2 and M7.**

---

## What was run

Eight one-line mutations of `background/direction.py`, each applied **alone**, each target asserted
present **exactly once** before patching, `__pycache__` cleared between runs, and each of the caller
suites run **separately** so the answer is a row per caller rather than one pass/fail.

**A baseline pass ran first and was green on all three:** `test_delivery_lane` 0 failed (1.6s),
`test_delivery_seat` 0 failed (1.6s), `test_the_self_audit...` 0 failed (3.4s). Every baseline red
would have been deselected from the mutation runs; there were none, so nothing was deselected. This
matters more than it looks — see §4.

## The result, three suites of four

`lane` = `test_delivery_lane.py`, `seat` = `test_delivery_seat.py`, `audit` =
`test_the_self_audit_declared_a_correction_and_nothing_carried_it.py`.

| # | contract | lane | seat | audit | the test that fired |
|---|---|---|---|---|---|
| M1 | `focus_multiplier` is ALWAYS >= 1.0 | — | **DIED** | — | `test_direction_can_NEVER_make_an_atom_harder_to_draw` |
| M2 | `focus_weights` untouched on length mismatch | — | — | — | *nothing* |
| M3 | forbidden keys refused at any depth | — | **DIED** | — | `test_a_record_carrying_a_TARGET_is_refused_whatever_it_is_called[benchmark]` |
| M4 | an empty `not_now` is refused | — | **DIED** | — | `test_a_direction_that_REJECTED_NOTHING_is_refused` |
| M5 | `wrong[i].corrected` must be a BOOLEAN | — | — | **DIED** | `test_an_error_with_NO_CORRECTION_STATE_is_refused[yes]` |
| M6 | `read_direction` NEVER RAISES | **DIED** | **DIED** | — | `test_a_MISSING_or_BROKEN_record_offers_nothing` / `test_a_BROKEN_direction_record_leaves_the_draw_byte_identical` |
| M7 | `is_live` is bounded BELOW as well as above | — | — | — | *nothing* |
| M8 | a legacy `wrong` row is `None`, not `False` | — | — | **DIED** | `test_the_recorded_audit_reads_in_BOTH_shapes_and_never_invents_a_verdict[stored2-expected2]` |

## Predictions, graded as written and not revised

| # | predicted | actual (3 suites) | verdict |
|---|---|---|---|
| M1 | dies in **supervisor** only | died in **seat** | **WRONG — right that it dies, wrong about who proves it** |
| M2 | survives all four | survived all three so far | pending supervisor |
| M3 | dies in seat only | died in seat only | **CORRECT** |
| M4 | dies in seat only | died in seat only | **CORRECT** |
| M5 | dies in audit only | died in audit only | **CORRECT** |
| M6 | **survives all four** | died in **lane AND seat** | **WRONG** |
| M7 | survives all four | survived all three so far | pending supervisor |
| M8 | dies in audit only | died in audit only | **CORRECT** |

Four correct, two wrong, two undecided. The two wrong ones are the interesting ones and they are
wrong in opposite directions: M1 said a contract was proved by its consumer and it is not, M6 said a
fail-soft breadth contract would be proved by nobody and it is proved twice over.

## 1. The finding: the draw's Rule 0 is proved by the writer, not the reader

`focus_multiplier` is the module's **only contract annotated in the source as
`MUTATION (must fire):`** — the module asserts in writing that returning below 1.0 for a non-focus
atom is covered. It is. But the covering test lives in `tests/background/test_delivery_seat.py`.

That is the wrong side of the seam, and the module's own docstring says why:

> `background/supervisor.py` imports THIS; it never imports `background/delivery_seat.py`. So the
> draw can read direction and has no path to the thing that writes it.

The split is deliberate and structural. `focus_multiplier` has **no external caller at all** — it is
reached only through `focus_weights`, and `focus_weights` is called from exactly four places, **all
of them in `background/supervisor.py`** (lines 1396, 1809, 1902, 2029). So the property that IS
Rule 0 here — *a direction record cannot empty the feasible set; the worst a wrong direction can do
is make the machine slower to reach something, never unable to* — is exercised only by the draw, and
proved only by the suite of the module the draw cannot see.

Delete or refactor `delivery_seat.py` and its suite goes with it. The draw keeps calling
`focus_weights`. Nothing anywhere would then be able to fail when direction starts filtering the
candidate list, and `test_supervisor.py` — the suite of the *only* caller — would stay green
throughout. **The prediction that M1 dies in `test_supervisor.py` was not a careless guess; it was
what the architecture implies. The architecture does not hold.**

This is the low-water shape from `38871422b` reproduced at a second subject, with a sharper edge:
there the contract was proved by *one* caller suite, here it is proved by a caller suite that
**structurally cannot reach the code path the contract governs**. It proves it by direct unit test of
`direction`, which is a fine test and an accident of where someone chose to file it.

## 2. `test_delivery_lane.py` proves nothing the others do not

It fires on exactly one mutation, M6, and `test_delivery_seat.py` kills M6 as well. On the three
suites measured, **removing `test_delivery_lane.py` entirely would leave no direction contract
without a proof.** That is not an argument for removing it — it tests `unreachable_focus` routing,
which no mutation here targets — but it does mean this caller contributes no unique coverage of the
eight contracts the module states in prose.

Coverage is concentrated: `seat` kills 4 of 8, `audit` kills 2 of 8 (exactly the two it is named
for, which is the file doing its job), `lane` kills 0 uniquely.

## 3. M6 was wrong in the useful direction

The prediction was that `read_direction`'s breadth — that a missing file, a permission error and a
YAML syntax error are one answer — would be the classic unproved fail-soft contract. It is proved
twice, by two different callers, and both tests are named for the property rather than for today's
answer (`..._leaves_the_draw_byte_identical`). Narrowing `except Exception` to
`except FileNotFoundError` fails immediately in both. Recorded because a prediction that a control is
missing, refuted by finding two good ones, is evidence the pessimism is not uniform.

## 4. A methodological finding, and it invalidates a prior run

A partial battery over this same subject was run on an earlier turn and its results are at
`/var/tmp/direction_battery_PRIOR.json` (M1–M7, supervisor column included). **Its rows agree with
this run's on every cell they share** — but the run itself could not have known that, because it
recorded neither a baseline nor the failing test **ids** (`failed: null` in every row). Without a
baseline, a `returncode == 1` is equally consistent with the mutation dying and with a red already
present at HEAD; without the ids, "which control proves this contract" — the entire question — is
unanswerable, and §1 above could not have been written from it.

That the two runs agree is luck, not method. The rule this earns: **a mutation battery that records
only a return code has measured that something failed, not what.**

## 5. WHY the consumer's suite proves nothing — measured, and it is by construction

Added after the three columns above landed, while the supervisor column is still running. This is
the mechanism, and it was found by reading the suite rather than waiting for it.

`tests/background/test_supervisor.py` imports `direction` for exactly one purpose. There is no test
of any direction contract in its 200 tests. Line 150, inside the shared fixture that isolates every
state path a cycle touches:

    monkeypatch.setattr(direction_module, "DIRECTION_PATH", tmp_path / "DIRECTION.yaml")

Nothing ever writes that file — line 150 is the only occurrence of `DIRECTION_PATH` in the suite and
`DIRECTION.yaml` appears elsewhere only in a comment. So **every test in the suite runs with the
direction record absent**, and that is deliberate and correct for what those tests describe: without
it, every "nothing is open" test reads the live record and correctly finds work in it.

Putting the suite's own condition to the module directly:

    DIRECTION_PATH -> a path that does not exist
    read_direction ->  None
    current_focus  ->  ()
    focus_weights([{id: atom-a}, {id: atom-b}], [1.0, 1.0]) -> [1.0, 1.0]   (unchanged)
    focus_multiplier invocations -> 0

`focus_weights` short-circuits at `if not focus` and **`focus_multiplier` is never called at all**.
So the mutated line in M1 — the one the module annotates `MUTATION (must fire):` — is not merely
unproved by the consumer's suite, it is **unreachable from it**. The same short-circuit is upstream
of every other mutation in the battery.

This is the sharper form of §1, and it is not an accusation of carelessness: the fixture is right,
and its comment says where it expects the proof to live instead — *"The lane itself is proven both
ways in test_delivery_lane.py."* §2 measured that suite. It kills one mutation of eight, and
`test_delivery_seat.py` kills the same one. **The deferral points at the suite with no unique
coverage.**

The shape, stated generally: *a caller's suite that isolates a dependency — correctly, so its own
subject is what is under test — can never fail when that dependency's contract breaks. Convergence
then leaves the contract proved by whichever OTHER caller happened to test it directly, and that
caller may be one the consumer is forbidden by design to see.*

**PRE-REGISTERED, before the supervisor column finishes** (it is ~100 minutes and in flight; this
prediction is filed now precisely so it cannot be written after the answer):

> All eight mutations SURVIVE `tests/background/test_supervisor.py`, and the killed-by sets in the
> table above are already final. Not because the suite is weak, but because the short-circuit above
> makes every mutated line unreachable under its fixture. If any mutation dies there, this section
> is wrong and the reachability argument with it.

If that holds, the standing prediction — *at least 1 of the 8 survives all four suites* — is
CONFIRMED at this subject by M2 and M7, and the LATENT general statement from `38871422b`
generalises to a second converged module.

## 6. The repair, and it is mutation-proven

`tests/background/test_direction_contracts.py` — 39 tests, 0.15s, the module's own suite. Written
against the properties rather than today's callers, so a contract's proof stops being an accident of
which caller someone happened to be working in.

Run through the same battery as a fifth column (`--suites test_direction_contracts`), baseline green:

| # | contract | four caller suites | own suite |
|---|---|---|---|
| M1 | `focus_multiplier` ALWAYS >= 1.0 | seat only | **DIED** `test_direction_can_only_ADD_attention_across_the_WHOLE_partition` |
| M2 | untouched on length mismatch | **nothing** | **DIED** `test_a_MISMATCHED_candidate_list_leaves_the_weights_BYTE_IDENTICAL` |
| M3 | forbidden keys at any depth | seat only | **DIED** `test_a_TARGET_SHAPED_key_is_refused_AT_ANY_DEPTH[target-inside a list of dicts]` |
| M4 | empty `not_now` refused | seat only | **DIED** `test_a_direction_that_REJECTED_NOTHING_is_refused` |
| M5 | `corrected` must be a BOOLEAN | audit only | **DIED** `test_a_recorded_ERROR_needs_a_BOOLEAN_correction_state[yes]` |
| M6 | `read_direction` NEVER RAISES | lane + seat | **DIED** `test_read_direction_NEVER_RAISES_whatever_is_wrong_with_the_file` |
| M7 | `is_live` bounded BELOW | **nothing** | **DIED** `test_a_FUTURE_DATED_record_does_not_steer_any_more_than_a_STALE_one[-0.5]` |
| M8 | legacy row is `None`, not `False` | audit only | **DIED** `test_an_UNRECORDED_correction_state_is_None_and_never_False[stored2]` |

**Eight of eight, each killed by the test named for that defect.** The two contracts that were
proved by nothing are now proved: a mismatched candidate list leaves the weights byte-identical, and
a future-dated record does not steer. The second is the one worth naming — without the lower bound a
record stamped in the future can *never* age out, because its age only grows toward zero, so a clock
skew or a bad stamp pins the draw to one orientation permanently.

Three things in that file are there to stop it becoming a control that cannot fail:

* **A vacuity guard.** Every test breaks one field of a shared valid record and asserts a refusal.
  If that record were itself invalid they would all pass for the wrong reason, so
  `test_the_fixture_record_is_actually_VALID_or_every_test_below_passes_vacuously` asserts it
  validates first.
* **The partition, not a leg per branch.** `focus_multiplier` is asserted `>= 1.0` over named,
  unnamed and empty ids *and* that every rank is reachable and distinct — because a function that
  ignored focus and always returned 1.0 would satisfy the bound on its own.
* **The inverse of the target guard.** A guard that refused everything would pass every
  forbidden-key test, so a `why` quoting a measurement (`"the belief error is +0.5pp"`) is asserted
  to be accepted.

The repair column is deliberately **not** a member of the battery's `SUITES` tuple.
`survived_all` answers the pre-registered question *"did any caller prove this"*, and folding the
repair into that population would make the question unanswerable the moment the repair landed.

## 7. What is still open

* The `test_supervisor.py` column, all eight mutations, in flight in an isolated worktree
  (`/var/tmp/se-battery-supervisor`, results to `/var/tmp/direction_battery_sup.json`) so that an
  in-flight mutation cannot dirty the shared tree and refuse a landing.
* **The standing prediction — "at least 1 of the 8 survives all four suites" — is UNGRADED.** M2 and
  M7 are the only candidates and both need the fourth column. Neither is called a survivor here.
* **The survivors are a reachable gap, not an equivalence, and §5 is what makes that certain.** The
  unreachability is in the *fixture*, not in the code: `focus_weights` is called on every real draw
  (`supervisor.py` lines 1396, 1809, 1902, 2029) against the live `docs/direction/DIRECTION.yaml`,
  so every mutated line is reachable in production and unreachable only under test. That is the
  opposite of dead code, and it is why the repair is a test rather than a deletion.
* **The repair is done and is §6.** It was written against the three measured columns plus the
  reachability measurement in §5, not against the pending fourth — which is sound because §5 shows
  the fourth column *cannot* kill anything, and because a suite keyed to the module's properties
  does not depend on which caller proves what. If the supervisor column refutes §5, the repair is
  still correct; only the account of why the gap existed would change.
* **Not done: nothing yet stops this recurring.** The eight contracts are now proved beside the
  module, but the next contract added to `direction.py` can be proved by a borrowed suite exactly as
  these were, and nothing would notice. Whether that is worth a control is a real question and the
  honest answer is probably not — a control that watches which file a test lives in is close to the
  register-that-guards-a-register shape this project keeps paying for. Recorded as a judgement, not
  deferred as a task.

## 8. How the fourth column was actually run, written BEFORE its results

The three cheap suites cost 1.3–3.5s a pass. `tests/background/test_supervisor.py` costs **661s**, so
eight mutations plus a baseline is ~99 minutes serially and two consecutive turns have now ended
mid-column: the first died after the baseline, during M1. The column is not hard, it is just longer
than a turn.

So it is **sharded across four locked worktrees** at the same commit (`cfd4a5d4c`), two mutations
each, run concurrently on a 16-core host. Wall clock becomes ~3 passes rather than ~9.

**This changes the method, and a changed method needs its own control, stated here before any of it
came back.** Three things guard it:

* **Both files are byte-identical across all four shards and this tree**, asserted by `md5sum` on
  `background/direction.py` and `tests/background/test_supervisor.py` before launch, so the four
  shards are measuring one subject and not four.
* **Each shard runs its own baseline under the same 4-way concurrency it will mutate under.** The
  serial baseline already recorded at `/var/tmp/direction_battery_sup.json` (green, 0 failed, 661.1s)
  is deliberately NOT reused. Reusing it would import a serial result into a concurrent run and make
  every concurrency-induced red read as a mutation dying — the §4 defect wearing a different hat. If
  a shard's own baseline is red, those ids are deselected from that shard's mutation runs by the
  harness, and the reds are reported here.
* **A DIED in this column is the surprising outcome and is not accepted on a return code.** §5
  predicts all eight survive. Any kill is therefore re-run alone — the named failing test, serially,
  unmutated and then mutated — before it is written down, because under concurrency a false kill and
  a real one look identical from the exit status.

The asymmetry is deliberate and stated so it cannot be quietly applied: a SURVIVOR here needs no
re-run, because concurrency can only add failures, never remove them. Under concurrency a survivor is
the *conservative* reading and a kill is the *fragile* one, so only kills are re-verified.

**That asymmetry has one hole and §9 is why it matters.** Concurrency can only add failures *within a
tree*. It cannot add a mutation that was never applied — and if two shards share a `BATTERY_TREE`,
one shard's `restore()` deletes the other's mutation and the unmutated run reports `200 passed`.
That manufactures a SURVIVOR, which is the reading this method treats as conservative. So the
provenance that has to be recorded for the fourth column is not the concurrency, it is the
**one-tree-per-shard mapping**, asserted by `md5sum` before launch.

## 9. PRE-REGISTERED POISON ROUND — written 2026-09-05 22:43 BST, before P1 and P2 returned

The fourth column never landed. §8's four shards were killed mid-baseline (their logs stop at
`BASELINE (no mutation, full pass, ...)`, 22:07) and `/var/tmp/direction_battery_sup.json` carries no
`test_supervisor.py` row for any of the eight. Three consecutive turns have now ended inside that
column. **This section is what makes the column's answer decidable without it**, and it is a
different measurement rather than a fourth attempt at the same one.

**Why a poison round at all.** "Survived" means the same thing for an unreachable room and an
unproved contract. §5 argues from reading the fixture that the supervisor suite's rooms are
unreachable, and probes the module directly under the fixture's condition — but it never ran the
suite against a mutation that the suite *must* catch if it reaches the subject at all. Without that,
eight survivals in a column are consistent with a suite that never imports the module, a suite that
imports it and never calls it, and a suite that calls it and is short-circuited. Those are three
different findings and only the third is §5's.

Three poisons, each far louder than any of the eight, each applied by the same harness with the same
exactly-once assertion, each in a worktree of its own:

| id | poison | what a kill proves |
|---|---|---|
| P0 | the module raises on import | the suite IMPORTS it |
| P1 | `focus_weights` returns all zeros, unconditionally, above every branch | the suite REACHES the seam |
| P2 | `current_focus` always returns `()` | the suite exercises something BELOW `read_direction` |

**P0 has returned and it died in all four suites** (`RuntimeError: POISON: direction imported`,
collection error, 0.9s). Every caller suite imports the module, so no survival anywhere in this
battery is the trivial kind.

**Predictions for P1 and P2, fixed here before either returned:**

| | supervisor | lane | seat | audit |
|---|---|---|---|---|
| P1 | **DIES** — `supervisor.py` calls `focus_weights` at four draw sites and `random.choices` raises on an all-zero weight list, so any test that runs a draw with candidates must fail | survives — no call site | **DIES** — asserts returned weights directly | survives |
| P2 | **SURVIVES** — under the suite's own fixture `current_focus` already returns `()` for all 200 tests, so the poison is a no-op there | DIES | **DIES** — `test_a_named_atom_actually_becomes_more_likely_and_the_steer_BITES` | survives |

**P1 DIES and P2 SURVIVES in `test_supervisor.py` is the outcome that confirms §5**, and it is the
only pair that does: it says the suite reaches the seam and nothing below `current_focus`, which is
exactly what "the fixture short-circuits it" means, measured rather than reasoned. Then all eight
mutated lines are unreachable from that suite by construction and the fourth column cannot kill
anything — a conclusion the column itself, run to completion, could never have distinguished from a
weak suite.

**P1 SURVIVING would be a stronger result and a different one**: the suite would never reach
`focus_weights` at all, and §1's architectural claim would need restating.
**P2 DYING refutes §5** and the reachability account with it.

The eight-mutation fourth column is running anyway, in five worktrees asserted byte-identical on both
subject and suite before launch (`0815090171e6…` / `963cdf0691d6…`), one mutation per tree per run
and a sixth tree carrying its own baseline, precisely so the survivor-manufacturing hole named above
is closed by provenance rather than by hope. Its results are §10.

---

## 10. GRADED — the poison round and the fourth column, both returned

Run 2026-09-05 23:47–00:12 BST, ten shards concurrently, **one tree per shard**, harness
`/var/tmp/sup_column_runner.py`. Nothing below was written before the results were in hand and
nothing above was edited to fit them.

### The poison round, against §9's table

| id | poison | predicted in `test_supervisor.py` | **actual** | verdict |
|---|---|---|---|---|
| P0 | module raises on import | dies (all four suites) | **DIED**, all four | **CORRECT** |
| P1 | `focus_weights` returns all zeros above every branch | **DIES** | **DIED**, 25.2s | **CORRECT** |
| P2 | `current_focus` always returns `()` | **SURVIVES** | **SURVIVED**, 200 passed | **CORRECT** |

P1 died on `test_maturity_map_draw_finds_atom_with_real_gap`, and it died by the exact mechanism
§9 named before the run — not merely at the predicted place:

    total = cum_weights[-1] + 0.0
    if total <= 0.0:
        raise ValueError('Total of weights must be greater than zero')
    /usr/lib/python3.14/random.py:489: ValueError

**P1 DIES and P2 SURVIVES is the pair §9 said would confirm §5, and it is the only pair that
would.** The suite reaches `focus_weights` with a real candidate list, and it exercises nothing
below `current_focus`. That is what "the fixture short-circuits it" means, measured rather than
reasoned.

### The fourth column, against §5's pre-registration

| # | contract | supervisor | lane | seat | audit | survived ALL FOUR |
|---|---|---|---|---|---|---|
| M1 | `focus_multiplier` ALWAYS >= 1.0 | survived | — | **DIED** | — | no |
| M2 | untouched on length mismatch | survived | — | — | — | **YES** |
| M3 | forbidden keys at any depth | survived | — | **DIED** | — | no |
| M4 | empty `not_now` refused | survived | — | **DIED** | — | no |
| M5 | `corrected` must be a BOOLEAN | survived | — | — | **DIED** | no |
| M6 | `read_direction` NEVER RAISES | survived | **DIED** | **DIED** | — | no |
| M7 | `is_live` bounded BELOW | survived | — | — | — | **YES** |
| M8 | legacy row is `None`, not `False` | survived | — | — | **DIED** | no |

**All eight survived. §5 predicted all eight would survive, and gave the reason before the answer
was known. §5 is CONFIRMED, and the reachability argument stands.** Every one of the eight was a
full `200 passed` run (847–855s each under ten-way concurrency, against 661s serial — a 1.29×
contention factor, not a truncation).

**The standing prediction — *at least 1 of the 8 survives all four suites* — is CONFIRMED**, by M2
and M7. Both are now proved by the repair suite in §6 and by nothing else in the tree.

### Grading §5's own claim, which is sharper than "all eight survived"

§5 did not predict weakness; it predicted **unreachability**, and those are different findings that
a column of survivals cannot tell apart. The poison round is what separates them, and it is why
this section can say something the completed column alone never could:

* P0 died → the suite **imports** the module. No survival here is the trivial kind.
* P1 died → the suite **reaches** `focus_weights` on a real draw.
* P2 survived → the suite exercises **nothing below `current_focus`**, because under its fixture
  `current_focus` already returns `()` for all 200 tests, so replacing its body with `return ()` is
  a no-op there.

Together: the suite calls the seam, the seam short-circuits at `if not focus`, and every one of the
eight mutated lines sits below that short-circuit. **The eight lines are unreachable from
`test_supervisor.py` by construction — not untested, unreachable.** That is an equivalence *under
this fixture* and a reachable gap *in production*, and §7 already records why: `focus_weights` is
called at four live draw sites against the real `docs/direction/DIRECTION.yaml`.

So the §1 finding survives its own strongest test. The only caller of `focus_weights` cannot fail
when `focus_weights` breaks, and the contract the module annotates `MUTATION (must fire):` was
proved — before §6 — by a suite that caller is forbidden by design to see.

### Provenance, because §8's asymmetry has exactly one hole and this is how it was closed

§8 accepts a SURVIVOR without re-running it, on the ground that concurrency can only add failures.
The hole it named: concurrency cannot add a mutation that was **never applied**, and a shard whose
mutation was wiped reports `200 passed` — a manufactured survivor, wearing the conservative
reading's clothes. Four guards, all machine-recorded in `/var/tmp/sup_column_results.json`:

* **One tree per shard, ten trees, no sharing.** Asserted by the runner (`len(set(TREES)) == 10`)
  rather than by the launch procedure, so no `restore()` can reach another shard's subject.
* **The subject and suite are the ones §8 named.** Every shard checks its pristine subject against
  `0815090171e6…` and its suite against `963cdf0691d6…` before patching. *This guard fired on the
  first launch* — the pin had been written out to a full digest that was never measured, and the
  run refused to start. That is the guard doing its job on its first application.
* **The mutation is asserted present AFTER patching and AGAIN after the run.** All ten patched
  digests are distinct, none equals pristine, and all ten are byte-identical before and after their
  pass (`mutation_held_throughout: true`, ten of ten). A wiped mutation cannot be recorded as a
  survivor.
* **The one kill was re-run serially and alone.** `test_maturity_map_draw_finds_atom_with_real_gap`
  in a quiet tree: **1 passed in 0.94s** unmutated, **1 failed in 1.20s** with P1 applied, same
  test, same `ValueError`. P1's death is not a concurrency artefact.

**One departure from §8, stated rather than applied quietly.** §8 required each shard to run its own
baseline under the same concurrency. This run has **no per-shard baseline** and buys the same
protection differently: because concurrency only adds failures, a baseline is needed only to stop a
concurrency-induced red being read as a kill — and re-running *every* kill serially (there was one,
and it was re-run) rules that out directly, at 2 seconds instead of ten more 850s passes. The serial
baseline recorded earlier (green, 0 failed, 661.1s) is used here **only** as evidence the suite is
green unmutated at this subject, never to discount a red. If a future run of this shape declines to
re-verify a kill, the baselines go back in.

### What this closes and what it does not

Closed: the fourth column, the §5 pre-registration, the §9 poison round, and the standing prediction
from `38871422b`. Four turns ended inside this column; what finished it was not a fourth attempt at
the same 100-minute measurement but the poison round, which answered the same question in 25 seconds
by asking whether the room was reachable instead of whether the contract was proved.

**The rule that earns:** *when a mutation battery's pre-registration predicts survival, run the
poison round FIRST. "Survived" means the same thing for an unreachable room and an unproved
contract, and the poison separates them in seconds where the column cannot separate them at all.*
Registered against `docs/design/CONTROLS_THAT_CANNOT_FAIL.md`'s reachability shape.

Not closed, and unchanged from §7: nothing stops the next contract added to `direction.py` being
proved by a borrowed suite. §7 records the judgement that a control watching which file a test lives
in is not worth having, and this section does not revisit it.
