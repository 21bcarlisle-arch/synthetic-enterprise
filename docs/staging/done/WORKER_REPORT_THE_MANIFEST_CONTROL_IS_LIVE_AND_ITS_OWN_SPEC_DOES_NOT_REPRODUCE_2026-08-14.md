# WORKER REPORT — the landed-manifest control is live and wired to the commit; the mutation its own spec named does not reproduce, and was not tuned until it did

**Severity:** RECORDED · **Lane:** H_harness
**drawn:** RUNG 1c blocking finding, `CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md` (BLOCKING,
`H_harness`), 2026-08-14 scheduled tick

## What was drawn, and what was actually owed

The class carries 27 instances and 3 BLOCKING ones. Triaged by each document's own close section
rather than by the class header, two of the three were already repaired in-tool and named their own
falsifiers; the single genuinely owed item was **Control 1**, from
`WORKER_FINDING_A_FINDING_RECORDED_ITS_OWN_INSTANCE_AS_FIXED_AND_THE_FIX_HAD_NEVER_BEEN_COMMITTED_2026-08-14.md`:

> A document may not claim a path LANDED unless that path's content is reachable from a commit.

That document is the **third instance in three days**, and it records that the first two were both
closed with prose. R3 says the second false completion on one mechanism means build the control.

## What landed this tick

`tools/landed_manifest_check.py` — the control. For each path a staging document THIS COMMIT
CHANGES claims LANDED: (1) ABSENT — not in the tree the commit creates; (2) STAGED — content for it
sits in the real index that this commit is not carrying, so a reader cannot tell which version the
claim is about. Every read is git plumbing against a tree or the index; `git status` is never
consulted and the working tree is never read, including for the document text itself.

`tools/pre_commit_test_gate.py` — the automated caller, inside the staging-room branch that runs
BEFORE the pure-docs early return, because a staging-only commit selects no test targets and is
exactly the commit that files the claim. Fail-closed at every step.

`tools/symbol_landing_check.py` and `tests/tools/test_symbol_landing_check.py` — **ADOPTED, not
written here.** Both were UNTRACKED while `tools/pre_commit_test_gate.py` already imported the
first at line 669, fail-closed. No commit had noticed because the step needs a staged `.py` and the
recent commits were docs-only; this one stages `.py`, so it was refused against a HEAD checkout
until they landed. That is the sibling of the finding below, in the gate's own dependencies, and it
is the reason "`git ls-tree HEAD` the modules your fix CALLS" is a rule. Adopted as-is and verified
green (17 passed) rather than rebuilt. The unit had a third, equally unlanded piece, found only
because landing the module made the step live and reddened
`tests/tools/test_pre_commit_test_gate.py::test_pytest_subprocess_env_strips_GIT_star` **in the
gate's HEAD checkout while it passed on this desk** — a single uncommitted hunk neutralising the
new step in a test whose subject is the pytest subprocess's environment. Landed with it. The new
landed-manifest step needs no such neutralisation: it early-returns unless a `docs/staging/` path
is staged, and that test stages `background/supervisor.py`.

`tests/tools/test_landed_manifest_check.py` — ten falsifiers against real git repositories, both
ways: fires on ABSENT, fires on the 2026-08-14 staged-but-not-carried shape, green when the claim is
true (a control that reds on honest landings is how a gate gets disabled), green when the path
landed earlier and is clean, plus one test per killer pattern — FAIL-OPEN (an unparseable claim is
NAMED as `unchecked`, never skipped), TAUTOLOGY (blank the working-tree copy after staging; it must
still red), FAIL-SILENT (the gate must contain the caller).

## The spec's own mutation does not reproduce, and the parser was not widened until it did

The finding specified its falsifier: re-run against the sibling pathspec finding at parent
`75290668f`; it must red on `tools/simplifications_store.py`. **It cannot.** That document's
manifest claims the SYMBOL half (`atom_name`, `name` in `NOTE_FIELDS`) and names in backticks only
`tools/migrate_atom_names.py` and `tests/design/test_maturity_map_facets.py` — both of which *are*
at HEAD. The supplier path appears in the document twice and **zero times inside the manifest
section**: only in the evidence block, where the document is correctly reporting that it never
landed. Path-existence could not have fired anyway — that file existed at `75290668f` (blob
`4ec6f9bf`).

So the class has two halves and neither control spans both: the PATH shape is this control's, the
SYMBOL shape is `tools/symbol_landing_check.py`'s and was already live. Pinned as a tripwire, not
argued: `test_tripwire_the_real_instances_manifest_names_symbols_not_the_supplier_path` fails if
that document is ever edited to name the supplier path, at which point the specified mutation
becomes reachable and should be built. Widening the parser until an evidence line read as a claim
would have been reading prose as a manifest — the defect already filed against exactly that shape.

## Measured on real history before wiring it

Over the 120 most recent commits touching `docs/staging/` (clause 1 only; the historical index is
not reconstructable, so the staged clause was exercised against a purpose-built repository
instead): **2 reds in 120 commits, both true positives**, each claiming a path never added on any
ref, then or since — verified with `git log --all --diff-filter=A`:

* `0c0733e0a` claims `tests/tools/test_no_orphan_published_customer_artefacts.py` landed.
* `40bbc32ef` claims `docs/observability/ntfy-delivery-log.md` landed.

Neither is repaired here (SELF_INTERRUPT_DISCIPLINE); both are queued as the class's next
instances. The control's own error bar is printed on its green path rather than buried: across
those commits it parsed 41 paths and reported **42 documents `unchecked`** — a claim seen, no path
parsed. That is roughly half the population, and it is the direct consequence of manifests that
promise symbols rather than files.

**It refused its own announcing commit, twice, and both refusals were right to be acted on.** The
first was a true positive (the untracked gate dependency above). The second was a FALSE positive
that changed the control: `git commit -- <pathspec>` builds the resulting tree from the WORKING
TREE, so an edited-but-never-`git add`ed path reads index(==HEAD) != tree, which is the ordinary
edit-then-commit shape rather than a false claim. Clause 2 now discriminates on "is there content
in the index that is not at HEAD and that this commit is not carrying", with the 2026-08-14 shape
and this one as paired falsifiers — either alone would make the discrimination a tautology in one
direction. A first draft also read any body line containing "landed" as a claim, which billed a
document for CITING another's false claim; the claim surface is now structural (header block plus
the manifest section), and narrowing it raised paths checked from 41 to 50 while lowering unchecked
from 42 to 40.

## What was found on the way and deliberately NOT swept in

Attempting to discharge the second blocker,
`WORKER_FINDING_THE_LANDING_TOOL_EXTRACTS_INTO_THE_TMPFS_THE_GATE_WAS_MOVED_OFF_2026-08-14.md`
("REPAIRED IN THE TOOL", three mutation-proven controls cited), showed its repair has **never been
in any tree** — 6 occurrences of `EXTRACT_ROOT` on this desk, 0 at HEAD, nothing on any ref, both
files unstaged. It stays BLOCKING and undischarged. Filed as a fourth instance of the class, with
the sharper half of the finding: `parse_discharge` validates cited artefacts against the WORKING
TREE, so the release valve would have granted that discharge on evidence no second reader can see.
See `docs/staging/WORKER_FINDING_A_REPAIRED_IN_THE_TOOL_CLAIM_HAS_NEVER_BEEN_IN_ANY_TREE_2026-08-14.md`.

## Lane state

`CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md` stays **BLOCKING** in `H_harness`: one of its three
blockers is discharged here with named falsifiers, one is undischarged for cause (above), and the
third's residue (controls 1 and 3 of the `pytest -x` finding) is unchanged — control 3's remedy
still exists UNWIRED in `background/tree_divergence.py`, already recorded by its own document.

**Evidence:** `python3 -m pytest tests/tools/test_landed_manifest_check.py` — 9 passed ·
`python3 -m background.finding_classes --check` — PASS (0 failures) · the 120-commit sweep above.
