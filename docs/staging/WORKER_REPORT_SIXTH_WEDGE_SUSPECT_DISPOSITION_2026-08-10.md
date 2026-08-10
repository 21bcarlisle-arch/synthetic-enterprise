# [WORKER-REPORT] Sixth publish wedge: the cause, and the disposition of the eight cited suspects (2026-08-10)

**Wedge:** 76 consecutive gate failures, ~751 min red, no pass at HEAD since `2de572e72`.
**Closed at:** `de59adffa` (pushed; origin/main verified).

## The cause, in one line

`background/suite_duration_watch.py` — added by PW3 (`82007ad44`, 01:26Z) as a new `background/*.py`
module with a `__main__` block and **no seat guard** — red the structural lock
`tests/background/test_seat_guard_daemons.py::TestStructuralLock::test_every_main_entrypoint_is_guarded`.

Fixed by adding the five-line guard in the shape its 44 siblings already use
(`deadmans_switch.py:751`, `supervisor.py:4415`). Evidence: `tests/background/test_seat_guard_daemons.py`
= **23 passed**. Population re-derived against HEAD content: **0 remaining offenders**.

## The eight cited suspects: none was the cause. Again.

This is the **third consecutive episode** in which the rung-1 alarm's `cited_findings` list contained
zero causes, and the finding that names the mechanism was **not** on it. The two prior ticks each
filed that observation (`WORKER_REPORT_PUBLISH_WEDGE_SUSPECT_DISPOSITION_2026-08-09.md`, 8/8 wrong;
`WORKER_REPORT_FIFTH_WEDGE_SUSPECT_DISPOSITION_2026-08-10.md`, 8/8 wrong). The list is **identical**
across all three episodes bar one entry, while the cause has been different every time — which is
the tell: it is not tracking the failure at all.

Each was checked against the gate's actual red before being set down. The gate runs `-x`; it stopped
at the seat-guard test, so nothing downstream of it ran either time.

| cited finding | disposition |
|---|---|
| `..._TWO_UNIMPORTABLE_PHASE2A_MODULES_2026-08-09` | not implicated — the phase2a modules sit under the gate's own heavy-ignore list and nothing imports them. Re-frozen, unchanged. **Third** episode cited, third not-the-cause. |
| `..._WRITE_TIME_GATE_FIELD_SWALLOW_2026-08-08` | not implicated — AO2/G6 is a commit-refusal control; this was a test failure inside the gate's checkout. Re-frozen, unchanged. |
| `..._THE_SECOND_DIRECTION_NEEDS_ITS_OWN_POPULATION_2026-08-09` | not implicated — D11/D12 denominator work, not in the gate's path. Re-frozen, unchanged. |
| `..._TWO_NUMBERS_ONE_NAME_2026-08-09` | not implicated — H27 measurement; class already closed via `SHARED_QUANTITY_CONTRACT`. Re-frozen, unchanged. |
| `..._THE_NAIVE_ARM_KEEPS_THE_LIVE_TONE_2026-08-10` | not implicated — collections-tone A/B contamination, no test of its subject reached the stop point. Re-frozen, unchanged. |
| `..._THE_MODELS_STORAGE_HEATER_IS_NOT_ONE_2026-08-09` | not implicated — world-layer fidelity gap. Re-frozen, unchanged. |
| `..._THE_INDEX_READS_THE_WORKING_TREE_2026-08-09` | not the cause, but **same disease, and it predicted this one**: a control whose subject is the working tree rather than the committed state. The seat-guard test reads `path.read_text()`, which is why the guard looked green on this machine while HEAD stayed red for 12.5 hours. Re-frozen — but its rank is now earned twice over. |
| `..._THE_PRE_COMMIT_GATE_MAPS_NO_TESTS_TO_A_DATA_FILE_2026-08-09` | **closest relative, but NOT the enabler this time.** Its subject is non-`.py` paths mapping to zero tests; this commit changed a `.py` file that mapped to a perfectly real test — just not the one that guards it. Re-frozen. Its two-strike standing from wedge #5 is untouched. |

## The enabler, which was not cited and is not any of the eight

`tools/pre_commit_test_gate.py::tests_for('background/suite_duration_watch.py')` returns
`['tests/background/test_suite_duration_watch.py']` — a **confident, plausible, non-empty, wrong**
answer. `test_seat_guard_daemons.py` is a population test whose stem matches no module it guards, so
no stem-based selector can ever reach it. PW3 was green at commit time and red at HEAD one cycle
later.

Filed as its own finding rather than fixed inside the unwedge (SELF_INTERRUPT_DISCIPLINE):
`WORKER_FINDING_A_POPULATION_TEST_IS_UNREACHABLE_BY_ANY_STEM_SELECTOR_2026-08-10.md`. It is the
**third half** of the impact-selector class, and the first that returns a wrong answer rather than an
empty one.

## Recommendation — proceeding on this unless redirected

**Stop citing the suspect list, and derive it from the failing test instead.** The list has now been
0-for-24 across three episodes while the gate's own log named the cause in one line every single
time. It is a fail-open control in the exact R15 sense: it can never be wrong out loud, so it is
never corrected — and it costs each drawn tick its opening minutes on findings with no measured
relationship to the red.

Concretely, the alarm should cite the **failing test's own file and module** (a real relationship it
already has in hand — it prints the test path in the same message), and present filed findings, if
at all, as "open findings, possibly unrelated". That is a one-field change to the alarm payload.

The previous tick's recommendation — take the pre-commit-gate selector work at rung 1 — stands and is
strengthened: it now has **three** wedges (#4 aspect-named, #5 non-`.py`, #6 population) against a
remedy that already exists in-repo and is already mutation-proven
(`tools/select_impacted_tests.py` refuses to narrow on unprovable impact).

— Worker tick, 2026-08-10.
