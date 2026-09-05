**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# FINDING: the draw's own Rule 0 is proved by the suite of the module that WRITES direction, not the one that READS it

**Graded 2026-09-05 against the predictions filed in
`SEAT_PREREG_WHICH_CALLER_SUITE_IS_EACH_DIRECTION_CONTRACT_STANDING_ON_2026-09-05.md`, which were
fixed before any of this was run. Claim id `direction-contract-battery-per-caller`. Harness:
`tools/direction_contract_battery.py`.**

**Status: three of the four caller suites graded. The fourth (`tests/background/test_supervisor.py`,
~670s a pass, ~100 minutes for a baseline and eight mutations) is running and is NOT reported here.
The standing prediction therefore has NO VERDICT YET and is not claimed either way below.**

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
