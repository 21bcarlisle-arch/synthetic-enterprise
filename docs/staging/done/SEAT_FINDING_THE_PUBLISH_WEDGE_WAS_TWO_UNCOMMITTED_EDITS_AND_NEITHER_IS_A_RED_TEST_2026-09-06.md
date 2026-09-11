**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# The 29-hour publish wedge was two uncommitted edits in the shared tree, and the test the record named had been green for six commits

**Found 2026-09-06 by the delivery seat, drawn on the publish-gate wedge (31 consecutive failures,
`wedge_since` 2026-09-05). The record named a red test. There was no red test.**

---

## What the record said, and why it was pointing at the wrong thing

`docs/observability/.publish_gate_state.json` carried
`blocking_tests: ["tests/design/test_atom_records_store.py::test_declarations_match_the_store_both_directions"]`
and `total_red: 1`, recorded against `74e9be26a`.

That test is green, and green at HEAD `23cbe058b`, and green in a clean `git archive HEAD` extract
(14 passed both ways, 1.52s both ways — the identical count and duration in both trees is what
rules out the vacuous-pass reading of a clean extract). `a43ee63fe` and `2ebae50ea`, both in
`74e9be26a..HEAD`, are the repair. **The named red was fixed six commits before this draw fired.**

The `blocking_tests` field is LATEST-wins over test refusals only, so it kept naming a spent red
while the thing actually refusing every commit changed underneath it. The newer evidence was
already in the same file and in a different key: `liveness_surface_refusal`, timestamped 1418s
*after* the last entry in `failures`, at `ff32a572b`, cause `gate_refusal`, and its captured tail
is the **orphan ratchet**, not pytest.

## The two causes, both uncommitted, both invisible to any per-commit reader

At HEAD, `tools/orphan_ratchet.py` exits 0. In the shared working tree it exits 1 on nine modules.
The gate reads the whole tree, so both of these refused every `git commit` in this tree — the
publisher's included.

**Cause A — a `--freeze` output that dropped seven still-orphaned entries.** The working-tree copy
of `docs/design/orphan_baseline.json` (written 02:13 today, uncommitted) removed
`company.market.bsc_settlement_run_register`, `tools.company_data_contract_battery` and the five
`tools.weather_cell_*` / `tools.weather_driver_sensitivity` modules from the grandfathered list,
while adding six of its own. All seven are still orphans, and all seven are grandfathered at HEAD.
A freeze taken against one tree state is a **regression** when replayed against another: it does
not merely fail to grandfather the new, it un-grandfathers the old.

**Cause B — an in-place edit from a stale base deleted the only edge to a live module.**
`background/process_run_complete.py` is held dirty by a lane refactoring `publish_standing_red`
into an untracked `background/standing_red`. Its base predates `2026-09-05`, so alongside that
deliberate refactor it deletes the eighteen-line block in `generate_dashboard_json` that calls
`tools.generate_regulatory_data`. That call is the **only** edge reaching that module anywhere in
the tree — `capability_index` gives it `callers: ['background.process_run_complete']` at HEAD and
`callers: []` in the working tree — so deleting it orphaned both it and
`company.regulatory.fuel_mix_disclosure` behind it. Neither is in either baseline, because neither
has ever been an orphan.

This is the shape already on the record as *a merge adopting one side's rewrite deletes the other's
purely additive work* — except **no merge happened**. An in-place working-tree edit does it with no
conflict, no merge commit, and nothing for a diff-of-the-merge review to look at.

## Two more of the same shape, found by running the gate rather than reading its record

With the ratchet green the gate's own argv still refused, and both reds are the same class again —
working-tree state no commit contains, invisible to every clean extract.

**Cause C — an in-flight rename finished everywhere except the control.** A lane renamed the reason
mix's `causes_not_observable_on_this_population` to `causes_not_in_the_interval`, for a good and
recorded reason: the SVT route made the interval's population and the *declared* population two
different sets, and the old name had the artefact calling a cause unobservable on a population that
the field directly above it declared able to observe. Producer, both readers and the artefact all
carry the new name, uncommitted since 2026-09-03 07:10. `tests/architecture/
test_a_departure_reading_declares_its_population.py` was left on the old one.

It was **not** a mechanical rename, which is presumably why it stalled. The control asserted the
interval's causes and the population's observable causes were the *same set* — an equality that was
free while the two sets were one set, and that the separation makes fail on an artefact that is now
strictly more honest. Repaired to the direction that carries the property: the interval may not
report a cause the population cannot see (subset), and a cause the population cannot see may not be
merely omitted (subset the other way). Equality was the pinned-to-today's-answer form.

**Cause D — an untracked artefact deleted a null control's negative case.** The same file's null
control read `covers_svt_route` off two committed captures, one renewal-only *because nothing had
ever written an SVT sibling beside it*. A lane generated `docs/reports/
c2_departure_factors_svt_segment_decisions.json` — still untracked — and the renewal-only capture
became a two-route one with no line of the test or of `declare` changing. The negative case left
the tree; what remained asserted `False is False` against a `True`.

**A null control whose negative case is a path another writer can fill in is not a control**, and
this one could not have been fixed by re-pointing it: no capture left in the tree lacks a sibling.
The negative case is now the same real bytes staged into `tmp_path` where no sibling can appear —
the loader, `svt_sibling` and `load_svt_decisions` all still run for real; only the absence is
staged. Poison rounds from a clean 18-pass baseline: forcing `covers_svt = True` kills the null
control; four independent artefact mutations each kill the repaired cause control and nothing else.

## Why nothing could see it

Both causes live in files no commit contains. `tools/surgical_land` gates the tree the commit
*would* create, where these two working-tree copies do not exist, so landings kept going through
this same gate while the publisher's `git commit` in the dirty tree was refused by it — the
two-doors-disagree case `orphan_ratchet.py`'s own comment records from 2026-09-03, recurring with
a different pair of files. And the wedge record's `suspects.modules` named
`merge_atom_status` / `simplifications_store` / `maturity_map_store`: the neighbourhood of the
**spent** red, scored from the field that was still naming it.

## The repair

Both fixes are to the working tree only. Relative to HEAD both files are now HEAD-plus-the-other-
lane's-additions, so **there is nothing here to land**: HEAD was already correct on both counts and
it was the shared tree that had drifted off it.

- The seven dropped entries restored to `orphan_baseline.json`, the other lane's six additions kept.
- The eighteen-line `generate_regulatory_data` block restored to `process_run_complete.py`, the
  other lane's `standing_red` refactor kept, with a comment naming what its loss costs so the next
  edit from a stale base has something to hit.

`tools/orphan_ratchet.py` exits 0 in the shared working tree afterwards, and all fifteen non-test
gates in `tools/git-hooks/pre-commit` exit 0 over it.

**C and D DO land, and only as one unit.** The repaired control alone would red HEAD, because
HEAD's artefact still carries the old key — the test, the producer, both readers and the artefact
are one commit or none. Landing the abandoned lane's rename is a judgement call and it is recorded
as one: the work has been static for three days, it is internally coherent, its reasoning is
written at the site, and leaving it in the tree leaves a modified tracked artefact that the
committed control disagrees with — a landmine for whichever lane next touches `docs/reports/`.
Measured before landing: HEAD plus those five files, clean extract, 24 passed.

Two staging documents were also finishing a half-staged room move — the index held
`root -> records/` while an identical untracked copy sat back in the root, which is
`--content-remove` leaving the deleted path untracked. Both root copies were byte-identical to the
tracked ones; deleting them took `finding_classes --check` from FAIL to PASS.

## What is worth building, and what is not

The recording defect is real and narrow: **a wedge record whose headline field only ever names test
reds will keep naming a spent one through an entire non-test outage.** `.publish_gate_state.json`
already held the newer, correct, non-test evidence in `liveness_surface_refusal`; nothing made the
reader prefer the later fact. That is a one-leg fix at the read end, not a new register.

The freeze defect is the more expensive one and it is not obviously worth a mechanism yet: one
occurrence. Worth stating plainly in `orphan_ratchet --freeze`'s own output that a freeze is a
whole-list replacement and can un-grandfather, which is a print statement, not a control.

Explicitly NOT proposed: any gate on editing a file another lane holds dirty. The shared tree is
shared by design and the cure is worse.
