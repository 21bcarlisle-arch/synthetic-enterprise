# WORKER FINDING — a neighbouring lane's staged deletion un-landed two committed falsifiers and froze a lane, and three controls asked the shared index the question only HEAD can answer

**Severity:** RECORDED · **Lane:** H_harness

**Found:** 2026-08-20, RUNG-1c BLOCKING draw on `H_harness`
**Class:** R15 — wrong subject (variant: *the subject is a buffer every other lane can write*)
**Repaired here, with the falsifiers named in §5.** Nothing is owed; the one case the repair
deliberately does not cover is named in §4 rather than absorbed.

## 1. What the draw looked like, and why it was nobody's fault

The doorbell drew lane `H_harness` at RUNG 1c: two class documents printing **BLOCKING**.

- `CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md` → `WORKER_FINDING_A_HARNESSES_CONVENIENCE_CHOSE_THE_CONTROLS_SUBJECT_2026-08-12.md`
- `CLASS_NO_CALLER_AND_NEVER_RUNS_2026-08-12.md` → `WORKER_FINDING_THE_CORRECTED_SENTENCE_NEVER_REACHED_THE_READER_AND_ITS_CONTROL_HAS_NO_CALLER_2026-08-15.md`

Both documents carry a `**Discharged:**` header. Both were released weeks ago. The previous
pass re-rendered the two headers and recorded that as the unblocking. It re-rendered them
from a severity that was **still deriving BLOCKING**, so the freeze came straight back.

Measured rather than reasoned about — `parse_severity_file` on each of the two archived
documents returned `BLOCKING`, and `parse_discharge` said why:

    artefact does not exist: site/customers/test_wall_exhibit.py::test_the_customer_view_...
    artefact does not exist: site/proof/test_published_caveat_reaches_the_reader.py::test_...

Both files are **at HEAD**, and all five cited nodes are in HEAD's blobs:

    site/customers/test_wall_exhibit.py                    head=Y  index=N
    site/proof/test_published_caveat_reaches_the_reader.py head=Y  index=N

A site-retirement lane had `git rm`'d 72 pages. The deletion is **in no commit**, is
uncommitted still, and may never land. Neither finding owns any part of it. Clone this
repository today and both falsifiers are there and runnable.

## 2. The mechanism

`background/finding_severity.parse_discharge` resolved every cited artefact against
`git ls-files` — the **index**. That read was itself a repair, landed 2026-08-18 to close a
real hole (a node that existed only in the author's editor released a finding), and it wrote
its premise down in the module:

> THE INDEX, not HEAD and not the disk. […] Post-commit the index matches HEAD and the two
> readings coincide.

That sentence is false on this project, and CLAUDE.md says so in as many words: three
concurrent writers — `process_run_complete.py`, the interactive session, and
`autonomous_runner.py`'s turns — share **one working tree and one index**. The index is not a
view of the commit in hand; it is a buffer holding every lane's in-flight intent, including
intents that will be abandoned. Asking it "does the repository have this falsifier" gives an
answer any other lane can change, about work that lane has never read.

The blast radius is not two documents. It is **every discharge on the tree**, and through
`class_severity` → the class documents → `_blocking_lane_draw`, **any lane** — for as long
as any deletion sits staged anywhere.

## 3. Three copies of the same question

The same question is asked in three places, and all three asked the index alone:

| site | subject | state when measured |
|---|---|---|
| `background/finding_severity.parse_discharge` | a document's `**Discharged:**` citations | froze `H_harness` |
| `tests/architecture/test_no_committed_discharge_cites_an_unlanded_falsifier.py` | every committed record's citations | RED on 8 citations across 4 records, all `site/`, all at HEAD |
| `tests/architecture/test_no_committed_store_claims_an_unlanded_falsifier.py` | atom stores' credited falsifiers | red, but for another lane's debt — unaffected either way, left alone |

R10: the first two are repaired as one class. The third is **not touched**, deliberately: its
reds are `tests/company/core/test_three_horizon_clv.py`, which is in no tree at all, and two
stale `_DECLARED_HONEST_ABSENCE` entries. Widening its subject would not have changed a
single one of its verdicts, and repairing another lane's debt from here is not this draw's
business. It is named so the next pass inherits the fact.

## 4. The repair, and the one thing it does not cover

**The landed set is the index OR HEAD.** A path at HEAD is landed — a clone has it today. A
path staged is landing with this commit. Only a path in **neither** is on one machine, which
is the entire hole the 2026-08-18 repair closed, and it stays closed: the working tree is
still the one tree that is never asked.

**NOT COVERED, named rather than absorbed:** a deletion that actually **commits**. There is
one index and it cannot say which lane staged what, so a falsifier deleted by the commit in
flight releases once more and goes red on the next read, when HEAD no longer carries it. A
one-read lag, against a permanent cross-lane freeze.

**The two directions of the architecture ratchet do not share a subject.** The tripwire asks
"will a clone have this" → index OR HEAD. The stale-entry direction asks "has the debt been
PAID" → **HEAD only**, because a citation that is merely staged has not paid it and the lane
holding it can drop that staging at any moment. When the two shared one subject, that
direction reported **11 entries as "landed, which is the good outcome"** and **nine of them
were nodes in another lane's index and in no commit**. Deleting an exemption on that reading
is how a ratchet shrinks past what actually landed. Two of the eleven had genuinely landed
(`tests/saas/test_clv_margin_basis.py`, `tests/tools/test_derived_basis_parentage_gate.py`,
both at HEAD since `b8e4f26be`) and are deleted from `_KNOWN_UNLANDED`.

## 5. Falsifiers

`background/finding_severity.py`, in `tests/background/test_finding_severity.py` — each
against a REAL git repository with a real commit, because a repo with no HEAD cannot
exercise this class at all and every assertion would pass vacuously:

- `test_another_lanes_staged_deletion_does_not_void_a_committed_falsifier` — the shipped
  defect, reproduced: commit the falsifier, `git rm` it, the discharge must still release.
- `test_a_node_only_head_still_defines_releases_when_the_index_copy_has_lost_it` — the node
  half, which a file-level union alone does not reach.
- `test_a_falsifier_in_neither_landed_tree_is_still_refused` — **the null control**, and the
  reason the widening cannot be mistaken for reopening the hole it was widened past. Both
  arms: a file never `git add`ed, and a node in no tree.
- `test_mutation_j_reading_the_landed_set_from_the_index_alone_kills_a_named_test` and
  `test_mutation_k_dropping_the_head_blob_fallback_kills_a_named_test` — R15, the shipped
  defect put back on a copy of the module, file half and node half separately. Each also
  asserts the untouched property still holds, so neither mutation passes by breaking
  everything.

`tests/architecture/test_no_committed_discharge_cites_an_unlanded_falsifier.py`:

- `test_the_tripwires_subject_is_exactly_the_index_union_head` — the union rebuilt from two
  independent git calls rather than compared against itself. Its boundary is stated in the
  test: on a tree whose index and HEAD agree it cannot tell a union from either half, which
  is why the behavioural proof lives in the module's mutation battery.
- `test_the_stale_entry_direction_does_not_count_a_staged_only_citation_as_paid` — driven
  through a synthetic citation set so the verdict does not depend on which lanes are
  mid-flight.

## 6. Two things repaired in the same tick because they refused the landing

**A self-clearing alarm cannot be superseded.** `background/alarm_repetition.py` escalates a
repeating alert into the draw by writing a `WORKER_FINDING_REPEATING_ALARM_*` document and
muting the pager for that signature until the state changes. Consolidation is a supersession
claim. Fold one into a class document and the condition is archived into a cost table with
its own pager still off — gone from both channels, converged on by nothing. The deadman's
switch filed **two documents for one signature** (`deadman_commit`); a machine wrote both
titles; one said the session "may be **wedged**" and that adverb alone filed it under the
publish-gate/wedge class, while its identical-signature sibling stayed unclassed. Now out of
consolidation by prefix (`SELF_CLEARING_ALARM_PREFIXES`) and **still in the population** —
same root, same severity, same lane, still drawable. R15 with a mutation on the constant and
a null control (a hand-written finding about an alarm still consolidates).

**A `::node` shorthand voids the whole discharge it appears in.**
`WORKER_FINDING_ONE_OLD_LEVEL_MOVE_BOUGHT_AN_ATOM_FORTY_THREE_UNBOUNDED_PASSES_2026-08-19.md`
listed one falsifier with its path and three more as bare `::test_...` continuations. Every
named artefact must exist or the whole claim is void, so all four were refused and
`test_the_staging_root_has_no_false_discharges` was red at HEAD — unnoticed, because the gate
selects tests by filename stem and nothing in that commit's change set had this one's stem.
Repaired in the document by writing the path out. The parser was deliberately NOT taught the
shorthand: a bare `::x` is a shape any backticked prose could produce, and accepting it would
be a new fail-open on the field whose entire job is to be fail-closed.

## 7. What this cost, and what it says

Eight passes wrote a landing account for the two frozen findings. None of them ran the tool
on the two documents; the pass before this one ran it on the class documents and re-rendered
headers from a severity that was still deriving BLOCKING. The measurement that ended it was
one call to `parse_discharge` on the two archived files, which named its own reason in the
refusal string it had been returning the whole time.

**The generalisation.** When a control's subject is shared mutable state, the control does not
measure its subject — it measures whoever wrote last. Every one of these three controls was
correct about the question it asked; the question was addressed to the wrong tree, and the
wrong tree was chosen because on a single-writer repository it is indistinguishable from the
right one. The tell is that the premise was written down as a virtue — *"post-commit the
index matches HEAD and the two readings coincide"* — which is the same shape as the already
filed class where a docstring explaining why a subject is narrower than its claim turns out
to be the defect, pre-confessed.
