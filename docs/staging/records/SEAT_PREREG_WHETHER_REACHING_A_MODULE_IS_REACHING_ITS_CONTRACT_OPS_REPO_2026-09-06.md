**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# PRE-REGISTRATION: is reaching a module the same as reaching its contract? (`background/ops_repo.py`)

**Written 2026-09-06 by the delivery seat BEFORE any mutation ran, in the shared tree at
`fa80a1361`. Claim id `converged-battery-next-subject`. The predictions below are kept unrevised
beside the result whatever they score — a prediction filed after the answer is not a prediction.**

---

## Why this subject, and the premise that has already half-expired

Subject 6 of the convergence sweep. `background/ops_repo.py` was named by the screen as one of
three converged modules with **no test importer whatsoever**, and the drawn direction says that is
where the shape should be strongest.

**That premise is spent and it is being recorded as spent, not quietly reused.** On 2026-09-05 the
seat found that defect and *repaired* it: `tests/background/test_the_ops_repo_push_had_no_refusal_
at_the_choke_point.py` now imports the module and drives its body, and the refusal it was missing
now exists at the choke point. So the question this battery can still answer is not "does anything
prove these contracts" — something now does, by construction. It is the **pre-registered** one:

> Of the three first-party callers that converged onto `commit_and_push`, **which of their suites
> proves anything about the shared body at all** — and does the poison round's answer ("this suite
> can go red for this subject") mean what four turns of this sweep have been reading it to mean?

That second clause is why this subject is worth the run rather than skipping to
`generate_company_data.py`. `direction.py`'s fourth column was eight green cells in a suite that
**never imported the subject through a live path** — the poison round caught it because the floor
and the failure were the same mechanism. `ops_repo` is the opposite shape and the sweep has not met
it yet: all three callers do `from background.ops_repo import commit_and_push` **at module level**,
so every caller suite will redden under an import-time poison — and then every one of them patches
`commit_and_push` *by name in the caller's namespace*, so the shared body is executed by none of
them. If that is what happens, **the reachability floor is necessary and not sufficient**, and
every "reaches the subject" this sweep has printed means only *imports it*.

## The rooms

| suite | relationship to the subject | column |
|---|---|---|
| `tests/background/test_ntfy_mirror.py` | caller suite; `patch("background.ntfy_mirror.commit_and_push")` | caller |
| `tests/background/test_director_input_log.py` | caller suite; `patch("background.director_input_log.commit_and_push")` | caller |
| `tests/background/test_backup_company_data.py` | caller suite; patches the name in all four tests | caller |
| `tests/background/test_the_ops_repo_push_had_no_refusal_at_the_choke_point.py` | the 2026-09-05 repair; the only real importer | **repair, scored separately** |

The repair suite is deliberately **not** a member of `SUITES`. `survived_all` answers "did any
*caller* prove this", and folding the repair into that population would make the pre-registered
question unanswerable the moment the repair landed.

## The eight contracts, as the module states them in prose

| id | the contract | the one-line edit |
|---|---|---|
| M1 | the refusal **raises**; a silent no-op is the strictly weaker shape two callers hand-rolled | `return` before the raise |
| M2 | the refusal is the **first statement**, before the `git add` | move `git add` above the guard |
| M3 | the refusal **names** the repo it protected | drop `{OPS_REPO_DIR}` from the message |
| M4 | "nothing to commit" is a **clean no-op**, not an exception | `return` → `pass` |
| M5 | a commit failure that is **not** emptiness is never swallowed by that branch | match on `True` |
| M6 | the ops lock is **exclusive** | `LOCK_EX` → `LOCK_SH` |
| M7 | the timeout **names the lock file** it could not take | drop `{_LOCK_FILE}` from the message |
| M8 | the guard **calls** `live_ledger_guard.in_test_process()`, not the callers' weaker `PYTEST_CURRENT_TEST` spelling | inline the weaker copy |

**Every mutation here is fail-CLOSED by construction and that is a design constraint, not an
accident.** The obvious M1 — delete the guard — would leave a test process with nothing between it
and `git push origin main` on the *real* private ops repo, which is a real-world write. So M1 keeps
the guard and makes it silent; M8 keeps a guard that still fires inside any test *body* and fails
open only at collection, where nothing pushes. No mutation in this table can reach `origin`.

## The six predictions

* **P1 — all three caller suites REACH the subject.** The import-time poison reds every one of
  them, because each caller imports the subject at module scope. Confidence: high.
* **P2 — and all eight mutations survive all three caller suites anyway.** `survived_all` = 8/8.
  Every caller suite patches the shared function by name; not one of them executes its body.
  Confidence: high. **P1 and P2 together are the finding** — if both land, "reaches the subject" and
  "reaches the contract" are different questions and the sweep has only been asking the first.
* **P3 — the repair suite kills all eight.** It was written against these contracts. A survivor
  here is a hole in a repair that is four days old. Confidence: high; this is the one that can
  embarrass the repair.
* **P4 — M4 and M5 both die only in the repair column.** They are the two sides of one branch and
  the caller suites never see either.
* **P5 — no mutation is an equivalence.** Every `old` is asserted present exactly once and every
  contract above is stated in the module's own prose, so a survivor in the repair column is a
  missing test, not an equivalence. Filed so it can be refuted.
* **P6 — the poison round takes under ten seconds for the whole subject.** All four suites run in
  ~1s at HEAD. If this is right, the cost argument for skipping the floor is dead for every cheap
  subject, and the floor should be unconditional.

## What done means (this is direction, not an atom — no exit test is written for it)

The spec lands in `tools/direction_contract_battery.py` as a third `SubjectSpec`, the battery runs
poison-first, and the result document states which column proved what — with the P1/P2 pair
answered explicitly, because that is the transferable part and the per-contract table is not.
