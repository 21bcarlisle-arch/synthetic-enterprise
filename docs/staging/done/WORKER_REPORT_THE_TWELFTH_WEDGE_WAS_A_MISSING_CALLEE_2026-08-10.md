# [WORKER-REPORT] The twelfth wedge: the H41 caller landed, its callee did not

**Closed:** 2026-08-10, worker tick. **Cause commit:** the H41 caller was committed without
`tools/simplifications_store.py`. **Fix:** `4fccacf39`. **Mint of the same tick:** `1c6e87ff9`.
**Episode length:** 110 consecutive gate failures, ~19.5h of frozen publishing.

## The cause, observed-with-evidence (R9)

At HEAD `9b6dcfcea`, `background/supervisor.py` is fully committed and clean:

```
line 133:  from tools import simplifications_store as _atom_store  # noqa: E402 (H41 record tenant)
line 1057: return _atom_store.records_for_atom(str(aid)).get("evidence")
```

The committed `tools/simplifications_store.py` defines no `records_for_atom`. The H41
record-tenant half was complete in the working tree and absent from every commit. `observed`:
`git show 9b6dcfcea:tools/simplifications_store.py | grep "^def "` lists 13 functions, none of
them `records_for_atom`; the working tree lists 18, including it.

This is the **same class** as `ebc2356c8` ("commit the callee I committed the caller of") and
`7cef2c1d4` / `b2e3284f1`. It is now the fourth instance.

## Why it took 110 cycles to name — the part worth keeping

`_is_drained_and_gated()` ends:

```python
    except Exception:
        return False
```

documented as FAIL-SAFE TOWARD WORK. So the `AttributeError` never surfaced as an import
error or a stack trace. It surfaced as **the rest predicate quietly answering False**, and the
gate reported:

```
FAILED tests/background/test_forward_discovery_draw.py::test_may_rest_with_genuinely_empty_authorized_set
```

— a test about *resting*, whose subject has nothing whatever to do with the atom store. Every
prior tick read the reported node id as the subject and went looking at the draw ladder. The
alarm was not lying; it was faithfully reporting the symptom of a swallowed exception.

**The general shape:** a broad `except Exception` that returns a *fail-safe value* converts
"this module is broken" into "this predicate is False". Any test asserting the predicate's
other branch then fails, and it names itself, not the break. A fail-safe default is still
correct policy here — but it should be *loud*: the handler should log what it swallowed.

`inferred`, not observed: had the handler logged the exception, this would have been a
one-cycle diagnosis.

## It was a stack, not a bug (third time this pattern recurs)

Three independent reds sat at HEAD. Fixing only the first would have produced yet another
"successor red" tick, which is exactly what `9b6dcfcea`'s own commit message records happening
the cycle before.

| # | red | verdict |
|---|---|---|
| 1 | missing `records_for_atom` callee | the wedge proper |
| 2 | `test_counts_match_file_contents` — `H_GAP_fabric_belief_truth_gap` map count 21 vs store 22 | pre-existing; store is right, the derived scalar had lagged; corrected to 22 |
| 3 | `test_predictions_ledger_can_fail` (2) — `site/data/proof.json` stale | pre-existing; site-lane only, surfaced by the evidence.json coupling |

## Two traps this tick hit, both worth filing

**(a) A projection regenerated against the WORKING TREE reds on the tree the commit would create.**
`proof.json`'s rendered age derives from two committed inputs — `site/state/live_portfolio.json`
(the stamp) and `site/state/track_record_scorecard.json` (the sim's today) — and the sim runner
rewrites both every few minutes. Regenerating locally produced a projection that passed in the
working tree and red-ed under `surgical_land` **twice**, with the age reading `-1 day(s)` and
then `20 day(s)`. The fix is to regenerate against the **committed** inputs, so the projection
is coherent with the sources actually shipped. `surgical_land`'s own refusal message states this
exactly — "a working tree that passes here means the unstaged half is what makes it pass" — and
it was right both times.

**(b) The pre-commit gate maps no test to a `maturity_map.yaml` change.** The mint at `1c6e87ff9`
passed its gate (17 targeted files) while introducing a red in
`tests/design/test_atom_notes_store.py` and `tests/design/test_atom_records_store.py`, because
neither is in `LEVEL_SENSITIVE_TESTS` for a map edit. This is the already-filed
`WORKER_FINDING_THE_PRE_COMMIT_GATE_MAPS_NO_TESTS_TO_A_DATA_FILE_2026-08-09` — this is its
second instance, and the first where the red was self-inflicted by a mint. Both reds were
cleared in `4fccacf39`.

## Disposition of the eight "suspects" the alarm cited

**0 of 8 named the cause. Again.** That is now five consecutive episodes at 0/8
(see `WORKER_REPORT_{PUBLISH,FIFTH,SIXTH}_WEDGE_SUSPECT_DISPOSITION_*`). The cited list is the
eight most recently modified `WORKER_FINDING_*.md` in staging, ranked by mtime and linked to the
failure by nothing at all — the list is near-identical every episode while the cause differs
every episode, which is the tell.

**The repair for this already exists, uncommitted, in `background/process_run_complete.py`**
(`GATE_BLOCKING_TESTS_FILE`, `_write_blocking_tests`, `_clear_blocking_tests`,
`last_blocking_tests`, `_blocking_clause`) with its test file
`tests/background/test_publish_gate_blocking_payload.py` untracked. It writes the red gate's
actual node IDs where the alarm process can read them, and makes the alarm say
"BLOCKING TEST: UNRECORDED" rather than guess. **It is not landed in this commit** — it is a
separate workstream from the wedge, and landing an unverified second change while unwedging is
how episode 2 cost seven hours. It should be the next draw: an alarm that has mis-pointed five
times running is itself a P0 defect, and the fix is already written.

## What actually closes the class

Not "commit the callee" — that is the instance. The class fix is a control that fails when
**HEAD references a name HEAD does not define**. `H40_full_suite_pollution_bisect` and the
no-caller census are adjacent but neither catches this. A cheap first cut: import every
first-party module in a clean HEAD checkout and assert the referenced attributes resolve.

## Verification

- `4fccacf39` landed through `tools.surgical_land` (the gate ran against the tree the commit
  would create, not the working tree). No `--no-verify`; the wall held.
- Pushed; `origin/main` contains `4fccacf39`.
- Publish gate re-run against a clean checkout of `4fccacf39` — result recorded in the tick's
  NTFY and `docs/status/LATEST.md`.
