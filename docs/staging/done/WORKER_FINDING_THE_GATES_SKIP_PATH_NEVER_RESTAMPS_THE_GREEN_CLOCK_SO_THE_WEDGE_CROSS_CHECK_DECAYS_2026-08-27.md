**Severity:** LATENT · **Lane:** H_harness · **Rank:** backlog, after the current delivery-lane item

# FINDING — the publish gate's SKIP path returns a green without re-stamping the green CLOCK, so the wedge detector's independence cross-check decays into "permanently armed" the moment one failure lands after the last real suite run

**Found by:** the RUNG-1 priority-zero wedge draw, 2026-08-27 08:25Z, at HEAD `21d83d92e`.
**Filed, not fixed on sight** (SELF-INTERRUPT DISCIPLINE): this is a harness monitoring control,
publishing is NOT actually blocked (§1), and the supply of harness findings is infinite.

**Relationship to the existing class member**
`WORKER_FINDING_A_GREEN_PUBLISH_CANNOT_CLEAR_THE_WEDGE_UNTIL_A_SECOND_SUITE_THE_DEADLINE_DOES_NOT_KNOW_ABOUT_FINISHES_2026-08-20`
(discharged, `6444f2778`): that one is about the **CLEAR** — `record_publish_gate_success` being
routed through a process that is still running. This is about the **INDEPENDENCE CROSS-CHECK** —
a different file (`.last_tested_green.json`), a different writer, a different predicate
(`_gate_pass_supersedes_failures`). They compound; neither closes the other.

---

## 1. Publishing is NOT blocked — observed, not inferred (R9)

The doorbell says the gate "has been FAILING for ~129 min and is BLOCKING ALL publishing". That is
wrong about the present tense, and it was already wrong when the draw fired.

| claim | evidence | class |
|---|---|---|
| the publish commit LANDED | `b0f3f1a3f Auto-process run complete: report + LATEST.md + site/ (git=f4b0b6334, net=£150,186)` | observed |
| it reached origin | `git rev-parse HEAD origin/main` → both `21d83d92e6e7…`; `b0f3f1a3f` is an ancestor | observed |
| the commit hook PASSED | `commit_hook_duration.jsonl` final row: `{"timestamp":"2026-08-27T07:37:18Z","git_hash":"f4b0b6334","duration_seconds":404.61,"outcome":"pass"}` | observed |
| the originally-refusing gate no longer refuses | `python3 -m background.finding_classes --check` → `check: PASS (0 failures)` at HEAD | observed |

**The original refusal cause is already repaired.** The four in-window failures were all recorded at
`f4b0b6334`; the 07:13Z one refused in **1.19 s** — far too fast for a suite — with the banner:

```
[test-gate] ❌ FINDING-CLASS CONSOLIDATION BROKEN -- COMMIT REFUSED.
  - STALE SEVERITY CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md:
    prints BLOCKING, instances derive LATENT — re-render (`--render`)
```

That document was re-rendered in `49387e0ce`, which is **on HEAD's history and newer than every
recorded failure**. No test was ever red in this episode, exactly as the doorbell suspected.

## 2. Why the alarm cannot switch itself off

`supervisor.py::_publish_gate_wedge_draw` disarms on either of two conditions. Both are now
structurally unreachable:

**(a) `head == last_tested`** — `.last_tested_hash` is `f4b0b6334`; HEAD is `21d83d92e`. Six worker
commits landed after the gate last ran, so this equality is unsatisfiable on a busy tree. The
docstring already anticipates this ("exact HEAD equality is unsatisfiable precisely when the gate is
healthy and busy") and delegates to (b).

**(b) `_gate_pass_supersedes_failures`**, whose operative line is:

```python
if not float(green_ts) > newest_failure_ts:
    return False
```

with the live values:

| quantity | source | value |
|---|---|---|
| `green_ts` | `.last_tested_green.json` → `{"sha":"f4b0b6334","ts":1787808100.15}` | **05:21:40Z** |
| `newest_failure_ts` | `.publish_gate_state.json`, newest of 4 | **07:13:47Z** |

`05:21:40 > 07:13:47` is False → not superseded → **the rung stays armed**, and will re-fire on
every tick forever.

## 3. The defect: SKIP returns a green through a path that never touches the clock

`green_ts` advances in exactly one place — `_run_gate_in`, on the suite's `rc=0`. But
`run_fast_tests` never reaches that writer when the hash is unchanged:

```python
def run_fast_tests(git_hash: str):
    if LAST_TESTED_HASH_FILE.exists():
        if LAST_TESTED_HASH_FILE.read_text().strip() == git_hash:
            log("Tests skipped — already passed for git={}".format(git_hash))
            return True, False        # <-- green returned; clock NOT re-stamped
```

The sim runner keeps emitting runs at one subject hash (`f4b0b6334` for every cycle this morning),
and that hash **equals** `.last_tested_hash` — so every cycle takes the SKIP branch, and
`green_ts` has been frozen at 05:21:40Z all morning. Observed: `stat` gives
`.last_tested_green.json` and `.last_tested_hash` an mtime of `06:21:40 +0100` (= 05:21:40Z) while
`.publish_gate_state.json` was rewritten at `08:13:47 +0100` (= 07:13:47Z).

**So the clock only ever moves forward on a cache MISS, while failure timestamps move forward on
every failure.** Once any failure is recorded after the last real suite run, the comparison is
permanently false and the only remaining escape is a fully successful publish that CLEARS
`failures` — which is precisely the path §1's sibling finding shows can be delayed indefinitely.

`LAST_TESTED_HASH_CONTRACT` asserts the sidecar is written "by the SAME writer, in the SAME rc=0
branch, immediately after the hash — so the independence stated above is unchanged, and the SKIP
consumer is untouched". That is true of the *write* and false of the *consequence*: the contract
reasons about SKIP only as a suite-time optimisation and never as a **clock stall**. This is the
R15 FAIL-OPEN shape one level up — the control is not reading a wrong value, it is reading a
correct value that has stopped moving.

## 4. Cost, and why this episode repeats

The draw is PRIORITY ZERO, so it outranks every product lane. It has now consumed this tick and,
per the doorbell's own text, has been re-firing across an episode in which **no test was ever
judged**. Each tick pays a full Opus context to re-derive §1. Meanwhile the tree is clean against
origin and the site is serving current data.

Second-order cost observed this tick: the live publisher (PID 509497) had 9 concurrent `pytest`
processes and 2 `claude -p` workers competing with it; its post-commit suite was 49 min into a step
that `publish_gate_duration.jsonl` records at ~540 s when uncontended, against a
`GATE_SUITE_TIMEOUT_SECONDS = 3800` deadline. A wedge draw that wakes extra workers onto a
contended box is capable of manufacturing the timeout it was sent to diagnose.

## 5. Closure — what a fix must do, and what must NOT be done

1. **Re-stamp the clock on the SKIP path.** A cache hit IS a green for the subject SHA; it should
   write `{"sha": git_hash, "ts": now}` before `return True, False`. This is the one-line repair
   and it is honest: the claim "this SHA is green" is exactly what SKIP asserts.
2. **Do NOT widen it to "any green ever".** Dropping the strict `>` re-opens the 2026-08-20 bug
   (ancestry running backwards across a stack-drained queue) that the clock was introduced to fix.
3. **R15 mutation, both ways, before this is claimed discharged:** freeze the clock and assert the
   rung stays ARMED; re-stamp it and assert the rung goes SILENT with the failures still on file.
   A test that only exercises the cache-miss path cannot see this defect at all — the fixture must
   take the SKIP branch, which means `.last_tested_hash` must equal the marker's hash.

**Falsifiable prediction (the cheap way to confirm before building anything):** the next publish
cycle whose subject hash is still `f4b0b6334` will log `Tests skipped — already passed`, leave
`.last_tested_green.json` at ts `1787808100.15`, and the RUNG-1 draw will fire again — even though
`finding_classes --check` is green and origin is current.

## Class registration

Belongs to `publish_gate_and_wedge`.

Declared explicitly rather than left to the title regex, and that is itself an instance of the
hole `finding_classes.py` documents beside `_CLASS_REGISTRATION_HEADING_RE`: this title names its
MECHANISM (a clock that is not re-stamped) and carries no `wedge`/`publish`/`gate` token in the
matched position, so `classify_subject` returned `None` and `--check` PASSED with the document
archived and unlisted. Observed this tick: after `--render`, `grep -c` for this filename in
`CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md` returned **0** and the instance count stayed at 47.
