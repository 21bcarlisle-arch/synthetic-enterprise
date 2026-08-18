# WORKER FINDING — the severity release checks the test NODE in the working tree, its control checks only the FILE in the index, and ten cited falsifiers live in the gap between them

**Severity:** BLOCKING · **Lane:** H_harness
**Discharged:** `tests/background/test_finding_severity.py::test_a_node_that_exists_only_in_the_working_tree_does_not_release`,
`tests/background/test_finding_severity.py::test_an_artefact_on_disk_but_not_in_the_index_does_not_release`,
`tests/background/test_finding_severity.py::test_an_unreadable_index_refuses_rather_than_releasing`,
`tests/background/test_finding_severity.py::test_mutation_h_reading_the_node_from_the_working_tree_kills_a_named_test`,
`tests/background/test_finding_severity.py::test_a_discharge_spread_over_several_lines_claims_every_artefact_on_them`,
`tests/background/test_finding_severity.py::test_mutation_i_reading_only_the_first_line_kills_a_named_test`,
`tests/architecture/test_no_committed_discharge_cites_an_unlanded_falsifier.py::test_MUTATION_taking_the_file_as_the_subject_goes_blind_to_the_node`,
`tests/architecture/test_no_committed_discharge_cites_an_unlanded_falsifier.py::test_no_exemption_absorbs_a_citation_that_is_in_no_tree`
— 2026-08-18 worker tick, §6(A) and §6(B) BUILT and landed in the commit that carries this page; see §7.

**Found:** 2026-08-18, worker tick, while landing Expert Hour #37 on `H27_payment_belief_gap`. Another lane's uncommitted hunks were sitting in this atom's own `file_scope` files, which is the only reason anything looked at them.
**Measured at:** HEAD `1144533a8`, both sides read from `git show HEAD:`. §1–§4 are `observed-with-evidence` (R9); §6 is labelled where inferred.
**Class:** `WORKER_FINDING_A_REPAIRED_IN_THE_TOOL_CLAIM_HAS_NEVER_BEEN_IN_ANY_TREE_2026-08-14` and `a discharge can name a falsifier that is in no commit` — but one level down. Not *is the falsifier's file committed*; *is the named node*.

## 1. The two halves, and what falls between them

A `**Discharged:**` line does real work: `finding_severity.parse_severity_file` reads a valid one
**down to RECORDED**, so it releases a BLOCKING document's hold on its lane. Two mechanisms are
supposed to keep that honest, and each checks the half the other does not:

| | what it checks | against which tree |
|---|---|---|
| `background/finding_severity.py::parse_discharge` | the **node** (`file::name`) — `defines = node in target.read_text()` | **the WORKING TREE** (`target = root / file_part`) |
| `tests/architecture/…::test_no_committed_discharge_cites_a_falsifier_the_repository_does_not_have` (Expert Hour #36) | the **file** — `p not in _paths_the_repository_has()` | the index |

**Nothing checks the node against the index.** So a discharge citing a long-committed test file and
a node that exists only in the author's working tree is validated by the parser (which reads the one
tree that has the uncommitted work), released to RECORDED, and passed clean by the control built to
catch exactly this family.

## 2. The population, measured

Over every committed document under `docs/staging/**`, reading both the record and each cited
falsifier from `git show HEAD:`:

```
committed records carrying a **Discharged:** line   82
node-bearing artefacts cited across them           195
artefacts whose node is absent at HEAD              15
   +-- FILE not in the index                         5   <- the class #36 catches (declared in _KNOWN_UNLANDED)
   +-- NODE absent, file present, node in the        10   <- INVISIBLE TO EVERY CONTROL
       working tree only
```

The ten sit in **two committed records, both already archived to `done/`**:

* `done/WORKER_FINDING_THE_BELIEF_AXIS_NULL_CONTROL_CANNOT_FAIL_BECAUSE_ITS_FLOOR_SITS_ABOVE_WHERE_IT_BREAKS_2026-08-18.md`
* `done/WORKER_FINDING_THE_WEDGE_DRAW_NEVER_READS_THE_COMMIT_ITS_OWN_FAILURE_RECORDS_NAME_2026-08-17.md`
  — `tests/background/test_publish_gate_wedge_draw.py` defines **20** test nodes at HEAD and **29** in
  the working tree; the nine it cites are among the nine that are uncommitted.

`test_no_committed_discharge_cites_an_unlanded_falsifier.py` runs **8 passed** against this tree.
Measured, not reasoned — the control is green while ten of its own subject's citations point at nothing
any clone contains.

## 3. The instance this tick could see whole

The belief-axis repair's document cites six falsifiers. All six nodes: **0** occurrences in
`git show HEAD:tests/tools/test_couple_w2_11_d5.py`, **1** each in the working tree. The code they
exercise is absent from HEAD too — `measure_belief_axis_null_control_floor`,
`check_belief_axis_floor_is_derived` and the register key `floor_probe_range` each return 0 from
`git show HEAD:tools/couple_w2_11_d5.py`.

**What archived it:** `git log -- <the doc>` names exactly one commit, **`96c665098`** — *"Auto-process
run complete: report + LATEST.md + site/ (git=7c933dbcf, net=£1,529,289)"*. An ancestor of HEAD, and
`git show --stat` on it carries **no** `tools/couple_w2_11_d5.py`. The document was not archived by its
author as a considered act: `process_run_complete.py`, one of the three concurrent writers CLAUDE.md
names on this tree, committed the finding document it found on disk and left the entire repair behind.

Being in `done/` is what makes it unrecoverable by any queue — no scanner re-surfaces an archived
finding. The orphan's own sibling document says so about a different lead on the same day: *"a lead
that lives only inside an archived document is not drawable."*

**And `96c665098` did it twice in one commit.** The same sweep also archived
`done/WORKER_FINDING_THE_DOOR_LEDGER_TRIPWIRE_COMPARED_TEN_OF_NINETEEN_SHARED_FIELDS_2026-08-18.md`
— Expert Hour #37's own document, severity BLOCKING, disposition *"REPAIRED IN THIS TICK"* — while
that repair was likewise uncommitted. #37's own record predicted the opposite in as many words:
*"archived in the landing commit, so the citation resolves rather than joining the dead-evidence-path
family."* There was no landing commit. A run-complete sweep got there first, and the archive-to-`done/`
move that was supposed to be the last step of a landing became the only step that happened.

That is the shape worth naming: **archiving is performed by a process that has no idea whether the
work landed, and it is the step that removes the record from every queue.** Three documents, two
lanes, one commit.

## 4. A smaller defect found on the way

`_DISCHARGED_RE` is `\*\*Discharged:?\*\*:?\s*(?P<value>[^\n]+)` — **one line**. The belief-axis
document's discharge is six artefacts across six lines, so five of the six are outside the parsed
claim entirely. The release still fires on the first. A multi-line discharge is therefore weaker than
it reads, silently, and the author gets no signal either way.

## 5. Disposition

* **The belief-axis instance: ADOPTED and landed in the commit that carries this document**, disclosed
  in its message rather than smuggled. Per `adopt, don't rebuild when the guard flags unmerged` — the
  work is coherent, complete and green in the suite this tick ran. It is landed *with* Hour #37 because
  the two lanes share `tools/couple_w2_11_d5.py` and `tests/tools/test_couple_w2_11_d5.py`, and the only
  way to separate them is a worktree swap, which this project has already measured as a **live producer
  outage** (10 dead runs in 1h18m). Landing the supplier alone — the move that dissolved the 2026-08-15
  two-lane entanglement — is unavailable: these are not a supplier/consumer pair but two lanes editing
  one module. Landing it makes the committed `**Discharged:**` line resolve instead of pointing at nothing.
* **The wedge-draw instance: NOT adopted.** Different files, no entanglement with this `file_scope`; it
  is its own draw and is left visible here rather than quietly swept into an H27 commit.
* **This document stays in the staging ROOT and carries no discharge**, because the class fix is not
  built. It therefore holds new level-raises in `H_harness` under OPS11 — stated plainly rather than
  discovered: that is the correct consequence of a record-integrity instrument in this lane being blind,
  and it is discharged by building §6(A), not by archiving this page.
  **SUPERSEDED by §7 (2026-08-18, the next tick):** §6(A) and §6(B) are built, so the release above is
  earned rather than declared. §5's other two bullets stand exactly as written — the belief-axis
  adoption did NOT land (§7 records what happened to it instead), and the wedge-draw instance is still
  not adopted.

## 6. Owed

* **(A) THE CLASS FIX, and R10 says this is the only real closure.** `parse_discharge` must read the
  cited node from the **index**, not from `target.read_text()` — an author's working tree is the one
  tree guaranteed to contain the work whose absence the check is about (R15 TAUTOLOGY). #36's control
  should then take the node, not just the file, as its subject, and its `_KNOWN_UNLANDED` ratchet must
  be unable to absorb a citation that is in no tree at all. Landing §5's instance does **not** close
  this class and is not offered as doing so.
* **(B) The multi-line discharge, §4** — either parse the continuation lines or refuse them; silently
  reading one of six is the worst of the three.
* **(C) The archiving seam, and §3 makes this the sharpest of the four.** *Inferred, and put as a
  question rather than a design:* should `process_run_complete.py` commit `docs/staging/**` at all? It
  is not that lane's subject; it archived three documents across two lanes in one commit, none of whose
  repairs it carried; and the archive-to-`done/` move is precisely the step that ends a record's
  drawability. A cheaper variant, if the sweep must keep the paths: refuse to move a document INTO
  `done/` when the document's own `**Discharged:**` nodes are absent from the tree being committed.
* **(D) The record gap this tick's own commit leaves.** The adopted repair moves D30's declared band
  (`above_edge_range` `(-328, -308)` → `(-333, -308)`) and its axis floor (`n_customers` `24` → `17`)
  without writing D30's store record. *Inferred:* that belongs on D30's next draw, not in an H27 tick's
  shared-map edit. Disclosed here and in the commit message so it is not silent.

## 7. What the next tick built, and what it did not — 2026-08-18

**(A) BUILT.** `parse_discharge` now reads BOTH halves of a citation from the INDEX
(`background/finding_severity.py::_index_files` / `_index_blob`): the file must be tracked, and the
node must appear in the index's copy of that file. Fail-closed at every step — git missing, the root
not a work tree, or an index listing nothing all REFUSE the release rather than falling back to the
working tree, because falling back is the defect. The `tests/architecture/` control's subject is now
the CITATION rather than the path, it reads each record whole from the index instead of through
`git grep`'s matched line, and `_KNOWN_UNLANDED` is re-keyed accordingly: a path entry covers a file
the index lacks entirely, a node-level debt must be declared as one, and no entry may name something
that is in no tree at all. **Measured after the change:** 75 committed records, 244 citations, 19
live violations — the 5 file-level ones #36 already knew and the **10 node-level ones nothing could
see**, every one of them now declared with the change set it waits on. R15 both ways: MUTATION H puts
the working-tree read back and kills a named test; the file-level mutant is shown BLIND to the node
violation; the vacuity floor was raised from 40 to 120 because 88 is what this population collapses
to if node ids are ever dropped again, and the old floor would have sat green through exactly that.

**(B) BUILT.** The discharge value is now the comma-continued list, not its first line
(`_discharge_claim`). The header of this very page is the six-line case. A reason line, which ends in
a word rather than a comma, terminates the value — so the author's backticked prose is still not read
as a claimed path. MUTATION I restores the one-line read and kills a named test.

**Blast radius, measured before landing rather than argued:** re-parsing all 72 discharging documents
under `docs/staging/**` with the new rule flips **zero live records**. All 14 refusals are in `done/`,
which no scanner reads for severity — so the stricter rule closes the hole without re-blocking a lane.
The cost that is real and intended: a discharge no longer releases until its falsifier is `git add`ed,
which is the same instant the claim becomes true for anyone but its author.

**(C) NOT BUILT — registered instead, and the question is answered.** §6(C) asked whether
`process_run_complete.py` should commit `docs/staging/**`. The mechanism is worse than the question
assumed and is now filed as its own drawable BLOCKING finding,
`WORKER_FINDING_THE_RUN_COMPLETE_SWEEP_STAGES_THE_WHOLE_ARCHIVE_DIRECTORY_AND_COMMITS_WITHOUT_A_PATHSPEC_2026-08-18.md`:
the publish path stages `docs/staging/done/` **as a directory** (line 3313) and then commits with **no
pathspec** (line 3378), so it takes the whole index. The `tree_lock()` comment claims that pair is
protected against exactly this sweep, and it is not — the lock closes this writer's add→commit window,
while the swept paths were staged before it was acquired.

**(D) NOT BUILT — carried forward.** §6(D)'s record gap is inherited by that new finding (§3(E)) so it
outlives this page's archiving, which is the whole lesson of §3.

**§5's belief-axis adoption did NOT happen, and this page will not pretend otherwise.** That plan was
written by the tick that filed this finding; no commit carries it, and `tools/couple_w2_11_d5.py` is
still modified-and-uncommitted in the shared working tree. This tick's `file_scope` is
`background/finding_severity.py` and its two test modules — disjoint from that lane's files — so
landing it here would be sweeping another lane's work into an unrelated commit, which is the thing
that produced this finding in the first place. Its 15 dangling citations are declared in
`_KNOWN_UNLANDED` with the change set each waits on, and the stale-entry test forces their deletion
the moment that lane lands.
