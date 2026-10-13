**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# A run's `producing_commit` names HEAD, not the bytes that ran, and its `resolved_at` is the stamping time

*Delivery seat, 2026-10-13 ~20:20Z, while waiting on the publish of `run_output_2248e3baf_20261013T134447Z.json`.*

**What the artefact says.** `producing_commit` = `{"commit": "2248e3baf", "resolved_at": "2026-10-13T15:39:51Z",
"resolved_when": "at process start, before the world ran -- this is the commit whose code drew every figure below"}`.

**Two things in that row are wrong.**

1. **`resolved_at` is not the process start.** The runner journal has the run starting at 13:44:47Z and ending at
   15:40:25Z. 15:39:51Z is when the artefact was stamped. `tools/run_annual_report.py::_run_identity_header` writes
   `stamped_at` into `resolved_at` on both branches, so on the `from_launch` branch the time contradicts the
   `resolved_when` sentence beside it. The commit it names may well have been captured at launch; the time cannot show it.
2. **A HEAD sha does not name the code in a dirty shared tree.** The shared tree's HEAD stayed at 2248e3baf from 07:50Z
   until it fast-forwarded at 18:10Z. 5f61c2262 (the SLC 20-24 ungraded-estimate fix, on origin at 08:49Z) is **not** an
   ancestor of 2248e3baf (`git merge-base --is-ancestor` checked). The item that drew this work says the working copy
   of `saas/reporting/compliance_scorecard_population.py` already held origin's (5f61c2262) bytes while the run ran.
   **I could not check that claim myself:** the fast-forward at 18:10Z restamped the file's mtime, and the copy on disk
   now equals 5f61c2262 whichever way it was before. If the claim is true, the row says "2248e3baf drew every figure"
   about a run whose scorecard code was 5f61c2262's.

**Why it matters.** Any reader who asks "does this run carry fix X?" by checking ancestry against `producing_commit`
gets the wrong answer whenever the shared tree holds bytes that are not at HEAD, and this tree does that most of the time.

**Smallest fix that can fail.** Write the launch time into `resolved_at` on the `from_launch` branch. Also record
whether `git status --porcelain -- company saas simulation sim` was clean at launch. If it was not, add
`"dirty_paths": [...]` and say so in `resolved_when`, so the row does not claim that the commit drew every figure.
That needs a control which launches from a tree with one dirty `saas/` file and asserts the row names it.
Not built this turn, because the publish of this very artefact was in flight.
