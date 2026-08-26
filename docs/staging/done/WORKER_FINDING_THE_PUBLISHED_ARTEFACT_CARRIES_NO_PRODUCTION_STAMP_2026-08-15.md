# WORKER FINDING — the published artefact carries no production stamp, and the only writer that would stamp it did not write it

**Severity:** LATENT · **Lane:** W4_the_wall · **Disposition:** QUEUED (not fixed on sight)

**Found:** 2026-08-15, during the EP6 per-key provenance walk (`docs/design/simplifications/EP6_wall_protocol_typing.yaml`, third note)
**Class:** an artefact whose own provenance is unrecorded, found while establishing provenance
**Measured at:** HEAD `26c047083`. Everything below is `observed-with-evidence` (R9).

## The measurement

`tools/run_annual_report.py::save_run_output_json()` is the documented writer of
`docs/reports/run_output_latest.json`. It does three things unconditionally — no flag, no
branch:

```python
data = extract_report_data(run_output)
commit_hash = _git_commit_hash()
timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
data["_cache_meta"] = {"git_commit": commit_hash, "generated_at_utc": timestamp}
...
RUN_OUTPUT_LATEST_PATH.write_text(payload)
versioned_path = RUN_OUTPUT_VERSIONED_DIR / f"run_output_{commit_hash}_{timestamp}.json"
versioned_path.write_text(payload)
```

The live artefact has neither output:

    python3 -c "import json; d=json.load(open('docs/reports/run_output_latest.json')); \
                print('_cache_meta' in d)"
    -> False

    ls docs/reports/run_output_versioned/
    -> the directory does not exist

The file itself is real and current: 4,156,355 bytes, mtime 2026-08-15 02:47:30, 92 top-level
keys, parsed in full without error. So the artefact was written — just not by the writer that
stamps it, and not by any path that leaves a versioned copy behind.

## Why this is filed rather than fixed

`SELF_INTERRUPT_DISCIPLINE`: the supply of findings is infinite and fixing on sight is the
treadmill. Fixing it also requires knowing WHICH writer produced the file, and that is a
separate walk — the grep for `run_output_latest` names ten modules, and this pass did not
establish which of them wrote these bytes. Naming a culprit without that walk would be the
`inferred`-presented-as-`observed` shape R9 exists to stop.

## Why it matters, stated at its real size and no larger

**It does not invalidate the EP6 walk it was found during.** That walk measured shipped CODE
(two AST walks of two reducers), and the row shapes it quotes from the artefact would be the
same whoever wrote it. This finding is not a retraction of anything.

**What it does cost** is one link in every claim that reads this file. `_cache_meta.git_commit`
is the only thing tying a published figure to the tree that computed it. Without it:

* R11 ("verify to the rendered value") can confirm a number is on the page and cannot confirm
  which code produced it.
* R14 ("no financial figure without its clock") is satisfied on the BASIS labels, which are
  in-payload — but the artefact's own *production* clock is absent, so "as of which run" is
  answerable only from filesystem mtime, which any copy or checkout resets.
* The versioned copies are the only history. There are none, so a figure that moves between
  two publishes cannot be diffed against its predecessor at all.

**And it is the same shape as the atom it was found under.** EP6 exists to make the wall's
messages typed and versioned. This is the artefact that carries the widest channel across that
wall, and it is unversioned and unstamped in the most literal possible way — the field exists,
the writer sets it, and the bytes on disk do not have it. That is `from_log_entry`'s
`schema_version` defect (already filed,
`WORKER_FINDING_THE_WALLS_CONFORMANCE_CONTROL_IS_IMPORT_SHAPED_2026-08-13.md`) one level up:
a version that cannot disagree, and now a stamp that is not there at all.

## Suggested shape, recorded not asked (`NEVER_ASK_WITHOUT_RECOMMENDING`)

Not "add the stamp" — it is already added, by a writer nobody used. The defect is that a
second write path exists and is silent about itself. The falsifiable form:

1. **Find the actual writer** before changing anything (the walk this finding did not do).
2. **Make the stamp a READ-side requirement, not a write-side courtesy.** The consumers
   (`saas/reporting/annual_report.py --from-json`, the dashboard generators, the site data
   builders) should REFUSE an artefact with no `_cache_meta` rather than proceed. A stamp that
   only the writer cares about is a stamp that stops existing the first time someone writes the
   file another way — which is precisely what happened here.
3. **R15 both ways**, and the fail-dangerous direction is the one that matters: a stamped
   artefact must still be accepted, and the mutation is deleting `_cache_meta` from a fixture
   and asserting every consumer reds. A control that only fires on a hand-built empty file
   would be the FAIL-OPEN pattern this project has caught in itself repeatedly.

**Where it sits in the queue:** below the EP6 channel-split work it was found beside, because
that work decides which wire this artefact even is. Nothing published is currently *wrong*
because of this; what is missing is the ability to prove it right.
