# WORKER FINDING — a pure `git mv` reads as a NEW oversized function to the size ratchet

**Found:** 2026-08-10, executing `KNIFE3_wall_crossing_paydown` step 8 (`A_composition_lift` part 1).
**Class:** control false positive — a tripwire firing on an event that carries no growth.
**Disposition:** QUEUED per SELF_INTERRUPT_DISCIPLINE. Not fixed on sight; the supply of harness
findings is infinite and this one is non-blocking (`rollout_state=warn`).

## Observed, with evidence

Seven files moved `simulation/ -> tools/` by `git mv`. `git diff --cached -M --stat` reports
**`7 files changed, 0 insertions(+), 0 deletions(-)`** — the bodies are byte-identical. The size
ratchet nevertheless reports:

```
[new_function_over_cap] tools/run_phase1c_full_window.py::main: 70 > 60 (+10) -- new function -- decompose it
[new_function_over_cap] tools/run_phase1c_renewals.py::main: 79 > 60 (+19) -- new function -- decompose it
```

Neither `main()` was written today; both are years old and unchanged by this commit.

## Mechanism (`tools/size_ratchet.py::_new_function_findings`)

```python
new_spans = function_spans(index_texts[path])
old = set(function_spans(head_texts[path])) if path in head_texts else set()
```

`head_texts` is keyed by **path at HEAD**. A renamed file has no entry, so `old` is empty and every
function in it is "new" — including ones over the 60-line cap that were grandfathered a moment
earlier at the old path. Rule 2b has no rename detection; `git`'s own `-M` similarity index, which
would resolve it, is not consulted.

**Rule 1 does not have this defect** (this commit carried the seven baseline keys across the rename
by hand, so `tools/run_phase1c_renewals.py: 153 > 143` still fires — the debt followed the file,
which is correct). The gap is specific to the FUNCTION rule, which reads git rather than the
baseline JSON.

## Why it matters beyond noise

1. **It taxes exactly the move the KNIFE programme is made of.** Every remaining cut in
   `A_composition_lift`, and B1's whole shape, is "move a misfiled module across a package
   boundary". Each such commit will emit spurious `new_function_over_cap` findings proportional to
   how many >60-line functions the moved file has.
2. **The pressure it applies is the wrong one.** The finding says "decompose it" about a function
   this commit did not touch, inside a commit whose whole point is *not* to change behaviour. Acting
   on it would mean editing code in a pure-rename commit — precisely what the instrument/measured-
   thing separation in this pass forbids.
3. **It is a false-positive-jams-pipeline shape if the rollout state ever flips to blocking.**
   Today `rollout_state=warn` so it only pollutes `size_ratchet_warnings.jsonl`. A blocking rollout
   would make every legitimate module move un-landable without an override, and overrides logged for
   renames would hollow out the override log's meaning.

## The fix, when drawn

Resolve renames before diffing function spans: ask git for the rename map
(`git diff --cached -M --name-status`, or `--find-renames` on the same census the ratchet already
takes) and look `old` up under the file's **pre-rename** path. R15 both ways:

* **Fires:** a genuinely new >60-line function in a renamed file must still be found (so the fix
  cannot be "skip renamed files", which would be a fail-open — a rename would become a laundering
  channel for oversized functions, the same shape as the unwalked-bridge hole step 7 closed).
* **Silent:** a byte-identical rename must produce zero function findings.
* **Vacuity guard:** the test tree must contain a real >60-line function, or "silent" proves nothing.

## Not a defect, for the record

The three `file_exceeds_baseline` findings on the moved files
(`run_phase1c_renewals 153>143`, `run_phase3a 94>89`, `run_phase4b_on_phase2b 75>70`) are CORRECT
and pre-existing — they were already in `size_ratchet_warnings.jsonl` against the old paths on
2026-08-09. This commit moved the baseline keys with the files deliberately, so the debt carried
rather than being re-frozen at today's larger count. A rename must not be a way to reset a ratchet
floor.
