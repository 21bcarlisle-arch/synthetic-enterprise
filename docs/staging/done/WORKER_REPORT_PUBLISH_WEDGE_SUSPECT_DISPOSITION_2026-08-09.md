# [WORKER-REPORT] The publish-gate alarm cited eight suspects. None of them was the cause. (2026-08-09)

**Written by:** the scheduled worker tick that closed the ~180-min wedge (25 consecutive gate
failures, no pass at HEAD since `765a7397c`).

The RUNG-1 wedge alarm carries a `cited_findings` list — the filed findings it believes are
"already holding the suspects" — and instructs the drawn tick to dispose of each *first*. That
instruction was followed. This is the disposition, and the headline is that **the citation
mechanism selected eight findings, none of which named either real cause.** That is worth
recording, because a suspect list that reads as authoritative and is wrong costs the next tick
its first twenty minutes.

## The two real causes (measured, R9)

| # | Blocking test | Cause |
|---|---|---|
| 1 | `test_epistemic_wall_ratchet.py::test_no_new_sim_reads_company` | KNIFE pass 2's **allowlist shrink was committed and its code was not**. HEAD carried all sixteen `simulation.* -> saas.customers` edges with the grandfathering already deleted. |
| 2 | `test_blocked_atom_visibility.py::test_the_real_staleness_clocks_...` | The gate's HEAD checkout **was not a git repo**, so AO11's `git blame` of the map died with `fatal: not a git repository`. |

Cause 1 was named — precisely, hours earlier — by
`WORKER_FINDING_THE_EPISTEMIC_WALL_IS_BREACHED_AT_HEAD_2026-08-09.md`, which the alarm **did not
cite**. Cause 2 is the second instance of the class whose first instance was patched at
`576105747`; it was not filed as a finding at all, so nothing could have cited it.

## Disposition of the eight cited findings

Each is dispositioned as the alarm requires — none is re-frozen, none is silenced, and none of
them moves as a result of this tick. All eight stay QUEUED at their filed rank.

| Cited finding | Verdict for THIS wedge | Disposition |
|---|---|---|
| `TWO_UNIMPORTABLE_PHASE2A_MODULES` | Not the cause. Two `run_phase2a*` modules cannot be imported; the gate's failing tests never import them. Adjacent by filename to cause 1's blast radius, which is likely why it was cited. | QUEUED, backlog, unchanged. |
| `WRITE_TIME_GATE_FIELD_SWALLOW` | Not the cause. AO2/G6 is a *commit-refusal* control; the wedge was a *test* failure inside a checkout. Different surface entirely. | QUEUED, unchanged. |
| `THE_PRE_COMMIT_GATE_MAPS_NO_TESTS_TO_A_DATA_FILE` | Not the cause, but the closest relative on the list: it is the same family — a control whose SCOPE is derived from a filename proxy. It caused the *previous* wedge, not this one. | QUEUED, unchanged. Worth its rank. |
| `THE_SECOND_DIRECTION_NEEDS_ITS_OWN_POPULATION` | Not the cause. D11/D12 denominator work; not in the gate's path. | QUEUED, unchanged. |
| `TWO_NUMBERS_ONE_NAME` | Not the cause. H27 Expert-Hour measurement; class already closed via `SHARED_QUANTITY_CONTRACT`. | QUEUED, unchanged. |
| `THE_GHOST_PUSHER_GUARD_FIRES_ON_A_CONCURRENT_WRITER` | Not the cause, and now **partly overtaken**: its subject is a fixture that shells out to git inside the gate. The checkout is a real repo from this commit on, which removes one of the two ways that fixture can misfire. Its actual complaint — that the guard cannot distinguish a test's commit from a concurrent writer's — is untouched and still live. | QUEUED, unchanged. Re-read it against the new checkout before building. |
| `THE_INDEX_READS_THE_WORKING_TREE` | Not the cause, and it is the same *disease* as cause 1 (a control measuring the tree rather than HEAD) at a different organ. It predicted this class. | QUEUED, unchanged; rank deserves a look. |
| `THE_MODELS_STORAGE_HEATER_IS_NOT_ONE` | Not the cause. A world-layer fidelity gap in `electric_storage`; no relationship to publishing. | QUEUED, unchanged. |

## The finding this leaves

**The alarm's suspect list is not evidence, and it currently reads as if it were.** Eight of eight
were wrong; the one finding that named the cause exactly was absent. A tick that obeys the
instruction "draw these FIRST, before any product or HARDEN work" spends its opening on a list
with no measured relationship to the red test — while the red test's own name and traceback,
already in `sim-runner-log.md`, identify the cause in one line.

Filed as its own finding rather than fixed here (SELF_INTERRUPT_DISCIPLINE): the citation
mechanism should either derive its suspects from the FAILING TEST's own file/module (a real
relationship), or stop presenting them as suspects and present them as "open findings, possibly
unrelated". Presenting an unranked keyword match as a suspect list is a fail-open control: it can
never be wrong out loud, so it is never corrected.

**Disposition of that finding:** QUEUED. Not blocking — this tick read the log instead.

## Related

* `docs/staging/WORKER_FINDING_THE_EPISTEMIC_WALL_IS_BREACHED_AT_HEAD_2026-08-09.md` — named
  cause 1 and was not cited.
* `DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09.md` — the ruling whose change of subject
  surfaced both causes.

— Worker tick, 2026-08-09.
