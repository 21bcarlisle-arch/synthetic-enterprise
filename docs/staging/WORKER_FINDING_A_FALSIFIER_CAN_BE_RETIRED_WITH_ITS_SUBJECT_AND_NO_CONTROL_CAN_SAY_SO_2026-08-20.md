**Severity:** BLOCKING · **Lane:** H_harness

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

**Not done in this tick, deliberately, with the reason stated:** two full suites were live over
this shared tree throughout (a 48-minute main suite and the operational suite), and
`tests/background/test_finding_severity.py`'s mutation harness `_load_mutant` reads the module's
SOURCE and pins exact lines. Editing that module underneath a running mutation battery is how a
false red gets written into the publish gate — which is the class this draw was opened on. The
index-OR-HEAD union was landed instead, because it was already written, already tested, and
already claimed as done by a committed record.
