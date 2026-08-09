# [WORKER-REPORT] The third publish wedge had two causes, and the second one was a full disk our own diagnostics filled (2026-08-09)

**Written by:** the scheduled worker tick drawn on the RUNG-1 publish-gate wedge (48 consecutive
episode failures, no pass at HEAD `450bf6903`).

**Headline, one line:** the wedge proper was the KNIFE2 allowlist shrink outrunning its code
again — **already fixed at HEAD** by `450bf6903` before this tick started — and what kept the
gate red afterwards was **`/tmp` (a 7.8GB tmpfs) exhausted by 4.4GB of repo checkouts abandoned
by the two earlier wedges' own diagnostic runs**, which git reported as `fatal: cannot mkdir`
and, worse, as `git is not installed`.

---

## Cause A — the ratchet, and it was already cured

`observed-with-evidence`. The publisher's own log names the blocking test in one line:

```
[2026-08-09 19:31 UTC] [process_run] Publish gate RED -- blocking test(s):
    FAILED tests/architecture/test_epistemic_wall_ratchet.py::test_no_new_sim_reads_company
```

The allowlist in that test had already deleted all sixteen `simulation.* -> saas.customers`
edges (KNIFE pass 2); the code that removes them was not in HEAD. Measured by import statement:

| ref | `^(from\|import) saas` in `simulation/` |
|---|---|
| `3cc852aff` (last recorded failure) | 61 |
| `450bf6903` (HEAD now) | 43 |
| working tree | 43 |

`450bf6903` ("adopt(KNIFE2): land the orphaned lane's residue") landed `company/interfaces/
supply_book.py` plus the sixteen rewired modules at 19:29, between the last recorded failure and
this tick. Verified directly rather than inferred — a clean `git archive HEAD` checkout of
`450bf6903`, which is exactly the gate's own subject, runs the previously-red module green:

```
$ git archive HEAD | tar -x -C /tmp/headcheck-89tH && cd /tmp/headcheck-89tH
$ SIM_FAST_MODE=1 python3 -m pytest tests/architecture/test_epistemic_wall_ratchet.py -q
12 passed, 8 warnings in 5.46s
```

The gate agreed on its own: `Publish gate recovered -- cleared wedge state, re-armed alarm` at
19:29 and again at 19:35.

## Cause B — and then the disk ran out

`observed-with-evidence`. One minute after recovering, the gate failed again, differently:

```
[2026-08-09 19:36 UTC] Publish gate: could not make the HEAD checkout a git repo: git is not installed
[2026-08-09 19:36 UTC] Publish gate: `git init` in the HEAD checkout failed rc=128 -- fatal: cannot mkdir
```

git was installed and working. The real state:

```
$ df -h /tmp
tmpfs           7.8G  5.9G  1.9G  76% /tmp
```

with **4.4GB of it abandoned full-repo checkouts** — `headclone` (473M), `headgate` (203M),
`gatechk` (189M), `fullgate-OzGK`, `gateB-G9SW`, `headcheck3`, `hg2`–`hg6`, `verify-head-*`,
`gatehead_repro`, `ratchet_probe`, `headtree`, `pristine`, `fresh`, `postcommit-*`, `headchk*`,
plus ~90 `h24_badmap_*` dirs. **Every one of them was left by a diagnostic run, not by the
gate** — `_head_checkout` removes its own tmpdir in a `finally`, and there were zero
`publish-gate-head-*` dirs on disk. The two earlier unwedge ticks filled the filesystem that the
third unwedge needed.

**Audited before pruning** (forks die dirty): three of the debris dirs were real git repos.
`headclone` and `gatehead_repro` carried only machine logs over commits already in main history;
`gatechk` carried the KNIFE2 work, verified byte-identical to what `450bf6903` had already
landed (`diff` clean on `simulation/live_population.py`, `run_phase1e.py`, `run_phase2b.py`,
`company/interfaces/supply_book.py`). Nothing was lost.

```
free before=1921M after=6372M reclaimed=4451M
tmpfs           7.8G  1.6G  6.3G  20% /tmp
```

## What was built, not just cleaned

Deleting 4.4GB fixes today. The mechanism is that **the failure did not name its own cause** —
and it failed at exactly the moment a tick was hunting a red test, so it read as one.
`background/process_run_complete.py::_head_checkout` now pre-flights free space BEFORE the
extraction, while the cause is still legible, and refuses with a line that says DISK and says
*"HEAD may be green; nothing here says a test failed."* Fail-closed is unchanged and deliberate
(R15: an unavailable check is a failed check) — the pre-flight does not turn a red into a green,
it makes the red self-describing.

R15 both ways, in `tests/background/test_publish_gate_disk_preflight.py` (8 tests, green):
the guard **fires** on its named defect (exhausted filesystem refused, log names disk, and
explicitly not `git is not installed`); it is **not vacuous** (ample space proceeds; an
*unmeasurable* filesystem proceeds rather than wedging publishing on a stat failure); and the
**mutation** — threshold set to zero — lets the same full disk through, which is what proves the
refusal comes from this guard.

## Filed, not fixed here (SELF_INTERRUPT_DISCIPLINE)

**`_classify_gate_failure` is rc-only, so it cannot express "not a test failure" — second
instance, therefore a class.** `rc > 0` maps to `test_regression`, labelled *"a real regression
is possible"*. The first instance is recorded in this file's own source at the commit-timeout
branch: *"the wedge detector recorded it as a test_regression, which it was not, and the
diagnosis pointed at the test suite for hours."* Cause B is the second: a full disk is not a
regression, and the alarm told the next tick to *"FIX the red test"* when there was none. R10
says the class, not the instance — the fix is a channel the gate can use to say what kind of
failure it was (a dedicated exit code, or a reason written alongside the rc), not another
special case. QUEUED.

## Disposition of the eight cited findings — the second time the same eight were wrong

The RUNG-1 alarm again cited the same eight findings as "already holding the suspects" and again
instructed the tick to draw them FIRST. **None of the eight named either cause**, for the second
consecutive wedge. Each is dispositioned as the alarm requires; none is re-frozen, none silenced,
none moves.

| Cited finding | Verdict for THIS wedge | Disposition |
|---|---|---|
| `TWO_NUMBERS_ONE_NAME` | Not the cause. H27 measurement; class already closed via `SHARED_QUANTITY_CONTRACT`. | QUEUED, unchanged. |
| `TWO_UNIMPORTABLE_PHASE2A_MODULES` | Not the cause — but **partly overtaken**: `450bf6903` rewired `run_phase2a.py` through the seam. Its `sum()` over `eac_kwh: None` is untouched; re-read before building. | QUEUED, unchanged. |
| `WRITE_TIME_GATE_FIELD_SWALLOW` | Not the cause. A commit-refusal control; both causes here were inside a checkout. | QUEUED, unchanged. |
| `THE_MODELS_STORAGE_HEATER_IS_NOT_ONE` | Not the cause. World-layer fidelity gap; no relation to publishing. | QUEUED, unchanged. |
| `THE_PRE_COMMIT_GATE_MAPS_NO_TESTS_TO_A_DATA_FILE` | Not the cause. Still the closest relative on the list — a control whose scope comes from a filename proxy. | QUEUED, unchanged. Worth its rank. |
| `THE_SECOND_DIRECTION_NEEDS_ITS_OWN_POPULATION` | Not the cause. D11/D12 denominator work. | QUEUED, unchanged. |
| `THE_GHOST_PUSHER_GUARD_FIRES_ON_A_CONCURRENT_WRITER` | Not the cause, and did not fire this time. Its complaint is still live. | QUEUED, unchanged. |
| `THE_INDEX_READS_THE_WORKING_TREE` | Not the cause, and again the same *disease* as cause A — a control measuring the tree rather than HEAD. It has now predicted this class twice. | QUEUED; **rank deserves a look**. |

`WORKER_REPORT_PUBLISH_WEDGE_SUSPECT_DISPOSITION_2026-08-09.md` filed exactly this complaint
about exactly these eight after the previous wedge, and the alarm cited them again unchanged.
That is the evidence that the citation list is not a suspect list and is not learning: **8 of 8
wrong, twice, while the publisher's own log named the blocking test in a single grep both
times.** The already-filed remedy stands — derive the suspects from the FAILING TEST's file, or
label them "open findings, possibly unrelated". Restated here rather than re-filed.

## Related

* `docs/staging/WORKER_REPORT_PUBLISH_WEDGE_SUSPECT_DISPOSITION_2026-08-09.md` — the first
  disposition of the same eight.
* `docs/staging/WORKER_FINDING_THE_EPISTEMIC_WALL_IS_BREACHED_AT_HEAD_2026-08-09.md` — named
  cause A's class, hours before this wedge, and was not cited either time.

— Worker tick, 2026-08-09.
