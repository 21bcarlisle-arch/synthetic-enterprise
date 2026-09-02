# [SEAT PRE-REGISTRATION] Whether tonight's census can write a complete row at all

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`
**Filed:** 2026-09-02, BEFORE the measurement. Lane 0: *"the measurement arrives on its own; what
is not established is that it can be recorded."*
**Discharged:** `tests/tools/test_head_green_census.py::test_a_completed_run_lands_a_row_the_REAL_register_accepts`,
`tests/tools/test_head_green_census.py::test_a_log_parsed_after_the_fact_records_no_sha_so_it_cannot_manufacture_a_run`,
`tests/tools/test_head_green_census.py::test_a_census_that_could_not_record_says_so_on_the_channel_he_reads` — all three mutation-proven
below. The recording path is measured to work and the one defect this exposed (the alarm not
carrying the fate of its own observation) is fixed in the same commit, so severity reads down from
BLOCKING to RECORDED on this line.

If the answer had been no, the 03:34 firing would spend ~60 minutes and record nothing, and the
director's question about the 830 reds would wait another day.

## The subject

`tools/head_green_census.main()` → `_record_observation()` → `background.head_red_register.record()`
→ a row in `docs/observability/head_red_observed.json` carrying a non-null `passed`.

## What is already established (not measured here)

1. Run 1's row (`2026-09-02T04:30:02+00:00`, head `ec2e0b1a4`, 830 red, `"passed": null`) was a
   **hand transcription of a COMPLETE run**, not a truncated one. Settled in
   `background/head_red_register.record`'s docstring: the 830 node ids match the journal 830-for-830.
2. **The recording path has never run live, not once.** The 04:30 journal prints
   `NEW_RED: 830 test(s) newly failing:` and carries **no `  register: ...` line** — the line
   current `main()` prints between the verdict and the causes. That run was the pre-`bc57c8e30`
   code, in which `_record_observation` did not exist. Tonight at 03:34 BST is its **first live
   exercise**.

So the direction's question — truncated, killed, or seeded by hand — is answered: **seeded by hand,
from a complete run.** What is NOT established is (2)'s consequence, and that is what this
pre-registration is about.

## Why this is not already covered by a test

`tests/tools/test_head_green_census.py` drives `_record_observation` twice, and **both times it
substitutes a fake `background.head_red_register` module** (`monkeypatch.setitem(sys.modules, ...)`
with a `_Reg` stub). Those tests pin the head-attribution defect and nothing else. **The real
`record()` has never been driven by a real `evaluate()` result.** The seam between the two — the
`passed` field's journey from pytest's summary line into the stored row — is untested end to end.

And `_record_observation` is documented **NEVER RAISES**: it catches `Exception` and returns a
note. So if the real `record()` refuses or throws tonight, the census prints one line, exits, and
**no row lands** — with no alarm distinguishing that from success.

## The prediction (recorded before running anything)

**P1.** Driving `main(["--from-log", <a realistic complete pytest log>])` with the store paths
redirected to a temp dir WILL append a row whose `passed` is non-null and equal to the log's
summary count. *Confidence: moderate.* The chain reads as correct; what is unproven is that it has
ever been executed.

**P2.** The row's `head` will be `null`, because `--from-log` deliberately declines to attribute a
parsed log to a commit. This is correct behaviour, NOT a defect, and it means `--from-log` **cannot
be used to manufacture run 2**. Run 2 must come from a real `run_suite`.

**P3.** If P1 is refuted, the cause will be inside the `except Exception` in `_record_observation`
— i.e. the failure will be **silent**, printed as a note rather than raised.

## What would refute each clause

- P1 refuted by: no new row, or a row with `"passed": null`, in the temp store after the run.
- P2 refuted by: a non-null `head` on a `--from-log` row (that would be the invented-sha defect).
- P3 refuted by: `main()` raising, or the failure being visible as a non-zero exit distinct from
  the ordinary NEW_RED exit 1.

## Constraint I am binding myself to

**I will not run the census by hand today.** `pgrep -af process_run_complete` showed pid 673399
live this turn on the shared 15 GB cgroup; a second unscoped suite beside it could kill the live
one, and that kill would be recorded as this episode's next failure — manufacturing the red I went
looking for. The probe below runs `--from-log` against an existing log: seconds, not an hour.

## Result

*Measured 2026-09-02 ~15:37 BST. The predictions above are left exactly as written.*

**P1 — CONFIRMED.** `main(["--from-log", <complete log>])` with `reg.OBSERVED_PATH` and
`reg.REGISTER_PATH` redirected appended exactly one row:

```json
{ "at": "2026-09-02T14:37:44+00:00", "causes": {}, "head": null, "passed": 24204, "red": 2 }
```

`passed` is non-null and equals the log's summary count. The census also printed the
`register: 2 owed, written to ...` line, so `_record_observation` ran to completion rather than
being swallowed. **The recording path works.** Tonight's run, if it finishes, will land a complete
row.

**P2 — CONFIRMED.** `head` is `null`. `--from-log` cannot attribute a parsed log to a commit and
does not pretend to, so it **cannot be used to manufacture run 2**. Run 2 must come from a real
`run_suite`, i.e. from the 03:34 firing.

**P3 — NOT REACHED.** P1 was not refuted, so the silent-failure branch was never exercised by the
probe. It is now exercised by a test instead (see below), which is the stronger form.

### What the probe did NOT establish, said plainly

The `"causes": {}` above is an artefact of my synthetic log's shape, **not** evidence that cause
parsing is broken. The real 04:30 run parsed causes correctly (`OSError x760, AssertionError x33,
…`). No claim is made here either way.

### The defect the probe exposed, which was not in the predictions

The probe confirmed the path works. It also made visible something the predictions did not
anticipate: **`_record_observation`'s failure note reaches only stdout, and this process's stdout
is a systemd journal.** The NTFY payload — the one surface the director reads — carried the red
count and said nothing about whether those reds were *stored*. So a night that measured 830 reds
and recorded none of them would have been indistinguishable, on every surface he sees, from one
that recorded them all. That is the register's own founding complaint, one level up: a fail-closed
verdict composed into an artefact no published surface reads.

Fixed in `tools/head_green_census.py` — the payload now carries `register`.

### Controls landed with this, all three mutation-proven

| Control | Mutation | Verdict |
|---|---|---|
| `test_a_completed_run_lands_a_row_the_REAL_register_accepts` | forward `passed=None` | KILLED |
| `test_a_log_parsed_after_the_fact_records_no_sha_so_it_cannot_manufacture_a_run` | fall back to live HEAD | KILLED |
| `test_a_census_that_could_not_record_says_so_on_the_channel_he_reads` | drop `register` from the payload | KILLED |

These are the first tests in the module to drive the **real** `head_red_register`. The two
pre-existing tests that touch `_record_observation` both substitute a fake module, which is why
the seam could go untested through the whole life of the control.

### The constraint, discharged against the artefact

`git status --porcelain` during this work never listed `docs/observability/head_red_observed.json`,
and the store still holds exactly **one** run row. No census was run by hand. The publish gate
(`process_run_complete`, pid 673399) was live throughout and was not disturbed.

## What is still owed, and by whom

Run 2 itself. It arrives at **03:34 BST on 2026-09-03** from the timer, not from this seat. When
it lands, `docs/staging/SEAT_PREREGISTRATION_WHETHER_THE_TMPFS_DIAGNOSIS_EXPLAINS_THE_830_RED_2026-09-02.md`
is graded clause by clause against it — remembering the honest constraint it already binds: **830
is a floor, not the complete set**, so a residual count *above* a run-1 sub-count is not
automatically a refutation, while one *below* it still is.

The route into the draw for the survivors needs no new work: `staging_rooms._with_the_head_red_register`
already draws `HEAD_RED_REGISTER.md` whenever `head_red_register.drawable()` is non-empty, and
`tests/background/test_red_at_head_has_a_route_into_the_draw.py` pins it. Writing the register is
what arms it, and tonight's run is what writes it.
