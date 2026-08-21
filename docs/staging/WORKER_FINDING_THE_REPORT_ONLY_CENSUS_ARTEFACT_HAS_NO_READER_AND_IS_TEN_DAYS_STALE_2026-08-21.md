**Severity:** LATENT · **Lane:** H_harness

# The report-only census artefact has no reader and is ten days stale

**Found:** 2026-08-21, unwedging publishing at HEAD `30e1ac3a3` (57th consecutive gate
failure). Filed rather than fixed, per SELF-INTERRUPT DISCIPLINE — the machine was not
blocked on it.

---

## Observed, with evidence

`docs/observability/publish_gate_red_census.json` is written by
`tools/enumerate_publish_gate_reds.py` (`CENSUS_ARTEFACT`, line 61). Its content on
2026-08-21 22:37Z:

```
head_sha    b905f46751c0d9b26024d5d6afa0b74ae856bffc
started_at  2026-08-11T07:19:15Z
outcome     complete
red_count   1
red_files   ["tests/background/test_derived_artefact_register.py"]
```

HEAD at that moment was `30e1ac3a3`. `b905f467` is not HEAD and has not been HEAD for ten
days. The file's mtime is 2026-08-20 06:09 — later than the run it describes, so the mtime
does not date the measurement either.

**No consumer reads it.** A repo-wide grep (`grep -rn publish_gate_red_census --include=*.py
--include=*.js --include=*.json --include=*.md .`) returns exactly one code site: the
producer at `tools/enumerate_publish_gate_reds.py:61`. Every other hit is prose — archived
findings, and one `autonomous-runner-log.md` line telling a human to eyeball its stamp.
`tests/background/test_publish_gate_red_census.py` is NOT a reader of this file; it covers
the in-gate census in `process_run_complete`, which is a different record.

The wedge doorbell's DEPTH clause — the thing that says "the
report-only census enumerated the WHOLE red set at this HEAD" — is
`supervisor.py::_wedge_depth_clause`, and its `total_red` comes from the gate state file
written by `process_run_complete._write_blocking_tests`, i.e. the IN-GATE census, not this
artefact.

## Why it is worth a finding anyway

`inferred`, and stated as such: this is a record that LOOKS like the census the doorbell
cites, is named as if it were, sits in the directory a diagnosing worker greps first, and
carries a `head_sha` field that makes it read as current. This tick spent a step on it
before establishing it had no reader. The failure mode is the one this project has already
named — a plausible sibling record answering a question it was not measuring
(`measurements_that_mirror`).

Note the honest half: the artefact does carry its own `head_sha` and `started_at`, so it is
*checkable*. It is stale, not lying. What it lacks is anything that makes a reader check.

## Disposition owed

One of:

1. **Delete it** — a producer with no consumer is dead weight; `enumerate_publish_gate_reds`
   can print to stdout for the human who runs it.
2. **Stamp it as advisory** — add a top-level `reader: none (report-only, run by hand)` and
   have the tool refuse to leave a record whose `head_sha` is not HEAD at write time.

Do **not** wire it into the wedge path as a third census. Two censuses already disagree
about which HEAD they describe; a third would not settle it. See
[[feedback_re_derive_a_constant_from_the_record_its_control_reads]].

## Falsifier

`tests/tools/test_enumerate_publish_gate_reds.py` — assert the written record's `head_sha`
equals the repo HEAD the tool ran against, and that the assertion fails when the tool is
handed a record from another commit. That test file exists and is inside the publish gate's
blocking set, so the control would run where it matters.
