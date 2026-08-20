**Severity:** BLOCKING · **Lane:** H_harness
**Discharged:** `tests/background/test_finding_severity.py::test_a_retired_falsifier_releases_and_records_that_its_evidence_is_HISTORICAL`,
`tests/background/test_finding_severity.py::test_a_falsifier_in_no_tree_and_never_deleted_is_still_refused`,
`tests/background/test_finding_severity.py::test_a_retired_file_is_not_an_AMNESTY_for_a_node_it_never_defined`,
`tests/background/test_finding_severity.py::test_mutation_i_dropping_the_pre_retirement_node_check_kills_a_named_test`,
`tests/background/test_finding_severity.py::test_a_discharge_below_the_header_block_DOES_release`,
`tests/background/test_finding_severity.py::test_a_discharge_written_mid_SENTENCE_is_prose_and_still_does_not_release`,
`tests/architecture/test_no_committed_discharge_cites_an_unlanded_falsifier.py::test_MUTATION_dropping_the_retirement_answer_reads_an_honest_record_as_a_lie` — 2026-08-20 worker tick, LANDED across two commits: the repair and its falsifiers first, this record second, so every node above is at HEAD and any clone can run them. §5 is built in BOTH controls and each now carries its own null control — the last citation is the TRIPWIRE's, added by the second tick because the first built the tripwire's retirement clause without a test that could fail on it, while claiming both halves were covered. §4 is fixed by widening the parser to the whole document under a line-start anchor, which the measurement in §8 justifies over the recommendation as written.

# WORKER FINDING — a falsifier can be RETIRED WITH ITS SUBJECT, and neither control can say so, so deleting a page re-opens findings it has nothing to do with; and the two controls disagree about where a discharge is even allowed to live

**Found:** 2026-08-20, RUNG-1c BLOCKING draw on `H_harness` (`CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md`)
**Class:** R15 — wrong subject (variant: *the subject was deliberately deleted and the control reads that as a lie*)
**Not repaired here.** The design is stated in §5 with its null control; what is owed is named in §7.

## 1. Why this draw found it

The drawn class document was BLOCKING. The repair for its stated cause was already written and
sitting **uncommitted** on the shared tree — the index-OR-HEAD union in
`WORKER_FINDING_ANOTHER_LANES_STAGED_DELETION_VOIDS_EVERY_DISCHARGE_ON_THE_TREE_2026-08-20`,
whose own record was **committed at HEAD claiming "Repaired here"** while its code was in no
commit. Landing it is what surfaced this: the union closes the *staged* deletion hole, and the
case it explicitly named as **not covered** — "a deletion that actually COMMITS" — had already
happened, four hours before that document was written.

## 2. Observed, with evidence

`tests/architecture/test_no_committed_discharge_cites_an_unlanded_falsifier.py` is **RED at
HEAD** on six citations across three committed records. Every one is `in no tree at all` —
not the index, not HEAD, not the disk:

| citation | cited as DISCHARGED by |
|---|---|
| `site/customers/test_wall_exhibit.py::test_the_customer_view_of_the_whole_page_contains_no_company_or_sim_panel` | `WORKER_FINDING_A_HARNESSES_CONVENIENCE_CHOSE_THE_CONTROLS_SUBJECT_2026-08-12` |
| `site/customers/test_wall_exhibit.py::test_mutation_a_view_switch_that_skips_the_op_state_region_kills_a_named_test` | ″ |
| `site/customers/test_wall_exhibit.py::test_the_named_figures_are_visible_to_the_checker_in_the_op_state_exhibit` | ″ |
| `site/proof/index.html` | `WORKER_FINDING_THE_PUBLISHED_DOOR_WAS_GENERATED_FROM_AN_UNCOMMITTED_TREE_2026-08-15` |
| `site/proof/test_the_committed_generator_reproduces_the_published_door.py` | ″ |
| `site/proof/test_coupled_gaps_panel.py::test_an_undeclared_entry_says_so_instead_of_implying_the_old_relation` | `WORKER_FINDING_THE_BASIS_LINE_PUBLISHED_A_RELATION_THAT_IS_FALSE_FOR_THREE_PAIRS_2026-08-13` |

**All six died in ONE commit**, and it is not a mistake anybody made:

    03dd8c49e  2026-08-20 09:40:53 +0100
    The five tabs are the site now: eleven pages deleted, their content moved,
    and 25,700 lines of surface nobody could reach are gone

The records are **honest**. Each falsifier existed, ran and passed when the discharge was
written; the page it tested was later retired on purpose. Nothing was laundered, nothing
regressed, and no repair was withdrawn. The pages' *content* moved — `test_published_caveat_
reaches_the_reader.py` survives at a new path — but these four nodes have **no successor**
anywhere in `site/` or `tests/` (grepped by node name; zero hits).

## 3. What it costs, measured rather than reasoned about

Running the live parser over the three archived records:

| record | severity NOW | `parse_discharge` |
|---|---|---|
| `…THE_BASIS_LINE_PUBLISHED_A_RELATION…_2026-08-13` | **BLOCKING** | refused: *artefact does not exist* |
| `…THE_PUBLISHED_DOOR_WAS_GENERATED_FROM_AN_UNCOMMITTED_TREE_2026-08-15` | LATENT | refused: *artefact does not exist* |
| `…A_HARNESSES_CONVENIENCE_CHOSE_THE_CONTROLS_SUBJECT_2026-08-12` | RECORDED | **never seen at all** — see §4 |

So a site-retirement lane, doing its job correctly, **re-opened a finding it has nothing to do
with and put `H_harness` back into BLOCKING**. This is the same shape as the staged-deletion
freeze that lane just paid eight passes for, one door along: there the subject was a buffer any
lane could write, here it is a tree any lane may legitimately delete from. Both times the
control was correct about the question it asked and the question was addressed to the wrong tree.

**`_KNOWN_UNLANDED` cannot absorb these, and must not be taught to.** Its own R15 test —
`test_no_exemption_absorbs_a_citation_that_is_in_no_tree` — refuses any entry naming something
in no tree, deliberately: that was the exact hole the 2026-08-18 repair closed. The ratchet is
right. There is simply no vocabulary in either control for *this falsifier is gone because its
subject is gone*, so the only expressible answers are "waiting to land" (false) and "the record
is lying" (also false).

## 4. The second defect, found while measuring the first

**The two controls disagree about where a discharge may live**, and neither says so.

* `background.finding_severity.parse_discharge` reads only `header_block(text)` —
  `HEADER_BLOCK_MAX_LINES = 40`, stopping at the first `## `.
* the architecture tripwire matches `^\*\*Discharged:\*\*` **anywhere in the document**.

`WORKER_FINDING_A_HARNESSES_CONVENIENCE_CHOSE_THE_CONTROLS_SUBJECT_2026-08-12` carries its
discharge on **line 53** — past the parser's 40-line cap, before the first `## ` (line 55). The
tripwire polices that claim; the parser that decides severity has never read it.

The dangerous direction is not this document. It is that **a genuine discharge written on line
41 or later silently fails to release its finding** — the repair lands, the falsifier is cited,
and the finding stays BLOCKING with no refusal reason anywhere, because to the parser the field
does not exist. A refusal is reportable; an unread field is not. R15 FAIL-SILENT, on the field
whose entire job is to be fail-closed.

## 5. The repair, designed and not built

**Retirement is CHECKABLE, which is why this belongs in the control and not in a hand-kept list.**

    git log -1 --diff-filter=D --format=%H -- <path>

A path deleted by a commit names that commit. A path that **never landed has no such commit** —
so the widening cannot launder the case the 2026-08-18 repair closed. The landed set gains a
third answer alongside *indexed* and *at HEAD*:

* **RETIRED** — git names a deletion commit for the path, **and** for a `::node` citation the
  node is present in the file's blob **at the deleting commit's parent**. That second clause is
  what stops a retired file from becoming an amnesty for nodes it never defined.
* everything else is refused exactly as today.

**The null control, which is the whole reason this is safe:** a file never `git add`ed, and a
node in no tree, must still be REFUSED — they have no deletion commit and no pre-deletion blob.
Without that arm the widening is indistinguishable from reopening the hole it was widened past,
which is the same argument `test_a_falsifier_in_neither_landed_tree_is_still_refused` already
makes for the index-OR-HEAD union.

**Both controls need it**, because they are two of the three copies of one question (§3 of the
staged-deletion finding). Repairing only the parser leaves the tripwire red at HEAD; repairing
only the tripwire leaves the lane frozen.

**What retirement must NOT do:** silently mark the finding as still-proven. The falsifier is
gone and cannot be re-run. The honest reading is *the claim was true when made and its subject
has since been retired at `<sha>`* — a discharge that releases the severity while recording that
its evidence is now historical, not a discharge that pretends a runnable test exists.

## 6. The generalisation

A control that reads "is the evidence there?" is really asking two questions it cannot tell
apart: *was this ever true* and *is it still runnable*. While nothing is ever deleted the two
coincide, so one read serves both — and the first deliberate deletion turns the control into an
accusation. This is the same class as the index-versus-HEAD freeze it sits next to, and the tell
is identical: the premise was written down as a virtue rather than a limitation.

## 7. What is owed

- Build §5 in `background/finding_severity.parse_discharge` and in the architecture tripwire,
  with the null control in both.
- Fix §4 — the parser and the tripwire must agree on a discharge's scope. Recommendation: the
  parser reads the whole document for this field, since the tripwire already does and the
  40-line cap is the half that fails silently.
- Until then `H_harness` is BLOCKING on `…THE_BASIS_LINE…`, and the architecture tripwire is
  RED at HEAD for **any** commit whose change set selects its filename stem.

## 8. BUILT 2026-08-20, and the one place the build departed from §7

§7 recommended *"the parser reads the whole document for this field, since the tripwire already
does"*. Built as recommended it would have been a **fail-open widening**, and the measurement
is why. Over every record under `docs/staging/`, **16** documents carry a `**Discharged:**` the
40-line cap hid. Only **5** are field-shaped. The other **11 are the field being TALKED ABOUT** —
this project writes findings about its own discharge control, so mid-sentence prose ("a path a
record cites on its `**Discharged:**` line") is ordinary, and `DIRECTOR_CONSOLE_2026-08-19.md`
quotes gate output whose **template names a fictional `tests/x/test_y.py::test_z`**. Read
unanchored, the parser would have manufactured 11 claims from prose — and would have RELEASED
on a quoted example path that happened to exist.

What §7 missed is that the tripwire's scope is not "the whole document": it is
`^\*\*Discharged:\*\*` — **anchored at line start**, and that anchor was doing load-bearing work
nobody had written down. The parser's regex was unanchored, so "same scope as the tripwire"
meant two different things depending on which half you read. Built as `(?m)^`: admits exactly
the 5, refuses the 11.

Two further things the build found, neither in §7:

* **An explicit negative is not a malformed claim.** Two committed records carry
  `**Discharged:** no.` — authors stating plainly that the finding is *not* discharged. Newly
  visible to the parser, these read as "names no artefact in backticks", i.e. two honest
  authors reported as having written broken claims. `_NEGATIVE_DISCHARGE_RE` now reads a
  whole-value negative as *no claim*. Deliberately narrow: it is the one branch that makes a
  claim vanish rather than refuse, so a half-written "not yet, waiting on `tests/x.py`" still
  carries a backtick and still refuses.
* **The null control's R15 mutation is weaker than the fail-open one, and is reported as such.**
  Deleting the `blob is None` arm raises TypeError rather than releasing quietly, because the
  lines after it are only well-defined once a never-landed citation has been sent away. That
  proves the arm is load-bearing, not that it *fires*. The fail-OPEN direction is carried by
  `test_mutation_i_…`, where an invented node in a retired file really does release.

**Verified:** both controls green (93 passed across the two suites), the six citations in §2
accepted as RETIRED naming `03dd8c49e`, the two never-landed null controls still refused, and
the BLOCKING record of §3 (`…THE_BASIS_LINE…`) now RECORDED with its reason reading *"evidence
is HISTORICAL, not runnable: … (retired at 03dd8c49e)"* — released, and not pretending a
runnable test exists. `false_discharges()` over the staging root: none.

**Superseded — the deferral below was the PREVIOUS tick's, and its stated blocker was checked
and found not to apply here:** the two live suites were `-m "operational or join_report_only or
scale_report_only"` and `site/`. `tests/background/test_finding_severity.py` carries no markers
and is not under `site/`, so neither running suite executes it or anything importing the module;
the mutation battery was not editable underneath.

**Not done in this tick, deliberately, with the reason stated:** two full suites were live over
this shared tree throughout (a 48-minute main suite and the operational suite), and
`tests/background/test_finding_severity.py`'s mutation harness `_load_mutant` reads the module's
SOURCE and pins exact lines. Editing that module underneath a running mutation battery is how a
false red gets written into the publish gate — which is the class this draw was opened on. The
index-OR-HEAD union was landed instead, because it was already written, already tested, and
already claimed as done by a committed record.

## 9. The THIRD tick, which is the one that landed it — and what §8 claimed and had not built

§8 was written by a tick that died before committing anything. Its work was real and is now at
HEAD; two of its claims were not.

**"§5 built in BOTH controls with the null control in each" was true of the parser and false of
the tripwire.** `tests/architecture/test_no_committed_discharge_cites_an_unlanded_falsifier.py`
had gained `_retired_at`, `_retirement_accounts_for` and an `allow_retired` switch, and not one
test that could fail on any of them — the switch existed for a mutation nobody had written. That
is the shape this project files as a control that cannot fail, added while repairing a control
that could not fail. Built here as
`test_MUTATION_dropping_the_retirement_answer_reads_an_honest_record_as_a_lie`, whose mutant is
literally the control as shipped yesterday (`allow_retired=False` IS index-OR-HEAD), asserted to
call the honest retired citation a violation, with the never-landed path and the invented node
still refused in both directions. Its subject is real immutable history (`03dd8c49e`), where the
parser's battery builds throwaway repositories — so the pair is now proven against a fixture and
against the deletion that actually caused this finding.

**The ratchet's good direction, taken.** All NINE `_KNOWN_UNLANDED` wedge-draw entries landed at
`71c59563a` and are deleted; the list is now EMPTY, which is the state it is supposed to reach.
That red was what the tripwire actually reported on this tree — the retirement widening itself
passed clean on first run.

**TWO ROOMS, resolved by measurement rather than by choosing.** This document was in the staging
ROOT *and* in `done/`: the previous tick staged the rename and never committed, and the root copy
was then resurrected untracked. `git hash-object` on the root copy returned the same
`61bb8ecce` as `git rev-parse HEAD:<root path>` — a byte-identical resurrection of the pre-move
blob, so deleting it loses nothing and the `done/` copy is the only one carrying the discharge.

**Landed in two commits, deliberately.** The repair and its falsifiers first (`664124a33`, three
paths), this record second, so the discharge cites nodes that are at HEAD when it is read rather
than nodes it hopes will be. Five earlier claims on the neighbouring document in this same class
were written into the tree while their code was in no commit; that is the failure mode this
ordering exists to refuse.
