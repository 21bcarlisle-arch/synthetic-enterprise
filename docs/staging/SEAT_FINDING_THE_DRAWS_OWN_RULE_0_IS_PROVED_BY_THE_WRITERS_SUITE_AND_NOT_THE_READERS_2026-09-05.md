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

## 5. What is still open

* The `test_supervisor.py` column, all eight mutations, in flight in an isolated worktree
  (`/var/tmp/se-battery-supervisor`, results to `/var/tmp/direction_battery_sup.json`) so that an
  in-flight mutation cannot dirty the shared tree and refuse a landing.
* **The standing prediction — "at least 1 of the 8 survives all four suites" — is UNGRADED.** M2 and
  M7 are the only candidates and both need the fourth column. Neither is called a survivor here.
* No repair is proposed yet. §1 names a reachable gap rather than an equivalence — `focus_weights`
  is live on every draw — but the repair belongs on the shared module where the contract lives, and
  choosing it before the fourth column lands would be choosing it without the evidence.
